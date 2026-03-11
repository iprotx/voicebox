"""Telegram bot helpers for status updates, rate limiting, and media sending fallback."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json
import threading
import time
import urllib.parse
import urllib.request

from ..utils.transcode import TranscodeError, transcode_for_audio, transcode_for_voice


@dataclass(frozen=True)
class BotLimits:
    max_input_file_size_mb: int = 20
    max_text_length: int = 2000
    max_requests_per_window: int = 6
    window_seconds: int = 60
    voice_max_seconds: int = 60
    voice_max_bytes: int = 8 * 1024 * 1024
    audio_max_bytes: int = 45 * 1024 * 1024


class FriendlyUserError(ValueError):
    pass


class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[int, list[float]] = {}

    def check(self, chat_id: int) -> None:
        now = time.time()
        start = now - self.window_seconds
        hits = [t for t in self._hits.get(chat_id, []) if t >= start]
        if len(hits) >= self.max_requests:
            raise FriendlyUserError("Слишком много запросов. Попробуйте ещё раз через минуту 🙏")
        hits.append(now)
        self._hits[chat_id] = hits


class VoiceboxApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def _get_json(self, path: str) -> dict[str, Any]:
        with urllib.request.urlopen(f"{self.base_url}{path}", timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))

    def get_health(self) -> dict[str, Any]:
        return self._get_json("/health")

    def get_active_tasks(self) -> dict[str, Any]:
        return self._get_json("/tasks/active")

    def get_model_progress(self, model_name: str) -> dict[str, Any]:
        encoded = urllib.parse.quote(model_name, safe="")
        return self._get_json(f"/models/progress/{encoded}")


class TelegramApiClient:
    def __init__(self, token: str) -> None:
        self.base_url = f"https://api.telegram.org/bot{token}"

    def _post_form(self, method: str, payload: dict[str, Any]) -> dict[str, Any]:
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(f"{self.base_url}/{method}", data=data, method="POST")
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))

    def send_message(self, chat_id: int, text: str) -> int:
        response = self._post_form("sendMessage", {"chat_id": chat_id, "text": text})
        return int(response["result"]["message_id"])

    def edit_message_text(self, chat_id: int, message_id: int, text: str) -> None:
        self._post_form(
            "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": text}
        )


class JobStatusUpdater:
    def __init__(
        self,
        tg: TelegramApiClient,
        voicebox: VoiceboxApiClient,
        chat_id: int,
        model_name: str,
        interval_seconds: int = 3,
    ) -> None:
        self.tg = tg
        self.voicebox = voicebox
        self.chat_id = chat_id
        self.model_name = model_name
        self.interval_seconds = interval_seconds
        self.message_id: int | None = None
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        self.message_id = self.tg.send_message(self.chat_id, "✅ Принято. Готовлю задачу…")
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        if self.message_id is None:
            return
        while not self._stop_event.wait(self.interval_seconds):
            try:
                health = self.voicebox.get_health()
                tasks = self.voicebox.get_active_tasks()
                model = self.voicebox.get_model_progress(self.model_name)
                text = (
                    "⚙️ В работе\n"
                    f"• Сервер: {health.get('status', 'unknown')}\n"
                    f"• Активных генераций: {len(tasks.get('generations', []))}\n"
                    f"• Загрузка модели: {model.get('progress', 0)}% ({model.get('status', 'unknown')})"
                )
                self.tg.edit_message_text(self.chat_id, self.message_id, text)
            except Exception:
                # Keep silent; next poll will retry.
                continue

    def finish(self, ok: bool, details: str) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1)
        if self.message_id is None:
            return
        prefix = "✅ Готово" if ok else "❌ Ошибка"
        self.tg.edit_message_text(self.chat_id, self.message_id, f"{prefix}\n{details}")


class ResultSender:
    def __init__(self, tg: TelegramApiClient, limits: BotLimits, temp_dir: Path) -> None:
        self.tg = tg
        self.limits = limits
        self.temp_dir = temp_dir

    def validate_request(self, text: str, file_size_bytes: int, limiter: SlidingWindowRateLimiter, chat_id: int) -> None:
        limiter.check(chat_id)
        if len(text.strip()) == 0:
            raise FriendlyUserError("Текст пустой. Добавьте текст для озвучки ✍️")
        if len(text) > self.limits.max_text_length:
            raise FriendlyUserError(
                f"Слишком длинный текст: максимум {self.limits.max_text_length} символов."
            )
        max_bytes = self.limits.max_input_file_size_mb * 1024 * 1024
        if file_size_bytes > max_bytes:
            raise FriendlyUserError(
                f"Файл слишком большой: максимум {self.limits.max_input_file_size_mb} МБ."
            )

    def send_result(self, chat_id: int, source_audio: Path, duration_seconds: float) -> str:
        file_size = source_audio.stat().st_size
        as_voice = duration_seconds <= self.limits.voice_max_seconds and file_size <= self.limits.voice_max_bytes

        if as_voice:
            try:
                voice = transcode_for_voice(source_audio, self.temp_dir)
                self._send_file(chat_id, "sendVoice", "voice", voice.output_path)
                return "voice"
            except TranscodeError:
                pass

        try:
            audio = transcode_for_audio(source_audio, self.temp_dir)
            if audio.output_path.stat().st_size <= self.limits.audio_max_bytes:
                self._send_file(chat_id, "sendAudio", "audio", audio.output_path)
                return "audio"
        except TranscodeError:
            pass

        self._send_file(chat_id, "sendDocument", "document", source_audio)
        return "document"

    def _send_file(self, chat_id: int, method: str, form_field: str, file_path: Path) -> None:
        boundary = "----voiceboxboundary"
        body = bytearray()

        def _add_part(name: str, value: str) -> None:
            body.extend(f"--{boundary}\r\n".encode())
            body.extend(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
            body.extend(value.encode())
            body.extend(b"\r\n")

        _add_part("chat_id", str(chat_id))
        body.extend(f"--{boundary}\r\n".encode())
        body.extend(
            (
                f'Content-Disposition: form-data; name="{form_field}"; '
                f'filename="{file_path.name}"\r\n'
                "Content-Type: application/octet-stream\r\n\r\n"
            ).encode()
        )
        body.extend(file_path.read_bytes())
        body.extend(b"\r\n")
        body.extend(f"--{boundary}--\r\n".encode())

        req = urllib.request.Request(
            f"{self.tg.base_url}/{method}",
            data=bytes(body),
            method="POST",
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        )
        with urllib.request.urlopen(req, timeout=60):
            return

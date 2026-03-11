"""Utilities for transcoding generated audio into Telegram-friendly formats."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess


class TranscodeError(RuntimeError):
    """Raised when ffmpeg transcoding fails."""


@dataclass(frozen=True)
class TranscodeResult:
    output_path: Path
    mime_type: str


def _run_ffmpeg(args: list[str]) -> None:
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise TranscodeError("ffmpeg is not installed or not available in PATH")

    cmd = [ffmpeg_path, "-y", *args]
    process = subprocess.run(cmd, capture_output=True, text=True)
    if process.returncode != 0:
        raise TranscodeError(
            f"ffmpeg failed with code {process.returncode}: {process.stderr.strip()}"
        )


def transcode_for_voice(input_path: Path, output_dir: Path) -> TranscodeResult:
    """Transcode to low-bitrate OGG/Opus suitable for sendVoice."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{input_path.stem}.voice.ogg"
    _run_ffmpeg(
        [
            "-i",
            str(input_path),
            "-c:a",
            "libopus",
            "-b:a",
            "48k",
            "-ac",
            "1",
            "-ar",
            "48000",
            str(output_path),
        ]
    )
    return TranscodeResult(output_path=output_path, mime_type="audio/ogg")


def transcode_for_audio(input_path: Path, output_dir: Path) -> TranscodeResult:
    """Transcode to MP3 suitable for sendAudio fallback."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{input_path.stem}.audio.mp3"
    _run_ffmpeg(
        [
            "-i",
            str(input_path),
            "-c:a",
            "libmp3lame",
            "-b:a",
            "128k",
            str(output_path),
        ]
    )
    return TranscodeResult(output_path=output_path, mime_type="audio/mpeg")

from pathlib import Path

from backend.bot.telegram_workflow import (
    BotLimits,
    FriendlyUserError,
    ResultSender,
    SlidingWindowRateLimiter,
)
from backend.utils.transcode import TranscodeError


def test_rate_limiter_blocks_after_limit() -> None:
    limiter = SlidingWindowRateLimiter(max_requests=2, window_seconds=60)
    limiter.check(1)
    limiter.check(1)

    try:
        limiter.check(1)
        assert False, "Expected FriendlyUserError"
    except FriendlyUserError:
        pass


def test_validate_request_limits_text_and_file_size(tmp_path: Path) -> None:
    sender = ResultSender(
        tg=type("Dummy", (), {"base_url": "http://example.com"})(),
        limits=BotLimits(max_text_length=10, max_input_file_size_mb=1),
        temp_dir=tmp_path,
    )
    limiter = SlidingWindowRateLimiter(max_requests=10, window_seconds=60)

    try:
        sender.validate_request("x" * 11, 100, limiter, 10)
        assert False, "Expected FriendlyUserError"
    except FriendlyUserError:
        pass

    try:
        sender.validate_request("ok", 2 * 1024 * 1024, limiter, 10)
        assert False, "Expected FriendlyUserError"
    except FriendlyUserError:
        pass


def test_send_result_fallback_to_document(tmp_path: Path, monkeypatch) -> None:
    sent: list[str] = []

    class DummyTG:
        base_url = "http://example.com"

    sender = ResultSender(tg=DummyTG(), limits=BotLimits(), temp_dir=tmp_path)

    audio_file = tmp_path / "in.wav"
    audio_file.write_bytes(b"audio")

    monkeypatch.setattr(sender, "_send_file", lambda *args: sent.append(args[1]))
    monkeypatch.setattr(
        "backend.bot.telegram_workflow.transcode_for_voice",
        lambda *args: (_ for _ in ()).throw(TranscodeError("err")),
    )
    monkeypatch.setattr(
        "backend.bot.telegram_workflow.transcode_for_audio",
        lambda *args: (_ for _ in ()).throw(TranscodeError("err")),
    )

    transport = sender.send_result(1, audio_file, duration_seconds=15)

    assert transport == "document"
    assert sent == ["sendDocument"]

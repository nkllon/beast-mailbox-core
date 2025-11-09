"""Tests for the file system mailbox service."""

import asyncio
import json
import logging
from pathlib import Path

import pytest

from beast_mailbox_core import FileSystemMailboxConfig, FileSystemMailboxService
from beast_mailbox_core.filesystem_mailbox import _create_fs_config_from_env


@pytest.mark.asyncio
async def test_send_message_creates_file(tmp_path: Path) -> None:
    """Sending a message should create a JSON file in the recipient inbox."""

    config = FileSystemMailboxConfig(base_path=str(tmp_path))
    sender = FileSystemMailboxService("sender", config)

    message_id = await sender.send_message("recipient", {"value": 42})

    inbox = tmp_path / "recipient" / "inbox"
    files = list(inbox.glob("*.json"))

    assert message_id is not None
    assert len(files) == 1


@pytest.mark.asyncio
async def test_start_and_receive_message(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Messages should be picked up by the recipient service."""

    config = FileSystemMailboxConfig(base_path=str(tmp_path), poll_interval=0.05)
    recipient = FileSystemMailboxService("recipient", config)
    received = []

    async def handler(message):
        received.append(message)

    recipient.register_handler(handler)
    caplog.set_level(logging.DEBUG, logger=recipient.logger.name)
    caplog.set_level(logging.DEBUG, logger="beast_mailbox.fs.sender")
    await recipient.start()

    sender = FileSystemMailboxService("sender", config)
    await sender.send_message("recipient", {"hello": "world"})

    await _wait_for(lambda: received, timeout=1.0)

    await recipient.stop()

    assert len(received) == 1
    assert received[0].payload == {"hello": "world"}

    inbox = tmp_path / "recipient" / "inbox"
    assert not list(inbox.glob("*.json"))
    assert "Sent file system message" in caplog.text
    assert "Delivered file system message" in caplog.text


async def _wait_for(predicate, timeout: float, interval: float = 0.025) -> None:
    """Utility to wait for a predicate in tests."""

    loop = asyncio.get_event_loop()
    deadline = loop.time() + timeout

    while loop.time() < deadline:
        if predicate():
            return
        await asyncio.sleep(interval)

    raise TimeoutError("Predicate not satisfied within timeout")


@pytest.mark.asyncio
async def test_send_message_applies_mkdir_mode(tmp_path: Path) -> None:
    """Recipient inbox should be created with configured permissions."""

    config = FileSystemMailboxConfig(base_path=str(tmp_path), mkdir_mode=0o750)
    sender = FileSystemMailboxService("sender", config)

    await sender.send_message("recipient", {"value": 1})

    inbox = tmp_path / "recipient" / "inbox"
    mode = inbox.stat().st_mode & 0o777

    assert mode == 0o750


@pytest.mark.asyncio
async def test_process_pending_logs_when_no_handlers(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Service should log and retain messages when no handlers are registered."""

    config = FileSystemMailboxConfig(base_path=str(tmp_path))
    service = FileSystemMailboxService("recipient", config)

    await service.connect()
    inbox = service.inbox_path
    message_path = inbox / "test-message.json"
    inbox.mkdir(parents=True, exist_ok=True)
    message_path.write_text(json.dumps({"message_id": "abc"}), encoding="utf-8")

    caplog.set_level(logging.DEBUG, logger=service.logger.name)

    await service._process_pending_files()

    assert (
        message_path.exists()
    ), "Message should remain when no handlers are registered"
    assert "No handlers registered" in caplog.text


@pytest.mark.asyncio
async def test_process_pending_cleans_orphaned_tmp_files(tmp_path: Path) -> None:
    """Temporary files left behind should be cleaned up during processing."""

    config = FileSystemMailboxConfig(base_path=str(tmp_path))
    service = FileSystemMailboxService("recipient", config)

    await service.connect()
    inbox = service.inbox_path
    tmp_file = inbox / "orphan.tmp"
    tmp_file.write_text("partial write", encoding="utf-8")

    await service._process_pending_files()

    assert not tmp_file.exists(), "Orphaned temporary files should be removed"


@pytest.mark.asyncio
async def test_process_pending_logs_and_removes_corrupted_files(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Corrupted JSON messages should log an error and be removed."""

    config = FileSystemMailboxConfig(base_path=str(tmp_path))
    service = FileSystemMailboxService("recipient", config)

    await service.connect()

    async def handler(message) -> None:  # pragma: no cover - should not be invoked
        pass

    service.register_handler(handler)

    inbox = service.inbox_path
    bad_file = inbox / "bad-message.json"
    bad_file.write_text("{not-valid-json", encoding="utf-8")

    caplog.set_level(logging.ERROR, logger=service.logger.name)

    await service._process_pending_files()

    assert not bad_file.exists(), "Corrupted message file should be removed"
    assert "Failed to decode message file" in caplog.text


@pytest.mark.asyncio
async def test_consume_loop_logs_and_continues_after_exception(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Polling loop should log exceptions and continue running."""

    config = FileSystemMailboxConfig(base_path=str(tmp_path), poll_interval=0.01)
    service = FileSystemMailboxService("recipient", config)

    await service.connect()
    caplog.set_level(logging.ERROR, logger=service.logger.name)

    call_count = 0

    async def failing_process() -> None:
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise RuntimeError("boom")
        service._running = False

    async def fake_sleep(_: float) -> None:
        return None

    service._process_pending_files = failing_process  # type: ignore[assignment]
    monkeypatch.setattr(asyncio, "sleep", fake_sleep)

    service._running = True
    await service._consume_loop()

    assert call_count >= 2, "Loop should continue after handling an exception"
    assert "loop error" in caplog.text


@pytest.mark.asyncio
async def test_stop_cancels_background_task(tmp_path: Path) -> None:
    """Stopping the service should cancel the polling task without errors."""

    config = FileSystemMailboxConfig(base_path=str(tmp_path), poll_interval=0.01)
    service = FileSystemMailboxService("agent", config)

    await service.start()
    assert service._processing_task is not None

    await service.stop()

    assert service._processing_task is None


def test_create_fs_config_from_env_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """Default configuration should be used when env vars are absent."""

    monkeypatch.delenv("BEAST_MAILBOX_FS_ROOT", raising=False)
    monkeypatch.delenv("BEAST_MAILBOX_FS_POLL_INTERVAL", raising=False)
    monkeypatch.delenv("BEAST_MAILBOX_FS_MKDIR_MODE", raising=False)

    config = _create_fs_config_from_env()

    assert config.base_path == "/tmp/beast_mailbox"
    assert config.poll_interval == 0.5
    assert config.mkdir_mode == 0o755


def test_create_fs_config_from_env_overrides(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Environment variables should override defaults."""

    monkeypatch.setenv("BEAST_MAILBOX_FS_ROOT", str(tmp_path))
    monkeypatch.setenv("BEAST_MAILBOX_FS_POLL_INTERVAL", "1.25")
    monkeypatch.setenv("BEAST_MAILBOX_FS_MKDIR_MODE", "700")

    config = _create_fs_config_from_env()

    assert config.base_path == str(tmp_path)
    assert config.poll_interval == 1.25
    assert config.mkdir_mode == 0o700


def test_create_fs_config_from_env_invalid_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Invalid environment values should fall back to safe defaults."""

    monkeypatch.setenv("BEAST_MAILBOX_FS_POLL_INTERVAL", "not-a-number")
    monkeypatch.setenv("BEAST_MAILBOX_FS_MKDIR_MODE", "xyz")

    config = _create_fs_config_from_env()

    assert config.poll_interval == 0.5
    assert config.mkdir_mode == 0o755

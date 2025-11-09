"""Tests for CLI argument surfaces and configuration handling."""

import asyncio
from pathlib import Path
from unittest import mock

import pytest

from beast_mailbox_core import cli
from beast_mailbox_core.filesystem_mailbox import FileSystemMailboxConfig, FileSystemMailboxService


def test_service_parser_supports_backend_choices() -> None:
    """Service parser should expose backend selection with sensible defaults."""

    parser = cli.create_service_parser()
    args = parser.parse_args(["agent"])

    assert args.backend == "redis"

    filesystem_args = parser.parse_args(
        [
            "agent",
            "--backend",
            "filesystem",
            "--filesystem-root",
            "/tmp/mailbox",
            "--poll-interval",
            "0.25",
        ]
    )

    assert filesystem_args.backend == "filesystem"
    assert filesystem_args.filesystem_root == "/tmp/mailbox"
    assert filesystem_args.poll_interval == pytest.approx(0.25)


def test_send_parser_requires_message_or_json() -> None:
    """Send parser should enforce mutually exclusive payload inputs."""

    parser = cli.create_send_parser()

    # Missing payload should raise
    with pytest.raises(SystemExit):
        parser.parse_args(["sender", "recipient"])

    # Supplying both message and json should raise
    with pytest.raises(SystemExit):
        parser.parse_args(
            [
                "sender",
                "recipient",
                "--message",
                "hello",
                "--json",
                '{"key": "value"}',
            ]
        )

    # Single payload option succeeds
    args = parser.parse_args(
        ["sender", "recipient", "--message", "ok", "--message-type", "notice"]
    )

    assert args.message == "ok"
    assert args.json is None
    assert args.message_type == "notice"


def test_get_redis_config_cli_overrides_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI flags should take precedence over REDIS_URL values."""

    monkeypatch.setenv("REDIS_URL", "redis://:envpass@envhost:6380/7")

    parser = cli.create_service_parser()
    args = parser.parse_args(
        [
            "agent",
            "--redis-host",
            "cli-host",
            "--redis-port",
            "1234",
            "--redis-password",
            "cli-pass",
            "--redis-db",
            "5",
        ]
    )

    config = cli.get_redis_config_from_args(args)

    assert config["host"] == "cli-host"
    assert config["port"] == 1234
    assert config["password"] == "cli-pass"
    assert config["db"] == 5


@pytest.mark.asyncio
async def test_run_service_async_uses_filesystem_backend(tmp_path: Path) -> None:
    """run_service_async should instantiate filesystem backend when selected."""

    parser = cli.create_service_parser()
    args = parser.parse_args(
        [
            "agent",
            "--backend",
            "filesystem",
            "--filesystem-root",
            str(tmp_path),
            "--poll-interval",
            "0.05",
        ]
    )

    with mock.patch("beast_mailbox_core.cli.FileSystemMailboxService", autospec=True) as mock_service_cls:
        service_instance = mock_service_cls.return_value
        service_instance.start.return_value = asyncio.Future()
        service_instance.start.return_value.set_result(True)
        service_instance.stop.return_value = asyncio.Future()
        service_instance.stop.return_value.set_result(None)

        wait_event = asyncio.Event()
        wait_event.set()

        with mock.patch("asyncio.Event", return_value=wait_event):
            with mock.patch("beast_mailbox_core.cli._fetch_latest_messages") as mock_fetch, mock.patch(
                "beast_mailbox_core.cli.RedisMailboxService", autospec=True
            ) as mock_redis_cls:
                mock_fetch.return_value = asyncio.Future()
                mock_fetch.return_value.set_result(None)

                redis_instance = mock_redis_cls.return_value
                redis_instance.start.return_value = asyncio.Future()
                redis_instance.start.return_value.set_result(True)
                redis_instance.stop.return_value = asyncio.Future()
                redis_instance.stop.return_value.set_result(None)

                await cli.run_service_async(args)

        mock_service_cls.assert_called_once()
        service_instance.start.assert_called_once()
        service_instance.stop.assert_called_once()


@pytest.mark.asyncio
async def test_send_message_async_parses_json_payload() -> None:
    """send_message_async should parse JSON payloads when provided."""

    parser = cli.create_send_parser()
    args = parser.parse_args(
        [
            "sender",
            "recipient",
            "--json",
            '{"value": "ok"}',
        ]
    )

    with mock.patch(
        "beast_mailbox_core.cli.RedisMailboxService", autospec=True
    ) as mock_service_cls:
        service_instance = mock_service_cls.return_value
        service_instance.send_message.return_value = asyncio.Future()
        service_instance.send_message.return_value.set_result("message-id")
        service_instance.stop.return_value = asyncio.Future()
        service_instance.stop.return_value.set_result(None)

        await cli.send_message_async(args)

        service_instance.send_message.assert_awaited_once()
        called_kwargs = service_instance.send_message.call_args.kwargs
        assert called_kwargs["payload"] == {"value": "ok"}
        assert called_kwargs["message_type"] == "direct_message"


@pytest.mark.asyncio
async def test_send_message_async_uses_filesystem_backend(tmp_path: Path) -> None:
    """send_message_async should instantiate filesystem service when requested."""

    parser = cli.create_send_parser()
    args = parser.parse_args(
        [
            "sender",
            "recipient",
            "--backend",
            "filesystem",
            "--filesystem-root",
            str(tmp_path),
            "--message",
            "hello",
            "--message-id",
            "immutable-id",
        ]
    )

    with mock.patch(
        "beast_mailbox_core.cli.FileSystemMailboxService", autospec=True
    ) as mock_service_cls:
        service_instance = mock_service_cls.return_value
        service_instance.send_message.return_value = asyncio.Future()
        service_instance.send_message.return_value.set_result("fs-id")
        service_instance.stop.return_value = asyncio.Future()
        service_instance.stop.return_value.set_result(None)

        await cli.send_message_async(args)

        mock_service_cls.assert_called_once()
        service_instance.send_message.assert_awaited_once()
        called_kwargs = service_instance.send_message.call_args.kwargs
        assert called_kwargs["payload"] == {"message": "hello"}
        assert called_kwargs["message_id"] == "immutable-id"
        assert called_kwargs["message_type"] == "direct_message"


@pytest.mark.asyncio
async def test_fetch_latest_filesystem_messages_handles_deletion(tmp_path: Path) -> None:
    """Filesystem latest fetch should delete messages when requested."""

    config = FileSystemMailboxConfig(base_path=str(tmp_path))
    service = FileSystemMailboxService("agent", config)
    await service.connect()

    inbox = service.inbox_path
    inbox.mkdir(parents=True, exist_ok=True)
    message_file = inbox / "1.json"
    message_file.write_text(
        '{"message_id": "1", "recipient": "agent", "sender": "sender", "payload": {"v": 1}}',
        encoding="utf-8",
    )

    await cli._fetch_latest_filesystem_messages(service, count=5, delete=True)

    assert not message_file.exists()


@pytest.mark.asyncio
async def test_fetch_latest_messages_ack_and_trim(monkeypatch: pytest.MonkeyPatch) -> None:
    """Redis latest fetch should acknowledge and trim when requested."""

    service = mock.create_autospec(cli.RedisMailboxService, instance=True)
    service.agent_id = "agent"
    service.inbox_stream = "stream"
    service.connect = mock.AsyncMock()
    service.stop = mock.AsyncMock()
    service._client = mock.AsyncMock()
    service._client.xrevrange.return_value = [("1-0", {"field": "value"})]

    message = mock.Mock()
    message.recipient = "agent"
    message.sender = "sender"
    message.message_type = "direct_message"
    message.payload = {"field": "value"}

    with mock.patch.object(cli.MailboxMessage, "from_redis_fields", return_value=message):
        await cli._fetch_latest_messages(service, count=1, ack=True, trim=True)

    service.connect.assert_awaited_once()
    service._client.xack.assert_awaited_once_with("stream", "agent:group", "1-0")
    service._client.xdel.assert_awaited_once_with("stream", "1-0")
    service.stop.assert_awaited_once()


"""Local file system backed mailbox service for intra-host Beast agents."""

from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Awaitable, Callable, Dict, List, Optional
from uuid import uuid4

from .redis_mailbox import MailboxMessage

_TEMP_FILE_SUFFIXES = (".tmp",)


@dataclass
class FileSystemMailboxConfig:
    """Configuration for file system based mailboxes."""

    base_path: str = "/tmp/beast_mailbox"
    poll_interval: float = 0.5
    mkdir_mode: int = 0o755


def _create_fs_config_from_env() -> FileSystemMailboxConfig:
    """Create FileSystemMailboxConfig from environment variables.

    Environment variables:
        BEAST_MAILBOX_FS_ROOT: Root directory for mailbox data (default: /tmp/beast_mailbox)
        BEAST_MAILBOX_FS_POLL_INTERVAL: Poll interval in seconds (default: 0.5)
        BEAST_MAILBOX_FS_MKDIR_MODE: Directory mode (octal string, default: 755)
    """

    base_path = os.getenv("BEAST_MAILBOX_FS_ROOT", "/tmp/beast_mailbox")

    try:
        poll_interval = float(os.getenv("BEAST_MAILBOX_FS_POLL_INTERVAL", "0.5"))
    except ValueError:
        poll_interval = 0.5

    try:
        mkdir_mode_env = os.getenv("BEAST_MAILBOX_FS_MKDIR_MODE")
        mkdir_mode = int(mkdir_mode_env, 8) if mkdir_mode_env else 0o755
    except ValueError:
        mkdir_mode = 0o755

    return FileSystemMailboxConfig(
        base_path=base_path,
        poll_interval=poll_interval,
        mkdir_mode=mkdir_mode,
    )


class FileSystemMailboxService:
    """Async mailbox service implemented on top of the local file system.

    Messages are serialized to JSON files located under `{base_path}/{agent_id}/inbox`.
    Atomic `os.replace` is used to avoid tearing during writes. A background task polls
    the inbox directory and dispatches received messages to registered async handlers.
    """

    def __init__(
        self,
        agent_id: str,
        config: Optional[FileSystemMailboxConfig] = None,
    ) -> None:
        self.agent_id = agent_id
        self.config = config or _create_fs_config_from_env()
        self.logger = logging.getLogger(f"beast_mailbox.fs.{agent_id}")
        self._handlers: List[Callable[[MailboxMessage], Awaitable[None]]] = []
        self._running = False
        self._processing_task: Optional[asyncio.Task] = None
        self._connected = False

    @property
    def inbox_path(self) -> Path:
        """Return the agent's inbox directory."""

        return Path(self.config.base_path, self.agent_id, "inbox")

    async def connect(self) -> None:
        """Ensure the inbox directory exists."""

        if self._connected:
            return

        inbox_path = self.inbox_path
        try:
            await asyncio.to_thread(
                inbox_path.mkdir,
                mode=self.config.mkdir_mode,
                parents=True,
                exist_ok=True,
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            self.logger.error("Failed to create inbox directory %s: %s", inbox_path, exc)
            raise

        self._connected = True

    def register_handler(self, handler: Callable[[MailboxMessage], Awaitable[None]]) -> None:
        """Register an async handler to process incoming messages."""

        self._handlers.append(handler)

    async def start(self) -> bool:
        """Start watching the inbox directory for new messages."""

        await self.connect()
        self._running = True
        self._processing_task = asyncio.create_task(self._consume_loop())
        return True

    async def stop(self) -> None:
        """Stop the background watcher task."""

        self._running = False
        if self._processing_task:
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
            except Exception:
                pass
            finally:
                self._processing_task = None

    async def send_message(
        self,
        recipient: str,
        payload: Dict,
        message_type: str = "direct_message",
        message_id: Optional[str] = None,
    ) -> str:
        """Write a message file into the recipient's inbox."""

        msg = MailboxMessage(
            message_id=message_id or str(uuid4()),
            sender=self.agent_id,
            recipient=recipient,
            payload=payload,
            message_type=message_type,
        )

        recipient_inbox = Path(self.config.base_path, recipient, "inbox")
        await asyncio.to_thread(
            recipient_inbox.mkdir,
            mode=self.config.mkdir_mode,
            parents=True,
            exist_ok=True,
        )

        filename = f"{msg.timestamp:.9f}_{msg.message_id}.json"
        destination = recipient_inbox / filename
        tmp_file = destination.with_suffix(".tmp")

        data = {
            "message_id": msg.message_id,
            "sender": msg.sender,
            "recipient": msg.recipient,
            "payload": msg.payload,
            "message_type": msg.message_type,
            "timestamp": msg.timestamp,
        }

        def _write_file() -> None:
            with tmp_file.open("w", encoding="utf-8") as handle:
                json.dump(data, handle)
            os.replace(tmp_file, destination)

        await asyncio.to_thread(_write_file)
        self.logger.debug("Sent file system message %s to %s", msg.message_id, destination)
        return msg.message_id

    async def _consume_loop(self) -> None:
        """Background task that polls the inbox directory for messages."""

        while self._running:
            try:
                await self._process_pending_files()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self.logger.exception("File system mailbox loop error: %s", exc)

            await asyncio.sleep(self.config.poll_interval)

    async def _process_pending_files(self) -> None:
        """Process all message files currently present."""

        inbox_path = self.inbox_path
        if not inbox_path.exists():
            return

        await asyncio.to_thread(self._cleanup_temporary_files, inbox_path)

        if not self._handlers:
            self.logger.debug("No handlers registered for inbox %s", inbox_path)
            return

        files = sorted(
            [
                entry
                for entry in inbox_path.iterdir()
                if entry.is_file() and entry.suffix == ".json"
            ],
            key=lambda path: path.name,
        )

        for path in files:
            try:
                message = await asyncio.to_thread(self._read_message_file, path)
            except FileNotFoundError:
                continue  # File may have been processed concurrently
            except json.JSONDecodeError as exc:
                self.logger.error("Failed to decode message file %s: %s", path, exc)
                await asyncio.to_thread(path.unlink, missing_ok=True)
                continue

            await self._dispatch(message)
            await asyncio.to_thread(path.unlink, missing_ok=True)

    def _read_message_file(self, path: Path) -> MailboxMessage:
        """Read a JSON message file."""

        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        return MailboxMessage(
            message_id=data["message_id"],
            sender=data["sender"],
            recipient=data["recipient"],
            payload=data["payload"],
            message_type=data.get("message_type", "direct_message"),
            timestamp=float(data.get("timestamp", 0.0)),
        )

    async def _dispatch(self, message: MailboxMessage) -> None:
        """Dispatch message to registered handlers."""

        for handler in list(self._handlers):
            try:
                await handler(message)
                self.logger.debug(
                    "Delivered file system message %s to handler %s",
                    message.message_id,
                    getattr(handler, "__name__", repr(handler)),
                )
            except Exception as exc:
                self.logger.exception("File system mailbox handler failed: %s", exc)

    def _cleanup_temporary_files(self, inbox_path: Path) -> None:
        """Remove orphaned temporary files left from interrupted writes."""

        for entry in inbox_path.iterdir():
            if entry.is_file() and entry.suffix in _TEMP_FILE_SUFFIXES:
                try:
                    entry.unlink()
                except FileNotFoundError:  # pragma: no cover - race condition
                    continue



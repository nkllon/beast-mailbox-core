#!/usr/bin/env python3
"""Tests for pending message recovery functionality."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from beast_mailbox_core import MailboxConfig, MailboxMessage, RecoveryMetrics, RedisMailboxService


@pytest.fixture
def config():
    """Test configuration."""
    return MailboxConfig(host="localhost", port=6379, db=15)


@pytest.fixture
def service(config):
    """Create service instance."""
    return RedisMailboxService("test-agent", config)


class TestRecoveryConfiguration:
    """Test recovery configuration options."""

    def test_recovery_enabled_by_default(self):
        """Test recovery is enabled by default."""
        config = MailboxConfig()
        assert config.enable_recovery is True
        assert config.recovery_min_idle_time == 0
        assert config.recovery_batch_size == 50

    def test_recovery_can_be_disabled(self):
        """Test recovery can be disabled."""
        config = MailboxConfig(enable_recovery=False)
        assert config.enable_recovery is False

    def test_recovery_batch_size_configurable(self):
        """Test recovery batch size is configurable."""
        config = MailboxConfig(recovery_batch_size=100)
        assert config.recovery_batch_size == 100

    def test_recovery_min_idle_time_configurable(self):
        """Test recovery min idle time is configurable."""
        config = MailboxConfig(recovery_min_idle_time=60)
        assert config.recovery_min_idle_time == 60


class TestRecoveryWithoutHandlers:
    """Test recovery behavior when no handlers are registered."""

    @pytest.mark.asyncio
    async def test_recovery_skips_when_no_handlers(self, service):
        """Test recovery skips gracefully when no handlers registered."""
        mock_client = AsyncMock()
        service._client = mock_client
        
        metrics = await service._recover_pending_messages()
        
        assert metrics.total_recovered == 0
        assert metrics.batches_processed == 0
        # Client should not be called when no handlers
        mock_client.assert_not_called()


class TestRecoveryWithHandlers:
    """Test recovery with handlers registered."""

    @pytest.mark.asyncio
    async def test_recovery_skips_when_disabled(self, service):
        """Test recovery skips when disabled in config."""
        service.config.enable_recovery = False
        mock_client = AsyncMock()
        service._client = mock_client
        
        async def handler(msg):
            pass
        
        service.register_handler(handler)
        
        metrics = await service._recover_pending_messages()
        
        assert metrics.total_recovered == 0
        # Client should not be called when disabled
        mock_client.assert_not_called()

    @pytest.mark.asyncio
    async def test_recovery_handles_nogroup_error(self, service):
        """Test recovery handles NOGROUP error gracefully."""
        async def handler(msg):
            pass
        
        service.register_handler(handler)
        
        mock_client = AsyncMock()
        mock_client.xpending_range = AsyncMock(
            side_effect=Exception("NOGROUP Consumer Group does not exist")
        )
        service._client = mock_client
        
        metrics = await service._recover_pending_messages()
        
        assert metrics.total_recovered == 0
        assert metrics.batches_processed == 0

    @pytest.mark.asyncio
    async def test_recovery_no_pending_messages(self, service):
        """Test recovery when no pending messages exist."""
        async def handler(msg):
            pass
        
        service.register_handler(handler)
        
        mock_client = AsyncMock()
        mock_client.xpending_range = AsyncMock(return_value=[])
        service._client = mock_client
        
        metrics = await service._recover_pending_messages()
        
        assert metrics.total_recovered == 0
        assert metrics.batches_processed == 0

    @pytest.mark.asyncio
    async def test_recovery_processes_pending_messages(self, service):
        """Test recovery processes pending messages successfully."""
        received_messages = []
        
        async def handler(msg):
            received_messages.append(msg)
        
        service.register_handler(handler)
        
        # Mock pending info
        mock_pending_info = [("0-0", "test-consumer", 1000, 1)]
        
        # Mock messages to claim
        mock_message_id = "1234567890-0"
        mock_fields = {
            b"message_id": b"msg-1",
            b"sender": b"alice",
            b"recipient": b"test-agent",
            b"payload": b'{"text": "hello"}',
            b"message_type": b"direct_message",
            b"timestamp": b"1.0",
        }
        
        mock_claimed_messages = [(mock_message_id, mock_fields)]
        
        mock_client = AsyncMock()
        mock_client.xpending_range = AsyncMock(return_value=mock_pending_info)
        mock_client.xautoclaim = AsyncMock(
            side_effect=[
                ("1234567890-0", mock_claimed_messages, []),  # First batch - returns messages
                ("0-0", [], []),  # Second batch - empty, signals completion
            ]
        )
        mock_client.xack = AsyncMock()
        service._client = mock_client
        
        metrics = await service._recover_pending_messages()
        
        assert metrics.total_recovered == 1
        assert metrics.batches_processed == 1
        assert len(received_messages) == 1
        assert received_messages[0].sender == "alice"
        mock_client.xack.assert_called_once()

    @pytest.mark.asyncio
    async def test_recovery_processes_multiple_batches(self, service):
        """Test recovery processes multiple batches of messages."""
        received_messages = []
        
        async def handler(msg):
            received_messages.append(msg)
        
        service.register_handler(handler)
        service.config.recovery_batch_size = 2
        
        mock_pending_info = [("0-0", "test-consumer", 1000, 3)]
        
        # First batch: 2 messages
        mock_message_1 = ("100-0", {
            b"message_id": b"msg-1",
            b"sender": b"alice",
            b"recipient": b"test-agent",
            b"payload": b'{"text": "msg1"}',
            b"message_type": b"direct_message",
            b"timestamp": b"1.0",
        })
        mock_message_2 = ("101-0", {
            b"message_id": b"msg-2",
            b"sender": b"bob",
            b"recipient": b"test-agent",
            b"payload": b'{"text": "msg2"}',
            b"message_type": b"direct_message",
            b"timestamp": b"2.0",
        })
        
        # Second batch: 1 message
        mock_message_3 = ("102-0", {
            b"message_id": b"msg-3",
            b"sender": b"charlie",
            b"recipient": b"test-agent",
            b"payload": b'{"text": "msg3"}',
            b"message_type": b"direct_message",
            b"timestamp": b"3.0",
        })
        
        mock_client = AsyncMock()
        mock_client.xpending_range = AsyncMock(return_value=mock_pending_info)
        mock_client.xautoclaim = AsyncMock(
            side_effect=[
                ("102-0", [mock_message_1, mock_message_2], []),
                ("0-0", [mock_message_3], []),
                ("0-0", [], []),
            ]
        )
        mock_client.xack = AsyncMock()
        service._client = mock_client
        
        metrics = await service._recover_pending_messages()
        
        assert metrics.total_recovered == 3
        assert metrics.batches_processed == 2
        assert len(received_messages) == 3
        assert mock_client.xack.call_count == 3

    @pytest.mark.asyncio
    async def test_recovery_handles_handler_errors(self, service):
        """Test recovery continues even if handler raises exception."""
        received_messages = []
        
        async def good_handler(msg):
            received_messages.append(msg)
        
        async def bad_handler(msg):
            raise ValueError("Handler failed!")
        
        service.register_handler(bad_handler)
        service.register_handler(good_handler)
        
        mock_pending_info = [("0-0", "test-consumer", 1000, 1)]
        mock_message_id = "1234567890-0"
        mock_fields = {
            b"message_id": b"msg-1",
            b"sender": b"alice",
            b"recipient": b"test-agent",
            b"payload": b'{"text": "hello"}',
            b"message_type": b"direct_message",
            b"timestamp": b"1.0",
        }
        
        mock_client = AsyncMock()
        mock_client.xpending_range = AsyncMock(return_value=mock_pending_info)
        mock_client.xautoclaim = AsyncMock(
            side_effect=[
                ("1234567890-0", [(mock_message_id, mock_fields)], []),
                ("0-0", [], []),
            ]
        )
        mock_client.xack = AsyncMock()
        service._client = mock_client
        
        # Should not raise
        metrics = await service._recover_pending_messages()
        
        # Even though one handler failed, the message is still processed
        assert metrics.total_recovered == 1
        assert len(received_messages) == 1


class TestRecoveryCallback:
    """Test recovery callback mechanism."""

    @pytest.mark.asyncio
    async def test_recovery_callback_invoked(self, service):
        """Test recovery callback is invoked with metrics."""
        callback_invoked = False
        callback_metrics = None
        
        async def handler(msg):
            pass
        
        async def callback(metrics):
            nonlocal callback_invoked, callback_metrics
            callback_invoked = True
            callback_metrics = metrics
        
        service.register_handler(handler)
        service.recovery_callback = callback
        
        mock_client = AsyncMock()
        mock_client.xpending_range = AsyncMock(return_value=[])
        service._client = mock_client
        
        await service._recover_pending_messages()
        
        assert callback_invoked is True
        assert callback_metrics is not None
        assert isinstance(callback_metrics, RecoveryMetrics)

    @pytest.mark.asyncio
    async def test_recovery_callback_handles_errors(self, service):
        """Test recovery continues even if callback raises exception."""
        async def handler(msg):
            pass
        
        async def callback(metrics):
            raise RuntimeError("Callback failed!")
        
        service.register_handler(handler)
        service.recovery_callback = callback
        
        mock_client = AsyncMock()
        mock_client.xpending_range = AsyncMock(return_value=[])
        service._client = mock_client
        
        # Should not raise
        metrics = await service._recover_pending_messages()
        assert metrics is not None
    


class TestRecoveryIntegrationWithStart:
    """Test recovery integration with service start."""

    @pytest.mark.asyncio
    async def test_start_runs_recovery_before_consume_loop(self, service):
        """Test start() runs recovery before launching consume loop."""
        async def handler(msg):
            pass
        
        service.register_handler(handler)
        
        mock_client = AsyncMock()
        mock_client.ping = AsyncMock()
        mock_client.xgroup_create = AsyncMock()
        mock_client.xpending_range = AsyncMock(return_value=[])
        # Make xreadgroup return immediately - don't block
        mock_client.xreadgroup = AsyncMock(return_value=[])
        service._client = mock_client
        
        # Track recovery execution
        recovery_called = False
        original_recover = service._recover_pending_messages
        
        async def mock_recover():
            nonlocal recovery_called
            recovery_called = True
            return await original_recover()
        
        service._recover_pending_messages = mock_recover
        
        # Start the service - recovery should run first
        result = await service.start()
        
        assert result is True
        assert recovery_called  # Recovery was called before consume loop started
        
        # Cleanup - stop immediately (doesn't wait for consume loop)
        await service.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])




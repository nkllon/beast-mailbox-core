#!/usr/bin/env python3
"""Tests specifically designed to boost coverage to 90%+."""

import argparse
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from beast_mailbox_core.cli import run_service_async
from beast_mailbox_core.redis_mailbox import RedisMailboxService, MailboxConfig


class TestRunServiceAsyncLatestMode:
    """Test run_service_async in one-shot latest mode."""

    @pytest.mark.asyncio
    async def test_run_service_async_latest_mode(self):
        """Test run_service_async with --latest flag (one-shot mode)."""
        args = argparse.Namespace(
            agent_id='coverage-test',
            redis_host='localhost',
            redis_port=6379,
            redis_password=None,
            redis_db=15,
            stream_prefix='test:mailbox',
            maxlen=1000,
            poll_interval=2.0,
            latest=True,  # One-shot mode
            count=5,
            ack=False,
            trim=False,
            echo=False,
        )
        
        # Mock the _fetch_latest_messages function since we're testing the routing logic
        with patch('beast_mailbox_core.cli._fetch_latest_messages', new_callable=AsyncMock) as mock_fetch:
            await run_service_async(args)
            
            # Verify _fetch_latest_messages was called with correct args
            mock_fetch.assert_called_once()
            call_args = mock_fetch.call_args
            assert call_args[0][1] == 5  # count
            assert call_args[0][2] is False  # ack
            assert call_args[0][3] is False  # trim

    @pytest.mark.asyncio
    async def test_run_service_async_latest_with_ack_and_trim(self):
        """Test run_service_async with --latest --ack --trim flags."""
        args = argparse.Namespace(
            agent_id='coverage-test',
            redis_host='localhost',
            redis_port=6379,
            redis_password=None,
            redis_db=15,
            stream_prefix='test:mailbox',
            maxlen=1000,
            poll_interval=2.0,
            latest=True,
            count=10,
            ack=True,
            trim=True,
            echo=False,
        )
        
        with patch('beast_mailbox_core.cli._fetch_latest_messages', new_callable=AsyncMock) as mock_fetch:
            await run_service_async(args)
            
            call_args = mock_fetch.call_args
            assert call_args[0][1] == 10  # count
            assert call_args[0][2] is True  # ack
            assert call_args[0][3] is True  # trim

    @pytest.mark.asyncio
    async def test_run_service_async_creates_config_correctly(self):
        """Test that run_service_async creates MailboxConfig with all parameters."""
        args = argparse.Namespace(
            agent_id='config-test',
            redis_host='redis.example.com',
            redis_port=6380,
            redis_password='secret123',
            redis_db=7,
            stream_prefix='custom:prefix',
            maxlen=5000,
            poll_interval=1.5,
            latest=True,
            count=1,
            ack=False,
            trim=False,
            echo=False,
        )
        
        created_config = None
        
        # Capture the config that gets created
        original_service_init = RedisMailboxService.__init__
        def capture_config(self, agent_id, config=None):
            nonlocal created_config
            created_config = config
            original_service_init(self, agent_id, config)
        
        with patch('beast_mailbox_core.cli._fetch_latest_messages', new_callable=AsyncMock):
            with patch.object(RedisMailboxService, '__init__', capture_config):
                await run_service_async(args)
        
        assert created_config is not None
        assert created_config.host == 'redis.example.com'
        assert created_config.port == 6380
        assert created_config.password == 'secret123'
        assert created_config.db == 7
        assert created_config.stream_prefix == 'custom:prefix'
        assert created_config.max_stream_length == 5000
        assert created_config.poll_interval == 1.5


class TestConsumeLoopEntry:
    """Test the entry point of _consume_loop (before infinite loop)."""

    @pytest.mark.asyncio
    async def test_consume_loop_asserts_client_exists(self):
        """Test that _consume_loop asserts client is not None."""
        config = MailboxConfig(host="localhost", db=15)
        service = RedisMailboxService("test-agent", config)
        
        # Client is None - should fail assertion
        service._running = True
        
        with pytest.raises(AssertionError):
            await service._consume_loop()


class TestAdditionalCoverage:
    """Tests to cover remaining edge cases."""

    @pytest.mark.asyncio
    async def test_run_service_async_with_echo_handler(self):
        """Test that echo handler is registered and called when --echo flag is set."""
        from beast_mailbox_core.cli import MailboxMessage
        
        args = argparse.Namespace(
            agent_id='echo-test',
            redis_host='localhost',
            redis_port=6379,
            redis_password=None,
            redis_db=0,
            stream_prefix='test:mailbox',
            maxlen=1000,
            poll_interval=2.0,
            latest=False,  # Service mode
            echo=True,  # Echo flag set
        )
        
        # Track if echo handler was called
        echo_called = []
        
        # Create a mock service that captures the handler
        mock_service = MagicMock()
        mock_service.start = AsyncMock(return_value=True)
        mock_service.stop = AsyncMock()
        mock_service.register_handler = MagicMock(side_effect=lambda h: echo_called.append(h))
        
        with patch('beast_mailbox_core.cli.RedisMailboxService', return_value=mock_service):
            with patch('beast_mailbox_core.cli.get_redis_config_from_args', return_value={'host': 'localhost', 'port': 6379, 'password': None, 'db': 0}):
                with patch('beast_mailbox_core.cli.MailboxConfig'):
                    with patch('asyncio.Event') as mock_event:
                        mock_event_instance = MagicMock()
                        mock_event.return_value = mock_event_instance
                        
                        async def raise_interrupt():
                            # Call the echo handler before raising
                            if echo_called:
                                test_msg = MailboxMessage(
                                    message_id="test-msg",
                                    sender="test-sender",
                                    recipient="echo-test",
                                    message_type="test",
                                    payload={"test": "data"}
                                )
                                await echo_called[0](test_msg)
                            raise KeyboardInterrupt()
                        
                        mock_event_instance.wait = raise_interrupt
                        
                        await run_service_async(args)
                        
                        # Verify echo handler was registered
                        mock_service.register_handler.assert_called_once()
                        
        # Mock service.start() to return False (failure case)
        with patch.object(RedisMailboxService, 'start', new_callable=AsyncMock, return_value=False):
            with pytest.raises(SystemExit, match="Failed to start mailbox service"):
                await run_service_async(args)
    
    @pytest.mark.asyncio
    async def test_run_service_async_handles_keyboard_interrupt(self):
        """Test that run_service_async handles KeyboardInterrupt gracefully."""
        args = argparse.Namespace(
            agent_id='interrupt-test',
            redis_host='localhost',
            redis_port=6379,
            redis_password=None,
            redis_db=0,
            stream_prefix='test:mailbox',
            maxlen=1000,
            poll_interval=2.0,
            latest=False,
            echo=False,
        )
        
        # Mock service to start successfully, then raise KeyboardInterrupt
        mock_service = MagicMock()
        mock_service.start = AsyncMock(return_value=True)
        mock_service.stop = AsyncMock()
        mock_service.register_handler = MagicMock()
        
        with patch('beast_mailbox_core.cli.RedisMailboxService', return_value=mock_service):
            with patch('beast_mailbox_core.cli.get_redis_config_from_args', return_value={'host': 'localhost', 'port': 6379, 'password': None, 'db': 0}):
                with patch('beast_mailbox_core.cli.MailboxConfig') as mock_config_class:
                    mock_config = MagicMock()
                    mock_config_class.return_value = mock_config
                    
                    # Mock asyncio.Event().wait() to raise KeyboardInterrupt
                    with patch('asyncio.Event') as mock_event:
                        mock_event_instance = MagicMock()
                        mock_event.return_value = mock_event_instance
                        
                        async def raise_interrupt():
                            raise KeyboardInterrupt()
                        
                        mock_event_instance.wait = raise_interrupt
                        
                        # Should not raise - should handle gracefully
                        await run_service_async(args)
                        
                        # Verify service.stop() was called
                        mock_service.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_acknowledge_messages_with_xgroup_create_failure(self):
        """Test _acknowledge_messages when xgroup_create raises non-BUSYGROUP error."""
        from beast_mailbox_core.cli import _acknowledge_messages
        
        mock_client = AsyncMock()
        mock_client.xgroup_create = AsyncMock(side_effect=Exception("Permission denied"))
        mock_client.xack = AsyncMock(return_value=1)
        
        # Should log warning but still proceed to ack
        await _acknowledge_messages(mock_client, "stream", "group", [b"msg1"])
        
        # Verify xack was still called despite group creation failure
        mock_client.xack.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_latest_messages_client_unavailable(self):
        """Test _fetch_latest_messages raises SystemExit when client is None."""
        from beast_mailbox_core.cli import _fetch_latest_messages
        
        config = MailboxConfig(host="localhost", db=15)
        service = RedisMailboxService("test-agent", config)
        
        # Mock connect to leave client as None
        async def failing_connect():
            service._client = None
        
        service.connect = failing_connect
        
        with pytest.raises(SystemExit, match="Redis client unavailable"):
            await _fetch_latest_messages(service, count=1, ack=False, trim=False)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


#!/usr/bin/env python3
"""Integration tests for pending message recovery.

These tests verify recovery end-to-end with a real Redis instance.
Set REDIS_URL environment variable to run against external Redis.
"""

import asyncio
import os
import pytest

from beast_mailbox_core import MailboxConfig, MailboxMessage, RecoveryMetrics, RedisMailboxService


def pytest_generate_tests(metafunc):
    """Generate parametrized tests with different Redis configurations."""
    if "redis_url" in metafunc.fixturenames:
        # Check for REDIS_URL environment variable
        redis_url = os.environ.get("REDIS_URL")
        if redis_url:
            # External Redis instance provided
            host = redis_url
            port = 6379
        else:
            # Skip tests unless external Redis is configured
            pytest.skip("Set REDIS_URL environment variable to run integration tests")


@pytest.fixture
def integration_config(request):
    """Create test configuration for integration tests."""
    redis_host = request.param if hasattr(request, "param") else "localhost"
    return MailboxConfig(
        host=redis_host,
        port=6379,
        db=15,  # Use separate DB for testing
        stream_prefix="test:mailbox:recovery",
        max_stream_length=100,
        poll_interval=0.1,
        enable_recovery=True,
        recovery_batch_size=50,
    )


@pytest.fixture
def agent_id():
    """Return test agent ID."""
    import time
    return f"test-agent-{time.time()}"


class TestRecoveryIntegration:
    """Integration tests for recovery with real Redis."""

    @pytest.mark.asyncio
    async def test_recovery_processes_pending_message(self, integration_config, agent_id):
        """Test recovery processes a pending message end-to-end."""
        # Clean up any existing test data
        service1 = RedisMailboxService("temp-cleanup", integration_config)
        await service1.connect()
        if service1._client:
            try:
                stream = service1.inbox_stream
                await service1._client.delete(stream)
                await service1._client.xgroup_destroy(service1.inbox_stream, f"{agent_id}:group")
            except Exception:
                pass
        await service1.stop()
        
        # Create service and send a message
        sender = RedisMailboxService("sender", integration_config)
        await sender.connect()
        
        message_id = await sender.send_message(
            recipient=agent_id,
            payload={"test": "recovery", "value": 42}
        )
        
        await sender.stop()
        
        # Now create a consumer, read the message to move it to PEL
        receiver = RedisMailboxService(agent_id, integration_config)
        await receiver.connect()
        
        # Read the message to move it to pending list
        await receiver._client.xreadgroup(
            groupname=receiver._consumer_group,
            consumername="temp-consumer",
            streams={receiver.inbox_stream: ">"},
            count=1,
        )
        
        await receiver.stop()
        
        # Now create a new service with a handler and start recovery
        received_messages = []
        recovery_metrics = None
        
        async def handler(msg: MailboxMessage):
            received_messages.append(msg)
        
        async def callback(metrics: RecoveryMetrics):
            nonlocal recovery_metrics
            recovery_metrics = metrics
        
        service = RedisMailboxService(agent_id, integration_config, recovery_callback=callback)
        service.register_handler(handler)
        
        # Start should trigger recovery
        result = await service.start()
        
        # Give it a moment to complete
        await asyncio.sleep(0.5)
        
        assert result is True
        
        # Stop the service
        await service.stop()
        
        # Verify message was recovered
        assert len(received_messages) == 1
        assert received_messages[0].message_id == message_id
        assert received_messages[0].payload["test"] == "recovery"
        assert recovery_metrics is not None
        assert recovery_metrics.total_recovered == 1
        
        # Verify message was acknowledged (it shouldn't be in pending anymore)
        check_service = RedisMailboxService(agent_id, integration_config)
        await check_service.connect()
        if check_service._client:
            pending_info = await check_service._client.xpending_range(
                name=check_service.inbox_stream,
                groupname=check_service._consumer_group,
                min="-",
                max="+",
                count=10,
            )
            assert len(pending_info) == 0
        
        await check_service.stop()

    @pytest.mark.asyncio
    async def test_recovery_handles_multiple_pending_messages(self, integration_config, agent_id):
        """Test recovery handles multiple pending messages."""
        agent_id = f"{agent_id}-multi"
        
        # Clean up
        service1 = RedisMailboxService("temp-cleanup", integration_config)
        await service1.connect()
        if service1._client:
            try:
                stream = f"{integration_config.stream_prefix}:{agent_id}:in"
                await service1._client.delete(stream)
                await service1._client.xgroup_destroy(stream, f"{agent_id}:group")
            except Exception:
                pass
        await service1.stop()
        
        # Send multiple messages
        sender = RedisMailboxService("sender", integration_config)
        await sender.connect()
        
        message_ids = []
        for i in range(5):
            msg_id = await sender.send_message(
                recipient=agent_id,
                payload={"index": i, "test": "multi-recovery"}
            )
            message_ids.append(msg_id)
        
        await sender.stop()
        
        # Read all messages to move them to PEL
        receiver = RedisMailboxService(agent_id, integration_config)
        await receiver.connect()
        
        # Read all messages
        await receiver._client.xreadgroup(
            groupname=receiver._consumer_group,
            consumername="temp-consumer",
            streams={receiver.inbox_stream: ">"},
            count=10,
        )
        
        await receiver.stop()
        
        # Now recover them
        received_messages = []
        
        async def handler(msg: MailboxMessage):
            received_messages.append(msg)
        
        service = RedisMailboxService(agent_id, integration_config)
        service.register_handler(handler)
        service.config.recovery_batch_size = 2  # Test batching
        
        result = await service.start()
        await asyncio.sleep(0.5)
        
        assert result is True
        assert len(received_messages) == 5
        
        await service.stop()

    @pytest.mark.asyncio
    async def test_recovery_no_pending_skips_gracefully(self, integration_config, agent_id):
        """Test recovery skips gracefully when no pending messages."""
        agent_id = f"{agent_id}-no-pending"
        
        received_messages = []
        
        async def handler(msg: MailboxMessage):
            received_messages.append(msg)
        
        service = RedisMailboxService(agent_id, integration_config)
        service.register_handler(handler)
        
        # Start should complete recovery even with no pending messages
        result = await service.start()
        await asyncio.sleep(0.5)
        
        assert result is True
        assert len(received_messages) == 0
        
        await service.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])




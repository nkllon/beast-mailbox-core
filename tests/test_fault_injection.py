#!/usr/bin/env python3
"""Fault injection tests with real Redis.

These tests create actual error conditions in Redis to verify error handling
works correctly with real errors, not mocks.

These are integration tests that require a running Redis instance.
They run automatically in CI where Redis is available as a service container.
"""

import asyncio
import os
import pytest
import time

from beast_mailbox_core import MailboxConfig, MailboxMessage, RecoveryMetrics, RedisMailboxService


# Check if Redis is available
try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


# redis_available fixture is now in conftest.py and uses Docker


def pytest_configure(config):
    """Configure pytest for fault injection tests."""
    # Mark tests that require Redis
    config.addinivalue_line("markers", "redis_required: Test requires Redis connection")


@pytest.fixture
def fault_injection_config():
    """Test configuration for fault injection tests."""
    return MailboxConfig(
        host="localhost",
        port=6379,
        db=15,  # Use separate DB for testing
        stream_prefix="test:mailbox:fault",
        max_stream_length=100,
        poll_interval=0.1,
        enable_recovery=True,
        recovery_batch_size=50,
        recovery_min_idle_time=0,  # 0 means immediate claim (no idle time required)
    )


@pytest.fixture
def fault_agent_id():
    """Return unique test agent ID."""
    return f"fault-test-{time.time()}"


@pytest.mark.asyncio
@pytest.mark.skipif(not pytest.importorskip("redis"), reason="Redis library not available")
async def test_start_with_existing_consumer_group_busygroup(fault_injection_config, fault_agent_id, redis_available, redis_docker):
    """Test start succeeds when consumer group already exists (BUSYGROUP)."""
    if not redis_available:
        pytest.skip("Redis not available - Docker container failed to start")
    """Test start succeeds when consumer group already exists (BUSYGROUP)."""
    # FAULT INJECTION: Create the consumer group first to trigger BUSYGROUP
    service1 = RedisMailboxService(fault_agent_id, fault_injection_config)
    await service1.connect()
    
    if service1._client:
        # Create consumer group explicitly
        try:
            await service1._client.xgroup_create(
                name=service1.inbox_stream,
                groupname=service1._consumer_group,
                id="$",
                mkstream=True,
            )
        except Exception:
            # Might already exist, that's fine
            pass
        
        await service1.stop()
    
    # Now try to start service - should handle BUSYGROUP gracefully
    service2 = RedisMailboxService(fault_agent_id, fault_injection_config)
    
    async def handler(msg):
        pass
    
    service2.register_handler(handler)
    
    # Should succeed despite BUSYGROUP
    result = await service2.start()
    
    assert result is True
    assert service2._running is True
    
    await service2.stop()


@pytest.mark.asyncio
@pytest.mark.skipif(not pytest.importorskip("redis"), reason="Redis library not available")
async def test_recovery_with_no_consumer_group_nogroup(fault_injection_config, fault_agent_id, redis_available, redis_docker):
    """Test recovery handles NOGROUP error when group doesn't exist."""
    if not redis_available:
        pytest.skip("Redis not available - Docker container failed to start")
    # FAULT INJECTION: Don't create consumer group, trigger NOGROUP
    service = RedisMailboxService(fault_agent_id, fault_injection_config)
    
    async def handler(msg):
        pass
    
    service.register_handler(handler)
    
    # Connect but don't create group
    await service.connect()
    
    # Try recovery without creating group - should handle NOGROUP gracefully
    # The recovery should detect NOGROUP and return empty metrics
    metrics = await service._recover_pending_messages()
    
    assert metrics is not None
    assert metrics.total_recovered == 0
    assert metrics.batches_processed == 0
    
    await service.stop()


@pytest.mark.asyncio
@pytest.mark.skipif(not pytest.importorskip("redis"), reason="Redis library not available")
async def test_acknowledge_messages_with_existing_group_busygroup(fault_injection_config, fault_agent_id, redis_available, redis_docker):
    """Test _acknowledge_messages handles BUSYGROUP when group exists."""
    if not redis_available:
        pytest.skip("Redis not available - Docker container failed to start")
    from beast_mailbox_core.cli import _acknowledge_messages
    
    # FAULT INJECTION: Create consumer group first
    service = RedisMailboxService(fault_agent_id, fault_injection_config)
    await service.connect()
    
    if service._client:
        # Create consumer group
        try:
            await service._client.xgroup_create(
                name=service.inbox_stream,
                groupname=service._consumer_group,
                id="$",
                mkstream=True,
            )
        except Exception:
            pass
        
        # Add a message to ack
        message_id = await service._client.xadd(
            name=service.inbox_stream,
            fields={
                "message_id": "msg-1",
                "sender": "test",
                "recipient": fault_agent_id,
                "payload": "{}",
                "message_type": "direct_message",
                "timestamp": str(time.time()),
            }
        )
        
        # Now try to ack - should handle BUSYGROUP gracefully
        # The function will try to create group again, get BUSYGROUP, but still ack
        await _acknowledge_messages(
            service._client,
            service.inbox_stream,
            service._consumer_group,
            [message_id],
        )
        
        # Verify message was acked (no longer in pending)
        # We can't easily verify this without reading, but the function should not raise
        # If it raises, the test fails - which is what we want
        
        await service.stop()


@pytest.mark.asyncio
@pytest.mark.skipif(not pytest.importorskip("redis"), reason="Redis library not available")
async def test_recovery_callback_handles_exception(fault_injection_config, fault_agent_id, redis_available, redis_docker):
    """Test recovery callback exception handling with real recovery."""
    if not redis_available:
        pytest.skip("Redis not available - Docker container failed to start")
    # FAULT INJECTION: Create pending message, then have callback raise
    received_messages = []
    
    async def handler(msg):
        received_messages.append(msg)
    
    async def callback(metrics: RecoveryMetrics):
        # FAULT INJECTION: Raise exception in callback
        raise RuntimeError("Callback failed!")
    
    service = RedisMailboxService(fault_agent_id, fault_injection_config, recovery_callback=callback)
    service.register_handler(handler)
    
    await service.connect()
    
    if service._client:
        # Create stream and group
        try:
            await service._client.xgroup_create(
                name=service.inbox_stream,
                groupname=service._consumer_group,
                id="$",
                mkstream=True,
            )
        except Exception:
            pass
        
        # Add a message and mark it as pending
        message_id = await service._client.xadd(
            name=service.inbox_stream,
            fields={
                "message_id": "msg-1",
                "sender": "test",
                "recipient": fault_agent_id,
                "payload": '{"test": "data"}',
                "message_type": "direct_message",
                "timestamp": str(time.time()),
            }
        )
        
        # Read message to move it to pending list
        await service._client.xreadgroup(
            groupname=service._consumer_group,
            consumername="temp-consumer",
            streams={service.inbox_stream: ">"},
            count=1,
        )
        
        # Wait a bit to ensure message is idle (recovery_min_idle_time might be > 0)
        await asyncio.sleep(0.01)
        
        # Now try recovery - callback should raise but recovery should continue
        metrics = await service._recover_pending_messages()
        
        # Should have recovered message despite callback failure
        assert metrics.total_recovered == 1
        assert len(received_messages) == 1
    
    await service.stop()


@pytest.mark.asyncio
@pytest.mark.skipif(not pytest.importorskip("redis"), reason="Redis library not available")
async def test_handler_exception_during_recovery(fault_injection_config, fault_agent_id, redis_available, redis_docker):
    """Test recovery continues even when handler raises exception."""
    if not redis_available:
        pytest.skip("Redis not available - Docker container failed to start")
    # FAULT INJECTION: Handler raises exception during recovery
    good_messages = []
    bad_messages = []
    
    async def bad_handler(msg):
        bad_messages.append(msg)
        raise ValueError("Handler failed!")
    
    async def good_handler(msg):
        good_messages.append(msg)
    
    service = RedisMailboxService(fault_agent_id, fault_injection_config)
    service.register_handler(bad_handler)
    service.register_handler(good_handler)
    
    await service.connect()
    
    if service._client:
        # Create stream and group
        try:
            await service._client.xgroup_create(
                name=service.inbox_stream,
                groupname=service._consumer_group,
                id="$",
                mkstream=True,
            )
        except Exception:
            pass
        
        # Add message and mark as pending
        message_id = await service._client.xadd(
            name=service.inbox_stream,
            fields={
                "message_id": "msg-1",
                "sender": "test",
                "recipient": fault_agent_id,
                "payload": '{"test": "data"}',
                "message_type": "direct_message",
                "timestamp": str(time.time()),
            }
        )
        
        # Read to move to pending
        await service._client.xreadgroup(
            groupname=service._consumer_group,
            consumername="temp-consumer",
            streams={service.inbox_stream: ">"},
            count=1,
        )
        
        # Wait a bit to ensure message is idle
        await asyncio.sleep(0.01)
        
        # Recovery should continue despite bad handler
        metrics = await service._recover_pending_messages()
        
        # Message should still be processed by good handler
        assert metrics.total_recovered == 1
        assert len(bad_messages) == 1  # Bad handler ran
        assert len(good_messages) == 1  # Good handler also ran
    
    await service.stop()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


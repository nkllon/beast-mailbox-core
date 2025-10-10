"""Pytest configuration and fixtures."""

import pytest


@pytest.fixture
def redis_config():
    """Return a test Redis configuration."""
    from beast_mailbox_core.redis_mailbox import MailboxConfig
    return MailboxConfig(
        host="localhost",
        port=6379,
        db=15,  # Use separate DB for testing
        password=None,
        stream_prefix="test:mailbox",
        max_stream_length=100,
        poll_interval=0.1,
    )


@pytest.fixture
def agent_id():
    """Return a test agent ID."""
    return "test-agent"


@pytest.fixture
def sample_payload():
    """Return a sample message payload."""
    return {"text": "test message", "priority": "high", "data": [1, 2, 3]}


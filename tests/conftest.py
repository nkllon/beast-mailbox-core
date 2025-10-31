"""Pytest configuration and fixtures."""

import atexit
import subprocess
import time
import pytest


def _stop_docker_container(container_name):
    """Stop and remove a Docker container."""
    try:
        subprocess.run(
            ["docker", "stop", container_name],
            capture_output=True,
            check=False,
        )
        subprocess.run(
            ["docker", "rm", container_name],
            capture_output=True,
            check=False,
        )
    except Exception:
        pass  # Container might not exist


@pytest.fixture(scope="session")
def redis_docker():
    """Start Redis in Docker for testing.
    
    Automatically starts Redis container and stops it after tests.
    If Docker is not available or container already exists, uses existing container.
    """
    container_name = "beast-mailbox-test-redis"
    
    # Check if container already exists and is running
    result = subprocess.run(
        ["docker", "ps", "--filter", f"name={container_name}", "--format", "{{.Names}}"],
        capture_output=True,
        text=True,
    )
    
    if container_name in result.stdout:
        # Container already running - use it
        yield "localhost", 6379
        return
    
    # Try to start existing stopped container
    result = subprocess.run(
        ["docker", "start", container_name],
        capture_output=True,
    )
    
    if result.returncode == 0:
        # Started existing container
        time.sleep(1)  # Wait for Redis to be ready
        yield "localhost", 6379
        _stop_docker_container(container_name)
        return
    
    # Create and start new container
    try:
        subprocess.run(
            [
                "docker", "run", "-d",
                "--name", container_name,
                "-p", "6379:6379",
                "redis:latest",
            ],
            capture_output=True,
            check=True,
        )
        
        # Wait for Redis to be ready
        time.sleep(2)
        
        # Register cleanup
        atexit.register(_stop_docker_container, container_name)
        
        yield "localhost", 6379
        
        # Cleanup
        _stop_docker_container(container_name)
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Docker not available or failed to start
        pytest.skip("Docker not available or Redis container failed to start")


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


@pytest.fixture(scope="session")
def redis_available(redis_docker):
    """Check if Redis is available for testing.
    
    Uses the redis_docker fixture to ensure Redis is running.
    Returns True if Redis is available, False otherwise.
    """
    try:
        import redis
        client = redis.Redis(host=redis_docker[0], port=redis_docker[1], db=15)
        client.ping()
        client.close()
        return True
    except Exception:
        return False


@pytest.fixture
def sample_payload():
    """Return a sample message payload."""
    return {"text": "test message", "priority": "high", "data": [1, 2, 3]}


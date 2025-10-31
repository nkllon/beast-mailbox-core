# API Reference - beast-mailbox-core

**Version**: 0.4.0  
**Last Updated**: 2025-01-27

This document provides comprehensive API reference for `beast-mailbox-core`, a Redis-backed mailbox utility for inter-agent messaging in the Beast Mode ecosystem.

---

## Table of Contents

1. [RedisMailboxService](#redismailboxservice)
2. [MailboxMessage](#mailboxmessage)
3. [MailboxConfig](#mailboxconfig)
4. [RecoveryMetrics](#recoverymetrics)
5. [Integration Patterns](#integration-patterns)
6. [Error Handling](#error-handling)
7. [Agent Registration & Discovery](#agent-registration--discovery)

---

## RedisMailboxService

The main service class for managing mailbox operations. Provides async methods for connecting, sending/receiving messages, and managing message handlers.

### Initialization

```python
RedisMailboxService(
    agent_id: str,
    config: Optional[MailboxConfig] = None,
    recovery_callback: Optional[Callable[[RecoveryMetrics], Awaitable[None]]] = None
)
```

**Parameters:**

- `agent_id` (str, required): Unique identifier for this agent instance. Used to generate:
  - Inbox stream: `{stream_prefix}:{agent_id}:in`
  - Consumer group: `{agent_id}:group`
  - Consumer name: `{agent_id}:{uuid}` (unique per instance)

- `config` (MailboxConfig, optional): Configuration object. Defaults to `MailboxConfig()` with:
  - `host="localhost"`
  - `port=6379`
  - `db=0`
  - `password=None`
  - `stream_prefix="beast:mailbox"`
  - See [MailboxConfig](#mailboxconfig) for all options.

- `recovery_callback` (Callable, optional): Async callback invoked after pending message recovery completes. Receives a `RecoveryMetrics` object with recovery statistics.

**Example:**

```python
from beast_mailbox_core import RedisMailboxService, MailboxConfig

# Basic initialization
service = RedisMailboxService("my-agent")

# With custom configuration
config = MailboxConfig(
    host="redis.example.com",
    port=6379,
    password="secret",
    db=1
)
service = RedisMailboxService("my-agent", config)

# With recovery metrics callback
async def on_recovery(metrics: RecoveryMetrics):
    print(f"Recovered {metrics.total_recovered} messages in {metrics.batches_processed} batches")

service = RedisMailboxService(
    "my-agent",
    config,
    recovery_callback=on_recovery
)
```

---

### Public Methods

#### `connect() -> None`

Establishes connection to Redis server and verifies connectivity.

**Behavior:**
- Creates Redis client if one doesn't exist
- Pings server to verify connection works
- Idempotent - safe to call multiple times

**Raises:**
- `redis.exceptions.ConnectionError`: If Redis server is unreachable
- `redis.exceptions.AuthenticationError`: If password is incorrect

**Example:**

```python
await service.connect()
```

**Note:** `connect()` is automatically called by `send_message()` and `start()` if not already connected.

---

#### `start() -> bool`

Start the mailbox service and begin consuming messages.

**Behavior:**
1. Connects to Redis (if not already connected)
2. Creates consumer group (if it doesn't exist, handles BUSYGROUP gracefully)
3. Recovers pending messages (if enabled and handlers are registered)
4. Launches background message consumption loop

**Returns:**
- `bool`: `True` if service started successfully

**Raises:**
- `Exception`: If consumer group creation fails (except BUSYGROUP, which is handled)

**Example:**

```python
# Register handlers before starting
async def handle_message(msg: MailboxMessage):
    print(f"Received: {msg.payload}")

service.register_handler(handle_message)
result = await service.start()  # Returns True
assert result is True
```

**Important Notes:**
- The service runs in a background `asyncio.Task`
- Messages are dispatched to registered handlers as they arrive
- Pending message recovery runs **synchronously** before the consume loop starts
- Service continues running until `stop()` is called

---

#### `stop() -> None`

Gracefully stop the mailbox service and cleanup resources.

**Behavior:**
1. Sets `_running` flag to `False` (stops consume loop)
2. Cancels and waits for the processing task to complete
3. Closes the Redis client connection using `aclose()`

**Notes:**
- Idempotent - safe to call multiple times
- Exceptions during shutdown are suppressed to ensure cleanup completes
- `CancelledError` is intentionally suppressed (this IS the cleanup handler)

**Example:**

```python
await service.stop()
```

**Best Practice:** Always call `stop()` during cleanup (e.g., in `finally` blocks, signal handlers, or context managers).

---

#### `register_handler(handler: Callable[[MailboxMessage], Awaitable[None]]) -> None`

Register an async handler function for incoming messages.

**Parameters:**
- `handler`: Async function that takes a `MailboxMessage` and returns `None`

**Behavior:**
- Multiple handlers can be registered
- Handlers are called **sequentially** for each message
- Handler errors are caught, logged, and don't stop other handlers from running
- Handlers must be registered **before** calling `start()` to process messages

**Example:**

```python
async def log_message(msg: MailboxMessage):
    print(f"Message from {msg.sender}: {msg.payload}")

async def process_message(msg: MailboxMessage):
    # Do something with the message
    pass

service.register_handler(log_message)
service.register_handler(process_message)
```

**Important:**
- Handlers must not modify the handler list during iteration
- Each handler receives the same `MailboxMessage` instance
- Handler exceptions are logged but don't affect message acknowledgment

---

#### `send_message(recipient: str, payload: Dict[str, Any], message_type: str = "direct_message", message_id: Optional[str] = None) -> str`

Send a message to another agent's inbox stream.

**Parameters:**
- `recipient` (str, required): Agent ID of the message recipient
- `payload` (Dict[str, Any], required): JSON-serializable data (dict, list, or primitives)
- `message_type` (str, optional): Classification of the message. Default: `"direct_message"`
- `message_id` (str, optional): Custom message ID. If `None`, auto-generated using `uuid4()`

**Returns:**
- `str`: Message ID of the sent message (useful for tracking/correlation)

**Raises:**
- `redis.exceptions.ConnectionError`: If Redis connection fails

**Example:**

```python
# Simple message
msg_id = await service.send_message(
    recipient="bob",
    payload={"text": "Hello, Bob!"}
)

# Structured message with custom type
msg_id = await service.send_message(
    recipient="bob",
    payload={"action": "deploy", "version": "1.2.3"},
    message_type="command"
)

# With custom message ID
msg_id = await service.send_message(
    recipient="bob",
    payload={"task": "sync"},
    message_id="task-12345"
)
```

**Notes:**
- Messages are added to recipient's inbox stream: `{stream_prefix}:{recipient}:in`
- Stream automatically trims old messages using `MAXLEN` (configured via `MailboxConfig.max_stream_length`)
- `send_message()` automatically calls `connect()` if not already connected
- Does not require `start()` to be called - can send messages before starting consumption

---

### Public Properties

#### `inbox_stream: str` (read-only)

Get the Redis stream name for this agent's inbox.

**Format:** `{stream_prefix}:{agent_id}:in`

**Example:**

```python
service = RedisMailboxService("alice", MailboxConfig(stream_prefix="beast:mailbox"))
assert service.inbox_stream == "beast:mailbox:alice:in"
```

---

#### `agent_id: str` (read-only)

The agent identifier for this service instance.

---

#### `config: MailboxConfig` (read-only)

The configuration object used by this service.

---

## MailboxMessage

Structured message dataclass exchanged between agents.

### Fields

```python
@dataclass
class MailboxMessage:
    message_id: str          # Unique message identifier
    sender: str              # Agent ID of the sender
    recipient: str           # Agent ID of the recipient
    payload: Dict[str, Any]  # JSON-serializable message data
    message_type: str = "direct_message"  # Message classification
    timestamp: float         # Unix timestamp (auto-generated)
```

**Field Descriptions:**

- `message_id` (str): Unique identifier for this message. Auto-generated if not provided.
- `sender` (str): Agent ID of the sending agent (automatically set by `send_message()`)
- `recipient` (str): Agent ID of the receiving agent
- `payload` (Dict[str, Any]): Message content - must be JSON-serializable
- `message_type` (str): Message classification (e.g., "direct_message", "command", "event", "request", "response")
- `timestamp` (float): Unix timestamp when message was created (auto-generated using `asyncio.get_event_loop().time()`)

**Example:**

```python
from beast_mailbox_core import MailboxMessage

message = MailboxMessage(
    message_id="msg-123",
    sender="alice",
    recipient="bob",
    payload={"text": "Hello", "priority": "high"},
    message_type="direct_message"
)
```

---

### Serialization Methods

#### `to_redis_fields() -> Dict[str, str]`

Serialize message to Redis stream fields format.

**Returns:**
- `Dict[str, str]`: Dictionary suitable for Redis `XADD` command

**Internal Format:**
```python
{
    "message_id": "msg-123",
    "sender": "alice",
    "recipient": "bob",
    "payload": '{"text": "Hello", "priority": "high"}',  # JSON string
    "message_type": "direct_message",
    "timestamp": "1234567890.123"
}
```

**Note:** Used internally by `send_message()`. Typically not called directly by users.

---

#### `from_redis_fields(fields: Dict[bytes, bytes]) -> MailboxMessage`

Deserialize message from Redis stream fields.

**Parameters:**
- `fields` (Dict[bytes, bytes]): Raw Redis stream fields

**Returns:**
- `MailboxMessage`: Deserialized message object

**Class Method:** Must be called on the class, not an instance.

**Example:**

```python
# Internal usage - typically not called directly
redis_fields = {
    b"message_id": b"msg-123",
    b"sender": b"alice",
    b"payload": b'{"text": "Hello"}',
    # ... other fields
}
message = MailboxMessage.from_redis_fields(redis_fields)
```

**Note:** Used internally by the consume loop. Automatically handles decoding and JSON parsing.

---

## MailboxConfig

Configuration dataclass for Redis connection and mailbox behavior.

**Key Use Cases:**
- ✅ Redis authentication (password-protected clusters)
- ✅ Custom host/port/database configuration
- ✅ Advanced mailbox settings (stream prefix, polling, recovery)
- ✅ **Required for `beast-agent` authenticated connections** - Pass `MailboxConfig` object to `BaseAgent(mailbox_url=config)`  
  **Note:** For complete `BaseAgent` API documentation, see the [beast-agent repository](https://github.com/nkllon/beast-agent).

### Fields

```python
@dataclass
class MailboxConfig:
    host: str = "localhost"              # Redis server hostname
    port: int = 6379                     # Redis server port
    db: int = 0                          # Redis database number
    password: Optional[str] = None        # Redis password
    stream_prefix: str = "beast:mailbox" # Prefix for stream names
    max_stream_length: int = 1000        # MAXLEN for stream trimming
    poll_interval: float = 2.0          # Seconds between XREADGROUP polls
    enable_recovery: bool = True         # Enable pending message recovery
    recovery_min_idle_time: int = 0      # Min idle seconds before claiming
    recovery_batch_size: int = 50        # Messages per recovery batch
```

### Field Descriptions

#### Connection Settings

- **`host`** (str, default: `"localhost"`): Redis server hostname or IP address.
  
  **Environment Variable Support:** Can be set via `REDIS_URL` environment variable.
  
  **Example:** `"192.168.1.100"`, `"redis.example.com"`

- **`port`** (int, default: `6379`): Redis server port.
  
  **Environment Variable Support:** Can be set via `REDIS_URL` environment variable.

- **`db`** (int, default: `0`): Redis database number (0-15 typically).
  
  **Environment Variable Support:** Can be set via `REDIS_URL` environment variable (e.g., `redis://host:port/1` for db 1).

- **`password`** (Optional[str], default: `None`): Redis authentication password.
  
  **⚠️ CRITICAL for Production:** Most production Redis clusters require authentication. Always set this for production deployments.
  
  **Usage with beast-agent:**
  ```python
  from beast_mailbox_core.redis_mailbox import MailboxConfig
  
  # For authenticated Redis
  config = MailboxConfig(
      host="production-redis.example.com",
      port=6379,
      password="your-secret-password",  # Set password here
      db=0
  )
  
  # Pass to beast-agent BaseAgent
  agent = BaseAgent(
      agent_id="my-agent",
      capabilities=["my-cap"],
      mailbox_url=config  # Pass MailboxConfig, not a URL string!
  )
  ```
  
  **Environment Variable Support:** Can be set via `REDIS_URL` environment variable (e.g., `redis://:password@host:port/db`). However, for authenticated connections, using `MailboxConfig` directly is recommended as it's more explicit and avoids URL parsing issues.

#### Stream Settings

- **`stream_prefix`** (str, default: `"beast:mailbox"`): Prefix for all stream names.
  
  - Inbox streams: `{stream_prefix}:{agent_id}:in`
  - Example: `"beast:mailbox:alice:in"` for agent "alice" with default prefix
  
  **Recommendation:** Use namespace prefixes (e.g., `"prod:mailbox"`, `"dev:mailbox"`) for multi-environment deployments.

- **`max_stream_length`** (int, default: `1000`): Maximum number of messages per stream.
  
  - When exceeded, oldest messages are trimmed automatically
  - Uses Redis `MAXLEN` with approximate trimming for performance
  - Set to `0` to disable trimming (not recommended for production)

- **`poll_interval`** (float, default: `2.0`): Seconds between `XREADGROUP` polls.
  
  - Lower values = faster message delivery but higher CPU usage
  - Higher values = lower CPU usage but slower message delivery
  - Minimum: `0.0` (non-blocking), Recommended: `1.0-5.0`

#### Recovery Settings

- **`enable_recovery`** (bool, default: `True`): Enable automatic pending message recovery on startup.
  
  - If `True`, pending messages are automatically claimed and processed using `XAUTOCLAIM`
  - If `False`, pending messages are ignored on startup
  - **Recommendation:** Keep enabled for at-least-once delivery semantics

- **`recovery_min_idle_time`** (int, default: `0`): Minimum idle time (seconds) before a pending message is claimed.
  
  - Messages idle for less than this time are skipped
  - Useful for avoiding recovery of very recent messages that may still be processing
  - Set to `0` to recover all pending messages immediately

- **`recovery_batch_size`** (int, default: `50`): Number of messages to process per recovery batch.
  
  - Larger batches = faster recovery but higher memory usage
  - Smaller batches = lower memory usage but slower recovery
  - **Recommendation:** `50-100` for most use cases

### Environment Variable Support

`MailboxConfig` can be initialized from the `REDIS_URL` environment variable:

**Format:** `redis://:password@host:port/db` or `redis://user:password@host:port/db`

**Priority Order:**
1. CLI flags (highest priority - explicit override)
2. `REDIS_URL` environment variable (convenient default)
3. Hardcoded defaults (`localhost:6379`)

**Example:**

```python
import os
from beast_mailbox_core import MailboxConfig

# Set environment variable
os.environ["REDIS_URL"] = "redis://:secret@redis.example.com:6379/1"

# Config automatically reads from environment (via CLI parsing)
# Or manually parse if needed:
from beast_mailbox_core.cli import parse_redis_url
env_config = parse_redis_url()
config = MailboxConfig(**env_config)
```

**CLI Integration:** When using CLI tools (`beast-mailbox-service`, `beast-mailbox-send`), `REDIS_URL` is automatically parsed. CLI flags override environment variables.

### Example Configurations

```python
from beast_mailbox_core import MailboxConfig

# Minimal configuration (uses all defaults)
config = MailboxConfig()

# Production configuration
config = MailboxConfig(
    host="redis.production.com",
    port=6379,
    password="super-secret",
    db=0,
    stream_prefix="prod:mailbox",
    max_stream_length=10000,
    poll_interval=1.0,
    enable_recovery=True,
    recovery_min_idle_time=60,  # Only recover messages idle > 1 minute
    recovery_batch_size=100
)

# Development configuration (local, faster polling)
config = MailboxConfig(
    host="localhost",
    port=6379,
    stream_prefix="dev:mailbox",
    poll_interval=0.5,  # Faster polling for development
    max_stream_length=100  # Smaller streams for dev
)

# Disable recovery (custom recovery logic)
config = MailboxConfig(
    enable_recovery=False
)
```

---

## RecoveryMetrics

Metrics collected during pending message recovery.

### Fields

```python
@dataclass
class RecoveryMetrics:
    total_recovered: int = 0              # Total messages recovered
    batches_processed: int = 0             # Number of batches processed
    start_time: Optional[float] = None     # Recovery start timestamp
    end_time: Optional[float] = None       # Recovery end timestamp
```

### Usage

```python
from beast_mailbox_core import RecoveryMetrics

async def on_recovery(metrics: RecoveryMetrics):
    elapsed = metrics.end_time - metrics.start_time if metrics.end_time else 0
    print(f"Recovered {metrics.total_recovered} messages in {metrics.batches_processed} batches")
    print(f"Recovery took {elapsed:.2f} seconds")
    
    # Integrate with Prometheus/StatsD
    # prometheus_gauge.labels("recovery").set(metrics.total_recovered)
    # statsd.gauge("mailbox.recovery.messages", metrics.total_recovered)

service = RedisMailboxService("my-agent", config, recovery_callback=on_recovery)
```

**Note:** The callback is invoked after recovery completes (synchronously during `start()`). If recovery is disabled or no handlers are registered, the callback is still invoked with zero metrics.

---

## Integration Patterns

### Basic Integration Pattern

```python
import asyncio
from beast_mailbox_core import RedisMailboxService, MailboxConfig, MailboxMessage

async def main():
    # 1. Create configuration
    config = MailboxConfig(
        host="localhost",
        port=6379,
        password=None,
        stream_prefix="beast:mailbox"
    )
    
    # 2. Initialize service
    service = RedisMailboxService("my-agent", config)
    
    # 3. Register message handlers
    async def handle_message(msg: MailboxMessage):
        print(f"Received from {msg.sender}: {msg.payload}")
        # Process message...
    
    service.register_handler(handle_message)
    
    # 4. Start service (connects, recovers, starts consume loop)
    await service.start()
    
    try:
        # 5. Send messages (can happen anytime after start)
        msg_id = await service.send_message(
            recipient="other-agent",
            payload={"text": "Hello!"}
        )
        print(f"Sent message: {msg_id}")
        
        # 6. Keep service running
        await asyncio.Event().wait()  # Run forever
        
    finally:
        # 7. Graceful shutdown
        await service.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

---

### Integration with BaseAgent Class

```python
from beast_mailbox_core import RedisMailboxService, MailboxConfig, MailboxMessage

class BaseAgent:
    def __init__(self, agent_id: str, config: MailboxConfig):
        self.agent_id = agent_id
        self.mailbox = RedisMailboxService(agent_id, config)
        self.mailbox.register_handler(self._handle_mailbox_message)
    
    async def _handle_mailbox_message(self, msg: MailboxMessage):
        """Route mailbox messages to agent's message handler."""
        await self.on_message(msg.sender, msg.payload, msg.message_type)
    
    async def on_message(self, sender: str, payload: dict, message_type: str):
        """Override this method to handle incoming messages."""
        pass
    
    async def start(self):
        """Start the agent and mailbox service."""
        await self.mailbox.start()
    
    async def stop(self):
        """Stop the agent and mailbox service."""
        await self.mailbox.stop()
    
    async def send(self, recipient: str, payload: dict, message_type: str = "direct_message"):
        """Send message to another agent."""
        return await self.mailbox.send_message(recipient, payload, message_type)
```

---

### Context Manager Pattern

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def mailbox_service(agent_id: str, config: MailboxConfig):
    """Context manager for mailbox service lifecycle."""
    service = RedisMailboxService(agent_id, config)
    try:
        await service.start()
        yield service
    finally:
        await service.stop()

# Usage
async def main():
    config = MailboxConfig(host="localhost")
    
    async with mailbox_service("my-agent", config) as service:
        service.register_handler(handle_message)
        # Service is running...
        await service.send_message("other-agent", {"text": "Hello"})
        await asyncio.sleep(60)  # Run for 60 seconds
    # Service automatically stopped
```

---

### Error Handling Pattern

```python
from beast_mailbox_core import RedisMailboxService, MailboxConfig
import redis.exceptions

async def robust_agent():
    config = MailboxConfig(host="redis.example.com", password="secret")
    service = RedisMailboxService("robust-agent", config)
    
    # Register handler with error handling
    async def safe_handler(msg: MailboxMessage):
        try:
            # Process message
            process_message(msg)
        except Exception as e:
            print(f"Error processing message {msg.message_id}: {e}")
            # Message is still acknowledged - implement retry logic if needed
    
    service.register_handler(safe_handler)
    
    try:
        await service.start()
    except redis.exceptions.ConnectionError:
        print("Failed to connect to Redis")
        return
    except Exception as e:
        print(f"Failed to start service: {e}")
        return
    
    try:
        # Main loop
        while True:
            try:
                await send_heartbeat(service)
                await asyncio.sleep(10)
            except redis.exceptions.ConnectionError:
                print("Redis connection lost - reconnecting...")
                await asyncio.sleep(5)
                # Service will reconnect automatically on next send_message()
    
    finally:
        await service.stop()
```

---

### Reconnection Behavior

The `RedisMailboxService` handles reconnection automatically:

- **Connection failures during `send_message()`**: 
  - Calls `connect()` automatically, which creates a new client
  - Reconnection happens transparently
  
- **Connection failures during consume loop**:
  - Errors are logged and the loop continues after `poll_interval` delay
  - The loop automatically retries on next iteration
  - No manual reconnection needed

**Best Practice:** Implement application-level health checks and monitoring rather than relying solely on automatic reconnection.

---

## Error Handling

### Exception Types

#### `redis.exceptions.ConnectionError`

Raised when Redis server is unreachable.

**When it occurs:**
- During `connect()` if server is down
- During `send_message()` if connection is lost
- During `start()` if connection fails

**Handling:**
```python
try:
    await service.connect()
except redis.exceptions.ConnectionError as e:
    print(f"Redis connection failed: {e}")
    # Retry logic, fallback behavior, etc.
```

#### `redis.exceptions.AuthenticationError`

Raised when Redis password is incorrect.

**When it occurs:**
- During `connect()` ping verification

**Handling:**
```python
try:
    await service.start()
except redis.exceptions.AuthenticationError:
    print("Redis authentication failed - check password")
```

#### `asyncio.CancelledError`

Raised when the service is stopped during operation.

**When it occurs:**
- During `stop()` when cancelling the consume loop task
- **Note:** Intentionally suppressed in `stop()` method

**Handling:**
```python
try:
    await service.stop()
except asyncio.CancelledError:
    # Already handled internally, safe to ignore
    pass
```

#### Generic `Exception`

Raised for various operational errors (consumer group creation failures, etc.).

**When it occurs:**
- Consumer group creation failures (non-BUSYGROUP errors)
- Invalid configuration
- Other unexpected errors

**Handling:**
```python
try:
    await service.start()
except Exception as e:
    if "BUSYGROUP" in str(e):
        # Normal - group already exists
        pass
    else:
        print(f"Unexpected error: {e}")
```

---

## Agent Registration & Discovery

### Current State

**Important:** `beast-mailbox-core` does **not** provide built-in agent registration or discovery mechanisms. It is a messaging transport layer only.

### Agent "Registration" via Messaging

Agents are implicitly "registered" when they:

1. **Start consuming messages** (`start()` method)
   - Creates consumer group: `{agent_id}:group`
   - Creates inbox stream: `{stream_prefix}:{agent_id}:in`
   - Becomes available to receive messages

2. **Send messages to other agents**
   - Recipient agent must be running and have handlers registered
   - Messages wait in the recipient's inbox stream until consumed

### Discovery Patterns

Since discovery is not built-in, implement one of these patterns:

#### Pattern 1: Static Configuration

```python
# Known agents list
KNOWN_AGENTS = ["agent-1", "agent-2", "agent-3"]

async def send_to_all_agents(service: RedisMailboxService, payload: dict):
    for agent_id in KNOWN_AGENTS:
        await service.send_message(agent_id, payload)
```

#### Pattern 2: Heartbeat-Based Discovery

```python
async def heartbeat_loop(service: RedisMailboxService):
    """Send periodic heartbeats and track responses."""
    while True:
        await service.send_message("discovery-agent", {
            "type": "heartbeat",
            "agent_id": service.agent_id,
            "capabilities": ["task-runner", "file-watcher"]
        })
        await asyncio.sleep(30)

async def handle_heartbeat(msg: MailboxMessage):
    """Store discovered agents from heartbeat messages."""
    if msg.message_type == "heartbeat":
        agent_id = msg.payload["agent_id"]
        capabilities = msg.payload["capabilities"]
        # Store in discovery registry
        DISCOVERED_AGENTS[agent_id] = capabilities
```

#### Pattern 3: Registry Service

```python
# Dedicated registry agent
class RegistryAgent:
    async def register(self, service: RedisMailboxService, agent_id: str, capabilities: list):
        """Register agent capabilities."""
        await service.send_message("registry", {
            "action": "register",
            "agent_id": agent_id,
            "capabilities": capabilities
        })
    
    async def query(self, service: RedisMailboxService, capability: str) -> list:
        """Query for agents with a specific capability."""
        await service.send_message("registry", {
            "action": "query",
            "capability": capability
        })
        # Wait for response...
```

#### Pattern 4: Redis-Based Registry

Use Redis directly (outside of mailbox-core) for agent registry:

```python
import redis.asyncio as redis

async def register_agent(redis_client, agent_id: str, capabilities: list):
    """Register agent in Redis registry."""
    key = f"beast:registry:agents:{agent_id}"
    await redis_client.hset(key, mapping={
        "agent_id": agent_id,
        "capabilities": json.dumps(capabilities),
        "last_seen": time.time()
    })
    await redis_client.sadd("beast:registry:agent_list", agent_id)

async def discover_agents(redis_client, capability: str) -> list:
    """Discover agents with specific capability."""
    agents = []
    for agent_id_bytes in await redis_client.smembers("beast:registry:agent_list"):
        agent_id = agent_id_bytes.decode()
        key = f"beast:registry:agents:{agent_id}"
        capabilities_json = await redis_client.hget(key, "capabilities")
        if capabilities_json:
            capabilities = json.loads(capabilities_json)
            if capability in capabilities:
                agents.append(agent_id)
    return agents
```

### Health Monitoring

Health monitoring is not built into `beast-mailbox-core`. Implement at the application level:

```python
async def health_check(service: RedisMailboxService) -> bool:
    """Check if mailbox service is healthy."""
    try:
        await service.connect()
        return True
    except Exception:
        return False

async def monitor_health(service: RedisMailboxService):
    """Periodic health monitoring."""
    while True:
        if await health_check(service):
            # Update health status
            pass
        await asyncio.sleep(10)
```

---

## Complete Integration Example

```python
"""
Complete example: Agent with mailbox integration, discovery, and error handling.
"""
import asyncio
import logging
from beast_mailbox_core import (
    RedisMailboxService,
    MailboxConfig,
    MailboxMessage,
    RecoveryMetrics
)

logging.basicConfig(level=logging.INFO)

class MyAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        config = MailboxConfig(
            host="localhost",
            port=6379,
            stream_prefix="beast:mailbox"
        )
        
        # Initialize mailbox with recovery callback
        self.mailbox = RedisMailboxService(
            agent_id,
            config,
            recovery_callback=self._on_recovery
        )
        
        # Register message handler
        self.mailbox.register_handler(self._handle_message)
    
    async def _on_recovery(self, metrics: RecoveryMetrics):
        """Handle recovery metrics."""
        logging.info(
            f"Recovery complete: {metrics.total_recovered} messages "
            f"in {metrics.batches_processed} batches"
        )
    
    async def _handle_message(self, msg: MailboxMessage):
        """Handle incoming mailbox messages."""
        logging.info(f"Received {msg.message_type} from {msg.sender}: {msg.payload}")
        
        # Route by message type
        if msg.message_type == "ping":
            await self._handle_ping(msg)
        elif msg.message_type == "command":
            await self._handle_command(msg)
        else:
            await self._handle_direct_message(msg)
    
    async def _handle_ping(self, msg: MailboxMessage):
        """Respond to ping messages."""
        await self.mailbox.send_message(
            recipient=msg.sender,
            payload={"response": "pong", "original_id": msg.message_id},
            message_type="pong"
        )
    
    async def _handle_command(self, msg: MailboxMessage):
        """Handle command messages."""
        command = msg.payload.get("command")
        if command == "status":
            await self.mailbox.send_message(
                recipient=msg.sender,
                payload={"status": "running", "agent_id": self.agent_id},
                message_type="response"
            )
    
    async def _handle_direct_message(self, msg: MailboxMessage):
        """Handle direct messages."""
        print(f"Direct message: {msg.payload}")
    
    async def start(self):
        """Start the agent."""
        logging.info(f"Starting agent {self.agent_id}...")
        await self.mailbox.start()
        logging.info("Agent started and consuming messages")
    
    async def stop(self):
        """Stop the agent."""
        logging.info(f"Stopping agent {self.agent_id}...")
        await self.mailbox.stop()
        logging.info("Agent stopped")
    
    async def send_message(self, recipient: str, payload: dict, message_type: str = "direct_message"):
        """Send message to another agent."""
        return await self.mailbox.send_message(recipient, payload, message_type)

async def main():
    # Create and start agent
    agent = MyAgent("agent-1")
    
    try:
        await agent.start()
        
        # Send a test message
        await agent.send_message("agent-2", {"text": "Hello!"})
        
        # Keep running
        await asyncio.Event().wait()
    
    except KeyboardInterrupt:
        logging.info("Shutting down...")
    finally:
        await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Summary

### Quick Reference

**Initialization:**
```python
service = RedisMailboxService("agent-id", MailboxConfig())
```

**Register Handler:**
```python
service.register_handler(async_handler_function)
```

**Start Service:**
```python
await service.start()
```

**Send Message:**
```python
msg_id = await service.send_message("recipient", {"data": "value"})
```

**Stop Service:**
```python
await service.stop()
```

**Message Handler Signature:**
```python
async def handler(msg: MailboxMessage) -> None:
    # Process msg.payload, msg.sender, msg.message_type, etc.
    pass
```

---

## For More Information

- **User Guide**: See `docs/USAGE_GUIDE.md`
- **Quick Reference**: See `docs/QUICK_REFERENCE.md`
- **README**: See `README.md` for installation and basic usage
- **Lessons Learned**: See `docs/LESSONS_LEARNED_v0.3.0.md` for development context

---

**API Documentation Version**: 0.4.0  
**Last Updated**: 2025-01-27  
**Maintained By**: beast-mailbox-core maintainers


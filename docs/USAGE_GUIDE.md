# Beast Mailbox Core - Complete Usage Guide

**Version:** 0.2.0  
**Installation:** `pip install beast-mailbox-core`

---

## Overview

Beast Mailbox Core is a Redis-backed inter-agent messaging system that provides durable, asynchronous communication between agents using Redis Streams. It's designed for distributed systems where agents need to send and receive messages reliably.

### Key Concepts

- **Agent**: An entity with a unique ID that can send/receive messages (e.g., `devbox`, `herbert`, `poe`)
- **Mailbox**: A Redis Stream for each agent (format: `beast:mailbox:<agent_id>:in`)
- **Consumer Group**: Per-agent groups for message consumption with delivery guarantees
- **Message**: Structured data with sender, recipient, payload, and metadata

---

## Installation & Requirements

```bash
# Install from PyPI
pip install beast-mailbox-core

# Requirements
# - Python >=3.9
# - redis >=5.0.0
# - A running Redis instance
```

---

## CLI Tools

### 1. beast-mailbox-service

Start a mailbox service for an agent (either streaming or one-shot mode).

#### Streaming Mode (Default)

Continuously listens for incoming messages:

```bash
# Start long-running listener for agent "herbert"
beast-mailbox-service herbert \
  --redis-host localhost \
  --redis-password mypassword \
  --echo

# With all options
BEAST_MODE_PROMETHEUS_ENABLED=false beast-mailbox-service myagent \
  --redis-host 192.168.1.119 \
  --redis-port 6379 \
  --redis-password beastmode2025 \
  --redis-db 0 \
  --stream-prefix beast:mailbox \
  --maxlen 1000 \
  --poll-interval 2.0 \
  --echo \
  --verbose
```

**When to use:**
- Production agents that need to process messages continuously
- Background services
- Long-running workers

**Output example:**
```
2025-10-10 12:30:45 INFO beast_mailbox.herbert: Created consumer group herbert:group for stream beast:mailbox:herbert:in
📬 herbert <- devbox (direct_message): {'text': 'Hello!'}
📬 herbert <- alice (task_update): {'task': 'sync', 'priority': 'high'}
```

#### One-Shot Mode (NEW in v0.2.0)

Fetch specific messages and exit:

```bash
# View latest message (read-only)
beast-mailbox-service devbox --latest --count 1 \
  --redis-host localhost

# View 5 most recent messages
beast-mailbox-service devbox --latest --count 5 --verbose

# View and acknowledge messages (marks as read)
beast-mailbox-service devbox --latest --count 5 --ack

# View and DELETE messages (destructive!)
beast-mailbox-service devbox --latest --count 5 --ack --trim
```

**When to use:**
- Debugging message queues
- Manual message inspection
- Cleanup operations
- Testing

**Output example with --ack:**
```
📬 devbox <- alice (direct_message) [1728571234-0]: {'text': 'Hello'}
📬 devbox <- bob (direct_message) [1728571235-0]: {'text': 'World'}
✓ Acknowledged 2 message(s) in group devbox:group
```

**Output example with --trim:**
```
📬 devbox <- alice (direct_message) [1728571234-0]: {'text': 'Hello'}
🗑️  Deleted 1 message(s) from stream
```

### 2. beast-mailbox-send

Send a message from one agent to another.

```bash
# Simple text message
beast-mailbox-send alice bob --message "ping"

# Structured JSON payload
beast-mailbox-send alice bob \
  --json '{"task": "process", "data": [1,2,3]}' \
  --message-type task_request

# With full connection details
beast-mailbox-send devbox herbert \
  --message "System ready" \
  --message-type status_update \
  --redis-host 192.168.1.119 \
  --redis-password beastmode2025 \
  --redis-db 0 \
  --verbose
```

**Output example:**
```
2025-10-10 12:35:20 INFO root: Sent message from alice to bob
```

---

## Programmatic API

### Basic Usage

```python
import asyncio
from beast_mailbox_core import RedisMailboxService, MailboxMessage
from beast_mailbox_core.redis_mailbox import MailboxConfig

async def main():
    # Configure connection
    config = MailboxConfig(
        host="localhost",
        port=6379,
        password="mypassword",
        db=0,
        stream_prefix="beast:mailbox",
        max_stream_length=1000,
        poll_interval=2.0
    )
    
    # Create service for agent "alice"
    service = RedisMailboxService(agent_id="alice", config=config)
    
    # Register message handler
    async def handle_message(message: MailboxMessage):
        print(f"Received from {message.sender}: {message.payload}")
    
    service.register_handler(handle_message)
    
    # Start listening
    await service.start()
    
    # Send a message to another agent
    await service.send_message(
        recipient="bob",
        payload={"text": "Hello Bob!"},
        message_type="greeting"
    )
    
    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        await service.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Sending Messages Only

```python
import asyncio
from beast_mailbox_core import RedisMailboxService
from beast_mailbox_core.redis_mailbox import MailboxConfig

async def send_message():
    config = MailboxConfig(host="localhost")
    service = RedisMailboxService(agent_id="sender", config=config)
    
    # Send without starting consumer
    message_id = await service.send_message(
        recipient="recipient",
        payload={"alert": "High CPU usage", "value": 95},
        message_type="system_alert"
    )
    
    print(f"Sent message: {message_id}")
    await service.stop()

asyncio.run(send_message())
```

### Custom Message Handler

```python
async def priority_handler(message: MailboxMessage):
    """Handle high-priority messages differently."""
    if message.payload.get("priority") == "high":
        print(f"⚠️  HIGH PRIORITY from {message.sender}")
        # Take urgent action
    else:
        print(f"📝 Regular message from {message.sender}")

service.register_handler(priority_handler)
```

---

## Configuration Options

### MailboxConfig

```python
from beast_mailbox_core.redis_mailbox import MailboxConfig

config = MailboxConfig(
    host="localhost",         # Redis server host
    port=6379,               # Redis server port
    db=0,                    # Redis database number
    password=None,           # Redis password (optional)
    stream_prefix="beast:mailbox",  # Prefix for stream keys
    max_stream_length=1000,  # Max messages per stream (XADD MAXLEN)
    poll_interval=2.0        # Seconds between polls in streaming mode
)
```

### MailboxMessage Structure

```python
@dataclass
class MailboxMessage:
    message_id: str          # Unique message ID
    sender: str              # Sender agent ID
    recipient: str           # Recipient agent ID
    payload: Dict[str, Any]  # Message data (JSON-serializable)
    message_type: str        # Message type/category
    timestamp: float         # Unix timestamp
```

---

## Use Cases & Examples

### 1. Microservice Communication

**Service A** (sender):
```bash
beast-mailbox-send service-a service-b \
  --json '{"action": "process_order", "order_id": "12345"}' \
  --message-type order_event
```

**Service B** (receiver):
```bash
beast-mailbox-service service-b --echo --verbose
```

### 2. Task Queue System

**Worker pool**:
```bash
# Start multiple workers
beast-mailbox-service worker-1 --echo &
beast-mailbox-service worker-2 --echo &
beast-mailbox-service worker-3 --echo &
```

**Task dispatcher**:
```bash
# Send tasks to workers
for i in {1..10}; do
  beast-mailbox-send dispatcher worker-$(( (i % 3) + 1 )) \
    --json "{\"task_id\": $i, \"type\": \"compute\"}"
done
```

### 3. Debugging & Inspection

```bash
# Check what messages are waiting
beast-mailbox-service myagent --latest --count 10 --verbose

# Peek at messages without consuming
beast-mailbox-service myagent --latest --count 5

# Clean up old messages
beast-mailbox-service myagent --latest --count 100 --ack --trim
```

### 4. Event Broadcasting

```python
async def broadcast_event():
    """Send event to multiple agents."""
    service = RedisMailboxService(agent_id="broadcaster", config=config)
    
    recipients = ["agent1", "agent2", "agent3", "agent4"]
    event = {"event": "system_shutdown", "time": "2025-10-10T12:00:00Z"}
    
    for recipient in recipients:
        await service.send_message(
            recipient=recipient,
            payload=event,
            message_type="broadcast"
        )
    
    await service.stop()
```

---

## Safety & Best Practices

### ⚠️ Destructive Operations

**Read-only (Safe):**
```bash
# Just peek at messages
beast-mailbox-service myagent --latest --count 5
```

**Acknowledge (Semi-destructive):**
```bash
# Marks messages as read, prevents redelivery
beast-mailbox-service myagent --latest --count 5 --ack
```

**Trim (DESTRUCTIVE):**
```bash
# Permanently deletes messages - CANNOT BE UNDONE!
beast-mailbox-service myagent --latest --count 5 --ack --trim
```

### Best Practices

1. **Always start with read-only inspection**
   - Use `--latest` without `--ack` or `--trim` first

2. **Use `--count` to limit blast radius**
   - Don't accidentally process/delete hundreds of messages
   - Start small: `--count 1`, then `--count 5`, etc.

3. **Enable `--verbose` for production operations**
   - Creates audit trail with timestamps and message IDs
   - Helps debugging if something goes wrong

4. **Prefer `--ack` over `--trim`**
   - Acknowledgment prevents redelivery but keeps messages for debugging
   - Only use `--trim` when you're certain you want to delete

5. **Back up before bulk trimming**
   ```bash
   # Export stream before destructive operations
   redis-cli -h myhost DUMP beast:mailbox:myagent:in > backup.rdb
   ```

6. **Test in development first**
   - Use a separate Redis database for testing
   - `--redis-db 1` for dev, `--redis-db 0` for prod

7. **Monitor Redis memory**
   - Streams can grow large without proper cleanup
   - Use `--maxlen` to cap stream size
   - Regular trimming of processed messages

---

## Troubleshooting

### Messages Not Appearing

```bash
# 1. Verify Redis connection
redis-cli -h localhost -a password ping
# Expected: PONG

# 2. Check if stream exists
redis-cli -h localhost XLEN beast:mailbox:myagent:in
# Expected: number of messages

# 3. View stream contents directly
redis-cli -h localhost XREAD COUNT 5 STREAMS beast:mailbox:myagent:in 0

# 4. Verify agent IDs match
# Sender sends to "herbert"
# Receiver listens as "herbert" (not "Herbert" or "herbert-1")
```

### Consumer Group Errors

```
ERROR: BUSYGROUP Consumer Group name already exists
```
**Solution:** This is normal and handled automatically. The library creates consumer groups on first use.

```bash
# If you need to reset a consumer group
redis-cli -h localhost XGROUP DESTROY beast:mailbox:myagent:in myagent:group
redis-cli -h localhost XGROUP CREATE beast:mailbox:myagent:in myagent:group 0 MKSTREAM
```

### Connection Refused

```
ERROR: Connection refused
```
**Solutions:**
- Ensure Redis is running: `redis-server`
- Check host/port: `--redis-host localhost --redis-port 6379`
- Verify firewall rules
- Test connectivity: `telnet localhost 6379`

### Authentication Failures

```
ERROR: NOAUTH Authentication required
```
**Solution:**
- Add `--redis-password` flag
- Or configure Redis to not require auth (dev only)

---

## Redis Stream Architecture

### How It Works

1. **Each agent has an inbox stream:**
   ```
   beast:mailbox:alice:in   ← Messages for Alice
   beast:mailbox:bob:in     ← Messages for Bob
   beast:mailbox:charlie:in ← Messages for Charlie
   ```

2. **Consumer groups ensure delivery:**
   - Each agent has a consumer group: `<agent_id>:group`
   - Messages are delivered to one consumer in the group
   - Acknowledgment confirms processing
   - Unacknowledged messages can be reclaimed

3. **Message flow:**
   ```
   Sender ──XADD──> Redis Stream ──XREADGROUP──> Receiver
                   (recipient:in)               (consumer group)
   ```

### Viewing Streams Directly

```bash
# Count messages
redis-cli XLEN beast:mailbox:myagent:in

# View last 10 messages
redis-cli XREVRANGE beast:mailbox:myagent:in + - COUNT 10

# View consumer group info
redis-cli XINFO GROUPS beast:mailbox:myagent:in

# View pending messages
redis-cli XPENDING beast:mailbox:myagent:in myagent:group
```

---

## Performance Considerations

### Throughput

- Redis Streams can handle 10,000+ messages/second
- Async architecture allows high concurrency
- Poll interval affects latency (default: 2 seconds)

### Memory

- Each message ~1KB (depends on payload)
- 10,000 messages ≈ 10MB memory
- Use `--maxlen` to cap stream size
- Regular trimming prevents unbounded growth

### Latency

- Network latency: depends on Redis location
- Polling interval: configurable (default: 2.0s)
- Processing: depends on handler implementation

---

## Advanced Topics

### Multiple Handlers

```python
service = RedisMailboxService(agent_id="agent", config=config)

async def logger(msg: MailboxMessage):
    print(f"LOG: {msg.sender} -> {msg.recipient}")

async def processor(msg: MailboxMessage):
    # Process message
    result = await process(msg.payload)
    print(f"Processed: {result}")

# All handlers are called for each message
service.register_handler(logger)
service.register_handler(processor)
```

### Custom Stream Prefixes

```python
# Use different prefix for isolation
config = MailboxConfig(
    host="localhost",
    stream_prefix="myapp:mailbox"  # instead of "beast:mailbox"
)
```

### Error Handling

```python
async def safe_handler(message: MailboxMessage):
    try:
        await risky_operation(message.payload)
    except Exception as e:
        print(f"Handler error: {e}")
        # Message will still be acknowledged
        # Implement your own retry/DLQ logic if needed

service.register_handler(safe_handler)
```

---

## Integration Examples

### With FastAPI

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager

app = FastAPI()
mailbox_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mailbox_service
    # Startup
    config = MailboxConfig(host="localhost")
    mailbox_service = RedisMailboxService(agent_id="api-server", config=config)
    
    async def handle_message(msg: MailboxMessage):
        print(f"Received: {msg.payload}")
    
    mailbox_service.register_handler(handle_message)
    await mailbox_service.start()
    
    yield
    
    # Shutdown
    await mailbox_service.stop()

app = FastAPI(lifespan=lifespan)

@app.post("/send")
async def send(recipient: str, message: str):
    await mailbox_service.send_message(
        recipient=recipient,
        payload={"text": message}
    )
    return {"status": "sent"}
```

### With Asyncio Tasks

```python
async def worker():
    service = RedisMailboxService(agent_id="worker", config=config)
    
    async def process_task(msg: MailboxMessage):
        task_id = msg.payload.get("task_id")
        result = await expensive_computation(task_id)
        # Send result back
        await service.send_message(
            recipient=msg.sender,
            payload={"task_id": task_id, "result": result},
            message_type="task_result"
        )
    
    service.register_handler(process_task)
    await service.start()

# Run multiple workers
async def main():
    workers = [asyncio.create_task(worker()) for _ in range(5)]
    await asyncio.gather(*workers)
```

---

## Version History

### 0.2.0 (2025-10-10)
- ✅ Added `--ack` flag for acknowledging messages
- ✅ Added `--trim` flag for deleting messages
- ✅ Enhanced error handling for partial failures
- ✅ Clear logging with emoji indicators (✓, 🗑️)
- ✅ Consumer group auto-creation with BUSYGROUP handling
- ✅ 610% README expansion with comprehensive documentation

### 0.1.0 (Initial Release)
- ✅ Basic streaming mailbox service
- ✅ One-shot message inspection
- ✅ Message sending utility
- ✅ Redis Streams integration
- ✅ Consumer groups per agent

---

## License

MIT License - See LICENSE file

## Links

- **GitHub:** https://github.com/nkllon/beast-mailbox-core
- **PyPI:** https://pypi.org/project/beast-mailbox-core/
- **Issues:** https://github.com/nkllon/beast-mailbox-core/issues

---

**Happy messaging! 📬**



# Beast Mailbox Core - Quick Reference

## Installation
```bash
pip install beast-mailbox-core
```

## Common Commands

### Start Listening
```bash
# Continuous listening
beast-mailbox-service myagent --redis-host localhost --echo

# View latest message
beast-mailbox-service myagent --latest --count 1

# View and clean up
beast-mailbox-service myagent --latest --count 10 --ack --trim
```

### Send Message
```bash
# Text message
beast-mailbox-send alice bob --message "hello"

# JSON payload
beast-mailbox-send alice bob --json '{"key": "value"}'
```

## Python Quick Start
```python
import asyncio
from beast_mailbox_core import RedisMailboxService, MailboxMessage
from beast_mailbox_core.redis_mailbox import MailboxConfig

async def main():
    # Create service
    config = MailboxConfig(host="localhost")
    service = RedisMailboxService("myagent", config)
    
    # Register handler
    async def handler(msg: MailboxMessage):
        print(f"Got: {msg.payload}")
    service.register_handler(handler)
    
    # Start & send
    await service.start()
    await service.send_message("otheragent", {"text": "hi"})
    
    # Keep running
    await asyncio.Event().wait()

asyncio.run(main())
```

## Key Flags

| Flag | Purpose | Safety |
|------|---------|--------|
| `--latest` | One-shot mode | ✅ Safe |
| `--count N` | Limit messages | ✅ Safe |
| `--ack` | Mark as read | ⚠️ Semi-destructive |
| `--trim` | DELETE messages | 🚨 DESTRUCTIVE |
| `--verbose` | Debug logging | ✅ Safe |
| `--echo` | Show messages | ✅ Safe |

## Stream Format
```
beast:mailbox:<agent_id>:in
```

Example: `beast:mailbox:alice:in` is Alice's inbox

## Redis Commands
```bash
# Count messages
redis-cli XLEN beast:mailbox:myagent:in

# View messages
redis-cli XREVRANGE beast:mailbox:myagent:in + - COUNT 5

# Check consumer groups
redis-cli XINFO GROUPS beast:mailbox:myagent:in
```

## Safety Rules
1. ✅ Test with `--latest --count 1` first
2. ✅ Use `--verbose` in production
3. ⚠️ `--ack` prevents redelivery
4. 🚨 `--trim` is permanent - back up first!
5. ✅ Always specify `--count` with destructive ops

## Message Structure
```python
{
    "message_id": "1728571234-0",
    "sender": "alice",
    "recipient": "bob",
    "payload": {"your": "data"},
    "message_type": "direct_message",
    "timestamp": 1728571234.567
}
```

## Common Patterns

### Check for messages
```bash
beast-mailbox-service myagent --latest --count 5 --verbose
```

### Send to multiple recipients
```bash
for agent in alice bob charlie; do
  beast-mailbox-send dispatcher $agent --message "broadcast"
done
```

### Clean old messages
```bash
beast-mailbox-service myagent --latest --count 100 --ack --trim
```

## Version: 0.2.0
- ✨ NEW: `--ack` and `--trim` flags
- ✨ NEW: Enhanced one-shot mode
- ✨ NEW: Emoji logging indicators



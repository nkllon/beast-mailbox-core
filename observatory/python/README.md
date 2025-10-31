# Apple Intelligence Agent - Python Bridge

**Purpose:** Bridge Apple Intelligence (Swift) with Beast Cohort (Python/mailbox)  
**Status:** Ready to implement

---

## Quick Start

### 1. Ensure Swift Server is Running

```bash
# In another terminal
cd observatory/swift
swift run ObservatoryApp

# Server should start on http://localhost:8081
```

### 2. Start Python Agent

```bash
cd observatory/python

# Set Redis config
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
# Optional:
export REDIS_PASSWORD="your-password"
export REDIS_DB="0"

# Run agent
python apple_intelligence_agent.py
```

### 3. Query from Other Agents

```python
from beast_mailbox_core import RedisMailboxService, MailboxConfig
from beast_mailbox_core.redis_mailbox import MailboxConfig

config = MailboxConfig(host="localhost", port=6379)
mailbox = RedisMailboxService("my-agent", config=config)
await mailbox.start()

# Query Apple Intelligence
await mailbox.send_message(
    recipient="apple-intelligence",
    message_type="QUERY_APPLE_INTELLIGENCE",
    payload={
        "query": "Review this code for issues",
        "context": code,
        "query_type": "code_review"
    }
)
```

---

## Query Types

1. **general** - General queries
2. **code_review** - Code review requests
3. **error_diagnosis** - Error analysis
4. **architecture** - Architecture advice
5. **documentation** - Documentation generation

---

**Status:** Ready to test when Swift server is running


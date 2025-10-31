# Apple Intelligence Agent - Python Bridge

**Purpose:** Bridge Apple Intelligence (Swift) with Beast Cohort (Python/mailbox)  
**Status:** Ready to implement

---

## The Babel Fish 🐟

**Simple function calls, not distributed system ceremony:**

```python
from babel_fish import ask_apple_intelligence

# That's it. Just ask.
response = await ask_apple_intelligence("Review this code", context=code)
```

No mailbox setup, no message types, no boilerplate. Just ask.

---

## Quick Start

### 1. Ensure Swift Server is Running

```bash
# In another terminal
cd observatory/swift
swift run ObservatoryApp

# Server should start on http://localhost:8081
```

### 2. Start Apple Intelligence Agent

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

### 3. Use Babel Fish in Your Code

```python
import asyncio
from babel_fish import ask_apple_intelligence, review_code, diagnose_error

async def main():
    # Simple query
    response = await ask_apple_intelligence("How should I structure this?")
    print(response)
    
    # Code review
    feedback = await review_code(my_code)
    print(feedback)
    
    # Error diagnosis
    diagnosis = await diagnose_error(error_log)
    print(diagnosis)

asyncio.run(main())
```

---

## API

### `ask_apple_intelligence(query, context=None, query_type="general")`

Ask Apple Intelligence anything.

**Parameters:**
- `query` (str): Your question
- `context` (str, optional): Additional context (code, logs, etc.)
- `query_type` (str): `"general"`, `"code_review"`, `"error_diagnosis"`, `"architecture"`, or `"documentation"`

**Returns:** Apple Intelligence response as string

**Example:**
```python
response = await ask_apple_intelligence(
    "Review this code for issues",
    context=code,
    query_type="code_review"
)
```

### Convenience Functions

**`review_code(code, query="Review this code for issues and improvements")`**
```python
feedback = await review_code(my_code)
```

**`diagnose_error(error_log, query="Why did this error occur and how do I fix it?")`**
```python
diagnosis = await diagnose_error(error_log)
```

**`get_architecture_advice(query, context=None)`**
```python
advice = await get_architecture_advice("How should I structure this?")
```

---

## Query Types

1. **general** - General queries
2. **code_review** - Code review requests
3. **error_diagnosis** - Error analysis
4. **architecture** - Architecture advice
5. **documentation** - Documentation generation

---

## Examples

### Code Review

```python
code = """
async def sync_metrics():
    await fetch_from_sonarcloud()
    await push_to_prometheus()
"""

feedback = await review_code(code)
# Apple Intelligence reviews code, suggests improvements
```

### Error Diagnosis

```python
error_log = """
ERROR: Connection refused
Traceback: ...
"""

diagnosis = await diagnose_error(error_log)
# Apple Intelligence analyzes error, suggests fix
```

### Architecture Advice

```python
advice = await get_architecture_advice(
    "How should I structure a sync service for reliability?"
)
# Apple Intelligence provides architecture recommendations
```

---

## Testing

```bash
python test_babel_fish.py
```

---

## How It Works

Behind the scenes, Babel Fish:
1. Connects to Redis mailbox (auto-detects from env)
2. Sends message to `apple-intelligence` agent
3. Waits for response
4. Returns result

You don't care. You just call a function.

---

**Status:** Ready to use. Just import and ask.

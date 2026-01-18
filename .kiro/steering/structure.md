# Project Structure

## Organization Philosophy

The codebase separates transport-agnostic mailbox contracts from backend-specific implementations. Specifications and steering live under `.kiro/` so AI agents share a single source of truth for requirements and context.

## Directory Patterns

### Core Library
**Location**: `/src/beast_mailbox_core/`  
**Purpose**: Public API, backend services, configuration helpers  
**Example**: `redis_mailbox.py`, `filesystem_mailbox.py`

### Tests
**Location**: `/tests/`  
**Purpose**: Pytest suites covering unit and integration scenarios  
**Example**: `test_redis_mailbox.py`, fixtures in `conftest.py`

### Specification Assets
**Location**: `/.kiro/specs/`  
**Purpose**: Generated specs per feature; manage exclusively with `/kiro` commands  
**Example**: `firestore-mailbox-backend/requirements.md`

> **Process Guardrail**: Run the `/kiro:` slash commands for every spec phase. They function as the canonical, deterministic editor—manual edits to `.kiro/specs/` (including `spec.json`) are prohibited.

### Steering Memory
**Location**: `/.kiro/steering/`  
**Purpose**: Persistent project guidance consumed before spec work  
**Example**: `product.md`, `tech.md`, `structure.md`

### CLI Commands
**Location**: `/.cursor/commands/kiro/`  
**Purpose**: Cursor slash commands that drive the AI-DLC workflow  
**Example**: `spec-init.md`, `validate-gap.md`

## Naming Conventions

- **Python modules**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case`
- **Specs**: `feature-name-kebab-case`

## Import Organization

```python
# Application modules first
from beast_mailbox_core.redis_mailbox import RedisMailboxService

# Standard library imports grouped separately
import asyncio
```

## Code Organization Principles

- Keep backend-agnostic contracts (`MailboxMessage`) free from implementation details.
- Encapsulate backend-specific config in dedicated dataclasses to simplify factory wiring.
- Treat `.kiro` files as authoritative project knowledge; avoid drifting manual docs.

---
_Document patterns, not file trees. New files following patterns shouldn't require updates_


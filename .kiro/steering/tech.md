# Technology Stack

## Architecture

Asynchronous Python services expose mailbox semantics over interchangeable persistence backends. Agents interact through the shared `MailboxMessage` model while concrete implementations (Redis streams, filesystem JSON drops, Firestore documents) handle delivery guarantees.

## Core Technologies

- **Language**: Python 3.9–3.12
- **Framework**: AsyncIO-based service layer with dataclass models
- **Runtime**: CPython with optional Redis/Firestore services

## Key Libraries

- `redis` for Redis Streams transport
- `google-cloud-firestore` (planned) for serverless GCP deployments
- `asyncio` + `dataclasses` for core concurrency and data modeling

## Development Standards

### Type Safety
- Prefer explicit typing across public APIs; maintain dataclass schemas for payloads.

### Code Quality
- Ruff + Black enforced in CI; SonarCloud Quality Gate must pass on every change.
- Docstring density ≥ 40 %; capture design decisions inline.

### Testing
- Pytest with asyncio auto mode.
- Coverage ≥ 85 % overall; 100 % of testable code must be covered.
- Integration tests use Redis docker fixtures where required.

## Development Environment

### Required Tools
- Node/npm (via Homebrew) to manage cc-sdd slash-command tooling.
- Python virtualenv with `pip install -e ".[dev]"`.
- Access to `/Volumes/lemon/cursor/cc-sdd` for refreshing `/kiro` commands.

### Common Commands
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run test suite with coverage
pytest tests/ --cov

# Refresh /kiro commands if templates change
node /Volumes/lemon/cursor/cc-sdd/tools/cc-sdd/dist/cli.js --cursor --lang en --yes
```

## Key Technical Decisions

- **Spec-Driven Delivery**: All substantive work originates from `/kiro` specs to preserve requirements/design/tasks history.
- **Backend Abstraction**: Core selects mailbox backend via configuration flag so future implementations (Firestore) plug in without API churn.
- **Async-First**: Services favor async handlers and background tasks, requiring careful cancellation handling and targeted tests.

---
_Document standards and patterns, not every dependency_


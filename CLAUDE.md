# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ CRITICAL: Read This First

**This is a cc-sdd project using Kiro spec-driven development.**

Before making any changes:
1. **Read AGENTS.md** - Spec-driven development workflow and rules
2. **Load steering context** from `.kiro/steering/` (product.md, tech.md, structure.md)
3. **Use `/kiro:` commands** for ALL spec work - never hand-edit `.kiro/specs/`
4. **Check active specs** with `/kiro/spec-status <feature-name>`

### Kiro Workflow Commands

**Available at:** `.cursor/commands/kiro/`

```bash
# Phase 0: Project context (run when context changes)
/kiro/steering
/kiro/steering-custom

# Phase 1: Specification workflow
/kiro/spec-init "feature description"
/kiro/spec-requirements {feature-name}
/kiro/validate-gap {feature-name}      # Optional: for existing codebase
/kiro/spec-design {feature-name} [-y]
/kiro/validate-design {feature-name}   # Optional: design review
/kiro/spec-tasks {feature-name} [-y]

# Phase 2: Implementation
/kiro/spec-impl {feature-name} [tasks]
/kiro/validate-impl {feature-name}     # Optional: post-implementation

# Progress check (anytime)
/kiro/spec-status {feature-name}
```

**Rule:** ALL substantive work must originate from `/kiro` specs. These commands are the deterministic, canonical editor for `.kiro/specs/` - never hand-edit those files.

### Steering Documents (Project Memory)

**Location:** `.kiro/steering/`

These documents provide persistent project-wide context that AI agents consume before spec work:
- **product.md** - Product vision, capabilities, use cases, value proposition
- **tech.md** - Technology stack, standards, development environment, key decisions
- **structure.md** - Organization patterns, naming conventions, process guardrails

**Always load steering context** before creating or updating specifications.

## Project Overview

**Beast Mailbox Core** is a Python package providing Redis Streams and filesystem-based mailbox utilities for inter-agent messaging. Built 100% by AI agents for AI agent communication.

**Current Version:** 0.5.0
**Python Support:** 3.9, 3.10, 3.11, 3.12
**Package:** [beast-mailbox-core on PyPI](https://pypi.org/project/beast-mailbox-core/)

### Core Purpose
Durable, reliable messaging between AI agents via:
- **Redis backend** - Distributed messaging using Redis Streams (XADD/XREADGROUP)
- **Filesystem backend** - Lightweight same-host messaging via atomic JSON files

### RPG2K Platform

**"Yay Verily RPG2K"** is the canonical name for the shared observability and infrastructure stack:
- **Required services:** Redis, Prometheus, Grafana, Pushgateway
- **Purpose:** Consistent platform definition across Beast ecosystem
- **Spec:** See `.kiro/specs/rpg2k-platform-definition/` for authoritative definition

Use this terminology consistently across documentation, code, and agent communication.

## Development Commands

### Setup
```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
beast-mailbox-service --help

# Refresh /kiro commands if templates change (cc-sdd)
node /Volumes/lemon/cursor/cc-sdd/tools/cc-sdd/dist/cli.js --cursor --lang en --yes
```

### Testing
```bash
# Run all tests
pytest tests/

# Run with coverage (must meet ≥85% threshold)
pytest tests/ --cov=src/beast_mailbox_core --cov-report=term-missing

# Run specific test file
pytest tests/test_redis_mailbox.py -v

# Run specific test
pytest tests/test_cli_functions.py::TestFetchLatestMessages::test_ack_flag -v

# Generate HTML coverage report
pytest tests/ --cov --cov-report=html
open htmlcov/index.html
```

### Code Quality
```bash
# Format code with Black
black .

# Check formatting without changes
black --check .

# Lint with Ruff
ruff check .

# Auto-fix linting issues
ruff check . --fix
```

### Building & Publishing
```bash
# Build package (wheel + source dist)
python -m build

# Clean build artifacts
rm -rf dist/ build/ *.egg-info
```

### Running Services
```bash
# Start Redis mailbox listener (with REDIS_URL env var)
export REDIS_URL="redis://:password@host:6379/0"
beast-mailbox-service my-agent --verbose

# Start filesystem mailbox listener
beast-mailbox-service my-agent --backend filesystem --verbose

# Send message
beast-mailbox-send sender recipient --message "Hello" --json '{"key": "value"}'

# Inspect latest messages (read-only)
beast-mailbox-service my-agent --latest --count 5 --verbose

# Acknowledge messages (semi-destructive)
beast-mailbox-service my-agent --latest --count 5 --ack

# Trim messages (destructive - permanently deletes)
beast-mailbox-service my-agent --latest --count 5 --trim
```

## Architecture

### Two-Backend Design

**1. Redis Backend (`RedisMailboxService`)**
- Uses Redis Streams with consumer groups
- Stream naming: `beast:mailbox:<agent_id>:in`
- Consumer groups: `<agent_id>:group`
- Supports distributed deployment across multiple hosts
- Automatic pending message recovery

**2. Filesystem Backend (`FileSystemMailboxService`)**
- JSON files under `{base_path}/{agent_id}/inbox/`
- Atomic writes via `os.replace` (no tearing)
- Polling-based consumption
- For same-host agent communication only

### Core Components

```
src/beast_mailbox_core/
├── __init__.py              # Public API exports
├── redis_mailbox.py         # RedisMailboxService, MailboxMessage, MailboxConfig
├── filesystem_mailbox.py    # FileSystemMailboxService, FileSystemMailboxConfig
└── cli.py                   # CLI entry points (beast-mailbox-service, beast-mailbox-send)
```

**Key Classes:**
- `MailboxMessage` - Message data model (sender, recipient, payload, timestamp)
- `RedisMailboxService` - Redis Streams-based service
- `FileSystemMailboxService` - Filesystem-based service
- `MailboxConfig` / `FileSystemMailboxConfig` - Configuration dataclasses

**Async Pattern:** Both services use background tasks for message consumption with async handler registration.

### Intentionally Untestable Code

Two infinite event loops are **architecturally untestable** in unit tests:
1. `cli.py` lines 200-242: `run_service_async()` event loop
2. `redis_mailbox.py` lines 316-343: `_consume_loop()` infinite loop

**Current coverage:** 90% (100% of testable code). Don't compromise architecture for metrics.

## Quality Standards (Non-Negotiable)

The project maintains exceptional quality standards tracked via SonarCloud:

| Metric | Target | Status |
|--------|--------|--------|
| **Tests** | ≥ Cognitive Complexity | 59 tests (125% of 47 complexity) ✅ |
| **Coverage** | ≥ 85% | 90% ✅ |
| **Comment Density** | ≥ 40% | 52.2% ✅ |
| **Bugs** | 0 | 0 ✅ |
| **Code Smells** | 0 | 0 ✅ |
| **Quality Gate** | PASSED | PASSED ✅ |

**Before committing:**
1. All tests must pass (100% success rate)
2. Coverage must be ≥ 85% (90% preferred)
3. Zero bugs, vulnerabilities, or critical code smells
4. Black formatting check passes
5. Ruff linting check passes

## Documentation Standards

Every function/class requires comprehensive docstrings:

```python
def function_name(param: Type) -> ReturnType:
    """One-line summary.

    Detailed description explaining the purpose, behavior,
    and important context. Include design decisions.

    Args:
        param: Description including constraints

    Returns:
        Description of return value

    Raises:
        ExceptionType: When and why

    Example:
        >>> result = function_name("value")
        >>> print(result)

    Note:
        Design decisions, warnings, or related functions
    """
```

**Target:** ≥ 40% comment density (currently 52.2%)

## Testing Patterns

### AsyncIO Testing
```python
# Use AsyncMock for Redis clients
from unittest.mock import AsyncMock, patch

mock_client = AsyncMock()
mock_client.xadd = AsyncMock(return_value=b"123-0")

with patch('beast_mailbox_core.redis_mailbox.redis.Redis', return_value=mock_client):
    result = await service.send_message("bob", {"msg": "hi"})
```

### Service Lifecycle
```python
async def test_start_stop():
    service = RedisMailboxService("test", config)
    await service.start()  # Creates background task
    assert service._processing_task is not None
    await service.stop()   # Cancels task gracefully
    assert service._processing_task is None
```

### Real Tasks for Cancellation
```python
# Don't use AsyncMock for tasks - create real tasks
async def dummy():
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        pass

service._processing_task = asyncio.create_task(dummy())
await service.stop()  # Should cancel without errors
```

## Release Process

**⚠️ CRITICAL:** Read `AGENT.md` and `steering/release-procedure-CORRECTED.md` before any release.

### Automated Release Validation Workflow

The project has a comprehensive release validation workflow that automates all pre-release checks:

```bash
# Trigger via GitHub Actions UI:
# 1. Go to Actions → "Release Validation" workflow
# 2. Click "Run workflow"
# 3. Enter version (e.g., "0.5.1")
# 4. Click "Run workflow"
```

**The workflow validates:**
- ✅ No uncommitted changes
- ✅ On main branch
- ✅ Version in `pyproject.toml` matches input
- ✅ CHANGELOG.md has entry for version
- ✅ Git tag doesn't already exist
- ✅ Black formatting passes
- ✅ Ruff linting passes
- ✅ All tests pass
- ✅ Coverage ≥ 85%
- ✅ SonarCloud Quality Gate is PASSED

**After validation passes, the workflow automatically:**
1. Creates annotated git tag
2. Pushes tag to origin
3. Creates GitHub release with CHANGELOG notes
4. Triggers PyPI publish (via separate workflow)

### Manual Release Steps (if workflow unavailable)

```bash
# 1. Update version and changelog
# Edit pyproject.toml: version = "0.X.Y"
# Edit CHANGELOG.md: Add [0.X.Y] section

# 2. Commit changes
git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.X.Y"
git push origin main

# 3. Create and push tag
git tag -a v0.X.Y -m "Release version 0.X.Y"
git push origin v0.X.Y

# 4. Create GitHub release (triggers PyPI publish)
gh release create v0.X.Y \
  --title "v0.X.Y" \
  --notes "$(cat CHANGELOG.md | sed -n '/\[0.X.Y\]/,/\[0/p' | head -n -1)"

# 5. Verify PyPI publish
pip index versions beast-mailbox-core
```

### Release Rules (Never Break These)

❌ **NEVER:**
- Publish without committing changes first
- Publish without creating a git tag
- Skip SonarCloud quality gate check
- Rush a release

✅ **ALWAYS:**
- Update CHANGELOG.md with accurate information
- Run all tests locally before release
- Verify coverage ≥ 85%
- Create GitHub release after tagging (triggers PyPI publish)

## CI/CD Workflows

### SonarCloud Analysis (`.github/workflows/sonarcloud.yml`)
- **Triggers:** Push to main, pull requests
- **Redis service:** Included for integration tests
- **Reports:** Coverage, quality metrics, bugs, code smells

### Release Validation (`.github/workflows/release-validation.yml`)
- **Trigger:** Manual workflow dispatch
- **Purpose:** Comprehensive pre-release validation
- **Automates:** Tag creation, GitHub release, PyPI publish trigger

### PyPI Publish (`.github/workflows/publish.yml`)
- **Triggers:** GitHub release publication
- **Requires:** `PYPI_API_TOKEN` secret configured
- **Steps:** Build package, upload to PyPI

## Environment Configuration

### Redis Backend
**Priority order:**
1. CLI flags (highest priority)
2. `REDIS_URL` environment variable
3. Individual env vars (`REDIS_HOST`, `REDIS_PORT`, etc.)
4. Defaults (localhost:6379)

```bash
# Option 1: REDIS_URL (recommended)
export REDIS_URL="redis://:password@host:port/db"

# Option 2: Individual env vars
export REDIS_HOST="prod-redis.example.com"
export REDIS_PORT="6379"
export REDIS_PASSWORD="secret"
export REDIS_DB="0"
```

### Filesystem Backend
```bash
# Optional overrides
export BEAST_MAILBOX_FS_ROOT="/var/beast/mailbox"
export BEAST_MAILBOX_FS_POLL_INTERVAL="0.5"
export BEAST_MAILBOX_FS_MKDIR_MODE="755"
```

## Workflow Philosophy: cc-sdd Spec-Driven Development

This project uses **cc-sdd** (Customize Spec-Driven Development), a framework that transforms AI coding agents from prototyping to production-ready development. The tooling is installed at `/Volumes/lemon/cursor/cc-sdd`.

### Core Principles

1. **Specs = Deterministic Slash Commands** - ALL spec work flows through `/kiro:` commands; never hand-edit `.kiro/specs/`
2. **Shared Project Memory** - Run `/kiro/steering` when context changes so guidance lands in `.kiro/steering/`
3. **3-Phase Approval Workflow** - Requirements → Design → Tasks → Implementation (human review required each phase)
4. **Keep cc-sdd in Sync** - Re-run installer if commands drift:
   ```bash
   node /Volumes/lemon/cursor/cc-sdd/tools/cc-sdd/dist/cli.js --cursor --lang en --yes
   ```

### Active Specifications

The project has 19 active specifications in `.kiro/specs/`:

**Core Features (Implemented):**
- `redis-mailbox` - Redis Streams backend (✅ tasks-generated, ready for implementation)
- `filesystem-mailbox` - Filesystem backend (✅ tasks-generated, approved for implementation)
- `cli-mailbox` - CLI utilities (✅ tasks-generated)
- `filesystem-mailbox-smoke` - Smoke tests for filesystem backend (✅ tasks-generated)

**Platform & Infrastructure:**
- `rpg2k-platform-definition` - RPG2K platform canonical definition (📋 tasks-generated, design not approved)
- `prometheus-pushgateway` - Prometheus integration (✅ tasks-generated)
- `telemetry-dashboards` - Observability dashboards (✅ tasks-generated)
- `channel-blaster-framework` - Multi-channel broadcast framework (✅ tasks-generated)

**Planned Features:**
- `sqlite-mailbox` - SQLite backend (🔧 initialized)
- `repeatable-release-bolt` - Release automation (🔧 initialized)
- `snowflake-mailbox-audit` - Audit logging to Snowflake (✅ tasks-generated)
- `servicenow-gateway-callback` - ServiceNow integration (✅ tasks-generated)

**Infrastructure:**
- `tardigrade-mode` - Resilient deployment mode (✅ tasks-generated)
- `tardigrade-management` - Management utilities (✅ tasks-generated)
- `remote-vscode-tunnel-devcontainer` - Remote dev environment (📝 requirements-generated)
- `windows-vpc-remote-dev` - Windows VPC development (✅ tasks-generated)

**Check spec status:** `/kiro/spec-status {feature-name}`

### Workflow Example

```bash
# 1. Start with steering context (when joining or context changes)
/kiro/steering

# 2. Initialize new feature
/kiro/spec-init "Add WebSocket transport backend"

# 3. Define requirements
/kiro/spec-requirements websocket-backend

# 4. (Optional) Validate against existing codebase
/kiro/validate-gap websocket-backend

# 5. Create design (requires approval)
/kiro/spec-design websocket-backend

# 6. (Optional) Review design
/kiro/validate-design websocket-backend

# 7. Break down into tasks (requires approval)
/kiro/spec-tasks websocket-backend

# 8. Implement tasks
/kiro/spec-impl websocket-backend

# 9. (Optional) Validate implementation
/kiro/validate-impl websocket-backend
```

**Document deviations in AGENT.md** if workflow steps cannot use `/kiro`.

## Critical Context

### AI-Native Development
This repository was **built 100% by AI agents** and is maintained by AI agents. Key resources:
- **AGENT.md** - Comprehensive maintainer guide for AI agents (1400+ lines)
- **AGENTS.md** - Spec-driven development workflow and rules (cc-sdd/Kiro)
- **.kiro/steering/** - Project memory (product.md, tech.md, structure.md)
- **docs/LESSONS_LEARNED_v0.3.0.md** - 80+ lessons from v0.1.0 → v0.3.0
- **steering/release-procedure-CORRECTED.md** - Mandatory release procedure

### Historical Crisis
**v0.2.0 Crisis:** A release was published to PyPI without committing to the repository, causing critical sync failure. The release validation workflow and comprehensive procedures exist to prevent this from ever happening again.

**Core Principle:** Repository is source of truth. ALWAYS commit → tag → push → then publish.

### Quality Philosophy
**"Quality is a choice, not a circumstance."** Project went from 0% coverage crisis to 90% coverage, 52% documentation density, 0 defects in one development session. Excellence is achievable through systematic pursuit of quality.

## Important Files

| File | Purpose |
|------|---------|
| `AGENT.md` | Comprehensive AI maintainer guide (READ THIS!) |
| `AGENTS.md` | Spec-driven development workflow and Kiro rules (CRITICAL!) |
| `.kiro/steering/product.md` | Product vision and capabilities (Project Memory) |
| `.kiro/steering/tech.md` | Technology stack and standards (Project Memory) |
| `.kiro/steering/structure.md` | Organization patterns and conventions (Project Memory) |
| `.kiro/specs/` | Active specifications (19 specs) - managed via `/kiro:` commands |
| `pyproject.toml` | Package metadata, version, dependencies, pytest config |
| `CHANGELOG.md` | Release notes (update before each release) |
| `README.md` | User-facing documentation |
| `.cursor/rules.md` | Cursor workspace rules (Kiro spec workflow) |
| `.cursor/commands/kiro/` | Kiro slash commands (11 commands) |
| `steering/release-procedure-CORRECTED.md` | Detailed release checklist |
| `docs/LESSONS_LEARNED_v0.3.0.md` | Historical context and hard-won lessons |
| `sonar-project.properties` | SonarCloud configuration |

## Common Tasks

### Adding a Feature (Spec-Driven)
1. Load steering context: `/kiro/steering`
2. Initialize spec: `/kiro/spec-init "feature description"`
3. Define requirements: `/kiro/spec-requirements {feature-name}`
4. (Optional) Validate against existing code: `/kiro/validate-gap {feature-name}`
5. Create design: `/kiro/spec-design {feature-name}`
6. Generate tasks: `/kiro/spec-tasks {feature-name}`
7. Implement: `/kiro/spec-impl {feature-name}`
8. Verify coverage ≥ 85%, all tests pass
9. Push and verify SonarCloud passes

### Fixing a Bug
1. Create failing test case that reproduces bug
2. Implement minimal fix
3. Verify test passes and no regressions
4. Update CHANGELOG.md under `### Fixed`
5. Add inline comments for design decisions

### Updating Dependencies
1. Check for updates: `pip list --outdated`
2. Update `pyproject.toml`
3. Test with new version: `pip install -e ".[dev]"`
4. Run full test suite: `pytest tests/`
5. Verify no breaking changes

## Support & Resources

- **GitHub:** https://github.com/nkllon/beast-mailbox-core
- **PyPI:** https://pypi.org/project/beast-mailbox-core/
- **SonarCloud:** https://sonarcloud.io/project/overview?id=nkllon_beast-mailbox-core
- **cc-sdd:** https://github.com/gotalab/cc-sdd (Spec-Driven Development framework)
- **cc-sdd npm:** https://www.npmjs.com/package/cc-sdd (v2.0.0-alpha.3)
- **Local cc-sdd:** /Volumes/lemon/cursor/cc-sdd (fork: https://github.com/nkllon/cc-sdd)
- **Documentation:** docs/API.md, docs/USAGE_GUIDE.md, docs/QUICK_REFERENCE.md

## Key Principles

1. **Quality First:** Never compromise quality for speed
2. **Test Everything:** If testable, it must be tested
3. **Document Thoroughly:** Explain why, not just what
4. **Follow Specs:** Use Kiro workflow for all spec work; never hand-edit `.kiro/specs/`
5. **Load Steering:** Always run `/kiro/steering` before creating or updating specifications
6. **Learn Continuously:** Update documentation with new lessons
7. **Repository = Truth:** Always commit before publishing

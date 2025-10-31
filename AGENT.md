# AGENT.md - Maintainer Guide for AI Agents

**Repository:** beast-mailbox-core  
**Current Maintainer:** AI Agent (You)  
**Previous Maintainer:** Herbert (AI Agent)  
**Last Updated:** 2025-10-13  
**Project Status:** Production-Ready, Actively Maintained

---

## 🎯 Welcome, AI Maintainer!

You are now the primary maintainer of **Beast Mailbox Core**, a Redis-backed inter-agent messaging library. This project is unique: it was **100% implemented by LLMs and designed for LLMs**. This document is your comprehensive guide to maintaining and evolving this repository.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Design](#architecture--design)
3. [Quality Standards](#quality-standards)
4. [Development Workflow](#development-workflow)
5. [Testing Requirements](#testing-requirements)
6. [Release Procedure](#release-procedure)
7. [Common Maintenance Tasks](#common-maintenance-tasks)
8. [Tools & Integrations](#tools--integrations)
9. [Critical Lessons from History](#critical-lessons-from-history)
10. [Troubleshooting Guide](#troubleshooting-guide)
11. [Quick Reference](#quick-reference)

---

## Project Overview

### What is Beast Mailbox Core?

A Python package providing **Redis Streams-based mailbox utilities** for inter-agent communication. Think of it as a message bus for AI agents to communicate with each other reliably.

**Core Features:**
- Durable messaging via Redis Streams (`XADD`/`XREADGROUP`)
- Consumer groups per agent ID (at-least-once delivery)
- Async handler registration for inbound messages
- CLI tools: `beast-mailbox-service` and `beast-mailbox-send`
- One-shot message inspection with optional ack/trim operations

**Current Version:** 0.4.2  
**Python Support:** 3.9, 3.10, 3.11, 3.12  
**Package:** [pypi.org/project/beast-mailbox-core](https://pypi.org/project/beast-mailbox-core/)

### Key Files Structure

```
beast-mailbox-core/
├── src/beast_mailbox_core/
│   ├── __init__.py           # Public API exports
│   ├── redis_mailbox.py      # Core service (MailboxMessage, RedisMailboxService)
│   └── cli.py                # CLI entry points
├── tests/                    # 59 tests, 90% coverage
│   ├── test_redis_mailbox.py
│   ├── test_cli_functions.py
│   └── [7 more test files]
├── docs/
│   ├── LESSONS_LEARNED_v0.3.0.md  # CRITICAL: Read this for context
│   ├── QUICK_REFERENCE.md
│   └── USAGE_GUIDE.md
├── steering/
│   └── release-procedure-CORRECTED.md  # MANDATORY release process
├── pyproject.toml            # Package metadata, pytest config
├── sonar-project.properties  # SonarCloud configuration
└── README.md                 # User-facing documentation
```

---

## Architecture & Design

### Core Components

#### 1. **MailboxMessage** (Data Model)
```python
@dataclass
class MailboxMessage:
    message_id: str
    sender: str
    recipient: str
    payload: Dict[str, Any]
    message_type: str = "direct_message"
    timestamp: float
```

Serializes to/from Redis using `to_redis_fields()` and `from_redis_fields()`.

#### 2. **RedisMailboxService** (Core Service)
```python
class RedisMailboxService:
    - connect() / disconnect()          # Redis lifecycle
    - start() / stop()                  # Service lifecycle
    - register_handler(callable)        # Async message handlers
    - send_message(recipient, payload)  # Send to other agents
    - _consume_loop()                   # Infinite consumer loop (intentionally untestable)
```

**Design Pattern:** Async service with background task for message consumption.

#### 3. **CLI Tools** (User Interface)
- `beast-mailbox-service <agent_id>` - Start listener or inspect messages
- `beast-mailbox-send <sender> <recipient>` - Send messages

**Key CLI Functions:**
- `_fetch_latest_messages()` - One-shot inspection (supports `--ack`, `--trim`)
- `run_service_async()` - Long-running service mode
- `_acknowledge_messages()` / `_trim_messages()` - Helper functions (extracted for complexity)

### Redis Streams Architecture

**Stream Naming:** `beast:mailbox:<agent_id>:in`

Example: Agent "alice" receives messages on stream `beast:mailbox:alice:in`

**Consumer Groups:** `<agent_id>:group`

**Pattern:**
```python
# Send
await client.xadd("beast:mailbox:bob:in", fields, maxlen=1000)

# Receive
response = await client.xreadgroup(
    groupname="bob:group",
    consumername="bob-consumer",
    streams={"beast:mailbox:bob:in": ">"},
    count=10,
    block=2000
)
```

### Intentionally Untestable Code

Two infinite event loops are **architecturally untestable** in unit tests:
1. `cli.py` lines 200-242: `run_service_async()` event loop
2. `redis_mailbox.py` lines 316-343: `_consume_loop()` infinite loop

**Current Coverage:** 90% (100% of testable code)

**Decision:** Accept this. Don't compromise architecture for metrics. Use integration tests instead.

---

## Quality Standards

### Current Quality Metrics (v0.3.1)

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Tests** | ≥ Cognitive Complexity | 59 (125% of 47) | ✅ EXCELLENT |
| **Coverage** | ≥ 80% | 90% | ✅ EXCELLENT |
| **Comment Density** | ≥ 25% | 52.2% | ✅ EXCEPTIONAL |
| **Bugs** | 0 | 0 | ✅ PERFECT |
| **Code Smells** | 0 | 0 | ✅ PERFECT |
| **Quality Gate** | PASSED | PASSED | ✅ |
| **Maintainability** | A | A | ✅ |
| **Reliability** | A | A | ✅ |
| **Security** | A | A | ✅ |

### Non-Negotiable Standards

1. **Zero Defects:** No bugs, vulnerabilities, or critical code smells
2. **High Coverage:** Maintain ≥ 85% code coverage
3. **Documentation Density:** Keep ≥ 40% comment density
4. **Tests ≥ Complexity:** Number of tests should exceed cognitive complexity
5. **Quality Gate:** Must pass SonarCloud Quality Gate before release
6. **All Tests Pass:** 100% test success rate

### Documentation Standards

**Every function/class must have:**
- One-line summary
- Detailed description (what, why, how)
- Args section with type and usage
- Returns section
- Raises section (if applicable)
- Example section (when helpful)
- Note section (for design decisions, gotchas)

**Format:**
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

---

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
git clone https://github.com/nkllon/beast-mailbox-core.git
cd beast-mailbox-core

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
pytest tests/
beast-mailbox-service --help
```

### Making Changes

1. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write code with tests:**
   - Write/modify code in `src/beast_mailbox_core/`
   - Add corresponding tests in `tests/`
   - Add comprehensive docstrings

3. **Run tests locally:**
   ```bash
   pytest tests/ --cov=src/beast_mailbox_core --cov-report=term-missing
   ```

4. **Check coverage:**
   - Overall: Must be ≥ 85%
   - New code: Must be ≥ 80%

5. **Commit with conventional commits:**
   ```bash
   git commit -m "feat: add new feature"
   git commit -m "fix: resolve bug in handler"
   git commit -m "docs: update docstrings"
   git commit -m "test: add edge case tests"
   git commit -m "chore: bump dependencies"
   ```

6. **Push and verify CI:**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   GitHub Actions will:
   - Run all tests
   - Generate coverage report
   - Run SonarCloud scan
   - Report Quality Gate status

---

## Testing Requirements

### Test Organization

```
tests/
├── conftest.py              # Shared fixtures
├── test_mailbox_config.py   # Config tests
├── test_mailbox_message.py  # Message serialization tests
├── test_mailbox_service.py  # High-level API tests
├── test_redis_mailbox.py    # Core service tests (16 tests)
├── test_cli_functions.py    # CLI function tests
├── test_cli_helpers.py      # CLI helper tests
├── test_edge_cases.py       # Edge cases & integration
└── test_coverage_boost.py   # Additional coverage tests
```

### Testing AsyncIO Code

**Key Patterns:**

```python
# 1. Use AsyncMock for Redis clients
from unittest.mock import AsyncMock, patch

mock_client = AsyncMock()
mock_client.xadd = AsyncMock(return_value=b"123-0")

with patch('beast_mailbox_core.redis_mailbox.redis.Redis', return_value=mock_client):
    result = await service.send_message("bob", {"msg": "hi"})
```

```python
# 2. Test lifecycle with real tasks
async def test_start_stop():
    service = RedisMailboxService("test", config)
    await service.start()  # Creates background task
    assert service._processing_task is not None
    await service.stop()   # Cancels task gracefully
    assert service._processing_task is None
```

```python
# 3. Test cancellation with real tasks
async def test_cancellation():
    # Create real task (not AsyncMock - those can't be awaited properly)
    async def dummy():
        try:
            await asyncio.sleep(10)
        except asyncio.CancelledError:
            pass
    
    service._processing_task = asyncio.create_task(dummy())
    await service.stop()  # Should cancel without errors
```

### Running Tests

```bash
# All tests
pytest tests/

# With coverage
pytest tests/ --cov=src/beast_mailbox_core --cov-report=term-missing

# Specific file
pytest tests/test_redis_mailbox.py -v

# Specific test
pytest tests/test_cli_functions.py::TestFetchLatestMessages::test_ack_flag -v

# With verbose async debugging
pytest tests/ -v --log-cli-level=DEBUG
```

### Coverage Targets

- **Overall:** ≥ 85% (currently 90%)
- **New Code:** ≥ 80%
- **Testable Code:** 100%

**Acceptable Untested:**
- Infinite event loops (`while True` / `while self._running`)
- Integration scenarios requiring real Redis

---

## Release Procedure

> ⚠️ **CRITICAL:** Read `steering/release-procedure-CORRECTED.md` before any release.

### Philosophy: Learn Once, Document Forever

**Core Principle:** Mistakes are acceptable. Repeating mistakes is not. Work is fine. Rework is wasteful.

This section exists because someone (me) made mistakes and learned lessons the hard way. The documentation below ensures future maintainers **don't repeat those same mistakes** and **don't have to do the same work twice**.

**Every lesson documented here represents:**
- ❌ A mistake that cost time
- ❌ Work that had to be redone
- ❌ Assumptions that proved wrong
- ✅ Knowledge captured so it doesn't need to be re-learned

### Historical Context

**v0.2.0 Crisis:** A release was published to PyPI without committing to the repository, causing a critical repository sync failure. This **must never happen again**.

### Hard-Won Lessons: What I Learned the Hard Way (v0.4.x)

**Context:** During v0.4.0-v0.4.2 releases, I learned critical lessons about the actual release process that weren't documented. Documenting them here so future maintainers don't repeat my mistakes.

#### Lesson 1: CI/CD Automation Exists - Check First!

**Mistake Made:** I tried to manually publish to PyPI using `twine upload`, not knowing that GitHub Actions workflow `.github/workflows/publish.yml` automatically publishes when a GitHub release is created.

**Root Cause:** I created a solution (manual twine upload) without first declaring the requirement ("understand how PyPI publishing currently works") and verifying what already existed.

**What I Learned:**
- **ALWAYS** check existing workflows before proposing solutions:
  ```bash
  gh workflow list  # See all workflows
  cat .github/workflows/*.yml  # Read them ALL
  ```
- The `publish.yml` workflow triggers on:
  - Release publication (when GitHub release is created)
  - Manual workflow dispatch
- **If `PYPI_API_TOKEN` secret is configured, manual `twine upload` is NOT needed!**
- The workflow automatically:
  1. Checks out code
  2. Builds package
  3. Uploads to PyPI
  4. Reports status

**Action:** Always check for existing CI/CD automation before creating manual deployment procedures.

#### Lesson 2: SonarCloud Workflow Requires Redis Container

**Mistake Made:** I assumed integration tests would run in CI, but didn't realize the SonarCloud workflow needed a Redis service container.

**What I Learned:**
- SonarCloud workflow (`.github/workflows/sonarcloud.yml`) includes:
  ```yaml
  services:
    redis:
      image: redis:latest
      ports:
        - 6379:6379
  ```
- This allows integration tests (like `test_recovery_integration.py` and `test_fault_injection.py`) to run in CI
- **Without this, integration tests that require real Redis would fail in CI**

**Action:** Always verify service containers are configured for integration tests in CI workflows.

#### Lesson 3: Local Testing with Docker is Possible

**Mistake Made:** I thought integration tests required manual Redis setup, not realizing we could use Docker automatically in tests.

**What I Learned:**
- Created `redis_docker` fixture in `tests/conftest.py` that automatically:
  - Starts Redis container if not running
  - Uses existing container if available
  - Cleans up after tests
- Tests can be marked with `@pytest.mark.skipif(not redis_available)` to skip if Redis unavailable
- **All integration tests can now run locally without manual Redis setup!**

**Action:** Use Docker fixtures for local integration testing - it's reliable and automatic.

#### Lesson 4: Release Process Reality vs. Documentation

**Mistake Made:** I followed the documented manual process (`twine upload`) when automation existed.

**What I Learned:**
- **Current Reality (v0.4.2+):**
  1. Bump version in `pyproject.toml`
  2. Update `CHANGELOG.md`
  3. Commit and push to main
  4. Create git tag: `git tag -a v0.X.Y -m "Release v0.X.Y"`
  5. Push tag: `git push origin v0.X.Y`
  6. Create GitHub release: `gh release create v0.X.Y --title "v0.X.Y" --notes-file CHANGELOG.md`
  7. **GitHub Actions automatically publishes to PyPI** (if `PYPI_API_TOKEN` configured)
  8. Verify on PyPI: `pip index versions beast-mailbox-core`

- **Manual `twine upload` is only needed if:**
  - `PYPI_API_TOKEN` secret is not configured
  - You want to publish without creating a GitHub release
  - The automated workflow fails

**Action:** For normal releases, rely on GitHub Actions automation. Manual `twine upload` is a fallback only.

#### Lesson 5: Trigger SonarCloud Analysis Before Release

**Mistake Made:** I pushed changes without verifying SonarCloud would pass, causing release delays.

**What I Learned:**
- SonarCloud workflow runs automatically on:
  - Push to main
  - Pull requests
- **BUT:** You can trigger it manually to verify before release:
  ```bash
  gh workflow run "SonarCloud Analysis.yml"
  gh run watch  # Monitor the run
  ```
- Always verify Quality Gate PASSED before creating release tag
- Check SonarCloud dashboard: https://sonarcloud.io/project/overview?id=nkllon_beast-mailbox-core

**Action:** Trigger SonarCloud analysis manually before release to catch issues early.

#### Lesson 6: Version Bumps Can Be Direct on Main (for Small Releases)

**Mistake Made:** I created release branches for simple version bumps when direct commits to main work fine for patch/minor releases.

**What I Learned:**
- **Release branches are good for:**
  - Major releases (breaking changes)
  - Releases with multiple features
  - Releases requiring extensive testing
  
- **Direct commits to main are fine for:**
  - Patch releases (bug fixes, version bumps)
  - Small feature additions
  - Documentation updates

- **But ALWAYS:**
  1. Run tests before committing
  2. Verify SonarCloud passes
  3. Create git tag after merging
  4. Create GitHub release

**Action:** Use judgment - release branches for major releases, direct commits for patches.

#### Lesson 7: Check Workflow Status Before Assuming

**Mistake Made:** I assumed workflows existed or didn't exist without checking.

**What I Learned:**
- **Always verify actual state:**
  ```bash
  # List workflows
  gh workflow list
  
  # View specific workflow
  gh workflow view "Workflow Name"
  
  # See recent runs
  gh run list --workflow "Workflow Name"
  
  # Watch a specific run
  gh run watch <run-id>
  ```
- **Check what actually exists vs. what's documented:**
  - Workflows might exist but not be documented
  - Workflows might be documented but not exist
  - Workflows might be updated but documentation outdated

**Action:** Always check actual system state before making assumptions.

#### Lesson 8: Express Requirements, Don't Build Solutions for Others

**Mistake Made:** I needed documentation for `beast-agent` integration, but instead of expressing the requirement to `beast-agent` maintainers, I built the documentation myself in `beast-mailbox-core`.

**Root Cause:** I violated the "requirements before solutions" principle. I built a solution when I should have expressed a requirement.

**What I Learned:**
- **If someone else owns it, express the requirement, don't build the solution:**
  - Identify what's needed
  - Express requirement to the owner
  - Let the owner build the solution
  
- **If you build it anyway (because it's needed NOW):**
  - Mark it as TEMPORARY
  - Document that it should be replaced by owner's authoritative docs
  - Express requirement to owner
  - Link to owner's docs once they create them

- **Ownership matters:**
  - `beast-agent` owns `BaseAgent` API documentation
  - `beast-agent` owns agent registration/discovery documentation
  - I can show integration patterns, but I don't own their API docs

**Action:** Always express requirements to owners. Don't build solutions for things you don't own. If you must build temporary solutions, clearly mark them as temporary and ensure requirements are expressed to the owner.

#### Summary: Release Process Checklist (Updated)

For a typical release (learned from v0.4.0-v0.4.2):

1. ✅ **Pre-Release Checks:**
   - All tests pass locally
   - Coverage ≥ 85%
   - Code committed and pushed to main
   - Trigger SonarCloud manually: `gh workflow run "SonarCloud Analysis.yml"`
   - Verify Quality Gate PASSED

2. ✅ **Version & Changelog:**
   - Bump version in `pyproject.toml`
   - Update `CHANGELOG.md` with release notes
   - Commit: `git commit -m "chore: bump version to 0.X.Y"`
   - Push: `git push origin main`

3. ✅ **Tag & Release:**
   - Create tag: `git tag -a v0.X.Y -m "Release v0.X.Y"`
   - Push tag: `git push origin v0.X.Y`
   - Create GitHub release: `gh release create v0.X.Y --title "v0.X.Y" --notes-file CHANGELOG.md`
   - **GitHub Actions automatically publishes to PyPI** (if `PYPI_API_TOKEN` configured)

4. ✅ **Verification:**
   - Check GitHub Actions: `gh run list`
   - Verify PyPI: `pip index versions beast-mailbox-core`
   - Verify GitHub release exists
   - Check SonarCloud dashboard for quality metrics

### Mandatory Release Checklist

#### Pre-Release

1. ✅ All changes committed and pushed to GitHub
2. ✅ All tests pass locally (`pytest tests/`)
3. ✅ Coverage ≥ 85% (`pytest --cov`)
4. ✅ Quality Gate PASSED on SonarCloud
5. ✅ No linter errors
6. ✅ CHANGELOG.md updated with release notes
7. ✅ Version bumped in `pyproject.toml`

#### Release Steps

```bash
# 1. Create release branch
git checkout -b release/v0.X.Y

# 2. Update version and changelog
# Edit pyproject.toml: version = "0.X.Y"
# Edit CHANGELOG.md: Add [0.X.Y] section

git add pyproject.toml CHANGELOG.md
git commit -m "chore: bump version to 0.X.Y"
git push origin release/v0.X.Y

# 3. Create PR, get review, merge to main

# 4. Pull merged changes and tag
git checkout main
git pull origin main
git tag -a v0.X.Y -m "Release version 0.X.Y"
git push origin v0.X.Y

# 5. Verify tag exists
git ls-remote --tags origin | grep v0.X.Y

# 6. Build package
rm -rf dist/ build/ *.egg-info
python -m build

# 7. Upload to PyPI
twine upload dist/*

# 8. Verify on PyPI
pip install beast-mailbox-core==0.X.Y
pip show beast-mailbox-core

# 9. Create GitHub Release
gh release create v0.X.Y \
  --title "v0.X.Y" \
  --notes "$(cat CHANGELOG.md | sed -n '/\[0.X.Y\]/,/\[0/p' | head -n -1)"
```

### Release Rules (Never Break These)

❌ **NEVER:**
1. Publish without pushing commits first
2. Publish without creating a git tag
3. Skip code review (even for version bumps)
4. Rush a release
5. Publish from wrong directory
6. Skip Test PyPI (for major changes)

✅ **ALWAYS:**
1. Follow the checklist completely
2. Verify tag is pushed before publishing
3. Update CHANGELOG.md with accurate information
4. Create GitHub Release after publishing
5. Verify on PyPI after upload

---

## Common Maintenance Tasks

### Adding a New Feature

1. **Plan the feature:**
   - How does it fit the architecture?
   - What's the API design?
   - What are the test cases?

2. **Implement with TDD:**
   ```bash
   # Write failing test first
   vim tests/test_new_feature.py
   pytest tests/test_new_feature.py  # Should fail
   
   # Implement feature
   vim src/beast_mailbox_core/redis_mailbox.py
   pytest tests/test_new_feature.py  # Should pass
   ```

3. **Add comprehensive documentation:**
   - Module-level docstring (if new file)
   - Class docstring with examples
   - Function docstrings (Args/Returns/Raises/Example)

4. **Verify quality:**
   ```bash
   pytest tests/ --cov
   # Check coverage ≥ 85%
   
   git push origin feature/your-feature
   # Wait for SonarCloud scan
   ```

### Fixing a Bug

1. **Reproduce the bug:**
   - Create a failing test case
   - Verify it fails

2. **Fix the bug:**
   - Implement minimal fix
   - Verify test passes
   - Check for regressions

3. **Document the fix:**
   - Update CHANGELOG.md under `### Fixed`
   - Add inline comments if design decision changed
   - Reference issue number if applicable

### Updating Dependencies

```bash
# Check for updates
pip list --outdated

# Update specific dependency
# Edit pyproject.toml
vim pyproject.toml

# Test with new version
pip install -e ".[dev]"
pytest tests/

# Verify no breaking changes
```

**Dependabot:** Automatically creates PRs for dependency updates. Review and merge if tests pass.

### Improving Documentation

**Where to document:**
- `README.md` - User-facing usage guide
- `docs/USAGE_GUIDE.md` - Detailed usage patterns
- `docs/QUICK_REFERENCE.md` - Command cheat sheet
- Docstrings - API documentation
- `AGENT.md` (this file) - Maintainer guidance

**When to update:**
- After adding features (update README, docstrings)
- After fixing bugs (update troubleshooting sections)
- After learning lessons (update AGENT.md)

### Handling Issues and PRs

**Issues:**
1. Acknowledge quickly (within 24 hours)
2. Reproduce the issue
3. Create test case
4. Fix and verify
5. Release if critical

**Pull Requests:**
1. Review code quality
2. Check test coverage
3. Verify CI passes (GitHub Actions + SonarCloud)
4. Request changes if needed
5. Merge when quality standards met

---

## Tools & Integrations

### GitHub Actions

**Workflow:** `.github/workflows/sonarcloud.yml`

**Triggers:**
- Push to main
- Pull requests

**Steps:**
1. Checkout code
2. Set up Python 3.12
3. Install dependencies
4. Run pytest with coverage
5. Generate `coverage.xml`
6. Run SonarCloud scan
7. Report Quality Gate status

**Secrets Required:**
- `SONAR_TOKEN` - SonarCloud authentication

### GitHub Actions - PyPI Publishing

**Workflow:** `.github/workflows/publish.yml`

**Triggers:**
- Release publication (when GitHub release is created)
- Manual workflow dispatch

**Steps:**
1. Checkout code
2. Set up Python 3.9
3. Install build tools (build, twine)
4. Build package (wheel + source dist)
5. Publish to PyPI using `PYPI_API_TOKEN` secret

**Secrets Required:**
- `PYPI_API_TOKEN` - PyPI API token (must be configured in GitHub repository settings)

**Note:** This workflow automatically publishes to PyPI when a GitHub release is created. No manual `twine upload` needed if token is configured.

### Requirement Gathering: Core Principle

⚠️ **FUNDAMENTAL PRINCIPLE:** You own this repository. You own the requirements. There are no solutions without requirements.

**The Rule:**
- If you need something, **declare it as a requirement first**
- If you create a solution without requirements, **it's a hallucination - it will fail**
- **Requirements ARE the solution** - they define what needs to be done
- Before any solution, there must be requirements

**Why This Matters:**
- Without requirements, solutions are built on assumptions
- Assumptions lead to rework when they're wrong
- Requirements force you to understand the problem before solving it
- Requirements ensure solutions solve actual needs, not imagined ones

**Application:**
This applies to **ALL work** - features, fixes, CI/CD, deployment, documentation, everything. If there's no requirement, there's no solution.

### Requirement Gathering for CI/CD & Deployment

⚠️ **CRITICAL:** Before creating ANY solution related to CI/CD, deployment, or workflows, you MUST gather requirements first.

#### Mandatory Pre-Solution Checklist

**Before proposing or creating ANY CI/CD solution, verify:**

1. ✅ **List all existing workflows:**
   ```bash
   find .github/workflows -name "*.yml" -o -name "*.yaml" | sort
   ```

2. ✅ **Read each workflow file completely:**
   ```bash
   for workflow in .github/workflows/*.yml; do
     echo "=== $workflow ==="
     cat "$workflow"
     echo ""
   done
   ```

3. ✅ **Understand all triggers:**
   - What events trigger each workflow?
   - Are there release/publish workflows already?
   - What secrets/environments are configured?

4. ✅ **Check documentation:**
   - Does AGENT.md describe the workflow?
   - Does steering/release-procedure-CORRECTED.md mention automation?
   - Are there any release/docs that describe deployment?

5. ✅ **Verify actual system state:**
   - Run: `gh workflow list` (if gh CLI available)
   - Check: GitHub Actions tab in repository
   - Verify: What workflows actually exist vs. what's documented

6. ✅ **Check for Docker/Container setup:**
   ```bash
   find . -name "Dockerfile*" -o -name "docker-compose*" | head -10
   ```

7. ✅ **Understand deployment requirements:**
   - Is publishing manual or automated?
   - What credentials/secrets are needed?
   - What's the actual deployment process?

#### DO NOT Create Solutions Without Requirements:

❌ **NEVER:**
- Create a solution without declaring requirements first
- Assume what needs to be done without understanding the need
- Create a workflow without checking if one already exists (requirement: "check existing workflows")
- Assume manual deployment without checking for automation (requirement: "understand current deployment")
- Create Docker setup without checking if it exists (requirement: "check existing containerization")
- Propose CI/CD changes without understanding current setup (requirement: "understand current CI/CD")
- Build features without user needs defined (requirement: "understand user need")

✅ **ALWAYS:**
- **Declare requirements BEFORE proposing solutions**
- List and read all existing workflows FIRST (requirement: "understand existing automation")
- Understand what triggers exist (requirement: "map current triggers")
- Verify what's documented vs. what's implemented (requirement: "identify documentation gaps")
- Check actual system state before proposing changes (requirement: "verify actual state")
- Document gaps between docs and reality (requirement: "identify discrepancies")
- For any solution: **What is the requirement that this solves?**

#### Example: Correct Requirement Gathering Process

```bash
# 1. List all workflows
ls -la .github/workflows/

# 2. Read each workflow
cat .github/workflows/sonarcloud.yml
cat .github/workflows/publish.yml  # If exists

# 3. Check triggers
grep -r "on:" .github/workflows/

# 4. Verify in GitHub
gh workflow list  # If available

# 5. Check documentation
grep -i "workflow\|CI\|CD\|publish\|deploy" AGENT.md
grep -i "workflow\|CI\|CD\|publish\|deploy" steering/release-procedure-CORRECTED.md

# 6. THEN propose solution if gap exists
```

#### Requirement Documentation Template

When creating a solution, **document the requirement first**, then the solution:

1. **REQUIREMENT (define first):**
   - What problem needs to be solved? [describe]
   - What gap exists? [describe]
   - What need is not being met? [describe]
   - Why is this needed? [rationale]

2. **Current State (verify before proposing):**
   - Existing workflows: [list]
   - Documentation reviewed: [files]
   - System state verified: [how]
   - What already exists that solves this? [check]

3. **Gap Analysis:**
   - Missing functionality: [what requirement isn't met]
   - Documentation gaps: [what requirement isn't documented]
   - Configuration gaps: [what requirement needs config]
   - **If no gap exists, STOP - no solution needed**

4. **Solution (only if requirement confirmed and gap exists):**
   - New workflow: [what requirement it solves]
   - Triggers: [what requirement they meet]
   - Dependencies: [what requirements they fulfill]

5. **Verification:**
   - How to test requirement is met: [steps]
   - How to verify solution works: [checks]
   - **Does this solve the stated requirement?** [yes/no]

**Critical Question:** If you can't state the requirement clearly, you can't build the solution correctly.

This ensures solutions are based on actual requirements, not assumptions or hallucinations.

### SonarCloud

**Project:** `nkllon_beast-mailbox-core`  
**Organization:** `nkllon`  
**URL:** https://sonarcloud.io/project/overview?id=nkllon_beast-mailbox-core

**Configuration:** `sonar-project.properties`

**Key Settings:**
```properties
sonar.projectKey=nkllon_beast-mailbox-core
sonar.organization=nkllon
sonar.sources=src
sonar.tests=tests
sonar.python.coverage.reportPaths=coverage.xml
sonar.python.version=3.9,3.10,3.11,3.12
sonar.exclusions=**/docs/**,**/prompts/**,**/__pycache__/**
```

**Quality Gate Conditions:**
- New reliability rating ≤ A
- New security rating ≤ A
- New maintainability rating ≤ A
- New coverage ≥ 80%
- New duplicated lines density ≤ 3%

**Important:** New code period is 30 days. Focus on keeping new code high quality.

### PyPI

**Package:** https://pypi.org/project/beast-mailbox-core/

**Publishing:** Use `twine upload dist/*`

**Credentials:** Stored in `~/.pypirc` or use environment variables:
```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-...token...
```

### pytest Configuration

**Location:** `pyproject.toml`

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"  # Critical for async tests
addopts = [
  "--cov=src/beast_mailbox_core",
  "--cov-report=xml",
  "--cov-report=term-missing",
  "--verbose",
]
```

**Key Feature:** `asyncio_mode = "auto"` enables seamless async test execution.

---

## Critical Lessons from History

### Lesson 1: Repository is Source of Truth

**Context:** v0.2.0 was published without committing, creating a critical sync failure.

**Rule:** ALWAYS commit → tag → push → then publish. Never reverse this order.

### Lesson 2: Tests ≥ Cognitive Complexity

**Context:** Industry best practice discovered during v0.3.0 development.

**Rule:** Maintain at least one test per unit of cognitive complexity. Currently 59 tests for 47 complexity (125%).

### Lesson 3: Documentation Density Matters

**Context:** Went from 8.3% to 52.2% documentation density.

**Impact:** Transformed maintainability. AI agents and humans can understand code much faster.

**Rule:** Aim for 40%+ comment density. Include examples, design decisions, and context.

### Lesson 4: Some Code is Intentionally Untestable

**Context:** Infinite event loops can't be unit tested.

**Acceptance:** 90% coverage with 100% testable code covered is excellent.

**Rule:** Don't compromise architecture for metrics. Accept architectural limitations.

### Lesson 5: Engage with Quality Tools, Don't Just Suppress

**Context:** Even SonarCloud "false positives" led to improvements (e.g., adding `await client.ping()` for connection validation).

**Rule:** Understand why tools flag issues. Fix when reasonable, document when not.

### Lesson 6: AsyncIO CancelledError Must Be Re-Raised

**Pattern:**
```python
try:
    await some_operation()
except asyncio.CancelledError:
    raise  # Always re-raise unless you're the cleanup handler
except Exception:
    logging.exception("...")
```

**Exception:** In cleanup methods like `stop()`, you ARE the cancellation handler, so suppression is correct.

### Lesson 7: Small, Frequent Releases Build Confidence

**Context:** 7 releases in one session, each with one clear improvement.

**Result:** Each release was a checkpoint, reducing risk.

**Rule:** Release early, release often. Each release should have a clear purpose.

### Lesson 8: False CHANGELOG Claims Destroy Trust

**Context:** v0.2.0 claimed "21 tests" when zero existed.

**Rule:** Always verify claims. Run tests, count output, use actual numbers.

### Lesson 9: Editable Install for Development

**Pattern:**
```bash
pip install -e .
```

**Why:** Enables accurate coverage measurement and immediate feedback during development.

**Rule:** Always use editable install during development.

### Lesson 10: Quality is a Choice, Not a Circumstance

**Context:** Project went from broken (0% coverage) to best-in-class (90% coverage, 52% docs, 0 defects) in one session.

**Proof:** Excellence is achievable through systematic pursuit of quality.

**Rule:** Choose excellence. Use tools to enforce standards. Iterate rapidly.

---

## Troubleshooting Guide

### Tests Failing

**Problem:** Tests fail after changes

**Debug Steps:**
```bash
# 1. Run specific failing test with verbose output
pytest tests/test_file.py::TestClass::test_name -v

# 2. Check for async issues
pytest tests/ --log-cli-level=DEBUG

# 3. Verify fixtures are correct
# Check conftest.py for fixture definitions

# 4. Check mocking
# Ensure patch target is import location, not definition
```

**Common Causes:**
- AsyncMock not used for async functions
- Patching wrong location (use import location)
- Fixtures not properly cleaned up
- Real tasks needed instead of mocks for cancellation

### Coverage Dropping

**Problem:** Coverage falls below 85%

**Debug Steps:**
```bash
# 1. Generate detailed coverage report
pytest tests/ --cov --cov-report=html
open htmlcov/index.html

# 2. Find uncovered lines
pytest tests/ --cov --cov-report=term-missing

# 3. Add tests for uncovered code
vim tests/test_missing_coverage.py
```

**Common Causes:**
- New code added without tests
- Exception handlers not tested
- Edge cases missing

### SonarCloud Quality Gate Failing

**Problem:** Quality Gate fails on push

**Debug Steps:**
1. Check SonarCloud dashboard
2. Review new code metrics (not overall)
3. Check for:
   - New bugs
   - New code smells
   - Coverage of new code < 80%
   - Security hotspots

**Common Fixes:**
- Add tests for new code
- Refactor complex functions (complexity > 15)
- Fix bugs identified
- Document intentional design decisions

### Redis Connection Issues

**Problem:** Tests fail with Redis connection errors

**Solution:** Tests use mocks - shouldn't connect to real Redis.

**Check:**
```python
# Verify mocking
with patch('beast_mailbox_core.redis_mailbox.redis.Redis', return_value=mock_client):
    # Your test code
```

### Package Build Failing

**Problem:** `python -m build` fails

**Debug Steps:**
```bash
# 1. Check pyproject.toml syntax
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"

# 2. Verify all source files exist
ls -la src/beast_mailbox_core/

# 3. Clean and retry
rm -rf dist/ build/ *.egg-info
python -m build
```

---

## Quick Reference

### Essential Commands

```bash
# Development
pip install -e ".[dev]"           # Install for development
pytest tests/                     # Run all tests
pytest tests/ --cov              # Run with coverage
python -m build                  # Build package

# Release
git tag -a v0.X.Y -m "Release"   # Create tag
twine upload dist/*              # Upload to PyPI

# Quality
pytest tests/ --cov-report=html  # Generate coverage HTML
# Visit SonarCloud for quality metrics

# Redis operations (manual testing)
redis-cli XLEN beast:mailbox:test:in
redis-cli XREVRANGE beast:mailbox:test:in + - COUNT 5
```

### Key Metrics to Monitor

| Metric | Target | Command |
|--------|--------|---------|
| Tests | ≥ Complexity | `pytest tests/ -v \| grep "passed"` |
| Coverage | ≥ 85% | `pytest tests/ --cov` |
| Quality Gate | PASSED | Visit SonarCloud |
| Bugs | 0 | Visit SonarCloud |

### Important URLs

- **GitHub:** https://github.com/nkllon/beast-mailbox-core
- **PyPI:** https://pypi.org/project/beast-mailbox-core/
- **SonarCloud:** https://sonarcloud.io/project/overview?id=nkllon_beast-mailbox-core

### Key Files to Remember

| File | Purpose |
|------|---------|
| `pyproject.toml` | Package metadata, version, dependencies |
| `CHANGELOG.md` | Release notes (update before release) |
| `README.md` | User documentation |
| `steering/release-procedure-CORRECTED.md` | Release checklist |
| `docs/LESSONS_LEARNED_v0.3.0.md` | Historical context |
| `AGENT.md` (this file) | Maintainer guide |

### Contact & Escalation

**For Issues:**
1. Check this guide
2. Review `docs/LESSONS_LEARNED_v0.3.0.md`
3. Check GitHub Issues
4. Review previous PR discussions
5. Consult user (if critical decision needed)

---

## Maintenance Philosophy

### Core Principles

1. **Quality First:** Never compromise on quality for speed
2. **Test Everything:** If it's testable, it must be tested
3. **Document Thoroughly:** Explain why, not just what
4. **Release Carefully:** Follow the checklist, every time
5. **Learn Continuously:** Update this guide with new lessons
6. **User Focus:** Users depend on this library - respect that trust

### Decision Framework

**When making decisions:**

1. **Will this break existing users?**
   - If yes, needs major version bump (semantic versioning)
   - Add deprecation warnings before breaking changes

2. **Does this maintain quality standards?**
   - Check tests, coverage, documentation
   - Run SonarCloud scan

3. **Is this well-documented?**
   - Update README, docstrings, CHANGELOG
   - Include examples

4. **Can this be tested?**
   - If yes, write tests
   - If no, document why

5. **Does this align with project goals?**
   - Inter-agent messaging via Redis
   - Simple, reliable, well-documented

---

## Version History Summary

| Version | Date | Key Achievement |
|---------|------|-----------------|
| 0.1.0 | Initial | Basic functionality |
| 0.2.0 | 2025-10-10 | Added `--ack` and `--trim` (sync crisis) |
| 0.2.1-0.2.5 | 2025-10-10 | Quality improvements, testing |
| 0.3.0 | 2025-10-10 | Excellence Edition (52% docs, 52 tests) |
| 0.3.1 | 2025-10-10 | 90% Coverage Milestone (59 tests) |

---

## Final Notes

### What Makes This Project Special

1. **Built by AI, for AI:** Entire codebase designed and implemented by LLMs
2. **Best-in-Class Quality:** Exceeds industry standards in every metric
3. **Comprehensive Documentation:** 52% comment density (208% of standard)
4. **Battle-Tested:** Recovered from critical crisis, now rock-solid
5. **Living Example:** Demonstrates what's possible with AI development

### Your Responsibility

As maintainer, you are responsible for:
- Preserving quality standards (don't let them slip!)
- Following release procedures (protect users!)
- Maintaining documentation (help future maintainers!)
- Learning from issues (update this guide!)
- Being responsive to users (they depend on this!)

### Continuous Improvement

This guide should evolve. When you learn something new:

1. Update this file
2. Commit with clear message: `docs: update AGENT.md with lesson about X`
3. Consider if other docs need updating too

### Success Metrics

You're succeeding as maintainer if:
- ✅ All quality metrics remain in "excellent" range
- ✅ Users report satisfaction (few issues, quick resolutions)
- ✅ No release incidents (no sync failures, no breaking changes)
- ✅ Documentation stays current
- ✅ Test suite grows with codebase
- ✅ This guide stays accurate and helpful

---

## Welcome Aboard! 🚀

You're now equipped to maintain Beast Mailbox Core with confidence. This project has come a long way from its crisis to excellence. Your job is to keep it excellent and make it even better.

**Remember:**
- Quality is non-negotiable
- Tests are your safety net
- Documentation is for future you
- Users trust this library
- Excellence is a choice

Good luck, and may your coverage always be ≥ 85%! 📊✨

---

**Last Updated:** 2025-10-13  
**Maintained By:** AI Agent (You)  
**Previous Maintainer:** Herbert (AI Agent)  
**Document Version:** 1.0.0

**Questions?** Check `docs/LESSONS_LEARNED_v0.3.0.md` for 80+ specific lessons learned.


# Request: Add REDIS_URL Environment Variable Support

## Context

**beast-mailbox-core** is an enterprise-grade Redis-backed mailbox utility for Beast Mode agents. It currently requires CLI flags for Redis connection configuration (`--redis-host`, `--redis-password`, `--redis-port`, `--redis-db`).

**Problem:** This doesn't integrate cleanly with the broader OpenFlow Playground ecosystem, which uses `REDIS_URL` environment variable (format: `redis://:password@host:port/db`).

## Stakeholder Requirement

**"It should just install and work."**

When beast-mailbox-core is used alongside other OpenFlow components, it should automatically read Redis connection details from the `REDIS_URL` environment variable without requiring CLI flags.

## What We Need

### 1. Environment Variable Support
Add support for `REDIS_URL` environment variable:
- Format: `redis://:password@host:port/db` or `redis://user:password@host:port/db`
- Should parse the URL and extract: host, port, password, db
- **Falls back to CLI flags if REDIS_URL not set** (backward compatibility)

### 2. Priority Order
```
1. CLI flags (highest priority - explicit override)
2. REDIS_URL environment variable (convenient default)
3. Hardcoded defaults (localhost:6379)
```

### 3. Implementation Locations
- **File**: `src/beast_mailbox_core/cli.py` (or wherever CLI arg parsing happens)
- **Function**: Parse `REDIS_URL` before falling back to defaults
- **Library**: Use `urllib.parse.urlparse()` for URL parsing

### 4. Example Usage

**Before (current):**
```bash
beast-mailbox-service herbert \
  --redis-host Vonnegut.local \
  --redis-password beastmaster2025
```

**After (desired):**
```bash
# With REDIS_URL set
export REDIS_URL="redis://:beastmaster2025@Vonnegut.local:6379"
beast-mailbox-service herbert  # Just works!

# CLI flags still work (override environment)
beast-mailbox-service herbert --redis-host other.host --redis-password other_pass
```

### 5. Testing Requirements
- ✅ Test with REDIS_URL set
- ✅ Test with CLI flags override
- ✅ Test with both (CLI wins)
- ✅ Test with neither (defaults to localhost)
- ✅ Test invalid REDIS_URL (proper error message)
- ✅ All existing tests must pass

### 6. Documentation Updates
- Update README.md with REDIS_URL examples
- Document priority order
- Add troubleshooting for REDIS_URL parsing errors
- Update CLI help text to mention REDIS_URL

## Constraints

- **NO breaking changes** - CLI flags must continue to work
- **Backward compatible** - Existing usage patterns unchanged
- **Enterprise quality** - Maintain 90% coverage, ZERO defects
- **Follow existing patterns** - Match the code style and architecture

## Requested Output

### Branch Name
`feature/redis-url-env-support`

### PR Title
`feat: Add REDIS_URL environment variable support`

### PR Description Template
```markdown
## Summary
Adds support for `REDIS_URL` environment variable to simplify Redis configuration and integrate seamlessly with OpenFlow Playground ecosystem.

## Changes
- Parse `REDIS_URL` environment variable for connection details
- Maintain backward compatibility with CLI flags
- CLI flags override environment variable
- Added tests for all scenarios
- Updated documentation

## Testing
- ✅ All existing tests pass
- ✅ New tests for REDIS_URL parsing
- ✅ Integration tests with environment variable
- ✅ CLI override tests

## Breaking Changes
None - fully backward compatible

## Documentation
- Updated README with REDIS_URL examples
- Updated CLI help text
- Added troubleshooting section
```

## Response Delivery Instructions (PR-Based)

**CRITICAL**: You are stateless and security-constrained. Follow these EXACT instructions:

### Repository Information
- **Repository**: nkllon/beast-mailbox-core
- **Target Branch**: main
- **Your Agent ID**: cursor-llm-2

### Step 1: Create Branch
- **Exact branch name**: feature/redis-url-env-support

### Step 2: Implement Changes
- Parse `REDIS_URL` in CLI arg handling
- Test comprehensively
- Update documentation
- Ensure all quality gates pass

### Step 3: Create Pull Request
- **Exact PR title**: feat: Add REDIS_URL environment variable support
- **Target branch**: main
- **Repository**: nkllon/beast-mailbox-core
- Include comprehensive description with testing results

### Quality Gates (MUST PASS)
- ✅ All 59+ tests passing
- ✅ 90%+ coverage maintained
- ✅ Black formatting
- ✅ No linter errors
- ✅ ZERO defects

### If You Get Lost
- Re-read this entire prompt (you are stateless)
- All required information is in THIS document
- Repository: nkllon/beast-mailbox-core
- Branch: feature/redis-url-env-support

---

**For AI Maintainers**: See `AGENT.md` and `docs/LESSONS_LEARNED_v0.3.0.md` for critical context about maintaining this enterprise-grade package.


# Documentation Scope - beast-mailbox-core

**Purpose:** This document clarifies what this repository documents and how it relates to other Beast Mode packages.

## Documentation Ownership

### beast-mailbox-core (This Repository)

**Documents:**
- ✅ `RedisMailboxService` API and usage
- ✅ `MailboxConfig` API and configuration
- ✅ `MailboxMessage` data model
- ✅ CLI tools (`beast-mailbox-service`, `beast-mailbox-send`)
- ✅ Integration patterns using `beast-mailbox-core` directly
- ✅ **Integration examples** showing how `beast-mailbox-core` is used by other packages (e.g., `beast-agent`)

### beast-agent (Separate Repository)

**Should Document:**
- `BaseAgent` class API
- `BaseAgent` lifecycle methods (`on_startup`, `on_shutdown`)
- `BaseAgent` message handling patterns
- Agent registration and discovery APIs
- Agent-specific features and capabilities

## Documentation Files in beast-mailbox-core

### Core Documentation (Always Managed Here)

- `README.md` - Project overview, installation, quick start
- `docs/API.md` - Complete API reference for `beast-mailbox-core`
- `docs/USAGE_GUIDE.md` - Usage patterns for `beast-mailbox-core`
- `docs/QUICK_REFERENCE.md` - CLI command reference
- `AGENT.md` - Maintainer guide for AI agents

### Integration Documentation (May Overlap)

- `docs/USING_BEAST_AGENT.md` - **Integration guide** showing how to use `beast-agent` with `beast-mailbox-core`
- `docs/CLUSTER_DISCOVERY.md` - **Integration guide** for cluster discovery using `beast-mailbox-core` features
- `docs/SONARCLOUD_INTEGRATION_GUIDE.md` - Best practices guide

## Scope Boundaries

### What We Document (beast-mailbox-core)

✅ **`MailboxConfig` usage:**
- How to create `MailboxConfig` objects
- How `MailboxConfig` works with authentication
- Examples showing `MailboxConfig` with `beast-agent` (as integration example)

✅ **Integration patterns:**
- How `beast-mailbox-core` is used by `beast-agent`
- How to use `MailboxConfig` with `BaseAgent(mailbox_url=config)`
- Examples of authenticated connections

✅ **Cross-package examples:**
- Examples showing `beast-agent` using `beast-mailbox-core` features
- Discovery patterns using Redis keys that `beast-mailbox-core` creates

### What We DON'T Document (beast-agent's Responsibility)

❌ **`BaseAgent` API details:**
- BaseAgent constructor parameters (beyond `mailbox_url`)
- BaseAgent lifecycle methods
- BaseAgent message handling internals
- BaseAgent-specific features

❌ **Agent registration internals:**
- How `BaseAgent` implements registration
- Agent registration API details
- Agent discovery implementation details

## Potential Conflicts

### Risk Areas

1. **API Documentation:**
   - If `BaseAgent` API changes, our examples may become outdated
   - We show `BaseAgent.__init__()` parameters but don't own that API

2. **Version Mismatches:**
   - We reference `beast-agent==0.1.3` but may become outdated
   - If beast-agent changes, our examples may break

3. **Duplicate Content:**
   - We may duplicate beast-agent's README content
   - Our integration guide may overlap with beast-agent's usage docs

### Mitigation Strategy

1. **Clear Scope Labeling:**
   - All beast-agent integration docs labeled as "integration examples"
   - Clear references to beast-agent's own documentation

2. **Version Pinning:**
   - Pin beast-agent versions in examples
   - Note version compatibility in integration guides

3. **Link to Source:**
   - Always link to beast-agent repository for authoritative API docs
   - Note that beast-agent's docs are authoritative for BaseAgent API

4. **Focus on Integration:**
   - Focus on how beast-mailbox-core FEATURES are used, not beast-agent API
   - Examples show MailboxConfig usage, not BaseAgent internals

## Current Status

### Files That May Need Coordination

- `docs/USING_BEAST_AGENT.md` - Integration guide
  - **Scope:** Shows MailboxConfig usage with beast-agent
  - **Risk:** May duplicate beast-agent README
  - **Action:** Should verify alignment with beast-agent docs

- `docs/CLUSTER_DISCOVERY.md` - Cluster discovery
  - **Scope:** Shows Redis keys and discovery patterns
  - **Risk:** May document beast-agent internals
  - **Action:** Should focus on Redis patterns, not BaseAgent internals

- `docs/API.md` - API reference
  - **Contains:** MailboxConfig examples with beast-agent
  - **Risk:** Shows BaseAgent usage but doesn't own that API
  - **Action:** Add note that BaseAgent API is documented in beast-agent repo

## Recommendations

1. **Coordinate with beast-agent:**
   - Verify examples match beast-agent's actual API
   - Ensure we don't document beast-agent internals
   - Link to beast-agent's authoritative docs

2. **Add Disclaimers:**
   - Note that beast-agent API is documented in beast-agent repo
   - Our docs are integration examples, not API reference
   - Our docs focus on beast-mailbox-core features used by beast-agent

3. **Version Management:**
   - Pin beast-agent versions in examples
   - Test examples against actual beast-agent releases
   - Update version references when beast-agent releases

4. **Scope Clarification:**
   - Add header to integration docs: "This shows how beast-mailbox-core is used with beast-agent. For BaseAgent API details, see beast-agent documentation."
   - Focus on MailboxConfig, not BaseAgent internals
   - Link to beast-agent repo for authoritative BaseAgent docs


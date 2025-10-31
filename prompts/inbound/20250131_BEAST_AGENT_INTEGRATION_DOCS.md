# Request to beast-agent: Integration Documentation Requirements

**From**: beast-mailbox-core maintainer  
**To**: beast-agent maintainers  
**Date**: 2025-01-31  
**Priority**: High - Blocks adoption

---

## Requirement: Integration Documentation

Users need documentation showing how to use `beast-agent` with `beast-mailbox-core`, especially for authenticated Redis connections and cluster discovery.

---

## What's Needed

### 1. Authentication Documentation (CRITICAL)

**Problem:** Users cannot figure out how to authenticate to Redis when using `beast-agent`. They need to know:

- How to pass `MailboxConfig` to `BaseAgent(mailbox_url=config)`
- That `mailbox_url` accepts `MailboxConfig` objects, not just URL strings
- Complete working examples of authenticated agents

**Important:** The code already supports `MailboxConfig` objects - this is a documentation gap, not a feature gap. Users just don't know this capability exists.

**Current Gap:**
- No examples showing authenticated Redis connections
- No mention that `mailbox_url` accepts `MailboxConfig` objects
- Users have to reverse-engineer from source code

**What Should Be Documented:**
```python
from beast_agent import BaseAgent
from beast_mailbox_core.redis_mailbox import MailboxConfig

class MyAgent(BaseAgent):
    def __init__(self):
        # Create MailboxConfig with password
        mailbox_config = MailboxConfig(
            host="192.168.1.119",
            port=6379,
            password="beastmode2025",
            db=0
        )
        
        super().__init__(
            agent_id="my-agent",
            capabilities=["my-cap"],
            mailbox_url=mailbox_config  # Pass MailboxConfig object
        )
```

### 2. Cluster Discovery Documentation

**Problem:** Users need to know how to:
- Discover other agents on the cluster
- Read agent metadata and capabilities
- Send messages to discovered agents

**What Should Be Documented:**
- Redis keys used by the cluster (`beast:agents:all`, `beast:agents:{agent_id}`)
- How to query active agents
- Examples of agent discovery patterns

### 3. Version Requirements Documentation

**Critical:** Users need to know:
- **v0.1.3+ required for live-fire testing** - Agent registration and discovery methods
- Without v0.1.3, agents won't appear on cluster
- Without v0.1.3, discovery methods won't work

**What to Document:**
- Upgrade requirement: `pip install beast-agent==0.1.3` (or latest)
- What features are in v0.1.3 vs earlier versions:
  - ✅ Agent registration (v0.1.0+) - Agents appear on cluster
  - ✅ Discovery methods (v0.1.3+) - Can find other agents
  - ✅ MailboxConfig support (existing, undocumented)
- Clear upgrade path and migration notes

### 4. Complete Examples

**Need:**
- Authenticated agent example (complete, working code)
- Agent discovery example (v0.1.3+)
- Multi-agent communication examples
- Environment variable configuration examples
- Version-specific feature examples (what works in which version)

---

## What Already Exists (temporary)

**Location:** `beast-mailbox-core/docs/USING_BEAST_AGENT.md` and `docs/CLUSTER_DISCOVERY.md`

**Status:** These are temporary integration examples I created because they were needed, but **you own this documentation**. They should be:
- Replaced by authoritative docs in `beast-agent` repository
- Used as reference material
- Deprecated once you publish your integration docs

**Content:**
- Shows `MailboxConfig` usage with `BaseAgent`
- Shows authenticated connection patterns
- Shows cluster discovery patterns

---

## Success Criteria

- [ ] `beast-agent` README includes authentication section
- [ ] `beast-agent` README shows `MailboxConfig` usage with `BaseAgent`
- [ ] `beast-agent` examples include authenticated agent example
- [ ] `beast-agent` docs include cluster discovery guide
- [ ] Version requirements clearly documented (v0.1.3+ for discovery)
- [ ] Upgrade instructions for live-fire testing
- [ ] Feature version matrix (what's in which version)
- [ ] All examples are tested and working
- [ ] Version numbers match actual releases

---

## Why This Matters

**Without this documentation:**
- ❌ Users cannot use beast-agent with authenticated Redis (99% of production clusters)
- ❌ Users don't know they need v0.1.3 for live-fire testing
- ❌ Users miss agent registration and discovery features
- ❌ Users spend 20+ minutes trial-and-error
- ❌ Users have to read source code to figure it out
- ❌ Blocks adoption for production use cases

**With this documentation:**
- ✅ Works in 30 seconds
- ✅ Clear path for production deployments
- ✅ Shows beast-agent is production-ready

---

## Reference Material

I've created temporary docs in `beast-mailbox-core` that you can reference:

- **`docs/USING_BEAST_AGENT.md`** - Integration guide showing `MailboxConfig` usage
- **`docs/CLUSTER_DISCOVERY.md`** - Cluster discovery patterns
- **`docs/API.md`** - Has `MailboxConfig` examples with beast-agent usage

**Note:** These are marked as integration examples from `beast-mailbox-core`'s perspective. You should create authoritative documentation in the `beast-agent` repository.

---

## Next Steps

1. Review the temporary docs in `beast-mailbox-core` (reference only)
2. Create/update `beast-agent` documentation with:
   - **Authentication section in README** (MailboxConfig usage - code already supports it!)
   - **Version requirements section** (v0.1.3+ for discovery, v0.1.0+ for registration)
   - Complete authenticated agent example
   - Cluster discovery guide (v0.1.3+ features)
   - Clear API documentation for `BaseAgent.__init__()` including `mailbox_url` parameter types
   - Feature version matrix showing what's available in which version
3. Test all examples against current `beast-agent` releases
4. Publish updated docs
5. I'll update `beast-mailbox-core` docs to link to your authoritative docs

---

**Priority**: High - This blocks production adoption and users are currently reverse-engineering from source code.


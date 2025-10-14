# Requirements: GitHub Token Automation

**Spec ID:** 001  
**Status:** Draft  
**Created:** 2025-10-14  
**Owner:** AI Agent Maintainer  
**Priority:** High (Security & Operations)

---

## Problem Statement

### The GitHub Security Paradox

GitHub provides **fine-grained Personal Access Tokens** as a "more secure" alternative to classic tokens, but they can **only be created and configured through a manual web UI**. This presents a critical security and operations challenge:

**What GitHub Requires:**
- Manual web browser navigation
- Point-and-click configuration across multiple screens
- Per-repository permission selection
- Manual token copying and storage
- No automation, no API, no repeatability

**What Security Operations Requires:**
- Auditable changes (version-controlled configurations)
- Repeatable processes (infrastructure-as-code)
- Automated rotation (scheduled, tested)
- Least-privilege automation (no human "Bob knows how to click")
- Documented procedures (not tribal knowledge)

### The Absurdity

As a CSOC professional, the recommended solution is to **use Selenium/Playwright to automate the web UI**, because a scripted, version-controlled browser automation is **more secure and auditable** than "manually click through the UI and hope you remember what you did."

**This requirement exists because GitHub's security model is broken for enterprise operations.**

---

## Current State

### What Works Today (Classic Tokens)

```bash
# Classic tokens (ghp_...) work immediately
# 1. Generate at https://github.com/settings/tokens/new
# 2. Check "repo" scope
# 3. Use it
gh auth login --with-token <<< "ghp_..."
```

**Pros:**
- Simple, immediate access
- Work for all repos (including org repos)
- Industry standard for CLI automation
- Fully supported (not deprecated)

**Cons:**
- Broad permissions (entire "repo" scope)
- No per-repository granularity

### What Doesn't Work (Fine-Grained Tokens)

```bash
# Fine-grained tokens (github_pat_...) require:
# 1. Web UI configuration
# 2. Repository selection (per-repo grants)
# 3. Detailed permission configuration (Issues: R/W, Contents: R/W, etc.)
# 4. Organization admin approval (for org repos)
# 5. Token regeneration after permission changes
```

**Pros:**
- Granular per-repository permissions
- Detailed permission scopes
- Better security model (in theory)

**Cons:**
- ❌ **NO API for creation or management**
- ❌ Manual web UI only
- ❌ Requires org admin approval (even if you're the admin)
- ❌ Tedious configuration process
- ❌ Not auditable or repeatable
- ❌ Cannot be automated with IaC tools

---

## Requirements

### REQ-001: Automated Token Provisioning

**Requirement:** Create a repeatable, auditable process for provisioning GitHub Personal Access Tokens with specified permissions.

**Acceptance Criteria:**
- ✅ Process is defined in version-controlled code
- ✅ Process can be executed by any authorized operator
- ✅ Process generates audit logs of actions taken
- ✅ Process is testable in non-production environment
- ✅ Process documentation is self-contained

**Priority:** P0 (Critical)

### REQ-002: Security & Auditability

**Requirement:** Token provisioning must meet enterprise security standards.

**Acceptance Criteria:**
- ✅ All actions are logged
- ✅ Configuration is stored in version control
- ✅ Changes require code review (PR process)
- ✅ Secrets are never committed to repository
- ✅ Process follows principle of least privilege

**Priority:** P0 (Critical)

### REQ-003: Repeatability & Documentation

**Requirement:** Process must be reproducible by any team member or AI agent.

**Acceptance Criteria:**
- ✅ Complete setup instructions documented
- ✅ All dependencies specified
- ✅ Error handling documented
- ✅ Recovery procedures documented
- ✅ Can be run in CI/CD pipeline (future)

**Priority:** P0 (Critical)

### REQ-004: Token Storage & Rotation

**Requirement:** Securely store and manage token lifecycle.

**Acceptance Criteria:**
- ✅ Tokens stored in `~/.env` (gitignored)
- ✅ Tokens set as GitHub repository secrets via API
- ✅ Token expiration tracked
- ✅ Rotation process defined (recommended: 90 days)
- ✅ Old tokens revoked after rotation

**Priority:** P1 (High)

### REQ-005: Support Multiple Token Types

**Requirement:** Support both classic and fine-grained token workflows.

**Acceptance Criteria:**
- ✅ Classic token workflow (simple, immediate)
- ✅ Fine-grained token workflow (complex, automated)
- ✅ Documentation clearly explains trade-offs
- ✅ Recommendation provided based on use case

**Priority:** P2 (Medium)

---

## Constraints

### Technical Constraints

1. **GitHub API Limitation**
   - No API endpoint for fine-grained token creation
   - Must use web automation (Selenium/Playwright)

2. **Authentication Requirements**
   - Must handle GitHub 2FA/passkeys
   - Must support different auth flows

3. **Browser Automation**
   - Must run headless for CI/CD
   - Must support headed mode for debugging
   - Must handle dynamic page elements

### Operational Constraints

1. **Environment**
   - Must work on macOS, Linux, Windows
   - Must not require GUI display for automation
   - Must work in Docker containers (future)

2. **Dependencies**
   - Minimize external dependencies
   - Document all required packages
   - Pin versions for repeatability

### Security Constraints

1. **Credentials**
   - Never log credentials
   - Never commit credentials
   - Use environment variables
   - Support secrets managers (future)

2. **Least Privilege**
   - Request minimum necessary permissions
   - Document why each permission is needed
   - Support permission verification

---

## Success Criteria

### Minimum Viable Solution

1. ✅ Script exists in `/scripts/provision-github-token.py`
2. ✅ Script documented in `/docs/TOKEN_AUTOMATION.md`
3. ✅ Script can provision classic tokens (immediate win)
4. ✅ Script can provision fine-grained tokens (via Selenium)
5. ✅ All actions logged to file
6. ✅ Process tested on macOS (primary development environment)

### Long-Term Success

1. ✅ Used in production for 90+ days without incident
2. ✅ Successfully rotated tokens using automation
3. ✅ New team members can provision tokens using docs
4. ✅ Process included in onboarding documentation
5. ✅ Zero manual token configuration required

---

## Non-Requirements

### Out of Scope

1. ❌ Creating a GitHub App (different use case, more complex)
2. ❌ Managing SSH keys (separate concern)
3. ❌ Managing other GitHub secrets (focused on PATs only)
4. ❌ Multi-factor authentication bypass (must respect 2FA)
5. ❌ Token sharing between team members (each gets their own)

---

## Dependencies

### For Implementation

1. **Python 3.9+** - Scripting language
2. **Playwright or Selenium** - Browser automation
3. **GitHub CLI (`gh`)** - Token verification and secret management
4. **Python packages:**
   - `playwright` or `selenium`
   - `python-dotenv` (for .env management)
   - `pyyaml` (for config files)

### For Documentation

1. **Markdown** - Specification format
2. **Diagrams** - Flow diagrams (optional)
3. **Screenshots** - Setup guides (optional)

---

## Risk Assessment

### High Risk

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| GitHub changes UI | High | Medium | Regular testing, version pinning |
| Credentials leaked | Critical | Low | Never log/commit, use env vars |
| Token misconfiguration | Medium | Medium | Validation step, permission verification |

### Medium Risk

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| Browser automation breaks | Medium | Medium | Error handling, manual fallback docs |
| 2FA issues | Medium | Medium | Support multiple auth methods |
| CI/CD integration fails | Medium | Low | Document limitations, test locally first |

### Low Risk

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| Script complexity | Low | High | Good documentation, simple design |
| Maintenance burden | Low | Medium | Clear ownership, regular review |

---

## Related Documents

- **Design Spec:** `./design.md` (to be created)
- **Implementation Guide:** `/docs/TOKEN_AUTOMATION.md` (to be created)
- **AGENT.md:** `/AGENT.md` (updated with lessons learned)
- **Security Policy:** (to be created if needed)

---

## Approval Status

- [ ] **Security Review** - Pending
- [ ] **Architecture Review** - Pending
- [ ] **User Acceptance** - Pending
- [ ] **Implementation Complete** - Pending

---

## Change Log

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2025-10-14 | 0.1.0 | Initial requirements | AI Agent |

---

## Notes

### Why This Requirement Exists

This requirement exists because:

1. **GitHub's security model is broken** for enterprise operations
2. **Web UI-only configuration is not secure** - it's not auditable, repeatable, or testable
3. **The CSOC perspective is correct** - automated web UI is more secure than manual clicks
4. **Requirements ARE the solution** - documenting the requirement enables any LLM to implement it

### Philosophy

> "If the only interface is a web UI, then the secure solution is to automate that web UI."
> 
> — CSOC Beast Mode

The mere existence of this specification document makes the solution possible. Any competent LLM can read these requirements and implement a working solution. **Requirements are executable documentation.**

---

**End of Requirements Specification**


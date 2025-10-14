# Design: GitHub Token Automation

**Spec ID:** 001  
**Status:** Draft  
**Created:** 2025-10-14  
**Related:** `requirements.md`

---

## Design Overview

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User / CI/CD                          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│         scripts/provision-github-token.py                │
│                                                          │
│  ┌────────────────────────────────────────────┐        │
│  │  1. Read Configuration                      │        │
│  │     - Token type (classic/fine-grained)    │        │
│  │     - Required permissions                 │        │
│  │     - Repository scope                     │        │
│  └────────────────────────────────────────────┘        │
│                     │                                    │
│                     ▼                                    │
│  ┌────────────────────────────────────────────┐        │
│  │  2. Execute Automation                      │        │
│  │     - Launch browser (Playwright)           │        │
│  │     - Navigate to GitHub                   │        │
│  │     - Handle authentication                │        │
│  │     - Configure permissions                │        │
│  │     - Extract token                        │        │
│  └────────────────────────────────────────────┘        │
│                     │                                    │
│                     ▼                                    │
│  ┌────────────────────────────────────────────┐        │
│  │  3. Store & Distribute                      │        │
│  │     - Save to ~/.env                       │        │
│  │     - Set GitHub secret (via gh CLI)       │        │
│  │     - Log actions taken                    │        │
│  │     - Generate audit report                │        │
│  └────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Outputs & Artifacts                         │
│                                                          │
│  - ~/.env (GITHUB_TOKEN=ghp_...)                       │
│  - GitHub Secrets (via API)                            │
│  - Audit log (.spec-workflow/logs/token-YYYYMMDD.log) │
└─────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Configuration (`config.yaml`)

**Location:** `.spec-workflow/specs/001-github-token-automation/config.yaml`

```yaml
token_type: "classic"  # or "fine-grained"

classic_token:
  scopes:
    - repo
    - workflow
  expiration: 90  # days

fine_grained_token:
  repositories:
    - nkllon/beast-mailbox-core
  permissions:
    contents: "read-write"
    issues: "read-write"
    pull_requests: "read-write"
    workflows: "read-write"
    secrets: "read-write"
  expiration: 90  # days

output:
  env_file: "~/.env"
  github_secret: true
  audit_log: ".spec-workflow/logs/token-{timestamp}.log"
```

### 2. Automation Script (`scripts/provision-github-token.py`)

**Core Responsibilities:**
- Read configuration
- Launch browser automation
- Handle GitHub auth flow
- Configure token permissions
- Extract and store token
- Update GitHub secrets
- Generate audit log

**Key Functions:**

```python
def main(config_path: str, mode: str = "headless"):
    """Main entry point for token provisioning."""
    
def provision_classic_token(config: dict, browser) -> str:
    """Automate classic token creation."""
    
def provision_fine_grained_token(config: dict, browser) -> str:
    """Automate fine-grained token creation."""
    
def store_token(token: str, config: dict):
    """Store token in env and GitHub secrets."""
    
def audit_log(action: str, details: dict):
    """Log all actions for audit trail."""
```

### 3. Browser Automation (Playwright)

**Why Playwright over Selenium:**
- Modern, maintained actively
- Better async support
- Built-in waits and retry logic
- Easier headless configuration
- Better screenshots/debugging

**Key Pages to Automate:**

1. **Authentication** - `https://github.com/login`
2. **Classic Tokens** - `https://github.com/settings/tokens/new`
3. **Fine-Grained Tokens** - `https://github.com/settings/personal-access-tokens/new`

**Selectors (as of 2025-10-14):**

```python
SELECTORS = {
    "login": {
        "username": 'input[name="login"]',
        "password": 'input[name="password"]',
        "submit": 'input[type="submit"]',
    },
    "classic_token": {
        "note": 'input[name="oauth_access_description"]',
        "expiration": 'select[name="oauth_access[expires_at]"]',
        "scope_repo": 'input[name="oauth_access[scopes][]"][value="repo"]',
        "scope_workflow": 'input[name="oauth_access[scopes][]"][value="workflow"]',
        "generate": 'button[type="submit"]',
        "token_display": 'input[id="oauth-token"]',
    },
    "fine_grained_token": {
        "name": 'input[name="token[name]"]',
        "expiration": 'select[name="token[expires_at]"]',
        "repository_access": '...',  # Complex, need inspection
        "permissions": '...',         # Complex, need inspection
        "generate": 'button[type="submit"]',
        "token_display": '...',       # Complex, need inspection
    }
}
```

**Note:** Selectors WILL change - design must handle updates.

---

## Implementation Phases

### Phase 1: Classic Token Automation (MVP)

**Goal:** Get working automation for classic tokens (simpler flow)

**Tasks:**
1. Create config schema
2. Implement browser automation for classic tokens
3. Implement token storage (env + GitHub secrets)
4. Implement audit logging
5. Test on macOS
6. Document usage

**Deliverables:**
- ✅ Working script for classic tokens
- ✅ Configuration file
- ✅ Basic documentation

**Success Criteria:**
- Can provision classic token non-interactively
- Token works with gh CLI
- Token stored securely
- Actions logged

### Phase 2: Fine-Grained Token Automation

**Goal:** Extend to fine-grained tokens (complex flow)

**Tasks:**
1. Map fine-grained token UI flow
2. Implement permission selection automation
3. Handle organization approval flow
4. Test on nkllon/beast-mailbox-core
5. Document edge cases

**Deliverables:**
- ✅ Fine-grained token support
- ✅ Repository selection automation
- ✅ Permission configuration automation

**Success Criteria:**
- Can provision fine-grained token
- Permissions correctly set
- Works for organization repos

### Phase 3: Robustness & Error Handling

**Goal:** Production-ready quality

**Tasks:**
1. Add comprehensive error handling
2. Add retry logic for flaky selectors
3. Add 2FA support detection
4. Add manual fallback documentation
5. Add token verification
6. Add health checks

**Deliverables:**
- ✅ Robust error handling
- ✅ Clear error messages
- ✅ Recovery documentation

**Success Criteria:**
- Handles common failures gracefully
- Provides actionable error messages
- Can recover from partial failures

### Phase 4: CI/CD Integration

**Goal:** Run in automated pipelines

**Tasks:**
1. Docker container support
2. Headless mode validation
3. CI/CD examples (GitHub Actions)
4. Secret management integration
5. Token rotation automation

**Deliverables:**
- ✅ Dockerfile
- ✅ CI/CD workflow examples
- ✅ Automated rotation

**Success Criteria:**
- Runs in GitHub Actions
- Can rotate tokens automatically
- Zero manual intervention

---

## Technology Choices

### Browser Automation: Playwright

**Why:**
- Modern, actively maintained
- Better async/await support
- Built-in auto-waiting
- Excellent documentation
- Cross-platform support

**Installation:**
```bash
pip install playwright
playwright install chromium
```

### Configuration: YAML

**Why:**
- Human-readable
- Comments supported
- Industry standard
- Python library (PyYAML)

### Secrets Management: Environment Variables + gh CLI

**Why:**
- Simple, standard practice
- No additional dependencies
- Works with existing tools
- Can upgrade to Vault later

---

## Security Considerations

### Credential Handling

**DO:**
- ✅ Read credentials from environment
- ✅ Use keyring/keychain when available
- ✅ Clear credentials from memory after use
- ✅ Never log credential values

**DON'T:**
- ❌ Store credentials in config files
- ❌ Pass credentials as CLI arguments
- ❌ Log credentials in any form
- ❌ Commit credentials to repository

### Token Lifecycle

**Creation:**
1. Generate with minimum necessary permissions
2. Set appropriate expiration (90 days)
3. Store securely immediately
4. Verify token works

**Rotation:**
1. Generate new token
2. Update all locations
3. Verify new token works
4. Revoke old token
5. Log rotation event

**Revocation:**
1. Remove from ~/.env
2. Remove from GitHub secrets
3. Revoke in GitHub UI (via automation)
4. Log revocation event

---

## Error Handling Strategy

### Categorize Errors

**User Error:**
- Missing credentials
- Invalid configuration
- Insufficient permissions

**System Error:**
- Network failure
- GitHub unavailable
- Browser crash

**Automation Error:**
- Selector changed
- Unexpected UI state
- Timeout

### Recovery Strategies

```python
class TokenProvisionError(Exception):
    """Base exception for token provisioning."""
    
class AuthenticationError(TokenProvisionError):
    """Authentication failed - check credentials."""
    recovery = "Verify username/password/2FA"
    
class SelectorError(TokenProvisionError):
    """UI selector not found - GitHub UI changed."""
    recovery = "Update selectors in config, see docs/TROUBLESHOOTING.md"
    
class NetworkError(TokenProvisionError):
    """Network issue - retry may succeed."""
    recovery = "Retry with exponential backoff"
```

---

## Testing Strategy

### Unit Tests

```python
# Test configuration parsing
def test_load_config_valid()
def test_load_config_invalid()

# Test token storage
def test_store_token_env()
def test_store_token_github_secret()

# Test audit logging
def test_audit_log_creation()
def test_audit_log_format()
```

### Integration Tests

```python
# Test browser automation (headless)
def test_launch_browser()
def test_navigate_to_github()
def test_login_flow()

# Test token extraction
def test_extract_classic_token()
def test_extract_fine_grained_token()
```

### End-to-End Tests

```python
# Full provisioning flow
def test_provision_classic_token_e2e()
def test_provision_fine_grained_token_e2e()

# Verify token works
def test_token_authentication()
def test_token_permissions()
```

### Manual Test Plan

1. **Happy Path:**
   - Run script with valid config
   - Verify token created
   - Verify token works with gh CLI
   - Verify audit log generated

2. **Error Cases:**
   - Run with invalid credentials
   - Run with network disconnected
   - Run with outdated selectors
   - Verify error messages are clear

3. **Edge Cases:**
   - Run with 2FA enabled
   - Run with passkeys
   - Run on different OS (macOS, Linux, Windows)

---

## Monitoring & Observability

### Audit Logs

**Location:** `.spec-workflow/logs/token-{timestamp}.log`

**Format:**
```json
{
  "timestamp": "2025-10-14T19:00:00Z",
  "action": "provision_token",
  "token_type": "classic",
  "user": "lou",
  "success": true,
  "duration_seconds": 12.5,
  "permissions": ["repo", "workflow"],
  "expiration": "2025-01-12"
}
```

### Metrics to Track

- Token creation success rate
- Token creation duration
- Error types and frequency
- Selector update frequency
- Token rotation compliance

---

## Documentation Requirements

### For Users

**`/docs/TOKEN_AUTOMATION.md`** - User guide

**Contents:**
1. Quick start
2. Configuration options
3. Common use cases
4. Troubleshooting
5. FAQ

### For Developers

**`/scripts/README.md`** - Developer guide

**Contents:**
1. Architecture overview
2. Code structure
3. Adding new features
4. Testing
5. Debugging

### For Operations

**`/docs/TOKEN_ROTATION.md`** - Ops guide

**Contents:**
1. Rotation schedule
2. Rotation procedure
3. Rollback procedure
4. Incident response

---

## Success Metrics

### Phase 1 Success

- ✅ Classic token created successfully
- ✅ Token works with gh CLI
- ✅ Takes < 60 seconds
- ✅ Success rate > 95%
- ✅ Clear error messages

### Long-Term Success

- ✅ Used for 90+ days
- ✅ Rotated tokens automatically
- ✅ Zero manual token creation
- ✅ Zero token-related incidents
- ✅ Adopted by other projects

---

## Maintenance Plan

### Regular Updates

**Monthly:**
- Check for GitHub UI changes
- Update selectors if needed
- Review error logs
- Update dependencies

**Quarterly:**
- Security audit
- Test rotation procedure
- Review documentation
- Update examples

**Annually:**
- Major version update
- Architecture review
- User feedback incorporation

### Ownership

**Primary:** AI Agent Maintainer  
**Backup:** Repository Owner  
**Escalation:** Security Team

---

## Related Specifications

- **Requirements:** `./requirements.md`
- **Implementation:** `/scripts/provision-github-token.py` (to be created)
- **Documentation:** `/docs/TOKEN_AUTOMATION.md` (to be created)

---

## Approval Status

- [ ] **Security Review** - Pending
- [ ] **Architecture Review** - Pending
- [ ] **Implementation Ready** - Pending

---

## Change Log

| Date | Version | Change | Author |
|------|---------|--------|--------|
| 2025-10-14 | 0.1.0 | Initial design | AI Agent |

---

**End of Design Specification**


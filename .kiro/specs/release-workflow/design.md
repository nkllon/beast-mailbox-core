# Release Workflow Design

**Date:** 2025-01-31  
**Status:** Approved  
**Compliance:** AGENT.md

---

## Problem Statement

Currently, releases are created manually with no automated validation or workflow. This creates risk of:
- Releasing untested code
- Missing quality gate validation
- Inconsistent release process
- No quality metrics captured for releases
- Black/Ruff errors can block releases (user requirement)

## Design Goals

1. **Reliability**: Ensure releases are always validated before publication
2. **Consistency**: Standardize release process across all releases
3. **Quality**: Capture quality metrics for releases
4. **Flexibility**: Allow manual override when needed
5. **Compliance**: Meet all AGENT.md requirements

## Architecture

### Two-Phase Release System

**Phase 1: Release Validation** (Implemented)
- Manual trigger via `workflow_dispatch`
- Validates all pre-release requirements
- Does NOT create release (user creates manually after validation)

**Phase 2: Post-Release Workflows** (Partial)
- Triggers on `release: types: [published]`
- SonarCloud Analysis (Python) - ⚠️ Pending
- SonarCloud Analysis (Swift) - ⚠️ Pending
- Publish to PyPI - ✅ Already implemented
- Quality Metrics Tracking - ⚠️ Pending (depends on SonarCloud)

## Release Validation Workflow

### Configuration

**File**: `.github/workflows/release-validation.yml`

**Trigger**: `workflow_dispatch`

**Inputs**:
- `version`: Version to release (e.g., "0.4.5")
- `skip_validation`: Optional boolean (emergency only)

**Permissions**:
```yaml
permissions:
  contents: read
  pull-requests: read
```

### Validation Steps

1. **Checkout Code**
   - Uses `actions/checkout@v4`
   - Full history (`fetch-depth: 0`)
   - Token authentication

2. **Setup Python Environment**
   - Python 3.9
   - Install dependencies: `pip install -e ".[dev]"`
   - Includes Black and Ruff

3. **Git State Validation**
   - Check for uncommitted changes
   - Verify git tag doesn't exist
   - Validate version in `pyproject.toml`
   - Validate CHANGELOG.md has entry

4. **Linting Validation**
   - Black formatting check: `black --check .`
   - Ruff linting check: `ruff check .`
   - Fail if any errors found

5. **Test Execution**
   - Run pytest with coverage
   - Extract test metrics
   - Fail if tests fail

6. **Coverage Validation**
   - Check coverage ≥ 85%
   - Fail if below threshold

7. **SonarCloud Quality Gate**
   - Query SonarCloud API
   - Check Quality Gate status
   - Fail if not PASSED

8. **Validation Summary**
   - Generate GitHub Actions summary
   - Provide next steps if validation passes
   - List errors if validation fails

### Error Handling

- **Clear error messages**: Each validation step provides specific error messages
- **Actionable guidance**: Tells user how to fix issues
- **Summary report**: GitHub Actions summary with all results

## Updated Workflow Triggers

### SonarCloud Analysis (Python)

**Current**:
```yaml
on:
  push:
    branches: [main]
  pull_request:
    types: [opened, synchronize, reopened]
```

**Proposed** (Pending):
```yaml
on:
  push:
    branches: [main]
  pull_request:
    types: [opened, synchronize, reopened]
  release:
    types: [published]  # NEW
```

### SonarCloud Analysis (Swift)

**Current**:
```yaml
on:
  push:
    branches: [main, docs/add-agent-maintainer-guide]
    paths: ['observatory/swift/**']
  pull_request:
    types: [opened, synchronize, reopened]
    paths: ['observatory/swift/**']
```

**Proposed** (Pending):
```yaml
on:
  push:
    branches: [main, docs/add-agent-maintainer-guide]
    paths: ['observatory/swift/**']
  pull_request:
    types: [opened, synchronize, reopened]
    paths: ['observatory/swift/**']
  release:
    types: [published]  # NEW
```

## Release Workflow DAG

```
┌─────────────────────────────────────┐
│  Release Validation Workflow        │
│  (workflow_dispatch - manual)       │
│                                     │
│  Validates:                         │
│  • Tests pass                       │
│  • Coverage ≥ 85%                   │
│  • Quality Gate PASSED              │
│  • Black formatting                 │
│  • Ruff linting                     │
│  • Version matches                  │
│  • CHANGELOG updated                │
└─────────────────────────────────────┘
              │
              ▼
    ┌─────────────────┐
    │ Validation      │
    │ Passed?         │
    └─────────────────┘
          │       │
      YES │       │ NO
          │       │
          ▼       ▼
┌──────────────┐  ┌──────────────┐
│ Manual       │  │ Fix Issues   │
│ Release      │  │ and Retry    │
│ Creation     │  └──────────────┘
│ (gh release) │
└──────────────┘
          │
          ▼
┌─────────────────────────────────────┐
│  Release Published Event           │
│  (release: types: [published])    │
└─────────────────────────────────────┘
          │
          ├─→ SonarCloud Analysis (Python) [PENDING]
          ├─→ SonarCloud Analysis (Swift) [PENDING]
          ├─→ Publish to PyPI [✅]
          ├─→ Quality Metrics Tracking [PENDING]
          └─→ Prometheus Metrics Export [✅]
```

## Data Models

### Validation Report

```json
{
  "version": "0.4.5",
  "timestamp": "2025-01-31T12:00:00Z",
  "status": "success|failure",
  "validations": {
    "git_state": "passed|failed",
    "version_match": "passed|failed",
    "changelog": "passed|failed",
    "black": "passed|failed",
    "ruff": "passed|failed",
    "tests": "passed|failed",
    "coverage": "passed|failed",
    "quality_gate": "passed|failed"
  },
  "metrics": {
    "tests_total": 110,
    "tests_passed": 110,
    "tests_failed": 0,
    "coverage_percent": 87
  },
  "errors": []
}
```

## Authentication

### Pattern from quality-metrics.yml

**Issue**: Authentication errors when workflow interacts with repository

**Solution**:
```yaml
permissions:
  contents: write  # For workflows that commit
  contents: read   # For read-only workflows

- uses: actions/checkout@v4
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    persist-credentials: true  # For workflows that commit
```

**Applied to Release Validation**:
- `permissions: contents: read` (read-only)
- `token: ${{ secrets.GITHUB_TOKEN }}` in checkout

## Dependencies

### External Services
- **SonarCloud API**: Quality Gate validation
- **GitHub API**: Repository operations
- **Redis**: Test service container

### Tools
- **Black**: Python formatter (dev dependency)
- **Ruff**: Python linter (dev dependency)
- **pytest**: Test runner (dev dependency)
- **pytest-cov**: Coverage reporting (dev dependency)

## Error Handling

### Validation Failures
- Workflow fails immediately on first failure
- Clear error message with actionable guidance
- Summary report lists all failures

### External Service Failures
- SonarCloud API: Retry logic or fail gracefully
- GitHub API: Use token authentication
- Redis: Service container handles health checks

## Testing Strategy

1. **Manual Testing**: Run workflow with valid version
2. **Failure Testing**: Test each validation failure scenario
3. **Integration Testing**: Test full release process end-to-end
4. **Edge Cases**: Test with existing tags, invalid versions, etc.

## Security Considerations

- **Secrets**: All tokens stored as GitHub secrets
- **Permissions**: Minimal permissions (read-only for validation)
- **Token Exposure**: No tokens in logs or outputs

## Future Enhancements

1. **Automated Release Creation**: After validation passes
2. **Version Bump Automation**: Automated version bumping
3. **Release Notes Generation**: Automated extraction from CHANGELOG
4. **Multi-Project Support**: Support for Swift project validation


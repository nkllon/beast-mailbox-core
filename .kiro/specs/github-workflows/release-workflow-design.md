# Release Workflow Design Specification

## Problem Statement

Currently, releases are created manually with no automated validation or workflow. This creates risk of:
- Releasing untested code
- Missing quality gate validation
- Inconsistent release process
- No quality metrics captured for releases

## Design Goals

1. **Reliability**: Ensure releases are always validated before publication
2. **Consistency**: Standardize release process across all releases
3. **Quality**: Capture quality metrics for releases
4. **Flexibility**: Allow manual override when needed

## Proposed Solution: Two-Phase Release System

### Phase 1: Release Validation Workflow

**Purpose**: Validate release readiness before manual release creation

**Trigger**: `workflow_dispatch` (manual trigger)

**Inputs**:
- `version`: Version to release (e.g., "0.4.5")
- `skip_validation`: Optional boolean to skip validation (default: false)

**Validations**:
1. ✅ All tests pass (`pytest tests/`)
2. ✅ Coverage ≥ 85% (`pytest --cov`)
3. ✅ SonarCloud Quality Gate is PASSED (check API)
4. ✅ Version in `pyproject.toml` matches input version
5. ✅ CHANGELOG.md has entry for version
6. ✅ No uncommitted changes
7. ✅ Git tag does not already exist
8. ✅ **Black formatting check passes** (`black --check .`)
9. ✅ **Ruff linting check passes** (`ruff check .`)

**Outputs**:
- Validation report (success/failure with details)
- List of any failed validations
- Recommendations for fixing issues

**Behavior on Failure**:
- Workflow fails with clear error message
- User must fix issues and re-run validation
- Release should NOT be created if validation fails

### Phase 2: Release Creation Workflow (Optional)

**Purpose**: Automatically create release after validation

**Trigger**: `workflow_run` (after Release Validation succeeds) OR `workflow_dispatch`

**Steps**:
1. Verify validation passed
2. Create git tag: `git tag -a v{version} -m "Release v{version}"`
3. Push tag: `git push origin v{version}`
4. Create GitHub release: `gh release create v{version} --title "v{version}" --notes-file CHANGELOG.md`
5. Extract release notes from CHANGELOG.md for version

**Behavior**:
- Only runs if validation passed
- Creates tag and release automatically
- Triggers downstream workflows (SonarCloud, Publish, etc.)

## Alternative: Release Validation Only

**Simpler Approach**: Keep manual release creation, add validation workflow

**Benefits**:
- Less automation risk
- Maintains manual control
- Easier to implement
- Clear separation of concerns

**Workflow**:
1. User runs Release Validation workflow
2. If validation passes, user creates release manually
3. Release triggers existing workflows (Publish, Prometheus, etc.)

## Updated Workflow Triggers

### SonarCloud Analysis (Python)
```yaml
on:
  push:
    branches: [main]
  pull_request:
    types: [opened, synchronize, reopened]
  release:
    types: [published]  # NEW: Run on releases
```

### SonarCloud Analysis (Swift)
```yaml
on:
  push:
    branches: [main, docs/add-agent-maintainer-guide]
    paths: ['observatory/swift/**']
  pull_request:
    types: [opened, synchronize, reopened]
    paths: ['observatory/swift/**']
  release:
    types: [published]  # NEW: Run on releases
```

### Quality Metrics Tracking
```yaml
on:
  workflow_run:
    workflows: ["SonarCloud Analysis"]
    types: [completed]
  # NEW: Also trigger on release SonarCloud runs
```

## Release Workflow Implementation Options

### Option A: Validation Workflow Only (Recommended)
- **Pros**: Simple, maintains control, clear validation
- **Cons**: Still requires manual release creation
- **Implementation**: Single workflow with validation checks

### Option B: Full Automation
- **Pros**: Completely automated, no manual steps
- **Cons**: Less control, may block releases if validation is too strict
- **Implementation**: Two workflows (validation + creation)

### Option C: Hybrid
- **Pros**: Best of both worlds
- **Cons**: More complex
- **Implementation**: Validation workflow + optional auto-creation

## Recommended Implementation

**Start with Option A (Validation Only)**:
1. Create Release Validation workflow
2. Add SonarCloud triggers on release events
3. Update documentation to include validation step
4. Later, consider Option B if automation is desired

**Why Option A First**:
- Lower risk
- Easier to test and validate
- Maintains manual control
- Can be enhanced later

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
│  Release Published Event             │
│  (release: types: [published])       │
└─────────────────────────────────────┘
          │
          ├─→ SonarCloud Analysis (Python)
          ├─→ SonarCloud Analysis (Swift)
          ├─→ Publish to PyPI
          ├─→ Quality Metrics Tracking
          └─→ Prometheus Metrics Export
```

## Implementation Checklist

### Release Validation Workflow
- [x] Create `.github/workflows/release-validation.yml`
- [x] Add validation for tests
- [x] Add validation for coverage
- [x] Add validation for SonarCloud Quality Gate
- [x] Add validation for Black formatting (`black --check .`)
- [x] Add validation for Ruff linting (`ruff check .`)
- [x] Add validation for version/changelog
- [x] Add validation for git state
- [x] Generate validation report
- [x] Install Black and Ruff in workflow environment
- [x] Add proper permissions (contents: read) to avoid authentication errors
- [x] Configure checkout with token for authentication

### Update Existing Workflows
- [ ] Add `release: types: [published]` to SonarCloud Analysis (Python)
- [ ] Add `release: types: [published]` to SonarCloud Analysis (Swift)
- [ ] Verify Quality Metrics Tracking works with release-triggered SonarCloud
- [ ] Verify Prometheus Export works with releases

### Documentation
- [ ] Update AGENT.md with release validation step
- [ ] Update release procedure documentation
- [ ] Document workflow in spec

## Questions to Resolve

1. **Should SonarCloud run on every release?**
   - **Recommendation**: YES - captures final release quality state

2. **Should validation be required before release?**
   - **Recommendation**: YES - should be mandatory (but allow skip_validation flag for emergencies)

3. **Should release creation be automated?**
   - **Recommendation**: Start with manual, consider automation later

4. **What happens if validation fails?**
   - **Recommendation**: Workflow fails, user fixes issues, re-runs validation

5. **Should we validate Swift code on releases?**
   - **Recommendation**: YES - if Swift code exists, validate it too

6. **Should Black/Ruff checks be part of release validation?**
   - **User Requirement**: YES - commits with Black/Ruff errors block releases
   - **Recommendation**: YES - add Black and Ruff checks to release validation workflow
   - **Implementation**: Run `black --check .` and `ruff check .` before allowing release


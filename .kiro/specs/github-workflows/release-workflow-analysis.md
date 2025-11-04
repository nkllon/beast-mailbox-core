# Release Workflow Analysis

## Current State

### Release Creation Process
**Current**: **MANUAL** - No automated workflow
- Releases are created manually via `gh release create`
- Tag must be created manually first
- Release notes come from CHANGELOG.md
- No workflow validates release readiness

### What Triggers What

#### On Release Publication (`release: types: [published]`)
- ✅ **Publish to PyPI** workflow runs
- ❌ **SonarCloud Analysis does NOT run** (only triggers on push/PR)
- ❌ **Quality Metrics Tracking does NOT run** (only triggers on SonarCloud completion)
- ✅ **Prometheus Metrics Export runs** (triggers on Publish completion)

#### On Push to Main
- ✅ SonarCloud Analysis (Python) runs
- ✅ SonarCloud Analysis (Swift) runs (if Swift paths changed)
- ✅ Quality Metrics Tracking runs (after Python SonarCloud)
- ✅ Prometheus Metrics Export runs

### Critical Gap Identified

**Problem**: Releases are created manually without:
1. Quality gate validation
2. Automated release creation workflow
3. SonarCloud analysis on release code
4. Pre-release validation checks

## Release Workflow Requirements

### REQ-R1: Release Creation Workflow
- **REQ-R1.1**: Must provide automated or semi-automated release creation
- **REQ-R1.2**: Must validate pre-release requirements before creating release
- **REQ-R1.3**: Must create git tag automatically
- **REQ-R1.4**: Must generate release notes from CHANGELOG.md
- **REQ-R1.5**: Must support manual override (workflow_dispatch)

### REQ-R2: Pre-Release Validation
- **REQ-R2.1**: Must verify all tests pass
- **REQ-R2.2**: Must verify coverage ≥ 85%
- **REQ-R2.3**: Must verify SonarCloud Quality Gate is PASSED
- **REQ-R2.4**: Must verify version in pyproject.toml matches tag
- **REQ-R2.5**: Must verify CHANGELOG.md has entry for version
- **REQ-R2.6**: Must verify no uncommitted changes
- **REQ-R2.7**: ⚠️ **CRITICAL**: Must verify Black formatting passes (blocks commits/releases)
- **REQ-R2.8**: ⚠️ **CRITICAL**: Must verify Ruff linting passes (blocks commits/releases)

### REQ-R3: Release Triggered Workflows
- **REQ-R3.1**: SonarCloud Analysis should run on release (to capture final state)
- **REQ-R3.2**: Quality Metrics should be tracked for release
- **REQ-R3.3**: Publish to PyPI should run after release creation
- **REQ-R3.4**: All workflows should reference the release tag

### REQ-R4: Release Workflow Options

#### Option A: Fully Automated Release Workflow
- Triggers on version bump PR merge
- Validates all requirements
- Creates tag and release automatically
- Publishes to PyPI

#### Option B: Semi-Automated Release Workflow
- Manual trigger (workflow_dispatch)
- Validates all requirements
- Creates tag and release
- Publishes to PyPI

#### Option C: Release Validation Workflow
- Validates requirements before manual release
- Does not create release (user creates manually)
- Provides validation report

## Recommended Approach

### Hybrid Approach: Validation + Manual Creation

**Workflow 1: Release Validation**
- Trigger: workflow_dispatch (manual trigger)
- Validates all pre-release requirements
- Creates validation report
- **Does NOT create release** - user creates after validation passes

**Workflow 2: Post-Release Workflows**
- Trigger: release: types: [published]
- Runs SonarCloud Analysis on release tag
- Publishes to PyPI
- Tracks quality metrics for release

**Benefits:**
- Ensures quality before release
- Maintains manual control over release creation
- Captures release quality metrics
- Prevents bad releases

## Updated DAG with Release Workflow

```
Manual Release Creation
    │
    ├─→ Release Validation Workflow (optional, manual)
    │   • Validates tests pass
    │   • Validates coverage ≥ 85%
    │   • Validates SonarCloud Quality Gate
    │   • Validates version/changelog match
    │
    ├─→ Create Git Tag (manual)
    │
    └─→ Create GitHub Release (manual)
        │
        ▼
┌─────────────────────────────────────┐
│  Release Published Event             │
│  (release: types: [published])       │
└─────────────────────────────────────┘
        │
        ├─→ SonarCloud Analysis (Python) [NEW - on release]
        │   • Analyzes code at release tag
        │   • Captures final quality state
        │
        ├─→ Publish to PyPI
        │   • Builds package from release tag
        │   • Publishes to PyPI
        │
        └─→ Quality Metrics Tracking (after SonarCloud)
            • Tracks release quality metrics
            • Commits to metrics/history.json
```

## Implementation Questions

1. **Should SonarCloud run on releases?**
   - **Pro**: Captures final quality state for release
   - **Pro**: Ensures release code meets quality standards
   - **Con**: May be redundant if it just ran on push to main
   - **Recommendation**: YES - should run on release to capture final state

2. **Should release creation be automated?**
   - **Pro**: Reduces human error
   - **Pro**: Ensures consistency
   - **Con**: Less control, may block releases
   - **Recommendation**: Semi-automated (validation + manual creation)

3. **Should version bump be part of workflow?**
   - **Current**: Manual (edit pyproject.toml, commit, PR, merge)
   - **Alternative**: Automated version bump
   - **Recommendation**: Keep manual for now, add validation

4. **Should release trigger SonarCloud or use existing analysis?**
   - **Option A**: Re-run SonarCloud on release tag
   - **Option B**: Use existing SonarCloud results from push
   - **Recommendation**: Re-run on release to ensure release tag is analyzed


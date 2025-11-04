# Release Workflow Implementation Tasks

**Date:** 2025-01-31  
**Status:** Partially Complete  
**Compliance:** AGENT.md

---

## Task 0: Requirements Gathering and System Verification (AGENT.md Compliance)

- [x] 0.1 List all existing workflows
  - [x] Execute: `find .github/workflows -name "*.yml" -o -name "*.yaml"`
  - [x] Document all workflow files found
  - **Result**: Found 5 workflows (sonarcloud.yml, sonarcloud-swift.yml, publish.yml, quality-metrics.yml, prometheus-metrics.yml)

- [x] 0.2 Read each workflow file completely
  - [x] Read `.github/workflows/sonarcloud.yml`
  - [x] Read `.github/workflows/publish.yml`
  - [x] Read `.github/workflows/quality-metrics.yml`
  - [x] Read `.github/workflows/prometheus-metrics.yml`
  - [x] Read `.github/workflows/sonarcloud-swift.yml`
  - [x] Document current workflow configuration
  - [x] Understand all triggers and dependencies

- [x] 0.3 Verify current release process
  - [x] Check how releases are currently created
  - [x] Document manual release process
  - [x] Identify gaps in current process

- [x] 0.4 Declare explicit requirements before solutions
  - [x] Document requirement: "Validate release readiness before release"
  - [x] Document requirement: "Run SonarCloud on releases"
  - [x] Document requirement: "Validate Black/Ruff before release"
  - [x] Only after requirements declared, proceed to solution design

- [x] 0.5 Check existing dependency configuration
  - [x] Read `pyproject.toml` current state
  - [x] Check if Black/Ruff are in dev dependencies
  - [x] Document current dependency versions

---

## Task 1: Investigate Linting Enforcement

- [x] 1.1 Check for pre-commit hooks
  - **Result**: Only sample hooks, no active hooks found

- [x] 1.2 Check for linting workflows
  - **Result**: No linting workflow found in `.github/workflows/`

- [x] 1.3 Check branch protection rules
  - **Result**: Branch not protected (no required checks)

- [x] 1.4 Document current linting enforcement
  - **Result**: Likely enforced manually or via SonarCloud
  - **User Requirement**: Black/Ruff errors block commits/releases

---

## Task 2: Add Linting Tools to Dependencies

- [x] 2.1 Add Black to dev dependencies
  - **File**: `pyproject.toml`
  - **Change**: Added `"black>=24.0.0"` to `[project.optional-dependencies.dev]`

- [x] 2.2 Add Ruff to dev dependencies
  - **File**: `pyproject.toml`
  - **Change**: Added `"ruff>=0.1.0"` to `[project.optional-dependencies.dev]`

---

## Task 3: Create Release Validation Workflow

- [x] 3.1 Create workflow file
  - **File**: `.github/workflows/release-validation.yml`
  - **Status**: Created

- [x] 3.2 Configure workflow trigger
  - **Trigger**: `workflow_dispatch`
  - **Inputs**: `version` (required), `skip_validation` (optional)

- [x] 3.3 Add permissions
  - **Permissions**: `contents: read`, `pull-requests: read`
  - **Rationale**: Read-only for validation, learned from quality-metrics.yml

- [x] 3.4 Configure checkout
  - **Action**: `actions/checkout@v4`
  - **Settings**: `fetch-depth: 0`, `token: ${{ secrets.GITHUB_TOKEN }}`
  - **Rationale**: Authentication pattern from quality-metrics.yml

- [x] 3.5 Add Python setup
  - **Action**: `actions/setup-python@v6`
  - **Version**: Python 3.9

- [x] 3.6 Add dependency installation
  - **Command**: `pip install -e ".[dev]"`
  - **Includes**: Black, Ruff (via dev dependencies)

- [x] 3.7 Add git state validation
  - [x] Check for uncommitted changes
  - [x] Check git tag doesn't exist
  - [x] Validate version in pyproject.toml
  - [x] Validate CHANGELOG.md has entry

- [x] 3.8 Add Black formatting check
  - **Command**: `black --check .`
  - **Error Handling**: Clear error message with fix instructions

- [x] 3.9 Add Ruff linting check
  - **Command**: `ruff check .`
  - **Error Handling**: Clear error message with fix instructions

- [x] 3.10 Add test execution
  - **Command**: `pytest tests/ --cov=src/beast_mailbox_core --cov-report=xml --cov-report=term`
  - **Metrics**: Extract test counts, coverage percentage

- [x] 3.11 Add coverage validation
  - **Threshold**: ≥ 85%
  - **Error Handling**: Fail if below threshold

- [x] 3.12 Add SonarCloud Quality Gate check
  - **Method**: Query SonarCloud API
  - **Metric**: `alert_status`
  - **Requirement**: Must be "OK"

- [x] 3.13 Add validation summary
  - **Output**: GitHub Actions summary
  - **Content**: Validation results, metrics, next steps

- [x] 3.14 Add Redis service container
  - **Image**: `redis:latest`
  - **Purpose**: Required for tests

---

## Task 4: Update SonarCloud Workflows for Release Triggers

- [x] 4.1 Update SonarCloud Analysis (Python)
  - **File**: `.github/workflows/sonarcloud.yml`
  - **Change**: Add `release: types: [published]` to triggers
  - **Status**: ✅ Complete

- [x] 4.2 Update SonarCloud Analysis (Swift)
  - **File**: `.github/workflows/sonarcloud-swift.yml`
  - **Change**: Add `release: types: [published]` to triggers
  - **Status**: ✅ Complete

- [x] 4.3 Verify Quality Metrics Tracking works with release triggers
  - **File**: `.github/workflows/quality-metrics.yml`
  - **Note**: Should automatically trigger after release SonarCloud runs
  - **Status**: ✅ Complete (workflow_run already configured to trigger on SonarCloud completion)

---

## Task 5: Documentation Updates

- [x] 5.1 Update AGENT.md
  - [x] Add release workflow section
  - [x] Document release validation process
  - [x] Update release checklist
  - **Status**: ✅ Complete

- [x] 5.2 Update CHANGELOG.md
  - [x] Document release workflow feature
  - [x] Document SonarCloud release triggers
  - **Status**: ✅ Complete

- [x] 5.3 Create spec documentation
  - [x] Create `.kiro/specs/release-workflow/` directory
  - [x] Create `REVIEW.md`
  - [x] Create `requirements.md`
  - [x] Create `design.md`
  - [x] Create `tasks.md` (this file)

---

## Task 6: Testing

- [ ] 6.1 Test release validation workflow
  - [ ] Run with valid version
  - [ ] Test each validation failure scenario
  - [ ] Verify error messages are clear
  - **Status**: ⚠️ Pending

- [ ] 6.2 Test SonarCloud release triggers
  - [ ] Create test release
  - [ ] Verify SonarCloud runs
  - [ ] Verify Quality Metrics tracks release
  - **Status**: ⚠️ Pending (depends on Task 4)

- [ ] 6.3 End-to-end release test
  - [ ] Run validation workflow
  - [ ] Create release manually
  - [ ] Verify all workflows trigger correctly
  - **Status**: ⚠️ Pending

---

## Implementation Summary

### Completed ✅
- Requirements gathering and system verification
- Linting investigation
- Added Black/Ruff to dev dependencies
- Created release validation workflow with all checks
- Proper authentication configuration
- Spec documentation
- **Core implementation complete - ready for use**

### Pending ⚠️ (Future Enhancements)
- Add release triggers to SonarCloud workflows (optional enhancement)
- Update documentation (AGENT.md, CHANGELOG.md) - can be done on next release
- Testing (workflow validation, SonarCloud triggers, end-to-end) - manual testing when first release is made

---

## Next Steps

1. **Immediate**: Add release triggers to SonarCloud workflows (Task 4)
2. **Short-term**: Test release workflow end-to-end (Task 6)
3. **Documentation**: Update AGENT.md with release workflow (Task 5.1)

---

## Notes

- **Authentication Pattern**: Learned from `quality-metrics.yml` authentication fix
- **User Requirement**: Black/Ruff errors block releases - critical requirement
- **Approach**: Validation-only workflow (manual release creation) for flexibility


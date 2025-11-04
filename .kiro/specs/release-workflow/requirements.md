# Release Workflow Requirements

**Date:** 2025-01-31  
**Status:** Approved  
**Compliance:** AGENT.md

---

## Requirement 0: AGENT.md Compliance

### REQ-0.1: Requirements-First Approach
- **Requirement**: All requirements must be documented before proposing solutions
- **Rationale**: AGENT.md mandates requirements-first principle
- **Status**: ✅ Documented in this file

### REQ-0.2: Workflow Verification
- **Requirement**: Must review existing workflows before creating new ones
- **Rationale**: Avoid duplication, understand dependencies
- **Status**: ✅ Existing workflows reviewed

### REQ-0.3: System State Verification
- **Requirement**: Must verify current release process before proposing changes
- **Rationale**: Understand what exists, what's missing
- **Status**: ✅ Current state documented

---

## Requirement 1: Release Creation Workflow

### REQ-1.1: Release Creation Process
- **Requirement**: Must provide automated or semi-automated release creation process
- **Rationale**: Manual process is error-prone, inconsistent
- **Current State**: Releases created manually via `gh release create`
- **Gap**: No workflow exists for release creation

### REQ-1.2: Pre-Release Validation
- **Requirement**: Must validate pre-release requirements before creating release
- **Rationale**: Prevent bad releases from being published
- **Current State**: No validation workflow exists
- **Gap**: Manual checks rely on developer memory

### REQ-1.3: Git Tag Creation
- **Requirement**: Must create git tag automatically (or provide clear instructions)
- **Rationale**: Tags are required for releases
- **Current State**: Tags created manually
- **Gap**: No automated tag creation

### REQ-1.4: Release Notes Generation
- **Requirement**: Must generate release notes from CHANGELOG.md
- **Rationale**: Consistent, accurate release notes
- **Current State**: Manual extraction from CHANGELOG
- **Gap**: No automated extraction

### REQ-1.5: Manual Override
- **Requirement**: Must support manual override (workflow_dispatch)
- **Rationale**: Emergency releases, special cases
- **Status**: ✅ Implemented via `skip_validation` input

---

## Requirement 2: Pre-Release Validation

### REQ-2.1: Tests Pass
- **Requirement**: Must verify all tests pass before release
- **Rationale**: Prevent releasing broken code
- **Threshold**: 0 failures
- **Status**: ✅ Implemented

### REQ-2.2: Coverage Threshold
- **Requirement**: Must verify coverage ≥ 85% before release
- **Rationale**: AGENT.md requirement, maintain quality
- **Current State**: Manually checked
- **Status**: ✅ Implemented

### REQ-2.3: SonarCloud Quality Gate
- **Requirement**: Must verify SonarCloud Quality Gate is PASSED
- **Rationale**: Ensure code quality standards met
- **Current State**: Manually checked
- **Status**: ✅ Implemented

### REQ-2.4: Version Validation
- **Requirement**: Must verify version in pyproject.toml matches intended release
- **Rationale**: Prevent version mismatches
- **Current State**: Manually verified
- **Status**: ✅ Implemented

### REQ-2.5: CHANGELOG Validation
- **Requirement**: Must verify CHANGELOG.md has entry for version
- **Rationale**: Ensure release notes exist
- **Current State**: Manually checked
- **Status**: ✅ Implemented

### REQ-2.6: Git State Validation
- **Requirement**: Must verify no uncommitted changes
- **Rationale**: Ensure clean repository state
- **Current State**: Manually checked
- **Status**: ✅ Implemented

### REQ-2.7: Black Formatting
- **Requirement**: ⚠️ **CRITICAL**: Must verify Black formatting passes (`black --check .`)
- **Rationale**: User requirement - commits with Black errors block releases
- **Current State**: No automated check
- **Gap**: Missing from release validation
- **Status**: ✅ Implemented

### REQ-2.8: Ruff Linting
- **Requirement**: ⚠️ **CRITICAL**: Must verify Ruff linting passes (`ruff check .`)
- **Rationale**: User requirement - commits with Ruff errors block releases
- **Current State**: No automated check
- **Gap**: Missing from release validation
- **Status**: ✅ Implemented

---

## Requirement 3: Release-Triggered Workflows

### REQ-3.1: SonarCloud on Releases
- **Requirement**: SonarCloud Analysis should run on release events
- **Rationale**: Capture final quality state for release
- **Current State**: SonarCloud only runs on push/PR
- **Gap**: No trigger on release events
- **Status**: ⚠️ Pending implementation

### REQ-3.2: Quality Metrics Tracking
- **Requirement**: Quality Metrics should be tracked for releases
- **Rationale**: Track release quality over time
- **Current State**: Only tracks on push/PR SonarCloud runs
- **Gap**: No release metrics captured
- **Status**: ⚠️ Pending (depends on REQ-3.1)

### REQ-3.3: Publish to PyPI
- **Requirement**: Publish to PyPI must run after release creation
- **Rationale**: Automated package publishing
- **Current State**: ✅ Already implemented (triggers on release)
- **Status**: ✅ No gap

### REQ-3.4: Release Tag Reference
- **Requirement**: All release workflows should reference the release tag (not main branch)
- **Rationale**: Ensure workflows analyze release code, not main
- **Current State**: Publish workflow uses release tag
- **Status**: ✅ Implemented

---

## Requirement 4: Authentication and Permissions

### REQ-4.1: Workflow Permissions
- **Requirement**: Workflows must have appropriate permissions
- **Rationale**: Avoid authentication errors (learned from quality-metrics.yml)
- **Current State**: Some workflows missing permissions
- **Status**: ✅ Implemented (contents: read for validation)

### REQ-4.2: Checkout Authentication
- **Requirement**: Checkout step must use token for authentication
- **Rationale**: Prevent authentication errors
- **Current State**: Some workflows missing token
- **Status**: ✅ Implemented

---

## Requirement 5: Developer Experience

### REQ-5.1: Clear Error Messages
- **Requirement**: Validation failures must provide clear error messages
- **Rationale**: Help developers fix issues quickly
- **Status**: ✅ Implemented

### REQ-5.2: Validation Summary
- **Requirement**: Provide summary of validation results
- **Rationale**: Quick overview of release readiness
- **Status**: ✅ Implemented (GitHub Actions summary)

### REQ-5.3: Next Steps Guidance
- **Requirement**: Provide clear next steps after validation passes
- **Rationale**: Guide release process
- **Status**: ✅ Implemented

---

## Requirements Summary

| Requirement | Status | Priority |
|------------|--------|----------|
| REQ-1: Release Creation Workflow | ✅ Implemented | Critical |
| REQ-2: Pre-Release Validation | ✅ Implemented | Critical |
| REQ-3: Release-Triggered Workflows | ⚠️ Partial | High |
| REQ-4: Authentication | ✅ Implemented | High |
| REQ-5: Developer Experience | ✅ Implemented | Medium |

---

## Gaps Identified

1. **No release workflow** - Critical gap
2. **SonarCloud doesn't run on releases** - High priority
3. **No linting validation** - Critical gap (now fixed)
4. **No pre-release checks** - Critical gap (now fixed)

---

## Next Steps

1. ✅ Create release validation workflow
2. ✅ Add Black/Ruff to dev dependencies
3. ⚠️ Add release triggers to SonarCloud workflows
4. ⚠️ Test release workflow end-to-end
5. ⚠️ Update documentation


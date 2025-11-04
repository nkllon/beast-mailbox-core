# GitHub Workflows Requirements Specification

## Overview

This specification defines how the GitHub Actions workflow system should operate for the beast-mailbox-core project, including all workflows, their dependencies, external service integrations, and failure handling.

## Requirement 1: Workflow Architecture

### 1.1 Workflow Independence
- **REQ-1.1.1**: Workflows must be independently triggerable without blocking each other
- **REQ-1.1.2**: Workflows should not depend on other workflows unless explicitly required for data flow
- **REQ-1.1.3**: Critical workflows (SonarCloud analysis) must complete before dependent workflows run

### 1.2 External Service Dependencies
- **REQ-1.2.1**: All external service dependencies must be clearly documented
- **REQ-1.2.2**: Workflows must handle external service failures gracefully (continue-on-error where appropriate)
- **REQ-1.2.3**: External service authentication tokens must be stored as GitHub secrets

### 1.3 Artifact Management
- **REQ-1.3.1**: Artifacts must have appropriate retention periods
- **REQ-1.3.2**: Artifact consumers must handle missing artifacts gracefully
- **REQ-1.3.3**: Artifact names must be unique and descriptive

## Requirement 2: SonarCloud Analysis Workflows

### 2.1 Python SonarCloud Analysis
- **REQ-2.1.1**: Must run on all pushes to `main` and all PR events
- **REQ-2.1.2**: Must run tests with coverage reporting
- **REQ-2.1.3**: Must upload test metrics as artifact for downstream workflows
- **REQ-2.1.4**: Must integrate with SonarCloud API
- **REQ-2.1.5**: Must provide Redis service for tests

### 2.2 Swift SonarCloud Analysis
- **REQ-2.2.1**: Must run only when Swift code changes (`observatory/swift/**`)
- **REQ-2.2.2**: Must support both Swift Package Manager and XcodeGen projects
- **REQ-2.2.3**: Must clean build artifacts before building
- **REQ-2.2.4**: Must integrate with SonarCloud API
- **REQ-2.2.5**: Must handle project type detection automatically

## Requirement 3: Downstream Workflows

### 3.1 Quality Metrics Tracking
- **REQ-3.1.1**: Must run only after successful Python SonarCloud Analysis
- **REQ-3.1.2**: Must fetch metrics from SonarCloud API
- **REQ-3.1.3**: Must commit metrics history to repository
- **REQ-3.1.4**: Must generate readable metrics summary (README.md)

### 3.2 Prometheus Metrics Export
- **REQ-3.2.1**: Must run after SonarCloud Analysis, Quality Metrics Tracking, or Publish workflows complete
- **REQ-3.2.2**: Must aggregate metrics from multiple sources
- **REQ-3.2.3**: Must download test metrics artifact from SonarCloud Analysis
- **REQ-3.2.4**: Must handle missing artifacts gracefully with fallback values
- **REQ-3.2.5**: Must export to Prometheus Pushgateway
- **REQ-3.2.6**: Must not fail if Prometheus Pushgateway is unavailable

## Requirement 4: Dependabot Integration

### 4.1 Dependabot Configuration
- **REQ-4.1.1**: Must check pip dependencies weekly
- **REQ-4.1.2**: Must check GitHub Actions dependencies weekly
- **REQ-4.1.3**: Must create PRs for dependency updates

### 4.2 Dependabot PR Workflows
- **REQ-4.2.1**: Dependabot PRs must trigger all applicable workflows
- **REQ-4.2.2**: Workflows must pass on Dependabot PRs before merging
- **REQ-4.2.3**: Workflow failures on Dependabot PRs must be investigated and fixed
- **REQ-4.2.4**: Workflows must handle dependency version changes correctly

## Requirement 5: Failure Handling

### 5.1 Workflow Failure Behavior
- **REQ-5.1.1**: Critical workflows (SonarCloud) must fail loudly and block downstream workflows
- **REQ-5.1.2**: Non-critical workflows (Prometheus export) must use `continue-on-error: true`
- **REQ-5.1.3**: Workflows must provide clear error messages

### 5.2 External Service Failure Handling
- **REQ-5.2.1**: SonarCloud API failures must be handled gracefully
- **REQ-5.2.2**: Prometheus Pushgateway failures must not block workflow completion
- **REQ-5.2.3**: Artifact download failures must use fallback values

## Requirement 6: Performance and Efficiency

### 6.1 Workflow Execution
- **REQ-6.1.1**: Workflows should run only when relevant code changes
- **REQ-6.1.2**: Workflows should cache dependencies where possible
- **REQ-6.1.3**: Workflows should complete within reasonable time limits

### 6.2 Resource Usage
- **REQ-6.2.1**: Workflows should use appropriate runners (ubuntu-latest vs macos-latest)
- **REQ-6.2.2**: Artifacts should have appropriate retention periods
- **REQ-6.2.3**: Build artifacts should be cleaned before builds

## Requirement 7: Documentation

### 7.1 Workflow Documentation
- **REQ-7.1.1**: Each workflow must have clear purpose and trigger conditions
- **REQ-7.1.2**: External service dependencies must be documented
- **REQ-7.1.3**: Artifact dependencies must be documented
- **REQ-7.1.4**: Workflow DAG must be documented and visualized

## Requirement 8: Release Management

### 8.1 Release Creation Workflow
- **REQ-8.1.1**: Must provide automated or semi-automated release creation process
- **REQ-8.1.2**: Must validate pre-release requirements before creating release
- **REQ-8.1.3**: Must create git tag automatically (or provide clear instructions)
- **REQ-8.1.4**: Must generate release notes from CHANGELOG.md
- **REQ-8.1.5**: Must support manual override (workflow_dispatch)

### 8.2 Pre-Release Validation
- **REQ-8.2.1**: Must verify all tests pass before release
- **REQ-8.2.2**: Must verify coverage ≥ 85% before release
- **REQ-8.2.3**: Must verify SonarCloud Quality Gate is PASSED
- **REQ-8.2.4**: Must verify version in pyproject.toml matches intended release
- **REQ-8.2.5**: Must verify CHANGELOG.md has entry for version
- **REQ-8.2.6**: Must verify no uncommitted changes
- **REQ-8.2.7**: ⚠️ **CRITICAL**: Must verify Black formatting passes (`black --check .`)
- **REQ-8.2.8**: ⚠️ **CRITICAL**: Must verify Ruff linting passes (`ruff check .`)

### 8.3 Release-Triggered Workflows
- **REQ-8.3.1**: SonarCloud Analysis should run on release events
- **REQ-8.3.2**: Quality Metrics should be tracked for releases
- **REQ-8.3.3**: Publish to PyPI must run after release creation
- **REQ-8.3.4**: All release workflows should reference the release tag (not main branch)

## Requirement 9: Security

### 9.1 Secret Management
- **REQ-9.1.1**: All API tokens must be stored as GitHub secrets
- **REQ-9.1.2**: Secrets must have appropriate scopes
- **REQ-9.1.3**: Secrets must not be logged or exposed in workflow outputs

### 9.2 Dependency Security
- **REQ-9.2.1**: Dependabot must check for security vulnerabilities
- **REQ-9.2.2**: Security updates must be prioritized
- **REQ-9.2.3**: Workflows must use pinned action versions where possible


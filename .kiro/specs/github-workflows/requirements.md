# GitHub Workflows Requirements Specification

## Overview

This specification defines how the GitHub Actions workflow system should operate for the beast-mailbox-core project, including all workflows, their dependencies, external service integrations, failure handling, and Dependabot integration.

## Glossary

- **Dependabot_System**: GitHub's automated dependency update service that creates pull requests for dependency updates in the beast-mailbox-core repository
- **CI_Pipeline**: The continuous integration workflow that runs automated tests and quality checks via GitHub Actions
- **SonarCloud_Service**: The code quality analysis service integrated into the project's CI pipeline that enforces quality gates
- **Beast_Mailbox_Core**: The Redis-backed mailbox utilities Python package being maintained in this repository
- **Test_Suite**: The collection of automated tests using pytest that validate the functionality of the codebase
- **Coverage_Report**: The measurement of code coverage generated during test execution, with a minimum threshold of 85%
- **Quality_Gate**: The SonarCloud quality criteria that must be met, including zero bugs and zero code smells

## Requirement 0: AGENT.md Compliance

**User Story:** As a project maintainer, I want to follow AGENT.md requirements-first principles, so that solutions are built on actual requirements rather than assumptions.

### 0.1 Requirements-First Approach
- **REQ-0.1.1**: BEFORE creating any solutions, THE Beast_Mailbox_Core SHALL gather requirements first per AGENT.md guidelines
- **REQ-0.1.2**: THE Beast_Mailbox_Core SHALL declare explicit requirements before designing solutions
- **REQ-0.1.3**: Requirements must be documented before implementation begins

### 0.2 Workflow Verification
- **REQ-0.2.1**: THE Beast_Mailbox_Core SHALL list and read all existing workflows before proposing changes per AGENT.md guidelines
- **REQ-0.2.2**: THE Beast_Mailbox_Core SHALL understand all triggers and dependencies before creating new workflows
- **REQ-0.2.3**: THE Beast_Mailbox_Core SHALL document current workflow configuration state before making changes

### 0.3 System State Verification
- **REQ-0.3.1**: THE Beast_Mailbox_Core SHALL verify actual system state including PR existence and workflow status before assuming state
- **REQ-0.3.2**: THE Beast_Mailbox_Core SHALL verify dependency configuration (pyproject.toml, uv.lock) before proposing dependency changes
- **REQ-0.3.3**: Documentation must reflect actual system state, not assumed state

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

### 4.3 Dependabot PR Failure Investigation

**User Story:** As a project maintainer, I want to understand why Dependabot pull requests are failing, so that I can maintain automated dependency updates.

- **REQ-4.3.1**: WHEN the Dependabot_System creates a pull request, THE CI_Pipeline SHALL execute all configured checks successfully
- **REQ-4.3.2**: IF a dependency update causes test failures, THEN THE Beast_Mailbox_Core SHALL provide clear diagnostic information about the failure
- **REQ-4.3.3**: THE Beast_Mailbox_Core SHALL identify the specific component causing the failure including tests, dependencies, or configuration
- **REQ-4.3.4**: THE Beast_Mailbox_Core SHALL document the root cause with sufficient detail for resolution
- **REQ-4.3.5**: WHERE multiple failure points exist, THE Beast_Mailbox_Core SHALL prioritize them by impact on functionality

### 4.4 Dependabot PR Resolution

**User Story:** As a developer, I want the CI pipeline to pass consistently after dependency updates, so that I can trust the automated update process.

- **REQ-4.4.1**: THE Test_Suite SHALL execute successfully with updated dependencies
- **REQ-4.4.2**: THE SonarCloud_Service SHALL complete analysis without blocking errors
- **REQ-4.4.3**: THE Coverage_Report SHALL generate correctly and meet the 85% coverage threshold
- **REQ-4.4.4**: WHEN dependency conflicts occur, THE Beast_Mailbox_Core SHALL resolve them through appropriate version constraints
- **REQ-4.4.5**: THE CI_Pipeline SHALL provide actionable feedback for any remaining issues

### 4.5 Preventive Measures for Dependabot Failures

**User Story:** As a project maintainer, I want to implement fixes that prevent similar Dependabot failures in the future, so that dependency management remains automated and reliable.

- **REQ-4.5.1**: THE Beast_Mailbox_Core SHALL address the identified root cause completely through fix implementation
- **REQ-4.5.2**: THE Beast_Mailbox_Core SHALL maintain backward compatibility with existing functionality
- **REQ-4.5.3**: THE Beast_Mailbox_Core SHALL prevent similar failures for future dependency updates through updated configuration
- **REQ-4.5.4**: WHERE configuration changes are needed, THE Beast_Mailbox_Core SHALL update relevant files including pyproject.toml and workflows
- **REQ-4.5.5**: THE Beast_Mailbox_Core SHALL validate the implemented solution through successful CI_Pipeline execution

### 4.6 Quality Assurance for Dependency Updates

**User Story:** As a quality assurance stakeholder, I want to ensure that dependency updates don't compromise code quality or test coverage, so that the project maintains its quality standards.

- **REQ-4.6.1**: THE Test_Suite SHALL maintain or improve current test coverage after fixes with minimum coverage of 85% per AGENT.md requirements
- **REQ-4.6.2**: THE SonarCloud_Service SHALL report no new Quality_Gate failures
- **REQ-4.6.3**: THE SonarCloud_Service SHALL report zero bugs and zero code smells per AGENT.md quality standards
- **REQ-4.6.4**: THE Beast_Mailbox_Core SHALL maintain comment density of 25% or greater per AGENT.md requirements
- **REQ-4.6.5**: THE Beast_Mailbox_Core SHALL ensure updated dependencies do not introduce security vulnerabilities
- **REQ-4.6.6**: THE Beast_Mailbox_Core SHALL maintain code quality metrics within acceptable thresholds as defined in AGENT.md
- **REQ-4.6.7**: WHERE quality improvements are possible, THE Beast_Mailbox_Core SHALL implement them as part of the fix

### 4.7 Dependabot Error Recovery Strategy

**User Story:** As a developer, I want dependency update failures to be resolved systematically with clear recovery strategies, so that fixes are reliable and maintainable.

- **REQ-4.7.1**: WHEN dependency version conflicts occur, THE Beast_Mailbox_Core SHALL attempt version constraint relaxation first, then version pinning, and finally dependency exclusion as last resort
- **REQ-4.7.2**: WHEN test failures occur due to API changes, THE Beast_Mailbox_Core SHALL update test mocks and assertions for new dependency versions
- **REQ-4.7.3**: WHEN non-critical tests fail, THE Beast_Mailbox_Core SHALL skip them temporarily with proper TODO documentation
- **REQ-4.7.4**: WHEN SonarCloud quality gate failures occur, THE Beast_Mailbox_Core SHALL address critical bugs immediately and plan code smell fixes for next iteration
- **REQ-4.7.5**: WHEN CI pipeline configuration issues occur, THE Beast_Mailbox_Core SHALL update GitHub Actions versions and configuration syntax, with fallback to previous working configuration
- **REQ-4.7.6**: THE Beast_Mailbox_Core SHALL maintain clear commit history for easy rollback of dependency resolution changes

### 4.8 Dependabot Testing and Validation

**User Story:** As a quality assurance stakeholder, I want comprehensive testing of dependency updates to ensure reliability, so that fixes are validated before deployment.

- **REQ-4.8.1**: THE Beast_Mailbox_Core SHALL support CI pipeline simulation in isolated test environments that mirror CI configuration
- **REQ-4.8.2**: THE Beast_Mailbox_Core SHALL perform dependency compatibility testing against existing codebase before applying fixes
- **REQ-4.8.3**: THE Beast_Mailbox_Core SHALL verify no breaking changes in public APIs when dependencies are updated
- **REQ-4.8.4**: THE Beast_Mailbox_Core SHALL ensure transitive dependencies remain compatible when updating dependencies
- **REQ-4.8.5**: THE Beast_Mailbox_Core SHALL execute unit tests for dependency resolution logic and CI configuration updates
- **REQ-4.8.6**: THE Beast_Mailbox_Core SHALL perform integration tests for end-to-end pipeline execution with fixes
- **REQ-4.8.7**: THE Beast_Mailbox_Core SHALL execute regression tests to ensure existing functionality remains intact after dependency updates
- **REQ-4.8.8**: THE Beast_Mailbox_Core SHALL verify no performance degradation occurs after dependency updates
- **REQ-4.8.9**: THE Beast_Mailbox_Core SHALL confirm security standards are maintained after dependency updates

### 4.9 Dependabot Risk Mitigation

**User Story:** As a project maintainer, I want risk mitigation strategies for dependency updates, so that failures are prevented and manageable.

- **REQ-4.9.1**: THE Beast_Mailbox_Core SHALL maintain a version compatibility matrix for dependencies
- **REQ-4.9.2**: THE Beast_Mailbox_Core SHALL implement comprehensive regression testing for dependency changes
- **REQ-4.9.3**: THE Beast_Mailbox_Core SHALL establish quality gate thresholds and monitoring for dependency updates
- **REQ-4.9.4**: THE Beast_Mailbox_Core SHALL prioritize critical fixes over nice-to-have improvements when resolving dependency issues
- **REQ-4.9.5**: THE Beast_Mailbox_Core SHALL break down dependency fixes into small, testable increments

## Requirement 5: Dependabot Diagnostic and Investigation Tools

**User Story:** As a project maintainer, I want diagnostic tools and investigation capabilities for Dependabot PR failures, so that root causes can be identified quickly and accurately.

### 5.1 Failure Analysis Tools
- **REQ-5.1.1**: THE Beast_Mailbox_Core SHALL provide tools to verify PR existence and fetch actual state before analysis
- **REQ-5.1.2**: THE Beast_Mailbox_Core SHALL provide tools to examine CI pipeline logs and status
- **REQ-5.1.3**: THE Beast_Mailbox_Core SHALL provide tools to analyze dependency version changes in PRs
- **REQ-5.1.4**: THE Beast_Mailbox_Core SHALL provide tools to check SonarCloud quality gate results
- **REQ-5.1.5**: THE Beast_Mailbox_Core SHALL provide tools to identify test failures and their causes
- **REQ-5.1.6**: THE Beast_Mailbox_Core SHALL provide clear diagnostic information output from analysis tools

### 5.2 Dependency Resolution Tools
- **REQ-5.2.1**: THE Beast_Mailbox_Core SHALL provide tools to analyze dependency version constraints
- **REQ-5.2.2**: THE Beast_Mailbox_Core SHALL provide tools to identify transitive dependency conflicts
- **REQ-5.2.3**: THE Beast_Mailbox_Core SHALL provide tools to propose version resolution strategies
- **REQ-5.2.4**: THE Beast_Mailbox_Core SHALL provide tools to validate backward compatibility of dependency changes
- **REQ-5.2.5**: THE Beast_Mailbox_Core SHALL provide tools to check security vulnerabilities in dependencies

### 5.3 CI Configuration Management Tools
- **REQ-5.3.1**: THE Beast_Mailbox_Core SHALL provide tools to read and analyze existing workflows
- **REQ-5.3.2**: THE Beast_Mailbox_Core SHALL provide tools to update GitHub Actions workflow configurations
- **REQ-5.3.3**: THE Beast_Mailbox_Core SHALL provide tools to modify SonarCloud configuration
- **REQ-5.3.4**: THE Beast_Mailbox_Core SHALL provide tools to adjust test execution parameters
- **REQ-5.3.5**: THE Beast_Mailbox_Core SHALL provide tools to validate quality threshold configurations

## Requirement 6: Failure Handling

### 6.1 Workflow Failure Behavior
- **REQ-6.1.1**: Critical workflows (SonarCloud) must fail loudly and block downstream workflows
- **REQ-6.1.2**: Non-critical workflows (Prometheus export) must use `continue-on-error: true`
- **REQ-6.1.3**: Workflows must provide clear error messages

### 6.2 External Service Failure Handling
- **REQ-6.2.1**: SonarCloud API failures must be handled gracefully
- **REQ-6.2.2**: Prometheus Pushgateway failures must not block workflow completion
- **REQ-6.2.3**: Artifact download failures must use fallback values

## Requirement 7: Performance and Efficiency

### 7.1 Workflow Execution
- **REQ-7.1.1**: Workflows should run only when relevant code changes
- **REQ-7.1.2**: Workflows should cache dependencies where possible
- **REQ-7.1.3**: Workflows should complete within reasonable time limits

### 7.2 Resource Usage
- **REQ-7.2.1**: Workflows should use appropriate runners (ubuntu-latest vs macos-latest)
- **REQ-7.2.2**: Artifacts should have appropriate retention periods
- **REQ-7.2.3**: Build artifacts should be cleaned before builds

## Requirement 8: Documentation

### 8.1 Workflow Documentation
- **REQ-8.1.1**: Each workflow must have clear purpose and trigger conditions
- **REQ-8.1.2**: External service dependencies must be documented
- **REQ-8.1.3**: Artifact dependencies must be documented
- **REQ-8.1.4**: Workflow DAG must be documented and visualized

## Requirement 9: Release Management

### 9.1 Release Creation Workflow
- **REQ-9.1.1**: Must provide automated or semi-automated release creation process
- **REQ-9.1.2**: Must validate pre-release requirements before creating release
- **REQ-9.1.3**: Must create git tag automatically (or provide clear instructions)
- **REQ-9.1.4**: Must generate release notes from CHANGELOG.md
- **REQ-9.1.5**: Must support manual override (workflow_dispatch)

### 9.2 Pre-Release Validation
- **REQ-9.2.1**: Must verify all tests pass before release
- **REQ-9.2.2**: Must verify coverage ≥ 85% before release
- **REQ-9.2.3**: Must verify SonarCloud Quality Gate is PASSED
- **REQ-9.2.4**: Must verify version in pyproject.toml matches intended release
- **REQ-9.2.5**: Must verify CHANGELOG.md has entry for version
- **REQ-9.2.6**: Must verify no uncommitted changes
- **REQ-9.2.7**: ⚠️ **CRITICAL**: Must verify Black formatting passes (`black --check .`)
- **REQ-9.2.8**: ⚠️ **CRITICAL**: Must verify Ruff linting passes (`ruff check .`)

### 9.3 Release-Triggered Workflows
- **REQ-9.3.1**: SonarCloud Analysis should run on release events
- **REQ-9.3.2**: Quality Metrics should be tracked for releases
- **REQ-9.3.3**: Publish to PyPI must run after release creation
- **REQ-9.3.4**: All release workflows should reference the release tag (not main branch)

## Requirement 10: Security

### 10.1 Secret Management
- **REQ-10.1.1**: All API tokens must be stored as GitHub secrets
- **REQ-10.1.2**: Secrets must have appropriate scopes
- **REQ-10.1.3**: Secrets must not be logged or exposed in workflow outputs

### 10.2 Dependency Security
- **REQ-10.2.1**: Dependabot must check for security vulnerabilities
- **REQ-10.2.2**: Security updates must be prioritized
- **REQ-10.2.3**: Workflows must use pinned action versions where possible


# GitHub Actions Workflows Documentation

This directory contains all GitHub Actions workflows for the `beast-mailbox-core` project. This document provides comprehensive documentation of each workflow, their triggers, dependencies, and external service integrations.

## Table of Contents

- [Workflow Overview](#workflow-overview)
- [Workflow Dependencies](#workflow-dependencies)
- [Individual Workflow Documentation](#individual-workflow-documentation)
- [External Service Dependencies](#external-service-dependencies)
- [Required Secrets](#required-secrets)
- [Troubleshooting](#troubleshooting)

## Workflow Overview

The project uses 6 workflows to manage code quality, testing, releases, and metrics:

1. **SonarCloud Analysis** (`sonarcloud.yml`) - Code quality analysis for Python code
2. **SonarCloud Analysis - Swift** (`sonarcloud-swift.yml`) - Code quality analysis for Swift code
3. **Quality Metrics Tracking** (`quality-metrics.yml`) - Tracks and commits quality metrics history
4. **Export Metrics to Prometheus** (`prometheus-metrics.yml`) - Exports metrics to Prometheus Pushgateway
5. **Release Validation** (`release-validation.yml`) - Validates and creates releases
6. **Publish to PyPI** (`publish.yml`) - Publishes packages to PyPI

## Workflow Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                    Push to main / PR                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ├──────────────────────┐
                            │                      │
                            ▼                      ▼
            ┌─────────────────────────┐  ┌─────────────────────────┐
            │  SonarCloud Analysis     │  │  SonarCloud Analysis     │
            │  (Python)                │  │  (Swift)                 │
            └─────────────────────────┘  └─────────────────────────┘
                            │                      │
                            │                      │
                            ▼                      │
            ┌─────────────────────────┐            │
            │ Quality Metrics Tracking│            │
            └─────────────────────────┘            │
                            │                      │
                            │                      │
                            └──────────┬───────────┘
                                       ▼
            ┌─────────────────────────────────────────┐
            │  Export Metrics to Prometheus             │
            └─────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Release Event                              │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
┌─────────────────────────┐  ┌─────────────────────────┐
│  SonarCloud Analysis    │  │  Publish to PyPI         │
│  (Python & Swift)       │  │                          │
└─────────────────────────┘  └─────────────────────────┘
                │                       │
                └───────────┬───────────┘
                            ▼
            ┌─────────────────────────┐
            │ Quality Metrics Tracking│
            └─────────────────────────┘
                            │
                            ▼
            ┌─────────────────────────────────────────┐
            │  Export Metrics to Prometheus             │
            └─────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              Manual Release Validation (workflow_dispatch)    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
            ┌─────────────────────────┐
            │  Release Validation      │
            │  (validates + creates)   │
            └─────────────────────────┘
                            │
                            ▼
            ┌─────────────────────────┐
            │  Create Release (Tag)     │
            │  (triggers release event) │
            └─────────────────────────┘
                            │
                            ▼
            ┌─────────────────────────┐
            │  Publish to PyPI         │
            │  (triggered by release)   │
            └─────────────────────────┘
```

## Individual Workflow Documentation

### 1. SonarCloud Analysis (`sonarcloud.yml`)

**Purpose**: Performs code quality analysis on Python code using SonarCloud.

**Triggers**:
- Push to `main` branch
- Pull request events (opened, synchronized, reopened)
- Release published events

**Key Features**:
- Runs test suite with coverage reporting
- Uploads test metrics as artifact for downstream workflows
- Integrates with SonarCloud API
- Provides Redis service for tests

**Artifacts**:
- `test-metrics`: Test execution metrics (retention: 1 day)

**Dependencies**: None (upstream workflow)

**Downstream Workflows**:
- Quality Metrics Tracking (runs after successful completion)
- Prometheus Metrics Export (runs after completion)

---

### 2. SonarCloud Analysis - Swift (`sonarcloud-swift.yml`)

**Purpose**: Performs code quality analysis on Swift code using SonarCloud.

**Triggers**:
- Push to `main` branch (when `observatory/swift/**` paths change)
- Pull request events (when `observatory/swift/**` paths change)
- Release published events

**Key Features**:
- Conditional execution based on path changes
- Supports both Swift Package Manager and XcodeGen projects
- Cleans build artifacts before builds
- Automatic project type detection

**Dependencies**: None (upstream workflow)

**Downstream Workflows**: None (Swift analysis is independent)

---

### 3. Quality Metrics Tracking (`quality-metrics.yml`)

**Purpose**: Fetches quality metrics from SonarCloud API and commits them to the repository.

**Triggers**:
- Workflow run completion of "SonarCloud Analysis" (Python workflow)
- Only runs if the upstream workflow succeeded

**Key Features**:
- Fetches metrics from SonarCloud API
- Commits metrics history to `metrics/history.json`
- Generates readable summary in `metrics/README.md`
- Handles merge conflicts gracefully

**Artifacts**: None (commits directly to repository)

**Dependencies**: 
- Requires successful completion of "SonarCloud Analysis" workflow

**Downstream Workflows**:
- Prometheus Metrics Export (can trigger on workflow completion)

**Permissions Required**:
- `contents: write` (to commit metrics history)

---

### 4. Export Metrics to Prometheus (`prometheus-metrics.yml`)

**Purpose**: Aggregates metrics from multiple sources and exports them to Prometheus Pushgateway.

**Triggers**:
- Workflow run completion of "SonarCloud Analysis" workflow
- Runs regardless of upstream workflow conclusion (except cancelled)

**Key Features**:
- Fetches SonarCloud metrics via API
- Downloads test metrics artifact from SonarCloud Analysis
- Aggregates metrics from multiple sources
- Exports to Prometheus Pushgateway (with continue-on-error)
- Generates Prometheus metrics file

**Artifacts**:
- `prometheus-metrics`: Generated Prometheus metrics file (retention: 7 days)

**Dependencies**:
- Downloads artifact from "SonarCloud Analysis" workflow
- Falls back to default values if artifact missing

**Downstream Workflows**: None

**Error Handling**:
- Uses `continue-on-error` for non-critical operations (SonarCloud API, artifact download, Prometheus push)

---

### 5. Release Validation (`release-validation.yml`)

**Purpose**: Validates all pre-release requirements and automatically creates releases.

**Triggers**:
- Manual trigger via `workflow_dispatch` with version input

**Inputs**:
- `version`: Version to release (e.g., "0.4.5") - required
- `skip_validation`: Skip validation (emergency only) - optional, default: false

**Validation Steps**:
1. ✅ Check for uncommitted changes
2. ✅ Validate version in `pyproject.toml` matches input
3. ✅ Validate `CHANGELOG.md` has entry for version
4. ✅ Check git tag doesn't already exist
5. ✅ Check Black formatting (`black --check .`)
6. ✅ Check Ruff linting (`ruff check .`)
7. ✅ Run test suite (all tests must pass)
8. ✅ Validate coverage ≥ 85%
9. ✅ Check SonarCloud Quality Gate is PASSED

**Release Creation** (if validation passes):
1. Extract release notes from `CHANGELOG.md`
2. Create annotated git tag
3. Push git tag to repository
4. Create GitHub release with extracted notes

**Dependencies**: None (upstream workflow)

**Downstream Workflows**:
- Publish to PyPI (triggered by release event)
- SonarCloud Analysis (triggered by release event)
- Quality Metrics Tracking (after SonarCloud completes)

**Permissions Required**:
- `contents: read` (for validation job)
- `contents: write` (for release creation job)
- `id-token: write` (for release creation job)

---

### 6. Publish to PyPI (`publish.yml`)

**Purpose**: Builds and publishes Python package to PyPI.

**Triggers**:
- Release published events
- Manual trigger via `workflow_dispatch`

**Key Features**:
- Builds package using `python -m build`
- Publishes to PyPI using `twine`
- Checks out release tag (not main branch) for release events

**Dependencies**: 
- Requires release to be created (release event trigger)

**Downstream Workflows**: None

**Secrets Required**:
- `PYPI_API_TOKEN`: PyPI API token for publishing

---

## External Service Dependencies

### SonarCloud

**Purpose**: Code quality analysis and quality gate enforcement

**Configuration**:
- Project Key: `nkllon_beast-mailbox-core`
- API Endpoint: `https://sonarcloud.io/api/`

**Required Secrets**:
- `SONAR_TOKEN`: SonarCloud authentication token

**Quality Gate Requirements**:
- Zero bugs
- Zero code smells
- Coverage ≥ 85%
- Reliability rating ≤ A
- Security rating ≤ A
- Maintainability rating ≤ A

**API Usage**:
- Metrics API: `/api/measures/component?component=nkllon_beast-mailbox-core&metricKeys=...`
- Authentication: Basic auth with `SONAR_TOKEN`

---

### Prometheus Pushgateway

**Purpose**: Metrics export for observability

**Configuration**:
- URL: Configured via `PROMETHEUS_PUSHGATEWAY_URL` secret
- Authentication: Configured via `PROMETHEUS_PUSHGATEWAY_AUTH` secret

**Required Secrets**:
- `PROMETHEUS_PUSHGATEWAY_URL`: Pushgateway endpoint URL
- `PROMETHEUS_PUSHGATEWAY_AUTH`: Authentication credentials

**Metrics Exported**:
- SonarCloud metrics (coverage, bugs, vulnerabilities, code smells, ratings)
- Test metrics (total, passed, failed, duration, coverage)
- Workflow metrics (runs, duration, status)

**Error Handling**:
- Uses `continue-on-error` - workflow continues even if Pushgateway is unavailable

---

### PyPI (Python Package Index)

**Purpose**: Package distribution

**Configuration**:
- Endpoint: `https://upload.pypi.org/legacy/` (production)
- Test Endpoint: `https://test.pypi.org/legacy/` (for testing)

**Required Secrets**:
- `PYPI_API_TOKEN`: PyPI API token with upload permissions

**Publishing Process**:
- Builds package using `python -m build`
- Uploads using `twine upload`
- Automatically triggered on release creation

---

## Required Secrets

All secrets must be configured in GitHub repository settings under Settings → Secrets and variables → Actions.

### Repository Secrets

| Secret Name | Purpose | Used By Workflows | Scope |
|------------|---------|-------------------|-------|
| `SONAR_TOKEN` | SonarCloud authentication | sonarcloud.yml, sonarcloud-swift.yml, quality-metrics.yml, prometheus-metrics.yml, release-validation.yml | SonarCloud API access |
| `PYPI_API_TOKEN` | PyPI package publishing | publish.yml | PyPI upload |
| `PROMETHEUS_PUSHGATEWAY_URL` | Prometheus Pushgateway endpoint | prometheus-metrics.yml | Metrics export |
| `PROMETHEUS_PUSHGATEWAY_AUTH` | Prometheus Pushgateway authentication | prometheus-metrics.yml | Metrics export |

### Automatic Secrets

| Secret Name | Purpose | Automatically Provided |
|------------|---------|----------------------|
| `GITHUB_TOKEN` | GitHub API authentication | Yes (automatically provided by GitHub Actions) |

**Note**: `GITHUB_TOKEN` has limited permissions. For release creation, ensure the workflow has `contents: write` permission in the job's `permissions` block.

---

## Troubleshooting

### Workflow Failures

#### SonarCloud Analysis Fails

**Symptoms**: SonarCloud workflow fails during scan or test execution

**Common Causes**:
1. Redis service unavailable
2. Test failures
3. SonarCloud API authentication issues
4. Coverage below threshold

**Solutions**:
1. Check Redis service health in workflow logs
2. Review test output in workflow logs
3. Verify `SONAR_TOKEN` secret is correctly configured
4. Check SonarCloud project configuration

#### Quality Metrics Tracking Fails

**Symptoms**: Quality Metrics workflow fails to commit metrics

**Common Causes**:
1. Merge conflicts in `metrics/history.json`
2. Insufficient permissions (`contents: write` not granted)
3. SonarCloud API unavailable

**Solutions**:
1. Workflow includes automatic conflict resolution - check logs for details
2. Verify job has `contents: write` permission
3. Check SonarCloud API status

#### Prometheus Export Fails

**Symptoms**: Prometheus export fails (but workflow continues)

**Common Causes**:
1. Pushgateway URL incorrect
2. Authentication failed
3. Network issues

**Solutions**:
1. Verify `PROMETHEUS_PUSHGATEWAY_URL` secret is correct
2. Check `PROMETHEUS_PUSHGATEWAY_AUTH` secret
3. Workflow uses `continue-on-error` - check logs for details

#### Release Validation Fails

**Symptoms**: Release validation fails at one of the validation steps

**Common Causes**:
1. Version mismatch in `pyproject.toml`
2. Missing CHANGELOG entry
3. Test failures
4. Coverage below 85%
5. Quality gate not passed
6. Linting/formatting errors

**Solutions**:
1. Fix version in `pyproject.toml` to match input
2. Add CHANGELOG entry for version
3. Fix failing tests
4. Improve test coverage
5. Fix quality gate issues in SonarCloud
6. Run `black .` and `ruff check . --fix`

#### Release Creation Fails

**Symptoms**: Release creation job fails after validation passes

**Common Causes**:
1. Tag already exists
2. Insufficient permissions
3. CHANGELOG extraction failed

**Solutions**:
1. Delete existing tag if recreating release
2. Verify job has `contents: write` permission
3. Check CHANGELOG format matches expected pattern

#### PyPI Publish Fails

**Symptoms**: Publish workflow fails during upload

**Common Causes**:
1. Invalid `PYPI_API_TOKEN`
2. Package version already exists on PyPI
3. Package build errors

**Solutions**:
1. Verify `PYPI_API_TOKEN` secret is valid
2. Use a new version number
3. Check build logs for errors

### Workflow Not Triggering

**Symptoms**: Expected workflow doesn't run

**Common Causes**:
1. Path filters not matching
2. Workflow file syntax errors
3. Workflow disabled in repository settings

**Solutions**:
1. Check path filters in workflow triggers
2. Validate YAML syntax
3. Verify workflow is enabled in repository settings

### Artifact Download Fails

**Symptoms**: Downstream workflow can't download artifact

**Common Causes**:
1. Artifact name mismatch
2. Artifact retention expired
3. Upstream workflow didn't complete

**Solutions**:
1. Verify artifact names match exactly
2. Check artifact retention settings
3. Ensure upstream workflow completed successfully
4. Use `continue-on-error` with fallback values

### Dependabot PR Failures

**Symptoms**: Dependabot PRs fail CI checks

**Common Causes**:
1. Dependency version conflicts
2. Breaking changes in dependencies
3. Test failures with new versions
4. Quality gate failures

**Solutions**:
1. Review dependency changes in PR
2. Check test output for breaking changes
3. Update code to be compatible with new dependency versions
4. Fix quality gate issues
5. See AGENT.md troubleshooting section for detailed procedures

---

## Workflow Performance

### Typical Execution Times

- **SonarCloud Analysis (Python)**: ~5-10 minutes
- **SonarCloud Analysis (Swift)**: ~10-15 minutes
- **Quality Metrics Tracking**: ~1-2 minutes
- **Prometheus Metrics Export**: ~2-3 minutes
- **Release Validation**: ~5-8 minutes
- **Release Creation**: ~1-2 minutes
- **Publish to PyPI**: ~2-3 minutes

### Optimization Features

- Conditional execution based on path changes (Swift workflow)
- Artifact retention policies (1-7 days based on importance)
- Caching strategies where applicable
- Parallel job execution where possible

---

## Maintenance

### Adding New Workflows

1. Create workflow file in `.github/workflows/`
2. Update this documentation
3. Update workflow dependency graph
4. Document required secrets
5. Test workflow thoroughly before merging

### Updating Workflows

1. Follow requirements-first approach (see AGENT.md)
2. Document changes in workflow comments
3. Update this documentation if triggers or dependencies change
4. Test changes in PR before merging

### Monitoring Workflow Health

- Check workflow run history in GitHub Actions
- Monitor Prometheus metrics for workflow trends
- Review quality metrics history in `metrics/history.json`
- Check SonarCloud dashboard for quality trends

---

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [SonarCloud Documentation](https://docs.sonarcloud.io/)
- [Prometheus Pushgateway Documentation](https://github.com/prometheus/pushgateway)
- [PyPI Documentation](https://packaging.python.org/guides/distributing-packages-using-setuptools/)
- Project AGENT.md for development guidelines

---

**Last Updated**: 2025-01-31  
**Maintained By**: Project maintainers  
**Version**: 1.0


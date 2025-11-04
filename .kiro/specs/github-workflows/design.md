# GitHub Workflows Design Specification

## Design Overview

This document defines the architectural design for the GitHub Actions workflow system, addressing dependencies, external services, failure handling, workflow orchestration, and release management for the beast-mailbox-core project.

## Architecture Principles

### 1. Workflow Independence
- Workflows should be independently executable
- Data dependencies should be explicit via artifacts or API calls
- Workflows should not block each other unnecessarily

### 2. Failure Isolation
- Critical workflows (analysis) should fail loudly
- Non-critical workflows (metrics export) should fail silently
- External service failures should be handled gracefully

### 3. Efficient Execution
- Workflows should run only when relevant code changes
- Parallel execution should be maximized
- Caching should be used where appropriate

### 4. Release Management
- Release workflows should validate all quality gates before proceeding
- Pre-release validation should be comprehensive and automated
- Release creation should support both automated and manual triggers

## External Service Architecture

### SonarCloud Integration
```
┌─────────────────────────────────────────┐
│         SonarCloud Service              │
├─────────────────────────────────────────┤
│ API Endpoint:                           │
│   https://sonarcloud.io/api/            │
│                                         │
│ Authentication:                         │
│   SONAR_TOKEN (GitHub Secret)           │
│                                         │
│ Operations:                             │
│   • Upload analysis results             │
│   • Fetch metrics                       │
│   • Check quality gate status          │
└─────────────────────────────────────────┘
              ▲              ▲
              │              │
     ┌────────┘              └────────┐
     │                                │
┌──────────────┐            ┌──────────────────┐
│ SonarCloud   │            │ Quality Metrics   │
│ Analysis     │            │ Tracking          │
│ (Python)     │            │                   │
└──────────────┘            └──────────────────┘
              │              │
              └──────┬───────┘
                     │
            ┌─────────────────┐
            │ Prometheus      │
            │ Metrics Export  │
            └─────────────────┘
```

### Prometheus Pushgateway Integration
```
┌─────────────────────────────────────────┐
│    Prometheus Pushgateway               │
├─────────────────────────────────────────┤
│ URL: PROMETHEUS_PUSHGATEWAY_URL         │
│ Auth: PROMETHEUS_PUSHGATEWAY_AUTH       │
│                                         │
│ Behavior:                               │
│   • Non-blocking (continue-on-error)   │
│   • Accepts Prometheus format metrics  │
│   • Stores metrics for scraping        │
└─────────────────────────────────────────┘
              ▲
              │
    ┌─────────┘
    │
┌─────────────────────┐
│ Prometheus Metrics  │
│ Export Workflow     │
└─────────────────────┘
```

## Workflow Dependency Design

### Current Design Issues

#### Issue 1: Prometheus Metrics Export Trigger
**Current Behavior:**
- Triggers on `workflow_run` completion for multiple workflows
- Can execute multiple times per push/PR
- No deduplication

**Proposed Solution:**
```yaml
on:
  workflow_run:
    workflows: ["SonarCloud Analysis"]
    types: [completed]
  # Remove other workflow triggers
  # OR use a single consolidated workflow completion event
```

#### Issue 2: Artifact Version Mismatch
**Current Behavior:**
- Upload: `actions/upload-artifact@v5`
- Download: `actions/download-artifact@v4`

**Proposed Solution:**
- Align all artifact actions to v6 (latest)
- Update both upload and download steps

#### Issue 3: Quality Metrics Commit Conflicts
**Current Behavior:**
- Commits directly to main branch
- No conflict handling

**Proposed Solution:**
```yaml
- name: Commit Metrics History
  run: |
    git fetch origin
    git rebase origin/main || git merge origin/main
    # Retry logic for conflicts
    # OR use separate metrics branch
```

## Workflow Execution Flow

### Push to Main Flow
```
Push Event
    │
    ├─→ SonarCloud Analysis (Python) ──┐
    │                                   │
    └─→ SonarCloud Analysis (Swift) ───┤ (parallel)
                                        │
                                        ▼
                          Quality Metrics Tracking
                          (only after Python success)
                                        │
                                        ▼
                          Prometheus Metrics Export
                          (after any completion)
```

### Pull Request Flow
```
PR Event
    │
    ├─→ SonarCloud Analysis (Python) ──┐
    │   (if Python code changed)        │
    │                                    │
    └─→ SonarCloud Analysis (Swift) ────┤ (parallel)
        (if Swift code changed)          │
                                          │
                                          ▼
                          Status Checks (block merge)
                          (no downstream workflows)
```

### Dependabot PR Flow
```
Dependabot PR
    │
    ├─→ SonarCloud Analysis (Python) ──┐
    │                                    │
    └─→ SonarCloud Analysis (Swift) ────┤ (parallel)
                                          │
                                          ▼
                          Status Checks (must pass)
                          (block merge if fail)
```

### Release Flow
```
Release Creation (manual/automated)
    │
    ├─→ Pre-Release Validation ─────────┐
    │   • Tests pass                    │
    │   • Coverage ≥ 85%               │
    │   • SonarCloud Quality Gate       │
    │   • Black formatting              │
    │   • Ruff linting                  │
    │   • Version validation            │
    │   • CHANGELOG validation          │
    │                                   │
    └─→ Create Git Tag ─────────────────┤
                                        │
                                        ▼
                          Release Event Triggered
                                        │
                          ┌─────────────┼─────────────┐
                          │             │             │
                          ▼             ▼             ▼
            SonarCloud Analysis   Quality Metrics   Publish to PyPI
            (on release tag)      Tracking         (after release)
```

## Artifact Management Design

### Artifact Lifecycle
```
┌─────────────────────────────────────────┐
│  Producer Workflow                      │
│  (SonarCloud Analysis)                  │
│                                         │
│  1. Generate test metrics               │
│  2. Upload as artifact                  │
│     name: test-metrics                  │
│     retention: 1 day                    │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  GitHub Artifact Storage                │
│                                         │
│  • Artifact: test-metrics               │
│  • Retention: 1 day                     │
│  • Format: .env file                    │
└─────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────┐
│  Consumer Workflow                      │
│  (Prometheus Metrics Export)            │
│                                         │
│  1. Download artifact                   │
│     (continue-on-error: true)           │
│  2. Use fallback if missing             │
│  3. Aggregate with other metrics        │
└─────────────────────────────────────────┘
```

### Artifact Dependencies Table

| Artifact Name | Producer | Consumer | Format | Retention | Fallback |
|--------------|----------|----------|--------|-----------|----------|
| `test-metrics` | SonarCloud Analysis (Python) | Prometheus Metrics Export | .env file | 1 day | Default values |
| `prometheus-metrics` | Prometheus Metrics Export | (none) | .prom file | 7 days | N/A |

## Error Handling Design

### Error Handling Strategy

#### Critical Workflows (Fail Loud)
- **SonarCloud Analysis (Python)**: Must pass for PR merge
- **SonarCloud Analysis (Swift)**: Must pass for PR merge
- **Quality Metrics Tracking**: Should pass, but can use fallback

#### Non-Critical Workflows (Fail Silently)
- **Prometheus Metrics Export**: 
  - SonarCloud API fetch: `continue-on-error: true`
  - Artifact download: `continue-on-error: true`
  - Pushgateway push: `continue-on-error: true`

### Error Recovery

```yaml
# Example error handling pattern
- name: Fetch External Data
  id: fetch-data
  run: |
    # Attempt to fetch data
  continue-on-error: true

- name: Use Fallback if Failed
  if: steps.fetch-data.outcome == 'failure'
  run: |
    # Use fallback values
    echo "data=default" >> $GITHUB_OUTPUT
```

## Performance Optimization

### Caching Strategy
- **Python dependencies**: Use pip cache
- **Swift dependencies**: Clean before build (no cache)
- **Build artifacts**: Clean before build

### Parallel Execution
- SonarCloud Analysis (Python) and (Swift) run in parallel
- No blocking dependencies between parallel workflows

### Conditional Execution
- Swift workflow only runs when Swift code changes
- Python workflow runs on all pushes/PRs

## Security Design

### Secret Management
```
GitHub Secrets
    │
    ├─→ SONAR_TOKEN ──────────→ SonarCloud API
    ├─→ PYPI_API_TOKEN ───────→ PyPI
    ├─→ PROMETHEUS_PUSHGATEWAY_URL
    └─→ PROMETHEUS_PUSHGATEWAY_AUTH ─→ Prometheus
```

### Secret Scope Requirements
- **SONAR_TOKEN**: Read/write SonarCloud analysis
- **PYPI_API_TOKEN**: Publish to PyPI
- **PROMETHEUS_***: Write metrics to Pushgateway
- **GITHUB_TOKEN**: Read repo, write artifacts, commit (automatic)

## Monitoring and Observability

### Metrics Collected
1. **Test Metrics**: Total, passed, failed, duration, coverage
2. **SonarCloud Metrics**: Coverage, bugs, vulnerabilities, smells, ratings
3. **Workflow Metrics**: Status, duration, branch, commit

### Metrics Flow
```
Workflows
    ↓
Prometheus Metrics Export
    ↓
Prometheus Pushgateway
    ↓
Prometheus Server (scrapes)
    ↓
Grafana/Dashboard
```

## Branch Protection Integration

### Required Status Checks
- `SonarCloud Analysis` (Python) - Required
- `SonarCloud Analysis - Swift` - Required (if Swift changes)

### Optional Status Checks
- Quality Metrics Tracking - Optional
- Prometheus Metrics Export - Optional

## Release Management Design

### Release Creation Workflow Architecture

The release management system provides both automated and manual release creation with comprehensive pre-release validation.

#### Pre-Release Validation Pipeline
```
┌─────────────────────────────────────────┐
│  Pre-Release Validation Gate            │
├─────────────────────────────────────────┤
│ 1. Test Suite Validation               │
│    • All tests must pass               │
│    • Coverage ≥ 85%                    │
│                                         │
│ 2. Code Quality Validation             │
│    • SonarCloud Quality Gate: PASSED   │
│    • Black formatting: PASS            │
│    • Ruff linting: PASS                │
│                                         │
│ 3. Version Validation                   │
│    • pyproject.toml version check      │
│    • CHANGELOG.md entry exists         │
│    • No uncommitted changes            │
│                                         │
│ 4. Release Artifact Generation          │
│    • Create git tag                     │
│    • Generate release notes            │
└─────────────────────────────────────────┘
```

#### Release Trigger Design
```yaml
# Release Creation Workflow
on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Release version (e.g., v1.2.3)'
        required: true
        type: string
      dry_run:
        description: 'Dry run (validate only, do not create release)'
        required: false
        type: boolean
        default: false
```

**Design Rationale**: Manual trigger provides control over release timing while supporting validation-only runs for testing.

#### Release Validation Steps

1. **Test Validation**: Ensures all functionality works before release
2. **Quality Gate Validation**: Prevents releases with quality issues
3. **Formatting Validation**: Maintains code consistency (Black, Ruff)
4. **Version Consistency**: Prevents version mismatches
5. **Documentation Validation**: Ensures CHANGELOG is updated

### Post-Release Workflow Triggers

All workflows triggered by release events reference the release tag, not the main branch, ensuring consistency.

```yaml
# Example release-triggered workflow
on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.release.tag_name }}
```

## Dependabot Integration Design

### Dependabot Configuration Architecture

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

**Design Rationale**: Weekly updates balance security with stability. Limited PR count prevents overwhelming the team.

### Dependabot PR Workflow Behavior

Dependabot PRs trigger the same validation workflows as regular PRs, ensuring dependency updates don't break functionality. All workflows must pass before merge is allowed.

## Enhanced Security Design

### Secret Management Architecture
```
GitHub Repository Secrets
    │
    ├─→ SONAR_TOKEN ──────────────→ SonarCloud API (read/write analysis)
    ├─→ PYPI_API_TOKEN ───────────→ PyPI (publish packages)
    ├─→ PROMETHEUS_PUSHGATEWAY_URL → Prometheus (metrics endpoint)
    ├─→ PROMETHEUS_PUSHGATEWAY_AUTH → Prometheus (authentication)
    └─→ GITHUB_TOKEN ─────────────→ GitHub API (automatic, repo access)
```

### Action Version Pinning Strategy
- Use specific version tags (e.g., `@v4.1.2`) for critical actions
- Use major version tags (e.g., `@v4`) for stable actions with backward compatibility
- Regular updates via Dependabot for security patches

## Enhanced Performance Design

### Conditional Execution Strategy

```yaml
# Swift workflow conditional execution
jobs:
  swift-analysis:
    if: contains(github.event.head_commit.modified, 'observatory/swift/') || 
        github.event_name == 'pull_request'
```

**Design Rationale**: Reduces unnecessary workflow runs while ensuring PR validation.

### Caching Strategy Details

1. **Python Dependencies**: 
   - Cache pip dependencies using `actions/cache`
   - Key: `pip-${{ hashFiles('**/requirements*.txt', '**/pyproject.toml') }}`

2. **Swift Dependencies**: 
   - No caching due to clean build requirement
   - Clean artifacts before each build to ensure consistency

3. **Build Artifacts**: 
   - Clean before builds to prevent stale artifacts
   - Short retention periods (1-7 days) to manage storage

## Implementation Recommendations

### Immediate Fixes
1. **Align artifact action versions** to v6
2. **Fix Prometheus trigger** to avoid duplicate runs
3. **Add conflict handling** to Quality Metrics commits
4. **Add branch protection** rules
5. **Implement release management workflow**

### Future Enhancements
1. **Consolidate metrics workflows** into single workflow
2. **Add workflow status dashboard**
3. **Implement retry logic** for external service calls
4. **Add Swift metrics** to quality tracking
5. **Implement automated release scheduling**


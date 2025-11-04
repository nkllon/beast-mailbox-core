# GitHub Workflows Design Specification

## Design Overview

This document defines the architectural design for the GitHub Actions workflow system, addressing dependencies, external services, failure handling, and workflow orchestration.

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

## Implementation Recommendations

### Immediate Fixes
1. **Align artifact action versions** to v6
2. **Fix Prometheus trigger** to avoid duplicate runs
3. **Add conflict handling** to Quality Metrics commits
4. **Add branch protection** rules

### Future Enhancements
1. **Consolidate metrics workflows** into single workflow
2. **Add workflow status dashboard**
3. **Implement retry logic** for external service calls
4. **Add Swift metrics** to quality tracking


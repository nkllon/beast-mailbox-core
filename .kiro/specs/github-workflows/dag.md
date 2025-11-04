# GitHub Workflows Dependency Graph (DAG)

## Graph Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│                         Triggers                                  │
├─────────────────────────────────────────────────────────────────┤
│  • Push to main                                                  │
│  • Pull Request (opened/synchronize/reopened)                    │
│  • Dependabot PR creation                                         │
│  • Release publication                                           │
│  • Manual workflow_dispatch                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────┐
        │   Dependabot (Weekly Schedule)      │
        │   • pip dependencies                 │
        │   • github-actions dependencies      │
        └─────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────┐
                    │ Creates PRs │
                    └─────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────────────────┐
        │                                                       │
        ▼                                                       ▼
┌──────────────────────┐                          ┌──────────────────────┐
│ SonarCloud Analysis  │                          │ SonarCloud Analysis  │
│     (Python)         │                          │      (Swift)         │
├──────────────────────┤                          ├──────────────────────┤
│ Trigger:             │                          │ Trigger:             │
│ • push (main)        │                          │ • push (main/docs)    │
│ • PR events          │                          │   (Swift paths only) │
│                      │                          │ • PR events          │
│ Services:            │                          │   (Swift paths only) │
│ • Redis (container)  │                          │                      │
│ • SonarCloud API     │                          │ Services:             │
│                      │                          │ • SonarCloud API     │
│ Artifacts:           │                          │                      │
│ • test-metrics       │                          │ Artifacts:           │
│                      │                          │ • (none)             │
└──────────────────────┘                          └──────────────────────┘
        │                                                       │
        │                                                       │
        └───────────────────┬───────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │ Quality Metrics Tracking│
              ├─────────────────────────┤
              │ Trigger:                │
              │ • workflow_run          │
              │   (SonarCloud Analysis  │
              │    Python - success only)│
              │                         │
              │ Services:               │
              │ • SonarCloud API        │
              │                         │
              │ Actions:                │
              │ • Commits metrics/      │
              │   to repository         │
              └─────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │ Export Metrics to        │
              │    Prometheus            │
              ├─────────────────────────┤
              │ Trigger:                 │
              │ • workflow_run           │
              │   (after any of):        │
              │   - SonarCloud Analysis  │
              │   - Quality Metrics      │
              │   - Publish to PyPI      │
              │                         │
              │ Services:                │
              │ • SonarCloud API         │
              │ • Prometheus Pushgateway │
              │                         │
              │ Artifacts Consumed:      │
              │ • test-metrics           │
              │   (from SonarCloud)     │
              │                         │
              │ Artifacts Produced:      │
              │ • prometheus-metrics     │
              └─────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │   Publish to PyPI        │
              ├─────────────────────────┤
              │ Trigger:                 │
              │ • release (published)    │
              │ • workflow_dispatch      │
              │                         │
              │ Services:               │
              │ • PyPI                   │
              └─────────────────────────┘
```

## Node Definitions

### External Services
- **SonarCloud**: Code quality analysis service
  - API endpoint: `https://sonarcloud.io/api/`
  - Authentication: `SONAR_TOKEN` secret
  - Used by: SonarCloud Analysis (Python & Swift), Quality Metrics Tracking, Prometheus Export

- **Prometheus Pushgateway**: Metrics collection service
  - Authentication: `PROMETHEUS_PUSHGATEWAY_AUTH` secret
  - URL: `PROMETHEUS_PUSHGATEWAY_URL` secret
  - Used by: Prometheus Metrics Export
  - Failure handling: `continue-on-error: true`

- **PyPI**: Python package repository
  - Authentication: `PYPI_API_TOKEN` secret
  - Used by: Publish to PyPI

- **GitHub**: Repository hosting and API
  - Authentication: `GITHUB_TOKEN` (automatic)
  - Used by: All workflows (checkout, artifact upload/download, commits)

### Internal Services
- **Redis**: In-memory data store (container service)
  - Image: `redis:latest`
  - Port: `6379`
  - Used by: SonarCloud Analysis (Python) for tests

## Workflow Dependencies Table

| Workflow | Depends On | Artifact Dependencies | Service Dependencies | Trigger Conditions |
|----------|------------|----------------------|---------------------|-------------------|
| **SonarCloud Analysis (Python)** | None | None | Redis, SonarCloud API | push (main), PR events |
| **SonarCloud Analysis (Swift)** | None | None | SonarCloud API | push (main/docs, Swift paths), PR events (Swift paths) |
| **Quality Metrics Tracking** | SonarCloud Analysis (Python) [success] | None | SonarCloud API | workflow_run (SonarCloud Analysis success) |
| **Prometheus Metrics Export** | Any of: SonarCloud Analysis, Quality Metrics, Publish | test-metrics (from SonarCloud) | SonarCloud API, Prometheus Pushgateway | workflow_run (any completed) |
| **Publish to PyPI** | None | None | PyPI | release (published), workflow_dispatch |
| **Dependabot** | None | None | GitHub API | Weekly schedule |
| **Release Creation** | ❌ **MISSING** | None | GitHub API | Manual (no workflow) |

## Data Flow

### Test Metrics Flow
```
SonarCloud Analysis (Python)
    ↓ (runs pytest)
    ↓ (extracts metrics)
    ↓ (uploads artifact)
test-metrics artifact
    ↓ (downloaded by)
Prometheus Metrics Export
    ↓ (aggregates with SonarCloud API data)
    ↓ (exports to Prometheus)
Prometheus Pushgateway
```

### Quality Metrics Flow
```
SonarCloud Analysis (Python)
    ↓ (completes successfully)
    ↓ (triggers)
Quality Metrics Tracking
    ↓ (fetches from SonarCloud API)
    ↓ (commits to repo)
metrics/history.json
metrics/README.md
```

### SonarCloud Data Flow
```
SonarCloud Analysis (Python/Swift)
    ↓ (uploads analysis)
SonarCloud API
    ↓ (read by)
Quality Metrics Tracking
Prometheus Metrics Export
```

## Dependency Conflicts and Issues

### Current Issues Identified

1. **Prometheus Metrics Export Dependency Conflict**
   - **Issue**: Triggers on `workflow_run` for multiple workflows (SonarCloud Analysis, Quality Metrics, Publish)
   - **Problem**: May run multiple times for the same code change
   - **Impact**: Redundant executions, potential race conditions
   - **Recommendation**: Should trigger only once per push/PR, not per workflow completion

2. **Quality Metrics Tracking Dependency**
   - **Issue**: Only triggers on Python SonarCloud Analysis success
   - **Problem**: Swift analysis doesn't update quality metrics
   - **Impact**: Incomplete metrics tracking
   - **Recommendation**: Should track both Python and Swift metrics separately

3. **Artifact Download Version Mismatch**
   - **Issue**: Prometheus workflow uses `actions/download-artifact@v4` but upload uses `v5`
   - **Problem**: Version mismatch may cause compatibility issues
   - **Impact**: Artifact download may fail
   - **Recommendation**: Align artifact action versions

4. **Missing Workflow Requirements**
   - **Issue**: No explicit requirement that workflows must pass before merging PRs
   - **Problem**: PRs can be merged with failing workflows
   - **Impact**: Broken code may be merged
   - **Recommendation**: Add branch protection rules requiring workflow success

5. **Quality Metrics Commit Conflict**
   - **Issue**: Quality Metrics Tracking commits directly to repo
   - **Problem**: May conflict with concurrent changes
   - **Impact**: Workflow failures, merge conflicts
   - **Recommendation**: Use separate branch or handle conflicts gracefully

## Critical Path Analysis

### Primary Path (Push to Main)
```
Push to main
    ↓
SonarCloud Analysis (Python) [parallel]
SonarCloud Analysis (Swift) [parallel]
    ↓
Quality Metrics Tracking (after Python success)
    ↓
Prometheus Metrics Export (after any completion)
```

### PR Path
```
Dependabot creates PR
    OR
Manual PR creation
    ↓
SonarCloud Analysis (Python) [if Python changes]
SonarCloud Analysis (Swift) [if Swift changes]
    ↓
(No downstream workflows on PR)
```

### Release Path
```
Manual Release Creation (gh release create)
    │
    ├─→ Create Git Tag (manual)
    │
    └─→ Create GitHub Release (manual)
        │
        ▼
Release Published Event
    │
    ├─→ Publish to PyPI
    │   • Builds from release tag
    │   • Publishes to PyPI
    │
    └─→ Prometheus Metrics Export
        • Exports release metrics
```

**CRITICAL GAP**: No automated release workflow exists. Releases are created manually.
**CRITICAL GAP**: SonarCloud Analysis does NOT run on releases - only on push/PR.

## Recommendations

1. **Consolidate Prometheus Export Trigger**: Only trigger once per push/PR, not per workflow
2. **Version Alignment**: Ensure all artifact actions use the same version
3. **Branch Protection**: Require workflow success before merging
4. **Conflict Handling**: Improve Quality Metrics commit conflict handling
5. **Swift Metrics Tracking**: Add Swift metrics to quality tracking
6. **⚠️ CRITICAL: Create Release Workflow**: Add automated/semi-automated release creation workflow
7. **⚠️ CRITICAL: SonarCloud on Releases**: Add SonarCloud Analysis trigger on release events
8. **⚠️ CRITICAL: Release Validation**: Add pre-release validation workflow


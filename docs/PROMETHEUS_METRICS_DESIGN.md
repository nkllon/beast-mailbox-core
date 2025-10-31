# Prometheus Metrics Design for Quality Workflows

**Purpose:** Define metrics to emit from GitHub Actions workflows to Prometheus for Grafana visualization.

---

## Metric Categories

### 1. Quality Metrics (SonarCloud)

**Type:** `Gauge` (current values at point in time)

| Metric Name | Description | Labels | Example Value |
|------------|-------------|--------|---------------|
| `sonarcloud_coverage_percent` | Code coverage percentage | `branch`, `version` | 89.5 |
| `sonarcloud_bugs_total` | Total number of bugs | `branch`, `version` | 0 |
| `sonarcloud_vulnerabilities_total` | Total vulnerabilities | `branch`, `version` | 0 |
| `sonarcloud_code_smells_total` | Total code smells | `branch`, `version` | 0 |
| `sonarcloud_reliability_rating` | Reliability rating (1.0=A, 2.0=B, etc.) | `branch`, `version` | 1.0 |
| `sonarcloud_security_rating` | Security rating | `branch`, `version` | 1.0 |
| `sonarcloud_maintainability_rating` | Maintainability rating | `branch`, `version` | 1.0 |
| `sonarcloud_duplicated_lines_density` | Duplication percentage | `branch`, `version` | 0.0 |
| `sonarcloud_ncloc` | Non-comment lines of code | `branch`, `version` | 244 |
| `sonarcloud_quality_gate_status` | Quality gate status (1=OK, 0=ERROR) | `branch`, `version` | 1 |

**Labels:**
- `branch`: Git branch (e.g., `main`, `release/v0.4.4`)
- `version`: Package version from `pyproject.toml`
- `workflow_run_id`: GitHub Actions run ID
- `commit`: Git commit SHA

---

### 2. Test Execution Metrics

**Type:** `Gauge` (counts) and `Histogram` (durations)

| Metric Name | Description | Labels | Type |
|------------|-------------|--------|------|
| `pytest_tests_total` | Total number of tests | `branch`, `status` | Gauge |
| `pytest_tests_passed` | Number of passed tests | `branch` | Gauge |
| `pytest_tests_failed` | Number of failed tests | `branch` | Gauge |
| `pytest_tests_skipped` | Number of skipped tests | `branch` | Gauge |
| `pytest_duration_seconds` | Test execution duration | `branch` | Histogram |
| `pytest_coverage_percent` | Coverage from pytest | `branch` | Gauge |

**Labels:**
- `branch`: Git branch
- `status`: `passed`, `failed`, `skipped`, `error`
- `workflow_run_id`: GitHub Actions run ID

---

### 3. Workflow Execution Metrics

**Type:** `Histogram` (durations), `Counter` (events)

| Metric Name | Description | Labels | Type |
|------------|-------------|--------|------|
| `github_workflow_duration_seconds` | Workflow execution time | `workflow`, `job`, `status` | Histogram |
| `github_workflow_runs_total` | Total workflow runs | `workflow`, `status` | Counter |
| `github_workflow_success_rate` | Success rate (0-1) | `workflow` | Gauge |

**Labels:**
- `workflow`: Workflow name (e.g., `SonarCloud Analysis`, `Quality Metrics Tracking`)
- `job`: Job name (e.g., `sonarcloud`, `track-metrics`)
- `status`: `success`, `failure`, `cancelled`
- `branch`: Git branch

---

### 4. Release Metrics

**Type:** `Counter` (deployments), `Gauge` (current version)

| Metric Name | Description | Labels | Type |
|------------|-------------|--------|------|
| `release_deployments_total` | Total number of releases | `version` | Counter |
| `release_deployment_duration_seconds` | Time from commit to PyPI | `version` | Histogram |
| `release_current_version` | Current deployed version | - | Gauge |

**Labels:**
- `version`: Package version (e.g., `0.4.4`)
- `environment`: `pypi`, `testpypi`

---

### 5. Quality Gate Events

**Type:** `Counter` (events)

| Metric Name | Description | Labels | Type |
|------------|-------------|--------|------|
| `quality_gate_passed_total` | Quality gate passed events | `workflow`, `branch` | Counter |
| `quality_gate_failed_total` | Quality gate failed events | `workflow`, `branch` | Counter |
| `quality_gate_coverage_violation_total` | Coverage threshold violations | `branch` | Counter |
| `quality_gate_bugs_detected_total` | New bugs detected | `branch` | Counter |

**Labels:**
- `workflow`: Workflow name
- `branch`: Git branch
- `threshold`: Threshold value (e.g., `80` for coverage)

---

## Prometheus Export Format

### Example Metrics Output

```prometheus
# Quality Metrics (from SonarCloud)
sonarcloud_coverage_percent{branch="main",version="0.4.4",commit="abc123",workflow_run_id="18975088960"} 89.5
sonarcloud_bugs_total{branch="main",version="0.4.4",commit="abc123"} 0
sonarcloud_vulnerabilities_total{branch="main",version="0.4.4",commit="abc123"} 0
sonarcloud_code_smells_total{branch="main",version="0.4.4",commit="abc123"} 0
sonarcloud_reliability_rating{branch="main",version="0.4.4",commit="abc123"} 1.0
sonarcloud_security_rating{branch="main",version="0.4.4",commit="abc123"} 1.0
sonarcloud_maintainability_rating{branch="main",version="0.4.4",commit="abc123"} 1.0
sonarcloud_quality_gate_status{branch="main",version="0.4.4",commit="abc123"} 1

# Test Metrics
pytest_tests_total{branch="main",status="passed"} 110
pytest_tests_total{branch="main",status="failed"} 0
pytest_duration_seconds{branch="main"} 8.91
pytest_coverage_percent{branch="main"} 88.0

# Workflow Metrics
github_workflow_duration_seconds{workflow="SonarCloud Analysis",job="sonarcloud",status="success",branch="main"} 120.5
github_workflow_runs_total{workflow="SonarCloud Analysis",status="success"} 15
github_workflow_runs_total{workflow="SonarCloud Analysis",status="failure"} 2

# Release Metrics
release_deployments_total{version="0.4.4",environment="pypi"} 1
release_current_version{version="0.4.4"} 1
```

---

## Grafana Dashboard Queries

### Coverage Over Time
```promql
sonarcloud_coverage_percent{branch="main"}
```

### Quality Gate Pass Rate (7 days)
```promql
rate(quality_gate_passed_total{branch="main"}[7d]) / 
(rate(quality_gate_passed_total{branch="main"}[7d]) + rate(quality_gate_failed_total{branch="main"}[7d])) * 100
```

### Test Pass Rate
```promql
sum(pytest_tests_total{status="passed"}) / sum(pytest_tests_total) * 100
```

### Workflow Success Rate
```promql
rate(github_workflow_runs_total{status="success"}[7d]) / 
rate(github_workflow_runs_total[7d]) * 100
```

### Release Frequency (per month)
```promql
rate(release_deployments_total[30d]) * 30 * 24 * 3600
```

### Mean Time to Recovery (MTTR)
```promql
histogram_quantile(0.95, rate(github_workflow_duration_seconds{status="failure"}[7d]))
```

---

## Implementation Options

### Option 1: Prometheus Pushgateway (Recommended)

**Architecture:**
- GitHub Actions workflow pushes metrics to Pushgateway
- Prometheus scrapes from Pushgateway
- Grafana queries Prometheus

**Pros:**
- Simple integration (just HTTP POST)
- No Prometheus server in CI/CD
- Works well with ephemeral jobs

**Cons:**
- Pushgateway can become bottleneck
- Metrics need explicit cleanup

### Option 2: Custom Metrics Endpoint

**Architecture:**
- Workflow posts metrics to custom endpoint
- Endpoint stores in time-series DB (InfluxDB, TimescaleDB)
- Grafana queries directly

**Pros:**
- More control over storage
- Can handle high volume
- Direct integration

**Cons:**
- Requires custom infrastructure
- More complex setup

### Option 3: OpenTelemetry Collector

**Architecture:**
- Workflow emits OpenTelemetry metrics
- OTel Collector receives and exports to Prometheus
- Grafana queries Prometheus

**Pros:**
- Standard format (OpenTelemetry)
- Flexible export backends
- Industry standard

**Cons:**
- More complex setup
- Requires OTel infrastructure

---

## Recommended Metrics Priority

### Phase 1: Critical Metrics (Immediate)
1. ✅ `sonarcloud_coverage_percent` - Track coverage trends
2. ✅ `sonarcloud_bugs_total` - Monitor bug count
3. ✅ `sonarcloud_quality_gate_status` - Binary pass/fail
4. ✅ `pytest_tests_total` - Test count trends
5. ✅ `github_workflow_runs_total` - Workflow execution count

### Phase 2: Quality Metrics (High Value)
6. ✅ `sonarcloud_vulnerabilities_total` - Security tracking
7. ✅ `sonarcloud_code_smells_total` - Code quality
8. ✅ `sonarcloud_reliability_rating` - Rating trends
9. ✅ `pytest_duration_seconds` - Test performance
10. ✅ `github_workflow_duration_seconds` - CI/CD efficiency

### Phase 3: Advanced Metrics (Nice to Have)
11. ✅ `release_deployments_total` - Deployment frequency
12. ✅ `release_deployment_duration_seconds` - Time to deploy
13. ✅ `quality_gate_coverage_violation_total` - Threshold violations
14. ✅ DORA metrics (Lead time, MTTR, Change failure rate)

---

## Example Grafana Panels

### Quality Dashboard
- **Coverage Trend**: Line graph of `sonarcloud_coverage_percent` over time
- **Quality Gate Status**: Single stat showing current status
- **Bugs/Smells/Vulns**: Three single stats with thresholds
- **Ratings**: Gauge showing reliability/security/maintainability
- **Test Count**: Bar chart of tests over time

### CI/CD Dashboard
- **Workflow Success Rate**: Percentage gauge
- **Workflow Duration**: Histogram of execution times
- **Test Pass Rate**: Line graph
- **Release Frequency**: Counter over time
- **MTTR**: Single stat (mean time to recovery)

---

## Next Steps

1. **Choose implementation** (Pushgateway recommended for simplicity)
2. **Add metric export step** to `quality-metrics.yml` workflow
3. **Configure Prometheus** to scrape Pushgateway
4. **Create Grafana dashboards** using queries above
5. **Set up alerts** on critical thresholds (coverage < 80%, bugs > 0)

---

**Status:** Design document - Ready for implementation


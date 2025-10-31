# Prometheus Pushgateway Architecture Guide

**Purpose:** Understanding Pushgateway deployment model and multi-agent reporting architecture.

---

## Core Question: One Pushgateway or Many?

**Answer: One Pushgateway per Prometheus instance (recommended)**

**Why:**
- Pushgateway is designed to handle many jobs/instances
- Labels differentiate metrics from different sources
- Simpler architecture, easier management
- Prometheus scrapes one endpoint instead of many

---

## Standard Architecture: Centralized Pushgateway

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub Actions                        │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Workflow #1  │  │ Workflow #2  │  │ Workflow #N  │  │
│  │ (Agent A)    │  │ (Agent B)    │  │ (Agent Z)    │  │
│  │              │  │              │  │              │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                  │                  │          │
│         └──────────────────┼──────────────────┘          │
│                            │                             │
│         All push to same   │                             │
│         Pushgateway        │                             │
└────────────────────────────┼─────────────────────────────┘
                             │
                             │ HTTP PUT with metrics
                             │ Labels: job, instance, branch, version
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│              Prometheus Pushgateway                      │
│              (Single Instance)                           │
│                                                          │
│  Metrics grouped by:                                     │
│  - job=beast-mailbox-core                                │
│  - instance={version}-{commit}                           │
│  - branch=main                                           │
│  - version=0.4.5                                         │
│                                                          │
└───────────────────────────┬─────────────────────────────┘
                             │
                             │ Scrape (every 15s)
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│              Prometheus Server                           │
│                                                          │
│  All metrics stored with labels:                        │
│  - job: beast-mailbox-core                               │
│  - instance: 0.4.5-abc123                                │
│  - branch: main                                           │
│  - version: 0.4.5                                        │
│  - commit: abc123                                        │
│  - workflow_run_id: 123456                               │
└───────────────────────────┬─────────────────────────────┘
                             │
                             │ Query via PromQL
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│              Grafana Dashboard                           │
│                                                          │
│  Filter by labels:                                       │
│  - sonarcloud_coverage_percent{branch="main"}            │
│  - pytest_tests_total{branch="main",status="passed"}     │
│  - github_workflow_runs_total{workflow="SonarCloud"}    │
└─────────────────────────────────────────────────────────┘
```

---

## How Multiple Agents Workflows Work

### Single Pushgateway, Multiple Workflows

**All workflows push to the same Pushgateway with unique labels:**

```bash
# Workflow #1 (Agent A - beast-mailbox-core)
PUT /metrics/job/beast-mailbox-core/instance/0.4.5-abc123/branch/main/version/0.4.5
Labels: {
  job: "beast-mailbox-core",
  instance: "0.4.5-abc123",
  branch: "main",
  version: "0.4.5",
  commit: "abc123"
}

# Workflow #2 (Agent B - different project)
PUT /metrics/job/my-project/instance/1.2.3-def456/branch/main/version/1.2.3
Labels: {
  job: "my-project",
  instance: "1.2.3-def456",
  branch: "main",
  version: "1.2.3",
  commit: "def456"
}

# Workflow #3 (Agent A - same project, different branch)
PUT /metrics/job/beast-mailbox-core/instance/0.4.5-ghi789/branch/develop/version/0.4.5
Labels: {
  job: "beast-mailbox-core",
  instance: "0.4.5-ghi789",
  branch: "develop",
  version: "0.4.5",
  commit: "ghi789"
}
```

**Prometheus differentiates by labels:**
```promql
# Get metrics for beast-mailbox-core only
sonarcloud_coverage_percent{job="beast-mailbox-core"}

# Get metrics for main branch only
sonarcloud_coverage_percent{branch="main"}

# Get metrics for specific version
sonarcloud_coverage_percent{version="0.4.5"}

# Get metrics for specific workflow run
sonarcloud_coverage_percent{instance="0.4.5-abc123"}
```

---

## Deployment Model: Per-Host vs Per-Service

### ✅ Recommended: One Pushgateway Per Prometheus Instance

**Architecture:**
- **One Pushgateway** handles all services/projects
- **All workflows** push to the same Pushgateway
- **Labels** distinguish different sources
- **Prometheus** scrapes one Pushgateway endpoint

**Pros:**
- ✅ Simple architecture
- ✅ Easy to manage (one service to monitor)
- ✅ Handles high throughput (Pushgateway scales well)
- ✅ Single scrape target for Prometheus
- ✅ Labels provide full isolation

**Cons:**
- ⚠️ Single point of failure (mitigated by: metrics are ephemeral, can restart)
- ⚠️ All traffic to one endpoint (usually fine - Pushgateway handles this well)

---

### Alternative: Multiple Pushgateways (Usually Overkill)

**When to consider:**
- Very high volume (>10k metrics/sec)
- Need geographic distribution
- Strict isolation requirements
- Multi-tenant with separate Prometheus instances

**Architecture:**
```
┌─────────────────┐      ┌─────────────────┐
│  Service A      │      │  Service B      │
│  Workflows      │      │  Workflows       │
└────────┬────────┘      └────────┬─────────┘
         │                         │
         ▼                         ▼
┌─────────────────┐      ┌─────────────────┐
│  Pushgateway A   │      │  Pushgateway B   │
└────────┬─────────┘      └────────┬─────────┘
         │                         │
         ▼                         ▼
┌─────────────────┐      ┌─────────────────┐
│  Prometheus A    │      │  Prometheus B    │
└─────────────────┘      └─────────────────┘
```

**Pros:**
- ✅ Isolation between services
- ✅ Can scale horizontally
- ✅ Geographic distribution possible

**Cons:**
- ❌ More complex architecture
- ❌ Multiple services to manage
- ❌ Multiple scrape targets
- ❌ Usually unnecessary

**Recommendation:** Only if you have specific requirements (very high volume, strict isolation, multi-tenant).

---

## Label Strategy: How Multiple Agents Are Differentiated

### Current Implementation

**Our label hierarchy:**

```
job/beast-mailbox-core/instance/{version}-{commit}/branch/{branch}/version/{version}
```

**Labels in metrics:**
- `job`: "beast-mailbox-core" (identifies the service/project)
- `instance`: "{version}-{commit}" (unique per workflow run)
- `branch`: Git branch (main, develop, feature/*)
- `version`: Package version (0.4.5)
- `commit`: Git commit SHA (abc123)
- `workflow_run_id`: GitHub Actions run ID (optional)

### How Prometheus Uses Labels

**All metrics from same Pushgateway, differentiated by labels:**

```promql
# All metrics from beast-mailbox-core
sonarcloud_coverage_percent{job="beast-mailbox-core"}

# Metrics from main branch only
sonarcloud_coverage_percent{branch="main"}

# Metrics from specific version
sonarcloud_coverage_percent{version="0.4.5"}

# Latest metrics (by instance timestamp)
topk(1, sonarcloud_coverage_percent{branch="main"})

# Time series for branch over time
sonarcloud_coverage_percent{branch="main"}
```

---

## Scaling Considerations

### How Many Workflows Can One Pushgateway Handle?

**Pushgateway capacity:**
- **Throughput:** ~10k metrics/second (typical)
- **Memory:** ~128Mi RAM per 100k metrics
- **Storage:** In-memory (optional persistence to disk)

**Real-world example:**
- 100 workflows reporting every 5 minutes = ~20 workflows/minute
- 100 metrics per workflow = 2k metrics/minute = ~33 metrics/second
- ✅ Well within capacity

**For our use case:**
- ✅ Single Pushgateway is more than sufficient
- ✅ Handles multiple agents/projects easily
- ✅ No need for multiple Pushgateways

---

## Best Practices

### ✅ Recommended Setup

1. **One Pushgateway** per Prometheus instance
2. **All workflows** push to same Pushgateway
3. **Labels** provide differentiation:
   - `job`: Service/project name
   - `instance`: Unique per workflow run
   - `branch`: Git branch
   - `version`: Package version
   - Other labels as needed
4. **Prometheus scrapes** single Pushgateway endpoint
5. **Grafana filters** by labels

### ✅ Label Strategy

**Use labels for:**
- ✅ Service/project identification (`job`)
- ✅ Unique workflow run (`instance`)
- ✅ Branch tracking (`branch`)
- ✅ Version tracking (`version`)
- ✅ Commit tracking (`commit`)

**Don't use labels for:**
- ❌ Multiple Pushgateways (unnecessary complexity)
- ❌ High-cardinality data (causes performance issues)
- ❌ Frequently changing values (wastes storage)

---

## Example: Multiple Projects Using Same Pushgateway

**Setup:**
```yaml
# docker-compose.yml
services:
  pushgateway:
    image: prom/pushgateway:latest
    ports:
      - "9091:9091"
```

**Project A (beast-mailbox-core):**
```bash
# GitHub Actions workflow pushes to:
PUT /metrics/job/beast-mailbox-core/instance/0.4.5-abc123/branch/main/version/0.4.5
```

**Project B (my-other-service):**
```bash
# Different GitHub Actions workflow pushes to:
PUT /metrics/job/my-other-service/instance/1.0.0-def456/branch/main/version/1.0.0
```

**Prometheus scrape config (same for both):**
```yaml
scrape_configs:
  - job_name: 'pushgateway'
    honor_labels: true
    static_configs:
      - targets: ['pushgateway:9091']  # Same endpoint
```

**Query in Grafana:**
```promql
# Project A metrics
sonarcloud_coverage_percent{job="beast-mailbox-core"}

# Project B metrics
sonarcloud_coverage_percent{job="my-other-service"}

# All metrics
sonarcloud_coverage_percent
```

---

## Failure Scenarios

### What if Pushgateway Goes Down?

**Impact:**
- ⚠️ Metrics push fails (GitHub Actions workflow logs error)
- ⚠️ Prometheus stops receiving new metrics
- ✅ **Existing metrics in Prometheus remain** (until retention expires)
- ✅ **Grafana dashboards still work** (show historical data)

**Recovery:**
- ✅ Restart Pushgateway: `docker restart prometheus-pushgateway`
- ✅ Next workflow run pushes metrics again
- ✅ Prometheus resumes scraping

**Mitigation:**
- ✅ Pushgateway is stateless (can restart without data loss)
- ✅ Metrics are ephemeral (missed metrics are acceptable for CI/CD)
- ✅ Historical data preserved in Prometheus
- ⚠️ For high availability, could run multiple Pushgateways (usually unnecessary)

---

## Recommended Architecture Summary

**For Multiple Agents/Workflows:**

1. **Deploy:** One Pushgateway per Prometheus instance
2. **Configure:** All workflows push to same Pushgateway
3. **Label Strategy:** Use labels to differentiate:
   - `job`: Service/project name
   - `instance`: Unique per run
   - `branch`: Git branch
   - `version`: Package version
4. **Prometheus:** Scrapes single Pushgateway endpoint
5. **Grafana:** Filters by labels (`job`, `branch`, `version`)

**Result:**
- ✅ Simple architecture
- ✅ Handles unlimited agents/workflows
- ✅ Easy to manage
- ✅ Scales to hundreds of workflows
- ✅ Labels provide full isolation

---

---

## Real-World Example: Our Implementation

**Current Setup:**

```bash
# Script pushes to Pushgateway with labels:
PUSH_URL="${PUSHGATEWAY_URL}/metrics/job/beast-mailbox-core/instance/${VERSION}-${COMMIT}/branch/${BRANCH}/version/${VERSION}"

# Example URLs:
# PUT /metrics/job/beast-mailbox-core/instance/0.4.5-abc123/branch/main/version/0.4.5
# PUT /metrics/job/beast-mailbox-core/instance/0.4.6-def456/branch/develop/version/0.4.6
```

**Multiple workflow runs:**
- Each workflow run creates unique `instance` label
- Same `job` label for all runs (beast-mailbox-core)
- Different `branch`/`version`/`commit` labels
- Prometheus stores all with labels
- Grafana filters by branch/version

**Result:**
- ✅ All runs push to same Pushgateway
- ✅ Labels differentiate each run
- ✅ Can query by branch/version/commit
- ✅ Time series shows trends over time

---

**Status:** Standard architecture - One Pushgateway per Prometheus, labels differentiate sources


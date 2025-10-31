# Prometheus & Grafana Setup for Quality Metrics

**Purpose:** Guide for setting up Prometheus Pushgateway and Grafana dashboards to monitor quality metrics.

---

## Architecture

```
GitHub Actions Workflow
    ↓ (HTTP POST)
Prometheus Pushgateway
    ↓ (scrape)
Prometheus Server
    ↓ (query)
Grafana Dashboards
```

---

## Step 1: Prometheus Pushgateway

### Installation (Docker)

```bash
docker run -d \
  --name=prometheus-pushgateway \
  -p 9091:9091 \
  prom/pushgateway
```

### Configuration

Access Pushgateway UI: `http://localhost:9091`

### Prometheus Server Config

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'pushgateway'
    static_configs:
      - targets: ['pushgateway:9091']
    honor_labels: true  # Important: use labels from pushgateway
```

---

## Step 2: GitHub Secrets

Add to repository secrets:
- `PROMETHEUS_PUSHGATEWAY_URL`: Full URL (e.g., `http://pushgateway:9091`)

---

## Step 3: Workflow Integration

The `.github/workflows/prometheus-metrics.yml` workflow will:
1. Fetch metrics from SonarCloud
2. Generate Prometheus format metrics
3. Push to Pushgateway (if URL configured)
4. Save metrics as artifact (for manual inspection)

---

## Step 4: Grafana Dashboards

### Import Dashboard JSON

See `docs/grafana-dashboard-quality.json` (to be created)

### Key Panels

1. **Quality Overview**
   - Coverage trend (line graph)
   - Quality gate status (single stat)
   - Bugs/Vulns/Smells (stat panel)

2. **Test Metrics**
   - Test pass rate (gauge)
   - Test count over time (bar chart)
   - Test duration (histogram)

3. **CI/CD Performance**
   - Workflow success rate
   - Workflow duration
   - Release frequency

---

## Step 5: Alerts

### Prometheus Alert Rules

```yaml
groups:
  - name: quality_alerts
    rules:
      - alert: CoverageBelowThreshold
        expr: sonarcloud_coverage_percent < 80
        for: 5m
        annotations:
          summary: "Code coverage below 80%"
      
      - alert: BugsDetected
        expr: sonarcloud_bugs_total > 0
        for: 1m
        annotations:
          summary: "Bugs detected in code"
      
      - alert: QualityGateFailed
        expr: sonarcloud_quality_gate_status == 0
        for: 1m
        annotations:
          summary: "Quality gate failed"
```

---

## Metrics Available

See `docs/PROMETHEUS_METRICS_DESIGN.md` for complete metric list.

---

**Status:** Setup guide - Ready for implementation


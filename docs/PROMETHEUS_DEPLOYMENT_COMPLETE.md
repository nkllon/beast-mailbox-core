# Complete Prometheus/Grafana Deployment Guide

**Purpose:** Step-by-step guide to deploy dashboards and load data from GitHub Actions workflows.

---

## Architecture Flow

```
GitHub Actions Workflow
    ↓ (HTTP PUT with metrics)
Prometheus Pushgateway
    ↓ (scrape every 15s)
Prometheus Server
    ↓ (query via PromQL)
Grafana Dashboard
```

---

## Part 1: Data Flow Setup

### Step 1.1: Deploy Pushgateway

**Docker (Quickest):**
```bash
docker run -d \
  --name=prometheus-pushgateway \
  --network=prometheus-network \
  -p 9091:9091 \
  --restart=unless-stopped \
  prom/pushgateway:latest \
    --persistence.file=/tmp/pushgateway.db \
    --persistence.interval=5m
```

**Verify it's running:**
```bash
docker ps | grep pushgateway
curl http://localhost:9091/metrics
```

**Access Pushgateway UI:**
```
http://localhost:9091
```

---

### Step 1.2: Configure Prometheus to Scrape Pushgateway

**Edit `prometheus.yml`:**

```yaml
global:
  scrape_interval: 15s
  scrape_timeout: 10s

scrape_configs:
  # Existing configs...
  
  - job_name: 'pushgateway'
    honor_labels: true  # Critical: preserves labels from Pushgateway
    static_configs:
      - targets: 
        - 'pushgateway:9091'  # Docker network name
        # Or: '192.168.1.119:9091' (direct IP)
        # Or: 'prometheus-pushgateway.monitoring.svc.cluster.local:9091' (K8s)
    scrape_interval: 15s
    scrape_timeout: 10s
```

**Reload Prometheus:**

**Docker:**
```bash
docker restart prometheus
# Or reload via API:
curl -X POST http://prometheus:9090/-/reload
```

**Kubernetes:**
```bash
kubectl rollout restart deployment/prometheus -n monitoring
# Or if using ConfigMap:
kubectl apply -f prometheus-configmap.yaml
kubectl delete pod -n monitoring -l app=prometheus  # Force reload
```

**Verify Prometheus is scraping:**
1. Go to: `http://prometheus:9090/targets`
2. Find `pushgateway` job
3. Status should be: **UP** ✅

---

### Step 1.3: Configure GitHub Actions Secret

**Set Pushgateway URL:**

1. Go to: `https://github.com/nkllon/beast-mailbox-core/settings/secrets/actions`

2. Click **"New repository secret"**

3. Add:
   - **Name:** `PROMETHEUS_PUSHGATEWAY_URL`
   - **Value:** Your Pushgateway URL
     - **Docker network:** `http://pushgateway:9091`
     - **Direct IP:** `http://192.168.1.119:9091`
     - **Kubernetes:** `http://prometheus-pushgateway.monitoring.svc.cluster.local:9091`
     - **External/LoadBalancer:** `https://pushgateway.example.com`

4. **(Optional) If Pushgateway requires auth:**
   - **Name:** `PROMETHEUS_PUSHGATEWAY_AUTH`
   - **Value:** `username:password`

---

### Step 1.4: Trigger Workflow to Push Data

**Option A: Wait for next SonarCloud run**
- Metrics will automatically export after SonarCloud analysis completes

**Option B: Manually trigger**
```bash
# Push a commit to trigger SonarCloud workflow
git commit --allow-empty -m "trigger: Test Prometheus export"
git push origin main
```

**Option C: Test manually (development)**
```bash
# Set environment variables
export PROMETHEUS_PUSHGATEWAY_URL="http://pushgateway:9091"
export BRANCH="main"
export VERSION="0.4.5"
export COMMIT="abc123"
export WORKFLOW_RUN_ID="test-123"
export METRICS_FILE="/tmp/test_metrics.prom"

# Create test metrics file
cat > /tmp/test_metrics.prom <<EOF
# HELP test_coverage Test coverage metric
# TYPE test_coverage gauge
test_coverage{branch="main",version="0.4.5"} 89.5
EOF

# Push to Pushgateway
./scripts/push_metrics_to_prometheus.sh
```

---

### Step 1.5: Verify Data in Prometheus

**Check Pushgateway has data:**
1. Go to: `http://pushgateway:9091`
2. Should see metrics grouped by:
   - Job: `beast-mailbox-core`
   - Instance: `{version}-{commit}`
   - Labels: `branch`, `version`, `commit`

**Check Prometheus has scraped data:**
1. Go to: `http://prometheus:9090`
2. Query: `sonarcloud_coverage_percent`
3. Should see metrics with labels: `branch`, `version`, `commit`

**Available metrics to query:**
```promql
# Quality metrics
sonarcloud_coverage_percent
sonarcloud_bugs_total
sonarcloud_vulnerabilities_total
sonarcloud_code_smells_total
sonarcloud_quality_gate_status
sonarcloud_reliability_rating
sonarcloud_security_rating
sonarcloud_maintainability_rating

# Test metrics
pytest_tests_total{status="passed"}
pytest_tests_total{status="failed"}
pytest_duration_seconds
pytest_coverage_percent

# Workflow metrics
github_workflow_runs_total{status="success"}
github_workflow_duration_seconds
```

---

## Part 2: Grafana Dashboard Deployment

### Step 2.1: Configure Prometheus Data Source in Grafana

**Via Grafana UI:**
1. Go to: `http://grafana:3000`
2. Click: **⚙️ Configuration → Data Sources**
3. Click: **Add data source**
4. Select: **Prometheus**
5. Configure:
   - **URL:** `http://prometheus:9090` (or your Prometheus URL)
   - **Access:** Server (default)
6. Click: **Save & Test**
7. Should see: **"Data source is working"** ✅

**Via Grafana API:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  http://grafana:3000/api/datasources \
  -d '{
    "name": "Prometheus",
    "type": "prometheus",
    "url": "http://prometheus:9090",
    "access": "proxy",
    "isDefault": true
  }'
```

**Via Configuration File (if using Grafana in Docker/K8s):**
```yaml
# grafana/provisioning/datasources/prometheus.yml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
```

---

### Step 2.2: Import Dashboard JSON

**Option A: Via Grafana UI (Recommended)**

1. **Download dashboard JSON:**
   ```bash
   # From repository
   curl -O https://raw.githubusercontent.com/nkllon/beast-mailbox-core/main/docs/grafana-quality-dashboard.json
   
   # Or from local file
   cat docs/grafana-quality-dashboard.json
   ```

2. **Import into Grafana:**
   - Go to: `http://grafana:3000`
   - Click: **➕ Create → Import**
   - Option 1: **Upload JSON file**
     - Click **"Upload JSON file"**
     - Select `grafana-quality-dashboard.json`
   - Option 2: **Paste JSON**
     - Click **"Import via panel json"**
     - Paste contents of `docs/grafana-quality-dashboard.json`
   - Click: **Load**
   - Select: **Prometheus** data source
   - Click: **Import**

3. **Verify dashboard:**
   - Dashboard should appear with all panels
   - Check that panels show "No data" initially (normal if no metrics yet)

**Option B: Via Grafana API**

```bash
# Import dashboard
curl -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  http://grafana:3000/api/dashboards/db \
  -d @docs/grafana-quality-dashboard.json
```

**Option C: Via Provisioning (Docker/K8s)**

1. **Create dashboard provisioning directory:**
   ```bash
   mkdir -p grafana/provisioning/dashboards
   ```

2. **Copy dashboard JSON:**
   ```bash
   cp docs/grafana-quality-dashboard.json grafana/provisioning/dashboards/
   ```

3. **Create provisioning config:**
   ```yaml
   # grafana/provisioning/dashboards/dashboards.yml
   apiVersion: 1
   providers:
     - name: 'beast-mailbox-core'
       orgId: 1
       folder: ''
       type: file
       disableDeletion: false
       updateIntervalSeconds: 10
       allowUiUpdates: true
       options:
         path: /etc/grafana/provisioning/dashboards
   ```

4. **Mount in Docker:**
   ```yaml
   # docker-compose.yml
   services:
     grafana:
       volumes:
         - ./grafana/provisioning:/etc/grafana/provisioning
         - ./docs/grafana-quality-dashboard.json:/etc/grafana/provisioning/dashboards/quality.json
   ```

---

### Step 2.3: Configure Dashboard Variables

**Branch Selector:**

1. Open dashboard: **"Beast Mailbox Core - Quality Metrics"**
2. Click: **⚙️ Dashboard settings → Variables**
3. Verify `branch` variable:
   - **Name:** `branch`
   - **Type:** Query
   - **Query:** `label_values(sonarcloud_coverage_percent, branch)`
   - **Current value:** `main`
4. **Test query:**
   - Click: **Test**
   - Should see available branches (e.g., `main`, `develop`)

---

### Step 2.4: Verify Data in Dashboard

**Wait for data:**
- After workflow runs and pushes metrics, wait ~15-30 seconds for:
  1. GitHub Actions to push to Pushgateway
  2. Prometheus to scrape Pushgateway (every 15s)
  3. Grafana to refresh (default 30s)

**Check panels:**
1. **Coverage Trend:** Should show line graph with coverage %
2. **Quality Gate Status:** Should show ✅ or ❌
3. **Bugs/Vulns/Smells:** Should show counts
4. **Ratings:** Should show A/B/C/D
5. **Test Metrics:** Should show pass rate and counts

**If "No data" appears:**
- Check Prometheus has data: `http://prometheus:9090/graph?g0.expr=sonarcloud_coverage_percent`
- Check Pushgateway has data: `http://pushgateway:9091`
- Verify workflow pushed successfully (check GitHub Actions logs)
- Check Grafana data source connection

---

## Part 3: Data Refresh and Automation

### Step 3.1: Workflow Triggers

**Automatic (Default):**
- Workflow runs after **SonarCloud Analysis** completes
- Metrics are pushed automatically
- No manual intervention needed

**Workflow sequence:**
```
1. Code push/PR → SonarCloud Analysis workflow
2. SonarCloud completes → Quality Metrics Tracking workflow
3. Quality Metrics Tracking completes → Export Metrics to Prometheus workflow
4. Metrics pushed to Pushgateway
5. Prometheus scrapes (every 15s)
6. Grafana queries Prometheus (refresh every 30s)
```

---

### Step 3.2: Dashboard Refresh Settings

**Per-dashboard refresh:**
1. Open dashboard
2. Click: **⚙️ Dashboard settings → General**
3. Set: **Time range:** Last 7 days
4. Set: **Auto-refresh:** 30s (or your preference)

**Global Grafana refresh:**
- Edit `grafana.ini`:
  ```ini
  [dashboards]
  min_refresh_interval = 5s
  ```

---

### Step 3.3: Verify Continuous Data Flow

**Check workflow logs:**
1. Go to: `https://github.com/nkllon/beast-mailbox-core/actions`
2. Find: **"Export Metrics to Prometheus"** workflow
3. Click: Latest run
4. Check step: **"Push to Prometheus Pushgateway"**
5. Should see: **"✅ Metrics pushed successfully (HTTP 200)"**

**Check Pushgateway:**
```bash
# View all metrics
curl http://pushgateway:9091 | grep beast-mailbox-core

# Check specific metric
curl http://pushgateway:9091/metrics/job/beast-mailbox-core
```

**Check Prometheus:**
1. Query: `sonarcloud_coverage_percent{branch="main"}`
2. Should see time series data
3. Click: **"Graph"** tab to see trend

**Check Grafana:**
- Dashboard should show updated data within 30-60 seconds

---

## Troubleshooting

### No Data in Grafana

**1. Check Prometheus has data:**
```bash
# Query in Prometheus UI
sonarcloud_coverage_percent
```

**2. Check Grafana data source:**
- Settings → Data Sources → Prometheus → Test

**3. Check dashboard queries:**
- Edit panel → Query inspector
- Check if PromQL returns data

**4. Check time range:**
- Ensure dashboard time range covers metric timestamps

---

### No Data in Prometheus

**1. Check Pushgateway:**
```bash
curl http://pushgateway:9091/metrics | grep sonarcloud
```

**2. Check Prometheus targets:**
- `http://prometheus:9090/targets`
- Pushgateway should be **UP**

**3. Check scrape config:**
- Verify `honor_labels: true` is set
- Verify target URL is correct

---

### No Data in Pushgateway

**1. Check workflow logs:**
- GitHub Actions → Export Metrics to Prometheus
- Check for errors in "Push to Prometheus Pushgateway" step

**2. Check GitHub secret:**
- Verify `PROMETHEUS_PUSHGATEWAY_URL` is set correctly
- Verify URL is accessible from GitHub Actions

**3. Test manual push:**
```bash
export PROMETHEUS_PUSHGATEWAY_URL="http://pushgateway:9091"
./scripts/push_metrics_to_prometheus.sh
```

---

## Verification Checklist

### Data Flow ✅
- [ ] Pushgateway is running (`docker ps | grep pushgateway`)
- [ ] Prometheus is scraping Pushgateway (`/targets` shows UP)
- [ ] GitHub secret `PROMETHEUS_PUSHGATEWAY_URL` is configured
- [ ] Workflow runs after SonarCloud analysis
- [ ] Workflow pushes metrics successfully (check logs)
- [ ] Pushgateway shows metrics (`http://pushgateway:9091`)
- [ ] Prometheus has metrics (`sonarcloud_coverage_percent` query works)

### Dashboard ✅
- [ ] Prometheus data source configured in Grafana
- [ ] Dashboard JSON imported successfully
- [ ] Dashboard panels visible (may show "No data" initially)
- [ ] Data appears after workflow runs
- [ ] Branch selector works (if multiple branches)
- [ ] Refresh settings configured (30s recommended)

---

## Next Steps

- ✅ **Set up alerts** (see `docs/PROMETHEUS_SETUP.md` for alert rules)
- ✅ **Customize dashboard** (edit JSON and re-import)
- ✅ **Add more metrics** (extend workflow or dashboard)
- ✅ **Set up notifications** (Grafana alerting for quality gate failures)

---

---

## Quick Reference: Import Dashboard via UI

**Fastest way (Grafana UI):**

1. Open Grafana: `http://grafana:3000`
2. Click: **➕ Create → Import**
3. Paste this URL:
   ```
   https://raw.githubusercontent.com/nkllon/beast-mailbox-core/main/docs/grafana-quality-dashboard.json
   ```
4. Click: **Load**
5. Select: **Prometheus** data source
6. Click: **Import**
7. ✅ Dashboard ready!

---

**Status:** Complete deployment guide - Ready for production use


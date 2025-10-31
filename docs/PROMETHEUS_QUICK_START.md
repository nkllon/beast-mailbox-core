# Prometheus Pushgateway - Quick Start Guide

**Purpose:** Get Prometheus metrics export working in 5 minutes.

---

## Prerequisites

- ✅ Prometheus server running in your cluster
- ✅ Grafana configured (optional, for visualization)
- ✅ GitHub Actions repository access

---

## Step 1: Deploy Pushgateway (2 minutes)

### Option A: Docker (Quickest)

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

### Option B: Docker Compose

Add to your `docker-compose.yml`:

```yaml
services:
  pushgateway:
    image: prom/pushgateway:latest
    ports:
      - "9091:9091"
    networks:
      - prometheus-network
```

Run:
```bash
docker compose up -d pushgateway
```

### Option C: Kubernetes

```bash
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus-pushgateway
spec:
  replicas: 1
  selector:
    matchLabels:
      app: pushgateway
  template:
    metadata:
      labels:
        app: pushgateway
    spec:
      containers:
      - name: pushgateway
        image: prom/pushgateway:latest
        ports:
        - containerPort: 9091
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus-pushgateway
spec:
  selector:
    app: pushgateway
  ports:
  - port: 9091
    targetPort: 9091
EOF
```

---

## Step 2: Configure Prometheus (1 minute)

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'pushgateway'
    honor_labels: true  # Critical!
    static_configs:
      - targets: ['pushgateway:9091']  # Or your cluster URL/IP
    scrape_interval: 15s
```

Reload Prometheus:
```bash
# Docker
docker restart prometheus

# Kubernetes
kubectl rollout restart deployment/prometheus

# Or HTTP API
curl -X POST http://prometheus:9090/-/reload
```

---

## Step 3: Configure GitHub Secret (1 minute)

1. Go to: `https://github.com/nkllon/beast-mailbox-core/settings/secrets/actions`

2. Click "New repository secret"

3. Add:
   - **Name:** `PROMETHEUS_PUSHGATEWAY_URL`
   - **Value:** Your Pushgateway URL
     - Docker network: `http://pushgateway:9091`
     - Kubernetes: `http://prometheus-pushgateway.monitoring.svc.cluster.local:9091`
     - Direct IP: `http://192.168.1.119:9091`
     - External: `https://pushgateway.example.com`

4. (Optional) If Pushgateway requires auth:
   - **Name:** `PROMETHEUS_PUSHGATEWAY_AUTH`
   - **Value:** `username:password`

---

## Step 4: Verify (1 minute)

### Test Pushgateway is Running

```bash
# Check container
docker ps | grep pushgateway

# Or Kubernetes
kubectl get pods | grep pushgateway

# Test endpoint
curl http://pushgateway:9091/metrics
```

### Test Manual Push

```bash
echo 'test_metric 42' | \
  curl --data-binary @- \
  http://pushgateway:9091/metrics/job/test_job/instance/test123
```

### Check in Prometheus

1. Go to: `http://prometheus:9090`
2. Query: `test_metric`
3. Should see: `test_metric{job="test_job", instance="test123"} 42`

---

## Step 5: Import Grafana Dashboard

1. Open Grafana: `http://grafana:3000`

2. Go to: **Dashboards → Import**

3. Upload: `docs/grafana-quality-dashboard.json`

4. Select Prometheus data source

5. Click **Import**

---

## Verification Checklist

- [ ] Pushgateway is running (`docker ps | grep pushgateway`)
- [ ] Pushgateway is accessible (`curl http://pushgateway:9091/metrics`)
- [ ] Prometheus is scraping Pushgateway (check `/targets` in Prometheus UI)
- [ ] GitHub secret `PROMETHEUS_PUSHGATEWAY_URL` is configured
- [ ] Workflow runs after SonarCloud analysis
- [ ] Metrics appear in Prometheus (`sonarcloud_coverage_percent`)
- [ ] Grafana dashboard shows data (optional)

---

## Troubleshooting

### Pushgateway Not Accessible

```bash
# Check if running
docker ps | grep pushgateway

# Check logs
docker logs prometheus-pushgateway

# Test connectivity
curl -v http://pushgateway:9091/metrics
```

### Metrics Not in Prometheus

1. Check Prometheus targets: `http://prometheus:9090/targets`
   - Pushgateway should show as "UP"

2. Check Pushgateway UI: `http://pushgateway:9091`
   - Should show metrics with labels

3. Query in Prometheus:
   ```promql
   {__name__=~"sonarcloud_.*"}
   ```

### GitHub Workflow Not Pushing

1. Check workflow logs: `Actions → Export Metrics to Prometheus → Run details`

2. Verify secret is set:
   ```bash
   # In workflow logs, check if URL is present
   grep "PROMETHEUS_PUSHGATEWAY_URL" workflow.log
   ```

3. Test script manually:
   ```bash
   export PROMETHEUS_PUSHGATEWAY_URL="http://pushgateway:9091"
   ./scripts/push_metrics_to_prometheus.sh
   ```

---

## Next Steps

- ✅ Create alerts in Prometheus (see `docs/PROMETHEUS_SETUP.md`)
- ✅ Customize Grafana dashboard (see `docs/grafana-quality-dashboard.json`)
- ✅ Add more metrics (see `docs/PROMETHEUS_METRICS_DESIGN.md`)

---

## Reference

- **Full Setup Guide:** `docs/PROMETHEUS_CLUSTER_SETUP.md`
- **Metrics Design:** `docs/PROMETHEUS_METRICS_DESIGN.md`
- **Grafana Dashboard:** `docs/grafana-quality-dashboard.json`

---

**Status:** Ready for production use


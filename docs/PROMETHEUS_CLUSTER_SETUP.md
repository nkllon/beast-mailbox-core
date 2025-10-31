# Prometheus Pushgateway - Cluster Integration Guide

**Purpose:** Guide for integrating Prometheus Pushgateway with existing Grafana and Prometheus instances in the cluster.

---

## Architecture

```
GitHub Actions Workflow
    ↓ (HTTP PUT)
Prometheus Pushgateway (Cluster Service)
    ↓ (scrape)
Prometheus Server (Cluster)
    ↓ (query)
Grafana (Cluster)
```

---

## Step 1: Pushgateway Deployment

### Determine Cluster Type

Check your cluster type:

```bash
# Kubernetes
kubectl get nodes

# Docker Swarm
docker node ls

# Docker Compose
docker ps --format "{{.Names}}" | grep -E "prometheus|grafana"
```

---

## Step 2: Deployment Options

### Kubernetes Cluster

1. **Create Pushgateway Deployment:**

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus-pushgateway
  namespace: monitoring
  labels:
    app: pushgateway
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
        image: prom/pushgateway:v1.7.0
        ports:
        - containerPort: 9091
          name: http
        args:
          - '--persistence.file=/var/lib/pushgateway/pushgateway.db'
          - '--persistence.interval=5m'
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        volumeMounts:
        - name: data
          mountPath: /var/lib/pushgateway
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: pushgateway-data
---
apiVersion: v1
kind: Service
metadata:
  name: prometheus-pushgateway
  namespace: monitoring
  labels:
    app: pushgateway
spec:
  selector:
    app: pushgateway
  ports:
  - port: 9091
    targetPort: 9091
    name: http
  type: ClusterIP
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pushgateway-data
  namespace: monitoring
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

2. **Deploy:**
```bash
kubectl apply -f pushgateway-deployment.yaml
```

3. **Get Service URL:**
```bash
kubectl get svc -n monitoring prometheus-pushgateway
# Use: http://prometheus-pushgateway.monitoring.svc.cluster.local:9091
```

---

### Docker Compose Cluster

1. **Add to docker-compose.yml:**

```yaml
services:
  pushgateway:
    image: prom/pushgateway:v1.7.0
    container_name: prometheus-pushgateway
    ports:
      - "9091:9091"
    restart: unless-stopped
    volumes:
      - pushgateway_data:/var/lib/pushgateway
    command:
      - '--persistence.file=/var/lib/pushgateway/pushgateway.db'
      - '--persistence.interval=5m'
    networks:
      - prometheus-network
    labels:
      - "com.docker.compose.service=pushgateway"

volumes:
  pushgateway_data:
    driver: local

networks:
  prometheus-network:
    external: true  # Join existing Prometheus network
    # OR: name: prometheus-network
```

2. **Deploy:**
```bash
docker compose up -d pushgateway
```

3. **Service URL:**
- Within Docker network: `http://pushgateway:9091`
- External access: `http://localhost:9091` or `http://<host-ip>:9091`

---

### Standalone Docker (for Testing)

```bash
docker run -d \
  --name=prometheus-pushgateway \
  --network=prometheus-network \
  -p 9091:9091 \
  --restart=unless-stopped \
  prom/pushgateway:v1.7.0 \
    --persistence.file=/var/lib/pushgateway/pushgateway.db \
    --persistence.interval=5m
```

---

## Step 3: Configure Prometheus to Scrape Pushgateway

### Update Prometheus Configuration

Add to your Prometheus config (`prometheus.yml` or ConfigMap):

```yaml
scrape_configs:
  # Existing scrape configs...
  
  - job_name: 'pushgateway'
    honor_labels: true  # Critical: preserve labels from pushgateway
    static_configs:
      - targets: 
        # Kubernetes:
        - 'prometheus-pushgateway.monitoring.svc.cluster.local:9091'
        # Docker Compose:
        - 'pushgateway:9091'
        # Direct IP (fallback):
        - '192.168.1.119:9091'
    scrape_interval: 15s
    scrape_timeout: 10s
```

### Reload Prometheus

**Kubernetes:**
```bash
# If using ConfigMap, update and restart
kubectl rollout restart deployment/prometheus -n monitoring

# Or reload via HTTP API
curl -X POST http://prometheus:9090/-/reload
```

**Docker:**
```bash
docker restart prometheus
```

---

## Step 4: Configure GitHub Secrets

### Required Secrets

1. Go to: `https://github.com/nkllon/beast-mailbox-core/settings/secrets/actions`

2. Add secrets:

**`PROMETHEUS_PUSHGATEWAY_URL`** (required):
- Kubernetes (internal): `http://prometheus-pushgateway.monitoring.svc.cluster.local:9091`
- Docker Compose: `http://pushgateway:9091`
- External: `http://your-cluster-ip:9091`
- If accessible via LoadBalancer/Ingress: `https://pushgateway.example.com`

**`PROMETHEUS_PUSHGATEWAY_AUTH`** (optional, if authentication required):
- Format: `username:password`
- Example: `metrics:secret-password`

---

## Step 5: Network Access

### Verify Connectivity

From GitHub Actions (or cluster network):

```bash
# Test Pushgateway is accessible
curl -v http://pushgateway:9091/metrics

# Test pushing metrics
echo 'test_metric 42' | curl --data-binary @- http://pushgateway:9091/metrics/job/test_job
```

### Firewall/Network Configuration

**If GitHub Actions can't reach Pushgateway directly:**

1. **Option A: Ingress/LoadBalancer**
   - Expose Pushgateway via Ingress or LoadBalancer
   - Use public URL in `PROMETHEUS_PUSHGATEWAY_URL`

2. **Option B: VPN/Tunnel**
   - Set up VPN or tunnel for GitHub Actions
   - Use internal cluster URL

3. **Option C: Reverse Proxy**
   - Proxy Pushgateway through existing service
   - Update URL accordingly

---

## Step 6: Test Integration

### Manual Test Push

```bash
# From cluster or GitHub Actions
curl -X PUT \
  --data-binary @- \
  "http://pushgateway:9091/metrics/job/beast-mailbox-core/instance/test-123/branch/main/version/0.4.4" <<EOF
# HELP test_metric Example metric
# TYPE test_metric gauge
test_metric{branch="main",version="0.4.4"} 42
EOF
```

### Verify in Prometheus

1. Go to Prometheus UI: `http://prometheus:9090`
2. Query: `test_metric`
3. Should see value: `42`

### Verify in Grafana

1. Add Prometheus data source (if not already)
2. Create test panel with query: `test_metric`
3. Should display metric

---

## Step 7: Grafana Dashboard Import

### Create Dashboard

Use queries from `docs/PROMETHEUS_METRICS_DESIGN.md`:

**Example Queries:**

```promql
# Coverage Trend
sonarcloud_coverage_percent{branch="main"}

# Quality Gate Status
sonarcloud_quality_gate_status{branch="main"}

# Test Pass Rate
sum(pytest_tests_total{branch="main",status="passed"}) / 
sum(pytest_tests_total{branch="main"}) * 100

# Workflow Success Rate
rate(github_workflow_runs_total{status="success"}[7d]) / 
rate(github_workflow_runs_total[7d]) * 100
```

### Dashboard JSON

See `docs/grafana-quality-dashboard.json` (to be created)

---

## Troubleshooting

### Pushgateway Not Accessible

```bash
# Check Pushgateway is running
kubectl get pods -n monitoring | grep pushgateway
docker ps | grep pushgateway

# Check service
kubectl get svc -n monitoring prometheus-pushgateway
docker ps | grep pushgateway

# Test connectivity
curl http://pushgateway:9091/metrics
```

### Metrics Not Appearing in Prometheus

1. **Check Prometheus targets:**
   ```
   http://prometheus:9090/targets
   ```
   - Pushgateway should show as "UP"

2. **Check labels:**
   ```promql
   {__name__=~"sonarcloud_.*"}
   ```

3. **Check Pushgateway UI:**
   ```
   http://pushgateway:9091
   ```
   - Should show metrics with labels

### Authentication Issues

If Pushgateway requires auth:

1. **Enable Basic Auth in Pushgateway** (requires custom image or proxy)
2. **Or use API key in URL:**
   ```
   http://api-key@pushgateway:9091
   ```

---

## Security Considerations

1. **Authentication:** Enable auth if Pushgateway is exposed
2. **Network Isolation:** Use internal cluster URLs when possible
3. **Rate Limiting:** Consider rate limits if high-volume
4. **Data Retention:** Configure Pushgateway persistence

---

## Monitoring Pushgateway Itself

Add to Prometheus scrape config:

```yaml
- job_name: 'pushgateway-metrics'
  static_configs:
    - targets: ['pushgateway:9091']
  metrics_path: '/metrics'  # Pushgateway's own metrics
```

---

**Status:** Ready for cluster deployment


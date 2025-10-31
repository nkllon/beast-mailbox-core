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

### Installation Options

#### Option 1: Docker (Standalone)

```bash
docker run -d \
  --name=prometheus-pushgateway \
  -p 9091:9091 \
  --restart=unless-stopped \
  prom/pushgateway:latest
```

#### Option 2: Docker Compose (Recommended for Cluster)

```yaml
version: '3.8'
services:
  pushgateway:
    image: prom/pushgateway:latest
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

volumes:
  pushgateway_data:

networks:
  prometheus-network:
    driver: bridge
```

#### Option 3: Kubernetes (if cluster is K8s)

```yaml
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
          name: http
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
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
    name: http
  type: ClusterIP
```

### Configuration

Access Pushgateway UI: `http://localhost:9091`

### Prometheus Server Config

Add to `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'pushgateway'
    honor_labels: true  # Important: use labels from pushgateway
    static_configs:
      - targets: ['pushgateway:9091']  # Adjust to your cluster DNS/IP
    scrape_interval: 15s
    scrape_timeout: 10s
```

**Cluster-Specific Configuration:**

For internal cluster (service discovery):
```yaml
scrape_configs:
  - job_name: 'pushgateway'
    honor_labels: true
    kubernetes_sd_configs:  # If using K8s service discovery
      - role: service
    relabel_configs:
      - source_labels: [__meta_kubernetes_service_name]
        regex: prometheus-pushgateway
        action: keep
```

For Docker network:
```yaml
scrape_configs:
  - job_name: 'pushgateway'
    honor_labels: true
    static_configs:
      - targets: ['pushgateway:9091']  # Docker service name
```

For direct IP:
```yaml
scrape_configs:
  - job_name: 'pushgateway'
    honor_labels: true
    static_configs:
      - targets: ['192.168.1.119:9091']  # Direct IP address
```

---

## Step 2: GitHub Secrets

Add to repository secrets:

**Required:**
- `PROMETHEUS_PUSHGATEWAY_URL`: Full URL to Pushgateway endpoint
  - Example: `http://pushgateway:9091` (internal cluster URL)
  - Example: `https://pushgateway.example.com` (public URL)
  - Example: `http://192.168.1.119:9091` (direct IP)

**Optional (if authentication required):**
- `PROMETHEUS_PUSHGATEWAY_AUTH`: Basic auth credentials
  - Format: `username:password`
  - Example: `metrics_user:metrics_password`

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


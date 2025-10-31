# Observatory Local Setup - Herbert

**Status:** ✅ Working  
**Date:** 2025-10-31  
**Stack:** Prometheus + Grafana + Pushgateway

---

## Quick Start

### 1. Start Stack

```bash
cd observatory
./scripts/setup_local.sh
```

**Services start on:**
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)
- Pushgateway: http://localhost:9091

### 2. Test Stack

```bash
./scripts/test_stack.sh
```

### 3. Verify Services

**Prometheus:**
```bash
curl http://localhost:9090/api/v1/status/config
```

**Grafana:**
```bash
curl http://localhost:3000/api/health
```

**Pushgateway:**
```bash
curl http://localhost:9091/metrics
```

---

## Service Configuration

### Prometheus

**Config:** `configs/prometheus/prometheus.yml`

**Scrapes:**
- Self (localhost:9090)
- Pushgateway (pushgateway:9091)
- Grafana (grafana:3000)

**Data Retention:** 30 days

### Grafana

**Default Credentials:** admin/admin

**Auto-Configured:**
- Prometheus datasource (http://prometheus:9090)
- Dashboard provisioning ready

**Data:** Persistent volume (`grafana_data`)

### Pushgateway

**Endpoint:** http://localhost:9091

**Persistence:** `/var/lib/pushgateway/pushgateway.db` (every 5 minutes)

**Usage:**
```bash
echo 'test_metric 42' | \
  curl --data-binary @- \
  http://localhost:9091/metrics/job/beast-mailbox-core/instance/test/branch/main
```

---

## Docker Compose

**File:** `docker/docker-compose.yml`

**Services:**
- `prometheus` - Metrics storage and querying
- `grafana` - Visualization dashboards
- `pushgateway` - Metrics gateway for push-based metrics

**Networks:**
- `observatory-network` (bridge)

**Volumes:**
- `prometheus_data` - Prometheus TSDB
- `grafana_data` - Grafana database and dashboards
- `pushgateway_data` - Pushgateway persistence

---

## Management

### Start Stack
```bash
cd docker
docker compose up -d
```

### Stop Stack
```bash
cd docker
docker compose down
```

### View Logs
```bash
cd docker
docker compose logs -f
```

### Restart Service
```bash
cd docker
docker compose restart prometheus
```

### Check Status
```bash
cd docker
docker compose ps
```

---

## Integration with beast-mailbox-core

**To push metrics from GitHub Actions:**

1. **Set GitHub Secret:**
   - Name: `PROMETHEUS_PUSHGATEWAY_URL`
   - Value: `http://localhost:9091` (for local) or your Pushgateway URL

2. **Workflow automatically pushes** after SonarCloud analysis

3. **Prometheus scrapes** from Pushgateway (every 15s)

4. **Grafana visualizes** via Prometheus datasource

---

## Troubleshooting

### Services Not Starting

```bash
# Check Docker logs
cd docker
docker compose logs

# Check service health
docker compose ps
```

### Prometheus Not Scraping Pushgateway

```bash
# Check targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.job=="pushgateway")'

# Check Pushgateway is accessible
docker exec prometheus wget -qO- http://pushgateway:9091/metrics | head -5
```

### Grafana Can't Connect to Prometheus

```bash
# Verify Prometheus is accessible
docker exec grafana wget -qO- http://prometheus:9090/api/v1/status/config

# Check datasource config
cat configs/grafana/provisioning/datasources/prometheus.yml
```

---

## Next Steps

1. ✅ Stack running locally
2. ⏳ Verify full integration (metrics flow)
3. ⏳ Add Grafana dashboards
4. ⏳ Package for separate repo

---

**Status:** ✅ Working - All services operational


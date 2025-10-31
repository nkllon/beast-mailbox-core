# SonarCloud Data Retention & Historical Metrics

**Purpose:** Understand SonarCloud's data retention and how to access historical metrics.

---

## SonarCloud Data Retention

### Current Understanding

**SonarCloud retains:**
- ✅ **Full history** for all metrics (no time limit stated publicly)
- ✅ **All analysis runs** with timestamps
- ✅ **Quality gate history** per analysis
- ✅ **Metric trends** over time

**Key Questions:**
1. How long does SonarCloud retain historical data?
2. Can we query historical metrics via API?
3. Should we rely on SonarCloud or Prometheus for long-term storage?

---

## SonarCloud API Capabilities

### 1. Current Metrics (What We're Using)

**Endpoint:** `/api/measures/component`
- ✅ Gets **current** metrics values
- ✅ Real-time snapshot
- ❌ No historical data

**Example:**
```bash
curl "https://sonarcloud.io/api/measures/component?component=nkllon_beast-mailbox-core&metricKeys=coverage,bugs"
```

### 2. Historical Metrics Search (Available)

**Endpoint:** `/api/measures/search_history`
- ✅ Gets **historical values** for metrics
- ✅ Can specify date ranges
- ✅ Returns time series data

**Example:**
```bash
curl "https://sonarcloud.io/api/measures/search_history?component=nkllon_beast-mailbox-core&metrics=coverage&ps=100"
```

**Returns:**
```json
{
  "measures": [
    {
      "metric": "coverage",
      "history": [
        {"date": "2025-01-31T14:00:00+0000", "value": "89.5"},
        {"date": "2025-01-30T14:00:00+0000", "value": "88.2"},
        ...
      ]
    }
  ]
}
```

### 3. Project Analyses (Analysis Runs)

**Endpoint:** `/api/project_analyses/search`
- ✅ Lists all analysis runs with dates
- ✅ Includes quality gate results per analysis
- ✅ Can get metrics per analysis

**Example:**
```bash
curl "https://sonarcloud.io/api/project_analyses/search?project=nkllon_beast-mailbox-core&ps=100"
```

---

## Retention Comparison

### SonarCloud vs Prometheus

| Aspect | SonarCloud | Prometheus (Our Config) |
|--------|------------|------------------------|
| **Retention** | **Unlimited** (as far as we know) | **30 days** (configured) |
| **Historical Access** | ✅ Full history via API | ✅ Limited to retention period |
| **Query Interface** | REST API | PromQL |
| **Data Export** | Via API | Native Prometheus format |
| **Cost** | Free for open source | Free (self-hosted) |

**Recommendation:**
- ✅ **Use SonarCloud as source of truth** for historical data
- ✅ **Use Prometheus for real-time visualization** and recent trends
- ✅ **Query SonarCloud API** for historical data when needed
- ✅ **Push recent data to Prometheus** for dashboards

---

## Hybrid Approach: Best of Both Worlds

### Strategy

1. **Real-time (Last 30 days):**
   - Push metrics to Prometheus via Pushgateway
   - Use Prometheus for Grafana dashboards
   - Fast queries, real-time updates

2. **Historical (Beyond 30 days):**
   - Query SonarCloud API for historical data
   - Import into Grafana as needed
   - SonarCloud as authoritative source

3. **Backup/Archive:**
   - Keep Prometheus data as cache
   - SonarCloud API as backup
   - Can query both sources

---

## Implementation Options

### Option 1: Query SonarCloud Historical API (Recommended)

**Advantages:**
- ✅ Unlimited history (SonarCloud retains all)
- ✅ No need to store long-term in Prometheus
- ✅ Always current data
- ✅ Single source of truth

**Disadvantages:**
- ⚠️ API rate limits (if any)
- ⚠️ Requires SonarCloud API access

**Implementation:**
```python
import requests

def get_historical_metrics(project_key, metric, days=30):
    """Query SonarCloud for historical metrics."""
    url = "https://sonarcloud.io/api/measures/search_history"
    params = {
        "component": project_key,
        "metrics": metric,
        "ps": 100  # Page size
    }
    response = requests.get(url, params=params)
    return response.json()
```

### Option 2: Sync SonarCloud → Prometheus Periodically

**Advantages:**
- ✅ Local data, faster queries
- ✅ Works offline
- ✅ Can extend Prometheus retention

**Disadvantages:**
- ⚠️ Need to manage data sync
- ⚠️ Still limited by Prometheus retention (or storage)

**Implementation:**
- Cron job to query SonarCloud API
- Push historical data to Pushgateway
- Prometheus scrapes and stores

### Option 3: Query SonarCloud On-Demand

**Advantages:**
- ✅ Always fresh data
- ✅ No storage needed
- ✅ Unlimited history

**Disadvantages:**
- ⚠️ Slower (API calls)
- ⚠️ Rate limits

**Implementation:**
- Grafana datasource plugin for SonarCloud
- Or custom Grafana panel that queries SonarCloud API directly

---

## Recommendation

**Use SonarCloud API for historical data:**

1. **Grafana Dashboard:**
   - **Recent data (last 30 days):** Query Prometheus
   - **Historical data (older):** Query SonarCloud API via custom panel

2. **Workflow:**
   - GitHub Actions pushes current metrics to Prometheus (existing workflow)
   - Grafana queries Prometheus for recent data
   - For historical views, Grafana queries SonarCloud API

3. **Benefits:**
   - ✅ No need to extend Prometheus retention
   - ✅ Always accurate (SonarCloud is source of truth)
   - ✅ Unlimited history
   - ✅ Faster Prometheus queries for recent data

---

## Next Steps

1. **Verify SonarCloud API access:**
   ```bash
   curl "https://sonarcloud.io/api/measures/search_history?component=nkllon_beast-mailbox-core&metrics=coverage&ps=10"
   ```

2. **Create Grafana datasource plugin** or custom panel for SonarCloud API

3. **Update workflow** to optionally query historical data from SonarCloud

4. **Document retention policy** once confirmed

---

## Questions to Answer

1. **SonarCloud retention period?** (Need to verify - likely unlimited for public projects)
2. **API rate limits?** (Check SonarCloud documentation)
3. **Best approach for Grafana?** (Plugin vs custom panel vs Prometheus scrape)

---

**Status:** Research phase - Need to verify SonarCloud retention policy


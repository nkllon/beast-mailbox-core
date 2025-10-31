# Strategy: SonarCloud vs Prometheus for Historical Data

**Key Insight:** SonarCloud API provides historical data, but with progressive thinning. We should use both strategically.

---

## SonarCloud Retention Policy (Verified)

**Progressive Retention:**
- **Day 1:** All snapshots retained
- **After 1 day:** 1 snapshot per day
- **After 1 week:** 1 snapshot per week  
- **After 4 weeks:** 1 snapshot every 4 weeks
- **After 2 years:** Only snapshots with version events
- **After 5 years:** All snapshots deleted

**Current Data Available:**
- ✅ 4 historical values for coverage/bugs (Oct 10-14, 2025)
- ✅ Analysis runs with dates available
- ✅ Historical API works: `/api/measures/search_history`

---

## Recommended Strategy

### 1. **Recent Data (Last 30 Days): Use Prometheus**
- ✅ **Fast queries** (local, optimized)
- ✅ **Real-time updates** (via Pushgateway)
- ✅ **Full granularity** (every workflow run)
- ✅ **30-day retention** matches our Prometheus config

### 2. **Historical Data (Beyond 30 Days): Query SonarCloud API**
- ✅ **Available now** - API works
- ✅ **Progressive thinning** - but data exists
- ✅ **No storage cost** - SonarCloud stores it
- ✅ **Always accurate** - Single source of truth

### 3. **Best of Both Worlds:**
- **Grafana Dashboard:**
  - **Recent (0-30 days):** Query Prometheus (fast)
  - **Historical (30+ days):** Query SonarCloud API (when needed)
- **Workflow:**
  - Push current metrics to Prometheus (existing)
  - Query SonarCloud for historical views (as needed)

---

## Implementation

### Option 1: Dual Grafana Queries (Recommended)

**Grafana Panel:**
```promql
# Recent data from Prometheus
sonarcloud_coverage_percent{branch="main"}

# Historical data via SonarCloud API datasource (if plugin exists)
# Or custom panel that queries SonarCloud API directly
```

### Option 2: Backfill Historical Data to Prometheus

**One-time script:**
```bash
# Query SonarCloud historical API
# Push to Prometheus Pushgateway
# Prometheus scrapes and stores

# This backfills up to 30 days (Prometheus retention)
# Beyond 30 days, query SonarCloud API
```

### Option 3: Hybrid Grafana Dashboard

**Two panels:**
1. **Recent Trends** (last 30 days) - Prometheus query
2. **Historical Trends** (all time) - SonarCloud API query (custom panel)

---

## Current Status

**SonarCloud API:**
- ✅ Historical endpoint works: `/api/measures/search_history`
- ✅ Returns time series data with dates and values
- ✅ Available for all metrics (coverage, bugs, smells, etc.)

**Prometheus:**
- ✅ Current metrics pushed successfully
- ✅ 30-day retention configured
- ✅ Scraping Pushgateway working

**Recommendation:**
- ✅ **Use Prometheus for recent data** (real-time, fast)
- ✅ **Query SonarCloud API for historical data** (when needed)
- ✅ **No need to extend Prometheus retention** beyond 30 days
- ✅ **SonarCloud is backup** if Prometheus data lost

---

## Next Steps

1. **Verify SonarCloud API retention** for our project (currently has 4 data points)
2. **Create Grafana plugin** or custom panel for SonarCloud API
3. **Update workflow** to optionally backfill recent historical data
4. **Document** which data source to use when

---

**Status:** Strategy defined - Use both sources strategically


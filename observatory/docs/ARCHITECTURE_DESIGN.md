# Observatory Architecture Design

**Status:** Design Phase  
**Date:** 2025-10-31

---

## Core Principle

**SonarCloud = Source of Truth**
- Pull historical data periodically
- Combine with real-time event feeds (GitHub Actions → Pushgateway)
- Periodic sync ensures we have data even if real-time feeds miss

---

## Architecture Proposal

### 1. Data Flow

```
┌─────────────────────────────────────────┐
│         SonarCloud (Source of Truth)    │
│                                         │
│  - Historical metrics                   │
│  - Progressive retention (thinning)     │
│  - API: /api/measures/search_history   │
└──────────────┬──────────────────────────┘
               │
               │ Periodic Sync (e.g., hourly)
               │
               ▼
┌─────────────────────────────────────────┐
│      Sync Service (beast-observatory)   │
│                                         │
│  - Queries SonarCloud API               │
│  - Backfills historical data            │
│  - Pushes to Pushgateway                │
└──────────────┬──────────────────────────┘
               │
               │ Real-time events
               │
               ▼
┌─────────────────────────────────────────┐
│      GitHub Actions Workflows           │
│                                         │
│  - After SonarCloud analysis            │
│  - Pushes current metrics               │
│  - Immediate, event-driven              │
└──────────────┬──────────────────────────┘
               │
               │ Both feed into:
               │
               ▼
┌─────────────────────────────────────────┐
│      Prometheus Pushgateway             │
│                                         │
│  - Accepts pushes from:                 │
│    • Periodic sync (historical)         │
│    • Real-time events (current)         │
└──────────────┬──────────────────────────┘
               │
               │ Scrapes
               │
               ▼
┌─────────────────────────────────────────┐
│      Prometheus                         │
│                                         │
│  - 30-day retention                     │
│  - Fast queries                         │
│  - Real-time data                       │
└──────────────┬──────────────────────────┘
               │
               │ Queries
               │
               ▼
┌─────────────────────────────────────────┐
│      Grafana                             │
│                                         │
│  - Visualizes Prometheus data           │
│  - Historical + Real-time               │
└─────────────────────────────────────────┘
```

---

## Design Decisions

### 1. Periodic Sync from SonarCloud

**Why:**
- ✅ Ensures we have data even if real-time feeds miss
- ✅ Backfills historical data into Prometheus
- ✅ SonarCloud is source of truth
- ✅ Handles workflow failures gracefully

**How:**
- Sync service queries SonarCloud API periodically (e.g., hourly)
- Gets recent historical data
- Pushes to Pushgateway with same label format
- Prometheus scrapes and stores

**Concerns Addressed:**
- ✅ What if GitHub Actions workflow fails? → Sync service still provides data
- ✅ What if Pushgateway is down? → Next sync will backfill
- ✅ What if Prometheus restarts? → Sync service backfills recent data

---

### 2. Redis Mailbox for Decoupling

**Question:** Should we use Redis mailbox (beast-mailbox-core) to decouple components?

**Analysis:**

**Services Are Co-Located:**
- Prometheus, Grafana, Pushgateway on same host/stack
- If host is down, all are down (single point of failure)
- Mailbox doesn't help with host failure

**When Mailbox Helps:**
- ✅ **Service isolation:** If one service crashes, others continue
- ✅ **Async operations:** Sync service can queue work
- ✅ **Rate limiting:** Handle SonarCloud API rate limits gracefully
- ✅ **Retry logic:** Failed syncs can be retried via queue
- ✅ **Decoupling:** Sync service independent of Prometheus availability

**When Mailbox Doesn't Help:**
- ❌ **Host failure:** If box is down, mailbox is down too
- ❌ **Network partition:** If host isolated, mailbox isolated
- ❌ **Power/internet:** External dependencies affect all

**Recommendation:**
- ✅ **Use Redis mailbox** for async sync operations
- ✅ **Decouples sync service** from Prometheus availability
- ✅ **Enables retry logic** and queuing
- ✅ **Handles rate limits** gracefully
- ⚠️ **Doesn't solve HA** (that needs multiple hosts)

---

## HA Strategy

### Current Reality
- **Single host:** If host down, all services down
- **Co-located services:** Prometheus, Grafana, Pushgateway together
- **All-or-nothing:** Box failure = complete outage

### Proposed HA Strategy

**Phase 1: Local HA (Two Machines)**
- **Machine 1:** Production Observatory stack
- **Machine 2:** Development OR HA standby
- **Benefits:**
  - ✅ Prod/Dev separation
  - ✅ Manual failover available
  - ✅ Reduces single-point-of-failure

**Phase 2: Cloud Third Leg**
- **Machine 3:** Cloud-based Observatory (e.g., AWS, GCP, Azure)
- **Benefits:**
  - ✅ Geographic redundancy
  - ✅ Internet outage tolerance
  - ✅ Power outage tolerance
  - ✅ True 99.999% availability

**Limitations:**
- ⚠️ **Shared dependencies:** If SonarCloud down, all instances affected
- ⚠️ **Shared source:** If GitHub Actions fail, all miss real-time data
- ✅ **But:** Periodic sync provides backup data

---

## Component Decoupling via Redis Mailbox

### Proposed Architecture

```
┌─────────────────────────────────────────┐
│      Sync Service (beast-observatory)   │
│                                         │
│  - Queries SonarCloud API               │
│  - Publishes metrics to mailbox         │
│  - Independent of Prometheus status      │
└──────────────┬──────────────────────────┘
               │
               │ Publishes to:
               │ beast:observatory:metrics
               │
               ▼
┌─────────────────────────────────────────┐
│      Redis Mailbox (beast-mailbox-core) │
│                                         │
│  - Queue: beast:observatory:metrics     │
│  - Handles rate limits                  │
│  - Retry logic                          │
│  - Decouples sync from consumers        │
└──────────────┬──────────────────────────┘
               │
               │ Consumer:
               │
               ▼
┌─────────────────────────────────────────┐
│      Metrics Consumer                    │
│                                         │
│  - Subscribes to mailbox                 │
│  - Consumes metrics                      │
│  - Pushes to Pushgateway                 │
│  - Independent of sync service          │
└──────────────┬──────────────────────────┘
               │
               │ Pushes to:
               │
               ▼
┌─────────────────────────────────────────┐
│      Prometheus Pushgateway             │
└─────────────────────────────────────────┘
```

**Benefits:**
- ✅ **Decoupling:** Sync service doesn't care if Prometheus is down
- ✅ **Reliability:** Metrics queued, consumed when Prometheus available
- ✅ **Retry:** Failed pushes can be retried
- ✅ **Rate limiting:** Handle SonarCloud API limits gracefully

**Trade-offs:**
- ⚠️ **Added complexity:** Redis mailbox layer
- ⚠️ **Still co-located:** If host down, Redis down too
- ✅ **But:** Better isolation between components

---

## Recommendations

### 1. Periodic Sync Strategy ✅

**Implement:**
- Sync service queries SonarCloud API hourly
- Backfills last 30 days into Prometheus
- Handles real-time feed gaps
- SonarCloud as source of truth

**Benefits:**
- ✅ Resilient to workflow failures
- ✅ Ensures data completeness
- ✅ Handles Prometheus restarts

### 2. Redis Mailbox for Decoupling ✅

**Implement:**
- Use Redis mailbox (beast-mailbox-core) for async operations
- Sync service publishes to mailbox
- Consumer pulls from mailbox and pushes to Pushgateway
- Decouples sync service from Prometheus availability

**Benefits:**
- ✅ Component isolation
- ✅ Retry logic built-in
- ✅ Rate limit handling
- ✅ Async processing

**Note:** Doesn't solve HA (needs multiple hosts), but improves reliability

### 3. HA Strategy ✅

**Phase 1 (Now):**
- Two local machines (prod + dev/HA)
- Manual failover
- Reduces single-point-of-failure

**Phase 2 (Future):**
- Add cloud third leg
- Geographic redundancy
- True 99.999% availability

**Limitations:**
- ⚠️ Shared dependencies (SonarCloud, GitHub Actions)
- ✅ But periodic sync provides backup

---

## Implementation Plan

### Phase 1: Periodic Sync Service

1. **Create sync service:**
   - Queries SonarCloud API `/api/measures/search_history`
   - Gets historical data (last 30 days)
   - Pushes to Pushgateway with labels

2. **Schedule sync:**
   - Run hourly (or configurable interval)
   - Backfills missing data
   - Handles API rate limits

### Phase 2: Redis Mailbox Integration

1. **Use beast-mailbox-core:**
   - Sync service publishes metrics to mailbox
   - Consumer subscribes and pushes to Pushgateway
   - Decouples components

2. **Benefits:**
   - Async processing
   - Retry logic
   - Rate limit handling

### Phase 3: HA Deployment

1. **Two local machines:**
   - Machine 1: Production
   - Machine 2: Dev/HA

2. **Cloud third leg:**
   - Machine 3: Cloud-based Observatory
   - Geographic redundancy

---

## Concerns and Mitigations

### Concern 1: SonarCloud API Rate Limits

**Mitigation:**
- ✅ Redis mailbox queues requests
- ✅ Sync service respects rate limits
- ✅ Periodic sync (hourly) is low frequency

### Concern 2: Prometheus Unavailability

**Mitigation:**
- ✅ Redis mailbox buffers metrics
- ✅ Consumer retries when Prometheus available
- ✅ Metrics not lost during downtime

### Concern 3: Host Failure

**Mitigation:**
- ✅ Two local machines (prod + dev/HA)
- ✅ Cloud third leg for geographic redundancy
- ✅ Periodic sync backfills after recovery

### Concern 4: SonarCloud Downtime

**Mitigation:**
- ✅ Prometheus retains 30 days of data
- ✅ Real-time feeds continue if GitHub Actions works
- ✅ Sync resumes when SonarCloud available

---

## Questions

1. **Sync frequency?** (Recommend: Hourly)
2. **Redis mailbox configuration?** (Use existing Redis cluster or separate?)
3. **HA deployment priority?** (Local HA first, then cloud?)
4. **Monitoring for sync service?** (Track sync success/failure?)

---

**Status:** Design complete - Ready for implementation


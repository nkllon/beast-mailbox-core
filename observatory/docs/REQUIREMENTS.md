# Observatory Project - Requirements

**Date:** 2025-01-31  
**Status:** Requirements Definition  
**Source:** Stakeholder requirements from architecture discussion

---

## Core Requirements

### 1. SonarCloud as Source of Truth

**Requirement:** SonarCloud is the authoritative source for historical metrics data.

**Rationale:**
- SonarCloud retains historical data (with progressive thinning)
- We should pull from SonarCloud at periodic intervals
- Combine with real-time event feeds for complete coverage

**Acceptance Criteria:**
- ✅ Sync service queries SonarCloud API periodically
- ✅ Backfills historical data into Prometheus
- ✅ Handles real-time feed gaps gracefully
- ✅ SonarCloud data takes precedence if conflicts

---

### 2. Periodic Sync Strategy

**Requirement:** Pull historical data from SonarCloud at regular intervals and update Prometheus with real-time event feeds.

**Rationale:**
- Real-time feeds (GitHub Actions → Pushgateway) may miss events
- Periodic sync ensures data completeness
- Combines best of both: real-time + historical

**Acceptance Criteria:**
- ✅ Sync service runs periodically (configurable interval, default: hourly)
- ✅ Queries SonarCloud API for historical metrics
- ✅ Pushes to Prometheus Pushgateway
- ✅ Real-time feeds continue to work independently
- ✅ Both sources feed into same Prometheus instance

---

### 3. Redis Mailbox for Decoupling (When Beneficial)

**Requirement:** Use Redis mailbox (beast-mailbox-core) to decouple components if it helps reliability, even if services are co-located.

**Rationale:**
- Services are co-located (same host), but mailbox provides:
  - Component isolation (one service down doesn't block others)
  - Async operations and queuing
  - Retry logic for failed operations
  - Rate limit handling
- Even if host is down, mailbox improves resilience during partial failures

**Acceptance Criteria:**
- ✅ Optional mailbox integration (configurable)
- ✅ Sync service can publish to mailbox
- ✅ Consumer service pulls from mailbox and pushes to Pushgateway
- ✅ Decouples sync service from Prometheus availability
- ✅ Enables retry logic and queuing

**Note:** Does NOT solve HA (that needs multiple hosts), but improves component reliability.

---

### 4. HA Strategy: Two Machines Locally + Cloud Third Leg

**Requirement:** 
- Phase 1: Two machines in lab (prod + dev/HA)
- Phase 2: Cloud third leg for geographic redundancy
- Pragmatic approach: If Cloudflare is down, we have bigger issues

**Rationale:**
- Two local machines: prod on one, dev/HA on other
- When not developing, can run HA on both
- Cloud third leg provides geographic redundancy
- Not aiming for 99.999% (that's overkill), but reliable enough

**Acceptance Criteria:**
- ✅ Design supports deployment on multiple hosts
- ✅ Configuration allows prod/dev separation
- ✅ Cloud deployment option available
- ✅ Manual or automatic failover capability
- ✅ Each instance can run independently

**Limitations:**
- ⚠️ Shared dependencies (SonarCloud, GitHub Actions) affect all instances
- ⚠️ If host down, all services on that host down (but other hosts available)
- ✅ Periodic sync provides backup even if real-time feeds fail

---

### 5. Service Co-Location Reality

**Requirement:** Acknowledge that services are co-located (Prometheus, Grafana, Pushgateway together), so if box is down, they're all down.

**Rationale:**
- Services run in same Docker Compose stack
- Single host failure = all services down
- Mailbox doesn't solve this (Redis also on same host)
- HA requires multiple hosts, not just mailbox

**Acceptance Criteria:**
- ✅ Architecture acknowledges co-location
- ✅ HA strategy addresses host-level failures
- ✅ Mailbox used for component isolation, not HA
- ✅ Documentation clarifies limitations

---

### 6. Data Retention Strategy

**Requirement:** Use SonarCloud for historical data, Prometheus for recent data (30-day window).

**Rationale:**
- SonarCloud retains data with progressive thinning (unlimited history via API)
- Prometheus configured for 30-day retention (good balance)
- Query SonarCloud API for historical data when needed
- Prometheus for fast queries on recent data

**Acceptance Criteria:**
- ✅ Prometheus retention: 30 days
- ✅ Sync service queries SonarCloud for historical data
- ✅ Grafana can query both sources
- ✅ No need to extend Prometheus retention beyond 30 days

---

## Design Decisions (Not Requirements, But Documented)

### Decision 1: Mailbox Decoupling (Optional)
- **Option:** Use Redis mailbox for async operations
- **Rationale:** Improves component isolation, enables retry logic
- **Status:** Optional feature, configurable

### Decision 2: Sync Frequency
- **Default:** Hourly periodic sync
- **Rationale:** Balances freshness with API rate limits
- **Status:** Configurable

### Decision 3: HA Deployment
- **Phase 1:** Two local machines
- **Phase 2:** Cloud third leg
- **Rationale:** Pragmatic approach, not over-engineering

---

## Requirements Traceability

| Requirement | Source | Implemented In | Status |
|------------|--------|---------------|--------|
| SonarCloud as source of truth | Stakeholder | sync_service.py | ✅ |
| Periodic sync | Stakeholder | sync_service.py | ✅ |
| Redis mailbox decoupling | Stakeholder | metrics_consumer.py | ✅ |
| Two machines + cloud | Stakeholder | ARCHITECTURE_DESIGN.md | ✅ |
| Co-location acknowledgment | Stakeholder | ARCHITECTURE_DESIGN.md | ✅ |
| 30-day Prometheus retention | Stakeholder | docker-compose.yml | ✅ |

---

## Validation

**Question:** Do all requirements have solutions?
- ✅ Yes - All requirements mapped to implementations

**Question:** Are there solutions without requirements?
- ✅ No - All implementations trace back to stakeholder requirements

**Question:** Can requirements change without breaking solutions?
- ✅ Yes - Requirements documented separately, solutions can be updated

---

**Status:** Requirements documented - Traceable to stakeholder input


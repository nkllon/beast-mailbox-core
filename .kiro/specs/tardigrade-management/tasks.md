# Implementation Plan

- [ ] 1. Stand up catalog service
  - Create database schema for tardigrade records, replicas, incidents, and policy assignments.
  - Implement sync job ingestor that scans `tardigrade.yaml` manifests and populates/repairs catalog entries.
  - Build REST endpoints/CLI to list tardigrades, filter, and export reports.
  - _Requirements: 1.1, 1.2, 1.4_

- [ ] 2. Duplicate and anomaly detection
  - Add logic to detect duplicate identifiers or missing catalog metadata during sync.
  - Emit incidents with severity and remediation guidance.
  - Integrate with alerting (Channel Blaster event + incident queue).
  - _Requirements: 1.3, 2.2_

- [ ] 3. Preservation scheduler & workers
  - Implement job scheduler (APScheduler/Celery beat) executing health checks across configured storage adapters.
  - Build worker tasks for replica verification, migration, credential rotation; ensure no payload mutation.
  - Publish metrics to RPG2K (healthy/warning/critical counters).
  - _Requirements: 2.1, 2.3, 2.4_

- [ ] 4. Incident management pipeline
  - Define incident queue storage and processing workflow (assignment, escalation, resolution).
  - Provide command/API to acknowledge, resolve, and annotate incidents.
  - Block revival when unresolved critical incidents exist.
  - _Requirements: 2.2, 3.2_

- [ ] 5. Revival & retirement workflow engine
  - Implement state machine handling approvals, revival steps, failure rollback, and retirement transitions.
  - Restore writable copies via Storage Adapter, update catalog, and trigger Channel Blaster notifications.
  - Persist audit trail entries for each step.
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 6. Policy engine & RBAC enforcement
  - Build policy evaluation layer with versioned policy documents.
  - Integrate role-based access across discovery API, preservation control, and revival endpoints.
  - Validate cross-repo operations by verifying identification metadata and policy compatibility.
  - _Requirements: 4.1, 4.2, 4.3, 4.4_


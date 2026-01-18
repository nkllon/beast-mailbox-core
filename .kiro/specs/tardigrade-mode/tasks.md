# Implementation Plan

- [ ] 1. Harden identification prerequisites
  - Extend `spec.json` schema and identification tooling to include immutable `id`, `owner`, and `hash` fields; fail if missing during Tardigrade promotion.
  - Provide CLI command (`identify-spec`) that writes metadata, computes hashes, and enforces immutability rules.
  - Update CI linting to warn/block promotion attempts on unidentifed specs.
  - _Requirements: 1.1, 2.1_

- [ ] 2. Build Tardigrade Controller
  - Implement promotion flow that validates identification metadata, sets read-only flags, generates `tardigrade.yaml`.
  - Hook controller into replication orchestrator and governance logger (atomic promotion log + manifest write).
  - Expose CLI/API to promote specs, with dry-run mode for verification.
  - _Requirements: 1.1, 1.2, 2.1, 2.4, 3.1_

- [ ] 3. Implement multi-backend storage replication
  - Create storage adapters for git mirror, object store (S3/GCS), and optional cold archive.
  - Ensure replication receipts capture hashes and timestamps; error handling escalates to governance.
  - Integrate drift auditor job comparing canonical hash versus replicas; publish metrics.
  - _Requirements: 2.1, 2.2, 2.4, 4.2_

- [ ] 4. Build discovery index and API
  - Design catalog schema (identifier, owner, dormancy timestamp, status, storage locations).
  - Implement sync job scanning manifests, updating catalog, and detecting duplicates.
  - Provide read-only API/CLI to list tardigrades, filter by owner/age, and export snapshots.
  - _Requirements: 3.1, 3.2, 4.1_

- [ ] 5. Implement revival workflow
  - Create state machine for `dormant → reviving → active/retired` with rollback logic.
  - Restore primary copy to writable state, clear read-only flags, and update index.
  - Publish revival/retirement events via Channel Blaster; notify owners and governance.
  - _Requirements: 3.1, 3.2, 4.4_

- [ ] 6. Security, policy, and automation hooks
  - Add RBAC checks for promotion/revival endpoints; integrate with existing auth provider.
  - Document API contract for external workflows to query status and permitted actions.
  - Ensure policy updates from Identified Spec/Channel Blaster propagate to Tardigrade Controller.
  - _Requirements: 4.1, 4.2, 4.3, 4.4_


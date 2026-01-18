# Implementation Plan

- [ ] 1. Implement identification CLI and API
  - Build `identify-spec` command (Typer) that validates inputs, generates ULID/UUIDv7, computes hashes, writes immutable fields to `spec.json`.
  - Provide FastAPI endpoint `POST /identify` for automation; reuse same validation pipeline.
  - Add helper commands `show-identification` and `verify-identification`.
  - _Requirements: 1.1, 1.3, 2.1, 4.1_

- [ ] 2. Enforce metadata validation
  - Extend schema checker to require name, `created_at`, owner contact, hash + algorithm when `id` present.
  - Integrate guardrails into CI (pre-commit/CI job) preventing identification with missing fields.
  - Emit actionable error messages guiding contributors to supply metadata.
  - _Requirements: 2.1, 2.2, 2.4_

- [ ] 3. Build identification registry
  - Create git-backed JSON/SQLite registry storing identifier → repo/path/owner/hash mapping.
  - Implement deduplication and merge conflict resolution helpers.
  - Provide read API for registry (used by Status API and other tools).
  - _Requirements: 1.4, 3.1, 3.2_

- [ ] 4. Lifecycle logging service
  - Implement append-only log recorder for identification events (identified, metadata-updated, deprecated).
  - Wire CLI/API to log every state transition with actor + timestamp.
  - Expose query/report utilities for governance audits.
  - _Requirements: 3.1, 3.4_

- [ ] 5. Status API & contract tests
  - Build `GET /identified/{id}` and `GET /identified/by-path` endpoints returning metadata snapshot and derived status.
  - Publish OpenAPI schema + contract tests for downstream repositories.
  - Integrate with Channel Blaster to broadcast schema or policy changes.
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 6. Hash normalization & recompute utilities
  - Define canonical hash scope (e.g., sorted files excluding `spec.json` ID fields) and document normalization.
  - Provide command to recompute hash and detect drift without mutating existing ID.
  - Ensure compatibility with Tardigrade Mode and preservation audits.
  - _Requirements: 2.3, 3.2_


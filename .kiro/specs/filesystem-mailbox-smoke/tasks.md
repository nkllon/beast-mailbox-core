# Implementation Plan

- [x] 1. Establish smoke test harness infrastructure
  - Create a pytest smoke marker and orchestrator entry point that sequences filesystem and Redis scenarios in one run.
  - Build an EnvironmentManager that provisions temporary inbox roots, injects Redis connection details, and generates a UUID `suite_run_id` shared across metrics and logs.
  - Provide a CLIExecutor helper that invokes `beast-mailbox-send` and `beast-mailbox-service` with backend flags while capturing stdout/stderr and exit codes.
  - _Requirements: Req 1, Req 2, Req 4_

- [ ] 1.1 Persist suite artifacts
  - Implement artifact directory creation for each run, storing raw CLI output, service logs, and structured `SuiteResult` JSON.
  - Ensure artifact paths are cleaned between runs to prevent residue on macOS and Linux hosts.
  - _Requirements: Req 4_

- [ ] 2. Implement filesystem smoke scenarios
  - Execute CLI-based send/receive flow, asserting exit status 0, message persistence, message cleanup, and immutable `message_id` reuse.
  - Run direct `FileSystemMailboxService` send/receive handling, confirming handler invocation, directory auto-creation with configured permissions, and removal of `.tmp` files.
  - Capture `beast_mailbox.fs.*` log records for send/receive identifiers during each step.
  - _Requirements: Req 1, Req 3_

- [ ] 2.1 Validate filesystem scenario telemetry inputs
  - Record per-phase metrics (`phase="send"`, `phase="receive"`) tagged with `suite_run_id` and filesystem backend label for later verification.
  - Persist the observed `message_id` in scenario output to support cross-backend comparisons.
  - _Requirements: Req 1, Req 3_

- [ ] 3. Implement Redis regression scenarios
  - Trigger CLI send/receive flow targeting Redis, matching payload and `message_id` against filesystem results to confirm parity.
  - Ensure redis inbox processing performs acknowledgement and trimming so streams return to a clean state post-run.
  - _Requirements: Req 2_

- [ ] 3.1 Cross-backend parity summary
  - Produce a comparison report highlighting filesystem vs Redis outcomes (message IDs, payload hashes, timing) without cross-contamination.
  - Surface discrepancies as failed scenario results with actionable context.
  - _Requirements: Req 2_

- [ ] 4. Implement telemetry verification and metric export
  - Query Prometheus using provided credentials, asserting `beast_mailbox_smoke_messages_total` and `beast_mailbox_smoke_suite_pass` reflect expected deltas for each backend.
  - Generate Prometheus exposition-format payloads (including `suite_run_id`) so other agents can push or re-emit smoke results.
  - _Requirements: Req 3_

- [ ] 4.1 Fallback logging and Grafana alignment
  - When Prometheus is unreachable, scrape filesystem logs for send/receive identifiers and mark telemetry results accordingly.
  - Validate that existing Grafana dashboards can reference the new metrics (e.g., via automated query check or documented query snippet in test output).
  - _Requirements: Req 3_

- [ ] 5. Finalize reporting and CI integration
  - Emit a concise pass/fail summary to stdout and persist a machine-readable artifact suitable for CI gating.
  - Wire cleanup routines to ensure temporary directories, Redis streams, and spawned processes terminate cleanly on macOS and Linux.
  - _Requirements: Req 4_

- [x] 5.1 Implement geometric load ramp and health harness
  - Extend orchestrator to execute batches of filesystem/redis scenarios in geometric progression (1, 2, 4, 8…) until latency thresholds or failures occur.
  - Capture per-batch latency, stream depth, filesystem backlog, and Prometheus/log snapshots, surfacing health summaries alongside artifacts.
  - Introduce configurable stop conditions (max concurrency, latency ceiling) to protect shared infrastructure during automated runs.
  - _Requirements: Req 3, Req 4_

- [ ] 5.2 Automate local telemetry and Redis harness lifecycle
  - Provide scripts/fixtures that start Prometheus (port 20090), Grafana (20300), and Redis (20637) containers for each smoke run, marking them as ephemeral high-port workloads.
  - Ensure harness publishes active endpoints so collaborating agents can attach to the same temporary stack, and tears everything down on completion.
  - _Requirements: Req 3, Req 4_

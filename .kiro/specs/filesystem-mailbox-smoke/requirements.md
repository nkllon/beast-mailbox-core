# Requirements Document

## Introduction
Define and execute smoke testing flows that exercise filesystem and Redis mailboxes end-to-end so upgrades preserve existing behavior while validating new functionality.

## Requirements

### Requirement 1: Filesystem Smoke Coverage
**Objective:** As a Beast release engineer, I want automated smoke flows for the filesystem mailbox, so that upgrades confirm message delivery without breaking existing users.

#### Acceptance Criteria
1. WHEN the smoke suite invokes `beast-mailbox-send` with the filesystem backend THEN the Smoke Test Suite SHALL persist the message, observe it via `beast-mailbox-service --latest`, and confirm CLI exit status 0.
2. WHEN the smoke suite runs direct `FileSystemMailboxService` send and receive operations THEN the Smoke Test Suite SHALL verify handler execution, message cleanup, and absence of orphaned `.tmp` files.
3. IF a filesystem inbox directory does not exist THEN the Smoke Test Suite SHALL confirm the service creates it with the configured permissions before message dispatch.
4. WHILE filesystem smoke tests execute THE Smoke Test Suite SHALL log send and receive identifiers using the standard `beast_mailbox.fs.*` logger namespace.

### Requirement 2: Redis Regression Safeguard
**Objective:** As a Beast platform engineer, I want Redis smoke coverage to run alongside filesystem tests, so that adding a filesystem backend does not regress existing Redis workflows.

#### Acceptance Criteria
1. WHEN the smoke suite runs `beast-mailbox-send` targeting Redis THEN the Smoke Test Suite SHALL observe delivery via `beast-mailbox-service --latest` and assert message parity with filesystem results.
2. WHEN Redis smoke flows complete THEN the Smoke Test Suite SHALL ensure pending entries are acknowledged or trimmed to leave streams clean.
3. IF both backends execute in the same suite THEN the Smoke Test Suite SHALL report a combined summary highlighting success/failure for each backend without cross-contamination.

### Requirement 3: Telemetry and Logging Verification
**Objective:** As an SRE, I want smoke tests to validate telemetry emissions, so that operational dashboards remain trustworthy.

#### Acceptance Criteria
1. WHEN Prometheus credentials (`Beastmaster2025`) and default port are supplied THEN the Smoke Test Suite SHALL query the Prometheus endpoint and confirm counters such as `beast_mailbox_messages_total` increase after send/receive flows.
2. IF Prometheus is unavailable THEN the Smoke Test Suite SHALL fall back to verifying filesystem log entries for send and receive events.
3. WHERE Grafana is present THE Smoke Test Suite SHALL populate or validate at least one dashboard panel sourcing the verified Prometheus metric.

### Requirement 4: Environment and Cross-Platform Readiness
**Objective:** As a Beast operations lead, I want smoke tests to reflect real deployment conditions, so that results hold across supported platforms.

#### Acceptance Criteria
1. WHEN smoke tests execute on macOS or Linux THEN the Smoke Test Suite SHALL run without mocks, using actual filesystem operations and live Prometheus/Grafana lab instances.
2. IF environment-specific configuration (paths, permissions) is required THEN the Smoke Test Suite SHALL document and apply the settings before running the backend flows.
3. WHERE temporary directories are used THE Smoke Test Suite SHALL clean them after execution to avoid residue across runs.
4. WHEN the smoke suite completes THEN the Smoke Test Suite SHALL emit a pass/fail signal suitable for CI gating and include pointers to collected telemetry/log artifacts.

# Requirements Document

## Introduction
Deploy a permanent Prometheus Pushgateway alongside the Beast telemetry stack so agents can publish smoke-test metrics without relying on remote Prometheus hosts, while documenting conventions for ephemeral/local test stacks.

## Requirements

### Requirement 1: Permanent Pushgateway Service
**Objective:** As a Beast operator, I want a dedicated Pushgateway instance running 24/7 on the canonical port, so that telemetry clients always have a low-latency ingest target.

#### Acceptance Criteria
1. WHEN the Beast telemetry stack boots THEN Operations SHALL start the Pushgateway on port 9091 (or cluster-assigned equivalent) with system-level supervision.
2. WHILE the Pushgateway instance runs THE Telemetry Platform SHALL expose readiness/liveness endpoints and integrate with Grafana dashboards.
3. IF the Pushgateway stops unexpectedly THEN the telemetry stack SHALL emit alerts and restart the service automatically.

### Requirement 2: Ephemeral Local Harness Convention
**Objective:** As a Beast developer, I want a standard pattern for temporary Pushgateway deployments, so local smoke tests do not conflict with shared infrastructure.

#### Acceptance Criteria
1. WHEN an engineer launches a local telemetry harness for testing THEN the tooling SHALL bind Prometheus, Grafana, and Pushgateway to reserved high ports (e.g., 20090/20300/20637) and label the stack as ephemeral.
2. IF the engineer does not tear the harness down manually THEN the tooling SHALL provide a cleanup command to stop and remove the containers safely.
3. WHERE multiple agents collaborate on the same host THE harness SHALL publish the active endpoints so peers can attach to the temporary stack knowingly.

### Requirement 3: Smoke Suite Metric Publishing
**Objective:** As a smoke-test author, I want the suite to push metrics reliably, so telemetry checks no longer rely on fallbacks.

#### Acceptance Criteria
1. WHEN a smoke run completes THEN the harness SHALL push the `metrics.prom` payload into the Pushgateway and ensure Prometheus scrapes it within the same run.
2. IF Prometheus counters do not reach expected deltas after pushing THEN the smoke suite SHALL fail the telemetry step with actionable diagnostics.
3. WHILE the permanent Pushgateway is reachable THE smoke suite SHALL prefer it over local harnesses; otherwise it SHALL fall back to the high-port stack configured for the run.

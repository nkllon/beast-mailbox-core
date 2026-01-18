# Implementation Plan

- [x] 1. Provision permanent Pushgateway service
  - Define systemd/Compose manifests (or equivalent) to run Pushgateway on port 9091 with health endpoints enabled.
  - Wire alerts and Grafana dashboards that monitor availability and restart behavior.
  - _Requirements: Req 1_

- [x] 2. Deliver ephemeral telemetry harness tooling
  - Provide start/stop scripts (or pytest fixtures) that launch Prometheus, Grafana, and Pushgateway on reserved high ports for local testing.
  - Publish active endpoints (e.g., via log output or artifact file) so collaborating agents can attach to the temporary stack.
  - _Requirements: Req 2_

- [x] 3. Integrate smoke suite metric publishing
  - Update smoke harness to push `metrics.prom` into the Pushgateway and verify Prometheus counters within each run.
  - Emit actionable diagnostics when counters fail to match expected deltas.
  - _Requirements: Req 3_

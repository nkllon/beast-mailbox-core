# Implementation Plan

- [ ] 1. Provision macOS node exporter and baseline dashboard
  - Deploy node_exporter on Tahoe (service or container) and add Prometheus scrape jobs (permanent stack + harness).
  - Import or author Grafana dashboard panels for CPU, memory, disk, network with alert banners for missing data.
  - _Requirements: Req 1_

- [ ] 2. Provide Docker metrics instrumentation
  - Add cAdvisor (or Docker metrics endpoint) to the harness and permanent stack; update Prometheus scrape configs accordingly.
  - Build Grafana panels tracking harness container CPU/memory/restarts and label them for multi-user visibility.
  - _Requirements: Req 2_

- [ ] 3. Create mailbox core smoke dashboard
  - Construct Grafana dashboard (JSON model) charting `beast_mailbox_smoke_messages_total` and suite pass rates by suite_run_id.
  - Add filters/annotations for load ramp batches and telemetry mismatch counters.
  - _Requirements: Req 3_

- [ ] 4. Document session lifecycle workflow
  - Update telemetry docs with session-level start/stop procedures (node exporter, harness, Redis) and per-test artifact correlation steps.
  - Provide guidance on exporting dashboards and aligning timestamps with smoke artifacts.
  - _Requirements: Req 1, Req 2, Req 3_

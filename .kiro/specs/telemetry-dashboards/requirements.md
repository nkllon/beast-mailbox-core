# Requirements Document

## Introduction
Standardize telemetry dashboards for Beast smoke testing by providing permanent baseline instrumentation (macOS host and Docker metrics) and feature-focused dashboards, starting with mailbox core smoke activity.

## Requirements

### Requirement 1: macOS Baseline Dashboard
**Objective:** As an operations engineer, I want a permanent macOS health dashboard, so that I can monitor host saturation during smoke sessions.

#### Acceptance Criteria
1. WHEN the telemetry stack initializes THEN Grafana SHALL expose a dashboard summarizing CPU, memory, disk, and network metrics scraped from `node_exporter` on the host.
2. WHILE node_exporter metrics are unavailable THE dashboard SHALL surface alert banners indicating missing data.
3. IF a smoke session records timestamps or suite identifiers THEN the dashboard SHALL allow time-range filtering to correlate host load with the session window.

### Requirement 2: Docker Metrics Dashboard
**Objective:** As a platform engineer, I want a permanent dashboard for Docker container statistics, so that I can verify harness containers are running and observe their resource usage.

#### Acceptance Criteria
1. WHEN the local telemetry harness starts THEN Grafana SHALL include panels for container CPU, memory, and restart counts collected via cAdvisor or Docker metrics endpoints.
2. WHILE a harness container stops unexpectedly THE dashboard SHALL show zero or missing metrics, prompting follow-up investigation.
3. IF multiple developers share a host THEN the dashboard SHALL highlight container names/labels so concurrent sessions can be distinguished.

### Requirement 3: Mailbox Core Smoke Dashboard
**Objective:** As a smoke suite author, I want a feature-specific dashboard for mailbox core runs, so that I can visualize message counts, suite_run_id activity, and pushgateway ingestion in near real time.

#### Acceptance Criteria
1. WHEN a smoke run pushes metrics via Pushgateway THEN the dashboard SHALL chart `beast_mailbox_smoke_messages_total` and `beast_mailbox_smoke_suite_pass` by suite_run_id.
2. WHILE a load ramp executes THE dashboard SHALL display concurrency-level annotations or overlays to correlate ramp steps with backend metrics.
3. IF smoke telemetry mismatches occur THEN the dashboard SHALL surface error counters or logs referencing the suite_run_id for troubleshooting.

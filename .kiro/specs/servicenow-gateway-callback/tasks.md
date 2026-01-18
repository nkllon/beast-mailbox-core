# Implementation Plan

- [ ] 1. Stand up authenticated gateway service
  - Scaffold FastAPI (or equivalent) application with secure TLS termination and health probes
  - Configure OAuth client credentials and mutual TLS trust store sourced from secure configuration
  - Add rate limiting middleware and structured logging primitives across all routes
  - _Requirements: 1, 4_

- [ ] 1.1 Implement request validation and correlation persistence
  - Define JSON schema for ServiceNow payloads with required field enforcement and allowlists
  - Persist correlation entries with message ID, ServiceNow record references, and status metadata
  - Return 202 Accepted responses containing message identifiers and correlation details
  - _Requirements: 1, 2_

- [ ] 2. Integrate Beast mailbox dispatch pipeline
  - Construct mailbox messages from validated payloads while injecting correlation metadata and origin info
  - Invoke configured Beast transport asynchronously with error translation and retry hooks
  - Emit audit records for each dispatch attempt including credential identifiers and timestamps
  - _Requirements: 2, 4_

- [ ] 2.1 Harden dispatch failure handling
  - Surface 4xx/5xx responses with descriptive errors when authentication or validation fails
  - Implement exponential backoff with jitter for transient dispatch errors without duplicate mailbox messages
  - Escalate unresolved dispatch failures via alerting and mark correlations pending_manual
  - _Requirements: 2, 4_

- [ ] 3. Deliver callback intake and routing
  - Expose authenticated callback endpoint for Beast handlers with signature or shared-secret validation
  - Lookup correlation records, map to one or more ServiceNow targets, and update statuses atomically
  - Forward callback outcomes to Snowflake audit pipeline for compliance logging
  - _Requirements: 2, 3, 4_

- [ ] 3.1 Implement ServiceNow update client
  - Create REST client for ServiceNow Table/Scripted APIs supporting PATCH or POST work note updates
  - Apply exponential backoff and retry budget for transient ServiceNow failures with final escalation path
  - Confirm state transitions and work note inserts, updating correlation store with closure timestamps
  - _Requirements: 3_

- [ ] 4. Provide observability and retention controls
  - Publish Prometheus metrics tracking throughput, validation failures, callback latency, and retry counts
  - Configure structured logging with correlation identifiers and redact sensitive payload details
  - Enforce retention policies that purge payloads after configured duration while retaining audit metadata
  - _Requirements: 4_

- [ ] 5. Validate end-to-end integration
  - Author unit tests for validators, credential manager, correlation store, and ServiceNow client adapters
  - Execute integration tests simulating ServiceNow -> gateway -> Beast -> callback loop using stubs/mocks
  - Load test gateway under expected concurrency to verify rate limiting, retry behavior, and alerting triggers
  - _Requirements: 1, 2, 3, 4_

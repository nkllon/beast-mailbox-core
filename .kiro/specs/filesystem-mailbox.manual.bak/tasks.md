# Implementation Plan

- [ ] 1. Establish filesystem mailbox configuration layer
  - Define configuration structure for base path, polling cadence, and directory permissions
  - Load configuration overrides from environment variables with validation and fallbacks
  - Document configuration defaults for platform engineers
  - _Requirements: Req 1_

- [ ] 1.1 Validate configuration edge cases
  - Handle invalid poll interval and permission inputs with safe defaults
  - Ensure configuration loader tolerates missing environment variables
  - _Requirements: Req 1_

- [ ] 2. Implement durable message persistence
  - Persist outbound messages as JSON envelopes aligned with `MailboxMessage`
  - Enforce single-writer atomicity using temporary files and `os.replace`
  - Ensure recipient inbox directories are created with configured permissions
  - _Requirements: Req 1_

- [ ] 2.1 Harden message write error handling
  - Surface filesystem exceptions with actionable log entries
  - Prevent orphaned temporary files during interrupted writes
  - _Requirements: Req 3_

- [ ] 3. Build asynchronous inbox processing
  - Create polling loop respecting configured interval and service lifecycle flags
  - Deserialize message files and invoke registered async handlers sequentially
  - Remove processed message files to prevent duplicate deliveries
  - _Requirements: Req 2_

- [ ] 3.1 Handle idle and no-handler scenarios
  - Detect absence of handlers and log informative messages without deleting files
  - Protect the loop against corrupted payloads via decode error handling
  - _Requirements: Req 2, Req 3_

- [ ] 4. Integrate observability and graceful shutdown
  - Emit debug-level send and receive events with message identifiers
  - Capture poll loop exceptions and continue operation after delays
  - Cancel background tasks on stop without surfacing cancellation errors
  - _Requirements: Req 2, Req 3_

- [ ] 4.1 Deliver automated test coverage
  - Add unit tests covering configuration loading and atomic message persistence
  - Add async integration tests exercising handler dispatch and cleanup
  - _Requirements: Req 1, Req 2, Req 3_



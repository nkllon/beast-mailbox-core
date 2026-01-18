# Implementation Plan

- [x] 1. Establish filesystem configuration layer
  - Define dataclass for `base_path`, `poll_interval`, and `mkdir_mode`
  - Load overrides from environment variables with validation and fallbacks
  - Document defaults for platform operators
  - _Requirements: Req 1_

- [x] 1.1 Validate configuration edge cases
  - Handle invalid poll interval and permission inputs with safe defaults
  - Tolerate absent environment variables without raising exceptions
  - _Requirements: Req 1_

- [x] 2. Implement durable message persistence
  - Persist outbound messages as JSON envelopes aligned with `MailboxMessage`
  - Use temporary files plus `os.replace` to ensure atomic writes
  - Create recipient inbox directories with configured permissions before writing
  - _Requirements: Req 1_

- [x] 2.1 Harden persistence error handling
  - Surface filesystem exceptions with actionable log entries
  - Clean up orphaned temporary files after interrupted writes
  - _Requirements: Req 3_

- [x] 3. Build asynchronous inbox processing
  - Implement polling loop controlled by `_running` flag and `poll_interval`
  - Deserialize message files, invoke handlers sequentially, and delete successes
  - _Requirements: Req 2_

- [x] 3.1 Handle idle and failure scenarios
  - Log when no handlers are registered without deleting messages
  - Catch JSON decode errors, log them, and remove corrupted files
  - _Requirements: Req 2, Req 3_

- [x] 4. Integrate observability and shutdown
  - Emit debug-level send and receive events with message identifiers
  - Log polling loop exceptions and continue after configured delay
  - Cancel background tasks during `stop()` and suppress cancellation errors
  - _Requirements: Req 2, Req 3_

- [x] 4.1 Deliver automated test coverage
  - Add unit tests for configuration loading and atomic file persistence
  - Add async tests covering handler dispatch and file cleanup
  - _Requirements: Req 1, Req 2, Req 3_


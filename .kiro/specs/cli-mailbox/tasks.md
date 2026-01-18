# Implementation Plan

- [x] 1. Build CLI command surfaces
  - Define entry points for `beast-mailbox-service` and `beast-mailbox-send`
  - Configure argument parsing for mode selection and configuration flags
  - Ensure help text documents streaming, latest, ack, trim, and send options
  - _Requirements: Req 1, Req 2, Req 3, Req 4_

- [x] 1.1 Validate input combinations
  - Enforce mutual exclusivity between `--message` and `--json`
  - Require recipient and sender arguments where applicable
  - Emit descriptive errors for missing or conflicting configuration flags
  - _Requirements: Req 3, Req 4_

- [x] 2. Implement configuration merge logic
  - Combine CLI flags with environment variables to construct mailbox configs
  - Override defaults when explicit CLI arguments are provided
  - Surface errors when configuration remains incomplete after merging
  - _Requirements: Req 4_

- [x] 3. Implement streaming mode
  - Instantiate mailbox service, register printing handler, and start background loop
  - Handle SIGINT/termination signals to stop the service gracefully
  - Support verbose logging by adjusting logger levels
  - _Requirements: Req 1_

- [x] 4. Implement latest/ack/trim operations
  - Fetch most recent messages without entering streaming loop
  - Apply acknowledgement or trimming when flags are set
  - Format output consistently for operators
  - _Requirements: Req 2_

- [x] 5. Implement send command
  - Create outbound payloads from text or JSON inputs
  - Invoke mailbox service to deliver the message with optional type override
  - Print confirmation including message identifier
  - _Requirements: Req 3_

- [x] 6. Provide automated test coverage
  - Add unit tests for argument parsing, configuration precedence, and validation errors
  - Add integration-style tests for send and latest flows using mocked mailbox services
  - _Requirements: Req 1, Req 2, Req 3, Req 4_


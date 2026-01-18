# Implementation Plan

- [ ] 1. Deliver Redis mailbox configuration experience
  - Parse discrete environment variables and `REDIS_URL` into a validated `MailboxConfig`
  - Provide sane defaults for localhost development when inputs are absent
  - Expose stream naming derived from configurable prefixes and agent identifiers
  - _Requirements: Req 1_

- [ ] 1.1 Harden connection bootstrap
  - Establish Redis clients with authentication and connectivity validation via `PING`
  - Surface descriptive errors when credentials or network access fail
  - _Requirements: Req 1, Req 4_

- [ ] 2. Implement message production workflow
  - Add messages to recipient streams with bounded trimming and generated IDs
  - Preserve `MailboxMessage` schema for payload serialization
  - _Requirements: Req 2_

- [ ] 2.1 Build consumer loop semantics
  - Create consumer groups per agent when absent
  - Read from streams using `XREADGROUP`, invoke async handlers sequentially, and acknowledge successes
  - Handle idle polls by respecting configured block intervals
  - _Requirements: Req 2_

- [ ] 3. Execute pending message recovery
  - Inspect pending entries to detect recovery needs before starting the consume loop
  - Claim idle messages with `XAUTOCLAIM` using configurable thresholds and batches
  - Dispatch reclaimed messages to handlers and acknowledge them to release ownership
  - _Requirements: Req 3_

- [ ] 3.1 Report recovery outcomes
  - Populate `RecoveryMetrics` with totals, batches, and timing data
  - Invoke optional callbacks even when no messages require recovery
  - _Requirements: Req 3, Req 4_

- [ ] 4. Strengthen operational resilience
  - Log consumer group clashes (`BUSYGROUP`), loop exceptions, and handler failures with actionable detail
  - Ensure stop routine cancels background tasks, handles cancellation errors, and closes Redis clients
  - _Requirements: Req 4_

- [ ] 5. Provide automated test coverage
  - Add unit tests covering environment parsing, stream naming, send semantics, and error propagation
  - Add async tests simulating consumer loops, recovery, and callback invocation
  - _Requirements: Req 1, Req 2, Req 3, Req 4_



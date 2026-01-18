# Implementation Plan

- [ ] 1. Deliver Redis configuration experience
  - Parse discrete environment variables and `REDIS_URL` into `MailboxConfig`
  - Provide localhost defaults when inputs are absent
  - Expose stream naming derived from configurable prefixes
  - _Requirements: Req 1_

- [ ] 1.1 Harden connection bootstrap
  - Establish Redis clients and validate connectivity via `PING`
  - Surface descriptive errors for authentication or network failures
  - _Requirements: Req 1, Req 4_

- [ ] 2. Implement message production workflow
  - Add messages to recipient streams with bounded trimming and generated IDs
  - Serialize payloads using `MailboxMessage` fields
  - _Requirements: Req 2_

- [ ] 2.1 Build consumer loop semantics
  - Create consumer groups per agent when absent (handling `BUSYGROUP`)
  - Read from streams using `XREADGROUP`, invoke handlers sequentially, and acknowledge successes
  - Respect configured block interval for idle polls
  - _Requirements: Req 2, Req 4_

- [ ] 3. Execute pending message recovery
  - Inspect pending entries before consuming new messages
  - Claim idle messages with `XAUTOCLAIM` using configurable thresholds and batch sizes
  - Dispatch reclaimed messages to handlers and acknowledge them
  - _Requirements: Req 3_

- [ ] 3.1 Report recovery outcomes
  - Populate `RecoveryMetrics` with totals, batches, and timing data
  - Invoke optional callbacks even when no messages require recovery
  - _Requirements: Req 3, Req 4_

- [ ] 4. Strengthen operational resilience
  - Log consumer group clashes, loop exceptions, and handler failures with actionable detail
  - Ensure `stop()` cancels background tasks and closes Redis clients cleanly
  - _Requirements: Req 4_

- [ ] 5. Provide automated test coverage
  - Add unit tests covering environment parsing, stream naming, and send semantics
  - Add async tests simulating consumer loops, recovery paths, and callback invocation
  - _Requirements: Req 1, Req 2, Req 3, Req 4_


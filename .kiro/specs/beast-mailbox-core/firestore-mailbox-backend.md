## Firestore Mailbox Backend Specification

### Overview
- Provide an alternative persistent mailbox implementation for Beast agents running on GCP.
- Core must select the mailbox backend at runtime based on configuration without code changes in consumers.
- Firestore offers pay-per-use pricing, strong per-document consistency, and managed security, meeting the “synchronous, secure, zero-cost-when-idle” goal.

### Goals
- Support multiple mailbox backends (Redis, filesystem, Firestore) through a single configuration flag in Beast mailbox core.
- Match the existing `MailboxMessage` contract (immutable payloads, sender/recipient metadata).
- Guarantee that once a write succeeds, subsequent reads see the message immediately.
- Ensure inbox consumers can enumerate all pending messages and process them exactly once.
- Maintain cost at ~0 when no mailbox operations occur (Firestore’s serverless billing).

### Non-Goals
- Real-time push notifications (initial version relies on polling like current filesystem implementation).
- Multi-recipient fan-out optimizations beyond writing multiple documents.
- Providing eventual consistency backends (e.g., Cloud Storage) under the new flag.

### Configuration Model
- New core configuration key: `BEAST_MAILBOX_BACKEND`.
  - Accepted values: `filesystem`, `redis`, `firestore`.
  - Default remains `redis` for backwards compatibility; Firestore activates only when explicitly selected.
- Optional backend-specific config sections:
  - Redis continues using existing environment variables.
  - Filesystem continues using `FileSystemMailboxConfig`.
  - Firestore introduces `FirestoreMailboxConfig` (see below).
- Core `create_mailbox_service(agent_id: str)` factory reads the flag and instantiates the selected implementation. This keeps plugin logic internal until we formalize an external plugin system.

### Interface Expectations
- All backends implement a common async interface (connect/start/stop/send/register handler).
- `MailboxMessage` remains the shared DTO; Firestore backend serializes/deserializes to match fields.
- Ordering semantics rely on a monotonically increasing `timestamp` or `sequence` field; Firestore backend must preserve comparable sort ordering.
- Handlers receive messages exactly once; backends must delete/ack messages only after successful handler completion.

### Firestore Data Model
- Collection layout: `mailboxes/{agentId}/messages/{messageId}`.
- Document schema:
  ```text
  {
    message_id: string,          # uuid4 or provided
    sender: string,
    recipient: string,
    payload: dict,               # JSON-serializable payload
    message_type: string,        # defaults to "direct_message"
    created_at: Firestore Timestamp,
    version: 1                   # reserved for schema upgrades
  }
  ```
- Required composite index: `mailboxes/{agentId}/messages` ordered by `created_at` descending for “latest message” queries.
- Optional TTL index on `created_at` for automatic cleanup after retention period (configurable).

### Firestore Operations
- **Send**:
  - Create document with provided `message_id` or generate new UUID.
  - Use `create` semantics to enforce immutability; attempts to overwrite existing `message_id` should fail.
  - Optionally wrap in a transaction if we must guarantee recipient inbox creation (not strictly necessary).
- **Receive/Poll**:
  - Query `mailboxes/{agentId}/messages` ordered ascending by `created_at`.
  - For each document, execute handler inside a Firestore transaction:
    1. Read document.
    2. Invoke handler (outside transaction).
    3. After handler success, delete document within a new transaction to avoid long-lived locks.
  - On handler failure, leave the document intact for retry.
- **List Latest**:
  - Query the collection with `limit=1, order_by("created_at", DESC)` to obtain the most recent message.

### Firestore Configuration
- `FirestoreMailboxConfig` fields:
  - `project_id`: GCP project (default from environment).
  - `collection_prefix`: allows sandbox isolation (default empty).
  - `poll_interval`: seconds between polling cycles (default 0.5).
  - `max_batch_size`: number of documents processed per poll (default 50).
  - `credentials_path` optional; prefer ADC with Workload Identity.
- Environment variables:
  - `BEAST_MAILBOX_FS_PROJECT_ID`
  - `BEAST_MAILBOX_FS_COLLECTION_PREFIX`
  - `BEAST_MAILBOX_FS_POLL_INTERVAL`
  - `BEAST_MAILBOX_FS_MAX_BATCH`
  (prefix subject to renaming—finalize during implementation).

### Security & Access Control
- Beast agents run with GCP service accounts granting Firestore read/write to their namespace.
- Restrict access via IAM to mailbox collections (potentially by project separation if fine-grained security rules aren’t used).
- Firestore client enforces TLS; no additional transport layer required.
- Support optional per-agent encryption-at-rest via payload-level encryption (future enhancement).

### Cost Profile
- Firestore charges per document write/read/delete and storage.
- When idle (no operations), cost remains effectively zero aside from negligible stored documents.
- Estimate per message: 1 write + 1 read + 1 delete (≈ $0.108 per 100k operations in default regions).

### Migration & Rollout
- Phase 1: add factory + configuration flag, default remains Redis.
- Phase 2: implement Firestore backend behind flag. Provide feature toggle for beta users.
- Phase 3: document operational guidance, Cloud project setup scripts, IAM roles.
- Out-of-scope: automatic data migration from Redis/filesystem to Firestore; handle via bespoke tooling if required.

### Testing Strategy
- Unit tests with Firestore emulator covering send/receive cycles and error handling.
- Integration tests verifying factory selection via configuration.
- Load tests to confirm polling performance and cost under expected traffic.
- Security tests to validate IAM least-permission configuration.

### Open Questions
- Do we need multi-recipient broadcasts (one write per recipient vs. shared doc with reference counts)?
- Should we expose mailbox retention policy as configuration or rely on TTL indexes?
- Is there a requirement for audit logging beyond native Firestore activity logs?



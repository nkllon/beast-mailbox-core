# Requirements Document

## Introduction
Beast Mailbox Core must provide a same-host transport so Beast agents that share a filesystem can exchange messages without Redis while preserving mailbox semantics, durability, and developer ergonomics.

## Requirements

### Requirement 1: Local Message Persistence
**Objective:** As a Beast platform engineer, I want the filesystem mailbox to durably store outbound messages, so that co-located agents can reliably retrieve them without external infrastructure.

#### Acceptance Criteria
1. WHEN `FileSystemMailboxService` sends a message THEN the service SHALL persist the payload as a JSON file under `{base_path}/{recipient}/inbox`.
2. IF the recipient inbox directory does not exist THEN `FileSystemMailboxService` SHALL create the directory with `mkdir_mode` permissions before writing.
3. WHILE a message file is being written THE `FileSystemMailboxService` SHALL use an atomic replace operation to prevent readers from observing partial data.
4. WHERE the filesystem mailbox is configured with `FileSystemMailboxConfig` THE service SHALL honor `base_path`, `poll_interval`, and `mkdir_mode` overrides.

### Requirement 2: Message Consumption & Lifecycle
**Objective:** As a Beast agent developer, I want inbound handlers to process filesystem messages consistently, so that inbox semantics match the Redis transport.

#### Acceptance Criteria
1. WHEN `FileSystemMailboxService` starts THEN the service SHALL poll the agent inbox on `poll_interval` cadence and dispatch each message exactly once to registered handlers.
2. WHEN a handler completes successfully THEN `FileSystemMailboxService` SHALL delete the processed message file from the inbox.
3. WHEN no handlers are registered THEN `FileSystemMailboxService` SHALL retain message files and log that no handlers are available.
4. IF a message file cannot be decoded THEN `FileSystemMailboxService` SHALL log an error and remove the corrupted file.

### Requirement 3: Operational Observability
**Objective:** As a Beast SRE, I want filesystem mailbox operations to surface actionable telemetry, so that operational issues can be diagnosed without Redis tooling.

#### Acceptance Criteria
1. WHEN directory creation fails THEN `FileSystemMailboxService` SHALL log the failure with the target path and propagate the exception.
2. WHEN the background poll loop encounters an unexpected exception THEN `FileSystemMailboxService` SHALL log the error and continue polling after the configured interval.
3. WHERE debug logging is enabled THE filesystem mailbox SHALL emit message send and receive events including message identifiers.
4. IF the service is stopped THEN `FileSystemMailboxService` SHALL cancel the polling task and suppress cancellation errors to allow graceful shutdown.

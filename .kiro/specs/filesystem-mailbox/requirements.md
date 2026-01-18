# Requirements Document

## Introduction
Beast Mailbox Core needs a same-host transport so Beast agents sharing a filesystem can exchange messages without Redis while preserving mailbox semantics, durability, and developer ergonomics.

## Requirements

### Requirement 1: Local Message Persistence
**Objective:** As a Beast platform engineer, I want filesystem-based outbound messaging, so that co-located agents can reliably persist messages without external services.

#### Acceptance Criteria
1. WHEN `FileSystemMailboxService` sends a message THEN the service SHALL persist the payload as a JSON file under `{base_path}/{recipient}/inbox`.
2. IF the recipient inbox directory does not exist THEN the service SHALL create the directory using the configured `mkdir_mode`.
3. WHILE a message file is being written THE service SHALL use an atomic temporary file and `os.replace` to avoid partial reads.
4. WHERE configuration overrides are provided THE service SHALL honor `base_path`, `poll_interval`, and `mkdir_mode`.

### Requirement 2: Message Consumption & Lifecycle
**Objective:** As a Beast agent developer, I want inbox handlers to process filesystem messages consistently, so that transport parity with Redis is maintained.

#### Acceptance Criteria
1. WHEN `FileSystemMailboxService` starts THEN it SHALL poll the inbox at `poll_interval` cadence and dispatch each message exactly once to registered handlers.
2. WHEN a handler completes successfully THEN the service SHALL delete the processed message file.
3. WHEN no handlers are registered THEN the service SHALL retain message files and log that no handlers are available.
4. IF a message file fails to decode THEN the service SHALL log the failure and remove the corrupted file.

### Requirement 3: Operational Observability
**Objective:** As a Beast SRE, I want filesystem mailbox operations to surface actionable telemetry, so that operational issues can be diagnosed quickly.

#### Acceptance Criteria
1. WHEN inbox directory creation fails THEN the service SHALL log the error with the target path and propagate the exception.
2. WHEN the polling loop encounters an unexpected exception THEN the service SHALL log the error and continue after the configured interval.
3. WHERE debug logging is enabled THE service SHALL emit send and receive events with message identifiers.
4. IF the service stops THEN it SHALL cancel the polling task and suppress cancellation errors to ensure graceful shutdown.
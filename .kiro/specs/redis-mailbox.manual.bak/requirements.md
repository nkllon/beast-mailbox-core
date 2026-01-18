# Requirements Document

## Introduction
Redis-backed mailbox transport provides Beast agents with durable, cross-host messaging using Redis Streams. The service must expose consistent async APIs, manage consumer groups automatically, and support environment-driven configuration for production deployments.

## Requirements

### Requirement 1: Redis Connectivity & Configuration
**Objective:** As a Beast platform engineer, I want the Redis mailbox to connect reliably using flexible configuration inputs, so that deployments can standardize without code changes.

#### Acceptance Criteria
1. WHEN `RedisMailboxService` initializes without explicit config THEN the service SHALL hydrate `MailboxConfig` from prioritized environment variables (`REDIS_HOST`/`PORT`/`PASSWORD`/`DB` before `REDIS_URL`).
2. IF mandatory Redis connection details are missing THEN `RedisMailboxService` SHALL fall back to localhost defaults.
3. WHEN the service connects to Redis THEN it SHALL authenticate with the configured credentials and raise descriptive errors on failure.
4. WHERE stream names are generated THE service SHALL prefix each inbox stream with `stream_prefix` and suffix with `:in`.

### Requirement 2: Message Delivery Semantics
**Objective:** As a Beast agent developer, I want to send and receive messages via Redis streams with at-least-once guarantees, so that agent handlers behave consistently across transports.

#### Acceptance Criteria
1. WHEN `RedisMailboxService` sends a message THEN it SHALL add an entry to the recipient stream with bounded length trimming (`MAXLEN`).
2. WHEN the consume loop runs THEN it SHALL read from the agent-specific consumer group and dispatch messages to registered handlers sequentially.
3. WHEN a handler completes without error THEN `RedisMailboxService` SHALL acknowledge the message (`XACK`) to prevent redelivery.
4. IF no handlers are registered THEN the service SHALL log the incoming message and retain it in the pending list.

### Requirement 3: Pending Message Recovery
**Objective:** As an operations engineer, I want the Redis mailbox to reclaim pending messages after restarts, so that at-least-once delivery is preserved across outages.

#### Acceptance Criteria
1. WHEN the service starts AND recovery is enabled THEN it SHALL check for existing consumer groups and pending entries before entering the consume loop.
2. WHEN pending messages exceed the configured idle threshold THEN `RedisMailboxService` SHALL claim them via `XAUTOCLAIM` and dispatch to handlers.
3. WHEN recovery completes THEN the service SHALL acknowledge all reclaimed message IDs and provide recovery metrics to the optional callback.
4. IF the consumer group does not exist THEN the service SHALL create it during startup without failing recovery.

### Requirement 4: Operational Resilience & Instrumentation
**Objective:** As a Beast SRE, I want visibility into Redis mailbox operations and graceful shutdown behavior, so that I can diagnose issues and recover cleanly.

#### Acceptance Criteria
1. WHEN consumer group creation encounters `BUSYGROUP` THEN `RedisMailboxService` SHALL log the condition and continue startup.
2. WHEN the consume loop encounters an unexpected exception THEN the service SHALL log the error and retry after the configured poll interval.
3. WHEN `stop()` is invoked THEN the service SHALL cancel the consume task, close the Redis client, and suppress cancellation errors.
4. WHERE a recovery callback is provided THE service SHALL invoke it after recovery attempts regardless of success or early exit.

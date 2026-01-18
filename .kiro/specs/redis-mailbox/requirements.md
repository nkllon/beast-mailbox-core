# Requirements Document

## Introduction
Redis-backed mailbox transport delivers durable, cross-host messaging for Beast agents using Redis Streams. The service must expose consistent async APIs, manage consumer groups automatically, and support environment-driven configuration for production deployments.

## Requirements

### Requirement 1: Redis Connectivity & Configuration
**Objective:** As a Beast platform engineer, I want flexible configuration for Redis connectivity, so that deployments can standardize without code changes.

#### Acceptance Criteria
1. WHEN `RedisMailboxService` initializes without explicit config THEN it SHALL hydrate `MailboxConfig` from prioritized environment variables (`REDIS_HOST`/`PORT`/`PASSWORD`/`DB` before `REDIS_URL`).
2. IF connection details are missing THEN the service SHALL fall back to localhost defaults.
3. WHEN connecting to Redis THEN the service SHALL authenticate and raise descriptive errors on failure.
4. WHERE stream names are generated THE service SHALL prefix each inbox stream with `stream_prefix` and suffix with `:in`.

### Requirement 2: Message Delivery Semantics
**Objective:** As a Beast agent developer, I want at-least-once delivery through Redis Streams, so that handlers behave consistently across transports.

#### Acceptance Criteria
1. WHEN `RedisMailboxService` sends a message THEN it SHALL add an entry to the recipient stream with bounded length trimming (`MAXLEN`).
2. WHEN the consume loop runs THEN it SHALL read from the agent-specific consumer group and dispatch messages to registered handlers sequentially.
3. WHEN a handler completes successfully THEN the service SHALL acknowledge the message (`XACK`) to prevent redelivery.
4. IF no handlers are registered THEN the service SHALL log the incoming message and retain it for later processing.

### Requirement 3: Pending Message Recovery
**Objective:** As an operations engineer, I want pending messages reclaimed after restarts, so that at-least-once delivery survives outages.

#### Acceptance Criteria
1. WHEN the service starts AND recovery is enabled THEN it SHALL check for existing consumer groups and pending entries before entering the consume loop.
2. WHEN pending messages exceed the idle threshold THEN it SHALL claim them via `XAUTOCLAIM` and dispatch to handlers.
3. WHEN recovery completes THEN the service SHALL acknowledge reclaimed message IDs and invoke the optional recovery callback with metrics.
4. IF the consumer group does not exist THEN the service SHALL create it during startup without failing recovery.

### Requirement 4: Operational Resilience & Instrumentation
**Objective:** As a Beast SRE, I want observability and graceful shutdown, so that Redis mailbox operations are diagnosable and safe.

#### Acceptance Criteria
1. WHEN consumer group creation encounters `BUSYGROUP` THEN the service SHALL log the condition and continue startup.
2. WHEN the consume loop encounters an unexpected exception THEN it SHALL log the error and retry after the configured poll interval.
3. WHEN `stop()` is invoked THEN the service SHALL cancel the consume task, close the Redis client, and suppress cancellation errors.
4. WHERE a recovery callback is provided THE service SHALL invoke it after every recovery attempt regardless of outcome.
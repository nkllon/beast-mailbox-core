# Requirements Document

## Introduction
Beast Mailbox Core must offer a CLI that controls mailbox services, inspects messages, and sends payloads so operators can interact with agents without writing code.

## Requirements

### Requirement 1: Service Lifecycle Control
**Objective:** As an operator, I want to start a streaming mailbox listener from the CLI, so that I can monitor inbound traffic for an agent.

#### Acceptance Criteria
1. WHEN `beast-mailbox-service <agent_id>` runs THEN it SHALL connect using the configured transport and begin streaming messages to stdout.
2. IF `--poll-interval` is provided THEN the CLI SHALL propagate the value to the underlying mailbox configuration.
3. WHILE streaming THE CLI SHALL handle SIGINT or termination signals by stopping the mailbox service gracefully.
4. WHERE verbose mode is enabled THE CLI SHALL surface debug logs for handler events and recovery actions.

### Requirement 2: One-Shot Inspection & Management
**Objective:** As an operator, I want to inspect and optionally acknowledge or delete messages, so that I can triage agent inboxes.

#### Acceptance Criteria
1. WHEN `beast-mailbox-service <agent_id> --latest` runs THEN it SHALL fetch the most recent messages without entering streaming mode.
2. IF `--ack` is provided THEN the CLI SHALL acknowledge the displayed messages via the mailbox service.
3. IF `--trim` is provided THEN the CLI SHALL delete the displayed messages after acknowledgment.
4. WHERE `--count N` is specified THE CLI SHALL limit inspection to `N` messages.

### Requirement 3: Message Sending
**Objective:** As a developer, I want to send structured messages from the CLI, so that I can trigger workflows during development or support.

#### Acceptance Criteria
1. WHEN `beast-mailbox-send <sender> <recipient>` runs with `--message` THEN it SHALL send a plain-text payload to the recipient mailbox.
2. WHEN the CLI receives `--json` THEN it SHALL parse the payload as JSON and send it using the mailbox service.
3. IF `--message-type` is provided THEN the CLI SHALL set the corresponding field on the outbound message.
4. IF both `--message` and `--json` are provided THEN the CLI SHALL raise a usage error indicating the conflict.

### Requirement 4: Configuration Overrides
**Objective:** As an operator, I want CLI flags to override environment-derived configuration, so that I can quickly target different backends.

#### Acceptance Criteria
1. WHEN `--redis-host`, `--redis-port`, `--redis-password`, or `--redis-db` are provided THEN the CLI SHALL pass those values to the mailbox configuration regardless of environment variables.
2. WHEN filesystem-specific overrides are provided (e.g., `--filesystem-root`) THEN the CLI SHALL apply them when the filesystem backend is active.
3. IF required configuration is missing after merging CLI flags and environment values THEN the CLI SHALL exit with a descriptive error message.
4. WHERE conflicting configuration sources exist THE CLI SHALL prioritize explicit CLI arguments over environment variables.
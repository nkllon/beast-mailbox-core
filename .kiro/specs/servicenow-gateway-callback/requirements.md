# Requirements Document

## Introduction
Beast Mailbox Core needs a ServiceNow integration gateway so that trusted ServiceNow workflows can post mailbox requests over secure REST and receive asynchronous callbacks that update the original ServiceNow records when Beast agents finish processing.

## Requirements

### Requirement 1: Secure Request Intake
**Objective:** As a ServiceNow platform owner, I want the gateway to authenticate and validate inbound requests, so that only authorized workflows can dispatch Beast mailbox messages.

#### Acceptance Criteria
1. WHEN ServiceNow sends a REST request to the gateway THEN the gateway SHALL verify client identity using configured OAuth or mutual TLS credentials before accepting the payload.
2. IF a request payload is missing required fields or violates schema THEN the gateway SHALL reject it with a descriptive 4xx response without touching Beast mailboxes.
3. WHERE rate limits are exceeded for a given credential THE gateway SHALL throttle additional requests and emit an audit log entry.
4. WHILE the gateway processes an accepted request THE gateway SHALL persist a correlation identifier linking the ServiceNow record to the Beast message.

### Requirement 2: Beast Dispatch and Callback Orchestration
**Objective:** As a Beast operator, I want mailbox requests from ServiceNow to be delivered asynchronously with completion callbacks, so that workflows can close the loop automatically.

#### Acceptance Criteria
1. WHEN the gateway validates a ServiceNow request THEN it SHALL construct a `MailboxMessage` and invoke the configured Beast mailbox transport without blocking on downstream handlers.
2. WHEN a Beast handler completes processing of a ServiceNow-originated message THEN the gateway SHALL receive a callback payload containing the original correlation identifier and outcome data.
3. IF the callback payload indicates a failure or retry requirement THEN the gateway SHALL relay that status to ServiceNow and preserve the message history for auditing.
4. WHERE callbacks must update multiple ServiceNow records THE gateway SHALL support mapping correlation identifiers to one or more target records defined in the original request.

### Requirement 3: ServiceNow Update Delivery
**Objective:** As a ServiceNow workflow author, I want completion callbacks to update incidents or service requests automatically, so that agents see Beast outcomes without manual effort.

#### Acceptance Criteria
1. WHEN the gateway receives a successful Beast callback THEN it SHALL invoke the configured ServiceNow REST endpoint to update the originating record’s state and append a work note containing the Beast response.
2. IF ServiceNow responds with a transient error THEN the gateway SHALL retry the update using exponential backoff up to a configurable limit.
3. WHEN ServiceNow confirms the update THEN the gateway SHALL mark the correlation as closed and expose the closure timestamp for reporting.
4. WHERE ServiceNow is unreachable for longer than the configured timeout window THE gateway SHALL escalate by logging an alert and leaving the correlation in a pending state for human intervention.

### Requirement 4: Observability and Compliance
**Objective:** As a compliance analyst, I want complete audit trails for cross-system interactions, so that investigations can reconstruct every request and callback event.

#### Acceptance Criteria
1. WHEN the gateway processes any inbound or outbound call THEN it SHALL emit structured logs that include correlation identifier, credential identifier, status code, and timestamps.
2. WHERE audit export is enabled THE gateway SHALL forward request and callback metadata to the Snowflake mailbox audit pipeline within one minute of occurrence.
3. IF suspicious activity such as repeated authentication failures occurs THEN the gateway SHALL trigger alerts using the existing monitoring stack.
4. WHILE data retention policies are in effect THE gateway SHALL purge stored payloads after the configured retention period while preserving audit metadata.


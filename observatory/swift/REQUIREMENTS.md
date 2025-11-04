# ObservatoryApp: High-level Requirements

This document defines the solution in requirements form. It is intentionally descriptive and technology-agnostic where possible, while remaining concrete enough for an agent to regenerate the implementation.

## 1. Purpose and Outcomes
- The system SHALL provide a macOS menu bar experience that indicates the health and recency of a background “observatory” synchronization process.
- The system SHALL allow a user to manually trigger a sync and receive feedback when it completes or fails.
- The system SHALL surface the “last successful sync” time and any recent error in a concise, glanceable UI.
- The system SHALL operate without blocking the UI and SHALL remain responsive during syncs and status updates.

## 2. Platforms and Runtime
- The system SHALL target macOS 13 or later.
- The system SHALL run as a menu bar application (status item) and SHALL not require a Dock icon.
- The system SHOULD be distributable as a standalone app or via Swift Package Manager executable target.

## 3. Core Functional Requirements
### 3.1 Menu Bar UI
- The system SHALL display a menu bar icon with a visual state:
  - “Healthy/Idle” state (e.g., green checkmark).
  - “Syncing” state (e.g., rotating arrows or progress indicator).
  - “Error” state (e.g., red warning triangle).
- The system SHALL present a popover or window-style menu containing:
  - A title identifying the app (“Beast Observatory” or configurable).
  - A “Last Sync” display:
    - If known: a human-friendly relative time (e.g., “5 minutes ago”).
    - If unknown: a suitable placeholder (e.g., “Never”).
  - An inline error display if a recent error exists.

### 3.2 Quick Actions
- The system SHALL provide a “Sync Now” action:
  - The action SHALL be disabled while a sync is already in progress.
  - The action SHALL initiate the sync process asynchronously.
- The system SHALL provide actions to:
  - Open a dashboard view (content may be minimal or stubbed).
  - Open a settings view (content may be minimal or stubbed).
  - View logs by opening a known log file path in the default viewer.
  - Quit the application.

### 3.3 Notifications
- The system SHALL request permission to show user notifications (time of prompt MAY be deferred to a user-initiated moment).
- The system SHALL present a local notification when:
  - A sync completes successfully.
  - A sync fails (including timeout and known error cases).

## 4. Sync Orchestration Requirements
### 4.1 Sync Trigger
- The system SHALL trigger a one-shot sync via an “observatory sync” service.
- The system SHALL support at least one “local process” execution mode:
  - The system SHALL attempt to execute a binary at a configurable or documented path (default: “/usr/local/bin/beast-observatory-sync”).
  - The system SHALL pass appropriate arguments to trigger a one-shot sync (default: “--one-shot”).

### 4.2 Async Behavior and Timeouts
- The system SHALL execute syncs asynchronously and SHALL NOT block the main/UI thread.
- The system SHALL provide a timeout for sync operations (default: 60 seconds).
- The system SHALL cancel or terminate the underlying process when a timeout occurs or when the operation is cancelled.
- The system SHALL surface a specific timeout error to the user (e.g., “Sync timed out after 60 seconds.”).

### 4.3 Status Reporting
- The system SHALL display “last successful sync time.”
- The system SHALL obtain the last sync time via at least one mechanism:
  - File-based: Read the modification date of a known log or state file (default path configurable; current default: “~/Library/Logs/beast-observatory/sync.log”).
- The system SHALL periodically refresh the last sync time (default: every 60 seconds).
- The system SHALL ensure periodic refresh is cancellable and does not leak resources.

### 4.4 Error Handling
- The system SHALL capture and present error states:
  - Non-zero exit codes from the process.
  - Timeouts.
  - Missing binary (command not found).
- The system SHALL log error details for diagnostics and agent follow-up.

## 5. Extensibility Requirements
### 5.1 Service Abstraction
- The system SHALL abstract the sync mechanism behind a protocol-based interface (e.g., “ObservatoryServicing”).
- The system SHALL allow multiple implementations (e.g., local process, HTTP client, mock) to be swapped with minimal change to UI or orchestration logic.

### 5.2 Optional HTTP Mode (Non-prescriptive)
- The system MAY support an alternative HTTP-based sync mode for debug/testing or production:
  - The app MAY select the HTTP service implementation at runtime based on environment variables (e.g., “OBS_SYNC_MODE=http”, “OBS_SYNC_ENDPOINT=…”).
  - The HTTP contract SHALL minimally support: “trigger sync” and “get last sync time.”
- The system SHALL NOT mandate any particular HTTP image or container; agents SHALL be free to provision their own service.

## 6. Logging and Observability
- The system SHALL use structured logging for key events:
  - Sync start/finish, exit status, timeout occurrence.
  - Notification authorization result.
  - Log file open attempts.
- The system SHOULD use platform logging facilities suitable for production diagnostics (e.g., `os.Logger`).
- Log messages SHALL be informative for agents and LLMs performing postmortems.

## 7. UX and Accessibility
- The system SHALL disable “Sync Now” while a sync is in progress.
- The system SHALL provide a small, glanceable display of status and last sync time.
- The system SHOULD include accessibility labels for status icons and key actions.

## 8. Configuration
- The system SHALL provide configurable parameters (via constants, environment variables, or settings) for:
  - Sync timeout duration.
  - Path to the local sync binary.
  - Log file path for last-sync inference.
- The system MAY expose these settings in a UI at a later stage; initial implementations MAY hard-code defaults.

## 9. Security and Distribution
- The system SHALL avoid hard-coding secrets.
- The system SHOULD be compatible with sandboxing requirements if targeted for App Store distribution:
  - If sandboxed, the system SHOULD avoid direct access to arbitrary log directories and MAY provide an in-app log viewer or use Application Support storage.

## 10. Testing Requirements
- The system SHALL be testable without the real service via protocol-based dependency injection.
- The system SHOULD include unit-testable logic for:
  - Sync state transitions (idle -> syncing -> success/error).
  - UI derivations based on state (icons, colors, disabled states).
- The system MAY support integration tests via Docker or other orchestration:
  - The system SHALL NOT dictate a specific container image; instead, the app SHALL be configurable to target an HTTP endpoint provided by the agent.

## 11. Non-functional Requirements
- Performance: The menu bar UI SHALL remain responsive during sync operations.
- Reliability: The system SHALL handle errors gracefully and present actionable feedback.
- Maintainability: The code SHALL be modular, with clear separation of concerns (UI, orchestration, service).
- Extensibility: The service layer SHALL be replaceable without UI changes.

## 12. Documentation Requirements
- The repository SHALL include a guidance document for agents (AGENTS.md) describing:
  - Architecture, components, and extension points.
  - Logging and error conventions.
  - Example, non-prescriptive mechanisms for providing an HTTP service (including Docker usage).
- The requirements (this document) SHALL be sufficiently descriptive for an agent to regenerate the implementation.

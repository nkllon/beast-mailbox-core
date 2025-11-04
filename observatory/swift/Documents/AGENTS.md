# AGENTS: ObservatoryApp Project Guidance

This document provides context and conventions for agents (human or automated) contributing to ObservatoryApp.

## Architecture Overview
- App Type: macOS menu bar app using SwiftUI + AppKit.
- Entry Point: `Sources/ObservatoryApp/MenuBarApp.swift` with `@main` app struct.
- Core Components:
  - `SyncStatusMonitor` (SwiftUI observable object, @MainActor): Manages sync state, notifications, and periodic status refresh.
  - `ObservatoryService` (service layer): Launches an external sync process (`/usr/local/bin/beast-observatory-sync`).
  - Views: `MenuBarView`, `DashboardView`, `SettingsView`.
- Dependency Injection: `ObservatoryServicing` protocol allows mocking `ObservatoryService` in tests.

## Key Behaviors
- Menu bar extra shows status icon and color based on sync state.
- User can trigger manual sync, open logs, open dashboard and settings.
- Periodic status updates every 60 seconds using a cancellable Task.
- Local notifications on sync completion/failure (UserNotifications framework).

## Concurrency & Process Execution
- `ObservatoryService.syncNow(timeout:)` is fully async and non-blocking.
  - Uses a termination handler + continuation.
  - Includes a timeout (default 60s) and cancellation handling.
  - Throws `ObservatoryError.timeout` on timeout; throws `.syncFailed(code)` otherwise.
- `SyncStatusMonitor.triggerSync()` prevents concurrent runs and uses `defer` for cleanup.

## Logging
- Use `Logger(subsystem: "ObservatoryApp", category: ...)` from `os` framework.
- Categories: `Sync`, `Notifications`.
- Log key events for LLM postmortems:
  - Start/finish of sync requests.
  - Exit status or timeout.
  - Notification permission results.
  - File open actions for logs.

## Error Handling & UX
- `ObservatoryError` includes `.timeout` with a friendly description.
- Timeouts are surfaced to users as: "Sync timed out after 60 seconds." and via a notification.
- Consider mapping common exit codes to user-friendly messages.

## Files & Structure
- Package manifest: `Package.swift` (no app code inside).
- Sources:
  - `Sources/ObservatoryApp/MenuBarApp.swift` (app, monitor, service, and protocol).
  - `Sources/ObservatoryApp/DashboardView.swift` (stub).
  - `Sources/ObservatoryApp/SettingsView.swift` (stub).
- Tests: `Tests/ObservatoryAppTests` (not populated yet).

## Testing Strategies
- Unit Tests (fast):
  - Implement a mock `ObservatoryServicing` to simulate success, failure, timeout.
  - Test `SyncStatusMonitor` state transitions (syncing -> success/error) and UI derivations (`statusIcon`, `statusColor`).
- Integration/Debug via Docker:
  - A Docker container can host the service under test. Parameterize endpoint or binary path via environment variables or build settings.
  - Add scripts to spin up/tear down the container for local runs or CI.

## Configuration & Extensibility
- Timeout: Adjust via `ObservatoryService.syncNow(timeout:)` or expose through Settings.
- Paths: The sync tool path is `/usr/local/bin/beast-observatory-sync`. Consider making this configurable for debug/testing.
- Logs: Currently opens `~/Library/Logs/beast-observatory/sync.log`. For sandboxed builds, consider Application Support and an in-app log viewer.

## Coding Conventions
- Prefer Swift Concurrency (async/await) and `@MainActor` for UI-bound types.
- Keep model state separate from presentation (e.g., store `Date`, format in view).
- Use dependency injection via protocols for testability.
- Avoid blocking the main thread; prefer async patterns and structured concurrency.

## Future Work Ideas
- Non-blocking process output capture (stdout/stderr) for richer error messages.
- Settings to configure timeout, log location, and binary path.
- Replace stubs with real `DashboardView` and `SettingsView` content.
- Add a small log viewer in-app.
- CI scripts to run Dockerized service for integration tests.

---

If you’re an automated agent, prefer minimal, focused diffs and keep this document updated when you introduce new patterns or decisions.

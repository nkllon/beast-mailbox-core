# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-10-10

### Added
- `--ack` flag for acknowledging messages after inspection in one-shot mode
- `--trim` flag for deleting messages from the stream
- Enhanced error handling for partial acknowledgement/deletion failures
- Clear logging with emoji indicators (✓ for ack, 🗑️ for trim)
- Consumer group auto-creation with BUSYGROUP error handling

### Changed
- Extended `_fetch_latest_messages` function with optional destructive operations
- Updated README with comprehensive documentation (610% size increase)
- Added CLI Options Reference section to README
- Added Best Practices and Safety Guidelines to README
- Added Troubleshooting section to README

### Fixed
- Improved error messages for Redis connection failures
- Better handling of partial ack/delete scenarios

### Meta
- ⚠️ **CRITICAL**: This release was retroactively synced to repository after being published to PyPI
- Repository integrity restored through PR (fix/sync-repo-with-v0.2.0)
- This represents a process failure that has been corrected
- Updated release procedures to prevent recurrence

## [0.1.0] - 2025-01-XX

### Added
- Initial release with Redis-backed mailbox utilities
- CLI tools: `beast-mailbox-service` and `beast-mailbox-send`
- Consumer groups per agent ID
- Async handler registration for inbound messages
- Streaming mailbox consumer with graceful shutdown
- One-shot message inspection mode
- Message sending utility with text/JSON payload support



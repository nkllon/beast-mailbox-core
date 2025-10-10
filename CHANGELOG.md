# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.2] - 2025-10-10

### Added
- Comprehensive test suite with 43 tests covering all functionality (84% coverage)
- pytest, pytest-asyncio, pytest-cov dev dependencies
- Automated coverage reporting (coverage.xml for SonarCloud)
- Tests for MailboxMessage, MailboxConfig, RedisMailboxService, and CLI
- AsyncIO lifecycle testing (start, stop, connect, message dispatching)
- CLI function tests (_fetch_latest_messages with all flags)
- SonarCloud integration with automated coverage upload

### Coverage Details
- __init__.py: 100%
- cli.py: 83% (only infinite event loops untested)
- redis_mailbox.py: 85% (only infinite consume loop untested)
- Overall: 84%

### Fixed
- Removed false claim of "21 tests" from v0.2.0 (tests didn't exist)
- Proper async mocking for non-blocking tests
- All tests complete in < 0.2 seconds

## [0.2.1] - 2025-10-10

### Fixed
- Added Python version classifiers to package metadata for proper badge display

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



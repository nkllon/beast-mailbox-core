# Local Testing Guide

## Running Tests Locally

All tests can be run locally. Some tests require Redis to be running.

### Quick Start (Docker)

```bash
# Start Redis
docker run -d -p 6379:6379 --name redis-test redis:latest

# Run all tests
pytest tests/ -v

# Run only fault injection tests (require Redis)
pytest tests/test_fault_injection.py -v

# Run only unit tests (no Redis needed)
pytest tests/test_redis_mailbox.py -v
```

### Alternative: Homebrew (macOS)

```bash
brew install redis
brew services start redis

# Verify Redis is running
redis-cli ping  # Should return: PONG

# Run tests
pytest tests/ -v
```

### Test Categories

**Unit Tests (No Redis needed):**
- `tests/test_redis_mailbox.py` - Uses mocks
- `tests/test_cli_functions.py` - Uses mocks
- `tests/test_recovery.py` - Uses mocks

**Integration Tests (Require Redis):**
- `tests/test_fault_injection.py` - Real Redis fault injection
- `tests/test_recovery_integration.py` - Real Redis recovery tests

Integration tests will skip automatically if Redis is not available.

### Troubleshooting

**Tests are skipped:**
- Check Redis is running: `redis-cli ping`
- Start Redis: `docker run -d -p 6379:6379 redis:latest`

**Connection refused:**
- Verify Redis is on port 6379: `docker ps`
- Check firewall settings

**Tests fail:**
- Ensure Redis is empty or using test DB (db=15)
- Check Redis logs: `docker logs redis-test`

#!/usr/bin/env python3
"""Tests for REDIS_URL environment variable support."""

import os
import pytest
from unittest.mock import AsyncMock, patch

from beast_mailbox_core.cli import parse_redis_url, get_redis_config_from_args
import beast_mailbox_core.cli as cli_module


class TestParseRedisUrl:
    """Test parse_redis_url() function."""

    def test_parse_full_url(self):
        """Test parsing a full Redis URL with all components."""
        result = parse_redis_url("redis://:password123@example.com:6380/5")
        assert result["host"] == "example.com"
        assert result["port"] == 6380
        assert result["password"] == "password123"
        assert result["db"] == 5

    def test_parse_url_without_password(self):
        """Test parsing URL without password."""
        result = parse_redis_url("redis://localhost:6379/0")
        assert result["host"] == "localhost"
        assert result["port"] == 6379
        assert result["password"] is None
        assert result["db"] == 0

    def test_parse_url_with_user_and_password(self):
        """Test parsing URL with username and password."""
        result = parse_redis_url("redis://user:pass@host:6379/1")
        assert result["host"] == "host"
        assert result["port"] == 6379
        assert result["password"] == "pass"
        assert result["db"] == 1

    def test_parse_url_with_empty_password(self):
        """Test parsing URL with empty password (colon but no password)."""
        result = parse_redis_url("redis://:mypass@host:6379/0")
        assert result["host"] == "host"
        assert result["password"] == "mypass"
        assert result["db"] == 0

    def test_parse_url_defaults_port(self):
        """Test that port defaults to 6379 if not specified."""
        result = parse_redis_url("redis://localhost/0")
        assert result["port"] == 6379
        assert result["host"] == "localhost"

    def test_parse_url_defaults_db(self):
        """Test that db defaults to 0 if not specified."""
        result = parse_redis_url("redis://localhost:6379")
        assert result["db"] == 0

    def test_parse_url_from_environment(self):
        """Test parsing from REDIS_URL environment variable."""
        with patch.dict(os.environ, {"REDIS_URL": "redis://:envpass@envhost:9999/7"}):
            result = parse_redis_url()
            assert result["host"] == "envhost"
            assert result["port"] == 9999
            assert result["password"] == "envpass"
            assert result["db"] == 7

    def test_parse_url_none_returns_empty(self):
        """Test that None URL returns empty dict."""
        with patch.dict(os.environ, {}, clear=True):
            result = parse_redis_url(None)
            assert result == {}

    def test_parse_url_empty_env_returns_empty(self):
        """Test that missing REDIS_URL returns empty dict."""
        with patch.dict(os.environ, {}, clear=True):
            result = parse_redis_url()
            assert result == {}

    def test_parse_url_invalid_scheme(self):
        """Test that invalid scheme raises SystemExit."""
        with pytest.raises(SystemExit):
            parse_redis_url("http://localhost:6379/0")

    def test_parse_url_rediss_scheme(self):
        """Test that rediss:// scheme is supported."""
        result = parse_redis_url("rediss://:pass@host:6380/1")
        assert result["host"] == "host"
        assert result["port"] == 6380
        assert result["password"] == "pass"
        assert result["db"] == 1

    def test_parse_url_invalid_db_number(self):
        """Test that invalid db number defaults to 0."""
        result = parse_redis_url("redis://localhost:6379/notanumber")
        assert result["db"] == 0


class TestGetRedisConfigFromArgs:
    """Test get_redis_config_from_args() priority handling."""

    def test_cli_overrides_environment(self):
        """Test that CLI flags override REDIS_URL."""
        args = type("Args", (), {
            "redis_host": "cli-host",
            "redis_port": 9999,
            "redis_password": "cli-pass",
            "redis_db": 2,
        })()
        
        with patch.dict(os.environ, {"REDIS_URL": "redis://:envpass@envhost:6379/5"}):
            result = get_redis_config_from_args(args)
            assert result["host"] == "cli-host"  # CLI wins
            assert result["port"] == 9999  # CLI wins
            assert result["password"] == "cli-pass"  # CLI wins
            assert result["db"] == 2  # CLI wins

    def test_environment_when_no_cli_flags(self):
        """Test that REDIS_URL is used when CLI flags not provided."""
        args = type("Args", (), {
            "redis_host": None,
            "redis_port": None,
            "redis_password": None,
            "redis_db": None,
        })()
        
        with patch.dict(os.environ, {"REDIS_URL": "redis://:envpass@envhost:8888/3"}):
            result = get_redis_config_from_args(args)
            assert result["host"] == "envhost"
            assert result["port"] == 8888
            assert result["password"] == "envpass"
            assert result["db"] == 3

    def test_defaults_when_no_env_or_cli(self):
        """Test defaults when neither REDIS_URL nor CLI flags provided."""
        args = type("Args", (), {
            "redis_host": None,
            "redis_port": None,
            "redis_password": None,
            "redis_db": None,
        })()
        
        with patch.dict(os.environ, {}, clear=True):
            result = get_redis_config_from_args(args)
            assert result["host"] == "localhost"
            assert result["port"] == 6379
            assert result["password"] is None
            assert result["db"] == 0

    def test_partial_cli_override(self):
        """Test that individual CLI flags override corresponding env values."""
        args = type("Args", (), {
            "redis_host": "override-host",
            "redis_port": None,  # Not overridden
            "redis_password": None,  # Not overridden
            "redis_db": 99,  # Overridden
        })()
        
        with patch.dict(os.environ, {"REDIS_URL": "redis://:envpass@envhost:8888/3"}):
            result = get_redis_config_from_args(args)
            assert result["host"] == "override-host"  # CLI
            assert result["port"] == 8888  # From env
            assert result["password"] == "envpass"  # From env
            assert result["db"] == 99  # CLI

    def test_default_values_prefer_env(self):
        """Test that CLI default values prefer REDIS_URL when available."""
        args = type("Args", (), {
            "redis_host": "localhost",  # Default value
            "redis_port": 6379,  # Default value
            "redis_password": None,  # Default value
            "redis_db": 0,  # Default value
        })()
        
        with patch.dict(os.environ, {"REDIS_URL": "redis://:envpass@envhost:8888/3"}):
            result = get_redis_config_from_args(args)
            # When CLI values match defaults, REDIS_URL is preferred
            assert result["host"] == "envhost"  # From REDIS_URL
            assert result["port"] == 8888  # From REDIS_URL
            assert result["password"] == "envpass"  # From REDIS_URL
            assert result["db"] == 3  # From REDIS_URL


class TestRedisUrlIntegration:
    """Integration tests for REDIS_URL in CLI commands."""

    @pytest.mark.asyncio
    async def test_service_with_redis_url(self):
        """Test that run_service_async uses REDIS_URL when set."""
        with patch.dict(os.environ, {"REDIS_URL": "redis://:testpass@testhost:9999/5"}):
            # Mock argparse args
            args = type("Args", (), {
                "agent_id": "test-agent",
                "redis_host": None,
                "redis_port": None,
                "redis_password": None,
                "redis_db": None,
                "stream_prefix": "test:mailbox",
                "maxlen": 1000,
                "poll_interval": 2.0,
                "latest": True,
                "count": 1,
                "ack": False,
                "trim": False,
                "echo": False,
            })()
            
            # Mock the service and its methods
            with patch("beast_mailbox_core.cli.RedisMailboxService") as mock_service_class:
                mock_service = AsyncMock()
                mock_service_class.return_value = mock_service
                mock_service.connect = AsyncMock()
                mock_service.stop = AsyncMock()
                mock_service.inbox_stream = "test:mailbox:test-agent:in"
                mock_service._client = AsyncMock()
                mock_service._client.xrevrange = AsyncMock(return_value=[])
                
                await cli_module.run_service_async(args)
                
                # Verify service was created with config from REDIS_URL
                mock_service_class.assert_called_once()
                call_args = mock_service_class.call_args
                config = call_args[1]["config"]
                assert config.host == "testhost"
                assert config.port == 9999
                assert config.password == "testpass"
                assert config.db == 5

    @pytest.mark.asyncio
    async def test_send_message_with_redis_url(self):
        """Test that send_message_async uses REDIS_URL when set."""
        with patch.dict(os.environ, {"REDIS_URL": "redis://:sendpass@sendhost:7777/2"}):
            args = type("Args", (), {
                "sender": "alice",
                "recipient": "bob",
                "message": "test",
                "json": None,
                "message_type": "direct_message",
                "redis_host": None,
                "redis_port": None,
                "redis_password": None,
                "redis_db": None,
                "stream_prefix": "test:mailbox",
            })()
            
            with patch("beast_mailbox_core.cli.RedisMailboxService") as mock_service_class:
                mock_service = AsyncMock()
                mock_service_class.return_value = mock_service
                mock_service.send_message = AsyncMock(return_value="msg-id-123")
                mock_service.stop = AsyncMock()
                
                await cli_module.send_message_async(args)
                
                # Verify service was created with config from REDIS_URL
                mock_service_class.assert_called_once()
                call_args = mock_service_class.call_args
                config = call_args[1]["config"]
                assert config.host == "sendhost"
                assert config.port == 7777
                assert config.password == "sendpass"
                assert config.db == 2


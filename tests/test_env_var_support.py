#!/usr/bin/env python3
"""Tests for environment variable support in RedisMailboxService.

Tests that RedisMailboxService reads from environment variables when config=None.
"""

import os
import pytest
from unittest.mock import patch

from beast_mailbox_core.redis_mailbox import MailboxConfig, RedisMailboxService


class TestEnvironmentVariableSupport:
    """Test RedisMailboxService reads from environment variables."""

    def test_reads_from_redis_host_env_var(self):
        """Test that REDIS_HOST is read when config=None."""
        with patch.dict(os.environ, {
            "REDIS_HOST": "prod-redis.example.com",
            "REDIS_PORT": "6380",
            "REDIS_PASSWORD": "secret123",
            "REDIS_DB": "2",
        }, clear=False):
            service = RedisMailboxService("test-agent", config=None)
            
            assert service.config.host == "prod-redis.example.com"
            assert service.config.port == 6380
            assert service.config.password == "secret123"
            assert service.config.db == 2
            assert service.config.stream_prefix == "beast:mailbox"
            assert service.config.enable_recovery is True

    def test_reads_from_redis_url_when_host_not_set(self):
        """Test that REDIS_URL is used when REDIS_HOST is not set."""
        with patch.dict(os.environ, {
            "REDIS_URL": "redis://:mypassword@redis-cluster.example.com:6379/1",
        }, clear=False):
            # Clear REDIS_HOST if it exists
            env = os.environ.copy()
            env.pop("REDIS_HOST", None)
            env.pop("REDIS_PORT", None)
            env.pop("REDIS_PASSWORD", None)
            env.pop("REDIS_DB", None)
            
            with patch.dict(os.environ, env, clear=True):
                service = RedisMailboxService("test-agent", config=None)
                
                assert service.config.host == "redis-cluster.example.com"
                assert service.config.port == 6379
                assert service.config.password == "mypassword"
                assert service.config.db == 1

    def test_redis_host_takes_priority_over_redis_url(self):
        """Test that REDIS_HOST takes priority over REDIS_URL."""
        with patch.dict(os.environ, {
            "REDIS_HOST": "priority-host.example.com",
            "REDIS_PORT": "9999",
            "REDIS_URL": "redis://:urlpass@url-host.example.com:6379/0",
        }, clear=False):
            service = RedisMailboxService("test-agent", config=None)
            
            # Should use REDIS_HOST values, not REDIS_URL
            assert service.config.host == "priority-host.example.com"
            assert service.config.port == 9999

    def test_defaults_to_localhost_when_no_env_vars(self):
        """Test that defaults to localhost:6379 when no env vars are set."""
        # Clear all Redis-related env vars
        env = os.environ.copy()
        env.pop("REDIS_HOST", None)
        env.pop("REDIS_PORT", None)
        env.pop("REDIS_PASSWORD", None)
        env.pop("REDIS_DB", None)
        env.pop("REDIS_URL", None)
        
        with patch.dict(os.environ, env, clear=False):
            service = RedisMailboxService("test-agent", config=None)
            
            assert service.config.host == "localhost"
            assert service.config.port == 6379
            assert service.config.password is None
            assert service.config.db == 0

    def test_explicit_config_still_works(self):
        """Test that explicit MailboxConfig still works (backward compatible)."""
        with patch.dict(os.environ, {
            "REDIS_HOST": "env-host.example.com",
            "REDIS_PASSWORD": "env-password",
        }, clear=False):
            # Explicit config should override env vars
            explicit_config = MailboxConfig(
                host="explicit-host.example.com",
                port=8888,
                password="explicit-password",
                db=3,
            )
            service = RedisMailboxService("test-agent", config=explicit_config)
            
            # Should use explicit config, not env vars
            assert service.config.host == "explicit-host.example.com"
            assert service.config.port == 8888
            assert service.config.password == "explicit-password"
            assert service.config.db == 3

    def test_partial_env_vars_use_defaults(self):
        """Test that partial env vars use defaults for missing values."""
        with patch.dict(os.environ, {
            "REDIS_HOST": "custom-host.example.com",
            # REDIS_PORT not set - should default to 6379
            # REDIS_PASSWORD not set - should be None
            "REDIS_DB": "5",
        }, clear=False):
            service = RedisMailboxService("test-agent", config=None)
            
            assert service.config.host == "custom-host.example.com"
            assert service.config.port == 6379  # Default
            assert service.config.password is None  # Default
            assert service.config.db == 5

    def test_redis_url_without_password(self):
        """Test REDIS_URL parsing without password."""
        env = os.environ.copy()
        env.pop("REDIS_HOST", None)
        env.pop("REDIS_PORT", None)
        env.pop("REDIS_PASSWORD", None)
        env.pop("REDIS_DB", None)
        
        with patch.dict(os.environ, {
            "REDIS_URL": "redis://redis.example.com:6380/2",
        }, clear=False):
            service = RedisMailboxService("test-agent", config=None)
            
            assert service.config.host == "redis.example.com"
            assert service.config.port == 6380
            assert service.config.password is None
            assert service.config.db == 2

    def test_redis_url_default_port_and_db(self):
        """Test REDIS_URL with default port and db."""
        env = os.environ.copy()
        env.pop("REDIS_HOST", None)
        env.pop("REDIS_PORT", None)
        env.pop("REDIS_PASSWORD", None)
        env.pop("REDIS_DB", None)
        
        with patch.dict(os.environ, {
            "REDIS_URL": "redis://:password@redis.example.com",
        }, clear=False):
            service = RedisMailboxService("test-agent", config=None)
            
            assert service.config.host == "redis.example.com"
            assert service.config.port == 6379  # Default
            assert service.config.password == "password"
            assert service.config.db == 0  # Default

    def test_invalid_redis_url_falls_back_to_defaults(self):
        """Test that invalid REDIS_URL falls back to defaults."""
        env = os.environ.copy()
        env.pop("REDIS_HOST", None)
        
        with patch.dict(os.environ, {
            "REDIS_URL": "invalid://not-a-redis-url",
        }, clear=False):
            # Should log warning but not crash
            service = RedisMailboxService("test-agent", config=None)
            
            # Should fall back to defaults
            assert service.config.host == "localhost"
            assert service.config.port == 6379

    def test_rediss_scheme_supported(self):
        """Test that rediss:// scheme is supported."""
        env = os.environ.copy()
        env.pop("REDIS_HOST", None)
        
        with patch.dict(os.environ, {
            "REDIS_URL": "rediss://:password@secure-redis.example.com:6380/3",
        }, clear=False):
            service = RedisMailboxService("test-agent", config=None)
            
            assert service.config.host == "secure-redis.example.com"
            assert service.config.port == 6380
            assert service.config.password == "password"
            assert service.config.db == 3

    def test_config_none_vs_not_provided(self):
        """Test that config=None and omitting config both read from env."""
        with patch.dict(os.environ, {
            "REDIS_HOST": "env-host.example.com",
            "REDIS_PORT": "1234",
        }, clear=False):
            # Both should behave the same
            service1 = RedisMailboxService("test-agent", config=None)
            service2 = RedisMailboxService("test-agent")  # config=None is default
            
            assert service1.config.host == service2.config.host
            assert service1.config.port == service2.config.port


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


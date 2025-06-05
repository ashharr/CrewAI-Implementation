"""
Tests for configuration management.
"""

import pytest
from src.shared.config import get_settings, Settings


def test_get_settings():
    """Test that settings can be loaded."""
    settings = get_settings()
    assert isinstance(settings, Settings)
    assert settings.environment == "development"
    assert settings.debug is True


def test_database_settings():
    """Test database configuration."""
    settings = get_settings()
    assert settings.database.host == "localhost"
    assert settings.database.port == 5432
    assert settings.database.name == "ai_agent_platform"


def test_redis_settings():
    """Test Redis configuration."""
    settings = get_settings()
    assert settings.redis.host == "localhost"
    assert settings.redis.port == 6379
    assert settings.redis.db == 0


def test_jwt_settings():
    """Test JWT configuration."""
    settings = get_settings()
    assert settings.jwt.algorithm == "HS256"
    assert settings.jwt.access_token_expire_minutes == 30
    assert settings.jwt.refresh_token_expire_days == 7 
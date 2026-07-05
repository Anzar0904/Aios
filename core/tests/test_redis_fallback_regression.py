import os
from unittest.mock import MagicMock, patch

import pytest
from aios.services.persistence_impl import (
    FakeRedisClient,
    RedisConfigurationService,
    RedisConnectionManager,
)


# Explicitly exclude this regression test file from inheriting the
# autouse conftest environment variables so we can test the environment
# switching behavior accurately.
@pytest.fixture(autouse=True)
def clean_env():
    old_env = os.environ.get("AIOS_ENV")
    old_fallback = os.environ.get("REDIS_FALLBACK_ENABLED")

    # Clean them up for these specific tests
    os.environ.pop("AIOS_ENV", None)
    os.environ.pop("REDIS_FALLBACK_ENABLED", None)

    yield

    if old_env is not None:
        os.environ["AIOS_ENV"] = old_env
    else:
        os.environ.pop("AIOS_ENV", None)

    if old_fallback is not None:
        os.environ["REDIS_FALLBACK_ENABLED"] = old_fallback
    else:
        os.environ.pop("REDIS_FALLBACK_ENABLED", None)


def test_production_mode_redis_unavailable_raises():
    """Production mode must never silently fall back; it must raise on failure."""
    os.environ["AIOS_ENV"] = "production"
    os.environ["REDIS_FALLBACK_ENABLED"] = "true"  # Should be ignored in production

    # Configure to use a non-existent port to force connection failure
    config = RedisConfigurationService()
    config.host = "127.0.0.1"
    config.port = 9999  # invalid port
    config.awaiting_configuration = False

    conn_manager = RedisConnectionManager(config)

    # In production, connecting to unavailable Redis should raise an exception
    with pytest.raises(Exception):  # noqa: B017
        conn_manager.connect()


def test_development_mode_fallback_enabled():
    """Development/Test mode with fallback enabled should return FakeRedisClient on failure."""
    os.environ["AIOS_ENV"] = "development"
    os.environ["REDIS_FALLBACK_ENABLED"] = "true"

    config = RedisConfigurationService()
    config.host = "127.0.0.1"
    config.port = 9999  # invalid port
    config.awaiting_configuration = False

    conn_manager = RedisConnectionManager(config)

    client = conn_manager.connect()
    assert isinstance(client, FakeRedisClient)
    assert client.ping() is True


def test_development_mode_fallback_disabled_raises():
    """Development/Test mode with fallback disabled must raise on failure."""
    os.environ["AIOS_ENV"] = "development"
    os.environ["REDIS_FALLBACK_ENABLED"] = "false"

    config = RedisConfigurationService()
    config.host = "127.0.0.1"
    config.port = 9999  # invalid port
    config.awaiting_configuration = False

    conn_manager = RedisConnectionManager(config)

    with pytest.raises(Exception):  # noqa: B017
        conn_manager.connect()


def test_successful_redis_reconnection():
    """If Redis becomes available later, connection manager should successfully reconnect."""
    os.environ["AIOS_ENV"] = "production"
    os.environ["REDIS_FALLBACK_ENABLED"] = "false"

    config = RedisConfigurationService()
    config.host = "127.0.0.1"
    config.port = 6379
    config.awaiting_configuration = False

    conn_manager = RedisConnectionManager(config)

    # Mock redis client ping to raise exception first, then return True
    mock_redis = MagicMock()
    mock_redis.ping.side_effect = [Exception("Connection lost"), True, True]

    with patch("redis.Redis", return_value=mock_redis):
        # First attempt: connection fails, raises exception
        with pytest.raises(Exception, match="Connection lost"):
            conn_manager.connect()

        # Second attempt: connection succeeds
        client = conn_manager.connect()
        assert client == mock_redis
        assert client.ping() is True

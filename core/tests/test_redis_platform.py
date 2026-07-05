import os
import pytest
from typing import Dict, Any, List
from unittest.mock import MagicMock

from aios.services.persistence import (
    RedisTransport,
    RedisProvider,
    RedisRuntimeService,
)

from aios.services.persistence_impl import (
    RedisConfigurationService,
    RedisConnectionManager,
    RedisTransportImpl,
    RedisProviderImpl,
    RedisTelemetry,
    RedisStatistics,
    RedisDiagnostics,
    RedisHealthMonitor,
    RedisValidator,
    RedisReportGenerator,
    RedisRuntimeServiceImpl,
    FakeRedisClient,
)


@pytest.fixture
def redis_env():
    # Setup test configuration
    config = RedisConfigurationService()
    config.host = "127.0.0.1"
    config.port = 6379
    config.awaiting_configuration = False

    conn_manager = RedisConnectionManager(config)
    transport = RedisTransportImpl(config, conn_manager)
    provider = RedisProviderImpl(transport)

    telemetry = RedisTelemetry()
    stats = RedisStatistics(telemetry)
    diag = RedisDiagnostics(conn_manager)
    health = RedisHealthMonitor(transport)
    validator = RedisValidator()
    report_gen = RedisReportGenerator(os.getcwd(), None)

    service = RedisRuntimeServiceImpl(
        config,
        transport,
        provider,
        health,
        diag,
        telemetry,
        stats,
        validator,
        report_gen
    )
    report_gen.runtime_service = service

    # Initialize all lifecycle services
    config.initialize()
    conn_manager.initialize()
    transport.initialize()
    provider.initialize()
    telemetry.initialize()
    stats.initialize()
    diag.initialize()
    health.initialize()
    validator.initialize()
    report_gen.initialize()
    service.initialize()

    return {
        "config": config,
        "conn_manager": conn_manager,
        "transport": transport,
        "provider": provider,
        "telemetry": telemetry,
        "stats": stats,
        "diagnostics": diag,
        "health": health,
        "validator": validator,
        "service": service,
        "report_gen": report_gen,
    }


def test_redis_configuration(redis_env):
    cfg = redis_env["config"]
    assert cfg.host == "127.0.0.1"
    assert cfg.port == 6379
    assert cfg.awaiting_configuration is False


def test_fake_redis_client():
    # Verify our inline Fake client matches basic Redis behaviors
    client = FakeRedisClient()
    assert client.ping() is True

    # Test GET/SET
    assert client.set("key1", "value1") is True
    assert client.get("key1") == "value1"

    # Test EXISTS
    assert client.exists("key1") is True

    # Test DELETE
    assert client.delete("key1") is True
    assert client.get("key1") is None
    assert client.exists("key1") is False


def test_redis_transport_and_provider(redis_env):
    transport = redis_env["transport"]
    provider = redis_env["provider"]

    # Connect to the transport (which falls back to FakeRedisClient dynamically)
    transport.connect()
    assert transport.is_connected() is True

    # Set value via provider
    assert provider.set("aios:v1:test_ws:test_proj:sub:entity:val", "hello") is True
    assert provider.get("aios:v1:test_ws:test_proj:sub:entity:val") == "hello"
    assert provider.exists("aios:v1:test_ws:test_proj:sub:entity:val") is True

    # Delete value
    assert provider.delete("aios:v1:test_ws:test_proj:sub:entity:val") is True
    assert provider.get("aios:v1:test_ws:test_proj:sub:entity:val") is None


def test_keyspace_validator(redis_env):
    validator = redis_env["validator"]
    
    # Valid key
    assert len(validator.validate_key("aios:v1:ws:proj:subsystem:entity:purpose")) == 0

    # Invalid key
    errors = validator.validate_key("invalid_key_prefix:test")
    assert len(errors) > 0
    assert any("Keyspace naming violation" in e for e in errors)


def test_telemetry_and_statistics(redis_env):
    telemetry = redis_env["telemetry"]
    stats = redis_env["stats"]

    # Record some queries
    telemetry.record_query(5.5, True)
    telemetry.record_query(10.5, True)
    telemetry.record_query(15.0, False)

    m = stats.get_metrics()
    assert m["queries_recorded"] == 3
    assert m["failed_queries"] == 1
    assert pytest.approx(m["average_latency_ms"], 0.1) == 10.33


def test_diagnostics_and_recommendations(redis_env):
    service = redis_env["service"]
    diag = redis_env["diagnostics"]
    conn_manager = redis_env["conn_manager"]

    # Trigger some simulated failures
    conn_manager.connection_failures = 5

    # Check diagnostics
    d = diag.get_diagnostics()
    assert d["status"] == "degraded"
    assert len(d["remediations"]) > 0

    # Check recommendations
    recs = service.get_recommendations()
    assert len(recs) > 0
    assert recs[0]["severity"] == "WARNING"


def test_report_generation(redis_env):
    service = redis_env["service"]
    service.generate_reports()

    # Verify reports were successfully generated in docs/persistence/
    r_dir = os.path.join(os.getcwd(), "docs", "persistence")
    assert os.path.exists(os.path.join(r_dir, "REDIS_PLATFORM_STATUS.md"))
    assert os.path.exists(os.path.join(r_dir, "REDIS_PLATFORM_HEALTH.md"))
    assert os.path.exists(os.path.join(r_dir, "REDIS_PLATFORM_STATISTICS.md"))
    assert os.path.exists(os.path.join(r_dir, "REDIS_PLATFORM_DIAGNOSTICS.md"))

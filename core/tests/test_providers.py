from aios.providers.interface import universal_health_registry


def test_provider_health_and_metrics():
    universal_health_registry.update_health(
        "openai",
        available=True,
        latency_ms=100.0,
        last_error=None,
        success_rate=1.0,
        failure_rate=0.0,
        health_score=100.0,
    )
    assert universal_health_registry.get_health("openai").available is True

    universal_health_registry.update_health(
        "openai",
        available=False,
        latency_ms=500.0,
        last_error="Timeout",
        success_rate=0.0,
        failure_rate=1.0,
        health_score=0.0,
    )
    assert universal_health_registry.get_health("openai").available is False


def test_provider_fallback_execution():
    assert True  # Moved to omniroute tests

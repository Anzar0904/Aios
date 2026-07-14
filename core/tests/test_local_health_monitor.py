"""
tests/test_local_health_monitor.py

Tests for Phase 1: LocalHealthMonitor — model health tracking and diagnostics.
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch

import pytest
from aios.local.discovery import ModelStatus, ModelType, OllamaDiscovery, OllamaModelMetadata
from aios.local.health_monitor import LocalHealthMonitor, ModelHealthStatus

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_meta(name: str, is_embed: bool = False) -> OllamaModelMetadata:
    return OllamaModelMetadata(
        name=name,
        size_bytes=8_000_000_000,
        modified_at="2025-01-01T00:00:00Z",
        model_type=ModelType.EMBEDDING if is_embed else ModelType.CHAT,
        status=ModelStatus.INSTALLED,
    )


INSTALLED_MODELS = [
    _make_meta("deepseek-coder-v2:16b"),
    _make_meta("gemma3:4b"),
    _make_meta("mxbai-embed-large:latest", is_embed=True),
]


@pytest.fixture
def mock_discovery():
    disc = MagicMock(spec=OllamaDiscovery)
    disc.discover.return_value = INSTALLED_MODELS
    disc.is_available.return_value = True
    return disc


@pytest.fixture
def monitor(mock_discovery):
    return LocalHealthMonitor(discovery=mock_discovery)


# ---------------------------------------------------------------------------
# Tests: refresh
# ---------------------------------------------------------------------------


class TestHealthMonitorRefresh:
    def test_refresh_populates_installed_models(self, monitor):
        with patch("httpx.Client") as mock_cls:
            client = MagicMock()
            client.__enter__ = MagicMock(return_value=client)
            client.__exit__ = MagicMock(return_value=False)
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {"models": []}  # No running models
            client.get.return_value = resp
            mock_cls.return_value = client
            statuses = monitor.refresh()

        assert "deepseek-coder-v2:16b" in statuses
        assert "gemma3:4b" in statuses
        assert "mxbai-embed-large:latest" in statuses

    def test_refresh_marks_installed_models_as_installed(self, monitor):
        with patch("httpx.Client") as mock_cls:
            client = MagicMock()
            client.__enter__ = MagicMock(return_value=client)
            client.__exit__ = MagicMock(return_value=False)
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {"models": []}
            client.get.return_value = resp
            mock_cls.return_value = client
            statuses = monitor.refresh()

        for name in ["deepseek-coder-v2:16b", "gemma3:4b"]:
            assert statuses[name].installed is True

    def test_refresh_detects_running_model(self, monitor):
        ps_response = {
            "models": [{"name": "deepseek-coder-v2:16b", "size_vram": 8 * 1024 * 1024 * 1024}]
        }
        with patch("httpx.Client") as mock_cls:
            client = MagicMock()
            client.__enter__ = MagicMock(return_value=client)
            client.__exit__ = MagicMock(return_value=False)
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = ps_response
            client.get.return_value = resp
            mock_cls.return_value = client
            statuses = monitor.refresh()

        assert statuses["deepseek-coder-v2:16b"].running is True
        assert statuses["deepseek-coder-v2:16b"].status == ModelStatus.RUNNING

    def test_refresh_marks_non_running_as_not_running(self, monitor):
        with patch("httpx.Client") as mock_cls:
            client = MagicMock()
            client.__enter__ = MagicMock(return_value=client)
            client.__exit__ = MagicMock(return_value=False)
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {"models": []}  # No running models
            client.get.return_value = resp
            mock_cls.return_value = client
            statuses = monitor.refresh()

        for name in ["gemma3:4b", "mxbai-embed-large:latest"]:
            assert statuses[name].running is False


# ---------------------------------------------------------------------------
# Tests: record_inference
# ---------------------------------------------------------------------------


class TestRecordInference:
    def test_records_successful_inference(self, monitor):
        monitor.record_inference(
            "gemma3:4b", success=True, latency_ms=500.0, tokens_per_second=25.0
        )
        status = monitor.get_status("gemma3:4b")
        assert status is not None
        assert status.success_count == 1
        assert status.total_requests == 1
        assert status.failure_count == 0

    def test_records_failed_inference(self, monitor):
        monitor.record_inference("gemma3:4b", success=False, latency_ms=100.0, error="timeout")
        status = monitor.get_status("gemma3:4b")
        assert status.failure_count == 1
        assert status.last_error == "timeout"

    def test_updates_last_used_timestamp(self, monitor):
        before = time.time()
        monitor.record_inference("gemma3:4b", success=True, latency_ms=200.0)
        status = monitor.get_status("gemma3:4b")
        assert status.last_used is not None
        assert status.last_used >= before

    def test_rolling_average_latency(self, monitor):
        monitor.record_inference("gemma3:4b", success=True, latency_ms=100.0)
        monitor.record_inference("gemma3:4b", success=True, latency_ms=300.0)
        status = monitor.get_status("gemma3:4b")
        assert status.avg_latency_ms == pytest.approx(200.0, rel=0.01)

    def test_rolling_average_tps(self, monitor):
        monitor.record_inference(
            "gemma3:4b", success=True, latency_ms=100.0, tokens_per_second=10.0
        )
        monitor.record_inference(
            "gemma3:4b", success=True, latency_ms=100.0, tokens_per_second=30.0
        )
        status = monitor.get_status("gemma3:4b")
        assert status.tokens_per_second == pytest.approx(20.0, rel=0.01)

    def test_success_rate_calculation(self, monitor):
        monitor.record_inference("model:1b", success=True, latency_ms=100.0)
        monitor.record_inference("model:1b", success=True, latency_ms=100.0)
        monitor.record_inference("model:1b", success=False, latency_ms=100.0)
        status = monitor.get_status("model:1b")
        assert status.success_rate == pytest.approx(2 / 3, rel=0.01)


# ---------------------------------------------------------------------------
# Tests: health score
# ---------------------------------------------------------------------------


class TestHealthScore:
    def test_new_model_has_zero_failure_count(self, monitor):
        h = ModelHealthStatus(model_name="test:1b", installed=True)
        assert h.failure_count == 0

    def test_health_score_100_for_healthy_model(self, monitor):
        h = ModelHealthStatus(model_name="test:1b", installed=True, failure_count=0)
        assert h.health_score == 100.0

    def test_health_score_0_for_missing_model(self, monitor):
        h = ModelHealthStatus(model_name="test:1b", installed=False)
        assert h.health_score == 0.0

    def test_health_score_decreases_with_failures(self, monitor):
        h = ModelHealthStatus(model_name="test:1b", installed=True, failure_count=5)
        assert h.health_score < 100.0

    def test_health_score_decreases_with_high_latency(self, monitor):
        h_low_latency = ModelHealthStatus(model_name="t", installed=True, avg_latency_ms=100.0)
        h_high_latency = ModelHealthStatus(model_name="t2", installed=True, avg_latency_ms=10000.0)
        assert h_low_latency.health_score >= h_high_latency.health_score


# ---------------------------------------------------------------------------
# Tests: doctor
# ---------------------------------------------------------------------------


class TestDoctor:
    def test_doctor_returns_dict(self, monitor, mock_discovery):
        with patch("httpx.Client") as mock_cls:
            client = MagicMock()
            client.__enter__ = MagicMock(return_value=client)
            client.__exit__ = MagicMock(return_value=False)
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {"models": []}
            client.get.return_value = resp
            mock_cls.return_value = client
            report = monitor.doctor()

        assert isinstance(report, dict)
        assert "ollama_online" in report
        assert "installed_count" in report
        assert "running_count" in report
        assert "model_health" in report

    def test_doctor_reports_ollama_online(self, monitor, mock_discovery):
        mock_discovery.is_available.return_value = True
        with patch("httpx.Client") as mock_cls:
            client = MagicMock()
            client.__enter__ = MagicMock(return_value=client)
            client.__exit__ = MagicMock(return_value=False)
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {"models": []}
            client.get.return_value = resp
            mock_cls.return_value = client
            report = monitor.doctor()

        assert report["ollama_online"] is True

    def test_doctor_includes_recommendations_when_failures(self, monitor):
        monitor.record_inference("gemma3:4b", success=False, latency_ms=100.0)
        monitor.record_inference("gemma3:4b", success=False, latency_ms=100.0)
        monitor.record_inference("gemma3:4b", success=False, latency_ms=100.0)
        monitor.record_inference("gemma3:4b", success=False, latency_ms=100.0)
        monitor.record_inference("gemma3:4b", success=False, latency_ms=100.0)
        monitor.record_inference("gemma3:4b", success=False, latency_ms=100.0)

        with patch("httpx.Client") as mock_cls:
            client = MagicMock()
            client.__enter__ = MagicMock(return_value=client)
            client.__exit__ = MagicMock(return_value=False)
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = {"models": []}
            client.get.return_value = resp
            mock_cls.return_value = client
            report = monitor.doctor()

        assert len(report["recommendations"]) > 0

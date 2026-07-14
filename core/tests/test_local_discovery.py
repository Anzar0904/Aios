"""
tests/test_local_discovery.py

Tests for Phase 1: OllamaDiscovery — automatic model detection.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from aios.local.discovery import ModelStatus, ModelType, OllamaDiscovery, OllamaModelMetadata

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_raw_model(
    name: str,
    size: int = 8_000_000_000,
    family: str = "",
    parameter_size: str = "14B",
    modified_at: str = "2025-01-01T00:00:00Z",
) -> dict:
    return {
        "name": name,
        "size": size,
        "modified_at": modified_at,
        "digest": "sha256:abc123",
        "details": {
            "family": family or name.split(":")[0],
            "parameter_size": parameter_size,
            "quantization_level": "Q4_K_M",
        },
    }


MOCK_API_RESPONSE = {
    "models": [
        _make_raw_model("deepseek-coder-v2:16b", family="deepseek-coder-v2"),
        _make_raw_model("qwen2.5-coder:14b", family="qwen2.5-coder"),
        _make_raw_model("deepseek-r1:14b", family="deepseek-r1"),
        _make_raw_model("mxbai-embed-large:latest", size=669_615_493, family="mxbai"),
        _make_raw_model("gemma3:4b", size=3_338_801_804, family="gemma3"),
        _make_raw_model("gemma3:12b", size=8_149_190_253, family="gemma3"),
        _make_raw_model("mistral-small:24b", family="mistral-small"),
        _make_raw_model("qwen3-coder:30b", family="qwen3-coder"),
        _make_raw_model("qwen3.5:9b", family="qwen3.5"),
        _make_raw_model("qwen3.6:27b", family="qwen3.6"),
    ]
}


@pytest.fixture
def discovery():
    return OllamaDiscovery(base_url="http://localhost:11434", cache_ttl=60.0)


@pytest.fixture
def mock_httpx_response():
    """Returns a callable that produces a mock httpx response."""

    def _make(status_code: int = 200, json_data: dict = None):
        response = MagicMock()
        response.status_code = status_code
        response.json.return_value = json_data or MOCK_API_RESPONSE
        response.raise_for_status = MagicMock()
        return response

    return _make


# ---------------------------------------------------------------------------
# Tests: is_available
# ---------------------------------------------------------------------------


class TestOllamaDiscoveryAvailability:
    def test_is_available_returns_true_when_ollama_responds(self, discovery, mock_httpx_response):
        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.return_value = mock_httpx_response(200)
            mock_client_cls.return_value = mock_client
            assert discovery.is_available() is True

    def test_is_available_returns_false_when_connection_fails(self, discovery):
        import httpx as real_httpx

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.side_effect = real_httpx.ConnectError("refused")
            mock_client_cls.return_value = mock_client
            assert discovery.is_available() is False


# ---------------------------------------------------------------------------
# Tests: discover
# ---------------------------------------------------------------------------


class TestOllamaDiscovery:
    def _patch_client(self, mock_client_cls, json_data=None):
        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = json_data or MOCK_API_RESPONSE
        resp.raise_for_status = MagicMock()
        mock_client.get.return_value = resp
        mock_client_cls.return_value = mock_client

    def test_discover_returns_list_of_metadata(self, discovery):
        with patch("httpx.Client") as mock_client_cls:
            self._patch_client(mock_client_cls)
            models = discovery.discover(force=True)

        assert isinstance(models, list)
        assert len(models) == 10

    def test_discover_returns_correct_names(self, discovery):
        with patch("httpx.Client") as mock_client_cls:
            self._patch_client(mock_client_cls)
            models = discovery.discover(force=True)

        names = [m.name for m in models]
        assert "deepseek-coder-v2:16b" in names
        assert "mxbai-embed-large:latest" in names

    def test_discover_classifies_embedding_model(self, discovery):
        with patch("httpx.Client") as mock_client_cls:
            self._patch_client(mock_client_cls)
            models = discovery.discover(force=True)

        mxbai = next(m for m in models if "mxbai" in m.name)
        assert mxbai.model_type == ModelType.EMBEDDING
        assert mxbai.is_embedding_model is True

    def test_discover_classifies_chat_models(self, discovery):
        with patch("httpx.Client") as mock_client_cls:
            self._patch_client(mock_client_cls)
            models = discovery.discover(force=True)

        chat_models = [
            m for m in models if "embed" not in m.name.lower() and "mxbai" not in m.name.lower()
        ]
        for m in chat_models:
            assert m.model_type == ModelType.CHAT

    def test_discover_returns_size_bytes(self, discovery):
        with patch("httpx.Client") as mock_client_cls:
            self._patch_client(mock_client_cls)
            models = discovery.discover(force=True)

        deepseek = next(m for m in models if m.name == "deepseek-coder-v2:16b")
        assert deepseek.size_bytes == 8_000_000_000
        assert deepseek.size_gb > 0

    def test_discover_resolves_context_length(self, discovery):
        with patch("httpx.Client") as mock_client_cls:
            self._patch_client(mock_client_cls)
            models = discovery.discover(force=True)

        deepseek = next(m for m in models if "deepseek-r1" in m.name)
        assert deepseek.context_length == 131072

    def test_discover_caches_results(self, discovery):
        call_count = 0

        def counting_client(*args, **kwargs):
            nonlocal call_count
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            resp = MagicMock()
            resp.json.return_value = MOCK_API_RESPONSE
            resp.raise_for_status = MagicMock()
            mock_client.get.return_value = resp
            call_count += 1
            return mock_client

        with patch("httpx.Client", side_effect=counting_client):
            discovery.discover(force=True)
            discovery.discover()  # Should use cache
            discovery.discover()  # Should use cache

        assert call_count == 1, "Should query API only once within cache TTL"

    def test_discover_force_bypasses_cache(self, discovery):
        call_count = 0

        def counting_client(*args, **kwargs):
            nonlocal call_count
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            resp = MagicMock()
            resp.json.return_value = MOCK_API_RESPONSE
            resp.raise_for_status = MagicMock()
            mock_client.get.return_value = resp
            call_count += 1
            return mock_client

        with patch("httpx.Client", side_effect=counting_client):
            discovery.discover(force=True)
            discovery.discover(force=True)

        assert call_count == 2

    def test_discover_raises_on_connection_error(self, discovery):
        import httpx as real_httpx

        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.side_effect = real_httpx.ConnectError("refused")
            mock_client_cls.return_value = mock_client
            with pytest.raises(ConnectionError):
                discovery.discover(force=True)

    def test_discover_all_statuses_are_installed(self, discovery):
        with patch("httpx.Client") as mock_client_cls:
            self._patch_client(mock_client_cls)
            models = discovery.discover(force=True)

        for m in models:
            assert m.status == ModelStatus.INSTALLED

    def test_discover_invalidate_cache_forces_refresh(self, discovery):
        with patch("httpx.Client") as mock_client_cls:
            self._patch_client(mock_client_cls)
            discovery.discover(force=True)

        discovery.invalidate_cache()
        assert discovery._last_discovery == 0.0
        assert discovery._cached_models == []


# ---------------------------------------------------------------------------
# Tests: get_running_models
# ---------------------------------------------------------------------------


class TestGetRunningModels:
    def test_returns_running_model_names(self, discovery):
        ps_data = {"models": [{"name": "deepseek-coder-v2:16b"}]}
        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            resp = MagicMock()
            resp.status_code = 200
            resp.json.return_value = ps_data
            mock_client.get.return_value = resp
            mock_client_cls.return_value = mock_client
            running = discovery.get_running_models()

        assert "deepseek-coder-v2:16b" in running

    def test_returns_empty_on_api_error(self, discovery):
        with patch("httpx.Client") as mock_client_cls:
            mock_client = MagicMock()
            mock_client.__enter__ = MagicMock(return_value=mock_client)
            mock_client.__exit__ = MagicMock(return_value=False)
            mock_client.get.side_effect = Exception("network error")
            mock_client_cls.return_value = mock_client
            running = discovery.get_running_models()

        assert running == []


# ---------------------------------------------------------------------------
# Tests: OllamaModelMetadata properties
# ---------------------------------------------------------------------------


class TestModelMetadataProperties:
    def test_size_gb_calculated_correctly(self):
        meta = OllamaModelMetadata(
            name="test:7b",
            size_bytes=7_000_000_000,
            modified_at="",
        )
        assert meta.size_gb == round(7_000_000_000 / (1024**3), 2)

    def test_is_embedding_model_false_for_chat(self):
        meta = OllamaModelMetadata(
            name="gemma3:4b",
            size_bytes=1_000_000,
            modified_at="",
            model_type=ModelType.CHAT,
        )
        assert meta.is_embedding_model is False
        assert meta.is_chat_model is True

    def test_is_embedding_model_true_for_embed(self):
        meta = OllamaModelMetadata(
            name="mxbai-embed-large",
            size_bytes=500_000_000,
            modified_at="",
            model_type=ModelType.EMBEDDING,
        )
        assert meta.is_embedding_model is True
        assert meta.is_chat_model is False

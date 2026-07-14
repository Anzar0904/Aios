"""
tests/test_local_loader.py

Tests for Phase 1: LocalModelLoader — dynamic model loading and unloading.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from aios.local.loader import InferenceResult, LocalModelLoader

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_client(status_code=200, json_data=None):
    """Returns a context-manager-compatible mock httpx.Client."""
    client = MagicMock()
    client.__enter__ = MagicMock(return_value=client)
    client.__exit__ = MagicMock(return_value=False)
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.raise_for_status = MagicMock()
    client.post.return_value = resp
    client.get.return_value = resp
    return client


GENERATE_RESPONSE = {
    "model": "deepseek-coder-v2:16b",
    "message": {
        "role": "assistant",
        "content": "Hello! Here is the function:\n```python\ndef foo(): pass\n```",
    },
    "done": True,
    "prompt_eval_count": 15,
    "eval_count": 42,
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def loader():
    return LocalModelLoader(base_url="http://localhost:11434", auto_unload=True)


# ---------------------------------------------------------------------------
# Tests: load
# ---------------------------------------------------------------------------


class TestModelLoad:
    def test_load_returns_success_result(self, loader):
        with patch("httpx.Client", return_value=_mock_client(json_data={"done": True})):
            result = loader.load("gemma3:4b")

        assert result.success is True
        assert result.model_name == "gemma3:4b"
        assert result.load_time_ms >= 0

    def test_load_sets_active_model(self, loader):
        with patch("httpx.Client", return_value=_mock_client(json_data={"done": True})):
            loader.load("gemma3:4b")

        assert loader.active_model == "gemma3:4b"

    def test_load_same_model_returns_success_without_api_call(self, loader):
        with patch("httpx.Client", return_value=_mock_client(json_data={"done": True})):
            loader.load("gemma3:4b")

        # Second load of same model should be a no-op
        call_count = 0

        def counting_client(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return _mock_client(json_data={"done": True})

        with patch("httpx.Client", side_effect=counting_client):
            result = loader.load("gemma3:4b")

        assert result.success is True
        assert call_count == 0  # No new API call needed

    def test_load_different_model_unloads_previous(self, loader):
        with patch("httpx.Client", return_value=_mock_client(json_data={"done": True})):
            loader.load("gemma3:4b")
            loader.load("deepseek-coder-v2:16b")

        assert loader.active_model == "deepseek-coder-v2:16b"

    def test_load_returns_error_on_api_failure(self, loader):
        with patch("httpx.Client") as mock_cls:
            client = _mock_client()
            client.post.side_effect = Exception("Connection refused")
            mock_cls.return_value = client
            result = loader.load("nonexistent-model:1b")

        assert result.success is False
        assert result.error is not None


# ---------------------------------------------------------------------------
# Tests: unload
# ---------------------------------------------------------------------------


class TestModelUnload:
    def test_unload_clears_active_model(self, loader):
        with patch("httpx.Client", return_value=_mock_client(json_data={"done": True})):
            loader.load("gemma3:4b")
            loader.unload("gemma3:4b")

        assert loader.active_model is None

    def test_unload_returns_true_on_success(self, loader):
        with patch("httpx.Client", return_value=_mock_client(status_code=200)):
            loader._active_model = "gemma3:4b"  # Simulate loaded state
            result = loader.unload("gemma3:4b")

        assert result is True

    def test_unload_without_target_unloads_active(self, loader):
        with patch("httpx.Client", return_value=_mock_client(json_data={"done": True})):
            loader.load("gemma3:4b")
            loader.unload()

        assert loader.active_model is None

    def test_unload_no_active_returns_true(self, loader):
        result = loader.unload()
        assert result is True

    def test_unload_on_api_error_returns_false(self, loader):
        with patch("httpx.Client") as mock_cls:
            client = _mock_client()
            client.post.side_effect = Exception("network error")
            mock_cls.return_value = client
            loader._active_model = "gemma3:4b"
            result = loader.unload("gemma3:4b")

        assert result is False


# ---------------------------------------------------------------------------
# Tests: generate
# ---------------------------------------------------------------------------


class TestGenerate:
    def test_generate_returns_inference_result(self, loader):
        loader._active_model = "deepseek-coder-v2:16b"
        with patch("httpx.Client", return_value=_mock_client(json_data=GENERATE_RESPONSE)):
            result = loader.generate("deepseek-coder-v2:16b", "Write a function")

        assert isinstance(result, InferenceResult)
        assert result.success is True
        assert "foo" in result.response

    def test_generate_sets_model_name(self, loader):
        loader._active_model = "deepseek-coder-v2:16b"
        with patch("httpx.Client", return_value=_mock_client(json_data=GENERATE_RESPONSE)):
            result = loader.generate("deepseek-coder-v2:16b", "test prompt")

        assert result.model_name == "deepseek-coder-v2:16b"

    def test_generate_records_inference_time(self, loader):
        loader._active_model = "deepseek-coder-v2:16b"
        with patch("httpx.Client", return_value=_mock_client(json_data=GENERATE_RESPONSE)):
            result = loader.generate("deepseek-coder-v2:16b", "test prompt")

        assert result.inference_time_ms >= 0

    def test_generate_counts_tokens(self, loader):
        loader._active_model = "deepseek-coder-v2:16b"
        with patch("httpx.Client", return_value=_mock_client(json_data=GENERATE_RESPONSE)):
            result = loader.generate("deepseek-coder-v2:16b", "test prompt")

        assert result.tokens_estimated == 15 + 42  # prompt + eval

    def test_generate_returns_failure_on_api_error(self, loader):
        loader._active_model = "deepseek-coder-v2:16b"
        with patch("httpx.Client") as mock_cls:
            client = _mock_client()
            client.post.side_effect = Exception("timeout")
            mock_cls.return_value = client
            result = loader.generate("deepseek-coder-v2:16b", "test")

        assert result.success is False
        assert result.error is not None

    def test_generate_auto_loads_model(self, loader):
        """generate() should auto-load if model not active."""
        with patch("httpx.Client", return_value=_mock_client(json_data=GENERATE_RESPONSE)):
            loader.generate("deepseek-coder-v2:16b", "prompt")

        # Even after auto-load, the model should be active
        assert loader.active_model == "deepseek-coder-v2:16b"


# ---------------------------------------------------------------------------
# Tests: execute_and_unload
# ---------------------------------------------------------------------------


class TestExecuteAndUnload:
    def test_execute_and_unload_returns_result(self, loader):
        with patch("httpx.Client", return_value=_mock_client(json_data=GENERATE_RESPONSE)):
            result = loader.execute_and_unload("deepseek-coder-v2:16b", "test")

        assert result.success is True

    def test_execute_and_unload_clears_active_model(self, loader):
        with patch("httpx.Client", return_value=_mock_client(json_data=GENERATE_RESPONSE)):
            loader.execute_and_unload("deepseek-coder-v2:16b", "test")

        assert loader.active_model is None


# ---------------------------------------------------------------------------
# Tests: Single model invariant
# ---------------------------------------------------------------------------


class TestSingleModelInvariant:
    def test_only_one_model_active_at_a_time(self, loader):
        """Loading a second model should unload the first."""
        with patch("httpx.Client", return_value=_mock_client(json_data={"done": True})):
            loader.load("gemma3:4b")
            assert loader.active_model == "gemma3:4b"
            loader.load("deepseek-r1:14b")
            assert loader.active_model == "deepseek-r1:14b"
            # Only one model should be active
            assert loader.active_model != "gemma3:4b"


# ---------------------------------------------------------------------------
# Tests: event history
# ---------------------------------------------------------------------------


class TestEventHistory:
    def test_load_event_logged(self, loader):
        with patch("httpx.Client", return_value=_mock_client(json_data={"done": True})):
            loader.load("gemma3:4b")

        history = loader.get_load_history()
        load_events = [e for e in history if e["event"] == "load"]
        assert len(load_events) == 1
        assert load_events[0]["model"] == "gemma3:4b"

    def test_unload_event_logged(self, loader):
        with patch("httpx.Client", return_value=_mock_client(json_data={"done": True})):
            loader.load("gemma3:4b")
            loader.unload("gemma3:4b")

        history = loader.get_load_history()
        unload_events = [e for e in history if e["event"] == "unload"]
        assert len(unload_events) == 1

    def test_history_capped_at_1000_entries(self, loader):
        for i in range(1100):
            loader._log_event("test", "model", 1.0)

        assert len(loader.get_load_history()) <= 1000

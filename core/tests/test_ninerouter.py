import json
from unittest.mock import MagicMock, patch

import httpx
import pytest
from aios.cli import execute_builtin_cli_command
from aios.providers.interface import (
    RoutingRequest,
    universal_model_registry,
    universal_provider_registry,
    universal_routing_engine,
)
from aios.providers.ninerouter import NineRouterProvider, discover_9router, generate_9router_reports


@pytest.fixture
def mock_httpx_client():
    """Fixture to mock httpx.Client context manager and responses."""
    with patch("httpx.Client") as mock_client_cls:
        mock_client = MagicMock()
        mock_client_cls.return_value.__enter__.return_value = mock_client
        yield mock_client


def test_ninerouter_health_check_success(mock_httpx_client):
    """Verify that NineRouterProvider.health() returns True on HTTP 200."""
    provider = NineRouterProvider(base_url="http://localhost:8080/v1")
    
    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_httpx_client.get.return_value = mock_res
    
    assert provider.health() is True
    mock_httpx_client.get.assert_called_once_with(
        "http://localhost:8080/v1/models", headers={"Authorization": "Bearer 9router-api-key"}
    )


def test_ninerouter_health_check_failure(mock_httpx_client):
    """Verify that NineRouterProvider.health() returns False on exception."""
    provider = NineRouterProvider()
    mock_httpx_client.get.side_effect = httpx.RequestError("Connection refused")
    
    assert provider.health() is False


def test_ninerouter_generate(mock_httpx_client):
    """Verify that generate sends correct payload and parses response."""
    provider = NineRouterProvider()
    mock_res = MagicMock()
    mock_res.json.return_value = {
        "choices": [{"message": {"content": "Hello from 9Router"}}]
    }
    mock_httpx_client.post.return_value = mock_res
    
    res = provider.generate(model="gpt-4o", prompt="ping")
    assert res == "Hello from 9Router"
    mock_httpx_client.post.assert_called_once()
    
    # Check payload structure
    args, kwargs = mock_httpx_client.post.call_args
    assert args[0] == "http://localhost:8080/v1/chat/completions"
    payload = kwargs["json"]
    assert payload["model"] == "gpt-4o"
    assert payload["messages"][-1]["content"] == "ping"


def test_ninerouter_stream(mock_httpx_client):
    """Verify streaming generator yields text chunks."""
    provider = NineRouterProvider()
    
    # Mock Client.stream as a context manager
    mock_response = MagicMock()
    mock_response.iter_lines.return_value = [
        "data: {\"choices\": [{\"delta\": {\"content\": \"Chunk 1\"}}]}",
        "data: {\"choices\": [{\"delta\": {\"content\": \"Chunk 2\"}}]}",
        "data: [DONE]",
    ]
    mock_httpx_client.stream.return_value.__enter__.return_value = mock_response
    
    chunks = list(provider.stream(model="gpt-4o", prompt="stream me"))
    assert chunks == ["Chunk 1", "Chunk 2"]


def test_discovery_and_model_registration(mock_httpx_client):
    """Verify that discover_9router registers models with correct capability flags."""
    provider = NineRouterProvider()
    
    mock_res = MagicMock()
    mock_res.status_code = 200
    mock_res.json.return_value = {
        "data": [
            {"id": "qwen-coder-32b"},
            {"id": "deepseek-r1-reasoning"},
            {"id": "gpt-4o-vision"},
            {"id": "text-embedding-ada-002"},
        ]
    }
    mock_httpx_client.get.return_value = mock_res
    
    res = discover_9router(provider, force=True)
    assert res["online"] is True
    assert "qwen-coder-32b" in res["models"]
    
    # Check that they were registered
    model_coder = universal_model_registry.get_model("qwen-coder-32b")
    assert model_coder is not None
    assert model_coder.supports_coding is True
    assert model_coder.supports_reasoning is False
    
    model_reasoner = universal_model_registry.get_model("deepseek-r1-reasoning")
    assert model_reasoner is not None
    assert model_reasoner.supports_reasoning is True
    
    model_vision = universal_model_registry.get_model("gpt-4o-vision")
    assert model_vision is not None
    assert model_vision.supports_vision is True


def test_discovery_offline_fallback(mock_httpx_client):
    """Verify discovery loads from cache file when server is offline."""
    provider = NineRouterProvider()
    mock_httpx_client.get.side_effect = Exception("Offline")
    
    # Setup mock cache file content
    cache_data = ["gpt-4o-cached", "claude-cached"]
    with patch("pathlib.Path.exists", return_value=True), \
         patch("pathlib.Path.read_text", return_value=json.dumps(cache_data)):
        res = discover_9router(provider, force=True)
        assert res["online"] is False
        assert res["models"] == cache_data


def test_omniroute_routing_integration(mock_httpx_client):
    """Verify OmniRoute routes requests to 9Router when online."""
    provider = NineRouterProvider()
    
    # Mock provider health to True
    with patch.object(provider, "health", return_value=True):
        universal_provider_registry.register(provider)
        
        # Register a coding model under ninerouter
        from aios.providers.interface import ModelInfo
        universal_model_registry.register_model(
            ModelInfo(
                provider="ninerouter",
                model_id="qwen-coder-mock",
                display_name="Qwen Coder Mock",
                family="Qwen",
                supports_coding=True,
            )
        )
        
        req = RoutingRequest(task_type="coding")
        decision = universal_routing_engine.route(req)
        
        assert decision.provider == "ninerouter"
        assert decision.model in ("qwen-coder-mock", "qwen-coder-32b")


def test_cli_commands():
    """Verify that CLI commands executes successfully without raising."""
    provider = NineRouterProvider()
    with patch.object(provider, "health", return_value=True):
        universal_provider_registry.register(provider)
        
        with patch("sys.exit") as mock_exit:
            # Test status command
            execute_builtin_cli_command(["providers", "status"], exit_on_complete=True)
            mock_exit.assert_called_with(0)
            
            # Test config command
            execute_builtin_cli_command(["providers", "config"], exit_on_complete=True)
            mock_exit.assert_called_with(0)


def test_report_generation():
    """Verify docs reports are written cleanly."""
    with patch("pathlib.Path.write_text") as mock_write:
        generate_9router_reports()
        assert mock_write.call_count == 4

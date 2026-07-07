import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest
from aios.bootstrap import bootstrap_kernel
from aios.providers import (
    OmniRouteRequest,
    RoutingRequest,
    universal_omniroute_engine,
    universal_routing_engine,
)
from aios.providers.interface import (
    universal_model_registry,
    universal_provider_registry,
)


def test_nvidia_provider_foundation_registration():
    """Verify that the NVIDIA provider registers automatically and routes via OmniRoute."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.toml"
        config_path.write_text("[model]\ndefault = 'mock-model'\n", encoding="utf-8")

        def mock_subprocess_run(cmd, **kwargs):
            mock_res = MagicMock()
            mock_res.returncode = 0
            mock_res.stdout = "main"
            return mock_res

        with patch("subprocess.run", side_effect=mock_subprocess_run):
            # Set environment API key to simulate active state
            os.environ["NVIDIA_API_KEY"] = "nv-mock-key-12345"

            # Bootstrap the kernel, which executes registration
            kernel = bootstrap_kernel(config_path)
            assert kernel is not None

            # Verify provider registration
            nvidia_provider = universal_provider_registry.lookup("nvidia")
            assert nvidia_provider is not None
            assert nvidia_provider.name == "nvidia"
            assert nvidia_provider.health() is True

            # Verify model registration
            model_id = "nvidia/nemotron-4-340b-instruct"
            model_info = universal_model_registry.get_model(model_id)
            assert model_info is not None
            assert model_info.provider == "nvidia"
            assert model_info.supports_coding is True

            # Verify routing engine resolves the provider
            req = RoutingRequest(
                task_type="coding",
                estimated_input_tokens=100,
                estimated_output_tokens=100,
                preferred_provider="nvidia",
                preferred_model=model_id,
            )
            decision = universal_routing_engine.route(req)
            assert decision is not None
            assert decision.provider == "nvidia"
            assert decision.model == model_id

            # Verify OmniRoute execution with mock HTTP response
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": (
                                "[NVIDIA Inference API response from "
                                "nvidia/nemotron-4-340b-instruct]"
                            ),
                        }
                    }
                ]
            }

            omni_req = OmniRouteRequest(
                prompt="Write a quicksort in python",
                task_type="coding",
                preferred_provider="nvidia",
                preferred_model=model_id,
            )

            with patch("httpx.Client.post", return_value=mock_response) as mock_post:
                response = universal_omniroute_engine.execute(omni_req)
                assert response is not None
                assert response.provider == "nvidia"
                assert response.model == model_id
                assert "NVIDIA Inference API response" in response.content
                mock_post.assert_called_once()


def test_nvidia_provider_authentication_failure():
    """Verify that a 401 Unauthorized response raises the expected RuntimeError."""
    nvidia_provider = universal_provider_registry.lookup("nvidia")
    assert nvidia_provider is not None

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized API key"

    with patch("httpx.Client.post", return_value=mock_response):
        with pytest.raises(RuntimeError, match="NVIDIA authentication failed"):
            nvidia_provider.generate(
                model="nvidia/nemotron-4-340b-instruct",
                prompt="Hello",
            )


def test_nvidia_provider_rate_limiting():
    """Verify that a 429 Too Many Requests response raises the expected RuntimeError."""
    nvidia_provider = universal_provider_registry.lookup("nvidia")
    assert nvidia_provider is not None

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.text = "Too Many Requests"

    with patch("httpx.Client.post", return_value=mock_response):
        with pytest.raises(RuntimeError, match="NVIDIA rate limit exceeded"):
            nvidia_provider.generate(
                model="nvidia/nemotron-4-340b-instruct",
                prompt="Hello",
            )


def test_nvidia_provider_timeout_failure():
    """Verify that a network timeout raises the expected RuntimeError."""
    nvidia_provider = universal_provider_registry.lookup("nvidia")
    assert nvidia_provider is not None

    with patch("httpx.Client.post", side_effect=httpx.TimeoutException("Request timed out")):
        with pytest.raises(RuntimeError, match="NVIDIA API request timed out"):
            nvidia_provider.generate(
                model="nvidia/nemotron-4-340b-instruct",
                prompt="Hello",
            )


def test_cli_provider_list():
    """Verify that aios provider list routes correctly non-interactively."""
    with patch("sys.argv", ["aios", "provider", "list"]), \
         patch("aios.cli.bootstrap_kernel") as mock_bootstrap, \
         patch("sys.exit", side_effect=SystemExit) as mock_exit:
        mock_kernel = MagicMock()
        mock_bootstrap.return_value = mock_kernel

        try:
            from aios.cli import main
            main()
        except SystemExit:
            pass

        mock_kernel.boot.assert_called_once()
        mock_exit.assert_called_once_with(0)


def test_cli_model_list():
    """Verify that aios model list routes correctly non-interactively."""
    with patch("sys.argv", ["aios", "model", "list"]), \
         patch("aios.cli.bootstrap_kernel") as mock_bootstrap, \
         patch("sys.exit", side_effect=SystemExit) as mock_exit:
        mock_kernel = MagicMock()
        mock_bootstrap.return_value = mock_kernel

        try:
            from aios.cli import main
            main()
        except SystemExit:
            pass

        mock_kernel.boot.assert_called_once()
        mock_exit.assert_called_once_with(0)


def test_cli_health():
    """Verify that aios health routes correctly non-interactively."""
    with patch("sys.argv", ["aios", "health"]), \
         patch("aios.cli.bootstrap_kernel") as mock_bootstrap, \
         patch("sys.exit", side_effect=SystemExit) as mock_exit:
        mock_kernel = MagicMock()
        mock_bootstrap.return_value = mock_kernel

        try:
            from aios.cli import main
            main()
        except SystemExit:
            pass

        mock_kernel.boot.assert_called_once()
        mock_exit.assert_called_once_with(0)


def test_cli_route():
    """Verify that aios route routes correctly non-interactively."""
    with patch("sys.argv", ["aios", "route", "chat"]), \
         patch("aios.cli.bootstrap_kernel") as mock_bootstrap, \
         patch("sys.exit", side_effect=SystemExit) as mock_exit:
        mock_kernel = MagicMock()
        mock_bootstrap.return_value = mock_kernel

        try:
            from aios.cli import main
            main()
        except SystemExit:
            pass

        mock_kernel.boot.assert_called_once()
        mock_exit.assert_called_once_with(0)

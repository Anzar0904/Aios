"""
# ruff: noqa: E501
aios/providers/nvidia.py

NVIDIA Inference API provider implementation.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Iterator, List, Optional

import httpx

from aios.providers.interface import (
    AIProvider,
    ModelInfo,
    ProviderCapabilities,
    ProviderCost,
    ProviderHealth,
    ProviderQuota,
    universal_capability_registry,
    universal_cost_registry,
    universal_health_registry,
    universal_model_registry,
    universal_provider_registry,
    universal_quota_registry,
)

logger = logging.getLogger(__name__)


class NVIDIAProviderAdapter:
    """Separates the NVIDIA Inference API request/response translation from AI OS routing logic."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.environ.get("NVIDIA_API_KEY")
        self.base_url = "https://integrate.api.nvidia.com/v1"

    def translate_request(
        self, model: str, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Translates generic AI OS arguments to NVIDIA Inference API payload."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1024),
            "top_p": kwargs.get("top_p", 1.0),
        }
        return payload

    def translate_response(self, response_data: Dict[str, Any]) -> str:
        """Translates raw response JSON structure from NVIDIA API to standard string."""
        try:
            return response_data["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to translate NVIDIA response: {e}")
            raise RuntimeError(f"Failed to parse model response from NVIDIA: {e}") from e

    def execute_completion(
        self, model: str, prompt: str, system_prompt: Optional[str] = None, **kwargs: Any
    ) -> str:
        """Sends HTTPS request to NVIDIA API with error handling."""
        if not self.api_key:
            raise ValueError("NVIDIA_API_KEY is not set. Cannot authenticate request.")

        payload = self.translate_request(model, prompt, system_prompt, **kwargs)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self.base_url}/chat/completions"
        timeout = float(kwargs.get("timeout", 30.0))

        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(url, headers=headers, json=payload)

                # Check status codes and handle errors
                if response.status_code == 200:
                    return self.translate_response(response.json())

                # 401 Unauthorized
                elif response.status_code == 401:
                    logger.error("NVIDIA Authentication failed: Invalid API key.")
                    raise RuntimeError(
                        "NVIDIA authentication failed. Please check your NVIDIA_API_KEY."
                    )

                # 429 Rate Limit
                elif response.status_code == 429:
                    logger.error("NVIDIA Rate Limit exceeded (429).")
                    raise RuntimeError("NVIDIA rate limit exceeded. Please try again later.")

                # 400 / 404 Invalid Models / Bad Request
                elif response.status_code in (400, 404):
                    err_msg = response.json().get("error", {}).get("message", response.text)
                    logger.error(
                        f"NVIDIA Invalid Request/Model ({response.status_code}): {err_msg}"
                    )
                    raise RuntimeError(f"NVIDIA API request failed: {err_msg}")

                # 5xx Server Error
                elif response.status_code >= 500:
                    logger.error(
                        f"NVIDIA Server Error ({response.status_code}): {response.text}"
                    )
                    raise RuntimeError(
                        "NVIDIA Inference server encountered an error. Please retry."
                    )

                else:
                    logger.error(
                        f"NVIDIA Unexpected HTTP Error ({response.status_code}): {response.text}"
                    )
                    raise RuntimeError(
                        f"NVIDIA API responded with unexpected status code {response.status_code}."
                    )

        except httpx.TimeoutException as e:
            logger.error(f"NVIDIA Connection timed out: {e}")
            raise RuntimeError(f"NVIDIA API request timed out: {e}") from e
        except httpx.NetworkError as e:
            logger.error(f"NVIDIA Network error occurred: {e}")
            raise RuntimeError(f"NVIDIA API network connection failure: {e}") from e
        except httpx.RequestError as e:
            logger.error(f"NVIDIA HTTP request error: {e}")
            raise RuntimeError(f"NVIDIA API request failed: {e}") from e


class NVIDIAProvider(AIProvider):
    """Concrete NVIDIA Inference API provider implementation."""

    def __init__(self, adapter: Optional[NVIDIAProviderAdapter] = None) -> None:
        self._adapter = adapter or NVIDIAProviderAdapter()

    @property
    def name(self) -> str:
        return "nvidia"

    def generate(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        logger.info(
            f"Generating response using model: {model} "
            f"(API Key present: {bool(self._adapter.api_key)})"
        )

        if not self._adapter.api_key:
            return f"[NVIDIAProvider] Mock response to prompt: '{prompt}'"

        return self._adapter.execute_completion(
            model,
            prompt,
            system_prompt,
            **kwargs,
        )

    def stream(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        """Not implemented in foundation milestone."""
        raise NotImplementedError("Streaming is not implemented in NVIDIA provider foundation.")

    def embeddings(
        self,
        model: str,
        text: str,
        **kwargs: Any,
    ) -> List[float]:
        """Not implemented in foundation milestone."""
        raise NotImplementedError("Embeddings are not implemented in NVIDIA provider foundation.")

    def health(self) -> bool:
        """Checks provider health based on key presence."""
        return bool(self._adapter.api_key)

    def capabilities(self) -> ProviderCapabilities:
        """Returns capabilities of NVIDIA provider."""
        return ProviderCapabilities(
            chat=True,
            coding=True,
            reasoning=True,
            vision=False,
            embeddings=False,
            tool_calling=True,
            streaming=False,  # stream() raises NotImplementedError; updated when implemented
            max_context_tokens=131072,
            max_output_tokens=4096,
            supports_json=True,
            supports_functions=True,
        )


def register_nvidia_provider() -> None:
    """Bootstraps and registers NVIDIA provider and its metadata inside the registries."""
    logger.info("Registering NVIDIA Inference API provider foundation...")

    # 1. Instantiate and Register Provider
    provider = NVIDIAProvider()
    universal_provider_registry.register(provider)

    # 2. Register NVIDIA models in ModelRegistry
    nvidia_models = [
        ModelInfo(
            provider="nvidia",
            model_id="nvidia/nemotron-4-340b-instruct",
            display_name="Nemotron-4 340B Instruct",
            family="nemotron",
            max_context_tokens=131072,
            max_output_tokens=4096,
            supports_chat=True,
            supports_coding=True,
            supports_reasoning=True,
            supports_tool_calling=True,
        ),
        ModelInfo(
            provider="nvidia",
            model_id="nvidia/llama-3.1-nemotron-70b-instruct",
            display_name="Llama 3.1 Nemotron 70B Instruct",
            family="nemotron",
            max_context_tokens=131072,
            max_output_tokens=4096,
            supports_chat=True,
            supports_coding=True,
            supports_reasoning=True,
            supports_tool_calling=True,
        ),
    ]

    for model in nvidia_models:
        universal_model_registry.register_model(model)

        # Register capabilities
        caps = ProviderCapabilities(
            chat=model.supports_chat,
            coding=model.supports_coding,
            reasoning=model.supports_reasoning,
            tool_calling=model.supports_tool_calling,
            max_context_tokens=model.max_context_tokens,
            max_output_tokens=model.max_output_tokens,
        )
        universal_capability_registry.register_model_capabilities(model.model_id, caps)

        # Register cost
        cost = ProviderCost(
            input_cost_per_million_tokens=0.0,
            output_cost_per_million_tokens=0.0,
        )
        universal_cost_registry.register_model_cost(model.model_id, cost)

    # 3. Register Health
    health = ProviderHealth(
        available=provider.health(),
        latency_ms=120.0,
        health_score=100.0 if provider.health() else 0.0,
    )
    universal_health_registry.update_health(
        "nvidia",
        available=health.available,
        latency_ms=health.latency_ms,
        health_score=health.health_score,
    )

    # 4. Register Quota
    quota = ProviderQuota(
        requests_remaining=5000,
        tokens_remaining=10000000,
        unlimited=False,
    )
    universal_quota_registry.update_quota(
        "nvidia",
        requests_remaining=quota.requests_remaining,
        tokens_remaining=quota.tokens_remaining,
        unlimited=quota.unlimited,
    )

    # 5. Register Model Resolutions
    model_resolutions = {
        "nvidia/nemotron-4-340b-instruct": "nvidia/nvidia-nemotron-nano-9b-v2",
        "nvidia/llama-3.1-nemotron-70b-instruct": "nvidia/nvidia-nemotron-nano-9b-v2",
        "nvidia/qwen/qwen3-coder": "nvidia/nvidia-nemotron-nano-9b-v2",
        "qwen/qwen3-coder": "nvidia/nvidia-nemotron-nano-9b-v2",
    }
    for canonical_id, provider_id in model_resolutions.items():
        universal_model_registry.register_model_resolution(
            provider="nvidia",
            canonical_id=canonical_id,
            provider_id=provider_id,
        )

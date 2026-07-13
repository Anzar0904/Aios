import json
import time
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

import httpx

from aios.providers.interface import AIProvider, ModelInfo, universal_model_registry
from aios.providers.models import ProviderCapabilities

CACHE_FILE = Path(".aios_9router_cache.json")


class NineRouterProvider(AIProvider):
    """OpenAI-compatible adapter to interact with the local 9Router gateway."""

    def __init__(
        self,
        base_url: str = "http://localhost:8080/v1",
        api_key: Optional[str] = None,
        timeout: int = 30,
    ) -> None:
        self.base_url = base_url
        self.api_key = api_key or "9router-api-key"
        self.timeout = timeout
        self._cached_models: List[str] = []
        self._last_discovery: float = 0.0

    @property
    def name(self) -> str:
        return "ninerouter"

    def generate(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        endpoint = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
        }
        if "max_tokens" in kwargs and kwargs["max_tokens"] is not None:
            payload["max_tokens"] = kwargs["max_tokens"]

        with httpx.Client(timeout=float(self.timeout)) as client:
            res = client.post(endpoint, json=payload, headers=headers)
            res.raise_for_status()
            return res.json()["choices"][0]["message"]["content"]

    def stream(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any,
    ) -> Iterator[str]:
        endpoint = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "stream": True,
        }
        with httpx.Client(timeout=float(self.timeout)) as client:
            with client.stream("POST", endpoint, json=payload, headers=headers) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            chunk_data = json.loads(data_str)
                            text = chunk_data["choices"][0]["delta"].get("content", "")
                            if text:
                                yield text
                        except Exception:
                            pass

    def embeddings(self, model: str, text: str, **kwargs: Any) -> List[float]:
        endpoint = f"{self.base_url.rstrip('/')}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": model, "input": text}
        with httpx.Client(timeout=float(self.timeout)) as client:
            res = client.post(endpoint, json=payload, headers=headers)
            res.raise_for_status()
            return res.json()["data"][0]["embedding"]

    def health(self) -> bool:
        try:
            endpoint = f"{self.base_url.rstrip('/')}/models"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            with httpx.Client(timeout=2.0) as client:
                res = client.get(endpoint, headers=headers)
                return res.status_code == 200
        except Exception:
            return False

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            chat=True,
            embeddings=True,
            streaming=True,
            vision=True,
            reasoning=True,
            coding=True,
        )


def discover_9router(
    provider: NineRouterProvider,
    force: bool = False,
) -> Dict[str, Any]:
    """Discovers running 9Router server instances, configurations, and available models."""
    now = time.time()
    # Cache discovery for 60 seconds unless forced
    if not force and provider._cached_models and (now - provider._last_discovery < 60):
        return {
            "online": True,
            "endpoint": provider.base_url,
            "models": provider._cached_models,
            "cached": True,
        }

    online = False
    models = []
    latency = 0.0

    try:
        start = time.time()
        endpoint = f"{provider.base_url.rstrip('/')}/models"
        headers = {"Authorization": f"Bearer {provider.api_key}"}
        with httpx.Client(timeout=3.0) as client:
            res = client.get(endpoint, headers=headers)
            if res.status_code == 200:
                online = True
                latency = (time.time() - start) * 1000.0
                data = res.json()
                for m in data.get("data", []):
                    models.append(m["id"])
    except Exception:
        online = False

    if online:
        provider._cached_models = models
        provider._last_discovery = now
        # Cache to file
        try:
            CACHE_FILE.write_text(json.dumps(models), encoding="utf-8")
        except Exception:
            pass
    else:
        # Load from cache file if offline
        if CACHE_FILE.exists():
            try:
                models = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
                provider._cached_models = models
            except Exception:
                pass

    # Register discovered models in the global registry
    for model_id in models:
        is_coder = (
            "coder" in model_id.lower()
            or "coding" in model_id.lower()
            or "code" in model_id.lower()
        )
        is_reasoner = (
            "o1" in model_id.lower() or "reasoning" in model_id.lower() or "r1" in model_id.lower()
        )
        is_vision = (
            "vision" in model_id.lower()
            or "gpt-4o" in model_id.lower()
            or "claude-3-5" in model_id.lower()
        )

        universal_model_registry.register_model(
            ModelInfo(
                provider="ninerouter",
                model_id=model_id,
                display_name=model_id.upper(),
                family=model_id.split("-")[0] if "-" in model_id else model_id,
                supports_chat=True,
                supports_coding=is_coder,
                supports_reasoning=is_reasoner,
                supports_vision=is_vision,
                supports_embeddings="embed" in model_id.lower(),
                supports_streaming=True,
            )
        )

    return {
        "online": online,
        "endpoint": provider.base_url,
        "models": models,
        "latency_ms": latency,
        "cached": False,
    }


def generate_9router_reports() -> None:
    """Generates the four standard markdown reports under docs/providers/."""
    from aios.config import load_config
    from aios.providers.interface import universal_provider_registry

    docs_dir = Path("docs/providers")
    docs_dir.mkdir(parents=True, exist_ok=True)

    config = None
    try:
        config = load_config(Path("config/config.toml"))
    except Exception:
        pass

    nr_provider = universal_provider_registry.lookup("ninerouter")
    is_online = nr_provider.health() if nr_provider else False
    latency_val = getattr(nr_provider, "_last_latency", 0.0) if nr_provider else 0.0

    # 1. Local Gateway Status
    gateway_status = [
        "# Local Gateway Status",
        f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"- **Status**: {'ONLINE' if is_online else 'OFFLINE'}",
        f"- **Base URL**: {nr_provider.base_url if nr_provider else 'N/A'}",
        f"- **Latency**: {latency_val:.1f}ms",
    ]
    (docs_dir / "local_gateway_status.md").write_text("\n".join(gateway_status), encoding="utf-8")

    # 2. Installed Providers
    installed = [
        "# Installed Providers",
        f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "| Provider Name | Type | Status |",
        "| --- | --- | --- |",
    ]
    for p_name in universal_provider_registry.list_providers():
        p_inst = universal_provider_registry.lookup(p_name)
        status = "Healthy" if p_inst and p_inst.health() else "Unavailable"
        t_name = p_inst.__class__.__name__ if p_inst else "Unknown"
        installed.append(f"| {p_name} | {t_name} | {status} |")
    (docs_dir / "installed_providers.md").write_text("\n".join(installed), encoding="utf-8")

    # 3. Connected Models
    connected = [
        "# Connected Models",
        f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "| Model ID | Provider | Chat | Coding | Vision | Reasoning | Embeddings |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for m in universal_model_registry.list_models():
        chat = "✓" if m.supports_chat else ""
        coding = "✓" if m.supports_coding else ""
        reasoning = "✓" if m.supports_reasoning else ""
        vision = "✓" if m.supports_vision else ""
        emb = "✓" if m.supports_embeddings else ""
        connected.append(
            f"| {m.model_id} | {m.provider} | {chat} | {coding} | {vision} | {reasoning} | {emb} |"
        )
    (docs_dir / "connected_models.md").write_text("\n".join(connected), encoding="utf-8")

    # 4. Configuration Summary
    conf_summary = [
        "# Configuration Summary",
        f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Active TOML Configuration",
        "```toml",
    ]
    if config and hasattr(config, "llm") and getattr(config.llm, "ninerouter", None):
        nr = config.llm.ninerouter
        conf_summary.append("[llm.ninerouter]")
        conf_summary.append(f'base_url = "{nr.base_url}"')
        key_val = "*" * len(nr.api_key) if nr.api_key else "None"
        conf_summary.append(f'api_key = "{key_val}"')
        conf_summary.append(f"timeout = {nr.timeout}")
        conf_summary.append(f'preferred_model = "{nr.preferred_model}"')
        conf_summary.append(f'preferred_backend = "{nr.preferred_backend}"')
    else:
        conf_summary.append("# No 9Router configuration section found.")
    conf_summary.append("```")
    (docs_dir / "configuration_summary.md").write_text("\n".join(conf_summary), encoding="utf-8")

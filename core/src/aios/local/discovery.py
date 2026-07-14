"""
aios/local/discovery.py

Automatic Ollama model discovery.
Queries Ollama's REST API to detect all installed models and extract metadata.
No hardcoded model names — fully dynamic.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)


class ModelType(str, Enum):
    """Discriminates between chat-capable and embedding-only models."""

    CHAT = "chat"
    EMBEDDING = "embedding"
    UNKNOWN = "unknown"


class ModelStatus(str, Enum):
    """Runtime availability status of a local model."""

    INSTALLED = "installed"
    RUNNING = "running"
    UNLOADED = "unloaded"
    MISSING = "missing"
    ERROR = "error"


@dataclass
class OllamaModelMetadata:
    """
    Full metadata profile for a single Ollama model.

    Populated by OllamaDiscovery.discover() and enriched
    with capability/type information via heuristic analysis.
    """

    name: str
    size_bytes: int
    modified_at: str
    model_type: ModelType = ModelType.CHAT
    status: ModelStatus = ModelStatus.INSTALLED
    context_length: int = 4096
    parameter_size: str = "unknown"
    quantization: str = "unknown"
    family: str = "unknown"
    families: List[str] = field(default_factory=list)
    digest: str = ""
    raw_details: Dict[str, Any] = field(default_factory=dict)

    @property
    def size_gb(self) -> float:
        """Returns model size in gigabytes."""
        return round(self.size_bytes / (1024**3), 2)

    @property
    def is_embedding_model(self) -> bool:
        """Returns True if this model is an embedding-only model."""
        return self.model_type == ModelType.EMBEDDING

    @property
    def is_chat_model(self) -> bool:
        """Returns True if this model supports chat/completion."""
        return self.model_type == ModelType.CHAT


class OllamaDiscovery:
    """
    Discovers all installed Ollama models via the Ollama REST API.

    Implements retry logic, TTL caching, and heuristic classification
    of model types (chat vs embedding) based on model name patterns.
    """

    EMBEDDING_PATTERNS = (
        "embed",
        "embedding",
        "mxbai",
        "nomic-embed",
        "all-minilm",
        "bge-",
        "e5-",
        "sentence",
    )

    # Known context lengths by model family/name patterns
    CONTEXT_LENGTH_MAP: Dict[str, int] = {
        "deepseek-r1": 131072,
        "deepseek-coder-v2": 131072,
        "qwen2.5-coder": 131072,
        "qwen3": 40960,
        "qwen3.5": 40960,
        "qwen3.6": 40960,
        "gemma3": 131072,
        "mistral-small": 131072,
        "mxbai-embed": 512,
    }

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: float = 10.0,
        cache_ttl: float = 60.0,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._cache_ttl = cache_ttl
        self._cached_models: List[OllamaModelMetadata] = []
        self._last_discovery: float = 0.0

    @property
    def base_url(self) -> str:
        return self._base_url

    def is_available(self) -> bool:
        """Checks whether the Ollama daemon is reachable."""
        try:
            with httpx.Client(timeout=3.0) as client:
                resp = client.get(f"{self._base_url}/api/version")
                return resp.status_code == 200
        except Exception:
            return False

    def discover(self, force: bool = False) -> List[OllamaModelMetadata]:
        """
        Returns a list of all installed Ollama models with full metadata.

        Results are cached for `cache_ttl` seconds. Pass force=True to bypass.
        Raises ConnectionError if Ollama daemon is unreachable.
        """
        now = time.monotonic()
        if not force and self._cached_models and (now - self._last_discovery) < self._cache_ttl:
            logger.debug(
                "Returning cached Ollama model discovery results (%d models)",
                len(self._cached_models),
            )
            return list(self._cached_models)

        logger.info("Querying Ollama API for installed models at %s", self._base_url)
        try:
            with httpx.Client(timeout=self._timeout) as client:
                resp = client.get(f"{self._base_url}/api/tags")
                resp.raise_for_status()
                data = resp.json()
        except httpx.ConnectError as exc:
            raise ConnectionError(
                f"Cannot reach Ollama daemon at {self._base_url}. "
                "Ensure Ollama is running: `ollama serve`"
            ) from exc
        except Exception as exc:
            raise ConnectionError(f"Ollama API request failed: {exc}") from exc

        models: List[OllamaModelMetadata] = []
        for raw in data.get("models", []):
            try:
                meta = self._parse_model(raw)
                models.append(meta)
            except Exception as exc:
                logger.warning("Failed to parse model entry %s: %s", raw.get("name", "?"), exc)

        self._cached_models = models
        self._last_discovery = now
        logger.info("Discovered %d local Ollama models", len(models))
        return list(models)

    def get_running_models(self) -> List[str]:
        """Returns names of models currently loaded in VRAM/RAM."""
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(f"{self._base_url}/api/ps")
                if resp.status_code != 200:
                    return []
                data = resp.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception:
            return []

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Fetches detailed model info from Ollama (SHOW endpoint)."""
        try:
            with httpx.Client(timeout=10.0) as client:
                resp = client.post(
                    f"{self._base_url}/api/show",
                    json={"name": model_name},
                )
                if resp.status_code == 200:
                    return resp.json()
        except Exception as exc:
            logger.warning("Could not fetch model info for %s: %s", model_name, exc)
        return None

    def invalidate_cache(self) -> None:
        """Forces next call to discover() to re-query the Ollama API."""
        self._last_discovery = 0.0
        self._cached_models = []

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _parse_model(self, raw: Dict[str, Any]) -> OllamaModelMetadata:
        """Builds an OllamaModelMetadata from raw Ollama API response data."""
        details = raw.get("details", {})
        name: str = raw.get("name", "")
        name_lower = name.lower()

        model_type = self._classify_type(name_lower)
        context_length = self._resolve_context_length(name_lower, details)
        family = details.get("family", self._extract_family(name))
        families = details.get("families") or ([family] if family else [])

        return OllamaModelMetadata(
            name=name,
            size_bytes=raw.get("size", 0),
            modified_at=raw.get("modified_at", ""),
            model_type=model_type,
            status=ModelStatus.INSTALLED,
            context_length=context_length,
            parameter_size=details.get("parameter_size", "unknown"),
            quantization=details.get("quantization_level", "unknown"),
            family=family,
            families=families,
            digest=raw.get("digest", ""),
            raw_details=details,
        )

    def _classify_type(self, name_lower: str) -> ModelType:
        """Heuristic: classify as EMBEDDING if name matches known embedding patterns."""
        for pattern in self.EMBEDDING_PATTERNS:
            if pattern in name_lower:
                return ModelType.EMBEDDING
        return ModelType.CHAT

    def _resolve_context_length(self, name_lower: str, details: Dict[str, Any]) -> int:
        """Resolves context length from API details or known pattern map."""
        # Try numeric fields from details
        for key in ("context_length",):
            val = details.get(key)
            if isinstance(val, int) and val > 0:
                return val

        # Match against known patterns
        for pattern, ctx in self.CONTEXT_LENGTH_MAP.items():
            if pattern in name_lower:
                return ctx

        return 4096  # Conservative fallback

    def _extract_family(self, name: str) -> str:
        """Extracts the model family from its name (e.g., 'deepseek-r1:14b' → 'deepseek-r1')."""
        base = name.split(":")[0]
        return base

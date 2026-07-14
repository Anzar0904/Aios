"""
aios/local/loader.py

Dynamic Model Loader.

Implements load → execute → store → unload lifecycle for local Ollama models.
Enforces the single-active-model constraint to optimize RAM usage.
Uses the Ollama REST API for all model control operations.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional

import httpx

logger = logging.getLogger(__name__)


@dataclass
class ModelLoadResult:
    """Result of a model load operation."""

    model_name: str
    success: bool
    load_time_ms: float
    error: Optional[str] = None


@dataclass
class InferenceResult:
    """Result of a model inference (generate/chat) operation."""

    model_name: str
    prompt: str
    response: str
    success: bool
    inference_time_ms: float
    tokens_estimated: int = 0
    error: Optional[str] = None
    memory_mb: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def tokens_per_second(self) -> float:
        """Estimated throughput."""
        if self.inference_time_ms <= 0 or self.tokens_estimated <= 0:
            return 0.0
        return self.tokens_estimated / (self.inference_time_ms / 1000.0)


class LocalModelLoader:
    """
    Manages the lifecycle of local Ollama models:
    load → execute → unload.

    Key invariant: only one model is active at a time.
    Calling load() on a different model automatically unloads
    the currently active one first.

    Memory optimization: models are explicitly unloaded via the
    Ollama /api/generate endpoint using keep_alive=0 after execution.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        default_timeout: float = 120.0,
        auto_unload: bool = True,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._default_timeout = default_timeout
        self._auto_unload = auto_unload
        self._active_model: Optional[str] = None
        self._load_history: List[Dict[str, Any]] = []

    @property
    def active_model(self) -> Optional[str]:
        """Returns the name of the currently loaded model, or None."""
        return self._active_model

    def load(self, model_name: str) -> ModelLoadResult:
        """
        Loads a model into memory via a warm-up generate call.

        If a different model is currently active, it is unloaded first.
        The Ollama daemon handles actual VRAM/RAM allocation; this method
        issues a minimal generate request to trigger eager loading.
        """
        # Unload previous model if different
        if self._active_model and self._active_model != model_name and self._auto_unload:
            logger.info(
                "Unloading previous model '%s' before loading '%s'", self._active_model, model_name
            )
            self.unload(self._active_model)

        if self._active_model == model_name:
            logger.debug("Model '%s' is already active — skipping load", model_name)
            return ModelLoadResult(model_name=model_name, success=True, load_time_ms=0.0)

        logger.info("Loading model: %s", model_name)
        start = time.monotonic()

        try:
            # Send a minimal request to trigger model loading
            with httpx.Client(timeout=self._default_timeout) as client:
                resp = client.post(
                    f"{self._base_url}/api/generate",
                    json={
                        "model": model_name,
                        "prompt": "",
                        "keep_alive": "5m",
                        "stream": False,
                    },
                )
                resp.raise_for_status()

            elapsed_ms = (time.monotonic() - start) * 1000.0
            self._active_model = model_name
            self._log_event("load", model_name, elapsed_ms)
            logger.info("Model '%s' loaded in %.1f ms", model_name, elapsed_ms)
            return ModelLoadResult(model_name=model_name, success=True, load_time_ms=elapsed_ms)

        except Exception as exc:
            elapsed_ms = (time.monotonic() - start) * 1000.0
            error_msg = str(exc)
            logger.error("Failed to load model '%s': %s", model_name, error_msg)
            self._log_event("load_error", model_name, elapsed_ms, error=error_msg)
            return ModelLoadResult(
                model_name=model_name, success=False, load_time_ms=elapsed_ms, error=error_msg
            )

    def unload(self, model_name: Optional[str] = None) -> bool:
        """
        Unloads the specified model (or active model) from RAM/VRAM.

        Uses keep_alive=0 to instruct Ollama to release resources.
        Returns True on success.
        """
        target = model_name or self._active_model
        if not target:
            logger.debug("No active model to unload")
            return True

        logger.info("Unloading model: %s", target)
        start = time.monotonic()

        try:
            with httpx.Client(timeout=30.0) as client:
                resp = client.post(
                    f"{self._base_url}/api/generate",
                    json={
                        "model": target,
                        "prompt": "",
                        "keep_alive": 0,
                        "stream": False,
                    },
                )
                # 200 or 404 (model not loaded) both count as success
                success = resp.status_code in (200, 404)

        except Exception as exc:
            logger.warning("Error unloading model '%s': %s", target, exc)
            success = False

        elapsed_ms = (time.monotonic() - start) * 1000.0
        if success and self._active_model == target:
            self._active_model = None

        self._log_event("unload", target, elapsed_ms, success=success)
        logger.info("Model '%s' unloaded (success=%s) in %.1f ms", target, success, elapsed_ms)
        return success

    def generate(
        self,
        model_name: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> InferenceResult:
        """
        Generates a response from the specified model.

        Automatically loads the model if not already active.
        After generation, the model remains loaded unless auto_unload is
        explicitly called.
        """
        # Ensure model is loaded
        if self._active_model != model_name:
            load_result = self.load(model_name)
            if not load_result.success:
                return InferenceResult(
                    model_name=model_name,
                    prompt=prompt,
                    response="",
                    success=False,
                    inference_time_ms=0.0,
                    error=f"Load failed: {load_result.error}",
                )

        logger.debug("Running inference on model '%s' (prompt length=%d)", model_name, len(prompt))
        start = time.monotonic()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }
        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens

        actual_timeout = timeout or self._default_timeout

        try:
            with httpx.Client(timeout=actual_timeout) as client:
                resp = client.post(
                    f"{self._base_url}/api/chat",
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()

            elapsed_ms = (time.monotonic() - start) * 1000.0
            response_text = data.get("message", {}).get("content", "")
            tokens_prompt = data.get("prompt_eval_count", 0) or 0
            tokens_eval = data.get("eval_count", 0) or 0
            total_tokens = tokens_prompt + tokens_eval

            self._log_event("generate", model_name, elapsed_ms, tokens=total_tokens)
            logger.debug(
                "Inference complete: model=%s time=%.1fms tokens=%d",
                model_name,
                elapsed_ms,
                total_tokens,
            )

            return InferenceResult(
                model_name=model_name,
                prompt=prompt,
                response=response_text,
                success=True,
                inference_time_ms=elapsed_ms,
                tokens_estimated=total_tokens,
                metadata={
                    "prompt_tokens": tokens_prompt,
                    "completion_tokens": tokens_eval,
                    "raw_response": data,
                },
            )

        except Exception as exc:
            elapsed_ms = (time.monotonic() - start) * 1000.0
            error_msg = str(exc)
            logger.error("Inference failed for model '%s': %s", model_name, error_msg)
            self._log_event("generate_error", model_name, elapsed_ms, error=error_msg)
            return InferenceResult(
                model_name=model_name,
                prompt=prompt,
                response="",
                success=False,
                inference_time_ms=elapsed_ms,
                error=error_msg,
            )

    def stream(
        self,
        model_name: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Iterator[str]:
        """
        Streams a response from the specified model token-by-token.

        Automatically loads the model if not already active.
        """
        if self._active_model != model_name:
            load_result = self.load(model_name)
            if not load_result.success:
                yield f"[Error: Could not load model {model_name}: {load_result.error}]"
                return

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload: Dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "stream": True,
            "options": {"temperature": temperature},
        }

        try:
            with httpx.Client(timeout=self._default_timeout) as client:
                with client.stream("POST", f"{self._base_url}/api/chat", json=payload) as response:
                    response.raise_for_status()
                    for line in response.iter_lines():
                        if not line:
                            continue
                        import json

                        try:
                            chunk = json.loads(line)
                            content = chunk.get("message", {}).get("content", "")
                            if content:
                                yield content
                            if chunk.get("done", False):
                                break
                        except Exception:
                            continue
        except Exception as exc:
            yield f"[Stream error: {exc}]"

    def generate_embedding(
        self,
        model_name: str,
        text: str,
        timeout: Optional[float] = None,
    ) -> List[float]:
        """
        Generates an embedding vector for the given text using an embedding model.
        """
        actual_timeout = timeout or self._default_timeout
        try:
            with httpx.Client(timeout=actual_timeout) as client:
                resp = client.post(
                    f"{self._base_url}/api/embeddings",
                    json={"model": model_name, "prompt": text},
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("embedding", [])
        except Exception as exc:
            logger.error("Embedding generation failed for model '%s': %s", model_name, exc)
            return []

    def execute_and_unload(
        self,
        model_name: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> InferenceResult:
        """
        Convenience method: load → generate → unload in one call.

        Guarantees the model is unloaded after execution regardless of outcome.
        """
        result = self.generate(model_name, prompt, system_prompt, temperature, max_tokens)
        self.unload(model_name)
        return result

    def get_load_history(self) -> List[Dict[str, Any]]:
        """Returns the event log of load/unload/generate operations."""
        return list(self._load_history)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _log_event(
        self,
        event_type: str,
        model_name: str,
        duration_ms: float,
        **kwargs: Any,
    ) -> None:
        """Appends a structured event to the internal load history."""
        entry: Dict[str, Any] = {
            "event": event_type,
            "model": model_name,
            "timestamp": time.time(),
            "duration_ms": round(duration_ms, 2),
        }
        entry.update(kwargs)
        self._load_history.append(entry)
        # Cap history at 1000 entries
        if len(self._load_history) > 1000:
            self._load_history = self._load_history[-1000:]

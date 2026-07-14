"""
aios/local/health_monitor.py

Health Monitor for local Ollama models.

Tracks installation status, running state, RAM/CPU usage,
latency, tokens/sec, last used, and failure count.
Refreshes health state from live Ollama API data.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx

from aios.local.discovery import ModelStatus, OllamaDiscovery, OllamaModelMetadata

logger = logging.getLogger(__name__)


@dataclass
class ModelHealthStatus:
    """
    Comprehensive health snapshot for a single local model.

    Fields track all dimensions from the specification:
    installed, missing, running, RAM, CPU, tokens/sec, latency, last_used, failures.
    """

    model_name: str
    installed: bool = False
    running: bool = False
    status: ModelStatus = ModelStatus.MISSING
    ram_mb: float = 0.0
    vram_mb: float = 0.0
    size_gb: float = 0.0
    tokens_per_second: float = 0.0
    avg_latency_ms: float = 0.0
    last_used: Optional[float] = None
    failure_count: int = 0
    total_requests: int = 0
    success_count: int = 0
    last_error: Optional[str] = None
    expires_at: Optional[float] = None  # When Ollama will auto-evict

    @property
    def success_rate(self) -> float:
        """Returns success rate as 0.0–1.0."""
        if self.total_requests == 0:
            return 1.0
        return self.success_count / self.total_requests

    @property
    def last_used_ago_seconds(self) -> Optional[float]:
        """Seconds since this model was last used, or None."""
        if self.last_used is None:
            return None
        return time.time() - self.last_used

    @property
    def health_score(self) -> float:
        """
        Composite health score 0-100.
        Penalized by failures, latency, and unavailability.
        """
        if not self.installed:
            return 0.0
        score = 100.0
        score -= min(40.0, self.failure_count * 5.0)
        if self.avg_latency_ms > 5000:
            score -= min(20.0, (self.avg_latency_ms - 5000) / 500)
        score *= self.success_rate
        return max(0.0, min(100.0, score))


class LocalHealthMonitor:
    """
    Monitors and tracks health metrics for all installed Ollama models.

    Design:
    - Aggregates Ollama's /api/ps (running models) and /api/tags (all models)
      to produce a comprehensive health snapshot.
    - Tracks historical latency and token metrics from inference results
      (fed by LocalModelLoader via record_inference()).
    - Provides doctor() method for actionable health diagnostics.
    """

    def __init__(
        self,
        discovery: OllamaDiscovery,
        base_url: str = "http://localhost:11434",
    ) -> None:
        self._discovery = discovery
        self._base_url = base_url.rstrip("/")
        self._health: Dict[str, ModelHealthStatus] = {}
        self._latency_history: Dict[str, List[float]] = {}
        self._tps_history: Dict[str, List[float]] = {}

    def refresh(self, force_discovery: bool = False) -> Dict[str, ModelHealthStatus]:
        """
        Refreshes health status for all models.

        Queries Ollama /api/tags (installed) and /api/ps (running),
        then merges into a unified health map.
        """
        # Installed models
        try:
            installed_models: List[OllamaModelMetadata] = self._discovery.discover(
                force=force_discovery
            )
            installed_names = {m.name for m in installed_models}
        except Exception as exc:
            logger.warning("Health refresh: discovery failed: %s", exc)
            installed_models = []
            installed_names = set()

        # Running models
        running_names: set = set()
        running_details: Dict[str, Dict[str, Any]] = {}
        try:
            with httpx.Client(timeout=5.0) as client:
                resp = client.get(f"{self._base_url}/api/ps")
                if resp.status_code == 200:
                    ps_data = resp.json()
                    for m in ps_data.get("models", []):
                        name = m.get("name", "")
                        running_names.add(name)
                        running_details[name] = m
        except Exception as exc:
            logger.debug("Health refresh: could not get running models: %s", exc)

        # Build health map for all installed models
        for meta in installed_models:
            h = self._health.setdefault(
                meta.name,
                ModelHealthStatus(
                    model_name=meta.name,
                    installed=True,
                    size_gb=meta.size_gb,
                ),
            )
            h.installed = True
            h.size_gb = meta.size_gb
            h.status = ModelStatus.INSTALLED

            if meta.name in running_names:
                h.running = True
                h.status = ModelStatus.RUNNING
                rdet = running_details.get(meta.name, {})
                # RAM usage reported by Ollama
                h.ram_mb = (
                    rdet.get("size_vram", 0) / (1024 * 1024) if rdet.get("size_vram") else 0.0
                )
                h.vram_mb = h.ram_mb
                exp_str = rdet.get("expires_at")
                if exp_str:
                    try:
                        from datetime import datetime

                        exp = datetime.fromisoformat(exp_str.replace("Z", "+00:00"))
                        h.expires_at = exp.timestamp()
                    except Exception:
                        pass
            else:
                h.running = False
                if h.status == ModelStatus.RUNNING:
                    h.status = ModelStatus.UNLOADED

        # Mark previously tracked models as missing if no longer installed
        for name in list(self._health.keys()):
            if name not in installed_names:
                self._health[name].installed = False
                self._health[name].running = False
                self._health[name].status = ModelStatus.MISSING

        return dict(self._health)

    def record_inference(
        self,
        model_name: str,
        success: bool,
        latency_ms: float,
        tokens_per_second: float = 0.0,
        error: Optional[str] = None,
    ) -> None:
        """
        Records an inference result for health tracking.

        Called by LocalModelLoader after each generate() operation.
        """
        h = self._health.setdefault(
            model_name,
            ModelHealthStatus(model_name=model_name),
        )
        h.total_requests += 1
        h.last_used = time.time()

        if success:
            h.success_count += 1
        else:
            h.failure_count += 1
            h.last_error = error

        # Rolling latency average (last 50 samples)
        hist = self._latency_history.setdefault(model_name, [])
        hist.append(latency_ms)
        if len(hist) > 50:
            hist.pop(0)
        h.avg_latency_ms = sum(hist) / len(hist)

        # Rolling TPS average
        if tokens_per_second > 0:
            tps_hist = self._tps_history.setdefault(model_name, [])
            tps_hist.append(tokens_per_second)
            if len(tps_hist) > 50:
                tps_hist.pop(0)
            h.tokens_per_second = sum(tps_hist) / len(tps_hist)

    def get_status(self, model_name: str) -> Optional[ModelHealthStatus]:
        """Returns the current health status for a single model."""
        return self._health.get(model_name)

    def get_all_statuses(self) -> Dict[str, ModelHealthStatus]:
        """Returns the full health map."""
        return dict(self._health)

    def get_running_models(self) -> List[str]:
        """Returns names of currently running (loaded) models."""
        return [name for name, h in self._health.items() if h.running]

    def get_installed_models(self) -> List[str]:
        """Returns names of all installed models."""
        return [name for name, h in self._health.items() if h.installed]

    def get_missing_models(self) -> List[str]:
        """Returns names of models tracked but no longer installed."""
        return [name for name, h in self._health.items() if not h.installed]

    def doctor(self, expected_models: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Runs a full health diagnostics check.

        Returns a structured report including:
        - Ollama availability
        - Per-model health
        - Missing expected models
        - Recommendations
        """
        self.refresh(force_discovery=True)

        ollama_online = self._discovery.is_available()
        installed = self.get_installed_models()
        running = self.get_running_models()
        missing: List[str] = []

        if expected_models:
            for em in expected_models:
                if not any(em.lower() in n.lower() for n in installed):
                    missing.append(em)

        recommendations = []
        if not ollama_online:
            recommendations.append("⚠️  Ollama daemon is not reachable. Run: ollama serve")
        if not installed:
            recommendations.append("⚠️  No models installed. Run: ollama pull <model>")
        for name, h in self._health.items():
            if h.failure_count > 5:
                recommendations.append(
                    f"⚠️  Model '{name}' has {h.failure_count} failures. "
                    "Consider pulling a fresh copy."
                )
            if h.success_rate < 0.5 and h.total_requests > 10:
                recommendations.append(
                    f"⚠️  Model '{name}' has low success rate ({h.success_rate:.1%})."
                )

        return {
            "ollama_online": ollama_online,
            "installed_count": len(installed),
            "running_count": len(running),
            "installed_models": installed,
            "running_models": running,
            "missing_expected": missing,
            "model_health": {
                name: {
                    "health_score": h.health_score,
                    "status": h.status.value,
                    "ram_mb": h.ram_mb,
                    "avg_latency_ms": h.avg_latency_ms,
                    "tokens_per_second": h.tokens_per_second,
                    "failure_count": h.failure_count,
                    "success_rate": h.success_rate,
                    "last_used_ago": h.last_used_ago_seconds,
                }
                for name, h in self._health.items()
            },
            "recommendations": recommendations,
        }

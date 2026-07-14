"""
aios/local/service.py

LocalModelService — ServiceLifecycle integration for Phase 1.

Ties together discovery, capability registry, router, loader,
health monitor, benchmark engine, and memory integration into a
single cohesive service that registers with the AI OS ServiceRegistry.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from aios.local.benchmark import BenchmarkEngine, ModelBenchmarkResult
from aios.local.capability_registry import LocalCapabilityRegistry, ModelCapability
from aios.local.discovery import OllamaDiscovery, OllamaModelMetadata
from aios.local.health_monitor import LocalHealthMonitor, ModelHealthStatus
from aios.local.loader import InferenceResult, LocalModelLoader, ModelLoadResult
from aios.local.memory_integration import LocalExecutionRecord, LocalMemoryIntegration
from aios.local.router import LocalModelRouter, RoutingResult
from aios.services.base import ServiceLifecycle

logger = logging.getLogger(__name__)


class LocalModelService(ServiceLifecycle):
    """
    Phase 1: Local Model Intelligence Service.

    Orchestrates all local AI subsystems:
    - OllamaDiscovery: auto-detects installed models
    - LocalCapabilityRegistry: maps models to roles/capabilities
    - LocalModelRouter: selects models by capability from task description
    - LocalModelLoader: load/unload with single-model constraint
    - LocalHealthMonitor: tracks health, RAM, latency, failures
    - BenchmarkEngine: measures and stores performance scores
    - LocalMemoryIntegration: persists every execution to DB

    Registered with the ServiceRegistry at bootstrap time.
    """

    def __init__(
        self,
        ollama_base_url: str = "http://localhost:11434",
        db_path: Optional[Path] = None,
        benchmark_results_path: Optional[Path] = None,
        cache_ttl: float = 60.0,
    ) -> None:
        self._ollama_url = ollama_base_url

        # Sub-systems
        self.discovery = OllamaDiscovery(
            base_url=ollama_base_url,
            cache_ttl=cache_ttl,
        )
        self.capability_registry = LocalCapabilityRegistry()
        self.loader = LocalModelLoader(
            base_url=ollama_base_url,
            auto_unload=True,
        )
        self.router = LocalModelRouter(
            capability_registry=self.capability_registry,
        )
        self.health_monitor = LocalHealthMonitor(
            discovery=self.discovery,
            base_url=ollama_base_url,
        )
        self.benchmark_engine = BenchmarkEngine(
            loader=self.loader,
            results_file=benchmark_results_path,
        )

        # Memory integration — uses existing aios.db
        resolved_db = db_path or Path("aios.db")
        self.memory = LocalMemoryIntegration(db_path=resolved_db)

        # Cached list of available model names
        self._available_models: List[str] = []
        self._initialized = False

    # ------------------------------------------------------------------
    # ServiceLifecycle
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        """Discovers installed models and primes the health monitor."""
        logger.info("[LocalModelService] Initializing Phase 1: Local Model Intelligence Layer")
        try:
            models = self.discovery.discover()
            self._available_models = [m.name for m in models]
            self.health_monitor.refresh()
            self._apply_benchmark_scores_to_registry()
            self._initialized = True
            logger.info(
                "[LocalModelService] Initialized with %d local models: %s",
                len(self._available_models),
                ", ".join(self._available_models),
            )
        except ConnectionError as exc:
            logger.warning("[LocalModelService] Ollama not reachable during init: %s", exc)
            self._initialized = True  # Non-fatal — CLI can still work offline

    def start(self) -> None:
        logger.debug("[LocalModelService] Started")

    def shutdown(self) -> None:
        """Unloads the active model gracefully."""
        if self.loader.active_model:
            logger.info(
                "[LocalModelService] Unloading active model on shutdown: %s",
                self.loader.active_model,
            )
            self.loader.unload()

    # ------------------------------------------------------------------
    # High-level API
    # ------------------------------------------------------------------

    def discover_models(self, force: bool = False) -> List[OllamaModelMetadata]:
        """
        Returns all installed Ollama models with full metadata.

        Refreshes the internal available_models list.
        """
        models = self.discovery.discover(force=force)
        self._available_models = [m.name for m in models]
        return models

    def route_and_execute(
        self,
        task: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        force_capability: Optional[ModelCapability] = None,
        unload_after: bool = True,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Full pipeline: route → load → execute → record → (optionally) unload.

        Returns a structured dict with routing decision, inference result,
        and memory record ID.
        """
        if not self._available_models:
            self._available_models = [m.name for m in self.discovery.discover()]

        # 1. Route
        routing: Optional[RoutingResult] = self.router.route(
            task=task,
            available_models=self._available_models,
            force_capability=force_capability,
        )

        if routing is None:
            return {
                "success": False,
                "error": "No suitable model found",
                "routing": None,
                "inference": None,
            }

        # 2. Execute (loader auto-manages load/unload)
        if unload_after:
            inference: InferenceResult = self.loader.execute_and_unload(
                model_name=routing.model_name,
                prompt=prompt,
                system_prompt=system_prompt,
            )
        else:
            inference = self.loader.generate(
                model_name=routing.model_name,
                prompt=prompt,
                system_prompt=system_prompt,
            )

        # 3. Record health metrics
        self.health_monitor.record_inference(
            model_name=routing.model_name,
            success=inference.success,
            latency_ms=inference.inference_time_ms,
            tokens_per_second=inference.tokens_per_second,
            error=inference.error,
        )

        # 4. Persist to memory
        record = LocalExecutionRecord(
            model_name=routing.model_name,
            capability=routing.capability.value,
            prompt=prompt,
            response=inference.response,
            success=inference.success,
            inference_time_ms=inference.inference_time_ms,
            tokens_estimated=inference.tokens_estimated,
            tokens_per_second=inference.tokens_per_second,
            memory_mb=inference.memory_mb,
            error=inference.error,
            metadata={
                "routing_confidence": routing.confidence,
                "routing_reasoning": routing.reasoning,
                "fallback_used": routing.fallback_used,
            },
            session_id=session_id,
        )
        record_id = self.memory.record(record)

        return {
            "success": inference.success,
            "response": inference.response,
            "model": routing.model_name,
            "capability": routing.capability.value,
            "routing_confidence": routing.confidence,
            "routing_reasoning": routing.reasoning,
            "inference_time_ms": inference.inference_time_ms,
            "tokens": inference.tokens_estimated,
            "tokens_per_second": inference.tokens_per_second,
            "record_id": record_id,
            "error": inference.error,
        }

    def load_model(self, model_name: str) -> ModelLoadResult:
        """Explicitly loads a model into memory."""
        return self.loader.load(model_name)

    def unload_model(self, model_name: Optional[str] = None) -> bool:
        """Explicitly unloads the active or specified model."""
        return self.loader.unload(model_name)

    def get_health_status(self) -> Dict[str, ModelHealthStatus]:
        """Returns health status map for all known models."""
        self.health_monitor.refresh()
        return self.health_monitor.get_all_statuses()

    def run_doctor(self) -> Dict[str, Any]:
        """Runs full health diagnostics and returns a report."""
        return self.health_monitor.doctor()

    def run_benchmark(
        self,
        model_name: Optional[str] = None,
        all_models: bool = False,
        skip_existing: bool = True,
    ) -> Dict[str, ModelBenchmarkResult]:
        """
        Runs benchmark suite.

        If model_name is provided, benchmarks only that model.
        If all_models=True, benchmarks all installed models.
        """
        if model_name:
            result = self.benchmark_engine.benchmark_model(model_name)
            self._apply_benchmark_scores_to_registry()
            return {model_name: result}

        if all_models:
            models = self._available_models or [m.name for m in self.discovery.discover()]
            # Skip embedding-only models from chat benchmarks
            chat_models = [
                m for m in models if "embed" not in m.lower() and "mxbai" not in m.lower()
            ]
            results = self.benchmark_engine.benchmark_all(chat_models, skip_existing=skip_existing)
            self._apply_benchmark_scores_to_registry()
            return results

        return self.benchmark_engine.get_all_results()

    def get_benchmark_results(self) -> Dict[str, ModelBenchmarkResult]:
        """Returns all saved benchmark results."""
        return self.benchmark_engine.get_all_results()

    def get_model_registry_info(self) -> List[Dict[str, Any]]:
        """
        Returns the full model registry: capabilities, roles, and benchmark scores.
        """
        result = []
        for meta in self.discover_models():
            role = self.capability_registry.get_role(meta.name)
            bench = self.benchmark_engine.get_result(meta.name)
            result.append(
                {
                    "name": meta.name,
                    "size_gb": meta.size_gb,
                    "type": meta.model_type.value,
                    "context_length": meta.context_length,
                    "status": meta.status.value,
                    "capabilities": [c.value for c in (role.capabilities if role else [])],
                    "description": role.description if role else "",
                    "priority": role.priority if role else 50,
                    "benchmark_score": bench.composite_score if bench else None,
                    "avg_latency_ms": bench.avg_latency_ms if bench else None,
                    "avg_tps": bench.avg_tokens_per_second if bench else None,
                }
            )
        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _apply_benchmark_scores_to_registry(self) -> None:
        """Feeds benchmark composite scores into the capability registry."""
        for model_name, result in self.benchmark_engine.get_all_results().items():
            self.capability_registry.update_benchmark_score(model_name, result.composite_score)

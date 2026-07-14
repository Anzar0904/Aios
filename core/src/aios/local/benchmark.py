"""
aios/local/benchmark.py

Benchmark Engine for local Ollama models.

Measures speed, latency, memory, and quality for each model.
Saves results to a persistent JSON file.
Router uses benchmark scores to inform tie-breaking.
"""

from __future__ import annotations

import json
import logging
import statistics
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from aios.local.loader import LocalModelLoader

logger = logging.getLogger(__name__)

# Standard benchmark prompts covering different task domains
_BENCHMARK_PROMPTS = [
    {
        "name": "quick_math",
        "prompt": "What is 17 * 23? Answer with only the number.",
        "expected_keywords": ["391"],
        "max_tokens": 10,
        "weight": 0.2,
    },
    {
        "name": "code_generation",
        "prompt": "Write a Python function that reverses a string. Return only the code.",
        "expected_keywords": ["def", "return", "[::-1]"],
        "max_tokens": 100,
        "weight": 0.3,
    },
    {
        "name": "reasoning",
        "prompt": "If all cats are animals and some animals are pets, can we conclude all cats are pets? Answer yes or no and briefly explain.",
        "expected_keywords": ["no", "not"],
        "max_tokens": 80,
        "weight": 0.3,
    },
    {
        "name": "summarization",
        "prompt": "Summarize in one sentence: Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
        "expected_keywords": ["learn", "machine", "artificial"],
        "max_tokens": 60,
        "weight": 0.2,
    },
]


@dataclass
class BenchmarkRun:
    """Result of a single benchmark prompt run."""

    prompt_name: str
    latency_ms: float
    tokens_estimated: int
    tokens_per_second: float
    quality_score: float  # 0.0–1.0 based on keyword presence
    success: bool
    error: Optional[str] = None


@dataclass
class ModelBenchmarkResult:
    """
    Aggregated benchmark results for a single model.

    Composite score drives router tie-breaking.
    """

    model_name: str
    timestamp: float = field(default_factory=time.time)
    runs: List[BenchmarkRun] = field(default_factory=list)

    # Aggregate metrics
    avg_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    avg_tokens_per_second: float = 0.0
    avg_quality_score: float = 0.0
    success_rate: float = 0.0
    composite_score: float = 0.0  # 0-100
    total_duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelBenchmarkResult":
        runs = [BenchmarkRun(**r) for r in data.pop("runs", [])]
        result = cls(**data)
        result.runs = runs
        return result


class BenchmarkEngine:
    """
    Benchmarks local Ollama models across speed, latency, memory, and quality dimensions.

    Saves results to a JSON file for persistence across sessions.
    Provides composite_score used by the capability registry for routing tie-breaking.
    """

    DEFAULT_RESULTS_FILE = Path("benchmark_results.json")

    def __init__(
        self,
        loader: LocalModelLoader,
        results_file: Optional[Path] = None,
    ) -> None:
        self._loader = loader
        self._results_file = results_file or self.DEFAULT_RESULTS_FILE
        self._results: Dict[str, ModelBenchmarkResult] = {}
        self._load_saved_results()

    def benchmark_model(
        self,
        model_name: str,
        prompts: Optional[List[Dict[str, Any]]] = None,
        runs_per_prompt: int = 1,
        unload_after: bool = True,
    ) -> ModelBenchmarkResult:
        """
        Runs a full benchmark suite against a single model.

        Args:
            model_name: Ollama model name (e.g., 'deepseek-coder-v2:16b').
            prompts: Override the default benchmark prompt suite.
            runs_per_prompt: Number of repeat runs per prompt (for averaging).
            unload_after: Whether to unload the model after benchmarking.

        Returns:
            ModelBenchmarkResult with aggregate metrics and composite score.
        """
        suite = prompts or _BENCHMARK_PROMPTS
        logger.info("Benchmarking model: %s (%d prompts)", model_name, len(suite))

        runs: List[BenchmarkRun] = []
        total_start = time.monotonic()

        for prompt_spec in suite:
            for _ in range(runs_per_prompt):
                run = self._run_benchmark_prompt(model_name, prompt_spec)
                runs.append(run)
                logger.debug(
                    "  [%s] %s: %.1f ms, %.1f tps, quality=%.2f",
                    model_name,
                    prompt_spec["name"],
                    run.latency_ms,
                    run.tokens_per_second,
                    run.quality_score,
                )

        total_ms = (time.monotonic() - total_start) * 1000.0

        if unload_after:
            self._loader.unload(model_name)

        result = self._aggregate(model_name, runs, total_ms)
        self._results[model_name] = result
        self._save_results()

        logger.info(
            "Benchmark complete: %s — score=%.1f latency=%.1fms tps=%.1f quality=%.2f",
            model_name,
            result.composite_score,
            result.avg_latency_ms,
            result.avg_tokens_per_second,
            result.avg_quality_score,
        )
        return result

    def benchmark_all(
        self,
        model_names: List[str],
        skip_existing: bool = False,
    ) -> Dict[str, ModelBenchmarkResult]:
        """
        Benchmarks all provided models sequentially.

        Args:
            model_names: List of Ollama model names to benchmark.
            skip_existing: Skip models that already have saved results.

        Returns:
            Dict mapping model name → ModelBenchmarkResult.
        """
        for name in model_names:
            if skip_existing and name in self._results:
                logger.info("Skipping already-benchmarked model: %s", name)
                continue
            try:
                self.benchmark_model(name)
            except Exception as exc:
                logger.error("Benchmark failed for '%s': %s", name, exc)
                # Record failed result
                self._results[name] = ModelBenchmarkResult(
                    model_name=name,
                    runs=[],
                    composite_score=0.0,
                )
        self._save_results()
        return dict(self._results)

    def get_result(self, model_name: str) -> Optional[ModelBenchmarkResult]:
        """Returns saved benchmark result for a model, if available."""
        return self._results.get(model_name)

    def get_all_results(self) -> Dict[str, ModelBenchmarkResult]:
        """Returns all saved benchmark results."""
        return dict(self._results)

    def get_ranked_models(self) -> List[tuple]:
        """
        Returns models ranked by composite_score (highest first).

        Returns:
            List of (composite_score, model_name) tuples.
        """
        ranked = [(r.composite_score, name) for name, r in self._results.items()]
        return sorted(ranked, reverse=True)

    def get_best_model_for_speed(self) -> Optional[str]:
        """Returns the model with the highest tokens/second."""
        if not self._results:
            return None
        return max(self._results, key=lambda n: self._results[n].avg_tokens_per_second)

    def get_best_model_for_quality(self) -> Optional[str]:
        """Returns the model with the highest quality score."""
        if not self._results:
            return None
        return max(self._results, key=lambda n: self._results[n].avg_quality_score)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _run_benchmark_prompt(self, model_name: str, prompt_spec: Dict[str, Any]) -> BenchmarkRun:
        """Runs a single benchmark prompt against a model and scores the result."""
        prompt = prompt_spec["prompt"]
        max_tokens = prompt_spec.get("max_tokens", 200)
        expected_keywords = prompt_spec.get("expected_keywords", [])
        weight = prompt_spec.get("weight", 1.0)

        result = self._loader.generate(
            model_name=model_name,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.1,  # Low temp for reproducible benchmarks
        )

        # Quality scoring: keyword presence
        quality = 0.0
        if result.success and expected_keywords:
            response_lower = result.response.lower()
            hits = sum(1 for kw in expected_keywords if kw.lower() in response_lower)
            quality = hits / len(expected_keywords)
        elif result.success:
            quality = 1.0 if result.response.strip() else 0.0

        return BenchmarkRun(
            prompt_name=prompt_spec["name"],
            latency_ms=result.inference_time_ms,
            tokens_estimated=result.tokens_estimated,
            tokens_per_second=result.tokens_per_second,
            quality_score=quality * weight,
            success=result.success,
            error=result.error,
        )

    def _aggregate(
        self,
        model_name: str,
        runs: List[BenchmarkRun],
        total_ms: float,
    ) -> ModelBenchmarkResult:
        """Computes aggregate metrics and composite score from individual runs."""
        successful = [r for r in runs if r.success]

        if not successful:
            return ModelBenchmarkResult(
                model_name=model_name,
                runs=runs,
                composite_score=0.0,
                total_duration_ms=total_ms,
            )

        latencies = [r.latency_ms for r in successful]
        tps_vals = [r.tokens_per_second for r in successful if r.tokens_per_second > 0]
        quality_vals = [r.quality_score for r in successful]

        avg_latency = statistics.mean(latencies) if latencies else 0.0
        p95_latency = sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0.0
        avg_tps = statistics.mean(tps_vals) if tps_vals else 0.0
        avg_quality = statistics.mean(quality_vals) if quality_vals else 0.0
        success_rate = len(successful) / len(runs) if runs else 0.0

        # Composite score: weighted blend of speed, quality, reliability
        # Latency score: inverse of latency (lower is better), normalized to 0-40
        latency_score = max(0.0, 40.0 - (avg_latency / 1000.0) * 4)
        # TPS score: 0-30 points
        tps_score = min(30.0, avg_tps * 0.5)
        # Quality score: 0-20 points
        quality_score = avg_quality * 20.0
        # Reliability score: 0-10 points
        reliability_score = success_rate * 10.0

        composite = latency_score + tps_score + quality_score + reliability_score

        return ModelBenchmarkResult(
            model_name=model_name,
            runs=runs,
            avg_latency_ms=round(avg_latency, 2),
            p95_latency_ms=round(p95_latency, 2),
            avg_tokens_per_second=round(avg_tps, 2),
            avg_quality_score=round(avg_quality, 4),
            success_rate=round(success_rate, 4),
            composite_score=round(composite, 2),
            total_duration_ms=round(total_ms, 2),
        )

    def _load_saved_results(self) -> None:
        """Loads benchmark results from the JSON persistence file."""
        if not self._results_file.exists():
            return
        try:
            data = json.loads(self._results_file.read_text(encoding="utf-8"))
            for name, raw in data.items():
                self._results[name] = ModelBenchmarkResult.from_dict(raw)
            logger.debug("Loaded %d saved benchmark results", len(self._results))
        except Exception as exc:
            logger.warning("Could not load benchmark results: %s", exc)

    def _save_results(self) -> None:
        """Persists all benchmark results to the JSON file."""
        try:
            self._results_file.parent.mkdir(parents=True, exist_ok=True)
            data = {name: r.to_dict() for name, r in self._results.items()}
            self._results_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
            logger.debug("Saved %d benchmark results to %s", len(data), self._results_file)
        except Exception as exc:
            logger.warning("Could not save benchmark results: %s", exc)

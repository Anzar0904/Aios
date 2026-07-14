"""
tests/test_local_benchmark.py

Tests for Phase 1: BenchmarkEngine — model performance measurement.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest
from aios.local.benchmark import BenchmarkEngine, BenchmarkRun, ModelBenchmarkResult
from aios.local.loader import InferenceResult, LocalModelLoader

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_inference_result(
    model: str,
    response: str,
    success: bool = True,
    latency_ms: float = 500.0,
    tokens: int = 50,
) -> InferenceResult:
    return InferenceResult(
        model_name=model,
        prompt="test",
        response=response,
        success=success,
        inference_time_ms=latency_ms,
        tokens_estimated=tokens,
        metadata={},
    )


@pytest.fixture
def mock_loader():
    loader = MagicMock(spec=LocalModelLoader)
    loader.generate.return_value = _make_inference_result(
        "gemma3:4b",
        "391",  # Correct answer for math benchmark
        latency_ms=300.0,
        tokens=5,
    )
    loader.unload.return_value = True
    return loader


@pytest.fixture
def tmp_results_file(tmp_path):
    return tmp_path / "benchmark_results.json"


@pytest.fixture
def engine(mock_loader, tmp_results_file):
    return BenchmarkEngine(loader=mock_loader, results_file=tmp_results_file)


# ---------------------------------------------------------------------------
# Tests: benchmark_model
# ---------------------------------------------------------------------------


class TestBenchmarkModel:
    def test_benchmark_returns_result(self, engine, mock_loader):
        result = engine.benchmark_model("gemma3:4b", unload_after=False)
        assert isinstance(result, ModelBenchmarkResult)

    def test_benchmark_result_has_model_name(self, engine):
        result = engine.benchmark_model("gemma3:4b", unload_after=False)
        assert result.model_name == "gemma3:4b"

    def test_benchmark_result_has_composite_score(self, engine):
        result = engine.benchmark_model("gemma3:4b", unload_after=False)
        assert isinstance(result.composite_score, float)
        assert result.composite_score >= 0.0

    def test_benchmark_result_has_avg_latency(self, engine, mock_loader):
        mock_loader.generate.return_value = _make_inference_result(
            "gemma3:4b", "391", latency_ms=400.0
        )
        result = engine.benchmark_model("gemma3:4b", unload_after=False)
        assert result.avg_latency_ms > 0

    def test_benchmark_result_has_success_rate(self, engine):
        result = engine.benchmark_model("gemma3:4b", unload_after=False)
        assert 0.0 <= result.success_rate <= 1.0

    def test_benchmark_saves_to_file(self, engine, tmp_results_file):
        engine.benchmark_model("gemma3:4b", unload_after=False)
        assert tmp_results_file.exists()
        data = json.loads(tmp_results_file.read_text())
        assert "gemma3:4b" in data

    def test_benchmark_unloads_model_when_requested(self, engine, mock_loader):
        engine.benchmark_model("gemma3:4b", unload_after=True)
        mock_loader.unload.assert_called()

    def test_benchmark_quality_score_correct_answer(self, engine, mock_loader):
        """Quick math: response '391' should match expected keyword '391'."""
        mock_loader.generate.return_value = _make_inference_result(
            "gemma3:4b", "The answer is 391", latency_ms=200.0
        )
        result = engine.benchmark_model("gemma3:4b", unload_after=False)
        # At least one run should have quality score > 0 (matched "391")
        quality_runs = [r for r in result.runs if r.quality_score > 0]
        assert len(quality_runs) > 0

    def test_benchmark_all_runs_failed_produces_zero_score(self, engine, mock_loader):
        mock_loader.generate.return_value = InferenceResult(
            model_name="gemma3:4b",
            prompt="test",
            response="",
            success=False,
            inference_time_ms=100.0,
            error="connection error",
        )
        result = engine.benchmark_model("gemma3:4b", unload_after=False)
        assert result.composite_score == 0.0


# ---------------------------------------------------------------------------
# Tests: benchmark_all
# ---------------------------------------------------------------------------


class TestBenchmarkAll:
    def test_benchmark_all_returns_dict(self, engine):
        results = engine.benchmark_all(["gemma3:4b", "gemma3:12b"])
        assert isinstance(results, dict)

    def test_benchmark_all_contains_all_models(self, engine):
        results = engine.benchmark_all(["gemma3:4b", "gemma3:12b"])
        assert "gemma3:4b" in results
        assert "gemma3:12b" in results

    def test_benchmark_all_skip_existing(self, engine, mock_loader):
        engine.benchmark_model("gemma3:4b", unload_after=False)
        initial_call_count = mock_loader.generate.call_count

        engine.benchmark_all(["gemma3:4b", "gemma3:12b"], skip_existing=True)
        # gemma3:4b should be skipped, gemma3:12b should be run
        calls_after_skip = mock_loader.generate.call_count
        # Only new calls for gemma3:12b
        assert calls_after_skip > initial_call_count


# ---------------------------------------------------------------------------
# Tests: persistence
# ---------------------------------------------------------------------------


class TestBenchmarkPersistence:
    def test_results_loaded_from_file(self, mock_loader, tmp_results_file):
        # Pre-populate file with a saved result
        saved_data = {
            "gemma3:4b": {
                "model_name": "gemma3:4b",
                "timestamp": 1234567890.0,
                "runs": [],
                "avg_latency_ms": 350.0,
                "p95_latency_ms": 400.0,
                "avg_tokens_per_second": 15.0,
                "avg_quality_score": 0.75,
                "success_rate": 1.0,
                "composite_score": 42.5,
                "total_duration_ms": 1000.0,
            }
        }
        tmp_results_file.write_text(json.dumps(saved_data))

        # New engine should load persisted results
        engine2 = BenchmarkEngine(loader=mock_loader, results_file=tmp_results_file)
        result = engine2.get_result("gemma3:4b")
        assert result is not None
        assert result.composite_score == 42.5

    def test_get_result_returns_none_for_unknown(self, engine):
        result = engine.get_result("nonexistent-model:1b")
        assert result is None


# ---------------------------------------------------------------------------
# Tests: ranking and analytics
# ---------------------------------------------------------------------------


class TestRanking:
    def test_get_ranked_models_sorted_desc(self, engine, mock_loader):
        # Produce two results with different scores
        mock_loader.generate.side_effect = [
            _make_inference_result("gemma3:4b", "391", latency_ms=200.0),
            _make_inference_result("gemma3:4b", "def", latency_ms=200.0),
            _make_inference_result("gemma3:4b", "no", latency_ms=200.0),
            _make_inference_result("gemma3:4b", "learn", latency_ms=200.0),
            _make_inference_result("gemma3:12b", "391", latency_ms=1000.0),
            _make_inference_result("gemma3:12b", "def", latency_ms=1000.0),
            _make_inference_result("gemma3:12b", "no", latency_ms=1000.0),
            _make_inference_result("gemma3:12b", "learn", latency_ms=1000.0),
        ]
        engine.benchmark_model("gemma3:4b", unload_after=False)
        engine.benchmark_model("gemma3:12b", unload_after=False)

        ranked = engine.get_ranked_models()
        assert len(ranked) >= 2
        # First item should have higher score
        assert ranked[0][0] >= ranked[1][0]

    def test_get_best_model_for_speed(self, engine, mock_loader):
        mock_loader.generate.return_value = _make_inference_result(
            "gemma3:4b", "391", latency_ms=100.0, tokens=200
        )
        engine.benchmark_model("gemma3:4b", unload_after=False)
        best = engine.get_best_model_for_speed()
        assert best is not None


# ---------------------------------------------------------------------------
# Tests: BenchmarkRun
# ---------------------------------------------------------------------------


class TestBenchmarkRun:
    def test_benchmark_run_has_required_fields(self):
        run = BenchmarkRun(
            prompt_name="test",
            latency_ms=100.0,
            tokens_estimated=50,
            tokens_per_second=25.0,
            quality_score=0.8,
            success=True,
        )
        assert run.latency_ms == 100.0
        assert run.quality_score == 0.8
        assert run.success is True

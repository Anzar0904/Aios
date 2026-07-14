"""
tests/test_local_memory_integration.py

Tests for Phase 1: LocalMemoryIntegration — execution persistence.
"""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path

import pytest
from aios.local.memory_integration import LocalExecutionRecord, LocalMemoryIntegration

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test_aios.db"


@pytest.fixture
def memory(db_path):
    return LocalMemoryIntegration(db_path=db_path)


def _make_record(
    model: str = "gemma3:4b",
    capability: str = "code_generation",
    prompt: str = "Write a function",
    response: str = "def foo(): pass",
    success: bool = True,
    latency_ms: float = 300.0,
    tokens: int = 25,
    session_id: str = None,
) -> LocalExecutionRecord:
    return LocalExecutionRecord(
        model_name=model,
        capability=capability,
        prompt=prompt,
        response=response,
        success=success,
        inference_time_ms=latency_ms,
        tokens_estimated=tokens,
        tokens_per_second=tokens / (latency_ms / 1000) if latency_ms > 0 else 0,
        memory_mb=0.0,
        session_id=session_id,
    )


# ---------------------------------------------------------------------------
# Tests: table creation
# ---------------------------------------------------------------------------


class TestTableCreation:
    def test_table_created_on_init(self, db_path):
        LocalMemoryIntegration(db_path=db_path)
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='local_model_executions'"
            )
            assert cursor.fetchone() is not None

    def test_indexes_created(self, db_path):
        LocalMemoryIntegration(db_path=db_path)
        with sqlite3.connect(str(db_path)) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_local_exec_%'"
            )
            indexes = cursor.fetchall()
            assert len(indexes) >= 1


# ---------------------------------------------------------------------------
# Tests: record
# ---------------------------------------------------------------------------


class TestRecord:
    def test_record_returns_row_id(self, memory):
        record = _make_record()
        row_id = memory.record(record)
        assert isinstance(row_id, int)
        assert row_id > 0

    def test_record_increments_id(self, memory):
        r1 = memory.record(_make_record(prompt="first"))
        r2 = memory.record(_make_record(prompt="second"))
        assert r2 > r1

    def test_record_persists_model_name(self, memory, db_path):
        memory.record(_make_record(model="deepseek-coder-v2:16b"))
        with sqlite3.connect(str(db_path)) as conn:
            row = conn.execute("SELECT model_name FROM local_model_executions LIMIT 1").fetchone()
        assert row[0] == "deepseek-coder-v2:16b"

    def test_record_persists_capability(self, memory, db_path):
        memory.record(_make_record(capability="deep_reasoning"))
        with sqlite3.connect(str(db_path)) as conn:
            row = conn.execute("SELECT capability FROM local_model_executions LIMIT 1").fetchone()
        assert row[0] == "deep_reasoning"

    def test_record_persists_success_flag(self, memory, db_path):
        memory.record(_make_record(success=True))
        with sqlite3.connect(str(db_path)) as conn:
            row = conn.execute("SELECT success FROM local_model_executions LIMIT 1").fetchone()
        assert row[0] == 1

    def test_record_persists_failure_flag(self, memory, db_path):
        memory.record(_make_record(success=False))
        with sqlite3.connect(str(db_path)) as conn:
            row = conn.execute("SELECT success FROM local_model_executions LIMIT 1").fetchone()
        assert row[0] == 0

    def test_record_truncates_long_prompt(self, memory, db_path):
        long_prompt = "x" * 10000
        memory.record(_make_record(prompt=long_prompt))
        with sqlite3.connect(str(db_path)) as conn:
            row = conn.execute(
                "SELECT length(prompt) FROM local_model_executions LIMIT 1"
            ).fetchone()
        assert row[0] <= 4096

    def test_record_persists_session_id(self, memory, db_path):
        memory.record(_make_record(session_id="sess-abc123"))
        with sqlite3.connect(str(db_path)) as conn:
            row = conn.execute("SELECT session_id FROM local_model_executions LIMIT 1").fetchone()
        assert row[0] == "sess-abc123"


# ---------------------------------------------------------------------------
# Tests: get_recent_executions
# ---------------------------------------------------------------------------


class TestGetRecentExecutions:
    def test_returns_list(self, memory):
        records = memory.get_recent_executions()
        assert isinstance(records, list)

    def test_returns_recorded_executions(self, memory):
        memory.record(_make_record(model="gemma3:4b"))
        records = memory.get_recent_executions()
        assert len(records) == 1

    def test_orders_by_timestamp_desc(self, memory):
        memory.record(_make_record(prompt="first"))
        time.sleep(0.01)
        memory.record(_make_record(prompt="second"))
        records = memory.get_recent_executions()
        # Most recent first
        assert records[0].prompt == "second"

    def test_filters_by_model_name(self, memory):
        memory.record(_make_record(model="gemma3:4b"))
        memory.record(_make_record(model="deepseek-r1:14b"))
        records = memory.get_recent_executions(model_name="gemma3:4b")
        assert all(r.model_name == "gemma3:4b" for r in records)
        assert len(records) == 1

    def test_filters_by_capability(self, memory):
        memory.record(_make_record(capability="debugging"))
        memory.record(_make_record(capability="code_review"))
        records = memory.get_recent_executions(capability="debugging")
        assert all(r.capability == "debugging" for r in records)

    def test_respects_limit(self, memory):
        for i in range(10):
            memory.record(_make_record(prompt=f"prompt {i}"))
        records = memory.get_recent_executions(limit=5)
        assert len(records) == 5

    def test_returns_correct_record_type(self, memory):
        memory.record(_make_record())
        records = memory.get_recent_executions()
        assert isinstance(records[0], LocalExecutionRecord)


# ---------------------------------------------------------------------------
# Tests: get_model_stats
# ---------------------------------------------------------------------------


class TestGetModelStats:
    def test_returns_zero_stats_for_no_executions(self, memory):
        stats = memory.get_model_stats("nonexistent:1b")
        assert stats["total_requests"] == 0

    def test_counts_total_requests(self, memory):
        for _ in range(5):
            memory.record(_make_record(model="gemma3:4b"))
        stats = memory.get_model_stats("gemma3:4b")
        assert stats["total_requests"] == 5

    def test_counts_successes(self, memory):
        memory.record(_make_record(success=True))
        memory.record(_make_record(success=True))
        memory.record(_make_record(success=False))
        stats = memory.get_model_stats("gemma3:4b")
        assert stats["success_count"] == 2
        assert stats["failure_count"] == 1

    def test_success_rate_calculation(self, memory):
        memory.record(_make_record(success=True))
        memory.record(_make_record(success=False))
        stats = memory.get_model_stats("gemma3:4b")
        assert stats["success_rate"] == pytest.approx(0.5, rel=0.01)

    def test_avg_latency_calculation(self, memory):
        memory.record(_make_record(latency_ms=100.0))
        memory.record(_make_record(latency_ms=300.0))
        stats = memory.get_model_stats("gemma3:4b")
        assert stats["avg_latency_ms"] == pytest.approx(200.0, rel=0.01)


# ---------------------------------------------------------------------------
# Tests: get_capability_stats
# ---------------------------------------------------------------------------


class TestGetCapabilityStats:
    def test_returns_dict(self, memory):
        stats = memory.get_capability_stats()
        assert isinstance(stats, dict)

    def test_groups_by_capability(self, memory):
        memory.record(_make_record(capability="debugging"))
        memory.record(_make_record(capability="debugging"))
        memory.record(_make_record(capability="code_review"))
        stats = memory.get_capability_stats()
        assert "debugging" in stats
        assert stats["debugging"]["total"] == 2
        assert "code_review" in stats
        assert stats["code_review"]["total"] == 1


# ---------------------------------------------------------------------------
# Tests: error resilience
# ---------------------------------------------------------------------------


class TestErrorResilience:
    def test_bad_db_path_returns_none_not_raise(self):
        """Memory integration should not crash on bad DB path."""
        memory = LocalMemoryIntegration(db_path=Path("/nonexistent/path/test.db"))
        record = _make_record()
        result = memory.record(record)
        # Should return None (failure) but not raise
        assert result is None

    def test_get_recent_on_bad_db_returns_empty(self):
        memory = LocalMemoryIntegration(db_path=Path("/nonexistent/path/test.db"))
        records = memory.get_recent_executions()
        assert records == []

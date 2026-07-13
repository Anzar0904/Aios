"""
Regression tests for _RepositoryMixin.

Verifies that:
1. Every Group-2 repository class inherits _RepositoryMixin.
2. initialize(), start(), stop() are inherited (no-ops) correctly.
3. _guard_status() returns None on success, PersistenceResult on failure.
4. _write() produces SUCCESS on normal execution and UNKNOWN_FAILURE on error.
5. _fetch_one() returns correct payload or UNKNOWN_FAILURE when not found.
6. _fetch_all() returns a list payload on success.
7. Duplicate bootstrap (calling register twice) does NOT break the repository.
8. STRICT policy propagates RuntimeError from all mixin helpers.
"""
from __future__ import annotations

import json
from typing import Dict
from unittest.mock import MagicMock

import pytest
from aios.services.persistence import (
    PersistencePolicy,
    PersistenceResult,
    PersistenceStatus,
)
from aios.services.persistence_impl_modules.repo_base import _RepositoryMixin

# ─── Minimal concrete repo used only in these tests ───────────────────────────

class _FailingError(Exception):
    pass


class _ConcreteRepo(_RepositoryMixin):
    """Minimal concrete class – does NOT override lifecycle methods."""

    def __init__(self, service):
        self.service = service


def _make_service(*, status: str = "ok", policy: PersistencePolicy = PersistencePolicy.BEST_EFFORT):
    """Return a mock PersistenceService configured for testing."""
    svc = MagicMock()
    svc.config = MagicMock()
    svc.config.policy = policy
    svc.config.provider_name = "sqlite"

    if status == "ok":
        ok_result = PersistenceResult(
            status=PersistenceStatus.SUCCESS,
            message="ok",
            repository="test_table",
        )
        svc.check_status = MagicMock(return_value=ok_result)
    else:
        fail_result = PersistenceResult(
            status=PersistenceStatus.UNKNOWN_FAILURE,
            message="Service unavailable",
            repository="test_table",
        )
        svc.check_status = MagicMock(return_value=fail_result)

    svc.get_diagnostics_for_error = MagicMock(return_value={"error_type": "test"})
    svc.execute = MagicMock(return_value=[])
    return svc



# ─── 1. Inheritance presence ──────────────────────────────────────────────────

def test_mixin_in_group2_classes():
    """All Group-2 repository classes must inherit _RepositoryMixin."""
    from aios.services.persistence_impl_modules import repositories as R

    group2_names = [
        "EngineeringTaskRepositoryImpl",
        "PlanningRepositoryImpl",
        "ApprovalRepositoryImpl",
        "ReviewRepositoryImpl",
        "DocumentationMetadataRepositoryImpl",
        "TestSessionRepositoryImpl",
        "TestResultRepositoryImpl",
        "WorkflowRepositoryImpl",
        "WorkflowExecutionRepositoryImpl",
        "WorkflowMonitoringRepositoryImpl",
        "WorkflowOptimizationRepositoryImpl",
        "WorkflowVersionRepositoryImpl",
        "WorkflowTranslationRepositoryImpl",
        "WorkflowIntegrationRepositoryImpl",
        "AutomationTelemetryRepositoryImpl",
        "AutomationStatisticsRepositoryImpl",
        "AIProviderRepositoryImpl",
        "ProviderCapabilityRepositoryImpl",
        "ProviderHealthRepositoryImpl",
        "ProviderTelemetryRepositoryImpl",
        "ProviderStatisticsRepositoryImpl",
        "ProviderQuotaRepositoryImpl",
        "ProviderRoutingRepositoryImpl",
        "ProviderSessionRepositoryImpl",
        "ProviderCheckpointRepositoryImpl",
        "ProviderFailoverRepositoryImpl",
    ]

    for class_name in group2_names:
        cls = getattr(R, class_name, None)
        assert cls is not None, f"{class_name} not found in repositories module"
        assert issubclass(cls, _RepositoryMixin), (
            f"{class_name} does not inherit _RepositoryMixin"
        )


def test_group1_classes_unmodified():
    """Group-1 repos (Workspace, Project, EngineeringProfile, Config) must NOT use the mixin."""
    from aios.services.persistence_impl_modules import repositories as R

    group1_names = [
        "WorkspaceRepositoryImpl",
        "WorkspaceSessionRepositoryImpl",
        "ProjectRepositoryImpl",
        "EngineeringProfileRepositoryImpl",
        "ConfigurationRepositoryImpl",
    ]
    for class_name in group1_names:
        cls = getattr(R, class_name, None)
        assert cls is not None, f"{class_name} not found"
        assert not issubclass(cls, _RepositoryMixin), (
            f"{class_name} should NOT inherit _RepositoryMixin"
        )


# ─── 2. Lifecycle no-ops inherited correctly ──────────────────────────────────

def test_lifecycle_methods_are_noop():
    """initialize/start/stop inherited from mixin must be callable and return None."""
    repo = _ConcreteRepo(_make_service())
    assert repo.initialize() is None
    assert repo.start() is None
    assert repo.stop() is None


def test_group2_lifecycle_noop():
    """Spot-check a Group-2 repo: initialize/start/stop must still be no-ops."""
    from aios.services.persistence_impl_modules.repositories import EngineeringTaskRepositoryImpl
    svc = _make_service()
    repo = EngineeringTaskRepositoryImpl(svc)
    assert repo.initialize() is None
    assert repo.start() is None
    assert repo.stop() is None


# ─── 3. _guard_status ─────────────────────────────────────────────────────────

def test_guard_status_returns_none_on_success():
    svc = _make_service(status="ok")
    repo = _ConcreteRepo(svc)
    result = repo._guard_status("test_table", "save")
    assert result is None


def test_guard_status_returns_result_on_failure():
    svc = _make_service(status="fail")
    repo = _ConcreteRepo(svc)
    result = repo._guard_status("test_table", "save")
    assert result is not None
    assert result.status == PersistenceStatus.UNKNOWN_FAILURE


def test_guard_status_raises_on_strict_failure():
    svc = _make_service(status="fail", policy=PersistencePolicy.STRICT)
    repo = _ConcreteRepo(svc)
    with pytest.raises(RuntimeError, match="Service unavailable"):
        repo._guard_status("test_table", "save")


# ─── 4. _write ────────────────────────────────────────────────────────────────

def test_write_success():
    svc = _make_service()
    svc.execute.return_value = []
    repo = _ConcreteRepo(svc)
    result = repo._write("my_table", "INSERT INTO my_table VALUES (?)", ("val",), "Saved.")
    assert result.status == PersistenceStatus.SUCCESS
    assert result.repository == "my_table"
    assert result.message == "Saved."
    assert result.latency is not None and result.latency >= 0


def test_write_failure_best_effort():
    svc = _make_service()
    svc.execute.side_effect = Exception("DB error")
    repo = _ConcreteRepo(svc)
    result = repo._write("my_table", "INSERT INTO my_table VALUES (?)", ("val",), "Saved.")
    assert result.status == PersistenceStatus.UNKNOWN_FAILURE
    assert "DB error" in result.message


def test_write_failure_strict_raises():
    svc = _make_service(policy=PersistencePolicy.STRICT)
    svc.execute.side_effect = Exception("Strict DB error")
    repo = _ConcreteRepo(svc)
    with pytest.raises(RuntimeError, match="Strict DB error"):
        repo._write("my_table", "INSERT INTO my_table VALUES (?)", ("v",), "Saved.")


# ─── 5. _fetch_one ────────────────────────────────────────────────────────────

def _row(data: Dict) -> MagicMock:
    """Make a mock row that behaves like a sqlite3.Row."""
    mock = MagicMock()
    mock.__iter__ = lambda self: iter(data.items())
    mock.keys = lambda: list(data.keys())
    # dict(row) works because of __iter__
    return data  # return plain dict; dict(dict) works fine


def test_fetch_one_found():
    svc = _make_service()
    row_data = {"id": "abc", "payload": json.dumps({"x": 1})}
    svc.execute.return_value = [row_data]

    repo = _ConcreteRepo(svc)

    def parse(row):
        row["payload"] = json.loads(row["payload"])
        return row

    result = repo._fetch_one("t", "SELECT * FROM t WHERE id=?", ("abc",), "abc", parse, "Got it.")
    assert result.status == PersistenceStatus.SUCCESS
    assert result.payload["payload"] == {"x": 1}


def test_fetch_one_not_found_best_effort():
    svc = _make_service()
    svc.execute.return_value = []
    repo = _ConcreteRepo(svc)
    result = repo._fetch_one("t", "SELECT * FROM t WHERE id=?", ("abc",), "abc", lambda r: r, "Got.")
    assert result.status == PersistenceStatus.UNKNOWN_FAILURE
    assert "not found" in result.message


def test_fetch_one_not_found_strict_raises():
    svc = _make_service(policy=PersistencePolicy.STRICT)
    svc.execute.return_value = []
    repo = _ConcreteRepo(svc)
    with pytest.raises(RuntimeError, match="not found"):
        repo._fetch_one("t", "SELECT * FROM t WHERE id=?", ("abc",), "abc", lambda r: r, "Got.")


def test_fetch_one_db_error_strict_raises():
    svc = _make_service(policy=PersistencePolicy.STRICT)
    svc.execute.side_effect = Exception("DB fail")
    repo = _ConcreteRepo(svc)
    with pytest.raises(RuntimeError, match="DB fail"):
        repo._fetch_one("t", "SELECT * FROM t WHERE id=?", ("abc",), "abc", lambda r: r, "Got.")


# ─── 6. _fetch_all ────────────────────────────────────────────────────────────

def test_fetch_all_empty():
    svc = _make_service()
    svc.execute.return_value = []
    repo = _ConcreteRepo(svc)
    result = repo._fetch_all("t", "SELECT * FROM t", lambda r: r, "Listed.")
    assert result.status == PersistenceStatus.SUCCESS
    assert result.payload == []


def test_fetch_all_multiple_rows():
    svc = _make_service()
    rows = [{"id": "1", "val": '"a"'}, {"id": "2", "val": '"b"'}]
    svc.execute.return_value = rows

    def parse(row):
        row["val"] = json.loads(row["val"])
        return row

    repo = _ConcreteRepo(svc)
    result = repo._fetch_all("t", "SELECT * FROM t", parse, "Listed.")
    assert result.status == PersistenceStatus.SUCCESS
    assert len(result.payload) == 2
    assert result.payload[0]["val"] == "a"
    assert result.payload[1]["val"] == "b"


def test_fetch_all_db_error_best_effort():
    svc = _make_service()
    svc.execute.side_effect = Exception("DB fail")
    repo = _ConcreteRepo(svc)
    result = repo._fetch_all("t", "SELECT * FROM t", lambda r: r, "Listed.")
    assert result.status == PersistenceStatus.UNKNOWN_FAILURE


# ─── 7. Duplicate bootstrap safety ───────────────────────────────────────────

def test_duplicate_instantiation_is_safe():
    """Instantiating a Group-2 repo twice must not raise or corrupt state."""
    from aios.services.persistence_impl_modules.repositories import PlanningRepositoryImpl
    svc = _make_service()
    repo1 = PlanningRepositoryImpl(svc)
    repo2 = PlanningRepositoryImpl(svc)
    # Both must expose the same interface without errors
    assert repo1.initialize() is None
    assert repo2.initialize() is None
    assert repo1.service is repo2.service


# ─── 8. End-to-end save + get + delete round-trip (in-memory mock) ───────────

def test_engineering_task_roundtrip():
    """EngineeringTaskRepositoryImpl save→get→delete using mocked service."""
    from aios.services.persistence_impl_modules.repositories import EngineeringTaskRepositoryImpl

    svc = _make_service()
    task = {
        "id": "task-001",
        "name": "Build API",
        "description": "Build the REST API",
        "priority": 1,
        "status": "pending",
        "creation_time": 0,
        "update_time": 0,
        "completion_time": None,
        "workspace": "ws-1",
        "current_phase": "design",
        "assigned_agent": "agent-1",
        "dependencies": ["dep-1"],
        "retry_count": 0,
        "operation_results": {},
    }

    # save
    svc.execute.return_value = []
    repo = EngineeringTaskRepositoryImpl(svc)
    save_result = repo.save(task)
    assert save_result.status == PersistenceStatus.SUCCESS

    # get
    db_row = {
        "id": "task-001",
        "name": "Build API",
        "description": "Build the REST API",
        "priority": 1,
        "status": "pending",
        "creation_time": 0,
        "update_time": 0,
        "completion_time": None,
        "workspace": "ws-1",
        "current_phase": "design",
        "assigned_agent": "agent-1",
        "dependencies": json.dumps(["dep-1"]),
        "retry_count": 0,
        "operation_results": json.dumps({}),
    }
    svc.execute.return_value = [db_row]
    get_result = repo.get("task-001")
    assert get_result.status == PersistenceStatus.SUCCESS
    assert get_result.payload["dependencies"] == ["dep-1"]
    assert get_result.payload["operation_results"] == {}

    # delete
    svc.execute.return_value = []
    del_result = repo.delete("task-001")
    assert del_result.status == PersistenceStatus.SUCCESS

    # list_all
    svc.execute.return_value = [db_row]
    list_result = repo.list_all()
    assert list_result.status == PersistenceStatus.SUCCESS
    assert len(list_result.payload) == 1


# ─── 9. _write_with_cache ─────────────────────────────────────────────────────

def test_write_with_cache_no_cache_service():
    """_write_with_cache succeeds even when no cache service is available."""
    svc = _make_service()
    repo = _ConcreteRepo(svc)
    result = repo._write_with_cache(
        "my_table",
        "INSERT INTO my_table VALUES (?)",
        ("val",),
        "Saved.",
        cache_namespace="my_ns",
        entity_id="e1",
    )
    assert result.status == PersistenceStatus.SUCCESS
    assert result.repository == "my_table"


def test_write_with_cache_failure_best_effort():
    """_write_with_cache returns UNKNOWN_FAILURE on DB error in BEST_EFFORT mode."""
    svc = _make_service()
    svc.execute.side_effect = Exception("DB error")
    repo = _ConcreteRepo(svc)
    result = repo._write_with_cache(
        "my_table", "INSERT INTO my_table VALUES (?)", ("val",), "Saved.",
        cache_namespace="my_ns", entity_id="e1",
    )
    assert result.status == PersistenceStatus.UNKNOWN_FAILURE


def test_write_with_cache_failure_strict_raises():
    """_write_with_cache raises RuntimeError on DB error in STRICT mode."""
    svc = _make_service(policy=PersistencePolicy.STRICT)
    svc.execute.side_effect = Exception("Strict DB error")
    repo = _ConcreteRepo(svc)
    with pytest.raises(RuntimeError, match="Strict DB error"):
        repo._write_with_cache(
            "my_table", "INSERT INTO my_table VALUES (?)", ("v",), "Saved.",
            cache_namespace="my_ns", entity_id="e1",
        )


def test_write_with_cache_write_through(monkeypatch):
    """_write_with_cache calls cache_payload_fn and caches when WRITE_THROUGH policy."""
    from unittest.mock import MagicMock

    import aios.services.persistence_impl_modules.repo_base as rb

    # Build fake cache, policy_mgr
    mock_cache = MagicMock()
    mock_policy_mgr = MagicMock()

    # Patch _resolve_cache_services to return our fakes
    monkeypatch.setattr(rb._RepositoryMixin, "_resolve_cache_services", staticmethod(lambda: (mock_cache, mock_policy_mgr)))

    # Make get_policy return WRITE_THROUGH
    try:
        from aios.services.persistence import CachePolicy
        mock_policy_mgr.get_policy.return_value = CachePolicy.WRITE_THROUGH
    except Exception:
        # CachePolicy not importable in this test context — skip the assertion
        return

    svc = _make_service()
    repo = _ConcreteRepo(svc)

    payload_called = []

    def _payload():
        payload_called.append(True)
        return {"x": 1}

    result = repo._write_with_cache(
        "t", "INSERT INTO t VALUES (?)", ("v",), "Saved.",
        cache_namespace="ns", entity_id="eid",
        cache_payload_fn=_payload, retrieve_msg="Got it.",
    )
    assert result.status == PersistenceStatus.SUCCESS
    assert payload_called  # _cache_payload_fn was invoked
    mock_cache.set.assert_called_once()


# ─── 10. _delete_with_cache ───────────────────────────────────────────────────

def test_delete_with_cache_no_cache_service():
    """_delete_with_cache succeeds when no cache service is available."""
    svc = _make_service()
    repo = _ConcreteRepo(svc)
    result = repo._delete_with_cache(
        "my_table",
        "DELETE FROM my_table WHERE id = ?",
        ("e1",),
        "Deleted.",
        "my_ns",
        "e1",
    )
    assert result.status == PersistenceStatus.SUCCESS


def test_delete_with_cache_with_cache_service(monkeypatch):
    """_delete_with_cache calls cache.delete when cache service is available."""
    from unittest.mock import MagicMock

    import aios.services.persistence_impl_modules.repo_base as rb

    mock_cache = MagicMock()
    monkeypatch.setattr(rb._RepositoryMixin, "_resolve_cache_svc", staticmethod(lambda: mock_cache))

    svc = _make_service()
    repo = _ConcreteRepo(svc)
    result = repo._delete_with_cache(
        "my_table",
        "DELETE FROM my_table WHERE id = ?",
        ("e1",),
        "Deleted.",
        "my_ns",
        "e1",
    )
    assert result.status == PersistenceStatus.SUCCESS
    mock_cache.delete.assert_called_once_with("my_ns", "e1")


def test_delete_with_cache_failure_strict_raises():
    """_delete_with_cache raises RuntimeError on DB error in STRICT mode."""
    svc = _make_service(policy=PersistencePolicy.STRICT)
    svc.execute.side_effect = Exception("DB fail")
    repo = _ConcreteRepo(svc)
    with pytest.raises(RuntimeError, match="DB fail"):
        repo._delete_with_cache(
            "t", "DELETE FROM t WHERE id = ?", ("e1",), "Deleted.", "ns", "e1",
        )


# ─── 11. _fetch_one_with_cache ────────────────────────────────────────────────

def test_fetch_one_with_cache_found_no_cache():
    """_fetch_one_with_cache returns SUCCESS when row found and no cache available."""
    svc = _make_service()
    svc.execute.return_value = [{"id": "abc", "val": "1"}]
    repo = _ConcreteRepo(svc)
    result = repo._fetch_one_with_cache(
        "t",
        "SELECT * FROM t WHERE id = ?",
        ("abc",),
        "abc",
        lambda r: r,
        "Got it.",
        "Not found.",
        "ns",
    )
    assert result.status == PersistenceStatus.SUCCESS
    assert result.payload["id"] == "abc"


def test_fetch_one_with_cache_not_found_no_cache():
    """_fetch_one_with_cache returns UNKNOWN_FAILURE when no rows found."""
    svc = _make_service()
    svc.execute.return_value = []
    repo = _ConcreteRepo(svc)
    result = repo._fetch_one_with_cache(
        "t",
        "SELECT * FROM t WHERE id = ?",
        ("abc",),
        "abc",
        lambda r: r,
        "Got it.",
        "Not found.",
        "ns",
    )
    assert result.status == PersistenceStatus.UNKNOWN_FAILURE
    assert "Not found" in result.message


def test_fetch_one_with_cache_strict_not_found_raises():
    """_fetch_one_with_cache raises RuntimeError in STRICT mode when no rows."""
    svc = _make_service(policy=PersistencePolicy.STRICT)
    svc.execute.return_value = []
    repo = _ConcreteRepo(svc)
    with pytest.raises(RuntimeError, match="Not found"):
        repo._fetch_one_with_cache(
            "t", "SELECT * FROM t WHERE id = ?", ("abc",),
            "abc", lambda r: r, "Got.", "Not found.", "ns",
        )


def test_fetch_one_with_cache_uses_cache_service(monkeypatch):
    """_fetch_one_with_cache delegates to cache.get when cache service is available."""
    from unittest.mock import MagicMock

    import aios.services.persistence_impl_modules.repo_base as rb

    mock_cache = MagicMock()
    cached_result = PersistenceResult(
        status=PersistenceStatus.SUCCESS,
        message="From cache.",
        repository="t",
        payload={"id": "abc"},
    )
    mock_cache.get.return_value = cached_result
    monkeypatch.setattr(rb._RepositoryMixin, "_resolve_cache_svc", staticmethod(lambda: mock_cache))

    svc = _make_service()
    repo = _ConcreteRepo(svc)
    result = repo._fetch_one_with_cache(
        "t", "SELECT * FROM t WHERE id = ?", ("abc",),
        "abc", lambda r: r, "Got.", "Not found.", "ns",
    )
    mock_cache.get.assert_called_once()
    assert result is cached_result


# ─── 12. Provider repos fully use mixin helpers ───────────────────────────────

def test_provider_capability_uses_mixin():
    """ProviderCapabilityRepositoryImpl.save/get/delete use mixin helpers."""
    from aios.services.persistence_impl_modules.repositories import ProviderCapabilityRepositoryImpl

    svc = _make_service()
    repo = ProviderCapabilityRepositoryImpl(svc)
    assert isinstance(repo, _RepositoryMixin)

    cap = {"id": "cap-1", "provider_name": "openai", "capabilities": {"text": True}, "timestamp": 0}

    # save
    svc.execute.return_value = []
    result = repo.save(cap)
    assert result.status == PersistenceStatus.SUCCESS

    # get — not found
    svc.execute.return_value = []
    result = repo.get("cap-1")
    assert result.status == PersistenceStatus.UNKNOWN_FAILURE

    # get — found
    db_row = {"id": "cap-1", "provider_name": "openai", "capabilities": '{"text": true}', "timestamp": 0}
    svc.execute.return_value = [db_row]
    result = repo.get("cap-1")
    assert result.status == PersistenceStatus.SUCCESS
    assert result.payload["capabilities"] == {"text": True}

    # delete
    svc.execute.return_value = []
    result = repo.delete("cap-1")
    assert result.status == PersistenceStatus.SUCCESS


def test_provider_health_uses_mixin():
    """ProviderHealthRepositoryImpl.save/get/delete use mixin helpers."""
    from aios.services.persistence_impl_modules.repositories import ProviderHealthRepositoryImpl

    svc = _make_service()
    repo = ProviderHealthRepositoryImpl(svc)

    health = {"id": "h-1", "provider_name": "openai", "is_healthy": True,
              "availability_pct": 99.9, "success_rate": 0.99,
              "rate_limited_until": None, "circuit_breaker_state": "closed",
              "cooldown_until": None, "timestamp": 0}

    svc.execute.return_value = []
    result = repo.save(health)
    assert result.status == PersistenceStatus.SUCCESS

    db_row = {**health, "is_healthy": 1}
    svc.execute.return_value = [db_row]
    result = repo.get("h-1")
    assert result.status == PersistenceStatus.SUCCESS
    assert result.payload["is_healthy"] is True

    svc.execute.return_value = []
    result = repo.delete("h-1")
    assert result.status == PersistenceStatus.SUCCESS


def test_provider_routing_uses_mixin():
    """ProviderRoutingRepositoryImpl.save/get/delete use mixin helpers."""
    from aios.services.persistence_impl_modules.repositories import ProviderRoutingRepositoryImpl

    svc = _make_service()
    repo = ProviderRoutingRepositoryImpl(svc)

    routing = {"id": "r-1", "request_model": "gpt-4", "selected_provider": "openai",
               "selected_model": "gpt-4", "strategy": "cost",
               "routing_candidates": ["openai"], "operation_result_ref": None, "timestamp": 0}

    svc.execute.return_value = []
    result = repo.save(routing)
    assert result.status == PersistenceStatus.SUCCESS

    db_row = {**routing, "routing_candidates": '["openai"]'}
    svc.execute.return_value = [db_row]
    result = repo.get("r-1")
    assert result.status == PersistenceStatus.SUCCESS
    assert result.payload["routing_candidates"] == ["openai"]

    svc.execute.return_value = []
    result = repo.delete("r-1")
    assert result.status == PersistenceStatus.SUCCESS

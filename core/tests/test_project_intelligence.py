"""Phase 5: Project Intelligence — Production Test Suite.

Tests cover:
- Project Registry CRUD (create, read, update, delete)
- Project Profile serialization / deserialization
- Project Memory CRUD and search
- Project Context management and context switching
- Dashboard data assembly
- Cross-project queries (by integration, related, attention)
- Project auto-detection from workspace path
- Built-in project seeding
- Model Router integration
- Graph Bridge integration (mocked)
- Thread safety
"""

from __future__ import annotations

import time
import uuid
from unittest.mock import MagicMock

import pytest
from aios.services.project_registry import (
    ProjectMemoryEntry,
    ProjectPriority,
    ProjectProfile,
    ProjectRuntimeContext,
    ProjectStatus,
    ProjectType,
    new_entry_id,
    new_project_id,
)
from aios.services.project_registry_impl import (
    BUILTIN_PROJECTS,
    ProjectContextImpl,
    ProjectMemoryImpl,
    ProjectRegistryImpl,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_db(tmp_path):
    return str(tmp_path / "test_projects.db")


@pytest.fixture
def reg(tmp_db):
    r = ProjectRegistryImpl(db_path=tmp_db)
    r.initialize()
    r.start()
    yield r
    r.shutdown()


@pytest.fixture
def mem(tmp_db):
    m = ProjectMemoryImpl(db_path=tmp_db)
    m.initialize()
    m.start()
    yield m
    m.shutdown()


@pytest.fixture
def ctx(reg, tmp_db):
    c = ProjectContextImpl(registry=reg, db_path=tmp_db)
    c.initialize()
    c.start()
    yield c
    c.shutdown()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_profile(
    name: str = "Test Project",
    ptype: ProjectType = ProjectType.SOFTWARE,
    priority: ProjectPriority = ProjectPriority.MEDIUM,
    status: ProjectStatus = ProjectStatus.ACTIVE,
    models: list | None = None,
    tags: list | None = None,
) -> ProjectProfile:
    return ProjectProfile(
        project_id=new_project_id(),
        name=name,
        description=f"Description for {name}",
        project_type=ptype,
        status=status,
        priority=priority,
        owner="Test Owner",
        preferred_models=models or ["deepseek-r1"],
        tags=tags or [],
    )


def make_memory_entry(
    project_id: str,
    category: str = "decisions",
    title: str = "My Entry",
) -> ProjectMemoryEntry:
    return ProjectMemoryEntry(
        entry_id=new_entry_id(),
        project_id=project_id,
        category=category,
        title=title,
        content="Some important content here",
        tags=["test", "memory"],
    )


# ---------------------------------------------------------------------------
# Project Registry — Lifecycle
# ---------------------------------------------------------------------------


class TestProjectRegistryLifecycle:
    def test_initialize_creates_schema(self, reg):
        assert reg.ready() is True

    def test_shutdown_disables_ready(self, tmp_db):
        r = ProjectRegistryImpl(db_path=tmp_db)
        r.initialize()
        r.shutdown()
        assert r.ready() is False

    def test_builtin_projects_seeded(self, reg):
        projects = reg.list_projects()
        names = {p.name for p in projects}
        for spec in BUILTIN_PROJECTS:
            assert spec["name"] in names, f"Built-in '{spec['name']}' not seeded"

    def test_seeding_is_idempotent(self, reg):
        before = len(reg.list_projects())
        reg._seed_builtin_projects()
        after = len(reg.list_projects())
        assert before == after


# ---------------------------------------------------------------------------
# Project Registry — CRUD
# ---------------------------------------------------------------------------


class TestProjectRegistryCRUD:
    def test_register_and_get_project(self, reg):
        p = make_profile("Alpha")
        reg.register_project(p)
        fetched = reg.get_project(p.project_id)
        assert fetched is not None
        assert fetched.name == "Alpha"

    def test_get_nonexistent_project_returns_none(self, reg):
        assert reg.get_project("nonexistent-id") is None

    def test_find_project_by_name(self, reg):
        p = make_profile("Beta")
        reg.register_project(p)
        found = reg.find_project("Beta")
        assert found is not None
        assert found.project_id == p.project_id

    def test_find_project_case_insensitive(self, reg):
        p = make_profile("GammaProject")
        reg.register_project(p)
        found = reg.find_project("gammaproject")
        assert found is not None

    def test_find_nonexistent_project_returns_none(self, reg):
        assert reg.find_project("NoSuchProjectXYZ") is None

    def test_list_projects(self, reg):
        p1 = make_profile("P1")
        p2 = make_profile("P2")
        reg.register_project(p1)
        reg.register_project(p2)
        all_projects = reg.list_projects()
        names = {p.name for p in all_projects}
        assert "P1" in names
        assert "P2" in names

    def test_list_projects_filter_by_type(self, reg):
        p = make_profile("SoftwareProj", ptype=ProjectType.SOFTWARE)
        reg.register_project(p)
        software = reg.list_projects(project_type=ProjectType.SOFTWARE)
        assert all(s.project_type == ProjectType.SOFTWARE for s in software)

    def test_list_projects_filter_by_status(self, reg):
        p = make_profile("PausedProj", status=ProjectStatus.PAUSED)
        reg.register_project(p)
        paused = reg.list_projects(status=ProjectStatus.PAUSED)
        assert all(s.status == ProjectStatus.PAUSED for s in paused)

    def test_update_project(self, reg):
        p = make_profile("UpdateMe")
        reg.register_project(p)
        updated = reg.update_project(p.project_id, {"current_sprint": "Sprint 99"})
        assert updated is not None
        assert updated.current_sprint == "Sprint 99"

    def test_update_nonexistent_returns_none(self, reg):
        result = reg.update_project("bad-id", {"name": "x"})
        assert result is None

    def test_delete_project(self, reg):
        p = make_profile("DeleteMe")
        reg.register_project(p)
        assert reg.delete_project(p.project_id) is True
        assert reg.get_project(p.project_id) is None

    def test_delete_nonexistent_returns_false(self, reg):
        assert reg.delete_project("not-real") is False

    def test_register_deduplicates_by_id(self, reg):
        p = make_profile("Dedup")
        reg.register_project(p)
        p2 = ProjectProfile.from_dict({**p.to_dict(), "description": "Updated"})
        reg.register_project(p2)
        fetched = reg.get_project(p.project_id)
        assert fetched.description == "Updated"


# ---------------------------------------------------------------------------
# Project Registry — Active Project
# ---------------------------------------------------------------------------


class TestProjectRegistryActiveProject:
    def test_set_and_get_active_project(self, reg):
        p = make_profile("ActiveProj")
        reg.register_project(p)
        assert reg.set_active_project(p.project_id) is True
        active = reg.get_active_project()
        assert active is not None
        assert active.project_id == p.project_id

    def test_set_active_nonexistent_returns_false(self, reg):
        assert reg.set_active_project("bad-id") is False

    def test_default_active_project_is_ai_os(self, reg):
        active = reg.get_active_project()
        assert active is not None
        assert active.name == "AI OS"


# ---------------------------------------------------------------------------
# Project Registry — Auto-Detection
# ---------------------------------------------------------------------------


class TestProjectAutoDetection:
    def test_detect_aios_project(self, reg):
        found = reg.detect_project_from_workspace("/Users/user/aios/core")
        assert found is not None
        assert found.name == "AI OS"

    def test_detect_agency_project(self, reg):
        found = reg.detect_project_from_workspace("/Users/user/agency/src")
        assert found is not None
        assert found.name == "Agency"

    def test_detect_campusconnect_project(self, reg):
        found = reg.detect_project_from_workspace("/Users/user/campusconnect")
        assert found is not None

    def test_detect_unknown_workspace_returns_none(self, reg):
        found = reg.detect_project_from_workspace("/Users/user/unknown-repo-xyz")
        assert found is None


# ---------------------------------------------------------------------------
# Project Registry — Cross-Project Intelligence
# ---------------------------------------------------------------------------


class TestCrossProjectIntelligence:
    def test_query_by_integration_github(self, reg):
        matches = reg.query_by_integration("github")
        assert any(p.github.enabled for p in matches)

    def test_query_by_integration_notion(self, reg):
        matches = reg.query_by_integration("notion")
        assert any(p.notion.enabled for p in matches)

    def test_query_by_integration_tag(self, reg):
        p = make_profile("TagProj", tags=["supabase", "postgres"])
        reg.register_project(p)
        matches = reg.query_by_integration("supabase")
        names = {m.name for m in matches}
        assert "TagProj" in names

    def test_find_related_by_model(self, reg):
        p1 = make_profile("ModelProj1", models=["deepseek-r1", "qwen3.5"])
        p2 = make_profile("ModelProj2", models=["deepseek-r1"])
        reg.register_project(p1)
        reg.register_project(p2)
        related = reg.find_related_projects(p1.project_id)
        names = {r.name for r in related}
        assert "ModelProj2" in names

    def test_find_related_by_tags(self, reg):
        p1 = make_profile("TagProj1", tags=["ai", "research"])
        p2 = make_profile("TagProj2", tags=["ai", "ml"])
        reg.register_project(p1)
        reg.register_project(p2)
        related = reg.find_related_projects(p1.project_id)
        names = {r.name for r in related}
        assert "TagProj2" in names

    def test_projects_needing_attention_includes_paused(self, reg):
        p = make_profile("PausedNeed", status=ProjectStatus.PAUSED)
        reg.register_project(p)
        needing = reg.get_projects_needing_attention()
        names = {n.name for n in needing}
        assert "PausedNeed" in names

    def test_projects_needing_attention_stale_active(self, reg):
        p = make_profile("StaleProj", status=ProjectStatus.ACTIVE)
        p2 = ProjectProfile.from_dict({**p.to_dict(), "last_active": time.time() - (10 * 86400)})
        reg.register_project(p2)
        needing = reg.get_projects_needing_attention()
        names = {n.name for n in needing}
        assert "StaleProj" in names


# ---------------------------------------------------------------------------
# Project Profile — Serialization
# ---------------------------------------------------------------------------


class TestProjectProfileSerialization:
    def test_to_and_from_dict_roundtrip(self):
        p = make_profile(
            "SerializeMe",
            ptype=ProjectType.RESEARCH,
            priority=ProjectPriority.HIGH,
            status=ProjectStatus.PLANNING,
            models=["deepseek-r1", "qwen3.5"],
            tags=["ai", "ml"],
        )
        r = ProjectProfile.from_dict(p.to_dict())
        assert r.project_id == p.project_id
        assert r.project_type == p.project_type
        assert r.priority == p.priority
        assert r.status == p.status
        assert r.preferred_models == p.preferred_models
        assert r.tags == p.tags

    def test_all_project_types_roundtrip(self):
        for ptype in ProjectType:
            p = make_profile(f"Test-{ptype.value}", ptype=ptype)
            r = ProjectProfile.from_dict(p.to_dict())
            assert r.project_type == ptype

    def test_all_priorities_roundtrip(self):
        for prio in ProjectPriority:
            p = make_profile(f"Prio-{prio.value}", priority=prio)
            r = ProjectProfile.from_dict(p.to_dict())
            assert r.priority == prio

    def test_all_statuses_roundtrip(self):
        for status in ProjectStatus:
            p = make_profile(f"Stat-{status.value}", status=status)
            r = ProjectProfile.from_dict(p.to_dict())
            assert r.status == status

    def test_github_config_roundtrip(self):
        p = make_profile("GHProj")
        p.github.enabled = True
        p.github.repo = "org/repo"
        p.github.branch = "develop"
        r = ProjectProfile.from_dict(p.to_dict())
        assert r.github.enabled is True
        assert r.github.repo == "org/repo"
        assert r.github.branch == "develop"

    def test_notion_config_roundtrip(self):
        p = make_profile("NotionProj")
        p.notion.enabled = True
        p.notion.workspace_id = "ws-123"
        r = ProjectProfile.from_dict(p.to_dict())
        assert r.notion.enabled is True
        assert r.notion.workspace_id == "ws-123"

    def test_n8n_config_roundtrip(self):
        p = make_profile("N8nProj")
        p.n8n.enabled = True
        p.n8n.workflow_ids = ["wf-1", "wf-2"]
        r = ProjectProfile.from_dict(p.to_dict())
        assert r.n8n.enabled is True
        assert r.n8n.workflow_ids == ["wf-1", "wf-2"]

    def test_unique_project_ids(self):
        ids = {new_project_id() for _ in range(50)}
        assert len(ids) == 50


# ---------------------------------------------------------------------------
# Project Memory
# ---------------------------------------------------------------------------


class TestProjectMemory:
    def test_store_and_retrieve(self, mem):
        pid = new_project_id()
        entry = make_memory_entry(pid, "decisions", "My Decision")
        mem.store(entry)
        results = mem.retrieve(pid)
        assert any(e.entry_id == entry.entry_id for e in results)

    def test_retrieve_by_category(self, mem):
        pid = new_project_id()
        mem.store(make_memory_entry(pid, "decisions", "Decision 1"))
        mem.store(make_memory_entry(pid, "architecture", "Arch note 1"))
        decisions = mem.retrieve(pid, category="decisions")
        assert all(e.category == "decisions" for e in decisions)

    def test_retrieve_respects_limit(self, mem):
        pid = new_project_id()
        for i in range(10):
            mem.store(make_memory_entry(pid, "meetings", f"Meeting {i}"))
        results = mem.retrieve(pid, limit=3)
        assert len(results) <= 3

    def test_search_by_title(self, mem):
        pid = new_project_id()
        mem.store(make_memory_entry(pid, "research", "SearchableTitleXYZ"))
        mem.store(make_memory_entry(pid, "research", "OtherTitle"))
        found = mem.search(pid, "SearchableTitleXYZ")
        assert any("SearchableTitleXYZ" in e.title for e in found)

    def test_search_by_content(self, mem):
        pid = new_project_id()
        e = ProjectMemoryEntry(
            entry_id=new_entry_id(),
            project_id=pid,
            category="notes",
            title="Plain Title",
            content="special_content_marker_for_search_test",
        )
        mem.store(e)
        found = mem.search(pid, "special_content_marker")
        assert len(found) >= 1

    def test_delete_entry(self, mem):
        pid = new_project_id()
        entry = make_memory_entry(pid, "tasks", "To Delete")
        mem.store(entry)
        assert mem.delete_entry(entry.entry_id) is True
        results = mem.retrieve(pid)
        assert not any(e.entry_id == entry.entry_id for e in results)

    def test_delete_nonexistent_returns_false(self, mem):
        assert mem.delete_entry("bad-id") is False

    def test_get_recent_returns_entries(self, mem):
        pid = new_project_id()
        for i in range(5):
            e = ProjectMemoryEntry(
                entry_id=new_entry_id(),
                project_id=pid,
                category="meetings",
                title=f"Meeting {i}",
                content="",
                updated_at=time.time() + i,
            )
            mem.store(e)
        recent = mem.get_recent(pid, limit=3)
        assert len(recent) <= 3

    def test_memory_entry_roundtrip(self):
        e = make_memory_entry(new_project_id(), "decisions", "My Decision")
        r = ProjectMemoryEntry.from_dict(e.to_dict())
        assert r.entry_id == e.entry_id
        assert r.project_id == e.project_id
        assert r.category == e.category
        assert r.title == e.title

    def test_store_upserts_existing(self, mem):
        pid = new_project_id()
        entry = make_memory_entry(pid, "notes", "Original")
        mem.store(entry)
        entry2 = ProjectMemoryEntry(
            entry_id=entry.entry_id,
            project_id=pid,
            category="notes",
            title="Updated Title",
            content="New content",
            updated_at=time.time(),
        )
        mem.store(entry2)
        results = mem.retrieve(pid)
        titles = [e.title for e in results]
        assert "Updated Title" in titles
        assert "Original" not in titles


# ---------------------------------------------------------------------------
# Project Context
# ---------------------------------------------------------------------------


class TestProjectContext:
    def test_get_context_builds_from_profile(self, reg, ctx):
        ai_os = reg.find_project("AI OS")
        assert ai_os is not None
        context = ctx.get_context(ai_os.project_id)
        assert context is not None
        assert context.project_name == "AI OS"

    def test_get_context_nonexistent_returns_none(self, reg, ctx):
        assert ctx.get_context("bad-id") is None

    def test_update_context(self, reg, ctx):
        ai_os = reg.find_project("AI OS")
        assert ai_os is not None
        updated = ctx.update_context(ai_os.project_id, {"current_sprint": "Sprint 99"})
        assert updated.current_sprint == "Sprint 99"

    def test_switch_to_sets_active(self, reg, ctx):
        agency = reg.find_project("Agency")
        assert agency is not None
        switched = ctx.switch_to(agency.project_id)
        assert switched.project_id == agency.project_id
        active = ctx.get_active_context()
        assert active is not None
        assert active.project_id == agency.project_id

    def test_switch_to_nonexistent_raises(self, reg, ctx):
        with pytest.raises(ValueError):
            ctx.switch_to("nonexistent-id")

    def test_get_active_context_defaults_to_ai_os(self, reg, ctx):
        active = ctx.get_active_context()
        assert active is not None
        assert active.project_name == "AI OS"

    def test_context_persists_across_instances(self, reg, tmp_db):
        ctx1 = ProjectContextImpl(registry=reg, db_path=tmp_db)
        ctx1.initialize()
        ai_os = reg.find_project("AI OS")
        ctx1.update_context(ai_os.project_id, {"current_sprint": "PersistSprint"})
        ctx1.shutdown()

        ctx2 = ProjectContextImpl(registry=reg, db_path=tmp_db)
        ctx2.initialize()
        result = ctx2.get_context(ai_os.project_id)
        assert result is not None
        assert result.current_sprint == "PersistSprint"
        ctx2.shutdown()

    def test_get_dashboard_data(self, reg, ctx):
        ai_os = reg.find_project("AI OS")
        assert ai_os is not None
        dash = ctx.get_dashboard_data(ai_os.project_id)
        assert "project" in dash
        assert "context" in dash
        assert "health_score" in dash
        assert "integrations" in dash
        assert "preferred_models" in dash

    def test_get_dashboard_data_nonexistent(self, reg, ctx):
        dash = ctx.get_dashboard_data("bad-id")
        assert "error" in dash

    def test_dashboard_health_score_range(self, reg, ctx):
        ai_os = reg.find_project("AI OS")
        dash = ctx.get_dashboard_data(ai_os.project_id)
        assert 0 <= dash["health_score"] <= 100

    def test_dashboard_paused_project_lower_health(self, reg, ctx):
        p = make_profile("PausedForDash", status=ProjectStatus.PAUSED)
        reg.register_project(p)
        dash = ctx.get_dashboard_data(p.project_id)
        assert dash["health_score"] < 100


# ---------------------------------------------------------------------------
# Project Runtime Context — Serialization
# ---------------------------------------------------------------------------


class TestProjectRuntimeContextSerialization:
    def test_to_and_from_dict_roundtrip(self):
        ctx = ProjectRuntimeContext(
            project_id="pid-1",
            project_name="My Project",
            current_sprint="Sprint 5",
            active_models=["deepseek-r1"],
            open_tasks=[{"title": "Task 1", "status": "Pending"}],
        )
        r = ProjectRuntimeContext.from_dict(ctx.to_dict())
        assert r.project_id == ctx.project_id
        assert r.current_sprint == ctx.current_sprint
        assert r.active_models == ctx.active_models
        assert r.open_tasks == ctx.open_tasks


# ---------------------------------------------------------------------------
# Builtin Project Data Validation
# ---------------------------------------------------------------------------


class TestBuiltinProjectData:
    def test_ai_os_has_preferred_models(self, reg):
        p = reg.find_project("AI OS")
        assert p is not None
        assert len(p.preferred_models) > 0
        assert "deepseek-coder-v2" in p.preferred_models

    def test_research_uses_reasoning_model(self, reg):
        p = reg.find_project("Research")
        assert p is not None
        assert any("deepseek-r1" in m or "r1" in m for m in p.preferred_models)

    def test_agency_notion_enabled(self, reg):
        p = reg.find_project("Agency")
        assert p is not None
        assert p.notion.enabled is True

    def test_ai_os_github_enabled(self, reg):
        p = reg.find_project("AI OS")
        assert p is not None
        assert p.github.enabled is True
        assert p.github.repo == "Anzar0904/Aios"

    def test_all_builtin_projects_have_valid_types(self, reg):
        for p in reg.list_projects():
            assert isinstance(p.project_type, ProjectType)
            assert isinstance(p.status, ProjectStatus)
            assert isinstance(p.priority, ProjectPriority)

    def test_seven_canonical_projects_seeded(self, reg):
        assert len(reg.list_projects()) == len(BUILTIN_PROJECTS)


# ---------------------------------------------------------------------------
# Project Graph Bridge
# ---------------------------------------------------------------------------


class TestProjectGraphBridge:
    def test_register_project_in_graph(self):
        from aios.services.project_graph_bridge import ProjectGraphBridge

        mock_engine = MagicMock()
        mock_entity = MagicMock()
        mock_entity.entity_id = "mock-entity-id"
        mock_engine.ensure_entity.return_value = mock_entity

        bridge = ProjectGraphBridge(mock_engine)
        p = make_profile("GraphBridgeProj")
        entity_id = bridge.register_project_in_graph(p)
        assert entity_id == "mock-entity-id"

    def test_link_repository_to_project(self):
        from aios.services.project_graph_bridge import ProjectGraphBridge

        mock_engine = MagicMock()
        bridge = ProjectGraphBridge(mock_engine)
        bridge.link_repository_to_project("my-repo", "AI OS")
        mock_engine.link_repository_to_project.assert_called_once_with("my-repo", "AI OS")

    def test_link_task_to_project(self):
        from aios.services.project_graph_bridge import ProjectGraphBridge

        mock_engine = MagicMock()
        bridge = ProjectGraphBridge(mock_engine)
        bridge.link_task_to_project("My Task", "AI OS")
        mock_engine.link_task_to_project.assert_called_once_with("My Task", "AI OS")

    def test_link_document_to_project(self):
        from aios.services.project_graph_bridge import ProjectGraphBridge

        mock_engine = MagicMock()
        bridge = ProjectGraphBridge(mock_engine)
        bridge.link_document_to_project("README.md", "AI OS")
        mock_engine.link_document_to_project.assert_called_once_with("README.md", "AI OS")

    def test_link_decision_to_project(self):
        from aios.services.project_graph_bridge import ProjectGraphBridge

        mock_engine = MagicMock()
        bridge = ProjectGraphBridge(mock_engine)
        bridge.link_decision_to_project("Use SQLite", "AI OS")
        mock_engine.link_decision_to_project.assert_called_once_with("Use SQLite", "AI OS")

    def test_link_workflow_to_project(self):
        from aios.services.project_graph_bridge import ProjectGraphBridge

        mock_engine = MagicMock()
        bridge = ProjectGraphBridge(mock_engine)
        bridge.link_workflow_to_project("CI Pipeline", "AI OS")
        mock_engine.link_workflow_to_project.assert_called_once_with("CI Pipeline", "AI OS")

    def test_graph_errors_handled_gracefully(self):
        from aios.services.project_graph_bridge import ProjectGraphBridge

        mock_engine = MagicMock()
        mock_engine.ensure_entity.side_effect = RuntimeError("graph down")
        bridge = ProjectGraphBridge(mock_engine)
        entity_id = bridge.register_project_in_graph(make_profile("ErrorProj"))
        assert entity_id == ""


# ---------------------------------------------------------------------------
# Project Model Router
# ---------------------------------------------------------------------------


class TestProjectModelRouter:
    def test_get_preferred_models_for_project(self, reg):
        from aios.services.project_graph_bridge import ProjectModelRouter

        router = ProjectModelRouter(reg)
        models = router.get_preferred_models("AI OS")
        assert len(models) > 0
        assert "deepseek-coder-v2" in models

    def test_get_primary_model(self, reg):
        from aios.services.project_graph_bridge import ProjectModelRouter

        router = ProjectModelRouter(reg)
        primary = router.get_primary_model("AI OS")
        assert primary == "deepseek-coder-v2"

    def test_get_model_profile(self, reg):
        from aios.services.project_graph_bridge import ProjectModelRouter

        router = ProjectModelRouter(reg)
        profile = router.get_model_profile("Research")
        assert "preferred_models" in profile
        assert "primary_model" in profile
        assert profile["project"] == "Research"

    def test_fallback_to_global_defaults(self, reg):
        from aios.services.project_graph_bridge import ProjectModelRouter

        router = ProjectModelRouter(reg)
        models = router.get_preferred_models("NonExistentProjectXYZ")
        assert len(models) > 0

    def test_get_preferred_models_uses_active_project(self, reg):
        from aios.services.project_graph_bridge import ProjectModelRouter

        router = ProjectModelRouter(reg)
        models = router.get_preferred_models()
        assert len(models) > 0


# ---------------------------------------------------------------------------
# Thread Safety
# ---------------------------------------------------------------------------


class TestThreadSafety:
    def test_concurrent_project_creation(self, reg):
        import threading

        results = []
        errors = []

        def create():
            try:
                p = make_profile(f"ThreadProj-{uuid.uuid4().hex[:6]}")
                reg.register_project(p)
                results.append(p.project_id)
            except Exception as exc:
                errors.append(str(exc))

        threads = [threading.Thread(target=create) for _ in range(15)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 15

    def test_concurrent_memory_store(self, mem):
        import threading

        pid = new_project_id()
        errors = []

        def store():
            try:
                mem.store(make_memory_entry(pid, "notes", f"Note {uuid.uuid4().hex[:6]}"))
            except Exception as exc:
                errors.append(str(exc))

        threads = [threading.Thread(target=store) for _ in range(15)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(mem.retrieve(pid)) == 15

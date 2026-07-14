"""Phase 4.5: Universal Knowledge Graph — Production Test Suite.

Tests cover:
- Entity CRUD operations
- Relationship CRUD operations
- Event recording and retrieval
- Graph query operations (neighbors, path-finding, search)
- Project subgraph traversal
- Graph Query Engine high-level API
- Integration hooks (auto-link on task/project/document/workflow/decision)
- CLI handler dispatch
- Stats and health checks
"""

import os
import uuid
from unittest.mock import patch

import pytest
from aios.services.graph import (
    EntityType,
    GraphEntity,
    GraphEvent,
    GraphEventType,
    GraphRelationship,
    GraphStats,
    RelationshipType,
    new_entity,
    new_event,
    new_relationship,
)
from aios.services.graph_hooks import GraphIntegrationHooks
from aios.services.graph_impl import GraphServiceImpl
from aios.services.graph_query import GraphQueryEngine

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_db(tmp_path):
    """Return a path to a temporary SQLite database file."""
    return str(tmp_path / "test_graph.db")


@pytest.fixture
def graph(tmp_db):
    """Initialized GraphServiceImpl backed by a temp SQLite file."""
    svc = GraphServiceImpl(db_path=tmp_db)
    svc.initialize()
    svc.start()
    yield svc
    svc.shutdown()


@pytest.fixture
def engine(graph):
    """GraphQueryEngine wrapping the test graph service."""
    return GraphQueryEngine(graph)


@pytest.fixture
def hooks(graph):
    """GraphIntegrationHooks backed by the test graph service."""
    return GraphIntegrationHooks(graph)


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def make_entity(
    entity_type: EntityType = EntityType.PROJECT, name: str = "Test Entity"
) -> GraphEntity:
    return new_entity(entity_type, name, {"test": True})


def make_relationship(
    source_id: str, target_id: str, rel_type: RelationshipType = RelationshipType.BELONGS_TO
) -> GraphRelationship:
    return new_relationship(source_id, target_id, rel_type)


# ---------------------------------------------------------------------------
# Service lifecycle tests
# ---------------------------------------------------------------------------


class TestGraphServiceLifecycle:
    def test_initialize_creates_schema(self, graph):
        assert graph.ready() is True

    def test_health_check_passes(self, graph):
        assert graph.health_check() is True

    def test_shutdown_disables_ready(self, tmp_db):
        svc = GraphServiceImpl(db_path=tmp_db)
        svc.initialize()
        svc.shutdown()
        assert svc.ready() is False

    def test_double_initialize_is_idempotent(self, tmp_db):
        svc = GraphServiceImpl(db_path=tmp_db)
        svc.initialize()
        svc.initialize()  # second call should not raise
        assert svc.ready() is True
        svc.shutdown()

    def test_default_db_path_uses_env(self, tmp_path):
        db = str(tmp_path / "env_graph.db")
        os.environ["AIOS_GRAPH_DB"] = db
        svc = GraphServiceImpl()
        assert svc._db_path == db
        del os.environ["AIOS_GRAPH_DB"]


# ---------------------------------------------------------------------------
# Entity CRUD
# ---------------------------------------------------------------------------


class TestEntityCRUD:
    def test_create_and_get_entity(self, graph):
        entity = make_entity(EntityType.PROJECT, "Alpha Project")
        created = graph.create_entity(entity)
        assert created.entity_id == entity.entity_id

        fetched = graph.get_entity(entity.entity_id)
        assert fetched is not None
        assert fetched.name == "Alpha Project"
        assert fetched.entity_type == EntityType.PROJECT

    def test_get_nonexistent_entity_returns_none(self, graph):
        assert graph.get_entity("nonexistent-id") is None

    def test_find_entities_by_type(self, graph):
        graph.create_entity(make_entity(EntityType.PROJECT, "Proj A"))
        graph.create_entity(make_entity(EntityType.TASK, "Task B"))
        graph.create_entity(make_entity(EntityType.PROJECT, "Proj C"))

        projects = graph.find_entities(entity_type=EntityType.PROJECT)
        project_names = {e.name for e in projects}
        assert "Proj A" in project_names
        assert "Proj C" in project_names
        assert "Task B" not in project_names

    def test_find_entities_by_name_contains(self, graph):
        graph.create_entity(make_entity(EntityType.PROJECT, "Alpha"))
        graph.create_entity(make_entity(EntityType.PROJECT, "Beta"))
        graph.create_entity(make_entity(EntityType.PROJECT, "Alphabet"))

        results = graph.find_entities(name_contains="Alpha")
        names = {e.name for e in results}
        assert "Alpha" in names
        assert "Alphabet" in names
        assert "Beta" not in names

    def test_find_entities_with_limit(self, graph):
        for i in range(10):
            graph.create_entity(make_entity(EntityType.TASK, f"Task {i}"))
        results = graph.find_entities(entity_type=EntityType.TASK, limit=3)
        assert len(results) <= 3

    def test_update_entity_name_and_properties(self, graph):
        entity = graph.create_entity(make_entity(EntityType.PROJECT, "Old Name"))
        updated = graph.update_entity(
            entity.entity_id,
            {"name": "New Name", "properties": {"status": "active"}},
        )
        assert updated is not None
        assert updated.name == "New Name"
        assert updated.properties.get("status") == "active"

    def test_update_nonexistent_entity_returns_none(self, graph):
        result = graph.update_entity("bad-id", {"name": "x"})
        assert result is None

    def test_delete_entity(self, graph):
        entity = graph.create_entity(make_entity(EntityType.PROJECT, "To Delete"))
        assert graph.delete_entity(entity.entity_id) is True
        assert graph.get_entity(entity.entity_id) is None

    def test_delete_nonexistent_entity_returns_false(self, graph):
        assert graph.delete_entity("not-real") is False

    def test_delete_entity_cascades_relationships(self, graph):
        src = graph.create_entity(make_entity(EntityType.TASK, "Task"))
        tgt = graph.create_entity(make_entity(EntityType.PROJECT, "Proj"))
        graph.create_relationship(make_relationship(src.entity_id, tgt.entity_id))

        graph.delete_entity(src.entity_id)
        rels = graph.find_relationships(source_id=src.entity_id)
        assert len(rels) == 0

    def test_all_entity_types_can_be_created(self, graph):
        for etype in EntityType:
            e = graph.create_entity(make_entity(etype, f"Test {etype.value}"))
            fetched = graph.get_entity(e.entity_id)
            assert fetched is not None
            assert fetched.entity_type == etype


# ---------------------------------------------------------------------------
# Relationship CRUD
# ---------------------------------------------------------------------------


class TestRelationshipCRUD:
    def test_create_and_get_relationship(self, graph):
        src = graph.create_entity(make_entity(EntityType.TASK, "Task"))
        tgt = graph.create_entity(make_entity(EntityType.PROJECT, "Project"))
        rel = graph.create_relationship(
            new_relationship(src.entity_id, tgt.entity_id, RelationshipType.BELONGS_TO)
        )

        fetched = graph.get_relationship(rel.relationship_id)
        assert fetched is not None
        assert fetched.source_id == src.entity_id
        assert fetched.target_id == tgt.entity_id
        assert fetched.relationship_type == RelationshipType.BELONGS_TO

    def test_get_nonexistent_relationship_returns_none(self, graph):
        assert graph.get_relationship("nonexistent") is None

    def test_find_relationships_by_source(self, graph):
        src = graph.create_entity(make_entity(EntityType.TASK, "Src"))
        tgt1 = graph.create_entity(make_entity(EntityType.PROJECT, "P1"))
        tgt2 = graph.create_entity(make_entity(EntityType.PROJECT, "P2"))
        other = graph.create_entity(make_entity(EntityType.TASK, "Other"))

        graph.create_relationship(
            new_relationship(src.entity_id, tgt1.entity_id, RelationshipType.BELONGS_TO)
        )
        graph.create_relationship(
            new_relationship(src.entity_id, tgt2.entity_id, RelationshipType.USES)
        )
        graph.create_relationship(
            new_relationship(other.entity_id, tgt1.entity_id, RelationshipType.BELONGS_TO)
        )

        rels = graph.find_relationships(source_id=src.entity_id)
        assert len(rels) == 2

    def test_find_relationships_by_type(self, graph):
        src = graph.create_entity(make_entity(EntityType.TASK, "T"))
        tgt = graph.create_entity(make_entity(EntityType.PROJECT, "P"))
        graph.create_relationship(
            new_relationship(src.entity_id, tgt.entity_id, RelationshipType.BELONGS_TO)
        )
        graph.create_relationship(
            new_relationship(src.entity_id, tgt.entity_id, RelationshipType.USES)
        )

        rels = graph.find_relationships(relationship_type=RelationshipType.BELONGS_TO)
        for r in rels:
            assert r.relationship_type == RelationshipType.BELONGS_TO

    def test_delete_relationship(self, graph):
        src = graph.create_entity(make_entity(EntityType.TASK, "T"))
        tgt = graph.create_entity(make_entity(EntityType.PROJECT, "P"))
        rel = graph.create_relationship(
            new_relationship(src.entity_id, tgt.entity_id, RelationshipType.BELONGS_TO)
        )

        assert graph.delete_relationship(rel.relationship_id) is True
        assert graph.get_relationship(rel.relationship_id) is None

    def test_delete_nonexistent_relationship_returns_false(self, graph):
        assert graph.delete_relationship("bogus-id") is False

    def test_all_relationship_types_can_be_created(self, graph):
        src = graph.create_entity(make_entity(EntityType.TASK, "Src"))
        tgt = graph.create_entity(make_entity(EntityType.PROJECT, "Tgt"))
        for rtype in RelationshipType:
            rel = graph.create_relationship(new_relationship(src.entity_id, tgt.entity_id, rtype))
            assert rel.relationship_type == rtype


# ---------------------------------------------------------------------------
# Event operations
# ---------------------------------------------------------------------------


class TestEventOperations:
    def test_record_and_retrieve_event(self, graph):
        evt = new_event(
            GraphEventType.ENTITY_CREATED,
            entity_id="test-entity-id",
            payload={"name": "Test"},
        )
        recorded = graph.record_event(evt)
        assert recorded.event_id == evt.event_id

        events = graph.get_events(entity_id="test-entity-id")
        assert len(events) >= 1
        assert any(e.event_id == evt.event_id for e in events)

    def test_entity_creation_auto_records_event(self, graph):
        entity = graph.create_entity(make_entity(EntityType.PROJECT, "Audited"))
        events = graph.get_events(entity_id=entity.entity_id)
        types = [e.event_type for e in events]
        assert GraphEventType.ENTITY_CREATED in types

    def test_entity_update_auto_records_event(self, graph):
        entity = graph.create_entity(make_entity(EntityType.PROJECT, "Upd"))
        graph.update_entity(entity.entity_id, {"name": "Upd2"})
        events = graph.get_events(entity_id=entity.entity_id)
        types = [e.event_type for e in events]
        assert GraphEventType.ENTITY_UPDATED in types

    def test_entity_delete_auto_records_event(self, graph):
        entity = graph.create_entity(make_entity(EntityType.PROJECT, "Del"))
        graph.delete_entity(entity.entity_id)
        events = graph.get_events(entity_id=entity.entity_id)
        types = [e.event_type for e in events]
        assert GraphEventType.ENTITY_DELETED in types

    def test_get_events_by_type_filter(self, graph):
        entity = graph.create_entity(make_entity(EntityType.PROJECT, "Ev"))
        graph.update_entity(entity.entity_id, {"name": "Ev2"})
        events = graph.get_events(event_type=GraphEventType.ENTITY_UPDATED)
        for e in events:
            assert e.event_type == GraphEventType.ENTITY_UPDATED

    def test_get_events_with_limit(self, graph):
        entity = graph.create_entity(make_entity(EntityType.PROJECT, "LimitEv"))
        for _ in range(5):
            graph.update_entity(entity.entity_id, {"name": "X"})
        events = graph.get_events(entity_id=entity.entity_id, limit=2)
        assert len(events) <= 2


# ---------------------------------------------------------------------------
# Query operations
# ---------------------------------------------------------------------------


class TestGraphQueryOperations:
    def test_get_neighbors_outbound(self, graph):
        task = graph.create_entity(make_entity(EntityType.TASK, "Task"))
        proj = graph.create_entity(make_entity(EntityType.PROJECT, "Proj"))
        graph.create_relationship(
            new_relationship(task.entity_id, proj.entity_id, RelationshipType.BELONGS_TO)
        )

        result = graph.get_neighbors(task.entity_id, direction="outbound")
        names = [e.name for e in result.entities]
        assert "Proj" in names

    def test_get_neighbors_inbound(self, graph):
        task = graph.create_entity(make_entity(EntityType.TASK, "Task"))
        proj = graph.create_entity(make_entity(EntityType.PROJECT, "Proj"))
        graph.create_relationship(
            new_relationship(task.entity_id, proj.entity_id, RelationshipType.BELONGS_TO)
        )

        result = graph.get_neighbors(proj.entity_id, direction="inbound")
        names = [e.name for e in result.entities]
        assert "Task" in names

    def test_get_neighbors_with_relationship_type_filter(self, graph):
        task = graph.create_entity(make_entity(EntityType.TASK, "Task"))
        proj = graph.create_entity(make_entity(EntityType.PROJECT, "Proj"))
        doc = graph.create_entity(make_entity(EntityType.DOCUMENT, "Doc"))
        graph.create_relationship(
            new_relationship(task.entity_id, proj.entity_id, RelationshipType.BELONGS_TO)
        )
        graph.create_relationship(
            new_relationship(task.entity_id, doc.entity_id, RelationshipType.REFERENCES)
        )

        result = graph.get_neighbors(task.entity_id, relationship_type=RelationshipType.BELONGS_TO)
        names = [e.name for e in result.entities]
        assert "Proj" in names
        assert "Doc" not in names

    def test_find_path_direct(self, graph):
        src = graph.create_entity(make_entity(EntityType.TASK, "Src"))
        tgt = graph.create_entity(make_entity(EntityType.PROJECT, "Tgt"))
        graph.create_relationship(
            new_relationship(src.entity_id, tgt.entity_id, RelationshipType.BELONGS_TO)
        )

        result = graph.find_path(src.entity_id, tgt.entity_id)
        assert result.total_count > 0
        names = [e.name for e in result.entities]
        assert "Src" in names
        assert "Tgt" in names

    def test_find_path_same_entity(self, graph):
        entity = graph.create_entity(make_entity(EntityType.PROJECT, "Self"))
        result = graph.find_path(entity.entity_id, entity.entity_id)
        assert result.total_count >= 1

    def test_find_path_no_path_returns_empty(self, graph):
        src = graph.create_entity(make_entity(EntityType.TASK, "Isolated A"))
        tgt = graph.create_entity(make_entity(EntityType.PROJECT, "Isolated B"))
        result = graph.find_path(src.entity_id, tgt.entity_id)
        assert result.total_count == 0

    def test_search_by_name(self, graph):
        graph.create_entity(make_entity(EntityType.PROJECT, "Searchable Alpha"))
        graph.create_entity(make_entity(EntityType.TASK, "Searchable Beta"))
        graph.create_entity(make_entity(EntityType.DOCUMENT, "Invisible"))

        result = graph.search("Searchable")
        names = [e.name for e in result.entities]
        assert "Searchable Alpha" in names
        assert "Searchable Beta" in names
        assert "Invisible" not in names

    def test_get_project_subgraph(self, graph):
        proj = graph.create_entity(make_entity(EntityType.PROJECT, "MainProj"))
        task = graph.create_entity(make_entity(EntityType.TASK, "ProjTask"))
        doc = graph.create_entity(make_entity(EntityType.DOCUMENT, "ProjDoc"))
        graph.create_relationship(
            new_relationship(task.entity_id, proj.entity_id, RelationshipType.BELONGS_TO)
        )
        graph.create_relationship(
            new_relationship(proj.entity_id, doc.entity_id, RelationshipType.CONTAINS)
        )

        result = graph.get_project_subgraph(proj.entity_id)
        names = {e.name for e in result.entities}
        assert "MainProj" in names
        assert "ProjTask" in names
        assert "ProjDoc" in names

    def test_get_project_subgraph_nonexistent(self, graph):
        result = graph.get_project_subgraph("nonexistent-id")
        assert result.total_count == 0


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------


class TestGraphStats:
    def test_empty_graph_stats(self, graph):
        stats = graph.get_stats()
        assert isinstance(stats, GraphStats)
        assert stats.total_entities == 0
        assert stats.total_relationships == 0

    def test_stats_count_entities(self, graph):
        graph.create_entity(make_entity(EntityType.PROJECT, "A"))
        graph.create_entity(make_entity(EntityType.TASK, "B"))
        stats = graph.get_stats()
        assert stats.total_entities == 2
        assert stats.entity_counts.get("project", 0) == 1
        assert stats.entity_counts.get("task", 0) == 1

    def test_stats_count_relationships(self, graph):
        src = graph.create_entity(make_entity(EntityType.TASK, "T"))
        tgt = graph.create_entity(make_entity(EntityType.PROJECT, "P"))
        graph.create_relationship(
            new_relationship(src.entity_id, tgt.entity_id, RelationshipType.BELONGS_TO)
        )
        stats = graph.get_stats()
        assert stats.total_relationships == 1
        assert stats.relationship_counts.get("BELONGS_TO", 0) == 1


# ---------------------------------------------------------------------------
# Graph Query Engine
# ---------------------------------------------------------------------------


class TestGraphQueryEngine:
    def test_ensure_entity_creates_new(self, engine):
        entity = engine.ensure_entity(EntityType.PROJECT, "NewProject")
        assert entity.name == "NewProject"
        assert entity.entity_type == EntityType.PROJECT

    def test_ensure_entity_returns_existing(self, engine):
        e1 = engine.ensure_entity(EntityType.PROJECT, "SameProject")
        e2 = engine.ensure_entity(EntityType.PROJECT, "SameProject")
        assert e1.entity_id == e2.entity_id

    def test_ensure_relationship_creates_new(self, engine, graph):
        src = graph.create_entity(make_entity(EntityType.TASK, "T"))
        tgt = graph.create_entity(make_entity(EntityType.PROJECT, "P"))
        rel = engine.ensure_relationship(src.entity_id, tgt.entity_id, RelationshipType.BELONGS_TO)
        assert rel.source_id == src.entity_id
        assert rel.target_id == tgt.entity_id

    def test_ensure_relationship_deduplicates(self, engine, graph):
        src = graph.create_entity(make_entity(EntityType.TASK, "T"))
        tgt = graph.create_entity(make_entity(EntityType.PROJECT, "P"))
        rel1 = engine.ensure_relationship(src.entity_id, tgt.entity_id, RelationshipType.BELONGS_TO)
        rel2 = engine.ensure_relationship(src.entity_id, tgt.entity_id, RelationshipType.BELONGS_TO)
        assert rel1.relationship_id == rel2.relationship_id

    def test_link_task_to_project(self, engine):
        result = engine.link_task_to_project("My Task", "My Project")
        assert result["task"]["name"] == "My Task"
        assert result["project"]["name"] == "My Project"
        assert result["relationship"]["relationship_type"] == "BELONGS_TO"

    def test_link_document_to_project(self, engine):
        result = engine.link_document_to_project("Spec.md", "My Project")
        assert result["document"]["name"] == "Spec.md"
        assert result["relationship"]["relationship_type"] == "CONTAINS"

    def test_link_workflow_to_project(self, engine):
        result = engine.link_workflow_to_project("CI Pipeline", "My Project")
        assert result["workflow"]["name"] == "CI Pipeline"
        assert result["relationship"]["relationship_type"] == "SUPPORTS"

    def test_link_decision_to_project(self, engine):
        result = engine.link_decision_to_project("Use SQLite", "My Project")
        assert result["decision"]["name"] == "Use SQLite"
        assert result["relationship"]["relationship_type"] == "REFERENCES"

    def test_link_repository_to_project(self, engine):
        result = engine.link_repository_to_project("aios-repo", "My Project")
        assert result["repository"]["name"] == "aios-repo"
        assert result["relationship"]["relationship_type"] == "BELONGS_TO"

    def test_link_model_to_workflow(self, engine):
        result = engine.link_model_to_workflow("claude-3-5", "My Workflow")
        assert result["model"]["name"] == "claude-3-5"
        assert result["relationship"]["relationship_type"] == "USES"

    def test_get_entity_summary(self, engine):
        engine.link_task_to_project("T1", "P1")
        entities = engine._graph.find_entities(entity_type=EntityType.PROJECT, name_contains="P1")
        summary = engine.get_entity_summary(entities[0].entity_id)
        assert "entity" in summary
        assert "neighbors" in summary
        assert "recent_events" in summary

    def test_get_entity_summary_not_found(self, engine):
        result = engine.get_entity_summary("bad-id")
        assert "error" in result

    def test_get_project_overview(self, engine):
        engine.link_task_to_project("T1", "MyProject")
        engine.link_document_to_project("Doc1.md", "MyProject")
        result = engine.get_project_overview("MyProject")
        assert "project" in result
        assert result["project"]["name"] == "MyProject"
        assert result["subgraph"]["total_nodes"] > 0

    def test_get_project_overview_not_found(self, engine):
        result = engine.get_project_overview("Nonexistent Project XYZ")
        assert "error" in result

    def test_search_graph(self, engine):
        engine.ensure_entity(EntityType.PROJECT, "Findable Project")
        result = engine.search_graph("Findable")
        assert result["total"] >= 1
        assert any(e["name"] == "Findable Project" for e in result["entities"])

    def test_get_relations(self, engine):
        engine.link_task_to_project("T", "P")
        result = engine.get_relations("T", entity_type=EntityType.TASK)
        assert "entity" in result
        assert result["relationship_count"] >= 1

    def test_get_relations_not_found(self, engine):
        result = engine.get_relations("NoSuchEntityXYZ999")
        assert "error" in result

    def test_get_stats_summary(self, engine):
        engine.ensure_entity(EntityType.PROJECT, "SP")
        stats = engine.get_stats_summary()
        assert stats["total_entities"] >= 1

    def test_find_path_between_named_entities(self, engine):
        engine.link_task_to_project("PathTask", "PathProject")
        result = engine.find_path("PathTask", "PathProject")
        assert result.get("path_found") is True

    def test_find_path_source_not_found(self, engine):
        result = engine.find_path("NoSrcXYZ", "anything")
        assert "error" in result

    def test_find_path_target_not_found(self, engine):
        engine.ensure_entity(EntityType.PROJECT, "RealSrc")
        result = engine.find_path("RealSrc", "NoTgtXYZ")
        assert "error" in result


# ---------------------------------------------------------------------------
# Integration Hooks
# ---------------------------------------------------------------------------


class TestGraphIntegrationHooks:
    def test_on_task_created_registers_entity(self, hooks, graph):
        hooks.on_task_created("task-001", "Deploy Pipeline", project_name="Infra")
        tasks = graph.find_entities(entity_type=EntityType.TASK, name_contains="Deploy Pipeline")
        assert len(tasks) >= 1

    def test_on_task_created_links_to_project(self, hooks, graph):
        hooks.on_task_created("task-002", "Write Tests", project_name="Core OS")
        rels = graph.find_relationships(relationship_type=RelationshipType.BELONGS_TO)
        assert len(rels) >= 1

    def test_on_task_created_no_project(self, hooks, graph):
        hooks.on_task_created("task-003", "Standalone Task")
        tasks = graph.find_entities(entity_type=EntityType.TASK, name_contains="Standalone Task")
        assert len(tasks) >= 1

    def test_on_project_created_registers_entity(self, hooks, graph):
        hooks.on_project_created("New Product", repository_name="my-repo")
        projects = graph.find_entities(entity_type=EntityType.PROJECT, name_contains="New Product")
        assert len(projects) >= 1

    def test_on_project_created_links_repository(self, hooks, graph):
        hooks.on_project_created("Proj With Repo", repository_name="gh/repo")
        repos = graph.find_entities(entity_type=EntityType.REPOSITORY, name_contains="gh/repo")
        assert len(repos) >= 1

    def test_on_document_saved_registers_entity(self, hooks, graph):
        hooks.on_document_saved("Architecture.md", project_name="Core OS")
        docs = graph.find_entities(entity_type=EntityType.DOCUMENT, name_contains="Architecture.md")
        assert len(docs) >= 1

    def test_on_document_saved_with_notion_page_id(self, hooks, graph):
        hooks.on_document_saved("Notion Doc", notion_page_id="page-abc-123")
        docs = graph.find_entities(entity_type=EntityType.DOCUMENT, name_contains="Notion Doc")
        assert len(docs) >= 1
        pages = graph.find_entities(entity_type=EntityType.NOTION_PAGE, name_contains="Notion")
        assert len(pages) >= 1

    def test_on_workflow_deployed_registers_entity(self, hooks, graph):
        hooks.on_workflow_deployed("n8n-ci-workflow", project_name="DevOps")
        wfs = graph.find_entities(entity_type=EntityType.WORKFLOW, name_contains="n8n-ci-workflow")
        assert len(wfs) >= 1

    def test_on_workflow_deployed_links_model(self, hooks, graph):
        hooks.on_workflow_deployed("ML Pipeline", model_name="gpt-4o")
        models = graph.find_entities(entity_type=EntityType.MODEL, name_contains="gpt-4o")
        assert len(models) >= 1

    def test_on_decision_recorded_registers_entity(self, hooks, graph):
        hooks.on_decision_recorded(
            "Use Postgres", project_name="Backend", rationale="ACID compliance"
        )
        decisions = graph.find_entities(
            entity_type=EntityType.DECISION, name_contains="Use Postgres"
        )
        assert len(decisions) >= 1

    def test_on_memory_stored_registers_document(self, hooks, graph):
        hooks.on_memory_stored("Daily Review 2026-07", "Daily Review", project_name="Personal OS")
        docs = graph.find_entities(
            entity_type=EntityType.DOCUMENT, name_contains="Daily Review 2026-07"
        )
        assert len(docs) >= 1

    def test_on_research_completed_registers_entity(self, hooks, graph):
        hooks.on_research_completed("LLM Benchmarks", project_name="AI Research")
        research = graph.find_entities(
            entity_type=EntityType.RESEARCH, name_contains="LLM Benchmarks"
        )
        assert len(research) >= 1

    def test_hooks_gracefully_handle_failures(self, hooks):
        """Hooks must not raise even if internal graph fails."""
        with patch.object(hooks._engine, "ensure_entity", side_effect=RuntimeError("boom")):
            # Should not raise
            hooks.on_task_created("x", "y", project_name="z")


# ---------------------------------------------------------------------------
# Data model serialization
# ---------------------------------------------------------------------------


class TestDataModelSerialization:
    def test_entity_to_and_from_dict(self):
        entity = new_entity(EntityType.PROJECT, "Test", {"key": "value"})
        d = entity.to_dict()
        restored = GraphEntity.from_dict(d)
        assert restored.entity_id == entity.entity_id
        assert restored.entity_type == entity.entity_type
        assert restored.name == entity.name
        assert restored.properties == entity.properties

    def test_relationship_to_and_from_dict(self):
        rel = new_relationship("src-1", "tgt-1", RelationshipType.USES, {"weight": 1})
        d = rel.to_dict()
        restored = GraphRelationship.from_dict(d)
        assert restored.relationship_id == rel.relationship_id
        assert restored.relationship_type == rel.relationship_type
        assert restored.properties == rel.properties

    def test_event_to_and_from_dict(self):
        evt = new_event(GraphEventType.ENTITY_CREATED, entity_id="e1", payload={"name": "X"})
        d = evt.to_dict()
        restored = GraphEvent.from_dict(d)
        assert restored.event_id == evt.event_id
        assert restored.event_type == evt.event_type
        assert restored.payload == evt.payload

    def test_new_entity_generates_uuid(self):
        e1 = new_entity(EntityType.TASK, "T")
        e2 = new_entity(EntityType.TASK, "T")
        assert e1.entity_id != e2.entity_id

    def test_new_relationship_generates_uuid(self):
        r1 = new_relationship("a", "b", RelationshipType.BELONGS_TO)
        r2 = new_relationship("a", "b", RelationshipType.BELONGS_TO)
        assert r1.relationship_id != r2.relationship_id

    def test_new_event_generates_uuid(self):
        e1 = new_event(GraphEventType.ENTITY_CREATED)
        e2 = new_event(GraphEventType.ENTITY_CREATED)
        assert e1.event_id != e2.event_id


# ---------------------------------------------------------------------------
# Thread safety (basic)
# ---------------------------------------------------------------------------


class TestThreadSafety:
    def test_concurrent_entity_creation(self, graph):
        import threading

        results = []
        errors = []

        def create():
            try:
                e = graph.create_entity(new_entity(EntityType.TASK, f"T-{uuid.uuid4().hex[:6]}"))
                results.append(e.entity_id)
            except Exception as exc:
                errors.append(str(exc))

        threads = [threading.Thread(target=create) for _ in range(20)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 20

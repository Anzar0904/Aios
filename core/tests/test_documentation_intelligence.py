"""Phase 8: Documentation Intelligence — Production Test Suite.

Tests cover:
- Document Registry CRUD
- Documentation Engine auto README, Architecture, and API builders
- Search Engine queries matching titles/contents
- Decisions Log system registry
- Knowledge Graph bridging integration assertions
- CLI command dispatcher smoke runs
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from aios.services.documentation import DecisionRecord, DocStatus, DocType, DocumentRecord, new_id
from aios.services.documentation_impl import DocumentationServiceImpl

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_db(tmp_path):
    return str(tmp_path / "test_documentation.db")


@pytest.fixture
def eng(tmp_db):
    from aios.local import documentation_commands

    documentation_commands._DB_PATH = tmp_db
    svc = DocumentationServiceImpl(db_path=tmp_db)
    svc.initialize()
    svc.start()
    yield svc
    svc.shutdown()
    documentation_commands._DB_PATH = None


# ---------------------------------------------------------------------------
# Document Registry & Seeding
# ---------------------------------------------------------------------------


class TestDocumentRegistry:
    def test_register_and_get_document(self, eng):
        did = new_id()
        doc = DocumentRecord(
            document_id=did,
            title="Overview Doc",
            doc_type=DocType.README,
            content="This is overview.",
            project_id="aios",
            owner="admin",
            status=DocStatus.PUBLISHED,
        )
        eng.register_document(doc)
        fetched = eng.get_document(did)
        assert fetched is not None
        assert fetched.title == "Overview Doc"
        assert fetched.status == DocStatus.PUBLISHED
        assert fetched.version == 1

        # Check duplicate update increments version
        updated = eng.register_document(fetched)
        assert updated.version == 2

    def test_delete_document(self, eng):
        did = new_id()
        doc = DocumentRecord(
            document_id=did,
            title="To Delete",
            doc_type=DocType.README,
            content="Temp",
        )
        eng.register_document(doc)
        assert eng.get_document(did) is not None

        success = eng.delete_document(did)
        assert success is True
        assert eng.get_document(did) is None


# ---------------------------------------------------------------------------
# Documentation Engine Builders
# ---------------------------------------------------------------------------


class TestDocumentationBuilders:
    def test_generate_readme(self, eng):
        doc = eng.generate_readme("core")
        assert doc.doc_type == DocType.README
        assert "Project README: Core" in doc.content

    def test_generate_architecture_doc(self, eng):
        doc = eng.generate_architecture_doc("core")
        assert doc.doc_type == DocType.ARCHITECTURE
        assert "System Architecture: Core" in doc.content

    def test_generate_api_doc(self, eng):
        doc = eng.generate_api_doc("workflow")
        assert doc.doc_type == DocType.API_DOCS
        assert "API Documentation: workflow" in doc.content


# ---------------------------------------------------------------------------
# Decision Log Registry
# ---------------------------------------------------------------------------


class TestDecisionLogs:
    def test_record_and_list_decisions(self, eng):
        dec_id = new_id()
        dec = DecisionRecord(
            decision_id=dec_id,
            title="Use SQLite WAL Mode",
            category="architectural",
            status="accepted",
            context="High concurrency is needed.",
            consequences="Better throughput.",
        )
        eng.record_decision(dec)
        decisions = eng.list_decisions()
        assert len(decisions) >= 1
        assert decisions[0].title == "Use SQLite WAL Mode"
        assert decisions[0].category == "architectural"


# ---------------------------------------------------------------------------
# Search Engine
# ---------------------------------------------------------------------------


class TestSearchEngine:
    def test_search_by_keywords(self, eng):
        d1 = DocumentRecord(
            document_id=new_id(),
            title="Secrets Management",
            doc_type=DocType.DEV_GUIDE,
            content="Do not store keys in git.",
        )
        d2 = DocumentRecord(
            document_id=new_id(),
            title="Code Guidelines",
            doc_type=DocType.DEV_GUIDE,
            content="Keep classes short.",
        )
        eng.register_document(d1)
        eng.register_document(d2)

        # Query secrets
        res = eng.search_documents("Secrets")
        assert len(res) == 1
        assert res[0].title == "Secrets Management"

        # Query code
        res_code = eng.search_documents("Guidelines")
        assert len(res_code) == 1
        assert res_code[0].title == "Code Guidelines"


# ---------------------------------------------------------------------------
# Knowledge Graph Integration
# ---------------------------------------------------------------------------


class TestDocumentationGraphBridge:
    def test_sync_document_node(self):
        from aios.services.documentation_graph_bridge import DocumentationGraphBridge

        mock_engine = MagicMock()
        mock_entity = MagicMock()
        mock_entity.entity_id = "mock-doc-id"
        mock_engine.ensure_entity.return_value = mock_entity

        bridge = DocumentationGraphBridge(mock_engine)
        doc = DocumentRecord(
            document_id="doc-123",
            title="Developer Guide",
            doc_type=DocType.DEV_GUIDE,
            project_id="aios",
        )
        entity_id = bridge.sync_document(doc)
        assert entity_id == "mock-doc-id"
        assert mock_engine.ensure_relationship.call_count == 1

    def test_sync_decision(self):
        from aios.services.documentation_graph_bridge import DocumentationGraphBridge

        mock_engine = MagicMock()
        mock_entity = MagicMock()
        mock_entity.entity_id = "mock-dec-id"
        mock_engine.ensure_entity.return_value = mock_entity

        bridge = DocumentationGraphBridge(mock_engine)
        dec = DecisionRecord(
            "dec-123", "Use SQLite", "architectural", "accepted", "context", "conseq"
        )
        entity_id = bridge.sync_decision(dec)
        assert entity_id == "mock-dec-id"


# ---------------------------------------------------------------------------
# CLI Command Dispatcher Smoke Tests
# ---------------------------------------------------------------------------


class TestDocumentationCLIDispatch:
    def test_cli_dashboard_smoke(self, eng):
        from aios.local.documentation_commands import cmd_docs_dashboard

        cmd_docs_dashboard([])

    def test_cli_list_smoke(self, eng):
        from aios.local.documentation_commands import cmd_docs_list

        cmd_docs_list([])

    def test_cli_search_smoke(self, eng):
        from aios.local.documentation_commands import cmd_docs_search

        cmd_docs_search(["Secrets"])

    def test_cli_readme_smoke(self, eng):
        from aios.local.documentation_commands import cmd_docs_readme

        cmd_docs_readme(["core"])

    def test_cli_architecture_smoke(self, eng):
        from aios.local.documentation_commands import cmd_docs_architecture

        cmd_docs_architecture(["core"])

    def test_cli_api_smoke(self, eng):
        from aios.local.documentation_commands import cmd_docs_api

        cmd_docs_api(["workflow"])

    def test_cli_project_smoke(self, eng):
        from aios.local.documentation_commands import cmd_docs_project

        cmd_docs_project(["agency"])

    def test_cli_workflows_smoke(self, eng):
        from aios.local.documentation_commands import cmd_docs_workflows

        cmd_docs_workflows(["lead_gen"])

    def test_cli_integrations_smoke(self, eng):
        from aios.local.documentation_commands import cmd_docs_integrations

        cmd_docs_integrations(["github"])

    def test_cli_agency_smoke(self, eng):
        from aios.local.documentation_commands import cmd_docs_agency

        cmd_docs_agency(["abc_client"])

    def test_cli_changelog_smoke(self, eng):
        from aios.local.documentation_commands import cmd_docs_changelog

        cmd_docs_changelog([])

    def test_cli_release_smoke(self, eng):
        from aios.local.documentation_commands import cmd_docs_release

        cmd_docs_release([])

"""Phase 10: Research Intelligence — Production Test Suite.

Tests cover:
- Research Project Registry CRUD & default seeding
- Paper Ingestion & Document Intelligence parser
- Knowledge Synthesis Engine opportunities patterns contradictions
- Learning Summary Engine failed experiments lessons learned logs
- Knowledge Graph bridging integration assertions
- CLI command dispatcher smoke runs
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from aios.services.research import IngestedPaper, LearningSummary, ResearchProject, new_id
from aios.services.research_impl import LocalResearchService

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_db(tmp_path):
    return str(tmp_path)


@pytest.fixture
def eng(tmp_db):
    from aios.local import research_commands

    research_commands._DB_PATH = tmp_db
    mock_model = MagicMock()
    svc = LocalResearchService(model_service=mock_model, workspace_root=tmp_db)
    svc.initialize()
    svc.start()
    yield svc
    svc.shutdown()
    research_commands._DB_PATH = None


# ---------------------------------------------------------------------------
# Registry & CRUD
# ---------------------------------------------------------------------------


class TestResearchRegistry:
    def test_seeded_projects(self, eng):
        projects = eng.list_research_projects()
        assert len(projects) >= 1
        assert projects[0].title == "Agentic OS Architecture Research"

    def test_create_and_get_project(self, eng):
        rid = new_id()
        proj = ResearchProject(
            research_id=rid,
            title="NLP Model Boundaries",
            category="nlp",
            topic="Context window optimization",
        )
        eng.create_research_project(proj)
        fetched = eng.get_research_project(rid)
        assert fetched is not None
        assert fetched.title == "NLP Model Boundaries"


# ---------------------------------------------------------------------------
# Paper Ingestion & Ingestions Lists
# ---------------------------------------------------------------------------


class TestPaperIngestion:
    def test_ingest_and_list_papers(self, eng):
        projects = eng.list_research_projects()
        rid = projects[0].research_id

        paper = IngestedPaper(
            paper_id=new_id(),
            research_id=rid,
            title="Optimizing sonnet models",
            authors=["Anthropic Team"],
            summary="This study maps context tokens behavior.",
            findings=["Adan speeds up convergence by 2x"],
            citations=["ArXiv 2025"],
        )
        eng.ingest_paper(paper)
        papers = eng.list_papers(rid)
        assert len(papers) >= 1
        assert "Optimizing sonnet models" in [p.title for p in papers]


# ---------------------------------------------------------------------------
# Knowledge Synthesis Engine
# ---------------------------------------------------------------------------


class TestKnowledgeSynthesis:
    def test_knowledge_synthesis(self, eng):
        projects = eng.list_research_projects()
        rid = projects[0].research_id

        # Synthesis complete
        res = eng.synthesize_knowledge(rid)
        assert "patterns" in res
        assert "contradictions" in res
        assert "opportunities" in res
        assert len(res["opportunities"]) >= 1


# ---------------------------------------------------------------------------
# Learning Summaries & Lessons Learned
# ---------------------------------------------------------------------------


class TestLearningSummaries:
    def test_record_and_list_summaries(self, eng):
        projects = eng.list_research_projects()
        rid = projects[0].research_id

        summary = LearningSummary(
            summary_id=new_id(),
            research_id=rid,
            topics=["LLM Decays"],
            successful_findings=["Fixed memory leak"],
            failed_experiments=["Direct state update crash"],
            lessons_learned="Always clone objects.",
        )
        eng.record_learning_summary(summary)
        summaries = eng.list_learning_summaries(rid)
        assert len(summaries) >= 1
        assert summaries[0].lessons_learned == "Always clone objects."


# ---------------------------------------------------------------------------
# Knowledge Graph Integration
# ---------------------------------------------------------------------------


class TestResearchGraphBridge:
    def test_sync_research_project(self):
        from aios.services.research_graph_bridge import ResearchGraphBridge

        mock_engine = MagicMock()
        mock_entity = MagicMock()
        mock_entity.entity_id = "mock-res-id"
        mock_engine.ensure_entity.return_value = mock_entity

        bridge = ResearchGraphBridge(mock_engine)
        proj = ResearchProject("res-123", "Agentic OS", "agentic", "topic")
        entity_id = bridge.sync_research_project(proj)
        assert entity_id == "mock-res-id"

    def test_sync_ingested_paper(self):
        from aios.services.research_graph_bridge import ResearchGraphBridge

        mock_engine = MagicMock()
        bridge = ResearchGraphBridge(mock_engine)
        paper = IngestedPaper("paper-123", "res-123", "Generative Agents")
        bridge.sync_ingested_paper(paper, "Agentic OS")
        assert mock_engine.ensure_entity.call_count >= 2


# ---------------------------------------------------------------------------
# CLI Command Dispatcher Smoke Tests
# ---------------------------------------------------------------------------


class TestResearchCLIDispatch:
    def test_cli_dashboard_smoke(self, eng):
        from aios.local.research_commands import cmd_research_dashboard

        cmd_research_dashboard([])

    def test_cli_list_smoke(self, eng):
        from aios.local.research_commands import cmd_research_list

        cmd_research_list([])

    def test_cli_search_smoke(self, eng):
        from aios.local.research_commands import cmd_research_search

        cmd_research_search(["Agentic"])

    def test_cli_paper_smoke(self, eng):
        from aios.local.research_commands import cmd_research_paper

        cmd_research_paper(["Generative Agents"])

    def test_cli_synthesize_smoke(self, eng):
        from aios.local.research_commands import cmd_research_synthesize

        cmd_research_synthesize([])

    def test_cli_learn_smoke(self, eng):
        from aios.local.research_commands import cmd_research_learn

        cmd_research_learn([])

    def test_cli_report_smoke(self, eng):
        from aios.local.research_commands import cmd_research_report

        cmd_research_report([])

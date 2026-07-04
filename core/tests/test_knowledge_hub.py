import json
import time
from unittest.mock import MagicMock, patch
import pytest

from aios.config import NotionConfig
from aios.registry import ServiceRegistry
from aios.services.personal import PersonalService, PersonalProfile, KnowledgeEntry, Contact
from aios.services.knowledge_hub import (
    KnowledgeHubService,
    KnowledgeDocument,
    KnowledgeMetadata,
    KnowledgeSyncResult,
)
from aios.services.knowledge_hub_impl import LocalKnowledgeHub, NotionProvider
from aios.services.memory import MemoryType


@pytest.fixture
def mock_personal_service():
    service = MagicMock(spec=PersonalService)
    profile = PersonalProfile(
        id="profile_123",
        name="John Doe",
        contact=Contact(email="john@doe.com"),
        goals=[],
        knowledge=[]
    )
    service.get_active_profile.return_value = profile
    return service


def test_notion_provider_offline_mode():
    config = NotionConfig(offline_mode=True)
    provider = NotionProvider(config)

    assert provider.get_name() == "notion"
    assert provider.authenticate() is True
    assert len(provider.discover_databases()) == 1
    assert len(provider.discover_pages()) == 1
    assert len(provider.search("test")) == 1

    page = provider.read_page("mock_id")
    assert page.page_id == "mock_id"
    assert "Mocked" in page.content

    created = provider.create_page("parent", "title", "content")
    assert created.title == "title"
    assert created.content == "content"


@patch("urllib.request.urlopen")
def test_notion_provider_http_calls(mock_urlopen):
    # Mock authentication response (GET /users/me)
    mock_resp = MagicMock()
    mock_resp.status = 200
    mock_resp.read.return_value = json.dumps({"object": "user", "name": "AI OS Bot"}).encode("utf-8")

    mock_urlopen.return_value.__enter__.return_value = mock_resp

    config = NotionConfig(token="secret_token", offline_mode=False)
    provider = NotionProvider(config)

    assert provider.authenticate() is True

    # Mock page creation response (POST /pages)
    mock_create_resp = MagicMock()
    mock_create_resp.status = 200
    mock_create_resp.read.return_value = json.dumps({
        "id": "new_page_123",
        "url": "https://notion.so/new_page_123",
        "properties": {
            "title": {
                "title": [{"text": {"content": "Sample Doc"}}]
            }
        }
    }).encode("utf-8")
    mock_urlopen.return_value.__enter__.return_value = mock_create_resp

    created = provider.create_page("parent_123", "Sample Doc", "# Heading\nSome paragraph text")
    assert created.page_id == "new_page_123"
    assert created.title == "Sample Doc"


def test_knowledge_hub_sync_lifecycle(mock_personal_service):
    config = NotionConfig(offline_mode=True)
    hub = LocalKnowledgeHub(config, mock_personal_service)
    hub.initialize()

    # Create a document
    doc = KnowledgeDocument(
        document_id="doc_xyz",
        title="Sync Document Title",
        content="Document content line 1\n# Title Header",
        metadata=KnowledgeMetadata(
            unique_id="doc_xyz",
            timestamp=time.time(),
            source_subsystem="daily_os",
            category="Daily Review"
        )
    )

    # 1. Sync first time (should call create_page and return success)
    res1 = hub.sync_document(doc, "notion")
    assert res1.status == "success"
    assert res1.provider_page_id is not None

    # 2. Sync second time with identical content (should return skipped - duplicate detection!)
    res2 = hub.sync_document(doc, "notion")
    assert res2.status == "skipped"
    assert res2.provider_page_id == res1.provider_page_id

    # 3. Modify content and sync third time (should trigger update_page and return success)
    doc.content = "Modified content line 1\n# Title Header"
    res3 = hub.sync_document(doc, "notion")
    assert res3.status == "success"
    assert res3.provider_page_id == res1.provider_page_id


def test_subsystem_integrations_mocked(mock_personal_service):
    registry = ServiceRegistry()

    config = NotionConfig(offline_mode=True)
    hub = LocalKnowledgeHub(config, mock_personal_service)
    hub.initialize()
    registry.register(KnowledgeHubService, hub)

    # 1. Daily Review Integration
    from aios.services.daily import DailyReviewSummary
    from aios.services.daily_impl import LocalDailyReview
    model_mock = MagicMock()
    personal_mock = mock_personal_service

    daily_review = LocalDailyReview(
        model_mock,
        personal_mock,
        None,
        registry,
        MagicMock(),
        MagicMock()
    )
    summary = DailyReviewSummary(
        completed_tasks=["Task A"],
        incomplete_tasks=["Task B"],
        productivity_summary="Great day."
    )
    daily_review._persist_review(summary)

    assert len(hub._sync_registry) == 1

    # 2. Career OS Planner Integration
    from aios.services.career_impl import LocalCareerPlanner
    from aios.services.model import LLMResponse
    model_mock.execute_request.return_value = LLMResponse(
        content=json.dumps({
            "evaluated_goals": "Goals aligned",
            "missing_skills_analysis": "No gaps",
            "career_alternatives": [],
            "growth_milestones": ["Get certified"],
            "estimated_impact": 95
        }),
        model_name="mock-model",
        provider_name="mock-provider"
    )
    planner = LocalCareerPlanner(model_mock, personal_mock, registry)
    planner.generate_plan()

    assert len(hub._sync_registry) == 2

    # 3. Mission Engine Integration
    from aios.services.mission_impl import LocalMissionEngine
    from aios.services.mission import Mission, MissionMilestone, MissionStatus
    engine = LocalMissionEngine(MagicMock(), registry=registry)
    mission = Mission(
        mission_id="m_123",
        title="Scale databases",
        objective="scale DB",
        status=MissionStatus.PENDING,
        milestones=[]
    )
    engine._repository.save_mission(mission)

    with patch.object(engine._executor, 'execute_mission') as mock_exec:
        mock_exec.return_value = True
        engine.start_mission("m_123")

    assert len(hub._sync_registry) == 3

    # 4. Research Service Integration
    from aios.services.research_impl import LocalResearchService
    research_svc = LocalResearchService(model_mock, registry=registry)
    model_mock.execute_request.return_value = LLMResponse(
        content="Markdown research report content [1]",
        model_name="mock-model",
        provider_name="mock-provider"
    )
    research_svc.research("Explain event bus")

    assert len(hub._sync_registry) == 4

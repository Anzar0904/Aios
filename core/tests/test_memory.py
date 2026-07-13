from aios.services.context import ContextLoadedEvent, WorkspaceContext
from aios.services.event_bus_impl import LocalEventBus
from aios.services.memory import MemoryType
from aios.services.memory_impl import LocalMemoryService
from aios.services.memory_storage_impl import LocalJSONMemoryStorage
from aios.services.session import Session, SessionEndedEvent, SessionStartedEvent


def test_memory_storage_crud(tmp_path):
    storage_file = tmp_path / "test_memory.json"
    storage = LocalJSONMemoryStorage(storage_file)

    event_bus = LocalEventBus()
    event_bus.register_event_type(ContextLoadedEvent)
    event_bus.register_event_type(SessionStartedEvent)
    event_bus.register_event_type(SessionEndedEvent)

    service = LocalMemoryService(event_bus, storage=storage)
    service.initialize()

    # Set context manually via event
    context = WorkspaceContext(
        working_directory="/test/workspace",
        git_repo_path=None,
        git_branch=None,
        project_root="/test/workspace",
        project_name="test_proj",
    )
    event_bus.publish(ContextLoadedEvent(context=context))

    # Start session
    session = Session(
        session_id="session-456",
        workspace_id="/test/workspace",
        start_time=12345.0,
        runtime_state="active",
    )
    event_bus.publish(SessionStartedEvent(session_id="session-456", session=session))

    # Add memory
    mem1 = service.add_memory(
        content="This is a test note about Python 3.12",
        memory_type=MemoryType.NOTE,
        tags=["python", "test"],
        importance=3,
        metadata_additional={"topic": "coding"},
    )

    assert mem1.memory_id is not None
    assert mem1.content == "This is a test note about Python 3.12"
    assert mem1.memory_type == MemoryType.NOTE
    assert mem1.metadata.workspace_id == "/test/workspace"
    assert mem1.metadata.session_id == "session-456"
    assert mem1.metadata.tags == ["python", "test"]
    assert mem1.metadata.importance == 3
    assert mem1.metadata.additional == {"topic": "coding"}

    # Get memory
    retrieved = service.get_memory(mem1.memory_id)
    assert retrieved == mem1

    # Search memory
    results = service.search_memory(query="Python")
    assert len(results) == 1
    assert results[0] == mem1

    results_empty = service.search_memory(query="JavaScript")
    assert len(results_empty) == 0

    # Search by tags
    results_tags = service.search_memory(query="Python", tags=["python"])
    assert len(results_tags) == 1

    results_tags_mismatch = service.search_memory(query="Python", tags=["golang"])
    assert len(results_tags_mismatch) == 0

    # Update memory
    updated = service.update_memory(
        memory_id=mem1.memory_id, content="Updated test note", importance=5
    )
    assert updated.content == "Updated test note"
    assert updated.metadata.importance == 5
    assert updated.updated_at >= mem1.created_at

    # End session to commit
    event_bus.publish(SessionEndedEvent(session_id="session-456", session=session))

    # Verify file is written
    assert storage_file.exists()

    # Start a new session on same workspace to verify restore
    new_storage = LocalJSONMemoryStorage(storage_file)
    new_service = LocalMemoryService(event_bus, storage=new_storage)
    new_service.initialize()

    event_bus.publish(ContextLoadedEvent(context=context))

    new_session = Session(
        session_id="session-789",
        workspace_id="/test/workspace",
        start_time=12350.0,
        runtime_state="active",
    )
    event_bus.publish(SessionStartedEvent(session_id="session-789", session=new_session))

    # The memory should have been restored
    restored = new_service.get_memory(mem1.memory_id)
    assert restored is not None
    assert restored.content == "Updated test note"
    assert restored.metadata.importance == 5

    # Delete memory
    new_service.delete_memory(mem1.memory_id)
    assert new_service.get_memory(mem1.memory_id) is None


def test_memory_intelligence_milestone1(tmp_path):
    import json
    from unittest.mock import MagicMock

    from aios.services.memory import MemoryCategory, MemoryImportance
    from aios.services.model import LLMResponse, ModelService

    storage_file = tmp_path / "test_memory_intelligence.json"
    storage = LocalJSONMemoryStorage(storage_file)

    event_bus = LocalEventBus()
    event_bus.register_event_type(ContextLoadedEvent)
    event_bus.register_event_type(SessionStartedEvent)
    event_bus.register_event_type(SessionEndedEvent)

    service = LocalMemoryService(event_bus, storage=storage)
    service.initialize()

    mock_model = MagicMock(spec=ModelService)
    mock_model.execute_request.return_value = LLMResponse(
        content=json.dumps({
            "category": "Daily Review",
            "importance_score": "High",
            "tags": ["productivity", "review"],
            "related_mission": "m_123",
            "related_project": "p_456",
            "related_company": "Google",
            "related_technologies": ["Python", "Rust"],
            "related_skills": ["Coding", "System Design"],
            "related_files": ["main.py"]
        }),
        model_name="mock-model",
        provider_name="mock-provider",
    )
    service.set_model_service(mock_model)

    context = WorkspaceContext(
        working_directory="/test/workspace",
        git_repo_path=None,
        git_branch=None,
        project_root="/test/workspace",
        project_name="test_proj",
    )
    event_bus.publish(ContextLoadedEvent(context=context))

    session = Session(
        session_id="session-456",
        workspace_id="/test/workspace",
        start_time=12345.0,
        runtime_state="active",
    )
    event_bus.publish(SessionStartedEvent(session_id="session-456", session=session))

    mem = service.add_memory(
        content="Daily review: completed SWE milestones for Career OS.",
        memory_type=MemoryType.NOTE,
    )

    assert mem.metadata.category == MemoryCategory.DAILY_REVIEW
    assert mem.metadata.importance_score == MemoryImportance.HIGH
    assert "productivity" in mem.metadata.tags
    assert mem.metadata.related_mission == "m_123"
    assert mem.metadata.related_project == "p_456"
    assert mem.metadata.related_company == "Google"
    assert "Python" in mem.metadata.related_technologies
    assert "main.py" in mem.metadata.related_files

    # Test indexing lookup
    indexer = service.indexer

    # 1. Lookup by category
    results_cat = indexer.lookup(category=MemoryCategory.DAILY_REVIEW)
    assert len(results_cat) == 1
    assert results_cat[0] == mem

    # 2. Lookup by tags
    results_tags = indexer.lookup(tags=["productivity"])
    assert len(results_tags) == 1

    # 3. Lookup by mission
    results_miss = indexer.lookup(mission="m_123")
    assert len(results_miss) == 1

    # 4. Lookup by project
    results_proj = indexer.lookup(project="p_456")
    assert len(results_proj) == 1

    # 5. Lookup by company
    results_comp = indexer.lookup(company="Google")
    assert len(results_comp) == 1

    # 6. Lookup by technology
    results_tech = indexer.lookup(technology="Python")
    assert len(results_tech) == 1

    # 7. Lookup by date range
    results_date = indexer.lookup(start_date=mem.metadata.timestamp - 10, end_date=mem.metadata.timestamp + 10)
    assert len(results_date) == 1


def test_backward_compatibility():
    from aios.services.memory import MemoryMetadata
    meta = MemoryMetadata(
        workspace_id="/test/workspace",
        session_id="session-123"
    )
    assert meta.workspace_id == "/test/workspace"
    assert meta.session_id == "session-123"
    assert meta.category is None
    assert meta.importance_score is None
    assert len(meta.related_technologies) == 0


def test_memory_retrieval_milestone2(tmp_path):
    from aios.services.memory import (
        MemoryCategory,
        MemoryImportance,
        RetrievalContext,
        RetrievalStrategy,
    )

    storage_file = tmp_path / "test_memory_retrieval.json"
    storage = LocalJSONMemoryStorage(storage_file)

    event_bus = LocalEventBus()
    event_bus.register_event_type(ContextLoadedEvent)
    event_bus.register_event_type(SessionStartedEvent)
    event_bus.register_event_type(SessionEndedEvent)

    service = LocalMemoryService(event_bus, storage=storage)
    service.initialize()

    context = WorkspaceContext(
        working_directory="/test/workspace",
        git_repo_path=None,
        git_branch=None,
        project_root="/test/workspace",
        project_name="test_proj",
    )
    event_bus.publish(ContextLoadedEvent(context=context))

    session = Session(
        session_id="session-456",
        workspace_id="/test/workspace",
        start_time=12345.0,
        runtime_state="active",
    )
    event_bus.publish(SessionStartedEvent(session_id="session-456", session=session))

    # Add various memories
    mem_mission = service.add_memory(content="Mission: scale databases to 10k QPS", memory_type=MemoryType.NOTE)
    mem_mission.metadata.category = MemoryCategory.MISSION
    mem_mission.metadata.importance_score = MemoryImportance.HIGH
    mem_mission.metadata.related_mission = "m_scale"

    mem_career = service.add_memory(content="Resume version for SWE application to Google", memory_type=MemoryType.NOTE)
    mem_career.metadata.category = MemoryCategory.CAREER
    mem_career.metadata.importance_score = MemoryImportance.LOW
    mem_career.metadata.related_company = "Google"

    mem_project = service.add_memory(content="ADR: use SQLite for local caching in AI OS", memory_type=MemoryType.NOTE)
    mem_project.metadata.category = MemoryCategory.PROJECT
    mem_project.metadata.importance_score = MemoryImportance.CRITICAL
    mem_project.metadata.related_project = "ai_os_core"

    # Verify retriever
    retriever = service.retriever

    # 1. Retrieve by Mission
    ctx_mission = RetrievalContext(
        objective="Analyze db scale progress",
        active_mission="m_scale",
        strategy=RetrievalStrategy.MISSION
    )
    res_mission = retriever.retrieve(ctx_mission)
    assert len(res_mission) == 1
    assert res_mission[0].metadata.related_mission == "m_scale"

    # 2. Retrieve by Career (Google query)
    ctx_career = RetrievalContext(
        objective="Prepare Google interview application",
        strategy=RetrievalStrategy.CAREER
    )
    res_career = retriever.retrieve(ctx_career)
    assert len(res_career) == 1
    assert res_career[0].metadata.related_company == "Google"

    # 3. Retrieve by Project
    ctx_project = RetrievalContext(
        objective="Review caching architecture",
        active_project="ai_os_core",
        strategy=RetrievalStrategy.PROJECT
    )
    res_project = retriever.retrieve(ctx_project)
    assert len(res_project) == 1
    assert res_project[0].metadata.related_project == "ai_os_core"

    # 4. Relevance Ordering (Critical first)
    ctx_mixed = RetrievalContext(
        objective="Daily planning overview",
        strategy=RetrievalStrategy.MIXED,
        max_results=5
    )
    res_mixed = retriever.retrieve(ctx_mixed)
    assert res_mixed[0].metadata.importance_score == MemoryImportance.CRITICAL

    # 5. Byte limit constraints (Limit to 50 bytes)
    ctx_limit = RetrievalContext(
        objective="Planning overview",
        strategy=RetrievalStrategy.MIXED,
        limit_bytes=50
    )
    res_limit = retriever.retrieve(ctx_limit)
    assert len(res_limit) == 1
    assert res_limit[0].metadata.importance_score == MemoryImportance.CRITICAL

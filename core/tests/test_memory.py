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

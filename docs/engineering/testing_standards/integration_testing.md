# Integration Testing Standards
**Engineering Bible — Milestone 4**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. Scope of Integration Tests

Integration tests in the Personal AI OS verify communication pathways and state transfers between multiple registered service modules. These tests ensure that components function correctly when integrated, without invoking remote networks or third-party APIs.

---

## 2. Event Bus Integration Verification

Since the system relies heavily on an event-driven design, integration tests must verify that events publish correctly and trigger the corresponding subscriber handlers.

### Event Integration Guidelines
* **No Inter-Test Leaks**: Every integration test must instantiate an isolated event bus using pytest fixtures to prevent event leakage across tests.
* **Callback Verification**: Verify that publishing a specific event (e.g. `ToolStartedEvent`) triggers execution in other registered systems (like `MemoryService`).
* **Isolation of Async Actions**: If handlers invoke async actions, use pytest async plugins (`pytest-asyncio`) to ensure callbacks complete before assertions are evaluated.

```python
def test_event_bus_memory_integration(mock_event_bus, local_memory_service):
    # Register subscribers on the isolated bus
    mock_event_bus.register_event_type(SessionStartedEvent)
    mock_event_bus.subscribe(SessionStartedEvent, local_memory_service.on_session_started)
    
    # Publish event
    mock_event_bus.publish(SessionStartedEvent(session_id="session-123"))
    
    # Assert side effects are registered inside MemoryService
    assert local_memory_service.get_active_session_id() == "session-123"
```

---

## 3. Database & File Persistence Isolation

Integration tests that write database records or write files to disk must run in isolation to prevent polluting the active workspace.

### Persistence Rules
* **Use the `tmp_path` Fixture**: Always use pytest's built-in `tmp_path` fixture to generate isolated temporary directories. Never hardcode absolute paths or write to standard workspace paths.
* **Auto-Cleanup**: Temporary directories are automatically deleted by the pytest framework after execution.
* **Verification of File Schemas**: Tests must verify that files written by services (e.g., chat logs or task logs) exist in the temporary folder and conform to the correct JSON/Relational schema rules.

```python
def test_session_records_flush_to_disk(tmp_path):
    # Setup service using temporary path as workspace
    session_service = LocalSessionService(workspace_root=str(tmp_path))
    session_service.start_session(str(tmp_path))
    
    session_service.append_message(role="user", content="hello")
    session_service.end_session()
    
    # Assert files exist inside the tmp_path folder
    session_file = tmp_path / ".aios_conversations" / f"{session_service.active_id}.json"
    assert session_file.exists()
```

---

## 4. Multi-Service Bootstrap Verification

To prevent dependency errors at boot, tests must verify that services construct and wire correctly through the `bootstrap_kernel` composition root.
* **Boot Integration Test**: Tests must verify that invoking `bootstrap_kernel` returns a Kernel instance with its service registry fully populated.
* **Teardown Verifications**: Verify that calling `kernel.shutdown()` triggers teardown lifecycle stages across all registered service instances.

---

*Engineering Bible Testing Standards · Personal AI OS · Sprint 8 M4 · Governed by [06_TESTING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/06_TESTING_GUIDELINES.md)*

# Unit Testing Standards
**Engineering Bible — Milestone 4**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. Unit Test Boundaries & Isolation

Unit tests in the Personal AI OS must focus exclusively on verifying a single component or utility function.

### Isolation Rules
* **No File System Access**: Writing, editing, or deleting files on the host system during a unit test is prohibited. Use memory buffers (`io.StringIO`) or mocks if filesystem operations must be tested.
* **No Subprocesses**: Invoking external processes, commands (`shlex` execution paths), or terminal tools is prohibited.
* **No Network Calls**: Socket binds, HTTP requests, or external API calls are prohibited. Any service containing these operations must be isolated behind mock interfaces.

---

## 2. Constructor dependency mocking

To ensure unit tests run quickly and remain isolated, any dependency passed to a class constructor must be mocked using `unittest.mock.MagicMock`.

```python
# Unit testing a service by mocking its dependencies
from unittest.mock import MagicMock
from aios.services.event_bus import EventBusService
from aios.services.session_impl import LocalSessionService

def test_session_starts_and_publishes_event():
    # 1. Arrange: Create mock dependency
    mock_event_bus = MagicMock(spec=EventBusService)
    
    # 2. Act: Inject mock through constructor
    session_service = LocalSessionService(event_bus=mock_event_bus)
    session_service.initialize()
    session_service.start_session(workspace_path="/mock/workspace")
    
    # 3. Assert: Verify method invocation and params
    mock_event_bus.publish.assert_called_once()
```

---

## 3. Pytest Standards

* **Exception Verification**: Use `pytest.raises` to verify that input validation errors trigger the correct exceptions (e.g. validating path traversals).
  
  ```python
  import pytest
  from aios.services.security import validate_workspace_path
  
  def test_path_traversal_throws_permission_error():
      with pytest.raises(PermissionError):
          validate_workspace_path(path="../../etc/passwd", root="/workspace")
  ```

* **Parameterized Testing**: Use `@pytest.mark.parametrize` to run tests against a range of inputs and expected outcomes without duplicating code.

  ```python
  @pytest.mark.parametrize(
      "input_cmd, expected_tokens",
      [
          ("git status", ["git", "status"]),
          ("echo 'hello world'", ["echo", "hello world"]),
      ]
  )
  def test_command_tokenization(input_cmd, expected_tokens):
      assert tokenize_command(input_cmd) == expected_tokens
  ```

---

*Engineering Bible Testing Standards · Personal AI OS · Sprint 8 M4 · Governed by [06_TESTING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/06_TESTING_GUIDELINES.md)*

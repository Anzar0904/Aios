# Mocking Guidelines & Test Isolation
**Engineering Bible — Milestone 4**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. The Philosophy of Mocking

We use mocks to isolate the code being tested from external systems (like databases, file systems, or remote APIs).

### Core Mocking Rules
* **Only Mock Adjacent Dependencies**: Mock only the components that interface directly with the class under test. Do not mock internal helper classes of the component being tested.
* **Never Mock the System Under Test (SUT)**: The class, utility, or function being tested must run as concrete code. Never mock methods on the SUT itself.
* **Prefer Constructor Mocking**: Always prefer injecting mock dependencies through class constructors over using dynamic runtime patches (`unittest.mock.patch`).

---

## 2. Using `unittest.mock` Safely

* **Use `spec` Verification**: Always create mocks with the `spec` parameter set to the interface class (e.g. `mock_bus = MagicMock(spec=EventBusService)`). This ensures the mock will throw an error if the test attempts to call a method that does not exist on the target interface.
* **Control Runtime Patch Scopes**: When using `unittest.mock.patch` for system operations (like patching `sys.stdout` or environment variables), use context managers or pytest fixtures to ensure the patch is uninstalled when the test finishes.

```python
from unittest.mock import patch

def test_system_variable_handling():
    # Patch scope is strictly confined to the with block
    with patch.dict("os.environ", {"OFFLINE_MODE": "True"}):
        assert is_system_offline() is True
```

---

## 3. Mocking External Interfaces

### Mocking LLM Providers & Remote API Clients
Since unit tests cannot access the network, all model queries must be simulated.
* **Structured Mock Responses**: Use mocks that return complete `LLMResponse` structures, including mock metadata (token usage, provider name, etc.).
* **Failing Scenarios**: Tests must verify error handling by mocking connections that raise exceptions or timeout errors.

```python
# Simulating a model provider response
from unittest.mock import MagicMock
from aios.services.model import LLMResponse

def test_model_selector_parses_response():
    mock_client = MagicMock()
    mock_client.generate.return_value = LLMResponse(
        content="Parsed response text",
        model_name="llama3",
        provider_name="ollama",
        usage={"input_tokens": 10, "output_tokens": 15}
    )
```

### Mocking Command Subprocesses
* **No Raw Shell Executions**: Running shell commands during testing is prohibited.
* **Subprocess Mocking**: Use mocks to intercept subprocess calls and verify the arguments passed to them.

```python
# Intercepting subprocess executions safely
from unittest.mock import patch, MagicMock

@patch("subprocess.run")
def test_git_status_tool_execution(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout=b"On branch main")
    
    result = run_git_status()
    
    assert "On branch main" in result
    mock_run.assert_called_once_with(["git", "status"], shell=False, capture_output=True)
```

---

## 4. Common Mocking Pitfalls to Avoid

* **Mocking Python Builtins**: Avoid patching built-in functions (like `open`, `print`, or `len`) unless absolutely necessary. Use pytest's `tmp_path` fixture or memory-based streams instead.
* **Forgotten Call Assertions**: Mock assertions (like `mock.assert_called_once()`) are sometimes written incorrectly (e.g., misspelled as `assert_called_once_with`). Use proper mock validation methods to ensure assertions run.
* **Over-Mocking**: If a test mocks most of the system, it ceases to verify actual code execution. Keep mocks focused on boundary components.

---

*Engineering Bible Testing Standards · Personal AI OS · Sprint 8 M4 · Governed by [06_TESTING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/06_TESTING_GUIDELINES.md)*

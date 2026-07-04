# 06 — Testing Guidelines
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## Document Metadata
* **Purpose**: Define the testing strategy, test pyramid, pytest configurations, mock boundaries, security/performance validation runs, and manual release checklists for the Personal AI OS.
* **Scope**: Applies to all unit, integration, and end-to-end tests inside the `core/tests/` folder and skill packages.
* **Audience**: Quality Engineers, Systems Developers, and AI Testing Agents.
* **Related Documents**:
  * [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) - Constitutional performance and reliability guidelines.
  * [01_ENGINEERING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) - Refactoring workflows and Definition of Done.
  * [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md) - Core service boundaries and event pipelines.
  * [03_IMPLEMENTATION_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/03_IMPLEMENTATION_GUIDELINES.md) - Code reviews and verification checklists.
  * [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md) - Path validation checks and Whitelist command validation.
* **Future Extensions**: Integration details for recording/replaying LLM interactions (VCR-style mocking) and dockerized integration pools as deployment pipelines scale.

---

## 1. Testing Philosophy

The Personal AI OS testing philosophy is grounded in **Contract-First Reliability**. Because the system is designed to run unattended, writing high-quality tests is the primary mechanism to protect against regressions introduced by AI code generators or refactoring edits.

Our testing guidelines are based on three core rules:
1. **Test the Contract, Not the Internals**: Assert against public service interfaces (e.g., event publishes, command return structures) rather than private helper methods. Tests must survive code refactoring that preserves behavior.
2. **Deterministic & Fast**: Tests must run locally with zero network dependencies. The entire test suite must execute in under **5 seconds** to prevent friction during development.
3. **No Suppressed Failures**: Skipping broken tests or manually disabling assertions to make a build pass is strictly prohibited. If a test fails, either the code has a regression or the requirement has changed—both require a code change, not a mock bypass.

---

## 2. The Test Pyramid

To maintain execution speed while verifying system integrity, the test suite is structured around a classic pyramid:

```
                  +------------------------------------------+
                  |               TEST PYRAMID               |
                  +---------------------+--------------------+
                                        |
                                      /   \
                                    /  E2E  \  <-- E.g. REPL loop queries with stdin.
                                  /   (~5%)   \      Verifies renderer output.
                                /               \
                              /   Integration     \  <-- E.g. Event Bus routing, memory tiering,
                            /       (~25%)          \      and provider selectors.
                          /                           \
                        /             Unit              \  <-- E.g. path validations, shlex splits,
                      /              (~70%)               \      command registrees, and dataclasses.
                    +---------------------------------------+
```

* **Unit Tests (~70%)**: Verify isolated utilities and services (e.g., [test_event_bus.py](file:///Users/anzarakhtar/aios/core/tests/test_event_bus.py), `test_context.py`). They mock all external factors (file systems, HTTP, network sockets) and execute instantly.
* **Integration Tests (~25%)**: Verify boundary zones where multiple services interact (e.g., [test_providers.py](file:///Users/anzarakhtar/aios/core/tests/test_providers.py) routing, `test_session.py` flushing caches, `test_brain.py` planning).
* **End-to-End (E2E) Tests (~5%)**: Verify execution loops by piping inputs into `cli.py` and asserting outcomes against terminal stdout prints or file status updates.

---

## 3. Testing Standards

### 3.1 Unit Testing Standards
* **Isolation**: Use `unittest.mock` to mock all dependency classes passed to constructor arguments.
* **Exceptions Checks**: Verify that input validation errors trigger the correct exceptions (e.g., utilizing `pytest.raises` for checking `PermissionError` during path traversals).
* **Coverage Target**: Touch files must maintain at least **85%** unit test coverage.

### 3.2 Integration Testing Standards
* **Event Dispatching**: Assert that events published to the `LocalEventBus` are successfully handled by registered service subscribers.
* **Persistence Validation**: Tests that write JSON records (like conversations or task logs) must use temporary folders (`tmp_path` fixture) and verify that files exist on disk with the correct JSON schema properties.

### 3.3 E2E Testing Standards
* **CLI Mocking**: Use Python's built-in stdout/stdin redirection mechanics to simulate user inputs (e.g., typing `session start`) and verify visual rendering outputs.
* **State Verification**: Confirm that session exits successfully trigger teardown hooks and clean up temporary execution states.

---

## 4. Special Core Testing Strategies

### 4.1 AI Provider & Selector Tests
* **Mock Provider Factories**: Tests must verify provider selection logic without making real HTTP calls. Use `MagicMock` to simulate provider endpoints returning structured `LLMResponse` objects or raising connection timeouts.
* **Routing Assertions**: Assert that `ProviderRouter` handles provider failures by updating the selector health statistics and falling back to the next model in the chain.

### 4.2 Brain & Command Tests
* **Objective Planning**: Mock LLM prompt generations and verify that the Brain Planner successfully parses step strings into structured execution logs.
* **Command Registry Verification**: Verify that custom skill commands register, resolve arguments, and log outputs during mock execution runs.

### 4.3 Security & Path Validation Tests
* **Path Containment checks**: Assert that the path validation helper `validate_workspace_path` permits canonical paths inside the active workspace root and throws exceptions for absolute path segments escaping the workspace (e.g., `../../etc/hosts`).
* **Command Injection checks**: Assert that terminal tools reject metacharacters (e.g., `;`, `&`, `|`) and block commands that are not in the whitelist.

### 4.4 Performance Benchmarks
* **Registry Bootstrap Latency**: Tests verifying that Kernel initialization and service registry lookups execute under **200ms**.
* **Token Count Tracking**: Assert that prompt compaction loops successfully truncate and summarize dialogue history when messages exceed 10 turns.

---

## 5. Mocking Strategy & Test Fixtures

### 5.1 Pytest Fixtures
All database operations, file writes, and network calls must be mocked or isolated using pytest fixtures:
* `tmp_path`: Python's built-in fixture to generate isolated temporary directories. Never hardcode absolute paths or write to host folders in tests.
* `mock_event_bus`: A clean, isolated instance of the local event bus to prevent event leaks between tests.
* `mock_model_service`: A mock service return container configured to return predictable code structures for testing planner parsing loops.

### 5.2 Mocking Example (Provider Failover)
* *Implementation Reference* (from [test_providers.py](file:///Users/anzarakhtar/aios/core/tests/test_providers.py)):
  ```python
  from unittest.mock import MagicMock
  from aios.providers import ProviderRouter, ProviderRegistry, ProviderHealthMonitor, ProviderMetricsCollector
  from aios.services.model import LLMRequest, LLMResponse, ProviderFactory

  def test_provider_fallback_execution():
      factory = ProviderFactory()
      
      # Mock a failing provider (e.g. OpenAI returning errors)
      failing_provider = MagicMock()
      failing_provider.name = "openai"
      failing_provider.generate.side_effect = Exception("OpenAI endpoint timeout")
      
      # Mock a succeeding local provider
      local_provider = MagicMock()
      local_provider.name = "ollama"
      local_provider.generate.return_value = LLMResponse(
          content="local response", model_name="llama3", provider_name="ollama", usage={}
      )
      
      factory.register_provider(failing_provider)
      factory.register_provider(local_provider)
      
      router = ProviderRouter(ProviderConfig(fallback_chain=["openai", "ollama"]), ProviderRegistry(), ProviderHealthMonitor(), ProviderMetricsCollector(), factory)
      response = router.route_request(LLMRequest(prompt="hello", model_name="gpt-4o"))
      
      assert response.provider_name == "ollama"
      assert response.content == "local response"
  ```

---

## 6. Manual Verification & Release Checklists

Before releasing a new milestone, the developer must perform these verification tasks:

### 6.1 Pre-Release Manual Checklist
- [ ] **Linter Run**: Verify that `ruff check ./core` and `ruff format --check ./core` execute successfully with zero styling failures.
- [ ] **Test Coverage Audit**: Run `PYTHONPATH=. pytest --cov=core` to verify that coverage on modified lines remains above **85%**.
- [ ] **Secrets Audit**: Run a git search query to confirm no API tokens or config settings are stored in unstaged files or history logs.
- [ ] **Interactive REPL Check**: Start the system locally with `aios`. Run basic commands (`session start`, `task run`, `git status`) and verify that outputs format correctly without crashes.
- [ ] **Changelog Validation**: Verify that the version is bumped according to SemVer rules and details are logged in plain language.

---

## 7. Common Testing Mistakes to Avoid
* **漏 Mocking Network Connections**: Forgetting to mock LLM provider endpoints, causing tests to run slowly or fail when offline.
* **Leakage of Database Files**: Writing SQLite entries or JSON conversation logs to the active project root directory instead of using the `tmp_path` fixture.
* **Coupling Tests to Implementations**: Asserting against private variables, leading to test failures during refactoring steps.
* **Bypassing Whitelist Guards**: Writing test cases that bypass command validations, which hides security path issues.
* **Skipping Failure Scenarios**: Writing only success path tests while omitting error validations.

---

## 8. Future Testing Roadmap
* **VCR Prompt Recording**: Deploying recording libraries to record actual remote model inputs and response outputs as local yaml files, enabling mock replays.
* **Property-Based Security Auditing**: Writing randomized input fuzzing tests (e.g., using Hypothesis) to verify path validations and terminal input parsing loops against novel prompt injections.
* **Automated CI Checks Integration**: Configuring pre-commit hooks to automate ruff formatting and pytest executions locally on every git commit.

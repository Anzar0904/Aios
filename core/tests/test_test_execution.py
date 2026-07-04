import os
import pytest
from unittest.mock import MagicMock, patch
import subprocess

from aios.services.memory import MemoryService
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.test_execution import (
    ExecutionTarget,
    ExecutionSession,
)
from aios.services.test_execution_impl import (
    PytestAdapter,
    LocalTestRunner,
    LocalTestExecutor,
    LocalTestExecutionService,
)


def test_pytest_adapter_validation(tmp_path):
    # Verify non-existent workspace gracefully returns failed result
    adapter = PytestAdapter()
    target = ExecutionTarget("t1", "core/tests/test_memory.py")
    res = adapter.execute_tests("/nonexistent/workspace", [target])
    assert not res.success
    assert "does not exist" in res.errors[0]


@patch("subprocess.run")
def test_pytest_adapter_successful_execution(mock_run, tmp_path):
    # Mock subprocess run response
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = "============================= 3 passed, 1 skipped in 0.52s =============================\n"
    mock_proc.stderr = ""
    mock_run.return_value = mock_proc

    adapter = PytestAdapter()
    target = ExecutionTarget("t1", "core/tests/test_memory.py")
    res = adapter.execute_tests(str(tmp_path), [target])
    
    assert res.success
    assert res.exit_code == 0
    assert res.metrics.passed_tests == 3
    assert res.metrics.skipped_tests == 1
    assert res.metrics.failed_tests == 0


@patch("subprocess.run")
def test_pytest_adapter_timeout(mock_run, tmp_path):
    mock_run.side_effect = subprocess.TimeoutExpired(["pytest"], 30.0)

    adapter = PytestAdapter()
    target = ExecutionTarget("t1", "core/tests/test_memory.py")
    res = adapter.execute_tests(str(tmp_path), [target])
    
    assert not res.success
    assert res.exit_code == -1
    assert "timed out" in res.errors[0]


@patch("subprocess.run")
def test_runner_and_executor(mock_run, tmp_path):
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = "1 passed in 0.1s"
    mock_proc.stderr = ""
    mock_run.return_value = mock_proc

    executor = LocalTestExecutor()
    target = ExecutionTarget("t1", "core/tests/test_memory.py")
    summary = executor.execute(str(tmp_path), [target])
    
    assert summary.overall_success
    assert summary.total_passed == 1
    assert len(summary.results) == 1


@patch("subprocess.run")
def test_execution_service_flow(mock_run, tmp_path):
    mock_proc = MagicMock()
    mock_proc.returncode = 0
    mock_proc.stdout = "2 passed in 0.1s"
    mock_proc.stderr = ""
    mock_run.return_value = mock_proc

    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)

    service = LocalTestExecutionService(
        memory_service=mock_memory,
        knowledge_hub=mock_kh
    )
    service.initialize()
    
    target = ExecutionTarget("t1", "core/tests/test_memory.py")
    summary = service.execute_workspace_tests(
        workspace_id="ws_1",
        workspace_root=str(tmp_path),
        targets=[target]
    )
    
    assert summary.overall_success
    assert summary.total_passed == 2
    
    # Store
    service.store_execution_summary(summary)
    mock_memory.add_memory.assert_called_once()
    
    # Publish
    service.publish_execution_report(summary)
    mock_kh.sync_document.assert_called_once()


def test_backward_compatibility():
    class CustomPytestAdapter(PytestAdapter):
        @property
        def framework_name(self):
            return "custom_pytest"
            
    adapter = CustomPytestAdapter()
    assert adapter.framework_name == "custom_pytest"

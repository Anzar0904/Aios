import time
import os
import subprocess
import logging
from typing import Dict, List, Any, Optional

from aios.services.memory import MemoryService, MemoryType, MemoryMetadata
from aios.services.knowledge_hub import (
    KnowledgeHubService,
    KnowledgeDocument,
    KnowledgeMetadata as KHMetadata,
)
from aios.services.test_execution import (
    ExecutionTarget,
    ExecutionLog,
    ExecutionMetrics,
    ExecutionResult,
    ExecutionSummary,
    ExecutionSession,
    TestFrameworkAdapter,
    TestRunner,
    TestExecutor,
    TestExecutionService,
)
from aios.services.persistence import PersistenceStatus, PersistencePolicy, TestSessionRepository, TestResultRepository
import json

logger = logging.getLogger(__name__)


class PytestAdapter(TestFrameworkAdapter):
    """Pytest framework adapter executing tests in the workspace sandbox."""

    @property
    def framework_name(self) -> str:
        return "pytest"

    def execute_tests(self, workspace_root: str, targets: List[ExecutionTarget]) -> ExecutionResult:
        if not os.path.exists(workspace_root):
            return ExecutionResult(
                target=targets[0],
                success=False,
                exit_code=1,
                metrics=ExecutionMetrics(0, 0, 0, 0, 0.0),
                raw_output="",
                errors=[f"Workspace root '{workspace_root}' does not exist."]
            )

        # Build paths
        paths = [t.file_path for t in targets]
        cmd = ["pytest"] + paths

        start_time = time.time()
        try:
            # We run the command. Note: in testing environment, we might want to stub/mock this execution.
            result = subprocess.run(
                cmd,
                cwd=workspace_root,
                capture_output=True,
                text=True,
                timeout=30.0
            )
            duration = time.time() - start_time
            
            # Simple output parser for passed/failed/skipped
            stdout = result.stdout
            passed = 0
            failed = 0
            skipped = 0
            
            # Parse simple pytest output summaries: e.g. "2 passed, 1 failed, 3 warnings in 0.23s"
            for line in stdout.splitlines():
                if "passed" in line or "failed" in line or "warnings" in line or "skipped" in line:
                    parts = line.split(",")
                    for part in parts:
                        tokens = part.strip().split()
                        for i, tok in enumerate(tokens):
                            if "passed" in tok and i > 0:
                                try:
                                    passed = int(tokens[i - 1])
                                except ValueError:
                                    pass
                            elif "failed" in tok and i > 0:
                                try:
                                    failed = int(tokens[i - 1])
                                except ValueError:
                                    pass
                            elif "skipped" in tok and i > 0:
                                try:
                                    skipped = int(tokens[i - 1])
                                except ValueError:
                                    pass
            
            total = passed + failed + skipped
            if total == 0 and result.returncode == 0:
                # No tests collected or simple passing stub
                passed = len(targets)
                total = passed

            metrics = ExecutionMetrics(
                total_tests=total,
                passed_tests=passed,
                failed_tests=failed,
                skipped_tests=skipped,
                duration=duration
            )

            return ExecutionResult(
                target=targets[0],
                success=(result.returncode == 0 and failed == 0),
                exit_code=result.returncode,
                metrics=metrics,
                raw_output=stdout + "\n" + result.stderr
            )
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return ExecutionResult(
                target=targets[0],
                success=False,
                exit_code=-1,
                metrics=ExecutionMetrics(0, 0, 0, 0, duration),
                raw_output="Timeout expired.",
                errors=["Execution timed out after 30 seconds."]
            )
        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                target=targets[0],
                success=False,
                exit_code=-2,
                metrics=ExecutionMetrics(0, 0, 0, 0, duration),
                raw_output=str(e),
                errors=[f"Failed process invocation: {e}"]
            )


class LocalTestRunner(TestRunner):
    """Executes target sessions using registered framework adapters."""

    def __init__(self) -> None:
        self._adapters: Dict[str, TestFrameworkAdapter] = {
            "pytest": PytestAdapter()
        }

    def run_session(self, session: ExecutionSession, workspace_root: str) -> ExecutionSummary:
        results = []
        overall_success = True
        total_duration = 0.0
        total_passed = 0
        total_failed = 0
        total_skipped = 0

        session.logs.append(ExecutionLog(time.time(), "INFO", f"Starting session {session.session_id}"))

        # Select pytest adapter for python files by default
        adapter = self._adapters["pytest"]
        
        # Group targets or execute individually
        if session.targets:
            res = adapter.execute_tests(workspace_root, session.targets)
            results.append(res)
            
            overall_success = overall_success and res.success
            total_duration += res.metrics.duration
            total_passed += res.metrics.passed_tests
            total_failed += res.metrics.failed_tests
            total_skipped += res.metrics.skipped_tests
            
            session.logs.append(ExecutionLog(time.time(), "INFO", f"Executed {len(session.targets)} targets. Success: {res.success}"))
        else:
            session.logs.append(ExecutionLog(time.time(), "WARNING", "No execution targets specified."))

        summary = ExecutionSummary(
            summary_id=f"exec_sum_{int(time.time())}",
            workspace_id=session.workspace_id,
            overall_success=overall_success,
            total_duration=total_duration,
            total_passed=total_passed,
            total_failed=total_failed,
            total_skipped=total_skipped,
            results=results,
            timestamp=time.time()
        )
        session.summary = summary
        return summary


class LocalTestExecutor(TestExecutor):
    """Executes and monitors test target lists."""

    def __init__(self) -> None:
        self._runner = LocalTestRunner()

    def execute(self, workspace_root: str, targets: List[ExecutionTarget]) -> ExecutionSummary:
        session = ExecutionSession(
            session_id=f"exec_sess_{int(time.time())}",
            workspace_id="default_ws",
            targets=targets
        )
        return self._runner.run_session(session, workspace_root)


class LocalTestExecutionService(TestExecutionService):
    """Coordinating service orchestrating execution, memory logging, and report syncing."""

    def __init__(
        self,
        memory_service: MemoryService,
        knowledge_hub: Optional[KnowledgeHubService] = None,
        model_service: Optional[Any] = None,
        registry: Optional[Any] = None
    ) -> None:
        self._memory = memory_service
        self._knowledge_hub = knowledge_hub
        self._model = model_service
        self._registry = registry
        
        self._executor = LocalTestExecutor()
        self._session_repo = None
        self._result_repo = None

    def initialize(self) -> None:
        logger.info("Initializing LocalTestExecutionService")
        if self._registry:
            try:
                self._session_repo = self._registry.get(TestSessionRepository)
                self._result_repo = self._registry.get(TestResultRepository)
            except Exception as e:
                logger.warning(f"Failed to load Test Session/Result Repositories: {e}")
        else:
            self._session_repo = None
            self._result_repo = None

    def _get_policy(self) -> PersistencePolicy:
        if self._session_repo and hasattr(self._session_repo, "service") and self._session_repo.service.config:
            return self._session_repo.service.config.policy
        return PersistencePolicy.STRICT

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def execute_workspace_tests(
        self,
        workspace_id: str,
        workspace_root: str,
        targets: List[ExecutionTarget]
    ) -> ExecutionSummary:
        logger.info(f"Executing workspace tests for workspace: '{workspace_id}'")
        summary = self._executor.execute(workspace_root, targets)
        summary.workspace_id = workspace_id

        if self._session_repo and self._result_repo:
            policy = self._get_policy()
            try:
                # Save test session
                session_mapped = {
                    "id": summary.summary_id,
                    "workspace_id": summary.workspace_id,
                    "status": "PASSED" if summary.overall_success else "FAILED",
                    "pass_count": summary.total_passed,
                    "fail_count": summary.total_failed,
                    "coverage_summary": json.dumps({"skipped": summary.total_skipped}),
                    "execution_time": summary.total_duration,
                    "failure_categories": json.dumps({}),
                    "environment_metadata": json.dumps({"workspace_root": workspace_root}),
                    "operation_results": json.dumps({}),
                    "timestamp": summary.timestamp
                }
                res = self._session_repo.save(session_mapped)
                if res.status != PersistenceStatus.SUCCESS:
                    if policy == PersistencePolicy.STRICT:
                        raise RuntimeError(f"Strict persistence save failure: {res.message}")
                    else:
                        logger.warning(f"Persistence best-effort fallback: {res.message}")

                # Save individual target results
                for r in summary.results:
                    result_mapped = {
                        "id": f"res_{summary.summary_id}_{r.target.target_id}",
                        "session_id": summary.summary_id,
                        "suite_id": r.target.target_id,
                        "name": r.target.file_path,
                        "category": "pytest",
                        "passed": 1 if r.success else 0,
                        "execution_time": r.metrics.duration,
                        "error_message": "\n".join(r.errors) if r.errors else "",
                        "metadata": json.dumps({
                            "exit_code": r.exit_code,
                            "metrics": {
                                "total": r.metrics.total_tests,
                                "passed": r.metrics.passed_tests,
                                "failed": r.metrics.failed_tests,
                                "skipped": r.metrics.skipped_tests
                            }
                        })
                    }
                    res_r = self._result_repo.save(result_mapped)
                    if res_r.status != PersistenceStatus.SUCCESS:
                        if policy == PersistencePolicy.STRICT:
                            raise RuntimeError(f"Strict persistence save failure: {res_r.message}")
                        else:
                            logger.warning(f"Persistence best-effort fallback: {res_r.message}")
            except Exception as e:
                if policy == PersistencePolicy.STRICT:
                    raise RuntimeError(f"Strict persistence save failure: {e}") from e
                logger.warning(f"Database error saving test session/results: {e}.")

        return summary

    def store_execution_summary(self, summary: ExecutionSummary) -> None:
        content = (
            f"Test Execution Summary - ID: {summary.summary_id}\n"
            f"Overall Success: {summary.overall_success}\n"
            f"Passed Count: {summary.total_passed}\n"
            f"Failed Count: {summary.total_failed}\n"
            f"Skipped Count: {summary.total_skipped}\n"
            f"Total Duration: {summary.total_duration:.2f}s"
        )
        
        self._memory.add_memory(
            content=content,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id=summary.summary_id,
                session_id=summary.summary_id,
                tags=["test_execution", "quality_metrics"],
                importance=2,
                source_subsystem="test_execution_engine"
            )
        )

    def publish_execution_report(self, summary: ExecutionSummary) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        results_md = []
        for r in summary.results:
            results_md.append(
                f"### Target: `{r.target.file_path}`\n"
                f"- **Success**: {r.success}\n"
                f"- **Duration**: {r.metrics.duration:.2f}s\n"
                f"- **Total Tests**: {r.metrics.total_tests}\n"
                f"- **Passed**: {r.metrics.passed_tests}\n"
                f"- **Failed**: {r.metrics.failed_tests}\n"
                f"- **Raw Output Preview**:\n```\n{r.raw_output[:1000]}...\n```\n"
            )

        report_md = (
            f"# Engineering Test Execution Report\n\n"
            f"**Summary ID**: `{summary.summary_id}`\n"
            f"**Workspace ID**: `{summary.workspace_id}`\n"
            f"**Overall Success**: `{summary.overall_success}`\n"
            f"**Total Passed**: {summary.total_passed}\n"
            f"**Total Failed**: {summary.total_failed}\n"
            f"**Total Duration**: {summary.total_duration:.2f}s\n\n"
            f"## Individual Suite Results\n"
            + "\n".join(results_md)
        )

        doc = KnowledgeDocument(
            document_id=f"exec_report_{summary.summary_id}",
            title=f"Test Execution Report - {summary.summary_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"exec_report_{summary.summary_id}",
                timestamp=summary.timestamp,
                source_subsystem="test_execution_engine",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

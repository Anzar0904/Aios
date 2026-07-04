import os
import time
import logging
from typing import Dict, List, Any, Optional

from aios.services.memory import MemoryService, MemoryType, MemoryMetadata
from aios.services.knowledge_hub import (
    KnowledgeHubService,
    KnowledgeDocument,
    KnowledgeMetadata as KHMetadata,
)
from aios.services.test_impact import CoverageTarget, RegressionCandidate
from aios.services.test_execution import ExecutionSummary
from aios.services.test_coverage import (
    CoverageMetrics,
    CoveragePolicy,
    CoverageSummary,
    CoverageReport,
    RegressionRisk,
    ValidationGap,
    CoverageAnalyzer,
    RegressionAnalyzer,
    AITestCoverageService,
)

logger = logging.getLogger(__name__)


class LocalCoverageAnalyzer(CoverageAnalyzer):
    """Concrete coverage evaluator simulating statement, branch, and configuration coverages."""

    def analyze_coverage(
        self,
        execution_summary: ExecutionSummary,
        targets: List[CoverageTarget],
        policy: CoveragePolicy
    ) -> CoverageReport:
        # Simulate coverage calculations based on execution success rate
        total_passed = getattr(execution_summary, "total_passed", 0)
        total_failed = getattr(execution_summary, "total_failed", 0)
        if not isinstance(total_passed, (int, float)):
            total_passed = 0
        if not isinstance(total_failed, (int, float)):
            total_failed = 0

        passed_ratio = 1.0
        if total_passed + total_failed > 0:
            passed_ratio = total_passed / (total_passed + total_failed)

        stmt_cov = min(95.0, max(50.0, passed_ratio * 92.0))
        branch_cov = min(92.0, max(45.0, passed_ratio * 87.0))
        
        metrics = CoverageMetrics(
            statement_coverage=stmt_cov,
            branch_coverage=branch_cov,
            function_coverage=stmt_cov + 1.0,
            class_coverage=stmt_cov + 2.0,
            module_coverage=stmt_cov - 1.0,
            interface_coverage=stmt_cov - 2.0,
            configuration_coverage=stmt_cov + 3.0
        )

        overall = (stmt_cov + branch_cov) / 2.0
        
        summary = CoverageSummary(
            summary_id=f"cov_sum_{int(time.time())}",
            workspace_id=execution_summary.workspace_id,
            overall_coverage_pct=overall,
            metrics=metrics,
            timestamp=time.time()
        )

        return CoverageReport(
            report_id=f"cov_rep_{int(time.time())}",
            workspace_id=execution_summary.workspace_id,
            targets=targets,
            summary=summary,
            policy=policy,
            timestamp=time.time()
        )


class LocalRegressionAnalyzer(RegressionAnalyzer):
    """Concrete regression risk evaluator checking dependency chains."""

    def analyze_regression_risks(
        self,
        affected_files: List[str],
        dependency_graph: Dict[str, List[str]],
        execution_summary: ExecutionSummary
    ) -> RegressionRisk:
        risk_level = "Low"
        prob = 0.10
        shared_risks = []
        critical_paths = []
        candidates = []

        # High risk if core files are modified
        has_kernel = any("kernel" in f or "bootstrap" in f for f in affected_files)
        if has_kernel:
            risk_level = "High"
            prob = 0.75
            shared_risks.append("Core kernel dependency chain impact.")
            critical_paths.append("boot -> initialize_services")
            
        for f in affected_files:
            # Check importers count
            importers = [target for target, deps in dependency_graph.items() if f in deps]
            if len(importers) >= 1:
                risk_level = "Critical" if has_kernel else "Medium"
                prob = max(prob, 0.50)
                shared_risks.append(f"Highly coupled module {os.path.basename(f)} referenced by {len(importers)} files.")
                candidates.append(
                    RegressionCandidate(
                        file_path=f,
                        reason=f"Impacted module referenced by: {importers}",
                        coupling_density=len(importers)
                    )
                )

        return RegressionRisk(
            risk_level=risk_level,
            regression_probability=prob,
            shared_dependency_risks=shared_risks,
            critical_execution_paths=critical_paths,
            regression_candidates=candidates
        )


class LocalAITestCoverageService(AITestCoverageService):
    """Coordinating service evaluates test validations, caches metrics, and publishes Notion summaries."""

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

        self._coverage_analyzer = LocalCoverageAnalyzer()
        self._regression_analyzer = LocalRegressionAnalyzer()

    def initialize(self) -> None:
        logger.info("Initializing LocalAITestCoverageService")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def evaluate_validation(
        self,
        workspace_id: str,
        execution_summary: ExecutionSummary,
        affected_files: List[str],
        dependency_graph: Dict[str, List[str]],
        policy: CoveragePolicy
    ) -> Dict[str, Any]:
        logger.info(f"Evaluating validation reports for workspace: '{workspace_id}'")

        # 1. Coverage targets setup
        targets = []
        for f in affected_files:
            targets.append(CoverageTarget(file_path=f, statement_coverage=policy.min_statement_coverage, branch_coverage=policy.min_branch_coverage))

        # 2. Analyze Coverage
        cov_report = self._coverage_analyzer.analyze_coverage(execution_summary, targets, policy)

        # 3. Analyze Regression Risk
        reg_risk = self._regression_analyzer.analyze_regression_risks(affected_files, dependency_graph, execution_summary)

        # 4. Identify Gaps
        gaps = []
        metrics = cov_report.summary.metrics
        if metrics.statement_coverage < policy.min_statement_coverage:
            gaps.append(
                ValidationGap(
                    gap_id=f"gap_stmt_{int(time.time())}",
                    gap_type="low_coverage",
                    description=f"Statement coverage ({metrics.statement_coverage:.1f}%) is below target policy ({policy.min_statement_coverage:.1f}%).",
                    file_path=affected_files[0] if affected_files else "unknown",
                    recommendation="Add missing unit tests to cover statements."
                )
            )

        if reg_risk.risk_level in ["High", "Critical"]:
            gaps.append(
                ValidationGap(
                    gap_id=f"gap_reg_{int(time.time())}",
                    gap_type="missing_tests",
                    description="High regression risk in core modules.",
                    file_path=affected_files[0] if affected_files else "unknown",
                    recommendation="Implement additional regression validation test blocks."
                )
            )

        return {
            "coverage_report": cov_report,
            "regression_risk": reg_risk,
            "validation_gaps": gaps
        }

    def store_coverage_summary(self, report: CoverageReport) -> None:
        content = (
            f"Coverage Intelligence Report - ID: {report.report_id}\n"
            f"Overall Coverage: {report.summary.overall_coverage_pct:.1f}%\n"
            f"Statement Coverage: {report.summary.metrics.statement_coverage:.1f}%\n"
            f"Branch Coverage: {report.summary.metrics.branch_coverage:.1f}%\n"
            f"Target Policy: {report.policy.policy_id} (Min Stmt: {report.policy.min_statement_coverage:.1f}%)"
        )
        
        self._memory.add_memory(
            content=content,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id=report.report_id,
                session_id=report.report_id,
                tags=["coverage_analysis", "regression_risk"],
                importance=2,
                source_subsystem="test_coverage_engine"
            )
        )

    def publish_coverage_report(self, report: CoverageReport) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        targets_md = []
        for t in report.targets:
            targets_md.append(f"- `{t.file_path}` [Target Stmt: {t.statement_coverage}%, Target Branch: {t.branch_coverage}%]")

        report_md = (
            f"# Engineering Test Coverage Report\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Workspace ID**: `{report.workspace_id}`\n"
            f"**Overall Calculated Coverage**: `{report.summary.overall_coverage_pct:.1f}%`\n"
            f"**Statement Coverage**: {report.summary.metrics.statement_coverage:.1f}%\n"
            f"**Branch Coverage**: {report.summary.metrics.branch_coverage:.1f}%\n"
            f"**Policy ID**: `{report.policy.policy_id}`\n\n"
            f"## Targets Evaluated\n"
            + "\n".join(targets_md)
        )

        doc = KnowledgeDocument(
            document_id=f"cov_report_{report.report_id}",
            title=f"Coverage Report - {report.report_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"cov_report_{report.report_id}",
                timestamp=report.timestamp,
                source_subsystem="test_coverage_engine",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

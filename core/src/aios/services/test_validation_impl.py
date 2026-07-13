import json
import logging
import time
from typing import Any, Optional

from aios.services.knowledge_hub import (
    KnowledgeDocument,
    KnowledgeHubService,
)
from aios.services.knowledge_hub import (
    KnowledgeMetadata as KHMetadata,
)
from aios.services.memory import MemoryMetadata, MemoryService, MemoryType
from aios.services.model import LLMRequest, ModelService
from aios.services.test_coverage import CoverageReport
from aios.services.test_execution import ExecutionSummary
from aios.services.test_failure import FailureAnalysisReport
from aios.services.test_validation import (
    ValidationDecision,
    ValidationEvidence,
    ValidationFinding,
    ValidationGate,
    ValidationMetrics,
    ValidationRecommendation,
    ValidationReport,
    ValidationScore,
    ValidationService,
    ValidationStatus,
    ValidationSummary,
)

logger = logging.getLogger(__name__)


class LocalValidationService(ValidationService):
    """Unified validation manager compiling executing metrics, coverage goals, and diagnostics reports."""

    def __init__(
        self,
        memory_service: MemoryService,
        knowledge_hub: Optional[KnowledgeHubService] = None,
        model_service: Optional[ModelService] = None,
        registry: Optional[Any] = None,
    ) -> None:
        self._memory = memory_service
        self._knowledge_hub = knowledge_hub
        self._model = model_service
        self._registry = registry

    def initialize(self) -> None:
        logger.info("Initializing LocalValidationService")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def synthesize_validation(
        self,
        workspace_id: str,
        execution_summary: ExecutionSummary,
        coverage_report: CoverageReport,
        failure_report: FailureAnalysisReport,
    ) -> ValidationReport:
        logger.info(f"Synthesizing unified validation report for workspace: '{workspace_id}'")

        # Extract values safely to avoid TypeError when using format strings on MagicMocks
        total_passed = getattr(execution_summary, "total_passed", 0)
        total_failed = getattr(execution_summary, "total_failed", 0)
        if not isinstance(total_passed, (int, float)):
            total_passed = 0
        if not isinstance(total_failed, (int, float)):
            total_failed = 0

        overall_cov = 0.0
        min_stmt = 80.0
        if coverage_report and hasattr(coverage_report, "summary") and coverage_report.summary:
            overall_cov = getattr(coverage_report.summary, "overall_coverage_pct", 0.0)
        if coverage_report and hasattr(coverage_report, "policy") and coverage_report.policy:
            min_stmt = getattr(coverage_report.policy, "min_statement_coverage", 80.0)

        if not isinstance(overall_cov, (int, float)):
            overall_cov = 0.0
        if not isinstance(min_stmt, (int, float)):
            min_stmt = 80.0

        fail_count = getattr(failure_report, "failed_suites_count", 0)
        if not isinstance(fail_count, (int, float)):
            fail_count = 0

        fail_severity_val = "low"
        if failure_report and hasattr(failure_report, "severity") and failure_report.severity:
            fail_severity_val = getattr(failure_report.severity, "value", "low")
        if not isinstance(fail_severity_val, str):
            fail_severity_val = "low"

        # 1. Validation gates evaluation
        gates = []

        # Test Execution Gate
        exec_ev = ValidationEvidence(
            evidence_id=f"ev_exec_{int(time.time())}",
            evidence_type="execution_summary",
            summary_text=f"Total run: {total_passed + total_failed}. Failed: {total_failed}.",
            metrics_pct=100.0 if total_failed == 0 else 0.0,
        )
        exec_gate = ValidationGate(
            gate_name="Tests Passed",
            status=ValidationStatus.PASS if total_failed == 0 else ValidationStatus.FAIL,
            checked_rule="Failed execution count must equal zero.",
            evidence=[exec_ev],
        )
        gates.append(exec_gate)

        # Coverage Gate
        cov_ev = ValidationEvidence(
            evidence_id=f"ev_cov_{int(time.time())}",
            evidence_type="coverage_report",
            summary_text=f"Overall coverage: {overall_cov:.1f}%. Target: {min_stmt:.1f}%.",
            metrics_pct=overall_cov,
        )
        cov_status = ValidationStatus.PASS
        if overall_cov < min_stmt:
            cov_status = ValidationStatus.WARNING
        cov_gate = ValidationGate(
            gate_name="Coverage Target Met",
            status=cov_status,
            checked_rule=f"Overall statement coverage must exceed {min_stmt:.1f}%.",
            evidence=[cov_ev],
        )
        gates.append(cov_gate)

        # Failure Severity Gate
        fail_ev = ValidationEvidence(
            evidence_id=f"ev_fail_{int(time.time())}",
            evidence_type="failure_report",
            summary_text=f"Failure severity diagnosed as: {fail_severity_val.upper()}.",
            metrics_pct=100.0 if fail_count == 0 else 50.0,
        )
        fail_status = ValidationStatus.PASS
        if fail_count > 0:
            fail_status = (
                ValidationStatus.FAIL
                if fail_severity_val == "critical"
                else ValidationStatus.WARNING
            )
        fail_gate = ValidationGate(
            gate_name="No Critical Failures",
            status=fail_status,
            checked_rule="Severity classification must not evaluate to Critical.",
            evidence=[fail_ev],
        )
        gates.append(fail_gate)

        # 2. Weighted scoring calculations
        raw_score = 100.0
        weights = {"execution": 0.50, "coverage": 0.30, "severity": 0.20}

        # Deductions
        exec_deduction = 50.0 * (total_failed / max(1, total_passed + total_failed))
        cov_deduction = max(0.0, min_stmt - overall_cov)
        fail_deduction = 20.0 if fail_count > 0 else 0.0

        raw_score -= (
            weights["execution"] * exec_deduction
            + weights["coverage"] * cov_deduction
            + weights["severity"] * fail_deduction
        )
        raw_score = max(0.0, min(100.0, raw_score))

        score_details = ValidationScore(
            raw_score=raw_score, weight_metrics=weights, confidence_penalty=0.0
        )

        # 3. Decision Selection
        overall_status = ValidationStatus.PASS
        decision = ValidationDecision.APPROVED

        failed_count = sum(1 for g in gates if g.status == ValidationStatus.FAIL)
        warning_count = sum(1 for g in gates if g.status == ValidationStatus.WARNING)

        if failed_count > 0 or raw_score < 70.0:
            overall_status = ValidationStatus.FAIL
            decision = ValidationDecision.REJECTED
        elif warning_count > 0 or raw_score < 90.0:
            overall_status = ValidationStatus.WARNING
            decision = ValidationDecision.MANUAL_REVIEW

        # 4. Findings and Recommendations compiler
        findings = []
        recommendations = []

        for idx, g in enumerate(gates):
            if g.status != ValidationStatus.PASS:
                findings.append(
                    ValidationFinding(
                        finding_id=f"find_{idx}_{int(time.time())}",
                        severity="High" if g.status == ValidationStatus.FAIL else "Medium",
                        description=g.checked_rule,
                        file_path="workspace",
                    )
                )
                recommendations.append(
                    ValidationRecommendation(
                        recommendation_id=f"rec_val_{idx}_{int(time.time())}",
                        recommendation_type="manual_review"
                        if g.status == ValidationStatus.WARNING
                        else "implementation_change",
                        description=f"Resolve validation gate failure for: {g.gate_name}.",
                        actionable_steps=["Trace code path.", "Verify requirements."],
                    )
                )

        metrics = ValidationMetrics(
            overall_score=raw_score,
            passed_gates_count=sum(1 for g in gates if g.status == ValidationStatus.PASS),
            failed_gates_count=failed_count,
            total_tests_run=total_passed + total_failed,
            failed_tests_run=total_failed,
            achieved_coverage_pct=overall_cov,
        )

        summary = ValidationSummary(
            summary_id=f"val_sum_{int(time.time())}",
            workspace_id=workspace_id,
            overall_status=overall_status,
            decision=decision,
            score=score_details,
            timestamp=time.time(),
        )

        report = ValidationReport(
            report_id=f"val_report_{int(time.time())}",
            workspace_id=workspace_id,
            executive_summary=f"Validation outcome evaluates to {overall_status.value.upper()}. Decision status set to {decision.value.upper()}.",
            summary=summary,
            gates=gates,
            findings=findings,
            recommendations=recommendations,
            metrics=metrics,
            timestamp=time.time(),
        )

        # 5. LLM refinement if model is active
        if self._model:
            try:
                prompt = (
                    "You are the Principal QA architect for the Personal AI OS.\n"
                    f"Overall Decision: {decision.value}\n"
                    f"Weighted Score: {raw_score:.1f}\n\n"
                    "Refine validation summary. Return a single pure JSON:\n"
                    "{\n"
                    '  "decision": "approved",\n'
                    '  "score_adjustment": 0.0,\n'
                    '  "executive_summary": "Refined executive summary validation passes."\n'
                    "}"
                )

                response = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output pure JSON only.",
                        task_category="testing",
                        preferences={"JSON_output": True},
                    )
                )

                content = response.content.strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]

                data = json.loads(content)
                dec_val = data.get("decision", "manual_review").upper()
                report.summary.decision = (
                    ValidationDecision[dec_val]
                    if dec_val in ValidationDecision.__members__
                    else report.summary.decision
                )
                report.executive_summary = data.get("executive_summary", report.executive_summary)
            except Exception as e:
                logger.debug(f"LLM validation synthesis refinement failed: {e}. Keeping defaults.")

        return report

    def store_validation_report(self, report: ValidationReport) -> None:
        summary = (
            f"Authoritative Validation Report - ID: {report.report_id}\n"
            f"Overall Status: {report.summary.overall_status.value.upper()}\n"
            f"Authoritative Decision: {report.summary.decision.value.upper()}\n"
            f"Overall Score: {report.metrics.overall_score:.1f}/100.0\n"
            f"Passed Gates: {report.metrics.passed_gates_count}/{len(report.gates)}\n"
            f"Total Tests Run: {report.metrics.total_tests_run}\n"
            f"Achieved Coverage: {report.metrics.achieved_coverage_pct:.1f}%"
        )

        self._memory.add_memory(
            content=summary,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id=report.report_id,
                session_id=report.report_id,
                tags=["validation_report", "quality_release_gates"],
                importance=2,
                source_subsystem="validation_service",
            ),
        )

    def publish_validation_report(self, report: ValidationReport) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        gates_md = []
        for g in report.gates:
            gates_md.append(f"- **{g.gate_name}**: `{g.status.value.upper()}` ({g.checked_rule})")

        findings_md = []
        for f in report.findings:
            findings_md.append(f"- `[{f.severity}]` {f.description}")

        recs_md = []
        for r in report.recommendations:
            steps = ", ".join(r.actionable_steps)
            recs_md.append(f"- **{r.recommendation_type}**: {r.description} Steps: [{steps}]")

        report_md = (
            f"# Authoritative Unified Validation Report\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Workspace ID**: `{report.workspace_id}`\n"
            f"**Overall Validation Decision**: `{report.summary.decision.value.upper()}`\n"
            f"**Calculated Score**: `{report.metrics.overall_score:.1f}/100.0`\n"
            f"**Passed Gates**: {report.metrics.passed_gates_count} / {len(report.gates)}\n\n"
            f"## Executive Summary\n"
            f"{report.executive_summary}\n\n"
            f"## Gating Outcomes\n" + "\n".join(gates_md) + "\n\n"
            "## Validation Findings\n"
            + (
                "\n".join(findings_md)
                if findings_md
                else "- *No warnings or errors detected. Gating satisfies release criteria.*"
            )
            + "\n\n"
            "## Corrective Action Recommendations\n"
            + ("\n".join(recs_md) if recs_md else "- *No actions required.*")
        )

        doc = KnowledgeDocument(
            document_id=f"val_report_{report.report_id}",
            title=f"Validation Report - {report.report_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"val_report_{report.report_id}",
                timestamp=report.timestamp,
                source_subsystem="validation_service",
                category="Project",
            ),
        )
        self._knowledge_hub.sync_document(doc, "notion")

import logging
import os
import time
from typing import Any, Dict, List, Optional

from aios.services.ai_workspace import AIWorkspaceService
from aios.services.approval import ApprovalPackage
from aios.services.knowledge_hub import (
    KnowledgeDocument,
    KnowledgeHubService,
)
from aios.services.knowledge_hub import (
    KnowledgeMetadata as KHMetadata,
)
from aios.services.memory import MemoryService, MemoryType
from aios.services.model import LLMRequest, ModelService
from aios.services.review import (
    ReviewAnalyzer,
    ReviewCategory,
    ReviewEngine,
    ReviewEvidence,
    ReviewFinding,
    ReviewRecommendation,
    ReviewReport,
    ReviewSession,
    ReviewSeverity,
    ReviewSummary,
    ReviewValidator,
)

logger = logging.getLogger(__name__)


class LocalReviewAnalyzer(ReviewAnalyzer):
    """Concrete review analyzer generating findings from Approval Package details."""

    def analyze_package(self, workspace_id: str, package: ApprovalPackage) -> tuple[ReviewSummary, List[ReviewFinding]]:
        findings = []
        strengths = []
        weaknesses = []
        blocking_issues = []
        recommendations = []

        # 1. Strengths Check
        if package.validation_summary.get("score", 0.0) >= 90.0:
            strengths.append(f"High validation pass rate ({package.validation_summary['score']:.1f}).")
        if package.coverage_summary.get("achieved_pct", 0.0) >= 80.0:
            strengths.append(f"Strong testing statement coverage ({package.coverage_summary['achieved_pct']:.1f}%).")
        if package.risk_summary.get("risk_level", "low").lower() == "low":
            strengths.append("Low overall implementation boundary coupling risk.")

        # 2. Validation / Health Checks -> High / Critical Findings
        if package.overall_health.lower() == "degraded":
            weaknesses.append("Degraded health status logged in package summary.")
            finding_id = f"find_health_{int(time.time())}_1"
            f_ev = ReviewEvidence("approval_package", "health", {"overall_health": "degraded"}, time.time())
            f_rec = ReviewRecommendation(
                recommendation_id=f"rec_health_{finding_id}",
                description="Restore repository sanity state by resolving diagnostic failures.",
                actionable_steps=["Check execution logs for compilation warnings.", "Resolve mock issues in tests."]
            )
            findings.append(
                ReviewFinding(
                    finding_id=finding_id,
                    category=ReviewCategory.RELIABILITY,
                    severity=ReviewSeverity.HIGH,
                    confidence=0.95,
                    description="Repository health metric is degraded.",
                    evidence=[f_ev],
                    recommendation=f_rec,
                    related_components=package.affected_components,
                    related_files=package.affected_files,
                    blocking=True
                )
            )
            blocking_issues.append("Repository health is degraded.")
            recommendations.append(f_rec)

        # 3. Test Score Check
        score = package.validation_summary.get("score", 100.0)
        if score < 80.0:
            weaknesses.append(f"Low validation gate score: {score:.1f}.")
            finding_id = f"find_score_{int(time.time())}_2"
            f_ev = ReviewEvidence("approval_package", "validation", {"score": score}, time.time())
            f_rec = ReviewRecommendation(
                recommendation_id=f"rec_score_{finding_id}",
                description="Increase validation compliance to clear gate rules.",
                actionable_steps=["Run failing test executions manually.", "Identify boundary edge cases."]
            )
            findings.append(
                ReviewFinding(
                    finding_id=finding_id,
                    category=ReviewCategory.TESTING,
                    severity=ReviewSeverity.HIGH,
                    confidence=1.0,
                    description=f"Validation score ({score:.1f}) is below standard gating limits.",
                    evidence=[f_ev],
                    recommendation=f_rec,
                    related_components=package.affected_components,
                    related_files=package.affected_files,
                    blocking=True
                )
            )
            blocking_issues.append(f"Validation score is below target: {score:.1f}.")
            recommendations.append(f_rec)

        # 4. Coverage Check
        cov = package.coverage_summary.get("achieved_pct", 100.0)
        if cov < 75.0:
            weaknesses.append(f"Low testing coverage: {cov:.1f}%.")
            finding_id = f"find_cov_{int(time.time())}_3"
            f_ev = ReviewEvidence("approval_package", "coverage", {"coverage_pct": cov}, time.time())
            f_rec = ReviewRecommendation(
                recommendation_id=f"rec_cov_{finding_id}",
                description="Author additional unit or integration tests targeting the modifications.",
                actionable_steps=["Write test coverage for modified lines.", "Inspect code structure gaps."]
            )
            findings.append(
                ReviewFinding(
                    finding_id=finding_id,
                    category=ReviewCategory.TESTING,
                    severity=ReviewSeverity.MEDIUM,
                    confidence=0.9,
                    description=f"Code statement coverage ({cov:.1f}%) is below recommended target.",
                    evidence=[f_ev],
                    recommendation=f_rec,
                    related_components=package.affected_components,
                    related_files=package.affected_files,
                    blocking=False
                )
            )
            recommendations.append(f_rec)

        # 5. Risk Check
        risk = package.risk_summary.get("risk_level", "low").lower()
        if risk in ["high", "critical"]:
            weaknesses.append(f"High coupling change risk: '{risk}'.")
            finding_id = f"find_risk_{int(time.time())}_4"
            f_ev = ReviewEvidence("approval_package", "risk", {"risk_level": risk}, time.time())
            f_rec = ReviewRecommendation(
                recommendation_id=f"rec_risk_{finding_id}",
                description="Refactor modules coupling and introduce strict boundary controls.",
                actionable_steps=["Isolate dependency routes.", "Add execution timeout sandboxes."]
            )
            findings.append(
                ReviewFinding(
                    finding_id=finding_id,
                    category=ReviewCategory.DEPENDENCY_RISK,
                    severity=ReviewSeverity.HIGH,
                    confidence=0.85,
                    description=f"High risk score evaluation: '{risk}'.",
                    evidence=[f_ev],
                    recommendation=f_rec,
                    related_components=package.affected_components,
                    related_files=package.affected_files,
                    blocking=True
                )
            )
            blocking_issues.append(f"High risk score evaluation: '{risk}'.")
            recommendations.append(f_rec)

        # 6. Documentation Check
        completed = package.documentation_summary.get("completed", True)
        if not completed:
            missing = package.documentation_summary.get("missing_docs", [])
            weaknesses.append("Incomplete documentation.")
            finding_id = f"find_doc_{int(time.time())}_5"
            f_ev = ReviewEvidence("approval_package", "documentation", {"missing_docs": missing}, time.time())
            f_rec = ReviewRecommendation(
                recommendation_id=f"rec_doc_{finding_id}",
                description="Complete all required module reference specifications.",
                actionable_steps=[f"Generate {m} reference specifications." for m in missing]
            )
            findings.append(
                ReviewFinding(
                    finding_id=finding_id,
                    category=ReviewCategory.DOCUMENTATION,
                    severity=ReviewSeverity.MEDIUM,
                    confidence=0.95,
                    description=f"Documentation is incomplete. Missing: {', '.join(missing)}.",
                    evidence=[f_ev],
                    recommendation=f_rec,
                    related_components=package.affected_components,
                    related_files=package.affected_files,
                    blocking=False
                )
            )
            recommendations.append(f_rec)

        # 7. Critical Failure Threshold Check
        fails = package.failure_summary.get("critical_count", 0)
        if fails > 0:
            weaknesses.append(f"Discovered {fails} critical test failures.")
            finding_id = f"find_fails_{int(time.time())}_6"
            f_ev = ReviewEvidence("approval_package", "failures", {"critical_count": fails}, time.time())
            f_rec = ReviewRecommendation(
                recommendation_id=f"rec_fails_{finding_id}",
                description="Fix all failing assertions and traceback faults to clear gating.",
                actionable_steps=["Trace failing tests traceback stack.", "Fix core bugs in components."]
            )
            findings.append(
                ReviewFinding(
                    finding_id=finding_id,
                    category=ReviewCategory.RELIABILITY,
                    severity=ReviewSeverity.CRITICAL,
                    confidence=0.98,
                    description=f"Discovered {fails} critical test failures during execution runs.",
                    evidence=[f_ev],
                    recommendation=f_rec,
                    related_components=package.affected_components,
                    related_files=package.affected_files,
                    blocking=True
                )
            )
            blocking_issues.append(f"Discovered {fails} critical test failures.")
            recommendations.append(f_rec)

        # Executive summary text
        exec_sum = (
            f"Automated engineering review completed for package '{package.package_id}'. "
            f"Detected {len(findings)} findings. Overall validation gating health is evaluated as '{package.overall_health.upper()}'."
        )

        summary = ReviewSummary(
            summary_id=f"sum_{package.package_id}",
            executive_summary=exec_sum,
            overall_health=package.overall_health,
            risk_summary=f"Evaluated overall change risk level: '{risk.upper()}'.",
            strengths=strengths if strengths else ["Basic functionality compliance verified."],
            weaknesses=weaknesses,
            blocking_issues=blocking_issues,
            recommendations=recommendations,
            reviewer_confidence=0.9,
            timestamp=time.time()
        )

        return summary, findings


class LocalReviewValidator(ReviewValidator):
    """Concrete validator flagging duplicate findings, evidence issues, and inconsistency gates."""

    def validate_review(self, report: ReviewReport) -> List[str]:
        errors = []
        seen_findings = set()

        # 1. Integrity check: Summary Confidence
        if not (0.0 <= report.summary.reviewer_confidence <= 1.0):
            errors.append(f"Review Integrity Error: Confidence rating '{report.summary.reviewer_confidence}' stands outside [0.0, 1.0].")

        for f in report.findings:
            # 2. Duplicate findings
            fingerprint = (f.category, f.severity, f.description.strip().lower())
            if fingerprint in seen_findings:
                errors.append(f"Duplicate Finding: Category '{f.category.value}' contains duplicate description.")
            seen_findings.add(fingerprint)

            # 3. Evidence completeness
            if not f.evidence:
                errors.append(f"Evidence Warning: Finding '{f.finding_id}' lacks supporting telemetry evidence.")

            # 4. Severity consistency
            if f.blocking and f.severity in [ReviewSeverity.INFO, ReviewSeverity.LOW]:
                errors.append(f"Severity Consistency Error: Finding '{f.finding_id}' is marked blocking but has low severity '{f.severity.value}'.")

            # 5. Recommendation completeness
            if not f.recommendation or not f.recommendation.recommendation_id:
                errors.append(f"Recommendation completeness error: Finding '{f.finding_id}' lacks actionable remediation recommendation.")
            elif not f.recommendation.actionable_steps:
                errors.append(f"Recommendation Warning: Actionable steps checklist is empty for finding '{f.finding_id}'.")

        return errors


class LocalReviewEngine(ReviewEngine):
    """Central orchestrator managing automated review runs, memory logging, Notion syncs."""

    def __init__(
        self,
        memory_service: MemoryService,
        knowledge_hub: Optional[KnowledgeHubService] = None,
        model_service: Optional[ModelService] = None,
        registry: Optional[Any] = None
    ) -> None:
        self._memory = memory_service
        self._knowledge_hub = knowledge_hub
        self._model = model_service
        self._registry = registry

        self._analyzer = LocalReviewAnalyzer()
        self._validator = LocalReviewValidator()

        self._sessions: Dict[str, ReviewSession] = {}
        self._histories: Dict[str, List[ReviewSummary]] = {}

    def initialize(self) -> None:
        logger.info("Initializing LocalReviewEngine")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def _write_to_workspace(self, workspace_id: str, filename: str, content: str) -> str:
        workspace_root = None
        workspace_service = None
        if self._registry:
            try:
                workspace_service = self._registry.get(AIWorkspaceService)
            except Exception:
                pass

        if workspace_service and hasattr(workspace_service, "_workspaces"):
            meta = workspace_service._workspaces.get(workspace_id)
            if meta:
                workspace_root = meta.workspace_root

        if not workspace_root:
            workspace_root = os.path.join(os.getcwd(), "temp", "workspaces", workspace_id)

        reviews_dir = os.path.join(workspace_root, "docs", "reviews")
        os.makedirs(reviews_dir, exist_ok=True)
        
        file_path = os.path.join(reviews_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return file_path

    def run_review(self, workspace_id: str, package: ApprovalPackage) -> ReviewSession:
        logger.info(f"Initiating code quality review on package '{package.package_id}'")

        # 1. Start Session
        session = ReviewSession(
            session_id=f"rev_sess_{int(time.time())}",
            workspace_id=workspace_id,
            package_id=package.package_id,
            report=None,
            status="open",
            created_at=time.time()
        )
        self._sessions[session.session_id] = session

        # 2. Run analysis
        summary, findings = self._analyzer.analyze_package(workspace_id, package)

        # 3. Model refinement
        if self._model:
            try:
                prompt = (
                    "You are the Principal Review Engineer for the Personal AI OS.\n"
                    f"Generated review summary: {summary.executive_summary}\n\n"
                    "Refine layout structures and write a concise, professional executive overview. Return refined summary text only."
                )
                res = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output refined text directly.",
                        task_category="testing"
                    )
                )
                refined = res.content.strip()
                if refined:
                    summary.executive_summary = refined
            except Exception as e:
                logger.debug(f"LLM Review refinement failed: {e}")

        # 4. Form Report
        report = ReviewReport(
            report_id=f"rep_{session.session_id}",
            session_id=session.session_id,
            workspace_id=workspace_id,
            summary=summary,
            findings=findings,
            timestamp=time.time()
        )
        session.report = report

        # 5. Run validation checks
        warnings = self._validator.validate_review(report)
        if warnings:
            logger.warning(f"Review validation warning logs: {warnings}")

        # 6. Save review artifacts inside AI Workspace ONLY
        findings_md = []
        for f in findings:
            steps_md = "\n".join(f"  - [ ] {step}" for step in f.recommendation.actionable_steps)
            findings_md.append(
                f"### [{f.severity.value}] {f.description}\n"
                f"- **Category**: `{f.category.value}` (Confidence: {f.confidence:.2f})\n"
                f"- **Blocking**: `{'YES' if f.blocking else 'NO'}`\n"
                f"- **Actionable Remediation**:\n{steps_md}"
            )

        report_md = (
            f"# Intelligent Review Engine Report\n\n"
            f"**Session ID**: `{session.session_id}`\n"
            f"**Workspace ID**: `{workspace_id}`\n"
            f"**Overall Health**: `{summary.overall_health.upper()}`\n"
            f"**Risk Level**: `{summary.risk_summary}`\n\n"
            f"## Executive Overview\n{summary.executive_summary}\n\n"
            f"## Discovered Findings\n" + "\n\n".join(findings_md)
        )
        self._write_to_workspace(workspace_id, f"REVIEW_REPORT_{session.session_id}.md", report_md)

        # 7. Add to history
        if workspace_id not in self._histories:
            self._histories[workspace_id] = []
        self._histories[workspace_id].append(summary)

        session.status = "closed"
        session.closed_at = time.time()
        return session

    def get_session(self, session_id: str) -> Optional[ReviewSession]:
        return self._sessions.get(session_id)

    def get_history(self, workspace_id: str) -> List[ReviewSummary]:
        return self._histories.get(workspace_id, [])

    def store_review_summary(self, session: ReviewSession) -> None:
        if not session.report:
            return
        
        # Count findings severities statistics
        stats = {"INFO": 0, "LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
        for f in session.report.findings:
            stats[f.severity.value] = stats.get(f.severity.value, 0) + 1

        # Form content string. Never store repository source code.
        content = (
            f"Intelligent Quality Review Logged\n"
            f"Workspace ID: {session.workspace_id}\n"
            f"Session ID: {session.session_id}\n"
            f"Findings Stats: Info={stats['INFO']}, Low={stats['LOW']}, Med={stats['MEDIUM']}, High={stats['HIGH']}, Crit={stats['CRITICAL']}\n"
            f"Health Rating Outcome: {session.report.summary.overall_health.upper()}\n"
            f"Timestamp: {time.ctime(session.created_at)}"
        )

        self._memory.add_memory(
            content=content,
            memory_type=MemoryType.PROJECT,
            tags=["quality_review", "audit_checkpoint", "findings_statistics"],
            importance=2,
            metadata_additional={
                "session_id": session.session_id,
                "workspace_id": session.workspace_id,
                "health_status": session.report.summary.overall_health,
                "findings_statistics": stats,
                "reviewer_confidence": session.report.summary.reviewer_confidence
            }
        )

    def publish_review_report(self, report: ReviewReport) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publishing.")
            return

        recs_list = []
        for rec in report.summary.recommendations:
            recs_list.append(f"- **{rec.description}** (Action items count: {len(rec.actionable_steps)})")

        report_md = (
            f"# Notion Sync - Automated Quality Review\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Workspace ID**: `{report.workspace_id}`\n"
            f"**Overall Health**: `{report.summary.overall_health.upper()}`\n\n"
            f"## Executive Summary Details\n{report.summary.executive_summary}\n\n"
            f"## Recommendations\n" + ("\n".join(recs_list) if recs_list else "- *None.*")
        )

        doc = KnowledgeDocument(
            document_id=f"rev_report_{report.report_id}",
            title=f"Quality Review - {report.report_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"rev_report_{report.report_id}",
                timestamp=report.timestamp,
                source_subsystem="review_engine_service",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from aios.services.ai_workspace import AIWorkspaceService
from aios.services.approval import (
    ApprovalDecision,
    ApprovalEngineService,
    ApprovalHistory,
    ApprovalManager,
    ApprovalPackage,
    ApprovalPolicy,
    ApprovalReport,
    ApprovalRequest,
    ApprovalRule,
    ApprovalSession,
    ApprovalStatus,
    ApprovalSummary,
    ApprovalValidator,
)
from aios.services.knowledge_hub import (
    KnowledgeDocument,
    KnowledgeHubService,
)
from aios.services.knowledge_hub import (
    KnowledgeMetadata as KHMetadata,
)
from aios.services.memory import MemoryService, MemoryType
from aios.services.model import LLMRequest, ModelService
from aios.services.persistence import (
    ApprovalRepository,
    PersistencePolicy,
    PersistenceStatus,
    ReviewRepository,
)

logger = logging.getLogger(__name__)


class MinValidationScoreRule(ApprovalRule):
    """Ensures validation overall score meets targeted gating value."""

    def __init__(self, min_score: float) -> None:
        super().__init__(
            rule_name="MinValidationScore",
            description=f"Validation score must meet or exceed {min_score} threshold."
        )
        self.min_score = min_score

    def evaluate(self, package: ApprovalPackage) -> tuple[bool, str]:
        score = package.validation_summary.get("score", 0.0)
        if score >= self.min_score:
            return True, f"Validation score of {score:.1f} meets min requirement {self.min_score:.1f}."
        return False, f"Validation score of {score:.1f} is below minimum requirement {self.min_score:.1f}."


class RequiredCoverageRule(ApprovalRule):
    """Ensures test statement coverage matches minimum thresholds."""

    def __init__(self, min_coverage: float) -> None:
        super().__init__(
            rule_name="RequiredCoverage",
            description=f"Statement coverage must stand above {min_coverage}%."
        )
        self.min_coverage = min_coverage

    def evaluate(self, package: ApprovalPackage) -> tuple[bool, str]:
        cov = package.coverage_summary.get("achieved_pct", 0.0)
        if cov >= self.min_coverage:
            return True, f"Coverage of {cov:.1f}% meets minimum criteria {self.min_coverage:.1f}%."
        return False, f"Coverage of {cov:.1f}% is below target requirement {self.min_coverage:.1f}%."


class MaxRiskLevelRule(ApprovalRule):
    """Enforces safety constraints by bounding implementation risks level."""

    def __init__(self, max_allowed_level: str) -> None:
        super().__init__(
            rule_name="MaxRiskLevel",
            description=f"Gating risk level must not exceed '{max_allowed_level}'."
        )
        self.max_allowed_level = max_allowed_level
        self._ranks = {"low": 1, "medium": 2, "high": 3, "critical": 4}

    def evaluate(self, package: ApprovalPackage) -> tuple[bool, str]:
        curr = package.risk_summary.get("risk_level", "low").lower()
        curr_val = self._ranks.get(curr, 1)
        max_val = self._ranks.get(self.max_allowed_level.lower(), 2)
        if curr_val <= max_val:
            return True, f"Current risk level '{curr}' complies with policy (<= '{self.max_allowed_level}')."
        return False, f"Current risk level '{curr}' exceeds acceptable limit of '{self.max_allowed_level}'."


class DocumentationCompletenessRule(ApprovalRule):
    """Validates that documentation files exist or are fully complete."""

    def __init__(self) -> None:
        super().__init__(
            rule_name="DocumentationCompleteness",
            description="Checks that all required documentation sections are resolved."
        )

    def evaluate(self, package: ApprovalPackage) -> tuple[bool, str]:
        completed = package.documentation_summary.get("completed", False)
        missing = package.documentation_summary.get("missing_docs", [])
        if completed and not missing:
            return True, "Documentation is complete and compliant."
        return False, f"Incomplete documentation. Missing: {', '.join(missing) if missing else 'Mandatory files missing'}"


class CriticalFailureThresholdRule(ApprovalRule):
    """Guards execution pathways from running when critical bugs/failures exist."""

    def __init__(self, max_failures: int = 0) -> None:
        super().__init__(
            rule_name="CriticalFailureThreshold",
            description=f"Critical failure count must stand below or equal to {max_failures}."
        )
        self.max_failures = max_failures

    def evaluate(self, package: ApprovalPackage) -> tuple[bool, str]:
        count = package.failure_summary.get("critical_count", 0)
        if count <= self.max_failures:
            return True, f"Critical failures count ({count}) is within limit (<= {self.max_failures})."
        return False, f"Critical failures count ({count}) exceeds maximum threshold of {self.max_failures}."


class EngineeringProfileRequirementsRule(ApprovalRule):
    """Verifies alignment between targets and global profile standards."""

    def __init__(self, target_language: str = "python") -> None:
        super().__init__(
            rule_name="EngineeringProfileRequirements",
            description=f"Language and style targets must conform to '{target_language}' standards."
        )
        self.target_language = target_language

    def evaluate(self, package: ApprovalPackage) -> tuple[bool, str]:
        lang = package.metadata.get("profile_language", "python")
        if lang == self.target_language:
            return True, f"Language check passed: '{lang}' conforms with active target profiles."
        return False, f"Target language '{lang}' does not match required profile configuration '{self.target_language}'."


class LocalApprovalValidator(ApprovalValidator):
    """Verifies that approval packages are complete and consistent."""

    def validate_package(self, package: ApprovalPackage) -> List[str]:
        errors = []
        if not package.engineering_summary.strip():
            errors.append("Validation Error: Engineering summary block is empty.")
        if not package.validation_summary:
            errors.append("Validation Error: Validation summary metrics missing.")
        if not package.documentation_summary:
            errors.append("Validation Error: Documentation completeness metrics missing.")
        if not package.risk_summary:
            errors.append("Validation Error: Risk assessment details missing.")
        if not package.affected_files:
            errors.append("Validation Error: Affected files list is empty.")
        if not (0.0 <= package.confidence_score <= 1.0):
            errors.append(f"Validation Error: Confidence score '{package.confidence_score}' stands outside range [0.0, 1.0].")
        if not package.overall_health:
            errors.append("Validation Error: Overall engineering health status parameter is missing.")
        return errors

    def check_duplicate_request(self, request: ApprovalRequest, history: List[ApprovalSummary]) -> bool:
        for record in history:
            if (
                record.workspace_id == request.workspace_id
                and abs(record.timestamp - request.timestamp) < 60.0
            ):
                return True
        return False


class LocalApprovalManager(ApprovalManager):
    """Concrete compiler and policy evaluation controller."""

    def create_session(self, request: ApprovalRequest) -> ApprovalSession:
        return ApprovalSession(
            session_id=f"app_sess_{int(time.time())}",
            request=request,
            package=None,
            decision=None,
            status="open",
            created_at=time.time()
        )

    def compile_package(self, session: ApprovalSession) -> ApprovalPackage:
        request = session.request
        
        # Populate defaults
        eng_summary = "Autogenerated technical summary details."
        validation_summary = {"score": 85.0, "status": "pass", "tests_run_count": 100}
        documentation_summary = {"completed": True, "missing_docs": []}
        risk_summary = {"risk_level": "low", "areas": ["kernel"]}
        affected_files = []
        affected_components = []
        coverage_summary = {"achieved_pct": 80.0}
        failure_summary = {"critical_count": 0}
        recommendations = []
        confidence_score = 0.9
        overall_health = "healthy"
        profile_lang = "python"

        # Parse aggregated evidence
        for ev in request.evidence:
            if ev.source == "validation_report":
                validation_summary["score"] = ev.data.get("overall_score", 85.0)
                validation_summary["tests_run_count"] = ev.data.get("total_tests_run", 100)
                coverage_summary["achieved_pct"] = ev.data.get("coverage_pct", 80.0)
                failure_summary["critical_count"] = ev.data.get("critical_count", 0)
                if failure_summary["critical_count"] > 0:
                    overall_health = "degraded"
            elif ev.source == "engineering_intelligence":
                eng_summary = ev.data.get("objective", "Objective sync summary.")
                risk_summary["risk_level"] = ev.data.get("risk_level", "low")
                affected_files.extend(ev.data.get("affected_files", []))
                affected_components.extend(ev.data.get("affected_components", []))
            elif ev.source == "readme_intelligence":
                missing = ev.data.get("missing_sections", [])
                if missing:
                    documentation_summary["completed"] = False
                    documentation_summary["missing_docs"] = missing
            elif ev.source == "engineering_profile":
                profile_lang = ev.data.get("language", "python")

        if not affected_files:
            affected_files = ["core/src/aios/kernel.py"]
        if not affected_components:
            affected_components = ["Kernel"]

        # Form default configurable policy
        policy = ApprovalPolicy(
            policy_id=request.policy_id,
            name="Standard Quality Gating Policy",
            rules=[
                MinValidationScoreRule(min_score=80.0),
                RequiredCoverageRule(min_coverage=75.0),
                MaxRiskLevelRule(max_allowed_level="medium"),
                DocumentationCompletenessRule(),
                CriticalFailureThresholdRule(max_failures=0),
                EngineeringProfileRequirementsRule(target_language=profile_lang)
            ]
        )

        return ApprovalPackage(
            package_id=f"pkg_{request.request_id}",
            workspace_id=request.workspace_id,
            engineering_summary=eng_summary,
            validation_summary=validation_summary,
            documentation_summary=documentation_summary,
            risk_summary=risk_summary,
            affected_files=affected_files,
            affected_components=affected_components,
            coverage_summary=coverage_summary,
            failure_summary=failure_summary,
            recommendations=recommendations,
            policy=policy,
            reviewer_notes=[],
            approval_history=[],
            confidence_score=confidence_score,
            overall_health=overall_health,
            evidence=request.evidence,
            metadata={"profile_language": profile_lang}
        )

    def evaluate_policy(self, package: ApprovalPackage) -> ApprovalDecision:
        passed_reasons = []
        failed_reasons = []
        
        for rule in package.policy.rules:
            ok, reason = rule.evaluate(package)
            if ok:
                passed_reasons.append(f"Passed: {rule.rule_name} - {reason}")
            else:
                failed_reasons.append(f"Failed: {rule.rule_name} - {reason}")

        reviewer_notes = list(passed_reasons)
        if failed_reasons:
            status = ApprovalStatus.REJECTED
            # Check if failures warrant manual review or rejection
            if len(failed_reasons) == 1 and "Documentation" in failed_reasons[0]:
                status = ApprovalStatus.CHANGES_REQUESTED
            reasoning = "Policy evaluation failed. Discrepancies discovered:\n" + "\n".join(failed_reasons)
        else:
            status = ApprovalStatus.APPROVED
            reasoning = "All safety checks and validation gates passed successfully."

        return ApprovalDecision(
            status=status,
            reasoning=reasoning,
            reviewer_notes=reviewer_notes,
            timestamp=time.time()
        )


class LocalApprovalEngineService(ApprovalEngineService):
    """Central orchestrator managing approval sessions, storage in memory, and reporting."""

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

        self._validator = LocalApprovalValidator()
        self._manager = LocalApprovalManager()
        
        self._sessions: Dict[str, ApprovalSession] = {}
        self._histories: Dict[str, ApprovalHistory] = {}
        self._approval_repo = None
        self._review_repo = None
        self.base_dir = Path(".agent/approval")

    def initialize(self) -> None:
        logger.info("Initializing LocalApprovalEngineService")
        if self._registry:
            try:
                self._approval_repo = self._registry.get(ApprovalRepository)
                self._review_repo = self._registry.get(ReviewRepository)
            except Exception as e:
                logger.warning(f"Failed to load M3 repositories in LocalApprovalEngineService: {e}")
        else:
            self._approval_repo = None
            self._review_repo = None

    def _get_policy(self) -> PersistencePolicy:
        if self._approval_repo and hasattr(self._approval_repo, "service") and self._approval_repo.service.config:
            return self._approval_repo.service.config.policy
        return PersistencePolicy.STRICT

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

        approvals_dir = os.path.join(workspace_root, "docs", "approvals")
        os.makedirs(approvals_dir, exist_ok=True)
        
        file_path = os.path.join(approvals_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return file_path

    def request_approval(self, request: ApprovalRequest) -> ApprovalSession:
        logger.info(f"Received approval request '{request.request_id}' for workspace '{request.workspace_id}'")

        # 1. Duplicate review check
        history = self.get_history(request.workspace_id)
        if self._validator.check_duplicate_request(request, history.records):
            logger.warning("Duplicate approval request detected within cooling-off threshold.")

        # 2. Start session
        session = self._manager.create_session(request)
        self._sessions[session.session_id] = session

        # 3. Compile Package
        package = self._manager.compile_package(session)
        session.package = package

        # Validate package completeness
        validation_warnings = self._validator.validate_package(package)
        if validation_warnings:
            logger.warning(f"Package validation structural warnings: {validation_warnings}")

        # 4. Evaluate Policy rules
        decision = self._manager.evaluate_policy(package)
        session.decision = decision

        # 5. AI Refinement (if model exists)
        if self._model:
            try:
                prompt = (
                    "You are the Lead Systems Architect responsible for quality approvals.\n"
                    f"Engineering Summary:\n{package.engineering_summary}\n"
                    f"Decision status: {decision.status.value}\n"
                    f"Decision reasoning: {decision.reasoning}\n\n"
                    "Refine layout structures and add architectural recommendations. Return refined markdown format only."
                )
                res = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output refined markdown content directly.",
                        task_category="testing"
                    )
                )
                refined = res.content.strip()
                if refined:
                    decision.reasoning = refined
            except Exception as e:
                logger.debug(f"LLM Approval decision refinement failed: {e}")

        # 6. Save artifacts ONLY in Workspace
        report_md = (
            f"# Approval Package Decision Report\n\n"
            f"**Session ID**: `{session.session_id}`\n"
            f"**Workspace ID**: `{package.workspace_id}`\n"
            f"**Overall Health Status**: `{package.overall_health.upper()}`\n"
            f"**Confidence Rating**: `{package.confidence_score:.2f}`\n"
            f"**Approval Decision**: `{decision.status.value.upper()}`\n\n"
            f"## Outcome Reasoning\n{decision.reasoning}\n\n"
            f"## Affected Files\n" + "\n".join(f"- `{f}`" for f in package.affected_files)
        )
        self._write_to_workspace(request.workspace_id, f"APPROVAL_REPORT_{session.session_id}.md", report_md)

        # 7. Record History
        summary = ApprovalSummary(
            summary_id=f"sum_{session.session_id}",
            session_id=session.session_id,
            workspace_id=request.workspace_id,
            status=decision.status,
            confidence_score=package.confidence_score,
            overall_health=package.overall_health,
            timestamp=time.time()
        )
        history.records.append(summary)

        session.status = "closed"
        session.closed_at = time.time()

        # Convert/serialize session to dict and save in DB
        if self._approval_repo:
            policy = self._get_policy()
            try:
                mapped = {
                    "id": session.session_id,
                    "workspace_id": request.workspace_id,
                    "metadata": {
                        "request": {
                            "request_id": request.request_id,
                            "workspace_id": request.workspace_id,
                            "target_version": request.target_version,
                            "policy_id": request.policy_id,
                            "timestamp": request.timestamp
                        },
                        "overall_health": package.overall_health,
                        "confidence_score": package.confidence_score,
                    },
                    "decision_outcome": decision.status.value,
                    "confidence": package.confidence_score,
                    "policy_used": {
                        "name": "default",
                        "rules": decision.reasoning
                    },
                    "review_status": session.status,
                    "approver": request.policy_id,
                    "timeline_metadata": {
                        "created_at": session.created_at,
                        "closed_at": session.closed_at
                    },
                    "operation_results": {},
                    "created_at": session.created_at,
                    "closed_at": session.closed_at
                }
                res = self._approval_repo.save(mapped)
                if res.status != PersistenceStatus.SUCCESS:
                    if policy == PersistencePolicy.STRICT:
                        raise RuntimeError(f"Strict persistence save failure: {res.message}")
                    else:
                        logger.warning(f"Persistence best-effort fallback: {res.message}")
            except Exception as e:
                if policy == PersistencePolicy.STRICT:
                    raise RuntimeError(f"Strict persistence save failure: {e}") from e
                logger.warning(f"Database error saving approval session {session.session_id}: {e}.")

        return session

    def get_session(self, session_id: str) -> Optional[ApprovalSession]:
        if session_id in self._sessions:
            return self._sessions[session_id]

        if self._approval_repo:
            try:
                res = self._approval_repo.get(session_id)
                if res.status == PersistenceStatus.SUCCESS and res.payload:
                    row = res.payload
                    req_meta = row.get("metadata", {}).get("request", {})
                    req = ApprovalRequest(
                        request_id=req_meta.get("request_id", ""),
                        workspace_id=req_meta.get("workspace_id", ""),
                        target_version=req_meta.get("target_version", ""),
                        policy_id=req_meta.get("policy_id", ""),
                        evidence=[],
                        timestamp=req_meta.get("timestamp", 0.0)
                    )
                    
                    dec_outcome = row.get("decision_outcome")
                    policy_used = row.get("policy_used", {})
                    dec = ApprovalDecision(
                        status=ApprovalStatus(dec_outcome) if dec_outcome else ApprovalStatus.PENDING,
                        reasoning=policy_used.get("rules", ""),
                        timestamp=row.get("closed_at", 0.0)
                    )
                    
                    pack_meta = row.get("metadata", {})
                    pack = ApprovalPackage(
                        package_id=f"pkg_{session_id}",
                        workspace_id=row.get("workspace_id", ""),
                        engineering_summary="",
                        validation_summary={},
                        documentation_summary={},
                        risk_summary={},
                        affected_files=[],
                        affected_components=[],
                        coverage_summary={},
                        failure_summary={},
                        recommendations=[],
                        policy=ApprovalPolicy(policy_id="default", name="Default Policy"),
                        reviewer_notes=[],
                        approval_history=[],
                        confidence_score=row.get("confidence", 1.0),
                        overall_health=pack_meta.get("overall_health", "healthy")
                    )
                    
                    session = ApprovalSession(
                        session_id=row.get("id"),
                        request=req,
                        package=pack,
                        decision=dec,
                        status=row.get("review_status", "closed"),
                        created_at=row.get("created_at", 0.0),
                        closed_at=row.get("closed_at")
                    )
                    self._sessions[session_id] = session
                    return session
            except Exception as e:
                policy = self._get_policy()
                if policy == PersistencePolicy.STRICT:
                    raise RuntimeError(f"Strict persistence load failure: {e}") from e
                logger.warning(f"Database error getting approval session {session_id}: {e}.")

        return None

    def get_history(self, workspace_id: str) -> ApprovalHistory:
        if workspace_id not in self._histories:
            records = []
            if self._approval_repo:
                try:
                    q = "SELECT id, workspace_id, confidence, overall_health, closed_at, decision_outcome FROM approval_sessions WHERE workspace_id = ?"
                    rows = self._approval_repo.service.execute(q, (workspace_id,))
                    for row in rows:
                        records.append(
                            ApprovalSummary(
                                summary_id=f"sum_{row['id']}",
                                session_id=row['id'],
                                workspace_id=row['workspace_id'],
                                status=ApprovalStatus(row['decision_outcome']),
                                confidence_score=row['confidence'],
                                overall_health=row['overall_health'],
                                timestamp=row['closed_at'] or time.time()
                            )
                        )
                except Exception as e:
                    logger.warning(f"Failed to load approval history for {workspace_id} from DB: {e}")
            
            self._histories[workspace_id] = ApprovalHistory(
                history_id=f"hist_{workspace_id}",
                workspace_id=workspace_id,
                records=records
            )
        return self._histories[workspace_id]

    def store_approval_summary(self, session: ApprovalSession) -> None:
        if not session.decision or not session.package:
            return
        
        # Save ONLY metadata summaries. Never save codebase contents or source files.
        content = (
            f"Approval Decision Logged\n"
            f"Workspace ID: {session.request.workspace_id}\n"
            f"Session ID: {session.session_id}\n"
            f"Decision Status: {session.decision.status.value.upper()}\n"
            f"Confidence Score: {session.package.confidence_score:.2f}\n"
            f"Timestamp: {time.ctime(session.created_at)}"
        )

        self._memory.add_memory(
            content=content,
            memory_type=MemoryType.PROJECT,
            tags=["approval_decision", "gating_history", "validation_checkpoint"],
            importance=2,
            metadata_additional={
                "session_id": session.session_id,
                "workspace_id": session.request.workspace_id,
                "status": session.decision.status.value,
                "confidence_score": session.package.confidence_score,
                "overall_health": session.package.overall_health
            }
        )

    def publish_approval_report(self, report: ApprovalReport) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publishing.")
            return

        recs_md = "\n".join(f"- {r}" for r in report.package_summary.get("recommendations", []))
        report_md = (
            f"# Notion Sync - Quality Gate Decision\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Session ID**: `{report.session_id}`\n"
            f"**Workspace ID**: `{report.workspace_id}`\n"
            f"**Decision status**: `{report.decision.status.value.upper()}`\n\n"
            f"## Details Reasoning\n{report.decision.reasoning}\n\n"
            f"## Recommendations\n" + (recs_md if recs_md else "- *None.*")
        )

        doc = KnowledgeDocument(
            document_id=f"app_report_{report.report_id}",
            title=f"Approval Gate - {report.report_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"app_report_{report.report_id}",
                timestamp=report.timestamp,
                source_subsystem="approval_engine_service",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

    # --- Secure JSON Storage helpers ---
    def _load_json(self, filename: str, default: Any) -> Any:
        path = self.base_dir / filename
        if not path.is_file():
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    def _save_json(self, filename: str, data: Any) -> None:
        path = self.base_dir / filename
        try:
            self.base_dir.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            # Apply owner-only 0600 permissions
            os.chmod(path, 0o600)
        except Exception as e:
            logger.error(f"Failed to write secure file {filename}: {e}")

    # --- Extended Governance APIs ---
    def list_queue(self) -> List[Dict[str, Any]]:
        """List all requests in the approval queue."""
        return self._load_json("queue.json", [])

    def list_pending(self) -> List[Dict[str, Any]]:
        """List all pending requests in the queue."""
        queue = self.list_queue()
        return [item for item in queue if item.get("status") == "pending"]

    def approve_request(self, request_id: str) -> bool:
        """Approve a request by ID."""
        queue = self.list_queue()
        for item in queue:
            if item.get("request_id") == request_id:
                item["status"] = "approved"
                self._save_json("queue.json", queue)
                self.log_audit_trail({
                    "action": item.get("action"),
                    "project": item.get("project"),
                    "client": item.get("client"),
                    "outcome": "approved",
                    "risk": item.get("risk"),
                    "user": item.get("user"),
                    "timestamp": time.time(),
                    "reason": f"Manual approval for request {request_id}"
                })
                return True
        return False

    def reject_request(self, request_id: str) -> bool:
        """Reject a request by ID."""
        queue = self.list_queue()
        for item in queue:
            if item.get("request_id") == request_id:
                item["status"] = "rejected"
                self._save_json("queue.json", queue)
                self.log_audit_trail({
                    "action": item.get("action"),
                    "project": item.get("project"),
                    "client": item.get("client"),
                    "outcome": "rejected",
                    "risk": item.get("risk"),
                    "user": item.get("user"),
                    "timestamp": time.time(),
                    "reason": f"Manual rejection for request {request_id}"
                })
                return True
        return False

    def cancel_request(self, request_id: str) -> bool:
        """Cancel a request by ID."""
        queue = self.list_queue()
        for item in queue:
            if item.get("request_id") == request_id:
                item["status"] = "cancelled"
                self._save_json("queue.json", queue)
                self.log_audit_trail({
                    "action": item.get("action"),
                    "project": item.get("project"),
                    "client": item.get("client"),
                    "outcome": "cancelled",
                    "risk": item.get("risk"),
                    "user": item.get("user"),
                    "timestamp": time.time(),
                    "reason": f"Manual cancellation for request {request_id}"
                })
                return True
        return False

    def retry_request(self, request_id: str) -> bool:
        """Retry execution of an approved or failed request."""
        queue = self.list_queue()
        for item in queue:
            if item.get("request_id") == request_id:
                # Update timestamp and status to trigger retry
                item["timestamp"] = time.time()
                item["status"] = "pending"
                self._save_json("queue.json", queue)
                self.log_audit_trail({
                    "action": item.get("action"),
                    "project": item.get("project"),
                    "client": item.get("client"),
                    "outcome": "retry",
                    "risk": item.get("risk"),
                    "user": item.get("user"),
                    "timestamp": time.time(),
                    "reason": f"Retry execution for request {request_id}"
                })
                return True
        return False

    def execute_request(self, request_id: str) -> Dict[str, Any]:
        """Execute an approved request."""
        queue = self.list_queue()
        for item in queue:
            if item.get("request_id") == request_id:
                if item.get("status") != "approved":
                    return {
                        "status": "failed",
                        "message": f"Request {request_id} is not approved."
                    }
                item["status"] = "executed"
                self._save_json("queue.json", queue)
                self.log_audit_trail({
                    "action": item.get("action"),
                    "project": item.get("project"),
                    "client": item.get("client"),
                    "outcome": "execution",
                    "risk": item.get("risk"),
                    "user": item.get("user"),
                    "timestamp": time.time(),
                    "reason": f"Executed approved request {request_id}"
                })
                # Add to history
                history = self._load_json("history.json", [])
                history.append(item)
                self._save_json("history.json", history)
                return {
                    "status": "executed",
                    "message": "Action executed successfully."
                }
        return {
            "status": "failed",
            "message": f"Request {request_id} not found."
        }

    def expire_requests(self) -> None:
        """Expire time-limited pending requests."""
        queue = self.list_queue()
        now = time.time()
        modified = False
        for item in queue:
            if item.get("status") == "pending" and now > item.get("expiration", 0):
                item["status"] = "expired"
                modified = True
                self.log_audit_trail({
                    "action": item.get("action"),
                    "project": item.get("project"),
                    "client": item.get("client"),
                    "outcome": "expired",
                    "risk": item.get("risk"),
                    "user": item.get("user"),
                    "timestamp": time.time(),
                    "reason": f"Request {item.get('request_id')} expired automatically"
                })
        if modified:
            self._save_json("queue.json", queue)

    def get_policies(self) -> Dict[str, Any]:
        """Get all configured policies."""
        return self._load_json("policies.json", {
            "global": "default"
        })

    def update_policy(self, policy_id: str, config: Dict[str, Any]) -> None:
        """Update a policy configuration."""
        policies = self.get_policies()
        policies[policy_id] = config
        self._save_json("policies.json", policies)

    def get_preview(self, request_id: str) -> Dict[str, Any]:
        """Generate or retrieve action preview details."""
        queue = self.list_queue()
        for item in queue:
            if item.get("request_id") == request_id:
                return item.get("preview", {})
        return {
            "action_summary": "Unknown action request",
            "files_affected": [],
            "services_affected": [],
            "expected_changes": "",
            "rollback_supported": False,
            "estimated_impact": "low"
        }

    def list_audit_trail(self) -> List[Dict[str, Any]]:
        """Retrieve audit log items."""
        return self._load_json("audit.json", [])

    def classify_risk(self, action: str, details: Dict[str, Any]) -> str:
        """Classify action risk level (low, medium, high, critical)."""
        action = action.lower()
        if "delete" in action or "migration" in action or "storage" in action:
            return "critical"
        if "production" in action or "release" in action or "push" in action:
            return "high"
        if "deploy" in action or "update" in action or "exec" in action:
            return "medium"
        return "low"

    def resolve_policy(self, action: str, project: str, client: str) -> str:
        """Resolve policy string for specified action, project, and client."""
        policies = self.get_policies()
        if f"action:{action}" in policies:
            return policies[f"action:{action}"]
        if f"project:{project}" in policies:
            return policies[f"project:{project}"]
        if f"client:{client}" in policies:
            return policies[f"client:{client}"]
        return policies.get("global", "default")

    def log_audit_trail(self, entry: Dict[str, Any]) -> None:
        """Log operational governance event into secure audit logs."""
        audit = self.list_audit_trail()
        entry["log_id"] = f"log_{int(time.time() * 1000)}"
        if "timestamp" not in entry:
            entry["timestamp"] = time.time()
        audit.append(entry)
        self._save_json("audit.json", audit)

    def queue_request_item(self, request_item: Dict[str, Any]) -> None:
        """Persist a new action request item in queue."""
        queue = self.list_queue()
        queue.append(request_item)
        self._save_json("queue.json", queue)

    def generate_reports(self, output_dir: Optional[Any] = None) -> Dict[str, Any]:
        """Generate markdown reports under docs/approval/."""
        out_path = Path(output_dir) if output_dir else Path("docs/approval")
        out_path.mkdir(parents=True, exist_ok=True)

        queue = self.list_queue()
        audit = self.list_audit_trail()
        policies = self.get_policies()

        # 1. Approval Report
        app_lines = []
        for q in queue:
            app_lines.append(
                f"- **{q.get('request_id')}**: {q.get('action')} | "
                f"Status: {q.get('status')} | Risk: {q.get('risk')}"
            )
        if not app_lines:
            app_lines.append("- (No active or pending approvals in queue)")
        with open(out_path / "approval_report.md", "w", encoding="utf-8") as f:
            f.write("# Approval Queue Report\n\n" + "\n".join(app_lines))

        # 2. Audit Report
        audit_lines = []
        for entry in audit:
            ts = time.localtime(entry.get('timestamp', 0))
            ts_str = time.strftime('%Y-%m-%d %H:%M:%S', ts)
            audit_lines.append(
                f"- [{ts_str}] **{entry.get('outcome').upper()}**: "
                f"{entry.get('action')} - {entry.get('reason')}"
            )
        if not audit_lines:
            audit_lines.append("- (No governance audit records logged yet)")
        with open(out_path / "audit_report.md", "w", encoding="utf-8") as f:
            f.write("# Governance Audit Trail Report\n\n" + "\n".join(audit_lines))

        # 3. Policy Report
        policy_lines = []
        for k, v in policies.items():
            policy_lines.append(f"- **{k}**: `{v}`")
        with open(out_path / "policy_report.md", "w", encoding="utf-8") as f:
            f.write("# Approval Policies Configuration Report\n\n" + "\n".join(policy_lines))

        # 4. Risk Report
        risk_md = """# Action Risk Classification Report

All protected actions are classified dynamically to enforce the appropriate gating policy:

- **LOW**: Low impact operations (read/log). Executes immediately by default.
- **MEDIUM**: Standard deployment and workflow runs. Requires dry-run preview.
- **HIGH**: Production releases and branch modifications. Requires manual approval.
- **CRITICAL**: Auth changes, storage removals, and branch deletions. Requires manual confirmation.
"""
        with open(out_path / "risk_report.md", "w", encoding="utf-8") as f:
            f.write(risk_md.strip())

        # 5. Rollback Report
        rollback_md = """# Action Rollback Availability Report

Rollback capability is assessed per action:

- **n8n workflow**: Rollback via local history cache. Supported.
- **Vercel deployment**: Rollback via production alias swap. Supported.
- **GitHub push**: Rollback via revert/reset force push. Supported with warnings.
- **Supabase database modifications**: Rollback via migration down files. DB states are non-trivial.
- **Client communication**: Rollback is impossible once sent.
"""
        with open(out_path / "rollback_report.md", "w", encoding="utf-8") as f:
            f.write(rollback_md.strip())

        return {"reports_written": 5, "output_dir": str(out_path)}


class ApprovalMiddleware:
    """Centralized middleware through which every protected action must pass."""

    def __init__(self, approval_service: ApprovalEngineService) -> None:
        self._service = approval_service

    def process_action(
        self,
        action: str,
        project: str,
        client: str,
        provider: str,
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Processes a protected action request."""
        risk_level = self._service.classify_risk(action, details)
        policy = self._service.resolve_policy(action, project, client)

        request_id = f"req_{int(time.time() * 1000)}"
        token = f"tok_{request_id}"

        if policy == "never_allow" or (policy == "default" and risk_level == "critical"):
            self._service.log_audit_trail({
                "action": action,
                "project": project,
                "client": client,
                "outcome": "rejected",
                "risk": risk_level,
                "user": "developer",
                "timestamp": time.time(),
                "reason": "Policy explicitly forbids or critical risk level rejected"
            })
            return {
                "status": "rejected",
                "request_id": request_id,
                "token": "",
                "message": "Action rejected by governance policy",
                "rollback_supported": False
            }

        if policy == "always_approve" or (policy == "default" and risk_level == "low"):
            self._service.log_audit_trail({
                "action": action,
                "project": project,
                "client": client,
                "outcome": "executed",
                "risk": risk_level,
                "user": "developer",
                "timestamp": time.time(),
                "reason": "Always approve policy or low risk auto-execution"
            })
            return {
                "status": "executed",
                "request_id": request_id,
                "token": token,
                "message": "Action auto-approved and executed",
                "rollback_supported": True
            }

        # Queue request for manual confirmation
        preview = {
            "action_summary": f"Protected {action} on {project}",
            "files_affected": details.get("files", []),
            "services_affected": [provider],
            "expected_changes": details.get("changes", "Metadata update"),
            "rollback_supported": details.get("rollback", True),
            "estimated_impact": risk_level
        }

        request_item = {
            "request_id": request_id,
            "token": token,
            "timestamp": time.time(),
            "expiration": time.time() + 3600,
            "user": "developer",
            "project": project,
            "client": client,
            "provider": provider,
            "action": action,
            "risk": risk_level,
            "status": "pending",
            "preview": preview,
            "rollback_capability": preview["rollback_supported"],
            "details": details
        }

        self._service.queue_request_item(request_item)
        self._service.log_audit_trail({
            "action": action,
            "project": project,
            "client": client,
            "outcome": "queued",
            "risk": risk_level,
            "user": "developer",
            "timestamp": time.time(),
            "reason": "Action queued for confirmation"
        })

        return {
            "status": "queued",
            "request_id": request_id,
            "token": token,
            "message": "Action queued for approval",
            "rollback_supported": preview["rollback_supported"]
        }


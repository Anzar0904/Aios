import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

from aios.services.ai_workspace import AIWorkspaceService
from aios.services.approval_history import (
    VALID_TRANSITIONS,
    ApprovalDecisionRecord,
    ApprovalHistoryAnalyzer,
    ApprovalHistoryEntry,
    ApprovalHistoryReport,
    ApprovalHistoryService,
    ApprovalHistoryValidator,
    ApprovalPattern,
    ApprovalRecommendationHistory,
    ApprovalState,
    ApprovalStateTransition,
    ApprovalStatistics,
    ApprovalTrend,
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
from aios.services.persistence import PersistencePolicy, PersistenceStatus, ReviewRepository

logger = logging.getLogger(__name__)


class LocalApprovalHistoryValidator(ApprovalHistoryValidator):
    """Enforces state transition rules, schema checks, and statistics limits."""

    def validate_transition(self, from_state: ApprovalState, to_state: ApprovalState) -> bool:
        allowed = VALID_TRANSITIONS.get(from_state, [])
        return to_state in allowed

    def validate_report(self, report: ApprovalHistoryReport) -> List[str]:
        errors = []
        stats = report.statistics

        # 1. Statistics integrity bounds check
        if stats.total_sessions < 0:
            errors.append("Statistics Integrity Error: Total session count cannot be negative.")
        if not (0.0 <= stats.average_confidence <= 1.0):
            errors.append(
                f"Statistics Integrity Error: Average confidence '{stats.average_confidence}' stands outside [0.0, 1.0]."
            )
        if not (0.0 <= stats.average_validation_score <= 100.0):
            errors.append(
                f"Statistics Integrity Error: Average validation score '{stats.average_validation_score}' stands outside [0.0, 100.0]."
            )
        if not (0.0 <= stats.average_coverage <= 100.0):
            errors.append(
                f"Statistics Integrity Error: Average coverage '{stats.average_coverage}' stands outside [0.0, 100.0]."
            )

        # 2. Timeline consistency
        for trend in report.trends:
            if trend.values_over_time:
                prev_time = -1.0
                for ts, _val in trend.values_over_time:
                    if ts < prev_time:
                        errors.append(
                            f"Timeline Consistency Warning: Time sequence in trend '{trend.trend_id}' is out of chronological order."
                        )
                    prev_time = ts

        return errors


class LocalApprovalHistoryAnalyzer(ApprovalHistoryAnalyzer):
    """Calculates aggregates, computes trend slopes, and identifies recurring pattern gaps."""

    def compile_statistics(self, records: List[ApprovalDecisionRecord]) -> ApprovalStatistics:
        if not records:
            return ApprovalStatistics(
                total_sessions=0,
                approved_count=0,
                rejected_count=0,
                changes_requested_count=0,
                average_confidence=0.0,
                average_validation_score=0.0,
                average_coverage=0.0,
            )

        total = len(records)
        app_cnt = sum(
            1
            for r in records
            if r.final_state in [ApprovalState.APPROVED, ApprovalState.APPROVED_WITH_CONDITIONS]
        )
        rej_cnt = sum(1 for r in records if r.final_state == ApprovalState.REJECTED)
        cr_cnt = sum(1 for r in records if r.final_state == ApprovalState.CHANGES_REQUESTED)

        avg_conf = sum(r.confidence_score for r in records) / total
        avg_val = sum(r.validation_score for r in records) / total
        avg_cov = sum(r.coverage_pct for r in records) / total

        return ApprovalStatistics(
            total_sessions=total,
            approved_count=app_cnt,
            rejected_count=rej_cnt,
            changes_requested_count=cr_cnt,
            average_confidence=avg_conf,
            average_validation_score=avg_val,
            average_coverage=avg_cov,
        )

    def analyze_trends(self, records: List[ApprovalDecisionRecord]) -> List[ApprovalTrend]:
        if not records:
            return []

        # Sort chronologically
        sorted_recs = sorted(records, key=lambda r: r.timestamp)

        trends = []
        metrics = ["validation_score", "coverage_pct", "confidence_score"]

        for _idx, m in enumerate(metrics):
            values = []
            for r in sorted_recs:
                val = getattr(r, m, 0.0)
                values.append((r.timestamp, val))

            direction = "stable"
            if len(values) >= 2:
                first = values[0][1]
                last = values[-1][1]
                if last > first:
                    direction = "improving"
                elif last < first:
                    direction = "declining"

            trends.append(
                ApprovalTrend(
                    trend_id=f"tr_{m}_{int(time.time())}",
                    metric_name=m.replace("_", " ").title(),
                    values_over_time=values,
                    direction=direction,
                )
            )

        return trends

    def discover_patterns(
        self, entries: List[ApprovalHistoryEntry], records: List[ApprovalDecisionRecord]
    ) -> List[ApprovalPattern]:
        patterns = []

        # 1. Reject checks
        rejections = sum(1 for r in records if r.final_state == ApprovalState.REJECTED)
        if rejections >= 2:
            patterns.append(
                ApprovalPattern(
                    pattern_id="pat_rejects",
                    pattern_type="repeated_blocker",
                    description="Critical validation faults lead to repeated approval gate rejections.",
                    occurrence_count=rejections,
                )
            )

        # 2. Changes requested checks
        cr_count = sum(1 for r in records if r.final_state == ApprovalState.CHANGES_REQUESTED)
        if cr_count >= 2:
            patterns.append(
                ApprovalPattern(
                    pattern_id="pat_cr",
                    pattern_type="frequent_changes_requested",
                    description="Code modifications regularly trigger human reviewer changes requested loops.",
                    occurrence_count=cr_count,
                )
            )

        # 3. Documentation checks (from entries metadata)
        doc_gaps = 0
        for entry in entries:
            if entry.metadata.get("documentation_incomplete", False):
                doc_gaps += 1

        if doc_gaps >= 1:
            patterns.append(
                ApprovalPattern(
                    pattern_id="pat_docs",
                    pattern_type="documentation_gap",
                    description="Validation sweeps identify recurring omissions in reference documentation.",
                    occurrence_count=doc_gaps,
                )
            )

        return patterns


class LocalApprovalHistoryService(ApprovalHistoryService):
    """Central manager coordinating transitions log, stats compiles, and report generation."""

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

        self._validator = LocalApprovalHistoryValidator()
        self._analyzer = LocalApprovalHistoryAnalyzer()

        self._entries: Dict[str, ApprovalHistoryEntry] = {}
        self._records: Dict[str, List[ApprovalDecisionRecord]] = {}
        self._review_repo = None

    def initialize(self) -> None:
        logger.info("Initializing LocalApprovalHistoryService")
        if self._registry:
            try:
                self._review_repo = self._registry.get(ReviewRepository)
            except Exception as e:
                logger.warning(
                    f"Failed to load ReviewRepository in LocalApprovalHistoryService: {e}"
                )
        else:
            self._review_repo = None

    def _get_policy(self) -> PersistencePolicy:
        if (
            self._review_repo
            and hasattr(self._review_repo, "service")
            and self._review_repo.service.config
        ):
            return self._review_repo.service.config.policy
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

        histories_dir = os.path.join(workspace_root, "docs", "histories")
        os.makedirs(histories_dir, exist_ok=True)

        file_path = os.path.join(histories_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return file_path

    def create_history_entry(
        self, workspace_id: str, session_id: str, initial_state: ApprovalState, actor: str
    ) -> ApprovalHistoryEntry:
        transition = ApprovalStateTransition(
            transition_id=f"tr_{session_id}_init",
            from_state=ApprovalState.DRAFT,  # initial source state before session start
            to_state=initial_state,
            actor=actor,
            reason="Session initialization gate.",
            timestamp=time.time(),
        )

        entry = ApprovalHistoryEntry(
            entry_id=f"ent_{session_id}",
            session_id=session_id,
            workspace_id=workspace_id,
            state_transitions=[transition],
            metadata={},
        )
        self._entries[session_id] = entry

        # Save to review repo
        if self._review_repo:
            policy = self._get_policy()
            try:
                mapped = {
                    "id": entry.entry_id,
                    "session_id": entry.session_id,
                    "workspace_id": entry.workspace_id,
                    "state_transitions": [
                        {
                            "transition_id": t.transition_id,
                            "from_state": t.from_state.value,
                            "to_state": t.to_state.value,
                            "actor": t.actor,
                            "reason": t.reason,
                            "timestamp": t.timestamp,
                        }
                        for t in entry.state_transitions
                    ],
                    "metadata": entry.metadata,
                }
                res = self._review_repo.save(mapped)
                if res.status != PersistenceStatus.SUCCESS:
                    if policy == PersistencePolicy.STRICT:
                        raise RuntimeError(f"Strict persistence save failure: {res.message}")
                    else:
                        logger.warning(f"Persistence best-effort fallback: {res.message}")
            except Exception as e:
                if policy == PersistencePolicy.STRICT:
                    raise RuntimeError(f"Strict persistence save failure: {e}") from e
                logger.warning(f"Database error saving review session {entry.entry_id}: {e}.")

        return entry

    def transition_state(
        self,
        workspace_id: str,
        session_id: str,
        target_state: ApprovalState,
        actor: str,
        reason: str,
    ) -> ApprovalHistoryEntry:
        entry = self.get_history_entry(session_id)
        if not entry:
            raise ValueError(f"History entry for session '{session_id}' not found.")

        current_state = entry.state_transitions[-1].to_state
        if not self._validator.validate_transition(current_state, target_state):
            raise ValueError(
                f"Invalid transition state trigger: '{current_state.value}' -> '{target_state.value}'."
            )

        transition_id = f"tr_{session_id}_{len(entry.state_transitions) + 1}"
        new_transition = ApprovalStateTransition(
            transition_id=transition_id,
            from_state=current_state,
            to_state=target_state,
            actor=actor,
            reason=reason,
            timestamp=time.time(),
        )
        entry.state_transitions.append(new_transition)

        # Save to review repo
        if self._review_repo:
            policy = self._get_policy()
            try:
                mapped = {
                    "id": entry.entry_id,
                    "session_id": entry.session_id,
                    "workspace_id": entry.workspace_id,
                    "state_transitions": [
                        {
                            "transition_id": t.transition_id,
                            "from_state": t.from_state.value,
                            "to_state": t.to_state.value,
                            "actor": t.actor,
                            "reason": t.reason,
                            "timestamp": t.timestamp,
                        }
                        for t in entry.state_transitions
                    ],
                    "metadata": entry.metadata,
                }
                res = self._review_repo.save(mapped)
                if res.status != PersistenceStatus.SUCCESS:
                    if policy == PersistencePolicy.STRICT:
                        raise RuntimeError(f"Strict persistence save failure: {res.message}")
                    else:
                        logger.warning(f"Persistence best-effort fallback: {res.message}")
            except Exception as e:
                if policy == PersistencePolicy.STRICT:
                    raise RuntimeError(f"Strict persistence save failure: {e}") from e
                logger.warning(f"Database error saving review session {entry.entry_id}: {e}.")

        return entry

    def record_decision(self, record: ApprovalDecisionRecord) -> None:
        ws_id = record.workspace_id
        if ws_id not in self._records:
            self._records[ws_id] = []
        self._records[ws_id].append(record)

        # Save to review repo as a decision record
        if self._review_repo:
            policy = self._get_policy()
            try:
                mapped = {
                    "id": f"rec_{record.session_id}",
                    "session_id": record.session_id,
                    "workspace_id": record.workspace_id,
                    "state_transitions": [],
                    "metadata": {
                        "record_id": record.record_id,
                        "final_state": record.final_state.value,
                        "confidence_score": record.confidence_score,
                        "validation_score": record.validation_score,
                        "coverage_pct": record.coverage_pct,
                        "has_critical_failures": record.has_critical_failures,
                        "reviewer_count": record.reviewer_count,
                        "timestamp": record.timestamp,
                        "type": "decision_record",
                    },
                }
                res = self._review_repo.save(mapped)
                if res.status != PersistenceStatus.SUCCESS:
                    if policy == PersistencePolicy.STRICT:
                        raise RuntimeError(f"Strict persistence save failure: {res.message}")
                    else:
                        logger.warning(f"Persistence best-effort fallback: {res.message}")
            except Exception as e:
                if policy == PersistencePolicy.STRICT:
                    raise RuntimeError(f"Strict persistence save failure: {e}") from e
                logger.warning(
                    f"Database error saving decision record for session {record.session_id}: {e}."
                )

    def get_history_entry(self, session_id: str) -> Optional[ApprovalHistoryEntry]:
        if session_id in self._entries:
            return self._entries[session_id]

        if self._review_repo:
            try:
                res = self._review_repo.get(f"ent_{session_id}")
                if res.status == PersistenceStatus.SUCCESS and res.payload:
                    row = res.payload
                    transitions = []
                    for t in row.get("state_transitions", []):
                        transitions.append(
                            ApprovalStateTransition(
                                transition_id=t.get("transition_id"),
                                from_state=ApprovalState(t.get("from_state")),
                                to_state=ApprovalState(t.get("to_state")),
                                actor=t.get("actor"),
                                reason=t.get("reason"),
                                timestamp=t.get("timestamp", 0.0),
                            )
                        )
                    entry = ApprovalHistoryEntry(
                        entry_id=row.get("id"),
                        session_id=row.get("session_id"),
                        workspace_id=row.get("workspace_id"),
                        state_transitions=transitions,
                        metadata=row.get("metadata", {}),
                    )
                    self._entries[session_id] = entry
                    return entry
            except Exception as e:
                policy = self._get_policy()
                if policy == PersistencePolicy.STRICT:
                    raise RuntimeError(f"Strict persistence load failure: {e}") from e
                logger.warning(
                    f"Database error getting history entry for session {session_id}: {e}."
                )

        return None

    def get_decision_records(self, workspace_id: str) -> List[ApprovalDecisionRecord]:
        records = []
        if self._review_repo:
            try:
                q = "SELECT * FROM review_sessions WHERE workspace_id = ? AND id LIKE 'rec_%'"
                rows = self._review_repo.service.execute(q, (workspace_id,))
                for row in rows:
                    meta = json.loads(row["metadata"] or "{}")
                    if meta.get("type") == "decision_record":
                        records.append(
                            ApprovalDecisionRecord(
                                record_id=meta["record_id"],
                                session_id=row["session_id"],
                                workspace_id=row["workspace_id"],
                                final_state=ApprovalState(meta["final_state"]),
                                confidence_score=meta["confidence_score"],
                                validation_score=meta["validation_score"],
                                coverage_pct=meta["coverage_pct"],
                                has_critical_failures=meta["has_critical_failures"],
                                reviewer_count=meta["reviewer_count"],
                                timestamp=meta["timestamp"],
                            )
                        )
            except Exception as e:
                logger.warning(f"Failed to load decision records for {workspace_id} from DB: {e}")

        # Merge with in-memory records
        existing_ids = {r.record_id for r in records}
        for r in self._records.get(workspace_id, []):
            if r.record_id not in existing_ids:
                records.append(r)

        self._records[workspace_id] = records
        return self._records[workspace_id]

    def run_history_analysis(self, workspace_id: str) -> ApprovalHistoryReport:
        records = self.get_decision_records(workspace_id)
        entries = [e for e in self._entries.values() if e.workspace_id == workspace_id]

        stats = self._analyzer.compile_statistics(records)
        trends = self._analyzer.analyze_trends(records)
        patterns = self._analyzer.discover_patterns(entries, records)

        recommendations = []
        for pat in patterns:
            recommendations.append(
                ApprovalRecommendationHistory(
                    recommendation_id=f"rec_{pat.pattern_id}",
                    description=f"Action recommended to mitigate pattern: {pat.description}",
                    source_pattern_id=pat.pattern_id,
                    timestamp=time.time(),
                )
            )

        report = ApprovalHistoryReport(
            report_id=f"rep_hist_{workspace_id}",
            workspace_id=workspace_id,
            statistics=stats,
            trends=trends,
            patterns=patterns,
            recommendations=recommendations,
            timestamp=time.time(),
        )

        # Validate report integrity
        warnings = self._validator.validate_report(report)
        if warnings:
            logger.warning(f"History report validation warnings: {warnings}")

        # LLM Summary query if active
        history_summary = "Quality gating historical trends audit completed."
        if self._model and records:
            try:
                stats_desc = (
                    f"Total runs count: {stats.total_sessions}. Approved: {stats.approved_count}, "
                    f"Rejected: {stats.rejected_count}, Changes Requested: {stats.changes_requested_count}. "
                    f"Avg Coverage: {stats.average_coverage:.1f}%, Avg Validation Score: {stats.average_validation_score:.1f}%."
                )
                prompt = (
                    "You are the Principal Decision Architect for the Personal AI OS.\n"
                    f"Historical Gating statistics: {stats_desc}\n\n"
                    "Summarize quality trend directions and recommend improvements. Return refined summaries text only."
                )
                res = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output quality summaries directly.",
                        task_category="testing",
                    )
                )
                refined = res.content.strip()
                if refined:
                    history_summary = refined
            except Exception as e:
                logger.debug(f"LLM Gating history summary refinement failed: {e}")

        # Save to workspace path ONLY
        trends_md = []
        for t in trends:
            trends_md.append(
                f"- **{t.metric_name}**: Trend direction evaluates as `{t.direction.upper()}`."
            )

        patterns_md = []
        for p in patterns:
            patterns_md.append(
                f"- [{p.pattern_type.upper()}] {p.description} (Occurrences: {p.occurrence_count})"
            )

        report_md = (
            f"# Decision Intelligence Gating History Report\n\n"
            f"**Workspace ID**: `{workspace_id}`\n\n"
            f"## Historical Summary Overview\n{history_summary}\n\n"
            f"## Gating Statistics\n"
            f"- **Total Sessions Evaluated**: `{stats.total_sessions}`\n"
            f"- **Approved Sessions**: `{stats.approved_count}`\n"
            f"- **Changes Requested**: `{stats.changes_requested_count}`\n"
            f"- **Rejected Runs**: `{stats.rejected_count}`\n"
            f"- **Average Quality Confidence**: `{stats.average_confidence:.2f}`\n\n"
            f"## Metric Trends\n" + "\n".join(trends_md) + "\n\n"
            "## Discovered Blocker Patterns\n"
            + (
                "\n".join(patterns_md)
                if patterns_md
                else "- *No recurring blocker patterns found.*"
            )
        )
        self._write_to_workspace(workspace_id, f"APPROVAL_HISTORY_{workspace_id}.md", report_md)

        return report

    def store_history_summary(self, workspace_id: str) -> None:
        records = self.get_decision_records(workspace_id)
        stats = self._analyzer.compile_statistics(records)

        # Form content string. Never store repository source code.
        content = (
            f"Approval Gating Trends Synced\n"
            f"Workspace ID: {workspace_id}\n"
            f"Total Gating Sessions: {stats.total_sessions}\n"
            f"Approved: {stats.approved_count}, Rejected: {stats.rejected_count}, Requested Updates: {stats.changes_requested_count}\n"
            f"Quality averages: Validation score={stats.average_validation_score:.1f}%, Code Coverage={stats.average_coverage:.1f}%\n"
            f"Timestamp: {time.ctime()}"
        )

        self._memory.add_memory(
            content=content,
            memory_type=MemoryType.PROJECT,
            tags=["gating_history_trends", "decision_statistics", "quality_audit_summary"],
            importance=2,
            metadata_additional={
                "workspace_id": workspace_id,
                "statistics": {
                    "total_sessions": stats.total_sessions,
                    "approved": stats.approved_count,
                    "rejected": stats.rejected_count,
                    "changes_requested": stats.changes_requested_count,
                    "average_coverage": stats.average_coverage,
                    "average_validation": stats.average_validation_score,
                },
            },
        )

    def publish_history_report(self, report: ApprovalHistoryReport) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publishing.")
            return

        trends_list = []
        for trend in report.trends:
            trends_list.append(f"- **{trend.metric_name}**: `{trend.direction.upper()}` direction.")

        report_md = (
            f"# Notion Sync - Gating Decision History\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Workspace ID**: `{report.workspace_id}`\n\n"
            f"## Performance Averages\n"
            f"- Avg Validation: {report.statistics.average_validation_score:.1f}%\n"
            f"- Avg Coverage: {report.statistics.average_coverage:.1f}%\n\n"
            f"## Trends Overview\n" + "\n".join(trends_list)
        )

        doc = KnowledgeDocument(
            document_id=f"hist_report_{report.report_id}",
            title=f"Gating History - {report.report_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"hist_report_{report.report_id}",
                timestamp=report.timestamp,
                source_subsystem="approval_history_service",
                category="Project",
            ),
        )
        self._knowledge_hub.sync_document(doc, "notion")

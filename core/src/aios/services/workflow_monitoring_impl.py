import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

from aios.services.ai_workspace import AIWorkspaceService
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
    PersistenceService,
    WorkflowExecutionRepository,
    WorkflowMonitoringRepository,
)
from aios.services.workflow_monitoring import (
    WorkflowAlert,
    WorkflowExecutionRecord,
    WorkflowExecutionState,
    WorkflowExecutionTracker,
    WorkflowFailureAnalyzer,
    WorkflowHealthScore,
    WorkflowMonitoringReport,
    WorkflowMonitoringService,
    WorkflowMonitoringValidator,
    WorkflowPerformanceAnalyzer,
    WorkflowRetryAnalyzer,
    WorkflowStatistics,
)

logger = logging.getLogger(__name__)


class LocalWorkflowExecutionTracker(WorkflowExecutionTracker):
    """Tracks active trace sessions in memory registers."""

    def __init__(self) -> None:
        self._records: Dict[str, List[WorkflowExecutionRecord]] = {}

    def track_execution(self, record: WorkflowExecutionRecord) -> None:
        w_id = record.workflow_id
        if w_id not in self._records:
            self._records[w_id] = []
        self._records[w_id].append(record)

    def get_executions(self, workflow_id: str) -> List[WorkflowExecutionRecord]:
        return self._records.get(workflow_id, [])


class LocalWorkflowPerformanceAnalyzer(WorkflowPerformanceAnalyzer):
    """Compiles statistics, P95 values, median midpoints, and rates ratios."""

    def analyze_performance(self, records: List[WorkflowExecutionRecord]) -> WorkflowStatistics:
        total = len(records)
        if total == 0:
            return WorkflowStatistics(0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0)

        success = sum(1 for r in records if r.state == WorkflowExecutionState.SUCCESS)
        failures = sum(1 for r in records if r.state == WorkflowExecutionState.FAILED)
        retries = sum(1 for r in records if r.metrics.retry_count > 0)
        timeouts = sum(1 for r in records if r.state == WorkflowExecutionState.TIMEOUT)
        cancelled = sum(1 for r in records if r.state == WorkflowExecutionState.CANCELLED)
        skipped = sum(1 for r in records if r.state == WorkflowExecutionState.SKIPPED)

        durations = sorted([r.metrics.duration_seconds for r in records])
        avg_dur = sum(durations) / total

        # Median
        mid = total // 2
        median = durations[mid] if total % 2 != 0 else (durations[mid - 1] + durations[mid]) / 2

        # P95
        p95_idx = int(total * 0.95)
        p95 = durations[min(p95_idx, total - 1)]

        return WorkflowStatistics(
            total_runs=total,
            success_rate=success / total,
            failure_rate=failures / total,
            retry_rate=retries / total,
            average_duration=avg_dur,
            median_duration=median,
            p95_duration=p95,
            timeout_count=timeouts,
            cancelled_count=cancelled,
            skipped_count=skipped
        )


class LocalWorkflowFailureAnalyzer(WorkflowFailureAnalyzer):
    """Analyzes failure rates and reports repeating error warnings."""

    def analyze_failures(self, records: List[WorkflowExecutionRecord]) -> List[str]:
        patterns = []
        errors = [r.error_message for r in records if r.error_message]
        
        # Check repeated errors
        err_counts = {}
        for err in errors:
            err_counts[err] = err_counts.get(err, 0) + 1

        for msg, count in err_counts.items():
            if count > 1:
                patterns.append(f"Recurring Failure: Error message '{msg}' was encountered {count} times.")

        return patterns


class LocalWorkflowRetryAnalyzer(WorkflowRetryAnalyzer):
    """Monitors retry trigger trends."""

    def analyze_retries(self, records: List[WorkflowExecutionRecord]) -> Dict[str, Any]:
        total_runs = len(records)
        total_retries = sum(r.metrics.retry_count for r in records)
        max_retry_run = max([r.metrics.retry_count for r in records], default=0)
        return {
            "total_retries_triggered": total_retries,
            "max_retries_single_run": max_retry_run,
            "retry_frequency_ratio": total_retries / max(total_runs, 1)
        }


class LocalWorkflowMonitoringValidator(WorkflowMonitoringValidator):
    """Checks sequence trace values for ordering anomalies."""

    def validate_telemetry(self, records: List[WorkflowExecutionRecord]) -> List[str]:
        errors = []
        for r in records:
            if r.end_time and r.end_time < r.start_time:
                errors.append(f"Timestamp Integrity Breach: execution '{r.execution_id}' ends before it starts.")
            if r.metrics.duration_seconds < 0:
                errors.append(f"Metrics Inconsistency: execution '{r.execution_id}' duration is negative.")
        return errors


class LocalWorkflowMonitoringService(WorkflowMonitoringService):
    """Coordinating service tracking runs, triggers alerts, and publishing telemetry reports."""

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

        self._tracker = LocalWorkflowExecutionTracker()
        self._perf_analyzer = LocalWorkflowPerformanceAnalyzer()
        self._fail_analyzer = LocalWorkflowFailureAnalyzer()
        self._retry_analyzer = LocalWorkflowRetryAnalyzer()
        self._validator = LocalWorkflowMonitoringValidator()

        self._reports: Dict[str, List[WorkflowMonitoringReport]] = {}
        self._session_reports: Dict[str, WorkflowMonitoringReport] = {}
        self._mon_repo: Optional[WorkflowMonitoringRepository] = None
        self._exec_repo: Optional[WorkflowExecutionRepository] = None
        if registry:
            try:
                self._mon_repo = registry.get(WorkflowMonitoringRepository)
                self._exec_repo = registry.get(WorkflowExecutionRepository)
            except Exception:
                pass

    def initialize(self) -> None:
        logger.info("Initializing LocalWorkflowMonitoringService")

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

        monitors_dir = os.path.join(workspace_root, "docs", "monitors")
        os.makedirs(monitors_dir, exist_ok=True)
        
        file_path = os.path.join(monitors_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return file_path

    def record_execution(self, record: WorkflowExecutionRecord) -> None:
        logger.info(f"Logging execution trace '{record.execution_id}' for workflow '{record.workflow_id}'")

        # 1. Track trace
        self._tracker.track_execution(record)

        # 2. Check timing ordering validations
        errs = self._validator.validate_telemetry([record])
        if errs:
            logger.warning(f"Telemetry validation anomalies found: {errs}")

        if self._exec_repo:
            try:
                self._exec_repo.save({
                    "id": record.execution_id,
                    "workflow_id": record.workflow_id,
                    "workspace_id": record.workspace_id,
                    "status": record.state.value if hasattr(record.state, "value") else str(record.state),
                    "success": 1 if (record.state.value if hasattr(record.state, "value") else str(record.state)) == "success" else 0,
                    "error_summary": record.error_message,
                    "execution_time": record.metrics.duration_seconds if record.metrics else 0.0,
                    "created_at": record.start_time,
                    "closed_at": record.end_time,
                    "metadata": {
                        "retry_count": record.metrics.retry_count if record.metrics else 0,
                        "cpu_usage_pct": record.metrics.cpu_usage_pct if record.metrics else 0.0,
                        "memory_usage_mb": record.metrics.memory_usage_mb if record.metrics else 0.0
                    }
                })
            except Exception:
                pass

    def get_telemetry_report(self, workspace_id: str) -> WorkflowMonitoringReport:
        # Collate all workflow IDs for this workspace
        all_records = []
        for w_id, recs in self._tracker._records.items():
            for r in recs:
                if r.workspace_id == workspace_id:
                    all_records.append(r)

        workflow_ids = set(r.workflow_id for r in all_records)

        statistics = {}
        health_scores = {}
        alerts = []

        for w_id in workflow_ids:
            w_recs = [r for r in all_records if r.workflow_id == w_id]
            
            # Analytics compiles
            stats = self._perf_analyzer.analyze_performance(w_recs)
            statistics[w_id] = stats

            # Health evaluations
            # Deduct health for errors, retries, and timeouts
            failures = sum(1 for r in w_recs if r.state == WorkflowExecutionState.FAILED)
            timeouts = sum(1 for r in w_recs if r.state == WorkflowExecutionState.TIMEOUT)
            retries = sum(1 for r in w_recs if r.metrics.retry_count > 0)
            
            deductions = (failures * 20.0) + (timeouts * 20.0) + (retries * 10.0)
            score = max(0.0, 100.0 - deductions)
            reliability = stats.success_rate
            
            status = "healthy"
            if score < 60.0:
                status = "degraded"
            elif score < 90.0:
                status = "warning"
                
            health_scores[w_id] = WorkflowHealthScore(w_id, score, reliability, status)

            # Anomaly trigger warning checks
            # 1. Repeated failure alerts
            fail_patterns = self._fail_analyzer.analyze_failures(w_recs)
            for pattern in fail_patterns:
                alerts.append(
                    WorkflowAlert(
                        alert_id=f"al_fail_{w_id}_{int(time.time())}",
                        workflow_id=w_id,
                        alert_type="repeated_failure",
                        severity="critical",
                        message=pattern,
                        timestamp=time.time()
                    )
                )

            # 2. Long duration execution alerts
            long_runs = [r for r in w_recs if r.metrics.duration_seconds > 300]
            if long_runs:
                alerts.append(
                    WorkflowAlert(
                        alert_id=f"al_dur_{w_id}_{int(time.time())}",
                        workflow_id=w_id,
                        alert_type="long_duration",
                        severity="warning",
                        message=f"Long Duration: {len(long_runs)} runs exceeded the 300 seconds timeout threshold.",
                        timestamp=time.time()
                    )
                )

            # 3. High retry counts alerts
            high_retries = [r for r in w_recs if r.metrics.retry_count > 2]
            if high_retries:
                alerts.append(
                    WorkflowAlert(
                        alert_id=f"al_retry_{w_id}_{int(time.time())}",
                        workflow_id=w_id,
                        alert_type="high_retry",
                        severity="warning",
                        message=f"High Retries: {len(high_retries)} runs triggered more than 2 retry cycles.",
                        timestamp=time.time()
                    )
                )

        report_id = f"rep_mon_{int(time.time())}"
        report = WorkflowMonitoringReport(
            report_id=report_id,
            workspace_id=workspace_id,
            statistics=statistics,
            health_scores=health_scores,
            alerts=alerts,
            timestamp=time.time()
        )

        if self._mon_repo:
            try:
                self._mon_repo.save({
                    "id": report.report_id,
                    "workflow_id": list(statistics.keys())[0] if statistics else "system",
                    "execution_summaries": {w_id: {"runs": s.total_runs} for w_id, s in statistics.items()},
                    "health_summaries": {w_id: {"score": h.score, "status": h.status} for w_id, h in health_scores.items()},
                    "performance_summaries": {w_id: {"avg_duration": s.average_duration, "p95": s.p95_duration} for w_id, s in statistics.items()},
                    "alert_summaries": [
                        {"alert_id": a.alert_id, "alert_type": a.alert_type, "severity": a.severity, "message": a.message}
                        for a in alerts
                    ],
                    "success_rates": {w_id: s.success_rate for w_id, s in statistics.items()},
                    "latency_summaries": {w_id: s.average_duration for w_id, s in statistics.items()},
                    "retry_summaries": {w_id: s.retry_rate for w_id, s in statistics.items()},
                    "timestamp": report.timestamp
                })
            except Exception:
                pass

        if workspace_id not in self._reports:
            self._reports[workspace_id] = []
        self._reports[workspace_id].append(report)
        self._session_reports[report_id] = report

        # Write workspace report file only
        recs_desc = "Telemetry compilation completed successfully."
        if self._model:
            try:
                prompt = (
                    "You are the Lead Quality Automation Reliability Engineer for the Personal AI OS.\n"
                    f"Health score: {health_scores}\n"
                    f"Anomalies alerts triggered: {alerts}\n\n"
                    "Provide a refined outline and summary of the compiled results. Return summary text only."
                )
                res = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output telemetry outline details.",
                        task_category="testing"
                    )
                )
                refined = res.content.strip()
                if refined:
                    recs_desc = refined
            except Exception as e:
                logger.debug(f"LLM telemetry refinement failed: {e}")

        stats_md = "\n".join(
            f"- **Workflow ID**: `{w_id}`\n"
            f"  - Total Runs: {s.total_runs}\n"
            f"  - Success Rate: {s.success_rate:.1%}\n"
            f"  - Failure Rate: {s.failure_rate:.1%}\n"
            f"  - Health Score: {health_scores[w_id].score:.1f} ({health_scores[w_id].status.upper()})"
            for w_id, s in statistics.items()
        )

        alerts_md = "\n".join(
            f"- **[{a.severity.upper()}]** {a.message} (Workflow: `{a.workflow_id}`)"
            for a in alerts
        )

        report_md = (
            f"# Workflow Telemetry & Health Monitoring Report\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Workspace ID**: `{workspace_id}`\n\n"
            f"## Reliability Overview\n{recs_desc}\n\n"
            f"## Subsystem Statistics\n" + (stats_md if stats_md else "- *None.*") + "\n\n"
            "## Subsystem Alerts Anomaly Checks\n" + (alerts_md if alerts_md else "- *None.*")
        )
        self._write_to_workspace(workspace_id, f"TELEMETRY_REPORT_{workspace_id}.md", report_md)

        return report

    def get_alerts(self, workspace_id: str) -> List[WorkflowAlert]:
        reports = self._reports.get(workspace_id, [])
        if not reports:
            # compile on-demand
            report = self.get_telemetry_report(workspace_id)
            return report.alerts
        return reports[-1].alerts

    def get_history(self, workspace_id: str) -> List[WorkflowMonitoringReport]:
        if self._mon_repo:
            try:
                p_service = self._registry.get(PersistenceService)
                res = p_service.execute("SELECT * FROM workflow_monitoring")
                reports = []
                for row in res:
                    r_id = row["id"]
                    exec_sums = json.loads(row["execution_summaries"] or "{}")
                    health_sums = json.loads(row["health_summaries"] or "{}")
                    perf_sums = json.loads(row["performance_summaries"] or "{}")
                    alerts_data = json.loads(row["alert_summaries"] or "[]")
                    success_rates = json.loads(row["success_rates"] or "{}")
                    latency_sums = json.loads(row["latency_summaries"] or "{}")
                    retry_sums = json.loads(row["retry_summaries"] or "{}")
                    
                    statistics = {}
                    health_scores = {}
                    alerts = []
                    
                    for w_id in exec_sums.keys():
                        statistics[w_id] = WorkflowStatistics(
                            total_runs=exec_sums.get(w_id, {}).get("runs", 0),
                            success_rate=success_rates.get(w_id, 1.0),
                            failure_rate=1.0 - success_rates.get(w_id, 1.0),
                            retry_rate=retry_sums.get(w_id, 0.0),
                            average_duration=latency_sums.get(w_id, 0.0),
                            median_duration=latency_sums.get(w_id, 0.0),
                            p95_duration=perf_sums.get(w_id, {}).get("p95", 0.0),
                            timeout_count=0, cancelled_count=0, skipped_count=0
                        )
                        h_data = health_sums.get(w_id, {})
                        health_scores[w_id] = WorkflowHealthScore(
                            workflow_id=w_id,
                            score=h_data.get("score", 100.0),
                            reliability=success_rates.get(w_id, 1.0),
                            status=h_data.get("status", "healthy")
                        )
                    for a in alerts_data:
                        alerts.append(
                            WorkflowAlert(
                                alert_id=a.get("alert_id", ""),
                                workflow_id=a.get("workflow_id", ""),
                                alert_type=a.get("alert_type", ""),
                                severity=a.get("severity", ""),
                                message=a.get("message", ""),
                                timestamp=row.get("timestamp") or time.time()
                            )
                        )
                    reports.append(
                        WorkflowMonitoringReport(
                            report_id=r_id,
                            workspace_id=workspace_id,
                            statistics=statistics,
                            health_scores=health_scores,
                            alerts=alerts,
                            timestamp=row.get("timestamp") or time.time()
                        )
                    )
                self._reports[workspace_id] = reports
                return reports
            except Exception:
                pass
        return self._reports.get(workspace_id, [])

    def store_monitoring_summary(self, workspace_id: str) -> None:
        reports = self.get_history(workspace_id)
        if not reports:
            return

        report = reports[-1]
        
        # Form content summary. Never store credentials or source code.
        content = (
            f"Workflow Telemetry Logged\n"
            f"Workspace ID: {workspace_id}\n"
            f"Report ID: {report.report_id}\n"
            f"Workflows Tracked: {len(report.statistics)}\n"
            f"Alerts Triggered: {len(report.alerts)}\n"
            f"Timestamp: {time.ctime(report.timestamp)}"
        )

        self._memory.add_memory(
            content=content,
            memory_type=MemoryType.PROJECT,
            tags=["workflow_monitoring", "telemetry_logs", "reliability_stats"],
            importance=2,
            metadata_additional={
                "report_id": report.report_id,
                "workspace_id": workspace_id,
                "alerts_count": len(report.alerts),
                "workflows_count": len(report.statistics)
            }
        )

    def publish_monitoring_report(self, report: WorkflowMonitoringReport) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publishing.")
            return

        report_md = (
            f"# Notion Sync - Workflow Telemetry Monitoring\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Workspace ID**: `{report.workspace_id}`\n"
            f"**Workflows Count**: {len(report.statistics)}\n"
            f"**Alerts Triggered**: {len(report.alerts)}\n"
        )

        doc = KnowledgeDocument(
            document_id=f"mon_report_{report.report_id}",
            title=f"Workflow Monitoring - {report.report_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"mon_report_{report.report_id}",
                timestamp=report.timestamp,
                source_subsystem="workflow_monitoring_service",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

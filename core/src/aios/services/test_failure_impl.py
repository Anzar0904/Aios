import json
import logging
import time
from typing import Any, Dict, List, Optional

from aios.services.knowledge_hub import (
    KnowledgeDocument,
    KnowledgeHubService,
)
from aios.services.knowledge_hub import (
    KnowledgeMetadata as KHMetadata,
)
from aios.services.memory import MemoryMetadata, MemoryService, MemoryType
from aios.services.model import LLMRequest, ModelService
from aios.services.test_execution import ExecutionSummary
from aios.services.test_failure import (
    FailureAnalysisReport,
    FailureAnalysisService,
    FailureAnalyzer,
    FailureCluster,
    FailureConfidence,
    FailurePattern,
    FailureRecommendation,
    FailureSeverity,
    FailureSignature,
    RootCauseAnalyzer,
)
from aios.services.workspace_intelligence import CodeStructureSummary

logger = logging.getLogger(__name__)


class LocalFailureAnalyzer(FailureAnalyzer):
    """Classifies traceback signatures and groups exceptions into clusters."""

    def classify_failure(self, raw_output: str) -> FailurePattern:
        if "AssertionError" in raw_output:
            return FailurePattern("p_assert", "assertion_failure", r"AssertionError")
        elif "ImportError" in raw_output or "ModuleNotFoundError" in raw_output:
            return FailurePattern("p_import", "import_failure", r"ImportError|ModuleNotFoundError")
        elif "SyntaxError" in raw_output:
            return FailurePattern("p_syntax", "syntax_failure", r"SyntaxError")
        elif "Timeout" in raw_output:
            return FailurePattern("p_timeout", "timeout", r"Timeout")
        else:
            return FailurePattern("p_runtime", "runtime_exception", r"Exception")

    def cluster_failures(self, signatures: List[FailureSignature]) -> List[FailureCluster]:
        clusters_map: Dict[str, List[FailureSignature]] = {}
        for s in signatures:
            clusters_map.setdefault(s.exception_class, []).append(s)

        clusters = []
        for idx, (_ex_class, sigs) in enumerate(clusters_map.items()):
            pattern = self.classify_failure("".join(s.error_message for s in sigs))
            clusters.append(
                FailureCluster(
                    cluster_id=f"cluster_{idx}_{int(time.time())}",
                    pattern=pattern,
                    signatures=sigs
                )
            )
        return clusters


class LocalRootCauseAnalyzer(RootCauseAnalyzer):
    """Correlates call structures and execution timelines to isolate origin failure components."""

    def analyze_root_cause(
        self,
        execution_summary: ExecutionSummary,
        code_summary: CodeStructureSummary
    ) -> Dict[str, Any]:
        origins = []
        for r in execution_summary.results:
            if not r.success:
                # Find matching module or public api coupling
                origins.append(r.target.file_path)

        return {
            "origin_components": origins,
            "propagation_chain": [f"{o} -> dependencies" for o in origins]
        }


class LocalFailureAnalysisService(FailureAnalysisService):
    """Coordinating diagnosis service utilizing Model Service routing layers for failure refinements."""

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

        self._analyzer = LocalFailureAnalyzer()
        self._root_cause = LocalRootCauseAnalyzer()

    def initialize(self) -> None:
        logger.info("Initializing LocalFailureAnalysisService")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def diagnose_failures(
        self,
        workspace_id: str,
        execution_summary: ExecutionSummary,
        code_summary: CodeStructureSummary
    ) -> FailureAnalysisReport:
        logger.info(f"Diagnosing test execution failures for workspace: '{workspace_id}'")

        # 1. Gather failed signatures
        signatures = []
        for idx, r in enumerate(execution_summary.results):
            if not r.success:
                # Find exception class
                ex_class = "RuntimeError"
                for line in r.raw_output.splitlines():
                    if "Error:" in line or "Exception:" in line:
                        ex_class = line.split(":")[0].strip()
                        break
                        
                signatures.append(
                    FailureSignature(
                        signature_id=f"sig_{idx}_{int(time.time())}",
                        error_message=r.raw_output,
                        stack_trace=r.raw_output,
                        exception_class=ex_class
                    )
                )

        # 2. Cluster failures
        clusters = self._analyzer.cluster_failures(signatures)

        # 3. Analyze root cause
        rc = self._root_cause.analyze_root_cause(execution_summary, code_summary)

        # 4. Generate recommendations
        recommendations = []
        for orig in rc["origin_components"]:
            recommendations.append(
                FailureRecommendation(
                    recommendation_id=f"rec_{hash(orig) % 1000}",
                    recommendation_type="implementation_change",
                    description=f"Inspect logic errors inside module: {orig}.",
                    actionable_steps=[
                        f"Check lines changed inside {orig}.",
                        "Verify mocked return values for dependent calls."
                    ]
                )
            )

        severity = FailureSeverity.LOW
        if execution_summary.total_failed > 0:
            severity = FailureSeverity.HIGH
            # check if kernel files failed
            if any("kernel" in c for c in rc["origin_components"]):
                severity = FailureSeverity.CRITICAL

        confidence = FailureConfidence.CERTAIN if execution_summary.total_failed > 0 else FailureConfidence.LOW

        report = FailureAnalysisReport(
            report_id=f"fail_rep_{int(time.time())}",
            workspace_id=workspace_id,
            failed_suites_count=execution_summary.total_failed,
            clusters=clusters,
            recommendations=recommendations,
            severity=severity,
            confidence=confidence,
            timestamp=time.time()
        )

        # 5. LLM refinement if model is active
        if self._model and execution_summary.total_failed > 0:
            try:
                prompt = (
                    "You are the Principal QA architect for the Personal AI OS.\n"
                    f"Failing targets: {rc['origin_components']}\n"
                    f"Diagnosed severity: {severity.value}\n\n"
                    "Refine severity classification and recommendations. Return a single pure JSON:\n"
                    "{\n"
                    "  \"severity\": \"Critical\",\n"
                    "  \"confidence\": \"Certain\",\n"
                    "  \"refined_recommendation\": \"Add missing boundary mocks for memory service.\"\n"
                    "}"
                )

                response = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output pure JSON only.",
                        task_category="testing",
                        preferences={"JSON_output": True}
                    )
                )

                content = response.content.strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]

                data = json.loads(content)
                sev_val = data.get("severity", "high").upper()
                report.severity = FailureSeverity[sev_val] if sev_val in FailureSeverity.__members__ else report.severity
                conf_val = data.get("confidence", "high").upper()
                report.confidence = FailureConfidence[conf_val] if conf_val in FailureConfidence.__members__ else report.confidence
                
                if "refined_recommendation" in data:
                    report.recommendations.append(
                        FailureRecommendation(
                            recommendation_id=f"rec_llm_{int(time.time())}",
                            recommendation_type="manual_review",
                            description=data["refined_recommendation"],
                            actionable_steps=["Execute manual tracing on the LLM diagnostic tip."]
                        )
                    )
            except Exception as e:
                logger.debug(f"LLM failure diagnosis refinement failed: {e}. Keeping defaults.")

        return report

    def store_failure_report(self, report: FailureAnalysisReport) -> None:
        summary = (
            f"Intelligent Failure Analysis Report - ID: {report.report_id}\n"
            f"Workspace ID: {report.workspace_id}\n"
            f"Failed Suites Count: {report.failed_suites_count}\n"
            f"Severity Rating: {report.severity.value}\n"
            f"Confidence Score: {report.confidence.value}\n"
            f"Clusters Identified: {len(report.clusters)}\n"
            f"Recommendations Count: {len(report.recommendations)}"
        )
        
        self._memory.add_memory(
            content=summary,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id=report.report_id,
                session_id=report.report_id,
                tags=["failure_analysis", "diagnostics"],
                importance=2,
                source_subsystem="failure_analyzer"
            )
        )

    def publish_failure_report(self, report: FailureAnalysisReport) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        recs_md = []
        for r in report.recommendations:
            steps = "\n".join(f"  - {s}" for s in r.actionable_steps)
            recs_md.append(f"- **{r.recommendation_type}**: {r.description}\n{steps}")

        clusters_md = []
        for c in report.clusters:
            sigs = "\n".join(f"  - Sig: `{s.signature_id}` ({s.exception_class})" for s in c.signatures)
            clusters_md.append(f"- **Cluster**: Pattern `{c.pattern.pattern_name}`\n{sigs}")

        report_md = (
            f"# Engineering Failure Analysis Report\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Workspace ID**: `{report.workspace_id}`\n"
            f"**Failed Suites Count**: {report.failed_suites_count}\n"
            f"**Severity**: `{report.severity.value.upper()}`\n"
            f"**Confidence**: `{report.confidence.value.upper()}`\n\n"
            f"## Identified Failure Clusters\n"
            + ("\n".join(clusters_md) if clusters_md else "- *No failure clusters identified.*") + "\n\n"
            "## Corrective Action Recommendations\n"
            + ("\n".join(recs_md) if recs_md else "- *No failures, no recommendations required.*")
        )

        doc = KnowledgeDocument(
            document_id=f"fail_report_{report.report_id}",
            title=f"Failure Report - {report.report_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"fail_report_{report.report_id}",
                timestamp=report.timestamp,
                source_subsystem="failure_analyzer",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

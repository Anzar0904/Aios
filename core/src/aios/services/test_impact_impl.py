import json
import time
import os
import logging
from typing import Dict, List, Any, Optional

from aios.services.model import LLMRequest, ModelService
from aios.services.memory import MemoryService, MemoryType, MemoryMetadata
from aios.services.knowledge_hub import (
    KnowledgeHubService,
    KnowledgeDocument,
    KnowledgeMetadata as KHMetadata,
)
from aios.services.workspace_intelligence import CodeStructureSummary
from aios.services.test_impact import (
    ImpactNode,
    ImpactEdge,
    ImpactGraph,
    AffectedComponent,
    AffectedTestSuite,
    RegressionCandidate,
    RiskAssessment,
    CoverageTarget,
    ImpactAnalysisResult,
    ChangeImpactAnalyzer,
)

logger = logging.getLogger(__name__)


class LocalChangeImpactAnalyzer(ChangeImpactAnalyzer):
    """Calculates propagation maps, runs risks assessments, and determines coverage scopes."""

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

    def initialize(self) -> None:
        logger.info("Initializing LocalChangeImpactAnalyzer")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def analyze_change_impact(
        self,
        workspace_id: str,
        objective: str,
        affected_files: List[str],
        code_summary: CodeStructureSummary
    ) -> ImpactAnalysisResult:
        logger.info(f"Analyzing change impact for workspace: '{workspace_id}'")
        
        # 1. Build Impact Graph
        nodes = {}
        edges = []
        dep_graph = code_summary.dependency_graph

        for f in affected_files:
            node_id = f"node_{hash(f) % 1000}"
            nodes[f] = ImpactNode(node_id=node_id, file_path=f, node_type="file", is_modified=True)
            
            # Map outbound dependencies
            for dep in dep_graph.get(f, []):
                if dep not in nodes:
                    dep_node_id = f"node_{hash(dep) % 1000}"
                    nodes[dep] = ImpactNode(node_id=dep_node_id, file_path=dep, node_type="file", is_modified=False)
                edges.append(ImpactEdge(source=node_id, target=nodes[dep].node_id, relation="imports"))

        graph = ImpactGraph(nodes=nodes, edges=edges)

        # 2. Map affected components
        affected_components = []
        for f in affected_files:
            name = os.path.basename(f)
            affected_components.append(
                AffectedComponent(
                    name=name,
                    file_path=f,
                    direct_impact=True,
                    reason=f"Direct file modification requested in planning."
                )
            )

        # 3. Identify Affected Test Suites
        affected_suites = []
        for f in affected_files:
            # Check if matching test file exists
            base = os.path.basename(f)
            test_name = f"test_{base}"
            
            # Estimate coupling and priority
            importers_count = sum(1 for target, deps in dep_graph.items() if f in deps)
            priority = "High" if importers_count > 1 else "Medium"
            
            affected_suites.append(
                AffectedTestSuite(
                    suite_name=test_name,
                    run_required=True,
                    priority=priority,
                    reason=f"Validates direct logic edits for {base}."
                )
            )

        # 4. Regression candidate selection
        regression_candidates = []
        for target_file, deps in dep_graph.items():
            if target_file not in affected_files:
                if any(af in deps for af in affected_files):
                    importers_count = sum(1 for tf, dps in dep_graph.items() if target_file in dps)
                    regression_candidates.append(
                        RegressionCandidate(
                            file_path=target_file,
                            reason="Indirectly impacted module that imports modified file.",
                            coupling_density=importers_count or 1
                        )
                    )

        # 5. Risk Assessment
        overall = "Medium"
        api_risk = "Low"
        shared_risk = "Low"
        
        has_critical = any("kernel" in f or "bootstrap" in f for f in affected_files)
        if has_critical:
            overall = "High"
            shared_risk = "High"
            
        has_api = any(api in "".join(affected_files) for api in code_summary.public_apis)
        if has_api:
            api_risk = "High"

        risk = RiskAssessment(
            overall_risk=overall,
            api_break_risk=api_risk,
            shared_lib_risk=shared_risk,
            dep_chain_risk="Medium",
            config_risk="Low",
            data_model_risk="Low"
        )

        # 6. Coverage Targets
        coverage_targets = []
        for f in affected_files:
            coverage_targets.append(
                CoverageTarget(
                    file_path=f,
                    statement_coverage=90.0 if overall == "High" else 85.0,
                    branch_coverage=85.0 if overall == "High" else 80.0
                )
            )

        result = ImpactAnalysisResult(
            analysis_id=f"imp_res_{int(time.time())}",
            workspace_id=workspace_id,
            impact_graph=graph,
            affected_components=affected_components,
            affected_suites=affected_suites,
            regression_candidates=regression_candidates,
            risk_assessment=risk,
            coverage_targets=coverage_targets,
            timestamp=time.time()
        )

        # 7. LLM refinement if model is active
        if self._model:
            try:
                prompt = (
                    "You are the Lead QA systems architect for the Personal AI OS.\n"
                    f"Objective: {objective}\n"
                    f"Staged modified files: {affected_files}\n"
                    f"Overall risk assessment estimation: {overall}\n\n"
                    "Refine risk assessment metrics. Return a single, pure JSON object:\n"
                    "{\n"
                    "  \"overall_risk\": \"High\",\n"
                    "  \"dep_chain_risk\": \"High\",\n"
                    "  \"statement_coverage_target\": 90.0\n"
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
                result.risk_assessment.overall_risk = data.get("overall_risk", result.risk_assessment.overall_risk)
                result.risk_assessment.dep_chain_risk = data.get("dep_chain_risk", result.risk_assessment.dep_chain_risk)
                
                stmt_cov = data.get("statement_coverage_target", 85.0)
                for cov in result.coverage_targets:
                    cov.statement_coverage = stmt_cov
            except Exception as e:
                logger.debug(f"LLM impact refinement failed: {e}. Relying on rule defaults.")

        return result

    def store_impact_result(self, result: ImpactAnalysisResult) -> None:
        summary = (
            f"Change Impact Analysis Result - ID: {result.analysis_id}\n"
            f"Overall Risk: {result.risk_assessment.overall_risk.upper()}\n"
            f"Affected Components Count: {len(result.affected_components)}\n"
            f"Suites to Run Count: {len(result.affected_suites)}\n"
            f"Regression Candidates: {[r.file_path for r in result.regression_candidates]}\n"
            f"API Break Risk: {result.risk_assessment.api_break_risk}\n"
            f"Dep Chain Risk: {result.risk_assessment.dep_chain_risk}"
        )
        
        self._memory.add_memory(
            content=summary,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id=result.analysis_id,
                session_id=result.analysis_id,
                tags=["impact_analysis", "risk_assessment"],
                importance=2,
                source_subsystem="test_impact_analyzer"
            )
        )

    def publish_impact_report(self, result: ImpactAnalysisResult) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        components_md = []
        for c in result.affected_components:
            components_md.append(f"- `{c.name}` ({c.file_path}): {c.reason}")

        suites_md = []
        for s in result.affected_suites:
            suites_md.append(f"- **{s.suite_name}** [Priority: {s.priority}]: {s.reason}")

        regression_md = []
        for r in result.regression_candidates:
            regression_md.append(f"- `{r.file_path}` [Coupling count: {r.coupling_density}]: {r.reason}")

        report_md = (
            f"# Change Impact Analysis Report\n\n"
            f"**Analysis ID**: `{result.analysis_id}`\n"
            f"**Workspace ID**: `{result.workspace_id}`\n"
            f"**Overall Architectural Risk**: `{result.risk_assessment.overall_risk.upper()}`\n\n"
            f"## Impact Assessment Summary\n"
            f"- **API Break Risk**: {result.risk_assessment.api_break_risk}\n"
            f"- **Shared Library Risk**: {result.risk_assessment.shared_lib_risk}\n"
            f"- **Dependency Chain Risk**: {result.risk_assessment.dep_chain_risk}\n\n"
            f"## Affected Components\n"
            + "\n".join(components_md) + "\n\n"
            f"## Prioritized Test Suites\n"
            + "\n".join(suites_md) + "\n\n"
            f"## Regression Candidates\n"
            + ("\n".join(regression_md) if regression_md else "- *No indirect regression candidates identified.*")
        )

        doc = KnowledgeDocument(
            document_id=f"impact_plan_{result.analysis_id}",
            title=f"Impact Report - {result.analysis_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"impact_plan_{result.analysis_id}",
                timestamp=result.timestamp,
                source_subsystem="test_impact_analyzer",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

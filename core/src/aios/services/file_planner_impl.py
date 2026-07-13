import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

from aios.services.file_planner import (
    AffectedDirectory,
    AffectedFile,
    ChangePlanner,
    FileDependencyResolver,
    FileImpactAnalyzer,
    FilePlanner,
    ImplementationScope,
    ModificationType,
    PlanningResult,
)
from aios.services.knowledge_hub import (
    KnowledgeDocument,
    KnowledgeHubService,
)
from aios.services.knowledge_hub import (
    KnowledgeMetadata as KHMetadata,
)
from aios.services.memory import MemoryMetadata, MemoryService, MemoryType
from aios.services.model import LLMRequest, ModelService
from aios.services.workspace_intelligence import CodeStructureSummary

logger = logging.getLogger(__name__)


class LocalFileImpactAnalyzer(FileImpactAnalyzer):
    """Rule-based impact analyzer mapping files and directories."""

    def analyze_impact(
        self,
        objective: str,
        code_summary: CodeStructureSummary
    ) -> tuple[List[AffectedFile], List[AffectedDirectory]]:
        affected_files = []
        affected_directories = []
        
        target_files = list(code_summary.dependency_graph.keys())
        keywords = [w.lower() for w in objective.split() if len(w) > 3]

        matched_paths = []
        for f in target_files:
            f_name = os.path.basename(f).lower()
            if any(k in f_name for k in keywords):
                matched_paths.append(f)
                affected_files.append(
                    AffectedFile(
                        file_path=f,
                        modification_type=ModificationType.MODIFY,
                        reason=f"File name matches objective keyword: '{os.path.basename(f)}'",
                        risk_level="Medium",
                        dependencies=code_summary.dependency_graph.get(f, [])
                    )
                )

        # Directory mapping
        dir_map = {}
        for f in matched_paths:
            d = os.path.dirname(f) or "."
            dir_map[d] = dir_map.get(d, 0) + 1
            
        for d, count in dir_map.items():
            affected_directories.append(
                AffectedDirectory(
                    dir_path=d,
                    reason="Contains files impacted by the change plan.",
                    affected_files_count=count
                )
            )

        # Fallbacks to ensure non-empty results if nothing matched
        if not affected_files and target_files:
            default_f = target_files[0]
            affected_files.append(
                AffectedFile(
                    file_path=default_f,
                    modification_type=ModificationType.MODIFY,
                    reason="Default target file selected for change planning fallback.",
                    risk_level="Low",
                    dependencies=code_summary.dependency_graph.get(default_f, [])
                )
            )
            d = os.path.dirname(default_f) or "."
            affected_directories.append(
                AffectedDirectory(
                    dir_path=d,
                    reason="Contains default fallback file.",
                    affected_files_count=1
                )
            )

        return affected_files, affected_directories


class LocalFileDependencyResolver(FileDependencyResolver):
    """Resolves direct and transitive (indirect) dependencies recursively."""

    def resolve_dependencies(
        self,
        affected_files: List[AffectedFile],
        code_summary: CodeStructureSummary
    ) -> tuple[Dict[str, List[str]], Dict[str, List[str]], List[str]]:
        direct = {}
        indirect = {}
        high_risk = []

        graph = code_summary.dependency_graph
        
        for af in affected_files:
            f = af.file_path
            deps = graph.get(f, [])
            direct[f] = deps
            
            # Resolve indirect dependencies via BFS/DFS closure
            visited = set()
            queue = list(deps)
            while queue:
                current = queue.pop(0)
                if current not in visited and current != f:
                    visited.add(current)
                    # Extend imports
                    for parent_dep in graph.get(current, []):
                        if parent_dep not in visited:
                            queue.append(parent_dep)
            indirect[f] = list(visited)

            # High-risk detection: if file has more than 3 direct dependencies
            if len(deps) > 3:
                high_risk.append(f)

        return direct, indirect, high_risk


class LocalChangePlanner(ChangePlanner):
    """Calculates ordered sequences, classifications, and rollback checkpoints."""

    def plan_changes(
        self,
        objective: str,
        scope: ImplementationScope,
        direct_deps: Dict[str, List[str]],
        code_summary: CodeStructureSummary
    ) -> PlanningResult:
        # Topology sort style or basic safe order: dependees implemented first, dependent files last.
        files = [f.file_path for f in scope.affected_files]
        
        # Safe sequence helper: reverse dependency list mapping
        sequence = []
        visited = set()

        def visit(node):
            if node in visited:
                return
            visited.add(node)
            for dep in direct_deps.get(node, []):
                if dep in files:
                    visit(dep)
            sequence.append(node)

        for f in files:
            visit(f)

        # Default risks mapping
        circular = []
        interfaces = []
        shared = []
        configs = []
        migrations = []

        for af in scope.affected_files:
            # Shared module risk
            if af.file_path in code_summary.dependency_graph:
                # If imported by others
                importers_count = sum(1 for target, deps in code_summary.dependency_graph.items() if af.file_path in deps)
                if importers_count > 2:
                    shared.append(f"{af.file_path} is imported by {importers_count} modules.")

            # Interface risk
            if any(api in af.file_path for api in code_summary.public_apis):
                interfaces.append(f"Public API definitions inside {af.file_path} might break consumers.")

        # Checkpoints
        validation_cp = ["Check syntax compilation in workspace.", "Run existing test suite."]
        testing_cp = [f"Develop unit tests covering {f}" for f in sequence]
        doc_cp = ["Update Knowledge Base reference index.", "Update PROJECT_STATUS.md milestone table."]
        rollback_cp = ["Snapshot checkout state before applying workspace changes."]

        return PlanningResult(
            planning_id=f"plan_res_{int(time.time())}",
            objective=objective,
            scope=scope,
            implementation_sequence=sequence,
            direct_dependencies=direct_deps,
            indirect_dependencies={},
            high_risk_dependencies=[],
            shared_interfaces=code_summary.public_apis[:10],
            potential_breaking_points=interfaces,
            circular_dependency_risks=circular,
            interface_risks=interfaces,
            shared_module_risks=shared,
            configuration_risks=configs,
            migration_risks=migrations,
            validation_checkpoints=validation_cp,
            testing_checkpoints=testing_cp,
            documentation_checkpoints=doc_cp,
            rollback_checkpoints=rollback_cp,
            timestamp=time.time()
        )


class LocalFilePlanner(FilePlanner):
    """Coordinating File Planner implementation supporting LLM parsing and fallback rules."""

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
        
        self._analyzer = LocalFileImpactAnalyzer()
        self._resolver = LocalFileDependencyResolver()
        self._change_planner = LocalChangePlanner()

    def initialize(self) -> None:
        logger.info("Initializing LocalFilePlanner")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def generate_planning_result(
        self,
        workspace_id: str,
        objective: str,
        code_summary: CodeStructureSummary
    ) -> PlanningResult:
        logger.info(f"Generating file planning result for objective: '{objective}'")
        
        # Rule-based fallback workflow
        affected_files, affected_directories = self._analyzer.analyze_impact(objective, code_summary)
        
        scope = ImplementationScope(
            workspace_id=workspace_id,
            affected_files=affected_files,
            affected_directories=affected_directories,
            total_files_count=len(affected_files)
        )
        
        direct, indirect, high_risk = self._resolver.resolve_dependencies(affected_files, code_summary)
        
        result = self._change_planner.plan_changes(objective, scope, direct, code_summary)
        result.indirect_dependencies = indirect
        result.high_risk_dependencies = high_risk
        
        if self._model:
            try:
                target_files = list(code_summary.dependency_graph.keys())[:35]
                prompt = (
                    "You are the Lead Systems Architect for the Personal AI OS.\n"
                    f"Objective: {objective}\n\n"
                    f"Codebase Files: {target_files}\n"
                    f"Direct Dependency Graph: {direct}\n"
                    f"Interface list: {code_summary.public_apis[:10]}\n\n"
                    "Refine the change planning. Return a single, pure JSON object with the following structure:\n"
                    "{\n"
                    "  \"implementation_sequence\": [ \"string\" ],\n"
                    "  \"high_risk_dependencies\": [ \"string\" ],\n"
                    "  \"circular_dependency_risks\": [ \"string\" ],\n"
                    "  \"interface_risks\": [ \"string\" ],\n"
                    "  \"shared_module_risks\": [ \"string\" ],\n"
                    "  \"configuration_risks\": [ \"string\" ],\n"
                    "  \"migration_risks\": [ \"string\" ],\n"
                    "  \"validation_checkpoints\": [ \"string\" ],\n"
                    "  \"testing_checkpoints\": [ \"string\" ],\n"
                    "  \"documentation_checkpoints\": [ \"string\" ],\n"
                    "  \"rollback_checkpoints\": [ \"string\" ]\n"
                    "}"
                )

                res = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output pure JSON only.",
                        task_category="coding",
                        preferences={"JSON_output": True}
                    )
                )

                content = res.content.strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]

                data = json.loads(content)
                
                # Merge LLM feedback
                result.implementation_sequence = data.get("implementation_sequence", result.implementation_sequence)
                result.high_risk_dependencies = data.get("high_risk_dependencies", result.high_risk_dependencies)
                result.circular_dependency_risks = data.get("circular_dependency_risks", result.circular_dependency_risks)
                result.interface_risks = data.get("interface_risks", result.interface_risks)
                result.shared_module_risks = data.get("shared_module_risks", result.shared_module_risks)
                result.configuration_risks = data.get("configuration_risks", result.configuration_risks)
                result.migration_risks = data.get("migration_risks", result.migration_risks)
                result.validation_checkpoints = data.get("validation_checkpoints", result.validation_checkpoints)
                result.testing_checkpoints = data.get("testing_checkpoints", result.testing_checkpoints)
                result.documentation_checkpoints = data.get("documentation_checkpoints", result.documentation_checkpoints)
                result.rollback_checkpoints = data.get("rollback_checkpoints", result.rollback_checkpoints)
            except Exception as e:
                logger.debug(f"LLM change refinement failed: {e}. Relying on rule defaults.")

        return result

    def store_planning_result(self, result: PlanningResult) -> None:
        summary = (
            f"File Planning Result for: '{result.objective}'\n"
            f"Workspace ID: {result.scope.workspace_id}\n"
            f"Affected Files Count: {result.scope.total_files_count}\n"
            f"Execution Sequence: {result.implementation_sequence}\n"
            f"Circular Dependency Risks: {result.circular_dependency_risks}\n"
            f"Validation Checkpoints: {result.validation_checkpoints}"
        )
        
        self._memory.add_memory(
            content=summary,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id=result.scope.workspace_id,
                session_id=f"sess_{result.scope.workspace_id}",
                tags=["file_planning", "dependency_analysis"],
                importance=2,
                source_subsystem="file_planner"
            )
        )

        try:
            import time

            from aios.services.persistence import SemanticMemoryManager
            sem_mgr = self._registry.get(SemanticMemoryManager) if self._registry else None
            if sem_mgr:
                ws_id = result.scope.workspace_id or "default"
                metadata = {
                    "workspace_id": ws_id,
                    "timestamp": time.time(),
                    "type": "planning_result"
                }
                sem_mgr.index_memory(
                    repository_name="project_memory",
                    entity_id=f"plan_{ws_id}_{int(time.time())}",
                    text=summary,
                    metadata=metadata,
                    tags=["file_planning", "dependency_analysis", result.objective]
                )
        except Exception:
            pass

    def publish_planning_result(self, result: PlanningResult) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        files_md = []
        for f in result.scope.affected_files:
            files_md.append(f"- `{f.file_path}` ({f.modification_type.value.upper()}) [Risk: {f.risk_level}]: {f.reason}")

        report_md = (
            f"# Intelligent File Planning Report\n\n"
            f"**Objective**: {result.objective}\n"
            f"**Workspace ID**: `{result.scope.workspace_id}`\n"
            f"**Timestamp**: {result.timestamp}\n\n"
            f"## Affected Files Scope\n"
            + "\n".join(files_md) + "\n\n"
            "## Implementation Order Sequence\n"
            + "\n".join([f"{idx}. `{f_path}`" for idx, f_path in enumerate(result.implementation_sequence, 1)]) + "\n\n"
            f"## Risk Classifications & Mitigations\n"
            f"- **Circular Dependency Risks**: {result.circular_dependency_risks}\n"
            f"- **Interface Risks**: {result.interface_risks}\n"
            f"- **Shared Module Risks**: {result.shared_module_risks}\n\n"
            f"## Quality Verification Checkpoints\n"
            f"- **Validation Checkpoints**: {result.validation_checkpoints}\n"
            f"- **Testing Checkpoints**: {result.testing_checkpoints}\n"
            f"- **Rollback Checkpoints**: {result.rollback_checkpoints}\n"
        )

        doc = KnowledgeDocument(
            document_id=f"file_plan_{result.planning_id}",
            title=f"File Planning Report - {result.objective}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"file_plan_{result.planning_id}",
                timestamp=result.timestamp,
                source_subsystem="file_planner",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

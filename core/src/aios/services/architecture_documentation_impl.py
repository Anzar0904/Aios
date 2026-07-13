import logging
import time
from typing import Any, Dict, List, Optional

from aios.services.architecture_documentation import (
    ArchitectureAnalyzer,
    ArchitectureComponent,
    ArchitectureDiagram,
    ArchitectureDocumentationService,
    ArchitectureDocumentPlanner,
    ArchitectureLayer,
    ArchitectureRegistry,
    ArchitectureRelationship,
    ArchitectureReport,
    ArchitectureSummary,
    ArchitectureValidator,
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

logger = logging.getLogger(__name__)


class LocalArchitectureAnalyzer(ArchitectureAnalyzer):
    """Concrete analyzer discovering layers decoupling rules violations."""

    def analyze_architecture(
        self, code_structure: Dict[str, Any], existing_docs: str
    ) -> ArchitectureReport:
        dependencies = code_structure.get("dependencies", {})

        violations = []
        circular = []
        unused = []

        # Find circular dependencies
        for source, targets in dependencies.items():
            for target in targets:
                # If target also imports source back
                if source in dependencies.get(target, []):
                    pair = sorted([source, target])
                    cycle = f"{pair[0]} <-> {pair[1]}"
                    if cycle not in circular:
                        circular.append(cycle)

        # Layer violation checks (e.g., Domain must not import Infrastructure)
        layers = code_structure.get("layers", {})
        for name, data in layers.items():
            level = data.get("level", 0)
            imports = data.get("imports", [])
            for imp in imports:
                imp_level = layers.get(imp, {}).get("level", 99)
                # Level violation: lower level importing higher level directly
                if imp_level < level:
                    violations.append(
                        f"Layer violation: '{name}' (level {level}) imports '{imp}' (level {imp_level})"
                    )

        return ArchitectureReport(
            report_id=f"arch_rep_{int(time.time())}",
            workspace_id=code_structure.get("workspace_id", "ws_1"),
            violations=violations,
            circular_dependencies=circular,
            unused_services=unused,
            timestamp=time.time(),
        )


class LocalArchitectureDocumentPlanner(ArchitectureDocumentPlanner):
    """Concrete planner mapping codebase reports to target component structures."""

    def plan_architecture_documentation(
        self, report: ArchitectureReport
    ) -> List[ArchitectureComponent]:
        components = []

        # Add basic architecture system components
        components.append(ArchitectureComponent("Kernel", "core", "System composition root."))
        components.append(
            ArchitectureComponent("ServiceRegistry", "core", "DI Registry container.")
        )
        components.append(
            ArchitectureComponent(
                "WorkspaceService", "workspace", "AI Workspace sandboxes manager."
            )
        )

        return components


class LocalArchitectureValidator(ArchitectureValidator):
    """Concrete validator flagging unknown node connection references."""

    def validate_architecture_document(
        self, diagram: ArchitectureDiagram, registry: ArchitectureRegistry
    ) -> List[str]:
        errors = []

        # Check connection references in Mermaid syntax
        # e.g., A --> B or A -->|label| B
        import re

        nodes = re.findall(r"(\w+)\s*-->\s*(?:\|[^|]+\|\s*)?(\w+)", diagram.content)
        for src, dest in nodes:
            if not registry.get_component(src):
                errors.append(
                    f"Mermaid target error: undefined component node '{src}' in connections."
                )
            if not registry.get_component(dest):
                errors.append(
                    f"Mermaid target error: undefined component node '{dest}' in connections."
                )

        return errors


class LocalArchitectureDocumentationService(ArchitectureDocumentationService):
    """Coordinating Architecture service formatting diagram representations and pushing logs."""

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

        self._in_memory_registry = ArchitectureRegistry()
        self._analyzer = LocalArchitectureAnalyzer()
        self._planner = LocalArchitectureDocumentPlanner()
        self._validator = LocalArchitectureValidator()

    def initialize(self) -> None:
        logger.info("Initializing LocalArchitectureDocumentationService")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def generate_architecture_documentation(
        self, workspace_id: str, code_structure: Dict[str, Any], existing_docs: str
    ) -> ArchitectureDiagram:
        logger.info(f"Generating architecture documentation for workspace: '{workspace_id}'")

        # 1. Analyze
        report = self._analyzer.analyze_architecture(code_structure, existing_docs)

        # 2. Plan
        components = self._planner.plan_architecture_documentation(report)

        # 3. Register components
        for c in components:
            self._in_memory_registry.register_component(c)

        # Register standard layers
        core_layer = ArchitectureLayer("Core", 1, [components[0], components[1]])
        self._in_memory_registry.register_layer(core_layer)

        # Add mock relationships
        self._in_memory_registry.add_relationship(
            ArchitectureRelationship("Kernel", "ServiceRegistry", "registers")
        )

        # 4. Generate Mermaid diagram flowchart string
        mermaid_lines = ["graph TD"]
        for rel in self._in_memory_registry.list_relationships():
            mermaid_lines.append(
                f"    {rel.source_component} -->|{rel.relationship_type}| {rel.target_component}"
            )

        diagram_content = "\n".join(mermaid_lines)
        diagram = ArchitectureDiagram(
            diagram_id=f"arch_diag_{int(time.time())}",
            diagram_type="mermaid_flowchart",
            content=diagram_content,
        )

        # 5. LLM Refinement if active
        if self._model and components:
            try:
                prompt = (
                    "You are the Principal Systems Architect for the Personal AI OS.\n"
                    f"Generated Mermaid diagram flowchart:\n{diagram.content}\n\n"
                    "Refine connection definitions and styles. Return refined Mermaid code block only."
                )

                response = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output refined Mermaid syntax directly.",
                        task_category="testing",
                    )
                )

                refined_content = response.content.strip()
                if refined_content:
                    diagram.content = refined_content
            except Exception as e:
                logger.debug(f"LLM Architecture specs refinement failed: {e}. Keeping defaults.")

        return diagram

    def store_architecture_summary(self, summary: ArchitectureSummary) -> None:
        content = (
            f"Architecture Spec Summary - ID: {summary.summary_id}\n"
            f"Layers Discovered: {summary.layers_count}\n"
            f"Components Registered: {summary.components_count}\n"
            f"Relationships Active: {summary.relationships_count}"
        )

        self._memory.add_memory(
            content=content,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id=summary.summary_id,
                session_id=summary.summary_id,
                tags=["architecture_intelligence", "spec_summary"],
                importance=2,
                source_subsystem="architecture_service",
            ),
        )

    def publish_architecture_report(self, report: ArchitectureReport) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        violations_md = "\n".join(f"- {v}" for v in report.violations)
        circular_md = "\n".join(f"- `{c}`" for c in report.circular_dependencies)

        report_md = (
            f"# Architecture Integrity Report\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Workspace ID**: `{report.workspace_id}`\n\n"
            f"## Decoupling Layer Violations\n"
            + (violations_md if violations_md else "- *No layer decoupling violations detected.*")
            + "\n\n"
            "## Circular Dependencies Paths\n"
            + (circular_md if circular_md else "- *No circular dependency nodes found.*")
        )

        doc = KnowledgeDocument(
            document_id=f"arch_report_{report.report_id}",
            title=f"Architecture Integrity Report - {report.report_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"arch_report_{report.report_id}",
                timestamp=report.timestamp,
                source_subsystem="architecture_service",
                category="Project",
            ),
        )
        self._knowledge_hub.sync_document(doc, "notion")

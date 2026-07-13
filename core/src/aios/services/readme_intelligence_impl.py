import logging
import re
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
from aios.services.readme_intelligence import (
    READMEAnalyzer,
    READMEArtifact,
    READMEGenerator,
    READMEIntelligenceService,
    READMEPlanner,
    READMEReport,
    READMESection,
    READMESummary,
    READMETemplate,
    READMEUpdater,
    READMEValidator,
)

logger = logging.getLogger(__name__)


class LocalREADMEAnalyzer(READMEAnalyzer):
    """Concrete analyzer identifying missing standard README sections."""

    def analyze_readme(self, existing_content: str, workspace_metadata: Dict[str, Any]) -> READMEReport:
        missing = []
        outdated = []
        improvements = []

        standard_headers = ["Overview", "Installation", "Usage", "Configuration", "Testing", "License"]
        for header in standard_headers:
            if not re.search(rf"^#+\s+{header}", existing_content, re.IGNORECASE | re.MULTILINE):
                missing.append(header)

        # Check if project name is outdated
        proj_name = workspace_metadata.get("project_name", "")
        if proj_name and proj_name not in existing_content:
            outdated.append("Project Title")
            improvements.append(f"Update title to match project metadata: '{proj_name}'")

        return READMEReport(
            report_id=f"readme_rep_{int(time.time())}",
            workspace_id=workspace_metadata.get("workspace_id", "ws_1"),
            analysis_summary=f"Analysis identified {len(missing)} missing standard sections.",
            missing_sections=missing,
            outdated_sections=outdated,
            recommended_improvements=improvements,
            timestamp=time.time()
        )


class LocalREADMEPlanner(READMEPlanner):
    """Concrete sections planner generating content template placeholders."""

    def plan_sections(self, report: READMEReport, template: READMETemplate) -> List[READMESection]:
        sections = []
        
        # Determine priority index
        for idx, heading in enumerate(template.sections_order):
            content = f"Placeholder content for {heading}."
            if heading == "Installation":
                content = "```bash\npip install -r requirements.txt\n```"
            elif heading == "License":
                content = "MIT License"
                
            sections.append(
                READMESection(
                    heading=heading,
                    content=content,
                    importance=idx
                )
            )
        return sections


class LocalREADMEValidator(READMEValidator):
    """Concrete validator flagging link errors or duplicate headers."""

    def validate_readme(self, content: str) -> List[str]:
        errors = []
        
        # 1. Duplicate headings
        headings = re.findall(r"^#+\s+(.*)$", content, re.MULTILINE)
        seen = set()
        for h in headings:
            stripped = h.strip().lower()
            if stripped in seen:
                errors.append(f"Duplicate heading: '{h}'")
            seen.add(stripped)

        # 2. Check broken markdown link syntax
        # e.g., missing parenthesis or bracket
        if re.search(r"\[[^\]]*\]\([^\)]*$", content):
            errors.append("Syntax alert: broken link parentheses structure.")

        return errors


class LocalREADMEGenerator(READMEGenerator):
    """Formats list of sections into single markdown string."""

    def generate_readme(self, workspace_id: str, sections: List[READMESection]) -> READMEArtifact:
        # Sort by importance
        sorted_sections = sorted(sections, key=lambda s: s.importance)
        
        lines = []
        for s in sorted_sections:
            lines.append(f"# {s.heading}\n{s.content}\n")
            
        full_content = "\n".join(lines)
        return READMEArtifact(
            artifact_id=f"readme_{int(time.time())}",
            workspace_id=workspace_id,
            content=full_content,
            sections=sorted_sections,
            timestamp=time.time()
        )


class LocalREADMEUpdater(READMEUpdater):
    """Updates targeted sections in existing files by heading keys."""

    def update_readme(self, existing: READMEArtifact, changes: List[READMESection]) -> READMEArtifact:
        sections_map = {s.heading: s for s in existing.sections}
        
        for c in changes:
            sections_map[c.heading] = c
            
        new_sections = list(sections_map.values())
        # Sort by importance
        new_sections = sorted(new_sections, key=lambda s: s.importance)
        
        lines = []
        for s in new_sections:
            lines.append(f"# {s.heading}\n{s.content}\n")
            
        full_content = "\n".join(lines)
        return READMEArtifact(
            artifact_id=existing.artifact_id,
            workspace_id=existing.workspace_id,
            content=full_content,
            sections=new_sections,
            timestamp=time.time()
        )


class LocalREADMEIntelligenceService(READMEIntelligenceService):
    """Coordinating README configuration manager routing LLM refinements and caching metadata."""

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

        self._analyzer = LocalREADMEAnalyzer()
        self._planner = LocalREADMEPlanner()
        self._validator = LocalREADMEValidator()
        self._generator = LocalREADMEGenerator()
        self._updater = LocalREADMEUpdater()

    def initialize(self) -> None:
        logger.info("Initializing LocalREADMEIntelligenceService")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def analyze_and_generate(
        self,
        workspace_id: str,
        existing_content: str,
        workspace_metadata: Dict[str, Any],
        template: READMETemplate
    ) -> READMEArtifact:
        logger.info(f"Executing analyze & generate pipeline for workspace README: '{workspace_id}'")

        # 1. Analyze
        report = self._analyzer.analyze_readme(existing_content, workspace_metadata)

        # 2. Plan
        sections = self._planner.plan_sections(report, template)

        # 3. Generate
        artifact = self._generator.generate_readme(workspace_id, sections)

        # 4. LLM Refinement if active
        if self._model:
            try:
                prompt = (
                    "You are the Principal documentation architect for the Personal AI OS.\n"
                    f"Planned markdown content:\n{artifact.content}\n\n"
                    "Refine layout structures and add professional badges/descriptions. Return refined markdown only."
                )

                response = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output refined markdown syntax directly.",
                        task_category="testing"
                    )
                )

                refined_content = response.content.strip()
                if refined_content:
                    artifact.content = refined_content
            except Exception as e:
                logger.debug(f"LLM README generation refinement failed: {e}. Keeping defaults.")

        return artifact

    def store_readme_summary(self, summary: READMESummary) -> None:
        content = (
            f"README Generation Summary - ID: {summary.summary_id}\n"
            f"Overall Status: {summary.overall_status.upper()}\n"
            f"Sections Count: {summary.sections_count}\n"
            f"Last Generated: {time.ctime(summary.last_generated)}"
        )
        
        self._memory.add_memory(
            content=content,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id=summary.summary_id,
                session_id=summary.summary_id,
                tags=["readme_intelligence", "generation_telemetry"],
                importance=2,
                source_subsystem="readme_service"
            )
        )

    def publish_readme_report(self, report: READMEReport) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        missing_md = "\n".join(f"- `{m}`" for m in report.missing_sections)
        recs_md = "\n".join(f"- {r}" for r in report.recommended_improvements)

        report_md = (
            f"# README Intelligence Gap Report\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Workspace ID**: `{report.workspace_id}`\n"
            f"**Analysis Summary**: {report.analysis_summary}\n\n"
            f"## Missing Standard Headers\n"
            + (missing_md if missing_md else "- *All standard headers present.*") + "\n\n"
            "## Recommended Action Adjustments\n"
            + (recs_md if recs_md else "- *No recommendations.*")
        )

        doc = KnowledgeDocument(
            document_id=f"readme_report_{report.report_id}",
            title=f"README Analysis - {report.report_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"readme_report_{report.report_id}",
                timestamp=report.timestamp,
                source_subsystem="readme_service",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

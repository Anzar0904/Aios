import logging
import time
from typing import Any, List, Optional

from aios.services.engineering_documentation import (
    ADRGenerator,
    DecisionRecord,
    EngineeringDocumentArtifact,
    EngineeringDocumentationReport,
    EngineeringDocumentationService,
    EngineeringDocumentPlanner,
    EngineeringDocumentValidator,
    EngineeringReportGenerator,
    ImplementationSummary,
    RiskSummary,
    ValidationSummary,
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


class LocalADRGenerator(ADRGenerator):
    """Concrete generator assembling ADR Markdown layouts."""

    def generate_adr(self, record: DecisionRecord) -> str:
        alts = "\n".join(f"- {a}" for a in record.alternatives)
        return (
            f"# ADR {record.adr_id}: {record.title}\n\n"
            f"**Status**: {record.status.upper()}\n\n"
            f"## Context\n{record.context}\n\n"
            f"## Decision\n{record.decision}\n\n"
            f"## Alternatives Considered\n"
            + (alts if alts else "- *None.*") + "\n\n"
            f"## Consequences\n{record.consequences}\n"
        )


class LocalEngineeringReportGenerator(EngineeringReportGenerator):
    """Concrete generator compiling metrics summaries into Markdown reports."""

    def generate_engineering_report(
        self,
        summary: ImplementationSummary,
        validation: ValidationSummary,
        risk: RiskSummary
    ) -> str:
        feats = "\n".join(f"- {f}" for f in summary.features_added)
        files = "\n".join(f"- `{f}`" for f in summary.files_modified)
        
        return (
            "# Executive Implementation Report\n\n"
            "## Features Implemented\n" + (feats if feats else "- *None.*") + "\n\n"
            "## Modified File Mappings\n" + (files if files else "- *None.*") + "\n\n"
            f"## Validation Results\n"
            f"- **Tests Executed**: {validation.tests_run_count}\n"
            f"- **Tests Passed**: {validation.passed_count}\n"
            f"- **Statement Coverage**: {validation.coverage_percentage:.1f}%\n\n"
            f"## Risk Assessment\n"
            f"- **Risk Tier**: {risk.risk_level.upper()}\n"
            f"- **Impacted Boundaries**: {', '.join(risk.impacted_areas) if risk.impacted_areas else 'None'}\n"
        )


class LocalEngineeringDocumentPlanner(EngineeringDocumentPlanner):
    """Concrete planner mapping decisions lists requiring documenting."""

    def plan_engineering_documents(self, workspace_id: str) -> List[DecisionRecord]:
        return [
            DecisionRecord(
                adr_id="ADR-001",
                title="Centralized Documentation Intelligence",
                status="accepted",
                context="Requirements for global Markdown and Mermaid spec generation.",
                decision="Implement central orchestrator services registered in bootstrap.",
                alternatives=["Decentralized files updates"],
                consequences="Standardizes system-wide documentation."
            )
        ]


class LocalEngineeringDocumentValidator(EngineeringDocumentValidator):
    """Concrete validator flagging duplicate ADRs or empty sections."""

    def validate_engineering_document(self, artifact: EngineeringDocumentArtifact) -> List[str]:
        errors = []
        seen = set()
        
        for adr in artifact.adr_records:
            if adr.adr_id in seen:
                errors.append(f"Duplicate ADR ID: '{adr.adr_id}' detected.")
            seen.add(adr.adr_id)
            
            if not adr.context.strip():
                errors.append(f"ADR '{adr.adr_id}' context block is empty.")
                
            if not adr.decision.strip():
                errors.append(f"ADR '{adr.adr_id}' decision block is empty.")

        return errors


class LocalEngineeringDocumentationService(EngineeringDocumentationService):
    """Coordinating service executing generators and memory synchronizations."""

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

        self._adr_generator = LocalADRGenerator()
        self._report_generator = LocalEngineeringReportGenerator()
        self._planner = LocalEngineeringDocumentPlanner()
        self._validator = LocalEngineeringDocumentValidator()

    def initialize(self) -> None:
        logger.info("Initializing LocalEngineeringDocumentationService")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def create_adr_document(self, workspace_id: str, record: DecisionRecord) -> EngineeringDocumentArtifact:
        logger.info(f"Generating ADR '{record.adr_id}' document.")
        
        content = self._adr_generator.generate_adr(record)
        artifact = EngineeringDocumentArtifact(
            artifact_id=f"adr_{record.adr_id}",
            workspace_id=workspace_id,
            content=content,
            adr_records=[record],
            timestamp=time.time()
        )

        # Refine with Model
        if self._model:
            try:
                prompt = (
                    "You are the Principal Documentation engineer.\n"
                    f"Planned ADR content:\n{artifact.content}\n\n"
                    "Refine layout structures and add trade-offs details. Return refined markdown only."
                )
                response = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output refined markdown syntax directly.",
                        task_category="testing"
                    )
                )
                refined = response.content.strip()
                if refined:
                    artifact.content = refined
            except Exception as e:
                logger.debug(f"LLM ADR refinement failed: {e}. Keeping defaults.")

        return artifact

    def create_engineering_report(
        self,
        workspace_id: str,
        summary: ImplementationSummary,
        validation: ValidationSummary,
        risk: RiskSummary
    ) -> EngineeringDocumentArtifact:
        logger.info(f"Generating Engineering Report '{summary.summary_id}'.")
        
        content = self._report_generator.generate_engineering_report(summary, validation, risk)
        artifact = EngineeringDocumentArtifact(
            artifact_id=f"eng_rep_{summary.summary_id}",
            workspace_id=workspace_id,
            content=content,
            adr_records=[],
            timestamp=time.time()
        )

        # Refine with Model
        if self._model:
            try:
                prompt = (
                    "You are the Principal Systems engineer.\n"
                    f"Generated Engineering Report:\n{artifact.content}\n\n"
                    "Refine layout structures and add future considerations notes. Return refined markdown only."
                )
                response = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output refined markdown syntax directly.",
                        task_category="testing"
                    )
                )
                refined = response.content.strip()
                if refined:
                    artifact.content = refined
            except Exception as e:
                logger.debug(f"LLM Report refinement failed: {e}. Keeping defaults.")

        return artifact

    def store_engineering_summary(self, artifact: EngineeringDocumentArtifact) -> None:
        content = (
            f"Engineering Documentation Created - ID: {artifact.artifact_id}\n"
            f"Workspace ID: {artifact.workspace_id}\n"
            f"ADRs count: {len(artifact.adr_records)}"
        )
        
        self._memory.add_memory(
            content=content,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id=artifact.artifact_id,
                session_id=artifact.artifact_id,
                tags=["engineering_documentation", "adr_summary"],
                importance=2,
                source_subsystem="engineering_documentation_service"
            )
        )

    def publish_engineering_report(self, report: EngineeringDocumentationReport) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        recs_md = "\n".join(f"- {r}" for r in report.recommendations)

        report_md = (
            f"# Executive Summary Report\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Workspace ID**: `{report.workspace_id}`\n\n"
            f"## Executive Summary Details\n{report.executive_summary}\n\n"
            f"## Risk Assessment\n{report.risk_assessment}\n\n"
            f"## Recommendations\n" + (recs_md if recs_md else "- *None.*")
        )

        doc = KnowledgeDocument(
            document_id=f"eng_report_{report.report_id}",
            title=f"Engineering Summary - {report.report_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"eng_report_{report.report_id}",
                timestamp=report.timestamp,
                source_subsystem="engineering_documentation_service",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

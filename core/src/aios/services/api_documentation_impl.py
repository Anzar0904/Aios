import time
import json
import logging
from typing import Dict, List, Any, Optional

from aios.services.model import LLMRequest, ModelService
from aios.services.memory import MemoryService, MemoryType, MemoryMetadata
from aios.services.knowledge_hub import (
    KnowledgeHubService,
    KnowledgeDocument,
    KnowledgeMetadata as KHMetadata,
)
from aios.services.api_documentation import (
    APIParameter,
    APISchema,
    APIExample,
    APIResponse,
    APIEndpoint,
    APIDocumentArtifact,
    APIReport,
    APIAnalyzer,
    APIDocumentationPlanner,
    APIDocumentValidator,
    APIRegistry,
    APIDocumentationService,
)

logger = logging.getLogger(__name__)


class LocalAPIAnalyzer(APIAnalyzer):
    """Concrete analyzer scanning code structures for REST routes."""

    def analyze_api(self, code_structure: Dict[str, Any], existing_docs: str) -> APIReport:
        routes = code_structure.get("routes", [])
        
        undocumented = []
        missing_params = []
        outdated_schemas = []
        missing_examples = []
        recommendations = []

        for route in routes:
            path = route.get("path", "")
            method = route.get("method", "GET")
            
            # Check if mentioned in existing documentation
            if path not in existing_docs:
                undocumented.append(f"{method} {path}")
                recommendations.append(f"Add documentation for route: {method} {path}.")
                
            # Check parameters
            params = route.get("parameters", [])
            for p in params:
                p_name = p.get("name", "")
                if p_name and p_name not in existing_docs:
                    missing_params.append(p_name)
                    recommendations.append(f"Add missing parameter mapping: {p_name} for route {path}.")

        return APIReport(
            report_id=f"api_rep_{int(time.time())}",
            workspace_id=code_structure.get("workspace_id", "ws_1"),
            undocumented_endpoints=undocumented,
            missing_parameters=missing_params,
            outdated_schemas=outdated_schemas,
            missing_examples=missing_examples,
            recommendations=recommendations,
            timestamp=time.time()
        )


class LocalAPIDocumentationPlanner(APIDocumentationPlanner):
    """Concrete planner mapping discovered endpoints to schemas configurations."""

    def plan_api_documentation(self, report: APIReport) -> List[APIEndpoint]:
        endpoints = []
        for raw in report.undocumented_endpoints:
            # Parse method and path
            parts = raw.split(" ")
            method = parts[0]
            path = parts[1] if len(parts) > 1 else "/"
            
            # Create default parameters
            params = [
                APIParameter("limit", "integer", False, "Number of items to retrieve."),
                APIParameter("offset", "integer", False, "Cursor offset count.")
            ]
            
            schema = APISchema("SuccessResponse", {"success": "boolean"}, "Standard success envelope.")
            resp = APIResponse(200, schema, "Success outcome description.")
            
            endpoints.append(
                APIEndpoint(
                    path=path,
                    method=method,
                    summary=f"Discovered route {method} {path}.",
                    parameters=params,
                    request_body_schema=None,
                    responses=[resp]
                )
            )
        return endpoints


class LocalAPIDocumentValidator(APIDocumentValidator):
    """Concrete validator flagging OpenAPI duplicate routes or empty schemas."""

    def validate_api_document(self, artifact: APIDocumentArtifact) -> List[str]:
        errors = []
        seen = set()
        
        for e in artifact.endpoints:
            key = f"{e.method}:{e.path}"
            if key in seen:
                errors.append(f"Duplicate route: '{e.method} {e.path}' detected.")
            seen.add(key)

            if not e.responses:
                errors.append(f"Empty responses for endpoint: '{e.method} {e.path}'.")

            for r in e.responses:
                if r.schema and not r.schema.fields:
                    errors.append(f"Empty schema fields for response status {r.status_code} in route '{e.method} {e.path}'.")
                    
        return errors


class LocalAPIDocumentationService(APIDocumentationService):
    """Coordinating API service cataloging schemas and pushing summaries to Notion."""

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

        self._in_memory_registry = APIRegistry()
        self._analyzer = LocalAPIAnalyzer()
        self._planner = LocalAPIDocumentationPlanner()
        self._validator = LocalAPIDocumentValidator()

    def initialize(self) -> None:
        logger.info("Initializing LocalAPIDocumentationService")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def generate_api_documentation(
        self,
        workspace_id: str,
        code_structure: Dict[str, Any],
        existing_docs: str
    ) -> APIDocumentArtifact:
        logger.info(f"Generating API documentation for workspace: '{workspace_id}'")

        # 1. Analyze
        report = self._analyzer.analyze_api(code_structure, existing_docs)

        # 2. Plan
        endpoints = self._planner.plan_api_documentation(report)

        # 3. Register
        for e in endpoints:
            self._in_memory_registry.register_endpoint(e)

        # 4. Generate markdown content
        lines = ["# API Specifications Reference\n"]
        for e in endpoints:
            lines.append(f"## `{e.method}` {e.path}")
            lines.append(f"**Description**: {e.summary}\n")
            
            lines.append("### Query Parameters")
            lines.append("| Name | Type | Required | Description |")
            lines.append("|---|---|---|---|")
            for p in e.parameters:
                req = "Yes" if p.required else "No"
                lines.append(f"| `{p.name}` | `{p.param_type}` | {req} | {p.description} |")
            lines.append("")

            lines.append("### Responses")
            for r in e.responses:
                lines.append(f"- **Status Code {r.status_code}**: {r.description}")
                if r.schema:
                    lines.append(f"  - Schema: `{r.schema.schema_name}`")
            lines.append("")

        full_content = "\n".join(lines)
        artifact = APIDocumentArtifact(
            artifact_id=f"api_doc_{int(time.time())}",
            workspace_id=workspace_id,
            content=full_content,
            endpoints=endpoints,
            timestamp=time.time()
        )

        # 5. LLM Refinement if active
        if self._model and endpoints:
            try:
                prompt = (
                    "You are the Principal API architect for the Personal AI OS.\n"
                    f"Generated API Specs markdown:\n{artifact.content}\n\n"
                    "Refine layout structures and add professional request/response examples. Return refined markdown only."
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
                logger.debug(f"LLM API specs generation refinement failed: {e}. Keeping defaults.")

        return artifact

    def store_api_summary(self, artifact: APIDocumentArtifact) -> None:
        content = (
            f"API Documentation Generated - ID: {artifact.artifact_id}\n"
            f"Workspace ID: {artifact.workspace_id}\n"
            f"Endpoints Cataloged: {len(artifact.endpoints)}\n"
            f"Registered Keys: {[f'{e.method} {e.path}' for e in artifact.endpoints]}"
        )
        
        self._memory.add_memory(
            content=content,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id=artifact.artifact_id,
                session_id=artifact.artifact_id,
                tags=["api_documentation", "specs_summary"],
                importance=2,
                source_subsystem="api_documentation_service"
            )
        )

    def publish_api_report(self, report: APIReport) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        missing_md = "\n".join(f"- `{m}`" for m in report.undocumented_endpoints)
        recs_md = "\n".join(f"- {r}" for r in report.recommendations)

        report_md = (
            f"# API Documentation Coverage Report\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Workspace ID**: `{report.workspace_id}`\n"
            f"**Undocumented Routes count**: {len(report.undocumented_endpoints)}\n\n"
            f"## Discovered Undocumented Endpoints\n"
            + (missing_md if missing_md else "- *No undocumented routes discovered.*") + "\n\n"
            f"## Action Recommendations\n"
            + (recs_md if recs_md else "- *No actions recommended.*")
        )

        doc = KnowledgeDocument(
            document_id=f"api_report_{report.report_id}",
            title=f"API Analysis Report - {report.report_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"api_report_{report.report_id}",
                timestamp=report.timestamp,
                source_subsystem="api_documentation_service",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

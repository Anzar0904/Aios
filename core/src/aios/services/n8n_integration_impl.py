import os
import json
import time
import logging
from typing import Dict, List, Any, Optional

from aios.services.model import LLMRequest, ModelService
from aios.services.memory import MemoryService, MemoryType
from aios.services.knowledge_hub import (
    KnowledgeHubService,
    KnowledgeDocument,
    KnowledgeMetadata as KHMetadata,
)
from aios.services.ai_workspace import AIWorkspaceService
from aios.services.engineering_profile import EngineeringProfileService
from aios.services.n8n_integration import (
    N8NServerInformation,
    N8NConnectionProfile,
    N8NIntegrationReport,
    N8NAuthenticationProvider,
    N8NConnectionManager,
    N8NClient,
    N8NWorkflowRepository,
    N8NExecutionRepository,
    N8NCredentialRepository,
    N8NHealthMonitor,
    N8NWorkspaceMapper,
    N8NValidator,
    N8NIntegrationService,
)

logger = logging.getLogger(__name__)


class LocalN8NClient(N8NClient):
    """Concrete mock client simulating HTTP REST calls to a self-hosted n8n server."""

    def __init__(self) -> None:
        self._workflows: Dict[str, Dict[str, Any]] = {}
        self._executions: Dict[str, Dict[str, Any]] = {}
        self._active_status: Dict[str, bool] = {}

    def upload_workflow(self, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        workflow_id = f"n8n_wf_{int(time.time())}"
        self._workflows[workflow_id] = workflow_json
        self._active_status[workflow_id] = False
        return {"id": workflow_id, "name": workflow_json.get("name", "Unnamed"), "active": False}

    def update_workflow(self, workflow_id: str, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        if workflow_id not in self._workflows:
            raise ValueError(f"Workflow '{workflow_id}' not found.")
        self._workflows[workflow_id] = workflow_json
        return {"id": workflow_id, "name": workflow_json.get("name", "Unnamed"), "active": self._active_status.get(workflow_id, False)}

    def delete_workflow(self, workflow_id: str) -> bool:
        if workflow_id in self._workflows:
            del self._workflows[workflow_id]
            if workflow_id in self._active_status:
                del self._active_status[workflow_id]
            return True
        return False

    def list_workflows(self) -> List[Dict[str, Any]]:
        return [{"id": k, "name": v.get("name", "Unnamed"), "active": self._active_status.get(k, False)} for k, v in self._workflows.items()]

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        if workflow_id not in self._workflows:
            raise ValueError(f"Workflow '{workflow_id}' not found.")
        return self._workflows[workflow_id]

    def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        if workflow_id not in self._workflows:
            raise ValueError(f"Workflow '{workflow_id}' not found.")
        execution_id = f"n8n_exec_{int(time.time())}"
        self._executions[execution_id] = {
            "id": execution_id,
            "workflowId": workflow_id,
            "status": "success",
            "data": input_data,
            "finished": True
        }
        return self._executions[execution_id]

    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        if execution_id not in self._executions:
            raise ValueError(f"Execution '{execution_id}' not found.")
        return self._executions[execution_id]

    def list_executions(self, workflow_id: str) -> List[Dict[str, Any]]:
        return [v for v in self._executions.values() if v["workflowId"] == workflow_id]

    def activate_workflow(self, workflow_id: str) -> bool:
        if workflow_id not in self._workflows:
            return False
        self._active_status[workflow_id] = True
        return True

    def deactivate_workflow(self, workflow_id: str) -> bool:
        if workflow_id not in self._workflows:
            return False
        self._active_status[workflow_id] = False
        return True


class LocalN8NWorkflowRepository(N8NWorkflowRepository):
    """Workflow metadata catalog."""

    def __init__(self) -> None:
        self._metadata: Dict[str, Dict[str, Any]] = {}

    def save_workflow_metadata(self, workflow_id: str, metadata: Dict[str, Any]) -> None:
        self._metadata[workflow_id] = metadata

    def get_workflow_metadata(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        return self._metadata.get(workflow_id)


class LocalN8NExecutionRepository(N8NExecutionRepository):
    """Executions metadata catalog."""

    def __init__(self) -> None:
        self._metadata: Dict[str, Dict[str, Any]] = {}

    def save_execution_metadata(self, execution_id: str, metadata: Dict[str, Any]) -> None:
        self._metadata[execution_id] = metadata


class LocalN8NCredentialRepository(N8NCredentialRepository):
    """Credential vault indexing references."""

    def __init__(self) -> None:
        self._vault: Dict[str, str] = {}

    def register_credential_reference(self, name: str, value: str) -> None:
        self._vault[name] = value


class LocalN8NHealthMonitor(N8NHealthMonitor):
    """Simulates ping endpoints returning low latency and typical capabilities list."""

    def check_health(self) -> Dict[str, Any]:
        return {
            "status": "online",
            "version": "1.25.0",
            "latency_ms": 12.5,
            "capabilities": ["webhooks", "oauth2", "variables", "sticky-notes"]
        }


class LocalN8NWorkspaceMapper(N8NWorkspaceMapper):
    """Maps workflows ownership IDs to workspaces identifiers."""

    def __init__(self) -> None:
        self._mappings: Dict[str, str] = {}

    def map_workflow_to_workspace(self, workflow_id: str, workspace_id: str) -> None:
        self._mappings[workflow_id] = workspace_id

    def get_workspace_for_workflow(self, workflow_id: str) -> Optional[str]:
        return self._mappings.get(workflow_id)


class LocalN8NValidator(N8NValidator):
    """Checks URL patterns and basic connections profiles parameters."""

    def validate_server_config(self, profile: N8NConnectionProfile) -> List[str]:
        errors = []
        if not profile.url.startswith(("http://", "https://")):
            errors.append("Validation Error: n8n server URL must start with http:// or https:// protocol.")
        if profile.timeout_seconds <= 0:
            errors.append("Validation Error: timeout_seconds delay must be greater than zero.")
        return errors


class LocalN8NIntegrationService(N8NIntegrationService):
    """Conductor service managing mock client uploads, health checks and Notion report syncing."""

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

        self._client = LocalN8NClient()
        self._wf_repo = LocalN8NWorkflowRepository()
        self._exec_repo = LocalN8NExecutionRepository()
        self._cred_repo = LocalN8NCredentialRepository()
        self._health_monitor = LocalN8NHealthMonitor()
        self._workspace_mapper = LocalN8NWorkspaceMapper()
        self._validator = LocalN8NValidator()

        self._reports: Dict[str, List[N8NIntegrationReport]] = {}
        self._session_reports: Dict[str, N8NIntegrationReport] = {}

    def initialize(self) -> None:
        logger.info("Initializing LocalN8NIntegrationService")

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

        automations_dir = os.path.join(workspace_root, "docs", "automations")
        os.makedirs(automations_dir, exist_ok=True)
        
        file_path = os.path.join(automations_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return file_path

    def upload_workflow_json(self, workspace_id: str, workflow_json: Dict[str, Any]) -> str:
        logger.info(f"Uploading workflow json under workspace '{workspace_id}'")

        # 1. Fetch preferences using EngineeringProfileService configuration details
        profile_service = None
        timeout = 30
        if self._registry:
            try:
                profile_service = self._registry.get(EngineeringProfileService)
            except Exception:
                pass

        # 2. Connection validator
        profile = N8NConnectionProfile("http://localhost:5678", "api_key", timeout)
        errors = self._validator.validate_server_config(profile)
        if errors:
            raise ValueError(f"Invalid Server Config: {errors}")

        # 3. Client upload API mock
        res = self._client.upload_workflow(workflow_json)
        workflow_id = res["id"]

        # 4. Save metadata mappings
        self._wf_repo.save_workflow_metadata(workflow_id, {"uploaded_at": time.time(), "workspace_id": workspace_id})
        self._workspace_mapper.map_workflow_to_workspace(workflow_id, workspace_id)

        # 5. Write artifacts only inside Workspace
        meta_json = {
            "workflow_id": workflow_id,
            "uploaded_at": time.time(),
            "workspace_id": workspace_id,
            "server_profile": {
                "url": profile.url,
                "auth_type": profile.auth_type
            }
        }
        self._write_to_workspace(workspace_id, f"N8N_METADATA_{workflow_id}.json", json.dumps(meta_json, indent=2))

        return workflow_id

    def trigger_workflow(self, workflow_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        workspace_id = self._workspace_mapper.get_workspace_for_workflow(workflow_id) or "ws_unknown"
        
        # 1. client execution API mock
        res = self._client.execute_workflow(workflow_id, inputs)
        
        # 2. Save metadata
        self._exec_repo.save_execution_metadata(res["id"], {"status": res["status"], "workflow_id": workflow_id})
        
        return res

    def get_health_status(self) -> N8NIntegrationReport:
        # Check health
        health = self._health_monitor.check_health()
        
        report_id = f"rep_int_{int(time.time())}"
        report = N8NIntegrationReport(
            report_id=report_id,
            workspace_id="system",
            server_version=health["version"],
            connectivity_status=health["status"],
            latency_ms=health["latency_ms"],
            uploaded_workflows_count=len(self._client.list_workflows()),
            timestamp=time.time()
        )
        
        self._session_reports[report_id] = report
        return report

    def get_history(self, workspace_id: str) -> List[N8NIntegrationReport]:
        return self._reports.get(workspace_id, [])

    def store_integration_summary(self, report_id: str) -> None:
        report = self._session_reports.get(report_id)
        if not report:
            return

        # Form content summary. Never store credentials, tokens, or secrets.
        content = (
            f"n8n Integration Server status compiled\n"
            f"Status: {report.connectivity_status.upper()}\n"
            f"Version: {report.server_version}\n"
            f"Latency: {report.latency_ms}ms\n"
            f"Workflows Count: {report.uploaded_workflows_count}\n"
            f"Timestamp: {time.ctime(report.timestamp)}"
        )

        self._memory.add_memory(
            content=content,
            memory_type=MemoryType.PROJECT,
            tags=["n8n_integration", "health_monitor", "n8n_metadata"],
            importance=2,
            metadata_additional={
                "report_id": report_id,
                "server_version": report.server_version,
                "connectivity_status": report.connectivity_status,
                "latency_ms": report.latency_ms
            }
        )

    def publish_integration_report(self, report: N8NIntegrationReport) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publishing.")
            return

        report_md = (
            f"# Notion Sync - self-hosted n8n Integration Status\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Connectivity Status**: `{report.connectivity_status.upper()}`\n"
            f"**Server Version**: `{report.server_version}`\n"
            f"**Latency**: `{report.latency_ms:.1f}ms`\n"
            f"**Uploaded Workflows**: {report.uploaded_workflows_count}\n"
        )

        doc = KnowledgeDocument(
            document_id=f"int_report_{report.report_id}",
            title=f"n8n Integration Status - {report.report_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"int_report_{report.report_id}",
                timestamp=report.timestamp,
                source_subsystem="n8n_integration_service",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

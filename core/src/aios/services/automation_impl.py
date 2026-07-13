import logging
import os
import time
from typing import Any, Dict, List, Optional

from aios.services.ai_workspace import AIWorkspaceService
from aios.services.automation import (
    AutomationManager,
    AutomationProvider,
    AutomationProviderRegistry,
    AutomationRegistry,
    AutomationReport,
    AutomationResult,
    AutomationService,
    AutomationSession,
    AutomationValidator,
    GitHubActionsProvider,
    N8NProvider,
    TemporalProvider,
    WorkflowDefinition,
    WorkflowExecutionPolicy,
)
from aios.services.engineering_profile import EngineeringProfileService
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
    PersistenceStatus,
    WorkflowExecutionRepository,
    WorkflowRepository,
)

logger = logging.getLogger(__name__)


class LocalN8NProvider(N8NProvider):
    """Concrete provider stub for n8n platform integration."""

    @property
    def provider_id(self) -> str:
        return "n8n"

    def validate_definition(self, definition: WorkflowDefinition) -> List[str]:
        errors = []
        for cred in definition.credentials:
            if cred.provider_type != "n8n":
                errors.append(
                    f"Provider Compatibility: n8n provider cannot resolve credential reference '{cred.reference_id}' of type '{cred.provider_type}'."
                )
        return errors

    def execute_workflow(
        self, definition: WorkflowDefinition, session: AutomationSession
    ) -> AutomationResult:
        start_time = time.time()
        # Mock execution logic (interface only, no actual communication)
        output_data = {
            "workflow_executed": definition.name,
            "provider": "n8n",
            "status": "completed",
        }
        return AutomationResult(
            session_id=session.session_id,
            success=True,
            output_data=output_data,
            errors=[],
            execution_time=time.time() - start_time,
        )


class LocalGitHubActionsProvider(GitHubActionsProvider):
    """Concrete provider stub for GitHub Actions platform integration."""

    @property
    def provider_id(self) -> str:
        return "github_actions"

    def validate_definition(self, definition: WorkflowDefinition) -> List[str]:
        errors = []
        for cred in definition.credentials:
            if cred.provider_type != "github":
                errors.append(
                    f"Provider Compatibility: GitHub actions provider cannot resolve credential reference '{cred.reference_id}' of type '{cred.provider_type}'."
                )
        return errors

    def execute_workflow(
        self, definition: WorkflowDefinition, session: AutomationSession
    ) -> AutomationResult:
        start_time = time.time()
        # Mock execution logic
        output_data = {
            "workflow_executed": definition.name,
            "provider": "github_actions",
            "status": "run_success",
        }
        return AutomationResult(
            session_id=session.session_id,
            success=True,
            output_data=output_data,
            errors=[],
            execution_time=time.time() - start_time,
        )


class LocalTemporalProvider(TemporalProvider):
    """Concrete provider stub for Temporal orchestrator integration."""

    @property
    def provider_id(self) -> str:
        return "temporal"

    def validate_definition(self, definition: WorkflowDefinition) -> List[str]:
        errors = []
        for cred in definition.credentials:
            if cred.provider_type != "temporal":
                errors.append(
                    f"Provider Compatibility: Temporal provider cannot resolve credential reference '{cred.reference_id}' of type '{cred.provider_type}'."
                )
        return errors

    def execute_workflow(
        self, definition: WorkflowDefinition, session: AutomationSession
    ) -> AutomationResult:
        start_time = time.time()
        # Mock execution logic
        output_data = {
            "workflow_executed": definition.name,
            "provider": "temporal",
            "status": "workflow_completed",
        }
        return AutomationResult(
            session_id=session.session_id,
            success=True,
            output_data=output_data,
            errors=[],
            execution_time=time.time() - start_time,
        )


class LocalAutomationRegistry(AutomationRegistry):
    """Concrete workflow catalog container storing workflow definitions."""

    def __init__(self, registry: Optional[Any] = None) -> None:
        self._definitions: Dict[str, WorkflowDefinition] = {}
        self._repo: Optional[WorkflowRepository] = None
        if registry:
            try:
                self._repo = registry.get(WorkflowRepository)
            except Exception:
                pass

    def register_workflow(self, definition: WorkflowDefinition) -> None:
        self._definitions[definition.workflow_id] = definition
        if self._repo:
            try:
                wf_data = {
                    "id": definition.workflow_id,
                    "name": definition.name,
                    "description": definition.metadata.description if definition.metadata else "",
                    "metadata": {
                        "tags": definition.metadata.tags if definition.metadata else [],
                        "labels": definition.metadata.labels if definition.metadata else {},
                    },
                    "triggers": [
                        {
                            "trigger_id": t.trigger_id,
                            "trigger_type": t.trigger_type,
                            "config": t.config,
                        }
                        for t in definition.triggers
                    ],
                    "actions": [
                        {"action_id": a.action_id, "action_type": a.action_type, "config": a.config}
                        for a in definition.actions
                    ],
                    "conditions": [
                        {
                            "condition_id": c.condition_id,
                            "expression": c.expression,
                            "config": c.config,
                        }
                        for c in definition.conditions
                    ],
                    "variables": [
                        {
                            "name": v.name,
                            "value_type": v.value_type,
                            "default_value": v.default_value,
                        }
                        for v in definition.variables
                    ],
                    "policy": {
                        "max_retries": definition.policy.max_retries if definition.policy else 3,
                        "retry_delay_seconds": definition.policy.retry_delay_seconds
                        if definition.policy
                        else 10,
                        "timeout_seconds": definition.policy.timeout_seconds
                        if definition.policy
                        else 600,
                        "concurrency_limit": definition.policy.concurrency_limit
                        if definition.policy
                        else 1,
                    }
                    if definition.policy
                    else {},
                }
                self._repo.save(wf_data)
            except Exception:
                pass

    def get_workflow(self, workflow_id: str) -> Optional[WorkflowDefinition]:
        if workflow_id in self._definitions:
            return self._definitions[workflow_id]

        if self._repo:
            try:
                res = self._repo.get(workflow_id)
                if res.status == PersistenceStatus.SUCCESS and res.payload:
                    payload = res.payload
                    from aios.services.automation import (
                        WorkflowAction,
                        WorkflowCondition,
                        WorkflowDefinition,
                        WorkflowExecutionPolicy,
                        WorkflowGraph,
                        WorkflowMetadata,
                        WorkflowTrigger,
                        WorkflowVariable,
                    )

                    metadata = WorkflowMetadata(
                        tags=payload.get("metadata", {}).get("tags", []),
                        labels=payload.get("metadata", {}).get("labels", {}),
                        description=payload.get("description", ""),
                    )
                    triggers = [
                        WorkflowTrigger(t["trigger_id"], t["trigger_type"], t.get("config", {}))
                        for t in payload.get("triggers", [])
                    ]
                    actions = [
                        WorkflowAction(a["action_id"], a["action_type"], a.get("config", {}))
                        for a in payload.get("actions", [])
                    ]
                    conditions = [
                        WorkflowCondition(c["condition_id"], c["expression"], c.get("config", {}))
                        for c in payload.get("conditions", [])
                    ]
                    variables = [
                        WorkflowVariable(v["name"], v["value_type"], v.get("default_value"))
                        for v in payload.get("variables", [])
                    ]
                    policy = None
                    p_data = payload.get("policy")
                    if p_data:
                        policy = WorkflowExecutionPolicy(
                            max_retries=p_data.get("max_retries", 3),
                            retry_delay_seconds=p_data.get("retry_delay_seconds", 10),
                            timeout_seconds=p_data.get("timeout_seconds", 600),
                            concurrency_limit=p_data.get("concurrency_limit", 1),
                        )
                    definition = WorkflowDefinition(
                        workflow_id=payload["id"],
                        name=payload.get("name", ""),
                        graph=WorkflowGraph(),
                        triggers=triggers,
                        actions=actions,
                        conditions=conditions,
                        variables=variables,
                        policy=policy,
                        metadata=metadata,
                    )
                    self._definitions[workflow_id] = definition
                    return definition
            except Exception:
                pass
        return None


class LocalAutomationValidator(AutomationValidator):
    """Performs topological checks (cycles, disconnected nodes, and policy validity)."""

    def validate_workflow(self, definition: WorkflowDefinition) -> List[str]:
        errors = []
        graph = definition.graph

        # 1. Check duplicate node identifiers
        node_ids = set()
        for node in graph.nodes:
            if node.node_id in node_ids:
                errors.append(
                    f"Duplicate Identifier: Node ID '{node.node_id}' is declared multiple times."
                )
            node_ids.add(node.node_id)

        # 2. Check missing triggers or actions
        has_trigger = any(n.node_type == "trigger" for n in graph.nodes) or bool(
            definition.triggers
        )
        has_action = any(n.node_type == "action" for n in graph.nodes) or bool(definition.actions)

        if not has_trigger:
            errors.append("Validation Error: Workflow definition lacks trigger source nodes.")
        if not has_action:
            errors.append("Validation Error: Workflow definition lacks action execution nodes.")

        # 3. Graph integrity / Disconnected nodes
        incoming_counts = {node.node_id: 0 for node in graph.nodes}
        outgoing_counts = {node.node_id: 0 for node in graph.nodes}

        for edge in graph.edges:
            if edge.source_node_id not in incoming_counts:
                errors.append(
                    f"Integrity Error: Edge source '{edge.source_node_id}' does not exist in graph nodes list."
                )
                continue
            if edge.target_node_id not in incoming_counts:
                errors.append(
                    f"Integrity Error: Edge target '{edge.target_node_id}' does not exist in graph nodes list."
                )
                continue

            outgoing_counts[edge.source_node_id] += 1
            incoming_counts[edge.target_node_id] += 1

        for node in graph.nodes:
            # Non-trigger nodes should have incoming links
            if node.node_type != "trigger" and incoming_counts.get(node.node_id, 0) == 0:
                errors.append(
                    f"Disconnected Node: Action node '{node.node_id}' lacks incoming execution edges."
                )

        # 4. Cycle detection using simple DFS
        visited = {}
        rec_stack = {}

        def has_cycle(node_id: str) -> bool:
            visited[node_id] = True
            rec_stack[node_id] = True

            # find neighbors
            neighbors = [
                edge.target_node_id for edge in graph.edges if edge.source_node_id == node_id
            ]
            for n in neighbors:
                if not visited.get(n, False):
                    if has_cycle(n):
                        return True
                elif rec_stack.get(n, False):
                    return True

            rec_stack[node_id] = False
            return False

        for node in graph.nodes:
            if not visited.get(node.node_id, False):
                if has_cycle(node.node_id):
                    errors.append("Circular execution path detected in graph edges coupling.")
                    break

        # 5. Credential reference completeness
        for cred in definition.credentials:
            if not cred.credential_name:
                errors.append(
                    f"Credential Error: Credential reference '{cred.reference_id}' is missing a vault name."
                )

        # 6. Policy consistency
        if definition.policy:
            if definition.policy.max_retries < 0:
                errors.append("Execution Policy Error: max_retries count cannot be negative.")
            if definition.policy.retry_delay_seconds <= 0:
                errors.append(
                    "Execution Policy Error: retry_delay_seconds delay must be greater than zero."
                )
            if definition.policy.timeout_seconds <= 0:
                errors.append(
                    "Execution Policy Error: timeout_seconds threshold must be greater than zero."
                )

        return errors


class LocalAutomationManager(AutomationManager):
    """Instantiates automation sessions and delegates executions to provider stubs."""

    def __init__(
        self, providers: AutomationProviderRegistry, registry: LocalAutomationRegistry
    ) -> None:
        self._providers = providers
        self._registry = registry

    def create_session(self, workflow_id: str, workspace_id: str) -> AutomationSession:
        return AutomationSession(
            session_id=f"aut_sess_{int(time.time())}",
            workflow_id=workflow_id,
            workspace_id=workspace_id,
            status="pending",
            created_at=time.time(),
        )

    def execute_session(self, session: AutomationSession, provider_id: str) -> AutomationResult:
        workflow = self._registry.get_workflow(session.workflow_id)
        if not workflow:
            return AutomationResult(
                session_id=session.session_id,
                success=False,
                errors=[f"Workflow definition '{session.workflow_id}' not found in registry."],
            )

        provider = self._providers.get(provider_id)
        if not provider:
            return AutomationResult(
                session_id=session.session_id,
                success=False,
                errors=[f"Execution provider '{provider_id}' is not registered."],
            )

        # Provider compatibility validation
        comp_errors = provider.validate_definition(workflow)
        if comp_errors:
            return AutomationResult(
                session_id=session.session_id, success=False, errors=comp_errors
            )

        session.status = "running"
        result = provider.execute_workflow(workflow, session)
        session.status = "success" if result.success else "failed"
        session.closed_at = time.time()
        return result


class LocalAutomationService(AutomationService):
    """Central conductor service managing workflows, providers registry, and workspace logging."""

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

        self._providers = AutomationProviderRegistry()
        self._workflow_registry = LocalAutomationRegistry(registry)
        self._validator = LocalAutomationValidator()
        self._manager = LocalAutomationManager(self._providers, self._workflow_registry)

        self._sessions: Dict[str, AutomationSession] = {}
        self._reports: Dict[str, List[AutomationReport]] = {}
        self._exec_repo: Optional[WorkflowExecutionRepository] = None
        if registry:
            try:
                self._exec_repo = registry.get(WorkflowExecutionRepository)
            except Exception:
                pass

        # Register default stubs
        self.register_provider(LocalN8NProvider())
        self.register_provider(LocalGitHubActionsProvider())
        self.register_provider(LocalTemporalProvider())

    def initialize(self) -> None:
        logger.info("Initializing LocalAutomationService")

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

    def register_provider(self, provider: AutomationProvider) -> None:
        self._providers.register(provider)

    def run_automation(
        self, workflow_id: str, workspace_id: str, provider_id: str
    ) -> AutomationSession:
        logger.info(
            f"Submitting execution request for workflow '{workflow_id}' under workspace '{workspace_id}'"
        )

        workflow = self._workflow_registry.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow '{workflow_id}' is not registered in registry.")

        # 1. Topological Gating checks
        warnings = self._validator.validate_workflow(workflow)
        if warnings:
            logger.warning(f"Workflow topological warnings found: {warnings}")

        # Consume profiles configurations (naming, timeouts)
        profile_service = None
        timeout = 600
        retries = 3
        if self._registry:
            try:
                profile_service = self._registry.get(EngineeringProfileService)
            except Exception:
                pass

        if profile_service:
            prof = profile_service.get_active_profile()
            if prof and hasattr(prof, "automation"):
                retries = prof.automation.max_retries

        if not workflow.policy:
            workflow.policy = WorkflowExecutionPolicy(
                max_retries=retries,
                retry_delay_seconds=10,
                timeout_seconds=timeout,
                concurrency_limit=1,
            )

        # 2. Instantiates session
        session = self._manager.create_session(workflow_id, workspace_id)
        self._sessions[session.session_id] = session
        if self._exec_repo:
            try:
                self._exec_repo.save(
                    {
                        "id": session.session_id,
                        "workflow_id": session.workflow_id,
                        "workspace_id": session.workspace_id,
                        "status": session.status,
                        "created_at": session.created_at,
                    }
                )
            except Exception:
                pass

        # 3. Execute Workflow run
        result = self._manager.execute_session(session, provider_id)
        if self._exec_repo:
            try:
                self._exec_repo.save(
                    {
                        "id": session.session_id,
                        "workflow_id": session.workflow_id,
                        "workspace_id": session.workspace_id,
                        "status": session.status,
                        "success": 1 if result.success else 0,
                        "error_summary": ", ".join(result.errors) if result.errors else None,
                        "execution_time": result.execution_time,
                        "created_at": session.created_at,
                        "closed_at": session.closed_at,
                        "metadata": {"provider": provider_id, "output_data": result.output_data},
                    }
                )
            except Exception:
                pass

        # 4. AI Overview Refinement if active
        overview = f"Workflow '{workflow.name}' run completed using provider '{provider_id}'."
        if self._model:
            try:
                prompt = (
                    "You are the Lead Quality Automation Gating conductor.\n"
                    f"Workflow execution results details: {result.output_data}\n"
                    f"Success outcome: {result.success}\n\n"
                    "Provide a refined, professional execution overview. Return summary text only."
                )
                res = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output refined execution details.",
                        task_category="testing",
                    )
                )
                refined = res.content.strip()
                if refined:
                    overview = refined
            except Exception as e:
                logger.debug(f"LLM automation refinement failed: {e}")

        # 5. Form Report
        report = AutomationReport(
            report_id=f"rep_aut_{session.session_id}",
            workspace_id=workspace_id,
            session_id=session.session_id,
            workflow_name=workflow.name,
            status=session.status,
            error_summary=", ".join(result.errors) if result.errors else None,
            timestamp=time.time(),
        )

        if workspace_id not in self._reports:
            self._reports[workspace_id] = []
        self._reports[workspace_id].append(report)

        # 6. Save reports only inside isolated workspace
        report_md = (
            f"# Quality Automation Execution Report\n\n"
            f"**Session ID**: `{session.session_id}`\n"
            f"**Workflow Name**: `{workflow.name}`\n"
            f"**Provider**: `{provider_id}`\n"
            f"**Status Outcome**: `{session.status.upper()}`\n"
            f"**Total Run Time**: `{result.execution_time:.3f}s`\n\n"
            f"## Execution Overview\n{overview}\n\n"
            f"## Output Diagnostics\n"
            f"```json\n{result.output_data}\n```\n"
        )
        self._write_to_workspace(
            workspace_id, f"AUTOMATION_REPORT_{session.session_id}.md", report_md
        )

        try:
            from aios.services.persistence import SemanticMemoryManager

            sem_mgr = self._registry.get(SemanticMemoryManager) if self._registry else None
            if sem_mgr:
                metadata = {
                    "workspace_id": workspace_id,
                    "session_id": session.session_id,
                    "workflow_name": workflow.name,
                    "timestamp": time.time(),
                    "type": "automation_execution",
                }
                sem_mgr.index_memory(
                    repository_name="automation_memory",
                    entity_id=session.session_id,
                    text=report_md,
                    metadata=metadata,
                    tags=["automation", "run_report", workflow.name],
                )
        except Exception:
            pass

        return session

    def get_session(self, session_id: str) -> Optional[AutomationSession]:
        if session_id in self._sessions:
            return self._sessions[session_id]
        if self._exec_repo:
            try:
                res = self._exec_repo.get(session_id)
                if res.status == PersistenceStatus.SUCCESS and res.payload:
                    payload = res.payload
                    session = AutomationSession(
                        session_id=payload["id"],
                        workflow_id=payload.get("workflow_id", ""),
                        workspace_id=payload.get("workspace_id", ""),
                        status=payload.get("status", ""),
                        created_at=payload.get("created_at", time.time()),
                        closed_at=payload.get("closed_at"),
                    )
                    self._sessions[session_id] = session
                    return session
            except Exception:
                pass
        return None

    def get_history(self, workspace_id: str) -> List[AutomationReport]:
        if self._exec_repo:
            try:
                p_service = self._registry.get(PersistenceService)
                res = p_service.execute(
                    "SELECT * FROM workflow_executions WHERE workspace_id = ? AND status != 'telemetry'",
                    (workspace_id,),
                )
                reports = []
                for row in res:
                    r_id = f"rep_aut_{row['id']}"
                    reports.append(
                        AutomationReport(
                            report_id=r_id,
                            workspace_id=workspace_id,
                            session_id=row["id"],
                            workflow_name=row.get("workflow_id", ""),
                            status=row.get("status", ""),
                            error_summary=row.get("error_summary"),
                            timestamp=row.get("closed_at") or row.get("created_at") or time.time(),
                        )
                    )
                self._reports[workspace_id] = reports
                return reports
            except Exception:
                pass
        return self._reports.get(workspace_id, [])

    def store_automation_summary(self, session_id: str) -> None:
        session = self.get_session(session_id)
        if not session:
            return

        # Fetch report details
        reports = self.get_history(session.workspace_id)
        next((r for r in reports if r.session_id == session_id), None)

        # Form summary string. Never store credentials or source code.
        content = (
            f"Automation Execution Logged\n"
            f"Workspace ID: {session.workspace_id}\n"
            f"Session ID: {session_id}\n"
            f"Workflow ID: {session.workflow_id}\n"
            f"Run Status: {session.status.upper()}\n"
            f"Timestamp: {time.ctime(session.created_at)}"
        )

        self._memory.add_memory(
            content=content,
            memory_type=MemoryType.PROJECT,
            tags=["automation_execution", "workflow_run", "telemetry_logs"],
            importance=2,
            metadata_additional={
                "session_id": session_id,
                "workspace_id": session.workspace_id,
                "workflow_id": session.workflow_id,
                "status": session.status,
            },
        )

    def publish_automation_report(self, report: AutomationReport) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publishing.")
            return

        report_md = (
            f"# Notion Sync - Workflow Automation Run\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Session ID**: `{report.session_id}`\n"
            f"**Workflow Name**: `{report.workflow_name}`\n"
            f"**Status Outcome**: `{report.status.upper()}`\n"
        )

        doc = KnowledgeDocument(
            document_id=f"aut_report_{report.report_id}",
            title=f"Automation Run - {report.report_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"aut_report_{report.report_id}",
                timestamp=report.timestamp,
                source_subsystem="automation_intelligence_service",
                category="Project",
            ),
        )
        self._knowledge_hub.sync_document(doc, "notion")

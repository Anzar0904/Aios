import logging
import os
import time
from typing import Any, Dict, List, Optional

from aios.services.ai_workspace import AIWorkspaceService
from aios.services.automation import (
    WorkflowDefinition,
    WorkflowEdge,
    WorkflowExecutionPolicy,
    WorkflowGraph,
    WorkflowNode,
)
from aios.services.automation import (
    WorkflowMetadata as WFMetadata,
)
from aios.services.knowledge_hub import (
    KnowledgeDocument,
    KnowledgeHubService,
)
from aios.services.knowledge_hub import (
    KnowledgeMetadata as KHMetadata,
)
from aios.services.memory import MemoryService, MemoryType
from aios.services.model import LLMRequest, ModelService
from aios.services.workflow_planning import (
    WorkflowComposer,
    WorkflowDependencyResolver,
    WorkflowIntentAnalyzer,
    WorkflowOptimizer,
    WorkflowPlanner,
    WorkflowPlanningReport,
    WorkflowPlanningSession,
    WorkflowSuggestionEngine,
    WorkflowTemplate,
    WorkflowTemplateRegistry,
)

logger = logging.getLogger(__name__)


class LocalWorkflowIntentAnalyzer(WorkflowIntentAnalyzer):
    """Concrete intent analyzer mapping keywords to categories and tags."""

    def analyze_intent(self, intent: str) -> Dict[str, Any]:
        intent_lower = intent.lower()
        tags = []
        target = "notification"

        if "deploy" in intent_lower or "release" in intent_lower:
            tags.extend(["cd", "deploy"])
            target = "cd_pipeline"
        elif "test" in intent_lower or "pytest" in intent_lower or "ci" in intent_lower:
            tags.extend(["ci", "testing"])
            target = "testing_pipeline"
        elif "doc" in intent_lower or "notion" in intent_lower or "readme" in intent_lower:
            tags.extend(["documentation", "sync"])
            target = "documentation_sync"
        elif "security" in intent_lower or "scan" in intent_lower:
            tags.extend(["security", "audit"])
            target = "security_scan"
        elif "backup" in intent_lower or "database" in intent_lower:
            tags.extend(["backup", "db"])
            target = "backup"
        elif "review" in intent_lower or "approval" in intent_lower:
            tags.extend(["review", "approval"])
            target = "engineering_review"

        return {"target_template": target, "tags": tags, "parsed_intent": intent}


class LocalWorkflowDependencyResolver(WorkflowDependencyResolver):
    """Topological resolver ordering workflow nodes matching DAG dependencies."""

    def resolve_dependencies(self, nodes: List[WorkflowNode], edges: List[WorkflowEdge]) -> List[str]:
        # Simple topological sort
        visited = set()
        stack = []
        {n.node_id: n for n in nodes}

        # Build adjacency list
        adj = {n.node_id: [] for n in nodes}
        for edge in edges:
            if edge.source_node_id in adj and edge.target_node_id in adj:
                adj[edge.source_node_id].append(edge.target_node_id)

        def dfs(node_id: str):
            visited.add(node_id)
            for neighbor in adj.get(node_id, []):
                if neighbor not in visited:
                    dfs(neighbor)
            stack.insert(0, node_id)

        for n in nodes:
            if n.node_id not in visited:
                dfs(n.node_id)

        return stack


class LocalWorkflowOptimizer(WorkflowOptimizer):
    """Topological graph optimizer removing redundant or duplicate nodes."""

    def optimize_graph(self, nodes: List[WorkflowNode], edges: List[WorkflowEdge]) -> tuple[List[WorkflowNode], List[WorkflowEdge], List[str]]:
        optimizations = []
        optimized_nodes = []
        optimized_edges = list(edges)

        # 1. Merge duplicate actions (nodes sharing same name and type)
        seen_actions = {}
        merged_ids = {}

        for node in nodes:
            fingerprint = (node.node_type, node.name.lower())
            if fingerprint in seen_actions:
                primary_id = seen_actions[fingerprint]
                merged_ids[node.node_id] = primary_id
                optimizations.append(f"Merged duplicate node '{node.node_id}' into primary '{primary_id}'.")
            else:
                seen_actions[fingerprint] = node.node_id
                optimized_nodes.append(node)

        # Update edges based on merged nodes
        final_edges = []
        for edge in optimized_edges:
            src = merged_ids.get(edge.source_node_id, edge.source_node_id)
            tgt = merged_ids.get(edge.target_node_id, edge.target_node_id)
            
            # Avoid self loop after merging duplicates
            if src == tgt:
                optimizations.append("Removed self-loop edge resulting from duplicate nodes merge.")
                continue
            
            # Avoid duplicate edges
            dup_edge = any(e.source_node_id == src and e.target_node_id == tgt for e in final_edges)
            if dup_edge:
                optimizations.append(f"Removed redundant parallel edge '{edge.edge_id}' between '{src}' and '{tgt}'.")
                continue

            final_edges.append(
                WorkflowEdge(
                    edge_id=edge.edge_id,
                    source_node_id=src,
                    target_node_id=tgt,
                    condition=edge.condition
                )
            )

        # 2. Unreachable nodes clean-up (nodes having no incoming links except triggers)
        final_nodes = []
        incoming_counts = {n.node_id: 0 for n in optimized_nodes}
        for edge in final_edges:
            if edge.target_node_id in incoming_counts:
                incoming_counts[edge.target_node_id] += 1

        for n in optimized_nodes:
            if n.node_type != "trigger" and incoming_counts.get(n.node_id, 0) == 0:
                optimizations.append(f"Discarded unreachable node '{n.node_id}' with zero incoming dependencies.")
                # also discard its outgoing edges
                final_edges = [edge for edge in final_edges if edge.source_node_id != n.node_id]
            else:
                final_nodes.append(n)

        return final_nodes, final_edges, optimizations


class LocalWorkflowSuggestionEngine(WorkflowSuggestionEngine):
    """Suggests template IDs matching intent tags."""

    def suggest_templates(self, intent: str, registry: WorkflowTemplateRegistry) -> List[str]:
        suggestions = []
        intent_lower = intent.lower()
        
        for t_id in registry.list_templates():
            t = registry.get_template(t_id)
            if t:
                # Match tags or descriptions keyword
                if t_id in intent_lower or t.name.lower() in intent_lower:
                    suggestions.append(t_id)
                    
        if not suggestions:
            # Fallback to general notification
            suggestions.append("notification")
            
        return suggestions


class LocalWorkflowComposer(WorkflowComposer):
    """Instantiates template parameters into parameterised WorkflowDefinitions."""

    def compose_workflow(self, template: WorkflowTemplate, params: Dict[str, Any]) -> WorkflowDefinition:
        # Clone graph structures
        nodes = []
        for n in template.default_nodes:
            # Hydrate params if config matches target keys
            config = dict(n.config)
            for k, v in params.items():
                if k in config:
                    config[k] = v
            nodes.append(WorkflowNode(n.node_id, n.name, n.node_type, config))

        edges = list(template.default_edges)
        graph = WorkflowGraph(nodes, edges)

        return WorkflowDefinition(
            workflow_id=f"wf_{template.template_id}_{int(time.time())}",
            name=template.name,
            graph=graph,
            policy=WorkflowExecutionPolicy(max_retries=3, retry_delay_seconds=10, timeout_seconds=600, concurrency_limit=1),
            metadata=WFMetadata(tags=[template.template_id])
        )


class LocalWorkflowPlanner(WorkflowPlanner):
    """Conductor service managing planning pipelines, registry setups, and workspace documents."""

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

        self._template_registry = WorkflowTemplateRegistry()
        self._intent_analyzer = LocalWorkflowIntentAnalyzer()
        self._dependency_resolver = LocalWorkflowDependencyResolver()
        self._optimizer = LocalWorkflowOptimizer()
        self._suggestion_engine = LocalWorkflowSuggestionEngine()
        self._composer = LocalWorkflowComposer()

        self._sessions: Dict[str, WorkflowPlanningSession] = {}
        self._reports: Dict[str, List[WorkflowPlanningReport]] = {}

        # Register default templates
        self._register_default_templates()

    def _register_default_templates(self) -> None:
        # 1. CI Pipeline
        t_ci = WorkflowTemplate(
            template_id="testing_pipeline",
            name="CI Pipeline Template",
            description="Compiles build steps, lints source files, and executes pytest runs.",
            default_nodes=[
                WorkflowNode("trig_1", "Code Commit webhook", "trigger"),
                WorkflowNode("act_lint", "Lint script", "action", {"command": "flake8"}),
                WorkflowNode("act_test", "Pytest suite run", "action", {"command": "pytest"}),
                WorkflowNode("act_test", "Pytest duplicate suite run", "action", {"command": "pytest"}), # intentionally duplicated to verify optimization
            ],
            default_edges=[
                WorkflowEdge("e1", "trig_1", "act_lint"),
                WorkflowEdge("e2", "act_lint", "act_test")
            ]
        )
        self._template_registry.register_template(t_ci)

        # 2. CD Pipeline
        t_cd = WorkflowTemplate(
            template_id="cd_pipeline",
            name="CD Pipeline Template",
            description="Schedules build builds, triggers docker deployments, and reports outcomes.",
            default_nodes=[
                WorkflowNode("trig_cd", "Release Schedule", "trigger"),
                WorkflowNode("act_build", "Build Bundle", "action"),
                WorkflowNode("act_deploy", "Docker Deploy", "action")
            ],
            default_edges=[
                WorkflowEdge("e1", "trig_cd", "act_build"),
                WorkflowEdge("e2", "act_build", "act_deploy")
            ]
        )
        self._template_registry.register_template(t_cd)

        # 3. Documentation Sync
        t_doc = WorkflowTemplate(
            template_id="documentation_sync",
            name="Documentation Sync Template",
            description="Syncs Markdown reference specifications to Notion Knowledge Hub database.",
            default_nodes=[
                WorkflowNode("trig_doc", "Doc change event", "trigger"),
                WorkflowNode("act_gen_api", "Compile API Specs", "action"),
                WorkflowNode("act_notion", "Sync database", "action")
            ],
            default_edges=[
                WorkflowEdge("e1", "trig_doc", "act_gen_api"),
                WorkflowEdge("e2", "act_gen_api", "act_notion")
            ]
        )
        self._template_registry.register_template(t_doc)

        # 4. Engineering Review
        t_rev = WorkflowTemplate(
            template_id="engineering_review",
            name="Engineering Review Template",
            description="Aggregates Validation reports to run Approval policy rules gates.",
            default_nodes=[
                WorkflowNode("trig_rev", "Review webhook", "trigger"),
                WorkflowNode("act_val", "Validation metrics parsing", "action"),
                WorkflowNode("act_gate", "Policy rule checks", "action")
            ],
            default_edges=[
                WorkflowEdge("e1", "trig_rev", "act_val"),
                WorkflowEdge("e2", "act_val", "act_gate")
            ]
        )
        self._template_registry.register_template(t_rev)

        # 5. Backup
        t_bak = WorkflowTemplate(
            template_id="backup",
            name="Backup Database Template",
            description="Performs database snapshot and archives artifacts.",
            default_nodes=[
                WorkflowNode("trig_bak", "Daily Scheduler", "trigger"),
                WorkflowNode("act_db", "Snapshot SQLite database", "action"),
                WorkflowNode("act_arch", "Archive snapshots", "action")
            ],
            default_edges=[
                WorkflowEdge("e1", "trig_bak", "act_db"),
                WorkflowEdge("e2", "act_db", "act_arch")
            ]
        )
        self._template_registry.register_template(t_bak)

        # 6. Notification
        t_not = WorkflowTemplate(
            template_id="notification",
            name="Slack Notification Template",
            description="Broadcasts general status alerts to Slack.",
            default_nodes=[
                WorkflowNode("trig_not", "Gating update event", "trigger"),
                WorkflowNode("act_slack", "Notify Slack channel", "action")
            ],
            default_edges=[
                WorkflowEdge("e1", "trig_not", "act_slack")
            ]
        )
        self._template_registry.register_template(t_not)

    def initialize(self) -> None:
        logger.info("Initializing LocalWorkflowPlanner")

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

        planners_dir = os.path.join(workspace_root, "docs", "planners")
        os.makedirs(planners_dir, exist_ok=True)
        
        file_path = os.path.join(planners_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return file_path

    def create_planning_session(self, workspace_id: str, intent: str) -> WorkflowPlanningSession:
        session = WorkflowPlanningSession(
            session_id=f"plan_sess_{int(time.time())}",
            workspace_id=workspace_id,
            intent=intent,
            status="open",
            created_at=time.time()
        )
        self._sessions[session.session_id] = session
        return session

    def generate_plan(self, session: WorkflowPlanningSession) -> WorkflowPlanningReport:
        logger.info(f"Generating workflow planning for session '{session.session_id}' (intent: '{session.intent}')")

        # 1. Analyze Intent
        analysis = self._intent_analyzer.analyze_intent(session.intent)
        target_template_id = analysis["target_template"]

        # 2. Retrieve Template
        template = self._template_registry.get_template(target_template_id)
        if not template:
            # Fallback to general notification
            template = self._template_registry.get_template("notification")

        # 3. Suggest related templates
        suggested = self._suggestion_engine.suggest_templates(session.intent, self._template_registry)

        # 4. Compose parameterised Graph
        wf = self._composer.compose_workflow(template, {})

        # 5. Resolve dependency ordering (topological sort)
        ordered_ids = self._dependency_resolver.resolve_dependencies(wf.graph.nodes, wf.graph.edges)

        # 6. Optimize graph (duplicate merges, unreachable discards)
        opt_nodes, opt_edges, optimizations = self._optimizer.optimize_graph(wf.graph.nodes, wf.graph.edges)
        wf.graph.nodes = opt_nodes
        wf.graph.edges = opt_edges

        # 7. Write planning artifacts inside AI Workspace ONLY
        plan_desc = f"Planned execution graph for template '{target_template_id}' consisting of {len(opt_nodes)} nodes."
        if self._model:
            try:
                prompt = (
                    "You are the Principal Workflow Architect for the Personal AI OS.\n"
                    f"Planned nodes: {ordered_ids}\n"
                    f"Optimization details: {optimizations}\n\n"
                    "Provide a refined outline and summary of the dependencies. Return refined overview text only."
                )
                res = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output workflow outline summaries.",
                        task_category="testing"
                    )
                )
                refined = res.content.strip()
                if refined:
                    plan_desc = refined
            except Exception as e:
                logger.debug(f"LLM workflow plan overview refinement failed: {e}")

        # Construct Report
        report = WorkflowPlanningReport(
            report_id=f"rep_plan_{session.session_id}",
            session_id=session.session_id,
            workspace_id=session.workspace_id,
            raw_intent=session.intent,
            resolved_dependencies=ordered_ids,
            optimization_recommendations=optimizations,
            suggested_templates=suggested,
            planned_workflow_id=wf.workflow_id,
            timestamp=time.time()
        )

        if session.workspace_id not in self._reports:
            self._reports[session.workspace_id] = []
        self._reports[session.workspace_id].append(report)

        # Save Report Markdown inside AI Workspace ONLY
        nodes_md = "\n".join(f"- `{n.node_id}` ({n.name} of type `{n.node_type}`)" for n in opt_nodes)
        opts_md = "\n".join(f"- {opt}" for opt in optimizations)

        report_md = (
            f"# Workflow Planning Execution Report\n\n"
            f"**Session ID**: `{session.session_id}`\n"
            f"**Planned Workflow ID**: `{wf.workflow_id}`\n"
            f"**Workspace ID**: `{session.workspace_id}`\n\n"
            f"## Planned Summary\n{plan_desc}\n\n"
            f"## Execution Topological Nodes\n" + (nodes_md if nodes_md else "- *None.*") + "\n\n"
            "## Applied Optimization Recommendations\n" + (opts_md if opts_md else "- *None.*")
        )
        self._write_to_workspace(session.workspace_id, f"PLANNING_REPORT_{session.session_id}.md", report_md)

        session.status = "closed"
        session.closed_at = time.time()
        return report

    def get_session(self, session_id: str) -> Optional[WorkflowPlanningSession]:
        return self._sessions.get(session_id)

    def get_history(self, workspace_id: str) -> List[WorkflowPlanningReport]:
        return self._reports.get(workspace_id, [])

    def store_planning_summary(self, session_id: str) -> None:
        session = self.get_session(session_id)
        if not session:
            return

        reports = self.get_history(session.workspace_id)
        target_report = next((r for r in reports if r.session_id == session_id), None)
        opts_count = len(target_report.optimization_recommendations) if target_report else 0

        # Form content summary string. Never store credentials or source code.
        content = (
            f"Workflow Plan Registered\n"
            f"Workspace ID: {session.workspace_id}\n"
            f"Session ID: {session_id}\n"
            f"Raw Intent: {session.intent}\n"
            f"Optimizations Applied: {opts_count}\n"
            f"Timestamp: {time.ctime(session.created_at)}"
        )

        self._memory.add_memory(
            content=content,
            memory_type=MemoryType.PROJECT,
            tags=["workflow_planning", "topological_plans", "automation_metadata"],
            importance=2,
            metadata_additional={
                "session_id": session_id,
                "workspace_id": session.workspace_id,
                "optimizations_count": opts_count,
                "workflow_id": target_report.planned_workflow_id if target_report else ""
            }
        )

    def publish_planning_report(self, report: WorkflowPlanningReport) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publishing.")
            return

        report_md = (
            f"# Notion Sync - Workflow Plan Outline\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Workspace ID**: `{report.workspace_id}`\n"
            f"**Raw Intent**: `{report.raw_intent}`\n"
            f"**Planned Workflow ID**: `{report.planned_workflow_id}`\n\n"
            f"## Applied Optimizations Count: {len(report.optimization_recommendations)}\n"
        )

        doc = KnowledgeDocument(
            document_id=f"plan_report_{report.report_id}",
            title=f"Workflow Plan - {report.report_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"plan_report_{report.report_id}",
                timestamp=report.timestamp,
                source_subsystem="workflow_planning_service",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

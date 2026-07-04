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
from aios.services.automation import WorkflowDefinition
from aios.services.n8n_translation import (
    WorkflowIR,
    TranslationContext,
    TranslationReport,
    N8NNodeMapper,
    N8NConnectionMapper,
    N8NExpressionBuilder,
    N8NCredentialMapper,
    N8NWorkflowBuilder,
    TranslationValidator,
    WorkflowCompiler,
    WorkflowSerializer,
    N8NTranslationEngine,
    WorkflowTranslator,
)

logger = logging.getLogger(__name__)


class LocalN8NNodeMapper(N8NNodeMapper):
    """Concrete node mapper converting IR nodes into n8n native node schemas."""

    def map_node(self, node: Dict[str, Any], context: TranslationContext) -> Dict[str, Any]:
        node_id = node.get("node_id", "")
        node_type = node.get("node_type", "")
        name = node.get("name", "")
        config = node.get("config", {})

        n8n_type = "n8n-nodes-base.manualTrigger"
        parameters = {}

        if node_type == "trigger":
            trig_type = config.get("trigger_type", "manual")
            if trig_type == "webhook":
                n8n_type = "n8n-nodes-base.webhook"
                parameters = {"path": config.get("path", f"webhook-{node_id}"), "httpMethod": "POST"}
            elif trig_type == "schedule":
                n8n_type = "n8n-nodes-base.cron"
                parameters = {"triggerTimes": {"item": [{"mode": "everyMinute"}]}}
        elif node_type == "action":
            act_type = config.get("action_type", "httpRequest")
            if act_type == "http_request":
                n8n_type = "n8n-nodes-base.httpRequest"
                parameters = {"url": config.get("url", "https://api.example.com"), "method": "GET"}
            elif act_type == "script" or act_type == "code":
                n8n_type = "n8n-nodes-base.code"
                parameters = {"jsCode": config.get("script_content", "return item;")}
            elif act_type == "slack" or act_type == "notify":
                n8n_type = "n8n-nodes-base.slack"
                parameters = {"message": config.get("message", "Workflow update notification.")}
            elif act_type == "email":
                n8n_type = "n8n-nodes-base.emailSend"
                parameters = {"toEmail": config.get("to", "recipient@example.com")}
            elif act_type == "github":
                n8n_type = "n8n-nodes-base.github"
                parameters = {"operation": "createPullRequest"}
        elif node_type == "condition":
            n8n_type = "n8n-nodes-base.if"
            parameters = {
                "conditions": {
                    "string": [
                        {
                            "value1": config.get("expression", ""),
                            "value2": "true"
                        }
                    ]
                }
            }

        return {
            "id": node_id,
            "name": name,
            "type": n8n_type,
            "typeVersion": 1,
            "position": [250, 250],
            "parameters": parameters
        }


class LocalTranslationValidator(TranslationValidator):
    """Integrity checking validator validating JSON schemas and edge connection links."""

    def validate_translation(self, ir: WorkflowIR, n8n_json: Dict[str, Any]) -> List[str]:
        errors = []

        # 1. Check schema presence
        if not n8n_json or "nodes" not in n8n_json or "connections" not in n8n_json:
            errors.append("Schema Error: Generated payload lacks nodes or connections properties.")
            return errors

        # 2. Duplicate node IDs
        seen_ids = set()
        node_names = set()
        for node in n8n_json["nodes"]:
            n_id = node.get("id")
            name = node.get("name")
            if n_id in seen_ids:
                errors.append(f"Duplicate Node ID: Node ID '{n_id}' is mapped multiple times.")
            seen_ids.add(n_id)
            node_names.add(name)

        # 3. Broken connections
        connections = n8n_json["connections"]
        for src_name, targets in connections.items():
            if src_name not in node_names:
                errors.append(f"Broken Connection: Source node name '{src_name}' does not match any node.")
            for conn_type, links in targets.items():
                for link_list in links:
                    for link in link_list:
                        tgt_name = link.get("node")
                        if tgt_name not in node_names:
                            errors.append(f"Broken Connection: Target node name '{tgt_name}' does not match any node.")

        return errors


class LocalWorkflowCompiler(WorkflowCompiler):
    """Compiles WorkflowDefinitions into intermediate canonical IR maps."""

    def compile_definition_to_ir(self, definition: WorkflowDefinition) -> WorkflowIR:
        nodes = []
        for n in definition.graph.nodes:
            nodes.append({
                "node_id": n.node_id,
                "name": n.name,
                "node_type": n.node_type,
                "config": n.config
            })

        edges = []
        for e in definition.graph.edges:
            edges.append({
                "edge_id": e.edge_id,
                "source_node_id": e.source_node_id,
                "target_node_id": e.target_node_id,
                "condition": e.condition
            })

        variables = {}
        for var in definition.variables:
            variables[var.name] = {
                "value_type": var.value_type,
                "default_value": var.default_value
            }

        metadata = {
            "tags": definition.metadata.tags if definition.metadata else [],
            "description": definition.metadata.description if definition.metadata else ""
        }

        policy = {
            "max_retries": definition.policy.max_retries if definition.policy else 3,
            "timeout_seconds": definition.policy.timeout_seconds if definition.policy else 600
        }

        return WorkflowIR(
            ir_id=f"ir_{definition.workflow_id}",
            workflow_id=definition.workflow_id,
            name=definition.name,
            nodes=nodes,
            edges=edges,
            variables=variables,
            metadata=metadata,
            policy=policy
        )


class LocalWorkflowSerializer(WorkflowSerializer):
    """Pretty prints output JSON to file buffers."""

    def serialize_to_json_string(self, n8n_json: Dict[str, Any]) -> str:
        return json.dumps(n8n_json, indent=2)


class LocalN8NTranslationEngine(N8NTranslationEngine):
    """Drives node translations and connections mappings."""

    def __init__(self) -> None:
        self.node_mapper = LocalN8NNodeMapper()
        self.connection_mapper = N8NConnectionMapper()
        self.credential_mapper = N8NCredentialMapper()
        self.builder = N8NWorkflowBuilder()

    def translate_ir(self, ir: WorkflowIR, context: TranslationContext) -> Dict[str, Any]:
        translated_nodes = []
        node_id_to_name = {}

        # 1. Map nodes
        for node in ir.nodes:
            n8n_node = self.node_mapper.map_node(node, context)
            translated_nodes.append(n8n_node)
            node_id_to_name[node["node_id"]] = n8n_node["name"]

        # 2. Map credentials
        for node in translated_nodes:
            # Match credentials references if node config matches
            pass

        # 3. Map connections (edges endpoints)
        # We need to map IR edge IDs (IDs) to n8n connections (Node Names)
        edges_named = []
        for edge in ir.edges:
            src_name = node_id_to_name.get(edge["source_node_id"])
            tgt_name = node_id_to_name.get(edge["target_node_id"])
            if src_name and tgt_name:
                edges_named.append({
                    "edge_id": edge["edge_id"],
                    "source_node_id": src_name,
                    "target_node_id": tgt_name
                })

        connections = self.connection_mapper.map_connections(edges_named, context)

        # 4. Build final JSON
        return self.builder.build_workflow_json(ir, translated_nodes, connections, context)


class LocalWorkflowTranslator(WorkflowTranslator):
    """Coordinating gateway compiling definitions and storing execution logs."""

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

        self._compiler = LocalWorkflowCompiler()
        self._engine = LocalN8NTranslationEngine()
        self._validator = LocalTranslationValidator()
        self._serializer = LocalWorkflowSerializer()

        self._reports: Dict[str, List[TranslationReport]] = {}
        self._session_reports: Dict[str, TranslationReport] = {}

    def initialize(self) -> None:
        logger.info("Initializing LocalWorkflowTranslator")

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

    def translate_workflow(self, definition: WorkflowDefinition, workspace_id: str) -> TranslationReport:
        logger.info(f"Submitting translation for workflow '{definition.workflow_id}' under workspace '{workspace_id}'")

        # 1. Compile Definition to IR canonical representation
        ir = self._compiler.compile_definition_to_ir(definition)

        # 2. Drive translation
        session_id = f"trans_sess_{int(time.time())}"
        context = TranslationContext(workspace_id, session_id)
        n8n_json = self._engine.translate_ir(ir, context)

        # 3. Validate
        errors = self._validator.validate_translation(ir, n8n_json)
        context.errors.extend(errors)

        # 4. Serialize
        json_str = self._serializer.serialize_to_json_string(n8n_json)

        # 5. Write artifacts only inside workspace
        json_file = f"N8N_WORKFLOW_{definition.workflow_id}.json"
        json_path = self._write_to_workspace(workspace_id, json_file, json_str)

        # 6. LLM overview refinement if active
        overview = f"Workflow '{definition.name}' compiled to intermediate representation successfully."
        if self._model:
            try:
                prompt = (
                    "You are the Lead n8n Translation pipeline architect.\n"
                    f"Workflow IR Nodes: {ir.nodes}\n"
                    f"Generated Connections: {n8n_json.get('connections')}\n\n"
                    "Provide a refined outline and summary of the compiled results. Return summary text only."
                )
                res = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output translation outline details.",
                        task_category="testing"
                    )
                )
                refined = res.content.strip()
                if refined:
                    overview = refined
            except Exception as e:
                logger.debug(f"LLM translation refinement failed: {e}")

        # Compile report
        report = TranslationReport(
            report_id=f"rep_trans_{session_id}",
            session_id=session_id,
            workspace_id=workspace_id,
            node_count=len(ir.nodes),
            connection_count=len(ir.edges),
            warnings=context.errors,
            n8n_json_file_path=json_path,
            timestamp=time.time()
        )

        if workspace_id not in self._reports:
            self._reports[workspace_id] = []
        self._reports[workspace_id].append(report)
        self._session_reports[report.report_id] = report

        # Write Report Markdown inside AI Workspace ONLY
        warns_md = "\n".join(f"- {w}" for w in context.errors)
        report_md = (
            f"# n8n Translation Pipeline Execution Report\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Workspace ID**: `{workspace_id}`\n"
            f"**Output JSON target**: `{json_file}`\n\n"
            f"## Compilation Overview\n{overview}\n\n"
            f"## Compilation Statistics\n"
            f"- **Node Count**: {report.node_count}\n"
            f"- **Connection Count**: {report.connection_count}\n\n"
            f"## Compilation Warnings/Errors\n" + (warns_md if warns_md else "- *None.*")
        )
        self._write_to_workspace(workspace_id, f"TRANSLATION_REPORT_{definition.workflow_id}.md", report_md)

        return report

    def get_history(self, workspace_id: str) -> List[TranslationReport]:
        return self._reports.get(workspace_id, [])

    def store_translation_summary(self, report_id: str) -> None:
        report = self._session_reports.get(report_id)
        if not report:
            return

        # Form content summary. Never store credentials or source code.
        content = (
            f"Workflow Compiled to n8n JSON\n"
            f"Workspace ID: {report.workspace_id}\n"
            f"Report ID: {report_id}\n"
            f"Node Count: {report.node_count}\n"
            f"Connection Count: {report.connection_count}\n"
            f"JSON Target: {report.n8n_json_file_path}\n"
            f"Timestamp: {time.ctime(report.timestamp)}"
        )

        self._memory.add_memory(
            content=content,
            memory_type=MemoryType.PROJECT,
            tags=["n8n_translation", "workflow_ir", "translation_stats"],
            importance=2,
            metadata_additional={
                "report_id": report_id,
                "workspace_id": report.workspace_id,
                "node_count": report.node_count,
                "connection_count": report.connection_count
            }
        )

    def publish_translation_report(self, report: TranslationReport) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publishing.")
            return

        report_md = (
            f"# Notion Sync - Workflow Translation Compiler\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Workspace ID**: `{report.workspace_id}`\n"
            f"**Compiled Nodes**: {report.node_count}\n"
            f"**Compiled Connections**: {report.connection_count}\n"
            f"**Output Path**: `{report.n8n_json_file_path}`\n"
        )

        doc = KnowledgeDocument(
            document_id=f"trans_report_{report.report_id}",
            title=f"Workflow Translation - {report.report_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"trans_report_{report.report_id}",
                timestamp=report.timestamp,
                source_subsystem="n8n_translation_service",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

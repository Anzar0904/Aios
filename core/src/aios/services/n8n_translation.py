import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List

from aios.services.automation import WorkflowDefinition
from aios.services.base import ServiceLifecycle


@dataclass
class WorkflowIR:
    """Canonical Intermediate Representation (IR) of a workflow."""
    ir_id: str
    workflow_id: str
    name: str
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    variables: Dict[str, Any]
    metadata: Dict[str, Any]
    policy: Dict[str, Any]


@dataclass
class TranslationContext:
    """Carries local session state variables, configurations and validation errors."""
    workspace_id: str
    session_id: str
    variables_mapping: Dict[str, str] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


@dataclass
class TranslationReport:
    """Outcome report describing compiles count, warnings, and path targets."""
    report_id: str
    session_id: str
    workspace_id: str
    node_count: int
    connection_count: int
    warnings: List[str]
    n8n_json_file_path: str
    timestamp: float


class N8NNodeMapper(abc.ABC):
    """Maps custom node configurations to native n8n schema specifications."""

    @abc.abstractmethod
    def map_node(self, node: Dict[str, Any], context: TranslationContext) -> Dict[str, Any]:
        """Translates node parameters to n8n parameters format."""
        pass


class N8NConnectionMapper:
    """Compiles workflow edges into main execution connection structures."""

    def map_connections(self, edges: List[Dict[str, Any]], context: TranslationContext) -> Dict[str, Any]:
        connections = {}
        for edge in edges:
            src = edge.get("source_node_id")
            tgt = edge.get("target_node_id")
            if not src or not tgt:
                context.errors.append(f"Connection Error: Edge '{edge.get('edge_id')}' has missing endpoints.")
                continue

            # n8n connection schema
            if src not in connections:
                connections[src] = {"main": [[]]}
            connections[src]["main"][0].append({
                "node": tgt,
                "type": "main",
                "index": 0
            })
        return connections


class N8NExpressionBuilder:
    """Parses expressions into evaluation parameters."""

    def build_expression(self, expression: str, context: TranslationContext) -> str:
        # Translates logic expressions into n8n JS expressions format: ={{ $json["variable"] }}
        return f"={{{{ {expression} }}}}"


class N8NCredentialMapper:
    """Associates credential vault pointers to secure nodes properties."""

    def map_credential(self, cred_ref: Dict[str, Any], context: TranslationContext) -> Dict[str, Any]:
        name = cred_ref.get("credential_name")
        p_type = cred_ref.get("provider_type")
        
        # Maps providers into n8n credential formats
        n8n_cred_name = "n8nApi"
        if p_type == "github":
            n8n_cred_name = "gitHubApi"
        elif p_type == "temporal":
            n8n_cred_name = "temporalApi"

        return {
            n8n_cred_name: {
                "id": f"cred_id_{name}",
                "name": name
            }
        }


class N8NWorkflowBuilder:
    """Constructs final JSON payloads compliant with n8n schema standards."""

    def build_workflow_json(
        self, 
        ir: WorkflowIR, 
        nodes: List[Dict[str, Any]], 
        connections: Dict[str, Any], 
        context: TranslationContext
    ) -> Dict[str, Any]:
        return {
            "name": ir.name,
            "nodes": nodes,
            "connections": connections,
            "active": True,
            "settings": {
                "executionTimeout": ir.policy.get("timeout_seconds", 3600)
            },
            "tags": ir.metadata.get("tags", [])
        }


class TranslationValidator(abc.ABC):
    """Verifies generated JSON integrity, schemas, and missing nodes mappings."""

    @abc.abstractmethod
    def validate_translation(self, ir: WorkflowIR, n8n_json: Dict[str, Any]) -> List[str]:
        """Runs checks against connections, duplicate node mappings, and n8n JSON formats."""
        pass


class WorkflowCompiler(abc.ABC):
    """Compiles high-level WorkflowDefinitions into intermediate canonical IR."""

    @abc.abstractmethod
    def compile_definition_to_ir(self, definition: WorkflowDefinition) -> WorkflowIR:
        """Translates workflow template configuration definition to IR."""
        pass


class WorkflowSerializer(abc.ABC):
    """Serializes execution payloads."""

    @abc.abstractmethod
    def serialize_to_json_string(self, n8n_json: Dict[str, Any]) -> str:
        """Returns pretty JSON output format."""
        pass


class N8NTranslationEngine(abc.ABC):
    """Translates canonical WorkflowIR components using registers node mappers."""

    @abc.abstractmethod
    def translate_ir(self, ir: WorkflowIR, context: TranslationContext) -> Dict[str, Any]:
        """Produces n8n execution diagram JSON."""
        pass


class WorkflowTranslator(ServiceLifecycle, abc.ABC):
    """Main gateway coordinating translation runs, memory stores, and reports updates."""

    @abc.abstractmethod
    def translate_workflow(self, definition: WorkflowDefinition, workspace_id: str) -> TranslationReport:
        """Executes full translation compiler pipeline, writes workspace reports and json target."""
        pass

    @abc.abstractmethod
    def get_history(self, workspace_id: str) -> List[TranslationReport]:
        """Retrieves history runs reports."""
        pass

    @abc.abstractmethod
    def store_translation_summary(self, report_id: str) -> None:
        """Saves metadata statistics inside memory. Never stores source code/credentials."""
        pass

    @abc.abstractmethod
    def publish_translation_report(self, report: TranslationReport) -> None:
        """Synchronizes report page details to Notion on-demand."""
        pass

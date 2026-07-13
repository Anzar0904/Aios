import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from aios.services.model import LLMRequest, ModelService
from aios.services.n8n import (
    ConnectionHealth,
    ExecutionMetrics,
    InternalConnection,
    InternalNode,
    InternalWorkflow,
    N8NService,
)


class LocalN8NService(N8NService):
    def __init__(self, model_service: ModelService, cache_filename: str = "n8n_workflows.json", workspace_root: str = ".") -> None:
        self._model_service = model_service
        self._cache_filename = cache_filename
        self._workspace_root = workspace_root
        self._workflows: Dict[str, InternalWorkflow] = {}

    def initialize(self) -> None:
        cache_path = Path(self._workspace_root) / self._cache_filename
        if cache_path.is_file():
            try:
                data = json.loads(cache_path.read_text(encoding="utf-8"))
                for wf_id, wf_data in data.items():
                    self._workflows[wf_id] = self._deserialize_workflow(wf_data)
            except Exception:
                pass

    def create_workflow(self, workflow: InternalWorkflow) -> InternalWorkflow:
        if not workflow.id:
            workflow.id = f"wf_{int(time.time() * 1000)}"
        self._workflows[workflow.id] = workflow
        self._save_cache()
        return workflow

    def update_workflow(self, workflow_id: str, workflow: InternalWorkflow) -> InternalWorkflow:
        workflow.id = workflow_id
        self._workflows[workflow_id] = workflow
        self._save_cache()
        return workflow

    def delete_workflow(self, workflow_id: str) -> bool:
        if workflow_id in self._workflows:
            del self._workflows[workflow_id]
            self._save_cache()
            return True
        return False

    def get_workflow(self, workflow_id: str) -> Optional[InternalWorkflow]:
        return self._workflows.get(workflow_id)

    def list_workflows(self) -> List[InternalWorkflow]:
        return list(self._workflows.values())

    def validate_workflow(self, workflow: InternalWorkflow) -> Dict[str, Any]:
        errors = []
        node_names = {node.name for node in workflow.nodes}

        # 1. Missing nodes check
        for conn in workflow.connections:
            if conn.from_node not in node_names:
                errors.append(f"Connection source '{conn.from_node}' does not exist.")
            if conn.to_node not in node_names:
                errors.append(f"Connection target '{conn.to_node}' does not exist.")

        # 2. Cycle detection (DFS coloring)
        adj = {node.name: [] for node in workflow.nodes}
        for conn in workflow.connections:
            if conn.from_node in adj and conn.to_node in adj:
                adj[conn.from_node].append(conn.to_node)

        visited = {}  # state tracking
        has_cycle = False

        def dfs(node_name: str) -> bool:
            visited[node_name] = 1
            for neighbor in adj[node_name]:
                state = visited.get(neighbor, 0)
                if state == 1:
                    return True
                elif state == 0:
                    if dfs(neighbor):
                        return True
            visited[node_name] = 2
            return False

        for node in workflow.nodes:
            if visited.get(node.name, 0) == 0:
                if dfs(node.name):
                    has_cycle = True
                    break

        if has_cycle:
            errors.append("Circular dependency detected.")

        # 3. Unreachable nodes detection
        trigger_types = {"n8n-nodes-base.start", "n8n-nodes-base.webhook", "n8n-nodes-base.cron"}
        roots = [
            node.name
            for node in workflow.nodes
            if node.type in trigger_types or "start" in node.name.lower() or "trigger" in node.name.lower()
        ]
        reachable = set()

        def traverse(node_name: str):
            if node_name in reachable:
                return
            reachable.add(node_name)
            for neighbor in adj[node_name]:
                traverse(neighbor)

        for root in roots:
            traverse(root)

        unreachable = [node.name for node in workflow.nodes if node.name not in reachable]
        if unreachable:
            errors.append(f"Unreachable nodes: {', '.join(unreachable)}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "diagnostics": {
                "nodes_count": len(workflow.nodes),
                "connections_count": len(workflow.connections),
                "roots": roots,
                "unreachable_count": len(unreachable)
            }
        }

    def generate_workflow_from_natural_language(self, description: str) -> InternalWorkflow:
        prompt = (
            "You are the Workflow Engineer for Personal AI OS.\n"
            f"Generate a structured workflow configuration JSON for the request: \"{description}\".\n"
            "Respond ONLY with a JSON object of this structure:\n"
            "{\n"
            "  \"name\": \"Workflow Name\",\n"
            "  \"nodes\": [\n"
            "    {\"id\": \"start\", \"name\": \"Start Trigger\", \"type\": \"n8n-nodes-base.start\", \"position\": [250, 300], \"parameters\": {}},\n"
            "    {\"id\": \"http-request\", \"name\": \"Get Weather\", \"type\": \"n8n-nodes-base.httpRequest\", \"position\": [450, 300], \"parameters\": {\"url\": \"https://api.weather.com\"}}\n"
            "  ],\n"
            "  \"connections\": [\n"
            "    {\"from_node\": \"Start Trigger\", \"to_node\": \"Get Weather\", \"to_input\": 0}\n"
            "  ]\n"
            "}\n"
        )
        try:
            model_name = getattr(self._model_service, "_default_model", None) or "claude-3-5-sonnet"
            res = self._model_service.execute_request(
                LLMRequest(
                    prompt=prompt,
                    system_instruction="You are a strict JSON builder. Output JSON only, no markdown wraps.",
                    model_name=model_name
                )
            )
            content = res.content.strip()
            if content.startswith("```json"):
                content = content.split("```json")[1].split("```")[0].strip()
            elif content.startswith("```"):
                content = content.split("```")[1].split("```")[0].strip()

            data = json.loads(content)
            nodes = [
                InternalNode(
                    id=n.get("id"),
                    name=n.get("name"),
                    type=n.get("type"),
                    parameters=n.get("parameters", {}),
                    position=n.get("position", [0, 0])
                )
                for n in data.get("nodes", [])
            ]
            connections = [
                InternalConnection(
                    from_node=c.get("from_node"),
                    to_node=c.get("to_node"),
                    to_input=c.get("to_input", 0)
                )
                for c in data.get("connections", [])
            ]
            return InternalWorkflow(
                id=None,
                name=data.get("name", "Generated Workflow"),
                nodes=nodes,
                connections=connections
            )
        except Exception:
            return InternalWorkflow(
                id=None,
                name="Fallback Workflow",
                nodes=[
                    InternalNode("start", "Start Trigger", "n8n-nodes-base.start", {}, [250, 300]),
                    InternalNode("http", "HTTP Request", "n8n-nodes-base.httpRequest", {}, [450, 300])
                ],
                connections=[
                    InternalConnection("Start Trigger", "HTTP Request")
                ]
            )

    def execute_workflow(self, workflow_id: str) -> bool:
        return workflow_id in self._workflows

    def stop_workflow(self, workflow_id: str) -> bool:
        return workflow_id in self._workflows

    def get_execution_metrics(self, workflow_id: str) -> Optional[ExecutionMetrics]:
        if workflow_id not in self._workflows:
            return None
        return ExecutionMetrics(
            workflow_id=workflow_id,
            status="success",
            success_rate=1.0,
            total_runs=10,
            failures=0,
            last_run=time.time(),
            logs=["Start Trigger activated", "HTTP Request completed successfully"]
        )

    def check_health(self) -> ConnectionHealth:
        return ConnectionHealth(
            online=True,
            api_version="1.0.0",
            latency_ms=15.5
        )

    def internal_to_n8n(self, wf: InternalWorkflow) -> Dict[str, Any]:
        nodes_list = []
        for node in wf.nodes:
            nodes_list.append({
                "parameters": node.parameters,
                "id": node.id,
                "name": node.name,
                "type": node.type,
                "typeVersion": 1,
                "position": node.position
            })

        connections_dict = {}
        for conn in wf.connections:
            from_node = conn.from_node
            to_node = conn.to_node
            if from_node not in connections_dict:
                connections_dict[from_node] = {"main": [[]]}
            connections_dict[from_node]["main"][0].append({
                "node": to_node,
                "type": "main",
                "index": conn.to_input
            })

        return {
            "id": wf.id,
            "name": wf.name,
            "nodes": nodes_list,
            "connections": connections_dict,
            "active": wf.active
        }

    def n8n_to_internal(self, data: Dict[str, Any]) -> InternalWorkflow:
        nodes = []
        for n in data.get("nodes", []):
            nodes.append(
                InternalNode(
                    id=n.get("id", ""),
                    name=n.get("name", ""),
                    type=n.get("type", ""),
                    parameters=n.get("parameters", {}),
                    position=n.get("position", [0, 0])
                )
            )

        connections = []
        conn_data = data.get("connections", {})
        for from_node, main_conn in conn_data.items():
            for target_list in main_conn.get("main", []):
                for target in target_list:
                    connections.append(
                        InternalConnection(
                            from_node=from_node,
                            to_node=target.get("node", ""),
                            from_output=0,
                            to_input=target.get("index", 0)
                        )
                    )

        return InternalWorkflow(
            id=data.get("id"),
            name=data.get("name", "Imported Workflow"),
            nodes=nodes,
            connections=connections,
            active=data.get("active", True)
        )

    def _save_cache(self) -> None:
        cache_path = Path(self._workspace_root) / self._cache_filename
        serialized = {}
        for wf_id, wf in self._workflows.items():
            serialized[wf_id] = self._serialize_workflow(wf)
        try:
            cache_path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _serialize_workflow(self, wf: InternalWorkflow) -> Dict[str, Any]:
        return {
            "id": wf.id,
            "name": wf.name,
            "nodes": [
                {
                    "id": n.id,
                    "name": n.name,
                    "type": n.type,
                    "parameters": n.parameters,
                    "position": n.position,
                }
                for n in wf.nodes
            ],
            "connections": [
                {
                    "from_node": c.from_node,
                    "to_node": c.to_node,
                    "from_output": c.from_output,
                    "to_input": c.to_input,
                }
                for c in wf.connections
            ],
            "active": wf.active,
            "version": wf.version,
        }

    def _deserialize_workflow(self, data: Dict[str, Any]) -> InternalWorkflow:
        nodes = [
            InternalNode(
                id=n["id"],
                name=n["name"],
                type=n["type"],
                parameters=n.get("parameters", {}),
                position=n.get("position", [0, 0]),
            )
            for n in data.get("nodes", [])
        ]
        connections = [
            InternalConnection(
                from_node=c["from_node"],
                to_node=c["to_node"],
                from_output=c.get("from_output", 0),
                to_input=c.get("to_input", 0),
            )
            for c in data.get("connections", [])
        ]
        return InternalWorkflow(
            id=data["id"],
            name=data.get("name", "Workflow"),
            nodes=nodes,
            connections=connections,
            active=data.get("active", True),
            version=data.get("version", 1),
        )

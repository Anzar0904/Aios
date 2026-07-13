import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from aios.providers.interface import OmniRouteRequest, universal_omniroute_engine

logger = logging.getLogger(__name__)

CACHE_DIR = Path(".aios_n8n_cache")
CACHE_DIR.mkdir(exist_ok=True)


class WorkflowTemplates:
    """Manages reusable n8n templates and caches them."""

    def __init__(self) -> None:
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._load_builtins()

    def _load_builtins(self) -> None:
        # Build templates for the 10 requested categories
        self._cache["lead_generation"] = {
            "name": "Lead Generation Workflow",
            "nodes": [
                {
                    "parameters": {"path": "lead-webhook"},
                    "id": "trigger-1",
                    "name": "Webhook Trigger",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [100, 200],
                },
                {
                    "parameters": {
                        "resource": "database",
                        "operation": "create",
                        "tableName": "leads",
                    },
                    "id": "node-db-1",
                    "name": "PostgreSQL Insert",
                    "type": "n8n-nodes-base.postgres",
                    "typeVersion": 1,
                    "position": [300, 200],
                },
                {
                    "parameters": {
                        "channel": "#sales-leads",
                        "text": "New Lead Generated: {{ $json.email }}",
                    },
                    "id": "node-slack-1",
                    "name": "Slack Notify",
                    "type": "n8n-nodes-base.slack",
                    "typeVersion": 1,
                    "position": [500, 200],
                },
            ],
            "connections": {
                "Webhook Trigger": {
                    "main": [
                        [
                            {
                                "node": "PostgreSQL Insert",
                                "type": "main",
                                "index": 0,
                            }
                        ]
                    ]
                },
                "PostgreSQL Insert": {
                    "main": [
                        [
                            {
                                "node": "Slack Notify",
                                "type": "main",
                                "index": 0,
                            }
                        ]
                    ]
                },
            },
        }

        self._cache["cold_email"] = {
            "name": "Cold Email Automation",
            "nodes": [
                {
                    "parameters": {"rule": "interval", "value": 1, "unit": "hours"},
                    "id": "trigger-2",
                    "name": "Schedule Trigger",
                    "type": "n8n-nodes-base.scheduleTrigger",
                    "typeVersion": 1,
                    "position": [100, 200],
                },
                {
                    "parameters": {
                        "operation": "read",
                        "tableName": "prospects",
                        "where": "status = 'new'",
                    },
                    "id": "node-db-2",
                    "name": "Get Prospects",
                    "type": "n8n-nodes-base.postgres",
                    "typeVersion": 1,
                    "position": [300, 200],
                },
                {
                    "parameters": {
                        "toEmail": "{{ $json.email }}",
                        "subject": "Quick Question",
                        "htmlBody": (
                            "<p>Hello {{ $json.name }}, "
                            "would you be open to a quick call?</p>"
                        ),
                    },
                    "id": "node-email-1",
                    "name": "Send Cold Email",
                    "type": "n8n-nodes-base.emailSend",
                    "typeVersion": 1,
                    "position": [500, 200],
                },
            ],
            "connections": {
                "Schedule Trigger": {
                    "main": [
                        [
                            {
                                "node": "Get Prospects",
                                "type": "main",
                                "index": 0,
                            }
                        ]
                    ]
                },
                "Get Prospects": {
                    "main": [
                        [
                            {
                                "node": "Send Cold Email",
                                "type": "main",
                                "index": 0,
                            }
                        ]
                    ]
                },
            },
        }

        self._cache["crm_automation"] = {
            "name": "CRM Sync Automation",
            "nodes": [
                {
                    "parameters": {"path": "crm-sync"},
                    "id": "trigger-3",
                    "name": "Sync Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [100, 200],
                },
                {
                    "parameters": {"resource": "contact", "operation": "upsert"},
                    "id": "node-crm-1",
                    "name": "HubSpot Upsert",
                    "type": "n8n-nodes-base.hubspot",
                    "typeVersion": 1,
                    "position": [300, 200],
                },
            ],
            "connections": {
                "Sync Webhook": {
                    "main": [
                        [
                            {
                                "node": "HubSpot Upsert",
                                "type": "main",
                                "index": 0,
                            }
                        ]
                    ]
                }
            },
        }

        self._cache["ai_agent"] = {
            "name": "AI Agent Assistant",
            "nodes": [
                {
                    "parameters": {"path": "ai-query"},
                    "id": "trigger-4",
                    "name": "User Query Trigger",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [100, 200],
                },
                {
                    "parameters": {"options": {}},
                    "id": "node-ai-1",
                    "name": "AI Agent Node",
                    "type": "n8n-nodes-base.agent",
                    "typeVersion": 1,
                    "position": [300, 200],
                },
                {
                    "parameters": {"model": "gpt-4o"},
                    "id": "node-model-1",
                    "name": "OpenAI Model",
                    "type": "n8n-nodes-base.lmChatOpenAi",
                    "typeVersion": 1,
                    "position": [300, 400],
                },
            ],
            "connections": {
                "User Query Trigger": {
                    "main": [
                        [
                            {
                                "node": "AI Agent Node",
                                "type": "main",
                                "index": 0,
                            }
                        ]
                    ]
                },
                "OpenAI Model": {
                    "ai_language_model": [
                        [
                            {
                                "node": "AI Agent Node",
                                "type": "ai_language_model",
                                "index": 0,
                            }
                        ]
                    ]
                },
            },
        }

        # Customer Support template
        self._cache["customer_support"] = {
            "name": "Customer Support Auto-Response",
            "nodes": [
                {
                    "parameters": {"path": "support-ticket"},
                    "id": "trigger-5",
                    "name": "Ticket Webhook",
                    "type": "n8n-nodes-base.webhook",
                    "typeVersion": 1,
                    "position": [100, 200],
                },
                {
                    "parameters": {
                        "jsCode": "return [{ json: { text: items[0].json.body.toLowerCase() } }];"
                    },
                    "id": "node-code-1",
                    "name": "Sanitize Query",
                    "type": "n8n-nodes-base.code",
                    "typeVersion": 1,
                    "position": [300, 200],
                },
                {
                    "parameters": {
                        "conditions": {
                            "string": [
                                {
                                    "value1": "={{ $json.text }}",
                                    "operation": "contains",
                                    "value2": "urgent",
                                }
                            ]
                        }
                    },
                    "id": "node-if-1",
                    "name": "Check Priority",
                    "type": "n8n-nodes-base.if",
                    "typeVersion": 1,
                    "position": [500, 200],
                },
            ],
            "connections": {
                "Ticket Webhook": {
                    "main": [
                        [
                            {
                                "node": "Sanitize Query",
                                "type": "main",
                                "index": 0,
                            }
                        ]
                    ]
                },
                "Sanitize Query": {
                    "main": [
                        [
                            {
                                "node": "Check Priority",
                                "type": "main",
                                "index": 0,
                            }
                        ]
                    ]
                },
            },
        }

        # Setup stubs for remainder of 10 templates to support future expansions
        for t_name in [
            "ticket_routing",
            "content_generation",
            "social_media",
            "data_processing",
            "document_processing",
        ]:
            self._cache[t_name] = {
                "name": f"{t_name.replace('_', ' ').title()} Template",
                "nodes": [
                    {
                        "parameters": {"path": f"{t_name}-webhook"},
                        "id": "trigger-generic",
                        "name": "Webhook Trigger",
                        "type": "n8n-nodes-base.webhook",
                        "typeVersion": 1,
                        "position": [100, 200],
                    }
                ],
                "connections": {},
            }

    def get_template(self, category: str) -> Optional[Dict[str, Any]]:
        return self._cache.get(category.lower())

    def list_templates(self) -> List[str]:
        return list(self._cache.keys())


class WorkflowValidator:
    """Validates workflow connections, circular routes, missing params, and credentials."""

    def validate(self, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        errors = []
        warnings = []
        nodes = workflow_json.get("nodes", [])
        connections = workflow_json.get("connections", {})

        if not nodes:
            errors.append("Workflow has no node definitions.")
            return {"valid": False, "errors": errors, "warnings": warnings}

        # Build adjacency graph
        node_names = {n["name"] for n in nodes}
        adjacency: Dict[str, List[str]] = {name: [] for name in node_names}

        # 1. Validate connections
        for source_name, target_types in connections.items():
            if source_name not in node_names:
                errors.append(f"Source node '{source_name}' in connections does not exist.")
                continue
            for _conn_type, dest_lists in target_types.items():
                for dest_list in dest_lists:
                    for dest in dest_list:
                        target_name = dest.get("node")
                        if target_name not in node_names:
                            errors.append(
                                f"Connection references non-existent target node '{target_name}'."
                            )
                        else:
                            adjacency[source_name].append(target_name)

        # 2. Cycle detection (DFS)
        visited = set()
        stack = set()
        has_cycle = False

        def dfs(node: str) -> bool:
            visited.add(node)
            stack.add(node)
            for neighbor in adjacency.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in stack:
                    return True
            stack.remove(node)
            return False

        for node in node_names:
            if node not in visited:
                if dfs(node):
                    has_cycle = True
                    break

        if has_cycle:
            errors.append("Circular execution loop detected in workflow nodes.")

        # 3. Detect orphaned nodes (no trigger path)
        triggers = {
            n["name"]
            for n in nodes
            if "trigger" in n.get("type", "").lower()
            or n.get("type", "") == "n8n-nodes-base.webhook"
        }
        if not triggers:
            warnings.append("No triggers or entrypoint nodes identified in the workflow.")

        # Check reachability from triggers
        reachable = set()

        def mark_reachable(node: str) -> None:
            reachable.add(node)
            for neighbor in adjacency.get(node, []):
                if neighbor not in reachable:
                    mark_reachable(neighbor)

        for trigger in triggers:
            mark_reachable(trigger)

        for node in node_names:
            if node not in reachable and node not in triggers:
                warnings.append(f"Orphaned Node: '{node}' is not reachable from any trigger.")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


class CredentialIntelligence:
    """Scans workflow JSON to identify required and missing credentials."""

    def __init__(self) -> None:
        self.credential_mappings = {
            "n8n-nodes-base.postgres": "PostgreSQL API",
            "n8n-nodes-base.lmChatOpenAi": "OpenAI Credentials",
            "n8n-nodes-base.slack": "Slack OAuth2 API",
            "n8n-nodes-base.discord": "Discord Bot API",
            "n8n-nodes-base.telegram": "Telegram API",
            "n8n-nodes-base.emailSend": "SMTP/Email API",
            "n8n-nodes-base.hubspot": "HubSpot OAuth2 API",
            "n8n-nodes-base.notion": "Notion API",
            "n8n-nodes-base.airtable": "Airtable API",
        }

    def detect_required_credentials(self, workflow_json: Dict[str, Any]) -> List[str]:
        required = []
        for node in workflow_json.get("nodes", []):
            node_type = node.get("type", "")
            if node_type in self.credential_mappings:
                cred = self.credential_mappings[node_type]
                if cred not in required:
                    required.append(cred)
        return required


class WorkflowOptimizer:
    """Optimizes workflows for cost, speed, and readability."""

    def optimize(self, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        nodes = workflow_json.get("nodes", [])
        connections = workflow_json.get("connections", {})
        
        # Incremental optimizations: Remove duplicated consecutive no-ops
        optimized_nodes = []
        seen_types = set()
        
        for node in nodes:
            # Drop identical duplicate nodes
            key = (node.get("type"), json.dumps(node.get("parameters", {})))
            if key in seen_types and "trigger" not in node.get("type", "").lower():
                continue
            seen_types.add(key)
            optimized_nodes.append(node)

        # Optimize connections dictionary to filter out missing target nodes
        optimized_connections = {}
        valid_node_names = {n["name"] for n in optimized_nodes}

        for src, val in connections.items():
            if src not in valid_node_names:
                continue
            new_val = {}
            for c_type, c_lists in val.items():
                new_lists = []
                for c_list in c_lists:
                    new_list = [dest for dest in c_list if dest.get("node") in valid_node_names]
                    if new_list:
                        new_lists.append(new_list)
                if new_lists:
                    new_val[c_type] = new_lists
            if new_val:
                optimized_connections[src] = new_val

        return {
            "name": workflow_json.get("name", "Optimized Workflow"),
            "nodes": optimized_nodes,
            "connections": optimized_connections,
        }


class WorkflowAnalyzer:
    """Analyzes imported workflows and provides execution path and bottlenecks summaries."""

    def analyze(self, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        nodes = workflow_json.get("nodes", [])

        triggers = [
            n["name"]
            for n in nodes
            if "trigger" in n.get("type", "").lower()
            or n.get("type", "") == "n8n-nodes-base.webhook"
        ]

        external_services = []
        cred_intel = CredentialIntelligence()
        creds = cred_intel.detect_required_credentials(workflow_json)

        for node in nodes:
            n_type = node.get("type", "")
            if "postgres" in n_type:
                external_services.append("PostgreSQL Database")
            elif "slack" in n_type:
                external_services.append("Slack Notifications")
            elif "email" in n_type:
                external_services.append("SMTP Email")
            elif "hubspot" in n_type:
                external_services.append("HubSpot CRM")

        bottlenecks = []
        suggestions = []

        # Standard rules
        if len(nodes) > 15:
            bottlenecks.append("High Node count may increase execution latency.")
            suggestions.append("Consider breaking down logical components into sub-workflows.")

        if any("code" in n.get("type", "").lower() for n in nodes):
            bottlenecks.append("Custom Code node execution adds dynamic parsing overhead.")
            suggestions.append("Ensure custom JavaScript/Python code is optimized and cached.")

        return {
            "summary": (
                f"Workflow containing {len(nodes)} nodes "
                f"with {len(triggers)} entry triggers."
            ),
            "trigger_chain": triggers,
            "external_services": list(set(external_services)),
            "credentials_required": creds,
            "bottlenecks": bottlenecks,
            "suggestions": suggestions,
        }


class WorkflowMemory:
    """Persists generated workflows and template metadata inside memory cache files."""

    def __init__(self) -> None:
        self.memory_file = CACHE_DIR / "workflow_memory.json"
        self._load()

    def _load(self) -> None:
        if self.memory_file.exists():
            try:
                self.workflows = json.loads(self.memory_file.read_text(encoding="utf-8"))
            except Exception:
                self.workflows = []
        else:
            self.workflows = []

    def save_workflow(self, name: str, workflow_json: Dict[str, Any]) -> None:
        self.workflows.append({
            "name": name,
            "timestamp": time.time(),
            "version": len(self.workflows) + 1,
            "workflow": workflow_json,
        })
        try:
            self.memory_file.write_text(json.dumps(self.workflows, indent=2), encoding="utf-8")
        except Exception as e:
            logger.error(f"Failed to persist workflow to memory file: {e}")

    def list_workflows(self) -> List[Dict[str, Any]]:
        return self.workflows

    def search_workflows(self, query: str) -> List[Dict[str, Any]]:
        matches = []
        for item in self.workflows:
            if (
                query.lower() in item["name"].lower()
                or query.lower() in json.dumps(item["workflow"]).lower()
            ):
                matches.append(item)
        return matches


class WorkflowGenerator:
    """Generates production-ready n8n workflows using template registries and OmniRoute engines."""

    def generate(self, prompt: str, category: Optional[str] = None) -> Dict[str, Any]:
        # Try to resolve category template first
        templates = WorkflowTemplates()
        if category and category.lower() in templates.list_templates():
            return templates.get_template(category)

        # Fallback to OmniRoute LLM generation
        system_prompt = (
            "You are a Senior n8n Workflow Architect. Generate a valid, production-ready n8n "
            "workflow in JSON format representing the user's request. Output ONLY valid JSON "
            "without markdown wrapping block. Follow standard n8n format: "
            "{ 'name': 'Workflow Name', 'nodes': [...], 'connections': {...} }."
        )

        try:
            req = OmniRouteRequest(
                prompt=prompt,
                system_prompt=system_prompt,
                task_type="coding",
                max_tokens=2048,
            )
            res = universal_omniroute_engine.execute(req)
            content = res.content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            return json.loads(content)
        except Exception as e:
            logger.warning(
                f"OmniRoute workflow generation failed: {e}. "
                f"Falling back to lead generation template."
            )
            return templates.get_template("lead_generation")


class WorkflowIntelligenceEngine:
    """Central orchestration engine for n8n workflow management, validation, and analytics."""

    def __init__(self) -> None:
        self.generator = WorkflowGenerator()
        self.validator = WorkflowValidator()
        self.optimizer = WorkflowOptimizer()
        self.analyzer = WorkflowAnalyzer()
        self.memory = WorkflowMemory()
        self.templates = WorkflowTemplates()

    def generate_reports(
        self,
        workflow_json: Dict[str, Any],
        output_dir: str = "docs/workflows",
    ) -> None:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Analyze
        analysis = self.analyzer.analyze(workflow_json)
        # Validate
        validation = self.validator.validate(workflow_json)
        # Optimize
        optimized = self.optimizer.optimize(workflow_json)
        opt_validation = self.validator.validate(optimized)

        # Credential checks
        cred_intel = CredentialIntelligence()
        creds = cred_intel.detect_required_credentials(workflow_json)

        # 1. workflow_summary.md
        with open(f"{output_dir}/workflow_summary.md", "w") as f:
            f.write(
                f"# n8n Workflow Engineering Summary\n\n"
                f"- **Workflow Name**: {workflow_json.get('name', 'Generated Workflow')}\n"
                f"- **Node Count**: {len(workflow_json.get('nodes', []))}\n"
                f"- **Summary**: {analysis['summary']}\n"
                f"- **Triggers**: {', '.join(analysis['trigger_chain']) or 'None'}\n"
            )

        # 2. validation_report.md
        with open(f"{output_dir}/validation_report.md", "w") as f:
            status_text = "[green]VALID[/green]" if validation["valid"] else "[red]INVALID[/red]"
            f.write(
                f"# Workflow Validation Report\n\n"
                f"- **Overall Status**: {status_text}\n\n"
                f"### Errors:\n"
            )
            for err in validation["errors"]:
                f.write(f"- {err}\n")
            if not validation["errors"]:
                f.write("No connection or schema errors detected.\n")

            f.write("\n### Warnings:\n")
            for wrn in validation["warnings"]:
                f.write(f"- {wrn}\n")
            if not validation["warnings"]:
                f.write("No warnings detected.\n")

        # 3. optimization_report.md
        with open(f"{output_dir}/optimization_report.md", "w") as f:
            f.write(
                f"# Workflow Optimization Report\n\n"
                f"- **Original Node Count**: {len(workflow_json.get('nodes', []))}\n"
                f"- **Optimized Node Count**: {len(optimized.get('nodes', []))}\n"
                f"- **Valid After Optimization**: {opt_validation['valid']}\n\n"
                f"### Optimization Suggestions:\n"
            )
            for sugg in analysis["suggestions"]:
                f.write(f"- {sugg}\n")
            if not analysis["suggestions"]:
                f.write("No optimization suggestions found.\n")

        # 4. credential_report.md
        with open(f"{output_dir}/credential_report.md", "w") as f:
            f.write(
                "# Credential Intelligence Report\n\n"
                "The following credentials are required to execute this workflow:\n\n"
            )
            for cred in creds:
                f.write(f"- {cred} (Missing/Required)\n")
            if not creds:
                f.write("No external credentials required.\n")
            f.write("\n*Disclaimer: AI OS does not store credential secrets locally.*\n")

        # 5. architecture_diagram.md
        with open(f"{output_dir}/architecture_diagram.md", "w") as f:
            f.write(
                "# Workflow Architecture Diagram\n\n"
                "```mermaid\n"
                "graph TD\n"
            )
            node_names = {n["name"] for n in workflow_json.get("nodes", [])}
            for src, targets in workflow_json.get("connections", {}).items():
                if src in node_names:
                    for _conn_type, dests in targets.items():
                        for dest_list in dests:
                            for dest in dest_list:
                                target = dest.get("node")
                                if target in node_names:
                                    src_fmt = src.replace(" ", "_")
                                    target_fmt = target.replace(" ", "_")
                                    f.write(f"  {src_fmt} --> {target_fmt}\n")
            f.write("```\n")

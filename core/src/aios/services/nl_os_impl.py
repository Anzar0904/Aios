import json
import logging
import re
import time
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from aios.registry import ServiceRegistry
from aios.services.context import ContextService
from aios.services.graph import (
    EntityType,
    GraphEntity,
    GraphRelationship,
    GraphService,
    RelationshipType,
)
from aios.services.intent import Intent
from aios.services.model import LLMRequest, ModelService
from aios.services.nl_os import ActionPlan, ActionStep, NLOSService

logger = logging.getLogger(__name__)


class NLOSServiceImpl(NLOSService):
    """Concrete implementation of NLOSService coordinating Natural Language CLI operations."""

    def __init__(self, workspace_root: str = ".") -> None:
        self.workspace_root = Path(workspace_root)
        self.history_path = self.workspace_root / ".agent" / "intent_history.json"
        self.execution_path = self.workspace_root / ".agent" / "execution_history.json"
        self.learning_path = self.workspace_root / ".agent" / "learning_patterns.json"

        self.intent_history: List[Dict[str, Any]] = []
        self.execution_history: List[Dict[str, Any]] = []
        self.learning_patterns: Dict[str, Any] = {
            "successful_patterns": [],
            "failed_patterns": [],
            "user_preferences": {},
            "frequently_used_actions": {},
            "context_usage": {},
        }

        self.last_explanation: Dict[str, Any] = {
            "objective": "",
            "intent": None,
            "plan": None,
            "reasoning": "No query resolved yet.",
        }

    def initialize(self) -> None:
        logger.info("Initializing NLOSServiceImpl")
        self._load_data()

    def start(self) -> None:
        pass

    def shutdown(self) -> None:
        self._save_data()

    def _load_data(self) -> None:
        try:
            if self.history_path.is_file():
                with open(self.history_path, "r", encoding="utf-8") as f:
                    self.intent_history = json.load(f)
            if self.execution_path.is_file():
                with open(self.execution_path, "r", encoding="utf-8") as f:
                    self.execution_history = json.load(f)
            if self.learning_path.is_file():
                with open(self.learning_path, "r", encoding="utf-8") as f:
                    self.learning_patterns = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load NL OS data: {e}")

    def _save_data(self) -> None:
        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(self.intent_history, f, indent=4)
            with open(self.execution_path, "w", encoding="utf-8") as f:
                json.dump(self.execution_history, f, indent=4)
            with open(self.learning_path, "w", encoding="utf-8") as f:
                json.dump(self.learning_patterns, f, indent=4)
        except Exception as e:
            logger.warning(f"Failed to save NL OS data: {e}")

    def _get_context_service(self) -> Optional[ContextService]:
        if ServiceRegistry._global_registry:
            try:
                return ServiceRegistry._global_registry.get(ContextService)
            except Exception:
                pass
        return None

    def _get_model_service(self) -> Optional[ModelService]:
        if ServiceRegistry._global_registry:
            try:
                return ServiceRegistry._global_registry.get(ModelService)
            except Exception:
                pass
        return None

    def _get_graph_service(self) -> Optional[GraphService]:
        if ServiceRegistry._global_registry:
            try:
                return ServiceRegistry._global_registry.get(GraphService)
            except Exception:
                pass
        return None

    def route_query(self, query: str) -> Optional[List[str]]:
        """Translates natural language to CLI arguments, resolving context/pronouns."""
        cleaned = query.strip().lower()
        context_service = self._get_context_service()

        # 1. Resolve pronouns (Pronoun Resolution)
        resolved_query = query
        pronouns = ["it", "them", "that", "this"]
        has_pronoun = any(re.search(rf"\b{p}\b", cleaned) for p in pronouns)

        if has_pronoun and context_service:
            # Determine domain of action to pick context variable
            if any(w in cleaned for w in ["workflow", "deploy", "activate", "deactivate"]):
                wf = context_service.get_context_item("workflow")
                if wf:
                    resolved_query = re.sub(
                        r"\b(it|them|that|this)\b", wf, query, flags=re.IGNORECASE
                    )
            elif any(w in cleaned for w in ["project", "switch", "create"]):
                proj = context_service.get_context_item("project")
                if proj:
                    resolved_query = re.sub(
                        r"\b(it|them|that|this)\b", proj, query, flags=re.IGNORECASE
                    )
            elif any(w in cleaned for w in ["client", "lead", "proposal"]):
                client = context_service.get_context_item("client")
                if client:
                    resolved_query = re.sub(
                        r"\b(it|them|that|this)\b", client, query, flags=re.IGNORECASE
                    )
            elif any(w in cleaned for w in ["research", "paper", "synthesize"]):
                topic = context_service.get_context_item("topic")
                if topic:
                    resolved_query = re.sub(
                        r"\b(it|them|that|this)\b", topic, query, flags=re.IGNORECASE
                    )
            elif "goal" in cleaned:
                goal = context_service.get_context_item("goal")
                if goal:
                    resolved_query = re.sub(
                        r"\b(it|them|that|this)\b", goal, query, flags=re.IGNORECASE
                    )

        cleaned_resolved = resolved_query.strip().lower()
        self.last_explanation["objective"] = query

        # Intercept multi-agent workflow requests
        if any(
            w in cleaned_resolved
            for w in ["build a crm", "create a github automation workflow", "research agent memory"]
        ):
            self.last_explanation["reasoning"] = (
                f"Routed to multi-agent executor for: {resolved_query}"
            )
            return ["agent", "execute", resolved_query]

        # Update context based on query content
        self._update_context_from_query(resolved_query)

        # 2. Rule-based Heuristic Mapping
        rule_tokens = self._match_heuristics(cleaned_resolved, resolved_query)
        if rule_tokens:
            self.last_explanation["reasoning"] = (
                f"Resolved via rule-based heuristics to: aios {' '.join(rule_tokens)}"
            )
            return rule_tokens

        # 3. LLM Router (Intelligent Translation)
        model_service = self._get_model_service()
        if model_service:
            try:
                # Load context details
                ctx_details = ""
                if context_service:
                    ctx_details = (
                        f"Current Project: {context_service.get_context_item('project') or 'None'}\n"
                        f"Current Workflow: {context_service.get_context_item('workflow') or 'None'}\n"
                        f"Current Goal: {context_service.get_context_item('goal') or 'None'}\n"
                        f"Current Research Topic: {context_service.get_context_item('topic') or 'None'}\n"
                        f"Current Agency Client: {context_service.get_context_item('client') or 'None'}\n"
                    )

                prompt = (
                    "You are the Natural Language Router for AI OS.\n"
                    "Translate the user's natural language command into the exact target CLI command tokens as a JSON list (e.g. ['project', 'create', 'AI Tutor'] or ['github', 'prs']). Do NOT prefix with 'aios'.\n\n"
                    "Available Commands:\n"
                    "- project list / create / switch / dashboard / status / graph / memory / models / cross\n"
                    "- workflows / workflow deploy / generate / activate / deactivate / diagnose / repair / versions / rollback / dashboard\n"
                    "- github repos / branches / commits / prs / issues / actions / releases / analytics / health\n"
                    "- research list / search / paper / synthesize / learn / report / dashboard\n"
                    "- agency dashboard / status / leads / crm / clients / proposals / outreach / calendar\n"
                    "- personal / goals / tasks / calendar / habits / reminders / today / morning / weekly / notes / learning / coach\n"
                    "- integration list / connect / disconnect / status / version / health / config / test\n"
                    "- doc list / generate / validate / analyze / status\n"
                    "- status / diagnostics / setup / session\n\n"
                    f"Context:\n{ctx_details}\n"
                    f'User Request: "{resolved_query}"\n\n'
                    'Return ONLY a valid JSON list of strings (pure JSON, no markdown codeblocks, no formatting, e.g. ["project", "list"]).'
                )

                res = model_service.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output pure JSON list of command tokens only.",
                        task_category="routing",
                    )
                )

                content = res.content.strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                content = content.strip()

                tokens = json.loads(content)
                if isinstance(tokens, list) and len(tokens) > 0:
                    self.last_explanation["reasoning"] = (
                        f"Resolved via LLM router to: aios {' '.join(tokens)}"
                    )
                    return tokens
            except Exception as e:
                logger.debug(f"LLM command routing failed: {e}. Falling back to general fallback.")

        # General keywords fallback
        fallback = self._match_fallbacks(cleaned_resolved)
        if fallback:
            self.last_explanation["reasoning"] = (
                f"Resolved via keyword fallbacks to: aios {' '.join(fallback)}"
            )
            return fallback

        self.last_explanation["reasoning"] = "Could not map query to any known CLI command."
        return None

    def _update_context_from_query(self, query: str) -> None:
        context_service = self._get_context_service()
        if not context_service:
            return

        entities = self.extract_entities(query)

        if entities.get("projects"):
            context_service.set_context_item("project", entities["projects"][0])
        if entities.get("workflows"):
            context_service.set_context_item("workflow", entities["workflows"][0])
        if entities.get("clients"):
            context_service.set_context_item("client", entities["clients"][0])
        if entities.get("research_topics"):
            context_service.set_context_item("topic", entities["research_topics"][0])
        if entities.get("goals"):
            context_service.set_context_item("goal", entities["goals"][0])

    def _match_heuristics(self, cleaned: str, original: str) -> Optional[List[str]]:
        # Github
        if any(
            p in cleaned
            for p in ["github prs", "review prs", "show open github prs", "review pull requests"]
        ):
            return ["github", "prs"]
        if "github commits" in cleaned or "commit history" in cleaned:
            return ["github", "commits"]
        if "github repos" in cleaned or "git repos" in cleaned:
            return ["github", "repos"]
        if "github issues" in cleaned or "open issues" in cleaned:
            return ["github", "issues"]
        if "github actions" in cleaned or "ci builds" in cleaned:
            return ["github", "actions"]
        if "github releases" in cleaned:
            return ["github", "releases"]

        # Workflows
        if cleaned.startswith("deploy "):
            m = re.search(
                r"deploy\s+(?:the\s+workflow\s+|workflow\s+)?([A-Za-z0-9_-]+)",
                original,
                re.IGNORECASE,
            )
            name = m.group(1) if m else ""
            return ["workflow", "deploy", name] if name else ["workflow", "deploy"]

        if cleaned.startswith("activate "):
            m = re.search(r"activate\s+(?:workflow\s+)?([A-Za-z0-9_-]+)", original, re.IGNORECASE)
            name = m.group(1) if m else ""
            return ["workflow", "activate", name] if name else ["workflow", "activate"]

        if "deploy the workflow" in cleaned or "deploy workflow" in cleaned:
            m = re.search(r"workflow\s+([A-Za-z0-9_-]+)", original, re.IGNORECASE)
            name = m.group(1) if m else ""
            return ["workflow", "deploy", name] if name else ["workflow", "deploy"]

        # Projects
        if "create a project" in cleaned or "create project" in cleaned:
            m = re.search(r"project\s+(?:for\s+|a\s+)?([A-Za-z0-9_-]+)", original, re.IGNORECASE)
            name = m.group(1) if m else "new_project"
            return ["project", "create", name]
        if "show project list" in cleaned or "list projects" in cleaned:
            return ["project", "list"]
        if "show project status" in cleaned or "project status" in cleaned:
            return ["project", "status"]
        if "project dashboard" in cleaned:
            return ["project", "dashboard"]

        # Personal / Priorities
        if any(p in cleaned for p in ["today's priorities", "today's schedule", "show today"]):
            return ["today"]
        if "morning briefing" in cleaned or "morning report" in cleaned:
            return ["morning"]
        if "weekly review" in cleaned or "weekly progress" in cleaned:
            return ["weekly"]
        if "create reminder" in cleaned or "add reminder" in cleaned:
            m = re.search(r"reminder\s+([A-Za-z0-9_-]+)", original, re.IGNORECASE)
            name = m.group(1) if m else "generic_reminder"
            return ["reminders", "create", name]
        if "my goals" in cleaned or "show goals" in cleaned:
            return ["goals"]
        if "tasks list" in cleaned or "show tasks" in cleaned:
            return ["tasks"]

        # Agency
        if "create agency lead" in cleaned:
            m = re.search(r"lead\s+([A-Za-z0-9_-]+)", original, re.IGNORECASE)
            name = m.group(1) if m else "generic_lead"
            return ["agency", "leads", "create", name]
        if "generate proposal" in cleaned:
            m = re.search(r"proposal\s+([A-Za-z0-9_-]+)", original, re.IGNORECASE)
            name = m.group(1) if m else ""
            return ["agency", "proposals", "generate", name] if name else ["agency", "proposals"]

        # Research
        if "start research project" in cleaned or "research topic" in cleaned:
            m = re.search(r"topic\s+([A-Za-z0-9_-]+)", original, re.IGNORECASE)
            name = m.group(1) if m else ""
            return ["research", "learn", name] if name else ["research", "learn"]

        # Diagnostics / System
        if "system status" in cleaned or "uptime" in cleaned:
            return ["status"]
        if "system diagnostics" in cleaned or "run diagnostics" in cleaned:
            return ["diagnostics"]

        return None

    def _match_fallbacks(self, cleaned: str) -> Optional[List[str]]:
        # Use explicit word boundaries to avoid matching "pr" in "project"
        if re.search(r"\bpr\b|\bprs\b|\bpull request\b", cleaned):
            return ["github", "prs"]
        if re.search(r"\bworkflow\b|\bworkflows\b", cleaned):
            if "deploy" in cleaned:
                return ["workflow", "deploy"]
            return ["workflows"]
        if re.search(r"\bproject\b|\bprojects\b", cleaned):
            if "create" in cleaned:
                return ["project", "create"]
            return ["project", "list"]
        if re.search(r"\blead\b|\bleads\b", cleaned):
            return ["agency", "leads"]
        if re.search(r"\bproposal\b|\bproposals\b", cleaned):
            return ["agency", "proposals"]
        if re.search(r"\bresearch\b", cleaned):
            return ["research", "dashboard"]
        if re.search(r"\breminder\b|\breminders\b", cleaned):
            return ["reminders"]
        if re.search(r"\bgoal\b|\bgoals\b", cleaned):
            return ["goals"]
        if re.search(r"\btask\b|\btasks\b", cleaned):
            return ["tasks"]
        return None

    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extracts Projects, Clients, Repositories, Workflows, etc. from query."""
        entities: Dict[str, List[str]] = {
            "projects": [],
            "clients": [],
            "repositories": [],
            "workflows": [],
            "tasks": [],
            "goals": [],
            "meetings": [],
            "research_topics": [],
            "files": [],
            "documents": [],
            "models": [],
            "agents": [],
        }

        # Rule-based regex extraction
        # Projects (supports "project compiler_design" or "project for compiler_design")
        m_proj = re.findall(r"\bproject\s+(?:for\s+|a\s+)?([A-Za-z0-9_-]+)", query, re.IGNORECASE)
        if m_proj:
            entities["projects"].extend(m_proj)

        # Workflows
        m_wf = re.findall(r"\bworkflow\s+(?:for\s+)?([A-Za-z0-9_-]+)", query, re.IGNORECASE)
        if m_wf:
            entities["workflows"].extend(m_wf)

        # Clients/leads
        m_client = re.findall(
            r"\b(?:client|lead|company)\s+(?:for\s+)?([A-Za-z0-9_-]+)", query, re.IGNORECASE
        )
        if m_client:
            entities["clients"].extend(m_client)

        # Research topics
        m_res = re.findall(
            r"\b(?:research|topic)\s+(?:on\s+)?([A-Za-z0-9_-]+)", query, re.IGNORECASE
        )
        if m_res:
            entities["research_topics"].extend(m_res)

        # Goals
        m_goal = re.findall(r"\bgoal\s+([A-Za-z0-9_-]+)", query, re.IGNORECASE)
        if m_goal:
            entities["goals"].extend(m_goal)

        # Tasks
        m_task = re.findall(r"\btask\s+([A-Za-z0-9_-]+)", query, re.IGNORECASE)
        if m_task:
            entities["tasks"].extend(m_task)

        # LLM Entity Extractor
        model_service = self._get_model_service()
        if model_service:
            try:
                prompt = (
                    "Extract entities from this user request.\n"
                    f'Request: "{query}"\n\n'
                    "Categories to extract:\n"
                    "- projects (Project names)\n"
                    "- clients (Client or Lead names)\n"
                    "- repositories (Git repo names)\n"
                    "- workflows (Automation workflow names)\n"
                    "- tasks (Action items or tasks)\n"
                    "- goals (Personal or sprint goals)\n"
                    "- meetings (Scheduled events or meetings)\n"
                    "- research_topics (Academic or technical research topics)\n"
                    "- files (Filenames or paths)\n"
                    "- documents (Documentation or ADR files)\n"
                    "- models (LLM model names)\n"
                    "- agents (AI agent roles)\n\n"
                    'Return ONLY a valid JSON dictionary where keys are the categories above and values are lists of extracted string values (e.g. {"projects": ["AI Tutor"], "workflows": []}). Output pure JSON, no markdown formatting.'
                )

                res = model_service.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output pure JSON dictionary only.",
                        task_category="entity_extraction",
                    )
                )
                content = res.content.strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                content = content.strip()

                llm_entities = json.loads(content)
                if isinstance(llm_entities, dict):
                    for k, v in llm_entities.items():
                        if k in entities and isinstance(v, list):
                            # Merge and deduplicate
                            entities[k] = list(set(entities[k] + v))
            except Exception as e:
                logger.debug(f"LLM entity extraction failed: {e}")

        return entities

    def generate_plan(self, query: str) -> ActionPlan:
        """Generates a step-by-step action plan for a natural language request."""
        # Check if plan contains multiple sub-commands (e.g. split by "and", "then")
        clauses = re.split(r"\band\b|\bthen\b", query, flags=re.IGNORECASE)
        steps = []

        plan_id = f"plan_{int(time.time())}"

        # Rule-based planner fallback
        for idx, clause in enumerate(clauses):
            clause_cleaned = clause.strip()
            if not clause_cleaned:
                continue

            tokens = self.route_query(clause_cleaned)
            if tokens:
                target_cmd = f"aios {' '.join(tokens)}"
                steps.append(
                    ActionStep(
                        step_id=f"step_{idx + 1}",
                        action_type="cli_command",
                        target=target_cmd,
                        description=f"Run command: {target_cmd}",
                        dependencies=[f"step_{idx}"] if idx > 0 else [],
                    )
                )

        # LLM Planner
        model_service = self._get_model_service()
        if not steps and model_service:
            try:
                prompt = (
                    "You are the Action Planner for AI OS.\n"
                    "Convert the following natural language request into a step-by-step execution plan.\n"
                    f'Request: "{query}"\n\n'
                    "For each step, specify:\n"
                    "- step_id: Unique string like 'step_1'\n"
                    "- action_type: 'cli_command'\n"
                    "- target: The exact CLI command to run (excluding 'aios' prefix, e.g. 'project list' or 'workflow deploy my_workflow')\n"
                    "- description: Brief description of the step\n"
                    "- dependencies: List of step_ids this step depends on\n\n"
                    'Return ONLY a JSON list of step dictionaries (pure JSON, no markdown formatting, e.g. [{"step_id": "step_1", "action_type": "cli_command", "target": "project create my_project", "description": "Create the project MyProject", "dependencies": []}]).'
                )

                res = model_service.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output pure JSON list of action steps only.",
                        task_category="planning",
                    )
                )
                content = res.content.strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                content = content.strip()

                llm_steps = json.loads(content)
                if isinstance(llm_steps, list):
                    for idx, s in enumerate(llm_steps):
                        target = s["target"]
                        if not target.startswith("aios "):
                            target = f"aios {target}"
                        steps.append(
                            ActionStep(
                                step_id=s.get("step_id", f"step_{idx + 1}"),
                                action_type=s.get("action_type", "cli_command"),
                                target=target,
                                description=s.get("description", f"Run {target}"),
                                dependencies=s.get("dependencies", []),
                            )
                        )
            except Exception as e:
                logger.debug(f"LLM Action Planner failed: {e}")

        # If still empty, create a single fallback step
        if not steps:
            steps.append(
                ActionStep(
                    step_id="step_1",
                    action_type="cli_command",
                    target=f"aios {query}",
                    description=f"Run command: aios {query}",
                )
            )

        plan = ActionPlan(plan_id=plan_id, objective=query, steps=steps)
        self.last_explanation["plan"] = plan
        return plan

    def execute_plan(self, plan: ActionPlan) -> bool:
        """Executes a generated action plan step-by-step."""
        from aios.cli import execute_builtin_cli_command

        logger.info(f"Executing Action Plan: {plan.plan_id}")
        plan.status = "running"
        all_success = True

        # Sync Plan to Graph
        graph_svc = self._get_graph_service()
        plan_node_id = f"plan_{plan.plan_id}"

        if graph_svc:
            try:
                # Create Plan entity in graph
                plan_entity = GraphEntity(
                    entity_id=plan_node_id,
                    entity_type=EntityType.PLAN,
                    name=f"Plan {plan.plan_id}",
                    properties={"objective": plan.objective},
                )
                graph_svc.create_entity(plan_entity)
            except Exception as exc:
                logger.debug(f"Could not record plan in graph: {exc}")

        for step in plan.steps:
            step.status = "running"
            logger.info(f"Running step {step.step_id}: {step.target}")

            # Extract arguments by removing 'aios ' prefix
            cmd_args = step.target
            if cmd_args.startswith("aios "):
                cmd_args = cmd_args[5:]

            args_list = cmd_args.split()

            try:
                # Sync Action/Execution to graph
                if graph_svc:
                    action_entity = GraphEntity(
                        entity_id=f"act_{plan.plan_id}_{step.step_id}",
                        entity_type=EntityType.ACTION,
                        name=f"Action {step.step_id}",
                        properties={"target": step.target, "description": step.description},
                    )
                    graph_svc.create_entity(action_entity)

                    # Link Plan -> Action
                    rel = GraphRelationship(
                        relationship_id=f"rel_{plan.plan_id}_{step.step_id}",
                        source_id=plan_node_id,
                        target_id=action_entity.entity_id,
                        relationship_type=RelationshipType.PLANNED,
                    )
                    graph_svc.create_relationship(rel)

                # Run CLI command handler directly
                res = execute_builtin_cli_command(args_list, exit_on_complete=False)

                if res:
                    step.status = "completed"
                    if graph_svc:
                        graph_svc.create_relationship(
                            GraphRelationship(
                                relationship_id=f"rel_exec_{plan.plan_id}_{step.step_id}",
                                source_id=f"act_{plan.plan_id}_{step.step_id}",
                                target_id=plan_node_id,
                                relationship_type=RelationshipType.EXECUTED,
                            )
                        )
                else:
                    step.status = "failed"
                    all_success = False
            except Exception as e:
                logger.error(f"Step {step.step_id} execution failed: {e}")
                step.status = "failed"
                all_success = False

        plan.status = "completed" if all_success else "failed"

        # Save to execution history
        self.execution_history.append(
            {
                "plan_id": plan.plan_id,
                "objective": plan.objective,
                "status": plan.status,
                "timestamp": time.time(),
                "steps": [asdict(s) for s in plan.steps],
            }
        )
        self._save_data()

        # Feed back to Learning Engine
        self._update_learning_engine(plan.objective, all_success)

        return all_success

    def _update_learning_engine(self, objective: str, success: bool) -> None:
        # Update successful/failed patterns
        patterns = (
            self.learning_patterns["successful_patterns"]
            if success
            else self.learning_patterns["failed_patterns"]
        )

        # Simple token count / keyword extraction to store learning pattern
        words = [w for w in objective.lower().split() if len(w) > 3]
        if words:
            pattern_str = " ".join(words[:4])
            if pattern_str not in patterns:
                patterns.append(pattern_str)

        # Track usage frequencies
        freq = self.learning_patterns["frequently_used_actions"]
        words_key = " ".join(words[:2]) if len(words) >= 2 else (words[0] if words else "unknown")
        freq[words_key] = freq.get(words_key, 0) + 1

        self._save_data()

    def get_last_explanation(self) -> Dict[str, Any]:
        return self.last_explanation

    def record_intent_history(self, query: str, intent: Intent, success: bool) -> None:
        # Update explanation state
        self.last_explanation["objective"] = query
        self.last_explanation["intent"] = intent
        self.last_explanation["reasoning"] = (
            f"Resolved via intent engine: {intent.intent_type.name}.{intent.action}."
        )

        self.intent_history.append(
            {
                "query": query,
                "intent_type": intent.intent_type.name,
                "target_service": intent.target_service,
                "action": intent.action,
                "confidence": intent.confidence,
                "success": success,
                "timestamp": time.time(),
            }
        )
        self._save_data()

        # Sync to Knowledge Graph
        graph_svc = self._get_graph_service()
        if graph_svc:
            try:
                intent_node_id = f"intent_{int(time.time())}"
                intent_entity = GraphEntity(
                    entity_id=intent_node_id,
                    entity_type=EntityType.INTENT,
                    name=f"Intent {intent.intent_type.name}",
                    properties={
                        "query": query,
                        "action": intent.action,
                        "confidence": intent.confidence,
                        "success": success,
                    },
                )
                graph_svc.create_entity(intent_entity)

                # Link Intent -> active conversation if possible
                context_svc = self._get_context_service()
                if context_svc:
                    active_conv = context_svc.get_context_item("conversation")
                    if active_conv:
                        graph_svc.create_relationship(
                            GraphRelationship(
                                relationship_id=f"rel_req_{intent_node_id}",
                                source_id=intent_node_id,
                                target_id=active_conv,
                                relationship_type=RelationshipType.REQUESTED,
                            )
                        )
            except Exception as exc:
                logger.debug(f"Could not record intent in graph: {exc}")

    def get_learning_patterns(self) -> Dict[str, Any]:
        return self.learning_patterns

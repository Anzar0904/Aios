import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from aios.registry import ServiceRegistry
from aios.services.agent import Agent, AgentContext
from aios.services.base import ServiceLifecycle
from aios.services.context import ContextService
from aios.services.graph import (
    EntityType,
    GraphEntity,
    GraphRelationship,
    GraphService,
    RelationshipType,
)
from aios.services.model import LLMRequest, ModelService

logger = logging.getLogger(__name__)


@dataclass
class AgentDescriptor:
    agent_id: str
    name: str
    role: str
    capabilities: List[str]
    status: str = "idle"  # "idle", "busy", "offline"
    assigned_tasks: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    memory_references: List[str] = field(default_factory=list)


@dataclass
class MultiAgentTask:
    task_id: str
    title: str
    description: str
    status: str = "pending"  # "pending", "running", "completed", "failed"
    assigned_agent: Optional[str] = None  # Agent ID
    dependencies: List[str] = field(default_factory=list)  # list of task_ids
    results: Optional[str] = None
    subtasks: List[str] = field(default_factory=list)
    parent_task: Optional[str] = None
    created_at: float = field(default_factory=time.time)


@dataclass
class AgentMessage:
    message_id: str
    sender_id: str
    recipient_id: str
    content: str
    message_type: str = "request"  # "request", "result", "escalation", "info"
    task_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)


class AutonomousAgentPlatform(ServiceLifecycle):
    """Platform managing core agents, task planning, delegation, communication, and execution."""

    def __init__(self, workspace_root: str = ".") -> None:
        self.workspace_root = Path(workspace_root)
        self.registry_path = self.workspace_root / ".agent" / "agents.json"
        self.memory_path = self.workspace_root / ".agent" / "agent_memory.json"
        self.communication_log_path = self.workspace_root / ".agent" / "agent_communications.json"

        self._agents: Dict[str, Agent] = {}
        self._descriptors: Dict[str, AgentDescriptor] = {}
        self._tasks: Dict[str, MultiAgentTask] = {}
        self._messages: List[AgentMessage] = []
        self._memory_logs: List[Dict[str, Any]] = []

    def initialize(self) -> None:
        logger.info("Initializing AutonomousAgentPlatform")
        self._load_data()
        self._register_default_agents()

    def start(self) -> None:
        pass

    def shutdown(self) -> None:
        self._save_data()

    def _load_data(self) -> None:
        try:
            if self.registry_path.is_file():
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for k, v in data.items():
                        self._descriptors[k] = AgentDescriptor(**v)
            if self.memory_path.is_file():
                with open(self.memory_path, "r", encoding="utf-8") as f:
                    self._memory_logs = json.load(f)
            if self.communication_log_path.is_file():
                with open(self.communication_log_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for m in data:
                        self._messages.append(AgentMessage(**m))
        except Exception as e:
            logger.warning(f"Failed to load multi-agent data: {e}")

    def _save_data(self) -> None:
        try:
            self.registry_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump({k: asdict(v) for k, v in self._descriptors.items()}, f, indent=4)
            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump(self._memory_logs, f, indent=4)
            with open(self.communication_log_path, "w", encoding="utf-8") as f:
                json.dump([asdict(m) for m in self._messages], f, indent=4)
        except Exception as e:
            logger.warning(f"Failed to save multi-agent data: {e}")

    def _get_graph_service(self) -> Optional[GraphService]:
        if ServiceRegistry._global_registry:
            try:
                return ServiceRegistry._global_registry.get(GraphService)
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

    def _get_context_service(self) -> Optional[ContextService]:
        if ServiceRegistry._global_registry:
            try:
                return ServiceRegistry._global_registry.get(ContextService)
            except Exception:
                pass
        return None

    def _register_default_agents(self) -> None:
        from aios.services.core_agents import (
            AgencyEngineerAgent,
            AutomationEngineerAgent,
            DocumentationEngineerAgent,
            IntegrationEngineerAgent,
            ResearchEngineerAgent,
            SoftwareEngineerAgent,
            TestEngineerAgent,
        )

        default_agents = [
            SoftwareEngineerAgent(
                "agent_software",
                "SoftwareEngineer",
                "Software Engineer",
                [
                    "coding",
                    "architecture",
                    "refactoring",
                    "feature_development",
                    "repository_updates",
                ],
            ),
            TestEngineerAgent(
                "agent_test",
                "TestEngineer",
                "Test Engineer",
                [
                    "testing",
                    "validation",
                    "regression_detection",
                    "ci_verification",
                    "bug_reproduction",
                ],
            ),
            DocumentationEngineerAgent(
                "agent_doc",
                "DocumentationEngineer",
                "Documentation Engineer",
                [
                    "readme_generation",
                    "architecture_docs",
                    "api_docs",
                    "guides",
                    "knowledge_base_updates",
                ],
            ),
            ResearchEngineerAgent(
                "agent_research",
                "ResearchEngineer",
                "Research Engineer",
                [
                    "paper_analysis",
                    "repository_analysis",
                    "knowledge_synthesis",
                    "technology_recommendations",
                ],
            ),
            AgencyEngineerAgent(
                "agent_agency",
                "AgencyEngineer",
                "Agency Engineer",
                ["lead_management", "proposal_generation", "client_tracking", "crm_operations"],
            ),
            AutomationEngineerAgent(
                "agent_automation",
                "AutomationEngineer",
                "Automation Engineer",
                [
                    "workflow_generation",
                    "workflow_deployment",
                    "monitoring",
                    "repair",
                    "optimization",
                ],
            ),
            IntegrationEngineerAgent(
                "agent_integration",
                "IntegrationEngineer",
                "Integration Engineer",
                ["github", "notion", "n8n", "supabase", "calendar", "email", "external_services"],
            ),
        ]

        for agent in default_agents:
            name_lower = agent.name.lower()
            self._agents[name_lower] = agent
            if name_lower not in self._descriptors:
                self._descriptors[name_lower] = AgentDescriptor(
                    agent_id=agent.agent_id,
                    name=agent.name,
                    role=agent.role,
                    capabilities=agent.capabilities,
                    performance_metrics={"success_rate": 1.0, "tasks_completed": 0, "failures": 0},
                )

            # Sync Agent details to Knowledge Graph
            graph_svc = self._get_graph_service()
            if graph_svc:
                try:
                    graph_svc.create_entity(
                        GraphEntity(
                            entity_id=f"agent_{agent.agent_id}",
                            entity_type=EntityType.AGENT,
                            name=agent.name,
                            properties={"role": agent.role, "capabilities": agent.capabilities},
                        )
                    )
                except Exception as e:
                    logger.warning(f"Could not register agent in graph: {e}")

    def register_agent(self, agent: Agent, role: str, capabilities: List[str]) -> None:
        name_lower = agent.name.lower()
        self._agents[name_lower] = agent
        agent_id = getattr(agent, "agent_id", f"agent_{name_lower}")
        self._descriptors[name_lower] = AgentDescriptor(
            agent_id=agent_id,
            name=agent.name,
            role=role,
            capabilities=capabilities,
            performance_metrics={"success_rate": 1.0, "tasks_completed": 0, "failures": 0},
        )
        self._save_data()

        # Sync to graph
        graph_svc = self._get_graph_service()
        if graph_svc:
            try:
                graph_svc.create_entity(
                    GraphEntity(
                        entity_id=f"agent_{agent_id}",
                        entity_type=EntityType.AGENT,
                        name=agent.name,
                        properties={"role": role, "capabilities": capabilities},
                    )
                )
            except Exception as e:
                logger.warning(f"Could not register custom agent in graph: {e}")

    def get_agent(self, name: str) -> Optional[Agent]:
        return self._agents.get(name.lower())

    def list_agents(self) -> List[AgentDescriptor]:
        return list(self._descriptors.values())

    def get_agent_descriptor(self, name: str) -> Optional[AgentDescriptor]:
        return self._descriptors.get(name.lower())

    # AGENT COMMUNICATION BUS
    def send_message(
        self,
        sender_id: str,
        recipient_id: str,
        content: str,
        message_type: str = "request",
        task_id: Optional[str] = None,
    ) -> AgentMessage:
        msg = AgentMessage(
            message_id=str(uuid4()),
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            message_type=message_type,
            task_id=task_id,
        )
        self._messages.append(msg)
        self._save_data()

        # Link in Knowledge Graph
        graph_svc = self._get_graph_service()
        if graph_svc:
            try:
                # Link Sender COLLABORATES_WITH Recipient
                graph_svc.create_relationship(
                    GraphRelationship(
                        relationship_id=f"rel_comm_{msg.message_id}",
                        source_id=f"agent_{sender_id}",
                        target_id=f"agent_{recipient_id}",
                        relationship_type=RelationshipType.COLLABORATES_WITH,
                    )
                )
            except Exception as exc:
                logger.warning(f"Could not log communication relationship: {exc}")
        return msg

    def get_messages(self) -> List[AgentMessage]:
        return self._messages

    # TASK DELEGATION ENGINE
    def assign_task(self, task_id: str, agent_id: str) -> None:
        if task_id in self._tasks:
            task = self._tasks[task_id]
            task.assigned_agent = agent_id
            task.status = "running"

            desc = self._find_descriptor(agent_id)
            if desc:
                if task_id not in desc.assigned_tasks:
                    desc.assigned_tasks.append(task_id)
                    desc.status = "busy"

            self._save_data()

            # Link in Knowledge Graph
            graph_svc = self._get_graph_service()
            if graph_svc:
                try:
                    graph_svc.create_relationship(
                        GraphRelationship(
                            relationship_id=f"rel_assign_{task_id}",
                            source_id=f"task_{task_id}",
                            target_id=f"agent_{agent_id}",
                            relationship_type=RelationshipType.ASSIGNED_TO,
                        )
                    )
                except Exception as exc:
                    logger.warning(f"Could not log task assignment: {exc}")

    def reassign_task(self, task_id: str, new_agent_id: str) -> None:
        if task_id in self._tasks:
            task = self._tasks[task_id]
            old_agent = task.assigned_agent

            if old_agent:
                old_desc = self._find_descriptor(old_agent)
                if old_desc and task_id in old_desc.assigned_tasks:
                    old_desc.assigned_tasks.remove(task_id)
                    if not old_desc.assigned_tasks:
                        old_desc.status = "idle"
            self.assign_task(task_id, new_agent_id)

    def split_task(self, task_id: str, subtasks_list: List[Dict[str, Any]]) -> List[MultiAgentTask]:
        subtasks = []
        if task_id in self._tasks:
            parent = self._tasks[task_id]
            for idx, s in enumerate(subtasks_list):
                sub_id = f"{task_id}_sub_{idx + 1}"
                sub = MultiAgentTask(
                    task_id=sub_id,
                    title=s["title"],
                    description=s["description"],
                    parent_task=task_id,
                    dependencies=s.get("dependencies", []),
                )
                self._tasks[sub_id] = sub
                parent.subtasks.append(sub_id)
                subtasks.append(sub)
                self._sync_task_to_graph(sub)
            self._save_data()
        return subtasks

    def merge_tasks(self, task_ids: List[str], target_task_id: str) -> None:
        if target_task_id in self._tasks:
            target = self._tasks[target_task_id]
            for tid in task_ids:
                if tid in self._tasks and tid != target_task_id:
                    t = self._tasks[tid]
                    target.description += f"\nMerged from {tid}: {t.description}"
                    if t.results:
                        target.description += f"\nResult: {t.results}"
                    del self._tasks[tid]
            self._save_data()

    def get_task(self, task_id: str) -> Optional[MultiAgentTask]:
        return self._tasks.get(task_id)

    def list_tasks(self) -> List[MultiAgentTask]:
        return list(self._tasks.values())

    def _find_descriptor(self, agent_id: str) -> Optional[AgentDescriptor]:
        for d in self._descriptors.values():
            if d.agent_id == agent_id or d.name.lower() == agent_id.lower():
                return d
        return None

    # PLANNING ENGINE
    def generate_plan(self, goal: str) -> List[MultiAgentTask]:
        """Converts user goal to a sequence of tasks with assigned agents and dependencies."""
        model_service = self._get_model_service()
        tasks = []

        # Rule-based Planning Fallback (CRM building default pipeline)
        if any(w in goal.lower() for w in ["crm", "customer relationship", "lead tracker"]):
            research_task = MultiAgentTask(
                task_id=f"task_crm_res_{int(time.time())}",
                title="Research CRM Architectures",
                description="Analyze specifications, databases, and schemas for a CRM system.",
                assigned_agent="agent_research",
            )
            software_task = MultiAgentTask(
                task_id=f"task_crm_soft_{int(time.time())}",
                title="Develop CRM Codebase",
                description="Develop backend controllers, frontend UI mockups, and database migrations.",
                assigned_agent="agent_software",
                dependencies=[research_task.task_id],
            )
            test_task = MultiAgentTask(
                task_id=f"task_crm_test_{int(time.time())}",
                title="Verify CRM with Tests",
                description="Write unit tests and run validation suites to verify no regression.",
                assigned_agent="agent_test",
                dependencies=[software_task.task_id],
            )
            doc_task = MultiAgentTask(
                task_id=f"task_crm_doc_{int(time.time())}",
                title="Generate CRM Documentation",
                description="Compile README.md and API guides for CRM.",
                assigned_agent="agent_doc",
                dependencies=[test_task.task_id],
            )
            tasks = [research_task, software_task, test_task, doc_task]

        # LLM Planning
        elif model_service:
            try:
                agents_details = ""
                for d in self._descriptors.values():
                    agents_details += f"- Agent ID: {d.agent_id}, Role: {d.role}, Capabilities: {d.capabilities}\n"

                prompt = (
                    "You are the Planning Engine for AI OS.\n"
                    f'Given the user\'s goal: "{goal}"\n'
                    f"And these available agents:\n{agents_details}\n"
                    "Decompose this goal into a list of structured tasks. For each task, specify:\n"
                    "- task_id: Unique identifier string\n"
                    "- title: Short task title\n"
                    "- description: Details on what needs to be done\n"
                    "- assigned_agent: The Agent ID best suited for the task (choose from agent_software, agent_test, agent_doc, agent_research, agent_agency, agent_automation, agent_integration)\n"
                    "- dependencies: List of task_ids this task depends on\n\n"
                    "Return ONLY a valid JSON list of task dicts (pure JSON, no markdown formatting)."
                )

                res = model_service.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output pure JSON list of tasks only.",
                        task_category="planning",
                    )
                )
                content = res.content.strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                content = content.strip()

                llm_tasks = json.loads(content)
                for s in llm_tasks:
                    tasks.append(
                        MultiAgentTask(
                            task_id=s["task_id"],
                            title=s["title"],
                            description=s["description"],
                            assigned_agent=s.get("assigned_agent"),
                            dependencies=s.get("dependencies", []),
                        )
                    )
            except Exception as e:
                logger.debug(f"LLM planner failed: {e}. Falling back to default list.")

        # Default fallback if empty
        if not tasks:
            tasks.append(
                MultiAgentTask(
                    task_id=f"task_gen_{int(time.time())}",
                    title="Accomplish Objective",
                    description=goal,
                    assigned_agent="agent_software",
                )
            )

        for t in tasks:
            self._tasks[t.task_id] = t
            self._sync_task_to_graph(t)

        self._save_data()
        return tasks

    def _sync_task_to_graph(self, task: MultiAgentTask) -> None:
        graph_svc = self._get_graph_service()
        if graph_svc:
            try:
                graph_svc.create_entity(
                    GraphEntity(
                        entity_id=f"task_{task.task_id}",
                        entity_type=EntityType.TASK,
                        name=task.title,
                        properties={"description": task.description, "status": task.status},
                    )
                )
                for dep in task.dependencies:
                    graph_svc.create_relationship(
                        GraphRelationship(
                            relationship_id=f"rel_dep_{task.task_id}_{dep}",
                            source_id=f"task_{task.task_id}",
                            target_id=f"task_{dep}",
                            relationship_type=RelationshipType.DEPENDS_ON,
                        )
                    )
            except Exception as e:
                logger.warning(f"Could not sync task to knowledge graph: {e}")

    # EXECUTION ENGINE
    def execute_plan(self, tasks: List[MultiAgentTask], parallel: bool = False) -> bool:
        """Executes a list of multi-agent tasks, tracking status and ownership."""
        logger.info(f"Starting Multi-Agent Execution of {len(tasks)} tasks.")
        completed_tasks = set()
        failed_tasks = set()

        for t in tasks:
            self._tasks[t.task_id] = t

        while len(completed_tasks) + len(failed_tasks) < len(tasks):
            runnable_tasks = []
            for t in tasks:
                if t.task_id in completed_tasks or t.task_id in failed_tasks:
                    continue
                deps_met = all(dep in completed_tasks for dep in t.dependencies)
                if deps_met:
                    runnable_tasks.append(t)

            if not runnable_tasks:
                logger.error("Multi-Agent Execution deadlock or dependent task failure.")
                break

            for t in runnable_tasks:
                self._execute_single_task(t, completed_tasks, failed_tasks)

        return len(completed_tasks) == len(tasks)

    def _execute_single_task(
        self, task: MultiAgentTask, completed_set: set, failed_set: set
    ) -> None:
        task.status = "running"
        agent_id = task.assigned_agent or "agent_software"

        desc = self._find_descriptor(agent_id)
        agent_name = desc.name if desc else "SoftwareEngineer"
        agent = self._agents.get(agent_name.lower())

        if not agent:
            task.results = f"Simulated fallback run. Accomplished: {task.description}"
            task.status = "completed"
            completed_set.add(task.task_id)
            self._record_memory(task, success=True)
            return

        from aios.services.intent import Intent, IntentType

        intent = Intent(
            intent_type=IntentType.SYSTEM,
            target_service=self.__class__.__name__,
            action=task.title,
            parameters={"description": task.description},
            confidence=1.0,
        )

        ctx_svc = self._get_context_service()
        ws_context = ctx_svc.get_current_context() if ctx_svc else None

        agent_ctx = AgentContext(intent=intent, context=ws_context, memories=[], tools=[])

        try:
            graph_svc = self._get_graph_service()
            exec_id = f"exec_{task.task_id}"
            if graph_svc:
                try:
                    graph_svc.create_entity(
                        GraphEntity(
                            entity_id=exec_id,
                            entity_type=EntityType.EXECUTION,
                            name=f"Execution of {task.title}",
                            properties={"timestamp": time.time()},
                        )
                    )
                    graph_svc.create_relationship(
                        GraphRelationship(
                            relationship_id=f"rel_exec_{exec_id}",
                            source_id=exec_id,
                            target_id=f"task_{task.task_id}",
                            relationship_type=RelationshipType.USES,
                        )
                    )
                except Exception as exc:
                    logger.warning(f"Could not log execution node: {exc}")

            result = agent.execute(agent_ctx)

            if result.success:
                task.status = "completed"
                task.results = result.response
                completed_set.add(task.task_id)
                self._record_memory(task, success=True)

                if graph_svc:
                    try:
                        graph_svc.create_relationship(
                            GraphRelationship(
                                relationship_id=f"rel_comp_{task.task_id}",
                                source_id=f"agent_{agent_id}",
                                target_id=f"task_{task.task_id}",
                                relationship_type=RelationshipType.COMPLETED_BY,
                            )
                        )
                    except Exception as exc:
                        logger.warning(f"Could not log completion relationship: {exc}")

                if desc:
                    desc.performance_metrics["tasks_completed"] = (
                        desc.performance_metrics.get("tasks_completed", 0) + 1
                    )
                    total = desc.performance_metrics[
                        "tasks_completed"
                    ] + desc.performance_metrics.get("failures", 0)
                    desc.performance_metrics["success_rate"] = (
                        desc.performance_metrics["tasks_completed"] / total
                    )
            else:
                task.status = "failed"
                task.results = result.response
                failed_set.add(task.task_id)
                self._record_memory(task, success=False)
                if desc:
                    desc.performance_metrics["failures"] = (
                        desc.performance_metrics.get("failures", 0) + 1
                    )
                    total = (
                        desc.performance_metrics.get("tasks_completed", 0)
                        + desc.performance_metrics["failures"]
                    )
                    desc.performance_metrics["success_rate"] = (
                        desc.performance_metrics.get("tasks_completed", 0) / total
                    )
        except Exception as e:
            logger.error(f"Task {task.task_id} execution failed: {e}")
            task.status = "failed"
            task.results = str(e)
            failed_set.add(task.task_id)
            self._record_memory(task, success=False)
            if desc:
                desc.performance_metrics["failures"] = (
                    desc.performance_metrics.get("failures", 0) + 1
                )
                total = (
                    desc.performance_metrics.get("tasks_completed", 0)
                    + desc.performance_metrics["failures"]
                )
                desc.performance_metrics["success_rate"] = (
                    desc.performance_metrics.get("tasks_completed", 0) / total
                )

        if desc:
            if task.task_id in desc.assigned_tasks:
                desc.assigned_tasks.remove(task.task_id)
            if not desc.assigned_tasks:
                desc.status = "idle"
        self._save_data()

    # AGENT MEMORY
    def _record_memory(self, task: MultiAgentTask, success: bool) -> None:
        lesson = "N/A"
        if not success:
            lesson = (
                f"Task '{task.title}' failed during execution. Need to investigate: {task.results}"
            )
        else:
            lesson = (
                f"Successfully completed '{task.title}'. Derived result: {task.results[:100]}..."
            )

        memory_entry = {
            "task_id": task.task_id,
            "title": task.title,
            "description": task.description,
            "success": success,
            "results": task.results,
            "assigned_agent": task.assigned_agent,
            "timestamp": time.time(),
            "lesson_learned": lesson,
        }
        self._memory_logs.append(memory_entry)

        desc = self._find_descriptor(task.assigned_agent) if task.assigned_agent else None
        if desc:
            mem_id = f"mem_agent_{task.assigned_agent}_{int(time.time())}"
            desc.memory_references.append(mem_id)

        self._save_data()

    def get_agent_memory(self, agent_id: str) -> List[Dict[str, Any]]:
        return [m for m in self._memory_logs if m.get("assigned_agent") == agent_id]

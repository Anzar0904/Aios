"""
aios/local/core_intelligence.py

Core Intelligence Layer implementation for AI OS (Phase 4).
Contains:
- Universal Task Engine
- Decision Engine
- Context Engine
- Event Bus extensions
- Notification Center
- Goal Engine
- Priority Engine
- Scheduler
- Plugin Registry
- Skill Registry
- Universal Action Engine
- Memory Index
- AI Planner
- AI Supervisor
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from aios.services.base import ServiceLifecycle

logger = logging.getLogger(__name__)


# --- Event Bus & Notification Definitions ---
@dataclass
class Event:
    event_type: str
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)


@dataclass
class Notification:
    notification_id: str
    title: str
    message: str
    severity: str  # Info, Success, Warning, Error, Critical
    timestamp: float = field(default_factory=time.time)


# --- Task Definition ---
@dataclass
class Task:
    task_id: str
    title: str
    description: str
    priority: str  # Critical, High, Medium, Low
    project: str
    workspace: str
    status: str  # Pending, In Progress, Completed, Failed
    dependencies: List[str] = field(default_factory=list)
    estimated_time: float = 1.0  # hours
    assigned_model: str = "deepseek-r1"
    required_skill: str = ""
    created_time: float = field(default_factory=time.time)
    completed_time: Optional[float] = None


# --- Goal Definition ---
@dataclass
class Goal:
    goal_id: str
    title: str
    category: str  # Daily, Weekly, Monthly, Sprint, Project, Agency, Hackathon
    target_date: str
    status: str  # Pending, In Progress, Achieved
    progress: float = 0.0  # 0.0 to 100.0


# --- Plugin & Skill Definitions ---
@dataclass
class Plugin:
    name: str
    version: str
    capabilities: List[str]
    dependencies: List[str]
    health: str  # Healthy, Degraded, Offline
    status: str  # Active, Disabled


@dataclass
class Skill:
    name: str
    description: str
    capability_type: str
    complexity: str  # High, Medium, Low


# --- Context Definition ---
@dataclass
class CoreContext:
    current_project: str = "Aios"
    current_sprint: str = "Sprint 31"
    current_branch: str = "main"
    current_workspace: str = "AI OS"
    current_client: str = "Default Client"
    current_hackathon: str = "Global AI Hackathon"
    current_conversation: str = "N/A"
    current_session: str = "N/A"
    current_active_models: List[str] = field(default_factory=list)


# --- 1. Universal Task Engine ---
class TaskEngine(ServiceLifecycle):
    def __init__(self, storage_path: Path = Path(".agent/tasks.json")) -> None:
        super().__init__()
        self.storage_path = storage_path
        self._tasks: Dict[str, Task] = {}
        self.load_tasks()

    def load_tasks(self) -> None:
        if not self.storage_path.is_file():
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for tid, tdata in data.items():
                    self._tasks[tid] = Task(**tdata)
        except Exception as e:
            logger.error("Failed to load tasks: %s", e)

    def save_tasks(self) -> None:
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump({tid: asdict(t) for tid, t in self._tasks.items()}, f, indent=4)
        except Exception as e:
            logger.error("Failed to save tasks: %s", e)

    def create_task(self, task: Task) -> Task:
        self._tasks[task.task_id] = task
        self.save_tasks()
        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def list_tasks(self) -> List[Task]:
        return list(self._tasks.values())

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Task]:
        t = self._tasks.get(task_id)
        if t:
            for k, v in updates.items():
                if hasattr(t, k):
                    setattr(t, k, v)
            if t.status == "Completed" and not t.completed_time:
                t.completed_time = time.time()
            self.save_tasks()
            return t
        return None

    def delete_task(self, task_id: str) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            self.save_tasks()
            return True
        return False


# --- 2. Decision Engine ---
class DecisionEngine(ServiceLifecycle):
    def __init__(self, model_registry: Any = None) -> None:
        super().__init__()
        self._registry = model_registry

    def choose_model(self, task_priority: str, required_skill: str) -> str:
        # Prioritize reasoning models for critical/high tasks
        if task_priority in ("Critical", "High") or "code" in required_skill.lower():
            return "deepseek-r1"
        return "gemma3:4b"

    def choose_tool(self, required_skill: str) -> str:
        skill = required_skill.lower()
        if "code" in skill or "git" in skill:
            return "DeveloperWorkspaceTool"
        elif "notion" in skill:
            return "NotionIntegrationTool"
        elif "meeting" in skill or "lead" in skill:
            return "AgencyCRMTool"
        return "StandardLLMTool"

    def choose_retry_strategy(self, task_status: str) -> Dict[str, Any]:
        return {
            "max_retries": 3,
            "backoff_factor": 2.0,
            "retry_on": ["ConnectionError", "TimeoutException"],
        }


# --- 3. Context Engine ---
class ContextEngine(ServiceLifecycle):
    def __init__(self, storage_path: Path = Path(".agent/context.json")) -> None:
        super().__init__()
        self.storage_path = storage_path
        self._ctx = CoreContext()
        self.load_context()

    def load_context(self) -> None:
        if not self.storage_path.is_file():
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._ctx = CoreContext(**data)
        except Exception as e:
            logger.error("Failed to load context: %s", e)

    def save_context(self) -> None:
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(asdict(self._ctx), f, indent=4)
        except Exception as e:
            logger.error("Failed to save context: %s", e)

    def get_current(self) -> CoreContext:
        return self._ctx

    def update_context(self, updates: Dict[str, Any]) -> CoreContext:
        for k, v in updates.items():
            if hasattr(self._ctx, k):
                setattr(self._ctx, k, v)
        self.save_context()
        return self._ctx


# --- 4. Event Bus ---
class EventBus(ServiceLifecycle):
    def __init__(self) -> None:
        super().__init__()
        self._listeners: Dict[str, List[Callable[[Event], None]]] = {}

    def subscribe(self, event_type: str, callback: Callable[[Event], None]) -> None:
        self._listeners.setdefault(event_type, []).append(callback)

    def publish(self, event: Event) -> None:
        for cb in self._listeners.get(event.event_type, []):
            try:
                cb(event)
            except Exception as e:
                logger.error("Error in event listener for %s: %s", event.event_type, e)


# --- 5. Notification Center ---
class NotificationCenter(ServiceLifecycle):
    def __init__(self, storage_path: Path = Path(".agent/notifications.json")) -> None:
        super().__init__()
        self.storage_path = storage_path
        self._notifications: List[Notification] = []
        self.load_notifications()

    def load_notifications(self) -> None:
        if not self.storage_path.is_file():
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._notifications = [Notification(**n) for n in data]
        except Exception as e:
            logger.error("Failed to load notifications: %s", e)

    def save_notifications(self) -> None:
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump([asdict(n) for n in self._notifications], f, indent=4)
        except Exception as e:
            logger.error("Failed to save notifications: %s", e)

    def create_notification(self, title: str, message: str, severity: str) -> Notification:
        n = Notification(
            notification_id=f"notif_{int(time.time() * 1000)}",
            title=title,
            message=message,
            severity=severity,
        )
        self._notifications.append(n)
        self.save_notifications()
        return n

    def list_notifications(self, min_severity: Optional[str] = None) -> List[Notification]:
        severities = ["Info", "Success", "Warning", "Error", "Critical"]
        if min_severity:
            min_idx = severities.index(min_severity)
            return [n for n in self._notifications if severities.index(n.severity) >= min_idx]
        return self._notifications


# --- 6. Goal Engine ---
class GoalEngine(ServiceLifecycle):
    def __init__(self, storage_path: Path = Path(".agent/goals.json")) -> None:
        super().__init__()
        self.storage_path = storage_path
        self._goals: Dict[str, Goal] = {}
        self.load_goals()

    def load_goals(self) -> None:
        if not self.storage_path.is_file():
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for gid, gdata in data.items():
                    self._goals[gid] = Goal(**gdata)
        except Exception as e:
            logger.error("Failed to load goals: %s", e)

    def save_goals(self) -> None:
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump({gid: asdict(g) for gid, g in self._goals.items()}, f, indent=4)
        except Exception as e:
            logger.error("Failed to save goals: %s", e)

    def create_goal(self, goal: Goal) -> Goal:
        self._goals[goal.goal_id] = goal
        self.save_goals()
        return goal

    def get_goal(self, goal_id: str) -> Optional[Goal]:
        return self._goals.get(goal_id)

    def list_goals(self, category: Optional[str] = None) -> List[Goal]:
        if category:
            return [g for g in self._goals.values() if g.category.lower() == category.lower()]
        return list(self._goals.values())

    def update_goal(self, goal_id: str, updates: Dict[str, Any]) -> Optional[Goal]:
        g = self._goals.get(goal_id)
        if g:
            for k, v in updates.items():
                if hasattr(g, k):
                    setattr(g, k, v)
            self.save_goals()
            return g
        return None


# --- 7. Priority Engine ---
class PriorityEngine(ServiceLifecycle):
    def __init__(self) -> None:
        super().__init__()

    def calculate_priority_score(self, task: Task, context: CoreContext) -> float:
        # Base weights
        score = 0.0

        # Priority mapping
        priority_weights = {"Critical": 100.0, "High": 75.0, "Medium": 50.0, "Low": 25.0}
        score += priority_weights.get(task.priority, 0.0)

        # Context alignment
        if task.project == context.current_project:
            score += 20.0
        if task.workspace == context.current_workspace:
            score += 15.0

        # Dependencies weight
        score += len(task.dependencies) * 10.0

        return score


# --- 8. Scheduler ---
class Scheduler(ServiceLifecycle):
    def __init__(self, storage_path: Path = Path(".agent/scheduler.json")) -> None:
        super().__init__()
        self.storage_path = storage_path
        self._jobs: Dict[str, Dict[str, Any]] = {}
        self.load_scheduler()

    def load_scheduler(self) -> None:
        if not self.storage_path.is_file():
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                self._jobs = json.load(f)
        except Exception as e:
            logger.error("Failed to load scheduler: %s", e)

    def save_scheduler(self) -> None:
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self._jobs, f, indent=4)
        except Exception as e:
            logger.error("Failed to save scheduler: %s", e)

    def register_job(self, job_id: str, interval: float, last_run: float = 0.0) -> None:
        self._jobs[job_id] = {"interval": interval, "last_run": last_run}
        self.save_scheduler()

    def list_jobs(self) -> Dict[str, Dict[str, Any]]:
        return self._jobs

    def trigger_job(self, job_id: str) -> None:
        if job_id in self._jobs:
            self._jobs[job_id]["last_run"] = time.time()
            self.save_scheduler()


# --- 9. Plugin Registry ---
class PluginRegistry(ServiceLifecycle):
    def __init__(self, storage_path: Path = Path(".agent/plugins.json")) -> None:
        super().__init__()
        self.storage_path = storage_path
        self._plugins: Dict[str, Plugin] = {}
        self.load_plugins()

    def load_plugins(self) -> None:
        if not self.storage_path.is_file():
            # Seed default core plugins
            self.register_plugin(
                Plugin(
                    name="GitHubPlugin",
                    version="1.0.0",
                    capabilities=["Create Issue", "Merge PR", "Review PR", "Release"],
                    dependencies=[],
                    health="Healthy",
                    status="Active",
                )
            )
            self.register_plugin(
                Plugin(
                    name="NotionPlugin",
                    version="1.0.0",
                    capabilities=["Create Page", "Update Page", "Archive Page"],
                    dependencies=[],
                    health="Healthy",
                    status="Active",
                )
            )
            self.register_plugin(
                Plugin(
                    name="AgencyPlugin",
                    version="1.0.0",
                    capabilities=["Create Lead", "Send Proposal", "Schedule Meeting"],
                    dependencies=[],
                    health="Healthy",
                    status="Active",
                )
            )
            self.register_plugin(
                Plugin(
                    name="n8nPlugin",
                    version="1.0.0",
                    capabilities=["Create Workflow", "Deploy Workflow", "Execute Workflow"],
                    dependencies=[],
                    health="Healthy",
                    status="Active",
                )
            )
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for name, pdata in data.items():
                    self._plugins[name] = Plugin(**pdata)
        except Exception as e:
            logger.error("Failed to load plugins: %s", e)

    def save_plugins(self) -> None:
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump({name: asdict(p) for name, p in self._plugins.items()}, f, indent=4)
        except Exception as e:
            logger.error("Failed to save plugins: %s", e)

    def register_plugin(self, plugin: Plugin) -> Plugin:
        self._plugins[plugin.name] = plugin
        self.save_plugins()
        return plugin

    def list_plugins(self) -> List[Plugin]:
        return list(self._plugins.values())


# --- 10. Skill Registry ---
class SkillRegistry(ServiceLifecycle):
    def __init__(self, storage_path: Path = Path(".agent/skills.json")) -> None:
        super().__init__()
        self.storage_path = storage_path
        self._skills: Dict[str, Skill] = {}
        self.load_skills()

    def load_skills(self) -> None:
        if not self.storage_path.is_file():
            # Seed default skills
            skills_data = [
                Skill(
                    "Generate Code",
                    "Produces high-quality Python/Typescript programs",
                    "coding",
                    "High",
                ),
                Skill(
                    "Review Code", "Analyzes codebase for bugs and compliance", "linting", "Medium"
                ),
                Skill(
                    "Generate Workflow",
                    "Designs JSON workflows for n8n platform",
                    "automation",
                    "Medium",
                ),
                Skill(
                    "Deploy Workflow",
                    "Deploys executable handlers in production",
                    "deployment",
                    "High",
                ),
                Skill(
                    "Research Paper",
                    "Pulls publications and compiles summaries",
                    "research",
                    "High",
                ),
                Skill("Summarize", "Generates concise bulleted reports", "utility", "Low"),
                Skill(
                    "Create Proposal",
                    "Drafts project scope and cost estimates",
                    "business",
                    "Medium",
                ),
                Skill(
                    "Generate Docs",
                    "Autogenerates markdown specifications and Guides",
                    "documentation",
                    "Low",
                ),
                Skill(
                    "Analyze Logs", "Parses stdout logs for root failures", "diagnostics", "Medium"
                ),
            ]
            for s in skills_data:
                self.register_skill(s)
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for name, sdata in data.items():
                    self._skills[name] = Skill(**sdata)
        except Exception as e:
            logger.error("Failed to load skills: %s", e)

    def save_skills(self) -> None:
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump({name: asdict(s) for name, s in self._skills.items()}, f, indent=4)
        except Exception as e:
            logger.error("Failed to save skills: %s", e)

    def register_skill(self, skill: Skill) -> Skill:
        self._skills[skill.name] = skill
        self.save_skills()
        return skill

    def list_skills(self) -> List[Skill]:
        return list(self._skills.values())


# --- 11. Universal Action Engine ---
class ActionEngine(ServiceLifecycle):
    def __init__(self) -> None:
        super().__init__()
        self._actions: Dict[str, Dict[str, Callable[..., Any]]] = {}

    def register_action(self, module_name: str, action_name: str, func: Callable[..., Any]) -> None:
        self._actions.setdefault(module_name, {})[action_name] = func

    def execute_action(self, module_name: str, action_name: str, *args: Any, **kwargs: Any) -> Any:
        module = self._actions.get(module_name)
        if not module:
            raise ValueError(f"Module '{module_name}' is not registered.")
        func = module.get(action_name)
        if not func:
            raise ValueError(
                f"Action '{action_name}' is not registered under module '{module_name}'."
            )
        return func(*args, **kwargs)


# --- 12. Memory Index ---
class MemoryIndex(ServiceLifecycle):
    def __init__(self, storage_path: Path = Path(".agent/memory_index.json")) -> None:
        super().__init__()
        self.storage_path = storage_path
        self._index: Dict[str, List[Dict[str, Any]]] = {}
        self.load_index()

    def load_index(self) -> None:
        if not self.storage_path.is_file():
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                self._index = json.load(f)
        except Exception as e:
            logger.error("Failed to load memory index: %s", e)

    def save_index(self) -> None:
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(self._index, f, indent=4)
        except Exception as e:
            logger.error("Failed to save memory index: %s", e)

    def index_item(self, category: str, item_id: str, metadata: Dict[str, Any]) -> None:
        entry = {"item_id": item_id, "timestamp": time.time(), "metadata": metadata}
        self._index.setdefault(category, []).append(entry)
        self.save_index()

    def search_category(self, category: str) -> List[Dict[str, Any]]:
        return self._index.get(category, [])


# --- 13. AI Planner ---
class AIPlanner(ServiceLifecycle):
    def __init__(self) -> None:
        super().__init__()

    def plan_objective(self, objective: str) -> List[Task]:
        # Simple rule-based planner breaking down complex objectives into dependency order tasks
        plan_tasks = []
        obj_lower = objective.lower()

        if "crm" in obj_lower or "build" in obj_lower:
            plan_tasks = [
                Task(
                    "plan_1",
                    "Architecture Blueprint",
                    "Design backend and schema databases",
                    "High",
                    "Aios",
                    "AI OS",
                    "Pending",
                ),
                Task(
                    "plan_2",
                    "Backend Integration",
                    "Construct endpoint nodes and routers",
                    "High",
                    "Aios",
                    "AI OS",
                    "Pending",
                    ["plan_1"],
                ),
                Task(
                    "plan_3",
                    "Frontend Renders",
                    "Build GUI dashboard layouts",
                    "Medium",
                    "Aios",
                    "AI OS",
                    "Pending",
                    ["plan_2"],
                ),
                Task(
                    "plan_4",
                    "Deployment & Verification",
                    "Release production artifacts",
                    "Medium",
                    "Aios",
                    "AI OS",
                    "Pending",
                    ["plan_3"],
                ),
            ]
        else:
            plan_tasks = [
                Task(
                    "plan_default",
                    f"Execute: {objective}",
                    f"Perform actions to satisfy {objective}",
                    "Medium",
                    "Aios",
                    "AI OS",
                    "Pending",
                )
            ]
        return plan_tasks


# --- 14. AI Supervisor ---
class AISupervisor(ServiceLifecycle):
    def __init__(self, diagnostics_provider: Any = None) -> None:
        super().__init__()
        self.diagnostics_provider = diagnostics_provider

    def monitor_services(self, registry: Any) -> Dict[str, Any]:
        report = {
            "status": "Healthy",
            "active_services": 0,
            "failed_count": 0,
            "actions_required": [],
        }
        if not registry:
            return report

        for svc in registry.get_all():
            report["active_services"] += 1
            # If service crashed or failed, log it
            if hasattr(svc, "_state") and svc._state == "HALTED":
                report["status"] = "Degraded"
                report["failed_count"] += 1
                report["actions_required"].append(f"Restart service: {svc.__class__.__name__}")

        return report

    def run_recovery_strategy(self, service_name: str) -> bool:
        logger.warning("Triggered recovery cycle for service: %s", service_name)
        # Mock recovery logic - returns True for successfully recovered service
        return True

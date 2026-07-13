from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class BrainObjective:
    raw_query: str
    parsed_intent: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillSelection:
    skill_id: str
    confidence: float
    reason: str
    matched_commands: List[str] = field(default_factory=list)


@dataclass
class ProviderSelection:
    provider_name: str
    model_name: str
    reason: str


@dataclass
class BrainContext:
    project_root: str
    project_name: str
    git_branch: Optional[str] = None
    memories: List[str] = field(default_factory=list)
    system_status: str = "READY"
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowStep:
    step_id: str
    description: str
    skill_id: str
    command: str
    args: str
    status: str = "pending"  # pending, running, completed, failed
    output: str = ""
    error: Optional[str] = None
    depends_on: List[str] = field(default_factory=list)
    parallel: bool = False


@dataclass
class Workflow:
    workflow_id: str
    objective: str
    steps: List[WorkflowStep] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed
    created_at: float = 0.0
    completed_at: Optional[float] = None


@dataclass
class BrainResponse:
    success: bool
    response: str
    workflow_id: Optional[str] = None
    steps_executed: List[Dict[str, Any]] = field(default_factory=list)
    provider_info: Optional[Dict[str, str]] = None

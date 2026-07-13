import abc
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle


class MissionStatus(Enum):
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class MissionTask:
    task_id: str
    name: str
    assigned_agent: str
    status: MissionStatus = MissionStatus.PENDING
    result: Optional[str] = None


@dataclass
class MissionMilestone:
    milestone_id: str
    name: str
    tasks: List[MissionTask] = field(default_factory=list)
    status: MissionStatus = MissionStatus.PENDING


@dataclass
class Mission:
    mission_id: str
    title: str
    objective: str
    milestones: List[MissionMilestone] = field(default_factory=list)
    status: MissionStatus = MissionStatus.PENDING
    current_milestone_index: int = 0


@dataclass
class MissionGoal:
    goal_id: str
    objective: str
    target_date: str
    category: str = "general"


@dataclass
class MissionContext:
    variables: Dict[str, Any] = field(default_factory=dict)


class MissionPlanner(abc.ABC):
    @abc.abstractmethod
    def plan_mission(self, objective: str, context: MissionContext) -> Mission:
        """Decomposes a long-term goal objective into structured milestones and tasks."""
        pass


class MissionExecutor(abc.ABC):
    @abc.abstractmethod
    def execute_mission(self, mission: Mission, context: MissionContext) -> bool:
        """Executes milestones sequentially, delegating tasks to agents."""
        pass


class MissionRepository(abc.ABC):
    @abc.abstractmethod
    def save_mission(self, mission: Mission) -> None:
        """Persists a mission state."""
        pass

    @abc.abstractmethod
    def load_mission(self, mission_id: str) -> Optional[Mission]:
        """Loads a persisted mission."""
        pass

    @abc.abstractmethod
    def list_missions(self) -> List[Mission]:
        """Lists all missions."""
        pass


class MissionEngine(ServiceLifecycle, abc.ABC):
    @abc.abstractmethod
    def create_mission(self, title: str, objective: str) -> Mission:
        """Creates and registers a new mission."""
        pass

    @abc.abstractmethod
    def start_mission(self, mission_id: str) -> bool:
        """Initiates execution of a registered mission."""
        pass

    @abc.abstractmethod
    def cancel_mission(self, mission_id: str) -> bool:
        """Cancels a running mission."""
        pass

    @abc.abstractmethod
    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """Retrieves a mission state."""
        pass

import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle


@dataclass
class DailyTask:
    task_id: str
    title: str
    priority: str  # Critical, High, Medium, Low
    effort_hours: float
    deadline: Optional[str] = None
    completed: bool = False
    estimated_duration_mins: float = 60.0
    deadline_impact: str = "Low"
    career_impact: str = "Low"
    mission_impact: str = "Low"
    learning_impact: str = "Low"
    status: str = "Not Started"  # Not Started, In Progress, Paused, Completed, Cancelled
    start_time: Optional[float] = None
    finish_time: Optional[float] = None
    actual_duration_mins: float = 0.0
    completion_percentage: float = 0.0


@dataclass
class ScheduleItem:
    time_slot: str
    task_id: str
    task_title: str
    item_type: str = "focus"  # focus, break


@dataclass
class DailySchedule:
    items: List[ScheduleItem] = field(default_factory=list)


@dataclass
class WorkSession:
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    duration_mins: float = 0.0
    task_id: str = ""
    mission_id: str = ""
    category: str = ""
    notes: str = ""


@dataclass
class DailyReviewSummary:
    completed_tasks: List[str] = field(default_factory=list)
    incomplete_tasks: List[str] = field(default_factory=list)
    mission_progress: List[str] = field(default_factory=list)
    career_progress: List[str] = field(default_factory=list)
    learning_progress: List[str] = field(default_factory=list)
    project_activity: List[str] = field(default_factory=list)
    github_activity: List[str] = field(default_factory=list)
    productivity_summary: str = ""
    tomorrow_priorities: List[str] = field(default_factory=list)
    suggested_improvements: List[str] = field(default_factory=list)


@dataclass
class DailyPlan:
    date: str
    tasks: List[DailyTask] = field(default_factory=list)
    schedule: DailySchedule = field(default_factory=DailySchedule)
    workload_summary: Dict[str, Any] = field(default_factory=dict)
    sessions: List[WorkSession] = field(default_factory=list)
    review: Optional[DailyReviewSummary] = None


class PriorityCalculator(abc.ABC):
    @abc.abstractmethod
    def calculate_priority(self, task: DailyTask) -> str:
        """Determines the final priority level (Critical, High, Medium, Low) of a task."""
        pass


class WorkloadEstimator(abc.ABC):
    @abc.abstractmethod
    def estimate_workload(self, tasks: List[DailyTask]) -> Dict[str, Any]:
        """Calculates total hours, overloaded schedule detection, remaining work, and capacity."""
        pass


class ScheduleOptimizer(abc.ABC):
    @abc.abstractmethod
    def optimize_schedule(self, tasks: List[DailyTask]) -> DailySchedule:
        """Orders tasks, groups similar work, reduces context switching, and recommends focus/break periods."""
        pass


class TaskPrioritizer(abc.ABC):
    @abc.abstractmethod
    def prioritize_tasks(self, tasks: List[DailyTask]) -> List[DailyTask]:
        """Calculates priorities and updates task models."""
        pass


class ProgressTracker(abc.ABC):
    @abc.abstractmethod
    def update_task_status(self, task_id: str, status: str, completion_percentage: float = 0.0) -> DailyTask:
        """Updates task execution status and start/finish timestamps."""
        pass

    @abc.abstractmethod
    def get_task(self, task_id: str) -> Optional[DailyTask]:
        """Retrieves a single task status."""
        pass

    @abc.abstractmethod
    def list_tasks(self) -> List[DailyTask]:
        """Lists active tasks."""
        pass


class SessionRecorder(abc.ABC):
    @abc.abstractmethod
    def start_session(self, task_id: str, mission_id: str, category: str, notes: str) -> WorkSession:
        """Logs start of a work session associated with a task/mission."""
        pass

    @abc.abstractmethod
    def end_session(self, session_id: str, notes: str) -> WorkSession:
        """Logs end of a work session and calculates duration."""
        pass

    @abc.abstractmethod
    def list_sessions(self, task_id: Optional[str] = None) -> List[WorkSession]:
        """Lists logged work sessions."""
        pass


class DailyReview(abc.ABC):
    @abc.abstractmethod
    def generate_review(self) -> DailyReviewSummary:
        """Generates an intelligent end-of-day summary using current tasks, commits, and goals."""
        pass


class ProductivityAnalyzer(abc.ABC):
    @abc.abstractmethod
    def analyze_productivity(self) -> Dict[str, Any]:
        """Calculates performance indicators like completion rate, focus time, and planning accuracy."""
        pass


class DailyPlanner(abc.ABC):
    @abc.abstractmethod
    def plan_day(self) -> DailyPlan:
        """Automatically generates a prioritized daily plan using missions, goals, tasks, and code metrics."""
        pass


class DailyOSService(ServiceLifecycle, abc.ABC):
    """Unified service interface coordinating Daily OS components."""

    @property
    @abc.abstractmethod
    def planner(self) -> DailyPlanner:
        pass

    @property
    @abc.abstractmethod
    def prioritizer(self) -> TaskPrioritizer:
        pass

    @property
    @abc.abstractmethod
    def priority_calculator(self) -> PriorityCalculator:
        pass

    @property
    @abc.abstractmethod
    def workload_estimator(self) -> WorkloadEstimator:
        pass

    @property
    @abc.abstractmethod
    def schedule_optimizer(self) -> ScheduleOptimizer:
        pass

    @property
    @abc.abstractmethod
    def progress_tracker(self) -> ProgressTracker:
        pass

    @property
    @abc.abstractmethod
    def session_recorder(self) -> SessionRecorder:
        pass

    @property
    @abc.abstractmethod
    def daily_review(self) -> DailyReview:
        pass

    @property
    @abc.abstractmethod
    def productivity_analyzer(self) -> ProductivityAnalyzer:
        pass

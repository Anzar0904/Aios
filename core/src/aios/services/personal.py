from __future__ import annotations

import abc
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle


@dataclass
class Contact:
    email: str
    phone: str = ""
    location: str = ""


@dataclass
class SocialProfile:
    platform: str
    url: str


@dataclass
class Experience:
    company: str
    role: str
    start_date: str
    end_date: str = "Present"
    description: str = ""


@dataclass
class Education:
    institution: str
    degree: str
    field_of_study: str
    grad_date: str


@dataclass
class SkillProfile:
    category: str
    skills: List[str] = field(default_factory=list)


@dataclass
class ProjectReference:
    name: str
    description: str
    url: str = ""


@dataclass
class ResumeVersion:
    version: int
    summary: str
    experiences: List[Experience] = field(default_factory=list)
    educations: List[Education] = field(default_factory=list)
    skills: List[SkillProfile] = field(default_factory=list)
    projects: List[ProjectReference] = field(default_factory=list)
    created_at: float = 0.0


@dataclass
class Resume:
    id: str
    title: str
    versions: List[ResumeVersion] = field(default_factory=list)
    current_version: int = 1


@dataclass
class PortfolioProject:
    id: str
    name: str
    description: str
    technologies: List[str] = field(default_factory=list)
    repository_url: str = ""
    live_url: str = ""


@dataclass
class CareerProfile:
    industry: str
    current_role: str
    years_experience: float
    target_roles: List[str] = field(default_factory=list)


@dataclass
class Goal:
    id: str
    title: str
    target_date: str
    status: str = "pending"  # pending, in-progress, completed
    category: str = "career"


@dataclass
class LearningItem:
    id: str
    title: str
    source: str
    status: str = "not-started"  # not-started, reading, completed
    progress_percentage: float = 0.0


@dataclass
class Certificate:
    name: str
    issuing_organization: str
    issue_date: str
    credential_id: str = ""


@dataclass
class Achievement:
    title: str
    description: str
    date: str


@dataclass
class Preference:
    key: str
    value: Any
    category: str = "general"


@dataclass
class Template:
    id: str
    name: str
    content: str
    category: str = "resume"


@dataclass
class KnowledgeEntry:
    id: str
    title: str
    content: str
    tags: List[str] = field(default_factory=list)
    updated_at: float = 0.0


@dataclass
class DocumentReference:
    id: str
    title: str
    file_path: str
    category: str = "transcript"


@dataclass
class PersonalProfile:
    id: str  # student, professional, research, startup, personal
    name: str
    contact: Contact
    socials: List[SocialProfile] = field(default_factory=list)
    career: Optional[CareerProfile] = None
    resumes: List[Resume] = field(default_factory=list)
    portfolio: List[PortfolioProject] = field(default_factory=list)
    goals: List[Goal] = field(default_factory=list)
    learning: List[LearningItem] = field(default_factory=list)
    certificates: List[Certificate] = field(default_factory=list)
    achievements: List[Achievement] = field(default_factory=list)
    preferences: List[Preference] = field(default_factory=list)
    templates: List[Template] = field(default_factory=list)
    knowledge: List[KnowledgeEntry] = field(default_factory=list)
    documents: List[DocumentReference] = field(default_factory=list)
    version: int = 1


class PersonalService(ServiceLifecycle, abc.ABC):
    @abc.abstractmethod
    def get_profile(self, profile_id: str) -> Optional[PersonalProfile]:
        """Retrieves a specific personal profile."""
        pass

    @abc.abstractmethod
    def create_profile(self, profile: PersonalProfile) -> PersonalProfile:
        """Creates and persists a new personal profile."""
        pass

    @abc.abstractmethod
    def update_profile(self, profile_id: str, profile: PersonalProfile) -> PersonalProfile:
        """Updates and increments the version of an existing profile."""
        pass

    @abc.abstractmethod
    def delete_profile(self, profile_id: str) -> bool:
        """Deletes a personal profile."""
        pass

    @abc.abstractmethod
    def switch_active_profile(self, profile_id: str) -> bool:
        """Switches the active profile used for context injection."""
        pass

    @abc.abstractmethod
    def get_active_profile(self) -> Optional[PersonalProfile]:
        """Returns the currently active profile."""
        pass

    @abc.abstractmethod
    def list_profiles(self) -> List[str]:
        """Lists all registered profile identifiers."""
        pass

    @abc.abstractmethod
    def get_relevant_context(self, objective: str) -> Dict[str, Any]:
        """Performs intelligent context selection based on the objective query."""
        pass

    # ── Phase 11 Personal Intelligence Extensions ───────────────────────────

    @abc.abstractmethod
    def create_goal(self, goal: PersonalGoal) -> PersonalGoal:
        """Register a new personal target goal."""

    @abc.abstractmethod
    def get_goal(self, goal_id: str) -> Optional[PersonalGoal]:
        """Retrieve goal configuration."""

    @abc.abstractmethod
    def list_goals(self) -> List[PersonalGoal]:
        """List active targets goals."""

    @abc.abstractmethod
    def create_task(self, task: PersonalTask) -> PersonalTask:
        """Register a new task configuration."""

    @abc.abstractmethod
    def get_task(self, task_id: str) -> Optional[PersonalTask]:
        """Retrieve task details."""

    @abc.abstractmethod
    def list_tasks(self) -> List[PersonalTask]:
        """List tasks recorded in database."""

    @abc.abstractmethod
    def create_event(self, event: CalendarEvent) -> CalendarEvent:
        """Create a new calendar event."""

    @abc.abstractmethod
    def list_events(self) -> List[CalendarEvent]:
        """List upcoming calendar events."""

    @abc.abstractmethod
    def detect_calendar_conflicts(self) -> List[Dict[str, Any]]:
        """Scan calendar events for execution time overlaps."""

    @abc.abstractmethod
    def create_habit(self, habit: Habit) -> Habit:
        """Register a new habit track."""

    @abc.abstractmethod
    def increment_habit_streak(self, habit_id: str) -> Optional[Habit]:
        """Increment streak consistency scoring."""

    @abc.abstractmethod
    def list_habits(self) -> List[Habit]:
        """List habits streak statistics."""

    @abc.abstractmethod
    def create_reminder(self, reminder: PersonalReminder) -> PersonalReminder:
        """Create a new reminder flag."""

    @abc.abstractmethod
    def list_reminders(self) -> List[PersonalReminder]:
        """List reminders trigger events."""

    @abc.abstractmethod
    def create_note(self, note: PersonalNote) -> PersonalNote:
        """Record note bookmarks idea."""

    @abc.abstractmethod
    def list_notes(self) -> List[PersonalNote]:
        """List bookmarks notes list."""

    @abc.abstractmethod
    def create_learning_item(self, item: PersonalLearningItem) -> PersonalLearningItem:
        """Create learning courses topics item."""

    @abc.abstractmethod
    def list_learning_items(self) -> List[PersonalLearningItem]:
        """List active skills courses books."""

    @abc.abstractmethod
    def get_coach_recommendations(self) -> Dict[str, Any]:
        """Analyze goals/habits execution to formulate insights recommendations."""


# ── Phase 11 Personal Data Models ──────────────────────────────────────────


@dataclass
class PersonalGoal:
    goal_id: str
    title: str
    timeframe: str  # annual|quarterly|monthly|weekly|daily
    category: str  # career|agency|projects|research|learning|finance|health|personal
    priority: int = 1  # 1-5 scale
    status: str = "pending"  # pending|in_progress|achieved|failed
    progress: float = 0.0  # 0.0 to 100.0
    dependencies: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    target_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "title": self.title,
            "timeframe": self.timeframe,
            "category": self.category,
            "priority": self.priority,
            "status": self.status,
            "progress": self.progress,
            "dependencies": self.dependencies,
            "created_at": self.created_at,
            "target_date": self.target_date,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PersonalGoal:
        import json as _json

        deps = data.get("dependencies", [])
        if isinstance(deps, str):
            try:
                deps = _json.loads(deps)
            except Exception:
                deps = []

        return cls(
            goal_id=data["goal_id"],
            title=data["title"],
            timeframe=data["timeframe"],
            category=data["category"],
            priority=data.get("priority", 1),
            status=data.get("status", "pending"),
            progress=data.get("progress", 0.0),
            dependencies=deps,
            created_at=data.get("created_at", time.time()),
            target_date=data.get("target_date"),
        )


@dataclass
class PersonalTask:
    task_id: str
    title: str
    category: str  # personal|project|agency|research|learning
    priority: int = 1  # 1-5 scale
    status: str = "pending"  # pending|in_progress|completed
    due_date: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    context: str = ""
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "category": self.category,
            "priority": self.priority,
            "status": self.status,
            "due_date": self.due_date,
            "dependencies": self.dependencies,
            "context": self.context,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PersonalTask:
        import json as _json

        deps = data.get("dependencies", [])
        if isinstance(deps, str):
            try:
                deps = _json.loads(deps)
            except Exception:
                deps = []

        return cls(
            task_id=data["task_id"],
            title=data["title"],
            category=data["category"],
            priority=data.get("priority", 1),
            status=data.get("status", "pending"),
            due_date=data.get("due_date"),
            dependencies=deps,
            context=data.get("context", ""),
            created_at=data.get("created_at", time.time()),
        )


@dataclass
class CalendarEvent:
    event_id: str
    title: str
    start_time: float
    end_time: float
    category: str  # meeting|hackathon|class|agency_call|research_session
    priority: int = 1
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "title": self.title,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "category": self.category,
            "priority": self.priority,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CalendarEvent:
        return cls(
            event_id=data["event_id"],
            title=data["title"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            category=data["category"],
            priority=data.get("priority", 1),
            description=data.get("description", ""),
        )


@dataclass
class Habit:
    habit_id: str
    name: str
    frequency: str  # daily|weekly
    streak: int = 0
    success_rate: float = 100.0
    consistency_score: float = 100.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "habit_id": self.habit_id,
            "name": self.name,
            "frequency": self.frequency,
            "streak": self.streak,
            "success_rate": self.success_rate,
            "consistency_score": self.consistency_score,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Habit:
        return cls(
            habit_id=data["habit_id"],
            name=data["name"],
            frequency=data["frequency"],
            streak=data.get("streak", 0),
            success_rate=data.get("success_rate", 100.0),
            consistency_score=data.get("consistency_score", 100.0),
        )


@dataclass
class PersonalReminder:
    reminder_id: str
    title: str
    trigger_time: float
    reminder_type: str  # one_time|recurring
    status: str = "pending"  # pending|triggered|dismissed

    def to_dict(self) -> Dict[str, Any]:
        return {
            "reminder_id": self.reminder_id,
            "title": self.title,
            "trigger_time": self.trigger_time,
            "reminder_type": self.reminder_type,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PersonalReminder:
        return cls(
            reminder_id=data["reminder_id"],
            title=data["title"],
            trigger_time=data["trigger_time"],
            reminder_type=data["reminder_type"],
            status=data.get("status", "pending"),
        )


@dataclass
class PersonalNote:
    note_id: str
    title: str
    content: str
    category: str = "idea"  # idea|lesson|bookmark|decision
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "note_id": self.note_id,
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PersonalNote:
        return cls(
            note_id=data["note_id"],
            title=data["title"],
            content=data["content"],
            category=data.get("category", "idea"),
            created_at=data.get("created_at", time.time()),
        )


@dataclass
class PersonalLearningItem:
    item_id: str
    title: str
    item_type: str  # course|book|paper|skill|certification
    progress: float = 0.0  # 0.0 to 100.0
    status: str = "pending"  # pending|in_progress|completed

    def to_dict(self) -> Dict[str, Any]:
        return {
            "item_id": self.item_id,
            "title": self.title,
            "item_type": self.item_type,
            "progress": self.progress,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PersonalLearningItem:
        return cls(
            item_id=data["item_id"],
            title=data["title"],
            item_type=data["item_type"],
            progress=data.get("progress", 0.0),
            status=data.get("status", "pending"),
        )


def new_id() -> str:
    return str(uuid.uuid4())

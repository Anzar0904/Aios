import abc
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from aios.services.base import ServiceLifecycle
from aios.services.engineering_intelligence import EngineeringReport


@dataclass
class ImplementationTask:
    """Represents a discrete unit of development work."""
    task_id: str
    title: str
    description: str
    priority: str  # "High", "Medium", "Low"
    estimated_effort_hours: float
    affected_components: List[str]
    validation_requirements: List[str]
    completion_criteria: str
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationStep:
    """Represents a test or verification check."""
    step_id: str
    name: str
    command: str
    expected_result: str


@dataclass
class DevelopmentPhase:
    """Represents a high-level stage in the feature implementation lifecycle."""
    phase_id: str
    name: str
    description: str
    tasks: List[ImplementationTask]
    validation_steps: List[ValidationStep]


@dataclass
class SoftwareEngineeringPlan:
    """Detailed development plan translating architectural goals to implementation steps."""
    plan_id: str
    objective: str
    timestamp: float
    phases: List[DevelopmentPhase]
    execution_order: List[str]
    required_files: List[str]
    dependencies: Dict[str, List[str]]
    required_tests: List[str]
    documentation_updates: List[str]
    migration_requirements: List[str]
    rollback_strategy: str
    verification_strategy: str
    testing_strategy: str
    meta: Dict[str, Any] = field(default_factory=dict)


class FeaturePlanner(abc.ABC):
    """Generates high-level development phases and validation tasks for a feature."""

    @abc.abstractmethod
    def plan_features(self, objective: str, engineering_report: EngineeringReport) -> List[DevelopmentPhase]:
        """Maps an engineering report into a set of development phases with validation tasks."""
        pass


class TaskDecomposer(abc.ABC):
    """Decomposes a major feature objective into structured implementation tasks."""

    @abc.abstractmethod
    def decompose_tasks(self, objective: str, engineering_report: EngineeringReport) -> List[ImplementationTask]:
        """Breaks down a feature into discrete, validated, dependency-tracked tasks."""
        pass


class ExecutionPlanner(abc.ABC):
    """Plans low-risk execution order, dependency mapping, and rollback strategies."""

    @abc.abstractmethod
    def plan_execution(
        self,
        tasks: List[ImplementationTask]
    ) -> tuple[List[str], Dict[str, List[str]], str]:
        """Returns safest execution order, task dependencies, and rollback strategy."""
        pass


class FilePlanner(abc.ABC):
    """Identifies required files, creation targets, and migration requirements."""

    @abc.abstractmethod
    def plan_files(self, objective: str, engineering_report: EngineeringReport) -> tuple[List[str], List[str]]:
        """Identifies target files to change and any migration/setup requirements."""
        pass


class TestingPlanner(abc.ABC):
    """Plans testing strategies, validation steps, and required tests."""

    @abc.abstractmethod
    def plan_testing(self, objective: str, engineering_report: EngineeringReport) -> tuple[List[str], str, str]:
        """Determines required tests, validation strategy, and general testing strategy."""
        pass


class DocumentationPlanner(abc.ABC):
    """Identifies documentation and architecture guide updates."""

    @abc.abstractmethod
    def plan_documentation(self, objective: str, engineering_report: EngineeringReport) -> List[str]:
        """Identifies which READMEs, guides, or KB files require updating."""
        pass


class ImplementationPlanner(abc.ABC):
    """Orchestrator producing complete, structured SoftwareEngineeringPlans."""

    @abc.abstractmethod
    def plan_implementation(self, objective: str, engineering_report: EngineeringReport) -> SoftwareEngineeringPlan:
        """Constructs a comprehensive, validated SoftwareEngineeringPlan."""
        pass


class SoftwareEngineerService(ServiceLifecycle, abc.ABC):
    """Unified service for creating, storing, and publishing development plans."""

    @abc.abstractmethod
    def create_development_plan(self, objective: str, engineering_report: EngineeringReport) -> SoftwareEngineeringPlan:
        """Generates a complete SoftwareEngineeringPlan based on an EngineeringReport."""
        pass

    @abc.abstractmethod
    def store_development_plan(self, plan: SoftwareEngineeringPlan) -> None:
        """Stores the development plan inside Memory Intelligence."""
        pass

    @abc.abstractmethod
    def publish_development_plan(self, plan: SoftwareEngineeringPlan) -> None:
        """Publishes the development plan to the Knowledge Hub."""
        pass

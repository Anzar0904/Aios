import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Any, Optional
from aios.services.base import ServiceLifecycle
from aios.services.workspace_intelligence import CodeStructureSummary


class ModificationType(Enum):
    """File modification categories."""
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    RENAME = "rename"
    MOVE = "move"
    TEST = "test"
    DOCUMENT = "document"


@dataclass
class AffectedFile:
    """Represents a file impacted by the plan."""
    file_path: str
    modification_type: ModificationType
    reason: str
    risk_level: str  # "Low", "Medium", "High", "Critical"
    dependencies: List[str] = field(default_factory=list)


@dataclass
class AffectedDirectory:
    """Represents a directory containing impacted files."""
    dir_path: str
    reason: str
    affected_files_count: int


@dataclass
class ImplementationScope:
    """Consolidates files and directories within implementation bounds."""
    workspace_id: str
    affected_files: List[AffectedFile]
    affected_directories: List[AffectedDirectory]
    total_files_count: int


@dataclass
class PlanningResult:
    """Result of intelligent file planning containing dependencies, order, and risks."""
    planning_id: str
    objective: str
    scope: ImplementationScope
    implementation_sequence: List[str]
    direct_dependencies: Dict[str, List[str]]
    indirect_dependencies: Dict[str, List[str]]
    high_risk_dependencies: List[str]
    shared_interfaces: List[str]
    potential_breaking_points: List[str]
    circular_dependency_risks: List[str]
    interface_risks: List[str]
    shared_module_risks: List[str]
    configuration_risks: List[str]
    migration_risks: List[str]
    validation_checkpoints: List[str]
    testing_checkpoints: List[str]
    documentation_checkpoints: List[str]
    rollback_checkpoints: List[str]
    timestamp: float


class FileImpactAnalyzer(abc.ABC):
    """Determines exact files and folders impacted by the objective."""

    @abc.abstractmethod
    def analyze_impact(
        self,
        objective: str,
        code_summary: CodeStructureSummary
    ) -> tuple[List[AffectedFile], List[AffectedDirectory]]:
        """Identifies modification files, target directories, and reasons."""
        pass


class FileDependencyResolver(abc.ABC):
    """Resolves direct and indirect dependency chains across code imports."""

    @abc.abstractmethod
    def resolve_dependencies(
        self,
        affected_files: List[AffectedFile],
        code_summary: CodeStructureSummary
    ) -> tuple[Dict[str, List[str]], Dict[str, List[str]], List[str]]:
        """Resolves direct/indirect imports and flags high-risk paths."""
        pass


class ChangePlanner(abc.ABC):
    """Formulates sequence checkpoints, risks, and execution order."""

    @abc.abstractmethod
    def plan_changes(
        self,
        objective: str,
        scope: ImplementationScope,
        direct_deps: Dict[str, List[str]],
        code_summary: CodeStructureSummary
    ) -> PlanningResult:
        """Determines ordered sequence, classification risks, and checkpoints."""
        pass


class FilePlanner(ServiceLifecycle, abc.ABC):
    """Primary service coordinating file planning, memory storage, and publishing."""

    @abc.abstractmethod
    def generate_planning_result(
        self,
        workspace_id: str,
        objective: str,
        code_summary: CodeStructureSummary
    ) -> PlanningResult:
        """Analyzes a development objective and returns a structured planning result."""
        pass

    @abc.abstractmethod
    def store_planning_result(self, result: PlanningResult) -> None:
        """Stores the file planning summary inside Memory Intelligence."""
        pass

    @abc.abstractmethod
    def publish_planning_result(self, result: PlanningResult) -> None:
        """Syncs the file planning report with the Knowledge Hub."""
        pass

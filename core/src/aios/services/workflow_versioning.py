import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle


@dataclass
class WorkflowVersionMetadata:
    """Version metadata carrying author, tags, and semantic versions."""

    author: str
    version_tag: str
    semantic_version: str
    description: str
    status: str  # "active", "deprecated", "draft"


@dataclass
class WorkflowVersion:
    """Immutable workflow version object mapping telemetry, IR, and translations references."""

    version_id: str
    workflow_id: str
    workflow_ir_ref: str
    translation_ref: str
    optimization_ref: str
    approval_ref: str
    telemetry_ref: str
    creation_timestamp: float
    metadata: WorkflowVersionMetadata
    compatibility: str  # "compatible", "breaking"
    migration_notes: str
    rollback_target_id: Optional[str] = None
    previous_version_id: Optional[str] = None
    parent_version_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)


@dataclass
class WorkflowVersionGraph:
    """DAG graph structure tracking parent-child branches of version histories."""

    workflow_id: str
    versions: Dict[str, WorkflowVersion] = field(default_factory=dict)


@dataclass
class WorkflowVersionHistory:
    """Timeline catalog ordering run versions chronologically."""

    workflow_id: str
    history_timeline: List[WorkflowVersion] = field(default_factory=list)


@dataclass
class WorkflowVersionDiff:
    """Immutable difference payload outlining changes between two version states."""

    diff_id: str
    workflow_id: str
    from_version_id: str
    to_version_id: str
    added_nodes: List[str] = field(default_factory=list)
    removed_nodes: List[str] = field(default_factory=list)
    modified_nodes: List[str] = field(default_factory=list)
    connection_changes: List[str] = field(default_factory=list)
    policy_changes: List[str] = field(default_factory=list)
    trigger_changes: List[str] = field(default_factory=list)
    variable_changes: List[str] = field(default_factory=list)
    credential_reference_changes: List[str] = field(default_factory=list)
    scheduling_changes: List[str] = field(default_factory=list)
    metadata_changes: List[str] = field(default_factory=list)


@dataclass
class WorkflowSnapshot:
    """Immutable full workflow snapshot."""

    snapshot_id: str
    workflow_id: str
    version_id: str
    workflow_ir_json: str
    timestamp: float


@dataclass
class WorkflowEvolutionPlan:
    """Plan detailing upgrade sequence path recommendations."""

    plan_id: str
    workflow_id: str
    target_semantic_version: str
    steps: List[str] = field(default_factory=list)
    compatibility_status: str = "compatible"
    breaking_changes: List[str] = field(default_factory=list)


@dataclass
class WorkflowRollbackPlan:
    """Plan detailing rollback path steps. Never executed by this subsystem."""

    plan_id: str
    workflow_id: str
    target_version_id: str
    risk: str  # "high", "medium", "low"
    affected_workflows: List[str] = field(default_factory=list)
    migration_steps: List[str] = field(default_factory=list)
    validation_checklist: List[str] = field(default_factory=list)
    estimated_downtime_seconds: float = 0.0


@dataclass
class WorkflowVersionReport:
    """Consolidated summary report describing workspace versioning updates."""

    report_id: str
    workspace_id: str
    timeline_summaries: Dict[str, List[str]] = field(default_factory=dict)
    difs_count: int = 0
    timestamp: float = 0.0


class WorkflowVersionRegistry(abc.ABC):
    """Immutable version catalogs catalog."""

    @abc.abstractmethod
    def register_version(self, version: WorkflowVersion) -> None:
        """Saves immutable version structure."""
        pass

    @abc.abstractmethod
    def get_version(self, version_id: str) -> Optional[WorkflowVersion]:
        """Retrieves immutable version structure by ID."""
        pass

    @abc.abstractmethod
    def get_graph(self, workflow_id: str) -> Optional[WorkflowVersionGraph]:
        """Retrieves versions DAG graph for a workflow."""
        pass


class WorkflowCompatibilityAnalyzer(abc.ABC):
    """Analyzes semver bounds, parameters updates, and breaking changes."""

    @abc.abstractmethod
    def analyze_compatibility(
        self, from_ver: WorkflowVersion, to_ver: WorkflowVersion
    ) -> Dict[str, Any]:
        """Returns upgrade compatibility results."""
        pass


class WorkflowMigrationPlanner(abc.ABC):
    """Assembles migration plans and rollbacks checklists."""

    @abc.abstractmethod
    def create_migration_plan(
        self, from_ver: WorkflowVersion, to_ver: WorkflowVersion
    ) -> WorkflowEvolutionPlan:
        """Returns upgrade migration plan."""
        pass

    @abc.abstractmethod
    def create_rollback_plan(
        self, from_ver: WorkflowVersion, target_ver: WorkflowVersion
    ) -> WorkflowRollbackPlan:
        """Returns target rollback path checklist plan."""
        pass


class WorkflowVersionValidator(abc.ABC):
    """Validates parameters, author definitions, and version formats."""

    @abc.abstractmethod
    def validate_version(self, version: WorkflowVersion) -> List[str]:
        """Validates formatting and references validations."""
        pass


class WorkflowVersionService(ServiceLifecycle, abc.ABC):
    """Orchestrates workflows version registry, diff executions, and migration plans."""

    @abc.abstractmethod
    def create_version(
        self, workflow_id: str, author: str, semver: str, description: str, ir_json: str
    ) -> WorkflowVersion:
        """Registers a new workflow version node."""
        pass

    @abc.abstractmethod
    def get_history(self, workflow_id: str) -> WorkflowVersionHistory:
        """Retrieves chronological run history timeline."""
        pass

    @abc.abstractmethod
    def diff_versions(self, from_version_id: str, to_version_id: str) -> WorkflowVersionDiff:
        """Generates immutable difference between two version nodes."""
        pass

    @abc.abstractmethod
    def generate_evolution_plan(
        self, workflow_id: str, target_semver: str
    ) -> WorkflowEvolutionPlan:
        """Compiles upgrade migration steps."""
        pass

    @abc.abstractmethod
    def generate_rollback_plan(
        self, workflow_id: str, target_version_id: str
    ) -> WorkflowRollbackPlan:
        """Compiles target rollback target checklist."""
        pass

    @abc.abstractmethod
    def generate_version_report(self, workspace_id: str) -> WorkflowVersionReport:
        """Assembles workspace versioning summary report."""
        pass

    @abc.abstractmethod
    def store_version_summary(self, workspace_id: str) -> None:
        """Saves metadata summaries inside memory. Never stores source code/credentials."""
        pass

    @abc.abstractmethod
    def publish_version_report(self, report: WorkflowVersionReport) -> None:
        """Synchronizes report details to Notion on-demand."""
        pass

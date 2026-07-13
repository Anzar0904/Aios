import abc
from dataclasses import dataclass, field
from typing import Dict, List

from aios.services.base import ServiceLifecycle
from aios.services.workspace_intelligence import CodeStructureSummary


@dataclass
class ImpactNode:
    """Represents a codebase node within an impact map graph."""

    __test__ = False
    node_id: str
    file_path: str
    node_type: str  # "file", "symbol", "module"
    is_modified: bool


@dataclass
class ImpactEdge:
    """Represents dependency/call relationships between impact nodes."""

    __test__ = False
    source: str
    target: str
    relation: str  # "imports", "calls", "inherits"


@dataclass
class ImpactGraph:
    """Consolidated graph structure representing codebase changes propagation paths."""

    __test__ = False
    nodes: Dict[str, ImpactNode] = field(default_factory=dict)
    edges: List[ImpactEdge] = field(default_factory=list)


@dataclass
class AffectedComponent:
    """Represents a component impacted directly or indirectly by modifications."""

    __test__ = False
    name: str
    file_path: str
    direct_impact: bool
    reason: str


@dataclass
class AffectedTestSuite:
    """Represents an existing test suite impacted by codebase changes."""

    __test__ = False
    suite_name: str
    run_required: bool
    priority: str  # "High", "Medium", "Low"
    reason: str


@dataclass
class RegressionCandidate:
    """Represents a codebase module prone to regressions."""

    __test__ = False
    file_path: str
    reason: str
    coupling_density: int


@dataclass
class RiskAssessment:
    """Assesses change risk ratings across architectural borders."""

    __test__ = False
    overall_risk: str  # "Low", "Medium", "High", "Critical"
    api_break_risk: str
    shared_lib_risk: str
    dep_chain_risk: str
    config_risk: str
    data_model_risk: str


@dataclass
class CoverageTarget:
    """Testing coverage goal for a specific file target."""

    __test__ = False
    file_path: str
    statement_coverage: float
    branch_coverage: float


@dataclass
class ImpactAnalysisResult:
    """Final outcome bundle of a change impact analyzer execution."""

    __test__ = False
    analysis_id: str
    workspace_id: str
    impact_graph: ImpactGraph
    affected_components: List[AffectedComponent]
    affected_suites: List[AffectedTestSuite]
    regression_candidates: List[RegressionCandidate]
    risk_assessment: RiskAssessment
    coverage_targets: List[CoverageTarget]
    timestamp: float


class ChangeImpactAnalyzer(ServiceLifecycle, abc.ABC):
    """Primary service coordinating testing impact calculations, memory persistency, and syncing."""

    __test__ = False

    @abc.abstractmethod
    def analyze_change_impact(
        self,
        workspace_id: str,
        objective: str,
        affected_files: List[str],
        code_summary: CodeStructureSummary,
    ) -> ImpactAnalysisResult:
        """Determines impacted interfaces, database nodes, regression risks, and coverage targets."""
        pass

    @abc.abstractmethod
    def store_impact_result(self, result: ImpactAnalysisResult) -> None:
        """Stores change impact summaries inside Memory."""
        pass

    @abc.abstractmethod
    def publish_impact_report(self, result: ImpactAnalysisResult) -> None:
        """Syncs change impact report with the Knowledge Hub."""
        pass

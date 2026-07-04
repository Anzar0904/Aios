import abc
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from aios.services.base import ServiceLifecycle
from aios.services.test_impact import CoverageTarget, RegressionCandidate
from aios.services.test_execution import ExecutionSummary


@dataclass
class CoverageMetrics:
    """Consolidates coverage percentage stats across scopes."""
    __test__ = False
    statement_coverage: float
    branch_coverage: float
    function_coverage: float
    class_coverage: float
    module_coverage: float
    interface_coverage: float
    configuration_coverage: float


@dataclass
class CoveragePolicy:
    """Enforces target threshold policy mappings."""
    __test__ = False
    policy_id: str
    min_statement_coverage: float
    min_branch_coverage: float


@dataclass
class CoverageSummary:
    """Aggregates coverage metrics summaries."""
    __test__ = False
    summary_id: str
    workspace_id: str
    overall_coverage_pct: float
    metrics: CoverageMetrics
    timestamp: float


@dataclass
class CoverageReport:
    """Assembled report tracking coverage results and policies."""
    __test__ = False
    report_id: str
    workspace_id: str
    targets: List[CoverageTarget]
    summary: CoverageSummary
    policy: CoveragePolicy
    timestamp: float


@dataclass
class RegressionRisk:
    """Details identified regression probability metrics."""
    __test__ = False
    risk_level: str  # "Low", "Medium", "High", "Critical"
    regression_probability: float
    shared_dependency_risks: List[str]
    critical_execution_paths: List[str]
    regression_candidates: List[RegressionCandidate] = field(default_factory=list)


@dataclass
class ValidationGap:
    """Highlights validation omissions or insufficient test coverages."""
    __test__ = False
    gap_id: str
    gap_type: str  # "missing_tests", "low_coverage", "untested_api"
    description: str
    file_path: str
    recommendation: str


class CoverageAnalyzer(abc.ABC):
    """Calculates coverage parameters and flags validation gaps."""
    __test__ = False

    @abc.abstractmethod
    def analyze_coverage(
        self,
        execution_summary: ExecutionSummary,
        targets: List[CoverageTarget],
        policy: CoveragePolicy
    ) -> CoverageReport:
        """Determines statement and branch coverages against target policies."""
        pass


class RegressionAnalyzer(abc.ABC):
    """Analyzes execution metrics and dependency graphs to isolate regression risks."""
    __test__ = False

    @abc.abstractmethod
    def analyze_regression_risks(
        self,
        affected_files: List[str],
        dependency_graph: Dict[str, List[str]],
        execution_summary: ExecutionSummary
    ) -> RegressionRisk:
        """Computes regression probability index."""
        pass


class AITestCoverageService(ServiceLifecycle, abc.ABC):
    """Coordinating service mapping coverage outputs, logging telemetry, and reporting gaps."""
    __test__ = False

    @abc.abstractmethod
    def evaluate_validation(
        self,
        workspace_id: str,
        execution_summary: ExecutionSummary,
        affected_files: List[str],
        dependency_graph: Dict[str, List[str]],
        policy: CoveragePolicy
    ) -> Dict[str, Any]:
        """Runs overall coverage & regression analysis validation checks."""
        pass

    @abc.abstractmethod
    def store_coverage_summary(self, report: CoverageReport) -> None:
        """Saves coverage and regression summaries inside Memory."""
        pass

    @abc.abstractmethod
    def publish_coverage_report(self, report: CoverageReport) -> None:
        """Syncs coverage and regression report with Knowledge Hub."""
        pass

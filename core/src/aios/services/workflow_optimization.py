import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from aios.services.base import ServiceLifecycle


class WorkflowOptimizationCategory(str, Enum):
    """Extensible optimization categories."""
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    COST = "cost"
    MAINTAINABILITY = "maintainability"
    PARALLELIZATION = "parallelization"
    CACHING = "caching"
    REDUNDANCY = "redundancy"
    SCHEDULING = "scheduling"
    RETRIES = "retries"
    TIMEOUTS = "timeouts"
    RESOURCE_USAGE = "resource_usage"
    SIMPLIFICATION = "simplification"


class WorkflowOptimizationImpact(str, Enum):
    """Impact tier levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class WorkflowOptimizationRecommendation:
    """Detailed recommendation payload describing optimization actions."""
    recommendation_id: str
    category: WorkflowOptimizationCategory
    priority: str  # "high", "medium", "low"
    expected_impact: WorkflowOptimizationImpact
    confidence: float  # 0.0 to 1.0
    reasoning: str
    supporting_evidence: str
    affected_nodes: List[str]
    estimated_benefit: str
    implementation_difficulty: str  # "easy", "medium", "hard"


@dataclass
class WorkflowOptimizationPlan:
    """Plan container organizing all recommended changes for a specific workflow."""
    plan_id: str
    workflow_id: str
    recommendations: List[WorkflowOptimizationRecommendation] = field(default_factory=list)
    score_before: float = 100.0
    score_after: float = 100.0
    estimated_time_savings_seconds: float = 0.0
    estimated_cost_savings_dollars: float = 0.0


@dataclass
class WorkflowOptimizationReport:
    """Consolidated optimization summary report for Notion syncing or workspace writing."""
    report_id: str
    workspace_id: str
    plans: Dict[str, WorkflowOptimizationPlan] = field(default_factory=dict)
    optimization_score: float = 100.0
    total_time_savings_seconds: float = 0.0
    total_cost_savings_dollars: float = 0.0
    timestamp: float = 0.0


class WorkflowCostAnalyzer(abc.ABC):
    """Analyzes execution logs to trim cloud resource or token costs."""

    @abc.abstractmethod
    def analyze_cost(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]:
        """Runs cost analysis checks."""
        pass


class WorkflowLatencyAnalyzer(abc.ABC):
    """Analyzes execution pathways to detect latency bottlenecks."""

    @abc.abstractmethod
    def analyze_latency(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]:
        """Runs latency bottlenecks analyses."""
        pass


class WorkflowParallelizationAnalyzer(abc.ABC):
    """Identifies independent branches suitable for concurrent execution."""

    @abc.abstractmethod
    def analyze_parallelization(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]:
        """Identifies parallelization branches opportunities."""
        pass


class WorkflowRedundancyAnalyzer(abc.ABC):
    """Finds duplicate nodes or redundant tasks."""

    @abc.abstractmethod
    def analyze_redundancy(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]:
        """Scans for duplicated actions or branches."""
        pass


class WorkflowResourceAnalyzer(abc.ABC):
    """Trims high-CPU or excessive-memory nodes."""

    @abc.abstractmethod
    def analyze_resources(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]:
        """Scans cpu and memory usage boundaries."""
        pass


class WorkflowOptimizationValidator(abc.ABC):
    """Validates confidence ranges, evidence completeness, and recommendation consistency."""

    @abc.abstractmethod
    def validate_plan(self, plan: WorkflowOptimizationPlan) -> List[str]:
        """Validates duplicate rules and confidence bounds."""
        pass


class WorkflowOptimizationAnalyzer(abc.ABC):
    """Coordinating analyzer generating optimization plans."""

    @abc.abstractmethod
    def generate_plan(self, workflow_id: str, workflow_graph: Any, telemetry: List[Any]) -> WorkflowOptimizationPlan:
        """Assembles analyzers recommendations into a plan."""
        pass


class WorkflowOptimizationService(ServiceLifecycle, abc.ABC):
    """Central conductor interface executing optimizations audits, caching summaries, and publishing reports."""

    @abc.abstractmethod
    def generate_optimization_report(self, workspace_id: str) -> WorkflowOptimizationReport:
        """Assembles optimization report for a workspace."""
        pass

    @abc.abstractmethod
    def get_latest_report(self, workspace_id: str) -> Optional[WorkflowOptimizationReport]:
        """Retrieves the latest generated report."""
        pass

    @abc.abstractmethod
    def get_history(self, workspace_id: str) -> List[WorkflowOptimizationReport]:
        """Retrieves completed reports history."""
        pass

    @abc.abstractmethod
    def store_optimization_summary(self, workspace_id: str) -> None:
        """Saves metadata summaries inside memory. Never stores source code/credentials."""
        pass

    @abc.abstractmethod
    def publish_optimization_report(self, report: WorkflowOptimizationReport) -> None:
        """Synchronizes report details to Notion on-demand."""
        pass

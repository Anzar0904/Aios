import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle


class WorkflowOptimizationCategory(str, Enum):
    """Optimization category tags."""
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
    COMPLEXITY = "complexity"
    SIMPLIFICATION = "simplification"
    FUTURE_SCALABILITY = "future_scalability"


class WorkflowOptimizationPriority(str, Enum):
    """Priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class WorkflowOptimizationImpact(str, Enum):
    """Impact levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class WorkflowOptimizationPattern:
    """Pre-defined knowledge pattern definition."""
    pattern_id: str
    name: str
    description: str


@dataclass
class WorkflowOptimizationRecommendation:
    """Detailed recommendation details."""
    recommendation_id: str
    category: WorkflowOptimizationCategory
    priority: WorkflowOptimizationPriority
    expected_impact: WorkflowOptimizationImpact
    confidence: float  # 0.0 to 1.0
    reasoning: str
    supporting_evidence: str
    affected_nodes: List[str]
    affected_branches: List[str]
    expected_time_savings_seconds: float
    expected_cost_savings_dollars: float
    estimated_risk: float  # 0.0 to 1.0
    implementation_difficulty: str  # "easy", "medium", "hard"
    rollback_considerations: str
    pattern_ids: List[str] = field(default_factory=list)


@dataclass
class WorkflowOptimizationPlan:
    """Immutable optimization plan container."""
    plan_id: str
    workflow_id: str
    recommendations: List[WorkflowOptimizationRecommendation] = field(default_factory=list)
    score_before: float = 100.0
    score_after: float = 100.0
    estimated_time_savings_seconds: float = 0.0
    estimated_cost_savings_dollars: float = 0.0
    complexity_score_before: float = 50.0
    complexity_score_after: float = 50.0
    maintainability_score: float = 100.0
    reliability_score: float = 100.0
    performance_score: float = 100.0
    resource_efficiency_score: float = 100.0
    overall_automation_quality_score: float = 100.0


@dataclass
class WorkflowOptimizationReport:
    """Immutable optimization report output containing all generated plans."""
    report_id: str
    workspace_id: str
    plans: Dict[str, WorkflowOptimizationPlan] = field(default_factory=dict)
    optimization_score: float = 100.0
    total_time_savings_seconds: float = 0.0
    total_cost_savings_dollars: float = 0.0
    timestamp: float = 0.0


class WorkflowOptimizationKnowledgeBase:
    """Catalog of pre-defined reusable optimization patterns."""

    def __init__(self) -> None:
        self._patterns: Dict[str, WorkflowOptimizationPattern] = {}
        self._bootstrap_patterns()

    def _bootstrap_patterns(self) -> None:
        patterns_list = [
            WorkflowOptimizationPattern("duplicate_http_requests", "Duplicate HTTP Requests", "Repeated REST calls fetching identical endpoints."),
            WorkflowOptimizationPattern("duplicate_nodes", "Duplicate Nodes", "Identical node types with matching arguments mapped inside the graph."),
            WorkflowOptimizationPattern("unused_branches", "Unused Branches", "Conditional branches never navigated during execution runs."),
            WorkflowOptimizationPattern("dead_nodes", "Dead Nodes", "Unreachable nodes that do not connect to triggers or targets."),
            WorkflowOptimizationPattern("sequential_independent_tasks", "Sequential Independent Tasks", "Independent tasks executing sequentially instead of concurrently."),
            WorkflowOptimizationPattern("long_critical_path", "Long Critical Path", "Long sequencing chains raising duration bottlenecks."),
            WorkflowOptimizationPattern("high_retry_count", "High Retry Count", "Excessive retry loops causing long timeouts."),
            WorkflowOptimizationPattern("excessive_timeout", "Excessive Timeout", "Timeouts thresholds configured too high for simple REST queries."),
            WorkflowOptimizationPattern("missing_cache", "Missing Cache", "Missing caching for static/slow external data."),
            WorkflowOptimizationPattern("expensive_trigger", "Expensive Trigger", "High polling frequencies raising compute overheads."),
            WorkflowOptimizationPattern("oversized_workflow", "Oversized Workflow", "Workflow mapping too many task operations under a single definition."),
            WorkflowOptimizationPattern("duplicate_conditions", "Duplicate Conditions", "Repeated conditional evaluations along branches."),
            WorkflowOptimizationPattern("resource_bottleneck", "Resource Bottleneck", "Excessive peak memory or CPU usage spikes."),
            WorkflowOptimizationPattern("repeated_failures", "Repeated Failures", "High recurring failures rates with identical error logs."),
            WorkflowOptimizationPattern("ineefficient_scheduling", "Ineefficient Scheduling", "Suboptimal cron timings raising collision risks."),
            WorkflowOptimizationPattern("large_fan_out", "Large Fan-Out", "Single nodes triggering excessive parallel runs."),
            WorkflowOptimizationPattern("large_fan_in", "Large Fan-In", "Excessive branches joining back to a single barrier node."),
            WorkflowOptimizationPattern("repeated_external_calls", "Repeated External Calls", "Duplicate outbound requests to external APIs.")
        ]
        for p in patterns_list:
            self._patterns[p.pattern_id] = p

    def get_pattern(self, pattern_id: str) -> Optional[WorkflowOptimizationPattern]:
        """Retrieves pattern metadata by ID."""
        return self._patterns.get(pattern_id)

    def get_all_patterns(self) -> List[WorkflowOptimizationPattern]:
        """Lists all registered patterns."""
        return list(self._patterns.values())


class WorkflowCostAnalyzer(abc.ABC):
    """Trims token/API billing bounds."""

    @abc.abstractmethod
    def analyze_cost(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]:
        pass


class WorkflowLatencyAnalyzer(abc.ABC):
    """Trims runtime latency path bottlenecks."""

    @abc.abstractmethod
    def analyze_latency(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]:
        pass


class WorkflowParallelizationAnalyzer(abc.ABC):
    """Suggests concurrent executions on independent branches."""

    @abc.abstractmethod
    def analyze_parallelization(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]:
        pass


class WorkflowRedundancyAnalyzer(abc.ABC):
    """Finds duplicate nodes/conditions."""

    @abc.abstractmethod
    def analyze_redundancy(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]:
        pass


class WorkflowSchedulingAnalyzer(abc.ABC):
    """Optimizes cron schedulers intervals."""

    @abc.abstractmethod
    def analyze_scheduling(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]:
        pass


class WorkflowResourceAnalyzer(abc.ABC):
    """Trims memory/CPU usage spikes."""

    @abc.abstractmethod
    def analyze_resources(self, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]:
        pass


class WorkflowComplexityAnalyzer(abc.ABC):
    """Measures graph complexity and maintains metric scores."""

    @abc.abstractmethod
    def analyze_complexity(self, workflow_graph: Any) -> Dict[str, float]:
        pass


class WorkflowOptimizationValidator(abc.ABC):
    """Validates plan integrity constraints, confidence bounds, and patterns references."""

    @abc.abstractmethod
    def validate_plan(self, plan: WorkflowOptimizationPlan) -> List[str]:
        pass


class WorkflowOptimizationAnalyzer(abc.ABC):
    """Analyzes telemetry and graphs using sub-analyzers."""

    @abc.abstractmethod
    def run_analysis(self, workflow_id: str, workflow_graph: Any, telemetry: List[Any]) -> List[WorkflowOptimizationRecommendation]:
        pass


class WorkflowOptimizationPlanner(abc.ABC):
    """Central planner coordinating sub-analyzers to construct plans."""

    @abc.abstractmethod
    def construct_optimization_plan(self, workflow_id: str, workflow_graph: Any, telemetry: List[Any]) -> WorkflowOptimizationPlan:
        pass


class WorkflowOptimizationService(ServiceLifecycle, abc.ABC):
    """Conductor orchestration optimizing workflows, writing reports, and syncing databases."""

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

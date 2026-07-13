import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List

from aios.services.base import ServiceLifecycle
from aios.services.workspace_intelligence import CodeStructureSummary


@dataclass
class AffectedFile:
    """Represents a source file likely to be affected by the engineering change."""
    file_path: str
    change_type: str  # "modify", "create", "delete", "refactor"
    reason: str
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AffectedComponent:
    """Represents an architectural component/symbol affected by the change."""
    name: str
    component_type: str  # "class", "method", "function", "interface", "enum", "module"
    impact_level: str  # "Low", "Medium", "High", "Critical"
    description: str
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChangeRecommendation:
    """A recommended structural modification for a specific target."""
    target: str
    recommendation: str
    rationale: str
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineeringPlan:
    """Structured implementation plan generated for a software change objective."""
    plan_id: str
    objective: str
    timestamp: float
    ordered_steps: List[Dict[str, Any]]
    dependencies: Dict[str, List[str]]
    required_services: List[str]
    risks: List[str]
    complexity: str  # "Low", "Medium", "High", "Very High"
    estimated_effort_hours: float
    validation_strategy: str
    recommended_execution_order: List[str]
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineeringReport:
    """Full engineering analysis report including impact, complexity, risks, and plans."""
    report_id: str
    objective: str
    timestamp: float
    affected_files: List[AffectedFile]
    affected_components: List[AffectedComponent]
    recommendations: List[ChangeRecommendation]
    plan: EngineeringPlan
    meta: Dict[str, Any] = field(default_factory=dict)


class ChangeImpactAnalyzer(abc.ABC):
    """Responsible for determining affected modules, services, interfaces, files, and docs."""

    @abc.abstractmethod
    def analyze_impact(
        self,
        workspace_root: str,
        objective: str,
        code_summary: CodeStructureSummary
    ) -> tuple[List[AffectedFile], List[AffectedComponent]]:
        """Identifies files, classes, methods, and interfaces affected by the change objective."""
        pass


class ComplexityEstimator(abc.ABC):
    """Responsible for estimating implementation complexity and effort based on architectural impact."""

    @abc.abstractmethod
    def estimate_complexity(
        self,
        affected_files: List[AffectedFile],
        affected_components: List[AffectedComponent],
        code_summary: CodeStructureSummary
    ) -> tuple[str, float]:
        """Returns complexity classification (Low/Medium/High/Very High) and estimated effort in hours."""
        pass


class RiskAnalyzer(abc.ABC):
    """Responsible for identifying architectural risks (breaking APIs, circular deps, violations)."""

    @abc.abstractmethod
    def analyze_risks(
        self,
        objective: str,
        affected_files: List[AffectedFile],
        affected_components: List[AffectedComponent],
        code_summary: CodeStructureSummary
    ) -> List[str]:
        """Identifies risk indicators like high coupling, circular dependencies, and API breakages."""
        pass


class ImplementationPlanner(abc.ABC):
    """Responsible for generating step-by-step engineering plans, execution orders, and validation plans."""

    @abc.abstractmethod
    def generate_plan(
        self,
        objective: str,
        affected_files: List[AffectedFile],
        affected_components: List[AffectedComponent],
        complexity: str,
        risks: List[str],
        code_summary: CodeStructureSummary
    ) -> EngineeringPlan:
        """Constructs an ordered implementation plan with validation strategies and dependencies."""
        pass


class EngineeringAnalyzer(abc.ABC):
    """Unified coordinator component executing impact, complexity, risk, and plan assessments."""

    @abc.abstractmethod
    def analyze_engineering(self, workspace_root: str, objective: str) -> EngineeringReport:
        """Executes full analysis pipeline and generates a complete Engineering Report."""
        pass


class EngineeringIntelligenceService(ServiceLifecycle, abc.ABC):
    """Primary service interface exposing engineering analysis, storage, and publishing."""

    @abc.abstractmethod
    def generate_report(self, workspace_root: str, objective: str) -> EngineeringReport:
        """Analyzes a change objective and constructs a complete EngineeringReport."""
        pass

    @abc.abstractmethod
    def store_report(self, report: EngineeringReport) -> None:
        """Stores the engineering plan and summary inside Memory Intelligence."""
        pass

    @abc.abstractmethod
    def publish_report(self, report: EngineeringReport) -> None:
        """Publishes the engineering report to the Knowledge Hub."""
        pass

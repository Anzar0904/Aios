import abc
from dataclasses import dataclass
from enum import Enum
from typing import List

from aios.services.base import ServiceLifecycle
from aios.services.workspace_intelligence import CodeStructureSummary


class TestCategory(Enum):
    """Supported testing disciplines."""
    __test__ = False
    UNIT = "unit"
    INTEGRATION = "integration"
    REGRESSION = "regression"
    API = "api"
    DATABASE = "database"
    SECURITY = "security"
    PERFORMANCE = "performance"
    END_TO_END = "end_to_end"
    SMOKE = "smoke"
    SANITY = "sanity"
    STATIC_ANALYSIS = "static_analysis"
    STYLE_VALIDATION = "style_validation"


class TestPriority(Enum):
    """Gauges prioritization sequence weights."""
    __test__ = False
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TestStrategy(Enum):
    """Refers to validation depth bounds."""
    __test__ = False
    MINIMAL = "minimal"
    STANDARD = "standard"
    STRICT = "strict"
    MISSION_CRITICAL = "mission_critical"


@dataclass
class TestRequirement:
    """Requirement criteria for satisfying validation targets."""
    __test__ = False
    requirement_id: str
    description: str
    category: TestCategory
    priority: TestPriority


@dataclass
class TestTarget:
    """Specific code target (file path or symbol class/function)."""
    __test__ = False
    target_id: str
    file_path: str
    symbols: List[str]
    is_critical: bool


@dataclass
class TestScope:
    """Encloses target lists, goals, and risk levels."""
    __test__ = False
    targets: List[TestTarget]
    excluded_targets: List[str]
    coverage_goal: float
    risk_level: str  # "Low", "Medium", "High", "Critical"


@dataclass
class TestSuite:
    """Packaged collection of test definitions targeting specific modules."""
    __test__ = False
    suite_id: str
    name: str
    category: TestCategory
    target_files: List[str]
    estimated_execution_time: float


@dataclass
class TestPlan:
    """Complete testing plan specification."""
    __test__ = False
    plan_id: str
    objective: str
    strategy: TestStrategy
    scope: TestScope
    suites: List[TestSuite]
    requirements: List[TestRequirement]


@dataclass
class TestPlanningResult:
    """Ordered result sequence of test planner run."""
    __test__ = False
    result_id: str
    plan: TestPlan
    ordered_execution_sequence: List[str]
    validation_checkpoints: List[str]
    timestamp: float


class TestPlanner(abc.ABC):
    """Core logic engine mapping changes to testing strategies and prioritization queues."""
    __test__ = False

    @abc.abstractmethod
    def plan_tests(
        self,
        objective: str,
        affected_files: List[str],
        code_summary: CodeStructureSummary
    ) -> TestPlanningResult:
        """Determines strategies, scopes, suites, prioritization order, and estimated timelines."""
        pass


class AITestEngineerService(ServiceLifecycle, abc.ABC):
    """Central service managing test planning, memory storage, and reports syncing."""

    @abc.abstractmethod
    def generate_test_plan(
        self,
        workspace_id: str,
        objective: str,
        affected_files: List[str],
        code_summary: CodeStructureSummary
    ) -> TestPlanningResult:
        """Orchestrates test planning result generation."""
        pass

    @abc.abstractmethod
    def store_test_plan(self, result: TestPlanningResult) -> None:
        """Stores the testing plan summary inside Memory Intelligence."""
        pass

    @abc.abstractmethod
    def publish_test_plan(self, result: TestPlanningResult) -> None:
        """Syncs the testing plan report with the Knowledge Hub."""
        pass

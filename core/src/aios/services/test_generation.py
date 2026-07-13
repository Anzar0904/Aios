import abc
from dataclasses import dataclass
from typing import Any, Dict, List

from aios.services.base import ServiceLifecycle
from aios.services.workspace_intelligence import CodeStructureSummary


@dataclass
class GeneratedTestArtifact:
    """Represents a generated test file artifact target."""
    __test__ = False
    artifact_id: str
    file_path: str
    content: str
    checksum: str
    timestamp: float


@dataclass
class TestGenerationReport:
    """Final outcome report detailing generated test telemetry."""
    __test__ = False
    report_id: str
    workspace_id: str
    strategy: str
    artifacts: List[GeneratedTestArtifact]
    pattern_summary: str
    warnings: List[str]
    confidence_estimate: float
    timestamp: float


class TestPatternAnalyzer(abc.ABC):
    """Analyzes existing tests to identify naming, fixture, and assertion styles."""
    __test__ = False

    @abc.abstractmethod
    def analyze_patterns(self, existing_tests_dir: str) -> str:
        """Returns structured patterns description summary."""
        pass


class TestTemplateEngine(abc.ABC):
    """Renders test mock skeletons using style guides."""
    __test__ = False

    @abc.abstractmethod
    def render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Renders test code templates."""
        pass


class TestCaseBuilder(abc.ABC):
    """Structures test parameters, steps, and targets."""
    __test__ = False

    @abc.abstractmethod
    def build_cases(self, objective: str, patterns: str) -> List[Dict[str, Any]]:
        """Determines target cases to create."""
        pass


class AssertionGenerator(abc.ABC):
    """Generates standard target assertions."""
    __test__ = False

    @abc.abstractmethod
    def generate_assertions(self, target_symbol: str) -> List[str]:
        """Returns assert snippets."""
        pass


class FixtureGenerator(abc.ABC):
    """Generates testing fixtures mapping setups."""
    __test__ = False

    @abc.abstractmethod
    def generate_fixtures(self, target_symbol: str) -> List[str]:
        """Returns pytest fixtures declarations."""
        pass


class MockGenerator(abc.ABC):
    """Generates service mock parameters."""
    __test__ = False

    @abc.abstractmethod
    def generate_mocks(self, target_symbol: str) -> List[str]:
        """Returns mock definitions."""
        pass


class EdgeCaseGenerator(abc.ABC):
    """Generates exception boundaries and edge cases parameters."""
    __test__ = False

    @abc.abstractmethod
    def generate_edge_cases(self, target_symbol: str) -> List[str]:
        """Returns exception test blocks."""
        pass


class RegressionTestGenerator(abc.ABC):
    """Generates regression-specific test targets."""
    __test__ = False

    @abc.abstractmethod
    def generate_regression_tests(self, target_symbol: str) -> List[str]:
        """Returns regression validation snippets."""
        pass


class TestGenerator(abc.ABC):
    """Primary engine executing generation of single test files."""
    __test__ = False

    @abc.abstractmethod
    def generate_test_suite(
        self,
        workspace_root: str,
        target_file: str,
        patterns: str,
        code_summary: CodeStructureSummary
    ) -> GeneratedTestArtifact:
        """Writes and returns test target artifacts."""
        pass


class TestGenerationService(ServiceLifecycle, abc.ABC):
    """Coordinating service executing test planning, context generation, and reviews packaging."""
    __test__ = False

    @abc.abstractmethod
    def generate_workspace_tests(
        self,
        workspace_id: str,
        objective: str,
        workspace_root: str,
        target_files: List[str],
        code_summary: CodeStructureSummary
    ) -> TestGenerationReport:
        """Executes test generation pipeline using the ModelService."""
        pass

    @abc.abstractmethod
    def store_generation_report(self, report: TestGenerationReport) -> None:
        """Stores test generation report inside Memory."""
        pass

    @abc.abstractmethod
    def publish_generation_report(self, report: TestGenerationReport) -> None:
        """Syncs test generation report with the Knowledge Hub."""
        pass

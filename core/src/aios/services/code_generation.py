import abc
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List

from aios.services.base import ServiceLifecycle
from aios.services.model import LLMRequest
from aios.services.workspace_intelligence import CodeStructureSummary


class GenerationPolicy(Enum):
    """Policies dictating structural refactoring permissibility levels."""

    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"


@dataclass
class GeneratedArtifact:
    """Represents a generated code file artifact target."""

    artifact_id: str
    file_path: str
    content: str
    checksum: str
    timestamp: float


@dataclass
class GenerationReport:
    """Final code generation execution telemetry report."""

    report_id: str
    objective: str
    policy: GenerationPolicy
    artifacts: List[GeneratedArtifact]
    warnings: List[str]
    confidence_estimate: float
    execution_statistics: Dict[str, Any]
    validation_status: str  # "passed", "failed"
    timestamp: float


@dataclass
class GenerationSession:
    """Active code generation session lifecycle tracker."""

    session_id: str
    workspace_id: str
    policy: GenerationPolicy
    status: str
    created_at: float


class CodePlanner(abc.ABC):
    """Formulates multi-step generation execution schedules."""

    @abc.abstractmethod
    def plan_generation_steps(
        self, objective: str, policy: GenerationPolicy
    ) -> List[Dict[str, Any]]:
        """Determines ordered files target steps and actions."""
        pass


class ContextAssembler(abc.ABC):
    """Assembles minimalist relevant file context without bloated prompts."""

    @abc.abstractmethod
    def assemble_context(self, file_path: str, code_summary: CodeStructureSummary) -> str:
        """Aggregates direct imports, interfaces, and minimal code snippets."""
        pass


class PromptBuilder(abc.ABC):
    """Formats system instructions, metadata, and task scopes."""

    @abc.abstractmethod
    def build_prompt(
        self, objective: str, target_file: str, context: str, policy: GenerationPolicy
    ) -> LLMRequest:
        """Packages LLMRequest with category, priority, and JSON schemas."""
        pass


class FileGenerator(abc.ABC):
    """Handles file creations within the isolated sandboxes."""

    @abc.abstractmethod
    def create_file(self, workspace_root: str, file_path: str, content: str) -> GeneratedArtifact:
        """Writes new file to workspace directory."""
        pass


class FileEditor(abc.ABC):
    """Applies modifications, appends, and replacements inside sandboxes."""

    @abc.abstractmethod
    def edit_file(self, workspace_root: str, file_path: str, edits: str) -> GeneratedArtifact:
        """Modifies existing sandbox files."""
        pass


class SyntaxValidator(abc.ABC):
    """Runs compiler checks and ast validation (e.g. compile() in python)."""

    @abc.abstractmethod
    def validate_syntax(self, content: str, file_path: str) -> tuple[bool, str]:
        """Validates that syntax parses cleanly without syntax errors."""
        pass


class StyleValidator(abc.ABC):
    """Checks basic layout, spacing, and convention compliance."""

    @abc.abstractmethod
    def validate_style(self, content: str, file_path: str) -> tuple[bool, str]:
        """Validates standard rules formatting and conventions."""
        pass


class ImportValidator(abc.ABC):
    """Verifies referenced packages/modules exist in target workspace."""

    @abc.abstractmethod
    def validate_imports(
        self, content: str, file_path: str, code_summary: CodeStructureSummary
    ) -> tuple[bool, str]:
        """Verifies that imports align with code summary dependencies."""
        pass


class GenerationValidator(abc.ABC):
    """Orchestrates comprehensive validation pipelines."""

    @abc.abstractmethod
    def validate_artifact(
        self, artifact: GeneratedArtifact, code_summary: CodeStructureSummary
    ) -> tuple[bool, List[str]]:
        """Aggregates syntax, style, and import verifications."""
        pass


class CodeGenerationService(ServiceLifecycle, abc.ABC):
    """Coordinating service orchestrating code planning, generation sessions, and reviews."""

    @abc.abstractmethod
    def start_session(self, workspace_id: str, policy: GenerationPolicy) -> GenerationSession:
        """Starts a tracked generation session."""
        pass

    @abc.abstractmethod
    def generate_code(
        self,
        session: GenerationSession,
        target_file: str,
        objective: str,
        workspace_root: str,
        code_summary: CodeStructureSummary,
    ) -> GenerationReport:
        """Executes Code Generation workflow using the ModelService."""
        pass

    @abc.abstractmethod
    def store_generation_summary(self, report: GenerationReport) -> None:
        """Stores code generation session stats inside Memory."""
        pass

    @abc.abstractmethod
    def publish_generation_report(self, report: GenerationReport) -> None:
        """Syncs the code generation report with the Knowledge Hub."""
        pass

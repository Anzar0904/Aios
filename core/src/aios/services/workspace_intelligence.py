from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle


@dataclass
class RepositoryHealth:
    """Represents health metrics of the repository."""
    file_count: int
    folder_count: int
    test_count: int
    documentation_coverage: float  # Scale of 0.0 to 1.0
    adr_count: int
    readme_coverage: float  # Scale of 0.0 to 1.0
    config_completeness: float  # Scale of 0.0 to 1.0
    statistics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RepositorySummary:
    """Contains full high-level and detailed analysis of a code repository."""
    summary_id: str
    timestamp: float
    high_level_architecture: str
    components: List[str]
    dependencies: Dict[str, List[str]]
    service_graph: Dict[str, Any]
    entry_points: List[str]
    execution_paths: List[str]
    design_patterns: List[str]
    architectural_observations: List[str]
    languages: Dict[str, int]
    frameworks: List[str]
    package_managers: List[str]
    health: RepositoryHealth
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FileMetadata:
    """Represents indexed metadata for a project file."""
    file_path: str
    language: str
    module: str
    extension: str
    size: int
    purpose: str  # source, test, documentation, config, build, asset, other
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    relationships: Dict[str, List[str]] = field(default_factory=dict)  # {"imports": [...], "imported_by": [...]}
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkspaceContext:
    """Unified context object describing the technology stack and architecture of the workspace."""
    workspace_root: str
    technology_stack: Dict[str, Any]
    architecture: Dict[str, Any]
    dependencies: Dict[str, List[str]]
    project_type: str  # monorepo, single-package, etc.
    important_directories: List[str]
    coding_conventions: Dict[str, Any]
    workspaces: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class RepositoryAnalyzer(abc.ABC):
    """Component to inspect files, structures, configuration, CI/CD, and Docker files."""

    @abc.abstractmethod
    def analyze(self, workspace_root: str) -> Dict[str, Any]:
        """Scans the repository structure, config files, and build pipelines."""
        pass


class ArchitectureAnalyzer(abc.ABC):
    """Component to evaluate high-level layout, components, and execution paths."""

    @abc.abstractmethod
    def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, Any]:
        """Identifies architectural layout, key components, entrypoints, and observations."""
        pass


class DependencyAnalyzer(abc.ABC):
    """Component to map imports, packages, and dependency relations."""

    @abc.abstractmethod
    def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, List[str]]:
        """Extracts dependency relationships between components and modules."""
        pass


class TechnologyAnalyzer(abc.ABC):
    """Component to identify languages, databases, linters, frameworks, and deployment options."""

    @abc.abstractmethod
    def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, Any]:
        """Identifies frameworks, database adapters, test configurations, linters, and clouds."""
        pass


class DocumentationAnalyzer(abc.ABC):
    """Component to analyze documentation files, README completeness, and ADR counts."""

    @abc.abstractmethod
    def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, Any]:
        """Measures documentation coverage, ADR counts, and README files quality details."""
        pass


class WorkspaceIntelligenceService(ServiceLifecycle, abc.ABC):
    """Unified service representing primary repository analysis and project health verification."""

    @abc.abstractmethod
    def analyze_repository(self, workspace_root: str) -> RepositorySummary:
        """Executes full repository analyzers, maps dependencies, and generates summary metrics."""
        pass

    @abc.abstractmethod
    def store_summary_in_memory(self, summary: RepositorySummary) -> None:
        """Stores the structured summary and health metrics inside the memory service."""
        pass

    @abc.abstractmethod
    def publish_to_knowledge_hub(self, summary: RepositorySummary) -> None:
        """Publishes the repository summary report to the Knowledge Hub."""
        pass

    @abc.abstractmethod
    def get_workspace_context(self, workspace_root: str) -> WorkspaceContext:
        """Generates a Workspace Context object summarizing tech stack, architecture, etc."""
        pass

    @abc.abstractmethod
    def generate_markdown_reports(self, workspace_root: str, summary: RepositorySummary, code_summary: CodeStructureSummary) -> None:
        """Generates complete markdown reports under workspace docs directory."""
        pass



@dataclass
class SymbolReference:
    """Represents a code symbol (class, function, method, interface, enum) extracted via AST."""
    symbol_id: str
    name: str
    symbol_type: str  # class, function, method, interface, enum, module
    file_path: str
    start_line: int
    end_line: int
    dependencies: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    is_public: bool = True
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeStructureSummary:
    """Unified code structure representation containing symbol indexes and call/dependency graphs."""
    summary_id: str
    timestamp: float
    symbols: Dict[str, SymbolReference]
    call_graph: Dict[str, List[str]]
    dependency_graph: Dict[str, List[str]]
    inheritance_map: Dict[str, List[str]]
    public_apis: List[str]


class LanguageASTParser(abc.ABC):
    """Interface for language-specific AST parsers."""

    @abc.abstractmethod
    def can_parse(self, file_extension: str) -> bool:
        """Returns True if this parser can handle the given file extension."""
        pass

    @abc.abstractmethod
    def parse(self, file_path: str, content: str) -> List[SymbolReference]:
        """Parses the content of a source file and returns extracted symbols."""
        pass


class ASTAnalyzer(abc.ABC):
    """Component responsible for parsing source code into syntax symbols."""

    @abc.abstractmethod
    def parse_file(self, file_path: str, content: str) -> List[SymbolReference]:
        """Parses source file content into a list of syntax symbols."""
        pass



class SymbolIndexer(abc.ABC):
    """Component maintaining code symbols lookup maps."""

    @abc.abstractmethod
    def index_symbols(self, symbols: List[SymbolReference]) -> None:
        """Indexes symbols for fast lookup."""
        pass

    @abc.abstractmethod
    def lookup_symbol(self, name: str) -> Optional[SymbolReference]:
        """Looks up a symbol by its name."""
        pass

    @abc.abstractmethod
    def list_symbols(self) -> List[SymbolReference]:
        """Returns all indexed symbols."""
        pass


class DependencyGraphBuilder(abc.ABC):
    """Component constructing module import and inheritance graphs."""

    @abc.abstractmethod
    def build_graph(self, file_paths: List[str], symbols: List[SymbolReference]) -> Dict[str, List[str]]:
        """Maps imports and module-level dependency relationships."""
        pass


class CallGraphBuilder(abc.ABC):
    """Component constructing function call dependency graphs."""

    @abc.abstractmethod
    def build_call_graph(self, symbols: List[SymbolReference]) -> Dict[str, List[str]]:
        """Builds a map representing function call references."""
        pass


class CodeIntelligenceService(ServiceLifecycle, abc.ABC):
    """Unified service representing code-level understanding and AST analyses."""

    @abc.abstractmethod
    def analyze_codebase(self, workspace_root: str) -> CodeStructureSummary:
        """Triggers complete source files AST parsing and graph builders."""
        pass

    @abc.abstractmethod
    def store_code_summary(self, summary: CodeStructureSummary) -> None:
        """Stores structural summaries inside Memory Intelligence without saving source content."""
        pass

    @abc.abstractmethod
    def publish_code_report(self, summary: CodeStructureSummary) -> None:
        """Publishes the code structure summary report to the Knowledge Hub."""
        pass

    @abc.abstractmethod
    def get_file_metadata(self, file_path: str) -> Optional[FileMetadata]:
        """Retrieves metadata for a specific indexed file."""
        pass

    @abc.abstractmethod
    def list_all_files_metadata(self) -> List[FileMetadata]:
        """Lists metadata for all indexed files in the workspace."""
        pass



import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from aios.services.base import ServiceLifecycle
from aios.services.model import LLMRequest, ModelService
from aios.services.project_intelligence import ProjectIntelligenceService, ProjectContext
from aios.services.memory import MemoryService, MemoryType, MemoryMetadata
from aios.services.knowledge_hub import KnowledgeHubService, KnowledgeDocument, KnowledgeMetadata as KHMetadata
from aios.services.workspace_intelligence import (
    RepositoryHealth,
    RepositorySummary,
    RepositoryAnalyzer,
    ArchitectureAnalyzer,
    DependencyAnalyzer,
    TechnologyAnalyzer,
    DocumentationAnalyzer,
    WorkspaceIntelligenceService,
)

logger = logging.getLogger(__name__)


class LocalRepositoryAnalyzer(RepositoryAnalyzer):
    def __init__(self, project_intel: ProjectIntelligenceService) -> None:
        self._project_intel = project_intel

    def analyze(self, workspace_root: str) -> Dict[str, Any]:
        context: ProjectContext = self._project_intel.analyze_workspace(workspace_root)

        root_path = Path(workspace_root)
        cicd_workflows = []
        workflows_dir = root_path / ".github" / "workflows"
        if workflows_dir.is_dir():
            try:
                cicd_workflows = [f.name for f in workflows_dir.iterdir() if f.is_file()]
            except Exception:
                pass

        has_docker = (root_path / "Dockerfile").is_file() or (root_path / "docker-compose.yml").is_file()

        env_files = []
        try:
            env_files = [f.name for f in root_path.iterdir() if f.is_file() and f.name.startswith(".env")]
        except Exception:
            pass

        return {
            "context": context,
            "cicd_workflows": cicd_workflows,
            "has_docker": has_docker,
            "env_files": env_files,
        }


class LocalArchitectureAnalyzer(ArchitectureAnalyzer):
    def __init__(self, model_service: Optional[ModelService] = None) -> None:
        self._model = model_service

    def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, Any]:
        context: ProjectContext = project_context["context"]
        files = context.structure[:50]
        folders_count = context.statistics.get("total_folders", 0)
        languages = context.languages

        if self._model:
            try:
                prompt = (
                    "You are the Lead Systems Architect for Personal AI OS.\n"
                    f"Analyze the following repository structure and file details:\n"
                    f"Files: {files}\n"
                    f"Folders count: {folders_count}\n"
                    f"Languages: {languages}\n\n"
                    "Produce a JSON object (pure JSON, no markdown formatting) with keys:\n"
                    "- high_level_architecture: overview description of the architectural layout\n"
                    "- components: list of key service/module names\n"
                    "- entry_points: list of main execution entry files\n"
                    "- execution_paths: list of major sequence execution paths\n"
                    "- design_patterns: list of patterns detected (e.g. Singleton, Dependency Injection)\n"
                    "- architectural_observations: list of key architectural observations/details"
                )
                res = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output pure JSON only.",
                        task_category="architecture",
                        preferences={"JSON_output": True},
                    )
                )
                content = res.content.strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                return json.loads(content)
            except Exception as e:
                logger.debug(f"LLM architectural analysis failed: {e}. Falling back to rules.")

        # Fallback
        components = ["Kernel", "Orchestrator", "ServiceRegistry", "MemoryService", "ReasoningService", "IntentEngine"]
        if "package.json" in str(files) or "npm/yarn" in context.package_managers:
            components.append("WebFrontEnd")

        design_patterns = ["Dependency Injection", "Singleton (ServiceRegistry)", "Composition Root", "Lifecycle Hooks"]
        observations = [
            "Modular services decouple implementation details from abstraction interfaces.",
            "Strict clean architecture boundaries are maintained in core directories."
        ]

        return {
            "high_level_architecture": "Clean Architecture implementation with segregated domains and dynamic service lookup registries.",
            "components": components,
            "entry_points": ["core/src/aios/bootstrap.py", "core/src/aios/kernel.py"],
            "execution_paths": ["Bootstrapping -> Kernel run -> Intent classification -> Reasoning Plan -> Execution"],
            "design_patterns": design_patterns,
            "architectural_observations": observations,
        }


class LocalDependencyAnalyzer(DependencyAnalyzer):
    def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, List[str]]:
        context: ProjectContext = project_context["context"]
        deps = context.dependencies

        relations = {}
        for dep in deps:
            relations[dep] = []

        # Add default core service dependency relationships
        relations["Kernel"] = ["ServiceRegistry", "bootstrap"]
        relations["Orchestrator"] = ["CommandRegistry"]
        relations["DailyOSService"] = ["CareerOSService", "GitHubService"]
        relations["IntentEngine"] = ["MemoryService", "ReasoningService"]
        return relations


class LocalTechnologyAnalyzer(TechnologyAnalyzer):
    def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, Any]:
        context: ProjectContext = project_context["context"]
        exts = context.languages.keys()

        languages = []
        if ".py" in exts:
            languages.append("Python")
        if ".js" in exts or ".ts" in exts:
            languages.append("JavaScript/TypeScript")
        if ".go" in exts:
            languages.append("Go")
        if ".rs" in exts:
            languages.append("Rust")

        frameworks = context.frameworks
        package_managers = context.package_managers

        testing_frameworks = []
        linters = []
        databases = []
        clouds = ["AWS/GCP/Mock"]

        all_deps = set(context.dependencies)
        if "pytest" in all_deps or any("test" in f for f in context.structure):
            testing_frameworks.append("pytest")
        if "ruff" in all_deps:
            linters.append("ruff")
        if "eslint" in all_deps:
            linters.append("eslint")
        if "sqlite3" in all_deps or "postgresql" in all_deps:
            databases.append("Relational Database")

        return {
            "languages": languages,
            "frameworks": frameworks,
            "package_managers": package_managers,
            "testing_frameworks": testing_frameworks,
            "linters": linters,
            "databases": databases,
            "clouds": clouds,
        }


class LocalDocumentationAnalyzer(DocumentationAnalyzer):
    def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, Any]:
        context: ProjectContext = project_context["context"]
        files = context.structure

        doc_files = [f for f in files if f.startswith("docs/") or f.endswith(".md") or f.endswith(".txt")]
        readme_files = [f for f in files if "README" in f.upper()]
        adr_count = context.adr_count

        doc_coverage = min(1.0, len(doc_files) / max(1, len(files) * 0.1))
        readme_coverage = min(1.0, len(readme_files) / 2.0)

        return {
            "doc_files_count": len(doc_files),
            "readme_files_count": len(readme_files),
            "doc_coverage": doc_coverage,
            "readme_coverage": readme_coverage,
            "adr_count": adr_count,
        }


class LocalWorkspaceIntelligenceService(WorkspaceIntelligenceService):
    def __init__(
        self,
        project_intel: ProjectIntelligenceService,
        memory_service: MemoryService,
        knowledge_hub: Optional[KnowledgeHubService] = None,
        model_service: Optional[ModelService] = None,
        registry: Optional[Any] = None,
    ) -> None:
        self._project_intel = project_intel
        self._memory = memory_service
        self._knowledge_hub = knowledge_hub
        self._model = model_service
        self._registry = registry

        self._analyzer = LocalRepositoryAnalyzer(project_intel)
        self._arch_analyzer = LocalArchitectureAnalyzer(model_service)
        self._dep_analyzer = LocalDependencyAnalyzer()
        self._tech_analyzer = LocalTechnologyAnalyzer()
        self._doc_analyzer = LocalDocumentationAnalyzer()

    def initialize(self) -> None:
        logger.info("Initializing LocalWorkspaceIntelligenceService")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def analyze_repository(self, workspace_root: str) -> RepositorySummary:
        logger.info(f"Workspace Intelligence analyzing repository at: '{workspace_root}'")

        repo_data = self._analyzer.analyze(workspace_root)
        arch_data = self._arch_analyzer.analyze(workspace_root, repo_data)
        dep_data = self._dep_analyzer.analyze(workspace_root, repo_data)
        tech_data = self._tech_analyzer.analyze(workspace_root, repo_data)
        doc_data = self._doc_analyzer.analyze(workspace_root, repo_data)

        context: ProjectContext = repo_data["context"]
        total_files = context.statistics.get("total_files", 0)
        total_folders = context.statistics.get("total_folders", 0)

        test_count = len([f for f in context.structure if "test_" in f or "_test" in f])
        config_files_count = len([f for f in context.structure if f.endswith(".json") or f.endswith(".toml") or f.endswith(".yaml") or f.endswith(".yml")])
        config_completeness = min(1.0, config_files_count / 10.0)

        health = RepositoryHealth(
            file_count=total_files,
            folder_count=total_folders,
            test_count=test_count,
            documentation_coverage=doc_data["doc_coverage"],
            adr_count=doc_data["adr_count"],
            readme_coverage=doc_data["readme_coverage"],
            config_completeness=config_completeness,
            statistics=context.statistics,
        )

        summary = RepositorySummary(
            summary_id=f"repo_summary_{int(time.time())}",
            timestamp=time.time(),
            high_level_architecture=arch_data["high_level_architecture"],
            components=arch_data["components"],
            dependencies=dep_data,
            service_graph={"nodes": arch_data["components"], "edges": []},
            entry_points=arch_data["entry_points"],
            execution_paths=arch_data["execution_paths"],
            design_patterns=arch_data["design_patterns"],
            architectural_observations=arch_data["architectural_observations"],
            languages=context.languages,
            frameworks=tech_data["frameworks"],
            package_managers=tech_data["package_managers"],
            health=health,
            metadata={
                "has_docker": repo_data["has_docker"],
                "env_files": repo_data["env_files"],
                "cicd_workflows": repo_data["cicd_workflows"],
            }
        )

        return summary

    def store_summary_in_memory(self, summary: RepositorySummary) -> None:
        summary_content = (
            f"Repository Architecture Summary:\n"
            f"Architecture: {summary.high_level_architecture}\n"
            f"Components: {summary.components}\n"
            f"Design Patterns: {summary.design_patterns}\n"
            f"Health stats: files={summary.health.file_count}, folders={summary.health.folder_count}"
        )
        self._memory.add_memory(
            content=summary_content,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id="default_workspace",
                session_id="workspace_intelligence_session",
                tags=["repository_summary", "architecture_summary"],
                importance=2,
                source_subsystem="workspace_intelligence"
            )
        )

    def publish_to_knowledge_hub(self, summary: RepositorySummary) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        report_md = (
            f"# Repository Summary: Architecture & Health\n\n"
            f"## High-level Architecture\n{summary.high_level_architecture}\n\n"
            f"## Key Components\n" + "\n".join([f"- {c}" for c in summary.components]) + "\n\n"
            f"## Repository Health\n"
            f"- File count: {summary.health.file_count}\n"
            f"- Folder count: {summary.health.folder_count}\n"
            f"- Test files count: {summary.health.test_count}\n"
            f"- Documentation coverage: {summary.health.documentation_coverage * 100:.1f}%\n"
        )

        doc = KnowledgeDocument(
            document_id=f"workspace_summary_{int(summary.timestamp)}",
            title=f"Workspace Architecture Summary - {int(summary.timestamp)}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"workspace_summary_{int(summary.timestamp)}",
                timestamp=summary.timestamp,
                source_subsystem="workspace_intelligence",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

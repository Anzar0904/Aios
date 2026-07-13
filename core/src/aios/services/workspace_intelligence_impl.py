from __future__ import annotations

import ast
import json
import logging
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from aios.services.developer_workspace import DeveloperWorkspaceService
from aios.services.knowledge_hub import KnowledgeDocument, KnowledgeHubService
from aios.services.knowledge_hub import KnowledgeMetadata as KHMetadata
from aios.services.memory import MemoryMetadata, MemoryService, MemoryType
from aios.services.model import LLMRequest, ModelService
from aios.services.project_intelligence import ProjectContext, ProjectIntelligenceService
from aios.services.workspace_intelligence import (
    ArchitectureAnalyzer,
    ASTAnalyzer,
    CallGraphBuilder,
    CodeIntelligenceService,
    CodeStructureSummary,
    DependencyAnalyzer,
    DependencyGraphBuilder,
    DocumentationAnalyzer,
    FileMetadata,
    LanguageASTParser,
    RepositoryAnalyzer,
    RepositoryHealth,
    RepositorySummary,
    SymbolIndexer,
    SymbolReference,
    TechnologyAnalyzer,
    WorkspaceContext,
    WorkspaceIntelligenceService,
)

logger = logging.getLogger(__name__)


def detect_project_boundary(workspace_root: str) -> str:
    """Walk up from workspace_root to find the project boundary.

    Strategy:
    1. If a .git directory exists anywhere in the ancestor chain, that directory
       is the definitive project root (handles monorepos correctly).
    2. Otherwise fall back to the innermost ancestor that contains a recognised
       package manifest (pyproject.toml, package.json, Cargo.toml, go.mod, …).
    """
    path = Path(workspace_root).resolve()
    git_root: Optional[Path] = None
    package_root: Optional[Path] = None

    current = path
    while True:
        if (current / ".git").exists():
            git_root = current
            break  # .git is unambiguous — stop here
        if package_root is None:
            package_indicators = {
                "pyproject.toml",
                "package.json",
                "Cargo.toml",
                "go.mod",
                "setup.py",
                "requirements.txt",
                "pom.xml",
                "build.gradle",
            }
            if any((current / ind).exists() for ind in package_indicators):
                package_root = current
        if current.parent == current:
            break
        current = current.parent

    return str(git_root or package_root or path)


def find_all_workspaces(project_root: str, default_ignores: set) -> List[str]:
    workspaces = []
    root_path = Path(project_root).resolve()
    config_names = {
        "package.json",
        "Cargo.toml",
        "go.mod",
        "pyproject.toml",
        "build.gradle",
        "pom.xml",
    }

    for root, dirs, files in os.walk(root_path):
        dirs[:] = [d for d in dirs if d not in default_ignores and not d.startswith(".")]
        if any(f in config_names for f in files):
            try:
                rel_path = Path(root).relative_to(root_path)
                if str(rel_path) == ".":
                    workspaces.append(".")
                else:
                    workspaces.append(str(rel_path))
            except Exception:
                pass
    return workspaces


def load_aiosignore_rules(root_path: Path) -> List[str]:
    rules = []
    aiosignore = root_path / ".aiosignore"
    if aiosignore.is_file():
        try:
            for line in aiosignore.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#"):
                    rules.append(line)
        except Exception:
            pass
    return rules


def symbol_to_dict(sym: SymbolReference) -> Dict[str, Any]:
    return {
        "symbol_id": sym.symbol_id,
        "name": sym.name,
        "symbol_type": sym.symbol_type,
        "file_path": sym.file_path,
        "start_line": sym.start_line,
        "end_line": sym.end_line,
        "dependencies": sym.dependencies,
        "decorators": sym.decorators,
        "is_public": sym.is_public,
        "meta": sym.meta,
    }


def dict_to_symbol(d: Dict[str, Any]) -> SymbolReference:
    return SymbolReference(
        symbol_id=d["symbol_id"],
        name=d["name"],
        symbol_type=d["symbol_type"],
        file_path=d["file_path"],
        start_line=d["start_line"],
        end_line=d["end_line"],
        dependencies=d.get("dependencies", []),
        decorators=d.get("decorators", []),
        is_public=d.get("is_public", True),
        meta=d.get("meta", {}),
    )


def classify_architecture(
    workspace_root: str, structure: List[str], code_intel: Optional[Any] = None
) -> Dict[str, List[str]]:
    arch_map = {
        "services": [],
        "controllers": [],
        "apis_routes": [],
        "models": [],
        "database_layer": [],
        "middleware": [],
        "utilities": [],
        "configuration": [],
    }

    for file in structure:
        file_path = Path(workspace_root) / file
        file_lower = file.lower()
        ext = file_path.suffix.lower()

        if ext in (".toml", ".json", ".yaml", ".yml", ".ini", ".cfg") or file_lower in (
            ".gitignore",
            ".env",
            "dockerfile",
            "docker-compose.yml",
        ):
            arch_map["configuration"].append(file)
            continue

        if ext not in (
            ".py",
            ".ts",
            ".tsx",
            ".js",
            ".jsx",
            ".go",
            ".rs",
            ".java",
            ".cpp",
            ".c",
            ".h",
        ):
            continue

        purpose = "source"
        if (
            "test_" in file_lower
            or "_test" in file_lower
            or file_lower.endswith((".test.js", ".spec.ts", ".test.ts"))
        ):
            purpose = "test"

        if purpose == "test":
            continue

        exports = []
        if code_intel:
            try:
                meta = code_intel.get_file_metadata(file)
                if meta:
                    exports = meta.exports
            except Exception:
                pass

        name_stem = file_path.stem.lower()

        if (
            "service" in name_stem
            or any("service" in exp.lower() for exp in exports)
            or "services/" in file
        ):
            arch_map["services"].append(file)
        elif "controller" in name_stem or any("controller" in exp.lower() for exp in exports):
            arch_map["controllers"].append(file)
        elif (
            "model" in name_stem
            or any("model" in exp.lower() for exp in exports)
            or "models/" in file
        ):
            arch_map["models"].append(file)
        elif any(
            db_word in name_stem
            for db_word in (
                "db",
                "database",
                "repository",
                "repo",
                "query",
                "postgres",
                "sql",
                "redis",
                "qdrant",
            )
        ):
            arch_map["database_layer"].append(file)
        elif "middleware" in name_stem or any("middleware" in exp.lower() for exp in exports):
            arch_map["middleware"].append(file)
        elif (
            any(
                util_word in name_stem
                for util_word in ("util", "helper", "common", "tool", "shared")
            )
            or "utils/" in file
            or "helpers/" in file
        ):
            arch_map["utilities"].append(file)

        is_route = False
        if any(route_word in name_stem for route_word in ("route", "api", "endpoint")):
            is_route = True
        else:
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                route_patterns = (
                    "@app.get",
                    "@app.post",
                    "@router.get",
                    "@router.post",
                    "@blueprint.route",
                    "router.get",
                    "app.get",
                )
                if any(pat in content for pat in route_patterns):
                    is_route = True
            except Exception:
                pass
        if is_route and file not in arch_map["services"] and file not in arch_map["controllers"]:
            arch_map["apis_routes"].append(file)

    return arch_map


def detect_coding_conventions(symbols: List[SymbolReference]) -> Dict[str, Any]:
    conventions = {
        "class_naming": "PascalCase",
        "function_naming": "snake_case",
        "method_naming": "snake_case",
    }
    [s.name for s in symbols if s.symbol_type == "class"]
    func_names = [s.name for s in symbols if s.symbol_type == "function"]

    if func_names:
        snake_count = sum(1 for name in func_names if "_" in name)
        camel_count = sum(
            1 for name in func_names if any(c.isupper() for c in name) and "_" not in name
        )
        if camel_count > snake_count:
            conventions["function_naming"] = "camelCase"
            conventions["method_naming"] = "camelCase"

    return conventions


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

        has_docker = (root_path / "Dockerfile").is_file() or (
            root_path / "docker-compose.yml"
        ).is_file()

        env_files = []
        try:
            env_files = [
                f.name for f in root_path.iterdir() if f.is_file() and f.name.startswith(".env")
            ]
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
        components = [
            "Kernel",
            "Orchestrator",
            "ServiceRegistry",
            "MemoryService",
            "ReasoningService",
            "IntentEngine",
        ]
        if "package.json" in str(files) or "npm/yarn" in context.package_managers:
            components.append("WebFrontEnd")

        design_patterns = [
            "Dependency Injection",
            "Singleton (ServiceRegistry)",
            "Composition Root",
            "Lifecycle Hooks",
        ]
        observations = [
            "Modular services decouple implementation details from abstraction interfaces.",
            "Strict clean architecture boundaries are maintained in core directories.",
        ]

        return {
            "high_level_architecture": "Clean Architecture implementation with segregated domains and dynamic service lookup registries.",
            "components": components,
            "entry_points": ["core/src/aios/bootstrap.py", "core/src/aios/kernel.py"],
            "execution_paths": [
                "Bootstrapping -> Kernel run -> Intent classification -> Reasoning Plan -> Execution"
            ],
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
        files = context.structure

        languages = []
        if ".py" in exts:
            languages.append("Python")
        if ".js" in exts or ".ts" in exts or ".tsx" in exts or ".jsx" in exts:
            languages.append("JavaScript/TypeScript")
        if ".go" in exts:
            languages.append("Go")
        if ".rs" in exts:
            languages.append("Rust")
        if ".java" in exts:
            languages.append("Java")
        if ".dart" in exts:
            languages.append("Dart")
        if ".cpp" in exts or ".c" in exts or ".h" in exts:
            languages.append("C/C++")

        frameworks = list(context.frameworks)
        package_managers = list(context.package_managers)
        build_systems = []
        runtimes = []
        deployment_configs = []

        # Analyze files list for ecosystem indicators
        files_set = set(files)

        # Next.js / Express / React
        if "package.json" in files_set:
            if "npm/yarn" not in package_managers:
                package_managers.append("npm/yarn")
            build_systems.append("npm scripts")
            runtimes.append("Node.js")
            try:
                content = (
                    (Path(workspace_root) / "package.json")
                    .read_text(encoding="utf-8", errors="ignore")
                    .lower()
                )
                if "next" in content and "Next.js" not in frameworks:
                    frameworks.append("Next.js")
                if "express" in content and "Express" not in frameworks:
                    frameworks.append("Express")
                if "react" in content and "React" not in frameworks:
                    frameworks.append("React")
                if "vue" in content and "Vue" not in frameworks:
                    frameworks.append("Vue")
                if "angular" in content and "Angular" not in frameworks:
                    frameworks.append("Angular")
            except Exception:
                pass

        # FastAPI / Django / Flask / Python
        if (
            "pyproject.toml" in files_set
            or "requirements.txt" in files_set
            or "setup.py" in files_set
        ):
            if "poetry/pip" not in package_managers:
                package_managers.append("poetry/pip")
            build_systems.append("setuptools/poetry")
            runtimes.append("Python Runtime")

            try:
                for f in ("pyproject.toml", "requirements.txt"):
                    f_path = Path(workspace_root) / f
                    if f_path.is_file():
                        content = f_path.read_text(encoding="utf-8", errors="ignore").lower()
                        if "fastapi" in content and "FastAPI" not in frameworks:
                            frameworks.append("FastAPI")
                        if "django" in content and "Django" not in frameworks:
                            frameworks.append("Django")
                        if "flask" in content and "Flask" not in frameworks:
                            frameworks.append("Flask")
            except Exception:
                pass

        # Rust
        if "Cargo.toml" in files_set:
            if "cargo" not in package_managers:
                package_managers.append("cargo")
            build_systems.append("cargo build")
            runtimes.append("Rust compiled binary")

        # Go
        if "go.mod" in files_set:
            if "go-modules" not in package_managers:
                package_managers.append("go-modules")
            build_systems.append("go build")
            runtimes.append("Go compiled binary")

        # Flutter / Dart
        if "pubspec.yaml" in files_set:
            package_managers.append("pub")
            build_systems.append("flutter build")
            frameworks.append("Flutter")
            runtimes.append("Dart VM / Flutter Native")

        # Java Spring Boot / Maven / Gradle
        if "pom.xml" in files_set:
            package_managers.append("maven")
            build_systems.append("maven package")
            runtimes.append("JVM")
            frameworks.append("Spring Boot")
        elif "build.gradle" in files_set:
            package_managers.append("gradle")
            build_systems.append("gradle build")
            runtimes.append("JVM")
            frameworks.append("Spring Boot")

        # Deployment indicators
        if "Dockerfile" in files_set or "docker-compose.yml" in files_set:
            deployment_configs.append("Docker")
        if any(f.startswith(".github/workflows") for f in files):
            deployment_configs.append("GitHub Actions")
        if "vercel.json" in files_set:
            deployment_configs.append("Vercel")
        if "supabase.js" in files_set or "supabase/config.toml" in files_set:
            deployment_configs.append("Supabase")

        testing_frameworks = []
        linters = []
        databases = []
        clouds = ["AWS/GCP/Mock"]

        all_deps = set(context.dependencies)
        if "pytest" in all_deps or any("test" in f for f in files):
            testing_frameworks.append("pytest")
        if "jest" in all_deps:
            testing_frameworks.append("jest")
        if "vitest" in all_deps:
            testing_frameworks.append("vitest")
        if "ruff" in all_deps:
            linters.append("ruff")
        if "eslint" in all_deps:
            linters.append("eslint")
        if (
            "sqlite3" in all_deps
            or "postgresql" in all_deps
            or "psycopg2" in all_deps
            or "psycopg2-binary" in all_deps
        ):
            databases.append("PostgreSQL / Relational Database")
        if "redis" in all_deps:
            databases.append("Redis Cache")
        if "qdrant-client" in all_deps:
            databases.append("Qdrant Vector Store")

        return {
            "languages": languages,
            "frameworks": frameworks,
            "package_managers": package_managers,
            "testing_frameworks": testing_frameworks,
            "linters": linters,
            "databases": databases,
            "clouds": clouds,
            "runtimes": runtimes,
            "build_systems": build_systems,
            "deployment_configs": deployment_configs,
        }


class LocalDocumentationAnalyzer(DocumentationAnalyzer):
    def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, Any]:
        context: ProjectContext = project_context["context"]
        files = context.structure

        doc_files = [
            f for f in files if f.startswith("docs/") or f.endswith(".md") or f.endswith(".txt")
        ]
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

        # 1. Project Boundary Detection
        boundary = detect_project_boundary(workspace_root)

        # 2. Default Ignores & Monorepos workspaces
        default_ignores = {
            ".git",
            "node_modules",
            ".venv",
            "venv",
            ".pytest_cache",
            ".ruff_cache",
            "__pycache__",
            "dist",
            "build",
        }
        workspaces = find_all_workspaces(boundary, default_ignores)

        # 3. Analyze raw repo data
        repo_data = self._analyzer.analyze(workspace_root)

        # 4. Custom Ignore patterns (.aiosignore rules)
        aiosignore_rules = load_aiosignore_rules(Path(boundary))
        context: ProjectContext = repo_data["context"]
        if aiosignore_rules:
            filtered_structure = []
            for f in context.structure:
                is_ignored = False
                f_clean = f.replace("\\", "/")
                for rule in aiosignore_rules:
                    rule_clean = rule.replace("\\", "/")
                    if rule_clean.endswith("/"):
                        if f_clean.startswith(rule_clean) or f"/{rule_clean}" in f_clean:
                            is_ignored = True
                            break
                    else:
                        if rule_clean in f_clean:
                            is_ignored = True
                            break
                if not is_ignored:
                    filtered_structure.append(f)
            context.structure = filtered_structure
            context.statistics["total_files"] = len(filtered_structure)

        arch_data = self._arch_analyzer.analyze(workspace_root, repo_data)
        dep_data = self._dep_analyzer.analyze(workspace_root, repo_data)
        tech_data = self._tech_analyzer.analyze(workspace_root, repo_data)
        doc_data = self._doc_analyzer.analyze(workspace_root, repo_data)

        total_files = context.statistics.get("total_files", 0)
        total_folders = context.statistics.get("total_folders", 0)

        test_count = len([f for f in context.structure if "test_" in f or "_test" in f])
        config_files_count = len(
            [
                f
                for f in context.structure
                if f.endswith(".json")
                or f.endswith(".toml")
                or f.endswith(".yaml")
                or f.endswith(".yml")
            ]
        )
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
                "workspaces": workspaces,
                "project_boundary": boundary,
                "circular_dependencies": [],
                "unused_modules": [],
                # Technology detail fields
                "runtimes": tech_data.get("runtimes", []),
                "build_systems": tech_data.get("build_systems", []),
                "testing_frameworks": tech_data.get("testing_frameworks", []),
                "databases": tech_data.get("databases", []),
                "deployment_configs": tech_data.get("deployment_configs", []),
            },
        )

        # 5. Dependency & Call graph details with CodeIntelligenceService
        code_intel = self._registry.get(CodeIntelligenceService) if self._registry else None
        code_summary = None
        if code_intel:
            try:
                code_summary = code_intel.analyze_codebase(workspace_root)

                # Circular dependency detection
                dep_graph = code_summary.dependency_graph
                visited = {}
                path = []
                circular_deps = []

                def detect_cycle(node):
                    visited[node] = 1
                    path.append(node)
                    for neighbor in dep_graph.get(node, []):
                        if visited.get(neighbor) == 1:
                            cycle_start = path.index(neighbor)
                            cycle = path[cycle_start:] + [neighbor]
                            try:
                                rel_cycle = [
                                    str(Path(p).relative_to(Path(workspace_root))) for p in cycle
                                ]
                                if rel_cycle not in circular_deps:
                                    circular_deps.append(rel_cycle)
                            except Exception:
                                pass
                        elif neighbor not in visited:
                            detect_cycle(neighbor)
                    path.pop()
                    visited[node] = 2

                for node in dep_graph:
                    if node not in visited:
                        detect_cycle(node)

                summary.metadata["circular_dependencies"] = circular_deps

                # Unused modules detection
                all_imported = set()
                for imports in dep_graph.values():
                    for imp in imports:
                        all_imported.add(imp)

                entry_points_abs = [str(Path(workspace_root) / ep) for ep in summary.entry_points]
                unused_modules = []

                for file_abs in dep_graph:
                    try:
                        rel_file = str(Path(file_abs).relative_to(Path(workspace_root)))
                        meta = code_intel.get_file_metadata(rel_file)
                        if (
                            meta
                            and meta.purpose == "source"
                            and file_abs not in all_imported
                            and file_abs not in entry_points_abs
                        ):
                            unused_modules.append(rel_file)
                    except Exception:
                        pass
                summary.metadata["unused_modules"] = unused_modules

            except Exception as e:
                logger.debug(f"Codebase analysis integration failed: {e}")

        # Automatically generate markdown reports
        try:
            self.generate_markdown_reports(workspace_root, summary, code_summary)
        except Exception as e:
            logger.warning(f"Failed to generate workspace markdown reports: {e}")

        return summary

    def store_summary_in_memory(self, summary: RepositorySummary) -> None:
        auth_locations = []
        db_locations = []
        api_entrypoints = []
        build_deployment_config = []

        code_intel = self._registry.get(CodeIntelligenceService) if self._registry else None
        if code_intel:
            try:
                for meta in code_intel.list_all_files_metadata():
                    file = meta.file_path
                    file_lower = file.lower()
                    if "auth" in file_lower or "login" in file_lower or "jwt" in file_lower:
                        auth_locations.append(file)
                    if (
                        "db" in file_lower
                        or "database" in file_lower
                        or "postgres" in file_lower
                        or "sql" in file_lower
                    ):
                        db_locations.append(file)
                    if "route" in file_lower or "api" in file_lower or "controller" in file_lower:
                        api_entrypoints.append(file)
                    if (
                        meta.purpose == "config"
                        or "docker" in file_lower
                        or "github/workflows" in file_lower
                        or "deployment" in file_lower
                    ):
                        build_deployment_config.append(file)
            except Exception:
                pass

        summary_content = (
            f"Repository Architecture Summary:\n"
            f"Architecture: {summary.high_level_architecture}\n"
            f"Components: {summary.components}\n"
            f"Design Patterns: {summary.design_patterns}\n"
            f"Health stats: files={summary.health.file_count}, folders={summary.health.folder_count}\n"
            f"Auth Locations: {auth_locations[:5]}\n"
            f"Database Locations: {db_locations[:5]}\n"
            f"API Entrypoints: {api_entrypoints[:5]}\n"
            f"Build/Deployment Config: {build_deployment_config[:5]}"
        )
        self._memory.add_memory(
            content=summary_content,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id="default_workspace",
                session_id="workspace_intelligence_session",
                tags=[
                    "repository_summary",
                    "architecture_summary",
                    "project_knowledge",
                    "auth_location",
                    "database_location",
                    "api_entrypoint",
                    "build_configuration",
                    "deployment_configuration",
                ],
                importance=2,
                source_subsystem="workspace_intelligence",
            ),
        )

        try:
            if self._registry:
                import time

                from aios.services.persistence import SemanticMemoryManager

                sem_mgr = self._registry.get(SemanticMemoryManager)
                if sem_mgr:
                    ws_id = "default_workspace"
                    metadata = {
                        "workspace_id": ws_id,
                        "timestamp": time.time(),
                        "type": "repository_summary",
                    }
                    sem_mgr.index_memory(
                        repository_name="workspace_memory",
                        entity_id=summary.summary_id,
                        text=summary_content,
                        metadata=metadata,
                        tags=["repository_summary", "architecture_summary"],
                    )
        except Exception:
            pass

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
                category="Project",
            ),
        )
        self._knowledge_hub.sync_document(doc, "notion")

    def get_workspace_context(self, workspace_root: str) -> WorkspaceContext:
        boundary = detect_project_boundary(workspace_root)
        summary = self.analyze_repository(workspace_root)

        default_ignores = {
            ".git",
            "node_modules",
            ".venv",
            "venv",
            ".pytest_cache",
            ".ruff_cache",
            "__pycache__",
            "dist",
            "build",
        }
        workspaces = find_all_workspaces(boundary, default_ignores)

        # Analyze codebase symbols for conventions
        code_intel = self._registry.get(CodeIntelligenceService) if self._registry else None
        conventions = {
            "class_naming": "PascalCase",
            "function_naming": "snake_case",
            "method_naming": "snake_case",
        }
        symbols = []
        if code_intel:
            try:
                symbols = code_intel._indexer.list_symbols()
                conventions = detect_coding_conventions(symbols)
            except Exception:
                pass

        arch_map = classify_architecture(
            workspace_root, summary.health.statistics.get("structure", []), code_intel
        )

        project_type = "single-package"
        if len(workspaces) > 1:
            project_type = "monorepo"

        tech_stack = {
            "languages": list(summary.languages.keys()),
            "frameworks": summary.frameworks,
            "package_managers": summary.package_managers,
        }

        # Important directories: directories at root level
        important_dirs = []
        try:
            for item in Path(workspace_root).iterdir():
                if (
                    item.is_dir()
                    and not item.name.startswith(".")
                    and item.name not in default_ignores
                ):
                    important_dirs.append(item.name)
        except Exception:
            pass

        return WorkspaceContext(
            workspace_root=workspace_root,
            technology_stack=tech_stack,
            architecture={
                "high_level_architecture": summary.high_level_architecture,
                "components": summary.components,
                "design_patterns": summary.design_patterns,
                "segmentation": arch_map,
            },
            dependencies=summary.dependencies,
            project_type=project_type,
            important_directories=important_dirs,
            coding_conventions=conventions,
            workspaces=workspaces,
            metadata=summary.metadata,
        )

    def generate_markdown_reports(
        self,
        workspace_root: str,
        summary: RepositorySummary,
        code_summary: Optional[CodeStructureSummary] = None,
    ) -> None:
        docs_dir = Path(workspace_root) / "docs"
        docs_dir.mkdir(exist_ok=True)

        # Retrieve git info safely
        dev_ws = self._registry.get(DeveloperWorkspaceService) if self._registry else None
        git_branch = "unknown"
        staged_files = []
        unstaged_files = []
        untracked_files = []
        if dev_ws:
            try:
                ws_info = dev_ws.get_workspace_info(workspace_root)
                git_branch = ws_info.extra.get("git_branch") or "unknown"
                staged_files = ws_info.staged_files
                unstaged_files = ws_info.unstaged_files
                untracked_files = ws_info.untracked_files
            except Exception:
                pass

        recent_commits = get_recent_commits(workspace_root)
        recent_commits_list = (
            "\n".join([f"- {c}" for c in recent_commits]) if recent_commits else "- None"
        )
        workspaces_list = "\n".join([f"- {ws}" for ws in summary.metadata.get("workspaces", [])])

        # 1. REPOSITORY_SUMMARY.md
        repo_summary_md = f"""# Repository Summary

## Overview
- **Project Name**: {Path(workspace_root).name}
- **Project Root**: `{workspace_root}`
- **Git Branch**: `{git_branch}`
- **Workspaces / Packages**:
{workspaces_list}

## Repository Statistics
- **Total Files**: {summary.health.file_count}
- **Total Folders**: {summary.health.folder_count}
- **Test Files Count**: {summary.health.test_count}
- **Documentation Coverage**: {summary.health.documentation_coverage:.1%}
- **ADR Count**: {summary.health.adr_count}
- **README Coverage**: {summary.health.readme_coverage:.1%}
- **Config Completeness**: {summary.health.config_completeness:.1%}

## Git Status Summary
- **Staged Files**: {len(staged_files)}
- **Unstaged Changes**: {len(unstaged_files)}
- **Untracked Files**: {len(untracked_files)}

### Recent Commits
{recent_commits_list}
"""
        (docs_dir / "REPOSITORY_SUMMARY.md").write_text(repo_summary_md, encoding="utf-8")

        # 2. ARCHITECTURE_SUMMARY.md
        code_intel = self._registry.get(CodeIntelligenceService) if self._registry else None
        arch_map = classify_architecture(
            workspace_root,
            summary.metadata.get("structure", []) or summary.health.statistics.get("structure", []),
            code_intel,
        )

        def format_list(lst):
            return "\n".join([f"- {item}" for item in lst]) if lst else "- None"

        components_list = format_list(summary.components)
        execution_paths_list = format_list(summary.execution_paths)
        design_patterns_list = format_list(summary.design_patterns)
        observations_list = format_list(summary.architectural_observations)

        arch_summary_md = f"""# Architecture Summary

## High-level Architecture
{summary.high_level_architecture}

## Key Components
{components_list}

## Execution Paths
{execution_paths_list}

## Design Patterns Detected
{design_patterns_list}

## Codebase Architecture Segmentation
### Services
{format_list(arch_map["services"])}

### Controllers
{format_list(arch_map["controllers"])}

### APIs / Routes
{format_list(arch_map["apis_routes"])}

### Models
{format_list(arch_map["models"])}

### Database Layer
{format_list(arch_map["database_layer"])}

### Middleware
{format_list(arch_map["middleware"])}

### Utilities
{format_list(arch_map["utilities"])}

### Configuration
{format_list(arch_map["configuration"])}

## Architectural Observations
{observations_list}
"""
        (docs_dir / "ARCHITECTURE_SUMMARY.md").write_text(arch_summary_md, encoding="utf-8")

        # 3. DEPENDENCY_SUMMARY.md
        circular_deps = summary.metadata.get("circular_dependencies", [])
        circular_deps_str = (
            "\n".join([f"- Cycle: {' -> '.join(cycle)}" for cycle in circular_deps])
            if circular_deps
            else "- None detected"
        )

        unused_mods = summary.metadata.get("unused_modules", [])
        unused_mods_str = format_list(unused_mods)

        relationships = []
        for src, dests in list(summary.dependencies.items())[:20]:
            if dests:
                relationships.append(f"- `{src}` imports: {', '.join([f'`{d}`' for d in dests])}")
        relationships_str = "\n".join(relationships) if relationships else "- None"

        dependency_summary_md = f"""# Dependency Summary

## Monorepo Workspaces
{workspaces_list}

## Circular Dependencies
{circular_deps_str}

## Unused Modules
{unused_mods_str}

## Module Import Relationships
{relationships_str}
"""
        (docs_dir / "DEPENDENCY_SUMMARY.md").write_text(dependency_summary_md, encoding="utf-8")

        # 4. TECHNOLOGY_STACK.md — derive from already-computed summary data
        tech_stack_md = f"""# Technology Stack

## Programming Languages
{format_list(list(summary.languages.keys()))}

## Frameworks
{format_list(summary.frameworks)}

## Package Managers
{format_list(summary.package_managers)}

## Build Systems
{format_list(summary.metadata.get("build_systems", []))}

## Runtimes
{format_list(summary.metadata.get("runtimes", []))}

## Testing Frameworks
{format_list(summary.metadata.get("testing_frameworks", []))}

## Databases
{format_list(summary.metadata.get("databases", []))}

## Deployment Configuration
{format_list(summary.metadata.get("deployment_configs", []))}
"""
        (docs_dir / "TECHNOLOGY_STACK.md").write_text(tech_stack_md, encoding="utf-8")

        # 5. WORKSPACE_HEALTH.md
        overall_health = "Green"
        health_score = (
            summary.health.documentation_coverage
            + summary.health.readme_coverage
            + summary.health.config_completeness
        ) / 3.0
        if health_score < 0.4:
            overall_health = "Red"
        elif health_score < 0.7:
            overall_health = "Yellow"

        # Gather todo markers from context structure if available
        todos_count = 0
        todos_list_str = "- None"
        try:
            proj_context = self._project_intel.analyze_workspace(workspace_root)
            todos_count = len(proj_context.todo_markers)
            todos_list_str = "\n".join(
                [
                    f"- `{t['file']}:L{t['line']}`: {t['text'][:100]}"
                    for t in proj_context.todo_markers[:15]
                ]
            )
        except Exception:
            pass

        workspace_health_md = f"""# Workspace Health Report

## Health Scores
- **Documentation Coverage**: {summary.health.documentation_coverage:.1%}
- **README Coverage**: {summary.health.readme_coverage:.1%}
- **Config Completeness**: {summary.health.config_completeness:.1%}
- **Overall Code Health**: {overall_health}

## Code Metrics
- **Total Files**: {summary.health.file_count}
- **Total Folders**: {summary.health.folder_count}
- **Test Files Count**: {summary.health.test_count}
- **Line Count**: {summary.health.statistics.get("total_lines", 0)}

## Git Status Summary
- **Uncommitted Changes**: {len(staged_files) + len(unstaged_files)}
- **Untracked Files**: {len(untracked_files)}

## TODO & FIXME Markers ({todos_count} found)
{todos_list_str}
"""
        (docs_dir / "WORKSPACE_HEALTH.md").write_text(workspace_health_md, encoding="utf-8")


def get_recent_commits(workspace_root: str) -> List[str]:
    try:
        res = subprocess.run(
            ["git", "log", "-n", "5", "--oneline"],
            cwd=workspace_root,
            capture_output=True,
            text=True,
            check=True,
        )
        return [line.strip() for line in res.stdout.splitlines() if line.strip()]
    except Exception:
        return []


class PythonSymbolVisitor(ast.NodeVisitor):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        self.symbols: List[SymbolReference] = []
        self.current_class: Optional[str] = None

    def _get_decorator_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_decorator_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Call):
            return self._get_decorator_name(node.func)
        return ""

    def _get_base_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_base_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return self._get_base_name(node.value)
        return ""

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]
        decorators = [d for d in decorators if d]

        bases = [self._get_base_name(b) for b in node.bases]
        bases = [b for b in bases if b]

        symbol_type = "class"

        # Identify Dataclasses
        if any("dataclass" in d for d in decorators):
            symbol_type = "dataclass"

        # Identify Enums
        elif any(b in ("Enum", "IntEnum", "StrEnum", "Flag") for b in bases):
            symbol_type = "enum"

        # Identify Interfaces
        elif any(b in ("ABC", "Protocol") or "Interface" in b or "Protocol" in b for b in bases):
            symbol_type = "interface"

        symbol = SymbolReference(
            symbol_id=f"{self.file_path}::{node.name}",
            name=node.name,
            symbol_type=symbol_type,
            file_path=self.file_path,
            start_line=node.lineno,
            end_line=getattr(node, "end_lineno", node.lineno),
            decorators=decorators,
            is_public=not node.name.startswith("_"),
            meta={"bases": bases},
        )
        self.symbols.append(symbol)

        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_func(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_func(node)

    def _visit_func(self, node: Any) -> None:
        decorators = [self._get_decorator_name(dec) for dec in node.decorator_list]
        decorators = [d for d in decorators if d]

        symbol_type = "method" if self.current_class else "function"
        name = f"{self.current_class}.{node.name}" if self.current_class else node.name

        symbol = SymbolReference(
            symbol_id=f"{self.file_path}::{name}",
            name=name,
            symbol_type=symbol_type,
            file_path=self.file_path,
            start_line=node.lineno,
            end_line=getattr(node, "end_lineno", node.lineno),
            decorators=decorators,
            is_public=not node.name.startswith("_"),
        )
        self.symbols.append(symbol)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            symbol = SymbolReference(
                symbol_id=f"{self.file_path}::import::{alias.name}",
                name=alias.name,
                symbol_type="import",
                file_path=self.file_path,
                start_line=node.lineno,
                end_line=node.lineno,
                is_public=False,
                meta={"module": alias.name, "asname": alias.asname},
            )
            self.symbols.append(symbol)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        names = [alias.name for alias in node.names]
        symbol = SymbolReference(
            symbol_id=f"{self.file_path}::import::{module}",
            name=module,
            symbol_type="import",
            file_path=self.file_path,
            start_line=node.lineno,
            end_line=node.lineno,
            is_public=False,
            meta={"module": module, "names": names, "level": node.level},
        )
        self.symbols.append(symbol)
        self.generic_visit(node)


class PythonASTParser(LanguageASTParser):
    def can_parse(self, file_extension: str) -> bool:
        return file_extension.lower() == ".py"

    def parse(self, file_path: str, content: str) -> List[SymbolReference]:
        try:
            tree = ast.parse(content)

            lines = content.splitlines()
            symbols = [
                SymbolReference(
                    symbol_id=file_path,
                    name=Path(file_path).stem,
                    symbol_type="module",
                    file_path=file_path,
                    start_line=1,
                    end_line=max(1, len(lines)),
                    is_public=True,
                )
            ]

            visitor = PythonSymbolVisitor(file_path)
            visitor.visit(tree)
            symbols.extend(visitor.symbols)
            return symbols
        except Exception:
            return []


class TypeScriptASTParser(LanguageASTParser):
    def can_parse(self, file_extension: str) -> bool:
        return file_extension.lower() in (".ts", ".tsx", ".js", ".jsx")

    def parse(self, file_path: str, content: str) -> List[SymbolReference]:
        cleaned_content = self._clean_source(content)
        lines_clean = cleaned_content.splitlines()
        lines_raw = content.splitlines()
        symbols = []

        symbols.append(
            SymbolReference(
                symbol_id=file_path,
                name=Path(file_path).name,
                symbol_type="module",
                file_path=file_path,
                start_line=1,
                end_line=max(1, len(lines_raw)),
                is_public=True,
            )
        )

        import_pattern = re.compile(r'\bimport\s+(?:([\w\s{},*]+)\s+from\s+)?[\'"]([^\'"]+)[\'"]')
        decorator_pattern = re.compile(r"^@([\w.]+)")
        class_pattern = re.compile(
            r"\b(?:export\s+)?(?:default\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w\s,]+))?"
        )
        interface_pattern = re.compile(
            r"\b(?:export\s+)?interface\s+(\w+)(?:\s+extends\s+([\w\s,]+))?"
        )
        enum_pattern = re.compile(r"\b(?:export\s+)?enum\s+(\w+)")
        func_pattern = re.compile(r"\b(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(\w+)")
        arrow_func_pattern = re.compile(
            r"\b(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(.*?\)\s*=>"
        )
        method_pattern = re.compile(
            r"\b(?:public|private|protected|readonly|static|async|get|set)?\s*(\w+)\s*\("
        )

        keywords = {
            "if",
            "for",
            "while",
            "switch",
            "catch",
            "super",
            "with",
            "return",
            "throw",
            "import",
            "export",
            "constructor",
        }

        decorators_accumulator = []
        active_blocks = []
        brace_level = 0
        pending_block = None

        for idx, (line_raw, line_clean) in enumerate(zip(lines_raw, lines_clean, strict=False), 1):
            line_stripped = line_clean.strip()
            line_raw_stripped = line_raw.strip()
            if not line_stripped and not line_raw_stripped:
                continue

            import_match = import_pattern.search(line_raw_stripped)
            if import_match:
                dep = import_match.group(2)
                raw_names = import_match.group(1)
                names = []
                if raw_names:
                    raw_names = raw_names.replace("{", "").replace("}", "").replace("* as ", "")
                    names = [n.strip() for n in raw_names.split(",") if n.strip()]

                symbol = SymbolReference(
                    symbol_id=f"{file_path}::import::{dep}",
                    name=dep,
                    symbol_type="import",
                    file_path=file_path,
                    start_line=idx,
                    end_line=idx,
                    is_public=False,
                    meta={"module": dep, "names": names},
                )
                symbols.append(symbol)
                decorators_accumulator = []
                continue

            dec_match = decorator_pattern.match(line_stripped)
            class_match = class_pattern.search(line_stripped)
            interface_match = interface_pattern.search(line_stripped)
            enum_match = enum_pattern.search(line_stripped)

            innermost_class = None
            if active_blocks and active_blocks[-1]["type"] == "class":
                innermost_class = active_blocks[-1]

            method_match = method_pattern.search(line_stripped) if innermost_class else None
            func_match = func_pattern.search(line_stripped)
            arrow_match = arrow_func_pattern.search(line_stripped)

            if dec_match:
                decorators_accumulator.append(dec_match.group(1))

            elif class_match:
                name = class_match.group(1)
                extends = class_match.group(2)
                implements_raw = class_match.group(3)
                implements = (
                    [i.strip() for i in implements_raw.split(",")] if implements_raw else []
                )
                is_public = "export" in line_stripped

                symbol = SymbolReference(
                    symbol_id=f"{file_path}::{name}",
                    name=name,
                    symbol_type="class",
                    file_path=file_path,
                    start_line=idx,
                    end_line=idx,
                    decorators=list(decorators_accumulator),
                    is_public=is_public,
                    meta={"extends": extends, "implements": implements}
                    if (extends or implements)
                    else {},
                )
                symbols.append(symbol)
                decorators_accumulator = []
                pending_block = {"type": "class", "name": name, "symbol": symbol, "start_line": idx}

            elif interface_match:
                name = interface_match.group(1)
                extends_raw = interface_match.group(2)
                extends = [e.strip() for e in extends_raw.split(",")] if extends_raw else []
                is_public = "export" in line_stripped

                symbol = SymbolReference(
                    symbol_id=f"{file_path}::{name}",
                    name=name,
                    symbol_type="interface",
                    file_path=file_path,
                    start_line=idx,
                    end_line=idx,
                    decorators=list(decorators_accumulator),
                    is_public=is_public,
                    meta={"extends": extends} if extends else {},
                )
                symbols.append(symbol)
                decorators_accumulator = []
                pending_block = {
                    "type": "interface",
                    "name": name,
                    "symbol": symbol,
                    "start_line": idx,
                }

            elif enum_match:
                name = enum_match.group(1)
                is_public = "export" in line_stripped

                symbol = SymbolReference(
                    symbol_id=f"{file_path}::{name}",
                    name=name,
                    symbol_type="enum",
                    file_path=file_path,
                    start_line=idx,
                    end_line=idx,
                    decorators=list(decorators_accumulator),
                    is_public=is_public,
                )
                symbols.append(symbol)
                decorators_accumulator = []
                pending_block = {"type": "enum", "name": name, "symbol": symbol, "start_line": idx}

            elif method_match:
                name = method_match.group(1)
                if name not in keywords:
                    is_public = not (
                        line_stripped.startswith("private")
                        or line_stripped.startswith("protected")
                        or name.startswith("#")
                    )
                    full_name = f"{innermost_class['name']}.{name}"
                    symbol = SymbolReference(
                        symbol_id=f"{file_path}::{full_name}",
                        name=full_name,
                        symbol_type="method",
                        file_path=file_path,
                        start_line=idx,
                        end_line=idx,
                        decorators=list(decorators_accumulator),
                        is_public=is_public,
                    )
                    symbols.append(symbol)
                    decorators_accumulator = []
                    pending_block = {
                        "type": "method",
                        "name": full_name,
                        "symbol": symbol,
                        "start_line": idx,
                    }

            elif func_match:
                name = func_match.group(1)
                is_public = "export" in line_stripped
                symbol = SymbolReference(
                    symbol_id=f"{file_path}::{name}",
                    name=name,
                    symbol_type="function",
                    file_path=file_path,
                    start_line=idx,
                    end_line=idx,
                    decorators=list(decorators_accumulator),
                    is_public=is_public,
                )
                symbols.append(symbol)
                decorators_accumulator = []
                pending_block = {
                    "type": "function",
                    "name": name,
                    "symbol": symbol,
                    "start_line": idx,
                }

            elif arrow_match:
                name = arrow_match.group(1)
                is_public = "export" in line_stripped
                symbol = SymbolReference(
                    symbol_id=f"{file_path}::{name}",
                    name=name,
                    symbol_type="function",
                    file_path=file_path,
                    start_line=idx,
                    end_line=idx,
                    decorators=list(decorators_accumulator),
                    is_public=is_public,
                )
                symbols.append(symbol)
                decorators_accumulator = []
                pending_block = {
                    "type": "function",
                    "name": name,
                    "symbol": symbol,
                    "start_line": idx,
                }

            for char in line_clean:
                if char == "{":
                    if pending_block:
                        pending_block["start_brace_level"] = brace_level
                        active_blocks.append(pending_block)
                        pending_block = None
                    brace_level += 1
                elif char == "}":
                    brace_level -= 1
                    if active_blocks and brace_level <= active_blocks[-1]["start_brace_level"]:
                        ended = active_blocks.pop()
                        ended["symbol"].end_line = idx

        return symbols

    def _clean_source(self, content: str) -> str:
        pattern = (
            r'(//.*?$)|(/\*.*?\*/)|("(?:\\.|[^\\"])*")|(\'(?:\\.|[^\\\'])*\')|(`(?:\\.|[^\\`])*`)'
        )

        def repl(match):
            if match.group(1):
                return ""
            if match.group(2):
                return "\n" * match.group(2).count("\n")
            return '""'

        return re.sub(pattern, repl, content, flags=re.MULTILINE)


class LocalASTAnalyzer(ASTAnalyzer):
    def __init__(self) -> None:
        self._parsers: List[LanguageASTParser] = [PythonASTParser(), TypeScriptASTParser()]

    def register_parser(self, parser: LanguageASTParser) -> None:
        self._parsers.insert(0, parser)

    def parse_file(self, file_path: str, content: str) -> List[SymbolReference]:
        ext = Path(file_path).suffix.lower()
        for parser in self._parsers:
            if parser.can_parse(ext):
                return parser.parse(file_path, content)
        return []


class LocalSymbolIndexer(SymbolIndexer):
    def __init__(self) -> None:
        self._symbols: Dict[str, SymbolReference] = {}

    def index_symbols(self, symbols: List[SymbolReference]) -> None:
        for sym in symbols:
            self._symbols[sym.name] = sym
            self._symbols[sym.symbol_id] = sym

    def lookup_symbol(self, name: str) -> Optional[SymbolReference]:
        return self._symbols.get(name)

    def list_symbols(self) -> List[SymbolReference]:
        seen = set()
        unique = []
        for sym in self._symbols.values():
            if sym.symbol_id not in seen:
                seen.add(sym.symbol_id)
                unique.append(sym)
        return unique


class LocalDependencyGraphBuilder(DependencyGraphBuilder):
    def build_graph(
        self, file_paths: List[str], symbols: List[SymbolReference]
    ) -> Dict[str, List[str]]:
        graph: Dict[str, List[str]] = {}
        for path in file_paths:
            graph[path] = []

        imports_by_file: Dict[str, List[SymbolReference]] = {}
        for sym in symbols:
            if sym.symbol_type == "import":
                imports_by_file.setdefault(sym.file_path, []).append(sym)

        file_map = {Path(p).name: p for p in file_paths}
        module_path_map = {}
        for path in file_paths:
            p = Path(path)
            if p.suffix == ".py":
                parts = p.parts
                if "src" in parts:
                    idx = parts.index("src")
                    mod_name = ".".join(parts[idx + 1 :]).replace(".py", "")
                    module_path_map[mod_name] = path
                    for k in range(1, len(parts) - idx):
                        sub_mod = ".".join(parts[idx + k :]).replace(".py", "")
                        module_path_map[sub_mod] = path
            module_path_map[p.stem] = path

        for path in file_paths:
            file_imports = imports_by_file.get(path, [])
            for imp in file_imports:
                imported_module = imp.meta.get("module", "")
                if not imported_module:
                    continue

                resolved_path = None
                if imported_module in module_path_map:
                    resolved_path = module_path_map[imported_module]
                else:
                    curr_dir = Path(path).parent
                    if imported_module.startswith("."):
                        try:
                            for ext in ("", ".ts", ".tsx", ".js", ".jsx", ".py"):
                                trial_path = (curr_dir / (imported_module + ext)).resolve()
                                if str(trial_path) in file_paths:
                                    resolved_path = str(trial_path)
                                    break
                        except Exception:
                            pass

                if not resolved_path:
                    for ext in (".py", ".ts", ".tsx", ".js", ".jsx"):
                        trial_name = imported_module + ext
                        if trial_name in file_map:
                            resolved_path = file_map[trial_name]
                            break

                if resolved_path and resolved_path != path:
                    if resolved_path not in graph[path]:
                        graph[path].append(resolved_path)

        return graph


class LocalCallGraphBuilder(CallGraphBuilder):
    def build_call_graph(self, symbols: List[SymbolReference]) -> Dict[str, List[str]]:
        call_graph: Dict[str, List[str]] = {}
        func_methods = [s for s in symbols if s.symbol_type in ("function", "method")]

        for sym in func_methods:
            call_graph[sym.name] = []

        symbols_by_file: Dict[str, List[SymbolReference]] = {}
        for sym in symbols:
            symbols_by_file.setdefault(sym.file_path, []).append(sym)

        for file_path, file_symbols in symbols_by_file.items():
            try:
                content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
                lines = content.splitlines()
            except Exception:
                continue

            for sym in file_symbols:
                if sym.symbol_type not in ("function", "method"):
                    continue

                start = max(0, sym.start_line - 1)
                end = min(len(lines), sym.end_line)
                body_content = "\n".join(lines[start:end])

                for other in func_methods:
                    if other.name == sym.name:
                        continue

                    short_name = other.name.split(".")[-1]
                    pattern = rf"\b{re.escape(short_name)}\s*\("
                    if re.search(pattern, body_content):
                        if other.name not in call_graph[sym.name]:
                            call_graph[sym.name].append(other.name)

        return call_graph


class LocalCodeIntelligenceService(CodeIntelligenceService):
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

        self._analyzer = LocalASTAnalyzer()
        self._indexer = LocalSymbolIndexer()
        self._dep_builder = LocalDependencyGraphBuilder()
        self._call_builder = LocalCallGraphBuilder()
        self._files_metadata: Dict[str, FileMetadata] = {}

    def initialize(self) -> None:
        logger.info("Initializing LocalCodeIntelligenceService")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get_file_metadata(self, file_path: str) -> Optional[FileMetadata]:
        return self._files_metadata.get(file_path)

    def list_all_files_metadata(self) -> List[FileMetadata]:
        return list(self._files_metadata.values())

    def analyze_codebase(self, workspace_root: str) -> CodeStructureSummary:
        logger.info(f"Analyzing codebase at: '{workspace_root}'")
        context: ProjectContext = self._project_intel.analyze_workspace(workspace_root)

        # Incremental AST parsing Cache
        cache_path = Path(workspace_root) / ".aios_code_intelligence.json"
        ast_cache = {}
        if cache_path.is_file():
            try:
                ast_cache = json.loads(cache_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        all_symbols = []
        target_files = [
            f for f in context.structure if f.endswith((".py", ".ts", ".tsx", ".js", ".jsx"))
        ]

        new_ast_cache = {}

        # Parallel processor helper
        def process_file(file):
            file_path = Path(workspace_root) / file
            if not file_path.is_file():
                return [], None

            try:
                stat = file_path.stat()
                mtime = stat.st_mtime
                size = stat.st_size

                cached_entry = ast_cache.get(file)
                if (
                    cached_entry
                    and cached_entry.get("mtime") == mtime
                    and cached_entry.get("size") == size
                ):
                    symbols_dicts = cached_entry.get("symbols", [])
                    symbols = [dict_to_symbol(d) for d in symbols_dicts]
                    return symbols, {"mtime": mtime, "size": size, "symbols": symbols_dicts}

                content = file_path.read_text(encoding="utf-8", errors="ignore")
                symbols = self._analyzer.parse_file(str(file_path), content)
                symbols_dicts = [symbol_to_dict(s) for s in symbols]
                return symbols, {"mtime": mtime, "size": size, "symbols": symbols_dicts}
            except Exception as e:
                logger.debug(f"Error parsing file {file}: {e}")
                return [], None

        import concurrent.futures

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            futures = {executor.submit(process_file, f): f for f in target_files}
            for future in concurrent.futures.as_completed(futures):
                file = futures[future]
                symbols, cache_entry = future.result()
                all_symbols.extend(symbols)
                if cache_entry:
                    new_ast_cache[file] = cache_entry

        try:
            cache_path.write_text(json.dumps(new_ast_cache, indent=2), encoding="utf-8")
        except Exception:
            pass

        self._indexer.index_symbols(all_symbols)
        unique_symbols = self._indexer.list_symbols()

        abs_target_paths = [str(Path(workspace_root) / f) for f in target_files]
        dep_graph = self._dep_builder.build_graph(abs_target_paths, unique_symbols)
        call_graph = self._call_builder.build_call_graph(unique_symbols)

        inheritance_map = {}
        public_apis = []
        symbols_map = {}

        for sym in unique_symbols:
            symbols_map[sym.symbol_id] = sym
            if sym.name not in symbols_map:
                symbols_map[sym.name] = sym

            if sym.is_public:
                public_apis.append(sym.name)

            if sym.symbol_type == "class" and "bases" in sym.meta:
                inheritance_map[sym.name] = sym.meta["bases"]
            elif sym.symbol_type == "class" and "extends" in sym.meta:
                inheritance_map[sym.name] = [sym.meta["extends"]]
            elif sym.symbol_type == "interface" and "extends" in sym.meta:
                inheritance_map[sym.name] = sym.meta["extends"]

        # Resolve imported_by relations
        imported_by_map = {}
        for src, dests in dep_graph.items():
            for dest in dests:
                imported_by_map.setdefault(dest, []).append(src)

        file_relative_map = {str(Path(workspace_root) / f): f for f in target_files}

        self._files_metadata = {}
        for file in target_files:
            abs_path_str = str(Path(workspace_root) / file)
            file_path = Path(abs_path_str)
            size = 0
            try:
                size = file_path.stat().st_size
            except Exception:
                pass

            ext = file_path.suffix.lower()
            stem = file_path.stem
            module_name = stem
            if ext == ".py":
                parts = file_path.relative_to(Path(workspace_root)).parts
                if "src" in parts:
                    idx = parts.index("src")
                    module_name = ".".join(parts[idx + 1 :]).replace(".py", "")
                else:
                    module_name = ".".join(parts).replace(".py", "")

            purpose = "source"
            file_lower = file.lower()
            if (
                "test_" in file_lower
                or "_test" in file_lower
                or file_lower.endswith((".test.js", ".spec.ts", ".test.ts"))
            ):
                purpose = "test"
            elif ext in (".md", ".txt", ".pdf"):
                purpose = "documentation"
            elif ext in (".json", ".toml", ".yaml", ".yml", ".ini", ".cfg") or file_lower in (
                ".gitignore",
                ".env",
            ):
                purpose = "config"
            elif ext in (".sh", ".bat", ".cmd", ".ps1"):
                purpose = "build"
            elif ext in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico"):
                purpose = "asset"

            file_imports = []
            file_exports = []
            for sym in unique_symbols:
                if sym.file_path == abs_path_str:
                    if sym.symbol_type == "import":
                        file_imports.append(sym.name)
                    elif sym.symbol_type not in ("module", "import"):
                        file_exports.append(sym.name)

            rel_imports = [
                file_relative_map[p]
                for p in dep_graph.get(abs_path_str, [])
                if p in file_relative_map
            ]
            rel_imported_by = [
                file_relative_map[p]
                for p in imported_by_map.get(abs_path_str, [])
                if p in file_relative_map
            ]

            self._files_metadata[file] = FileMetadata(
                file_path=file,
                language=ext[1:].upper() if ext else "UNKNOWN",
                module=module_name,
                extension=ext,
                size=size,
                purpose=purpose,
                imports=file_imports,
                exports=file_exports,
                relationships={"imports": rel_imports, "imported_by": rel_imported_by},
            )

        # Index non-codebase files too
        for file in context.structure:
            if file not in self._files_metadata:
                file_path = Path(workspace_root) / file
                size = 0
                try:
                    size = file_path.stat().st_size
                except Exception:
                    pass
                ext = file_path.suffix.lower()
                purpose = "other"
                file_lower = file.lower()
                if ext in (".md", ".txt", ".pdf"):
                    purpose = "documentation"
                elif ext in (".json", ".toml", ".yaml", ".yml", ".ini", ".cfg") or file_lower in (
                    ".gitignore",
                    ".env",
                ):
                    purpose = "config"
                elif ext in (".sh", ".bat", ".cmd", ".ps1"):
                    purpose = "build"
                elif ext in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico"):
                    purpose = "asset"

                self._files_metadata[file] = FileMetadata(
                    file_path=file,
                    language=ext[1:].upper() if ext else "UNKNOWN",
                    module=file_path.stem,
                    extension=ext,
                    size=size,
                    purpose=purpose,
                    imports=[],
                    exports=[],
                    relationships={"imports": [], "imported_by": []},
                )

        return CodeStructureSummary(
            summary_id=f"code_summary_{int(time.time())}",
            timestamp=time.time(),
            symbols=symbols_map,
            call_graph=call_graph,
            dependency_graph=dep_graph,
            inheritance_map=inheritance_map,
            public_apis=public_apis,
        )

    def store_code_summary(self, summary: CodeStructureSummary) -> None:
        symbol_counts = {}
        for sym in summary.symbols.values():
            if sym.symbol_type not in ("import", "module"):
                symbol_counts[sym.symbol_type] = symbol_counts.get(sym.symbol_type, 0) + 1

        symbol_summary = ", ".join([f"{t}: {c}" for t, c in symbol_counts.items()])

        dep_summary_lines = []
        for mod, deps in list(summary.dependency_graph.items())[:15]:
            dep_summary_lines.append(f"- {Path(mod).name} -> {[Path(d).name for d in deps]}")
        dep_summary = "\n".join(dep_summary_lines)

        call_summary_lines = []
        for caller, callees in list(summary.call_graph.items())[:15]:
            if callees:
                call_summary_lines.append(f"- {caller} calls {callees}")
        call_summary = "\n".join(call_summary_lines)

        summary_content = (
            f"Codebase Structure Summary:\n"
            f"Symbol Stats: {symbol_summary}\n\n"
            f"Module Dependencies (sample):\n{dep_summary}\n\n"
            f"Call Graph (sample):\n{call_summary}\n\n"
            f"Public APIs (sample): {', '.join(summary.public_apis[:15])}"
        )

        self._memory.add_memory(
            content=summary_content,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id="default_workspace",
                session_id="code_intelligence_session",
                tags=["code_summary", "ast_symbols"],
                importance=2,
                source_subsystem="code_intelligence",
            ),
        )

    def publish_code_report(self, summary: CodeStructureSummary) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        report_md = (
            "# Codebase Symbol & Graph Summary\n\n"
            "## Public APIs\n"
            + "\n".join([f"- {api}" for api in summary.public_apis[:20]])
            + "\n\n"
            "## Inheritance Structure\n"
            + "\n".join(
                [f"- {cls} extends {parent}" for cls, parent in summary.inheritance_map.items()]
            )
            + "\n\n"
            f"## Symbol Counts\n"
            f"- Total extracted symbols: {len(summary.symbols)}\n"
        )

        doc = KnowledgeDocument(
            document_id=f"code_summary_{int(summary.timestamp)}",
            title=f"Codebase Structural Report - {int(summary.timestamp)}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"code_summary_{int(summary.timestamp)}",
                timestamp=summary.timestamp,
                source_subsystem="code_intelligence",
                category="Project",
            ),
        )
        self._knowledge_hub.sync_document(doc, "notion")

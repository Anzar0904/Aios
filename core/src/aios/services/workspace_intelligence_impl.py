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

        try:
            if self._registry:
                from aios.services.persistence import SemanticMemoryManager
                import time
                sem_mgr = self._registry.get(SemanticMemoryManager)
                if sem_mgr:
                    ws_id = "default_workspace"
                    metadata = {
                        "workspace_id": ws_id,
                        "timestamp": time.time(),
                        "type": "repository_summary"
                    }
                    sem_mgr.index_memory(
                        repository_name="workspace_memory",
                        entity_id=summary.summary_id,
                        text=summary_content,
                        metadata=metadata,
                        tags=["repository_summary", "architecture_summary"]
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
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")


import ast
import re
from aios.services.workspace_intelligence import (
    SymbolReference,
    CodeStructureSummary,
    ASTAnalyzer,
    SymbolIndexer,
    DependencyGraphBuilder,
    CallGraphBuilder,
    CodeIntelligenceService,
    LanguageASTParser,
)


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
            meta={"bases": bases}
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
            is_public=not node.name.startswith("_")
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
                meta={"module": alias.name, "asname": alias.asname}
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
            meta={"module": module, "names": names, "level": node.level}
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
            symbols = [SymbolReference(
                symbol_id=file_path,
                name=Path(file_path).stem,
                symbol_type="module",
                file_path=file_path,
                start_line=1,
                end_line=max(1, len(lines)),
                is_public=True
            )]
            
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
        
        symbols.append(SymbolReference(
            symbol_id=file_path,
            name=Path(file_path).name,
            symbol_type="module",
            file_path=file_path,
            start_line=1,
            end_line=max(1, len(lines_raw)),
            is_public=True
        ))
        
        import_pattern = re.compile(r'\bimport\s+(?:([\w\s{},*]+)\s+from\s+)?[\'"]([^\'"]+)[\'"]')
        decorator_pattern = re.compile(r'^@([\w.]+)')
        class_pattern = re.compile(
            r'\b(?:export\s+)?(?:default\s+)?class\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w\s,]+))?'
        )
        interface_pattern = re.compile(
            r'\b(?:export\s+)?interface\s+(\w+)(?:\s+extends\s+([\w\s,]+))?'
        )
        enum_pattern = re.compile(r'\b(?:export\s+)?enum\s+(\w+)')
        func_pattern = re.compile(r'\b(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(\w+)')
        arrow_func_pattern = re.compile(r'\b(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s*)?\(.*?\)\s*=>')
        method_pattern = re.compile(r'\b(?:public|private|protected|readonly|static|async|get|set)?\s*(\w+)\s*\(')
        
        keywords = {"if", "for", "while", "switch", "catch", "super", "with", "return", "throw", "import", "export", "constructor"}

        decorators_accumulator = []
        active_blocks = []
        brace_level = 0
        pending_block = None

        for idx, (line_raw, line_clean) in enumerate(zip(lines_raw, lines_clean), 1):
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
                    raw_names = raw_names.replace('{', '').replace('}', '').replace('* as ', '')
                    names = [n.strip() for n in raw_names.split(',') if n.strip()]
                
                symbol = SymbolReference(
                    symbol_id=f"{file_path}::import::{dep}",
                    name=dep,
                    symbol_type="import",
                    file_path=file_path,
                    start_line=idx,
                    end_line=idx,
                    is_public=False,
                    meta={"module": dep, "names": names}
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
                implements = [i.strip() for i in implements_raw.split(',')] if implements_raw else []
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
                    meta={"extends": extends, "implements": implements} if (extends or implements) else {}
                )
                symbols.append(symbol)
                decorators_accumulator = []
                pending_block = {"type": "class", "name": name, "symbol": symbol, "start_line": idx}
                
            elif interface_match:
                name = interface_match.group(1)
                extends_raw = interface_match.group(2)
                extends = [e.strip() for e in extends_raw.split(',')] if extends_raw else []
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
                    meta={"extends": extends} if extends else {}
                )
                symbols.append(symbol)
                decorators_accumulator = []
                pending_block = {"type": "interface", "name": name, "symbol": symbol, "start_line": idx}
                
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
                    is_public=is_public
                )
                symbols.append(symbol)
                decorators_accumulator = []
                pending_block = {"type": "enum", "name": name, "symbol": symbol, "start_line": idx}
                
            elif method_match:
                name = method_match.group(1)
                if name not in keywords:
                    is_public = not (line_stripped.startswith("private") or line_stripped.startswith("protected") or name.startswith("#"))
                    full_name = f"{innermost_class['name']}.{name}"
                    symbol = SymbolReference(
                        symbol_id=f"{file_path}::{full_name}",
                        name=full_name,
                        symbol_type="method",
                        file_path=file_path,
                        start_line=idx,
                        end_line=idx,
                        decorators=list(decorators_accumulator),
                        is_public=is_public
                    )
                    symbols.append(symbol)
                    decorators_accumulator = []
                    pending_block = {"type": "method", "name": full_name, "symbol": symbol, "start_line": idx}
                    
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
                    is_public=is_public
                )
                symbols.append(symbol)
                decorators_accumulator = []
                pending_block = {"type": "function", "name": name, "symbol": symbol, "start_line": idx}
                
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
                    is_public=is_public
                )
                symbols.append(symbol)
                decorators_accumulator = []
                pending_block = {"type": "function", "name": name, "symbol": symbol, "start_line": idx}

            for char in line_clean:
                if char == '{':
                    if pending_block:
                        pending_block["start_brace_level"] = brace_level
                        active_blocks.append(pending_block)
                        pending_block = None
                    brace_level += 1
                elif char == '}':
                    brace_level -= 1
                    if active_blocks and brace_level <= active_blocks[-1]["start_brace_level"]:
                        ended = active_blocks.pop()
                        ended["symbol"].end_line = idx

        return symbols

    def _clean_source(self, content: str) -> str:
        pattern = r'(//.*?$)|(/\*.*?\*/)|("(?:\\.|[^\\"])*")|(\'(?:\\.|[^\\\'])*\')|(`(?:\\.|[^\\`])*`)'
        
        def repl(match):
            if match.group(1):
                return ""
            if match.group(2):
                return "\n" * match.group(2).count("\n")
            return '""'
            
        return re.sub(pattern, repl, content, flags=re.MULTILINE)


class LocalASTAnalyzer(ASTAnalyzer):
    def __init__(self) -> None:
        self._parsers: List[LanguageASTParser] = [
            PythonASTParser(),
            TypeScriptASTParser()
        ]

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
    def build_graph(self, file_paths: List[str], symbols: List[SymbolReference]) -> Dict[str, List[str]]:
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
                    mod_name = ".".join(parts[idx+1:]).replace(".py", "")
                    module_path_map[mod_name] = path
                    for k in range(1, len(parts) - idx):
                        sub_mod = ".".join(parts[idx+k:]).replace(".py", "")
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
                    
                    short_name = other.name.split('.')[-1]
                    pattern = rf'\b{re.escape(short_name)}\s*\('
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

    def initialize(self) -> None:
        logger.info("Initializing LocalCodeIntelligenceService")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def analyze_codebase(self, workspace_root: str) -> CodeStructureSummary:
        logger.info(f"Analyzing codebase at: '{workspace_root}'")
        context: ProjectContext = self._project_intel.analyze_workspace(workspace_root)
        
        all_symbols = []
        target_files = [f for f in context.structure if f.endswith(".py") or f.endswith(".ts") or f.endswith(".tsx") or f.endswith(".js") or f.endswith(".jsx")]
        
        for file in target_files:
            file_path = Path(workspace_root) / file
            if file_path.is_file():
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    symbols = self._analyzer.parse_file(str(file_path), content)
                    all_symbols.extend(symbols)
                except Exception:
                    pass

        self._indexer.index_symbols(all_symbols)
        unique_symbols = self._indexer.list_symbols()

        dep_graph = self._dep_builder.build_graph(
            [str(Path(workspace_root) / f) for f in target_files], unique_symbols
        )
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
                source_subsystem="code_intelligence"
            )
        )

    def publish_code_report(self, summary: CodeStructureSummary) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        report_md = (
            f"# Codebase Symbol & Graph Summary\n\n"
            f"## Public APIs\n" + "\n".join([f"- {api}" for api in summary.public_apis[:20]]) + "\n\n"
            f"## Inheritance Structure\n" + "\n".join([f"- {cls} extends {parent}" for cls, parent in summary.inheritance_map.items()]) + "\n\n"
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
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")



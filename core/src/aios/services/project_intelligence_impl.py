import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional

from aios.services.project_intelligence import ProjectContext, ProjectIntelligenceService


class LocalProjectIntelligence(ProjectIntelligenceService):
    def __init__(self, cache_filename: str = ".aios_project_intelligence.json") -> None:
        self._cache_filename = cache_filename

    def initialize(self) -> None:
        pass

    def analyze_workspace(self, workspace_root: str) -> ProjectContext:
        root_path = Path(workspace_root).resolve()
        cache_path = root_path / self._cache_filename

        # Load cache
        cache = {}
        if cache_path.is_file():
            try:
                cache = json.loads(cache_path.read_text(encoding="utf-8"))
            except Exception:
                pass

        # Build Gitignore rules list
        gitignore_rules = self._load_gitignore_rules(root_path)

        # Ignores list
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

        todo_markers = []
        languages = {}
        structure = []
        total_files = 0
        total_folders = 0
        total_lines = 0

        # Scan directory tree
        new_cache = {}
        for current_root, dirs, files in os.walk(root_path):
            current_path = Path(current_root)
            rel_dir = current_path.relative_to(root_path)

            # Skip ignored root dirs
            parts = rel_dir.parts
            if parts and (any(p in default_ignores for p in parts) or any(self._is_ignored(str(rel_dir), gitignore_rules) for gitignore_rules in [gitignore_rules])):
                continue

            # Remove ignored directories in-place to avoid walking into them
            dirs[:] = [
                d
                for d in dirs
                if d not in default_ignores
                and not self._is_ignored(str(rel_dir / d), gitignore_rules)
            ]

            total_folders += len(dirs)

            for file in files:
                if file == self._cache_filename:
                    continue
                rel_file = rel_dir / file
                rel_file_str = str(rel_file)

                if self._is_ignored(rel_file_str, gitignore_rules):
                    continue

                total_files += 1
                file_path = current_path / file
                structure.append(rel_file_str)

                # Get extension for language counts
                ext = file_path.suffix.lower()
                if ext:
                    languages[ext] = languages.get(ext, 0) + 1

                # Incremental file scanning
                mtime = 0.0
                try:
                    mtime = file_path.stat().st_mtime
                except Exception:
                    pass

                cached_data = cache.get(rel_file_str)
                if cached_data and cached_data.get("mtime") == mtime:
                    # Cache hit!
                    todo_markers.extend(cached_data.get("todos", []))
                    total_lines += cached_data.get("lines", 0)
                    new_cache[rel_file_str] = cached_data
                else:
                    # Cache miss: analyze file
                    todos, lines = self._analyze_file(file_path, rel_file_str)
                    total_lines += lines
                    cached_entry = {"mtime": mtime, "todos": todos, "lines": lines}
                    todo_markers.extend(todos)
                    new_cache[rel_file_str] = cached_entry

        # Save cache back
        try:
            cache_path.write_text(json.dumps(new_cache, indent=2), encoding="utf-8")
        except Exception:
            pass

        # Detect package managers, build configs, frameworks, dependencies
        package_managers = []
        frameworks = []
        dependencies = []

        self._detect_project_configs(
            root_path, package_managers, frameworks, dependencies
        )

        # Retrieve git metadata
        git_branch, git_commits = self._get_git_metadata(workspace_root)

        # Count ADRs under docs/
        adr_count = 0
        docs_path = root_path / "docs"
        if docs_path.is_dir():
            adr_count = len(
                [f for f in docs_path.iterdir() if f.is_file() and "decision" in f.name.lower()]
            )

        # Set statistics
        statistics = {
            "total_files": total_files,
            "total_folders": total_folders,
            "total_lines": total_lines,
        }

        return ProjectContext(
            project_root=workspace_root,
            languages=languages,
            frameworks=frameworks,
            package_managers=package_managers,
            dependencies=dependencies,
            git_branch=git_branch,
            git_commits=git_commits,
            todo_markers=todo_markers,
            statistics=statistics,
            structure=structure,
            adr_count=adr_count,
        )

    def _load_gitignore_rules(self, root_path: Path) -> List[str]:
        rules = []
        gitignore = root_path / ".gitignore"
        if gitignore.is_file():
            try:
                for line in gitignore.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if line and not line.startswith("#"):
                        rules.append(line)
            except Exception:
                pass
        return rules

    def _is_ignored(self, path_str: str, rules: List[str]) -> bool:
        path_str = path_str.replace("\\", "/")
        for rule in rules:
            rule = rule.replace("\\", "/")
            if rule.endswith("/"):
                if path_str.startswith(rule) or f"/{rule}" in path_str:
                    return True
            else:
                if rule in path_str:
                    return True
        return False

    def _analyze_file(self, file_path: Path, rel_file_str: str) -> tuple[List[Dict[str, Any]], int]:
        todos = []
        lines_count = 0

        # Skip binary / large files
        try:
            if file_path.stat().st_size > 1 * 1024 * 1024:
                return [], 0

            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()
            lines_count = len(lines)

            for idx, line in enumerate(lines, 1):
                line_stripped = line.strip()
                if "TODO" in line or "FIXME" in line:
                    todos.append(
                        {
                            "file": rel_file_str,
                            "line": idx,
                            "text": line_stripped
                        }
                    )
        except Exception:
            pass

        return todos, lines_count

    def _detect_project_configs(
        self, root_path: Path, package_managers: List[str], frameworks: List[str], dependencies: List[str]
    ) -> None:
        # Node
        pkg_json = root_path / "package.json"
        if pkg_json.is_file():
            package_managers.append("npm/yarn")
            try:
                data = json.loads(pkg_json.read_text(encoding="utf-8"))
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                for dep in deps:
                    dependencies.append(dep)
                    if dep in ("react", "next", "vue", "angular", "vite", "webpack"):
                        frameworks.append(dep)
            except Exception:
                pass

        # Python Poetry/Pipenv
        pyproject = root_path / "pyproject.toml"
        if pyproject.is_file():
            package_managers.append("poetry/pip")
            try:
                content = pyproject.read_text(encoding="utf-8")
                for line in content.splitlines():
                    if "=" in line and not line.startswith("["):
                        dep = line.split("=")[0].strip()
                        if dep and dep not in ("name", "version", "description", "authors"):
                            dependencies.append(dep)
                            if dep in ("fastapi", "django", "flask", "pytest", "ruff"):
                                frameworks.append(dep)
            except Exception:
                pass

        # Rust Cargo
        cargo = root_path / "Cargo.toml"
        if cargo.is_file():
            package_managers.append("cargo")

        # Go modules
        go_mod = root_path / "go.mod"
        if go_mod.is_file():
            package_managers.append("go-modules")

    def _get_git_metadata(self, workspace_root: str) -> tuple[Optional[str], List[str]]:
        try:
            # Branch lookup
            res_branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=workspace_root,
                capture_output=True,
                text=True,
                shell=False
            )
            branch = res_branch.stdout.strip() if res_branch.returncode == 0 else None

            # Commits lookup
            res_commits = subprocess.run(
                ["git", "log", "-n", "5", "--oneline"],
                cwd=workspace_root,
                capture_output=True,
                text=True,
                shell=False
            )
            commits = (
                [line.strip() for line in res_commits.stdout.splitlines() if line.strip()]
                if res_commits.returncode == 0
                else []
            )

            return branch, commits
        except Exception:
            return None, []

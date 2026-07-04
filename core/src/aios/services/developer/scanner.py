import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional


class RepositoryScanner:
    def __init__(self, workspace_root: str) -> None:
        self.workspace_root = Path(workspace_root).resolve()

    def scan(self, max_depth: int = 3) -> Dict[str, Any]:
        git_branch = self._get_git_branch()
        git_status = self._get_git_status()
        git_commits = self._get_git_commits()
        git_diff = self._get_git_diff()
        git_diff_cached = self._get_git_diff_cached()
        dir_tree = self._get_dir_tree(self.workspace_root, max_depth=max_depth)
        readme = self._get_readme()

        # Language, framework, package manager detection
        config_files = self._get_important_configs()
        languages = self._detect_languages()
        pkg_manager, frameworks, build_system, test_framework = self._detect_ecosystem(config_files)

        return {
            "project_name": self.workspace_root.name,
            "repository_root": str(self.workspace_root),
            "git_branch": git_branch,
            "git_status": git_status,
            "git_diff": git_diff,
            "git_diff_cached": git_diff_cached,
            "last_commits": git_commits,
            "directory_tree": dir_tree,
            "readme": readme,
            "package_manager": pkg_manager,
            "languages": languages,
            "frameworks": frameworks,
            "build_system": build_system,
            "test_framework": test_framework,
            "config_files": [str(c.relative_to(self.workspace_root)) for c in config_files],
        }

    def _get_git_diff(self) -> Optional[str]:
        try:
            res = subprocess.run(
                ["git", "diff"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return res.stdout.strip()
        except Exception:
            return None

    def _get_git_diff_cached(self) -> Optional[str]:
        try:
            res = subprocess.run(
                ["git", "diff", "--cached"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return res.stdout.strip()
        except Exception:
            return None

    def _get_git_branch(self) -> Optional[str]:
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return res.stdout.strip()
        except Exception:
            return None

    def _get_git_status(self) -> Optional[str]:
        try:
            res = subprocess.run(
                ["git", "status"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return res.stdout.strip()
        except Exception:
            return None

    def _get_git_commits(self) -> List[str]:
        try:
            res = subprocess.run(
                ["git", "log", "-n", "10", "--oneline"],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                check=True,
            )
            return [line.strip() for line in res.stdout.strip().split("\n") if line.strip()]
        except Exception:
            return []

    def _get_dir_tree(self, path: Path, current_depth: int = 1, max_depth: int = 3) -> str:
        if current_depth > max_depth:
            return ""
        lines = []
        try:
            for item in sorted(path.iterdir()):
                if item.name.startswith(
                    (
                        ".",
                        "__pycache__",
                        "node_modules",
                        ".venv",
                        ".pytest_cache",
                        ".ruff_cache",
                        "egg-info",
                    )
                ):
                    continue
                indent = "  " * (current_depth - 1)
                if item.is_dir():
                    lines.append(f"{indent}└── {item.name}/")
                    sub_tree = self._get_dir_tree(item, current_depth + 1, max_depth)
                    if sub_tree:
                        lines.append(sub_tree)
                else:
                    lines.append(f"{indent}├── {item.name}")
        except Exception:
            pass
        return "\n".join(lines)

    def _get_readme(self) -> Optional[str]:
        for name in ["README.md", "readme.md", "README", "README.txt"]:
            path = self.workspace_root / name
            if path.is_file():
                try:
                    return path.read_text(encoding="utf-8")[:2000]  # Cap README size
                except Exception:
                    pass
        return None

    def _get_important_configs(self) -> List[Path]:
        configs = []
        config_names = {
            "pyproject.toml",
            "package.json",
            "tsconfig.json",
            "cargo.toml",
            "go.mod",
            "pom.xml",
            "build.gradle",
            "requirements.txt",
            "setup.py",
            "webpack.config.js",
            "vite.config.js",
            "docker-compose.yml",
        }
        try:
            # Check root and one level down
            for p in self.workspace_root.iterdir():
                if p.is_file() and p.name.lower() in config_names:
                    configs.append(p)
                elif p.is_dir() and not p.name.startswith("."):
                    try:
                        for sp in p.iterdir():
                            if sp.is_file() and sp.name.lower() in config_names:
                                configs.append(sp)
                    except Exception:
                        pass
        except Exception:
            pass
        return configs

    def _detect_languages(self) -> List[str]:
        extensions = {}
        ext_map = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".tsx": "TypeScript (React)",
            ".jsx": "JavaScript (React)",
            ".rs": "Rust",
            ".go": "Go",
            ".java": "Java",
            ".c": "C",
            ".cpp": "C++",
            ".html": "HTML",
            ".css": "CSS",
            ".toml": "TOML",
            ".json": "JSON",
            ".md": "Markdown",
            ".sh": "Shell",
        }
        try:
            for p in self.workspace_root.rglob("*"):
                if p.is_file():
                    if any(
                        part.startswith(
                            (
                                ".",
                                "__pycache__",
                                "node_modules",
                                ".venv",
                                ".pytest_cache",
                                ".ruff_cache",
                                "egg-info",
                            )
                        )
                        for part in p.parts
                    ):
                        continue
                    suffix = p.suffix.lower()
                    if suffix in ext_map:
                        lang = ext_map[suffix]
                        extensions[lang] = extensions.get(lang, 0) + 1
        except Exception:
            pass
        sorted_langs = sorted(extensions.items(), key=lambda x: x[1], reverse=True)
        return [lang for lang, count in sorted_langs[:5]]

    def _detect_ecosystem(
        self, configs: List[Path]
    ) -> tuple[Optional[str], List[str], Optional[str], Optional[str]]:
        pkg_manager = None
        frameworks = []
        build_system = None
        test_framework = None

        config_names = {c.name for c in configs}

        # Python
        if (
            "pyproject.toml" in config_names
            or "requirements.txt" in config_names
            or "setup.py" in config_names
        ):
            pkg_manager = "pip / poetry"
            build_system = "setuptools / poetry-core"
            test_framework = "pytest"
            for c in configs:
                if c.name == "pyproject.toml" or c.name == "requirements.txt":
                    try:
                        content = c.read_text(encoding="utf-8").lower()
                        if "django" in content:
                            frameworks.append("Django")
                        if "flask" in content:
                            frameworks.append("Flask")
                        if "fastapi" in content:
                            frameworks.append("FastAPI")
                        if "pytest" in content:
                            test_framework = "pytest"
                        if "unittest" in content:
                            test_framework = "unittest"
                    except Exception:
                        pass

        # Node/JS
        if "package.json" in config_names:
            pkg_manager = "npm / yarn / pnpm"
            build_system = "npm scripts"
            try:
                pjson_path = next(c for c in configs if c.name == "package.json")
                import json

                with open(pjson_path, "r", encoding="utf-8") as f:
                    pjson = json.load(f)
                deps = pjson.get("dependencies", {})
                dev_deps = pjson.get("devDependencies", {})
                all_deps = {**deps, **dev_deps}

                if "react" in all_deps:
                    frameworks.append("React")
                if "next" in all_deps:
                    frameworks.append("Next.js")
                if "vue" in all_deps:
                    frameworks.append("Vue")
                if "express" in all_deps:
                    frameworks.append("Express")
                if "jest" in all_deps:
                    test_framework = "jest"
                elif "vitest" in all_deps:
                    test_framework = "vitest"
                elif "mocha" in all_deps:
                    test_framework = "mocha"
            except Exception:
                pass

        # Rust
        if "cargo.toml" in config_names:
            pkg_manager = "cargo"
            build_system = "cargo build"
            test_framework = "cargo test"

        # Go
        if "go.mod" in config_names:
            pkg_manager = "go modules"
            build_system = "go build"
            test_framework = "go test"

        return pkg_manager, frameworks, build_system, test_framework

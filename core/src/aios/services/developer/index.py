import re
from pathlib import Path
from typing import Any, Dict, List


class CodeIndex:
    def __init__(self, workspace_root: str) -> None:
        self.workspace_root = Path(workspace_root).resolve()

    def index(self) -> Dict[str, Any]:
        source_dirs = self._find_directories(["src", "core/src", "app", "lib", "source"])
        test_dirs = self._find_directories(["tests", "test", "spec"])
        entry_points = self._find_entry_points()
        configs = self._find_configs()
        docs = self._find_docs()
        largest_files = self._find_largest_files()
        todos = self._find_todos_and_fixmes()

        return {
            "source_directories": source_dirs,
            "test_directories": test_dirs,
            "entry_points": entry_points,
            "configuration_files": configs,
            "documentation": docs,
            "largest_files": largest_files,
            "todos": todos,
        }

    def _find_directories(self, candidates: List[str]) -> List[str]:
        dirs = []
        for cand in candidates:
            p = self.workspace_root / cand
            if p.is_dir():
                dirs.append(str(p.relative_to(self.workspace_root)))
        return dirs

    def _find_entry_points(self) -> List[str]:
        entry_names = {
            "main.py",
            "cli.py",
            "app.py",
            "index.js",
            "app.js",
            "server.js",
            "index.ts",
            "main.go",
            "lib.rs",
            "main.rs",
        }
        entries = []
        try:
            for p in self.workspace_root.rglob("*"):
                if p.is_file() and p.name in entry_names:
                    if any(
                        part.startswith((".", "__pycache__", "node_modules", ".venv"))
                        for part in p.parts
                    ):
                        continue
                    entries.append(str(p.relative_to(self.workspace_root)))
        except Exception:
            pass
        return entries[:5]

    def _find_configs(self) -> List[str]:
        configs = []
        config_exts = {".toml", ".yaml", ".yml", ".json", ".ini", ".conf"}
        try:
            for p in self.workspace_root.iterdir():
                if (
                    p.is_file()
                    and p.suffix.lower() in config_exts
                    and p.name != "package-lock.json"
                ):
                    configs.append(str(p.relative_to(self.workspace_root)))
        except Exception:
            pass
        return configs

    def _find_docs(self) -> List[str]:
        docs = []
        try:
            for p in self.workspace_root.rglob("*.md"):
                if p.is_file():
                    if any(
                        part.startswith((".", "__pycache__", "node_modules", ".venv"))
                        for part in p.parts
                    ):
                        continue
                    docs.append(str(p.relative_to(self.workspace_root)))
        except Exception:
            pass
        return docs[:10]

    def _find_largest_files(self) -> List[Dict[str, Any]]:
        files = []
        try:
            for p in self.workspace_root.rglob("*"):
                if p.is_file():
                    if any(
                        part.startswith((".", "__pycache__", "node_modules", ".venv", ".git"))
                        for part in p.parts
                    ):
                        continue
                    files.append((p, p.stat().st_size))
        except Exception:
            pass
        files.sort(key=lambda x: x[1], reverse=True)
        return [
            {"path": str(f[0].relative_to(self.workspace_root)), "size_bytes": f[1]}
            for f in files[:5]
        ]

    def _find_todos_and_fixmes(self) -> List[Dict[str, Any]]:
        todos = []
        todo_pattern = re.compile(r"\b(TODO|FIXME)\b(.*)", re.IGNORECASE)
        valid_suffixes = {
            ".py",
            ".js",
            ".ts",
            ".rs",
            ".go",
            ".c",
            ".cpp",
            ".java",
            ".sh",
            ".toml",
            ".json",
            ".md",
        }
        try:
            for p in self.workspace_root.rglob("*"):
                if p.is_file() and p.suffix.lower() in valid_suffixes:
                    if any(
                        part.startswith((".", "__pycache__", "node_modules", ".venv", ".git"))
                        for part in p.parts
                    ):
                        continue
                    if p.stat().st_size > 100_000:
                        continue
                    try:
                        with open(p, "r", encoding="utf-8", errors="ignore") as f:
                            for idx, line in enumerate(f, 1):
                                match = todo_pattern.search(line)
                                if match:
                                    todos.append(
                                        {
                                            "file": str(p.relative_to(self.workspace_root)),
                                            "line_number": idx,
                                            "type": match.group(1).upper(),
                                            "comment": match.group(2).strip(),
                                        }
                                    )
                                    if len(todos) >= 30:
                                        return todos
                    except Exception:
                        pass
        except Exception:
            pass
        return todos

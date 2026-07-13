import os
from typing import Any, Dict, List, Optional


class RepositoryScanner:
    """Scans the AI OS codebase to identify packages, services, and configs."""

    def __init__(self, root_dir: str, exclude_patterns: Optional[List[str]] = None) -> None:
        self.root_dir = os.path.abspath(root_dir)
        self.exclude_patterns = exclude_patterns or [
            ".git",
            ".venv",
            "__pycache__",
            ".pytest_cache",
            "node_modules",
            "build",
            "dist",
            ".ruff_cache",
            "MagicMock",
            "temp",
        ]

    def scan(self) -> Dict[str, Any]:
        """Scans the repository and returns structural metadata."""
        results = {
            "packages": [],
            "modules": [],
            "services": [],
            "providers": [],
            "registries": [],
            "tests": [],
            "configuration_files": [],
            "documentation": [],
            "cli_commands": [],
        }

        for root, _dirs, files in os.walk(self.root_dir):
            # Skip excluded paths
            if any(pattern in root for pattern in self.exclude_patterns):
                continue

            rel_root = os.path.relpath(root, self.root_dir)
            if rel_root == ".":
                rel_root = ""

            # Detect packages
            if "__init__.py" in files:
                pkg_name = rel_root.replace(os.sep, ".")
                if pkg_name:
                    results["packages"].append(pkg_name)

            for file in files:
                file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(file_path, self.root_dir)

                # Skip files inside excluded paths
                if any(pattern in rel_file_path for pattern in self.exclude_patterns):
                    continue

                lower_file = file.lower()
                split_rel = rel_file_path.replace(os.sep, "/").split("/")

                # 1. Config files
                if file.endswith((".toml", ".yaml", ".yml", ".json", ".ini", ".conf")):
                    results["configuration_files"].append({"name": file, "path": rel_file_path})

                # 2. Documentation files
                elif file.endswith((".md", ".rst", ".txt")):
                    results["documentation"].append({"name": file, "path": rel_file_path})

                # 3. Python Modules and specific types
                elif file.endswith(".py"):
                    module_name = os.path.splitext(rel_file_path)[0].replace(os.sep, ".")
                    results["modules"].append(module_name)

                    # CLI commands detection
                    if "cli.py" in lower_file or "command" in split_rel:
                        results["cli_commands"].append({"name": file, "path": rel_file_path})

                    # Test suites detection
                    if file.startswith("test_") or "tests" in split_rel:
                        results["tests"].append({"name": file, "path": rel_file_path})

                    # Provider detection
                    elif "provider" in lower_file or "providers" in split_rel:
                        results["providers"].append({"name": file, "path": rel_file_path})

                    # Registry detection
                    elif "registry" in lower_file or "registries" in split_rel:
                        results["registries"].append({"name": file, "path": rel_file_path})

                    # Service detection
                    elif "service" in lower_file or "impl" in lower_file or "services" in split_rel:
                        results["services"].append({"name": file, "path": rel_file_path})

        return results

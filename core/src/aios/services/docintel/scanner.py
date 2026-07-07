import os
from typing import Any, Dict


class RepositoryScanner:
    """Scans the AI OS codebase to identify system components."""

    def __init__(self, root_dir: str) -> None:
        self.root_dir = os.path.abspath(root_dir)

    def scan(self) -> Dict[str, Any]:
        """Scans the repository and returns structural metadata."""
        results = {
            "packages": [],
            "modules": [],
            "services": [],
            "providers": [],
            "registries": [],
            "tests": []
        }

        exclude_dirs = [
            ".venv", ".git", "__pycache__", ".pytest_cache",
            ".ruff_cache", "MagicMock", "temp"
        ]

        for root, _dirs, files in os.walk(self.root_dir):
            # Skip virtualenv, git, and cache dirs
            if any(p in root for p in exclude_dirs):
                continue

            rel_root = os.path.relpath(root, self.root_dir)
            if rel_root == ".":
                rel_root = ""

            # Detect package
            if "__init__.py" in files:
                results["packages"].append(rel_root.replace(os.sep, "."))

            for file in files:
                if not file.endswith(".py"):
                    continue

                file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(file_path, self.root_dir)
                module_name = os.path.splitext(rel_file_path)[0].replace(os.sep, ".")

                results["modules"].append(module_name)

                # Detection rules based on file conventions
                if file.startswith("test_"):
                    results["tests"].append({
                        "name": file,
                        "path": rel_file_path
                    })
                elif "provider" in file or "providers" in root.replace(os.sep, "/").split("/"):
                    results["providers"].append({
                        "name": file,
                        "path": rel_file_path
                    })
                elif "registry" in file.lower() or "registries" in root.lower():
                    results["registries"].append({
                        "name": file,
                        "path": rel_file_path
                    })
                elif "service" in file.lower() or "impl" in file.lower():
                    results["services"].append({
                        "name": file,
                        "path": rel_file_path
                    })

        return results

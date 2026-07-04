from typing import Any, Dict


class WorkspaceSummary:
    def __init__(self, scan_results: Dict[str, Any], index_results: Dict[str, Any]) -> None:
        self.scan_results = scan_results
        self.index_results = index_results

    def generate(self) -> Dict[str, Any]:
        """
        Synthesizes scanner and indexer results into a clean, structured WorkspaceSummary.
        """
        modules = self.index_results.get("source_directories", [])

        tests = {
            "test_directories": self.index_results.get("test_directories", []),
            "test_framework": self.scan_results.get("test_framework"),
        }

        project = {
            "name": self.scan_results.get("project_name"),
            "repository_root": self.scan_results.get("repository_root"),
            "readme_preview": self.scan_results.get("readme")[:1000]
            if self.scan_results.get("readme")
            else None,
        }

        architecture = {
            "entry_points": self.index_results.get("entry_points", []),
            "build_system": self.scan_results.get("build_system"),
            "configuration_files": self.index_results.get("configuration_files", []),
        }

        recent_activity = self.scan_results.get("last_commits", [])

        git_status = {
            "branch": self.scan_results.get("git_branch"),
            "status": self.scan_results.get("git_status"),
        }

        dependencies = {
            "package_manager": self.scan_results.get("package_manager"),
            "config_files": self.scan_results.get("config_files", []),
        }

        return {
            "Project": project,
            "Languages": self.scan_results.get("languages", []),
            "Frameworks": self.scan_results.get("frameworks", []),
            "Architecture": architecture,
            "Modules": modules,
            "Dependencies": dependencies,
            "Tests": tests,
            "Git Status": git_status,
            "Recent Activity": recent_activity,
            "Open TODOs": self.index_results.get("todos", []),
        }

from typing import Any, Dict, List


class RepositoryAnalysis:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.project_name: str = data.get("project_name", "")
        self.repository_root: str = data.get("repository_root", "")
        self.git_branch: str = data.get("git_branch", "")
        self.git_status: str = data.get("git_status", "")
        self.git_diff: str = data.get("git_diff", "")
        self.git_diff_cached: str = data.get("git_diff_cached", "")
        self.last_commits: List[str] = data.get("last_commits", [])
        self.directory_tree: str = data.get("directory_tree", "")
        self.readme: str = data.get("readme", "")
        self.package_manager: str = data.get("package_manager", "")
        self.languages: List[str] = data.get("languages", [])
        self.frameworks: List[str] = data.get("frameworks", [])
        self.build_system: str = data.get("build_system", "")
        self.test_framework: str = data.get("test_framework", "")
        self.config_files: List[str] = data.get("config_files", [])

class RepositoryAnalyzer:
    def __init__(self, scanner_results: Dict[str, Any], index_results: Dict[str, Any]) -> None:
        self.scanner_results = scanner_results
        self.index_results = index_results

    def analyze(self) -> RepositoryAnalysis:
        merged = {**self.scanner_results, **self.index_results}
        return RepositoryAnalysis(merged)

from typing import Any, Dict


class ContextRanker:
    def __init__(self) -> None:
        pass

    def select_context(
        self, action: str, query: str, full_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        action_lower = action.lower()
        query_lower = query.lower()

        selected = {
            "project_name": full_analysis.get("project_name", ""),
            "repository_root": full_analysis.get("repository_root", ""),
            "git_branch": full_analysis.get("git_branch", ""),
            "package_manager": full_analysis.get("package_manager", ""),
            "languages": full_analysis.get("languages", []),
            "frameworks": full_analysis.get("frameworks", []),
            "build_system": full_analysis.get("build_system", ""),
            "test_framework": full_analysis.get("test_framework", ""),
        }

        # 1. Directory Tree
        if "repository" in action_lower or "analyze" in action_lower:
            selected["directory_tree"] = full_analysis.get("directory_tree", "")
        else:
            tree = full_analysis.get("directory_tree", "")
            lines = tree.split("\n")
            if len(lines) > 20:
                selected["directory_tree"] = (
                    "\n".join(lines[:20]) + "\n... (truncated for context focus)"
                )
            else:
                selected["directory_tree"] = tree

        # 2. Git Status and Git Diff
        git_keywords = ["git", "diff", "commit", "release", "security", "change", "review"]
        if any(kw in action_lower or kw in query_lower for kw in git_keywords):
            selected["git_status"] = full_analysis.get("git_status", "")
            selected["git_diff"] = full_analysis.get("git_diff", "")
            selected["git_diff_cached"] = full_analysis.get("git_diff_cached", "")
            selected["last_commits"] = full_analysis.get("last_commits", [])
        else:
            selected["git_status"] = "Omitted for context focus."
            selected["git_diff"] = "Omitted for context focus."
            selected["git_diff_cached"] = "Omitted for context focus."
            selected["last_commits"] = full_analysis.get("last_commits", [])[:3]

        # 3. TODOs
        todo_keywords = ["todo", "fixme", "smell", "repository", "quality"]
        if any(kw in action_lower or kw in query_lower for kw in todo_keywords):
            selected["open_todos"] = full_analysis.get("open_todos", "")
        else:
            selected["open_todos"] = "Omitted for context focus."

        return selected

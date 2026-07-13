"""
GitHub Report Generator — Sprint 25.

Writes markdown documentation files under docs/github/:
  - repository_summary.md
  - pull_request_report.md
  - issue_report.md
  - branch_report.md
  - release_report.md
  - actions_report.md
"""

import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class GitHubReportGenerator:
    """Generates docs/github/ markdown reports from GitHub Intelligence data."""

    def __init__(self, output_dir: str = "docs/github") -> None:
        self._dir = Path(output_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

    def _write(self, filename: str, content: str) -> None:
        (self._dir / filename).write_text(content, encoding="utf-8")

    # ── Individual reports ───────────────────────────────────────────────────

    def write_repository_summary(
        self,
        repo: Dict[str, Any],
        ai_summary: Optional[str] = None,
    ) -> None:
        lines = [
            f"# Repository Summary — {repo.get('owner', '')}/{repo.get('name', '')}",
            "",
            f"- **Description**: {repo.get('description') or 'N/A'}",
            f"- **URL**: {repo.get('url', 'N/A')}",
            f"- **Stars**: {repo.get('stars', 0)}",
            f"- **Forks**: {repo.get('forks', 0)}",
            f"- **Open Issues**: {repo.get('open_issues_count', 0)}",
            f"- **Languages**: {', '.join(repo.get('languages', [])) or 'N/A'}",
            f"- **Private**: {repo.get('is_private', False)}",
            "",
            "## AI Summary",
            "",
            ai_summary or "_Not generated._",
            "",
            f"_Generated at {time.ctime()}_",
        ]
        self._write("repository_summary.md", "\n".join(lines))

    def write_pull_request_report(self, prs: List[Dict[str, Any]]) -> None:
        lines = [
            "# Pull Request Report",
            "",
            f"- **Total PRs Listed**: {len(prs)}",
            "",
            "| # | Title | State | Author | URL |",
            "|---|---|---|---|---|",
        ]
        for pr in prs[:50]:
            lines.append(
                f"| {pr.get('number', '')} "
                f"| {pr.get('title', '')} "
                f"| {pr.get('state', '')} "
                f"| {pr.get('user', '')} "
                f"| {pr.get('url', '')} |"
            )
        lines += ["", f"_Generated at {time.ctime()}_"]
        self._write("pull_request_report.md", "\n".join(lines))

    def write_issue_report(self, issues: List[Dict[str, Any]]) -> None:
        lines = [
            "# Issue Report",
            "",
            f"- **Total Issues Listed**: {len(issues)}",
            "",
            "| # | Title | State | Labels | Author |",
            "|---|---|---|---|---|",
        ]
        for issue in issues[:50]:
            labels = ", ".join(issue.get("labels", []))
            lines.append(
                f"| {issue.get('number', '')} "
                f"| {issue.get('title', '')} "
                f"| {issue.get('state', '')} "
                f"| {labels} "
                f"| {issue.get('user', '')} |"
            )
        lines += ["", f"_Generated at {time.ctime()}_"]
        self._write("issue_report.md", "\n".join(lines))

    def write_branch_report(self, branches: List[Dict[str, Any]]) -> None:
        lines = [
            "# Branch Report",
            "",
            f"- **Total Branches**: {len(branches)}",
            "",
            "| Branch | SHA |",
            "|---|---|",
        ]
        for branch in branches:
            lines.append(f"| {branch.get('name', '')} | {branch.get('sha', '')} |")
        lines += ["", f"_Generated at {time.ctime()}_"]
        self._write("branch_report.md", "\n".join(lines))

    def write_release_report(self, releases: List[Dict[str, Any]]) -> None:
        lines = [
            "# Release Report",
            "",
            f"- **Total Releases**: {len(releases)}",
            "",
            "| Tag | Name | Created At |",
            "|---|---|---|",
        ]
        for r in releases:
            lines.append(
                f"| {r.get('tag_name', '')} | {r.get('name', '')} | {r.get('created_at', '')} |"
            )
        lines += ["", f"_Generated at {time.ctime()}_"]
        self._write("release_report.md", "\n".join(lines))

    def write_actions_report(
        self, workflows: List[Dict[str, Any]], ai_summary: Optional[str] = None
    ) -> None:
        lines = [
            "# GitHub Actions Report",
            "",
            f"- **Total Runs Listed**: {len(workflows)}",
            "",
            "| Run ID | Name | Status | Conclusion |",
            "|---|---|---|---|",
        ]
        for w in workflows[:50]:
            lines.append(
                f"| {w.get('id', '')} "
                f"| {w.get('name', '')} "
                f"| {w.get('status', '')} "
                f"| {w.get('conclusion') or 'pending'} |"
            )
        lines += [
            "",
            "## AI Health Summary",
            "",
            ai_summary or "_Not generated._",
            "",
            f"_Generated at {time.ctime()}_",
        ]
        self._write("actions_report.md", "\n".join(lines))

    # ── Bulk generation ──────────────────────────────────────────────────────

    def generate_all(
        self,
        repo: Dict[str, Any],
        prs: List[Dict[str, Any]],
        issues: List[Dict[str, Any]],
        branches: List[Dict[str, Any]],
        releases: List[Dict[str, Any]],
        workflows: List[Dict[str, Any]],
        ai_repo_summary: Optional[str] = None,
        ai_actions_summary: Optional[str] = None,
    ) -> None:
        self.write_repository_summary(repo, ai_repo_summary)
        self.write_pull_request_report(prs)
        self.write_issue_report(issues)
        self.write_branch_report(branches)
        self.write_release_report(releases)
        self.write_actions_report(workflows, ai_actions_summary)

"""
GitHub Intelligence Engine — Sprint 25.

Builds on top of LocalGitHubService (from aios.services.github_impl) and
adds intelligence-layer methods for:
  - Repository summarisation
  - PR summary generation
  - Issue summarisation
  - Commit message generation
  - Changelog / release notes generation
  - Actions workflow summarisation
  - Branch comparison intelligence

All AI calls are routed through the existing ModelService / OmniRoute layer.
Memory is persisted via GitHubMemory.
"""

import logging
from typing import Any, Dict, List, Optional

from aios.github.connection import GitHubConnectionManager
from aios.github.memory import GitHubMemory
from aios.services.github import (
    GitHubBranch,
    GitHubCommit,
    GitHubIssue,
    GitHubPullRequest,
    GitHubRelease,
    GitHubRepository,
    GitHubWorkflow,
)
from aios.services.github_impl import LocalGitHubService
from aios.services.model import LLMRequest, ModelService

logger = logging.getLogger(__name__)


class GitHubIntelligenceEngine:
    """Orchestrates GitHub API access, memory caching, and AI summaries."""

    def __init__(
        self,
        model_service: ModelService,
        token: Optional[str] = None,
        cache_dir: Optional[str] = None,
    ) -> None:
        self.conn = GitHubConnectionManager(token=token)
        self.memory = GitHubMemory(cache_dir=cache_dir)
        self._svc = LocalGitHubService(model_service=model_service, token=token)
        self._model = model_service

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _llm(self, prompt: str, system: str = "You are an expert software engineer.") -> str:
        try:
            res = self._model.execute_request(LLMRequest(prompt=prompt, system_instruction=system))
            return res.content
        except Exception as e:
            logger.warning(f"LLM call failed: {e}")
            return f"[AI summary unavailable: {e}]"

    # ── Repository Intelligence ──────────────────────────────────────────────

    def inspect_repository(self, repo_name: str) -> GitHubRepository:
        repo = self._svc.inspect_repository(repo_name)
        self.memory.save_repo(
            repo_name,
            {
                "owner": repo.owner,
                "name": repo.name,
                "description": repo.description,
                "stars": repo.stars,
                "forks": repo.forks,
                "languages": repo.languages,
                "url": repo.url,
                "is_private": repo.is_private,
                "open_issues_count": repo.open_issues_count,
            },
        )
        return repo

    def generate_repo_summary(self, repo_name: str) -> str:
        repo = self.inspect_repository(repo_name)
        prompt = (
            f"Repository: {repo.owner}/{repo.name}\n"
            f"Description: {repo.description}\n"
            f"Stars: {repo.stars} | Forks: {repo.forks} | Open Issues: {repo.open_issues_count}\n"
            f"Languages: {', '.join(repo.languages) or 'N/A'}\n\n"
            "Write a concise 3-5 sentence executive summary of this repository."
        )
        return self._llm(prompt, "You are a technical writer summarising open-source projects.")

    # ── Branch Intelligence ──────────────────────────────────────────────────

    def list_branches(self, repo_name: str) -> List[GitHubBranch]:
        branches = self._svc.list_branches(repo_name)
        self.memory.save_branches(repo_name, [{"name": b.name, "sha": b.sha} for b in branches])
        return branches

    def compare_branches(self, repo_name: str, base: str, head: str) -> str:
        """Return a diff string between two branches."""
        try:
            return self._svc.get_diff(repo_name, base, head)
        except Exception as e:
            return f"Could not compare branches: {e}"

    # ── Commit Intelligence ──────────────────────────────────────────────────

    def get_commit_history(
        self, repo_name: str, branch: Optional[str] = None, limit: int = 20
    ) -> List[GitHubCommit]:
        return self._svc.get_commit_history(repo_name, branch)[:limit]

    def generate_commit_message(self, diff_snippet: str) -> str:
        prompt = (
            f"Given this code diff:\n\n{diff_snippet[:3000]}\n\n"
            "Generate a concise conventional commit message (type: scope: description). "
            "Use one of: feat, fix, refactor, docs, test, chore, perf."
        )
        return self._llm(prompt, "You are a senior developer writing git commit messages.")

    def explain_commit_history(self, repo_name: str, branch: Optional[str] = None) -> str:
        return self._svc.explain_commit_history(repo_name, branch)

    # ── Pull Request Intelligence ────────────────────────────────────────────

    def list_pull_requests(self, repo_name: str, state: str = "open") -> List[Dict[str, Any]]:
        try:
            from aios.source_control.github_provider import GitHubProvider

            gh = GitHubProvider(token=self.conn._token)
            res = gh._request("GET", f"/repos/{repo_name}/pulls", params={"state": state})
            prs = res.json()
            simplified = [
                {
                    "number": p["number"],
                    "title": p["title"],
                    "state": p["state"],
                    "user": p["user"]["login"],
                    "url": p["html_url"],
                    "created_at": p.get("created_at", ""),
                }
                for p in prs
            ]
            self.memory.save_prs(repo_name, simplified)
            return simplified
        except Exception as e:
            logger.warning(f"list_pull_requests failed: {e}")
            return self.memory.load_prs(repo_name)

    def inspect_pull_request(self, repo_name: str, pr_number: int) -> GitHubPullRequest:
        return self._svc.inspect_pull_request(repo_name, pr_number)

    def generate_pr_summary(self, repo_name: str, pr_number: int) -> str:
        return self._svc.review_pr(repo_name, pr_number)

    # ── Issue Intelligence ───────────────────────────────────────────────────

    def list_issues(self, repo_name: str, state: str = "open") -> List[Dict[str, Any]]:
        try:
            from aios.source_control.github_provider import GitHubProvider

            gh = GitHubProvider(token=self.conn._token)
            res = gh._request("GET", f"/repos/{repo_name}/issues", params={"state": state})
            issues = res.json()
            simplified = [
                {
                    "number": i["number"],
                    "title": i["title"],
                    "state": i["state"],
                    "user": i["user"]["login"],
                    "labels": [lb["name"] for lb in i.get("labels", [])],
                    "created_at": i.get("created_at", ""),
                }
                for i in issues
                if "pull_request" not in i  # exclude PRs from issue list
            ]
            self.memory.save_issues(repo_name, simplified)
            return simplified
        except Exception as e:
            logger.warning(f"list_issues failed: {e}")
            return self.memory.load_issues(repo_name)

    def inspect_issue(self, repo_name: str, issue_number: int) -> GitHubIssue:
        return self._svc.inspect_issue(repo_name, issue_number)

    # ── Release Intelligence ─────────────────────────────────────────────────

    def get_release_history(self, repo_name: str) -> List[GitHubRelease]:
        releases = self._svc.get_release_history(repo_name)
        self.memory.save_releases(
            repo_name,
            [
                {
                    "tag_name": r.tag_name,
                    "name": r.name,
                    "body": r.body,
                    "created_at": r.created_at,
                }
                for r in releases
            ],
        )
        return releases

    def generate_changelog(self, repo_name: str, since_tag: Optional[str] = None) -> str:
        commits = self.get_commit_history(repo_name)
        releases = self.get_release_history(repo_name)
        commits_str = "\n".join(f"- {c.sha[:7]} {c.message} ({c.author})" for c in commits[:25])
        releases_str = "\n".join(f"- {r.tag_name}: {r.name}" for r in releases[:5])
        prompt = (
            f"Repository: {repo_name}\n\n"
            f"Recent Commits:\n{commits_str}\n\n"
            f"Recent Releases:\n{releases_str}\n\n"
            "Generate a professional CHANGELOG in Keep a Changelog format "
            "for the next release, grouping changes as Added, Changed, Fixed, Removed."
        )
        return self._llm(prompt, "You are a release engineer writing changelogs.")

    # ── GitHub Actions Intelligence ──────────────────────────────────────────

    def get_workflow_status(self, repo_name: str) -> List[GitHubWorkflow]:
        workflows = self._svc.get_workflow_status(repo_name)
        self.memory.save_workflows(
            repo_name,
            [
                {
                    "id": w.id,
                    "name": w.name,
                    "state": w.state,
                    "status": w.status,
                    "conclusion": w.conclusion,
                }
                for w in workflows
            ],
        )
        return workflows

    def summarise_actions(self, repo_name: str) -> str:
        workflows = self.get_workflow_status(repo_name)
        summary_lines = [
            f"- #{w.id} {w.name}: status={w.status} conclusion={w.conclusion or 'pending'}"
            for w in workflows[:15]
        ]
        prompt = (
            f"GitHub Actions run history for {repo_name}:\n"
            + "\n".join(summary_lines)
            + "\n\nSummarise the CI/CD health, highlight failures, and suggest fixes."
        )
        return self._llm(prompt, "You are a DevOps engineer analysing CI pipeline health.")

    # ── Full Repository Summary ──────────────────────────────────────────────

    def full_summary(self, repo_name: str) -> str:
        return self._svc.review_repository(repo_name)

import base64
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

import httpx

from aios.services.developer_workspace import DeveloperWorkspaceService
from aios.services.github import (
    GitHubAuthentication,
    GitHubBranch,
    GitHubCache,
    GitHubCommit,
    GitHubContext,
    GitHubIssue,
    GitHubPullRequest,
    GitHubRelease,
    GitHubRepository,
    GitHubService,
    GitHubWorkflow,
)
from aios.services.model import LLMRequest, ModelService
from aios.services.project_intelligence import ProjectIntelligenceService

logger = logging.getLogger(__name__)


class LocalGitHubService(GitHubService):
    """Concrete implementation of GitHubService providing repository metadata and AI analyses."""

    def __init__(
        self,
        model_service: ModelService,
        project_intel: Optional[ProjectIntelligenceService] = None,
        dev_workspace: Optional[DeveloperWorkspaceService] = None,
        token: Optional[str] = None,
        base_url: str = "https://api.github.com",
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit_per_min: int = 60,
        cache_enabled: bool = True,
        offline_mode: bool = False,
    ) -> None:
        self._model_service = model_service
        self._project_intel = project_intel
        self._dev_workspace = dev_workspace
        self._registry = None

        # Load token prioritizing explicit parameter, then GITHUB_TOKEN / GITHUB_PAT env vars
        self._token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PAT")
        self._auth = GitHubAuthentication(token=self._token)
        self._cache = GitHubCache()
        self._context = GitHubContext(auth=self._auth)

        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_retries = max_retries
        self._rate_limit_per_min = rate_limit_per_min
        self._cache_enabled = cache_enabled
        self._offline_mode = offline_mode

        # Rate limiting state
        self._last_request_time = 0.0
        self._request_interval = 60.0 / rate_limit_per_min if rate_limit_per_min > 0 else 0.0

    def initialize(self) -> None:
        logger.info("Initializing LocalGitHubService")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def _parse_repo_name(self, repo_name: str) -> tuple[str, str]:
        """Normalize repo name from potential URLs or full paths."""
        if "/" in repo_name:
            if "github.com/" in repo_name:
                repo_name = repo_name.split("github.com/")[-1]
            parts = [p.strip() for p in repo_name.split("/") if p.strip()]
            if len(parts) >= 2:
                return parts[-2], parts[-1]
        return "owner", repo_name

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
    ) -> Any:
        if hasattr(self, "_registry") and self._registry:
            try:
                from aios.source_control import SourceControlService
                sc_service = self._registry.get(SourceControlService)
                gh_provider = sc_service.registry.get_provider("github")
                res = gh_provider._request(method, f"/{path.lstrip('/')}", params=params, json=json_data)
                content_type = res.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    return res.json()
                return res.text
            except Exception as e:
                logger.warning(f"SourceControlService delegation failed, falling back to legacy request: {e}")

        cache_key = f"{method}:{path}:{json.dumps(params or {})}:{json.dumps(json_data or {})}"

        # Caching check for GET
        if method == "GET" and self._cache_enabled:
            cached = self._cache.get(cache_key)
            if cached is not None:
                logger.info(f"GitHub cache hit for path: {path}")
                return cached

        # Offline Mode handling
        if self._offline_mode:
            if method == "GET" and self._cache_enabled:
                cached = self._cache.get(cache_key)
                if cached is not None:
                    return cached
            raise httpx.ConnectError("Offline mode enabled. GitHub API request blocked.")

        # Rate limiting sleep
        if self._request_interval > 0.0:
            current = time.time()
            elapsed = current - self._last_request_time
            if elapsed < self._request_interval:
                time.sleep(self._request_interval - elapsed)
            self._last_request_time = time.time()

        url = f"{self._base_url}/{path.lstrip('/')}"
        headers = self._auth.get_headers()

        last_exception = None
        for attempt in range(self._max_retries):
            try:
                logger.info(f"GitHub API call attempt {attempt + 1}/{self._max_retries}: {method} {path}")
                with httpx.Client(timeout=float(self._timeout)) as client:
                    if method == "GET":
                        res = client.get(url, headers=headers, params=params)
                    elif method == "POST":
                        res = client.post(url, headers=headers, json=json_data)
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")

                # Handle transient errors
                if res.status_code in (429, 500, 502, 503, 504):
                    logger.warning(f"Transient HTTP error {res.status_code} received on attempt {attempt + 1}")
                    time.sleep(2**attempt)
                    continue

                if res.status_code not in (200, 201):
                    raise Exception(f"GitHub API returned error {res.status_code}: {res.text}")

                # Parse JSON or text
                content_type = res.headers.get("Content-Type", "")
                if "application/json" in content_type:
                    result = res.json()
                else:
                    result = res.text

                # Save cache for GET requests
                if method == "GET" and self._cache_enabled:
                    self._cache.set(cache_key, result)

                return result

            except (httpx.TimeoutException, httpx.NetworkError) as e:
                logger.warning(f"GitHub connection error on attempt {attempt + 1}: {e}")
                last_exception = e
                time.sleep(2**attempt)

        if last_exception:
            raise last_exception
        raise Exception(f"GitHub API request failed after {self._max_retries} attempts.")

    def inspect_repository(self, repo_name: str) -> GitHubRepository:
        owner, repo = self._parse_repo_name(repo_name)
        data = self._request("GET", f"repos/{owner}/{repo}")
        
        # Optionally try to get languages
        languages_list = []
        try:
            langs_dict = self._request("GET", f"repos/{owner}/{repo}/languages")
            if isinstance(langs_dict, dict):
                languages_list = list(langs_dict.keys())
        except Exception:
            pass

        return GitHubRepository(
            owner=data["owner"]["login"],
            name=data["name"],
            description=data.get("description"),
            stars=data.get("stargazers_count", 0),
            forks=data.get("forks_count", 0),
            languages=languages_list,
            url=data.get("html_url", ""),
            is_private=data.get("private", False),
            open_issues_count=data.get("open_issues_count", 0),
        )

    def list_branches(self, repo_name: str) -> List[GitHubBranch]:
        owner, repo = self._parse_repo_name(repo_name)
        data = self._request("GET", f"repos/{owner}/{repo}/branches")
        return [
            GitHubBranch(name=b["name"], sha=b["commit"]["sha"])
            for b in data
        ]

    def create_branch(self, repo_name: str, branch_name: str, target_sha: str) -> GitHubBranch:
        owner, repo = self._parse_repo_name(repo_name)
        payload = {
            "ref": f"refs/heads/{branch_name}",
            "sha": target_sha,
        }
        self._request("POST", f"repos/{owner}/{repo}/git/refs", json_data=payload)
        return GitHubBranch(name=branch_name, sha=target_sha)

    def inspect_pull_request(self, repo_name: str, pr_number: int) -> GitHubPullRequest:
        owner, repo = self._parse_repo_name(repo_name)
        data = self._request("GET", f"repos/{owner}/{repo}/pulls/{pr_number}")
        return GitHubPullRequest(
            number=data["number"],
            title=data["title"],
            state=data["state"],
            body=data.get("body"),
            user=data["user"]["login"],
            html_url=data.get("html_url", ""),
            diff_url=data.get("diff_url", ""),
            created_at=data.get("created_at", ""),
        )

    def inspect_issue(self, repo_name: str, issue_number: int) -> GitHubIssue:
        owner, repo = self._parse_repo_name(repo_name)
        data = self._request("GET", f"repos/{owner}/{repo}/issues/{issue_number}")
        
        labels_list = []
        if "labels" in data:
            labels_list = [label["name"] for label in data["labels"]]
            
        milestone_title = None
        if data.get("milestone"):
            milestone_title = data["milestone"]["title"]

        return GitHubIssue(
            number=data["number"],
            title=data["title"],
            state=data["state"],
            body=data.get("body"),
            user=data["user"]["login"],
            labels=labels_list,
            milestone=milestone_title,
            created_at=data.get("created_at", ""),
        )

    def get_commit_history(self, repo_name: str, branch: Optional[str] = None) -> List[GitHubCommit]:
        owner, repo = self._parse_repo_name(repo_name)
        params = {}
        if branch:
            params["sha"] = branch
        data = self._request("GET", f"repos/{owner}/{repo}/commits", params=params)
        
        commits = []
        for c in data:
            commit_info = c["commit"]
            commits.append(
                GitHubCommit(
                    sha=c["sha"],
                    author=commit_info["author"]["name"],
                    message=commit_info["message"],
                    date=commit_info["author"]["date"],
                    url=c.get("html_url", ""),
                )
            )
        return commits

    def get_release_history(self, repo_name: str) -> List[GitHubRelease]:
        owner, repo = self._parse_repo_name(repo_name)
        data = self._request("GET", f"repos/{owner}/{repo}/releases")
        return [
            GitHubRelease(
                tag_name=r["tag_name"],
                name=r["name"],
                body=r.get("body"),
                created_at=r.get("created_at", ""),
            )
            for r in data
        ]

    def get_workflow_status(self, repo_name: str) -> List[GitHubWorkflow]:
        owner, repo = self._parse_repo_name(repo_name)
        data = self._request("GET", f"repos/{owner}/{repo}/actions/runs")
        runs = data.get("workflow_runs", [])
        return [
            GitHubWorkflow(
                id=run["id"],
                name=run.get("name", "workflow"),
                state=run.get("status", ""),
                status=run.get("status", ""),
                conclusion=run.get("conclusion"),
            )
            for run in runs
        ]

    def get_repository_stats(self, repo_name: str) -> Dict[str, Any]:
        owner, repo = self._parse_repo_name(repo_name)
        data = self._request("GET", f"repos/{owner}/{repo}")
        return {
            "stars": data.get("stargazers_count", 0),
            "forks": data.get("forks_count", 0),
            "open_issues": data.get("open_issues_count", 0),
            "subscribers": data.get("subscribers_count", 0),
        }

    def search_repositories(self, query: str) -> List[GitHubRepository]:
        data = self._request("GET", "search/repositories", params={"q": query})
        items = data.get("items", [])
        return [
            GitHubRepository(
                owner=item["owner"]["login"],
                name=item["name"],
                description=item.get("description"),
                stars=item.get("stargazers_count", 0),
                forks=item.get("forks_count", 0),
                languages=[],
                url=item.get("html_url", ""),
                is_private=item.get("private", False),
                open_issues_count=item.get("open_issues_count", 0),
            )
            for item in items
        ]

    def get_repository_metadata(self, repo_name: str) -> Dict[str, Any]:
        owner, repo = self._parse_repo_name(repo_name)
        return self._request("GET", f"repos/{owner}/{repo}")

    def get_diff(self, repo_name: str, base: str, head: str) -> str:
        owner, repo = self._parse_repo_name(repo_name)
        # Using Compare branch API for diff output format
        headers = self._auth.get_headers()
        headers["Accept"] = "application/vnd.github.diff"
        
        # Note: self._request wraps headers differently, so we manually call it or custom implement
        url = f"{self._base_url}/repos/{owner}/{repo}/compare/{base}...{head}"
        if self._offline_mode:
            raise httpx.ConnectError("Offline mode enabled. Cannot get branch diff.")

        with httpx.Client(timeout=float(self._timeout)) as client:
            res = client.get(url, headers=headers)
            if res.status_code == 200:
                return res.text
            raise Exception(f"Failed to fetch branch comparison: {res.status_code}")

    def get_file(self, repo_name: str, path: str, ref: Optional[str] = None) -> str:
        owner, repo = self._parse_repo_name(repo_name)
        params = {}
        if ref:
            params["ref"] = ref
        data = self._request("GET", f"repos/{owner}/{repo}/contents/{path}", params=params)
        
        if isinstance(data, dict) and data.get("encoding") == "base64":
            content_bytes = base64.b64decode(data["content"])
            return content_bytes.decode("utf-8", errors="ignore")
        return str(data)

    def get_readme(self, repo_name: str) -> str:
        owner, repo = self._parse_repo_name(repo_name)
        data = self._request("GET", f"repos/{owner}/{repo}/readme")
        
        if isinstance(data, dict) and data.get("encoding") == "base64":
            content_bytes = base64.b64decode(data["content"])
            return content_bytes.decode("utf-8", errors="ignore")
        return str(data)

    def get_contributors(self, repo_name: str) -> List[Dict[str, Any]]:
        owner, repo = self._parse_repo_name(repo_name)
        data = self._request("GET", f"repos/{owner}/{repo}/contributors")
        return [
            {"login": c["login"], "contributions": c["contributions"]}
            for c in data
        ]

    def get_labels(self, repo_name: str) -> List[str]:
        owner, repo = self._parse_repo_name(repo_name)
        data = self._request("GET", f"repos/{owner}/{repo}/labels")
        return [label["name"] for label in data]

    def get_milestones(self, repo_name: str) -> List[Dict[str, Any]]:
        owner, repo = self._parse_repo_name(repo_name)
        data = self._request("GET", f"repos/{owner}/{repo}/milestones")
        return [
            {
                "id": m["id"],
                "title": m["title"],
                "state": m["state"],
                "description": m.get("description"),
            }
            for m in data
        ]


    # AI OS Intelligence methods
    def review_repository(self, repo_name: str) -> str:
        repo = self.inspect_repository(repo_name)
        readme = ""
        try:
            readme = self.get_readme(repo_name)
        except Exception:
            readme = "No README file found."

        root_contents = []
        try:
            owner, repo_base = self._parse_repo_name(repo_name)
            contents = self._request("GET", f"repos/{owner}/{repo_base}/contents")
            root_contents = [c["name"] for c in contents]
        except Exception:
            pass

        # Combine Repository Metadata + Local Project Intelligence + Developer Workspace info if relevant
        local_intel_str = ""
        if self._project_intel:
            try:
                # Use current workspace context if it relates to the same repo
                ctx = self._project_intel.analyze_workspace(".")
                local_intel_str = (
                    f"\nLocal Workspace Languages: {ctx.languages}\n"
                    f"Local Frameworks: {ctx.frameworks}\n"
                )
            except Exception:
                pass

        workspace_info_str = ""
        if self._dev_workspace:
            try:
                info = self._dev_workspace.get_workspace_info(".")
                workspace_info_str = f"\nGit Status:\n{info.git_status}\n"
            except Exception:
                pass

        prompt = (
            f"You are a Lead Software Architect analyzing the repository: {repo.owner}/{repo.name}.\n\n"
            f"Description: {repo.description}\n"
            f"Stars: {repo.stars} | Forks: {repo.forks}\n"
            f"Primary Languages: {repo.languages}\n"
            f"Root files/folders: {root_contents}\n"
            f"{local_intel_str}"
            f"{workspace_info_str}"
            f"README Content Snippet:\n{readme[:3000]}\n\n"
            "Please perform a deep repository review and generate a report on:\n"
            "1. Architecture Analysis (Identify folder layout, design patterns)\n"
            "2. Framework Detection (What technologies/frameworks are used?)\n"
            "3. Explanations of core files and folders structure\n"
            "4. Technical risks, security flaws, or code quality risks\n"
            "5. Recommendations for architecture improvements\n"
            "6. Brief overall project summary"
        )

        res = self._model_service.execute_request(
            LLMRequest(
                prompt=prompt,
                system_instruction="You are a strict, expert software architect. Deliver clear, actionable reviews.",
                model_name="claude-3-5-sonnet",
            )
        )
        return res.content

    def review_pr(self, repo_name: str, pr_number: int) -> str:
        pr = self.inspect_pull_request(repo_name, pr_number)
        
        diff = ""
        try:
            diff = self.get_diff(repo_name, f"pull/{pr_number}/merge", f"pull/{pr_number}/head")
        except Exception:
            try:
                # Fallback to get_diff using the PR diff url or comparable logic
                diff = self.get_diff(repo_name, "main", "dev") # generic fallback if base/head unknown
            except Exception:
                diff = "No diff available."

        prompt = (
            f"You are a Senior Software Engineer conducting a pull request review for: {repo_name} PR #{pr_number}.\n\n"
            f"PR Title: {pr.title}\n"
            f"PR Description:\n{pr.body or 'No description provided.'}\n\n"
            f"PR Code Diff:\n{diff[:5000]}\n\n"
            "Please review the changes and output:\n"
            "1. Summary of Changes (List key features/bugfixes)\n"
            "2. Risk Assessment (Evaluate overall risk score, e.g. Low/Medium/High, and explain)\n"
            "3. Detected Breaking Changes (Any API, config, or DB schema alterations)\n"
            "4. Suggested Code Quality & Style Improvements\n"
            "5. Specific review comments or warnings"
        )

        res = self._model_service.execute_request(
            LLMRequest(
                prompt=prompt,
                system_instruction="You are a senior developer performing a PR code review. Focus on SOLID, performance, bugs, and edge cases.",
                model_name="claude-3-5-sonnet",
            )
        )
        return res.content

    def explain_commit_history(self, repo_name: str, branch: Optional[str] = None) -> str:
        commits = self.get_commit_history(repo_name, branch)[:30] # analyze top 30 commits
        
        commits_str = "\n".join([
            f"- sha: {c.sha[:7]} | message: {c.message} | author: {c.author} | date: {c.date}"
            for c in commits
        ])

        prompt = (
            f"You are a release coordinator analyzing the commit history for: {repo_name} (branch: {branch or 'default'}).\n\n"
            f"Commits List:\n{commits_str}\n\n"
            "Please analyze these commits and generate an architectural summary:\n"
            "1. Commit Clustering (Group commits by feature, bugfix, refactor, or test)\n"
            "2. Key Milestones & Release Candidates identified\n"
            "3. Automatically generated project Changelog\n"
            "4. Code Refactors and structural cleanup detected"
        )

        res = self._model_service.execute_request(
            LLMRequest(
                prompt=prompt,
                system_instruction="You are an expert release engineer summarizing development milestones.",
                model_name="claude-3-5-sonnet",
            )
        )
        return res.content

import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle


@dataclass
class GitHubAuthentication:
    token: Optional[str] = None

    def get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers


class GitHubCache:
    def __init__(self) -> None:
        self._cache: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value

    def clear(self) -> None:
        self._cache.clear()


@dataclass
class GitHubRepository:
    owner: str
    name: str
    description: Optional[str] = None
    stars: int = 0
    forks: int = 0
    languages: List[str] = field(default_factory=list)
    url: str = ""
    is_private: bool = False
    open_issues_count: int = 0


@dataclass
class GitHubPullRequest:
    number: int
    title: str
    state: str
    body: Optional[str] = None
    user: str = ""
    html_url: str = ""
    diff_url: str = ""
    created_at: str = ""
    is_draft: bool = False


@dataclass
class GitHubIssue:
    number: int
    title: str
    state: str
    body: Optional[str] = None
    user: str = ""
    labels: List[str] = field(default_factory=list)
    milestone: Optional[str] = None
    created_at: str = ""


@dataclass
class GitHubCommit:
    sha: str
    author: str
    message: str
    date: str = ""
    url: str = ""


@dataclass
class GitHubBranch:
    name: str
    sha: str


@dataclass
class GitHubRelease:
    tag_name: str
    name: str
    body: Optional[str] = None
    created_at: str = ""


@dataclass
class GitHubWorkflow:
    id: int
    name: str
    state: str
    status: str = ""
    conclusion: Optional[str] = None


@dataclass
class GitHubContext:
    active_repo: Optional[str] = None  # "owner/repo"
    auth: Optional[GitHubAuthentication] = None


class GitHubService(ServiceLifecycle, abc.ABC):
    """Unified service interface for GitHub Intelligence."""

    @abc.abstractmethod
    def inspect_repository(self, repo_name: str) -> GitHubRepository:
        """Fetch details of a repository."""
        pass

    @abc.abstractmethod
    def list_branches(self, repo_name: str) -> List[GitHubBranch]:
        """List all branches in a repository."""
        pass

    @abc.abstractmethod
    def create_branch(self, repo_name: str, branch_name: str, target_sha: str) -> GitHubBranch:
        """Create a new branch in a repository."""
        pass

    @abc.abstractmethod
    def inspect_pull_request(self, repo_name: str, pr_number: int) -> GitHubPullRequest:
        """Inspect details of a pull request."""
        pass

    @abc.abstractmethod
    def inspect_issue(self, repo_name: str, issue_number: int) -> GitHubIssue:
        """Inspect details of an issue."""
        pass

    @abc.abstractmethod
    def get_commit_history(self, repo_name: str, branch: Optional[str] = None) -> List[GitHubCommit]:
        """Fetch commit history for a repository."""
        pass

    @abc.abstractmethod
    def get_release_history(self, repo_name: str) -> List[GitHubRelease]:
        """Fetch release history for a repository."""
        pass

    @abc.abstractmethod
    def get_workflow_status(self, repo_name: str) -> List[GitHubWorkflow]:
        """Fetch GitHub Action workflows status."""
        pass

    @abc.abstractmethod
    def get_repository_stats(self, repo_name: str) -> Dict[str, Any]:
        """Fetch repository statistics (stars, forks, open issues)."""
        pass

    @abc.abstractmethod
    def search_repositories(self, query: str) -> List[GitHubRepository]:
        """Search GitHub for repositories matching a query."""
        pass

    @abc.abstractmethod
    def get_repository_metadata(self, repo_name: str) -> Dict[str, Any]:
        """Fetch full repository metadata."""
        pass

    @abc.abstractmethod
    def get_diff(self, repo_name: str, base: str, head: str) -> str:
        """Get code diff between base and head branches/commits."""
        pass

    @abc.abstractmethod
    def get_file(self, repo_name: str, path: str, ref: Optional[str] = None) -> str:
        """Retrieve file content from repository."""
        pass

    @abc.abstractmethod
    def get_readme(self, repo_name: str) -> str:
        """Retrieve README.md content from repository."""
        pass

    @abc.abstractmethod
    def get_contributors(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get repository contributors list."""
        pass

    @abc.abstractmethod
    def get_labels(self, repo_name: str) -> List[str]:
        """Get repository issue/PR labels."""
        pass

    @abc.abstractmethod
    def get_milestones(self, repo_name: str) -> List[Dict[str, Any]]:
        """Get repository milestones."""
        pass

    # AI OS Intelligence methods
    @abc.abstractmethod
    def review_repository(self, repo_name: str) -> str:
        """Deep architectural review of the repository using LLM."""
        pass

    @abc.abstractmethod
    def review_pr(self, repo_name: str, pr_number: int) -> str:
        """AI code review of a pull request."""
        pass

    @abc.abstractmethod
    def explain_commit_history(self, repo_name: str, branch: Optional[str] = None) -> str:
        """Analyze and cluster commit history, identifying refactors and milestones."""
        pass

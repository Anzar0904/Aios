from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class RepositoryMetadata:
    owner: str
    name: str
    description: Optional[str] = None
    stars: int = 0
    forks: int = 0
    languages: List[str] = field(default_factory=list)
    url: str = ""
    is_private: bool = False
    open_issues_count: int = 0
    permissions: Dict[str, bool] = field(default_factory=dict)
    branch_protection_rules: List[str] = field(default_factory=list)


@dataclass
class BranchInfo:
    name: str
    sha: str
    is_protected: bool = False


@dataclass
class CommitInfo:
    sha: str
    author: str
    message: str
    date: str = ""
    url: str = ""


@dataclass
class PullRequestInfo:
    number: int
    title: str
    state: str  # "open", "closed", "merged"
    body: Optional[str] = None
    user: str = ""
    html_url: str = ""
    diff_url: str = ""
    created_at: str = ""
    is_draft: bool = False
    reviewers: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    milestone: Optional[str] = None
    assignees: List[str] = field(default_factory=list)


@dataclass
class IssueInfo:
    number: int
    title: str
    state: str  # "open", "closed"
    body: Optional[str] = None
    user: str = ""
    labels: List[str] = field(default_factory=list)
    milestone: Optional[str] = None
    assignees: List[str] = field(default_factory=list)
    created_at: str = ""


@dataclass
class ReleaseInfo:
    tag_name: str
    name: str
    body: Optional[str] = None
    created_at: str = ""
    is_draft: bool = False
    is_prerelease: bool = False
    assets: List[str] = field(default_factory=list)


@dataclass
class WorkflowInfo:
    id: str
    name: str
    state: str
    status: str = ""
    conclusion: Optional[str] = None
    created_at: str = ""


@dataclass
class WebhookInfo:
    id: str
    url: str
    events: List[str]
    is_active: bool = True

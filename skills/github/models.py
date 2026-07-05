from dataclasses import dataclass
from typing import Optional


@dataclass
class GitHubRepo:
    name: str
    owner: str
    description: Optional[str] = None
    url: str = ""
    is_private: bool = False


@dataclass
class GitHubBranch:
    name: str
    commit_sha: str


@dataclass
class GitHubPR:
    number: int
    title: str
    state: str
    body: Optional[str] = None
    html_url: str = ""
    diff_url: str = ""


@dataclass
class GitHubIssue:
    number: int
    title: str
    state: str
    body: Optional[str] = None
    html_url: str = ""


@dataclass
class GitHubRelease:
    tag_name: str
    name: str
    body: Optional[str] = None
    published_at: str = ""


@dataclass
class GitHubWorkflow:
    id: int
    name: str
    state: str
    path: str = ""


@dataclass
class GitHubCommit:
    sha: str
    message: str
    author: str
    date: str = ""


@dataclass
class GitHubTag:
    name: str
    commit_sha: str

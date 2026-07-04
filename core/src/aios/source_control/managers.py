import os
from typing import List, Dict, Any, Optional

from aios.providers.models import DIInitializeMixin
from aios.source_control.service import SourceControlService
from aios.source_control.git_local import LocalGitExecutor
from aios.source_control.models import (
    RepositoryMetadata,
    BranchInfo,
    CommitInfo,
    PullRequestInfo,
    IssueInfo,
    ReleaseInfo,
    WorkflowInfo,
    WebhookInfo,
)


class RepositoryManager(DIInitializeMixin):
    def __init__(self, service: SourceControlService) -> None:
        self.service = service

    def get_metadata(self, repo_name: str) -> RepositoryMetadata:
        return self.service.get_active_provider().get_repository_metadata(repo_name)

    def create(self, name: str, is_private: bool = False, description: Optional[str] = None) -> RepositoryMetadata:
        return self.service.get_active_provider().create_repository(name, is_private, description)

    def fork(self, repo_name: str) -> RepositoryMetadata:
        return self.service.get_active_provider().fork_repository(repo_name)

    def delete(self, repo_name: str) -> bool:
        return self.service.get_active_provider().delete_repository(repo_name)


class BranchManager(DIInitializeMixin):
    def __init__(self, git_executor: LocalGitExecutor) -> None:
        self.git_executor = git_executor

    def create(self, branch_name: str, cwd: Optional[str] = None) -> str:
        return self.git_executor.create_branch(branch_name, cwd)

    def delete(self, branch_name: str, force: bool = False, cwd: Optional[str] = None) -> str:
        return self.git_executor.delete_branch(branch_name, force, cwd)


class CommitManager(DIInitializeMixin):
    def __init__(self, git_executor: LocalGitExecutor) -> None:
        self.git_executor = git_executor

    def commit(self, message: str, amend: bool = False, cwd: Optional[str] = None) -> str:
        return self.git_executor.commit(message, amend, cwd)

    def log(self, max_count: int = 20, cwd: Optional[str] = None) -> str:
        return self.git_executor.log(max_count, cwd)


class TagManager(DIInitializeMixin):
    def __init__(self, git_executor: LocalGitExecutor) -> None:
        self.git_executor = git_executor

    def create_tag(self, name: str, message: Optional[str] = None, cwd: Optional[str] = None) -> str:
        return self.git_executor.tag(name, message, cwd)


class MergeManager(DIInitializeMixin):
    def __init__(self, git_executor: LocalGitExecutor) -> None:
        self.git_executor = git_executor

    def merge(self, source_branch: str, cwd: Optional[str] = None) -> str:
        return self.git_executor.merge(source_branch, cwd)

    def rebase(self, upstream: str, cwd: Optional[str] = None) -> str:
        return self.git_executor.rebase(upstream, cwd)

    def cherry_pick(self, sha: str, cwd: Optional[str] = None) -> str:
        return self.git_executor.cherry_pick(sha, cwd)


class DiffManager(DIInitializeMixin):
    def __init__(self, git_executor: LocalGitExecutor) -> None:
        self.git_executor = git_executor

    def diff(self, base: Optional[str] = None, head: Optional[str] = None, cwd: Optional[str] = None) -> str:
        return self.git_executor.diff(base, head, cwd)


class WorkspaceRepositoryManager(DIInitializeMixin):
    def __init__(self, git_executor: LocalGitExecutor) -> None:
        self.git_executor = git_executor

    def init_repo(self, path: str) -> str:
        return self.git_executor.init(path)

    def clone_repo(self, url: str, path: str) -> str:
        return self.git_executor.clone(url, path)

    def stage_file(self, path: str, cwd: Optional[str] = None) -> str:
        return self.git_executor.stage(path, cwd)

    def unstage_file(self, path: str, cwd: Optional[str] = None) -> str:
        return self.git_executor.unstage(path, cwd)

    def fetch_repo(self, remote: str = "origin", cwd: Optional[str] = None) -> str:
        return self.git_executor.fetch(remote, cwd)

    def pull_repo(self, remote: str = "origin", branch: str = "main", cwd: Optional[str] = None) -> str:
        return self.git_executor.pull(remote, branch, cwd)

    def push_repo(self, remote: str = "origin", branch: str = "main", cwd: Optional[str] = None) -> str:
        return self.git_executor.push(remote, branch, cwd)

    def reset_repo(self, target: str, mode: str = "--hard", cwd: Optional[str] = None) -> str:
        return self.git_executor.reset(target, mode, cwd)

    def check_conflicts(self, cwd: Optional[str] = None) -> List[str]:
        return self.git_executor.detect_conflicts(cwd)


class PullRequestManager(DIInitializeMixin):
    def __init__(self, service: SourceControlService) -> None:
        self.service = service

    def create(self, repo_name: str, title: str, head: str, base: str, body: Optional[str] = None, is_draft: bool = False) -> PullRequestInfo:
        return self.service.get_active_provider().create_pull_request(repo_name, title, head, base, body, is_draft)

    def inspect(self, repo_name: str, pr_number: int) -> PullRequestInfo:
        return self.service.get_active_provider().inspect_pull_request(repo_name, pr_number)

    def update(self, repo_name: str, pr_number: int, payload: Dict[str, Any]) -> PullRequestInfo:
        return self.service.get_active_provider().update_pull_request(repo_name, pr_number, payload)

    def merge(self, repo_name: str, pr_number: int, commit_message: Optional[str] = None) -> bool:
        return self.service.get_active_provider().merge_pull_request(repo_name, pr_number, commit_message)


class IssueManager(DIInitializeMixin):
    def __init__(self, service: SourceControlService) -> None:
        self.service = service

    def create(self, repo_name: str, title: str, body: Optional[str] = None, assignees: List[str] = None, labels: List[str] = None) -> IssueInfo:
        return self.service.get_active_provider().create_issue(repo_name, title, body, assignees, labels)

    def inspect(self, repo_name: str, issue_number: int) -> IssueInfo:
        return self.service.get_active_provider().inspect_issue(repo_name, issue_number)


class ReleaseManager(DIInitializeMixin):
    def __init__(self, service: SourceControlService) -> None:
        self.service = service

    def create(self, repo_name: str, tag_name: str, name: str, body: Optional[str] = None, draft: bool = False, prerelease: bool = False) -> ReleaseInfo:
        return self.service.get_active_provider().create_release(repo_name, tag_name, name, body, draft, prerelease)


class WorkflowManager(DIInitializeMixin):
    def __init__(self, service: SourceControlService) -> None:
        self.service = service

    def list_workflows(self, repo_name: str) -> List[WorkflowInfo]:
        return self.service.get_active_provider().list_workflows(repo_name)


class WebhookManager(DIInitializeMixin):
    def __init__(self, service: SourceControlService) -> None:
        self.service = service

    def create(self, repo_name: str, url: str, events: List[str]) -> WebhookInfo:
        return self.service.get_active_provider().create_webhook(repo_name, url, events)

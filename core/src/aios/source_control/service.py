import os
import time
import shutil
import subprocess
import logging
from typing import Dict, List, Any, Optional, Type

from aios.services.base import ServiceLifecycle
from aios.providers.models import DIInitializeMixin
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

logger = logging.getLogger(__name__)


class SourceControlProvider(DIInitializeMixin):
    """Abstract interface defining required methods for source control host providers."""

    def __init__(self, name: str) -> None:
        self.name = name

    # Repositories
    def get_repository_metadata(self, repo_name: str) -> RepositoryMetadata:
        raise NotImplementedError()

    def create_repository(self, name: str, is_private: bool = False, description: Optional[str] = None) -> RepositoryMetadata:
        raise NotImplementedError()

    def fork_repository(self, repo_name: str) -> RepositoryMetadata:
        raise NotImplementedError()

    def delete_repository(self, repo_name: str) -> bool:
        raise NotImplementedError()

    # Pull Requests
    def create_pull_request(self, repo_name: str, title: str, head: str, base: str, body: Optional[str] = None, is_draft: bool = False) -> PullRequestInfo:
        raise NotImplementedError()

    def inspect_pull_request(self, repo_name: str, pr_number: int) -> PullRequestInfo:
        raise NotImplementedError()

    def update_pull_request(self, repo_name: str, pr_number: int, payload: Dict[str, Any]) -> PullRequestInfo:
        raise NotImplementedError()

    def merge_pull_request(self, repo_name: str, pr_number: int, commit_message: Optional[str] = None) -> bool:
        raise NotImplementedError()

    # Issues
    def create_issue(self, repo_name: str, title: str, body: Optional[str] = None, assignees: List[str] = None, labels: List[str] = None) -> IssueInfo:
        raise NotImplementedError()

    def inspect_issue(self, repo_name: str, issue_number: int) -> IssueInfo:
        raise NotImplementedError()

    # Releases
    def create_release(self, repo_name: str, tag_name: str, name: str, body: Optional[str] = None, draft: bool = False, prerelease: bool = False) -> ReleaseInfo:
        raise NotImplementedError()

    # Webhooks
    def create_webhook(self, repo_name: str, url: str, events: List[str]) -> WebhookInfo:
        raise NotImplementedError()

    # Actions/Workflows
    def list_workflows(self, repo_name: str) -> List[WorkflowInfo]:
        raise NotImplementedError()


class SourceControlRegistry(DIInitializeMixin):
    """Registry container saving registered providers."""

    def __init__(self) -> None:
        self._providers: Dict[str, SourceControlProvider] = {}

    def register_provider(self, provider: SourceControlProvider) -> None:
        self._providers[provider.name] = provider
        logger.info(f"Registered source control provider: {provider.name}")

    def get_provider(self, name: str) -> SourceControlProvider:
        prov = self._providers.get(name)
        if not prov:
            raise KeyError(f"Source control provider '{name}' is not registered.")
        return prov

    def list_providers(self) -> List[str]:
        return list(self._providers.keys())


class ProviderConfigurationService(DIInitializeMixin):
    """Manages active configuration properties and engineering profile strategies."""

    def __init__(self) -> None:
        self.preferred_provider: str = "github"
        self.repository_defaults: Dict[str, Any] = {"is_private": True, "license": "MIT"}
        self.branch_strategy: str = "gitflow"  # "gitflow", "trunk"
        self.commit_strategy: str = "conventional"
        self.merge_strategy: str = "squash"  # "squash", "rebase", "merge"
        self.pr_strategy: str = "require_review"
        self.authentication_strategy: str = "cli"  # "cli", "token"


class ProviderDiscovery(DIInitializeMixin):
    """Discovers local environment configurations and external hosts."""

    def __init__(self, registry: SourceControlRegistry) -> None:
        self.registry = registry

    def discover_and_register(self) -> None:
        # Registers the default GitHub provider
        from aios.source_control.github_provider import GitHubProvider
        gh = GitHubProvider()
        self.registry.register_provider(gh)


class ProviderHealthMonitor(DIInitializeMixin):
    """Polls provider host latency, rate limits, and failure tracking metrics."""

    def __init__(self, registry: SourceControlRegistry) -> None:
        self.registry = registry
        self.failure_counts: Dict[str, int] = {}
        self.latencies: Dict[str, List[float]] = {}

    def record_call(self, provider_name: str, latency: float, success: bool) -> None:
        if provider_name not in self.latencies:
            self.latencies[provider_name] = []
        self.latencies[provider_name].append(latency)
        if len(self.latencies[provider_name]) > 100:
            self.latencies[provider_name].pop(0)

        if not success:
            self.failure_counts[provider_name] = self.failure_counts.get(provider_name, 0) + 1

    def get_health_status(self, provider_name: str) -> Dict[str, Any]:
        lats = self.latencies.get(provider_name, [])
        avg = sum(lats) / len(lats) if lats else 0.0
        sorted_lats = sorted(lats)
        p95 = sorted_lats[int(len(sorted_lats) * 0.95)] if lats else 0.0
        return {
            "status": "online",
            "average_latency_sec": avg,
            "p95_latency_sec": p95,
            "failures": self.failure_counts.get(provider_name, 0)
        }


class ProviderDiagnostics(DIInitializeMixin):
    """Detects Git install versions, GitHub CLI auth states, and rate limits."""

    def run_diagnostics(self) -> Dict[str, Any]:
        git_installed = shutil.which("git") is not None
        git_version = "unknown"
        if git_installed:
            try:
                res = subprocess.run(["git", "--version"], capture_output=True, text=True)
                git_version = res.stdout.strip().split()[-1]
            except Exception:
                pass

        gh_installed = shutil.which("gh") is not None
        gh_authenticated = False
        if gh_installed:
            try:
                res = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
                gh_authenticated = "Logged in" in res.stderr or "Logged in" in res.stdout
            except Exception:
                pass

        return {
            "git_installed": git_installed,
            "git_version": git_version,
            "gh_cli_installed": gh_installed,
            "gh_cli_authenticated": gh_authenticated,
            "pat_configured": os.environ.get("GITHUB_TOKEN") is not None
        }


class ProviderValidator(DIInitializeMixin):
    """Validates configuration parameters and repo urls."""

    def validate_repository_name(self, name: str) -> bool:
        if not name or "/" not in name:
            return False
        parts = name.split("/")
        return len(parts) == 2 and all(p.strip() for p in parts)


class SourceControlService(DIInitializeMixin):
    """Central manager delegating queries to the active provider and tracking call metrics."""

    def __init__(
        self,
        registry: SourceControlRegistry,
        config_service: ProviderConfigurationService,
        health_monitor: ProviderHealthMonitor,
        diagnostics: ProviderDiagnostics,
        validator: ProviderValidator,
    ) -> None:
        self.registry = registry
        self.config_service = config_service
        self.health_monitor = health_monitor
        self.diagnostics = diagnostics
        self.validator = validator

    def get_active_provider(self) -> SourceControlProvider:
        p_name = self.config_service.preferred_provider
        return self.registry.get_provider(p_name)

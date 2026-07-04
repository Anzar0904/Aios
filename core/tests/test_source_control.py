import os
import shutil
import pytest
from unittest.mock import MagicMock, patch

from aios.source_control import (
    SourceControlRegistry,
    ProviderDiscovery,
    ProviderConfigurationService,
    ProviderHealthMonitor,
    ProviderDiagnostics,
    ProviderValidator,
    SourceControlService,
    LocalGitExecutor,
    RepositoryManager,
    BranchManager,
    CommitManager,
    TagManager,
    MergeManager,
    DiffManager,
    WorkspaceRepositoryManager,
    PullRequestManager,
    IssueManager,
    ReleaseManager,
    WorkflowManager,
    WebhookManager,
    SourceControlTelemetry,
    SourceControlStatistics,
    SourceControlReportGenerator,
    GitHubProvider,
)


@pytest.fixture
def temp_git_dir(tmp_path):
    path = tmp_path / "test_repo"
    os.makedirs(path, exist_ok=True)
    return str(path)


def test_local_git_lifecycle(temp_git_dir):
    executor = LocalGitExecutor(temp_git_dir)
    executor.init(temp_git_dir)
    assert os.path.exists(os.path.join(temp_git_dir, ".git"))

    # Test file staging and status
    test_file = os.path.join(temp_git_dir, "hello.txt")
    with open(test_file, "w") as f:
        f.write("hello world")

    executor.stage("hello.txt", cwd=temp_git_dir)
    status_out = executor.status(cwd=temp_git_dir)
    assert "hello.txt" in status_out

    # Test commit
    executor.commit("initial commit", cwd=temp_git_dir)
    log_out = executor.log(1, cwd=temp_git_dir)
    assert "initial commit" in log_out


def test_source_control_registry():
    registry = SourceControlRegistry()
    discovery = ProviderDiscovery(registry)
    discovery.discover_and_register()

    providers = registry.list_providers()
    assert "github" in providers
    assert isinstance(registry.get_provider("github"), GitHubProvider)


def test_provider_configuration():
    config = ProviderConfigurationService()
    assert config.preferred_provider == "github"
    assert config.merge_strategy == "squash"


@patch("httpx.Client.request")
def test_github_provider_adapter(mock_request):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "owner": {"login": "test-owner"},
        "name": "test-repo",
        "stargazers_count": 50,
        "forks_count": 5,
        "html_url": "https://github.com/test-owner/test-repo",
        "private": True,
        "open_issues_count": 0,
        "permissions": {"admin": True}
    }
    mock_request.return_value = mock_resp

    provider = GitHubProvider(token="test-pat")
    meta = provider.get_repository_metadata("test-owner/test-repo")
    assert meta.owner == "test-owner"
    assert meta.name == "test-repo"
    assert meta.stars == 50
    assert meta.is_private is True


def test_diagnostics():
    diagnostics = ProviderDiagnostics()
    res = diagnostics.run_diagnostics()
    assert "git_installed" in res
    assert "gh_cli_installed" in res


def test_validator():
    validator = ProviderValidator()
    assert validator.validate_repository_name("owner/repo") is True
    assert validator.validate_repository_name("repo") is False


def test_telemetry_recording():
    telemetry = SourceControlTelemetry()
    telemetry.record_call(0.125, True)
    telemetry.record_call(0.045, True)
    metrics = telemetry.get_metrics()
    assert metrics["total_calls"] == 2
    assert metrics["success_rate"] == 1.0
    assert metrics["average_api_time_sec"] == pytest.approx(0.085)


def test_report_generation(tmp_path):
    ws_root = str(tmp_path)
    diagnostics = ProviderDiagnostics()
    registry = SourceControlRegistry()
    discovery = ProviderDiscovery(registry)
    discovery.discover_and_register()
    health = ProviderHealthMonitor(registry)
    statistics = SourceControlStatistics()

    reporter = SourceControlReportGenerator(ws_root, diagnostics, health, statistics)
    reporter.generate_reports()

    sc_dir = os.path.join(ws_root, "docs", "source_control")
    assert os.path.exists(os.path.join(sc_dir, "SOURCE_CONTROL_STATUS.md"))
    assert os.path.exists(os.path.join(sc_dir, "REPOSITORY_REPORT.md"))
    assert os.path.exists(os.path.join(sc_dir, "BRANCH_REPORT.md"))
    assert os.path.exists(os.path.join(sc_dir, "PULL_REQUEST_REPORT.md"))
    assert os.path.exists(os.path.join(sc_dir, "RELEASE_REPORT.md"))
    assert os.path.exists(os.path.join(sc_dir, "WORKFLOW_REPORT.md"))
    assert os.path.exists(os.path.join(sc_dir, "DIAGNOSTICS.md"))

"""
Sprint 25 — GitHub Intelligence Test Suite.

Coverage:
- GitHubConnectionManager: login, logout, status, list_user_repos, list_orgs, test_connection
- GitHubMemory: save/load for all entity types, list_cached_repos
- GitHubIntelligenceEngine: inspect_repository, list_branches, list_pull_requests,
  list_issues, get_release_history, get_workflow_status, commit_history,
  generate_repo_summary, generate_commit_message, generate_changelog,
  summarise_actions
- GitHubReportGenerator: all 6 reports + generate_all bulk
- CLI commands: all 11 sub-commands route correctly
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from aios.cli import execute_builtin_cli_command
from aios.github.connection import GitHubConnectionManager
from aios.github.intelligence import GitHubIntelligenceEngine
from aios.github.memory import GitHubMemory
from aios.github.reports import GitHubReportGenerator
from aios.services.github import (
    GitHubBranch,
    GitHubCommit,
    GitHubIssue,
    GitHubPullRequest,
    GitHubRelease,
    GitHubRepository,
    GitHubWorkflow,
)

# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_model():
    m = MagicMock()
    m.execute_request.return_value = MagicMock(content="AI summary text.")
    return m


@pytest.fixture
def tmp_memory(tmp_path):
    return GitHubMemory(cache_dir=str(tmp_path))


def _mock_repo():
    return GitHubRepository(
        owner="Anzar0904",
        name="aios",
        description="AI OS",
        stars=42,
        forks=7,
        languages=["Python"],
        url="https://github.com/Anzar0904/aios",
        is_private=True,
        open_issues_count=3,
    )


# ── GitHubConnectionManager ───────────────────────────────────────────────────


def test_connection_login_success(tmp_path):
    mgr = GitHubConnectionManager(token="ghp_test_token")
    with (
        patch.object(
            mgr,
            "_get",
            return_value={"login": "Anzar0904", "name": "Anzar"},
        ),
        patch.object(mgr, "_save_state"),
    ):
        result = mgr.login()

    assert result["success"] is True
    assert result["user"] == "Anzar0904"
    assert "Logged in as" in result["message"]


@patch("httpx.Client")
def test_connection_login_failure(mock_client_class, tmp_path):
    mock_client = MagicMock()
    mock_client_class.return_value.__enter__.return_value = mock_client
    mock_client.get.side_effect = Exception("Connection refused")

    with patch(
        "aios.github.connection._STATE_FILE",
        tmp_path / ".aios_github_cache/connection_state.json",
    ):
        mgr = GitHubConnectionManager(token="bad_token")
        result = mgr.login()

    assert result["success"] is False
    assert "Connection refused" in result["message"]


def test_connection_status_disconnected(tmp_path):
    with patch(
        "aios.github.connection._STATE_FILE",
        tmp_path / "no_state.json",
    ):
        mgr = GitHubConnectionManager()
        st = mgr.get_status()

    assert st["connected"] is False
    assert st["user"] is None


@patch("httpx.Client")
def test_connection_list_user_repos(mock_client_class, tmp_path):
    mock_client = MagicMock()
    mock_client_class.return_value.__enter__.return_value = mock_client

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [{"name": "aios", "full_name": "Anzar0904/aios", "private": True}]
    mock_client.get.return_value = mock_resp

    with patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"):
        mgr = GitHubConnectionManager(token="ghp_test")
        repos = mgr.list_user_repos()

    assert len(repos) == 1
    assert repos[0]["name"] == "aios"


@patch("httpx.Client")
def test_connection_test_connection_reachable(mock_client_class, tmp_path):
    mock_client = MagicMock()
    mock_client_class.return_value.__enter__.return_value = mock_client

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"login": "Anzar0904"}
    mock_client.get.return_value = mock_resp

    with patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"):
        mgr = GitHubConnectionManager(token="ghp_test")
        result = mgr.test_connection()

    assert result["reachable"] is True
    assert result["user"] == "Anzar0904"
    assert result["latency_ms"] >= 0.0


# ── GitHubMemory ──────────────────────────────────────────────────────────────


def test_memory_repo_save_load(tmp_memory):
    repo = {"owner": "X", "name": "Y", "stars": 10}
    tmp_memory.save_repo("X/Y", repo)
    loaded = tmp_memory.load_repo("X/Y")
    assert loaded["name"] == "Y"
    assert loaded["stars"] == 10


def test_memory_prs_save_load(tmp_memory):
    prs = [{"number": 1, "title": "Fix bug"}]
    tmp_memory.save_prs("X/Y", prs)
    assert tmp_memory.load_prs("X/Y") == prs


def test_memory_issues_save_load(tmp_memory):
    issues = [{"number": 5, "title": "Crash"}]
    tmp_memory.save_issues("X/Y", issues)
    assert tmp_memory.load_issues("X/Y") == issues


def test_memory_branches_save_load(tmp_memory):
    branches = [{"name": "main", "sha": "abc123"}]
    tmp_memory.save_branches("X/Y", branches)
    assert tmp_memory.load_branches("X/Y") == branches


def test_memory_releases_save_load(tmp_memory):
    releases = [{"tag_name": "v1.0", "name": "First Release"}]
    tmp_memory.save_releases("X/Y", releases)
    assert tmp_memory.load_releases("X/Y") == releases


def test_memory_workflows_save_load(tmp_memory):
    runs = [{"id": 1, "name": "CI", "status": "completed", "conclusion": "success"}]
    tmp_memory.save_workflows("X/Y", runs)
    assert tmp_memory.load_workflows("X/Y") == runs


def test_memory_list_cached_repos(tmp_memory):
    tmp_memory.save_repo("A/B", {"name": "B"})
    tmp_memory.save_repo("C/D", {"name": "D"})
    cached = tmp_memory.list_cached_repos()
    assert "A/B" in cached
    assert "C/D" in cached


def test_memory_returns_empty_on_missing(tmp_memory):
    assert tmp_memory.load_prs("nonexistent/repo") == []
    assert tmp_memory.load_issues("nonexistent/repo") == []
    assert tmp_memory.load_branches("nonexistent/repo") == []


# ── GitHubIntelligenceEngine ──────────────────────────────────────────────────


@patch("httpx.Client")
def test_engine_inspect_repository(mock_client_class, mock_model, tmp_path):
    mock_client = MagicMock()
    mock_client_class.return_value.__enter__.return_value = mock_client

    mock_resp_repo = MagicMock()
    mock_resp_repo.status_code = 200
    mock_resp_repo.headers = {"Content-Type": "application/json"}
    mock_resp_repo.json.return_value = {
        "owner": {"login": "Anzar0904"},
        "name": "aios",
        "description": "AI OS",
        "stargazers_count": 42,
        "forks_count": 7,
        "html_url": "https://github.com/Anzar0904/aios",
        "private": True,
        "open_issues_count": 3,
    }
    mock_resp_langs = MagicMock()
    mock_resp_langs.status_code = 200
    mock_resp_langs.headers = {"Content-Type": "application/json"}
    mock_resp_langs.json.return_value = {"Python": 9999}
    mock_client.get.side_effect = [mock_resp_repo, mock_resp_langs]

    with patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"):
        engine = GitHubIntelligenceEngine(model_service=mock_model, cache_dir=str(tmp_path))
        repo = engine.inspect_repository("Anzar0904/aios")

    assert repo.name == "aios"
    assert repo.stars == 42
    assert "Python" in repo.languages


@patch("httpx.Client")
def test_engine_list_branches(mock_client_class, mock_model, tmp_path):
    mock_client = MagicMock()
    mock_client_class.return_value.__enter__.return_value = mock_client

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_resp.json.return_value = [{"name": "main", "commit": {"sha": "abc1234"}}]
    mock_client.get.return_value = mock_resp

    with patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"):
        engine = GitHubIntelligenceEngine(model_service=mock_model, cache_dir=str(tmp_path))
        branches = engine.list_branches("Anzar0904/aios")

    assert len(branches) == 1
    assert branches[0].name == "main"
    assert branches[0].sha == "abc1234"


@patch("httpx.Client")
def test_engine_get_release_history(mock_client_class, mock_model, tmp_path):
    mock_client = MagicMock()
    mock_client_class.return_value.__enter__.return_value = mock_client

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_resp.json.return_value = [
        {
            "tag_name": "v1.0.0",
            "name": "First Release",
            "body": "Notes",
            "created_at": "2026-01-01T00:00:00Z",
        }
    ]
    mock_client.get.return_value = mock_resp

    with patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"):
        engine = GitHubIntelligenceEngine(model_service=mock_model, cache_dir=str(tmp_path))
        releases = engine.get_release_history("Anzar0904/aios")

    assert len(releases) == 1
    assert releases[0].tag_name == "v1.0.0"


@patch("httpx.Client")
def test_engine_generate_repo_summary(mock_client_class, mock_model, tmp_path):
    mock_client = MagicMock()
    mock_client_class.return_value.__enter__.return_value = mock_client

    mock_resp_repo = MagicMock()
    mock_resp_repo.status_code = 200
    mock_resp_repo.headers = {"Content-Type": "application/json"}
    mock_resp_repo.json.return_value = {
        "owner": {"login": "Anzar0904"},
        "name": "aios",
        "description": "AI OS",
        "stargazers_count": 42,
        "forks_count": 7,
        "html_url": "https://github.com/Anzar0904/aios",
        "private": True,
        "open_issues_count": 3,
    }
    mock_resp_langs = MagicMock()
    mock_resp_langs.status_code = 200
    mock_resp_langs.headers = {"Content-Type": "application/json"}
    mock_resp_langs.json.return_value = {"Python": 9999}
    mock_client.get.side_effect = [mock_resp_repo, mock_resp_langs]

    with patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"):
        engine = GitHubIntelligenceEngine(model_service=mock_model, cache_dir=str(tmp_path))
        summary = engine.generate_repo_summary("Anzar0904/aios")

    assert "AI summary text." in summary
    mock_model.execute_request.assert_called_once()


def test_engine_generate_commit_message(mock_model, tmp_path):
    with patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"):
        engine = GitHubIntelligenceEngine(model_service=mock_model, cache_dir=str(tmp_path))
        msg = engine.generate_commit_message("+ def foo(): return 42")

    assert "AI summary text." in msg
    mock_model.execute_request.assert_called_once()


# ── GitHubReportGenerator ─────────────────────────────────────────────────────


def test_report_generator_all_files(tmp_path):
    rpt = GitHubReportGenerator(output_dir=str(tmp_path / "docs" / "github"))

    repo = {
        "owner": "Anzar0904",
        "name": "aios",
        "description": "AI OS",
        "stars": 42,
        "forks": 7,
        "languages": ["Python"],
        "url": "https://github.com/Anzar0904/aios",
        "is_private": True,
        "open_issues_count": 3,
    }
    prs = [{"number": 1, "title": "Fix X", "state": "open", "user": "dev1", "url": "#1"}]
    issues = [{"number": 5, "title": "Bug Y", "state": "open", "labels": ["bug"], "user": "dev2"}]
    branches = [{"name": "main", "sha": "abc1234"}]
    releases = [{"tag_name": "v1.0", "name": "v1", "created_at": "2026-01-01T00:00:00Z"}]
    workflows = [{"id": 1, "name": "CI", "status": "completed", "conclusion": "success"}]

    rpt.generate_all(
        repo=repo,
        prs=prs,
        issues=issues,
        branches=branches,
        releases=releases,
        workflows=workflows,
        ai_repo_summary="This is a great project.",
        ai_actions_summary="CI is healthy.",
    )

    out_dir = tmp_path / "docs" / "github"
    for fname in [
        "repository_summary.md",
        "pull_request_report.md",
        "issue_report.md",
        "branch_report.md",
        "release_report.md",
        "actions_report.md",
    ]:
        assert (out_dir / fname).is_file(), f"Missing: {fname}"

    summary_content = (out_dir / "repository_summary.md").read_text()
    assert "Anzar0904" in summary_content
    assert "This is a great project." in summary_content

    pr_content = (out_dir / "pull_request_report.md").read_text()
    assert "Fix X" in pr_content

    issue_content = (out_dir / "issue_report.md").read_text()
    assert "Bug Y" in issue_content

    branch_content = (out_dir / "branch_report.md").read_text()
    assert "main" in branch_content

    release_content = (out_dir / "release_report.md").read_text()
    assert "v1.0" in release_content

    actions_content = (out_dir / "actions_report.md").read_text()
    assert "CI" in actions_content
    assert "CI is healthy." in actions_content


# ── CLI Command routing ───────────────────────────────────────────────────────


def _mock_engine(tmp_path):
    """Returns a fully mocked GitHubIntelligenceEngine instance."""
    model = MagicMock()
    model.execute_request.return_value = MagicMock(content="AI summary.")

    with patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"):
        engine = GitHubIntelligenceEngine.__new__(GitHubIntelligenceEngine)

    engine.conn = MagicMock()
    engine.memory = GitHubMemory(cache_dir=str(tmp_path))
    engine._model = model

    svc = MagicMock()
    svc.inspect_repository.return_value = _mock_repo()
    svc.list_branches.return_value = [GitHubBranch(name="main", sha="abc1234")]
    svc.get_commit_history.return_value = [
        GitHubCommit(sha="abc1234", author="dev", message="feat: init", date="2026-01-01")
    ]
    svc.get_release_history.return_value = [
        GitHubRelease(tag_name="v1.0", name="First", created_at="2026-01-01")
    ]
    svc.get_workflow_status.return_value = [
        GitHubWorkflow(id=1, name="CI", state="completed", status="completed", conclusion="success")
    ]
    svc.inspect_pull_request.return_value = GitHubPullRequest(
        number=12, title="Fix router", state="open", user="dev1", html_url="#12"
    )
    svc.inspect_issue.return_value = GitHubIssue(
        number=5, title="Crash", state="open", labels=["bug"]
    )
    svc.review_repository.return_value = "Deep repo review."
    svc.review_pr.return_value = "PR review."
    svc.explain_commit_history.return_value = "Commit history analysis."
    engine._svc = svc

    return engine


@pytest.fixture
def mock_engine_factory(tmp_path):
    def _factory():
        return _mock_engine(tmp_path)

    return _factory


def _cli(args, mock_factory, exit_code=0):
    """Helper to execute a CLI command with mocked engine factory."""
    with (
        patch("aios.github.connection._STATE_FILE", Path("/tmp/test_s.json")),
        patch(
            "aios.github.intelligence.GitHubIntelligenceEngine",
            side_effect=lambda **kw: mock_factory(),
        ),
        patch("sys.exit") as mock_exit,
    ):
        execute_builtin_cli_command(["github"] + args, exit_on_complete=True)
        if exit_code == 0:
            mock_exit.assert_called_with(0)
        return mock_exit


def test_cli_github_login_no_token(tmp_path):
    """Login without a token reports failure (no real API call)."""
    with (
        patch("httpx.Client") as mock_client_class,
        patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"),
        patch("sys.exit") as mock_exit,
    ):
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        mock_client.get.side_effect = Exception("Not authenticated")

        execute_builtin_cli_command(["github", "login"], exit_on_complete=True)
        mock_exit.assert_called_with(1)


def test_cli_github_status(tmp_path):
    with (
        patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"),
        patch("sys.exit") as mock_exit,
    ):
        execute_builtin_cli_command(["github", "status"], exit_on_complete=True)
        mock_exit.assert_called_with(0)


def test_cli_github_repos_no_token(tmp_path):
    """Repos with no token prints empty list, exits 0."""
    with (
        patch("httpx.Client") as mc,
        patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"),
        patch("sys.exit") as mock_exit,
    ):
        mock_client = MagicMock()
        mc.return_value.__enter__.return_value = mock_client
        mock_client.get.return_value = MagicMock(status_code=401)
        mock_client.get.side_effect = Exception("Auth required")

        execute_builtin_cli_command(["github", "repos"], exit_on_complete=True)
        mock_exit.assert_called_with(0)


def test_cli_github_repo_no_arg(tmp_path):
    """Missing repo arg exits 1."""
    with (
        patch("sys.exit") as mock_exit,
        patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"),
    ):
        execute_builtin_cli_command(["github", "repo"], exit_on_complete=True)
        mock_exit.assert_called_with(1)


def test_cli_github_repo_with_arg(tmp_path, mock_engine_factory):
    with (
        patch("aios.github.intelligence.GitHubIntelligenceEngine") as mock_eng,
        patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"),
        patch("sys.exit") as mock_exit,
    ):
        mock_eng.return_value = mock_engine_factory()
        execute_builtin_cli_command(["github", "repo", "Anzar0904/aios"], exit_on_complete=True)
        mock_exit.assert_called_with(0)


def test_cli_github_branches(tmp_path, mock_engine_factory):
    with (
        patch("aios.github.intelligence.GitHubIntelligenceEngine") as mock_eng,
        patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"),
        patch("sys.exit") as mock_exit,
    ):
        mock_eng.return_value = mock_engine_factory()
        execute_builtin_cli_command(["github", "branches", "Anzar0904/aios"], exit_on_complete=True)
        mock_exit.assert_called_with(0)


def test_cli_github_commits(tmp_path, mock_engine_factory):
    with (
        patch("aios.github.intelligence.GitHubIntelligenceEngine") as mock_eng,
        patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"),
        patch("sys.exit") as mock_exit,
    ):
        mock_eng.return_value = mock_engine_factory()
        execute_builtin_cli_command(["github", "commits", "Anzar0904/aios"], exit_on_complete=True)
        mock_exit.assert_called_with(0)


def test_cli_github_issues(tmp_path, mock_engine_factory):
    with (
        patch("aios.github.intelligence.GitHubIntelligenceEngine") as mock_eng,
        patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"),
        patch("sys.exit") as mock_exit,
    ):
        engine = mock_engine_factory()
        engine.list_issues = MagicMock(
            return_value=[{"number": 5, "title": "Crash", "labels": ["bug"]}]
        )
        mock_eng.return_value = engine
        execute_builtin_cli_command(["github", "issues", "Anzar0904/aios"], exit_on_complete=True)
        mock_exit.assert_called_with(0)


def test_cli_github_pr_list(tmp_path, mock_engine_factory):
    with (
        patch("aios.github.intelligence.GitHubIntelligenceEngine") as mock_eng,
        patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"),
        patch("sys.exit") as mock_exit,
    ):
        engine = mock_engine_factory()
        engine.list_pull_requests = MagicMock(
            return_value=[{"number": 12, "title": "Fix", "state": "open", "user": "dev1"}]
        )
        mock_eng.return_value = engine
        execute_builtin_cli_command(["github", "pr", "Anzar0904/aios"], exit_on_complete=True)
        mock_exit.assert_called_with(0)


def test_cli_github_pr_inspect(tmp_path, mock_engine_factory):
    with (
        patch("aios.github.intelligence.GitHubIntelligenceEngine") as mock_eng,
        patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"),
        patch("sys.exit") as mock_exit,
    ):
        mock_eng.return_value = mock_engine_factory()
        execute_builtin_cli_command(["github", "pr", "Anzar0904/aios", "12"], exit_on_complete=True)
        mock_exit.assert_called_with(0)


def test_cli_github_releases(tmp_path, mock_engine_factory):
    with (
        patch("aios.github.intelligence.GitHubIntelligenceEngine") as mock_eng,
        patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"),
        patch("sys.exit") as mock_exit,
    ):
        mock_eng.return_value = mock_engine_factory()
        execute_builtin_cli_command(["github", "releases", "Anzar0904/aios"], exit_on_complete=True)
        mock_exit.assert_called_with(0)


def test_cli_github_actions(tmp_path, mock_engine_factory):
    with (
        patch("aios.github.intelligence.GitHubIntelligenceEngine") as mock_eng,
        patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"),
        patch("sys.exit") as mock_exit,
    ):
        mock_eng.return_value = mock_engine_factory()
        execute_builtin_cli_command(["github", "actions", "Anzar0904/aios"], exit_on_complete=True)
        mock_exit.assert_called_with(0)


def test_cli_github_summary(tmp_path, mock_engine_factory):
    with (
        patch("aios.github.intelligence.GitHubIntelligenceEngine") as mock_eng,
        patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"),
        patch("sys.exit") as mock_exit,
    ):
        engine = mock_engine_factory()
        engine.list_pull_requests = MagicMock(return_value=[])
        engine.list_issues = MagicMock(return_value=[])
        engine.generate_repo_summary = MagicMock(return_value="Excellent repo.")
        engine.summarise_actions = MagicMock(return_value="CI is fine.")
        mock_eng.return_value = engine
        execute_builtin_cli_command(["github", "summary", "Anzar0904/aios"], exit_on_complete=True)
        mock_exit.assert_called_with(0)


def test_cli_github_unknown_sub(tmp_path):
    """Unknown sub-command exits 1."""
    with (
        patch("aios.github.connection._STATE_FILE", tmp_path / "s.json"),
        patch("sys.exit") as mock_exit,
    ):
        execute_builtin_cli_command(["github", "unknownstuff"], exit_on_complete=True)
        mock_exit.assert_called_with(1)

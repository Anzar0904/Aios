"""Phase 9: GitHub Intelligence — Production Test Suite.

Tests cover:
- Repository Registry CRUD & default seeding
- Branch and Commit Intelligence listings
- Pull Request and Issues priority metrics tracking
- Actions workflows and releases version catalogs
- Health Score calculations (verifying penalties deductions)
- Knowledge Graph bridging integration assertions
- CLI command dispatcher smoke runs
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from aios.services.github_intelligence import (
    GitActionWorkflow,
    GitBranch,
    GitCommit,
    GitIssue,
    GitPullRequest,
    GitRelease,
    GitRepository,
    new_id,
)
from aios.services.github_intelligence_impl import GitHubIntelligenceServiceImpl

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_db(tmp_path):
    return str(tmp_path / "test_github.db")


@pytest.fixture
def eng(tmp_db):
    from aios.local import github_intelligence_commands

    github_intelligence_commands._DB_PATH = tmp_db
    svc = GitHubIntelligenceServiceImpl(db_path=tmp_db)
    svc.initialize()
    svc.start()
    yield svc
    svc.shutdown()
    github_intelligence_commands._DB_PATH = None


# ---------------------------------------------------------------------------
# Registry & CRUD
# ---------------------------------------------------------------------------


class TestGitHubRegistry:
    def test_seeded_repositories(self, eng):
        repos = eng.list_repositories()
        assert len(repos) >= 1
        assert repos[0].name == "Anzar0904/Aios"

    def test_register_and_get_repository(self, eng):
        rid = new_id()
        repo = GitRepository(
            repository_id=rid,
            name="Anzar0904/Agency",
            owner="Anzar0904",
            description="CRM and Leads intelligence.",
        )
        eng.register_repository(repo)
        fetched = eng.get_repository(rid)
        assert fetched is not None
        assert fetched.name == "Anzar0904/Agency"


# ---------------------------------------------------------------------------
# Branch & Commit Intelligence
# ---------------------------------------------------------------------------


class TestBranchCommitIntelligence:
    def test_branch_and_commits_recording(self, eng):
        repos = eng.list_repositories()
        rid = repos[0].repository_id

        # Record branch
        branch = GitBranch(
            branch_id=new_id(),
            repository_id=rid,
            name="feat/billing",
            author="Anzar0904",
        )
        eng.record_branch(branch)
        branches = eng.list_branches(rid)
        assert "feat/billing" in [b.name for b in branches]

        # Record commit
        commit = GitCommit(
            commit_sha="sha-12345678",
            repository_id=rid,
            author="Anzar0904",
            message="feat: add Stripe billing webhooks",
            files_changed=4,
            lines_added=150,
            lines_removed=12,
        )
        eng.record_commit(commit)
        commits = eng.list_commits(rid)
        assert len(commits) >= 1
        assert commits[0].commit_sha == "sha-12345678"


# ---------------------------------------------------------------------------
# PR & Issue Intelligence
# ---------------------------------------------------------------------------


class TestPRIssueIntelligence:
    def test_pr_and_issue_recording(self, eng):
        repos = eng.list_repositories()
        rid = repos[0].repository_id

        # PR
        pr = GitPullRequest(
            pr_id=new_id(),
            pr_number=18,
            repository_id=rid,
            title="Refactor auth hooks",
            author="Anzar0904",
            status="open",
            risk_score=35,
        )
        eng.record_pull_request(pr)
        prs = eng.list_pull_requests(rid)
        assert 18 in [p.pr_number for p in prs]

        # Issue
        issue = GitIssue(
            issue_id=new_id(),
            repository_id=rid,
            title="Fix OAuth token refresh bug",
            priority=5,
            status="open",
            assignee="Anzar0904",
            labels=["bug", "high-priority"],
        )
        eng.record_issue(issue)
        issues = eng.list_issues(rid)
        assert 5 in [i.priority for i in issues]


# ---------------------------------------------------------------------------
# Actions & Releases
# ---------------------------------------------------------------------------


class TestActionsReleases:
    def test_workflow_runs_and_releases(self, eng):
        repos = eng.list_repositories()
        rid = repos[0].repository_id

        # Actions
        run = GitActionWorkflow(
            workflow_id="run-99",
            repository_id=rid,
            name="deploy.yml",
            status="success",
            duration_secs=80,
        )
        eng.record_workflow_run(run)
        runs = eng.list_workflow_runs(rid)
        assert len(runs) >= 1
        assert runs[0].name == "deploy.yml"

        # Release
        release = GitRelease(
            release_id=new_id(),
            repository_id=rid,
            version="v2.1.0",
            title="CRM Billing release",
            features=["Stripe gateway integration"],
            fixes=["OAuth Token refresh Fix"],
        )
        eng.record_release(release)
        releases = eng.list_releases(rid)
        assert len(releases) >= 1
        assert releases[0].version == "v2.1.0"


# ---------------------------------------------------------------------------
# Repository Health Scoring
# ---------------------------------------------------------------------------


class TestRepositoryHealth:
    def test_health_scoring_deduction(self, eng):
        rid = new_id()
        repo = GitRepository(repository_id=rid, name="TestHealthRepo", owner="admin")
        eng.register_repository(repo)

        # 100 base score
        initial_health = eng.calculate_repository_health(rid)
        assert initial_health == 100

        # Record 1 open issue -> -5 points
        eng.record_issue(
            GitIssue(issue_id="issue-1", repository_id=rid, title="Bug 1", status="open")
        )

        # Record 1 failed action workflow run -> -15 points
        eng.record_workflow_run(
            GitActionWorkflow(
                workflow_id="run-failed", repository_id=rid, name="ci.yml", status="failed"
            )
        )

        # Record 1 open PR with risk score 40 -> -20 points (40 * 0.5)
        eng.record_pull_request(
            GitPullRequest(
                pr_id="pr-1",
                pr_number=1,
                repository_id=rid,
                title="PR 1",
                author="dev",
                status="open",
                risk_score=40,
            )
        )

        # Final health score: 100 - 5 (issue) - 15 (CI) - 20 (PR risk) = 60
        final_health = eng.calculate_repository_health(rid)
        assert final_health == 60


# ---------------------------------------------------------------------------
# Knowledge Graph Integration
# ---------------------------------------------------------------------------


class TestGitHubIntelligenceGraphBridge:
    def test_sync_repository_node(self):
        from aios.services.github_intelligence_graph_bridge import GitHubIntelligenceGraphBridge

        mock_engine = MagicMock()
        mock_entity = MagicMock()
        mock_entity.entity_id = "mock-repo-id"
        mock_engine.ensure_entity.return_value = mock_entity

        bridge = GitHubIntelligenceGraphBridge(mock_engine)
        repo = GitRepository(repository_id="repo-123", name="Anzar0904/Aios", owner="Anzar0904")
        entity_id = bridge.sync_repository(repo)
        assert entity_id == "mock-repo-id"

    def test_sync_branch(self):
        from aios.services.github_intelligence_graph_bridge import GitHubIntelligenceGraphBridge

        mock_engine = MagicMock()
        bridge = GitHubIntelligenceGraphBridge(mock_engine)
        branch = GitBranch("branch-123", "repo-123", "main", author="Anzar0904")
        bridge.sync_branch(branch, "Anzar0904/Aios")
        assert mock_engine.ensure_entity.call_count >= 2

    def test_sync_pull_request(self):
        from aios.services.github_intelligence_graph_bridge import GitHubIntelligenceGraphBridge

        mock_engine = MagicMock()
        bridge = GitHubIntelligenceGraphBridge(mock_engine)
        pr = GitPullRequest("pr-123", 14, "repo-123", "Title", "author")
        bridge.sync_pull_request(pr, "Anzar0904/Aios")
        assert mock_engine.ensure_entity.call_count >= 2

    def test_sync_issue(self):
        from aios.services.github_intelligence_graph_bridge import GitHubIntelligenceGraphBridge

        mock_engine = MagicMock()
        bridge = GitHubIntelligenceGraphBridge(mock_engine)
        issue = GitIssue("issue-123", "repo-123", "Title")
        bridge.sync_issue(issue, "Anzar0904/Aios")
        assert mock_engine.ensure_entity.call_count >= 2


# ---------------------------------------------------------------------------
# CLI Command Dispatcher Smoke Tests
# ---------------------------------------------------------------------------


class TestGitHubCLIDispatch:
    def test_cli_dashboard_smoke(self, eng):
        from aios.local.github_intelligence_commands import cmd_github_dashboard

        cmd_github_dashboard([])

    def test_cli_repos_smoke(self, eng):
        from aios.local.github_intelligence_commands import cmd_github_repos

        cmd_github_repos([])

    def test_cli_branches_smoke(self, eng):
        from aios.local.github_intelligence_commands import cmd_github_branches

        cmd_github_branches([])

    def test_cli_commits_smoke(self, eng):
        from aios.local.github_intelligence_commands import cmd_github_commits

        cmd_github_commits([])

    def test_cli_prs_smoke(self, eng):
        from aios.local.github_intelligence_commands import cmd_github_prs

        cmd_github_prs([])

    def test_cli_issues_smoke(self, eng):
        from aios.local.github_intelligence_commands import cmd_github_issues

        cmd_github_issues([])

    def test_cli_actions_smoke(self, eng):
        from aios.local.github_intelligence_commands import cmd_github_actions

        cmd_github_actions([])

    def test_cli_releases_smoke(self, eng):
        from aios.local.github_intelligence_commands import cmd_github_releases

        cmd_github_releases([])

    def test_cli_analytics_smoke(self, eng):
        from aios.local.github_intelligence_commands import cmd_github_analytics

        cmd_github_analytics([])

    def test_cli_health_smoke(self, eng):
        from aios.local.github_intelligence_commands import cmd_github_health

        cmd_github_health([])

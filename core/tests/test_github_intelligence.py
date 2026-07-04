import pytest
from unittest.mock import MagicMock, patch
import httpx

from aios.brain.skill_selector import SkillSelector
from aios.brain.models import SkillSelection
from aios.skills.registry import SkillRegistry
from aios.skills.base import BaseSkill

from aios.services.intent import Intent, IntentType
from aios.services.agent import AgentContext
from aios.services.agent_impl import CareerAgent
from aios.services.model import LLMResponse
from aios.services.github import (
    GitHubAuthentication,
    GitHubCache,
    GitHubRepository,
    GitHubPullRequest,
    GitHubIssue,
    GitHubCommit,
    GitHubBranch,
    GitHubRelease,
    GitHubWorkflow,
)
from aios.services.github_impl import LocalGitHubService


def test_github_authentication():
    auth = GitHubAuthentication(token="test-token")
    headers = auth.get_headers()
    assert headers["Authorization"] == "Bearer test-token"
    assert headers["Accept"] == "application/vnd.github+json"

    no_auth = GitHubAuthentication(token=None)
    assert "Authorization" not in no_auth.get_headers()


@patch("httpx.Client")
def test_repository_retrieval(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value.__enter__.return_value = mock_client
    
    # Mock Repository metadata and languages
    mock_response_repo = MagicMock()
    mock_response_repo.status_code = 200
    mock_response_repo.headers = {"Content-Type": "application/json"}
    mock_response_repo.json.return_value = {
        "owner": {"login": "Anzar0904"},
        "name": "aios",
        "description": "Personal AI OS",
        "stargazers_count": 42,
        "forks_count": 7,
        "html_url": "https://github.com/Anzar0904/aios",
        "private": True,
        "open_issues_count": 3,
    }
    
    mock_response_langs = MagicMock()
    mock_response_langs.status_code = 200
    mock_response_langs.headers = {"Content-Type": "application/json"}
    mock_response_langs.json.return_value = {"Python": 12345, "Shell": 500}
    
    mock_client.get.side_effect = [mock_response_repo, mock_response_langs]

    model_service = MagicMock()
    service = LocalGitHubService(model_service=model_service)
    
    repo = service.inspect_repository("Anzar0904/aios")
    assert repo.owner == "Anzar0904"
    assert repo.name == "aios"
    assert repo.stars == 42
    assert repo.is_private is True
    assert "Python" in repo.languages


@patch("httpx.Client")
def test_pull_requests(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value.__enter__.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "number": 12,
        "title": "Refactor router",
        "state": "open",
        "body": "PR description",
        "user": {"login": "dev1"},
        "html_url": "https://github.com/Anzar0904/aios/pull/12",
        "diff_url": "https://github.com/Anzar0904/aios/pull/12.diff",
        "created_at": "2026-07-04T12:00:00Z",
    }
    mock_client.get.return_value = mock_response

    model_service = MagicMock()
    service = LocalGitHubService(model_service=model_service)
    pr = service.inspect_pull_request("Anzar0904/aios", 12)
    assert pr.number == 12
    assert pr.title == "Refactor router"
    assert pr.user == "dev1"


@patch("httpx.Client")
def test_issues(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value.__enter__.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "number": 5,
        "title": "Crash on boot",
        "state": "closed",
        "body": "Crash log snippet",
        "user": {"login": "user1"},
        "labels": [{"name": "bug"}, {"name": "critical"}],
        "milestone": {"title": "v1.0.0"},
        "created_at": "2026-07-04T10:00:00Z",
    }
    mock_client.get.return_value = mock_response

    model_service = MagicMock()
    service = LocalGitHubService(model_service=model_service)
    issue = service.inspect_issue("Anzar0904/aios", 5)
    assert issue.number == 5
    assert "bug" in issue.labels
    assert issue.milestone == "v1.0.0"


@patch("httpx.Client")
def test_commits_and_branches(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value.__enter__.return_value = mock_client
    
    # Mock branches response
    mock_response_branches = MagicMock()
    mock_response_branches.status_code = 200
    mock_response_branches.headers = {"Content-Type": "application/json"}
    mock_response_branches.json.return_value = [
        {"name": "main", "commit": {"sha": "sha123"}}
    ]
    mock_client.get.return_value = mock_response_branches

    model_service = MagicMock()
    service = LocalGitHubService(model_service=model_service)
    branches = service.list_branches("Anzar0904/aios")
    assert len(branches) == 1
    assert branches[0].name == "main"
    assert branches[0].sha == "sha123"


@patch("httpx.Client")
def test_caching(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value.__enter__.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"owner": {"login": "Anzar0904"}, "name": "aios"}
    mock_client.get.return_value = mock_response

    model_service = MagicMock()
    service = LocalGitHubService(model_service=model_service, cache_enabled=True)
    
    # First call: cache miss, makes request
    service.inspect_repository("Anzar0904/aios")
    # Second call: cache hit, uses cache
    service.inspect_repository("Anzar0904/aios")
    
    assert mock_client.get.call_count == 2  # 1 for repo and 1 for languages (cached on second run)


@patch("httpx.Client")
def test_retries_transient_failures(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value.__enter__.return_value = mock_client
    
    # Return 500 first, then 200
    mock_response_500 = MagicMock()
    mock_response_500.status_code = 500
    
    mock_response_200 = MagicMock()
    mock_response_200.status_code = 200
    mock_response_200.headers = {"Content-Type": "application/json"}
    mock_response_200.json.return_value = {"owner": {"login": "Anzar0904"}, "name": "aios"}

    mock_client.get.side_effect = [mock_response_500, mock_response_200, mock_response_200]

    model_service = MagicMock()
    service = LocalGitHubService(model_service=model_service, max_retries=3, rate_limit_per_min=0)
    
    with patch("time.sleep") as mock_sleep:
        repo = service.inspect_repository("Anzar0904/aios")
        assert repo.name == "aios"
        mock_sleep.assert_called_once_with(1)  # wait 2^0 = 1 second on attempt 1


def test_offline_mode():
    model_service = MagicMock()
    service = LocalGitHubService(model_service=model_service, offline_mode=True)
    
    with pytest.raises(httpx.ConnectError):
        service.inspect_repository("Anzar0904/aios")


def test_rate_limiting():
    model_service = MagicMock()
    service = LocalGitHubService(
        model_service=model_service,
        rate_limit_per_min=6000,  # high frequency but short interval (0.01s)
    )
    assert service._request_interval == 0.01


def test_brain_integration():
    skill_registry = MagicMock()
    mock_skill = MagicMock(spec=BaseSkill)
    mock_metadata = MagicMock()
    mock_metadata.id = "github"
    mock_metadata.commands = ["list repositories"]
    mock_skill.metadata = mock_metadata
    mock_skill.enabled = True
    
    skill_registry.list_skills.return_value = [mock_skill]
    
    selector = SkillSelector(skill_registry)
    
    # Query containing 'repository' keyword
    selections = selector.select_skills("list my GitHub repositories please")
    assert len(selections) == 1
    assert selections[0].skill_id == "github"
    assert selections[0].confidence == 0.99



@patch("httpx.Client")
def test_career_agent_integration(mock_client_class):
    mock_client = MagicMock()
    mock_client_class.return_value.__enter__.return_value = mock_client
    
    # Mock search repositories return
    mock_response_search = MagicMock()
    mock_response_search.status_code = 200
    mock_response_search.headers = {"Content-Type": "application/json"}
    mock_response_search.json.return_value = {
        "items": [
            {
                "owner": {"login": "Anzar0904"},
                "name": "aios",
                "description": "AI OS",
                "stargazers_count": 10,
                "forks_count": 2,
                "private": False,
                "open_issues_count": 0,
            }
        ]
    }
    
    # Mock repository stats return
    mock_response_stats = MagicMock()
    mock_response_stats.status_code = 200
    mock_response_stats.headers = {"Content-Type": "application/json"}
    mock_response_stats.json.return_value = {
        "stargazers_count": 10,
        "forks_count": 2,
        "open_issues_count": 0,
    }
    
    mock_client.get.side_effect = [mock_response_search, mock_response_stats]

    memory_service = MagicMock()
    context_service = MagicMock()
    tool_service = MagicMock()
    model_service = MagicMock()
    
    model_service.execute_request.return_value = LLMResponse(
        content="Analyzed GitHub profile.",
        model_name="claude-3-5-sonnet",
        provider_name="claude",
    )

    github_service = LocalGitHubService(model_service=model_service)
    
    agent = CareerAgent(
        memory_service=memory_service,
        context_service=context_service,
        tool_service=tool_service,
        model_service=model_service,
        github_service=github_service,
    )
    
    intent = Intent(
        intent_type=IntentType.CAREER,
        target_service="AgentRuntimeService",
        action="GitHubPortfolio",
        parameters={"username": "Anzar0904"},
        confidence=1.0,
    )
    
    agent_context = AgentContext(intent=intent, context=None, memories=[], tools=[])

    res = agent.execute(agent_context)
    
    assert res.success is True
    assert "Analyzed GitHub profile." in res.response
    model_service.execute_request.assert_called_once()

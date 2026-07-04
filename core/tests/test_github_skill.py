import os
import tempfile
from unittest.mock import MagicMock, patch

from aios.services.agent import AgentContext
from aios.services.command import CommandRegistry
from aios.services.intent import Intent, IntentType
from aios.services.model import LLMResponse

from skills.github.agent import GitHubAgent, render_template
from skills.github.commands import (
    parse_repo_and_args,
    register_commands,
)
from skills.github.github_client import EncryptedConfig, GitHubClient


def test_encrypted_config():
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = os.path.join(tmpdir, "config.json")
        config = EncryptedConfig(config_path)

        # Test no file
        assert config.load_token() is None

        # Test save and load
        test_token = "ghp_1234567890abcdef"
        config.save_token(test_token)

        loaded = config.load_token()
        assert loaded == test_token


def test_github_client_mock_fallbacks():
    client = GitHubClient(token=None)
    # Ensure env variable override doesn't interfere
    with patch.dict(os.environ, {}, clear=True):
        client.token = None

        # Test repositories
        repos = client.list_repositories()
        assert len(repos) == 2
        assert repos[0].name == "aios"

        # Test PR
        pr = client.get_pr("owner", "repo", 42)
        assert pr.number == 42
        assert "Mock PR" in pr.title

        # Test Issue
        issue = client.get_issue("owner", "repo", 7)
        assert issue.number == 7
        assert "Mock Issue" in issue.title

        # Test Workflows
        wfs = client.list_workflows("owner", "repo")
        assert len(wfs) == 2

        # Test Latest Release
        rel = client.get_latest_release("owner", "repo")
        assert rel.tag_name == "v1.0.0"

        # Test Commits
        commits = client.list_commits("owner", "repo")
        assert len(commits) == 2

        # Test Tags
        tags = client.list_tags("owner", "repo")
        assert len(tags) == 2
        assert tags[0].name == "v1.0.0"


def test_render_template(tmp_path):
    template_file = tmp_path / "test_template.md"
    template_file.write_text("Hello {{ name }}! Welcome to {{ place }}.", encoding="utf-8")

    rendered = render_template(template_file, {"name": "Alice", "place": "AI OS"})
    assert rendered == "Hello Alice! Welcome to AI OS."


def test_github_agent_execution():
    memory_service = MagicMock()
    context_service = MagicMock()
    tool_service = MagicMock()
    model_service = MagicMock()

    # Stub ModelService execution response
    model_service.execute_request.return_value = LLMResponse(
        content="This is a mock LLM review output.",
        model_name="claude-3-5-sonnet",
        provider_name="claude",
    )

    agent = GitHubAgent(memory_service, context_service, tool_service, model_service)

    # Test Review PR
    agent_context = AgentContext(
        intent=Intent(
            intent_type=IntentType.DEVELOPER,
            target_service="AgentRuntimeService",
            action="ReviewPR",
            parameters={"owner": "test_owner", "repo": "test_repo", "number": 12},
            confidence=1.0,
        ),
        context=None,
        memories=[],
        tools=[],
    )

    res = agent.execute(agent_context)
    assert res.success is True
    assert "LLM review output" in res.response
    model_service.execute_request.assert_called()


def test_parse_repo_and_args():
    # Test input with owner/repo and extra args
    owner, repo, extra = parse_repo_and_args("Anzar0904/aios 15")
    assert owner == "Anzar0904"
    assert repo == "aios"
    assert extra == ["15"]

    # Test input without owner/repo
    with patch("skills.github.commands.get_local_repo_info") as mock_local:
        mock_local.return_value = ("local_owner", "local_repo")
        owner, repo, extra = parse_repo_and_args("42")
        assert owner == "local_owner"
        assert repo == "local_repo"
        assert extra == ["42"]


def test_register_commands():
    registry = CommandRegistry()
    kernel = MagicMock()
    conv_manager = MagicMock()

    register_commands(registry, kernel, conv_manager)

    # Verify commands exist in registry
    assert registry.get_command("github login") is not None
    assert registry.get_command("github status") is not None
    assert registry.get_command("list repositories") is not None
    assert registry.get_command("clone repository") is not None
    assert registry.get_command("review pull request") is not None
    assert registry.get_command("review issue") is not None

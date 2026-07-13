import os
import re
import subprocess
from typing import List, Optional, Tuple

import httpx
from aios.services.agent import AgentContext
from aios.services.command.metadata import CommandCategory, CommandMetadata
from aios.services.intent import Intent, IntentType

from skills.github.agent import GitHubAgent
from skills.github.github_client import EncryptedConfig, GitHubClient


def get_local_repo_info() -> Tuple[Optional[str], Optional[str]]:
    """Helper to detect owner and repo from local git configuration or remote url."""
    try:
        url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"], stderr=subprocess.DEVNULL, text=True
        ).strip()
        if not url:
            return None, None

        # Parse SSH or HTTPS urls
        # HTTPS: https://github.com/owner/repo.git or http://github.com/owner/repo
        # SSH: git@github.com:owner/repo.git
        match = re.search(r"github\.com[:/]([^/]+)/([^/.]+)(?:\.git)?$", url)
        if match:
            return match.group(1), match.group(2)
    except Exception:
        # Fallback to parsing .git/config manually
        try:
            if os.path.exists(".git/config"):
                with open(".git/config", "r") as f:
                    content = f.read()
                match = re.search(
                    r"url\s*=\s*(?:https://github\.com/|git@github\.com:)([^/]+)/([^/\n]+?)(?:\.git)?\s*$",
                    content,
                    re.MULTILINE,
                )
                if match:
                    return match.group(1), match.group(2)
        except Exception:
            pass
    return None, None


def parse_repo_and_args(args: str) -> Tuple[Optional[str], Optional[str], List[str]]:
    """
    Parses repository owner/repo and any extra positional arguments from command args.
    If owner/repo is omitted, attempts to auto-detect it from local git configuration.
    """
    parts = args.strip().split() if args else []

    if parts and "/" in parts[0] and not parts[0].startswith("http"):
        owner_repo = parts[0]
        extra = parts[1:]
        owner, repo = owner_repo.split("/", 1)
        return owner, repo, extra

    owner, repo = get_local_repo_info()
    return owner, repo, parts


def require_action_engine_approval(objective: str, steps: List[str]) -> bool:
    """Enforces approval for write actions."""
    print("\n==========================================")
    print("ACTION ENGINE APPROVAL REQUIRED")
    print(f"Objective: {objective}")
    print("Steps to execute:")
    for idx, step in enumerate(steps, 1):
        print(f"  {idx}. {step}")
    print("==========================================")
    confirm = input("Approve this action plan? (y/n): ").strip().lower()
    return confirm == "y"


def get_github_agent(kernel) -> GitHubAgent:
    from aios.services.context import ContextService
    from aios.services.memory import MemoryService
    from aios.services.model import ModelService
    from aios.services.tool import ToolService

    return GitHubAgent(
        memory_service=kernel.registry.get(MemoryService),
        context_service=kernel.registry.get(ContextService),
        tool_service=kernel.registry.get(ToolService),
        model_service=kernel.registry.get(ModelService),
    )


# --- Command Callbacks ---


def execute_github_login(args: str) -> None:
    print("GitHub Authentication Setup")
    token = input("Enter GitHub Personal Access Token: ").strip()
    if not token:
        print("Error: Token cannot be empty.")
        return
    EncryptedConfig().save_token(token)
    print("Success: Token encrypted and saved successfully.")


def execute_github_status(args: str) -> None:
    client = GitHubClient()
    if not client.token:
        print("GitHub Status: Not logged in. Using mock client.")
        return

    try:
        with httpx.Client() as http_client:
            res = http_client.get(f"{client.base_url}/user", headers=client._get_headers())
            if res.status_code == 200:
                user_data = res.json()
                msg = (
                    f"GitHub Status: Logged in as {user_data.get('login')} "
                    f"({user_data.get('name')})"
                )
                print(msg)
                print(f"Profile URL: {user_data.get('html_url')}")
            else:
                print(
                    f"GitHub Status: Token is present, but API returned status {res.status_code}."
                )
    except Exception as e:
        print(f"GitHub Status: Error connecting to GitHub: {e}")


def execute_list_repositories(args: str) -> None:
    client = GitHubClient()
    repos = client.list_repositories()
    if not repos:
        print("No repositories found.")
        return
    print("\nRepositories:")
    for r in repos:
        priv_str = " (Private)" if r.is_private else ""
        print(f"- {r.owner}/{r.name}{priv_str} - {r.url}")
    print()


def execute_clone_repository(args: str) -> None:
    parts = args.strip().split() if args else []
    if not parts:
        print(
            "Usage: clone repository <owner>/<repo> [dest_dir] or "
            "clone repository <clone_url> [dest_dir]"
        )
        return

    target = parts[0]
    dest_dir = parts[1] if len(parts) > 1 else ""

    if "github.com" in target or target.startswith("git@") or target.startswith("http"):
        clone_url = target
        repo_name = target.split("/")[-1].replace(".git", "")
    else:
        if "/" not in target:
            print("Error: Repository must be in owner/repo format or a valid git clone URL.")
            return
        clone_url = f"https://github.com/{target}.git"
        repo_name = target.split("/")[-1]

    dest = dest_dir or repo_name

    approved = require_action_engine_approval(
        objective="Clone repository to local filesystem",
        steps=[
            f"Download repository from URL: {clone_url}",
            f"Save repository into directory: {dest}",
        ],
    )
    if not approved:
        print("Action rejected by Action Engine.")
        return

    print(f"Cloning {clone_url} into {dest}...")
    try:
        subprocess.check_call(["git", "clone", clone_url, dest])
        print("Repository cloned successfully.")
    except Exception as e:
        print(f"Error cloning repository: {e}")


def execute_review_pr(kernel, args: str) -> None:
    owner, repo, extra = parse_repo_and_args(args)
    if not owner or not repo:
        print(
            "Error: Could not determine owner/repo. "
            "Specify as 'owner/repo <pr_number>' or run inside a git repo."
        )
        return
    if not extra:
        print("Usage: review pull request [<owner>/<repo>] <pr_number>")
        return
    pr_number = extra[0]

    agent = get_github_agent(kernel)
    agent_context = AgentContext(
        intent=Intent(
            intent_type=IntentType.DEVELOPER,
            target_service="AgentRuntimeService",
            action="ReviewPR",
            parameters={"owner": owner, "repo": repo, "number": pr_number},
            confidence=1.0,
        ),
        context=None,
        memories=[],
        tools=[],
    )
    print(f"Intelligently reviewing PR #{pr_number} for {owner}/{repo} using Developer Mode...")
    res = agent.execute(agent_context)
    if res.success:
        print("\n=== Pull Request Review ===")
        print(res.response)
    else:
        print(f"Error: {res.response}")


def execute_review_issue(kernel, args: str) -> None:
    owner, repo, extra = parse_repo_and_args(args)
    if not owner or not repo:
        print(
            "Error: Could not determine owner/repo. "
            "Specify as 'owner/repo <issue_number>' or run inside a git repo."
        )
        return
    if not extra:
        print("Usage: review issue [<owner>/<repo>] <issue_number>")
        return
    issue_number = extra[0]

    agent = get_github_agent(kernel)
    agent_context = AgentContext(
        intent=Intent(
            intent_type=IntentType.DEVELOPER,
            target_service="AgentRuntimeService",
            action="ReviewIssue",
            parameters={"owner": owner, "repo": repo, "number": issue_number},
            confidence=1.0,
        ),
        context=None,
        memories=[],
        tools=[],
    )
    print(f"Intelligently reviewing Issue #{issue_number} for {owner}/{repo}...")
    res = agent.execute(agent_context)
    if res.success:
        print("\n=== Issue Review ===")
        print(res.response)
    else:
        print(f"Error: {res.response}")


def execute_summarize_repository(kernel, args: str) -> None:
    owner, repo, extra = parse_repo_and_args(args)
    if not owner or not repo:
        print(
            "Error: Could not determine owner/repo. "
            "Specify as 'owner/repo' or run inside a git repo."
        )
        return

    agent = get_github_agent(kernel)
    agent_context = AgentContext(
        intent=Intent(
            intent_type=IntentType.DEVELOPER,
            target_service="AgentRuntimeService",
            action="SummarizeRepo",
            parameters={"owner": owner, "repo": repo},
            confidence=1.0,
        ),
        context=None,
        memories=[],
        tools=[],
    )
    print(f"Summarizing repository {owner}/{repo}...")
    res = agent.execute(agent_context)
    if res.success:
        print("\n=== Repository Summary ===")
        print(res.response)
    else:
        print(f"Error: {res.response}")


def execute_compare_branches(kernel, args: str) -> None:
    owner, repo, extra = parse_repo_and_args(args)
    if not owner or not repo:
        print("Error: Could not determine owner/repo. Specify as 'owner/repo <base> <head>'.")
        return
    if len(extra) < 2:
        print("Usage: compare branches [<owner>/<repo>] <base> <head>")
        return
    base, head = extra[0], extra[1]

    agent = get_github_agent(kernel)
    agent_context = AgentContext(
        intent=Intent(
            intent_type=IntentType.DEVELOPER,
            target_service="AgentRuntimeService",
            action="CompareBranches",
            parameters={"owner": owner, "repo": repo, "base": base, "head": head},
            confidence=1.0,
        ),
        context=None,
        memories=[],
        tools=[],
    )
    print(f"Comparing branch '{base}' and '{head}' for {owner}/{repo}...")
    res = agent.execute(agent_context)
    if res.success:
        print("\n=== Branch Comparison ===")
        print(res.response)
    else:
        print(f"Error: {res.response}")


def execute_generate_release_notes(kernel, args: str) -> None:
    owner, repo, extra = parse_repo_and_args(args)
    if not owner or not repo:
        print("Error: Could not determine owner/repo. Specify as 'owner/repo <tag_name>'.")
        return
    tag_name = extra[0] if extra else "v1.0.0"

    agent = get_github_agent(kernel)
    agent_context = AgentContext(
        intent=Intent(
            intent_type=IntentType.DEVELOPER,
            target_service="AgentRuntimeService",
            action="GenerateReleaseNotes",
            parameters={"owner": owner, "repo": repo, "tag_name": tag_name},
            confidence=1.0,
        ),
        context=None,
        memories=[],
        tools=[],
    )
    print(f"Generating release notes for tag '{tag_name}' of {owner}/{repo}...")
    res = agent.execute(agent_context)
    if res.success:
        print("\n=== Release Notes ===")
        print(res.response)
    else:
        print(f"Error: {res.response}")


def execute_create_issue(args: str) -> None:
    owner, repo, extra = parse_repo_and_args(args)
    if not owner or not repo:
        print(
            "Error: Could not determine owner/repo. "
            "Specify as 'owner/repo' or run inside a git repo."
        )
        return

    print(f"Creating new issue in {owner}/{repo}:")
    title = input("Enter issue title: ").strip()
    if not title:
        print("Error: Title is required.")
        return
    body = input("Enter issue body: ").strip()

    approved = require_action_engine_approval(
        objective=f"Create a GitHub Issue in {owner}/{repo}",
        steps=[f"Send POST request to create issue titled '{title}'"],
    )
    if not approved:
        print("Action rejected by Action Engine.")
        return

    client = GitHubClient()
    issue = client.create_issue(owner, repo, title, body)
    if issue:
        print(f"Success: Created issue #{issue.number} at {issue.html_url}")
    else:
        print("Failed to create issue.")


def execute_create_pr(args: str) -> None:
    owner, repo, extra = parse_repo_and_args(args)
    if not owner or not repo:
        print(
            "Error: Could not determine owner/repo. "
            "Specify as 'owner/repo' or run inside a git repo."
        )
        return

    print(f"Creating new Pull Request in {owner}/{repo}:")
    title = input("Enter PR title: ").strip()
    if not title:
        print("Error: Title is required.")
        return
    head = input("Enter head branch (source): ").strip()
    if not head:
        print("Error: Head branch is required.")
        return
    base = input("Enter base branch (target, default 'main'): ").strip() or "main"
    body = input("Enter PR body: ").strip()

    approved = require_action_engine_approval(
        objective=f"Create a Pull Request in {owner}/{repo}",
        steps=[f"Send POST request to merge '{head}' into '{base}' with title '{title}'"],
    )
    if not approved:
        print("Action rejected by Action Engine.")
        return

    client = GitHubClient()
    pr = client.create_pr(owner, repo, title, head, base, body)
    if pr:
        print(f"Success: Created Pull Request #{pr.number} at {pr.html_url}")
    else:
        print("Failed to create Pull Request.")


def execute_list_workflows(args: str) -> None:
    owner, repo, extra = parse_repo_and_args(args)
    if not owner or not repo:
        print(
            "Error: Could not determine owner/repo. "
            "Specify as 'owner/repo' or run inside a git repo."
        )
        return

    client = GitHubClient()
    wfs = client.list_workflows(owner, repo)
    if not wfs:
        print("No workflows found.")
        return
    print(f"\nWorkflows in {owner}/{repo}:")
    for w in wfs:
        print(f"- {w.name} (ID: {w.id}, State: {w.state}) - Path: {w.path}")
    print()


def execute_workflow_status(kernel, args: str) -> None:
    owner, repo, extra = parse_repo_and_args(args)
    if not owner or not repo:
        print(
            "Error: Could not determine owner/repo. "
            "Specify as 'owner/repo' or run inside a git repo."
        )
        return

    client = GitHubClient()
    runs = client.get_workflow_runs(owner, repo)
    if not runs:
        print("No workflow runs found.")
        return

    print(f"\nLatest Workflow Runs in {owner}/{repo}:")
    for r in runs[:5]:
        conclusion = r.get("conclusion") or r.get("status")
        is_success = conclusion == "success"
        conclusion_marker = "✓" if is_success else "✗" if conclusion == "failure" else "..."
        print(f"[{conclusion_marker}] {r.get('name')} - {conclusion} - Run ID: {r.get('id')}")

    latest_run = runs[0]
    if latest_run.get("conclusion") == "failure":
        print("\nDetected failure in latest workflow run. Generating CI log explanation...")
        agent = get_github_agent(kernel)
        agent_context = AgentContext(
            intent=Intent(
                intent_type=IntentType.DEVELOPER,
                target_service="AgentRuntimeService",
                action="ExplainCIFailures",
                parameters={"owner": owner, "repo": repo},
                confidence=1.0,
            ),
            context=None,
            memories=[],
            tools=[],
        )
        res = agent.execute(agent_context)
        if res.success:
            print("\n=== CI Failure Explanation ===")
            print(res.response)
        else:
            print(f"Error explaining failure: {res.response}")


def execute_latest_release(args: str) -> None:
    owner, repo, extra = parse_repo_and_args(args)
    if not owner or not repo:
        print(
            "Error: Could not determine owner/repo. "
            "Specify as 'owner/repo' or run inside a git repo."
        )
        return

    client = GitHubClient()
    rel = client.get_latest_release(owner, repo)
    if not rel:
        print(f"No releases found for {owner}/{repo}.")
        return
    print(f"\nLatest Release for {owner}/{repo}:")
    print(f"Tag: {rel.tag_name}")
    print(f"Name: {rel.name}")
    print(f"Published: {rel.published_at}")
    print(f"Release Notes:\n{rel.body}")
    print()


# --- Registration ---


def register_commands(registry, kernel, conv_manager) -> None:
    # Register the github_agent in the Agent Runtime Service if possible
    try:
        from aios.services.agent import AgentRuntimeService

        agent_runtime = kernel.registry.get(AgentRuntimeService)
        github_agent = get_github_agent(kernel)
        agent_runtime.register_agent(github_agent)
    except Exception:
        pass

    # 1. github login
    registry.register_command(
        CommandMetadata(
            name="github login",
            description="Log in to GitHub via Personal Access Token.",
            category=CommandCategory.AUTOMATION,
            required_agent="github_agent",
            required_tools=["filesystem"],
            example_usage="github login",
        ),
        execute_github_login,
    )

    # 2. github status
    registry.register_command(
        CommandMetadata(
            name="github status",
            description="Check GitHub login status.",
            category=CommandCategory.AUTOMATION,
            required_agent="github_agent",
            required_tools=[],
            example_usage="github status",
        ),
        execute_github_status,
    )

    # 3. list repositories
    registry.register_command(
        CommandMetadata(
            name="list repositories",
            description="List authenticated user's repositories.",
            category=CommandCategory.AUTOMATION,
            required_agent="github_agent",
            required_tools=[],
            example_usage="list repositories",
        ),
        execute_list_repositories,
    )

    # 4. clone repository
    registry.register_command(
        CommandMetadata(
            name="clone repository",
            description="Clone a repository to local filesystem.",
            category=CommandCategory.AUTOMATION,
            required_agent="github_agent",
            required_tools=["filesystem", "git"],
            example_usage="clone repository Anzar0904/aios",
        ),
        execute_clone_repository,
    )

    # 5. review pull request
    registry.register_command(
        CommandMetadata(
            name="review pull request",
            description="Review a pull request using Developer Mode.",
            category=CommandCategory.AUTOMATION,
            required_agent="github_agent",
            required_tools=[],
            example_usage="review pull request Anzar0904/aios 12",
        ),
        lambda args: execute_review_pr(kernel, args),
    )

    # 6. review issue
    registry.register_command(
        CommandMetadata(
            name="review issue",
            description="Review an issue using Developer Mode.",
            category=CommandCategory.AUTOMATION,
            required_agent="github_agent",
            required_tools=[],
            example_usage="review issue Anzar0904/aios 5",
        ),
        lambda args: execute_review_issue(kernel, args),
    )

    # 7. summarize repository
    registry.register_command(
        CommandMetadata(
            name="summarize repository",
            description="Summarize repository structure and README.",
            category=CommandCategory.AUTOMATION,
            required_agent="github_agent",
            required_tools=[],
            example_usage="summarize repository Anzar0904/aios",
        ),
        lambda args: execute_summarize_repository(kernel, args),
    )

    # 8. compare branches
    registry.register_command(
        CommandMetadata(
            name="compare branches",
            description="Compare branch changes.",
            category=CommandCategory.AUTOMATION,
            required_agent="github_agent",
            required_tools=[],
            example_usage="compare branches Anzar0904/aios main dev",
        ),
        lambda args: execute_compare_branches(kernel, args),
    )

    # 9. generate release notes
    registry.register_command(
        CommandMetadata(
            name="generate release notes",
            description="Generate release notes.",
            category=CommandCategory.AUTOMATION,
            required_agent="github_agent",
            required_tools=[],
            example_usage="generate release notes Anzar0904/aios v1.0.0",
        ),
        lambda args: execute_generate_release_notes(kernel, args),
    )

    # 10. create issue
    registry.register_command(
        CommandMetadata(
            name="create issue",
            description="Create a new issue on GitHub.",
            category=CommandCategory.AUTOMATION,
            required_agent="github_agent",
            required_tools=[],
            example_usage="create issue Anzar0904/aios",
        ),
        execute_create_issue,
    )

    # 11. create pull request
    registry.register_command(
        CommandMetadata(
            name="create pull request",
            description="Create a new pull request on GitHub.",
            category=CommandCategory.AUTOMATION,
            required_agent="github_agent",
            required_tools=[],
            example_usage="create pull request Anzar0904/aios",
        ),
        execute_create_pr,
    )

    # 12. list workflows
    registry.register_command(
        CommandMetadata(
            name="list workflows",
            description="List actions workflows.",
            category=CommandCategory.AUTOMATION,
            required_agent="github_agent",
            required_tools=[],
            example_usage="list workflows Anzar0904/aios",
        ),
        execute_list_workflows,
    )

    # 13. workflow status
    registry.register_command(
        CommandMetadata(
            name="workflow status",
            description="Check status of actions workflows.",
            category=CommandCategory.AUTOMATION,
            required_agent="github_agent",
            required_tools=[],
            example_usage="workflow status Anzar0904/aios",
        ),
        lambda args: execute_workflow_status(kernel, args),
    )

    # 14. latest release
    registry.register_command(
        CommandMetadata(
            name="latest release",
            description="Get the latest release of a repository.",
            category=CommandCategory.AUTOMATION,
            required_agent="github_agent",
            required_tools=[],
            example_usage="latest release Anzar0904/aios",
        ),
        execute_latest_release,
    )

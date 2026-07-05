# GitHub Skill Pro

Deep integration with GitHub for repositories, branches, pull requests, issues, releases, commits, tags, and workflows.

## Architecture

GitHub Skill Pro consists of the following components:
- `skill.toml`: Skill metadata defining version, category, commands, and requirements.
- `models.py`: Strongly typed dataclasses representing GitHub resources (PRs, Issues, Workflows, Commits, Tags).
- `github_client.py`: API wrapper supporting authentication via Token, Env variables, and encrypted configuration.
- `agent.py`: Agent logic consumed by the AI OS to review PRs/issues, analyze failures, compare branches, and draft release notes.
- `commands.py`: Command metadata and registration handlers mapping CLI inputs to agent actions.

## Commands

- `github login`: Prompt for and securely encrypt GitHub Personal Access Token.
- `github status`: Verify authentication state and display current user status.
- `list repositories`: List all repositories owned or accessible by the user.
- `clone repository`: Clone a GitHub repository locally (requires Action Engine approval).
- `review pull request`: Fetch and analyze PR diffs using Developer Mode.
- `review issue`: Review GitHub issues, summarize them, and suggest fixes.
- `summarize repository`: Perform architectural and structural summaries of a repository.
- `compare branches`: Compare two branches and summarize functional changes.
- `generate release notes`: Generate structured release notes from commit history.
- `create issue`: Create a new issue on GitHub (requires Action Engine approval).
- `create pull request`: Create a new pull request on GitHub (requires Action Engine approval).
- `list workflows`: List all GitHub Actions workflows.
- `workflow status`: Check status of workflows, and explain logs if failed.
- `latest release`: Get the latest release metadata.

## Security and Constraints

- **Action Engine Approval**: Write actions (cloning, creating issues/PRs) explicitly prompt for approval before execution.
- **Local Encryption**: Personal Access Tokens are encrypted locally via base64 XOR.

import logging
from pathlib import Path
from typing import Any, Dict

from aios.services.agent import Agent, AgentContext, AgentResult
from aios.services.model import LLMRequest

from skills.github.github_client import GitHubClient

logger = logging.getLogger(__name__)


def render_template(template_path: Path, context: Dict[str, Any]) -> str:
    if not template_path.is_file():
        return ""
    content = template_path.read_text(encoding="utf-8")
    for k, v in context.items():
        content = content.replace(f"{{{{ {k} }}}}", str(v))
        content = content.replace(f"{{{{{k}}}}}", str(v))
        content = content.replace(f"{{{k}}}", str(v))
    return content


class GitHubAgent(Agent):
    def __init__(
        self,
        memory_service,
        context_service,
        tool_service,
        model_service,
    ) -> None:
        self._memory_service = memory_service
        self._context_service = context_service
        self._tool_service = tool_service
        self._model_service = model_service

    @property
    def name(self) -> str:
        return "github_agent"

    @property
    def description(self) -> str:
        return (
            "GitHub agent for reviewing pull requests, issues, commits, "
            "and releases using Developer Mode."
        )

    def execute(self, agent_context: AgentContext) -> AgentResult:
        intent = agent_context.intent
        action = intent.action
        params = intent.parameters

        templates_dir = Path(__file__).parent / "prompts"
        client = GitHubClient()

        owner = params.get("owner")
        repo = params.get("repo")

        if action == "ReviewPR":
            pr_number = params.get("number")
            if not pr_number:
                return AgentResult(success=False, response="PR number is required.")

            pr = client.get_pr(owner, repo, int(pr_number))
            if not pr:
                return AgentResult(success=False, response=f"PR #{pr_number} not found.")

            diff = client.get_pr_diff(owner, repo, int(pr_number))

            template_path = templates_dir / "review_pr.md"
            prompt = render_template(
                template_path,
                {
                    "pr_title": pr.title,
                    "pr_body": pr.body or "No description provided.",
                    "pr_diff": diff,
                },
            )

            llm_res = self._model_service.execute_request(
                LLMRequest(
                    prompt=prompt,
                    system_instruction=(
                        "You are a Senior GitHub Integration Engineer. Provide "
                        "developer-level code reviews focusing on SOLID, bugs, "
                        "security, and style."
                    ),
                    model_name="claude-3-5-sonnet",
                )
            )
            return AgentResult(success=True, response=llm_res.content)

        elif action == "ReviewIssue":
            issue_number = params.get("number")
            if not issue_number:
                return AgentResult(success=False, response="Issue number is required.")

            issue = client.get_issue(owner, repo, int(issue_number))
            if not issue:
                return AgentResult(success=False, response=f"Issue #{issue_number} not found.")

            template_path = templates_dir / "review_issue.md"
            prompt = render_template(
                template_path,
                {
                    "issue_title": issue.title,
                    "issue_body": issue.body or "No description provided.",
                },
            )

            llm_res = self._model_service.execute_request(
                LLMRequest(
                    prompt=prompt,
                    system_instruction=(
                        "You are an expert software developer. Review issues, "
                        "identify root causes, and suggest solutions."
                    ),
                    model_name="claude-3-5-sonnet",
                )
            )
            return AgentResult(success=True, response=llm_res.content)

        elif action == "SummarizeRepo":
            repo_details = client.list_repositories()
            repo_desc = ""
            for r in repo_details:
                if r.name == repo and r.owner == owner:
                    repo_desc = r.description or ""
                    break

            template_path = templates_dir / "summarize_repo.md"
            prompt = render_template(
                template_path,
                {
                    "repo_name": f"{owner}/{repo}",
                    "repo_description": repo_desc or "No description provided.",
                },
            )

            llm_res = self._model_service.execute_request(
                LLMRequest(
                    prompt=prompt,
                    system_instruction=(
                        "You are a software architect summarizing codebase structure."
                    ),
                    model_name="claude-3-5-sonnet",
                )
            )
            return AgentResult(success=True, response=llm_res.content)

        elif action == "CompareBranches":
            base = params.get("base")
            head = params.get("head")
            if not base or not head:
                return AgentResult(success=False, response="Base and head branches are required.")

            diff = client.compare_branches(owner, repo, base, head)

            template_path = templates_dir / "compare_branches.md"
            prompt = render_template(
                template_path, {"base_branch": base, "head_branch": head, "diff_content": diff}
            )

            llm_res = self._model_service.execute_request(
                LLMRequest(
                    prompt=prompt,
                    system_instruction=(
                        "You are a Senior Engineer. Compare branches and "
                        "summarize key additions/removals."
                    ),
                    model_name="claude-3-5-sonnet",
                )
            )
            return AgentResult(success=True, response=llm_res.content)

        elif action == "GenerateReleaseNotes":
            tag_name = params.get("tag_name", "v1.0.0")
            commits = client.list_commits(owner, repo)
            commit_msgs = "\n".join([f"- {c.message} (by {c.author})" for c in commits])

            template_path = templates_dir / "generate_release_notes.md"
            prompt = render_template(
                template_path, {"tag_name": tag_name, "commit_messages": commit_msgs}
            )

            llm_res = self._model_service.execute_request(
                LLMRequest(
                    prompt=prompt,
                    system_instruction="You are an AI OS technical writer drafting release notes.",
                    model_name="claude-3-5-sonnet",
                )
            )
            return AgentResult(success=True, response=llm_res.content)

        elif action == "ExplainCIFailures":
            wf_name, status, log_snippet = client.get_latest_failed_job_log(owner, repo)
            if not log_snippet:
                return AgentResult(
                    success=True,
                    response=f"No failed workflow runs or jobs found for {owner}/{repo}.",
                )

            template_path = templates_dir / "explain_ci_failure.md"
            prompt = render_template(
                template_path,
                {
                    "workflow_name": wf_name or "Unknown Workflow",
                    "workflow_status": status or "failed",
                    "error_logs": log_snippet,
                },
            )

            llm_res = self._model_service.execute_request(
                LLMRequest(
                    prompt=prompt,
                    system_instruction="You are a CI/CD DevOps expert analyzing build failures.",
                    model_name="claude-3-5-sonnet",
                )
            )
            return AgentResult(success=True, response=llm_res.content)

        elif action == "ReviewWorkflow":
            workflow_path = params.get("path")
            if not workflow_path:
                return AgentResult(success=False, response="Workflow file path is required.")

            read_res = self._tool_service.execute_tool(
                "filesystem", {"action": "read", "path": workflow_path}
            )
            if not read_res.success:
                return AgentResult(
                    success=False,
                    response=f"Failed to read workflow file '{workflow_path}': {read_res.error}",
                )

            workflow_content = read_res.output
            prompt = (
                f"You are a DevOps expert. Review the following GitHub workflow YAML file:\n\n"
                f"File: {workflow_path}\n"
                f"Content:\n{workflow_content}\n\n"
                f"Analyze it for efficiency, deprecations, potential security flaws, and syntax."
            )

            llm_res = self._model_service.execute_request(
                LLMRequest(
                    prompt=prompt,
                    system_instruction=(
                        "You are a DevOps expert. Review and critique GitHub workflow YAML files."
                    ),
                    model_name="claude-3-5-sonnet",
                )
            )
            return AgentResult(success=True, response=llm_res.content)

        else:
            return AgentResult(
                success=False, response=f"GitHubAgent action '{action}' is not supported."
            )

import logging
from typing import Any, Dict, Optional

from aios.services.agent import (
    Agent,
    AgentCompletedEvent,
    AgentContext,
    AgentFailedEvent,
    AgentResult,
    AgentRuntimeService,
    AgentStartedEvent,
)
from aios.services.career import JobApplication
from aios.services.context import ContextService
from aios.services.event_bus import EventBusService
from aios.services.intent import Intent, IntentType
from aios.services.memory import MemoryService, MemoryType
from aios.services.model import LLMRequest, ModelService
from aios.services.personal import Resume, ResumeVersion
from aios.services.tool import ToolService

logger = logging.getLogger(__name__)


class MockAgent(Agent):
    """Mock agent that simulates planning, reasoning, memory retrieval, tool

    execution, and returns structured responses.
    """

    def __init__(
        self,
        memory_service: MemoryService,
        context_service: ContextService,
        tool_service: ToolService,
    ) -> None:
        self._memory_service = memory_service
        self._context_service = context_service
        self._tool_service = tool_service

    @property
    def name(self) -> str:
        return "mock_agent"

    @property
    def description(self) -> str:
        return "Mock Agent for demonstrating the execution pipeline."

    def execute(self, agent_context: AgentContext) -> AgentResult:
        intent = agent_context.intent
        logger.info(f"MockAgent executing intent: {intent.intent_type.name}.{intent.action}")

        # Simulate reasoning steps
        reasoning = (
            f"[MockAgent] Reasoning:\n"
            f"  - Received intent: {intent.intent_type.name}.{intent.action}\n"
            f"  - Retrieved {len(agent_context.memories)} memories for workspace.\n"
            f"  - Available tools: {[t.name for t in agent_context.tools]}\n"
        )

        try:
            if intent.intent_type == IntentType.MEMORY:
                if intent.action == "Add":
                    content = intent.parameters.get("content", "")
                    memory = self._memory_service.add_memory(content, MemoryType.NOTE)
                    resp = (
                        f"{reasoning}"
                        f"  - Action: Storing content in Memory Service.\n"
                        f'✓ Memory stored successfully: "{content}" (ID: {memory.memory_id})'
                    )
                    return AgentResult(success=True, response=resp, data={"memory": memory})

            elif intent.intent_type == IntentType.CONTEXT:
                if intent.action == "Show":
                    context = agent_context.context
                    if context:
                        resp = (
                            f"{reasoning}"
                            f"  - Action: Loading workspace context.\n"
                            f"Current Context:\n"
                            f"  Workspace: {context.working_directory}\n"
                            f"  Project: {context.project_name}\n"
                            f"  Git Branch: {context.git_branch or 'non-git'}"
                        )
                        return AgentResult(success=True, response=resp, data={"context": context})
                    else:
                        return AgentResult(success=False, response="No active workspace context.")

            elif intent.intent_type == IntentType.SESSION:
                if intent.action == "End":
                    resp = (
                        f"{reasoning}"
                        f"  - Action: Ending active session.\n"
                        f"Session ended successfully."
                    )
                    return AgentResult(success=True, response=resp)

            elif intent.intent_type == IntentType.SYSTEM:
                if intent.action == "Status":
                    resp = (
                        f"{reasoning}"
                        f"  - Action: Retrieving OS status parameters.\n"
                        f"System Status: READY"
                    )
                    return AgentResult(success=True, response=resp)

                elif intent.action == "ToolList":
                    resp_lines = [
                        reasoning + "  - Action: Listing registered tools from Tool Manager.",
                        "Available Tools:",
                    ]
                    for t in agent_context.tools:
                        resp_lines.append(f"  - {t.name}: {t.description}")
                    return AgentResult(success=True, response="\n".join(resp_lines))

                elif intent.action == "ExecuteTool":
                    tool_name = intent.parameters.get("tool_name", "")
                    arguments = intent.parameters.get("arguments", {})

                    res = self._tool_service.execute_tool(tool_name, arguments)

                    resp = (
                        f"{reasoning}"
                        f"  - Action: Invoking tool '{tool_name}' with arguments {arguments}.\n"
                        f"Tool Output:\n{res.output}"
                    )
                    return AgentResult(success=res.success, response=resp, data={"result": res})

            return AgentResult(
                success=False,
                response=(
                    f"Execution for {intent.intent_type.name}.{intent.action} is not supported."
                ),
            )

        except Exception as e:
            return AgentResult(success=False, response=f"Agent execution exception: {e}")


class DeveloperAgent(Agent):
    """Developer Agent that helps develop software by orchestrating context,

    memories, tools (git, filesystem, terminal), and querying the LLM adapter.
    """

    def __init__(
        self,
        memory_service: MemoryService,
        context_service: ContextService,
        tool_service: ToolService,
        model_service: ModelService,
    ) -> None:
        self._memory_service = memory_service
        self._context_service = context_service
        self._tool_service = tool_service
        self._model_service = model_service

    @property
    def name(self) -> str:
        return "developer_agent"

    @property
    def description(self) -> str:
        return "Developer Agent for analyzing repositories, files, git status, and architecture."

    def execute(self, agent_context: AgentContext) -> AgentResult:
        from pathlib import Path

        from aios.services.conversation.manager import ConversationManager
        from aios.services.conversation.store import ConversationStore
        from aios.services.developer.builder import PromptBuilder
        from aios.services.developer.index import CodeIndex
        from aios.services.developer.scanner import RepositoryScanner
        from aios.services.developer.summary import WorkspaceSummary

        intent = agent_context.intent
        action = intent.action
        logger.info(f"DeveloperAgent v2 executing action: {action}")

        # Determine workspace root
        context = agent_context.context
        workspace_root = context.project_root if context else str(Path.cwd().resolve())

        # Initialize Scanner, Indexer, and Summary
        scanner = RepositoryScanner(workspace_root)
        index = CodeIndex(workspace_root)

        scan_results = scanner.scan()
        index_results = index.index()

        summary_gen = WorkspaceSummary(scan_results, index_results)
        workspace_summary = summary_gen.generate()

        # Determine templates directory (typically 'skills/developer/prompts' at project root)
        templates_dir = Path(workspace_root) / "skills" / "developer" / "prompts"
        builder = PromptBuilder(str(templates_dir))

        # Setup Conversation
        conv_store = ConversationStore(Path(workspace_root) / ".aios_conversations")
        conv_manager = ConversationManager(conv_store)

        raw_query = intent.parameters.get("raw_query", f"Run {action}")
        conv = conv_manager.get_current_conversation()
        if not conv:
            conv = conv_manager.create_conversation(
                title="Default Conversation", agent_name="developer_agent"
            )

        # Append User Message to Conversation
        conv_manager.add_message(conv.id, "user", raw_query)
        # Reload updated conversation
        conv = conv_manager.get_current_conversation()

        base_system_instruction = (
            "You are the Lead Software Engineer Developer Agent for this Personal AI OS.\n"
            "Analyze and reason about the codebase based on context and tool outputs provided.\n"
            "Focus on high-quality technical analysis, architectural structure, and code design.\n"
            "Do not execute automatic file modifications or perform autonomous actions."
        )

        try:
            # Format Conversation Summary
            conversation_summary = "No previous summary."
            if conv.summary:
                s = conv.summary
                conversation_summary = (
                    f"Summary: {s.summary}\n"
                    f"Decisions:\n" + "\n".join([f"- {d}" for d in s.decisions]) + "\n"
                    "Action Items:\n" + "\n".join([f"- {a}" for a in s.action_items]) + "\n"
                    "Unresolved Questions:\n"
                    + "\n".join([f"- {q}" for q in s.unresolved_questions])
                )

            # Format Conversation History (excluding the last user prompt we just appended)
            history_lines = []
            for m in conv.messages[:-1]:
                history_lines.append(f"{m.role.upper()}: {m.content}")
            conversation_history = (
                "\n".join(history_lines) if history_lines else "No previous messages."
            )

            extra_replacements = {}
            template_name = ""

            if action == "AnalyzeRepository":
                template_name = "analyze_repository"

            elif action == "ExplainFile":
                template_name = "explain_file"
                path = intent.parameters.get("path", "core/src/aios/kernel.py")
                read_res = self._tool_service.execute_tool(
                    "filesystem", {"action": "read", "path": path}
                )
                if not read_res.success:
                    return AgentResult(
                        success=False,
                        response=f"Failed to read file '{path}': {read_res.error}",
                    )
                extra_replacements["file_contents"] = read_res.output

            elif action == "SummarizeArchitecture":
                template_name = "summarize_architecture"

            elif action == "GitReview":
                template_name = "git_review"

            elif action == "ReviewRepository":
                template_name = "review_repository"

            elif action == "ReviewArchitecture":
                template_name = "review_architecture"

            elif action == "ReviewSecurity":
                template_name = "review_security"

            elif action == "AnalyzeDependencies":
                template_name = "analyze_dependencies"

            elif action == "DetectDeadCode":
                template_name = "detect_dead_code"

            elif action == "AnalyzeTodos":
                template_name = "analyze_todos"

            elif action == "ReviewTests":
                template_name = "review_tests"

            elif action == "ReviewGitChanges":
                template_name = "review_git_changes"

            elif action == "GenerateReleaseNotes":
                template_name = "generate_release_notes"

            elif action == "GenerateCommitMessage":
                template_name = "generate_commit_message"

            elif action == "InvestigateBug":
                template_name = "investigate_bug"
                bug_desc = intent.parameters.get("bug_description", "")
                if not bug_desc and "args" in intent.parameters:
                    bug_desc = intent.parameters["args"]
                extra_replacements["bug_description"] = bug_desc or "No description provided."

            elif action == "ExplainStackTrace":
                template_name = "explain_stack_trace"
                stack = intent.parameters.get("stack_trace", "")
                if not stack and "args" in intent.parameters:
                    stack = intent.parameters["args"]
                extra_replacements["stack_trace"] = stack or "No stack trace provided."

            elif action == "DetectCodeSmells":
                template_name = "detect_code_smells"

            elif action == "DetectDuplicateCode":
                template_name = "detect_duplicate_code"

            elif action == "SuggestRefactoring":
                template_name = "suggest_refactoring"

            else:
                return AgentResult(
                    success=False,
                    response=f"DeveloperAgent action '{action}' is not supported.",
                )

            # --- INTELLIGENCE ENGINE PIPELINE ---
            from aios.services.intelligence import (
                ContextRanker,
                IntentExpander,
                MemoryRanker,
                ReasoningContext,
                RepositoryAnalyzer,
                ToolSelector,
            )

            # 1. Repository Analyzer
            analyzer = RepositoryAnalyzer(scan_results, index_results)
            full_analysis = analyzer.analyze()

            # Merge extra_replacements into analysis dict for context ranking
            analysis_dict = {**full_analysis.__dict__, **extra_replacements}

            # 2. Context Ranker
            selected_context = ContextRanker().select_context(action, raw_query, analysis_dict)

            # 3. Memory Ranker
            ranked_memories = MemoryRanker(agent_context.memories).rank(
                raw_query, context.project_root if context else "default"
            )

            # Retrieve relevant semantic memories before reasoning
            class SemanticMemoryWrapper:
                class MockType:
                    def __init__(self, val: str) -> None:
                        self.value = val

                def __init__(self, content: str, mtype: str) -> None:
                    self.content = content
                    self.memory_type = self.MockType(mtype)

            try:
                from aios.registry import ServiceRegistry
                from aios.services.persistence import SemanticMemoryManager

                registry = ServiceRegistry._global_registry
                if registry:
                    sem_mgr = registry.get(SemanticMemoryManager)
                    if sem_mgr:
                        for repo in [
                            "engineering_memory",
                            "workspace_memory",
                            "documentation_memory",
                        ]:
                            mems = sem_mgr.retrieve_memories(repo, raw_query, limit=3)
                            for m in mems:
                                payload = m.get("payload", {})
                                text = payload.get("text", "")
                                if text:
                                    wrapped = SemanticMemoryWrapper(text, f"semantic_{repo}")
                                    ranked_memories.append(wrapped)
            except Exception as e:
                logger.warning(f"DeveloperAgent: Failed to retrieve semantic memories: {e}")

            # 4. Tool Selector
            selected_tools = ToolSelector().select_tools(intent)

            # 5. Intent Expander
            expanded_query = IntentExpander().expand(intent)

            # 6. Assemble Reasoning Context
            project_name = workspace_summary.get("project", {}).get("project_name", "Unknown")
            reasoning_context = ReasoningContext(
                intent=intent,
                repository_analysis=selected_context,
                conversation_summary=conversation_summary,
                conversation_history=conversation_history,
                memories=ranked_memories,
                workspace={"project_name": project_name},
                selected_tools=selected_tools,
                expanded_query=expanded_query,
            )

            # 7. Prompt Builder consumes only ReasoningContext
            prompt = builder.build_prompt_from_reasoning_context(template_name, reasoning_context)

            # Execute Request to LLM
            llm_res = self._model_service.execute_request(
                LLMRequest(
                    prompt=prompt,
                    system_instruction=base_system_instruction,
                    model_name="claude-3-5-sonnet",
                )
            )

            # Store useful knowledge after reasoning
            try:
                import time

                from aios.registry import ServiceRegistry
                from aios.services.persistence import SemanticMemoryManager

                registry = ServiceRegistry._global_registry
                if registry:
                    sem_mgr = registry.get(SemanticMemoryManager)
                    if sem_mgr:
                        summary_text = (
                            f"Developer Agent Executed Action: {action}\n"
                            f"Query: {raw_query}\n"
                            f"Response Summary: {llm_res.content[:500]}..."
                        )
                        metadata = {
                            "action": action,
                            "query": raw_query,
                            "timestamp": time.time(),
                            "type": "developer_agent_reasoning",
                        }
                        import uuid

                        know_uuid = str(
                            uuid.uuid5(
                                uuid.NAMESPACE_DNS, f"dev_agent_{time.time()}_{raw_query[:10]}"
                            )
                        )
                        sem_mgr.index_memory(
                            repository_name="knowledge_memory",
                            entity_id=know_uuid,
                            text=summary_text,
                            metadata=metadata,
                            tags=["developer_agent", "reasoning_knowledge", action],
                        )
            except Exception as e:
                logger.warning(f"DeveloperAgent: Failed to store reasoning knowledge: {e}")

            # Append Assistant Message to Conversation
            conv_manager.add_message(conv.id, "assistant", llm_res.content)
            # Reload to summarize if needed
            conv = conv_manager.get_current_conversation()
            conv_manager.summarize_if_needed(conv, self._model_service)

            return AgentResult(
                success=True,
                response=llm_res.content,
                data={"llm_response": llm_res, "workspace_summary": workspace_summary},
            )

        except Exception as e:
            logger.error(f"DeveloperAgent execution exception: {e}", exc_info=True)
            return AgentResult(success=False, response=f"DeveloperAgent execution exception: {e}")


class CareerAgent(Agent):
    """Career Agent to help prepare job applications by analyzing job descriptions,

    tailoring resumes, ATS scoring, and generating cover letters.
    """

    def __init__(
        self,
        memory_service: MemoryService,
        context_service: ContextService,
        tool_service: ToolService,
        model_service: ModelService,
        github_service: Optional[Any] = None,
        career_os: Optional[Any] = None,
        daily_os: Optional[Any] = None,
    ) -> None:
        self._memory_service = memory_service
        self._context_service = context_service
        self._tool_service = tool_service
        self._model_service = model_service
        self._github_service = github_service
        self._career_os = career_os
        self._daily_os = daily_os

    @property
    def name(self) -> str:
        return "career_agent"

    @property
    def description(self) -> str:
        return "Career Agent to help prepare job applications."

    def execute(self, agent_context: AgentContext) -> AgentResult:
        import json
        from pathlib import Path

        from aios.services.developer.builder import PromptBuilder

        intent = agent_context.intent
        action = intent.action
        logger.info(f"CareerAgent executing action: {action}")

        # Determine workspace root
        context = agent_context.context
        workspace_root = context.project_root if context else str(Path.cwd().resolve())

        # Determine templates directory (typically 'skills/career/prompts' at project root)
        templates_dir = Path(workspace_root) / "skills" / "career" / "prompts"
        builder = PromptBuilder(str(templates_dir))

        base_system_instruction = (
            "You are the Career Coach Agent for this Personal AI OS.\n"
            "Analyze and reason about the job requirements and user qualifications.\n"
            "Focus on high-quality technical analysis, skill matching, and tailored suggestions.\n"
            "Do not execute automatic file modifications or perform autonomous actions."
        )

        try:
            extra_replacements = {}
            template_name = ""

            if action == "AnalyzeJob":
                template_name = "analyze_job"
                job_path = intent.parameters.get("job_description_path", "job.pdf")
                read_res = self._tool_service.execute_tool(
                    "filesystem", {"action": "read", "path": job_path}
                )
                job_content = (
                    read_res.output
                    if read_res.success
                    else f"Placeholder job requirements for {job_path}."
                )
                if self._career_os:
                    analysis = self._career_os.job_analyzer.analyze_job(job_content)
                    return AgentResult(
                        success=True,
                        response=f"Job analysis complete:\n{json.dumps(analysis, indent=2)}",
                        data={"analysis": analysis},
                    )
                extra_replacements["job_path"] = job_path
                extra_replacements["job_content"] = job_content

            elif action == "TailorResume":
                template_name = "tailor_resume"
                resume_path = intent.parameters.get("resume_path", "resume.pdf")
                job_path = intent.parameters.get("job_description_path", "job.pdf")

                read_resume = self._tool_service.execute_tool(
                    "filesystem", {"action": "read", "path": resume_path}
                )
                resume_content = (
                    read_resume.output
                    if read_resume.success
                    else f"Placeholder resume content for {resume_path}."
                )

                read_job = self._tool_service.execute_tool(
                    "filesystem", {"action": "read", "path": job_path}
                )
                job_content = (
                    read_job.output
                    if read_job.success
                    else f"Placeholder job requirements for {job_path}."
                )
                if self._career_os:
                    # Construct active Resume and tailor
                    dummy_resume = Resume(
                        id="resume_tailored",
                        title="Tailored Resume",
                        versions=[ResumeVersion(version=1, summary=resume_content)],
                    )
                    optimized = self._career_os.resume_optimizer.tailor_resume(
                        dummy_resume, job_content
                    )
                    return AgentResult(
                        success=True,
                        response=f"Resume tailoring complete:\nSummary: {optimized.summary}\nProjects count: {len(optimized.projects)}",
                        data={"optimized_version": optimized},
                    )
                extra_replacements["resume_path"] = resume_path
                extra_replacements["resume_content"] = resume_content
                extra_replacements["job_path"] = job_path
                extra_replacements["job_content"] = job_content

            elif action == "ATSScore":
                template_name = "ats_score"
                resume_path = intent.parameters.get("resume_path", "resume.pdf")
                job_path = intent.parameters.get("job_description_path", "job.pdf")

                read_resume = self._tool_service.execute_tool(
                    "filesystem", {"action": "read", "path": resume_path}
                )
                resume_content = (
                    read_resume.output
                    if read_resume.success
                    else f"Placeholder resume content for {resume_path}."
                )

                read_job = self._tool_service.execute_tool(
                    "filesystem", {"action": "read", "path": job_path}
                )
                job_content = (
                    read_job.output
                    if read_job.success
                    else f"Placeholder job requirements for {job_path}."
                )
                if self._career_os:
                    dummy_version = ResumeVersion(version=1, summary=resume_content)
                    analysis = self._career_os.ats_analyzer.score_resume_against_job(
                        dummy_version, job_content
                    )
                    return AgentResult(
                        success=True,
                        response=f"ATS scoring complete:\n{json.dumps(analysis, indent=2)}",
                        data={"ats_analysis": analysis},
                    )
                extra_replacements["resume_content"] = resume_content
                extra_replacements["job_content"] = job_content

            elif action == "InterviewPrep":
                template_name = "interview_prep"
                job_path = intent.parameters.get("job_description_path", "job.pdf")
                read_res = self._tool_service.execute_tool(
                    "filesystem", {"action": "read", "path": job_path}
                )
                job_content = (
                    read_res.output
                    if read_res.success
                    else f"Placeholder job requirements for {job_path}."
                )
                if self._career_os:
                    company = intent.parameters.get("company", "Target Company")
                    role = intent.parameters.get("role", "Software Engineer")
                    prep = self._career_os.interview_coach.prepare_interview(company, role)
                    return AgentResult(
                        success=True,
                        response=f"Interview prep materials generated:\n{json.dumps(prep, indent=2)}",
                        data={"prep": prep},
                    )
                extra_replacements["job_content"] = job_content

            elif action == "CoverLetter":
                template_name = "cover_letter"
                resume_path = intent.parameters.get("resume_path", "resume.pdf")
                job_path = intent.parameters.get("job_description_path", "job.pdf")

                read_resume = self._tool_service.execute_tool(
                    "filesystem", {"action": "read", "path": resume_path}
                )
                resume_content = (
                    read_resume.output
                    if read_resume.success
                    else f"Placeholder resume content for {resume_path}."
                )

                read_job = self._tool_service.execute_tool(
                    "filesystem", {"action": "read", "path": job_path}
                )
                job_content = (
                    read_job.output
                    if read_job.success
                    else f"Placeholder job requirements for {job_path}."
                )
                if self._career_os:
                    dummy_version = ResumeVersion(version=1, summary=resume_content)
                    letter = self._career_os.cover_letter_generator.generate_cover_letter(
                        dummy_version, job_content
                    )
                    return AgentResult(
                        success=True,
                        response=f"Cover letter complete:\n{letter}",
                        data={"cover_letter": letter},
                    )
                extra_replacements["resume_content"] = resume_content
                extra_replacements["job_content"] = job_content

            elif action == "GitHubPortfolio":
                username = intent.parameters.get("username", "Anzar0904")
                if self._career_os:
                    analysis = self._career_os.portfolio_analyzer.analyze_portfolio(username)
                    return AgentResult(
                        success=True,
                        response=f"GitHub Portfolio analysis complete:\n{json.dumps(analysis, indent=2)}",
                        data={"analysis": analysis},
                    )

                if not self._github_service:
                    return AgentResult(
                        success=False, response="GitHubService is not configured for CareerAgent."
                    )

                try:
                    repos = self._github_service.search_repositories(f"user:{username}")
                except Exception as e:
                    return AgentResult(
                        success=False, response=f"Failed to fetch repositories for {username}: {e}"
                    )

                repos_details = []
                for r in repos[:5]:
                    try:
                        stats = self._github_service.get_repository_stats(f"{r.owner}/{r.name}")
                        repos_details.append(
                            {
                                "name": r.name,
                                "description": r.description,
                                "stars": stats.get("stars", 0),
                                "forks": stats.get("forks", 0),
                                "open_issues": stats.get("open_issues", 0),
                            }
                        )
                    except Exception:
                        pass

                prompt = (
                    f"You are the Career Coach Agent. Analyze the user's GitHub profile and repositories for portfolio building.\n\n"
                    f"GitHub Username: {username}\n"
                    f"Repositories:\n{json.dumps(repos_details, indent=2)}\n\n"
                    "Please analyze these repositories and generate a report on:\n"
                    "1. Profile Evaluation (Overall strength and technical focus)\n"
                    "2. Strongest Repositories (Select and rank the top projects)\n"
                    "3. Portfolio Summaries (Write elevator pitches for the best repositories)\n"
                    "4. Resume Recommendations (How to highlight these projects on a resume)\n"
                    "5. Active vs. Inactive status detection"
                )

                llm_res = self._model_service.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction=base_system_instruction,
                        model_name="claude-3-5-sonnet",
                    )
                )
                return AgentResult(
                    success=True, response=llm_res.content, data={"llm_response": llm_res}
                )

            elif action == "ListApplications":
                if self._career_os:
                    apps = self._career_os.application_tracker.list_applications()
                    return AgentResult(
                        success=True,
                        response=f"Applications tracked count: {len(apps)}",
                        data={"applications": apps},
                    )

            elif action == "AddApplication":
                if self._career_os:
                    app = JobApplication(
                        id=intent.parameters.get("id", "app_1"),
                        company=intent.parameters.get("company", "Default Company"),
                        role=intent.parameters.get("role", "Developer"),
                        status=intent.parameters.get("status", "applied"),
                        applied_date=intent.parameters.get("applied_date", "2026-07-04"),
                        notes=intent.parameters.get("notes", ""),
                    )
                    self._career_os.application_tracker.add_application(app)
                    return AgentResult(
                        success=True,
                        response=f"Successfully added application for {app.role} at {app.company}.",
                        data={"application": app},
                    )

            elif action == "GenerateCareerPlan":
                if self._career_os:
                    plan = self._career_os.career_planner.generate_plan()
                    return AgentResult(
                        success=True,
                        response=f"Career growth plan generated:\n{json.dumps(plan, indent=2)}",
                        data={"plan": plan},
                    )

            elif action == "MatchJobs":
                if self._career_os:
                    jobs = intent.parameters.get("jobs", ["Default Job description"])
                    matches = self._career_os.job_matcher.match_jobs(jobs)
                    return AgentResult(
                        success=True,
                        response=f"Matches summary count: {len(matches)}",
                        data={"matches": matches},
                    )

            elif action == "PlanDay":
                if self._daily_os:
                    plan = self._daily_os.planner.plan_day()
                    tasks_str = "\n".join(
                        [f"- [{t.priority}] {t.title} ({t.effort_hours}h)" for t in plan.tasks]
                    )
                    sched_str = "\n".join(
                        [f"- {item.time_slot}: {item.task_title}" for item in plan.schedule.items]
                    )
                    return AgentResult(
                        success=True,
                        response=f"Daily Plan generated for {plan.date}:\n\nTasks:\n{tasks_str}\n\nSchedule:\n{sched_str}",
                        data={"plan": plan},
                    )

            elif action == "UpdateTaskStatus":
                if self._daily_os:
                    tid = intent.parameters.get("task_id", "")
                    status = intent.parameters.get("status", "Completed")
                    pct = float(intent.parameters.get("completion_percentage", 100.0))
                    task = self._daily_os.progress_tracker.update_task_status(tid, status, pct)
                    return AgentResult(
                        success=True,
                        response=f"Task {tid} status updated to {status} ({pct}%).",
                        data={"task": task},
                    )

            elif action == "StartWorkSession":
                if self._daily_os:
                    tid = intent.parameters.get("task_id", "")
                    mid = intent.parameters.get("mission_id", "")
                    cat = intent.parameters.get("category", "focus")
                    notes = intent.parameters.get("notes", "")
                    session = self._daily_os.session_recorder.start_session(tid, mid, cat, notes)
                    return AgentResult(
                        success=True,
                        response=f"Work session started: {session.session_id}.",
                        data={"session": session},
                    )

            elif action == "EndWorkSession":
                if self._daily_os:
                    sid = intent.parameters.get("session_id", "")
                    notes = intent.parameters.get("notes", "")
                    session = self._daily_os.session_recorder.end_session(sid, notes)
                    return AgentResult(
                        success=True,
                        response=f"Work session {sid} ended. Duration: {session.duration_mins:.2f} mins.",
                        data={"session": session},
                    )

            elif action == "GenerateDailyReview":
                if self._daily_os:
                    review = self._daily_os.daily_review.generate_review()
                    return AgentResult(
                        success=True,
                        response=f"Daily Review:\nProductivity Rating/Summary: {review.productivity_summary}\nCompleted: {review.completed_tasks}\nIncomplete: {review.incomplete_tasks}",
                        data={"review": review},
                    )

            elif action == "AnalyzeProductivity":
                if self._daily_os:
                    metrics = self._daily_os.productivity_analyzer.analyze_productivity()
                    return AgentResult(
                        success=True,
                        response=f"Productivity Metrics:\nCompletion Rate: {metrics['completion_rate']}%\nFocus Time: {metrics['focus_time_mins']} mins\nPlanning Accuracy: {metrics['planning_accuracy_percentage']}%",
                        data={"metrics": metrics},
                    )

            else:
                return AgentResult(
                    success=False,
                    response=f"CareerAgent action '{action}' is not supported.",
                )

            # Build prompt
            prompt = builder.build_prompt(
                template_name=template_name,
                workspace_summary={},
                intent_action=action,
                intent_parameters=intent.parameters,
                memories=agent_context.memories,
                extra_replacements=extra_replacements,
            )

            # Query LLM
            llm_res = self._model_service.execute_request(
                LLMRequest(
                    prompt=prompt,
                    system_instruction=base_system_instruction,
                )
            )

            return AgentResult(
                success=True, response=llm_res.content, data={"llm_response": llm_res}
            )

        except Exception as e:
            return AgentResult(success=False, response=f"CareerAgent execution exception: {e}")


class LocalAgentRuntime(AgentRuntimeService):
    """Agent Runtime coordinating memory retrieval, context loading,

    and agent execution.
    """

    def __init__(
        self,
        event_bus: EventBusService,
        memory_service: MemoryService,
        context_service: ContextService,
        tool_service: ToolService,
        model_service: ModelService,
    ) -> None:
        self._event_bus = event_bus
        self._memory_service = memory_service
        self._context_service = context_service
        self._tool_service = tool_service
        self._model_service = model_service
        self._agents: Dict[str, Agent] = {}
        self._interrupted = False

    def initialize(self) -> None:
        logger.info("Initializing LocalAgentRuntime")
        self._event_bus.register_event_type(AgentStartedEvent)
        self._event_bus.register_event_type(AgentCompletedEvent)
        self._event_bus.register_event_type(AgentFailedEvent)

    def register_agent(self, agent: Agent) -> None:
        name = agent.name
        self._agents[name] = agent
        logger.info(f"Registered agent: {name}")

    def unregister_agent(self, name: str) -> None:
        if name in self._agents:
            del self._agents[name]
            logger.info(f"Unregistered agent: {name}")

    def execute(self, intent: Intent) -> AgentResult:
        self._interrupted = False
        logger.info(f"AgentRuntime executing intent: {intent.intent_type.name}.{intent.action}")

        self._event_bus.publish(AgentStartedEvent(intent=intent))

        try:
            context = self._context_service.get_current_context()

            workspace_id = context.project_root if context else ""
            memories = (
                self._memory_service.load_workspace_memory(workspace_id) if workspace_id else []
            )

            tools = self._tool_service.list_tools()

            agent_context = AgentContext(
                intent=intent,
                context=context,
                memories=memories,
                tools=tools,
            )

            # Route intents to corresponding agents
            if intent.intent_type == IntentType.DEVELOPER:
                agent = self._agents.get("developer_agent")
            elif intent.intent_type == IntentType.CAREER:
                agent = self._agents.get("career_agent")
            else:
                agent = self._agents.get("mock_agent")

            if not agent and self._agents:
                agent = next(iter(self._agents.values()))

            if not agent:
                raise RuntimeError("No active agent registered in the Agent Runtime.")

            result = agent.execute(agent_context)

            if result.success:
                self._event_bus.publish(AgentCompletedEvent(result=result))
            else:
                self._event_bus.publish(AgentFailedEvent(error=result.response))

            return result

        except Exception as e:
            err_msg = f"Agent Runtime execution failed: {e}"
            logger.error(err_msg, exc_info=True)
            self._event_bus.publish(AgentFailedEvent(error=err_msg))
            return AgentResult(success=False, response=err_msg)

    def interrupt(self) -> None:
        self._interrupted = True
        logger.info("Agent Runtime execution interrupted.")

    def cancel(self) -> None:
        self._interrupted = True
        logger.info("Agent Runtime execution cancelled.")

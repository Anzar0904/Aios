import logging
from typing import Dict

from aios.services.agent import (
    Agent,
    AgentCompletedEvent,
    AgentContext,
    AgentFailedEvent,
    AgentResult,
    AgentRuntimeService,
    AgentStartedEvent,
)
from aios.services.event_bus import EventBusService
from aios.services.intent import Intent, IntentType
from aios.services.memory import MemoryType
from aios.services.model import LLMRequest

logger = logging.getLogger(__name__)


class MockAgent(Agent):
    """Mock agent that simulates planning, reasoning, memory retrieval, tool

    execution, and returns structured responses.
    """

    def __init__(self, memory_service, context_service, tool_service) -> None:
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

    def __init__(self, memory_service, context_service, tool_service, model_service) -> None:
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
        intent = agent_context.intent
        action = intent.action
        logger.info(f"DeveloperAgent executing action: {action}")

        context = agent_context.context
        context_str = (
            f"Workspace: {context.working_directory}\n"
            f"Project Name: {context.project_name}\n"
            f"Git Branch: {context.git_branch or 'non-git'}"
            if context
            else "No active workspace context."
        )

        memories_str = (
            "\n".join([f"- [{m.memory_type.value}] {m.content}" for m in agent_context.memories])
            or "No relevant memories retrieved."
        )

        base_system_instruction = (
            "You are the Lead Software Engineer Developer Agent for this Personal AI OS.\n"
            "Analyze and reason about the codebase based on context and tool outputs provided.\n"
            "Focus on high-quality technical analysis, architectural structure, and code design.\n"
            "Do not execute automatic file modifications or perform autonomous actions."
        )

        try:
            if action == "AnalyzeRepository":
                list_res = self._tool_service.execute_tool(
                    "filesystem", {"action": "list", "path": "."}
                )
                files_list = list_res.output if list_res.success else "Failed to list files."

                prompt = (
                    f"Perform a repository analysis for the current workspace.\n\n"
                    f"Context Info:\n{context_str}\n\n"
                    f"Relevant Memories:\n{memories_str}\n\n"
                    f"Files in workspace root:\n{files_list}\n\n"
                    f"Please provide an overview of the workspace structure, its primary files, "
                    f"and main capabilities."
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

            elif action == "ExplainFile":
                path = intent.parameters.get("path", "core/src/aios/kernel.py")

                read_res = self._tool_service.execute_tool(
                    "filesystem", {"action": "read", "path": path}
                )
                if not read_res.success:
                    return AgentResult(
                        success=False,
                        response=f"Failed to read file '{path}': {read_res.error}",
                    )

                prompt = (
                    f"Explain the following file in the codebase.\n\n"
                    f"File Path: {path}\n\n"
                    f"File Contents:\n```python\n{read_res.output}\n```\n\n"
                    f"Please explain its purpose, key classes/functions, and role in the system."
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

            elif action == "SummarizeArchitecture":
                list_res = self._tool_service.execute_tool(
                    "filesystem", {"action": "list", "path": "."}
                )
                files_list = list_res.output if list_res.success else "Failed to list files."

                prompt = (
                    f"Summarize the system architecture.\n\n"
                    f"Workspace Context:\n{context_str}\n\n"
                    f"Relevant memories:\n{memories_str}\n\n"
                    f"Files in project root:\n{files_list}\n\n"
                    f"Describe the system architecture, component relationships, "
                    f"and service organization."
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

            elif action == "GitReview":
                status_res = self._tool_service.execute_tool("git", {"action": "status"})
                git_status = (
                    status_res.output if status_res.success else "Failed to get git status."
                )

                log_res = self._tool_service.execute_tool("git", {"action": "log"})
                git_log = log_res.output if log_res.success else "Failed to get git log."

                prompt = (
                    f"Perform a review of current git changes and recent history.\n\n"
                    f"Git Status:\n{git_status}\n\n"
                    f"Git Log (recent commits):\n{git_log}\n\n"
                    f"Please review the uncommitted changes, explain their purpose, "
                    f"and summarize progress."
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

            return AgentResult(
                success=False,
                response=f"DeveloperAgent action '{action}' is not supported.",
            )

        except Exception as e:
            return AgentResult(success=False, response=f"DeveloperAgent execution exception: {e}")


class LocalAgentRuntime(AgentRuntimeService):
    """Agent Runtime coordinating memory retrieval, context loading,

    and agent execution.
    """

    def __init__(
        self,
        event_bus: EventBusService,
        memory_service,
        context_service,
        tool_service,
        model_service,
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

        self.register_agent(
            MockAgent(self._memory_service, self._context_service, self._tool_service)
        )
        self.register_agent(
            DeveloperAgent(
                self._memory_service,
                self._context_service,
                self._tool_service,
                self._model_service,
            )
        )

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

            # Route developer intents to developer_agent
            if intent.intent_type == IntentType.DEVELOPER:
                agent = self._agents.get("developer_agent")
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

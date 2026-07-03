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
    ) -> None:
        self._event_bus = event_bus
        self._memory_service = memory_service
        self._context_service = context_service
        self._tool_service = tool_service
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

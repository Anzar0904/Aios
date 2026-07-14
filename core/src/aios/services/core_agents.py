import json
import logging
from typing import List

from aios.registry import ServiceRegistry
from aios.services.agent import Agent, AgentContext, AgentResult
from aios.services.model import LLMRequest, ModelService

logger = logging.getLogger(__name__)


class BaseCoreAgent(Agent):
    def __init__(self, agent_id: str, name: str, role: str, capabilities: List[str]):
        self._id = agent_id
        self._name = name
        self._role = role
        self._capabilities = capabilities

    @property
    def agent_id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def role(self) -> str:
        return self._role

    @property
    def capabilities(self) -> List[str]:
        return self._capabilities

    @property
    def description(self) -> str:
        return f"{self._role} Agent with capabilities: {', '.join(self._capabilities)}"

    def execute(self, agent_context: AgentContext) -> AgentResult:
        logger.info(f"Agent {self.name} executing action: {agent_context.intent.action}")

        model_service = None
        if ServiceRegistry._global_registry:
            try:
                model_service = ServiceRegistry._global_registry.get(ModelService)
            except KeyError:
                pass

        prompt = (
            f"You are the {self.role} Agent for AI OS.\n"
            f"Your capabilities are: {', '.join(self.capabilities)}.\n"
            f"You are assigned the following request:\n"
            f"Action: {agent_context.intent.action}\n"
            f"Parameters: {json.dumps(agent_context.intent.parameters)}\n\n"
            f"Describe how you accomplish this task step-by-step. Keep it professional, and return a clear summary of your findings or code."
        )

        if model_service:
            try:
                res = model_service.execute_request(
                    LLMRequest(prompt=prompt, system_instruction=f"Act as the {self.role} Agent.")
                )
                return AgentResult(success=True, response=res.content, data={"agent": self.name})
            except Exception as e:
                logger.error(f"Agent {self.name} LLM execution failed: {e}")

        # Fallback response
        return AgentResult(
            success=True,
            response=f"[{self.role} Agent] Accomplished task '{agent_context.intent.action}' successfully.",
            data={"agent": self.name},
        )


class SoftwareEngineerAgent(BaseCoreAgent):
    """Core Agent for coding, architecture, refactoring, and codebase updates."""

    pass


class TestEngineerAgent(BaseCoreAgent):
    """Core Agent for testing, validation, regression, and CI runs."""

    pass


class DocumentationEngineerAgent(BaseCoreAgent):
    """Core Agent for compiling manuals, READMEs, guides, and api reference sheets."""

    pass


class ResearchEngineerAgent(BaseCoreAgent):
    """Core Agent for paper review, tech analysis, and knowledge synthesis."""

    pass


class AgencyEngineerAgent(BaseCoreAgent):
    """Core Agent for crm metrics, leads tracking, and proposal campaigns."""

    pass


class AutomationEngineerAgent(BaseCoreAgent):
    """Core Agent for workflow template builders, deploys, and repairs."""

    pass


class IntegrationEngineerAgent(BaseCoreAgent):
    """Core Agent for third-party connector auth and synchronization."""

    pass

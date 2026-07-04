import logging
from pathlib import Path

from aios.kernel import Kernel
from aios.config import load_config

from aios.registry import ServiceRegistry
from aios.services.agent import AgentRuntimeService
from aios.services.agent_impl import CareerAgent, DeveloperAgent, LocalAgentRuntime, MockAgent
from aios.services.context import ContextService
from aios.services.context_impl import LocalContextService

# Interface imports
from aios.services.event_bus import EventBusService
from aios.services.github import GitHubService

# Concrete imports
from aios.services.event_bus_impl import LocalEventBus
from aios.services.github_impl import LocalGitHubService

from aios.services.intent import IntentResolverService
from aios.services.intent_impl import LocalIntentResolver
from aios.services.memory import MemoryService
from aios.services.memory_impl import LocalMemoryService
from aios.services.model import ModelService
from aios.services.model_impl import LocalModelService
from aios.services.session import SessionService
from aios.services.session_impl import LocalSessionService
from aios.services.tool import ToolService
from aios.services.tool_impl import LocalToolManager
from aios.services.project_intelligence import ProjectIntelligenceService
from aios.services.project_intelligence_impl import LocalProjectIntelligence
from aios.services.developer_workspace import DeveloperWorkspaceService
from aios.services.developer_workspace_impl import LocalDeveloperWorkspace
from aios.services.research import ResearchService
from aios.services.research_impl import LocalResearchService
from aios.services.n8n import N8NService
from aios.services.n8n_impl import LocalN8NService
from aios.services.personal import PersonalService
from aios.services.personal_impl import LocalPersonalService
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.knowledge_hub_impl import LocalKnowledgeHub

from aios.services.command import CommandRegistry
from aios.services.orchestrator import OrchestratorService
from aios.services.orchestrator_impl import LocalOrchestratorService
from aios.services.agent import AgentRegistry, LocalAgentManager
from aios.services.mission import MissionEngine
from aios.services.mission_impl import LocalMissionEngine
from aios.services.runtime import RuntimeService
from aios.services.runtime_impl import LocalRuntime
from aios.services.reasoning import ReasoningService
from aios.services.reasoning_impl import LocalReasoningService










logger = logging.getLogger(__name__)

def bootstrap_kernel(config_path: Path) -> Kernel:
    """
    Composition Root for Personal AI OS.
    Constructs, wires, and registers all concrete services.
    Returns a configured Kernel instance.
    """
    logger.info("Bootstrapping AI OS system (Composition Root)...")

    # 1. Initialize Registry
    registry = ServiceRegistry()
    config = load_config(Path(config_path))

    # 2. Construct services and wire dependencies

    event_bus = LocalEventBus()
    session_service = LocalSessionService(event_bus)
    context_service = LocalContextService(event_bus)
    memory_service = LocalMemoryService(event_bus)
    tool_service = LocalToolManager(event_bus)
    intent_resolver = LocalIntentResolver()
    model_service = LocalModelService(config_path=str(config_path))
    memory_service.set_model_service(model_service)

    project_intelligence = LocalProjectIntelligence()
    developer_workspace = LocalDeveloperWorkspace()
    research_service = LocalResearchService(model_service, registry=registry)

    research_service.initialize()
    n8n_service = LocalN8NService(model_service)
    n8n_service.initialize()
    personal_service = LocalPersonalService()
    personal_service.initialize()

    notion_cfg = getattr(config, "notion", None)
    knowledge_hub = LocalKnowledgeHub(
        config=notion_cfg,
        personal_service=personal_service
    )
    knowledge_hub.initialize()

    command_registry = CommandRegistry()

    command_registry.initialize()
    orchestrator_service = LocalOrchestratorService(command_registry)
    orchestrator_service.initialize()
    agent_registry = AgentRegistry()
    agent_manager = LocalAgentManager(agent_registry, orchestrator_service)
    agent_manager.initialize()

    github_cfg = getattr(config, "github", None)
    github_service = LocalGitHubService(
        model_service=model_service,
        project_intel=project_intelligence,
        dev_workspace=developer_workspace,
        token=github_cfg.token if github_cfg else None,
        base_url=github_cfg.base_url if github_cfg else "https://api.github.com",
        timeout=github_cfg.timeout if github_cfg else 30,
        max_retries=github_cfg.max_retries if github_cfg else 3,
        rate_limit_per_min=github_cfg.rate_limit_per_min if github_cfg else 60,
        cache_enabled=github_cfg.cache_enabled if github_cfg else True,
        offline_mode=github_cfg.offline_mode if github_cfg else False,
    )
    github_service.initialize()

    from aios.services.career import CareerOSService
    from aios.services.career_impl import LocalCareerOSService
    career_os = LocalCareerOSService(
        model_service=model_service,
        personal_service=personal_service,
        github_service=github_service,
        project_intel=project_intelligence,
        n8n_service=n8n_service,
        registry=registry
    )

    career_os.initialize()
    registry.register(CareerOSService, career_os)


    from aios.services.daily import DailyOSService
    from aios.services.daily_impl import LocalDailyOSService
    daily_os = LocalDailyOSService(
        model_service=model_service,
        personal_service=personal_service,
        github_service=github_service,
        project_intel=project_intelligence,
        career_os=career_os,
        registry=registry,
    )

    daily_os.initialize()
    registry.register(DailyOSService, daily_os)

    # Instantiate agents
    career_agent = CareerAgent(
        memory_service, context_service, tool_service, model_service, github_service, career_os, daily_os
    )


    developer_agent = DeveloperAgent(memory_service, context_service, tool_service, model_service)
    mock_agent = MockAgent(memory_service, context_service, tool_service)


    # Register to AgentRegistry
    agent_registry.register(career_agent)
    agent_registry.register(developer_agent)
    agent_registry.register(mock_agent)

    agent_runtime = LocalAgentRuntime(
        event_bus=event_bus,
        memory_service=memory_service,
        context_service=context_service,
        tool_service=tool_service,
        model_service=model_service
    )

    mission_engine = LocalMissionEngine(agent_runtime, registry=registry)

    mission_engine.initialize()
    runtime_service = LocalRuntime()
    runtime_service.initialize()
    reasoning_service = LocalReasoningService()
    reasoning_service.initialize()



    # 3. Register agents to the Agent Runtime
    agent_runtime.register_agent(mock_agent)
    agent_runtime.register_agent(developer_agent)
    agent_runtime.register_agent(career_agent)

    # 4. Register services on registry
    registry.register(EventBusService, event_bus)
    registry.register(SessionService, session_service)
    registry.register(ContextService, context_service)
    registry.register(MemoryService, memory_service)
    registry.register(IntentResolverService, intent_resolver)
    registry.register(ModelService, model_service)
    registry.register(ToolService, tool_service)
    registry.register(AgentRuntimeService, agent_runtime)
    registry.register(GitHubService, github_service)
    registry.register(ProjectIntelligenceService, project_intelligence)

    registry.register(DeveloperWorkspaceService, developer_workspace)
    registry.register(ResearchService, research_service)
    registry.register(N8NService, n8n_service)
    registry.register(PersonalService, personal_service)
    registry.register(KnowledgeHubService, knowledge_hub)

    registry.register(CommandRegistry, command_registry)
    registry.register(OrchestratorService, orchestrator_service)
    registry.register(AgentRegistry, agent_registry)
    registry.register(LocalAgentManager, agent_manager)
    registry.register(MissionEngine, mission_engine)
    registry.register(RuntimeService, runtime_service)
    registry.register(ReasoningService, reasoning_service)

    # 5. Instantiate Kernel with the registry
    kernel = Kernel(config_path=config_path, registry=registry)
    runtime_service._kernel = kernel
    return kernel

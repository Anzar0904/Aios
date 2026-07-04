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

    from aios.services.intent_engine import IntentEngine
    from aios.services.intent_engine_impl import LocalIntentEngine

    intent_engine = LocalIntentEngine(
        memory_service=memory_service,
        reasoning_service=reasoning_service,
        model_service=model_service
    )
    intent_engine.initialize()
    registry.register(IntentEngine, intent_engine)

    from aios.services.workspace_intelligence import WorkspaceIntelligenceService, CodeIntelligenceService
    from aios.services.workspace_intelligence_impl import LocalWorkspaceIntelligenceService, LocalCodeIntelligenceService

    workspace_intel = LocalWorkspaceIntelligenceService(
        project_intel=project_intelligence,
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    workspace_intel.initialize()
    registry.register(WorkspaceIntelligenceService, workspace_intel)

    code_intel = LocalCodeIntelligenceService(
        project_intel=project_intelligence,
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    code_intel.initialize()
    registry.register(CodeIntelligenceService, code_intel)

    from aios.services.engineering_intelligence import EngineeringIntelligenceService
    from aios.services.engineering_intelligence_impl import LocalEngineeringIntelligenceService

    eng_intel = LocalEngineeringIntelligenceService(
        code_intel=code_intel,
        workspace_intel=workspace_intel,
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    eng_intel.initialize()
    registry.register(EngineeringIntelligenceService, eng_intel)

    from aios.services.software_engineer import SoftwareEngineerService
    from aios.services.software_engineer_impl import LocalSoftwareEngineerService

    swe_service = LocalSoftwareEngineerService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    swe_service.initialize()
    registry.register(SoftwareEngineerService, swe_service)

    from aios.services.execution_engine import ExecutionEngine
    from aios.services.execution_engine_impl import LocalExecutionEngine

    exec_engine = LocalExecutionEngine(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    exec_engine.initialize()
    registry.register(ExecutionEngine, exec_engine)

    from aios.services.ai_workspace import AIWorkspaceService
    from aios.services.ai_workspace_impl import LocalAIWorkspaceService

    workspace_service = LocalAIWorkspaceService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        registry=registry
    )
    workspace_service.initialize()
    registry.register(AIWorkspaceService, workspace_service)

    from aios.services.file_planner import FilePlanner
    from aios.services.file_planner_impl import LocalFilePlanner

    file_planner_service = LocalFilePlanner(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    file_planner_service.initialize()
    registry.register(FilePlanner, file_planner_service)

    from aios.services.patch_generation import PatchGenerationService
    from aios.services.patch_generation_impl import LocalPatchGenerationService

    patch_service = LocalPatchGenerationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        registry=registry
    )
    patch_service.initialize()
    registry.register(PatchGenerationService, patch_service)

    from aios.services.code_generation import CodeGenerationService
    from aios.services.code_generation_impl import LocalCodeGenerationService

    codegen_service = LocalCodeGenerationService(
        memory_service=memory_service,
        model_service=model_service,
        knowledge_hub=knowledge_hub,
        registry=registry
    )
    codegen_service.initialize()
    registry.register(CodeGenerationService, codegen_service)

    from aios.services.test_engineer import AITestEngineerService
    from aios.services.test_engineer_impl import LocalAITestEngineerService

    test_eng_service = LocalAITestEngineerService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    test_eng_service.initialize()
    registry.register(AITestEngineerService, test_eng_service)

    from aios.services.test_impact import ChangeImpactAnalyzer
    from aios.services.test_impact_impl import LocalChangeImpactAnalyzer

    impact_analyzer = LocalChangeImpactAnalyzer(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    impact_analyzer.initialize()
    registry.register(ChangeImpactAnalyzer, impact_analyzer)

    from aios.services.test_generation import TestGenerationService
    from aios.services.test_generation_impl import LocalTestGenerationService

    test_gen_service = LocalTestGenerationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    test_gen_service.initialize()
    registry.register(TestGenerationService, test_gen_service)

    from aios.services.test_execution import TestExecutionService
    from aios.services.test_execution_impl import LocalTestExecutionService

    test_exec_service = LocalTestExecutionService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    test_exec_service.initialize()
    registry.register(TestExecutionService, test_exec_service)

    from aios.services.test_coverage import AITestCoverageService
    from aios.services.test_coverage_impl import LocalAITestCoverageService

    test_cov_service = LocalAITestCoverageService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    test_cov_service.initialize()
    registry.register(AITestCoverageService, test_cov_service)

    from aios.services.test_failure import FailureAnalysisService
    from aios.services.test_failure_impl import LocalFailureAnalysisService

    test_fail_service = LocalFailureAnalysisService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    test_fail_service.initialize()
    registry.register(FailureAnalysisService, test_fail_service)

    from aios.services.test_validation import ValidationService
    from aios.services.test_validation_impl import LocalValidationService

    validation_service = LocalValidationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    validation_service.initialize()
    registry.register(ValidationService, validation_service)

    from aios.services.engineering_profile import EngineeringProfileService
    from aios.services.engineering_profile_impl import LocalEngineeringProfileService

    profile_service = LocalEngineeringProfileService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    profile_service.initialize()
    registry.register(EngineeringProfileService, profile_service)

    from aios.services.documentation_intelligence import DocumentationService
    from aios.services.documentation_intelligence_impl import LocalDocumentationService

    doc_service = LocalDocumentationService(
        memory_service=memory_service,
        engineering_profile_service=profile_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    doc_service.initialize()
    registry.register(DocumentationService, doc_service)

    from aios.services.readme_intelligence import READMEIntelligenceService
    from aios.services.readme_intelligence_impl import LocalREADMEIntelligenceService

    readme_service = LocalREADMEIntelligenceService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    readme_service.initialize()
    registry.register(READMEIntelligenceService, readme_service)

    from aios.services.api_documentation import APIDocumentationService
    from aios.services.api_documentation_impl import LocalAPIDocumentationService

    api_doc_service = LocalAPIDocumentationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    api_doc_service.initialize()
    registry.register(APIDocumentationService, api_doc_service)

    from aios.services.architecture_documentation import ArchitectureDocumentationService
    from aios.services.architecture_documentation_impl import LocalArchitectureDocumentationService

    arch_doc_service = LocalArchitectureDocumentationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    arch_doc_service.initialize()
    registry.register(ArchitectureDocumentationService, arch_doc_service)

    from aios.services.engineering_documentation import EngineeringDocumentationService
    from aios.services.engineering_documentation_impl import LocalEngineeringDocumentationService

    eng_doc_service = LocalEngineeringDocumentationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    eng_doc_service.initialize()
    registry.register(EngineeringDocumentationService, eng_doc_service)

    from aios.services.release_documentation import ReleaseDocumentationService
    from aios.services.release_documentation_impl import LocalReleaseDocumentationService

    release_doc_service = LocalReleaseDocumentationService(
        memory_service=memory_service,
        profile_service=profile_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    release_doc_service.initialize()
    registry.register(ReleaseDocumentationService, release_doc_service)

    from aios.services.approval import ApprovalEngineService
    from aios.services.approval_impl import LocalApprovalEngineService

    approval_service = LocalApprovalEngineService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    approval_service.initialize()
    registry.register(ApprovalEngineService, approval_service)

    from aios.services.review import ReviewEngine
    from aios.services.review_impl import LocalReviewEngine

    review_service = LocalReviewEngine(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    review_service.initialize()
    registry.register(ReviewEngine, review_service)

    from aios.services.collaboration import ReviewCollaborationService
    from aios.services.collaboration_impl import LocalReviewCollaborationService

    collab_service = LocalReviewCollaborationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    collab_service.initialize()
    registry.register(ReviewCollaborationService, collab_service)

    from aios.services.approval_history import ApprovalHistoryService
    from aios.services.approval_history_impl import LocalApprovalHistoryService

    history_service = LocalApprovalHistoryService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    history_service.initialize()
    registry.register(ApprovalHistoryService, history_service)

    from aios.services.automation import AutomationService
    from aios.services.automation_impl import LocalAutomationService

    automation_service = LocalAutomationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    automation_service.initialize()
    registry.register(AutomationService, automation_service)

    from aios.services.workflow_planning import WorkflowPlanner
    from aios.services.workflow_planning_impl import LocalWorkflowPlanner

    workflow_planner = LocalWorkflowPlanner(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    workflow_planner.initialize()
    registry.register(WorkflowPlanner, workflow_planner)

    from aios.services.n8n_translation import WorkflowTranslator
    from aios.services.n8n_translation_impl import LocalWorkflowTranslator

    workflow_translator = LocalWorkflowTranslator(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry
    )
    workflow_translator.initialize()
    registry.register(WorkflowTranslator, workflow_translator)

    # 5. Instantiate Kernel with the registry
    kernel = Kernel(config_path=config_path, registry=registry)
    runtime_service._kernel = kernel
    return kernel

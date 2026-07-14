"""
bootstrap_modules/services.py

Constructs, initializes, and registers AIOS services, source control, testing platforms,
and document intelligence.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

# Self-hosted production n8n imports
from aios.n8n import (
    N8NAuthenticationManager,
    N8NCapabilityManager,
    N8NClient,
    N8NConfigurationService,
    N8NConnectionManager,
    N8NCredentialManager,
    N8NDiagnostics,
    N8NEventMonitor,
    N8NExecutionManager,
    N8NHealthMonitor,
    N8NReportGenerator,
    N8NSessionManager,
    N8NTelemetryCollector,
    N8NValidator,
    N8NVersionManager,
    N8NWorkflowManager,
    N8NWorkspaceManager,
)
from aios.services.api_documentation import APIDocumentationService
from aios.services.api_documentation_impl import LocalAPIDocumentationService

# Approval, Review and Collaboration
from aios.services.approval import ApprovalEngineService
from aios.services.approval_history import ApprovalHistoryService
from aios.services.approval_history_impl import LocalApprovalHistoryService
from aios.services.approval_impl import LocalApprovalEngineService
from aios.services.architecture_documentation import ArchitectureDocumentationService
from aios.services.architecture_documentation_impl import LocalArchitectureDocumentationService

# Automation services
from aios.services.automation import AutomationService
from aios.services.automation_impl import LocalAutomationService
from aios.services.business import BusinessIntelligenceService
from aios.services.business_impl import LocalBusinessIntelligenceService

# Career and Daily OS imports
from aios.services.career import CareerOSService
from aios.services.career_impl import LocalCareerOSService
from aios.services.code_generation import CodeGenerationService
from aios.services.code_generation_impl import LocalCodeGenerationService
from aios.services.collaboration import ReviewCollaborationService
from aios.services.collaboration_impl import LocalReviewCollaborationService
from aios.services.context import ContextService
from aios.services.context_impl import LocalContextService
from aios.services.daily import DailyOSService
from aios.services.daily_impl import LocalDailyOSService
from aios.services.documentation_intelligence import DocumentationService
from aios.services.documentation_intelligence_impl import LocalDocumentationService
from aios.services.engineering_documentation import EngineeringDocumentationService
from aios.services.engineering_documentation_impl import LocalEngineeringDocumentationService

# Profile and documentation services
from aios.services.engineering_profile import EngineeringProfileService
from aios.services.engineering_profile_impl import LocalEngineeringProfileService
from aios.services.execution_engine import ExecutionEngine
from aios.services.execution_engine_impl import LocalExecutionEngine
from aios.services.file_planner import FilePlanner
from aios.services.file_planner_impl import LocalFilePlanner
from aios.services.github import GitHubService
from aios.services.github_impl import LocalGitHubService
from aios.services.intent import IntentResolverService

# Advanced engineering and testing services
from aios.services.intent_engine import IntentEngine
from aios.services.intent_engine_impl import LocalIntentEngine
from aios.services.intent_impl import LocalIntentResolver
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.knowledge_hub_impl import LocalKnowledgeHub
from aios.services.model import ModelService
from aios.services.model_impl import LocalModelService
from aios.services.n8n import N8NService
from aios.services.n8n_impl import LocalN8NService
from aios.services.n8n_integration import N8NIntegrationService
from aios.services.n8n_integration_impl import LocalN8NIntegrationService
from aios.services.n8n_translation import WorkflowTranslator
from aios.services.n8n_translation_impl import LocalWorkflowTranslator
from aios.services.notion import NotionService
from aios.services.notion_impl import LocalNotionService
from aios.services.orchestrator import OrchestratorService
from aios.services.orchestrator_impl import LocalOrchestratorService
from aios.services.patch_generation import PatchGenerationService
from aios.services.patch_generation_impl import LocalPatchGenerationService
from aios.services.personal import PersonalService
from aios.services.personal_impl import LocalPersonalService
from aios.services.project_intelligence import ProjectIntelligenceService
from aios.services.project_intelligence_impl import LocalProjectIntelligence
from aios.services.readme_intelligence import READMEIntelligenceService
from aios.services.readme_intelligence_impl import LocalREADMEIntelligenceService
from aios.services.reasoning import ReasoningService
from aios.services.reasoning_impl import LocalReasoningService
from aios.services.release_documentation import ReleaseDocumentationService
from aios.services.release_documentation_impl import LocalReleaseDocumentationService
from aios.services.research import ResearchService
from aios.services.research_impl import LocalResearchService
from aios.services.review import ReviewEngine
from aios.services.review_impl import LocalReviewEngine
from aios.services.runtime import RuntimeService
from aios.services.runtime_impl import LocalRuntime

# Core interface and implementation imports
from aios.services.session import SessionService
from aios.services.session_impl import LocalSessionService
from aios.services.software_engineer import SoftwareEngineerService
from aios.services.software_engineer_impl import LocalSoftwareEngineerService
from aios.services.supabase import SupabaseService
from aios.services.supabase_impl import LocalSupabaseIntelligenceService
from aios.services.test_coverage import AITestCoverageService
from aios.services.test_coverage_impl import LocalAITestCoverageService
from aios.services.test_engineer import AITestEngineerService
from aios.services.test_engineer_impl import LocalAITestEngineerService
from aios.services.test_execution import TestExecutionService
from aios.services.test_execution_impl import LocalTestExecutionService
from aios.services.test_failure import FailureAnalysisService
from aios.services.test_failure_impl import LocalFailureAnalysisService
from aios.services.test_generation import TestGenerationService
from aios.services.test_generation_impl import LocalTestGenerationService
from aios.services.test_impact import ChangeImpactAnalyzer
from aios.services.test_impact_impl import LocalChangeImpactAnalyzer
from aios.services.test_validation import ValidationService
from aios.services.test_validation_impl import LocalValidationService
from aios.services.tool import ToolService
from aios.services.tool_impl import LocalToolManager
from aios.services.vercel import VercelService
from aios.services.vercel_impl import LocalVercelIntelligenceService

# Workflow monitoring and optimization
from aios.services.workflow_monitoring import WorkflowMonitoringService
from aios.services.workflow_monitoring_impl import LocalWorkflowMonitoringService
from aios.services.workflow_optimization import WorkflowOptimizationService
from aios.services.workflow_optimization_impl import LocalWorkflowOptimizationService
from aios.services.workflow_planning import WorkflowPlanner
from aios.services.workflow_planning_impl import LocalWorkflowPlanner
from aios.services.workflow_versioning import WorkflowVersionService
from aios.services.workflow_versioning_impl import LocalWorkflowVersionService

# Source Control Platform imports
from aios.source_control import (
    BranchManager,
    CommitManager,
    DiffManager,
    IssueManager,
    LocalGitExecutor,
    MergeManager,
    ProviderConfigurationService,
    ProviderDiagnostics,
    ProviderDiscovery,
    ProviderHealthMonitor,
    ProviderValidator,
    PullRequestManager,
    ReleaseManager,
    RepositoryManager,
    SourceControlRegistry,
    SourceControlReportGenerator,
    SourceControlService,
    SourceControlStatistics,
    SourceControlTelemetry,
    TagManager,
    WebhookManager,
    WorkflowManager,
    WorkspaceRepositoryManager,
)

logger = logging.getLogger(__name__)


def bootstrap_services(
    registry,  # noqa: ANN001
    config_path: Path,
    config,  # noqa: ANN001
    event_bus,  # noqa: ANN001
    infra_ctx: dict,
    workspace_repo_ctx: dict,
    memory_ctx: dict,
    command_registry,  # noqa: ANN001
) -> dict:
    """Wires, initializes, and registers core local and domain services."""
    profile_repo = workspace_repo_ctx["profile_repo"]
    memory_service = memory_ctx["memory_service"]

    # ── 1. CORE AIOS SERVICES ──
    session_service = LocalSessionService(event_bus)
    context_service = LocalContextService(event_bus)
    tool_service = LocalToolManager(event_bus)
    intent_resolver = LocalIntentResolver()
    orchestrator_service = LocalOrchestratorService(command_registry)
    orchestrator_service.initialize()

    model_service = LocalModelService(config_path=str(config_path), registry=registry)
    memory_service.set_model_service(model_service)

    from aios.local.service import LocalModelService as Phase1LocalModelService

    phase1_local_model_service = Phase1LocalModelService(ollama_base_url="http://localhost:11434")

    # Register NVIDIA provider foundation
    from aios.providers.nvidia import register_nvidia_provider

    register_nvidia_provider()

    project_intelligence = LocalProjectIntelligence()
    research_service = LocalResearchService(model_service, registry=registry)
    research_service.initialize()

    n8n_service = LocalN8NService(model_service)
    n8n_service.initialize()

    personal_service = LocalPersonalService()
    personal_service.initialize()

    notion_cfg = getattr(config, "notion", None)
    knowledge_hub = LocalKnowledgeHub(config=notion_cfg, personal_service=personal_service)
    knowledge_hub.initialize()

    # ── 2. GITHUB & SOURCE CONTROL SERVICE ──
    github_cfg = getattr(config, "github", None)
    github_service = LocalGitHubService(
        model_service=model_service,
        project_intel=project_intelligence,
        dev_workspace=None,  # will link after developer_workspace is created in orchestrator
        token=github_cfg.token if github_cfg else None,
        base_url=github_cfg.base_url if github_cfg else "https://api.github.com",
        timeout=github_cfg.timeout if github_cfg else 30,
        max_retries=github_cfg.max_retries if github_cfg else 3,
        rate_limit_per_min=github_cfg.rate_limit_per_min if github_cfg else 60,
        cache_enabled=github_cfg.cache_enabled if github_cfg else True,
        offline_mode=github_cfg.offline_mode if github_cfg else False,
    )
    github_service.initialize()
    github_service._registry = registry

    sc_registry = SourceControlRegistry()
    sc_discovery = ProviderDiscovery(sc_registry)
    sc_discovery.discover_and_register()

    sc_config = ProviderConfigurationService()
    sc_health = ProviderHealthMonitor(sc_registry)
    sc_diagnostics = ProviderDiagnostics()
    sc_validator = ProviderValidator()

    source_control_service = SourceControlService(
        registry=sc_registry,
        config_service=sc_config,
        health_monitor=sc_health,
        diagnostics=sc_diagnostics,
        validator=sc_validator,
    )

    local_git = LocalGitExecutor()
    repo_mgr = RepositoryManager(source_control_service)
    branch_mgr = BranchManager(local_git)
    commit_mgr = CommitManager(local_git)
    tag_mgr = TagManager(local_git)
    merge_mgr = MergeManager(local_git)
    diff_mgr = DiffManager(local_git)
    workspace_repo_mgr = WorkspaceRepositoryManager(local_git)
    pr_mgr = PullRequestManager(source_control_service)
    issue_mgr = IssueManager(source_control_service)
    release_mgr = ReleaseManager(source_control_service)
    workflow_mgr = WorkflowManager(source_control_service)
    webhook_mgr = WebhookManager(source_control_service)

    sc_telemetry = SourceControlTelemetry()
    sc_statistics = SourceControlStatistics()
    sc_report = SourceControlReportGenerator(
        workspace_root=os.getcwd(),
        diagnostics=sc_diagnostics,
        health_monitor=sc_health,
        statistics=sc_statistics,
    )

    sc_registry.initialize()
    sc_discovery.initialize()
    sc_config.initialize()
    sc_health.initialize()
    sc_diagnostics.initialize()
    sc_validator.initialize()
    source_control_service.initialize()
    local_git.initialize()
    repo_mgr.initialize()
    branch_mgr.initialize()
    commit_mgr.initialize()
    tag_mgr.initialize()
    merge_mgr.initialize()
    diff_mgr.initialize()
    workspace_repo_mgr.initialize()
    pr_mgr.initialize()
    issue_mgr.initialize()
    release_mgr.initialize()
    workflow_mgr.initialize()
    webhook_mgr.initialize()
    sc_telemetry.initialize()
    sc_statistics.initialize()
    sc_report.initialize()

    # ── 3. CAREER OS & DAILY OS ──
    career_os = LocalCareerOSService(
        model_service=model_service,
        personal_service=personal_service,
        github_service=github_service,
        project_intel=project_intelligence,
        n8n_service=n8n_service,
        registry=registry,
    )
    career_os.initialize()

    daily_os = LocalDailyOSService(
        model_service=model_service,
        personal_service=personal_service,
        github_service=github_service,
        project_intel=project_intelligence,
        career_os=career_os,
        registry=registry,
    )
    daily_os.initialize()

    # ── 4. BASE RUNTIME & REASONING SERVICES ──
    runtime_service = LocalRuntime()
    runtime_service.initialize()

    reasoning_service = LocalReasoningService()
    reasoning_service.initialize()

    # ── 5. ADVANCED DOMAIN SERVICES ──
    intent_engine = LocalIntentEngine(
        memory_service=memory_service,
        reasoning_service=reasoning_service,
        model_service=model_service,
    )
    intent_engine.initialize()

    swe_service = LocalSoftwareEngineerService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    swe_service.initialize()

    exec_engine = LocalExecutionEngine(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    exec_engine.initialize()

    file_planner_service = LocalFilePlanner(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    file_planner_service.initialize()

    patch_service = LocalPatchGenerationService(
        memory_service=memory_service, knowledge_hub=knowledge_hub, registry=registry
    )
    patch_service.initialize()

    codegen_service = LocalCodeGenerationService(
        memory_service=memory_service,
        model_service=model_service,
        knowledge_hub=knowledge_hub,
        registry=registry,
    )
    codegen_service.initialize()

    test_eng_service = LocalAITestEngineerService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    test_eng_service.initialize()

    impact_analyzer = LocalChangeImpactAnalyzer(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    impact_analyzer.initialize()

    test_gen_service = LocalTestGenerationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    test_gen_service.initialize()

    test_exec_service = LocalTestExecutionService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    test_exec_service.initialize()

    test_cov_service = LocalAITestCoverageService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    test_cov_service.initialize()

    test_fail_service = LocalFailureAnalysisService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    test_fail_service.initialize()

    validation_service = LocalValidationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    validation_service.initialize()

    profile_service = LocalEngineeringProfileService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
        profile_repo=profile_repo,
    )
    profile_service.initialize()

    doc_service = LocalDocumentationService(
        memory_service=memory_service,
        engineering_profile_service=profile_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    doc_service.initialize()

    from aios.services.docintel.agent import DocumentationAgent

    doc_agent = DocumentationAgent(model_service=model_service, index_path="docs/index.json")
    doc_agent.initialize()

    from aios.services.engineer.bible import EngineeringBibleService

    bible_service = EngineeringBibleService(
        model_service=model_service, index_path="docs/index.json"
    )
    bible_service.initialize()

    readme_service = LocalREADMEIntelligenceService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    readme_service.initialize()

    api_doc_service = LocalAPIDocumentationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    api_doc_service.initialize()

    arch_doc_service = LocalArchitectureDocumentationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    arch_doc_service.initialize()

    eng_doc_service = LocalEngineeringDocumentationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    eng_doc_service.initialize()

    release_doc_service = LocalReleaseDocumentationService(
        memory_service=memory_service,
        profile_service=profile_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    release_doc_service.initialize()

    approval_service = LocalApprovalEngineService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    approval_service.initialize()

    review_service = LocalReviewEngine(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    review_service.initialize()

    collab_service = LocalReviewCollaborationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    collab_service.initialize()

    history_service = LocalApprovalHistoryService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    history_service.initialize()

    automation_service = LocalAutomationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    automation_service.initialize()

    workflow_planner = LocalWorkflowPlanner(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    workflow_planner.initialize()

    workflow_translator = LocalWorkflowTranslator(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    workflow_translator.initialize()

    n8n_integration_service = LocalN8NIntegrationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    n8n_integration_service.initialize()

    # ── 6. SELF-HOSTED PRODUCTION N8N PLATFORM ──
    n8n_config = N8NConfigurationService()
    n8n_session = N8NSessionManager(n8n_config)
    n8n_auth = N8NAuthenticationManager(n8n_config, n8n_session)
    n8n_conn = N8NConnectionManager(n8n_config, n8n_auth)
    n8n_client = N8NClient(n8n_conn, n8n_session)
    n8n_workflow = N8NWorkflowManager(n8n_client)
    n8n_execution = N8NExecutionManager(n8n_client)
    n8n_credential = N8NCredentialManager(n8n_client)
    n8n_workspace = N8NWorkspaceManager()
    n8n_version = N8NVersionManager(n8n_client)
    n8n_capability = N8NCapabilityManager(n8n_client)
    n8n_health = N8NHealthMonitor(
        n8n_client, n8n_auth, n8n_workflow, n8n_execution, n8n_version, n8n_capability
    )
    n8n_telemetry = N8NTelemetryCollector(n8n_health)
    n8n_event = N8NEventMonitor()
    n8n_validator = N8NValidator()
    n8n_diagnostics = N8NDiagnostics(n8n_config, n8n_auth, n8n_session)
    n8n_report = N8NReportGenerator(os.getcwd(), n8n_health, n8n_diagnostics)

    n8n_config.initialize()
    n8n_session.initialize()
    n8n_auth.initialize()
    n8n_conn.initialize()
    n8n_client.initialize()
    n8n_workflow.initialize()
    n8n_execution.initialize()
    n8n_credential.initialize()
    n8n_workspace.initialize()
    n8n_health.initialize()
    n8n_version.initialize()
    n8n_capability.initialize()
    n8n_telemetry.initialize()
    n8n_event.initialize()
    n8n_validator.initialize()
    n8n_diagnostics.initialize()
    n8n_report.initialize()

    # Wire to n8n integration health monitor
    n8n_integration_service._health_monitor._prod_health = n8n_health

    # ── 7. WORKFLOW MONITORING, OPTIMIZATION & VERSIONING ──
    workflow_monitoring_service = LocalWorkflowMonitoringService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    workflow_monitoring_service.initialize()

    workflow_optimization_service = LocalWorkflowOptimizationService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    workflow_optimization_service.initialize()

    workflow_version_service = LocalWorkflowVersionService(
        memory_service=memory_service,
        knowledge_hub=knowledge_hub,
        model_service=model_service,
        registry=registry,
    )
    workflow_version_service.initialize()

    # ── 8. DI REGISTRATIONS ──
    registry.register(SessionService, session_service)
    registry.register(ContextService, context_service)
    registry.register(IntentResolverService, intent_resolver)
    registry.register(ModelService, model_service)
    registry.register(Phase1LocalModelService, phase1_local_model_service)
    registry.register(ToolService, tool_service)
    registry.register(GitHubService, github_service)

    notion_service = LocalNotionService(
        model_service=model_service,
        memory_service=memory_service,
    )
    notion_service.initialize()
    registry.register(NotionService, notion_service)

    supabase_service = LocalSupabaseIntelligenceService()
    supabase_service.initialize()
    registry.register(SupabaseService, supabase_service)

    vercel_service = LocalVercelIntelligenceService()
    vercel_service.initialize()
    registry.register(VercelService, vercel_service)

    business_service = LocalBusinessIntelligenceService()
    business_service.initialize()
    registry.register(BusinessIntelligenceService, business_service)

    registry.register(SourceControlRegistry, sc_registry)
    registry.register(ProviderDiscovery, sc_discovery)
    registry.register(ProviderConfigurationService, sc_config)
    registry.register(ProviderHealthMonitor, sc_health)
    registry.register(ProviderDiagnostics, sc_diagnostics)
    registry.register(ProviderValidator, sc_validator)
    registry.register(SourceControlService, source_control_service)
    registry.register(LocalGitExecutor, local_git)
    registry.register(RepositoryManager, repo_mgr)
    registry.register(BranchManager, branch_mgr)
    registry.register(CommitManager, commit_mgr)
    registry.register(TagManager, tag_mgr)
    registry.register(MergeManager, merge_mgr)
    registry.register(DiffManager, diff_mgr)
    registry.register(WorkspaceRepositoryManager, workspace_repo_mgr)
    registry.register(PullRequestManager, pr_mgr)
    registry.register(IssueManager, issue_mgr)
    registry.register(ReleaseManager, release_mgr)
    registry.register(WorkflowManager, workflow_mgr)
    registry.register(WebhookManager, webhook_mgr)
    registry.register(SourceControlTelemetry, sc_telemetry)
    registry.register(SourceControlStatistics, sc_statistics)
    registry.register(SourceControlReportGenerator, sc_report)

    registry.register(ProjectIntelligenceService, project_intelligence)
    registry.register(ResearchService, research_service)
    registry.register(N8NService, n8n_service)
    registry.register(PersonalService, personal_service)
    registry.register(KnowledgeHubService, knowledge_hub)
    registry.register(OrchestratorService, orchestrator_service)

    registry.register(CareerOSService, career_os)
    registry.register(DailyOSService, daily_os)

    registry.register(RuntimeService, runtime_service)
    registry.register(ReasoningService, reasoning_service)

    registry.register(IntentEngine, intent_engine)
    registry.register(SoftwareEngineerService, swe_service)
    registry.register(ExecutionEngine, exec_engine)
    registry.register(FilePlanner, file_planner_service)
    registry.register(PatchGenerationService, patch_service)
    registry.register(CodeGenerationService, codegen_service)
    registry.register(AITestEngineerService, test_eng_service)
    registry.register(ChangeImpactAnalyzer, impact_analyzer)
    registry.register(TestGenerationService, test_gen_service)
    registry.register(TestExecutionService, test_exec_service)
    registry.register(AITestCoverageService, test_cov_service)
    registry.register(FailureAnalysisService, test_fail_service)
    registry.register(ValidationService, validation_service)
    registry.register(EngineeringProfileService, profile_service)
    registry.register(DocumentationService, doc_service)
    registry.register(DocumentationAgent, doc_agent)
    registry.register(EngineeringBibleService, bible_service)
    registry.register(READMEIntelligenceService, readme_service)
    registry.register(APIDocumentationService, api_doc_service)
    registry.register(ArchitectureDocumentationService, arch_doc_service)
    registry.register(EngineeringDocumentationService, eng_doc_service)
    registry.register(ReleaseDocumentationService, release_doc_service)
    registry.register(ApprovalEngineService, approval_service)
    registry.register(ReviewEngine, review_service)
    registry.register(ReviewCollaborationService, collab_service)
    registry.register(ApprovalHistoryService, history_service)
    registry.register(AutomationService, automation_service)
    registry.register(WorkflowPlanner, workflow_planner)
    registry.register(WorkflowTranslator, workflow_translator)
    registry.register(N8NIntegrationService, n8n_integration_service)

    registry.register(N8NConfigurationService, n8n_config)
    registry.register(N8NSessionManager, n8n_session)
    registry.register(N8NAuthenticationManager, n8n_auth)
    registry.register(N8NConnectionManager, n8n_conn)
    registry.register(N8NClient, n8n_client)
    registry.register(N8NWorkflowManager, n8n_workflow)
    registry.register(N8NExecutionManager, n8n_execution)
    registry.register(N8NCredentialManager, n8n_credential)
    registry.register(N8NWorkspaceManager, n8n_workspace)
    registry.register(N8NHealthMonitor, n8n_health)
    registry.register(N8NVersionManager, n8n_version)
    registry.register(N8NCapabilityManager, n8n_capability)
    registry.register(N8NTelemetryCollector, n8n_telemetry)
    registry.register(N8NEventMonitor, n8n_event)
    registry.register(N8NValidator, n8n_validator)
    registry.register(N8NDiagnostics, n8n_diagnostics)
    registry.register(N8NReportGenerator, n8n_report)

    registry.register(WorkflowMonitoringService, workflow_monitoring_service)
    registry.register(WorkflowOptimizationService, workflow_optimization_service)
    registry.register(WorkflowVersionService, workflow_version_service)

    return {
        "session_service": session_service,
        "context_service": context_service,
        "tool_service": tool_service,
        "intent_resolver": intent_resolver,
        "model_service": model_service,
        "project_intelligence": project_intelligence,
        "research_service": research_service,
        "n8n_service": n8n_service,
        "personal_service": personal_service,
        "knowledge_hub": knowledge_hub,
        "github_service": github_service,
        "career_os": career_os,
        "daily_os": daily_os,
        "runtime_service": runtime_service,
        "reasoning_service": reasoning_service,
        "swe_service": swe_service,
        "n8n_integration_service": n8n_integration_service,
        "orchestrator_service": orchestrator_service,
    }

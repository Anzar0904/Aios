import os
import json
import time
import logging
from typing import Dict, List, Any, Optional

from aios.services.memory import MemoryService, MemoryType, MemoryMetadata
from aios.services.knowledge_hub import (
    KnowledgeHubService,
    KnowledgeDocument,
    KnowledgeMetadata as KHMetadata,
)
from aios.services.engineering_profile import (
    ProjectProfile,
    CodingProfile,
    TestingProfile,
    ExecutionProfile,
    DocumentationProfile,
    GitHubProfile,
    ReleaseProfile,
    AutomationProfile,
    WorkspaceProfile,
    EngineeringProfile,
    ProfileSerializer,
    ProfileLoader,
    ProfileManager,
    ProfileRegistry,
    EngineeringProfileService,
)

logger = logging.getLogger(__name__)


class LocalProfileSerializer(ProfileSerializer):
    """Concrete profile serializer mapping dict structures to dataclasses."""

    def serialize(self, profile: EngineeringProfile) -> Dict[str, Any]:
        return {
            "profile_id": profile.profile_id,
            "project": {
                "project_name": profile.project.project_name,
                "version": profile.project.version,
                "description": profile.project.description
            },
            "coding": {
                "language": profile.coding.language,
                "coding_standards": profile.coding.coding_standards,
                "naming_conventions": profile.coding.naming_conventions
            },
            "testing": {
                "framework": profile.testing.framework,
                "min_statement_coverage": profile.testing.min_statement_coverage,
                "min_branch_coverage": profile.testing.min_branch_coverage
            },
            "execution": {
                "max_timeout_seconds": profile.execution.max_timeout_seconds,
                "sandbox_enabled": profile.execution.sandbox_enabled
            },
            "documentation": {
                "format": profile.documentation.format,
                "generate_api_docs": profile.documentation.generate_api_docs
            },
            "github": {
                "org_name": profile.github.org_name,
                "repo_name": profile.github.repo_name,
                "default_branch": profile.github.default_branch
            },
            "release": {
                "auto_release": profile.release.auto_release,
                "versioning_scheme": profile.release.versioning_scheme
            },
            "automation": {
                "cron_expression": profile.automation.cron_expression,
                "max_retries": profile.automation.max_retries
            },
            "workspace": {
                "workspace_root": profile.workspace.workspace_root,
                "exclude_patterns": profile.workspace.exclude_patterns
            },
            "timestamp": profile.timestamp
        }

    def deserialize(self, data: Dict[str, Any]) -> EngineeringProfile:
        project_data = data.get("project", {})
        project = ProjectProfile(
            project_name=project_data.get("project_name", ""),
            version=project_data.get("version", "0.1.0"),
            description=project_data.get("description", "")
        )
        
        coding_data = data.get("coding", {})
        coding = CodingProfile(
            language=coding_data.get("language", "python"),
            coding_standards=coding_data.get("coding_standards", []),
            naming_conventions=coding_data.get("naming_conventions", {})
        )
        
        testing_data = data.get("testing", {})
        testing = TestingProfile(
            framework=testing_data.get("framework", "pytest"),
            min_statement_coverage=float(testing_data.get("min_statement_coverage", 80.0)),
            min_branch_coverage=float(testing_data.get("min_branch_coverage", 75.0))
        )
        
        exec_data = data.get("execution", {})
        execution = ExecutionProfile(
            max_timeout_seconds=int(exec_data.get("max_timeout_seconds", 300)),
            sandbox_enabled=bool(exec_data.get("sandbox_enabled", True))
        )
        
        doc_data = data.get("documentation", {})
        documentation = DocumentationProfile(
            format=doc_data.get("format", "markdown"),
            generate_api_docs=bool(doc_data.get("generate_api_docs", True))
        )
        
        git_data = data.get("github", {})
        github = GitHubProfile(
            org_name=git_data.get("org_name", ""),
            repo_name=git_data.get("repo_name", ""),
            default_branch=git_data.get("default_branch", "main")
        )
        
        rel_data = data.get("release", {})
        release = ReleaseProfile(
            auto_release=bool(rel_data.get("auto_release", False)),
            versioning_scheme=rel_data.get("versioning_scheme", "semver")
        )
        
        auto_data = data.get("automation", {})
        automation = AutomationProfile(
            cron_expression=auto_data.get("cron_expression", ""),
            max_retries=int(auto_data.get("max_retries", 3))
        )
        
        work_data = data.get("workspace", {})
        workspace = WorkspaceProfile(
            workspace_root=work_data.get("workspace_root", ""),
            exclude_patterns=work_data.get("exclude_patterns", [])
        )

        return EngineeringProfile(
            profile_id=data.get("profile_id", "default"),
            project=project,
            coding=coding,
            testing=testing,
            execution=execution,
            documentation=documentation,
            github=github,
            release=release,
            automation=automation,
            workspace=workspace,
            timestamp=float(data.get("timestamp", time.time()))
        )


class LocalProfileLoader(ProfileLoader):
    """Loads profiles from JSON files on local disk paths."""

    def load_from_file(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load profile configuration from '{file_path}': {e}")
            return {}


class LocalProfileManager(ProfileManager):
    """Deep merges profile structures and runs basic validations checks."""

    def merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(base)
        for key, value in override.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                merged[key] = self.merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    def validate(self, profile: EngineeringProfile) -> List[str]:
        errors = []
        if not profile.profile_id:
            errors.append("Profile id must not be empty.")
        if not profile.project.project_name:
            errors.append("Project name must not be empty.")
        if not (0.0 <= profile.testing.min_statement_coverage <= 100.0):
            errors.append("Min statement coverage must stand between 0.0 and 100.0.")
        if not (0.0 <= profile.testing.min_branch_coverage <= 100.0):
            errors.append("Min branch coverage must stand between 0.0 and 100.0.")
        if profile.execution.max_timeout_seconds <= 0:
            errors.append("Max timeout seconds must exceed zero.")
        return errors


class LocalEngineeringProfileService(EngineeringProfileService):
    """Concrete profile service orchestrating serializer, registry, loader, and manager tools."""

    def __init__(
        self,
        memory_service: MemoryService,
        knowledge_hub: Optional[KnowledgeHubService] = None,
        model_service: Optional[Any] = None,
        registry: Optional[Any] = None
    ) -> None:
        self._memory = memory_service
        self._knowledge_hub = knowledge_hub
        self._model = model_service
        self._registry = registry

        self._in_memory_registry = ProfileRegistry()
        self._serializer = LocalProfileSerializer()
        self._loader = LocalProfileLoader()
        self._manager = LocalProfileManager()

    def initialize(self) -> None:
        logger.info("Initializing LocalEngineeringProfileService")
        # Load default profile
        default_dict = {
            "profile_id": "default",
            "project": {
                "project_name": "Personal AI OS",
                "version": "1.0.0",
                "description": "Principal OS Kernel Layer Configurations."
            },
            "coding": {
                "language": "python",
                "coding_standards": ["PEP8", "type-safety"],
                "naming_conventions": {"class": "PascalCase", "function": "snake_case"}
            },
            "testing": {
                "framework": "pytest",
                "min_statement_coverage": 85.0,
                "min_branch_coverage": 80.0
            },
            "execution": {
                "max_timeout_seconds": 600,
                "sandbox_enabled": True
            },
            "documentation": {
                "format": "markdown",
                "generate_api_docs": True
            },
            "github": {
                "org_name": "Anzar0904",
                "repo_name": "Aios",
                "default_branch": "main"
            },
            "release": {
                "auto_release": False,
                "versioning_scheme": "semver"
            },
            "automation": {
                "cron_expression": "*/5 * * * *",
                "max_retries": 3
            },
            "workspace": {
                "workspace_root": "/Users/anzarakhtar/aios",
                "exclude_patterns": [".venv", "node_modules"]
            }
        }
        
        default_profile = self._serializer.deserialize(default_dict)
        self._in_memory_registry.register("default", default_profile)

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get_profile(self, profile_id: str) -> Optional[EngineeringProfile]:
        return self._in_memory_registry.get(profile_id)

    def save_profile(self, profile: EngineeringProfile) -> None:
        self._in_memory_registry.register(profile.profile_id, profile)

    def store_profile_summary(self, profile: EngineeringProfile) -> None:
        content = (
            f"Engineering Profile Registered - ID: {profile.profile_id}\n"
            f"Project: {profile.project.project_name} (v{profile.project.version})\n"
            f"Language standard: {profile.coding.language}\n"
            f"Testing framework: {profile.testing.framework} (Target statement: {profile.testing.min_statement_coverage:.1f}%)\n"
            f"Default GitHub Branch: {profile.github.default_branch}"
        )
        
        self._memory.add_memory(
            content=content,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id=profile.profile_id,
                session_id=profile.profile_id,
                tags=["engineering_profile", "configuration"],
                importance=2,
                source_subsystem="profile_service"
            )
        )

    def publish_profile_summary(self, profile: EngineeringProfile) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        report_md = (
            f"# Engineering Profile Summary Configuration\n\n"
            f"**Profile ID**: `{profile.profile_id}`\n"
            f"**Project Name**: {profile.project.project_name}\n"
            f"**Language Standard**: `{profile.coding.language}`\n"
            f"**Testing Framework**: `{profile.testing.framework}`\n"
            f"**Statement Target Coverage**: {profile.testing.min_statement_coverage:.1f}%\n"
            f"**Branch Target Coverage**: {profile.testing.min_branch_coverage:.1f}%\n"
            f"**Sandbox Enabled**: `{profile.execution.sandbox_enabled}`\n"
            f"**Target Repository**: `{profile.github.org_name}/{profile.github.repo_name}`\n"
        )

        doc = KnowledgeDocument(
            document_id=f"profile_summary_{profile.profile_id}",
            title=f"Engineering Profile Configuration - {profile.profile_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"profile_summary_{profile.profile_id}",
                timestamp=profile.timestamp,
                source_subsystem="profile_service",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

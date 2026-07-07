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
from aios.services.persistence import EngineeringProfileRepository, PersistencePolicy, PersistenceStatus
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
            "id": profile.profile_id,
            "workspace_id": getattr(profile, "workspace_id", None),
            "project_name": profile.project.project_name,
            "project_version": profile.project.version,
            "project_description": profile.project.description,
            "language": profile.coding.language,
            "coding_standards": profile.coding.coding_standards,
            "naming_conventions": profile.coding.naming_conventions,
            "testing_framework": profile.testing.framework,
            "min_statement_coverage": profile.testing.min_statement_coverage,
            "min_branch_coverage": profile.testing.min_branch_coverage,
            "max_timeout_seconds": profile.execution.max_timeout_seconds,
            "sandbox_enabled": profile.execution.sandbox_enabled,
            "documentation_format": profile.documentation.format,
            "generate_api_docs": profile.documentation.generate_api_docs,
            "release_formatting_rules": profile.documentation.release_formatting_rules,
            "markdown_preferences": profile.documentation.markdown_preferences,
            "section_ordering": profile.documentation.section_ordering,
            "doc_naming_conventions": profile.documentation.naming_conventions,
            "doc_versioning_preferences": profile.documentation.versioning_preferences,
            "github_org": profile.github.org_name,
            "github_repo": profile.github.repo_name,
            "github_default_branch": profile.github.default_branch,
            "auto_release": profile.release.auto_release,
            "versioning_scheme": profile.release.versioning_scheme,
            "cron_expression": profile.automation.cron_expression,
            "max_retries": profile.automation.max_retries,
            "workspace_root": profile.workspace.workspace_root,
            "exclude_patterns": profile.workspace.exclude_patterns,
            "timestamp": profile.timestamp,
        }

    def deserialize(self, data: Dict[str, Any]) -> EngineeringProfile:
        # Support both flat DB-row format and nested config-file format.
        is_flat = "language" in data or "project_name" in data or "id" in data

        if is_flat:
            # Flat format from DB rows
            coding_standards = data.get("coding_standards", [])
            if isinstance(coding_standards, str):
                try:
                    import json as _json
                    coding_standards = _json.loads(coding_standards)
                except Exception:
                    coding_standards = []

            naming_conventions = data.get("naming_conventions", {})
            if isinstance(naming_conventions, str):
                try:
                    import json as _json
                    naming_conventions = _json.loads(naming_conventions)
                except Exception:
                    naming_conventions = {}

            def _json_parse(val, default):
                if isinstance(val, str):
                    try:
                        import json as _json
                        return _json.loads(val)
                    except Exception:
                        return default
                return val if val is not None else default

            project = ProjectProfile(
                project_name=data.get("project_name", ""),
                version=data.get("project_version", "0.1.0"),
                description=data.get("project_description", "")
            )
            coding = CodingProfile(
                language=data.get("language", "python"),
                coding_standards=coding_standards,
                naming_conventions=naming_conventions,
            )
            testing = TestingProfile(
                framework=data.get("testing_framework", "pytest"),
                min_statement_coverage=float(data.get("min_statement_coverage", 80.0) or 80.0),
                min_branch_coverage=float(data.get("min_branch_coverage", 75.0) or 75.0),
            )
            execution = ExecutionProfile(
                max_timeout_seconds=int(data.get("max_timeout_seconds", 300) or 300),
                sandbox_enabled=bool(data.get("sandbox_enabled", True)),
            )
            documentation = DocumentationProfile(
                format=data.get("documentation_format", "markdown"),
                generate_api_docs=bool(data.get("generate_api_docs", True)),
                release_formatting_rules=_json_parse(data.get("release_formatting_rules"), {}),
                markdown_preferences=_json_parse(data.get("markdown_preferences"), {}),
                section_ordering=_json_parse(data.get("section_ordering"), []),
                naming_conventions=_json_parse(data.get("doc_naming_conventions"), {}),
                versioning_preferences=_json_parse(data.get("doc_versioning_preferences"), {}),
            )
            github = GitHubProfile(
                org_name=data.get("github_org", ""),
                repo_name=data.get("github_repo", ""),
                default_branch=data.get("github_default_branch", "main"),
            )
            release = ReleaseProfile(
                auto_release=bool(data.get("auto_release", False)),
                versioning_scheme=data.get("versioning_scheme", "semver"),
            )
            automation = AutomationProfile(
                cron_expression=data.get("cron_expression", ""),
                max_retries=int(data.get("max_retries", 3) or 3),
            )
            workspace = WorkspaceProfile(
                workspace_root=data.get("workspace_root", ""),
                exclude_patterns=_json_parse(data.get("exclude_patterns"), []),
            )
            return EngineeringProfile(
                profile_id=data.get("id") or data.get("profile_id", "default"),
                project=project,
                coding=coding,
                testing=testing,
                execution=execution,
                documentation=documentation,
                github=github,
                release=release,
                automation=automation,
                workspace=workspace,
                timestamp=float(data.get("timestamp", time.time()) or time.time()),
            )

        # Nested config-file format
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
            generate_api_docs=bool(doc_data.get("generate_api_docs", True)),
            release_formatting_rules=doc_data.get("release_formatting_rules", {}),
            markdown_preferences=doc_data.get("markdown_preferences", {}),
            section_ordering=doc_data.get("section_ordering", []),
            naming_conventions=doc_data.get("naming_conventions", {}),
            versioning_preferences=doc_data.get("versioning_preferences", {})
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
    """Concrete profile service orchestrating database persistence and verification checks."""

    def __init__(
        self,
        memory_service: MemoryService,
        knowledge_hub: Optional[KnowledgeHubService] = None,
        model_service: Optional[Any] = None,
        registry: Optional[Any] = None,
        profile_repo: Optional[EngineeringProfileRepository] = None
    ) -> None:
        self._memory = memory_service
        self._knowledge_hub = knowledge_hub
        self._model = model_service
        self._registry = registry
        self._profile_repo = profile_repo

        self._in_memory_registry = ProfileRegistry()
        self._serializer = LocalProfileSerializer()
        self._loader = LocalProfileLoader()
        self._manager = LocalProfileManager()

    def _get_policy(self) -> PersistencePolicy:
        policy = PersistencePolicy.STRICT
        if self._registry:
            try:
                from aios.services.persistence import PersistenceService
                p_svc = self._registry.get(PersistenceService)
                if p_svc and p_svc.config:
                    return p_svc.config.policy
            except Exception:
                pass
        if self._profile_repo and hasattr(self._profile_repo, "service"):
            try:
                return self._profile_repo.service.config.policy
            except Exception:
                pass
        return policy

    def initialize(self) -> None:
        logger.info("Initializing LocalEngineeringProfileService")
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
                "generate_api_docs": True,
                "release_formatting_rules": {
                    "include_header_metadata": True,
                    "use_code_blocks_for_versions": True
                },
                "markdown_preferences": {
                    "list_style": "-",
                    "bold_headers": True
                },
                "section_ordering": [
                    "Feature Summary",
                    "Bug Fix Summary",
                    "Breaking Changes",
                    "Validation Summary",
                    "Known Issues",
                    "Compatibility Notes",
                    "Future Improvements",
                    "Release Checklist",
                    "Deployment Notes",
                    "Rollback Notes"
                ],
                "naming_conventions": {
                    "release_notes": "RELEASE_NOTES_{version}.md",
                    "changelog": "CHANGELOG.md",
                    "migration_guide": "MIGRATION_GUIDE_{from}_TO_{to}.md",
                    "upgrade_guide": "UPGRADE_GUIDE_{version}.md"
                },
                "versioning_preferences": {
                    "supported_channels": ["alpha", "beta", "rc", "stable"],
                    "strict_semver": True
                }
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
        policy = self._get_policy()
        if self._profile_repo:
            try:
                existing = self._profile_repo.get("default")
                if not existing:
                    res = self._profile_repo.save(self._serializer.serialize(default_profile))
                    if res.status != PersistenceStatus.SUCCESS:
                        is_awaiting = (res.status == PersistenceStatus.AWAITING_RUNTIME_CONFIGURATION)
                        if policy == PersistencePolicy.STRICT and not is_awaiting:
                            raise RuntimeError(f"Strict initialization failure: {res.message}")
                        else:
                            logger.warning(f"Database error during initialize(): {res.message}. Using in-memory.")
                            self._in_memory_registry.register("default", default_profile)
                    else:
                        self._in_memory_registry.register("default", default_profile)
                else:
                    db_default = self.get_profile("default")
                    if db_default:
                        self._in_memory_registry.register("default", db_default)
            except Exception as e:
                is_awaiting = False
                if self._profile_repo and hasattr(self._profile_repo, "service"):
                    try:
                        status_res = self._profile_repo.service.check_status()
                        if status_res.status == PersistenceStatus.AWAITING_RUNTIME_CONFIGURATION:
                            is_awaiting = True
                    except Exception:
                        pass

                if policy == PersistencePolicy.STRICT and not is_awaiting:
                    logger.error("Strict initialization database error.")
                    raise
                logger.warning(f"Database error during initialize(): {e}. Using in-memory fallback.")
                self._in_memory_registry.register("default", default_profile)
        else:
            self._in_memory_registry.register("default", default_profile)

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get_profile(self, profile_id: str) -> Optional[EngineeringProfile]:
        policy = self._get_policy()
        if self._profile_repo:
            try:
                data = self._profile_repo.get(profile_id)
                if not data:
                    return self._in_memory_registry.get(profile_id)

                mapped = {
                    "profile_id": data["id"],
                    "project": {
                        "project_name": data.get("project_name", ""),
                        "version": data.get("project_version", "1.0.0"),
                        "description": data.get("project_description", "")
                    },
                    "coding": {
                        "language": data.get("language", "python"),
                        "coding_standards": data.get("coding_standards", []),
                        "naming_conventions": data.get("naming_conventions", {})
                    },
                    "testing": {
                        "framework": data.get("testing_framework", "pytest"),
                        "min_statement_coverage": data.get("min_statement_coverage", 80.0),
                        "min_branch_coverage": data.get("min_branch_coverage", 75.0)
                    },
                    "execution": {
                        "max_timeout_seconds": data.get("max_timeout_seconds", 300),
                        "sandbox_enabled": data.get("sandbox_enabled", True)
                    },
                    "documentation": {
                        "format": data.get("documentation_format", "markdown"),
                        "generate_api_docs": data.get("generate_api_docs", True),
                        "release_formatting_rules": data.get("release_formatting_rules", {}),
                        "markdown_preferences": data.get("markdown_preferences", {}),
                        "section_ordering": data.get("section_ordering", []),
                        "naming_conventions": data.get("doc_naming_conventions", {}),
                        "versioning_preferences": data.get("doc_versioning_preferences", {})
                    },
                    "github": {
                        "org_name": data.get("github_org", ""),
                        "repo_name": data.get("github_repo", ""),
                        "default_branch": data.get("github_default_branch", "main")
                    },
                    "release": {
                        "auto_release": data.get("auto_release", False),
                        "versioning_scheme": data.get("versioning_scheme", "semver")
                    },
                    "automation": {
                        "cron_expression": data.get("cron_expression", ""),
                        "max_retries": data.get("max_retries", 3)
                    },
                    "workspace": {
                        "workspace_root": data.get("workspace_root", ""),
                        "exclude_patterns": data.get("exclude_patterns", [])
                    },
                    "timestamp": data.get("timestamp", time.time())
                }
                profile = self._serializer.deserialize(mapped)
                self._in_memory_registry.register(profile_id, profile)
                return profile
            except Exception as e:
                if policy == PersistencePolicy.STRICT:
                    raise
                logger.warning(f"Database error getting profile {profile_id}: {e}. Falling back to in-memory.")
                return self._in_memory_registry.get(profile_id)

        return self._in_memory_registry.get(profile_id)

    def save_profile(self, profile: EngineeringProfile) -> None:
        errors = self._manager.validate(profile)
        if errors:
            raise ValueError(f"Profile validation failed: {errors}")

        policy = self._get_policy()

        if self._profile_repo:
            mapped = {
                "id": profile.profile_id,
                "workspace_id": profile.workspace.workspace_root,
                "project_name": profile.project.project_name,
                "project_version": profile.project.version,
                "project_description": profile.project.description,
                "language": profile.coding.language,
                "coding_standards": profile.coding.coding_standards,
                "naming_conventions": profile.coding.naming_conventions,
                "testing_framework": profile.testing.framework,
                "min_statement_coverage": profile.testing.min_statement_coverage,
                "min_branch_coverage": profile.testing.min_branch_coverage,
                "max_timeout_seconds": profile.execution.max_timeout_seconds,
                "sandbox_enabled": profile.execution.sandbox_enabled,
                "documentation_format": profile.documentation.format,
                "generate_api_docs": profile.documentation.generate_api_docs,
                "release_formatting_rules": profile.documentation.release_formatting_rules,
                "markdown_preferences": profile.documentation.markdown_preferences,
                "section_ordering": profile.documentation.section_ordering,
                "doc_naming_conventions": profile.documentation.naming_conventions,
                "doc_versioning_preferences": profile.documentation.versioning_preferences,
                "github_org": profile.github.org_name,
                "github_repo": profile.github.repo_name,
                "github_default_branch": profile.github.default_branch,
                "auto_release": profile.release.auto_release,
                "versioning_scheme": profile.release.versioning_scheme,
                "cron_expression": profile.automation.cron_expression,
                "max_retries": profile.automation.max_retries,
                "workspace_root": profile.workspace.workspace_root,
                "exclude_patterns": profile.workspace.exclude_patterns,
                "timestamp": profile.timestamp
            }
            try:
                res = self._profile_repo.save(mapped)
                if res.status != PersistenceStatus.SUCCESS:
                    if policy == PersistencePolicy.STRICT:
                        raise RuntimeError(f"Strict persistence save failure: {res.message}")
                    else:
                        logger.warning(f"Persistence best-effort fallback: {res.message}")
                self._in_memory_registry.register(profile.profile_id, profile)
            except Exception as e:
                if policy == PersistencePolicy.STRICT:
                    raise RuntimeError(f"Strict persistence save failure: {e}") from e
                logger.warning(f"Database error saving profile {profile.profile_id}: {e}.")
                self._in_memory_registry.register(profile.profile_id, profile)
        else:
            self._in_memory_registry.register(profile.profile_id, profile)

    def delete_profile(self, profile_id: str) -> None:
        policy = self._get_policy()
        if self._profile_repo:
            try:
                res = self._profile_repo.delete(profile_id)
                if res.status != PersistenceStatus.SUCCESS:
                    if policy == PersistencePolicy.STRICT:
                        raise RuntimeError(f"Strict persistence delete failure: {res.message}")
                    else:
                        logger.warning(f"Persistence best-effort fallback: {res.message}")
                self._in_memory_registry._profiles.pop(profile_id, None)
            except Exception as e:
                if policy == PersistencePolicy.STRICT:
                    raise RuntimeError(f"Strict persistence delete failure: {e}") from e
                logger.warning(f"Database error deleting profile {profile_id}: {e}.")
                self._in_memory_registry._profiles.pop(profile_id, None)
        else:
            self._in_memory_registry._profiles.pop(profile_id, None)

    def get_profile_history(self, profile_id: str) -> List[Dict[str, Any]]:
        policy = self._get_policy()
        if self._profile_repo:
            try:
                return self._profile_repo.get_history(profile_id)
            except Exception as e:
                if policy == PersistencePolicy.STRICT:
                    raise
                logger.warning(f"Database error getting history for profile {profile_id}: {e}.")
        return []

    def rollback_profile(self, profile_id: str, version: int) -> None:
        policy = self._get_policy()
        if not self._profile_repo:
            return
        try:
            history = self.get_profile_history(profile_id)
            target = None
            for record in history:
                if record.get("version") == version:
                    target = record
                    break
            if not target:
                raise ValueError(f"Version {version} not found in profile history.")
            
            mapped = {
                "id": target["id"],
                "workspace_id": target.get("workspace_id", ""),
                "project_name": target.get("project_name", ""),
                "project_version": target.get("project_version", ""),
                "project_description": target.get("project_description", ""),
                "language": target.get("language", ""),
                "coding_standards": target.get("coding_standards", []),
                "naming_conventions": target.get("naming_conventions", {}),
                "testing_framework": target.get("testing_framework", ""),
                "min_statement_coverage": target.get("min_statement_coverage", 80.0),
                "min_branch_coverage": target.get("min_branch_coverage", 75.0),
                "max_timeout_seconds": target.get("max_timeout_seconds", 300),
                "sandbox_enabled": bool(target.get("sandbox_enabled", True)),
                "documentation_format": target.get("documentation_format", ""),
                "generate_api_docs": bool(target.get("generate_api_docs", True)),
                "release_formatting_rules": target.get("release_formatting_rules", {}),
                "markdown_preferences": target.get("markdown_preferences", {}),
                "section_ordering": target.get("section_ordering", []),
                "doc_naming_conventions": target.get("doc_naming_conventions", {}),
                "doc_versioning_preferences": target.get("doc_versioning_preferences", {}),
                "github_org": target.get("github_org", ""),
                "github_repo": target.get("github_repo", ""),
                "github_default_branch": target.get("github_default_branch", ""),
                "auto_release": bool(target.get("auto_release", False)),
                "versioning_scheme": target.get("versioning_scheme", ""),
                "cron_expression": target.get("cron_expression", ""),
                "max_retries": target.get("max_retries", 3),
                "workspace_root": target.get("workspace_root", ""),
                "exclude_patterns": target.get("exclude_patterns", []),
                "timestamp": time.time()
            }
            res = self._profile_repo.save(mapped)
            if res.status != PersistenceStatus.SUCCESS:
                if policy == PersistencePolicy.STRICT:
                    raise RuntimeError(f"Strict persistence rollback failure: {res.message}")
                else:
                    logger.warning(f"Persistence best-effort rollback fallback: {res.message}")
            
            p = self.get_profile(profile_id)
            if p:
                self._in_memory_registry.register(profile_id, p)
        except Exception as e:
            if policy == PersistencePolicy.STRICT:
                raise RuntimeError(f"Strict persistence rollback failure: {e}") from e
            logger.warning(f"Database error rolling back profile {profile_id}: {e}.")
            if isinstance(e, ValueError):
                raise

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

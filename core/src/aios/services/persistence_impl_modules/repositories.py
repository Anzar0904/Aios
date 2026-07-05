# ruff: noqa: F403, F405, E501, N802, E402, N806, B007
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle
from aios.services.persistence import *

logger = logging.getLogger(__name__)


class WorkspaceRepositoryImpl(WorkspaceRepository):
    """Concrete repository mapping workspaces configuration schemas to SQLite/PostgreSQL."""

    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def save(self, workspace: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("workspaces", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        if self.service.config.policy == PersistencePolicy.READ_ONLY:
            return PersistenceResult(
                status=PersistenceStatus.READ_ONLY_MODE,
                message="Cannot write: READ_ONLY policy is active.",
                repository="workspaces",
            )

        start_time = time.time()
        try:
            q = (
                "INSERT INTO workspaces (id, name, metadata, state, created_at, last_accessed, version, status, health) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "name=excluded.name, metadata=excluded.metadata, state=excluded.state, "
                "last_accessed=excluded.last_accessed, version=excluded.version, "
                "status=excluded.status, health=excluded.health"
            )
            self.service.execute(
                q,
                (
                    workspace["id"],
                    workspace.get("name"),
                    json.dumps(workspace.get("metadata", {})),
                    workspace.get("state"),
                    workspace.get("created_at"),
                    workspace.get("last_accessed"),
                    workspace.get("version"),
                    workspace.get("status"),
                    workspace.get("health"),
                ),
            )
            latency = (time.time() - start_time) * 1000

            # Cache integration
            from aios.registry import ServiceRegistry

            try:
                cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
                policy_mgr = ServiceRegistry._global_registry.get(CachePolicyManager)
            except Exception:
                cache_svc = None
                policy_mgr = None

            if cache_svc and policy_mgr:
                policy = policy_mgr.get_policy("workspace")
                if policy == CachePolicy.WRITE_THROUGH:
                    cache_svc.set("workspace", workspace["id"], workspace)
                elif policy != CachePolicy.NO_CACHE:
                    cache_svc.delete("workspace", workspace["id"])

            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workspace saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workspaces",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="workspaces",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        status_res = self.service.check_status("workspaces", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return None

        from aios.registry import ServiceRegistry

        try:
            cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
        except Exception:
            cache_svc = None

        def fetch():
            q = "SELECT * FROM workspaces WHERE id = ?"
            rows = self.service.execute(q, (workspace_id,))
            if not rows:
                return None
            row = dict(rows[0])
            row["metadata"] = json.loads(row["metadata"] or "{}")
            return row

        if cache_svc:
            return cache_svc.get("workspace", workspace_id, fetch)
        return fetch()

    def delete(self, workspace_id: str) -> PersistenceResult:
        status_res = self.service.check_status("workspaces", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        if self.service.config.policy == PersistencePolicy.READ_ONLY:
            return PersistenceResult(
                status=PersistenceStatus.READ_ONLY_MODE,
                message="Cannot write: READ_ONLY policy is active.",
                repository="workspaces",
            )

        start_time = time.time()
        try:
            q = "DELETE FROM workspaces WHERE id = ?"
            self.service.execute(q, (workspace_id,))
            latency = (time.time() - start_time) * 1000

            # Cache integration
            from aios.registry import ServiceRegistry

            try:
                cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
            except Exception:
                cache_svc = None
            if cache_svc:
                cache_svc.delete("workspace", workspace_id)

            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workspace deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workspaces",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="workspaces",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def list_all(self) -> List[Dict[str, Any]]:
        status_res = self.service.check_status("workspaces", "list_all")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return []

        try:
            rows = self.service.execute("SELECT * FROM workspaces")
            results = []
            for r in rows:
                row = dict(r)
                row["metadata"] = json.loads(row["metadata"] or "{}")
                results.append(row)
            return results
        except Exception:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise
            return []


class WorkspaceSessionRepositoryImpl(WorkspaceSessionRepository):
    """Concrete repository mapping session lifecycles durability."""

    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def save(self, session: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("workspace_sessions", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        if self.service.config.policy == PersistencePolicy.READ_ONLY:
            return PersistenceResult(
                status=PersistenceStatus.READ_ONLY_MODE,
                message="Cannot write: READ_ONLY policy is active.",
                repository="workspace_sessions",
            )

        start_time = time.time()
        try:
            q = (
                "INSERT INTO workspace_sessions (id, workspace_id, start_time, end_time, state, "
                "current_task, current_branch, current_agent, current_provider, metrics, health, checkpoints, resume_metadata) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "workspace_id=excluded.workspace_id, start_time=excluded.start_time, end_time=excluded.end_time, "
                "state=excluded.state, current_task=excluded.current_task, current_branch=excluded.current_branch, "
                "current_agent=excluded.current_agent, current_provider=excluded.current_provider, "
                "metrics=excluded.metrics, health=excluded.health, checkpoints=excluded.checkpoints, resume_metadata=excluded.resume_metadata"
            )
            self.service.execute(
                q,
                (
                    session["id"],
                    session.get("workspace_id"),
                    session.get("start_time"),
                    session.get("end_time"),
                    session.get("state"),
                    session.get("current_task"),
                    session.get("current_branch"),
                    session.get("current_agent"),
                    session.get("current_provider"),
                    json.dumps(session.get("metrics", {})),
                    session.get("health"),
                    json.dumps(session.get("checkpoints", {})),
                    json.dumps(session.get("resume_metadata", {})),
                ),
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workspace session saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workspace_sessions",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="workspace_sessions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        status_res = self.service.check_status("workspace_sessions", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return None

        try:
            q = "SELECT * FROM workspace_sessions WHERE id = ?"
            rows = self.service.execute(q, (session_id,))
            if not rows:
                return None
            row = dict(rows[0])
            row["metrics"] = json.loads(row["metrics"] or "{}")
            row["checkpoints"] = json.loads(row["checkpoints"] or "{}")
            row["resume_metadata"] = json.loads(row["resume_metadata"] or "{}")
            return row
        except Exception:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise
            return None

    def delete(self, session_id: str) -> PersistenceResult:
        status_res = self.service.check_status("workspace_sessions", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        if self.service.config.policy == PersistencePolicy.READ_ONLY:
            return PersistenceResult(
                status=PersistenceStatus.READ_ONLY_MODE,
                message="Cannot write: READ_ONLY policy is active.",
                repository="workspace_sessions",
            )

        start_time = time.time()
        try:
            q = "DELETE FROM workspace_sessions WHERE id = ?"
            self.service.execute(q, (session_id,))
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workspace session deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workspace_sessions",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="workspace_sessions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def list_all(self) -> List[Dict[str, Any]]:
        status_res = self.service.check_status("workspace_sessions", "list_all")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return []

        try:
            rows = self.service.execute("SELECT * FROM workspace_sessions")
            results = []
            for r in rows:
                row = dict(r)
                row["metrics"] = json.loads(row["metrics"] or "{}")
                row["checkpoints"] = json.loads(row["checkpoints"] or "{}")
                row["resume_metadata"] = json.loads(row["resume_metadata"] or "{}")
                results.append(row)
            return results
        except Exception:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise
            return []


class ProjectRepositoryImpl(ProjectRepository):
    """Concrete repository mapping projects models."""

    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def save(self, project: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("projects", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        if self.service.config.policy == PersistencePolicy.READ_ONLY:
            return PersistenceResult(
                status=PersistenceStatus.READ_ONLY_MODE,
                message="Cannot write: READ_ONLY policy is active.",
                repository="projects",
            )

        start_time = time.time()
        try:
            q = (
                "INSERT INTO projects (id, workspace_id, name, version, description) "
                "VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "workspace_id=excluded.workspace_id, name=excluded.name, "
                "version=excluded.version, description=excluded.description"
            )
            self.service.execute(
                q,
                (
                    project["id"],
                    project.get("workspace_id"),
                    project.get("name"),
                    project.get("version"),
                    project.get("description"),
                ),
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Project saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="projects",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="projects",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, project_id: str) -> Optional[Dict[str, Any]]:
        status_res = self.service.check_status("projects", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return None

        try:
            q = "SELECT * FROM projects WHERE id = ?"
            rows = self.service.execute(q, (project_id,))
            if not rows:
                return None
            return dict(rows[0])
        except Exception:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise
            return None

    def delete(self, project_id: str) -> PersistenceResult:
        status_res = self.service.check_status("projects", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        if self.service.config.policy == PersistencePolicy.READ_ONLY:
            return PersistenceResult(
                status=PersistenceStatus.READ_ONLY_MODE,
                message="Cannot write: READ_ONLY policy is active.",
                repository="projects",
            )

        start_time = time.time()
        try:
            q = "DELETE FROM projects WHERE id = ?"
            self.service.execute(q, (project_id,))
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Project deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="projects",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="projects",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class EngineeringProfileRepositoryImpl(EngineeringProfileRepository):
    """Concrete repository mapping engineering configurations and historical versions."""

    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def save(self, profile: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("engineering_profiles", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        if self.service.config.policy == PersistencePolicy.READ_ONLY:
            return PersistenceResult(
                status=PersistenceStatus.READ_ONLY_MODE,
                message="Cannot write: READ_ONLY policy is active.",
                repository="engineering_profiles",
            )

        start_time = time.time()
        try:
            existing = self.get(profile["id"])
            history_list = []
            ver = 1
            if existing:
                ver = existing.get("version", 1) + 1
                history_str = existing.get("history") or "[]"
                try:
                    history_list = json.loads(history_str)
                except Exception:
                    history_list = []
                old_record = dict(existing)
                old_record.pop("history", None)
                history_list.append(old_record)

            q = (
                "INSERT INTO engineering_profiles (id, workspace_id, project_name, project_version, project_description, "
                "language, coding_standards, naming_conventions, testing_framework, min_statement_coverage, min_branch_coverage, "
                "max_timeout_seconds, sandbox_enabled, documentation_format, generate_api_docs, release_formatting_rules, "
                "markdown_preferences, section_ordering, doc_naming_conventions, doc_versioning_preferences, github_org, "
                "github_repo, github_default_branch, auto_release, versioning_scheme, cron_expression, max_retries, "
                "workspace_root, exclude_patterns, timestamp, history, version) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "workspace_id=excluded.workspace_id, project_name=excluded.project_name, project_version=excluded.project_version, "
                "project_description=excluded.project_description, language=excluded.language, coding_standards=excluded.coding_standards, "
                "naming_conventions=excluded.naming_conventions, testing_framework=excluded.testing_framework, "
                "min_statement_coverage=excluded.min_statement_coverage, min_branch_coverage=excluded.min_branch_coverage, "
                "max_timeout_seconds=excluded.max_timeout_seconds, sandbox_enabled=excluded.sandbox_enabled, "
                "documentation_format=excluded.documentation_format, generate_api_docs=excluded.generate_api_docs, "
                "release_formatting_rules=excluded.release_formatting_rules, markdown_preferences=excluded.markdown_preferences, "
                "section_ordering=excluded.section_ordering, doc_naming_conventions=excluded.doc_naming_conventions, "
                "doc_versioning_preferences=excluded.doc_versioning_preferences, github_org=excluded.github_org, "
                "github_repo=excluded.github_repo, github_default_branch=excluded.github_default_branch, "
                "auto_release=excluded.auto_release, versioning_scheme=excluded.versioning_scheme, "
                "cron_expression=excluded.cron_expression, max_retries=excluded.max_retries, "
                "workspace_root=excluded.workspace_root, exclude_patterns=excluded.exclude_patterns, "
                "timestamp=excluded.timestamp, history=excluded.history, version=excluded.version"
            )
            self.service.execute(
                q,
                (
                    profile["id"],
                    profile.get("workspace_id"),
                    profile.get("project_name"),
                    profile.get("project_version"),
                    profile.get("project_description"),
                    profile.get("language"),
                    json.dumps(profile.get("coding_standards", [])),
                    json.dumps(profile.get("naming_conventions", {})),
                    profile.get("testing_framework"),
                    profile.get("min_statement_coverage"),
                    profile.get("min_branch_coverage"),
                    profile.get("max_timeout_seconds"),
                    1 if profile.get("sandbox_enabled") else 0,
                    profile.get("documentation_format"),
                    1 if profile.get("generate_api_docs") else 0,
                    json.dumps(profile.get("release_formatting_rules", {})),
                    json.dumps(profile.get("markdown_preferences", {})),
                    json.dumps(profile.get("section_ordering", [])),
                    json.dumps(profile.get("doc_naming_conventions", {})),
                    json.dumps(profile.get("doc_versioning_preferences", {})),
                    profile.get("github_org"),
                    profile.get("github_repo"),
                    profile.get("github_default_branch"),
                    1 if profile.get("auto_release") else 0,
                    profile.get("versioning_scheme"),
                    profile.get("cron_expression"),
                    profile.get("max_retries"),
                    profile.get("workspace_root"),
                    json.dumps(profile.get("exclude_patterns", [])),
                    profile.get("timestamp", time.time()),
                    json.dumps(history_list),
                    ver,
                ),
            )
            latency = (time.time() - start_time) * 1000

            # Cache integration
            from aios.registry import ServiceRegistry

            try:
                cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
                policy_mgr = ServiceRegistry._global_registry.get(CachePolicyManager)
            except Exception:
                cache_svc = None
                policy_mgr = None

            if cache_svc and policy_mgr:
                policy = policy_mgr.get_policy("profile")
                if policy == CachePolicy.WRITE_THROUGH:
                    prof_copy = {**profile}
                    prof_copy["coding_standards"] = profile.get("coding_standards", [])
                    prof_copy["naming_conventions"] = profile.get("naming_conventions", {})
                    prof_copy["release_formatting_rules"] = profile.get(
                        "release_formatting_rules", {}
                    )
                    prof_copy["markdown_preferences"] = profile.get("markdown_preferences", {})
                    prof_copy["section_ordering"] = profile.get("section_ordering", [])
                    prof_copy["doc_naming_conventions"] = profile.get("doc_naming_conventions", {})
                    prof_copy["doc_versioning_preferences"] = profile.get(
                        "doc_versioning_preferences", {}
                    )
                    prof_copy["exclude_patterns"] = profile.get("exclude_patterns", [])
                    prof_copy["sandbox_enabled"] = bool(profile.get("sandbox_enabled"))
                    prof_copy["generate_api_docs"] = bool(profile.get("generate_api_docs"))
                    prof_copy["auto_release"] = bool(profile.get("auto_release"))
                    prof_copy["version"] = ver
                    cache_svc.set("profile", profile["id"], prof_copy)
                elif policy != CachePolicy.NO_CACHE:
                    cache_svc.delete("profile", profile["id"])

            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Engineering profile saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="engineering_profiles",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="engineering_profiles",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, profile_id: str) -> Optional[Dict[str, Any]]:
        status_res = self.service.check_status("engineering_profiles", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return None

        from aios.registry import ServiceRegistry

        try:
            cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
        except Exception:
            cache_svc = None

        def fetch():
            q = "SELECT * FROM engineering_profiles WHERE id = ?"
            rows = self.service.execute(q, (profile_id,))
            if not rows:
                return None
            row = dict(rows[0])
            row["coding_standards"] = json.loads(row["coding_standards"] or "[]")
            row["naming_conventions"] = json.loads(row["naming_conventions"] or "{}")
            row["release_formatting_rules"] = json.loads(row["release_formatting_rules"] or "{}")
            row["markdown_preferences"] = json.loads(row["markdown_preferences"] or "{}")
            row["section_ordering"] = json.loads(row["section_ordering"] or "[]")
            row["doc_naming_conventions"] = json.loads(row["doc_naming_conventions"] or "{}")
            row["doc_versioning_preferences"] = json.loads(
                row["doc_versioning_preferences"] or "{}"
            )
            row["exclude_patterns"] = json.loads(row["exclude_patterns"] or "[]")
            row["sandbox_enabled"] = bool(row["sandbox_enabled"])
            row["generate_api_docs"] = bool(row["generate_api_docs"])
            row["auto_release"] = bool(row["auto_release"])
            return row

        if cache_svc:
            return cache_svc.get("profile", profile_id, fetch)
        return fetch()

    def delete(self, profile_id: str) -> PersistenceResult:
        status_res = self.service.check_status("engineering_profiles", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        if self.service.config.policy == PersistencePolicy.READ_ONLY:
            return PersistenceResult(
                status=PersistenceStatus.READ_ONLY_MODE,
                message="Cannot write: READ_ONLY policy is active.",
                repository="engineering_profiles",
            )

        start_time = time.time()
        try:
            q = "DELETE FROM engineering_profiles WHERE id = ?"
            self.service.execute(q, (profile_id,))
            latency = (time.time() - start_time) * 1000

            # Cache integration
            from aios.registry import ServiceRegistry

            try:
                cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
            except Exception:
                cache_svc = None
            if cache_svc:
                cache_svc.delete("profile", profile_id)

            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Engineering profile deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="engineering_profiles",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="engineering_profiles",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get_history(self, profile_id: str) -> List[Dict[str, Any]]:
        status_res = self.service.check_status("engineering_profiles", "get_history")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return []

        try:
            profile = self.get(profile_id)
            if not profile or not profile.get("history"):
                return []
            return json.loads(profile["history"])
        except Exception:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise
            return []


class ConfigurationRepositoryImpl(ConfigurationRepository):
    """Concrete repository mapping configuration profile references."""

    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def save(self, config_profile: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("configuration_profiles", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        if self.service.config.policy == PersistencePolicy.READ_ONLY:
            return PersistenceResult(
                status=PersistenceStatus.READ_ONLY_MODE,
                message="Cannot write: READ_ONLY policy is active.",
                repository="configuration_profiles",
            )

        start_time = time.time()
        try:
            q = (
                "INSERT INTO configuration_profiles (id, workspace_id, env_profile, workspace_settings, "
                "provider_preferences, git_preferences, automation_preferences, documentation_preferences, "
                "testing_preferences, approval_preferences) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "workspace_id=excluded.workspace_id, env_profile=excluded.env_profile, "
                "workspace_settings=excluded.workspace_settings, provider_preferences=excluded.provider_preferences, "
                "git_preferences=excluded.git_preferences, automation_preferences=excluded.automation_preferences, "
                "documentation_preferences=excluded.documentation_preferences, testing_preferences=excluded.testing_preferences, "
                "approval_preferences=excluded.approval_preferences"
            )
            self.service.execute(
                q,
                (
                    config_profile["id"],
                    config_profile.get("workspace_id"),
                    json.dumps(config_profile.get("env_profile", {})),
                    json.dumps(config_profile.get("workspace_settings", {})),
                    json.dumps(config_profile.get("provider_preferences", {})),
                    json.dumps(config_profile.get("git_preferences", {})),
                    json.dumps(config_profile.get("automation_preferences", {})),
                    json.dumps(config_profile.get("documentation_preferences", {})),
                    json.dumps(config_profile.get("testing_preferences", {})),
                    json.dumps(config_profile.get("approval_preferences", {})),
                ),
            )
            latency = (time.time() - start_time) * 1000

            # Cache integration
            from aios.registry import ServiceRegistry

            try:
                cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
                policy_mgr = ServiceRegistry._global_registry.get(CachePolicyManager)
            except Exception:
                cache_svc = None
                policy_mgr = None

            if cache_svc and policy_mgr:
                policy = policy_mgr.get_policy("configuration")
                if policy == CachePolicy.WRITE_THROUGH:
                    cfg_copy = {**config_profile}
                    cfg_copy["env_profile"] = config_profile.get("env_profile", {})
                    cfg_copy["workspace_settings"] = config_profile.get("workspace_settings", {})
                    cfg_copy["provider_preferences"] = config_profile.get(
                        "provider_preferences", {}
                    )
                    cfg_copy["git_preferences"] = config_profile.get("git_preferences", {})
                    cfg_copy["automation_preferences"] = config_profile.get(
                        "automation_preferences", {}
                    )
                    cfg_copy["documentation_preferences"] = config_profile.get(
                        "documentation_preferences", {}
                    )
                    cfg_copy["testing_preferences"] = config_profile.get("testing_preferences", {})
                    cfg_copy["approval_preferences"] = config_profile.get(
                        "approval_preferences", {}
                    )
                    cache_svc.set("configuration", config_profile["id"], cfg_copy)
                elif policy != CachePolicy.NO_CACHE:
                    cache_svc.delete("configuration", config_profile["id"])

            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Configuration profile saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="configuration_profiles",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="configuration_profiles",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, config_profile_id: str) -> Optional[Dict[str, Any]]:
        status_res = self.service.check_status("configuration_profiles", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return None

        from aios.registry import ServiceRegistry

        try:
            cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
        except Exception:
            cache_svc = None

        def fetch():
            q = "SELECT * FROM configuration_profiles WHERE id = ?"
            rows = self.service.execute(q, (config_profile_id,))
            if not rows:
                return None
            row = dict(rows[0])
            row["env_profile"] = json.loads(row["env_profile"] or "{}")
            row["workspace_settings"] = json.loads(row["workspace_settings"] or "{}")
            row["provider_preferences"] = json.loads(row["provider_preferences"] or "{}")
            row["git_preferences"] = json.loads(row["git_preferences"] or "{}")
            row["automation_preferences"] = json.loads(row["automation_preferences"] or "{}")
            row["documentation_preferences"] = json.loads(row["documentation_preferences"] or "{}")
            row["testing_preferences"] = json.loads(row["testing_preferences"] or "{}")
            row["approval_preferences"] = json.loads(row["approval_preferences"] or "{}")
            return row

        if cache_svc:
            return cache_svc.get("configuration", config_profile_id, fetch)
        return fetch()

    def delete(self, config_profile_id: str) -> PersistenceResult:
        status_res = self.service.check_status("configuration_profiles", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        if self.service.config.policy == PersistencePolicy.READ_ONLY:
            return PersistenceResult(
                status=PersistenceStatus.READ_ONLY_MODE,
                message="Cannot write: READ_ONLY policy is active.",
                repository="configuration_profiles",
            )

        start_time = time.time()
        try:
            q = "DELETE FROM configuration_profiles WHERE id = ?"
            self.service.execute(q, (config_profile_id,))
            latency = (time.time() - start_time) * 1000

            # Cache integration
            from aios.registry import ServiceRegistry

            try:
                cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
            except Exception:
                cache_svc = None
            if cache_svc:
                cache_svc.delete("configuration", config_profile_id)

            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Configuration profile deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="configuration_profiles",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="configuration_profiles",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class WorkspacePersistenceValidator(ServiceLifecycle):
    """Validator checking configuration inconsistencies."""

    def validate_workspace(self, workspace: Dict[str, Any]) -> List[str]:
        errors = []
        if not workspace.get("id"):
            errors.append("Workspace ID must not be empty.")
        if not workspace.get("version"):
            errors.append("Workspace version must not be empty.")
        return errors


class WorkspacePersistenceTelemetry(ServiceLifecycle):
    """Tracks query latency statistics and database rollbacks."""

    def __init__(self) -> None:
        self.rollbacks: int = 0
        self.failures: Dict[str, int] = {}
        self.latencies: List[float] = []

    def record_rollback(self) -> None:
        self.rollbacks += 1

    def record_failure(self, repo_name: str) -> None:
        self.failures[repo_name] = self.failures.get(repo_name, 0) + 1

    def record_latency(self, latency_ms: float) -> None:
        self.latencies.append(latency_ms)

    def get_telemetry(self) -> Dict[str, Any]:
        p95 = 0.0
        avg_lat = 0.0
        if self.latencies:
            sorted_l = sorted(self.latencies)
            idx = int(len(sorted_l) * 0.95)
            p95 = sorted_l[idx]
            avg_lat = sum(self.latencies) / len(self.latencies)
        return {
            "transaction_rollbacks": self.rollbacks,
            "repository_failures": self.failures,
            "average_query_latency_ms": avg_lat,
            "p95_query_latency_ms": p95,
        }


class WorkspacePersistenceStatistics(ServiceLifecycle):
    """Compiles statistics summaries from tables."""

    def __init__(
        self, workspace_repo: WorkspaceRepository, session_repo: WorkspaceSessionRepository
    ) -> None:
        self.workspace_repo = workspace_repo
        self.session_repo = session_repo

    def get_stats(self) -> Dict[str, Any]:
        try:
            workspaces = self.workspace_repo.list_all()
        except Exception:
            workspaces = []
        try:
            sessions = self.session_repo.list_all()
        except Exception:
            sessions = []
        return {
            "workspace_count": len(workspaces),
            "session_count": len(sessions),
            "active_session_count": len([s for s in sessions if s.get("state") == "active"]),
        }


class WorkspacePersistenceServiceImpl(WorkspacePersistenceService):
    """Concrete coordinating service executing operations across durable workspaces."""

    def __init__(
        self,
        workspace_repo: WorkspaceRepository,
        session_repo: WorkspaceSessionRepository,
        project_repo: ProjectRepository,
        profile_repo: EngineeringProfileRepository,
        config_repo: ConfigurationRepository,
        validator: WorkspacePersistenceValidator,
        telemetry: WorkspacePersistenceTelemetry,
        statistics: WorkspacePersistenceStatistics,
    ) -> None:
        self.workspace_repo = workspace_repo
        self.session_repo = session_repo
        self.project_repo = project_repo
        self.profile_repo = profile_repo
        self.config_repo = config_repo
        self.validator = validator
        self.telemetry = telemetry
        self.statistics = statistics

    def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        return self.workspace_repo.get(workspace_id)

    def save_workspace(self, workspace: Dict[str, Any]) -> None:
        errors = self.validator.validate_workspace(workspace)
        if errors:
            raise ValueError(f"Invalid workspace parameters: {errors}")
        self.workspace_repo.save(workspace)

        try:
            import time

            from aios.registry import ServiceRegistry
            from aios.services.persistence import SemanticMemoryManager

            registry = ServiceRegistry._global_registry
            if registry:
                sem_mgr = registry.get(SemanticMemoryManager)
                if sem_mgr:
                    ws_id = workspace.get("id") or workspace.get("workspace_id") or "default"
                    name = workspace.get("name") or workspace.get("project_name") or ws_id
                    desc = workspace.get("description") or "Workspace configuration metadata"

                    text_summary = f"Workspace Configuration: {name}\nID: {ws_id}\nDescription: {desc}\nMetadata: {workspace}"
                    metadata = {
                        "workspace_id": ws_id,
                        "project_id": workspace.get("project_id") or "default",
                        "timestamp": time.time(),
                        "type": "workspace_metadata",
                    }
                    sem_mgr.index_memory(
                        repository_name="workspace_memory",
                        entity_id=ws_id,
                        text=text_summary,
                        metadata=metadata,
                        tags=["workspace", "configuration", "metadata"],
                    )
        except Exception:
            pass


class WorkspacePersistenceReportGenerator(ServiceLifecycle):
    """Compiles metrics, registries, status, and health indicators into markdown reports."""

    def __init__(
        self,
        workspace_root: str,
        service: WorkspacePersistenceService,
        diagnostics: PersistenceDiagnostics,
        telemetry: WorkspacePersistenceTelemetry,
        statistics: WorkspacePersistenceStatistics,
        registry: RepositoryRegistry,
    ) -> None:
        self.workspace_root = workspace_root
        self.service = service
        self.diagnostics = diagnostics
        self.telemetry = telemetry
        self.statistics = statistics
        self.registry = registry

    def generate_reports(self) -> None:
        p_dir = os.path.join(self.workspace_root, "docs", "persistence")
        os.makedirs(p_dir, exist_ok=True)

        stats = self.statistics.get_stats()
        telemetry_data = self.telemetry.get_telemetry()
        diag = self.diagnostics.run_diagnostics()

        # 1. WORKSPACE_PERSISTENCE_STATUS.md
        with open(
            os.path.join(p_dir, "WORKSPACE_PERSISTENCE_STATUS.md"), "w", encoding="utf-8"
        ) as f:
            f.write(
                f"# Workspace Persistence Status\n\n"
                f"- **Status**: ACTIVE\n"
                f"- **Total Workspaces**: {stats['workspace_count']}\n"
                f"- **Active Sessions**: {stats['active_session_count']}\n"
                f"- **Diagnostics Status**: {diag['status'].upper()}\n"
            )

        # 2. WORKSPACE_HEALTH.md
        with open(os.path.join(p_dir, "WORKSPACE_HEALTH.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Workspace Persistence Health\n\n"
                f"- **P95 Latency**: {telemetry_data['p95_query_latency_ms']:.2f} ms\n"
                f"- **Average Query Latency**: {telemetry_data['average_query_latency_ms']:.2f} ms\n"
                f"- **Transaction Rollbacks**: {telemetry_data['transaction_rollbacks']}\n"
            )

        # 3. WORKSPACE_STATISTICS.md
        with open(os.path.join(p_dir, "WORKSPACE_STATISTICS.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Workspace Persistence Statistics\n\n"
                f"- **Workspace Count**: {stats['workspace_count']}\n"
                f"- **Session Count**: {stats['session_count']}\n"
                f"- **Active Session Count**: {stats['active_session_count']}\n"
            )

        # 4. WORKSPACE_DIAGNOSTICS.md
        with open(os.path.join(p_dir, "WORKSPACE_DIAGNOSTICS.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Workspace Diagnostics\n\n"
                f"- **Diagnostics Status**: {diag['status'].upper()}\n\n"
                f"## Logged Diagnostics Issues\n\n"
            )
            if diag["issues"]:
                for issue in diag["issues"]:
                    f.write(
                        f"### [{issue['type']}] {issue['message']}\n"
                        f"**Remediation**: {issue['remediation']}\n\n"
                    )
            else:
                f.write("All diagnostics validation checks passed.\n")

        # 5. REPOSITORY_REGISTRY.md
        with open(os.path.join(p_dir, "REPOSITORY_REGISTRY.md"), "w", encoding="utf-8") as f:
            f.write("# Repository Registry\n\nRegistered Repositories:\n\n")
            for repo_name in getattr(self.registry, "_repositories", {}).keys():
                f.write(f"- `{repo_name}`\n")


class EngineeringTaskRepositoryImpl(EngineeringTaskRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, task: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("engineering_tasks", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = (
                "INSERT INTO engineering_tasks (id, name, description, priority, status, "
                "creation_time, update_time, completion_time, workspace, current_phase, "
                "assigned_agent, dependencies, retry_count, operation_results) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "name=excluded.name, description=excluded.description, priority=excluded.priority, "
                "status=excluded.status, update_time=excluded.update_time, completion_time=excluded.completion_time, "
                "workspace=excluded.workspace, current_phase=excluded.current_phase, "
                "assigned_agent=excluded.assigned_agent, dependencies=excluded.dependencies, "
                "retry_count=excluded.retry_count, operation_results=excluded.operation_results"
            )
            self.service.execute(
                q,
                (
                    task["id"],
                    task.get("name"),
                    task.get("description"),
                    task.get("priority"),
                    task.get("status"),
                    task.get("creation_time"),
                    task.get("update_time"),
                    task.get("completion_time"),
                    task.get("workspace"),
                    task.get("current_phase"),
                    task.get("assigned_agent"),
                    json.dumps(task.get("dependencies") or []),
                    task.get("retry_count", 0),
                    json.dumps(task.get("operation_results") or {}),
                ),
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Task saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="engineering_tasks",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="engineering_tasks",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, task_id: str) -> PersistenceResult:
        status_res = self.service.check_status("engineering_tasks", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "SELECT * FROM engineering_tasks WHERE id = ?"
            rows = self.service.execute(q, (task_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=f"Task '{task_id}' not found.",
                    latency=latency,
                    repository="engineering_tasks",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            row["dependencies"] = json.loads(row["dependencies"] or "[]")
            row["operation_results"] = json.loads(row["operation_results"] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Task retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="engineering_tasks",
                payload=row,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="engineering_tasks",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, task_id: str) -> PersistenceResult:
        status_res = self.service.check_status("engineering_tasks", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "DELETE FROM engineering_tasks WHERE id = ?"
            self.service.execute(q, (task_id,))
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Task deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="engineering_tasks",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="engineering_tasks",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def list_all(self) -> PersistenceResult:
        status_res = self.service.check_status("engineering_tasks", "list_all")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "SELECT * FROM engineering_tasks"
            rows = self.service.execute(q)
            latency = (time.time() - start_time) * 1000
            results = []
            for r in rows:
                row = dict(r)
                row["dependencies"] = json.loads(row["dependencies"] or "[]")
                row["operation_results"] = json.loads(row["operation_results"] or "{}")
                results.append(row)
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Tasks listed successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="engineering_tasks",
                payload=results,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="engineering_tasks",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class PlanningRepositoryImpl(PlanningRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, plan: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("planning_sessions", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = (
                "INSERT INTO planning_sessions (id, execution_plan, decision_tree, "
                "architecture_decisions, dependency_graph, planning_statistics, planning_version, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "execution_plan=excluded.execution_plan, decision_tree=excluded.decision_tree, "
                "architecture_decisions=excluded.architecture_decisions, dependency_graph=excluded.dependency_graph, "
                "planning_statistics=excluded.planning_statistics, planning_version=excluded.planning_version, timestamp=excluded.timestamp"
            )
            self.service.execute(
                q,
                (
                    plan["id"],
                    json.dumps(plan.get("execution_plan") or {}),
                    json.dumps(plan.get("decision_tree") or {}),
                    json.dumps(plan.get("architecture_decisions") or {}),
                    json.dumps(plan.get("dependency_graph") or {}),
                    json.dumps(plan.get("planning_statistics") or {}),
                    plan.get("planning_version", 1),
                    plan.get("timestamp", time.time()),
                ),
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Planning session saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="planning_sessions",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="planning_sessions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, plan_id: str) -> PersistenceResult:
        status_res = self.service.check_status("planning_sessions", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "SELECT * FROM planning_sessions WHERE id = ?"
            rows = self.service.execute(q, (plan_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=f"Plan '{plan_id}' not found.",
                    latency=latency,
                    repository="planning_sessions",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            row["execution_plan"] = json.loads(row["execution_plan"] or "{}")
            row["decision_tree"] = json.loads(row["decision_tree"] or "{}")
            row["architecture_decisions"] = json.loads(row["architecture_decisions"] or "{}")
            row["dependency_graph"] = json.loads(row["dependency_graph"] or "{}")
            row["planning_statistics"] = json.loads(row["planning_statistics"] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Planning session retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="planning_sessions",
                payload=row,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="planning_sessions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, plan_id: str) -> PersistenceResult:
        status_res = self.service.check_status("planning_sessions", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "DELETE FROM planning_sessions WHERE id = ?"
            self.service.execute(q, (plan_id,))
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Planning session deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="planning_sessions",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="planning_sessions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ApprovalRepositoryImpl(ApprovalRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, approval: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("approval_sessions", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = (
                "INSERT INTO approval_sessions (id, workspace_id, metadata, decision_outcome, "
                "confidence, policy_used, review_status, approver, timeline_metadata, operation_results, created_at, closed_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "workspace_id=excluded.workspace_id, metadata=excluded.metadata, decision_outcome=excluded.decision_outcome, "
                "confidence=excluded.confidence, policy_used=excluded.policy_used, review_status=excluded.review_status, "
                "approver=excluded.approver, timeline_metadata=excluded.timeline_metadata, "
                "operation_results=excluded.operation_results, created_at=excluded.created_at, closed_at=excluded.closed_at"
            )
            self.service.execute(
                q,
                (
                    approval["id"],
                    approval.get("workspace_id"),
                    json.dumps(approval.get("metadata") or {}),
                    approval.get("decision_outcome"),
                    approval.get("confidence", 1.0),
                    json.dumps(approval.get("policy_used") or {}),
                    approval.get("review_status"),
                    approval.get("approver"),
                    json.dumps(approval.get("timeline_metadata") or {}),
                    json.dumps(approval.get("operation_results") or {}),
                    approval.get("created_at"),
                    approval.get("closed_at"),
                ),
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Approval session saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="approval_sessions",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="approval_sessions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, approval_id: str) -> PersistenceResult:
        status_res = self.service.check_status("approval_sessions", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "SELECT * FROM approval_sessions WHERE id = ?"
            rows = self.service.execute(q, (approval_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=f"Approval '{approval_id}' not found.",
                    latency=latency,
                    repository="approval_sessions",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            row["metadata"] = json.loads(row["metadata"] or "{}")
            row["policy_used"] = json.loads(row["policy_used"] or "{}")
            row["timeline_metadata"] = json.loads(row["timeline_metadata"] or "{}")
            row["operation_results"] = json.loads(row["operation_results"] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Approval session retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="approval_sessions",
                payload=row,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="approval_sessions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, approval_id: str) -> PersistenceResult:
        status_res = self.service.check_status("approval_sessions", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "DELETE FROM approval_sessions WHERE id = ?"
            self.service.execute(q, (approval_id,))
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Approval session deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="approval_sessions",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="approval_sessions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ReviewRepositoryImpl(ReviewRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, review: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("review_sessions", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = (
                "INSERT INTO review_sessions (id, session_id, workspace_id, state_transitions, metadata) "
                "VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "session_id=excluded.session_id, workspace_id=excluded.workspace_id, "
                "state_transitions=excluded.state_transitions, metadata=excluded.metadata"
            )
            self.service.execute(
                q,
                (
                    review["id"],
                    review.get("session_id"),
                    review.get("workspace_id"),
                    json.dumps(review.get("state_transitions") or []),
                    json.dumps(review.get("metadata") or {}),
                ),
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Review session saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="review_sessions",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="review_sessions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, review_id: str) -> PersistenceResult:
        status_res = self.service.check_status("review_sessions", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "SELECT * FROM review_sessions WHERE id = ?"
            rows = self.service.execute(q, (review_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=f"Review '{review_id}' not found.",
                    latency=latency,
                    repository="review_sessions",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            row["state_transitions"] = json.loads(row["state_transitions"] or "[]")
            row["metadata"] = json.loads(row["metadata"] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Review session retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="review_sessions",
                payload=row,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="review_sessions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, review_id: str) -> PersistenceResult:
        status_res = self.service.check_status("review_sessions", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "DELETE FROM review_sessions WHERE id = ?"
            self.service.execute(q, (review_id,))
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Review session deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="review_sessions",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="review_sessions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class DocumentationMetadataRepositoryImpl(DocumentationMetadataRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, doc: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("documentation_metadata", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = (
                "INSERT INTO documentation_metadata (id, workspace_id, session_id, category, "
                "status, generation_time, author, publication_status, knowledge_references, checksums, version) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "workspace_id=excluded.workspace_id, session_id=excluded.session_id, category=excluded.category, "
                "status=excluded.status, generation_time=excluded.generation_time, author=excluded.author, "
                "publication_status=excluded.publication_status, knowledge_references=excluded.knowledge_references, "
                "checksums=excluded.checksums, version=excluded.version"
            )
            self.service.execute(
                q,
                (
                    doc["id"],
                    doc.get("workspace_id"),
                    doc.get("session_id"),
                    doc.get("category"),
                    doc.get("status"),
                    doc.get("generation_time"),
                    doc.get("author"),
                    doc.get("publication_status"),
                    json.dumps(doc.get("knowledge_references") or []),
                    json.dumps(doc.get("checksums") or {}),
                    doc.get("version", 1),
                ),
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Documentation metadata saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="documentation_metadata",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="documentation_metadata",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, doc_id: str) -> PersistenceResult:
        status_res = self.service.check_status("documentation_metadata", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "SELECT * FROM documentation_metadata WHERE id = ?"
            rows = self.service.execute(q, (doc_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=f"Doc metadata '{doc_id}' not found.",
                    latency=latency,
                    repository="documentation_metadata",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            row["knowledge_references"] = json.loads(row["knowledge_references"] or "[]")
            row["checksums"] = json.loads(row["checksums"] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Documentation metadata retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="documentation_metadata",
                payload=row,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="documentation_metadata",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, doc_id: str) -> PersistenceResult:
        status_res = self.service.check_status("documentation_metadata", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "DELETE FROM documentation_metadata WHERE id = ?"
            self.service.execute(q, (doc_id,))
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Documentation metadata deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="documentation_metadata",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="documentation_metadata",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class TestSessionRepositoryImpl(TestSessionRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, session: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("test_sessions", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = (
                "INSERT INTO test_sessions (id, workspace_id, status, pass_count, fail_count, "
                "coverage_summary, execution_time, failure_categories, environment_metadata, operation_results, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "workspace_id=excluded.workspace_id, status=excluded.status, pass_count=excluded.pass_count, "
                "fail_count=excluded.fail_count, coverage_summary=excluded.coverage_summary, "
                "execution_time=excluded.execution_time, failure_categories=excluded.failure_categories, "
                "environment_metadata=excluded.environment_metadata, operation_results=excluded.operation_results, timestamp=excluded.timestamp"
            )
            self.service.execute(
                q,
                (
                    session["id"],
                    session.get("workspace_id"),
                    session.get("status"),
                    session.get("pass_count", 0),
                    session.get("fail_count", 0),
                    json.dumps(session.get("coverage_summary") or {}),
                    session.get("execution_time", 0.0),
                    json.dumps(session.get("failure_categories") or {}),
                    json.dumps(session.get("environment_metadata") or {}),
                    json.dumps(session.get("operation_results") or {}),
                    session.get("timestamp", time.time()),
                ),
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Test session saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="test_sessions",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="test_sessions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, session_id: str) -> PersistenceResult:
        status_res = self.service.check_status("test_sessions", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "SELECT * FROM test_sessions WHERE id = ?"
            rows = self.service.execute(q, (session_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=f"Test session '{session_id}' not found.",
                    latency=latency,
                    repository="test_sessions",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            row["coverage_summary"] = json.loads(row["coverage_summary"] or "{}")
            row["failure_categories"] = json.loads(row["failure_categories"] or "{}")
            row["environment_metadata"] = json.loads(row["environment_metadata"] or "{}")
            row["operation_results"] = json.loads(row["operation_results"] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Test session retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="test_sessions",
                payload=row,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="test_sessions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, session_id: str) -> PersistenceResult:
        status_res = self.service.check_status("test_sessions", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "DELETE FROM test_sessions WHERE id = ?"
            self.service.execute(q, (session_id,))
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Test session deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="test_sessions",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="test_sessions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class TestResultRepositoryImpl(TestResultRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, result: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("test_results", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = (
                "INSERT INTO test_results (id, session_id, suite_id, name, category, passed, execution_time, error_message, metadata) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "session_id=excluded.session_id, suite_id=excluded.suite_id, name=excluded.name, "
                "category=excluded.category, passed=excluded.passed, execution_time=excluded.execution_time, "
                "error_message=excluded.error_message, metadata=excluded.metadata"
            )
            self.service.execute(
                q,
                (
                    result["id"],
                    result.get("session_id"),
                    result.get("suite_id"),
                    result.get("name"),
                    result.get("category"),
                    1 if result.get("passed") else 0,
                    result.get("execution_time", 0.0),
                    result.get("error_message"),
                    json.dumps(result.get("metadata") or {}),
                ),
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Test result saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="test_results",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="test_results",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, result_id: str) -> PersistenceResult:
        status_res = self.service.check_status("test_results", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "SELECT * FROM test_results WHERE id = ?"
            rows = self.service.execute(q, (result_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=f"Test result '{result_id}' not found.",
                    latency=latency,
                    repository="test_results",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            row["passed"] = bool(row["passed"])
            row["metadata"] = json.loads(row["metadata"] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Test result retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="test_results",
                payload=row,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="test_results",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, result_id: str) -> PersistenceResult:
        status_res = self.service.check_status("test_results", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "DELETE FROM test_results WHERE id = ?"
            self.service.execute(q, (result_id,))
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Test result deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="test_results",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="test_results",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class EngineeringMemoryValidator(ServiceLifecycle):
    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def validate_task(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"):
            errors.append("Missing required field: id")
        if not data.get("name"):
            errors.append("Missing required field: name")
        return errors

    def validate_plan(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"):
            errors.append("Missing required field: id")
        return errors

    def validate_approval(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"):
            errors.append("Missing required field: id")
        return errors

    def validate_review(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"):
            errors.append("Missing required field: id")
        return errors

    def validate_doc(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"):
            errors.append("Missing required field: id")
        return errors

    def validate_test_session(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"):
            errors.append("Missing required field: id")
        return errors

    def validate_test_result(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"):
            errors.append("Missing required field: id")
        return errors


class EngineeringMemoryTelemetry(ServiceLifecycle):
    def __init__(self) -> None:
        self.latencies: List[float] = []
        self.query_count = 0
        self.failures = 0

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def record_query(self, latency_ms: float, success: bool = True) -> None:
        self.latencies.append(latency_ms)
        self.query_count += 1
        if not success:
            self.failures += 1

    def get_average_latency(self) -> float:
        if not self.latencies:
            return 0.0
        return sum(self.latencies) / len(self.latencies)

    def get_p95_latency(self) -> float:
        if not self.latencies:
            return 0.0
        sorted_lats = sorted(self.latencies)
        idx = int(len(sorted_lats) * 0.95)
        return sorted_lats[min(idx, len(sorted_lats) - 1)]


class EngineeringMemoryStatistics(ServiceLifecycle):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def compile_statistics(self) -> Dict[str, Any]:
        stats = {
            "task_count": 0,
            "planning_count": 0,
            "approval_count": 0,
            "documentation_count": 0,
            "test_count": 0,
            "repository_utilization": {},
            "repository_failures": 0,
        }
        status_res = self.service.check_status()
        if status_res.status != PersistenceStatus.SUCCESS:
            stats["repository_failures"] += 1
            return stats

        try:
            t_rows = self.service.execute("SELECT COUNT(*) as cnt FROM engineering_tasks")
            if t_rows:
                stats["task_count"] = t_rows[0].get("cnt", 0)

            p_rows = self.service.execute("SELECT COUNT(*) as cnt FROM planning_sessions")
            if p_rows:
                stats["planning_count"] = p_rows[0].get("cnt", 0)

            a_rows = self.service.execute("SELECT COUNT(*) as cnt FROM approval_sessions")
            if a_rows:
                stats["approval_count"] = a_rows[0].get("cnt", 0)

            d_rows = self.service.execute("SELECT COUNT(*) as cnt FROM documentation_metadata")
            if d_rows:
                stats["documentation_count"] = d_rows[0].get("cnt", 0)

            ts_rows = self.service.execute("SELECT COUNT(*) as cnt FROM test_sessions")
            if ts_rows:
                stats["test_count"] = ts_rows[0].get("cnt", 0)

            stats["repository_utilization"] = {
                "engineering_tasks": stats["task_count"],
                "planning_sessions": stats["planning_count"],
                "approval_sessions": stats["approval_count"],
                "documentation_metadata": stats["documentation_count"],
                "test_sessions": stats["test_count"],
            }
        except Exception:
            stats["repository_failures"] += 1

        return stats


class EngineeringMemoryHealthMonitor(ServiceLifecycle):
    def __init__(
        self,
        service: PersistenceService,
        telemetry: EngineeringMemoryTelemetry,
        stats_compiler: EngineeringMemoryStatistics,
    ) -> None:
        self.service = service
        self.telemetry = telemetry
        self.stats_compiler = stats_compiler

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def check_health(self) -> Dict[str, Any]:
        health_data = {"status": "healthy", "server_reachable": False, "metrics": {}, "errors": []}

        status_res = self.service.check_status()
        health_data["server_reachable"] = status_res.status == PersistenceStatus.SUCCESS
        if not health_data["server_reachable"]:
            health_data["status"] = "degraded"
            health_data["errors"].append(status_res.message)

        stats = self.stats_compiler.compile_statistics()
        health_data["metrics"] = {
            "query_count": self.telemetry.query_count,
            "average_latency_ms": self.telemetry.get_average_latency(),
            "p95_latency_ms": self.telemetry.get_p95_latency(),
            "repository_failures": self.telemetry.failures + stats.get("repository_failures", 0),
            "task_count": stats.get("task_count", 0),
            "planning_count": stats.get("planning_count", 0),
            "approval_count": stats.get("approval_count", 0),
            "documentation_count": stats.get("documentation_count", 0),
            "test_count": stats.get("test_count", 0),
            "policy": self.service.config.policy.name if self.service.config else "STRICT",
        }

        return health_data


class EngineeringMemoryReportGenerator(ServiceLifecycle):
    def __init__(self, workspace_root: str, health_monitor: EngineeringMemoryHealthMonitor) -> None:
        self.workspace_root = workspace_root
        self.health_monitor = health_monitor

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def generate_reports(self) -> None:
        p_dir = os.path.join(self.workspace_root, "docs", "persistence")
        os.makedirs(p_dir, exist_ok=True)

        health_data = self.health_monitor.check_health()
        metrics = health_data["metrics"]

        # 1. ENGINEERING_MEMORY_STATUS.md
        with open(os.path.join(p_dir, "ENGINEERING_MEMORY_STATUS.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Engineering Memory Subsystem Status\n\n"
                f"- **Status**: {health_data['status'].upper()}\n"
                f"- **Database Reachable**: {health_data['server_reachable']}\n"
                f"- **Active Policy**: {metrics.get('policy', 'STRICT')}\n"
            )

        # 2. ENGINEERING_MEMORY_HEALTH.md
        with open(os.path.join(p_dir, "ENGINEERING_MEMORY_HEALTH.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Engineering Memory Health Metrics\n\n"
                f"- **Total Queries Executed**: {metrics.get('query_count', 0)}\n"
                f"- **Average Query Latency**: {metrics.get('average_latency_ms', 0.0):.2f} ms\n"
                f"- **P95 Query Latency**: {metrics.get('p95_latency_ms', 0.0):.2f} ms\n"
                f"- **Repository Failures**: {metrics.get('repository_failures', 0)}\n"
            )

        # 3. ENGINEERING_MEMORY_STATISTICS.md
        with open(
            os.path.join(p_dir, "ENGINEERING_MEMORY_STATISTICS.md"), "w", encoding="utf-8"
        ) as f:
            f.write(
                f"# Engineering Memory Statistics\n\n"
                f"- **Task Count**: {metrics.get('task_count', 0)}\n"
                f"- **Planning Count**: {metrics.get('planning_count', 0)}\n"
                f"- **Approval Count**: {metrics.get('approval_count', 0)}\n"
                f"- **Documentation Count**: {metrics.get('documentation_count', 0)}\n"
                f"- **Test Count**: {metrics.get('test_count', 0)}\n"
            )

        # 4. ENGINEERING_MEMORY_DIAGNOSTICS.md
        with open(
            os.path.join(p_dir, "ENGINEERING_MEMORY_DIAGNOSTICS.md"), "w", encoding="utf-8"
        ) as f:
            f.write("# Engineering Memory Diagnostics\n\n")
            if health_data["errors"]:
                for err in health_data["errors"]:
                    f.write(f"- **Error**: {err}\n")
            else:
                f.write("All diagnostics validation checks passed. Database operation is stable.\n")


class EngineeringMemoryServiceImpl(EngineeringMemoryService):
    def __init__(
        self,
        service: PersistenceService,
        task_repo: EngineeringTaskRepository,
        planning_repo: PlanningRepository,
        approval_repo: ApprovalRepository,
        review_repo: ReviewRepository,
        doc_repo: DocumentationMetadataRepository,
        test_session_repo: TestSessionRepository,
        test_result_repo: TestResultRepository,
        validator: EngineeringMemoryValidator,
        telemetry: EngineeringMemoryTelemetry,
        stats_compiler: EngineeringMemoryStatistics,
        health_monitor: EngineeringMemoryHealthMonitor,
        report_generator: EngineeringMemoryReportGenerator,
    ) -> None:
        self.service = service
        self.task_repo = task_repo
        self.planning_repo = planning_repo
        self.approval_repo = approval_repo
        self.review_repo = review_repo
        self.doc_repo = doc_repo
        self.test_session_repo = test_session_repo
        self.test_result_repo = test_result_repo
        self.validator = validator
        self.telemetry = telemetry
        self.stats_compiler = stats_compiler
        self.health_monitor = health_monitor
        self.report_generator = report_generator

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def _get_repo(self, category: str) -> Optional[Any]:
        repos = {
            "tasks": self.task_repo,
            "planning": self.planning_repo,
            "approvals": self.approval_repo,
            "reviews": self.review_repo,
            "documentation": self.doc_repo,
            "test_sessions": self.test_session_repo,
            "test_results": self.test_result_repo,
        }
        return repos.get(category)

    def Record(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult:
        return self.record(category, entity_id, data)

    def record(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult:
        start_time = time.time()
        repo = self._get_repo(category)
        if not repo:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'"
            )

        errors = []
        if category == "tasks":
            errors = self.validator.validate_task(data)
        elif category == "planning":
            errors = self.validator.validate_plan(data)
        elif category == "approvals":
            errors = self.validator.validate_approval(data)
        elif category == "reviews":
            errors = self.validator.validate_review(data)
        elif category == "documentation":
            errors = self.validator.validate_doc(data)
        elif category == "test_sessions":
            errors = self.validator.validate_test_session(data)
        elif category == "test_results":
            errors = self.validator.validate_test_result(data)

        if errors:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(
                status=PersistenceStatus.VALIDATION_FAILED,
                message=f"Validation failed: {errors}",
                repository=category,
            )

        data["id"] = entity_id
        res = repo.save(data)
        latency = (time.time() - start_time) * 1000
        self.telemetry.record_query(latency, res.status == PersistenceStatus.SUCCESS)

        if res.status == PersistenceStatus.SUCCESS:
            try:
                is_completed_task = category == "tasks" and data.get("status") == "completed"
                tags = data.get("tags") or []
                if isinstance(tags, str):
                    tags = [tags]
                tags_lower = [t.lower() for t in tags]

                is_arch_decision = "architecture" in tags_lower or "decision" in tags_lower
                is_code_review = category == "reviews" or "review" in tags_lower
                is_bug_fix = "bug" in tags_lower or "fix" in tags_lower
                is_tech_debt = "debt" in tags_lower or "refactor" in tags_lower
                is_design_discussion = "design" in tags_lower or "discussion" in tags_lower

                if (
                    is_completed_task
                    or is_arch_decision
                    or is_code_review
                    or is_bug_fix
                    or is_tech_debt
                    or is_design_discussion
                ):
                    from aios.registry import ServiceRegistry
                    from aios.services.persistence import SemanticMemoryManager

                    registry = ServiceRegistry._global_registry
                    if registry:
                        sem_mgr = registry.get(SemanticMemoryManager)
                        if sem_mgr:
                            summary_parts = [f"Engineering Memory [{category}] ID: {entity_id}"]
                            if "title" in data:
                                summary_parts.append(f"Title: {data['title']}")
                            if "description" in data:
                                summary_parts.append(f"Description: {data['description']}")
                            if "summary" in data:
                                summary_parts.append(f"Summary: {data['summary']}")
                            if "status" in data:
                                summary_parts.append(f"Status: {data['status']}")
                            summary_text = "\n".join(summary_parts)

                            metadata = {
                                "workspace_id": data.get("workspace_id")
                                or data.get("workspace")
                                or "default",
                                "project_id": data.get("project_id")
                                or data.get("project")
                                or "default",
                                "category": category,
                                "entity_id": entity_id,
                                "timestamp": time.time(),
                            }
                            sem_mgr.index_memory(
                                repository_name="engineering_memory",
                                entity_id=entity_id,
                                text=summary_text,
                                metadata=metadata,
                                tags=list(tags),
                            )
            except Exception:
                pass

        return res

    def Update(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult:
        return self.update(category, entity_id, data)

    def update(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult:
        return self.record(category, entity_id, data)

    def Archive(self, category: str, entity_id: str) -> PersistenceResult:
        return self.archive(category, entity_id)

    def archive(self, category: str, entity_id: str) -> PersistenceResult:
        start_time = time.time()
        repo = self._get_repo(category)
        if not repo:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'"
            )
        res = repo.get(entity_id)
        if res.status != PersistenceStatus.SUCCESS or not res.payload:
            self.telemetry.record_query(0.0, False)
            return res
        data = dict(res.payload)
        if "status" in data:
            data["status"] = "archived"
        elif "metadata" in data:
            if isinstance(data["metadata"], dict):
                data["metadata"]["archived"] = True
        else:
            data["archived"] = True
        res2 = repo.save(data)
        latency = (time.time() - start_time) * 1000
        self.telemetry.record_query(latency, res2.status == PersistenceStatus.SUCCESS)
        return res2

    def Restore(self, category: str, entity_id: str) -> PersistenceResult:
        return self.restore(category, entity_id)

    def restore(self, category: str, entity_id: str) -> PersistenceResult:
        start_time = time.time()
        repo = self._get_repo(category)
        if not repo:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'"
            )
        res = repo.get(entity_id)
        if res.status != PersistenceStatus.SUCCESS or not res.payload:
            self.telemetry.record_query(0.0, False)
            return res
        data = dict(res.payload)
        if "status" in data:
            data["status"] = "active"
        elif "metadata" in data:
            if isinstance(data["metadata"], dict) and "archived" in data["metadata"]:
                data["metadata"]["archived"] = False
        else:
            data["archived"] = False
        res2 = repo.save(data)
        latency = (time.time() - start_time) * 1000
        self.telemetry.record_query(latency, res2.status == PersistenceStatus.SUCCESS)
        return res2

    def History(self, category: str, entity_id: str) -> PersistenceResult:
        return self.history(category, entity_id)

    def history(self, category: str, entity_id: str) -> PersistenceResult:
        start_time = time.time()
        repo = self._get_repo(category)
        if not repo:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'"
            )
        res = repo.get(entity_id)
        latency = (time.time() - start_time) * 1000
        self.telemetry.record_query(latency, res.status == PersistenceStatus.SUCCESS)
        if res.status != PersistenceStatus.SUCCESS or not res.payload:
            return res
        payload = res.payload
        history_list = []
        if category == "reviews" and "state_transitions" in payload:
            history_list = payload["state_transitions"]
        else:
            history_list = [payload]
        return PersistenceResult(
            status=PersistenceStatus.SUCCESS, message="History retrieved.", payload=history_list
        )

    def Statistics(self) -> PersistenceResult:
        return self.statistics()

    def statistics(self) -> PersistenceResult:
        stats = self.stats_compiler.compile_statistics()
        return PersistenceResult(
            status=PersistenceStatus.SUCCESS, message="Statistics compiled.", payload=stats
        )

    def SearchMetadata(self, category: str, query_params: Dict[str, Any]) -> PersistenceResult:
        return self.search_metadata(category, query_params)

    def search_metadata(self, category: str, query_params: Dict[str, Any]) -> PersistenceResult:
        repo = self._get_repo(category)
        if not repo:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'"
            )

        table_map = {
            "tasks": "engineering_tasks",
            "planning": "planning_sessions",
            "approvals": "approval_sessions",
            "reviews": "review_sessions",
            "documentation": "documentation_metadata",
            "test_sessions": "test_sessions",
            "test_results": "test_results",
        }
        table_name = table_map.get(category)
        if not table_name:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'"
            )

        start_time = time.time()
        try:
            where_clauses = []
            params = []
            for k, v in query_params.items():
                where_clauses.append(f"{k} = ?")
                params.append(v)

            q = f"SELECT * FROM {table_name}"
            if where_clauses:
                q += " WHERE " + " AND ".join(where_clauses)

            rows = repo.service.execute(q, tuple(params) if params else None)
            latency = (time.time() - start_time) * 1000

            results = []
            for r in rows:
                row = dict(r)
                for json_field in [
                    "dependencies",
                    "operation_results",
                    "execution_plan",
                    "decision_tree",
                    "architecture_decisions",
                    "dependency_graph",
                    "planning_statistics",
                    "metadata",
                    "policy_used",
                    "timeline_metadata",
                    "state_transitions",
                    "knowledge_references",
                    "checksums",
                    "coverage_summary",
                    "failure_categories",
                    "environment_metadata",
                ]:
                    if json_field in row:
                        try:
                            row[json_field] = json.loads(row[json_field] or "{}")
                        except Exception:
                            pass
                results.append(row)

            self.telemetry.record_query(latency, True)
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Search executed successfully.",
                provider=repo.service.config.provider_name,
                latency=latency,
                repository=table_name,
                payload=results,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.telemetry.record_query(latency, False)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository=table_name,
            )
            return result


class WorkflowRepositoryImpl(WorkflowRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, workflow: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("automation_workflows", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = (
                "INSERT INTO automation_workflows (id, name, description, metadata, triggers, "
                "actions, conditions, variables, policy, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "name=excluded.name, description=excluded.description, metadata=excluded.metadata, "
                "triggers=excluded.triggers, actions=excluded.actions, conditions=excluded.conditions, "
                "variables=excluded.variables, policy=excluded.policy, created_at=excluded.created_at, "
                "updated_at=excluded.updated_at"
            )
            self.service.execute(
                q,
                (
                    workflow["id"],
                    workflow.get("name"),
                    workflow.get("description"),
                    json.dumps(workflow.get("metadata") or {}),
                    json.dumps(workflow.get("triggers") or []),
                    json.dumps(workflow.get("actions") or []),
                    json.dumps(workflow.get("conditions") or []),
                    json.dumps(workflow.get("variables") or []),
                    json.dumps(workflow.get("policy") or {}),
                    workflow.get("created_at") or time.time(),
                    workflow.get("updated_at") or time.time(),
                ),
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow definition saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="automation_workflows",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="automation_workflows",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, workflow_id: str) -> PersistenceResult:
        status_res = self.service.check_status("automation_workflows", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "SELECT * FROM automation_workflows WHERE id = ?"
            rows = self.service.execute(q, (workflow_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=f"Workflow definition '{workflow_id}' not found.",
                    latency=latency,
                    repository="automation_workflows",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            for json_field in [
                "metadata",
                "triggers",
                "actions",
                "conditions",
                "variables",
                "policy",
            ]:
                row[json_field] = json.loads(row[json_field] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow definition retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="automation_workflows",
                payload=row,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="automation_workflows",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, workflow_id: str) -> PersistenceResult:
        status_res = self.service.check_status("automation_workflows", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "DELETE FROM automation_workflows WHERE id = ?"
            self.service.execute(q, (workflow_id,))
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow definition deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="automation_workflows",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="automation_workflows",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class WorkflowExecutionRepositoryImpl(WorkflowExecutionRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, execution: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("workflow_executions", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = (
                "INSERT INTO workflow_executions (id, workflow_id, workspace_id, status, success, "
                "error_summary, execution_time, created_at, closed_at, metadata) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "workflow_id=excluded.workflow_id, workspace_id=excluded.workspace_id, status=excluded.status, "
                "success=excluded.success, error_summary=excluded.error_summary, execution_time=excluded.execution_time, "
                "created_at=excluded.created_at, closed_at=excluded.closed_at, metadata=excluded.metadata"
            )
            self.service.execute(
                q,
                (
                    execution["id"],
                    execution.get("workflow_id"),
                    execution.get("workspace_id"),
                    execution.get("status"),
                    execution.get("success", 0),
                    execution.get("error_summary"),
                    execution.get("execution_time", 0.0),
                    execution.get("created_at") or time.time(),
                    execution.get("closed_at"),
                    json.dumps(execution.get("metadata") or {}),
                ),
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow execution saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_executions",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_executions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, execution_id: str) -> PersistenceResult:
        status_res = self.service.check_status("workflow_executions", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "SELECT * FROM workflow_executions WHERE id = ?"
            rows = self.service.execute(q, (execution_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=f"Workflow execution '{execution_id}' not found.",
                    latency=latency,
                    repository="workflow_executions",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            row["metadata"] = json.loads(row["metadata"] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow execution retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_executions",
                payload=row,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_executions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, execution_id: str) -> PersistenceResult:
        status_res = self.service.check_status("workflow_executions", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "DELETE FROM workflow_executions WHERE id = ?"
            self.service.execute(q, (execution_id,))
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow execution deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_executions",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_executions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class WorkflowMonitoringRepositoryImpl(WorkflowMonitoringRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, monitor_report: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("workflow_monitoring", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = (
                "INSERT INTO workflow_monitoring (id, workflow_id, execution_summaries, health_summaries, "
                "performance_summaries, alert_summaries, success_rates, latency_summaries, retry_summaries, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "workflow_id=excluded.workflow_id, execution_summaries=excluded.execution_summaries, "
                "health_summaries=excluded.health_summaries, performance_summaries=excluded.performance_summaries, "
                "alert_summaries=excluded.alert_summaries, success_rates=excluded.success_rates, "
                "latency_summaries=excluded.latency_summaries, retry_summaries=excluded.retry_summaries, "
                "timestamp=excluded.timestamp"
            )
            self.service.execute(
                q,
                (
                    monitor_report["id"],
                    monitor_report.get("workflow_id"),
                    json.dumps(monitor_report.get("execution_summaries") or {}),
                    json.dumps(monitor_report.get("health_summaries") or {}),
                    json.dumps(monitor_report.get("performance_summaries") or {}),
                    json.dumps(monitor_report.get("alert_summaries") or []),
                    json.dumps(monitor_report.get("success_rates") or {}),
                    json.dumps(monitor_report.get("latency_summaries") or {}),
                    json.dumps(monitor_report.get("retry_summaries") or {}),
                    monitor_report.get("timestamp") or time.time(),
                ),
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow monitoring report saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_monitoring",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_monitoring",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, report_id: str) -> PersistenceResult:
        status_res = self.service.check_status("workflow_monitoring", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "SELECT * FROM workflow_monitoring WHERE id = ?"
            rows = self.service.execute(q, (report_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=f"Workflow monitoring report '{report_id}' not found.",
                    latency=latency,
                    repository="workflow_monitoring",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            for json_field in [
                "execution_summaries",
                "health_summaries",
                "performance_summaries",
                "alert_summaries",
                "success_rates",
                "latency_summaries",
                "retry_summaries",
            ]:
                row[json_field] = json.loads(row[json_field] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow monitoring report retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_monitoring",
                payload=row,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_monitoring",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, report_id: str) -> PersistenceResult:
        status_res = self.service.check_status("workflow_monitoring", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "DELETE FROM workflow_monitoring WHERE id = ?"
            self.service.execute(q, (report_id,))
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow monitoring report deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_monitoring",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_monitoring",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class WorkflowOptimizationRepositoryImpl(WorkflowOptimizationRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, optimization: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("workflow_optimizations", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = (
                "INSERT INTO workflow_optimizations (id, workflow_id, optimization_plans, detected_patterns, "
                "complexity_scores, recommendation_metadata, optimization_statistics, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "workflow_id=excluded.workflow_id, optimization_plans=excluded.optimization_plans, "
                "detected_patterns=excluded.detected_patterns, complexity_scores=excluded.complexity_scores, "
                "recommendation_metadata=excluded.recommendation_metadata, "
                "optimization_statistics=excluded.optimization_statistics, timestamp=excluded.timestamp"
            )
            self.service.execute(
                q,
                (
                    optimization["id"],
                    optimization.get("workflow_id"),
                    json.dumps(optimization.get("optimization_plans") or {}),
                    json.dumps(optimization.get("detected_patterns") or []),
                    json.dumps(optimization.get("complexity_scores") or {}),
                    json.dumps(optimization.get("recommendation_metadata") or {}),
                    json.dumps(optimization.get("optimization_statistics") or {}),
                    optimization.get("timestamp") or time.time(),
                ),
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow optimization recommendations saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_optimizations",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_optimizations",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, optimization_id: str) -> PersistenceResult:
        status_res = self.service.check_status("workflow_optimizations", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "SELECT * FROM workflow_optimizations WHERE id = ?"
            rows = self.service.execute(q, (optimization_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=f"Workflow optimization '{optimization_id}' not found.",
                    latency=latency,
                    repository="workflow_optimizations",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            for json_field in [
                "optimization_plans",
                "detected_patterns",
                "complexity_scores",
                "recommendation_metadata",
                "optimization_statistics",
            ]:
                row[json_field] = json.loads(row[json_field] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow optimization retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_optimizations",
                payload=row,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_optimizations",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, optimization_id: str) -> PersistenceResult:
        status_res = self.service.check_status("workflow_optimizations", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "DELETE FROM workflow_optimizations WHERE id = ?"
            self.service.execute(q, (optimization_id,))
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow optimization deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_optimizations",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_optimizations",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class WorkflowVersionRepositoryImpl(WorkflowVersionRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, version: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("workflow_versions", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = (
                "INSERT INTO workflow_versions (id, workflow_id, version_metadata, migration_metadata, "
                "compatibility_metadata, rollback_metadata, version_graph_references, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "workflow_id=excluded.workflow_id, version_metadata=excluded.version_metadata, "
                "migration_metadata=excluded.migration_metadata, compatibility_metadata=excluded.compatibility_metadata, "
                "rollback_metadata=excluded.rollback_metadata, version_graph_references=excluded.version_graph_references, "
                "timestamp=excluded.timestamp"
            )
            self.service.execute(
                q,
                (
                    version["id"],
                    version.get("workflow_id"),
                    json.dumps(version.get("version_metadata") or {}),
                    json.dumps(version.get("migration_metadata") or {}),
                    json.dumps(version.get("compatibility_metadata") or {}),
                    json.dumps(version.get("rollback_metadata") or {}),
                    json.dumps(version.get("version_graph_references") or {}),
                    version.get("timestamp") or time.time(),
                ),
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow version details saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_versions",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_versions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, version_id: str) -> PersistenceResult:
        status_res = self.service.check_status("workflow_versions", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "SELECT * FROM workflow_versions WHERE id = ?"
            rows = self.service.execute(q, (version_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=f"Workflow version '{version_id}' not found.",
                    latency=latency,
                    repository="workflow_versions",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            for json_field in [
                "version_metadata",
                "migration_metadata",
                "compatibility_metadata",
                "rollback_metadata",
                "version_graph_references",
            ]:
                row[json_field] = json.loads(row[json_field] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow version retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_versions",
                payload=row,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_versions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, version_id: str) -> PersistenceResult:
        status_res = self.service.check_status("workflow_versions", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "DELETE FROM workflow_versions WHERE id = ?"
            self.service.execute(q, (version_id,))
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow version deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_versions",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_versions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class WorkflowTranslationRepositoryImpl(WorkflowTranslationRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, translation: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("workflow_translations", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = (
                "INSERT INTO workflow_translations (id, workflow_id, workflow_metadata, translation_metadata, "
                "ir_version, translation_statistics, compilation_summaries, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "workflow_id=excluded.workflow_id, workflow_metadata=excluded.workflow_metadata, "
                "translation_metadata=excluded.translation_metadata, ir_version=excluded.ir_version, "
                "translation_statistics=excluded.translation_statistics, "
                "compilation_summaries=excluded.compilation_summaries, timestamp=excluded.timestamp"
            )
            self.service.execute(
                q,
                (
                    translation["id"],
                    translation.get("workflow_id"),
                    json.dumps(translation.get("workflow_metadata") or {}),
                    json.dumps(translation.get("translation_metadata") or {}),
                    translation.get("ir_version"),
                    json.dumps(translation.get("translation_statistics") or {}),
                    json.dumps(translation.get("compilation_summaries") or {}),
                    translation.get("timestamp") or time.time(),
                ),
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow translation saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_translations",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_translations",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, translation_id: str) -> PersistenceResult:
        status_res = self.service.check_status("workflow_translations", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "SELECT * FROM workflow_translations WHERE id = ?"
            rows = self.service.execute(q, (translation_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=f"Workflow translation '{translation_id}' not found.",
                    latency=latency,
                    repository="workflow_translations",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            for json_field in [
                "workflow_metadata",
                "translation_metadata",
                "translation_statistics",
                "compilation_summaries",
            ]:
                row[json_field] = json.loads(row[json_field] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow translation retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_translations",
                payload=row,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_translations",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, translation_id: str) -> PersistenceResult:
        status_res = self.service.check_status("workflow_translations", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "DELETE FROM workflow_translations WHERE id = ?"
            self.service.execute(q, (translation_id,))
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow translation deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_translations",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_translations",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class WorkflowIntegrationRepositoryImpl(WorkflowIntegrationRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, integration: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("workflow_integrations", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            conn_metadata = dict(integration.get("connection_metadata") or {})
            for key in ["password", "token", "secret", "cookie", "api_key", "credentials"]:
                if key in conn_metadata:
                    del conn_metadata[key]

            q = (
                "INSERT INTO workflow_integrations (id, workflow_id, execution_id, connection_metadata, "
                "server_metadata, health_metadata, capability_discovery, validation_metadata, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "workflow_id=excluded.workflow_id, execution_id=excluded.execution_id, "
                "connection_metadata=excluded.connection_metadata, server_metadata=excluded.server_metadata, "
                "health_metadata=excluded.health_metadata, capability_discovery=excluded.capability_discovery, "
                "validation_metadata=excluded.validation_metadata, timestamp=excluded.timestamp"
            )
            self.service.execute(
                q,
                (
                    integration["id"],
                    integration.get("workflow_id"),
                    integration.get("execution_id"),
                    json.dumps(conn_metadata),
                    json.dumps(integration.get("server_metadata") or {}),
                    json.dumps(integration.get("health_metadata") or {}),
                    json.dumps(integration.get("capability_discovery") or []),
                    json.dumps(integration.get("validation_metadata") or {}),
                    integration.get("timestamp") or time.time(),
                ),
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow integration metadata saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_integrations",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_integrations",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, integration_id: str) -> PersistenceResult:
        status_res = self.service.check_status("workflow_integrations", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "SELECT * FROM workflow_integrations WHERE id = ?"
            rows = self.service.execute(q, (integration_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=f"Workflow integration '{integration_id}' not found.",
                    latency=latency,
                    repository="workflow_integrations",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            for json_field in [
                "connection_metadata",
                "server_metadata",
                "health_metadata",
                "capability_discovery",
                "validation_metadata",
            ]:
                row[json_field] = json.loads(row[json_field] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow integration retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_integrations",
                payload=row,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_integrations",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, integration_id: str) -> PersistenceResult:
        status_res = self.service.check_status("workflow_integrations", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "DELETE FROM workflow_integrations WHERE id = ?"
            self.service.execute(q, (integration_id,))
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow integration deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_integrations",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_integrations",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class AutomationTelemetryRepositoryImpl(AutomationTelemetryRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, telemetry: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("workflow_executions", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = (
                "INSERT INTO workflow_executions (id, workflow_id, workspace_id, status, success, "
                "execution_time, created_at, metadata) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "status=excluded.status, success=excluded.success, execution_time=excluded.execution_time, "
                "metadata=excluded.metadata"
            )
            self.service.execute(
                q,
                (
                    telemetry["id"],
                    telemetry.get("workflow_id", "system"),
                    telemetry.get("workspace_id", "system"),
                    "telemetry",
                    1 if telemetry.get("success", True) else 0,
                    telemetry.get("execution_time", 0.0),
                    time.time(),
                    json.dumps(telemetry),
                ),
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Telemetry saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_executions",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_executions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, telemetry_id: str) -> PersistenceResult:
        status_res = self.service.check_status("workflow_executions", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "SELECT * FROM workflow_executions WHERE id = ?"
            rows = self.service.execute(q, (telemetry_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=f"Telemetry '{telemetry_id}' not found.",
                    latency=latency,
                    repository="workflow_executions",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            payload = json.loads(row["metadata"] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Telemetry retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_executions",
                payload=payload,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_executions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, telemetry_id: str) -> PersistenceResult:
        status_res = self.service.check_status("workflow_executions", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "DELETE FROM workflow_executions WHERE id = ?"
            self.service.execute(q, (telemetry_id,))
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Telemetry deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_executions",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_executions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class AutomationStatisticsRepositoryImpl(AutomationStatisticsRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, stats: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("automation_statistics", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = (
                "INSERT INTO automation_statistics (id, workflow_count, execution_count, translation_count, "
                "optimization_count, monitoring_count, version_count, success_ratios, failure_ratios, "
                "usage_trends, timestamp) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
                "ON CONFLICT(id) DO UPDATE SET "
                "workflow_count=excluded.workflow_count, execution_count=excluded.execution_count, "
                "translation_count=excluded.translation_count, optimization_count=excluded.optimization_count, "
                "monitoring_count=excluded.monitoring_count, version_count=excluded.version_count, "
                "success_ratios=excluded.success_ratios, failure_ratios=excluded.failure_ratios, "
                "usage_trends=excluded.usage_trends, timestamp=excluded.timestamp"
            )
            self.service.execute(
                q,
                (
                    stats["id"],
                    stats.get("workflow_count", 0),
                    stats.get("execution_count", 0),
                    stats.get("translation_count", 0),
                    stats.get("optimization_count", 0),
                    stats.get("monitoring_count", 0),
                    stats.get("version_count", 0),
                    json.dumps(stats.get("success_ratios") or {}),
                    json.dumps(stats.get("failure_ratios") or {}),
                    json.dumps(stats.get("usage_trends") or {}),
                    stats.get("timestamp") or time.time(),
                ),
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Automation statistics saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="automation_statistics",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="automation_statistics",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, stats_id: str) -> PersistenceResult:
        status_res = self.service.check_status("automation_statistics", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "SELECT * FROM automation_statistics WHERE id = ?"
            rows = self.service.execute(q, (stats_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=f"Automation statistics '{stats_id}' not found.",
                    latency=latency,
                    repository="automation_statistics",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            for json_field in ["success_ratios", "failure_ratios", "usage_trends"]:
                row[json_field] = json.loads(row[json_field] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Automation statistics retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="automation_statistics",
                payload=row,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="automation_statistics",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, stats_id: str) -> PersistenceResult:
        status_res = self.service.check_status("automation_statistics", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        start_time = time.time()
        try:
            q = "DELETE FROM automation_statistics WHERE id = ?"
            self.service.execute(q, (stats_id,))
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Automation statistics deleted successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="automation_statistics",
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="automation_statistics",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class AutomationPersistenceValidator(ServiceLifecycle):
    """Validates Automation entity schemas and structures."""

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def validate_workflow(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"):
            errors.append("Workflow id is missing.")
        if not data.get("name"):
            errors.append("Workflow name is missing.")
        return errors

    def validate_execution(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"):
            errors.append("Execution id is missing.")
        if not data.get("workflow_id"):
            errors.append("Workflow id is missing.")
        return errors

    def validate_monitor(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"):
            errors.append("Monitoring report id is missing.")
        return errors

    def validate_optimization(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"):
            errors.append("Optimization plan id is missing.")
        return errors

    def validate_version(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"):
            errors.append("Version id is missing.")
        return errors

    def validate_translation(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"):
            errors.append("Translation report id is missing.")
        return errors

    def validate_integration(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"):
            errors.append("Integration id is missing.")
        return errors

    def validate_telemetry(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"):
            errors.append("Telemetry id is missing.")
        return errors

    def validate_statistics(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"):
            errors.append("Statistics id is missing.")
        return errors


class AutomationPersistenceTelemetry(ServiceLifecycle):
    """Monitors queries latencies and failures for Automation Persistence Service."""

    def __init__(self) -> None:
        self.query_count = 0
        self.failure_count = 0
        self.latencies = []

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def record_query(self, latency: float, success: bool) -> None:
        self.query_count += 1
        self.latencies.append(latency)
        if not success:
            self.failure_count += 1

    def get_average_latency(self) -> float:
        if not self.latencies:
            return 0.0
        return sum(self.latencies) / len(self.latencies)

    def get_p95_latency(self) -> float:
        if not self.latencies:
            return 0.0
        sorted_lats = sorted(self.latencies)
        idx = int(len(sorted_lats) * 0.95)
        return sorted_lats[min(idx, len(sorted_lats) - 1)]


class AutomationPersistenceStatistics(ServiceLifecycle):
    """Compiles statistics across Automation tables."""

    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def compile_statistics(self) -> Dict[str, Any]:
        stats = {
            "workflow_count": 0,
            "execution_count": 0,
            "translation_count": 0,
            "optimization_count": 0,
            "monitoring_count": 0,
            "version_count": 0,
            "repository_utilization": {},
            "repository_failures": 0,
        }
        status_res = self.service.check_status()
        if status_res.status != PersistenceStatus.SUCCESS:
            stats["repository_failures"] += 1
            return stats

        try:
            w_rows = self.service.execute("SELECT COUNT(*) as cnt FROM automation_workflows")
            if w_rows:
                stats["workflow_count"] = w_rows[0].get("cnt", 0)

            e_rows = self.service.execute("SELECT COUNT(*) as cnt FROM workflow_executions")
            if e_rows:
                stats["execution_count"] = e_rows[0].get("cnt", 0)

            t_rows = self.service.execute("SELECT COUNT(*) as cnt FROM workflow_translations")
            if t_rows:
                stats["translation_count"] = t_rows[0].get("cnt", 0)

            o_rows = self.service.execute("SELECT COUNT(*) as cnt FROM workflow_optimizations")
            if o_rows:
                stats["optimization_count"] = o_rows[0].get("cnt", 0)

            m_rows = self.service.execute("SELECT COUNT(*) as cnt FROM workflow_monitoring")
            if m_rows:
                stats["monitoring_count"] = m_rows[0].get("cnt", 0)

            v_rows = self.service.execute("SELECT COUNT(*) as cnt FROM workflow_versions")
            if v_rows:
                stats["version_count"] = v_rows[0].get("cnt", 0)

            stats["repository_utilization"] = {
                "automation_workflows": stats["workflow_count"],
                "workflow_executions": stats["execution_count"],
                "workflow_translations": stats["translation_count"],
                "workflow_optimizations": stats["optimization_count"],
                "workflow_monitoring": stats["monitoring_count"],
                "workflow_versions": stats["version_count"],
            }
        except Exception:
            stats["repository_failures"] += 1

        return stats


class AutomationPersistenceHealthMonitor(ServiceLifecycle):
    """Validates connectivity and schema consistency for automation persistence."""

    def __init__(
        self,
        service: PersistenceService,
        telemetry: AutomationPersistenceTelemetry,
        stats: AutomationPersistenceStatistics,
    ) -> None:
        self.service = service
        self.telemetry = telemetry
        self.stats = stats

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def check_health(self) -> Dict[str, Any]:
        health = {
            "status": "healthy",
            "db_connected": False,
            "schema_verified": False,
            "telemetry_avg_latency_ms": self.telemetry.get_average_latency(),
            "failures": self.telemetry.failure_count,
        }
        res = self.service.check_status()
        if res.status == PersistenceStatus.SUCCESS:
            health["db_connected"] = True
            try:
                self.service.execute("SELECT 1 FROM automation_workflows LIMIT 1")
                health["schema_verified"] = True
            except Exception:
                health["status"] = "degraded"
        else:
            health["status"] = "unhealthy"

        return health


class AutomationPersistenceReportGenerator(ServiceLifecycle):
    """Outputs status, diagnostics, and metrics summaries for M4."""

    def __init__(
        self, workspace_root: str, health_monitor: AutomationPersistenceHealthMonitor
    ) -> None:
        self.workspace_root = workspace_root
        self.health_monitor = health_monitor

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def generate_health_report(self) -> str:
        health = self.health_monitor.check_health()
        stats = self.health_monitor.stats.compile_statistics()
        report = (
            f"# Automation Persistence Health & Diagnostic Report\n\n"
            f"**Overall Status**: {health['status'].upper()}\n"
            f"**Database Connected**: {health['db_connected']}\n"
            f"**Schema Level Verified**: {health['schema_verified']}\n"
            f"**Query Telemetry average latency**: {health['telemetry_avg_latency_ms']:.2f}ms\n"
            f"**Failures Tallied**: {health['failures']}\n\n"
            f"## Repository Utilization\n"
            f"- Workflows: {stats['workflow_count']}\n"
            f"- Executions: {stats['execution_count']}\n"
            f"- Translations: {stats['translation_count']}\n"
            f"- Monitoring Records: {stats['monitoring_count']}\n"
            f"- Optimization Records: {stats['optimization_count']}\n"
            f"- Version Logs: {stats['version_count']}\n"
        )
        return report


class AutomationPersistenceServiceImpl(AutomationPersistenceService):
    """Implementation of AutomationPersistenceService coordinator."""

    def __init__(
        self,
        service: PersistenceService,
        workflow_repo: WorkflowRepository,
        execution_repo: WorkflowExecutionRepository,
        monitor_repo: WorkflowMonitoringRepository,
        optimization_repo: WorkflowOptimizationRepository,
        version_repo: WorkflowVersionRepository,
        translation_repo: WorkflowTranslationRepository,
        integration_repo: WorkflowIntegrationRepository,
        telemetry_repo: AutomationTelemetryRepository,
        stats_repo: AutomationStatisticsRepository,
        validator: AutomationPersistenceValidator,
        telemetry: AutomationPersistenceTelemetry,
        stats_compiler: AutomationPersistenceStatistics,
        health_monitor: AutomationPersistenceHealthMonitor,
        report_generator: AutomationPersistenceReportGenerator,
    ) -> None:
        self.service = service
        self.workflow_repo = workflow_repo
        self.execution_repo = execution_repo
        self.monitor_repo = monitor_repo
        self.optimization_repo = optimization_repo
        self.version_repo = version_repo
        self.translation_repo = translation_repo
        self.integration_repo = integration_repo
        self.telemetry_repo = telemetry_repo
        self.stats_repo = stats_repo
        self.validator = validator
        self.telemetry = telemetry
        self.stats_compiler = stats_compiler
        self.health_monitor = health_monitor
        self.report_generator = report_generator

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def _get_repo(self, category: str) -> Optional[Any]:
        repos = {
            "workflows": self.workflow_repo,
            "executions": self.execution_repo,
            "monitoring": self.monitor_repo,
            "optimizations": self.optimization_repo,
            "versions": self.version_repo,
            "translations": self.translation_repo,
            "integrations": self.integration_repo,
            "telemetry": self.telemetry_repo,
            "statistics": self.stats_repo,
        }
        return repos.get(category)

    def Record(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult:
        return self.record(category, entity_id, data)

    def record(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult:
        start_time = time.time()
        repo = self._get_repo(category)
        if not repo:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'"
            )

        errors = []
        if category == "workflows":
            errors = self.validator.validate_workflow(data)
        elif category == "executions":
            errors = self.validator.validate_execution(data)
        elif category == "monitoring":
            errors = self.validator.validate_monitor(data)
        elif category == "optimizations":
            errors = self.validator.validate_optimization(data)
        elif category == "versions":
            errors = self.validator.validate_version(data)
        elif category == "translations":
            errors = self.validator.validate_translation(data)
        elif category == "integrations":
            errors = self.validator.validate_integration(data)
        elif category == "telemetry":
            errors = self.validator.validate_telemetry(data)
        elif category == "statistics":
            errors = self.validator.validate_statistics(data)

        if errors:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(
                status=PersistenceStatus.VALIDATION_FAILED,
                message=f"Validation failed: {errors}",
                repository=category,
            )

        data["id"] = entity_id
        res = repo.save(data)
        latency = (time.time() - start_time) * 1000
        self.telemetry.record_query(latency, res.status == PersistenceStatus.SUCCESS)
        return res

    def Update(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult:
        return self.update(category, entity_id, data)

    def update(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult:
        return self.record(category, entity_id, data)

    def Archive(self, category: str, entity_id: str) -> PersistenceResult:
        return self.archive(category, entity_id)

    def archive(self, category: str, entity_id: str) -> PersistenceResult:
        start_time = time.time()
        repo = self._get_repo(category)
        if not repo:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'"
            )
        res = repo.get(entity_id)
        if res.status != PersistenceStatus.SUCCESS or not res.payload:
            self.telemetry.record_query(0.0, False)
            return res
        data = dict(res.payload)
        if "status" in data:
            data["status"] = "archived"
        elif "metadata" in data:
            if isinstance(data["metadata"], dict):
                data["metadata"]["archived"] = True
        else:
            data["archived"] = True
        res2 = repo.save(data)
        latency = (time.time() - start_time) * 1000
        self.telemetry.record_query(latency, res2.status == PersistenceStatus.SUCCESS)
        return res2

    def Restore(self, category: str, entity_id: str) -> PersistenceResult:
        return self.restore(category, entity_id)

    def restore(self, category: str, entity_id: str) -> PersistenceResult:
        start_time = time.time()
        repo = self._get_repo(category)
        if not repo:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'"
            )
        res = repo.get(entity_id)
        if res.status != PersistenceStatus.SUCCESS or not res.payload:
            self.telemetry.record_query(0.0, False)
            return res
        data = dict(res.payload)
        if "status" in data:
            data["status"] = "active"
        elif "metadata" in data:
            if isinstance(data["metadata"], dict) and "archived" in data["metadata"]:
                data["metadata"]["archived"] = False
        else:
            data["archived"] = False
        res2 = repo.save(data)
        latency = (time.time() - start_time) * 1000
        self.telemetry.record_query(latency, res2.status == PersistenceStatus.SUCCESS)
        return res2

    def History(self, category: str, entity_id: str) -> PersistenceResult:
        return self.history(category, entity_id)

    def history(self, category: str, entity_id: str) -> PersistenceResult:
        start_time = time.time()
        repo = self._get_repo(category)
        if not repo:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'"
            )
        res = repo.get(entity_id)
        latency = (time.time() - start_time) * 1000
        self.telemetry.record_query(latency, res.status == PersistenceStatus.SUCCESS)
        if res.status != PersistenceStatus.SUCCESS or not res.payload:
            return res
        payload = res.payload
        history_list = [payload]
        return PersistenceResult(
            status=PersistenceStatus.SUCCESS, message="History retrieved.", payload=history_list
        )

    def Statistics(self) -> PersistenceResult:
        return self.statistics()

    def statistics(self) -> PersistenceResult:
        stats = self.stats_compiler.compile_statistics()
        return PersistenceResult(
            status=PersistenceStatus.SUCCESS, message="Statistics compiled.", payload=stats
        )

    def SearchMetadata(self, category: str, query_params: Dict[str, Any]) -> PersistenceResult:
        return self.search_metadata(category, query_params)

    def search_metadata(self, category: str, query_params: Dict[str, Any]) -> PersistenceResult:
        repo = self._get_repo(category)
        if not repo:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'"
            )

        table_map = {
            "workflows": "automation_workflows",
            "executions": "workflow_executions",
            "monitoring": "workflow_monitoring",
            "optimizations": "workflow_optimizations",
            "versions": "workflow_versions",
            "translations": "workflow_translations",
            "integrations": "workflow_integrations",
            "telemetry": "workflow_executions",
            "statistics": "automation_statistics",
        }
        table_name = table_map.get(category)
        if not table_name:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'"
            )

        start_time = time.time()
        try:
            where_clauses = []
            params = []
            for k, v in query_params.items():
                where_clauses.append(f"{k} = ?")
                params.append(v)

            q = f"SELECT * FROM {table_name}"
            if where_clauses:
                q += " WHERE " + " AND ".join(where_clauses)

            rows = repo.service.execute(q, tuple(params) if params else None)
            latency = (time.time() - start_time) * 1000

            results = []
            for r in rows:
                row = dict(r)
                for json_field in [
                    "metadata",
                    "triggers",
                    "actions",
                    "conditions",
                    "variables",
                    "policy",
                    "execution_summaries",
                    "health_summaries",
                    "performance_summaries",
                    "alert_summaries",
                    "success_rates",
                    "latency_summaries",
                    "retry_summaries",
                    "optimization_plans",
                    "detected_patterns",
                    "complexity_scores",
                    "recommendation_metadata",
                    "optimization_statistics",
                    "version_metadata",
                    "migration_metadata",
                    "compatibility_metadata",
                    "rollback_metadata",
                    "version_graph_references",
                    "workflow_metadata",
                    "translation_metadata",
                    "translation_statistics",
                    "compilation_summaries",
                    "connection_metadata",
                    "server_metadata",
                    "health_metadata",
                    "capability_discovery",
                    "validation_metadata",
                    "success_ratios",
                    "failure_ratios",
                    "usage_trends",
                ]:
                    if json_field in row:
                        try:
                            row[json_field] = json.loads(row[json_field] or "{}")
                        except Exception:
                            pass
                results.append(row)

            self.telemetry.record_query(latency, True)
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Search executed successfully.",
                provider=repo.service.config.provider_name,
                latency=latency,
                repository=table_name,
                payload=results,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.telemetry.record_query(latency, False)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository=table_name,
            )
            return result


class AIProviderRepositoryImpl(AIProviderRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, provider: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("ai_providers", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            q = "INSERT OR REPLACE INTO ai_providers (id, name, version, priority, status, context_window, cost_per_million_input, cost_per_million_output, auth_type, supported_models, is_local, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            params = (
                provider["id"],
                provider.get("name"),
                provider.get("version"),
                provider.get("priority"),
                provider.get("status"),
                provider.get("context_window"),
                provider.get("cost_per_million_input"),
                provider.get("cost_per_million_output"),
                provider.get("auth_type"),
                json.dumps(provider.get("supported_models", [])),
                1 if provider.get("is_local") else 0,
                provider.get("created_at") or time.time(),
                provider.get("updated_at") or time.time(),
            )
            self.service.execute(q, params)
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="AI Provider saved.",
                provider=self.service.config.provider_name,
                latency=(time.time() - start_time) * 1000,
                repository="ai_providers",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="ai_providers",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, provider_id: str) -> PersistenceResult:
        status_res = self.service.check_status("ai_providers", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            q = "SELECT * FROM ai_providers WHERE id = ?"
            rows = self.service.execute(q, (provider_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=f"Provider '{provider_id}' not found.",
                    latency=latency,
                    repository="ai_providers",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result
            row = dict(rows[0])
            row["supported_models"] = json.loads(row["supported_models"] or "[]")
            row["is_local"] = bool(row["is_local"])
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Provider retrieved.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="ai_providers",
                payload=row,
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="ai_providers",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, provider_id: str) -> PersistenceResult:
        status_res = self.service.check_status("ai_providers", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            self.service.execute("DELETE FROM ai_providers WHERE id = ?", (provider_id,))
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Provider deleted.",
                provider=self.service.config.provider_name,
                latency=(time.time() - start_time) * 1000,
                repository="ai_providers",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="ai_providers",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ProviderCapabilityRepositoryImpl(ProviderCapabilityRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, capabilities: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("provider_capabilities", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            q = "INSERT OR REPLACE INTO provider_capabilities (id, provider_name, capabilities, timestamp) VALUES (?, ?, ?, ?)"
            params = (
                capabilities["id"],
                capabilities.get("provider_name"),
                json.dumps(capabilities.get("capabilities", {})),
                capabilities.get("timestamp") or time.time(),
            )
            self.service.execute(q, params)
            latency = (time.time() - start_time) * 1000

            # Cache integration
            from aios.registry import ServiceRegistry

            try:
                cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
                policy_mgr = ServiceRegistry._global_registry.get(CachePolicyManager)
            except Exception:
                cache_svc = None
                policy_mgr = None

            if cache_svc and policy_mgr:
                policy = policy_mgr.get_policy("provider_capabilities")
                if policy == CachePolicy.WRITE_THROUGH:
                    row = {**capabilities}
                    row["capabilities"] = capabilities.get("capabilities", {})
                    row["timestamp"] = capabilities.get("timestamp") or time.time()
                    res = PersistenceResult(
                        status=PersistenceStatus.SUCCESS,
                        message="Capabilities retrieved.",
                        provider=self.service.config.provider_name,
                        latency=latency,
                        repository="provider_capabilities",
                        payload=row,
                    )
                    cache_svc.set("provider_capabilities", capabilities["id"], res)
                elif policy != CachePolicy.NO_CACHE:
                    cache_svc.delete("provider_capabilities", capabilities["id"])

            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Capabilities saved.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="provider_capabilities",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_capabilities",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, capability_id: str) -> PersistenceResult:
        status_res = self.service.check_status("provider_capabilities", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        from aios.registry import ServiceRegistry

        try:
            cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
        except Exception:
            cache_svc = None

        def fetch():
            start_time = time.time()
            try:
                rows = self.service.execute(
                    "SELECT * FROM provider_capabilities WHERE id = ?", (capability_id,)
                )
                latency = (time.time() - start_time) * 1000
                if not rows:
                    result = PersistenceResult(
                        status=PersistenceStatus.UNKNOWN_FAILURE,
                        message="Capabilities not found.",
                        latency=latency,
                        repository="provider_capabilities",
                    )
                    if self.service.config.policy == PersistencePolicy.STRICT:
                        raise RuntimeError(result.message)
                    return result
                row = dict(rows[0])
                row["capabilities"] = json.loads(row["capabilities"] or "{}")
                return PersistenceResult(
                    status=PersistenceStatus.SUCCESS,
                    message="Capabilities retrieved.",
                    provider=self.service.config.provider_name,
                    latency=latency,
                    repository="provider_capabilities",
                    payload=row,
                )
            except Exception as e:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=str(e),
                    latency=(time.time() - start_time) * 1000,
                    repository="provider_capabilities",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message) from e
                return result

        if cache_svc:
            return cache_svc.get("provider_capabilities", capability_id, fetch)
        return fetch()

    def delete(self, capability_id: str) -> PersistenceResult:
        status_res = self.service.check_status("provider_capabilities", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            self.service.execute("DELETE FROM provider_capabilities WHERE id = ?", (capability_id,))
            latency = (time.time() - start_time) * 1000

            # Cache integration
            from aios.registry import ServiceRegistry

            try:
                cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
            except Exception:
                cache_svc = None
            if cache_svc:
                cache_svc.delete("provider_capabilities", capability_id)

            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Capabilities deleted.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="provider_capabilities",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_capabilities",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ProviderHealthRepositoryImpl(ProviderHealthRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, health: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("provider_health", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            q = "INSERT OR REPLACE INTO provider_health (id, provider_name, is_healthy, availability_pct, success_rate, rate_limited_until, circuit_breaker_state, cooldown_until, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
            params = (
                health["id"],
                health.get("provider_name"),
                1 if health.get("is_healthy") else 0,
                health.get("availability_pct"),
                health.get("success_rate"),
                health.get("rate_limited_until"),
                health.get("circuit_breaker_state"),
                health.get("cooldown_until"),
                health.get("timestamp") or time.time(),
            )
            self.service.execute(q, params)
            latency = (time.time() - start_time) * 1000

            # Cache integration
            from aios.registry import ServiceRegistry

            try:
                cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
                policy_mgr = ServiceRegistry._global_registry.get(CachePolicyManager)
            except Exception:
                cache_svc = None
                policy_mgr = None

            if cache_svc and policy_mgr:
                policy = policy_mgr.get_policy("provider_health")
                if policy == CachePolicy.WRITE_THROUGH:
                    row = {**health}
                    row["is_healthy"] = bool(health.get("is_healthy"))
                    res = PersistenceResult(
                        status=PersistenceStatus.SUCCESS,
                        message="Health report retrieved.",
                        provider=self.service.config.provider_name,
                        latency=latency,
                        repository="provider_health",
                        payload=row,
                    )
                    cache_svc.set("provider_health", health["id"], res)
                elif policy != CachePolicy.NO_CACHE:
                    cache_svc.delete("provider_health", health["id"])

            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Health status saved.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="provider_health",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_health",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, health_id: str) -> PersistenceResult:
        status_res = self.service.check_status("provider_health", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        from aios.registry import ServiceRegistry

        try:
            cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
        except Exception:
            cache_svc = None

        def fetch():
            start_time = time.time()
            try:
                rows = self.service.execute(
                    "SELECT * FROM provider_health WHERE id = ?", (health_id,)
                )
                latency = (time.time() - start_time) * 1000
                if not rows:
                    result = PersistenceResult(
                        status=PersistenceStatus.UNKNOWN_FAILURE,
                        message="Health report not found.",
                        latency=latency,
                        repository="provider_health",
                    )
                    if self.service.config.policy == PersistencePolicy.STRICT:
                        raise RuntimeError(result.message)
                    return result
                row = dict(rows[0])
                row["is_healthy"] = bool(row["is_healthy"])
                return PersistenceResult(
                    status=PersistenceStatus.SUCCESS,
                    message="Health report retrieved.",
                    provider=self.service.config.provider_name,
                    latency=latency,
                    repository="provider_health",
                    payload=row,
                )
            except Exception as e:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=str(e),
                    latency=(time.time() - start_time) * 1000,
                    repository="provider_health",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message) from e
                return result

        if cache_svc:
            return cache_svc.get("provider_health", health_id, fetch)
        return fetch()

    def delete(self, health_id: str) -> PersistenceResult:
        status_res = self.service.check_status("provider_health", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            self.service.execute("DELETE FROM provider_health WHERE id = ?", (health_id,))
            latency = (time.time() - start_time) * 1000

            # Cache integration
            from aios.registry import ServiceRegistry

            try:
                cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
            except Exception:
                cache_svc = None
            if cache_svc:
                cache_svc.delete("provider_health", health_id)

            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Health report deleted.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="provider_health",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_health",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ProviderTelemetryRepositoryImpl(ProviderTelemetryRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, telemetry: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("provider_telemetry", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            q = "INSERT OR REPLACE INTO provider_telemetry (id, provider_name, average_latency, p95_latency, query_latencies, timestamp) VALUES (?, ?, ?, ?, ?, ?)"
            params = (
                telemetry["id"],
                telemetry.get("provider_name"),
                telemetry.get("average_latency"),
                telemetry.get("p95_latency"),
                json.dumps(telemetry.get("query_latencies", [])),
                telemetry.get("timestamp") or time.time(),
            )
            self.service.execute(q, params)
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Telemetry saved.",
                provider=self.service.config.provider_name,
                latency=(time.time() - start_time) * 1000,
                repository="provider_telemetry",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_telemetry",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, telemetry_id: str) -> PersistenceResult:
        status_res = self.service.check_status("provider_telemetry", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            rows = self.service.execute(
                "SELECT * FROM provider_telemetry WHERE id = ?", (telemetry_id,)
            )
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message="Telemetry report not found.",
                    latency=latency,
                    repository="provider_telemetry",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result
            row = dict(rows[0])
            row["query_latencies"] = json.loads(row["query_latencies"] or "[]")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Telemetry report retrieved.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="provider_telemetry",
                payload=row,
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_telemetry",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, telemetry_id: str) -> PersistenceResult:
        status_res = self.service.check_status("provider_telemetry", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            self.service.execute("DELETE FROM provider_telemetry WHERE id = ?", (telemetry_id,))
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Telemetry deleted.",
                provider=self.service.config.provider_name,
                latency=(time.time() - start_time) * 1000,
                repository="provider_telemetry",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_telemetry",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ProviderStatisticsRepositoryImpl(ProviderStatisticsRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, statistics: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("provider_statistics", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            q = "INSERT OR REPLACE INTO provider_statistics (id, provider_name, total_requests, success_count, failure_count, error_summary, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)"
            params = (
                statistics["id"],
                statistics.get("provider_name"),
                statistics.get("total_requests"),
                statistics.get("success_count"),
                statistics.get("failure_count"),
                statistics.get("error_summary"),
                statistics.get("timestamp") or time.time(),
            )
            self.service.execute(q, params)
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Statistics saved.",
                provider=self.service.config.provider_name,
                latency=(time.time() - start_time) * 1000,
                repository="provider_statistics",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_statistics",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, statistics_id: str) -> PersistenceResult:
        status_res = self.service.check_status("provider_statistics", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            rows = self.service.execute(
                "SELECT * FROM provider_statistics WHERE id = ?", (statistics_id,)
            )
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message="Statistics not found.",
                    latency=latency,
                    repository="provider_statistics",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result
            row = dict(rows[0])
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Statistics retrieved.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="provider_statistics",
                payload=row,
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_statistics",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, statistics_id: str) -> PersistenceResult:
        status_res = self.service.check_status("provider_statistics", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            self.service.execute("DELETE FROM provider_statistics WHERE id = ?", (statistics_id,))
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Statistics deleted.",
                provider=self.service.config.provider_name,
                latency=(time.time() - start_time) * 1000,
                repository="provider_statistics",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_statistics",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ProviderQuotaRepositoryImpl(ProviderQuotaRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, quota: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("provider_quotas", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            q = "INSERT OR REPLACE INTO provider_quotas (id, provider_name, quota_limit, quota_used, remaining_quota, is_exhausted, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)"
            params = (
                quota["id"],
                quota.get("provider_name"),
                quota.get("quota_limit"),
                quota.get("quota_used"),
                quota.get("remaining_quota"),
                1 if quota.get("is_exhausted") else 0,
                quota.get("timestamp") or time.time(),
            )
            self.service.execute(q, params)
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Quota saved.",
                provider=self.service.config.provider_name,
                latency=(time.time() - start_time) * 1000,
                repository="provider_quotas",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_quotas",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, quota_id: str) -> PersistenceResult:
        status_res = self.service.check_status("provider_quotas", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            rows = self.service.execute("SELECT * FROM provider_quotas WHERE id = ?", (quota_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message="Quota not found.",
                    latency=latency,
                    repository="provider_quotas",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result
            row = dict(rows[0])
            row["is_exhausted"] = bool(row["is_exhausted"])
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Quota retrieved.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="provider_quotas",
                payload=row,
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_quotas",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, quota_id: str) -> PersistenceResult:
        status_res = self.service.check_status("provider_quotas", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            self.service.execute("DELETE FROM provider_quotas WHERE id = ?", (quota_id,))
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Quota deleted.",
                provider=self.service.config.provider_name,
                latency=(time.time() - start_time) * 1000,
                repository="provider_quotas",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_quotas",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ProviderRoutingRepositoryImpl(ProviderRoutingRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, routing: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("provider_routing", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            q = "INSERT OR REPLACE INTO provider_routing (id, request_model, selected_provider, selected_model, strategy, routing_candidates, operation_result_ref, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            params = (
                routing["id"],
                routing.get("request_model"),
                routing.get("selected_provider"),
                routing.get("selected_model"),
                routing.get("strategy"),
                json.dumps(routing.get("routing_candidates", [])),
                routing.get("operation_result_ref"),
                routing.get("timestamp") or time.time(),
            )
            self.service.execute(q, params)
            latency = (time.time() - start_time) * 1000

            # Cache integration
            from aios.registry import ServiceRegistry

            try:
                cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
                policy_mgr = ServiceRegistry._global_registry.get(CachePolicyManager)
            except Exception:
                cache_svc = None
                policy_mgr = None

            if cache_svc and policy_mgr:
                policy = policy_mgr.get_policy("provider_routing")
                if policy == CachePolicy.WRITE_THROUGH:
                    row = {**routing}
                    row["routing_candidates"] = routing.get("routing_candidates", [])
                    row["timestamp"] = routing.get("timestamp") or time.time()
                    res = PersistenceResult(
                        status=PersistenceStatus.SUCCESS,
                        message="Routing decision retrieved.",
                        provider=self.service.config.provider_name,
                        latency=latency,
                        repository="provider_routing",
                        payload=row,
                    )
                    cache_svc.set("provider_routing", routing["id"], res)
                elif policy != CachePolicy.NO_CACHE:
                    cache_svc.delete("provider_routing", routing["id"])

            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Routing decision saved.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="provider_routing",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_routing",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, routing_id: str) -> PersistenceResult:
        status_res = self.service.check_status("provider_routing", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        from aios.registry import ServiceRegistry

        try:
            cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
        except Exception:
            cache_svc = None

        def fetch():
            start_time = time.time()
            try:
                rows = self.service.execute(
                    "SELECT * FROM provider_routing WHERE id = ?", (routing_id,)
                )
                latency = (time.time() - start_time) * 1000
                if not rows:
                    result = PersistenceResult(
                        status=PersistenceStatus.UNKNOWN_FAILURE,
                        message="Routing decision not found.",
                        latency=latency,
                        repository="provider_routing",
                    )
                    if self.service.config.policy == PersistencePolicy.STRICT:
                        raise RuntimeError(result.message)
                    return result
                row = dict(rows[0])
                row["routing_candidates"] = json.loads(row["routing_candidates"] or "[]")
                return PersistenceResult(
                    status=PersistenceStatus.SUCCESS,
                    message="Routing decision retrieved.",
                    provider=self.service.config.provider_name,
                    latency=latency,
                    repository="provider_routing",
                    payload=row,
                )
            except Exception as e:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=str(e),
                    latency=(time.time() - start_time) * 1000,
                    repository="provider_routing",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message) from e
                return result

        if cache_svc:
            return cache_svc.get("provider_routing", routing_id, fetch)
        return fetch()

    def delete(self, routing_id: str) -> PersistenceResult:
        status_res = self.service.check_status("provider_routing", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            self.service.execute("DELETE FROM provider_routing WHERE id = ?", (routing_id,))
            latency = (time.time() - start_time) * 1000

            # Cache integration
            from aios.registry import ServiceRegistry

            try:
                cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
            except Exception:
                cache_svc = None
            if cache_svc:
                cache_svc.delete("provider_routing", routing_id)

            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Routing decision deleted.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="provider_routing",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_routing",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ProviderSessionRepositoryImpl(ProviderSessionRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, session: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("provider_sessions", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            q = "INSERT OR REPLACE INTO provider_sessions (id, session_id, workspace_id, project_id, active_provider, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)"
            params = (
                session["id"],
                session.get("session_id"),
                session.get("workspace_id"),
                session.get("project_id"),
                session.get("active_provider"),
                session.get("created_at") or time.time(),
                session.get("updated_at") or time.time(),
            )
            self.service.execute(q, params)
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Session saved.",
                provider=self.service.config.provider_name,
                latency=(time.time() - start_time) * 1000,
                repository="provider_sessions",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_sessions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, session_id: str) -> PersistenceResult:
        status_res = self.service.check_status("provider_sessions", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            rows = self.service.execute(
                "SELECT * FROM provider_sessions WHERE id = ?", (session_id,)
            )
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message="Session not found.",
                    latency=latency,
                    repository="provider_sessions",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result
            row = dict(rows[0])
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Session retrieved.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="provider_sessions",
                payload=row,
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_sessions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, session_id: str) -> PersistenceResult:
        status_res = self.service.check_status("provider_sessions", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            self.service.execute("DELETE FROM provider_sessions WHERE id = ?", (session_id,))
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Session deleted.",
                provider=self.service.config.provider_name,
                latency=(time.time() - start_time) * 1000,
                repository="provider_sessions",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_sessions",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ProviderCheckpointRepositoryImpl(ProviderCheckpointRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, checkpoint: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("provider_checkpoints", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            ctx = checkpoint.get("context")
            ctx_str = json.dumps(ctx) if isinstance(ctx, (dict, list)) else str(ctx)
            q = "INSERT OR REPLACE INTO provider_checkpoints (id, task_id, provider_name, context, retry_count, timestamp) VALUES (?, ?, ?, ?, ?, ?)"
            params = (
                checkpoint["id"],
                checkpoint.get("task_id"),
                checkpoint.get("provider_name"),
                ctx_str,
                checkpoint.get("retry_count"),
                checkpoint.get("timestamp") or time.time(),
            )
            self.service.execute(q, params)
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Checkpoint saved.",
                provider=self.service.config.provider_name,
                latency=(time.time() - start_time) * 1000,
                repository="provider_checkpoints",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_checkpoints",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, checkpoint_id: str) -> PersistenceResult:
        status_res = self.service.check_status("provider_checkpoints", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            rows = self.service.execute(
                "SELECT * FROM provider_checkpoints WHERE id = ?", (checkpoint_id,)
            )
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message="Checkpoint not found.",
                    latency=latency,
                    repository="provider_checkpoints",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result
            row = dict(rows[0])
            try:
                row["context"] = json.loads(row["context"])
            except Exception:
                pass
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Checkpoint retrieved.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="provider_checkpoints",
                payload=row,
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_checkpoints",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, checkpoint_id: str) -> PersistenceResult:
        status_res = self.service.check_status("provider_checkpoints", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            self.service.execute("DELETE FROM provider_checkpoints WHERE id = ?", (checkpoint_id,))
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Checkpoint deleted.",
                provider=self.service.config.provider_name,
                latency=(time.time() - start_time) * 1000,
                repository="provider_checkpoints",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_checkpoints",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ProviderFailoverRepositoryImpl(ProviderFailoverRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def save(self, failover: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("provider_failovers", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            q = "INSERT OR REPLACE INTO provider_failovers (id, failed_provider, target_provider, checkpoint_id, error_message, timestamp) VALUES (?, ?, ?, ?, ?, ?)"
            params = (
                failover["id"],
                failover.get("failed_provider"),
                failover.get("target_provider"),
                failover.get("checkpoint_id"),
                failover.get("error_message"),
                failover.get("timestamp") or time.time(),
            )
            self.service.execute(q, params)
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Failover history logged.",
                provider=self.service.config.provider_name,
                latency=(time.time() - start_time) * 1000,
                repository="provider_failovers",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_failovers",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, failover_id: str) -> PersistenceResult:
        status_res = self.service.check_status("provider_failovers", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            rows = self.service.execute(
                "SELECT * FROM provider_failovers WHERE id = ?", (failover_id,)
            )
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message="Failover log not found.",
                    latency=latency,
                    repository="provider_failovers",
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result
            row = dict(rows[0])
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Failover log retrieved.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="provider_failovers",
                payload=row,
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_failovers",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, failover_id: str) -> PersistenceResult:
        status_res = self.service.check_status("provider_failovers", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            self.service.execute("DELETE FROM provider_failovers WHERE id = ?", (failover_id,))
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Failover log deleted.",
                provider=self.service.config.provider_name,
                latency=(time.time() - start_time) * 1000,
                repository="provider_failovers",
            )
        except Exception as e:
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=(time.time() - start_time) * 1000,
                repository="provider_failovers",
            )
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

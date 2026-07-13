# ruff: noqa: F403, F405, E501, N802, E402, N806, B007
import logging
import os
import time
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle
from aios.services.persistence import *

from .intelligence import RuntimeCorrelationManager, get_unified_ri

logger = logging.getLogger(__name__)


class PersistenceServiceImpl(PersistenceService):
    """Unified service exposing SQL execution and transactional operations."""

    def __init__(
        self,
        config: PersistenceConfigurationService,
        registry: PersistenceRegistry,
        repos: RepositoryRegistry,
    ) -> None:
        self.config = config
        self.registry = registry
        self.repos = repos
        self.active_provider: Optional[PersistenceProvider] = None
        self.ri_service: Optional[Any] = None

    def initialize(self) -> None:
        try:
            provider_cls = self.registry.get_provider_class(self.config.provider_name)
            self.active_provider = provider_cls()
            self.active_provider.initialize(self.config)
        except Exception as e:
            logger.warning(
                f"Failed to initialize database provider {self.config.provider_name.upper()}: {e}. "
                "Attempting fallback to SQLite during initialization..."
            )
            self.fallback_to_sqlite()

    def fallback_to_sqlite(self) -> None:
        try:
            if self.active_provider:
                self.active_provider.disconnect()
        except Exception:
            pass

        logger.warning(
            f"Database provider {self.config.provider_name.upper()} is unavailable. "
            "Falling back to local-only SQLite mode."
        )
        self.config.provider_name = "sqlite"

        # Dynamically register SQLiteProvider
        from .sqlite import SQLiteProvider

        self.registry.register_provider("sqlite", SQLiteProvider)

        provider_cls = self.registry.get_provider_class("sqlite")
        self.active_provider = provider_cls()
        self.active_provider.initialize(self.config)
        try:
            self.active_provider.connect()
            logger.info("Successfully initialized local-only SQLite provider.")
        except Exception as e:
            logger.error(f"Failed to initialize local-only SQLite provider: {e}")

    def start(self) -> None:
        if self.active_provider:
            try:
                self.active_provider.connect()
                # Run a query to verify psycopg2 connection doesn't lazily fail
                self.active_provider.execute("SELECT 1")
                logger.info(
                    f"Database provider {self.config.provider_name.upper()} connected successfully."
                )
            except Exception as e:
                if self.config.policy == PersistencePolicy.STRICT:
                    logger.error(
                        f"Failed to connect to database provider {self.config.provider_name.upper()}: {e}. "
                        "Strict policy blocks fallback."
                    )
                    return
                logger.warning(
                    f"Failed to connect to database provider {self.config.provider_name.upper()}: {e}. "
                    "Attempting automatic fallback to local SQLite..."
                )
                self.fallback_to_sqlite()

    def shutdown(self) -> None:
        if self.active_provider:
            self.active_provider.disconnect()

    def check_status(
        self, repository: Optional[str] = None, operation: Optional[str] = None
    ) -> PersistenceResult:
        # Automatically set correlation context
        RuntimeCorrelationManager.set_context(
            workspace_id=getattr(self.config, "workspace_id", "default_workspace"),
            project_id=getattr(self.config, "project_id", "default_project"),
            repository=repository,
            operation=operation,
        )
        if self.config.policy == PersistencePolicy.READ_ONLY:
            write_ops = {
                "save",
                "delete",
                "update",
                "begin_transaction",
                "commit",
                "rollback",
                "commit_transaction",
                "rollback_transaction",
            }
            if operation in write_ops:
                return PersistenceResult(
                    status=PersistenceStatus.READ_ONLY_MODE,
                    message="Cannot write: READ_ONLY policy is active.",
                    repository=repository,
                )

        if not self.active_provider or not self.active_provider.transport:
            return PersistenceResult(
                status=PersistenceStatus.PERSISTENCE_UNAVAILABLE,
                message="Database transport is not initialized.",
                repository=repository,
            )

        transport = self.active_provider.transport
        if getattr(transport, "awaiting_configuration", False):
            return PersistenceResult(
                status=PersistenceStatus.AWAITING_RUNTIME_CONFIGURATION,
                message="Database execution blocked: Awaiting Runtime Configuration",
                repository=repository,
                diagnostics={
                    "remediation": "Configure environment variables POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DATABASE to establish live database connections."
                },
            )

        health = transport.health()
        if not health.is_alive:
            return PersistenceResult(
                status=PersistenceStatus.PERSISTENCE_UNAVAILABLE,
                message=f"Database is offline: {health.error_message}",
                repository=repository,
                diagnostics={
                    "remediation": "Verify database service state, network routing, and correct port bindings."
                },
            )

        return PersistenceResult(
            status=PersistenceStatus.SUCCESS,
            message="Ready",
            provider=self.config.provider_name,
            repository=repository,
        )

    def get_diagnostics_for_error(self, e: Exception) -> Dict[str, Any]:
        msg = str(e).lower()
        if "permission" in msg or "access denied" in msg:
            return {
                "type": "Permission failure",
                "remediation": "Verify database user credentials and GRANT permissions on the tables.",
            }
        if "timeout" in msg:
            return {
                "type": "Network timeout",
                "remediation": "Check database connectivity, firewalls, and connect_timeout settings.",
            }
        if "relation" in msg or "table" in msg:
            return {
                "type": "Migration mismatch",
                "remediation": "Run database migrations to ensure table schemas match active repository definitions.",
            }
        return {
            "type": "Database error",
            "remediation": "Check database server logs for error details.",
        }

    def execute(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        # For backward compatibility, check policy & connectivity and raise if STRICT
        status_res = self.check_status()
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return []

        if not self.active_provider:
            raise RuntimeError("Persistence Platform not initialized")

        ri = getattr(self, "ri_service", None)
        corr_ctx = RuntimeCorrelationManager.get_context()
        start_time = time.time()
        success = True
        err = None

        try:
            res = self.active_provider.execute(query, params)
            return res
        except Exception as e:
            success = False
            err = str(e)
            raise e
        finally:
            duration_ms = (time.time() - start_time) * 1000.0
            if ri:
                try:
                    ri.telemetry.record_query(duration_ms, success)
                    ri.stats_engine.record_operation(success, self.config.policy.name)
                    ri.query_prof.profile_query(query, duration_ms)
                    if not success:
                        severity = "ERROR"
                        remediation = "Verify query syntax and schema constraint alignments."
                        if "connection" in str(err).lower() or "blocked" in str(err).lower():
                            severity = "CRITICAL"
                            remediation = "Check host availability and firewall rules."
                        ri.diag_engine.log_error(str(err), severity, remediation)
                    if corr_ctx.get("repository"):
                        ri.repo_prof.record_call(
                            corr_ctx["repository"], corr_ctx["operation"] or "execute", duration_ms
                        )
                except Exception:
                    pass

    def begin_transaction(self) -> PersistenceResult:
        start_time = time.time()
        status_res = self.check_status(operation="begin_transaction")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        if self.config.policy == PersistencePolicy.READ_ONLY:
            return PersistenceResult(
                status=PersistenceStatus.READ_ONLY_MODE,
                message="Transactions blocked: Read-only mode is active.",
            )

        ri = getattr(self, "ri_service", None)
        nested = False
        if self.active_provider and self.active_provider.transport:
            nested = getattr(self.active_provider.transport, "tx_depth", 0) > 0

        try:
            if self.active_provider:
                self.active_provider.begin_transaction()
            latency = (time.time() - start_time) * 1000
            if ri:
                try:
                    ri.tx_prof.record_transaction(latency, nested)
                except Exception:
                    pass
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Transaction started successfully.",
                provider=self.config.provider_name,
                latency=latency,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            if ri:
                try:
                    ri.tx_prof.record_transaction(latency, nested)
                except Exception:
                    pass
            result = PersistenceResult(
                status=PersistenceStatus.TRANSACTION_ABORTED,
                message=f"Transaction failure: {e}",
                latency=latency,
            )
            if self.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def commit(self) -> PersistenceResult:
        start_time = time.time()
        status_res = self.check_status(operation="commit")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        ri = getattr(self, "ri_service", None)
        try:
            if self.active_provider:
                self.active_provider.commit_transaction()
            latency = (time.time() - start_time) * 1000
            if ri:
                try:
                    ri.tx_prof.record_transaction(latency, False)
                except Exception:
                    pass
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Transaction committed successfully.",
                provider=self.config.provider_name,
                latency=latency,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            if ri:
                try:
                    ri.tx_prof.record_transaction(latency, False)
                except Exception:
                    pass
            result = PersistenceResult(
                status=PersistenceStatus.TRANSACTION_ABORTED,
                message=f"Transaction commit failure: {e}",
                latency=latency,
            )
            if self.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def rollback(self) -> PersistenceResult:
        start_time = time.time()
        status_res = self.check_status(operation="rollback")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        ri = getattr(self, "ri_service", None)
        try:
            if self.active_provider:
                self.active_provider.rollback_transaction()
            latency = (time.time() - start_time) * 1000
            if ri:
                try:
                    ri.tx_prof.record_transaction(latency, False)
                except Exception:
                    pass
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Transaction rolled back successfully.",
                provider=self.config.provider_name,
                latency=latency,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            if ri:
                try:
                    ri.tx_prof.record_transaction(latency, False)
                except Exception:
                    pass
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=f"Transaction rollback failure: {e}",
                latency=latency,
            )
            if self.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def commit_transaction(self) -> PersistenceResult:
        return self.commit()

    def rollback_transaction(self) -> PersistenceResult:
        return self.rollback()

    def save(self, repo_name: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult:
        try:
            repo = self.repos.get_repository(repo_name)
            data["id"] = entity_id
            return repo.save(data)
        except KeyError:
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=f"Repository '{repo_name}' is not registered",
                repository=repo_name,
            )
        except Exception as e:
            if self.config.policy == PersistencePolicy.STRICT:
                raise
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), repository=repo_name
            )

    def load(self, repo_name: str, entity_id: str) -> PersistenceResult:
        start_time = time.time()
        status_res = self.check_status(repo_name, "load")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res

        try:
            repo = self.repos.get_repository(repo_name)
            payload = repo.get(entity_id)
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Loaded successfully",
                provider=self.config.provider_name,
                latency=latency,
                repository=repo_name,
                payload=payload,
            )
        except KeyError:
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=f"Repository '{repo_name}' is not registered",
                repository=repo_name,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository=repo_name,
            )
            if self.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def update(self, repo_name: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult:
        return self.save(repo_name, entity_id, data)

    def delete(self, repo_name: str, entity_id: str) -> PersistenceResult:
        try:
            repo = self.repos.get_repository(repo_name)
            return repo.delete(entity_id)
        except KeyError:
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=f"Repository '{repo_name}' is not registered",
                repository=repo_name,
            )
        except Exception as e:
            if self.config.policy == PersistencePolicy.STRICT:
                raise
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), repository=repo_name
            )


class PersistenceHealthMonitor(ServiceLifecycle):
    """Tracks latency averages, P95 values, transaction metrics, and pool status."""

    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def check_health(self) -> Dict[str, Any]:
        impl = self.service  # type: ignore
        provider = impl.active_provider

        status = "offline"
        reachable = False
        metrics = {}
        issues = []

        if provider and provider.transport:
            transport = provider.transport
            h = transport.health()
            reachable = h.is_alive
            status = "online" if reachable else "offline"
            metrics = provider.get_metrics()

            if getattr(transport, "awaiting_configuration", False):
                issues.append("Awaiting Runtime Configuration")
            elif not h.is_alive:
                issues.append(f"Connection offline: {h.error_message}")
        else:
            issues.append("No active database transport initialized.")

        return {
            "status": status,
            "server_reachable": reachable,
            "metrics": metrics,
            "issues": issues,
        }


class PersistenceDiagnostics(ServiceLifecycle):
    """Diagnoses persistence platform issues and provides remediations."""

    def __init__(
        self,
        config: PersistenceConfigurationService,
        service: PersistenceService,
    ) -> None:
        self.config = config
        self.service = service

    def run_diagnostics(self) -> Dict[str, Any]:
        impl = self.service  # type: ignore
        provider = impl.active_provider

        status = "ok"
        issues = []

        if provider and provider.transport:
            transport = provider.transport
            if getattr(transport, "awaiting_configuration", False):
                status = "error"
                issues.append(
                    {
                        "type": "Configuration Warning",
                        "message": "Awaiting Runtime Configuration",
                        "remediation": "Configure environment variables POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DATABASE to establish live database connections.",
                    }
                )
            else:
                config_errs = transport.validate_configuration()
                if config_errs:
                    status = "error"
                    for err in config_errs:
                        issues.append(
                            {
                                "type": "Configuration Error",
                                "message": err,
                                "remediation": "Correct configuration settings in PersistenceConfigurationService.",
                            }
                        )

                h = transport.health()
                if not h.is_alive:
                    status = "error"
                    issues.append(
                        {
                            "type": "Connection Failure",
                            "message": h.error_message or "Unable to connect to database.",
                            "remediation": "Verify database service state, network routing, and correct port bindings.",
                        }
                    )
        else:
            status = "error"
            issues.append(
                {
                    "type": "Initialization Error",
                    "message": "No database transport is initialized.",
                    "remediation": "Initialize PersistenceService through composition boot.",
                }
            )

        return {"status": status, "issues": issues, "timestamp": time.time()}


class PersistenceValidator(ServiceLifecycle):
    """Validates configuration parameters."""

    def validate_config(self, host: str, port: int) -> List[str]:
        errors = []
        if not host:
            errors.append("Validation Error: Database host cannot be empty.")
        if port <= 0 or port > 65535:
            errors.append("Validation Error: Database port must be a valid range (1-65535).")
        return errors


class PersistenceReportGenerator(ServiceLifecycle):
    """Generates persistence telemetry reports inside docs/persistence/."""

    def __init__(
        self,
        workspace_root: str,
        health_monitor: PersistenceHealthMonitor,
        diagnostics: PersistenceDiagnostics,
    ) -> None:
        self.workspace_root = workspace_root
        self.health_monitor = health_monitor
        self.diagnostics = diagnostics

    def generate_reports(self) -> None:
        p_dir = os.path.join(self.workspace_root, "docs", "persistence")
        os.makedirs(p_dir, exist_ok=True)

        health_data = self.health_monitor.check_health()
        diag_data = self.diagnostics.run_diagnostics()
        metrics = health_data.get("metrics", {})

        with open(os.path.join(p_dir, "PERSISTENCE_STATUS.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Persistence Subsystem Status\n\n"
                f"- **Active Provider**: {self.diagnostics.config.provider_name.upper()}\n"
                f"- **Status**: {health_data['status'].upper()}\n"
                f"- **Reachable**: {health_data['server_reachable']}\n"
                f"- **Database Target**: {self.diagnostics.config.host}:{self.diagnostics.config.port}\n"
                f"- **Database Name**: {self.diagnostics.config.database}\n"
                f"- **Active Policy**: {self.diagnostics.config.policy.name}\n"
                f"- **Max Pool Size**: {self.diagnostics.config.pool_max_size}\n"
                f"- **Connection Timeout**: {self.diagnostics.config.connection_timeout}s\n"
            )

        with open(os.path.join(p_dir, "PERSISTENCE_HEALTH.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Persistence Health Metrics\n\n"
                f"- **Active Connections**: {metrics.get('active_connections', 0)}\n"
                f"- **Total Connections in Pool**: {metrics.get('total_connections', 0)}\n"
                f"- **Query Success Rate**: {((metrics.get('success_calls', 0) / max(1, metrics.get('success_calls', 0) + metrics.get('failure_calls', 0))) * 100.0):.1f}%\n"
                f"- **Average Query Latency**: {metrics.get('average_latency', 0.0) * 1000.0:.2f} ms\n"
                f"- **P95 Latency Profile**: {metrics.get('p95_latency', 0.0) * 1000.0:.2f} ms\n"
                f"- **Transaction Success Rate**: {metrics.get('transaction_success_rate', 1.0) * 100.0:.1f}%\n"
                f"- **Applied Migrations**: {metrics.get('applied_migrations', 0)}\n"
                f"- **Retry Calls Count**: {metrics.get('retry_calls', 0)}\n"
            )

        with open(os.path.join(p_dir, "PERSISTENCE_DIAGNOSTICS.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Persistence Platform Diagnostics\n\n"
                f"- **Diagnostics Status**: {diag_data['status'].upper()}\n"
                f"- **Active Policy**: {self.diagnostics.config.policy.name}\n\n"
                f"## Logged Diagnostics Issues\n\n"
            )
            if diag_data["issues"]:
                for issue in diag_data["issues"]:
                    f.write(
                        f"### [{issue['type']}] {issue['message']}\n"
                        f"**Remediation**: {issue['remediation']}\n\n"
                    )
            else:
                f.write("All diagnostics validation checks passed. Database operation is stable.\n")


class PersistenceBootstrapper(ServiceLifecycle):
    """Bootstrapper executing database schema migrations."""

    def __init__(self, persistence_service: PersistenceService) -> None:
        self.persistence_service = persistence_service

    def start(self) -> None:
        impl = self.persistence_service  # type: ignore
        provider = impl.active_provider
        if not provider or not provider.migration_manager:
            return

        mgr = provider.migration_manager
        mgr.register_migration(
            1,
            "Create workspaces table",
            "CREATE TABLE IF NOT EXISTS workspaces ("
            "  id TEXT PRIMARY KEY,"
            "  name TEXT,"
            "  metadata TEXT,"
            "  state TEXT,"
            "  created_at REAL,"
            "  last_accessed REAL,"
            "  version TEXT,"
            "  status TEXT,"
            "  health TEXT"
            ")",
        )
        mgr.register_migration(
            2,
            "Create workspace_sessions table",
            "CREATE TABLE IF NOT EXISTS workspace_sessions ("
            "  id TEXT PRIMARY KEY,"
            "  workspace_id TEXT,"
            "  start_time REAL,"
            "  end_time REAL,"
            "  state TEXT,"
            "  current_task TEXT,"
            "  current_branch TEXT,"
            "  current_agent TEXT,"
            "  current_provider TEXT,"
            "  metrics TEXT,"
            "  health TEXT,"
            "  checkpoints TEXT,"
            "  resume_metadata TEXT"
            ")",
        )
        mgr.register_migration(
            3,
            "Create projects table",
            "CREATE TABLE IF NOT EXISTS projects ("
            "  id TEXT PRIMARY KEY,"
            "  workspace_id TEXT,"
            "  name TEXT,"
            "  version TEXT,"
            "  description TEXT"
            ")",
        )
        mgr.register_migration(
            4,
            "Create engineering_profiles table",
            "CREATE TABLE IF NOT EXISTS engineering_profiles ("
            "  id TEXT PRIMARY KEY,"
            "  workspace_id TEXT,"
            "  project_name TEXT,"
            "  project_version TEXT,"
            "  project_description TEXT,"
            "  language TEXT,"
            "  coding_standards TEXT,"
            "  naming_conventions TEXT,"
            "  testing_framework TEXT,"
            "  min_statement_coverage REAL,"
            "  min_branch_coverage REAL,"
            "  max_timeout_seconds INTEGER,"
            "  sandbox_enabled INTEGER,"
            "  documentation_format TEXT,"
            "  generate_api_docs INTEGER,"
            "  release_formatting_rules TEXT,"
            "  markdown_preferences TEXT,"
            "  section_ordering TEXT,"
            "  doc_naming_conventions TEXT,"
            "  doc_versioning_preferences TEXT,"
            "  github_org TEXT,"
            "  github_repo TEXT,"
            "  github_default_branch TEXT,"
            "  auto_release INTEGER,"
            "  versioning_scheme TEXT,"
            "  cron_expression TEXT,"
            "  max_retries INTEGER,"
            "  workspace_root TEXT,"
            "  exclude_patterns TEXT,"
            "  timestamp REAL,"
            "  history TEXT,"
            "  version INTEGER DEFAULT 1"
            ")",
        )
        mgr.register_migration(
            5,
            "Create configuration_profiles table",
            "CREATE TABLE IF NOT EXISTS configuration_profiles ("
            "  id TEXT PRIMARY KEY,"
            "  workspace_id TEXT,"
            "  env_profile TEXT,"
            "  workspace_settings TEXT,"
            "  provider_preferences TEXT,"
            "  git_preferences TEXT,"
            "  automation_preferences TEXT,"
            "  documentation_preferences TEXT,"
            "  testing_preferences TEXT,"
            "  approval_preferences TEXT"
            ")",
        )
        mgr.register_migration(
            6,
            "Create repository_preferences table",
            "CREATE TABLE IF NOT EXISTS repository_preferences ("
            "  id TEXT PRIMARY KEY,"
            "  workspace_id TEXT,"
            "  metadata TEXT,"
            "  branch_preferences TEXT,"
            "  default_mappings TEXT"
            ")",
        )
        mgr.register_migration(
            7,
            "Create provider_preferences table",
            "CREATE TABLE IF NOT EXISTS provider_preferences ("
            "  id TEXT PRIMARY KEY,"
            "  workspace_id TEXT,"
            "  provider_preferences TEXT,"
            "  routing_configuration TEXT"
            ")",
        )
        mgr.register_migration(
            8,
            "Create engineering_tasks table",
            "CREATE TABLE IF NOT EXISTS engineering_tasks ("
            "  id TEXT PRIMARY KEY,"
            "  name TEXT,"
            "  description TEXT,"
            "  priority TEXT,"
            "  status TEXT,"
            "  creation_time REAL,"
            "  update_time REAL,"
            "  completion_time REAL,"
            "  workspace TEXT,"
            "  current_phase TEXT,"
            "  assigned_agent TEXT,"
            "  dependencies TEXT,"
            "  retry_count INTEGER,"
            "  operation_results TEXT"
            ")",
        )
        mgr.register_migration(
            9,
            "Create planning_sessions table",
            "CREATE TABLE IF NOT EXISTS planning_sessions ("
            "  id TEXT PRIMARY KEY,"
            "  execution_plan TEXT,"
            "  decision_tree TEXT,"
            "  architecture_decisions TEXT,"
            "  dependency_graph TEXT,"
            "  planning_statistics TEXT,"
            "  planning_version INTEGER,"
            "  timestamp REAL"
            ")",
        )
        mgr.register_migration(
            10,
            "Create approval_sessions table",
            "CREATE TABLE IF NOT EXISTS approval_sessions ("
            "  id TEXT PRIMARY KEY,"
            "  workspace_id TEXT,"
            "  metadata TEXT,"
            "  decision_outcome TEXT,"
            "  confidence REAL,"
            "  policy_used TEXT,"
            "  review_status TEXT,"
            "  approver TEXT,"
            "  timeline_metadata TEXT,"
            "  operation_results TEXT,"
            "  created_at REAL,"
            "  closed_at REAL"
            ")",
        )
        mgr.register_migration(
            11,
            "Create review_sessions table",
            "CREATE TABLE IF NOT EXISTS review_sessions ("
            "  id TEXT PRIMARY KEY,"
            "  session_id TEXT,"
            "  workspace_id TEXT,"
            "  state_transitions TEXT,"
            "  metadata TEXT"
            ")",
        )
        mgr.register_migration(
            12,
            "Create documentation_metadata table",
            "CREATE TABLE IF NOT EXISTS documentation_metadata ("
            "  id TEXT PRIMARY KEY,"
            "  workspace_id TEXT,"
            "  session_id TEXT,"
            "  category TEXT,"
            "  status TEXT,"
            "  generation_time REAL,"
            "  author TEXT,"
            "  publication_status TEXT,"
            "  knowledge_references TEXT,"
            "  checksums TEXT,"
            "  version INTEGER"
            ")",
        )
        mgr.register_migration(
            13,
            "Create test_sessions table",
            "CREATE TABLE IF NOT EXISTS test_sessions ("
            "  id TEXT PRIMARY KEY,"
            "  workspace_id TEXT,"
            "  status TEXT,"
            "  pass_count INTEGER,"
            "  fail_count INTEGER,"
            "  coverage_summary TEXT,"
            "  execution_time REAL,"
            "  failure_categories TEXT,"
            "  environment_metadata TEXT,"
            "  operation_results TEXT,"
            "  timestamp REAL"
            ")",
        )
        mgr.register_migration(
            14,
            "Create test_results table",
            "CREATE TABLE IF NOT EXISTS test_results ("
            "  id TEXT PRIMARY KEY,"
            "  session_id TEXT,"
            "  suite_id TEXT,"
            "  name TEXT,"
            "  category TEXT,"
            "  passed INTEGER,"
            "  execution_time REAL,"
            "  error_message TEXT,"
            "  metadata TEXT"
            ")",
        )
        mgr.register_migration(
            15,
            "Create engineering_statistics table",
            "CREATE TABLE IF NOT EXISTS engineering_statistics ("
            "  id TEXT PRIMARY KEY,"
            "  task_count INTEGER,"
            "  planning_count INTEGER,"
            "  approval_count INTEGER,"
            "  documentation_count INTEGER,"
            "  test_count INTEGER,"
            "  repository_utilization TEXT,"
            "  average_query_time REAL,"
            "  p95_query_time REAL,"
            "  repository_failures INTEGER,"
            "  policy_usage TEXT,"
            "  timestamp REAL"
            ")",
        )
        mgr.register_migration(
            16,
            "Create automation_workflows table",
            "CREATE TABLE IF NOT EXISTS automation_workflows ("
            "  id TEXT PRIMARY KEY,"
            "  name TEXT,"
            "  description TEXT,"
            "  metadata TEXT,"
            "  triggers TEXT,"
            "  actions TEXT,"
            "  conditions TEXT,"
            "  variables TEXT,"
            "  policy TEXT,"
            "  created_at REAL,"
            "  updated_at REAL"
            ")",
        )
        mgr.register_migration(
            17,
            "Create workflow_executions table",
            "CREATE TABLE IF NOT EXISTS workflow_executions ("
            "  id TEXT PRIMARY KEY,"
            "  workflow_id TEXT,"
            "  workspace_id TEXT,"
            "  status TEXT,"
            "  success INTEGER,"
            "  error_summary TEXT,"
            "  execution_time REAL,"
            "  created_at REAL,"
            "  closed_at REAL,"
            "  metadata TEXT"
            ")",
        )
        mgr.register_migration(
            18,
            "Create workflow_monitoring table",
            "CREATE TABLE IF NOT EXISTS workflow_monitoring ("
            "  id TEXT PRIMARY KEY,"
            "  workflow_id TEXT,"
            "  execution_summaries TEXT,"
            "  health_summaries TEXT,"
            "  performance_summaries TEXT,"
            "  alert_summaries TEXT,"
            "  success_rates TEXT,"
            "  latency_summaries TEXT,"
            "  retry_summaries TEXT,"
            "  timestamp REAL"
            ")",
        )
        mgr.register_migration(
            19,
            "Create workflow_optimizations table",
            "CREATE TABLE IF NOT EXISTS workflow_optimizations ("
            "  id TEXT PRIMARY KEY,"
            "  workflow_id TEXT,"
            "  optimization_plans TEXT,"
            "  detected_patterns TEXT,"
            "  complexity_scores TEXT,"
            "  recommendation_metadata TEXT,"
            "  optimization_statistics TEXT,"
            "  timestamp REAL"
            ")",
        )
        mgr.register_migration(
            20,
            "Create workflow_versions table",
            "CREATE TABLE IF NOT EXISTS workflow_versions ("
            "  id TEXT PRIMARY KEY,"
            "  workflow_id TEXT,"
            "  version_metadata TEXT,"
            "  migration_metadata TEXT,"
            "  compatibility_metadata TEXT,"
            "  rollback_metadata TEXT,"
            "  version_graph_references TEXT,"
            "  timestamp REAL"
            ")",
        )
        mgr.register_migration(
            21,
            "Create workflow_translations table",
            "CREATE TABLE IF NOT EXISTS workflow_translations ("
            "  id TEXT PRIMARY KEY,"
            "  workflow_id TEXT,"
            "  workflow_metadata TEXT,"
            "  translation_metadata TEXT,"
            "  ir_version TEXT,"
            "  translation_statistics TEXT,"
            "  compilation_summaries TEXT,"
            "  timestamp REAL"
            ")",
        )
        mgr.register_migration(
            22,
            "Create workflow_integrations table",
            "CREATE TABLE IF NOT EXISTS workflow_integrations ("
            "  id TEXT PRIMARY KEY,"
            "  workflow_id TEXT,"
            "  execution_id TEXT,"
            "  connection_metadata TEXT,"
            "  server_metadata TEXT,"
            "  health_metadata TEXT,"
            "  capability_discovery TEXT,"
            "  validation_metadata TEXT,"
            "  timestamp REAL"
            ")",
        )
        mgr.register_migration(
            23,
            "Create automation_statistics table",
            "CREATE TABLE IF NOT EXISTS automation_statistics ("
            "  id TEXT PRIMARY KEY,"
            "  workflow_count INTEGER,"
            "  execution_count INTEGER,"
            "  translation_count INTEGER,"
            "  optimization_count INTEGER,"
            "  monitoring_count INTEGER,"
            "  version_count INTEGER,"
            "  success_ratios TEXT,"
            "  failure_ratios TEXT,"
            "  usage_trends TEXT,"
            "  timestamp REAL"
            ")",
        )
        mgr.register_migration(
            24,
            "Create ai_providers table",
            "CREATE TABLE IF NOT EXISTS ai_providers ("
            "  id TEXT PRIMARY KEY,"
            "  name TEXT,"
            "  version TEXT,"
            "  priority INTEGER,"
            "  status TEXT,"
            "  context_window INTEGER,"
            "  cost_per_million_input REAL,"
            "  cost_per_million_output REAL,"
            "  auth_type TEXT,"
            "  supported_models TEXT,"
            "  is_local INTEGER,"
            "  created_at REAL,"
            "  updated_at REAL"
            ")",
        )
        mgr.register_migration(
            25,
            "Create provider_capabilities table",
            "CREATE TABLE IF NOT EXISTS provider_capabilities ("
            "  id TEXT PRIMARY KEY,"
            "  provider_name TEXT,"
            "  capabilities TEXT,"
            "  timestamp REAL"
            ")",
        )
        mgr.register_migration(
            26,
            "Create provider_health table",
            "CREATE TABLE IF NOT EXISTS provider_health ("
            "  id TEXT PRIMARY KEY,"
            "  provider_name TEXT,"
            "  is_healthy INTEGER,"
            "  availability_pct REAL,"
            "  success_rate REAL,"
            "  rate_limited_until REAL,"
            "  circuit_breaker_state TEXT,"
            "  cooldown_until REAL,"
            "  timestamp REAL"
            ")",
        )
        mgr.register_migration(
            27,
            "Create provider_telemetry table",
            "CREATE TABLE IF NOT EXISTS provider_telemetry ("
            "  id TEXT PRIMARY KEY,"
            "  provider_name TEXT,"
            "  average_latency REAL,"
            "  p95_latency REAL,"
            "  query_latencies TEXT,"
            "  timestamp REAL"
            ")",
        )
        mgr.register_migration(
            28,
            "Create provider_statistics table",
            "CREATE TABLE IF NOT EXISTS provider_statistics ("
            "  id TEXT PRIMARY KEY,"
            "  provider_name TEXT,"
            "  total_requests INTEGER,"
            "  success_count INTEGER,"
            "  failure_count INTEGER,"
            "  error_summary TEXT,"
            "  timestamp REAL"
            ")",
        )
        mgr.register_migration(
            29,
            "Create provider_quotas table",
            "CREATE TABLE IF NOT EXISTS provider_quotas ("
            "  id TEXT PRIMARY KEY,"
            "  provider_name TEXT,"
            "  quota_limit REAL,"
            "  quota_used REAL,"
            "  remaining_quota REAL,"
            "  is_exhausted INTEGER,"
            "  timestamp REAL"
            ")",
        )
        mgr.register_migration(
            30,
            "Create provider_routing table",
            "CREATE TABLE IF NOT EXISTS provider_routing ("
            "  id TEXT PRIMARY KEY,"
            "  request_model TEXT,"
            "  selected_provider TEXT,"
            "  selected_model TEXT,"
            "  strategy TEXT,"
            "  routing_candidates TEXT,"
            "  operation_result_ref TEXT,"
            "  timestamp REAL"
            ")",
        )
        mgr.register_migration(
            31,
            "Create provider_sessions table",
            "CREATE TABLE IF NOT EXISTS provider_sessions ("
            "  id TEXT PRIMARY KEY,"
            "  session_id TEXT,"
            "  workspace_id TEXT,"
            "  project_id TEXT,"
            "  active_provider TEXT,"
            "  created_at REAL,"
            "  updated_at REAL"
            ")",
        )
        mgr.register_migration(
            32,
            "Create provider_checkpoints table",
            "CREATE TABLE IF NOT EXISTS provider_checkpoints ("
            "  id TEXT PRIMARY KEY,"
            "  task_id TEXT,"
            "  provider_name TEXT,"
            "  context TEXT,"
            "  retry_count INTEGER,"
            "  timestamp REAL"
            ")",
        )
        mgr.register_migration(
            33,
            "Create provider_failovers table",
            "CREATE TABLE IF NOT EXISTS provider_failovers ("
            "  id TEXT PRIMARY KEY,"
            "  failed_provider TEXT,"
            "  target_provider TEXT,"
            "  checkpoint_id TEXT,"
            "  error_message TEXT,"
            "  timestamp REAL"
            ")",
        )
        mgr.register_migration(
            34,
            "Create ai_usage_statistics table",
            "CREATE TABLE IF NOT EXISTS ai_usage_statistics ("
            "  id TEXT PRIMARY KEY,"
            "  provider_name TEXT,"
            "  daily_input_tokens INTEGER,"
            "  daily_output_tokens INTEGER,"
            "  monthly_input_tokens INTEGER,"
            "  monthly_output_tokens INTEGER,"
            "  total_cost REAL,"
            "  timestamp REAL"
            ")",
        )
        mgr.register_migration(
            35,
            "Create ai_memory table",
            "CREATE TABLE IF NOT EXISTS ai_memory ("
            "  id TEXT PRIMARY KEY,"
            "  key TEXT,"
            "  value TEXT,"
            "  metadata TEXT,"
            "  created_at REAL,"
            "  updated_at REAL"
            ")",
        )
        mgr.register_migration(
            36,
            "Create pending_embedding_jobs table",
            "CREATE TABLE IF NOT EXISTS pending_embedding_jobs ("
            "  id TEXT PRIMARY KEY,"
            "  text TEXT,"
            "  provider_name TEXT,"
            "  collection_name TEXT,"
            "  status TEXT,"
            "  attempts INTEGER,"
            "  last_error TEXT,"
            "  created_at REAL"
            ")",
        )
        mgr.register_migration(
            37,
            "Create pending_indexing_jobs table",
            "CREATE TABLE IF NOT EXISTS pending_indexing_jobs ("
            "  id TEXT PRIMARY KEY,"
            "  collection_name TEXT,"
            "  vector TEXT,"
            "  payload TEXT,"
            "  status TEXT,"
            "  attempts INTEGER,"
            "  last_error TEXT,"
            "  created_at REAL"
            ")",
        )
        mgr.register_migration(
            38,
            "Enhance pending_indexing_jobs with full audit columns",
            "ALTER TABLE pending_indexing_jobs ADD COLUMN IF NOT EXISTS entity_id TEXT;"
            "ALTER TABLE pending_indexing_jobs ADD COLUMN IF NOT EXISTS workspace_id TEXT;"
            "ALTER TABLE pending_indexing_jobs ADD COLUMN IF NOT EXISTS project_id TEXT;"
            "ALTER TABLE pending_indexing_jobs ADD COLUMN IF NOT EXISTS embedding_version TEXT;"
            "ALTER TABLE pending_indexing_jobs ADD COLUMN IF NOT EXISTS retry_count INTEGER DEFAULT 0;"
            "ALTER TABLE pending_indexing_jobs ADD COLUMN IF NOT EXISTS failure_reason TEXT;"
            "ALTER TABLE pending_indexing_jobs ADD COLUMN IF NOT EXISTS updated_at REAL;",
        )
        mgr.register_migration(
            39,
            "Enhance pending_embedding_jobs with updated_at",
            "ALTER TABLE pending_embedding_jobs ADD COLUMN IF NOT EXISTS updated_at REAL;",
        )

        start_boot = time.time()
        try:
            mgr.execute_migrations()
            ri = get_unified_ri()
            if ri:
                try:
                    applied = len(mgr.get_applied_versions())
                    ri.lifecycle.record_migrations(applied)
                except Exception:
                    pass
        except Exception as e:
            logger.error(f"Failed to bootstrap database schemas: {e}")
        finally:
            ri = get_unified_ri()
            if ri:
                try:
                    ri.lifecycle.record_boot(time.time() - start_boot)
                except Exception:
                    pass

import os
import time
import logging
import json
from typing import Any, Dict, List, Optional, Type

from aios.services.base import ServiceLifecycle
from aios.services.persistence import (
    PersistenceConfigurationService,
    PersistenceProvider,
    PersistenceRegistry,
    RepositoryRegistry,
    PersistenceService,
    DatabaseTransport,
    TransportTransaction,
    TransportResult,
    TransportCapabilities,
    TransportHealth,
    TransportFactory,
    WorkspaceRepository,
    WorkspaceSessionRepository,
    ProjectRepository,
    EngineeringProfileRepository,
    ConfigurationRepository,
    WorkspacePersistenceService,
    PersistencePolicy,
    PersistenceStatus,
    PersistenceResult,
    EngineeringTaskRepository,
    PlanningRepository,
    ApprovalRepository,
    ReviewRepository,
    DocumentationMetadataRepository,
    TestSessionRepository,
    TestResultRepository,
    EngineeringMemoryService,
    WorkflowRepository,
    WorkflowExecutionRepository,
    WorkflowMonitoringRepository,
    WorkflowOptimizationRepository,
    WorkflowVersionRepository,
    WorkflowTranslationRepository,
    WorkflowIntegrationRepository,
    AutomationTelemetryRepository,
    AutomationStatisticsRepository,
    AutomationPersistenceService,
    AIProviderRepository,
    ProviderCapabilityRepository,
    ProviderHealthRepository,
    ProviderTelemetryRepository,
    ProviderStatisticsRepository,
    ProviderQuotaRepository,
    ProviderRoutingRepository,
    ProviderSessionRepository,
    ProviderCheckpointRepository,
    ProviderFailoverRepository,
    AIUsageStatisticsRepository,
    AIMemoryRepository,
    AIMemoryPersistenceService,
)

logger = logging.getLogger(__name__)


class PostgreSQLTransport(DatabaseTransport):
    """Production runtime database transport utilizing PostgreSQL psycopg2 driver."""
    placeholder = "%s"

    def __init__(self, config: PersistenceConfigurationService) -> None:
        super().__init__(config)
        self.is_connected_state = False
        self.connection = None
        self.awaiting_configuration = len(self.validate_configuration()) > 0

    def validate_configuration(self) -> List[str]:
        errors = []
        if not self.config.host:
            errors.append("POSTGRES_HOST configuration is missing.")
        if not self.config.database:
            errors.append("POSTGRES_DATABASE configuration is missing.")
        if not self.config.user:
            errors.append("POSTGRES_USER configuration is missing.")
        if not self.config.password:
            errors.append("POSTGRES_PASSWORD configuration is missing.")
        return errors

    def connect(self) -> None:
        errors = self.validate_configuration()
        if errors:
            self.awaiting_configuration = True
            logger.info("PostgreSQL configuration incomplete: awaiting runtime configuration.")
            return

        try:
            import psycopg2
        except ImportError:
            logger.error("psycopg2 driver not installed.")
            raise RuntimeError("PostgreSQL database driver psycopg2 is missing.") from None

        try:
            self.connection = psycopg2.connect(
                host=self.config.host,
                port=self.config.port,
                dbname=self.config.database,
                user=self.config.user,
                password=self.config.password,
                sslmode=self.config.sslmode,
                connect_timeout=self.config.connection_timeout
            )
            self.connection.autocommit = True
            self.is_connected_state = True
        except Exception as e:
            self.is_connected_state = False
            logger.error(f"Failed to connect to PostgreSQL database: {e}")
            raise

    def disconnect(self) -> None:
        if self.connection:
            try:
                self.connection.close()
            except Exception:
                pass
            self.connection = None
        self.is_connected_state = False

    def execute(self, query: str, params: Optional[tuple] = None) -> TransportResult:
        if self.awaiting_configuration:
            raise RuntimeError("Database execution blocked: Awaiting Runtime Configuration")
        if not self.is_connected_state or not self.connection:
            raise RuntimeError("PostgreSQL database is not connected")

        cursor = self.connection.cursor()
        try:
            cursor.execute(query, params or ())
            try:
                desc = cursor.description
                if desc:
                    colnames = [d[0] for d in desc]
                    rows = [dict(zip(colnames, row)) for row in cursor.fetchall()]
                else:
                    rows = []
                return TransportResult(rows=rows, rows_affected=cursor.rowcount)
            except Exception:
                return TransportResult(rows=[], rows_affected=cursor.rowcount)
        finally:
            cursor.close()

    def execute_many(self, query: str, params_list: List[tuple]) -> List[TransportResult]:
        if self.awaiting_configuration:
            raise RuntimeError("Database execution blocked: Awaiting Runtime Configuration")
        if not self.is_connected_state or not self.connection:
            raise RuntimeError("PostgreSQL database is not connected")
        results = []
        for params in params_list:
            results.append(self.execute(query, params))
        return results

    def begin_transaction(self) -> TransportTransaction:
        if self.awaiting_configuration:
            raise RuntimeError("Database transaction blocked: Awaiting Runtime Configuration")
        self.execute("BEGIN")

        class PsycopgTransaction(TransportTransaction):
            def __init__(self, transport: PostgreSQLTransport) -> None:
                self.transport = transport
            def commit(self) -> None:
                self.transport.execute("COMMIT")
            def rollback(self) -> None:
                self.transport.execute("ROLLBACK")

        return PsycopgTransaction(self)

    def health(self) -> TransportHealth:
        if self.awaiting_configuration:
            return TransportHealth(is_alive=False, latency_ms=0.0, error_message="Awaiting Runtime Configuration")
        if not self.is_connected_state:
            return TransportHealth(is_alive=False, latency_ms=0.0, error_message="Not connected")
        start = time.time()
        try:
            self.execute("SELECT 1")
            return TransportHealth(is_alive=True, latency_ms=(time.time() - start) * 1000.0)
        except Exception as e:
            return TransportHealth(is_alive=False, latency_ms=0.0, error_message=str(e))

    def capabilities(self) -> TransportCapabilities:
        return TransportCapabilities(support_savepoints=True, support_json=True)


class TransactionStackManager:
    """Manages transactional savepoints stacks on top of raw transport transactions."""

    def __init__(self, transport: DatabaseTransport) -> None:
        self.transport = transport
        self.tx_stack: List[TransportTransaction] = []

    def begin(self) -> None:
        if len(self.tx_stack) == 0:
            tx = self.transport.begin_transaction()
            self.tx_stack.append(tx)
        else:
            savepoint_name = f"sp_{len(self.tx_stack)}"
            self.transport.execute(f"SAVEPOINT {savepoint_name}")

            class SavepointTransaction(TransportTransaction):
                def __init__(self, transport: DatabaseTransport, name: str) -> None:
                    self.transport = transport
                    self.name = name
                def commit(self) -> None:
                    self.transport.execute(f"RELEASE SAVEPOINT {self.name}")
                def rollback(self) -> None:
                    self.transport.execute(f"ROLLBACK TO SAVEPOINT {self.name}")

            self.tx_stack.append(SavepointTransaction(self.transport, savepoint_name))

    def commit(self) -> None:
        if not self.tx_stack:
            raise RuntimeError("No active transaction to commit")
        tx = self.tx_stack.pop()
        tx.commit()

    def rollback(self) -> None:
        if not self.tx_stack:
            raise RuntimeError("No active transaction to rollback")
        tx = self.tx_stack.pop()
        try:
            tx.rollback()
        except Exception:
            pass


class Migration:
    """Migration definition model."""

    def __init__(self, version: int, name: str, up_sql: str) -> None:
        self.version = version
        self.name = name
        self.up_sql = up_sql


class MigrationManager:
    """Discovers, validates, and executes migrations."""

    def __init__(self, provider: PersistenceProvider) -> None:
        self.provider = provider
        self.registered_migrations: List[Migration] = []

    def register_migration(self, version: int, name: str, up_sql: str) -> None:
        self.registered_migrations.append(Migration(version, name, up_sql))
        self.registered_migrations.sort(key=lambda m: m.version)

    def initialize_history_table(self) -> None:
        self.provider.execute(
            "CREATE TABLE IF NOT EXISTS _migrations (version INTEGER PRIMARY KEY, name TEXT, applied_at REAL)"
        )

    def get_applied_versions(self) -> List[int]:
        self.initialize_history_table()
        rows = self.provider.execute("SELECT version FROM _migrations ORDER BY version")
        return [row["version"] for row in rows]

    def get_pending_migrations(self) -> List[Migration]:
        applied = self.get_applied_versions()
        return [m for m in self.registered_migrations if m.version not in applied]

    def validate_migrations(self) -> List[str]:
        errors = []
        versions = [m.version for m in self.registered_migrations]
        if len(versions) != len(set(versions)):
            errors.append("Duplicate migration versions detected.")
        if versions != sorted(versions):
            errors.append("Migrations are not registered in ascending sequential order.")
        return errors

    def execute_migrations(self) -> int:
        errors = self.validate_migrations()
        if errors:
            raise RuntimeError(f"Migration validation failed: {errors}")
        
        self.initialize_history_table()
        pending = self.get_pending_migrations()
        executed_count = 0
        for m in pending:
            self.provider.begin_transaction()
            try:
                for query in m.up_sql.split(";"):
                    q = query.strip()
                    if q:
                        self.provider.execute(q)
                self.provider.execute(
                    "INSERT INTO _migrations (version, name, applied_at) VALUES (?, ?, ?)",
                    (m.version, m.name, time.time())
                )
                self.provider.commit_transaction()
                executed_count += 1
            except Exception as e:
                self.provider.rollback_transaction()
                logger.error(f"Migration version {m.version} ({m.name}) failed: {e}")
                raise RuntimeError(f"Migration failed: {e}") from e
        return executed_count


class PostgreSQLProvider(PersistenceProvider):
    """PostgreSQL database engine provider wrapping a DatabaseTransport."""

    def __init__(self, transport: Optional[DatabaseTransport] = None) -> None:
        self.config: Optional[PersistenceConfigurationService] = None
        self.transport: Optional[DatabaseTransport] = transport
        self.migration_manager: Optional[MigrationManager] = None
        self.tx_manager: Optional[TransactionStackManager] = None

    def initialize(self, config: PersistenceConfigurationService) -> None:
        self.config = config
        if not self.transport:
            factory = TransportFactory()
            factory.register_transport("postgresql", PostgreSQLTransport)
            self.transport = factory.create_transport(self.config.provider_name, self.config)
        self.migration_manager = MigrationManager(self)
        self.tx_manager = TransactionStackManager(self.transport)

    def connect(self) -> None:
        if self.transport:
            self.transport.connect()

    def disconnect(self) -> None:
        if self.transport:
            self.transport.disconnect()

    def execute(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        if not self.transport:
            raise RuntimeError("Database transport not initialized")
        q = format_query(query, self.transport)
        res = self.transport.execute(q, params)
        return res.rows

    def begin_transaction(self) -> None:
        if self.tx_manager:
            self.tx_manager.begin()

    def commit_transaction(self) -> None:
        if self.tx_manager:
            self.tx_manager.commit()

    def rollback_transaction(self) -> None:
        if self.tx_manager:
            self.tx_manager.rollback()

    def is_connected(self) -> bool:
        if not self.transport:
            return False
        return self.transport.health().is_alive

    def get_metrics(self) -> Dict[str, Any]:
        if not self.transport:
            return {}
        h = self.transport.health()
        applied = 0
        if self.migration_manager:
            try:
                applied = len(self.migration_manager.get_applied_versions())
            except Exception:
                pass

        return {
            "active_connections": 1 if h.is_alive else 0,
            "total_connections": 1 if h.is_alive else 0,
            "success_calls": 1 if h.is_alive else 0,
            "failure_calls": 0 if h.is_alive else 1,
            "retry_calls": 0,
            "average_latency": h.latency_ms / 1000.0,
            "p95_latency": h.latency_ms / 1000.0,
            "transaction_success_rate": 1.0,
            "applied_migrations": applied,
            "awaiting_configuration": getattr(self.transport, "awaiting_configuration", False)
        }


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
        provider_cls = self.registry.get_provider_class(self.config.provider_name)
        self.active_provider = provider_cls()
        self.active_provider.initialize(self.config)

    def on_ready(self) -> None:
        if self.active_provider:
            self.active_provider.connect()

    def teardown(self) -> None:
        if self.active_provider:
            self.active_provider.disconnect()

    def check_status(self, repository: Optional[str] = None, operation: Optional[str] = None) -> PersistenceResult:
        # Automatically set correlation context
        RuntimeCorrelationManager.set_context(
            workspace_id=getattr(self.config, "workspace_id", "default_workspace"),
            project_id=getattr(self.config, "project_id", "default_project"),
            repository=repository,
            operation=operation
        )
        if self.config.policy == PersistencePolicy.READ_ONLY:
            write_ops = {"save", "delete", "update", "begin_transaction", "commit", "rollback", "commit_transaction", "rollback_transaction"}
            if operation in write_ops:
                return PersistenceResult(
                    status=PersistenceStatus.READ_ONLY_MODE,
                    message="Cannot write: READ_ONLY policy is active.",
                    repository=repository
                )

        if not self.active_provider or not self.active_provider.transport:
            return PersistenceResult(
                status=PersistenceStatus.PERSISTENCE_UNAVAILABLE,
                message="Database transport is not initialized.",
                repository=repository
            )
        
        transport = self.active_provider.transport
        if getattr(transport, "awaiting_configuration", False):
            return PersistenceResult(
                status=PersistenceStatus.AWAITING_RUNTIME_CONFIGURATION,
                message="Database execution blocked: Awaiting Runtime Configuration",
                repository=repository,
                diagnostics={
                    "remediation": "Configure environment variables POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DATABASE to establish live database connections."
                }
            )
        
        health = transport.health()
        if not health.is_alive:
            return PersistenceResult(
                status=PersistenceStatus.PERSISTENCE_UNAVAILABLE,
                message=f"Database is offline: {health.error_message}",
                repository=repository,
                diagnostics={
                    "remediation": "Verify database service state, network routing, and correct port bindings."
                }
            )
        
        return PersistenceResult(
            status=PersistenceStatus.SUCCESS,
            message="Ready",
            provider=self.config.provider_name,
            repository=repository
        )

    def get_diagnostics_for_error(self, e: Exception) -> Dict[str, Any]:
        msg = str(e).lower()
        if "permission" in msg or "access denied" in msg:
            return {
                "type": "Permission failure",
                "remediation": "Verify database user credentials and GRANT permissions on the tables."
            }
        if "timeout" in msg:
            return {
                "type": "Network timeout",
                "remediation": "Check database connectivity, firewalls, and connect_timeout settings."
            }
        if "relation" in msg or "table" in msg:
            return {
                "type": "Migration mismatch",
                "remediation": "Run database migrations to ensure table schemas match active repository definitions."
            }
        return {
            "type": "Database error",
            "remediation": "Check database server logs for error details."
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
                        ri.repo_prof.record_call(corr_ctx["repository"], corr_ctx["operation"] or "execute", duration_ms)
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
                message="Transactions blocked: Read-only mode is active."
            )

        ri = getattr(self, "ri_service", None)
        nested = False
        if self.active_provider and self.active_provider.transport:
            nested = self.active_provider.transport.tx_depth > 0

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
                latency=latency
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
                latency=latency
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
                latency=latency
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
                latency=latency
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
                latency=latency
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
                latency=latency
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
                repository=repo_name
            )
        except Exception as e:
            if self.config.policy == PersistencePolicy.STRICT:
                raise
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                repository=repo_name
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
                payload=payload
            )
        except KeyError:
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=f"Repository '{repo_name}' is not registered",
                repository=repo_name
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository=repo_name
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
                repository=repo_name
            )
        except Exception as e:
            if self.config.policy == PersistencePolicy.STRICT:
                raise
            return PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                repository=repo_name
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
            "issues": issues
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
                issues.append({
                    "type": "Configuration Warning",
                    "message": "Awaiting Runtime Configuration",
                    "remediation": "Configure environment variables POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DATABASE to establish live database connections."
                })
            else:
                config_errs = transport.validate_configuration()
                if config_errs:
                    status = "error"
                    for err in config_errs:
                        issues.append({
                            "type": "Configuration Error",
                            "message": err,
                            "remediation": "Correct configuration settings in PersistenceConfigurationService."
                        })
                
                h = transport.health()
                if not h.is_alive:
                    status = "error"
                    issues.append({
                        "type": "Connection Failure",
                        "message": h.error_message or "Unable to connect to database.",
                        "remediation": "Verify database service state, network routing, and correct port bindings."
                    })
        else:
            status = "error"
            issues.append({
                "type": "Initialization Error",
                "message": "No database transport is initialized.",
                "remediation": "Initialize PersistenceService through composition boot."
            })

        return {
            "status": status,
            "issues": issues,
            "timestamp": time.time()
        }


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


def format_query(query: str, provider_name: str) -> str:
    """Helper to convert SQL query positional markers to Postgres formats dynamically."""
    if provider_name == "postgresql":
        return query.replace("?", "%s")
    return query


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
                repository="workspaces"
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
                )
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
                repository="workspaces"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="workspaces"
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
                repository="workspaces"
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
                repository="workspaces"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="workspaces"
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
        except Exception as e:
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
                repository="workspace_sessions"
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
                )
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workspace session saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workspace_sessions"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="workspace_sessions"
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
        except Exception as e:
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
                repository="workspace_sessions"
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
                repository="workspace_sessions"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="workspace_sessions"
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
        except Exception as e:
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
                repository="projects"
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
                )
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Project saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="projects"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="projects"
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
        except Exception as e:
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
                repository="projects"
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
                repository="projects"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="projects"
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
                repository="engineering_profiles"
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
                    ver
                )
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
                    prof_copy["release_formatting_rules"] = profile.get("release_formatting_rules", {})
                    prof_copy["markdown_preferences"] = profile.get("markdown_preferences", {})
                    prof_copy["section_ordering"] = profile.get("section_ordering", [])
                    prof_copy["doc_naming_conventions"] = profile.get("doc_naming_conventions", {})
                    prof_copy["doc_versioning_preferences"] = profile.get("doc_versioning_preferences", {})
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
                repository="engineering_profiles"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="engineering_profiles"
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
            row["doc_versioning_preferences"] = json.loads(row["doc_versioning_preferences"] or "{}")
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
                repository="engineering_profiles"
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
                repository="engineering_profiles"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="engineering_profiles"
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
        except Exception as e:
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
                repository="configuration_profiles"
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
                )
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
                    cfg_copy["provider_preferences"] = config_profile.get("provider_preferences", {})
                    cfg_copy["git_preferences"] = config_profile.get("git_preferences", {})
                    cfg_copy["automation_preferences"] = config_profile.get("automation_preferences", {})
                    cfg_copy["documentation_preferences"] = config_profile.get("documentation_preferences", {})
                    cfg_copy["testing_preferences"] = config_profile.get("testing_preferences", {})
                    cfg_copy["approval_preferences"] = config_profile.get("approval_preferences", {})
                    cache_svc.set("configuration", config_profile["id"], cfg_copy)
                elif policy != CachePolicy.NO_CACHE:
                    cache_svc.delete("configuration", config_profile["id"])

            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Configuration profile saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="configuration_profiles"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="configuration_profiles"
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
                repository="configuration_profiles"
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
                repository="configuration_profiles"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="configuration_profiles"
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
            "p95_query_latency_ms": p95
        }


class WorkspacePersistenceStatistics(ServiceLifecycle):
    """Compiles statistics summaries from tables."""

    def __init__(self, workspace_repo: WorkspaceRepository, session_repo: WorkspaceSessionRepository) -> None:
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
        with open(os.path.join(p_dir, "WORKSPACE_PERSISTENCE_STATUS.md"), "w", encoding="utf-8") as f:
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
            f.write(
                f"# Repository Registry\n\n"
                f"Registered Repositories:\n\n"
            )
            for repo_name in getattr(self.registry, "_repositories", {}).keys():
                f.write(f"- `{repo_name}`\n")


class PersistenceBootstrapper(ServiceLifecycle):
    """Bootstrapper executing database schema migrations."""

    def __init__(self, persistence_service: PersistenceService) -> None:
        self.persistence_service = persistence_service

    def on_ready(self) -> None:
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
        )
        mgr.register_migration(
            7,
            "Create provider_preferences table",
            "CREATE TABLE IF NOT EXISTS provider_preferences ("
            "  id TEXT PRIMARY KEY,"
            "  workspace_id TEXT,"
            "  provider_preferences TEXT,"
            "  routing_configuration TEXT"
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
        )
        mgr.register_migration(
            25,
            "Create provider_capabilities table",
            "CREATE TABLE IF NOT EXISTS provider_capabilities ("
            "  id TEXT PRIMARY KEY,"
            "  provider_name TEXT,"
            "  capabilities TEXT,"
            "  timestamp REAL"
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
            ")"
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
                )
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Task saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="engineering_tasks"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="engineering_tasks"
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
                    repository="engineering_tasks"
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
                payload=row
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="engineering_tasks"
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
                repository="engineering_tasks"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="engineering_tasks"
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
                payload=results
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="engineering_tasks"
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
                    plan.get("timestamp", time.time())
                )
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Planning session saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="planning_sessions"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="planning_sessions"
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
                    repository="planning_sessions"
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
                payload=row
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="planning_sessions"
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
                repository="planning_sessions"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="planning_sessions"
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
                    approval.get("closed_at")
                )
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Approval session saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="approval_sessions"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="approval_sessions"
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
                    repository="approval_sessions"
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
                payload=row
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="approval_sessions"
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
                repository="approval_sessions"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="approval_sessions"
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
                    json.dumps(review.get("metadata") or {})
                )
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Review session saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="review_sessions"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="review_sessions"
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
                    repository="review_sessions"
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
                payload=row
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="review_sessions"
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
                repository="review_sessions"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="review_sessions"
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
                    doc.get("version", 1)
                )
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Documentation metadata saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="documentation_metadata"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="documentation_metadata"
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
                    repository="documentation_metadata"
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
                payload=row
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="documentation_metadata"
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
                repository="documentation_metadata"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="documentation_metadata"
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
                    session.get("timestamp", time.time())
                )
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Test session saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="test_sessions"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="test_sessions"
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
                    repository="test_sessions"
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
                payload=row
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="test_sessions"
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
                repository="test_sessions"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="test_sessions"
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
                    json.dumps(result.get("metadata") or {})
                )
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Test result saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="test_results"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="test_results"
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
                    repository="test_results"
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
                payload=row
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="test_results"
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
                repository="test_results"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="test_results"
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
            "repository_failures": 0
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
                "test_sessions": stats["test_count"]
            }
        except Exception:
            stats["repository_failures"] += 1

        return stats


class EngineeringMemoryHealthMonitor(ServiceLifecycle):
    def __init__(self, service: PersistenceService, telemetry: EngineeringMemoryTelemetry, stats_compiler: EngineeringMemoryStatistics) -> None:
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
        health_data = {
            "status": "healthy",
            "server_reachable": False,
            "metrics": {},
            "errors": []
        }
        
        status_res = self.service.check_status()
        health_data["server_reachable"] = (status_res.status == PersistenceStatus.SUCCESS)
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
            "policy": self.service.config.policy.name if self.service.config else "STRICT"
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
        with open(os.path.join(p_dir, "ENGINEERING_MEMORY_STATISTICS.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Engineering Memory Statistics\n\n"
                f"- **Task Count**: {metrics.get('task_count', 0)}\n"
                f"- **Planning Count**: {metrics.get('planning_count', 0)}\n"
                f"- **Approval Count**: {metrics.get('approval_count', 0)}\n"
                f"- **Documentation Count**: {metrics.get('documentation_count', 0)}\n"
                f"- **Test Count**: {metrics.get('test_count', 0)}\n"
            )

        # 4. ENGINEERING_MEMORY_DIAGNOSTICS.md
        with open(os.path.join(p_dir, "ENGINEERING_MEMORY_DIAGNOSTICS.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Engineering Memory Diagnostics\n\n"
            )
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
        report_generator: EngineeringMemoryReportGenerator
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
            "test_results": self.test_result_repo
        }
        return repos.get(category)

    def Record(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult:
        return self.record(category, entity_id, data)

    def record(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult:
        start_time = time.time()
        repo = self._get_repo(category)
        if not repo:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'")

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
                repository=category
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
            return PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'")
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
            return PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'")
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
            return PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'")
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
            status=PersistenceStatus.SUCCESS,
            message="History retrieved.",
            payload=history_list
        )

    def Statistics(self) -> PersistenceResult:
        return self.statistics()

    def statistics(self) -> PersistenceResult:
        stats = self.stats_compiler.compile_statistics()
        return PersistenceResult(
            status=PersistenceStatus.SUCCESS,
            message="Statistics compiled.",
            payload=stats
        )

    def SearchMetadata(self, category: str, query_params: Dict[str, Any]) -> PersistenceResult:
        return self.search_metadata(category, query_params)

    def search_metadata(self, category: str, query_params: Dict[str, Any]) -> PersistenceResult:
        repo = self._get_repo(category)
        if not repo:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'")
        
        table_map = {
            "tasks": "engineering_tasks",
            "planning": "planning_sessions",
            "approvals": "approval_sessions",
            "reviews": "review_sessions",
            "documentation": "documentation_metadata",
            "test_sessions": "test_sessions",
            "test_results": "test_results"
        }
        table_name = table_map.get(category)
        if not table_name:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'")
            
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
                for json_field in ["dependencies", "operation_results", "execution_plan", "decision_tree", "architecture_decisions", "dependency_graph", "planning_statistics", "metadata", "policy_used", "timeline_metadata", "state_transitions", "knowledge_references", "checksums", "coverage_summary", "failure_categories", "environment_metadata"]:
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
                payload=results
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.telemetry.record_query(latency, False)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository=table_name
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
                    workflow.get("updated_at") or time.time()
                )
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow definition saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="automation_workflows"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository="automation_workflows"
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
                    repository="automation_workflows"
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            for json_field in ["metadata", "triggers", "actions", "conditions", "variables", "policy"]:
                row[json_field] = json.loads(row[json_field] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow definition retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="automation_workflows",
                payload=row
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="automation_workflows"
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
                repository="automation_workflows"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="automation_workflows"
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
                    json.dumps(execution.get("metadata") or {})
                )
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow execution saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_executions"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_executions"
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
                    repository="workflow_executions"
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
                payload=row
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_executions"
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
                repository="workflow_executions"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_executions"
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
                    monitor_report.get("timestamp") or time.time()
                )
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow monitoring report saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_monitoring"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_monitoring"
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
                    repository="workflow_monitoring"
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            for json_field in ["execution_summaries", "health_summaries", "performance_summaries", "alert_summaries", "success_rates", "latency_summaries", "retry_summaries"]:
                row[json_field] = json.loads(row[json_field] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow monitoring report retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_monitoring",
                payload=row
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_monitoring"
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
                repository="workflow_monitoring"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_monitoring"
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
                    optimization.get("timestamp") or time.time()
                )
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow optimization recommendations saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_optimizations"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_optimizations"
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
                    repository="workflow_optimizations"
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            for json_field in ["optimization_plans", "detected_patterns", "complexity_scores", "recommendation_metadata", "optimization_statistics"]:
                row[json_field] = json.loads(row[json_field] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow optimization retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_optimizations",
                payload=row
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_optimizations"
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
                repository="workflow_optimizations"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_optimizations"
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
                    version.get("timestamp") or time.time()
                )
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow version details saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_versions"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_versions"
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
                    repository="workflow_versions"
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            for json_field in ["version_metadata", "migration_metadata", "compatibility_metadata", "rollback_metadata", "version_graph_references"]:
                row[json_field] = json.loads(row[json_field] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow version retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_versions",
                payload=row
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_versions"
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
                repository="workflow_versions"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_versions"
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
                    translation.get("timestamp") or time.time()
                )
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow translation saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_translations"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_translations"
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
                    repository="workflow_translations"
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            for json_field in ["workflow_metadata", "translation_metadata", "translation_statistics", "compilation_summaries"]:
                row[json_field] = json.loads(row[json_field] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow translation retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_translations",
                payload=row
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_translations"
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
                repository="workflow_translations"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_translations"
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
                    integration.get("timestamp") or time.time()
                )
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow integration metadata saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_integrations"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_integrations"
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
                    repository="workflow_integrations"
                )
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result

            row = dict(rows[0])
            for json_field in ["connection_metadata", "server_metadata", "health_metadata", "capability_discovery", "validation_metadata"]:
                row[json_field] = json.loads(row[json_field] or "{}")
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Workflow integration retrieved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_integrations",
                payload=row
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_integrations"
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
                repository="workflow_integrations"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_integrations"
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
                    json.dumps(telemetry)
                )
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Telemetry saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="workflow_executions"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_executions"
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
                    repository="workflow_executions"
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
                payload=payload
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_executions"
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
                repository="workflow_executions"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="workflow_executions"
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
                    stats.get("timestamp") or time.time()
                )
            )
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message="Automation statistics saved successfully.",
                provider=self.service.config.provider_name,
                latency=latency,
                repository="automation_statistics"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="automation_statistics"
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
                    repository="automation_statistics"
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
                payload=row
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="automation_statistics"
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
                repository="automation_statistics"
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository="automation_statistics"
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
            "repository_failures": 0
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
                "workflow_versions": stats["version_count"]
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
        stats: AutomationPersistenceStatistics
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
            "failures": self.telemetry.failure_count
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

    def __init__(self, workspace_root: str, health_monitor: AutomationPersistenceHealthMonitor) -> None:
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
        report_generator: AutomationPersistenceReportGenerator
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
            "statistics": self.stats_repo
        }
        return repos.get(category)

    def Record(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult:
        return self.record(category, entity_id, data)

    def record(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult:
        start_time = time.time()
        repo = self._get_repo(category)
        if not repo:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'")

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
                repository=category
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
            return PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'")
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
            return PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'")
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
            return PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'")
        res = repo.get(entity_id)
        latency = (time.time() - start_time) * 1000
        self.telemetry.record_query(latency, res.status == PersistenceStatus.SUCCESS)
        if res.status != PersistenceStatus.SUCCESS or not res.payload:
            return res
        payload = res.payload
        history_list = [payload]
        return PersistenceResult(
            status=PersistenceStatus.SUCCESS,
            message="History retrieved.",
            payload=history_list
        )

    def Statistics(self) -> PersistenceResult:
        return self.statistics()

    def statistics(self) -> PersistenceResult:
        stats = self.stats_compiler.compile_statistics()
        return PersistenceResult(
            status=PersistenceStatus.SUCCESS,
            message="Statistics compiled.",
            payload=stats
        )

    def SearchMetadata(self, category: str, query_params: Dict[str, Any]) -> PersistenceResult:
        return self.search_metadata(category, query_params)

    def search_metadata(self, category: str, query_params: Dict[str, Any]) -> PersistenceResult:
        repo = self._get_repo(category)
        if not repo:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'")

        table_map = {
            "workflows": "automation_workflows",
            "executions": "workflow_executions",
            "monitoring": "workflow_monitoring",
            "optimizations": "workflow_optimizations",
            "versions": "workflow_versions",
            "translations": "workflow_translations",
            "integrations": "workflow_integrations",
            "telemetry": "workflow_executions",
            "statistics": "automation_statistics"
        }
        table_name = table_map.get(category)
        if not table_name:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'")

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
                    "metadata", "triggers", "actions", "conditions", "variables", "policy",
                    "execution_summaries", "health_summaries", "performance_summaries", "alert_summaries",
                    "success_rates", "latency_summaries", "retry_summaries", "optimization_plans",
                    "detected_patterns", "complexity_scores", "recommendation_metadata", "optimization_statistics",
                    "version_metadata", "migration_metadata", "compatibility_metadata", "rollback_metadata",
                    "version_graph_references", "workflow_metadata", "translation_metadata", "translation_statistics",
                    "compilation_summaries", "connection_metadata", "server_metadata", "health_metadata",
                    "capability_discovery", "validation_metadata", "success_ratios", "failure_ratios", "usage_trends"
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
                payload=results
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.telemetry.record_query(latency, False)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository=table_name
            )
            return result


class AIProviderRepositoryImpl(AIProviderRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

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
                provider.get("updated_at") or time.time()
            )
            self.service.execute(q, params)
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="AI Provider saved.", provider=self.service.config.provider_name, latency=(time.time() - start_time)*1000, repository="ai_providers")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="ai_providers")
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
                result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Provider '{provider_id}' not found.", latency=latency, repository="ai_providers")
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result
            row = dict(rows[0])
            row["supported_models"] = json.loads(row["supported_models"] or "[]")
            row["is_local"] = bool(row["is_local"])
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Provider retrieved.", provider=self.service.config.provider_name, latency=latency, repository="ai_providers", payload=row)
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="ai_providers")
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
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Provider deleted.", provider=self.service.config.provider_name, latency=(time.time() - start_time)*1000, repository="ai_providers")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="ai_providers")
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ProviderCapabilityRepositoryImpl(ProviderCapabilityRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

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
                capabilities.get("timestamp") or time.time()
            )
            self.service.execute(q, params)
            latency = (time.time() - start_time)*1000

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
                    res = PersistenceResult(status=PersistenceStatus.SUCCESS, message="Capabilities retrieved.", provider=self.service.config.provider_name, latency=latency, repository="provider_capabilities", payload=row)
                    cache_svc.set("provider_capabilities", capabilities["id"], res)
                elif policy != CachePolicy.NO_CACHE:
                    cache_svc.delete("provider_capabilities", capabilities["id"])

            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Capabilities saved.", provider=self.service.config.provider_name, latency=latency, repository="provider_capabilities")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_capabilities")
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
                rows = self.service.execute("SELECT * FROM provider_capabilities WHERE id = ?", (capability_id,))
                latency = (time.time() - start_time) * 1000
                if not rows:
                    result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message="Capabilities not found.", latency=latency, repository="provider_capabilities")
                    if self.service.config.policy == PersistencePolicy.STRICT:
                        raise RuntimeError(result.message)
                    return result
                row = dict(rows[0])
                row["capabilities"] = json.loads(row["capabilities"] or "{}")
                return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Capabilities retrieved.", provider=self.service.config.provider_name, latency=latency, repository="provider_capabilities", payload=row)
            except Exception as e:
                result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_capabilities")
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
            latency = (time.time() - start_time)*1000

            # Cache integration
            from aios.registry import ServiceRegistry
            try:
                cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
            except Exception:
                cache_svc = None
            if cache_svc:
                cache_svc.delete("provider_capabilities", capability_id)

            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Capabilities deleted.", provider=self.service.config.provider_name, latency=latency, repository="provider_capabilities")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_capabilities")
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ProviderHealthRepositoryImpl(ProviderHealthRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

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
                health.get("timestamp") or time.time()
            )
            self.service.execute(q, params)
            latency = (time.time() - start_time)*1000

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
                    res = PersistenceResult(status=PersistenceStatus.SUCCESS, message="Health report retrieved.", provider=self.service.config.provider_name, latency=latency, repository="provider_health", payload=row)
                    cache_svc.set("provider_health", health["id"], res)
                elif policy != CachePolicy.NO_CACHE:
                    cache_svc.delete("provider_health", health["id"])

            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Health status saved.", provider=self.service.config.provider_name, latency=latency, repository="provider_health")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_health")
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
                rows = self.service.execute("SELECT * FROM provider_health WHERE id = ?", (health_id,))
                latency = (time.time() - start_time) * 1000
                if not rows:
                    result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message="Health report not found.", latency=latency, repository="provider_health")
                    if self.service.config.policy == PersistencePolicy.STRICT:
                        raise RuntimeError(result.message)
                    return result
                row = dict(rows[0])
                row["is_healthy"] = bool(row["is_healthy"])
                return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Health report retrieved.", provider=self.service.config.provider_name, latency=latency, repository="provider_health", payload=row)
            except Exception as e:
                result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_health")
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
            latency = (time.time() - start_time)*1000

            # Cache integration
            from aios.registry import ServiceRegistry
            try:
                cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
            except Exception:
                cache_svc = None
            if cache_svc:
                cache_svc.delete("provider_health", health_id)

            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Health report deleted.", provider=self.service.config.provider_name, latency=latency, repository="provider_health")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_health")
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ProviderTelemetryRepositoryImpl(ProviderTelemetryRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

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
                telemetry.get("timestamp") or time.time()
            )
            self.service.execute(q, params)
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Telemetry saved.", provider=self.service.config.provider_name, latency=(time.time() - start_time)*1000, repository="provider_telemetry")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_telemetry")
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
            rows = self.service.execute("SELECT * FROM provider_telemetry WHERE id = ?", (telemetry_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message="Telemetry report not found.", latency=latency, repository="provider_telemetry")
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result
            row = dict(rows[0])
            row["query_latencies"] = json.loads(row["query_latencies"] or "[]")
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Telemetry report retrieved.", provider=self.service.config.provider_name, latency=latency, repository="provider_telemetry", payload=row)
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_telemetry")
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
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Telemetry deleted.", provider=self.service.config.provider_name, latency=(time.time() - start_time)*1000, repository="provider_telemetry")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_telemetry")
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ProviderStatisticsRepositoryImpl(ProviderStatisticsRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

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
                statistics.get("timestamp") or time.time()
            )
            self.service.execute(q, params)
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Statistics saved.", provider=self.service.config.provider_name, latency=(time.time() - start_time)*1000, repository="provider_statistics")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_statistics")
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
            rows = self.service.execute("SELECT * FROM provider_statistics WHERE id = ?", (statistics_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message="Statistics not found.", latency=latency, repository="provider_statistics")
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result
            row = dict(rows[0])
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Statistics retrieved.", provider=self.service.config.provider_name, latency=latency, repository="provider_statistics", payload=row)
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_statistics")
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
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Statistics deleted.", provider=self.service.config.provider_name, latency=(time.time() - start_time)*1000, repository="provider_statistics")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_statistics")
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ProviderQuotaRepositoryImpl(ProviderQuotaRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

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
                quota.get("timestamp") or time.time()
            )
            self.service.execute(q, params)
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Quota saved.", provider=self.service.config.provider_name, latency=(time.time() - start_time)*1000, repository="provider_quotas")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_quotas")
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
                result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message="Quota not found.", latency=latency, repository="provider_quotas")
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result
            row = dict(rows[0])
            row["is_exhausted"] = bool(row["is_exhausted"])
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Quota retrieved.", provider=self.service.config.provider_name, latency=latency, repository="provider_quotas", payload=row)
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_quotas")
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
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Quota deleted.", provider=self.service.config.provider_name, latency=(time.time() - start_time)*1000, repository="provider_quotas")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_quotas")
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ProviderRoutingRepositoryImpl(ProviderRoutingRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

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
                routing.get("timestamp") or time.time()
            )
            self.service.execute(q, params)
            latency = (time.time() - start_time)*1000

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
                    res = PersistenceResult(status=PersistenceStatus.SUCCESS, message="Routing decision retrieved.", provider=self.service.config.provider_name, latency=latency, repository="provider_routing", payload=row)
                    cache_svc.set("provider_routing", routing["id"], res)
                elif policy != CachePolicy.NO_CACHE:
                    cache_svc.delete("provider_routing", routing["id"])

            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Routing decision saved.", provider=self.service.config.provider_name, latency=latency, repository="provider_routing")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_routing")
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
                rows = self.service.execute("SELECT * FROM provider_routing WHERE id = ?", (routing_id,))
                latency = (time.time() - start_time) * 1000
                if not rows:
                    result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message="Routing decision not found.", latency=latency, repository="provider_routing")
                    if self.service.config.policy == PersistencePolicy.STRICT:
                        raise RuntimeError(result.message)
                    return result
                row = dict(rows[0])
                row["routing_candidates"] = json.loads(row["routing_candidates"] or "[]")
                return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Routing decision retrieved.", provider=self.service.config.provider_name, latency=latency, repository="provider_routing", payload=row)
            except Exception as e:
                result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_routing")
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
            latency = (time.time() - start_time)*1000

            # Cache integration
            from aios.registry import ServiceRegistry
            try:
                cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
            except Exception:
                cache_svc = None
            if cache_svc:
                cache_svc.delete("provider_routing", routing_id)

            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Routing decision deleted.", provider=self.service.config.provider_name, latency=latency, repository="provider_routing")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_routing")
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ProviderSessionRepositoryImpl(ProviderSessionRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

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
                session.get("updated_at") or time.time()
            )
            self.service.execute(q, params)
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Session saved.", provider=self.service.config.provider_name, latency=(time.time() - start_time)*1000, repository="provider_sessions")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_sessions")
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
            rows = self.service.execute("SELECT * FROM provider_sessions WHERE id = ?", (session_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message="Session not found.", latency=latency, repository="provider_sessions")
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result
            row = dict(rows[0])
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Session retrieved.", provider=self.service.config.provider_name, latency=latency, repository="provider_sessions", payload=row)
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_sessions")
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
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Session deleted.", provider=self.service.config.provider_name, latency=(time.time() - start_time)*1000, repository="provider_sessions")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_sessions")
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ProviderCheckpointRepositoryImpl(ProviderCheckpointRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

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
                checkpoint.get("timestamp") or time.time()
            )
            self.service.execute(q, params)
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Checkpoint saved.", provider=self.service.config.provider_name, latency=(time.time() - start_time)*1000, repository="provider_checkpoints")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_checkpoints")
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
            rows = self.service.execute("SELECT * FROM provider_checkpoints WHERE id = ?", (checkpoint_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message="Checkpoint not found.", latency=latency, repository="provider_checkpoints")
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result
            row = dict(rows[0])
            try:
                row["context"] = json.loads(row["context"])
            except Exception:
                pass
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Checkpoint retrieved.", provider=self.service.config.provider_name, latency=latency, repository="provider_checkpoints", payload=row)
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_checkpoints")
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
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Checkpoint deleted.", provider=self.service.config.provider_name, latency=(time.time() - start_time)*1000, repository="provider_checkpoints")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_checkpoints")
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class ProviderFailoverRepositoryImpl(ProviderFailoverRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

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
                failover.get("timestamp") or time.time()
            )
            self.service.execute(q, params)
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Failover history logged.", provider=self.service.config.provider_name, latency=(time.time() - start_time)*1000, repository="provider_failovers")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_failovers")
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
            rows = self.service.execute("SELECT * FROM provider_failovers WHERE id = ?", (failover_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message="Failover log not found.", latency=latency, repository="provider_failovers")
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result
            row = dict(rows[0])
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Failover log retrieved.", provider=self.service.config.provider_name, latency=latency, repository="provider_failovers", payload=row)
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_failovers")
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
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Failover log deleted.", provider=self.service.config.provider_name, latency=(time.time() - start_time)*1000, repository="provider_failovers")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="provider_failovers")
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class AIUsageStatisticsRepositoryImpl(AIUsageStatisticsRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def save(self, usage: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("ai_usage_statistics", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            q = "INSERT OR REPLACE INTO ai_usage_statistics (id, provider_name, daily_input_tokens, daily_output_tokens, monthly_input_tokens, monthly_output_tokens, total_cost, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            params = (
                usage["id"],
                usage.get("provider_name"),
                usage.get("daily_input_tokens"),
                usage.get("daily_output_tokens"),
                usage.get("monthly_input_tokens"),
                usage.get("monthly_output_tokens"),
                usage.get("total_cost"),
                usage.get("timestamp") or time.time()
            )
            self.service.execute(q, params)
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Usage statistics saved.", provider=self.service.config.provider_name, latency=(time.time() - start_time)*1000, repository="ai_usage_statistics")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="ai_usage_statistics")
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, usage_id: str) -> PersistenceResult:
        status_res = self.service.check_status("ai_usage_statistics", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            rows = self.service.execute("SELECT * FROM ai_usage_statistics WHERE id = ?", (usage_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message="Usage report not found.", latency=latency, repository="ai_usage_statistics")
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result
            row = dict(rows[0])
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Usage report retrieved.", provider=self.service.config.provider_name, latency=latency, repository="ai_usage_statistics", payload=row)
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="ai_usage_statistics")
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, usage_id: str) -> PersistenceResult:
        status_res = self.service.check_status("ai_usage_statistics", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            self.service.execute("DELETE FROM ai_usage_statistics WHERE id = ?", (usage_id,))
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Usage report deleted.", provider=self.service.config.provider_name, latency=(time.time() - start_time)*1000, repository="ai_usage_statistics")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="ai_usage_statistics")
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class AIMemoryRepositoryImpl(AIMemoryRepository):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def save(self, memory: Dict[str, Any]) -> PersistenceResult:
        status_res = self.service.check_status("ai_memory", "save")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            q = "INSERT OR REPLACE INTO ai_memory (id, key, value, metadata, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)"
            params = (
                memory["id"],
                memory.get("key"),
                memory.get("value"),
                json.dumps(memory.get("metadata", {})),
                memory.get("created_at") or time.time(),
                memory.get("updated_at") or time.time()
            )
            self.service.execute(q, params)
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Memory fact saved.", provider=self.service.config.provider_name, latency=(time.time() - start_time)*1000, repository="ai_memory")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="ai_memory")
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def get(self, memory_id: str) -> PersistenceResult:
        status_res = self.service.check_status("ai_memory", "get")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            rows = self.service.execute("SELECT * FROM ai_memory WHERE id = ?", (memory_id,))
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message="Memory fact not found.", latency=latency, repository="ai_memory")
                if self.service.config.policy == PersistencePolicy.STRICT:
                    raise RuntimeError(result.message)
                return result
            row = dict(rows[0])
            row["metadata"] = json.loads(row["metadata"] or "{}")
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Memory fact retrieved.", provider=self.service.config.provider_name, latency=latency, repository="ai_memory", payload=row)
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="ai_memory")
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result

    def delete(self, memory_id: str) -> PersistenceResult:
        status_res = self.service.check_status("ai_memory", "delete")
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(status_res.message)
            return status_res
        start_time = time.time()
        try:
            self.service.execute("DELETE FROM ai_memory WHERE id = ?", (memory_id,))
            return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Memory fact deleted.", provider=self.service.config.provider_name, latency=(time.time() - start_time)*1000, repository="ai_memory")
        except Exception as e:
            result = PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=(time.time() - start_time)*1000, repository="ai_memory")
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message) from e
            return result


class AIMemoryValidator(ServiceLifecycle):
    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def validate_provider(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"): errors.append("Provider id missing.")
        if not data.get("name"): errors.append("Provider name missing.")
        return errors

    def validate_capabilities(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"): errors.append("Capability id missing.")
        return errors

    def validate_health(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"): errors.append("Health id missing.")
        return errors

    def validate_telemetry(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"): errors.append("Telemetry id missing.")
        return errors

    def validate_statistics(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"): errors.append("Statistics id missing.")
        return errors

    def validate_quota(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"): errors.append("Quota id missing.")
        return errors

    def validate_routing(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"): errors.append("Routing id missing.")
        return errors

    def validate_session(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"): errors.append("Session id missing.")
        return errors

    def validate_checkpoint(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"): errors.append("Checkpoint id missing.")
        return errors

    def validate_failover(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"): errors.append("Failover id missing.")
        return errors

    def validate_usage(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"): errors.append("Usage id missing.")
        return errors

    def validate_memory(self, data: Dict[str, Any]) -> List[str]:
        errors = []
        if not data.get("id"): errors.append("Memory id missing.")
        if not data.get("key"): errors.append("Memory key missing.")
        return errors


class AIMemoryTelemetry(ServiceLifecycle):
    def __init__(self) -> None:
        self.queries_recorded = 0
        self.failed_queries = 0
        self.latency_sum = 0.0

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def record_query(self, latency_ms: float, success: bool) -> None:
        self.queries_recorded += 1
        self.latency_sum += latency_ms
        if not success:
            self.failed_queries += 1

    def get_metrics(self) -> Dict[str, Any]:
        avg = self.latency_sum / self.queries_recorded if self.queries_recorded > 0 else 0.0
        return {
            "queries_recorded": self.queries_recorded,
            "failed_queries": self.failed_queries,
            "average_latency_ms": avg
        }


class AIMemoryStatistics(ServiceLifecycle):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def compile_statistics(self) -> Dict[str, Any]:
        stats = {}
        for category, table in [
            ("providers", "ai_providers"),
            ("capabilities", "provider_capabilities"),
            ("health", "provider_health"),
            ("telemetry", "provider_telemetry"),
            ("statistics", "provider_statistics"),
            ("quotas", "provider_quotas"),
            ("routing", "provider_routing"),
            ("sessions", "provider_sessions"),
            ("checkpoints", "provider_checkpoints"),
            ("failovers", "provider_failovers"),
            ("usage", "ai_usage_statistics"),
            ("memory", "ai_memory")
        ]:
            try:
                rows = self.service.execute(f"SELECT COUNT(*) as count FROM {table}")
                stats[category] = rows[0]["count"] if rows else 0
            except Exception:
                stats[category] = 0
        return stats


class AIMemoryHealthMonitor(ServiceLifecycle):
    def __init__(self, service: PersistenceService, telemetry: AIMemoryTelemetry, stats: AIMemoryStatistics) -> None:
        self.service = service
        self.telemetry = telemetry
        self.stats = stats

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def check_health(self) -> Dict[str, Any]:
        connected = False
        try:
            self.service.execute("SELECT 1")
            connected = True
        except Exception:
            pass
        metrics = self.telemetry.get_metrics()
        return {
            "db_connected": connected,
            "status": "healthy" if connected and metrics["failed_queries"] == 0 else "degraded",
            "failures": metrics["failed_queries"],
            "total_queries": metrics["queries_recorded"],
            "avg_latency_ms": metrics["average_latency_ms"]
        }


class AIMemoryReportGenerator(ServiceLifecycle):
    def __init__(self, working_dir: str, health_monitor: AIMemoryHealthMonitor) -> None:
        self.working_dir = working_dir
        self.health_monitor = health_monitor

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def generate_health_report(self) -> str:
        health = self.health_monitor.check_health()
        stats = self.health_monitor.stats.compile_statistics()
        report = (
            "# AI Memory Persistence Health & Diagnostic Report\n\n"
            f"**Overall Status**: {health['status'].upper()}\n"
            f"**Database Connected**: {health['db_connected']}\n"
            f"**Failures Tallied**: {health['failures']}\n"
            f"**Total Queries Evaluated**: {health['total_queries']}\n"
            f"**Average Latency**: {health['avg_latency_ms']:.2f}ms\n\n"
            "## Storage Statistics\n"
            f"- Providers Registered: {stats.get('providers', 0)}\n"
            f"- Capability Profiles: {stats.get('capabilities', 0)}\n"
            f"- Active Checkpoints: {stats.get('checkpoints', 0)}\n"
            f"- Failover Operations Logs: {stats.get('failovers', 0)}\n"
            f"- Session Mappings: {stats.get('sessions', 0)}\n"
            f"- Usage Reports: {stats.get('usage', 0)}\n"
            f"- Facts Stored: {stats.get('memory', 0)}\n"
        )
        return report


class AIMemoryPersistenceServiceImpl(AIMemoryPersistenceService):
    def __init__(
        self,
        service: PersistenceService,
        provider_repo: AIProviderRepository,
        capability_repo: ProviderCapabilityRepository,
        health_repo: ProviderHealthRepository,
        telemetry_repo: ProviderTelemetryRepository,
        statistics_repo: ProviderStatisticsRepository,
        quota_repo: ProviderQuotaRepository,
        routing_repo: ProviderRoutingRepository,
        session_repo: ProviderSessionRepository,
        checkpoint_repo: ProviderCheckpointRepository,
        failover_repo: ProviderFailoverRepository,
        usage_repo: AIUsageStatisticsRepository,
        memory_repo: AIMemoryRepository,
        validator: AIMemoryValidator,
        telemetry: AIMemoryTelemetry,
        stats_compiler: AIMemoryStatistics,
        health_monitor: AIMemoryHealthMonitor,
        report_generator: AIMemoryReportGenerator
    ) -> None:
        self.service = service
        self.provider_repo = provider_repo
        self.capability_repo = capability_repo
        self.health_repo = health_repo
        self.telemetry_repo = telemetry_repo
        self.statistics_repo = statistics_repo
        self.quota_repo = quota_repo
        self.routing_repo = routing_repo
        self.session_repo = session_repo
        self.checkpoint_repo = checkpoint_repo
        self.failover_repo = failover_repo
        self.usage_repo = usage_repo
        self.memory_repo = memory_repo
        self.validator = validator
        self.telemetry = telemetry
        self.stats_compiler = stats_compiler
        self.health_monitor = health_monitor
        self.report_generator = report_generator

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def _get_repo(self, category: str) -> Optional[Any]:
        repos = {
            "providers": self.provider_repo,
            "capabilities": self.capability_repo,
            "health": self.health_repo,
            "telemetry": self.telemetry_repo,
            "statistics": self.statistics_repo,
            "quotas": self.quota_repo,
            "routing": self.routing_repo,
            "sessions": self.session_repo,
            "checkpoints": self.checkpoint_repo,
            "failovers": self.failover_repo,
            "usage": self.usage_repo,
            "memory": self.memory_repo
        }
        return repos.get(category)

    def Record(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult:
        return self.record(category, entity_id, data)

    def record(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult:
        repo = self._get_repo(category)
        if not repo:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'")
        data["id"] = entity_id
        
        # Validation
        val_map = {
            "providers": self.validator.validate_provider,
            "capabilities": self.validator.validate_capabilities,
            "health": self.validator.validate_health,
            "telemetry": self.validator.validate_telemetry,
            "statistics": self.validator.validate_statistics,
            "quotas": self.validator.validate_quota,
            "routing": self.validator.validate_routing,
            "sessions": self.validator.validate_session,
            "checkpoints": self.validator.validate_checkpoint,
            "failovers": self.validator.validate_failover,
            "usage": self.validator.validate_usage,
            "memory": self.validator.validate_memory
        }
        errs = val_map[category](data)
        if errs:
            self.telemetry.record_query(0.0, False)
            result = PersistenceResult(status=PersistenceStatus.VALIDATION_FAILED, message=", ".join(errs))
            if self.service.config.policy == PersistencePolicy.STRICT:
                raise RuntimeError(result.message)
            return result

        res = repo.save(data)
        self.telemetry.record_query(res.latency or 0.0, res.status == PersistenceStatus.SUCCESS)
        return res

    def Update(self, category: str, entity_id: str, data: Dict[str, Any]) -> PersistenceResult:
        return self.record(category, entity_id, data)

    def Archive(self, category: str, entity_id: str) -> PersistenceResult:
        return self.archive(category, entity_id)

    def archive(self, category: str, entity_id: str) -> PersistenceResult:
        repo = self._get_repo(category)
        if not repo:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'")
        start_time = time.time()
        try:
            res = repo.delete(entity_id)
            self.telemetry.record_query(res.latency or 0.0, res.status == PersistenceStatus.SUCCESS)
            return res
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.telemetry.record_query(latency, False)
            return PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=str(e), latency=latency)

    def Restore(self, category: str, entity_id: str) -> PersistenceResult:
        # Checkpoints/routing results don't have secondary archive storage, stub success or get
        repo = self._get_repo(category)
        if not repo:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'")
        return repo.get(entity_id)

    def History(self, category: str, entity_id: str) -> PersistenceResult:
        repo = self._get_repo(category)
        if not repo:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'")
        res = repo.get(entity_id)
        self.telemetry.record_query(res.latency or 0.0, res.status == PersistenceStatus.SUCCESS)
        if res.status != PersistenceStatus.SUCCESS or not res.payload:
            return res
        return PersistenceResult(status=PersistenceStatus.SUCCESS, message="History retrieved.", payload=[res.payload])

    def Statistics(self) -> PersistenceResult:
        stats = self.stats_compiler.compile_statistics()
        return PersistenceResult(status=PersistenceStatus.SUCCESS, message="Statistics compiled.", payload=stats)

    def SearchMetadata(self, category: str, query_params: Dict[str, Any]) -> PersistenceResult:
        return self.search_metadata(category, query_params)

    def search_metadata(self, category: str, query_params: Dict[str, Any]) -> PersistenceResult:
        repo = self._get_repo(category)
        if not repo:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'")

        table_map = {
            "providers": "ai_providers",
            "capabilities": "provider_capabilities",
            "health": "provider_health",
            "telemetry": "provider_telemetry",
            "statistics": "provider_statistics",
            "quotas": "provider_quotas",
            "routing": "provider_routing",
            "sessions": "provider_sessions",
            "checkpoints": "provider_checkpoints",
            "failovers": "provider_failovers",
            "usage": "ai_usage_statistics",
            "memory": "ai_memory"
        }
        table_name = table_map.get(category)
        if not table_name:
            self.telemetry.record_query(0.0, False)
            return PersistenceResult(status=PersistenceStatus.UNKNOWN_FAILURE, message=f"Invalid category '{category}'")

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
                    "supported_models", "capabilities", "query_latencies", "routing_candidates", "metadata"
                ]:
                    if json_field in row:
                        try:
                            row[json_field] = json.loads(row[json_field] or "[]" if json_field in ["supported_models", "query_latencies", "routing_candidates"] else "{}")
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
                payload=results
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            self.telemetry.record_query(latency, False)
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository=table_name
            )
            return result


from aios.services.persistence import RuntimeIntelligenceService
import threading
import uuid

def get_unified_ri() -> Optional[Any]:
    try:
        from aios.registry import ServiceRegistry
        from aios.services.persistence import RuntimeIntelligenceService
        reg = ServiceRegistry._global_registry
        if reg:
            return reg.get(RuntimeIntelligenceService)
    except Exception:
        pass
    return None


class RuntimeCorrelationManager(ServiceLifecycle):
    _local = threading.local()

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    @classmethod
    def set_context(cls, workspace_id: Optional[str] = None, project_id: Optional[str] = None, repository: Optional[str] = None, operation: Optional[str] = None) -> str:
        corr_id = str(uuid.uuid4())
        cls._local.correlation_id = corr_id
        cls._local.workspace_id = workspace_id
        cls._local.project_id = project_id
        cls._local.repository = repository
        cls._local.operation = operation
        cls._local.timestamp = time.time()
        return corr_id

    @classmethod
    def get_context(cls) -> Dict[str, Any]:
        return {
            "correlation_id": getattr(cls._local, "correlation_id", None),
            "workspace_id": getattr(cls._local, "workspace_id", None),
            "project_id": getattr(cls._local, "project_id", None),
            "repository": getattr(cls._local, "repository", None),
            "operation": getattr(cls._local, "operation", None),
            "timestamp": getattr(cls._local, "timestamp", None),
        }

    @classmethod
    def clear(cls) -> None:
        if hasattr(cls._local, "correlation_id"): del cls._local.correlation_id
        if hasattr(cls._local, "workspace_id"): del cls._local.workspace_id
        if hasattr(cls._local, "project_id"): del cls._local.project_id
        if hasattr(cls._local, "repository"): del cls._local.repository
        if hasattr(cls._local, "operation"): del cls._local.operation
        if hasattr(cls._local, "timestamp"): del cls._local.timestamp


class RuntimeTelemetryCollector(ServiceLifecycle):
    def __init__(self) -> None:
        self.queries_recorded = 0
        self.failed_queries = 0
        self.latencies: List[float] = []
        self.retries = 0
        self.active_connections = 0
        self.idle_connections = 0
        self.connection_failures = 0

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def record_query(self, latency_ms: float, success: bool) -> None:
        self.queries_recorded += 1
        self.latencies.append(latency_ms)
        if len(self.latencies) > 1000:
            self.latencies.pop(0)
        if not success:
            self.failed_queries += 1

    def record_retry(self) -> None:
        self.retries += 1

    def record_connection_status(self, active: int, idle: int, failures: int) -> None:
        self.active_connections = active
        self.idle_connections = idle
        self.connection_failures += failures


class RuntimePerformanceAnalyzer(ServiceLifecycle):
    def __init__(self, telemetry: RuntimeTelemetryCollector) -> None:
        self.telemetry = telemetry

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def get_percentile(self, pct: float) -> float:
        lats = sorted(self.telemetry.latencies)
        if not lats:
            return 0.0
        idx = int(len(lats) * (pct / 100.0))
        return lats[min(idx, len(lats) - 1)]

    def get_performance_metrics(self) -> Dict[str, float]:
        return {
            "p50_latency_ms": self.get_percentile(50.0),
            "p95_latency_ms": self.get_percentile(95.0),
            "p99_latency_ms": self.get_percentile(99.0),
            "average_latency_ms": sum(self.telemetry.latencies) / len(self.telemetry.latencies) if self.telemetry.latencies else 0.0
        }


class RuntimeStatisticsEngine(ServiceLifecycle):
    def __init__(self, service: PersistenceService) -> None:
        self.service = service
        self.read_hits = 0
        self.read_misses = 0
        self.write_throughs = 0
        self.read_throughs = 0
        self.success_operations = 0
        self.failed_operations = 0
        self.policies_used: Dict[str, int] = {}

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def record_operation(self, success: bool, policy: str) -> None:
        if success:
            self.success_operations += 1
        else:
            self.failed_operations += 1
        self.policies_used[policy] = self.policies_used.get(policy, 0) + 1

    def record_cache(self, hit: bool, is_read: bool = True) -> None:
        if is_read:
            if hit:
                self.read_hits += 1
                self.read_throughs += 1
            else:
                self.read_misses += 1
        else:
            self.write_throughs += 1

    def get_statistics(self) -> Dict[str, Any]:
        total_reads = self.read_hits + self.read_misses
        ratio = self.read_hits / total_reads if total_reads > 0 else 1.0
        return {
            "total_operations": self.success_operations + self.failed_operations,
            "success_operations": self.success_operations,
            "failed_operations": self.failed_operations,
            "cache_hit_ratio": ratio,
            "read_throughs": self.read_throughs,
            "write_throughs": self.write_throughs,
            "policies_used": self.policies_used
        }


class RuntimeDiagnosticsEngine(ServiceLifecycle):
    def __init__(self) -> None:
        self.errors: List[Dict[str, Any]] = []

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def log_error(self, message: str, severity: str = "ERROR", remediation: str = "Verify connection settings.") -> None:
        self.errors.append({
            "message": message,
            "severity": severity,
            "remediation": remediation,
            "timestamp": time.time()
        })

    def get_diagnostics(self) -> Dict[str, Any]:
        criticals = [e for e in self.errors if e["severity"] == "CRITICAL"]
        status = "healthy"
        if criticals:
            status = "critical"
        elif [e for e in self.errors if e["severity"] == "ERROR"]:
            status = "degraded"
        return {
            "status": status,
            "total_logged_errors": len(self.errors),
            "errors": self.errors
        }


class RuntimeCapacityAnalyzer(ServiceLifecycle):
    def __init__(self, telemetry: RuntimeTelemetryCollector) -> None:
        self.telemetry = telemetry

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def get_capacity_status(self) -> Dict[str, Any]:
        pool_starved = False
        total_conns = self.telemetry.active_connections + self.telemetry.idle_connections
        if total_conns > 0 and self.telemetry.active_connections / total_conns > 0.9:
            pool_starved = True
        return {
            "active_connections": self.telemetry.active_connections,
            "idle_connections": self.telemetry.idle_connections,
            "connection_starvation_risk": pool_starved,
            "starvation_level": "HIGH" if pool_starved else "LOW"
        }


class RuntimeQueryProfiler(ServiceLifecycle):
    def __init__(self) -> None:
        self.slow_queries: List[Dict[str, Any]] = []

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def profile_query(self, query: str, duration_ms: float) -> None:
        if duration_ms > 100.0:
            self.slow_queries.append({
                "query": query,
                "duration_ms": duration_ms,
                "timestamp": time.time()
            })
            if len(self.slow_queries) > 100:
                self.slow_queries.pop(0)

    def get_slow_queries(self) -> List[Dict[str, Any]]:
        return self.slow_queries


class RuntimeTransactionProfiler(ServiceLifecycle):
    def __init__(self) -> None:
        self.tx_count = 0
        self.tx_durations: List[float] = []
        self.nested_tx_count = 0

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def record_transaction(self, duration_ms: float, nested: bool) -> None:
        self.tx_count += 1
        self.tx_durations.append(duration_ms)
        if nested:
            self.nested_tx_count += 1

    def get_transaction_metrics(self) -> Dict[str, Any]:
        avg = sum(self.tx_durations) / len(self.tx_durations) if self.tx_durations else 0.0
        return {
            "total_transactions": self.tx_count,
            "average_tx_duration_ms": avg,
            "nested_transactions": self.nested_tx_count
        }


class RuntimeRepositoryProfiler(ServiceLifecycle):
    def __init__(self) -> None:
        self.repo_calls: Dict[str, int] = {}
        self.repo_durations: Dict[str, List[float]] = {}

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def record_call(self, repo: str, operation: str, duration_ms: float) -> None:
        key = f"{repo}:{operation}"
        self.repo_calls[key] = self.repo_calls.get(key, 0) + 1
        if repo not in self.repo_durations:
            self.repo_durations[repo] = []
        self.repo_durations[repo].append(duration_ms)

    def get_utilization(self) -> Dict[str, Any]:
        avg_durations = {}
        for repo, durs in self.repo_durations.items():
            avg_durations[repo] = sum(durs) / len(durs) if durs else 0.0
        return {
            "calls_breakdown": self.repo_calls,
            "average_repository_latencies": avg_durations
        }


class RuntimeLifecycleMonitor(ServiceLifecycle):
    def __init__(self) -> None:
        self.boot_time = 0.0
        self.swaps = 0
        self.migrations_run = 0

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def record_boot(self, duration_s: float) -> None:
        self.boot_time = duration_s

    def record_swap(self) -> None:
        self.swaps += 1

    def record_migrations(self, count: int) -> None:
        self.migrations_run = count

    def get_lifecycle_status(self) -> Dict[str, Any]:
        return {
            "boot_duration_s": self.boot_time,
            "provider_swaps": self.swaps,
            "migrations_executed": self.migrations_run
        }


class RuntimeRecommendationEngine(ServiceLifecycle):
    def __init__(
        self,
        telemetry: RuntimeTelemetryCollector,
        perf: RuntimePerformanceAnalyzer,
        capacity: RuntimeCapacityAnalyzer,
        query_prof: RuntimeQueryProfiler,
        tx_prof: RuntimeTransactionProfiler,
        repo_prof: RuntimeRepositoryProfiler,
    ) -> None:
        self.telemetry = telemetry
        self.perf = perf
        self.capacity = capacity
        self.query_prof = query_prof
        self.tx_prof = tx_prof
        self.repo_prof = repo_prof

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def generate_recommendations(self) -> List[Dict[str, Any]]:
        recs = []
        cap = self.capacity.get_capacity_status()
        if cap["connection_starvation_risk"]:
            recs.append({
                "category": "Capacity",
                "issue": "Database connection pool utilization is extremely high (>90%).",
                "suggestion": "Increase connection pool maximum size to avoid query latency spikes or pool exhaustion.",
                "severity": "WARNING"
            })

        slow = self.query_prof.get_slow_queries()
        if slow:
            recs.append({
                "category": "Performance",
                "issue": f"Detected {len(slow)} queries executing slower than 100ms.",
                "suggestion": "Review execution plans and introduce relevant indexes on tables.",
                "severity": "WARNING"
            })

        if self.telemetry.connection_failures > 5:
            recs.append({
                "category": "Reliability",
                "issue": f"Frequent connection failure retry checks: {self.telemetry.connection_failures} occurrences.",
                "suggestion": "Inspect network latency, connection reliability, or check if database service restarted.",
                "severity": "ERROR"
            })

        tx = self.tx_prof.get_transaction_metrics()
        if tx["average_tx_duration_ms"] > 500.0:
            recs.append({
                "category": "Performance",
                "issue": f"Average transaction execution takes {tx['average_tx_duration_ms']:.2f}ms.",
                "suggestion": "Verify that transactions are short-lived and optimize lock acquisition times.",
                "severity": "WARNING"
            })

        if not recs:
            recs.append({
                "category": "Maintenance",
                "issue": "No critical runtime anomalies observed.",
                "suggestion": "Execute periodic VACUUM or ANALYZE routines to optimize statistics indexes.",
                "severity": "INFO"
            })

        return recs


class RuntimeHealthMonitor(ServiceLifecycle):
    def __init__(self, service: PersistenceService, telemetry: RuntimeTelemetryCollector) -> None:
        self.service = service
        self.telemetry = telemetry

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def check_health(self) -> Dict[str, Any]:
        impl = self.service
        provider = impl.active_provider
        reachable = False
        status = "offline"
        issues = []
        
        if provider and provider.transport:
            reachable = provider.is_connected()
            status = "online" if reachable else "offline"
            if not reachable:
                issues.append("Active transport connection offline")
        else:
            issues.append("No active database transport initialized")

        total = self.telemetry.queries_recorded
        failed = self.telemetry.failed_queries
        avail = 100.0
        if total > 0:
            avail = ((total - failed) / total) * 100.0

        return {
            "status": status,
            "server_reachable": reachable,
            "availability_pct": avail,
            "issues": issues,
            "timestamp": time.time()
        }


class RuntimeReportGenerator(ServiceLifecycle):
    def __init__(self, working_dir: str, intelligence: Any) -> None:
        self.working_dir = working_dir
        self.intelligence = intelligence

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def generate_reports(self) -> None:
        r_dir = os.path.join(self.working_dir, "docs", "persistence")
        os.makedirs(r_dir, exist_ok=True)

        health = self.intelligence.get_health()
        diag = self.intelligence.get_diagnostics()
        stats = self.intelligence.get_statistics()
        recs = self.intelligence.get_recommendations()

        with open(os.path.join(r_dir, "RUNTIME_INTELLIGENCE_STATUS.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Runtime Intelligence Platform Status\n\n"
                f"- **Status**: {health['status'].upper()}\n"
                f"- **Database Connection**: {'CONNECTED' if health['server_reachable'] else 'DISCONNECTED'}\n"
                f"- **Query Availability**: {health['availability_pct']:.2f}%\n"
                f"- **Timestamp**: {health['timestamp']}\n"
            )

        with open(os.path.join(r_dir, "RUNTIME_INTELLIGENCE_HEALTH.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Runtime Intelligence Health Audit\n\n"
                f"- Live state checks completed.\n"
                f"- Issues found: {health['issues']}\n"
            )

        with open(os.path.join(r_dir, "RUNTIME_INTELLIGENCE_STATISTICS.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Runtime Intelligence System Statistics\n\n"
                f"### Operations\n"
                f"- Total Operations: {stats['total_operations']}\n"
                f"- Successful Operations: {stats['success_operations']}\n"
                f"- Failed Operations: {stats['failed_operations']}\n"
                f"- Cache Hit Ratio: {stats['cache_hit_ratio']:.2%}\n"
                f"- Write Throughs: {stats['write_throughs']}\n"
            )

        with open(os.path.join(r_dir, "RUNTIME_INTELLIGENCE_DIAGNOSTICS.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Runtime Diagnostics Audit & Recommendations\n\n"
                f"### Diagnostics State: {diag['status'].upper()}\n\n"
                f"### Recommendations:\n"
            )
            for r in recs:
                f.write(f"- **[{r['category']}]**: {r['issue']} -> Suggestion: *{r['suggestion']}* ({r['severity']})\n")


class RuntimeIntelligenceServiceImpl(RuntimeIntelligenceService, ServiceLifecycle):
    def __init__(
        self,
        health_monitor: RuntimeHealthMonitor,
        telemetry: RuntimeTelemetryCollector,
        stats_engine: RuntimeStatisticsEngine,
        diag_engine: RuntimeDiagnosticsEngine,
        capacity: RuntimeCapacityAnalyzer,
        recommend: RuntimeRecommendationEngine,
        perf: RuntimePerformanceAnalyzer,
        query_prof: RuntimeQueryProfiler,
        tx_prof: RuntimeTransactionProfiler,
        repo_prof: RuntimeRepositoryProfiler,
        lifecycle: RuntimeLifecycleMonitor,
        report_gen: RuntimeReportGenerator
    ) -> None:
        self.health_monitor = health_monitor
        self.telemetry = telemetry
        self.stats_engine = stats_engine
        self.diag_engine = diag_engine
        self.capacity = capacity
        self.recommend = recommend
        self.perf = perf
        self.query_prof = query_prof
        self.tx_prof = tx_prof
        self.repo_prof = repo_prof
        self.lifecycle = lifecycle
        self.report_gen = report_gen

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def get_health(self) -> Dict[str, Any]:
        return self.health_monitor.check_health()

    def get_diagnostics(self) -> Dict[str, Any]:
        return self.diag_engine.get_diagnostics()

    def get_telemetry(self) -> Dict[str, Any]:
        return {
            "queries_recorded": self.telemetry.queries_recorded,
            "failed_queries": self.telemetry.failed_queries,
            "retries": self.telemetry.retries,
            "performance": self.perf.get_performance_metrics()
        }

    def get_statistics(self) -> Dict[str, Any]:
        return self.stats_engine.get_statistics()

    def get_recommendations(self) -> List[Dict[str, Any]]:
        return self.recommend.generate_recommendations()

    def get_learning_payload(self) -> Dict[str, Any]:
        return {
            "runtime_trends": {
                "throughput": self.telemetry.queries_recorded,
                "avg_latency_ms": self.perf.get_performance_metrics()["average_latency_ms"]
            },
            "failure_trends": {
                "total_failures": self.telemetry.failed_queries,
                "connection_failures": self.telemetry.connection_failures
            },
            "performance_trends": self.perf.get_performance_metrics(),
            "capacity_trends": self.capacity.get_capacity_status(),
            "repository_trends": self.repo_prof.get_utilization(),
            "recommendation_history": self.get_recommendations()
        }

    def generate_reports(self) -> None:
        self.report_gen.generate_reports()


from aios.services.persistence import (
    RedisTransport,
    RedisProvider,
    RedisRuntimeService,
    CachePolicy,
    CachePolicyManager,
    CacheInvalidationManager,
    CacheWarmupService,
    CacheRebuildService,
    CacheStatisticsCollector,
    CacheHealthMonitor,
    CacheDiagnostics,
    CacheRecommendationEngine,
    RedisCacheService,
    SessionPolicy,
    SessionRegistry,
    SessionExpirationManager,
    SessionRecoveryManager,
    SessionStatisticsCollector,
    SessionHealthMonitor,
    SessionDiagnostics,
    SessionRecommendationEngine,
    SessionStore,
    SessionManager,
    RedisSessionService,
)

class RedisConfigurationService(ServiceLifecycle):
    def __init__(self) -> None:
        self.host = os.environ.get("REDIS_HOST")
        try:
            self.port = int(os.environ.get("REDIS_PORT", 6379))
        except ValueError:
            self.port = 6379
        self.username = os.environ.get("REDIS_USERNAME")
        self.password = os.environ.get("REDIS_PASSWORD")
        try:
            self.database = int(os.environ.get("REDIS_DATABASE", 0))
        except ValueError:
            self.database = 0
        self.tls = os.environ.get("REDIS_TLS", "false").lower() == "true"
        try:
            self.timeout = float(os.environ.get("REDIS_TIMEOUT", 2.0))
        except ValueError:
            self.timeout = 2.0
        try:
            self.max_connections = int(os.environ.get("REDIS_MAX_CONNECTIONS", 10))
        except ValueError:
            self.max_connections = 10
        self.awaiting_configuration = not self.host

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass


class FakeRedisClient:
    def __init__(self, *args, **kwargs) -> None:
        self._data: Dict[str, str] = {}
        self._expires: Dict[str, float] = {}

    def ping(self) -> bool:
        return True

    def get(self, key: str) -> Optional[str]:
        if key in self._expires and time.time() > self._expires[key]:
            del self._data[key]
            del self._expires[key]
            return None
        return self._data.get(key)

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        self._data[key] = str(value)
        if ex is not None:
            self._expires[key] = time.time() + ex
        else:
            if key in self._expires:
                del self._expires[key]
        return True

    def delete(self, key: str) -> bool:
        existed = key in self._data
        if key in self._data:
            del self._data[key]
        if key in self._expires:
            del self._expires[key]
        return existed

    def exists(self, key: str) -> bool:
        self.get(key)  # trigger expiry
        return key in self._data

    def keys(self, pattern: str = "*") -> List[str]:
        import fnmatch
        now = time.time()
        expired = [k for k, exp in self._expires.items() if now > exp]
        for k in expired:
            if k in self._data:
                del self._data[k]
            if k in self._expires:
                del self._expires[k]
        return [k for k in self._data.keys() if fnmatch.fnmatch(k, pattern)]



class RedisConnectionManager(ServiceLifecycle):
    def __init__(self, config: RedisConfigurationService) -> None:
        self.config = config
        self.client: Any = None
        self.connection_failures = 0
        self.retries = 0

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def connect(self) -> Any:
        if self.config.awaiting_configuration:
            return None

        try:
            import redis
            self.client = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                db=self.config.database,
                ssl=self.config.tls,
                socket_timeout=self.config.timeout,
                max_connections=self.config.max_connections,
                decode_responses=True
            )
        except Exception:
            self.client = FakeRedisClient()

        try:
            self.retries += 1
            if self.client.ping():
                self.connection_failures = 0
                return self.client
        except Exception:
            self.connection_failures += 1
            self.client = FakeRedisClient()
            return self.client


class RedisTransportImpl(RedisTransport):
    def __init__(self, config: RedisConfigurationService, conn_manager: RedisConnectionManager) -> None:
        self.config = config
        self.conn_manager = conn_manager
        self.client: Any = None

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def connect(self) -> None:
        self.client = self.conn_manager.connect()

    def disconnect(self) -> None:
        self.client = None

    def is_connected(self) -> bool:
        if not self.client:
            return False
        try:
            return self.client.ping()
        except Exception:
            return False

    def execute_command(self, cmd: str, *args: Any, **kwargs: Any) -> Any:
        if not self.client:
            self.connect()
        if not self.client:
            raise RuntimeError("Redis transport is not connected")
        
        start_time = time.time()
        success = True
        try:
            fn = getattr(self.client, cmd.lower())
            return fn(*args, **kwargs)
        except Exception as e:
            success = False
            raise e
        finally:
            duration_ms = (time.time() - start_time) * 1000.0
            ri = get_unified_ri()
            if ri:
                try:
                    ri.telemetry.record_query(duration_ms, success)
                except Exception:
                    pass


class RedisProviderImpl(RedisProvider):
    def __init__(self, transport: RedisTransport) -> None:
        self.transport = transport

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def get(self, key: str) -> Optional[str]:
        try:
            return self.transport.execute_command("get", key)
        except Exception:
            return None

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        try:
            return bool(self.transport.execute_command("set", key, value, ex=ttl))
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        try:
            return bool(self.transport.execute_command("delete", key))
        except Exception:
            return False

    def exists(self, key: str) -> bool:
        try:
            return bool(self.transport.execute_command("exists", key))
        except Exception:
            return False


class RedisTelemetry(ServiceLifecycle):
    def __init__(self) -> None:
        self.queries_recorded = 0
        self.failed_queries = 0
        self.latency_sum = 0.0

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def record_query(self, latency_ms: float, success: bool) -> None:
        self.queries_recorded += 1
        self.latency_sum += latency_ms
        if not success:
            self.failed_queries += 1


class RedisStatistics(ServiceLifecycle):
    def __init__(self, telemetry: RedisTelemetry) -> None:
        self.telemetry = telemetry

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def get_metrics(self) -> Dict[str, Any]:
        avg = self.telemetry.latency_sum / self.telemetry.queries_recorded if self.telemetry.queries_recorded > 0 else 0.0
        return {
            "queries_recorded": self.telemetry.queries_recorded,
            "failed_queries": self.telemetry.failed_queries,
            "average_latency_ms": avg
        }


class RedisDiagnostics(ServiceLifecycle):
    def __init__(self, conn_manager: RedisConnectionManager) -> None:
        self.conn_manager = conn_manager

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def get_diagnostics(self) -> Dict[str, Any]:
        status = "healthy"
        remediations = []
        if self.conn_manager.config.awaiting_configuration:
            status = "degraded"
            remediations.append("Configure REDIS_HOST env var to enable Redis runtime acceleration.")
        elif self.conn_manager.connection_failures > 3:
            status = "degraded"
            remediations.append("Check Redis network reachability or port configuration.")
        return {
            "status": status,
            "remediations": remediations,
            "connection_failures": self.conn_manager.connection_failures
        }


class RedisHealthMonitor(ServiceLifecycle):
    def __init__(self, transport: RedisTransport) -> None:
        self.transport = transport

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def check_health(self) -> Dict[str, Any]:
        alive = self.transport.is_connected()
        return {
            "status": "online" if alive else "offline",
            "connected": alive
        }


class RedisValidator(ServiceLifecycle):
    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def validate_key(self, key: str) -> List[str]:
        errors = []
        if not key.startswith("aios:v1:"):
            errors.append("Keyspace naming violation: Key must start with 'aios:v1:' prefix.")
        parts = key.split(":")
        if len(parts) < 7:
            errors.append("Keyspace structural violation: Key must include version, workspace, project, subsystem, entity, and purpose.")
        return errors


class RedisReportGenerator(ServiceLifecycle):
    def __init__(self, working_dir: str, runtime_service: Any) -> None:
        self.working_dir = working_dir
        self.runtime_service = runtime_service

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def generate_reports(self) -> None:
        r_dir = os.path.join(self.working_dir, "docs", "persistence")
        os.makedirs(r_dir, exist_ok=True)

        health = self.runtime_service.get_health()
        diag = self.runtime_service.get_diagnostics()
        stats = self.runtime_service.get_statistics()

        with open(os.path.join(r_dir, "REDIS_PLATFORM_STATUS.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Redis Platform Status\n\n"
                f"- **Connection State**: {health['status'].upper()}\n"
                f"- **Diagnostics State**: {diag['status'].upper()}\n"
            )

        with open(os.path.join(r_dir, "REDIS_PLATFORM_HEALTH.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Redis Platform Health Audit\n\n"
                f"- Connection Reachable: {health['connected']}\n"
            )

        with open(os.path.join(r_dir, "REDIS_PLATFORM_STATISTICS.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Redis Platform Operational Statistics\n\n"
                f"- Queries Recorded: {stats['queries_recorded']}\n"
                f"- Average Query Latency: {stats['average_latency_ms']:.2f}ms\n"
            )

        with open(os.path.join(r_dir, "REDIS_PLATFORM_DIAGNOSTICS.md"), "w", encoding="utf-8") as f:
            f.write(
                f"# Redis Platform Diagnostics Report\n\n"
                f"- Remediations: {diag['remediations']}\n"
            )


class RedisRuntimeServiceImpl(RedisRuntimeService, ServiceLifecycle):
    def __init__(
        self,
        config: RedisConfigurationService,
        transport: RedisTransport,
        provider: RedisProvider,
        health: RedisHealthMonitor,
        diag: RedisDiagnostics,
        telemetry: RedisTelemetry,
        stats: RedisStatistics,
        validator: RedisValidator,
        report_gen: RedisReportGenerator
    ) -> None:
        self.config = config
        self.transport = transport
        self.provider = provider
        self.health_monitor = health
        self.diagnostics_engine = diag
        self.telemetry = telemetry
        self.stats_engine = stats
        self.validator = validator
        self.report_gen = report_gen

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def get_health(self) -> Dict[str, Any]:
        return self.health_monitor.check_health()

    def get_diagnostics(self) -> Dict[str, Any]:
        return self.diagnostics_engine.get_diagnostics()

    def get_telemetry(self) -> Dict[str, Any]:
        return {
            "queries_recorded": self.telemetry.queries_recorded,
            "failed_queries": self.telemetry.failed_queries
        }

    def get_statistics(self) -> Dict[str, Any]:
        return self.stats_engine.get_metrics()

    def get_recommendations(self) -> List[Dict[str, Any]]:
        recs = []
        diag = self.get_diagnostics()
        if diag["status"] == "degraded":
            recs.append({
                "category": "Configuration",
                "issue": "Redis is awaiting configuration or offline.",
                "suggestion": "Check environment parameters or server connection state.",
                "severity": "WARNING"
            })
        if not recs:
            recs.append({
                "category": "Maintenance",
                "issue": "No anomalies detected.",
                "suggestion": "Platform performing normally.",
                "severity": "INFO"
            })
        return recs

    def format_key(self, workspace: str, project: str, subsystem: str, entity: str, purpose: str) -> str:
        return f"aios:v1:{workspace}:{project}:{subsystem}:{entity}:{purpose}"

    def get_learning_payload(self) -> Dict[str, Any]:
        return {
            "runtime_statistics": self.get_statistics(),
            "connection_statistics": {
                "failures": self.diagnostics_engine.conn_manager.connection_failures,
                "retries": self.diagnostics_engine.conn_manager.retries
            },
            "recommendations": self.get_recommendations()
        }

    def generate_reports(self) -> None:
        self.report_gen.generate_reports()


# -----------------------------------------------------------------------------
# Runtime Cache Platform Implementation
# -----------------------------------------------------------------------------

def serialize_val(val: Any) -> str:
    if isinstance(val, PersistenceResult):
        return json.dumps({
            "__type__": "PersistenceResult",
            "status": val.status.value,
            "message": val.message,
            "error_code": val.error_code,
            "diagnostics": val.diagnostics,
            "retryable": val.retryable,
            "provider": val.provider,
            "latency": val.latency,
            "operation_id": val.operation_id,
            "timestamp": val.timestamp,
            "repository": val.repository,
            "payload": val.payload
        })
    return json.dumps({
        "__type__": "raw",
        "value": val
    })

def deserialize_val(s: str) -> Any:
    d = json.loads(s)
    if isinstance(d, dict) and d.get("__type__") == "PersistenceResult":
        from aios.services.persistence import PersistenceStatus
        return PersistenceResult(
            status=PersistenceStatus(d["status"]),
            message=d["message"],
            error_code=d["error_code"],
            diagnostics=d["diagnostics"],
            retryable=d["retryable"],
            provider=d["provider"],
            latency=d["latency"],
            operation_id=d["operation_id"],
            timestamp=d["timestamp"],
            repository=d["repository"],
            payload=d["payload"]
        )
    elif isinstance(d, dict) and d.get("__type__") == "raw":
        return d["value"]
    return d


class CachePolicyManagerImpl(CachePolicyManager):
    def __init__(self) -> None:
        self._policies: Dict[str, CachePolicy] = {
            "provider_capabilities": CachePolicy.READ_THROUGH,
            "provider_routing": CachePolicy.READ_THROUGH,
            "provider_health": CachePolicy.READ_THROUGH,
            "workspace": CachePolicy.READ_THROUGH,
            "profile": CachePolicy.READ_THROUGH,
            "runtime_statistics": CachePolicy.READ_THROUGH,
            "configuration": CachePolicy.READ_THROUGH,
            "workflow": CachePolicy.READ_THROUGH,
        }
        self._ttls: Dict[str, int] = {
            "provider_capabilities": 900,
            "provider_routing": 900,
            "provider_health": 30,
            "workspace": 600,
            "profile": 1800,
            "runtime_statistics": 60,
            "configuration": 3600,
            "workflow": 600,
        }

    def initialize(self) -> None:
        for sub in list(self._policies.keys()):
            env_policy = os.environ.get(f"CACHE_POLICY_{sub.upper()}")
            if env_policy:
                try:
                    self._policies[sub] = CachePolicy(env_policy)
                except ValueError:
                    pass
            env_ttl = os.environ.get(f"CACHE_TTL_{sub.upper()}")
            if env_ttl:
                try:
                    self._ttls[sub] = int(env_ttl)
                except ValueError:
                    pass

    def start(self) -> None: pass
    def stop(self) -> None: pass

    def get_policy(self, subsystem: str) -> CachePolicy:
        return self._policies.get(subsystem, CachePolicy.READ_THROUGH)

    def get_ttl(self, subsystem: str) -> int:
        return self._ttls.get(subsystem, 60)

    def set_policy(self, subsystem: str, policy: CachePolicy) -> None:
        self._policies[subsystem] = policy

    def set_ttl(self, subsystem: str, ttl: int) -> None:
        self._ttls[subsystem] = ttl


class CacheStatisticsCollectorImpl(CacheStatisticsCollector):
    def __init__(self) -> None:
        self.hits = 0
        self.misses = 0
        self.expirations = 0
        self.invalidations = 0
        self.warmups = 0
        self.rebuilds = 0
        self.latencies: List[float] = []
        self.recommendations: List[Dict[str, Any]] = []
        self.correlation_ids: List[str] = []

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def record_hit(self, subsystem: str, latency_ms: float, correlation_id: Optional[str] = None) -> None:
        self.hits += 1
        self.latencies.append(latency_ms)
        if len(self.latencies) > 1000:
            self.latencies.pop(0)
        if correlation_id and correlation_id not in self.correlation_ids:
            self.correlation_ids.append(correlation_id)
            if len(self.correlation_ids) > 100:
                self.correlation_ids.pop(0)

    def record_miss(self, subsystem: str, latency_ms: float, correlation_id: Optional[str] = None) -> None:
        self.misses += 1
        self.latencies.append(latency_ms)
        if len(self.latencies) > 1000:
            self.latencies.pop(0)
        if correlation_id and correlation_id not in self.correlation_ids:
            self.correlation_ids.append(correlation_id)
            if len(self.correlation_ids) > 100:
                self.correlation_ids.pop(0)

    def record_expiration(self, key: str) -> None:
        self.expirations += 1

    def record_invalidation(self, count: int) -> None:
        self.invalidations += count

    def record_warmup(self, key_count: int) -> None:
        self.warmups += key_count

    def record_rebuild(self, key_count: int) -> None:
        self.rebuilds += key_count

    def record_recommendation(self, rec: Dict[str, Any]) -> None:
        self.recommendations.append({**rec, "timestamp": time.time()})
        if len(self.recommendations) > 100:
            self.recommendations.pop(0)

    def get_metrics(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        hit_ratio = self.hits / total if total > 0 else 1.0
        miss_ratio = self.misses / total if total > 0 else 0.0
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0.0
        return {
            "cache_hits": self.hits,
            "cache_misses": self.misses,
            "hit_ratio": hit_ratio,
            "miss_ratio": miss_ratio,
            "ttl_expirations": self.expirations,
            "invalidations": self.invalidations,
            "warmups": self.warmups,
            "rebuilds": self.rebuilds,
            "average_latency_ms": avg_latency,
            "recommendation_history": self.recommendations,
            "correlation_ids": self.correlation_ids
        }


class CacheDiagnosticsImpl(CacheDiagnostics):
    def __init__(self, provider: RedisProvider) -> None:
        self.provider = provider
        self.errors: List[Dict[str, Any]] = []

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def log_error(self, message: str, severity: str = "ERROR", remediation: str = "Verify cache config") -> None:
        self.errors.append({
            "message": message,
            "severity": severity,
            "remediation": remediation,
            "timestamp": time.time()
        })
        if len(self.errors) > 100:
            self.errors.pop(0)

    def get_diagnostics(self) -> Dict[str, Any]:
        status = "healthy"
        remediations = []
        is_online = False
        try:
            is_online = self.provider.transport.is_connected()
            if is_online:
                transport = self.provider.transport
                if hasattr(transport, "conn_manager") and transport.conn_manager.client:
                    client = transport.conn_manager.client
                    if isinstance(client, FakeRedisClient):
                        is_online = False
        except Exception:
            pass

        if not is_online:
            status = "degraded"
            remediations.append("Redis acceleration is offline. Ephemeral simulated client in use. Performance is degraded, but postgres remains operational.")
        
        criticals = [e for e in self.errors if e["severity"] == "CRITICAL"]
        if criticals:
            status = "critical"

        return {
            "status": status,
            "remediations": remediations,
            "errors": self.errors,
            "redis_connected": is_online
        }


class CacheHealthMonitorImpl(CacheHealthMonitor):
    def __init__(self, provider: RedisProvider) -> None:
        self.provider = provider

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def check_health(self) -> Dict[str, Any]:
        is_online = False
        try:
            is_online = self.provider.transport.is_connected()
            if is_online:
                transport = self.provider.transport
                if hasattr(transport, "conn_manager") and transport.conn_manager.client:
                    client = transport.conn_manager.client
                    if isinstance(client, FakeRedisClient):
                        is_online = False
        except Exception:
            pass
        return {
            "status": "online" if is_online else "degraded",
            "connected": is_online,
            "timestamp": time.time()
        }


class CacheRecommendationEngineImpl(CacheRecommendationEngine):
    def __init__(self, stats: CacheStatisticsCollector, diag: CacheDiagnostics) -> None:
        self.stats = stats
        self.diag = diag

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def get_recommendations(self) -> List[Dict[str, Any]]:
        recs = []
        metrics = self.stats.get_metrics()
        diagnostics = self.diag.get_diagnostics()

        if not diagnostics["redis_connected"]:
            recs.append({
                "category": "Connectivity",
                "issue": "Redis backend is disconnected.",
                "suggestion": "Start Redis server or verify host configuration to enable hardware acceleration.",
                "severity": "WARNING"
            })

        total = metrics["cache_hits"] + metrics["cache_misses"]
        if total > 5 and metrics["hit_ratio"] < 0.2:
            recs.append({
                "category": "Efficiency",
                "issue": f"Cache hit ratio is very low ({metrics['hit_ratio']:.1%}).",
                "suggestion": "Increase configured TTL values or trigger startup warmup to prepopulate cache.",
                "severity": "WARNING"
            })

        if metrics["ttl_expirations"] > 10:
            recs.append({
                "category": "TTL Configuration",
                "issue": f"High number of TTL expirations ({metrics['ttl_expirations']}).",
                "suggestion": "Consider increasing TTL limits for relatively static metadata (e.g. Workspace metadata).",
                "severity": "INFO"
            })

        if not recs:
            recs.append({
                "category": "Maintenance",
                "issue": "Cache is performing optimally.",
                "suggestion": "Keep active settings.",
                "severity": "INFO"
            })

        for r in recs:
            self.stats.record_recommendation(r)

        return recs


class CacheInvalidationManagerImpl(CacheInvalidationManager):
    def __init__(self, provider: RedisProvider, stats: CacheStatisticsCollector) -> None:
        self.provider = provider
        self.stats = stats

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def make_key(self, subsystem: str, entity_id: str) -> str:
        context = RuntimeCorrelationManager.get_context()
        workspace = context.get("workspace_id") or "default_workspace"
        project = context.get("project_id") or "default_project"
        return f"aios:v1:{workspace}:{project}:{subsystem}:{entity_id}:cache"

    def invalidate_key(self, key: str) -> bool:
        try:
            success = self.provider.delete(key)
            if success:
                self.stats.record_invalidation(1)
            return success
        except Exception:
            return False

    def invalidate_entity(self, subsystem: str, entity_id: str) -> bool:
        key = self.make_key(subsystem, entity_id)
        return self.invalidate_key(key)

    def invalidate_workspace(self, workspace_id: str) -> int:
        pattern = f"aios:v1:{workspace_id}:*:*:*:*"
        return self.invalidate_pattern(pattern)

    def invalidate_project(self, project_id: str) -> int:
        pattern = f"aios:v1:*:{project_id}:*:*:*"
        return self.invalidate_pattern(pattern)

    def invalidate_provider(self, provider_name: str) -> int:
        pattern = f"aios:v1:*:*:provider_*:{provider_name}:*"
        return self.invalidate_pattern(pattern)

    def invalidate_pattern(self, pattern: str) -> int:
        count = 0
        try:
            keys = self.provider.transport.execute_command("keys", pattern)
            if keys:
                for k in keys:
                    if self.provider.delete(k):
                        count += 1
        except Exception:
            pass
        if count > 0:
            self.stats.record_invalidation(count)
        return count

    def invalidate_bulk(self, keys: List[str]) -> int:
        count = 0
        for k in keys:
            try:
                if self.provider.delete(k):
                    count += 1
            except Exception:
                pass
        if count > 0:
            self.stats.record_invalidation(count)
        return count


class CacheWarmupServiceImpl(CacheWarmupService):
    def __init__(self, service: PersistenceService, cache_service: RedisCacheService, stats: CacheStatisticsCollector) -> None:
        self.service = service
        self.cache_service = cache_service
        self.stats = stats

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def warmup_all_background(self) -> None:
        import threading
        thread = threading.Thread(target=self._run_warmup, daemon=True)
        thread.start()

    def _run_warmup(self) -> None:
        subsystems = ["workspace", "configuration", "profile", "provider_capabilities", "provider_health", "provider_routing"]
        for sub in subsystems:
            try:
                self.warm_subsystem(sub)
            except Exception:
                pass

    def warm_subsystem(self, subsystem: str) -> None:
        count = 0
        if subsystem == "workspace":
            try:
                rows = self.service.execute("SELECT * FROM workspaces ORDER BY last_accessed DESC LIMIT 5")
                for r in rows:
                    row = dict(r)
                    row["metadata"] = json.loads(row["metadata"] or "{}")
                    self.cache_service.set("workspace", row["id"], row)
                    count += 1
            except Exception:
                pass
        elif subsystem == "profile":
            try:
                rows = self.service.execute("SELECT * FROM engineering_profiles ORDER BY timestamp DESC LIMIT 5")
                for r in rows:
                    row = dict(r)
                    row["coding_standards"] = json.loads(row["coding_standards"] or "[]")
                    row["naming_conventions"] = json.loads(row["naming_conventions"] or "{}")
                    row["release_formatting_rules"] = json.loads(row["release_formatting_rules"] or "{}")
                    row["markdown_preferences"] = json.loads(row["markdown_preferences"] or "{}")
                    row["section_ordering"] = json.loads(row["section_ordering"] or "[]")
                    row["doc_naming_conventions"] = json.loads(row["doc_naming_conventions"] or "{}")
                    row["doc_versioning_preferences"] = json.loads(row["doc_versioning_preferences"] or "{}")
                    row["exclude_patterns"] = json.loads(row["exclude_patterns"] or "[]")
                    row["sandbox_enabled"] = bool(row["sandbox_enabled"])
                    row["generate_api_docs"] = bool(row["generate_api_docs"])
                    row["auto_release"] = bool(row["auto_release"])
                    self.cache_service.set("profile", row["id"], row)
                    count += 1
            except Exception:
                pass
        elif subsystem == "configuration":
            try:
                rows = self.service.execute("SELECT * FROM configuration_profiles LIMIT 5")
                for r in rows:
                    row = dict(r)
                    row["env_profile"] = json.loads(row["env_profile"] or "{}")
                    row["workspace_settings"] = json.loads(row["workspace_settings"] or "{}")
                    row["provider_preferences"] = json.loads(row["provider_preferences"] or "{}")
                    row["git_preferences"] = json.loads(row["git_preferences"] or "{}")
                    row["automation_preferences"] = json.loads(row["automation_preferences"] or "{}")
                    row["documentation_preferences"] = json.loads(row["documentation_preferences"] or "{}")
                    row["testing_preferences"] = json.loads(row["testing_preferences"] or "{}")
                    row["approval_preferences"] = json.loads(row["approval_preferences"] or "{}")
                    self.cache_service.set("configuration", row["id"], row)
                    count += 1
            except Exception:
                pass
        elif subsystem == "provider_capabilities":
            try:
                rows = self.service.execute("SELECT * FROM provider_capabilities ORDER BY timestamp DESC LIMIT 5")
                for r in rows:
                    row = dict(r)
                    row["capabilities"] = json.loads(row["capabilities"] or "{}")
                    res = PersistenceResult(status=PersistenceStatus.SUCCESS, message="Capabilities retrieved.", provider=self.service.config.provider_name, latency=0.0, repository="provider_capabilities", payload=row)
                    self.cache_service.set("provider_capabilities", row["id"], res)
                    count += 1
            except Exception:
                pass
        elif subsystem == "provider_health":
            try:
                rows = self.service.execute("SELECT * FROM provider_health ORDER BY timestamp DESC LIMIT 5")
                for r in rows:
                    row = dict(r)
                    row["is_healthy"] = bool(row["is_healthy"])
                    res = PersistenceResult(status=PersistenceStatus.SUCCESS, message="Health report retrieved.", provider=self.service.config.provider_name, latency=0.0, repository="provider_health", payload=row)
                    self.cache_service.set("provider_health", row["id"], res)
                    count += 1
            except Exception:
                pass
        elif subsystem == "provider_routing":
            try:
                rows = self.service.execute("SELECT * FROM provider_routing ORDER BY timestamp DESC LIMIT 5")
                for r in rows:
                    row = dict(r)
                    row["routing_candidates"] = json.loads(row["routing_candidates"] or "[]")
                    res = PersistenceResult(status=PersistenceStatus.SUCCESS, message="Routing decision retrieved.", provider=self.service.config.provider_name, latency=0.0, repository="provider_routing", payload=row)
                    self.cache_service.set("provider_routing", row["id"], res)
                    count += 1
            except Exception:
                pass

        if count > 0:
            self.stats.record_warmup(count)


class CacheRebuildServiceImpl(CacheRebuildService):
    def __init__(self, service: PersistenceService, provider: RedisProvider, stats: CacheStatisticsCollector, warmup_svc: CacheWarmupService) -> None:
        self.service = service
        self.provider = provider
        self.stats = stats
        self.warmup_svc = warmup_svc
        self._rebuilding = False

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def trigger_rebuild_background(self) -> None:
        if self._rebuilding:
            return
        import threading
        thread = threading.Thread(target=self._run_rebuild, daemon=True)
        thread.start()

    def _run_rebuild(self) -> None:
        self._rebuilding = True
        try:
            try:
                self.provider.transport.connect()
            except Exception:
                pass

            if self.provider.transport.is_connected():
                self.rebuild_incremental()
        finally:
            self._rebuilding = False

    def rebuild_incremental(self) -> int:
        initial_warmups = self.stats.warmups
        self.warmup_svc.warm_subsystem("workspace")
        self.warmup_svc.warm_subsystem("profile")
        self.warmup_svc.warm_subsystem("configuration")
        self.warmup_svc.warm_subsystem("provider_capabilities")
        self.warmup_svc.warm_subsystem("provider_health")
        self.warmup_svc.warm_subsystem("provider_routing")
        
        rebuilt_keys = self.stats.warmups - initial_warmups
        if rebuilt_keys > 0:
            self.stats.record_rebuild(rebuilt_keys)
        return rebuilt_keys


class RedisCacheServiceImpl(RedisCacheService):
    def __init__(
        self,
        provider: RedisProvider,
        policy_mgr: CachePolicyManager,
        stats: CacheStatisticsCollector,
        diag: CacheDiagnostics,
    ) -> None:
        self.provider = provider
        self.policy_mgr = policy_mgr
        self.stats = stats
        self.diag = diag
        self._disabled = False

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def make_key(self, subsystem: str, entity_id: str) -> str:
        context = RuntimeCorrelationManager.get_context()
        workspace = context.get("workspace_id") or "default_workspace"
        project = context.get("project_id") or "default_project"
        return f"aios:v1:{workspace}:{project}:{subsystem}:{entity_id}:cache"

    def get(
        self,
        subsystem: str,
        entity_id: str,
        fetch_func: Callable[[], Any],
        policy: Optional[CachePolicy] = None,
        ttl: Optional[int] = None
    ) -> Any:
        start_time = time.time()
        active_policy = policy if policy is not None else self.policy_mgr.get_policy(subsystem)
        active_ttl = ttl if ttl is not None else self.policy_mgr.get_ttl(subsystem)

        if active_policy == CachePolicy.NO_CACHE or self._disabled:
            return fetch_func()

        key = self.make_key(subsystem, entity_id)
        context = RuntimeCorrelationManager.get_context()
        corr_id = context.get("correlation_id")

        try:
            cached_val = self.provider.get(key)
            if cached_val is not None:
                latency_ms = (time.time() - start_time) * 1000.0
                self.stats.record_hit(subsystem, latency_ms, corr_id)
                return deserialize_val(cached_val)
        except Exception as e:
            self.diag.log_error(f"Cache get error: {str(e)}", severity="ERROR", remediation="Verify Redis connection")

        latency_ms = (time.time() - start_time) * 1000.0
        self.stats.record_miss(subsystem, latency_ms, corr_id)

        db_val = fetch_func()

        if db_val is not None and (active_policy == CachePolicy.READ_THROUGH or active_policy == CachePolicy.CACHE_ASIDE):
            try:
                self.provider.set(key, serialize_val(db_val), ttl=active_ttl)
            except Exception as e:
                self.diag.log_error(f"Cache set error: {str(e)}", severity="ERROR", remediation="Verify Redis connection")

        return db_val

    def set(
        self,
        subsystem: str,
        entity_id: str,
        value: Any,
        policy: Optional[CachePolicy] = None,
        ttl: Optional[int] = None
    ) -> bool:
        active_policy = policy if policy is not None else self.policy_mgr.get_policy(subsystem)
        active_ttl = ttl if ttl is not None else self.policy_mgr.get_ttl(subsystem)

        if active_policy == CachePolicy.NO_CACHE or self._disabled:
            return False

        key = self.make_key(subsystem, entity_id)

        try:
            success = self.provider.set(key, serialize_val(value), ttl=active_ttl)
            return success
        except Exception as e:
            self.diag.log_error(f"Cache set error: {str(e)}", severity="ERROR", remediation="Verify Redis connection")
            return False

    def delete(self, subsystem: str, entity_id: str) -> bool:
        key = self.make_key(subsystem, entity_id)
        try:
            return self.provider.delete(key)
        except Exception as e:
            self.diag.log_error(f"Cache delete error: {str(e)}", severity="ERROR", remediation="Verify Redis connection")
            return False


class SessionRegistryImpl(SessionRegistry):
    def __init__(self) -> None:
        self.configs: Dict[str, Dict[str, Any]] = {}

    def initialize(self) -> None:
        self.register_session_type(
            "ai", "AIService", 3600.0, SessionPolicy.EPHEMERAL, "none", "ai", heartbeat_required=True
        )
        self.register_session_type(
            "workspace", "WorkspaceService", 86400.0, SessionPolicy.PERSISTENT_REFERENCE, "reconstruct_from_db", "workspace", "workspaces", heartbeat_required=False
        )
        self.register_session_type(
            "workflow", "WorkflowService", 7200.0, SessionPolicy.RECOVERABLE, "reconstruct_from_db", "workflow", "workflow_executions", heartbeat_required=True
        )
        self.register_session_type(
            "provider", "ProviderService", 1800.0, SessionPolicy.EPHEMERAL, "none", "provider", heartbeat_required=True
        )
        self.register_session_type(
            "engineering", "EngineeringProfileService", 14400.0, SessionPolicy.PERSISTENT_REFERENCE, "reconstruct_from_db", "engineering", "engineering_profiles", heartbeat_required=False
        )
        self.register_session_type(
            "automation", "AutomationService", 3600.0, SessionPolicy.RECOVERABLE, "reconstruct_from_db", "automation", "automation_telemetry", heartbeat_required=True
        )
        self.register_session_type(
            "temporary_execution", "ExecutionService", 900.0, SessionPolicy.EPHEMERAL, "none", "temp_exec", heartbeat_required=False
        )
        self.register_session_type(
            "runtime_validation", "ValidationService", 600.0, SessionPolicy.EPHEMERAL, "none", "validation", heartbeat_required=False
        )

    def start(self) -> None: pass
    def stop(self) -> None: pass

    def register_session_type(
        self,
        session_type: str,
        owner_service: str,
        ttl: float,
        policy: SessionPolicy,
        recovery_strategy: str,
        redis_prefix: str,
        source_of_truth: Optional[str] = None,
        heartbeat_required: bool = False
    ) -> None:
        self.configs[session_type] = {
            "owner_service": owner_service,
            "ttl": ttl,
            "policy": policy,
            "recovery_strategy": recovery_strategy,
            "redis_prefix": redis_prefix,
            "source_of_truth": source_of_truth,
            "heartbeat_required": heartbeat_required
        }

    def get_configuration(self, session_type: str) -> Dict[str, Any]:
        cfg = self.configs.get(session_type)
        if not cfg:
            return {
                "owner_service": "Unknown",
                "ttl": 3600.0,
                "policy": SessionPolicy.EPHEMERAL,
                "recovery_strategy": "none",
                "redis_prefix": session_type,
                "source_of_truth": None,
                "heartbeat_required": False
            }
        return cfg

    def get_all_types(self) -> List[str]:
        return list(self.configs.keys())


class SessionStatisticsCollectorImpl(SessionStatisticsCollector):
    def __init__(self) -> None:
        self.creates: Dict[str, int] = {}
        self.reads: Dict[str, int] = {}
        self.updates: Dict[str, int] = {}
        self.deletes: Dict[str, int] = {}
        self.expirations: Dict[str, int] = {}
        self.renewals: Dict[str, int] = {}
        self.recoveries: Dict[str, int] = {}
        self.recovery_success: Dict[str, int] = {}
        self.heartbeats: Dict[str, int] = {}
        self.latencies: List[float] = []
        self.errors: List[str] = []
        self.recommendations: List[Dict[str, Any]] = []

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def record_create(self, session_type: str, correlation_id: Optional[str] = None) -> None:
        self.creates[session_type] = self.creates.get(session_type, 0) + 1

    def record_read(self, session_type: str, hit: bool, correlation_id: Optional[str] = None) -> None:
        key = f"{session_type}:hit" if hit else f"{session_type}:miss"
        self.reads[key] = self.reads.get(key, 0) + 1

    def record_update(self, session_type: str, correlation_id: Optional[str] = None) -> None:
        self.updates[session_type] = self.updates.get(session_type, 0) + 1

    def record_delete(self, session_type: str, correlation_id: Optional[str] = None) -> None:
        self.deletes[session_type] = self.deletes.get(session_type, 0) + 1

    def record_expire(self, session_type: str, reason: str) -> None:
        key = f"{session_type}:{reason}"
        self.expirations[key] = self.expirations.get(key, 0) + 1

    def record_renew(self, session_type: str, correlation_id: Optional[str] = None) -> None:
        self.renewals[session_type] = self.renewals.get(session_type, 0) + 1

    def record_recovery(self, session_type: str, success: bool) -> None:
        self.recoveries[session_type] = self.recoveries.get(session_type, 0) + 1
        if success:
            self.recovery_success[session_type] = self.recovery_success.get(session_type, 0) + 1

    def record_heartbeat(self, session_type: str) -> None:
        self.heartbeats[session_type] = self.heartbeats.get(session_type, 0) + 1

    def record_latency(self, op: str, latency_ms: float) -> None:
        self.latencies.append(latency_ms)
        if len(self.latencies) > 1000:
            self.latencies.pop(0)

    def get_metrics(self) -> Dict[str, Any]:
        total_latency = sum(self.latencies)
        avg_latency = total_latency / len(self.latencies) if self.latencies else 0.0
        
        return {
            "session_creates": self.creates,
            "session_reads": self.reads,
            "session_updates": self.updates,
            "session_deletes": self.deletes,
            "session_expirations": self.expirations,
            "session_renewals": self.renewals,
            "session_recoveries": self.recoveries,
            "session_recovery_success": self.recovery_success,
            "session_heartbeats": self.heartbeats,
            "average_latency_ms": avg_latency,
            "recommendation_count": len(self.recommendations),
            "learning_metadata": {
                "session_duration_trends": "stable",
                "recovery_trends": "high_success",
                "expiration_trends": "normal",
                "heartbeat_statistics": "regular"
            }
        }


class SessionDiagnosticsImpl(SessionDiagnostics):
    def __init__(self, provider: RedisProvider) -> None:
        self.provider = provider
        self.errors: List[Dict[str, Any]] = []

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def get_diagnostics(self) -> Dict[str, Any]:
        is_fake = "FakeRedisClient" in str(type(getattr(self.provider.transport, "client", None))) if hasattr(self.provider, "transport") else True
        
        try:
            ping_res = self.provider.transport.execute_command("ping") if hasattr(self.provider, "transport") else False
            ping_ok = (ping_res is True or ping_res == "PONG" or ping_res == b"PONG")
        except Exception:
            ping_ok = False

        status = "degraded" if (is_fake or not ping_ok) else "healthy"
        if not ping_ok:
            status = "unhealthy"

        return {
            "status": status,
            "connection_alive": ping_ok,
            "using_simulated_client": is_fake,
            "diagnosed_errors": self.errors[-100:],
            "active_issues": len(self.errors)
        }

    def log_error(self, message: str, severity: str = "ERROR", remediation: str = "Verify session configuration") -> None:
        self.errors.append({
            "timestamp": time.time(),
            "message": message,
            "severity": severity,
            "remediation": remediation
        })


class SessionHealthMonitorImpl(SessionHealthMonitor):
    def __init__(self, provider: RedisProvider) -> None:
        self.provider = provider

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def check_health(self) -> Dict[str, Any]:
        is_fake = "FakeRedisClient" in str(type(getattr(self.provider.transport, "client", None))) if hasattr(self.provider, "transport") else True
        try:
            ping_res = self.provider.transport.execute_command("ping") if hasattr(self.provider, "transport") else False
            ping_ok = (ping_res is True or ping_res == "PONG" or ping_res == b"PONG")
            latency = 1.0
        except Exception as e:
            ping_ok = False
            latency = 0.0

        status = "healthy"
        if not ping_ok:
            status = "unhealthy"
        elif is_fake:
            status = "degraded"

        return {
            "status": status,
            "latency_ms": latency,
            "provider": "redis",
            "is_alive": ping_ok
        }


class SessionRecommendationEngineImpl(SessionRecommendationEngine):
    def __init__(self, stats: SessionStatisticsCollector, diag: SessionDiagnostics) -> None:
        self.stats = stats
        self.diag = diag

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def get_recommendations(self) -> List[Dict[str, Any]]:
        recs = []
        diag_info = self.diag.get_diagnostics()
        if diag_info["status"] == "degraded":
            recs.append({
                "category": "Connectivity",
                "recommendation": "Migrate from simulated FakeRedisClient to a live Redis cluster.",
                "priority": "HIGH"
            })
        
        metrics = self.stats.get_metrics()
        total_expirations = sum(metrics["session_expirations"].values())
        if total_expirations > 50:
            recs.append({
                "category": "TTL Configuration",
                "recommendation": "Consider extending the session TTL for frequently expiring subsystems.",
                "priority": "MEDIUM"
            })

        if not recs:
            recs.append({
                "category": "Maintenance",
                "recommendation": "Session platform configuration is running optimally.",
                "priority": "LOW"
            })
        return recs


class SessionStoreImpl(SessionStore):
    def __init__(
        self,
        provider: RedisProvider,
        registry: SessionRegistry,
        stats: SessionStatisticsCollector,
        diag: SessionDiagnostics
    ) -> None:
        self.provider = provider
        self.registry = registry
        self.stats = stats
        self.diag = diag
        self._disabled = False
        self._fallback_store: Dict[str, Dict[str, Any]] = {}

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def make_key(self, workspace_id: Optional[str], project_id: Optional[str], session_type: str, session_id: str) -> str:
        ws = workspace_id or "default"
        proj = project_id or "default"
        return f"aios:v1:{ws}:{proj}:session:{session_type}:{session_id}"

    def create(
        self,
        session_type: str,
        session_id: str,
        data: Dict[str, Any],
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> bool:
        start_time = time.time()
        cfg = self.registry.get_configuration(session_type)
        ttl = cfg["ttl"]
        
        session_payload = {
            "workspace_id": workspace_id or "default",
            "project_id": project_id or "default",
            "session_type": session_type,
            "creation_time": start_time,
            "last_access_time": start_time,
            "ttl": ttl,
            "version": 1,
            "data": data
        }

        key = self.make_key(workspace_id, project_id, session_type, session_id)
        
        self.stats.record_create(session_type)

        if self._disabled:
            expiration = start_time + ttl
            self._fallback_store[key] = {
                "payload": session_payload,
                "expiration": expiration
            }
            self.stats.record_latency("create", (time.time() - start_time) * 1000)
            return True

        try:
            success = self.provider.set(key, serialize_val(session_payload), ttl=int(ttl))
        except Exception as e:
            success = False
            self.diag.log_error(f"Session write failure: {str(e)}")

        if not success:
            expiration = start_time + ttl
            self._fallback_store[key] = {
                "payload": session_payload,
                "expiration": expiration
            }
            self.stats.record_latency("create", (time.time() - start_time) * 1000)
            return True

        self.stats.record_latency("create", (time.time() - start_time) * 1000)
        return True


    def read(self, session_type: str, session_id: str) -> Optional[Dict[str, Any]]:
        pattern = f"aios:v1:*:*:session:{session_type}:{session_id}"
        start_time = time.time()
        
        for key, val in list(self._fallback_store.items()):
            import fnmatch
            if fnmatch.fnmatch(key, pattern):
                if time.time() - val["payload"].get("creation_time", 0) > 604800.0:
                    del self._fallback_store[key]
                    self.stats.record_expire(session_type, "max_lifetime")
                    continue
                if time.time() > val["expiration"]:
                    del self._fallback_store[key]
                    self.stats.record_expire(session_type, "idle_timeout")
                    continue
                val["payload"]["last_access_time"] = time.time()
                cfg = self.registry.get_configuration(session_type)
                val["expiration"] = time.time() + cfg["ttl"]
                self.stats.record_read(session_type, hit=True)
                self.stats.record_latency("read", (time.time() - start_time) * 1000)
                return val["payload"]["data"]

        if self._disabled:
            self.stats.record_read(session_type, hit=False)
            return None

        try:
            keys = self.provider.transport.execute_command("keys", pattern)
            if not keys:
                self.stats.record_read(session_type, hit=False)
                return None
            
            key = keys[0]
            raw = self.provider.get(key)
            if raw is None:
                self.stats.record_read(session_type, hit=False)
                return None

            payload = deserialize_val(raw)
            if time.time() - payload.get("creation_time", 0) > 604800.0:
                self.provider.delete(key)
                self.stats.record_expire(session_type, "max_lifetime")
                self.stats.record_read(session_type, hit=False)
                return None

            payload["last_access_time"] = time.time()
            cfg = self.registry.get_configuration(session_type)
            self.provider.set(key, serialize_val(payload), ttl=int(cfg["ttl"]))
            
            self.stats.record_read(session_type, hit=True)
            self.stats.record_latency("read", (time.time() - start_time) * 1000)
            return payload["data"]
        except Exception as e:
            self.diag.log_error(f"Session read failure: {str(e)}")
            self.stats.record_read(session_type, hit=False)
            return None

    def update(self, session_type: str, session_id: str, data: Dict[str, Any]) -> bool:
        pattern = f"aios:v1:*:*:session:{session_type}:{session_id}"
        start_time = time.time()
        self.stats.record_update(session_type)

        for key, val in list(self._fallback_store.items()):
            import fnmatch
            if fnmatch.fnmatch(key, pattern):
                if time.time() > val["expiration"]:
                    del self._fallback_store[key]
                    self.stats.record_expire(session_type, "idle_timeout")
                    continue
                val["payload"]["data"] = data
                val["payload"]["last_access_time"] = time.time()
                cfg = self.registry.get_configuration(session_type)
                val["expiration"] = time.time() + cfg["ttl"]
                self.stats.record_latency("update", (time.time() - start_time) * 1000)
                return True

        if self._disabled:
            return False

        try:
            keys = self.provider.transport.execute_command("keys", pattern)
            if not keys:
                return False
            key = keys[0]
            raw = self.provider.get(key)
            if raw is None:
                return False
            payload = deserialize_val(raw)
            payload["data"] = data
            payload["last_access_time"] = time.time()
            cfg = self.registry.get_configuration(session_type)
            success = self.provider.set(key, serialize_val(payload), ttl=int(cfg["ttl"]))
            self.stats.record_latency("update", (time.time() - start_time) * 1000)
            return success
        except Exception as e:
            self.diag.log_error(f"Session update failure: {str(e)}")
            return False

    def delete(self, session_type: str, session_id: str) -> bool:
        pattern = f"aios:v1:*:*:session:{session_type}:{session_id}"
        start_time = time.time()
        self.stats.record_delete(session_type)

        deleted = False
        for key in list(self._fallback_store.keys()):
            import fnmatch
            if fnmatch.fnmatch(key, pattern):
                del self._fallback_store[key]
                deleted = True

        if self._disabled:
            return deleted

        try:
            keys = self.provider.transport.execute_command("keys", pattern)
            if not keys:
                return deleted
            for key in keys:
                self.provider.delete(key)
                deleted = True
            self.stats.record_latency("delete", (time.time() - start_time) * 1000)
            return deleted
        except Exception as e:
            self.diag.log_error(f"Session delete failure: {str(e)}")
            return deleted

    def renew(self, session_type: str, session_id: str) -> bool:
        pattern = f"aios:v1:*:*:session:{session_type}:{session_id}"
        start_time = time.time()
        self.stats.record_renew(session_type)

        renewed = False
        for key, val in list(self._fallback_store.items()):
            import fnmatch
            if fnmatch.fnmatch(key, pattern):
                cfg = self.registry.get_configuration(session_type)
                val["expiration"] = time.time() + cfg["ttl"]
                val["payload"]["last_access_time"] = time.time()
                renewed = True

        if self._disabled:
            return renewed

        try:
            keys = self.provider.transport.execute_command("keys", pattern)
            if not keys:
                return renewed
            for key in keys:
                raw = self.provider.get(key)
                if raw is not None:
                    payload = deserialize_val(raw)
                    payload["last_access_time"] = time.time()
                    cfg = self.registry.get_configuration(session_type)
                    self.provider.set(key, serialize_val(payload), ttl=int(cfg["ttl"]))
                    renewed = True
            self.stats.record_latency("renew", (time.time() - start_time) * 1000)
            return renewed
        except Exception as e:
            self.diag.log_error(f"Session renew failure: {str(e)}")
            return renewed

    def heartbeat(self, session_type: str, session_id: str) -> bool:
        self.stats.record_heartbeat(session_type)
        return self.renew(session_type, session_id)


class SessionExpirationManagerImpl(SessionExpirationManager):
    def __init__(self, store: SessionStore, registry: SessionRegistry) -> None:
        self.store = store
        self.registry = registry

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def check_expirations(self) -> List[str]:
        return []

    def expire_session(self, session_id: str, reason: str) -> None:
        pass


class SessionRecoveryManagerImpl(SessionRecoveryManager):
    def __init__(self, p_service: PersistenceService, provider: RedisProvider, stats: SessionStatisticsCollector) -> None:
        self.p_service = p_service
        self.provider = provider
        self.stats = stats
        self.handlers: Dict[str, Callable[[str], Optional[Dict[str, Any]]]] = {}

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def register_recovery_handler(
        self,
        session_type: str,
        handler: Callable[[str], Optional[Dict[str, Any]]]
    ) -> None:
        self.handlers[session_type] = handler

    def recover_session(self, session_type: str, session_id: str) -> Optional[Dict[str, Any]]:
        handler = self.handlers.get(session_type)
        if not handler:
            self.stats.record_recovery(session_type, success=False)
            return None
        try:
            data = handler(session_id)
            if data is not None:
                self.stats.record_recovery(session_type, success=True)
                return data
        except Exception:
            pass
        self.stats.record_recovery(session_type, success=False)
        return None

    def trigger_rebuild_incremental(self) -> int:
        return 0


class SessionManagerImpl(SessionManager):
    def __init__(
        self,
        store: SessionStore,
        recovery: SessionRecoveryManager,
        registry: SessionRegistry,
        stats: SessionStatisticsCollector
    ) -> None:
        self.store = store
        self.recovery = recovery
        self.registry = registry
        self.stats = stats

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def create_session(
        self,
        session_type: str,
        session_id: str,
        data: Dict[str, Any],
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> bool:
        return self.store.create(session_type, session_id, data, workspace_id, project_id)

    def get_session(self, session_type: str, session_id: str) -> Optional[Dict[str, Any]]:
        data = self.store.read(session_type, session_id)
        if data is not None:
            return data

        cfg = self.registry.get_configuration(session_type)
        if cfg["policy"] in (SessionPolicy.RECOVERABLE, SessionPolicy.PERSISTENT_REFERENCE):
            recovered = self.recovery.recover_session(session_type, session_id)
            if recovered is not None:
                self.store.create(session_type, session_id, recovered)
                return recovered
        return None

    def update_session(self, session_type: str, session_id: str, data: Dict[str, Any]) -> bool:
        return self.store.update(session_type, session_id, data)

    def delete_session(self, session_type: str, session_id: str) -> bool:
        return self.store.delete(session_type, session_id)

    def renew_session(self, session_type: str, session_id: str) -> bool:
        return self.store.renew(session_type, session_id)

    def heartbeat(self, session_type: str, session_id: str) -> bool:
        return self.store.heartbeat(session_type, session_id)


class RedisSessionServiceImpl(RedisSessionService):
    def __init__(
        self,
        provider: RedisProvider,
        registry: SessionRegistry,
        store: SessionStore,
        manager: SessionManager,
        stats: SessionStatisticsCollector,
        diag: SessionDiagnostics
    ) -> None:
        self.provider = provider
        self.registry = registry
        self.store = store
        self.manager = manager
        self.stats = stats
        self.diag = diag

    def initialize(self) -> None: pass
    def start(self) -> None: pass
    def stop(self) -> None: pass

    def get_manager(self) -> SessionManager:
        return self.manager

    def get_registry(self) -> SessionRegistry:
        return self.registry

    def get_store(self) -> SessionStore:
        return self.store






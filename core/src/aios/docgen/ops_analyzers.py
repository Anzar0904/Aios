"""
ops_analyzers.py — Analyzers for extracting operational information.

Static analyzers that extract deployment requirements, configuration parameters,
startup sequences, and operational metadata from the codebase.

All analyzers derive facts directly from implementation files so that generated
guides stay in sync with actual runtime behavior.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

from aios.docgen.ops_models import (
    BackupTarget,
    ConfigurationItem,
    MonitoringMetric,
    OmniRouteProvider,
    ServiceDeployment,
    StartupStep,
    TroubleshootingEntry,
)


class ServiceDeploymentAnalyzer:
    """Analyzes service deployment requirements."""

    def analyze(self, project_root: Path) -> List[ServiceDeployment]:
        """Extract service deployment requirements."""
        deployments = [
            # Internal services
            ServiceDeployment(
                name="AIOS Core",
                type="internal",
                required=True,
                config_keys=["AIOS_HOME", "AIOS_LOG_LEVEL"],
                dependencies=[],
            ),
            # External services — ordered by bootstrap sequence
            ServiceDeployment(
                name="PostgreSQL",
                type="external",
                port=5432,
                required=True,
                config_keys=[
                    "POSTGRES_HOST",
                    "POSTGRES_PORT",
                    "POSTGRES_DATABASE",
                    "POSTGRES_USER",
                    "POSTGRES_PASSWORD",
                    "POSTGRES_SSLMODE",
                    "POSTGRES_CONNECT_TIMEOUT",
                ],
                dependencies=[],
            ),
            ServiceDeployment(
                name="Redis",
                type="external",
                port=6379,
                required=True,
                config_keys=[
                    "REDIS_HOST",
                    "REDIS_PORT",
                    "REDIS_USERNAME",
                    "REDIS_PASSWORD",
                    "REDIS_DATABASE",
                    "REDIS_TLS",
                    "REDIS_TIMEOUT",
                ],
                dependencies=[],
            ),
            ServiceDeployment(
                name="Qdrant",
                type="external",
                port=6333,
                required=True,
                config_keys=[
                    "QDRANT_HOST",
                    "QDRANT_PORT",
                    "QDRANT_GRPC_PORT",
                    "QDRANT_API_KEY",
                    "QDRANT_HTTPS",
                    "QDRANT_TIMEOUT",
                    "QDRANT_RETRY_COUNT",
                    "QDRANT_DEFAULT_DIMENSIONS",
                    "QDRANT_DEFAULT_DISTANCE",
                ],
                dependencies=[],
            ),
            ServiceDeployment(
                name="n8n",
                type="external",
                port=5678,
                required=False,
                config_keys=[
                    "N8N_SERVER_URL",
                    "N8N_API_KEY",
                    "N8N_EMAIL",
                    "N8N_PASSWORD",
                    "N8N_BEARER_TOKEN",
                ],
                dependencies=[],
            ),
        ]
        return deployments


class ConfigurationAnalyzer:
    """Analyzes configuration parameters from the actual implementation."""

    def analyze(self, project_root: Path) -> List[ConfigurationItem]:
        """Extract configuration parameters aligned with implementation."""
        configs = [
            # ── Core ──────────────────────────────────────────────────────────
            ConfigurationItem(
                key="AIOS_HOME",
                description="Root directory for AIOS installation",
                default=None,
                required=True,
                env_var="AIOS_HOME",
                example="/opt/aios",
                section="core",
            ),
            ConfigurationItem(
                key="AIOS_LOG_LEVEL",
                description="Logging level for the application",
                default="INFO",
                required=False,
                env_var="AIOS_LOG_LEVEL",
                example="DEBUG",
                section="core",
            ),
            # ── PostgreSQL ───────────────────────────────────────────────────
            # Sourced from: core/src/aios/services/persistence.py
            ConfigurationItem(
                key="POSTGRES_HOST",
                description="PostgreSQL server hostname",
                default="localhost",
                required=True,
                env_var="POSTGRES_HOST",
                example="postgres.example.com",
                section="postgres",
            ),
            ConfigurationItem(
                key="POSTGRES_PORT",
                description="PostgreSQL server port",
                default="5432",
                required=True,
                env_var="POSTGRES_PORT",
                example="5432",
                section="postgres",
            ),
            ConfigurationItem(
                key="POSTGRES_DATABASE",
                description="PostgreSQL database name (also accepted as POSTGRES_DB)",
                default="aios",
                required=True,
                env_var="POSTGRES_DATABASE",
                example="aios_production",
                section="postgres",
            ),
            ConfigurationItem(
                key="POSTGRES_USER",
                description="PostgreSQL username",
                default=None,
                required=True,
                env_var="POSTGRES_USER",
                example="aios_user",
                section="postgres",
            ),
            ConfigurationItem(
                key="POSTGRES_PASSWORD",
                description="PostgreSQL password (store securely, never commit)",
                default=None,
                required=True,
                env_var="POSTGRES_PASSWORD",
                example="<secure-password>",
                section="postgres",
            ),
            ConfigurationItem(
                key="POSTGRES_SSLMODE",
                description="PostgreSQL SSL connection mode",
                default="prefer",
                required=False,
                env_var="POSTGRES_SSLMODE",
                example="require",
                section="postgres",
            ),
            ConfigurationItem(
                key="POSTGRES_CONNECT_TIMEOUT",
                description="PostgreSQL connection timeout in seconds",
                default="5",
                required=False,
                env_var="POSTGRES_CONNECT_TIMEOUT",
                example="10",
                section="postgres",
            ),
            # ── Redis ─────────────────────────────────────────────────────────
            # Sourced from: core/src/aios/services/persistence_impl_modules/redis.py
            ConfigurationItem(
                key="REDIS_HOST",
                description="Redis server hostname",
                default="localhost",
                required=True,
                env_var="REDIS_HOST",
                example="redis.example.com",
                section="redis",
            ),
            ConfigurationItem(
                key="REDIS_PORT",
                description="Redis server port",
                default="6379",
                required=True,
                env_var="REDIS_PORT",
                example="6379",
                section="redis",
            ),
            ConfigurationItem(
                key="REDIS_USERNAME",
                description="Redis username (Redis 6+ ACL authentication)",
                default=None,
                required=False,
                env_var="REDIS_USERNAME",
                example="aios_redis_user",
                section="redis",
            ),
            ConfigurationItem(
                key="REDIS_PASSWORD",
                description="Redis password for authentication (store securely)",
                default=None,
                required=False,
                env_var="REDIS_PASSWORD",
                example="<redis-password>",
                section="redis",
            ),
            ConfigurationItem(
                key="REDIS_DATABASE",
                description="Redis logical database index (0–15)",
                default="0",
                required=False,
                env_var="REDIS_DATABASE",
                example="0",
                section="redis",
            ),
            ConfigurationItem(
                key="REDIS_TLS",
                description="Enable TLS/SSL for Redis connection",
                default="false",
                required=False,
                env_var="REDIS_TLS",
                example="true",
                section="redis",
            ),
            ConfigurationItem(
                key="REDIS_TIMEOUT",
                description="Redis connection timeout in seconds",
                default="2.0",
                required=False,
                env_var="REDIS_TIMEOUT",
                example="5.0",
                section="redis",
            ),
            # ── Qdrant ────────────────────────────────────────────────────────
            # Sourced from: core/src/aios/services/persistence_impl_modules/qdrant.py
            ConfigurationItem(
                key="QDRANT_HOST",
                description="Qdrant vector database hostname",
                default="127.0.0.1",
                required=True,
                env_var="QDRANT_HOST",
                example="qdrant.example.com",
                section="qdrant",
            ),
            ConfigurationItem(
                key="QDRANT_PORT",
                description="Qdrant HTTP/REST API port",
                default="6333",
                required=True,
                env_var="QDRANT_PORT",
                example="6333",
                section="qdrant",
            ),
            ConfigurationItem(
                key="QDRANT_GRPC_PORT",
                description="Qdrant gRPC port for high-throughput vector operations",
                default="6334",
                required=False,
                env_var="QDRANT_GRPC_PORT",
                example="6334",
                section="qdrant",
            ),
            ConfigurationItem(
                key="QDRANT_API_KEY",
                description="Qdrant API key for authentication (cloud or secured deployments)",
                default=None,
                required=False,
                env_var="QDRANT_API_KEY",
                example="<qdrant-api-key>",
                section="qdrant",
            ),
            ConfigurationItem(
                key="QDRANT_HTTPS",
                description="Enable HTTPS for Qdrant connection",
                default="false",
                required=False,
                env_var="QDRANT_HTTPS",
                example="true",
                section="qdrant",
            ),
            ConfigurationItem(
                key="QDRANT_TIMEOUT",
                description="Qdrant operation timeout in seconds",
                default="5.0",
                required=False,
                env_var="QDRANT_TIMEOUT",
                example="10.0",
                section="qdrant",
            ),
            ConfigurationItem(
                key="QDRANT_RETRY_COUNT",
                description="Number of retries for failed Qdrant operations",
                default="3",
                required=False,
                env_var="QDRANT_RETRY_COUNT",
                example="5",
                section="qdrant",
            ),
            ConfigurationItem(
                key="QDRANT_DEFAULT_DIMENSIONS",
                description="Default vector embedding dimension size",
                default="1536",
                required=False,
                env_var="QDRANT_DEFAULT_DIMENSIONS",
                example="1536",
                section="qdrant",
            ),
            ConfigurationItem(
                key="QDRANT_DEFAULT_DISTANCE",
                description="Default vector similarity metric (COSINE, DOT, EUCLID)",
                default="cosine",
                required=False,
                env_var="QDRANT_DEFAULT_DISTANCE",
                example="COSINE",
                section="qdrant",
            ),
            # ── n8n (optional) ───────────────────────────────────────────────
            # Sourced from: core/src/aios/n8n/service.py
            ConfigurationItem(
                key="N8N_SERVER_URL",
                description="URL of the self-hosted n8n server",
                default="http://localhost:5678",
                required=False,
                env_var="N8N_SERVER_URL",
                example="http://localhost:5678",
                section="n8n",
            ),
            ConfigurationItem(
                key="N8N_API_KEY",
                description="n8n API key for API authentication (preferred over email/password)",
                default=None,
                required=False,
                env_var="N8N_API_KEY",
                example="<n8n-api-key>",
                section="n8n",
            ),
            ConfigurationItem(
                key="N8N_EMAIL",
                description="n8n admin email for session-based authentication",
                default=None,
                required=False,
                env_var="N8N_EMAIL",
                example="admin@example.com",
                section="n8n",
            ),
            ConfigurationItem(
                key="N8N_PASSWORD",
                description="n8n admin password for session-based authentication (store securely)",
                default=None,
                required=False,
                env_var="N8N_PASSWORD",
                example="<n8n-password>",
                section="n8n",
            ),
            ConfigurationItem(
                key="N8N_BEARER_TOKEN",
                description="n8n bearer token for stateless authentication",
                default=None,
                required=False,
                env_var="N8N_BEARER_TOKEN",
                example="<bearer-token>",
                section="n8n",
            ),
            # ── OmniRoute / AI Providers ─────────────────────────────────────
            # Sourced from: core/src/aios/services/model_impl.py, providers/registry.py
            ConfigurationItem(
                key="OPENROUTER_API_KEY",
                description="OpenRouter API key for multi-model routing via OmniRoute",
                default=None,
                required=False,
                env_var="OPENROUTER_API_KEY",
                example="sk-or-...",
                section="omniroute",
            ),
            ConfigurationItem(
                key="ANTHROPIC_API_KEY",
                description="Anthropic Claude API key (also accepted as CLAUDE_CODE_API_KEY)",
                default=None,
                required=False,
                env_var="ANTHROPIC_API_KEY",
                example="sk-ant-...",
                section="omniroute",
            ),
            ConfigurationItem(
                key="GEMINI_API_KEY",
                description="Google Gemini API key",
                default=None,
                required=False,
                env_var="GEMINI_API_KEY",
                example="AIza...",
                section="omniroute",
            ),
        ]
        return configs


class StartupSequenceAnalyzer:
    """
    Analyzes service startup order from the bootstrap_kernel composition root.

    The bootstrap sequence is derived from:
        core/src/aios/bootstrap_modules/bootstrap_kernel.py

    Order:
      1. PostgreSQL   — required by PersistenceBootstrapper (step 3 of bootstrap)
      2. Redis        — required by RedisRuntimeService (step 4 of bootstrap)
      3. Qdrant       — required by QdrantPlatform (step 5 of bootstrap)
      4. DB Migration — run once PostgreSQL is ready (PersistenceBootstrapper.on_ready)
      5. AIOS Core    — starts after all external services (step 6)
      6. n8n          — optional; registered as step 8 of bootstrap
    """

    def analyze(self) -> List[StartupStep]:
        """Extract service startup sequence aligned with bootstrap_kernel.py."""
        steps = [
            StartupStep(
                order=1,
                service="PostgreSQL",
                command="docker-compose up -d postgres",
                description="Start PostgreSQL database server (required by Persistence Platform)",
                wait_for=[],
                healthcheck="psql -U $POSTGRES_USER -d $POSTGRES_DATABASE -c 'SELECT 1;'",
                notes=(
                    "The AIOS Persistence Platform connects to PostgreSQL immediately on startup. "
                    "Ensure POSTGRES_HOST, POSTGRES_USER, POSTGRES_PASSWORD, and "
                    "POSTGRES_DATABASE are set before starting AIOS Core."
                ),
            ),
            StartupStep(
                order=2,
                service="Redis",
                command="docker-compose up -d redis",
                description="Start Redis cache/coordination server (required by Redis Platform)",
                wait_for=[],
                healthcheck="redis-cli -h $REDIS_HOST -p $REDIS_PORT ping",
                notes=(
                    "Redis is used for caching, session management, distributed locking, "
                    "rate limiting, and inter-service queue coordination. "
                    "Set REDIS_HOST and REDIS_PORT before starting AIOS Core."
                ),
            ),
            StartupStep(
                order=3,
                service="Qdrant",
                command="docker-compose up -d qdrant",
                description="Start Qdrant vector database (required by Runtime Intelligence Platform)",
                wait_for=[],
                healthcheck="curl -sf http://$QDRANT_HOST:$QDRANT_PORT/health",
                notes=(
                    "Qdrant stores conversation memory, semantic search indexes, and "
                    "AI memory embeddings. The Runtime Intelligence Platform connects "
                    "to Qdrant during bootstrap. QDRANT_HOST and QDRANT_PORT must be set."
                ),
            ),
            StartupStep(
                order=4,
                service="Database Migrations",
                command="python -m aios.migrations",
                description=(
                    "Run PostgreSQL schema migrations via PersistenceBootstrapper "
                    "(called automatically on bootstrap_kernel initialization)"
                ),
                wait_for=["PostgreSQL"],
                healthcheck=None,
                notes=(
                    "Migrations are run automatically inside bootstrap_kernel() via "
                    "PersistenceBootstrapper.start(). Running manually ensures the "
                    "schema is current before the first startup."
                ),
            ),
            StartupStep(
                order=5,
                service="AIOS Core",
                command="aios",
                description=(
                    "Start the AIOS application (Kernel + all platform services). "
                    "Bootstraps: ServiceRegistry → Persistence → Redis → Qdrant → "
                    "RuntimeServices → SourceControl → n8n."
                ),
                wait_for=["PostgreSQL", "Redis", "Qdrant"],
                healthcheck="aios --version",
                notes=(
                    "The full bootstrap sequence is orchestrated by bootstrap_kernel() in "
                    "bootstrap_modules/bootstrap_kernel.py. All three external services "
                    "must be healthy before launching AIOS Core."
                ),
            ),
            StartupStep(
                order=6,
                service="n8n (optional)",
                command="docker-compose up -d n8n",
                description=(
                    "Start the self-hosted n8n workflow automation server. "
                    "AIOS auto-detects n8n via N8N_SERVER_URL on startup."
                ),
                wait_for=[],
                healthcheck="curl -sf $N8N_SERVER_URL/healthz",
                notes=(
                    "n8n is optional. If N8N_SERVER_URL is not set, the n8n platform "
                    "is registered but remains in a disconnected state. "
                    "Authentication: set N8N_API_KEY (preferred) or N8N_EMAIL + N8N_PASSWORD."
                ),
            ),
        ]
        return steps


class OmniRouteAnalyzer:
    """Analyzes OmniRoute provider configuration from the providers registry."""

    def analyze(self) -> List[OmniRouteProvider]:
        """
        Extract OmniRoute provider configuration.

        Derived from:
          - core/src/aios/providers/registry.py
          - core/src/aios/services/model_impl.py
          - config/config.toml
        """
        providers = [
            OmniRouteProvider(
                name="OpenRouter",
                env_key="OPENROUTER_API_KEY",
                base_url="https://openrouter.ai/api/v1",
                default_model="qwen/qwen3-coder",
                description=(
                    "Primary multi-model gateway. Routes requests to 100+ models "
                    "via a single API. Configured via config/config.toml [llm.openrouter]."
                ),
                required=False,
            ),
            OmniRouteProvider(
                name="Anthropic / Claude",
                env_key="ANTHROPIC_API_KEY",
                base_url="https://api.anthropic.com/v1",
                default_model="claude-3-5-sonnet",
                description=(
                    "Direct Anthropic Claude integration. Also accepted via "
                    "CLAUDE_CODE_API_KEY for Claude Code compatibility."
                ),
                required=False,
            ),
            OmniRouteProvider(
                name="Google Gemini",
                env_key="GEMINI_API_KEY",
                base_url="https://generativelanguage.googleapis.com/v1beta",
                default_model="gemini-2.0-flash-exp",
                description=(
                    "Google Gemini provider. Used for embedding generation "
                    "and as a fallback model provider."
                ),
                required=False,
            ),
        ]
        return providers


class BackupAnalyzer:
    """Analyzes backup requirements from the data persistence architecture."""

    def analyze(self) -> List[BackupTarget]:
        """Extract backup targets."""
        targets = [
            BackupTarget(
                name="PostgreSQL Database",
                type="database",
                location="/var/backups/aios/postgres",
                frequency="daily",
                retention="30 days",
                tool="pg_dump",
                notes=(
                    "Contains all workspaces, sessions, engineering tasks, planning, "
                    "approval, review, documentation metadata, and AI memory persistence."
                ),
            ),
            BackupTarget(
                name="Qdrant Vector Store",
                type="database",
                location="/var/backups/aios/qdrant",
                frequency="daily",
                retention="30 days",
                tool="Qdrant Snapshot API",
                notes=(
                    "Contains conversation_memory, semantic search indexes, and "
                    "runtime intelligence vectors. Use the Qdrant snapshot API."
                ),
            ),
            BackupTarget(
                name="Configuration Files",
                type="configuration",
                location="/var/backups/aios/config",
                frequency="weekly",
                retention="90 days",
                tool="tar",
                notes=(
                    "Includes config/config.toml, .env, docker-compose files. "
                    "Never store secrets in the backup archive unencrypted."
                ),
            ),
            BackupTarget(
                name="User Data & Workspaces",
                type="files",
                location="/var/backups/aios/data",
                frequency="daily",
                retention="30 days",
                tool="rsync",
                notes=(
                    "Includes user conversation histories, workspace snapshots, "
                    "and any generated artifacts stored on the filesystem."
                ),
            ),
        ]
        return targets


class MonitoringAnalyzer:
    """Analyzes monitoring requirements."""

    def analyze(self) -> List[MonitoringMetric]:
        """Extract monitoring metrics."""
        metrics = [
            # Service metrics
            MonitoringMetric(
                name="API Response Time",
                description="Average response time for API calls",
                source="service",
                alert_threshold="> 500ms p95",
            ),
            MonitoringMetric(
                name="Error Rate",
                description="Percentage of requests resulting in errors",
                source="service",
                alert_threshold="> 1%",
            ),
            MonitoringMetric(
                name="OmniRoute Provider Latency",
                description="Per-provider LLM response latency",
                source="service",
                alert_threshold="> 10s p99",
            ),
            MonitoringMetric(
                name="OmniRoute Provider Failures",
                description="Consecutive failures triggering failover routing",
                source="service",
                alert_threshold="> 3 consecutive failures",
            ),
            # Database metrics
            MonitoringMetric(
                name="PostgreSQL Connection Pool",
                description="Number of active database connections",
                source="database",
                alert_threshold="> 80% of max_connections",
            ),
            MonitoringMetric(
                name="PostgreSQL Query Latency",
                description="Average PostgreSQL query execution time",
                source="database",
                alert_threshold="> 200ms p95",
            ),
            MonitoringMetric(
                name="Redis Memory Usage",
                description="Redis memory consumption",
                source="database",
                alert_threshold="> 80% of maxmemory",
            ),
            MonitoringMetric(
                name="Redis Eviction Rate",
                description="Rate of keys evicted from Redis cache",
                source="database",
                alert_threshold="> 0 evictions/s (investigate maxmemory policy)",
            ),
            MonitoringMetric(
                name="Qdrant Collection Size",
                description="Number of vectors in each Qdrant collection",
                source="database",
                alert_threshold="N/A (monitor for unexpected growth)",
            ),
            MonitoringMetric(
                name="Qdrant Search Latency",
                description="Vector similarity search response time",
                source="database",
                alert_threshold="> 100ms p95",
            ),
            # System metrics
            MonitoringMetric(
                name="CPU Usage",
                description="System CPU utilization",
                source="system",
                alert_threshold="> 80%",
            ),
            MonitoringMetric(
                name="Memory Usage",
                description="System memory utilization",
                source="system",
                alert_threshold="> 85%",
            ),
            MonitoringMetric(
                name="Disk Usage",
                description="Disk space utilization",
                source="system",
                alert_threshold="> 90%",
            ),
            MonitoringMetric(
                name="n8n Workflow Failures",
                description="Failed n8n workflow executions per hour",
                source="service",
                alert_threshold="> 5 failures/hour",
            ),
        ]
        return metrics


class TroubleshootingAnalyzer:
    """Analyzes common troubleshooting scenarios from known failure modes."""

    def analyze(self) -> List[TroubleshootingEntry]:
        """Extract troubleshooting scenarios."""
        entries = [
            TroubleshootingEntry(
                symptom="AIOS fails to start with database connection error",
                cause="PostgreSQL is not running or POSTGRES_* environment variables are incorrect",
                solution=(
                    "1. Verify PostgreSQL is running: `docker-compose ps postgres`\n"
                    "2. Check POSTGRES_HOST, POSTGRES_DATABASE, POSTGRES_USER, POSTGRES_PASSWORD\n"
                    "3. Test connection manually: `psql -U $POSTGRES_USER -d $POSTGRES_DATABASE`\n"
                    "4. Check PostgreSQL logs: `docker-compose logs postgres`"
                ),
                related_logs=["aios.log", "postgres.log"],
                cross_refs=["configuration.md#postgresql-configuration"],
            ),
            TroubleshootingEntry(
                symptom="Redis connection refused or timeout on startup",
                cause="Redis is not running, wrong host/port, or authentication failure",
                solution=(
                    "1. Verify Redis is running: `docker-compose ps redis`\n"
                    "2. Check REDIS_HOST and REDIS_PORT environment variables\n"
                    "3. Test connection: `redis-cli -h $REDIS_HOST -p $REDIS_PORT ping`\n"
                    "4. If using auth, verify REDIS_PASSWORD is correct\n"
                    "5. Check TLS settings: REDIS_TLS should match server config"
                ),
                related_logs=["aios.log", "redis.log"],
                cross_refs=["configuration.md#redis-configuration"],
            ),
            TroubleshootingEntry(
                symptom="Qdrant connection error or vector collection missing",
                cause="Qdrant is not running, wrong host/port, or collection not initialized",
                solution=(
                    "1. Verify Qdrant is running: `docker-compose ps qdrant`\n"
                    "2. Check QDRANT_HOST and QDRANT_PORT environment variables\n"
                    "3. Test health: `curl http://$QDRANT_HOST:$QDRANT_PORT/health`\n"
                    "4. List collections: `curl http://$QDRANT_HOST:$QDRANT_PORT/collections`\n"
                    "5. If QDRANT_API_KEY is set, verify it matches the server config"
                ),
                related_logs=["aios.log", "qdrant.log"],
                cross_refs=["configuration.md#qdrant-configuration"],
            ),
            TroubleshootingEntry(
                symptom="Slow response times or AI model timeouts",
                cause="OmniRoute provider latency, Redis cache miss, or Qdrant vector search overload",
                solution=(
                    "1. Check OmniRoute provider health: review aios.log for provider errors\n"
                    "2. Verify API keys: OPENROUTER_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY\n"
                    "3. Check Redis cache hit rate: `redis-cli info stats | grep keyspace`\n"
                    "4. Check Qdrant search latency via /collections endpoint\n"
                    "5. Review provider-specific rate limits and quotas"
                ),
                related_logs=["aios.log", "redis.log", "qdrant.log"],
                cross_refs=["configuration.md#omniroute--ai-provider-configuration"],
            ),
            TroubleshootingEntry(
                symptom="Memory leaks or high memory usage",
                cause="Unclosed database connections or large embedding cache",
                solution=(
                    "1. Monitor PostgreSQL connection pool size\n"
                    "2. Monitor Redis memory: `redis-cli info memory`\n"
                    "3. Adjust REDIS_TIMEOUT to reclaim idle connections\n"
                    "4. Check Qdrant vector collection sizes\n"
                    "5. Restart services in order: AIOS Core → Redis → Qdrant → PostgreSQL"
                ),
                related_logs=["aios.log", "system.log"],
                cross_refs=["monitoring.md#database-metrics"],
            ),
            TroubleshootingEntry(
                symptom="n8n workflows not triggering or integration errors",
                cause="n8n server not running, N8N_* variables incorrect, or authentication failure",
                solution=(
                    "1. Verify n8n is running: `docker-compose ps n8n` or `curl $N8N_SERVER_URL/healthz`\n"
                    "2. Check N8N_SERVER_URL points to the correct server\n"
                    "3. Verify authentication: N8N_API_KEY (preferred) or N8N_EMAIL + N8N_PASSWORD\n"
                    "4. Check n8n logs: `docker-compose logs n8n`\n"
                    "5. In AIOS, run the `/n8n-status` command to diagnose connection"
                ),
                related_logs=["aios.log", "n8n.log"],
                cross_refs=["configuration.md#n8n-optional-configuration"],
            ),
            TroubleshootingEntry(
                symptom="Database migrations fail on startup",
                cause="Schema version mismatch, insufficient permissions, or PostgreSQL unavailable",
                solution=(
                    "1. Ensure PostgreSQL is running before running migrations\n"
                    "2. Verify POSTGRES_USER has CREATE TABLE and ALTER TABLE permissions\n"
                    "3. Run migrations manually: `python -m aios.migrations`\n"
                    "4. Check migration logs for specific SQL errors\n"
                    "5. If needed, reset schema: drop and recreate the database, then re-run migrations"
                ),
                related_logs=["aios.log", "postgres.log"],
                cross_refs=["startup.md#step-4-database-migrations"],
            ),
        ]
        return entries

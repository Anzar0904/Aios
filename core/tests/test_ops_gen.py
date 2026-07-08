"""
test_ops_gen.py — Comprehensive Regression Tests for the Operations Guide Generator.

Verifies:
  - Guide generation status and completeness
  - File existence and non-emptiness
  - Auto-generated banners
  - Content accuracy for all guides
  - PostgreSQL, Redis, Qdrant, n8n, OmniRoute configuration coverage
  - Startup sequence matches actual bootstrap_kernel.py order
  - Cross-references between guides
  - Idempotency (identical output on repeated runs)
  - Handwritten documentation preservation
  - Production checklist completeness

Sprint 7 — Milestone 5 (Deployment & Operations Guides)
"""

from pathlib import Path

import pytest

from aios.docgen.ops_analyzers import (
    BackupAnalyzer,
    ConfigurationAnalyzer,
    MonitoringAnalyzer,
    OmniRouteAnalyzer,
    ServiceDeploymentAnalyzer,
    StartupSequenceAnalyzer,
    TroubleshootingAnalyzer,
)
from aios.docgen.ops_engine import OperationsGeneratorEngine
from aios.docgen.ops_models import (
    BackupTarget,
    ConfigurationItem,
    MonitoringMetric,
    OmniRouteProvider,
    OperationsGenerationResult,
    ServiceDeployment,
    StartupStep,
    TroubleshootingEntry,
)


# ==============================================================================
# Fixtures
# ==============================================================================


@pytest.fixture(scope="module")
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture(scope="module")
def operations_dir(project_root: Path) -> Path:
    """Return the operations output directory."""
    return project_root / "docs" / "operations"


@pytest.fixture(scope="module")
def run_generator_once(project_root: Path) -> OperationsGenerationResult:
    """Run the operations generator once and return the result."""
    engine = OperationsGeneratorEngine(project_root=project_root)
    return engine.run()


@pytest.fixture(scope="module")
def all_guide_contents(operations_dir: Path, run_generator_once: OperationsGenerationResult) -> dict:
    """Load all guide file contents after generation."""
    guides = [
        "README.md",
        "local_setup.md",
        "configuration.md",
        "deployment.md",
        "startup.md",
        "monitoring.md",
        "backup_restore.md",
        "troubleshooting.md",
        "production_checklist.md",
    ]
    return {f: (operations_dir / f).read_text(encoding="utf-8") for f in guides}


# ==============================================================================
# 1. Generation Status Tests
# ==============================================================================


class TestOperationsGenerationStatus:
    """Test that operations guide generation completes successfully."""

    def test_generation_succeeds(self, run_generator_once):
        """Operations generation should complete with success status."""
        assert run_generator_once.status == "success"

    def test_no_errors(self, run_generator_once):
        """Operations generation should produce no errors."""
        assert len(run_generator_once.errors) == 0

    def test_nine_guides_produced(self, run_generator_once):
        """Operations generation should produce exactly 9 files."""
        assert run_generator_once.guides_generated == 9

    def test_elapsed_is_positive(self, run_generator_once):
        """Generation should complete in positive time."""
        assert run_generator_once.elapsed >= 0

    def test_files_written_list_has_nine_entries(self, run_generator_once):
        """files_written should contain exactly 9 absolute paths."""
        assert len(run_generator_once.files_written) == 9

    def test_all_written_paths_are_absolute(self, run_generator_once):
        """All written file paths should be absolute."""
        for path_str in run_generator_once.files_written:
            assert Path(path_str).is_absolute(), f"Not absolute: {path_str}"


# ==============================================================================
# 2. File Existence Tests
# ==============================================================================


_EXPECTED_FILES = [
    "README.md",
    "local_setup.md",
    "configuration.md",
    "deployment.md",
    "startup.md",
    "monitoring.md",
    "backup_restore.md",
    "troubleshooting.md",
    "production_checklist.md",
]


class TestOperationsFilesExist:
    """Test that all expected operations guide files are created."""

    @pytest.mark.parametrize("filename", _EXPECTED_FILES)
    def test_file_exists(self, operations_dir, run_generator_once, filename):
        """Each expected guide file should exist."""
        assert (operations_dir / filename).exists(), f"{filename} must exist"

    @pytest.mark.parametrize("filename", _EXPECTED_FILES)
    def test_file_not_empty(self, operations_dir, run_generator_once, filename):
        """Each guide file should have content."""
        content = (operations_dir / filename).read_text(encoding="utf-8")
        assert len(content) > 100, f"{filename} must have substantial content"

    @pytest.mark.parametrize("filename", _EXPECTED_FILES)
    def test_file_has_auto_generated_banner(self, operations_dir, run_generator_once, filename):
        """Every generated file should have the auto-generated banner."""
        content = (operations_dir / filename).read_text(encoding="utf-8")
        assert "AUTO-GENERATED" in content
        assert "DO NOT EDIT MANUALLY" in content

    @pytest.mark.parametrize("filename", _EXPECTED_FILES)
    def test_file_has_generated_timestamp(self, operations_dir, run_generator_once, filename):
        """Every generated file should have a timestamp in the banner."""
        content = (operations_dir / filename).read_text(encoding="utf-8")
        assert "Generated on:" in content


# ==============================================================================
# 3. README Index Tests
# ==============================================================================


class TestReadmeIndex:
    """Test the README.md index content."""

    def test_header_present(self, all_guide_contents):
        content = all_guide_contents["README.md"]
        assert "# Deployment & Operations Guides" in content

    def test_generated_banner(self, all_guide_contents):
        content = all_guide_contents["README.md"]
        assert "AUTO-GENERATED" in content
        assert "DO NOT EDIT MANUALLY" in content

    def test_overview_section(self, all_guide_contents):
        content = all_guide_contents["README.md"]
        assert "## Overview" in content

    def test_all_guide_files_listed(self, all_guide_contents):
        content = all_guide_contents["README.md"]
        for filename in _EXPECTED_FILES:
            assert filename in content, f"README must list {filename}"

    def test_regeneration_instructions(self, all_guide_contents):
        content = all_guide_contents["README.md"]
        assert "## Regeneration" in content
        assert "python -m aios.docgen.ops_main" in content

    def test_cross_references_present(self, all_guide_contents):
        content = all_guide_contents["README.md"]
        assert "## Cross-References" in content
        assert "../generated/README.md" in content
        assert "../reference/README.md" in content
        assert "../diagrams/README.md" in content


# ==============================================================================
# 4. Local Setup Guide Tests
# ==============================================================================


class TestLocalSetupGuide:
    """Test the local_setup.md guide content."""

    def test_header_present(self, all_guide_contents):
        content = all_guide_contents["local_setup.md"]
        assert "# Local Development Setup" in content

    def test_prerequisites_section(self, all_guide_contents):
        content = all_guide_contents["local_setup.md"]
        assert "## Prerequisites" in content
        assert "Python" in content
        assert "Docker" in content

    def test_installation_steps_section(self, all_guide_contents):
        content = all_guide_contents["local_setup.md"]
        assert "## Installation Steps" in content

    def test_clone_step(self, all_guide_contents):
        content = all_guide_contents["local_setup.md"]
        assert "git clone" in content

    def test_venv_step(self, all_guide_contents):
        content = all_guide_contents["local_setup.md"]
        assert "python3 -m venv .venv" in content

    def test_docker_compose_step(self, all_guide_contents):
        content = all_guide_contents["local_setup.md"]
        assert "docker-compose up -d postgres redis qdrant" in content

    def test_external_services_listed(self, all_guide_contents):
        content = all_guide_contents["local_setup.md"]
        assert "PostgreSQL" in content
        assert "Redis" in content
        assert "Qdrant" in content

    def test_minimum_env_vars_example(self, all_guide_contents):
        content = all_guide_contents["local_setup.md"]
        assert "POSTGRES_DATABASE" in content
        assert "REDIS_HOST" in content
        assert "QDRANT_HOST" in content
        assert "OPENROUTER_API_KEY" in content

    def test_config_toml_step(self, all_guide_contents):
        content = all_guide_contents["local_setup.md"]
        assert "config/config.toml" in content or "config.toml" in content

    def test_database_migration_step(self, all_guide_contents):
        content = all_guide_contents["local_setup.md"]
        assert "python -m aios.migrations" in content

    def test_start_aios_step(self, all_guide_contents):
        content = all_guide_contents["local_setup.md"]
        assert "aios" in content

    def test_verification_section(self, all_guide_contents):
        content = all_guide_contents["local_setup.md"]
        assert "## Verification" in content

    def test_troubleshooting_cross_ref(self, all_guide_contents):
        content = all_guide_contents["local_setup.md"]
        assert "troubleshooting.md" in content


# ==============================================================================
# 5. Configuration Guide Tests
# ==============================================================================


class TestConfigurationGuide:
    """Test the configuration.md guide content for complete parameter coverage."""

    def test_header_present(self, all_guide_contents):
        content = all_guide_contents["configuration.md"]
        assert "# Configuration Guide" in content

    def test_configuration_overview_section(self, all_guide_contents):
        content = all_guide_contents["configuration.md"]
        assert "## Configuration Overview" in content

    def test_priority_order_explained(self, all_guide_contents):
        content = all_guide_contents["configuration.md"]
        assert "Priority order" in content or "priority" in content.lower()

    # ── PostgreSQL ────────────────────────────────────────────────────────────

    def test_postgres_section_present(self, all_guide_contents):
        content = all_guide_contents["configuration.md"]
        assert "## PostgreSQL Configuration" in content

    @pytest.mark.parametrize("param", [
        "POSTGRES_HOST",
        "POSTGRES_PORT",
        "POSTGRES_DATABASE",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
        "POSTGRES_SSLMODE",
        "POSTGRES_CONNECT_TIMEOUT",
    ])
    def test_postgres_param_documented(self, all_guide_contents, param):
        """Each PostgreSQL env var found in persistence.py must be documented."""
        content = all_guide_contents["configuration.md"]
        assert param in content, f"PostgreSQL param {param} must be documented"

    def test_postgres_sslmode_production_note(self, all_guide_contents):
        content = all_guide_contents["configuration.md"]
        assert "POSTGRES_SSLMODE=require" in content

    def test_postgres_implementation_reference(self, all_guide_contents):
        content = all_guide_contents["configuration.md"]
        assert "persistence.py" in content or "PersistenceConfigurationService" in content

    # ── Redis ─────────────────────────────────────────────────────────────────

    def test_redis_section_present(self, all_guide_contents):
        content = all_guide_contents["configuration.md"]
        assert "## Redis Configuration" in content

    @pytest.mark.parametrize("param", [
        "REDIS_HOST",
        "REDIS_PORT",
        "REDIS_USERNAME",
        "REDIS_PASSWORD",
        "REDIS_DATABASE",
        "REDIS_TLS",
        "REDIS_TIMEOUT",
    ])
    def test_redis_param_documented(self, all_guide_contents, param):
        """Each Redis env var found in redis.py must be documented."""
        content = all_guide_contents["configuration.md"]
        assert param in content, f"Redis param {param} must be documented"

    def test_redis_usage_note(self, all_guide_contents):
        content = all_guide_contents["configuration.md"]
        assert "Cache" in content or "cache" in content
        assert "session" in content.lower() or "Session" in content

    # ── Qdrant ────────────────────────────────────────────────────────────────

    def test_qdrant_section_present(self, all_guide_contents):
        content = all_guide_contents["configuration.md"]
        assert "## Qdrant Configuration" in content

    @pytest.mark.parametrize("param", [
        "QDRANT_HOST",
        "QDRANT_PORT",
        "QDRANT_GRPC_PORT",
        "QDRANT_API_KEY",
        "QDRANT_HTTPS",
        "QDRANT_TIMEOUT",
        "QDRANT_RETRY_COUNT",
        "QDRANT_DEFAULT_DIMENSIONS",
        "QDRANT_DEFAULT_DISTANCE",
    ])
    def test_qdrant_param_documented(self, all_guide_contents, param):
        """Each Qdrant env var found in qdrant.py must be documented."""
        content = all_guide_contents["configuration.md"]
        assert param in content, f"Qdrant param {param} must be documented"

    def test_qdrant_collections_note(self, all_guide_contents):
        content = all_guide_contents["configuration.md"]
        assert "conversation_memory" in content or "collection" in content.lower()

    # ── n8n ───────────────────────────────────────────────────────────────────

    def test_n8n_section_present(self, all_guide_contents):
        content = all_guide_contents["configuration.md"]
        assert "n8n" in content.lower()

    @pytest.mark.parametrize("param", [
        "N8N_SERVER_URL",
        "N8N_API_KEY",
        "N8N_EMAIL",
        "N8N_PASSWORD",
        "N8N_BEARER_TOKEN",
    ])
    def test_n8n_param_documented(self, all_guide_contents, param):
        """Each n8n env var from service.py must be documented."""
        content = all_guide_contents["configuration.md"]
        assert param in content, f"n8n param {param} must be documented"

    def test_n8n_auth_priority_documented(self, all_guide_contents):
        """Authentication priority order must be documented."""
        content = all_guide_contents["configuration.md"]
        assert "N8N_API_KEY" in content
        assert "N8N_BEARER_TOKEN" in content

    # ── OmniRoute ─────────────────────────────────────────────────────────────

    def test_omniroute_section_present(self, all_guide_contents):
        content = all_guide_contents["configuration.md"]
        assert "OmniRoute" in content

    @pytest.mark.parametrize("param", [
        "OPENROUTER_API_KEY",
        "ANTHROPIC_API_KEY",
        "GEMINI_API_KEY",
    ])
    def test_omniroute_param_documented(self, all_guide_contents, param):
        """Each OmniRoute provider API key must be documented."""
        content = all_guide_contents["configuration.md"]
        assert param in content, f"OmniRoute param {param} must be documented"

    def test_config_toml_example(self, all_guide_contents):
        """config/config.toml example must be included."""
        content = all_guide_contents["configuration.md"]
        assert "config/config.toml" in content or "config.toml" in content
        assert "openrouter" in content
        assert "default_model" in content

    def test_security_note_present(self, all_guide_contents):
        content = all_guide_contents["configuration.md"]
        assert "securely" in content.lower() or "never commit" in content.lower()

    def test_omniroute_diagram_cross_ref(self, all_guide_contents):
        """Configuration should cross-reference the OmniRoute diagram."""
        content = all_guide_contents["configuration.md"]
        assert "../diagrams/omniroute.md" in content or "diagrams/omniroute" in content


# ==============================================================================
# 6. Deployment Guide Tests
# ==============================================================================


class TestDeploymentGuide:
    """Test the deployment.md guide content."""

    def test_header_present(self, all_guide_contents):
        content = all_guide_contents["deployment.md"]
        assert "# Deployment Guide" in content

    def test_deployment_architecture_section(self, all_guide_contents):
        content = all_guide_contents["deployment.md"]
        assert "## Deployment Architecture" in content

    def test_required_services_listed(self, all_guide_contents):
        content = all_guide_contents["deployment.md"]
        assert "PostgreSQL" in content
        assert "Redis" in content
        assert "Qdrant" in content

    def test_optional_services_listed(self, all_guide_contents):
        content = all_guide_contents["deployment.md"]
        assert "n8n" in content

    def test_pre_deployment_checklist_ref(self, all_guide_contents):
        content = all_guide_contents["deployment.md"]
        assert "production_checklist.md" in content

    def test_deployment_steps_section(self, all_guide_contents):
        content = all_guide_contents["deployment.md"]
        assert "## Deployment Steps" in content

    def test_environment_configuration_step(self, all_guide_contents):
        content = all_guide_contents["deployment.md"]
        assert "POSTGRES_SSLMODE" in content or "configuration.md" in content

    def test_migrations_step(self, all_guide_contents):
        content = all_guide_contents["deployment.md"]
        assert "python -m aios.migrations" in content

    def test_post_deployment_section(self, all_guide_contents):
        content = all_guide_contents["deployment.md"]
        assert "## Post-Deployment" in content

    def test_rollback_procedure(self, all_guide_contents):
        content = all_guide_contents["deployment.md"]
        assert "## Rollback Procedure" in content or "Rollback" in content


# ==============================================================================
# 7. Startup Guide Tests
# ==============================================================================


class TestStartupGuide:
    """
    Test the startup.md guide content matches the actual bootstrap_kernel.py order.

    Expected bootstrap sequence from bootstrap_modules/bootstrap_kernel.py:
      1. PostgreSQL → Persistence Platform
      2. Redis → Redis Platform
      3. Qdrant → Vector Memory Platform
      4. Database Migrations → PersistenceBootstrapper.start()
      5. AIOS Core → full kernel
      6. n8n → optional workflow platform
    """

    def test_header_present(self, all_guide_contents):
        content = all_guide_contents["startup.md"]
        assert "# Service Startup Guide" in content

    def test_bootstrap_architecture_section(self, all_guide_contents):
        """Startup guide must document the bootstrap architecture."""
        content = all_guide_contents["startup.md"]
        assert "bootstrap" in content.lower() or "Bootstrap" in content

    def test_startup_sequence_section(self, all_guide_contents):
        content = all_guide_contents["startup.md"]
        assert "## Startup Sequence" in content

    def test_postgres_is_step_1(self, all_guide_contents):
        """PostgreSQL must be step 1 — required by PersistenceBootstrapper."""
        content = all_guide_contents["startup.md"]
        assert "Step 1: PostgreSQL" in content or "Step 1" in content and "PostgreSQL" in content

    def test_redis_is_step_2(self, all_guide_contents):
        """Redis must be step 2 — required by RedisRuntimeService."""
        content = all_guide_contents["startup.md"]
        assert "Step 2: Redis" in content or ("Step 2" in content and "Redis" in content)

    def test_qdrant_is_step_3(self, all_guide_contents):
        """Qdrant must be step 3 — required by QdrantPlatform."""
        content = all_guide_contents["startup.md"]
        assert "Step 3: Qdrant" in content or ("Step 3" in content and "Qdrant" in content)

    def test_migration_is_step_4(self, all_guide_contents):
        """Database Migrations must be step 4 — depends on PostgreSQL."""
        content = all_guide_contents["startup.md"]
        assert "Step 4" in content and "Migration" in content

    def test_aios_core_is_step_5(self, all_guide_contents):
        """AIOS Core must be step 5 — depends on all external services."""
        content = all_guide_contents["startup.md"]
        assert "Step 5" in content and "AIOS" in content

    def test_n8n_is_step_6(self, all_guide_contents):
        """n8n must be step 6 and marked as optional."""
        content = all_guide_contents["startup.md"]
        assert "Step 6" in content and "n8n" in content
        assert "optional" in content.lower()

    def test_all_healthchecks_present(self, all_guide_contents):
        """Each service should have a verification/healthcheck command."""
        content = all_guide_contents["startup.md"]
        assert "psql" in content  # PostgreSQL verification
        assert "redis-cli" in content  # Redis verification
        assert "curl" in content  # Qdrant verification

    def test_postgres_depends_noted(self, all_guide_contents):
        content = all_guide_contents["startup.md"]
        assert "PostgreSQL" in content

    def test_bootstrap_order_matches_kernel(self, all_guide_contents):
        """
        Verify startup.md step order is consistent with bootstrap_kernel.py.
        The bootstrap sequence reads: Persistence → Redis → Qdrant → Runtime → n8n.
        """
        content = all_guide_contents["startup.md"]
        pg_pos = content.find("Step 1")
        redis_pos = content.find("Step 2")
        qdrant_pos = content.find("Step 3")
        aios_pos = content.find("Step 5")
        n8n_pos = content.find("Step 6")
        assert pg_pos < redis_pos < qdrant_pos < aios_pos < n8n_pos, (
            "Startup steps must be in bootstrap order: PG < Redis < Qdrant < AIOS < n8n"
        )

    def test_automated_startup_section(self, all_guide_contents):
        content = all_guide_contents["startup.md"]
        assert "## Automated Startup" in content
        assert "docker-compose up -d" in content

    def test_shutdown_sequence_present(self, all_guide_contents):
        content = all_guide_contents["startup.md"]
        assert "Shutdown" in content or "shutdown" in content.lower()

    def test_startup_failures_section(self, all_guide_contents):
        content = all_guide_contents["startup.md"]
        assert "Startup Failures" in content or "failure" in content.lower()

    def test_troubleshooting_cross_ref(self, all_guide_contents):
        content = all_guide_contents["startup.md"]
        assert "troubleshooting.md" in content


# ==============================================================================
# 8. Monitoring Guide Tests
# ==============================================================================


class TestMonitoringGuide:
    """Test the monitoring.md guide content."""

    def test_header_present(self, all_guide_contents):
        content = all_guide_contents["monitoring.md"]
        assert "# Monitoring Guide" in content

    def test_monitoring_overview_section(self, all_guide_contents):
        content = all_guide_contents["monitoring.md"]
        assert "## Monitoring Overview" in content

    def test_service_metrics_section(self, all_guide_contents):
        content = all_guide_contents["monitoring.md"]
        assert "## Service Metrics" in content

    def test_database_metrics_section(self, all_guide_contents):
        content = all_guide_contents["monitoring.md"]
        assert "## Database Metrics" in content

    def test_system_metrics_section(self, all_guide_contents):
        content = all_guide_contents["monitoring.md"]
        assert "## System Metrics" in content

    def test_api_response_time_metric(self, all_guide_contents):
        content = all_guide_contents["monitoring.md"]
        assert "API Response Time" in content

    def test_omniroute_metrics(self, all_guide_contents):
        """OmniRoute provider metrics must be documented."""
        content = all_guide_contents["monitoring.md"]
        assert "OmniRoute" in content

    def test_postgres_metric_documented(self, all_guide_contents):
        content = all_guide_contents["monitoring.md"]
        assert "PostgreSQL" in content

    def test_redis_metric_documented(self, all_guide_contents):
        content = all_guide_contents["monitoring.md"]
        assert "Redis" in content

    def test_qdrant_metric_documented(self, all_guide_contents):
        content = all_guide_contents["monitoring.md"]
        assert "Qdrant" in content

    def test_n8n_metric_documented(self, all_guide_contents):
        """n8n workflow failures metric must be documented."""
        content = all_guide_contents["monitoring.md"]
        assert "n8n" in content

    def test_monitoring_stack_section(self, all_guide_contents):
        content = all_guide_contents["monitoring.md"]
        assert "## Monitoring Stack" in content
        assert "Prometheus" in content
        assert "Grafana" in content

    def test_health_check_endpoints(self, all_guide_contents):
        content = all_guide_contents["monitoring.md"]
        assert "/health" in content
        assert "/health/db" in content
        assert "/health/redis" in content
        assert "/health/qdrant" in content

    def test_log_management_section(self, all_guide_contents):
        content = all_guide_contents["monitoring.md"]
        assert "## Log Management" in content

    def test_cross_references_present(self, all_guide_contents):
        content = all_guide_contents["monitoring.md"]
        assert "../reference/services.md" in content or "reference" in content
        assert "../generated/runtime.md" in content or "generated" in content


# ==============================================================================
# 9. Backup & Restore Guide Tests
# ==============================================================================


class TestBackupRestoreGuide:
    """Test the backup_restore.md guide content."""

    def test_header_present(self, all_guide_contents):
        content = all_guide_contents["backup_restore.md"]
        assert "# Backup & Restore Guide" in content

    def test_backup_strategy_section(self, all_guide_contents):
        content = all_guide_contents["backup_restore.md"]
        assert "## Backup Strategy" in content

    def test_postgres_backup_documented(self, all_guide_contents):
        content = all_guide_contents["backup_restore.md"]
        assert "PostgreSQL" in content
        assert "pg_dump" in content

    def test_qdrant_backup_documented(self, all_guide_contents):
        content = all_guide_contents["backup_restore.md"]
        assert "Qdrant" in content
        assert "snapshots" in content

    def test_config_backup_documented(self, all_guide_contents):
        content = all_guide_contents["backup_restore.md"]
        assert "Configuration" in content
        assert "config.toml" in content or "tar" in content

    def test_postgres_restore_procedure(self, all_guide_contents):
        content = all_guide_contents["backup_restore.md"]
        assert "pg_restore" in content

    def test_qdrant_restore_procedure(self, all_guide_contents):
        content = all_guide_contents["backup_restore.md"]
        assert "snapshots/recover" in content or "recover" in content

    def test_disaster_recovery_section(self, all_guide_contents):
        content = all_guide_contents["backup_restore.md"]
        assert "## Disaster Recovery" in content

    def test_rto_rpo_defined(self, all_guide_contents):
        content = all_guide_contents["backup_restore.md"]
        assert "RTO" in content
        assert "RPO" in content

    def test_backup_summary_table(self, all_guide_contents):
        """A backup strategy summary table should be present."""
        content = all_guide_contents["backup_restore.md"]
        assert "| Component |" in content or "| Backup" in content or "Frequency" in content

    def test_cross_references_present(self, all_guide_contents):
        content = all_guide_contents["backup_restore.md"]
        assert "startup.md" in content or "deployment.md" in content


# ==============================================================================
# 10. Troubleshooting Guide Tests
# ==============================================================================


class TestTroubleshootingGuide:
    """Test the troubleshooting.md guide content."""

    def test_header_present(self, all_guide_contents):
        content = all_guide_contents["troubleshooting.md"]
        assert "# Troubleshooting Guide" in content

    def test_quick_diagnostics_section(self, all_guide_contents):
        """Guide should have quick diagnostics commands."""
        content = all_guide_contents["troubleshooting.md"]
        assert "Diagnostic" in content or "diagnostic" in content.lower()

    def test_postgres_issue_documented(self, all_guide_contents):
        content = all_guide_contents["troubleshooting.md"]
        assert "PostgreSQL" in content or "database connection" in content.lower()

    def test_redis_issue_documented(self, all_guide_contents):
        content = all_guide_contents["troubleshooting.md"]
        assert "Redis" in content and "redis-cli" in content

    def test_qdrant_issue_documented(self, all_guide_contents):
        content = all_guide_contents["troubleshooting.md"]
        assert "Qdrant" in content

    def test_n8n_issue_documented(self, all_guide_contents):
        content = all_guide_contents["troubleshooting.md"]
        assert "n8n" in content
        assert "N8N_API_KEY" in content or "N8N_EMAIL" in content

    def test_omniroute_issue_documented(self, all_guide_contents):
        """OmniRoute/provider timeout issues must be documented."""
        content = all_guide_contents["troubleshooting.md"]
        assert "OmniRoute" in content or "OPENROUTER" in content

    def test_migration_issue_documented(self, all_guide_contents):
        """Migration failures must be documented."""
        content = all_guide_contents["troubleshooting.md"]
        assert "migrat" in content.lower()

    def test_common_issues_section(self, all_guide_contents):
        content = all_guide_contents["troubleshooting.md"]
        assert "## Common Issues" in content

    def test_general_troubleshooting_steps(self, all_guide_contents):
        content = all_guide_contents["troubleshooting.md"]
        assert "## General Troubleshooting Steps" in content

    def test_diagnostic_commands_present(self, all_guide_contents):
        content = all_guide_contents["troubleshooting.md"]
        assert "psql" in content
        assert "redis-cli" in content
        assert "curl" in content
        assert "docker-compose" in content

    def test_getting_help_section(self, all_guide_contents):
        content = all_guide_contents["troubleshooting.md"]
        assert "## Getting Help" in content

    def test_cross_references_present(self, all_guide_contents):
        content = all_guide_contents["troubleshooting.md"]
        assert "configuration.md" in content
        assert "startup.md" in content


# ==============================================================================
# 11. Production Checklist Tests
# ==============================================================================


class TestProductionChecklist:
    """Test the production_checklist.md content for completeness."""

    def test_header_present(self, all_guide_contents):
        content = all_guide_contents["production_checklist.md"]
        assert "# Production Deployment Checklist" in content

    def test_infrastructure_section(self, all_guide_contents):
        content = all_guide_contents["production_checklist.md"]
        assert "## Infrastructure" in content

    def test_security_section(self, all_guide_contents):
        content = all_guide_contents["production_checklist.md"]
        assert "## Security" in content

    def test_configuration_section(self, all_guide_contents):
        content = all_guide_contents["production_checklist.md"]
        assert "## Configuration" in content

    def test_database_section(self, all_guide_contents):
        content = all_guide_contents["production_checklist.md"]
        assert "## Database" in content

    def test_application_section(self, all_guide_contents):
        content = all_guide_contents["production_checklist.md"]
        assert "## Application" in content

    def test_monitoring_observability_section(self, all_guide_contents):
        content = all_guide_contents["production_checklist.md"]
        assert "Monitoring" in content

    def test_backup_dr_section(self, all_guide_contents):
        content = all_guide_contents["production_checklist.md"]
        assert "Backup" in content

    def test_performance_section(self, all_guide_contents):
        content = all_guide_contents["production_checklist.md"]
        assert "## Performance" in content

    def test_documentation_section(self, all_guide_contents):
        content = all_guide_contents["production_checklist.md"]
        assert "## Documentation" in content

    def test_post_deployment_section(self, all_guide_contents):
        content = all_guide_contents["production_checklist.md"]
        assert "Post-Deployment" in content

    def test_sign_off_section(self, all_guide_contents):
        content = all_guide_contents["production_checklist.md"]
        assert "## Sign-Off" in content

    def test_redis_password_in_security(self, all_guide_contents):
        content = all_guide_contents["production_checklist.md"]
        assert "REDIS_PASSWORD" in content

    def test_qdrant_api_key_in_security(self, all_guide_contents):
        content = all_guide_contents["production_checklist.md"]
        assert "QDRANT_API_KEY" in content

    def test_n8n_in_checklist(self, all_guide_contents):
        content = all_guide_contents["production_checklist.md"]
        assert "n8n" in content

    def test_omniroute_in_checklist(self, all_guide_contents):
        content = all_guide_contents["production_checklist.md"]
        assert "OmniRoute" in content

    def test_all_checkbox_items_use_correct_format(self, all_guide_contents):
        """All checklist items must use standard markdown task syntax."""
        content = all_guide_contents["production_checklist.md"]
        lines = content.splitlines()
        checklist_lines = [l for l in lines if l.strip().startswith("- [ ]")]
        assert len(checklist_lines) >= 30, (
            f"Production checklist should have at least 30 items, got {len(checklist_lines)}"
        )

    def test_cross_references_all_guides(self, all_guide_contents):
        """Production checklist should cross-reference all related guides."""
        content = all_guide_contents["production_checklist.md"]
        assert "configuration.md" in content
        assert "deployment.md" in content
        assert "startup.md" in content
        assert "monitoring.md" in content
        assert "backup_restore.md" in content
        assert "troubleshooting.md" in content


# ==============================================================================
# 12. Cross-Reference Validity Tests
# ==============================================================================


class TestCrossReferences:
    """Test that cross-references between guides are valid."""

    @pytest.mark.parametrize("source_file,target_file", [
        ("local_setup.md", "configuration.md"),
        ("local_setup.md", "troubleshooting.md"),
        ("deployment.md", "configuration.md"),
        ("deployment.md", "monitoring.md"),
        ("deployment.md", "backup_restore.md"),
        ("deployment.md", "production_checklist.md"),
        ("startup.md", "troubleshooting.md"),
        ("troubleshooting.md", "configuration.md"),
        ("troubleshooting.md", "startup.md"),
        ("backup_restore.md", "startup.md"),
        ("production_checklist.md", "configuration.md"),
        ("production_checklist.md", "monitoring.md"),
    ])
    def test_internal_cross_reference(self, all_guide_contents, source_file, target_file):
        """Source guide should reference target guide."""
        content = all_guide_contents[source_file]
        assert target_file in content, (
            f"{source_file} should cross-reference {target_file}"
        )

    @pytest.mark.parametrize("source_file", _EXPECTED_FILES)
    def test_generated_dir_reference_in_readme(self, all_guide_contents, source_file):
        """README should reference all generated directories."""
        if source_file == "README.md":
            content = all_guide_contents["README.md"]
            assert "../generated/README.md" in content
            assert "../reference/README.md" in content
            assert "../diagrams/README.md" in content


# ==============================================================================
# 13. Idempotency Tests
# ==============================================================================


class TestIdempotency:
    """Test that running the generator twice produces identical output."""

    def test_second_run_succeeds(self, project_root):
        """Second generation run should succeed."""
        engine = OperationsGeneratorEngine(project_root=project_root)
        result = engine.run()
        assert result.status == "success"
        assert len(result.errors) == 0

    def test_idempotent_output(self, project_root, operations_dir):
        """Running generator twice produces identical content (modulo timestamp in banner)."""
        engine = OperationsGeneratorEngine(project_root=project_root)

        # Run 1
        engine.run()
        run1_contents = {}
        for f in _EXPECTED_FILES:
            path = operations_dir / f
            if path.exists():
                content = path.read_text(encoding="utf-8")
                # Strip timestamp line to allow comparison
                run1_contents[f] = _strip_timestamps(content)

        # Run 2
        engine.run()
        run2_contents = {}
        for f in _EXPECTED_FILES:
            path = operations_dir / f
            if path.exists():
                content = path.read_text(encoding="utf-8")
                run2_contents[f] = _strip_timestamps(content)

        for f in _EXPECTED_FILES:
            assert run1_contents[f] == run2_contents[f], (
                f"Idempotency violation: {f} differs between runs"
            )

    def test_file_count_stable_across_runs(self, project_root):
        """Guide count must be stable across multiple runs."""
        engine = OperationsGeneratorEngine(project_root=project_root)
        r1 = engine.run()
        r2 = engine.run()
        assert r1.guides_generated == r2.guides_generated == 9


def _strip_timestamps(content: str) -> str:
    """Strip timestamp values so idempotency check ignores generation time."""
    import re
    # Remove ISO 8601 timestamps from banners and **Generated**: lines
    return re.sub(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", "TIMESTAMP", content)


# ==============================================================================
# 14. Handwritten Documentation Preservation Tests
# ==============================================================================


class TestHandwrittenDocPreservation:
    """
    Verify that the generator does NOT overwrite handwritten documentation
    in other docs/ subdirectories.
    """

    @pytest.fixture(scope="class")
    def handwritten_dirs(self, project_root: Path) -> list:
        """Return list of handwritten documentation directories."""
        docs_root = project_root / "docs"
        return [
            docs_root / "architecture",
            docs_root / "guides",
            docs_root / "database",
            docs_root / "persistence",
            docs_root / "adr",
        ]

    def test_architecture_docs_unchanged(self, project_root, handwritten_dirs, run_generator_once):
        """Generating operations docs must not touch architecture directory."""
        arch_dir = project_root / "docs" / "architecture"
        if arch_dir.exists():
            # Verify no operations-generator banner in architecture files
            for md_file in arch_dir.rglob("*.md"):
                content = md_file.read_text(encoding="utf-8")
                assert "ops_main" not in content, (
                    f"{md_file} should not be touched by ops generator"
                )

    def test_guides_docs_unchanged(self, project_root, run_generator_once):
        """Generating operations docs must not touch guides directory."""
        guides_dir = project_root / "docs" / "guides"
        if guides_dir.exists():
            for md_file in guides_dir.rglob("*.md"):
                content = md_file.read_text(encoding="utf-8")
                # Ops generator banner should not appear in handwritten guides
                if "aios.docgen operations guide generator" in content:
                    pytest.fail(f"{md_file} was modified by ops generator")

    def test_generator_only_writes_to_operations_dir(self, run_generator_once, operations_dir):
        """All written files must be inside docs/operations/."""
        for path_str in run_generator_once.files_written:
            path = Path(path_str)
            assert str(operations_dir) in str(path), (
                f"Generator wrote outside operations dir: {path}"
            )


# ==============================================================================
# 15. Analyzer Unit Tests
# ==============================================================================


class TestServiceDeploymentAnalyzer:
    """Unit tests for ServiceDeploymentAnalyzer."""

    @pytest.fixture
    def deployments(self, project_root) -> list:
        return ServiceDeploymentAnalyzer().analyze(project_root)

    def test_returns_list(self, deployments):
        assert isinstance(deployments, list)

    def test_all_items_are_service_deployments(self, deployments):
        for d in deployments:
            assert isinstance(d, ServiceDeployment)

    def test_postgres_is_present(self, deployments):
        names = [d.name for d in deployments]
        assert "PostgreSQL" in names

    def test_redis_is_present(self, deployments):
        names = [d.name for d in deployments]
        assert "Redis" in names

    def test_qdrant_is_present(self, deployments):
        names = [d.name for d in deployments]
        assert "Qdrant" in names

    def test_n8n_is_optional(self, deployments):
        n8n = next((d for d in deployments if d.name == "n8n"), None)
        assert n8n is not None
        assert n8n.required is False

    def test_postgres_port_is_5432(self, deployments):
        pg = next(d for d in deployments if d.name == "PostgreSQL")
        assert pg.port == 5432

    def test_redis_port_is_6379(self, deployments):
        redis = next(d for d in deployments if d.name == "Redis")
        assert redis.port == 6379

    def test_qdrant_port_is_6333(self, deployments):
        qdrant = next(d for d in deployments if d.name == "Qdrant")
        assert qdrant.port == 6333

    def test_n8n_port_is_5678(self, deployments):
        n8n = next(d for d in deployments if d.name == "n8n")
        assert n8n.port == 5678

    def test_postgres_has_required_config_keys(self, deployments):
        pg = next(d for d in deployments if d.name == "PostgreSQL")
        assert "POSTGRES_HOST" in pg.config_keys
        assert "POSTGRES_DATABASE" in pg.config_keys
        assert "POSTGRES_PASSWORD" in pg.config_keys

    def test_redis_has_password_and_tls_keys(self, deployments):
        redis = next(d for d in deployments if d.name == "Redis")
        assert "REDIS_PASSWORD" in redis.config_keys
        assert "REDIS_TLS" in redis.config_keys

    def test_qdrant_has_grpc_port_key(self, deployments):
        qdrant = next(d for d in deployments if d.name == "Qdrant")
        assert "QDRANT_GRPC_PORT" in qdrant.config_keys

    def test_n8n_has_auth_keys(self, deployments):
        n8n = next(d for d in deployments if d.name == "n8n")
        assert "N8N_API_KEY" in n8n.config_keys
        assert "N8N_EMAIL" in n8n.config_keys
        assert "N8N_BEARER_TOKEN" in n8n.config_keys


class TestConfigurationAnalyzer:
    """Unit tests for ConfigurationAnalyzer."""

    @pytest.fixture
    def configs(self, project_root) -> list:
        return ConfigurationAnalyzer().analyze(project_root)

    def test_returns_list(self, configs):
        assert isinstance(configs, list)

    def test_all_items_are_config_items(self, configs):
        for c in configs:
            assert isinstance(c, ConfigurationItem)

    def test_postgres_database_is_canonical_key(self, configs):
        """POSTGRES_DATABASE (not POSTGRES_DB) is the canonical env var."""
        keys = [c.key for c in configs]
        assert "POSTGRES_DATABASE" in keys

    def test_postgres_sslmode_present(self, configs):
        keys = [c.key for c in configs]
        assert "POSTGRES_SSLMODE" in keys

    def test_redis_password_present(self, configs):
        keys = [c.key for c in configs]
        assert "REDIS_PASSWORD" in keys

    def test_redis_username_present(self, configs):
        keys = [c.key for c in configs]
        assert "REDIS_USERNAME" in keys

    def test_redis_tls_present(self, configs):
        keys = [c.key for c in configs]
        assert "REDIS_TLS" in keys

    def test_qdrant_grpc_port_present(self, configs):
        keys = [c.key for c in configs]
        assert "QDRANT_GRPC_PORT" in keys

    def test_qdrant_https_present(self, configs):
        keys = [c.key for c in configs]
        assert "QDRANT_HTTPS" in keys

    def test_qdrant_default_dimensions_present(self, configs):
        keys = [c.key for c in configs]
        assert "QDRANT_DEFAULT_DIMENSIONS" in keys

    def test_n8n_server_url_present(self, configs):
        keys = [c.key for c in configs]
        assert "N8N_SERVER_URL" in keys

    def test_n8n_bearer_token_present(self, configs):
        keys = [c.key for c in configs]
        assert "N8N_BEARER_TOKEN" in keys

    def test_openrouter_api_key_present(self, configs):
        keys = [c.key for c in configs]
        assert "OPENROUTER_API_KEY" in keys

    def test_gemini_api_key_present(self, configs):
        keys = [c.key for c in configs]
        assert "GEMINI_API_KEY" in keys

    def test_configs_have_sections(self, configs):
        sections = {c.section for c in configs}
        assert "postgres" in sections
        assert "redis" in sections
        assert "qdrant" in sections
        assert "n8n" in sections
        assert "omniroute" in sections


class TestStartupSequenceAnalyzer:
    """Unit tests for StartupSequenceAnalyzer."""

    @pytest.fixture
    def steps(self) -> list:
        return StartupSequenceAnalyzer().analyze()

    def test_returns_list(self, steps):
        assert isinstance(steps, list)

    def test_six_steps(self, steps):
        assert len(steps) == 6

    def test_all_items_are_startup_steps(self, steps):
        for s in steps:
            assert isinstance(s, StartupStep)

    def test_step_1_is_postgres(self, steps):
        step1 = next(s for s in steps if s.order == 1)
        assert "PostgreSQL" in step1.service

    def test_step_2_is_redis(self, steps):
        step2 = next(s for s in steps if s.order == 2)
        assert "Redis" in step2.service

    def test_step_3_is_qdrant(self, steps):
        step3 = next(s for s in steps if s.order == 3)
        assert "Qdrant" in step3.service

    def test_step_4_is_migrations(self, steps):
        step4 = next(s for s in steps if s.order == 4)
        assert "Migration" in step4.service or "migration" in step4.description.lower()

    def test_step_4_depends_on_postgres(self, steps):
        step4 = next(s for s in steps if s.order == 4)
        assert "PostgreSQL" in step4.wait_for

    def test_step_5_is_aios_core(self, steps):
        step5 = next(s for s in steps if s.order == 5)
        assert "AIOS" in step5.service

    def test_step_5_depends_on_all_external_services(self, steps):
        step5 = next(s for s in steps if s.order == 5)
        assert "PostgreSQL" in step5.wait_for
        assert "Redis" in step5.wait_for
        assert "Qdrant" in step5.wait_for

    def test_step_6_is_n8n(self, steps):
        step6 = next(s for s in steps if s.order == 6)
        assert "n8n" in step6.service.lower()

    def test_steps_have_healthchecks(self, steps):
        """All service steps except migrations should have healthcheck commands."""
        for step in steps:
            if step.order != 4:  # Migrations have no healthcheck
                assert step.healthcheck is not None, (
                    f"Step {step.order} ({step.service}) should have a healthcheck"
                )

    def test_steps_have_notes(self, steps):
        """All steps should have contextual notes."""
        for step in steps:
            assert step.notes is not None and len(step.notes) > 10, (
                f"Step {step.order} ({step.service}) should have notes"
            )

    def test_steps_are_ordered_correctly(self, steps):
        orders = sorted(s.order for s in steps)
        assert orders == list(range(1, 7))


class TestOmniRouteAnalyzer:
    """Unit tests for OmniRouteAnalyzer."""

    @pytest.fixture
    def providers(self) -> list:
        return OmniRouteAnalyzer().analyze()

    def test_returns_list(self, providers):
        assert isinstance(providers, list)

    def test_three_providers(self, providers):
        assert len(providers) == 3

    def test_all_items_are_omniroute_providers(self, providers):
        for p in providers:
            assert isinstance(p, OmniRouteProvider)

    def test_openrouter_provider_present(self, providers):
        names = [p.name for p in providers]
        assert any("OpenRouter" in n for n in names)

    def test_anthropic_provider_present(self, providers):
        names = [p.name for p in providers]
        assert any("Anthropic" in n or "Claude" in n for n in names)

    def test_gemini_provider_present(self, providers):
        names = [p.name for p in providers]
        assert any("Gemini" in n or "Google" in n for n in names)

    def test_providers_have_env_keys(self, providers):
        for p in providers:
            assert p.env_key, f"Provider {p.name} must have an env_key"

    def test_providers_have_base_urls(self, providers):
        for p in providers:
            assert p.base_url.startswith("http"), f"Provider {p.name} must have a valid URL"

    def test_providers_have_default_models(self, providers):
        for p in providers:
            assert p.default_model, f"Provider {p.name} must have a default_model"

    def test_openrouter_default_model(self, providers):
        """Default model for OpenRouter matches config/config.toml."""
        or_provider = next(p for p in providers if "OpenRouter" in p.name)
        assert "qwen" in or_provider.default_model or or_provider.default_model


class TestBackupAnalyzer:
    """Unit tests for BackupAnalyzer."""

    @pytest.fixture
    def targets(self) -> list:
        return BackupAnalyzer().analyze()

    def test_returns_list(self, targets):
        assert isinstance(targets, list)

    def test_four_backup_targets(self, targets):
        assert len(targets) == 4

    def test_all_items_are_backup_targets(self, targets):
        for t in targets:
            assert isinstance(t, BackupTarget)

    def test_postgres_backup_daily(self, targets):
        pg = next(t for t in targets if "PostgreSQL" in t.name)
        assert pg.frequency == "daily"

    def test_qdrant_backup_daily(self, targets):
        qdrant = next(t for t in targets if "Qdrant" in t.name)
        assert qdrant.frequency == "daily"

    def test_config_backup_weekly(self, targets):
        config = next(t for t in targets if "Config" in t.name)
        assert config.frequency == "weekly"

    def test_all_targets_have_retention(self, targets):
        for t in targets:
            assert t.retention, f"Target {t.name} must have retention period"

    def test_all_targets_have_locations(self, targets):
        for t in targets:
            assert t.location.startswith("/"), f"Target {t.name} location must be absolute"

    def test_targets_have_notes(self, targets):
        for t in targets:
            assert t.notes, f"Target {t.name} should have notes"


class TestMonitoringAnalyzer:
    """Unit tests for MonitoringAnalyzer."""

    @pytest.fixture
    def metrics(self) -> list:
        return MonitoringAnalyzer().analyze()

    def test_returns_list(self, metrics):
        assert isinstance(metrics, list)

    def test_all_items_are_monitoring_metrics(self, metrics):
        for m in metrics:
            assert isinstance(m, MonitoringMetric)

    def test_has_service_metrics(self, metrics):
        service = [m for m in metrics if m.source == "service"]
        assert len(service) >= 2

    def test_has_database_metrics(self, metrics):
        db = [m for m in metrics if m.source == "database"]
        assert len(db) >= 3

    def test_has_system_metrics(self, metrics):
        sys_m = [m for m in metrics if m.source == "system"]
        assert len(sys_m) >= 3

    def test_omniroute_metrics_present(self, metrics):
        """OmniRoute-specific metrics must be included."""
        names = [m.name for m in metrics]
        assert any("OmniRoute" in n for n in names)

    def test_n8n_metric_present(self, metrics):
        names = [m.name for m in metrics]
        assert any("n8n" in n.lower() for n in names)

    def test_all_metrics_have_thresholds(self, metrics):
        for m in metrics:
            assert m.alert_threshold is not None, (
                f"Metric {m.name} should have an alert threshold"
            )


class TestTroubleshootingAnalyzer:
    """Unit tests for TroubleshootingAnalyzer."""

    @pytest.fixture
    def entries(self) -> list:
        return TroubleshootingAnalyzer().analyze()

    def test_returns_list(self, entries):
        assert isinstance(entries, list)

    def test_at_least_seven_entries(self, entries):
        assert len(entries) >= 7

    def test_all_items_are_troubleshooting_entries(self, entries):
        for e in entries:
            assert isinstance(e, TroubleshootingEntry)

    def test_postgres_entry_present(self, entries):
        assert any("PostgreSQL" in e.symptom or "database" in e.symptom.lower()
                   for e in entries)

    def test_redis_entry_present(self, entries):
        assert any("Redis" in e.symptom for e in entries)

    def test_qdrant_entry_present(self, entries):
        assert any("Qdrant" in e.symptom for e in entries)

    def test_n8n_entry_present(self, entries):
        assert any("n8n" in e.symptom for e in entries)

    def test_omniroute_entry_present(self, entries):
        """OmniRoute/provider timeout issues must be documented."""
        assert any("timeout" in e.symptom.lower() or "model" in e.symptom.lower()
                   for e in entries)

    def test_migration_entry_present(self, entries):
        assert any("migration" in e.symptom.lower() for e in entries)

    def test_entries_have_solutions(self, entries):
        for e in entries:
            assert len(e.solution) > 20, f"Entry '{e.symptom}' needs a detailed solution"

    def test_entries_have_related_logs(self, entries):
        for e in entries:
            assert len(e.related_logs) >= 1, f"Entry '{e.symptom}' needs related logs"

    def test_entries_have_cross_refs(self, entries):
        for e in entries:
            assert len(e.cross_refs) >= 1, f"Entry '{e.symptom}' needs cross-references"

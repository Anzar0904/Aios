"""
ops_engine.py — Operations Guide Generator Engine.

Orchestrates analysis and rendering of operational documentation.

Usage:
    engine = OperationsGeneratorEngine(project_root=Path("/path/to/aios"))
    result = engine.run()

Generation is idempotent: re-running overwrites only the docs/operations/
directory and leaves all other documentation untouched.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

from aios.docgen.ops_analyzers import (
    BackupAnalyzer,
    ConfigurationAnalyzer,
    MonitoringAnalyzer,
    OmniRouteAnalyzer,
    ServiceDeploymentAnalyzer,
    StartupSequenceAnalyzer,
    TroubleshootingAnalyzer,
)
from aios.docgen.ops_models import OperationsGenerationResult
from aios.docgen.ops_renderers import (
    render_backup_restore,
    render_configuration,
    render_deployment,
    render_local_setup,
    render_monitoring,
    render_production_checklist,
    render_readme_index,
    render_startup,
    render_troubleshooting,
)

logger = logging.getLogger(__name__)


class OperationsGeneratorEngine:
    """
    Orchestrates the analysis and generation of operational documentation.

    Analyzes deployment requirements, configuration parameters, startup sequences,
    OmniRoute provider configuration, and operational procedures to generate
    comprehensive operations guides under docs/operations/.
    """

    def __init__(self, project_root: Optional[Path] = None) -> None:
        """
        Initialize the operations generator engine.

        Args:
            project_root: Root directory of the AIOS project. Defaults to cwd.
        """
        self._root = project_root or Path.cwd()
        self._output_dir = self._root / "docs" / "operations"

    def run(self) -> OperationsGenerationResult:
        """
        Run the full operations guide generation pipeline.

        Returns:
            OperationsGenerationResult with status, timing, and file list.
        """
        start = time.time()
        result = OperationsGenerationResult()

        try:
            # Analysis phase
            logger.info("OperationsGeneratorEngine: starting analysis phase...")

            deployments = self._analyze_deployments()
            configs = self._analyze_configuration()
            startup_steps = self._analyze_startup()
            backup_targets = self._analyze_backups()
            metrics = self._analyze_monitoring()
            troubleshooting = self._analyze_troubleshooting()
            omniroute_providers = self._analyze_omniroute()

            logger.info(f"  Analyzed {len(deployments)} service deployments")
            logger.info(f"  Analyzed {len(configs)} configuration parameters")
            logger.info(f"  Analyzed {len(startup_steps)} startup steps")
            logger.info(f"  Analyzed {len(omniroute_providers)} OmniRoute providers")

            # Rendering phase
            logger.info("OperationsGeneratorEngine: starting rendering phase...")
            rendered_guides = self._render_all(
                deployments=deployments,
                configs=configs,
                startup_steps=startup_steps,
                backup_targets=backup_targets,
                metrics=metrics,
                troubleshooting=troubleshooting,
                omniroute_providers=omniroute_providers,
            )

            # Writing phase
            logger.info(f"OperationsGeneratorEngine: writing to {self._output_dir} ...")
            self._output_dir.mkdir(parents=True, exist_ok=True)

            for filename, content in rendered_guides.items():
                file_path = self._output_dir / filename
                file_path.write_text(content, encoding="utf-8")
                logger.info(f"  Written: {filename} ({len(content)} bytes)")
                result.files_written.append(str(file_path))

            result.status = "success"
            result.guides_generated = len(rendered_guides)
            result.elapsed = time.time() - start
            logger.info(
                f"OperationsGeneratorEngine: complete in {result.elapsed:.2f}s — "
                f"status={result.status} guides={result.guides_generated}"
            )

        except Exception as e:
            result.status = "failed"
            result.errors.append(str(e))
            result.elapsed = time.time() - start
            logger.exception("OperationsGeneratorEngine: generation failed")

        return result

    def _analyze_deployments(self):
        """Analyze service deployment requirements."""
        analyzer = ServiceDeploymentAnalyzer()
        return analyzer.analyze(self._root)

    def _analyze_configuration(self):
        """Analyze configuration parameters."""
        analyzer = ConfigurationAnalyzer()
        return analyzer.analyze(self._root)

    def _analyze_startup(self):
        """Analyze startup sequence."""
        analyzer = StartupSequenceAnalyzer()
        return analyzer.analyze()

    def _analyze_backups(self):
        """Analyze backup requirements."""
        analyzer = BackupAnalyzer()
        return analyzer.analyze()

    def _analyze_monitoring(self):
        """Analyze monitoring metrics."""
        analyzer = MonitoringAnalyzer()
        return analyzer.analyze()

    def _analyze_troubleshooting(self):
        """Analyze troubleshooting scenarios."""
        analyzer = TroubleshootingAnalyzer()
        return analyzer.analyze()

    def _analyze_omniroute(self):
        """Analyze OmniRoute provider configuration."""
        analyzer = OmniRouteAnalyzer()
        return analyzer.analyze()

    def _render_all(self, **kwargs) -> dict[str, str]:
        """Render all operational guide files."""
        guides = {}

        # Local setup guide
        guides["local_setup.md"] = render_local_setup(kwargs["deployments"])

        # Configuration guide (includes OmniRoute providers)
        guides["configuration.md"] = render_configuration(
            kwargs["configs"], kwargs["omniroute_providers"]
        )

        # Deployment guide
        guides["deployment.md"] = render_deployment(kwargs["deployments"])

        # Startup sequence guide
        guides["startup.md"] = render_startup(kwargs["startup_steps"])

        # Monitoring guide
        guides["monitoring.md"] = render_monitoring(kwargs["metrics"])

        # Backup & restore guide
        guides["backup_restore.md"] = render_backup_restore(kwargs["backup_targets"])

        # Troubleshooting guide
        guides["troubleshooting.md"] = render_troubleshooting(kwargs["troubleshooting"])

        # Production checklist
        guides["production_checklist.md"] = render_production_checklist()

        # Index
        guides["README.md"] = render_readme_index(len(guides))

        return guides

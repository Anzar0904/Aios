"""
refgen_engine.py — Reference Generator Engine.

Orchestrates discovery, rendering, and writing of API & Service reference documentation.

Usage:
    engine = ReferenceGeneratorEngine(project_root=Path("/path/to/aios"))
    result = engine.run()

Generation is idempotent: re-running overwrites only the docs/reference/
directory and leaves all other documentation untouched.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import List, Optional

from aios.docgen.refgen_discoverers import ServiceReferenceDiscoverer
from aios.docgen.refgen_models import ServiceInterface
from aios.docgen.refgen_renderers import (
    render_api_reference,
    render_dependency_injection_reference,
    render_interfaces_reference,
    render_lifecycle_reference,
    render_reference_index,
    render_services_reference,
)

logger = logging.getLogger(__name__)


class ReferenceGeneratorEngine:
    """
    Orchestrates the discovery and generation of API & Service reference documentation.

    Discovers services with detailed API information (method signatures, parameters,
    return types, exceptions, lifecycle methods) and generates comprehensive reference
    documentation in docs/reference/.
    """

    def __init__(self, project_root: Optional[Path] = None) -> None:
        """
        Initialize the reference generator engine.

        Args:
            project_root: Root directory of the AIOS project. Defaults to cwd.
        """
        self._root = project_root or Path.cwd()
        self._output_dir = self._root / "docs" / "reference"
        self._services_root = self._root / "core" / "src" / "aios" / "services"
        self._src_root = self._root / "core" / "src"

    def run(self) -> ReferenceGenerationResult:
        """
        Run the full reference generation pipeline.

        Returns:
            ReferenceGenerationResult with status, timing, and file list.
        """
        start = time.time()
        result = ReferenceGenerationResult()

        try:
            # Discovery phase
            logger.info("ReferenceGeneratorEngine: starting discovery phase...")
            services = self._discover_services()
            result.services_discovered = len(services)
            logger.info(f"  Discovered {len(services)} services with API details")

            # Rendering phase
            logger.info("ReferenceGeneratorEngine: starting rendering phase...")
            rendered_files = self._render_all(services)

            # Writing phase
            logger.info(f"ReferenceGeneratorEngine: writing to {self._output_dir} ...")
            self._output_dir.mkdir(parents=True, exist_ok=True)
            for filename, content in rendered_files.items():
                file_path = self._output_dir / filename
                file_path.write_text(content, encoding="utf-8")
                logger.info(f"  Written: {filename} ({len(content)} bytes)")
                result.files_written.append(str(file_path))

            result.status = "success"
            result.elapsed = time.time() - start
            logger.info(
                f"ReferenceGeneratorEngine: complete in {result.elapsed:.2f}s — "
                f"status={result.status} files={len(result.files_written)}"
            )

        except Exception as e:
            result.status = "failed"
            result.errors.append(str(e))
            result.elapsed = time.time() - start
            logger.exception("ReferenceGeneratorEngine: generation failed")

        return result

    def _discover_services(self) -> List[ServiceInterface]:
        """Discover services with enhanced API information."""
        discoverer = ServiceReferenceDiscoverer(
            services_root=self._services_root,
            src_root=self._src_root,
        )
        return discoverer.discover()

    def _render_all(self, services: List[ServiceInterface]) -> dict[str, str]:
        """Render all reference documentation files."""
        return {
            "services.md": render_services_reference(services),
            "interfaces.md": render_interfaces_reference(services),
            "lifecycle.md": render_lifecycle_reference(services),
            "dependency_injection.md": render_dependency_injection_reference(services),
            "api_reference.md": render_api_reference(services),
            "README.md": render_reference_index(services),
        }


class ReferenceGenerationResult:
    """Result of a reference generation run."""

    def __init__(self) -> None:
        self.status: str = "pending"
        self.elapsed: float = 0.0
        self.services_discovered: int = 0
        self.files_written: List[str] = []
        self.errors: List[str] = []

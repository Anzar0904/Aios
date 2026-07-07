"""
docgen/engine.py — Documentation Generation Engine.

Orchestrates discovery, rendering, and writing of generated documentation.

Usage:
    engine = DocGeneratorEngine(project_root=Path("/path/to/aios"))
    result = engine.run()

Generation is idempotent: re-running overwrites only the docs/generated/
directory and leaves all other documentation untouched.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

from aios.docgen.discoverers import (
    DIBindingDiscoverer,
    DbModelDiscoverer,
    ProviderDiscoverer,
    RepositoryDiscoverer,
    RuntimeComponentDiscoverer,
    ServiceDiscoverer,
    SkillDiscoverer,
)
from aios.docgen.models import (
    GeneratedFile,
    GenerationResult,
    GenerationStatus,
)
from aios.docgen.renderers import (
    render_db_model_catalog,
    render_dependency_graph,
    render_index,
    render_provider_catalog,
    render_repository_catalog,
    render_runtime_catalog,
    render_service_catalog,
    render_skill_catalog,
)

logger = logging.getLogger(__name__)


class DocGeneratorEngine:
    """
    Documentation Generation Engine for the Personal AI OS.

    Discovers components through static AST analysis (no runtime imports)
    and produces Markdown documentation into docs/generated/.

    Design Principles:
    - Idempotent: re-running produces identical output given unchanged source.
    - Non-destructive: only writes inside docs/generated/; handwritten docs untouched.
    - No side-effects on the running system: purely reads source code.
    - Deterministic ordering: all lists are sorted alphabetically.
    """

    _OUTPUT_SUBDIR = "generated"

    def __init__(self, project_root: Optional[Path] = None) -> None:
        if project_root is None:
            # Default: two levels up from this file (core/src/aios/docgen → project root)
            project_root = Path(__file__).parent.parent.parent.parent.parent

        self._project_root = project_root.resolve()
        self._core_src = self._project_root / "core" / "src"
        self._aios_src = self._core_src / "aios"
        self._services_root = self._aios_src / "services"
        self._providers_root = self._aios_src / "providers"
        self._bootstrap_file = self._aios_src / "bootstrap.py"
        self._bootstrap_modules = self._aios_src / "bootstrap_modules"
        self._skills_root = self._project_root / "skills"
        self._docs_root = self._project_root / "docs"
        self._output_dir = self._docs_root / self._OUTPUT_SUBDIR

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> GenerationResult:
        """
        Execute a full documentation generation run.

        Returns a GenerationResult summarising what was produced and any
        warnings or errors encountered.
        """
        start = time.time()
        result = GenerationResult(status=GenerationStatus.SUCCESS)

        logger.info("DocGeneratorEngine: starting discovery phase...")

        # --- Discovery Phase ---------------------------------------------------
        try:
            services = ServiceDiscoverer(self._services_root, self._core_src).discover()
            result.services_count = len(services)
            logger.info("  Discovered %d services", len(services))
        except Exception as exc:
            logger.warning("Service discovery failed: %s", exc)
            result.warnings.append(f"Service discovery: {exc}")
            services = []

        try:
            repositories = RepositoryDiscoverer(self._services_root, self._core_src).discover()
            result.repositories_count = len(repositories)
            logger.info("  Discovered %d repositories", len(repositories))
        except Exception as exc:
            logger.warning("Repository discovery failed: %s", exc)
            result.warnings.append(f"Repository discovery: {exc}")
            repositories = []

        try:
            skills = SkillDiscoverer(self._skills_root).discover()
            result.skills_count = len(skills)
            logger.info("  Discovered %d skills", len(skills))
        except Exception as exc:
            logger.warning("Skill discovery failed: %s", exc)
            result.warnings.append(f"Skill discovery: {exc}")
            skills = []

        try:
            providers = ProviderDiscoverer(self._providers_root, self._core_src).discover()
            result.providers_count = len(providers)
            logger.info("  Discovered %d providers", len(providers))
        except Exception as exc:
            logger.warning("Provider discovery failed: %s", exc)
            result.warnings.append(f"Provider discovery: {exc}")
            providers = []

        try:
            runtime = RuntimeComponentDiscoverer(
                self._services_root, self._core_src
            ).discover()
            result.runtime_count = len(runtime)
            logger.info("  Discovered %d runtime components", len(runtime))
        except Exception as exc:
            logger.warning("Runtime discovery failed: %s", exc)
            result.warnings.append(f"Runtime discovery: {exc}")
            runtime = []

        try:
            db_models = DbModelDiscoverer(self._services_root, self._core_src).discover()
            result.db_models_count = len(db_models)
            logger.info("  Discovered %d DB models", len(db_models))
        except Exception as exc:
            logger.warning("DB model discovery failed: %s", exc)
            result.warnings.append(f"DB model discovery: {exc}")
            db_models = []

        try:
            di_bindings = []
            if self._bootstrap_modules.exists() and self._bootstrap_modules.is_dir():
                for f in self._bootstrap_modules.glob("*.py"):
                    di_bindings.extend(DIBindingDiscoverer(f).discover())
            if self._bootstrap_file.exists():
                di_bindings.extend(DIBindingDiscoverer(self._bootstrap_file).discover())
            
            result.di_bindings_count = len(di_bindings)
            logger.info("  Discovered %d DI bindings", len(di_bindings))
        except Exception as exc:
            logger.warning("DI binding discovery failed: %s", exc)
            result.warnings.append(f"DI binding discovery: {exc}")
            di_bindings = []

        # --- Rendering Phase --------------------------------------------------
        logger.info("DocGeneratorEngine: starting rendering phase...")

        documents = {
            "services.md": render_service_catalog(services),
            "repositories.md": render_repository_catalog(repositories),
            "skills.md": render_skill_catalog(skills),
            "providers.md": render_provider_catalog(providers),
            "runtime.md": render_runtime_catalog(runtime),
            "db_models.md": render_db_model_catalog(db_models),
            "dependency_graph.md": render_dependency_graph(di_bindings),
        }

        # --- Writing Phase -----------------------------------------------------
        logger.info("DocGeneratorEngine: writing to %s ...", self._output_dir)
        try:
            self._output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            result.errors.append(f"Cannot create output dir: {exc}")
            result.status = GenerationStatus.FAILED
            result.elapsed_seconds = time.time() - start
            return result

        generated_paths: list[str] = []

        for filename, content in documents.items():
            out_path = self._output_dir / filename
            try:
                out_path.write_text(content, encoding="utf-8")
                size = out_path.stat().st_size
                title = filename.replace(".md", "").replace("_", " ").title()
                # Count entries heuristically via section headings (###)
                entry_count = content.count("\n### ")
                result.files.append(
                    GeneratedFile(
                        path=str(out_path),
                        title=title,
                        entry_count=entry_count,
                        size_bytes=size,
                    )
                )
                generated_paths.append(str(out_path))
                logger.info("  Written: %s (%d bytes)", out_path.name, size)
            except OSError as exc:
                err = f"Failed to write {filename}: {exc}"
                result.errors.append(err)
                logger.error(err)

        # Write index
        index_content = render_index(
            services_count=result.services_count,
            repositories_count=result.repositories_count,
            skills_count=result.skills_count,
            providers_count=result.providers_count,
            runtime_count=result.runtime_count,
            db_models_count=result.db_models_count,
            di_bindings_count=result.di_bindings_count,
            generated_files=generated_paths,
        )
        index_path = self._output_dir / "README.md"
        try:
            index_path.write_text(index_content, encoding="utf-8")
            result.files.append(
                GeneratedFile(
                    path=str(index_path),
                    title="Index",
                    entry_count=len(documents),
                    size_bytes=index_path.stat().st_size,
                )
            )
            generated_paths.append(str(index_path))
        except OSError as exc:
            result.errors.append(f"Failed to write index: {exc}")

        # Determine final status
        if result.errors:
            result.status = (
                GenerationStatus.PARTIAL if result.files else GenerationStatus.FAILED
            )
        else:
            result.status = GenerationStatus.SUCCESS

        result.elapsed_seconds = time.time() - start
        logger.info(
            "DocGeneratorEngine: complete in %.2fs — status=%s files=%d",
            result.elapsed_seconds,
            result.status,
            len(result.files),
        )
        return result

    @property
    def output_dir(self) -> Path:
        """Return the configured output directory (docs/generated/)."""
        return self._output_dir

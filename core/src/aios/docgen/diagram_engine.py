"""
diagram_engine.py — Diagram Generator Engine.

Orchestrates analysis and rendering of architecture diagrams.

Usage:
    engine = DiagramGeneratorEngine(project_root=Path("/path/to/aios"))
    result = engine.run()

Generation is idempotent: re-running overwrites only the docs/diagrams/
directory and leaves all other documentation untouched.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Optional

from aios.docgen.diagram_analyzers import (
    ArchitectureComponentAnalyzer,
    BootstrapSequenceAnalyzer,
    LifecycleAnalyzer,
    PersistenceAnalyzer,
    ServiceDependencyAnalyzer,
)
from aios.docgen.diagram_models import DiagramGenerationResult
from aios.docgen.diagram_renderers import (
    render_agent_interaction_flow,
    render_bootstrap_sequence,
    render_di_graph,
    render_diagrams_index,
    render_hybrid_retrieval_pipeline,
    render_lifecycle_diagram,
    render_omniroute_architecture,
    render_overall_architecture,
    render_persistence_architecture,
    render_semantic_memory_pipeline,
    render_service_dependency_graph,
)
from aios.docgen.discoverers import DIBindingDiscoverer

logger = logging.getLogger(__name__)


class DiagramGeneratorEngine:
    """
    Orchestrates the analysis and generation of architecture diagrams.

    Analyzes the codebase to extract architectural information and generates
    Mermaid diagrams for visualization in docs/diagrams/.
    """

    def __init__(self, project_root: Optional[Path] = None) -> None:
        """
        Initialize the diagram generator engine.

        Args:
            project_root: Root directory of the AIOS project. Defaults to cwd.
        """
        self._root = project_root or Path.cwd()
        self._output_dir = self._root / "docs" / "diagrams"
        self._services_root = self._root / "core" / "src" / "aios" / "services"
        self._src_root = self._root / "core" / "src"
        self._bootstrap_file = self._root / "core" / "src" / "aios" / "bootstrap.py"

    def run(self) -> DiagramGenerationResult:
        """
        Run the full diagram generation pipeline.

        Returns:
            DiagramGenerationResult with status, timing, and file list.
        """
        start = time.time()
        result = DiagramGenerationResult()

        try:
            # Analysis phase
            logger.info("DiagramGeneratorEngine: starting analysis phase...")

            components = self._analyze_components()
            services = self._analyze_services()
            di_bindings = self._analyze_di_bindings()
            lifecycle_phases = self._analyze_lifecycle()
            bootstrap_steps = self._analyze_bootstrap()
            persistence_layers = self._analyze_persistence()

            logger.info(f"  Analyzed {len(components)} components")
            logger.info(f"  Analyzed {len(services)} services")
            logger.info(f"  Analyzed {len(di_bindings)} DI bindings")
            logger.info(f"  Analyzed {len(lifecycle_phases)} lifecycle phases")

            # Rendering phase
            logger.info("DiagramGeneratorEngine: starting rendering phase...")
            rendered_diagrams = self._render_all(
                components=components,
                services=services,
                di_bindings=di_bindings,
                lifecycle_phases=lifecycle_phases,
                bootstrap_steps=bootstrap_steps,
                persistence_layers=persistence_layers,
            )

            # Writing phase
            logger.info(f"DiagramGeneratorEngine: writing to {self._output_dir} ...")
            self._output_dir.mkdir(parents=True, exist_ok=True)

            for filename, content in rendered_diagrams.items():
                file_path = self._output_dir / filename
                file_path.write_text(content, encoding="utf-8")
                logger.info(f"  Written: {filename} ({len(content)} bytes)")
                result.files_written.append(str(file_path))

            result.status = "success"
            result.diagrams_generated = len(rendered_diagrams)
            result.elapsed = time.time() - start
            logger.info(
                f"DiagramGeneratorEngine: complete in {result.elapsed:.2f}s — "
                f"status={result.status} diagrams={result.diagrams_generated}"
            )

        except Exception as e:
            result.status = "failed"
            result.errors.append(str(e))
            result.elapsed = time.time() - start
            logger.exception("DiagramGeneratorEngine: generation failed")

        return result

    def _analyze_components(self):
        """Analyze high-level architectural components."""
        analyzer = ArchitectureComponentAnalyzer()
        return analyzer.analyze()

    def _analyze_services(self):
        """Analyze service dependencies."""
        analyzer = ServiceDependencyAnalyzer(
            services_root=self._services_root,
            src_root=self._src_root,
        )
        return analyzer.analyze()

    def _analyze_di_bindings(self):
        """Analyze DI bindings."""
        discoverer = DIBindingDiscoverer(bootstrap_file=self._bootstrap_file)
        return discoverer.discover()

    def _analyze_lifecycle(self):
        """Analyze lifecycle phases."""
        analyzer = LifecycleAnalyzer(
            services_root=self._services_root,
            src_root=self._src_root,
        )
        return analyzer.analyze()

    def _analyze_bootstrap(self):
        """Analyze bootstrap sequence."""
        analyzer = BootstrapSequenceAnalyzer(bootstrap_file=self._bootstrap_file)
        return analyzer.analyze()

    def _analyze_persistence(self):
        """Analyze persistence layers."""
        analyzer = PersistenceAnalyzer()
        return analyzer.analyze(self._root)

    def _render_all(self, **kwargs) -> dict[str, str]:
        """Render all diagram files."""
        diagrams = {}

        # Overall architecture
        diagrams["architecture.md"] = render_overall_architecture(kwargs["components"])

        # Service dependency graph
        diagrams["dependency_graph.md"] = render_service_dependency_graph(kwargs["services"])

        # Lifecycle diagram (includes DI graph content)
        diagrams["lifecycle.md"] = render_lifecycle_diagram(kwargs["lifecycle_phases"])

        # Bootstrap sequence (runtime initialization)
        diagrams["runtime.md"] = render_bootstrap_sequence(kwargs["bootstrap_steps"])

        # Persistence architecture
        diagrams["persistence.md"] = render_persistence_architecture(kwargs["persistence_layers"])

        # Semantic memory pipeline
        diagrams["semantic_memory.md"] = render_semantic_memory_pipeline()

        # Hybrid retrieval pipeline
        diagrams["hybrid_retrieval.md"] = render_hybrid_retrieval_pipeline()

        # OmniRoute architecture
        diagrams["omniroute.md"] = render_omniroute_architecture()

        # Agent interaction flow
        diagrams["agents.md"] = render_agent_interaction_flow()

        # Index
        diagrams["README.md"] = render_diagrams_index(len(diagrams))

        return diagrams

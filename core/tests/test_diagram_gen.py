"""
test_diagram_gen.py — Tests for the Architecture Diagram Generator.

Verifies diagram generation, Mermaid syntax validity, cross-references,
idempotency, and handwritten documentation preservation.
"""

from pathlib import Path

import pytest
from aios.docgen.diagram_engine import DiagramGeneratorEngine


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def diagrams_dir(project_root):
    """Return the diagrams output directory."""
    return project_root / "docs" / "diagrams"


@pytest.fixture
def run_generator_once(project_root):
    """Run the diagram generator once and return the result."""
    engine = DiagramGeneratorEngine(project_root=project_root)
    result = engine.run()
    return result


# ==============================================================================
# Generation Status Tests
# ==============================================================================


class TestDiagramGenerationStatus:
    """Test that diagram generation completes successfully."""

    def test_generation_succeeds(self, run_generator_once):
        """Diagram generation should complete with success status."""
        assert run_generator_once.status == "success"

    def test_no_errors(self, run_generator_once):
        """Diagram generation should produce no errors."""
        assert len(run_generator_once.errors) == 0

    def test_ten_diagrams_produced(self, run_generator_once):
        """Diagram generation should produce exactly 10 files."""
        assert run_generator_once.diagrams_generated == 10

    def test_elapsed_is_positive(self, run_generator_once):
        """Generation should complete in positive time."""
        assert run_generator_once.elapsed > 0


# ==============================================================================
# File Existence Tests
# ==============================================================================


class TestDiagramFilesExist:
    """Test that all expected diagram files are created."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.mark.parametrize(
        "filename",
        [
            "README.md",
            "architecture.md",
            "dependency_graph.md",
            "lifecycle.md",
            "runtime.md",
            "persistence.md",
            "semantic_memory.md",
            "hybrid_retrieval.md",
            "omniroute.md",
            "agents.md",
        ],
    )
    def test_file_exists(self, diagrams_dir, filename):
        """Each expected diagram file should exist."""
        file_path = diagrams_dir / filename
        assert file_path.exists(), f"{filename} should exist"

    @pytest.mark.parametrize(
        "filename",
        [
            "README.md",
            "architecture.md",
            "dependency_graph.md",
            "lifecycle.md",
            "runtime.md",
            "persistence.md",
            "semantic_memory.md",
            "hybrid_retrieval.md",
            "omniroute.md",
            "agents.md",
        ],
    )
    def test_file_not_empty(self, diagrams_dir, filename):
        """Each diagram file should have content."""
        file_path = diagrams_dir / filename
        content = file_path.read_text()
        assert len(content) > 0, f"{filename} should not be empty"


# ==============================================================================
# Mermaid Syntax Tests
# ==============================================================================


class TestMermaidSyntax:
    """Test that generated diagrams have valid Mermaid syntax."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.mark.parametrize(
        "filename",
        [
            "architecture.md",
            "dependency_graph.md",
            "lifecycle.md",
            "runtime.md",
            "persistence.md",
            "semantic_memory.md",
            "hybrid_retrieval.md",
            "omniroute.md",
            "agents.md",
        ],
    )
    def test_has_mermaid_code_block(self, diagrams_dir, filename):
        """Each diagram should have a Mermaid code block."""
        content = (diagrams_dir / filename).read_text()
        assert "```mermaid" in content, f"{filename} should have Mermaid code block"
        assert "```" in content.split("```mermaid")[1], f"{filename} should close Mermaid block"

    @pytest.mark.parametrize(
        "filename,diagram_type",
        [
            ("architecture.md", "graph"),
            ("dependency_graph.md", "graph"),
            ("lifecycle.md", "stateDiagram"),
            ("runtime.md", "sequenceDiagram"),
            ("persistence.md", "graph"),
            ("semantic_memory.md", "graph"),
            ("hybrid_retrieval.md", "graph"),
            ("omniroute.md", "graph"),
            ("agents.md", "sequenceDiagram"),
        ],
    )
    def test_has_correct_diagram_type(self, diagrams_dir, filename, diagram_type):
        """Each diagram should declare the correct Mermaid diagram type."""
        content = (diagrams_dir / filename).read_text()
        assert diagram_type in content, f"{filename} should contain {diagram_type}"


# ==============================================================================
# Architecture Diagram Tests
# ==============================================================================


class TestArchitectureDiagram:
    """Test the architecture.md diagram content."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.fixture
    def content(self, diagrams_dir):
        """Load architecture.md content."""
        return (diagrams_dir / "architecture.md").read_text()

    def test_header_present(self, content):
        """Architecture diagram should have proper header."""
        assert "# AI OS Architecture" in content

    def test_generated_banner(self, content):
        """Architecture diagram should have auto-generated banner."""
        assert "AUTO-GENERATED" in content
        assert "DO NOT EDIT MANUALLY" in content

    def test_has_component_types_legend(self, content):
        """Architecture diagram should have legend."""
        assert "## Component Types" in content

    def test_has_nodes(self, content):
        """Architecture diagram should define nodes."""
        # Should have node definitions like: NodeName[Label]
        assert "[" in content and "]" in content

    def test_has_dependencies(self, content):
        """Architecture diagram should show dependencies."""
        assert "-->" in content or "--->" in content


# ==============================================================================
# Service Dependency Graph Tests
# ==============================================================================


class TestServiceDependencyGraph:
    """Test the dependency_graph.md diagram content."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.fixture
    def content(self, diagrams_dir):
        """Load dependency_graph.md content."""
        return (diagrams_dir / "dependency_graph.md").read_text()

    def test_header_present(self, content):
        """Dependency graph should have proper header."""
        assert "# Service Dependency Graph" in content

    def test_has_legend(self, content):
        """Dependency graph should have legend."""
        assert "## Legend" in content

    def test_shows_dependencies(self, content):
        """Dependency graph should show service dependencies."""
        assert "-->" in content


# ==============================================================================
# Lifecycle Diagram Tests
# ==============================================================================


class TestLifecycleDiagram:
    """Test the lifecycle.md diagram content."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.fixture
    def content(self, diagrams_dir):
        """Load lifecycle.md content."""
        return (diagrams_dir / "lifecycle.md").read_text()

    def test_header_present(self, content):
        """Lifecycle diagram should have proper header."""
        assert "# Runtime Lifecycle" in content

    def test_has_lifecycle_phases(self, content):
        """Lifecycle diagram should document phases."""
        assert "## Lifecycle Phases" in content
        assert "Initialization" in content or "initialization" in content


# ==============================================================================
# Bootstrap Sequence Tests
# ==============================================================================


class TestBootstrapSequence:
    """Test the runtime.md diagram content."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.fixture
    def content(self, diagrams_dir):
        """Load runtime.md content."""
        return (diagrams_dir / "runtime.md").read_text()

    def test_header_present(self, content):
        """Bootstrap sequence should have proper header."""
        assert "# Bootstrap Sequence" in content

    def test_has_sequence_diagram(self, content):
        """Bootstrap sequence should use sequence diagram."""
        assert "sequenceDiagram" in content

    def test_has_bootstrap_steps(self, content):
        """Bootstrap sequence should list steps."""
        assert "## Bootstrap Steps" in content or "Bootstrap" in content


# ==============================================================================
# Persistence Architecture Tests
# ==============================================================================


class TestPersistenceArchitecture:
    """Test the persistence.md diagram content."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.fixture
    def content(self, diagrams_dir):
        """Load persistence.md content."""
        return (diagrams_dir / "persistence.md").read_text()

    def test_header_present(self, content):
        """Persistence diagram should have proper header."""
        assert "# Persistence Architecture" in content

    def test_has_persistence_layers(self, content):
        """Persistence diagram should show layers."""
        assert "SQLite" in content or "PostgreSQL" in content or "Redis" in content or "Qdrant" in content


# ==============================================================================
# Semantic Memory Pipeline Tests
# ==============================================================================


class TestSemanticMemoryPipeline:
    """Test the semantic_memory.md diagram content."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.fixture
    def content(self, diagrams_dir):
        """Load semantic_memory.md content."""
        return (diagrams_dir / "semantic_memory.md").read_text()

    def test_header_present(self, content):
        """Semantic memory diagram should have proper header."""
        assert "# Semantic Memory Pipeline" in content

    def test_has_pipeline_stages(self, content):
        """Semantic memory diagram should describe pipeline."""
        assert "## Pipeline Stages" in content or "Pipeline" in content


# ==============================================================================
# Hybrid Retrieval Pipeline Tests
# ==============================================================================


class TestHybridRetrievalPipeline:
    """Test the hybrid_retrieval.md diagram content."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.fixture
    def content(self, diagrams_dir):
        """Load hybrid_retrieval.md content."""
        return (diagrams_dir / "hybrid_retrieval.md").read_text()

    def test_header_present(self, content):
        """Hybrid retrieval diagram should have proper header."""
        assert "# Hybrid Retrieval Pipeline" in content

    def test_has_keyword_and_semantic_paths(self, content):
        """Hybrid retrieval should show both search paths."""
        assert "Keyword" in content or "keyword" in content
        assert "Semantic" in content or "semantic" in content


# ==============================================================================
# OmniRoute Architecture Tests
# ==============================================================================


class TestOmniRouteArchitecture:
    """Test the omniroute.md diagram content."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.fixture
    def content(self, diagrams_dir):
        """Load omniroute.md content."""
        return (diagrams_dir / "omniroute.md").read_text()

    def test_header_present(self, content):
        """OmniRoute diagram should have proper header."""
        assert "# OmniRoute Architecture" in content

    def test_has_model_selection(self, content):
        """OmniRoute diagram should show model selection."""
        assert "Model" in content or "model" in content


# ==============================================================================
# Agent Interaction Flow Tests
# ==============================================================================


class TestAgentInteractionFlow:
    """Test the agents.md diagram content."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.fixture
    def content(self, diagrams_dir):
        """Load agents.md content."""
        return (diagrams_dir / "agents.md").read_text()

    def test_header_present(self, content):
        """Agent flow diagram should have proper header."""
        assert "# Agent Interaction Flow" in content

    def test_has_sequence_diagram(self, content):
        """Agent flow should use sequence diagram."""
        assert "sequenceDiagram" in content

    def test_has_agent_capabilities(self, content):
        """Agent flow should describe agent types."""
        assert "## Agent Capabilities" in content or "Agent" in content


# ==============================================================================
# README Index Tests
# ==============================================================================


class TestDiagramsIndex:
    """Test the README.md index content."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.fixture
    def content(self, diagrams_dir):
        """Load README.md content."""
        return (diagrams_dir / "README.md").read_text()

    def test_header_present(self, content):
        """README should have proper header."""
        assert "# Architecture Diagrams" in content

    def test_overview_section(self, content):
        """README should have overview."""
        assert "## Overview" in content

    def test_diagram_files_table(self, content):
        """README should list all diagram files."""
        assert "## Diagram Files" in content
        assert "architecture.md" in content
        assert "dependency_graph.md" in content
        assert "lifecycle.md" in content

    def test_viewing_instructions(self, content):
        """README should explain how to view diagrams."""
        assert "## Viewing Diagrams" in content
        assert "Mermaid" in content

    def test_regeneration_instructions(self, content):
        """README should have regeneration instructions."""
        assert "## Regeneration" in content
        assert "python -m aios.docgen.diagram_main" in content

    def test_cross_references(self, content):
        """README should have cross-references."""
        assert "## Cross-References" in content


# ==============================================================================
# Idempotency Tests
# ==============================================================================


class TestDiagramIdempotency:
    """Test that diagram generation is idempotent."""

    def test_same_diagram_count_on_rerun(self, project_root):
        """Re-running should generate the same number of diagrams."""
        engine = DiagramGeneratorEngine(project_root=project_root)
        result1 = engine.run()
        result2 = engine.run()

        assert result1.diagrams_generated == result2.diagrams_generated

    def test_same_file_count_on_rerun(self, project_root):
        """Re-running should produce the same number of files."""
        engine = DiagramGeneratorEngine(project_root=project_root)
        result1 = engine.run()
        result2 = engine.run()

        assert len(result1.files_written) == len(result2.files_written)


# ==============================================================================
# Handwritten Documentation Preservation Tests
# ==============================================================================


class TestHandwrittenDocsUntouched:
    """Test that diagram generation doesn't modify handwritten documentation."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.mark.parametrize(
        "doc_path",
        [
            "docs/00_PROJECT_VISION.md",
            "docs/README.md",
            "docs/generated/README.md",
            "docs/reference/README.md",
        ],
    )
    def test_handwritten_doc_unchanged(self, project_root, doc_path):
        """Handwritten documentation should remain unchanged after generation."""
        file_path = project_root / doc_path
        if not file_path.exists():
            pytest.skip(f"{doc_path} does not exist")

        # Store modification time before generation
        mtime_before = file_path.stat().st_mtime

        # Run generator
        engine = DiagramGeneratorEngine(project_root=project_root)
        engine.run()

        # Check modification time after generation
        mtime_after = file_path.stat().st_mtime

        assert mtime_before == mtime_after, f"{doc_path} was modified by generator"

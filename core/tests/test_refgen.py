"""
test_refgen.py — Tests for the API & Service Reference Generator.

Verifies reference generation, content accuracy, idempotency, and that
handwritten documentation remains untouched.
"""

from pathlib import Path

import pytest
from aios.docgen.refgen_engine import ReferenceGeneratorEngine


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def reference_dir(project_root):
    """Return the reference output directory."""
    return project_root / "docs" / "reference"


@pytest.fixture
def run_generator_once(project_root):
    """Run the reference generator once and return the result."""
    engine = ReferenceGeneratorEngine(project_root=project_root)
    result = engine.run()
    return result


# ==============================================================================
# Generation Status Tests
# ==============================================================================


class TestReferenceGenerationStatus:
    """Test that reference generation completes successfully."""

    def test_generation_succeeds(self, run_generator_once):
        """Reference generation should complete with success status."""
        assert run_generator_once.status == "success"

    def test_no_errors(self, run_generator_once):
        """Reference generation should produce no errors."""
        assert len(run_generator_once.errors) == 0

    def test_six_files_produced(self, run_generator_once):
        """Reference generation should produce exactly 6 files."""
        assert len(run_generator_once.files_written) == 6

    def test_services_discovered(self, run_generator_once):
        """Reference generation should discover services."""
        assert run_generator_once.services_discovered > 0

    def test_elapsed_is_positive(self, run_generator_once):
        """Generation should complete in positive time."""
        assert run_generator_once.elapsed > 0


# ==============================================================================
# File Existence Tests
# ==============================================================================


class TestReferenceFilesExist:
    """Test that all expected reference files are created."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.mark.parametrize(
        "filename",
        [
            "README.md",
            "services.md",
            "interfaces.md",
            "lifecycle.md",
            "dependency_injection.md",
            "api_reference.md",
        ],
    )
    def test_file_exists(self, reference_dir, filename):
        """Each expected reference file should exist."""
        file_path = reference_dir / filename
        assert file_path.exists(), f"{filename} should exist"

    @pytest.mark.parametrize(
        "filename",
        [
            "README.md",
            "services.md",
            "interfaces.md",
            "lifecycle.md",
            "dependency_injection.md",
            "api_reference.md",
        ],
    )
    def test_file_not_empty(self, reference_dir, filename):
        """Each reference file should have content."""
        file_path = reference_dir / filename
        content = file_path.read_text()
        assert len(content) > 0, f"{filename} should not be empty"


# ==============================================================================
# Services Reference Tests
# ==============================================================================


class TestServicesReference:
    """Test the services.md reference content."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.fixture
    def services_content(self, reference_dir):
        """Load services.md content."""
        return (reference_dir / "services.md").read_text()

    def test_header_present(self, services_content):
        """Services reference should have proper header."""
        assert "# Service API Reference" in services_content

    def test_generated_banner(self, services_content):
        """Services reference should have auto-generated banner."""
        assert "AUTO-GENERATED" in services_content
        assert "DO NOT EDIT MANUALLY" in services_content

    def test_summary_section(self, services_content):
        """Services reference should have summary statistics."""
        assert "## Summary" in services_content
        assert "Total Services" in services_content
        assert "Total Public Methods" in services_content

    def test_contains_service_entries(self, services_content):
        """Services reference should contain actual service documentation."""
        assert "### " in services_content  # Service headers
        assert "**Module**:" in services_content

    def test_method_signatures_present(self, services_content):
        """Services reference should document method signatures."""
        assert "```python" in services_content
        assert "def " in services_content

    def test_parameters_documented(self, services_content):
        """Services reference should document parameters."""
        assert "**Parameters**:" in services_content or "**Dependencies**:" in services_content


# ==============================================================================
# Interfaces Reference Tests
# ==============================================================================


class TestInterfacesReference:
    """Test the interfaces.md reference content."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.fixture
    def interfaces_content(self, reference_dir):
        """Load interfaces.md content."""
        return (reference_dir / "interfaces.md").read_text()

    def test_header_present(self, interfaces_content):
        """Interfaces reference should have proper header."""
        assert "# Interface to Implementation Reference" in interfaces_content

    def test_interface_registry_table(self, interfaces_content):
        """Interfaces reference should have interface registry table."""
        assert "## Interface Registry" in interfaces_content
        assert "| Interface | Implementation | Module |" in interfaces_content

    def test_standalone_implementations_section(self, interfaces_content):
        """Interfaces reference should list standalone implementations."""
        assert "## Standalone Implementations" in interfaces_content

    def test_interface_details_section(self, interfaces_content):
        """Interfaces reference should have detailed interface documentation."""
        assert "## Interface Details" in interfaces_content


# ==============================================================================
# Lifecycle Reference Tests
# ==============================================================================


class TestLifecycleReference:
    """Test the lifecycle.md reference content."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.fixture
    def lifecycle_content(self, reference_dir):
        """Load lifecycle.md content."""
        return (reference_dir / "lifecycle.md").read_text()

    def test_header_present(self, lifecycle_content):
        """Lifecycle reference should have proper header."""
        assert "# Service Lifecycle Reference" in lifecycle_content

    def test_lifecycle_phases_section(self, lifecycle_content):
        """Lifecycle reference should document lifecycle phases."""
        assert "## Lifecycle Phases" in lifecycle_content
        assert "Initialization" in lifecycle_content
        assert "Cleanup" in lifecycle_content

    def test_initialization_phase_section(self, lifecycle_content):
        """Lifecycle reference should document initialization phase."""
        assert "## Initialization Phase" in lifecycle_content

    def test_cleanup_phase_section(self, lifecycle_content):
        """Lifecycle reference should document cleanup phase."""
        assert "## Cleanup Phase" in lifecycle_content


# ==============================================================================
# Dependency Injection Reference Tests
# ==============================================================================


class TestDependencyInjectionReference:
    """Test the dependency_injection.md reference content."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.fixture
    def di_content(self, reference_dir):
        """Load dependency_injection.md content."""
        return (reference_dir / "dependency_injection.md").read_text()

    def test_header_present(self, di_content):
        """DI reference should have proper header."""
        assert "# Dependency Injection Reference" in di_content

    def test_dependency_graph_summary(self, di_content):
        """DI reference should have dependency graph summary."""
        assert "## Dependency Graph Summary" in di_content

    def test_service_dependencies_section(self, di_content):
        """DI reference should document service dependencies."""
        assert "## Service Dependencies" in di_content

    def test_injected_dependencies_table(self, di_content):
        """DI reference should have dependency tables."""
        assert "**Injected Dependencies**:" in di_content
        assert "| Parameter | Type | Required |" in di_content


# ==============================================================================
# API Reference Tests
# ==============================================================================


class TestAPIReference:
    """Test the api_reference.md complete reference content."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.fixture
    def api_content(self, reference_dir):
        """Load api_reference.md content."""
        return (reference_dir / "api_reference.md").read_text()

    def test_header_present(self, api_content):
        """API reference should have proper header."""
        assert "# Complete API Reference" in api_content

    def test_table_of_contents(self, api_content):
        """API reference should have table of contents."""
        assert "## Table of Contents" in api_content

    def test_service_sections(self, api_content):
        """API reference should have sections for services."""
        assert "## " in api_content  # Service sections
        assert "**Module**:" in api_content

    def test_methods_documented(self, api_content):
        """API reference should document methods."""
        assert "### Methods" in api_content or "#### " in api_content


# ==============================================================================
# README Index Tests
# ==============================================================================


class TestReferenceIndex:
    """Test the README.md index content."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.fixture
    def readme_content(self, reference_dir):
        """Load README.md content."""
        return (reference_dir / "README.md").read_text()

    def test_header_present(self, readme_content):
        """README should have proper header."""
        assert "# API & Service Reference" in readme_content

    def test_overview_section(self, readme_content):
        """README should have overview."""
        assert "## Overview" in readme_content

    def test_documentation_files_table(self, readme_content):
        """README should list all documentation files."""
        assert "## Documentation Files" in readme_content
        assert "services.md" in readme_content
        assert "interfaces.md" in readme_content
        assert "lifecycle.md" in readme_content
        assert "dependency_injection.md" in readme_content
        assert "api_reference.md" in readme_content

    def test_statistics_section(self, readme_content):
        """README should have statistics."""
        assert "## Statistics" in readme_content
        assert "**Services**:" in readme_content

    def test_regeneration_instructions(self, readme_content):
        """README should have regeneration instructions."""
        assert "## Regeneration" in readme_content
        assert "python -m aios.docgen.refgen" in readme_content

    def test_cross_references_section(self, readme_content):
        """README should have cross-references to other documentation."""
        assert "## Cross-References" in readme_content


# ==============================================================================
# Idempotency Tests
# ==============================================================================


class TestReferenceIdempotency:
    """Test that reference generation is idempotent."""

    def test_same_service_count_on_rerun(self, project_root):
        """Re-running the generator should discover the same number of services."""
        engine = ReferenceGeneratorEngine(project_root=project_root)
        result1 = engine.run()
        result2 = engine.run()

        assert result1.services_discovered == result2.services_discovered

    def test_same_file_count_on_rerun(self, project_root):
        """Re-running the generator should produce the same number of files."""
        engine = ReferenceGeneratorEngine(project_root=project_root)
        result1 = engine.run()
        result2 = engine.run()

        assert len(result1.files_written) == len(result2.files_written)

    def test_same_file_sizes_on_rerun(self, project_root, reference_dir):
        """Re-running the generator should produce files of the same size (modulo timestamps)."""
        engine = ReferenceGeneratorEngine(project_root=project_root)
        engine.run()

        sizes1 = {}
        for filename in [
            "services.md",
            "interfaces.md",
            "lifecycle.md",
            "dependency_injection.md",
            "api_reference.md",
            "README.md",
        ]:
            file_path = reference_dir / filename
            sizes1[filename] = file_path.stat().st_size

        # Run again
        engine.run()

        sizes2 = {}
        for filename in [
            "services.md",
            "interfaces.md",
            "lifecycle.md",
            "dependency_injection.md",
            "api_reference.md",
            "README.md",
        ]:
            file_path = reference_dir / filename
            sizes2[filename] = file_path.stat().st_size

        # File sizes should be very similar (within 200 bytes for timestamp differences)
        for filename in sizes1.keys():
            size_diff = abs(sizes1[filename] - sizes2[filename])
            assert size_diff < 200, f"{filename} size changed by {size_diff} bytes"


# ==============================================================================
# Handwritten Documentation Preservation Tests
# ==============================================================================


class TestHandwrittenDocsUntouched:
    """Test that reference generation doesn't modify handwritten documentation."""

    @pytest.fixture(autouse=True)
    def setup(self, run_generator_once):
        """Ensure generator has run before tests."""
        pass

    @pytest.mark.parametrize(
        "doc_path",
        [
            "docs/00_PROJECT_VISION.md",
            "docs/01_ENGINEERING_GUIDELINES.md",
            "docs/02_ARCHITECTURE_GUIDELINES.md",
            "docs/README.md",
            "docs/INDEX.md",
        ],
    )
    def test_handwritten_doc_unchanged(self, project_root, doc_path):
        """Handwritten documentation should remain unchanged after generation."""
        file_path = project_root / doc_path
        if not file_path.exists():
            pytest.skip(f"{doc_path} does not exist")

        # Store the modification time before generation
        mtime_before = file_path.stat().st_mtime

        # Run generator
        engine = ReferenceGeneratorEngine(project_root=project_root)
        engine.run()

        # Check modification time after generation
        mtime_after = file_path.stat().st_mtime

        assert mtime_before == mtime_after, f"{doc_path} was modified by generator"


# ==============================================================================
# Discoverer Unit Tests
# ==============================================================================


class TestServiceReferenceDiscoverer:
    """Test the enhanced service discoverer."""

    def test_discovers_services(self, project_root):
        """Discoverer should find services."""
        from aios.docgen.refgen_discoverers import ServiceReferenceDiscoverer

        discoverer = ServiceReferenceDiscoverer(
            services_root=project_root / "core" / "src" / "aios" / "services",
            src_root=project_root / "core" / "src",
        )
        services = discoverer.discover()

        assert len(services) > 0

    def test_all_services_have_name(self, project_root):
        """All discovered services should have a name."""
        from aios.docgen.refgen_discoverers import ServiceReferenceDiscoverer

        discoverer = ServiceReferenceDiscoverer(
            services_root=project_root / "core" / "src" / "aios" / "services",
            src_root=project_root / "core" / "src",
        )
        services = discoverer.discover()

        assert all(s.name for s in services)

    def test_all_services_have_module(self, project_root):
        """All discovered services should have a module path."""
        from aios.docgen.refgen_discoverers import ServiceReferenceDiscoverer

        discoverer = ServiceReferenceDiscoverer(
            services_root=project_root / "core" / "src" / "aios" / "services",
            src_root=project_root / "core" / "src",
        )
        services = discoverer.discover()

        assert all(s.module for s in services)

    def test_services_have_methods(self, project_root):
        """Services should have method signatures extracted."""
        from aios.docgen.refgen_discoverers import ServiceReferenceDiscoverer

        discoverer = ServiceReferenceDiscoverer(
            services_root=project_root / "core" / "src" / "aios" / "services",
            src_root=project_root / "core" / "src",
        )
        services = discoverer.discover()

        # At least some services should have methods
        services_with_methods = [s for s in services if s.methods]
        assert len(services_with_methods) > 0

    def test_sorted_alphabetically(self, project_root):
        """Services should be sorted alphabetically by name."""
        from aios.docgen.refgen_discoverers import ServiceReferenceDiscoverer

        discoverer = ServiceReferenceDiscoverer(
            services_root=project_root / "core" / "src" / "aios" / "services",
            src_root=project_root / "core" / "src",
        )
        services = discoverer.discover()

        names = [s.name for s in services]
        assert names == sorted(names)

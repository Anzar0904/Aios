"""
test_docgen.py — Regression tests for Sprint 7 Milestone 2: Documentation Generator.

Tests verify:
1. All six catalogs are generated
2. Generated files contain expected sections
3. Discovery finds real AIOS components
4. Generation is idempotent (deterministic structure)
5. Handwritten docs are not modified
6. GenerationResult fields are populated correctly
"""

from __future__ import annotations

import os
import re
import time
from pathlib import Path
from unittest.mock import patch

import pytest

# Path helpers — all tests use the real source tree
# test file: core/tests/test_docgen.py  → parent=core/tests → parent=core → parent=repo_root
_REPO_ROOT = Path(__file__).parent.parent.parent  # /path/to/aios
_CORE_SRC = _REPO_ROOT / "core" / "src"
_AIOS_SRC = _CORE_SRC / "aios"



# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def generated_dir(tmp_path_factory):
    """
    Run the generator once against the real source tree but write output
    to a temp directory so handwritten docs are untouched.
    """
    from aios.docgen.engine import DocGeneratorEngine

    tmp = tmp_path_factory.mktemp("generated_docs")

    engine = DocGeneratorEngine(project_root=_REPO_ROOT)
    # Override output dir
    engine._output_dir = tmp  # type: ignore[attr-defined]

    result = engine.run()
    return tmp, result


@pytest.fixture(scope="module")
def generation_result(generated_dir):
    _, result = generated_dir
    return result


@pytest.fixture(scope="module")
def output_dir(generated_dir):
    d, _ = generated_dir
    return d


# ---------------------------------------------------------------------------
# 1. Generation succeeds without errors
# ---------------------------------------------------------------------------


class TestGenerationStatus:
    def test_generation_succeeds(self, generation_result):
        """Generator must complete with SUCCESS status."""
        from aios.docgen.models import GenerationStatus
        assert generation_result.status == GenerationStatus.SUCCESS

    def test_no_errors(self, generation_result):
        """No hard errors should be raised during generation."""
        assert generation_result.errors == [], f"Errors: {generation_result.errors}"

    def test_eight_files_produced(self, generation_result):
        """Exactly 8 files must be produced (7 catalogs + README index)."""
        assert generation_result.total_files == 8

    def test_elapsed_is_positive(self, generation_result):
        """Elapsed time must be measured and positive."""
        assert generation_result.elapsed_seconds > 0


# ---------------------------------------------------------------------------
# 2. All six catalogs and the dependency graph are generated
# ---------------------------------------------------------------------------


class TestGeneratedFilesExist:
    _EXPECTED_FILES = [
        "services.md",
        "repositories.md",
        "skills.md",
        "providers.md",
        "runtime.md",
        "db_models.md",
        "dependency_graph.md",
        "README.md",
    ]

    @pytest.mark.parametrize("fname", _EXPECTED_FILES)
    def test_file_exists(self, output_dir, fname):
        assert (output_dir / fname).is_file(), f"{fname} not generated"

    @pytest.mark.parametrize("fname", _EXPECTED_FILES)
    def test_file_not_empty(self, output_dir, fname):
        size = (output_dir / fname).stat().st_size
        assert size > 100, f"{fname} is suspiciously small ({size} bytes)"


# ---------------------------------------------------------------------------
# 3. Service Catalog — content verification
# ---------------------------------------------------------------------------


class TestServiceCatalog:
    @pytest.fixture(scope="class")
    def content(self, output_dir):
        return (output_dir / "services.md").read_text(encoding="utf-8")

    def test_header_present(self, content):
        assert "# Service Catalog" in content

    def test_generated_banner(self, content):
        assert "AUTO-GENERATED" in content

    def test_contains_known_service(self, content):
        assert "MemoryService" in content

    def test_contains_event_bus(self, content):
        assert "EventBusService" in content

    def test_contains_session_service(self, content):
        assert "SessionService" in content

    def test_services_count_positive(self, generation_result):
        assert generation_result.services_count > 0

    def test_services_count_reasonable(self, generation_result):
        # We know there are at least 20 services in the codebase
        assert generation_result.services_count >= 20

    def test_summary_statistics_section(self, content):
        assert "## Summary Statistics" in content

    def test_has_module_column(self, content):
        assert "**Module**" in content


# ---------------------------------------------------------------------------
# 4. Repository Catalog — content verification
# ---------------------------------------------------------------------------


class TestRepositoryCatalog:
    @pytest.fixture(scope="class")
    def content(self, output_dir):
        return (output_dir / "repositories.md").read_text(encoding="utf-8")

    def test_header_present(self, content):
        assert "# Repository Catalog" in content

    def test_contains_workspace_repo(self, content):
        assert "WorkspaceRepository" in content

    def test_contains_project_repo(self, content):
        assert "ProjectRepository" in content

    def test_repositories_count_positive(self, generation_result):
        assert generation_result.repositories_count > 0

    def test_repositories_count_reasonable(self, generation_result):
        assert generation_result.repositories_count >= 10

    def test_entity_column_present(self, content):
        assert "**Entity**" in content


# ---------------------------------------------------------------------------
# 5. Skill Catalog — content verification
# ---------------------------------------------------------------------------


class TestSkillCatalog:
    @pytest.fixture(scope="class")
    def content(self, output_dir):
        return (output_dir / "skills.md").read_text(encoding="utf-8")

    def test_header_present(self, content):
        assert "# Skill Catalog" in content

    def test_contains_research_skill(self, content):
        assert "Research" in content

    def test_skills_count_equals_toml_count(self, generation_result):
        toml_count = len(list((_REPO_ROOT / "skills").rglob("skill.toml")))
        assert generation_result.skills_count == toml_count

    def test_skill_matrix_present(self, content):
        assert "## Skill Matrix" in content

    def test_version_column_present(self, content):
        assert "Version" in content

    def test_category_column_present(self, content):
        assert "Category" in content


# ---------------------------------------------------------------------------
# 6. Provider Catalog — content verification
# ---------------------------------------------------------------------------


class TestProviderCatalog:
    @pytest.fixture(scope="class")
    def content(self, output_dir):
        return (output_dir / "providers.md").read_text(encoding="utf-8")

    def test_header_present(self, content):
        assert "# Provider Catalog" in content

    def test_contains_claude_provider(self, content):
        assert "claude" in content.lower()

    def test_contains_gemini_provider(self, content):
        assert "gemini" in content.lower()

    def test_providers_count_positive(self, generation_result):
        assert generation_result.providers_count > 0

    def test_cost_comparison_section(self, content):
        assert "## Cost Comparison" in content

    def test_capability_matrix_section(self, content):
        assert "## Capability Matrix" in content

    def test_context_window_present(self, content):
        assert "Context Window" in content


# ---------------------------------------------------------------------------
# 7. Runtime Component Catalog — content verification
# ---------------------------------------------------------------------------


class TestRuntimeCatalog:
    @pytest.fixture(scope="class")
    def content(self, output_dir):
        return (output_dir / "runtime.md").read_text(encoding="utf-8")

    def test_header_present(self, content):
        assert "# Runtime Component Catalog" in content

    def test_runtime_count_positive(self, generation_result):
        assert generation_result.runtime_count > 0

    def test_runtime_count_reasonable(self, generation_result):
        # We know there are many impl classes
        assert generation_result.runtime_count >= 5

    def test_summary_statistics_section(self, content):
        assert "## Summary Statistics" in content


# ---------------------------------------------------------------------------
# 8. Dependency Graph — content verification
# ---------------------------------------------------------------------------


class TestDependencyGraph:
    @pytest.fixture(scope="class")
    def content(self, output_dir):
        return (output_dir / "dependency_graph.md").read_text(encoding="utf-8")

    def test_header_present(self, content):
        assert "# Dependency Graph" in content

    def test_mermaid_block_present(self, content):
        assert "```mermaid" in content

    def test_di_table_present(self, content):
        assert "## DI Bindings Table" in content

    def test_di_bindings_count_positive(self, generation_result):
        assert generation_result.di_bindings_count > 0

    def test_di_bindings_count_reasonable(self, generation_result):
        # We know there are many DI registrations in bootstrap.py
        assert generation_result.di_bindings_count >= 10

    def test_graph_lr_directive(self, content):
        assert "graph LR" in content


# ---------------------------------------------------------------------------
# 9. DB Model Catalog — content verification
# ---------------------------------------------------------------------------


class TestDbModelCatalog:
    @pytest.fixture(scope="class")
    def content(self, output_dir):
        return (output_dir / "db_models.md").read_text(encoding="utf-8")

    def test_header_present(self, content):
        assert "# Database Model Catalog" in content

    def test_enumerations_section(self, content):
        assert "## Enumerations" in content

    def test_dataclasses_section(self, content):
        assert "## Dataclasses" in content

    def test_db_models_count_positive(self, generation_result):
        assert generation_result.db_models_count > 0

    def test_db_models_count_reasonable(self, generation_result):
        assert generation_result.db_models_count >= 10


# ---------------------------------------------------------------------------
# 10. Idempotency
# ---------------------------------------------------------------------------


class TestIdempotency:
    def test_same_discovery_counts_on_rerun(self, tmp_path):
        """Two consecutive runs on the same source must yield identical counts."""
        from aios.docgen.engine import DocGeneratorEngine

        def run():
            engine = DocGeneratorEngine(project_root=_REPO_ROOT)
            engine._output_dir = tmp_path  # type: ignore[attr-defined]
            return engine.run()

        r1 = run()
        r2 = run()

        assert r1.services_count == r2.services_count
        assert r1.repositories_count == r2.repositories_count
        assert r1.skills_count == r2.skills_count
        assert r1.providers_count == r2.providers_count
        assert r1.runtime_count == r2.runtime_count
        assert r1.db_models_count == r2.db_models_count
        assert r1.di_bindings_count == r2.di_bindings_count

    def test_same_file_count_on_rerun(self, tmp_path):
        """Two consecutive runs must produce exactly the same number of files."""
        from aios.docgen.engine import DocGeneratorEngine

        def run():
            engine = DocGeneratorEngine(project_root=_REPO_ROOT)
            engine._output_dir = tmp_path  # type: ignore[attr-defined]
            return engine.run()

        r1 = run()
        r2 = run()

        assert r1.total_files == r2.total_files

    def test_same_file_sizes_on_rerun(self, tmp_path):
        """
        Content sizes must match between runs (timestamps differ but sections are equal).
        We compare content stripped of lines containing the timestamp.
        """
        from aios.docgen.engine import DocGeneratorEngine

        def run():
            engine = DocGeneratorEngine(project_root=_REPO_ROOT)
            engine._output_dir = tmp_path  # type: ignore[attr-defined]
            engine.run()
            # Read all generated files except README (contains timestamp count)
            return {
                f.name: _strip_timestamps(f.read_text())
                for f in tmp_path.glob("*.md")
                if f.name != "README.md"
            }

        files1 = run()
        files2 = run()

        assert set(files1.keys()) == set(files2.keys())
        for fname in files1:
            assert files1[fname] == files2[fname], (
                f"{fname} content differs between runs"
            )


def _strip_timestamps(content: str) -> str:
    """Remove lines containing ISO 8601 timestamps for idempotency comparison."""
    return "\n".join(
        line for line in content.splitlines()
        if not re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", line)
    )


# ---------------------------------------------------------------------------
# 11. Handwritten docs are not modified
# ---------------------------------------------------------------------------


class TestHandwrittenDocsUntouched:
    _HANDWRITTEN = [
        "docs/00_PROJECT_VISION.md",
        "docs/01_ENGINEERING_GUIDELINES.md",
        "docs/02_ARCHITECTURE_GUIDELINES.md",
        "docs/README.md",
        "docs/INDEX.md",
    ]

    @pytest.mark.parametrize("rel_path", _HANDWRITTEN)
    def test_handwritten_doc_unchanged(self, rel_path):
        """Generator must never write to handwritten documentation files."""
        full_path = _REPO_ROOT / rel_path
        if not full_path.exists():
            pytest.skip(f"{rel_path} does not exist in this checkout")

        mtime_before = full_path.stat().st_mtime

        from aios.docgen.engine import DocGeneratorEngine

        # Run generator to a temp dir to avoid touching real output
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            engine = DocGeneratorEngine(project_root=_REPO_ROOT)
            engine._output_dir = Path(tmp)  # type: ignore[attr-defined]
            engine.run()

        mtime_after = full_path.stat().st_mtime
        assert mtime_before == mtime_after, (
            f"{rel_path} was modified by the generator!"
        )


# ---------------------------------------------------------------------------
# 12. Discoverer unit tests
# ---------------------------------------------------------------------------


class TestServiceDiscoverer:
    def test_discovers_memory_service(self):
        from aios.docgen.discoverers import ServiceDiscoverer
        d = ServiceDiscoverer(_AIOS_SRC / "services", _CORE_SRC)
        services = d.discover()
        names = [s.name for s in services]
        assert "MemoryService" in names

    def test_all_entries_have_name(self):
        from aios.docgen.discoverers import ServiceDiscoverer
        d = ServiceDiscoverer(_AIOS_SRC / "services", _CORE_SRC)
        for svc in d.discover():
            assert svc.name, "Service entry has empty name"

    def test_all_entries_have_module(self):
        from aios.docgen.discoverers import ServiceDiscoverer
        d = ServiceDiscoverer(_AIOS_SRC / "services", _CORE_SRC)
        for svc in d.discover():
            assert svc.module, f"{svc.name} has empty module"

    def test_sorted_alphabetically(self):
        from aios.docgen.discoverers import ServiceDiscoverer
        d = ServiceDiscoverer(_AIOS_SRC / "services", _CORE_SRC)
        names = [s.name for s in d.discover()]
        assert names == sorted(names)


class TestRepositoryDiscoverer:
    def test_discovers_workspace_repository(self):
        from aios.docgen.discoverers import RepositoryDiscoverer
        d = RepositoryDiscoverer(_AIOS_SRC / "services", _CORE_SRC)
        repos = d.discover()
        names = [r.name for r in repos]
        assert "WorkspaceRepository" in names

    def test_all_entries_have_entity(self):
        from aios.docgen.discoverers import RepositoryDiscoverer
        d = RepositoryDiscoverer(_AIOS_SRC / "services", _CORE_SRC)
        for repo in d.discover():
            assert repo.entity is not None, f"{repo.name} has no entity"

    def test_sorted_alphabetically(self):
        from aios.docgen.discoverers import RepositoryDiscoverer
        d = RepositoryDiscoverer(_AIOS_SRC / "services", _CORE_SRC)
        names = [r.name for r in d.discover()]
        assert names == sorted(names)


class TestSkillDiscoverer:
    def test_discovers_research_skill(self):
        from aios.docgen.discoverers import SkillDiscoverer
        d = SkillDiscoverer(_REPO_ROOT / "skills")
        skills = d.discover()
        ids = [s.skill_id for s in skills]
        assert "research" in ids

    def test_all_skills_have_name(self):
        from aios.docgen.discoverers import SkillDiscoverer
        for skill in SkillDiscoverer(_REPO_ROOT / "skills").discover():
            assert skill.name, f"{skill.skill_id} has empty name"

    def test_all_skills_have_description(self):
        from aios.docgen.discoverers import SkillDiscoverer
        for skill in SkillDiscoverer(_REPO_ROOT / "skills").discover():
            assert skill.description, f"{skill.skill_id} has empty description"

    def test_missing_skills_dir_returns_empty(self, tmp_path):
        from aios.docgen.discoverers import SkillDiscoverer
        empty_dir = tmp_path / "no_skills"
        empty_dir.mkdir()
        assert SkillDiscoverer(empty_dir).discover() == []


class TestProviderDiscoverer:
    def test_discovers_providers(self):
        from aios.docgen.discoverers import ProviderDiscoverer
        d = ProviderDiscoverer(_AIOS_SRC / "providers", _CORE_SRC)
        providers = d.discover()
        assert len(providers) > 0

    def test_all_providers_have_name(self):
        from aios.docgen.discoverers import ProviderDiscoverer
        for p in ProviderDiscoverer(_AIOS_SRC / "providers", _CORE_SRC).discover():
            assert p.name, "Provider has empty name"

    def test_context_window_positive(self):
        from aios.docgen.discoverers import ProviderDiscoverer
        for p in ProviderDiscoverer(_AIOS_SRC / "providers", _CORE_SRC).discover():
            assert p.context_window > 0, f"{p.name} has non-positive context window"


class TestDbModelDiscoverer:
    def test_discovers_enums(self):
        from aios.docgen.discoverers import DbModelDiscoverer
        models = DbModelDiscoverer(_AIOS_SRC / "services", _CORE_SRC).discover()
        kinds = {m.kind for m in models}
        assert "enum" in kinds

    def test_discovers_dataclasses(self):
        from aios.docgen.discoverers import DbModelDiscoverer
        models = DbModelDiscoverer(_AIOS_SRC / "services", _CORE_SRC).discover()
        kinds = {m.kind for m in models}
        assert "dataclass" in kinds

    def test_all_models_have_module(self):
        from aios.docgen.discoverers import DbModelDiscoverer
        for m in DbModelDiscoverer(_AIOS_SRC / "services", _CORE_SRC).discover():
            assert m.module, f"{m.name} has empty module"


class TestDIBindingDiscoverer:
    def test_discovers_bindings(self):
        from aios.docgen.discoverers import DIBindingDiscoverer
        bindings = DIBindingDiscoverer(_AIOS_SRC / "bootstrap_modules" / "infrastructure.py").discover()
        assert len(bindings) > 0

    def test_all_bindings_have_interface(self):
        from aios.docgen.discoverers import DIBindingDiscoverer
        for b in DIBindingDiscoverer(_AIOS_SRC / "bootstrap.py").discover():
            assert b.interface, "DI binding has empty interface"

    def test_all_bindings_have_concrete(self):
        from aios.docgen.discoverers import DIBindingDiscoverer
        for b in DIBindingDiscoverer(_AIOS_SRC / "bootstrap.py").discover():
            assert b.concrete, "DI binding has empty concrete"


# ---------------------------------------------------------------------------
# 13. Renderer unit tests
# ---------------------------------------------------------------------------


class TestRenderers:
    def test_service_catalog_renderer_produces_markdown(self):
        from aios.docgen.models import ServiceEntry
        from aios.docgen.renderers import render_service_catalog
        entries = [
            ServiceEntry(
                name="FooService",
                module="aios.services.foo",
                file_path="/fake/foo.py",
                docstring="A test service.",
                implementation="LocalFooService",
            )
        ]
        output = render_service_catalog(entries)
        assert "# Service Catalog" in output
        assert "FooService" in output
        assert "A test service." in output

    def test_skill_catalog_renderer_produces_markdown(self):
        from aios.docgen.models import SkillEntry
        from aios.docgen.renderers import render_skill_catalog
        entries = [
            SkillEntry(
                skill_id="test",
                name="Test Skill",
                version="1.0.0",
                author="test",
                description="A test skill.",
                category="Testing",
                commands=["run test"],
            )
        ]
        output = render_skill_catalog(entries)
        assert "# Skill Catalog" in output
        assert "Test Skill" in output
        assert "run test" in output

    def test_dependency_graph_renderer_has_mermaid(self):
        from aios.docgen.models import DIBinding
        from aios.docgen.renderers import render_dependency_graph
        bindings = [
            DIBinding(interface="IFooService", concrete="LocalFooService", module="bootstrap")
        ]
        output = render_dependency_graph(bindings)
        assert "```mermaid" in output
        assert "IFooService" in output

    def test_provider_catalog_renderer_has_cost_table(self):
        from aios.docgen.models import ProviderEntry
        from aios.docgen.renderers import render_provider_catalog
        providers = [
            ProviderEntry(
                name="test_provider",
                version="1.0",
                status="online",
                context_window=100000,
                cost_per_million_input=1.0,
                cost_per_million_output=3.0,
                auth_type="api_key",
                is_local=False,
            )
        ]
        output = render_provider_catalog(providers)
        assert "# Provider Catalog" in output
        assert "Cost Comparison" in output
        assert "test_provider" in output

    def test_repository_catalog_renderer(self):
        from aios.docgen.models import RepositoryEntry
        from aios.docgen.renderers import render_repository_catalog
        repos = [
            RepositoryEntry(
                name="FooRepository",
                module="aios.services.persistence",
                file_path="/fake/persistence.py",
                docstring="Stores Foo records.",
                entity="Foo",
            )
        ]
        output = render_repository_catalog(repos)
        assert "# Repository Catalog" in output
        assert "FooRepository" in output
        assert "Foo" in output

    def test_index_renderer(self):
        from aios.docgen.renderers import render_index
        output = render_index(
            services_count=10,
            repositories_count=20,
            skills_count=5,
            providers_count=3,
            runtime_count=50,
            db_models_count=100,
            di_bindings_count=80,
            generated_files=["/docs/generated/services.md"],
        )
        assert "AIOS Generated Documentation" in output
        assert "services.md" in output


# ---------------------------------------------------------------------------
# 14. GenerationResult model
# ---------------------------------------------------------------------------


class TestGenerationResultModel:
    def test_default_status_no_errors(self):
        from aios.docgen.models import GenerationResult, GenerationStatus
        r = GenerationResult(status=GenerationStatus.SUCCESS)
        assert r.success is True
        assert r.total_files == 0
        assert r.errors == []

    def test_failed_status(self):
        from aios.docgen.models import GenerationResult, GenerationStatus
        r = GenerationResult(status=GenerationStatus.FAILED)
        assert r.success is False

    def test_partial_status(self):
        from aios.docgen.models import GenerationResult, GenerationStatus
        r = GenerationResult(status=GenerationStatus.PARTIAL)
        assert r.success is False

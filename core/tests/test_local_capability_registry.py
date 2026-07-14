"""
tests/test_local_capability_registry.py

Tests for Phase 1: LocalCapabilityRegistry — model capability mapping.
"""

from __future__ import annotations

import pytest
from aios.local.capability_registry import (
    LocalCapabilityRegistry,
    ModelCapability,
    ModelRole,
    local_capability_registry,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def registry():
    """Fresh registry for each test."""
    return LocalCapabilityRegistry()


# ---------------------------------------------------------------------------
# Tests: Seed data
# ---------------------------------------------------------------------------


class TestCapabilityRegistrySeed:
    def test_registry_has_seed_roles(self, registry):
        roles = registry.list_all_roles()
        assert len(roles) > 0

    def test_deepseek_coder_has_software_engineering(self, registry):
        caps = registry.get_capabilities_for_model("deepseek-coder-v2:16b")
        assert ModelCapability.SOFTWARE_ENGINEERING in caps

    def test_deepseek_coder_has_debugging(self, registry):
        caps = registry.get_capabilities_for_model("deepseek-coder-v2:16b")
        assert ModelCapability.DEBUGGING in caps

    def test_deepseek_coder_has_refactoring(self, registry):
        caps = registry.get_capabilities_for_model("deepseek-coder-v2:16b")
        assert ModelCapability.REFACTORING in caps

    def test_qwen_coder_has_code_review(self, registry):
        caps = registry.get_capabilities_for_model("qwen2.5-coder:14b")
        assert ModelCapability.CODE_REVIEW in caps

    def test_qwen_coder_has_testing(self, registry):
        caps = registry.get_capabilities_for_model("qwen2.5-coder:14b")
        assert ModelCapability.TESTING in caps

    def test_deepseek_r1_has_deep_reasoning(self, registry):
        caps = registry.get_capabilities_for_model("deepseek-r1:14b")
        assert ModelCapability.DEEP_REASONING in caps

    def test_deepseek_r1_has_architecture(self, registry):
        caps = registry.get_capabilities_for_model("deepseek-r1:14b")
        assert ModelCapability.ARCHITECTURE in caps

    def test_gemma3_4b_has_fast_assistant(self, registry):
        caps = registry.get_capabilities_for_model("gemma3:4b")
        assert ModelCapability.FAST_ASSISTANT in caps

    def test_gemma3_4b_has_routing(self, registry):
        caps = registry.get_capabilities_for_model("gemma3:4b")
        assert ModelCapability.ROUTING in caps

    def test_gemma3_12b_has_documentation(self, registry):
        caps = registry.get_capabilities_for_model("gemma3:12b")
        assert ModelCapability.DOCUMENTATION in caps

    def test_gemma3_12b_has_summarization(self, registry):
        caps = registry.get_capabilities_for_model("gemma3:12b")
        assert ModelCapability.SUMMARIZATION in caps

    def test_mxbai_has_embeddings(self, registry):
        caps = registry.get_capabilities_for_model("mxbai-embed-large:latest")
        assert ModelCapability.EMBEDDINGS in caps

    def test_mxbai_has_memory(self, registry):
        caps = registry.get_capabilities_for_model("mxbai-embed-large:latest")
        assert ModelCapability.MEMORY in caps


# ---------------------------------------------------------------------------
# Tests: Pattern matching
# ---------------------------------------------------------------------------


class TestPatternMatching:
    def test_pattern_matches_versioned_name(self, registry):
        """'deepseek-coder-v2' pattern should match 'deepseek-coder-v2:16b'."""
        role = registry.get_role("deepseek-coder-v2:16b")
        assert role is not None

    def test_pattern_matches_tag_variant(self, registry):
        """'gemma3' pattern should match 'gemma3:12b'."""
        role = registry.get_role("gemma3:12b")
        assert role is not None

    def test_returns_none_for_unknown_model(self, registry):
        role = registry.get_role("totally-unknown-model:1b")
        assert role is None

    def test_capabilities_empty_for_unknown_model(self, registry):
        caps = registry.get_capabilities_for_model("totally-unknown-model:1b")
        assert caps == []

    def test_more_specific_pattern_wins(self, registry):
        """'gemma3:4b' should match the 'gemma3:4b' role (priority=5) not generic 'gemma3' (30)."""
        role = registry.get_role("gemma3:4b")
        assert role is not None
        # The specific gemma3:4b role has FAST_ASSISTANT and ROUTING
        assert ModelCapability.FAST_ASSISTANT in role.capabilities


# ---------------------------------------------------------------------------
# Tests: get_models_for_capability
# ---------------------------------------------------------------------------


class TestGetModelsForCapability:
    def test_returns_models_for_code_generation(self, registry):
        available = ["deepseek-coder-v2:16b", "qwen2.5-coder:14b", "gemma3:4b"]
        models = registry.get_models_for_capability(ModelCapability.CODE_GENERATION, available)
        # Should return coding models
        assert len(models) > 0

    def test_returns_mxbai_for_embeddings(self, registry):
        available = ["mxbai-embed-large:latest", "gemma3:4b"]
        models = registry.get_models_for_capability(ModelCapability.EMBEDDINGS, available)
        assert any("mxbai" in m for m in models)

    def test_returns_in_priority_order(self, registry):
        available = ["deepseek-coder-v2:16b", "qwen2.5-coder:14b"]
        models = registry.get_models_for_capability(ModelCapability.SOFTWARE_ENGINEERING, available)
        # deepseek-coder-v2 has priority=10, qwen2.5-coder has priority=15
        assert models.index(next(m for m in models if "deepseek" in m)) < models.index(
            next(m for m in models if "qwen2.5" in m)
        )

    def test_returns_empty_when_no_models_available(self, registry):
        models = registry.get_models_for_capability(
            ModelCapability.EMBEDDINGS,
            available_models=["gemma3:4b"],  # No embedding model available
        )
        assert models == []

    def test_no_duplicates_in_results(self, registry):
        available = ["deepseek-coder-v2:16b", "deepseek-coder-v2:16b"]  # Duplicate
        models = registry.get_models_for_capability(ModelCapability.CODE_GENERATION, available)
        assert len(models) == len(set(models))


# ---------------------------------------------------------------------------
# Tests: register_role
# ---------------------------------------------------------------------------


class TestRegisterRole:
    def test_register_custom_role(self, registry):
        custom_role = ModelRole(
            model_pattern="custom-model",
            capabilities=[ModelCapability.WRITING, ModelCapability.SUMMARIZATION],
            description="Custom test model",
            priority=50,
        )
        registry.register_role("custom-model", custom_role)
        caps = registry.get_capabilities_for_model("custom-model")
        assert ModelCapability.WRITING in caps
        assert ModelCapability.SUMMARIZATION in caps

    def test_registered_model_appears_in_capability_query(self, registry):
        custom_role = ModelRole(
            model_pattern="new-model:7b",
            capabilities=[ModelCapability.ANALYSIS],
            priority=99,
        )
        registry.register_role("new-model:7b", custom_role)
        models = registry.get_models_for_capability(
            ModelCapability.ANALYSIS,
            available_models=["new-model:7b"],
        )
        assert "new-model:7b" in models


# ---------------------------------------------------------------------------
# Tests: benchmark score integration
# ---------------------------------------------------------------------------


class TestBenchmarkScoreIntegration:
    def test_update_benchmark_score(self, registry):
        registry.update_benchmark_score("deepseek-coder-v2", 85.5)
        role = registry.get_role("deepseek-coder-v2:16b")
        assert role is not None
        assert role.benchmark_score == 85.5

    def test_update_score_for_unknown_pattern_is_noop(self, registry):
        # Should not raise
        registry.update_benchmark_score("nonexistent-model", 50.0)


# ---------------------------------------------------------------------------
# Tests: Global singleton
# ---------------------------------------------------------------------------


class TestGlobalSingleton:
    def test_singleton_is_instance_of_registry(self):
        assert isinstance(local_capability_registry, LocalCapabilityRegistry)

    def test_singleton_has_seed_data(self):
        roles = local_capability_registry.list_all_roles()
        assert len(roles) > 0

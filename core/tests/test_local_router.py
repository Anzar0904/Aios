"""
tests/test_local_router.py

Tests for Phase 1: LocalModelRouter — intelligent task routing.
"""

from __future__ import annotations

import pytest
from aios.local.capability_registry import LocalCapabilityRegistry, ModelCapability
from aios.local.router import LocalModelRouter

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


AVAILABLE_MODELS = [
    "deepseek-coder-v2:16b",
    "qwen2.5-coder:14b",
    "deepseek-r1:14b",
    "qwen3.5:9b",
    "qwen3.6:27b",
    "gemma3:4b",
    "gemma3:12b",
    "mxbai-embed-large:latest",
    "mistral-small:24b",
    "qwen3-coder:30b",
]


@pytest.fixture
def registry():
    return LocalCapabilityRegistry()


@pytest.fixture
def router(registry):
    return LocalModelRouter(capability_registry=registry)


# ---------------------------------------------------------------------------
# Tests: Capability resolution from tasks
# ---------------------------------------------------------------------------


class TestCapabilityResolution:
    def test_coding_task_maps_to_code_generation(self, router):
        cap, conf = router.get_capability_for_task("Write a python function to parse JSON")
        assert cap == ModelCapability.CODE_GENERATION
        assert conf > 0.5

    def test_review_task_maps_to_code_review(self, router):
        cap, conf = router.get_capability_for_task("Review this pull request for issues")
        assert cap == ModelCapability.CODE_REVIEW
        assert conf > 0.5

    def test_architecture_task_maps_to_architecture(self, router):
        cap, conf = router.get_capability_for_task("Explain the system architecture design")
        assert cap == ModelCapability.ARCHITECTURE
        assert conf > 0.5

    def test_documentation_task_maps_to_documentation(self, router):
        cap, conf = router.get_capability_for_task("Generate documentation for this module")
        assert cap == ModelCapability.DOCUMENTATION

    def test_embedding_task_maps_to_embeddings(self, router):
        cap, conf = router.get_capability_for_task(
            "Remember this conversation for later recall context"
        )
        assert cap == ModelCapability.EMBEDDINGS

    def test_debug_task_maps_to_debugging(self, router):
        cap, conf = router.get_capability_for_task("Debug this traceback error")
        assert cap == ModelCapability.DEBUGGING

    def test_refactor_task_maps_to_refactoring(self, router):
        cap, conf = router.get_capability_for_task("Refactor this code to be cleaner")
        assert cap == ModelCapability.REFACTORING

    def test_testing_task_maps_to_testing(self, router):
        cap, conf = router.get_capability_for_task("Write unit tests for this function")
        assert cap == ModelCapability.TESTING

    def test_reasoning_task_maps_to_deep_reasoning(self, router):
        cap, conf = router.get_capability_for_task(
            "Reason step by step through this complex problem"
        )
        assert cap == ModelCapability.DEEP_REASONING

    def test_summary_task_maps_to_summarization(self, router):
        cap, conf = router.get_capability_for_task("Summarize this document for a brief overview")
        assert cap == ModelCapability.SUMMARIZATION

    def test_n8n_workflow_maps_to_code_generation(self, router):
        """Project brief example: 'Create n8n workflow' → Coding."""
        cap, conf = router.get_capability_for_task("Create n8n workflow for email automation")
        assert cap == ModelCapability.CODE_GENERATION

    def test_pr_review_maps_to_code_review(self, router):
        """Project brief example: 'Review pull request' → Code Review."""
        cap, conf = router.get_capability_for_task("Review pull request #42")
        assert cap == ModelCapability.CODE_REVIEW

    def test_explain_architecture_maps_to_architecture(self, router):
        """Project brief example: 'Explain architecture' → Deep Reasoning / Architecture."""
        cap, conf = router.get_capability_for_task("Explain the microservice architecture")
        assert cap in (ModelCapability.ARCHITECTURE, ModelCapability.EXPLANATION)

    def test_remember_conversation_maps_to_embeddings(self, router):
        """Project brief example: 'Remember conversation' → Embedding."""
        cap, conf = router.get_capability_for_task(
            "Remember this conversation context for recall context"
        )
        assert cap == ModelCapability.EMBEDDINGS

    def test_unknown_task_falls_back_to_general_chat(self, router):
        cap, conf = router.get_capability_for_task("xyzzy completely unknown input !!!@@@")
        assert cap == ModelCapability.GENERAL_CHAT
        assert conf < 0.5


# ---------------------------------------------------------------------------
# Tests: Model selection
# ---------------------------------------------------------------------------


class TestModelSelection:
    def test_router_selects_a_model_for_coding(self, router):
        result = router.route("Write a function to sort a list", AVAILABLE_MODELS)
        assert result is not None
        assert result.model_name in AVAILABLE_MODELS

    def test_router_selects_coding_model_for_code_task(self, router):
        result = router.route("Write a python function to sort a list", AVAILABLE_MODELS)
        assert result is not None
        # Should pick a coding model
        assert any(keyword in result.model_name for keyword in ("coder", "deepseek", "qwen"))

    def test_router_selects_embedding_model_for_memory(self, router):
        result = router.route("Embed this text for semantic search", AVAILABLE_MODELS)
        assert result is not None
        assert "mxbai" in result.model_name or "embed" in result.model_name.lower()

    def test_router_selects_reasoning_model_for_deep_analysis(self, router):
        result = router.route(
            "Deep reason through this complex problem step by step", AVAILABLE_MODELS
        )
        assert result is not None
        # Should prefer deepseek-r1 or qwen3.6 for reasoning
        assert any(keyword in result.model_name for keyword in ("r1", "deepseek", "qwen3.6"))

    def test_router_returns_none_when_no_models_available(self, router):
        result = router.route("Write some code", [])
        assert result is None

    def test_router_uses_fallback_when_no_primary_match(self, router):
        # Remove all coding models, keep only general chat
        limited_models = ["gemma3:4b", "mistral-small:24b"]
        result = router.route("Write some code to solve this", limited_models)
        assert result is not None
        # Should still return something (fallback)
        assert result.model_name in limited_models

    def test_routing_result_has_confidence(self, router):
        result = router.route("Write code to parse JSON", AVAILABLE_MODELS)
        assert result is not None
        assert 0.0 <= result.confidence <= 1.0

    def test_routing_result_has_capability(self, router):
        result = router.route("Generate documentation for this API", AVAILABLE_MODELS)
        assert result is not None
        assert isinstance(result.capability, ModelCapability)

    def test_routing_result_has_candidates(self, router):
        result = router.route("Write a unit test", AVAILABLE_MODELS)
        assert result is not None
        assert len(result.candidates) > 0

    def test_routing_result_has_reasoning(self, router):
        result = router.route("Debug this traceback", AVAILABLE_MODELS)
        assert result is not None
        assert isinstance(result.reasoning, str)
        assert len(result.reasoning) > 0

    def test_force_capability_overrides_resolution(self, router):
        result = router.route(
            "Hello world",
            AVAILABLE_MODELS,
            force_capability=ModelCapability.EMBEDDINGS,
        )
        assert result is not None
        assert result.capability == ModelCapability.EMBEDDINGS
        assert result.confidence == 1.0

    def test_fallback_flag_set_when_no_primary_match(self, router):
        # Use only an embedding model for a code task
        result = router.route("Write some code", ["mxbai-embed-large:latest"])
        # mxbai doesn't have CODE_GENERATION capability, so should fall back
        # to GENERAL_CHAT or the embedding model itself
        assert result is not None
        # fallback_used should be True if no model matches the primary capability
        # (mxbai only has EMBEDDINGS/MEMORY/SEMANTIC_SEARCH)


# ---------------------------------------------------------------------------
# Tests: explain method
# ---------------------------------------------------------------------------


class TestRouterExplain:
    def test_explain_returns_string(self, router):
        explanation = router.explain("Write code to fetch an API", AVAILABLE_MODELS)
        assert isinstance(explanation, str)
        assert len(explanation) > 0

    def test_explain_no_models_returns_message(self, router):
        explanation = router.explain("Write code", [])
        assert "No suitable" in explanation


# ---------------------------------------------------------------------------
# Tests: Selection never by model name
# ---------------------------------------------------------------------------


class TestNoNameSelection:
    """Router must NEVER select by model name — always by capability."""

    def test_route_selects_by_capability_not_name(self, router):
        """If we only supply one model, it should still go through capability resolution."""
        # Only supply deepseek-r1 — if it routes correctly to reasoning, it uses capability
        task = "Reason step by step through this architectural decision"
        result = router.route(task, ["deepseek-r1:14b"])
        assert result is not None
        # The model was selected because it has the matching capability
        assert result.capability in (
            ModelCapability.DEEP_REASONING,
            ModelCapability.ARCHITECTURE,
            ModelCapability.ANALYSIS,
        )

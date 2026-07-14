"""
aios/local/router.py

Intelligent Local Model Router.

Selects models by capability — NEVER by name.
Uses task keyword analysis → capability resolution → capability registry → model selection.
Benchmark scores inform tie-breaking between equivalent candidates.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from aios.local.capability_registry import LocalCapabilityRegistry, ModelCapability

logger = logging.getLogger(__name__)


@dataclass
class RoutingResult:
    """
    The outcome of a routing decision.

    Attributes:
        model_name: The fully-qualified Ollama model name selected.
        capability: The resolved capability that drove the selection.
        confidence: 0.0–1.0 confidence in the routing decision.
        candidates: All models considered, in priority order.
        reasoning: Human-readable explanation of the routing decision.
        fallback_used: True if no primary match was found and a fallback was applied.
    """

    model_name: str
    capability: ModelCapability
    confidence: float
    candidates: List[str] = field(default_factory=list)
    reasoning: str = ""
    fallback_used: bool = False


# Task keyword → capability mapping.
# IMPORTANT: Order matters — more specific patterns must appear BEFORE broader ones
# to avoid shadowing. The scoring uses keyword-count, so specifics win on ties.
_TASK_CAPABILITY_MAP: List[Tuple[List[str], ModelCapability]] = [
    # Embeddings & Memory (very specific vocabulary)
    (
        [
            "embed",
            "embedding",
            "semantic search",
            "vector store",
            "remember this",
            "memory store",
            "recall context",
        ],
        ModelCapability.EMBEDDINGS,
    ),
    # Software Engineering — fine-grained, ordered by specificity
    (["refactor", "clean up code", "restructure", "reorganize code"], ModelCapability.REFACTORING),
    (
        ["debug", "fix bug", "traceback", "exception", "error in code", "stack trace"],
        ModelCapability.DEBUGGING,
    ),
    (
        ["write test", "unit test", "pytest", "test coverage", "mock", "tdd", "bdd"],
        ModelCapability.TESTING,
    ),
    (["optimize", "performance", "speed up", "profil"], ModelCapability.OPTIMIZATION),
    (["patch", "apply patch", "code change"], ModelCapability.PATCH_GENERATION),
    (["review", "pull request", "pr review", "code review", "lgtm"], ModelCapability.CODE_REVIEW),
    (["api design", "rest api", "graphql", "openapi", "swagger"], ModelCapability.API_DESIGN),
    # CODE_GENERATION: broad coding vocabulary — 'write' here is paired with 'function'/'code'
    (
        [
            "write a function",
            "write code",
            "create function",
            "implement function",
            "n8n workflow",
            "script",
            "code generation",
            "generate code",
            "write a python",
            "write a script",
            "write a class",
        ],
        ModelCapability.CODE_GENERATION,
    ),
    (
        ["software engineer", "develop", "build feature", "programming"],
        ModelCapability.SOFTWARE_ENGINEERING,
    ),
    # Architecture & Deep Reasoning
    (
        ["architect", "system design", "design pattern", "microservice", "monolith", "scalab"],
        ModelCapability.ARCHITECTURE,
    ),
    (
        [
            "reason",
            "chain of thought",
            "step by step",
            "think through",
            "deep analysis",
            "complex problem",
        ],
        ModelCapability.DEEP_REASONING,
    ),
    (["analyze", "analysis", "investigate", "evaluate", "assess"], ModelCapability.ANALYSIS),
    (["plan", "roadmap", "strategy", "timeline", "phases"], ModelCapability.PLANNING),
    (["research", "find information", "look up", "investigate topic"], ModelCapability.RESEARCH),
    # Documentation & Writing — summarize BEFORE document to avoid subdomain shadowing
    (
        ["summarize", "summary", "tldr", "shorten", "condense", "brief"],
        ModelCapability.SUMMARIZATION,
    ),
    (
        [
            "document",
            "readme",
            "docstring",
            "comment code",
            "api docs",
            "write docs",
            "generate documentation",
        ],
        ModelCapability.DOCUMENTATION,
    ),
    (["explain", "what is", "how does", "describe", "clarify"], ModelCapability.EXPLANATION),
    # WRITING: catch-all for prose; 'write' alone (not qualified by function/code/docs) lands here
    (
        ["draft", "compose", "article", "blog post", "email", "essay", "prose"],
        ModelCapability.WRITING,
    ),
    # Fast / General
    (
        ["quick", "fast", "simple question", "hello", "hi ", "help me with"],
        ModelCapability.FAST_ASSISTANT,
    ),
]


class LocalModelRouter:
    """
    Routes tasks to local Ollama models by capability.

    Algorithm:
    1. Normalize and tokenize the task description.
    2. Score each capability by keyword overlap.
    3. Select the highest-scoring capability.
    4. Query LocalCapabilityRegistry for priority-sorted model candidates.
    5. Return the first available model with confidence score.

    Tie-breaking: benchmark_score from the registry is used when
    multiple candidates have equal priority.
    """

    def __init__(
        self,
        capability_registry: LocalCapabilityRegistry,
        default_capability: ModelCapability = ModelCapability.GENERAL_CHAT,
    ) -> None:
        self._registry = capability_registry
        self._default_capability = default_capability

    def route(
        self,
        task: str,
        available_models: List[str],
        force_capability: Optional[ModelCapability] = None,
    ) -> Optional[RoutingResult]:
        """
        Resolves the best local model for the given task description.

        Args:
            task: Natural language description of the task.
            available_models: List of model names currently installed/available.
            force_capability: Override capability resolution (for explicit routing).

        Returns:
            RoutingResult if a suitable model is found, None otherwise.
        """
        if not available_models:
            logger.warning("Router: no available models to route to")
            return None

        if force_capability is not None:
            capability = force_capability
            confidence = 1.0
            keyword_matches: List[str] = []
        else:
            capability, confidence, keyword_matches = self._resolve_capability(task)

        candidates = self._registry.get_models_for_capability(
            capability, available_models=available_models
        )

        fallback_used = False
        if not candidates:
            logger.debug(
                "No models for capability %s — falling back to %s",
                capability.value,
                self._default_capability.value,
            )
            fallback_used = True
            candidates = self._registry.get_models_for_capability(
                self._default_capability, available_models=available_models
            )
            if not candidates:
                # Last resort: return first available model
                candidates = list(available_models)

        if not candidates:
            return None

        selected = candidates[0]
        reasoning = self._build_reasoning(
            task, capability, selected, keyword_matches, fallback_used
        )

        return RoutingResult(
            model_name=selected,
            capability=capability,
            confidence=confidence,
            candidates=candidates,
            reasoning=reasoning,
            fallback_used=fallback_used,
        )

    def explain(self, task: str, available_models: List[str]) -> str:
        """Returns a human-readable routing explanation without executing."""
        result = self.route(task, available_models)
        if result is None:
            return "No suitable model found for this task."
        return result.reasoning

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _resolve_capability(self, task: str) -> Tuple[ModelCapability, float, List[str]]:
        """
        Scores each capability by keyword matching and returns the best one.

        Returns:
            (best_capability, confidence_score, matched_keywords)
        """
        task_normalized = task.lower().strip()
        scores: Dict[ModelCapability, Tuple[int, List[str]]] = {}

        for keywords, capability in _TASK_CAPABILITY_MAP:
            matches = [kw for kw in keywords if kw in task_normalized]
            if matches:
                scores[capability] = (len(matches), matches)

        if not scores:
            logger.debug("No capability matched for task: '%s' — using default", task[:80])
            return self._default_capability, 0.3, []

        # Select capability with most keyword matches
        best_cap = max(scores, key=lambda c: scores[c][0])
        count, matched = scores[best_cap]

        # Confidence: number of keyword matches / max possible matches for this capability
        max_possible = max(len(kws) for kws, _ in _TASK_CAPABILITY_MAP if _ == best_cap)
        confidence = min(1.0, 0.5 + (count / max(max_possible, 1)) * 0.5)

        return best_cap, round(confidence, 2), matched

    def _build_reasoning(
        self,
        task: str,
        capability: ModelCapability,
        selected_model: str,
        matched_keywords: List[str],
        fallback_used: bool,
    ) -> str:
        """Constructs a human-readable routing explanation."""
        parts = [
            f'Task: "{task[:100]}"',
            f"Resolved capability: {capability.value}",
            f"Selected model: {selected_model}",
        ]
        if matched_keywords:
            parts.append(f"Matched keywords: {', '.join(matched_keywords[:5])}")
        if fallback_used:
            parts.append(f"Note: No primary match — fallback to {self._default_capability.value}")
        return " | ".join(parts)

    def get_capability_for_task(self, task: str) -> Tuple[ModelCapability, float]:
        """Public method: returns just the capability and confidence without full routing."""
        cap, conf, _ = self._resolve_capability(task)
        return cap, conf

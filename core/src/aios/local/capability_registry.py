"""
aios/local/capability_registry.py

Capability Registry for local Ollama models.

Defines structured roles and capabilities for each model family/name pattern.
The registry is seeded with known model roles but auto-extends when new models
are discovered through OllamaDiscovery.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class ModelCapability(str, Enum):
    """
    Canonical capability labels used by the router to match tasks to models.

    These are the routing vocabulary — tasks are mapped to capabilities,
    capabilities are mapped to models.
    """

    # Engineering
    SOFTWARE_ENGINEERING = "software_engineering"
    DEBUGGING = "debugging"
    REFACTORING = "refactoring"
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    TESTING = "testing"
    OPTIMIZATION = "optimization"
    PATCH_GENERATION = "patch_generation"
    API_DESIGN = "api_design"
    ARCHITECTURE = "architecture"

    # Reasoning & Analysis
    DEEP_REASONING = "deep_reasoning"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    RESEARCH = "research"

    # Content & Documentation
    DOCUMENTATION = "documentation"
    SUMMARIZATION = "summarization"
    EXPLANATION = "explanation"
    WRITING = "writing"

    # Conversational
    FAST_ASSISTANT = "fast_assistant"
    ROUTING = "routing"
    GENERAL_CHAT = "general_chat"

    # Memory & Embeddings
    EMBEDDINGS = "embeddings"
    SEMANTIC_SEARCH = "semantic_search"
    MEMORY = "memory"


@dataclass
class ModelRole:
    """
    A role definition binding a model to its ordered list of capabilities.

    Priority determines which model is chosen when multiple models share a capability.
    Lower value = higher priority.
    """

    model_pattern: str  # Substring matched against model name (case-insensitive)
    capabilities: List[ModelCapability]
    description: str = ""
    priority: int = 50  # 0-100; lower = selected first
    benchmark_score: float = 0.0  # Populated by BenchmarkEngine


class LocalCapabilityRegistry:
    """
    Registry mapping model names → capabilities and capabilities → candidate models.

    Design decisions:
    - Pattern-based matching allows version-agnostic lookups
      (e.g., 'deepseek-coder-v2' matches 'deepseek-coder-v2:16b')
    - Seeded with known roles for the models specified in the project brief
    - Extensible: call register_role() to add new model roles at runtime
    - Router queries get_models_for_capability() to retrieve a priority-sorted
      list of candidate models for a given capability
    """

    # Seed roles for all models listed in the project brief.
    # Priority: lower = preferred when multiple models match a capability.
    _SEED_ROLES: List[ModelRole] = [
        ModelRole(
            model_pattern="deepseek-coder-v2",
            capabilities=[
                ModelCapability.SOFTWARE_ENGINEERING,
                ModelCapability.CODE_GENERATION,
                ModelCapability.DEBUGGING,
                ModelCapability.REFACTORING,
                ModelCapability.PATCH_GENERATION,
                ModelCapability.API_DESIGN,
            ],
            description="Expert coding model for complex software engineering tasks",
            priority=10,
        ),
        ModelRole(
            model_pattern="qwen2.5-coder",
            capabilities=[
                ModelCapability.CODE_REVIEW,
                ModelCapability.TESTING,
                ModelCapability.OPTIMIZATION,
                ModelCapability.SOFTWARE_ENGINEERING,
                ModelCapability.DEBUGGING,
                ModelCapability.CODE_GENERATION,
            ],
            description="Qwen coding model for code review, testing, and optimization",
            priority=15,
        ),
        ModelRole(
            model_pattern="qwen3-coder",
            capabilities=[
                ModelCapability.CODE_GENERATION,
                ModelCapability.SOFTWARE_ENGINEERING,
                ModelCapability.DEBUGGING,
                ModelCapability.REFACTORING,
                ModelCapability.API_DESIGN,
                ModelCapability.OPTIMIZATION,
            ],
            description="Qwen3 coder — large context coding powerhouse",
            priority=12,
        ),
        ModelRole(
            model_pattern="deepseek-r1",
            capabilities=[
                ModelCapability.DEEP_REASONING,
                ModelCapability.ARCHITECTURE,
                ModelCapability.ANALYSIS,
                ModelCapability.PLANNING,
                ModelCapability.RESEARCH,
                ModelCapability.DEBUGGING,
            ],
            description="Deep reasoning and architectural thinking with chain-of-thought",
            priority=10,
        ),
        ModelRole(
            model_pattern="gemma3:4b",
            capabilities=[
                ModelCapability.FAST_ASSISTANT,
                ModelCapability.ROUTING,
                ModelCapability.GENERAL_CHAT,
                ModelCapability.SUMMARIZATION,
            ],
            description="Fast, lightweight assistant for quick responses and routing",
            priority=5,
        ),
        ModelRole(
            model_pattern="gemma3:12b",
            capabilities=[
                ModelCapability.DOCUMENTATION,
                ModelCapability.SUMMARIZATION,
                ModelCapability.EXPLANATION,
                ModelCapability.WRITING,
                ModelCapability.GENERAL_CHAT,
            ],
            description="Mid-size Gemma for documentation, summaries, and writing",
            priority=20,
        ),
        ModelRole(
            model_pattern="gemma3",
            capabilities=[
                ModelCapability.GENERAL_CHAT,
                ModelCapability.SUMMARIZATION,
                ModelCapability.WRITING,
                ModelCapability.FAST_ASSISTANT,
            ],
            description="Gemma general-purpose assistant",
            priority=30,
        ),
        ModelRole(
            model_pattern="mxbai",
            capabilities=[
                ModelCapability.EMBEDDINGS,
                ModelCapability.SEMANTIC_SEARCH,
                ModelCapability.MEMORY,
            ],
            description="High-quality embedding model for semantic memory and search",
            priority=5,
        ),
        ModelRole(
            model_pattern="mistral-small",
            capabilities=[
                ModelCapability.GENERAL_CHAT,
                ModelCapability.WRITING,
                ModelCapability.EXPLANATION,
                ModelCapability.SUMMARIZATION,
                ModelCapability.ANALYSIS,
                ModelCapability.CODE_REVIEW,
            ],
            description="Mistral balanced model for general tasks and analysis",
            priority=25,
        ),
        ModelRole(
            model_pattern="qwen3.5",
            capabilities=[
                ModelCapability.GENERAL_CHAT,
                ModelCapability.ANALYSIS,
                ModelCapability.PLANNING,
                ModelCapability.WRITING,
                ModelCapability.SUMMARIZATION,
            ],
            description="Qwen3.5 general reasoning and chat model",
            priority=20,
        ),
        ModelRole(
            model_pattern="qwen3.6",
            capabilities=[
                ModelCapability.DEEP_REASONING,
                ModelCapability.ARCHITECTURE,
                ModelCapability.ANALYSIS,
                ModelCapability.PLANNING,
                ModelCapability.SOFTWARE_ENGINEERING,
                ModelCapability.CODE_REVIEW,
            ],
            description="Qwen3.6 large-scale reasoning and engineering tasks",
            priority=15,
        ),
    ]

    def __init__(self) -> None:
        # model_name → ModelRole mapping
        self._roles: Dict[str, ModelRole] = {}
        # capability → list of (priority, model_name) tuples, sorted by priority asc
        self._capability_index: Dict[ModelCapability, List[tuple]] = {}

        # Seed with known roles
        for role in self._SEED_ROLES:
            self._register_role_internal(role.model_pattern, role)

    def register_role(self, model_name: str, role: ModelRole) -> None:
        """
        Registers a model role for the given model name.

        If a role already exists for the model_pattern, it is replaced.
        Re-indexes all capabilities.
        """
        self._register_role_internal(model_name, role)
        logger.debug("Registered capability role for model: %s", model_name)

    def get_role(self, model_name: str) -> Optional[ModelRole]:
        """
        Retrieves the capability role for a model.

        Matches by exact name first, then falls back to pattern substring matching.
        """
        # Exact match
        if model_name in self._roles:
            return self._roles[model_name]

        # Pattern match (case-insensitive substring)
        name_lower = model_name.lower()
        best: Optional[ModelRole] = None
        for pattern, role in self._roles.items():
            if pattern.lower() in name_lower:
                if best is None or role.priority < best.priority:
                    best = role
        return best

    def get_capabilities_for_model(self, model_name: str) -> List[ModelCapability]:
        """Returns the list of capabilities a model supports."""
        role = self.get_role(model_name)
        return role.capabilities if role else []

    def get_models_for_capability(
        self,
        capability: ModelCapability,
        available_models: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Returns model names that support the given capability,
        sorted by priority ascending (lower = preferred).

        If available_models is provided, only returns models present in that list.
        """
        candidates = self._capability_index.get(capability, [])
        result: List[str] = []
        for _, pattern in sorted(candidates):
            if available_models is not None:
                # Find any available model whose name contains this pattern
                matched = [m for m in available_models if pattern.lower() in m.lower()]
                result.extend(matched)
            else:
                result.append(pattern)
        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for m in result:
            if m not in seen:
                seen.add(m)
                deduped.append(m)
        return deduped

    def list_all_capabilities(self) -> List[ModelCapability]:
        """Returns all capability keys present in the registry."""
        return list(self._capability_index.keys())

    def list_all_roles(self) -> List[ModelRole]:
        """Returns all registered model roles."""
        return list(self._roles.values())

    def update_benchmark_score(self, model_pattern: str, score: float) -> None:
        """Updates the benchmark score for a model role. Used by BenchmarkEngine."""
        if model_pattern in self._roles:
            self._roles[model_pattern].benchmark_score = score
            # Re-sort capability index since benchmark may adjust routing
            for cap in self._roles[model_pattern].capabilities:
                self._rebuild_capability_index(cap)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _register_role_internal(self, pattern: str, role: ModelRole) -> None:
        """Internal: stores role and updates capability index."""
        self._roles[pattern] = role
        for cap in role.capabilities:
            if cap not in self._capability_index:
                self._capability_index[cap] = []
            # Remove existing entry for this pattern (if re-registering)
            self._capability_index[cap] = [
                (p, n) for p, n in self._capability_index[cap] if n != pattern
            ]
            self._capability_index[cap].append((role.priority, pattern))
            self._capability_index[cap].sort()

    def _rebuild_capability_index(self, capability: ModelCapability) -> None:
        """Rebuilds the sorted index for a single capability."""
        entries = self._capability_index.get(capability, [])
        rebuilt = []
        for priority, pattern in entries:
            if pattern in self._roles:
                rebuilt.append((self._roles[pattern].priority, pattern))
        self._capability_index[capability] = sorted(rebuilt)


# Module-level singleton
local_capability_registry = LocalCapabilityRegistry()

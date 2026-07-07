"""
bootstrap_modules/providers.py

Registers database, embedding, and source control providers.
"""

from __future__ import annotations

import logging

# Embedding Provider imports
from aios.services.persistence_impl import (
    GeminiProvider,
    MockEmbeddingProvider,
    OllamaProvider,
    OpenAIProvider,
    SentenceTransformerProvider,
)

logger = logging.getLogger(__name__)


def bootstrap_providers(registry, embedding_service) -> dict:  # noqa: ANN001
    """Constructs, initializes, and registers embedding providers into embedding_service."""
    mock_embed_provider = MockEmbeddingProvider()
    mock_embed_provider.initialize()
    embedding_service.register_provider("mock", mock_embed_provider)

    st_provider = SentenceTransformerProvider()
    st_provider.initialize()
    embedding_service.register_provider("sentence_transformer", st_provider)

    openai_provider = OpenAIProvider()
    openai_provider.initialize()
    embedding_service.register_provider("openai", openai_provider)

    gemini_provider = GeminiProvider()
    gemini_provider.initialize()
    embedding_service.register_provider("gemini", gemini_provider)

    ollama_provider = OllamaProvider()
    ollama_provider.initialize()
    embedding_service.register_provider("ollama", ollama_provider)

    return {
        "mock_embed_provider": mock_embed_provider,
        "st_provider": st_provider,
        "openai_provider": openai_provider,
        "gemini_provider": gemini_provider,
        "ollama_provider": ollama_provider,
    }

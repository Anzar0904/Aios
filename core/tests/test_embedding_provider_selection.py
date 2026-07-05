"""
Regression tests for embedding provider selection.

Issue: EmbeddingEngineImpl defaulted to "mock" when EMBEDDING_PROVIDER was
unset, causing production to silently return low-quality hash-based vectors
instead of real semantic embeddings.

Fix: default changed to "sentence_transformer"; initialize() now validates the
configured provider is registered and raises ValueError if not.
"""
import os
import pytest
from typing import Optional

from aios.services.persistence import (
    EmbeddingRequest,
)
from aios.services.persistence_impl import (
    EmbeddingServiceImpl,
    EmbeddingCacheImpl,
    EmbeddingEngineImpl,
    MockEmbeddingProvider,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_service_with_providers(*names: str) -> EmbeddingServiceImpl:
    """Return an EmbeddingServiceImpl pre-loaded with named stub providers."""
    service = EmbeddingServiceImpl()
    for name in names:
        mock = MockEmbeddingProvider()
        mock.initialize()
        service.register_provider(name, mock)
    return service


def make_engine(service: EmbeddingServiceImpl, provider_env: Optional[str] = None) -> EmbeddingEngineImpl:
    """Construct EmbeddingEngineImpl with optional EMBEDDING_PROVIDER override."""
    cache = EmbeddingCacheImpl()
    cache.initialize()
    env_backup = os.environ.pop("EMBEDDING_PROVIDER", None)
    try:
        if provider_env is not None:
            os.environ["EMBEDDING_PROVIDER"] = provider_env
        engine = EmbeddingEngineImpl(service, cache)
    finally:
        if env_backup is not None:
            os.environ["EMBEDDING_PROVIDER"] = env_backup
        elif "EMBEDDING_PROVIDER" in os.environ:
            del os.environ["EMBEDDING_PROVIDER"]
    return engine


# ---------------------------------------------------------------------------
# Regression: default must NOT be "mock"
# ---------------------------------------------------------------------------

def test_default_active_provider_is_not_mock():
    """When EMBEDDING_PROVIDER is unset the default must NOT be 'mock'."""
    env_backup = os.environ.pop("EMBEDDING_PROVIDER", None)
    try:
        cache = EmbeddingCacheImpl()
        service = EmbeddingServiceImpl()
        engine = EmbeddingEngineImpl(service, cache)
        assert engine._active_provider != "mock", (
            "Production default must not be 'mock'. "
            "Set EMBEDDING_PROVIDER=mock explicitly for testing."
        )
    finally:
        if env_backup is not None:
            os.environ["EMBEDDING_PROVIDER"] = env_backup


def test_default_active_provider_is_sentence_transformer():
    """When EMBEDDING_PROVIDER is unset the default must be 'sentence_transformer'."""
    env_backup = os.environ.pop("EMBEDDING_PROVIDER", None)
    try:
        cache = EmbeddingCacheImpl()
        service = EmbeddingServiceImpl()
        engine = EmbeddingEngineImpl(service, cache)
        assert engine._active_provider == "sentence_transformer"
    finally:
        if env_backup is not None:
            os.environ["EMBEDDING_PROVIDER"] = env_backup


# ---------------------------------------------------------------------------
# Regression: production startup fails clearly on invalid provider
# ---------------------------------------------------------------------------

def test_initialize_raises_when_provider_not_registered():
    """initialize() must raise ValueError when the configured provider is missing."""
    service = make_service_with_providers("sentence_transformer", "mock")
    engine = make_engine(service, provider_env="nonexistent_provider")

    with pytest.raises(ValueError, match="nonexistent_provider"):
        engine.initialize()


def test_initialize_error_message_lists_available_providers():
    """The ValueError from initialize() must list available providers."""
    service = make_service_with_providers("sentence_transformer", "mock")
    engine = make_engine(service, provider_env="bad_provider")

    with pytest.raises(ValueError) as exc_info:
        engine.initialize()

    error_msg = str(exc_info.value)
    assert "sentence_transformer" in error_msg
    assert "mock" in error_msg
    assert "EMBEDDING_PROVIDER" in error_msg


# ---------------------------------------------------------------------------
# Production startup: real provider selected and works
# ---------------------------------------------------------------------------

def test_initialize_succeeds_with_sentence_transformer_registered():
    """Production default 'sentence_transformer' must pass initialize() validation."""
    service = make_service_with_providers("sentence_transformer", "mock")
    engine = make_engine(service)  # no env override -> default = sentence_transformer

    # Must not raise
    engine.initialize()
    assert engine._active_provider == "sentence_transformer"


def test_embed_text_uses_sentence_transformer_by_default():
    """embed_text() with no provider_name must route to sentence_transformer, not mock."""
    service = make_service_with_providers("sentence_transformer", "mock")
    engine = make_engine(service)
    engine.initialize()

    req = EmbeddingRequest(text="hello world")  # no provider_name -> uses _active_provider
    resp = engine.embed_text(req)

    assert resp.provider_name == "sentence_transformer"
    assert resp.error is None


# ---------------------------------------------------------------------------
# Explicit mock: tests/development can still request the mock provider
# ---------------------------------------------------------------------------

def test_mock_provider_works_when_explicitly_requested_via_env():
    """EMBEDDING_PROVIDER=mock must still work -- useful for tests."""
    service = make_service_with_providers("sentence_transformer", "mock")
    engine = make_engine(service, provider_env="mock")
    engine.initialize()  # must not raise

    assert engine._active_provider == "mock"


def test_mock_provider_works_when_explicitly_requested_per_request():
    """Passing provider_name='mock' on an EmbeddingRequest must use mock even in production."""
    service = make_service_with_providers("sentence_transformer", "mock")
    engine = make_engine(service)  # default = sentence_transformer
    engine.initialize()

    req = EmbeddingRequest(text="test embedding", provider_name="mock")
    resp = engine.embed_text(req)

    assert resp.provider_name == "mock"
    assert resp.error is None


# ---------------------------------------------------------------------------
# Edge case: initialize() with no registered providers skips validation
# ---------------------------------------------------------------------------

def test_initialize_skips_validation_when_no_providers_registered():
    """If no providers are registered yet, initialize() must not raise (deferred registration)."""
    service = EmbeddingServiceImpl()  # empty -- no providers registered
    cache = EmbeddingCacheImpl()
    engine = EmbeddingEngineImpl(service, cache)

    # Must not raise (validation only runs when providers exist)
    engine.initialize()

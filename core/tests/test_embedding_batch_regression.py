from typing import List

import pytest
from aios.services.persistence import (
    EmbeddingMetadata,
    EmbeddingProvider,
    EmbeddingRequest,
)
from aios.services.persistence_impl import (
    EmbeddingCacheImpl,
    EmbeddingEngineImpl,
    EmbeddingServiceImpl,
)


# Custom Mock Providers for testing batch behaviors
class NativeBatchProvider(EmbeddingProvider):
    def __init__(self) -> None:
        self.embed_text_calls = 0
        self.embed_batch_calls = 0

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def embed_text(self, text: str) -> List[float]:
        self.embed_text_calls += 1
        return [float(len(text))] * 1536

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        self.embed_batch_calls += 1
        return [[float(len(t))] * 1536 for t in texts]

    def get_metadata(self) -> EmbeddingMetadata:
        return EmbeddingMetadata(
            model_name="native-batch-model", version="v1", dimensions=1536, provider_type="NATIVE"
        )


class SequentialFallbackProvider(EmbeddingProvider):
    def __init__(self) -> None:
        self.embed_text_calls = 0
        self.embed_batch_calls = 0

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def embed_text(self, text: str) -> List[float]:
        self.embed_text_calls += 1
        return [float(len(text))] * 1536

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        self.embed_batch_calls += 1
        raise NotImplementedError("Batch embedding not natively supported.")

    def get_metadata(self) -> EmbeddingMetadata:
        return EmbeddingMetadata(
            model_name="sequential-fallback-model",
            version="v1",
            dimensions=1536,
            provider_type="SEQUENTIAL",
        )


class PartialFailureProvider(EmbeddingProvider):
    def __init__(self) -> None:
        self.embed_batch_calls = 0

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def embed_text(self, text: str) -> List[float]:
        return [1.0] * 1536

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        self.embed_batch_calls += 1
        results = []
        for t in texts:
            if t == "fail-validation":
                # Returns vector with invalid dimensions to trigger validation failure
                results.append([1.0] * 500)
            else:
                results.append([1.0] * 1536)
        return results

    def get_metadata(self) -> EmbeddingMetadata:
        return EmbeddingMetadata(
            model_name="partial-failure-model",
            version="v1",
            dimensions=1536,
            provider_type="PARTIAL",
        )


@pytest.fixture
def test_setup():
    service = EmbeddingServiceImpl()

    native_provider = NativeBatchProvider()
    fallback_provider = SequentialFallbackProvider()
    partial_provider = PartialFailureProvider()

    service.register_provider("native", native_provider)
    service.register_provider("fallback", fallback_provider)
    service.register_provider("partial", partial_provider)

    cache = EmbeddingCacheImpl()
    cache.initialize()

    engine = EmbeddingEngineImpl(service, cache)
    engine._active_provider = "native"
    engine.initialize()

    return {
        "engine": engine,
        "cache": cache,
        "native": native_provider,
        "fallback": fallback_provider,
        "partial": partial_provider,
    }


def test_native_batch_embedding(test_setup):
    """Verify that native batch API is called when supported by the provider."""
    engine = test_setup["engine"]
    prov = test_setup["native"]

    reqs = [
        EmbeddingRequest(text="hello", provider_name="native"),
        EmbeddingRequest(text="world", provider_name="native"),
    ]

    responses = engine.embed_batch(reqs)

    assert len(responses) == 2
    assert responses[0].text == "hello"
    assert len(responses[0].vector) == 1536
    assert responses[1].text == "world"

    assert prov.embed_batch_calls == 1
    assert prov.embed_text_calls == 0


def test_sequential_fallback_embedding(test_setup):
    """Verify that we fall back to sequential calls when embed_batch raises NotImplementedError."""
    engine = test_setup["engine"]
    prov = test_setup["fallback"]

    reqs = [
        EmbeddingRequest(text="foo", provider_name="fallback"),
        EmbeddingRequest(text="bar", provider_name="fallback"),
    ]

    responses = engine.embed_batch(reqs)

    assert len(responses) == 2
    assert responses[0].text == "foo"
    assert responses[1].text == "bar"

    assert prov.embed_batch_calls == 1
    assert prov.embed_text_calls == 2


def test_partial_failures_in_batch(test_setup):
    """Verify that validation failures on a single request don't fail the whole batch."""
    engine = test_setup["engine"]
    prov = test_setup["partial"]

    reqs = [
        EmbeddingRequest(text="success-1", provider_name="partial"),
        EmbeddingRequest(text="fail-validation", provider_name="partial"),
        EmbeddingRequest(text="success-2", provider_name="partial"),
    ]

    responses = engine.embed_batch(reqs)

    assert len(responses) == 3
    assert responses[0].error is None
    assert len(responses[0].vector) == 1536

    # Second request fails validation (mismatch dimensions) but returns safe error
    assert responses[1].error is not None
    assert responses[1].vector == []

    assert responses[2].error is None
    assert len(responses[2].vector) == 1536

    assert prov.embed_batch_calls == 1


def test_batch_statistics_and_cache_behavior(test_setup):
    """Verify that cache hits are bypassed, misses are cached, and

    statistics are updated correctly.
    """
    engine = test_setup["engine"]
    cache = test_setup["cache"]
    prov = test_setup["native"]

    # 1. Warm cache for one text
    cache.set("cached-text", [9.9] * 1536, "v1")

    reqs = [
        EmbeddingRequest(text="cached-text", provider_name="native"),  # cache hit
        EmbeddingRequest(text="uncached-text", provider_name="native"),  # cache miss
    ]

    responses = engine.embed_batch(reqs)

    assert len(responses) == 2
    assert responses[0].text == "cached-text"
    assert responses[0].vector == [9.9] * 1536

    assert responses[1].text == "uncached-text"
    assert responses[1].vector == [13.0] * 1536  # NativeBatchProvider len("uncached-text") = 13

    # Native batch should only be called once, with only 1 text ("uncached-text")
    assert prov.embed_batch_calls == 1
    assert prov.embed_text_calls == 0

    # Verify new text is now in cache
    assert cache.get("uncached-text", "v1") == [13.0] * 1536

    # Verify statistics
    stats = engine.get_statistics()
    assert stats["operation_counts"]["batch_embed"] == 1
    assert stats["operation_counts"]["failures"] == 0
    assert len(engine.latencies) == 1

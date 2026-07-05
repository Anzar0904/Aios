import os
import time

import pytest
from aios.services.persistence_impl import EmbeddingCacheImpl


@pytest.fixture(autouse=True)
def clean_env():
    # Keep env clean of any other tests cache overrides
    old_max = os.environ.get("EMBEDDING_CACHE_MAX_SIZE")
    old_ttl = os.environ.get("EMBEDDING_CACHE_TTL")

    os.environ.pop("EMBEDDING_CACHE_MAX_SIZE", None)
    os.environ.pop("EMBEDDING_CACHE_TTL", None)

    yield

    if old_max is not None:
        os.environ["EMBEDDING_CACHE_MAX_SIZE"] = old_max
    else:
        os.environ.pop("EMBEDDING_CACHE_MAX_SIZE", None)

    if old_ttl is not None:
        os.environ["EMBEDDING_CACHE_TTL"] = old_ttl
    else:
        os.environ.pop("EMBEDDING_CACHE_TTL", None)


def test_cache_lru_eviction():
    """Verify that the cache evicts the least recently used element when exceeding max_size."""
    os.environ["EMBEDDING_CACHE_MAX_SIZE"] = "3"
    os.environ["EMBEDDING_CACHE_TTL"] = "0"  # No expiration

    cache = EmbeddingCacheImpl()
    cache.initialize()

    cache.set("text1", [1.0], "v1")
    cache.set("text2", [2.0], "v1")
    cache.set("text3", [3.0], "v1")

    # Access text1 to make it most recently used
    assert cache.get("text1", "v1") == [1.0]

    # Add text4, exceeding size limit of 3
    cache.set("text4", [4.0], "v1")

    # text2 should be evicted because it was the least recently used
    # (text1 was accessed, text3 was added after text2, text4 added last)
    assert cache.get("text2", "v1") is None

    # Check other items still exist
    assert cache.get("text1", "v1") == [1.0]
    assert cache.get("text3", "v1") == [3.0]
    assert cache.get("text4", "v1") == [4.0]


def test_cache_ttl_expiration():
    """Verify that cached elements expire after their configured TTL."""
    os.environ["EMBEDDING_CACHE_MAX_SIZE"] = "10"
    os.environ["EMBEDDING_CACHE_TTL"] = "1"  # 1 second TTL

    cache = EmbeddingCacheImpl()
    cache.initialize()

    cache.set("text1", [1.0], "v1")
    assert cache.get("text1", "v1") == [1.0]

    # Sleep to allow the cache entry to expire
    time.sleep(1.1)

    # Item should be expired and return None
    assert cache.get("text1", "v1") is None


def test_cache_size_limits():
    """Verify that the cache size never exceeds EMBEDDING_CACHE_MAX_SIZE."""
    os.environ["EMBEDDING_CACHE_MAX_SIZE"] = "5"
    os.environ["EMBEDDING_CACHE_TTL"] = "0"

    cache = EmbeddingCacheImpl()
    cache.initialize()

    for i in range(10):
        cache.set(f"text{i}", [float(i)], "v1")

    stats = cache.get_statistics()
    assert stats["cache_size"] == 5


def test_cache_statistics_after_eviction():
    """Verify hit, miss, size, and ratio stats remain correct after evictions/expirations."""
    os.environ["EMBEDDING_CACHE_MAX_SIZE"] = "2"
    os.environ["EMBEDDING_CACHE_TTL"] = "1"

    cache = EmbeddingCacheImpl()
    cache.initialize()

    cache.set("text1", [1.0], "v1")
    cache.set("text2", [2.0], "v1")

    # Hits: 1 (text1), Misses: 0
    assert cache.get("text1", "v1") == [1.0]

    # Hits: 1, Misses: 1 (text3)
    assert cache.get("text3", "v1") is None

    # Evict text2 by adding text4 (lru evicted text2 because text1 was accessed)
    cache.set("text4", [4.0], "v1")

    # Hits: 1, Misses: 2 (text2 was evicted)
    assert cache.get("text2", "v1") is None

    stats = cache.get_statistics()
    assert stats["cache_size"] == 2
    assert stats["hits"] == 1
    assert stats["misses"] == 2
    assert stats["hit_ratio"] == 1 / 3.0

    # Wait for expiration
    time.sleep(1.1)

    # Stats cleanup expired entries: size becomes 0
    stats = cache.get_statistics()
    assert stats["cache_size"] == 0
    assert stats["hits"] == 1
    assert stats["misses"] == 2

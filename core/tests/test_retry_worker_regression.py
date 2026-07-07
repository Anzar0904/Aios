import os
import time
from unittest.mock import MagicMock, patch

import pytest
from aios.services.persistence import EmbeddingResponse
from aios.services.persistence_impl import EmbeddingEngineImpl


# Ensuring clean env and configuration overrides
@pytest.fixture(autouse=True)
def clean_env():
    old_backoff = os.environ.get("AIOS_RETRY_BASE_BACKOFF")
    old_max = os.environ.get("AIOS_RETRY_MAX_ATTEMPTS")

    os.environ.pop("AIOS_RETRY_BASE_BACKOFF", None)
    os.environ.pop("AIOS_RETRY_MAX_ATTEMPTS", None)

    yield

    if old_backoff is not None:
        os.environ["AIOS_RETRY_BASE_BACKOFF"] = old_backoff
    else:
        os.environ.pop("AIOS_RETRY_BASE_BACKOFF", None)

    if old_max is not None:
        os.environ["AIOS_RETRY_MAX_ATTEMPTS"] = old_max
    else:
        os.environ.pop("AIOS_RETRY_MAX_ATTEMPTS", None)


class MockDB:
    def __init__(self):
        self.queries = []
        self.results = {}

    def execute(self, query, params=None):
        self.queries.append((query, params))
        for key, value in self.results.items():
            if key in query:
                return value
        return []


class MockRepos:
    def __init__(self):
        self.repositories = {}

    def get_repository(self, name):
        return self.repositories.setdefault(name, MagicMock())


@pytest.fixture
def retry_setup():
    service = MagicMock()
    cache = MagicMock()
    engine = EmbeddingEngineImpl(service, cache)

    mock_db = MockDB()
    mock_repos = MockRepos()

    # Mock ServiceRegistry._global_registry.get
    mock_registry = MagicMock()

    def registry_get(service_cls):
        from aios.services.persistence import PersistenceService, RepositoryRegistry

        if service_cls == PersistenceService:
            return mock_db
        if service_cls == RepositoryRegistry:
            return mock_repos
        return None

    mock_registry.get.side_effect = registry_get

    return {
        "engine": engine,
        "db": mock_db,
        "repos": mock_repos,
        "registry": mock_registry,
    }


def test_retry_worker_success(retry_setup):
    """Verify that a successful retry removes the job and saves the vector."""
    engine = retry_setup["engine"]
    db = retry_setup["db"]
    repos = retry_setup["repos"]
    registry = retry_setup["registry"]

    # Setup eligible pending job
    db.results["pending_embedding_jobs"] = [
        {
            "id": "job123",
            "text": "test text",
            "provider_name": "mock",
            "collection_name": "col123",
            "attempts": 1,
            "created_at": time.time() - 100,
            "updated_at": time.time() - 100,
        }
    ]

    # Mock embed_batch to succeed
    mock_vector = [0.1, 0.2]
    with patch.object(engine, "embed_batch") as mock_embed_batch:
        mock_embed_batch.return_value = [
            EmbeddingResponse(
                text="test text", vector=mock_vector, version="v1", provider_name="mock"
            )
        ]

        with patch("aios.registry.ServiceRegistry._global_registry", registry):
            engine.run_retry_cycle()

        # Verify it called embed_batch with the correct EmbeddingRequest
        mock_embed_batch.assert_called_once()
        reqs = mock_embed_batch.call_args[0][0]
        assert len(reqs) == 1
        assert reqs[0].text == "test text"

    # Verify the job is deleted from the DB
    delete_queries = [q for q, p in db.queries if "DELETE FROM pending_embedding_jobs" in q]
    assert len(delete_queries) == 1
    assert delete_queries[0] == "DELETE FROM pending_embedding_jobs WHERE id = ?"

    # Verify the vector is saved to repository
    repos.get_repository("col123").save.assert_called_once_with(
        "job123", mock_vector, {"text": "test text"}, retry=True
    )


def test_retry_worker_failure(retry_setup):
    """Verify that a failed retry updates attempts and updated_at, without deleting it."""
    engine = retry_setup["engine"]
    db = retry_setup["db"]
    registry = retry_setup["registry"]

    db.results["pending_embedding_jobs"] = [
        {
            "id": "job123",
            "text": "test text",
            "provider_name": "mock",
            "collection_name": "col123",
            "attempts": 2,
            "created_at": time.time() - 100,
            "updated_at": time.time() - 100,
        }
    ]

    with patch.object(engine, "embed_batch") as mock_embed_batch:
        mock_embed_batch.return_value = [
            EmbeddingResponse(
                text="test text",
                vector=[],
                version="unknown",
                provider_name="mock",
                error="Failed again",
            )
        ]

        with patch("aios.registry.ServiceRegistry._global_registry", registry):
            engine.run_retry_cycle()

    # Verify job is updated (attempts incremented to 3) instead of deleted
    delete_queries = [q for q, p in db.queries if "DELETE" in q]
    assert len(delete_queries) == 0

    update_queries = [(q, p) for q, p in db.queries if "UPDATE pending_embedding_jobs" in q]
    assert len(update_queries) == 1
    query, params = update_queries[0]
    assert params[0] == "PENDING"  # status
    assert params[1] == 3  # next_attempts


def test_retry_worker_exponential_backoff(retry_setup):
    """Verify that exponential backoff blocks retries until the backoff period has passed."""
    engine = retry_setup["engine"]
    db = retry_setup["db"]
    registry = retry_setup["registry"]

    os.environ["AIOS_RETRY_BASE_BACKOFF"] = "10.0"

    # Setup two jobs:
    # job_ready: attempts=1, updated_at=now - 11s (backoff is 10 * 2^0 = 10s -> ready!)
    # job_not_ready: attempts=2, updated_at=now - 11s (backoff is 10 * 2^1 = 20s -> not ready!)
    now = time.time()
    db.results["pending_embedding_jobs"] = [
        {
            "id": "job_ready",
            "text": "ready text",
            "provider_name": "mock",
            "collection_name": "col",
            "attempts": 1,
            "created_at": now - 100,
            "updated_at": now - 11,
        },
        {
            "id": "job_not_ready",
            "text": "not ready text",
            "provider_name": "mock",
            "collection_name": "col",
            "attempts": 2,
            "created_at": now - 100,
            "updated_at": now - 11,
        },
    ]

    with patch.object(engine, "embed_batch") as mock_embed_batch:
        mock_embed_batch.return_value = [
            EmbeddingResponse(text="ready text", vector=[1.0], version="v1", provider_name="mock")
        ]

        with patch("aios.registry.ServiceRegistry._global_registry", registry):
            engine.run_retry_cycle()

        mock_embed_batch.assert_called_once()
        reqs = mock_embed_batch.call_args[0][0]
        # Only job_ready should have been retried
        assert len(reqs) == 1
        assert reqs[0].text == "ready text"


def test_retry_worker_batched_processing(retry_setup):
    """Verify that multiple eligible jobs are grouped and batched into a single embed_batch call."""
    engine = retry_setup["engine"]
    db = retry_setup["db"]
    registry = retry_setup["registry"]

    now = time.time()
    db.results["pending_embedding_jobs"] = [
        {
            "id": "job1",
            "text": "text 1",
            "provider_name": "mock",
            "collection_name": "col1",
            "attempts": 1,
            "created_at": now - 100,
            "updated_at": now - 100,
        },
        {
            "id": "job2",
            "text": "text 2",
            "provider_name": "mock",
            "collection_name": "col1",
            "attempts": 1,
            "created_at": now - 100,
            "updated_at": now - 100,
        },
    ]

    with patch.object(engine, "embed_batch") as mock_embed_batch:
        mock_embed_batch.return_value = [
            EmbeddingResponse(text="text 1", vector=[1.0], version="v1", provider_name="mock"),
            EmbeddingResponse(text="text 2", vector=[1.0], version="v1", provider_name="mock"),
        ]

        with patch("aios.registry.ServiceRegistry._global_registry", registry):
            engine.run_retry_cycle()

        # Verify that both jobs were sent in a single batch call
        mock_embed_batch.assert_called_once()
        reqs = mock_embed_batch.call_args[0][0]
        assert len(reqs) == 2
        assert {reqs[0].text, reqs[1].text} == {"text 1", "text 2"}

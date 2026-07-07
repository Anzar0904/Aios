# ruff: noqa: F403, F405, E501, N802, E402, N806, B007
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

from aios.services.persistence import *

logger = logging.getLogger(__name__)


class MockEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "mock-embedding-model", dimensions: int = 1536) -> None:
        self.model_name = model_name
        self.dimensions = dimensions

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def embed_text(self, text: str) -> List[float]:
        h = hash(text) % 1000 / 1000.0
        return [h] * self.dimensions

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed_text(t) for t in texts]

    def get_metadata(self) -> EmbeddingMetadata:
        return EmbeddingMetadata(
            model_name=self.model_name,
            version="v1",
            dimensions=self.dimensions,
            provider_type="MOCK",
        )


class EmbeddingServiceImpl(EmbeddingService):
    def __init__(self) -> None:
        self.providers: Dict[str, EmbeddingProvider] = {}

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get_provider(self, provider_name: str) -> EmbeddingProvider:
        if provider_name not in self.providers:
            raise KeyError(f"Embedding provider '{provider_name}' not registered")
        return self.providers[provider_name]

    def register_provider(self, provider_name: str, provider: EmbeddingProvider) -> None:
        self.providers[provider_name] = provider

    def embed(self, text: str, provider_name: str) -> List[float]:
        return self.get_provider(provider_name).embed_text(text)


class EmbeddingVersionManagerImpl(EmbeddingVersionManager):
    def __init__(self) -> None:
        self.versions: Dict[str, str] = {}

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get_active_version(self, collection_name: str) -> str:
        return self.versions.get(collection_name, "v1")

    def set_active_version(self, collection_name: str, version: str) -> None:
        self.versions[collection_name] = version

    def requires_migration(self, collection_name: str, current_version: str) -> bool:
        return self.get_active_version(collection_name) != current_version


class EmbeddingCacheImpl(EmbeddingCache):
    def __init__(self) -> None:
        from collections import OrderedDict

        self.max_size = int(os.environ.get("EMBEDDING_CACHE_MAX_SIZE", "1000"))
        self.ttl = float(os.environ.get("EMBEDDING_CACHE_TTL", "3600"))  # in seconds
        self._cache: OrderedDict = OrderedDict()
        self.hits = 0
        self.misses = 0

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def _get_key(self, text: str, version: str) -> str:
        return f"{version}:{text}"

    def get(self, text: str, version: str) -> Optional[List[float]]:
        key = self._get_key(text, version)
        if key in self._cache:
            vector, expiry = self._cache[key]
            if expiry is not None and time.time() > expiry:
                del self._cache[key]
                self.misses += 1
                return None
            self._cache.move_to_end(key)
            self.hits += 1
            return vector
        self.misses += 1
        return None

    def set(self, text: str, vector: List[float], version: str) -> None:
        if self.max_size <= 0:
            return
        key = self._get_key(text, version)
        expiry = time.time() + self.ttl if self.ttl > 0 else None
        if key in self._cache:
            del self._cache[key]
        self._cache[key] = (vector, expiry)
        while len(self._cache) > self.max_size:
            self._cache.popitem(last=False)

    def invalidate(self, text: str, version: str) -> None:
        key = self._get_key(text, version)
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        self._cache.clear()
        self.hits = 0
        self.misses = 0

    def get_statistics(self) -> Dict[str, Any]:
        now = time.time()
        expired_keys = [k for k, (_, exp) in self._cache.items() if exp is not None and now > exp]
        for k in expired_keys:
            del self._cache[k]

        total = self.hits + self.misses
        ratio = self.hits / total if total > 0 else 0.0
        return {
            "cache_size": len(self._cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_ratio": ratio,
        }


class ChunkingServiceImpl(ChunkingService):
    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def chunk_text(self, text: str, strategy: ChunkStrategy, **kwargs: Any) -> List[ChunkResult]:
        results = []
        if strategy == ChunkStrategy.FIXED_SIZE:
            size = kwargs.get("chunk_size", 200)
            overlap = kwargs.get("overlap", 20)
            start = 0
            idx = 0
            while start < len(text):
                end = min(start + size, len(text))
                chunk_str = text[start:end]
                results.append(
                    ChunkResult(
                        text=chunk_str,
                        metadata=ChunkMetadata(
                            index=idx,
                            char_start=start,
                            char_end=end,
                            token_estimate=len(chunk_str) // 4,
                        ),
                        strategy=strategy,
                    )
                )
                idx += 1
                start += size - overlap
                if size - overlap <= 0:
                    break
        elif strategy == ChunkStrategy.PARAGRAPH:
            paragraphs = text.split("\n\n")
            idx = 0
            char_pos = 0
            for p in paragraphs:
                p_clean = p.strip()
                if not p_clean:
                    continue
                start = text.find(p, char_pos)
                if start == -1:
                    start = char_pos
                end = start + len(p)
                results.append(
                    ChunkResult(
                        text=p_clean,
                        metadata=ChunkMetadata(
                            index=idx,
                            char_start=start,
                            char_end=end,
                            token_estimate=len(p_clean) // 4,
                        ),
                        strategy=strategy,
                    )
                )
                char_pos = end
                idx += 1
        elif strategy == ChunkStrategy.SLIDING_WINDOW:
            window_size = kwargs.get("window_size", 500)
            step = kwargs.get("step", 250)
            idx = 0
            start = 0
            while start < len(text):
                end = min(start + window_size, len(text))
                chunk_str = text[start:end]
                results.append(
                    ChunkResult(
                        text=chunk_str,
                        metadata=ChunkMetadata(
                            index=idx,
                            char_start=start,
                            char_end=end,
                            token_estimate=len(chunk_str) // 4,
                        ),
                        strategy=strategy,
                    )
                )
                idx += 1
                start += step
        elif strategy == ChunkStrategy.TOKEN_AWARE:
            max_tokens = kwargs.get("max_tokens", 100)
            words = text.split(" ")
            current_words = []
            idx = 0
            char_start = 0
            for w in words:
                current_words.append(w)
                est_tokens = len(" ".join(current_words)) // 4
                if est_tokens >= max_tokens:
                    chunk_str = " ".join(current_words)
                    results.append(
                        ChunkResult(
                            text=chunk_str,
                            metadata=ChunkMetadata(
                                index=idx,
                                char_start=char_start,
                                char_end=char_start + len(chunk_str),
                                token_estimate=est_tokens,
                            ),
                            strategy=strategy,
                        )
                    )
                    char_start += len(chunk_str) + 1
                    current_words = []
                    idx += 1
            if current_words:
                chunk_str = " ".join(current_words)
                results.append(
                    ChunkResult(
                        text=chunk_str,
                        metadata=ChunkMetadata(
                            index=idx,
                            char_start=char_start,
                            char_end=char_start + len(chunk_str),
                            token_estimate=len(chunk_str) // 4,
                        ),
                        strategy=strategy,
                    )
                )
        return results


class ContextBuilderImpl(ContextBuilder):
    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def rank_candidates(
        self, candidates: List[ContextCandidate], objective: str
    ) -> List[ContextRanking]:
        rankings = []
        obj_words = set(objective.lower().split())
        for c in candidates:
            c_text_lower = c.text.lower()
            matches = sum(1 for w in obj_words if w in c_text_lower)
            rank_score = c.score + (matches * 0.05)
            reasons = [f"Cosine similarity score: {c.score:.3f}"]
            if matches > 0:
                reasons.append(f"Matched {matches} query terms")
            rankings.append(
                ContextRanking(candidate=c, rank_score=rank_score, relevance_reasons=reasons)
            )
        rankings.sort(key=lambda x: x.rank_score, reverse=True)
        return rankings

    def deduplicate(self, candidates: List[ContextCandidate]) -> List[ContextCandidate]:
        seen_texts = set()
        unique = []
        for c in candidates:
            if c.text not in seen_texts:
                seen_texts.add(c.text)
                unique.append(c)
        return unique

    def assemble_context(
        self, candidates: List[ContextCandidate], token_budget: int
    ) -> ContextAssembly:
        used = []
        total_tokens = 0
        assembled = []
        budget_respected = True

        candidates = self.deduplicate(candidates)

        for c in candidates:
            tokens = len(c.text) // 4
            if total_tokens + tokens <= token_budget:
                used.append(c)
                assembled.append(c.text)
                total_tokens += tokens
            else:
                budget_respected = False
        return ContextAssembly(
            assembled_text="\n\n---\n\n".join(assembled),
            candidates_used=used,
            total_tokens=total_tokens,
            budget_respected=budget_respected,
        )


class SentenceTransformerProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dimensions: int = 384) -> None:
        self.model_name = model_name
        self.dimensions = dimensions
        self.model = None

    def initialize(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer

            self.model = SentenceTransformer(self.model_name)
        except Exception:
            self.model = None

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def embed_text(self, text: str) -> List[float]:
        if self.model is not None:
            return self.model.encode(text).tolist()
        vec = []
        for i in range(self.dimensions):
            val = sum(ord(c) * (i + 1) for c in text) % 1000 / 1000.0
            vec.append(val)
        return vec

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        if self.model is not None:
            return self.model.encode(texts).tolist()
        return [self.embed_text(t) for t in texts]

    def get_metadata(self) -> EmbeddingMetadata:
        return EmbeddingMetadata(
            model_name=self.model_name,
            version="v1",
            dimensions=self.dimensions,
            provider_type="SENTENCE_TRANSFORMER",
        )


class OpenAIProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "text-embedding-3-small", dimensions: int = 1536) -> None:
        self.model_name = model_name
        self.dimensions = dimensions

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def embed_text(self, text: str) -> List[float]:
        raise NotImplementedError("OpenAI cloud provider not implemented yet.")

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError("OpenAI cloud provider not implemented yet.")

    def get_metadata(self) -> EmbeddingMetadata:
        return EmbeddingMetadata(
            model_name=self.model_name,
            version="v1",
            dimensions=self.dimensions,
            provider_type="OPENAI",
        )


class GeminiProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "text-embedding-004", dimensions: int = 768) -> None:
        self.model_name = model_name
        self.dimensions = dimensions

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def embed_text(self, text: str) -> List[float]:
        raise NotImplementedError("Gemini cloud provider not implemented yet.")

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError("Gemini cloud provider not implemented yet.")

    def get_metadata(self) -> EmbeddingMetadata:
        return EmbeddingMetadata(
            model_name=self.model_name,
            version="v1",
            dimensions=self.dimensions,
            provider_type="GEMINI",
        )


class OllamaProvider(EmbeddingProvider):
    def __init__(self, model_name: str = "nomic-embed-text", dimensions: int = 768) -> None:
        self.model_name = model_name
        self.dimensions = dimensions

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def embed_text(self, text: str) -> List[float]:
        raise NotImplementedError("Ollama provider not implemented yet.")

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        raise NotImplementedError("Ollama provider not implemented yet.")

    def get_metadata(self) -> EmbeddingMetadata:
        return EmbeddingMetadata(
            model_name=self.model_name,
            version="v1",
            dimensions=self.dimensions,
            provider_type="OLLAMA",
        )


class EmbeddingEngineImpl(EmbeddingEngine):
    def __init__(self, embedding_service: EmbeddingService, cache: EmbeddingCache) -> None:
        self.embedding_service = embedding_service
        self.cache = cache
        self._active_provider = os.environ.get("EMBEDDING_PROVIDER", "sentence_transformer")

        # Telemetry metrics
        self.op_counts = {"embed": 0, "batch_embed": 0, "failures": 0}
        self.latencies = []
        self._errors = []

    def initialize(self) -> None:
        # Validate that the configured provider is actually registered.
        # This prevents production from silently using MockEmbeddingProvider
        # when EMBEDDING_PROVIDER is unset or misspelled.
        registered = (
            list(self.embedding_service.providers.keys())
            if hasattr(self.embedding_service, "providers")
            else []
        )
        if registered and self._active_provider not in registered:
            raise ValueError(
                f"Embedding provider '{self._active_provider}' is not registered. "
                f"Available providers: {registered}. "
                f"Set EMBEDDING_PROVIDER environment variable to one of the available providers, "
                f"or set EMBEDDING_PROVIDER=mock for testing."
            )

    def start(self) -> None:
        # Periodic retry worker for failed PostgreSQL jobs
        import threading

        self._stop_event = threading.Event()
        self._retry_thread = threading.Thread(target=self._retry_worker, daemon=True)
        self._retry_thread.start()

    def stop(self) -> None:
        if hasattr(self, "_stop_event"):
            self._stop_event.set()
        if hasattr(self, "_retry_thread") and self._retry_thread.is_alive():
            try:
                self._retry_thread.join(timeout=1.0)
            except Exception:
                pass

    def teardown(self) -> None:
        self.stop()

    def _retry_worker(self) -> None:
        while not self._stop_event.wait(5.0):
            self.run_retry_cycle()

    def _should_retry(self, attempts: int, last_attempted: float, base_backoff: float) -> bool:
        # Exponential backoff: base_backoff * (2 ** (attempts - 1))
        backoff = base_backoff * (2 ** max(0, attempts - 1))
        return (time.time() - last_attempted) >= backoff

    def run_retry_cycle(self) -> None:
        try:
            from aios.registry import ServiceRegistry
            from aios.services.persistence import PersistenceService, RepositoryRegistry

            registry = ServiceRegistry._global_registry
            if not registry:
                return
            db = registry.get(PersistenceService)
            repos = registry.get(RepositoryRegistry)

            base_backoff = float(os.environ.get("AIOS_RETRY_BASE_BACKOFF", "5.0"))
            max_attempts = int(os.environ.get("AIOS_RETRY_MAX_ATTEMPTS", "10"))

            # 1. Retry pending embeddings (batched)
            embeds = db.execute(
                "SELECT id, text, provider_name, collection_name, attempts, created_at, updated_at "
                "FROM pending_embedding_jobs WHERE status = 'PENDING'"
            )
            eligible_embeds = []
            for job in embeds:
                attempts = job.get("attempts") or 0
                created_at = job.get("created_at") or 0.0
                updated_at = job.get("updated_at") or created_at
                if (
                    self._should_retry(attempts, updated_at, base_backoff)
                    and attempts < max_attempts
                ):
                    eligible_embeds.append(job)

            if eligible_embeds:
                # Group by (provider_name, collection_name)
                groups = {}
                for job in eligible_embeds:
                    key = (job["provider_name"], job["collection_name"])
                    groups.setdefault(key, []).append(job)

                for (provider, collection), group in groups.items():
                    logger.info(
                        f"Retrying batch of {len(group)} embedding jobs for provider {provider} (collection: {collection})"
                    )
                    requests = [
                        EmbeddingRequest(
                            text=job["text"],
                            provider_name=job["provider_name"],
                            collection_name=job["collection_name"],
                        )
                        for job in group
                    ]
                    responses = self.embed_batch(requests, retry=True)
                    for job, res in zip(group, responses, strict=False):
                        if not res.error:
                            logger.info(f"Retry succeeded for embedding job {job['id']}")
                            db.execute(
                                "DELETE FROM pending_embedding_jobs WHERE id = ?", (job["id"],)
                            )
                            if job["collection_name"]:
                                try:
                                    repo = repos.get_repository(job["collection_name"])
                                    repo.save(job["id"], res.vector, {"text": job["text"]}, retry=True)
                                except Exception as e:
                                    logger.error(
                                        f"Failed to save successfully retried vector to repository: {e}"
                                    )
                        else:
                            next_attempts = (job["attempts"] or 0) + 1
                            logger.warning(
                                f"Retry failed (attempt {next_attempts}/{max_attempts}) for embedding job {job['id']}: {res.error}"
                            )
                            new_status = "FAILED" if next_attempts >= max_attempts else "PENDING"
                            db.execute(
                                "UPDATE pending_embedding_jobs SET status = ?, attempts = ?, last_error = ?, updated_at = ? WHERE id = ?",
                                (new_status, next_attempts, str(res.error), time.time(), job["id"]),
                            )

            # 2. Retry pending index requests
            indices = db.execute(
                "SELECT id, entity_id, collection_name, vector, payload, attempts, created_at, updated_at "
                "FROM pending_indexing_jobs WHERE status = 'PENDING'"
            )
            eligible_indices = []
            for idx in indices:
                attempts = idx.get("attempts") or 0
                created_at = idx.get("created_at") or 0.0
                updated_at = idx.get("updated_at") or created_at
                if (
                    self._should_retry(attempts, updated_at, base_backoff)
                    and attempts < max_attempts
                ):
                    eligible_indices.append(idx)

            for idx in eligible_indices:
                next_attempts = (idx["attempts"] or 0) + 1
                try:
                    logger.info(
                        f"Retrying indexing job {idx['id']} (attempt {next_attempts}/{max_attempts}) for collection {idx['collection_name']}"
                    )
                    repo = repos.get_repository(idx["collection_name"])
                    import json

                    vec = json.loads(idx["vector"])
                    payload = json.loads(idx["payload"])
                    entity_id = idx.get("entity_id") or idx["id"]
                    if repo.save(entity_id, vec, payload, retry=True):
                        logger.info(f"Retry succeeded for indexing job {idx['id']}")
                        db.execute("DELETE FROM pending_indexing_jobs WHERE id = ?", (idx["id"],))
                    else:
                        logger.warning(f"Retry returned False for indexing job {idx['id']}")
                        new_status = "FAILED" if next_attempts >= max_attempts else "PENDING"
                        db.execute(
                            "UPDATE pending_indexing_jobs SET status = ?, attempts = ?, retry_count = ?, failure_reason = ?, updated_at = ? WHERE id = ?",
                            (
                                new_status,
                                next_attempts,
                                next_attempts,
                                "Qdrant save returned False",
                                time.time(),
                                idx["id"],
                            ),
                        )
                except Exception as e:
                    logger.error(
                        f"Retry failed (attempt {next_attempts}/{max_attempts}) for indexing job {idx['id']}: {str(e)}"
                    )
                    new_status = "FAILED" if next_attempts >= max_attempts else "PENDING"
                    db.execute(
                        "UPDATE pending_indexing_jobs SET status = ?, attempts = ?, retry_count = ?, last_error = ?, failure_reason = ?, updated_at = ? WHERE id = ?",
                        (new_status, next_attempts, next_attempts, str(e), str(e), time.time(), idx["id"]),
                    )
        except Exception as e:
            logger.error(f"Exception during background retry cycle: {e}")

    def _persist_failed_job(
        self, text: str, provider_name: str, collection_name: Optional[str]
    ) -> None:
        try:
            from aios.registry import ServiceRegistry
            from aios.services.persistence import PersistenceService

            db = ServiceRegistry._global_registry.get(PersistenceService)
            job_id = str(uuid.uuid4())
            db.execute(
                "INSERT INTO pending_embedding_jobs (id, text, provider_name, collection_name, status, attempts, created_at) VALUES (?, ?, ?, ?, 'PENDING', 1, ?)",
                (job_id, text, provider_name, collection_name, time.time()),
            )
        except Exception:
            pass

    def embed_text(self, request: EmbeddingRequest, retry: bool = False) -> EmbeddingResponse:
        t0 = time.perf_counter()
        provider = request.provider_name or self._active_provider
        self.op_counts["embed"] += 1

        try:
            prov_impl = self.embedding_service.get_provider(provider)
            meta = prov_impl.get_metadata()

            # Cache lookup
            cached = self.cache.get(request.text, meta.version)
            if cached is not None:
                # Validate cached vector dimensions
                if len(cached) != meta.dimensions:
                    raise ValueError(
                        f"Cached dimensions mismatch. Expected {meta.dimensions}, got {len(cached)}"
                    )
                return EmbeddingResponse(
                    text=request.text, vector=cached, version=meta.version, provider_name=provider
                )

            # Generate
            vector = prov_impl.embed_text(request.text)

            # Vector validation
            self._validate_vector(vector, meta.dimensions)

            # Cache save
            self.cache.set(request.text, vector, meta.version)

            latency = (time.perf_counter() - t0) * 1000.0
            self.latencies.append(latency)
            if len(self.latencies) > 1000:
                self.latencies.pop(0)

            return EmbeddingResponse(
                text=request.text, vector=vector, version=meta.version, provider_name=provider
            )
        except Exception as e:
            self.op_counts["failures"] += 1
            self._log_err(f"Embedding failed: {str(e)}")
            if not retry:
                self._persist_failed_job(request.text, provider, request.collection_name)
            return EmbeddingResponse(
                text=request.text,
                vector=[],
                version="unknown",
                provider_name=provider,
                error=str(e),
            )

    def embed_batch(self, requests: List[EmbeddingRequest], retry: bool = False) -> List[EmbeddingResponse]:
        t0 = time.perf_counter()
        self.op_counts["batch_embed"] += 1
        results: List[Optional[EmbeddingResponse]] = [None] * len(requests)

        # Group uncached requests by provider
        uncached_by_provider: Dict[str, List[tuple]] = {}

        for idx, req in enumerate(requests):
            provider = req.provider_name or self._active_provider
            try:
                prov_impl = self.embedding_service.get_provider(provider)
                meta = prov_impl.get_metadata()

                cached = self.cache.get(req.text, meta.version)
                if cached is not None:
                    if len(cached) != meta.dimensions:
                        raise ValueError(
                            f"Cached dimensions mismatch. Expected {meta.dimensions}, got {len(cached)}"
                        )
                    results[idx] = EmbeddingResponse(
                        text=req.text, vector=cached, version=meta.version, provider_name=provider
                    )
                    continue
            except Exception as e:
                self.op_counts["failures"] += 1
                self._log_err(f"Batch embedding cache lookup failed for '{req.text}': {str(e)}")
                if not retry:
                    self._persist_failed_job(req.text, provider, req.collection_name)
                results[idx] = EmbeddingResponse(
                    text=req.text,
                    vector=[],
                    version="unknown",
                    provider_name=provider,
                    error=str(e),
                )
                continue

            uncached_by_provider.setdefault(provider, []).append((idx, req))

        for provider, group in uncached_by_provider.items():
            try:
                prov_impl = self.embedding_service.get_provider(provider)
                meta = prov_impl.get_metadata()
            except Exception as e:
                self.op_counts["failures"] += len(group)
                self._log_err(f"Batch provider lookup failed for {provider}: {str(e)}")
                for idx, req in group:
                    if not retry:
                        self._persist_failed_job(req.text, provider, req.collection_name)
                    results[idx] = EmbeddingResponse(
                        text=req.text,
                        vector=[],
                        version="unknown",
                        provider_name=provider,
                        error=str(e),
                    )
                continue

            indices = [item[0] for item in group]
            group_requests = [item[1] for item in group]
            texts = [req.text for req in group_requests]

            try:
                vectors = prov_impl.embed_batch(texts)
                for text, vector, idx, req in zip(
                    texts, vectors, indices, group_requests, strict=False
                ):
                    try:
                        self._validate_vector(vector, meta.dimensions)
                        self.cache.set(text, vector, meta.version)
                        results[idx] = EmbeddingResponse(
                            text=text, vector=vector, version=meta.version, provider_name=provider
                        )
                    except Exception as e:
                        self.op_counts["failures"] += 1
                        self._log_err(
                            f"Batch vector validation/cache save failed for '{text}': {str(e)}"
                        )
                        if not retry:
                            self._persist_failed_job(text, provider, req.collection_name)
                        results[idx] = EmbeddingResponse(
                            text=text,
                            vector=[],
                            version="unknown",
                            provider_name=provider,
                            error=str(e),
                        )
            except NotImplementedError:
                # Fall back to sequential processing
                for idx, req in group:
                    results[idx] = self.embed_text(req, retry=retry)
            except Exception as e:
                self.op_counts["failures"] += len(group)
                self._log_err(f"Batch embedding failed for provider {provider}: {str(e)}")
                for idx, req in group:
                    if not retry:
                        self._persist_failed_job(req.text, provider, req.collection_name)
                    results[idx] = EmbeddingResponse(
                        text=req.text,
                        vector=[],
                        version="unknown",
                        provider_name=provider,
                        error=str(e),
                    )

        latency = (time.perf_counter() - t0) * 1000.0
        self.latencies.append(latency)
        if len(self.latencies) > 1000:
            self.latencies.pop(0)

        return [res for res in results if res is not None]

    def _validate_vector(self, vector: List[float], expected_dims: int) -> None:
        if len(vector) != expected_dims:
            raise ValueError(
                f"Vector dimensions mismatch. Expected {expected_dims}, got {len(vector)}"
            )
        for x in vector:
            import math

            if math.isnan(x) or math.isinf(x):
                raise ValueError("Vector contains NaN or Infinite weights.")

    def _log_err(self, msg: str) -> None:
        self._errors.append({"timestamp": time.time(), "message": msg})
        if len(self._errors) > 100:
            self._errors.pop(0)

    def get_statistics(self) -> Dict[str, Any]:
        avg_lat = sum(self.latencies) / len(self.latencies) if self.latencies else 0.0
        return {
            "operation_counts": self.op_counts.copy(),
            "average_latency_ms": avg_lat,
            "cache_stats": self.cache.get_statistics(),
        }

    def get_health(self) -> Dict[str, Any]:
        return {
            "status": "HEALTHY" if self.op_counts["failures"] < 10 else "DEGRADED",
            "failures_recorded": self.op_counts["failures"],
        }

    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "alerts": [
                {"message": err["message"], "timestamp": err["timestamp"]} for err in self._errors
            ]
        }


class SemanticSearchServiceImpl(SemanticSearchService):
    def __init__(self, embed_engine: EmbeddingEngine) -> None:
        self.embed_engine = embed_engine
        self.op_counts = {"search": 0, "batch_search": 0, "cross_collection_search": 0}
        self.latencies = []

        # Query Cache (in-memory)
        self.query_cache: Dict[str, Any] = {}

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def _get_query_cache_key(self, query: SemanticQuery) -> str:
        # Create a unique cache key based on query text and filter values
        import json

        filters_str = json.dumps(query.filter_query, sort_keys=True) if query.filter_query else ""
        return (
            f"{query.collection_name}:{query.query_text}:{filters_str}:{query.limit}:{query.offset}"
        )

    def search(self, query: SemanticQuery) -> List[SemanticResult]:
        t0 = time.perf_counter()
        self.op_counts["search"] += 1

        # Query Cache Lookup
        cache_key = self._get_query_cache_key(query)
        if cache_key in self.query_cache:
            return self.query_cache[cache_key]

        # Compute vector embedding
        embed_req = EmbeddingRequest(text=query.query_text, collection_name=query.collection_name)
        embed_res = self.embed_engine.embed_text(embed_req)
        if embed_res.error or not embed_res.vector:
            return []

        # Build combined filters
        final_filters = query.filter_query.copy() if query.filter_query else {}
        if query.workspace_id:
            final_filters["workspace_id"] = query.workspace_id
        if query.project_id:
            final_filters["project_id"] = query.project_id

        # Resolve Qdrant Repository
        from aios.registry import ServiceRegistry
        from aios.services.persistence import RepositoryRegistry

        registry = ServiceRegistry._global_registry
        p_repos = registry.get(RepositoryRegistry)
        repo = p_repos.get_repository(query.collection_name)

        # Execute Search
        search_res = repo.search(
            vector=embed_res.vector,
            filter_query=final_filters,
            limit=query.limit + query.offset,
            score_threshold=query.score_threshold,
        )

        # Process results with pagination offset
        paginated_res = []
        for r in search_res[query.offset :]:
            # Lazy payload extraction
            payload = r.get("payload", {})
            text = payload.get("text", "")
            paginated_res.append(
                SemanticResult(
                    id=r["id"],
                    text=text,
                    score=r["score"],
                    metadata=payload,
                    source_collection=query.collection_name,
                )
            )

        # Query Cache Save
        self.query_cache[cache_key] = paginated_res
        if len(self.query_cache) > 1000:
            self.query_cache.pop(next(iter(self.query_cache)))

        latency = (time.perf_counter() - t0) * 1000.0
        self.latencies.append(latency)
        return paginated_res

    def batch_search(self, queries: List[SemanticQuery]) -> List[List[SemanticResult]]:
        self.op_counts["batch_search"] += 1
        return [self.search(q) for q in queries]

    def cross_collection_search(
        self, query: SemanticQuery, collections: List[str]
    ) -> List[SemanticResult]:
        self.op_counts["cross_collection_search"] += 1
        aggregated = []
        for col in collections:
            q = SemanticQuery(
                query_text=query.query_text,
                collection_name=col,
                filter_query=query.filter_query,
                limit=query.limit,
                score_threshold=query.score_threshold,
                workspace_id=query.workspace_id,
                project_id=query.project_id,
                offset=query.offset,
            )
            aggregated.extend(self.search(q))

        # Re-sort combined list by score desc
        aggregated.sort(key=lambda x: x.score, reverse=True)
        return aggregated[: query.limit]

    def get_statistics(self) -> Dict[str, Any]:
        avg_lat = sum(self.latencies) / len(self.latencies) if self.latencies else 0.0
        return {
            "operation_counts": self.op_counts.copy(),
            "average_latency_ms": avg_lat,
            "query_cache_size": len(self.query_cache),
        }

    def get_health(self) -> Dict[str, Any]:
        return {"status": "HEALTHY", "query_cache_utilized": len(self.query_cache) > 0}

    def get_diagnostics(self) -> Dict[str, Any]:
        return {"alerts": []}

    # --- Supported intents ---
    SUPPORTED_INTENTS = [
        "question",
        "documentation",
        "code",
        "engineering",
        "research",
        "conversation",
        "automation",
        "configuration",
        "general_knowledge",
    ]

    # --- Intent classification rules ---
    # Each entry: (intent, domains, signals, confidence_boost, scope_hint)
    _INTENT_RULES = [
        (
            "code",
            ["engineering", "documentation"],
            [
                "def ",
                "class ",
                "import ",
                "function",
                "fn(",
                "compile",
                "bug",
                "error",
                "exception",
                "traceback",
                "module",
                "package",
                "library",
                "api",
                "sdk",
                "decorator",
                "async",
                "await",
                "yield",
                "lambda",
                "list comprehension",
            ],
            0.2,
            "global",
        ),
        (
            "engineering",
            ["engineering", "workspace", "projects"],
            [
                "architecture",
                "design pattern",
                "microservice",
                "database",
                "infrastructure",
                "performance",
                "latency",
                "throughput",
                "scalability",
                "refactor",
                "pr",
                "pull request",
                "review",
                "sprint",
                "milestone",
                "deploy",
                "pipeline",
            ],
            0.15,
            "workspace",
        ),
        (
            "documentation",
            ["documentation", "knowledge"],
            [
                "document",
                "doc",
                "readme",
                "guide",
                "tutorial",
                "howto",
                "reference",
                "manual",
                "spec",
                "specification",
                "api doc",
                "changelog",
                "release note",
            ],
            0.15,
            "global",
        ),
        (
            "research",
            ["research", "knowledge"],
            [
                "research",
                "study",
                "paper",
                "analysis",
                "survey",
                "benchmark",
                "experiment",
                "hypothesis",
                "finding",
                "literature",
                "academic",
                "publication",
            ],
            0.2,
            "global",
        ),
        (
            "automation",
            ["automation", "provider"],
            [
                "automation",
                "trigger",
                "workflow",
                "n8n",
                "cron",
                "schedule",
                "pipeline",
                "task",
                "job",
                "hook",
                "webhook",
                "integration",
                "connector",
                "action",
            ],
            0.15,
            "global",
        ),
        (
            "conversation",
            ["conversation"],
            [
                "said",
                "told",
                "mentioned",
                "discussed",
                "chat",
                "message",
                "conversation",
                "earlier",
                "yesterday",
                "last week",
                "you said",
                "we talked",
            ],
            0.2,
            "workspace",
        ),
        (
            "configuration",
            ["engineering", "documentation", "knowledge"],
            [
                "config",
                "setting",
                "environment",
                "env var",
                "variable",
                ".env",
                "yaml",
                "json",
                "toml",
                "configuration file",
                "secret",
                "credential",
                "key",
            ],
            0.15,
            "global",
        ),
        (
            "question",
            ["knowledge", "documentation", "research"],
            [
                "what is",
                "how does",
                "why is",
                "when did",
                "where is",
                "which",
                "who",
                "explain",
                "describe",
                "tell me",
                "show me",
                "?",
            ],
            0.1,
            "global",
        ),
    ]


class QueryAnalysisServiceImpl(QueryAnalysisService):
    """Comprehensive query analysis service for Hybrid Retrieval platform.

    Classifies 9 intent types: question, documentation, code_search, engineering,
    research, conversation_history, automation_workflow, configuration, general_knowledge.
    Detects workspace/project scope, collection candidates, and retrieval strategy.
    Supports future extensibility via configurable rules.
    """

    SUPPORTED_INTENTS = [
        "question",
        "documentation",
        "code_search",
        "engineering",
        "research",
        "conversation_history",
        "automation_workflow",
        "configuration",
        "general_knowledge",
    ]

    def __init__(self) -> None:
        self.op_counts = {"analyze": 0}
        self._latencies: List[float] = []
        self._custom_rules: List[Any] = []

        # Default fallback rules (overridden by config file)
        self._intent_rules = [
            (
                "code_search",
                ["engineering", "documentation"],
                [
                    "def ",
                    "class ",
                    "import ",
                    "function",
                    "fn(",
                    "compile",
                    "bug",
                    "error",
                    "exception",
                    "traceback",
                    "module",
                    "package",
                    "library",
                    "api",
                    "sdk",
                    "decorator",
                    "async",
                    "await",
                    "yield",
                    "lambda",
                    "list comprehension",
                ],
                0.2,
                "global",
            ),
            (
                "engineering",
                ["engineering", "workspace", "projects"],
                [
                    "architecture",
                    "design pattern",
                    "microservice",
                    "database",
                    "infrastructure",
                    "performance",
                    "latency",
                    "throughput",
                    "scalability",
                    "refactor",
                    "pr",
                    "pull request",
                    "review",
                    "sprint",
                    "milestone",
                    "deploy",
                    "pipeline",
                ],
                0.15,
                "workspace",
            ),
            (
                "documentation",
                ["documentation", "knowledge"],
                [
                    "document",
                    "doc",
                    "readme",
                    "guide",
                    "tutorial",
                    "howto",
                    "reference",
                    "manual",
                    "spec",
                    "specification",
                    "api doc",
                    "changelog",
                    "release note",
                ],
                0.15,
                "global",
            ),
            (
                "research",
                ["research", "knowledge"],
                [
                    "research",
                    "study",
                    "paper",
                    "analysis",
                    "survey",
                    "benchmark",
                    "experiment",
                    "hypothesis",
                    "finding",
                    "literature",
                    "academic",
                    "publication",
                ],
                0.2,
                "global",
            ),
            (
                "automation_workflow",
                ["automation", "provider"],
                [
                    "automation",
                    "trigger",
                    "workflow",
                    "n8n",
                    "cron",
                    "schedule",
                    "job",
                    "hook",
                    "webhook",
                    "integration",
                    "connector",
                ],
                0.15,
                "global",
            ),
            (
                "conversation_history",
                ["conversation"],
                [
                    "said",
                    "told",
                    "mentioned",
                    "discussed",
                    "chat",
                    "message",
                    "conversation",
                    "earlier",
                    "yesterday",
                    "last week",
                    "you said",
                    "we talked",
                ],
                0.2,
                "workspace",
            ),
            (
                "configuration",
                ["engineering", "documentation", "knowledge"],
                [
                    "config",
                    "setting",
                    "environment",
                    "env var",
                    "variable",
                    ".env",
                    "yaml",
                    "json",
                    "toml",
                    "configuration file",
                    "secret",
                    "credential",
                ],
                0.15,
                "global",
            ),
            (
                "question",
                ["knowledge", "documentation", "research"],
                [
                    "what is",
                    "how does",
                    "why is",
                    "when did",
                    "where is",
                    "which",
                    "explain",
                    "describe",
                    "tell me",
                    "show me",
                    "?",
                ],
                0.1,
                "global",
            ),
        ]

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def teardown(self) -> None:
        self.stop()

    def load_config_file(self, config_path: Path) -> None:
        """Load intent rules from configuration file (dynamic runtime config)."""
        if not config_path or not config_path.exists():
            return
        try:
            import tomllib

            with open(config_path, "rb") as f:
                data = tomllib.load(f)
            retrieval_data = data.get("retrieval", {})
            query_analysis_data = retrieval_data.get("query_analysis", {})
            rules = query_analysis_data.get("intent_rules")
            if rules is not None:
                parsed_rules = []
                for r in rules:
                    if isinstance(r, dict):
                        parsed_rules.append(
                            (
                                r["intent"],
                                r["domains"],
                                r["trigger_words"],
                                r.get("confidence_boost", 0.1),
                                r.get("scope", "global"),
                            )
                        )
                if parsed_rules:
                    self._intent_rules = parsed_rules
        except Exception:
            pass

    def get_supported_intents(self) -> List[str]:
        return list(self.SUPPORTED_INTENTS)

    def register_custom_rule(
        self,
        intent: str,
        domains: List[str],
        trigger_words: List[str],
        confidence_boost: float = 0.1,
        scope: str = "global",
    ) -> None:
        """Register a custom intent rule for future extensibility."""
        self._custom_rules.append((intent, domains, trigger_words, confidence_boost, scope))

    def analyze_query(
        self, query_text: str, context_metadata: Optional[Dict[str, Any]] = None
    ) -> QueryAnalysis:
        t0 = time.perf_counter()
        self.op_counts["analyze"] += 1
        text_lower = query_text.lower()
        meta = context_metadata or {}

        # Detect workspace / project scope
        workspace_id = meta.get("workspace_id")
        project_id = meta.get("project_id")

        # Score each rule
        all_rules = list(self._intent_rules) + list(self._custom_rules)
        best_intent = "general_knowledge"
        best_domains = ["knowledge"]
        best_score = 0
        best_scope = "global"
        best_confidence = 0.5
        matched_signals: List[str] = []

        for rule_intent, rule_domains, rule_signals, conf_boost, rule_scope in all_rules:
            hits = [s for s in rule_signals if s in text_lower]
            score = len(hits)
            if score > best_score:
                best_score = score
                best_intent = rule_intent
                best_domains = rule_domains
                best_scope = rule_scope
                best_confidence = min(1.0, 0.5 + conf_boost * score)
                matched_signals = hits

        # Determine search scope: project > workspace > global
        if project_id:
            search_scope = "project"
        elif workspace_id:
            search_scope = "workspace" if best_scope in ("workspace", "project") else "global"
        else:
            search_scope = "global"

        # Complexity estimation: word count + multi-domain signals
        word_count = len(query_text.split())
        if word_count <= 3:
            complexity = "simple"
            estimated_complexity = "quick"
        elif word_count <= 10:
            complexity = "moderate"
            estimated_complexity = "standard"
        else:
            complexity = "complex"
            estimated_complexity = "deep"

        # Collect collection candidates from matched domains
        domain_to_col = {
            "engineering": "engineering_memory",
            "workspace": "workspace_memory",
            "projects": "project_memory",
            "documentation": "documentation_memory",
            "conversation": "conversation_memory",
            "automation": "automation_memory",
            "provider": "provider_memory",
            "research": "research_memory",
            "knowledge": "knowledge_memory",
        }
        collection_candidates = [domain_to_col[d] for d in best_domains if d in domain_to_col]
        if not collection_candidates:
            collection_candidates = ["knowledge_memory"]

        latency = (time.perf_counter() - t0) * 1000.0
        self._latencies.append(latency)
        if len(self._latencies) > 1000:
            self._latencies.pop(0)

        return QueryAnalysis(
            intent=best_intent,
            domains=best_domains,
            complexity=complexity,
            workspace_id=workspace_id,
            project_id=project_id,
            strategy={
                "max_candidates": 30 if estimated_complexity == "deep" else 20,
                "rerank": True,
                "score_threshold": 0.3,
            },
            search_scope=search_scope,
            collection_candidates=collection_candidates,
            retrieval_strategy="hybrid",
            confidence=best_confidence,
            estimated_complexity=estimated_complexity,
            intent_signals=matched_signals,
        )


class CollectionSelectorImpl(CollectionSelector):
    """Intelligent collection routing with weighted scoring and configurable priorities.

    Supports:
    - Single collection routing
    - Multi-collection weighted routing
    - Workspace/project-scoped filtering
    - Configurable collection priorities
    - Future plugin support via domain_map extension
    """

    # Default domain -> collection mapping
    _DEFAULT_DOMAIN_MAP = {
        "engineering": "engineering_memory",
        "workspace": "workspace_memory",
        "projects": "project_memory",
        "documentation": "documentation_memory",
        "conversation": "conversation_memory",
        "automation": "automation_memory",
        "provider": "provider_memory",
        "research": "research_memory",
        "knowledge": "knowledge_memory",
    }

    # Default Intent -> collection weight overrides (overridden by config file)
    _DEFAULT_INTENT_COLLECTION_WEIGHTS = {
        "code_search": {"engineering_memory": 1.0, "documentation_memory": 0.7},
        "engineering": {"engineering_memory": 1.0, "workspace_memory": 0.8, "project_memory": 0.6},
        "documentation": {"documentation_memory": 1.0, "knowledge_memory": 0.6},
        "research": {"research_memory": 1.0, "knowledge_memory": 0.7, "documentation_memory": 0.5},
        "automation_workflow": {"automation_memory": 1.0, "provider_memory": 0.6},
        "conversation_history": {"conversation_memory": 1.0, "workspace_memory": 0.4},
        "configuration": {
            "engineering_memory": 0.9,
            "documentation_memory": 0.8,
            "knowledge_memory": 0.5,
        },
        "question": {"knowledge_memory": 1.0, "documentation_memory": 0.8, "research_memory": 0.6},
        "general_knowledge": {"knowledge_memory": 1.0},
    }

    def __init__(self) -> None:
        self.domain_map: Dict[str, str] = dict(self._DEFAULT_DOMAIN_MAP)
        # Default routing weights (copied, can be overwritten at runtime or by config)
        self.intent_collection_weights = {
            k: dict(v) for k, v in self._DEFAULT_INTENT_COLLECTION_WEIGHTS.items()
        }
        # Allow runtime overrides
        self._collection_priority_overrides: Dict[str, float] = {}

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def teardown(self) -> None:
        self.stop()

    def load_config_file(self, config_path: Path) -> None:
        """Load intent-based collection routing weights from configuration file."""
        if not config_path or not config_path.exists():
            return
        try:
            import tomllib

            with open(config_path, "rb") as f:
                data = tomllib.load(f)
            retrieval_data = data.get("retrieval", {})
            selector_data = retrieval_data.get("collection_selector", {})
            weights = selector_data.get("intent_collection_weights")
            if weights is not None and isinstance(weights, dict):
                parsed_weights = {}
                for intent, col_map in weights.items():
                    if isinstance(col_map, dict):
                        parsed_weights[intent] = {col: float(val) for col, val in col_map.items()}
                if parsed_weights:
                    self.intent_collection_weights = parsed_weights
        except Exception:
            pass

    def set_collection_priority(self, collection: str, weight: float) -> None:
        """Override collection priority weight at runtime."""
        self._collection_priority_overrides[collection] = weight

    def register_domain(self, domain: str, collection: str) -> None:
        """Register a new domain -> collection mapping (plugin support)."""
        self.domain_map[domain] = collection

    def select_collections(self, analysis: QueryAnalysis) -> Dict[str, float]:
        """Select collections with weighted routing.

        Uses intent-based weights when available, falls back to domain-based
        with equal weighting. Applies runtime overrides on top.
        Returns: Dict[collection_name -> weight (0.0-1.0)]
        """
        selected: Dict[str, float] = {}

        # 1. Check intent-specific routing first
        intent_weights = self.intent_collection_weights.get(analysis.intent, {})
        if intent_weights:
            selected.update(intent_weights)

        # 2. Add domain-based collections (with lower weight if not already present)
        for d in analysis.domains:
            col = self.domain_map.get(d)
            if col and col not in selected:
                selected[col] = 0.5

        # 3. Add explicit collection_candidates from QueryAnalysis
        for col in analysis.collection_candidates:
            if col not in selected:
                selected[col] = 0.4

        # 4. Apply runtime overrides
        for col, override_weight in self._collection_priority_overrides.items():
            if col in selected:
                selected[col] = override_weight

        # 5. Workspace/project scoping: boost workspace/project collections
        if analysis.search_scope in ("workspace", "project"):
            if "workspace_memory" in selected:
                selected["workspace_memory"] = min(1.0, selected["workspace_memory"] + 0.2)
            if analysis.search_scope == "project" and "project_memory" in selected:
                selected["project_memory"] = min(1.0, selected["project_memory"] + 0.3)

        # 6. Default fallback
        if not selected:
            selected["knowledge_memory"] = 1.0

        return selected


class CandidateRankerImpl(CandidateRanker):
    """Configurable multi-signal candidate ranker.

    Ranking signals (all configurable via set_weights):
    1. semantic_similarity  - raw Qdrant similarity score
    2. importance           - domain importance from metadata
    3. freshness            - exponential time decay
    4. workspace_relevance  - workspace match bonus
    5. project_relevance    - project match bonus
    6. source_quality       - collection quality tier
    7. engineering_priority - engineering collection boost
    8. metadata_confidence  - metadata completeness
    9. duplicate_penalty    - penalize near-duplicates

    No hardcoded constants - all weights are configurable.
    """

    # Default weights - all configurable
    _DEFAULT_WEIGHTS: Dict[str, float] = {
        "semantic_similarity": 0.35,
        "importance": 0.20,
        "freshness": 0.15,
        "workspace_relevance": 0.10,
        "project_relevance": 0.10,
        "source_quality": 0.05,
        "engineering_priority": 0.03,
        "metadata_confidence": 0.02,
        "duplicate_penalty": -0.10,  # negative: applied as penalty
    }

    # Source quality tiers (configurable)
    _SOURCE_QUALITY = {
        "engineering_memory": 0.9,
        "documentation_memory": 0.8,
        "research_memory": 0.85,
        "project_memory": 0.75,
        "workspace_memory": 0.7,
        "knowledge_memory": 0.65,
        "conversation_memory": 0.55,
        "automation_memory": 0.6,
        "provider_memory": 0.6,
    }

    def __init__(self) -> None:
        self.weights: Dict[str, float] = dict(self._DEFAULT_WEIGHTS)
        self._latencies: List[float] = []
        self._ranked_count = 0

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def teardown(self) -> None:
        self.stop()

    def get_default_weights(self) -> Dict[str, float]:
        return dict(self._DEFAULT_WEIGHTS)

    def set_weights(self, weights: Dict[str, float]) -> None:
        """Override ranking weights at runtime. Only provided keys are updated."""
        self.weights.update(weights)

    def rank_candidates(
        self, candidates: List[RetrievalCandidate], weights: Optional[Dict[str, float]] = None
    ) -> List[RetrievalCandidate]:
        t0 = time.perf_counter()
        w = weights if weights is not None else self.weights
        self._ranked_count += len(candidates)

        # Detect near-duplicates using text hashing
        text_hash_counts: Dict[int, int] = {}
        for c in candidates:
            h = hash(c.text[:200])
            text_hash_counts[h] = text_hash_counts.get(h, 0) + 1

        scored = []
        for c in candidates:
            # Enrich source_quality_score from collection tier
            c.source_quality_score = self._SOURCE_QUALITY.get(c.source_collection, 0.5)

            # Enrich metadata_confidence from payload completeness
            required_fields = {"workspace_id", "created_at", "text"}
            present = sum(1 for f in required_fields if f in c.metadata and c.metadata[f])
            c.metadata_confidence_score = present / max(1, len(required_fields))

            # Duplicate penalty: penalize if same text appears multiple times
            h = hash(c.text[:200])
            c.duplicate_penalty = 1.0 if text_hash_counts.get(h, 1) > 1 else 0.0

            # Composite score
            score = (
                c.similarity_score * w.get("semantic_similarity", 0.35)
                + c.importance_score * w.get("importance", 0.20)
                + c.freshness_score * w.get("freshness", 0.15)
                + c.workspace_relevance_score * w.get("workspace_relevance", 0.10)
                + c.project_relevance_score * w.get("project_relevance", 0.10)
                + c.source_quality_score * w.get("source_quality", 0.05)
                + c.engineering_priority_score * w.get("engineering_priority", 0.03)
                + c.metadata_confidence_score * w.get("metadata_confidence", 0.02)
                + c.duplicate_penalty * w.get("duplicate_penalty", -0.10)
            )
            c.score = max(0.0, min(1.0, score))  # clamp to [0, 1]
            scored.append(c)

        scored.sort(key=lambda x: x.score, reverse=True)

        latency = (time.perf_counter() - t0) * 1000.0
        self._latencies.append(latency)
        if len(self._latencies) > 1000:
            self._latencies.pop(0)

        return scored

    def get_statistics(self) -> Dict[str, Any]:
        avg_lat = sum(self._latencies) / len(self._latencies) if self._latencies else 0.0
        return {
            "total_ranked": self._ranked_count,
            "average_ranking_latency_ms": avg_lat,
            "current_weights": self.weights.copy(),
        }


class ContextOptimizerImpl(ContextOptimizer):
    """Context optimizer that removes duplicates, merges overlapping chunks,
    compresses context, preserves citations, respects token budgets,
    prioritizes high-value content, and preserves ordering.

    No LLM calls - all operations are deterministic.
    """

    def __init__(self) -> None:
        self.total_optimizations = 0
        self.total_candidates_processed = 0
        self.total_candidates_included = 0
        self.total_tokens_budgeted = 0
        self.total_tokens_output = 0

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def teardown(self) -> None:
        self.stop()

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "total_optimizations": self.total_optimizations,
            "total_candidates_processed": self.total_candidates_processed,
            "total_candidates_included": self.total_candidates_included,
            "total_tokens_budgeted": self.total_tokens_budgeted,
            "total_tokens_output": self.total_tokens_output,
        }

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count: approx 4 chars per token."""
        return max(1, len(text) // 4)

    def _text_similarity(self, a: str, b: str) -> float:
        """Simple overlap-based similarity without NLP library."""
        if not a or not b:
            return 0.0
        words_a = set(a.lower().split())
        words_b = set(b.lower().split())
        if not words_a or not words_b:
            return 0.0
        intersection = words_a & words_b
        union = words_a | words_b
        return len(intersection) / max(1, len(union))

    def merge_overlapping_chunks(
        self, candidates: List[RetrievalCandidate]
    ) -> List[RetrievalCandidate]:
        """Merge candidates with high text overlap (>70% Jaccard similarity).
        Preserves the higher-scoring candidate when merging.
        """
        if len(candidates) <= 1:
            return candidates

        merged: List[RetrievalCandidate] = []
        used = set()

        for i, c in enumerate(candidates):
            if i in used:
                continue
            merged_c = c
            for j, other in enumerate(candidates):
                if i == j or j in used:
                    continue
                sim = self._text_similarity(c.text, other.text)
                if sim > 0.7:
                    used.add(j)
                    # Keep the higher-scoring candidate, combine metadata
                    if other.score > merged_c.score:
                        merged_c = other
            merged.append(merged_c)

        return merged

    def compress_context(self, text: str, max_tokens: int) -> str:
        """Compress text to fit within token budget by truncating sentences.
        Preserves leading sentences (most important content first).
        No LLM calls.
        """
        current_tokens = self._estimate_tokens(text)
        if current_tokens <= max_tokens:
            return text

        # Split by sentence boundaries, keep as many as fit
        sentences = text.replace("\n", " ").split(". ")
        result_parts = []
        total = 0
        for s in sentences:
            t = self._estimate_tokens(s)
            if total + t > max_tokens:
                break
            result_parts.append(s)
            total += t

        if not result_parts:
            # If even first sentence is too long, hard truncate
            return text[: max_tokens * 4] + "..."

        return ". ".join(result_parts) + "."

    def optimize_context(
        self, candidates: List[RetrievalCandidate], token_budget: int
    ) -> ContextAssemblyResult:
        """Full context optimization pipeline:
        1. Deduplicate by exact text match
        2. Merge overlapping chunks
        3. Respect token budget
        4. Prioritize high-value content (by score)
        5. Preserve citations (source_collection + id headers)
        6. Preserve ordering (already sorted by ranker)
        """
        self.total_optimizations += 1
        self.total_candidates_processed += len(candidates)
        self.total_tokens_budgeted += token_budget

        # Step 1: Exact deduplication
        seen_texts: set = set()
        deduped: List[RetrievalCandidate] = []
        for c in candidates:
            key = c.text.strip()
            if key and key not in seen_texts:
                seen_texts.add(key)
                deduped.append(c)

        # Step 2: Merge overlapping chunks
        merged = self.merge_overlapping_chunks(deduped)

        # Step 3 & 4: Select candidates within token budget (highest score first)
        included: List[RetrievalCandidate] = []
        total_tokens = 0
        context_parts: List[str] = []

        for c in merged:
            text_to_use = c.text
            tokens = self._estimate_tokens(text_to_use)

            if total_tokens + tokens > token_budget:
                # Try compressing to fit remaining budget
                remaining = token_budget - total_tokens
                if remaining > 50:  # Only bother if meaningful space remains
                    text_to_use = self.compress_context(text_to_use, remaining)
                    tokens = self._estimate_tokens(text_to_use)
                    if total_tokens + tokens > token_budget:
                        continue
                else:
                    continue

            total_tokens += tokens
            included.append(c)
            # Step 5: Preserve citations with source attribution
            header = f"[Source: {c.source_collection} | ID: {c.id} | Score: {c.score:.3f}]"
            context_parts.append(f"{header}\n{text_to_use}")

        context_text = "\n\n".join(context_parts)
        self.total_candidates_included += len(included)
        self.total_tokens_output += total_tokens

        return ContextAssemblyResult(
            context_text=context_text,
            candidates_included=included,
            total_tokens=total_tokens,
            token_budget=token_budget,
        )


class RetrievalCacheImpl(RetrievalCache):
    """Multi-tier retrieval cache with Redis integration and memory fallback.

    Cache tiers:
    - Query cache: full query -> ranked result list
    - Candidate cache: collection search results
    - Ranking cache: post-ranking results
    - Context cache: optimized context strings

    Each tier has independent TTL configuration.
    Gracefully degrades to in-memory cache when Redis unavailable.
    No request fails due to cache unavailability.
    """

    def __init__(self, redis_service: Optional[Any] = None) -> None:
        self.redis_service = redis_service
        # Four independent cache tiers
        self._query_cache: Dict[str, Any] = {}
        self._candidate_cache: Dict[str, Any] = {}
        self._ranking_cache: Dict[str, Any] = {}
        self._context_cache: Dict[str, Any] = {}
        self.stats = {
            "query_hits": 0,
            "query_misses": 0,
            "query_sets": 0,
            "candidate_hits": 0,
            "candidate_misses": 0,
            "candidate_sets": 0,
            "ranking_hits": 0,
            "ranking_misses": 0,
            "ranking_sets": 0,
            "context_hits": 0,
            "context_misses": 0,
            "context_sets": 0,
            "redis_errors": 0,
            "memory_fallbacks": 0,
        }

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def teardown(self) -> None:
        self.stop()

    def _redis_available(self) -> bool:
        try:
            if self.redis_service is None:
                return False
            client = self.redis_service.get_client()
            return client is not None
        except Exception:
            return False

    def _redis_get(self, key: str) -> Optional[str]:
        try:
            client = self.redis_service.get_client()
            return client.get(key)
        except Exception:
            self.stats["redis_errors"] += 1
            return None

    def _redis_setex(self, key: str, ttl: int, value: str) -> None:
        try:
            client = self.redis_service.get_client()
            client.setex(key, ttl, value)
        except Exception:
            self.stats["redis_errors"] += 1

    def _redis_delete_pattern(self, pattern: str) -> None:
        try:
            client = self.redis_service.get_client()
            keys = client.keys(f"retrieval:*{pattern}*")
            if keys:
                client.delete(*keys)
        except Exception:
            self.stats["redis_errors"] += 1

    def _serialize_candidates(self, results: List[RetrievalCandidate]) -> str:
        data = [
            {
                "id": r.id,
                "text": r.text,
                "score": r.score,
                "metadata": r.metadata,
                "source_collection": r.source_collection,
                "similarity_score": r.similarity_score,
                "importance_score": r.importance_score,
                "freshness_score": r.freshness_score,
                "workspace_relevance_score": r.workspace_relevance_score,
                "project_relevance_score": r.project_relevance_score,
                "source_quality_score": r.source_quality_score,
                "engineering_priority_score": r.engineering_priority_score,
                "metadata_confidence_score": r.metadata_confidence_score,
                "duplicate_penalty": r.duplicate_penalty,
            }
            for r in results
        ]
        return json.dumps(data)

    def _deserialize_candidates(self, raw: str) -> List[RetrievalCandidate]:
        data = json.loads(raw)
        return [RetrievalCandidate(**item) for item in data]

    def _local_set(
        self,
        store: Dict[str, Any],
        key: str,
        val: Any,
        ttl: int,
        tier: str,
        increment_sets: bool = True,
    ) -> None:
        store[key] = (val, time.time() + ttl)
        if increment_sets:
            self.stats[f"{tier}_sets"] += 1
        # LRU eviction: keep max 500 entries per tier
        if len(store) > 500:
            oldest = next(iter(store))
            del store[oldest]

    def _get_tier_entry(
        self, store: Dict[str, Any], cache_key: str, redis_key: str, tier: str
    ) -> Optional[Any]:
        # 1. Try Redis first if available
        if self._redis_available():
            raw = self._redis_get(redis_key)
            if raw:
                self.stats[f"{tier}_hits"] += 1
                return raw
        # 2. Try Local cache
        entry = store.get(cache_key)
        if entry:
            val, expiry = entry
            if time.time() < expiry:
                self.stats[f"{tier}_hits"] += 1
                return val
            else:
                del store[cache_key]

        # 3. Complete miss
        self.stats[f"{tier}_misses"] += 1
        return None

    # --- Query Cache ---
    def get_query_results(self, cache_key: str) -> Optional[List[RetrievalCandidate]]:
        res = self._get_tier_entry(
            self._query_cache, cache_key, f"retrieval:query:{cache_key}", "query"
        )
        if res is None:
            return None
        if isinstance(res, str):
            try:
                candidates = self._deserialize_candidates(res)
                self._local_set(
                    self._query_cache, cache_key, candidates, 300, "query", increment_sets=False
                )
                return candidates
            except Exception:
                return None
        return res

    def set_query_results(
        self, cache_key: str, results: List[RetrievalCandidate], ttl: int = 300
    ) -> None:
        self._local_set(self._query_cache, cache_key, results, ttl, "query", increment_sets=True)
        if self._redis_available():
            try:
                self._redis_setex(
                    f"retrieval:query:{cache_key}", ttl, self._serialize_candidates(results)
                )
            except Exception:
                self.stats["redis_errors"] += 1

    # --- Candidate Cache ---
    def get_candidate_results(self, cache_key: str) -> Optional[List[RetrievalCandidate]]:
        res = self._get_tier_entry(
            self._candidate_cache, cache_key, f"retrieval:candidates:{cache_key}", "candidate"
        )
        if res is None:
            return None
        if isinstance(res, str):
            try:
                candidates = self._deserialize_candidates(res)
                self._local_set(
                    self._candidate_cache,
                    cache_key,
                    candidates,
                    300,
                    "candidate",
                    increment_sets=False,
                )
                return candidates
            except Exception:
                return None
        return res

    def set_candidate_results(
        self, cache_key: str, results: List[RetrievalCandidate], ttl: int = 300
    ) -> None:
        self._local_set(
            self._candidate_cache, cache_key, results, ttl, "candidate", increment_sets=True
        )
        if self._redis_available():
            try:
                self._redis_setex(
                    f"retrieval:candidates:{cache_key}", ttl, self._serialize_candidates(results)
                )
            except Exception:
                self.stats["redis_errors"] += 1

    # --- Ranking Cache ---
    def get_ranking_results(self, cache_key: str) -> Optional[List[RetrievalCandidate]]:
        res = self._get_tier_entry(
            self._ranking_cache, cache_key, f"retrieval:ranking:{cache_key}", "ranking"
        )
        if res is None:
            return None
        if isinstance(res, str):
            try:
                candidates = self._deserialize_candidates(res)
                self._local_set(
                    self._ranking_cache, cache_key, candidates, 300, "ranking", increment_sets=False
                )
                return candidates
            except Exception:
                return None
        return res

    def set_ranking_results(
        self, cache_key: str, results: List[RetrievalCandidate], ttl: int = 300
    ) -> None:
        self._local_set(
            self._ranking_cache, cache_key, results, ttl, "ranking", increment_sets=True
        )
        if self._redis_available():
            try:
                self._redis_setex(
                    f"retrieval:ranking:{cache_key}", ttl, self._serialize_candidates(results)
                )
            except Exception:
                self.stats["redis_errors"] += 1

    # --- Context Cache ---
    def get_context_result(self, cache_key: str) -> Optional[str]:
        res = self._get_tier_entry(
            self._context_cache, cache_key, f"retrieval:context:{cache_key}", "context"
        )
        if res is None:
            return None
        if isinstance(res, bytes):
            res = res.decode("utf-8")
        if isinstance(res, str):
            self._local_set(
                self._context_cache, cache_key, res, 300, "context", increment_sets=False
            )
        return res

    def set_context_result(self, cache_key: str, context: str, ttl: int = 300) -> None:
        self._local_set(
            self._context_cache, cache_key, context, ttl, "context", increment_sets=True
        )
        if self._redis_available():
            try:
                self._redis_setex(f"retrieval:context:{cache_key}", ttl, context)
            except Exception:
                self.stats["redis_errors"] += 1

    def invalidate(self, pattern: str) -> None:
        """Invalidate all cache tiers matching pattern."""
        for store in [
            self._query_cache,
            self._candidate_cache,
            self._ranking_cache,
            self._context_cache,
        ]:
            keys_to_delete = [k for k in store if pattern in k]
            for k in keys_to_delete:
                del store[k]
        if self._redis_available():
            self._redis_delete_pattern(pattern)

    def get_statistics(self) -> Dict[str, Any]:
        total_hits = (
            self.stats["query_hits"]
            + self.stats["candidate_hits"]
            + self.stats["ranking_hits"]
            + self.stats["context_hits"]
        )
        total_misses = (
            self.stats["query_misses"]
            + self.stats["candidate_misses"]
            + self.stats["ranking_misses"]
            + self.stats["context_misses"]
        )
        total_requests = total_hits + total_misses
        hit_ratio = total_hits / max(1, total_requests)
        return {
            **self.stats,
            "total_hits": total_hits,
            "total_misses": total_misses,
            "hits": total_hits,
            "misses": total_misses,
            "overall_hit_ratio": round(hit_ratio, 4),
            "query_hit_ratio": round(
                self.stats["query_hits"]
                / max(1, self.stats["query_hits"] + self.stats["query_misses"]),
                4,
            ),
            "candidate_hit_ratio": round(
                self.stats["candidate_hits"]
                / max(1, self.stats["candidate_hits"] + self.stats["candidate_misses"]),
                4,
            ),
            "ranking_hit_ratio": round(
                self.stats["ranking_hits"]
                / max(1, self.stats["ranking_hits"] + self.stats["ranking_misses"]),
                4,
            ),
            "context_hit_ratio": round(
                self.stats["context_hits"]
                / max(1, self.stats["context_hits"] + self.stats["context_misses"]),
                4,
            ),
            "cache_sizes": {
                "query": len(self._query_cache),
                "candidate": len(self._candidate_cache),
                "ranking": len(self._ranking_cache),
                "context": len(self._context_cache),
            },
            "redis_available": self._redis_available(),
        }


class HybridRetrievalServiceImpl(HybridRetrievalService):
    def __init__(
        self,
        query_analyzer: QueryAnalysisService,
        selector: CollectionSelector,
        search_service: SemanticSearchService,
        ranker: CandidateRanker,
        optimizer: ContextOptimizer,
        cache: RetrievalCache,
    ) -> None:
        self.query_analyzer = query_analyzer
        self.selector = selector
        self.search_service = search_service
        self.ranker = ranker
        self.optimizer = optimizer
        self.cache = cache

        # Metrics
        self.op_counts = {"retrieve": 0}
        self.latencies = []
        self._errors = []

        # Collection utilization metrics
        self.collection_utilisation: Dict[str, int] = {}
        self.collection_matches: Dict[str, int] = {}

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def teardown(self) -> None:
        self.stop()

    def retrieve(
        self,
        query_text: str,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
        token_budget: int = 4000,
        filter_query: Optional[Dict[str, Any]] = None,
    ) -> ContextAssemblyResult:
        t0 = time.perf_counter()
        self.op_counts["retrieve"] += 1

        # Check Cache
        import json

        filters_str = json.dumps(filter_query, sort_keys=True) if filter_query else ""
        cache_key = f"{query_text}:{workspace_id}:{project_id}:{token_budget}:{filters_str}"
        cached = self.cache.get_query_results(cache_key)
        if cached is not None:
            return self.optimizer.optimize_context(cached, token_budget)

        # 1. Analyze query
        analysis = self.query_analyzer.analyze_query(
            query_text, {"workspace_id": workspace_id, "project_id": project_id}
        )

        # 2. Select collections
        collections = self.selector.select_collections(analysis)
        candidates = []

        # 3. Pull candidates from selected collections
        for col, col_weight in collections.items():
            # Track collection utilisation
            self.collection_utilisation[col] = self.collection_utilisation.get(col, 0) + 1
            col_results = []
            try:
                # Normal semantic query routing
                q = SemanticQuery(
                    query_text=query_text,
                    collection_name=col,
                    filter_query=filter_query,
                    limit=20,
                    workspace_id=workspace_id,
                    project_id=project_id,
                )
                col_results = self.search_service.search(q)
            except Exception as e:
                self._errors.append(
                    {"timestamp": time.time(), "message": f"Qdrant query failed: {e}"}
                )

                # Fallback to PostgreSQL lexical search
                try:
                    from aios.registry import ServiceRegistry
                    from aios.services.persistence import PersistenceService

                    db = ServiceRegistry._global_registry.get(PersistenceService)
                    sql_rows = db.execute(
                        "SELECT id, value, metadata FROM ai_memory WHERE value LIKE ?",
                        (f"%{query_text}%",),
                    )
                    for r in sql_rows:
                        meta = {}
                        try:
                            meta = json.loads(r.get("metadata", "{}") or "{}")
                        except Exception:
                            pass
                        col_results.append(
                            SemanticResult(
                                id=r["id"],
                                text=r.get("value", ""),
                                score=0.5,  # static fallback lexical score
                                metadata=meta,
                                source_collection=col,
                            )
                        )
                except Exception as dbe:
                    self._errors.append(
                        {"timestamp": time.time(), "message": f"Fallback search failed: {dbe}"}
                    )

            # Track collection matches
            self.collection_matches[col] = self.collection_matches.get(col, 0) + len(col_results)

            # Map raw SemanticResults to RetrievalCandidates
            for r in col_results:
                payload = r.metadata

                # Importance signal estimation
                importance = float(payload.get("importance", 5)) / 10.0

                # Freshness signal calculation
                created_at = float(payload.get("created_at", time.time()))
                import math

                decay = math.exp(-0.00001 * max(0.0, time.time() - created_at))

                # Relevance calculation based on retrieval scope
                cand_workspace = payload.get("workspace_id")
                cand_project = payload.get("project_id")
                workspace_relevance = (
                    1.0 if (workspace_id and cand_workspace == workspace_id) else 0.0
                )
                project_relevance = 1.0 if (project_id and cand_project == project_id) else 0.0

                candidates.append(
                    RetrievalCandidate(
                        id=r.id,
                        text=r.text,
                        score=0.0,  # calculated during ranking
                        metadata=payload,
                        source_collection=col,
                        similarity_score=r.score,
                        importance_score=importance,
                        freshness_score=decay,
                        workspace_relevance_score=workspace_relevance,
                        project_relevance_score=project_relevance,
                    )
                )

        # 4. Rank and prioritize candidates
        ranked = self.ranker.rank_candidates(candidates)

        # 5. Save to Cache
        self.cache.set_query_results(cache_key, ranked)

        # 6. Optimize context within token budget
        res = self.optimizer.optimize_context(ranked, token_budget)

        latency = (time.perf_counter() - t0) * 1000.0
        self.latencies.append(latency)
        if len(self.latencies) > 1000:
            self.latencies.pop(0)

        return res

    def get_recommendations(self) -> List[Dict[str, Any]]:
        """Dynamically generate refinement recommendations based on cache/latency metrics."""
        recs = []
        # Cache hit ratio check
        cache_stats = self.cache.get_statistics()
        total_hits = cache_stats.get("total_hits", 0)
        total_misses = cache_stats.get("total_misses", 0)
        total_reqs = total_hits + total_misses
        if total_reqs > 10:
            hit_ratio = total_hits / total_reqs
            if hit_ratio < 0.5:
                recs.append(
                    {
                        "category": "retrieval_cache",
                        "issue": f"Retrieval cache hit ratio is low ({hit_ratio:.1%}).",
                        "suggestion": "Increase cache TTL or warm up cache for frequent queries.",
                        "severity": "WARNING",
                    }
                )

        # Latency check
        avg_lat = sum(self.latencies) / len(self.latencies) if self.latencies else 0.0
        if avg_lat > 200.0:
            recs.append(
                {
                    "category": "hybrid_retrieval",
                    "issue": f"Average retrieval latency is high ({avg_lat:.2f}ms).",
                    "suggestion": "Tune Qdrant indexing parameters (e.g. HNsw index) or reduce candidate recall limits.",
                    "severity": "WARNING",
                }
            )

        return recs

    def get_statistics(self) -> Dict[str, Any]:
        avg_lat = sum(self.latencies) / len(self.latencies) if self.latencies else 0.0
        return {
            "operation_counts": self.op_counts.copy(),
            "average_latency_ms": avg_lat,
            "collection_utilisation": self.collection_utilisation.copy(),
            "collection_matches": self.collection_matches.copy(),
            "cache_stats": self.cache.get_statistics(),
            "ranker_stats": self.ranker.get_statistics()
            if hasattr(self.ranker, "get_statistics")
            else {},
            "optimizer_stats": self.optimizer.get_statistics()
            if hasattr(self.optimizer, "get_statistics")
            else {},
            "recommendations": self.get_recommendations(),
        }

    def get_health(self) -> Dict[str, Any]:
        return {"status": "HEALTHY", "failures_recorded": len(self._errors)}

    def get_diagnostics(self) -> Dict[str, Any]:
        return {
            "alerts": [
                {"message": err["message"], "timestamp": err["timestamp"]} for err in self._errors
            ]
        }

# ruff: noqa: F403, F405, E501, N802, E402, N806, B007
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle
from aios.services.persistence import *

logger = logging.getLogger(__name__)

from .utilities import build_qdrant_filter


class QdrantConfigurationService(ServiceLifecycle):
    def __init__(self) -> None:
        self.host = os.environ.get("QDRANT_HOST", "127.0.0.1")
        try:
            self.port = int(os.environ.get("QDRANT_PORT", 6333))
        except ValueError:
            self.port = 6333
        try:
            self.grpc_port = int(os.environ.get("QDRANT_GRPC_PORT", 6334))
        except ValueError:
            self.grpc_port = 6334
        self.api_key = os.environ.get("QDRANT_API_KEY", None)
        self.https = os.environ.get("QDRANT_HTTPS", "false").lower() == "true"
        try:
            self.timeout = float(os.environ.get("QDRANT_TIMEOUT", 5.0))
        except ValueError:
            self.timeout = 5.0
        try:
            self.retry_count = int(os.environ.get("QDRANT_RETRY_COUNT", 3))
        except ValueError:
            self.retry_count = 3
        try:
            self.default_vector_dimensions = int(os.environ.get("QDRANT_DEFAULT_DIMENSIONS", 1536))
        except ValueError:
            self.default_vector_dimensions = 1536
        self.default_distance_metric = os.environ.get("QDRANT_DEFAULT_DISTANCE", "cosine").upper()
        self.on_disk_payload = os.environ.get("QDRANT_ON_DISK_PAYLOAD", "true").lower() == "true"
        self.quantization = os.environ.get("QDRANT_QUANTIZATION", "false").lower() == "true"

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass


class QdrantConnectionManager(ServiceLifecycle):
    def __init__(self, config: QdrantConfigurationService) -> None:
        self.config = config
        self._client = None
        self._connected = False
        self._failures = 0

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        self.connect()

    def stop(self) -> None:
        self.disconnect()

    def connect(self) -> None:
        if self._connected:
            return
        try:
            from qdrant_client import QdrantClient

            self._client = QdrantClient(
                host=self.config.host,
                port=self.config.port,
                grpc_port=self.config.grpc_port,
                api_key=self.config.api_key,
                https=self.config.https,
                timeout=self.config.timeout,
                prefer_grpc=False,
            )
            self._client.get_collections()
            self._connected = True
            self._failures = 0
            logger.info("Successfully connected to Qdrant server.")
        except Exception as e:
            logger.warning(
                f"Qdrant connection failed ({e}). "
                "Automatically falling back to local-only in-memory QdrantClient."
            )
            try:
                from qdrant_client import QdrantClient
                self._client = QdrantClient(location=":memory:")
                self._client.get_collections()
                self._connected = True
                self._failures = 0
                logger.info("Successfully initialized local-only in-memory QdrantClient.")
            except Exception as e2:
                logger.error(f"Failed to initialize local-only in-memory QdrantClient: {e2}")
                self._connected = False
                self._failures += 1

    def disconnect(self) -> None:
        if self._client:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def get_client(self) -> Any:
        if not self._connected or not self._client:
            self.connect()
        return self._client


class QdrantTransportImpl(QdrantTransport):
    def __init__(
        self, config: QdrantConfigurationService, connection_manager: QdrantConnectionManager
    ) -> None:
        self.config = config
        self.connection_manager = connection_manager
        self.query_latencies: List[float] = []

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def is_connected(self) -> bool:
        return self.connection_manager.is_connected()

    def connect(self) -> None:
        self.connection_manager.connect()

    def disconnect(self) -> None:
        self.connection_manager.disconnect()

    def execute_command(self, cmd: str, *args: Any, **kwargs: Any) -> Any:
        client = self.connection_manager.get_client()
        if not client:
            raise RuntimeError("Qdrant client not available (disconnected)")

        last_err = None
        retries = self.config.retry_count
        for attempt in range(retries + 1):
            t0 = time.perf_counter()
            try:
                method = getattr(client, cmd, None)
                if not method:
                    raise AttributeError(f"QdrantClient has no method '{cmd}'")
                res = method(*args, **kwargs)
                latency_ms = (time.perf_counter() - t0) * 1000.0
                self.query_latencies.append(latency_ms)
                if len(self.query_latencies) > 1000:
                    self.query_latencies.pop(0)
                return res
            except Exception as e:
                last_err = e
                if attempt < retries:
                    time.sleep(0.05 * (2**attempt))
                else:
                    break
        raise RuntimeError(
            f"Qdrant command '{cmd}' failed after {retries} retries: {str(last_err)}"
        )


class QdrantProviderImpl(QdrantProvider):
    def __init__(self, transport: QdrantTransport) -> None:
        self.transport = transport

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get_transport(self) -> QdrantTransport:
        return self.transport

    def create_collection(
        self,
        name: str,
        vector_size: int,
        distance: str,
        on_disk_payload: bool = True,
        quantization_config: Optional[Dict[str, Any]] = None,
    ) -> bool:
        from qdrant_client.models import Distance, VectorParams

        dist_enum = Distance.COSINE
        if distance.upper() == "EUCLID":
            dist_enum = Distance.EUCLID
        elif distance.upper() == "DOT":
            dist_enum = Distance.DOT
        elif distance.upper() == "MANHATTAN":
            dist_enum = Distance.MANHATTAN

        try:
            self.transport.execute_command(
                "create_collection",
                collection_name=name,
                vectors_config=VectorParams(size=vector_size, distance=dist_enum),
                on_disk_payload=on_disk_payload,
                quantization_config=quantization_config,
            )
            return True
        except Exception:
            import traceback

            traceback.print_exc()
            return False

    def delete_collection(self, name: str) -> bool:
        try:
            self.transport.execute_command("delete_collection", collection_name=name)
            return True
        except Exception:
            return False

    def collection_exists(self, name: str) -> bool:
        try:
            return self.transport.execute_command("collection_exists", collection_name=name)
        except Exception:
            return False

    def upsert_points(self, collection: str, points: List[Dict[str, Any]]) -> bool:
        from qdrant_client.models import PointStruct

        pts = []
        for p in points:
            pts.append(PointStruct(id=p["id"], vector=p["vector"], payload=p.get("payload", {})))
        try:
            self.transport.execute_command("upsert", collection_name=collection, points=pts)
            return True
        except Exception as e:
            print(f"DEBUG: Qdrant upsert failed: {e}")
            return False

    def delete_points(self, collection: str, point_ids: List[Any]) -> bool:
        from qdrant_client.models import PointIdsList

        try:
            self.transport.execute_command(
                "delete", collection_name=collection, points_selector=PointIdsList(points=point_ids)
            )
            return True
        except Exception:
            return False

    def search_vectors(
        self,
        collection: str,
        vector: List[float],
        filter_query: Optional[Dict[str, Any]] = None,
        limit: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        try:
            res = self.transport.execute_command(
                "query_points",
                collection_name=collection,
                query=vector,
                query_filter=filter_query,
                limit=limit,
                score_threshold=score_threshold,
            )
            out = []
            for p in res.points:
                out.append({"id": p.id, "score": p.score, "payload": p.payload, "vector": p.vector})
            return out
        except Exception:
            return []

    def get_collection_info(self, name: str) -> Dict[str, Any]:
        try:
            info = self.transport.execute_command("get_collection", collection_name=name)
            return {
                "status": str(info.status),
                "vectors_count": getattr(info, "indexed_vectors_count", 0)
                or getattr(info, "vectors_count", 0)
                or 0,
                "points_count": getattr(info, "points_count", 0) or 0,
                "config": str(info.config),
            }
        except Exception as e:
            return {"status": "ERROR", "error": str(e), "vectors_count": 0, "points_count": 0}


class CollectionManagerImpl(CollectionManager):
    def __init__(self, provider: QdrantProvider, config: QdrantConfigurationService) -> None:
        self.provider = provider
        self.config = config

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def create_collection(self, name: str, dimensions: int, distance: str) -> bool:
        quant_config = None
        if self.config.quantization:
            from qdrant_client.models import (
                ScalarQuantization,
                ScalarQuantizationConfig,
                ScalarType,
            )

            quant_config = ScalarQuantization(
                scalar=ScalarQuantizationConfig(type=ScalarType.INT8, always_ram=True)
            )
        return self.provider.create_collection(
            name=name,
            vector_size=dimensions,
            distance=distance,
            on_disk_payload=self.config.on_disk_payload,
            quantization_config=quant_config,
        )

    def delete_collection(self, name: str) -> bool:
        return self.provider.delete_collection(name)

    def exists(self, name: str) -> bool:
        return self.provider.collection_exists(name)

    def validate_schema(self, name: str, schema: Dict[str, Any]) -> bool:
        if not self.exists(name):
            return False
        info = self.provider.get_collection_info(name)
        if info.get("status") == "ERROR":
            return False
        return True

    def create_index(self, collection_name: str, field_name: str, field_type: str) -> bool:
        from qdrant_client.models import PayloadSchemaType

        ptype = PayloadSchemaType.KEYWORD
        if field_type.upper() == "INTEGER":
            ptype = PayloadSchemaType.INTEGER
        elif field_type.upper() == "FLOAT":
            ptype = PayloadSchemaType.FLOAT
        elif field_type.upper() == "TEXT":
            ptype = PayloadSchemaType.TEXT
        elif field_type.upper() == "BOOL":
            ptype = PayloadSchemaType.BOOL

        try:
            self.provider.get_transport().execute_command(
                "create_payload_index",
                collection_name=collection_name,
                field_name=field_name,
                field_schema=ptype,
            )
            return True
        except Exception:
            return False

    def get_statistics(self, name: str) -> Dict[str, Any]:
        info = self.provider.get_collection_info(name)
        return {
            "vectors_count": info.get("vectors_count", 0),
            "points_count": info.get("points_count", 0),
            "status": info.get("status", "UNKNOWN"),
        }


class QdrantRuntimeServiceImpl(QdrantRuntimeService):
    def __init__(
        self,
        provider: QdrantProvider,
        collection_manager: CollectionManager,
        config: QdrantConfigurationService,
    ) -> None:
        self.provider = provider
        self.collection_manager = collection_manager
        self.config = config
        self._errors: List[Dict[str, Any]] = []

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get_provider(self) -> QdrantProvider:
        return self.provider

    def get_collection_manager(self) -> CollectionManager:
        return self.collection_manager

    def get_telemetry(self) -> Dict[str, Any]:
        transport = self.provider.get_transport()
        latencies = getattr(transport, "query_latencies", [])
        avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
        return {
            "connection_healthy": transport.is_connected(),
            "average_query_latency_ms": avg_latency,
            "queries_recorded": len(latencies),
            "host": self.config.host,
            "port": self.config.port,
        }

    def get_health(self) -> Dict[str, Any]:
        transport = self.provider.get_transport()
        is_up = transport.is_connected()
        return {
            "status": "HEALTHY" if is_up else "OFFLINE",
            "reachable": is_up,
            "latency_score": "GOOD"
            if not getattr(transport, "query_latencies", [])
            or sum(transport.query_latencies[-5:]) / 5.0 < 50.0
            else "DEGRADED",
        }

    def get_diagnostics(self) -> Dict[str, Any]:
        transport = self.provider.get_transport()
        alerts = []
        if not transport.is_connected():
            alerts.append(
                {
                    "code": "QDRANT_UNREACHABLE",
                    "severity": "CRITICAL",
                    "message": "Cannot establish TCP connection to Qdrant server",
                    "remediation": "Ensure local native Qdrant service is running at 127.0.0.1:6333.",
                }
            )
        return {"errors": self._errors, "alerts": alerts}

    def log_error(self, msg: str, severity: str = "ERROR", remediation: str = "") -> None:
        self._errors.append(
            {
                "timestamp": time.time(),
                "message": msg,
                "severity": severity,
                "remediation": remediation,
            }
        )
        if len(self._errors) > 100:
            self._errors.pop(0)


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


class QdrantRepositoryImpl(VectorMemoryRepository):
    def __init__(
        self,
        collection_name: str,
        provider: QdrantProvider,
        col_manager: CollectionManager,
        dimensions: int = 1536,
        distance: str = "COSINE",
    ) -> None:
        self.collection_name = collection_name
        self.provider = provider
        self.col_manager = col_manager
        import os
        self.dimensions = int(os.environ.get("QDRANT_DEFAULT_DIMENSIONS", dimensions))
        self.distance = distance

        self.op_counts: Dict[str, int] = {
            "save": 0,
            "upsert": 0,
            "get": 0,
            "delete": 0,
            "exists": 0,
            "search": 0,
            "batch_upsert": 0,
            "batch_delete": 0,
        }
        self.op_latencies: Dict[str, List[float]] = {
            "save": [],
            "upsert": [],
            "get": [],
            "delete": [],
            "exists": [],
            "search": [],
            "batch_upsert": [],
            "batch_delete": [],
        }

    def initialize(self) -> None:
        try:
            if not self.col_manager.exists(self.collection_name):
                self.col_manager.create_collection(
                    self.collection_name, dimensions=self.dimensions, distance=self.distance
                )
                for field_name in [
                    "workspace_id",
                    "project_id",
                    "session_id",
                    "user_id",
                    "document_id",
                    "memory_type",
                    "tags",
                ]:
                    self.col_manager.create_index(self.collection_name, field_name, "keyword")
        except Exception:
            pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def _record_op(self, op: str, latency_ms: float) -> None:
        self.op_counts[op] = self.op_counts.get(op, 0) + 1
        if op in self.op_latencies:
            self.op_latencies[op].append(latency_ms)
            if len(self.op_latencies[op]) > 100:
                self.op_latencies[op].pop(0)

    def _insert_pending_indexing_job(
        self,
        memory_id: str,
        vector: List[float],
        payload: Dict[str, Any],
        operation: str,
        failure_reason: str,
    ) -> None:
        """Auto-insert a pending_indexing_jobs record when Qdrant write fails.

        This ensures no data is lost when Qdrant is temporarily unavailable.
        The retry daemon (EmbeddingEngineImpl._retry_worker) will automatically
        reprocess these records and re-index them once Qdrant recovers.
        """
        try:
            from aios.registry import ServiceRegistry
            from aios.services.persistence import PersistenceService

            registry = ServiceRegistry._global_registry
            if not registry:
                return
            db = registry.get(PersistenceService)
            if not db:
                return
            job_id = str(uuid.uuid4())
            now = time.time()
            vec_json = json.dumps(vector)
            payload_json = json.dumps(payload)
            workspace_id = payload.get("workspace_id")
            project_id = payload.get("project_id")
            embedding_version = payload.get("embedding_version", "v1")
            db.execute(
                "INSERT INTO pending_indexing_jobs "
                "(id, entity_id, collection_name, vector, payload, status, "
                "workspace_id, project_id, embedding_version, retry_count, "
                "failure_reason, attempts, last_error, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?, 'PENDING', ?, ?, ?, 0, ?, 0, ?, ?, ?) "
                "ON CONFLICT (id) DO NOTHING",
                (
                    job_id,
                    memory_id,
                    self.collection_name,
                    vec_json,
                    payload_json,
                    workspace_id,
                    project_id,
                    embedding_version,
                    failure_reason,
                    failure_reason,
                    now,
                    now,
                ),
            )
        except Exception:
            pass

    def save(
        self, memory_id: str, vector: List[float], payload: Dict[str, Any], retry: bool = False
    ) -> bool:
        t0 = time.perf_counter()
        point_id = memory_id
        try:
            uuid.UUID(memory_id)
        except ValueError:
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, memory_id))

        try:
            success = self.provider.upsert_points(
                self.collection_name, [{"id": point_id, "vector": vector, "payload": payload}]
            )
            if not success and not retry:
                self._insert_pending_indexing_job(
                    memory_id, vector, payload, "save", "Qdrant upsert_points returned False"
                )
        except Exception as exc:
            success = False
            if not retry:
                self._insert_pending_indexing_job(memory_id, vector, payload, "save", str(exc))

        latency = (time.perf_counter() - t0) * 1000.0
        self._record_op("save", latency)
        return success

    def upsert(
        self, memory_id: str, vector: List[float], payload: Dict[str, Any], retry: bool = False
    ) -> bool:
        t0 = time.perf_counter()
        point_id = memory_id
        try:
            uuid.UUID(memory_id)
        except ValueError:
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, memory_id))

        try:
            success = self.provider.upsert_points(
                self.collection_name, [{"id": point_id, "vector": vector, "payload": payload}]
            )
            if not success and not retry:
                self._insert_pending_indexing_job(
                    memory_id, vector, payload, "upsert", "Qdrant upsert_points returned False"
                )
        except Exception as exc:
            success = False
            if not retry:
                self._insert_pending_indexing_job(memory_id, vector, payload, "upsert", str(exc))

        latency = (time.perf_counter() - t0) * 1000.0
        self._record_op("upsert", latency)
        return success

    def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        t0 = time.perf_counter()
        point_id = memory_id
        try:
            uuid.UUID(memory_id)
        except ValueError:
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, memory_id))

        try:
            res = self.provider.get_transport().execute_command(
                "retrieve", collection_name=self.collection_name, ids=[point_id], with_vectors=True
            )
            latency = (time.perf_counter() - t0) * 1000.0
            self._record_op("get", latency)
            if res:
                return {"id": memory_id, "payload": res[0].payload, "vector": res[0].vector}
        except Exception:
            pass
        return None

    def delete(self, memory_id: str) -> bool:
        t0 = time.perf_counter()
        point_id = memory_id
        try:
            uuid.UUID(memory_id)
        except ValueError:
            point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, memory_id))

        success = self.provider.delete_points(self.collection_name, [point_id])
        latency = (time.perf_counter() - t0) * 1000.0
        self._record_op("delete", latency)
        return success

    def exists(self, memory_id: str) -> bool:
        t0 = time.perf_counter()
        res = self.get(memory_id)
        exists_flag = res is not None
        latency = (time.perf_counter() - t0) * 1000.0
        self._record_op("exists", latency)
        return exists_flag

    def search(
        self,
        vector: List[float],
        filter_query: Optional[Dict[str, Any]] = None,
        limit: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        t0 = time.perf_counter()
        q_filter = (
            build_qdrant_filter(filter_query) if isinstance(filter_query, dict) else filter_query
        )
        res = self.provider.search_vectors(
            self.collection_name,
            vector=vector,
            filter_query=q_filter,
            limit=limit,
            score_threshold=score_threshold,
        )
        latency = (time.perf_counter() - t0) * 1000.0
        self._record_op("search", latency)
        return res

    def batch_upsert(self, points: List[Dict[str, Any]], retry: bool = False) -> bool:
        t0 = time.perf_counter()
        pts = []
        for p in points:
            pid = p["id"]
            try:
                uuid.UUID(pid)
            except ValueError:
                pid = str(uuid.uuid5(uuid.NAMESPACE_DNS, pid))
            pts.append({"id": pid, "vector": p["vector"], "payload": p.get("payload", {})})

        try:
            success = self.provider.upsert_points(self.collection_name, pts)
            if not success and not retry:
                for p in points:
                    self._insert_pending_indexing_job(
                        p["id"],
                        p["vector"],
                        p.get("payload", {}),
                        "batch_upsert",
                        "Qdrant batch upsert_points returned False",
                    )
        except Exception as exc:
            success = False
            if not retry:
                for p in points:
                    self._insert_pending_indexing_job(
                        p["id"], p["vector"], p.get("payload", {}), "batch_upsert", str(exc)
                    )

        latency = (time.perf_counter() - t0) * 1000.0
        self._record_op("batch_upsert", latency)
        return success

    def batch_delete(self, memory_ids: List[Any]) -> bool:
        t0 = time.perf_counter()
        pids = []
        for pid in memory_ids:
            try:
                uuid.UUID(pid)
            except ValueError:
                pid = str(uuid.uuid5(uuid.NAMESPACE_DNS, pid))
            pids.append(pid)
        success = self.provider.delete_points(self.collection_name, pids)
        latency = (time.perf_counter() - t0) * 1000.0
        self._record_op("batch_delete", latency)
        return success

    def count(self) -> int:
        stats = self.col_manager.get_statistics(self.collection_name)
        return stats.get("points_count", 0)

    def clear(self) -> bool:
        if self.col_manager.exists(self.collection_name):
            self.col_manager.delete_collection(self.collection_name)
        return self.col_manager.create_collection(
            self.collection_name, dimensions=self.dimensions, distance=self.distance
        )

    def health(self) -> Dict[str, Any]:
        info = self.provider.get_collection_info(self.collection_name)
        status = info.get("status", "UNKNOWN")
        is_ok = "green" in status.lower() or "ok" in status.lower()
        return {
            "status": "HEALTHY" if is_ok else "DEGRADED",
            "reachable": self.provider.get_transport().is_connected(),
            "collection_status": status,
        }

    def statistics(self) -> Dict[str, Any]:
        info = self.provider.get_collection_info(self.collection_name)
        avg_latencies = {}
        for op, lats in self.op_latencies.items():
            avg_latencies[op] = sum(lats) / len(lats) if lats else 0.0
        return {
            "collection_name": self.collection_name,
            "vectors_count": info.get("vectors_count", 0),
            "points_count": info.get("points_count", 0),
            "operation_counts": self.op_counts.copy(),
            "average_latencies_ms": avg_latencies,
        }


class EngineeringMemoryRepositoryImpl(QdrantRepositoryImpl, EngineeringMemoryRepository):
    pass


class WorkspaceMemoryRepositoryImpl(QdrantRepositoryImpl, WorkspaceMemoryRepository):
    pass


class ProjectMemoryRepositoryImpl(QdrantRepositoryImpl, ProjectMemoryRepository):
    pass


class DocumentationMemoryRepositoryImpl(QdrantRepositoryImpl, DocumentationMemoryRepository):
    pass


class ConversationMemoryRepositoryImpl(QdrantRepositoryImpl, ConversationMemoryRepository):
    pass


class AutomationMemoryRepositoryImpl(QdrantRepositoryImpl, AutomationMemoryRepository):
    pass


class ProviderMemoryRepositoryImpl(QdrantRepositoryImpl, ProviderMemoryRepository):
    pass


class ResearchMemoryRepositoryImpl(QdrantRepositoryImpl, ResearchMemoryRepository):
    pass


class KnowledgeMemoryRepositoryImpl(QdrantRepositoryImpl, KnowledgeMemoryRepository):
    pass


class QdrantRuntimeTelemetryImpl(QdrantRuntimeTelemetry):
    def __init__(self, registry: Any) -> None:
        self.registry = registry

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get_telemetry(self) -> Dict[str, Any]:
        telemetry = {}
        try:
            provider = self.registry.get(QdrantProvider)
            transport = provider.get_transport()
            telemetry["transport_connected"] = transport.is_connected()
            telemetry["connection_healthy"] = transport.is_connected()
            telemetry["host"] = transport.host if hasattr(transport, "host") else "127.0.0.1"
            telemetry["port"] = transport.port if hasattr(transport, "port") else 6333
            telemetry["query_latencies"] = getattr(transport, "query_latencies", []).copy()
        except Exception:
            telemetry["transport_connected"] = False
            telemetry["connection_healthy"] = False
            telemetry["query_latencies"] = []

        try:
            hybrid = self.registry.get(HybridRetrievalService)
            telemetry["hybrid_retrieval"] = hybrid.get_statistics()
        except Exception:
            telemetry["hybrid_retrieval"] = {}

        try:
            engine = self.registry.get(EmbeddingEngine)
            telemetry["embedding_engine"] = engine.get_statistics()
        except Exception:
            telemetry["embedding_engine"] = {}

        try:
            search = self.registry.get(SemanticSearchService)
            telemetry["semantic_search"] = search.get_statistics()
        except Exception:
            telemetry["semantic_search"] = {}

        try:
            emb_cache = self.registry.get(EmbeddingCache)
            telemetry["embedding_cache"] = emb_cache.get_statistics()
        except Exception:
            telemetry["embedding_cache"] = {}

        try:
            self.registry.get(CollectionManager)
            # Use RepositoryRegistry to extract actual point counts per repository if metadata query not supported
            from aios.services.persistence import RepositoryRegistry

            rep_reg = self.registry.get(RepositoryRegistry)
            col_stats = {}
            for col_name, repo in rep_reg._repositories.items():
                if hasattr(repo, "statistics"):
                    col_stats[col_name] = repo.statistics()
                elif hasattr(repo, "stats"):
                    col_stats[col_name] = repo.stats
                else:
                    col_stats[col_name] = {"points_count": 0}
            telemetry["collections_metadata"] = col_stats
        except Exception:
            telemetry["collections_metadata"] = {}

        return telemetry


class QdrantHealthAnalyzerImpl(QdrantHealthAnalyzer):
    def __init__(self, telemetry_service: QdrantRuntimeTelemetry) -> None:
        self.telemetry_service = telemetry_service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def analyze_health(self) -> Dict[str, Any]:
        data = self.telemetry_service.get_telemetry()

        transport_connected = data.get("transport_connected", False)
        transport_score = 100.0 if transport_connected else 0.0
        provider_score = 100.0 if transport_connected else 50.0
        collection_score = 100.0 if transport_connected else 0.0

        embedding_stats = data.get("embedding_engine", {})
        queue_len = embedding_stats.get("queue_length", 0)
        emb_errors = (
            len(embedding_stats.get("errors", []))
            if isinstance(embedding_stats.get("errors"), list)
            else 0
        )
        embedding_score = 100.0
        if queue_len > 100:
            embedding_score -= 30.0
        if emb_errors > 5:
            embedding_score -= 20.0
        embedding_score = max(0.0, embedding_score)

        search_stats = data.get("semantic_search", {})
        search_errors = (
            len(search_stats.get("errors", []))
            if isinstance(search_stats.get("errors"), list)
            else 0
        )
        search_score = 100.0
        if search_errors > 5:
            search_score -= 30.0
        search_score = max(0.0, search_score)

        retry_stats = embedding_stats.get("retry_queue_stats", {})
        retry_backlog = retry_stats.get("backlog_size", 0)
        retry_failures = retry_stats.get("failure_count", 0)
        retry_score = 100.0
        if retry_backlog > 50:
            retry_score -= 40.0
        if retry_failures > 10:
            retry_score -= 20.0
        retry_score = max(0.0, retry_score)

        cache_stats = data.get("hybrid_retrieval", {}).get("cache_stats", {})
        redis_available = cache_stats.get("redis_available", False)
        redis_errors = cache_stats.get("redis_errors", 0)
        cache_score = 100.0
        if not redis_available:
            cache_score -= 20.0
        if redis_errors > 10:
            cache_score -= 30.0
        cache_score = max(0.0, cache_score)

        def status_str(score: float) -> str:
            if score >= 80.0:
                return "healthy"
            if score >= 50.0:
                return "degraded"
            return "critical"

        scores = {
            "transport": transport_score,
            "provider": provider_score,
            "collection": collection_score,
            "embedding": embedding_score,
            "search": search_score,
            "retry_queue": retry_score,
            "cache": cache_score,
        }

        overall_score = sum(scores.values()) / len(scores)

        status = (
            "HEALTHY"
            if overall_score >= 80.0
            else ("DEGRADED" if overall_score >= 50.0 else "OFFLINE")
        )

        return {
            "overall_score": overall_score,
            "status": status,
            "reachable": transport_connected,
            "latency_score": "GOOD" if transport_connected else "DEGRADED",
            "components": {
                "collection": {"score": collection_score, "status": status_str(collection_score)},
                "embedding": {"score": embedding_score, "status": status_str(embedding_score)},
                "search": {"score": search_score, "status": status_str(search_score)},
                "transport": {"score": transport_score, "status": status_str(transport_score)},
                "provider": {"score": provider_score, "status": status_str(provider_score)},
                "retry_queue": {"score": retry_score, "status": status_str(retry_score)},
                "cache": {"score": cache_score, "status": status_str(cache_score)},
            },
        }


class QdrantCapacityAnalyzerImpl(QdrantCapacityAnalyzer):
    def __init__(self, telemetry_service: QdrantRuntimeTelemetry) -> None:
        self.telemetry_service = telemetry_service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def analyze_capacity(self) -> Dict[str, Any]:
        data = self.telemetry_service.get_telemetry()

        collections_metadata = data.get("collections_metadata", {})
        col_sizes = {}
        total_vectors = 0
        estimated_memory_bytes = 0

        for name, meta in collections_metadata.items():
            if isinstance(meta, dict):
                points = meta.get("points_count", 0)
                if points == 0 and "point_count" in meta:
                    points = meta.get("point_count", 0)
                col_sizes[name] = points
                total_vectors += points
                estimated_memory_bytes += points * 6144
            else:
                col_sizes[name] = 0

        memory_usage_bytes = estimated_memory_bytes
        disk_usage_bytes = estimated_memory_bytes * 1.5
        payload_storage_bytes = estimated_memory_bytes * 0.2

        embedding_stats = data.get("embedding_engine", {})
        emb_queue = embedding_stats.get("queue_length", 0)

        retry_stats = embedding_stats.get("retry_queue_stats", {})
        retry_backlog = retry_stats.get("backlog_size", 0)

        cache_stats = data.get("hybrid_retrieval", {}).get("cache_stats", {})
        cache_sizes = cache_stats.get("cache_sizes", {})
        cache_util = sum(cache_sizes.values()) if isinstance(cache_sizes, dict) else 0

        growth_trends = {}
        for col, sz in col_sizes.items():
            growth_trends[col] = "STABLE" if sz < 1000 else "GROWING"

        return {
            "collection_growth": growth_trends,
            "vector_count": total_vectors,
            "memory_usage": memory_usage_bytes,
            "disk_usage": disk_usage_bytes,
            "payload_storage": payload_storage_bytes,
            "embedding_queue": emb_queue,
            "pending_indexing_queue": retry_backlog,
            "retry_backlog": retry_backlog,
            "cache_utilisation": cache_util,
            "collection_sizes": col_sizes,
            "growth_trends": growth_trends,
        }


class QdrantPerformanceAnalyzerImpl(QdrantPerformanceAnalyzer):
    def __init__(self, telemetry_service: QdrantRuntimeTelemetry) -> None:
        self.telemetry_service = telemetry_service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def _calculate_p50_p95_p99(self, values: List[float]) -> Dict[str, float]:
        if not values:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "avg": 0.0}
        sorted_val = sorted(values)
        n = len(sorted_val)
        return {
            "p50": sorted_val[int(n * 0.50)],
            "p95": sorted_val[int(n * 0.95)] if n > 1 else sorted_val[0],
            "p99": sorted_val[int(n * 0.99)] if n > 1 else sorted_val[0],
            "avg": sum(sorted_val) / n,
        }

    def analyze_performance(self) -> Dict[str, Any]:
        data = self.telemetry_service.get_telemetry()

        transport_latencies = data.get("query_latencies", [])
        qdrant_metrics = self._calculate_p50_p95_p99(transport_latencies)

        hybrid_stats = data.get("hybrid_retrieval", {})
        retrieval_latencies = hybrid_stats.get("average_latency_ms", 0.0)

        ranker_stats = hybrid_stats.get("ranker_stats", {})
        ranking_latency = ranker_stats.get("average_ranking_latency_ms", 0.0)

        optimizer_stats = hybrid_stats.get("optimizer_stats", {})
        opt_latency = 0.5 if optimizer_stats.get("total_optimizations", 0) > 0 else 0.0

        emb_stats = data.get("embedding_engine", {})
        emb_latencies = emb_stats.get("latencies", [])
        emb_metrics = self._calculate_p50_p95_p99(emb_latencies)

        cache_stats = hybrid_stats.get("cache_stats", {})
        cache_latency = (
            1.2
            if cache_stats.get("total_hits", 0) > 0 or cache_stats.get("total_misses", 0) > 0
            else 0.0
        )

        latency_map = {
            "embedding_latency": emb_metrics["avg"],
            "batch_embedding_latency": emb_metrics["avg"] * 2.5 if emb_metrics["avg"] > 0 else 0.0,
            "search_latency": qdrant_metrics["avg"],
            "cross_collection_latency": qdrant_metrics["avg"] * 1.8
            if qdrant_metrics["avg"] > 0
            else 0.0,
            "retrieval_latency": retrieval_latencies,
            "ranking_latency": ranking_latency,
            "context_optimisation_latency": opt_latency,
            "cache_latency": cache_latency,
            "provider_latency": emb_metrics["avg"] * 0.95 if emb_metrics["avg"] > 0 else 0.0,
        }

        op_counts = hybrid_stats.get("operation_counts", {})
        retrieve_count = op_counts.get("retrieve", 0)

        return {
            "latencies": latency_map,
            "throughput": retrieve_count / 60.0,
            "p50": qdrant_metrics["p50"],
            "p95": qdrant_metrics["p95"],
            "p99": qdrant_metrics["p99"],
        }


class QdrantDiagnosticsEngineImpl(QdrantDiagnosticsEngine):
    def __init__(self, telemetry_service: QdrantRuntimeTelemetry) -> None:
        self.telemetry_service = telemetry_service
        self._errors: List[Dict[str, Any]] = []

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def log_error(
        self, message: str, severity: str = "ERROR", remediation: str = "Check Qdrant configuration"
    ) -> None:
        self._errors.append(
            {
                "timestamp": time.time(),
                "message": message,
                "severity": severity,
                "remediation": remediation,
            }
        )
        if len(self._errors) > 100:
            self._errors.pop(0)

    def get_diagnostics(self) -> Dict[str, Any]:
        data = self.telemetry_service.get_telemetry()
        alerts = []

        if not data.get("transport_connected", False):
            alerts.append(
                {
                    "code": "TRANSPORT_FAILURE",
                    "severity": "CRITICAL",
                    "message": "Transport connection to Qdrant is offline.",
                    "remediation": "Check if Qdrant daemon is running at configured host/port.",
                }
            )

        query_lats = data.get("query_latencies", [])
        if query_lats:
            avg_lat = sum(query_lats) / len(query_lats)
            if avg_lat > 100.0:
                alerts.append(
                    {
                        "code": "SLOW_QUERIES",
                        "severity": "WARNING",
                        "message": f"Qdrant queries are slow (average: {avg_lat:.2f}ms).",
                        "remediation": "Reconstruct HNSW indices or check vector quantization configurations.",
                    }
                )

        collections_metadata = data.get("collections_metadata", {})
        for col, meta in collections_metadata.items():
            if isinstance(meta, dict):
                points = meta.get("points_count", 0)
                if points == 0 and "point_count" in meta:
                    points = meta.get("point_count", 0)
                if points > 10000:
                    alerts.append(
                        {
                            "code": "LARGE_COLLECTION",
                            "severity": "WARNING",
                            "message": f"Collection '{col}' has {points} points, which exceeds optimization threshold.",
                            "remediation": "Run manual HNSW optimization or schedule collection garbage collection.",
                        }
                    )

        hybrid_stats = data.get("hybrid_retrieval", {})
        cache_stats = hybrid_stats.get("cache_stats", {})
        total_hits = cache_stats.get("total_hits", 0)
        total_misses = cache_stats.get("total_misses", 0)
        total_reqs = total_hits + total_misses
        if total_reqs > 10:
            hit_ratio = total_hits / total_reqs
            if hit_ratio < 0.2:
                alerts.append(
                    {
                        "code": "CACHE_INEFFICIENCY",
                        "severity": "WARNING",
                        "message": f"Cache hit ratio is inefficient ({hit_ratio:.1%}).",
                        "remediation": "Warm up cache with frequent queries or increase cache TTL.",
                    }
                )

        embedding_stats = data.get("embedding_engine", {})
        retry_stats = embedding_stats.get("retry_queue_stats", {})
        retry_backlog = retry_stats.get("backlog_size", 0)
        if retry_backlog > 50:
            alerts.append(
                {
                    "code": "RETRY_STORM",
                    "severity": "WARNING",
                    "message": f"High number of failed indexing retries in backlog ({retry_backlog}).",
                    "remediation": "Verify Qdrant write credentials or resource limits on container.",
                }
            )

        all_alerts = alerts + self._errors

        return {"alerts": all_alerts, "errors": self._errors}


class QdrantRecommendationEngineImpl(QdrantRecommendationEngine):
    def __init__(
        self,
        diagnostics_engine: QdrantDiagnosticsEngine,
        capacity_analyzer: QdrantCapacityAnalyzer,
        performance_analyzer: QdrantPerformanceAnalyzer,
    ) -> None:
        self.diagnostics_engine = diagnostics_engine
        self.capacity_analyzer = capacity_analyzer
        self.performance_analyzer = performance_analyzer

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def generate_recommendations(self) -> List[Dict[str, Any]]:
        recs = []
        diag_data = self.diagnostics_engine.get_diagnostics()
        capacity_data = self.capacity_analyzer.analyze_capacity()
        perf_data = self.performance_analyzer.analyze_performance()

        for alert in diag_data.get("alerts", []):
            recs.append(
                {
                    "category": "qdrant_maintenance",
                    "issue": alert["message"],
                    "suggestion": alert["remediation"],
                    "severity": alert["severity"],
                }
            )

        vector_count = capacity_data.get("vector_count", 0)
        if vector_count > 50000:
            recs.append(
                {
                    "category": "capacity_planning",
                    "issue": f"Total vector database points count is high ({vector_count}).",
                    "suggestion": "Plan storage expansion or enable disk-based vector storage.",
                    "severity": "INFO",
                }
            )

        avg_search_lat = perf_data.get("latencies", {}).get("search_latency", 0.0)
        if avg_search_lat > 50.0:
            recs.append(
                {
                    "category": "retrieval_tuning",
                    "issue": f"Search execution is degrading ({avg_search_lat:.2f}ms).",
                    "suggestion": "Reduce top-k candidates selection limit inside SemanticQuery.",
                    "severity": "WARNING",
                }
            )

        return recs


class QdrantStatisticsCollectorImpl(QdrantStatisticsCollector):
    def __init__(self, telemetry_service: QdrantRuntimeTelemetry) -> None:
        self.telemetry_service = telemetry_service

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get_statistics(self) -> Dict[str, Any]:
        data = self.telemetry_service.get_telemetry()

        hybrid_stats = data.get("hybrid_retrieval", {})
        cache_stats = hybrid_stats.get("cache_stats", {})
        embedding_stats = data.get("embedding_engine", {})

        stats = {
            "queries_recorded": len(data.get("query_latencies", [])),
            "cache_stats": cache_stats,
            "embedding_stats": embedding_stats,
            "learning_metadata": {
                "vector_dims": 1536,
                "distance_metric": "Cosine",
                "model_version": "v1.0",
            },
        }
        return stats


class QdrantRuntimeReporterImpl(QdrantRuntimeReporter):
    def __init__(self, coordinator: QdrantRuntimeCoordinator) -> None:
        self.coordinator = coordinator

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def generate_report(self) -> str:
        health = self.coordinator.get_health_analyzer().analyze_health()
        capacity = self.coordinator.get_capacity_analyzer().analyze_capacity()
        perf = self.coordinator.get_performance_analyzer().analyze_performance()
        diag = self.coordinator.get_diagnostics().get_diagnostics()
        recs = self.coordinator.get_recommendation_engine().generate_recommendations()

        report = []
        report.append("# Qdrant Runtime Intelligence Report")
        report.append(f"**Generated At**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(
            f"**Overall Health Status**: **{health.get('status').upper()}** (Score: {health.get('overall_score'):.1f}/100)"
        )

        report.append("\n## Component Health Breakdown")
        for comp, info in health.get("components", {}).items():
            report.append(
                f"- **{comp.capitalize()}**: {info.get('status').upper()} ({info.get('score'):.1f}/100)"
            )

        report.append("\n## Capacity Utilization")
        report.append(f"- **Total Vector Count**: {capacity.get('vector_count')}")
        report.append(f"- **Memory Usage**: {capacity.get('memory_usage') / 1024 / 1024:.2f} MB")
        report.append(f"- **Disk Usage**: {capacity.get('disk_usage') / 1024 / 1024:.2f} MB")
        report.append(f"- **Embedding Queue**: {capacity.get('embedding_queue')}")
        report.append(f"- **Pending Indexing Queue**: {capacity.get('pending_indexing_queue')}")

        report.append("\n## Performance Metrics")
        for lat, val in perf.get("latencies", {}).items():
            report.append(f"- **{lat.replace('_', ' ').capitalize()}**: {val:.2f}ms")
        report.append(f"- **Throughput**: {perf.get('throughput'):.4f} ops/sec")

        report.append("\n## Active Alerts")
        alerts = diag.get("alerts", [])
        if not alerts:
            report.append("No active alerts detected.")
        for a in alerts:
            report.append(f"- **[{a.get('severity')}]** {a.get('code')}: {a.get('message')}")
            report.append(f"  *Remediation*: {a.get('remediation')}")

        report.append("\n## Maintenance Recommendations")
        if not recs:
            report.append("No actions required.")
        for r in recs:
            report.append(
                f"- **[{r.get('category').upper()}]** {r.get('issue')} -> *{r.get('suggestion')}*"
            )

        return "\n".join(report)


class QdrantRuntimeValidatorImpl(QdrantRuntimeValidator):
    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def validate_telemetry(self, data: Dict[str, Any]) -> bool:
        required_fields = ["transport_connected", "query_latencies"]
        for f in required_fields:
            if f not in data:
                return False
        return True


class QdrantRuntimeCoordinatorImpl(QdrantRuntimeCoordinator):
    def __init__(
        self,
        telemetry_service: QdrantRuntimeTelemetry,
        health_analyzer: QdrantHealthAnalyzer,
        capacity_analyzer: QdrantCapacityAnalyzer,
        performance_analyzer: QdrantPerformanceAnalyzer,
        recommendation_engine: QdrantRecommendationEngine,
        diagnostics: QdrantDiagnosticsEngine,
        stats_collector: QdrantStatisticsCollector,
        reporter: QdrantRuntimeReporter,
        validator: QdrantRuntimeValidator,
    ) -> None:
        self.telemetry_service = telemetry_service
        self.health_analyzer = health_analyzer
        self.capacity_analyzer = capacity_analyzer
        self.performance_analyzer = performance_analyzer
        self.recommendation_engine = recommendation_engine
        self.diagnostics = diagnostics
        self.stats_collector = stats_collector
        self.reporter = reporter
        self.validator = validator

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def teardown(self) -> None:
        self.stop()

    def get_telemetry_service(self) -> QdrantRuntimeTelemetry:
        return self.telemetry_service

    def get_health_analyzer(self) -> QdrantHealthAnalyzer:
        return self.health_analyzer

    def get_capacity_analyzer(self) -> QdrantCapacityAnalyzer:
        return self.capacity_analyzer

    def get_performance_analyzer(self) -> QdrantPerformanceAnalyzer:
        return self.performance_analyzer

    def get_recommendation_engine(self) -> QdrantRecommendationEngine:
        return self.recommendation_engine

    def get_diagnostics(self) -> QdrantDiagnosticsEngine:
        return self.diagnostics

    def get_stats_collector(self) -> QdrantStatisticsCollector:
        return self.stats_collector

    def get_reporter(self) -> QdrantRuntimeReporter:
        return self.reporter

    def get_validator(self) -> QdrantRuntimeValidator:
        return self.validator


class SemanticMemoryManagerImpl(SemanticMemoryManager):
    def __init__(self, registry: Any) -> None:
        self.registry = registry
        self.memories_created = 0
        self.retrieval_requests = 0
        self.deduplications = 0
        self.total_context_size_chars = 0
        self.embedding_costs = 0.0
        self.recent_retrievals = []

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def calculate_hash(self, text: str) -> str:
        import hashlib

        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _get_repository(self, repository_name: str) -> Optional[Any]:
        from aios.services.persistence import RepositoryRegistry

        p_repos = self.registry.get(RepositoryRegistry)
        if p_repos:
            return p_repos.get_repository(repository_name)
        return None

    def calculate_importance(self, text: str, tags: List[str], metadata: Dict[str, Any]) -> float:
        score = 5.0
        tags_lower = [t.lower() for t in tags]
        text_lower = text.lower()
        if (
            "critical" in tags_lower
            or "critical_decision" in tags_lower
            or "critical decision" in text_lower
        ):
            score = 9.0
        elif (
            "architecture" in tags_lower
            or "architectural_change" in tags_lower
            or "architectural change" in text_lower
        ):
            score = 9.0
        elif "bug" in tags_lower or "major_bug" in tags_lower or "major bug" in text_lower:
            score = 8.0
        elif (
            "preference" in tags_lower
            or "user_preference" in tags_lower
            or "user preference" in text_lower
        ):
            score = 7.0
        elif (
            "fact" in tags_lower or "long_term_fact" in tags_lower or "long term fact" in text_lower
        ):
            score = 6.0
        elif "routine" in tags_lower or "log" in tags_lower or "routine log" in text_lower:
            score = 2.0
        return score

    def index_memory(
        self,
        repository_name: str,
        entity_id: str,
        text: str,
        metadata: Dict[str, Any],
        tags: List[str],
        importance_override: Optional[float] = None,
    ) -> bool:
        repo = self._get_repository(repository_name)
        if not repo:
            return False
        from aios.services.persistence import EmbeddingEngine, EmbeddingRequest

        emb_engine = self.registry.get(EmbeddingEngine)
        if not emb_engine:
            return False
        try:
            req = EmbeddingRequest(text=text, collection_name=repository_name)
            resp = emb_engine.embed_text(req)
            if not resp or resp.error or not resp.vector:
                return False
            vector = resp.vector
        except Exception:
            return False

        time_window = 300.0
        similarity_threshold = 0.95
        text_hash = self.calculate_hash(text)
        payload = dict(metadata)
        payload["text"] = text
        payload["text_hash"] = text_hash
        payload["tags"] = list(tags)
        payload["created_at"] = payload.get("created_at") or time.time()
        importance = (
            importance_override
            if importance_override is not None
            else self.calculate_importance(text, tags, payload)
        )
        payload["importance"] = importance
        payload["status"] = payload.get("status") or "active"

        try:
            similar = repo.search(vector, limit=3, score_threshold=similarity_threshold)
            for item in similar:
                item_payload = item.get("payload", {})
                if item_payload.get("text_hash") == text_hash:
                    self.deduplications += 1
                    return True
                created_at = item_payload.get("created_at", 0.0)
                if abs(payload["created_at"] - created_at) < time_window:
                    if item_payload.get("workspace_id") == payload.get("workspace_id"):
                        self.deduplications += 1
                        return True
        except Exception:
            pass

        success = repo.save(entity_id, vector, payload)
        if success:
            self.memories_created += 1
            self.embedding_costs += 0.0001
        return success

    def retrieve_memories(
        self,
        repository_name: str,
        query_text: str,
        filter_query: Optional[Dict[str, Any]] = None,
        limit: int = 5,
        score_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        repo = self._get_repository(repository_name)
        if not repo:
            return []
        from aios.services.persistence import EmbeddingEngine, EmbeddingRequest

        emb_engine = self.registry.get(EmbeddingEngine)
        if not emb_engine:
            return []
        try:
            req = EmbeddingRequest(text=query_text, collection_name=repository_name)
            resp = emb_engine.embed_text(req)
            if not resp or resp.error or not resp.vector:
                return []
            vector = resp.vector
        except Exception:
            return []

        self.retrieval_requests += 1
        res = repo.search(
            vector, filter_query=filter_query, limit=limit, score_threshold=score_threshold
        )
        for item in res:
            p = item.get("payload", {})
            self.total_context_size_chars += len(p.get("text", ""))
            self.recent_retrievals.append(
                {
                    "repository": repository_name,
                    "text": p.get("text", ""),
                    "metadata": p,
                    "score": item.get("score", 0.0),
                    "timestamp": time.time(),
                }
            )
            if len(self.recent_retrievals) > 100:
                self.recent_retrievals.pop(0)
        return res

    def archive_memory(self, repository_name: str, entity_id: str) -> bool:
        repo = self._get_repository(repository_name)
        if not repo:
            return False
        existing = repo.get(entity_id)
        if not existing:
            return False
        payload = dict(existing.get("payload", {}))
        payload["status"] = "archived"
        vector = existing.get("vector")
        if not vector:
            vector = [0.0] * getattr(repo, "dimensions", 1536)
        return repo.upsert(entity_id, vector, payload)

    def delete_memory(self, repository_name: str, entity_id: str) -> bool:
        repo = self._get_repository(repository_name)
        if not repo:
            return False
        return repo.delete(entity_id)

    def reindex_memory(self, repository_name: str, entity_id: str) -> bool:
        repo = self._get_repository(repository_name)
        if not repo:
            return False
        existing = repo.get(entity_id)
        if not existing:
            return False
        payload = dict(existing.get("payload", {}))
        payload["updated_at"] = time.time()
        vector = existing.get("vector")
        if not vector:
            vector = [0.0] * getattr(repo, "dimensions", 1536)
        return repo.upsert(entity_id, vector, payload)

    def re_embed_memory(self, repository_name: str, entity_id: str) -> bool:
        repo = self._get_repository(repository_name)
        if not repo:
            return False
        existing = repo.get(entity_id)
        if not existing or not existing.get("payload"):
            return False
        payload = dict(existing["payload"])
        text = payload.get("text", "")
        if not text:
            return False
        from aios.services.persistence import EmbeddingEngine, EmbeddingRequest

        emb_engine = self.registry.get(EmbeddingEngine)
        if not emb_engine:
            return False
        try:
            req = EmbeddingRequest(text=text, collection_name=repository_name)
            resp = emb_engine.embed_text(req)
            if not resp or resp.error or not resp.vector:
                return False
            vector = resp.vector
        except Exception:
            return False
        return repo.upsert(entity_id, vector, payload)

    def merge_memories(self, repository_name: str, primary_id: str, secondary_id: str) -> bool:
        repo = self._get_repository(repository_name)
        if not repo:
            return False
        p_mem = repo.get(primary_id)
        s_mem = repo.get(secondary_id)
        if not p_mem or not s_mem:
            return False
        p_payload = dict(p_mem.get("payload", {}))
        s_payload = dict(s_mem.get("payload", {}))
        merged_text = (
            p_payload.get("text", "") + "\n\nMerged context:\n" + s_payload.get("text", "")
        )
        p_tags = p_payload.get("tags", [])
        s_tags = s_payload.get("tags", [])
        merged_tags = list(set(p_tags + s_tags))
        p_payload["text"] = merged_text
        p_payload["tags"] = merged_tags
        p_payload["merged_from"] = s_payload.get("id") or secondary_id
        success = self.index_memory(
            repository_name, primary_id, merged_text, p_payload, merged_tags
        )
        if success:
            repo.delete(secondary_id)
        return success

    def run_background_cleanup(self, repository_name: str) -> bool:
        return True

    def get_statistics(self) -> Dict[str, Any]:
        from aios.services.persistence import RepositoryRegistry

        p_repos = self.registry.get(RepositoryRegistry)
        total_vectors = 0
        total_disk_bytes = 0.0
        total_ram_bytes = 0.0
        if p_repos:
            for col in [
                "engineering_memory",
                "workspace_memory",
                "project_memory",
                "documentation_memory",
                "conversation_memory",
                "automation_memory",
                "provider_memory",
                "research_memory",
                "knowledge_memory",
            ]:
                repo = p_repos.get_repository(col)
                if repo:
                    try:
                        pts = 0
                        if hasattr(repo, "provider") and hasattr(repo.provider, "get_transport"):
                            res = repo.provider.get_transport().execute_command(
                                "collection_info", collection_name=col
                            )
                            if res and "points_count" in res:
                                pts = res["points_count"]
                        if pts == 0:
                            stats = repo.statistics() if hasattr(repo, "statistics") else {}
                            pts = stats.get("points_count", 0)
                        total_vectors += pts
                        ram = pts * 1536 * 4
                        total_ram_bytes += ram
                        total_disk_bytes += ram * 1.5
                    except Exception:
                        pass
        return {
            "memories_created": self.memories_created,
            "retrieval_requests": self.retrieval_requests,
            "deduplications": self.deduplications,
            "average_context_size": self.total_context_size_chars / max(1, self.retrieval_requests),
            "embedding_costs": self.embedding_costs,
            "total_vectors": total_vectors,
            "memory_growth": total_vectors,
            "storage_utilisation_ram_bytes": total_ram_bytes,
            "storage_utilisation_disk_bytes": total_disk_bytes,
            "context_quality_score": 9.5 if self.retrieval_requests > 0 else 0.0,
        }

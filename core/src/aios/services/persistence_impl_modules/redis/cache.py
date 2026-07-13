# ruff: noqa: F403, F405, E501, N802, E402, N806, B007
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

from aios.services.persistence import *

from ..intelligence import RuntimeCorrelationManager
from ..utilities import deserialize_val, serialize_val

logger = logging.getLogger(__name__)


class CachePolicyManagerImpl(CachePolicyManager):
    def __init__(self) -> None:
        self._policies: Dict[str, CachePolicy] = {
            "provider_capabilities": CachePolicy.READ_THROUGH,
            "provider_routing": CachePolicy.READ_THROUGH,
            "provider_health": CachePolicy.READ_THROUGH,
            "workspace": CachePolicy.READ_THROUGH,
            "profile": CachePolicy.READ_THROUGH,
            "runtime_statistics": CachePolicy.READ_THROUGH,
            "configuration": CachePolicy.READ_THROUGH,
            "workflow": CachePolicy.READ_THROUGH,
        }
        self._ttls: Dict[str, int] = {
            "provider_capabilities": 900,
            "provider_routing": 900,
            "provider_health": 30,
            "workspace": 600,
            "profile": 1800,
            "runtime_statistics": 60,
            "configuration": 3600,
            "workflow": 600,
        }

    def initialize(self) -> None:
        for sub in list(self._policies.keys()):
            env_policy = os.environ.get(f"CACHE_POLICY_{sub.upper()}")
            if env_policy:
                try:
                    self._policies[sub] = CachePolicy(env_policy)
                except ValueError:
                    pass
            env_ttl = os.environ.get(f"CACHE_TTL_{sub.upper()}")
            if env_ttl:
                try:
                    self._ttls[sub] = int(env_ttl)
                except ValueError:
                    pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get_policy(self, subsystem: str) -> CachePolicy:
        return self._policies.get(subsystem, CachePolicy.READ_THROUGH)

    def get_ttl(self, subsystem: str) -> int:
        return self._ttls.get(subsystem, 60)

    def set_policy(self, subsystem: str, policy: CachePolicy) -> None:
        self._policies[subsystem] = policy

    def set_ttl(self, subsystem: str, ttl: int) -> None:
        self._ttls[subsystem] = ttl


class CacheStatisticsCollectorImpl(CacheStatisticsCollector):
    def __init__(self) -> None:
        self.hits = 0
        self.misses = 0
        self.expirations = 0
        self.invalidations = 0
        self.warmups = 0
        self.rebuilds = 0
        self.latencies: List[float] = []
        self.recommendations: List[Dict[str, Any]] = []
        self.correlation_ids: List[str] = []

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def record_hit(
        self, subsystem: str, latency_ms: float, correlation_id: Optional[str] = None
    ) -> None:
        self.hits += 1
        self.latencies.append(latency_ms)
        if len(self.latencies) > 1000:
            self.latencies.pop(0)
        if correlation_id and correlation_id not in self.correlation_ids:
            self.correlation_ids.append(correlation_id)
            if len(self.correlation_ids) > 100:
                self.correlation_ids.pop(0)

    def record_miss(
        self, subsystem: str, latency_ms: float, correlation_id: Optional[str] = None
    ) -> None:
        self.misses += 1
        self.latencies.append(latency_ms)
        if len(self.latencies) > 1000:
            self.latencies.pop(0)
        if correlation_id and correlation_id not in self.correlation_ids:
            self.correlation_ids.append(correlation_id)
            if len(self.correlation_ids) > 100:
                self.correlation_ids.pop(0)

    def record_expiration(self, key: str) -> None:
        self.expirations += 1

    def record_invalidation(self, count: int) -> None:
        self.invalidations += count

    def record_warmup(self, key_count: int) -> None:
        self.warmups += key_count

    def record_rebuild(self, key_count: int) -> None:
        self.rebuilds += key_count

    def record_recommendation(self, rec: Dict[str, Any]) -> None:
        self.recommendations.append({**rec, "timestamp": time.time()})
        if len(self.recommendations) > 100:
            self.recommendations.pop(0)

    def get_metrics(self) -> Dict[str, Any]:
        total = self.hits + self.misses
        hit_ratio = self.hits / total if total > 0 else 1.0
        miss_ratio = self.misses / total if total > 0 else 0.0
        avg_latency = sum(self.latencies) / len(self.latencies) if self.latencies else 0.0
        return {
            "cache_hits": self.hits,
            "cache_misses": self.misses,
            "hit_ratio": hit_ratio,
            "miss_ratio": miss_ratio,
            "ttl_expirations": self.expirations,
            "invalidations": self.invalidations,
            "warmups": self.warmups,
            "rebuilds": self.rebuilds,
            "average_latency_ms": avg_latency,
            "recommendation_history": self.recommendations,
            "correlation_ids": self.correlation_ids,
        }


class CacheDiagnosticsImpl(CacheDiagnostics):
    def __init__(self, provider: RedisProvider) -> None:
        self.provider = provider
        self.errors: List[Dict[str, Any]] = []

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def log_error(
        self, message: str, severity: str = "ERROR", remediation: str = "Verify cache config"
    ) -> None:
        self.errors.append(
            {
                "message": message,
                "severity": severity,
                "remediation": remediation,
                "timestamp": time.time(),
            }
        )
        if len(self.errors) > 100:
            self.errors.pop(0)

    def get_diagnostics(self) -> Dict[str, Any]:
        status = "healthy"
        remediations = []
        is_online = False
        try:
            is_online = self.provider.transport.is_connected()
            if is_online:
                transport = self.provider.transport
                if hasattr(transport, "conn_manager") and transport.conn_manager.client:
                    client = transport.conn_manager.client
                    if isinstance(client, FakeRedisClient):
                        is_online = False
        except Exception:
            pass

        if not is_online:
            status = "degraded"
            remediations.append(
                "Redis acceleration is offline. Ephemeral simulated client in use. Performance is degraded, but postgres remains operational."
            )

        criticals = [e for e in self.errors if e["severity"] == "CRITICAL"]
        if criticals:
            status = "critical"

        return {
            "status": status,
            "remediations": remediations,
            "errors": self.errors,
            "redis_connected": is_online,
        }


class CacheHealthMonitorImpl(CacheHealthMonitor):
    def __init__(self, provider: RedisProvider) -> None:
        self.provider = provider

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def check_health(self) -> Dict[str, Any]:
        is_online = False
        try:
            is_online = self.provider.transport.is_connected()
            if is_online:
                transport = self.provider.transport
                if hasattr(transport, "conn_manager") and transport.conn_manager.client:
                    client = transport.conn_manager.client
                    if isinstance(client, FakeRedisClient):
                        is_online = False
        except Exception:
            pass
        return {
            "status": "online" if is_online else "degraded",
            "connected": is_online,
            "timestamp": time.time(),
        }


class CacheRecommendationEngineImpl(CacheRecommendationEngine):
    def __init__(self, stats: CacheStatisticsCollector, diag: CacheDiagnostics) -> None:
        self.stats = stats
        self.diag = diag

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get_recommendations(self) -> List[Dict[str, Any]]:
        recs = []
        metrics = self.stats.get_metrics()
        diagnostics = self.diag.get_diagnostics()

        if not diagnostics["redis_connected"]:
            recs.append(
                {
                    "category": "Connectivity",
                    "issue": "Redis backend is disconnected.",
                    "suggestion": "Start Redis server or verify host configuration to enable hardware acceleration.",
                    "severity": "WARNING",
                }
            )

        total = metrics["cache_hits"] + metrics["cache_misses"]
        if total > 5 and metrics["hit_ratio"] < 0.2:
            recs.append(
                {
                    "category": "Efficiency",
                    "issue": f"Cache hit ratio is very low ({metrics['hit_ratio']:.1%}).",
                    "suggestion": "Increase configured TTL values or trigger startup warmup to prepopulate cache.",
                    "severity": "WARNING",
                }
            )

        if metrics["ttl_expirations"] > 10:
            recs.append(
                {
                    "category": "TTL Configuration",
                    "issue": f"High number of TTL expirations ({metrics['ttl_expirations']}).",
                    "suggestion": "Consider increasing TTL limits for relatively static metadata (e.g. Workspace metadata).",
                    "severity": "INFO",
                }
            )

        if not recs:
            recs.append(
                {
                    "category": "Maintenance",
                    "issue": "Cache is performing optimally.",
                    "suggestion": "Keep active settings.",
                    "severity": "INFO",
                }
            )

        for r in recs:
            self.stats.record_recommendation(r)

        return recs


class CacheInvalidationManagerImpl(CacheInvalidationManager):
    def __init__(self, provider: RedisProvider, stats: CacheStatisticsCollector) -> None:
        self.provider = provider
        self.stats = stats

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def make_key(self, subsystem: str, entity_id: str) -> str:
        context = RuntimeCorrelationManager.get_context()
        workspace = context.get("workspace_id") or "default_workspace"
        project = context.get("project_id") or "default_project"
        return f"aios:v1:{workspace}:{project}:{subsystem}:{entity_id}:cache"

    def invalidate_key(self, key: str) -> bool:
        try:
            success = self.provider.delete(key)
            if success:
                self.stats.record_invalidation(1)
            return success
        except Exception:
            return False

    def invalidate_entity(self, subsystem: str, entity_id: str) -> bool:
        key = self.make_key(subsystem, entity_id)
        return self.invalidate_key(key)

    def invalidate_workspace(self, workspace_id: str) -> int:
        pattern = f"aios:v1:{workspace_id}:*:*:*:*"
        return self.invalidate_pattern(pattern)

    def invalidate_project(self, project_id: str) -> int:
        pattern = f"aios:v1:*:{project_id}:*:*:*"
        return self.invalidate_pattern(pattern)

    def invalidate_provider(self, provider_name: str) -> int:
        pattern = f"aios:v1:*:*:provider_*:{provider_name}:*"
        return self.invalidate_pattern(pattern)

    def invalidate_pattern(self, pattern: str) -> int:
        count = 0
        try:
            keys = self.provider.transport.execute_command("keys", pattern)
            if keys:
                for k in keys:
                    if self.provider.delete(k):
                        count += 1
        except Exception:
            pass
        if count > 0:
            self.stats.record_invalidation(count)
        return count

    def invalidate_bulk(self, keys: List[str]) -> int:
        count = 0
        for k in keys:
            try:
                if self.provider.delete(k):
                    count += 1
            except Exception:
                pass
        if count > 0:
            self.stats.record_invalidation(count)
        return count


class CacheWarmupServiceImpl(CacheWarmupService):
    def __init__(
        self,
        service: PersistenceService,
        cache_service: RedisCacheService,
        stats: CacheStatisticsCollector,
    ) -> None:
        self.service = service
        self.cache_service = cache_service
        self.stats = stats

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def warmup_all_background(self) -> None:
        import threading

        thread = threading.Thread(target=self._run_warmup, daemon=True)
        thread.start()

    def _run_warmup(self) -> None:
        subsystems = [
            "workspace",
            "configuration",
            "profile",
            "provider_capabilities",
            "provider_health",
            "provider_routing",
        ]
        for sub in subsystems:
            try:
                self.warm_subsystem(sub)
            except Exception:
                pass

    def warm_subsystem(self, subsystem: str) -> None:
        count = 0
        if subsystem == "workspace":
            try:
                rows = self.service.execute(
                    "SELECT * FROM workspaces ORDER BY last_accessed DESC LIMIT 5"
                )
                for r in rows:
                    row = dict(r)
                    row["metadata"] = json.loads(row["metadata"] or "{}")
                    self.cache_service.set("workspace", row["id"], row)
                    count += 1
            except Exception:
                pass
        elif subsystem == "profile":
            try:
                rows = self.service.execute(
                    "SELECT * FROM engineering_profiles ORDER BY timestamp DESC LIMIT 5"
                )
                for r in rows:
                    row = dict(r)
                    row["coding_standards"] = json.loads(row["coding_standards"] or "[]")
                    row["naming_conventions"] = json.loads(row["naming_conventions"] or "{}")
                    row["release_formatting_rules"] = json.loads(
                        row["release_formatting_rules"] or "{}"
                    )
                    row["markdown_preferences"] = json.loads(row["markdown_preferences"] or "{}")
                    row["section_ordering"] = json.loads(row["section_ordering"] or "[]")
                    row["doc_naming_conventions"] = json.loads(
                        row["doc_naming_conventions"] or "{}"
                    )
                    row["doc_versioning_preferences"] = json.loads(
                        row["doc_versioning_preferences"] or "{}"
                    )
                    row["exclude_patterns"] = json.loads(row["exclude_patterns"] or "[]")
                    row["sandbox_enabled"] = bool(row["sandbox_enabled"])
                    row["generate_api_docs"] = bool(row["generate_api_docs"])
                    row["auto_release"] = bool(row["auto_release"])
                    self.cache_service.set("profile", row["id"], row)
                    count += 1
            except Exception:
                pass
        elif subsystem == "configuration":
            try:
                rows = self.service.execute("SELECT * FROM configuration_profiles LIMIT 5")
                for r in rows:
                    row = dict(r)
                    row["env_profile"] = json.loads(row["env_profile"] or "{}")
                    row["workspace_settings"] = json.loads(row["workspace_settings"] or "{}")
                    row["provider_preferences"] = json.loads(row["provider_preferences"] or "{}")
                    row["git_preferences"] = json.loads(row["git_preferences"] or "{}")
                    row["automation_preferences"] = json.loads(
                        row["automation_preferences"] or "{}"
                    )
                    row["documentation_preferences"] = json.loads(
                        row["documentation_preferences"] or "{}"
                    )
                    row["testing_preferences"] = json.loads(row["testing_preferences"] or "{}")
                    row["approval_preferences"] = json.loads(row["approval_preferences"] or "{}")
                    self.cache_service.set("configuration", row["id"], row)
                    count += 1
            except Exception:
                pass
        elif subsystem == "provider_capabilities":
            try:
                rows = self.service.execute(
                    "SELECT * FROM provider_capabilities ORDER BY timestamp DESC LIMIT 5"
                )
                for r in rows:
                    row = dict(r)
                    row["capabilities"] = json.loads(row["capabilities"] or "{}")
                    res = PersistenceResult(
                        status=PersistenceStatus.SUCCESS,
                        message="Capabilities retrieved.",
                        provider=self.service.config.provider_name,
                        latency=0.0,
                        repository="provider_capabilities",
                        payload=row,
                    )
                    self.cache_service.set("provider_capabilities", row["id"], res)
                    count += 1
            except Exception:
                pass
        elif subsystem == "provider_health":
            try:
                rows = self.service.execute(
                    "SELECT * FROM provider_health ORDER BY timestamp DESC LIMIT 5"
                )
                for r in rows:
                    row = dict(r)
                    row["is_healthy"] = bool(row["is_healthy"])
                    res = PersistenceResult(
                        status=PersistenceStatus.SUCCESS,
                        message="Health report retrieved.",
                        provider=self.service.config.provider_name,
                        latency=0.0,
                        repository="provider_health",
                        payload=row,
                    )
                    self.cache_service.set("provider_health", row["id"], res)
                    count += 1
            except Exception:
                pass
        elif subsystem == "provider_routing":
            try:
                rows = self.service.execute(
                    "SELECT * FROM provider_routing ORDER BY timestamp DESC LIMIT 5"
                )
                for r in rows:
                    row = dict(r)
                    row["routing_candidates"] = json.loads(row["routing_candidates"] or "[]")
                    res = PersistenceResult(
                        status=PersistenceStatus.SUCCESS,
                        message="Routing decision retrieved.",
                        provider=self.service.config.provider_name,
                        latency=0.0,
                        repository="provider_routing",
                        payload=row,
                    )
                    self.cache_service.set("provider_routing", row["id"], res)
                    count += 1
            except Exception:
                pass

        if count > 0:
            self.stats.record_warmup(count)


class CacheRebuildServiceImpl(CacheRebuildService):
    def __init__(
        self,
        service: PersistenceService,
        provider: RedisProvider,
        stats: CacheStatisticsCollector,
        warmup_svc: CacheWarmupService,
    ) -> None:
        self.service = service
        self.provider = provider
        self.stats = stats
        self.warmup_svc = warmup_svc
        self._rebuilding = False

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def trigger_rebuild_background(self) -> None:
        if self._rebuilding:
            return
        import threading

        thread = threading.Thread(target=self._run_rebuild, daemon=True)
        thread.start()

    def _run_rebuild(self) -> None:
        self._rebuilding = True
        try:
            try:
                self.provider.transport.connect()
            except Exception:
                pass

            if self.provider.transport.is_connected():
                self.rebuild_incremental()
        finally:
            self._rebuilding = False

    def rebuild_incremental(self) -> int:
        initial_warmups = self.stats.warmups
        self.warmup_svc.warm_subsystem("workspace")
        self.warmup_svc.warm_subsystem("profile")
        self.warmup_svc.warm_subsystem("configuration")
        self.warmup_svc.warm_subsystem("provider_capabilities")
        self.warmup_svc.warm_subsystem("provider_health")
        self.warmup_svc.warm_subsystem("provider_routing")

        rebuilt_keys = self.stats.warmups - initial_warmups
        if rebuilt_keys > 0:
            self.stats.record_rebuild(rebuilt_keys)
        return rebuilt_keys


class RedisCacheServiceImpl(RedisCacheService):
    def __init__(
        self,
        provider: RedisProvider,
        policy_mgr: CachePolicyManager,
        stats: CacheStatisticsCollector,
        diag: CacheDiagnostics,
    ) -> None:
        self.provider = provider
        self.policy_mgr = policy_mgr
        self.stats = stats
        self.diag = diag
        self._disabled = False

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def make_key(self, subsystem: str, entity_id: str) -> str:
        context = RuntimeCorrelationManager.get_context()
        workspace = context.get("workspace_id") or "default_workspace"
        project = context.get("project_id") or "default_project"
        return f"aios:v1:{workspace}:{project}:{subsystem}:{entity_id}:cache"

    def get(
        self,
        subsystem: str,
        entity_id: str,
        fetch_func: Callable[[], Any],
        policy: Optional[CachePolicy] = None,
        ttl: Optional[int] = None,
    ) -> Any:
        start_time = time.time()
        active_policy = policy if policy is not None else self.policy_mgr.get_policy(subsystem)
        active_ttl = ttl if ttl is not None else self.policy_mgr.get_ttl(subsystem)

        if active_policy == CachePolicy.NO_CACHE or self._disabled:
            return fetch_func()

        key = self.make_key(subsystem, entity_id)
        context = RuntimeCorrelationManager.get_context()
        corr_id = context.get("correlation_id")

        try:
            cached_val = self.provider.get(key)
            if cached_val is not None:
                latency_ms = (time.time() - start_time) * 1000.0
                self.stats.record_hit(subsystem, latency_ms, corr_id)
                return deserialize_val(cached_val)
        except Exception as e:
            self.diag.log_error(
                f"Cache get error: {str(e)}",
                severity="ERROR",
                remediation="Verify Redis connection",
            )

        latency_ms = (time.time() - start_time) * 1000.0
        self.stats.record_miss(subsystem, latency_ms, corr_id)

        db_val = fetch_func()

        if db_val is not None and (
            active_policy == CachePolicy.READ_THROUGH or active_policy == CachePolicy.CACHE_ASIDE
        ):
            try:
                self.provider.set(key, serialize_val(db_val), ttl=active_ttl)
            except Exception as e:
                self.diag.log_error(
                    f"Cache set error: {str(e)}",
                    severity="ERROR",
                    remediation="Verify Redis connection",
                )

        return db_val

    def set(
        self,
        subsystem: str,
        entity_id: str,
        value: Any,
        policy: Optional[CachePolicy] = None,
        ttl: Optional[int] = None,
    ) -> bool:
        active_policy = policy if policy is not None else self.policy_mgr.get_policy(subsystem)
        active_ttl = ttl if ttl is not None else self.policy_mgr.get_ttl(subsystem)

        if active_policy == CachePolicy.NO_CACHE or self._disabled:
            return False

        key = self.make_key(subsystem, entity_id)

        try:
            success = self.provider.set(key, serialize_val(value), ttl=active_ttl)
            return success
        except Exception as e:
            self.diag.log_error(
                f"Cache set error: {str(e)}",
                severity="ERROR",
                remediation="Verify Redis connection",
            )
            return False

    def delete(self, subsystem: str, entity_id: str) -> bool:
        key = self.make_key(subsystem, entity_id)
        try:
            return self.provider.delete(key)
        except Exception as e:
            self.diag.log_error(
                f"Cache delete error: {str(e)}",
                severity="ERROR",
                remediation="Verify Redis connection",
            )
            return False

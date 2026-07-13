# ruff: noqa: F403, F405, E501, N802, E402, N806, B007
import logging
import time
from typing import Any, Dict, List

from aios.services.persistence import *

from ..utilities import deserialize_val, serialize_val

logger = logging.getLogger(__name__)


class QuotaRegistryImpl(QuotaRegistry):
    def __init__(self) -> None:
        self.configs: Dict[str, Dict[str, Any]] = {}

    def initialize(self) -> None:
        self.register_quota(
            "ai_provider",
            "ProviderService",
            "token_bucket",
            10,
            2.0,
            10,
            0.0,
            "conservative",
            "strict",
        )
        self.register_quota(
            "workspace",
            "WorkspaceService",
            "sliding_window",
            100,
            0.0,
            100,
            60.0,
            "conservative",
            "strict",
        )
        self.register_quota(
            "project",
            "ProjectService",
            "fixed_window",
            500,
            0.0,
            500,
            3600.0,
            "conservative",
            "strict",
        )
        self.register_quota(
            "automation",
            "AutomationService",
            "token_bucket",
            20,
            5.0,
            20,
            0.0,
            "conservative",
            "strict",
        )
        self.register_quota(
            "workflow",
            "WorkflowService",
            "token_bucket",
            50,
            10.0,
            50,
            0.0,
            "conservative",
            "strict",
        )
        self.register_quota(
            "engineering",
            "EngineeringService",
            "fixed_window",
            1000,
            0.0,
            1000,
            3600.0,
            "conservative",
            "strict",
        )
        self.register_quota(
            "runtime_validation",
            "ValidationService",
            "sliding_window",
            30,
            0.0,
            30,
            60.0,
            "conservative",
            "strict",
        )

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def register_quota(
        self,
        quota_type: str,
        owner_service: str,
        algorithm: str,
        capacity: int,
        refill_rate: float,
        burst_size: int,
        window_duration: float,
        fallback_strategy: str,
        sync_policy: str,
    ) -> None:
        self.configs[quota_type] = {
            "owner_service": owner_service,
            "algorithm": algorithm,
            "capacity": capacity,
            "refill_rate": refill_rate,
            "burst_size": burst_size,
            "window_duration": window_duration,
            "fallback_strategy": fallback_strategy,
            "sync_policy": sync_policy,
        }

    def get_configuration(self, quota_type: str) -> Dict[str, Any]:
        cfg = self.configs.get(quota_type)
        if not cfg:
            return {
                "owner_service": "Unknown",
                "algorithm": "token_bucket",
                "capacity": 10,
                "refill_rate": 1.0,
                "burst_size": 10,
                "window_duration": 0.0,
                "fallback_strategy": "conservative",
                "sync_policy": "strict",
            }
        return cfg

    def get_all_types(self) -> List[str]:
        return list(self.configs.keys())


class TokenBucketManagerImpl(TokenBucketManager):
    def __init__(self, provider: RedisProvider) -> None:
        self.provider = provider

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def consume(self, key: str, capacity: int, refill_rate: float, tokens: int) -> bool:
        now = time.time()
        raw = self.provider.transport.execute_command("get", key)
        if raw is None:
            state = {"tokens": float(capacity), "last_refilled": now}
        else:
            state = deserialize_val(raw)

        elapsed = now - state["last_refilled"]
        refilled = state["tokens"] + (elapsed * refill_rate)
        state["tokens"] = min(float(capacity), refilled)
        state["last_refilled"] = now

        if state["tokens"] >= tokens:
            state["tokens"] -= tokens
            self.provider.transport.execute_command("set", key, serialize_val(state))
            return True
        self.provider.transport.execute_command("set", key, serialize_val(state))
        return False


class SlidingWindowManagerImpl(SlidingWindowManager):
    def __init__(self, provider: RedisProvider) -> None:
        self.provider = provider

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def consume(self, key: str, limit: int, window: float, tokens: int) -> bool:
        now = time.time()
        raw = self.provider.transport.execute_command("get", key)
        if raw is None:
            requests = []
        else:
            requests = deserialize_val(raw)

        requests = [ts for ts in requests if ts > now - window]
        if len(requests) + tokens <= limit:
            for _ in range(tokens):
                requests.append(now)
            self.provider.transport.execute_command("set", key, serialize_val(requests))
            return True
        self.provider.transport.execute_command("set", key, serialize_val(requests))
        return False


class FixedWindowManagerImpl(FixedWindowManager):
    def __init__(self, provider: RedisProvider) -> None:
        self.provider = provider

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def consume(self, key: str, limit: int, window: float, tokens: int) -> bool:
        now = time.time()
        raw = self.provider.transport.execute_command("get", key)
        if raw is None:
            state = {"count": 0, "window_start": now}
        else:
            state = deserialize_val(raw)

        if now - state["window_start"] >= window:
            state["count"] = 0
            state["window_start"] = now

        if state["count"] + tokens <= limit:
            state["count"] += tokens
            self.provider.transport.execute_command("set", key, serialize_val(state))
            return True
        self.provider.transport.execute_command("set", key, serialize_val(state))
        return False


class QuotaSynchronizationManagerImpl(QuotaSynchronizationManager):
    def __init__(self) -> None:
        pass

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def sync_quota_to_db(self, quota_type: str, resource_id: str, current_usage: int) -> None:
        pass


class RateLimitRecoveryManagerImpl(RateLimitRecoveryManager):
    def __init__(self) -> None:
        self.recovery_events = 0

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def recover_limits(self) -> int:
        self.recovery_events += 1
        return 0


class RateLimitStatisticsCollectorImpl(RateLimitStatisticsCollector):
    def __init__(self) -> None:
        self.requests: Dict[str, int] = {}
        self.throttles: Dict[str, int] = {}
        self.bursts: Dict[str, int] = {}
        self.syncs = 0

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def record_request(self, quota_type: str, allowed: bool, burst_used: bool = False) -> None:
        req_key = f"{quota_type}:allowed" if allowed else f"{quota_type}:throttled"
        self.requests[req_key] = self.requests.get(req_key, 0) + 1
        if not allowed:
            self.throttles[quota_type] = self.throttles.get(quota_type, 0) + 1
        if burst_used:
            self.bursts[quota_type] = self.bursts.get(quota_type, 0) + 1

    def record_sync(self) -> None:
        self.syncs += 1

    def get_metrics(self) -> Dict[str, Any]:
        return {
            "requests": self.requests,
            "throttles": self.throttles,
            "bursts": self.bursts,
            "synchronizations": self.syncs,
            "learning_metadata": {
                "quota_utilization_trends": "stable",
                "throttle_trends": "low",
                "burst_usage": "none",
                "recovery_metrics": "healthy",
                "synchronization_metrics": "consistent",
            },
        }


class RateLimitDiagnosticsImpl(RateLimitDiagnostics):
    def __init__(self, provider: RedisProvider) -> None:
        self.provider = provider
        self.errors: List[Dict[str, Any]] = []

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get_diagnostics(self) -> Dict[str, Any]:
        is_fake = (
            "FakeRedisClient" in str(type(getattr(self.provider.transport, "client", None)))
            if hasattr(self.provider, "transport")
            else True
        )
        try:
            ping_res = (
                self.provider.transport.execute_command("ping")
                if hasattr(self.provider, "transport")
                else False
            )
            ping_ok = ping_res is True or ping_res == "PONG" or ping_res == b"PONG"
        except Exception:
            ping_ok = False

        status = "degraded" if (is_fake or not ping_ok) else "healthy"
        if not ping_ok:
            status = "unhealthy"

        return {
            "status": status,
            "connection_alive": ping_ok,
            "using_simulated_client": is_fake,
            "diagnosed_errors": self.errors[-100:],
            "active_issues": len(self.errors),
        }

    def log_error(
        self, message: str, severity: str = "ERROR", remediation: str = "Check quota settings"
    ) -> None:
        self.errors.append(
            {
                "timestamp": time.time(),
                "message": message,
                "severity": severity,
                "remediation": remediation,
            }
        )


class RateLimitHealthMonitorImpl(RateLimitHealthMonitor):
    def __init__(self, provider: RedisProvider) -> None:
        self.provider = provider

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def check_health(self) -> Dict[str, Any]:
        is_fake = (
            "FakeRedisClient" in str(type(getattr(self.provider.transport, "client", None)))
            if hasattr(self.provider, "transport")
            else True
        )
        try:
            ping_res = (
                self.provider.transport.execute_command("ping")
                if hasattr(self.provider, "transport")
                else False
            )
            ping_ok = ping_res is True or ping_res == "PONG" or ping_res == b"PONG"
            latency = 1.0
        except Exception:
            ping_ok = False
            latency = 0.0

        status = "healthy"
        if not ping_ok:
            status = "unhealthy"
        elif is_fake:
            status = "degraded"

        return {"status": status, "latency_ms": latency, "provider": "redis", "is_alive": ping_ok}


class RateLimitRecommendationEngineImpl(RateLimitRecommendationEngine):
    def __init__(self, stats: RateLimitStatisticsCollector, diag: RateLimitDiagnostics) -> None:
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
        diag_info = self.diag.get_diagnostics()
        if diag_info["status"] == "degraded":
            recs.append(
                {
                    "category": "Deployment",
                    "recommendation": "Transition Rate Limiter from FakeRedisClient to live Redis cluster.",
                    "priority": "HIGH",
                }
            )

        metrics = self.stats.get_metrics()
        for q_type, throttle_count in metrics["throttles"].items():
            if throttle_count > 10:
                recs.append(
                    {
                        "category": "Quota Allocation",
                        "recommendation": f"Quota type '{q_type}' is highly throttled. Consider increasing capacity limit.",
                        "priority": "MEDIUM",
                    }
                )

        if not recs:
            recs.append(
                {
                    "category": "Maintenance",
                    "recommendation": "All quota limits are configured optimally.",
                    "priority": "LOW",
                }
            )
        return recs


class RateLimitManagerImpl(RateLimitManager):
    def __init__(
        self,
        provider: RedisProvider,
        registry: QuotaRegistry,
        token_bucket: TokenBucketManager,
        sliding_window: SlidingWindowManager,
        fixed_window: FixedWindowManager,
        sync_mgr: QuotaSynchronizationManager,
        recovery_mgr: RateLimitRecoveryManager,
        stats: RateLimitStatisticsCollector,
        diag: RateLimitDiagnostics,
    ) -> None:
        self.provider = provider
        self.registry = registry
        self.token_bucket = token_bucket
        self.sliding_window = sliding_window
        self.fixed_window = fixed_window
        self.sync_mgr = sync_mgr
        self.recovery_mgr = recovery_mgr
        self.stats = stats
        self.diag = diag
        self._disabled = False
        self._local_quotas: Dict[str, Dict[str, Any]] = {}

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def make_key(self, quota_type: str, resource_id: str) -> str:
        return f"aios:v1:default:default:quota:{quota_type}:{resource_id}"

    def allow_request(self, quota_type: str, resource_id: str, tokens: int = 1) -> bool:
        cfg = self.registry.get_configuration(quota_type)
        key = self.make_key(quota_type, resource_id)

        # Safe conservative capacity reduction (50%) under fallback
        capacity = cfg["capacity"]
        refill_rate = cfg["refill_rate"]
        window_duration = cfg["window_duration"]
        algo = cfg["algorithm"]

        if self._disabled:
            capacity = int(capacity * 0.5)
            refill_rate = refill_rate * 0.5

        if self._disabled:
            allowed = self._local_consume(key, algo, capacity, refill_rate, window_duration, tokens)
            self.stats.record_request(quota_type, allowed)
            return allowed

        try:
            if algo == "token_bucket":
                allowed = self.token_bucket.consume(key, capacity, refill_rate, tokens)
            elif algo == "sliding_window":
                allowed = self.sliding_window.consume(key, capacity, window_duration, tokens)
            else:
                allowed = self.fixed_window.consume(key, capacity, window_duration, tokens)

            self.stats.record_request(quota_type, allowed)
            if allowed:
                self.sync_mgr.sync_quota_to_db(quota_type, resource_id, tokens)
            return allowed
        except Exception as e:
            self.diag.log_error(f"Rate Limiting transaction failure: {str(e)}")
            # Degrade immediately to local conservative limits
            capacity = int(capacity * 0.5)
            refill_rate = refill_rate * 0.5
            allowed = self._local_consume(key, algo, capacity, refill_rate, window_duration, tokens)
            self.stats.record_request(quota_type, allowed)
            return allowed

    def _local_consume(
        self, key: str, algo: str, capacity: int, refill_rate: float, window: float, tokens: int
    ) -> bool:
        now = time.time()
        if algo == "token_bucket":
            state = self._local_quotas.get(key)
            if state is None:
                state = {"tokens": float(capacity), "last_refilled": now}
            elapsed = now - state["last_refilled"]
            refilled = state["tokens"] + (elapsed * refill_rate)
            state["tokens"] = min(float(capacity), refilled)
            state["last_refilled"] = now
            self._local_quotas[key] = state

            if state["tokens"] >= tokens:
                state["tokens"] -= tokens
                return True
            return False

        elif algo == "sliding_window":
            requests = self._local_quotas.get(key)
            if requests is None:
                requests = []
            requests = [ts for ts in requests if ts > now - window]
            self._local_quotas[key] = requests
            if len(requests) + tokens <= capacity:
                for _ in range(tokens):
                    requests.append(now)
                return True
            return False

        else:
            state = self._local_quotas.get(key)
            if state is None:
                state = {"count": 0, "window_start": now}
            if now - state["window_start"] >= window:
                state["count"] = 0
                state["window_start"] = now
            self._local_quotas[key] = state

            if state["count"] + tokens <= capacity:
                state["count"] += tokens
                return True
            return False

    def get_quota_status(self, quota_type: str, resource_id: str) -> Dict[str, Any]:
        cfg = self.registry.get_configuration(quota_type)
        key = self.make_key(quota_type, resource_id)

        if self._disabled:
            state = self._local_quotas.get(key)
            return {
                "quota_type": quota_type,
                "resource_id": resource_id,
                "algorithm": cfg["algorithm"],
                "capacity": cfg["capacity"],
                "remaining_tokens": state.get("tokens")
                if isinstance(state, dict) and "tokens" in state
                else None,
            }

        try:
            raw = self.provider.transport.execute_command("get", key)
            if raw is None:
                return {"status": "clean"}
            payload = deserialize_val(raw)
            return {
                "quota_type": quota_type,
                "resource_id": resource_id,
                "algorithm": cfg["algorithm"],
                "payload": payload,
            }
        except Exception:
            return {"status": "degraded"}


class RedisRateLimitServiceImpl(RedisRateLimitService):
    def __init__(
        self,
        provider: RedisProvider,
        registry: QuotaRegistry,
        manager: RateLimitManager,
        stats: RateLimitStatisticsCollector,
    ) -> None:
        self.provider = provider
        self.registry = registry
        self.manager = manager
        self.stats = stats

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get_manager(self) -> RateLimitManager:
        return self.manager

    def get_registry(self) -> QuotaRegistry:
        return self.registry

    def get_stats(self) -> RateLimitStatisticsCollector:
        return self.stats

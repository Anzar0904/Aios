# ruff: noqa: F403, F405, E501, N802, E402, N806, B007
import logging
import os
import time
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle
from aios.services.persistence import *

from ..intelligence import get_unified_ri

logger = logging.getLogger(__name__)

class RedisConfigurationService(ServiceLifecycle):
    def __init__(self) -> None:
        self.host = os.environ.get("REDIS_HOST")
        try:
            self.port = int(os.environ.get("REDIS_PORT", 6379))
        except ValueError:
            self.port = 6379
        self.username = os.environ.get("REDIS_USERNAME")
        self.password = os.environ.get("REDIS_PASSWORD")
        try:
            self.database = int(os.environ.get("REDIS_DATABASE", 0))
        except ValueError:
            self.database = 0
        self.tls = os.environ.get("REDIS_TLS", "false").lower() == "true"
        try:
            self.timeout = float(os.environ.get("REDIS_TIMEOUT", 2.0))
        except ValueError:
            self.timeout = 2.0
        try:
            self.max_connections = int(os.environ.get("REDIS_MAX_CONNECTIONS", 10))
        except ValueError:
            self.max_connections = 10
        self.awaiting_configuration = not self.host
        self.environment = os.environ.get("AIOS_ENV", "production").lower()
        self.fallback_enabled = os.environ.get("REDIS_FALLBACK_ENABLED", "false").lower() == "true"

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass


class FakeRedisClient:
    def __init__(self, *args, **kwargs) -> None:
        self._data: Dict[str, str] = {}
        self._expires: Dict[str, float] = {}

    def ping(self) -> bool:
        return True

    def get(self, key: str) -> Optional[str]:
        if key in self._expires and time.time() > self._expires[key]:
            del self._data[key]
            del self._expires[key]
            return None
        return self._data.get(key)

    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        self._data[key] = str(value)
        if ex is not None:
            self._expires[key] = time.time() + ex
        else:
            if key in self._expires:
                del self._expires[key]
        return True

    def delete(self, key: str) -> bool:
        existed = key in self._data
        if key in self._data:
            del self._data[key]
        if key in self._expires:
            del self._expires[key]
        return existed

    def exists(self, key: str) -> bool:
        self.get(key)  # trigger expiry
        return key in self._data

    def keys(self, pattern: str = "*") -> List[str]:
        import fnmatch

        now = time.time()
        expired = [k for k, exp in self._expires.items() if now > exp]
        for k in expired:
            if k in self._data:
                del self._data[k]
            if k in self._expires:
                del self._expires[k]
        return [k for k in self._data.keys() if fnmatch.fnmatch(k, pattern)]


class RedisConnectionManager(ServiceLifecycle):
    def __init__(self, config: RedisConfigurationService) -> None:
        self.config = config
        self.client: Any = None
        self.connection_failures = 0
        self.retries = 0

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def connect(self) -> Any:
        if self.config.awaiting_configuration:
            logger.warning("Redis is not configured (awaiting configuration). Falling back to FakeRedisClient local mode.")
            self.client = FakeRedisClient()
            return self.client

        is_prod = self.config.environment == "production"
        primary_error = None

        try:
            import redis

            self.client = redis.Redis(
                host=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                db=self.config.database,
                ssl=self.config.tls,
                socket_timeout=self.config.timeout,
                max_connections=self.config.max_connections,
                decode_responses=True,
            )
            self.retries += 1
            if self.client.ping():
                self.connection_failures = 0
                logger.info("Successfully connected to Redis server.")
                return self.client
        except Exception as e:
            primary_error = e

        if not is_prod or self.config.fallback_enabled:
            error_reason = primary_error or "Redis ping failed"
            logger.warning(
                f"Redis connection failed ({error_reason}). "
                "Falling back to FakeRedisClient local mode."
            )
            self.client = FakeRedisClient()
            self.connection_failures += 1
            return self.client
        else:
            self.connection_failures += 1
            error_reason = primary_error or RuntimeError("Redis ping failed")
            logger.error(
                f"Redis connection failed ({error_reason}) and fallback is disabled "
                f"in environment '{self.config.environment}'."
            )
            if isinstance(error_reason, Exception):
                raise error_reason
            raise RuntimeError(str(error_reason))


class RedisTransportImpl(RedisTransport):
    def __init__(
        self, config: RedisConfigurationService, conn_manager: RedisConnectionManager
    ) -> None:
        self.config = config
        self.conn_manager = conn_manager
        self.client: Any = None

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def connect(self) -> None:
        self.client = self.conn_manager.connect()

    def disconnect(self) -> None:
        self.client = None

    def is_connected(self) -> bool:
        if not self.client:
            return False
        try:
            return self.client.ping()
        except Exception:
            return False

    def execute_command(self, cmd: str, *args: Any, **kwargs: Any) -> Any:
        if not self.client:
            self.connect()
        if not self.client:
            raise RuntimeError("Redis transport is not connected")

        start_time = time.time()
        success = True
        try:
            fn = getattr(self.client, cmd.lower())
            return fn(*args, **kwargs)
        except Exception as e:
            success = False
            raise e
        finally:
            duration_ms = (time.time() - start_time) * 1000.0
            ri = get_unified_ri()
            if ri:
                try:
                    ri.telemetry.record_query(duration_ms, success)
                except Exception:
                    pass


class RedisProviderImpl(RedisProvider):
    def __init__(self, transport: RedisTransport) -> None:
        self.transport = transport

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get(self, key: str) -> Optional[str]:
        try:
            return self.transport.execute_command("get", key)
        except Exception:
            return None

    def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        try:
            return bool(self.transport.execute_command("set", key, value, ex=ttl))
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        try:
            return bool(self.transport.execute_command("delete", key))
        except Exception:
            return False

    def exists(self, key: str) -> bool:
        try:
            return bool(self.transport.execute_command("exists", key))
        except Exception:
            return False



class RedisRuntimeServiceImpl(RedisRuntimeService, ServiceLifecycle):
    def __init__(
        self,
        config: RedisConfigurationService,
        transport: RedisTransport,
        provider: RedisProvider,
        health: RedisHealthMonitor,
        diag: RedisDiagnostics,
        telemetry: RedisTelemetry,
        stats: RedisStatistics,
        validator: RedisValidator,
        report_gen: RedisReportGenerator,
    ) -> None:
        self.config = config
        self.transport = transport
        self.provider = provider
        self.health_monitor = health
        self.diagnostics_engine = diag
        self.telemetry = telemetry
        self.stats_engine = stats
        self.validator = validator
        self.report_gen = report_gen

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def get_health(self) -> Dict[str, Any]:
        return self.health_monitor.check_health()

    def get_diagnostics(self) -> Dict[str, Any]:
        return self.diagnostics_engine.get_diagnostics()

    def get_telemetry(self) -> Dict[str, Any]:
        return {
            "queries_recorded": self.telemetry.queries_recorded,
            "failed_queries": self.telemetry.failed_queries,
        }

    def get_statistics(self) -> Dict[str, Any]:
        return self.stats_engine.get_metrics()

    def get_recommendations(self) -> List[Dict[str, Any]]:
        recs = []
        diag = self.get_diagnostics()
        if diag["status"] == "degraded":
            recs.append(
                {
                    "category": "Configuration",
                    "issue": "Redis is awaiting configuration or offline.",
                    "suggestion": "Check environment parameters or server connection state.",
                    "severity": "WARNING",
                }
            )
        if not recs:
            recs.append(
                {
                    "category": "Maintenance",
                    "issue": "No anomalies detected.",
                    "suggestion": "Platform performing normally.",
                    "severity": "INFO",
                }
            )
        return recs

    def format_key(
        self, workspace: str, project: str, subsystem: str, entity: str, purpose: str
    ) -> str:
        return f"aios:v1:{workspace}:{project}:{subsystem}:{entity}:{purpose}"

    def get_learning_payload(self) -> Dict[str, Any]:
        return {
            "runtime_statistics": self.get_statistics(),
            "connection_statistics": {
                "failures": self.diagnostics_engine.conn_manager.connection_failures,
                "retries": self.diagnostics_engine.conn_manager.retries,
            },
            "recommendations": self.get_recommendations(),
        }

    def generate_reports(self) -> None:
        self.report_gen.generate_reports()



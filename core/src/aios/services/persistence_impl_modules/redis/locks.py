# ruff: noqa: F403, F405, E501, N802, E402, N806, B007
import logging
import time
from typing import Any, Dict, List, Optional

from aios.services.persistence import *

from ..utilities import deserialize_val, serialize_val

logger = logging.getLogger(__name__)


class LockRegistryImpl(LockRegistry):
    def __init__(self) -> None:
        self.configs: Dict[str, Dict[str, Any]] = {}

    def initialize(self) -> None:
        # Pre-register default lock types
        self.register_lock_type(
            "workspace", "WorkspaceService", "workspace", 60.0, "heartbeat", 10.0, "none", {}, {}
        )
        self.register_lock_type(
            "workflow", "WorkflowService", "workflow", 120.0, "heartbeat", 30.0, "rebuild", {}, {}
        )
        self.register_lock_type(
            "automation",
            "AutomationService",
            "automation",
            30.0,
            "heartbeat",
            5.0,
            "rebuild",
            {},
            {},
        )
        self.register_lock_type(
            "provider", "ProviderService", "provider", 15.0, "heartbeat", 2.0, "none", {}, {}
        )
        self.register_lock_type(
            "engineering",
            "EngineeringProfileService",
            "engineering",
            300.0,
            "heartbeat",
            60.0,
            "none",
            {},
            {},
        )
        self.register_lock_type(
            "configuration",
            "ConfigurationService",
            "configuration",
            60.0,
            "heartbeat",
            10.0,
            "none",
            {},
            {},
        )
        self.register_lock_type(
            "temporary_execution",
            "ExecutionService",
            "temp_exec",
            10.0,
            "heartbeat",
            1.0,
            "none",
            {},
            {},
        )

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def register_lock_type(
        self,
        lock_type: str,
        owner_service: str,
        redis_prefix: str,
        lease_duration: float,
        renewal_strategy: str,
        timeout: float,
        recovery_strategy: str,
        deadlock_rules: Dict[str, Any],
        retry_policy: Dict[str, Any],
    ) -> None:
        self.configs[lock_type] = {
            "owner_service": owner_service,
            "redis_prefix": redis_prefix,
            "lease_duration": lease_duration,
            "renewal_strategy": renewal_strategy,
            "timeout": timeout,
            "recovery_strategy": recovery_strategy,
            "deadlock_rules": deadlock_rules,
            "retry_policy": retry_policy,
        }

    def get_configuration(self, lock_type: str) -> Dict[str, Any]:
        cfg = self.configs.get(lock_type)
        if not cfg:
            # Pluggable future lock type support
            return {
                "owner_service": "Unknown",
                "redis_prefix": lock_type,
                "lease_duration": 60.0,
                "renewal_strategy": "heartbeat",
                "timeout": 10.0,
                "recovery_strategy": "none",
                "deadlock_rules": {},
                "retry_policy": {},
            }
        return cfg

    def get_all_types(self) -> List[str]:
        return list(self.configs.keys())


class LockLeaseManagerImpl(LockLeaseManager):
    def __init__(
        self,
        provider: RedisProvider,
        registry: LockRegistry,
        deadlock: DeadlockDetector,
        stats: CoordinationStatisticsCollector,
        diag: CoordinationDiagnostics,
    ) -> None:
        self.provider = provider
        self.registry = registry
        self.deadlock = deadlock
        self.stats = stats
        self.diag = diag
        self._disabled = False
        self._local_locks: Dict[str, Dict[str, Any]] = {}

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def make_key(self, lock_type: str, lock_id: str) -> str:
        return f"aios:v1:default:default:lock:{lock_type}:{lock_id}"

    def acquire_lease(
        self,
        lock_type: str,
        lock_id: str,
        owner_id: str,
        policy: LockPolicy,
        lease_duration: Optional[float] = None,
    ) -> bool:
        time.time()
        cfg = self.registry.get_configuration(lock_type)
        duration = lease_duration if lease_duration is not None else cfg["lease_duration"]
        key = self.make_key(lock_type, lock_id)

        if self._disabled:
            if key in self._local_locks:
                lock_info = self._local_locks[key]
                if time.time() > lock_info["expiration"]:
                    del self._local_locks[key]
                    if key in self.deadlock.lock_owners:
                        del self.deadlock.lock_owners[key]

            if key in self._local_locks:
                lock_info = self._local_locks[key]
                if policy == LockPolicy.REENTRANT and lock_info["owner_id"] == owner_id:
                    lock_info["count"] += 1
                    lock_info["expiration"] = time.time() + duration
                    return True
                if policy == LockPolicy.SHARED and lock_info["policy"] == LockPolicy.SHARED:
                    lock_info["owners"].add(owner_id)
                    lock_info["expiration"] = max(lock_info["expiration"], time.time() + duration)
                    return True
                return False

            self._local_locks[key] = {
                "owner_id": owner_id,
                "owners": {owner_id},
                "policy": policy,
                "count": 1,
                "expiration": time.time() + duration,
            }
            self.deadlock.lock_owners[key] = owner_id
            return True

        try:
            raw = self.provider.transport.execute_command("get", key)
            if raw is not None:
                payload = deserialize_val(raw)
                if time.time() - payload.get("creation_time", 0) > duration:
                    self.provider.transport.execute_command("delete", key)
                    raw = None

            if raw is not None:
                payload = deserialize_val(raw)
                if policy == LockPolicy.REENTRANT and payload["owner_id"] == owner_id:
                    payload["count"] += 1
                    payload["last_renewal"] = time.time()
                    payload["expiration"] = time.time() + duration
                    self.provider.transport.execute_command(
                        "set", key, serialize_val(payload), ex=int(duration)
                    )
                    return True
                if policy == LockPolicy.SHARED and payload["policy"] == LockPolicy.SHARED.value:
                    owners = set(payload["owners"])
                    owners.add(owner_id)
                    payload["owners"] = list(owners)
                    payload["last_renewal"] = time.time()
                    payload["expiration"] = max(payload["expiration"], time.time() + duration)
                    self.provider.transport.execute_command(
                        "set", key, serialize_val(payload), ex=int(duration)
                    )
                    return True

                return False

            payload = {
                "owner_id": owner_id,
                "owners": [owner_id],
                "policy": policy.value,
                "count": 1,
                "creation_time": time.time(),
                "last_renewal": time.time(),
                "expiration": time.time() + duration,
                "workspace_id": "default",
                "project_id": "default",
            }
            self.provider.transport.execute_command(
                "set", key, serialize_val(payload), ex=int(duration)
            )
            self.deadlock.lock_owners[key] = owner_id
            return True
        except Exception as e:
            self.diag.log_error(f"Lease acquire failure: {str(e)}")
            self._local_locks[key] = {
                "owner_id": owner_id,
                "owners": {owner_id},
                "policy": policy,
                "count": 1,
                "expiration": time.time() + duration,
            }
            self.deadlock.lock_owners[key] = owner_id
            return True

    def renew_lease(self, lock_type: str, lock_id: str, owner_id: str) -> bool:
        cfg = self.registry.get_configuration(lock_type)
        duration = cfg["lease_duration"]
        key = self.make_key(lock_type, lock_id)

        if self._disabled:
            if key in self._local_locks:
                lock_info = self._local_locks[key]
                if lock_info["owner_id"] == owner_id or (
                    lock_info["policy"] == LockPolicy.SHARED and owner_id in lock_info["owners"]
                ):
                    lock_info["expiration"] = time.time() + duration
                    self.stats.record_renewal(lock_type, success=True)
                    return True
            self.stats.record_renewal(lock_type, success=False)
            return False

        try:
            raw = self.provider.transport.execute_command("get", key)
            if raw is None:
                self.stats.record_renewal(lock_type, success=False)
                return False
            payload = deserialize_val(raw)
            if payload["owner_id"] == owner_id or (
                payload["policy"] == LockPolicy.SHARED.value and owner_id in payload["owners"]
            ):
                payload["last_renewal"] = time.time()
                payload["expiration"] = time.time() + duration
                self.provider.transport.execute_command(
                    "set", key, serialize_val(payload), ex=int(duration)
                )
                self.stats.record_renewal(lock_type, success=True)
                return True
            self.stats.record_renewal(lock_type, success=False)
            return False
        except Exception as e:
            self.diag.log_error(f"Lease renew failure: {str(e)}")
            if key in self._local_locks:
                lock_info = self._local_locks[key]
                if lock_info["owner_id"] == owner_id or (
                    lock_info["policy"] == LockPolicy.SHARED and owner_id in lock_info["owners"]
                ):
                    lock_info["expiration"] = time.time() + duration
                    self.stats.record_renewal(lock_type, success=True)
                    return True
            return False

    def release_lease(self, lock_type: str, lock_id: str, owner_id: str) -> bool:
        key = self.make_key(lock_type, lock_id)

        if self._disabled:
            if key in self._local_locks:
                lock_info = self._local_locks[key]
                if (
                    lock_info["policy"] == LockPolicy.REENTRANT
                    and lock_info["owner_id"] == owner_id
                ):
                    lock_info["count"] -= 1
                    if lock_info["count"] <= 0:
                        del self._local_locks[key]
                        if key in self.deadlock.lock_owners:
                            del self.deadlock.lock_owners[key]
                    self.stats.record_release(lock_type, success=True)
                    return True
                if lock_info["policy"] == LockPolicy.SHARED:
                    if owner_id in lock_info["owners"]:
                        lock_info["owners"].remove(owner_id)
                        if not lock_info["owners"]:
                            del self._local_locks[key]
                            if key in self.deadlock.lock_owners:
                                del self.deadlock.lock_owners[key]
                        self.stats.record_release(lock_type, success=True)
                        return True
                if lock_info["owner_id"] == owner_id:
                    del self._local_locks[key]
                    if key in self.deadlock.lock_owners:
                        del self.deadlock.lock_owners[key]
                    self.stats.record_release(lock_type, success=True)
                    return True
            self.stats.record_release(lock_type, success=False)
            return False

        try:
            raw = self.provider.transport.execute_command("get", key)
            if raw is None:
                self.stats.record_release(lock_type, success=False)
                return False
            payload = deserialize_val(raw)
            if payload["policy"] == LockPolicy.REENTRANT.value and payload["owner_id"] == owner_id:
                payload["count"] -= 1
                if payload["count"] <= 0:
                    self.provider.transport.execute_command("delete", key)
                    if key in self.deadlock.lock_owners:
                        del self.deadlock.lock_owners[key]
                else:
                    cfg = self.registry.get_configuration(lock_type)
                    self.provider.transport.execute_command(
                        "set", key, serialize_val(payload), ex=int(cfg["lease_duration"])
                    )
                self.stats.record_release(lock_type, success=True)
                return True
            if payload["policy"] == LockPolicy.SHARED.value:
                owners = set(payload["owners"])
                if owner_id in owners:
                    owners.remove(owner_id)
                    if not owners:
                        self.provider.transport.execute_command("delete", key)
                        if key in self.deadlock.lock_owners:
                            del self.deadlock.lock_owners[key]
                    else:
                        payload["owners"] = list(owners)
                        cfg = self.registry.get_configuration(lock_type)
                        self.provider.transport.execute_command(
                            "set", key, serialize_val(payload), ex=int(cfg["lease_duration"])
                        )
                    self.stats.record_release(lock_type, success=True)
                    return True
            if payload["owner_id"] == owner_id:
                self.provider.transport.execute_command("delete", key)
                if key in self.deadlock.lock_owners:
                    del self.deadlock.lock_owners[key]
                self.stats.record_release(lock_type, success=True)
                return True
            self.stats.record_release(lock_type, success=False)
            return False
        except Exception as e:
            self.diag.log_error(f"Lease release failure: {str(e)}")
            deleted = False
            if key in self._local_locks:
                lock_info = self._local_locks[key]
                if (
                    lock_info["policy"] == LockPolicy.REENTRANT
                    and lock_info["owner_id"] == owner_id
                ):
                    lock_info["count"] -= 1
                    if lock_info["count"] <= 0:
                        del self._local_locks[key]
                        if key in self.deadlock.lock_owners:
                            del self.deadlock.lock_owners[key]
                    self.stats.record_release(lock_type, success=True)
                    deleted = True
                elif lock_info["policy"] == LockPolicy.SHARED:
                    if owner_id in lock_info["owners"]:
                        lock_info["owners"].remove(owner_id)
                        if not lock_info["owners"]:
                            del self._local_locks[key]
                            if key in self.deadlock.lock_owners:
                                del self.deadlock.lock_owners[key]
                        self.stats.record_release(lock_type, success=True)
                        deleted = True
                elif lock_info["owner_id"] == owner_id:
                    del self._local_locks[key]
                    if key in self.deadlock.lock_owners:
                        del self.deadlock.lock_owners[key]
                    self.stats.record_release(lock_type, success=True)
                    deleted = True
            return deleted

    def force_release(self, lock_type: str, lock_id: str) -> bool:
        key = self.make_key(lock_type, lock_id)
        if key in self._local_locks:
            del self._local_locks[key]
        if key in self.deadlock.lock_owners:
            del self.deadlock.lock_owners[key]
        if self._disabled:
            return True
        try:
            self.provider.delete(key)
            return True
        except Exception:
            return False

    def verify_ownership(self, lock_type: str, lock_id: str, owner_id: str) -> bool:
        key = self.make_key(lock_type, lock_id)
        if self._disabled:
            if key in self._local_locks:
                lock_info = self._local_locks[key]
                return lock_info["owner_id"] == owner_id or (
                    lock_info["policy"] == LockPolicy.SHARED and owner_id in lock_info["owners"]
                )
            return False
        try:
            raw = self.provider.transport.execute_command("get", key)
            if raw is None:
                if key in self._local_locks:
                    lock_info = self._local_locks[key]
                    return lock_info["owner_id"] == owner_id or (
                        lock_info["policy"] == LockPolicy.SHARED and owner_id in lock_info["owners"]
                    )
                return False
            payload = deserialize_val(raw)
            return payload["owner_id"] == owner_id or (
                payload["policy"] == LockPolicy.SHARED.value and owner_id in payload["owners"]
            )
        except Exception:
            if key in self._local_locks:
                lock_info = self._local_locks[key]
                return lock_info["owner_id"] == owner_id or (
                    lock_info["policy"] == LockPolicy.SHARED and owner_id in lock_info["owners"]
                )
            return False


class LockRecoveryManagerImpl(LockRecoveryManager):
    def __init__(self, stats: CoordinationStatisticsCollector) -> None:
        self.stats = stats

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def recover_locks(self) -> int:
        self.stats.record_recovery(0)
        return 0

    def trigger_lock_rebuild(self) -> None:
        pass


class MutexManagerImpl(MutexManager):
    def __init__(
        self, lease_manager: LockLeaseManager, stats: CoordinationStatisticsCollector
    ) -> None:
        self.lease_manager = lease_manager
        self.stats = stats

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def acquire_mutex(self, lock_type: str, lock_id: str, owner_id: str, timeout: float) -> bool:
        start_time = time.time()
        end_time = start_time + timeout

        while time.time() < end_time:
            success = self.lease_manager.acquire_lease(
                lock_type, lock_id, owner_id, LockPolicy.EXCLUSIVE
            )
            if success:
                latency_ms = (time.time() - start_time) * 1000.0
                self.stats.record_latency("acquire_mutex", latency_ms)
                return True
            time.sleep(0.05)

        return False

    def release_mutex(self, lock_type: str, lock_id: str, owner_id: str) -> bool:
        return self.lease_manager.release_lease(lock_type, lock_id, owner_id)


class DistributedLockManagerImpl(DistributedLockManager):
    def __init__(
        self,
        lease_manager: LockLeaseManager,
        deadlock: DeadlockDetector,
        stats: CoordinationStatisticsCollector,
    ) -> None:
        self.lease_manager = lease_manager
        self.deadlock = deadlock
        self.stats = stats

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def acquire(
        self,
        lock_type: str,
        lock_id: str,
        owner_id: str,
        policy: LockPolicy,
        lease_duration: Optional[float] = None,
        timeout: Optional[float] = None,
    ) -> bool:
        start_time = time.time()
        eff_timeout = timeout if timeout is not None else 5.0
        end_time = start_time + eff_timeout

        self.deadlock.register_wait(owner_id, lock_id, lock_type)

        try:
            while time.time() < end_time:
                success = self.lease_manager.acquire_lease(
                    lock_type, lock_id, owner_id, policy, lease_duration
                )
                if success:
                    self.deadlock.unregister_wait(owner_id, lock_id)
                    wait_time_ms = (time.time() - start_time) * 1000.0
                    self.stats.record_acquisition(
                        lock_type, policy, success=True, wait_time_ms=wait_time_ms
                    )
                    return True
                time.sleep(0.05)
        finally:
            self.deadlock.unregister_wait(owner_id, lock_id)

        wait_time_ms = (time.time() - start_time) * 1000.0
        self.stats.record_acquisition(lock_type, policy, success=False, wait_time_ms=wait_time_ms)
        return False

    def release(self, lock_type: str, lock_id: str, owner_id: str) -> bool:
        return self.lease_manager.release_lease(lock_type, lock_id, owner_id)

    def renew(self, lock_type: str, lock_id: str, owner_id: str) -> bool:
        return self.lease_manager.renew_lease(lock_type, lock_id, owner_id)

    def is_locked(self, lock_type: str, lock_id: str) -> bool:
        key = self.lease_manager.make_key(lock_type, lock_id)
        if self.lease_manager._disabled:
            return key in self.lease_manager._local_locks
        try:
            return self.lease_manager.provider.exists(key)
        except Exception:
            return key in self.lease_manager._local_locks

# ruff: noqa: F401
"""
persistence_impl_modules/repo_base.py

Shared mixin for repository implementations that expose all CRUD operations
as PersistenceResult-returning methods (the "engineering" / "automation" /
"AI-provider" style repositories).

Subclasses must expose ``self.service: PersistenceService``.
This mixin is INTERNAL to the persistence_impl_modules package and must not be
imported from outside it, so no public contract changes occur.

Cache-aware helpers
-------------------
``_write_with_cache`` and ``_fetch_one_with_cache`` consolidate the
cache-invalidation / write-through bookkeeping that several provider-level
repositories perform after every write or read.  They delegate to the plain
``_write`` / ``_fetch_one`` helpers for the core SQL work, then apply optional
Redis-backed cache logic through the ServiceRegistry without introducing
any additional imports at module load time.
"""

from __future__ import annotations

import time
from typing import Any, Callable, Dict, Optional, Tuple

from aios.services.persistence import (
    PersistencePolicy,
    PersistenceResult,
    PersistenceService,
    PersistenceStatus,
)


class _RepositoryMixin:
    """
    Internal mixin providing shared CRUD helper utilities and no-op lifecycle
    stubs for repository implementations whose operations all return
    ``PersistenceResult``.

    Concrete classes gain four benefits:
      1. ``initialize() / start() / stop()`` are inherited as no-ops.
      2. Status-guard logic is de-duplicated via ``_guard_status()``.
      3. Write, fetch-one, and fetch-all boilerplate is de-duplicated via
         ``_write()``, ``_fetch_one()``, and ``_fetch_all()``.
      4. Cache-aware write and fetch helpers are de-duplicated via
         ``_write_with_cache()`` and ``_fetch_one_with_cache()``.
    """

    # ── Lifecycle no-ops (shared by all Group-2 repos) ────────────────────

    def initialize(self) -> None:  # noqa: D102
        pass

    def start(self) -> None:  # noqa: D102
        pass

    def stop(self) -> None:  # noqa: D102
        pass

    # ── Guard helpers ─────────────────────────────────────────────────────

    def _guard_status(self, table: str, operation: str) -> Optional[PersistenceResult]:
        """
        Check service readiness for *table*/*operation*.

        Returns the failed ``PersistenceResult`` when the service is not ready;
        returns ``None`` when the service is healthy and ready to proceed.
        Raises ``RuntimeError`` immediately when STRICT policy is active.
        """
        status_res = self.service.check_status(table, operation)  # type: ignore[attr-defined]
        if status_res.status != PersistenceStatus.SUCCESS:
            if self.service.config.policy == PersistencePolicy.STRICT:  # type: ignore[attr-defined]
                raise RuntimeError(status_res.message)
            return status_res
        return None

    # ── Write helper ──────────────────────────────────────────────────────

    def _write(
        self,
        table: str,
        query: str,
        params: Tuple[Any, ...],
        success_msg: str,
    ) -> PersistenceResult:
        """
        Execute a write SQL statement (INSERT / UPDATE / DELETE) and wrap the
        outcome in a ``PersistenceResult``.

        On success returns ``PersistenceStatus.SUCCESS``.
        On failure returns ``PersistenceStatus.UNKNOWN_FAILURE`` (or raises
        ``RuntimeError`` when STRICT policy is active).
        """
        start_time = time.time()
        try:
            self.service.execute(query, params)  # type: ignore[attr-defined]
            latency = (time.time() - start_time) * 1000
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message=success_msg,
                provider=self.service.config.provider_name,  # type: ignore[attr-defined]
                latency=latency,
                repository=table,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)  # type: ignore[attr-defined]
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository=table,
            )
            if self.service.config.policy == PersistencePolicy.STRICT:  # type: ignore[attr-defined]
                raise RuntimeError(result.message) from e
            return result

    # ── Fetch helpers ─────────────────────────────────────────────────────

    def _fetch_one(
        self,
        table: str,
        query: str,
        params: Tuple[Any, ...],
        entity_id: str,
        parse_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
        success_msg: str,
    ) -> PersistenceResult:
        """
        SELECT a single row by id and wrap it in a ``PersistenceResult``.

        Returns ``PersistenceStatus.UNKNOWN_FAILURE`` (or raises in STRICT mode)
        when no row is found.
        """
        start_time = time.time()
        try:
            rows = self.service.execute(query, params)  # type: ignore[attr-defined]
            latency = (time.time() - start_time) * 1000
            if not rows:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=f"Record '{entity_id}' not found in {table}.",
                    latency=latency,
                    repository=table,
                )
                if self.service.config.policy == PersistencePolicy.STRICT:  # type: ignore[attr-defined]
                    raise RuntimeError(result.message)
                return result
            row = parse_fn(dict(rows[0]))
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message=success_msg,
                provider=self.service.config.provider_name,  # type: ignore[attr-defined]
                latency=latency,
                repository=table,
                payload=row,
            )
        except RuntimeError:
            raise
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)  # type: ignore[attr-defined]
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository=table,
            )
            if self.service.config.policy == PersistencePolicy.STRICT:  # type: ignore[attr-defined]
                raise RuntimeError(result.message) from e
            return result

    def _fetch_all(
        self,
        table: str,
        query: str,
        parse_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
        success_msg: str,
    ) -> PersistenceResult:
        """
        SELECT all rows from *table* and wrap in a ``PersistenceResult`` whose
        ``payload`` is a list of parsed row dicts.
        """
        start_time = time.time()
        try:
            rows = self.service.execute(query)  # type: ignore[attr-defined]
            latency = (time.time() - start_time) * 1000
            results = [parse_fn(dict(r)) for r in rows]
            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message=success_msg,
                provider=self.service.config.provider_name,  # type: ignore[attr-defined]
                latency=latency,
                repository=table,
                payload=results,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            diag = self.service.get_diagnostics_for_error(e)  # type: ignore[attr-defined]
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                diagnostics=diag,
                latency=latency,
                repository=table,
            )
            if self.service.config.policy == PersistencePolicy.STRICT:  # type: ignore[attr-defined]
                raise RuntimeError(result.message) from e
            return result

    # ── Cache-aware helpers ───────────────────────────────────────────────

    @staticmethod
    def _resolve_cache_services():
        """
        Attempt to resolve RedisCacheService and CachePolicyManager from the
        global ServiceRegistry.  Returns ``(cache_svc, policy_mgr)`` where
        either may be ``None`` when the services are unavailable.

        The import is deferred to avoid circular-import issues at module load
        time and to keep the mixin usable without Redis being present.
        """
        try:
            from aios.registry import ServiceRegistry
            from aios.services.persistence import (  # type: ignore[attr-defined]
                CachePolicyManager,
                RedisCacheService,
            )

            cache_svc = ServiceRegistry._global_registry.get(RedisCacheService)
            policy_mgr = ServiceRegistry._global_registry.get(CachePolicyManager)
            return cache_svc, policy_mgr
        except Exception:
            return None, None

    @staticmethod
    def _resolve_cache_svc():
        """
        Attempt to resolve only RedisCacheService.  Returns ``cache_svc`` or
        ``None`` when unavailable.
        """
        try:
            from aios.registry import ServiceRegistry
            from aios.services.persistence import RedisCacheService  # type: ignore[attr-defined]

            return ServiceRegistry._global_registry.get(RedisCacheService)
        except Exception:
            return None

    def _write_with_cache(
        self,
        table: str,
        query: str,
        params: Tuple[Any, ...],
        success_msg: str,
        cache_namespace: str,
        entity_id: str,
        *,
        cache_payload_fn: Optional[Callable[[], Dict[str, Any]]] = None,
        retrieve_msg: str = "",
    ) -> PersistenceResult:
        """
        Execute a write SQL statement then apply Redis cache policy.

        After a successful write the method:
        - On ``WRITE_THROUGH`` policy: calls ``cache_payload_fn()`` to obtain
          the cache payload and stores a ``PersistenceResult`` in the cache.
        - On any other policy (except ``NO_CACHE``): invalidates the entry.

        Parameters
        ----------
        table:
            SQL table name used for the ``PersistenceResult.repository`` field
            and the status guard.
        query:
            INSERT / UPDATE / DELETE SQL string.
        params:
            Positional parameters for the query.
        success_msg:
            Human-readable message on success.
        cache_namespace:
            Logical Redis namespace (e.g. ``"provider_capabilities"``).
        entity_id:
            Primary key of the entity being written.
        cache_payload_fn:
            Optional zero-argument callable returning the dict to cache.
            Only called on ``WRITE_THROUGH``.
        retrieve_msg:
            Message used in the cached ``PersistenceResult`` payload.
        """
        start_time = time.time()
        try:
            self.service.execute(query, params)  # type: ignore[attr-defined]
            latency = (time.time() - start_time) * 1000

            # ── Optional cache integration ─────────────────────────────────
            try:
                from aios.services.persistence import CachePolicy  # type: ignore[attr-defined]

                cache_svc, policy_mgr = self._resolve_cache_services()
                if cache_svc and policy_mgr:
                    policy = policy_mgr.get_policy(cache_namespace)
                    if policy == CachePolicy.WRITE_THROUGH and cache_payload_fn is not None:
                        payload = cache_payload_fn()
                        cached_result = PersistenceResult(
                            status=PersistenceStatus.SUCCESS,
                            message=retrieve_msg or success_msg,
                            provider=self.service.config.provider_name,  # type: ignore[attr-defined]
                            latency=latency,
                            repository=table,
                            payload=payload,
                        )
                        cache_svc.set(cache_namespace, entity_id, cached_result)
                    elif policy != CachePolicy.NO_CACHE:
                        cache_svc.delete(cache_namespace, entity_id)
            except Exception:
                pass  # Cache errors must never fail a write

            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message=success_msg,
                provider=self.service.config.provider_name,  # type: ignore[attr-defined]
                latency=latency,
                repository=table,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository=table,
            )
            if self.service.config.policy == PersistencePolicy.STRICT:  # type: ignore[attr-defined]
                raise RuntimeError(result.message) from e
            return result

    def _delete_with_cache(
        self,
        table: str,
        query: str,
        params: Tuple[Any, ...],
        success_msg: str,
        cache_namespace: str,
        entity_id: str,
    ) -> PersistenceResult:
        """
        Execute a DELETE SQL statement then invalidate the Redis cache entry.

        Equivalent to ``_write_with_cache`` but always invalidates (no
        write-through path needed for deletes).
        """
        start_time = time.time()
        try:
            self.service.execute(query, params)  # type: ignore[attr-defined]
            latency = (time.time() - start_time) * 1000

            # ── Cache invalidation ─────────────────────────────────────────
            try:
                cache_svc = self._resolve_cache_svc()
                if cache_svc:
                    cache_svc.delete(cache_namespace, entity_id)
            except Exception:
                pass  # Cache errors must never fail a delete

            return PersistenceResult(
                status=PersistenceStatus.SUCCESS,
                message=success_msg,
                provider=self.service.config.provider_name,  # type: ignore[attr-defined]
                latency=latency,
                repository=table,
            )
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            result = PersistenceResult(
                status=PersistenceStatus.UNKNOWN_FAILURE,
                message=str(e),
                latency=latency,
                repository=table,
            )
            if self.service.config.policy == PersistencePolicy.STRICT:  # type: ignore[attr-defined]
                raise RuntimeError(result.message) from e
            return result

    def _fetch_one_with_cache(
        self,
        table: str,
        query: str,
        params: Tuple[Any, ...],
        entity_id: str,
        parse_fn: Callable[[Dict[str, Any]], Dict[str, Any]],
        success_msg: str,
        not_found_msg: str,
        cache_namespace: str,
    ) -> PersistenceResult:
        """
        Fetch a single row through Redis cache when available, falling back to
        a direct SQL query.

        The cache is expected to store a ``PersistenceResult`` (as set by
        ``_write_with_cache`` on WRITE_THROUGH).  If the cache returns a
        ``PersistenceResult`` it is returned directly; otherwise the fallback
        SQL fetch is executed and wrapped in a new ``PersistenceResult``.
        """
        guard = self._guard_status(table, "get")
        if guard is not None:
            return guard

        cache_svc = self._resolve_cache_svc()

        def _do_fetch() -> PersistenceResult:
            start_time = time.time()
            try:
                rows = self.service.execute(query, params)  # type: ignore[attr-defined]
                latency = (time.time() - start_time) * 1000
                if not rows:
                    result = PersistenceResult(
                        status=PersistenceStatus.UNKNOWN_FAILURE,
                        message=not_found_msg,
                        latency=latency,
                        repository=table,
                    )
                    if self.service.config.policy == PersistencePolicy.STRICT:  # type: ignore[attr-defined]
                        raise RuntimeError(result.message)
                    return result
                row = parse_fn(dict(rows[0]))
                return PersistenceResult(
                    status=PersistenceStatus.SUCCESS,
                    message=success_msg,
                    provider=self.service.config.provider_name,  # type: ignore[attr-defined]
                    latency=latency,
                    repository=table,
                    payload=row,
                )
            except RuntimeError:
                raise
            except Exception as e:
                result = PersistenceResult(
                    status=PersistenceStatus.UNKNOWN_FAILURE,
                    message=str(e),
                    latency=(time.time() - start_time) * 1000,
                    repository=table,
                )
                if self.service.config.policy == PersistencePolicy.STRICT:  # type: ignore[attr-defined]
                    raise RuntimeError(result.message) from e
                return result

        if cache_svc:
            return cache_svc.get(cache_namespace, entity_id, _do_fetch)
        return _do_fetch()

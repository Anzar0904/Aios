# Qdrant Platform Health Status

- **Connection Reachable**: False (Discovery Phase)
- **Engine Status**: UNINITIALIZED
- **Active Subsystem Connections**: 0/9 collections loaded

---

## 1. Health Monitoring Design

The health of the Qdrant service is monitored via the `QdrantHealthMonitorImpl` component, which runs periodic checks and exposes status variables:

### Indicators:
* **Connection Reachability**: Checked using a simple client API check (ping / collection list retrieve).
* **Read Health**: A lightweight scroll query against a validation collection.
* **Write Health**: A dummy point insertion and deletion sequence in a dedicated test collection.
* **Collection Sync State**: Count of active collections registered in Qdrant vs defined configuration collections.

---

## 2. Degradation Paths

When a health check fails (service goes offline):
1. **Health State**: Transitions from `HEALTHY` to `DEGRADED` or `OFFLINE`.
2. **Alert Trigger**: Logs a `CRITICAL` diagnostics alert and requests connection retries.
3. **Execution Fallback**: Bypasses the Qdrant index. All queries to `MemoryService.search_memory` will fallback to PostgreSQL substring searches automatically.
4. **Queue Storage**: Write transactions are held in a pending queue in PostgreSQL.

# Known Issues — Personal AI OS v1.0.0 (Release Candidate)

The following non-blocking issues are known and deferred to future stability releases (v1.1 / v1.2):

### 1. Dashboard Subsystem Latency Metrics (REC-005 — P2)
- **Description**: Metrics shown in dashboard reports are loaded statically from the local metrics cache on kernel boot. Dynamic real-time graphing updates are not supported.
- **Workaround**: Reboot the shell or run command `aios health` to manually reload metrics.

### 2. Flat-file Database Concurrency Race Conditions (REC-006 — P2)
- **Description**: When utilizing JSON flat-file storage modes (e.g. n8n workflow caches, missions), concurrent operations from multiple client threads may trigger file-locking race conditions.
- **Workaround**: In multi-user setups, utilize PostgreSQL for unified SQL storage.

### 3. API Key Exposure in Stack Traces (REC-007 — P2)
- **Description**: Running the system in high-verbosity debug mode (`debug = true` in `config.toml`) might print raw configuration structures to stdout during connection failures, which could include loaded API key metadata.
- **Workaround**: Keep `debug = false` in production settings and restrict read access to configuration files.

### 4. Synchronous Event Bus Execution (REC-008 — P3)
- **Description**: The core `EventBusService` processes event handlers synchronously on the main execution thread. Heavy or slow event handlers may temporarily block shell input.
- **Workaround**: Offload heavy callback handling functions to background worker threads.

### 5. Mock-based Testing Replays (REC-009 — P3)
- **Description**: Integration and provider tests rely on static manual mock mocks rather than dynamic HTTP replays.
- **Workaround**: Run with actual provider keys to execute live integration tests.

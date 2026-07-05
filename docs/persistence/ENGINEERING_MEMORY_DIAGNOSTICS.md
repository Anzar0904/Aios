# Engineering Memory Diagnostics

## Diagnostics Engine
The `EngineeringMemoryReportGenerator` collaborates with the `EngineeringMemoryHealthMonitor` to run diagnostic cycles.

## Troubleshooting Guides

### Database Connection Failure
- **Symptoms**: Writes or reads timeout or raise connection errors. Under `STRICT` policy, `RuntimeError` is immediately raised.
- **Diagnostics Run**:
  1. Check database server availability (in production, check PostgreSQL container/service).
  2. Verify database connection string configuration in `PersistenceConfigurationService`.
  3. Under test fallback environments, verify the in-memory SQLite transport is correctly configured.

### Schema Validation Error
- **Symptoms**: `Record` or `Update` returns a status of `PersistenceStatus.VALIDATION_FAILED`.
- **Diagnostics Run**:
  1. Inspect the validator error list in the `PersistenceResult.message` string.
  2. Ensure the payload dictionary contains all required fields with their correct types (e.g. `id` for primary keys, valid date fields).

### Strict Policy Compliance Exceptions
- **Symptoms**: Unhandled `RuntimeError` crashes in calling services.
- **Diagnostics Run**:
  1. Under tests or dev work where PostgreSQL is not running, switch the policy in configuration to `BEST_EFFORT` or ensure `SQLiteTransportForTests` is loaded.

# Business Intelligence — Developer Guide

This document is aimed at developers extending AI OS or integrating new modules into the Business Intelligence layer.

---

## Extension Guide

To connect a new subsystem intelligence service into the Business operational analytics or client reports:

1. **Modify `get_analytics`**:
   Open [business_impl.py](file:///Users/anzarakhtar/aios/core/src/aios/services/business_impl.py#L145) and resolve your new service using `ServiceRegistry._global_registry.get(YourNewService)`.
2. **Merge Metadata**:
   Append any new metrics returned by the subsystem to the aggregate analytics dictionary:
   ```python
   try:
       new_service = ServiceRegistry._global_registry.get(YourNewService)
       if new_service:
           analytics["custom_subsystem_metric"] = new_service.get_metric()
   except Exception:
       pass
   ```
3. **Extend Reporting**:
   Update `generate_reports` to output any new subsystem summaries under `docs/business/`.
4. **Extend CLI**:
   Add new subcommands parsing in [cli.py](file:///Users/anzarakhtar/aios/core/src/aios/cli.py) and interactive registries in [discovery.py](file:///Users/anzarakhtar/aios/core/src/aios/services/command/discovery.py).

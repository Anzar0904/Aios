# Project Intelligence — Developer Guide

This document is aimed at developers extending AI OS or integrating new modules into the Project Intelligence layer.

---

## Extension Guide

To connect a new subsystem intelligence service into the Project Profile aggregator:

1. **Modify `get_project_profile`**:
   Open [project_intelligence_impl.py](file:///Users/anzarakhtar/aios/core/src/aios/services/project_intelligence_impl.py#L225) and resolve your new service using `ServiceRegistry._global_registry.get(YourNewService)`.
2. **Merge Metadata**:
   Append the returned service properties to the unified project profile dictionary:
   ```python
   try:
       new_service = ServiceRegistry._global_registry.get(YourNewService)
       if new_service:
           profile["new_subsystem"] = new_service.get_metadata()
   except Exception:
       pass
   ```
3. **Extend Reporting**:
   Update `generate_reports` to output any new subsystem summaries under `docs/project/`.

# Approval Engine & Governance — Developer Guide

This document is aimed at developers adding new protected integrations or writing custom governance rules.

---

## Integrating a Protected Operation

To guard a high-impact operation in a subsystem using the governance middleware:

1. **Resolve Approval Service**:
   Retrieve the service instance from the dependency injection registry:
   ```python
   from aios.registry import ServiceRegistry
   from aios.services.approval import ApprovalEngineService

   service = ServiceRegistry._global_registry.get(ApprovalEngineService)
   ```

2. **Initialize Middleware**:
   Create a middleware wrapper:
   ```python
   from aios.services.approval_impl import ApprovalMiddleware
   middleware = ApprovalMiddleware(service)
   ```

3. **Process Action**:
   Call `process_action` before executing the actual logic:
   ```python
   res = middleware.process_action(
       action="delete_database",
       project="my_project",
       client="my_client",
       provider="supabase",
       details={"changes": "dropping tables", "rollback": False}
   )

   if res["status"] == "executed":
       # Proceed with execution using the single-use token: res["token"]
       execute_drop_tables()
   elif res["status"] == "queued":
       # Action queued, show request ID to the user: res["request_id"]
       print(f"Action queued for approval. Request ID: {res['request_id']}")
   else:
       # Rejected
       raise PermissionError("Action rejected by governance middleware policy.")
   ```

# self-hosted n8n Integration — Phase 1 Milestone 4 Report

## Executive Summary
This report details the implementation of **Phase 1: Automation Intelligence**, specifically **Milestone 4: Self-hosted n8n Integration**. This subsystem manages connection profiles, authentication headers, REST API integrations, and health metrics monitoring.

The integration is mock-driven and has no external server dependency. It never builds workflows or changes Workflow IR models.

---

## 1. Integration Architecture

The integration service coordinates calls from workspace layers, validates profiles configs, drives client REST mock uploads/triggers, and exports JSON metadata:

```mermaid
graph TD
    A[N8NIntegrationService] --> B[N8NClient]
    A --> C[N8NConnectionManager]
    A --> D[N8NHealthMonitor]
    A --> E[N8NWorkspaceMapper]
    A --> F[N8NValidator]
    
    C --> G[N8NAuthenticationProvider]
    G -->|Type 1| H[APIKeyAuthenticationProvider]
    G -->|Type 2| I[BearerTokenAuthenticationProvider]
    
    A -. -->|Caches connection status| J[MemoryService]
    A -. -->|Writes metadata JSON| K[AIWorkspaceService]
    A -. -->|Pushes diagnostics| L[KnowledgeHubService]
```

---

## 2. Client & API Abstractions Design

The `N8NClient` models standard self-hosted n8n REST endpoints:
* **`upload_workflow`**: Submits workflow JSON to the n8n catalog.
* **`execute_workflow`**: Triggers workflow execution runs.
* **`activate_workflow` / `deactivate_workflow`**: Changes trigger listener active states.
* **`list_workflows` / `list_executions`**: Queries metadata logs.

---

## 3. Extensible Authentication Provider

The `N8NAuthenticationProvider` uses an extensible structure to generate request headers:
* **`APIKeyAuthenticationProvider`**: Supplies `X-N8N-API-KEY` header parameters.
* **`BearerTokenAuthenticationProvider`**: Supplies standard `Authorization` Bearer token strings.
* Credentials and API secrets are never cached in memory or printed in markdown reports.

---

## 4. Health Monitoring

The `N8NHealthMonitor` analyzes server endpoints. It returns:
* **Connectivity status**: `online` / `offline`.
* **Latency metrics**: Server response latency in milliseconds.
* **Capabilities**: Array listing supported node versions or OAuth credentials.

---

## 5. Workspace Mapping & Repository Mappings

The service maps n8n workflow assets back to the generating workspace:
* **`N8NWorkspaceMapper`**: Resolves ownership mappings to prevent cross-workspace contamination.
* **`N8NWorkflowRepository` & `N8NExecutionRepository`**: Track uploaded workflows and execution log metadata.
* **JSON Exporting**: Writes connection metadata and workflow details to `docs/automations/N8N_METADATA_{workflow_id}.json` inside the isolated workspace path.

---

## 6. Integration Points

* **`n8n Translation Engine`**: Feeds translated n8n workflow JSON arrays to the integration service.
* **`Intent Engine` / `Mission Engine`**: Trigger automated executions on-demand.
* **`Daily OS`**: Runs automated schedules by calling active webhook urls.

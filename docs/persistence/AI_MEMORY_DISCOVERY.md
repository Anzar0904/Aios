# Architecture Discovery Report: AI Memory Persistence

## 1. Overview
This report documents the discovery of runtime-only state storage within the AI OS Provider, Routing, Quota, Checkpoint, and Telemetry subsystems. It outlines how these volatile components will be mapped to persistent database tables in Sprint 4 Milestone 5.

## 2. Discovery of Runtime-Only Storage

### 2.1 Provider Registry & Metadata
* **Components**: `ProviderRegistry` (`core/src/aios/providers/registry.py`)
* **Storage Location**: `self._providers: Dict[str, ProviderMetadata]`
* **Data Transience**: Currently, default providers are hardcoded and loaded into an in-memory dictionary. Any additions or updates are lost on reboot.
* **Proposed Persistence**: `AIProviderRepository` and `ProviderCapabilityRepository`.

### 2.2 Health & Diagnostics
* **Components**: `ProviderHealthMonitor` (`core/src/aios/providers/health.py`)
* **Storage Location**:
  * `self.latency_analyzer._latencies: Dict[str, List[float]]`
  * `self.success_analyzer._successes: Dict[str, int]`, `_timestamps: Dict[str, float]`
  * `self.failure_analyzer._failures: Dict[str, int]`, `_timestamps: Dict[str, float]`, `_error_logs: Dict[str, List[str]]`
  * `self.rate_limit_manager._cooldowns: Dict[str, float]`
* **Data Transience**: Query histories, success rates, availability stats, and cooldown timestamps reside entirely in local lists and dictionaries.
* **Proposed Persistence**: `ProviderHealthRepository`, `ProviderTelemetryRepository`, `ProviderStatisticsRepository`.

### 2.3 Quotas & Budgets
* **Components**: `ProviderQuotaManager` (`core/src/aios/providers/health.py`)
* **Storage Location**: `self.quota_manager._quota_used: Dict[str, float]`
* **Data Transience**: Total daily/monthly expenditure tracking is reset whenever the kernel halts.
* **Proposed Persistence**: `ProviderQuotaRepository`.

### 2.4 Token Usage
* **Components**: `ProviderTokenUsageTracker` (`core/src/aios/providers/health.py`)
* **Storage Location**: `self.token_usage._daily_input`, `_daily_output`, `_monthly_input`, `_monthly_output`
* **Data Transience**: Aggregated token measurements exist solely in runtime memory.
* **Proposed Persistence**: `AIUsageStatisticsRepository`.

### 2.5 Routing decisions
* **Components**: `RoutingPolicyEngine` and specialized routers (`core/src/aios/providers/selector.py`)
* **Storage Location**: Selected options during runtime routing.
* **Proposed Persistence**: `ProviderRoutingRepository`.

### 2.6 Checkpoints, Resumptions, and Failovers
* **Components**: `CheckpointManager`, `ResumeManager`, `AutomaticFailoverEngine` (`core/src/aios/providers/router.py`)
* **Storage Location**: `self._checkpoints: Dict[str, Dict[str, Any]]`
* **Data Transience**: Execution context checkpoints and failover logs are lost upon process termination.
* **Proposed Persistence**: `ProviderCheckpointRepository`, `ProviderSessionRepository`, `ProviderFailoverRepository`.

---

## 3. Database Schema Proposals

### 3.1 Migration 24: `ai_providers`
Exposes the name, version, status, priority, context window, and cost details of providers.

### 3.2 Migration 25: `provider_capabilities`
Exposes capabilities (streaming, vision, function_calling, etc.) mapped to provider IDs.

### 3.3 Migration 26: `provider_health`
Exposes rate limits, circuit breaker states, and uptime metrics.

### 3.4 Migration 27: `provider_telemetry`
Exposes latency tracking and success rates.

### 3.5 Migration 28: `provider_statistics`
Exposes counts of total requests, failures, and latency stats.

### 3.6 Migration 29: `provider_quotas`
Exposes quota limits and daily/monthly expenditures.

### 3.7 Migration 30: `provider_routing`
Exposes selected models, routing strategies, and targets.

### 3.8 Migration 31: `provider_sessions`
Exposes active sessions routing states.

### 3.9 Migration 32: `provider_checkpoints`
Exposes task IDs, context metadata, and retries count.

### 3.10 Migration 33: `provider_failovers`
Exposes failed/target providers and failover dates.

### 3.11 Migration 34: `ai_usage_statistics`
Exposes token usage counts and costs.

### 3.12 Migration 35: `ai_memory`
Exposes facts and durable semantic metadata.

---

## 4. Exclusion & Safety Constraints
* **NEVER PERSIST**: API keys, auth tokens, passwords, cookies, prompts, prompt templates, model outputs, dialog logs, chain-of-thought, or embeddings.
* **STRICT Caching**: All repositories execute read-through/write-through caching to local dicts.

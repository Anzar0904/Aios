# AI OS Provider Manager Specification

This document details the architecture, routing rules, health monitor mechanics, configuration capabilities, and performance metrics of the **Provider Manager** inside the Personal AI OS.

---

## 1. Overview & Objectives

The Provider Manager is a unified routing layer positioned directly between the AI OS core services (e.g. `LocalModelService`) and the underlying LLM provider clients (e.g., OpenRouter, OpenAI, Anthropic, Gemini, Ollama, LM Studio). It automatically handles provider health checks, context limitations, cost/latency criteria, fallback hierarchies, and offline constraints.

---

## 2. Directory Layout

All provider routing and management components live under:

```
core/src/aios/providers/
├── __init__.py    # Packages imports
├── config.py      # ProviderConfig: preferred_provider, fallback_chain, offline_mode
├── models.py      # Dataclasses representing provider capabilities, context sizes, costs, latency
├── registry.py    # ProviderRegistry: default configurations for all 6 supported providers
├── selector.py    # ProviderSelector: capability, context, availability, and offline constraint filters
├── health.py      # ProviderHealthMonitor: tracks success rates and moving average latency
└── metrics.py     # ProviderMetricsCollector: tracks cumulative tokens, costs, and model counts
```

---

## 3. Selector Filtering Pipeline

For every request, the `ProviderSelector` applies a strict series of checks:

1. **Model Support**: If a specific model is requested, it filters for providers officially listing support for it.
2. **Offline Constraint**: If `offline_mode = True`, only local providers (Ollama, LM Studio) are evaluated.
3. **Availability Filter**: Providers with success rates below `50%` are bypassed.
4. **Context Fit**: The request prompt length is compared against the provider's official context window.
5. **Fallback Chain**: Evaluates the fallback chain in order to select the final active provider and model.

---

## 4. Fallback Execution Flow

If a selected remote provider experiences a connection timeout, HTTP error, or rate limits:
1. The health monitor records a failure.
2. The `ProviderRouter` catches the exception.
3. The router re-queries the selector excluding the failed provider to obtain the next best option (e.g. falling back from OpenRouter to OpenAI, or to Ollama locally).
4. Records the success metric when a provider successfully completes the request.

---

## 5. OmniRoute Intelligent Routing Integration

OmniRoute has been integrated into the Provider Layer as the primary intelligent Model Routing Backend.

### 5.1 Architecture & Role
* **OmniRoute** handles: model selection, routing weights, multi-provider failover, streaming, provider health tracking, and request forwarding.
* **AI OS** handles: task description, reasoning, and context assembly.
* **Agility**: The Brain remains completely model-agnostic, simply requesting a model name or category (e.g. `coding`, `research`, `chat`). The Provider Layer maps this context to OmniRoute's auto-routing endpoints.

### 5.2 Configuration
OmniRoute is configured via `config/config.toml` under the `[llm]` and `[llm.omniroute]` headers:
```toml
[llm]
provider = "omniroute"
default_model = "auto"

[llm.omniroute]
base_url = "http://localhost:20128/v1"
routing_policy = "FREE_ONLY"      # Only FREE_ONLY is supported for v1.0
timeout = 30
retry_count = 3
streaming_enabled = true
offline_mode = false
```

### 5.3 Authentication
* Primarily authenticated using the `Authorization: Bearer <API_KEY>` header.
* Credentials are loaded from the configuration file or retrieved from the `OMNIROUTE_API_KEY` environment variable.

### 5.4 Metadata Mapping Flow
For AI OS v1.0, the `FREE_ONLY` policy is strictly enforced. The model selector maps task indicators to OmniRoute auto-combo routes ending with `:free`:
* `claude-3-5-sonnet` / `coding` / `code` / `developer` -> `auto/coding:free`
* `gpt-4o` / `gemini-1.5-pro` / `reasoning` / `research` / `learning` / `smart` -> `auto/reasoning:free`
* `llama3` / `mistral` / `phi3` / `chat` / `conversation` / `career` -> `auto/chat:free`
* `vision` / `multimodal` -> `auto/multimodal:free`

### 5.5 Streaming Integration
* Streaming executes via HTTP Server-Sent Events (SSE) using the `/chat/completions` endpoint with `stream = true`.
* The client parses chunks dynamically, yielding individual `LLMResponse` items. If the stream encounters connection failures, it automatically falls back to standard HTTP POST generation.

### 5.6 Retry & Timeout Logic
* Retries (up to the configured `retry_count`) execute using exponential backoff (`2 ** attempt` seconds sleep) on transient HTTP status codes (429, 500, 502, 503, 504).
* The `timeout` threshold governs individual request durations before raising an `LLMProviderError` and triggering Provider Router fallback execution.

### 5.7 Health & Connection Checks
* The provider performs an active health check using OmniRoute's lightweight database check `/api/health/ping`.
* If the ping check is unreachable, it falls back to testing the standard `/v1/models` catalog endpoint.

### 5.8 Diagnostics & Observability
* **Rich Metadata Propagation**: Instead of requesting specific model choices (like 'Use Claude', 'Use GPT', or 'Use Gemini'), AI OS describes the work. It sends `X-OmniRoute-Task-Category` (e.g. `coding`, `research`, `reasoning`, `automation`, `learning`, `career`, `conversation`) and `X-OmniRoute-Preferences` (e.g., `reasoning_depth`, `latency_preference`, `JSON_output`, `tool_calling`, `long_context`) in custom HTTP headers and JSON payload request metadata.
* **Telemetry Diagnostics**: After every prompt generation or stream request, `OmniRouteProvider` parses custom `X-OmniRoute-*` headers from the response to record the actual `selected_provider`, `selected_model`, whether a `fallback_used` indicator was triggered, the `fallback_reason` (e.g., rate limits, cooldowns, or quota exhaustions), and the total request `latency`.
* **Diagnostics Storage**: Telemetry info is stored under `LLMResponse.metadata["diagnostics"]` and output to logs for debugging, without interfering with normal user interaction.



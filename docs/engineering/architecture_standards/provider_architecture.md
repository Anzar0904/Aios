# Model Provider & Routing Standards
**Engineering Bible — Milestone 3**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. Decoupled Provider Clients

To ensure that the Personal AI OS is completely independent of specific model vendors, all LLM operations are decoupled behind the `ModelService` interface.

### Decoupling Rules
* **No Direct SDK Imports**: Custom skills, tools, and execution engines are prohibited from importing vendor SDK libraries (such as `openai`, `anthropic`, or `google-generativeai`) directly.
* **Abstract Contracts**: Calling code must interact solely with `ModelService` using standard model inputs (prompts, temperature, token limits) and structured outputs. Swapping model endpoints requires configuration changes rather than refactoring code.

---

## 2. OmniRoute Strategy

The **OmniRoute Selector** is the intelligent routing engine inside the `ModelService` layer. It acts as the gateway for all model interactions, evaluating requests against environment constraints.

```
       [Request Prompt]
              │
              ▼
   +───────────────────────+
   │  Offline Mode Check?  ├─(Yes)─▶ [Route to Local Ollama / LM Studio]
   +──────────┬────────────+
              │(No)
              ▼
   +───────────────────────+
   │ Context Window Check  ├─(Fails)─▶ [Raise TokenLimitError]
   +──────────┬────────────+
              │(Passes)
              ▼
   +───────────────────────+
   │ Execute Primary Call  ├─(Timeout/Error)─▶ [Attempt Fallback Chain]
   +───────────────────────+
```

### OmniRoute Operations

#### 1. Offline Mode Routing
If `offline_mode = True` is set in `config.toml`, OmniRoute blocks remote API calls and routes requests to local endpoints (e.g., Ollama, LM Studio). Remote endpoints must not be accessed when offline mode is active.

#### 2. Context Boundary Filtering
OmniRoute evaluates the prompt size against candidate provider context boundaries. If a prompt length exceeds a model's window, that provider is filtered out, or a `TokenLimitError` is raised before dispatching.

#### 3. Automatic Failover Chains
If a primary provider client times out or returns a service failure (e.g., rate limits or API outage), OmniRoute catches the exception and routes the request to fallback endpoints defined in the configuration chain.

---

## 3. Telemetry, Quotas & Usage Auditing

* **Usage Tracking**: The `ModelService` aggregates token usage metrics (input, output, and cache hit metrics) and persists them to the `AIUsageStatisticsRepository`.
* **Latency Percentile Metrics**: Tracks execution durations to build P50, p90, and p99 performance profiles, helping the router select endpoints that meet performance requirements.
* **Quota Safeguards**: If usage metrics exceed a user's defined financial caps, OmniRoute suspends remote calls and reverts to local execution until the budget resets.

---

*Engineering Bible Architecture Standards · Personal AI OS · Sprint 8 M3 · Governed by [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md)*

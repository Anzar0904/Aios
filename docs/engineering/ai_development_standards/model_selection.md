# Model Selection & Offline Failover Guidance
**Engineering Bible — Milestone 6**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. Task-to-Model Mapping Registry

To balance performance and budget, the system routes queries to models matching the required intelligence level:

| Task Category | Primary Model | Fallback Model | Local (Offline) Model |
|---------------|---------------|----------------|-----------------------|
| **Complex Coding & Audits** | `claude-3-5-sonnet` | `qwen/qwen3-coder` | `codellama` |
| **Dialogue & Chat** | `gpt-4o-mini` | `gemini-1.5-flash` | `llama3` |
| **Memory & Summarization** | `gemini-1.5-flash` | `gpt-4o-mini` | `mistral` |
| **Structured JSON Parsing** | `gpt-4o` | `gemini-1.5-pro` | `hermes-2-pro` |

---

## 2. Cost Constraints & Budget Gates

The system monitors model token costs to prevent budget overruns:
* **Cost Calculations**: Remote queries (via OpenAI, Anthropic, or OpenRouter) calculate input and output token costs based on defined rates (e.g. $3.00/M input for Sonnet).
* **Token Compaction**: Use token compaction (dialogue summarization) when conversations exceed 10 turns to minimize input costs.
* **Local Processing Deflection**: For repetitive queries (like unit test iterations or log audits), deflect calls to local Ollama or LM Studio models.

---

## 3. Offline Failover Policy

To support local-first operation:
* **Offline Detection**: If `offline_mode = True` is set in `config.toml`, the system blocks outgoing external API connections.
* **Automatic Failover**: If a remote provider times out or returns error codes (such as HTTP 429 rate limits), the `ProviderRouter` registers the issue and routes the request to local endpoints.
* **Mock Mode fallback**: If all remote and local models are offline, the system routes calls to the `mock-model` to prevent execution crashes.

---

*Engineering Bible AI Development Standards · Personal AI OS · Sprint 8 M6 · Governed by [04_AI_MODEL_STRATEGY.md](file:///Users/anzarakhtar/aios/docs/04_AI_MODEL_STRATEGY.md)*

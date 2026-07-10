# Routing Summary
Generated at: 2026-07-10 22:15:32

## Active Routing Policies
- **default**: Health score weight (0.4), Latency weight (0.3), Cost weight (0.3).
- **cost-first**: Health score weight (0.2), Latency weight (0.1), Cost weight (0.7).
- **speed-first**: Health score weight (0.2), Latency weight (0.7), Cost weight (0.1).
- **quality-first**: Health score weight (0.7), Latency weight (0.2), Cost weight (0.1) with model capabilities boost.
- **local-first**: Prioritizes local providers (like `ollama`, `lmstudio`, `mock`) with massive weight boost.

## Current Routing Choices
| Task Type | Best Provider | Best Model | Score | Reasoning |
| --- | --- | --- | --- | --- |
| chat | mock | mock-model | 100.0 | Routed under policy 'default'. Health score: 100.0 (40% weight), latency: 0.0ms (30% weight), estimated cost: 0.0000 USD (30% weight). |
| coding | mock | default | 10.0 | No matching candidates passed filters. Falling back to default provider 'mock'. |
| embeddings | mock | default | 10.0 | No matching candidates passed filters. Falling back to default provider 'mock'. |
| vision | mock | default | 10.0 | No matching candidates passed filters. Falling back to default provider 'mock'. |
| reasoning | mock | default | 10.0 | No matching candidates passed filters. Falling back to default provider 'mock'. |
# Routing Summary
Generated at: 2026-07-14 23:18:08

## Active Routing Policies
- **default**: Health score weight (0.4), Latency weight (0.3), Cost weight (0.3).
- **cost-first**: Health score weight (0.2), Latency weight (0.1), Cost weight (0.7).
- **speed-first**: Health score weight (0.2), Latency weight (0.7), Cost weight (0.1).
- **quality-first**: Health (0.7), Latency (0.2), Cost (0.1) with capability boost.
- **local-first**: Prioritizes local providers (Ollama, LMStudio, Mock) with boost.

## Current Routing Choices
| Task Type | Best Provider | Best Model | Score | Reasoning |
| --- | --- | --- | --- | --- |
| chat | claude | claude-3-5-sonnet | 100.0 | Routed under policy 'default'. Health score: 100.0 (40% weight), latency: 0.0ms (30% weight), estimated cost: 0.0000 USD (30% weight). |
| coding | nvidia | nvidia/nemotron-4-340b-instruct | 100.0 | Routed under policy 'default'. Health score: 100.0 (40% weight), latency: 0.0ms (30% weight), estimated cost: 0.0000 USD (30% weight). |
| embeddings | openai | gpt-4o | 100.0 | Routed under policy 'default'. Health score: 100.0 (40% weight), latency: 0.0ms (30% weight), estimated cost: 0.0000 USD (30% weight). |
| vision | ninerouter | qwen-coder-32b | 90.0 | Routed under policy 'default'. Health score: 90.0 (40% weight), latency: 0.0ms (30% weight), estimated cost: 0.0000 USD (30% weight). |
| reasoning | nvidia | nvidia/nemotron-4-340b-instruct | 100.0 | Routed under policy 'default'. Health score: 100.0 (40% weight), latency: 0.0ms (30% weight), estimated cost: 0.0000 USD (30% weight). |
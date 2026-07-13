import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List

from aios.providers.interface import (
    RoutingRequest,
    universal_capability_registry,
    universal_cost_registry,
    universal_health_registry,
    universal_model_registry,
    universal_provider_registry,
    universal_routing_engine,
)

logger = logging.getLogger(__name__)

METRICS_FILE = Path(".aios_providers_metrics.json")


def load_metrics() -> List[Dict[str, Any]]:
    if METRICS_FILE.is_file():
        try:
            return json.loads(METRICS_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return []


def save_metrics(metrics: List[Dict[str, Any]]) -> None:
    try:
        METRICS_FILE.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to save metrics: {e}")


def record_metric(
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cost: float,
    latency_ms: float,
    success: bool,
) -> None:
    metrics = load_metrics()
    metrics.append(
        {
            "timestamp": time.time(),
            "provider": provider,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost,
            "latency_ms": latency_ms,
            "success": success,
        }
    )
    if len(metrics) > 1000:
        metrics = metrics[-1000:]
    save_metrics(metrics)


def run_parallel_health_checks() -> Dict[str, bool]:
    """Runs health checks on all registered providers in parallel."""
    providers = universal_provider_registry.list_providers()
    results = {}

    def check_health(provider_name: str) -> tuple[str, bool]:
        provider = universal_provider_registry.lookup(provider_name)
        if not provider:
            return provider_name, False
        try:
            start_time = time.time()
            is_healthy = provider.health()
            latency = (time.time() - start_time) * 1000.0
            if is_healthy:
                universal_health_registry.update_health_success(provider_name, latency)
            else:
                universal_health_registry.update_health_failure(
                    provider_name, "Health check failed"
                )
            return provider_name, is_healthy
        except Exception as e:
            universal_health_registry.update_health_failure(provider_name, str(e))
            return provider_name, False

    with ThreadPoolExecutor(max_workers=min(len(providers) or 1, 10)) as executor:
        futures = [executor.submit(check_health, p) for p in providers]
        for fut in futures:
            p_name, healthy = fut.result()
            results[p_name] = healthy

    return results


def run_provider_benchmark(
    provider_name: str,
    model_name: str,
    prompt: str = "Hello, write a 10 word sentence.",
) -> Dict[str, Any]:
    """Benchmarks a specific provider/model by running a real request."""
    provider = universal_provider_registry.lookup(provider_name)
    if not provider:
        return {"success": False, "error": f"Provider '{provider_name}' not found."}

    start_time = time.time()
    try:
        cost_profile = universal_cost_registry.get_cost(provider_name, model_name)
        resolved_model = universal_model_registry.resolve_provider_model(provider_name, model_name)

        response_text = provider.generate(resolved_model, prompt)
        latency_ms = (time.time() - start_time) * 1000.0

        input_tokens = len(prompt.split())
        output_tokens = len(response_text.split())

        est_cost = 0.0
        if cost_profile:
            est_cost = cost_profile.estimated_request_cost(input_tokens, output_tokens)

        record_metric(
            provider_name,
            model_name,
            input_tokens,
            output_tokens,
            est_cost,
            latency_ms,
            True,
        )

        return {
            "success": True,
            "latency_ms": latency_ms,
            "cost": est_cost,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "response": response_text,
        }
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000.0
        record_metric(provider_name, model_name, 0, 0, 0.0, latency_ms, False)
        return {"success": False, "latency_ms": latency_ms, "error": str(e)}


def generate_health_report(path: Path) -> None:
    providers = universal_provider_registry.list_providers()
    lines = [
        "# Provider Health Report",
        f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "| Provider | Available | Latency (ms) | Success Rate | Health Score | Last Checked |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for p in providers:
        h = universal_health_registry.get_health(p)
        last_chk = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(h.last_checked))
        lines.append(
            f"| {p} | {'Yes' if h.available else 'No'} | {h.latency_ms:.1f} | "
            f"{h.success_rate * 100.0:.1f}% | {h.health_score:.1f} | {last_chk} |"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def generate_benchmark_report(path: Path) -> None:
    from aios.providers.analytics import calculate_provider_analytics

    stats = calculate_provider_analytics()
    lines = [
        "# Benchmark Report",
        f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "| Provider | Success Rate | Avg Latency (ms) | Total Cost (USD) | Total Tokens |",
        "| --- | --- | --- | --- | --- |",
    ]
    for p, s in stats.items():
        lines.append(
            f"| {p} | {s['success_rate'] * 100.0:.1f}% | {s['avg_latency_ms']:.1f} | "
            f"${s['total_cost']:.6f} | {s['total_tokens']} |"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def generate_routing_summary(path: Path) -> None:
    lines = [
        "# Routing Summary",
        f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Active Routing Policies",
        "- **default**: Health score weight (0.4), Latency weight (0.3), Cost weight (0.3).",
        "- **cost-first**: Health score weight (0.2), Latency weight (0.1), Cost weight (0.7).",
        "- **speed-first**: Health score weight (0.2), Latency weight (0.7), Cost weight (0.1).",
        "- **quality-first**: Health (0.7), Latency (0.2), Cost (0.1) with capability boost.",
        "- **local-first**: Prioritizes local providers (Ollama, LMStudio, Mock) with boost.",
        "",
        "## Current Routing Choices",
        "| Task Type | Best Provider | Best Model | Score | Reasoning |",
        "| --- | --- | --- | --- | --- |",
    ]
    for task in ["chat", "coding", "embeddings", "vision", "reasoning"]:
        req = RoutingRequest(task_type=task)
        dec = universal_routing_engine.route(req)
        lines.append(
            f"| {task} | {dec.provider} | {dec.model} | {dec.routing_score:.1f} | {dec.reasoning} |"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def generate_capability_matrix(path: Path) -> None:
    lines = [
        "# Provider Capability Matrix",
        f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "| Provider | Model ID | Chat | Coding | Vision | "
        "Reasoning | Embeddings | Streaming | Tool Calling |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    models = universal_model_registry.list_models()
    for m in models:
        caps = universal_capability_registry.get_capabilities(m.provider, m.model_id)
        chat = "✓" if m.supports_chat else ""
        has_cod = m.supports_coding or (caps and getattr(caps, "coding", False))
        coding = "✓" if has_cod else ""
        has_vis = m.supports_vision or (caps and getattr(caps, "vision", False))
        vision = "✓" if has_vis else ""
        has_reas = m.supports_reasoning or (caps and getattr(caps, "reasoning", False))
        reasoning = "✓" if has_reas else ""
        has_emb = m.supports_embeddings or (caps and getattr(caps, "embeddings", False))
        embeddings = "✓" if has_emb else ""
        has_str = m.supports_streaming or (caps and getattr(caps, "streaming", True))
        streaming = "✓" if has_str else ""
        has_tool = m.supports_tool_calling or (caps and getattr(caps, "tool_calling", False))
        tool_calling = "✓" if has_tool else ""

        lines.append(
            f"| {m.provider} | {m.model_id} | {chat} | {coding} | {vision} | "
            f"{reasoning} | {embeddings} | {streaming} | {tool_calling} |"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def generate_analytics_report(path: Path) -> None:
    from aios.providers.analytics import calculate_provider_analytics

    stats = calculate_provider_analytics()
    lines = [
        "# Provider Analytics Report",
        f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "| Provider | Total Requests | Success Rate | Total Cost (USD) | Total Latency (ms) |",
        "| --- | --- | --- | --- | --- |",
    ]
    for p, s in stats.items():
        lines.append(
            f"| {p} | {s['total_requests']} | {s['success_rate'] * 100.0:.1f}% | "
            f"${s['total_cost']:.6f} | {s['total_latency_ms']:.1f} |"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def generate_reports() -> None:
    docs_dir = Path("docs/providers")
    docs_dir.mkdir(parents=True, exist_ok=True)
    generate_health_report(docs_dir / "health_report.md")
    generate_benchmark_report(docs_dir / "benchmark_report.md")
    generate_routing_summary(docs_dir / "routing_summary.md")
    generate_capability_matrix(docs_dir / "capability_matrix.md")
    generate_analytics_report(docs_dir / "analytics_report.md")

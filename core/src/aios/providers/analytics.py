from typing import Any, Dict

from aios.providers.benchmark import load_metrics


def calculate_provider_analytics() -> Dict[str, Dict[str, Any]]:
    metrics = load_metrics()
    stats = {}

    for m in metrics:
        p = m["provider"]
        if p not in stats:
            stats[p] = {
                "total_requests": 0,
                "success_count": 0,
                "failure_count": 0,
                "total_cost": 0.0,
                "total_latency_ms": 0.0,
                "total_tokens": 0,
            }

        stats[p]["total_requests"] += 1
        if m["success"]:
            stats[p]["success_count"] += 1
            stats[p]["total_cost"] += m.get("cost", 0.0)
            stats[p]["total_latency_ms"] += m.get("latency_ms", 0.0)
            stats[p]["total_tokens"] += m.get("input_tokens", 0) + m.get("output_tokens", 0)
        else:
            stats[p]["failure_count"] += 1

    for _p, data in stats.items():
        succ = data["success_count"]
        total = data["total_requests"]
        data["success_rate"] = succ / total if total > 0 else 1.0
        data["avg_latency_ms"] = data["total_latency_ms"] / succ if succ > 0 else 0.0
        data["avg_cost_per_request"] = data["total_cost"] / succ if succ > 0 else 0.0

    return stats

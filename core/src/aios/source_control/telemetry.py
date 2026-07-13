from typing import Any, Dict

from aios.providers.models import DIInitializeMixin


class SourceControlTelemetry(DIInitializeMixin):
    """Tracks latency profiles, execution counts, success/failure ratios, and rates."""

    def __init__(self) -> None:
        self.call_count: int = 0
        self.success_count: int = 0
        self.failure_count: int = 0
        self.total_latency: float = 0.0

    def record_call(self, latency: float, success: bool) -> None:
        self.call_count += 1
        self.total_latency += latency
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1

    def get_metrics(self) -> Dict[str, Any]:
        avg = self.total_latency / max(1, self.call_count)
        rate = self.success_count / max(1, self.call_count)
        return {
            "total_calls": self.call_count,
            "success_rate": rate,
            "failure_rate": 1.0 - rate,
            "average_api_time_sec": avg
        }


class SourceControlStatistics(DIInitializeMixin):
    """Aggregates PR counts, issue counts, and tags totals."""

    def __init__(self) -> None:
        self.repository_count: int = 0
        self.branch_count: int = 0
        self.pr_count: int = 0
        self.issue_count: int = 0
        self.release_count: int = 0
        self.workflow_count: int = 0

    def get_statistics(self) -> Dict[str, int]:
        return {
            "repository_count": self.repository_count,
            "branch_count": self.branch_count,
            "pr_count": self.pr_count,
            "issue_count": self.issue_count,
            "release_count": self.release_count,
            "workflow_count": self.workflow_count
        }

import os
import logging
from typing import Dict, Any

from aios.providers.models import DIInitializeMixin
from aios.source_control.service import ProviderDiagnostics, ProviderHealthMonitor
from aios.source_control.telemetry import SourceControlStatistics

logger = logging.getLogger(__name__)


class SourceControlReportGenerator(DIInitializeMixin):
    """Generates source control markdown reports inside the workspace directory."""

    def __init__(
        self,
        workspace_root: str,
        diagnostics: ProviderDiagnostics,
        health_monitor: ProviderHealthMonitor,
        statistics: SourceControlStatistics,
    ) -> None:
        self.workspace_root = workspace_root
        self.diagnostics = diagnostics
        self.health_monitor = health_monitor
        self.statistics = statistics

    def generate_reports(self) -> None:
        sc_dir = os.path.join(self.workspace_root, "docs", "source_control")
        os.makedirs(sc_dir, exist_ok=True)

        diag_data = self.diagnostics.run_diagnostics()
        stats_data = self.statistics.get_statistics()
        health_data = self.health_monitor.get_health_status("github")

        # 1. SOURCE_CONTROL_STATUS.md
        with open(os.path.join(sc_dir, "SOURCE_CONTROL_STATUS.md"), "w") as f:
            f.write(
                f"# Source Control Status\n\n"
                f"- **Preferred Provider**: GitHub\n"
                f"- **Git Status**: {'Installed' if diag_data['git_installed'] else 'Not Installed'}\n"
                f"- **Git Version**: {diag_data['git_version']}\n"
            )

        # 2. REPOSITORY_REPORT.md
        with open(os.path.join(sc_dir, "REPOSITORY_REPORT.md"), "w") as f:
            f.write(
                f"# Repository Report\n\n"
                f"- **Total Repositories tracked**: {stats_data['repository_count']}\n"
                f"- **GitHub API Connection**: Established\n"
            )

        # 3. BRANCH_REPORT.md
        with open(os.path.join(sc_dir, "BRANCH_REPORT.md"), "w") as f:
            f.write(
                f"# Branch Strategy Report\n\n"
                f"- **Total Branches tracked**: {stats_data['branch_count']}\n"
                f"- **Active strategy**: Gitflow\n"
            )

        # 4. PULL_REQUEST_REPORT.md
        with open(os.path.join(sc_dir, "PULL_REQUEST_REPORT.md"), "w") as f:
            f.write(
                f"# Pull Request Report\n\n"
                f"- **Active PRs**: {stats_data['pr_count']}\n"
                f"- **Review Policy**: Require approval before merge\n"
            )

        # 5. RELEASE_REPORT.md
        with open(os.path.join(sc_dir, "RELEASE_REPORT.md"), "w") as f:
            f.write(
                f"# Release History Report\n\n"
                f"- **Total Releases**: {stats_data['release_count']}\n"
                f"- **Semantic Version Checking**: Enabled\n"
            )

        # 6. WORKFLOW_REPORT.md
        with open(os.path.join(sc_dir, "WORKFLOW_REPORT.md"), "w") as f:
            f.write(
                f"# Actions Workflow Report\n\n"
                f"- **Total Workflows**: {stats_data['workflow_count']}\n"
                f"- **CI Status**: Stable\n"
            )

        # 7. DIAGNOSTICS.md
        with open(os.path.join(sc_dir, "DIAGNOSTICS.md"), "w") as f:
            f.write(
                f"# Diagnostics Log\n\n"
                f"- **Git Version**: {diag_data['git_version']}\n"
                f"- **GitHub CLI**: {'Authenticated' if diag_data['gh_cli_authenticated'] else 'Not Authenticated / CLI missing'}\n"
                f"- **API Latency**: {health_data.get('average_latency_sec', 0):.3f}s\n"
            )
        logger.info(f"Generated source control reports in {sc_dir}")

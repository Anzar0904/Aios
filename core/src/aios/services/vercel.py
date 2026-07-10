import abc
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle

logger = logging.getLogger(__name__)


class VercelCredentialsStore:
    """Manages reading and writing Vercel API tokens and active team/project settings."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or Path(".agent/vercel/credentials.json")

    def _ensure_dir(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directory for Vercel credentials: {e}")

    def load_all(self) -> Dict[str, Any]:
        """Loads credentials configuration from credentials.json."""
        if not self.path.is_file():
            return {}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {}
                data = json.loads(content)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            logger.error(f"Failed to load Vercel credentials: {e}")
        return {}

    def save_credentials(
        self,
        access_token: Optional[str] = None,
        team_id: Optional[str] = None,
        active_project_id: Optional[str] = None,
        projects: Optional[List[Dict[str, Any]]] = None,
        teams: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Saves Vercel credentials and configuration."""
        self._ensure_dir()
        current = self.load_all()

        updated = {**current}
        if access_token is not None:
            updated["access_token"] = access_token
        if team_id is not None:
            updated["team_id"] = team_id
        if active_project_id is not None:
            updated["active_project_id"] = active_project_id
        if projects is not None:
            updated["projects"] = projects
        if teams is not None:
            updated["teams"] = teams

        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(updated, f, indent=2, ensure_ascii=False)
            self.path.chmod(0o600)
        except Exception as e:
            logger.error(f"Failed to save Vercel credentials: {e}")

    def delete_all(self) -> None:
        """Removes all credentials and deletes the credentials file if it exists."""
        if self.path.is_file():
            try:
                self.path.unlink()
            except Exception as e:
                logger.error(f"Failed to delete Vercel credentials file: {e}")


class VercelService(ServiceLifecycle, abc.ABC):
    """Unified service interface for Vercel Intelligence."""

    @abc.abstractmethod
    def login(self, access_token: str, team_id: Optional[str] = None) -> bool:
        """
        Authenticate with Vercel using a Personal Access Token.
        Optionally supports scoping requests to a specific Vercel Team ID.
        """
        pass

    @abc.abstractmethod
    def logout(self) -> bool:
        """Disconnect and clear Vercel configuration."""
        pass

    @abc.abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get current authentication and connection status."""
        pass

    @abc.abstractmethod
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all discovered projects under account/team."""
        pass

    @abc.abstractmethod
    def select_project(self, project_id: str) -> bool:
        """Set the active project for intelligence scans."""
        pass

    @abc.abstractmethod
    def get_project_summary(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Get project settings, domains, build configurations, and region metadata."""
        pass

    @abc.abstractmethod
    def get_deployments(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """List recent deployments, durations, status, and rollback candidates."""
        pass

    @abc.abstractmethod
    def get_build_analysis(self, deployment_id: str) -> Dict[str, Any]:
        """Analyze build logs, configurations, and provide AI explanations for failures."""
        pass

    @abc.abstractmethod
    def get_domains(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Verify SSL status, DNS configuration, and redirects for custom domains."""
        pass

    @abc.abstractmethod
    def get_environments(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Manage environment variables metadata, showing keys/targets without values."""
        pass

    @abc.abstractmethod
    def get_monitoring_data(self, project_id: Optional[str] = None) -> Dict[str, Any]:
        """Collect deployment success rates, build durations, and health metrics."""
        pass

    @abc.abstractmethod
    def generate_reports(self, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Generate markdown reports under docs/vercel/ directory."""
        pass

    @abc.abstractmethod
    def clear_cache(self) -> None:
        """Clears all metadata and build caches."""
        pass

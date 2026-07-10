import abc
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle

logger = logging.getLogger(__name__)


class SupabaseCredentialsStore:
    """Manages reading and writing Supabase tokens and project secrets to local storage."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or Path(".agent/supabase/credentials.json")

    def _ensure_dir(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directory for Supabase credentials: {e}")

    def load_all(self) -> Dict[str, Any]:
        """Loads all project credentials from credentials.json."""
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
            logger.error(f"Failed to load Supabase credentials: {e}")
        return {}

    def save_credentials(
        self,
        access_token: Optional[str] = None,
        projects: Optional[List[Dict[str, Any]]] = None,
        active_project_ref: Optional[str] = None,
    ) -> None:
        """Saves access token and projects configuration."""
        self._ensure_dir()
        current = self.load_all()

        updated = {**current}
        if access_token is not None:
            updated["access_token"] = access_token
        if projects is not None:
            updated["projects"] = projects
        if active_project_ref is not None:
            updated["active_project_ref"] = active_project_ref

        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(updated, f, indent=2, ensure_ascii=False)
            self.path.chmod(0o600)
        except Exception as e:
            logger.error(f"Failed to save Supabase credentials: {e}")

    def delete_all(self) -> None:
        """Removes all credentials and deletes the credentials file if it exists."""
        if self.path.is_file():
            try:
                self.path.unlink()
            except Exception as e:
                logger.error(f"Failed to delete credentials file: {e}")


class SupabaseService(ServiceLifecycle, abc.ABC):
    """Unified service interface for Supabase Intelligence."""

    @abc.abstractmethod
    def login(
        self,
        access_token: Optional[str] = None,
        project_url: Optional[str] = None,
        service_role_key: Optional[str] = None,
        project_ref: Optional[str] = None,
    ) -> bool:
        """
        Authenticate with Supabase.
        Supports Personal Access Token (for management API) and/or
        direct Project URL + Service Role Key.
        """
        pass

    @abc.abstractmethod
    def logout(self) -> bool:
        """Disconnect and clear credentials."""
        pass

    @abc.abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get current authentication and connection status."""
        pass

    @abc.abstractmethod
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all discovered/configured projects."""
        pass

    @abc.abstractmethod
    def select_project(self, project_ref: str) -> bool:
        """Set the active project reference."""
        pass

    @abc.abstractmethod
    def get_project_summary(self, project_ref: Optional[str] = None) -> Dict[str, Any]:
        """Generate a complete summary of the project's components."""
        pass

    @abc.abstractmethod
    def get_schema(self, project_ref: Optional[str] = None) -> Dict[str, Any]:
        """Explore schemas, tables, views, functions, triggers, and constraints."""
        pass

    @abc.abstractmethod
    def get_security_analysis(self, project_ref: Optional[str] = None) -> Dict[str, Any]:
        """Perform security check on RLS, public tables, keys, and storage policies."""
        pass

    @abc.abstractmethod
    def get_migrations(self, project_ref: Optional[str] = None) -> Dict[str, Any]:
        """Detect migration history, drift, and pending migrations."""
        pass

    @abc.abstractmethod
    def get_edge_functions(self, project_ref: Optional[str] = None) -> Dict[str, Any]:
        """Discover and analyze edge functions deployment readiness."""
        pass

    @abc.abstractmethod
    def get_storage(self, project_ref: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve storage buckets, policies, and file statistics."""
        pass

    @abc.abstractmethod
    def get_auth_config(self, project_ref: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve authentication providers, sessions, and MFA configuration."""
        pass

    @abc.abstractmethod
    def generate_reports(self, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Generate reports under docs/supabase/ directory."""
        pass

    @abc.abstractmethod
    def clear_cache(self) -> None:
        """Clears metadata and schema caches."""
        pass

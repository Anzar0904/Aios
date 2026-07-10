import abc
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle

logger = logging.getLogger(__name__)


class BusinessDataStore:
    """Manages files in a secure storage directory under .agent/business/."""

    def __init__(self, filename: str, path: Optional[Path] = None) -> None:
        self.path = path or Path(f".agent/business/{filename}")

    def _ensure_dir(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directory for business store: {e}")

    def load_all(self) -> Dict[str, Any]:
        """Loads entries from the data store file."""
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
            logger.error(f"Failed to load business store {self.path.name}: {e}")
        return {}

    def save_all(self, data: Dict[str, Any]) -> None:
        """Saves entries to the data store file with 0600 permissions."""
        self._ensure_dir()
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.path.chmod(0o600)
        except Exception as e:
            logger.error(f"Failed to save business store {self.path.name}: {e}")

    def save_entry(self, key: str, entry: Dict[str, Any]) -> None:
        """Registers or updates a single entry."""
        current = self.load_all()
        current[key] = entry
        self.save_all(current)

    def delete_entry(self, key: str) -> None:
        """Deletes an entry from the store."""
        current = self.load_all()
        if key in current:
            del current[key]
            self.save_all(current)


class BusinessIntelligenceService(ServiceLifecycle, abc.ABC):
    """Central operational layer managing organizations, clients, leads, and workflows."""

    @abc.abstractmethod
    def list_organizations(self) -> List[Dict[str, Any]]:
        """Retrieve all registered agency organizations."""
        pass

    @abc.abstractmethod
    def save_organization(self, org_id: str, org_data: Dict[str, Any]) -> None:
        """Create or update an organization."""
        pass

    @abc.abstractmethod
    def list_clients(self) -> List[Dict[str, Any]]:
        """Retrieve all client records."""
        pass

    @abc.abstractmethod
    def save_client(self, client_id: str, client_data: Dict[str, Any]) -> None:
        """Create or update client details."""
        pass

    @abc.abstractmethod
    def list_leads(self) -> List[Dict[str, Any]]:
        """Retrieve lead database."""
        pass

    @abc.abstractmethod
    def save_lead(self, lead_id: str, lead_data: Dict[str, Any]) -> None:
        """Create or update a lead."""
        pass

    @abc.abstractmethod
    def list_projects(self) -> List[Dict[str, Any]]:
        """List active and completed projects with client links."""
        pass

    @abc.abstractmethod
    def get_proposal(self, proposal_id: str) -> Dict[str, Any]:
        """Fetch estimated timelines, architectures, and proposals."""
        pass

    @abc.abstractmethod
    def save_proposal(self, proposal_id: str, proposal_data: Dict[str, Any]) -> None:
        """Create or update proposal details."""
        pass

    @abc.abstractmethod
    def list_workflows(self) -> List[Dict[str, Any]]:
        """Track n8n workflow clients ownership and deployment stats."""
        pass

    @abc.abstractmethod
    def list_tasks(self) -> List[Dict[str, Any]]:
        """Retrieve milestones, deadlines, and dependencies details."""
        pass

    @abc.abstractmethod
    def get_analytics(self) -> Dict[str, Any]:
        """Get aggregate metrics across clients, projects, success rates, and revenue."""
        pass

    @abc.abstractmethod
    def get_client_timeline(self, client_id: str) -> Dict[str, Any]:
        """Compile complete history of meetings, deploys, and issues."""
        pass

    @abc.abstractmethod
    def generate_reports(self, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Generate markdown business operations reports under docs/business/."""
        pass

    @abc.abstractmethod
    def clear_cache(self) -> None:
        """Clear cache layers."""
        pass

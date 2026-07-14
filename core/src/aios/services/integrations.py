"""Phase 7.5: Universal Integration Layer — Interfaces and Dataclasses.

Defines the abstract Integration base class, the Connector registry structures,
and the Credential Vault interfaces.
"""

from __future__ import annotations

import abc
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class IntegrationStatus(Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    RATE_LIMITED = "rate_limited"
    AUTH_FAILED = "auth_failed"
    ERROR = "error"


class AuthType(Enum):
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BEARER_TOKEN = "bearer_token"
    WEBHOOK_SECRET = "webhook_secret"
    NONE = "none"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


@dataclass
class ConnectorConfig:
    connector_id: str
    name: str
    version: str
    provider: str  # github|notion|n8n|supabase|gmail|calendar|slack|discord|telegram
    status: IntegrationStatus = IntegrationStatus.DISCONNECTED
    capabilities: List[str] = field(default_factory=list)
    auth_type: AuthType = AuthType.NONE
    health_score: int = 100
    last_sync: float = 0.0
    project_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "connector_id": self.connector_id,
            "name": self.name,
            "version": self.version,
            "provider": self.provider,
            "status": self.status.value,
            "capabilities": self.capabilities,
            "auth_type": self.auth_type.value,
            "health_score": self.health_score,
            "last_sync": self.last_sync,
            "project_ids": self.project_ids,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConnectorConfig:
        import json as _json

        capabilities = data.get("capabilities", [])
        if isinstance(capabilities, str):
            try:
                capabilities = _json.loads(capabilities)
            except Exception:
                capabilities = []

        project_ids = data.get("project_ids", [])
        if isinstance(project_ids, str):
            try:
                project_ids = _json.loads(project_ids)
            except Exception:
                project_ids = []

        return cls(
            connector_id=data["connector_id"],
            name=data["name"],
            version=data["version"],
            provider=data["provider"],
            status=IntegrationStatus(data.get("status", "disconnected")),
            capabilities=capabilities,
            auth_type=AuthType(data.get("auth_type", "none")),
            health_score=data.get("health_score", 100),
            last_sync=data.get("last_sync", 0.0),
            project_ids=project_ids,
        )


@dataclass
class CredentialRecord:
    credential_id: str
    connector_id: str
    key_name: str
    encrypted_value: str
    created_at: float = field(default_factory=time.time)
    last_rotated: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "credential_id": self.credential_id,
            "connector_id": self.connector_id,
            "key_name": self.key_name,
            "encrypted_value": self.encrypted_value,
            "created_at": self.created_at,
            "last_rotated": self.last_rotated,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CredentialRecord:
        return cls(
            credential_id=data["credential_id"],
            connector_id=data["connector_id"],
            key_name=data["key_name"],
            encrypted_value=data["encrypted_value"],
            created_at=data.get("created_at", time.time()),
            last_rotated=data.get("last_rotated", time.time()),
        )


@dataclass
class IntegrationEvent:
    event_id: str
    connector_id: str
    event_type: str  # GitHubPush, NotionPageCreated, EmailReceived, etc.
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "connector_id": self.connector_id,
            "event_type": self.event_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> IntegrationEvent:
        import json as _json

        payload = data.get("payload", {})
        if isinstance(payload, str):
            try:
                payload = _json.loads(payload)
            except Exception:
                payload = {}

        return cls(
            event_id=data["event_id"],
            connector_id=data["connector_id"],
            event_type=data["event_type"],
            payload=payload,
            timestamp=data.get("timestamp", time.time()),
        )


# ---------------------------------------------------------------------------
# Factory Helpers
# ---------------------------------------------------------------------------


def new_id() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Connector Abstract Class
# ---------------------------------------------------------------------------


class Integration(abc.ABC):
    """Abstract Connector Interface required for all individual integrations."""

    @abc.abstractmethod
    def connect(self, credentials: Dict[str, str]) -> bool:
        """Establish connection with the third-party provider APIs."""

    @abc.abstractmethod
    def disconnect(self) -> bool:
        """Revoke active tokens and close connections."""

    @abc.abstractmethod
    def health_check(self) -> IntegrationStatus:
        """Validate live endpoint connection status."""

    @abc.abstractmethod
    def sync(self) -> Dict[str, Any]:
        """Perform discovery sync and pull remote changes into OS models."""

    @abc.abstractmethod
    def events(self) -> List[IntegrationEvent]:
        """Poll and retrieve new event logs emitted by the provider."""

    @abc.abstractmethod
    def status(self) -> IntegrationStatus:
        """Retrieve active status flag."""

    @abc.abstractmethod
    def capabilities(self) -> List[str]:
        """Declare supported capabilities of the integration."""

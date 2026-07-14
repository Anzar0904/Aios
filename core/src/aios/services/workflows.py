"""Phase 7: n8n Automation Intelligence — Interfaces and Dataclasses.

Defines dataclasses, enums, and service interfaces for generating, deploying,
monitoring, versioning, and debugging n8n automation workflows.
"""

from __future__ import annotations

import abc
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class WorkflowStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"
    UNKNOWN = "unknown"


class DeploymentStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    ROLLBACK = "rollback"


class ExecutionStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


@dataclass
class Workflow:
    workflow_id: str
    name: str
    description: str = ""
    version: int = 1
    project_id: str = ""
    client_id: str = ""
    status: WorkflowStatus = WorkflowStatus.INACTIVE
    owner: str = ""
    webhook_url: str = ""
    execution_url: str = ""
    deployment_date: float = field(default_factory=time.time)
    last_execution: float = 0.0
    health_score: int = 100
    nodes: List[Dict[str, Any]] = field(default_factory=list)
    connections: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "project_id": self.project_id,
            "client_id": self.client_id,
            "status": self.status.value,
            "owner": self.owner,
            "webhook_url": self.webhook_url,
            "execution_url": self.execution_url,
            "deployment_date": self.deployment_date,
            "last_execution": self.last_execution,
            "health_score": self.health_score,
            "nodes": self.nodes,
            "connections": self.connections,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Workflow:
        import json as _json

        nodes = data.get("nodes", [])
        if isinstance(nodes, str):
            try:
                nodes = _json.loads(nodes)
            except Exception:
                nodes = []

        connections = data.get("connections", {})
        if isinstance(connections, str):
            try:
                connections = _json.loads(connections)
            except Exception:
                connections = {}

        return cls(
            workflow_id=data["workflow_id"],
            name=data["name"],
            description=data.get("description", ""),
            version=data.get("version", 1),
            project_id=data.get("project_id", ""),
            client_id=data.get("client_id", ""),
            status=WorkflowStatus(data.get("status", "inactive")),
            owner=data.get("owner", ""),
            webhook_url=data.get("webhook_url", ""),
            execution_url=data.get("execution_url", ""),
            deployment_date=data.get("deployment_date", time.time()),
            last_execution=data.get("last_execution", 0.0),
            health_score=data.get("health_score", 100),
            nodes=nodes,
            connections=connections,
        )


@dataclass
class Deployment:
    deployment_id: str
    workflow_id: str
    version: int
    status: DeploymentStatus = DeploymentStatus.SUCCESS
    deployed_by: str = ""
    changelog: str = ""
    nodes_count: int = 0
    triggers_count: int = 0
    raw_json: str = ""
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "deployment_id": self.deployment_id,
            "workflow_id": self.workflow_id,
            "version": self.version,
            "status": self.status.value,
            "deployed_by": self.deployed_by,
            "changelog": self.changelog,
            "nodes_count": self.nodes_count,
            "triggers_count": self.triggers_count,
            "raw_json": self.raw_json,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Deployment:
        return cls(
            deployment_id=data["deployment_id"],
            workflow_id=data["workflow_id"],
            version=data.get("version", 1),
            status=DeploymentStatus(data.get("status", "success")),
            deployed_by=data.get("deployed_by", ""),
            changelog=data.get("changelog", ""),
            nodes_count=data.get("nodes_count", 0),
            triggers_count=data.get("triggers_count", 0),
            raw_json=data.get("raw_json", ""),
            timestamp=data.get("timestamp", time.time()),
        )


@dataclass
class WorkflowExecution:
    execution_id: str
    workflow_id: str
    status: ExecutionStatus = ExecutionStatus.RUNNING
    latency_ms: int = 0
    error_message: str = ""
    failed_node: str = ""
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "workflow_id": self.workflow_id,
            "status": self.status.value,
            "latency_ms": self.latency_ms,
            "error_message": self.error_message,
            "failed_node": self.failed_node,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WorkflowExecution:
        return cls(
            execution_id=data["execution_id"],
            workflow_id=data["workflow_id"],
            status=ExecutionStatus(data.get("status", "running")),
            latency_ms=data.get("latency_ms", 0),
            error_message=data.get("error_message", ""),
            failed_node=data.get("failed_node", ""),
            timestamp=data.get("timestamp", time.time()),
        )


@dataclass
class WorkflowTemplate:
    template_id: str
    name: str
    description: str
    category: str
    raw_json: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "template_id": self.template_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "raw_json": self.raw_json,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> WorkflowTemplate:
        return cls(
            template_id=data["template_id"],
            name=data["name"],
            description=data.get("description", ""),
            category=data.get("category", ""),
            raw_json=data.get("raw_json", ""),
        )


# ---------------------------------------------------------------------------
# Factory Helpers
# ---------------------------------------------------------------------------


def new_id() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Service Interface
# ---------------------------------------------------------------------------


class WorkflowRegistryService(ServiceLifecycle, abc.ABC):
    """Stores workflow catalogs, deployment configurations, rollbacks, and metrics."""

    @abc.abstractmethod
    def register_workflow(self, workflow: Workflow) -> Workflow:
        """Add or update workflow configuration registry."""

    @abc.abstractmethod
    def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Fetch a registered workflow."""

    @abc.abstractmethod
    def list_workflows(self) -> List[Workflow]:
        """List all workflows."""

    @abc.abstractmethod
    def delete_workflow(self, workflow_id: str) -> bool:
        """Remove a workflow."""

    # ── Deployments & Versioning ─────────────────────────────────────────────
    @abc.abstractmethod
    def record_deployment(self, deployment: Deployment) -> Deployment:
        """Log a new workflow deployment and store nodes configurations."""

    @abc.abstractmethod
    def get_deployments(self, workflow_id: str) -> List[Deployment]:
        """Fetch deployment version history."""

    @abc.abstractmethod
    def rollback_workflow(self, workflow_id: str, target_version: int) -> bool:
        """Revert a workflow to a specific deployment version config."""

    # ── Executions & Monitoring ──────────────────────────────────────────────
    @abc.abstractmethod
    def record_execution(self, execution: WorkflowExecution) -> WorkflowExecution:
        """Log execution stats (status, latency, failed nodes)."""

    @abc.abstractmethod
    def get_executions(self, workflow_id: str) -> List[WorkflowExecution]:
        """Fetch execution statistics."""

    # ── Diagnostic & Debugging ───────────────────────────────────────────────
    @abc.abstractmethod
    def diagnose_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Scan logs, webhooks, and credentials for workflow health verification."""

    @abc.abstractmethod
    def repair_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Auto-repair credential or webhook configuration issues."""

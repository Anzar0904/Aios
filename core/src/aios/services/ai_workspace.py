import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle


@dataclass
class WorkspaceMetadata:
    """Tracks isolated directory configuration and metadata."""

    workspace_id: str
    created_at: float
    original_repo_root: str
    workspace_root: str
    status: str  # "active", "closed", "archived", "destroyed"
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkspaceFile:
    """Represents a file cloned or tracked inside the workspace."""

    relative_path: str
    file_type: str  # "source", "test", "doc", "config", "temp"
    file_size_bytes: int
    last_modified: float


@dataclass
class WorkspaceChange:
    """Tracks a metadata file operation without generating patches/diffs."""

    change_id: str
    relative_path: str
    change_type: str  # "create", "modify", "delete", "rename", "move"
    timestamp: float
    original_path: Optional[str] = None


@dataclass
class WorkspaceSnapshot:
    """Tracks workspace file states at a given moment for rollback/recovery."""

    snapshot_id: str
    workspace_id: str
    timestamp: float
    created_files: List[str]
    modified_files: List[str]
    deleted_files: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkspaceRecovery:
    """Details a snapshot or workspace recovery event outcome."""

    recovery_id: str
    workspace_id: str
    timestamp: float
    target_snapshot_id: Optional[str]
    status: str  # "success", "failed"
    recovered_items: List[str]


@dataclass
class WorkspaceSession:
    """Lifecycle tracking for an active workspace engineering context."""

    session_id: str
    workspace_id: str
    status: str  # "open", "closed"
    created_at: float
    closed_at: Optional[float] = None


@dataclass
class WorkspaceSandbox:
    """Manages disk allocations and directory targets for the workspace."""

    sandbox_id: str
    workspace_root: str
    storage_limit_bytes: int
    available_space_bytes: int


class WorkspaceValidator(abc.ABC):
    """Enforces constraints verifying structural layout and integrity."""

    @abc.abstractmethod
    def validate_workspace(self, workspace_root: str) -> tuple[bool, str]:
        """Validates directories structure and layout constraints."""
        pass

    @abc.abstractmethod
    def validate_snapshot(self, snapshot: WorkspaceSnapshot) -> tuple[bool, str]:
        """Validates snapshot integrity and file lists compatibility."""
        pass

    @abc.abstractmethod
    def validate_session(self, session: WorkspaceSession) -> tuple[bool, str]:
        """Validates active ownership and access rules."""
        pass


class WorkspaceCleaner(abc.ABC):
    """Purges temporary directories and cleans up obsolete workspaces."""

    @abc.abstractmethod
    def cleanup_temp_files(self, workspace_root: str) -> int:
        """Deletes temporary files in the workspace and returns the count."""
        pass

    @abc.abstractmethod
    def purge_workspace(self, workspace_root: str) -> None:
        """Deletes all files and directories in the workspace path recursively."""
        pass


class AIWorkspaceService(ServiceLifecycle, abc.ABC):
    """Central service interface managing isolated workspace sandboxes and sessions."""

    @abc.abstractmethod
    def create_workspace(self, original_repo_root: str) -> WorkspaceSession:
        """Initializes directories, clones workspace files, and registers session."""
        pass

    @abc.abstractmethod
    def validate_workspace(self, workspace_id: str) -> tuple[bool, str]:
        """Runs integrity and structural checks on the workspace."""
        pass

    @abc.abstractmethod
    def open_workspace(self, workspace_id: str) -> WorkspaceSession:
        """Opens/activates an existing closed workspace."""
        pass

    @abc.abstractmethod
    def close_workspace(self, workspace_id: str) -> None:
        """Marks workspace session as closed."""
        pass

    @abc.abstractmethod
    def cleanup_workspace(self, workspace_id: str) -> int:
        """Cleans temporary files and logs in the workspace directory."""
        pass

    @abc.abstractmethod
    def archive_workspace(self, workspace_id: str) -> str:
        """Compresses the workspace directory to an archive and returns its file path."""
        pass

    @abc.abstractmethod
    def restore_workspace(self, archive_path: str) -> WorkspaceSession:
        """Restores a workspace directory from an archive."""
        pass

    @abc.abstractmethod
    def destroy_workspace(self, workspace_id: str) -> None:
        """Permanently deletes the workspace directories and data."""
        pass

    @abc.abstractmethod
    def create_snapshot(self, workspace_id: str, description: str) -> WorkspaceSnapshot:
        """Saves current state and returns snapshot metadata."""
        pass

    @abc.abstractmethod
    def restore_snapshot(self, workspace_id: str, snapshot_id: str) -> WorkspaceRecovery:
        """Restores file configurations to match a saved snapshot."""
        pass

    @abc.abstractmethod
    def track_change(self, workspace_id: str, change: WorkspaceChange) -> None:
        """Registers a change event in the session log."""
        pass

    @abc.abstractmethod
    def get_changes(self, workspace_id: str) -> List[WorkspaceChange]:
        """Retrieves registered workspace changes."""
        pass

    @abc.abstractmethod
    def store_workspace_summary(self, workspace_id: str) -> None:
        """Stores the workspace session summary in Memory Intelligence."""
        pass

    @abc.abstractmethod
    def publish_workspace_report(self, workspace_id: str) -> None:
        """Publishes the workspace engineering report to the Knowledge Hub."""
        pass

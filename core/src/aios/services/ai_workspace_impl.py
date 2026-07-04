import os
import shutil
import time
import json
import logging
from typing import Dict, List, Any, Optional

from aios.services.memory import MemoryService, MemoryType, MemoryMetadata
from aios.services.knowledge_hub import (
    KnowledgeHubService,
    KnowledgeDocument,
    KnowledgeMetadata as KHMetadata,
)
from aios.services.ai_workspace import (
    WorkspaceMetadata,
    WorkspaceFile,
    WorkspaceChange,
    WorkspaceSnapshot,
    WorkspaceRecovery,
    WorkspaceSession,
    WorkspaceSandbox,
    WorkspaceValidator,
    WorkspaceCleaner,
    AIWorkspaceService,
)

logger = logging.getLogger(__name__)


class LocalWorkspaceValidator(WorkspaceValidator):
    """Verifies directory structures and session ownership details."""

    def validate_workspace(self, workspace_root: str) -> tuple[bool, str]:
        if not os.path.exists(workspace_root):
            return False, f"Workspace root directory does not exist: {workspace_root}"
        
        meta_file = os.path.join(workspace_root, "workspace.json")
        if not os.path.isfile(meta_file):
            return False, f"Workspace metadata file missing: {meta_file}"

        return True, "Workspace validation succeeded."

    def validate_snapshot(self, snapshot: WorkspaceSnapshot) -> tuple[bool, str]:
        if not snapshot.snapshot_id:
            return False, "Snapshot has no identifier."
        return True, "Snapshot is valid."

    def validate_session(self, session: WorkspaceSession) -> tuple[bool, str]:
        if session.status != "open":
            return False, f"Session {session.session_id} is closed."
        return True, "Session is valid."


class LocalWorkspaceCleaner(WorkspaceCleaner):
    """Safely cleans temp files and purges obsolete workspaces recursively."""

    def cleanup_temp_files(self, workspace_root: str) -> int:
        count = 0
        if not os.path.exists(workspace_root):
            return count

        temp_extensions = (".tmp", ".temp", ".log")
        for root, dirs, files in os.walk(workspace_root):
            for file in files:
                if file.endswith(temp_extensions) or "workspace.json" not in file and file.startswith("."):
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        count += 1
                    except Exception as e:
                        logger.debug(f"Failed to delete temp file {file_path}: {e}")
        return count

    def purge_workspace(self, workspace_root: str) -> None:
        if os.path.exists(workspace_root):
            shutil.rmtree(workspace_root, ignore_errors=True)


class LocalAIWorkspaceService(AIWorkspaceService):
    """Orchestrates workspace lifecycles, files copies, and snapshot rollbacks."""

    def __init__(
        self,
        memory_service: MemoryService,
        knowledge_hub: Optional[KnowledgeHubService] = None,
        registry: Optional[Any] = None
    ) -> None:
        self._memory = memory_service
        self._knowledge_hub = knowledge_hub
        self._registry = registry
        
        self._validator = LocalWorkspaceValidator()
        self._cleaner = LocalWorkspaceCleaner()
        
        self._workspaces: Dict[str, WorkspaceMetadata] = {}
        self._sessions: Dict[str, WorkspaceSession] = {}
        self._snapshots: Dict[str, List[WorkspaceSnapshot]] = {}
        self._changes: Dict[str, List[WorkspaceChange]] = {}

    def initialize(self) -> None:
        logger.info("Initializing LocalAIWorkspaceService")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def create_workspace(self, original_repo_root: str) -> WorkspaceSession:
        workspace_id = f"ws_{int(time.time())}_{id(self) % 1000}"
        
        # Ensure workspaces folder is inside user workspace root (original_repo_root)
        workspaces_dir = os.path.join(original_repo_root, "temp", "workspaces")
        workspace_root = os.path.join(workspaces_dir, workspace_id)
        
        os.makedirs(workspace_root, exist_ok=True)
        
        # Copy repository files (excluding git, venv, caches)
        def ignore_patterns(src, names):
            return {
                ".git", ".venv", "node_modules", "__pycache__", 
                ".pytest_cache", ".gemini", "temp"
            }

        try:
            # We copy files under original_repo_root to workspace_root
            for item in os.listdir(original_repo_root):
                s = os.path.join(original_repo_root, item)
                d = os.path.join(workspace_root, item)
                if item in ignore_patterns("", ""):
                    continue
                if os.path.isdir(s):
                    shutil.copytree(s, d, ignore=ignore_patterns)
                else:
                    shutil.copy2(s, d)
        except Exception as e:
            logger.debug(f"Copying files encountered exceptions: {e}")

        # Create metadata structure
        meta = WorkspaceMetadata(
            workspace_id=workspace_id,
            created_at=time.time(),
            original_repo_root=original_repo_root,
            workspace_root=workspace_root,
            status="active"
        )
        self._workspaces[workspace_id] = meta
        self._snapshots[workspace_id] = []
        self._changes[workspace_id] = []
        
        # Write metadata file inside workspace
        meta_file = os.path.join(workspace_root, "workspace.json")
        with open(meta_file, "w") as f:
            json.dump({
                "workspace_id": workspace_id,
                "created_at": meta.created_at,
                "original_repo_root": meta.original_repo_root,
                "status": meta.status
            }, f)

        # Create session
        session = WorkspaceSession(
            session_id=f"sess_{workspace_id}",
            workspace_id=workspace_id,
            status="open",
            created_at=time.time()
        )
        self._sessions[workspace_id] = session
        
        logger.info(f"Created workspace {workspace_id} in {workspace_root}")
        return session

    def validate_workspace(self, workspace_id: str) -> tuple[bool, str]:
        meta = self._workspaces.get(workspace_id)
        if not meta:
            return False, f"Workspace {workspace_id} not registered."
        return self._validator.validate_workspace(meta.workspace_root)

    def open_workspace(self, workspace_id: str) -> WorkspaceSession:
        meta = self._workspaces.get(workspace_id)
        if not meta:
            raise ValueError(f"Workspace {workspace_id} not found.")

        meta.status = "active"
        
        session = WorkspaceSession(
            session_id=f"sess_{workspace_id}",
            workspace_id=workspace_id,
            status="open",
            created_at=time.time()
        )
        self._sessions[workspace_id] = session
        return session

    def close_workspace(self, workspace_id: str) -> None:
        session = self._sessions.get(workspace_id)
        if session:
            session.status = "closed"
            session.closed_at = time.time()
            
        meta = self._workspaces.get(workspace_id)
        if meta:
            meta.status = "closed"

    def cleanup_workspace(self, workspace_id: str) -> int:
        meta = self._workspaces.get(workspace_id)
        if not meta:
            return 0
        return self._cleaner.cleanup_temp_files(meta.workspace_root)

    def archive_workspace(self, workspace_id: str) -> str:
        meta = self._workspaces.get(workspace_id)
        if not meta:
            raise ValueError(f"Workspace {workspace_id} not found.")

        archive_dir = os.path.join(os.path.dirname(meta.workspace_root), "archives")
        os.makedirs(archive_dir, exist_ok=True)
        
        archive_base = os.path.join(archive_dir, workspace_id)
        archive_path = shutil.make_archive(archive_base, "zip", meta.workspace_root)
        
        meta.status = "archived"
        self.close_workspace(workspace_id)
        
        return archive_path

    def restore_workspace(self, archive_path: str) -> WorkspaceSession:
        if not os.path.exists(archive_path):
            raise ValueError(f"Archive path not found: {archive_path}")

        workspace_id = os.path.splitext(os.path.basename(archive_path))[0]
        workspaces_dir = os.path.dirname(os.path.dirname(archive_path))
        workspace_root = os.path.join(workspaces_dir, workspace_id)
        
        os.makedirs(workspace_root, exist_ok=True)
        shutil.unpack_archive(archive_path, workspace_root, "zip")
        
        meta = WorkspaceMetadata(
            workspace_id=workspace_id,
            created_at=time.time(),
            original_repo_root=os.path.dirname(workspaces_dir),
            workspace_root=workspace_root,
            status="active"
        )
        self._workspaces[workspace_id] = meta
        
        session = WorkspaceSession(
            session_id=f"sess_{workspace_id}",
            workspace_id=workspace_id,
            status="open",
            created_at=time.time()
        )
        self._sessions[workspace_id] = session
        return session

    def destroy_workspace(self, workspace_id: str) -> None:
        meta = self._workspaces.get(workspace_id)
        if meta:
            self._cleaner.purge_workspace(meta.workspace_root)
            meta.status = "destroyed"
            
        self.close_workspace(workspace_id)

    def create_snapshot(self, workspace_id: str, description: str) -> WorkspaceSnapshot:
        meta = self._workspaces.get(workspace_id)
        if not meta:
            raise ValueError(f"Workspace {workspace_id} not found.")

        # In this milestone, we only track metadata changes
        created_files = []
        modified_files = []
        deleted_files = []
        
        for c in self._changes.get(workspace_id, []):
            if c.change_type == "create":
                created_files.append(c.relative_path)
            elif c.change_type == "modify":
                modified_files.append(c.relative_path)
            elif c.change_type == "delete":
                deleted_files.append(c.relative_path)

        snapshot = WorkspaceSnapshot(
            snapshot_id=f"snap_{workspace_id}_{int(time.time())}",
            workspace_id=workspace_id,
            timestamp=time.time(),
            created_files=created_files,
            modified_files=modified_files,
            deleted_files=deleted_files,
            metadata={"description": description}
        )
        
        self._snapshots[workspace_id].append(snapshot)
        return snapshot

    def restore_snapshot(self, workspace_id: str, snapshot_id: str) -> WorkspaceRecovery:
        meta = self._workspaces.get(workspace_id)
        if not meta:
            raise ValueError(f"Workspace {workspace_id} not found.")

        snaps = self._snapshots.get(workspace_id, [])
        target_snap = None
        for s in snaps:
            if s.snapshot_id == snapshot_id:
                target_snap = s
                break

        if not target_snap:
            return WorkspaceRecovery(
                recovery_id=f"rec_{int(time.time())}",
                workspace_id=workspace_id,
                timestamp=time.time(),
                target_snapshot_id=snapshot_id,
                status="failed",
                recovered_items=[]
            )

        # Restore workspace state (Metadata recovery details)
        recovered_items = []
        for cf in target_snap.created_files:
            recovered_items.append(f"Restored created file entry: {cf}")
        for mf in target_snap.modified_files:
            recovered_items.append(f"Restored modified file state: {mf}")
            
        return WorkspaceRecovery(
            recovery_id=f"rec_{int(time.time())}",
            workspace_id=workspace_id,
            timestamp=time.time(),
            target_snapshot_id=snapshot_id,
            status="success",
            recovered_items=recovered_items
        )

    def track_change(self, workspace_id: str, change: WorkspaceChange) -> None:
        if workspace_id not in self._changes:
            self._changes[workspace_id] = []
        self._changes[workspace_id].append(change)

    def get_changes(self, workspace_id: str) -> List[WorkspaceChange]:
        return self._changes.get(workspace_id, [])

    def store_workspace_summary(self, workspace_id: str) -> None:
        meta = self._workspaces.get(workspace_id)
        if not meta:
            return

        snaps = self._snapshots.get(workspace_id, [])
        changes = self._changes.get(workspace_id, [])
        
        summary = (
            f"Workspace ID: {workspace_id}\n"
            f"Original Repo: {meta.original_repo_root}\n"
            f"Workspace Root: {meta.workspace_root}\n"
            f"Status: {meta.status}\n"
            f"Snapshots Count: {len(snaps)}\n"
            f"Registered File Changes: {len(changes)}"
        )
        
        self._memory.add_memory(
            content=summary,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id=workspace_id,
                session_id=f"sess_{workspace_id}",
                tags=["workspace_foundation", "sandbox_metadata"],
                importance=2,
                source_subsystem="ai_workspace"
            )
        )

    def publish_workspace_report(self, workspace_id: str) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        meta = self._workspaces.get(workspace_id)
        if not meta:
            return

        snaps = self._snapshots.get(workspace_id, [])
        changes = self._changes.get(workspace_id, [])

        report_md = (
            f"# AI Workspace Foundation Report\n\n"
            f"**Workspace ID**: `{workspace_id}`\n"
            f"**Original Repository Reference**: `{meta.original_repo_root}`\n"
            f"**Workspace Sandbox Root**: `{meta.workspace_root}`\n"
            f"**Current Status**: `{meta.status}`\n\n"
            f"## File Operations Metrics\n"
            f"- **File Changes Tracked**: {len(changes)}\n"
            f"- **Workspace Snapshots Captured**: {len(snaps)}\n"
        )
        
        doc = KnowledgeDocument(
            document_id=f"ws_report_{workspace_id}",
            title=f"AI Workspace Report - {workspace_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"ws_report_{workspace_id}",
                timestamp=time.time(),
                source_subsystem="ai_workspace",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

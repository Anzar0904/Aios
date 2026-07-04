import os
import shutil
import pytest
from unittest.mock import MagicMock

from aios.services.memory import MemoryService
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.ai_workspace import WorkspaceChange, WorkspaceSnapshot, WorkspaceSession
from aios.services.ai_workspace_impl import (
    LocalWorkspaceValidator,
    LocalWorkspaceCleaner,
    LocalAIWorkspaceService,
)


@pytest.fixture
def temp_repo_root(tmp_path):
    # Setup dummy repo root
    repo = tmp_path / "original_repo"
    repo.mkdir()
    (repo / "src").mkdir()
    (repo / "src" / "code.py").write_text("print('hello')")
    (repo / "docs").mkdir()
    (repo / "docs" / "readme.md").write_text("# Readme")
    
    # Git / Venv paths to ignore
    (repo / ".git").mkdir()
    (repo / ".git" / "config").write_text("git config")
    
    return str(repo)


def test_workspace_creation(temp_repo_root):
    mock_memory = MagicMock(spec=MemoryService)
    service = LocalAIWorkspaceService(memory_service=mock_memory)
    
    session = service.create_workspace(temp_repo_root)
    assert session.status == "open"
    assert session.workspace_id in service._workspaces
    
    meta = service._workspaces[session.workspace_id]
    assert os.path.exists(meta.workspace_root)
    assert os.path.exists(os.path.join(meta.workspace_root, "src", "code.py"))
    # Git should be ignored
    assert not os.path.exists(os.path.join(meta.workspace_root, ".git"))

    # Cleanup at the end
    service.destroy_workspace(session.workspace_id)


def test_workspace_validation(temp_repo_root):
    mock_memory = MagicMock(spec=MemoryService)
    service = LocalAIWorkspaceService(memory_service=mock_memory)
    
    session = service.create_workspace(temp_repo_root)
    valid, msg = service.validate_workspace(session.workspace_id)
    assert valid
    
    # Remove metadata file to simulate invalid workspace
    meta = service._workspaces[session.workspace_id]
    os.remove(os.path.join(meta.workspace_root, "workspace.json"))
    valid_invalid, msg_invalid = service.validate_workspace(session.workspace_id)
    assert not valid_invalid
    assert "metadata file missing" in msg_invalid

    service.destroy_workspace(session.workspace_id)


def test_session_lifecycle(temp_repo_root):
    mock_memory = MagicMock(spec=MemoryService)
    service = LocalAIWorkspaceService(memory_service=mock_memory)
    session = service.create_workspace(temp_repo_root)
    
    service.close_workspace(session.workspace_id)
    assert session.status == "closed"
    assert service._workspaces[session.workspace_id].status == "closed"
    
    new_sess = service.open_workspace(session.workspace_id)
    assert new_sess.status == "open"
    assert service._workspaces[session.workspace_id].status == "active"

    service.destroy_workspace(session.workspace_id)


def test_snapshot_creation_and_restoration(temp_repo_root):
    mock_memory = MagicMock(spec=MemoryService)
    service = LocalAIWorkspaceService(memory_service=mock_memory)
    session = service.create_workspace(temp_repo_root)
    
    # Register some changes
    change_1 = WorkspaceChange("c1", "src/code.py", "modify", 100.0)
    change_2 = WorkspaceChange("c2", "docs/new_doc.md", "create", 101.0)
    service.track_change(session.workspace_id, change_1)
    service.track_change(session.workspace_id, change_2)
    
    assert len(service.get_changes(session.workspace_id)) == 2
    
    # Create Snapshot
    snap = service.create_snapshot(session.workspace_id, "checkpoint 1")
    assert snap.snapshot_id is not None
    assert "src/code.py" in snap.modified_files
    assert "docs/new_doc.md" in snap.created_files
    
    # Restore Snapshot
    rec = service.restore_snapshot(session.workspace_id, snap.snapshot_id)
    assert rec.status == "success"
    assert len(rec.recovered_items) == 2

    # Restore invalid snapshot
    rec_invalid = service.restore_snapshot(session.workspace_id, "invalid_snap")
    assert rec_invalid.status == "failed"

    service.destroy_workspace(session.workspace_id)


def test_workspace_cleanup_and_archive(temp_repo_root):
    mock_memory = MagicMock(spec=MemoryService)
    service = LocalAIWorkspaceService(memory_service=mock_memory)
    session = service.create_workspace(temp_repo_root)
    
    meta = service._workspaces[session.workspace_id]
    
    # Create a temp file
    temp_file = os.path.join(meta.workspace_root, "build.tmp")
    with open(temp_file, "w") as f:
        f.write("temporary data")
        
    cleaned = service.cleanup_workspace(session.workspace_id)
    assert cleaned == 1
    assert not os.path.exists(temp_file)
    
    # Archive
    archive_path = service.archive_workspace(session.workspace_id)
    assert os.path.exists(archive_path)
    assert archive_path.endswith(".zip")
    
    # Restore from archive
    restored_session = service.restore_workspace(archive_path)
    assert restored_session.workspace_id == session.workspace_id
    assert service._workspaces[restored_session.workspace_id].status == "active"

    # Destroy
    service.destroy_workspace(session.workspace_id)
    assert not os.path.exists(meta.workspace_root)
    if os.path.exists(archive_path):
        os.remove(archive_path)


def test_memory_and_knowledge_hub_integration(temp_repo_root):
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    service = LocalAIWorkspaceService(memory_service=mock_memory, knowledge_hub=mock_kh)
    
    session = service.create_workspace(temp_repo_root)
    service.create_snapshot(session.workspace_id, "snapshot 1")
    
    service.store_workspace_summary(session.workspace_id)
    mock_memory.add_memory.assert_called_once()
    
    service.publish_workspace_report(session.workspace_id)
    mock_kh.sync_document.assert_called_once()

    service.destroy_workspace(session.workspace_id)


def test_backward_compatibility():
    class CustomWorkspaceValidator(LocalWorkspaceValidator):
        def validate_workspace(self, workspace_root):
            valid, reason = super().validate_workspace(workspace_root)
            if not valid:
                return False, reason
            return True, "Custom check passed."
            
    validator = CustomWorkspaceValidator()
    assert validator is not None

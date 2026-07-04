import os
import pytest
from unittest.mock import MagicMock

from aios.services.memory import MemoryService
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.patch_generation import PatchBundle, PatchMetadata, PatchStatistics
from aios.services.patch_generation_impl import (
    LocalDiffGenerator,
    LocalPatchGenerator,
    LocalPatchValidator,
    LocalConflictDetector,
    LocalPatchSerializer,
    LocalPatchGenerationService,
)


@pytest.fixture
def temp_workspace_and_repo(tmp_path):
    # original repo root
    repo = tmp_path / "original_repo"
    repo.mkdir()
    (repo / "file1.py").write_text("def run():\n    print('old')\n")
    (repo / "file2.py").write_text("def test():\n    pass\n")

    # workspace root
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "file1.py").write_text("def run():\n    print('new')\n    print('added line')\n")
    (workspace / "file2.py").write_text("def test():\n    pass\n") # Unchanged

    return str(workspace), str(repo)


def test_diff_generator():
    diff_gen = LocalDiffGenerator()
    orig = "line1\nline2\n"
    mod = "line1\nline3\n"
    
    diff = diff_gen.generate_diff(orig, mod, "test.txt")
    assert "--- a/test.txt" in diff
    assert "+++ b/test.txt" in diff
    assert "-line2" in diff
    assert "+line3" in diff


def test_patch_generator_bundle(temp_workspace_and_repo):
    ws_root, repo_root = temp_workspace_and_repo
    diff_gen = LocalDiffGenerator()
    generator = LocalPatchGenerator(diff_gen)
    
    bundle = generator.generate_patch_bundle(ws_root, repo_root, ["file1.py", "file2.py"])
    
    assert bundle.statistics.files_modified == 1 # Only file1 changed
    assert bundle.statistics.lines_added == 2
    assert bundle.statistics.lines_removed == 1
    assert "file1.py" in bundle.patches
    assert "file2.py" not in bundle.patches
    
    meta = bundle.metadata["file1.py"]
    assert meta.checksum is not None
    assert meta.size_bytes > 0


def test_patch_validator(temp_workspace_and_repo):
    ws_root, repo_root = temp_workspace_and_repo
    diff_gen = LocalDiffGenerator()
    generator = LocalPatchGenerator(diff_gen)
    validator = LocalPatchValidator()
    
    bundle = generator.generate_patch_bundle(ws_root, repo_root, ["file1.py"])
    valid, msg = validator.validate_patch_bundle(bundle, ws_root)
    assert valid
    
    # Intentionally corrupt checksum to test validation rejection
    bundle.metadata["file1.py"].checksum = "corrupted_checksum"
    valid_invalid, msg_invalid = validator.validate_patch_bundle(bundle, ws_root)
    assert not valid_invalid
    assert "Checksum verification failed" in msg_invalid


def test_conflict_detector():
    detector = LocalConflictDetector()
    bundle = MagicMock(spec=PatchBundle)
    bundle.patches = {"file1.py": "diff"}
    
    conflicts, inconsistencies = detector.detect_conflicts(bundle, ".")
    assert len(conflicts) == 0
    assert len(inconsistencies) == 0


def test_serializer(temp_workspace_and_repo):
    ws_root, repo_root = temp_workspace_and_repo
    diff_gen = LocalDiffGenerator()
    generator = LocalPatchGenerator(diff_gen)
    serializer = LocalPatchSerializer()
    
    bundle = generator.generate_patch_bundle(ws_root, repo_root, ["file1.py"])
    serialized = serializer.serialize_bundle(bundle)
    assert "bundle_id" in serialized
    
    deserialized = serializer.deserialize_bundle(serialized)
    assert deserialized.bundle_id == bundle.bundle_id
    assert deserialized.statistics.lines_added == bundle.statistics.lines_added
    assert deserialized.metadata["file1.py"].checksum == bundle.metadata["file1.py"].checksum


def test_patch_service_integration(temp_workspace_and_repo):
    ws_root, repo_root = temp_workspace_and_repo
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    
    service = LocalPatchGenerationService(
        memory_service=mock_memory,
        knowledge_hub=mock_kh
    )
    service.initialize()
    
    package = service.create_review_package("ws_1", repo_root, ws_root, ["file1.py"])
    
    assert package.workspace_id == "ws_1"
    assert package.validation_status == "passed"
    assert len(package.previews) == 1
    assert "file1.py" in package.previews[0].file_path
    
    # Store
    service.store_patch_summary(package)
    mock_memory.add_memory.assert_called_once()
    
    # Publish
    service.publish_patch_report(package)
    mock_kh.sync_document.assert_called_once()


def test_backward_compatibility():
    class CustomPatchValidator(LocalPatchValidator):
        def validate_patch_bundle(self, bundle, workspace_root):
            valid, reason = super().validate_patch_bundle(bundle, workspace_root)
            if not valid:
                return False, reason
            return True, "Custom validation checks passed."
            
    validator = CustomPatchValidator()
    assert validator is not None

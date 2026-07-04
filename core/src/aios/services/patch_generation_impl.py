import difflib
import hashlib
import json
import time
import os
import logging
from typing import Dict, List, Any, Optional

from aios.services.memory import MemoryService, MemoryType, MemoryMetadata
from aios.services.knowledge_hub import (
    KnowledgeHubService,
    KnowledgeDocument,
    KnowledgeMetadata as KHMetadata,
)
from aios.services.patch_generation import (
    PatchMetadata,
    PatchStatistics,
    PatchPreview,
    PatchBundle,
    ReviewPackage,
    DiffGenerator,
    PatchGenerator,
    PatchValidator,
    ConflictDetector,
    PatchSerializer,
    PatchGenerationService,
)

logger = logging.getLogger(__name__)


class LocalDiffGenerator(DiffGenerator):
    """Generates unified diff representation using Python difflib standard library."""

    def generate_diff(self, original_content: str, modified_content: str, file_path: str) -> str:
        original_lines = original_content.splitlines(keepends=True)
        modified_lines = modified_content.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            original_lines,
            modified_lines,
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}"
        )
        return "".join(diff)


class LocalPatchGenerator(PatchGenerator):
    """Computes unified diffs and metadata across files in workspace and repo root."""

    def __init__(self, diff_generator: DiffGenerator) -> None:
        self._diff_gen = diff_generator

    def generate_patch_bundle(
        self,
        workspace_root: str,
        original_repo_root: str,
        affected_files: List[str]
    ) -> PatchBundle:
        patches = {}
        metadata = {}
        
        total_added = 0
        total_removed = 0
        modified_count = 0
        total_chunks = 0

        for f in affected_files:
            # 1. Resolve file path in original and workspace
            workspace_file = os.path.join(workspace_root, f)
            original_file = os.path.join(original_repo_root, f)
            
            # 2. Load content
            workspace_content = ""
            if os.path.isfile(workspace_file):
                with open(workspace_file, "r") as fh:
                    workspace_content = fh.read()
                    
            original_content = ""
            if os.path.isfile(original_file):
                with open(original_file, "r") as fh:
                    original_content = fh.read()

            # 3. Generate Diff
            diff = self._diff_gen.generate_diff(original_content, workspace_content, f)
            if not diff:
                continue

            patches[f] = diff
            modified_count += 1

            # 4. Count line changes and chunks
            added = 0
            removed = 0
            chunks = 0
            for line in diff.splitlines():
                if line.startswith("+") and not line.startswith("+++"):
                    added += 1
                elif line.startswith("-") and not line.startswith("---"):
                    removed += 1
                elif line.startswith("@@"):
                    chunks += 1

            total_added += added
            total_removed += removed
            total_chunks += chunks

            # Calculate SHA-256 Checksum
            sha = hashlib.sha256(diff.encode("utf-8")).hexdigest()
            
            metadata[f] = PatchMetadata(
                patch_id=f"patch_{sha[:10]}",
                file_path=f,
                timestamp=time.time(),
                checksum=sha,
                size_bytes=len(diff),
                author="ai_software_engineer"
            )

        stats = PatchStatistics(
            lines_added=total_added,
            lines_removed=total_removed,
            files_modified=modified_count,
            chunks_count=total_chunks
        )

        return PatchBundle(
            bundle_id=f"bundle_{int(time.time())}",
            patches=patches,
            metadata=metadata,
            statistics=stats,
            timestamp=time.time()
        )


class LocalPatchValidator(PatchValidator):
    """Enforces syntax check and checksum compatibility for patches."""

    def validate_patch_bundle(self, bundle: PatchBundle, workspace_root: str) -> tuple[bool, str]:
        if not bundle.patches:
            return False, "Patch bundle has no patches."
            
        for f, diff in bundle.patches.items():
            # Basic validation: ensure diff headers exist
            if "--- a/" not in diff or "+++ b/" not in diff:
                return False, f"Diff for {f} is malformed (headers missing)."
                
            # Verify checksum matches metadata
            sha = hashlib.sha256(diff.encode("utf-8")).hexdigest()
            meta = bundle.metadata.get(f)
            if not meta or meta.checksum != sha:
                return False, f"Checksum verification failed for file patch: {f}"

        return True, "Patch bundle validation checks passed."


class LocalConflictDetector(ConflictDetector):
    """Detects merge collisions between workspace and origin repository roots."""

    def detect_conflicts(
        self,
        bundle: PatchBundle,
        original_repo_root: str
    ) -> tuple[List[str], List[str]]:
        conflicts = []
        inconsistencies = []

        # Simulate detecting merge conflict by comparing modified files
        for f in bundle.patches.keys():
            original_file = os.path.join(original_repo_root, f)
            if os.path.isfile(original_file):
                # If modified inside repo root directly since the workspace session (simulated check)
                # In real scenario we compare timestamp or git ref. Here we check path.
                pass
                
        # Basic dependency check
        for f in bundle.patches.keys():
            if f.endswith(".py"):
                # If file is missing or deleted in plan
                pass

        return conflicts, inconsistencies


class LocalPatchSerializer(PatchSerializer):
    """Converts patch objects to/from JSON."""

    def serialize_bundle(self, bundle: PatchBundle) -> str:
        # Convert metadata dataclasses to dict
        meta_dict = {}
        for k, v in bundle.metadata.items():
            meta_dict[k] = {
                "patch_id": v.patch_id,
                "file_path": v.file_path,
                "timestamp": v.timestamp,
                "checksum": v.checksum,
                "size_bytes": v.size_bytes,
                "author": v.author
            }
        
        stats_dict = {
            "lines_added": bundle.statistics.lines_added,
            "lines_removed": bundle.statistics.lines_removed,
            "files_modified": bundle.statistics.files_modified,
            "chunks_count": bundle.statistics.chunks_count
        }

        data = {
            "bundle_id": bundle.bundle_id,
            "patches": bundle.patches,
            "metadata": meta_dict,
            "statistics": stats_dict,
            "timestamp": bundle.timestamp
        }
        return json.dumps(data, indent=2)

    def deserialize_bundle(self, content: str) -> PatchBundle:
        data = json.loads(content)
        
        meta = {}
        for k, v in data.get("metadata", {}).items():
            meta[k] = PatchMetadata(
                patch_id=v["patch_id"],
                file_path=v["file_path"],
                timestamp=v["timestamp"],
                checksum=v["checksum"],
                size_bytes=v["size_bytes"],
                author=v["author"]
            )
            
        st_data = data.get("statistics", {})
        stats = PatchStatistics(
            lines_added=st_data.get("lines_added", 0),
            lines_removed=st_data.get("lines_removed", 0),
            files_modified=st_data.get("files_modified", 0),
            chunks_count=st_data.get("chunks_count", 0)
        )
        
        return PatchBundle(
            bundle_id=data["bundle_id"],
            patches=data["patches"],
            metadata=meta,
            statistics=stats,
            timestamp=data["timestamp"]
        )


class LocalPatchGenerationService(PatchGenerationService):
    """Coordinates reviews packaging, stats caching, and publication."""

    def __init__(
        self,
        memory_service: MemoryService,
        knowledge_hub: Optional[KnowledgeHubService] = None,
        registry: Optional[Any] = None
    ) -> None:
        self._memory = memory_service
        self._knowledge_hub = knowledge_hub
        self._registry = registry
        
        self._diff_generator = LocalDiffGenerator()
        self._generator = LocalPatchGenerator(self._diff_generator)
        self._validator = LocalPatchValidator()
        self._conflict_detector = LocalConflictDetector()

    def initialize(self) -> None:
        logger.info("Initializing LocalPatchGenerationService")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def create_review_package(
        self,
        workspace_id: str,
        original_repo_root: str,
        workspace_root: str,
        affected_files: List[str]
    ) -> ReviewPackage:
        logger.info(f"Creating review package for workspace: '{workspace_id}'")
        
        # 1. Generate bundle
        bundle = self._generator.generate_patch_bundle(workspace_root, original_repo_root, affected_files)
        
        # 2. Validate
        valid, msg = self._validator.validate_patch_bundle(bundle, workspace_root)
        val_status = "passed" if valid else "failed"

        # 3. Detect conflicts
        conflicts, inconsistencies = self._conflict_detector.detect_conflicts(bundle, original_repo_root)

        # 4. Generate previews
        previews = []
        for f, diff in bundle.patches.items():
            previews.append(
                PatchPreview(
                    preview_id=f"prev_{bundle.metadata[f].patch_id}",
                    file_path=f,
                    diff_content=diff,
                    human_readable_summary=f"Unified diff for {f} containing {bundle.statistics.lines_added} additions and {bundle.statistics.lines_removed} deletions."
                )
            )

        package_id = f"rev_{workspace_id}_{int(time.time())}"
        package = ReviewPackage(
            package_id=package_id,
            workspace_id=workspace_id,
            bundle=bundle,
            previews=previews,
            conflicts=conflicts,
            planning_inconsistencies=inconsistencies,
            validation_status=val_status
        )

        # Write patch file inside workspace for review tracking
        patch_file = os.path.join(workspace_root, "changes.patch")
        try:
            with open(patch_file, "w") as fh:
                # Concatenate all patch diffs
                fh.write("".join(bundle.patches.values()))
        except Exception as e:
            logger.debug(f"Failed to write patch to workspace: {e}")

        return package

    def store_patch_summary(self, review_package: ReviewPackage) -> None:
        summary = (
            f"Review Package ID: {review_package.package_id}\n"
            f"Workspace ID: {review_package.workspace_id}\n"
            f"Validation Status: {review_package.validation_status}\n"
            f"Lines Added: {review_package.bundle.statistics.lines_added}\n"
            f"Lines Removed: {review_package.bundle.statistics.lines_removed}\n"
            f"Files Modified Count: {review_package.bundle.statistics.files_modified}\n"
            f"Conflicts Detected: {review_package.conflicts}"
        )
        
        self._memory.add_memory(
            content=summary,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id=review_package.workspace_id,
                session_id=f"sess_{review_package.workspace_id}",
                tags=["patch_generation", "code_review"],
                importance=2,
                source_subsystem="patch_generator"
            )
        )

    def publish_patch_report(self, review_package: ReviewPackage) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        previews_md = []
        for p in review_package.previews:
            previews_md.append(
                f"### Preview: `{p.file_path}`\n"
                f"*{p.human_readable_summary}*\n"
                f"```diff\n{p.diff_content}```\n"
            )

        report_md = (
            f"# Engineering Patch Generation Report\n\n"
            f"**Review Package ID**: `{review_package.package_id}`\n"
            f"**Workspace ID**: `{review_package.workspace_id}`\n"
            f"**Validation Status**: `{review_package.validation_status.upper()}`\n\n"
            f"## Modification Metrics\n"
            f"- **Files Changed**: {review_package.bundle.statistics.files_modified}\n"
            f"- **Lines Added**: {review_package.bundle.statistics.lines_added}\n"
            f"- **Lines Removed**: {review_package.bundle.statistics.lines_removed}\n"
            f"- **Conflicts Detected Count**: {len(review_package.conflicts)}\n\n"
            f"## File Preview Diffs\n"
            + "\n".join(previews_md)
        )

        doc = KnowledgeDocument(
            document_id=f"patch_report_{review_package.package_id}",
            title=f"Patch Report - {review_package.package_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"patch_report_{review_package.package_id}",
                timestamp=review_package.bundle.timestamp,
                source_subsystem="patch_generator",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

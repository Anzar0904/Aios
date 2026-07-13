import abc
from dataclasses import dataclass
from typing import Dict, List

from aios.services.base import ServiceLifecycle


@dataclass
class PatchMetadata:
    """Tracks patch metadata, identifiers, and validations."""

    patch_id: str
    file_path: str
    timestamp: float
    checksum: str
    size_bytes: int
    author: str


@dataclass
class PatchStatistics:
    """Consolidates modification metrics across code patches."""

    lines_added: int
    lines_removed: int
    files_modified: int
    chunks_count: int


@dataclass
class PatchPreview:
    """Human-readable preview of planned code alterations."""

    preview_id: str
    file_path: str
    diff_content: str
    human_readable_summary: str


@dataclass
class PatchBundle:
    """Aggregates multiple file diffs and metadata."""

    bundle_id: str
    patches: Dict[str, str]  # file_path -> unified_diff_content
    metadata: Dict[str, PatchMetadata]
    statistics: PatchStatistics
    timestamp: float


@dataclass
class ReviewPackage:
    """Consolidated package for developer code review before merge approval."""

    package_id: str
    workspace_id: str
    bundle: PatchBundle
    previews: List[PatchPreview]
    conflicts: List[str]
    planning_inconsistencies: List[str]
    validation_status: str  # "passed", "failed"


class DiffGenerator(abc.ABC):
    """Generates standard unified diff format strings."""

    @abc.abstractmethod
    def generate_diff(self, original_content: str, modified_content: str, file_path: str) -> str:
        """Returns standard unified diff comparison output."""
        pass


class PatchGenerator(abc.ABC):
    """Orchestrates patch bundle creation across isolated workspaces."""

    @abc.abstractmethod
    def generate_patch_bundle(
        self, workspace_root: str, original_repo_root: str, affected_files: List[str]
    ) -> PatchBundle:
        """Generates a PatchBundle containing all changed file diffs."""
        pass


class PatchValidator(abc.ABC):
    """Verifies lines offsets, checksums, and syntax integrity."""

    @abc.abstractmethod
    def validate_patch_bundle(self, bundle: PatchBundle, workspace_root: str) -> tuple[bool, str]:
        """Validates patch formatting, line mappings, and syntax validity."""
        pass


class ConflictDetector(abc.ABC):
    """Checks for concurrent modifications and dependency mismatches."""

    @abc.abstractmethod
    def detect_conflicts(
        self, bundle: PatchBundle, original_repo_root: str
    ) -> tuple[List[str], List[str]]:
        """Checks for merge conflicts and planning inconsistencies."""
        pass


class PatchSerializer(abc.ABC):
    """Serializes patch bundles to/from standardized file systems representations."""

    @abc.abstractmethod
    def serialize_bundle(self, bundle: PatchBundle) -> str:
        """Serializes bundle to a structured string."""
        pass

    @abc.abstractmethod
    def deserialize_bundle(self, content: str) -> PatchBundle:
        """Deserializes bundle from a structured string."""
        pass


class PatchGenerationService(ServiceLifecycle, abc.ABC):
    """Primary service managing unified diff generation, validations, and review packaging."""

    @abc.abstractmethod
    def create_review_package(
        self,
        workspace_id: str,
        original_repo_root: str,
        workspace_root: str,
        affected_files: List[str],
    ) -> ReviewPackage:
        """Assembles a full review package containing preview, stats, and conflict checks."""
        pass

    @abc.abstractmethod
    def store_patch_summary(self, review_package: ReviewPackage) -> None:
        """Persists the patch execution summary in Memory Intelligence."""
        pass

    @abc.abstractmethod
    def publish_patch_report(self, review_package: ReviewPackage) -> None:
        """Publishes the patch review report to the Knowledge Hub."""
        pass

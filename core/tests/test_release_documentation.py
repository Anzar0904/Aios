import os
import time
from unittest.mock import MagicMock

import pytest
from aios.services.ai_workspace import AIWorkspaceService, WorkspaceMetadata
from aios.services.engineering_profile import (
    DocumentationProfile,
    EngineeringProfile,
    EngineeringProfileService,
)
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.memory import Memory, MemoryService
from aios.services.model import LLMResponse, ModelService
from aios.services.release_documentation import (
    ReleaseArtifact,
    ReleaseDocumentationReport,
    ReleaseSummary,
)
from aios.services.release_documentation_impl import (
    LocalChangelogGenerator,
    LocalMigrationGuideGenerator,
    LocalReleaseDocumentationService,
    LocalReleaseNotesGenerator,
    LocalReleaseValidator,
    LocalUpgradeGuideGenerator,
)


@pytest.fixture
def mock_memory_service():
    service = MagicMock(spec=MemoryService)
    # Return empty list on search to avoid duplicate warning initially
    service.search_memory.return_value = []
    return service


@pytest.fixture
def mock_profile_service():
    service = MagicMock(spec=EngineeringProfileService)

    doc_prof = DocumentationProfile(
        format="markdown",
        generate_api_docs=True,
        release_formatting_rules={
            "include_header_metadata": True,
            "use_code_blocks_for_versions": True,
        },
        markdown_preferences={"list_style": "-", "bold_headers": True},
        section_ordering=[
            "Feature Summary",
            "Bug Fix Summary",
            "Breaking Changes",
            "Validation Summary",
        ],
        naming_conventions={
            "release_notes": "RELEASE_NOTES_{version}.md",
            "changelog": "CHANGELOG.md",
            "migration_guide": "MIGRATION_GUIDE_{from}_TO_{to}.md",
            "upgrade_guide": "UPGRADE_GUIDE_{version}.md",
        },
        versioning_preferences={
            "supported_channels": ["alpha", "beta", "rc", "stable"],
            "strict_semver": True,
        },
    )
    eng_prof = MagicMock(spec=EngineeringProfile)
    eng_prof.documentation = doc_prof

    service.get_profile.return_value = eng_prof
    return service


@pytest.fixture
def mock_workspace_service():
    service = MagicMock(spec=AIWorkspaceService)
    return service


@pytest.fixture
def mock_model_service():
    service = MagicMock(spec=ModelService)

    response = MagicMock(spec=LLMResponse)
    response.content = "LLM Refined Markdown Content"
    service.execute_request.return_value = response
    return service


def test_release_notes_generation():
    generator = LocalReleaseNotesGenerator()
    summary = ReleaseSummary(
        version="1.0.0",
        channel="stable",
        release_date=0.0,
        features_count=2,
        fixes_count=1,
        breaking_changes_count=0,
    )
    details = {
        "features": ["Integrated Github interface", "Added career services"],
        "fixes": ["Resolved rate limits crash"],
        "breaking_changes": [],
        "validation_summary": {"status": "PASS", "tests_run_count": 335, "coverage_pct": 85.5},
        "markdown_preferences": {"list_style": "-", "bold_headers": True},
    }

    notes = generator.generate_release_notes(summary, details)
    assert "# Release Notes - Version 1.0.0 (STABLE)" in notes
    assert "- Features added: 2" in notes
    assert "- Bug fixes: 1" in notes
    assert "## **Features**" in notes
    assert "- Integrated Github interface" in notes
    assert "## **Bug Fixes**" in notes
    assert "- Resolved rate limits crash" in notes
    assert "## **Validation & Testing Summary**" in notes
    assert "- **Statement Coverage**: 85.5%" in notes


def test_changelog_generation():
    generator = LocalChangelogGenerator()
    summary = ReleaseSummary(
        version="1.1.0",
        channel="rc",
        release_date=0.0,
        features_count=1,
        fixes_count=1,
        breaking_changes_count=0,
    )
    commits = [
        {"hash": "abcdef123456", "message": "feat: Support Notion DB synchronizations"},
        {"hash": "123456abcdef", "message": "fix: Handle symlink boundary checking error"},
    ]

    changelog = generator.generate_changelog(summary, commits)
    assert "# Changelog" in changelog
    assert "## [1.1.0]" in changelog
    assert "### Added" in changelog
    assert "- feat: Support Notion DB synchronizations (commit: `abcdef1`)" in changelog
    assert "### Fixed" in changelog
    assert "- fix: Handle symlink boundary checking error (commit: `123456a`)" in changelog


def test_migration_guide_generation():
    generator = LocalMigrationGuideGenerator()
    guide = generator.generate_migration_guide(
        version_from="0.9.0",
        version_to="1.0.0",
        instructions=[
            "Upgrade Python runtime environment to 3.10+",
            "Run notion-db migration script",
        ],
    )
    assert "# Migration Guide: v0.9.0 to v1.0.0" in guide
    assert "1. [ ] **Upgrade Python runtime environment to 3.10+**" in guide
    assert "2. [ ] **Run notion-db migration script**" in guide
    assert "> [!WARNING]" in guide


def test_upgrade_guide_generation():
    generator = LocalUpgradeGuideGenerator()
    guide = generator.generate_upgrade_guide(
        target_version="1.2.0", checklist=["Git pull origin main", "Poetry install", "Agy restart"]
    )
    assert "# Upgrade Guide - Target Version 1.2.0" in guide
    assert "- [ ] Git pull origin main" in guide
    assert "- [ ] Poetry install" in guide
    assert "- [ ] Agy restart" in guide


def test_validation(mock_memory_service):
    validator = LocalReleaseValidator(mock_memory_service)

    # 1. Valid artifact
    artifact = ReleaseArtifact(
        "release_notes_1.0.0",
        "ws_1",
        "1.0.0",
        "stable",
        "# Features\n# Bug Fixes\n# Breaking Changes",
        0.0,
    )
    errors = validator.validate_release_document(artifact)
    assert len(errors) == 0

    # 2. Invalid semantic version
    artifact_bad_version = ReleaseArtifact(
        "notes_v1", "ws_1", "v1.0", "stable", "# Features\n# Bug Fixes\n# Breaking Changes", 0.0
    )
    errors = validator.validate_release_document(artifact_bad_version)
    assert any("Invalid semantic version structure" in e for e in errors)

    # 3. Duplicate release entry detection
    mock_memory = MagicMock(spec=Memory)
    mock_memory.content = "Release Summary: Version: 1.0.0"
    mock_memory_service.search_memory.return_value = [mock_memory]

    artifact_dup = ReleaseArtifact(
        "release_notes_1.0.0",
        "ws_1",
        "1.0.0",
        "stable",
        "# Features\n# Bug Fixes\n# Breaking Changes",
        0.0,
    )
    errors_dup = validator.validate_release_document(artifact_dup)
    assert any("Duplicate release entry detected" in e for e in errors_dup)


def test_workspace_generation(
    tmp_path, mock_memory_service, mock_profile_service, mock_workspace_service
):
    # Setup mock workspace directories
    ws_id = "ws_test_123"
    ws_root = str(tmp_path / ws_id)
    os.makedirs(ws_root, exist_ok=True)

    meta = WorkspaceMetadata(ws_id, 0.0, "/src", ws_root, "active")
    mock_workspace_service._workspaces = {ws_id: meta}

    registry = MagicMock()
    registry.get.side_effect = lambda t: mock_workspace_service if t == AIWorkspaceService else None

    service = LocalReleaseDocumentationService(
        memory_service=mock_memory_service, profile_service=mock_profile_service, registry=registry
    )
    service.initialize()

    summary = ReleaseSummary("1.0.0", "stable", 0.0, 1, 1, 0)
    details = {"features": ["F1"], "fixes": ["FX1"], "breaking_changes": []}

    # Create notes -> should write under ws_root/docs/releases/RELEASE_NOTES_1.0.0.md
    artifact = service.create_release_notes(ws_id, summary, details)
    expected_path = os.path.join(ws_root, "docs", "releases", "RELEASE_NOTES_1.0.0.md")

    assert os.path.exists(expected_path)
    with open(expected_path, "r") as f:
        content = f.read()
    assert "# Release Notes - Version 1.0.0" in content
    assert artifact.version == "1.0.0"


def test_profile_integration(mock_memory_service, mock_profile_service):
    service = LocalReleaseDocumentationService(
        memory_service=mock_memory_service, profile_service=mock_profile_service
    )
    prefs = service._get_profile_preferences()
    assert prefs["section_ordering"] == [
        "Feature Summary",
        "Bug Fix Summary",
        "Breaking Changes",
        "Validation Summary",
    ]
    assert prefs["naming_conventions"]["release_notes"] == "RELEASE_NOTES_{version}.md"


def test_memory_integration(mock_memory_service, mock_profile_service):
    service = LocalReleaseDocumentationService(
        memory_service=mock_memory_service, profile_service=mock_profile_service
    )

    artifact = ReleaseArtifact(
        artifact_id="art_1",
        workspace_id="ws_1",
        version="1.0.0",
        channel="stable",
        content="some code or doc details",
        timestamp=100.0,
    )

    service.store_release_summary(artifact)

    # Verify that add_memory is called with metadata summaries, never with content = artifact.content
    mock_memory_service.add_memory.assert_called_once()
    args, kwargs = mock_memory_service.add_memory.call_args
    content = kwargs.get("content", args[0] if args else "")
    tags = kwargs.get("tags", [])

    assert (
        "some code" not in content
    )  # Ensuring repository source code / raw doc is not in the text
    assert "Version: 1.0.0" in content
    assert "release_summary" in tags


def test_knowledge_hub_integration(mock_memory_service, mock_profile_service):
    mock_kh = MagicMock(spec=KnowledgeHubService)

    service = LocalReleaseDocumentationService(
        memory_service=mock_memory_service,
        profile_service=mock_profile_service,
        knowledge_hub=mock_kh,
    )

    report = ReleaseDocumentationReport("rep_1", "ws_1", True, [], time.time())
    service.publish_release_report(report)

    mock_kh.sync_document.assert_called_once()
    args, kwargs = mock_kh.sync_document.call_args
    doc = args[0]
    assert doc.title == "Release Validation - rep_1"
    assert "PASSED" in doc.content


def test_backward_compatibility(mock_memory_service, mock_profile_service):
    class CustomUpgradeGuideGenerator(LocalUpgradeGuideGenerator):
        def generate_upgrade_guide(self, target_version, checklist):
            # Custom additions
            guide = super().generate_upgrade_guide(target_version, checklist)
            return guide + "\n- Custom compatibility check passed."

    generator = CustomUpgradeGuideGenerator()
    guide = generator.generate_upgrade_guide("1.0.0", [])
    assert "- Custom compatibility check passed." in guide

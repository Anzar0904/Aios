import pytest
from unittest.mock import MagicMock

from aios.services.memory import MemoryService
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.engineering_profile import EngineeringProfile
from aios.services.engineering_profile_impl import (
    LocalProfileSerializer,
    LocalProfileLoader,
    LocalProfileManager,
    LocalEngineeringProfileService,
)


@pytest.fixture
def sample_profile_dict():
    return {
        "profile_id": "test_profile",
        "project": {
            "project_name": "Test project",
            "version": "1.2.3",
            "description": "A test project."
        },
        "coding": {
            "language": "python",
            "coding_standards": ["PEP8"],
            "naming_conventions": {"class": "PascalCase"}
        },
        "testing": {
            "framework": "pytest",
            "min_statement_coverage": 90.0,
            "min_branch_coverage": 85.0
        },
        "execution": {
            "max_timeout_seconds": 120,
            "sandbox_enabled": True
        },
        "documentation": {
            "format": "markdown",
            "generate_api_docs": False
        },
        "github": {
            "org_name": "test_org",
            "repo_name": "test_repo",
            "default_branch": "main"
        },
        "release": {
            "auto_release": True,
            "versioning_scheme": "semver"
        },
        "automation": {
            "cron_expression": "0 0 * * *",
            "max_retries": 5
        },
        "workspace": {
            "workspace_root": "/tmp/test",
            "exclude_patterns": [".git"]
        },
        "timestamp": 123456789.0
    }


def test_profile_serialization(sample_profile_dict):
    serializer = LocalProfileSerializer()
    profile = serializer.deserialize(sample_profile_dict)
    
    assert isinstance(profile, EngineeringProfile)
    assert profile.profile_id == "test_profile"
    assert profile.project.project_name == "Test project"
    assert profile.coding.language == "python"
    assert profile.testing.min_statement_coverage == 90.0
    
    serialized = serializer.serialize(profile)
    assert serialized["profile_id"] == "test_profile"
    assert serialized["project"]["project_name"] == "Test project"
    assert serialized["coding"]["language"] == "python"
    assert serialized["testing"]["min_statement_coverage"] == 90.0


def test_profile_validation(sample_profile_dict):
    serializer = LocalProfileSerializer()
    manager = LocalProfileManager()
    
    profile = serializer.deserialize(sample_profile_dict)
    errors = manager.validate(profile)
    assert len(errors) == 0

    # 1. Invalid ID
    profile.profile_id = ""
    # 2. Invalid Coverage range
    profile.testing.min_statement_coverage = 150.0
    
    errors = manager.validate(profile)
    assert len(errors) == 2
    assert "Profile id" in errors[0]
    assert "Min statement coverage" in errors[1]


def test_profile_merging_precedence(sample_profile_dict):
    manager = LocalProfileManager()
    
    override = {
        "project": {
            "version": "1.2.4"
        },
        "testing": {
            "min_statement_coverage": 95.0
        }
    }
    
    merged = manager.merge(sample_profile_dict, override)
    
    # Touch points updated
    assert merged["project"]["version"] == "1.2.4"
    assert merged["testing"]["min_statement_coverage"] == 95.0
    # Untouched base points preserved
    assert merged["project"]["project_name"] == "Test project"
    assert merged["testing"]["min_branch_coverage"] == 85.0


def test_profile_service_integrations(sample_profile_dict):
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    
    service = LocalEngineeringProfileService(
        memory_service=mock_memory,
        knowledge_hub=mock_kh
    )
    service.initialize()
    
    serializer = LocalProfileSerializer()
    profile = serializer.deserialize(sample_profile_dict)
    
    # Save
    service.save_profile(profile)
    assert service.get_profile("test_profile") == profile
    
    # Store
    service.store_profile_summary(profile)
    mock_memory.add_memory.assert_called_once()
    
    # Publish
    service.publish_profile_summary(profile)
    mock_kh.sync_document.assert_called_once()


def test_backward_compatibility():
    class CustomSerializer(LocalProfileSerializer):
        def serialize(self, profile):
            res = super().serialize(profile)
            res["custom_flag"] = True
            return res
            
    serializer = CustomSerializer()
    profile = serializer.deserialize({"profile_id": "compat"})
    serialized = serializer.serialize(profile)
    assert serialized["custom_flag"] is True

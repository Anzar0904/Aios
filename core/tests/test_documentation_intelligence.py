from unittest.mock import MagicMock

import pytest
from aios.services.documentation_intelligence import (
    DocumentArtifact,
    DocumentationProfileAdapter,
    DocumentationRegistry,
    DocumentationResult,
    DocumentationWorkspace,
    DocumentCategory,
    DocumentMetadata,
    DocumentSource,
    DocumentTemplate,
)
from aios.services.documentation_intelligence_impl import (
    LocalDocumentationPlanner,
    LocalDocumentationService,
)
from aios.services.engineering_profile import (
    DocumentationProfile,
    EngineeringProfile,
    EngineeringProfileService,
)
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.memory import MemoryService


@pytest.fixture
def mock_profile_service():
    service = MagicMock(spec=EngineeringProfileService)
    
    doc_prof = DocumentationProfile(
        format="markdown",
        generate_api_docs=True
    )
    eng_prof = MagicMock(spec=EngineeringProfile)
    eng_prof.documentation = doc_prof
    
    service.get_profile.return_value = eng_prof
    return service


def test_registry_creation():
    registry = DocumentationRegistry()
    template = DocumentTemplate("t1", "README layout", ["Title", "Overview"])
    
    registry.register_template(template)
    assert registry.get_template("t1") == template


def test_metadata_validation():
    metadata = DocumentMetadata(
        doc_id="d1",
        category=DocumentCategory.README,
        source=DocumentSource.SOFTWARE_ENG,
        title="Project README",
        version="1.0.0",
        author="Antigravity",
        timestamp=0.0
    )
    
    assert metadata.category == DocumentCategory.README
    assert metadata.source == DocumentSource.SOFTWARE_ENG
    assert metadata.title == "Project README"


def test_profile_integration():
    doc_prof = DocumentationProfile(format="rst", generate_api_docs=False)
    adapter = DocumentationProfileAdapter(doc_prof)
    
    assert adapter.get_format() == "rst"
    assert adapter.should_generate_api() is False
    assert "language" in adapter.get_style_rules()


def test_document_registration():
    registry = DocumentationRegistry()
    metadata = DocumentMetadata(
        doc_id="d1",
        category=DocumentCategory.CHANGELOG,
        source=DocumentSource.PATCH_GEN,
        title="Changelog",
        version="0.2.0",
        author="Antigravity",
        timestamp=0.0
    )
    artifact = DocumentArtifact("art_1", metadata, "Content summary.")
    
    registry.register_artifact(artifact)
    assert registry.get_artifact("art_1") == artifact


def test_service_evaluation_flow(mock_profile_service):
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    
    service = LocalDocumentationService(
        memory_service=mock_memory,
        engineering_profile_service=mock_profile_service,
        knowledge_hub=mock_kh
    )
    service.initialize()
    
    workspace = DocumentationWorkspace("ws_1", "/tmp/path")
    session = service.create_session(workspace)
    
    assert session.status == "initialized"
    
    # Plan
    templates = service.plan_session(session)
    assert len(templates) > 0
    assert session.status == "planning"
    mock_profile_service.get_profile.assert_called_with("default")
    
    # Register artifact
    metadata = DocumentMetadata(
        doc_id="d1",
        category=DocumentCategory.API_DOC,
        source=DocumentSource.WORKSPACE_INTEL,
        title="API Doc",
        version="1.0.0",
        author="Antigravity",
        timestamp=0.0
    )
    art = DocumentArtifact("art_1", metadata, "API classes documentation.")
    service.register_artifact(art)
    assert service.get_artifact("art_1") == art
    
    # Store
    result = DocumentationResult("res_1", session.session_id, [art], True)
    service.store_documentation_summary(result)
    mock_memory.add_memory.assert_called_once()
    
    # Publish
    service.publish_documentation_summary(result)
    mock_kh.sync_document.assert_called_once()


def test_backward_compatibility():
    class CustomPlanner(LocalDocumentationPlanner):
        def plan_documentation(self, session, profile_adapter):
            templates = super().plan_documentation(session, profile_adapter)
            templates.append(DocumentTemplate("tmpl_custom", "Custom Layout", ["Custom"]))
            return templates
            
    planner = CustomPlanner()
    templates = planner.plan_documentation(MagicMock(), MagicMock())
    template_ids = [t.template_id for t in templates]
    assert "tmpl_custom" in template_ids

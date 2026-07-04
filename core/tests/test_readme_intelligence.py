import pytest
from unittest.mock import MagicMock

from aios.services.memory import MemoryService
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.model import ModelService, LLMResponse
from aios.services.readme_intelligence import READMESection, READMETemplate, READMEArtifact, READMESummary
from aios.services.readme_intelligence_impl import (
    LocalREADMEAnalyzer,
    LocalREADMEPlanner,
    LocalREADMEValidator,
    LocalREADMEGenerator,
    LocalREADMEUpdater,
    LocalREADMEIntelligenceService,
)


def test_readme_analyzer():
    analyzer = LocalREADMEAnalyzer()
    existing = "# My Project\nSome description."
    metadata = {"project_name": "My Project", "workspace_id": "ws_1"}
    
    report = analyzer.analyze_readme(existing, metadata)
    assert len(report.missing_sections) > 0
    assert "Installation" in report.missing_sections


def test_readme_planner():
    planner = LocalREADMEPlanner()
    template = READMETemplate(
        template_id="t1",
        sections_order=["Overview", "Installation", "License"],
        style_rules={}
    )
    report = MagicMock()
    
    sections = planner.plan_sections(report, template)
    assert len(sections) == 3
    assert sections[0].heading == "Overview"
    assert sections[1].heading == "Installation"


def test_readme_validator():
    validator = LocalREADMEValidator()
    
    # 1. Valid markdown
    errors = validator.validate_readme("# Hello\nSome text.")
    assert len(errors) == 0
    
    # 2. Duplicate heading
    errors_dup = validator.validate_readme("# Intro\ntext\n# Intro\ntext")
    assert len(errors_dup) == 1
    assert "Duplicate heading" in errors_dup[0]

    # 3. Broken link parenthesis
    errors_link = validator.validate_readme("[Link](https://google.com")
    assert len(errors_link) == 1


def test_readme_generation():
    generator = LocalREADMEGenerator()
    sections = [
        READMESection("Overview", "Intro text", 0),
        READMESection("Installation", "pip install", 1)
    ]
    
    artifact = generator.generate_readme("ws_1", sections)
    assert "# Overview\nIntro text" in artifact.content
    assert "# Installation\npip install" in artifact.content


def test_readme_updating():
    updater = LocalREADMEUpdater()
    existing_sections = [
        READMESection("Overview", "Old intro", 0),
        READMESection("Installation", "pip install", 1)
    ]
    existing = READMEArtifact("art_1", "ws_1", "content", existing_sections, 0.0)
    
    changes = [
        READMESection("Overview", "New intro", 0),
        READMESection("License", "MIT", 2)
    ]
    
    updated = updater.update_readme(existing, changes)
    assert len(updated.sections) == 3
    assert updated.sections[0].content == "New intro"
    assert updated.sections[2].heading == "License"


def test_service_evaluation_flow():
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    mock_model = MagicMock(spec=ModelService)
    
    # Mock LLM Response
    mock_response = MagicMock(spec=LLMResponse)
    mock_response.content = "# Overview\nLLM Refined intro."
    mock_model.execute_request.return_value = mock_response

    service = LocalREADMEIntelligenceService(
        memory_service=mock_memory,
        knowledge_hub=mock_kh,
        model_service=mock_model
    )
    service.initialize()
    
    template = READMETemplate(
        template_id="t1",
        sections_order=["Overview"],
        style_rules={}
    )
    
    artifact = service.analyze_and_generate("ws_1", "", {"project_name": "My Project"}, template)
    assert artifact.content == "# Overview\nLLM Refined intro."
    
    # Store
    summary = READMESummary("s1", "valid", 1, 0.0)
    service.store_readme_summary(summary)
    mock_memory.add_memory.assert_called_once()
    
    # Publish
    report = MagicMock()
    service.publish_readme_report(report)
    mock_kh.sync_document.assert_called_once()


def test_backward_compatibility():
    class CustomAnalyzer(LocalREADMEAnalyzer):
        def analyze_readme(self, existing_content, workspace_metadata):
            report = super().analyze_readme(existing_content, workspace_metadata)
            report.analysis_summary = "Custom summary."
            return report
            
    analyzer = CustomAnalyzer()
    report = analyzer.analyze_readme("", {})
    assert report.analysis_summary == "Custom summary."

import time
from unittest.mock import MagicMock

import pytest
from aios.services.engineering_intelligence import (
    AffectedComponent,
    AffectedFile,
)
from aios.services.engineering_intelligence_impl import (
    LocalChangeImpactAnalyzer,
    LocalComplexityEstimator,
    LocalEngineeringIntelligenceService,
    LocalImplementationPlanner,
    LocalRiskAnalyzer,
)
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.memory import MemoryService
from aios.services.workspace_intelligence import (
    CodeIntelligenceService,
    CodeStructureSummary,
    SymbolReference,
    WorkspaceIntelligenceService,
)


@pytest.fixture
def dummy_code_summary():
    # Setup dummy symbols
    symbols = {
        "dummy_module::MyClass": SymbolReference(
            symbol_id="dummy_module::MyClass",
            name="MyClass",
            symbol_type="class",
            file_path="dummy_module.py",
            start_line=1,
            end_line=20,
            decorators=[],
            is_public=True
        ),
        "dummy_module::MyClass.execute": SymbolReference(
            symbol_id="dummy_module::MyClass.execute",
            name="MyClass.execute",
            symbol_type="method",
            file_path="dummy_module.py",
            start_line=5,
            end_line=10,
            decorators=[],
            is_public=True
        )
    }
    
    # Setup dummy dependency graph
    dependency_graph = {
        "dummy_module.py": [],
        "another_module.py": ["dummy_module.py"]
    }
    
    # Setup call graph
    call_graph = {
        "execute": []
    }
    
    return CodeStructureSummary(
        summary_id="summary_123",
        timestamp=time.time(),
        symbols=symbols,
        call_graph=call_graph,
        dependency_graph=dependency_graph,
        inheritance_map={},
        public_apis=["MyClass", "execute"]
    )


def test_change_impact_analyzer(dummy_code_summary):
    analyzer = LocalChangeImpactAnalyzer()
    
    # Match by file keyword
    files, components = analyzer.analyze_impact(".", "Modify dummy module", dummy_code_summary)
    assert len(files) >= 1
    assert any("dummy_module.py" in f.file_path for f in files)
    
    # Check that matched symbols are found
    assert len(components) >= 1
    assert any("MyClass" in c.name for c in components)


def test_complexity_estimator(dummy_code_summary):
    estimator = LocalComplexityEstimator()
    
    # 1 file
    files_low = [AffectedFile(file_path="a.py", change_type="modify", reason="")]
    complexity, hours = estimator.estimate_complexity(files_low, [], dummy_code_summary)
    assert complexity == "Low"
    assert hours == 3.0
    
    # 3 files
    files_med = [
        AffectedFile(file_path="a.py", change_type="modify", reason=""),
        AffectedFile(file_path="b.py", change_type="modify", reason=""),
        AffectedFile(file_path="c.py", change_type="modify", reason="")
    ]
    complexity_med, hours_med = estimator.estimate_complexity(files_med, [], dummy_code_summary)
    assert complexity_med == "Medium"
    assert hours_med == 8.5


def test_risk_analyzer(dummy_code_summary):
    analyzer = LocalRiskAnalyzer()
    
    # Check method impact risks
    components = [
        AffectedComponent(name="MyClass.execute", component_type="method", impact_level="High", description="")
    ]
    risks = analyzer.analyze_risks("Refactor execute", [], components, dummy_code_summary)
    assert any("public APIs" in r for r in risks)
    
    # Check coupling risks
    files = [
        AffectedFile(file_path="a.py", change_type="modify", reason=""),
        AffectedFile(file_path="b.py", change_type="modify", reason=""),
        AffectedFile(file_path="c.py", change_type="modify", reason=""),
        AffectedFile(file_path="d.py", change_type="modify", reason="")
    ]
    risks_coupling = analyzer.analyze_risks("Refactor all", files, [], dummy_code_summary)
    assert any("coupling" in r.lower() for r in risks_coupling)


def test_implementation_planner(dummy_code_summary):
    planner = LocalImplementationPlanner()
    files = [AffectedFile(file_path="dummy_module.py", change_type="modify", reason="")]
    risks = ["Risk 1"]
    
    plan = planner.generate_plan("Objective", files, [], "Medium", risks, dummy_code_summary)
    assert plan.complexity == "Medium"
    assert "step_1_design" in [s["step_id"] for s in plan.ordered_steps]
    assert plan.dependencies["step_2_implement"] == ["step_1_design"]
    assert "dummy_module.py" in plan.recommended_execution_order


def test_engineering_intelligence_service_integration(dummy_code_summary):
    mock_code_intel = MagicMock(spec=CodeIntelligenceService)
    mock_code_intel.analyze_codebase.return_value = dummy_code_summary
    
    mock_workspace_intel = MagicMock(spec=WorkspaceIntelligenceService)
    mock_memory_service = MagicMock(spec=MemoryService)
    mock_knowledge_hub = MagicMock(spec=KnowledgeHubService)
    
    service = LocalEngineeringIntelligenceService(
        code_intel=mock_code_intel,
        workspace_intel=mock_workspace_intel,
        memory_service=mock_memory_service,
        knowledge_hub=mock_knowledge_hub
    )
    service.initialize()
    
    # Generate report
    report = service.generate_report(".", "Implement dummy database")
    assert report.objective == "Implement dummy database"
    assert len(report.affected_files) >= 1
    
    # Store report
    service.store_report(report)
    mock_memory_service.add_memory.assert_called_once()
    
    # Publish report
    service.publish_report(report)
    mock_knowledge_hub.sync_document.assert_called_once()


def test_backward_compatibility_and_custom_extensions():
    # Verify extensibility by subclassing risk analyzer
    class CustomRiskAnalyzer(LocalRiskAnalyzer):
        def analyze_risks(self, objective, affected_files, affected_components, code_summary):
            base_risks = super().analyze_risks(objective, affected_files, affected_components, code_summary)
            base_risks.append("Custom project risk detected.")
            return base_risks
            
    analyzer = CustomRiskAnalyzer()
    risks = analyzer.analyze_risks("Test", [], [], MagicMock())
    assert "Custom project risk detected." in risks

import pytest
import time
from unittest.mock import MagicMock

from aios.services.workspace_intelligence import CodeStructureSummary, SymbolReference
from aios.services.memory import MemoryService
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.file_planner import (
    ModificationType,
    AffectedFile,
    AffectedDirectory,
    ImplementationScope,
    PlanningResult,
)
from aios.services.file_planner_impl import (
    LocalFileImpactAnalyzer,
    LocalFileDependencyResolver,
    LocalChangePlanner,
    LocalFilePlanner,
)


@pytest.fixture
def mock_code_structure():
    # Setup mock dependency graph
    dependency_graph = {
        "core/src/aios/kernel.py": ["core/src/aios/bootstrap.py"],
        "core/src/aios/bootstrap.py": ["core/src/aios/services/memory.py"],
        "core/src/aios/services/memory.py": []
    }
    
    return CodeStructureSummary(
        summary_id="summary_123",
        timestamp=time.time(),
        symbols={},
        call_graph={},
        dependency_graph=dependency_graph,
        inheritance_map={},
        public_apis=["boot", "initialize"]
    )


def test_file_impact_analyzer(mock_code_structure):
    analyzer = LocalFileImpactAnalyzer()
    
    # Matching keyword 'memory'
    files, directories = analyzer.analyze_impact("Optimize memory subsystem", mock_code_structure)
    assert len(files) == 1
    assert files[0].file_path == "core/src/aios/services/memory.py"
    assert len(directories) == 1
    assert directories[0].dir_path == "core/src/aios/services"


def test_file_dependency_resolver(mock_code_structure):
    resolver = LocalFileDependencyResolver()
    
    affected = [
        AffectedFile("core/src/aios/kernel.py", ModificationType.MODIFY, "reason", "Medium")
    ]
    
    direct, indirect, high_risk = resolver.resolve_dependencies(affected, mock_code_structure)
    
    # Direct dep: kernel.py imports bootstrap.py
    assert direct["core/src/aios/kernel.py"] == ["core/src/aios/bootstrap.py"]
    # Indirect dep: kernel.py transitively imports memory.py through bootstrap.py
    assert "core/src/aios/services/memory.py" in indirect["core/src/aios/kernel.py"]


def test_change_planner(mock_code_structure):
    planner = LocalChangePlanner()
    
    files = [
        AffectedFile("core/src/aios/kernel.py", ModificationType.MODIFY, "reason", "Medium"),
        AffectedFile("core/src/aios/bootstrap.py", ModificationType.MODIFY, "reason", "Medium")
    ]
    scope = ImplementationScope(
        workspace_id="ws_1",
        affected_files=files,
        affected_directories=[],
        total_files_count=2
    )
    
    direct_deps = {
        "core/src/aios/kernel.py": ["core/src/aios/bootstrap.py"],
        "core/src/aios/bootstrap.py": []
    }
    
    result = planner.plan_changes("Modify core execution", scope, direct_deps, mock_code_structure)
    
    # Safe ordering: bootstrap.py has no dependency on kernel.py, so it should be implemented first
    assert result.implementation_sequence == ["core/src/aios/bootstrap.py", "core/src/aios/kernel.py"]
    assert len(result.validation_checkpoints) >= 1


def test_file_planner_service_integration(mock_code_structure):
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    
    planner = LocalFilePlanner(
        memory_service=mock_memory,
        knowledge_hub=mock_kh
    )
    planner.initialize()
    
    # Generate result
    result = planner.generate_planning_result("ws_1", "Improve memory storage", mock_code_structure)
    assert result.objective == "Improve memory storage"
    assert len(result.scope.affected_files) >= 1
    
    # Store
    planner.store_planning_result(result)
    mock_memory.add_memory.assert_called_once()
    
    # Publish
    planner.publish_planning_result(result)
    mock_kh.sync_document.assert_called_once()


def test_backward_compatibility():
    class CustomDependencyResolver(LocalFileDependencyResolver):
        def resolve_dependencies(self, affected_files, code_summary):
            direct, indirect, high_risk = super().resolve_dependencies(affected_files, code_summary)
            # Custom logic
            high_risk.append("custom_risk.py")
            return direct, indirect, high_risk
            
    resolver = CustomDependencyResolver()
    _, _, high_risk = resolver.resolve_dependencies([], MagicMock())
    assert "custom_risk.py" in high_risk

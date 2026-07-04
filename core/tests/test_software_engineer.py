import pytest
import time
from unittest.mock import MagicMock

from aios.services.engineering_intelligence import EngineeringReport, EngineeringPlan as EngPlan
from aios.services.memory import MemoryService, MemoryType
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.software_engineer import (
    ImplementationTask,
    ValidationStep,
    DevelopmentPhase,
    SoftwareEngineeringPlan,
)
from aios.services.software_engineer_impl import (
    LocalFeaturePlanner,
    LocalTaskDecomposer,
    LocalExecutionPlanner,
    LocalFilePlanner,
    LocalTestingPlanner,
    LocalDocumentationPlanner,
    LocalImplementationPlanner,
    LocalSoftwareEngineerService,
)


@pytest.fixture
def mock_engineering_report():
    # Setup dummy engineering report
    plan = EngPlan(
        plan_id="plan_123",
        objective="Implement User Profiles",
        timestamp=time.time(),
        ordered_steps=[{"step_id": "s1", "description": "design"}],
        dependencies={},
        required_services=["ModelService"],
        risks=["Breaking change on user profile schema"],
        complexity="Medium",
        estimated_effort_hours=8.0,
        validation_strategy="pytest",
        recommended_execution_order=["profile.py"]
    )
    
    return EngineeringReport(
        report_id="rep_123",
        objective="Implement User Profiles",
        timestamp=time.time(),
        affected_files=[MagicMock(file_path="profile.py", change_type="modify", reason="change")],
        affected_components=[MagicMock(name="UserProfile", component_type="class", impact_level="Medium", description="descr")],
        recommendations=[],
        plan=plan
    )


def test_feature_planner(mock_engineering_report):
    planner = LocalFeaturePlanner()
    phases = planner.plan_features("Objective", mock_engineering_report)
    
    assert len(phases) == 1
    assert phases[0].phase_id == "phase_1_core"
    assert len(phases[0].tasks) == 2
    assert phases[0].tasks[0].task_id == "task_1_interface"


def test_task_decomposer(mock_engineering_report):
    decomposer = LocalTaskDecomposer()
    tasks = decomposer.decompose_tasks("Objective", mock_engineering_report)
    
    assert len(tasks) == 2
    assert tasks[0].priority == "High"
    assert tasks[0].estimated_effort_hours == 2.0


def test_execution_planner():
    planner = LocalExecutionPlanner()
    tasks = [
        ImplementationTask("t1", "title1", "d1", "High", 1.0, [], [], ""),
        ImplementationTask("t2", "title2", "d2", "High", 2.0, [], [], "")
    ]
    order, deps, rollback = planner.plan_execution(tasks)
    
    assert order == ["t1", "t2"]
    assert deps["t2"] == ["t1"]
    assert "git checkout" in rollback.lower()


def test_file_planner(mock_engineering_report):
    planner = LocalFilePlanner()
    files, migrations = planner.plan_files("Objective", mock_engineering_report)
    
    assert "profile.py" in files
    assert len(migrations) == 1


def test_testing_planner(mock_engineering_report):
    planner = LocalTestingPlanner()
    tests, val_strat, test_strat = planner.plan_testing("Objective", mock_engineering_report)
    
    assert len(tests) >= 1
    assert "pytest" in val_strat


def test_documentation_planner(mock_engineering_report):
    planner = LocalDocumentationPlanner()
    docs = planner.plan_documentation("Objective", mock_engineering_report)
    
    assert "PROJECT_STATUS.md" in docs
    assert "KNOWLEDGE_BASE.md" in docs


def test_software_engineer_service_integration(mock_engineering_report):
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    
    service = LocalSoftwareEngineerService(
        memory_service=mock_memory,
        knowledge_hub=mock_kh
    )
    service.initialize()
    
    # Create plan
    plan = service.create_development_plan("Implement Profiles", mock_engineering_report)
    assert plan.objective == "Implement Profiles"
    assert len(plan.phases) >= 1
    
    # Store plan
    service.store_development_plan(plan)
    mock_memory.add_memory.assert_called_once()
    
    # Publish plan
    service.publish_development_plan(plan)
    mock_kh.sync_document.assert_called_once()


def test_backward_compatibility_and_custom_extensions(mock_engineering_report):
    class ExtendedFeaturePlanner(LocalFeaturePlanner):
        def plan_features(self, objective, report):
            base_phases = super().plan_features(objective, report)
            # Add an extra phase
            base_phases.append(
                DevelopmentPhase("phase_custom", "Custom Phase", "Description", [], [])
            )
            return base_phases
            
    planner = ExtendedFeaturePlanner()
    phases = planner.plan_features("Objective", mock_engineering_report)
    assert len(phases) == 2
    assert phases[1].phase_id == "phase_custom"

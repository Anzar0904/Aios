import time
from unittest.mock import MagicMock

import pytest
from aios.services.execution_engine import (
    ExecutionSession,
    ExecutionState,
)
from aios.services.execution_engine_impl import (
    LocalExecutionEngine,
    LocalExecutionValidator,
    LocalTaskExecutor,
)
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.memory import MemoryService
from aios.services.software_engineer import (
    DevelopmentPhase,
    ImplementationTask,
    SoftwareEngineeringPlan,
)


@pytest.fixture
def mock_swe_plan():
    task_1 = ImplementationTask(
        task_id="t1",
        title="Task 1",
        description="d1",
        priority="High",
        estimated_effort_hours=2.0,
        affected_components=["comp1"],
        validation_requirements=["val1"],
        completion_criteria="crit1"
    )
    task_2 = ImplementationTask(
        task_id="t2",
        title="Task 2",
        description="d2",
        priority="High",
        estimated_effort_hours=3.0,
        affected_components=["comp2"],
        validation_requirements=["val2"],
        completion_criteria="crit2"
    )
    phase = DevelopmentPhase(
        phase_id="p1",
        name="Phase 1",
        description="pdescr",
        tasks=[task_1, task_2],
        validation_steps=[]
    )
    return SoftwareEngineeringPlan(
        plan_id="plan_123",
        objective="Feature X",
        timestamp=time.time(),
        phases=[phase],
        execution_order=["t1", "t2"],
        required_files=["file1.py"],
        dependencies={"t2": ["t1"]},
        required_tests=[],
        documentation_updates=[],
        migration_requirements=[],
        rollback_strategy="revert",
        verification_strategy="test",
        testing_strategy="pytest"
    )


def test_validation_pre_flight(mock_swe_plan):
    validator = LocalExecutionValidator()
    session = ExecutionSession(
        session_id="s1",
        plan_id=mock_swe_plan.plan_id,
        state=ExecutionState.RUNNING,
        current_task_idx=0
    )
    
    # Task 1 is first: validation should succeed
    task_1 = mock_swe_plan.phases[0].tasks[0]
    valid, msg = validator.validate_pre_execution(mock_swe_plan, task_1, session)
    assert valid
    
    # Task 2 requires Task 1: validation should fail because Task 1 is not in completed list
    task_2 = mock_swe_plan.phases[0].tasks[1]
    valid_2, msg_2 = validator.validate_pre_execution(mock_swe_plan, task_2, session)
    assert not valid_2
    assert "Dependency" in msg_2


def test_task_executor_user_gate():
    executor = LocalTaskExecutor()
    session = ExecutionSession("s1", "p1", ExecutionState.RUNNING, 0)
    task = ImplementationTask("t1", "Task 1", "d1", "High", 1.0, ["comp1"], [], "crit1")
    
    # Approved
    success, msg, steps = executor.execute_task(task, session, lambda: True)
    assert success
    assert len(steps) == 1
    assert steps[0].status == "completed"
    
    # Rejected
    success_rej, msg_rej, steps_rej = executor.execute_task(task, session, lambda: False)
    assert not success_rej
    assert steps_rej[0].status == "failed"


def test_execution_engine_lifecycle(mock_swe_plan):
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    
    engine = LocalExecutionEngine(
        memory_service=mock_memory,
        knowledge_hub=mock_kh
    )
    engine.initialize()
    
    # 1. Create Session
    session = engine.create_session(mock_swe_plan)
    assert session.state == ExecutionState.PENDING
    assert session.current_task_idx == 0
    
    # 2. Start execution (approved)
    res = engine.start_execution(session.session_id, lambda: True)
    assert res.success
    assert session.state == ExecutionState.COMPLETED
    assert len(session.completed_tasks) == 2
    assert len(session.checkpoints) == 2


def test_execution_engine_pause_resume(mock_swe_plan):
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    
    engine = LocalExecutionEngine(memory_service=mock_memory, knowledge_hub=mock_kh)
    session = engine.create_session(mock_swe_plan)
    
    # Implement callback that pauses the engine after task 1
    call_count = 0
    def approval_callback():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            engine.pause_execution(session.session_id)
        return True

    res = engine.start_execution(session.session_id, approval_callback)
    # Loop broke because status was changed to paused
    assert not res.success
    assert session.state == ExecutionState.PAUSED
    assert len(session.completed_tasks) == 1
    assert session.current_task_idx == 1

    # Resume execution
    res_resume = engine.resume_execution(session.session_id, lambda: True)
    assert res_resume.success
    assert session.state == ExecutionState.COMPLETED
    assert len(session.completed_tasks) == 2


def test_rollback_generation(mock_swe_plan):
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    engine = LocalExecutionEngine(memory_service=mock_memory, knowledge_hub=mock_kh)
    
    session = engine.create_session(mock_swe_plan)
    engine.start_execution(session.session_id, lambda: True)
    
    # Rollback Plan
    rollback = engine.generate_rollback_plan(session.session_id)
    assert rollback.task_id == "t2"
    assert "file1.py" in rollback.target_files
    assert "Undo changes from task" in rollback.rollback_instructions


def test_memory_and_knowledge_hub_integration(mock_swe_plan):
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    engine = LocalExecutionEngine(memory_service=mock_memory, knowledge_hub=mock_kh)
    
    session = engine.create_session(mock_swe_plan)
    engine.start_execution(session.session_id, lambda: True)
    
    # Store
    engine.store_execution_summary(session.session_id)
    mock_memory.add_memory.assert_called_once()
    
    # Publish
    engine.publish_execution_report(session.session_id)
    mock_kh.sync_document.assert_called_once()


def test_backward_compatibility():
    class CustomExecutionValidator(LocalExecutionValidator):
        def validate_pre_execution(self, plan, task, session):
            valid, reason = super().validate_pre_execution(plan, task, session)
            if not valid:
                return False, reason
            return True, "Custom validation check passed."
            
    validator = CustomExecutionValidator()
    # Should work seamlessly
    assert validator is not None

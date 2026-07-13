import os
import time
from unittest.mock import MagicMock

import pytest
from aios.services.ai_workspace import AIWorkspaceService, WorkspaceMetadata
from aios.services.approval import (
    ApprovalDecision,
    ApprovalEvidence,
    ApprovalPackage,
    ApprovalReport,
    ApprovalRequest,
    ApprovalRule,
    ApprovalStatus,
    ApprovalSummary,
)
from aios.services.approval_impl import (
    CriticalFailureThresholdRule,
    LocalApprovalEngineService,
    LocalApprovalManager,
    LocalApprovalValidator,
    MaxRiskLevelRule,
    MinValidationScoreRule,
    RequiredCoverageRule,
)
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.memory import MemoryService
from aios.services.model import LLMResponse, ModelService


@pytest.fixture
def mock_memory_service():
    service = MagicMock(spec=MemoryService)
    service.search_memory.return_value = []
    return service


@pytest.fixture
def mock_workspace_service():
    service = MagicMock(spec=AIWorkspaceService)
    return service


@pytest.fixture
def mock_model_service():
    service = MagicMock(spec=ModelService)
    response = MagicMock(spec=LLMResponse)
    response.content = "LLM Refined Approval reasoning."
    service.execute_request.return_value = response
    return service


def test_rules_evaluation():
    # Construct a dummy package
    package = ApprovalPackage(
        package_id="pkg_1",
        workspace_id="ws_1",
        engineering_summary="Test sum",
        validation_summary={"score": 85.0},
        documentation_summary={"completed": True, "missing_docs": []},
        risk_summary={"risk_level": "medium"},
        affected_files=["core/kernel.py"],
        affected_components=["Kernel"],
        coverage_summary={"achieved_pct": 80.0},
        failure_summary={"critical_count": 0},
        recommendations=[],
        policy=MagicMock(),
        reviewer_notes=[],
        approval_history=[],
        confidence_score=0.9,
        overall_health="healthy"
    )

    # 1. Validation Score Rule
    rule_score_pass = MinValidationScoreRule(80.0)
    ok, reason = rule_score_pass.evaluate(package)
    assert ok is True
    assert "meets min requirement" in reason

    rule_score_fail = MinValidationScoreRule(90.0)
    ok, reason = rule_score_fail.evaluate(package)
    assert ok is False
    assert "below minimum" in reason

    # 2. Coverage Rule
    rule_cov_pass = RequiredCoverageRule(75.0)
    ok, reason = rule_cov_pass.evaluate(package)
    assert ok is True

    # 3. Risk Level Rule
    rule_risk_pass = MaxRiskLevelRule("high")
    ok, reason = rule_risk_pass.evaluate(package)
    assert ok is True

    rule_risk_fail = MaxRiskLevelRule("low")
    ok, reason = rule_risk_fail.evaluate(package)
    assert ok is False

    # 4. Critical Failure Threshold Rule
    rule_fail_pass = CriticalFailureThresholdRule(0)
    ok, reason = rule_fail_pass.evaluate(package)
    assert ok is True


def test_package_construction():
    manager = LocalApprovalManager()
    evidence = [
        ApprovalEvidence("validation_report", "test_run", {"overall_score": 92.5, "total_tests_run": 345, "coverage_pct": 85.0, "critical_count": 0}, 0.0),
        ApprovalEvidence("engineering_intelligence", "analysis", {"objective": "Upgrade Kernel", "risk_level": "medium", "affected_files": ["f1.py"]}, 0.0),
        ApprovalEvidence("readme_intelligence", "report", {"missing_sections": ["Installation"]}, 0.0),
        ApprovalEvidence("engineering_profile", "config", {"language": "typescript"}, 0.0)
    ]
    request = ApprovalRequest("req_1", "ws_1", "1.0.0", "standard", evidence, 0.0)
    session = manager.create_session(request)
    package = manager.compile_package(session)

    assert package.workspace_id == "ws_1"
    assert package.engineering_summary == "Upgrade Kernel"
    assert package.validation_summary["score"] == 92.5
    assert package.documentation_summary["completed"] is False
    assert "Installation" in package.documentation_summary["missing_docs"]
    assert package.risk_summary["risk_level"] == "medium"
    assert "f1.py" in package.affected_files
    assert package.metadata["profile_language"] == "typescript"


def test_decision_generation_approved():
    manager = LocalApprovalManager()
    evidence = [
        ApprovalEvidence("validation_report", "test_run", {"overall_score": 90.0, "coverage_pct": 80.0, "critical_count": 0}, 0.0),
        ApprovalEvidence("engineering_intelligence", "analysis", {"objective": "Clean objective", "risk_level": "low"}, 0.0),
        ApprovalEvidence("engineering_profile", "config", {"language": "python"}, 0.0)
    ]
    request = ApprovalRequest("req_1", "ws_1", "1.0.0", "standard", evidence, 0.0)
    session = manager.create_session(request)
    package = manager.compile_package(session)
    decision = manager.evaluate_policy(package)

    assert decision.status == ApprovalStatus.APPROVED
    assert "safety checks" in decision.reasoning.lower()


def test_decision_generation_rejected():
    manager = LocalApprovalManager()
    evidence = [
        ApprovalEvidence("validation_report", "test_run", {"overall_score": 50.0, "coverage_pct": 40.0, "critical_count": 2}, 0.0),
        ApprovalEvidence("engineering_intelligence", "analysis", {"objective": "Dangerous objective", "risk_level": "critical"}, 0.0)
    ]
    request = ApprovalRequest("req_1", "ws_1", "1.0.0", "standard", evidence, 0.0)
    session = manager.create_session(request)
    package = manager.compile_package(session)
    decision = manager.evaluate_policy(package)

    assert decision.status == ApprovalStatus.REJECTED
    assert "failed" in decision.reasoning.lower()


def test_validator():
    validator = LocalApprovalValidator()
    
    # Incomplete package
    package = ApprovalPackage(
        package_id="pkg_1",
        workspace_id="ws_1",
        engineering_summary="",
        validation_summary={},
        documentation_summary={},
        risk_summary={},
        affected_files=[],
        affected_components=[],
        coverage_summary={},
        failure_summary={},
        recommendations=[],
        policy=MagicMock(),
        reviewer_notes=[],
        approval_history=[],
        confidence_score=2.0,  # invalid
        overall_health=""
    )
    errors = validator.validate_package(package)
    assert len(errors) > 0
    assert any("engineering summary" in e.lower() for e in errors)
    assert any("confidence score" in e.lower() for e in errors)

    # Duplicate check
    history = [
        ApprovalSummary("sum_1", "sess_1", "ws_1", ApprovalStatus.APPROVED, 0.9, "healthy", 100.0)
    ]
    req = ApprovalRequest("req_2", "ws_1", "1.0.0", "standard", [], 130.0)  # within 60s
    assert validator.check_duplicate_request(req, history) is True

    req_diff_ws = ApprovalRequest("req_3", "ws_other", "1.0.0", "standard", [], 130.0)
    assert validator.check_duplicate_request(req_diff_ws, history) is False


def test_workspace_integration(tmp_path, mock_memory_service, mock_workspace_service):
    ws_id = "ws_test_approval"
    ws_root = str(tmp_path / ws_id)
    os.makedirs(ws_root, exist_ok=True)
    
    meta = WorkspaceMetadata(ws_id, 0.0, "/src", ws_root, "active")
    mock_workspace_service._workspaces = {ws_id: meta}
    
    registry = MagicMock()
    registry.get.side_effect = lambda t: mock_workspace_service if t == AIWorkspaceService else None

    service = LocalApprovalEngineService(
        memory_service=mock_memory_service,
        registry=registry
    )
    service.initialize()

    request = ApprovalRequest("req_1", ws_id, "1.0.0", "standard", [], 0.0)
    session = service.request_approval(request)

    expected_file = os.path.join(ws_root, "docs", "approvals", f"APPROVAL_REPORT_{session.session_id}.md")
    assert os.path.exists(expected_file)
    with open(expected_file, "r") as f:
        report_content = f.read()
    assert "# Approval Package Decision Report" in report_content
    assert session.status == "closed"


def test_memory_integration(mock_memory_service):
    service = LocalApprovalEngineService(
        memory_service=mock_memory_service
    )
    
    request = ApprovalRequest("req_1", "ws_1", "1.0.0", "standard", [], 0.0)
    session = service._manager.create_session(request)
    package = service._manager.compile_package(session)
    session.package = package
    session.decision = ApprovalDecision(ApprovalStatus.APPROVED, "reason", [], 100.0)
    
    service.store_approval_summary(session)
    
    mock_memory_service.add_memory.assert_called_once()
    args, kwargs = mock_memory_service.add_memory.call_args
    content = kwargs.get("content", args[0] if args else "")
    tags = kwargs.get("tags", [])
    
    # Ensure source code not stored and metadata summaries only
    assert "source code" not in content.lower()
    assert "Approval Decision Logged" in content
    assert "approval_decision" in tags


def test_knowledge_hub_integration(mock_memory_service):
    mock_kh = MagicMock(spec=KnowledgeHubService)
    service = LocalApprovalEngineService(
        memory_service=mock_memory_service,
        knowledge_hub=mock_kh
    )
    
    report = ApprovalReport("rep_1", "ws_1", "sess_1", ApprovalDecision(ApprovalStatus.APPROVED, "reason", []), {}, time.time())
    service.publish_approval_report(report)
    
    mock_kh.sync_document.assert_called_once()
    args, kwargs = mock_kh.sync_document.call_args
    doc = args[0]
    assert doc.title == "Approval Gate - rep_1"
    assert "APPROVED" in doc.content


def test_backward_compatibility():
    class CustomRule(ApprovalRule):
        def evaluate(self, package):
            return True, "Custom passes always."
            
    rule = CustomRule("CustomRule", "Ensures custom logic passes.")
    ok, reason = rule.evaluate(None)
    assert ok is True
    assert reason == "Custom passes always."

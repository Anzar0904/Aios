import os
import time
import pytest
from unittest.mock import MagicMock

from aios.services.memory import MemoryService, MemoryType
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.model import ModelService, LLMResponse
from aios.services.ai_workspace import AIWorkspaceService, WorkspaceMetadata
from aios.services.approval import ApprovalPackage
from aios.services.review import (
    ReviewCategory,
    ReviewSeverity,
    ReviewEvidence,
    ReviewRecommendation,
    ReviewFinding,
    ReviewSummary,
    ReviewReport,
)
from aios.services.review_impl import (
    LocalReviewAnalyzer,
    LocalReviewValidator,
    LocalReviewEngine,
)


@pytest.fixture
def mock_memory_service():
    service = MagicMock(spec=MemoryService)
    return service


@pytest.fixture
def mock_workspace_service():
    service = MagicMock(spec=AIWorkspaceService)
    return service


@pytest.fixture
def mock_model_service():
    service = MagicMock(spec=ModelService)
    response = MagicMock(spec=LLMResponse)
    response.content = "LLM Refined Code Review overview."
    service.execute_request.return_value = response
    return service


@pytest.fixture
def dummy_package():
    return ApprovalPackage(
        package_id="pkg_test_1",
        workspace_id="ws_1",
        engineering_summary="Clean objective description",
        validation_summary={"score": 75.0, "status": "fail", "tests_run_count": 50},
        documentation_summary={"completed": False, "missing_docs": ["API Reference"]},
        risk_summary={"risk_level": "critical", "areas": ["kernel"]},
        affected_files=["core/kernel.py"],
        affected_components=["Kernel"],
        coverage_summary={"achieved_pct": 70.0},
        failure_summary={"critical_count": 3},
        recommendations=[],
        policy=MagicMock(),
        reviewer_notes=[],
        approval_history=[],
        confidence_score=0.85,
        overall_health="degraded",
        evidence=[],
        metadata={"profile_language": "python"}
    )


def test_review_analysis(dummy_package):
    analyzer = LocalReviewAnalyzer()
    summary, findings = analyzer.analyze_package("ws_1", dummy_package)

    assert summary.overall_health == "degraded"
    assert "critical" in summary.risk_summary.lower()
    assert len(summary.weaknesses) > 0

    # Ensure findings categorization maps correctly
    categories = [f.category for f in findings]
    severities = [f.severity for f in findings]

    assert ReviewCategory.RELIABILITY in categories
    assert ReviewCategory.TESTING in categories
    assert ReviewCategory.DOCUMENTATION in categories
    assert ReviewCategory.DEPENDENCY_RISK in categories

    assert ReviewSeverity.CRITICAL in severities
    assert ReviewSeverity.HIGH in severities
    assert ReviewSeverity.MEDIUM in severities

    # Ensure blocking flag behaves correctly
    assert any(f.blocking for f in findings if f.severity == ReviewSeverity.CRITICAL)


def test_review_validation():
    validator = LocalReviewValidator()

    # 1. Inconsistent severity (blocking but low severity)
    finding_bad_severity = ReviewFinding(
        finding_id="f1",
        category=ReviewCategory.SECURITY,
        severity=ReviewSeverity.LOW,
        confidence=0.9,
        description="Low severity warning",
        evidence=[ReviewEvidence("source", "type", {}, 0.0)],
        recommendation=ReviewRecommendation("rec_1", "action", ["step"]),
        blocking=True  # Blocking but low severity!
    )
    report = ReviewReport(
        report_id="rep_1",
        session_id="sess_1",
        workspace_id="ws_1",
        summary=ReviewSummary("sum_1", "overview", "healthy", "low", reviewer_confidence=0.9),
        findings=[finding_bad_severity]
    )

    errors = validator.validate_review(report)
    assert len(errors) > 0
    assert any("severity consistency" in e.lower() for e in errors)

    # 2. Duplicate findings
    finding_dup = ReviewFinding(
        finding_id="f2",
        category=ReviewCategory.SECURITY,
        severity=ReviewSeverity.LOW,
        confidence=0.9,
        description="Low severity warning",
        evidence=[ReviewEvidence("source", "type", {}, 0.0)],
        recommendation=ReviewRecommendation("rec_2", "action", ["step"]),
        blocking=False
    )
    report_dup = ReviewReport(
        report_id="rep_1",
        session_id="sess_1",
        workspace_id="ws_1",
        summary=ReviewSummary("sum_1", "overview", "healthy", "low", reviewer_confidence=0.9),
        findings=[finding_bad_severity, finding_dup]
    )
    # Clear blocking to bypass first check
    finding_bad_severity.blocking = False
    errors_dup = validator.validate_review(report_dup)
    assert any("duplicate finding" in e.lower() for e in errors_dup)

    # 3. Missing evidence
    finding_no_evidence = ReviewFinding(
        finding_id="f3",
        category=ReviewCategory.MAINTAINABILITY,
        severity=ReviewSeverity.MEDIUM,
        confidence=0.8,
        description="Maintainability check",
        evidence=[],  # empty
        recommendation=ReviewRecommendation("rec_3", "action", ["step"]),
        blocking=False
    )
    report_no_ev = ReviewReport(
        report_id="rep_1",
        session_id="sess_1",
        workspace_id="ws_1",
        summary=ReviewSummary("sum_1", "overview", "healthy", "low", reviewer_confidence=0.9),
        findings=[finding_no_evidence]
    )
    errors_no_ev = validator.validate_review(report_no_ev)
    assert any("lacks supporting telemetry" in e.lower() for e in errors_no_ev)


def test_workspace_integration(tmp_path, mock_memory_service, mock_workspace_service, dummy_package):
    ws_id = "ws_test_review"
    ws_root = str(tmp_path / ws_id)
    os.makedirs(ws_root, exist_ok=True)

    meta = WorkspaceMetadata(ws_id, 0.0, "/src", ws_root, "active")
    mock_workspace_service._workspaces = {ws_id: meta}

    registry = MagicMock()
    registry.get.side_effect = lambda t: mock_workspace_service if t == AIWorkspaceService else None

    engine = LocalReviewEngine(
        memory_service=mock_memory_service,
        registry=registry
    )
    engine.initialize()

    session = engine.run_review(ws_id, dummy_package)
    expected_file = os.path.join(ws_root, "docs", "reviews", f"REVIEW_REPORT_{session.session_id}.md")
    
    assert os.path.exists(expected_file)
    with open(expected_file, "r") as f:
        content = f.read()
    assert "# Intelligent Review Engine Report" in content
    assert session.status == "closed"


def test_memory_integration(mock_memory_service, dummy_package):
    engine = LocalReviewEngine(
        memory_service=mock_memory_service
    )
    session = engine.run_review("ws_1", dummy_package)
    engine.store_review_summary(session)

    mock_memory_service.add_memory.assert_called_once()
    args, kwargs = mock_memory_service.add_memory.call_args
    content = kwargs.get("content", args[0] if args else "")
    tags = kwargs.get("tags", [])

    assert "source code" not in content.lower()
    assert "Intelligent Quality Review Logged" in content
    assert "quality_review" in tags


def test_knowledge_hub_integration(mock_memory_service, dummy_package):
    mock_kh = MagicMock(spec=KnowledgeHubService)
    engine = LocalReviewEngine(
        memory_service=mock_memory_service,
        knowledge_hub=mock_kh
    )
    
    session = engine.run_review("ws_1", dummy_package)
    engine.publish_review_report(session.report)

    mock_kh.sync_document.assert_called_once()
    args, kwargs = mock_kh.sync_document.call_args
    doc = args[0]
    assert doc.title == f"Quality Review - rep_{session.session_id}"
    assert "Notion Sync" in doc.content


def test_backward_compatibility(dummy_package):
    class CustomReviewAnalyzer(LocalReviewAnalyzer):
        def analyze_package(self, workspace_id, package):
            summary, findings = super().analyze_package(workspace_id, package)
            # Add custom strength
            summary.strengths.append("Custom strength check passed.")
            return summary, findings

    analyzer = CustomReviewAnalyzer()
    summary, findings = analyzer.analyze_package("ws_1", dummy_package)
    assert "Custom strength check passed." in summary.strengths

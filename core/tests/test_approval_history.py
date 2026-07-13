import os
import time
from unittest.mock import MagicMock

import pytest
from aios.services.ai_workspace import AIWorkspaceService, WorkspaceMetadata
from aios.services.approval_history import (
    ApprovalDecisionRecord,
    ApprovalHistoryEntry,
    ApprovalHistoryReport,
    ApprovalState,
    ApprovalStatistics,
)
from aios.services.approval_history_impl import (
    LocalApprovalHistoryAnalyzer,
    LocalApprovalHistoryService,
    LocalApprovalHistoryValidator,
)
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.memory import MemoryService
from aios.services.model import LLMResponse, ModelService


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
    response.content = "LLM Refined Decision History details."
    service.execute_request.return_value = response
    return service


def test_state_machine_valid_transitions():
    validator = LocalApprovalHistoryValidator()

    # Valid transitions
    assert validator.validate_transition(ApprovalState.DRAFT, ApprovalState.SUBMITTED) is True
    assert (
        validator.validate_transition(ApprovalState.SUBMITTED, ApprovalState.UNDER_REVIEW) is True
    )
    assert validator.validate_transition(ApprovalState.UNDER_REVIEW, ApprovalState.APPROVED) is True
    assert (
        validator.validate_transition(ApprovalState.UNDER_REVIEW, ApprovalState.CHANGES_REQUESTED)
        is True
    )
    assert (
        validator.validate_transition(ApprovalState.CHANGES_REQUESTED, ApprovalState.UPDATED)
        is True
    )
    assert validator.validate_transition(ApprovalState.UPDATED, ApprovalState.UNDER_REVIEW) is True

    # Invalid transitions
    assert validator.validate_transition(ApprovalState.DRAFT, ApprovalState.APPROVED) is False
    assert (
        validator.validate_transition(ApprovalState.APPROVED, ApprovalState.UNDER_REVIEW) is False
    )
    assert validator.validate_transition(ApprovalState.REJECTED, ApprovalState.SUBMITTED) is False


def test_history_service_transitions(mock_memory_service):
    service = LocalApprovalHistoryService(memory_service=mock_memory_service)
    service.initialize()

    # Create entry
    entry = service.create_history_entry("ws_1", "sess_1", ApprovalState.UNDER_REVIEW, "Alice")
    assert entry.state_transitions[0].to_state == ApprovalState.UNDER_REVIEW

    # Transition to changes requested
    service.transition_state("ws_1", "sess_1", ApprovalState.CHANGES_REQUESTED, "Bob", "Lacks docs")
    assert entry.state_transitions[-1].to_state == ApprovalState.CHANGES_REQUESTED
    assert entry.state_transitions[-1].from_state == ApprovalState.UNDER_REVIEW
    assert entry.state_transitions[-1].actor == "Bob"

    # Reject invalid transition
    with pytest.raises(ValueError):
        service.transition_state("ws_1", "sess_1", ApprovalState.APPROVED, "Bob", "Force pass")


def test_analyzer_statistics_and_trends():
    analyzer = LocalReviewHistoryAnalyzerWrapper()
    records = [
        ApprovalDecisionRecord(
            "rec_1", "sess_1", "ws_1", ApprovalState.APPROVED, 0.9, 85.0, 80.0, False, 2, 100.0
        ),
        ApprovalDecisionRecord(
            "rec_2",
            "sess_2",
            "ws_1",
            ApprovalState.CHANGES_REQUESTED,
            0.7,
            75.0,
            70.0,
            True,
            1,
            110.0,
        ),
        ApprovalDecisionRecord(
            "rec_3",
            "sess_3",
            "ws_1",
            ApprovalState.APPROVED_WITH_CONDITIONS,
            0.95,
            95.0,
            90.0,
            False,
            3,
            120.0,
        ),
    ]

    # Stats
    stats = analyzer.compile_statistics(records)
    assert stats.total_sessions == 3
    assert stats.approved_count == 2
    assert stats.changes_requested_count == 1
    assert stats.average_confidence == pytest.approx(0.85)
    assert stats.average_validation_score == pytest.approx(85.0)
    assert stats.average_coverage == pytest.approx(80.0)

    # Trends
    trends = analyzer.analyze_trends(records)
    assert len(trends) == 3
    val_trend = next(t for t in trends if "Validation" in t.metric_name)
    assert val_trend.direction == "improving"  # 85.0 -> 75.0 -> 95.0, ends higher than first


def test_analyzer_pattern_discovery():
    analyzer = LocalReviewHistoryAnalyzerWrapper()
    entries = [
        ApprovalHistoryEntry("ent_1", "sess_1", "ws_1", [], {"documentation_incomplete": True}),
        ApprovalHistoryEntry("ent_2", "sess_2", "ws_1", [], {"documentation_incomplete": True}),
    ]
    records = [
        ApprovalDecisionRecord(
            "rec_1", "sess_1", "ws_1", ApprovalState.REJECTED, 0.6, 50.0, 45.0, True, 1, 100.0
        ),
        ApprovalDecisionRecord(
            "rec_2", "sess_2", "ws_1", ApprovalState.REJECTED, 0.6, 55.0, 40.0, True, 1, 110.0
        ),
    ]

    patterns = analyzer.discover_patterns(entries, records)
    assert len(patterns) >= 2
    types = [p.pattern_type for p in patterns]
    assert "repeated_blocker" in types
    assert "documentation_gap" in types


def test_workspace_integration(tmp_path, mock_memory_service, mock_workspace_service):
    ws_id = "ws_test_history"
    ws_root = str(tmp_path / ws_id)
    os.makedirs(ws_root, exist_ok=True)

    meta = WorkspaceMetadata(ws_id, 0.0, "/src", ws_root, "active")
    mock_workspace_service._workspaces = {ws_id: meta}

    registry = MagicMock()
    registry.get.side_effect = lambda t: mock_workspace_service if t == AIWorkspaceService else None

    service = LocalApprovalHistoryService(memory_service=mock_memory_service, registry=registry)
    service.initialize()

    record = ApprovalDecisionRecord(
        "rec_1", "sess_1", ws_id, ApprovalState.APPROVED, 0.9, 85.0, 80.0, False, 2, time.time()
    )
    service.record_decision(record)

    service.run_history_analysis(ws_id)
    expected_file = os.path.join(ws_root, "docs", "histories", f"APPROVAL_HISTORY_{ws_id}.md")

    assert os.path.exists(expected_file)
    with open(expected_file, "r") as f:
        content = f.read()
    assert "# Decision Intelligence Gating History Report" in content


def test_memory_integration(mock_memory_service):
    service = LocalApprovalHistoryService(memory_service=mock_memory_service)
    service.initialize()

    record = ApprovalDecisionRecord(
        "rec_1", "sess_1", "ws_1", ApprovalState.APPROVED, 0.9, 85.0, 80.0, False, 2, time.time()
    )
    service.record_decision(record)

    service.store_history_summary("ws_1")

    mock_memory_service.add_memory.assert_called_once()
    args, kwargs = mock_memory_service.add_memory.call_args
    content = kwargs.get("content", args[0] if args else "")
    tags = kwargs.get("tags", [])

    assert "source code" not in content.lower()
    assert "Approval Gating Trends Synced" in content
    assert "gating_history_trends" in tags


def test_knowledge_hub_integration(mock_memory_service):
    mock_kh = MagicMock(spec=KnowledgeHubService)
    service = LocalApprovalHistoryService(memory_service=mock_memory_service, knowledge_hub=mock_kh)
    service.initialize()

    stats = ApprovalStatistics(1, 1, 0, 0, 0.9, 90.0, 80.0)
    report = ApprovalHistoryReport(
        report_id="rep_hist_ws_1", workspace_id="ws_1", statistics=stats, timestamp=time.time()
    )
    service.publish_history_report(report)

    mock_kh.sync_document.assert_called_once()
    args, kwargs = mock_kh.sync_document.call_args
    doc = args[0]
    assert doc.title == "Gating History - rep_hist_ws_1"
    assert "Notion Sync" in doc.content


def test_backward_compatibility(mock_memory_service):
    class CustomHistoryService(LocalApprovalHistoryService):
        def record_decision(self, record):
            # Intercept decision recording
            super().record_decision(record)
            record.metadata_custom = "intercepted"

    service = CustomHistoryService(memory_service=mock_memory_service)
    service.initialize()

    record = ApprovalDecisionRecord(
        "rec_1", "sess_1", "ws_1", ApprovalState.APPROVED, 0.9, 85.0, 80.0, False, 2, time.time()
    )
    service.record_decision(record)
    assert record.metadata_custom == "intercepted"


class LocalReviewHistoryAnalyzerWrapper(LocalApprovalHistoryAnalyzer):
    """Wrapper class assisting test checks on analyzer logic."""

    pass

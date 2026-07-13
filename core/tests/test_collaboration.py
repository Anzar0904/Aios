import os
import time
from unittest.mock import MagicMock

import pytest
from aios.services.ai_workspace import AIWorkspaceService, WorkspaceMetadata
from aios.services.collaboration import (
    ReviewAction,
    ReviewCollaborationReport,
    ReviewComment,
    Reviewer,
    ReviewerRole,
    ReviewVote,
)
from aios.services.collaboration_impl import (
    LocalReviewCollaborationService,
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
    response.content = "LLM Refined Reviewer Consensus details."
    service.execute_request.return_value = response
    return service


def test_reviewer_roles():
    reviewer = Reviewer(
        reviewer_id="rev_1",
        name="Alice",
        role=ReviewerRole.ARCHITECT,
        permissions=["resolve_thread", "cast_vote"],
    )
    assert reviewer.role == ReviewerRole.ARCHITECT
    assert "cast_vote" in reviewer.permissions


def test_comment_and_thread_lifecycle(mock_memory_service):
    service = LocalReviewCollaborationService(memory_service=mock_memory_service)
    service.initialize()

    # 1. Thread creation
    comment = ReviewComment(
        comment_id="c1",
        author="Alice",
        content="This is an architectural issue.",
        comment_type="architecture",
        timestamp=time.time(),
        linked_artifacts=["core/kernel.py"],
    )
    thread = service.create_thread("ws_1", "sess_1", comment)
    assert thread.root_comment.author == "Alice"
    assert thread.root_comment.comment_type == "architecture"
    assert thread.resolution_state == "open"

    # 2. Nested reply
    reply = ReviewComment(
        comment_id="c2",
        author="Bob",
        content="I will fix it in the next patch.",
        comment_type="general",
        timestamp=time.time(),
    )
    service.reply_to_comment("ws_1", thread.thread_id, "c1", reply)

    threads = service.get_threads("ws_1", "sess_1")
    assert len(threads[0].root_comment.replies) == 1
    assert threads[0].root_comment.replies[0].author == "Bob"

    # 3. Resolve thread
    service.resolve_thread("ws_1", thread.thread_id, "Alice")
    assert threads[0].resolution_state == "resolved"
    assert threads[0].resolved_by == "Alice"

    # 4. Reopen thread
    service.reopen_thread("ws_1", thread.thread_id, "Bob")
    assert threads[0].resolution_state == "open"
    assert threads[0].resolved_by is None


def test_audit_log_and_timeline(mock_memory_service):
    service = LocalReviewCollaborationService(memory_service=mock_memory_service)
    service.initialize()

    comment = ReviewComment("c1", "Alice", "Validation comments", "validation", time.time())
    service.create_thread("ws_1", "sess_1", comment)

    vote = ReviewVote("Bob", "approve_with_conditions", "Minor code style warnings.", time.time())
    service.cast_vote("ws_1", "sess_1", vote)

    audit_log = service.get_audit_log("ws_1", "sess_1")
    assert len(audit_log) == 2
    assert audit_log[0].action == ReviewAction.CREATE
    assert audit_log[1].action == ReviewAction.VOTE

    timeline = service.get_timeline("ws_1", "sess_1")
    assert len(timeline.events) == 2
    assert timeline.events[1].actor == "Bob"


def test_workspace_integration(tmp_path, mock_memory_service, mock_workspace_service):
    ws_id = "ws_test_collab"
    ws_root = str(tmp_path / ws_id)
    os.makedirs(ws_root, exist_ok=True)

    meta = WorkspaceMetadata(ws_id, 0.0, "/src", ws_root, "active")
    mock_workspace_service._workspaces = {ws_id: meta}

    registry = MagicMock()
    registry.get.side_effect = lambda t: mock_workspace_service if t == AIWorkspaceService else None

    service = LocalReviewCollaborationService(memory_service=mock_memory_service, registry=registry)
    service.initialize()

    comment = ReviewComment("c1", "Alice", "Doc issue", "documentation", time.time())
    service.create_thread(ws_id, "sess_collab_1", comment)

    service.compile_collaboration_report(ws_id, "sess_collab_1")
    expected_file = os.path.join(
        ws_root, "docs", "collaborations", "COLLABORATION_REPORT_sess_collab_1.md"
    )

    assert os.path.exists(expected_file)
    with open(expected_file, "r") as f:
        content = f.read()
    assert "# Gate Review Collaboration Report" in content


def test_memory_integration(mock_memory_service):
    service = LocalReviewCollaborationService(memory_service=mock_memory_service)
    service.initialize()

    comment = ReviewComment("c1", "Alice", "General comments", "general", time.time())
    service.create_thread("ws_1", "sess_1", comment)
    service.cast_vote("ws_1", "sess_1", ReviewVote("Bob", "approve", "Approved", time.time()))

    service.store_collaboration_summary("ws_1", "sess_1")

    mock_memory_service.add_memory.assert_called_once()
    args, kwargs = mock_memory_service.add_memory.call_args
    content = kwargs.get("content", args[0] if args else "")
    tags = kwargs.get("tags", [])

    assert "source code" not in content.lower()
    assert "Review Collaboration Summary Logged" in content
    assert "collaboration_review" in tags


def test_knowledge_hub_integration(mock_memory_service):
    mock_kh = MagicMock(spec=KnowledgeHubService)
    service = LocalReviewCollaborationService(
        memory_service=mock_memory_service, knowledge_hub=mock_kh
    )
    service.initialize()

    report = ReviewCollaborationReport(
        report_id="rep_collab_sess_1",
        workspace_id="ws_1",
        session_id="sess_1",
        vote_summary={"approve": 1},
        timestamp=time.time(),
    )
    service.publish_collaboration_report(report)

    mock_kh.sync_document.assert_called_once()
    args, kwargs = mock_kh.sync_document.call_args
    doc = args[0]
    assert doc.title == "Gate Collaboration - rep_collab_sess_1"
    assert "Notion Sync" in doc.content


def test_backward_compatibility(mock_memory_service):
    class CustomCollaborationService(LocalReviewCollaborationService):
        def create_thread(self, workspace_id, session_id, comment):
            # Intercept thread creation
            thread = super().create_thread(workspace_id, session_id, comment)
            thread.resolution_state = "intercepted"
            return thread

    service = CustomCollaborationService(memory_service=mock_memory_service)
    service.initialize()
    comment = ReviewComment("c1", "Alice", "Intercepted check", "general", time.time())
    thread = service.create_thread("ws_1", "sess_1", comment)
    assert thread.resolution_state == "intercepted"

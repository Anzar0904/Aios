import logging
import os
import time
from typing import Any, Dict, List, Optional

from aios.services.ai_workspace import AIWorkspaceService
from aios.services.collaboration import (
    ReviewAction,
    ReviewAuditLog,
    ReviewCollaborationReport,
    ReviewCollaborationService,
    ReviewComment,
    ReviewThread,
    ReviewTimeline,
    ReviewVote,
)
from aios.services.knowledge_hub import (
    KnowledgeDocument,
    KnowledgeHubService,
)
from aios.services.knowledge_hub import (
    KnowledgeMetadata as KHMetadata,
)
from aios.services.memory import MemoryService, MemoryType
from aios.services.model import LLMRequest, ModelService

logger = logging.getLogger(__name__)


class LocalReviewCollaborationService(ReviewCollaborationService):
    """Concrete collaboration coordinator managing reviewer feedback and immutable audit traces."""

    def __init__(
        self,
        memory_service: MemoryService,
        knowledge_hub: Optional[KnowledgeHubService] = None,
        model_service: Optional[ModelService] = None,
        registry: Optional[Any] = None,
    ) -> None:
        self._memory = memory_service
        self._knowledge_hub = knowledge_hub
        self._model = model_service
        self._registry = registry

        self._threads: Dict[str, List[ReviewThread]] = {}
        self._timelines: Dict[str, ReviewTimeline] = {}
        self._votes: Dict[str, List[ReviewVote]] = {}
        self._audit_logs: Dict[str, List[ReviewAuditLog]] = {}

    def initialize(self) -> None:
        logger.info("Initializing LocalReviewCollaborationService")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def _write_to_workspace(self, workspace_id: str, filename: str, content: str) -> str:
        workspace_root = None
        workspace_service = None
        if self._registry:
            try:
                workspace_service = self._registry.get(AIWorkspaceService)
            except Exception:
                pass

        if workspace_service and hasattr(workspace_service, "_workspaces"):
            meta = workspace_service._workspaces.get(workspace_id)
            if meta:
                workspace_root = meta.workspace_root

        if not workspace_root:
            workspace_root = os.path.join(os.getcwd(), "temp", "workspaces", workspace_id)

        collab_dir = os.path.join(workspace_root, "docs", "collaborations")
        os.makedirs(collab_dir, exist_ok=True)

        file_path = os.path.join(collab_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return file_path

    def _get_audit_log_list(self, session_id: str) -> List[ReviewAuditLog]:
        if session_id not in self._audit_logs:
            self._audit_logs[session_id] = []
        return self._audit_logs[session_id]

    def _add_audit_log(
        self, session_id: str, action: ReviewAction, actor: str, details: str
    ) -> None:
        log_list = self._get_audit_log_list(session_id)
        log_id = f"log_{session_id}_{len(log_list) + 1}_{int(time.time())}"
        entry = ReviewAuditLog(
            log_id=log_id, action=action, actor=actor, details=details, timestamp=time.time()
        )
        log_list.append(entry)

        # Sync update inside the timeline as well
        timeline = self.get_timeline("", session_id)
        timeline.events.append(entry)

    def create_thread(
        self, workspace_id: str, session_id: str, comment: ReviewComment
    ) -> ReviewThread:
        if session_id not in self._threads:
            self._threads[session_id] = []

        thread_id = f"thr_{session_id}_{len(self._threads[session_id]) + 1}"
        thread = ReviewThread(thread_id=thread_id, root_comment=comment, resolution_state="open")
        self._threads[session_id].append(thread)

        self._add_audit_log(
            session_id=session_id,
            action=ReviewAction.CREATE,
            actor=comment.author,
            details=f"Created thread '{thread_id}' with root comment type '{comment.comment_type}'.",
        )
        return thread

    def reply_to_comment(
        self, workspace_id: str, thread_id: str, comment_id: str, reply: ReviewComment
    ) -> ReviewComment:
        parts = thread_id.split("_")
        session_id = "_".join(parts[1:-1]) if len(parts) > 2 else "default"
        threads = self.get_threads(workspace_id, session_id)

        target_thread = None
        for t in threads:
            if t.thread_id == thread_id:
                target_thread = t
                break

        if not target_thread:
            raise ValueError(f"Thread '{thread_id}' not found.")

        # Search for parent comment recursive utility
        def add_reply(curr_comment: ReviewComment) -> bool:
            if curr_comment.comment_id == comment_id:
                curr_comment.replies.append(reply)
                return True
            for r in curr_comment.replies:
                if add_reply(r):
                    return True
            return False

        success = add_reply(target_thread.root_comment)
        if not success:
            raise ValueError(
                f"Parent comment '{comment_id}' not found inside thread '{thread_id}'."
            )

        self._add_audit_log(
            session_id=session_id,
            action=ReviewAction.REPLY,
            actor=reply.author,
            details=f"Replied to comment '{comment_id}' inside thread '{thread_id}'.",
        )
        return reply

    def resolve_thread(self, workspace_id: str, thread_id: str, resolver: str) -> None:
        parts = thread_id.split("_")
        session_id = "_".join(parts[1:-1]) if len(parts) > 2 else "default"
        threads = self.get_threads(workspace_id, session_id)

        for t in threads:
            if t.thread_id == thread_id:
                t.resolution_state = "resolved"
                t.resolved_by = resolver
                t.resolved_at = time.time()
                t.root_comment.status = "resolved"
                break

        self._add_audit_log(
            session_id=session_id,
            action=ReviewAction.RESOLVE,
            actor=resolver,
            details=f"Resolved thread '{thread_id}'.",
        )

    def reopen_thread(self, workspace_id: str, thread_id: str, reopener: str) -> None:
        parts = thread_id.split("_")
        session_id = "_".join(parts[1:-1]) if len(parts) > 2 else "default"
        threads = self.get_threads(workspace_id, session_id)

        for t in threads:
            if t.thread_id == thread_id:
                t.resolution_state = "open"
                t.resolved_by = None
                t.resolved_at = None
                t.root_comment.status = "active"
                break

        self._add_audit_log(
            session_id=session_id,
            action=ReviewAction.REOPEN,
            actor=reopener,
            details=f"Reopened thread '{thread_id}'.",
        )

    def cast_vote(self, workspace_id: str, session_id: str, vote: ReviewVote) -> None:
        if session_id not in self._votes:
            self._votes[session_id] = []
        self._votes[session_id].append(vote)

        self._add_audit_log(
            session_id=session_id,
            action=ReviewAction.VOTE,
            actor=vote.voter_id,
            details=f"Cast vote '{vote.vote_value}' with rationale: {vote.rationale}",
        )

    def get_threads(self, workspace_id: str, session_id: str) -> List[ReviewThread]:
        return self._threads.get(session_id, [])

    def get_timeline(self, workspace_id: str, session_id: str) -> ReviewTimeline:
        if session_id not in self._timelines:
            self._timelines[session_id] = ReviewTimeline(
                timeline_id=f"timeline_{session_id}", events=[]
            )
        return self._timelines[session_id]

    def get_audit_log(self, workspace_id: str, session_id: str) -> List[ReviewAuditLog]:
        return self._get_audit_log_list(session_id)

    def store_collaboration_summary(self, workspace_id: str, session_id: str) -> None:
        threads = self.get_threads(workspace_id, session_id)
        votes = self._votes.get(session_id, [])

        open_threads_count = sum(1 for t in threads if t.resolution_state == "open")
        resolved_threads_count = len(threads) - open_threads_count

        vote_stats = {"approve": 0, "approve_with_conditions": 0, "request_changes": 0, "reject": 0}
        for v in votes:
            val = v.vote_value.lower()
            if val in vote_stats:
                vote_stats[val] += 1

        # Compile memory summary. Never store repository source code.
        content = (
            f"Review Collaboration Summary Logged\n"
            f"Workspace ID: {workspace_id}\n"
            f"Session ID: {session_id}\n"
            f"Discussion Status: Open Threads={open_threads_count}, Resolved Threads={resolved_threads_count}\n"
            f"Reviewer Votes: Approve={vote_stats['approve']}, Conditional Approve={vote_stats['approve_with_conditions']}, Request Changes={vote_stats['request_changes']}, Reject={vote_stats['reject']}\n"
            f"Timestamp: {time.ctime()}"
        )

        self._memory.add_memory(
            content=content,
            memory_type=MemoryType.PROJECT,
            tags=["collaboration_review", "reviewer_consensus", "audit_trail"],
            importance=2,
            metadata_additional={
                "session_id": session_id,
                "workspace_id": workspace_id,
                "open_threads": open_threads_count,
                "resolved_threads": resolved_threads_count,
                "vote_statistics": vote_stats,
            },
        )

    def compile_collaboration_report(
        self, workspace_id: str, session_id: str
    ) -> ReviewCollaborationReport:
        threads = self.get_threads(workspace_id, session_id)
        votes = self._votes.get(session_id, [])
        timeline = self.get_timeline(workspace_id, session_id)
        audit_log = self.get_audit_log(workspace_id, session_id)

        vote_summary = {
            "approve": 0,
            "approve_with_conditions": 0,
            "request_changes": 0,
            "reject": 0,
        }
        for v in votes:
            val = v.vote_value.lower()
            if val in vote_summary:
                vote_summary[val] += 1

        report = ReviewCollaborationReport(
            report_id=f"rep_collab_{session_id}",
            workspace_id=workspace_id,
            session_id=session_id,
            threads=threads,
            timeline=timeline,
            audit_log=audit_log,
            vote_summary=vote_summary,
            timestamp=time.time(),
        )

        # Refine consensus using model if active
        consensus = "No clear consensus recorded."
        if self._model and votes:
            try:
                votes_desc = "\n".join(
                    f"- Reviewer: {v.voter_id}, Vote: {v.vote_value}, Rationale: {v.rationale}"
                    for v in votes
                )
                prompt = (
                    "You are the Lead Quality Architect responsible for collaborative gates evaluations.\n"
                    f"Reviewer Votes details:\n{votes_desc}\n\n"
                    "Refine consensus summary text and list recommendations. Return refined consensus overview text only."
                )
                res = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output refined consensus details directly.",
                        task_category="testing",
                    )
                )
                refined = res.content.strip()
                if refined:
                    consensus = refined
            except Exception as e:
                logger.debug(f"LLM consensus summary refinement failed: {e}")

        # Save to workspace path ONLY
        threads_md = []
        for t in threads:
            status_tag = "[RESOLVED]" if t.resolution_state == "resolved" else "[OPEN]"
            linked_tag = (
                f" (Artifacts: {', '.join(t.root_comment.linked_artifacts)})"
                if t.root_comment.linked_artifacts
                else ""
            )
            threads_md.append(
                f"### {status_tag} Thread `{t.thread_id}`{linked_tag}\n"
                f"- **{t.root_comment.author}**: {t.root_comment.content}\n"
                + "\n".join(
                    f"  - **{rep.author}**: {rep.content}" for rep in t.root_comment.replies
                )
            )

        events_md = []
        for e in audit_log:
            events_md.append(
                f"- **{time.ctime(e.timestamp)}** [{e.action.value.upper()}] ({e.actor}): {e.details}"
            )

        report_md = (
            f"# Gate Review Collaboration Report\n\n"
            f"**Session ID**: `{session_id}`\n"
            f"**Workspace ID**: `{workspace_id}`\n\n"
            f"## Consensus Summary\n{consensus}\n\n"
            f"## Discussion Threads\n" + "\n\n".join(threads_md) + "\n\n"
            "## Audit Timeline History\n" + "\n".join(events_md)
        )
        self._write_to_workspace(workspace_id, f"COLLABORATION_REPORT_{session_id}.md", report_md)
        return report

    def publish_collaboration_report(self, report: ReviewCollaborationReport) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publishing.")
            return

        votes_md = "\n".join(f"- **{k.upper()}**: {v}" for k, v in report.vote_summary.items())
        report_md = (
            f"# Notion Sync - Gate Review Collaboration\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Session ID**: `{report.session_id}`\n"
            f"**Workspace ID**: `{report.workspace_id}`\n\n"
            f"## Reviewer Votes Summary\n{votes_md}\n\n"
            f"## Threads Overview\n"
            f"Active threads count: {len(report.threads)}\n"
            f"Events log entries: {len(report.audit_log)}"
        )

        doc = KnowledgeDocument(
            document_id=f"collab_report_{report.report_id}",
            title=f"Gate Collaboration - {report.report_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"collab_report_{report.report_id}",
                timestamp=report.timestamp,
                source_subsystem="review_collaboration_service",
                category="Project",
            ),
        )
        self._knowledge_hub.sync_document(doc, "notion")

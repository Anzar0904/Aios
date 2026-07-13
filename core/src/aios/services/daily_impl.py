import json
import logging
import time
from typing import Any, Dict, List, Optional

from aios.services.career import CareerOSService
from aios.services.daily import (
    DailyOSService,
    DailyPlan,
    DailyPlanner,
    DailyReview,
    DailyReviewSummary,
    DailySchedule,
    DailyTask,
    PriorityCalculator,
    ProductivityAnalyzer,
    ProgressTracker,
    ScheduleItem,
    ScheduleOptimizer,
    SessionRecorder,
    TaskPrioritizer,
    WorkloadEstimator,
    WorkSession,
)
from aios.services.github import GitHubService
from aios.services.model import LLMRequest, ModelService
from aios.services.personal import PersonalService
from aios.services.project_intelligence import ProjectIntelligenceService

logger = logging.getLogger(__name__)


class LocalPriorityCalculator(PriorityCalculator):
    def __init__(
        self,
        model_service: ModelService,
        personal_service: PersonalService,
        career_os: Optional[CareerOSService],
        registry: Any,
        project_intel: ProjectIntelligenceService,
    ) -> None:
        self._model = model_service
        self._personal = personal_service
        self._career_os = career_os
        self._registry = registry
        self._project_intel = project_intel

    def calculate_priority(self, task: DailyTask) -> str:
        # Gather active missions
        missions = []
        try:
            from aios.services.mission import MissionEngine

            mission_engine = self._registry.get(MissionEngine) if self._registry else None
            if mission_engine and hasattr(mission_engine, "_repository"):
                missions = [m.title for m in mission_engine._repository.list_missions()]
        except Exception:
            pass

        # Gather active applications/interviews
        apps = []
        if self._career_os:
            try:
                apps = [
                    f"{app.role} at {app.company} (Status: {app.status}, Date: {app.applied_date}, Interview: {app.interview_date})"
                    for app in self._career_os.application_tracker.list_applications()
                ]
            except Exception:
                pass

        # Gather project workspace telemetry
        workspace_info = {}
        try:
            context = self._project_intel.analyze_workspace(".")
            workspace_info = {
                "branch": context.git_branch,
                "todos_count": len(context.todo_markers),
                "commits_count": len(context.git_commits),
            }
        except Exception:
            pass

        prompt = (
            f"You are the Priority Calculator Engine. Analyze this task and decide its final priority (Critical, High, Medium, Low):\n\n"
            f"Task details:\n"
            f"- Title: {task.title}\n"
            f"- Effort hours: {task.effort_hours}\n"
            f"- Deadline: {task.deadline}\n"
            f"- Deadline Impact: {task.deadline_impact}\n"
            f"- Career Impact: {task.career_impact}\n"
            f"- Mission Impact: {task.mission_impact}\n"
            f"- Learning Impact: {task.learning_impact}\n\n"
            f"Context metrics:\n"
            f"- Active Missions: {missions}\n"
            f"- Job Applications/Interviews: {apps}\n"
            f"- Project/Workspace state: {workspace_info}\n\n"
            "Rules:\n"
            "- Critical priority must be reserved for tasks with immediate deadlines, close interviews, or direct blocker dependencies on active missions.\n"
            "- High priority is for active work or projects with high TODO counts/active repositories.\n"
            "- Output a JSON object (pure JSON, no markdown formatting) with key: priority"
        )

        res = self._model.execute_request(
            LLMRequest(
                prompt=prompt,
                system_instruction="Output pure JSON matching the schema.",
                task_category="reasoning",
                preferences={"JSON_output": True},
            )
        )

        try:
            content = res.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            data = json.loads(content)
            return data.get("priority", "Medium")
        except Exception:
            if task.deadline_impact == "Critical" or task.career_impact == "Critical":
                return "Critical"
            if task.deadline_impact == "High" or task.career_impact == "High":
                return "High"
            return "Medium"


class LocalWorkloadEstimator(WorkloadEstimator):
    def estimate_workload(self, tasks: List[DailyTask]) -> Dict[str, Any]:
        total_hours = sum(t.effort_hours for t in tasks if not t.completed)
        remaining_tasks = sum(1 for t in tasks if not t.completed)
        is_overloaded = total_hours > 8.0
        free_capacity = max(0.0, 8.0 - total_hours)

        return {
            "total_work_hours": total_hours,
            "remaining_work_count": remaining_tasks,
            "overloaded_schedule_detected": is_overloaded,
            "free_capacity_hours": free_capacity,
        }


class LocalScheduleOptimizer(ScheduleOptimizer):
    def __init__(self, model_service: ModelService) -> None:
        self._model = model_service

    def optimize_schedule(self, tasks: List[DailyTask]) -> DailySchedule:
        tasks_desc = [
            {
                "id": t.task_id,
                "title": t.title,
                "priority": t.priority,
                "effort_hours": t.effort_hours,
            }
            for t in tasks
        ]

        prompt = (
            f"You are the Calendar Schedule Optimizer. Sequence these tasks chronologically:\n\n"
            f"Tasks: {tasks_desc}\n\n"
            "Rules:\n"
            "- Sequence Critical and High priority tasks first.\n"
            "- Group similar tasks together to reduce context switching.\n"
            "- Limit scheduled tasks duration to a realistic workday (total 8 hours).\n"
            "- Automatically recommend 90-minute focus blocks separated by 15-minute breaks.\n"
            "Output as a JSON list of objects (pure JSON, no markdown formatting) with keys:\n"
            "- time_slot: (e.g. 09:00 - 10:30)\n"
            "- task_id: matching task ID or 'break'\n"
            "- task_title: task title or 'Break'\n"
            "- item_type: 'focus' or 'break'"
        )

        res = self._model.execute_request(
            LLMRequest(
                prompt=prompt,
                system_instruction="Output pure JSON list only.",
                task_category="reasoning",
                preferences={"JSON_output": True},
            )
        )

        try:
            content = res.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            data = json.loads(content)

            items = []
            for item in data:
                items.append(
                    ScheduleItem(
                        time_slot=item.get("time_slot", ""),
                        task_id=item.get("task_id", ""),
                        task_title=item.get("task_title", ""),
                        item_type=item.get("item_type", "focus"),
                    )
                )
            return DailySchedule(items=items)
        except Exception:
            items = []
            current_time = 9.0  # 09:00
            for t in sorted(
                tasks,
                key=lambda x: {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}.get(x.priority, 2),
            ):
                if t.completed:
                    continue
                start_h = int(current_time)
                start_m = int((current_time - start_h) * 60)
                end_time = current_time + t.effort_hours
                end_h = int(end_time)
                end_m = int((end_time - end_h) * 60)
                time_slot = f"{start_h:02d}:{start_m:02d} - {end_h:02d}:{end_m:02d}"
                items.append(
                    ScheduleItem(
                        time_slot=time_slot,
                        task_id=t.task_id,
                        task_title=t.title,
                        item_type="focus",
                    )
                )
                current_time = end_time
                # Add a break after each task
                items.append(
                    ScheduleItem(
                        time_slot=f"{end_h:02d}:{end_m:02d} - {end_h:02d}:{end_m + 15:02d}",
                        task_id="break",
                        task_title="Break",
                        item_type="break",
                    )
                )
                current_time += 0.25
            return DailySchedule(items=items)


class LocalTaskPrioritizer(TaskPrioritizer):
    def __init__(self, priority_calculator: PriorityCalculator) -> None:
        self._calculator = priority_calculator

    def prioritize_tasks(self, tasks: List[DailyTask]) -> List[DailyTask]:
        for t in tasks:
            t.priority = self._calculator.calculate_priority(t)
        return tasks


class LocalProgressTracker(ProgressTracker):
    def __init__(self, personal_service: PersonalService) -> None:
        self._personal = personal_service

    def _get_tasks(self) -> List[DailyTask]:
        profile = self._personal.get_active_profile()
        if not profile:
            return []
        for entry in profile.knowledge:
            if entry.id == "daily_tasks_list":
                try:
                    loaded = json.loads(entry.content)
                    return [
                        DailyTask(
                            task_id=t["task_id"],
                            title=t["title"],
                            priority=t["priority"],
                            effort_hours=t["effort_hours"],
                            deadline=t.get("deadline"),
                            completed=t.get("completed", False),
                            estimated_duration_mins=t.get("estimated_duration_mins", 60.0),
                            deadline_impact=t.get("deadline_impact", "Low"),
                            career_impact=t.get("career_impact", "Low"),
                            mission_impact=t.get("mission_impact", "Low"),
                            learning_impact=t.get("learning_impact", "Low"),
                            status=t.get("status", "Not Started"),
                            start_time=t.get("start_time"),
                            finish_time=t.get("finish_time"),
                            actual_duration_mins=t.get("actual_duration_mins", 0.0),
                            completion_percentage=t.get("completion_percentage", 0.0),
                        )
                        for t in loaded
                    ]
                except Exception:
                    return []
        return []

    def _save_tasks(self, tasks: List[DailyTask]) -> None:
        profile = self._personal.get_active_profile()
        if not profile:
            return
        serializable = [
            {
                "task_id": t.task_id,
                "title": t.title,
                "priority": t.priority,
                "effort_hours": t.effort_hours,
                "deadline": t.deadline,
                "completed": t.completed,
                "estimated_duration_mins": t.estimated_duration_mins,
                "deadline_impact": t.deadline_impact,
                "career_impact": t.career_impact,
                "mission_impact": t.mission_impact,
                "learning_impact": t.learning_impact,
                "status": t.status,
                "start_time": t.start_time,
                "finish_time": t.finish_time,
                "actual_duration_mins": t.actual_duration_mins,
                "completion_percentage": t.completion_percentage,
            }
            for t in tasks
        ]
        from aios.services.personal import KnowledgeEntry

        new_entry = KnowledgeEntry(
            id="daily_tasks_list",
            title="Daily Task Progress Cache",
            content=json.dumps(serializable),
            tags=["daily", "tasks"],
            updated_at=time.time(),
        )
        replaced = False
        for idx, entry in enumerate(profile.knowledge):
            if entry.id == "daily_tasks_list":
                profile.knowledge[idx] = new_entry
                replaced = True
                break
        if not replaced:
            profile.knowledge.append(new_entry)
        profile.version += 1
        self._personal.update_profile(profile.id, profile)

    def update_task_status(
        self, task_id: str, status: str, completion_percentage: float = 0.0
    ) -> DailyTask:
        tasks = self._get_tasks()
        target = None
        for t in tasks:
            if t.task_id == task_id:
                t.status = status
                if status == "In Progress" and not t.start_time:
                    t.start_time = time.time()
                elif status in ["Completed", "Cancelled"]:
                    t.finish_time = time.time()
                    t.completed = status == "Completed"
                    t.completion_percentage = 100.0
                    if t.start_time:
                        t.actual_duration_mins = (t.finish_time - t.start_time) / 60.0
                else:
                    t.completion_percentage = completion_percentage
                target = t
                break
        if target:
            self._save_tasks(tasks)
            return target
        raise ValueError(f"Task '{task_id}' not found.")

    def get_task(self, task_id: str) -> Optional[DailyTask]:
        tasks = self._get_tasks()
        for t in tasks:
            if t.task_id == task_id:
                return t
        return None

    def list_tasks(self) -> List[DailyTask]:
        return self._get_tasks()


class LocalSessionRecorder(SessionRecorder):
    def __init__(self, personal_service: PersonalService) -> None:
        self._personal = personal_service

    def _get_sessions(self) -> List[WorkSession]:
        profile = self._personal.get_active_profile()
        if not profile:
            return []
        for entry in profile.knowledge:
            if entry.id == "daily_work_sessions":
                try:
                    loaded = json.loads(entry.content)
                    return [
                        WorkSession(
                            session_id=s["session_id"],
                            start_time=s["start_time"],
                            end_time=s.get("end_time"),
                            duration_mins=s.get("duration_mins", 0.0),
                            task_id=s.get("task_id", ""),
                            mission_id=s.get("mission_id", ""),
                            category=s.get("category", ""),
                            notes=s.get("notes", ""),
                        )
                        for s in loaded
                    ]
                except Exception:
                    return []
        return []

    def _save_sessions(self, sessions: List[WorkSession]) -> None:
        profile = self._personal.get_active_profile()
        if not profile:
            return
        serializable = [
            {
                "session_id": s.session_id,
                "start_time": s.start_time,
                "end_time": s.end_time,
                "duration_mins": s.duration_mins,
                "task_id": s.task_id,
                "mission_id": s.mission_id,
                "category": s.category,
                "notes": s.notes,
            }
            for s in sessions
        ]
        from aios.services.personal import KnowledgeEntry

        new_entry = KnowledgeEntry(
            id="daily_work_sessions",
            title="Work Session Records",
            content=json.dumps(serializable),
            tags=["daily", "sessions"],
            updated_at=time.time(),
        )
        replaced = False
        for idx, entry in enumerate(profile.knowledge):
            if entry.id == "daily_work_sessions":
                profile.knowledge[idx] = new_entry
                replaced = True
                break
        if not replaced:
            profile.knowledge.append(new_entry)
        profile.version += 1
        self._personal.update_profile(profile.id, profile)

    def start_session(
        self, task_id: str, mission_id: str, category: str, notes: str
    ) -> WorkSession:
        sessions = self._get_sessions()
        session = WorkSession(
            session_id=f"work_session_{int(time.time())}",
            start_time=time.time(),
            task_id=task_id,
            mission_id=mission_id,
            category=category,
            notes=notes,
        )
        sessions.append(session)
        self._save_sessions(sessions)
        return session

    def end_session(self, session_id: str, notes: str) -> WorkSession:
        sessions = self._get_sessions()
        target = None
        for s in sessions:
            if s.session_id == session_id:
                s.end_time = time.time()
                s.duration_mins = (s.end_time - s.start_time) / 60.0
                s.notes = notes
                target = s
                break
        if target:
            self._save_sessions(sessions)
            return target
        raise ValueError(f"WorkSession '{session_id}' not found.")

    def list_sessions(self, task_id: Optional[str] = None) -> List[WorkSession]:
        sessions = self._get_sessions()
        if task_id:
            return [s for s in sessions if s.task_id == task_id]
        return sessions


class LocalDailyReview(DailyReview):
    def __init__(
        self,
        model_service: ModelService,
        personal_service: PersonalService,
        career_os: Optional[CareerOSService],
        registry: Any,
        project_intel: ProjectIntelligenceService,
        github_service: GitHubService,
    ) -> None:
        self._model = model_service
        self._personal = personal_service
        self._career_os = career_os
        self._registry = registry
        self._project_intel = project_intel
        self._github = github_service

    def generate_review(self) -> DailyReviewSummary:
        daily_os = self._registry.get(DailyOSService) if self._registry else None

        # Gather completed/incomplete tasks
        tasks = daily_os.progress_tracker.list_tasks() if daily_os else []
        completed = [t.title for t in tasks if t.completed]
        incomplete = [t.title for t in tasks if not t.completed]

        # Gather missions
        missions = []
        try:
            from aios.services.mission import MissionEngine

            mission_engine = self._registry.get(MissionEngine) if self._registry else None
            if mission_engine and hasattr(mission_engine, "_repository"):
                missions = [m.title for m in mission_engine._repository.list_missions()]
        except Exception:
            pass

        # Gather Career OS metrics
        career_activities = []
        if self._career_os:
            try:
                apps = self._career_os.application_tracker.list_applications()
                career_activities.append(f"Active applications count: {len(apps)}")
                plan = self._career_os.career_planner.generate_plan()
                career_activities.append(f"Active career milestones: {plan.get('milestones', [])}")
            except Exception:
                pass

        # Gather Project Intelligence telemetry
        project_activities = []
        try:
            context = self._project_intel.analyze_workspace(".")
            project_activities.append(f"Workspace TODO markers: {len(context.todo_markers)}")
            project_activities.append(f"Failing tests: {context.extra.get('failing_tests', 0)}")
            project_activities.append(f"Git Commits logged: {context.git_commits}")
        except Exception:
            pass

        prompt = (
            f"You are the Daily Review Engine. Summarize today's execution and build a development workflow review:\n\n"
            f"Completed Tasks: {completed}\n"
            f"Incomplete Tasks: {incomplete}\n"
            f"Active Missions: {missions}\n"
            f"Career/Milestones state: {career_activities}\n"
            f"Project code changes & TODOs: {project_activities}\n\n"
            "Produce an intelligent end-of-day summary detailing:\n"
            "- Completed tasks\n"
            "- Incomplete tasks\n"
            "- Mission progress summary\n"
            "- Career progress summary\n"
            "- Learning progress summary\n"
            "- Project activity summary\n"
            "- GitHub/Git activity summary\n"
            "- Overall productivity rating and summary\n"
            "- Tomorrow's priorities\n"
            "- Suggestions for improvement\n\n"
            "Output as a JSON object (pure JSON, no markdown formatting) with keys:\n"
            "- completed_tasks: list of strings\n"
            "- incomplete_tasks: list of strings\n"
            "- mission_progress: list of strings\n"
            "- career_progress: list of strings\n"
            "- learning_progress: list of strings\n"
            "- project_activity: list of strings\n"
            "- github_activity: list of strings\n"
            "- productivity_summary: string\n"
            "- tomorrow_priorities: list of strings\n"
            "- suggested_improvements: list of strings"
        )

        res = self._model.execute_request(
            LLMRequest(
                prompt=prompt,
                system_instruction="Output pure JSON only matching the schema.",
                task_category="reasoning",
                preferences={"JSON_output": True},
            )
        )

        try:
            content = res.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            data = json.loads(content)

            summary = DailyReviewSummary(
                completed_tasks=data.get("completed_tasks", completed),
                incomplete_tasks=data.get("incomplete_tasks", incomplete),
                mission_progress=data.get("mission_progress", []),
                career_progress=data.get("career_progress", []),
                learning_progress=data.get("learning_progress", []),
                project_activity=data.get("project_activity", []),
                github_activity=data.get("github_activity", []),
                productivity_summary=data.get("productivity_summary", "Review complete."),
                tomorrow_priorities=data.get("tomorrow_priorities", []),
                suggested_improvements=data.get("suggested_improvements", []),
            )

            # Persist summary inside Personal Profile knowledge for future memory retrieval
            self._persist_review(summary)
            return summary
        except Exception:
            summary = DailyReviewSummary(
                completed_tasks=completed,
                incomplete_tasks=incomplete,
                productivity_summary="Execution logged successfully.",
            )
            self._persist_review(summary)
            return summary

    def _persist_review(self, summary: DailyReviewSummary) -> None:
        profile = self._personal.get_active_profile()
        if not profile:
            return

        serializable = {
            "completed_tasks": summary.completed_tasks,
            "incomplete_tasks": summary.incomplete_tasks,
            "mission_progress": summary.mission_progress,
            "career_progress": summary.career_progress,
            "learning_progress": summary.learning_progress,
            "project_activity": summary.project_activity,
            "github_activity": summary.github_activity,
            "productivity_summary": summary.productivity_summary,
            "tomorrow_priorities": summary.tomorrow_priorities,
            "suggested_improvements": summary.suggested_improvements,
        }

        # Keep a list of reviews in the history profile database
        from aios.services.personal import KnowledgeEntry

        reviews_history = []
        for entry in profile.knowledge:
            if entry.id == "daily_reviews_history":
                try:
                    reviews_history = json.loads(entry.content)
                except Exception:
                    pass
                break

        reviews_history.append({"timestamp": time.time(), "review": serializable})
        new_entry = KnowledgeEntry(
            id="daily_reviews_history",
            title="Daily Reviews Archive",
            content=json.dumps(reviews_history),
            tags=["daily", "reviews"],
            updated_at=time.time(),
        )

        replaced = False
        for idx, entry in enumerate(profile.knowledge):
            if entry.id == "daily_reviews_history":
                profile.knowledge[idx] = new_entry
                replaced = True
                break
        if not replaced:
            profile.knowledge.append(new_entry)
        profile.version += 1
        self._personal.update_profile(profile.id, profile)

        # Synchronize with Knowledge Hub
        try:
            from aios.services.knowledge_hub import (
                KnowledgeDocument,
                KnowledgeHubService,
                KnowledgeMetadata,
            )

            knowledge_hub = self._registry.get(KnowledgeHubService) if self._registry else None
            if knowledge_hub:
                md_content = f"# Daily Review Summary\n\n## Productivity Summary\n{summary.productivity_summary}\n\n## Completed Tasks\n"
                for t in summary.completed_tasks:
                    md_content += f"- {t}\n"
                md_content += "\n## Incomplete Tasks\n"
                for t in summary.incomplete_tasks:
                    md_content += f"- {t}\n"

                doc = KnowledgeDocument(
                    document_id=f"daily_review_{int(time.time())}",
                    title=f"Daily Review - {time.strftime('%Y-%m-%d')}",
                    content=md_content,
                    metadata=KnowledgeMetadata(
                        unique_id=f"daily_review_{int(time.time())}",
                        timestamp=time.time(),
                        source_subsystem="daily_os",
                        category="Daily Review",
                    ),
                )
                knowledge_hub.sync_document(doc, "notion")
        except Exception as e:
            logger.error(f"Failed to sync daily review to Knowledge Hub: {e}")


class LocalProductivityAnalyzer(ProductivityAnalyzer):
    def __init__(self, personal_service: PersonalService, registry: Any) -> None:
        self._personal = personal_service
        self._registry = registry

    def analyze_productivity(self) -> Dict[str, Any]:
        daily_os = self._registry.get(DailyOSService) if self._registry else None

        tasks = daily_os.progress_tracker.list_tasks() if daily_os else []
        sessions = daily_os.session_recorder.list_sessions() if daily_os else []

        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.completed)
        completion_rate = (completed_tasks / total_tasks * 100.0) if total_tasks > 0 else 0.0

        focus_time = sum(s.duration_mins for s in sessions if s.category == "focus")
        interrupted_time = sum(s.duration_mins for s in sessions if s.category == "break")

        actual_durations = [
            t.actual_duration_mins for t in tasks if t.completed and t.actual_duration_mins > 0
        ]
        avg_duration = (sum(actual_durations) / len(actual_durations)) if actual_durations else 0.0

        # Estimated vs actual planning accuracy
        total_estimated = sum(t.estimated_duration_mins for t in tasks if t.completed)
        total_actual = sum(t.actual_duration_mins for t in tasks if t.completed)
        planning_accuracy = (total_estimated / total_actual * 100.0) if total_actual > 0 else 100.0

        metrics = {
            "completion_rate": completion_rate,
            "focus_time_mins": focus_time,
            "interrupted_time_mins": interrupted_time,
            "average_task_duration_mins": avg_duration,
            "planning_accuracy_percentage": planning_accuracy,
            "total_tasks_completed": completed_tasks,
            "recommendations": [
                "Good task completion rate.",
                "Ensure focus block sessions remain uninterrupted.",
            ],
        }

        # Persist metrics
        profile = self._personal.get_active_profile()
        if profile:
            from aios.services.personal import KnowledgeEntry

            metrics_history = []
            for entry in profile.knowledge:
                if entry.id == "daily_productivity_metrics":
                    try:
                        metrics_history = json.loads(entry.content)
                    except Exception:
                        pass
                    break
            metrics_history.append({"timestamp": time.time(), "metrics": metrics})
            new_entry = KnowledgeEntry(
                id="daily_productivity_metrics",
                title="Productivity Heuristics History",
                content=json.dumps(metrics_history),
                tags=["daily", "metrics"],
                updated_at=time.time(),
            )
            replaced = False
            for idx, entry in enumerate(profile.knowledge):
                if entry.id == "daily_productivity_metrics":
                    profile.knowledge[idx] = new_entry
                    replaced = True
                    break
            if not replaced:
                profile.knowledge.append(new_entry)
            profile.version += 1
            self._personal.update_profile(profile.id, profile)

        return metrics


class LocalDailyPlanner(DailyPlanner):
    def __init__(
        self,
        model_service: ModelService,
        personal_service: PersonalService,
        github_service: GitHubService,
        project_intel: ProjectIntelligenceService,
        career_os: Optional[CareerOSService],
        registry: Any,
    ) -> None:
        self._model = model_service
        self._personal = personal_service
        self._github = github_service
        self._project_intel = project_intel
        self._career_os = career_os
        self._registry = registry

    def plan_day(self) -> DailyPlan:
        # Retrieve memories dynamically based on objective
        try:
            from aios.services.memory import MemoryService, RetrievalContext, RetrievalStrategy

            memory_service = self._registry.get(MemoryService) if self._registry else None
            if memory_service:
                ctx = RetrievalContext(
                    objective="Determine tasks and milestones matching active missions and daily planning review",
                    strategy=RetrievalStrategy.MIXED,
                    max_results=3,
                )
                memory_service.retriever.retrieve(ctx)
        except Exception:
            pass

        # Gather active tasks and context
        profile = self._personal.get_active_profile()
        [g.title for g in profile.goals] if profile else []

        tasks = [
            DailyTask(
                task_id="task_1",
                title="Review active mission milestones",
                priority="Medium",
                effort_hours=1.5,
                deadline_impact="Medium",
                career_impact="Medium",
                mission_impact="High",
            ),
            DailyTask(
                task_id="task_2",
                title="Prepare software engineer interview prep questions",
                priority="Medium",
                effort_hours=2.0,
                deadline_impact="High",
                career_impact="High",
                learning_impact="High",
            ),
            DailyTask(
                task_id="task_3",
                title="Audit repository open TODO markers and doc gaps",
                priority="Medium",
                effort_hours=1.0,
                deadline_impact="Low",
                career_impact="Low",
                mission_impact="Medium",
            ),
        ]

        # Prioritize tasks
        daily_os_svc = self._registry.get(DailyOSService) if self._registry else None
        if daily_os_svc:
            # Sync initial task list inside cache
            try:
                cached_tasks = daily_os_svc.progress_tracker.list_tasks()
                if not cached_tasks:
                    daily_os_svc.progress_tracker._save_tasks(tasks)
                    cached_tasks = tasks
                prioritized = daily_os_svc.prioritizer.prioritize_tasks(cached_tasks)
                daily_os_svc.progress_tracker._save_tasks(prioritized)
            except Exception:
                prioritized = tasks

            workload = daily_os_svc.workload_estimator.estimate_workload(prioritized)
            schedule = daily_os_svc.schedule_optimizer.optimize_schedule(prioritized)
            sessions = daily_os_svc.session_recorder.list_sessions()
            try:
                review = daily_os_svc.daily_review.generate_review()
            except Exception:
                review = None
        else:
            prioritized = tasks
            workload = {"total_work_hours": 4.5}
            schedule = DailySchedule()
            sessions = []
            review = None

        return DailyPlan(
            date="2026-07-04",
            tasks=prioritized,
            schedule=schedule,
            workload_summary=workload,
            sessions=sessions,
            review=review,
        )


class LocalDailyOSService(DailyOSService):
    """Unified service implementation coordinating all Daily OS modules."""

    def __init__(
        self,
        model_service: ModelService,
        personal_service: PersonalService,
        github_service: GitHubService,
        project_intel: ProjectIntelligenceService,
        career_os: Optional[CareerOSService] = None,
        registry: Any = None,
    ) -> None:
        self._model = model_service
        self._personal = personal_service
        self._github = github_service
        self._project_intel = project_intel
        self._career_os = career_os
        self._registry = registry

        # Instantiate subcomponents
        self._priority_calculator = LocalPriorityCalculator(
            model_service, personal_service, career_os, registry, project_intel
        )
        self._workload_estimator = LocalWorkloadEstimator()
        self._schedule_optimizer = LocalScheduleOptimizer(model_service)
        self._prioritizer = LocalTaskPrioritizer(self._priority_calculator)

        self._progress_tracker = LocalProgressTracker(personal_service)
        self._session_recorder = LocalSessionRecorder(personal_service)
        self._daily_review = LocalDailyReview(
            model_service, personal_service, career_os, registry, project_intel, github_service
        )
        self._productivity_analyzer = LocalProductivityAnalyzer(personal_service, registry)

        self._planner = LocalDailyPlanner(
            model_service, personal_service, github_service, project_intel, career_os, registry
        )

    def initialize(self) -> None:
        logger.info("Initializing LocalDailyOSService")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    @property
    def planner(self) -> DailyPlanner:
        return self._planner

    @property
    def prioritizer(self) -> TaskPrioritizer:
        return self._prioritizer

    @property
    def priority_calculator(self) -> PriorityCalculator:
        return self._priority_calculator

    @property
    def workload_estimator(self) -> WorkloadEstimator:
        return self._workload_estimator

    @property
    def schedule_optimizer(self) -> ScheduleOptimizer:
        return self._schedule_optimizer

    @property
    def progress_tracker(self) -> ProgressTracker:
        return self._progress_tracker

    @property
    def session_recorder(self) -> SessionRecorder:
        return self._session_recorder

    @property
    def daily_review(self) -> DailyReview:
        return self._daily_review

    @property
    def productivity_analyzer(self) -> ProductivityAnalyzer:
        return self._productivity_analyzer

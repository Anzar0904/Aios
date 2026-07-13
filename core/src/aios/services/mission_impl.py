import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from aios.services.agent import AgentRuntimeService
from aios.services.intent import Intent, IntentType
from aios.services.mission import (
    Mission,
    MissionContext,
    MissionEngine,
    MissionExecutor,
    MissionMilestone,
    MissionPlanner,
    MissionRepository,
    MissionStatus,
    MissionTask,
)

logger = logging.getLogger(__name__)


class LocalMissionPlanner(MissionPlanner):
    def plan_mission(self, objective: str, context: MissionContext) -> Mission:
        obj_lower = objective.lower()
        mission_id = f"mission_{int(time.time())}"

        # 1. Career Mission Planning
        if any(kw in obj_lower for kw in ("internship", "job", "career")):
            milestones = [
                MissionMilestone(
                    milestone_id="m1-research",
                    name="Identify target AI internships today",
                    tasks=[
                        MissionTask("t1-search", "Find opportunities", "career_agent")
                    ]
                ),
                MissionMilestone(
                    milestone_id="m2-optimize",
                    name="Resume tailored optimization analysis",
                    tasks=[
                        MissionTask("t2-ats", "ATS Scoring & suggestions", "career_agent")
                    ]
                ),
                MissionMilestone(
                    milestone_id="m3-application",
                    name="Draft custom application cover letters",
                    tasks=[
                        MissionTask("t3-letter", "Generate tailored letter", "career_agent")
                    ]
                )
            ]
            return Mission(
                mission_id=mission_id,
                title="Career Internship Acquisition",
                objective=objective,
                milestones=milestones
            )

        # 2. Learning Mission Planning
        elif any(kw in obj_lower for kw in ("kubernetes", "learn", "study")):
            milestones = [
                MissionMilestone(
                    milestone_id="m1-syllabus",
                    name="Research core K8s production topics",
                    tasks=[
                        MissionTask("t1-syllabus", "Generate learning syllabus", "career_agent")
                    ]
                ),
                MissionMilestone(
                    milestone_id="m2-schedule",
                    name="Establish weekly study goals",
                    tasks=[
                        MissionTask("t2-schedule", "Build weekly plan", "career_agent")
                    ]
                )
            ]
            return Mission(
                mission_id=mission_id,
                title="Production Kubernetes Certification",
                objective=objective,
                milestones=milestones
            )

        # 3. Project Mission Planning (Default)
        else:
            milestones = [
                MissionMilestone(
                    milestone_id="m1-audit",
                    name="Analyze active repository and workspace structure",
                    tasks=[
                        MissionTask("t1-workspace", "Get Git status and stats", "developer_agent")
                    ]
                ),
                MissionMilestone(
                    milestone_id="m2-refactor",
                    name="Build safe automation scripts",
                    tasks=[
                        MissionTask("t2-workflow", "Generate n8n compiler flow", "developer_agent")
                    ]
                )
            ]
            return Mission(
                mission_id=mission_id,
                title="Personal AI OS Core Roadmap",
                objective=objective,
                milestones=milestones
            )


class LocalMissionExecutor(MissionExecutor):
    def __init__(self, agent_runtime: AgentRuntimeService) -> None:
        self._runtime = agent_runtime
        self._cancelled_missions = set()

    def cancel(self, mission_id: str) -> None:
        self._cancelled_missions.add(mission_id)

    def execute_mission(self, mission: Mission, context: MissionContext) -> bool:
        logger.info(f"Executing mission '{mission.mission_id}'...")
        mission.status = MissionStatus.RUNNING

        # Process milestones sequentially
        for i in range(mission.current_milestone_index, len(mission.milestones)):
            if mission.mission_id in self._cancelled_missions:
                mission.status = MissionStatus.CANCELLED
                logger.info(f"Mission '{mission.mission_id}' execution cancelled.")
                return False

            mission.current_milestone_index = i
            milestone = mission.milestones[i]
            milestone.status = MissionStatus.RUNNING
            logger.info(f"Starting milestone: {milestone.name}")

            # Run tasks in milestone
            for task in milestone.tasks:
                if mission.mission_id in self._cancelled_missions:
                    milestone.status = MissionStatus.CANCELLED
                    mission.status = MissionStatus.CANCELLED
                    return False

                task.status = MissionStatus.RUNNING

                # Compose Intent to dispatch to Agent Runtime
                intent = Intent(
                    intent_type=IntentType.CAREER if "career" in task.assigned_agent else IntentType.DEVELOPER,
                    action=task.name,
                    parameters={"objective": mission.objective},
                    target_service=task.assigned_agent,
                    confidence=1.0
                )

                try:
                    result = self._runtime.execute(intent)
                    if result.success:
                        task.status = MissionStatus.COMPLETED
                        task.result = result.response
                    else:
                        task.status = MissionStatus.FAILED
                        task.result = result.response
                        milestone.status = MissionStatus.FAILED
                        mission.status = MissionStatus.FAILED
                        return False
                except Exception as e:
                    task.status = MissionStatus.FAILED
                    task.result = str(e)
                    milestone.status = MissionStatus.FAILED
                    mission.status = MissionStatus.FAILED
                    return False

            milestone.status = MissionStatus.COMPLETED

        mission.status = MissionStatus.COMPLETED
        logger.info(f"Mission '{mission.mission_id}' successfully completed.")
        return True


class LocalMissionRepository(MissionRepository):
    def __init__(self, cache_filename: str = "missions.json", workspace_root: str = ".") -> None:
        self._cache_filename = cache_filename
        self._workspace_root = workspace_root
        self._missions: Dict[str, Mission] = {}

    def initialize(self) -> None:
        cache_path = Path(self._workspace_root) / self._cache_filename
        if cache_path.is_file():
            try:
                data = json.loads(cache_path.read_text(encoding="utf-8"))
                for mid, mdata in data.items():
                    self._missions[mid] = self._deserialize_mission(mdata)
            except Exception:
                pass

    def save_mission(self, mission: Mission) -> None:
        self._missions[mission.mission_id] = mission
        self._save_cache()

    def load_mission(self, mission_id: str) -> Optional[Mission]:
        return self._missions.get(mission_id)

    def list_missions(self) -> List[Mission]:
        return list(self._missions.values())

    def _save_cache(self) -> None:
        cache_path = Path(self._workspace_root) / self._cache_filename
        serialized = {mid: self._serialize_mission(m) for mid, m in self._missions.items()}
        try:
            cache_path.write_text(json.dumps(serialized, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _serialize_mission(self, m: Mission) -> Dict[str, Any]:
        return {
            "mission_id": m.mission_id,
            "title": m.title,
            "objective": m.objective,
            "status": m.status.name,
            "current_milestone_index": m.current_milestone_index,
            "milestones": [
                {
                    "milestone_id": ms.milestone_id,
                    "name": ms.name,
                    "status": ms.status.name,
                    "tasks": [
                        {
                            "task_id": t.task_id,
                            "name": t.name,
                            "assigned_agent": t.assigned_agent,
                            "status": t.status.name,
                            "result": t.result
                        }
                        for t in ms.tasks
                    ]
                }
                for ms in m.milestones
            ]
        }

    def _deserialize_mission(self, data: Dict[str, Any]) -> Mission:
        milestones = []
        for ms_data in data.get("milestones", []):
            tasks = []
            for t_data in ms_data.get("tasks", []):
                tasks.append(
                    MissionTask(
                        task_id=t_data["task_id"],
                        name=t_data["name"],
                        assigned_agent=t_data["assigned_agent"],
                        status=MissionStatus[t_data["status"]],
                        result=t_data.get("result")
                    )
                )
            milestones.append(
                MissionMilestone(
                    milestone_id=ms_data["milestone_id"],
                    name=ms_data["name"],
                    tasks=tasks,
                    status=MissionStatus[ms_data["status"]]
                )
            )

        return Mission(
            mission_id=data["mission_id"],
            title=data["title"],
            objective=data["objective"],
            milestones=milestones,
            status=MissionStatus[data["status"]],
            current_milestone_index=data.get("current_milestone_index", 0)
        )


class LocalMissionEngine(MissionEngine):
    def __init__(self, agent_runtime: AgentRuntimeService, workspace_root: str = ".", registry: Optional[Any] = None) -> None:
        self._planner = LocalMissionPlanner()
        self._executor = LocalMissionExecutor(agent_runtime)
        self._repository = LocalMissionRepository(workspace_root=workspace_root)
        self._registry = registry

    def initialize(self) -> None:
        self._repository.initialize()

    def create_mission(self, title: str, objective: str) -> Mission:
        ctx = MissionContext()
        mission = self._planner.plan_mission(objective, ctx)
        if title:
            mission.title = title
        self._repository.save_mission(mission)
        return mission

    def start_mission(self, mission_id: str) -> bool:
        mission = self._repository.load_mission(mission_id)
        if not mission:
            return False
        ctx = MissionContext()
        success = self._executor.execute_mission(mission, ctx)
        self._repository.save_mission(mission)

        # Synchronize with Knowledge Hub on completion
        if success:
            try:
                from aios.services.knowledge_hub import (
                    KnowledgeDocument,
                    KnowledgeHubService,
                    KnowledgeMetadata,
                )
                knowledge_hub = self._registry.get(KnowledgeHubService) if self._registry else None
                if knowledge_hub:
                    md_content = f"# Mission Summary: {mission.title}\n\n## Objective\n{mission.objective}\n\n## Milestones\n"
                    for ms in mission.milestones:
                        md_content += f"### Milestone: {ms.name} ({ms.status.name})\n"
                        for t in ms.tasks:
                            md_content += f"- Task: {t.name} (Assigned: {t.assigned_agent}, Status: {t.status.name})\n"

                    doc = KnowledgeDocument(
                        document_id=f"mission_{mission.mission_id}",
                        title=f"Mission - {mission.title}",
                        content=md_content,
                        metadata=KnowledgeMetadata(
                            unique_id=f"mission_{mission.mission_id}",
                            timestamp=time.time(),
                            source_subsystem="mission_engine",
                            category="Mission"
                        )
                    )
                    knowledge_hub.sync_document(doc, "notion")
            except Exception:
                pass

        return success

    def cancel_mission(self, mission_id: str) -> bool:
        mission = self._repository.load_mission(mission_id)
        if not mission:
            return False
        self._executor.cancel(mission_id)
        mission.status = MissionStatus.CANCELLED
        self._repository.save_mission(mission)
        return True

    def get_mission(self, mission_id: str) -> Optional[Mission]:
        return self._repository.load_mission(mission_id)

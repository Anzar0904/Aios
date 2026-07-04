import json
import logging
import time
import uuid
from typing import Any, Dict, List, Optional

from aios.services.context import ContextLoadedEvent
from aios.services.event_bus import EventBusService
from aios.services.model import ModelService, LLMRequest
from aios.services.memory import (
    Memory,
    MemoryMetadata,
    MemoryService,
    MemoryType,
    MemoryCategory,
    MemoryImportance,
    MemoryReference,
    MemoryClassifier,
    MemoryIndexer,
    RetrievalContext,
    RetrievalStrategy,
    MemoryFilter,
    MemorySelector,
    MemoryRetriever,
)
from aios.services.memory_storage import MemoryStorage
from aios.services.memory_storage_impl import LocalJSONMemoryStorage
from aios.services.session import SessionEndedEvent, SessionStartedEvent

logger = logging.getLogger(__name__)


class LocalMemoryClassifier(MemoryClassifier):
    def __init__(self, memory_service: "LocalMemoryService") -> None:
        self._service = memory_service

    def classify_memory(self, content: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        content_lower = content.lower()

        category = MemoryCategory.PERSONAL
        if "daily review" in content_lower or "productivity rating" in content_lower:
            category = MemoryCategory.DAILY_REVIEW
        elif "git" in content_lower or "github" in content_lower or "commit" in content_lower or "pull request" in content_lower:
            category = MemoryCategory.GITHUB
        elif "interview" in content_lower or "job application" in content_lower or "resume" in content_lower or "career" in content_lower:
            category = MemoryCategory.CAREER
        elif "mission" in content_lower or "milestone" in content_lower or "objective" in content_lower:
            category = MemoryCategory.MISSION
        elif "research" in content_lower or "paper" in content_lower or "literature" in content_lower:
            category = MemoryCategory.RESEARCH
        elif "learning" in content_lower or "course" in content_lower or "tutorial" in content_lower or "study" in content_lower:
            category = MemoryCategory.LEARNING
        elif "workflow" in content_lower or "pipeline" in content_lower or "automation" in content_lower:
            category = MemoryCategory.WORKFLOW
        elif "project" in content_lower or "workspace" in content_lower or "repository" in content_lower:
            category = MemoryCategory.PROJECT
        elif "conversation" in content_lower or "chat" in content_lower or "dialogue" in content_lower:
            category = MemoryCategory.CONVERSATION

        importance = MemoryImportance.MEDIUM
        if any(w in content_lower for w in ["critical", "blocker", "emergency", "failing"]):
            importance = MemoryImportance.CRITICAL
        elif any(w in content_lower for w in ["high", "important", "urgent", "milestone"]):
            importance = MemoryImportance.HIGH
        elif any(w in content_lower for w in ["low", "trivial", "minor"]):
            importance = MemoryImportance.LOW

        tags = []
        if category != MemoryCategory.PERSONAL:
            tags.append(category.value.lower())
        if importance != MemoryImportance.MEDIUM:
            tags.append(importance.value.lower())

        fallback_result = {
            "category": category,
            "importance_score": importance,
            "tags": tags,
            "related_mission": None,
            "related_project": None,
            "related_company": None,
            "related_technologies": [],
            "related_skills": [],
            "related_files": [],
        }

        model_service = self._service.model_service
        if not model_service:
            return fallback_result

        prompt = (
            f"You are the Memory Classification Engine. Analyze this memory content:\n\n"
            f"Content: {content}\n\n"
            "Classify it into one of these Categories: Conversation, Daily Review, Career, Project, GitHub, Research, Mission, Learning, Workflow, Personal.\n"
            "Determine the Importance Score: Low, Medium, High, Critical.\n"
            "Extract tags, related missions, related projects, related companies, technologies, skills, and files.\n"
            "Output as a JSON object (pure JSON, no markdown formatting) with keys:\n"
            "- category: (string)\n"
            "- importance_score: (string)\n"
            "- tags: list of strings\n"
            "- related_mission: Optional string\n"
            "- related_project: Optional string\n"
            "- related_company: Optional string\n"
            "- related_technologies: list of strings\n"
            "- related_skills: list of strings\n"
            "- related_files: list of strings"
        )

        try:
            res = model_service.execute_request(
                LLMRequest(
                    prompt=prompt,
                    system_instruction="Output pure JSON matching the schema.",
                    task_category="reasoning",
                    preferences={"JSON_output": True},
                )
            )
            content_str = res.content.strip()
            if content_str.startswith("```"):
                content_str = content_str.split("```")[1]
                if content_str.startswith("json"):
                    content_str = content_str[4:]
            data = json.loads(content_str)

            cat_str = data.get("category", "")
            final_cat = category
            for m_cat in MemoryCategory:
                if m_cat.value.lower() == cat_str.lower() or m_cat.name.lower() == cat_str.lower():
                    final_cat = m_cat
                    break

            imp_str = data.get("importance_score", "")
            final_imp = importance
            for m_imp in MemoryImportance:
                if m_imp.value.lower() == imp_str.lower() or m_imp.name.lower() == imp_str.lower():
                    final_imp = m_imp
                    break

            return {
                "category": final_cat,
                "importance_score": final_imp,
                "tags": list(set(tags + data.get("tags", []))),
                "related_mission": data.get("related_mission"),
                "related_project": data.get("related_project"),
                "related_company": data.get("related_company"),
                "related_technologies": data.get("related_technologies", []),
                "related_skills": data.get("related_skills", []),
                "related_files": data.get("related_files", []),
            }
        except Exception:
            return fallback_result


class LocalMemoryIndexer(MemoryIndexer):
    def __init__(self, memory_service: "LocalMemoryService") -> None:
        self._service = memory_service

    def index_memory(self, memory: Memory) -> None:
        pass

    def deindex_memory(self, memory_id: str) -> None:
        pass

    def lookup(
        self,
        category: Optional[MemoryCategory] = None,
        tags: Optional[List[str]] = None,
        mission: Optional[str] = None,
        project: Optional[str] = None,
        company: Optional[str] = None,
        technology: Optional[str] = None,
        start_date: Optional[float] = None,
        end_date: Optional[float] = None,
    ) -> List[Memory]:
        results = []
        for memory in self._service._memories.values():
            meta = memory.metadata

            if category is not None and meta.category != category:
                continue

            if tags is not None:
                if not all(tag in meta.tags for tag in tags):
                    continue

            if mission is not None and meta.related_mission != mission:
                continue

            if project is not None and meta.related_project != project:
                continue

            if company is not None and meta.related_company != company:
                continue

            if technology is not None:
                if not any(technology.lower() in tech.lower() for tech in meta.related_technologies):
                    continue

            if start_date is not None and meta.timestamp < start_date:
                continue

            if end_date is not None and meta.timestamp > end_date:
                continue

            results.append(memory)
        return results


class LocalMemoryFilter(MemoryFilter):
    def filter_memories(self, memories: List[Memory], context: RetrievalContext) -> List[Memory]:
        results = []
        for m in memories:
            meta = m.metadata

            # Active mission constraint
            if context.active_mission and meta.related_mission != context.active_mission:
                continue

            # Active project constraint
            if context.active_project and meta.related_project != context.active_project:
                continue

            results.append(m)
        return results


class LocalMemorySelector(MemorySelector):
    def select_memories(self, memories: List[Memory], context: RetrievalContext) -> List[Memory]:
        # Sort by importance and recency
        def sort_key(m: Memory):
            imp_val = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}.get(
                m.metadata.importance_score.value if m.metadata.importance_score else "", 2
            )
            return (imp_val, m.created_at)

        ordered = sorted(memories, key=sort_key, reverse=True)

        # Avoid prompt inflation
        selected = []
        current_bytes = 0
        for m in ordered:
            m_len = len(m.content.encode("utf-8"))
            if current_bytes + m_len <= context.limit_bytes:
                selected.append(m)
                current_bytes += m_len
            if len(selected) >= context.max_results:
                break
        return selected


class LocalMemoryRetriever(MemoryRetriever):
    def __init__(
        self,
        memory_service: "LocalMemoryService",
        filter_component: MemoryFilter,
        selector_component: MemorySelector,
    ) -> None:
        self._service = memory_service
        self._filter = filter_component
        self._selector = selector_component

    def retrieve(self, context: RetrievalContext) -> List[Memory]:
        objective_lower = context.objective.lower()

        category_filter = None
        company_filter = None
        project_filter = context.active_project
        mission_filter = context.active_mission
        technology_filter = None
        tags_filter = None

        if context.strategy != RetrievalStrategy.MIXED:
            if context.strategy == RetrievalStrategy.MISSION:
                category_filter = MemoryCategory.MISSION
            elif context.strategy == RetrievalStrategy.CAREER:
                category_filter = MemoryCategory.CAREER
            elif context.strategy == RetrievalStrategy.PROJECT:
                category_filter = MemoryCategory.PROJECT
            elif context.strategy == RetrievalStrategy.LEARNING:
                category_filter = MemoryCategory.LEARNING

            if "google" in objective_lower:
                company_filter = "Google"
            if "resume" in objective_lower or "interview" in objective_lower or "applying" in objective_lower:
                category_filter = MemoryCategory.CAREER
            if "daily planning" in objective_lower or "yesterday" in objective_lower:
                category_filter = MemoryCategory.DAILY_REVIEW


        # Index lookup
        candidates = self._service.indexer.lookup(
            category=category_filter,
            tags=tags_filter,
            mission=mission_filter,
            project=project_filter,
            company=company_filter,
            technology=technology_filter,
        )

        filtered = self._filter.filter_memories(candidates, context)
        return self._selector.select_memories(filtered, context)


class LocalMemoryService(MemoryService):
    """Concrete implementation of MemoryService utilizing a configurable local storage backend."""

    def __init__(self, event_bus: EventBusService, storage: Optional[MemoryStorage] = None) -> None:
        self._event_bus = event_bus
        self._workspace_id: Optional[str] = None
        self._session_id: Optional[str] = None
        self._model_service: Optional[ModelService] = None

        if storage is None:
            self._storage: MemoryStorage = LocalJSONMemoryStorage()
        else:
            self._storage = storage

        self._memories: Dict[str, Memory] = {}
        self._classifier = LocalMemoryClassifier(self)
        self._indexer = LocalMemoryIndexer(self)
        self._filter = LocalMemoryFilter()
        self._selector = LocalMemorySelector()
        self._retriever = LocalMemoryRetriever(self, self._filter, self._selector)

    def set_model_service(self, model_service: ModelService) -> None:
        self._model_service = model_service

    @property
    def model_service(self) -> Optional[ModelService]:
        return self._model_service

    @property
    def classifier(self) -> MemoryClassifier:
        return self._classifier

    @property
    def indexer(self) -> MemoryIndexer:
        return self._indexer

    @property
    def retriever(self) -> MemoryRetriever:
        return self._retriever

    def initialize(self) -> None:
        logger.info("Initializing LocalMemoryService")
        self._event_bus.subscribe(ContextLoadedEvent, self._on_context_loaded)
        self._event_bus.subscribe(SessionStartedEvent, self._on_session_started)
        self._event_bus.subscribe(SessionEndedEvent, self._on_session_ended)

    def _on_context_loaded(self, event: ContextLoadedEvent) -> None:
        self._workspace_id = event.context.project_root
        logger.info(f"MemoryService context loaded for workspace: {self._workspace_id}")

    def _on_session_started(self, event: SessionStartedEvent) -> None:
        self._session_id = event.session_id
        workspace_id = event.session.workspace_id
        self._workspace_id = workspace_id

        loaded = self.load_workspace_memory(workspace_id)
        print(f"[MemoryService] Restored {len(loaded)} memories for workspace: {workspace_id}")

    def _on_session_ended(self, event: SessionEndedEvent) -> None:
        self.commit()
        print(f"[MemoryService] Committed memories for workspace: {self._workspace_id}")
        self._session_id = None

    def add_memory(
        self,
        content: str,
        memory_type: MemoryType,
        tags: List[str] = None,
        importance: int = 1,
        metadata_additional: Dict[str, Any] = None,
    ) -> Memory:
        if metadata_additional is None:
            metadata_additional = {}
        if tags is None:
            tags = []
        if self._workspace_id is None:
            raise RuntimeError("Cannot add memory: no active workspace context")

        session_id = self._session_id if self._session_id else "system"
        memory_id = str(uuid.uuid4())
        now = time.time()

        classification = self._classifier.classify_memory(content)

        seen = set()
        combined_tags = []
        for t in (tags + classification["tags"]):
            if t not in seen:
                seen.add(t)
                combined_tags.append(t)

        metadata = MemoryMetadata(
            workspace_id=self._workspace_id,
            session_id=session_id,
            tags=combined_tags,
            importance=importance,
            additional=metadata_additional,
            unique_id=memory_id,
            timestamp=now,
            source_subsystem="daily_os" if "daily" in content.lower() else "personal_intelligence",
            category=classification["category"],
            importance_score=classification["importance_score"],
            related_mission=classification["related_mission"],
            related_project=classification["related_project"],
            related_company=classification["related_company"],
            related_technologies=classification["related_technologies"],
            related_skills=classification["related_skills"],
            related_files=classification["related_files"],
        )

        memory = Memory(
            memory_id=memory_id,
            content=content,
            memory_type=memory_type,
            metadata=metadata,
            created_at=now,
            updated_at=now,
        )

        self._memories[memory_id] = memory
        self._storage.save_memory(memory)
        return memory

    def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        tags: Optional[List[str]] = None,
        importance: Optional[int] = None,
        metadata_additional: Optional[Dict[str, Any]] = None,
    ) -> Memory:
        memory = self.get_memory(memory_id)
        if memory is None:
            raise KeyError(f"Memory with ID {memory_id} not found")

        if content is not None:
            memory.content = content
            classification = self._classifier.classify_memory(content)
            memory.metadata.category = classification["category"]
            memory.metadata.importance_score = classification["importance_score"]
            memory.metadata.related_mission = classification["related_mission"]
            memory.metadata.related_project = classification["related_project"]
            memory.metadata.related_company = classification["related_company"]
            memory.metadata.related_technologies = classification["related_technologies"]
            memory.metadata.related_skills = classification["related_skills"]
            memory.metadata.related_files = classification["related_files"]

            seen_u = set()
            combined_tags_u = []
            for t in ((tags or memory.metadata.tags) + classification["tags"]):
                if t not in seen_u:
                    seen_u.add(t)
                    combined_tags_u.append(t)
            memory.metadata.tags = combined_tags_u
        else:
            if tags is not None:
                memory.metadata.tags = tags

        if importance is not None:
            memory.metadata.importance = importance
        if metadata_additional is not None:
            memory.metadata.additional.update(metadata_additional)

        memory.updated_at = time.time()
        self._storage.save_memory(memory)
        return memory

    def delete_memory(self, memory_id: str) -> None:
        if memory_id in self._memories:
            del self._memories[memory_id]
        self._storage.delete_memory(memory_id)

    def search_memory(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Memory]:
        results = []
        for memory in self._memories.values():
            if query.lower() not in memory.content.lower():
                continue
            if memory_type is not None and memory.memory_type != memory_type:
                continue
            if tags is not None:
                if not all(tag in memory.metadata.tags for tag in tags):
                    continue
            results.append(memory)
        return results

    def get_memory(self, memory_id: str) -> Optional[Memory]:
        if memory_id in self._memories:
            return self._memories[memory_id]
        return self._storage.get_memory(memory_id)

    def load_workspace_memory(self, workspace_id: str) -> List[Memory]:
        all_memories = self._storage.load_all_memories()
        workspace_memories = [m for m in all_memories if m.metadata.workspace_id == workspace_id]
        self._memories = {m.memory_id: m for m in workspace_memories}
        return workspace_memories

    def commit(self) -> None:
        self._storage.commit()

    # Existing backward-compatibility interface methods
    def restore_memory(self, context: dict) -> None:
        workspace_id = context.get("project_root") or context.get("working_directory")
        if workspace_id:
            self._workspace_id = workspace_id
            self.load_workspace_memory(workspace_id)

    def observe_event(self, event: dict) -> None:
        pass

    def commit_memory(self) -> None:
        self.commit()

    def prune_memory(self) -> None:
        pass

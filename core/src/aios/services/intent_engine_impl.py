import json
import logging
import time
from typing import Any, Dict, List, Optional

from aios.services.intent_engine import (
    IntentAnalyzer,
    IntentClassifier,
    IntentContext,
    IntentEngine,
    IntentPlan,
    IntentResolver,
    IntentResult,
)
from aios.services.memory import MemoryService, RetrievalContext
from aios.services.model import LLMRequest, ModelService
from aios.services.reasoning import ReasoningContext, ReasoningService

logger = logging.getLogger(__name__)


class LocalIntentClassifier(IntentClassifier):
    def __init__(self, model_service: Optional[ModelService] = None) -> None:
        self._model = model_service

    def classify(self, text: str) -> List[str]:
        cleaned = text.strip()

        # Try LLM classification first if model service is available
        if self._model:
            try:
                prompt = (
                    "You are the Lead Intent Classifier for Personal AI OS.\n"
                    f"Classify the following objective into one or more categories:\n"
                    f'Objective: "{cleaned}"\n\n'
                    "Categories available:\n"
                    "- Career\n- Project\n- Research\n- Learning\n- Automation\n- Planning\n- Coding\n- GitHub\n- Knowledge\n- Mission\n- Daily\n- Conversation\n- Hybrid\n\n"
                    'Return a JSON list of matched categories (pure JSON, no markdown formatting, e.g. ["Career", "Research"])'
                )
                res = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output pure JSON list only.",
                        task_category="intent",
                        preferences={"JSON_output": True},
                    )
                )
                content = res.content.strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                categories = json.loads(content)
                if isinstance(categories, list):
                    return [c.capitalize() for c in categories]
            except Exception as e:
                logger.debug(f"LLM intent classification failed: {e}. Falling back to rule-based.")

        # Keyword mapping fallback
        matched = []
        lower_text = cleaned.lower()

        keyword_map = {
            "Career": ["career", "resume", "job", "internship", "interview", "portfolio", "apply"],
            "Project": ["project", "repository", "repo", "adr", "milestone", "workspace"],
            "Research": [
                "research",
                "paper",
                "topic",
                "explain",
                "summarize",
                "literature",
                "find",
            ],
            "Learning": ["learn", "study", "kubernetes", "course", "syllabus", "tutorial"],
            "Automation": ["automate", "n8n", "workflow", "trigger", "deploy", "cron"],
            "Planning": ["plan", "schedule", "roadmap", "backlog", "milestones"],
            "Coding": ["code", "refactor", "build", "compile", "bug", "fix", "function", "class"],
            "GitHub": ["github", "pull request", "pr", "commit", "branch", "git"],
            "Knowledge": ["knowledge", "notion", "obsidian", "sync", "hub", "confluence"],
            "Mission": [
                "mission",
                "objective",
                "executor",
                "milestone report",
                "roadmap completion",
            ],
            "Daily": [
                "daily",
                "task",
                "schedule",
                "session",
                "review",
                "productivity",
                "today",
                "yesterday",
            ],
            "Conversation": ["chat", "say", "hello", "conversation", "dialogue", "respond"],
        }

        for category, keywords in keyword_map.items():
            if any(kw in lower_text for kw in keywords):
                matched.append(category)

        if len(matched) >= 3:
            matched.append("Hybrid")

        if not matched:
            matched.append("Conversation")

        return matched


class LocalIntentAnalyzer(IntentAnalyzer):
    def analyze(self, text: str, context: IntentContext) -> Dict[str, Any]:
        # Maps categories to participating service definitions
        service_map = {
            "Career": "CareerOSService",
            "Project": "ProjectIntelligenceService",
            "Research": "ResearchService",
            "Learning": "CareerOSService",
            "Automation": "N8NService",
            "Planning": "DailyOSService",
            "Coding": "DeveloperWorkspaceService",
            "GitHub": "GitHubService",
            "Knowledge": "KnowledgeHubService",
            "Mission": "MissionEngine",
            "Daily": "DailyOSService",
            "Conversation": "SessionService",
        }

        # Expected outputs mapping
        output_map = {
            "CareerOSService": "career_growth_plan",
            "ProjectIntelligenceService": "project_architecture_audit",
            "ResearchService": "technical_research_report",
            "N8NService": "workflow_execution_logs",
            "DailyOSService": "daily_task_schedule",
            "DeveloperWorkspaceService": "code_refactoring_diff",
            "GitHubService": "git_commit_status",
            "KnowledgeHubService": "notion_sync_confirmation",
            "MissionEngine": "mission_execution_summary",
            "SessionService": "conversation_history_record",
        }

        return {
            "service_map": service_map,
            "output_map": output_map,
        }


class LocalIntentResolver(IntentResolver):
    def __init__(self, classifier: IntentClassifier, analyzer: IntentAnalyzer) -> None:
        self._classifier = classifier
        self._analyzer = analyzer

    def resolve_plan(self, text: str, context: IntentContext) -> IntentPlan:
        categories = self._classifier.classify(text)
        analysis = self._analyzer.analyze(text, context)

        service_map = analysis["service_map"]
        output_map = analysis["output_map"]

        # 1. Determine participating services
        participating = set()
        for cat in categories:
            svc = service_map.get(cat)
            if svc:
                participating.add(svc)

        # Always include MemoryService for state queries
        participating.add("MemoryService")
        participating_list = list(participating)

        # 2. Establish Execution Order based on priority
        # Pre-defined topological ordering for services
        priority_order = [
            "MemoryService",
            "GitHubService",
            "ResearchService",
            "ProjectIntelligenceService",
            "CareerOSService",
            "DailyOSService",
            "MissionEngine",
            "KnowledgeHubService",
            "N8NService",
            "SessionService",
        ]

        execution_order = [svc for svc in priority_order if svc in participating_list]

        # 3. Formulate dependencies dynamically
        dependencies = {}
        for idx, svc in enumerate(execution_order):
            if idx == 0:
                dependencies[svc] = []
            else:
                # Depend on previous service in order
                dependencies[svc] = [execution_order[idx - 1]]

        # 4. Formulate expected outputs
        expected_outputs = {}
        for svc in execution_order:
            expected_outputs[svc] = output_map.get(svc, "execution_status_report")

        # 5. Formulate context requirements
        context_requirements = {
            "required_keys": ["objective", "active_profile"],
            "memories_count": len(context.memories),
        }

        return IntentPlan(
            plan_id=f"intent_plan_{int(time.time())}",
            objective=text,
            intents=categories,
            participating_services=execution_order,
            execution_order=execution_order,
            dependencies=dependencies,
            expected_outputs=expected_outputs,
            context_requirements=context_requirements,
        )


class LocalIntentEngine(IntentEngine):
    def __init__(
        self,
        memory_service: MemoryService,
        reasoning_service: ReasoningService,
        model_service: Optional[ModelService] = None,
    ) -> None:
        self._memory = memory_service
        self._reasoning = reasoning_service
        self._model = model_service
        self._classifier = LocalIntentClassifier(model_service)
        self._analyzer = LocalIntentAnalyzer()
        self._resolver = LocalIntentResolver(self._classifier, self._analyzer)

    def initialize(self) -> None:
        logger.info("Initializing LocalIntentEngine")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def process_objective(self, objective: str) -> IntentResult:
        logger.info(f"Intent Engine processing objective: '{objective}'")

        # 1. Memory retrieval check
        memories = []
        try:
            retriever = self._memory.retriever
            retrieval_ctx = RetrievalContext(objective=objective, max_results=5)
            memories = retriever.retrieve(retrieval_ctx)
        except Exception as e:
            logger.error(f"Failed to retrieve memories for intent planning: {e}")

        # 2. Formulate context
        context = IntentContext(
            variables={"timestamp": time.time(), "objective": objective},
            memories=[m.content for m in memories],
        )

        # 3. Resolve plan execution graph
        try:
            plan = self._resolver.resolve_plan(objective, context)
        except Exception as e:
            return IntentResult(success=False, error_message=f"Plan formulation failed: {e}")

        # 4. Pass execution plan to reasoning engine
        try:
            reasoning_ctx = ReasoningContext(
                variables={
                    "intent_plan": {
                        "plan_id": plan.plan_id,
                        "intents": plan.intents,
                        "participating_services": plan.participating_services,
                        "execution_order": plan.execution_order,
                    },
                    "retrieved_memories": context.memories,
                }
            )
            # Evaluate using the Reasoning Engine
            res = self._reasoning.reason(objective, reasoning_ctx)
            if not res.success:
                return IntentResult(
                    success=False,
                    plan=plan,
                    error_message=f"Reasoning evaluation rejected the plan: {res.self_critique.get('safety_status', 'Unknown')}",
                )
        except Exception as e:
            logger.error(f"Reasoning engine check failed: {e}")

        return IntentResult(success=True, plan=plan)

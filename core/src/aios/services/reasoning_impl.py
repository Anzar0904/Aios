import time
import logging
from typing import Dict, List, Any, Optional

from aios.services.reasoning import (
    ReasoningStrategy,
    ReasoningStep,
    ReasoningChain,
    ReasoningContext,
    ReasoningResult,
    ReasoningSession,
    ReasoningEvaluator,
    ReasoningCritic,
    ReasoningService,
)

logger = logging.getLogger(__name__)


class LocalReasoningEvaluator(ReasoningEvaluator):
    def evaluate(self, plan: Dict[str, Any], strategy: ReasoningStrategy) -> Dict[str, Any]:
        tasks = plan.get("tasks", [])
        completeness = 1.0 if len(tasks) >= 2 else 0.5
        
        # Calculate complexity based on step counts
        complexity = "low" if len(tasks) <= 2 else "medium"
        
        # Safety analysis
        safety_status = "safe"
        for t in tasks:
            cmd = t.get("command", "").lower()
            if any(unsafe in cmd for unsafe in (";", "&&", "||", "rm -rf", "sudo")):
                safety_status = "unsafe"
                break

        return {
            "completeness_score": completeness,
            "complexity": complexity,
            "safety_status": safety_status,
            "evaluated_at": time.time()
        }


class LocalReasoningCritic(ReasoningCritic):
    def critique(self, step: ReasoningStep, context: ReasoningContext) -> str:
        thought_lower = step.thought.lower()
        criticisms = []

        if "rm" in thought_lower or "delete" in thought_lower:
            criticisms.append("Warning: Step mentions file deletions. Ensure backup actions exist.")
        if len(thought_lower) < 15:
            criticisms.append("Step thought is brief; detail complexity trade-offs.")

        return " | ".join(criticisms) if criticisms else "Acceptable thought."


class LocalReasoningService(ReasoningService):
    def __init__(self) -> None:
        self._evaluator = LocalReasoningEvaluator()
        self._critic = LocalReasoningCritic()
        self._sessions: Dict[str, ReasoningSession] = {}

    def initialize(self) -> None:
        pass

    def create_session(self, objective: str) -> ReasoningSession:
        session_id = f"rsession_{int(time.time())}"
        session = ReasoningSession(session_id=session_id, objective=objective, created_at=time.time())
        self._sessions[session_id] = session
        return session

    def reason(self, objective: str, context: ReasoningContext) -> ReasoningResult:
        logger.info(f"Reasoning about objective: '{objective}'...")
        
        # 1. Goal Analysis: Select reasoning strategy
        strategy = self._select_strategy(objective)
        
        # 2. Context Collection
        workspace_files = context.variables.get("staged_files", [])
        profile_email = context.variables.get("contact_email", "")

        # 3. Create Reasoning Chain and critique pipeline
        chain = ReasoningChain(chain_id=f"chain_{int(time.time())}")
        
        step1 = ReasoningStep(
            step_id="step-1-parse",
            thought=f"Need to formulate a plan to solve: {objective} matching strategy {strategy.name}."
        )
        step1.critique = self._critic.critique(step1, context)
        chain.steps.append(step1)

        # 4. Generate candidate plan steps
        candidate_tasks = []
        if strategy == ReasoningStrategy.CAREER:
            candidate_tasks = [
                {"step_id": "r1", "name": "research openings", "command": "career jobs python internship"},
                {"step_id": "r2", "name": "tailor summary", "command": "career optimize resume"}
            ]
        elif strategy == ReasoningStrategy.AUTOMATION:
            candidate_tasks = [
                {"step_id": "a1", "name": "validate connection", "command": "n8n workflow validate"},
                {"step_id": "a2", "name": "deploy workflow", "command": "n8n workflow execute"}
            ]
        else:
            candidate_tasks = [
                {"step_id": "g1", "name": "gather context", "command": "research topic AI OS design"},
                {"step_id": "g2", "name": "analyze structure", "command": "career analyze code"}
            ]

        compiled_plan = {
            "plan_id": f"plan_{int(time.time())}",
            "tasks": candidate_tasks
        }

        # 5. Evaluate plan quality
        critique_report = self._evaluator.evaluate(compiled_plan, strategy)

        # Success is determined by safety check
        success = critique_report["safety_status"] == "safe"

        return ReasoningResult(
            success=success,
            plan=compiled_plan,
            strategy=strategy,
            self_critique=critique_report,
            chain=chain
        )

    def _select_strategy(self, objective: str) -> ReasoningStrategy:
        obj_lower = objective.lower()
        if any(kw in obj_lower for kw in ("code", "refactor", "build", "compile")):
            return ReasoningStrategy.ENGINEERING
        elif any(kw in obj_lower for kw in ("research", "paper", "find", "locate")):
            return ReasoningStrategy.RESEARCH
        elif any(kw in obj_lower for kw in ("career", "resume", "job", "internship")):
            return ReasoningStrategy.CAREER
        elif any(kw in obj_lower for kw in ("automate", "n8n", "workflow", "deploy")):
            return ReasoningStrategy.AUTOMATION
        elif any(kw in obj_lower for kw in ("learn", "study", "kubernetes")):
            return ReasoningStrategy.LEARNING
        else:
            return ReasoningStrategy.HYBRID

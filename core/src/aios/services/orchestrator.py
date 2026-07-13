import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List

from aios.services.base import ServiceLifecycle


@dataclass
class SkillInvocation:
    step_id: str
    skill_id: str
    command: str
    depends_on: List[str] = field(default_factory=list)
    inputs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    plan_id: str
    invocations: List[SkillInvocation] = field(default_factory=list)


@dataclass
class ExecutionContext:
    variables: Dict[str, Any] = field(default_factory=dict)


class ResultAggregator(abc.ABC):
    @abc.abstractmethod
    def aggregate(self, results: Dict[str, Any]) -> str:
        """Aggregates multiple step outputs into a single consolidated report."""
        pass


class OrchestratorService(ServiceLifecycle, abc.ABC):
    @abc.abstractmethod
    def execute_plan(self, plan: ExecutionPlan, initial_ctx: ExecutionContext) -> Dict[str, Any]:
        """Executes a multi-skill execution plan in dependency order, passing outputs."""
        pass

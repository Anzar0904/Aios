import contextlib
import io
import logging
from typing import Any, Dict, List

from aios.services.command import CommandRegistry
from aios.services.orchestrator import (
    ExecutionContext,
    ExecutionPlan,
    OrchestratorService,
    ResultAggregator,
    SkillInvocation,
)

logger = logging.getLogger(__name__)


class DefaultResultAggregator(ResultAggregator):
    def aggregate(self, results: Dict[str, Any]) -> str:
        report = ["# Multi-Skill Execution Report\n"]
        for step_id, out in results.items():
            report.append(f"## Step ID: {step_id}\n")
            report.append(f"{out}\n")
        return "\n".join(report)


class LocalOrchestratorService(OrchestratorService):
    def __init__(self, command_registry: CommandRegistry) -> None:
        self._registry = command_registry
        self._aggregator = DefaultResultAggregator()

    def initialize(self) -> None:
        pass

    def execute_plan(self, plan: ExecutionPlan, initial_ctx: ExecutionContext) -> Dict[str, Any]:
        logger.info(
            f"Orchestrating execution plan '{plan.plan_id}' with {len(plan.invocations)} invocations..."
        )

        # 1. Topological Sort / Level grouping of skill invocations
        try:
            levels = self._group_invocations_into_levels(plan.invocations)
        except Exception as e:
            logger.error(f"Failed to group invocations: {str(e)}")
            return {"success": False, "error": f"Invalid graph: {str(e)}"}

        results = {}
        for level in levels:
            for inv in level:
                # 2. Variable substitution / Context parameter passing
                substituted_command = self._substitute_parameters(
                    inv.command, initial_ctx.variables
                )

                logger.info(f"Running invocation step '{inv.step_id}': {substituted_command}")
                try:
                    # 3. Resolve command handler
                    handler, args = self._resolve_handler_and_args(substituted_command)

                    # 4. Execute with stdout capture redirection
                    output = self._run_handler_capture(handler, args)

                    # 5. Save results to context variables
                    results[inv.step_id] = output
                    initial_ctx.variables[inv.step_id] = output
                    initial_ctx.variables[f"{inv.step_id}.result"] = output

                except Exception as e:
                    logger.error(f"Step '{inv.step_id}' failed: {str(e)}")
                    results[inv.step_id] = f"ERROR: {str(e)}"
                    return {
                        "success": False,
                        "error": f"Step '{inv.step_id}' failed: {str(e)}",
                        "partial_results": results,
                        "report": self._aggregator.aggregate(results),
                    }

        return {"success": True, "results": results, "report": self._aggregator.aggregate(results)}

    def _group_invocations_into_levels(
        self, invocations: List[SkillInvocation]
    ) -> List[List[SkillInvocation]]:
        # DFS coloring loop checks
        adj = {inv.step_id: [] for inv in invocations}
        lookup = {inv.step_id: inv for inv in invocations}

        for inv in invocations:
            for dep in inv.depends_on:
                if dep not in adj:
                    raise ValueError(f"Dependency '{dep}' does not exist in execution plan.")
                adj[dep].append(inv.step_id)

        # Detect cycles
        visited = {}

        def dfs(node: str) -> bool:
            visited[node] = 1
            for neighbor in adj[node]:
                state = visited.get(neighbor, 0)
                if state == 1:
                    return True
                elif state == 0:
                    if dfs(neighbor):
                        return True
            visited[node] = 2
            return False

        for node in adj:
            if visited.get(node, 0) == 0:
                if dfs(node):
                    raise ValueError("Circular dependency detected in execution plan.")

        # Compute level grouping (longest dependency path length)
        memo = {}

        def get_max_depth(node: str) -> int:
            if node in memo:
                return memo[node]

            inv = lookup[node]
            if not inv.depends_on:
                depth = 0
            else:
                depth = 1 + max(get_max_depth(dep) for dep in inv.depends_on)
            memo[node] = depth
            return depth

        level_groups = {}
        for inv in invocations:
            depth = get_max_depth(inv.step_id)
            level_groups.setdefault(depth, []).append(inv)

        return [level_groups[d] for d in sorted(level_groups.keys())]

    def _substitute_parameters(self, command: str, variables: Dict[str, Any]) -> str:
        # Replaces placeholders like {step_id} or {step_id.result} with variable values
        for key, val in variables.items():
            placeholder = f"{{{key}}}"
            if placeholder in command:
                command = command.replace(placeholder, str(val))
        return command

    def _resolve_handler_and_args(self, command_str: str) -> tuple[Any, str]:
        command_str_lower = command_str.lower()
        matched_cmd = None
        matched_args = ""

        # Sort by length descending to match longest prefix
        for cmd_name in sorted(self._registry._commands.keys(), key=len, reverse=True):
            if command_str_lower.startswith(cmd_name):
                matched_cmd = cmd_name
                matched_args = command_str[len(cmd_name) :].strip()
                break

        if not matched_cmd:
            raise ValueError(f"Command '{command_str}' matches no registered skills.")

        handler = self._registry.get_handler(matched_cmd)
        return handler, matched_args

    def _run_handler_capture(self, handler: Any, args: str) -> str:
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            res = handler(args)
        output = f.getvalue().strip()
        return str(res) if res else output

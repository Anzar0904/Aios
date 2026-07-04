import time

from aios.services.action.models import ActionPlan


class ActionReportGenerator:
    def __init__(self) -> None:
        pass

    def generate(self, plan: ActionPlan, start_time: float) -> str:
        elapsed = time.time() - start_time
        
        summary = "# Execution Report\n\n"
        summary += "## Summary\n"
        summary += f"- **Objective**: {plan.objective}\n"
        summary += f"- **Status**: {plan.status.upper()}\n"
        summary += f"- **Elapsed Time**: {elapsed:.2f} seconds\n\n"
        
        summary += "## Steps Executed\n"
        files_changed = []
        commands_executed = []
        verification_results = []
        warnings = []
        errors = []
        
        for idx, step in enumerate(plan.steps, 1):
            status_marker = (
                "✓"
                if step.status == "completed"
                else "✗"
                if step.status == "failed"
                else "..."
            )
            summary += f"### {idx}. {step.description} [{step.status.upper()}] {status_marker}\n"
            summary += f"- **Tool**: {step.tool_name}\n"
            summary += f"- **Args**: `{step.tool_args}`\n"
            if step.error:
                summary += f"- **Error**: {step.error}\n"
                errors.append(f"Step {idx} failed: {step.error}")
            
            if step.tool_name == "filesystem" and "path" in step.tool_args:
                files_changed.append(step.tool_args["path"])
            if step.tool_name in ("git", "terminal"):
                commands_executed.append(str(step.tool_args))
                
            verification_results.append(f"Step {idx}: {step.status}")
            
            if not step.is_reversible:
                warnings.append(f"Step {idx} ({step.description}) is irreversible.")

        summary += "\n## Files Changed\n"
        if files_changed:
            summary += "\n".join([f"- {f}" for f in set(files_changed)]) + "\n"
        else:
            summary += "None.\n"
            
        summary += "\n## Tool Operations\n"
        if commands_executed:
            summary += "\n".join([f"- `{c}`" for c in commands_executed]) + "\n"
        else:
            summary += "None.\n"
            
        summary += "\n## Verification Results\n"
        summary += "\n".join([f"- {v}" for v in verification_results]) + "\n"
        
        if warnings:
            summary += "\n## Warnings\n"
            summary += "\n".join([f"- ⚠️ {w}" for w in warnings]) + "\n"
            
        if errors:
            summary += "\n## Errors\n"
            summary += "\n".join([f"- ❌ {e}" for e in errors]) + "\n"
            
        return summary

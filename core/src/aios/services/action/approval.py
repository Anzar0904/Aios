from aios.services.action.models import ActionPlan, RiskLevel


class ApprovalManager:
    def __init__(self) -> None:
        pass

    def display_plan(self, plan: ActionPlan) -> None:
        print(f"\nExecution Plan (ID: {plan.id})")
        print(f"Objective: {plan.objective}")
        print("-" * 50)

        has_high_risk = False
        for idx, step in enumerate(plan.steps, 1):
            risk_str = step.risk_level.value
            if step.risk_level == RiskLevel.HIGH:
                risk_str = "⚠️ HIGH risk"
                has_high_risk = True

            reversible_str = "Reversible" if step.is_reversible else "⚠️ IRREVERSIBLE"
            print(f"Step {idx}: {step.description}")
            print(f"  Action: {step.action_type.value} | Risk: {risk_str} | {reversible_str}")
            print(f"  Tool: {step.tool_name} with args: {step.tool_args}")
            print()

        if has_high_risk:
            print("⚠️ THIS PLAN CONTAINS HIGH RISK STEPS AND REQUIRES EXPLICIT APPROVAL.")
            print()

    def approve_plan(self, plan: ActionPlan) -> None:
        plan.status = "approved"
        for step in plan.steps:
            step.status = "approved"

    def reject_plan(self, plan: ActionPlan) -> None:
        plan.status = "rejected"
        for step in plan.steps:
            step.status = "rejected"

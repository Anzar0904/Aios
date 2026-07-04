import logging
import time
from typing import Any, Optional

from aios.services.command.metadata import CommandCategory, CommandMetadata
from aios.services.command.registry import CommandRegistry
from aios.services.intent import Intent, IntentType

logger = logging.getLogger(__name__)


def execute_agent_intent(kernel: Any, intent_type: IntentType, action: str, params: dict) -> None:
    intent = Intent(
        intent_type=intent_type,
        target_service="AgentRuntimeService",
        action=action,
        parameters=params,
        confidence=1.0,
    )
    result = kernel.execute_intent(intent)
    print(result.message)


def execute_tailor_resume(kernel: Any, args: str) -> None:
    parts = args.strip().split() if args else []
    resume = parts[0] if len(parts) > 0 else "resume.pdf"
    job = parts[1] if len(parts) > 1 else "job.pdf"
    execute_agent_intent(
        kernel,
        IntentType.CAREER,
        "TailorResume",
        {"resume_path": resume, "job_description_path": job},
    )


def execute_ats_score(kernel: Any, args: str) -> None:
    parts = args.strip().split() if args else []
    resume = parts[0] if len(parts) > 0 else "resume.pdf"
    job = parts[1] if len(parts) > 1 else "job.pdf"
    execute_agent_intent(
        kernel,
        IntentType.CAREER,
        "ATSScore",
        {"resume_path": resume, "job_description_path": job},
    )


def execute_cover_letter(kernel: Any, args: str) -> None:
    parts = args.strip().split() if args else []
    resume = parts[0] if len(parts) > 0 else "resume.pdf"
    job = parts[1] if len(parts) > 1 else "job.pdf"
    execute_agent_intent(
        kernel,
        IntentType.CAREER,
        "CoverLetter",
        {"resume_path": resume, "job_description_path": job},
    )


def execute_system_status(kernel: Any) -> None:
    intent = Intent(
        intent_type=IntentType.SYSTEM,
        target_service="Kernel",
        action="Status",
        parameters={},
        confidence=1.0,
    )
    result = kernel.execute_intent(intent)
    print(result.message)


def handle_new_conversation(conv_manager: Any, args: str) -> None:
    title = args.strip() if args else None
    conv = conv_manager.create_conversation(title=title, agent_name="developer_agent")
    print(f"Created and switched to conversation: '{conv.title}' ({conv.id})")


def handle_list_conversations(conv_manager: Any) -> None:
    convs = conv_manager.list_conversations()
    if not convs:
        print("No conversations found.")
    else:
        print("\nConversations:")
        current = conv_manager.active_conversation_id
        for c in convs:
            active_marker = "*" if c["id"] == current else " "
            agent_name = c["active_agent"] or "None"
            print(f"{active_marker} {c['id']} - {c['title']} (Agent: {agent_name})")
        print()


def handle_resume_conversation(conv_manager: Any, args: str) -> None:
    target = args.strip()
    if not target:
        convs = conv_manager.list_conversations()
        if not convs:
            print("No conversations to resume.")
            return
        print("\nConversations:")
        for idx, c in enumerate(convs, 1):
            print(f"[{idx}] {c['id']} - {c['title']}")
        choice = input("Enter number or ID to resume: ").strip()
        if not choice:
            return
        try:
            idx = int(choice)
            if 1 <= idx <= len(convs):
                target = convs[idx - 1]["id"]
        except ValueError:
            target = choice

    convs = conv_manager.list_conversations()
    found_id = None
    for c in convs:
        if c["id"] == target or c["title"].lower() == target.lower():
            found_id = c["id"]
            break

    if found_id:
        conv = conv_manager.resume_conversation(found_id)
        print(f"Resumed conversation: '{conv.title}' ({conv.id})")
    else:
        print(f"Conversation '{target}' not found.")


def handle_rename_conversation(conv_manager: Any) -> None:
    conv = conv_manager.get_current_conversation()
    if not conv:
        print("No active conversation to rename.")
        return
    new_title = input(f"Enter new title for '{conv.title}': ").strip()
    if new_title:
        conv_manager.rename_conversation(conv.id, new_title)
        print(f"Renamed conversation to: '{new_title}'")


def handle_delete_conversation(conv_manager: Any, args: str) -> None:
    target = args.strip()
    convs = conv_manager.list_conversations()
    if not convs:
        print("No conversations to delete.")
        return

    if not target:
        print("\nConversations:")
        for idx, c in enumerate(convs, 1):
            print(f"[{idx}] {c['id']} - {c['title']}")
        choice = input("Enter number or ID to delete: ").strip()
        if not choice:
            return
        target = choice
        try:
            idx = int(choice)
            if 1 <= idx <= len(convs):
                target = convs[idx - 1]["id"]
        except ValueError:
            pass

    found_id = None
    for c in convs:
        if c["id"] == target or c["title"].lower() == target.lower():
            found_id = c["id"]
            break

    if found_id:
        confirm = (
            input(f"Are you sure you want to delete conversation '{found_id}'? (y/n): ")
            .strip()
            .lower()
        )
        if confirm == "y":
            conv_manager.delete_conversation(found_id)
            print(f"Deleted conversation: {found_id}")
    else:
        print(f"Conversation '{target}' not found.")


def handle_current_conversation(conv_manager: Any) -> None:
    conv = conv_manager.get_current_conversation()
    if not conv:
        print("No active conversation.")
    else:
        print("\nActive Conversation:")
        print(f"  ID: {conv.id}")
        print(f"  Title: {conv.title}")
        print(f"  Agent: {conv.active_agent or 'None'}")
        created_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(conv.created_time))
        updated_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(conv.updated_time))
        print(f"  Created: {created_str}")
        print(f"  Updated: {updated_str}")
        if conv.summary:
            print(f"  Summary: {conv.summary.summary}")
        print()


def handle_show_history(conv_manager: Any) -> None:
    conv = conv_manager.get_current_conversation()
    if not conv:
        print("No active conversation.")
    else:
        print(f"\n--- History for '{conv.title}' ---")
        if conv.summary:
            s = conv.summary
            print(f"[SUMMARY] {s.summary}")
            if s.decisions:
                print("  Decisions:")
                for d in s.decisions:
                    print(f"    - {d}")
            if s.action_items:
                print("  Action Items:")
                for a in s.action_items:
                    print(f"    - {a}")
            if s.unresolved_questions:
                print("  Unresolved Questions:")
                for q in s.unresolved_questions:
                    print(f"    - {q}")
            print("-" * 30)

        for m in conv.messages:
            role_str = m.role.upper()
            print(f"[{role_str}]")
            print(m.content)
            print()
        print("-----------------------------------")


def handle_action_plan(kernel: Any, action_history: Any, args: str) -> None:
    objective = args.strip()
    if not objective:
        print("Please provide an action objective.")
        return

    from aios.services.model import ModelService

    try:
        model_svc = kernel.registry.get(ModelService)
    except Exception:
        model_svc = None

    from aios.services.action.approval import ApprovalManager
    from aios.services.action.planner import ActionPlanner

    planner = ActionPlanner(model_svc)
    plan = planner.plan(objective)

    action_history.save_plan(plan)
    action_history.set_active_plan(plan)

    ApprovalManager().display_plan(plan)


def handle_action_approve(action_history: Any) -> None:
    plan = action_history.get_active_plan()
    if not plan:
        print("No active plan to approve.")
        return

    from aios.services.action.approval import ApprovalManager

    ApprovalManager().approve_plan(plan)
    action_history.save_plan(plan)
    action_history.set_active_plan(plan)
    print("Plan approved successfully. Run 'execute' to execute approved steps.")


def handle_action_reject(action_history: Any) -> None:
    plan = action_history.get_active_plan()
    if not plan:
        print("No active plan to reject.")
        return

    from aios.services.action.approval import ApprovalManager

    ApprovalManager().reject_plan(plan)
    action_history.save_plan(plan)
    action_history.clear_active_plan()
    print("Plan rejected. Active plan cleared.")


def handle_action_execute(kernel: Any, action_history: Any) -> None:
    plan = action_history.get_active_plan()
    if not plan:
        print("No active plan to execute. Generate a plan first.")
        return

    if plan.status != "approved":
        print(f"Plan cannot be executed. Status is '{plan.status}'. Run 'approve' first.")
        return

    from aios.services.tool import ToolService

    tool_svc = kernel.registry.get(ToolService)

    from aios.services.action.executor import ActionExecutor

    executor = ActionExecutor(tool_svc)

    print("\nExecuting approved plan steps...")
    report = executor.execute_plan(plan)
    action_history.save_plan(plan)
    action_history.clear_active_plan()

    print("\nExecution Report:")
    print(report)


def handle_action_rollback(kernel: Any, action_history: Any, args: str) -> None:
    target_id = args.strip()
    if not target_id:
        plans = action_history.list_plans()
        if not plans:
            print("No plan history found.")
            return
        plan = plans[0]
    else:
        plan = action_history.load_plan(target_id)
        if not plan:
            print(f"Plan '{target_id}' not found.")
            return

    print(f"\nRolling back Plan: {plan.objective}")

    from aios.services.tool import ToolService

    tool_svc = kernel.registry.get(ToolService)

    from aios.services.action.rollback import RollbackCoordinator

    coordinator = RollbackCoordinator(tool_svc)

    rolled_back_count = 0
    for step in reversed(plan.steps):
        if step.status == "completed" and step.is_reversible:
            success = coordinator.rollback_step(step)
            if success:
                rolled_back_count += 1
                print(f"Rolled back step: {step.description}")
            else:
                print(f"Failed to roll back step: {step.description}")

    plan.status = "rolled_back"
    action_history.save_plan(plan)
    print(f"Rollback finished. {rolled_back_count} steps reverted.")


def handle_action_history(action_history: Any) -> None:
    plans = action_history.list_plans()
    if not plans:
        print("No execution history found.")
        return
    print("\nExecution History:")
    for p in plans:
        print(f"  {p.id[:8]} - {p.objective:<40} [{p.status.upper()}]")
    print()


def handle_run_task(
    registry: CommandRegistry,
    kernel: Any,
    task_history: Any,
    progress_tracker: Any,
    args: str,
) -> None:
    objective = args.strip()
    if not objective:
        print("Please provide a task objective.")
        return

    from aios.services.model import ModelService

    try:
        model_svc = kernel.registry.get(ModelService)
    except Exception:
        model_svc = None

    from aios.services.task import Task, TaskExecutor, TaskPlanner

    planner = TaskPlanner(registry, model_svc)
    steps = planner.plan(objective)

    if not steps:
        print("Failed to plan steps for the given objective. No matching commands found.")
        return

    task = Task(objective=objective, steps=steps)
    task_history.save_task(task)

    executor = TaskExecutor(registry, progress_tracker)
    executor.execute_task(task)
    task_history.save_task(task)

    print(f"\nTask execution completed with status: {task.status.upper()}")


def handle_task_status(task_history: Any) -> None:
    tasks = task_history.list_tasks()
    if not tasks:
        print("No tasks found in history.")
        return
    task = tasks[0]
    print("\nLast Task Status:")
    print(f"  ID: {task.id}")
    print(f"  Objective: {task.objective}")
    print(f"  Status: {task.status.upper()}")
    updated_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(task.updated_at))
    print(f"  Uptime/Updated: {updated_str}")
    print("\nSteps:")
    for idx, s in enumerate(task.steps, 1):
        marker = "✓" if s.status == "completed" else "✗" if s.status == "failed" else "..."
        print(f"  [{idx}/{len(task.steps)}] {s.command} ({s.status.upper()}) {marker}")
    print()


def handle_task_history(task_history: Any) -> None:
    tasks = task_history.list_tasks()
    if not tasks:
        print("No tasks found in history.")
        return
    print("\nTask History:")
    for t in tasks:
        print(f"  {t.id[:8]} - {t.title:<40} [{t.status.upper()}]")
    print()


def handle_task_resume(
    registry: CommandRegistry,
    kernel: Any,
    task_history: Any,
    progress_tracker: Any,
    args: str,
) -> None:
    target_id = args.strip()
    from aios.services.task import TaskExecutor

    if not target_id:
        tasks = task_history.list_tasks()
        incomplete = [t for t in tasks if t.status in ("failed", "pending", "running")]
        if not incomplete:
            print("No failed or incomplete tasks found to resume.")
            return
        task = incomplete[0]
    else:
        task = task_history.load_task(target_id)
        if not task:
            print(f"Task '{target_id}' not found.")
            return

    print(f"\nResuming Task: {task.title}")
    resumed_any = False
    for step in task.steps:
        if step.status in ("failed", "pending", "running"):
            step.status = "pending"
            resumed_any = True

    if not resumed_any:
        print("All steps are already completed. Nothing to resume.")
        return

    executor = TaskExecutor(registry, progress_tracker)
    executor.execute_task(task)
    task_history.save_task(task)
    print(f"\nTask execution completed with status: {task.status.upper()}")


def handle_help(registry: CommandRegistry, args: str) -> None:
    target = args.strip().lower()
    if not target:
        print("\n=== Personal AI OS Command Help ===")
        print("Use 'commands' to see all available commands.")
        print("Use 'help <command>' to get details on a specific command.")
        print("Use 'search command <keyword>' to search for a command.")
        print("====================================\n")
        return

    cmd = registry.get_command(target)
    if cmd:
        print(f"\nCommand: {cmd.name}")
        print(f"  Description: {cmd.description}")
        print(f"  Category: {cmd.category.value}")
        print(f"  Required Agent: {cmd.required_agent}")
        tools_str = ", ".join(cmd.required_tools) if cmd.required_tools else "None"
        print(f"  Required Tools: {tools_str}")
        print(f"  Example: {cmd.example_usage}")
        print()
    else:
        print(f"Command '{target}' not found. Use 'commands' to see all commands.")


def handle_commands(registry: CommandRegistry, args: str) -> None:
    target = args.strip().lower()

    matched_category = None
    if target:
        for cat in CommandCategory:
            if cat.value.lower() == target or cat.name.lower() == target:
                matched_category = cat
                break
        if not matched_category:
            print(f"Category '{target}' not recognized. Showing all commands.")

    if matched_category:
        cmds = registry.list_commands(matched_category)
        print(f"\n=== {matched_category.value} Commands ===")
        for c in cmds:
            print(f"  {c.name:<25} - {c.description}")
        print()
    else:
        print("\n=== All Commands ===")
        for cat in CommandCategory:
            cmds = registry.list_commands(cat)
            if cmds:
                print(f"\nCategory: {cat.value}")
                for c in cmds:
                    print(f"  {c.name:<25} - {c.description}")
        print()


def handle_search_command(registry: CommandRegistry, args: str) -> None:
    keyword = args.strip()
    if not keyword:
        print("Please provide a keyword to search for.")
        return

    results = registry.search_commands(keyword)
    if not results:
        print(f"No commands matching '{keyword}' found.")
    else:
        print(f"\n=== Search Results for '{keyword}' ===")
        for c in results:
            print(f"  {c.name:<25} [{c.category.value}] - {c.description}")
        print()


def handle_skills_list(registry: Any) -> None:
    skills = registry.list_skills()
    if not skills:
        print("No skills loaded.")
        return
    print("\nLoaded Skills:")
    for s in skills:
        status = "ENABLED" if s.enabled else "DISABLED"
        print(f"  {s.metadata.id:<15} - {s.metadata.name:<25} v{s.metadata.version:<8} [{status}]")
    print()


def handle_skills_inspect(registry: Any, args: str) -> None:
    target = args.strip().lower()
    if not target:
        print("Please specify a skill ID. E.g. skills inspect developer")
        return
    skill = registry.get_skill(target)
    if not skill:
        print(f"Skill '{target}' not found.")
        return
    meta = skill.metadata
    print(f"\nSkill: {meta.name} (ID: {meta.id})")
    print(f"  Version: {meta.version}")
    print(f"  Author: {meta.author}")
    print(f"  Description: {meta.description}")
    print(f"  Category: {meta.category}")
    print(f"  Enabled: {skill.enabled}")
    print(f"  Commands: {', '.join(meta.commands) if meta.commands else 'None'}")
    print(f"  Required Tools: {', '.join(meta.required_tools) if meta.required_tools else 'None'}")
    print(
        f"  Required Models: {', '.join(meta.required_models) if meta.required_models else 'None'}"
    )
    print()


def handle_skills_enable(
    manager: Any, registry: Any, kernel: Any, conv_manager: Any, args: str
) -> None:
    target = args.strip().lower()
    if not target:
        print("Please specify a skill ID. E.g. skills enable developer")
        return
    success = manager.enable_skill(target, registry, kernel, conv_manager)
    if success:
        print(f"Skill '{target}' enabled and commands registered.")
    else:
        print(f"Failed to enable skill '{target}'.")


def handle_skills_disable(manager: Any, registry: Any, args: str) -> None:
    target = args.strip().lower()
    if not target:
        print("Please specify a skill ID. E.g. skills disable developer")
        return
    success = manager.disable_skill(target, registry)
    if success:
        print(f"Skill '{target}' disabled and commands unregistered.")
    else:
        print(f"Failed to disable skill '{target}'.")


def handle_skills_reload(
    manager: Any, registry: Any, kernel: Any, conv_manager: Any, args: str
) -> None:
    target = args.strip().lower()
    if target:
        success = manager.reload_skill(target, registry, kernel, conv_manager)
        if success:
            print(f"Skill '{target}' reloaded successfully.")
        else:
            print(f"Failed to reload skill '{target}'.")
    else:
        print("Reloading all skills...")
        for skill in manager.registry.list_skills():
            skill.unregister_commands(registry)
        manager.registry._skills.clear()

        manager.load_all_skills()
        manager.register_all_commands(registry, kernel, conv_manager)
        print("All skills reloaded successfully.")


def match_command(
    user_input: str, registry: CommandRegistry
) -> Optional[tuple[CommandMetadata, str]]:
    cleaned = user_input.strip()
    sorted_cmds = sorted(registry._commands.values(), key=lambda x: len(x.name), reverse=True)
    for cmd in sorted_cmds:
        if cleaned.lower() == cmd.name.lower():
            return cmd, ""
        elif cleaned.lower().startswith(cmd.name.lower() + " "):
            args = cleaned[len(cmd.name) :].strip()
            return cmd, args
    return None


def register_default_commands(registry: CommandRegistry, kernel: Any, conv_manager: Any) -> None:
    from pathlib import Path

    workspace_root = "."
    if kernel:
        try:
            from aios.services.context import ContextService

            ctx_svc = kernel.registry.get(ContextService)
            ctx = ctx_svc.get_current_context()
            if ctx:
                workspace_root = ctx.project_root
        except Exception:
            pass

    # 1. Initialize SkillRegistry and SkillManager
    from aios.skills.manager import SkillManager
    from aios.skills.registry import SkillRegistry

    skills_dir = Path(workspace_root) / "skills"
    skill_registry = SkillRegistry()
    skill_manager = SkillManager(skills_dir, skill_registry)

    # Automatically load and register all skills
    skill_manager.load_all_skills()
    skill_manager.register_all_commands(registry, kernel, conv_manager)

    # 2. CLI Category (help / commands / search)
    registry.register_command(
        CommandMetadata(
            name="help",
            description="Displays general help or detailed documentation for a specific command.",
            category=CommandCategory.CLI,
            required_agent="None",
            required_tools=[],
            example_usage="help analyze repository",
        ),
        lambda args: handle_help(registry, args),
    )

    registry.register_command(
        CommandMetadata(
            name="commands",
            description="Lists all commands, optionally filtered by category.",
            category=CommandCategory.CLI,
            required_agent="None",
            required_tools=[],
            example_usage="commands developer",
        ),
        lambda args: handle_commands(registry, args),
    )

    registry.register_command(
        CommandMetadata(
            name="search command",
            description="Searches for commands matching a keyword.",
            category=CommandCategory.CLI,
            required_agent="None",
            required_tools=[],
            example_usage="search command review",
        ),
        lambda args: handle_search_command(registry, args),
    )

    # 3. CLI Category (Skill Lifecycle commands)
    registry.register_command(
        CommandMetadata(
            name="skills",
            description="Lists all loaded skills.",
            category=CommandCategory.CLI,
            required_agent="None",
            required_tools=[],
            example_usage="skills",
        ),
        lambda args: handle_skills_list(skill_registry),
    )

    registry.register_command(
        CommandMetadata(
            name="skills list",
            description="Lists all loaded skills.",
            category=CommandCategory.CLI,
            required_agent="None",
            required_tools=[],
            example_usage="skills list",
        ),
        lambda args: handle_skills_list(skill_registry),
    )

    registry.register_command(
        CommandMetadata(
            name="skills inspect",
            description="Inspects metadata details of a specific skill.",
            category=CommandCategory.CLI,
            required_agent="None",
            required_tools=[],
            example_usage="skills inspect developer",
        ),
        lambda args: handle_skills_inspect(skill_registry, args),
    )

    registry.register_command(
        CommandMetadata(
            name="skills enable",
            description="Enables a disabled skill and registers its commands.",
            category=CommandCategory.CLI,
            required_agent="None",
            required_tools=[],
            example_usage="skills enable developer",
        ),
        lambda args: handle_skills_enable(skill_manager, registry, kernel, conv_manager, args),
    )

    registry.register_command(
        CommandMetadata(
            name="skills disable",
            description="Disables an enabled skill and unregisters its commands.",
            category=CommandCategory.CLI,
            required_agent="None",
            required_tools=[],
            example_usage="skills disable developer",
        ),
        lambda args: handle_skills_disable(skill_manager, registry, args),
    )

    registry.register_command(
        CommandMetadata(
            name="skills reload",
            description="Reloads skills and updates their metadata/commands.",
            category=CommandCategory.CLI,
            required_agent="None",
            required_tools=[],
            example_usage="skills reload",
        ),
        lambda args: handle_skills_reload(skill_manager, registry, kernel, conv_manager, args),
    )

    # 4. Brain Commands
    from aios.brain.brain import Brain
    brain_instance = Brain(kernel, registry)

    def handle_brain_execute(args: str) -> None:
        if not args.strip():
            print("Usage: brain <query>")
            return
        print(f"Brain executing: '{args}'...")
        res = brain_instance.execute(args)
        if res.success:
            print("\nResponse:")
            print(res.response)
        else:
            print(f"\nExecution failed:\n{res.response}")

    def handle_brain_explain(args: str) -> None:
        if not args.strip():
            print("Usage: brain explain <query>")
            return
        explanation = brain_instance.explain(args)
        print("\n=== BRAIN EXPLANATION ===")
        print(f"Objective: {explanation['objective']}")
        print(f"Provider: {explanation['provider']['model_name']} (provider: {explanation['provider']['provider_name']})")
        print(f"Reason: {explanation['provider']['reason']}")
        print("\nContext:")
        print(f"  Project Root: {explanation['context']['project_root']}")
        print(f"  Project Name: {explanation['context']['project_name']}")
        print(f"  Git Branch: {explanation['context']['git_branch']}")
        print(f"  Memories Count: {explanation['context']['memories_count']}")
        print("\nSelected Skills:")
        for s in explanation['selected_skills']:
            print(f"  - Skill: {s['skill_id']} (Confidence: {s['confidence']:.2f})")
            print(f"    Reason: {s['reason']}")
        print("\nPlanned Workflow Steps:")
        for idx, step in enumerate(explanation['workflow']['steps'], 1):
            print(f"  {idx}. [{step['skill_id']}] {step['description']}")
            print(f"     Command: {step['command']} {step['args']}")
        print("=========================\n")

    def handle_brain_trace(args: str) -> None:
        wf = None
        target_id = args.strip()
        if target_id:
            for w in brain_instance.history:
                if w.workflow_id == target_id:
                    wf = w
                    break
            if not wf:
                print(f"Workflow '{target_id}' not found in history.")
                return
        else:
            wf = brain_instance.active_workflow
            if not wf:
                print("No active workflow or trace history found.")
                return

        print("\n=== BRAIN TRACE ===")
        print(f"Workflow ID: {wf.workflow_id}")
        print(f"Objective: {wf.objective}")
        print(f"Status: {wf.status}")
        print("\nSteps Trace:")
        for idx, step in enumerate(wf.steps, 1):
            print(f"  {idx}. [{step.status.upper()}] - {step.description}")
            print(f"     Command: {step.command} {step.args}")
            if step.output:
                print(f"     Output: {step.output}")
            if step.error:
                print(f"     Error: {step.error}")
        print("===================\n")

    def handle_brain_status(args: str) -> None:
        print("\n=== BRAIN STATUS ===")
        print(f"Active Workflow: {brain_instance.active_workflow.workflow_id if brain_instance.active_workflow else 'None'}")
        print(f"History Size: {len(brain_instance.history)}")
        print(f"Model Service Model: {getattr(brain_instance.model_service, '_default_model', 'mock-model')}")
        print("====================\n")

    registry.register_command(
        CommandMetadata(
            name="brain explain",
            description="Explains how the Brain would route and plan a given query.",
            category=CommandCategory.CLI,
            required_agent="None",
            required_tools=[],
            example_usage="brain explain clone repository Anzar0904/aios",
        ),
        handle_brain_explain,
    )

    registry.register_command(
        CommandMetadata(
            name="brain trace",
            description="Traces execution details of the last or specified workflow.",
            category=CommandCategory.CLI,
            required_agent="None",
            required_tools=[],
            example_usage="brain trace wf_abcd",
        ),
        handle_brain_trace,
    )

    registry.register_command(
        CommandMetadata(
            name="brain status",
            description="Displays the status and history of the Brain orchestrator.",
            category=CommandCategory.CLI,
            required_agent="None",
            required_tools=[],
            example_usage="brain status",
        ),
        handle_brain_status,
    )

    registry.register_command(
        CommandMetadata(
            name="brain",
            description="Runs a multi-skill query or objective through the Brain orchestrator.",
            category=CommandCategory.CLI,
            required_agent="None",
            required_tools=[],
            example_usage="brain clone repository Anzar0904/aios and get status",
        ),
        handle_brain_execute,
    )


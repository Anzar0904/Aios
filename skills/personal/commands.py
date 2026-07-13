import time

from aios.services.command.metadata import CommandCategory, CommandMetadata
from aios.services.personal import (
    Contact,
    Goal,
    KnowledgeEntry,
    LearningItem,
    PersonalProfile,
    PersonalService,
    PortfolioProject,
    Preference,
    Resume,
    ResumeVersion,
    Template,
)


def execute_profile_show(args: str, kernel, conv_manager) -> None:
    try:
        personal_svc = kernel.registry.get(PersonalService)
        profile = personal_svc.get_active_profile()
        if not profile:
            print("No active profile found.")
            return

        print(f"\n=== Active Personal Profile: {profile.name} (ID: {profile.id}) ===")
        print(f" - Version: {profile.version}")
        print(f" - Contact Email: {profile.contact.email}")
        print(f" - Resumes count: {len(profile.resumes)}")
        print(f" - Portfolio count: {len(profile.portfolio)}")
        print(f" - Goals count: {len(profile.goals)}")
        print(f" - Learning items: {len(profile.learning)}")
    except Exception as e:
        print(f"Failed to show profile: {str(e)}")


def execute_profile_list(args: str, kernel, conv_manager) -> None:
    try:
        personal_svc = kernel.registry.get(PersonalService)
        profiles = personal_svc.list_profiles()
        active = personal_svc.get_active_profile()
        print("\n=== Registered Profiles ===")
        for p in profiles:
            star = "*" if active and active.id == p else " "
            print(f" {star} {p}")
    except Exception as e:
        print(f"Failed to list profiles: {str(e)}")


def execute_profile_create(args: str, kernel, conv_manager) -> None:
    pid = args.strip()
    if not pid:
        print("Usage: profile create <profile_id>")
        return

    try:
        personal_svc = kernel.registry.get(PersonalService)
        profile = PersonalProfile(
            id=pid,
            name=f"New {pid.capitalize()} Profile",
            contact=Contact(email="new_profile@example.com")
        )
        personal_svc.create_profile(profile)
        print(f"Profile '{pid}' successfully created.")
    except Exception as e:
        print(f"Failed to create profile: {str(e)}")


def execute_profile_switch(args: str, kernel, conv_manager) -> None:
    pid = args.strip()
    if not pid:
        print("Usage: profile switch <profile_id>")
        return

    try:
        personal_svc = kernel.registry.get(PersonalService)
        success = personal_svc.switch_active_profile(pid)
        if success:
            print(f"Switched active profile to '{pid}'.")
        else:
            print(f"Profile '{pid}' not found.")
    except Exception as e:
        print(f"Failed to switch profile: {str(e)}")


def execute_profile_update(args: str, kernel, conv_manager) -> None:
    name = args.strip()
    if not name:
        print("Usage: profile update <name>")
        return

    try:
        personal_svc = kernel.registry.get(PersonalService)
        profile = personal_svc.get_active_profile()
        if not profile:
            print("No active profile.")
            return

        profile.name = name
        personal_svc.update_profile(profile.id, profile)
        print(f"Profile updated successfully. New Name: {name}, New Version: {profile.version}")
    except Exception as e:
        print(f"Failed to update profile: {str(e)}")


def execute_profile_delete(args: str, kernel, conv_manager) -> None:
    pid = args.strip()
    if not pid:
        print("Usage: profile delete <profile_id>")
        return

    try:
        personal_svc = kernel.registry.get(PersonalService)
        success = personal_svc.delete_profile(pid)
        if success:
            print(f"Profile '{pid}' deleted successfully.")
        else:
            print(f"Profile '{pid}' not found.")
    except Exception as e:
        print(f"Failed to delete profile: {str(e)}")


def execute_resume_create(args: str, kernel, conv_manager) -> None:
    title = args.strip()
    if not title:
        print("Usage: resume create <title>")
        return

    try:
        personal_svc = kernel.registry.get(PersonalService)
        profile = personal_svc.get_active_profile()
        if not profile:
            print("No active profile.")
            return

        new_res = Resume(
            id=f"res_{int(time.time())}",
            title=title,
            versions=[ResumeVersion(version=1, summary="Dynamic professional summary.", created_at=time.time())]
        )
        profile.resumes.append(new_res)
        personal_svc.update_profile(profile.id, profile)
        print(f"Resume '{title}' created successfully under active profile '{profile.id}'.")
    except Exception as e:
        print(f"Failed to create resume: {str(e)}")


def execute_resume_optimize(args: str, kernel, conv_manager) -> None:
    print("Optimizing resume layout for target roles...")


def execute_resume_versions(args: str, kernel, conv_manager) -> None:
    print("Listing resume historical versions...")


def execute_resume_compare(args: str, kernel, conv_manager) -> None:
    print("Comparing resume versions...")


def execute_portfolio_list(args: str, kernel, conv_manager) -> None:
    try:
        personal_svc = kernel.registry.get(PersonalService)
        profile = personal_svc.get_active_profile()
        if not profile or not profile.portfolio:
            print("Portfolio is empty.")
            return

        print("\n=== Portfolio Projects ===")
        for p in profile.portfolio:
            print(f" - {p.name} (ID: {p.id}) | {p.description}")
    except Exception as e:
        print(f"Failed to list portfolio: {str(e)}")


def execute_portfolio_add(args: str, kernel, conv_manager) -> None:
    name = args.strip()
    if not name:
        print("Usage: portfolio add <name>")
        return

    try:
        personal_svc = kernel.registry.get(PersonalService)
        profile = personal_svc.get_active_profile()
        if not profile:
            return

        project = PortfolioProject(
            id=f"proj_{int(time.time())}",
            name=name,
            description="Add project description here."
        )
        profile.portfolio.append(project)
        personal_svc.update_profile(profile.id, profile)
        print(f"Portfolio project '{name}' added successfully.")
    except Exception as e:
        print(f"Failed to add portfolio: {str(e)}")


def execute_goal_add(args: str, kernel, conv_manager) -> None:
    title = args.strip()
    if not title:
        print("Usage: goal add <title>")
        return

    try:
        personal_svc = kernel.registry.get(PersonalService)
        profile = personal_svc.get_active_profile()
        if not profile:
            return

        new_goal = Goal(
            id=f"goal_{int(time.time())}",
            title=title,
            target_date="2026-12-31"
        )
        profile.goals.append(new_goal)
        personal_svc.update_profile(profile.id, profile)
        print(f"Goal '{title}' added successfully.")
    except Exception as e:
        print(f"Failed to add goal: {str(e)}")


def execute_goal_update(args: str, kernel, conv_manager) -> None:
    parts = args.strip().split()
    if len(parts) < 2:
        print("Usage: goal update <goal_id> <status>")
        return

    gid, status = parts[0], parts[1]
    try:
        personal_svc = kernel.registry.get(PersonalService)
        profile = personal_svc.get_active_profile()
        if not profile:
            return

        for g in profile.goals:
            if g.id == gid:
                g.status = status
                personal_svc.update_profile(profile.id, profile)
                print(f"Goal '{gid}' status updated to '{status}'.")
                return
        print(f"Goal '{gid}' not found.")
    except Exception as e:
        print(f"Failed to update goal: {str(e)}")


def execute_goal_list(args: str, kernel, conv_manager) -> None:
    try:
        personal_svc = kernel.registry.get(PersonalService)
        profile = personal_svc.get_active_profile()
        if not profile or not profile.goals:
            print("No goals set.")
            return

        print("\n=== Personal Goals ===")
        for g in profile.goals:
            print(f" - [{g.status.upper()}] {g.title} (ID: {g.id}) | Target: {g.target_date}")
    except Exception as e:
        print(f"Failed to list goals: {str(e)}")


def execute_learning_add(args: str, kernel, conv_manager) -> None:
    title = args.strip()
    if not title:
        print("Usage: learning add <title>")
        return

    try:
        personal_svc = kernel.registry.get(PersonalService)
        profile = personal_svc.get_active_profile()
        if not profile:
            return

        new_learn = LearningItem(
            id=f"learn_{int(time.time())}",
            title=title,
            source="Self Study"
        )
        profile.learning.append(new_learn)
        personal_svc.update_profile(profile.id, profile)
        print(f"Learning item '{title}' added successfully.")
    except Exception as e:
        print(f"Failed to add learning item: {str(e)}")


def execute_learning_progress(args: str, kernel, conv_manager) -> None:
    parts = args.strip().split()
    if len(parts) < 2:
        print("Usage: learning progress <item_id> <percentage>")
        return

    lid, progress = parts[0], float(parts[1])
    try:
        personal_svc = kernel.registry.get(PersonalService)
        profile = personal_svc.get_active_profile()
        if not profile:
            return

        for item in profile.learning:
            if item.id == lid:
                item.progress_percentage = progress
                if progress >= 100.0:
                    item.status = "completed"
                else:
                    item.status = "reading"
                personal_svc.update_profile(profile.id, profile)
                print(f"Learning item '{lid}' progress updated to {progress}%.")
                return
        print(f"Learning item '{lid}' not found.")
    except Exception as e:
        print(f"Failed to update progress: {str(e)}")


def execute_knowledge_add(args: str, kernel, conv_manager) -> None:
    title = args.strip()
    if not title:
        print("Usage: knowledge add <title>")
        return

    try:
        personal_svc = kernel.registry.get(PersonalService)
        profile = personal_svc.get_active_profile()
        if not profile:
            return

        new_k = KnowledgeEntry(
            id=f"k_{int(time.time())}",
            title=title,
            content="Add body content here.",
            updated_at=time.time()
        )
        profile.knowledge.append(new_k)
        personal_svc.update_profile(profile.id, profile)
        print(f"Knowledge entry '{title}' added successfully.")
    except Exception as e:
        print(f"Failed to add knowledge: {str(e)}")


def execute_knowledge_search(args: str, kernel, conv_manager) -> None:
    term = args.strip().lower()
    if not term:
        print("Usage: knowledge search <term>")
        return

    try:
        personal_svc = kernel.registry.get(PersonalService)
        profile = personal_svc.get_active_profile()
        if not profile or not profile.knowledge:
            print("No matching knowledge entries found.")
            return

        matched = [k for k in profile.knowledge if term in k.title.lower()]
        print(f"\n=== Search Results for '{term}' ===")
        if not matched:
            print("No matching entries found.")
            return
        for k in matched:
            print(f" - {k.title} (ID: {k.id})")
    except Exception as e:
        print(f"Search failed: {str(e)}")


def execute_preferences_show(args: str, kernel, conv_manager) -> None:
    try:
        personal_svc = kernel.registry.get(PersonalService)
        profile = personal_svc.get_active_profile()
        if not profile or not profile.preferences:
            print("No preferences defined.")
            return

        print("\n=== Personal Preferences ===")
        for p in profile.preferences:
            print(f" - {p.key}: {p.value} ({p.category})")
    except Exception as e:
        print(f"Failed to show preferences: {str(e)}")


def execute_preferences_update(args: str, kernel, conv_manager) -> None:
    parts = args.strip().split(maxsplit=1)
    if len(parts) < 2:
        print("Usage: preferences update <key> <value>")
        return

    key, value = parts[0], parts[1]
    try:
        personal_svc = kernel.registry.get(PersonalService)
        profile = personal_svc.get_active_profile()
        if not profile:
            return

        for p in profile.preferences:
            if p.key == key:
                p.value = value
                personal_svc.update_profile(profile.id, profile)
                print(f"Preference '{key}' updated to '{value}'.")
                return

        profile.preferences.append(Preference(key=key, value=value))
        personal_svc.update_profile(profile.id, profile)
        print(f"Preference '{key}' successfully added and set to '{value}'.")
    except Exception as e:
        print(f"Failed to update preferences: {str(e)}")


def execute_template_create(args: str, kernel, conv_manager) -> None:
    name = args.strip()
    if not name:
        print("Usage: template create <name>")
        return

    try:
        personal_svc = kernel.registry.get(PersonalService)
        profile = personal_svc.get_active_profile()
        if not profile:
            return

        new_t = Template(
            id=f"temp_{int(time.time())}",
            name=name,
            content="Add template body content."
        )
        profile.templates.append(new_t)
        personal_svc.update_profile(profile.id, profile)
        print(f"Template '{name}' created successfully.")
    except Exception as e:
        print(f"Failed to create template: {str(e)}")


def execute_template_list(args: str, kernel, conv_manager) -> None:
    try:
        personal_svc = kernel.registry.get(PersonalService)
        profile = personal_svc.get_active_profile()
        if not profile or not profile.templates:
            print("No templates defined.")
            return

        print("\n=== Templates ===")
        for t in profile.templates:
            print(f" - {t.name} (ID: {t.id}) | {t.category}")
    except Exception as e:
        print(f"Failed to list templates: {str(e)}")


def register_commands(registry, kernel, conv_manager) -> None:
    commands_map = {
        "profile show": execute_profile_show,
        "profile list": execute_profile_list,
        "profile create": execute_profile_create,
        "profile switch": execute_profile_switch,
        "profile update": execute_profile_update,
        "profile delete": execute_profile_delete,
        "resume create": execute_resume_create,
        "resume optimize": execute_resume_optimize,
        "resume versions": execute_resume_versions,
        "resume compare": execute_resume_compare,
        "portfolio list": execute_portfolio_list,
        "portfolio add": execute_portfolio_add,
        "project add": execute_portfolio_add,
        "project list": execute_portfolio_list,
        "goal add": execute_goal_add,
        "goal update": execute_goal_update,
        "goal list": execute_goal_list,
        "learning add": execute_learning_add,
        "learning progress": execute_learning_progress,
        "knowledge add": execute_knowledge_add,
        "knowledge search": execute_knowledge_search,
        "preferences show": execute_preferences_show,
        "preferences update": execute_preferences_update,
        "template create": execute_template_create,
        "template list": execute_template_list,
    }

    for name, handler in commands_map.items():
        registry.register_command(
            CommandMetadata(
                name=name,
                description=f"Command to perform {name} action on personal details.",
                category=CommandCategory.CLI,
                required_agent="None",
                required_tools=[],
                example_usage=f"{name} arguments",
            ),
            lambda args, h=handler: h(args, kernel, conv_manager),
        )

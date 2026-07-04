import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from aios.brain.context_manager import ContextManager
from aios.services.context import WorkspaceContext
from aios.services.personal import (
    Contact,
    PersonalProfile,
    Preference,
    Goal,
    LearningItem,
    PortfolioProject,
    Resume,
    ResumeVersion,
)
from aios.services.personal_impl import LocalPersonalService


def test_profile_crud_and_switching():
    with tempfile.TemporaryDirectory() as tmpdir:
        service = LocalPersonalService(cache_filename="profiles.json", workspace_root=tmpdir)
        service.initialize()

        # Check default profile created
        profiles = service.list_profiles()
        assert "professional" in profiles
        assert service.get_active_profile().name == "Default Developer"

        # Create new profile
        new_p = PersonalProfile(
            id="student",
            name="Alice Student",
            contact=Contact(email="alice@student.com")
        )
        service.create_profile(new_p)
        assert "student" in service.list_profiles()

        # Switch profile
        assert service.switch_active_profile("student") is True
        assert service.get_active_profile().name == "Alice Student"

        # Update profile and verify version increments
        active = service.get_active_profile()
        active.name = "Alice Grad Student"
        service.update_profile(active.id, active)
        
        updated = service.get_profile("student")
        assert updated.name == "Alice Grad Student"
        assert updated.version == 2

        # Delete profile
        assert service.delete_profile("student") is True
        assert "student" not in service.list_profiles()


def test_resume_and_portfolio_helpers():
    with tempfile.TemporaryDirectory() as tmpdir:
        service = LocalPersonalService(cache_filename="profiles.json", workspace_root=tmpdir)
        service.initialize()

        profile = service.get_active_profile()
        
        # Add Resume
        resume = Resume(
            id="res-1",
            title="Python Dev Resume",
            versions=[ResumeVersion(version=1, summary="Python Specialist Summary")]
        )
        profile.resumes.append(resume)
        
        # Add Portfolio Project
        project = PortfolioProject(
            id="proj-1",
            name="Personal AI OS",
            description="Agentic OS using Python",
            technologies=["Python", "pytest"]
        )
        profile.portfolio.append(project)

        service.update_profile(profile.id, profile)

        # Retrieve and verify
        updated = service.get_active_profile()
        assert len(updated.resumes) == 1
        assert updated.resumes[0].title == "Python Dev Resume"
        assert len(updated.portfolio) == 1
        assert updated.portfolio[0].name == "Personal AI OS"


def test_intelligent_context_selection():
    with tempfile.TemporaryDirectory() as tmpdir:
        service = LocalPersonalService(cache_filename="profiles.json", workspace_root=tmpdir)
        service.initialize()

        profile = service.get_active_profile()
        profile.resumes.append(Resume(id="r1", title="Job CV"))
        profile.goals.append(Goal(id="g1", title="Learn Go", target_date="2026-12-31"))
        profile.portfolio.append(PortfolioProject(id="p1", name="Project Alpha", description="Description"))
        service.update_profile(profile.id, profile)

        # 1. Career query
        ctx_career = service.get_relevant_context("Optimize my resume for Python jobs")
        assert "resumes" in ctx_career
        assert "goals" not in ctx_career
        assert "portfolio" not in ctx_career

        # 2. Learning query
        ctx_learning = service.get_relevant_context("What are my personal goals for this quarter?")
        assert "goals" in ctx_learning
        assert "resumes" not in ctx_learning
        assert "portfolio" not in ctx_learning

        # 3. Project query
        ctx_project = service.get_relevant_context("List my portfolio repositories and build files")
        assert "portfolio" in ctx_project
        assert "resumes" not in ctx_project
        assert "goals" not in ctx_project


def test_context_manager_personal_integration():
    context_service = MagicMock()
    memory_service = MagicMock()
    personal_service = MagicMock()

    workspace_ctx = WorkspaceContext(
        working_directory="/tmp/test_workspace",
        git_repo_path="/tmp/test_workspace/.git",
        git_branch="main",
        project_root="/tmp/test_workspace",
        project_name="test_proj"
    )
    context_service.get_current_context.return_value = workspace_ctx
    memory_service.search_memory.return_value = []

    mock_personal_ctx = {"name": "Alice", "preferences": []}
    personal_service.get_relevant_context.return_value = mock_personal_ctx

    manager = ContextManager(
        context_service=context_service,
        memory_service=memory_service,
        project_intel=None,
        dev_workspace=None,
        personal_service=personal_service
    )
    
    assembled = manager.assemble_context("Optimize my CV")
    assert assembled.extra.get("personal_intelligence") == mock_personal_ctx
    personal_service.get_relevant_context.assert_called_once_with("Optimize my CV")

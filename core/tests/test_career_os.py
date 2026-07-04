import json
import time
import pytest
from unittest.mock import MagicMock, patch

from aios.services.model import ModelService, LLMRequest, LLMResponse
from aios.services.personal import PersonalService, PersonalProfile, Contact, CareerProfile, Resume, ResumeVersion, Goal, Experience, ProjectReference
from aios.services.github import GitHubService, GitHubRepository
from aios.services.career import JobApplication
from aios.services.career_impl import (
    LocalCareerOSService,
    LocalCareerProfileManager,
    LocalJobAnalyzer,
    LocalResumeOptimizer,
    LocalATSAnalyzer,
    LocalCoverLetterGenerator,
    LocalPortfolioAnalyzer,
    LocalApplicationTracker,
    LocalInterviewCoach,
    LocalCareerPlanner,
    LocalJobMatcher,
)


@pytest.fixture
def mock_model_service():
    service = MagicMock(spec=ModelService)
    # Set default mock response content
    response = LLMResponse(
        content="{}",
        model_name="mock-model",
        provider_name="mock-provider",
    )
    service.execute_request.return_value = response
    return service


@pytest.fixture
def mock_personal_service():
    service = MagicMock(spec=PersonalService)
    profile = PersonalProfile(
        id="professional",
        name="John Doe",
        contact=Contact(email="john@doe.com"),
        career=CareerProfile(
            industry="Software Engineering",
            current_role="Senior Dev",
            years_experience=5.0,
            target_roles=["Engineering Manager", "Tech Lead"],
        ),
        goals=[Goal(id="g_1", title="Transition to Management", target_date="2026-12-31")],
        knowledge=[],
    )
    service.get_active_profile.return_value = profile
    return service


@pytest.fixture
def mock_github_service():
    service = MagicMock(spec=GitHubService)
    repo = GitHubRepository(
        owner="JohnDoe",
        name="SmartProject",
        description="An AI project",
        url="https://github.com/JohnDoe/SmartProject",
        stars=10,
        forks=2,
    )
    service.search_repositories.return_value = [repo]
    service.get_repository_stats.return_value = {"stars": 12, "forks": 3}
    return service


def test_career_profile_manager(mock_personal_service):
    manager = LocalCareerProfileManager(mock_personal_service)
    prof = manager.get_career_profile()
    assert prof is not None
    assert prof.industry == "Software Engineering"

    new_prof = CareerProfile(
        industry="Management", current_role="Director", years_experience=10.0, target_roles=["VP"]
    )
    manager.update_career_profile(new_prof)
    mock_personal_service.update_profile.assert_called_once()
    assert mock_personal_service.get_active_profile().career.industry == "Management"


def test_job_analyzer(mock_model_service, mock_personal_service):
    analyzer = LocalJobAnalyzer(mock_model_service, mock_personal_service)
    
    mock_model_service.execute_request.return_value = LLMResponse(
        content=json.dumps({
            "required_skills": ["Python", "System Design"],
            "preferred_technologies": ["Kubernetes"],
            "estimated_ats_keywords": ["Python Developer"],
            "match_score": 85,
            "recommended_improvements": ["Add Kubernetes cert"],
        }),
        model_name="mock-model",
        provider_name="mock-provider",
    )

    res = analyzer.analyze_job("Looking for a Senior Python Dev with Kubernetes expertise.")
    assert res["match_score"] == 85
    assert "System Design" in res["required_skills"]
    assert "Add Kubernetes cert" in res["recommended_improvements"]


def test_resume_optimizer_tailoring(mock_model_service, mock_personal_service):
    optimizer = LocalResumeOptimizer(mock_model_service, mock_personal_service)
    
    mock_model_service.execute_request.return_value = LLMResponse(
        content=json.dumps({
            "summary": "Tailored senior profile with strong focus on Kubernetes and python.",
            "tailored_experiences": ["Enhanced Python backend services scaling up to 10M requests."],
            "suggested_project_ordering": ["SmartProject"],
        }),
        model_name="mock-model",
        provider_name="mock-provider",
    )

    resume = Resume(
        id="res_1",
        title="Software Dev Resume",
        versions=[
            ResumeVersion(
                version=1,
                summary="Base dev summary",
                experiences=[],
                projects=[ProjectReference(name="SmartProject", description="AI project")],
            )
        ]
    )

    new_version = optimizer.tailor_resume(resume, "Senior python dev role description.")
    assert new_version.version == 2
    assert "Kubernetes" in new_version.summary
    assert new_version.projects[0].name == "SmartProject"


def test_resume_optimizer_ats_keywords(mock_model_service, mock_personal_service):
    optimizer = LocalResumeOptimizer(mock_model_service, mock_personal_service)
    
    mock_model_service.execute_request.return_value = LLMResponse(
        content=json.dumps({
            "summary": "Optimized summary with Kubernetes",
            "optimized_descriptions": ["Worked on Kubernetes scaling deployments"],
        }),
        model_name="mock-model",
        provider_name="mock-provider",
    )

    base_version = ResumeVersion(
        version=1,
        summary="Plain Summary",
        experiences=[Experience(company="Google", role="Engineer", start_date="2020", description="Plain experience")],
    )

    res = optimizer.optimize_ats(base_version, ["Kubernetes"])
    assert res.summary == "Optimized summary with Kubernetes"
    assert res.experiences[0].description == "Worked on Kubernetes scaling deployments"


def test_ats_analyzer(mock_model_service):
    analyzer = LocalATSAnalyzer(mock_model_service)
    
    mock_model_service.execute_request.return_value = LLMResponse(
        content=json.dumps({
            "ats_score": 90,
            "matched_keywords": ["Python"],
            "missing_keywords": ["Docker"],
            "recommendations": ["Add Docker project details"],
        }),
        model_name="mock-model",
        provider_name="mock-provider",
    )

    version = ResumeVersion(version=1, summary="Python Engineer with experience")
    res = analyzer.score_resume_against_job(version, "Require Python and Docker skills.")
    assert res["ats_score"] == 90
    assert "Docker" in res["missing_keywords"]


def test_cover_letter_generator(mock_model_service):
    generator = LocalCoverLetterGenerator(mock_model_service)
    
    mock_model_service.execute_request.return_value = LLMResponse(
        content="Dear Hiring Manager, this is my cover letter.",
        model_name="mock-model",
        provider_name="mock-provider",
    )

    version = ResumeVersion(version=1, summary="Expert Dev")
    letter = generator.generate_cover_letter(version, "Dev role at Microsoft")
    assert "Dear Hiring Manager" in letter


def test_portfolio_analyzer(mock_model_service, mock_github_service):
    analyzer = LocalPortfolioAnalyzer(mock_model_service, mock_github_service)
    
    mock_model_service.execute_request.return_value = LLMResponse(
        content=json.dumps({
            "strongest_work": ["SmartProject"],
            "ranked_projects": ["SmartProject"],
            "readme_improvements": ["Add install script section"],
            "documentation_gaps": ["No API docs found"],
            "portfolio_summary_description": "Strong developer focusing on AI.",
        }),
        model_name="mock-model",
        provider_name="mock-provider",
    )

    res = analyzer.analyze_portfolio("JohnDoe")
    assert "SmartProject" in res["strongest_work"]
    assert "No API docs found" in res["documentation_gaps"]


def test_application_tracker(mock_personal_service):
    tracker = LocalApplicationTracker(mock_personal_service)
    assert len(tracker.list_applications()) == 0

    app = JobApplication(
        id="app_test",
        company="Hooli",
        role="Middle Manager",
        status="applied",
        applied_date="2026-07-04",
        notes="Nice interview prep",
    )
    tracker.add_application(app)
    
    apps = tracker.list_applications()
    assert len(apps) == 1
    assert apps[0].company == "Hooli"

    tracker.update_application_status("app_test", "interview")
    apps_updated = tracker.list_applications()
    assert apps_updated[0].status == "interview"


def test_interview_coach(mock_model_service):
    coach = LocalInterviewCoach(mock_model_service)
    
    mock_model_service.execute_request.return_value = LLMResponse(
        content=json.dumps({
            "company_prep": "Value speed and scalability",
            "weakness_analysis": "Focus on high throughput design patterns",
            "learning_roadmap": ["Step 1: scale-out design", "Step 2: microservices"],
        }),
        model_name="mock-model",
        provider_name="mock-provider",
    )

    prep = coach.prepare_interview("Netflix", "Senior Distributed Systems Engineer")
    assert "scale-out design" in prep["learning_roadmap"][0]

    # Generate questions mock
    mock_model_service.execute_request.return_value = LLMResponse(
        content=json.dumps(["How do you design a key-value store?", "Explain Paxos."]),
        model_name="mock-model",
        provider_name="mock-provider",
    )
    questions = coach.generate_questions("Tech Lead", "technical")
    assert len(questions) == 2
    assert "Explain Paxos." in questions


def test_career_planner(mock_model_service, mock_personal_service):
    planner = LocalCareerPlanner(mock_model_service, mock_personal_service)
    
    mock_model_service.execute_request.return_value = LLMResponse(
        content=json.dumps({
            "evaluated_goals": "Target date is realistic",
            "missing_skills_analysis": "Needs leadership training",
            "career_alternatives": ["Product Manager", "Architect"],
            "growth_milestones": ["Get cert", "Lead project"],
            "estimated_impact": 95,
        }),
        model_name="mock-model",
        provider_name="mock-provider",
    )

    plan = planner.generate_plan()
    assert plan["estimated_impact"] == 95
    assert "Product Manager" in plan["career_alternatives"]


def test_job_matcher(mock_model_service, mock_personal_service):
    matcher = LocalJobMatcher(mock_model_service, mock_personal_service)
    
    mock_model_service.execute_request.return_value = LLMResponse(
        content=json.dumps({
            "score": 90,
            "matched": ["System Design"],
            "gap": ["None"],
            "recommended_action": "Apply now!",
        }),
        model_name="mock-model",
        provider_name="mock-provider",
    )

    res = matcher.match_jobs(["Require System Design expert"])
    assert res[0]["score"] == 90


def test_career_os_service_unified_creation(
    mock_model_service, mock_personal_service, mock_github_service
):
    service = LocalCareerOSService(
        model_service=mock_model_service,
        personal_service=mock_personal_service,
        github_service=mock_github_service,
    )
    service.initialize()
    service.start()
    service.stop()

    assert service.profile_manager is not None
    assert service.job_analyzer is not None
    assert service.resume_optimizer is not None
    assert service.ats_analyzer is not None
    assert service.cover_letter_generator is not None
    assert service.portfolio_analyzer is not None
    assert service.application_tracker is not None
    assert service.interview_coach is not None
    assert service.career_planner is not None
    assert service.job_matcher is not None

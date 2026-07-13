import json
import logging
import time
from typing import Any, Dict, List, Optional

from aios.services.career import (
    ApplicationTracker,
    ATSAnalyzer,
    CareerOSService,
    CareerPlanner,
    CareerProfileManager,
    CoverLetterGenerator,
    InterviewCoach,
    JobAnalyzer,
    JobApplication,
    JobMatcher,
    PortfolioAnalyzer,
    ResumeOptimizer,
)
from aios.services.github import GitHubService
from aios.services.model import LLMRequest, ModelService
from aios.services.n8n import N8NService
from aios.services.personal import (
    CareerProfile,
    Experience,
    PersonalService,
    Resume,
    ResumeVersion,
)
from aios.services.project_intelligence import ProjectIntelligenceService

logger = logging.getLogger(__name__)


class LocalCareerProfileManager(CareerProfileManager):
    def __init__(self, personal_service: PersonalService) -> None:
        self._personal = personal_service

    def get_career_profile(self) -> Optional[CareerProfile]:
        profile = self._personal.get_active_profile()
        if profile:
            return profile.career
        return None

    def update_career_profile(self, profile: CareerProfile) -> None:
        active = self._personal.get_active_profile()
        if active:
            active.career = profile
            active.version += 1
            self._personal.update_profile(active.id, active)


class LocalJobAnalyzer(JobAnalyzer):
    def __init__(self, model_service: ModelService, personal_service: PersonalService) -> None:
        self._model = model_service
        self._personal = personal_service

    def analyze_job(self, job_description: str) -> Dict[str, Any]:
        profile = self._personal.get_active_profile()
        skills_str = ""
        if profile and profile.career:
            skills_str = f"User Target Roles: {profile.career.target_roles}"

        prompt = (
            f"You are a Job Requirements Analyst. Analyze this job description:\n\n"
            f"{job_description}\n\n"
            f"User Profile details:\n{skills_str}\n\n"
            "Analyze and output as a JSON dictionary (do not include markdown block formatting, output pure JSON) with keys:\n"
            "- required_skills: list of key required skills\n"
            "- preferred_technologies: list of technologies\n"
            "- estimated_ats_keywords: list of ATS keywords\n"
            "- match_score: score from 0 to 100 relative to user targets\n"
            "- recommended_improvements: list of suggestions"
        )

        res = self._model.execute_request(
            LLMRequest(
                prompt=prompt,
                system_instruction="You are a precise technical recruiter. Output pure JSON only.",
                task_category="career",
                preferences={"JSON_output": True},
            )
        )
        try:
            content = res.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content)
        except Exception as e:
            logger.error(f"Error parsing JobAnalyzer JSON response: {e}")
            return {
                "required_skills": [],
                "preferred_technologies": [],
                "estimated_ats_keywords": [],
                "match_score": 50,
                "recommended_improvements": [f"Could not parse analysis: {e}"],
            }


class LocalResumeOptimizer(ResumeOptimizer):
    def __init__(self, model_service: ModelService, personal_service: PersonalService) -> None:
        self._model = model_service
        self._personal = personal_service

    def tailor_resume(self, resume: Resume, job_description: str) -> ResumeVersion:
        base_version = None
        if resume.versions:
            base_version = resume.versions[-1]

        summary = ""
        experiences = []
        educations = []
        skills = []
        projects = []

        if base_version:
            summary = base_version.summary
            experiences = base_version.experiences
            educations = base_version.educations
            skills = base_version.skills
            projects = base_version.projects

        prompt = (
            f"You are a Career Resume Architect. Tailor the following resume details for this job:\n\n"
            f"Job Description:\n{job_description}\n\n"
            f"Current Summary: {summary}\n"
            f"Current Experiences: {experiences}\n"
            f"Current Projects: {projects}\n\n"
            "Please rewrite the professional summary and optimize the project bullet points/ordering to maximize ATS alignment.\n"
            "Output a JSON object (pure JSON, no markdown formatting) with keys:\n"
            "- summary: new professional summary\n"
            "- tailored_experiences: list of experiences descriptions updated\n"
            "- suggested_project_ordering: list of project titles in recommended order"
        )

        res = self._model.execute_request(
            LLMRequest(
                prompt=prompt,
                system_instruction="You are an expert resume writer. Output pure JSON.",
                task_category="career",
                preferences={"JSON_output": True},
            )
        )

        try:
            content = res.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            data = json.loads(content)

            new_summary = data.get("summary", summary)
            # Reorder projects if recommended
            new_projects = list(projects)
            order = data.get("suggested_project_ordering", [])
            if order:
                proj_map = {p.name: p for p in projects}
                ordered = []
                for o_name in order:
                    if o_name in proj_map:
                        ordered.append(proj_map[o_name])
                for p in projects:
                    if p not in ordered:
                        ordered.append(p)
                new_projects = ordered

            return ResumeVersion(
                version=len(resume.versions) + 1,
                summary=new_summary,
                experiences=experiences,
                educations=educations,
                skills=skills,
                projects=new_projects,
                created_at=time.time(),
            )
        except Exception as e:
            logger.error(f"Error tailoring resume: {e}")
            return ResumeVersion(
                version=len(resume.versions) + 1,
                summary=summary,
                experiences=experiences,
                educations=educations,
                skills=skills,
                projects=projects,
                created_at=time.time(),
            )

    def optimize_ats(self, resume_version: ResumeVersion, keywords: List[str]) -> ResumeVersion:
        prompt = (
            f"You are a Resume Keyword Optimizer. Add these keywords naturally into the summary and achievements:\n\n"
            f"Keywords: {keywords}\n\n"
            f"Summary: {resume_version.summary}\n"
            f"Experiences descriptions: {[exp.description for exp in resume_version.experiences]}\n\n"
            "Output a JSON object (pure JSON, no markdown formatting) with keys:\n"
            "- summary: optimized summary\n"
            "- optimized_descriptions: list of optimized experience descriptions matching original count"
        )
        res = self._model.execute_request(
            LLMRequest(
                prompt=prompt,
                system_instruction="Output pure JSON only.",
                task_category="career",
                preferences={"JSON_output": True},
            )
        )
        try:
            content = res.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            data = json.loads(content)

            new_experiences = []
            new_descriptions = data.get("optimized_descriptions", [])
            for idx, exp in enumerate(resume_version.experiences):
                desc = new_descriptions[idx] if idx < len(new_descriptions) else exp.description
                new_experiences.append(
                    Experience(
                        company=exp.company,
                        role=exp.role,
                        start_date=exp.start_date,
                        end_date=exp.end_date,
                        description=desc,
                    )
                )

            return ResumeVersion(
                version=resume_version.version,
                summary=data.get("summary", resume_version.summary),
                experiences=new_experiences,
                educations=resume_version.educations,
                skills=resume_version.skills,
                projects=resume_version.projects,
                created_at=time.time(),
            )
        except Exception:
            return resume_version


class LocalATSAnalyzer(ATSAnalyzer):
    def __init__(self, model_service: ModelService) -> None:
        self._model = model_service

    def score_resume_against_job(
        self, resume_version: ResumeVersion, job_description: str
    ) -> Dict[str, Any]:
        prompt = (
            f"You are an ATS Parser and Job Match Analyzer. Compare this resume version with the job details:\n\n"
            f"Resume Summary: {resume_version.summary}\n"
            f"Skills: {[s.skills for s in resume_version.skills]}\n\n"
            f"Job Description:\n{job_description}\n\n"
            "Score the resume alignment and output as a JSON object (pure JSON, no markdown formatting) with keys:\n"
            "- ats_score: 0-100 score\n"
            "- matched_keywords: list of matched keywords found\n"
            "- missing_keywords: list of missing key keywords\n"
            "- recommendations: list of improvements to achieve a higher score"
        )
        res = self._model.execute_request(
            LLMRequest(
                prompt=prompt,
                system_instruction="Output pure JSON only.",
                task_category="career",
                preferences={"JSON_output": True},
            )
        )
        try:
            content = res.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content)
        except Exception as e:
            return {
                "ats_score": 40,
                "matched_keywords": [],
                "missing_keywords": [],
                "recommendations": [f"Parsing failed: {e}"],
            }


class LocalCoverLetterGenerator(CoverLetterGenerator):
    def __init__(self, model_service: ModelService) -> None:
        self._model = model_service

    def generate_cover_letter(self, resume_version: ResumeVersion, job_description: str) -> str:
        prompt = (
            f"You are a Career Consultant. Draft a compelling cover letter matching this resume with the job description:\n\n"
            f"Resume Summary: {resume_version.summary}\n"
            f"Job Description:\n{job_description}\n\n"
            "Write a highly professional and tailored cover letter."
        )
        res = self._model.execute_request(
            LLMRequest(
                prompt=prompt,
                system_instruction="You are a professional cover letter writer.",
                task_category="career",
            )
        )
        return res.content


class LocalPortfolioAnalyzer(PortfolioAnalyzer):
    def __init__(self, model_service: ModelService, github_service: GitHubService) -> None:
        self._model = model_service
        self._github = github_service

    def analyze_portfolio(self, username: str) -> Dict[str, Any]:
        repos = self._github.search_repositories(f"user:{username}")
        repos_summary = []
        for r in repos[:5]:
            try:
                stats = self._github.get_repository_stats(f"{r.owner}/{r.name}")
                repos_summary.append(
                    {
                        "name": r.name,
                        "description": r.description,
                        "stars": stats.get("stars", 0),
                        "forks": stats.get("forks", 0),
                    }
                )
            except Exception:
                repos_summary.append(
                    {
                        "name": r.name,
                        "description": r.description,
                        "stars": 0,
                        "forks": 0,
                    }
                )

        prompt = (
            f"You are a Technical Portfolio Reviewer. Analyze these GitHub repositories:\n\n"
            f"{repos_summary}\n\n"
            "Assess repository strength and produce a JSON object (pure JSON, no markdown formatting) with keys:\n"
            "- strongest_work: list of repository names that show the highest code quality/complexity\n"
            "- ranked_projects: list of repositories ranked by overall strength\n"
            "- readme_improvements: list of suggestions for improving repository READMEs\n"
            "- documentation_gaps: list of missing documentations detected\n"
            "- portfolio_summary_description: a short summary of the user's software engineering strengths"
        )
        res = self._model.execute_request(
            LLMRequest(
                prompt=prompt,
                system_instruction="Output pure JSON only.",
                task_category="career",
                preferences={"JSON_output": True},
            )
        )
        try:
            content = res.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content)
        except Exception as e:
            return {
                "strongest_work": [],
                "ranked_projects": [],
                "readme_improvements": [],
                "documentation_gaps": [],
                "portfolio_summary_description": f"Failed to analyze portfolio: {e}",
            }


class LocalApplicationTracker(ApplicationTracker):
    def __init__(self, personal_service: PersonalService) -> None:
        self._personal = personal_service

    def _get_applications(self) -> List[JobApplication]:
        profile = self._personal.get_active_profile()
        if not profile:
            return []
        apps_data = (
            profile.knowledge
        )  # we can save applications dynamically inside profile knowledge tags or extra fields
        # Look for a specific entry labeled 'applications'
        for entry in apps_data:
            if entry.id == "applications_tracker":
                try:
                    loaded = json.loads(entry.content)
                    return [
                        JobApplication(
                            id=item["id"],
                            company=item["company"],
                            role=item["role"],
                            status=item["status"],
                            applied_date=item["applied_date"],
                            interview_date=item.get("interview_date"),
                            offer_details=item.get("offer_details"),
                            notes=item.get("notes", ""),
                        )
                        for item in loaded
                    ]
                except Exception:
                    return []
        return []

    def _save_applications(self, apps: List[JobApplication]) -> None:
        profile = self._personal.get_active_profile()
        if not profile:
            return

        serializable = [
            {
                "id": app.id,
                "company": app.company,
                "role": app.role,
                "status": app.status,
                "applied_date": app.applied_date,
                "interview_date": app.interview_date,
                "offer_details": app.offer_details,
                "notes": app.notes,
            }
            for app in apps
        ]

        from aios.services.personal import KnowledgeEntry

        new_entry = KnowledgeEntry(
            id="applications_tracker",
            title="Applications Tracker History",
            content=json.dumps(serializable),
            tags=["career", "tracker"],
            updated_at=time.time(),
        )

        # Replace existing or append
        replaced = False
        for idx, entry in enumerate(profile.knowledge):
            if entry.id == "applications_tracker":
                profile.knowledge[idx] = new_entry
                replaced = True
                break
        if not replaced:
            profile.knowledge.append(new_entry)

        profile.version += 1
        self._personal.update_profile(profile.id, profile)

    def add_application(self, app: JobApplication) -> None:
        apps = self._get_applications()
        apps.append(app)
        self._save_applications(apps)

    def update_application_status(self, app_id: str, status: str) -> None:
        apps = self._get_applications()
        for app in apps:
            if app.id == app_id:
                app.status = status
                break
        self._save_applications(apps)

    def list_applications(self) -> List[JobApplication]:
        return self._get_applications()


class LocalInterviewCoach(InterviewCoach):
    def __init__(self, model_service: ModelService) -> None:
        self._model = model_service

    def prepare_interview(self, company: str, role: str) -> Dict[str, Any]:
        prompt = (
            f"You are an Interview Prep Coach. Prepare the user for a {role} interview at {company}.\n\n"
            "Generate a prep report including company-specific prep, weaknesses to address, and a study roadmap.\n"
            "Output as a JSON object (pure JSON, no markdown formatting) with keys:\n"
            "- company_prep: guidelines about what the company values\n"
            "- weakness_analysis: key tech/interview gaps to address\n"
            "- learning_roadmap: step-by-step prep checklist"
        )
        res = self._model.execute_request(
            LLMRequest(
                prompt=prompt,
                system_instruction="Output pure JSON only.",
                task_category="career",
                preferences={"JSON_output": True},
            )
        )
        try:
            content = res.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content)
        except Exception as e:
            return {
                "company_prep": "Failed to load",
                "weakness_analysis": "Failed to load",
                "learning_roadmap": [f"Error: {e}"],
            }

    def generate_questions(self, role: str, category: str) -> List[str]:
        prompt = (
            f"You are an Interview Examiner. Generate 5 interview questions for a {role} role.\n\n"
            f"Category: {category} (e.g. technical, behavioral, system design, coding)\n\n"
            "Output as a JSON list of strings (pure JSON, no markdown formatting)."
        )
        res = self._model.execute_request(
            LLMRequest(
                prompt=prompt,
                system_instruction="Output pure JSON list only.",
                task_category="career",
                preferences={"JSON_output": True},
            )
        )
        try:
            content = res.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            return json.loads(content)
        except Exception:
            return [
                "Tell me about a time you resolved a tech challenge.",
                "Explain how virtual memory works.",
            ]


class LocalCareerPlanner(CareerPlanner):
    def __init__(
        self,
        model_service: ModelService,
        personal_service: PersonalService,
        registry: Optional[Any] = None,
    ) -> None:
        self._model = model_service
        self._personal = personal_service
        self._registry = registry

    def generate_plan(self) -> Dict[str, Any]:
        profile = self._personal.get_active_profile()
        goals = [g.title for g in profile.goals] if profile else []
        skills = []
        if profile and profile.career:
            skills = profile.career.target_roles

        prompt = (
            f"You are a Career Growth Strategist. Review the user's profile details:\n\n"
            f"Goals: {goals}\n"
            f"Target Roles: {skills}\n\n"
            "Construct a professional growth plan evaluating goals, missing skills, alternatives, and impact estimations.\n"
            "Output as a JSON object (pure JSON, no markdown formatting) with keys:\n"
            "- evaluated_goals: details of goal alignment\n"
            "- missing_skills_analysis: identified skill gaps\n"
            "- career_alternatives: recommended alternative titles\n"
            "- growth_milestones: step-by-step milestone checklist\n"
            "- estimated_impact: predicted profile strength improvement (0-100)"
        )
        res = self._model.execute_request(
            LLMRequest(
                prompt=prompt,
                system_instruction="Output pure JSON only.",
                task_category="career",
                preferences={"JSON_output": True},
            )
        )
        plan = {
            "evaluated_goals": "Failed to parse growth plan",
            "missing_skills_analysis": "Failed to parse",
            "career_alternatives": [],
            "growth_milestones": [],
            "estimated_impact": 0,
        }
        try:
            content = res.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            plan = json.loads(content)
        except Exception as e:
            plan["growth_milestones"] = [f"Error: {e}"]

        # Synchronize with Knowledge Hub
        try:
            from aios.services.knowledge_hub import (
                KnowledgeDocument,
                KnowledgeHubService,
                KnowledgeMetadata,
            )

            knowledge_hub = self._registry.get(KnowledgeHubService) if self._registry else None
            if knowledge_hub:
                md_content = f"# Career Growth Plan\n\n## Missing Skills Analysis\n{plan.get('missing_skills_analysis')}\n\n## Growth Milestones\n"
                for m in plan.get("growth_milestones", []):
                    md_content += f"- {m}\n"

                doc = KnowledgeDocument(
                    document_id=f"career_plan_{int(time.time())}",
                    title="Career Growth Plan",
                    content=md_content,
                    metadata=KnowledgeMetadata(
                        unique_id=f"career_plan_{int(time.time())}",
                        timestamp=time.time(),
                        source_subsystem="career_os",
                        category="Career",
                    ),
                )
                knowledge_hub.sync_document(doc, "notion")
        except Exception:
            pass

        return plan


class LocalJobMatcher(JobMatcher):
    def __init__(self, model_service: ModelService, personal_service: PersonalService) -> None:
        self._model = model_service
        self._personal = personal_service

    def match_jobs(self, jobs: List[str]) -> List[Dict[str, Any]]:
        profile = self._personal.get_active_profile()
        skills = []
        if profile and profile.career:
            skills = profile.career.target_roles

        results = []
        for _idx, job in enumerate(jobs):
            prompt = (
                f"You are a Match Scoring Engine. Evaluate alignment of this job description with target skills:\n\n"
                f"Job: {job}\n\n"
                f"Target Skills: {skills}\n\n"
                "Return a JSON object (pure JSON, no markdown formatting) with keys:\n"
                "- score: 0-100 match rating\n"
                "- matched: list of matching skills\n"
                "- gap: list of missing elements\n"
                "- recommended_action: short action recommendation"
            )
            res = self._model.execute_request(
                LLMRequest(
                    prompt=prompt,
                    system_instruction="Output pure JSON only.",
                    task_category="career",
                    preferences={"JSON_output": True},
                )
            )
            try:
                content = res.content.strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                results.append(json.loads(content))
            except Exception:
                results.append(
                    {
                        "score": 50,
                        "matched": [],
                        "gap": ["parsing issue"],
                        "recommended_action": "Check job details manually",
                    }
                )
        return results


class LocalCareerOSService(CareerOSService):
    """Unified service implementation coordinating all Career OS modules."""

    def __init__(
        self,
        model_service: ModelService,
        personal_service: PersonalService,
        github_service: GitHubService,
        project_intel: Optional[ProjectIntelligenceService] = None,
        n8n_service: Optional[N8NService] = None,
        registry: Optional[Any] = None,
    ) -> None:
        self._model = model_service
        self._personal = personal_service
        self._github = github_service
        self._project_intel = project_intel
        self._n8n = n8n_service
        self._registry = registry

        # Initialize subcomponents
        self._profile_manager = LocalCareerProfileManager(personal_service)
        self._job_analyzer = LocalJobAnalyzer(model_service, personal_service)
        self._resume_optimizer = LocalResumeOptimizer(model_service, personal_service)
        self._ats_analyzer = LocalATSAnalyzer(model_service)
        self._cover_letter_generator = LocalCoverLetterGenerator(model_service)
        self._portfolio_analyzer = LocalPortfolioAnalyzer(model_service, github_service)
        self._application_tracker = LocalApplicationTracker(personal_service)
        self._interview_coach = LocalInterviewCoach(model_service)
        self._career_planner = LocalCareerPlanner(model_service, personal_service, registry)
        self._job_matcher = LocalJobMatcher(model_service, personal_service)

    def initialize(self) -> None:
        logger.info("Initializing LocalCareerOSService")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    @property
    def profile_manager(self) -> CareerProfileManager:
        return self._profile_manager

    @property
    def job_analyzer(self) -> JobAnalyzer:
        return self._job_analyzer

    @property
    def resume_optimizer(self) -> ResumeOptimizer:
        return self._resume_optimizer

    @property
    def ats_analyzer(self) -> ATSAnalyzer:
        return self._ats_analyzer

    @property
    def cover_letter_generator(self) -> CoverLetterGenerator:
        return self._cover_letter_generator

    @property
    def portfolio_analyzer(self) -> PortfolioAnalyzer:
        return self._portfolio_analyzer

    @property
    def application_tracker(self) -> ApplicationTracker:
        return self._application_tracker

    @property
    def interview_coach(self) -> InterviewCoach:
        return self._interview_coach

    @property
    def career_planner(self) -> CareerPlanner:
        return self._career_planner

    @property
    def job_matcher(self) -> JobMatcher:
        return self._job_matcher

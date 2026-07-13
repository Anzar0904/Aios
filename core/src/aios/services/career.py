import abc
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle
from aios.services.personal import CareerProfile, Resume, ResumeVersion


@dataclass
class JobApplication:
    id: str
    company: str
    role: str
    status: str  # applied, interview, offer, rejected
    applied_date: str
    interview_date: Optional[str] = None
    offer_details: Optional[str] = None
    notes: str = ""


class CareerProfileManager(abc.ABC):
    @abc.abstractmethod
    def get_career_profile(self) -> Optional[CareerProfile]:
        """Get the user's active career profile details."""
        pass

    @abc.abstractmethod
    def update_career_profile(self, profile: CareerProfile) -> None:
        """Update active career profile settings."""
        pass


class JobAnalyzer(abc.ABC):
    @abc.abstractmethod
    def analyze_job(self, job_description: str) -> Dict[str, Any]:
        """Extract requirements, required skills, preferred technologies, and ATS keywords."""
        pass


class ResumeOptimizer(abc.ABC):
    @abc.abstractmethod
    def tailor_resume(self, resume: Resume, job_description: str) -> ResumeVersion:
        """Create a tailored ResumeVersion for a target job description."""
        pass

    @abc.abstractmethod
    def optimize_ats(self, resume_version: ResumeVersion, keywords: List[str]) -> ResumeVersion:
        """Optimize ResumeVersion bullet points and keywords for target ATS list."""
        pass


class ATSAnalyzer(abc.ABC):
    @abc.abstractmethod
    def score_resume_against_job(
        self, resume_version: ResumeVersion, job_description: str
    ) -> Dict[str, Any]:
        """Evaluate match score, list found/missing keywords, and suggest improvements."""
        pass


class CoverLetterGenerator(abc.ABC):
    @abc.abstractmethod
    def generate_cover_letter(self, resume_version: ResumeVersion, job_description: str) -> str:
        """Generate a cover letter tailored to a target job and resume version."""
        pass


class PortfolioAnalyzer(abc.ABC):
    @abc.abstractmethod
    def analyze_portfolio(self, username: str) -> Dict[str, Any]:
        """Rank projects, recommend featured projects, and suggest documentation/README improvements."""
        pass


class ApplicationTracker(abc.ABC):
    @abc.abstractmethod
    def add_application(self, app: JobApplication) -> None:
        """Add a job application to tracking history."""
        pass

    @abc.abstractmethod
    def update_application_status(self, app_id: str, status: str) -> None:
        """Update status of a tracked job application."""
        pass

    @abc.abstractmethod
    def list_applications(self) -> List[JobApplication]:
        """List all tracked job applications."""
        pass


class InterviewCoach(abc.ABC):
    @abc.abstractmethod
    def prepare_interview(self, company: str, role: str) -> Dict[str, Any]:
        """Generate company prep materials, system design preparation, and weakness analysis."""
        pass

    @abc.abstractmethod
    def generate_questions(self, role: str, category: str) -> List[str]:
        """Generate technical, behavioral, system design, or coding questions."""
        pass


class CareerPlanner(abc.ABC):
    @abc.abstractmethod
    def generate_plan(self) -> Dict[str, Any]:
        """Analyze goals, missing skills, alternative career paths, and estimate impact."""
        pass


class JobMatcher(abc.ABC):
    @abc.abstractmethod
    def match_jobs(self, jobs: List[str]) -> List[Dict[str, Any]]:
        """Score multiple job descriptions against profile and recommend improvements."""
        pass


class CareerOSService(ServiceLifecycle, abc.ABC):
    """Unified service interface coordinating Career OS components."""

    @property
    @abc.abstractmethod
    def profile_manager(self) -> CareerProfileManager:
        pass

    @property
    @abc.abstractmethod
    def job_analyzer(self) -> JobAnalyzer:
        pass

    @property
    @abc.abstractmethod
    def resume_optimizer(self) -> ResumeOptimizer:
        pass

    @property
    @abc.abstractmethod
    def ats_analyzer(self) -> ATSAnalyzer:
        pass

    @property
    @abc.abstractmethod
    def cover_letter_generator(self) -> CoverLetterGenerator:
        pass

    @property
    @abc.abstractmethod
    def portfolio_analyzer(self) -> PortfolioAnalyzer:
        pass

    @property
    @abc.abstractmethod
    def application_tracker(self) -> ApplicationTracker:
        pass

    @property
    @abc.abstractmethod
    def interview_coach(self) -> InterviewCoach:
        pass

    @property
    @abc.abstractmethod
    def career_planner(self) -> CareerPlanner:
        pass

    @property
    @abc.abstractmethod
    def job_matcher(self) -> JobMatcher:
        pass

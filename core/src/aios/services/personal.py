import abc
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from aios.services.base import ServiceLifecycle


@dataclass
class Contact:
    email: str
    phone: str = ""
    location: str = ""


@dataclass
class SocialProfile:
    platform: str
    url: str


@dataclass
class Experience:
    company: str
    role: str
    start_date: str
    end_date: str = "Present"
    description: str = ""


@dataclass
class Education:
    institution: str
    degree: str
    field_of_study: str
    grad_date: str


@dataclass
class SkillProfile:
    category: str
    skills: List[str] = field(default_factory=list)


@dataclass
class ProjectReference:
    name: str
    description: str
    url: str = ""


@dataclass
class ResumeVersion:
    version: int
    summary: str
    experiences: List[Experience] = field(default_factory=list)
    educations: List[Education] = field(default_factory=list)
    skills: List[SkillProfile] = field(default_factory=list)
    projects: List[ProjectReference] = field(default_factory=list)
    created_at: float = 0.0


@dataclass
class Resume:
    id: str
    title: str
    versions: List[ResumeVersion] = field(default_factory=list)
    current_version: int = 1


@dataclass
class PortfolioProject:
    id: str
    name: str
    description: str
    technologies: List[str] = field(default_factory=list)
    repository_url: str = ""
    live_url: str = ""


@dataclass
class CareerProfile:
    industry: str
    current_role: str
    years_experience: float
    target_roles: List[str] = field(default_factory=list)


@dataclass
class Goal:
    id: str
    title: str
    target_date: str
    status: str = "pending"  # pending, in-progress, completed
    category: str = "career"


@dataclass
class LearningItem:
    id: str
    title: str
    source: str
    status: str = "not-started"  # not-started, reading, completed
    progress_percentage: float = 0.0


@dataclass
class Certificate:
    name: str
    issuing_organization: str
    issue_date: str
    credential_id: str = ""


@dataclass
class Achievement:
    title: str
    description: str
    date: str


@dataclass
class Preference:
    key: str
    value: Any
    category: str = "general"


@dataclass
class Template:
    id: str
    name: str
    content: str
    category: str = "resume"


@dataclass
class KnowledgeEntry:
    id: str
    title: str
    content: str
    tags: List[str] = field(default_factory=list)
    updated_at: float = 0.0


@dataclass
class DocumentReference:
    id: str
    title: str
    file_path: str
    category: str = "transcript"


@dataclass
class PersonalProfile:
    id: str  # student, professional, research, startup, personal
    name: str
    contact: Contact
    socials: List[SocialProfile] = field(default_factory=list)
    career: Optional[CareerProfile] = None
    resumes: List[Resume] = field(default_factory=list)
    portfolio: List[PortfolioProject] = field(default_factory=list)
    goals: List[Goal] = field(default_factory=list)
    learning: List[LearningItem] = field(default_factory=list)
    certificates: List[Certificate] = field(default_factory=list)
    achievements: List[Achievement] = field(default_factory=list)
    preferences: List[Preference] = field(default_factory=list)
    templates: List[Template] = field(default_factory=list)
    knowledge: List[KnowledgeEntry] = field(default_factory=list)
    documents: List[DocumentReference] = field(default_factory=list)
    version: int = 1


class PersonalService(ServiceLifecycle, abc.ABC):
    @abc.abstractmethod
    def get_profile(self, profile_id: str) -> Optional[PersonalProfile]:
        """Retrieves a specific personal profile."""
        pass

    @abc.abstractmethod
    def create_profile(self, profile: PersonalProfile) -> PersonalProfile:
        """Creates and persists a new personal profile."""
        pass

    @abc.abstractmethod
    def update_profile(self, profile_id: str, profile: PersonalProfile) -> PersonalProfile:
        """Updates and increments the version of an existing profile."""
        pass

    @abc.abstractmethod
    def delete_profile(self, profile_id: str) -> bool:
        """Deletes a personal profile."""
        pass

    @abc.abstractmethod
    def switch_active_profile(self, profile_id: str) -> bool:
        """Switches the active profile used for context injection."""
        pass

    @abc.abstractmethod
    def get_active_profile(self) -> Optional[PersonalProfile]:
        """Returns the currently active profile."""
        pass

    @abc.abstractmethod
    def list_profiles(self) -> List[str]:
        """Lists all registered profile identifiers."""
        pass

    @abc.abstractmethod
    def get_relevant_context(self, objective: str) -> Dict[str, Any]:
        """Performs intelligent context selection based on the objective query."""
        pass

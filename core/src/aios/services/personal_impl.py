import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

from aios.services.personal import (
    Contact,
    SocialProfile,
    Experience,
    Education,
    SkillProfile,
    ProjectReference,
    ResumeVersion,
    Resume,
    PortfolioProject,
    CareerProfile,
    Goal,
    LearningItem,
    Certificate,
    Achievement,
    Preference,
    Template,
    KnowledgeEntry,
    DocumentReference,
    PersonalProfile,
    PersonalService,
)


class LocalPersonalService(PersonalService):
    def __init__(self, cache_filename: str = "personal_profiles.json", workspace_root: str = ".") -> None:
        self._cache_filename = cache_filename
        self._workspace_root = workspace_root
        self._profiles: Dict[str, PersonalProfile] = {}
        self._active_profile_id: Optional[str] = None

    def initialize(self) -> None:
        cache_path = Path(self._workspace_root) / self._cache_filename
        if cache_path.is_file():
            try:
                data = json.loads(cache_path.read_text(encoding="utf-8"))
                profiles_data = data.get("profiles", {})
                self._active_profile_id = data.get("active_profile_id")
                for pid, pdata in profiles_data.items():
                    self._profiles[pid] = self._deserialize_profile(pdata)
            except Exception:
                pass

        # Create default profiles if empty
        if not self._profiles:
            default_p = PersonalProfile(
                id="professional",
                name="Default Developer",
                contact=Contact(email="developer@example.com", phone="123-456", location="Localhost"),
                preferences=[Preference(key="editor", value="vscode")]
            )
            self.create_profile(default_p)
            self._active_profile_id = "professional"

    def get_profile(self, profile_id: str) -> Optional[PersonalProfile]:
        return self._profiles.get(profile_id)

    def create_profile(self, profile: PersonalProfile) -> PersonalProfile:
        self._profiles[profile.id] = profile
        self._save_cache()
        return profile

    def update_profile(self, profile_id: str, profile: PersonalProfile) -> PersonalProfile:
        profile.id = profile_id
        profile.version += 1
        self._profiles[profile_id] = profile
        self._save_cache()
        return profile

    def delete_profile(self, profile_id: str) -> bool:
        if profile_id in self._profiles:
            del self._profiles[profile_id]
            if self._active_profile_id == profile_id:
                self._active_profile_id = list(self._profiles.keys())[0] if self._profiles else None
            self._save_cache()
            return True
        return False

    def switch_active_profile(self, profile_id: str) -> bool:
        if profile_id in self._profiles:
            self._active_profile_id = profile_id
            self._save_cache()
            return True
        return False

    def get_active_profile(self) -> Optional[PersonalProfile]:
        if not self._active_profile_id and self._profiles:
            self._active_profile_id = list(self._profiles.keys())[0]
        if self._active_profile_id:
            return self._profiles.get(self._active_profile_id)
        return None

    def list_profiles(self) -> List[str]:
        return list(self._profiles.keys())

    def get_relevant_context(self, objective: str) -> Dict[str, Any]:
        profile = self.get_active_profile()
        if not profile:
            return {}

        objective_lower = objective.lower()
        context = {
            "name": profile.name,
            "contact": {
                "email": profile.contact.email,
                "phone": profile.contact.phone,
                "location": profile.contact.location
            }
        }

        # Career related injection
        if any(kw in objective_lower for kw in ("resume", "job", "career", "experience", "education", "interview")):
            context["resumes"] = [self._serialize_resume(r) for r in profile.resumes]
            if profile.career:
                context["career"] = {
                    "industry": profile.career.industry,
                    "current_role": profile.career.current_role,
                    "years_experience": profile.career.years_experience,
                    "target_roles": profile.career.target_roles
                }
            context["achievements"] = [
                {"title": a.title, "description": a.description, "date": a.date}
                for a in profile.achievements
            ]

        # Learning & Goals related injection
        elif any(kw in objective_lower for kw in ("learn", "study", "course", "goal", "certificate")):
            context["goals"] = [
                {"id": g.id, "title": g.title, "target_date": g.target_date, "status": g.status, "category": g.category}
                for g in profile.goals
            ]
            context["learning"] = [
                {"id": l.id, "title": l.title, "source": l.source, "status": l.status, "progress": l.progress_percentage}
                for l in profile.learning
            ]
            context["certificates"] = [
                {"name": c.name, "organization": c.issuing_organization, "date": c.issue_date}
                for c in profile.certificates
            ]

        # Project & Portfolio related injection
        elif any(kw in objective_lower for kw in ("project", "portfolio", "code", "build", "repo")):
            context["portfolio"] = [
                {"id": p.id, "name": p.name, "description": p.description, "tech": p.technologies, "repo": p.repository_url}
                for p in profile.portfolio
            ]

        # Knowledge entries related injection
        elif any(kw in objective_lower for kw in ("knowledge", "research", "note", "find")):
            context["knowledge"] = [
                {"id": k.id, "title": k.title, "content": k.content, "tags": k.tags}
                for k in profile.knowledge
            ]

        # Fallback preference injection
        else:
            context["preferences"] = [
                {"key": p.key, "value": p.value}
                for p in profile.preferences
            ]

        return context

    def _save_cache(self) -> None:
        cache_path = Path(self._workspace_root) / self._cache_filename
        serialized = {}
        for pid, p in self._profiles.items():
            serialized[pid] = self._serialize_profile(p)
        payload = {
            "active_profile_id": self._active_profile_id,
            "profiles": serialized
        }
        try:
            cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _serialize_profile(self, p: PersonalProfile) -> Dict[str, Any]:
        return {
            "id": p.id,
            "name": p.name,
            "contact": {"email": p.contact.email, "phone": p.contact.phone, "location": p.contact.location},
            "socials": [{"platform": s.platform, "url": s.url} for s in p.socials],
            "career": {
                "industry": p.career.industry,
                "current_role": p.career.current_role,
                "years_experience": p.career.years_experience,
                "target_roles": p.career.target_roles
            } if p.career else None,
            "resumes": [self._serialize_resume(r) for r in p.resumes],
            "portfolio": [
                {
                    "id": proj.id,
                    "name": proj.name,
                    "description": proj.description,
                    "technologies": proj.technologies,
                    "repository_url": proj.repository_url,
                    "live_url": proj.live_url
                }
                for proj in p.portfolio
            ],
            "goals": [
                {"id": g.id, "title": g.title, "target_date": g.target_date, "status": g.status, "category": g.category}
                for g in p.goals
            ],
            "learning": [
                {"id": l.id, "title": l.title, "source": l.source, "status": l.status, "progress_percentage": l.progress_percentage}
                for l in p.learning
            ],
            "certificates": [
                {"name": c.name, "issuing_organization": c.issuing_organization, "issue_date": c.issue_date, "credential_id": c.credential_id}
                for c in p.certificates
            ],
            "achievements": [
                {"title": a.title, "description": a.description, "date": a.date}
                for a in p.achievements
            ],
            "preferences": [
                {"key": pref.key, "value": pref.value, "category": pref.category}
                for pref in p.preferences
            ],
            "templates": [
                {"id": t.id, "name": t.name, "content": t.content, "category": t.category}
                for t in p.templates
            ],
            "knowledge": [
                {"id": k.id, "title": k.title, "content": k.content, "tags": k.tags, "updated_at": k.updated_at}
                for k in p.knowledge
            ],
            "documents": [
                {"id": d.id, "title": d.title, "file_path": d.file_path, "category": d.category}
                for d in p.documents
            ],
            "version": p.version
        }

    def _serialize_resume(self, r: Resume) -> Dict[str, Any]:
        return {
            "id": r.id,
            "title": r.title,
            "current_version": r.current_version,
            "versions": [
                {
                    "version": v.version,
                    "summary": v.summary,
                    "experiences": [
                        {"company": e.company, "role": e.role, "start_date": e.start_date, "end_date": e.end_date, "description": e.description}
                        for e in v.experiences
                    ],
                    "educations": [
                        {"institution": ed.institution, "degree": ed.degree, "field_of_study": ed.field_of_study, "grad_date": ed.grad_date}
                        for ed in v.educations
                    ],
                    "skills": [
                        {"category": s.category, "skills": s.skills}
                        for s in v.skills
                    ],
                    "projects": [
                        {"name": pr.name, "description": pr.description, "url": pr.url}
                        for pr in v.projects
                    ],
                    "created_at": v.created_at
                }
                for v in r.versions
            ]
        }

    def _deserialize_profile(self, data: Dict[str, Any]) -> PersonalProfile:
        contact_data = data.get("contact", {})
        contact = Contact(
            email=contact_data.get("email", ""),
            phone=contact_data.get("phone", ""),
            location=contact_data.get("location", "")
        )
        socials = [SocialProfile(**s) for s in data.get("socials", [])]
        
        career_data = data.get("career")
        career = CareerProfile(**career_data) if career_data else None

        resumes = []
        for rdata in data.get("resumes", []):
            versions = []
            for vdata in rdata.get("versions", []):
                exps = [Experience(**e) for e in vdata.get("experiences", [])]
                eds = [Education(**ed) for ed in vdata.get("educations", [])]
                sks = [SkillProfile(**sk) for sk in vdata.get("skills", [])]
                prjs = [ProjectReference(**pr) for pr in vdata.get("projects", [])]
                versions.append(
                    ResumeVersion(
                        version=vdata.get("version", 1),
                        summary=vdata.get("summary", ""),
                        experiences=exps,
                        educations=eds,
                        skills=sks,
                        projects=prjs,
                        created_at=vdata.get("created_at", 0.0)
                    )
                )
            resumes.append(
                Resume(
                    id=rdata.get("id", ""),
                    title=rdata.get("title", ""),
                    versions=versions,
                    current_version=rdata.get("current_version", 1)
                )
            )

        portfolio = [PortfolioProject(**p) for p in data.get("portfolio", [])]
        goals = [Goal(**g) for g in data.get("goals", [])]
        learning = [LearningItem(**l) for l in data.get("learning", [])]
        certificates = [Certificate(**c) for c in data.get("certificates", [])]
        achievements = [Achievement(**a) for a in data.get("achievements", [])]
        preferences = [Preference(**pref) for pref in data.get("preferences", [])]
        templates = [Template(**t) for t in data.get("templates", [])]
        knowledge = [KnowledgeEntry(**k) for k in data.get("knowledge", [])]
        documents = [DocumentReference(**d) for d in data.get("documents", [])]

        return PersonalProfile(
            id=data.get("id", ""),
            name=data.get("name", ""),
            contact=contact,
            socials=socials,
            career=career,
            resumes=resumes,
            portfolio=portfolio,
            goals=goals,
            learning=learning,
            certificates=certificates,
            achievements=achievements,
            preferences=preferences,
            templates=templates,
            knowledge=knowledge,
            documents=documents,
            version=data.get("version", 1)
        )

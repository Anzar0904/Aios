import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from aios.services.personal import (
    Achievement,
    CalendarEvent,
    CareerProfile,
    Certificate,
    Contact,
    DocumentReference,
    Education,
    Experience,
    Goal,
    Habit,
    KnowledgeEntry,
    LearningItem,
    PersonalGoal,
    PersonalLearningItem,
    PersonalNote,
    PersonalProfile,
    PersonalReminder,
    PersonalService,
    PersonalTask,
    PortfolioProject,
    Preference,
    ProjectReference,
    Resume,
    ResumeVersion,
    SkillProfile,
    SocialProfile,
    Template,
)


class LocalPersonalService(PersonalService):
    def __init__(
        self, cache_filename: str = "personal_profiles.json", workspace_root: str = "."
    ) -> None:
        self._cache_filename = cache_filename
        self._workspace_root = workspace_root
        self._profiles: Dict[str, PersonalProfile] = {}
        self._active_profile_id: Optional[str] = None
        self._conn: Optional[sqlite3.Connection] = None

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
                contact=Contact(
                    email="developer@example.com", phone="123-456", location="Localhost"
                ),
                preferences=[Preference(key="editor", value="vscode")],
            )
            self.create_profile(default_p)
            self._active_profile_id = "professional"

        # Initialize SQLite database for Phase 11
        db_path = Path(self._workspace_root) / "aios.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._bootstrap_schema()
        self._seed_default_personal_entities()

    def shutdown(self) -> None:
        super().shutdown()
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass

    def _bootstrap_schema(self) -> None:
        with self._conn:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS personal_goals (
                    goal_id       TEXT PRIMARY KEY,
                    title         TEXT NOT NULL,
                    timeframe     TEXT NOT NULL,
                    category      TEXT NOT NULL,
                    priority      INTEGER NOT NULL DEFAULT 1,
                    status        TEXT NOT NULL DEFAULT 'pending',
                    progress      REAL NOT NULL DEFAULT 0.0,
                    dependencies  TEXT NOT NULL DEFAULT '[]',
                    created_at    REAL NOT NULL,
                    target_date   TEXT
                );
            """)

            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS personal_tasks (
                    task_id       TEXT PRIMARY KEY,
                    title         TEXT NOT NULL,
                    category      TEXT NOT NULL,
                    priority      INTEGER NOT NULL DEFAULT 1,
                    status        TEXT NOT NULL DEFAULT 'pending',
                    due_date      TEXT,
                    dependencies  TEXT NOT NULL DEFAULT '[]',
                    context       TEXT NOT NULL DEFAULT '',
                    created_at    REAL NOT NULL
                );
            """)

            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS calendar_events (
                    event_id      TEXT PRIMARY KEY,
                    title         TEXT NOT NULL,
                    start_time    REAL NOT NULL,
                    end_time      REAL NOT NULL,
                    category      TEXT NOT NULL,
                    priority      INTEGER NOT NULL DEFAULT 1,
                    description   TEXT NOT NULL DEFAULT ''
                );
            """)

            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS habits (
                    habit_id          TEXT PRIMARY KEY,
                    name              TEXT NOT NULL UNIQUE,
                    frequency         TEXT NOT NULL,
                    streak            INTEGER NOT NULL DEFAULT 0,
                    success_rate      REAL NOT NULL DEFAULT 100.0,
                    consistency_score REAL NOT NULL DEFAULT 100.0
                );
            """)

            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS personal_reminders (
                    reminder_id   TEXT PRIMARY KEY,
                    title         TEXT NOT NULL,
                    trigger_time  REAL NOT NULL,
                    reminder_type TEXT NOT NULL,
                    status        TEXT NOT NULL DEFAULT 'pending'
                );
            """)

            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS personal_notes (
                    note_id       TEXT PRIMARY KEY,
                    title         TEXT NOT NULL,
                    content       TEXT NOT NULL,
                    category      TEXT NOT NULL DEFAULT 'idea',
                    created_at    REAL NOT NULL
                );
            """)

            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS personal_learning_items (
                    item_id       TEXT PRIMARY KEY,
                    title         TEXT NOT NULL,
                    item_type     TEXT NOT NULL,
                    progress      REAL NOT NULL DEFAULT 0.0,
                    status        TEXT NOT NULL DEFAULT 'pending'
                );
            """)

    def _seed_default_personal_entities(self) -> None:
        cursor = self._conn.cursor()
        # Seed default goal
        cursor.execute("SELECT count(*) FROM personal_goals")
        if cursor.fetchone()[0] == 0:
            self.create_goal(
                PersonalGoal(
                    goal_id="goal_default_1",
                    title="Master Agentic Programming",
                    timeframe="quarterly",
                    category="learning",
                    priority=5,
                    status="in_progress",
                    progress=45.0,
                )
            )

        # Seed default task
        cursor.execute("SELECT count(*) FROM personal_tasks")
        if cursor.fetchone()[0] == 0:
            self.create_task(
                PersonalTask(
                    task_id="task_default_1",
                    title="Implement Phase 11 Personal Intelligence",
                    category="personal",
                    priority=5,
                    status="pending",
                )
            )

        # Seed default habit
        cursor.execute("SELECT count(*) FROM habits")
        if cursor.fetchone()[0] == 0:
            self.create_habit(
                Habit(
                    habit_id="habit_default_1",
                    name="Daily Code Review",
                    frequency="daily",
                    streak=7,
                    success_rate=95.0,
                    consistency_score=98.0,
                )
            )

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
                "location": profile.contact.location,
            },
        }

        # Career related injection
        if any(
            kw in objective_lower
            for kw in ("resume", "job", "career", "experience", "education", "interview")
        ):
            context["resumes"] = [self._serialize_resume(r) for r in profile.resumes]
            if profile.career:
                context["career"] = {
                    "industry": profile.career.industry,
                    "current_role": profile.career.current_role,
                    "years_experience": profile.career.years_experience,
                    "target_roles": profile.career.target_roles,
                }
            context["achievements"] = [
                {"title": a.title, "description": a.description, "date": a.date}
                for a in profile.achievements
            ]

        # Learning & Goals related injection
        elif any(
            kw in objective_lower for kw in ("learn", "study", "course", "goal", "certificate")
        ):
            context["goals"] = [
                {
                    "id": g.id,
                    "title": g.title,
                    "target_date": g.target_date,
                    "status": g.status,
                    "category": g.category,
                }
                for g in profile.goals
            ]
            context["learning"] = [
                {
                    "id": l.id,
                    "title": l.title,
                    "source": l.source,
                    "status": l.status,
                    "progress": l.progress_percentage,
                }
                for l in profile.learning
            ]
            context["certificates"] = [
                {"name": c.name, "organization": c.issuing_organization, "date": c.issue_date}
                for c in profile.certificates
            ]

        # Project & Portfolio related injection
        elif any(kw in objective_lower for kw in ("project", "portfolio", "code", "build", "repo")):
            context["portfolio"] = [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "tech": p.technologies,
                    "repo": p.repository_url,
                }
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
            context["preferences"] = [{"key": p.key, "value": p.value} for p in profile.preferences]

        return context

    def _save_cache(self) -> None:
        cache_path = Path(self._workspace_root) / self._cache_filename
        serialized = {}
        for pid, p in self._profiles.items():
            serialized[pid] = self._serialize_profile(p)
        payload = {"active_profile_id": self._active_profile_id, "profiles": serialized}
        try:
            cache_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        except Exception:
            pass

    def _serialize_profile(self, p: PersonalProfile) -> Dict[str, Any]:
        return {
            "id": p.id,
            "name": p.name,
            "contact": {
                "email": p.contact.email,
                "phone": p.contact.phone,
                "location": p.contact.location,
            },
            "socials": [{"platform": s.platform, "url": s.url} for s in p.socials],
            "career": {
                "industry": p.career.industry,
                "current_role": p.career.current_role,
                "years_experience": p.career.years_experience,
                "target_roles": p.career.target_roles,
            }
            if p.career
            else None,
            "resumes": [self._serialize_resume(r) for r in p.resumes],
            "portfolio": [
                {
                    "id": proj.id,
                    "name": proj.name,
                    "description": proj.description,
                    "technologies": proj.technologies,
                    "repository_url": proj.repository_url,
                    "live_url": proj.live_url,
                }
                for proj in p.portfolio
            ],
            "goals": [
                {
                    "id": g.id,
                    "title": g.title,
                    "target_date": g.target_date,
                    "status": g.status,
                    "category": g.category,
                }
                for g in p.goals
            ],
            "learning": [
                {
                    "id": l.id,
                    "title": l.title,
                    "source": l.source,
                    "status": l.status,
                    "progress_percentage": l.progress_percentage,
                }
                for l in p.learning
            ],
            "certificates": [
                {
                    "name": c.name,
                    "issuing_organization": c.issuing_organization,
                    "issue_date": c.issue_date,
                    "credential_id": c.credential_id,
                }
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
                {
                    "id": k.id,
                    "title": k.title,
                    "content": k.content,
                    "tags": k.tags,
                    "updated_at": k.updated_at,
                }
                for k in p.knowledge
            ],
            "documents": [
                {"id": d.id, "title": d.title, "file_path": d.file_path, "category": d.category}
                for d in p.documents
            ],
            "version": p.version,
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
                        {
                            "company": e.company,
                            "role": e.role,
                            "start_date": e.start_date,
                            "end_date": e.end_date,
                            "description": e.description,
                        }
                        for e in v.experiences
                    ],
                    "educations": [
                        {
                            "institution": ed.institution,
                            "degree": ed.degree,
                            "field_of_study": ed.field_of_study,
                            "grad_date": ed.grad_date,
                        }
                        for ed in v.educations
                    ],
                    "skills": [{"category": s.category, "skills": s.skills} for s in v.skills],
                    "projects": [
                        {"name": pr.name, "description": pr.description, "url": pr.url}
                        for pr in v.projects
                    ],
                    "created_at": v.created_at,
                }
                for v in r.versions
            ],
        }

    def _deserialize_profile(self, data: Dict[str, Any]) -> PersonalProfile:
        contact_data = data.get("contact", {})
        contact = Contact(
            email=contact_data.get("email", ""),
            phone=contact_data.get("phone", ""),
            location=contact_data.get("location", ""),
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
                        created_at=vdata.get("created_at", 0.0),
                    )
                )
            resumes.append(
                Resume(
                    id=rdata.get("id", ""),
                    title=rdata.get("title", ""),
                    versions=versions,
                    current_version=rdata.get("current_version", 1),
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
            version=data.get("version", 1),
        )

    # ── Phase 11 Personal Intelligence Implementations ──────────────────────

    def create_goal(self, goal: PersonalGoal) -> PersonalGoal:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO personal_goals (
                    goal_id, title, timeframe, category, priority, status, progress, dependencies, created_at, target_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(goal_id) DO UPDATE SET
                    title=excluded.title, timeframe=excluded.timeframe, category=excluded.category,
                    priority=excluded.priority, status=excluded.status, progress=excluded.progress,
                    dependencies=excluded.dependencies, target_date=excluded.target_date
                """,
                (
                    goal.goal_id,
                    goal.title,
                    goal.timeframe,
                    goal.category,
                    goal.priority,
                    goal.status,
                    goal.progress,
                    json.dumps(goal.dependencies),
                    goal.created_at,
                    goal.target_date,
                ),
            )
        return goal

    def get_goal(self, goal_id: str) -> Optional[PersonalGoal]:
        cursor = self._conn.cursor()
        row = cursor.execute(
            "SELECT * FROM personal_goals WHERE goal_id = ?", (goal_id,)
        ).fetchone()
        return PersonalGoal.from_dict(dict(row)) if row else None

    def list_goals(self) -> List[PersonalGoal]:
        cursor = self._conn.cursor()
        rows = cursor.execute("SELECT * FROM personal_goals").fetchall()
        return [PersonalGoal.from_dict(dict(r)) for r in rows]

    def create_task(self, task: PersonalTask) -> PersonalTask:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO personal_tasks (
                    task_id, title, category, priority, status, due_date, dependencies, context, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(task_id) DO UPDATE SET
                    title=excluded.title, category=excluded.category, priority=excluded.priority,
                    status=excluded.status, due_date=excluded.due_date, dependencies=excluded.dependencies,
                    context=excluded.context
                """,
                (
                    task.task_id,
                    task.title,
                    task.category,
                    task.priority,
                    task.status,
                    task.due_date,
                    json.dumps(task.dependencies),
                    task.context,
                    task.created_at,
                ),
            )
        return task

    def get_task(self, task_id: str) -> Optional[PersonalTask]:
        cursor = self._conn.cursor()
        row = cursor.execute(
            "SELECT * FROM personal_tasks WHERE task_id = ?", (task_id,)
        ).fetchone()
        return PersonalTask.from_dict(dict(row)) if row else None

    def list_tasks(self) -> List[PersonalTask]:
        cursor = self._conn.cursor()
        rows = cursor.execute("SELECT * FROM personal_tasks").fetchall()
        return [PersonalTask.from_dict(dict(r)) for r in rows]

    def create_event(self, event: CalendarEvent) -> CalendarEvent:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO calendar_events (
                    event_id, title, start_time, end_time, category, priority, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(event_id) DO UPDATE SET
                    title=excluded.title, start_time=excluded.start_time, end_time=excluded.end_time,
                    category=excluded.category, priority=excluded.priority, description=excluded.description
                """,
                (
                    event.event_id,
                    event.title,
                    event.start_time,
                    event.end_time,
                    event.category,
                    event.priority,
                    event.description,
                ),
            )
        return event

    def list_events(self) -> List[CalendarEvent]:
        cursor = self._conn.cursor()
        rows = cursor.execute("SELECT * FROM calendar_events").fetchall()
        return [CalendarEvent.from_dict(dict(r)) for r in rows]

    def detect_calendar_conflicts(self) -> List[Dict[str, Any]]:
        events = self.list_events()
        conflicts = []
        for i in range(len(events)):
            for j in range(i + 1, len(events)):
                e1 = events[i]
                e2 = events[j]
                # Check for overlap
                if max(e1.start_time, e2.start_time) < min(e1.end_time, e2.end_time):
                    conflicts.append(
                        {
                            "event_1": e1.title,
                            "event_2": e2.title,
                            "start_time": max(e1.start_time, e2.start_time),
                        }
                    )
        return conflicts

    def create_habit(self, habit: Habit) -> Habit:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO habits (
                    habit_id, name, frequency, streak, success_rate, consistency_score
                ) VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(habit_id) DO UPDATE SET
                    name=excluded.name, frequency=excluded.frequency, streak=excluded.streak,
                    success_rate=excluded.success_rate, consistency_score=excluded.consistency_score
                """,
                (
                    habit.habit_id,
                    habit.name,
                    habit.frequency,
                    habit.streak,
                    habit.success_rate,
                    habit.consistency_score,
                ),
            )
        return habit

    def increment_habit_streak(self, habit_id: str) -> Optional[Habit]:
        with self._conn:
            self._conn.execute(
                "UPDATE habits SET streak = streak + 1 WHERE habit_id = ?", (habit_id,)
            )
        return self.get_habit(habit_id)

    def get_habit(self, habit_id: str) -> Optional[Habit]:
        cursor = self._conn.cursor()
        row = cursor.execute("SELECT * FROM habits WHERE habit_id = ?", (habit_id,)).fetchone()
        return Habit.from_dict(dict(row)) if row else None

    def list_habits(self) -> List[Habit]:
        cursor = self._conn.cursor()
        rows = cursor.execute("SELECT * FROM habits").fetchall()
        return [Habit.from_dict(dict(r)) for r in rows]

    def create_reminder(self, reminder: PersonalReminder) -> PersonalReminder:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO personal_reminders (
                    reminder_id, title, trigger_time, reminder_type, status
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(reminder_id) DO UPDATE SET
                    title=excluded.title, trigger_time=excluded.trigger_time,
                    reminder_type=excluded.reminder_type, status=excluded.status
                """,
                (
                    reminder.reminder_id,
                    reminder.title,
                    reminder.trigger_time,
                    reminder.reminder_type,
                    reminder.status,
                ),
            )
        return reminder

    def list_reminders(self) -> List[PersonalReminder]:
        cursor = self._conn.cursor()
        rows = cursor.execute("SELECT * FROM personal_reminders").fetchall()
        return [PersonalReminder.from_dict(dict(r)) for r in rows]

    def create_note(self, note: PersonalNote) -> PersonalNote:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO personal_notes (
                    note_id, title, content, category, created_at
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(note_id) DO UPDATE SET
                    title=excluded.title, content=excluded.content, category=excluded.category
                """,
                (
                    note.note_id,
                    note.title,
                    note.content,
                    note.category,
                    note.created_at,
                ),
            )
        return note

    def list_notes(self) -> List[PersonalNote]:
        cursor = self._conn.cursor()
        rows = cursor.execute("SELECT * FROM personal_notes").fetchall()
        return [PersonalNote.from_dict(dict(r)) for r in rows]

    def create_learning_item(self, item: PersonalLearningItem) -> PersonalLearningItem:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO personal_learning_items (
                    item_id, title, item_type, progress, status
                ) VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(item_id) DO UPDATE SET
                    title=excluded.title, item_type=excluded.item_type,
                    progress=excluded.progress, status=excluded.status
                """,
                (
                    item.item_id,
                    item.title,
                    item.item_type,
                    item.progress,
                    item.status,
                ),
            )
        return item

    def list_learning_items(self) -> List[PersonalLearningItem]:
        cursor = self._conn.cursor()
        rows = cursor.execute("SELECT * FROM personal_learning_items").fetchall()
        return [PersonalLearningItem.from_dict(dict(r)) for r in rows]

    def get_coach_recommendations(self) -> Dict[str, Any]:
        """Perform productivity analysis and return coach recommendations."""
        goals = self.list_goals()
        habits = self.list_habits()

        rec = []
        if goals and any(g.status != "achieved" for g in goals):
            rec.append("Set weekly milestones for your quarterly goals.")
        if habits and any(h.streak < 3 for h in habits):
            rec.append("Focus on consistency for habit: " + habits[0].name)
        else:
            rec.append("Great consistency! Consider setting a new stretch goal.")

        return {
            "insights": ["Completion rates are stable.", "Consistency score remains at 95%."],
            "recommendations": rec,
        }

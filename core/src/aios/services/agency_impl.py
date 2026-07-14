"""Phase 6: Agency Intelligence — SQLite Database Implementation.

Implements the AgencyCRMService interface with a local SQLite database,
supporting WAL mode, locks, transaction isolation, custom analytical pipelines,
seeding default records, proposal generation templates, and outreach helpers.
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import time
from contextlib import contextmanager
from threading import Lock
from typing import Any, Dict, Generator, List, Optional

from aios.services.agency import (
    AgencyCRMService,
    Client,
    ClientStatus,
    Company,
    Contact,
    FollowUp,
    Lead,
    LeadPriority,
    LeadStage,
    Meeting,
    Outreach,
    OutreachStatus,
    OutreachType,
    Proposal,
    ProposalStatus,
    ProposalType,
    new_id,
)

logger = logging.getLogger(__name__)

_DEFAULT_DB = os.path.join(os.path.expanduser("~"), ".aios_agency.db")

# ── Seed data for CRM elements ───────────────────────────────────────────────
DEFAULT_COMPANIES = [
    {
        "name": "Cyberdyne Systems",
        "industry": "Robotics & AI",
        "website": "https://cyberdyne.ai",
        "size": "500-1000",
        "location": "Sunnyvale, CA",
        "services": ["Automation", "AI Development"],
        "client_status": "active",
    },
    {
        "name": "Miller Retail",
        "industry": "Retail & E-commerce",
        "website": "https://millerretail.com",
        "size": "50-100",
        "location": "Austin, TX",
        "services": ["Consulting", "Chatbot Integration"],
        "client_status": "none",
    },
    {
        "name": "Tyrell Corporation",
        "industry": "Synthetic Biology",
        "website": "https://tyrell.com",
        "size": "10000+",
        "location": "Los Angeles, CA",
        "services": ["AI Consulting"],
        "client_status": "none",
    },
]

DEFAULT_CONTACTS = [
    {
        "name": "Sarah Connor",
        "email": "sarah.connor@cyberdyne.ai",
        "phone": "+1-408-555-0199",
        "company_name": "Cyberdyne Systems",
        "role": "VP of Operations",
        "linkedin": "https://linkedin.com/in/sarah-connor-cyberdyne",
        "source": "Inbound Referral",
        "notes": "Interested in deployment pipelines and custom automations.",
        "tags": ["decision_maker", "tech"],
    },
    {
        "name": "David Miller",
        "email": "david@millerretail.com",
        "phone": "+1-512-555-0182",
        "company_name": "Miller Retail",
        "role": "Founder & CEO",
        "linkedin": "https://linkedin.com/in/david-miller-retail",
        "source": "Outreach Campaign",
        "notes": "Looking to automate client followups and Notion syncing.",
        "tags": ["prospect", "retail"],
    },
    {
        "name": "Eldon Tyrell",
        "email": "eldon@tyrell.com",
        "phone": "+1-213-555-0144",
        "company_name": "Tyrell Corporation",
        "role": "Chief Executive",
        "linkedin": "https://linkedin.com/in/eldon-tyrell-replicants",
        "source": "Cold Outreach",
        "notes": "Inquiry about high-end reasoning model routing capabilities.",
        "tags": ["enterprise", "replicant"],
    },
]


class AgencyCRMServiceImpl(AgencyCRMService):
    """SQLite-backed CRM registry and pipeline manager."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self._db_path = db_path or os.getenv("AIOS_AGENCY_DB", _DEFAULT_DB)
        self._lock = Lock()
        self._conn: Optional[sqlite3.Connection] = None

    # ── Lifecycle ────────────────────────────────────────────────────────────

    def initialize(self) -> None:
        self._conn = sqlite3.connect(self._db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._bootstrap_schema()
        self._seed_default_data()
        logger.info("Agency CRM Service initialized at: %s", self._db_path)

    def start(self) -> None:
        pass

    def shutdown(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None

    def ready(self) -> bool:
        return self._conn is not None

    # ── Database Schema ──────────────────────────────────────────────────────

    def _bootstrap_schema(self) -> None:
        assert self._conn is not None
        with self._conn:
            self._conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS contacts (
                    contact_id    TEXT PRIMARY KEY,
                    name          TEXT NOT NULL,
                    email         TEXT NOT NULL UNIQUE,
                    phone         TEXT NOT NULL DEFAULT '',
                    company_id    TEXT NOT NULL DEFAULT '',
                    role          TEXT NOT NULL DEFAULT '',
                    linkedin      TEXT NOT NULL DEFAULT '',
                    website       TEXT NOT NULL DEFAULT '',
                    status        TEXT NOT NULL DEFAULT 'active',
                    source        TEXT NOT NULL DEFAULT '',
                    notes         TEXT NOT NULL DEFAULT '',
                    tags          TEXT NOT NULL DEFAULT '[]',
                    created_at    REAL NOT NULL,
                    last_contact  REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS companies (
                    company_id    TEXT PRIMARY KEY,
                    name          TEXT NOT NULL UNIQUE,
                    industry      TEXT NOT NULL DEFAULT '',
                    website       TEXT NOT NULL DEFAULT '',
                    size          TEXT NOT NULL DEFAULT '',
                    location      TEXT NOT NULL DEFAULT '',
                    services      TEXT NOT NULL DEFAULT '[]',
                    decision_makers TEXT NOT NULL DEFAULT '[]',
                    lead_count    INTEGER NOT NULL DEFAULT 0,
                    client_status TEXT NOT NULL DEFAULT 'none',
                    projects      TEXT NOT NULL DEFAULT '[]',
                    created_at    REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS leads (
                    lead_id         TEXT PRIMARY KEY,
                    company_id      TEXT NOT NULL,
                    contact_id      TEXT NOT NULL,
                    title           TEXT NOT NULL,
                    stage           TEXT NOT NULL DEFAULT 'new',
                    priority        TEXT NOT NULL DEFAULT 'medium',
                    score           INTEGER NOT NULL DEFAULT 50,
                    expected_value  REAL NOT NULL DEFAULT 0.0,
                    next_action     TEXT NOT NULL DEFAULT '',
                    followup_date   REAL NOT NULL DEFAULT 0.0,
                    created_at      REAL NOT NULL,
                    updated_at      REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS clients (
                    client_id      TEXT PRIMARY KEY,
                    company_id     TEXT NOT NULL UNIQUE,
                    status         TEXT NOT NULL DEFAULT 'active',
                    projects       TEXT NOT NULL DEFAULT '[]',
                    meetings       TEXT NOT NULL DEFAULT '[]',
                    invoices       TEXT NOT NULL DEFAULT '[]',
                    contracts      TEXT NOT NULL DEFAULT '[]',
                    documents      TEXT NOT NULL DEFAULT '[]',
                    workflows      TEXT NOT NULL DEFAULT '[]',
                    relationship_history TEXT NOT NULL DEFAULT '[]',
                    created_at     REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS proposals (
                    proposal_id    TEXT PRIMARY KEY,
                    lead_id        TEXT NOT NULL,
                    title          TEXT NOT NULL,
                    proposal_type  TEXT NOT NULL,
                    status         TEXT NOT NULL DEFAULT 'draft',
                    value          REAL NOT NULL DEFAULT 0.0,
                    content        TEXT NOT NULL DEFAULT '',
                    created_at     REAL NOT NULL,
                    updated_at     REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS outreach (
                    outreach_id    TEXT PRIMARY KEY,
                    lead_id        TEXT NOT NULL,
                    contact_id     TEXT NOT NULL,
                    outreach_type  TEXT NOT NULL,
                    status         TEXT NOT NULL DEFAULT 'pending',
                    subject        TEXT NOT NULL DEFAULT '',
                    body           TEXT NOT NULL DEFAULT '',
                    sent_at        REAL NOT NULL DEFAULT 0.0,
                    replied_at     REAL NOT NULL DEFAULT 0.0
                );

                CREATE TABLE IF NOT EXISTS meetings (
                    meeting_id     TEXT PRIMARY KEY,
                    title          TEXT NOT NULL,
                    start_time     REAL NOT NULL,
                    duration_min   INTEGER NOT NULL DEFAULT 30,
                    participants   TEXT NOT NULL DEFAULT '[]',
                    company_id     TEXT NOT NULL DEFAULT '',
                    agenda         TEXT NOT NULL DEFAULT '',
                    notes          TEXT NOT NULL DEFAULT '',
                    decisions      TEXT NOT NULL DEFAULT '[]',
                    action_items   TEXT NOT NULL DEFAULT '[]',
                    follow_ups     TEXT NOT NULL DEFAULT '[]',
                    created_at     REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS followups (
                    followup_id    TEXT PRIMARY KEY,
                    target_type    TEXT NOT NULL,
                    target_id      TEXT NOT NULL,
                    title          TEXT NOT NULL,
                    due_date       REAL NOT NULL,
                    status         TEXT NOT NULL DEFAULT 'pending',
                    notes          TEXT NOT NULL DEFAULT '',
                    created_at     REAL NOT NULL
                );
                """
            )

    def _seed_default_data(self) -> None:
        """Populate defaults if database table is empty."""
        assert self._conn is not None
        with self._lock:
            count = self._conn.execute("SELECT count(*) FROM companies").fetchone()[0]
        if count > 0:
            return

        # Seed Companies
        company_ids = {}
        for c in DEFAULT_COMPANIES:
            cid = new_id()
            company_ids[c["name"]] = cid
            comp = Company(
                company_id=cid,
                name=c["name"],
                industry=c["industry"],
                website=c["website"],
                size=c["size"],
                location=c["location"],
                services=c["services"],
                client_status=c["client_status"],
            )
            self.create_company(comp)

        # Seed Contacts
        contact_ids = {}
        for cn in DEFAULT_CONTACTS:
            cid = new_id()
            contact_ids[cn["name"]] = cid
            comp_id = company_ids.get(cn["company_name"], "")
            contact = Contact(
                contact_id=cid,
                name=cn["name"],
                email=cn["email"],
                phone=cn["phone"],
                company_id=comp_id,
                role=cn["role"],
                linkedin=cn["linkedin"],
                source=cn["source"],
                notes=cn["notes"],
                tags=cn["tags"],
            )
            self.create_contact(contact)

            # Link back decision maker to company
            if comp_id:
                company = self.get_company(comp_id)
                if company:
                    company.decision_makers.append(cid)
                    self.create_company(company)

        # Seed Active Client
        cyber_id = company_ids["Cyberdyne Systems"]
        cyber_client = Client(
            client_id=new_id(),
            company_id=cyber_id,
            status=ClientStatus.ACTIVE,
            projects=["aios-project-id"],
            relationship_history=[
                {"date": time.time() - 172800, "event": "Onboarded as active automation client."}
            ],
        )
        self.create_client(cyber_client)

        # Seed Leads
        miller_id = company_ids["Miller Retail"]
        miller_contact = contact_ids["David Miller"]
        miller_lead = Lead(
            lead_id=new_id(),
            company_id=miller_id,
            contact_id=miller_contact,
            title="E-commerce Automation Pipeline Integration",
            stage=LeadStage.QUALIFIED,
            priority=LeadPriority.HIGH,
            score=85,
            expected_value=8500.0,
            next_action="Send Consulting Proposal",
            followup_date=time.time() + 86400,
        )
        self.create_lead(miller_lead)

        tyrell_id = company_ids["Tyrell Corporation"]
        tyrell_contact = contact_ids["Eldon Tyrell"]
        tyrell_lead = Lead(
            lead_id=new_id(),
            company_id=tyrell_id,
            contact_id=tyrell_contact,
            title="Enterprise AI Reasoning Model Consulting",
            stage=LeadStage.NEW,
            priority=LeadPriority.CRITICAL,
            score=95,
            expected_value=25000.0,
            next_action="Prepare Custom AI Development Proposal Outline",
            followup_date=time.time() + 172800,
        )
        self.create_lead(tyrell_lead)

        # Seed initial meeting
        meeting = Meeting(
            meeting_id=new_id(),
            title="Cyberdyne Kickoff & Discovery Session",
            start_time=time.time() - 3600,
            duration_min=45,
            participants=[contact_ids["Sarah Connor"]],
            company_id=cyber_id,
            agenda="Introduce AI OS workflow capabilities, discuss supabase and notion integrations.",
            notes="Sarah is looking for robust local model routing. DeepSeek and Qwen are preferred.",
            decisions=["Use local AI OS instance to manage Cyberdyne deployment pipelines."],
            action_items=[
                {"task": "Set up n8n sync pipeline", "done": False, "owner": "Anzar Akhtar"}
            ],
        )
        self.create_meeting(meeting)

        # Seed followup task
        fol = FollowUp(
            followup_id=new_id(),
            target_type="lead",
            target_id=miller_lead.lead_id,
            title="Follow up with David Miller regarding proposed budget estimate",
            due_date=time.time() - 3600,  # Overdue for test visualization
            status="pending",
            notes="Sarah from Cyberdyne is waiting on proposal drafts too.",
        )
        self.create_followup(fol)

    # ── Database Helpers ─────────────────────────────────────────────────────

    @contextmanager
    def _tx(self) -> Generator[sqlite3.Connection, None, None]:
        assert self._conn is not None, "Agency database connection offline."
        with self._lock:
            with self._conn:
                yield self._conn

    # ── Contacts CRUD ────────────────────────────────────────────────────────

    def create_contact(self, contact: Contact) -> Contact:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO contacts (
                    contact_id, name, email, phone, company_id, role,
                    linkedin, website, status, source, notes, tags, created_at, last_contact
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(contact_id) DO UPDATE SET
                    name=excluded.name, email=excluded.email, phone=excluded.phone,
                    company_id=excluded.company_id, role=excluded.role, linkedin=excluded.linkedin,
                    website=excluded.website, status=excluded.status, source=excluded.source,
                    notes=excluded.notes, tags=excluded.tags, last_contact=excluded.last_contact
                """,
                (
                    contact.contact_id,
                    contact.name,
                    contact.email,
                    contact.phone,
                    contact.company_id,
                    contact.role,
                    contact.linkedin,
                    contact.website,
                    contact.status.value,
                    contact.source,
                    contact.notes,
                    json.dumps(contact.tags),
                    contact.created_at,
                    contact.last_contact,
                ),
            )
        return contact

    def get_contact(self, contact_id: str) -> Optional[Contact]:
        assert self._conn is not None
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM contacts WHERE contact_id = ?", (contact_id,)
            ).fetchone()
        return Contact.from_dict(dict(row)) if row else None

    def list_contacts(self) -> List[Contact]:
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute("SELECT * FROM contacts").fetchall()
        return [Contact.from_dict(dict(r)) for r in rows]

    def delete_contact(self, contact_id: str) -> bool:
        if not self.get_contact(contact_id):
            return False
        with self._tx() as conn:
            conn.execute("DELETE FROM contacts WHERE contact_id = ?", (contact_id,))
        return True

    # ── Companies CRUD ───────────────────────────────────────────────────────

    def create_company(self, company: Company) -> Company:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO companies (
                    company_id, name, industry, website, size, location,
                    services, decision_makers, lead_count, client_status, projects, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(company_id) DO UPDATE SET
                    name=excluded.name, industry=excluded.industry, website=excluded.website,
                    size=excluded.size, location=excluded.location, services=excluded.services,
                    decision_makers=excluded.decision_makers, lead_count=excluded.lead_count,
                    client_status=excluded.client_status, projects=excluded.projects
                """,
                (
                    company.company_id,
                    company.name,
                    company.industry,
                    company.website,
                    company.size,
                    company.location,
                    json.dumps(company.services),
                    json.dumps(company.decision_makers),
                    company.lead_count,
                    company.client_status,
                    json.dumps(company.projects),
                    company.created_at,
                ),
            )
        return company

    def get_company(self, company_id: str) -> Optional[Company]:
        assert self._conn is not None
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM companies WHERE company_id = ?", (company_id,)
            ).fetchone()
        return Company.from_dict(dict(row)) if row else None

    def list_companies(self) -> List[Company]:
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute("SELECT * FROM companies").fetchall()
        return [Company.from_dict(dict(r)) for r in rows]

    def delete_company(self, company_id: str) -> bool:
        if not self.get_company(company_id):
            return False
        with self._tx() as conn:
            conn.execute("DELETE FROM companies WHERE company_id = ?", (company_id,))
        return True

    # ── Leads CRUD ───────────────────────────────────────────────────────────

    def create_lead(self, lead: Lead) -> Lead:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO leads (
                    lead_id, company_id, contact_id, title, stage, priority,
                    score, expected_value, next_action, followup_date, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(lead_id) DO UPDATE SET
                    company_id=excluded.company_id, contact_id=excluded.contact_id,
                    title=excluded.title, stage=excluded.stage, priority=excluded.priority,
                    score=excluded.score, expected_value=excluded.expected_value,
                    next_action=excluded.next_action, followup_date=excluded.followup_date,
                    updated_at=excluded.updated_at
                """,
                (
                    lead.lead_id,
                    lead.company_id,
                    lead.contact_id,
                    lead.title,
                    lead.stage.value,
                    lead.priority.value,
                    lead.score,
                    lead.expected_value,
                    lead.next_action,
                    lead.followup_date,
                    lead.created_at,
                    lead.updated_at,
                ),
            )
        return lead

    def get_lead(self, lead_id: str) -> Optional[Lead]:
        assert self._conn is not None
        with self._lock:
            row = self._conn.execute("SELECT * FROM leads WHERE lead_id = ?", (lead_id,)).fetchone()
        return Lead.from_dict(dict(row)) if row else None

    def list_leads(self) -> List[Lead]:
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute("SELECT * FROM leads").fetchall()
        return [Lead.from_dict(dict(r)) for r in rows]

    def delete_lead(self, lead_id: str) -> bool:
        if not self.get_lead(lead_id):
            return False
        with self._tx() as conn:
            conn.execute("DELETE FROM leads WHERE lead_id = ?", (lead_id,))
        return True

    # ── Clients CRUD ─────────────────────────────────────────────────────────

    def create_client(self, client: Client) -> Client:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO clients (
                    client_id, company_id, status, projects, meetings,
                    invoices, contracts, documents, workflows, relationship_history, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(client_id) DO UPDATE SET
                    company_id=excluded.company_id, status=excluded.status,
                    projects=excluded.projects, meetings=excluded.meetings,
                    invoices=excluded.invoices, contracts=excluded.contracts,
                    documents=excluded.documents, workflows=excluded.workflows,
                    relationship_history=excluded.relationship_history
                """,
                (
                    client.client_id,
                    client.company_id,
                    client.status.value,
                    json.dumps(client.projects),
                    json.dumps(client.meetings),
                    json.dumps(client.invoices),
                    json.dumps(client.contracts),
                    json.dumps(client.documents),
                    json.dumps(client.workflows),
                    json.dumps(client.relationship_history),
                    client.created_at,
                ),
            )
        return client

    def get_client(self, client_id: str) -> Optional[Client]:
        assert self._conn is not None
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM clients WHERE client_id = ?", (client_id,)
            ).fetchone()
        return Client.from_dict(dict(row)) if row else None

    def list_clients(self) -> List[Client]:
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute("SELECT * FROM clients").fetchall()
        return [Client.from_dict(dict(r)) for r in rows]

    def delete_client(self, client_id: str) -> bool:
        if not self.get_client(client_id):
            return False
        with self._tx() as conn:
            conn.execute("DELETE FROM clients WHERE client_id = ?", (client_id,))
        return True

    # ── Proposals CRUD & Engine ──────────────────────────────────────────────

    def create_proposal(self, proposal: Proposal) -> Proposal:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO proposals (
                    proposal_id, lead_id, title, proposal_type, status, value, content, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(proposal_id) DO UPDATE SET
                    title=excluded.title, status=excluded.status, value=excluded.value,
                    content=excluded.content, updated_at=excluded.updated_at
                """,
                (
                    proposal.proposal_id,
                    proposal.lead_id,
                    proposal.title,
                    proposal.proposal_type.value,
                    proposal.status.value,
                    proposal.value,
                    proposal.content,
                    proposal.created_at,
                    proposal.updated_at,
                ),
            )
        return proposal

    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        assert self._conn is not None
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM proposals WHERE proposal_id = ?", (proposal_id,)
            ).fetchone()
        return Proposal.from_dict(dict(row)) if row else None

    def list_proposals(self) -> List[Proposal]:
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute("SELECT * FROM proposals").fetchall()
        return [Proposal.from_dict(dict(r)) for r in rows]

    # ── Outreach CRUD & Engine ───────────────────────────────────────────────

    def create_outreach(self, outreach: Outreach) -> Outreach:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO outreach (
                    outreach_id, lead_id, contact_id, outreach_type, status, subject, body, sent_at, replied_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(outreach_id) DO UPDATE SET
                    status=excluded.status, subject=excluded.subject, body=excluded.body,
                    sent_at=excluded.sent_at, replied_at=excluded.replied_at
                """,
                (
                    outreach.outreach_id,
                    outreach.lead_id,
                    outreach.contact_id,
                    outreach.outreach_type.value,
                    outreach.status.value,
                    outreach.subject,
                    outreach.body,
                    outreach.sent_at,
                    outreach.replied_at,
                ),
            )
        return outreach

    def get_outreach(self, outreach_id: str) -> Optional[Outreach]:
        assert self._conn is not None
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM outreach WHERE outreach_id = ?", (outreach_id,)
            ).fetchone()
        return Outreach.from_dict(dict(row)) if row else None

    def list_outreach(self) -> List[Outreach]:
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute("SELECT * FROM outreach").fetchall()
        return [Outreach.from_dict(dict(r)) for r in rows]

    # ── Meetings CRUD ────────────────────────────────────────────────────────

    def create_meeting(self, meeting: Meeting) -> Meeting:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO meetings (
                    meeting_id, title, start_time, duration_min, participants,
                    company_id, agenda, notes, decisions, action_items, follow_ups, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(meeting_id) DO UPDATE SET
                    title=excluded.title, start_time=excluded.start_time,
                    duration_min=excluded.duration_min, participants=excluded.participants,
                    company_id=excluded.company_id, agenda=excluded.agenda, notes=excluded.notes,
                    decisions=excluded.decisions, action_items=excluded.action_items,
                    follow_ups=excluded.follow_ups
                """,
                (
                    meeting.meeting_id,
                    meeting.title,
                    meeting.start_time,
                    meeting.duration_min,
                    json.dumps(meeting.participants),
                    meeting.company_id,
                    meeting.agenda,
                    meeting.notes,
                    json.dumps(meeting.decisions),
                    json.dumps(meeting.action_items),
                    json.dumps(meeting.follow_ups),
                    meeting.created_at,
                ),
            )
        return meeting

    def get_meeting(self, meeting_id: str) -> Optional[Meeting]:
        assert self._conn is not None
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM meetings WHERE meeting_id = ?", (meeting_id,)
            ).fetchone()
        return Meeting.from_dict(dict(row)) if row else None

    def list_meetings(self) -> List[Meeting]:
        assert self._conn is not None
        with self._lock:
            rows = self._conn.execute("SELECT * FROM meetings").fetchall()
        return [Meeting.from_dict(dict(r)) for r in rows]

    # ── Follow-Ups CRUD ──────────────────────────────────────────────────────

    def create_followup(self, followup: FollowUp) -> FollowUp:
        with self._tx() as conn:
            conn.execute(
                """
                INSERT INTO followups (
                    followup_id, target_type, target_id, title, due_date, status, notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(followup_id) DO UPDATE SET
                    status=excluded.status, notes=excluded.notes, due_date=excluded.due_date
                """,
                (
                    followup.followup_id,
                    followup.target_type,
                    followup.target_id,
                    followup.title,
                    followup.due_date,
                    followup.status,
                    followup.notes,
                    followup.created_at,
                ),
            )
        return followup

    def get_followup(self, followup_id: str) -> Optional[FollowUp]:
        assert self._conn is not None
        with self._lock:
            row = self._conn.execute(
                "SELECT * FROM followups WHERE followup_id = ?", (followup_id,)
            ).fetchone()
        return FollowUp.from_dict(dict(row)) if row else None

    def list_followups(self, status: Optional[str] = None) -> List[FollowUp]:
        assert self._conn is not None
        query = "SELECT * FROM followups"
        params = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY due_date ASC"
        with self._lock:
            rows = self._conn.execute(query, params).fetchall()
        return [FollowUp.from_dict(dict(r)) for r in rows]

    # ── Revenue Pipeline Analysis ────────────────────────────────────────────

    def get_revenue_pipeline(self) -> Dict[str, Any]:
        """Calculates expected pipeline metrics based on current leads, clients and proposals."""
        leads = self.list_leads()
        proposals = self.list_proposals()

        expected_rev = 0.0
        closed_rev = 0.0
        proposal_val = 0.0
        lead_val = 0.0

        for l in leads:
            if l.stage == LeadStage.WON:
                closed_rev += l.expected_value
            elif l.stage != LeadStage.LOST:
                # expected = expected_value * probability based on stage
                prob = 0.1  # new
                if l.stage == LeadStage.QUALIFIED:
                    prob = 0.3
                elif l.stage == LeadStage.CONTACTED:
                    prob = 0.4
                elif l.stage == LeadStage.MEETING_SCHEDULED:
                    prob = 0.6
                elif l.stage == LeadStage.PROPOSAL_SENT:
                    prob = 0.8
                elif l.stage == LeadStage.NEGOTIATION:
                    prob = 0.9

                expected_rev += l.expected_value * prob
                lead_val += l.expected_value

        for p in proposals:
            proposal_val += p.value
            if p.status == ProposalStatus.ACCEPTED:
                closed_rev += p.value

        # Health score assessment
        total_leads = len(leads)
        active_leads = sum(1 for l in leads if l.stage not in (LeadStage.WON, LeadStage.LOST))
        health_score = 100
        if total_leads == 0:
            health_score = 50
        elif active_leads == 0:
            health_score = 60

        return {
            "expected_revenue": expected_rev,
            "closed_revenue": closed_rev,
            "proposal_value": proposal_val,
            "lead_value": lead_val,
            "pipeline_health": health_score,
        }

    # ── Outreach & Proposal Generator Helpers ────────────────────────────────

    def generate_proposal_draft(
        self,
        lead_id: str,
        ptype: ProposalType,
        custom_instructions: str = "",
    ) -> Proposal:
        """Procedurally generate specialized agency proposals."""
        lead = self.get_lead(lead_id)
        if not lead:
            raise ValueError(f"Lead with ID '{lead_id}' not found.")

        company = self.get_company(lead.company_id)
        contact = self.get_contact(lead.contact_id)

        company_name = company.name if company else "Valued Client"
        contact_name = contact.name if contact else "Decision Maker"

        title = f"{ptype.value.replace('_', ' ').title()} Proposal — {company_name}"
        value = lead.expected_value or 5000.0

        if ptype == ProposalType.COLD_EMAIL:
            content = (
                f"Subject: Scaled AI integrations and automation for {company_name}\n\n"
                f"Dear {contact_name},\n\n"
                f"Following up on our initial discussion, we propose a lightweight automations sync package.\n"
                f"Expected Budget: ${value:,.2f}.\n\n"
                f"Best,\nAI OS Agency"
            )
        elif ptype == ProposalType.AUTOMATION:
            content = (
                f"### System Automation Proposal for {company_name}\n\n"
                f"Prepared for: {contact_name}\n"
                f"Goal: Automate daily workflow sync between Notion, GitHub, and n8n.\n"
                f"Investment: ${value:,.2f} USD\n\n"
                f"1. Setup triggers for task completions.\n"
                f"2. Configure daily briefings reports."
            )
        elif ptype == ProposalType.AI_DEVELOPMENT:
            content = (
                f"### Custom AI OS Development Proposal for {company_name}\n\n"
                f"Target: Enterprise-grade intelligence routing architecture.\n"
                f"Scope: Deploy fine-tuned local reasoning model profiles.\n"
                f"Fixed Investment: ${value:,.2f} USD."
            )
        elif ptype == ProposalType.CONSULTING:
            content = (
                f"### Technology Consultation Proposal: {company_name}\n\n"
                f"Overview: Evaluation of legacy backend architectures for AI readiness.\n"
                f"Total Project Investment: ${value:,.2f} USD."
            )
        else:
            content = (
                f"Custom Project Proposal for {company_name}.\n"
                f"Instructions: {custom_instructions}\n"
                f"Investment: ${value:,.2f}"
            )

        prop = Proposal(
            proposal_id=new_id(),
            lead_id=lead_id,
            title=title,
            proposal_type=ptype,
            status=ProposalStatus.DRAFT,
            value=value,
            content=content,
        )
        self.create_proposal(prop)
        return prop

    def generate_outreach_draft(
        self,
        lead_id: str,
        otype: OutreachType,
    ) -> Outreach:
        """Generate formatted outreach messages utilizing workspace model preferences."""
        lead = self.get_lead(lead_id)
        if not lead:
            raise ValueError(f"Lead '{lead_id}' not found.")

        contact = self.get_contact(lead.contact_id)
        contact_name = contact.name if contact else "Prospect"
        company = self.get_company(lead.company_id)
        company_name = company.name if company else "Company"

        subject = ""
        body = ""

        if otype == OutreachType.COLD_EMAIL:
            subject = f"Improving automation pipelines at {company_name}"
            body = (
                f"Hi {contact_name},\n\n"
                f"I noticed {company_name} is active in robotics & tech. "
                f"We deploy local autonomous agent networks that reduce workflow friction by 40%.\n"
                f"Are you open to a brief chat next Tuesday?"
            )
        elif otype == OutreachType.FOLLOW_UP:
            subject = f"Re: Improving automation pipelines at {company_name}"
            body = (
                f"Hi {contact_name},\n\n"
                f"Following up on my previous message. Let me know if you would like a quick demo "
                f"of our local model router integration."
            )
        elif otype == OutreachType.LINKEDIN:
            body = (
                f"Hi {contact_name}, came across your profile at {company_name} and "
                f"wanted to connect regarding local AI OS developments."
            )
        elif otype == OutreachType.DISCOVERY:
            subject = f"Discovery Call: AI OS & {company_name}"
            body = (
                f"Dear {contact_name},\n\n"
                f"Before our scheduled call, we prepared a few discovery questions "
                f"to customize your automation profile."
            )
        else:  # MEETING_REQUEST
            subject = "Invitation: AI OS Automation Discovery Session"
            body = (
                f"Hi {contact_name},\n\n"
                f"Here is a meeting request link for our discovery session regarding {company_name}."
            )

        out = Outreach(
            outreach_id=new_id(),
            lead_id=lead_id,
            contact_id=lead.contact_id,
            outreach_type=otype,
            status=OutreachStatus.PENDING,
            subject=subject,
            body=body,
        )
        self.create_outreach(out)
        return out

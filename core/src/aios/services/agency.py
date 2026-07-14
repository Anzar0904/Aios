"""Phase 6: Agency Intelligence — Interfaces and Dataclasses.

Defines dataclasses and service interfaces for managing Leads, Contacts,
Companies, Clients, Meetings, Proposals, Outreach, Follow-Ups, and Revenue.
"""

from __future__ import annotations

import abc
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ContactStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DO_NOT_CONTACT = "do_not_contact"


class LeadStage(Enum):
    NEW = "new"
    QUALIFIED = "qualified"
    CONTACTED = "contacted"
    MEETING_SCHEDULED = "meeting_scheduled"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class LeadPriority(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ClientStatus(Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class ProposalType(Enum):
    COLD_EMAIL = "cold_email"
    AUTOMATION = "automation"
    AI_DEVELOPMENT = "ai_development"
    CONSULTING = "consulting"
    CUSTOM = "custom"


class ProposalStatus(Enum):
    DRAFT = "draft"
    SENT = "sent"
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class OutreachType(Enum):
    COLD_EMAIL = "cold_email"
    FOLLOW_UP = "follow_up"
    LINKEDIN = "linkedin"
    DISCOVERY = "discovery"
    MEETING_REQUEST = "meeting_request"


class OutreachStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    REPLIED = "replied"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------


@dataclass
class Contact:
    contact_id: str
    name: str
    email: str
    phone: str = ""
    company_id: str = ""
    role: str = ""
    linkedin: str = ""
    website: str = ""
    status: ContactStatus = ContactStatus.ACTIVE
    source: str = ""
    notes: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_contact: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contact_id": self.contact_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "company_id": self.company_id,
            "role": self.role,
            "linkedin": self.linkedin,
            "website": self.website,
            "status": self.status.value,
            "source": self.source,
            "notes": self.notes,
            "tags": self.tags,
            "created_at": self.created_at,
            "last_contact": self.last_contact,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Contact:
        import json as _json

        tags = data.get("tags", [])
        if isinstance(tags, str):
            try:
                tags = _json.loads(tags)
            except Exception:
                tags = []
        return cls(
            contact_id=data["contact_id"],
            name=data["name"],
            email=data["email"],
            phone=data.get("phone", ""),
            company_id=data.get("company_id", ""),
            role=data.get("role", ""),
            linkedin=data.get("linkedin", ""),
            website=data.get("website", ""),
            status=ContactStatus(data.get("status", "active")),
            source=data.get("source", ""),
            notes=data.get("notes", ""),
            tags=tags,
            created_at=data.get("created_at", time.time()),
            last_contact=data.get("last_contact", time.time()),
        )


@dataclass
class Company:
    company_id: str
    name: str
    industry: str = ""
    website: str = ""
    size: str = ""
    location: str = ""
    services: List[str] = field(default_factory=list)
    decision_makers: List[str] = field(default_factory=list)  # list of contact_ids
    lead_count: int = 0
    client_status: str = "none"  # none|active|paused|completed
    projects: List[str] = field(default_factory=list)  # list of project_ids
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_id": self.company_id,
            "name": self.name,
            "industry": self.industry,
            "website": self.website,
            "size": self.size,
            "location": self.location,
            "services": self.services,
            "decision_makers": self.decision_makers,
            "lead_count": self.lead_count,
            "client_status": self.client_status,
            "projects": self.projects,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Company:
        import json as _json

        services = data.get("services", [])
        if isinstance(services, str):
            try:
                services = _json.loads(services)
            except Exception:
                services = []

        decision_makers = data.get("decision_makers", [])
        if isinstance(decision_makers, str):
            try:
                decision_makers = _json.loads(decision_makers)
            except Exception:
                decision_makers = []

        projects = data.get("projects", [])
        if isinstance(projects, str):
            try:
                projects = _json.loads(projects)
            except Exception:
                projects = []

        return cls(
            company_id=data["company_id"],
            name=data["name"],
            industry=data.get("industry", ""),
            website=data.get("website", ""),
            size=data.get("size", ""),
            location=data.get("location", ""),
            services=services,
            decision_makers=decision_makers,
            lead_count=data.get("lead_count", 0),
            client_status=data.get("client_status", "none"),
            projects=projects,
            created_at=data.get("created_at", time.time()),
        )


@dataclass
class Lead:
    lead_id: str
    company_id: str
    contact_id: str
    title: str
    stage: LeadStage = LeadStage.NEW
    priority: LeadPriority = LeadPriority.MEDIUM
    score: int = 50
    expected_value: float = 0.0
    next_action: str = ""
    followup_date: float = 0.0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "lead_id": self.lead_id,
            "company_id": self.company_id,
            "contact_id": self.contact_id,
            "title": self.title,
            "stage": self.stage.value,
            "priority": self.priority.value,
            "score": self.score,
            "expected_value": self.expected_value,
            "next_action": self.next_action,
            "followup_date": self.followup_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Lead:
        return cls(
            lead_id=data["lead_id"],
            company_id=data["company_id"],
            contact_id=data["contact_id"],
            title=data["title"],
            stage=LeadStage(data.get("stage", "new")),
            priority=LeadPriority(data.get("priority", "medium")),
            score=data.get("score", 50),
            expected_value=data.get("expected_value", 0.0),
            next_action=data.get("next_action", ""),
            followup_date=data.get("followup_date", 0.0),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
        )


@dataclass
class Client:
    client_id: str
    company_id: str
    status: ClientStatus = ClientStatus.ACTIVE
    projects: List[str] = field(default_factory=list)  # project_ids
    meetings: List[str] = field(default_factory=list)  # meeting_ids
    invoices: List[Dict[str, Any]] = field(default_factory=list)
    contracts: List[Dict[str, Any]] = field(default_factory=list)
    documents: List[str] = field(default_factory=list)  # paths or titles
    workflows: List[str] = field(default_factory=list)  # workflow_ids
    relationship_history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "client_id": self.client_id,
            "company_id": self.company_id,
            "status": self.status.value,
            "projects": self.projects,
            "meetings": self.meetings,
            "invoices": self.invoices,
            "contracts": self.contracts,
            "documents": self.documents,
            "workflows": self.workflows,
            "relationship_history": self.relationship_history,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Client:
        import json as _json

        projects = data.get("projects", [])
        if isinstance(projects, str):
            try:
                projects = _json.loads(projects)
            except Exception:
                projects = []

        meetings = data.get("meetings", [])
        if isinstance(meetings, str):
            try:
                meetings = _json.loads(meetings)
            except Exception:
                meetings = []

        invoices = data.get("invoices", [])
        if isinstance(invoices, str):
            try:
                invoices = _json.loads(invoices)
            except Exception:
                invoices = []

        contracts = data.get("contracts", [])
        if isinstance(contracts, str):
            try:
                contracts = _json.loads(contracts)
            except Exception:
                contracts = []

        documents = data.get("documents", [])
        if isinstance(documents, str):
            try:
                documents = _json.loads(documents)
            except Exception:
                documents = []

        workflows = data.get("workflows", [])
        if isinstance(workflows, str):
            try:
                workflows = _json.loads(workflows)
            except Exception:
                workflows = []

        relationship_history = data.get("relationship_history", [])
        if isinstance(relationship_history, str):
            try:
                relationship_history = _json.loads(relationship_history)
            except Exception:
                relationship_history = []

        return cls(
            client_id=data["client_id"],
            company_id=data["company_id"],
            status=ClientStatus(data.get("status", "active")),
            projects=projects,
            meetings=meetings,
            invoices=invoices,
            contracts=contracts,
            documents=documents,
            workflows=workflows,
            relationship_history=relationship_history,
            created_at=data.get("created_at", time.time()),
        )


@dataclass
class Proposal:
    proposal_id: str
    lead_id: str
    title: str
    proposal_type: ProposalType
    status: ProposalStatus = ProposalStatus.DRAFT
    value: float = 0.0
    content: str = ""
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "lead_id": self.lead_id,
            "title": self.title,
            "proposal_type": self.proposal_type.value,
            "status": self.status.value,
            "value": self.value,
            "content": self.content,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Proposal:
        return cls(
            proposal_id=data["proposal_id"],
            lead_id=data["lead_id"],
            title=data["title"],
            proposal_type=ProposalType(data.get("proposal_type", "custom")),
            status=ProposalStatus(data.get("status", "draft")),
            value=data.get("value", 0.0),
            content=data.get("content", ""),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
        )


@dataclass
class Outreach:
    outreach_id: str
    lead_id: str
    contact_id: str
    outreach_type: OutreachType
    status: OutreachStatus = OutreachStatus.PENDING
    subject: str = ""
    body: str = ""
    sent_at: float = 0.0
    replied_at: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "outreach_id": self.outreach_id,
            "lead_id": self.lead_id,
            "contact_id": self.contact_id,
            "outreach_type": self.outreach_type.value,
            "status": self.status.value,
            "subject": self.subject,
            "body": self.body,
            "sent_at": self.sent_at,
            "replied_at": self.replied_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Outreach:
        return cls(
            outreach_id=data["outreach_id"],
            lead_id=data["lead_id"],
            contact_id=data["contact_id"],
            outreach_type=OutreachType(data.get("outreach_type", "cold_email")),
            status=OutreachStatus(data.get("status", "pending")),
            subject=data.get("subject", ""),
            body=data.get("body", ""),
            sent_at=data.get("sent_at", 0.0),
            replied_at=data.get("replied_at", 0.0),
        )


@dataclass
class Meeting:
    meeting_id: str
    title: str
    start_time: float
    duration_min: int = 30
    participants: List[str] = field(default_factory=list)  # list of contact_ids
    company_id: str = ""
    agenda: str = ""
    notes: str = ""
    decisions: List[str] = field(default_factory=list)
    action_items: List[Dict[str, Any]] = field(default_factory=list)
    follow_ups: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "meeting_id": self.meeting_id,
            "title": self.title,
            "start_time": self.start_time,
            "duration_min": self.duration_min,
            "participants": self.participants,
            "company_id": self.company_id,
            "agenda": self.agenda,
            "notes": self.notes,
            "decisions": self.decisions,
            "action_items": self.action_items,
            "follow_ups": self.follow_ups,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Meeting:
        import json as _json

        participants = data.get("participants", [])
        if isinstance(participants, str):
            try:
                participants = _json.loads(participants)
            except Exception:
                participants = []

        decisions = data.get("decisions", [])
        if isinstance(decisions, str):
            try:
                decisions = _json.loads(decisions)
            except Exception:
                decisions = []

        action_items = data.get("action_items", [])
        if isinstance(action_items, str):
            try:
                action_items = _json.loads(action_items)
            except Exception:
                action_items = []

        follow_ups = data.get("follow_ups", [])
        if isinstance(follow_ups, str):
            try:
                follow_ups = _json.loads(follow_ups)
            except Exception:
                follow_ups = []

        return cls(
            meeting_id=data["meeting_id"],
            title=data["title"],
            start_time=data["start_time"],
            duration_min=data.get("duration_min", 30),
            participants=participants,
            company_id=data.get("company_id", ""),
            agenda=data.get("agenda", ""),
            notes=data.get("notes", ""),
            decisions=decisions,
            action_items=action_items,
            follow_ups=follow_ups,
            created_at=data.get("created_at", time.time()),
        )


@dataclass
class FollowUp:
    followup_id: str
    target_type: str  # lead|proposal|client|meeting
    target_id: str
    title: str
    due_date: float
    status: str = "pending"  # pending|completed|overdue
    notes: str = ""
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "followup_id": self.followup_id,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "title": self.title,
            "due_date": self.due_date,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> FollowUp:
        return cls(
            followup_id=data["followup_id"],
            target_type=data["target_type"],
            target_id=data["target_id"],
            title=data["title"],
            due_date=data["due_date"],
            status=data.get("status", "pending"),
            notes=data.get("notes", ""),
            created_at=data.get("created_at", time.time()),
        )


# ---------------------------------------------------------------------------
# Factory Helpers
# ---------------------------------------------------------------------------


def new_id() -> str:
    return str(uuid.uuid4())


# ---------------------------------------------------------------------------
# Service Interfaces
# ---------------------------------------------------------------------------


class AgencyCRMService(ServiceLifecycle, abc.ABC):
    """Core CRM layer storing contacts, companies, leads, clients, and meetings."""

    # ── Contacts ─────────────────────────────────────────────────────────────
    @abc.abstractmethod
    def create_contact(self, contact: Contact) -> Contact:
        """Create or update a contact in the database."""

    @abc.abstractmethod
    def get_contact(self, contact_id: str) -> Optional[Contact]:
        """Fetch a contact by ID."""

    @abc.abstractmethod
    def list_contacts(self) -> List[Contact]:
        """List all contacts."""

    @abc.abstractmethod
    def delete_contact(self, contact_id: str) -> bool:
        """Delete a contact."""

    # ── Companies ────────────────────────────────────────────────────────────
    @abc.abstractmethod
    def create_company(self, company: Company) -> Company:
        """Create or update a company."""

    @abc.abstractmethod
    def get_company(self, company_id: str) -> Optional[Company]:
        """Fetch a company by ID."""

    @abc.abstractmethod
    def list_companies(self) -> List[Company]:
        """List all companies."""

    @abc.abstractmethod
    def delete_company(self, company_id: str) -> bool:
        """Delete a company."""

    # ── Leads ────────────────────────────────────────────────────────────────
    @abc.abstractmethod
    def create_lead(self, lead: Lead) -> Lead:
        """Create or update a lead."""

    @abc.abstractmethod
    def get_lead(self, lead_id: str) -> Optional[Lead]:
        """Fetch a lead by ID."""

    @abc.abstractmethod
    def list_leads(self) -> List[Lead]:
        """List all leads."""

    @abc.abstractmethod
    def delete_lead(self, lead_id: str) -> bool:
        """Delete a lead."""

    # ── Clients ──────────────────────────────────────────────────────────────
    @abc.abstractmethod
    def create_client(self, client: Client) -> Client:
        """Create or update a client."""

    @abc.abstractmethod
    def get_client(self, client_id: str) -> Optional[Client]:
        """Fetch a client by ID."""

    @abc.abstractmethod
    def list_clients(self) -> List[Client]:
        """List all clients."""

    @abc.abstractmethod
    def delete_client(self, client_id: str) -> bool:
        """Delete a client."""

    # ── Meetings ─────────────────────────────────────────────────────────────
    @abc.abstractmethod
    def create_meeting(self, meeting: Meeting) -> Meeting:
        """Create or update a meeting."""

    @abc.abstractmethod
    def get_meeting(self, meeting_id: str) -> Optional[Meeting]:
        """Fetch a meeting by ID."""

    @abc.abstractmethod
    def list_meetings(self) -> List[Meeting]:
        """List all meetings."""

    # ── Proposals & Outreach ────────────────────────────────────────────────
    @abc.abstractmethod
    def create_proposal(self, proposal: Proposal) -> Proposal:
        """Store a proposal."""

    @abc.abstractmethod
    def get_proposal(self, proposal_id: str) -> Optional[Proposal]:
        """Fetch a proposal."""

    @abc.abstractmethod
    def list_proposals(self) -> List[Proposal]:
        """List all proposals."""

    @abc.abstractmethod
    def create_outreach(self, outreach: Outreach) -> Outreach:
        """Store outreach log."""

    @abc.abstractmethod
    def get_outreach(self, outreach_id: str) -> Optional[Outreach]:
        """Fetch outreach."""

    @abc.abstractmethod
    def list_outreach(self) -> List[Outreach]:
        """List outreach attempts."""

    # ── Follow-Ups ───────────────────────────────────────────────────────────
    @abc.abstractmethod
    def create_followup(self, followup: FollowUp) -> FollowUp:
        """Store a follow-up action."""

    @abc.abstractmethod
    def get_followup(self, followup_id: str) -> Optional[FollowUp]:
        """Fetch follow-up."""

    @abc.abstractmethod
    def list_followups(self, status: Optional[str] = None) -> List[FollowUp]:
        """List follow-ups."""

    # ── Analytics & Revenue ──────────────────────────────────────────────────
    @abc.abstractmethod
    def get_revenue_pipeline(self) -> Dict[str, Any]:
        """Calculate and retrieve expected, closed, proposed, and total pipeline values."""

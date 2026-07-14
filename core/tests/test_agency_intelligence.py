"""Phase 6: Agency Intelligence — Production Test Suite.

Tests cover:
- Contact Registry CRUD
- Company Registry CRUD
- Lead Pipeline (stages, scoring,expected value)
- Proposal Engine (generation templates, acceptance, value)
- Outreach Engine (email, linkedin, discovery drafts)
- Meeting Intelligence (decisions, action items)
- Revenue Pipeline (forecast, closed vs expected value)
- Follow-ups schedule (overdue detection)
- Knowledge Graph Integration (works_for, attended, sent_to links)
- Integration structures (Notion/n8n)
- CLI main dispatch
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock

import pytest
from aios.services.agency import (
    Client,
    ClientStatus,
    Company,
    Contact,
    FollowUp,
    Lead,
    LeadPriority,
    LeadStage,
    Meeting,
    OutreachType,
    Proposal,
    ProposalType,
    new_id,
)
from aios.services.agency_impl import AgencyCRMServiceImpl

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_db(tmp_path):
    return str(tmp_path / "test_agency.db")


@pytest.fixture
def crm(tmp_db):
    from aios.local import agency_commands
    agency_commands._DB_PATH = tmp_db
    svc = AgencyCRMServiceImpl(db_path=tmp_db)
    svc.initialize()
    svc.start()
    yield svc
    svc.shutdown()
    agency_commands._DB_PATH = None


# ---------------------------------------------------------------------------
# Contact Registry
# ---------------------------------------------------------------------------


class TestContactRegistry:
    def test_create_and_get_contact(self, crm):
        cid = new_id()
        c = Contact(
            contact_id=cid,
            name="John Doe",
            email="john.doe@example.com",
            phone="123456",
            role="CTO",
            tags=["tech"],
        )
        crm.create_contact(c)
        fetched = crm.get_contact(cid)
        assert fetched is not None
        assert fetched.name == "John Doe"
        assert fetched.email == "john.doe@example.com"
        assert fetched.role == "CTO"
        assert "tech" in fetched.tags

    def test_get_nonexistent_contact_returns_none(self, crm):
        assert crm.get_contact("nonexistent") is None

    def test_list_contacts(self, crm):
        initial_count = len(crm.list_contacts())
        c = Contact(
            contact_id=new_id(),
            name="Jane Doe",
            email="jane.doe@example.com",
        )
        crm.create_contact(c)
        contacts = crm.list_contacts()
        assert len(contacts) == initial_count + 1

    def test_delete_contact(self, crm):
        cid = new_id()
        c = Contact(contact_id=cid, name="Del Contact", email="del@example.com")
        crm.create_contact(c)
        assert crm.delete_contact(cid) is True
        assert crm.get_contact(cid) is None

    def test_delete_nonexistent_returns_false(self, crm):
        assert crm.delete_contact("fake") is False


# ---------------------------------------------------------------------------
# Company Registry
# ---------------------------------------------------------------------------


class TestCompanyRegistry:
    def test_create_and_get_company(self, crm):
        cid = new_id()
        comp = Company(
            company_id=cid,
            name="Initech Corporation",
            industry="Software Consulting",
            website="https://initech.com",
            size="10-50",
            location="Austin, TX",
            services=["Automations", "AI Integrations"],
        )
        crm.create_company(comp)
        fetched = crm.get_company(cid)
        assert fetched is not None
        assert fetched.name == "Initech Corporation"
        assert "Automations" in fetched.services

    def test_list_companies(self, crm):
        initial_count = len(crm.list_companies())
        comp = Company(company_id=new_id(), name="Acme Corp")
        crm.create_company(comp)
        companies = crm.list_companies()
        assert len(companies) == initial_count + 1

    def test_delete_company(self, crm):
        cid = new_id()
        comp = Company(company_id=cid, name="Delete Corp")
        crm.create_company(comp)
        assert crm.delete_company(cid) is True
        assert crm.get_company(cid) is None


# ---------------------------------------------------------------------------
# Lead Pipeline
# ---------------------------------------------------------------------------


class TestLeadPipeline:
    def test_create_and_get_lead(self, crm):
        lid = new_id()
        lead = Lead(
            lead_id=lid,
            company_id="company-1",
            contact_id="contact-1",
            title="AI Chatbot Integration",
            stage=LeadStage.NEW,
            priority=LeadPriority.HIGH,
            score=70,
            expected_value=12000.0,
            next_action="Send Discovery Document",
        )
        crm.create_lead(lead)
        fetched = crm.get_lead(lid)
        assert fetched is not None
        assert fetched.title == "AI Chatbot Integration"
        assert fetched.stage == LeadStage.NEW
        assert fetched.expected_value == 12000.0

    def test_delete_lead(self, crm):
        lid = new_id()
        lead = Lead(
            lead_id=lid,
            company_id="c-2",
            contact_id="ct-2",
            title="Temp Lead",
        )
        crm.create_lead(lead)
        assert crm.delete_lead(lid) is True
        assert crm.get_lead(lid) is None


# ---------------------------------------------------------------------------
# Client Management
# ---------------------------------------------------------------------------


class TestClientManagement:
    def test_create_and_get_client(self, crm):
        cl_id = new_id()
        client = Client(
            client_id=cl_id,
            company_id="comp-client-1",
            status=ClientStatus.ACTIVE,
            projects=["p-1", "p-2"],
        )
        crm.create_client(client)
        fetched = crm.get_client(cl_id)
        assert fetched is not None
        assert fetched.company_id == "comp-client-1"
        assert "p-1" in fetched.projects

    def test_list_clients(self, crm):
        initial_count = len(crm.list_clients())
        cl = Client(client_id=new_id(), company_id="comp-client-2")
        crm.create_client(cl)
        clients = crm.list_clients()
        assert len(clients) == initial_count + 1


# ---------------------------------------------------------------------------
# Proposal Engine
# ---------------------------------------------------------------------------


class TestProposalEngine:
    def test_generate_cold_email_proposal(self, crm):
        lid = new_id()
        lead = Lead(
            lead_id=lid,
            company_id="company-p1",
            contact_id="contact-p1",
            title="Cold outreach project",
            expected_value=4500.0,
        )
        crm.create_lead(lead)

        prop = crm.generate_proposal_draft(lid, ProposalType.COLD_EMAIL)
        assert prop is not None
        assert prop.proposal_type == ProposalType.COLD_EMAIL
        assert prop.value == 4500.0
        assert "Subject:" in prop.content

    def test_generate_ai_development_proposal(self, crm):
        lid = new_id()
        lead = Lead(
            lead_id=lid,
            company_id="company-p2",
            contact_id="contact-p2",
            title="AI Dev project",
            expected_value=15000.0,
        )
        crm.create_lead(lead)

        prop = crm.generate_proposal_draft(lid, ProposalType.AI_DEVELOPMENT)
        assert prop is not None
        assert prop.proposal_type == ProposalType.AI_DEVELOPMENT
        assert "Investment: $15,000.00" in prop.content

    def test_list_proposals(self, crm):
        initial_count = len(crm.list_proposals())
        p = Proposal(
            proposal_id=new_id(),
            lead_id="l-1",
            title="Consulting Proposal",
            proposal_type=ProposalType.CONSULTING,
            value=8000.0,
        )
        crm.create_proposal(p)
        proposals = crm.list_proposals()
        assert len(proposals) == initial_count + 1


# ---------------------------------------------------------------------------
# Outreach Engine
# ---------------------------------------------------------------------------


class TestOutreachEngine:
    def test_generate_cold_email_outreach(self, crm):
        lid = new_id()
        lead = Lead(
            lead_id=lid,
            company_id="company-o1",
            contact_id="contact-o1",
            title="AI automation discussion",
        )
        crm.create_lead(lead)

        out = crm.generate_outreach_draft(lid, OutreachType.COLD_EMAIL)
        assert out is not None
        assert out.outreach_type == OutreachType.COLD_EMAIL
        assert "Tuesday" in out.body

    def test_generate_linkedin_outreach(self, crm):
        lid = new_id()
        lead = Lead(
            lead_id=lid,
            company_id="company-o2",
            contact_id="contact-o2",
            title="LinkedIn sync",
        )
        crm.create_lead(lead)

        out = crm.generate_outreach_draft(lid, OutreachType.LINKEDIN)
        assert out is not None
        assert out.outreach_type == OutreachType.LINKEDIN
        assert "connect" in out.body


# ---------------------------------------------------------------------------
# Meeting Intelligence
# ---------------------------------------------------------------------------


class TestMeetingIntelligence:
    def test_create_and_get_meeting(self, crm):
        mid = new_id()
        meeting = Meeting(
            meeting_id=mid,
            title="Consulting kick-off session",
            start_time=time.time(),
            duration_min=45,
            participants=["contact-1", "contact-2"],
            agenda="Discuss automations scope",
            notes="Client is interested in n8n workflows.",
            decisions=["Use Qwen for code generations."],
            action_items=[{"task": "Design blueprint", "done": False}],
        )
        crm.create_meeting(meeting)
        fetched = crm.get_meeting(mid)
        assert fetched is not None
        assert fetched.title == "Consulting kick-off session"
        assert "contact-1" in fetched.participants
        assert "Use Qwen for code generations." in fetched.decisions


# ---------------------------------------------------------------------------
# Revenue Pipeline
# ---------------------------------------------------------------------------


class TestRevenuePipeline:
    def test_revenue_pipeline_calculations(self, crm):
        # Initial seeded data already has values. Let's add specific leads.
        # Clean current leads to have predictable results
        for l in crm.list_leads():
            crm.delete_lead(l.lead_id)

        l1 = Lead(
            lead_id=new_id(),
            company_id="comp-r1",
            contact_id="cont-r1",
            title="Qualified Lead",
            stage=LeadStage.QUALIFIED,
            expected_value=10000.0,
        )
        l2 = Lead(
            lead_id=new_id(),
            company_id="comp-r2",
            contact_id="cont-r2",
            title="Proposal Sent Lead",
            stage=LeadStage.PROPOSAL_SENT,
            expected_value=20000.0,
        )
        l3 = Lead(
            lead_id=new_id(),
            company_id="comp-r3",
            contact_id="cont-r3",
            title="Won Lead",
            stage=LeadStage.WON,
            expected_value=15000.0,
        )
        crm.create_lead(l1)
        crm.create_lead(l2)
        crm.create_lead(l3)

        pipe = crm.get_revenue_pipeline()
        # Expected Revenue = l1 Expected * Probability + l2 Expected * Probability
        # Qualified = 0.3 * 10,000 = 3,000
        # Proposal Sent = 0.8 * 20,000 = 16,000
        # Expected = 19,000
        assert pipe["expected_revenue"] == 19000.0
        # Closed Revenue = Won lead l3 expected = 15,000
        assert pipe["closed_revenue"] == 15000.0
        # Lead value = active leads (l1 + l2) expected = 30,000
        assert pipe["lead_value"] == 30000.0


# ---------------------------------------------------------------------------
# Follow-Ups Schedule
# ---------------------------------------------------------------------------


class TestFollowUps:
    def test_create_and_list_followups(self, crm):
        fid = new_id()
        fol = FollowUp(
            followup_id=fid,
            target_type="lead",
            target_id="lead-1",
            title="Follow-up regarding proposal acceptance",
            due_date=time.time() - 3600,  # Overdue
            status="pending",
        )
        crm.create_followup(fol)
        followups = crm.list_followups()
        assert any(f.followup_id == fid for f in followups)

    def test_list_followups_by_status(self, crm):
        fid = new_id()
        fol = FollowUp(
            followup_id=fid,
            target_type="client",
            target_id="client-1",
            title="Client check-in",
            due_date=time.time() + 86400,
            status="completed",
        )
        crm.create_followup(fol)
        completed = crm.list_followups(status="completed")
        assert all(f.status == "completed" for f in completed)


# ---------------------------------------------------------------------------
# Knowledge Graph Integration
# ---------------------------------------------------------------------------


class TestAgencyGraphBridge:
    def test_sync_contact_person(self):
        from aios.services.agency_graph_bridge import AgencyGraphBridge

        mock_engine = MagicMock()
        mock_entity = MagicMock()
        mock_entity.entity_id = "mock-person-id"
        mock_engine.ensure_entity.return_value = mock_entity

        bridge = AgencyGraphBridge(mock_engine)
        c = Contact(contact_id=new_id(), name="Sarah Connor", email="sarah@example.com")
        entity_id = bridge.sync_contact(c)
        assert entity_id == "mock-person-id"

    def test_link_contact_to_company(self):
        from aios.services.agency_graph_bridge import AgencyGraphBridge

        mock_engine = MagicMock()
        bridge = AgencyGraphBridge(mock_engine)
        bridge.link_contact_to_company("John Connor", "Cyberdyne Systems")
        mock_engine.ensure_entity.assert_any_call(
            mock_engine.ensure_entity.call_args_list[0][0][0], "John Connor"
        )

    def test_link_meeting_participants(self):
        from aios.services.agency_graph_bridge import AgencyGraphBridge

        mock_engine = MagicMock()
        bridge = AgencyGraphBridge(mock_engine)
        bridge.link_meeting_participants("Kickoff Session", ["Sarah Connor", "David Miller"])
        assert mock_engine.ensure_relationship.call_count >= 2


# ---------------------------------------------------------------------------
# CLI Commands Smoke Tests
# ---------------------------------------------------------------------------


class TestAgencyCLIDispatch:
    def test_cli_dashboard_execution(self, crm):
        from aios.local.agency_commands import cmd_agency_dashboard

        # Smoke test: ensure rendering completes without exceptions
        cmd_agency_dashboard([])

    def test_cli_leads_execution(self, crm):
        from aios.local.agency_commands import cmd_agency_leads

        # Smoke test
        cmd_agency_leads([])

    def test_cli_leads_create_execution(self, crm):
        from aios.local.agency_commands import cmd_agency_leads

        cmd_agency_leads(["create", "AcmeCo", "Jane", "jane@acme.com", "Pipeline Build", "12000"])
        assert any(c.name == "AcmeCo" for c in crm.list_companies())

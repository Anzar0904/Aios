"""Phase 6: Agency Intelligence — Graph Integration.

Bridges the CRM/Agency database engine with the Phase 4.5 Knowledge Graph.
Synchronizes contacts, companies, leads, proposals, clients, meetings, and
contracts into graph entities with WORKS_FOR, ATTENDED, SENT_TO, and RELATED_TO relationships.
"""

from __future__ import annotations

import logging
from typing import List

from aios.services.agency import Company, Contact, Meeting, Proposal
from aios.services.graph import EntityType, RelationshipType
from aios.services.graph_query import GraphQueryEngine

logger = logging.getLogger(__name__)


class AgencyGraphBridge:
    """Synchronizes CRM entities and operations to the Universal Knowledge Graph."""

    def __init__(self, graph_engine: GraphQueryEngine) -> None:
        self._engine = graph_engine

    def sync_contact(self, contact: Contact) -> str:
        """Create or update a PERSON node in the graph."""
        try:
            props = {
                "email": contact.email,
                "phone": contact.phone,
                "role": contact.role,
                "linkedin": contact.linkedin,
                "source": contact.source,
                "tags": contact.tags,
            }
            entity = self._engine.ensure_entity(EntityType.PERSON, contact.name, props)
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync contact to graph: %s", exc)
            return ""

    def sync_company(self, company: Company) -> str:
        """Create or update a COMPANY node in the graph."""
        try:
            props = {
                "industry": company.industry,
                "website": company.website,
                "size": company.size,
                "location": company.location,
                "services": company.services,
                "client_status": company.client_status,
            }
            entity = self._engine.ensure_entity(EntityType.COMPANY, company.name, props)
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync company to graph: %s", exc)
            return ""

    def sync_lead(self, lead_title: str, expected_value: float, priority_val: str) -> str:
        """Create or update a LEAD node in the graph."""
        try:
            props = {
                "expected_value": expected_value,
                "priority": priority_val,
            }
            entity = self._engine.ensure_entity(EntityType.LEAD, lead_title, props)
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync lead to graph: %s", exc)
            return ""

    def sync_meeting(self, meeting: Meeting) -> str:
        """Create or update a MEETING node in the graph."""
        try:
            props = {
                "start_time": meeting.start_time,
                "duration_min": meeting.duration_min,
                "agenda": meeting.agenda,
            }
            entity = self._engine.ensure_entity(EntityType.MEETING, meeting.title, props)
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync meeting to graph: %s", exc)
            return ""

    def sync_proposal(self, proposal: Proposal) -> str:
        """Create or update a PROPOSAL node in the graph."""
        try:
            props = {
                "value": proposal.value,
                "proposal_type": proposal.proposal_type.value,
                "status": proposal.status.value,
            }
            entity = self._engine.ensure_entity(EntityType.PROPOSAL, proposal.title, props)
            return entity.entity_id
        except Exception as exc:
            logger.warning("Failed to sync proposal to graph: %s", exc)
            return ""

    def link_contact_to_company(self, contact_name: str, company_name: str) -> None:
        """Create WORKS_FOR relationship from person to company."""
        try:
            person = self._engine.ensure_entity(EntityType.PERSON, contact_name)
            company = self._engine.ensure_entity(EntityType.COMPANY, company_name)
            self._engine.ensure_relationship(
                person.entity_id, company.entity_id, RelationshipType.WORKS_FOR
            )
        except Exception as exc:
            logger.warning("Failed to link contact to company: %s", exc)

    def link_meeting_participants(self, meeting_title: str, participant_names: List[str]) -> None:
        """Link participants to a meeting via ATTENDED edges."""
        try:
            meeting = self._engine.ensure_entity(EntityType.MEETING, meeting_title)
            for name in participant_names:
                person = self._engine.ensure_entity(EntityType.PERSON, name)
                self._engine.ensure_relationship(
                    person.entity_id, meeting.entity_id, RelationshipType.ATTENDED
                )
        except Exception as exc:
            logger.warning("Failed to link meeting participants: %s", exc)

    def link_proposal_to_lead(self, proposal_title: str, lead_title: str) -> None:
        """Link proposal to lead via RELATED_TO."""
        try:
            prop = self._engine.ensure_entity(EntityType.PROPOSAL, proposal_title)
            lead = self._engine.ensure_entity(EntityType.LEAD, lead_title)
            self._engine.ensure_relationship(
                prop.entity_id, lead.entity_id, RelationshipType.RELATED_TO
            )
        except Exception as exc:
            logger.warning("Failed to link proposal to lead: %s", exc)

from __future__ import annotations

import abc
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle


@dataclass
class Source:
    url: str
    title: str
    snippet: str
    content: str
    score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Citation:
    source_url: str
    text: str
    offset: int = 0


@dataclass
class ResearchResult:
    query: str
    sources: List[Source] = field(default_factory=list)
    report: str = ""
    citations: List[Citation] = field(default_factory=list)
    created_at: float = 0.0


class SearchProvider(abc.ABC):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Name of the search provider."""
        pass

    @abc.abstractmethod
    def search(self, query: str, limit: int = 5) -> List[Source]:
        """Performs a search query and returns list of source results."""
        pass


class SecurityBoundaryViolation(Exception):  # noqa: N818
    """Raised when an outbound HTTP request violates security boundaries (e.g. SSRF)."""

    pass


@dataclass
class ResearchDocument:
    document_id: str
    source_uri: str
    source_category: str  # e.g., 'DOCUMENTATION', 'API', 'SPECIFICATION', 'RFC'
    title: str
    markdown_content: str
    sha256: str
    author: Optional[str] = None
    published_at: Optional[float] = None
    cached_at: Optional[float] = None


@dataclass
class VerificationResult:
    claim: str
    confidence_score: float
    verification_status: str  # 'VERIFIED', 'CONFLICTING', 'UNVERIFIED'
    consensus_score: float
    direct_validation: float
    age_decay_factor: float
    source_credibility_score: float
    citations: List[Dict[str, Any]] = field(default_factory=list)
    contradictions: List[str] = field(default_factory=list)


@dataclass
class RawResource:
    uri: str
    content_type: str
    content_bytes: bytes
    status_code: int = 200


class KnowledgeAcquisitionProvider(abc.ABC):
    @abc.abstractmethod
    def get_provider_name(self) -> str:
        """Return provider identifier (e.g. 'arxiv', 'github_issues', 'web_scraper')."""
        pass

    @abc.abstractmethod
    def acquire_resource(self, source_uri: str) -> RawResource:
        """Download raw content (HTML, PDF, JSON) from target URI."""
        pass

    @abc.abstractmethod
    def parse_to_markdown(self, raw_resource: RawResource) -> str:
        """Clean raw content, stripping HTML tags, scripts, and adverts, returning clean MD."""
        pass


class ResearchIntelligenceService(abc.ABC):
    @abc.abstractmethod
    def search(self, query: str, limit: int = 5) -> List[ResearchDocument]:
        """Search cached research database and query external providers on cache miss."""
        pass

    @abc.abstractmethod
    def fetch_document(self, url: str) -> ResearchDocument:
        """Retrieve document from url, parse content to markdown, and run verification."""
        pass

    @abc.abstractmethod
    def verify_claim(self, claim: str) -> VerificationResult:
        """Cross-reference a technical claim against local databases and official RFC specs."""
        pass


class ResearchService(ServiceLifecycle, ResearchIntelligenceService, abc.ABC):
    @abc.abstractmethod
    def register_provider(self, provider: SearchProvider) -> None:
        """Registers an external or local search provider."""
        pass

    @abc.abstractmethod
    def research(self, query: str, limit: int = 5) -> ResearchResult:
        """Decomposes queries, gathers sources, deduplicates/ranks them,
        and generates a cited report.
        """
        pass

    # ── Phase 10 Research Intelligence Extensions ───────────────────────────

    @abc.abstractmethod
    def create_research_project(self, project: ResearchProject) -> ResearchProject:
        """Register a new research project profile."""

    @abc.abstractmethod
    def get_research_project(self, research_id: str) -> Optional[ResearchProject]:
        """Fetch research project profile."""

    @abc.abstractmethod
    def list_research_projects(self) -> List[ResearchProject]:
        """List active research projects."""

    @abc.abstractmethod
    def ingest_paper(self, paper: IngestedPaper) -> IngestedPaper:
        """Register parsed academic or methodology paper."""

    @abc.abstractmethod
    def list_papers(self, research_id: str) -> List[IngestedPaper]:
        """List papers associated with a project."""

    @abc.abstractmethod
    def synthesize_knowledge(self, research_id: str) -> Dict[str, Any]:
        """Merge ingested papers to summarize patterns, contradictions, and recommendations."""

    @abc.abstractmethod
    def record_learning_summary(self, summary: LearningSummary) -> LearningSummary:
        """Log lessons learned summary."""

    @abc.abstractmethod
    def list_learning_summaries(self, research_id: str) -> List[LearningSummary]:
        """Fetch learning history of a project."""


# ── Phase 10 Data Models ───────────────────────────────────────────────────


@dataclass
class ResearchProject:
    research_id: str
    title: str
    category: str  # deep_learning|nlp|systems|agentic
    topic: str
    status: str = "active"  # active|completed|suspended
    priority: int = 1  # 1-5 scale
    owner: str = "admin"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    knowledge_sources: List[str] = field(default_factory=list)
    project_ids: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "research_id": self.research_id,
            "title": self.title,
            "category": self.category,
            "topic": self.topic,
            "status": self.status,
            "priority": self.priority,
            "owner": self.owner,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "knowledge_sources": self.knowledge_sources,
            "project_ids": self.project_ids,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ResearchProject:
        import json as _json

        knowledge_sources = data.get("knowledge_sources", [])
        if isinstance(knowledge_sources, str):
            try:
                knowledge_sources = _json.loads(knowledge_sources)
            except Exception:
                knowledge_sources = []

        project_ids = data.get("project_ids", [])
        if isinstance(project_ids, str):
            try:
                project_ids = _json.loads(project_ids)
            except Exception:
                project_ids = []

        return cls(
            research_id=data["research_id"],
            title=data["title"],
            category=data["category"],
            topic=data["topic"],
            status=data.get("status", "active"),
            priority=data.get("priority", 1),
            owner=data.get("owner", "admin"),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            knowledge_sources=knowledge_sources,
            project_ids=project_ids,
        )


@dataclass
class IngestedPaper:
    paper_id: str
    research_id: str
    title: str
    authors: List[str] = field(default_factory=list)
    summary: str = ""
    methodology: str = ""
    findings: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "paper_id": self.paper_id,
            "research_id": self.research_id,
            "title": self.title,
            "authors": self.authors,
            "summary": self.summary,
            "methodology": self.methodology,
            "findings": self.findings,
            "citations": self.citations,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> IngestedPaper:
        import json as _json

        authors = data.get("authors", [])
        if isinstance(authors, str):
            try:
                authors = _json.loads(authors)
            except Exception:
                authors = []

        findings = data.get("findings", [])
        if isinstance(findings, str):
            try:
                findings = _json.loads(findings)
            except Exception:
                findings = []

        citations = data.get("citations", [])
        if isinstance(citations, str):
            try:
                citations = _json.loads(citations)
            except Exception:
                citations = []

        return cls(
            paper_id=data["paper_id"],
            research_id=data["research_id"],
            title=data["title"],
            authors=authors,
            summary=data.get("summary", ""),
            methodology=data.get("methodology", ""),
            findings=findings,
            citations=citations,
            timestamp=data.get("timestamp", time.time()),
        )


@dataclass
class LearningSummary:
    summary_id: str
    research_id: str
    topics: List[str] = field(default_factory=list)
    successful_findings: List[str] = field(default_factory=list)
    failed_experiments: List[str] = field(default_factory=list)
    lessons_learned: str = ""
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary_id": self.summary_id,
            "research_id": self.research_id,
            "topics": self.topics,
            "successful_findings": self.successful_findings,
            "failed_experiments": self.failed_experiments,
            "lessons_learned": self.lessons_learned,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LearningSummary:
        import json as _json

        topics = data.get("topics", [])
        if isinstance(topics, str):
            try:
                topics = _json.loads(topics)
            except Exception:
                topics = []

        successful_findings = data.get("successful_findings", [])
        if isinstance(successful_findings, str):
            try:
                successful_findings = _json.loads(successful_findings)
            except Exception:
                successful_findings = []

        failed_experiments = data.get("failed_experiments", [])
        if isinstance(failed_experiments, str):
            try:
                failed_experiments = _json.loads(failed_experiments)
            except Exception:
                failed_experiments = []

        return cls(
            summary_id=data["summary_id"],
            research_id=data["research_id"],
            topics=topics,
            successful_findings=successful_findings,
            failed_experiments=failed_experiments,
            lessons_learned=data.get("lessons_learned", ""),
            timestamp=data.get("timestamp", time.time()),
        )


def new_id() -> str:
    import uuid as _uuid

    return str(_uuid.uuid4())

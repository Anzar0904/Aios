import abc
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

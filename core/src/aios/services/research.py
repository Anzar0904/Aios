import abc
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

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


class ResearchService(ServiceLifecycle, abc.ABC):
    @abc.abstractmethod
    def register_provider(self, provider: SearchProvider) -> None:
        """Registers an external or local search provider."""
        pass

    @abc.abstractmethod
    def research(self, query: str, limit: int = 5) -> ResearchResult:
        """Decomposes queries, gathers sources, deduplicates/ranks them, and generates a cited report."""
        pass

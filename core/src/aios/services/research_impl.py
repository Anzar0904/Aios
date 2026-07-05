import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

from aios.services.model import LLMRequest, ModelService
from aios.services.research import Source, Citation, ResearchResult, SearchProvider, ResearchService


class MockSearchProvider(SearchProvider):
    @property
    def name(self) -> str:
        return "mock_search"

    def search(self, query: str, limit: int = 5) -> List[Source]:
        q_lower = query.lower()
        if "event" in q_lower or "bus" in q_lower:
            return [
                Source(
                    url="https://docs.aios.dev/architecture/event-bus",
                    title="LocalEventBus Specs",
                    snippet="LocalEventBus handles low-overhead asynchronous signaling inside Personal AI OS.",
                    content="LocalEventBus implements publish-subscribe patterns locally using Python. Handlers register callbacks on topics.",
                    score=0.9
                ),
                Source(
                    url="https://nats.io/documentation",
                    title="NATS Streaming Comparison",
                    snippet="NATS provides distributed clustering event publishing, whereas LocalEventBus is purely in-process.",
                    content="NATS messaging is designed for multi-node microservices. LocalEventBus is single-process for minimal OS overhead.",
                    score=0.85
                )
            ]
        elif "git" in q_lower or "version" in q_lower:
            return [
                Source(
                    url="https://git-scm.com/docs",
                    title="Git SCM Documentation",
                    snippet="Git is a free and open source distributed version control system.",
                    content="Git coordinates commits, branches, and merges using local trees.",
                    score=0.8
                )
            ]
        return [
            Source(
                url="https://en.wikipedia.org/wiki/Artificial_intelligence",
                title="Artificial Intelligence Basics",
                snippet="AI covers deep learning, NLP, and reasoning models.",
                content="Artificial intelligence is intelligence demonstrated by machines, matching human cognitive capacities.",
                score=0.5
            )
        ]


class LocalResearchService(ResearchService):
    def __init__(self, model_service: ModelService, cache_filename: str = "research_cache.json", workspace_root: str = ".", registry: Optional[Any] = None) -> None:
        self._model_service = model_service
        self._cache_filename = cache_filename
        self._workspace_root = workspace_root
        self._providers: List[SearchProvider] = []
        self._registry = registry


    def initialize(self) -> None:
        self.register_provider(MockSearchProvider())

    def register_provider(self, provider: SearchProvider) -> None:
        self._providers.append(provider)

    def research(self, query: str, limit: int = 5) -> ResearchResult:
        cache_path = Path(self._workspace_root) / self._cache_filename
        result = None

        # Load cache
        if cache_path.is_file():
            try:
                cache_data = json.loads(cache_path.read_text(encoding="utf-8"))
                if query in cache_data:
                    entry = cache_data[query]
                    sources = [Source(**s) for s in entry["sources"]]
                    citations = [Citation(**c) for c in entry["citations"]]
                    result = ResearchResult(
                        query=query,
                        sources=sources,
                        report=entry["report"],
                        citations=citations,
                        created_at=entry["created_at"]
                    )
            except Exception:
                pass

        if result is None:
            # 1. Search Query Planner: plan sub-queries
            sub_queries = self._plan_queries(query)

            # 2. Gather sources from all providers
            raw_sources = []
            for provider in self._providers:
                for sub_q in sub_queries:
                    try:
                        results = provider.search(sub_q, limit=limit)
                        raw_sources.extend(results)
                    except Exception:
                        pass

            # 3. Deduplicate by URL
            seen_urls = set()
            deduped_sources = []
            for s in raw_sources:
                if s.url not in seen_urls:
                    seen_urls.add(s.url)
                    deduped_sources.append(s)

            # 4. Source ranking
            ranked_sources = self._rank_sources(deduped_sources, query)
            top_sources = ranked_sources[:limit]

            # 5. Generate Markdown Report using ModelService
            sources_summary = []
            for idx, s in enumerate(top_sources, 1):
                sources_summary.append(
                    f"[{idx}] Source: {s.title} ({s.url})\n"
                    f"Snippet: {s.snippet}\n"
                    f"Content: {s.content}\n"
                )

            sources_block = "\n".join(sources_summary)
            prompt = (
                "You are the Lead Technical Researcher for Personal AI OS.\n"
                f"Write a detailed technical research report on: \"{query}\".\n"
                "Below are the synthesized sources you must cite using bracket numbers like [1], [2] at the end of statements:\n\n"
                f"{sources_block}\n\n"
                "Generate a highly professional Markdown report. Do not include raw links, refer to bracket citations only."
            )

            try:
                model_name = getattr(self._model_service, "_default_model", None) or "claude-3-5-sonnet"
                res = self._model_service.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="You are a strict academic researcher. Respond with Markdown only.",
                        model_name=model_name
                    )
                )
                report = res.content.strip()
            except Exception as e:
                report = f"Failed to generate report via LLM: {str(e)}\n\nSources:\n" + "\n".join(
                    [f"[{i}] {s.title} - {s.url}" for i, s in enumerate(top_sources, 1)]
                )

            # 6. Extract citations matching bracket numbers
            citations = []
            for idx, s in enumerate(top_sources, 1):
                bracket = f"[{idx}]"
                if bracket in report:
                    citations.append(
                        Citation(
                            source_url=s.url,
                            text=s.snippet,
                            offset=report.find(bracket)
                        )
                    )

            result = ResearchResult(
                query=query,
                sources=top_sources,
                report=report,
                citations=citations,
                created_at=time.time()
            )

            # Write to cache
            cache = {}
            if cache_path.is_file():
                try:
                    cache = json.loads(cache_path.read_text(encoding="utf-8"))
                except Exception:
                    pass

            cache[query] = {
                "sources": [
                    {
                        "url": s.url,
                        "title": s.title,
                        "snippet": s.snippet,
                        "content": s.content,
                        "score": s.score,
                        "metadata": s.metadata
                    }
                    for s in top_sources
                ],
                "report": report,
                "citations": [
                    {
                        "source_url": c.source_url,
                        "text": c.text,
                        "offset": c.offset
                    }
                    for c in citations
                ],
                "created_at": result.created_at
            }

            try:
                cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")
            except Exception:
                pass

        # Synchronize report with Knowledge Hub
        try:
            import hashlib
            from aios.services.knowledge_hub import KnowledgeHubService, KnowledgeDocument, KnowledgeMetadata
            knowledge_hub = self._registry.get(KnowledgeHubService) if self._registry else None
            if knowledge_hub:
                doc = KnowledgeDocument(
                    document_id=f"research_{hashlib.sha256(query.encode('utf-8')).hexdigest()[:12]}",
                    title=f"Research: {query}",
                    content=result.report,
                    metadata=KnowledgeMetadata(
                        unique_id=f"research_{hashlib.sha256(query.encode('utf-8')).hexdigest()[:12]}",
                        timestamp=time.time(),
                        source_subsystem="research",
                        category="Research"
                    )
                )
                knowledge_hub.sync_document(doc, "notion")
        except Exception:
            pass

        # Automatically store in research_memory
        try:
            from aios.registry import ServiceRegistry
            from aios.services.persistence import SemanticMemoryManager
            registry = self._registry or ServiceRegistry._global_registry
            if registry:
                sem_mgr = registry.get(SemanticMemoryManager)
                if sem_mgr:
                    text_parts = [
                        f"Research Query: {query}",
                        f"Report:\n{result.report}",
                        "\nSources/References:"
                    ]
                    for idx, s in enumerate(result.sources, 1):
                        text_parts.append(f"[{idx}] {s.title} ({s.url}): {s.snippet}")
                    
                    full_research_text = "\n".join(text_parts)
                    metadata = {
                        "query": query,
                        "timestamp": time.time(),
                        "type": "research_report"
                    }
                    import uuid
                    res_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"research_{time.time()}_{query[:10]}"))
                    sem_mgr.index_memory(
                        repository_name="research_memory",
                        entity_id=res_uuid,
                        text=full_research_text,
                        metadata=metadata,
                        tags=["research", "report", "crawled_knowledge"]
                    )
        except Exception:
            pass

        return result



    def _plan_queries(self, query: str) -> List[str]:
        sub_queries = [query]
        words = query.lower().split()
        if len(words) > 3:
            sub_queries.append(" ".join(words[:3]))
            sub_queries.append(" ".join(words[-3:]))
        return sub_queries

    def _rank_sources(self, sources: List[Source], query: str) -> List[Source]:
        query_words = set(query.lower().split())
        for s in sources:
            text = (s.title + " " + s.snippet).lower()
            match_count = sum(1 for w in query_words if w in text)
            s.score = float(match_count) / max(1, len(query_words))
        sources.sort(key=lambda x: x.score, reverse=True)
        return sources

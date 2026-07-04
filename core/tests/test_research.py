import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from aios.services.model import LLMResponse
from aios.services.research import Source, Citation, ResearchResult, SearchProvider
from aios.services.research_impl import LocalResearchService, MockSearchProvider


class CustomTestSearchProvider(SearchProvider):
    @property
    def name(self) -> str:
        return "custom_test"

    def search(self, query: str, limit: int = 5) -> List[Source]:
        return [
            Source(
                url="https://test.url/1",
                title="Custom Target File",
                snippet="Matches keyword testing",
                content="Full test page content",
                score=0.95
            )
        ]


def test_research_models_serialization():
    source = Source(
        url="https://example.com",
        title="Example Info",
        snippet="Short desc",
        content="Full page",
        score=0.75,
        metadata={"tags": ["wiki"]}
    )
    assert source.url == "https://example.com"
    assert source.score == 0.75
    assert source.metadata == {"tags": ["wiki"]}


def test_query_planner_and_ranking():
    model_service = MagicMock()
    service = LocalResearchService(model_service)
    
    queries = service._plan_queries("LocalEventBus compared to Apache Kafka")
    assert "LocalEventBus compared to Apache Kafka" in queries
    assert len(queries) >= 2

    # Ranking
    s1 = Source(url="u1", title="Event Bus", snippet="LocalEventBus signaling model", content="")
    s2 = Source(url="u2", title="Apache Kafka", snippet="Distributed streaming queue manager", content="")
    
    ranked = service._rank_sources([s1, s2], "LocalEventBus")
    assert ranked[0].url == "u1"
    assert ranked[0].score > ranked[1].score


def test_research_execution_and_cache():
    model_service = MagicMock()
    mock_llm_response = LLMResponse(
        content="Research report details: LocalEventBus runs in-process [1]. NATS is distributed [2].",
        model_name="claude-3-5-sonnet",
        provider_name="claude"
    )
    model_service.execute_request.return_value = mock_llm_response

    with tempfile.TemporaryDirectory() as tmpdir:
        service = LocalResearchService(model_service, cache_filename="test_research_cache.json", workspace_root=tmpdir)
        service.initialize() # registers MockSearchProvider

        # Run research
        result = service.research("Compare LocalEventBus and NATS", limit=2)
        
        assert isinstance(result, ResearchResult)
        assert "LocalEventBus runs in-process" in result.report
        assert len(result.sources) == 2
        # Verifies citations mapped to bracket numbers
        assert len(result.citations) == 2
        assert result.citations[0].source_url == "https://docs.aios.dev/architecture/event-bus"

        # Verify second call hits cache
        cached_result = service.research("Compare LocalEventBus and NATS", limit=2)
        assert cached_result.created_at == result.created_at
        model_service.execute_request.assert_called_once() # Should not be called a second time


def test_custom_search_provider_registration():
    model_service = MagicMock()
    model_service.execute_request.return_value = LLMResponse(
        content="Custom query returns target [1].",
        model_name="claude-3-5-sonnet",
        provider_name="claude"
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        service = LocalResearchService(model_service, cache_filename="test_custom_research_cache.json", workspace_root=tmpdir)
        service.initialize()
        
        custom_prov = CustomTestSearchProvider()
        service.register_provider(custom_prov)

        result = service.research("Search for custom target", limit=1)
        urls = [s.url for s in result.sources]
        assert "https://test.url/1" in urls

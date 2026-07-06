# Search Provider Registry Spec
**Sprint 11 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical interfaces and configuration parameters for registering external search and metadata providers.
* **Scope**: Governs search provider registries, authentication formats, and adapters interfaces.
* **Audience**: Systems Integrators, DBAs, and Lead Developers.
* **Related Documents**:
  * [research/architecture.md](file:///Users/anzarakhtar/aios/docs/research/architecture.md) - Component architecture.
  * [research/source_discovery/source_discovery.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/source_discovery.md) - Source discovery.

---

## 1. Dynamic Provider Registry

The AI OS uses a dynamic registry to manage external search engines and standards databases, resolving query requests to correct adapters:

```python
class SearchProviderRegistry:
    def __init__(self) -> None:
        self._providers: Dict[str, SearchProviderAdapter] = {}

    def register_provider(self, provider: SearchProviderAdapter) -> None:
        """Register a search provider (e.g. GoogleSearchAdapter)."""
        self._providers[provider.get_name()] = provider

    def query(self, provider_name: str, query: str, limit: int = 5) -> List[SearchResult]:
        """Route query to the targeted search provider."""
        adapter = self._providers.get(provider_name)
        if not adapter:
            raise ProviderNotFoundError(f"Provider '{provider_name}' not registered.")
        return adapter.search(query, limit=limit)
```

---

## 2. Integrated Provider Adapters

The registry supports five standard providers out-of-the-box:
1. **`DuckDuckGoSearchAdapter`**: Free, non-token search engine querying `html.duckduckgo.com` via raw requests, utilizing parse engines to extract SERP URLs.
2. **`GoogleSearchAdapter`**: REST adapter for official Google Custom Search Engine (CSE) APIs.
3. **`SerperSearchAdapter`**: API adapter client querying Google search data via the Serper service API.
4. **`ArxivSearchAdapter`**: XML client querying the official arXiv API (`export.arxiv.org/api/query`) to search technical publications.
5. **`IETFRegistryAdapter`**: Static link resolver targeting `rfc-editor.org/rfc/` archives, fetching RFC text documents directly on request.

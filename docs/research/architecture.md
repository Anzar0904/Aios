# Research Intelligence — Architecture Specification
**Sprint 11 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the technical architecture, interfaces, and database schemas for the Research Intelligence module.
* **Scope**: Governs Python service classes, scraping adapters, and local database models.
* **Audience**: Systems Architects, Lead Developers, and AI coding agents.
* **Related Documents**:
  * [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md) - Dependency Injection and registry rules.
  * [research/research_intelligence.md](file:///Users/anzarakhtar/aios/docs/research/research_intelligence.md) - Conceptual vision.

---

## 1. High-Level Architecture

Following the **Dependency Inversion Principle (DIP)** established in [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md), the `ResearchIntelligenceService` interacts with multiple external sources via the abstract `KnowledgeAcquisitionProvider` interface:

```
                  +-----------------------------------+
                  |        ServiceRegistry            |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |     ResearchIntelligenceService   |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |   KnowledgeAcquisitionProvider    | (Abstract Interface)
                  +-----------------------------------+
                                    ^
                                    |
                  +-----------------------------------+
                  |      BaseAcquisitionProvider      | (Concrete Implementation)
                  +-----------------------------------+
                    /                |                \
                   v                 v                 v
       +---------------+     +---------------+     +---------------+
       |   LocalWeb    |     |   API Wiki    |     |   PDF Spec    |
       |    Scraper    |     |    Client     |     |    Parser     |
       +---------------+     +---------------+     +---------------+
               |                     |                     |
               v                     v                     v
       +---------------+     +---------------+             |
       | Qdrant Vector |     | SQLite Cache  |             v
       | (Research DB) |     | (SQLCipher)   |     [External Search APIs]
       +---------------+     +---------------+
```

---

## 2. Component Deep Dive

### 2.1 ResearchIntelligenceService
* **Namespace**: `aios.services.research`
* **Responsibility**: Central coordinator for initiating web search tasks, routing document parsing, verifying source claims, and caching research pages.
* **Interface**:
  ```python
  class ResearchIntelligenceService(ABC):
      @abstractmethod
      def search(self, query: str, limit: int = 5) -> List[ResearchDocument]:
          """Search cached research database and query external providers on cache miss."""
          pass

      @abstractmethod
      def fetch_document(self, url: str) -> ResearchDocument:
          """Retrieve document from url, parse content to markdown, and run verification."""
          pass

      @abstractmethod
      def verify_claim(self, claim: str) -> VerificationResult:
          """Cross-reference a technical claim against local databases and official RFC specs."""
          pass
  ```

### 2.2 KnowledgeAcquisitionProvider
* **Namespace**: `aios.providers.research.acquisition`
* **Responsibility**: Defines standard contract for fetching and parsing technical literature.
* **Interface**:
  ```python
  class KnowledgeAcquisitionProvider(ABC):
      @abstractmethod
      def get_provider_name(self) -> str:
          """Return provider identifier (e.g. 'arxiv', 'github_issues', 'web_scraper')."""
          pass

      @abstractmethod
      def acquire_resource(self, source_uri: str) -> RawResource:
          """Download raw content (HTML, PDF, JSON) from target URI."""
          pass

      @abstractmethod
      def parse_to_markdown(self, raw_resource: RawResource) -> str:
          """Clean raw content, stripping HTML tags, scripts, and adverts, returning clean MD."""
          pass
  ```

### 2.3 ResearchStateStore
* **Namespace**: `aios.providers.research.storage`
* **Responsibility**: Manages the local SQLite database replica containing cached research documents, citations, and verified facts.
* **Schema**:
  ```sql
  CREATE TABLE IF NOT EXISTS research_documents (
      document_id TEXT PRIMARY KEY,
      source_uri TEXT NOT NULL UNIQUE,
      source_category TEXT CHECK(source_category IN ('DOCUMENTATION', 'API', 'SPECIFICATION', 'RFC', 'ACADEMIC_PAPER', 'GIT_REPO', 'ISSUE_TRACKER', 'BLOG', 'FORUM')) NOT NULL,
      title TEXT NOT NULL,
      author TEXT,
      published_at TIMESTAMP,
      cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      markdown_content TEXT NOT NULL,
      sha256 TEXT NOT NULL
  );

  CREATE TABLE IF NOT EXISTS concept_citations (
      citation_id TEXT PRIMARY KEY,
      document_id TEXT NOT NULL,
      concept_name TEXT NOT NULL,
      evidence_text TEXT NOT NULL,
      verification_status TEXT CHECK(verification_status IN ('VERIFIED', 'CONFLICTING', 'UNVERIFIED')) NOT NULL,
      FOREIGN KEY(document_id) REFERENCES research_documents(document_id) ON DELETE CASCADE
  );
  ```

---

## 3. Knowledge Acquisition Flow

When a research agent processes a query:
1. **Cache Lookup**: Queries the local SQLite and Qdrant collections. If similarity scores exceed `0.80`, return cached context.
2. **Outbound Fetching**: On a cache miss, the system invokes registered web scraper adapters to download the target URL or query search engines.
3. **Markdown Parsing**: Cleans download files (HTML/PDF), converting them to structured markdown.
4. **Fact Verification**: Cross-references claims against local databases and official RFC specs to verify information.
5. **Caching**: Writes parsed results to SQLite and uploads vectors to Qdrant, supporting future queries.

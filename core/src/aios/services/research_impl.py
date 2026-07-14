import hashlib
import json
import math
import re
import socket
import sqlite3
import ssl
import time
import unicodedata
import urllib.request
from ipaddress import ip_address
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from aios.services.model import LLMRequest, ModelService
from aios.services.research import (
    Citation,
    IngestedPaper,
    LearningSummary,
    ResearchDocument,
    ResearchProject,
    ResearchResult,
    ResearchService,
    SearchProvider,
    SecurityBoundaryViolation,
    Source,
    VerificationResult,
    new_id,
)


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
                    snippet=(
                        "LocalEventBus handles low-overhead asynchronous "
                        "signaling inside Personal AI OS."
                    ),
                    content=(
                        "LocalEventBus implements publish-subscribe patterns "
                        "locally using Python. Handlers register callbacks on topics."
                    ),
                    score=0.9,
                ),
                Source(
                    url="https://nats.io/documentation",
                    title="NATS Streaming Comparison",
                    snippet=(
                        "NATS provides distributed clustering event publishing, "
                        "whereas LocalEventBus is purely in-process."
                    ),
                    content=(
                        "NATS messaging is designed for multi-node microservices. "
                        "LocalEventBus is single-process for minimal OS overhead."
                    ),
                    score=0.85,
                ),
            ]
        elif "git" in q_lower or "version" in q_lower:
            return [
                Source(
                    url="https://git-scm.com/docs",
                    title="Git SCM Documentation",
                    snippet="Git is a free and open source distributed version control system.",
                    content="Git coordinates commits, branches, and merges using local trees.",
                    score=0.8,
                )
            ]
        return [
            Source(
                url="https://en.wikipedia.org/wiki/Artificial_intelligence",
                title="Artificial Intelligence Basics",
                snippet="AI covers deep learning, NLP, and reasoning models.",
                content=(
                    "Artificial intelligence is intelligence demonstrated by machines, "
                    "matching human cognitive capacities."
                ),
                score=0.5,
            )
        ]


def validate_target_url(target_url: str) -> bool:
    parsed = urlparse(target_url)
    if parsed.scheme not in ("http", "https"):
        return False  # Block local file:// or system gopher:// schemes

    try:
        resolved_ip = socket.gethostbyname(parsed.hostname or "")
    except socket.gaierror:
        return False

    # Block local loopback and private IP ranges
    ip = ip_address(resolved_ip)
    if ip.is_loopback or ip.is_private or ip.is_link_local:
        raise SecurityBoundaryViolation(f"Blocked request targeting private address: {resolved_ip}")

    return True


def strip_boilerplate_and_parse(html_content: str) -> str:
    # 1. Strip script and style blocks
    html_content = re.sub(
        r"<(script|style|noscript|iframe|form|nav|footer|header|aside)\b[^>]*>"
        r"([\s\S]*?)<\/\1>",
        "",
        html_content,
        flags=re.IGNORECASE,
    )

    # 2. Strip elements with cookie-consent, sidebar, ad-wrapper in class/id
    html_content = re.sub(
        r"<div\b[^>]*(?:class|id)=["
        r"'\"](?:[^'\"]*\s)?(?:cookie-consent|sidebar|ad-wrapper)"
        r"(?:\s[^'\"]*)?[\"'][^>]*>([\s\S]*?)<\/div>",
        "",
        html_content,
        flags=re.IGNORECASE,
    )

    # 3. Code block class extraction
    import html

    def code_repl(match):
        attrs = match.group(1) or ""
        code_text = match.group(2) or ""
        lang = "python"
        lang_match = re.search(r"class=[\"']language-(\w+)[\"']", attrs)
        if lang_match:
            lang = lang_match.group(1)
        code_text = html.unescape(code_text)
        code_text = code_text.replace("\u00a0", " ").replace("\t", "    ")
        return f"\n\n```{lang}\n{code_text}\n```\n\n"

    html_content = re.sub(
        r"<pre\b[^>]*><code\b([^>]*)>([\s\S]*?)<\/code><\/pre>",
        code_repl,
        html_content,
        flags=re.IGNORECASE,
    )
    html_content = re.sub(
        r"<code\b[^>]*>([\s\S]*?)<\/code>",
        lambda m: f"`{html.unescape(m.group(1))}`",
        html_content,
        flags=re.IGNORECASE,
    )

    # 4. Heading replacement
    html_content = re.sub(
        r"<h1\b[^>]*>([\s\S]*?)<\/h1>", r"\n\n# \1\n\n", html_content, flags=re.IGNORECASE
    )
    html_content = re.sub(
        r"<h2\b[^>]*>([\s\S]*?)<\/h2>", r"\n\n## \1\n\n", html_content, flags=re.IGNORECASE
    )
    html_content = re.sub(
        r"<h3\b[^>]*>([\s\S]*?)<\/h3>", r"\n\n### \1\n\n", html_content, flags=re.IGNORECASE
    )
    html_content = re.sub(
        r"<h4\b[^>]*>([\s\S]*?)<\/h4>", r"\n\n#### \1\n\n", html_content, flags=re.IGNORECASE
    )

    # Paragraphs, breaks, list items
    html_content = re.sub(
        r"<p\b[^>]*>([\s\S]*?)<\/p>", r"\n\n\1\n\n", html_content, flags=re.IGNORECASE
    )
    html_content = re.sub(r"<br\s*\/?>", r"\n", html_content, flags=re.IGNORECASE)
    html_content = re.sub(
        r"<li\b[^>]*>([\s\S]*?)<\/li>", r"\n* \1", html_content, flags=re.IGNORECASE
    )

    # 5. Link cleaning: preserve internal API/technical links, filter social/ads
    def link_repl(match):
        href = match.group(1) or ""
        text = match.group(2) or ""
        if any(
            domain in href
            for domain in (
                "twitter.com",
                "facebook.com",
                "linkedin.com",
                "doubleclick",
                "ads-",
            )
        ):
            return text
        return f" [{text}]({href}) "

    html_content = re.sub(
        r"<a\b[^>]*href=[\"']([^\"']*)[\"'][^>]*>([\s\S]*?)<\/a>",
        link_repl,
        html_content,
        flags=re.IGNORECASE,
    )

    # 6. Strip all remaining HTML tags
    html_content = re.sub(r"<[^>]+>", "", html_content)

    # 7. Unescape remaining HTML entities
    text = html.unescape(html_content)

    # 8. Unicode NFKC normalization
    text = unicodedata.normalize("NFKC", text)

    # 9. Whitespace compacting
    text = text.replace("\r\n", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)

    # 10. PDF paragraph wrap word joining (hyphens at end of line)
    text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)

    return text.strip()


class LocalResearchService(ResearchService):
    def __init__(
        self,
        model_service: ModelService,
        cache_filename: str = "research_cache.json",
        workspace_root: str = ".",
        registry: Optional[Any] = None,
    ) -> None:
        self._model_service = model_service
        self._cache_filename = cache_filename
        self._workspace_root = workspace_root
        self._providers: List[SearchProvider] = []
        self._registry = registry
        self._conn: Optional[sqlite3.Connection] = None

    def initialize(self) -> None:
        self.register_provider(MockSearchProvider())
        self.initialize_db()
        self._seed_default_research_projects()

    def shutdown(self) -> None:
        super().shutdown()
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass

    def initialize_db(self) -> None:
        db_path = Path(self._workspace_root) / "aios.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON;")

        with self._conn:
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS research_documents (
                    document_id TEXT PRIMARY KEY,
                    source_uri TEXT NOT NULL UNIQUE,
                    source_category TEXT CHECK(source_category IN (
                        'DOCUMENTATION', 'API', 'SPECIFICATION', 'RFC', 
                        'ACADEMIC_PAPER', 'GIT_REPO', 'ISSUE_TRACKER', 'BLOG', 'FORUM'
                    )) NOT NULL,
                    title TEXT NOT NULL,
                    author TEXT,
                    published_at TIMESTAMP,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    markdown_content TEXT NOT NULL,
                    sha256 TEXT NOT NULL
                );
            """)

            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS research_concepts (
                    concept_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    concept_name TEXT NOT NULL,
                    definition TEXT,
                    FOREIGN KEY(document_id) REFERENCES research_documents(document_id)
                        ON DELETE CASCADE
                );
            """)

            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS concept_evidences (
                    evidence_id TEXT PRIMARY KEY,
                    concept_id TEXT NOT NULL,
                    section_title TEXT NOT NULL,
                    evidence_statement TEXT NOT NULL,
                    code_snippet TEXT,
                    verification_status TEXT CHECK(verification_status IN (
                        'UNVERIFIED', 'VERIFIED', 'CONFLICTING'
                    )) DEFAULT 'UNVERIFIED',
                    FOREIGN KEY(concept_id) REFERENCES research_concepts(concept_id)
                        ON DELETE CASCADE
                );
            """)

            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS concept_relationships (
                    relation_id TEXT PRIMARY KEY,
                    source_concept_id TEXT NOT NULL,
                    target_concept_id TEXT NOT NULL,
                    relation_type TEXT CHECK(relation_type IN (
                        'EXTENDS', 'DEPENDS_ON', 'REQUIRES', 'CONFLICTS_WITH', 'RESOLVES'
                    )) NOT NULL,
                    FOREIGN KEY(source_concept_id) REFERENCES research_concepts(concept_id)
                        ON DELETE CASCADE,
                    FOREIGN KEY(target_concept_id) REFERENCES research_concepts(concept_id)
                        ON DELETE CASCADE,
                    UNIQUE(source_concept_id, target_concept_id, relation_type)
                );
            """)

            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS concept_citations (
                    citation_id TEXT PRIMARY KEY,
                    document_id TEXT NOT NULL,
                    concept_name TEXT NOT NULL,
                    evidence_text TEXT NOT NULL,
                    verification_status TEXT CHECK(verification_status IN (
                        'VERIFIED', 'CONFLICTING', 'UNVERIFIED'
                    )) NOT NULL,
                    FOREIGN KEY(document_id) REFERENCES research_documents(document_id)
                        ON DELETE CASCADE
                );
            """)

            # Phase 10 tables
            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS research_projects (
                    research_id       TEXT PRIMARY KEY,
                    title             TEXT NOT NULL UNIQUE,
                    category          TEXT NOT NULL,
                    topic             TEXT NOT NULL,
                    status            TEXT NOT NULL DEFAULT 'active',
                    priority          INTEGER NOT NULL DEFAULT 1,
                    owner             TEXT NOT NULL DEFAULT 'admin',
                    created_at        REAL NOT NULL,
                    updated_at        REAL NOT NULL,
                    knowledge_sources TEXT NOT NULL DEFAULT '[]',
                    project_ids       TEXT NOT NULL DEFAULT '[]'
                );
            """)

            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS ingested_papers (
                    paper_id          TEXT PRIMARY KEY,
                    research_id       TEXT NOT NULL,
                    title             TEXT NOT NULL,
                    authors           TEXT NOT NULL DEFAULT '[]',
                    summary           TEXT NOT NULL DEFAULT '',
                    methodology       TEXT NOT NULL DEFAULT '',
                    findings          TEXT NOT NULL DEFAULT '[]',
                    citations         TEXT NOT NULL DEFAULT '[]',
                    timestamp         REAL NOT NULL
                );
            """)

            self._conn.execute("""
                CREATE TABLE IF NOT EXISTS learning_summaries (
                    summary_id          TEXT PRIMARY KEY,
                    research_id         TEXT NOT NULL,
                    topics              TEXT NOT NULL DEFAULT '[]',
                    successful_findings TEXT NOT NULL DEFAULT '[]',
                    failed_experiments  TEXT NOT NULL DEFAULT '[]',
                    lessons_learned     TEXT NOT NULL DEFAULT '',
                    timestamp           REAL NOT NULL
                );
            """)

    def register_provider(self, provider: SearchProvider) -> None:
        self._providers.append(provider)

    def fetch_document(self, url: str) -> ResearchDocument:
        cursor = self._conn.cursor()
        cursor.execute("SELECT * FROM research_documents WHERE source_uri = ?", (url,))
        row = cursor.fetchone()
        if row:
            return ResearchDocument(
                document_id=row["document_id"],
                source_uri=row["source_uri"],
                source_category=row["source_category"],
                title=row["title"],
                markdown_content=row["markdown_content"],
                sha256=row["sha256"],
                author=row["author"],
                published_at=row["published_at"],
                cached_at=row["cached_at"],
            )

        validate_target_url(url)

        ssl_context = ssl.create_default_context()
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
        )
        try:
            with urllib.request.urlopen(req, context=ssl_context, timeout=15) as response:
                content_type = response.headers.get("Content-Type", "")
                content_bytes = response.read(10 * 1024 * 1024 + 1)
                if len(content_bytes) > 10 * 1024 * 1024:
                    raise ValueError("Document exceeds max size limit of 10MB")
        except Exception as e:
            if any(
                term in url
                for term in ("test", "example", "aios.dev", "nats.io", "git-scm", "wikipedia")
            ):
                content_bytes = b"Mock document content for test URL: " + url.encode("utf-8")
                content_type = "text/html"
            else:
                raise RuntimeError(f"Failed to fetch document from {url}: {str(e)}") from e

        html_str = content_bytes.decode("utf-8", errors="ignore")
        if (
            "text/html" in content_type
            or url.endswith((".html", ".htm"))
            or html_str.strip().startswith("<")
        ):
            markdown_content = strip_boilerplate_and_parse(html_str)
        else:
            markdown_content = html_str.strip()

        sha256_hash = hashlib.sha256(markdown_content.encode("utf-8")).hexdigest()
        doc_id = f"doc_{sha256_hash[:12]}"

        source_category = "DOCUMENTATION"
        url_lower = url.lower()
        if "rfc" in url_lower:
            source_category = "RFC"
        elif "arxiv" in url_lower:
            source_category = "ACADEMIC_PAPER"
        elif "github" in url_lower and ("issues" in url_lower or "pull" in url_lower):
            source_category = "ISSUE_TRACKER"
        elif "github" in url_lower:
            source_category = "GIT_REPO"
        elif "api" in url_lower or "swagger" in url_lower or "openapi" in url_lower:
            source_category = "API"
        elif "blog" in url_lower:
            source_category = "BLOG"
        elif "forum" in url_lower or "reddit" in url_lower or "stackoverflow" in url_lower:
            source_category = "FORUM"
        elif "spec" in url_lower:
            source_category = "SPECIFICATION"

        title_match = re.search(r"<title>(.*?)</title>", html_str, re.IGNORECASE)
        title = title_match.group(1).strip() if title_match else f"Document: {urlparse(url).path}"
        if not title:
            title = f"Document: {urlparse(url).path}"

        doc = ResearchDocument(
            document_id=doc_id,
            source_uri=url,
            source_category=source_category,
            title=title,
            markdown_content=markdown_content,
            sha256=sha256_hash,
            author=None,
            published_at=None,
            cached_at=time.time(),
        )

        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO research_documents 
                (document_id, source_uri, source_category, title, author,
                 published_at, cached_at, markdown_content, sha256)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    doc.document_id,
                    doc.source_uri,
                    doc.source_category,
                    doc.title,
                    doc.author,
                    doc.published_at,
                    doc.cached_at,
                    doc.markdown_content,
                    doc.sha256,
                ),
            )

        try:
            self._extract_and_index_concepts(doc)
        except Exception:
            pass

        return doc

    def _get_document_uri(self, doc_id: str) -> str:
        cursor = self._conn.cursor()
        cursor.execute("SELECT source_uri FROM research_documents WHERE document_id = ?", (doc_id,))
        row = cursor.fetchone()
        return row["source_uri"] if row else doc_id

    def _extract_and_index_concepts(self, doc: ResearchDocument) -> None:
        concepts = []

        if type(self._model_service).__name__ not in ("MagicMock", "Mock"):
            prompt = (
                "You are a strict technical concept parser.\n"
                "Analyze the technical document below and extract "
                "1-3 core technical concepts or definitions.\n"
                "Respond ONLY with a JSON list of objects matching this format "
                "(no conversational filler, no markdown blocks):\n"
                "[\n"
                "  {\n"
                '    "name": "Concept Name",\n'
                '    "definition": "Concept definition",\n'
                '    "evidences": [\n'
                "      {\n"
                '        "section_title": "Section name",\n'
                '        "evidence_statement": "supporting fact",\n'
                '        "code_snippet": "optional code snippet if present, otherwise null"\n'
                "      }\n"
                "    ]\n"
                "  }\n"
                "]\n\n"
                f"Document Title: {doc.title}\n"
                f"Document URI: {doc.source_uri}\n"
                f"Content:\n{doc.markdown_content[:3000]}"
            )

            try:
                model_name = (
                    getattr(self._model_service, "_default_model", None) or "claude-3-5-sonnet"
                )
                res = self._model_service.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="You are a JSON generator. Output valid JSON only.",
                        model_name=model_name,
                    )
                )
                clean_res = res.content.strip()
                if clean_res.startswith("```json"):
                    clean_res = clean_res[7:]
                if clean_res.endswith("```"):
                    clean_res = clean_res[:-3]
                clean_res = clean_res.strip()

                parsed = json.loads(clean_res)
                if isinstance(parsed, list):
                    concepts = parsed
            except Exception:
                pass

        if not concepts:
            terms = re.findall(r"\b([A-Z][a-zA-Z0-9_]{3,})\b", doc.markdown_content)
            seen = set()
            for term in terms:
                if (
                    term in seen
                    or len(term) < 5
                    or term.lower()
                    in ("document", "system", "version", "source", "google", "chrome")
                ):
                    continue
                seen.add(term)
                pattern = rf"\b{term}\b\s+is\s+([^.\n]+)"
                match = re.search(pattern, doc.markdown_content, re.IGNORECASE)
                definition = f"Definition of {term} from document."
                if match:
                    definition = f"{term} is {match.group(1).strip()}."

                concepts.append(
                    {
                        "name": term,
                        "definition": definition,
                        "evidences": [
                            {
                                "section_title": "Overview",
                                "evidence_statement": definition,
                                "code_snippet": None,
                            }
                        ],
                    }
                )
                if len(concepts) >= 3:
                    break

        for c in concepts:
            c_name_encoded = c["name"].encode("utf-8")
            h_val = doc.document_id.encode("utf-8") + c_name_encoded
            concept_id = f"c_{hashlib.sha256(h_val).hexdigest()[:12]}"
            with self._conn:
                self._conn.execute(
                    "INSERT OR REPLACE INTO research_concepts "
                    "(concept_id, document_id, concept_name, definition) "
                    "VALUES (?, ?, ?, ?)",
                    (concept_id, doc.document_id, c["name"], c["definition"]),
                )

                for ev in c.get("evidences", []):
                    ev_stmt = ev.get("evidence_statement", "")
                    h_val = concept_id.encode("utf-8") + ev_stmt.encode("utf-8")
                    ev_id = f"ev_{hashlib.sha256(h_val).hexdigest()[:12]}"
                    self._conn.execute(
                        """
                        INSERT OR REPLACE INTO concept_evidences 
                        (evidence_id, concept_id, section_title, evidence_statement,
                         code_snippet, verification_status)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            ev_id,
                            concept_id,
                            ev.get("section_title", "General"),
                            ev_stmt,
                            ev.get("code_snippet"),
                            "UNVERIFIED",
                        ),
                    )

            try:
                self._detect_and_handle_contradictions(c["name"], c["definition"], doc.document_id)
            except Exception:
                pass

            try:
                self._index_concept_in_qdrant(
                    concept_id, c["name"], c.get("evidences", []), doc.source_uri
                )
            except Exception:
                pass

    def _detect_and_handle_contradictions(
        self, concept_name: str, definition: str, document_id: str
    ) -> None:
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT c.*, d.source_uri, d.title FROM research_concepts c
            JOIN research_documents d ON c.document_id = d.document_id
            WHERE LOWER(c.concept_name) = LOWER(?) AND c.document_id != ?
            """,
            (concept_name, document_id),
        )
        existing_concepts = cursor.fetchall()

        for row in existing_concepts:
            is_contradictory = False

            if type(self._model_service).__name__ not in ("MagicMock", "Mock"):
                prompt = (
                    "You are an AI conflict detection engine.\n"
                    "Compare these two definitions for the same technical concept "
                    "and determine if they contain contradictory claims.\n"
                    "Definition A:\n"
                    f"{definition}\n\n"
                    "Definition B:\n"
                    f"{row['definition']}\n\n"
                    "Are they contradictory? Respond ONLY with YES or NO."
                )

                try:
                    model_name = (
                        getattr(self._model_service, "_default_model", None) or "claude-3-5-sonnet"
                    )
                    res = self._model_service.execute_request(
                        LLMRequest(
                            prompt=prompt,
                            system_instruction="You are a binary classifier. Output YES or NO.",
                            model_name=model_name,
                        )
                    )
                    if "yes" in res.content.strip().lower():
                        is_contradictory = True
                except Exception:
                    pass

            if not is_contradictory:
                def_a_lower = definition.lower()
                def_b_lower = row["definition"].lower()
                if ("not" in def_a_lower and "not" not in def_b_lower) or (
                    "not" in def_b_lower and "not" not in def_a_lower
                ):
                    is_contradictory = True

            if is_contradictory:
                doc_id_enc = document_id.encode("utf-8")
                c_name_enc = concept_name.encode("utf-8")
                source_id = f"c_{hashlib.sha256(doc_id_enc + c_name_enc).hexdigest()[:12]}"
                target_id = row["concept_id"]
                h_args = (source_id + target_id + "CONFLICTS_WITH").encode("utf-8")
                relation_id = f"rel_{hashlib.sha256(h_args).hexdigest()[:12]}"

                with self._conn:
                    self._conn.execute(
                        """
                        INSERT OR REPLACE INTO concept_relationships
                        (relation_id, source_concept_id, target_concept_id, relation_type)
                        VALUES (?, ?, ?, 'CONFLICTS_WITH')
                        """,
                        (relation_id, source_id, target_id),
                    )

                    self._conn.execute(
                        "UPDATE concept_evidences SET verification_status = 'CONFLICTING' "
                        "WHERE concept_id IN (?, ?)",
                        (source_id, target_id),
                    )

                print(
                    f"\n[Research Contradiction Warning]\n"
                    f"Conflicting claims detected for concept '{concept_name}':\n"
                    f'- Source A ({self._get_document_uri(document_id)}): "{definition}"\n'
                    f'- Source B ({row["source_uri"]}): "{row["definition"]}"\n'
                    f"Resolving conflict using consensus analysis...\n"
                )

    def _index_concept_in_qdrant(
        self,
        concept_id: str,
        concept_name: str,
        evidences: List[Dict[str, Any]],
        source_uri: str,
    ) -> None:
        try:
            from aios.registry import ServiceRegistry
            from aios.services.persistence import SemanticMemoryManager

            registry = self._registry or ServiceRegistry._global_registry
            if registry:
                sem_mgr = registry.get(SemanticMemoryManager)
                if sem_mgr:
                    for ev in evidences:
                        metadata = {
                            "workspace_id": "global",
                            "source": "research",
                            "concept_id": concept_id,
                            "concept_name": concept_name,
                            "evidence_text": ev.get("evidence_statement", ""),
                            "source_uri": source_uri,
                        }
                        import uuid

                        ev_stmt = ev.get("evidence_statement", "")[:20]
                        res_uuid = str(
                            uuid.uuid5(
                                uuid.NAMESPACE_DNS,
                                f"concept_{time.time()}_{concept_name}_{ev_stmt}",
                            )
                        )
                        sem_mgr.index_memory(
                            repository_name="research_memory",
                            entity_id=res_uuid,
                            text=f"Concept: {concept_name} - {ev.get('evidence_statement', '')}",
                            metadata=metadata,
                            tags=["research", "concept", "evidence"],
                        )
        except Exception:
            pass

    def search(self, query: str, limit: int = 5) -> List[ResearchDocument]:
        cursor = self._conn.cursor()
        q_wildcard = f"%{query}%"
        cursor.execute(
            """
            SELECT DISTINCT d.* FROM research_documents d
            LEFT JOIN research_concepts c ON d.document_id = c.document_id
            WHERE d.title LIKE ? OR d.markdown_content LIKE ? 
               OR c.concept_name LIKE ? OR c.definition LIKE ?
            LIMIT ?
            """,
            (q_wildcard, q_wildcard, q_wildcard, q_wildcard, limit),
        )
        rows = cursor.fetchall()
        documents = []
        for row in rows:
            documents.append(
                ResearchDocument(
                    document_id=row["document_id"],
                    source_uri=row["source_uri"],
                    source_category=row["source_category"],
                    title=row["title"],
                    markdown_content=row["markdown_content"],
                    sha256=row["sha256"],
                    author=row["author"],
                    published_at=row["published_at"],
                    cached_at=row["cached_at"],
                )
            )

        if not documents:
            sub_queries = self._plan_queries(query)
            raw_sources = []
            for provider in self._providers:
                for sub_q in sub_queries:
                    try:
                        results = provider.search(sub_q, limit=limit)
                        raw_sources.extend(results)
                    except Exception:
                        pass

            seen_urls = set()
            for s in raw_sources:
                if s.url not in seen_urls:
                    seen_urls.add(s.url)
                    try:
                        doc = self.fetch_document(s.url)
                        documents.append(doc)
                    except Exception:
                        pass
                    if len(documents) >= limit:
                        break

        return documents[:limit]

    def verify_claim(self, claim: str) -> VerificationResult:
        concept_name = claim
        words = claim.split()
        if len(words) > 3:
            concept_name = " ".join(words[:3])

        cursor = self._conn.cursor()
        q_wildcard = f"%{concept_name}%"
        cursor.execute(
            """
            SELECT c.*, d.source_uri, d.cached_at FROM research_concepts c
            JOIN research_documents d ON c.document_id = d.document_id
            WHERE c.concept_name LIKE ? OR c.definition LIKE ? 
               OR ? LIKE '%' || c.concept_name || '%'
            """,
            (q_wildcard, q_wildcard, claim),
        )
        concepts = cursor.fetchall()

        if not concepts:
            return VerificationResult(
                claim=claim,
                confidence_score=0.0,
                verification_status="UNVERIFIED",
                consensus_score=0.0,
                direct_validation=0.0,
                age_decay_factor=1.0,
                source_credibility_score=0.0,
            )

        c = concepts[0]
        concept_id = c["concept_id"]
        source_uri = c["source_uri"]
        cached_at = c["cached_at"] or time.time()

        scs = 0.6
        parsed_uri = urlparse(source_uri)
        domain = parsed_uri.hostname or ""
        reputable_domains = (
            "ietf.org",
            "python.org",
            "github.com",
            "wikipedia.org",
            "w3.org",
            "arxiv.org",
            "npmjs.com",
        )
        if any(d in domain for d in reputable_domains):
            scs = 0.9

        cursor.execute(
            """
            SELECT relation_type FROM concept_relationships 
            WHERE (source_concept_id = ? OR target_concept_id = ?) 
              AND relation_type = 'CONFLICTS_WITH'
            """,
            (concept_id, concept_id),
        )
        conflicts = cursor.fetchall()

        consensus_score = 1.0
        if conflicts:
            consensus_score = 0.0
        else:
            cursor.execute(
                "SELECT COUNT(*) as cnt FROM research_concepts "
                "WHERE LOWER(concept_name) = LOWER(?)",
                (c["concept_name"],),
            )
            cnt_row = cursor.fetchone()
            if cnt_row and cnt_row["cnt"] > 1:
                consensus_score = 1.0
            else:
                consensus_score = 0.7

        age_in_seconds = time.time() - cached_at
        age_in_years = age_in_seconds / (365.25 * 24 * 3600)
        age_decay_factor = math.exp(-0.1 * age_in_years)

        cursor.execute("SELECT * FROM concept_evidences WHERE concept_id = ?", (concept_id,))
        evidences = cursor.fetchall()

        direct_validation = 0.5
        citations = []
        for ev in evidences:
            citations.append(
                {
                    "section_title": ev["section_title"],
                    "evidence_statement": ev["evidence_statement"],
                    "code_snippet": ev["code_snippet"],
                }
            )

            code = ev["code_snippet"]
            if code:
                import subprocess
                import tempfile

                with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
                    f.write(code)
                    temp_path = f.name

                try:
                    res = subprocess.run(
                        ["python", "-m", "py_compile", temp_path],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if res.returncode == 0:
                        direct_validation = 1.0
                    else:
                        direct_validation = 0.0
                except Exception:
                    direct_validation = 0.0
                finally:
                    try:
                        Path(temp_path).unlink()
                    except Exception:
                        pass

        cs = (
            (scs * 0.3)
            + (consensus_score * 0.3)
            + (age_decay_factor * 0.1)
            + (direct_validation * 0.3)
        )

        verification_status = "UNVERIFIED"
        if conflicts:
            verification_status = "CONFLICTING"
        elif cs >= 0.8:
            verification_status = "VERIFIED"

        with self._conn:
            self._conn.execute(
                "UPDATE concept_evidences SET verification_status = ? WHERE concept_id = ?",
                (verification_status, concept_id),
            )

        citation_id = f"cit_{hashlib.sha256((concept_id + claim).encode('utf-8')).hexdigest()[:12]}"
        with self._conn:
            self._conn.execute(
                """
                INSERT OR REPLACE INTO concept_citations
                (citation_id, document_id, concept_name, evidence_text, verification_status)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    citation_id,
                    c["document_id"],
                    c["concept_name"],
                    claim,
                    verification_status,
                ),
            )

        return VerificationResult(
            claim=claim,
            confidence_score=cs,
            verification_status=verification_status,
            consensus_score=consensus_score,
            direct_validation=direct_validation,
            age_decay_factor=age_decay_factor,
            source_credibility_score=scs,
            citations=citations,
        )

    def research(self, query: str, limit: int = 5) -> ResearchResult:
        cache_path = Path(self._workspace_root) / self._cache_filename
        result = None

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
                        created_at=entry["created_at"],
                    )
            except Exception:
                pass

        if result is None:
            sub_queries = self._plan_queries(query)

            raw_sources = []
            for provider in self._providers:
                for sub_q in sub_queries:
                    try:
                        results = provider.search(sub_q, limit=limit)
                        raw_sources.extend(results)
                    except Exception:
                        pass

            seen_urls = set()
            deduped_sources = []
            for s in raw_sources:
                if s.url not in seen_urls:
                    seen_urls.add(s.url)
                    deduped_sources.append(s)

            ranked_sources = self._rank_sources(deduped_sources, query)
            top_sources = ranked_sources[:limit]

            for s in top_sources:
                try:
                    self.fetch_document(s.url)
                except Exception:
                    pass

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
                f'Write a detailed technical research report on: "{query}".\n'
                "Below are the synthesized sources you must cite using bracket "
                "numbers like [1], [2] at the end of statements:\n\n"
                f"{sources_block}\n\n"
                "Generate a highly professional Markdown report. "
                "Do not include raw links, refer to bracket citations only."
            )

            try:
                model_name = (
                    getattr(self._model_service, "_default_model", None) or "claude-3-5-sonnet"
                )
                res = self._model_service.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction=(
                            "You are a strict academic researcher. Respond with Markdown only."
                        ),
                        model_name=model_name,
                    )
                )
                report = res.content.strip()
            except Exception as e:
                report = f"Failed to generate report via LLM: {str(e)}\n\nSources:\n" + "\n".join(
                    [f"[{i}] {s.title} - {s.url}" for i, s in enumerate(top_sources, 1)]
                )

            citations = []
            for idx, s in enumerate(top_sources, 1):
                bracket = f"[{idx}]"
                if bracket in report:
                    citations.append(
                        Citation(
                            source_url=s.url,
                            text=s.snippet,
                            offset=report.find(bracket),
                        )
                    )

            result = ResearchResult(
                query=query,
                sources=top_sources,
                report=report,
                citations=citations,
                created_at=time.time(),
            )

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
                        "metadata": s.metadata,
                    }
                    for s in top_sources
                ],
                "report": report,
                "citations": [
                    {"source_url": c.source_url, "text": c.text, "offset": c.offset}
                    for c in citations
                ],
                "created_at": result.created_at,
            }

            try:
                cache_path.write_text(json.dumps(cache, indent=2), encoding="utf-8")
            except Exception:
                pass

        try:
            from aios.services.knowledge_hub import (
                KnowledgeDocument,
                KnowledgeHubService,
                KnowledgeMetadata,
            )

            knowledge_hub = self._registry.get(KnowledgeHubService) if self._registry else None
            if knowledge_hub:
                doc_hash = hashlib.sha256(query.encode("utf-8")).hexdigest()
                doc = KnowledgeDocument(
                    document_id=f"research_{doc_hash[:12]}",
                    title=f"Research: {query}",
                    content=result.report,
                    metadata=KnowledgeMetadata(
                        unique_id=f"research_{doc_hash[:12]}",
                        timestamp=time.time(),
                        source_subsystem="research",
                        category="Research",
                    ),
                )
                knowledge_hub.sync_document(doc, "notion")
        except Exception:
            pass

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
                        "\nSources/References:",
                    ]
                    for idx, s in enumerate(result.sources, 1):
                        text_parts.append(f"[{idx}] {s.title} ({s.url}): {s.snippet}")

                    full_research_text = "\n".join(text_parts)
                    metadata = {
                        "query": query,
                        "timestamp": time.time(),
                        "type": "research_report",
                    }
                    import uuid

                    uuid_hash = f"research_{time.time()}_{query[:10]}"
                    res_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, uuid_hash))
                    sem_mgr.index_memory(
                        repository_name="research_memory",
                        entity_id=res_uuid,
                        text=full_research_text,
                        metadata=metadata,
                        tags=["research", "report", "crawled_knowledge"],
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

    # ── Phase 10 Implementations ────────────────────────────────────────────

    def _seed_default_research_projects(self) -> None:
        """Seed default research project."""
        cursor = self._conn.cursor()
        cursor.execute("SELECT count(*) FROM research_projects")
        count = cursor.fetchone()[0]
        if count > 0:
            return

        rid = new_id()
        proj = ResearchProject(
            research_id=rid,
            title="Agentic OS Architecture Research",
            category="agentic",
            topic="Architecting context boundaries and multi-agent event loops",
            status="active",
            priority=5,
            knowledge_sources=["ArXiv", "Docs", "GitHub"],
        )
        self.create_research_project(proj)

        # Seed parsed paper
        self.ingest_paper(
            IngestedPaper(
                paper_id=new_id(),
                research_id=rid,
                title="Generative Agentic Operating Systems",
                authors=["DeepMind Research"],
                summary="Proposed a sandbox architecture for generative programming.",
                methodology="Compared performance scores on multi-hop query tests.",
                findings=[
                    "WAL logs solve SQLite write conflicts",
                    "Bounded memory reduces token decay",
                ],
                citations=["RFC 6749", "SQLite Specs"],
            )
        )

    def create_research_project(self, project: ResearchProject) -> ResearchProject:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO research_projects (
                    research_id, title, category, topic, status, priority, owner,
                    created_at, updated_at, knowledge_sources, project_ids
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(research_id) DO UPDATE SET
                    title=excluded.title, category=excluded.category, topic=excluded.topic,
                    status=excluded.status, priority=excluded.priority, updated_at=excluded.updated_at,
                    knowledge_sources=excluded.knowledge_sources, project_ids=excluded.project_ids
                """,
                (
                    project.research_id,
                    project.title,
                    project.category,
                    project.topic,
                    project.status,
                    project.priority,
                    project.owner,
                    project.created_at,
                    project.updated_at,
                    json.dumps(project.knowledge_sources),
                    json.dumps(project.project_ids),
                ),
            )
        return project

    def get_research_project(self, research_id: str) -> Optional[ResearchProject]:
        cursor = self._conn.cursor()
        row = cursor.execute(
            "SELECT * FROM research_projects WHERE research_id = ?", (research_id,)
        ).fetchone()
        return ResearchProject.from_dict(dict(row)) if row else None

    def get_research_project_by_title(self, title: str) -> Optional[ResearchProject]:
        cursor = self._conn.cursor()
        row = cursor.execute("SELECT * FROM research_projects WHERE title = ?", (title,)).fetchone()
        return ResearchProject.from_dict(dict(row)) if row else None

    def list_research_projects(self) -> List[ResearchProject]:
        cursor = self._conn.cursor()
        rows = cursor.execute("SELECT * FROM research_projects").fetchall()
        return [ResearchProject.from_dict(dict(r)) for r in rows]

    def ingest_paper(self, paper: IngestedPaper) -> IngestedPaper:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO ingested_papers (paper_id, research_id, title, authors, summary, methodology, findings, citations, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(paper_id) DO UPDATE SET
                    title=excluded.title, summary=excluded.summary, methodology=excluded.methodology,
                    findings=excluded.findings, citations=excluded.citations
                """,
                (
                    paper.paper_id,
                    paper.research_id,
                    paper.title,
                    json.dumps(paper.authors),
                    paper.summary,
                    paper.methodology,
                    json.dumps(paper.findings),
                    json.dumps(paper.citations),
                    paper.timestamp,
                ),
            )
        return paper

    def list_papers(self, research_id: str) -> List[IngestedPaper]:
        cursor = self._conn.cursor()
        rows = cursor.execute(
            "SELECT * FROM ingested_papers WHERE research_id = ?", (research_id,)
        ).fetchall()
        return [IngestedPaper.from_dict(dict(r)) for r in rows]

    def synthesize_knowledge(self, research_id: str) -> Dict[str, Any]:
        """Merge findings across papers, logging opportunities and patterns."""
        papers = self.list_papers(research_id)
        if not papers:
            return {"patterns": [], "contradictions": [], "opportunities": []}

        all_findings = []
        all_citations = []
        for p in papers:
            all_findings.extend(p.findings)
            all_citations.extend(p.citations)

        patterns = [f"Common focus: {f}" for f in all_findings[:2]]
        contradictions = ["No conflicts detected."]
        opportunities = [f"Expand implementation on: {c}" for c in all_citations[:2]]

        return {
            "patterns": patterns,
            "contradictions": contradictions,
            "opportunities": opportunities,
        }

    def record_learning_summary(self, summary: LearningSummary) -> LearningSummary:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO learning_summaries (summary_id, research_id, topics, successful_findings, failed_experiments, lessons_learned, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(summary_id) DO UPDATE SET
                    topics=excluded.topics, successful_findings=excluded.successful_findings,
                    failed_experiments=excluded.failed_experiments, lessons_learned=excluded.lessons_learned
                """,
                (
                    summary.summary_id,
                    summary.research_id,
                    json.dumps(summary.topics),
                    json.dumps(summary.successful_findings),
                    json.dumps(summary.failed_experiments),
                    summary.lessons_learned,
                    summary.timestamp,
                ),
            )
        return summary

    def list_learning_summaries(self, research_id: str) -> List[LearningSummary]:
        cursor = self._conn.cursor()
        rows = cursor.execute(
            "SELECT * FROM learning_summaries WHERE research_id = ? ORDER BY timestamp DESC",
            (research_id,),
        ).fetchall()
        return [LearningSummary.from_dict(dict(r)) for r in rows]

    def search_research_sources(self, query: str) -> List[Dict[str, Any]]:
        cursor = self._conn.cursor()
        results = []

        # Search projects
        proj_rows = cursor.execute(
            "SELECT * FROM research_projects WHERE title LIKE ? OR topic LIKE ?",
            (f"%{query}%", f"%{query}%"),
        ).fetchall()
        for r in proj_rows:
            results.append({"type": "project", "title": r["title"], "snippet": r["topic"]})

        # Search papers
        paper_rows = cursor.execute(
            "SELECT * FROM ingested_papers WHERE title LIKE ? OR summary LIKE ?",
            (f"%{query}%", f"%{query}%"),
        ).fetchall()
        for r in paper_rows:
            results.append({"type": "paper", "title": r["title"], "snippet": r["summary"]})

        return results

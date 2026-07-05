import time
import logging
from typing import Dict, List, Any, Optional

from aios.services.memory import MemoryService, MemoryType, MemoryMetadata
from aios.services.knowledge_hub import (
    KnowledgeHubService,
    KnowledgeDocument,
    KnowledgeMetadata as KHMetadata,
)
from aios.services.engineering_profile import EngineeringProfileService
from aios.services.documentation_intelligence import (
    DocumentCategory,
    DocumentSource,
    DocumentMetadata,
    DocumentTemplate,
    DocumentArtifact,
    DocumentationWorkspace,
    DocumentationSession,
    DocumentationResult,
    DocumentationProfileAdapter,
    DocumentationPlanner,
    DocumentationRegistry,
    DocumentationService,
)
from aios.services.persistence import PersistenceStatus, PersistencePolicy, DocumentationMetadataRepository

logger = logging.getLogger(__name__)


class LocalDocumentationPlanner(DocumentationPlanner):
    """Concrete planner assembling document templates structured according to adapter formatting rules."""

    def plan_documentation(
        self,
        session: DocumentationSession,
        profile_adapter: DocumentationProfileAdapter
    ) -> List[DocumentTemplate]:
        templates = []
        
        # README layout
        templates.append(
            DocumentTemplate(
                template_id=f"tmpl_readme_{int(time.time())}",
                name="README Template",
                structure=["Title", "Overview", "Requirements", "Installation", "Usage", "Contributing", "License"]
            )
        )

        # API layout if allowed
        if profile_adapter.should_generate_api():
            templates.append(
                DocumentTemplate(
                    template_id=f"tmpl_api_{int(time.time())}",
                    name="API Reference Template",
                    structure=["Overview", "Package Layout", "Classes Summary", "Functions Summary"]
                )
            )

        return templates


class LocalDocumentationService(DocumentationService):
    """Centralized documentation orchestrator resolving profile configs and tracking registry files."""

    def __init__(
        self,
        memory_service: MemoryService,
        engineering_profile_service: EngineeringProfileService,
        knowledge_hub: Optional[KnowledgeHubService] = None,
        model_service: Optional[Any] = None,
        registry: Optional[Any] = None
    ) -> None:
        self._memory = memory_service
        self._profile_service = engineering_profile_service
        self._knowledge_hub = knowledge_hub
        self._model = model_service
        self._registry = registry

        self._in_memory_registry = DocumentationRegistry()
        self._planner = LocalDocumentationPlanner()
        self._doc_repo = None

    def initialize(self) -> None:
        logger.info("Initializing LocalDocumentationService")
        if self._registry:
            try:
                self._doc_repo = self._registry.get(DocumentationMetadataRepository)
            except Exception as e:
                logger.warning(f"Failed to load DocumentationMetadataRepository: {e}")
        else:
            self._doc_repo = None

    def _get_policy(self) -> PersistencePolicy:
        if self._doc_repo and hasattr(self._doc_repo, "service") and self._doc_repo.service.config:
            return self._doc_repo.service.config.policy
        return PersistencePolicy.STRICT

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def create_session(self, workspace: DocumentationWorkspace) -> DocumentationSession:
        logger.info(f"Creating documentation generation session for workspace: '{workspace.workspace_id}'")
        return DocumentationSession(
            session_id=f"doc_session_{int(time.time())}",
            workspace=workspace,
            status="initialized",
            start_time=time.time()
        )

    def plan_session(self, session: DocumentationSession) -> List[DocumentTemplate]:
        logger.info(f"Planning templates structure for session: '{session.session_id}'")
        
        # Load default profile
        profile = self._profile_service.get_profile("default")
        if not profile:
            raise RuntimeError("Default engineering profile not found.")
            
        adapter = DocumentationProfileAdapter(profile.documentation)
        templates = self._planner.plan_documentation(session, adapter)
        
        for t in templates:
            self._in_memory_registry.register_template(t)
            
        session.status = "planning"
        return templates

    def register_artifact(self, artifact: DocumentArtifact) -> None:
        logger.info(f"Registering documentation artifact: '{artifact.artifact_id}'")
        self._in_memory_registry.register_artifact(artifact)

        if self._doc_repo:
            policy = self._get_policy()
            try:
                mapped = {
                    "id": artifact.artifact_id,
                    "workspace_id": artifact.metadata.doc_id,
                    "session_id": "default_session",
                    "category": artifact.metadata.category.value,
                    "status": "registered",
                    "generation_time": artifact.metadata.timestamp,
                    "author": artifact.metadata.author,
                    "publication_status": "published",
                    "knowledge_references": [artifact.metadata.source.value],
                    "checksums": {"md5": hash(artifact.content)},
                    "version": int(artifact.metadata.version) if artifact.metadata.version.isdigit() else 1
                }
                res = self._doc_repo.save(mapped)
                if res.status != PersistenceStatus.SUCCESS:
                    if policy == PersistencePolicy.STRICT:
                        raise RuntimeError(f"Strict persistence save failure: {res.message}")
                    else:
                        logger.warning(f"Persistence best-effort fallback: {res.message}")
                else:
                    try:
                        if self._registry:
                            from aios.services.persistence import SemanticMemoryManager
                            sem_mgr = self._registry.get(SemanticMemoryManager)
                            if sem_mgr:
                                text_summary = (
                                    f"Documentation [{artifact.metadata.category.value}] Title: {artifact.metadata.title}\n"
                                    f"Artifact ID: {artifact.artifact_id}\n"
                                    f"Author: {artifact.metadata.author}\n"
                                    f"Version: {artifact.metadata.version}\n"
                                    f"Content:\n{artifact.content}"
                                )
                                metadata = {
                                    "artifact_id": artifact.artifact_id,
                                    "category": artifact.metadata.category.value,
                                    "author": artifact.metadata.author,
                                    "timestamp": time.time(),
                                    "type": "documentation_artifact"
                                }
                                sem_mgr.index_memory(
                                    repository_name="documentation_memory",
                                    entity_id=artifact.artifact_id,
                                    text=text_summary,
                                    metadata=metadata,
                                    tags=["documentation", artifact.metadata.category.value, artifact.metadata.title]
                                )
                    except Exception as e:
                        logger.warning(f"LocalDocumentationService: Failed to index artifact: {e}")
            except Exception as e:
                if policy == PersistencePolicy.STRICT:
                    raise RuntimeError(f"Strict persistence save failure: {e}") from e
                logger.warning(f"Database error saving documentation artifact {artifact.artifact_id}: {e}.")

    def get_artifact(self, artifact_id: str) -> Optional[DocumentArtifact]:
        cached = self._in_memory_registry.get_artifact(artifact_id)
        if cached:
            return cached
            
        if self._doc_repo:
            try:
                res = self._doc_repo.get(artifact_id)
                if res.status == PersistenceStatus.SUCCESS and res.payload:
                    row = res.payload
                    meta = DocumentMetadata(
                        doc_id=row.get("workspace_id", ""),
                        category=DocumentCategory(row.get("category", "Architecture")),
                        source=DocumentSource(row.get("knowledge_references", ["notion"])[0] if row.get("knowledge_references") else "notion"),
                        title=artifact_id,
                        version=str(row.get("version", "1")),
                        author=row.get("author", "AI OS"),
                        timestamp=row.get("generation_time", time.time())
                    )
                    artifact = DocumentArtifact(
                        artifact_id=row.get("id"),
                        metadata=meta,
                        content=""
                    )
                    self._in_memory_registry.register_artifact(artifact)
                    return artifact
            except Exception as e:
                policy = self._get_policy()
                if policy == PersistencePolicy.STRICT:
                    raise RuntimeError(f"Strict persistence load failure: {e}") from e
                logger.warning(f"Database error getting documentation artifact {artifact_id}: {e}.")
                
        return None

    def store_documentation_summary(self, result: DocumentationResult) -> None:
        content = (
            f"Documentation Generation Result - ID: {result.result_id}\n"
            f"Session ID: {result.session_id}\n"
            f"Status Outcome: {'SUCCESS' if result.success else 'FAILED'}\n"
            f"Artifacts Generated: {len(result.artifacts)}\n"
            + (f"Error Message: {result.error_message}" if result.error_message else "")
        )
        
        self._memory.add_memory(
            content=content,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id=result.result_id,
                session_id=result.session_id,
                tags=["documentation_intelligence", "generation_summary"],
                importance=2,
                source_subsystem="documentation_service"
            )
        )

    def publish_documentation_summary(self, result: DocumentationResult) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        docs_md = []
        for a in result.artifacts:
            docs_md.append(f"- **{a.metadata.title}** (Category: `{a.metadata.category.value}`, Source: `{a.metadata.source.value}`)")

        report_md = (
            f"# Centralized Documentation Sync Report\n\n"
            f"**Result ID**: `{result.result_id}`\n"
            f"**Session ID**: `{result.session_id}`\n"
            f"**Total Registered Documents**: {len(result.artifacts)}\n\n"
            f"## Registered Documentation Listing\n"
            + ("\n".join(docs_md) if docs_md else "- *No documents registered.*")
        )

        doc = KnowledgeDocument(
            document_id=f"doc_sync_{result.result_id}",
            title=f"Documentation Sync - {result.result_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"doc_sync_{result.result_id}",
                timestamp=time.time(),
                source_subsystem="documentation_service",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

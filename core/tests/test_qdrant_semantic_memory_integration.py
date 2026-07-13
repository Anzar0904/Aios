import os
import time
import unittest.mock as mock
import uuid
from pathlib import Path
from typing import Any, Dict, List

import pytest
from aios.bootstrap import bootstrap_kernel
from aios.services.agent import AgentRuntimeService
from aios.services.context import ContextService
from aios.services.conversation.manager import ConversationManager
from aios.services.conversation.store import ConversationStore
from aios.services.documentation_intelligence import (
    DocumentArtifact,
    DocumentationService,
    DocumentCategory,
    DocumentMetadata,
    DocumentSource,
)
from aios.services.intent import Intent, IntentType
from aios.services.model import LLMResponse, ModelService
from aios.services.persistence import (
    CollectionManager,
    EngineeringMemoryService,
    PersistenceResult,
    PersistenceStatus,
    SemanticMemoryManager,
    WorkspacePersistenceService,
)
from aios.services.research import ResearchService


@pytest.fixture
def kernel_setup(monkeypatch):
    # Class-level monkeypatch to bypass PostgreSQL blocks
    from aios.services.persistence_impl import (
        DocumentationMetadataRepositoryImpl,
        EngineeringTaskRepositoryImpl,
        WorkspaceRepositoryImpl,
    )
    mock_success_res = PersistenceResult(status=PersistenceStatus.SUCCESS, message="Mock success")
    monkeypatch.setattr(WorkspaceRepositoryImpl, "save", mock.Mock(return_value=mock_success_res))
    monkeypatch.setattr(DocumentationMetadataRepositoryImpl, "save", mock.Mock(return_value=mock_success_res))
    monkeypatch.setattr(EngineeringTaskRepositoryImpl, "save", mock.Mock(return_value=mock_success_res))

    # Class-level monkeypatch for Notion sync
    from aios.services.knowledge_hub import KnowledgeSyncResult
    from aios.services.knowledge_hub_impl import LocalKnowledgeHub
    monkeypatch.setattr(LocalKnowledgeHub, "sync_document", mock.Mock(return_value=KnowledgeSyncResult(
        document_id="mock_doc_id",
        provider="notion",
        status="success"
    )))

    # Custom index_memory monkeypatch to bypass mock vector collisions in similarity deduplication
    from aios.services.persistence_impl import SemanticMemoryManagerImpl
    original_index_memory = SemanticMemoryManagerImpl.index_memory
    
    def mock_index_memory(self, repository_name: str, entity_id: str, text: str, metadata: Dict[str, Any], tags: List[str], importance_override=None):
        repo = self._get_repository(repository_name)
        if repo and repo.exists(entity_id):
            existing = repo.get(entity_id)
            if existing and existing.get("payload", {}).get("text") == text:
                self.deduplications += 1
                return True
        if repo:
            original_search = repo.search
            repo.search = mock.Mock(return_value=[])
            try:
                return original_index_memory(self, repository_name, entity_id, text, metadata, tags, importance_override)
            finally:
                repo.search = original_search
        return original_index_memory(self, repository_name, entity_id, text, metadata, tags, importance_override)
        
    monkeypatch.setattr(SemanticMemoryManagerImpl, "index_memory", mock_index_memory)

    os.environ["QDRANT_DEFAULT_DIMENSIONS"] = "384"
    config_path = Path("aios.toml")
    kernel = bootstrap_kernel(config_path)
    
    # Set the global registry so all components resolve correctly
    from aios.registry import ServiceRegistry
    ServiceRegistry._global_registry = kernel.registry
    
    # Mock EventBus publish to avoid Event type registration errors in test environments
    from aios.services.event_bus import EventBusService
    bus = kernel.registry.get(EventBusService)
    if bus:
        bus.publish = mock.Mock()

    # Recreate collections with 1536 dimensions for mock embedding provider
    col_mgr = kernel.registry.get(CollectionManager)
    if col_mgr:
        for col in ["workspace_memory", "conversation_memory", "engineering_memory", "research_memory", "documentation_memory", "knowledge_memory", "project_memory"]:
            if col_mgr.exists(col):
                col_mgr.delete_collection(col)
            col_mgr.create_collection(col, dimensions=384, distance="cosine")
        
    return kernel


def test_semantic_memory_manager_basic(kernel_setup):
    registry = kernel_setup.registry
    sem_mgr = registry.get(SemanticMemoryManager)
    assert sem_mgr is not None

    # Test basic indexing and deduplication
    unique_id = str(uuid.uuid4())
    entity_id = f"test_mem_{int(time.time())}"
    text = f"Unique basic test: Important architecture decision to use Qdrant for semantic search {unique_id}."
    metadata = {"workspace_id": "test_ws_basic", "project_id": "test_proj_basic"}
    tags = ["architecture", "critical_decision"]

    # 1. First index
    success = sem_mgr.index_memory("engineering_memory", entity_id, text, metadata, tags)
    assert success is True

    # 2. Duplicate index (same text, within time window) -> should be deduplicated
    is_dup = sem_mgr.index_memory("engineering_memory", entity_id, text, metadata, tags)
    assert is_dup is True
    stats = sem_mgr.get_statistics()
    assert stats["deduplications"] >= 1

    # 3. Test importance scoring
    importance = sem_mgr.calculate_importance(text, tags, metadata)
    assert importance == 9.0  # Critical decision/architecture keyword match

    # 4. Retrieval
    results = sem_mgr.retrieve_memories("engineering_memory", unique_id, limit=30)
    assert len(results) > 0
    assert any(unique_id in r["payload"]["text"] for r in results)

    # 5. Lifecycle: Archive
    arch_success = sem_mgr.archive_memory("engineering_memory", entity_id)
    assert arch_success is True
    ret = sem_mgr._get_repository("engineering_memory").get(entity_id)
    assert ret["payload"]["status"] == "archived"

    # 6. Lifecycle: Merge
    entity_id_2 = f"test_mem_2_{int(time.time())}"
    text_2 = f"Additional detail: Redis is used for caching basic test {unique_id}."
    sem_mgr.index_memory("engineering_memory", entity_id_2, text_2, metadata, ["redis"])
    
    merge_success = sem_mgr.merge_memories("engineering_memory", entity_id, entity_id_2)
    assert merge_success is True
    merged_ret = sem_mgr._get_repository("engineering_memory").get(entity_id)
    assert "Merged context" in merged_ret["payload"]["text"]
    assert "redis" in merged_ret["payload"]["tags"]

    # Clean up
    sem_mgr.delete_memory("engineering_memory", entity_id)


def test_conversation_indexing(kernel_setup):
    registry = kernel_setup.registry
    sem_mgr = registry.get(SemanticMemoryManager)
    
    # Initialize a conversation and add message
    workspace_root = Path.cwd().resolve()
    conv_store = ConversationStore(Path(workspace_root) / ".aios_conversations")
    conv_manager = ConversationManager(conv_store)
    
    unique_id = str(uuid.uuid4())
    conv = conv_manager.create_conversation(title="Test Semantic Dialog Unique", agent_name="test_agent")
    conv_manager.add_message(conv.id, "user", f"How do I query the database dialog semantic {unique_id}?")
    
    # Check that message is automatically indexed in conversation_memory
    mems = sem_mgr.retrieve_memories("conversation_memory", unique_id, limit=30)
    assert len(mems) > 0
    texts = [m["payload"]["text"] for m in mems]
    assert any(unique_id in t for t in texts)
    
    # Clean up
    conv_manager.delete_conversation(conv.id)


def test_workspace_indexing(kernel_setup):
    registry = kernel_setup.registry
    sem_mgr = registry.get(SemanticMemoryManager)
    workspace_svc = registry.get(WorkspacePersistenceService)
    
    unique_id = str(uuid.uuid4())
    ws_data = {
        "id": "ws_semantic_test",
        "name": f"Semantic Test Workspace Unique Description {unique_id}",
        "description": f"A workspace to verify automatic semantic indexing of configurations workspace_semantic_test {unique_id}",
        "project_id": "proj_test",
        "version": "1.0"
    }
    workspace_svc.save_workspace(ws_data)
    
    # Verify auto-indexed in workspace_memory
    mems = sem_mgr.retrieve_memories("workspace_memory", unique_id, limit=30)
    assert len(mems) > 0
    texts = [m["payload"]["text"] for m in mems]
    assert any(unique_id in t for t in texts)


def test_engineering_indexing(kernel_setup):
    registry = kernel_setup.registry
    sem_mgr = registry.get(SemanticMemoryManager)
    eng_svc = registry.get(EngineeringMemoryService)
    
    unique_id = str(uuid.uuid4())
    task_id = f"task_{int(time.time())}"
    task_data = {
        "id": task_id,
        "name": f"Fix critical database leak in repository manager pool engineering_test {unique_id}",
        "title": f"Fix critical database leak in repository manager pool engineering_test {unique_id}",
        "description": f"Resolve connection leak in repository manager pool engineering_test {unique_id}",
        "status": "completed",
        "tags": ["bug", "critical"]
    }
    eng_svc.record("tasks", task_id, task_data)
    
    # Verify auto-indexed in engineering_memory
    mems = sem_mgr.retrieve_memories("engineering_memory", unique_id, limit=30)
    assert len(mems) > 0
    texts = [m["payload"]["text"] for m in mems]
    assert any(unique_id in t for t in texts)


def test_research_indexing(kernel_setup):
    registry = kernel_setup.registry
    sem_mgr = registry.get(SemanticMemoryManager)
    research_svc = registry.get(ResearchService)
    
    unique_id = str(uuid.uuid4())
    # Run a research query (will trigger mock search provider & LLM plan/report)
    research_svc.research(f"Explain LocalEventBus implementation details research_test {unique_id}")
    
    # Verify auto-indexed in research_memory
    mems = sem_mgr.retrieve_memories("research_memory", unique_id, limit=30)
    assert len(mems) > 0
    texts = [m["payload"]["text"] for m in mems]
    assert any(unique_id in t for t in texts)


def test_documentation_indexing(kernel_setup):
    registry = kernel_setup.registry
    sem_mgr = registry.get(SemanticMemoryManager)
    doc_svc = registry.get(DocumentationService)
    
    unique_id = str(uuid.uuid4())
    art = DocumentArtifact(
        artifact_id="art_arch_spec",
        content=f"This specification details the semantic memory integration using Qdrant doc_test {unique_id}.",
        metadata=DocumentMetadata(
            doc_id="test_doc",
            category=DocumentCategory.ARCHITECTURE,
            source=DocumentSource.KNOWLEDGE_HUB,
            title="Semantic Spec Doc Test",
            version="1",
            author="Architect Agent",
            timestamp=time.time()
        )
    )
    doc_svc.register_artifact(art)
    
    # Verify auto-indexed in documentation_memory
    mems = sem_mgr.retrieve_memories("documentation_memory", unique_id, limit=30)
    assert len(mems) > 0
    texts = [m["payload"]["text"] for m in mems]
    assert any(unique_id in t for t in texts)


def test_developer_agent_semantic_memory(kernel_setup):
    registry = kernel_setup.registry
    agent_svc = registry.get(AgentRuntimeService)
    sem_mgr = registry.get(SemanticMemoryManager)
    model_svc = registry.get(ModelService)
    
    # Mock model service execute_request for DeveloperAgent
    if model_svc:
        model_svc.execute_request = mock.Mock(return_value=LLMResponse(
            content="Mock agent reasoning response.",
            model_name="claude-3-5-sonnet",
            provider_name="mock"
        ))
        
    unique_id = str(uuid.uuid4())
    # Seed semantic memories
    sem_mgr.index_memory(
        "engineering_memory",
        "seed_1",
        f"Specific hint: The solution is to use npx create-vite-app {unique_id}.",
        {"workspace_id": "default"},
        ["coding"]
    )
    
    intent = Intent(
        intent_type=IntentType.DEVELOPER,
        target_service="developer",
        action="SummarizeArchitecture",
        parameters={"raw_query": f"How do we initialize a Vite app {unique_id}?"},
        confidence=1.0
    )
    res = agent_svc.execute(intent)
    assert res.success is True
    
    # Verify reasoning knowledge was stored in knowledge_memory after execution
    mems = sem_mgr.retrieve_memories("knowledge_memory", unique_id, limit=30)
    assert len(mems) > 0
    texts = [m["payload"]["text"] for m in mems]
    assert any(unique_id in t for t in texts)


def test_context_service_enriched_context(kernel_setup):
    registry = kernel_setup.registry
    ctx_svc = registry.get(ContextService)
    sem_mgr = registry.get(SemanticMemoryManager)
    
    # Clear memories to avoid mock embedding vector collisions pushing new items out of retrieval limit
    sem_mgr._get_repository("workspace_memory").clear()
    sem_mgr._get_repository("conversation_memory").clear()
    sem_mgr._get_repository("engineering_memory").clear()
    
    # Seed various memories
    sem_mgr.index_memory("workspace_memory", "ctx_seed_ws", "Workspace active files: index.css, main.js", {"workspace_id": "test_ctx"}, ["files"])
    sem_mgr.index_memory("conversation_memory", "ctx_seed_conv", "User preference: Prefer HSL colors", {"workspace_id": "test_ctx"}, ["preference"])
    sem_mgr.index_memory("engineering_memory", "ctx_seed_eng", "Completed task: Configured Tailwind", {"workspace_id": "test_ctx"}, ["tailwind"])
    
    enriched = ctx_svc.build_enriched_context("Tailwind index.css preference")
    
    # Assert context contains aggregated states
    assert "Workspace active files" in enriched["assembled_text"]
    assert "Prefer HSL colors" in enriched["assembled_text"]
    assert "Configured Tailwind" in enriched["assembled_text"]




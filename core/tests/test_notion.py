import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest
from aios.services.memory import MemoryType
from aios.services.notion import NotionCredentialsStore
from aios.services.notion_impl import LocalNotionService


def test_credentials_store_isolated(tmp_path):
    # Setup custom temp credentials path
    cred_path = tmp_path / "credentials.json"
    store = NotionCredentialsStore(path=cred_path)

    # Initially empty
    assert store.load_all() == {}

    # Save a workspace token
    store.save_token("workspace_1", "secret_123")
    assert store.load_all() == {"workspace_1": "secret_123"}
    assert (cred_path.stat().st_mode & 0o777) == 0o600

    # Save another workspace token (check multiple workspaces)
    store.save_token("workspace_2", "secret_456")
    loaded = store.load_all()
    assert loaded["workspace_1"] == "secret_123"
    assert loaded["workspace_2"] == "secret_456"
    assert (cred_path.stat().st_mode & 0o777) == 0o600

    # Delete workspace_1
    store.delete_workspace("workspace_1")
    assert store.load_all() == {"workspace_2": "secret_456"}
    assert (cred_path.stat().st_mode & 0o777) == 0o600

    # Delete all
    store.delete_all()
    assert store.load_all() == {}
    assert not cred_path.exists()


def test_local_notion_service_lifecycle(tmp_path):
    cred_path = tmp_path / "credentials.json"

    # Instantiate service
    service = LocalNotionService(credentials_path=cred_path)
    service.initialize()
    service.start()

    # Check status initially disconnected
    status = service.get_status()
    assert status["status"] == "disconnected"
    assert status["workspaces"] == []

    # Login workspace_1
    success = service.login("secret_abc", "workspace_1")
    assert success is True

    # Status should be connected
    status = service.get_status()
    assert status["status"] == "connected"
    assert status["workspaces"] == ["workspace_1"]

    # Login workspace_2
    success = service.login("secret_xyz", "workspace_2")
    assert success is True
    status = service.get_status()
    assert status["status"] == "connected"
    assert sorted(status["workspaces"]) == ["workspace_1", "workspace_2"]

    # Initialize a new service instance to verify persistence/load on initialization
    service_persistent = LocalNotionService(credentials_path=cred_path)
    service_persistent.initialize()
    status_persistent = service_persistent.get_status()
    assert status_persistent["status"] == "connected"
    assert sorted(status_persistent["workspaces"]) == ["workspace_1", "workspace_2"]

    # Logout workspace_1
    success = service.logout("workspace_1")
    assert success is True
    status = service.get_status()
    assert status["workspaces"] == ["workspace_2"]

    # Logout all (by passing None)
    success = service.logout(None)
    assert success is True
    status = service.get_status()
    assert status["status"] == "disconnected"
    assert status["workspaces"] == []

    service.shutdown()


def test_notion_service_operations(tmp_path):
    cred_path = tmp_path / "credentials.json"
    cache_path = tmp_path / "cache.json"

    # 1. Setup mock cache file content
    cache_data = {
        "workspace_1": {
            "metadata": {"last_sync_time": "2026-07-08T10:00:00.000Z"},
            "pages": [
                {
                    "object": "page",
                    "id": "page_1",
                    "last_edited_time": "2026-07-08T10:00:00.000Z",
                    "parent": {"type": "database_id", "database_id": "db_1"},
                    "properties": {
                        "title": {
                            "type": "title",
                            "title": [
                                {
                                    "type": "text",
                                    "text": {"content": "Page 1 title"},
                                    "plain_text": "Page 1 title",
                                }
                            ],
                        },
                        "MyRelation": {"type": "relation", "relation": [{"id": "page_2"}]},
                    },
                    "blocks": [
                        {
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "text",
                                        "text": {"content": "Paragraph block content"},
                                        "plain_text": "Paragraph block content",
                                    }
                                ]
                            },
                        }
                    ],
                    "memory_id": "mem_page_1",
                },
                {
                    "object": "page",
                    "id": "page_2",
                    "last_edited_time": "2026-07-08T10:00:00.000Z",
                    "parent": {"type": "page_id", "page_id": "page_1"},
                    "properties": {
                        "title": {
                            "type": "title",
                            "title": [
                                {
                                    "type": "text",
                                    "text": {"content": "Page 2 title"},
                                    "plain_text": "Page 2 title",
                                }
                            ],
                        }
                    },
                    "blocks": [],
                    "memory_id": "mem_page_2",
                },
            ],
            "databases": [
                {
                    "object": "database",
                    "id": "db_1",
                    "parent": {"type": "workspace", "workspace": True},
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": "My Database"},
                            "plain_text": "My Database",
                        }
                    ],
                    "properties": {"title": {"type": "title"}},
                }
            ],
            "users": [],
        }
    }

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f)

    # 2. Setup mock services
    mock_memory_service = MagicMock()
    mock_model_service = MagicMock()

    service = LocalNotionService(
        credentials_path=cred_path,
        cache_path=cache_path,
        model_service=mock_model_service,
        memory_service=mock_memory_service,
    )
    service.initialize()
    service.login("secret_123", "workspace_1")

    # 3. Test list_databases
    dbs = service.list_databases()
    assert len(dbs) == 1
    assert dbs[0]["id"] == "db_1"

    # 4. Test explain
    explanation = service.explain("page_1")
    assert explanation["id"] == "page_1"
    assert explanation["title"] == "Page 1 title"
    assert explanation["workspace"] == "workspace_1"
    assert explanation["hierarchy"]["parent_type"] == "database_id"
    assert explanation["hierarchy"]["parent_id"] == "db_1"
    assert explanation["child_block_types"] == ["paragraph"]

    # 5. Test summarize
    # Mock ModelService execution response
    mock_response = MagicMock()
    mock_response.content = "This is a great summary of Page 1."
    mock_model_service.execute_request.return_value = mock_response

    summary = service.summarize("page_1")
    assert summary == "This is a great summary of Page 1."

    # Assert ModelService was called with LLMRequest containing prompt
    mock_model_service.execute_request.assert_called_once()
    llm_req = mock_model_service.execute_request.call_args[0][0]
    assert "Page 1 title" in llm_req.prompt
    assert "Paragraph block content" in llm_req.prompt

    # 6. Test create_page
    mock_response_create = {
        "object": "page",
        "id": "new_page_999",
        "parent": {"type": "page_id", "page_id": "page_1"},
        "properties": {
            "title": {
                "type": "title",
                "title": [
                    {
                        "type": "text",
                        "text": {"content": "New Child Page"},
                        "plain_text": "New Child Page",
                    }
                ],
            }
        },
    }

    mock_memory = MagicMock()
    mock_memory.memory_id = "mem_new_page"
    mock_memory_service.add_memory.return_value = mock_memory

    # Mock httpx client response
    with patch("aios.services.notion_impl.httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        mock_http_response = MagicMock()
        mock_http_response.json.return_value = mock_response_create
        mock_client.request.return_value = mock_http_response

        new_page = service.create_page(
            parent_id="page_1", title="New Child Page", content="Line 1 content\nLine 2 content"
        )
        assert new_page["id"] == "new_page_999"

        # Verify request parameters
        mock_client.request.assert_called_once()
        method, url = mock_client.request.call_args[0]
        assert method == "POST"
        assert "/v1/pages" in url

        json_payload = mock_client.request.call_args[1]["json"]
        assert json_payload["parent"]["page_id"] == "page_1"
        assert len(json_payload["children"]) == 2
        assert (
            json_payload["children"][0]["paragraph"]["rich_text"][0]["text"]["content"]
            == "Line 1 content"
        )

        # Verify MemoryService and cache updates
        mock_memory_service.add_memory.assert_called_once()
        mock_memory_service.commit.assert_called_once()

        # Reload cache to verify creation persisted
        with open(cache_path, "r", encoding="utf-8") as f:
            updated_cache = json.load(f)
        ws_pages = updated_cache["workspace_1"]["pages"]
        assert any(p["id"] == "new_page_999" for p in ws_pages)
        created_cached_page = next(p for p in ws_pages if p["id"] == "new_page_999")
        assert created_cached_page["memory_id"] == "mem_new_page"

    # 7. Test update_page
    mock_response_update = {
        "object": "list",
        "results": [
            {
                "object": "block",
                "id": "block_new_1",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": "Updated paragraph content"},
                            "plain_text": "Updated paragraph content",
                        }
                    ]
                },
            }
        ],
    }

    mock_memory_service.commit.reset_mock()
    with patch("aios.services.notion_impl.httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        mock_http_response = MagicMock()
        mock_http_response.json.return_value = mock_response_update
        mock_client.request.return_value = mock_http_response

        update_res = service.update_page(page_id="page_1", content="Updated paragraph content")
        assert update_res["status"] == "updated"
        assert update_res["blocks_added"] == 1

        # Verify request parameters
        mock_client.request.assert_called_once()
        method, url = mock_client.request.call_args[0]
        assert method == "POST"
        assert "/v1/blocks/page_1/children" in url

        # Verify memory/cache update
        mock_memory_service.update_memory.assert_called_once()
        mock_memory_service.commit.assert_called_once()

        with open(cache_path, "r", encoding="utf-8") as f:
            updated_cache = json.load(f)
        ws_pages = updated_cache["workspace_1"]["pages"]
        updated_cached_page = next(p for p in ws_pages if p["id"] == "page_1")
        assert len(updated_cached_page["blocks"]) == 2
        assert updated_cached_page["blocks"][1]["id"] == "block_new_1"

    # 8. Test search
    search_results = service.search("title")
    assert len(search_results) == 3
    assert {r["id"] for r in search_results} == {"page_1", "page_2", "new_page_999"}

    db_search = service.search("Database")
    assert len(db_search) == 2
    assert {d["id"] for d in db_search} == {"page_1", "db_1"}


def test_notion_service_generate_graphs(tmp_path):
    cred_path = tmp_path / "credentials.json"
    cache_path = tmp_path / "cache.json"
    graphs_path = tmp_path / "graphs"

    # Setup mock cache
    cache_data = {
        "workspace_1": {
            "metadata": {"last_sync_time": "2026-07-08T10:00:00.000Z"},
            "pages": [
                {
                    "object": "page",
                    "id": "page_1",
                    "parent": {"type": "workspace", "workspace": True},
                    "properties": {
                        "title": {
                            "type": "title",
                            "title": [
                                {
                                    "type": "text",
                                    "text": {"content": "Page 1 Title"},
                                    "plain_text": "Page 1 Title",
                                }
                            ],
                        },
                        "relation_prop": {"type": "relation", "relation": [{"id": "page_2"}]},
                    },
                    "blocks": [
                        {
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [
                                    {
                                        "type": "mention",
                                        "mention": {"type": "database", "database": {"id": "db_1"}},
                                    }
                                ]
                            },
                        }
                    ],
                },
                {
                    "object": "page",
                    "id": "page_2",
                    "parent": {"type": "database_id", "database_id": "db_1"},
                    "properties": {
                        "title": {
                            "type": "title",
                            "title": [
                                {
                                    "type": "text",
                                    "text": {"content": "Page 2 Title"},
                                    "plain_text": "Page 2 Title",
                                }
                            ],
                        }
                    },
                    "blocks": [],
                },
            ],
            "databases": [
                {
                    "object": "database",
                    "id": "db_1",
                    "parent": {"type": "workspace", "workspace": True},
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": "Database 1"},
                            "plain_text": "Database 1",
                        }
                    ],
                    "properties": {"title": {"type": "title"}},
                }
            ],
            "users": [],
        }
    }

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache_data, f)

    service = LocalNotionService(credentials_path=cred_path, cache_path=cache_path)
    service.initialize()

    # Generate graphs
    result = service.generate_graphs(graphs_dir=graphs_path)

    assert result["status"] == "success"
    assert result["graphs_dir"] == str(graphs_path)

    # Assert all files were written
    expected_files = [
        "workspace_graph.dot",
        "page_relationship.dot",
        "database_relationship.dot",
        "sync_dependency.dot",
        "notion_graphs.md",
    ]

    for filename in expected_files:
        filepath = graphs_path / filename
        assert filepath.is_file()

        # Read to verify basic DOT/Markdown syntax
        content = filepath.read_text(encoding="utf-8")
        if filename.endswith(".dot"):
            assert content.startswith("digraph ")
            assert content.endswith("}\n")
        else:
            assert "# Notion Workspace Relationships Summary" in content
            assert "```mermaid" in content


def test_credentials_store_default_path():
    store = NotionCredentialsStore()
    assert store.path == Path(".agent/notion/credentials.json")


def test_local_notion_service_login_invalid_inputs(tmp_path):
    cred_path = tmp_path / "credentials.json"
    service = LocalNotionService(credentials_path=cred_path)
    service.initialize()

    # Empty token
    assert service.login("", "workspace_1") is False

    # Empty workspace name
    assert service.login("secret_abc", "") is False

    # Both empty
    assert service.login("", "") is False


def test_local_notion_service_request_error(tmp_path):
    cred_path = tmp_path / "credentials.json"
    cache_path = tmp_path / "cache.json"
    service = LocalNotionService(credentials_path=cred_path, cache_path=cache_path)
    service.initialize()
    service.login("secret_abc", "workspace_1")

    with patch("aios.services.notion_impl.httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client

        # Mock an HTTP status error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Mocked HTTP error", request=MagicMock(), response=mock_response
        )
        mock_client.request.return_value = mock_response

        with pytest.raises(httpx.HTTPStatusError):
            service._request("GET", "/v1/users")


def test_local_notion_service_crawl_and_cache(tmp_path):
    cred_path = tmp_path / "credentials.json"
    cache_path = tmp_path / "cache.json"
    service = LocalNotionService(credentials_path=cred_path, cache_path=cache_path)
    service.initialize()
    service.login("secret_abc", "workspace_1")

    def mock_request_side_effect(method, url, **kwargs):
        response_mock = MagicMock()

        if "/v1/search" in url:
            body = kwargs.get("json", {})
            if body and body.get("start_cursor") == "cursor_page_2":
                response_mock.json.return_value = {
                    "results": [{"object": "page", "id": "page_id_2"}],
                    "has_more": False,
                    "next_cursor": None,
                }
            else:
                response_mock.json.return_value = {
                    "results": [
                        {"object": "page", "id": "page_id_1"},
                        {"object": "database", "id": "db_id_1"},
                    ],
                    "has_more": True,
                    "next_cursor": "cursor_page_2",
                }
        elif "/v1/blocks/page_id_1/children" in url:
            response_mock.json.return_value = {
                "results": [
                    {"object": "block", "id": "block_id_1", "has_children": True},
                    {"object": "block", "id": "block_id_2", "has_children": False},
                ],
                "has_more": False,
                "next_cursor": None,
            }
        elif "/v1/blocks/page_id_2/children" in url:
            response_mock.json.return_value = {
                "results": [],
                "has_more": False,
                "next_cursor": None,
            }
        elif "/v1/blocks/block_id_1/children" in url:
            response_mock.json.return_value = {
                "results": [{"object": "block", "id": "block_child_1", "has_children": False}],
                "has_more": False,
                "next_cursor": None,
            }
        elif "/v1/users" in url:
            response_mock.json.return_value = {
                "results": [{"object": "user", "id": "user_id_1", "name": "Alice"}],
                "has_more": False,
                "next_cursor": None,
            }
        else:
            response_mock.json.return_value = {}

        return response_mock

    with patch("aios.services.notion_impl.httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        mock_client.request.side_effect = mock_request_side_effect

        # Trigger crawl
        result = service._crawl_workspace("workspace_1", "secret_abc")

        # Verify structured result format
        assert "pages" in result
        assert "databases" in result
        assert "users" in result

        assert len(result["pages"]) == 2
        assert len(result["databases"]) == 1
        assert len(result["users"]) == 1

        # Check recursion in blocks
        page1 = next(p for p in result["pages"] if p["id"] == "page_id_1")
        assert "blocks" in page1
        assert len(page1["blocks"]) == 2
        block1 = next(b for b in page1["blocks"] if b["id"] == "block_id_1")
        assert "children" in block1
        assert len(block1["children"]) == 1
        assert block1["children"][0]["id"] == "block_child_1"

        # Verify cache serialization
        assert cache_path.is_file()
        with open(cache_path, "r", encoding="utf-8") as f:
            cache_content = json.load(f)

        assert "workspace_1" in cache_content
        cached_ws = cache_content["workspace_1"]
        assert len(cached_ws["pages"]) == 2
        assert len(cached_ws["databases"]) == 1
        assert len(cached_ws["users"]) == 1

        # Check sync method triggers the crawling for all active workspaces
        # We will add another workspace to test sync behavior
        service.login("secret_xyz", "workspace_2")

        # Reset mock calls count/state
        mock_client.request.reset_mock()

        sync_result = service.sync()
        assert sync_result["status"] == "success"
        assert "workspace_1" in sync_result["workspaces"]
        assert "workspace_2" in sync_result["workspaces"]

        # Both workspaces should now be present in the cache file
        with open(cache_path, "r", encoding="utf-8") as f:
            updated_cache = json.load(f)
        assert "workspace_1" in updated_cache
        assert "workspace_2" in updated_cache


def test_local_notion_service_incremental_sync_and_memory_service(tmp_path):
    cred_path = tmp_path / "credentials.json"
    cache_path = tmp_path / "cache.json"

    # Setup Mock MemoryService
    mock_memory_service = MagicMock()
    added_memories = []
    updated_memories = []

    def mock_add_memory(content, memory_type, tags=None, importance=1, metadata_additional=None):
        mem = MagicMock()
        mem.memory_id = f"mem_id_{len(added_memories) + 1}"
        mem.content = content
        mem.memory_type = memory_type
        mem.tags = tags
        mem.metadata = MagicMock()
        mem.metadata.additional = metadata_additional
        added_memories.append(mem)
        return mem

    def mock_update_memory(
        memory_id, content=None, tags=None, importance=None, metadata_additional=None
    ):
        mem = MagicMock()
        mem.memory_id = memory_id
        mem.content = content
        mem.tags = tags
        mem.metadata = MagicMock()
        mem.metadata.additional = metadata_additional
        updated_memories.append(mem)
        return mem

    mock_memory_service.add_memory.side_effect = mock_add_memory
    mock_memory_service.update_memory.side_effect = mock_update_memory

    service = LocalNotionService(
        credentials_path=cred_path, cache_path=cache_path, memory_service=mock_memory_service
    )
    service.initialize()
    service.login("secret_abc", "workspace_1")

    # Define mock response variables to simulate Notion API behavior over multiple syncs
    search_results = []
    block_results = []

    def mock_request_side_effect(method, url, **kwargs):
        response_mock = MagicMock()
        if "/v1/search" in url:
            response_mock.json.return_value = {
                "results": search_results,
                "has_more": False,
                "next_cursor": None,
            }
        elif "/v1/blocks/page_id_1/children" in url:
            response_mock.json.return_value = {
                "results": block_results,
                "has_more": False,
                "next_cursor": None,
            }
        elif "/v1/users" in url:
            response_mock.json.return_value = {
                "results": [],
                "has_more": False,
                "next_cursor": None,
            }
        else:
            response_mock.json.return_value = {}
        return response_mock

    with patch("aios.services.notion_impl.httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value.__enter__.return_value = mock_client
        mock_client.request.side_effect = mock_request_side_effect

        # --- FIRST SYNC: FULL SYNC ---
        search_results = [
            {
                "object": "page",
                "id": "page_id_1",
                "last_edited_time": "2026-07-08T10:00:00.000Z",
                "properties": {
                    "Name": {
                        "type": "title",
                        "title": [{"type": "text", "text": {"content": "Initial Title"}}],
                    }
                },
            }
        ]
        block_results = [
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "Hello page content"}}]
                },
            }
        ]

        service.sync()

        # Verify blocks crawled
        # Search request + block children request + users request
        urls_called = [args[1] for args, _ in mock_client.request.call_args_list]
        assert any("/v1/blocks/page_id_1/children" in u for u in urls_called)

        # Verify add_memory called
        assert len(added_memories) == 1
        assert "Initial Title" in added_memories[0].content
        assert "Hello page content" in added_memories[0].content
        assert added_memories[0].memory_type == MemoryType.NOTE
        assert added_memories[0].tags == ["notion"]
        assert added_memories[0].metadata.additional["page_id"] == "page_id_1"
        assert added_memories[0].metadata.additional["workspace_name"] == "workspace_1"
        mock_memory_service.commit.assert_called_once()

        # Cache file should record the memory ID
        with open(cache_path, "r", encoding="utf-8") as f:
            cache_content = json.load(f)
        cached_page = cache_content["workspace_1"]["pages"][0]
        assert cached_page["memory_id"] == "mem_id_1"
        assert "last_sync_time" in cache_content["workspace_1"]["metadata"]

        # Reset mocks for next stage
        mock_client.request.reset_mock()
        mock_memory_service.commit.reset_mock()
        added_memories.clear()
        updated_memories.clear()

        # --- SECOND SYNC: INCREMENTAL SYNC - UNCHANGED ---
        # The page state remains identical (same last_edited_time)
        service.sync()

        # Verify NO blocks crawled
        urls_called_2 = [args[1] for args, _ in mock_client.request.call_args_list]
        assert not any("/v1/blocks/page_id_1/children" in u for u in urls_called_2)

        # Verify no memory updates or additions
        assert len(added_memories) == 0
        assert len(updated_memories) == 0

        # Reset mocks for next stage
        mock_client.request.reset_mock()
        mock_memory_service.commit.reset_mock()
        added_memories.clear()
        updated_memories.clear()

        # --- THIRD SYNC: INCREMENTAL SYNC - CHANGED ---
        # Update search results to simulate updated page
        search_results = [
            {
                "object": "page",
                "id": "page_id_1",
                "last_edited_time": "2028-07-08T11:00:00.000Z",
                "properties": {
                    "Name": {
                        "type": "title",
                        "title": [{"type": "text", "text": {"content": "Updated Title"}}],
                    }
                },
            }
        ]
        block_results = [
            {
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": "Modified page content"}}]
                },
            }
        ]

        service.sync()

        # Verify blocks crawled again since it was modified
        urls_called_3 = [args[1] for args, _ in mock_client.request.call_args_list]
        assert any("/v1/blocks/page_id_1/children" in u for u in urls_called_3)

        # Verify update_memory was called instead of add_memory
        assert len(added_memories) == 0
        assert len(updated_memories) == 1
        assert updated_memories[0].memory_id == "mem_id_1"
        assert "Updated Title" in updated_memories[0].content
        assert "Modified page content" in updated_memories[0].content
        mock_memory_service.commit.assert_called_once()

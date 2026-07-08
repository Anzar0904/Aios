import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest
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


def test_stub_methods(tmp_path):
    cred_path = tmp_path / "credentials.json"
    service = LocalNotionService(credentials_path=cred_path)
    service.initialize()
    service.login("secret_123", "workspace_1")

    # sync
    with patch.object(service, "_crawl_workspace", return_value={"pages": []}) as mock_crawl:
        sync_res = service.sync()
        mock_crawl.assert_called_once_with("workspace_1", "secret_123")
    assert sync_res["status"] == "success"
    assert sync_res["synced_pages"] == 0
    assert "workspace_1" in sync_res["workspaces"]

    # search
    assert service.search("query") == []

    # summarize
    assert service.summarize("page_123") == "Summary of page page_123"

    # create_page
    create_res = service.create_page("parent_abc", "My Page", "Hello World")
    assert create_res["id"] == "mock_page_parent_abc"
    assert create_res["title"] == "My Page"
    assert create_res["status"] == "created"

    # update_page
    update_res = service.update_page("page_abc", "New Content")
    assert update_res["id"] == "page_abc"
    assert update_res["content"] == "New Content"
    assert update_res["status"] == "updated"

    # list_databases
    assert service.list_databases() == []


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
            "Mocked HTTP error",
            request=MagicMock(),
            response=mock_response
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
                    "results": [
                        {"object": "page", "id": "page_id_2"}
                    ],
                    "has_more": False,
                    "next_cursor": None
                }
            else:
                response_mock.json.return_value = {
                    "results": [
                        {"object": "page", "id": "page_id_1"},
                        {"object": "database", "id": "db_id_1"}
                    ],
                    "has_more": True,
                    "next_cursor": "cursor_page_2"
                }
        elif "/v1/blocks/page_id_1/children" in url:
            response_mock.json.return_value = {
                "results": [
                    {"object": "block", "id": "block_id_1", "has_children": True},
                    {"object": "block", "id": "block_id_2", "has_children": False}
                ],
                "has_more": False,
                "next_cursor": None
            }
        elif "/v1/blocks/page_id_2/children" in url:
            response_mock.json.return_value = {
                "results": [],
                "has_more": False,
                "next_cursor": None
            }
        elif "/v1/blocks/block_id_1/children" in url:
            response_mock.json.return_value = {
                "results": [
                    {"object": "block", "id": "block_child_1", "has_children": False}
                ],
                "has_more": False,
                "next_cursor": None
            }
        elif "/v1/users" in url:
            response_mock.json.return_value = {
                "results": [
                    {"object": "user", "id": "user_id_1", "name": "Alice"}
                ],
                "has_more": False,
                "next_cursor": None
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

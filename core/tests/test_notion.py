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
    sync_res = service.sync()
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
    from pathlib import Path
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

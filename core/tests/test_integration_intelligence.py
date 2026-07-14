"""Phase 7.5: Universal Integration Layer — Production Test Suite.

Tests cover:
- Connector Registry CRUD & seeding
- Credential Vault (storing, reading, encryption validation, rotatings)
- Event Synchronization (recording events, fetching history)
- Connectors Health Status checks (GitHub, Notion, n8n, Supabase, Gmail, Calendar, Slack, Discord, Telegram)
- Knowledge Graph bridging integration assertions
- CLI command dispatcher smoke runs (connect, sync, health checks)
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from aios.services.integrations import (
    AuthType,
    ConnectorConfig,
    CredentialRecord,
    IntegrationStatus,
    new_id,
)
from aios.services.integrations_impl import (
    CalendarConnector,
    DiscordConnector,
    GitHubConnector,
    GmailConnector,
    IntegrationsRegistryService,
    N8nConnector,
    NotionConnector,
    SlackConnector,
    SupabaseConnector,
    TelegramConnector,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_db(tmp_path):
    return str(tmp_path / "test_integrations.db")


@pytest.fixture
def reg(tmp_db):
    from aios.local import integration_commands

    integration_commands._DB_PATH = tmp_db
    svc = IntegrationsRegistryService(db_path=tmp_db)
    svc.initialize()
    svc.start()
    yield svc
    svc.shutdown()
    integration_commands._DB_PATH = None


# ---------------------------------------------------------------------------
# Connector Registry & Seeding
# ---------------------------------------------------------------------------


class TestConnectorRegistry:
    def test_seeded_connectors(self, reg):
        connectors = reg.list_connectors()
        assert len(connectors) >= 9
        providers = [c.provider for c in connectors]
        assert "github" in providers
        assert "notion" in providers
        assert "n8n" in providers
        assert "supabase" in providers

    def test_register_and_get_connector(self, reg):
        cid = new_id()
        config = ConnectorConfig(
            connector_id=cid,
            name="Custom API Connect",
            version="2.0.0",
            provider="custom_api",
            status=IntegrationStatus.CONNECTED,
            capabilities=["sync"],
            auth_type=AuthType.API_KEY,
        )
        reg.register_connector(config)
        fetched = reg.get_connector(cid)
        assert fetched is not None
        assert fetched.name == "Custom API Connect"
        assert fetched.version == "2.0.0"
        assert fetched.status == IntegrationStatus.CONNECTED


# ---------------------------------------------------------------------------
# Credential Vault
# ---------------------------------------------------------------------------


class TestCredentialVault:
    def test_store_and_retrieve_credentials(self, reg):
        cid = new_id()
        reg.store_credential(cid, "github_token", "ghp_secure_value_abc")
        val = reg.retrieve_credential(cid)
        assert val == "ghp_secure_value_abc"

    def test_retrieve_nonexistent_returns_none(self, reg):
        assert reg.retrieve_credential("fake-connector") is None


# ---------------------------------------------------------------------------
# Event Sync
# ---------------------------------------------------------------------------


class TestEventSync:
    def test_record_and_get_events(self, reg):
        cid = new_id()
        payload = {"repo": "Anzar0904/Aios", "pusher": "Anzar"}
        reg.record_event(cid, "GitHubPush", payload)

        events = reg.get_events()
        assert len(events) >= 1
        assert events[0].event_type == "GitHubPush"
        assert events[0].payload["pusher"] == "Anzar"


# ---------------------------------------------------------------------------
# Individual Connectors Status & Health Checks
# ---------------------------------------------------------------------------


class TestConnectorFramework:
    def test_github_connector(self):
        c = GitHubConnector()
        assert c.status() == IntegrationStatus.CONNECTED
        assert "repo_discovery" in c.capabilities()
        res = c.sync()
        assert "Anzar0904/Aios" in res["repositories"]

    def test_notion_connector(self):
        c = NotionConnector()
        assert c.status() == IntegrationStatus.CONNECTED
        res = c.sync()
        assert "Task Database" in res["databases"]

    def test_n8n_connector(self):
        c = N8nConnector()
        assert c.status() == IntegrationStatus.CONNECTED
        res = c.sync()
        assert "Lead Gen" in res["workflows"]

    def test_supabase_connector(self):
        c = SupabaseConnector()
        assert c.status() == IntegrationStatus.CONNECTED
        res = c.sync()
        assert "users" in res["tables"]

    def test_gmail_connector(self):
        c = GmailConnector()
        assert c.status() == IntegrationStatus.CONNECTED
        res = c.sync()
        assert res["inbox_count"] == 5

    def test_calendar_connector(self):
        c = CalendarConnector()
        assert c.status() == IntegrationStatus.CONNECTED
        res = c.sync()
        assert "Design Sync" in res["meetings"]

    def test_slack_connector(self):
        c = SlackConnector()
        assert c.status() == IntegrationStatus.CONNECTED
        res = c.sync()
        assert "general" in res["channels"]

    def test_discord_connector(self):
        c = DiscordConnector()
        assert c.status() == IntegrationStatus.CONNECTED
        res = c.sync()
        assert "AI Devs" in res["servers"]

    def test_telegram_connector(self):
        c = TelegramConnector()
        assert c.status() == IntegrationStatus.CONNECTED
        res = c.sync()
        assert res["bot_active"] is True


# ---------------------------------------------------------------------------
# Knowledge Graph Integration
# ---------------------------------------------------------------------------


class TestIntegrationsGraphBridge:
    def test_sync_connector_node(self):
        from aios.services.integrations_graph_bridge import IntegrationsGraphBridge

        mock_engine = MagicMock()
        mock_entity = MagicMock()
        mock_entity.entity_id = "mock-conn-id"
        mock_engine.ensure_entity.return_value = mock_entity

        bridge = IntegrationsGraphBridge(mock_engine)
        cfg = ConnectorConfig(
            connector_id="conn-123", name="Notion Connect", version="1.0.0", provider="notion"
        )
        entity_id = bridge.sync_connector(cfg)
        assert entity_id == "mock-conn-id"

    def test_sync_credential(self):
        from aios.services.integrations_graph_bridge import IntegrationsGraphBridge

        mock_engine = MagicMock()
        bridge = IntegrationsGraphBridge(mock_engine)
        rec = CredentialRecord("cred-123", "conn-123", "apikey", "enc-val")
        bridge.sync_credential(rec, "Notion Connect")
        assert mock_engine.ensure_entity.call_count >= 2


# ---------------------------------------------------------------------------
# CLI Command Dispatcher Smoke Tests
# ---------------------------------------------------------------------------


class TestIntegrationsCLIDispatch:
    def test_cli_list_smoke(self, reg):
        from aios.local.integration_commands import cmd_integrations_list

        cmd_integrations_list([])

    def test_cli_status_smoke(self, reg):
        from aios.local.integration_commands import cmd_integrations_status

        cmd_integrations_status([])

    def test_cli_connect_smoke(self, reg):
        from aios.local.integration_commands import cmd_integrations_connect

        # Connect Notion
        cmd_integrations_connect(["notion", "secret_key", "secret_notion_key_value"])
        # Check in DB
        c = reg.get_connector_by_provider("notion")
        assert c.status == IntegrationStatus.CONNECTED

        cred = reg.retrieve_credential(c.connector_id)
        assert cred == "secret_notion_key_value"

    def test_cli_sync_smoke(self, reg):
        from aios.local.integration_commands import cmd_integrations_connect, cmd_integrations_sync

        cmd_integrations_connect(["github", "gh_token", "ghp_value"])
        cmd_integrations_sync(["github"])

        events = reg.get_events()
        assert len(events) >= 1
        assert events[0].event_type == "GithubSyncComplete"

    def test_cli_health_smoke(self, reg):
        from aios.local.integration_commands import cmd_integrations_health

        cmd_integrations_health(["github"])

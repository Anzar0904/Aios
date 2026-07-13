from unittest.mock import patch

from aios.cli import execute_builtin_cli_command
from aios.n8n.intelligence import (
    CredentialIntelligence,
    WorkflowAnalyzer,
    WorkflowIntelligenceEngine,
    WorkflowMemory,
    WorkflowOptimizer,
    WorkflowTemplates,
    WorkflowValidator,
)


def test_workflow_templates():
    """Verify built-in workflow template retrieval and listing."""
    templates = WorkflowTemplates()
    categories = templates.list_templates()

    assert "lead_generation" in categories
    assert "cold_email" in categories
    assert "crm_automation" in categories
    assert "ai_agent" in categories
    assert "customer_support" in categories

    lead_gen = templates.get_template("lead_generation")
    assert lead_gen is not None
    assert lead_gen["name"] == "Lead Generation Workflow"
    assert len(lead_gen["nodes"]) > 0
    assert "connections" in lead_gen


def test_workflow_validator_valid():
    """Verify validator identifies a correct template as valid."""
    templates = WorkflowTemplates()
    lead_gen = templates.get_template("lead_generation")

    validator = WorkflowValidator()
    res = validator.validate(lead_gen)

    assert res["valid"] is True
    assert len(res["errors"]) == 0


def test_workflow_validator_invalid_connections():
    """Verify validator flags reference to non-existent target nodes."""
    bad_workflow = {
        "nodes": [
            {
                "name": "Webhook Trigger",
                "type": "n8n-nodes-base.webhook",
            }
        ],
        "connections": {
            "Webhook Trigger": {
                "main": [
                    [
                        {
                            "node": "Non Existent Node",
                            "type": "main",
                            "index": 0,
                        }
                    ]
                ]
            }
        },
    }

    validator = WorkflowValidator()
    res = validator.validate(bad_workflow)

    assert res["valid"] is False
    assert any("references non-existent target node" in err for err in res["errors"])


def test_workflow_validator_circular():
    """Verify cycle detection identifies circular execution loops."""
    circular_workflow = {
        "nodes": [
            {"name": "Node A", "type": "n8n-nodes-base.code"},
            {"name": "Node B", "type": "n8n-nodes-base.code"},
        ],
        "connections": {
            "Node A": {"main": [[{"node": "Node B", "type": "main", "index": 0}]]},
            "Node B": {"main": [[{"node": "Node A", "type": "main", "index": 0}]]},
        },
    }

    validator = WorkflowValidator()
    res = validator.validate(circular_workflow)

    assert res["valid"] is False
    assert any("Circular execution loop" in err for err in res["errors"])


def test_credential_intelligence():
    """Verify detection of required credentials from node types."""
    templates = WorkflowTemplates()
    lead_gen = templates.get_template("lead_generation")

    cred_intel = CredentialIntelligence()
    creds = cred_intel.detect_required_credentials(lead_gen)

    assert "PostgreSQL API" in creds
    assert "Slack OAuth2 API" in creds


def test_workflow_optimizer():
    """Verify redundant duplicate nodes are consolidated."""
    wf_with_duplicates = {
        "nodes": [
            {"name": "Trigger", "type": "n8n-nodes-base.webhook"},
            {
                "name": "Slack Notify 1",
                "type": "n8n-nodes-base.slack",
                "parameters": {"text": "hello"},
            },
            {
                "name": "Slack Notify 2",
                "type": "n8n-nodes-base.slack",
                "parameters": {"text": "hello"},
            },
        ],
        "connections": {
            "Trigger": {"main": [[{"node": "Slack Notify 1", "type": "main", "index": 0}]]}
        },
    }

    optimizer = WorkflowOptimizer()
    opt = optimizer.optimize(wf_with_duplicates)

    assert len(opt["nodes"]) == 2  # Consolidates duplicate Slack node
    assert "Trigger" in opt["connections"]


def test_workflow_analyzer():
    """Verify path analysis bottlenecks and suggestion reporting."""
    templates = WorkflowTemplates()
    ai_agent = templates.get_template("ai_agent")

    analyzer = WorkflowAnalyzer()
    res = analyzer.analyze(ai_agent)

    assert "Query" in res["summary"] or "nodes" in res["summary"]
    assert "User Query Trigger" in res["trigger_chain"]
    assert "OpenAI Credentials" in res["credentials_required"]


def test_workflow_memory(tmp_path):
    """Verify save, search, list operations inside WorkflowMemory."""
    # Patch CACHE_DIR to run inside temporary folder
    with patch("aios.n8n.intelligence.CACHE_DIR", tmp_path):
        memory = WorkflowMemory()

        wf = {"name": "Test Workflow", "nodes": []}
        memory.save_workflow("Test Workflow", wf)

        listed = memory.list_workflows()
        assert len(listed) == 1
        assert listed[0]["name"] == "Test Workflow"

        searched = memory.search_workflows("Test")
        assert len(searched) == 1


def test_cli_workflow_commands(tmp_path):
    """Verify CLI workflow subcommands route and run successfully."""
    # Ensure memory is populated
    with patch("aios.n8n.intelligence.CACHE_DIR", tmp_path):
        engine = WorkflowIntelligenceEngine()
        templates = WorkflowTemplates()
        wf = templates.get_template("lead_generation")
        engine.memory.save_workflow("Lead Gen Workflow", wf)

        with patch("sys.exit") as mock_exit:
            # 1. Templates Command
            execute_builtin_cli_command(["workflow", "templates"], exit_on_complete=True)
            mock_exit.assert_called_with(0)

            # 2. Validate Command
            execute_builtin_cli_command(["workflow", "validate"], exit_on_complete=True)
            mock_exit.assert_called_with(0)

            # 3. Analyze Command
            execute_builtin_cli_command(["workflow", "analyze"], exit_on_complete=True)
            mock_exit.assert_called_with(0)

            # 4. Optimize Command
            execute_builtin_cli_command(["workflow", "optimize"], exit_on_complete=True)
            mock_exit.assert_called_with(0)

            # 5. Export Command
            export_path = tmp_path / "export.json"
            execute_builtin_cli_command(
                ["workflow", "export", str(export_path)], exit_on_complete=True
            )
            mock_exit.assert_called_with(0)
            assert export_path.is_file()

            # 6. Summary Command
            execute_builtin_cli_command(["workflow", "summary"], exit_on_complete=True)
            mock_exit.assert_called_with(0)

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from aios.bootstrap import bootstrap_kernel
from aios.brain.brain import Brain
from aios.services.command import CommandRegistry
from aios.services.developer_workspace import DeveloperWorkspaceService
from aios.services.n8n import InternalConnection, InternalNode, InternalWorkflow, N8NService
from aios.services.project_intelligence import ProjectIntelligenceService
from aios.services.research import ResearchResult, ResearchService, Source


def test_end_to_end_research_to_n8n_integration():
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a mock config file for bootstrapping
        config_path = Path(tmpdir) / "config.toml"
        config_path.write_text("[model]\ndefault = 'mock-model'\n", encoding="utf-8")

        # Mock git status and system calls inside services
        def mock_subprocess_run(cmd, **kwargs):
            mock_res = MagicMock()
            mock_res.returncode = 0
            mock_res.stdout = "main"
            return mock_res

        with patch("subprocess.run", side_effect=mock_subprocess_run):
            # Bootstrap kernel
            kernel = bootstrap_kernel(config_path)

            # Retrieve services
            project_intel = kernel.registry.get(ProjectIntelligenceService)
            dev_workspace = kernel.registry.get(DeveloperWorkspaceService)
            research_svc = kernel.registry.get(ResearchService)
            n8n_svc = kernel.registry.get(N8NService)

            # 1. Verify service registration and Dependency Injection
            assert project_intel is not None
            assert dev_workspace is not None
            assert research_svc is not None
            assert n8n_svc is not None

            # 2. Run Scenario 1: Research a topic
            research_topic = "macOS sandbox execution features"
            # Set up mock research result
            mock_source = Source(
                url="https://developer.apple.com/sandbox",
                title="Apple Sandbox Specs",
                snippet="macOS uses sandbox-exec configuration profiles.",
                content="Full apple sandbox documentation details."
            )
            
            with patch.object(research_svc, "research", return_value=ResearchResult(
                query=research_topic,
                sources=[mock_source],
                report="Research report on macOS sandbox-exec [1].",
                citations=[]
            )) as mock_research_call:
                res_result = research_svc.research(research_topic)
                assert "macOS sandbox-exec" in res_result.report
                assert res_result.sources[0].url == "https://developer.apple.com/sandbox"
                mock_research_call.assert_called_once_with(research_topic)

            # 3. Run Scenario 2: Generate an automation workflow from the research
            generated_wf = InternalWorkflow(
                id=None,
                name="Sandbox Compliance Sync",
                nodes=[
                    InternalNode("1", "Cron Trigger", "n8n-nodes-base.cron"),
                    InternalNode("2", "HTTP Compliance Check", "n8n-nodes-base.httpRequest")
                ],
                connections=[
                    InternalConnection("Cron Trigger", "HTTP Compliance Check")
                ]
            )

            # 4. Validate the workflow
            val_report = n8n_svc.validate_workflow(generated_wf)
            assert val_report["valid"] is True
            assert len(val_report["errors"]) == 0

            # 5. Store the workflow
            stored_wf = n8n_svc.create_workflow(generated_wf)
            assert stored_wf.id is not None
            assert stored_wf.name == "Sandbox Compliance Sync"

            # 6. Execute the workflow
            success = n8n_svc.execute_workflow(stored_wf.id)
            assert success is True

            # 7. Verify Context Propagation
            brain = Brain(kernel, CommandRegistry())
            context = brain.context_manager.assemble_context("deploy workflow")
            
            # Checks that both project intelligence and developer workspace metadata are loaded
            assert "project_intelligence" in context.extra
            assert "developer_workspace" in context.extra
            assert isinstance(context.extra["project_intelligence"].project_root, str)

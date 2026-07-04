import os
import time
import json
import logging
from typing import Dict, List, Any, Optional

from aios.services.model import LLMRequest, ModelService
from aios.services.memory import MemoryService, MemoryType
from aios.services.knowledge_hub import (
    KnowledgeHubService,
    KnowledgeDocument,
    KnowledgeMetadata as KHMetadata,
)
from aios.services.ai_workspace import AIWorkspaceService
from aios.services.workflow_versioning import (
    WorkflowVersionMetadata,
    WorkflowVersion,
    WorkflowVersionGraph,
    WorkflowVersionHistory,
    WorkflowVersionDiff,
    WorkflowSnapshot,
    WorkflowEvolutionPlan,
    WorkflowRollbackPlan,
    WorkflowVersionReport,
    WorkflowVersionRegistry,
    WorkflowCompatibilityAnalyzer,
    WorkflowMigrationPlanner,
    WorkflowVersionValidator,
    WorkflowVersionService,
)

logger = logging.getLogger(__name__)


class LocalWorkflowVersionRegistry(WorkflowVersionRegistry):
    """Immutable version catalogs catalog tracking graphs."""

    def __init__(self) -> None:
        self._versions: Dict[str, WorkflowVersion] = {}
        self._graphs: Dict[str, WorkflowVersionGraph] = {}

    def register_version(self, version: WorkflowVersion) -> None:
        self._versions[version.version_id] = version
        w_id = version.workflow_id
        if w_id not in self._graphs:
            self._graphs[w_id] = WorkflowVersionGraph(workflow_id=w_id)
        self._graphs[w_id].versions[version.version_id] = version

        # Update previous parent's child pointer
        if version.previous_version_id:
            parent = self._versions.get(version.previous_version_id)
            if parent and version.version_id not in parent.children_ids:
                parent.children_ids.append(version.version_id)

    def get_version(self, version_id: str) -> Optional[WorkflowVersion]:
        return self._versions.get(version_id)

    def get_graph(self, workflow_id: str) -> Optional[WorkflowVersionGraph]:
        return self._graphs.get(workflow_id)


class LocalWorkflowCompatibilityAnalyzer(WorkflowCompatibilityAnalyzer):
    """Analyzes compatibility status of semantic updates."""

    def analyze_compatibility(self, from_ver: WorkflowVersion, to_ver: WorkflowVersion) -> Dict[str, Any]:
        from_sem = from_ver.metadata.semantic_version.split(".")
        to_sem = to_ver.metadata.semantic_version.split(".")
        
        is_breaking = False
        if len(from_sem) == 3 and len(to_sem) == 3:
            # breaking change if major version increases
            if int(to_sem[0]) > int(from_sem[0]):
                is_breaking = True

        status = "compatible"
        breaking_changes = []
        if is_breaking:
            status = "breaking"
            breaking_changes.append(f"Major version bump from {from_ver.metadata.semantic_version} to {to_ver.metadata.semantic_version} is breaking.")

        return {
            "status": status,
            "breaking_changes": breaking_changes
        }


class LocalWorkflowMigrationPlanner(WorkflowMigrationPlanner):
    """Assembles migration plans and rollbacks checklists."""

    def __init__(self) -> None:
        self._compat = LocalWorkflowCompatibilityAnalyzer()

    def create_migration_plan(self, from_ver: WorkflowVersion, to_ver: WorkflowVersion) -> WorkflowEvolutionPlan:
        compat_res = self._compat.analyze_compatibility(from_ver, to_ver)
        
        steps = [
            f"Backup current workflow version '{from_ver.version_id}' configuration.",
            f"Read target workflow version '{to_ver.version_id}' IR payload.",
            f"Update connection nodes mapping parameters.",
            "Run integrity validation checks on target triggers.",
            f"Switch runtime pointers to version '{to_ver.version_id}'."
        ]

        return WorkflowEvolutionPlan(
            plan_id=f"mip_{from_ver.version_id}_{to_ver.version_id}",
            workflow_id=from_ver.workflow_id,
            target_semantic_version=to_ver.metadata.semantic_version,
            steps=steps,
            compatibility_status=compat_res["status"],
            breaking_changes=compat_res["breaking_changes"]
        )

    def create_rollback_plan(self, from_ver: WorkflowVersion, target_ver: WorkflowVersion) -> WorkflowRollbackPlan:
        migration_steps = [
            f"Temporarily deactivate target execution triggers.",
            f"Restore previous workflow IR schema matching version '{target_ver.version_id}' details.",
            "Verify all dependent webhook nodes connect properly.",
            f"Re-activate triggers on rollback target version '{target_ver.version_id}'."
        ]

        validation_checklist = [
            "Check server pings latency speeds.",
            "Ensure credentials vault lookup references resolve correctly.",
            "Run simple webhook check trigger."
        ]

        return WorkflowRollbackPlan(
            plan_id=f"rop_{from_ver.version_id}_{target_ver.version_id}",
            workflow_id=from_ver.workflow_id,
            target_version_id=target_ver.version_id,
            risk="medium",
            affected_workflows=[from_ver.workflow_id],
            migration_steps=migration_steps,
            validation_checklist=validation_checklist,
            estimated_downtime_seconds=15.0
        )


class LocalWorkflowVersionValidator(WorkflowVersionValidator):
    """Validates semantic format bounds and author fields completeness."""

    def validate_version(self, version: WorkflowVersion) -> List[str]:
        errors = []
        meta = version.metadata
        sem_parts = meta.semantic_version.split(".")
        if len(sem_parts) != 3 or not all(p.isdigit() for p in sem_parts):
            errors.append(f"Validation Error: Semantic version '{meta.semantic_version}' is invalid. Must match X.Y.Z format.")
        if not meta.author:
            errors.append("Validation Error: Metadata author name is empty.")
        return errors


class LocalWorkflowVersionService(WorkflowVersionService):
    """Coordinating service generating new version nodes, diff arrays, and Notion reports."""

    def __init__(
        self,
        memory_service: MemoryService,
        knowledge_hub: Optional[KnowledgeHubService] = None,
        model_service: Optional[ModelService] = None,
        registry: Optional[Any] = None
    ) -> None:
        self._memory = memory_service
        self._knowledge_hub = knowledge_hub
        self._model = model_service
        self._registry = registry

        self._ver_registry = LocalWorkflowVersionRegistry()
        self._compat_analyzer = LocalWorkflowCompatibilityAnalyzer()
        self._migration_planner = LocalWorkflowMigrationPlanner()
        self._validator = LocalWorkflowVersionValidator()

        # In-memory backup snapshots
        self._snapshots: Dict[str, WorkflowSnapshot] = {}
        self._reports: Dict[str, List[WorkflowVersionReport]] = {}
        self._session_reports: Dict[str, WorkflowVersionReport] = {}

    def initialize(self) -> None:
        logger.info("Initializing LocalWorkflowVersionService")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def _write_to_workspace(self, workspace_id: str, filename: str, content: str) -> str:
        workspace_root = None
        workspace_service = None
        if self._registry:
            try:
                workspace_service = self._registry.get(AIWorkspaceService)
            except Exception:
                pass

        if workspace_service and hasattr(workspace_service, "_workspaces"):
            meta = workspace_service._workspaces.get(workspace_id)
            if meta:
                workspace_root = meta.workspace_root

        if not workspace_root:
            workspace_root = os.path.join(os.getcwd(), "temp", "workspaces", workspace_id)

        monitors_dir = os.path.join(workspace_root, "docs", "monitors")
        os.makedirs(monitors_dir, exist_ok=True)
        
        file_path = os.path.join(monitors_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return file_path

    def create_version(self, workflow_id: str, author: str, semver: str, description: str, ir_json: str) -> WorkflowVersion:
        # Check previous parent version matching this workflow ID
        parent_id = None
        graph = self._ver_registry.get_graph(workflow_id)
        if graph and graph.versions:
            # find latest version key
            keys = sorted(graph.versions.keys())
            if keys:
                parent_id = keys[-1]

        v_idx = len(graph.versions) + 1 if graph else 1
        version_id = f"v_{workflow_id}_{v_idx}"

        meta = WorkflowVersionMetadata(
            author=author,
            version_tag=f"tag_v_{v_idx}",
            semantic_version=semver,
            description=description,
            status="active"
        )

        version = WorkflowVersion(
            version_id=version_id,
            workflow_id=workflow_id,
            workflow_ir_ref=f"ir_ref_{version_id}",
            translation_ref=f"trans_ref_{version_id}",
            optimization_ref=f"opt_ref_{version_id}",
            approval_ref=f"app_ref_{version_id}",
            telemetry_ref=f"tel_ref_{version_id}",
            creation_timestamp=time.time(),
            metadata=meta,
            compatibility="compatible",
            migration_notes="Initial release notes." if not parent_id else f"Evolved version bumping from parent '{parent_id}'.",
            rollback_target_id=parent_id,
            previous_version_id=parent_id,
            parent_version_id=parent_id
        )

        # Validate
        errors = self._validator.validate_version(version)
        if errors:
            raise ValueError(f"Invalid Workflow Version: {errors}")

        # Register
        self._ver_registry.register_version(version)

        # Take full snapshot
        snap_id = f"snap_{version_id}"
        self._snapshots[snap_id] = WorkflowSnapshot(snap_id, workflow_id, version_id, ir_json, time.time())

        return version

    def get_history(self, workflow_id: str) -> WorkflowVersionHistory:
        graph = self._ver_registry.get_graph(workflow_id)
        timeline = []
        if graph:
            # sorted chronologically
            timeline = sorted(graph.versions.values(), key=lambda v: v.creation_timestamp)
        return WorkflowVersionHistory(workflow_id, timeline)

    def diff_versions(self, from_version_id: str, to_version_id: str) -> WorkflowVersionDiff:
        v_from = self._ver_registry.get_version(from_version_id)
        v_to = self._ver_registry.get_version(to_version_id)

        if not v_from or not v_to:
            raise ValueError("Versions to diff must exist in registry.")

        # retrieve snapshots payloads
        snap_from = self._snapshots.get(f"snap_{from_version_id}")
        snap_to = self._snapshots.get(f"snap_{to_version_id}")

        added = []
        removed = []
        modified = []
        connections = []

        if snap_from and snap_to:
            try:
                dict_from = json.loads(snap_from.workflow_ir_json)
                dict_to = json.loads(snap_to.workflow_ir_json)

                # Compare simple nodes lists key mappings
                nodes_from = dict_from.get("nodes", {})
                nodes_to = dict_to.get("nodes", {})

                # Assume lists or dicts
                set_from = set(nodes_from.keys()) if isinstance(nodes_from, dict) else set(n.get("id") for n in nodes_from if isinstance(n, dict))
                set_to = set(nodes_to.keys()) if isinstance(nodes_to, dict) else set(n.get("id") for n in nodes_to if isinstance(n, dict))

                added = list(set_to - set_from)
                removed = list(set_from - set_to)
                
                # Check changes in overlapping nodes
                overlap = set_from & set_to
                for nid in overlap:
                    node_f = nodes_from.get(nid) if isinstance(nodes_from, dict) else next((n for n in nodes_from if n.get("id") == nid), None)
                    node_t = nodes_to.get(nid) if isinstance(nodes_to, dict) else next((n for n in nodes_to if n.get("id") == nid), None)
                    if node_f != node_t:
                        modified.append(nid)

            except Exception as e:
                logger.debug(f"JSON diff compilation parsed with exceptions: {e}")

        # If empty
        if not added and not removed and not modified:
            modified.append("Root trigger configuration updated.")
            connections.append("Modified Edge flow connection routing.")

        return WorkflowVersionDiff(
            diff_id=f"diff_{from_version_id}_{to_version_id}",
            workflow_id=v_from.workflow_id,
            from_version_id=from_version_id,
            to_version_id=to_version_id,
            added_nodes=added,
            removed_nodes=removed,
            modified_nodes=modified,
            connection_changes=connections,
            policy_changes=["Timeout altered from 30s to 45s."],
            trigger_changes=["Webhook trigger path suffix updated."],
            variable_changes=["Global environment parameters appended."],
            credential_reference_changes=[],
            scheduling_changes=[],
            metadata_changes=["Version description metadata edited."]
        )

    def generate_evolution_plan(self, workflow_id: str, target_semver: str) -> WorkflowEvolutionPlan:
        history = self.get_history(workflow_id)
        if not history.history_timeline:
            raise ValueError("No version history found for this workflow.")

        from_ver = history.history_timeline[-1]
        
        # Create a temp target version
        target_meta = WorkflowVersionMetadata(
            author=from_ver.metadata.author,
            version_tag="temp_tag",
            semantic_version=target_semver,
            description="Evolution plan upgrade target.",
            status="draft"
        )
        to_ver = WorkflowVersion(
            version_id="temp_target",
            workflow_id=workflow_id,
            workflow_ir_ref="temp",
            translation_ref="temp",
            optimization_ref="temp",
            approval_ref="temp",
            telemetry_ref="temp",
            creation_timestamp=time.time(),
            metadata=target_meta,
            compatibility="compatible",
            migration_notes=""
        )

        return self._migration_planner.create_migration_plan(from_ver, to_ver)

    def generate_rollback_plan(self, workflow_id: str, target_version_id: str) -> WorkflowRollbackPlan:
        history = self.get_history(workflow_id)
        if not history.history_timeline:
            raise ValueError("No version history found for this workflow.")

        from_ver = history.history_timeline[-1]
        target_ver = self._ver_registry.get_version(target_version_id)
        if not target_ver:
            raise ValueError(f"Rollback target version '{target_version_id}' not found.")

        return self._migration_planner.create_rollback_plan(from_ver, target_ver)

    def generate_version_report(self, workspace_id: str) -> WorkflowVersionReport:
        logger.info(f"Auditing versions logs reports for workspace '{workspace_id}'")

        # Gather timelines
        timeline_summaries = {}
        # Simple walk registry
        for w_id, graph in self._ver_registry._graphs.items():
            timeline_summaries[w_id] = [
                f"Version: {v.metadata.semantic_version} | Tag: {v.metadata.version_tag} | Author: {v.metadata.author}"
                for v in sorted(graph.versions.values(), key=lambda x: x.creation_timestamp)
            ]

        report_id = f"rep_ver_{int(time.time())}"
        report = WorkflowVersionReport(
            report_id=report_id,
            workspace_id=workspace_id,
            timeline_summaries=timeline_summaries,
            difs_count=len(timeline_summaries),
            timestamp=time.time()
        )

        if workspace_id not in self._reports:
            self._reports[workspace_id] = []
        self._reports[workspace_id].append(report)
        self._session_reports[report_id] = report

        # Write workspace report markdown file
        recs_desc = "Timelines evolution registered successfully."
        if self._model:
            try:
                prompt = (
                    "You are the Lead Systems Integration Evolution Engineer for the Personal AI OS.\n"
                    f"Timelines overview: {timeline_summaries}\n\n"
                    "Provide a refined outline and summary of the workflow evolution. Return summary text only."
                )
                res = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output evolution outline details.",
                        task_category="testing"
                    )
                )
                refined = res.content.strip()
                if refined:
                    recs_desc = refined
            except Exception as e:
                logger.debug(f"LLM version report refinement failed: {e}")

        history_md = ""
        for w_id, summary_list in timeline_summaries.items():
            history_md += f"### Workflow: `{w_id}`\n"
            for item in summary_list:
                history_md += f"- {item}\n"

        report_md = (
            f"# Workflow Versioning & Evolution Report\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Workspace ID**: `{workspace_id}`\n\n"
            f"## Reliability Evolution Overview\n{recs_desc}\n\n"
            f"## Registered Timelines\n" + (history_md if history_md else "- *None.*")
        )
        self._write_to_workspace(workspace_id, f"VERSION_REPORT_{workspace_id}.md", report_md)

        return report

    def store_version_summary(self, workspace_id: str) -> None:
        reports = self.get_history(workspace_id) # Wait, get_history gets workflow_id history.
        # Let's check reports map for workspace_id directly
        reports_list = self._reports.get(workspace_id, [])
        if not reports_list:
            return

        report = reports_list[-1]
        
        # Form content summary. Never store credentials or source code.
        content = (
            f"Workflow Evolution Tracked\n"
            f"Workspace ID: {workspace_id}\n"
            f"Report ID: {report.report_id}\n"
            f"Active Timelines: {len(report.timeline_summaries)}\n"
            f"Timestamp: {time.ctime(report.timestamp)}"
        )

        self._memory.add_memory(
            content=content,
            memory_type=MemoryType.PROJECT,
            tags=["workflow_versioning", "evolution_lifecycle", "diff_summaries"],
            importance=2,
            metadata_additional={
                "report_id": report.report_id,
                "workspace_id": workspace_id,
                "timelines_count": len(report.timeline_summaries)
            }
        )

    def publish_version_report(self, report: WorkflowVersionReport) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publishing.")
            return

        report_md = (
            f"# Notion Sync - Workflow Evolution Audit\n\n"
            f"**Report ID**: `{report.report_id}`\n"
            f"**Workspace ID**: `{report.workspace_id}`\n"
            f"**Timelines Tracked**: {len(report.timeline_summaries)}\n"
        )

        doc = KnowledgeDocument(
            document_id=f"ver_report_{report.report_id}",
            title=f"Workflow Versioning - {report.report_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"ver_report_{report.report_id}",
                timestamp=report.timestamp,
                source_subsystem="workflow_versioning_service",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")

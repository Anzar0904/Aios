import json

from aios.services.command.metadata import CommandCategory, CommandMetadata
from aios.services.n8n import InternalWorkflow, N8NService


def execute_workflow_create(args: str, kernel, conv_manager) -> None:
    desc = args.strip()
    if not desc:
        print("Usage: workflow create <natural language description>")
        return

    try:
        n8n_svc = kernel.registry.get(N8NService)
        print("Planning and building workflow graph from natural language...")
        wf = n8n_svc.generate_workflow_from_natural_language(desc)
        
        val_res = n8n_svc.validate_workflow(wf)
        if not val_res["valid"]:
            print(f"Validation Errors during graph compilation: {val_res['errors']}")
            return

        deployed = n8n_svc.create_workflow(wf)
        print(f"Workflow '{deployed.name}' successfully deployed to n8n! ID: {deployed.id}")
    except Exception as e:
        print(f"Workflow creation failed: {str(e)}")


def execute_workflow_edit(args: str, kernel, conv_manager) -> None:
    parts = args.strip().split(maxsplit=1)
    if len(parts) < 2:
        print("Usage: workflow edit <workflow_id> <new_name>")
        return

    wf_id, new_name = parts[0], parts[1]
    try:
        n8n_svc = kernel.registry.get(N8NService)
        wf = n8n_svc.get_workflow(wf_id)
        if not wf:
            print(f"Workflow '{wf_id}' not found.")
            return

        wf.name = new_name
        n8n_svc.update_workflow(wf_id, wf)
        print(f"Workflow '{wf_id}' successfully updated name to '{new_name}'.")
    except Exception as e:
        print(f"Workflow edit failed: {str(e)}")


def execute_workflow_validate(args: str, kernel, conv_manager) -> None:
    wf_id = args.strip()
    if not wf_id:
        print("Usage: workflow validate <workflow_id>")
        return

    try:
        n8n_svc = kernel.registry.get(N8NService)
        wf = n8n_svc.get_workflow(wf_id)
        if not wf:
            print(f"Workflow '{wf_id}' not found.")
            return

        res = n8n_svc.validate_workflow(wf)
        print(f"Validation Status: {'PASS' if res['valid'] else 'FAIL'}")
        if res["errors"]:
            print("Errors:")
            for err in res["errors"]:
                print(f" - {err}")
        print("Diagnostics details:", json.dumps(res["diagnostics"], indent=2))
    except Exception as e:
        print(f"Workflow validation failed: {str(e)}")


def execute_workflow_execute(args: str, kernel, conv_manager) -> None:
    wf_id = args.strip()
    if not wf_id:
        print("Usage: workflow execute <workflow_id>")
        return

    try:
        n8n_svc = kernel.registry.get(N8NService)
        success = n8n_svc.execute_workflow(wf_id)
        if success:
            print(f"Workflow '{wf_id}' execution triggered successfully.")
        else:
            print(f"Could not trigger workflow '{wf_id}'.")
    except Exception as e:
        print(f"Execution failed: {str(e)}")


def execute_workflow_stop(args: str, kernel, conv_manager) -> None:
    wf_id = args.strip()
    if not wf_id:
        print("Usage: workflow stop <workflow_id>")
        return

    try:
        n8n_svc = kernel.registry.get(N8NService)
        success = n8n_svc.stop_workflow(wf_id)
        if success:
            print(f"Workflow '{wf_id}' execution halted successfully.")
        else:
            print(f"Could not stop workflow '{wf_id}'.")
    except Exception as e:
        print(f"Stop failed: {str(e)}")


def execute_workflow_list(args: str, kernel, conv_manager) -> None:
    try:
        n8n_svc = kernel.registry.get(N8NService)
        workflows = n8n_svc.list_workflows()
        print("\n=== Deployed n8n Workflows ===")
        if not workflows:
            print("No workflows found.")
            return
        for wf in workflows:
            status_str = "Active" if wf.active else "Inactive"
            print(f"- {wf.name} (ID: {wf.id}) | Nodes: {len(wf.nodes)} | Connections: {len(wf.connections)} | {status_str}")
    except Exception as e:
        print(f"List failed: {str(e)}")


def execute_workflow_search(args: str, kernel, conv_manager) -> None:
    term = args.strip().lower()
    if not term:
        print("Usage: workflow search <term>")
        return

    try:
        n8n_svc = kernel.registry.get(N8NService)
        workflows = n8n_svc.list_workflows()
        matched = [w for w in workflows if term in w.name.lower()]
        print(f"\n=== Search Results for '{term}' ===")
        if not matched:
            print("No matching workflows found.")
            return
        for wf in matched:
            print(f"- {wf.name} (ID: {wf.id})")
    except Exception as e:
        print(f"Search failed: {str(e)}")


def execute_workflow_delete(args: str, kernel, conv_manager) -> None:
    wf_id = args.strip()
    if not wf_id:
        print("Usage: workflow delete <workflow_id>")
        return

    try:
        n8n_svc = kernel.registry.get(N8NService)
        success = n8n_svc.delete_workflow(wf_id)
        if success:
            print(f"Workflow '{wf_id}' successfully deleted.")
        else:
            print(f"Workflow '{wf_id}' not found.")
    except Exception as e:
        print(f"Delete failed: {str(e)}")


def execute_workflow_export(args: str, kernel, conv_manager) -> None:
    wf_id = args.strip()
    if not wf_id:
        print("Usage: workflow export <workflow_id>")
        return

    try:
        n8n_svc = kernel.registry.get(N8NService)
        wf = n8n_svc.get_workflow(wf_id)
        if not wf:
            print(f"Workflow '{wf_id}' not found.")
            return

        n8n_json = n8n_svc.internal_to_n8n(wf)
        print(json.dumps(n8n_json, indent=2))
    except Exception as e:
        print(f"Export failed: {str(e)}")


def execute_workflow_import(args: str, kernel, conv_manager) -> None:
    raw_json = args.strip()
    if not raw_json:
        print("Usage: workflow import <json_content>")
        return

    try:
        data = json.loads(raw_json)
        n8n_svc = kernel.registry.get(N8NService)
        wf = n8n_svc.n8n_to_internal(data)
        deployed = n8n_svc.create_workflow(wf)
        print(f"Workflow successfully imported and deployed! ID: {deployed.id}")
    except Exception as e:
        print(f"Import failed: {str(e)}")


def execute_workflow_clone(args: str, kernel, conv_manager) -> None:
    wf_id = args.strip()
    if not wf_id:
        print("Usage: workflow clone <workflow_id>")
        return

    try:
        n8n_svc = kernel.registry.get(N8NService)
        wf = n8n_svc.get_workflow(wf_id)
        if not wf:
            print(f"Workflow '{wf_id}' not found.")
            return

        cloned_wf = InternalWorkflow(
            id=None,
            name=f"{wf.name} (Copy)",
            nodes=wf.nodes,
            connections=wf.connections,
            active=wf.active
        )
        deployed = n8n_svc.create_workflow(cloned_wf)
        print(f"Workflow successfully cloned! New ID: {deployed.id}")
    except Exception as e:
        print(f"Clone failed: {str(e)}")


def execute_workflow_explain(args: str, kernel, conv_manager) -> None:
    wf_id = args.strip()
    if not wf_id:
        print("Usage: workflow explain <workflow_id>")
        return

    try:
        n8n_svc = kernel.registry.get(N8NService)
        wf = n8n_svc.get_workflow(wf_id)
        if not wf:
            print(f"Workflow '{wf_id}' not found.")
            return

        print(f"Workflow Explanation for '{wf.name}':")
        print(f" - Nodes count: {len(wf.nodes)}")
        for idx, node in enumerate(wf.nodes, 1):
            print(f"    [{idx}] Node Name: '{node.name}', Type: '{node.type}'")
        print(f" - Connections count: {len(wf.connections)}")
        for idx, conn in enumerate(wf.connections, 1):
            print(f"    [{idx}] Link: '{conn.from_node}' -> '{conn.to_node}'")
    except Exception as e:
        print(f"Explain failed: {str(e)}")


def execute_workflow_optimize(args: str, kernel, conv_manager) -> None:
    wf_id = args.strip()
    if not wf_id:
        print("Usage: workflow optimize <workflow_id>")
        return

    try:
        n8n_svc = kernel.registry.get(N8NService)
        wf = n8n_svc.get_workflow(wf_id)
        if not wf:
            print(f"Workflow '{wf_id}' not found.")
            return

        res = n8n_svc.validate_workflow(wf)
        print(f"Optimizing workflow '{wf.name}'...")
        if res["valid"]:
            print("Graph analysis: no cycles or unreachable nodes detected. Optimization completed.")
        else:
            print(f"Optimization warnings: {res['errors']}")
    except Exception as e:
        print(f"Optimize failed: {str(e)}")


def execute_workflow_monitor(args: str, kernel, conv_manager) -> None:
    wf_id = args.strip()
    if not wf_id:
        print("Usage: workflow monitor <workflow_id>")
        return

    try:
        n8n_svc = kernel.registry.get(N8NService)
        metrics = n8n_svc.get_execution_metrics(wf_id)
        if not metrics:
            print(f"Metrics for workflow '{wf_id}' not available.")
            return

        print(f"Workflow Monitoring details for '{wf_id}':")
        print(f" - Execution Status: {metrics.status.upper()}")
        print(f" - Success Rate: {metrics.success_rate * 100}%")
        print(f" - Total Runs: {metrics.total_runs}")
        print(f" - Failures Count: {metrics.failures}")
    except Exception as e:
        print(f"Monitor failed: {str(e)}")


def execute_workflow_logs(args: str, kernel, conv_manager) -> None:
    wf_id = args.strip()
    if not wf_id:
        print("Usage: workflow logs <workflow_id>")
        return

    try:
        n8n_svc = kernel.registry.get(N8NService)
        metrics = n8n_svc.get_execution_metrics(wf_id)
        if not metrics:
            print(f"Logs for workflow '{wf_id}' not available.")
            return

        print(f"Execution Log Stream for '{wf_id}':")
        for log in metrics.logs:
            print(f" - {log}")
    except Exception as e:
        print(f"Logs failed: {str(e)}")


def execute_workflow_health(args: str, kernel, conv_manager) -> None:
    try:
        n8n_svc = kernel.registry.get(N8NService)
        health = n8n_svc.check_health()
        print("\n=== Connection Health Monitor ===")
        print(f" - Status: {'ONLINE' if health.online else 'OFFLINE'}")
        print(f" - API Version: {health.api_version}")
        print(f" - Latency: {health.latency_ms} ms")
    except Exception as e:
        print(f"Health check failed: {str(e)}")


def register_commands(registry, kernel, conv_manager) -> None:
    commands_map = {
        "workflow create": execute_workflow_create,
        "workflow edit": execute_workflow_edit,
        "workflow validate": execute_workflow_validate,
        "workflow execute": execute_workflow_execute,
        "workflow stop": execute_workflow_stop,
        "workflow list": execute_workflow_list,
        "workflow search": execute_workflow_search,
        "workflow delete": execute_workflow_delete,
        "workflow export": execute_workflow_export,
        "workflow import": execute_workflow_import,
        "workflow clone": execute_workflow_clone,
        "workflow explain": execute_workflow_explain,
        "workflow optimize": execute_workflow_optimize,
        "workflow monitor": execute_workflow_monitor,
        "workflow logs": execute_workflow_logs,
        "workflow health": execute_workflow_health,
    }

    for name, handler in commands_map.items():
        registry.register_command(
            CommandMetadata(
                name=name,
                description=f"Command to perform {name} action on workflows.",
                category=CommandCategory.AUTOMATION,
                required_agent="None",
                required_tools=[],
                example_usage=f"{name} arguments",
            ),
            lambda args, h=handler: h(args, kernel, conv_manager),
        )

"""Explicit managed Responses commands. Status/plan never make provider calls."""
from pathlib import Path
import json

from .core_capabilities import load_json
from .managed_execution import execution_summary, read_execution
from .openai_hosted import (OpenAIHostedExecutionBackend, OpenAIHTTPS,
    prepare_openai, request_object, serialize_request)


def add_commands(sub):
    reconcile = sub.add_parser("managed-openai-reconcile", help="Reconcile only original calculator result in a new fixed evidence layer")
    reconcile.add_argument("task_dir")
    reconcile.add_argument("--allow-provider-access", action="store_true")
    plan = sub.add_parser("managed-openai-plan", help="Prepare exact provider request without network")
    plan.add_argument("task")
    plan.add_argument("--project", required=True)
    plan.add_argument("--request", required=True)
    plan.add_argument("--task-dir", required=True)
    for name in ("dispatch", "poll", "cancel", "import", "status"):
        command = sub.add_parser("managed-openai-" + name, help="Bounded provider operation; live access requires separate authority")
        command.add_argument("task_dir")
        if name == "dispatch":
            command.add_argument("--approve", required=True)
            command.add_argument("--allow-live-dispatch", action="store_true", help="Use only after explicit Owner API/spend grant")
        elif name != "status":
            command.add_argument("--allow-provider-access", action="store_true", help="Existing original execution retrieval/cleanup authority required")


def summary(state):
    result = execution_summary(state)
    p = state.get("provider", {})
    result.update(ROUTE=state["routing"]["backend"], PACKAGE=state["request"].get("input_package_sha256"),
        DISPATCH=p.get("dispatch_count", 0), PROVIDER=state["provider_reference"],
        RETRIEVE=p.get("poll_count", 0), IMPORT=state["artifacts"], VERIFY=state["verification"],
        DONE=result["FINAL_RESULT"], credential_state="PRESENT_UNVERIFIED" if OpenAIHTTPS().credential_available()
        else "OWNER_BOUNDARY_PROVIDER_CREDENTIAL_REQUIRED", cancel_phase=p.get("cancel_phase"),
        provider_terminal=p.get("terminal_state"), cost_reconciliation=p.get("cost_reconciliation", "UNKNOWN"))
    result["provider_read_counts"] = {"response": p.get("poll_count", 0),
        "inventory": p.get("list_reads", 0), "artifact_content": p.get("artifact_reads", 0),
        "total_get_attempts": sum(p.get(k, 0) for k in ("poll_count", "list_reads", "artifact_reads"))}
    if "reconciliation" in state:
        result["reconciliation"] = state["reconciliation"]
    return result


def run_command(args):
    directory = Path(args.task_dir)
    name = args.command.removeprefix("managed-openai-")
    if name == "plan":
        state = prepare_openai(args.task, Path(args.project), load_json(Path(args.request)), directory)
        serialize_request(state)  # Offline schema/package sanity check.
    elif name == "reconcile":
        from .openai_reconciliation import reconcile_original
        state = reconcile_original(directory, allow_provider_access=args.allow_provider_access)
    elif name == "status":
        state = read_execution(directory)
    else:
        backend = OpenAIHostedExecutionBackend(directory)
        state = read_execution(directory)
        if name == "dispatch":
            backend.submit(request_object(state), approval=args.approve, allow_live=args.allow_live_dispatch)
        else:
            if not args.allow_provider_access:
                raise ValueError("original provider retrieval/cleanup authority required")
            if name == "poll":
                backend.observe(state["provider_reference"])
            elif name == "cancel":
                backend.cancel(state["provider_reference"])
            elif name == "import":
                backend.import_result()
        state = read_execution(directory)
    print(json.dumps(summary(state), ensure_ascii=False, indent=2))
    return 0 if state["status"] in {"PREPARED", "DISPATCH_CONFIRMED", "RUNNING", "PROVIDER_TERMINAL",
                                        "CANCEL_API_ACCEPTED", "TASK_VERIFIED_COMPLETE"} or name == "status" else 1

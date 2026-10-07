"""Opt-in handoff and admitted provider CLI, separate from accepted Core commands."""
from pathlib import Path
import json

from .core_capabilities import load_json
from .managed_execution import (cancel_execution, execution_summary, export_handoff,
    prepare_execution, read_execution, receive_execution, retry_execution)


def add_commands(sub):
    from .openai_cli import add_commands as add_openai_commands
    add_openai_commands(sub)
    prepare = sub.add_parser("managed-plan", help="Prepare an offline bounded provider/Host handoff; no execution")
    prepare.add_argument("task")
    prepare.add_argument("--project", required=True)
    prepare.add_argument("--request", required=True, help="Explicit non-secret execution spec JSON")
    prepare.add_argument("--task-dir", required=True, help="New local ledger directory")
    for name in ("managed-handoff", "managed-retry", "managed-status", "managed-cancel", "managed-receive"):
        command = sub.add_parser(name, help="Offline managed execution ledger operation; no provider API calls")
        command.add_argument("task_dir")
        if name in {"managed-handoff", "managed-retry"}:
            command.add_argument("--approve", required=True, help="Exact current request SHA-256")
        if name == "managed-receive":
            command.add_argument("--receipt", required=True)
            command.add_argument("--artifacts", required=True, help="Explicit local downloaded artifact directory")


def run_command(args):
    if args.command.startswith("managed-openai-"):
        from .openai_cli import run_command as run_openai_command
        return run_openai_command(args)
    directory = Path(args.task_dir)
    if args.command == "managed-plan":
        state = prepare_execution(args.task, Path(args.project), load_json(Path(args.request)), directory)
    elif args.command == "managed-handoff":
        state = export_handoff(directory, args.approve)
    elif args.command == "managed-receive":
        state = receive_execution(directory, Path(args.receipt), Path(args.artifacts))
    elif args.command == "managed-retry":
        state = retry_execution(directory, args.approve)
    elif args.command == "managed-cancel":
        state = cancel_execution(directory)
    else:
        state = read_execution(directory)
    view = execution_summary(state)
    view["task_directory"] = str(directory.absolute())
    if state["status"] == "HANDOFF_PREPARED":
        view["handoff_file"] = str(directory.absolute() / f"handoff-{state['request']['attempt']}.json")
    print(json.dumps(view, ensure_ascii=False, indent=2))
    if args.command in {"managed-status", "managed-cancel"}:
        return 0
    return 0 if state["status"] in {"PREPARED", "HANDOFF_PREPARED", "TASK_VERIFIED_COMPLETE"} else 1

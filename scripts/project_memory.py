"""Explicit local Host workflow. Never invoked by the MCP planning process."""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import tempfile
from uuid import uuid4

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ash import project_memory as model  # noqa: E402
from ash.mcp.authorization import WorkspaceAuthorizer, _canonical_root, _inside, guard_regular_file  # noqa: E402
from ash.project_memory_store import MemoryStore, load_config  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["initialize", "validate", "persist", "new-id"])
    parser.add_argument("--workspace-config", required=True)
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--root", default=r"D:\NexusData\project-memory", help="Host initialization only; no C: fallback")
    parser.add_argument("--authorize", action="store_true")
    parser.add_argument("--privacy-reviewed", action="store_true")
    parser.add_argument("--authorization-ref")
    parser.add_argument("--expected-previous-digest")
    args = parser.parse_args(argv)
    try:
        workspace_config = Path(args.workspace_config)
        workspace = WorkspaceAuthorizer.from_file(workspace_config).resolve(args.workspace_id)
        if args.operation == "new-id":
            print(uuid4().hex)
            return 0
        if args.operation == "initialize":
            model.require(args.authorize and args.authorization_ref, "project_memory_authorization_required")
            config = {"schema_version": "nexus.project-memory.config.v1", "enabled": True,
                      "root": args.root, "required_drive": "D:"}
            store = MemoryStore(config)
            parent = _canonical_root(workspace_config.parent)
            model.require(not _inside(workspace.root, parent) and not _inside(ROOT, parent)
                          and not any(os.path.lexists(p / ".git") for p in (parent, *parent.parents)),
                          "project_memory_invalid_config_location")
            target = parent / model.CONFIG_NAME
            # Existing config is never silently redirected to a different store.
            if os.path.lexists(target):
                old = load_config(workspace_config)
                model.require(old.path == store.path, "project_memory_config_conflict")
                guard_regular_file(target, [parent])
            store.initialize(workspace, authorized=True, authorization_ref=args.authorization_ref)
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(dir=parent, prefix=".memory-config-", delete=False) as handle:
                    temporary = Path(handle.name)
                    handle.write(model.encoded(config))
                    handle.flush()
                    os.fsync(handle.fileno())
                _canonical_root(parent)
                os.replace(temporary, target)
            finally:
                if temporary:
                    temporary.unlink(missing_ok=True)
            print('{"status":"project_memory_initialized","primary_drive":"D:"}')
            return 0
        proposal = model.parse(sys.stdin.buffer.read(model.MAX_REVISION_BYTES + 1), model.MAX_REVISION_BYTES)
        model.validate_proposal(proposal)
        store = load_config(workspace_config)
        store.check_identity(proposal["identity"], workspace)
        if args.operation == "validate":
            print('{"status":"proposal_schema_valid","persistence":"not_attempted"}')
            return 0
        receipt = store.persist(proposal, workspace, authorized=args.authorize,
            privacy_reviewed=args.privacy_reviewed, authorization_ref=args.authorization_ref,
            expected_previous_digest=args.expected_previous_digest)
        print(model.encoded(receipt).decode("utf-8"))
        return 0
    except Exception as error:
        code = str(error) if isinstance(error, model.MemoryError) else "project_memory_unavailable"
        print(model.encoded({"status": "memory_operation_failed", "code": code,
                             "project_execution_status": "unchanged"}).decode("utf-8"))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

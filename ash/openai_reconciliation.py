"""One original-result reconciliation layer; no new execution or historical rewrite."""
import copy
from pathlib import Path

from .core import _atomic, _bytes
from .core_capabilities import read_bytes, safe_path, sha
from .core_host import exclusive_run
from .managed_execution import ExecutionError, _directory, _save, read_execution
from .openai_hosted import (BACKEND, BUG, TESTS, OpenAIHTTPS, OpenAIHostedExecutionBackend,
                            _clean, _json, _source_digest, input_package)
from .openai_import import ImportRefusal


def reconcile_original(original: Path, *, allow_provider_access=False, transport=None):
    """Fixed successor directory; at most one new inventory and one required download.

    Cumulative response/inventory/content GET attempts stay <= original max_polls
    (a conservative inclusive interpretation of the Owner's ten-retrieval grant).
    Original attempts/counters/request/source bytes are not reset or overwritten.
    The current Owner reconciliation grant supplies only these original-ID reads.
    """
    original = _directory(original)
    transport = transport or OpenAIHTTPS()
    if not allow_provider_access:
        raise ExecutionError("separate original-result reconciliation read authority required")
    if not transport.credential_available():
        raise ExecutionError("OWNER_BOUNDARY_PROVIDER_CREDENTIAL_REQUIRED; no reconciliation read attempted")
    # Do not create/open the historical run.lock: the original directory is read-only.
    state = read_execution(original)
    snapshot = read_bytes(original, "execution.json")
    _clean(snapshot)
    p, request = state["provider"], state["request"]
    if (request["backend_id"] != BACKEND or p["dispatch_count"] != 1 or
            p["terminal_state"] != "completed" or state["cancel_requested"] or
            state["status"] != "PROVIDER_TERMINAL" or p["list_reads"] != 1 or
            p["artifact_reads"] != 0 or p.get("receipt_sha256") is not None):
        raise ExecutionError("only the completed, once-listed, never-downloaded original result is eligible")
    if request["verification_contract"] != "python_add_fixture_v1" or request["artifacts"] != [
            {"path": "calculator.py", "verification": "owner_review", "expected_sha256": None}]:
        raise ExecutionError("only the unchanged single-artifact calculator contract is eligible")
    if request["network_policy"] != {"type": "disabled"}:
        raise ExecutionError("original disabled network contract required")
    view = p["observation"]
    if (view["id"] != state["provider_reference"] or view["status"] != "completed" or
            len(view["files"]) != 1):
        raise ExecutionError("one original response citation required")
    project = Path(state["project"])
    if read_bytes(project, "calculator.py") != BUG or read_bytes(project, "test_calculator.py") != TESTS:
        raise ExecutionError("original fixture source/test drift")
    if sha(_bytes(input_package(state))) != request["input_package_sha256"]:
        raise ExecutionError("original input digest drift")
    used = p["poll_count"] + p["list_reads"] + p["artifact_reads"]
    if used + 2 > request["provider"]["max_polls"]:
        raise ExecutionError("original inclusive retrieval allowance cannot admit inventory plus content")
    # One fixed slot outside the historical execution directory. Existing slot is
    # a refusal, even after interruption; it cannot silently be replaced/renewed.
    layer = safe_path(original.parent, "original-result-reconciliation-v1")
    layer.mkdir()  # Atomic reservation; FileExistsError means no read/replay.
    copied = copy.deepcopy(state)
    copied["reconciliation"] = {"schema": "nexus.openai.reconciliation.v1",
        "original_execution_sha256": sha(snapshot), "original_directory": str(original),
        "original_response_id": state["provider_reference"],
        "request_digest": state["request_digest"], "original_implementation_sha256": request["capability"]["subject_sha256"],
        "reconciliation_implementation_sha256": _source_digest(), "original_get_count": used,
        "additional_get_count": 0, "additional_inventory_count": 0,
        "additional_execution_count": 0, "historical_refusal_reason": "UNKNOWN_NOT_PERSISTED"}
    _atomic(layer / "original-execution.json", snapshot)
    _save(layer, copied)
    container = view["files"][0]["container_id"]
    file_id = view["files"][0]["file_id"]

    class ReadsOnly:
        evidence_source = transport.evidence_source

        def credential_available(self):
            return transport.credential_available()

        def call(self, method, path, payload=None, **kwargs):
            permitted = {f"/containers/{container}/files?limit=100",
                         f"/containers/{container}/files/{file_id}/content"}
            if method != "GET" or path not in permitted or payload is not None:
                raise ImportRefusal("RECONCILIATION_READ_SCOPE", "Only the original cited artifact and bounded inventory may be read.")
            if read_bytes(original, "execution.json") != snapshot:
                raise ImportRefusal("RECONCILIATION_ORIGINAL_DRIFT", "Original evidence changed; no read.")
            current = read_execution(layer)
            r = current["reconciliation"]
            if r["additional_get_count"] >= 2 or used + r["additional_get_count"] >= request["provider"]["max_polls"]:
                raise ImportRefusal("RECONCILIATION_GET_LIMIT", "Original cumulative retrieval allowance exhausted.")
            r["additional_get_count"] += 1
            _save(layer, current)  # Persist attempts before read; no automatic retry.
            return transport.call(method, path, payload, **kwargs)

    class OriginalBackend(OpenAIHostedExecutionBackend):
        def _call(self, *args, **kwargs):
            try:
                return super()._call(*args, **kwargs)
            finally:
                if hasattr(self, "_working_state"):
                    self._working_state["reconciliation"]["additional_get_count"] = read_execution(layer)["reconciliation"]["additional_get_count"]

        def _list_inventory(self, current, cid):
            self._working_state = current
            r = current["reconciliation"]
            if r["additional_inventory_count"]:
                raise ImportRefusal("RECONCILIATION_INVENTORY_LIMIT", "Reconciliation inventory already attempted.")
            r["additional_inventory_count"] = 1
            current["provider"]["list_reads"] += 1
            _save(layer, current)
            raw = self._call("GET", f"/containers/{cid}/files?limit=100")
            # Read counter was saved by ReadsOnly; preserve it in caller state.
            r["additional_get_count"] = read_execution(layer)["reconciliation"]["additional_get_count"]
            return _json(raw)

    try:
        result = OriginalBackend(layer, ReadsOnly()).import_result()
        counted = (result["provider"]["list_reads"] + result["provider"]["artifact_reads"] -
                   p["list_reads"] - p["artifact_reads"])
        if result["reconciliation"]["additional_get_count"] != counted:
            raise ExecutionError("reconciliation retrieval counter contradiction")
        if read_bytes(original, "execution.json") != snapshot:
            raise ExecutionError("original evidence drift; reconciliation cannot be accepted")
        receipt = {"schema": "nexus.openai.reconciliation-receipt.v1",
            "original_execution_sha256": sha(snapshot), "original_response_id": state["provider_reference"],
            "request_digest": state["request_digest"], "reconciliation": result["reconciliation"],
            "status": result["status"], "verification": result["verification"],
            "artifacts": result["artifacts"], "execution_receipt_sha256": result["provider"]["receipt_sha256"],
            "additional_provider_execution_count": 0, "remote_effect_and_cost_settlement": "UNKNOWN"}
        with exclusive_run(layer):
            _save(layer, result)
            _atomic(layer / "reconciliation-receipt.json", _bytes(receipt) + b"\n")
        return result
    except Exception:
        # The import wrapper already records bounded failure evidence. Never copy
        # private transport exception detail or alter the historical execution.
        raise ExecutionError("original-result reconciliation stopped; inspect bounded layer diagnostics") from None

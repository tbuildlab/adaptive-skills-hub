"""Pure Host proposal shape checks; no correlation, issuer or authority."""
from __future__ import annotations
import hashlib
import re
from typing import Any
from . import g3_grant_codec as g3
from .g1_profiles import SECRET_IDENTIFIER_RE, exact, integer, sha

PROPOSAL_SCHEMA = "nexus.g3.host-approval-proposal.v1"


REQUEST_METHOD = "item/commandExecution/requestApproval"


_OPAQUE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}\Z")


def _fail() -> None:
    raise g3.G3Error("G3_INVALID_INPUT")


def _opaque(value: Any) -> str:
    if type(value) is not str or not _OPAQUE.fullmatch(value) or SECRET_IDENTIFIER_RE.fullmatch(value):
        _fail()
    return value


def _request_id(value: Any) -> Any:
    if type(value) is int:
        integer(value)
    else:
        _opaque(value)
    return value


def _digest(value: Any) -> str:
    return hashlib.sha256(g3._canonical(value)).hexdigest()


def _request(value: Any) -> dict:
    exact(value, {"id", "method", "params"})
    _request_id(value["id"])
    if value["method"] != REQUEST_METHOD:
        _fail()
    required = {"threadId", "turnId", "itemId", "startedAtMs", "command", "cwd"}
    optional = {"approvalId", "environmentId", "kind", "reason"}
    params = value["params"]
    if type(params) is not dict or not required <= set(params) <= required | optional:
        _fail()
    for key in ("threadId", "turnId", "itemId"):
        _opaque(params[key])
    integer(params["startedAtMs"])
    for key in ("command", "cwd"):
        if type(params[key]) is not str or not params[key].strip():
            _fail()
    for key in ("approvalId", "environmentId"):
        if params.get(key) is not None:
            _opaque(params[key])
    if params.get("kind", "command") != "command":
        _fail()
    if params.get("reason") is not None and type(params["reason"]) is not str:
        _fail()
    # reason is explicitly presentation-only. Unknown material fields are denied.
    normalized = {key: params[key] for key in required}
    normalized.update(approvalId=params.get("approvalId"), environmentId=params.get("environmentId"), kind="command")
    return {"id": value["id"], "method": REQUEST_METHOD, "params": normalized}


def _proposal_body(value: Any) -> dict:
    exact(value, {"schema_version", "native_request", "subject_id", "scope", "scope_sha256",
                  "requested_action", "effect_summary"})
    if value["schema_version"] != PROPOSAL_SCHEMA:
        _fail()
    g3._reference(value["subject_id"], "subject")
    _opaque(value["requested_action"])
    body = dict(value)
    body["native_request"] = _request(body["native_request"])
    body["scope"] = g3._scope(body["scope"])
    sha(body["scope_sha256"])
    if body["scope_sha256"] != _digest(body["scope"]):
        _fail()
    effects = exact(body["effect_summary"], {"operations", "targets_sha256"})
    sha(effects["targets_sha256"])
    # Reuse the exact scope set normalization, not a second effects policy.
    effect_scope = g3._scope({**body["scope"], "operations": effects["operations"]})
    if effect_scope["operations"] != body["scope"]["operations"]:
        _fail()
    body["effect_summary"] = {"operations": effect_scope["operations"], "targets_sha256": effects["targets_sha256"]}
    return body


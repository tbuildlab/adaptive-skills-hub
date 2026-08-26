"""Strict data contract for a future bounded Nexus Agent Runtime.

R5 and this foundation phase do not execute Agents.  The contract exists so a
later, separately approved runtime cannot silently inherit shell, write,
network, delegation, or raw-context authority from an Agent persona.
"""
from __future__ import annotations

import json
import re
from pathlib import PurePosixPath, PureWindowsPath
from typing import Any, Mapping


AGENT_CONTRACT_SCHEMA_VERSION = "nexus.agent-task-contract.v1"
AGENT_MODES = frozenset({"advisory_only"})
MAX_TURNS = 8
MAX_TIMEOUT_SECONDS = 900
MAX_TOKEN_BUDGET = 32_000
OPAQUE_ID_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._:/-]{0,127}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_KEYS = frozenset(
    {
        "raw_context",
        "raw_instructions",
        "skill_md",
        "environment",
        "secrets",
        "hidden_reasoning",
        "workspace_content",
    }
)


class AgentContractError(ValueError):
    """Raised when an Agent task contract exceeds the approved boundary."""


def _identifier(value: Any, field: str) -> str:
    if not isinstance(value, str) or not OPAQUE_ID_RE.fullmatch(value):
        raise AgentContractError(f"Agent contract identifier is invalid: {field}")
    return value


def _id_list(value: Any, field: str, *, allow_empty: bool = True) -> list[str]:
    if not isinstance(value, list) or (not allow_empty and not value):
        raise AgentContractError(f"Agent contract list is invalid: {field}")
    result = [_identifier(item, field) for item in value]
    if len(set(result)) != len(result):
        raise AgentContractError(f"Agent contract list is duplicated: {field}")
    return result


def _walk_forbidden(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).casefold() in FORBIDDEN_KEYS:
                raise AgentContractError("Agent contract contains forbidden raw context")
            _walk_forbidden(child)
    elif isinstance(value, list):
        for child in value:
            _walk_forbidden(child)
    elif isinstance(value, str):
        normalized = value.replace("\\", "/")
        if PurePosixPath(normalized).is_absolute() or PureWindowsPath(value).is_absolute():
            raise AgentContractError("Agent contract contains an absolute path")


def validate_agent_task_contract(payload: Any) -> dict[str, Any]:
    """Validate an advisory-only, cancellable, budgeted Agent task contract."""
    if not isinstance(payload, Mapping) or payload.get("schema_version") != AGENT_CONTRACT_SCHEMA_VERSION:
        raise AgentContractError("Agent contract schema is invalid")
    _walk_forbidden(payload)
    _identifier(payload.get("contract_id"), "contract_id")
    _identifier(payload.get("agent_id"), "agent_id")
    if payload.get("mode") not in AGENT_MODES:
        raise AgentContractError("Agent contract mode is not approved")
    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AgentContractError("Agent provenance is invalid")
    _identifier(provenance.get("source_id"), "source_id")
    repository = provenance.get("repository")
    commit = provenance.get("commit")
    digest = provenance.get("content_sha256")
    if not isinstance(repository, str) or repository.count("/") != 1:
        raise AgentContractError("Agent repository is invalid")
    if not isinstance(commit, str) or not COMMIT_RE.fullmatch(commit):
        raise AgentContractError("Agent commit is not pinned")
    if digest is not None and (not isinstance(digest, str) or not SHA256_RE.fullmatch(digest)):
        raise AgentContractError("Agent content digest is invalid")
    task = payload.get("task")
    if not isinstance(task, Mapping):
        raise AgentContractError("Agent task is invalid")
    _identifier(task.get("objective_id"), "objective_id")
    _id_list(task.get("input_reference_ids"), "input_reference_ids")
    _identifier(task.get("output_schema_id"), "output_schema_id")
    _id_list(payload.get("allowed_capability_ids"), "allowed_capability_ids")
    limits = payload.get("limits")
    if not isinstance(limits, Mapping):
        raise AgentContractError("Agent limits are invalid")
    turns = limits.get("max_turns")
    timeout = limits.get("timeout_seconds")
    tokens = limits.get("token_budget")
    if not isinstance(turns, int) or not 1 <= turns <= MAX_TURNS:
        raise AgentContractError("Agent turn budget is invalid")
    if not isinstance(timeout, int) or not 1 <= timeout <= MAX_TIMEOUT_SECONDS:
        raise AgentContractError("Agent timeout is invalid")
    if not isinstance(tokens, int) or not 1 <= tokens <= MAX_TOKEN_BUDGET:
        raise AgentContractError("Agent token budget is invalid")
    permissions = payload.get("permissions")
    required_permissions = {
        "read_only": True,
        "network": False,
        "shell": False,
        "subprocess": False,
        "write": False,
        "delegation": False,
    }
    if permissions != required_permissions:
        raise AgentContractError("Agent permissions exceed the advisory boundary")
    cancellation = payload.get("cancellation")
    if not isinstance(cancellation, Mapping) or cancellation.get("supported") is not True:
        raise AgentContractError("Agent cancellation is required")
    _identifier(cancellation.get("signal_id"), "cancellation.signal_id")
    validation = payload.get("validation")
    if not isinstance(validation, Mapping) or validation.get("required") is not True:
        raise AgentContractError("Agent output validation is required")
    _id_list(validation.get("validator_capability_ids"), "validator_capability_ids", allow_empty=False)
    receipt = payload.get("receipt")
    if not isinstance(receipt, Mapping):
        raise AgentContractError("Agent receipt contract is invalid")
    required_receipt_fields = {
        "contract_id",
        "agent_id",
        "started",
        "completed",
        "cancelled",
        "output_reference_id",
        "validation_status",
        "result_code",
    }
    if set(receipt.get("required_fields", [])) != required_receipt_fields:
        raise AgentContractError("Agent receipt fields are incomplete")
    return json.loads(json.dumps(payload, ensure_ascii=False))

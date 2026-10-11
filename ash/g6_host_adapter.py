"""Thin G6 preparation and G4 gate composition; no execution or qualification.

OpenAI/Host supplies observations and performs authorized work independently.
Nexus checks bounded evidence consistency. No callback, retry, ledger or storage.
"""
from __future__ import annotations

from typing import Any

from .g6_contracts import G6Error, validate_bundle, require
from .g1_profiles import G1Error, integer
from .g4_contracts import G4Error, binding, validate_domain_bundle
from .g4_host_adapter import pre_execution_gate, request


def evaluate_preparation(bundle: Any, *, domain_bundle: Any = None) -> dict:
    """Optional G4 domain composition binds to the same artifact and task.

    A PASS reports structural consistency only, never a live or value result.
    Errors return fixed diagnostics with no raw records or exception text.
    """
    try:
        require(type(bundle) is dict)
        verdict = validate_bundle(**bundle)
        if domain_bundle is not None:
            require(type(domain_bundle) is dict)
            binding(domain_bundle.get("expected_binding"))
            integer(domain_bundle.get("now"))
            require(domain_bundle.get("expected_binding") == bundle["expected_binding"]
                    and domain_bundle.get("now") == bundle["now"], "G6_BINDING_MISMATCH")
            # Artifact identity is checked by G4's own independent observation oracle.
            domain = validate_domain_bundle(**domain_bundle)
            require(all(o["artifact_sha256"] == bundle["expected_artifact_sha256"]
                        for o in domain_bundle["observations"].values()),
                    "G6_ARTIFACT_SUBSTITUTED")
            verdict = {**verdict, "domain_pack_ref": domain["pack_ref"]}
        return {**verdict, "g3_dependency": "BLOCKED_BY_G3", "d03_dependency": "BLOCKED_BY_D03"}
    except G6Error as exc:
        # G6Error is emitted only with module-owned fixed codes.
        return _deny(str(exc) if str(exc).startswith("G6_") else "G6_INVALID_INPUT")
    except (G1Error, G4Error, KeyError, TypeError, ValueError, AttributeError, RecursionError):
        return _deny("G6_INVALID_INPUT")


def _deny(reason: str) -> dict:
    return {"status": "DENY", "reason": reason, "basis": "NON_AUTHORITATIVE",
            "dispatch_authority": "none", "real_admission_enabled": False,
            "production_freeze": "DENY"}


def release_gate(value: Any, g3_authority: Any = None, *, now: int) -> dict:
    """Reuse G4's typed authority boundary. There is no positive G6 branch.

    D03 metadata, historical lessons, structural receipts and restart snapshots
    cannot enable publication or production freeze.
    """
    decision = pre_execution_gate(value, g3_authority, now=now)
    try:
        recovery_required = request(value)["requires_recovery"]
    except (G4Error, TypeError, ValueError):
        recovery_required = True
    return {**_deny("G6_REAL_ADMISSION_DISABLED"), "g4_reason": decision["reason"],
            "g3_dependency": "BLOCKED_BY_G3",
            "d03_dependency": "BLOCKED_BY_D03" if recovery_required else "NOT_REQUIRED_FOR_REQUEST"}

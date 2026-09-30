"""Offline pair consistency only; no source authentication or production caller."""
import json

from prototypes.governance_assessment_offline_v1 import MAX_BYTES, review_bytes


def review_pair(source_bytes: bytes, derived_bytes: bytes) -> dict:
    """Compare non-secret report bytes with recomputation; MATCH never grants."""
    current = None
    comparison = "INVALID_INPUT"
    if (
        type(source_bytes) is bytes
        and type(derived_bytes) is bytes
        and len(source_bytes) <= MAX_BYTES
        and len(derived_bytes) <= MAX_BYTES
    ):
        current = review_bytes(source_bytes)
        expected = (
            json.dumps(current, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
            + "\n"
        ).encode("utf-8")
        comparison = "MATCH" if derived_bytes == expected else "MISMATCH"
    count = None
    if current is not None and current["structure"] == "CONSISTENT":
        count = len(current["declared_checks"])
    return {
        "comparison": comparison,
        "authority": "none",
        "dispatch_requested": False,
        "proof_scope": "recomputed_offline_report_matches_supplied_bytes_only",
        "source_evidence_status": "UNVERIFIED",
        "selection_completeness": "UNVERIFIED",
        "declared_check_count": count,
        "recomputed_report": current,
    }

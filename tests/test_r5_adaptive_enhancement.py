from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest

from ash.mcp.adapter import NexusMcpRuntime
from ash.mcp.authorization import WorkspaceAuthorizer
from ash.mcp.enhancement import (
    ENHANCEMENT_HANDOFF_SCHEMA_VERSION,
    is_current_enhancement_handoff,
    select_enhancement,
    validate_enhancement_receipt,
)
from ash.mcp.handoff import HANDOFF_SCHEMA_VERSION
from ash.mcp.host_mapping import PRESENTATIONS_ENHANCEMENT_MAPPING_ID, PRESENTATIONS_MAPPING_ID, presentation_profile
from ash.mcp.redaction import safe_enhancement_handoff
from ash.mcp.schemas import NexusMcpError, parse_prepare_enhancement_handoff_request


def valid_state(*, observations: list[str] | None = None, enhancement_pass: int = 0) -> dict:
    return {
        "schema_version": "nexus.host-artifact-state.v1",
        "artifact_kind": "pptx",
        "base_mapping_id": PRESENTATIONS_MAPPING_ID,
        "base_execution_state": "execution_succeeded",
        "base_validation_state": "validation_passed",
        "checks": {
            "artifact_created": "passed",
            "artifact_editable": "passed",
            "presentation_open_render": "passed",
        },
        "observations": observations or [],
        "enhancement_pass": enhancement_pass,
    }


def valid_base_pair() -> tuple[dict, dict]:
    expiry = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat().replace("+00:00", "Z")
    handoff = {
        "schema_version": HANDOFF_SCHEMA_VERSION,
        "handoff_id": "r4-current-handoff",
        "expires_at": expiry,
        "selected_skill": {"name": "Presentations", "content_sha256": "a" * 64},
        "logical_host_capability": "chatgpt.presentations",
        "host_execution_profile": presentation_profile(),
    }
    receipt = {
        "handoff_id": handoff["handoff_id"],
        "selected_skill": "Presentations",
        "content_sha256": "a" * 64,
        "host_capability": "chatgpt.presentations",
        "host_execution_mapping_id": PRESENTATIONS_MAPPING_ID,
        "input_resolution": "safe_defaults_applied",
        "states": [
            "selected", "loaded_verified", "host_eligible", "execution_requested",
            "execution_started", "execution_succeeded", "validation_passed",
        ],
        "result_code": "EXECUTION_SUCCEEDED",
        "artifact_ref": "host-artifact:primary",
        "artifact_kind": "pptx",
    }
    return handoff, receipt


class R5AdaptiveEnhancementTests(unittest.TestCase):
    def _handoff(self, observations: list[str] | None = None) -> dict:
        return safe_enhancement_handoff(parse_prepare_enhancement_handoff_request(valid_state(observations=observations)))

    @staticmethod
    def _success_receipt(handoff: dict) -> dict:
        return {
            "handoff_id": handoff["handoff_id"],
            "candidate_id": handoff["selected_candidate"]["candidate_id"],
            "host_capability": "chatgpt.presentations",
            "host_execution_mapping_id": PRESENTATIONS_ENHANCEMENT_MAPPING_ID,
            "states": [
                "base_execution_verified", "artifact_state_verified", "enhancement_requested",
                "checkpoint_created", "enhancement_started", "enhancement_succeeded", "revalidation_passed",
            ],
            "result_code": "ENHANCEMENT_SUCCEEDED",
            "checkpoint_created": True,
            "artifact_ref": "host-artifact:enhanced",
            "artifact_kind": "pptx",
            "validation_checks": {"artifact_editable": "passed", "presentation_open_render": "passed"},
            "improvement_assessment": "improved",
        }

    def test_r5_selects_one_deterministic_minimal_host_mapped_candidate(self) -> None:
        state = parse_prepare_enhancement_handoff_request(valid_state(observations=["text_legibility_low", "layout_density_high"]))
        decision = select_enhancement(state)
        self.assertEqual(decision.status, "enhancement_requested")
        self.assertEqual(decision.profile["candidate_id"], "presentation_layout_polish.v1")
        handoff = safe_enhancement_handoff(state)
        self.assertEqual(handoff["schema_version"], ENHANCEMENT_HANDOFF_SCHEMA_VERSION)
        self.assertEqual(handoff["status"], "enhancement_requested")
        self.assertEqual(handoff["selected_candidate"]["candidate_id"], "presentation_layout_polish.v1")
        self.assertEqual(handoff["logical_host_capability"], "chatgpt.presentations")
        self.assertEqual(handoff["required_checkpoint"], "host_copy_on_write")
        self.assertTrue(is_current_enhancement_handoff(handoff))
        self.assertEqual(handoff["security_result"]["code"], "HOST_ENHANCEMENT_HANDOFF_READY")

    def test_clean_or_budget_exhausted_artifact_has_no_enhancement(self) -> None:
        clean = self._handoff()
        self.assertEqual(clean["status"], "no_enhancement_needed")
        self.assertEqual(clean["security_result"]["code"], "NO_ENHANCEMENT_NEEDED")
        exhausted = safe_enhancement_handoff(parse_prepare_enhancement_handoff_request(valid_state(observations=["layout_density_high"], enhancement_pass=1)))
        self.assertEqual(exhausted["status"], "no_enhancement_needed")
        self.assertEqual(exhausted["reason_codes"], ["enhancement_pass_budget_exhausted"])

    def test_state_schema_rejects_paths_artifacts_skills_hashes_agents_and_raw_content(self) -> None:
        for forbidden in ("path", "artifact_ref", "task", "handoff_id", "receipt", "skill", "agent", "content_sha256", "RAW_SKILL_SENTINEL"):
            with self.assertRaises(NexusMcpError):
                parse_prepare_enhancement_handoff_request({**valid_state(), forbidden: "attacker-controlled"})
        for mutation in (
            {"observations": ["not-an-approved-observation"]},
            {"observations": ["layout_density_high", "layout_density_high"]},
            {"checks": {"artifact_created": "passed"}},
            {"base_mapping_id": "nexus.host-map.documents.v1"},
            {"base_validation_state": "validation_failed"},
            {"enhancement_pass": 2},
        ):
            with self.assertRaises(NexusMcpError):
                parse_prepare_enhancement_handoff_request({**valid_state(), **mutation})

    def test_handoff_is_redacted_and_never_reloads_or_reroutes_a_skill(self) -> None:
        handoff = self._handoff(["layout_density_high"])
        encoded = json.dumps(handoff)
        for forbidden in ("RAW_SKILL_SENTINEL", "SECRET_VALUE_SENTINEL", "instructions", "path", "artifact_ref", "task", "agent", "Canva", "ppt-master"):
            self.assertNotIn(forbidden, encoded)
        self.assertNotIn("selected_skill", handoff)
        self.assertNotIn("content_sha256", handoff)

    def test_runtime_enhancement_tool_does_not_build_catalog_or_access_workspace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "project"
            root.mkdir()
            called = False

            def catalog():
                nonlocal called
                called = True
                raise AssertionError("R5 must not re-run discovery or planning")

            runtime = NexusMcpRuntime(WorkspaceAuthorizer.from_roots_for_test({"project": root}), catalog_builder=catalog, skill_roots=[])
            payload = runtime.prepare_enhancement_handoff(valid_state(observations=["layout_density_high"]))
            self.assertEqual(payload["status"], "enhancement_requested")
            self.assertFalse(called)

    def test_receipt_requires_bound_primary_success_checkpoint_artifact_and_revalidation(self) -> None:
        handoff = self._handoff(["layout_density_high"])
        base_handoff, base_receipt = valid_base_pair()
        self.assertEqual(validate_enhancement_receipt(handoff, self._success_receipt(handoff), base_handoff=base_handoff, base_receipt=base_receipt), "ENHANCEMENT_SUCCEEDED")
        no_artifact = self._success_receipt(handoff)
        no_artifact["artifact_ref"] = ""
        self.assertEqual(validate_enhancement_receipt(handoff, no_artifact, base_handoff=base_handoff, base_receipt=base_receipt), "ARTIFACT_MISSING")
        no_improvement_evidence = self._success_receipt(handoff)
        no_improvement_evidence.pop("improvement_assessment")
        self.assertEqual(validate_enhancement_receipt(handoff, no_improvement_evidence, base_handoff=base_handoff, base_receipt=base_receipt), "IMPROVEMENT_UNVERIFIED")
        no_checkpoint = self._success_receipt(handoff)
        no_checkpoint["checkpoint_created"] = False
        self.assertEqual(validate_enhancement_receipt(handoff, no_checkpoint, base_handoff=base_handoff, base_receipt=base_receipt), "HOST_ROLLBACK_UNAVAILABLE")
        invalid_base = dict(base_receipt)
        invalid_base["content_sha256"] = "b" * 64
        self.assertEqual(validate_enhancement_receipt(handoff, self._success_receipt(handoff), base_handoff=base_handoff, base_receipt=invalid_base), "BASE_RECEIPT_INVALID")

    def test_receipt_rejects_substitution_replay_and_expiry(self) -> None:
        handoff = self._handoff(["layout_density_high"])
        base_handoff, base_receipt = valid_base_pair()
        substituted = self._success_receipt(handoff)
        substituted["candidate_id"] = "presentation_legibility_polish.v1"
        self.assertEqual(validate_enhancement_receipt(handoff, substituted, base_handoff=base_handoff, base_receipt=base_receipt), "ENHANCEMENT_SUBSTITUTION_REJECTED")
        seen: set[str] = set()
        self.assertEqual(validate_enhancement_receipt(handoff, self._success_receipt(handoff), base_handoff=base_handoff, base_receipt=base_receipt, seen_handoff_ids=seen), "ENHANCEMENT_SUCCEEDED")
        self.assertEqual(validate_enhancement_receipt(handoff, self._success_receipt(handoff), base_handoff=base_handoff, base_receipt=base_receipt, seen_handoff_ids=seen), "ENHANCEMENT_HANDOFF_REPLAYED")
        expired = dict(handoff)
        expired["expires_at"] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat().replace("+00:00", "Z")
        self.assertEqual(validate_enhancement_receipt(expired, self._success_receipt(expired), base_handoff=base_handoff, base_receipt=base_receipt), "ENHANCEMENT_HANDOFF_EXPIRED")

    def test_host_failure_and_transactional_rollback_receipts_are_truthful(self) -> None:
        handoff = self._handoff(["layout_density_high"])
        base_handoff, base_receipt = valid_base_pair()
        unavailable = self._success_receipt(handoff)
        unavailable.update({"states": ["base_execution_verified", "artifact_state_verified", "enhancement_requested"], "result_code": "HOST_CAPABILITY_UNAVAILABLE"})
        self.assertEqual(validate_enhancement_receipt(handoff, unavailable, base_handoff=base_handoff, base_receipt=base_receipt), "HOST_CAPABILITY_UNAVAILABLE")
        refused = self._success_receipt(handoff)
        refused.update({"states": ["base_execution_verified", "artifact_state_verified", "enhancement_requested"], "result_code": "EXECUTION_REFUSED"})
        self.assertEqual(validate_enhancement_receipt(handoff, refused, base_handoff=base_handoff, base_receipt=base_receipt), "EXECUTION_REFUSED")
        validation_failed = self._success_receipt(handoff)
        validation_failed.update({
            "states": ["base_execution_verified", "artifact_state_verified", "enhancement_requested", "checkpoint_created", "enhancement_started", "enhancement_succeeded", "revalidation_failed", "rollback_restored"],
            "result_code": "VALIDATION_FAILED",
            "rollback_status": "restored",
        })
        self.assertEqual(validate_enhancement_receipt(handoff, validation_failed, base_handoff=base_handoff, base_receipt=base_receipt), "VALIDATION_FAILED_ROLLBACK_RESTORED")
        no_improvement = self._success_receipt(handoff)
        no_improvement.update({
            "states": ["base_execution_verified", "artifact_state_verified", "enhancement_requested", "checkpoint_created", "enhancement_started", "enhancement_succeeded", "revalidation_passed", "rollback_restored"],
            "result_code": "NO_IMPROVEMENT",
            "rollback_status": "restored",
            "improvement_assessment": "not_improved",
        })
        self.assertEqual(validate_enhancement_receipt(handoff, no_improvement, base_handoff=base_handoff, base_receipt=base_receipt), "NO_IMPROVEMENT_ROLLBACK_RESTORED")
        rollback_unavailable = self._success_receipt(handoff)
        rollback_unavailable.update({
            "states": ["base_execution_verified", "artifact_state_verified", "enhancement_requested", "rollback_unavailable"],
            "result_code": "HOST_ROLLBACK_UNAVAILABLE",
            "checkpoint_created": False,
        })
        self.assertEqual(validate_enhancement_receipt(handoff, rollback_unavailable, base_handoff=base_handoff, base_receipt=base_receipt), "HOST_ROLLBACK_UNAVAILABLE")

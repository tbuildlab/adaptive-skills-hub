from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import ash.mcp.adapter as adapter
from ash.mcp.adapter import NexusMcpRuntime, R4_PRESENTATIONS_CONSTRAINT
from ash.mcp.authorization import WorkspaceAuthorizer
from ash.mcp.handoff import HANDOFF_SCHEMA_VERSION, is_current_handoff, validate_host_receipt
from ash.mcp.host_mapping import PRESENTATIONS_MAPPING_ID
from ash.mcp.redaction import safe_host_handoff
from ash.mcp.schemas import NexusMcpError, parse_prepare_host_handoff_request
from ash.semantic_domains import make_trusted_applicability


def presentation_record(root: Path, *, name: str = "Presentations") -> dict:
    path = root / "presentations" / "SKILL.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\nname: Presentations\ndescription: Create editable PowerPoint presentation decks.\n---\n"
        "RAW_SKILL_SENTINEL\nSECRET_VALUE_SENTINEL\n",
        encoding="utf-8",
    )
    return {
        "id": "skill:presentations", "kind": "skill", "name": name,
        "description": "Create editable PowerPoint presentation decks.",
        "path": str(path.parent), "skill_md_path": str(path), "scope": "project",
        "source": "local", "tags": ["presentation"], "status": "available", "metadata": {},
        "provenance": {"source_scope": "project-specific", "precedence": 40},
        "content_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "content_bytes": path.stat().st_size,
        "_nexus_trusted_applicability": make_trusted_applicability(
            supported_domains=("presentation",),
            supported_task_kinds=("create_artifact", "edit_artifact", "read_artifact"),
            required_context=("office_artifact",),
            artifact_families=("presentation",),
            provenance="unit_test_fixture",
        ),
    }


class R4HostHandoffTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "project"
        self.root.mkdir()
        self.skills = Path(self.temp.name) / "skills"
        self.skill = presentation_record(self.skills)
        self.runtime = NexusMcpRuntime(
            WorkspaceAuthorizer.from_roots_for_test({"project": self.root}),
            catalog_builder=lambda: {"skills": [self.skill], "agents": []},
            skill_roots=[self.skills],
        )
        self.arguments = {
            "task": "Create an editable PowerPoint presentation about digital transformation in business.",
            "workspace_id": "project", "project_context_mode": "none",
        }

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _handoff(self) -> dict:
        return self.runtime.prepare_host_handoff(self.arguments)

    @staticmethod
    def _success_receipt(handoff: dict) -> dict:
        return {
            "handoff_id": handoff["handoff_id"], "selected_skill": "Presentations",
            "content_sha256": handoff["selected_skill"]["content_sha256"],
            "host_capability": "chatgpt.presentations",
            "host_execution_mapping_id": PRESENTATIONS_MAPPING_ID,
            "input_resolution": "safe_defaults_applied",
            "states": ["selected", "loaded_verified", "host_eligible", "execution_requested", "execution_started", "execution_succeeded", "validation_passed"],
            "result_code": "EXECUTION_SUCCEEDED", "artifact_ref": "host-artifact:opaque-presentation", "artifact_kind": "pptx",
        }

    def test_handoff_is_single_presentation_redacted_and_short_lived(self) -> None:
        handoff = self._handoff()
        self.assertEqual(handoff["schema_version"], HANDOFF_SCHEMA_VERSION)
        self.assertEqual(handoff["status"], "execution_requested")
        self.assertEqual(handoff["selected_skill"]["name"], "Presentations")
        self.assertEqual(handoff["selected_skill"]["load_verification_state"], "loaded_verified")
        self.assertEqual(handoff["logical_host_capability"], "chatgpt.presentations")
        self.assertEqual(handoff["requested_execution_mode"], "host_native_presentations")
        self.assertEqual(handoff["host_execution_profile"]["mapping_id"], PRESENTATIONS_MAPPING_ID)
        self.assertEqual(handoff["host_execution_profile"]["continuation_policy"], "continue_with_safe_defaults")
        self.assertEqual(handoff["host_execution_profile"]["clarification_policy"], "ask_only_for_required_noninferable_input")
        self.assertTrue(is_current_handoff(handoff))
        encoded = json.dumps(handoff)
        for forbidden in ("RAW_SKILL_SENTINEL", "SECRET_VALUE_SENTINEL", str(self.root), str(self.skills), "instructions", "path", "project_context", "rules"):
            self.assertNotIn(forbidden, encoded)

    def test_default_profile_is_allowlisted_and_receipt_must_record_it(self) -> None:
        handoff = self._handoff()
        profile = handoff["host_execution_profile"]
        self.assertEqual(profile["resolved_defaults"]["artifact_format"], "editable_pptx")
        self.assertNotIn(self.arguments["task"], json.dumps(profile))
        omitted = self._success_receipt(handoff)
        omitted.pop("input_resolution")
        self.assertEqual(validate_host_receipt(handoff, omitted), "INPUT_RESOLUTION_UNVERIFIED")
        mismatch = self._success_receipt(handoff)
        mismatch["host_execution_mapping_id"] = "nexus.host-map.unknown.v1"
        self.assertEqual(validate_host_receipt(handoff, mismatch), "HOST_MAPPING_MISMATCH")

    def test_selected_but_not_loaded_fails_closed(self) -> None:
        self.skill["skill_md_path"] = str(self.skills / "missing" / "SKILL.md")
        with self.assertRaisesRegex(NexusMcpError, "selected Skill load evidence") as raised:
            self._handoff()
        self.assertEqual(raised.exception.code, "SKILL_LOAD_FAILED")

    def test_r4_constraint_selects_only_presentations_without_changing_default_ranking(self) -> None:
        ppt_root = Path(self.temp.name) / "ppt-master"
        ppt_path = ppt_root / "SKILL.md"
        ppt_root.mkdir()
        ppt_path.write_text(
            "---\nname: ppt-master\ndescription: Create editable PowerPoint PPTX presentation decks.\n---\n",
            encoding="utf-8",
        )
        ppt = {
            **self.skill, "id": "skill:ppt-master", "name": "ppt-master", "description": "Create editable PowerPoint PPTX presentation decks.",
            "path": str(ppt_root), "skill_md_path": str(ppt_path),
            "content_sha256": hashlib.sha256(ppt_path.read_bytes()).hexdigest(),
            "content_bytes": ppt_path.stat().st_size,
        }
        self.runtime.catalog_builder = lambda: {"skills": [ppt, self.skill], "agents": []}
        self.runtime.skill_roots = [self.skills, ppt_root]
        unconstrained = self.runtime.plan(self.arguments)
        self.assertEqual(unconstrained["selected_skills"][0]["name"], "ppt-master")
        constrained_args = {**self.arguments, "constraints": [R4_PRESENTATIONS_CONSTRAINT]}
        constrained = self.runtime.plan(constrained_args)
        self.assertEqual([item["name"] for item in constrained["selected_skills"]], ["Presentations"])
        handoff = self.runtime.prepare_host_handoff(constrained_args)
        self.assertEqual(handoff["security_result"]["code"], "HOST_HANDOFF_READY")

    def test_unsupported_r4_host_constraint_is_rejected(self) -> None:
        with self.assertRaisesRegex(NexusMcpError, "host capability constraint") as raised:
            self.runtime.prepare_host_handoff({**self.arguments, "constraints": ["r4_host_capability:documents"]})
        self.assertEqual(raised.exception.code, "INVALID_REQUEST")

    def test_ambiguous_skill_selection_is_ineligible(self) -> None:
        plan, loads, validation = self.runtime._plan_and_load(parse_prepare_host_handoff_request(self.arguments))
        plan.selected.append(plan.selected[0])
        with self.assertRaisesRegex(NexusMcpError, "exactly one selected Skill") as raised:
            safe_host_handoff(plan, loads, validation)
        self.assertEqual(raised.exception.code, "HANDOFF_NOT_ELIGIBLE")

    def test_hash_mismatch_between_load_and_handoff_fails_closed(self) -> None:
        actual_loader = adapter.load_plan_skills
        calls = 0

        def altered_loader(*args, **kwargs):
            nonlocal calls
            calls += 1
            result = actual_loader(*args, **kwargs)
            if calls == 2:
                result[0]["sha256"] = "0" * 64
            return result

        with patch.object(adapter, "load_plan_skills", side_effect=altered_loader):
            with self.assertRaisesRegex(NexusMcpError, "changed before host handoff") as raised:
                self._handoff()
        self.assertEqual(raised.exception.code, "SKILL_INTEGRITY_FAILED")

    def test_malformed_handoff_input_cannot_supply_skill_hash_or_replay_data(self) -> None:
        for forbidden in ("skill", "content_sha256", "handoff_id", "artifact_ref"):
            with self.assertRaises(NexusMcpError):
                parse_prepare_host_handoff_request({**self.arguments, forbidden: "attacker-controlled"})

    def test_host_capability_unavailable_and_execution_refused_are_explicit(self) -> None:
        handoff = self._handoff()
        unavailable = self._success_receipt(handoff)
        unavailable.update({
            "host_capability": "unavailable",
            "states": [
                "selected", "loaded_verified", "execution_requested",
                "host_capability_unavailable",
            ],
            "result_code": "HOST_CAPABILITY_UNAVAILABLE",
        })
        unavailable.pop("artifact_ref")
        unavailable.pop("artifact_kind")
        self.assertEqual(validate_host_receipt(handoff, unavailable), "HOST_CAPABILITY_UNAVAILABLE")
        refused = self._success_receipt(handoff)
        refused.update({
            "states": [
                "selected", "loaded_verified", "host_eligible",
                "execution_requested", "execution_refused",
            ],
            "result_code": "EXECUTION_REFUSED",
        })
        refused.pop("artifact_ref")
        refused.pop("artifact_kind")
        self.assertEqual(validate_host_receipt(handoff, refused), "EXECUTION_REFUSED")
        binding_unavailable = self._success_receipt(handoff)
        binding_unavailable.update({
            "states": [
                "selected", "loaded_verified", "execution_requested",
                "host_execution_binding_unavailable",
            ],
            "result_code": "HOST_EXECUTION_BINDING_UNAVAILABLE",
        })
        binding_unavailable.pop("artifact_ref")
        binding_unavailable.pop("artifact_kind")
        self.assertEqual(
            validate_host_receipt(handoff, binding_unavailable),
            "HOST_EXECUTION_BINDING_UNAVAILABLE",
        )

    def test_contradictory_or_noncanonical_state_sequences_fail_closed(self) -> None:
        handoff = self._handoff()
        contradictory = self._success_receipt(handoff)
        contradictory["states"] = [
            "selected", "loaded_verified", "host_eligible",
            "execution_requested", "execution_started", "execution_failed",
            "execution_succeeded", "validation_passed",
        ]
        self.assertEqual(validate_host_receipt(handoff, contradictory), "HANDOFF_MALFORMED")

        validation_without_execution = self._success_receipt(handoff)
        validation_without_execution["states"] = [
            "selected", "loaded_verified", "host_eligible",
            "execution_requested", "validation_passed",
        ]
        self.assertEqual(validate_host_receipt(handoff, validation_without_execution), "HANDOFF_MALFORMED")

        failed_with_success_trace = self._success_receipt(handoff)
        failed_with_success_trace.update({
            "result_code": "ARTIFACT_GENERATION_FAILED",
            "states": [
                "selected", "loaded_verified", "host_eligible",
                "execution_requested", "execution_started", "execution_succeeded",
                "validation_passed",
            ],
        })
        self.assertEqual(validate_host_receipt(handoff, failed_with_success_trace), "HANDOFF_MALFORMED")

    def test_no_artifact_generation_failure_and_validation_failure_are_not_success(self) -> None:
        handoff = self._handoff()
        no_artifact = self._success_receipt(handoff)
        no_artifact.update({"states": ["selected", "loaded_verified", "host_eligible", "execution_requested", "execution_started"], "artifact_ref": ""})
        self.assertEqual(validate_host_receipt(handoff, no_artifact), "ARTIFACT_MISSING")
        for invalid_ref in (
            " ", "opaque-presentation", "C:\\private\\deck.pptx", "C:private.pptx",
            "/tmp/deck.pptx", "file:private", "https:example.invalid",
            "https://example.invalid/deck.pptx", "host-artifact:C:private.pptx",
            "host-artifact:../private.pptx", "host-artifact:private/secret.pptx",
            "host-artifact:%2Fprivate.pptx", "host-artifact:" + "a" * 243,
        ):
            invalid_artifact = self._success_receipt(handoff)
            invalid_artifact["artifact_ref"] = invalid_ref
            with self.subTest(artifact_ref=invalid_ref):
                self.assertEqual(validate_host_receipt(handoff, invalid_artifact), "ARTIFACT_MISSING")
        generated_failure = self._success_receipt(handoff)
        generated_failure.update({"states": ["selected", "loaded_verified", "host_eligible", "execution_requested", "execution_started", "execution_failed"], "result_code": "ARTIFACT_GENERATION_FAILED"})
        generated_failure.pop("artifact_ref")
        generated_failure.pop("artifact_kind")
        self.assertEqual(validate_host_receipt(handoff, generated_failure), "ARTIFACT_GENERATION_FAILED")
        for leaked_artifact in ("C:\\private\\deck.pptx", "https://example.invalid/deck.pptx"):
            malformed_failure = dict(generated_failure)
            malformed_failure["artifact_ref"] = leaked_artifact
            with self.subTest(failure_artifact_ref=leaked_artifact):
                self.assertEqual(validate_host_receipt(handoff, malformed_failure), "HANDOFF_MALFORMED")
        validation_failure = self._success_receipt(handoff)
        validation_failure.update({"states": ["selected", "loaded_verified", "host_eligible", "execution_requested", "execution_started", "execution_succeeded", "validation_failed"], "result_code": "VALIDATION_FAILED"})
        self.assertEqual(validate_host_receipt(handoff, validation_failure), "VALIDATION_FAILED")
        validation_failure["artifact_ref"] = ""
        self.assertEqual(validate_host_receipt(handoff, validation_failure), "ARTIFACT_MISSING")

        invalid_input_resolution = self._success_receipt(handoff)
        invalid_input_resolution["input_resolution"] = "caller_supplied"
        self.assertEqual(
            validate_host_receipt(handoff, invalid_input_resolution),
            "INPUT_RESOLUTION_UNVERIFIED",
        )

    def test_malformed_receipt_is_rejected_without_accepting_extra_context(self) -> None:
        handoff = self._handoff()
        malformed = self._success_receipt(handoff)
        malformed["path"] = str(self.root)
        self.assertEqual(validate_host_receipt(handoff, malformed), "HANDOFF_MALFORMED")

    def test_skill_substitution_replay_and_expiry_are_rejected(self) -> None:
        handoff = self._handoff()
        substituted = self._success_receipt(handoff)
        substituted["selected_skill"] = "Canva"
        self.assertEqual(validate_host_receipt(handoff, substituted), "SKILL_SUBSTITUTION_REJECTED")
        seen: set[str] = set()
        self.assertEqual(validate_host_receipt(handoff, self._success_receipt(handoff), seen_handoff_ids=seen), "EXECUTION_SUCCEEDED")
        self.assertEqual(validate_host_receipt(handoff, self._success_receipt(handoff), seen_handoff_ids=seen), "HANDOFF_REPLAYED")
        expired = dict(handoff)
        expired["expires_at"] = (datetime.now(timezone.utc) - timedelta(seconds=1)).isoformat().replace("+00:00", "Z")
        self.assertEqual(validate_host_receipt(expired, self._success_receipt(expired)), "HANDOFF_EXPIRED")

    def test_success_receipt_requires_real_pptx_reference_and_full_state_trace(self) -> None:
        handoff = self._handoff()
        self.assertEqual(validate_host_receipt(handoff, self._success_receipt(handoff)), "EXECUTION_SUCCEEDED")

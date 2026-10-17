from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ash import project_memory as m
from ash.mcp.authorization import WorkspaceAuthorizer
from ash.project_memory_store import MemoryStore
from ash.reusable_references import workspace_binding


def fact(key="fact", text="Keep the accepted layout", confidence="observed", evidence_refs=None):
    return dict(id=key, text=text, confidence=confidence, evidence_refs=evidence_refs or [])


def fixture(root, project_id="a" * 32):
    project = root / "project"
    project.mkdir(exist_ok=True)
    (project / "artifact.txt").write_text("Verified controlled artifact", encoding="utf-8")
    now = datetime.now(timezone.utc).isoformat()
    binding = workspace_binding(project)
    checks = [dict(kind="test", status="passed", confidence="verified", evidence_refs=["validation"])]
    receipt = dict(schema_version="nexus.project-validation.v1", project_id=project_id,
        workspace_binding=binding, scope="Controlled milestone", scope_complete=True, automated_validation="passed",
        validated_at=now, checks=checks,
        artifact_digests=[dict(locator="artifact.txt", sha256=hashlib.sha256((project / "artifact.txt").read_bytes()).hexdigest())])
    (project / "validation.json").write_bytes(m.encoded(receipt))
    evidence = dict(id="validation", kind="execution_validation", locator="validation.json",
        sha256=hashlib.sha256((project / "validation.json").read_bytes()).hexdigest(), confidence="verified", summary="Host test passed")
    proposal = dict(schema_version="nexus.project-memory.proposal.v1",
        identity=dict(project_id=project_id, name="Portfolio", purpose="Controlled project continuity", workspace_binding=binding,
                      project_locator=str(project.resolve())),
        state={"stack": ["HTML"], "decisions": [], **{key: [] for key in m.STATE_FIELDS}},
        completion=dict(kind="validated_checkpoint", scope="Controlled milestone", scope_complete=True,
            automated_validation="passed", user_acceptance="not_obtained", validated_at=now,
            receipt_id="validation", checks=checks, evidence_refs=["validation"]),
        artifacts=[], evidence=[evidence], references_used=[], capabilities_used=dict(skills=[], agents=[], workflows=[], fallbacks=[]),
        lessons=[], environment=[], supersessions=[])
    proposal["state"]["completed_scope"] = [fact(confidence="verified", evidence_refs=["validation"])]
    workspace = WorkspaceAuthorizer.from_roots_for_test({"project": project}).resolve("project")
    return proposal, workspace


def temporary():
    # Hermetic D: fixtures only. Never the actual primary store or a C: copy.
    return tempfile.TemporaryDirectory(prefix="nexus-phase-c-test-", dir="D:/" if Path("D:/").is_dir() else None)


class MemoryModelTests(unittest.TestCase):
    def setUp(self):
        self.temp = temporary()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.proposal, self.workspace = fixture(self.root)

    def test_closed_schema_and_completion_checkpoint(self):
        m.validate_proposal(self.proposal)
        complete = deepcopy(self.proposal)
        complete["completion"]["kind"] = "project_completed"
        m.validate_proposal(complete)
        self.assertEqual(complete["completion"]["user_acceptance"], "not_obtained")
        for updates in ({"automated_validation": "failed"}, {"scope_complete": False},
                        {"receipt_id": None}, {"user_acceptance": "rejected"}):
            value = deepcopy(complete)
            value["completion"].update(updates)
            with self.subTest(updates=updates), self.assertRaises(m.MemoryError):
                m.validate_proposal(value)
        value = deepcopy(complete)
        value["state"]["unfinished_work"] = [fact()]
        with self.assertRaises(m.MemoryError):
            m.validate_proposal(value)

    def test_failed_and_incomplete_never_completed(self):
        for kind in ("failed", "incomplete"):
            value = deepcopy(self.proposal)
            value["completion"]["kind"] = kind
            with self.assertRaises(m.MemoryError):
                m.validate_proposal(value)
            value["state"]["completed_scope"] = []
            value["completion"]["automated_validation"] = "failed"
            m.validate_proposal(value)

    def test_user_acceptance_needs_distinct_bound_evidence(self):
        value = deepcopy(self.proposal)
        value["completion"]["user_acceptance"] = "accepted"
        with self.assertRaises(m.MemoryError):
            m.validate_proposal(value)
        receipt = {**value["evidence"][0], "id": "owner", "kind": "user_acceptance"}
        value["evidence"].append(receipt)
        value["completion"]["evidence_refs"].append("owner")
        m.validate_proposal(value)

    def test_limits_for_fields_counts_revision_and_current_core(self):
        for edit in (lambda v: v["capabilities_used"].update(skills=[{}] * 9),
                     lambda v: v.update(lessons=[{}] * 17),
                     lambda v: v["state"].update(constraints=[fact(str(n), "x" * 512) for n in range(16)])):
            value = deepcopy(self.proposal)
            edit(value)
            with self.assertRaises(m.MemoryError):
                m.validate_proposal(value)
        with patch.object(m, "MAX_REVISION_BYTES", 512):
            with self.assertRaises(m.MemoryError):
                m.validate_proposal(self.proposal)

    def test_known_root_cause_requires_verified_support(self):
        value = deepcopy(self.proposal)
        lesson = dict(id="failure", kind="failed_attempt", tags=["navigation"], summary="Boundary mismatch",
            confidence="verified", evidence_refs=["validation"], symptom="Observed mismatch", root_cause_status="known",
            root_cause="Conflicting boundary geometry", correction="Adjusted geometry", validation_result="passed", prevention="Boundary checks")
        value["lessons"] = [lesson]
        m.validate_proposal(value)
        lesson["confidence"] = "inferred"
        with self.assertRaises(m.MemoryError):
            m.validate_proposal(value)

    def test_privacy_and_unsafe_pointers(self):
        values = ["password=not-a-real-secret", "api_key: fixture_only_value", "token=fixture-only-token",
                  "-----BEGIN PRIVATE KEY-----", "sk-" + "A" * 30, "```python dummy", "assistant: transcript",
                  "def sample(): pass", r"C:\Users\private\file", "https://example.org/?credential=dummy"]
        for text in values:
            value = deepcopy(self.proposal)
            value["identity"]["purpose"] = text
            with self.subTest(text=text[:20]), self.assertRaises(m.MemoryError):
                m.validate_proposal(value)
        for locator in ("../artifact", "/absolute", "C:/file", "name:stream", "dir/../file", "NUL", "a\\b"):
            value = deepcopy(self.proposal)
            value["evidence"][0]["locator"] = locator
            with self.subTest(locator=locator), self.assertRaises(m.MemoryError):
                m.validate_proposal(value)

    def test_unknown_fields_duplicate_json_and_size(self):
        value = deepcopy(self.proposal)
        value["transcript"] = "not allowed"
        with self.assertRaises(m.MemoryError):
            m.validate_proposal(value)
        value = deepcopy(self.proposal)
        value["identity"]["purpose"] = "中" * 400
        with self.assertRaises(m.MemoryError):
            m.validate_proposal(value)
        for raw in (b'{"a":1,"a":2}', b'{"a":NaN}', b'x' * (m.MAX_REVISION_BYTES + 1)):
            with self.assertRaises(m.MemoryError):
                m.parse(raw, m.MAX_REVISION_BYTES)

    def test_skills_agents_and_learning_remain_bounded_and_local(self):
        capability = dict(id="skill-fixture", name="Fixture Skill", version="1", source="Host fixture",
            role="validation", scope="current project", selected=True, used=True, result="effective",
            limitation="", evidence_refs=["validation"])
        self.proposal["capabilities_used"]["skills"] = [capability]
        agent = {**capability, "id": "agent-fixture", "result": "partial", "role": "review"}
        self.proposal["capabilities_used"]["agents"] = [agent]
        for number, kind in enumerate(("successful_pattern", "failed_attempt", "rejected_approach", "recovery")):
            self.proposal["lessons"].append(dict(id=f"lesson-{number}", kind=kind, tags=["navigation"],
                summary="Boundary navigation check", confidence="verified", evidence_refs=["validation"],
                symptom="Boundary state mismatch" if kind == "failed_attempt" else "", root_cause_status="unknown",
                root_cause="", correction="Adjusted boundary check", validation_result="passed", prevention="Test boundaries"))
        m.validate_proposal(self.proposal)
        bad = deepcopy(self.proposal)
        bad["lessons"][0]["root_cause"] = "Guessed cause"
        with self.assertRaises(m.MemoryError):
            m.validate_proposal(bad)
        bad = deepcopy(self.proposal)
        bad["capabilities_used"]["skills"][0]["used"] = False
        with self.assertRaises(m.MemoryError):
            m.validate_proposal(bad)
        for outcome in ("partial", "ineffective", "fallback"):
            self.proposal["capabilities_used"]["skills"][0]["result"] = outcome
            m.validate_proposal(self.proposal)


if __name__ == "__main__":
    unittest.main()

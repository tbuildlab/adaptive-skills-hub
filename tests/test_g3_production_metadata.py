"""Synthetic metadata only; no Owner, grants, storage, login or dispatch."""
import ast
import copy
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import tempfile
import unittest

from scripts import g3_production_metadata as m
from ash import g3_authorization as legacy
from tests.g3_fixtures import subject_body, scope

ROOT = Path(__file__).resolve().parents[1]


def evidence(ref="synthetic-evidence"):
    return {"ref": ref, "sha256": "e" * 64}


def reference(kind, old=False):
    return {"id": ("nexus.g3." if old else m.PREFIX) + kind + ".v1:" + "a" * 64,
            "body_sha256": "b" * 64}


def context():
    return dict(context_id="synthetic-context", context_generation=1, authenticated_at_ms=1000,
                context_expires_at_ms=301000, identity_evidence=evidence("identity"), session_evidence=evidence("managed-proof"))


def binding():
    return dict(owner=dict(issuer="https://issuer.invalid", client_id="synthetic-app", subject="synthetic-owner"),
                owner_generation=1, workspace_id="synthetic-workspace", project_id="synthetic-project",
                binding_id="synthetic-binding", binding_generation=1)


def stamp():
    return dict(authority_instance="synthetic-authority", authority_epoch=1, incarnation="synthetic-run",
                base_recovery_sequence=0, base_checkpoint=reference("recovery-checkpoint"))


def json_evidence():
    raw = b'{"synthetic":"material"}'
    return dict(contract_ref="unqualified-synthetic-contract", contract_sha256="c" * 64,
                canonical_utf8=raw.decode(), content_sha256=hashlib.sha256(raw).hexdigest(), source_evidence=evidence())


def material():
    s = subject_body()
    sc = scope(task_id="synthetic-task")
    target = json_evidence()
    payload = json_evidence()
    return dict(subject=s, subject_id=legacy.subject(s).subject_id, scope=sc,
                scope_sha256=hashlib.sha256(m.canonical_bytes(sc)).hexdigest(), requested_action="read",
                operations=["read"], targets=target, dispatch_payload=payload,
                effect_summary=dict(operations=["read"], targets_sha256=target["content_sha256"]),
                effect_explanation="Synthetic untrusted material only.",
                dispatch_material_sha256=m.domain_digest(m.PREFIX + "dispatch-material.v1", payload),
                source_evidence=[evidence()])


def facts():
    return [dict(kind=k, verdict="PASS", observed_at_ms=1000, valid_until_ms=20000,
                 source_evidence=evidence()) for k in m.GATE_KINDS]


def revocation_read():
    return dict(grant=reference("grant", True), index_generation=1, read_at_ms=1000, revocations=[])


def samples():
    mat = material()
    proposal = m.PREFIX + "proposal-material.v1:" + m.domain_digest(m.PREFIX + "proposal-material.v1", mat)
    base = dict(stamp=stamp())
    challenge = dict(base, schema_version=m.PREFIX + "authority-challenge.v1", binding=binding(), material=mat,
                     proposal_id=proposal, nonce="c" * 64, issued_at_ms=1000, expires_at_ms=301000)
    view = dict(base, schema_version=m.PREFIX + "presentation-view.v1", challenge=reference("authority-challenge"),
                owner_context=context(), view_key="synthetic-view", template_revision="d" * 64,
                render_evidence=evidence(), presentation_sha256="e" * 64, issued_at_ms=1000, expires_at_ms=20000)
    decision = dict(base, schema_version=m.PREFIX + "owner-decision.v1", challenge=reference("authority-challenge"),
                    view=reference("presentation-view"), binding=binding(), owner_context=context(), proposal_id=proposal,
                    nonce="c" * 64, presentation_sha256="e" * 64, decision="CONFIRM", observed_at_ms=1001, origin_evidence=evidence())
    receipt = dict(base, schema_version=m.PREFIX + "trusted-decision-receipt.v1", challenge=reference("authority-challenge"),
                   view=reference("presentation-view"), owner_decision=reference("owner-decision"), binding=binding(),
                   owner_context=context(), proposal_id=proposal, nonce="c" * 64, presentation_sha256="e" * 64,
                   decision="CONFIRM", accepted_at_ms=1001, confirmation_expires_at_ms=20000,
                   legacy_time_basis="UNIX_MS", provenance_evidence=[evidence()])
    intent = dict(base, schema_version=m.PREFIX + "admission-intent.v1", receipt=reference("trusted-decision-receipt"),
                  challenge=reference("authority-challenge"), binding=binding(), owner_context=context(), proposal_id=proposal,
                  subject_id=mat["subject_id"], scope_sha256=mat["scope_sha256"], dispatch_material_sha256=mat["dispatch_material_sha256"],
                  grant=reference("grant", True), revocation_read=revocation_read(), gate_facts=facts(), disposition="ADMIT_PENDING",
                  reason_codes=["INTENT_PENDING"], evaluated_at_ms=1001, use_until_ms=20000,
                  executor_environment="synthetic-executor", intent_key="synthetic-intent")
    claim = dict(base, schema_version=m.PREFIX + "dispatch-attempt.v1", phase="CLAIM", attempt_key="synthetic-attempt",
                 intent=reference("admission-intent"), grant=reference("grant", True), dispatch_material_sha256=mat["dispatch_material_sha256"],
                 claimed_at_ms=1001, handoff_until_ms=20000, gate_facts=facts(), revocation_read=revocation_read(),
                 executor_environment="synthetic-executor")
    result = dict(base, schema_version=m.PREFIX + "dispatch-attempt.v1", phase="RESULT", attempt_key="synthetic-attempt",
                  intent=reference("admission-intent"), grant=reference("grant", True), dispatch_material_sha256=mat["dispatch_material_sha256"],
                  claim=reference("dispatch-attempt"), observed_at_ms=20001, outcome="UNKNOWN", outcome_evidence=[])
    checkpoint = dict(schema_version=m.PREFIX + "recovery-checkpoint.v1", authority_instance="synthetic-authority",
                      authority_epoch=1, incarnation="synthetic-run", recovery_sequence=0, previous_checkpoint=None,
                      transition_kind="GENESIS", record_refs=[], ledger_commit_sha256="e" * 64, time_high_water_ms=1000)
    return [challenge, view, decision, receipt, intent, claim, result, checkpoint]


class ProductionMetadataTests(unittest.TestCase):
    def setUp(self):
        self.rows = samples()

    def parse(self, body):
        return m.parse_metadata(m.canonical_bytes(body))

    def reject(self, body):
        with self.assertRaises(m.MetadataError) as error:
            self.parse(body)
        self.assertEqual(str(error.exception), "G3_PRODUCTION_METADATA_INVALID")

    def test_all_seven_domains_and_both_dispatch_variants_untrusted(self):
        self.assertEqual(len(m.DOMAINS), 7)
        for body in self.rows:
            with self.subTest(schema=body["schema_version"], phase=body.get("phase")):
                item = self.parse(body)
                self.assertEqual(item.to_dict(), body)
                self.assertEqual(item.basis, "OFFLINE_UNTRUSTED_METADATA")
                self.assertEqual(item.authority, "NONE")
                self.assertEqual(item.semantic_validation, "NOT_PERFORMED")

    def test_unknown_outer_fields_every_variant(self):
        for body in self.rows:
            self.reject(dict(body, fixture=1))

    def test_missing_outer_fields_every_variant(self):
        for body in self.rows:
            for key in body:
                row = copy.deepcopy(body)
                del row[key]
                self.reject(row)

    def test_unknown_versions_and_legacy_decision_not_cast(self):
        for version in ("nexus.g3.eligibility-decision.v1", m.PREFIX + "production-eligibility-decision.v1",
                        m.PREFIX + "owner-decision.v2", "", None, 1):
            self.reject(dict(self.rows[2], schema_version=version))

    def test_dispatch_variants_are_closed(self):
        for variant in ("CONFIRM", "claim", None, []):
            self.reject(dict(self.rows[5], phase=variant))
        self.reject(dict(self.rows[5], outcome="COMPLETED"))
        self.reject(dict(self.rows[6], claimed_at_ms=1001))

    def test_duplicate_key_and_nested_duplicate(self):
        for raw in (b'{"schema_version":1,"schema_version":2}', b'{"owner":{"subject":"a","subject":"b"}}'):
            with self.assertRaises(m.MetadataError):
                m.parse_json(raw)

    def test_utf8_bom_surrogates_and_raw_type(self):
        for raw in (b'\xef\xbb\xbf{}', b'\xff', b'"\\ud800"', b'', bytearray(b'{}'), '{}'):
            with self.assertRaises(m.MetadataError):
                m.parse_json(raw)

    def test_non_json_and_scalar_types(self):
        for value in (True, False, -1, 1.1, float("nan"), float("inf"), 2**63, (), set(), object()):
            with self.assertRaises(m.MetadataError):
                m.canonical_bytes({"value": value})

    def test_nfc_control_bidi_and_empty_key(self):
        for value in ("e\u0301", "a\x00b", "a\nb", "a\x7fb", "a\u202eb"):
            with self.assertRaises(m.MetadataError):
                m.canonical_bytes({"x": value})
        with self.assertRaises(m.MetadataError):
            m.canonical_bytes({"": 1})

    def test_depth_members_bytes_and_cycles(self):
        deep = 1
        for _ in range(13):
            deep = [deep]
        cyc = []
        cyc.append(cyc)
        for value in (deep, cyc, list(range(65)), {str(i): i for i in range(65)}, ["x" * 16384] * 5):
            with self.assertRaises(m.MetadataError):
                m.canonical_bytes(value)

    def test_node_limit(self):
        with self.assertRaises(m.MetadataError):
            m.canonical_bytes([[[0]*64 for _ in range(64)] for _ in range(4)])

    def test_canonical_order_utf8_and_detached_copy(self):
        self.assertEqual(m.canonical_bytes({"z": 2, "a": "中文"}), '{"a":"中文","z":2}'.encode())
        item = self.parse(self.rows[2])
        detached = item.to_dict()
        detached["decision"] = "DENY"
        self.assertEqual(item.to_dict()["decision"], "CONFIRM")

    def test_hash_domain_separation_and_exact_formula(self):
        row = self.rows[2]
        parsed = self.parse(row)
        raw = m.canonical_bytes(row)
        expected = hashlib.sha256(row["schema_version"].encode()+b'\0'+raw).hexdigest()
        self.assertEqual(parsed.record_id, row["schema_version"]+":"+expected)
        self.assertEqual(parsed.body_sha256, hashlib.sha256(raw).hexdigest())
        self.assertNotEqual(expected, parsed.body_sha256)
        self.assertNotEqual(m.domain_digest(next(iter(m.DOMAINS)), {"x": 1}), m.domain_digest(m.PREFIX+"ledger-commit.v1", {"x": 1}))
        with self.assertRaises(m.MetadataError):
            m.domain_digest("executor-selected-domain", row)

    def test_wrong_typed_refs_and_hashes(self):
        for ref in (reference("owner-decision"), {"id": "a"*64, "body_sha256": "b"*64},
                    dict(reference("authority-challenge"), body_sha256="B"*64), None):
            self.reject(dict(self.rows[2], challenge=ref))

    def test_unknown_nested_fields(self):
        for key in ("stamp", "binding", "owner_context", "origin_evidence"):
            body = copy.deepcopy(self.rows[2])
            body[key]["executor_override"] = 1
            self.reject(body)
        row = copy.deepcopy(self.rows[2])
        row["binding"]["owner"]["email"] = "synthetic@example.invalid"
        self.reject(row)

    def test_principal_is_structural_not_authentication(self):
        row = copy.deepcopy(self.rows[2])
        row["binding"]["owner"]["issuer"] = "unqualified-issuer-label"
        self.assertEqual(self.parse(row).authority, "NONE")
        row["binding"]["owner"]["subject"] = "x"*513
        self.reject(row)

    def test_context_bound_and_generation_type(self):
        for start, end in ((1000, 1000), (1000, 301001), (1000, True)):
            row = copy.deepcopy(self.rows[2])
            row["owner_context"].update(authenticated_at_ms=start, context_expires_at_ms=end)
            self.reject(row)
        row = copy.deepcopy(self.rows[2])
        row["binding"]["owner_generation"] = 0
        self.reject(row)

    def test_challenge_lifetime_nonce_and_material_join(self):
        self.reject(dict(self.rows[0], expires_at_ms=301001))
        self.reject(dict(self.rows[0], nonce="short"))
        row = copy.deepcopy(self.rows[0])
        row["material"]["requested_action"] = "write"
        self.reject(row)

    def test_scope_subject_and_effect_substitutions(self):
        for path, value in (("subject_id", "nexus.g3.subject.v1:"+"f"*64), ("scope_sha256", "f"*64),
                            ("operations", ["write"]), ("dispatch_material_sha256", "f"*64)):
            row = copy.deepcopy(self.rows[0])
            row["material"][path] = value
            self.reject(row)
        row = copy.deepcopy(self.rows[0])
        row["material"]["effect_summary"]["targets_sha256"] = "f"*64
        self.reject(row)

    def test_payload_canonical_hash_and_no_dynamic_contract_resolution(self):
        row = copy.deepcopy(self.rows[0])
        row["material"]["targets"]["canonical_utf8"] = '{ "synthetic": "material" }'
        self.reject(row)
        row = copy.deepcopy(self.rows[0])
        row["material"]["dispatch_payload"]["content_sha256"] = "f"*64
        self.reject(row)
        self.assertEqual(self.parse(self.rows[0]).semantic_validation, "NOT_PERFORMED")

    def test_proposal_digest_mismatch_and_optional_null(self):
        self.reject(dict(self.rows[0], proposal_id=m.PREFIX+"proposal-material.v1:"+"f"*64))
        self.reject(dict(self.rows[0], host_proposal=None))

    def test_optional_host_body_must_be_closed_and_bound(self):
        row = copy.deepcopy(self.rows[0])
        row["host_proposal"] = dict(body={}, proposal_id="nexus.g3.host-approval-proposal.v1:"+"a"*64)
        self.reject(row)
        self.assertEqual(self.parse(self.rows[0]).authority, "NONE")

    def test_within_body_context_and_gate_time_joins(self):
        self.reject(dict(self.rows[2], observed_at_ms=999))
        self.reject(dict(self.rows[2], observed_at_ms=301000))
        self.reject(dict(self.rows[3], accepted_at_ms=999))
        row = copy.deepcopy(self.rows[4])
        row["gate_facts"][0]["valid_until_ms"] = 1001
        self.reject(row)
        row = copy.deepcopy(self.rows[5])
        row["gate_facts"][0]["observed_at_ms"] = 1002
        self.reject(row)

    def test_decision_closed_enum_and_receipt_clock(self):
        for decision in ("APPROVE", "accept", True, None):
            self.reject(dict(self.rows[2], decision=decision))
        self.reject(dict(self.rows[3], legacy_time_basis="SECONDS"))
        self.reject(dict(self.rows[3], confirmation_expires_at_ms=301001))

    def test_evidence_order_uniqueness_and_secret_field(self):
        for refs in ([evidence("z"), evidence("a")], [evidence(), evidence()], []):
            self.reject(dict(self.rows[3], provenance_evidence=refs))
        row = copy.deepcopy(self.rows[3])
        row["owner_context"]["session_evidence"]["session_token"] = "synthetic-forbidden-field"
        self.reject(row)

    def test_eight_gates_order_and_positive_shape_not_authority(self):
        for rows in (facts()[:-1], list(reversed(facts()))):
            self.reject(dict(self.rows[4], gate_facts=rows))
        rows = facts()
        rows[0]["verdict"] = "UNKNOWN"
        self.reject(dict(self.rows[4], gate_facts=rows))
        self.assertEqual(self.parse(self.rows[4]).authority, "NONE")

    def test_intent_null_parity_denial_and_deadlines(self):
        self.reject(dict(self.rows[4], grant=None))
        self.reject(dict(self.rows[4], use_until_ms=61002))
        denial = dict(self.rows[4], disposition="DENIED", grant=None, revocation_read=None,
                      reason_codes=["ORIGIN_UNVERIFIED"], use_until_ms=1001)
        self.assertEqual(self.parse(denial).authority, "NONE")
        self.reject(dict(denial, reason_codes=["COMPLETED"]))
        self.reject(dict(denial, reason_codes=["UNRECOGNIZED_REASON"]))

    def test_revocation_read_mismatch_and_duplicate(self):
        row = copy.deepcopy(self.rows[5])
        row["revocation_read"]["grant"]["id"] = "nexus.g3.grant.v1:"+"f"*64
        self.reject(row)
        row = copy.deepcopy(self.rows[5])
        row["revocation_read"]["revocations"] = [reference("revocation", True)]*2
        self.reject(row)

    def test_unknown_outcome_never_claimable(self):
        self.assertEqual(self.parse(self.rows[6]).authority, "NONE")
        self.reject(dict(self.rows[6], outcome="COMPLETED"))
        self.reject(dict(self.rows[6], outcome="RETRY"))
        self.reject(dict(self.rows[5], handoff_until_ms=1001))

    def test_checkpoint_genesis_sequence_and_previous(self):
        self.reject(dict(self.rows[7], previous_checkpoint=reference("recovery-checkpoint")))
        self.reject(dict(self.rows[7], recovery_sequence=1))
        next_row = dict(self.rows[7], recovery_sequence=1, previous_checkpoint=reference("recovery-checkpoint"), transition_kind="RECOVER")
        self.assertEqual(self.parse(next_row).semantic_validation, "NOT_PERFORMED")
        # A predecessor relationship and real recovery ceremony are not inferred.
        self.reject(dict(next_row, previous_checkpoint=None))

    def test_checkpoint_ref_domains_and_duplicates(self):
        self.reject(dict(self.rows[7], record_refs=[reference("subject", True)]))
        self.reject(dict(self.rows[7], record_refs=[reference("grant", True)]*2))
        self.assertEqual(self.parse(dict(self.rows[7], record_refs=[reference("grant", True)])).authority, "NONE")

    def test_no_public_consumer_no_io_and_no_fixture_import(self):
        source = ROOT / "scripts/g3_production_metadata.py"
        tree = ast.parse(source.read_text(encoding="utf-8"))
        imports = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
        modules = [n.module or "" for n in imports if isinstance(n, ast.ImportFrom)]
        modules += [name.name for n in imports if isinstance(n, ast.Import) for name in n.names]
        self.assertFalse(any(x.split('.')[0] in {"tests", "requests", "httpx", "boto3", "stytch", "socket", "os", "subprocess"} for x in modules))
        for path in (ROOT/"ash").glob("*.py"):
            if path != source:
                self.assertNotIn("g3_production_metadata", path.read_text(encoding="utf-8"), str(path))
        self.assertFalse(hasattr(m, "admit"))
        self.assertFalse(hasattr(m, "dispatch"))


class ManifestRuleRegressionTests(unittest.TestCase):
    def test_sensitive_paths_excluded_by_both_unchanged_tools(self):
        loaded = {}
        for name in ("build_manifest", "package_nexus"):
            spec = importlib.util.spec_from_file_location(name, ROOT/f"scripts/{name}.py")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            loaded[name] = module
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paths = [f"tests/example-{name}.md" for name in ("SESSION", "oauth", "token", "cookie", "credential", "private_key")]
            paths += ["tests/ordinary.md"]
            for name in paths:
                path = root/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("synthetic plain documentation", encoding="utf-8")
            _, entries = loaded["build_manifest"].build_manifest_bytes(root=root)
            self.assertIn("tests/ordinary.md", entries)
            self.assertTrue(loaded["package_nexus"]._allowed_relative(PurePosixPath("tests/ordinary.md")))
            for name in paths[:-1]:
                self.assertNotIn(name, entries)
                self.assertFalse(loaded["package_nexus"]._allowed_relative(PurePosixPath(name)))


if __name__ == "__main__":
    unittest.main()

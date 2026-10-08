"""Adversarial offline models; no login, cloud resources, grants or effects."""
from dataclasses import replace
from pathlib import Path
import ast
import unittest
from unittest.mock import patch

from scripts import g3_offline_control as m


def ref(kind):
    prefix = "nexus.g3." if kind in ("grant","revocation") else "nexus.g3.production."
    return dict(id=prefix+kind+".v1:"+"a"*64,body_sha256="b"*64)


def sample(family):
    """One shape vector per documented family; never claimed authentic."""
    _, _, spec = m.SPECS[family]
    value = dict(schema_version=m.VERSION,family=family,revision=1)
    for item in spec.split():
        field, desc = item.split(":",1)
        if desc.startswith("?"):
            v = None
        elif "|" in desc or desc == "WITNESSED":
            v = desc.split("|")[0]
        elif desc == "t": v = "test-"+field.replace("_","-")
        elif desc == "s": v = "synthetic"
        elif desc == "h": v = "a"*64
        elif desc in ("u","g"): v = 1
        elif desc == "p": v = dict(issuer="test-only:issuer",client_id="test-only:client",subject="test-only:owner")
        elif desc == "e": v = dict(ref="test-only:evidence",sha256="a"*64)
        elif desc.startswith("r:"): v = ref(desc[2:])
        elif desc.startswith("l:"): v = []
        else: raise AssertionError(desc)
        value[field] = v
    if family == "root":
        value.update(recovery_sequence=0,time_high_water_ms=0)
    if family == "context": value.update(authenticated_at_ms=1000,expires_at_ms=301000)
    if family == "source": value.update(observed_at_ms=1000,expires_at_ms=301000)
    if family == "revocation": value.update(index_id="authority",state="INDEX")
    return value


def ready(intent=True, claim=False):
    a = m.FakeAuthorityModel()
    a.transact("CONFIRM",evidence=m.FakeSessionEvidence())
    a.transact("GRANT_MODEL",evidence=m.FakeSessionEvidence())
    if intent: a.transact("INTENT_MODEL",evidence=m.FakeSessionEvidence(),material=a.material)
    if claim: a.transact("CLAIM_MODEL",evidence=m.FakeSessionEvidence(),material=a.material)
    return a


class ClosedEncodingTests(unittest.TestCase):
    def test_all_sixteen_closed_families(self):
        self.assertEqual(len(m.SPECS),16)
        for family in m.SPECS:
            with self.subTest(family=family):
                row=m.ControlRow.from_value(sample(family))
                self.assertEqual(row.authority,"NONE")
                self.assertEqual(m.decode(row.value),sample(family))

    def test_unknown_field_every_family(self):
        for family in m.SPECS:
            with self.subTest(family=family):
                value=sample(family);value["extra"]="caller"
                with self.assertRaises(m.OfflineError): m.ControlRow.from_value(value)

    def test_missing_field_every_family(self):
        for family in m.SPECS:
            with self.subTest(family=family):
                value=sample(family);del value["revision"]
                with self.assertRaises(m.OfflineError): m.ControlRow.from_value(value)

    def test_unknown_version_and_family(self):
        for field,value in (("schema_version","nexus.g3.n01-control.v2"),("family","arbitrary")):
            body=sample("root");body[field]=value
            with self.assertRaises(m.OfflineError): m.ControlRow.from_value(body)

    def test_wrong_key_and_namespace(self):
        row=m.ControlRow.from_value(sample("root"))
        for changes in (dict(key="root:other"),dict(namespace="bindings")):
            with self.assertRaises(m.OfflineError): replace(row,**changes)

    def test_boolean_float_negative_overflow(self):
        for value in (True,1.0,-1,2**63):
            body=sample("root");body["authority_epoch"]=value
            with self.assertRaises(m.OfflineError): m.ControlRow.from_value(body)

    def test_noncanonical_duplicate_and_bom(self):
        for raw in (b'{"x":1, "y":2}',b'{"x":1,"x":2}',b'\xef\xbb\xbf{}'):
            with self.assertRaises(m.OfflineError): m.decode(raw)

    def test_wrong_record_kind(self):
        body=sample("challenge");body["record_ref"]=ref("dispatch-attempt")
        with self.assertRaises(m.OfflineError): m.ControlRow.from_value(body)

    def test_invalid_context_bounds(self):
        for expiry in (1000,301001):
            body=sample("context");body["expires_at_ms"]=expiry
            with self.assertRaises(m.OfflineError): m.ControlRow.from_value(body)

    def test_no_secret_fields(self):
        for name in ("session_token","session_jwt","secret","cookie"):
            body=sample("context");body[name]="synthetic-forbidden"
            with self.assertRaises(m.OfflineError): m.ControlRow.from_value(body)

    def test_revocation_header_and_consumed_nonce(self):
        body=sample("revocation");body["index_id"]="wrong"
        with self.assertRaises(m.OfflineError): m.ControlRow.from_value(body)
        body=sample("nonce");body["state"]="CONSUMED"
        with self.assertRaises(m.OfflineError): m.ControlRow.from_value(body)

    def test_root_null_predecessor_only_genesis(self):
        body=sample("root");body["recovery_sequence"]=1
        with self.assertRaises(m.OfflineError): m.ControlRow.from_value(body)

    def test_deterministic_snapshot_order_and_coverage(self):
        root=sample("root");root.update(recovery_sequence=2,previous_checkpoint=ref("recovery-checkpoint"))
        rows=tuple(m.ControlRow.from_value(root if f=="root" else sample(f)) for f in m.SPECS)
        first=m.encode_snapshot(rows);second=m.encode_snapshot(tuple(reversed(rows)))
        self.assertEqual(first,second)
        header=m.decode(first.root)
        self.assertEqual(header["inventory"],list(m.NAMESPACES))
        self.assertEqual(sum(p["row_count"] for p in header["pages"]),16)
        for page,reference in zip(first.pages,header["pages"]):
            self.assertEqual(m.digest(page),reference["page_sha256"])
            for row in m.decode(page)["rows"]:
                self.assertEqual(m.digest(row["value_canonical_utf8"].encode()),row["value_sha256"])

    def test_no_root_duplicate_or_self_checkpoint(self):
        root=m.ControlRow.from_value(sample("root"))
        recovery=m.ControlRow.from_value(sample("recovery"))
        for rows in ((root,root),(recovery,),(root,recovery)):
            with self.assertRaises(m.OfflineError): m.encode_snapshot(rows)

    def test_page_rollover_preserves_all_rows(self):
        rows=[m.ControlRow.from_value(sample("root"))]
        for i in range(130):
            body=sample("nonce");body["nonce"]=f'{i:064x}'
            rows.append(m.ControlRow.from_value(body))
        snapshot=m.encode_snapshot(tuple(rows));header=m.decode(snapshot.root)
        refs=[p for p in header["pages"] if p["namespace"]=="nonce_consumption"]
        self.assertEqual([p["row_count"] for p in refs],[64,64,2])
        self.assertEqual(set(m.verify_snapshot(snapshot)),set(rows))

    def test_capacity_denies_without_truncation(self):
        root=m.ControlRow.from_value(sample("root"))
        with self.assertRaises(m.OfflineError): m.encode_snapshot((root,)*4097)

    def test_snapshot_corrupt_or_missing_page(self):
        snapshot=m.encode_snapshot((m.ControlRow.from_value(sample("root")),))
        for bad in (replace(snapshot,pages=()),replace(snapshot,pages=(b'{}',)),
                    replace(snapshot,pages=snapshot.pages*2)):
            with self.assertRaises(m.OfflineError): m.verify_snapshot(bad)

    def test_snapshot_namespace_omission_and_header_mismatch(self):
        snapshot=m.encode_snapshot((m.ControlRow.from_value(sample("root")),))
        for change in (dict(inventory=list(m.NAMESPACES)[1:]),dict(authority_epoch=2)):
            header=m.decode(snapshot.root);header.update(change)
            with self.assertRaises(m.OfflineError): m.verify_snapshot(replace(snapshot,root=m.canonical(header)))

    def test_valid_hash_cannot_hide_changed_row(self):
        snapshot=m.encode_snapshot((m.ControlRow.from_value(sample("root")),))
        page=m.decode(snapshot.pages[0]);page["rows"][0]["value_sha256"]="0"*64
        raw=m.canonical(page);header=m.decode(snapshot.root);header["pages"][0]["page_sha256"]=m.digest(raw)
        with self.assertRaises(m.OfflineError): m.verify_snapshot(m.EncodedSnapshot(m.canonical(header),(raw,)))


class SyntheticContractTests(unittest.TestCase):
    def test_reference_only_observation(self):
        a=ready(claim=True)
        self.assertEqual(a.handoff_observation(a.material,now=1000),(m.BASIS,m.digest(a.material.payload)))
        self.assertEqual(a.authority,"NONE")

    def test_wrong_contract_revision(self):
        a=ready()
        with self.assertRaises(m.OfflineError): a.transact("CLAIM_MODEL",evidence=m.FakeSessionEvidence(),material=replace(a.material,target_revision="other"))

    def test_wrong_dispatch_contract_revision(self):
        material=replace(m.reference_material(),dispatch_revision="other")
        with self.assertRaises(m.OfflineError): material.validate()

    def test_wrong_adapter_revision(self):
        a=ready()
        with self.assertRaises(m.OfflineError): a.transact("CLAIM_MODEL",evidence=m.FakeSessionEvidence(),material=replace(a.material,adapter_revision="other"))

    def test_changed_target_bytes(self):
        a=ready();different=m.reference_material("changed")
        with self.assertRaises(m.OfflineError): a.transact("CLAIM_MODEL",evidence=m.FakeSessionEvidence(),material=different)

    def test_changed_dispatch_payload(self):
        a=ready();material=replace(a.material,payload=m.canonical(dict(operation="echo",arguments=["changed"])))
        with self.assertRaises(m.OfflineError): a.transact("CLAIM_MODEL",evidence=m.FakeSessionEvidence(),material=material)

    def test_stale_environment_registration(self):
        a=ready()
        for changes in (dict(environment_generation=2),dict(environment="production"),dict(environment_generation=True)):
            with self.assertRaises(m.OfflineError): a.transact("CLAIM_MODEL",evidence=m.FakeSessionEvidence(),material=replace(a.material,**changes))

    def test_arbitrary_operation_hidden_fields_indirection(self):
        material=m.reference_material()
        for payload in (dict(operation="shell",arguments=["synthetic"]),dict(operation="echo",arguments=["synthetic"],env="hidden")):
            with self.assertRaises(m.OfflineError): replace(material,payload=m.canonical(payload)).validate()
        target=dict(resource="https://mutable.invalid",content="synthetic")
        with self.assertRaises(m.OfflineError): replace(material,target=m.canonical(target)).validate()

    def test_oversize_and_non_nfc_denied(self):
        for value in ("a"*257,"e\u0301"):
            with self.assertRaises(m.OfflineError): m.reference_material(value)


class AdversarialStateTests(unittest.TestCase):
    def test_stale_owner_context(self):
        a=ready()
        with self.assertRaises(m.OfflineError): a.transact("CLAIM_MODEL",now=301000,evidence=m.FakeSessionEvidence(observed_at_ms=301000),material=a.material)
        self.assertEqual(a.state.claim,"NONE")

    def test_reused_nonce(self):
        a=m.FakeAuthorityModel();a.transact("DENY",evidence=m.FakeSessionEvidence())
        with self.assertRaises(m.OfflineError): a.transact("CONFIRM",evidence=m.FakeSessionEvidence())
        self.assertEqual(a.state.decision,"DENY")

    def test_duplicate_confirm(self):
        a=ready(False)
        with self.assertRaises(m.OfflineError): a.transact("CONFIRM",evidence=m.FakeSessionEvidence())

    def test_conflicting_confirm_deny(self):
        a=ready(False)
        with self.assertRaises(m.OfflineError): a.transact("DENY",evidence=m.FakeSessionEvidence())
        self.assertEqual(a.state.decision,"CONFIRM")

    def test_duplicate_grant_provenance(self):
        a=ready(False)
        with self.assertRaises(m.OfflineError): a.transact("GRANT_MODEL",evidence=m.FakeSessionEvidence())

    def test_incomplete_revocation_index(self):
        for already_intent in (False,True):
            a=ready(already_intent);a.transact("INCOMPLETE_INDEX_TEST")
            with self.assertRaises(m.OfflineError): a.transact("CLAIM_MODEL" if already_intent else "INTENT_MODEL",evidence=m.FakeSessionEvidence(),material=a.material)

    def test_revoke_before_intent(self):
        a=ready(False);a.transact("REVOKE_MODEL")
        with self.assertRaises(m.OfflineError): a.transact("INTENT_MODEL",evidence=m.FakeSessionEvidence(),material=a.material)

    def test_revoke_after_intent_before_claim(self):
        a=ready();a.transact("REVOKE_MODEL")
        with self.assertRaises(m.OfflineError): a.transact("CLAIM_MODEL",evidence=m.FakeSessionEvidence(),material=a.material)

    def test_duplicate_claim(self):
        a=ready(claim=True)
        with self.assertRaises(m.OfflineError): a.transact("CLAIM_MODEL",evidence=m.FakeSessionEvidence(),material=a.material)
        self.assertEqual(a.state.grant,"TEST_CONSUMED")

    def test_crash_before_fence(self):
        a=ready();a.prepare("CLAIM_MODEL",evidence=m.FakeSessionEvidence(),material=a.material);a.crash()
        with self.assertRaises(m.OfflineError): a.finalize()
        with self.assertRaises(m.OfflineError): a.handoff_observation(a.material,now=1000)
        with self.assertRaises(m.OfflineError): a.recover_for_test()

    def test_crash_after_fence_before_ack(self):
        a=ready();a.prepare("CLAIM_MODEL",evidence=m.FakeSessionEvidence(),material=a.material);a.witness();a.crash()
        with self.assertRaises(m.OfflineError): a.handoff_observation(a.material,now=1000)
        a.recover_for_test()
        self.assertEqual(a.state.result,"UNKNOWN")
        self.assertEqual(a.state.context_state,"RETIRED")
        self.assertEqual(a.state.grant,"TEST_CONSUMED")
        with self.assertRaises(m.OfflineError): a.transact("CLAIM_MODEL",evidence=m.FakeSessionEvidence(),material=a.material)

    def test_rollback_old_control_snapshot(self):
        a=ready();old_state,old_head=a.state,a.head
        a.transact("REVOKE_MODEL");a.restored_for_test(old_state,old_head)
        with self.assertRaises(m.OfflineError): a.check_restore()
        with self.assertRaises(m.OfflineError): a.recover_for_test()

    def test_forked_checkpoint(self):
        a=ready();tail=a.fence.history[-1]
        a.fence.history=a.fence.history[:-1]+(replace(tail,previous="0"*64),)
        with self.assertRaises(m.OfflineError): a.transact("CLAIM_MODEL",evidence=m.FakeSessionEvidence(),material=a.material)
        self.assertTrue(a.closed)

    def test_missing_checkpoint_gap(self):
        a=ready();a.fence.history=a.fence.history[:1]+a.fence.history[2:]
        with self.assertRaises(m.OfflineError): a.check_restore()

    def test_result_unknown(self):
        a=ready(claim=True);a.transact("RESULT_MODEL",result="UNKNOWN")
        self.assertEqual(a.state.result,"UNKNOWN")
        with self.assertRaises(m.OfflineError): a.handoff_observation(a.material,now=1000)
        with self.assertRaises(m.OfflineError): a.transact("RESULT_MODEL",result="SUCCEEDED")

    def test_redispatch_attempt(self):
        a=ready(claim=True);a.handoff_observation(a.material,now=1000)
        with self.assertRaises(m.OfflineError): a.handoff_observation(a.material,now=1000)

    def test_fake_adapter_production_promotion(self):
        a=ready(claim=True)
        with self.assertRaisesRegex(m.OfflineError,"PROMOTION_FORBIDDEN"): a.promote_to_production()
        self.assertEqual(a.authority,"NONE")

    def test_finalize_without_witness(self):
        a=ready();a.prepare("CLAIM_MODEL",evidence=m.FakeSessionEvidence(),material=a.material)
        with self.assertRaises(m.OfflineError): a.finalize()
        self.assertTrue(a.closed)

    def test_duplicate_witness(self):
        a=ready();a.prepare("CLAIM_MODEL",evidence=m.FakeSessionEvidence(),material=a.material);a.witness()
        with self.assertRaises(m.OfflineError): a.witness()
        self.assertTrue(a.closed)

    def test_stale_cas_and_pending_transition_exclusion(self):
        a=ready()
        with self.assertRaises(m.OfflineError): a.prepare("REVOKE_MODEL",expected_sequence=0)
        a.prepare("REVOKE_MODEL")
        with self.assertRaises(m.OfflineError): a.prepare("CLAIM_MODEL",evidence=m.FakeSessionEvidence(),material=a.material)

    def test_local_invalidation(self):
        a=ready();a.transact("INVALIDATE_MODEL")
        with self.assertRaises(m.OfflineError): a.transact("CLAIM_MODEL",evidence=m.FakeSessionEvidence(),material=a.material)

    def test_wrong_principal_session_and_stale_remote_proof(self):
        a=ready()
        for evidence in (m.FakeSessionEvidence(principal="other"),m.FakeSessionEvidence(session="other"),
                         m.FakeSessionEvidence(observed_at_ms=999),m.FakeSessionEvidence(verdict="UNKNOWN")):
            with self.assertRaises(m.OfflineError): a.transact("CLAIM_MODEL",evidence=evidence,material=a.material)

    def test_time_regression_and_expired_handoff(self):
        a=ready(claim=True)
        with self.assertRaises(m.OfflineError): a.transact("RESULT_MODEL",now=999,result="UNKNOWN")
        with self.assertRaises(m.OfflineError): a.handoff_observation(a.material,now=2000)

    def test_restart_matching_snapshot_still_retires(self):
        a=ready();a.restored_for_test(a.state,a.head)
        with self.assertRaises(m.OfflineError): a.check_restore()
        a.recover_for_test();self.assertEqual(a.state.context_state,"RETIRED")
        self.assertEqual(a.state.intent,"TEST_RETIRED")
        self.assertEqual(a.state.nonce_state,"CONSUMED")
        self.assertEqual(a.state.epoch,2)

    def test_revoke_after_claim_preserves_consumption(self):
        a=ready(claim=True);a.transact("REVOKE_MODEL")
        self.assertEqual(a.state.claim,"TEST_CLAIMED")
        with self.assertRaises(m.OfflineError): a.handoff_observation(a.material,now=1000)

    def test_crash_after_finalize_preserves_unknown_consumption(self):
        a=ready(claim=True);a.crash();a.recover_for_test()
        self.assertEqual(a.state.result,"UNKNOWN")
        with self.assertRaises(m.OfflineError): a.transact("CLAIM_MODEL",evidence=m.FakeSessionEvidence(),material=a.material)

    def test_no_io_or_runtime_consumer(self):
        with patch("builtins.open",side_effect=AssertionError("filesystem")), \
             patch("os.getenv",side_effect=AssertionError("environment")), \
             patch("urllib.request.urlopen",side_effect=AssertionError("network")):
            a=ready(claim=True);a.handoff_observation(a.material,now=1000)
            m.encode_snapshot((m.ControlRow.from_value(sample("root")),))
        root=Path(m.__file__).resolve().parents[1]
        for path in (root/"ash").rglob("*.py"):
            self.assertNotIn("g3_offline_control",path.read_text(encoding="utf-8"))
        tree=ast.parse(Path(m.__file__).read_text(encoding="utf-8"))
        forbidden={"requests","urllib","boto3","stytch","socket","os","subprocess","pathlib"}
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):
                self.assertFalse(any(n.name.split('.')[0] in forbidden for n in node.names))
            elif isinstance(node,ast.ImportFrom):
                self.assertNotIn((node.module or '').split('.')[0],forbidden)


if __name__=="__main__":
    unittest.main()

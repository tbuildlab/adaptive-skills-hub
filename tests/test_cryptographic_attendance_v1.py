"""Synthetic ES256 unit/attack-model tests; no actual Owner or input ceremony."""
from pathlib import Path
import copy
import hashlib
import json
import tempfile
import unittest
from unittest.mock import patch

from prototypes import cryptographic_attendance_v1 as p


class FakeAuthenticator:
    """Known non-secret test scalar; NOT an enrolled/protected Owner credential."""
    def __init__(self, scalar=1):
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives import serialization
        self._key = ec.derive_private_key(scalar, ec.SECP256R1())
        point = self._key.public_key().public_bytes(serialization.Encoding.X962,
                                                   serialization.PublicFormat.UncompressedPoint)
        self.binding = p.PublicBinding(b"synthetic-unit-id", point)

    def assertion(self, c, *, flags=5, counter=1, client_changes=None, rp=None):
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives import hashes
        client = {"type": "webauthn.get", "challenge": p.b64(p.canonical(c)),
                  "origin": c["policy"]["origin"], "crossOrigin": False}
        client.update(client_changes or {})
        raw = p.canonical(client)
        auth = hashlib.sha256((rp or c["policy"]["rp_id"]).encode()).digest()
        auth += bytes([flags]) + counter.to_bytes(4, "big")
        signed = auth + hashlib.sha256(raw).digest()
        signature = self._key.sign(signed, ec.ECDSA(hashes.SHA256(), deterministic_signing=True))
        return {"credential_id": self.binding.credential_id, "client_data_json": raw,
                "authenticator_data": auth, "signature": signature}


@unittest.skipIf(p.ec is None, "Existing cryptography backend unavailable; no install")
class CryptographicAttendanceTests(unittest.TestCase):
    def setUp(self):
        # Every case is an independent synthetic fixture, never a recovery original.
        self.tmp = tempfile.TemporaryDirectory(prefix="nexus-attendance-unit-")
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "journal.json"
        self.fake = FakeAuthenticator()
        self.policy = p.Policy("synthetic-policy-v1", "nexus.example.invalid",
                               "https://nexus.example.invalid")
        self.ledger = p.ProtectedChallengeLedger(self.path, self.policy, self.fake.binding,
                                                 create=True)
        self.verifier = p.WebAuthnAttendanceVerifier(self.ledger, self.policy, self.fake.binding)
        self.c = self.ledger.issue("synthetic-incident", "synthetic-operation",
                                   p.ClockSample(10000, 20000, "synthetic-epoch"))
        self.a = self.fake.assertion(self.c)

    def verify(self, c=None, a=None, **kwargs):
        return self.verifier.verify(
            self.c if c is None else c, self.a if a is None else a,
            incident=kwargs.pop("incident", "synthetic-incident"),
            operation=kwargs.pop("operation", "synthetic-operation"),
            sample=kwargs.pop("sample", p.ClockSample(10001, 20001, "synthetic-epoch")),
            **kwargs)

    def denied(self, code, **kwargs):
        with self.assertRaisesRegex(p.AttendanceError, "^" + code + "$"):
            self.verify(**kwargs)

    def test_crypto_01_valid_synthetic_assertion(self):
        e = self.verify().record()
        self.assertEqual(e["result"], "ASSERTION_VALIDATED_IN_LAB_MODEL")
        self.assertEqual(e["owner_presence"], "UNKNOWN")
        self.assertEqual(e["authority"], "NONE")
        self.assertFalse(e["dispatch_requested"])

    def test_crypto_02_wrong_challenge(self):
        a = self.fake.assertion(self.c, client_changes={"challenge": "wrong"})
        self.denied("CLIENT_CONTEXT", a=a)

    def test_crypto_03_expired(self):
        self.denied("STALE_OR_CLOCK", sample=p.ClockSample(15000, 25000, "synthetic-epoch"))

    def test_crypto_04_replay_completed(self):
        self.verify()
        self.denied("REPLAY")

    def test_crypto_05_duplicate_assertion(self):
        self.verify()
        self.denied("REPLAY", a=copy.deepcopy(self.a))

    def test_crypto_06_wrong_incident(self):
        self.denied("CONTEXT", incident="other")

    def test_crypto_07_wrong_operation(self):
        self.denied("CONTEXT", operation="other")

    def test_crypto_08_wrong_binding(self):
        a = self.fake.assertion(self.c)
        a["credential_id"] = b"another-known-id"
        self.denied("CREDENTIAL", a=a)

    def test_crypto_09_invalid_signature(self):
        a = dict(self.a, signature=b"invalid")
        self.denied("SIGNATURE", a=a)

    def test_crypto_10_modified_signed_payload(self):
        a = dict(self.a)
        a["authenticator_data"] = a["authenticator_data"][:-1] + b"\x02"
        self.denied("SIGNATURE", a=a)

    def test_crypto_11_missing_up(self):
        self.denied("UP", a=self.fake.assertion(self.c, flags=4))

    def test_crypto_12_missing_uv(self):
        self.denied("UV", a=self.fake.assertion(self.c, flags=1))

    def test_crypto_13_counter_anomaly(self):
        self.verify()
        c = self.ledger.issue("synthetic-incident", "synthetic-operation",
                              p.ClockSample(10002, 20002, "synthetic-epoch"))
        self.denied("COUNTER", c=c, a=self.fake.assertion(c, counter=1),
                    sample=p.ClockSample(10003, 20003, "synthetic-epoch"))

    def test_crypto_14_plain_ui_only(self):
        self.denied("ASSERTION", a={"button_callback": True})

    def test_crypto_15_presence_true_only(self):
        self.denied("ASSERTION", a={"presence": True})

    def test_crypto_16_unsigned_object(self):
        self.denied("ASSERTION", a={"credential_id": self.fake.binding.credential_id})

    def test_crypto_17_direct_success_injection(self):
        self.denied("ASSERTION", a={"result": "SUCCESS", "caller": "Work/Codex"})

    def test_crypto_18_rollback_with_retained_checkpoint(self):
        before = self.path.read_bytes()
        self.verify()
        cp = self.ledger.checkpoint
        self.path.write_bytes(before)
        with self.assertRaisesRegex(p.AttendanceError, "ROLLBACK_OR_MUTATION"):
            p.ProtectedChallengeLedger(self.path, self.policy, self.fake.binding, cp)

    def test_crypto_19_consumed_reused_after_reload(self):
        self.verify()
        loaded = p.ProtectedChallengeLedger(self.path, self.policy, self.fake.binding,
                                            self.ledger.checkpoint)
        self.verifier = p.WebAuthnAttendanceVerifier(loaded, self.policy, self.fake.binding)
        self.denied("REPLAY")

    def test_crypto_20_policy_version_mismatch(self):
        c = copy.deepcopy(self.c); c["policy"]["version"] = "other"
        self.denied("CHALLENGE_SUBSTITUTION", c=c)

    def test_crypto_21_lineage_removed(self):
        e = self.verify(); record = e.record(); del record["lineage"]
        self.assertFalse(e.matches(record))

    def test_crypto_22_unknown_credential(self):
        self.denied("CREDENTIAL", a=dict(self.a, credential_id=b"unknown"))

    def test_crypto_23_verifier_storage_unavailable(self):
        with patch.object(Path, "open", side_effect=OSError("synthetic I/O failure")):
            self.denied("STORAGE")

    def test_crypto_24_challenge_storage_unavailable(self):
        self.verify()
        with patch.object(Path, "open", side_effect=OSError("synthetic I/O failure")):
            with self.assertRaisesRegex(p.AttendanceError, "STORAGE"):
                self.ledger.issue("synthetic-incident", "synthetic-operation",
                                  p.ClockSample(10002, 20002, "synthetic-epoch"))

    def test_crypto_25_ambiguous_completion(self):
        self.ledger.ambiguous(self.c)
        self.denied("REPLAY")

    def test_wrong_rp(self):
        self.denied("RP", a=self.fake.assertion(self.c, rp="wrong.example.invalid"))

    def test_wrong_origin(self):
        self.denied("CLIENT_CONTEXT", a=self.fake.assertion(
            self.c, client_changes={"origin": "https://wrong.example.invalid"}))

    def test_cross_origin(self):
        self.denied("CLIENT_CONTEXT", a=self.fake.assertion(
            self.c, client_changes={"crossOrigin": True}))

    def test_different_public_key_same_credential(self):
        self.denied("SIGNATURE", a=FakeAuthenticator(2).assertion(self.c))

    def test_clock_epoch_and_monotonic_expiry(self):
        self.denied("STALE_OR_CLOCK", sample=p.ClockSample(10001, 20001, "other-epoch"))

    def test_monotonic_expiry_despite_valid_utc(self):
        self.denied("STALE_OR_CLOCK", sample=p.ClockSample(10001, 25000, "synthetic-epoch"))

    def test_malformed_challenge(self):
        self.denied("MALFORMED", c={})

    def test_duplicate_client_json(self):
        a = dict(self.a, client_data_json=b'{"type":"webauthn.get","type":"fake"}')
        self.denied("DUPLICATE_FIELD", a=a)

    def test_oversized_assertion(self):
        self.denied("MALFORMED", a=dict(self.a, client_data_json=b"x" * (p.MAX_BYTES + 1)))

    def test_unsupported_backup_and_extension_flags(self):
        self.denied("UNSUPPORTED_FLAGS", a=self.fake.assertion(self.c, flags=13))

    def test_stale_evidence_and_mutation(self):
        e = self.verify(); record = e.record()
        record["subject"]["expires_utc_ms"] += 1
        body = dict(record); del body["integrity_sha256"]
        record["integrity_sha256"] = p.digest(body)
        self.assertFalse(e.matches(record))
        self.assertTrue(e.matches(e.record()))

    def test_live_ledger_mutation(self):
        body = json.loads(self.path.read_bytes()); body["lineage"] = "PRODUCTION"
        self.path.write_bytes(p.canonical(body))
        self.denied("ROLLBACK_OR_MUTATION")

    def test_reload_pending_is_ambiguous(self):
        loaded = p.ProtectedChallengeLedger(self.path, self.policy, self.fake.binding,
                                            self.ledger.checkpoint)
        self.verifier = p.WebAuthnAttendanceVerifier(loaded, self.policy, self.fake.binding)
        self.denied("REPLAY")

    def test_missing_independent_checkpoint(self):
        with self.assertRaisesRegex(p.AttendanceError, "CHECKPOINT_REQUIRED"):
            p.ProtectedChallengeLedger(self.path, self.policy, self.fake.binding)

    def test_failed_verification_is_terminal(self):
        self.denied("SIGNATURE", a=dict(self.a, signature=b"invalid"))
        self.denied("REPLAY")

    def test_sequence_previous_and_nonce(self):
        self.verify()
        c = self.ledger.issue("synthetic-incident", "synthetic-operation",
                              p.ClockSample(10002, 20002, "synthetic-epoch"))
        self.assertEqual(c["sequence"], 2)
        self.assertEqual(c["previous_status"], "CONSUMED")
        self.assertNotEqual(c["nonce"], self.c["nonce"])

    def test_outstanding_challenge_blocks_another(self):
        with self.assertRaisesRegex(p.AttendanceError, "OUTSTANDING"):
            self.ledger.issue("synthetic-incident", "synthetic-operation",
                              p.ClockSample(10002, 20002, "synthetic-epoch"))

    def test_creation_cannot_overwrite_existing_ledger(self):
        with self.assertRaisesRegex(p.AttendanceError, "STORAGE"):
            p.ProtectedChallengeLedger(self.path, self.policy, self.fake.binding, create=True)

    def test_zero_counter_is_not_replay_proof(self):
        self.verify(a=self.fake.assertion(self.c, counter=0))
        c = self.ledger.issue("synthetic-incident", "synthetic-operation",
                              p.ClockSample(10002, 20002, "synthetic-epoch"))
        self.verify(c=c, a=self.fake.assertion(c, counter=0),
                    sample=p.ClockSample(10003, 20003, "synthetic-epoch"))

    def test_capacity_refuses(self):
        with patch.object(p, "MAX_EVENTS", 1):
            self.denied("CAPACITY")

    def test_software_acknowledgement_variants(self):
        # Schema/signature model tests, NOT live UI/backend injection coverage.
        variants = [{"SendInput": True}, {"PowerShell": "ack"}, {"C#": "UI event"},
                    {"caller": "Codex", "presence": True}, {"success": True},
                    {"signature": b"", "presence": True}]
        for i, a in enumerate(variants):
            with self.subTest(i=i):
                # Pure cryptographic parser check so no actual original is reset.
                with self.assertRaisesRegex(p.AttendanceError, "ASSERTION"):
                    self.verifier._verify(self.c, a, "synthetic-incident",
                                          "synthetic-operation",
                                          p.ClockSample(10001, 20001, "synthetic-epoch"), 0)

    def test_actual_same_user_checkpoint_substitution_not_protected(self):
        # Successful same-user custody attack, recorded as limitation, not source PASS.
        before = self.path.read_bytes()
        self.verify()
        self.path.write_bytes(before)
        forged = p.Checkpoint(1, hashlib.sha256(before).hexdigest())
        loaded = p.ProtectedChallengeLedger(self.path, self.policy, self.fake.binding, forged)
        # Pending closes, but previously consumed history was replaced: rollback escaped
        # detection when BOTH storage and the caller-supplied reference were controlled.
        self.assertEqual(loaded._state()["challenges"][self.c["nonce"]]["state"], "AMBIGUOUS")
        self.assertFalse(any(e.get("state") == "CONSUMED" for e in loaded._read()["events"]))
        self.assertEqual(p.real_ceremony_readiness()["protected_consumer"], "UNKNOWN")

    def test_real_ceremony_descriptor_no_api_or_success(self):
        self.assertEqual(p.real_ceremony_readiness()["state"], "OWNER_PHYSICAL_PRESENCE_REQUIRED")
        self.assertFalse(p.real_ceremony_readiness()["native_call_implemented"])
        self.assertFalse(p.real_ceremony_readiness()["ceremony_performed"])

    def test_forged_malformed_journal_is_status_only_refusal(self):
        body = self.ledger._read()
        body["events"].append({"kind": "close", "nonce": self.c["nonce"], "state": {}})
        raw = p.canonical(body)
        self.path.write_bytes(raw)
        forged = p.Checkpoint(2, hashlib.sha256(raw).hexdigest())
        with self.assertRaisesRegex(p.AttendanceError, "^JOURNAL$"):
            p.ProtectedChallengeLedger(self.path, self.policy, self.fake.binding, forged)

    def test_verifier_cannot_switch_binding_away_from_ledger(self):
        with self.assertRaisesRegex(p.AttendanceError, "POLICY_BINDING"):
            p.WebAuthnAttendanceVerifier(self.ledger, self.policy, FakeAuthenticator(2).binding)

    def test_failed_atomic_replace_never_returns_evidence(self):
        with patch.object(p.os, "replace", side_effect=OSError("synthetic replace failure")):
            self.denied("STORAGE")
        self.assertTrue(self.path.with_name("journal.json.pending").exists())
        # Residue blocks subsequent writes; it is not silently erased or retried.
        self.denied("STORAGE")

    def test_concurrent_duplicate_same_instance_is_one_use(self):
        from concurrent.futures import ThreadPoolExecutor
        def attempt():
            try:
                return self.verify().result
            except p.AttendanceError as exc:
                return str(exc)
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: attempt(), range(2)))
        self.assertCountEqual(results, ["ASSERTION_VALIDATED_IN_LAB_MODEL", "REPLAY"])

    def test_result_sequence_and_returned_copy_are_bound(self):
        e = self.verify()
        record = e.record()
        self.assertEqual(record["result_sequence"], self.c["sequence"])
        record["subject"]["sequence"] = 999
        self.assertEqual(e.record()["subject"]["sequence"], self.c["sequence"])

    def test_backend_unavailable_refuses_without_installation(self):
        with patch.object(p, "ec", None):
            with self.assertRaisesRegex(p.AttendanceError, "CRYPTO_BACKEND_UNAVAILABLE"):
                self.fake.binding.validate()


if __name__ == "__main__":
    unittest.main()

"""VM-free fixture expectations. Reproduced attacks are SECURITY FAIL, not PASS."""
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from prototypes import cryptographic_attendance_v1 as c
from prototypes import recovery_admission_lab_v1 as p
from test_cryptographic_attendance_v1 import FakeAuthenticator


class RecoveryAdmissionLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # One synthetic verifier setup; no real enrollment or private capability.
        cls.auth_temp = tempfile.TemporaryDirectory(prefix="nexus-sprint-auth-")
        cls.fake = FakeAuthenticator()
        cls.policy = c.Policy("synthetic-policy-v1", "nexus.example.invalid",
                             "https://nexus.example.invalid")
        ledger = c.ProtectedChallengeLedger(Path(cls.auth_temp.name)/"attendance.json",
                                           cls.policy, cls.fake.binding, create=True)
        cls.now = c.ClockSample(10000,20000,"synthetic-epoch")
        challenge = ledger.issue("synthetic-incident","synthetic-operation",cls.now)
        cls.attendance = c.WebAuthnAttendanceVerifier(ledger,cls.policy,cls.fake.binding).verify(
            challenge,cls.fake.assertion(challenge),incident="synthetic-incident",
            operation="synthetic-operation",sample=replace(cls.now,utc_ms=10001,monotonic_ms=20001))

    @classmethod
    def tearDownClass(cls):
        cls.auth_temp.cleanup()  # only exact new synthetic test objects

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="nexus-sprint-admission-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.d = p.OperationDescriptor("synthetic-incident","synthetic-operation",
                "synthetic-target","synthetic-policy",self.fake.binding.fingerprint())
        self.a = p.FixtureAuthority(self.d.fingerprint(),11000,100,4096)
        self.b = p.FixtureBindings(self.d.target,self.d.policy,"reviewed-verifier",
                  self.d.attendance_binding,"fixed-consumer","process-1","handle-1",
                  "reservation-1","budget-1","state-1")
        self.clock = p.ClockEnvelope(self.now,11000,21000,20900)
        self.e = p.EvidenceReservation(self.root,4096)
        self.addCleanup(self.e.close)
        self.j = p.FixtureJournal(self.root,"synthetic-original")
        self.g = p.RecoveryAdmissionGate(self.root,self.d,self.a,self.b,self.clock,
                                        self.attendance,self.e,self.j)

    def at(self,delta=1):
        return replace(self.now,utc_ms=self.now.utc_ms+delta,monotonic_ms=self.now.monotonic_ms+delta)

    def reserve(self): return self.g.admit(self.at())

    def test_01_crypto_integration_intent_before_fixed_marker(self):
        self.assertEqual(self.reserve()["status"],"ADMITTED_INTENT_RESERVED")
        body=self.j.read()
        self.assertTrue(body["slot_consumed"]);self.assertEqual(body["reserved_ms"],20)
        self.assertEqual(body["reserved_bytes"],4096);self.assertFalse(self.g.marker.exists())
        result=self.g.deliver(self.at(2))
        self.assertFalse(result["production_admissible"]);self.assertEqual(result["authority"],"NONE")
        self.assertEqual(self.j.read()["status"],"CONFIRMED")

    def test_02_replay_duplicate_dispatch_and_consumption(self):
        self.reserve();self.g.deliver(self.at(2))
        with self.assertRaisesRegex(c.AttendanceError,"ORIGINAL_SLOT_CONSUMED"): self.reserve()
        with self.assertRaisesRegex(c.AttendanceError,"NOT_RESERVED_OR_REPLAY"):self.g.deliver(self.at(3))

    def test_03_ambiguous_delivery_retains_slot_and_reservations(self):
        self.reserve()
        with patch.object(Path,"open",side_effect=OSError("synthetic failure")):
            with self.assertRaises(c.AttendanceError):self.g.deliver(self.at(2))
        self.assertTrue(self.j.read()["slot_consumed"])
        self.assertEqual(self.j.read()["reserved_ms"],20)
        with self.assertRaises(c.AttendanceError):self.reserve()

    def test_04_revocation_and_changed_budget_after_admission(self):
        self.reserve()
        with self.assertRaisesRegex(c.AttendanceError,"AUTHORITY"):
            self.g.deliver(self.at(2),authority=replace(self.a,revoked=True))
        self.assertEqual(self.j.read()["status"],"AMBIGUOUS")
        self.assertFalse(self.g.marker.exists())

    def test_05_budget_evidence_and_wrong_grant_pre_effect(self):
        for authority in (replace(self.a,budget_ms=19),replace(self.a,evidence_bytes=10),
                          replace(self.a,descriptor_digest="wrong"),replace(self.a,utc_expiry=10001)):
            with self.subTest(authority=authority):
                with self.assertRaises(c.AttendanceError):self.g.admit(self.at(),authority=authority)
                self.assertFalse(self.j.read()["slot_consumed"])
        self.assertFalse(self.g.marker.exists())

    def test_06_attendance_expiry_after_reservation(self):
        self.g.clock=replace(self.clock,utc_expiry=20000,monotonic_deadline=30000,phase_deadline=29000)
        self.g.authority=replace(self.a,utc_expiry=20000)
        self.reserve()
        with self.assertRaisesRegex(c.AttendanceError,"ATTENDANCE_MODEL"):
            self.g.deliver(self.at(5000))
        self.assertFalse(self.g.marker.exists())

    def test_07_toctou_drift_all_bound_object_dimensions(self):
        # Before-admission drift: no slot consumed. Post-admission is tested separately.
        for field in p.FixtureBindings.__dataclass_fields__:
            with self.subTest(field=field):
                with self.assertRaisesRegex(c.AttendanceError,"BINDING_DRIFT"):
                    self.g.admit(self.at(),bindings=replace(self.b,**{field:"substituted"}))
        self.assertFalse(self.g.marker.exists())

    def test_08_target_policy_handle_drift_after_reservation(self):
        self.reserve()
        with self.assertRaisesRegex(c.AttendanceError,"BINDING_DRIFT"):
            self.g.deliver(self.at(2),bindings=replace(self.b,handle="substituted"))
        self.assertTrue(self.j.read()["slot_consumed"]);self.assertFalse(self.g.marker.exists())

    def test_09_clock_earliest_deadline_margin_and_phase(self):
        for delta in (899,900,999,1000):
            with self.subTest(delta=delta):
                with self.assertRaisesRegex(c.AttendanceError,"CLOCK_EXPIRED_OR_MARGIN"):
                    self.g.admit(self.at(delta))

    def test_10_clock_rollback_and_utc_discrepancy(self):
        for sample in (replace(self.now,monotonic_ms=19999),replace(self.now,utc_ms=9999),
                       replace(self.now,utc_ms=10090,monotonic_ms=20001),replace(self.now,epoch="other")):
            with self.subTest(sample=sample):
                with self.assertRaises(c.AttendanceError):self.g.admit(sample)

    def test_11_clock_no_pause_or_reset_and_real_readback(self):
        self.reserve()
        with self.assertRaisesRegex(c.AttendanceError,"CLOCK_ROLLBACK"):
            self.g.deliver(self.now)
        observed=p.read_clock();observed.validate()
        self.assertEqual(observed.epoch,p.PROCESS_EPOCH)
        self.assertGreater(observed.monotonic_ms,0)

    def test_12_evidence_allocated_before_dispatch_readback(self):
        self.assertEqual(self.e.path.stat().st_size,4096)
        self.assertEqual(self.e.file.read(4096),bytes(4096))
        self.reserve();self.e.check()
        self.assertGreater(self.e.written,0);self.assertFalse(self.g.marker.exists())

    def test_13_evidence_capacity_is_prechecked_no_spill(self):
        with self.assertRaisesRegex(c.AttendanceError,"EVIDENCE_CAPACITY"):
            self.e.append(bytes(4097))
        self.assertEqual(set(x.name for x in self.root.iterdir()),{"evidence.bin","admission.json"})

    def test_14_evidence_writer_mutation_is_logically_detected(self):
        with self.e.path.open("r+b") as f:f.write(b"x")
        with self.assertRaisesRegex(c.AttendanceError,"EVIDENCE_MUTATION"):self.reserve()

    def test_15_evidence_loss_closed_handle_and_reparse_model(self):
        with patch.object(Path,"is_symlink",return_value=True):
            with self.assertRaisesRegex(c.AttendanceError,"EVIDENCE_IDENTITY"):self.reserve()
        self.e.close()
        with self.assertRaisesRegex(c.AttendanceError,"EVIDENCE_STORAGE"):self.reserve()

    def test_16_partial_evidence_write_never_reserves_effect(self):
        with patch.object(self.e,"append",side_effect=c.AttendanceError("EVIDENCE_PARTIAL")):
            with self.assertRaisesRegex(c.AttendanceError,"EVIDENCE_PARTIAL"):self.reserve()
        self.assertFalse(self.j.read()["slot_consumed"]);self.assertFalse(self.g.marker.exists())

    def test_17_ledger_mutation_and_checkpoint_replacement_attack(self):
        original=self.j.path.read_bytes();self.reserve();cp=self.j.head
        self.j.path.write_bytes(original)
        with self.assertRaisesRegex(c.AttendanceError,"JOURNAL_MUTATION"):
            p.FixtureJournal(self.root,"synthetic-original",checkpoint=cp)
        forged=hashlib.sha256(original).hexdigest()
        loaded=p.FixtureJournal(self.root,"synthetic-original",checkpoint=forged)
        # Actual attacker-writable history/reference vulnerability reproduced.
        self.assertFalse(loaded.read()["slot_consumed"])

    def test_18_reserved_reload_is_ambiguous_no_retry(self):
        self.reserve();loaded=p.FixtureJournal(self.root,"synthetic-original",checkpoint=self.j.head)
        self.assertEqual(loaded.read()["status"],"AMBIGUOUS")
        self.assertTrue(loaded.read()["slot_consumed"]);self.assertEqual(loaded.read()["reserved_ms"],20)

    def test_19_malformed_and_corrupt_state_refused(self):
        self.j.path.write_bytes(b"malformed")
        with self.assertRaisesRegex(c.AttendanceError,"JOURNAL_MUTATION"):self.j.read()
        self.j.head=hashlib.sha256(b"malformed").hexdigest()
        with self.assertRaisesRegex(c.AttendanceError,"MALFORMED"):self.j.read()

    def test_20_result_replacement_and_consumer_drift(self):
        self.g.attendance=replace(self.attendance,head="different")
        with self.assertRaisesRegex(c.AttendanceError,"ATTENDANCE_MUTATION"):self.reserve()

    def test_21_same_user_public_code_policy_consumer_files_not_protected(self):
        # New synthetic files only; live repository, key and Owner files untouched.
        for name in ("verifier.txt","dependency.txt","public-binding.json","policy.json","consumer.txt"):
            path=self.root/name;path.write_text("reviewed synthetic bytes")
            before=hashlib.sha256(path.read_bytes()).digest()
            path.write_text("software replacement")
            self.assertNotEqual(hashlib.sha256(path.read_bytes()).digest(),before)

    def test_22_direct_dispatch_bypasses_gate_actual_same_user_write(self):
        self.g.marker.write_text("bypass synthetic marker")
        self.assertTrue(self.g.marker.exists());self.assertFalse(self.j.read()["slot_consumed"])

    def test_23_private_handle_duplication_is_not_exclusion(self):
        import os
        duplicate=os.dup(self.e.file.fileno())
        try:
            os.lseek(duplicate,0,os.SEEK_SET);os.write(duplicate,b"x")
        finally:os.close(duplicate)
        with self.assertRaisesRegex(c.AttendanceError,"EVIDENCE_MUTATION"):self.reserve()

    def test_24_final_recheck_to_effect_gap_is_not_atomic(self):
        self.reserve();original=self.g._check;calls=[]
        def revoke_after_check(*args):
            original(*args);calls.append(1)
            if len(calls)==2:self.g.authority=replace(self.a,revoked=True)
        with patch.object(self.g,"_check",side_effect=revoke_after_check):
            self.g.deliver(self.at(2))
        # The fixture still writes after final recheck; cannot claim OS atomic mediation.
        self.assertTrue(self.g.marker.exists());self.assertTrue(self.g.authority.revoked)

    def test_25_non_promotion_and_real_admission_always_refused(self):
        for supplied in ({},{"lineage":"PRODUCTION"},{"presence":True,"authority":"OWNER"},self.attendance.record()):
            self.assertEqual(p.production_admission(supplied)["status"],"REFUSED")
        with self.assertRaisesRegex(c.AttendanceError,"DESCRIPTOR"):
            replace(self.d,lineage="PRODUCTION").validate()

    def test_26_cross_original_attendance_custody_not_qualified(self):
        self.reserve()
        # Immutable in-memory basis detects change; no globally protected consumed
        # attendance reference exists between independent synthetic consumers.
        self.assertEqual(self.attendance.record()["owner_presence"],"UNKNOWN")
        self.assertEqual(p.production_admission({})["status"],"REFUSED")

    def test_27_descriptor_change_and_no_original_replacement(self):
        self.g.descriptor=replace(self.d,operation="other")
        with self.assertRaises(c.AttendanceError):self.reserve()
        with self.assertRaisesRegex(c.AttendanceError,"JOURNAL_STORAGE"):
            p.FixtureJournal(self.root,"replacement-original")

    def test_28_ambiguous_after_marker_write_keeps_original(self):
        self.reserve();original=self.j.persist;calls=[]
        def failed_confirmation(body):
            calls.append(body["status"])
            if body["status"]=="CONFIRMED":raise c.AttendanceError("synthetic confirm storage loss")
            return original(body)
        with patch.object(self.j,"persist",side_effect=failed_confirmation):
            with self.assertRaises(c.AttendanceError):self.g.deliver(self.at(2))
        self.assertTrue(self.g.marker.exists());self.assertEqual(self.j.read()["status"],"AMBIGUOUS")
        with self.assertRaises(c.AttendanceError):self.g.deliver(self.at(3))


if __name__=="__main__":unittest.main()

"""Offline adapter adversarial regression; never reported as live service proof."""
from datetime import datetime, timedelta, timezone
from io import BytesIO
import unittest

from scripts import g3_d03_s3_fence as f
from scripts import g3_d03_canary_vectors as v
from scripts.g3_production_metadata import canonical_bytes


class MemoryS3:
    def __init__(self):
        self.rows = {}
        self.calls = []
        self.mode = None

    def add(self, key, raw, *, duplicate=False, retained=True):
        versions = self.rows.setdefault(key, [])
        if versions and not duplicate:
            raise RuntimeError("precondition")
        versions.append((str(len(versions)+1), raw, retained))

    def list_object_versions(self, **kw):
        self.calls.append(("list", kw))
        if self.mode == "unavailable": raise RuntimeError("private backend details")
        values = [dict(Key=k, VersionId=vid, Size=len(raw), IsLatest=n==len(rows)-1)
            for k, rows in self.rows.items() if k.startswith(kw["Prefix"])
            for n, (vid, raw, _) in enumerate(rows)]
        result = dict(Versions=values, IsTruncated=False, ResponseMetadata={"HTTPStatusCode":200})
        if self.mode == "marker": result["DeleteMarkers"] = [{"Key":"deleted"}]
        if self.mode == "partial": result["IsTruncated"] = True
        if self.mode == "changed" and len([x for x in self.calls if x[0] == "list"]) >= 3:
            result["Versions"] = []
        return result

    def get_object(self, **kw):
        self.calls.append(("get", kw))
        row = next(x for x in self.rows[kw["Key"]] if x[0] == kw["VersionId"])
        return dict(Body=BytesIO(row[1]), ContentLength=len(row[1]), VersionId=row[0],
            ResponseMetadata={"HTTPStatusCode":200})

    def get_object_retention(self, **kw):
        self.calls.append(("retention", kw))
        row = next(x for x in self.rows[kw["Key"]] if x[0] == kw["VersionId"])
        return dict(Retention=dict(Mode="COMPLIANCE", RetainUntilDate=datetime.now(timezone.utc)+
            timedelta(days=7 if row[2] else -1)), ResponseMetadata={"HTTPStatusCode":200})

    def put_object(self, **kw):
        self.calls.append(("put", kw))
        if self.mode == "unknown-before": raise RuntimeError("not committed")
        if kw.get("IfNoneMatch") != "*": raise RuntimeError("missing precondition")
        self.add(kw["Key"], kw["Body"])
        if self.mode == "unknown-after": raise RuntimeError("ack lost")
        return dict(VersionId="1", ResponseMetadata={"HTTPStatusCode":200})


class FenceTests(unittest.TestCase):
    def setUp(self):
        self.client = MemoryS3()
        self.vectors = v.vectors()
        r = v.registration_body()
        self.registration = f.Registration("nexus-d03-custody-862902859484-ap-southeast-1-v1",
            "862902859484", v.NORMAL, v.INSTANCE, 1, r["genesis"]["id"],
            r["genesis"]["body_sha256"], tuple(r["admin_checkpoint_ids"]))
        self.fence = f.S3Fence(self.client, self.registration)
        self.until = datetime.now(timezone.utc)+timedelta(hours=1)
        self.install(0)

    def install(self, seq, *, journal=True):
        raw, objects = self.vectors[seq]
        for digest, value in objects.items():
            key = v.NORMAL+"objects/"+digest
            if key not in self.client.rows: self.client.add(key, value)
        if journal: self.client.add(v.NORMAL+f"journal/{seq:020d}", raw)
        if seq == 4:
            key="qualification/v1/faults/admin-authorizations-v1/"+f"{4:020d}/authorization.json"
            value=dict(schema_version="nexus.g3.d03.diagnostic-admin-authorization.v1",
                purpose="TEST_ONLY",generation=1,checkpoint=f.reference(raw),
                previous_checkpoint=f.reference(self.vectors[3][0]))
            self.client.add(key,canonical_bytes(value))

    def read(self): return self.fence.read(valid_until=self.until)

    def test_valid_retained_history_never_authority(self):
        self.install(1)
        h = self.read()
        self.assertEqual(h.authority, "NONE")
        self.assertEqual(v.verify_consumer(h)["production_eligibility"], "DENY")

    def test_exact_append(self):
        self.install(1, journal=False)
        h = self.fence.append(self.vectors[1][0], self.read().head, valid_until=self.until)
        self.assertEqual(len(h.checkpoints), 2)
        self.assertEqual([x[1]["IfNoneMatch"] for x in self.client.calls if x[0]=="put"], ["*"])

    def test_duplicate_append_rejected(self):
        self.install(1)
        with self.assertRaises(f.FenceError):
            self.fence.append(self.vectors[1][0], f.reference(self.vectors[0][0]), valid_until=self.until)
        self.assertFalse(any(x[0]=="put" for x in self.client.calls))

    def test_stale_snapshot_not_current(self):
        self.install(1)
        with self.assertRaises(f.FenceError):
            v.verify_consumer(self.read(), restored_head=f.reference(self.vectors[0][0]))

    def test_predecessor_mismatch(self):
        self.install(1)
        raw = f.decoded(self.vectors[1][0]); raw["previous_checkpoint"]["body_sha256"]="0"*64
        self.client.rows[v.NORMAL+f"journal/{1:020d}"]=[("1", canonical_bytes(raw), True)]
        with self.assertRaises(f.FenceError): self.read()

    def test_gap(self):
        self.install(2)
        with self.assertRaises(f.FenceError): self.read()

    def test_fork_duplicate_version(self):
        self.client.add(v.NORMAL+f"journal/{0:020d}", self.vectors[0][0], duplicate=True)
        with self.assertRaises(f.FenceError): self.read()

    def test_delete_marker(self):
        self.client.mode="marker"
        with self.assertRaises(f.FenceError): self.read()

    def test_truncated_unresolved_page(self):
        self.client.mode="partial"
        with self.assertRaises(f.FenceError): self.read()

    def test_missing_history(self):
        del self.client.rows[v.NORMAL+f"journal/{0:020d}"]
        with self.assertRaises(f.FenceError): self.read()

    def test_corrupted_body(self):
        self.client.rows[v.NORMAL+f"journal/{0:020d}"]=[("1", b'{}', True)]
        with self.assertRaises(f.FenceError): self.read()

    def test_missing_exact_referenced_bytes(self):
        del self.client.rows[v.NORMAL+"objects/"+next(iter(self.vectors[0][1]))]
        with self.assertRaises(f.FenceError): self.read()

    def test_corrupted_descriptor(self):
        key=v.NORMAL+"objects/"+f.decoded(self.vectors[0][0])["ledger_commit_sha256"]
        self.client.rows[key]=[("1", b'{}', True)]
        with self.assertRaises(f.FenceError): self.read()

    def test_expired_retention(self):
        self.client.rows[v.NORMAL+f"journal/{0:020d}"]=[("1", self.vectors[0][0], False)]
        with self.assertRaises(f.FenceError): self.read()

    def test_unavailable_backend_sanitized(self):
        self.client.mode="unavailable"
        with self.assertRaisesRegex(f.FenceError, '^D03_QUARANTINE$'): self.read()

    def test_changed_history_quarantines(self):
        self.client.mode="changed"
        with self.assertRaises(f.FenceError): self.read()

    def test_unknown_after_commit_exact_reconciliation_no_retry(self):
        self.install(1, journal=False); head=self.read().head
        self.client.mode="unknown-after"
        with self.assertRaises(f.FenceError): self.fence.append(self.vectors[1][0],head,valid_until=self.until)
        with self.assertRaises(f.FenceError): self.fence.append(self.vectors[1][0],head,valid_until=self.until)
        self.client.mode=None
        self.assertEqual(self.fence.reconcile(valid_until=self.until).head, f.reference(self.vectors[1][0]))
        self.assertEqual(sum(x[0]=="put" for x in self.client.calls),1)

    def test_unknown_before_commit_never_redispatched(self):
        self.install(1,journal=False); head=self.read().head
        self.client.mode="unknown-before"
        with self.assertRaises(f.FenceError): self.fence.append(self.vectors[1][0],head,valid_until=self.until)
        self.client.mode=None
        with self.assertRaises(f.FenceError): self.fence.reconcile(valid_until=self.until)
        self.assertEqual(sum(x[0]=="put" for x in self.client.calls),1)

    def test_restart_requires_new_incarnation_and_preserves_terminal(self):
        for seq in range(1,5): self.install(seq)
        restart=f.S3Fence(self.client,self.registration)
        self.assertTrue(restart.quarantined)
        h=restart.read(valid_until=self.until)
        with self.assertRaises(f.FenceError): v.verify_consumer(h, incarnation="canary-incarnation-1")
        self.assertEqual(v.verify_consumer(h,incarnation="canary-incarnation-2")["automatic_redispatch"], "DENY")
        rows=v.verify_snapshot(v.EncodedSnapshot(h.controls[-1],h.pages[-1]))
        self.assertTrue(any("canary-consumed-unknown" in row.key for row in rows))

    def test_generation_mismatch(self):
        with self.assertRaises(f.FenceError): v.verify_consumer(self.read(),generation=2)

    def test_ordinary_cannot_bootstrap_or_recover(self):
        for seq in (0,4):
            with self.assertRaises(f.FenceError):
                self.fence.append(self.vectors[seq][0],self.read().head,valid_until=self.until)
        self.assertFalse(any(x[0]=="put" for x in self.client.calls))

    def test_unregistered_recovery_rejected(self):
        for seq in range(1,4): self.install(seq)
        raw, objects=v.checkpoint(4,f.reference(self.vectors[3][0]),"RECOVER",3,"unapproved",True)
        for key, value in objects.items(): self.client.add(v.NORMAL+"objects/"+key,value)
        self.client.add(v.NORMAL+f"journal/{4:020d}",raw)
        with self.assertRaises(f.FenceError): self.read()

    def test_call_budget(self):
        self.fence=f.S3Fence(self.client,self.registration,max_attempts=1)
        with self.assertRaises(f.FenceError): self.read()
        self.assertEqual(self.fence.attempts,1)

    def test_wrong_scope_and_production_registration(self):
        from dataclasses import replace
        for changes in (dict(owner="175880707430"),dict(prefix="elsewhere/"),dict(purpose="PRODUCTION"),dict(generation=True)):
            with self.assertRaises(f.FenceError): replace(self.registration,**changes)

    def test_invalid_evidence_schema_and_noncanonical(self):
        for raw in (b'{"x":1,"x":2}', b'{ "x":1}', b'\xef\xbb\xbf{}'):
            with self.assertRaises(f.FenceError): f.decoded(raw)

    def test_missing_candidate_artifacts_cannot_poison_history(self):
        with self.assertRaises(f.FenceError):
            self.fence.append(self.vectors[1][0], self.read().head, valid_until=self.until)
        self.assertFalse(any(x[0]=="put" for x in self.client.calls))

    def test_known_recover_hash_without_independent_admin_record_rejected(self):
        for seq in range(1,5): self.install(seq)
        key="qualification/v1/faults/admin-authorizations-v1/"+f"{4:020d}/authorization.json"
        del self.client.rows[key]
        with self.assertRaises(f.FenceError): self.read()


if __name__ == "__main__": unittest.main()

"""Fixed VM-free admission/evidence model. Never operational recovery authority.

All custody is ordinary same-user fixture custody, NOT an OS-qualified boundary.
No process launcher, command, IPC server, network, service or VM API exists here.
"""
from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
import secrets
import threading
import time

from prototypes.cryptographic_attendance_v1 import (
    AttendanceError, AttendanceEvidenceRecord, ClockSample, LINEAGE,
    canonical, digest, strict_json, text,
)

MAX_OBJECT_BYTES = 65536
PROCESS_EPOCH = secrets.token_hex(16)  # process-local epoch, NOT boot attestation


def fail(code):
    raise AttendanceError(code)


def read_clock():
    """Ordinary OS clock observation. No tamper-proof source claim."""
    return ClockSample(time.time_ns() // 1000000, time.monotonic_ns() // 1000000,
                       PROCESS_EPOCH)


@dataclass(frozen=True)
class ClockEnvelope:
    issued: ClockSample
    utc_expiry: int
    monotonic_deadline: int
    phase_deadline: int
    margin_ms: int = 1
    skew_tolerance_ms: int = 25

    def check(self, sample, previous=None):
        self.issued.validate(); sample.validate()
        values = (self.utc_expiry, self.monotonic_deadline, self.phase_deadline,
                  self.margin_ms, self.skew_tolerance_ms)
        if any(type(v) is not int or v < 0 for v in values):
            fail("CLOCK_POLICY")
        if sample.epoch != self.issued.epoch:
            fail("CLOCK_EPOCH")
        du = sample.utc_ms - self.issued.utc_ms
        dm = sample.monotonic_ms - self.issued.monotonic_ms
        if du < 0 or dm < 0 or (previous is not None and
                (sample.utc_ms < previous.utc_ms or sample.monotonic_ms < previous.monotonic_ms)):
            fail("CLOCK_ROLLBACK")
        if abs(du - dm) > self.skew_tolerance_ms:
            fail("CLOCK_DISCREPANCY")
        if (sample.utc_ms + self.margin_ms >= self.utc_expiry or
                sample.monotonic_ms + self.margin_ms >=
                min(self.monotonic_deadline, self.phase_deadline)):
            fail("CLOCK_EXPIRED_OR_MARGIN")


@dataclass(frozen=True)
class OperationDescriptor:
    incident: str
    operation: str
    target: str
    policy: str
    attendance_binding: str
    planned_ms: int = 20
    evidence_bytes: int = 4096
    original_slot: int = 1
    lineage: str = LINEAGE

    def validate(self):
        for value in (self.incident, self.operation, self.target, self.policy,
                      self.attendance_binding): text(value)
        if (self.lineage != LINEAGE or type(self.original_slot) is not int or
                self.original_slot != 1 or type(self.planned_ms) is not int or
                not 1 <= self.planned_ms <= 1000 or type(self.evidence_bytes) is not int or
                not 1 <= self.evidence_bytes <= MAX_OBJECT_BYTES):
            fail("DESCRIPTOR")

    def fingerprint(self):
        self.validate(); return digest(asdict(self))


@dataclass(frozen=True)
class FixtureAuthority:
    """Synthetic grant input; not an Owner issuer, signature or admission grant."""
    descriptor_digest: str
    utc_expiry: int
    budget_ms: int
    evidence_bytes: int
    issuer: str = "SYNTHETIC_VM_FREE_TEST_ISSUER"
    revoked: bool = False
    lineage: str = LINEAGE

    def validate(self, descriptor, sample):
        if (self.issuer != "SYNTHETIC_VM_FREE_TEST_ISSUER" or self.lineage != LINEAGE or
                self.descriptor_digest != descriptor.fingerprint() or
                type(self.revoked) is not bool or self.revoked or
                type(self.utc_expiry) is not int or sample.utc_ms >= self.utc_expiry):
            fail("AUTHORITY")
        if (type(self.budget_ms) is not int or descriptor.planned_ms > self.budget_ms or
                type(self.evidence_bytes) is not int or
                descriptor.evidence_bytes > self.evidence_bytes):
            fail("BUDGET")


@dataclass(frozen=True)
class FixtureBindings:
    """Modeled exact identities. These strings are not process/token attestation."""
    target: str
    policy: str
    verifier: str
    public_binding: str
    consumer: str
    process: str
    handle: str
    reservation: str
    budget: str
    state: str

    def validate(self):
        for value in asdict(self).values(): text(value)


class EvidenceReservation:
    """Held, prewritten fixed fixture object; no disk quota/custody guarantee.

    Opens only 'evidence.bin' in the caller's declared synthetic fixture root.
    A same-user actor can still reopen or replace it. That attack is tested.
    """
    def __init__(self, root, capacity):
        if type(capacity) is not int or not 1 <= capacity <= MAX_OBJECT_BYTES:
            fail("EVIDENCE_CAPACITY")
        root = Path(root)
        if not root.is_dir() or root.is_symlink(): fail("FIXTURE_ROOT")
        self.path = root / "evidence.bin"
        self.capacity = capacity
        self.written = 0
        try:
            self.file = self.path.open("x+b", buffering=0)
            self.file.write(bytes(capacity)); self.file.flush(); os.fsync(self.file.fileno())
            info = os.fstat(self.file.fileno())
            self.identity = (info.st_dev, info.st_ino)
            self.file.seek(0)
            if self.file.read(capacity) != bytes(capacity): fail("EVIDENCE_READBACK")
            self.file.seek(0)
            self.expected_hash = hashlib.sha256(bytes(capacity)).hexdigest()
        except OSError:
            if hasattr(self, "file"): self.file.close()
            fail("EVIDENCE_STORAGE")

    def check(self):
        try:
            held, named = os.fstat(self.file.fileno()), self.path.stat()
            if (self.path.is_symlink() or (held.st_dev, held.st_ino) != self.identity or
                    (named.st_dev, named.st_ino) != self.identity or
                    held.st_size != self.capacity): fail("EVIDENCE_IDENTITY")
            self.file.seek(0)
            if hashlib.sha256(self.file.read(self.capacity)).hexdigest() != self.expected_hash:
                fail("EVIDENCE_MUTATION")
        except AttendanceError:
            raise
        except (OSError, ValueError): fail("EVIDENCE_STORAGE")

    def append(self, payload):
        if type(payload) is not bytes or self.written + len(payload) > self.capacity:
            fail("EVIDENCE_CAPACITY")
        self.check()
        try:
            self.file.seek(self.written)
            if self.file.write(payload) != len(payload): fail("EVIDENCE_PARTIAL")
            self.file.flush(); os.fsync(self.file.fileno())
            self.file.seek(self.written)
            if self.file.read(len(payload)) != payload: fail("EVIDENCE_READBACK")
        except OSError: fail("EVIDENCE_STORAGE")
        self.written += len(payload)
        self.file.seek(0)
        self.expected_hash = hashlib.sha256(self.file.read(self.capacity)).hexdigest()

    def close(self):
        self.file.close()  # does not delete anything


class FixtureJournal:
    """One original/slot journal with a retained in-memory hash, not protected."""
    def __init__(self, root, original, *, checkpoint=None):
        text(original)
        self.path = Path(root) / "admission.json"
        self.original = original
        if checkpoint is None:
            body = {"original": original, "lineage": LINEAGE, "sequence": 0,
                    "slot_consumed": False, "reserved_ms": 0, "reserved_bytes": 0,
                    "status": "NEW", "intent": None, "observations": []}
            raw = canonical(body)
            try:
                with self.path.open("xb") as f:
                    f.write(raw); f.flush(); os.fsync(f.fileno())
            except OSError: fail("JOURNAL_STORAGE")
            self.head = hashlib.sha256(raw).hexdigest()
        else:
            if type(checkpoint) is not str or len(checkpoint) != 64: fail("CHECKPOINT")
            self.head = checkpoint
            body = self.read()
            if body["slot_consumed"] and body["status"] in {"RESERVED", "SUBMITTED"}:
                body["status"] = "AMBIGUOUS"; self.persist(body)

    def read(self):
        try:
            return self._read_checked()
        except AttendanceError:
            raise
        except (TypeError, KeyError, ValueError):
            fail("JOURNAL_SCHEMA")

    def _read_checked(self):
        try:
            with self.path.open("rb") as f: raw = f.read(MAX_OBJECT_BYTES + 1)
        except OSError: fail("JOURNAL_STORAGE")
        if hashlib.sha256(raw).hexdigest() != self.head: fail("JOURNAL_MUTATION")
        body = strict_json(raw)
        fields = {"original", "lineage", "sequence", "slot_consumed", "reserved_ms",
                  "reserved_bytes", "status", "intent", "observations"}
        if (type(body) is not dict or set(body) != fields or body["original"] != self.original or
                body["lineage"] != LINEAGE or type(body["slot_consumed"]) is not bool or
                type(body["sequence"]) is not int or not 0 <= body["sequence"] <= 128 or
                type(body["reserved_ms"]) is not int or body["reserved_ms"] < 0 or
                type(body["reserved_bytes"]) is not int or body["reserved_bytes"] < 0 or
                type(body["observations"]) is not list or len(body["observations"]) > 128 or
                body["status"] not in {"NEW", "RESERVED", "SUBMITTED", "CONFIRMED", "AMBIGUOUS"}):
            fail("JOURNAL_SCHEMA")
        if ((body["status"] == "NEW") != (not body["slot_consumed"]) or
                (body["slot_consumed"] and type(body["intent"]) is not dict)):
            fail("JOURNAL_SCHEMA")
        return body

    def persist(self, body):
        self.read()  # reject mutation before replacing the held logical original
        raw = canonical(body)
        temp = self.path.with_name("admission.pending")
        try:
            with temp.open("xb") as f:
                f.write(raw); f.flush(); os.fsync(f.fileno())
            os.replace(temp, self.path)
        except OSError: fail("JOURNAL_STORAGE")
        self.head = hashlib.sha256(raw).hexdigest()


class RecoveryAdmissionGate:
    """Private fixture intent/marker model. Actual recovery always REFUSED.

    The marker path is deliberately directly writable by the same user: mediation
    therefore FAILS as an actual OS boundary, regardless of model test success.
    """
    def __init__(self, root, descriptor, authority, bindings, clock, attendance,
                 evidence, journal):
        descriptor.validate(); bindings.validate()
        if type(attendance) is not AttendanceEvidenceRecord: fail("ATTENDANCE_MODEL")
        if evidence.capacity < descriptor.evidence_bytes: fail("EVIDENCE_CAPACITY")
        self.root = Path(root)
        self.descriptor, self.authority, self.bindings = descriptor, authority, bindings
        self.clock, self.attendance, self.evidence, self.journal = clock, attendance, evidence, journal
        self.marker = self.root / "fixture-effect.json"
        self._lock = threading.RLock()
        self._previous = None
        self._reserved_head = None
        self._attendance_basis = canonical(attendance.record())

    def _check(self, sample, authority, bindings):
        self.clock.check(sample, self._previous)
        self.descriptor.validate(); authority.validate(self.descriptor, sample); bindings.validate()
        if authority != self.authority or bindings != self.bindings: fail("BINDING_DRIFT")
        if bindings.target != self.descriptor.target or bindings.policy != self.descriptor.policy:
            fail("TARGET_OR_POLICY")
        self.evidence.check()
        record = self.attendance.record()
        if canonical(record) != self._attendance_basis: fail("ATTENDANCE_MUTATION")
        c = record["subject"]
        if (record["lineage"] != LINEAGE or record["authority"] != "NONE" or
                record["owner_presence"] != "UNKNOWN" or record["dispatch_requested"] is not False or
                record["result"] != "ASSERTION_VALIDATED_IN_LAB_MODEL" or
                c["incident"] != self.descriptor.incident or c["operation"] != self.descriptor.operation or
                c["binding"] != self.descriptor.attendance_binding or
                c["epoch"] != sample.epoch or sample.utc_ms < c["issued_utc_ms"] or
                sample.monotonic_ms < c["issued_monotonic_ms"] or
                sample.utc_ms >= c["expires_utc_ms"] or sample.monotonic_ms >= c["expires_monotonic_ms"]):
            fail("ATTENDANCE_MODEL")
        self._previous = sample

    def admit(self, sample, *, authority=None, bindings=None):
        with self._lock:
            body = self.journal.read()
            if body["slot_consumed"]: fail("ORIGINAL_SLOT_CONSUMED")
            self._check(sample, authority or self.authority, bindings or self.bindings)
            intent = {"descriptor": asdict(self.descriptor), "authority": asdict(self.authority),
                      "bindings": asdict(self.bindings), "attendance": digest(self.attendance.record()),
                      "clock": asdict(sample), "evidence_identity": list(self.evidence.identity),
                      "lineage": LINEAGE, "authority_class": "SYNTHETIC_FIXTURE_ONLY"}
            self.evidence.append(canonical(intent))  # reservation already exists before admission
            body.update(slot_consumed=True, reserved_ms=self.descriptor.planned_ms,
                        reserved_bytes=self.descriptor.evidence_bytes, sequence=body["sequence"]+1,
                        status="RESERVED", intent=intent)
            self.journal.persist(body)
            self._reserved_head = self.journal.head
            return {"status": "ADMITTED_INTENT_RESERVED", "lineage": LINEAGE,
                    "actual_recovery_authority": "NONE", "sequence": body["sequence"]}

    def deliver(self, sample, *, authority=None, bindings=None):
        with self._lock:
            body = self.journal.read()
            if body["status"] != "RESERVED" or self._reserved_head != self.journal.head:
                fail("NOT_RESERVED_OR_REPLAY")
            try:
                self._check(sample, authority or self.authority, bindings or self.bindings)
                body["status"] = "SUBMITTED"; self.journal.persist(body)
                # Fixed harmless effect only. This recheck is NOT an atomic OS authorization.
                self._check(sample, authority or self.authority, bindings or self.bindings)
                with self.marker.open("xb") as f:
                    f.write(canonical({"fixture": "VM_FREE_MARKER", "lineage": LINEAGE,
                                       "intent": digest(body["intent"])}))
                    f.flush(); os.fsync(f.fileno())
                body["status"] = "CONFIRMED"; self.journal.persist(body)
            except Exception:
                body["status"] = "AMBIGUOUS"
                self.journal.persist(body)
                raise
            return {"status": "CONFIRMED_SYNTHETIC_MARKER", "lineage": LINEAGE,
                    "authority": "NONE", "production_admissible": False}


def production_admission(_):
    """Permanent refusal, including objects with removed/fabricated lineage."""
    return {"status": "REFUSED", "reason": "VM_FREE_MODEL_NOT_OPERATIONAL",
            "lineage": LINEAGE, "actual_recovery_authority": "NONE"}

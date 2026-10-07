"""VM-free assertion model. LAB_ONLY; no ceremony, effect dispatch or authority.

Storage/checkpoints are logical integrity controls, NOT same-SID protection.
Only public assertion inputs are accepted. No native authentication API is called.
"""
from __future__ import annotations

import base64
import copy
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import secrets
import threading

try:
    from cryptography.exceptions import InvalidSignature
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import ec
except ImportError:
    ec = hashes = None
    InvalidSignature = ValueError

MAX_BYTES = 65536
MAX_EVENTS = 128
LINEAGE = "LAB_ONLY/ENGINEERING_ONLY_NON_QUALIFYING"
PURPOSE = "NEXUS_ATTENDANCE_ONLY_V1"


class AttendanceError(ValueError):
    """A fixed code only: never include assertion/credential input in errors."""


def reject(code):
    raise AttendanceError(code)


def canonical(value):
    try:
        raw = json.dumps(value, sort_keys=True, separators=(",", ":"),
                         ensure_ascii=True, allow_nan=False).encode("utf-8")
    except (TypeError, ValueError, RecursionError):
        reject("MALFORMED")
    if len(raw) > MAX_BYTES:
        reject("SIZE")
    return raw


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def strict_json(raw):
    if type(raw) is not bytes or len(raw) > MAX_BYTES:
        reject("MALFORMED")
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                reject("DUPLICATE_FIELD")
            out[k] = v
        return out
    def constant(_):
        reject("MALFORMED")
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                          parse_constant=constant)
    except AttendanceError:
        raise
    except (ValueError, UnicodeError, RecursionError):
        reject("MALFORMED")


def text(value):
    if type(value) is not str or not 1 <= len(value) <= 128:
        reject("MALFORMED")
    if any(ord(c) < 32 for c in value):
        reject("MALFORMED")


def b64(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


@dataclass(frozen=True)
class ClockSample:
    utc_ms: int
    monotonic_ms: int
    epoch: str

    def validate(self):
        text(self.epoch)
        if any(type(v) is not int or v < 0 for v in (self.utc_ms, self.monotonic_ms)):
            reject("CLOCK")


@dataclass(frozen=True)
class Policy:
    version: str
    rp_id: str
    origin: str
    ttl_ms: int = 5000  # test profile only, NOT an accepted recovery allowance
    require_uv: bool = True

    def validate(self):
        for v in (self.version, self.rp_id, self.origin):
            text(v)
        if type(self.ttl_ms) is not int or not 1 <= self.ttl_ms <= 60000:
            reject("POLICY")
        if type(self.require_uv) is not bool:
            reject("POLICY")

    def record(self):
        self.validate()
        return dict(version=self.version, rp_id=self.rp_id, origin=self.origin,
                    ttl_ms=self.ttl_ms, require_uv=self.require_uv)


@dataclass(frozen=True)
class PublicBinding:
    credential_id: bytes
    public_point: bytes  # SEC1 uncompressed P-256, public data only
    initial_counter: int = 0

    def validate(self):
        if (type(self.credential_id) is not bytes or
                not 1 <= len(self.credential_id) <= 1023 or
                type(self.public_point) is not bytes or
                len(self.public_point) != 65 or self.public_point[0] != 4 or
                type(self.initial_counter) is not int or
                not 0 <= self.initial_counter <= 0xffffffff):
            reject("BINDING")
        if ec is None:
            reject("CRYPTO_BACKEND_UNAVAILABLE")
        try:
            ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(), self.public_point)
        except ValueError:
            reject("BINDING")

    def fingerprint(self):
        self.validate()
        return digest({"credential": b64(self.credential_id), "point": b64(self.public_point),
                       "initial_counter": self.initial_counter})


@dataclass(frozen=True)
class Checkpoint:
    generation: int
    head: str
    # An externally retained reference is required. This object is NOT attested.


class ProtectedChallengeLedger:
    """Fixed bounded journal; name describes its intended role, not OS custody.

    A live/reloaded instance compares disk to a retained checkpoint. Replacing
    disk AND the supplied checkpoint can bypass that check; reported/tested.
    No secret MAC or privileged service is introduced.
    """
    def __init__(self, path, policy, binding, checkpoint=None, *, create=False):
        self._path = Path(path)
        self._policy = policy.record()
        self._binding = binding.fingerprint()
        self._lock = threading.RLock()
        if create:
            body = {"version": 1, "lineage": LINEAGE, "policy": self._policy,
                    "binding": self._binding, "events": []}
            raw = canonical(body)
            try:
                with self._path.open("xb") as f:
                    f.write(raw)
                    f.flush()
                    os.fsync(f.fileno())
            except OSError:
                reject("STORAGE")
            self._checkpoint = Checkpoint(0, hashlib.sha256(raw).hexdigest())
        else:
            if not isinstance(checkpoint, Checkpoint):
                reject("CHECKPOINT_REQUIRED")
            if (type(checkpoint.generation) is not int or
                    not 0 <= checkpoint.generation <= MAX_EVENTS or
                    type(checkpoint.head) is not str or len(checkpoint.head) != 64 or
                    any(c not in "0123456789abcdef" for c in checkpoint.head)):
                reject("CHECKPOINT")
            self._checkpoint = checkpoint
        self._read()
        if not create:
            state = self._state()
            for nonce, record in state["challenges"].items():
                if record["state"] in {"OUTSTANDING", "VERIFYING"}:
                    self._append({"kind": "close", "nonce": nonce, "state": "AMBIGUOUS"})

    @property
    def checkpoint(self):
        self._read()
        return self._checkpoint

    def _read(self):
        try:
            with self._path.open("rb") as f:
                raw = f.read(MAX_BYTES + 1)
        except OSError:
            reject("STORAGE")
        if hashlib.sha256(raw).hexdigest() != self._checkpoint.head:
            reject("ROLLBACK_OR_MUTATION")
        body = strict_json(raw)
        if (type(body) is not dict or
                set(body) != {"version", "lineage", "policy", "binding", "events"} or
                body["version"] != 1 or body["lineage"] != LINEAGE or
                body["policy"] != self._policy or body["binding"] != self._binding or
                type(body["events"]) is not list or
                len(body["events"]) != self._checkpoint.generation or
                len(body["events"]) > MAX_EVENTS):
            reject("JOURNAL")
        if canonical(body) != raw:
            reject("JOURNAL")
        return body

    def _append(self, event):
        body = self._read()
        if len(body["events"]) >= MAX_EVENTS:
            reject("CAPACITY")
        body["events"].append(event)
        raw = canonical(body)
        tmp = self._path.with_name(self._path.name + ".pending")
        try:
            with tmp.open("xb") as f:
                f.write(raw)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, self._path)
        except OSError:
            reject("STORAGE")
        self._checkpoint = Checkpoint(len(body["events"]), hashlib.sha256(raw).hexdigest())

    def _state(self):
        try:
            return self._validated_state()
        except AttendanceError:
            raise
        except (KeyError, TypeError, ValueError, RecursionError):
            reject("JOURNAL")

    def _validated_state(self):
        state = {"challenges": {}, "counter": 0, "sequence": 0}
        for event in self._read()["events"]:
            if type(event) is not dict:
                reject("JOURNAL")
            if event.get("kind") == "issue":
                if set(event) != {"kind", "challenge"}:
                    reject("JOURNAL")
                c = event["challenge"]
                expected = {"purpose", "lineage", "incident", "operation", "nonce",
                            "sequence", "previous_status", "policy", "binding",
                            "issued_utc_ms", "expires_utc_ms", "issued_monotonic_ms",
                            "expires_monotonic_ms", "epoch", "one_use"}
                if type(c) is not dict or set(c) != expected:
                    reject("JOURNAL")
                for field in ("incident", "operation", "epoch", "nonce"):
                    text(c[field])
                prior = list(state["challenges"].values())
                if (c["purpose"] != PURPOSE or c["lineage"] != LINEAGE or
                        c["policy"] != self._policy or c["binding"] != self._binding or
                        c["one_use"] is not True or type(c["sequence"]) is not int or
                        c["sequence"] != state["sequence"] + 1 or
                        c["nonce"] in state["challenges"] or len(c["nonce"]) != 43 or
                        any(x not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
                            for x in c["nonce"]) or
                        c["previous_status"] != (prior[-1]["state"] if prior else "NONE") or
                        any(v["state"] in {"OUTSTANDING", "VERIFYING"} for v in prior)):
                    reject("JOURNAL")
                for start, end in (("issued_utc_ms", "expires_utc_ms"),
                                   ("issued_monotonic_ms", "expires_monotonic_ms")):
                    if (type(c[start]) is not int or c[start] < 0 or
                            type(c[end]) is not int or
                            c[end] != c[start] + self._policy["ttl_ms"]):
                        reject("JOURNAL")
                state["challenges"][c["nonce"]] = {"challenge": c, "state": "OUTSTANDING"}
                state["sequence"] = c["sequence"]
            elif event.get("kind") == "close":
                if (set(event) not in ({"kind", "nonce", "state"},
                                      {"kind", "nonce", "state", "counter"}) or
                        type(event["nonce"]) is not str or
                        event["nonce"] not in state["challenges"] or
                        event["state"] not in {"VERIFYING", "REFUSED", "CONSUMED", "AMBIGUOUS"}):
                    reject("JOURNAL")
                previous = state["challenges"][event["nonce"]]["state"]
                allowed = {"OUTSTANDING": {"VERIFYING", "AMBIGUOUS"},
                           "VERIFYING": {"REFUSED", "CONSUMED", "AMBIGUOUS"}}
                if event["state"] not in allowed.get(previous, set()):
                    reject("JOURNAL")
                if (event["state"] == "CONSUMED") != ("counter" in event):
                    reject("JOURNAL")
                if "counter" in event:
                    value = event["counter"]
                    if (type(value) is not int or not 0 <= value <= 0xffffffff or
                            ((state["counter"] or value) and value <= state["counter"])):
                        reject("JOURNAL")
                    state["counter"] = event["counter"]
                state["challenges"][event["nonce"]]["state"] = event["state"]
            else:
                reject("JOURNAL")
        return state

    def issue(self, incident, operation, sample):
        with self._lock:
            text(incident); text(operation); sample.validate()
            state = self._state()
            if any(v["state"] in {"OUTSTANDING", "VERIFYING"}
                   for v in state["challenges"].values()):
                reject("OUTSTANDING")
            c = {"purpose": PURPOSE, "lineage": LINEAGE, "incident": incident,
                 "operation": operation, "nonce": b64(secrets.token_bytes(32)),
                 "sequence": state["sequence"] + 1,
                 "previous_status": list(state["challenges"].values())[-1]["state"]
                 if state["challenges"] else "NONE",
                 "policy": self._policy, "binding": self._binding,
                 "issued_utc_ms": sample.utc_ms,
                 "expires_utc_ms": sample.utc_ms + self._policy["ttl_ms"],
                 "issued_monotonic_ms": sample.monotonic_ms,
                 "expires_monotonic_ms": sample.monotonic_ms + self._policy["ttl_ms"],
                 "epoch": sample.epoch, "one_use": True}
            self._append({"kind": "issue", "challenge": c})
            return copy.deepcopy(c)

    def begin(self, challenge):
        # Reserve a delivery before cryptographic work. Any later failure is terminal.
        state = self._state()
        if type(challenge) is not dict or type(challenge.get("nonce")) is not str:
            reject("MALFORMED")
        record = state["challenges"].get(challenge["nonce"])
        if record is None:
            reject("UNKNOWN_CHALLENGE")
        if record["state"] != "OUTSTANDING":
            reject("REPLAY")
        if challenge != record["challenge"]:
            reject("CHALLENGE_SUBSTITUTION")
        self._append({"kind": "close", "nonce": challenge["nonce"], "state": "VERIFYING"})
        return state["counter"]

    def finish(self, nonce, status, counter=None):
        current = self._state()["challenges"].get(nonce)
        if (current is None or current["state"] != "VERIFYING" or
                status not in {"CONSUMED", "REFUSED", "AMBIGUOUS"} or
                (status == "CONSUMED") != (counter is not None)):
            reject("STATE")
        event = {"kind": "close", "nonce": nonce, "state": status}
        if counter is not None:
            event["counter"] = counter
        self._append(event)

    def ambiguous(self, challenge):
        with self._lock:
            self.begin(challenge)
            self.finish(challenge["nonce"], "AMBIGUOUS")


@dataclass(frozen=True)
class AttendanceEvidenceRecord:
    """A lab verifier result, never an operational Owner-presence capability."""
    result: str
    subject: bytes
    head: str

    def record(self):
        body = {"version": 1, "lineage": LINEAGE, "purpose": PURPOSE,
                "result": self.result, "subject": strict_json(self.subject),
                "result_sequence": strict_json(self.subject)["sequence"],
                "head": self.head, "owner_presence": "UNKNOWN",
                "source_custody": "UNQUALIFIED", "authority": "NONE",
                "dispatch_requested": False}
        return {**body, "integrity_sha256": digest(body)}

    def matches(self, supplied):
        return type(supplied) is dict and supplied == self.record()
        # Matching a retained record is not independent evidence-store custody.


class WebAuthnAttendanceVerifier:
    """Bounded ES256 assertion checking, not WebAuthn enrollment/attestation."""
    def __init__(self, ledger, policy, binding):
        binding.validate()
        if ledger._policy != policy.record() or ledger._binding != binding.fingerprint():
            reject("POLICY_BINDING")
        self.ledger, self.policy, self.binding = ledger, policy, binding

    def verify(self, challenge, assertion, *, incident, operation, sample):
        with self.ledger._lock:
            previous_counter = self.ledger.begin(challenge)
            try:
                counter = self._verify(challenge, assertion, incident, operation, sample,
                                       max(previous_counter, self.binding.initial_counter))
            except Exception:
                self.ledger.finish(challenge["nonce"], "REFUSED")
                raise
            self.ledger.finish(challenge["nonce"], "CONSUMED", counter)
            return AttendanceEvidenceRecord("ASSERTION_VALIDATED_IN_LAB_MODEL",
                                             canonical(challenge),
                                             self.ledger.checkpoint.head)

    def _verify(self, c, a, incident, operation, sample, previous):
        sample.validate()
        if c["incident"] != incident or c["operation"] != operation:
            reject("CONTEXT")
        if c["policy"] != self.policy.record() or c["binding"] != self.binding.fingerprint():
            reject("POLICY_BINDING")
        if (sample.epoch != c["epoch"] or sample.utc_ms < c["issued_utc_ms"] or
                sample.monotonic_ms < c["issued_monotonic_ms"] or
                sample.utc_ms >= c["expires_utc_ms"] or
                sample.monotonic_ms >= c["expires_monotonic_ms"]):
            reject("STALE_OR_CLOCK")
        if type(a) is not dict or set(a) != {
                "credential_id", "client_data_json", "authenticator_data", "signature"}:
            reject("ASSERTION")
        if any(type(a[k]) is not bytes for k in a):
            reject("ASSERTION")
        if a["credential_id"] != self.binding.credential_id:
            reject("CREDENTIAL")
        client = strict_json(a["client_data_json"])
        if type(client) is not dict or set(client) != {"type", "challenge", "origin", "crossOrigin"}:
            reject("CLIENT_DATA")
        if (client["type"] != "webauthn.get" or
                client["challenge"] != b64(canonical(c)) or
                client["origin"] != self.policy.origin or client["crossOrigin"] is not False):
            reject("CLIENT_CONTEXT")
        auth = a["authenticator_data"]
        if len(auth) != 37 or len(a["signature"]) > 80:
            reject("AUTH_DATA")
        if auth[:32] != hashlib.sha256(self.policy.rp_id.encode("utf-8")).digest():
            reject("RP")
        flags = auth[32]
        if flags & ~5:  # this deliberately narrow profile rejects backup/extensions/RFU
            reject("UNSUPPORTED_FLAGS")
        if not flags & 1:
            reject("UP")
        if self.policy.require_uv and not flags & 4:
            reject("UV")
        counter = int.from_bytes(auth[33:], "big")
        if (previous != 0 or counter != 0) and counter <= previous:
            reject("COUNTER")
        try:
            key = ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256R1(),
                                                             self.binding.public_point)
            key.verify(a["signature"], auth + hashlib.sha256(a["client_data_json"]).digest(),
                       ec.ECDSA(hashes.SHA256()))
        except (ValueError, InvalidSignature):
            reject("SIGNATURE")
        return counter


def real_ceremony_readiness():
    """No discovery/API/UI calls: explicit incomplete prerequisite descriptor."""
    return {"state": "OWNER_PHYSICAL_PRESENCE_REQUIRED", "ceremony_performed": False,
            "credential_enrolled": False, "private_capability_custody": "UNKNOWN",
            "protected_consumer": "UNKNOWN", "native_call_implemented": False,
            "required": ["accepted exact source/enrollment binding",
                         "protected client/display/verifier/checkpoint custody",
                         "separately authorized Owner-direct ceremony"],
            "authority": "NONE", "lineage": LINEAGE}

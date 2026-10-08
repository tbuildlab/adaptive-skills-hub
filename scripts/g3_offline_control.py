"""Closed storage encoding and synthetic crash model. OFFLINE / TEST / NO AUTHORITY.

There is no persistence, login, network, production promotion or dispatch API.
The schemas validate closed row shapes; typed record bodies/source authenticity
and complete production semantic joins are deliberately not implemented.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import re
from types import MappingProxyType

from scripts.g3_production_metadata import canonical_bytes, parse_json, MetadataError

BASIS = "OFFLINE_TEST_NO_AUTHORITY"
VERSION = "nexus.g3.n01-control.v1"
NAMESPACES = tuple(sorted(("bindings", "contexts", "challenges", "views", "decisions",
    "receipts", "grants", "revocations", "nonce_consumption", "intent_indexes",
    "claim_indexes", "retirement", "provenance")))
_TOKEN = re.compile(r"[a-z0-9][a-z0-9._:-]{0,95}\Z")
_HEX = re.compile(r"[0-9a-f]{64}\Z")
_MAX = 2**63 - 1


class OfflineError(ValueError):
    """Fixed diagnostic; never echo untrusted material."""


def require(condition):
    if not condition:
        raise OfflineError("G3_OFFLINE_REJECTED")


def digest(raw):
    require(type(raw) is bytes)
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    try:
        return canonical_bytes(value)
    except (MetadataError, UnicodeError, RecursionError):
        raise OfflineError("G3_OFFLINE_REJECTED") from None


def decode(raw):
    require(type(raw) is bytes)
    try:
        value = parse_json(raw)
    except (MetadataError, UnicodeError, RecursionError):
        raise OfflineError("G3_OFFLINE_REJECTED") from None
    require(canonical(value) == raw)
    return value


# namespace, identity field, exact type descriptor per additional field.
# Types: t token, s text, h SHA256, u uint, g positive generation, p Principal,
# e EvidenceRef, r:<kind> RecordRef, ? nullable, l:<kind> sorted unique refs,
# | closed enum. These are storage shapes, not generic authorizing policies.
_SPECS = {
 "root": ("provenance", "authority_instance", "authority_instance:t authority_epoch:g incarnation:t recovery_sequence:u previous_checkpoint:?r:recovery-checkpoint time_high_water_ms:u quarantine:OPEN|CLOSED revocation_generation:g"),
 "binding": ("bindings", "binding_id", "binding_id:t principal:p owner_generation:g workspace_id:t project_id:t binding_generation:g state:CURRENT|RETIRED"),
 "context": ("contexts", "context_id", "context_id:t context_generation:g binding_id:t binding_generation:g owner_generation:g authority_epoch:g incarnation:t provider_project:s provider_user:s provider_session:s authenticated_at_ms:u expires_at_ms:u identity_evidence:e session_evidence:e state:CURRENT|CONSUMED|RETIRED"),
 "challenge": ("challenges", "challenge_id", "challenge_id:t record_ref:r:authority-challenge context_id:t view_id:t nonce:h expires_at_ms:u state:PENDING|CONFIRM|DENY|RETIRED"),
 "view": ("views", "view_id", "view_id:t record_ref:r:presentation-view context_id:t challenge_id:t presentation_sha256:h template_revision:t deployment_revision:t state:CURRENT|RETIRED"),
 "decision": ("decisions", "challenge_id", "challenge_id:t record_ref:r:owner-decision choice:CONFIRM|DENY context_id:t view_id:t nonce:h"),
 "receipt": ("receipts", "challenge_id", "challenge_id:t record_ref:r:trusted-decision-receipt decision_ref:r:owner-decision expires_at_ms:u"),
 "grant": ("grants", "grant_id", "grant_id:t record_ref:r:grant receipt_ref:r:trusted-decision-receipt issuer_registration:t state:CURRENT|CONSUMED|RETIRED use_until_ms:u"),
 "revocation": ("revocations", "index_id", "index_id:t grant_id:?t revocation_refs:l:revocation generation:g completeness:COMPLETE|INCOMPLETE state:INDEX|CLEAR|REVOKED"),
 "nonce": ("nonce_consumption", "nonce", "nonce:h challenge_id:t state:PENDING|CONSUMED|RETIRED decision_ref:?r:owner-decision"),
 "intent": ("intent_indexes", "intent_id", "intent_id:t record_ref:r:admission-intent task_id:t grant_id:t target_sha256:h payload_sha256:h registration_id:t context_id:t use_until_ms:u state:ADMIT_PENDING|DENIED|CONSUMED|RETIRED"),
 "claim": ("claim_indexes", "attempt_key", "attempt_key:t intent_id:t record_ref:r:dispatch-attempt result_ref:?r:dispatch-attempt handoff_deadline_ms:u outcome:CLAIMED|SUCCEEDED|FAILED|UNKNOWN"),
 "retirement": ("retirement", "entity_id", "entity_kind:" + "|".join(("root","binding","context","challenge","view","decision","receipt","grant","revocation","nonce","intent","claim","retirement","recovery","registration","source")) + " entity_id:t retired_sequence:u reason:EXPIRED|INVALIDATED|RESTART|REVOKED|MISMATCH"),
 "recovery": ("provenance", "sequence", "sequence:u checkpoint_ref:r:recovery-checkpoint control_sha256:h descriptor_sha256:h state:WITNESSED"),
 "registration": ("provenance", "registration_id", "registration_id:t subject_kind:t target_revision:t dispatch_revision:t adapter_revision:t environment_id:t environment_generation:g target_contract_sha256:h dispatch_contract_sha256:h config_sha256:h enforcement_sha256:h runtime_revision:t n02_revision:t issuer_ref:t state:CURRENT|RETIRED purpose:PRODUCTION|TEST_ONLY"),
 "source": ("provenance", "source_id", "source_id:t evidence_ref:e assertion_sha256:h kind:OWNER_ENROLLMENT|D01|D03|D04|TECHNICAL|TASK|HOST|G1|G2 principal:p binding_id:t context_id:?t registration_id:t observed_at_ms:u expires_at_ms:u conclusion:PASS|FAIL|UNKNOWN state:CURRENT|RETIRED"),
}
SPECS = MappingProxyType(_SPECS)


def check_type(value, descriptor):
    if descriptor.startswith("?"):
        if value is None:
            return
        return check_type(value, descriptor[1:])
    if "|" in descriptor or descriptor == "WITNESSED":
        require(type(value) is str and value in descriptor.split("|"))
    elif descriptor in ("u", "g"):
        require(type(value) is int and (1 if descriptor == "g" else 0) <= value <= _MAX)
    elif descriptor in ("t", "h"):
        require(type(value) is str and (_TOKEN if descriptor == "t" else _HEX).fullmatch(value) is not None)
    elif descriptor == "s":
        require(type(value) is str and 0 < len(value) <= 512)
        canonical(value)
    elif descriptor == "p":
        require(type(value) is dict and set(value) == {"issuer", "client_id", "subject"})
        for item in value.values():
            check_type(item, "s")
    elif descriptor == "e":
        require(type(value) is dict and set(value) == {"ref", "sha256"})
        check_type(value["ref"], "t"); check_type(value["sha256"], "h")
    elif descriptor.startswith("r:"):
        require(type(value) is dict and set(value) == {"id", "body_sha256"})
        kind = descriptor[2:]
        prefix = ("nexus.g3." if kind in ("grant", "revocation") else "nexus.g3.production.") + kind + ".v1:"
        require(type(value["id"]) is str and value["id"].startswith(prefix))
        check_type(value["id"][len(prefix):], "h"); check_type(value["body_sha256"], "h")
    elif descriptor.startswith("l:"):
        require(type(value) is list and len(value) <= 64)
        for item in value:
            check_type(item, "r:" + descriptor[2:])
        ids = [item["id"] for item in value]
        require(ids == sorted(set(ids)))
    else:
        require(False)


@dataclass(frozen=True)
class ControlRow:
    """Immutable closed encoding result; has no authority or issuer semantics."""
    namespace: str
    key: str
    value: bytes

    def __post_init__(self):
        require(type(self.namespace) is str and self.namespace in NAMESPACES)
        body = decode(self.value)
        require(type(body) is dict and type(body.get("family")) is str and body["family"] in SPECS)
        family = body["family"]
        namespace, identity, specification = SPECS[family]
        descriptors = dict(item.split(":", 1) for item in specification.split())
        require(set(body) == {"schema_version", "family", "revision"} | set(descriptors))
        require(body["schema_version"] == VERSION and namespace == self.namespace)
        check_type(body["revision"], "g")
        for field, descriptor in descriptors.items():
            check_type(body[field], descriptor)
        key_part = str(body[identity])
        if family == "recovery":
            key_part = f'{body[identity]:020d}'
        elif family == "retirement":
            key_part = body["entity_kind"] + ":" + key_part
        require(type(self.key) is str and self.key == family + ":" + key_part and len(self.key) <= 512)
        require(len(self.value) <= 16384)
        if family == "context":
            require(0 < body["expires_at_ms"] - body["authenticated_at_ms"] <= 300000)
        if family == "source":
            require(body["observed_at_ms"] < body["expires_at_ms"])
        if family == "root":
            require((body["previous_checkpoint"] is None) == (body["recovery_sequence"] == 0))
        if family == "revocation":
            require((body["grant_id"] is None) == (body["state"] == "INDEX"))
            require(body["index_id"] == ("authority" if body["grant_id"] is None else body["grant_id"]))
            if body["state"] == "REVOKED":
                require(len(body["revocation_refs"]) > 0)
        if family == "nonce" and body["state"] == "CONSUMED":
            require(body["decision_ref"] is not None)
        if family == "claim":
            require((body["result_ref"] is None) == (body["outcome"] == "CLAIMED"))

    @property
    def authority(self):
        return "NONE"

    @classmethod
    def from_value(cls, body):
        require(type(body) is dict and type(body.get("family")) is str and body["family"] in SPECS)
        family = body["family"]
        namespace, field, _ = SPECS[family]
        require(field in body)
        part = str(body[field])
        if family == "recovery":
            check_type(body[field], "u"); part = f'{body[field]:020d}'
        elif family == "retirement":
            require(type(body.get("entity_kind")) is str); part = body["entity_kind"] + ":" + part
        return cls(namespace, family + ":" + part, canonical(body))


@dataclass(frozen=True)
class EncodedSnapshot:
    root: bytes
    pages: tuple[bytes, ...]

    @property
    def control_after_sha256(self):
        return digest(self.root)

    @property
    def authority(self):
        return "NONE"


def encode_snapshot(rows):
    """Closed rows + header agreement, not full production semantic qualification."""
    require(type(rows) is tuple and 1 <= len(rows) <= 4096)
    require(all(type(row) is ControlRow for row in rows))
    for row in rows:
        ControlRow(row.namespace,row.key,row.value)
    ordered = sorted(rows, key=lambda row: (row.namespace.encode(), row.key.encode()))
    require(len({(row.namespace, row.key) for row in ordered}) == len(ordered))
    roots = [decode(row.value) for row in ordered if decode(row.value)["family"] == "root"]
    require(len(roots) == 1)
    root = roots[0]
    for row in ordered:
        value = decode(row.value)
        if value["family"] == "recovery":
            require(value["sequence"] < root["recovery_sequence"])
    pages = []
    references = []
    for namespace in NAMESPACES:
        pending = []
        def page_bytes(items):
            return canonical({"codec_version": "nexus.g3.control-page.v1", "namespace": namespace, "rows": items})
        def flush():
            if pending:
                raw = page_bytes(pending)
                pages.append(raw)
                references.append(dict(namespace=namespace,first_key=pending[0]["key"],
                    last_key=pending[-1]["key"],row_count=len(pending),page_sha256=digest(raw)))
                pending.clear()
        for row in ordered:
            if row.namespace != namespace:
                continue
            item = dict(key=row.key,value_canonical_utf8=row.value.decode(),value_sha256=digest(row.value))
            if len(pending) == 64:
                flush()
            try:
                page_bytes(pending + [item])
            except OfflineError:
                require(len(pending) > 0); flush(); page_bytes([item])
            pending.append(item)
        flush()
    require(len(references) <= 64)
    header = {field: root[field] for field in ("authority_instance","authority_epoch","incarnation","recovery_sequence","time_high_water_ms")}
    header.update(codec_version="nexus.g3.control-snapshot.v1", inventory=list(NAMESPACES),pages=references)
    return EncodedSnapshot(canonical(header), tuple(pages))


def verify_snapshot(snapshot):
    """Verify exact closed encoding/readback; never authenticate its origin."""
    require(type(snapshot) is EncodedSnapshot and type(snapshot.pages) is tuple)
    header = decode(snapshot.root)
    require(type(header) is dict and set(header) == {"codec_version","authority_instance","authority_epoch",
        "incarnation","recovery_sequence","time_high_water_ms","inventory","pages"})
    require(header["codec_version"] == "nexus.g3.control-snapshot.v1")
    require(header["inventory"] == list(NAMESPACES))
    require(type(header["pages"]) is list and len(header["pages"]) == len(snapshot.pages) <= 64)
    rows=[]
    for raw,reference in zip(snapshot.pages,header["pages"]):
        require(type(reference) is dict and set(reference) == {"namespace","first_key","last_key","row_count","page_sha256"})
        require(digest(raw)==reference["page_sha256"])
        page=decode(raw)
        require(type(page) is dict and set(page)=={"codec_version","namespace","rows"})
        require(page["codec_version"]=="nexus.g3.control-page.v1" and page["namespace"]==reference["namespace"])
        require(type(page["rows"]) is list and 1<=len(page["rows"])<=64)
        require(type(reference["row_count"]) is int and reference["row_count"]==len(page["rows"]))
        keys=[]
        for item in page["rows"]:
            require(type(item) is dict and set(item)=={"key","value_canonical_utf8","value_sha256"})
            require(type(item["value_canonical_utf8"]) is str)
            value=item["value_canonical_utf8"].encode("utf-8")
            require(digest(value)==item["value_sha256"])
            rows.append(ControlRow(page["namespace"],item["key"],value));keys.append(item["key"])
        require(keys==sorted(set(keys),key=lambda key:key.encode()))
        require(keys[0]==reference["first_key"] and keys[-1]==reference["last_key"])
    # Re-encoding rejects omitted root, overlapping pages, header mismatch and
    # non-deterministic splitting. Complete semantic joins remain a future gate.
    require(encode_snapshot(tuple(rows))==snapshot)
    return tuple(rows)


@dataclass(frozen=True)
class SyntheticMaterial:
    target: bytes
    payload: bytes
    target_revision: str = "synthetic.target.v1"
    dispatch_revision: str = "synthetic.dispatch.v1"
    adapter_revision: str = "fake.v1"
    environment: str = "test-only"
    environment_generation: int = 1

    def validate(self):
        require(type(self) is SyntheticMaterial)
        require((self.target_revision,self.dispatch_revision,self.adapter_revision,self.environment) ==
                ("synthetic.target.v1","synthetic.dispatch.v1","fake.v1","test-only"))
        require(type(self.environment_generation) is int and self.environment_generation == 1)
        target, payload = decode(self.target), decode(self.payload)
        require(type(target) is dict and set(target) == {"resource","content"})
        require(target["resource"] == "test-only:buffer")
        check_type(target["content"], "s"); require(len(target["content"]) <= 256)
        require(type(payload) is dict and set(payload) == {"operation","arguments"})
        require(payload["operation"] == "echo" and payload["arguments"] == [target["content"]])

    @property
    def authority(self):
        return "NONE"


def reference_material(content="synthetic"):
    material = SyntheticMaterial(canonical(dict(resource="test-only:buffer",content=content)),
                                 canonical(dict(operation="echo",arguments=[content])))
    material.validate()
    return material


@dataclass(frozen=True)
class FakeSessionEvidence:
    """A test observation, never a real Stytch credential or authenticated user."""
    principal: str = "test-owner"
    session: str = "test-session"
    observed_at_ms: int = 1000
    verdict: str = "TEST_VALID"


@dataclass(frozen=True)
class TestState:
    sequence: int = 0
    epoch: int = 1
    incarnation: str = "test-incarnation-1"
    time_ms: int = 0
    context_expiry: int = 301000
    context_state: str = "CURRENT"
    nonce_state: str = "PENDING"
    decision: str = "NONE"
    grant: str = "NONE"
    revocation_generation: int = 1
    revocation_complete: str = "COMPLETE"
    revoked: str = "NO"
    intent: str = "NONE"
    intent_expiry: int = 0
    claim: str = "NONE"
    claim_sequence: int = 0
    handoff_deadline: int = 0
    result: str = "NONE"


@dataclass(frozen=True)
class TestCheckpoint:
    """Fake journal bytes, deliberately not a D05 R07 record."""
    sequence: int
    previous: str
    after_sha256: str

    @property
    def id(self):
        return digest(canonical(dict(test_only=BASIS, sequence=self.sequence,
                                     previous=self.previous,after_sha256=self.after_sha256)))


def test_state_digest(state):
    require(type(state) is TestState)
    return digest(canonical(dict(test_only=BASIS, **state.__dict__)))


class FakeFence:
    """Independent in-memory history for tests; no real enforcement is claimed."""
    def __init__(self, state):
        require(type(state) is TestState and state.sequence == 0)
        self.history = (TestCheckpoint(0, "0"*64, test_state_digest(state)),)

    def validate(self):
        require(type(self.history) is tuple and len(self.history) > 0)
        prior = "0"*64
        for index, entry in enumerate(self.history):
            require(type(entry) is TestCheckpoint and type(entry.sequence) is int and entry.sequence == index)
            check_type(entry.after_sha256,"h"); require(entry.previous == prior)
            prior = entry.id

    def append(self, state, previous):
        self.validate()
        require(state.sequence == len(self.history) and previous == self.history[-1].id)
        self.history += (TestCheckpoint(state.sequence,previous,test_state_digest(state)),)


class FakeAuthorityModel:
    """Fixture state transitions only. No actual grants/receipts/admission output.

    PREPARED -> fake witness -> finalize; all interruptions close the model.
    Test callers can tamper Python memory; none of it constitutes trusted state.
    """
    def __init__(self, material=None):
        self.material = reference_material() if material is None else material
        self.material.validate()
        self.state = TestState()
        self.fence = FakeFence(self.state)
        self.head = self.fence.history[-1].id
        self.pending = None
        self.closed = False
        self._observed_attempts = set()

    @property
    def authority(self):
        return "NONE"

    @property
    def basis(self):
        return BASIS

    def promote_to_production(self):
        raise OfflineError("FAKE_AUTHORITY_PROMOTION_FORBIDDEN")

    def _consistent(self):
        try:
            self.fence.validate()
            require(self.state.sequence == len(self.fence.history)-1)
            require(self.head == self.fence.history[-1].id)
            require(test_state_digest(self.state) == self.fence.history[-1].after_sha256)
        except OfflineError:
            self.closed = True
            raise

    def _context(self, now, evidence):
        require(self.state.context_state in ("CURRENT","CONSUMED") and 1000 <= now < self.state.context_expiry)
        require(type(evidence) is FakeSessionEvidence)
        require(evidence.principal == "test-owner" and evidence.session == "test-session")
        require(type(evidence.observed_at_ms) is int and evidence.observed_at_ms == now)
        require(evidence.verdict == "TEST_VALID")

    def _material(self, material):
        require(type(material) is SyntheticMaterial)
        material.validate()
        require(material == self.material)

    def prepare(self, action, *, now=1000, evidence=None, material=None, result=None, expected_sequence=None):
        require(type(action) is str)
        require(not self.closed and self.pending is None)
        self._consistent()
        check_type(now,"u"); require(now >= self.state.time_ms)
        if expected_sequence is not None:
            require(type(expected_sequence) is int and expected_sequence == self.state.sequence)
        s = self.state
        changes = {}
        if action in ("CONFIRM","DENY"):
            self._context(now,evidence)
            require(s.nonce_state == "PENDING" and s.decision == "NONE")
            changes = dict(nonce_state="CONSUMED",context_state="CONSUMED",decision=action)
        elif action == "GRANT_MODEL":
            self._context(now,evidence)
            require(s.decision == "CONFIRM" and s.grant == "NONE" and s.revoked == "NO")
            changes = dict(grant="TEST_CURRENT")
        elif action == "REVOKE_MODEL":
            require(s.grant != "NONE" and s.revoked == "NO")
            require(s.revocation_generation < _MAX)
            changes = dict(revoked="YES",revocation_generation=s.revocation_generation+1)
        elif action == "INCOMPLETE_INDEX_TEST":
            changes = dict(revocation_complete="INCOMPLETE")
        elif action == "INTENT_MODEL":
            self._context(now,evidence);self._material(material)
            require(s.grant == "TEST_CURRENT" and s.revoked == "NO" and s.revocation_complete == "COMPLETE")
            require(s.intent == "NONE" and s.claim == "NONE")
            changes = dict(intent="TEST_PENDING",intent_expiry=min(now+60000,s.context_expiry))
        elif action == "CLAIM_MODEL":
            self._context(now,evidence);self._material(material)
            require(s.grant == "TEST_CURRENT" and s.revoked == "NO" and s.revocation_complete == "COMPLETE")
            require(s.intent == "TEST_PENDING" and now < s.intent_expiry and s.claim == "NONE")
            changes = dict(intent="TEST_CONSUMED",grant="TEST_CONSUMED",claim="TEST_CLAIMED",
                           claim_sequence=s.sequence+1,
                           handoff_deadline=min(now+1000,s.intent_expiry,s.context_expiry))
        elif action == "RESULT_MODEL":
            require(s.claim == "TEST_CLAIMED" and s.result == "NONE" and result in ("SUCCEEDED","FAILED","UNKNOWN"))
            changes = dict(result=result)
        elif action == "INVALIDATE_MODEL":
            changes = dict(context_state="RETIRED",nonce_state="RETIRED" if s.nonce_state=="PENDING" else s.nonce_state,
                           intent="TEST_RETIRED" if s.intent=="TEST_PENDING" else s.intent,
                           grant="TEST_RETIRED" if s.grant=="TEST_CURRENT" else s.grant)
        else:
            require(False)
        require(s.sequence < _MAX)
        candidate = replace(s,sequence=s.sequence+1,time_ms=now,**changes)
        self.pending = (candidate,self.head)

    def witness(self):
        require(not self.closed and self.pending is not None)
        candidate, previous = self.pending
        try:
            self.fence.append(candidate,previous)
        except OfflineError:
            self.closed = True
            raise

    def finalize(self):
        require(not self.closed and self.pending is not None)
        candidate, previous = self.pending
        try:
            self.fence.validate()
            require(self.head == previous and candidate.sequence == self.state.sequence+1)
            tail = self.fence.history[-1]
            require(tail.sequence == candidate.sequence and tail.previous == previous and tail.after_sha256 == test_state_digest(candidate))
        except OfflineError:
            self.closed = True
            raise
        self.state = candidate; self.head = tail.id; self.pending = None

    def transact(self, action, **kwargs):
        self.prepare(action,**kwargs);self.witness();self.finalize()
        return BASIS

    def crash(self):
        self.closed = True

    def restored_for_test(self, old_state, old_head):
        """Keep independent history; restoring ledger alone never resets the fence."""
        self.state=old_state;self.head=old_head;self.pending=None;self.closed=True

    def check_restore(self):
        self._consistent()
        require(not self.closed)  # Even matching restored bytes require new incarnation.

    def recover_for_test(self):
        """Synthetic reconciliation, retiring contexts; not a recovery authority API."""
        require(self.closed)
        self.fence.validate()
        tail = self.fence.history[-1]
        if self.pending is not None:
            candidate, previous = self.pending
            require(tail.sequence == candidate.sequence and tail.previous == previous and
                    tail.after_sha256 == test_state_digest(candidate))
            self.state = candidate; self.head = tail.id; self.pending = None
        self._consistent()
        s = self.state
        require(s.epoch < _MAX and s.sequence < _MAX)
        recovered = replace(s,sequence=s.sequence+1,epoch=s.epoch+1,
            incarnation=f"test-incarnation-{s.epoch+1}",context_state="RETIRED",
            nonce_state="RETIRED" if s.nonce_state=="PENDING" else s.nonce_state,
            grant="TEST_RETIRED" if s.grant=="TEST_CURRENT" else s.grant,
            intent="TEST_RETIRED" if s.intent=="TEST_PENDING" else s.intent,
            result="UNKNOWN" if s.claim=="TEST_CLAIMED" and s.result=="NONE" else s.result)
        self.fence.append(recovered,self.head)
        self.state=recovered;self.head=self.fence.history[-1].id;self.closed=False

    def handoff_observation(self, material, *, now):
        """Return a test digest only. No provider, execution or effect function exists."""
        require(not self.closed and self.pending is None)
        self._consistent();self._material(material);check_type(now,"u")
        require(self.state.claim=="TEST_CLAIMED" and self.state.result=="NONE")
        require(self.state.revoked=="NO" and self.state.revocation_complete=="COMPLETE")
        require(self.state.context_state!="RETIRED" and self.state.claim_sequence not in self._observed_attempts)
        require(self.state.time_ms <= now < self.state.handoff_deadline)
        self._observed_attempts.add(self.state.claim_sequence)
        return (BASIS,digest(material.payload))

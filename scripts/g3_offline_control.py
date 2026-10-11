"""Synthetic offline crash model; encoding uses the unchanged shared codec.

No production authority, persistence, network, login or dispatch.
"""
from dataclasses import dataclass, replace
from ash.g3_control_codec import (
    BASIS,
    VERSION,
    NAMESPACES,
    _TOKEN,
    _HEX,
    _MAX,
    OfflineError,
    require,
    digest,
    canonical,
    decode,
    _SPECS,
    SPECS,
    check_type,
    ControlRow,
    EncodedSnapshot,
    encode_snapshot,
    verify_snapshot
)
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

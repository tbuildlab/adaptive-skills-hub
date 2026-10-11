"""Fixed N01 PREPARED contract for nine accepted transaction groups.

Pure preparation and comparison only. Independent custody, qualified provenance,
durable reservation/finalization and fresh runtime checks remain mandatory.
Prepared bytes never issue a receipt, grant, claim or execution permission.
"""
from dataclasses import dataclass
from ash import g3_control_codec as c
from ash import g3_record_codec as r
from ash.g3_control_semantics import CheckedControl, ControlError, require


GROUPS = {
    "T1": ({"CHALLENGE"}, {"context", "challenge", "nonce", "view"}),
    "T2": ({"CHALLENGE", "INVALIDATE"}, {"view", "challenge", "context", "nonce", "retirement"}),
    "T3": ({"CONFIRM", "DENY"}, {"context", "challenge", "decision", "receipt", "nonce"}),
    "T4": ({"EVALUATE"}, {"grant", "revocation"}),
    "T5": ({"REVOKE", "INVALIDATE"}, {"binding", "context", "challenge", "view", "grant", "revocation", "nonce", "intent", "registration", "retirement"}),
    "T6": ({"EVALUATE"}, {"intent"}),
    "T7": ({"CLAIM"}, {"intent", "grant", "claim"}),
    "T8": ({"RESULT"}, {"claim"}),
    "T9": ({"RECOVER"}, {"context", "challenge", "view", "grant", "nonce", "intent", "claim", "retirement"}),
}
_STATES = {
    "binding": {"CURRENT": {"RETIRED"}},
    "context": {"CURRENT": {"CONSUMED", "RETIRED"}},
    "challenge": {"PENDING": {"CONFIRM", "DENY", "RETIRED"}},
    "view": {"CURRENT": {"RETIRED"}},
    "grant": {"CURRENT": {"CONSUMED", "RETIRED"}, "CONSUMED": {"RETIRED"}},
    "nonce": {"PENDING": {"CONSUMED", "RETIRED"}},
    "intent": {"ADMIT_PENDING": {"CONSUMED", "RETIRED"}},
    "claim": {"CLAIMED": {"SUCCEEDED", "FAILED", "UNKNOWN"}},
    "registration": {"CURRENT": {"RETIRED"}},
    "source": {"CURRENT": {"RETIRED"}},
}


@dataclass(frozen=True)
class Preparation:
    group: str
    expected_checkpoint: bytes
    checkpoint: bytes
    descriptor: bytes
    snapshot: c.EncodedSnapshot

    @property
    def authority(self):
        return "NONE"

    @property
    def reservation_digest(self):
        return c.digest(self.checkpoint)


def checkpoint_ref(raw):
    value = r.parse_metadata(raw)
    require(value.to_dict()["schema_version"] == r.PREFIX + "recovery-checkpoint.v1")
    return dict(id=value.record_id, body_sha256=value.body_sha256)


def _prepare(before, after, checkpoint, group, transition, record_refs):
    require(type(before) is CheckedControl and type(after) is CheckedControl)
    require(group in GROUPS and transition in GROUPS[group][0])
    require(type(record_refs) is list)
    # Recheck the immutable encoding instead of trusting a constructed dataclass.
    require(c.verify_snapshot(before.snapshot) == before.rows)
    require(c.verify_snapshot(after.snapshot) == after.rows)
    old = {row.key:c.decode(row.value) for row in before.rows}
    new = {row.key:c.decode(row.value) for row in after.rows}
    require(set(old) <= set(new))  # No compaction, omitted consumption or TTL deletion.
    prior = next(value for value in old.values() if value["family"] == "root")
    current = next(value for value in new.values() if value["family"] == "root")
    previous = r.parse_metadata(checkpoint).to_dict()
    require(previous["authority_instance"] == prior["authority_instance"])
    for field in ("authority_epoch", "incarnation", "recovery_sequence", "time_high_water_ms"):
        require(previous[field] == prior[field])
    prior_descriptor = {key:value for key,value in previous.items()
                        if key not in ("schema_version", "ledger_commit_sha256")}
    prior_descriptor["control_after_sha256"] = before.snapshot.control_after_sha256
    require(r.domain_digest(r.PREFIX + "ledger-commit.v1", prior_descriptor)
            == previous["ledger_commit_sha256"])
    require(current["authority_instance"] == prior["authority_instance"])
    require(current["recovery_sequence"] == prior["recovery_sequence"] + 1)
    require(current["previous_checkpoint"] == checkpoint_ref(checkpoint))
    require(current["time_high_water_ms"] >= prior["time_high_water_ms"])
    require(current["revocation_generation"] in (prior["revocation_generation"], prior["revocation_generation"] + 1))
    if transition == "RECOVER":
        require(current["authority_epoch"] == prior["authority_epoch"] + 1)
        require(current["incarnation"] != prior["incarnation"])
        for value in new.values():
            if value["family"] in ("context", "challenge", "view", "grant", "nonce", "intent"):
                require(value.get("state") not in ("CURRENT", "PENDING", "ADMIT_PENDING"))
    else:
        require((current["authority_epoch"], current["incarnation"]) == (prior["authority_epoch"], prior["incarnation"]))
        require(not (prior["quarantine"] == "CLOSED" and current["quarantine"] == "OPEN"))
    allowed = GROUPS[group][1] | {"root", "recovery", "source"}
    for key, value in new.items():
        former = old.get(key)
        if former == value:
            continue
        family = value["family"]
        require(family in allowed)
        if former is None:
            require(value["revision"] == 1)
            continue
        require(value["revision"] == former["revision"] + 1)
        if family == "root":
            continue
        if family == "revocation":
            require(former["state"] != "REVOKED" or value["state"] == "REVOKED")
            require(value["generation"] >= former["generation"])
            require(all(ref in value["revocation_refs"] for ref in former["revocation_refs"]))
            mutable = {"revision", "state", "generation", "revocation_refs"}
        else:
            state_field = "outcome" if family == "claim" else "state"
            require(family in _STATES)
            require(value[state_field] in _STATES[family].get(former[state_field], set()))
            mutable = {"revision", state_field}
            if family == "nonce":
                mutable.add("decision_ref")
            if family == "claim":
                mutable.add("result_ref")
        require({k:v for k,v in former.items() if k not in mutable} ==
                {k:v for k,v in value.items() if k not in mutable})
    history = new.get("recovery:" + f'{prior["recovery_sequence"]:020d}')
    require(history is not None and history["checkpoint_ref"] == checkpoint_ref(checkpoint))
    require(history["control_sha256"] == before.snapshot.control_after_sha256)
    require(history["descriptor_sha256"] == previous["ledger_commit_sha256"])
    def memberships(values):
        result = {}
        for value in values:
            for field in ("record_ref", "result_ref"):
                ref = value.get(field)
                if ref is not None:
                    require(ref["id"] not in result or result[ref["id"]] == ref)
                    result[ref["id"]] = ref
        return result
    old_refs, new_refs = memberships(old.values()), memberships(new.values())
    require(record_refs == [new_refs[key] for key in sorted(set(new_refs) - set(old_refs))])
    descriptor = {key:current[key] for key in ("authority_instance", "authority_epoch",
        "incarnation", "recovery_sequence", "previous_checkpoint", "time_high_water_ms")}
    descriptor.update(transition_kind=transition, record_refs=record_refs,
        control_after_sha256=after.snapshot.control_after_sha256)
    ledger = r.domain_digest(r.PREFIX + "ledger-commit.v1", descriptor)
    body = {key:value for key,value in descriptor.items() if key != "control_after_sha256"}
    body.update(schema_version=r.PREFIX + "recovery-checkpoint.v1", ledger_commit_sha256=ledger)
    raw = r.canonical_bytes(body)
    checkpoint_ref(raw)
    return Preparation(group, checkpoint, raw, r.canonical_bytes(descriptor), after.snapshot)


def prepare_transition(before, after, checkpoint, *, group, transition, record_refs):
    """No I/O, retries, authority or effect; only one exact reviewed candidate."""
    try:
        return _prepare(before, after, checkpoint, group, transition, record_refs)
    except (ValueError, TypeError, KeyError, StopIteration, UnicodeError):
        raise ControlError("G3_CONTROL_QUARANTINE") from None

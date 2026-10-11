"""Closed N01 cross-family consistency checks; never authentication or authority.

These checks reject incomplete/corrupt proposed state before durable preparation.
Actual qualified writers, current source observations and protected deployment
membership are separate mandatory runtime gates. There is no public positive
admission, issuer, effect, model, workflow or provider interface here.
"""
from __future__ import annotations

from dataclasses import dataclass
from ash import g3_control_codec as codec
from ash import g3_record_codec as records
from ash import g3_grant_codec as legacy


class ControlError(ValueError):
    """A fixed non-secret diagnostic for corrupt or incomplete control state."""


def require(condition):
    if not condition:
        raise ControlError("G3_CONTROL_QUARANTINE")


@dataclass(frozen=True)
class CheckedControl:
    """Consistency result only. It cannot be exchanged for a grant or claim."""
    snapshot: codec.EncodedSnapshot
    rows: tuple[codec.ControlRow, ...]

    @property
    def authority(self):
        return "NONE"


def _check(snapshot, bodies, evidence, assertions, profile):
    require(profile in ("PRODUCTION", "TEST_ONLY"))
    require(type(bodies) is dict and len(bodies) <= 4096)
    require(type(evidence) is dict and len(evidence) <= 4096)
    require(type(assertions) is dict and len(assertions) <= 4096)
    rows = codec.verify_snapshot(snapshot)
    families = {name: {} for name in codec.SPECS}
    for row in rows:
        value = codec.decode(row.value)
        families[value["family"]][row.key] = value
    require(len(families["root"]) == 1)
    root = next(iter(families["root"].values()))

    def row(family, identity):
        found = families[family].get(family + ":" + identity)
        require(found is not None)
        return found

    resolved = {}
    def body(ref):
        require(type(ref) is dict and set(ref) == {"id", "body_sha256"})
        ident = ref["id"]
        raw = bodies.get(ident)
        require(type(raw) is bytes and 0 < len(raw) <= 65536 and codec.digest(raw) == ref["body_sha256"])
        if ident in resolved:
            require(resolved[ident][0] == raw)
            return resolved[ident][1]
        value = codec.decode(raw)
        if value.get("schema_version") == legacy.GRANT_SCHEMA:
            parsed = legacy.approval_grant(value)
            actual = parsed.grant_id
        elif value.get("schema_version") == legacy.REVOCATION_SCHEMA:
            actual = legacy.revocation(value).revocation_id
        else:
            actual = records.parse_metadata(raw).record_id
        require(actual == ident)
        resolved[ident] = (raw, value)
        return value

    source_refs = {}
    for value in families["source"].values():
        ref = value["evidence_ref"]
        require(ref["ref"] not in source_refs)
        raw = evidence.get(ref["ref"])
        require(type(raw) is bytes and 0 < len(raw) <= 65536)
        require(codec.digest(raw) == ref["sha256"])
        assertion = assertions.get(value["assertion_sha256"])
        require(type(assertion) is bytes and 0 < len(assertion) <= 65536 and codec.digest(assertion) == value["assertion_sha256"])
        codec.decode(assertion)
        # Hash presence is consistency only, not qualified source-writer proof.
        source_refs[ref["ref"]] = value
        registered = row("registration", value["registration_id"])
        require(registered["purpose"] == profile)
        bound = row("binding", value["binding_id"])
        require(value["principal"] == bound["principal"])
        if value["context_id"] is not None:
            require(row("context", value["context_id"])["binding_id"] == value["binding_id"])

    def proof(ref, binding_id=None, context_id=None, kind=None):
        value = source_refs.get(ref["ref"])
        require(value is not None and value["evidence_ref"] == ref)
        if binding_id is not None:
            require(value["binding_id"] == binding_id)
        if context_id is not None:
            require(value["context_id"] == context_id)
        if kind is not None:
            require(value["kind"] == kind)
        return value

    def context_value(value):
        context = row("context", value["context_id"])
        require(value == {"context_id":context["context_id"],
            "context_generation":context["context_generation"],
            "authenticated_at_ms":context["authenticated_at_ms"],
            "context_expires_at_ms":context["expires_at_ms"],
            "identity_evidence":context["identity_evidence"],
            "session_evidence":context["session_evidence"]})
        return context

    def resolve_nested(value):
        if type(value) is dict:
            if set(value) == {"id", "body_sha256"}:
                body(value)
            elif set(value) == {"ref", "sha256"}:
                proof(value)
            else:
                for child in value.values():
                    resolve_nested(child)
        elif type(value) is list:
            for child in value:
                resolve_nested(child)

    for values in families.values():
        for value in values.values():
            resolve_nested(value)
    # References inside retained immutable bodies are also complete, including
    # historical stamps, previous checkpoints and evidence memberships.
    scanned = set()
    while set(resolved) - scanned:
        for ident in tuple(set(resolved) - scanned):
            scanned.add(ident)
            resolve_nested(resolved[ident][1])

    history = sorted(families["recovery"].values(), key=lambda value: value["sequence"])
    require([value["sequence"] for value in history] == list(range(root["recovery_sequence"])))
    previous = None
    for item in history:
        checkpoint = body(item["checkpoint_ref"])
        require(checkpoint["authority_instance"] == root["authority_instance"])
        require(checkpoint["recovery_sequence"] == item["sequence"])
        require(checkpoint["previous_checkpoint"] == previous)
        require(checkpoint["ledger_commit_sha256"] == item["descriptor_sha256"])
        previous = item["checkpoint_ref"]
    require(root["previous_checkpoint"] == previous)
    for _, value in resolved.values():
        if "stamp" in value:
            stamp = value["stamp"]
            anchor = body(stamp["base_checkpoint"])
            require(stamp["authority_instance"] == anchor["authority_instance"] == root["authority_instance"])
            require(stamp["base_recovery_sequence"] == anchor["recovery_sequence"] < root["recovery_sequence"])
            require((stamp["authority_epoch"], stamp["incarnation"]) ==
                    (anchor["authority_epoch"], anchor["incarnation"]))

    active_bindings = set()
    for bound in families["binding"].values():
        if bound["state"] == "CURRENT":
            key = (bound["workspace_id"], bound["project_id"])
            require(key not in active_bindings)
            active_bindings.add(key)
    for context in families["context"].values():
        bound = row("binding", context["binding_id"])
        require((context["owner_generation"], context["binding_generation"]) ==
                (bound["owner_generation"], bound["binding_generation"]))
        for field in ("identity_evidence", "session_evidence"):
            proof(context[field], bound["binding_id"], context["context_id"], "D01")
        if context["state"] == "CURRENT":
            require(bound["state"] == "CURRENT")
            require((context["authority_epoch"], context["incarnation"]) ==
                    (root["authority_epoch"], root["incarnation"]))
    for bound in families["binding"].values():
        require(sum(c["state"] == "CURRENT" and c["binding_id"] == bound["binding_id"]
                    for c in families["context"].values()) <= 8)

    context_challenges = set()
    for challenge in families["challenge"].values():
        context = row("context", challenge["context_id"])
        bound = row("binding", context["binding_id"])
        value = body(challenge["record_ref"])
        expected_binding = dict(owner=bound["principal"], owner_generation=bound["owner_generation"],
            workspace_id=bound["workspace_id"], project_id=bound["project_id"],
            binding_id=bound["binding_id"], binding_generation=bound["binding_generation"])
        require(value["binding"] == expected_binding)
        require((value["material"]["scope"]["workspace_id"], value["material"]["scope"]["project_id"])
                == (bound["workspace_id"], bound["project_id"]))
        require(value["nonce"] == challenge["nonce"] and value["expires_at_ms"] == challenge["expires_at_ms"])
        require(challenge["expires_at_ms"] <= context["expires_at_ms"])
        require(challenge["context_id"] not in context_challenges)
        context_challenges.add(challenge["context_id"])
        nonce = row("nonce", challenge["nonce"])
        require(nonce["challenge_id"] == challenge["challenge_id"])
        if challenge["state"] == "PENDING":
            require(context["state"] == "CURRENT" and nonce["state"] == "PENDING")
        elif challenge["state"] in ("CONFIRM", "DENY"):
            decision = row("decision", challenge["challenge_id"])
            require(decision["choice"] == challenge["state"])
            require(context["state"] == "CONSUMED" and nonce["state"] == "CONSUMED")
        else:
            require(nonce["state"] in ("RETIRED", "CONSUMED"))
        view = row("view", challenge["view_id"])
        require(view["challenge_id"] == challenge["challenge_id"] and view["context_id"] == challenge["context_id"])

    for view in families["view"].values():
        challenge = row("challenge", view["challenge_id"])
        value = body(view["record_ref"])
        require(value["challenge"] == challenge["record_ref"])
        require(value["view_key"] == view["view_id"] and value["template_revision"] == view["template_revision"])
        require(value["presentation_sha256"] == view["presentation_sha256"])
        require(view["context_id"] == challenge["context_id"])
        require(context_value(value["owner_context"])["context_id"] == view["context_id"])
        material = body(challenge["record_ref"])
        projection = dict(challenge_body=material, owner_context=value["owner_context"],
            template_revision=value["template_revision"], expires_at_ms=value["expires_at_ms"])
        require(records.domain_digest(records.PREFIX + "presentation-material.v1", projection)
                == value["presentation_sha256"])
        if view["state"] == "CURRENT":
            require(challenge["view_id"] == view["view_id"] and challenge["state"] != "RETIRED")
    for decision in families["decision"].values():
        challenge = row("challenge", decision["challenge_id"])
        view = row("view", decision["view_id"])
        value = body(decision["record_ref"])
        require(value["challenge"] == challenge["record_ref"] and value["view"] == view["record_ref"])
        require(value["decision"] == decision["choice"] == challenge["state"])
        challenge_body = body(challenge["record_ref"])
        view_body = body(view["record_ref"])
        require(value["binding"] == challenge_body["binding"])
        require(value["proposal_id"] == challenge_body["proposal_id"])
        require(value["nonce"] == challenge_body["nonce"])
        require(value["presentation_sha256"] == view_body["presentation_sha256"])
        require(value["owner_context"] == view_body["owner_context"])
        require(decision["context_id"] == challenge["context_id"] and decision["nonce"] == challenge["nonce"])
        nonce = row("nonce", decision["nonce"])
        require(nonce["decision_ref"] == decision["record_ref"])
        receipt = row("receipt", decision["challenge_id"])
        require(receipt["decision_ref"] == decision["record_ref"])
    for receipt in families["receipt"].values():
        decision = row("decision", receipt["challenge_id"])
        value = body(receipt["record_ref"])
        require(value["owner_decision"] == decision["record_ref"])
        require(value["confirmation_expires_at_ms"] == receipt["expires_at_ms"])
        decision_body = body(decision["record_ref"])
        for field in ("challenge", "view", "binding", "owner_context", "proposal_id",
                      "nonce", "presentation_sha256", "decision"):
            require(value[field] == decision_body[field])
        require(value["accepted_at_ms"] >= decision_body["observed_at_ms"])
    for nonce in families["nonce"].values():
        require(row("challenge", nonce["challenge_id"])["nonce"] == nonce["nonce"])

    global_index = row("revocation", "authority")
    require(global_index["state"] == "INDEX" and global_index["revocation_refs"] == [])
    require(global_index["generation"] == root["revocation_generation"] and global_index["completeness"] == "COMPLETE")
    require({v["grant_id"] for v in families["revocation"].values() if v["grant_id"] is not None}
            == {v["grant_id"] for v in families["grant"].values()})
    for grant in families["grant"].values():
        require(grant["grant_id"] == grant["record_ref"]["id"])
        value = body(grant["record_ref"])
        require(value["expires_at"] is not None and grant["use_until_ms"] <= value["expires_at"])
        receipt = body(grant["receipt_ref"])
        require(receipt["decision"] == "CONFIRM" and grant["use_until_ms"] <= receipt["confirmation_expires_at_ms"])
        material = body(receipt["challenge"])["material"]
        require(value["subject_id"] == material["subject_id"] and value["scope"] == material["scope"])
        require(value["capability_id"] == material["subject"]["capability_id"])
        require(value["expires_at"] <= receipt["confirmation_expires_at_ms"])
        require(value["expires_at"] <= value["effective_at"] + 600000)
        require(value["effective_at"] >= receipt["accepted_at_ms"])
        registered = row("registration", grant["issuer_registration"])
        require(registered["purpose"] == profile and registered["issuer_ref"] == value["issuer_ref"])
        index = row("revocation", grant["grant_id"])
        require(index["generation"] <= global_index["generation"] and index["completeness"] == "COMPLETE")
        for ref in index["revocation_refs"]:
            require(body(ref)["grant_id"] == grant["grant_id"])
        require((index["state"] == "REVOKED") == bool(index["revocation_refs"]))
        if grant["state"] == "CURRENT":
            require(index["state"] == "CLEAR" and registered["state"] == "CURRENT")

    claimed_intents = set()
    for claim in families["claim"].values():
        intent = row("intent", claim["intent_id"])
        require(claim["intent_id"] not in claimed_intents)
        claimed_intents.add(claim["intent_id"])
        require(intent["state"] == "CONSUMED")
        value = body(claim["record_ref"])
        require(value["phase"] == "CLAIM" and value["intent"] == intent["record_ref"])
        require(value["attempt_key"] == claim["attempt_key"] and value["handoff_until_ms"] == claim["handoff_deadline_ms"])
        require(value["dispatch_material_sha256"] == body(intent["record_ref"])["dispatch_material_sha256"])
        grant = row("grant", intent["grant_id"])
        require(grant["state"] in ("CONSUMED", "RETIRED") and value["grant"] == grant["record_ref"])
        if claim["result_ref"] is not None:
            result = body(claim["result_ref"])
            require(result["phase"] == "RESULT" and result["claim"] == claim["record_ref"])
            require(result["attempt_key"] == claim["attempt_key"])
            for field in ("intent", "grant", "dispatch_material_sha256"):
                require(result[field] == value[field])
            require(result["observed_at_ms"] >= value["claimed_at_ms"])
            expected = {"COMPLETED":"SUCCEEDED", "FAILED":"FAILED", "UNKNOWN":"UNKNOWN"}
            require(claim["outcome"] == expected[result["outcome"]])
    for intent in families["intent"].values():
        value = body(intent["record_ref"])
        require(value["intent_key"] == intent["intent_id"])
        challenge = body(value["challenge"])
        material = challenge["material"]
        require((intent["target_sha256"], intent["payload_sha256"]) ==
                (material["targets"]["content_sha256"], material["dispatch_payload"]["content_sha256"]))
        for field in ("subject_id", "scope_sha256", "dispatch_material_sha256"):
            require(value[field] == material[field])
        require(intent["task_id"] == material["scope"]["task_id"])
        require(value["binding"] == challenge["binding"])
        require(context_value(value["owner_context"])["context_id"] == intent["context_id"])
        receipt = body(value["receipt"])
        for field in ("challenge", "binding", "owner_context", "proposal_id"):
            require(value[field] == receipt[field])
        if value["grant"] is not None:
            require(value["grant"] == row("grant", intent["grant_id"])["record_ref"])
            require(value["revocation_read"]["index_generation"] <= global_index["generation"])
        require(intent["use_until_ms"] == value["use_until_ms"])
        if intent["state"] == "ADMIT_PENDING":
            require(value["disposition"] == "ADMIT_PENDING")
            require(row("grant", intent["grant_id"])["state"] == "CURRENT")
            require(row("registration", intent["registration_id"])["purpose"] == profile)
    gate_sources = {"D01_IDENTITY_CONTEXT":"D01", "D03_RECOVERY_FRESHNESS":"D03",
        "D04_EXECUTOR_EXCLUSION":"D04", "TECHNICAL":"TECHNICAL", "TASK":"TASK",
        "HOST":"HOST", "G1":"G1", "G2":"G2"}
    for _, value in resolved.values():
        if "gate_facts" not in value:
            continue
        intent_value = value if "binding" in value else body(value["intent"])
        binding_id = intent_value["binding"]["binding_id"]
        context_id = intent_value["owner_context"]["context_id"]
        for fact in value["gate_facts"]:
            source = proof(fact["source_evidence"], binding_id, context_id, gate_sources[fact["kind"]])
            require(source["conclusion"] == fact["verdict"])
            require(source["observed_at_ms"] <= fact["observed_at_ms"])
            require(fact["valid_until_ms"] <= source["expires_at_ms"])
    for retirement in families["retirement"].values():
        require(retirement["retired_sequence"] <= root["recovery_sequence"])
        retired = row(retirement["entity_kind"], retirement["entity_id"])
        require(retired.get("state") not in ("CURRENT", "PENDING", "ADMIT_PENDING"))
    return CheckedControl(snapshot, rows)


def check_control(snapshot, bodies, evidence, *, profile, assertions=None):
    """Validate complete consistency; NONE even if every supplied byte matches."""
    try:
        return _check(snapshot, bodies, evidence, {} if assertions is None else assertions, profile)
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError, OverflowError, UnicodeError):
        raise ControlError("G3_CONTROL_QUARANTINE") from None

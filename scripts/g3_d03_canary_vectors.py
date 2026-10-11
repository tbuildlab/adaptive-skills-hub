"""Synthetic D03 consumer vectors. TEST_ONLY / NO_AUTHORITY, not N01 runtime.

Reuse unchanged R07 and the existing closed control snapshot codec. No grant,
bearer, login context, positive admission or provider execution is created.
Production consumers must never import this diagnostic module.
"""
from scripts.g3_production_metadata import canonical_bytes, domain_digest
from scripts.g3_offline_control import ControlRow, encode_snapshot, verify_snapshot, EncodedSnapshot
from scripts.g3_d03_s3_fence import SCHEMA, LEDGER, reference, sha, decoded, require

INSTANCE = "d03-test-only-custody-v1"
NORMAL = "qualification/v1/normal/canary-v1/"
FAULTS = "qualification/v1/faults/"
BASE_TIME = 1791698400000


def checkpoint(seq, previous, kind, epoch=1, incarnation="canary-incarnation-1", terminal=False):
    root = dict(schema_version="nexus.g3.n01-control.v1", family="root", revision=seq+1,
        authority_instance=INSTANCE, authority_epoch=epoch, incarnation=incarnation,
        recovery_sequence=seq, previous_checkpoint=previous, time_high_water_ms=BASE_TIME+seq,
        quarantine="OPEN", revocation_generation=1)
    rows = [ControlRow.from_value(root)]
    if terminal:
        rows.append(ControlRow.from_value(dict(schema_version="nexus.g3.n01-control.v1",
            family="retirement", revision=1, entity_kind="claim", entity_id="canary-consumed-unknown",
            retired_sequence=2, reason="INVALIDATED")))
    if kind == "RECOVER":
        rows.append(ControlRow.from_value(dict(schema_version="nexus.g3.n01-control.v1",
            family="retirement", revision=1, entity_kind="context", entity_id="canary-incarnation-1",
            retired_sequence=seq, reason="RESTART")))
    snapshot = encode_snapshot(tuple(rows))
    verify_snapshot(snapshot)
    descriptor = dict(authority_instance=INSTANCE, authority_epoch=epoch, incarnation=incarnation,
        recovery_sequence=seq, previous_checkpoint=previous, transition_kind=kind,
        record_refs=[], control_after_sha256=sha(snapshot.root), time_high_water_ms=BASE_TIME+seq)
    digest = domain_digest(LEDGER, descriptor)
    body = dict(descriptor)
    del body["control_after_sha256"]
    body.update(schema_version=SCHEMA, ledger_commit_sha256=digest)
    objects = {sha(snapshot.root): snapshot.root, digest: canonical_bytes(descriptor)}
    objects.update({sha(raw): raw for raw in snapshot.pages})
    raw = canonical_bytes(body)
    reference(raw)
    return raw, objects


def vectors():
    result, prior = [], None
    for seq, kind in enumerate(("GENESIS", "DENY", "RESULT", "INVALIDATE", "RECOVER")):
        raw, objects = checkpoint(seq, prior, kind, 2 if seq == 4 else 1,
            "canary-incarnation-2" if seq == 4 else "canary-incarnation-1", seq >= 2)
        result.append((raw, objects)); prior = reference(raw)
    return tuple(result)


def registration_body():
    v = vectors()
    return dict(schema_version="nexus.g3.d03.diagnostic-registration.v1", purpose="TEST_ONLY",
        generation=1, authority_instance=INSTANCE, normal_prefix=NORMAL,
        genesis=reference(v[0][0]), admin_checkpoint_ids=[reference(v[x][0])["id"] for x in (0,4)],
        no_automatic_redispatch="REQUIRED", real_admission="NO")


def verify_consumer(history, *, generation=1, incarnation=None, restored_head=None):
    """Only synthetic canary predicates. Never returns execution permission."""
    require(type(generation) is int and generation == 1)
    for control, pages in zip(history.controls, history.pages):
        verify_snapshot(EncodedSnapshot(control, pages))
    head = decoded(history.checkpoints[-1])
    require(incarnation is None or incarnation == head["incarnation"])
    require(restored_head is None or restored_head == history.head)
    return dict(authority="NONE", production_eligibility="DENY",
        epoch=head["authority_epoch"], incarnation=head["incarnation"], sequence=head["recovery_sequence"],
        automatic_redispatch="DENY")

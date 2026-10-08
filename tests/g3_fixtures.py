"""Explicit TEST FIXTURE issuer, never imported by runtime or used as Owner.

This helper trusts only its synthetic marker and exact canonical record IDs.
It models a reviewed issuer snapshot; it does not authenticate any real person.
"""
from ash import g3_authorization as g3
from tests.g1_fixtures import NOW

EVIDENCE = {"ref": "test-fixture-decision", "sha256": "e" * 64}


def subject_body(kind="local_adapter"):
    common = {"schema_version": g3.SUBJECT_SCHEMA, "capability_id": "fixture/capability",
              "kind": kind, "provider": "synthetic", "action": "read"}
    if kind == "mcp_tool":
        return {**common, "server_ref": "fixture-server", "tool_name": "Read",
                "revision": "r1", "contract_sha256": "a" * 64,
                "config_sha256": "b" * 64, "account_context": "fixture-account"}
    if kind == "local_component":
        from ash.ecosystem_models import (
            build_component_identity, build_component_revision_identity,
            build_revision_identity, source_identity, typed_id,
        )
        source = source_identity("github", "synthetic-fixture/component")
        revision = build_revision_identity(source_id=source, commit_object_format="git_sha1",
                                          commit_oid="a" * 40, input_sha256="a" * 64,
                                          tree_id=typed_id("tree", {"entries": []}))
        component = build_component_identity(source_id=source, component_root="skill")
        component_revision = build_component_revision_identity(
            revision_id=revision, component_id=component, component_manifest_sha256="c" * 64)
        return {**common, "provider": "github", "source_id": source,
                "component_revision_id": component_revision,
                "config_sha256": "b" * 64}
    return {**common, "source_ref": "fixture-source", "revision": "r1",
            "content_sha256": "a" * 64, "config_sha256": "b" * 64}


def scope(**changes):
    return {"workspace_id": "fixture-workspace", "project_id": "fixture-project",
            "task_classes": ["governance"], "operations": ["read"], **changes}


def grant_body(requested_subject=None, **changes):
    s = requested_subject or g3.subject(subject_body())
    return {"schema_version": g3.GRANT_SCHEMA, "capability_id": s.to_dict()["capability_id"],
            "subject_id": s.subject_id, "subject_sha256": s.subject_id.rsplit(":", 1)[1],
            "scope": scope(), "effective_at": 1000, "expires_at": 3000,
            "issuer_ref": "test-fixture", "decision_evidence": dict(EVIDENCE), **changes}


def revoke_body(grant, **changes):
    return {"schema_version": g3.REVOCATION_SCHEMA, "grant_id": grant.grant_id,
            "effective_at": 1500, "issuer_ref": "test-fixture",
            "decision_evidence": dict(EVIDENCE), "reason": "test-revoked", **changes}


def evaluate_fixture(s, grants, revocations=(), requested_scope=None, **changes):
    # Exact IDs bind each reviewed fixture body; marker equality alone never
    # becomes production provenance because the public evaluator has no seam.
    def trusted(rows, field):
        return frozenset(getattr(row, field) for row in rows
                         if row.to_dict()["issuer_ref"] == "test-fixture"
                         and row.to_dict()["decision_evidence"] == EVIDENCE)

    arguments = {"now": NOW, "technical_available": True, "task_authorized": True,
                 "host_authorized": True, "g1_passed": True, "g2_passed": True, **changes}
    return g3._evaluate(s, grants, revocations, requested_scope or scope(),
                        fixture_grant_ids=trusted(grants, "grant_id"),
                        fixture_revocation_ids=trusted(revocations, "revocation_id"), **arguments)

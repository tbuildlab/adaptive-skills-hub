"""NON_AUTHORITATIVE G4 structural examples; never production qualification."""
from ash import g4_contracts as c
from ash import g4_host_adapter as a

NOW = 1000
SOURCE = "a" * 64
ORIGINAL = "b" * 64
AUTHORITY = "c" * 64
OBLIGATION = "d" * 64
ARTIFACT = "e" * 64
ENDPOINT = "f" * 64


def binding(**changes):
    return {"workspace_id": "fixture", "project_id": "fixture-project", "task_id": "fixture-task",
            "action_id": "fixture-action", "execution_id": "fixture-execution", "generation": 1,
            "incarnation": "fixture-incarnation", "input_sha256": "0" * 64, **changes}


def request(**changes):
    return {"schema_version": a.REQUEST_SCHEMA, "binding": binding(), "operations": ["read"],
            "expires_at": NOW + 100, "requires_recovery": False, **changes}


def result(status="COMPLETED", **changes):
    kind = {"COMPLETED": "artifact", "FAILED": "failure", "CANCELLED": "cancellation", "UNKNOWN": "unknown"}[status]
    outcome = {"COMPLETED": "PASS", "FAILED": "FAIL", "CANCELLED": "REQUESTED", "UNKNOWN": "UNKNOWN"}[status]
    return {"schema_version": a.RESULT_SCHEMA, "basis": a.BASIS, "binding": binding(), "status": status,
            "observed_at": NOW + 1, "evidence": [{"type": kind, "source": "STRUCTURAL_FIXTURE",
            "sha256": ARTIFACT, "ref": SOURCE, "observed_at": NOW + 1, "result": outcome}], **changes}


def domain_body(kind, pack="website", **changes):
    fields = {
        "project-decision": {"decision_key": "fixture-decision", "content_sha256": SOURCE, "source_refs": [SOURCE], "approving_authority_ref": AUTHORITY,
                             "valid_until": NOW + 100, "state": "CONFIRMED", "supersedes": None,
                             "retention": "TASK", "obligations": [OBLIGATION]},
        "context-manifest": {"sources": [{"ref": SOURCE, "sha256": SOURCE, "project_id": "fixture-project",
                             "task_id": "fixture-task", "transformation": "ORIGINAL", "original_ref": None,
                             "valid_until": NOW + 100}], "recipients": ["local-host"], "omissions": [],
                             "disclosure_limits": ["local-host"], "preserved_obligations": [OBLIGATION]},
        "capability-relation": {"relation": "uses", "from_endpoint": {"ref": SOURCE, "version": "v1"},
                                "to_endpoint": {"ref": ENDPOINT, "version": "v1"}, "provenance_refs": [SOURCE]},
        "change-impact": {"repository_id": "fixture-repo", "base_commit": "1" * 40, "changed_surfaces": ["page"],
                          "dependencies": ["shared-control"], "consumers": ["page", "shared-control"],
                          "shared_contracts": ["interaction"], "validation_obligations": ["shared-control"], "unexamined": []},
        "workflow-pack": {"pack": pack, "version": "v1", "applicability": ["fixture"], "required_capabilities": ["host"],
                          "allowed_operations": ["read"], "required_evidence": sorted(c.PACK_EVIDENCE[pack])},
    }
    return {"schema_version": "nexus.g4." + kind + ".v1", "binding": binding(), **fields[kind], **changes}


def bundle(pack="website"):
    observations = {key: {"status": "PASS", "input_sha256": "0" * 64, "artifact_sha256": ARTIFACT,
                          "source_refs": [SOURCE]} for key in c.PACK_EVIDENCE[pack] | {"shared-control"}}
    return {"pack": c.record("workflow-pack", domain_body("workflow-pack", pack)),
            "context": c.record("context-manifest", domain_body("context-manifest")),
            "impact": c.record("change-impact", domain_body("change-impact")),
            "decisions": (c.record("project-decision", domain_body("project-decision")),),
            "relations": (c.record("capability-relation", domain_body("capability-relation")),),
            "expected_binding": binding(), "now": NOW, "permitted_operations": ["read"],
            "permitted_recipients": ["local-host"], "source_refs": [SOURCE, ORIGINAL],
            "confirmation_refs": [AUTHORITY], "endpoint_versions": {SOURCE: "v1", ENDPOINT: "v1"},
            "source_digests": {SOURCE: SOURCE, ORIGINAL: ORIGINAL}, "task_class": "fixture",
            "expected_repository_id": "fixture-repo", "expected_base_commit": "1" * 40,
            "required_obligations": [OBLIGATION], "required_consumers": ["shared-control"],
            "required_validations": ["shared-control"], "available_capabilities": ["host"], "observations": observations}

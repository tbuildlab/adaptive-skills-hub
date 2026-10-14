#!/usr/bin/env python3
"""Read back one local G4 evidence packet. No dispatch or approval capability."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ash import core_capabilities as files, g4_contracts as contracts

SCHEMA = "nexus.g4.local-workflow-evidence.v1"


def verify(root: Path, packet_name: str) -> dict:
    """Same-user Host evidence integrity, not authentic production qualification.

    Runtime measurements are obtained by the Host, never executed from a packet.
    Original checks and omitted observations must remain available for readback.
    """
    root = root.resolve(strict=True)
    packet = contracts.parse(files.read_bytes(root, packet_name))
    contracts.require(set(packet) == {"schema", "records", "oracle", "files", "checks",
                                      "artifact_paths", "input_paths", "scope", "memory_path"})
    contracts.require(packet["schema"] == SCHEMA)
    table = packet["files"]
    contracts.require(type(table) is dict and 1 <= len(table) <= 32)
    actual = {}
    for name, expected in table.items():
        contracts.require(type(expected) is dict and set(expected) == {"sha256", "bytes"})
        data = files.read_bytes(root, name)
        actual[name] = {"sha256": files.sha(data), "bytes": len(data)}
        contracts.require(actual[name] == expected, "G4_LOCAL_BYTES_CHANGED")
    inputs, artifacts = packet["input_paths"], packet["artifact_paths"]
    for names in (inputs, artifacts):
        contracts.require(type(names) is list and names and len(names) == len(set(names))
                          and set(names) <= set(actual))
    contracts.require(not set(inputs) & set(artifacts))
    # Bind the entire declared source and artifact sets, not a chosen single file.
    input_digest = contracts.digest({name: actual[name] for name in sorted(inputs)})
    artifact_digest = contracts.digest({name: actual[name] for name in sorted(artifacts)})
    scope = packet["scope"]
    contracts.require(type(scope) is dict and set(scope) == {"included", "excluded_unexamined"})
    contracts.require(type(scope["included"]) is list and scope["included"])
    contracts.require(type(scope["excluded_unexamined"]) is list)
    for area in scope["excluded_unexamined"]:
        contracts.require(type(area) is dict and set(area) == {"area", "reason"}
                          and area["area"] and area["reason"]
                          and area["area"] not in scope["included"])
    records = packet["records"]
    contracts.require(set(records) == {"pack", "context", "impact", "decisions", "relations"})
    args = dict(packet["oracle"])
    for key, kind in (("pack", "workflow-pack"), ("context", "context-manifest"),
                      ("impact", "change-impact")):
        args[key] = contracts.record(kind, records[key])
    for key, kind in (("decisions", "project-decision"), ("relations", "capability-relation")):
        args[key] = tuple(contracts.record(kind, body) for body in records[key])
    contracts.require(args["expected_binding"]["input_sha256"] == input_digest,
                      "G4_LOCAL_INPUT_SUBSTITUTION")
    # No caller-supplied PASS dictionary without accessible original measurement.
    observations = args["observations"]
    checks = packet["checks"]
    contracts.require(type(checks) is dict and set(checks) == set(observations),
                      "G4_LOCAL_REDUCTION_LOSS")
    contracts.require(set(actual) == set(inputs) | set(artifacts) | set(checks.values()),
                      "G4_LOCAL_UNREPRESENTED_SOURCE")
    memory_path = packet["memory_path"]
    contracts.require(memory_path in inputs)
    memory = contracts.parse(files.read_bytes(root, memory_path))
    contracts.require(set(memory) == {"schema", "project_id", "task_id", "rule", "source_ref",
                                      "retention", "state", "dispatch_authority"})
    contracts.require(memory["schema"] == "nexus.g4.local-task-memory-entry.v1"
                      and memory["project_id"] == args["expected_binding"]["project_id"]
                      and memory["task_id"] == args["expected_binding"]["task_id"]
                      and memory["dispatch_authority"] == "none"
                      and memory["retention"] == "TASK"
                      and memory["state"] == "CONFIRMED_TASK_CONSTRAINT_ONLY",
                      "G4_LOCAL_MEMORY_SCOPE")
    contracts.require(len(records["decisions"]) == 1
                      and records["decisions"][0]["content_sha256"] == actual[memory_path]["sha256"]
                      and memory["source_ref"] in records["decisions"][0]["source_refs"],
                      "G4_LOCAL_MEMORY_SUBSTITUTION")
    represented = set()
    for key, name in checks.items():
        contracts.require(name in actual)
        detail = contracts.parse(files.read_bytes(root, name))
        contracts.require(set(detail) == {"schema", "pack", "checks"}
                          and detail["schema"] == "nexus.g4.host-measurements.v1"
                          and detail["pack"] == records["pack"]["pack"])
        detail_checks = detail["checks"]
        contracts.require(type(detail_checks) is dict and key in detail_checks)
        # Every retained FAIL/UNKNOWN stops acceptance, including optional checks.
        for item in detail_checks.values():
            contracts.require(type(item) is dict and set(item) == {"status", "measurements"}
                              and item["status"] == "PASS" and item["measurements"],
                              "G4_LOCAL_MEASUREMENT_NOT_PASS")
        represented.update((name, item) for item in detail_checks)
        observation = observations[key]
        contracts.require(observation["artifact_sha256"] == artifact_digest,
                          "G4_LOCAL_ARTIFACT_SUBSTITUTION")
        contracts.require(files.sha(files.read_bytes(root, name)) in observation["source_refs"],
                          "G4_LOCAL_CHECK_SOURCE_MISSING")
    declared = {(name, key) for key, name in checks.items()}
    contracts.require(represented == declared, "G4_LOCAL_REDUCTION_LOSS")
    context_sources = records["context"]["sources"]
    for source in context_sources:
        contracts.require(source["ref"] in {entry["sha256"] for entry in actual.values()},
                          "G4_LOCAL_SOURCE_MISSING")
        contracts.require(source["ref"] == source["sha256"], "G4_LOCAL_SOURCE_MISSING")
    # Structural validation stays structural. This tool never calls the deny gate
    # as a permission oracle and never substitutes its result for execution authority.
    verdict = contracts.validate_domain_bundle(**args)
    return {"schema": "nexus.g4.local-verification.v1",
            "status": "LOCAL_ARTIFACT_AND_EVIDENCE_VERIFIED",
            "contract_verdict": verdict, "pack": records["pack"]["pack"],
            "artifact_sha256": artifact_digest, "input_sha256": input_digest,
            "files_reopened": len(actual), "checks_preserved": sorted(checks),
            "excluded_unexamined": scope["excluded_unexamined"],
            "dispatch_authority": "none", "real_admission": "NO",
            "qualification_scope": "TRUSTED_LOCAL_HOST_ONLY_NOT_PRODUCTION_ADMISSION"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path)
    parser.add_argument("packet")
    args = parser.parse_args()
    try:
        result = verify(args.root, args.packet)
    except (ValueError, OSError, KeyError, TypeError):
        print(json.dumps({"status": "DENY_OR_HOLD", "dispatch_authority": "none",
                          "real_admission": "NO"}))
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

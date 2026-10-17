"""Advisory memory lookup, separate from V2 rules, research and qualification."""
from __future__ import annotations

import json
from pathlib import Path

from . import project_memory as model
from .common import tokenize
from .mcp.schemas import NexusMcpError, MAX_SAFE_ENVELOPE_BYTES
from .project_memory_store import load_config


def unavailable(status):
    return {"schema_version": "nexus.project-memory.context.v1", "status": status,
            "authority": "none", "scope": "project_local", "content_trust": "untrusted_historical_data"}


class ProjectMemoryReader:
    def __init__(self, workspace_config: Path):
        self.workspace_config = workspace_config

    def __call__(self, workspace, task, project_id=None):
        try:
            store = load_config(self.workspace_config)
            bundle = store.lookup(workspace, project_id)
            revision = bundle["revisions"][-1]
            tokens = tokenize(task)
            lessons = []
            latest_lessons = {}
            for source in bundle["revisions"]:
                for lesson in source["lessons"]:
                    latest_lessons[lesson["id"]] = (source, lesson)
            eligible = 0
            for source, lesson in latest_lessons.values():
                overlap = sorted(tokens & tokenize(" ".join(lesson["tags"]) + " " + lesson["summary"]))
                if overlap:
                    eligible += 1
                    projection = {key: lesson[key] for key in ("id", "kind", "summary", "confidence", "root_cause_status",
                                                              "root_cause", "correction", "validation_result", "prevention", "evidence_refs")}
                    projection["match_reasons"] = ["task_overlap:" + word for word in overlap[:4]]
                    projection["source_revision"] = source["number"]
                    projection["source_revision_digest"] = source["revision_digest"]
                    if len(model.encoded(projection)) <= 768:
                        lessons.append((len(overlap), lesson["confidence"] == "verified", lesson["id"], projection))
            lessons.sort(key=lambda item: (-item[0], -item[1], item[2]))
            result = unavailable("project_memory_loaded")
            result.update(project_id=bundle["project_id"], revision=revision["number"],
                          revision_digest=bundle["current_digest"], current_state=model.core_context(revision),
                          artifacts=revision["artifacts"],
                          capabilities_used=revision["capabilities_used"], references_used=revision["references_used"],
                          environment=revision["environment"], evidence=revision["evidence"], lessons=[item[3] for item in lessons[:4]],
                          omitted_sections=[], omitted_lesson_count=eligible - min(len(lessons), 4))
            # Mandatory current state is never silently truncated.
            for key in ("lessons", "environment", "capabilities_used", "references_used", "evidence", "artifacts"):
                if len(model.encoded(result)) <= model.MAX_CONTEXT_BYTES:
                    break
                result.pop(key)
                result["omitted_sections"].append(key)
            model.require(len(model.encoded(result)) <= model.MAX_CONTEXT_BYTES, "project_memory_context_overflow")
            model.validate(result, "context")
            return result
        except model.MemoryError as exc:
            return unavailable(str(exc))
        except (OSError, ValueError, TypeError, RecursionError, NexusMcpError):
            return unavailable("project_memory_unavailable")


def attach_context(payload, memory):
    """Keep the old plan and wire ceiling; omit memory visibly if no safe space."""
    try:
        model.validate(memory, "context")
        model.screen(memory)
        model.require(len(model.encoded(memory)) <= model.MAX_CONTEXT_BYTES)
        if memory["status"] == "project_memory_loaded":
            model.require(all(k in memory for k in ("project_id", "revision", "revision_digest", "current_state")))
            model.require(memory["current_state"]["project_id"] == memory["project_id"])
        else:
            memory = unavailable(memory["status"])
    except (model.MemoryError, TypeError, ValueError):
        memory = unavailable("project_memory_invalid")
    result = dict(payload)
    result["project_memory"] = memory
    def size():
        return len(json.dumps(result, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))
    if size() > MAX_SAFE_ENVELOPE_BYTES:
        result["project_memory"] = unavailable("project_memory_context_overflow")
    if size() > MAX_SAFE_ENVELOPE_BYTES:
        # Preserve the original valid plan when even the status block cannot fit.
        result = dict(payload)
        warnings = result.get("warnings", [])
        result["warnings"] = [*warnings, "project_memory_context_overflow"]
        if len(model.encoded(result)) > MAX_SAFE_ENVELOPE_BYTES:
            # Replace an existing optional warning instead of invalidating planning.
            result["warnings"] = ["project_memory_context_overflow"]
        if len(model.encoded(result)) > MAX_SAFE_ENVELOPE_BYTES:
            # Only generic display summaries may be shortened. Capabilities,
            # validations, fallback, rules and research data remain unchanged.
            for group in ("execution_steps", "validation_plan"):
                result[group] = [dict(item) for item in result.get(group, [])]
                for item in result[group]:
                    if "summary" in item:
                        item["summary"] = ""
                    if len(model.encoded(result)) <= MAX_SAFE_ENVELOPE_BYTES:
                        return result
            # Real safe_plan always includes this fixed display subtitle. Its
            # removal funds a visible warning without changing any plan decision.
            result = dict(payload)
            result["warnings"] = ["project_memory_context_overflow"]
            result["product"] = dict(payload.get("product", {}))
            result["product"].pop("subtitle", None)
            if len(model.encoded(result)) <= MAX_SAFE_ENVELOPE_BYTES:
                return result
            # Only nonstandard synthetic envelopes can lack every display reserve.
            # Return a small explicit context warning, not an execution success.
            return {"status": "fallback_needed", "project_memory": unavailable("project_memory_context_overflow"),
                    "warnings": ["nonstandard_plan_envelope"]}
    return result

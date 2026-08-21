#!/usr/bin/env python3
"""Build a compact combined registry from registered sources and local indexes."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
src = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))

registry = {
    "schema_version": 2,
    "generated_from": ["sources.json", "state/installed-skills.json", "state/installed-agents.json"],
    "capabilities": [],
    "installed_skills": [],
    "installed_agents": [],
    "duplicate_resolutions": [],
}

for item in src["sources"]:
    registry["capabilities"].append({
        "id": item["id"],
        "kind": item["kind"],
        "repo": item["repo"],
        "default_branch": item["default_branch"],
        "categories": item["categories"],
        "use_for": item["use_for"],
        "avoid_for": item["avoid_for"],
    })

registry["capabilities"].sort(key=lambda x: (x["kind"], x["id"]))
for filename, target in (("installed-skills.json", "installed_skills"), ("installed-agents.json", "installed_agents")):
    try:
        index = json.loads((ROOT / "state" / filename).read_text(encoding="utf-8"))
        registry[target] = index.get("skills" if target == "installed_skills" else "agents", [])
        if target == "installed_skills":
            registry["duplicate_resolutions"] = index.get("duplicate_resolutions", [])
    except (FileNotFoundError, json.JSONDecodeError):
        pass
(ROOT / "registry.json").write_text(
    json.dumps(registry, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(f"Built registry with {len(registry['capabilities'])} registered capabilities, "
      f"{len(registry['installed_skills'])} skills, and {len(registry['installed_agents'])} agents.")

#!/usr/bin/env python3
"""
CHECK-ONLY upstream revision checker.

Requires:
- git installed
- network access to github.com

It does NOT clone, pull, merge, or overwrite anything.
It records the latest remote commit SHA for each registered source.
"""
from pathlib import Path
import json
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
SOURCES = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
STATE_PATH = ROOT / "state" / "source-revisions.json"

try:
    old_state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
except FileNotFoundError:
    old_state = {"sources": {}}

new_state = {
    "checked_at_utc": datetime.now(timezone.utc).isoformat(),
    "sources": {}
}

changed = []
errors = []

for item in SOURCES["sources"]:
    repo = item["repo"]
    branch = item["default_branch"]
    url = f"https://github.com/{repo}.git"
    try:
        result = subprocess.run(
            ["git", "ls-remote", url, f"refs/heads/{branch}"],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        line = result.stdout.strip()
        if not line:
            raise RuntimeError(f"No revision returned for branch {branch}")
        sha = line.split()[0]
        previous = old_state.get("sources", {}).get(item["id"], {}).get("sha")
        new_state["sources"][item["id"]] = {
            "repo": repo,
            "branch": branch,
            "sha": sha,
        }
        if previous and previous != sha:
            changed.append((item["id"], previous[:12], sha[:12]))
    except Exception as exc:
        errors.append((item["id"], str(exc)))

STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
STATE_PATH.write_text(
    json.dumps(new_state, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

print("Adaptive Skills Hub - upstream check")
print(f"Checked: {len(new_state['sources'])}/{len(SOURCES['sources'])}")

if changed:
    print("\nUpdates detected:")
    for source_id, old, new in changed:
        print(f"- {source_id}: {old} -> {new}")
else:
    print("\nNo known revision changes detected (or this is the first baseline run).")

if errors:
    print("\nErrors:")
    for source_id, error in errors:
        print(f"- {source_id}: {error}")

print("\nCHECK-ONLY: no repositories were pulled or modified.")

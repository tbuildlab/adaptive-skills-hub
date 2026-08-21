from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from .common import sha256_text, utc_now


def _command_from_metadata(metadata: dict[str, Any], key: str, skill_dir: Path) -> list[str] | None:
    command = metadata.get(key)
    if not isinstance(command, list) or not all(isinstance(part, str) for part in command):
        return None
    replacements = {"{python}": sys.executable, "{skill_dir}": str(skill_dir)}
    return [replacements.get(part, part) for part in command]


def load_selected_skills(route: dict[str, Any]) -> list[dict[str, Any]]:
    loaded: list[dict[str, Any]] = []
    for skill in route.get("selected_skills", []):
        path = Path(skill["skill_md_path"])
        try:
            instructions = path.read_text(encoding="utf-8")
            loaded.append({"name": skill["name"], "path": str(path), "sha256": sha256_text(instructions), "characters": len(instructions), "instructions": instructions})
        except (OSError, UnicodeDecodeError) as exc:
            loaded.append({"name": skill["name"], "path": str(path), "load_error": str(exc)})
    return loaded


def execute_route(route: dict[str, Any], allow_skill_commands: bool = False, timeout_seconds: int = 60) -> dict[str, Any]:
    """Load real selected instructions and optionally run explicit local command hooks.

    Plain SKILL.md prose is intentionally delegated to the Codex executor: no model or
    shell command is fabricated from it. A command hook is opt-in metadata and never
    runs with shell=True.
    """
    loaded = load_selected_skills(route)
    results: list[dict[str, Any]] = []
    validations: list[dict[str, Any]] = []
    for selected, item in zip(route.get("selected_skills", []), loaded):
        if "load_error" in item:
            results.append({"name": selected["name"], "status": "load_failed", "error": item["load_error"]})
            continue
        metadata = selected.get("metadata", {})
        command = _command_from_metadata(metadata, "hub_command", Path(selected["path"]))
        if command is None:
            results.append({"name": selected["name"], "status": "loaded_for_codex_execution"})
            continue
        if not allow_skill_commands:
            results.append({"name": selected["name"], "status": "command_not_authorized", "command": command})
            continue
        try:
            completed = subprocess.run(command, cwd=selected["path"], shell=False, capture_output=True, text=True, timeout=timeout_seconds, check=False)
            status = "command_executed" if completed.returncode == 0 else "command_failed"
            results.append({"name": selected["name"], "status": status, "returncode": completed.returncode, "stdout": completed.stdout[-2000:], "stderr": completed.stderr[-2000:]})
        except (OSError, subprocess.TimeoutExpired) as exc:
            results.append({"name": selected["name"], "status": "command_failed", "error": str(exc)})
    for selected in route.get("selected_skills", []):
        command = _command_from_metadata(selected.get("metadata", {}), "hub_validate", Path(selected["path"]))
        if command is None or not allow_skill_commands:
            continue
        completed = subprocess.run(command, cwd=selected["path"], shell=False, capture_output=True, text=True, timeout=timeout_seconds, check=False)
        validations.append({"name": selected["name"], "returncode": completed.returncode, "stdout": completed.stdout[-2000:], "stderr": completed.stderr[-2000:]})
    return {"executed_at_utc": utc_now(), "route": route, "loaded_skills": loaded, "execution": results, "validation": validations}


def write_packet(path: Path, result: dict[str, Any]) -> None:
    packet = dict(result)
    # Full instructions are necessary to hand execution to Codex, but console output stays concise.
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

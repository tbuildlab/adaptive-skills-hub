"""G6 qualification evidence only; no product adapter or release authority.

Run only against a NEW explicit destination. Reads frozen public project files;
all task state and Git changes remain in that destination. No model, cloud,
remote Git, external capability enrollment, or retired G3 approval is used.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("source", type=Path)
    cli.add_argument("destination", type=Path)
    args = cli.parse_args()
    source = args.source.resolve(strict=True)
    destination = args.destination.absolute()
    destination.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(source))
    from ash.core import read_task, run_task
    from ash.core_capabilities import inventory, summary
    from ash.core_profiles import prepare_project

    observed = {"schema": "nexus.g6.local-host-qualification.v1",
                "started_utc": datetime.now(timezone.utc).isoformat(),
                "basis": "ACTUAL_TRUSTED_LOCAL_CORE_EXECUTION_NOT_MODEL_QUALIFICATION",
                "real_admission": "NO", "dispatch_authority": "none", "cases": []}

    def git(project, *arguments):
        # Disable hook execution even in the disposable owner-controlled repository.
        result = subprocess.run(["git", "-c", "core.hooksPath=" + str(destination / "empty-hooks"),
                                 "-c", "core.autocrlf=false", *arguments], cwd=project,
                                capture_output=True, timeout=20, check=True)
        return result.stdout.decode("utf-8").strip()

    def retain(name, state, directory, **extra):
        # Core keeps the receipt INSIDE task.json; it has no receipt.json file.
        retained = destination / ("observed-state-%02d.json" % len(observed["cases"]))
        retained.write_bytes((directory / "task.json").read_bytes())
        receipt = state.get("receipt")
        receipt_bytes = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
        observed["cases"].append({"name": name, "status": state["status"],
                                   "commands_used": state["commands_used"],
                                   "task_directory": str(directory),
                                   "state_sha256": digest(retained), "retained_state": str(retained),
                                   "receipt_basis": "EMBEDDED_TASK_STATE" if receipt is not None else "NOT_FINAL",
                                   "receipt_sha256": hashlib.sha256(receipt_bytes).hexdigest() if receipt is not None else None,
                                   "blocker": state["blocker"], **extra})

    try:
        # An existing real domain document, not a canned test fixture.
        project = destination / "website-copy"
        project.mkdir()
        original = source / "docs/g4-local-workflows/index.html"
        (project / "index.html").write_bytes(original.read_bytes())
        old, new = ">Clear filter</button>", ">Clear workflow filter</button>"
        assert (project / "index.html").read_text("utf-8").count(old) == 1
        configuration = {"schema": "nexus.core.project.v1", "profile": "static-web",
                         "files": ["index.html"],
                         "patches": [{"path": "index.html", "old": old, "new": new}],
                         "checks": [{"path": "index.html", "contains": new}]}
        save(project / ".nexus.json", configuration)
        (project / ".gitignore").write_text(".nexus/\nnexus-results/\n", encoding="utf-8")
        git(project, "init", "-q")
        git(project, "add", "--", "index.html", ".nexus.json", ".gitignore")
        git(project, "-c", "user.name=Nexus G6 qualification", "-c", "user.email=qualification@example.invalid",
            "-c", "commit.gpgSign=false", "commit", "-qm", "Owner-controlled isolated G6 input snapshot")
        base = git(project, "rev-parse", "HEAD")
        # Preserve a real dirty, explicitly unexamined file; the task must not clean it.
        (project / "unexamined-note.txt").write_text("Outside the one-file edit scope.\n", encoding="utf-8")
        dirty = git(project, "status", "--porcelain=v1")
        before = digest(project / "index.html")
        state, directory = prepare_project("Improve HTML UI content and run regression tests.", project)
        state = run_task(directory, approval=state["approval_sha256"])
        assert state["status"] == "completed", state["blocker"]
        assert git(project, "diff", "--name-only") == "index.html"
        assert digest(project / "index.html") != before
        assert (project / "index.html").read_bytes() == original.read_bytes().replace(old.encode(), new.encode(), 1)
        assert "?? unexamined-note.txt" in git(project, "status", "--porcelain=v1")
        assert git(project, "rev-parse", "HEAD") == base
        assert digest(original) == before
        checks = project / state["approval_context"]["output"] / "checks.json"
        assert json.loads(checks.read_bytes())["passed"] is True
        retain("B_existing_repository_exact_change", state, directory, base_commit=base,
               input_sha256=before, output_sha256=digest(project / "index.html"),
               dirty_input=dirty, observed_changed_paths=["index.html"],
               shared_consumers=["workflows.html uses the same catalog.js/site.css; both unchanged in frozen source"],
               unexamined=["Browser interaction after this text-only copy edit; frozen G4 browser evidence is separate",
                           "unexamined-note.txt", "External deployment"],
               checks_sha256=digest(checks), frozen_original_unchanged=True)

        report = destination / "roadmap-evidence"
        report.mkdir()
        names = ["nexus-roadmap-v2.md", "nexus-g3-original-final-acceptance-freeze-v1.md",
                 "nexus-g4-final-acceptance-freeze-v1.md"]
        for name in names:
            (report / name).write_bytes((source / "docs" / name).read_bytes())
        save(report / ".nexus.json", {"schema": "nexus.core.project.v1", "profile": "evidence", "files": names})
        state, directory = prepare_project("Research local project evidence and review the software architecture.", report)
        state = run_task(directory, approval=state["approval_sha256"], max_steps=1)
        assert state["status"] == "paused" and state["commands_used"] == 2
        artifact = report / state["approval_context"]["output"] / "inventory.json"
        prior = artifact.stat().st_mtime_ns, digest(artifact)
        budget, created = dict(state["budget"]), state["created_at_utc"]
        retain("D_pause_after_verified_effect", state, directory, inventory_sha256=prior[1])
        # Resume in another interpreter: task state, not Python object identity.
        code = ("from pathlib import Path; from ash.core import read_task,run_task; "
                "import sys; p=Path(sys.argv[1]); s=read_task(p); "
                "r=run_task(p,approval=s['approval_sha256']); assert r['status']=='completed',r['blocker']")
        subprocess.run([sys.executable, "-X", "utf8", "-c", code, str(directory)], cwd=source,
                       check=True, capture_output=True, timeout=90)
        state = read_task(directory)
        assert state["commands_used"] == 4 and state["budget"] == budget and state["created_at_utc"] == created
        assert (artifact.stat().st_mtime_ns, digest(artifact)) == prior
        settings = state["approval_context"]
        output = report / settings["output"] / "summary.md"
        assert output.read_bytes() == summary(report, settings)
        assert json.loads(artifact.read_bytes()) == inventory(report, settings)
        for name in names:
            assert digest(report / name) == digest(source / "docs" / name)
        retain("C_real_source_bound_report_and_D_fresh_process_resume", state, directory,
               artifact_sha256=digest(output), report_path=str(output), sources=inventory(report, settings),
               inventory_not_redispatched=True, budgets_and_deadline_preserved=True,
               semantic_claims="Only file metadata and explicitly quoted first lines; no invented interpretation")

        # Separate fresh tasks: no replay or alteration of any historical task.
        state, directory = prepare_project("Research local project evidence and review the software architecture.", report)
        blocked = run_task(directory, approval=None)
        assert blocked["commands_used"] == 0 and blocked["status"] == "prepared"
        retain("A_no_opt_in_no_effect_NOT_AUTHENTICATED_G3_APPROVAL", blocked, directory)
        victim = report / names[0]
        original_bytes = victim.read_bytes()
        victim.write_bytes(original_bytes + b"\nG6 isolated substitution negative control.\n")
        blocked = run_task(directory, approval=state["approval_sha256"])
        assert blocked["status"] == "blocked" and blocked["commands_used"] == 0
        retain("A_input_substitution_before_dispatch", blocked, directory)
        victim.write_bytes(original_bytes)  # Restore only this owned copy, never source.
        observed["status"] = "PASS_BOUNDED_LOCAL_CASES_ONLY"
    except Exception as exc:
        observed["status"] = "FAIL_OR_HOLD"
        observed["error_class"] = type(exc).__name__
        raise
    finally:
        observed["finished_utc"] = datetime.now(timezone.utc).isoformat()
        save(destination / "qualification.json", observed)
        print(json.dumps({"status": observed["status"], "cases": len(observed["cases"]),
                          "evidence": str(destination / "qualification.json"), "real_admission": "NO"}))


if __name__ == "__main__":
    main()

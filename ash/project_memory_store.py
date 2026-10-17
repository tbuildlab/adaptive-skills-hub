"""Host-only bounded bundle persistence; read paths never create or repair data."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import tempfile

from . import project_memory as model
from .mcp.authorization import AuthorizedWorkspace, _assert_no_reparse_chain, _canonical_root, _inside, guard_regular_file, verify_unchanged
from .mcp.schemas import NexusMcpError
from .reusable_references import load_library, workspace_binding

ROOT = Path(__file__).resolve().parents[1]
MARKER = {"schema_version": "nexus.project-memory.root.v1", "storage": "host_owned_project_local"}


def _require_d_drive(root):
    model.require(os.name == "nt" and root.drive.casefold() == "d:", "project_memory_invalid_root")
    import ctypes
    model.require(ctypes.windll.kernel32.GetDriveTypeW(str(root.anchor)) == 3, "project_memory_invalid_root")


def _lexical_path(value):
    model.require(type(value) is str and value and len(value.encode("utf-8")) <= 512,
                  "project_memory_invalid_root")
    path = Path(value)
    model.require(path.is_absolute() and not value.startswith(("\\", "//")) and path != Path(path.anchor),
                  "project_memory_invalid_root")
    for part in path.parts[1:]:
        model.require(part not in {".", ".."} and not part.endswith((".", " "))
                      and not any(c in part for c in ':*?<>|%')
                      and not re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", part),
                      "project_memory_invalid_root")
    # Path normalizes dot components, so inspect raw spelling as well.
    model.require(not any(p in {".", ".."} for p in value.replace("\\", "/").split("/")),
                  "project_memory_invalid_root")
    return path


def stable_read(path, root, limit):
    guarded, before = guard_regular_file(path, [root])
    model.require(before.st_size <= limit and before.st_nlink == 1, "project_memory_unsafe_file")
    with guarded.open("rb") as handle:
        opened = os.fstat(handle.fileno())
        model.require((opened.st_dev, opened.st_ino) == (before.st_dev, before.st_ino))
        raw = handle.read(limit + 1)
    verify_unchanged(guarded, before)
    guard_regular_file(path, [root])
    model.require(len(raw) <= limit, "project_memory_size_limit")
    return raw


class MemoryStore:
    def __init__(self, config):
        model.validate(config, "config")
        model.require(config["enabled"], "project_memory_unavailable")
        self.path = _lexical_path(config["root"])
        _require_d_drive(self.path)

    def root(self, workspace=None, *, allow_missing=False):
        _require_d_drive(self.path)
        candidate = self.path
        while not os.path.lexists(candidate):
            model.require(allow_missing, "project_memory_unavailable")
            candidate = candidate.parent
        if candidate == Path(candidate.anchor):
            _assert_no_reparse_chain(candidate)
            model.require(candidate.is_dir(), "project_memory_unavailable")
            ancestor = candidate
        else:
            ancestor = _canonical_root(candidate)
        # Do not create storage in repositories/worktrees, managed runtime or caches.
        for parent in (ancestor, *ancestor.parents):
            model.require(not os.path.lexists(parent / ".git") and not (parent / "HEAD").is_file(),
                          "project_memory_invalid_root")
        model.require(not any(part.casefold() in {".codex", ".agents", ".cache", "releases", "runtime", "node_modules"}
                              for part in self.path.parts), "project_memory_invalid_root")
        if workspace is not None:
            approved = _canonical_root(workspace.root)
            model.require(not _inside(approved, self.path) and not _inside(self.path, approved),
                          "project_memory_invalid_root")
        model.require(not _inside(ROOT, self.path) and not _inside(self.path, ROOT), "project_memory_invalid_root")
        return _canonical_root(self.path) if self.path.exists() else self.path

    def initialize(self, workspace, *, authorized, authorization_ref):
        model.require(authorized is True, "project_memory_authorization_required")
        model._validate(authorization_ref, model.ID)
        model.screen(authorization_ref)
        root = self.root(workspace, allow_missing=True)
        if not root.exists():
            # Create only validated missing components, rechecking each ancestor.
            missing = []
            current = root
            while not current.exists():
                missing.append(current)
                current = current.parent
            for directory in reversed(missing):
                if directory.parent == Path(directory.anchor):
                    _assert_no_reparse_chain(directory.parent)
                else:
                    _canonical_root(directory.parent)
                directory.mkdir()
                _canonical_root(directory)
        root = self.root(workspace)
        entries = self.root_entries(root)
        if entries:
            self.check_layout(root)
            return
        with (root / model.ROOT_MARKER).open("xb") as handle:
            handle.write(model.encoded(MARKER))
            handle.flush()
            os.fsync(handle.fileno())
        (root / "projects").mkdir()
        self.check_layout(root)

    def check_layout(self, root):
        model.require(model.parse(stable_read(root / model.ROOT_MARKER, root, 1024), 1024) == MARKER)
        directory = _canonical_root(root / "projects")
        model.require(_inside(root, directory))
        # A single fixed layout; no unbounded recursive traversal.
        model.require(set(self.root_entries(root)) <= {model.ROOT_MARKER, "projects", ".write.lock"})
        return directory

    @staticmethod
    def root_entries(root):
        names = []
        with os.scandir(root) as iterator:
            for entry in iterator:
                model.require(len(names) < 3, "project_memory_invalid")
                names.append(entry.name)
        return names

    def entries(self, directory):
        entries = []
        with os.scandir(directory) as iterator:
            for entry in iterator:
                model.require(len(entries) < model.MAX_PROJECTS, "project_memory_capacity_reached")
                model.require(re.fullmatch(r"[a-f0-9]{64}\.[a-f0-9]{32}\.json", entry.name), "project_memory_invalid")
                entries.append(Path(entry.path))
        return entries

    def read_bundle(self, path, root):
        return model.validate_bundle(model.parse(stable_read(path, root, model.MAX_BUNDLE_BYTES), model.MAX_BUNDLE_BYTES))

    def lookup(self, workspace, project_id=None):
        root = self.root(workspace)
        directory = self.check_layout(root)
        binding = workspace_binding(_canonical_root(workspace.root))
        if project_id is not None:
            model._validate(project_id, model.string(32, model.PROJECT_ID))
        matches = [p for p in self.entries(directory) if p.name.startswith(binding + ".")
                   and (project_id is None or p.name == binding + "." + project_id + ".json")]
        if len(matches) > 1:
            raise model.MemoryError("project_memory_ambiguous")
        if not matches:
            raise model.MemoryError("project_memory_missing")
        bundle = self.read_bundle(matches[0], root)
        latest = bundle["revisions"][-1]
        self.check_identity(latest["identity"], workspace)
        model.require(matches[0].name == binding + "." + bundle["project_id"] + ".json")
        return bundle

    @staticmethod
    def check_identity(identity, workspace):
        model.require(type(workspace) is AuthorizedWorkspace, "project_memory_unauthorized_workspace")
        approved = _canonical_root(workspace.root)
        locator = _canonical_root(_lexical_path(identity["project_locator"]))
        model.require(_inside(approved, locator) and identity["workspace_binding"] == workspace_binding(approved),
                      "project_memory_unauthorized_workspace")
        model.require(str(locator) == identity["project_locator"], "project_memory_unsafe_locator")
        return locator

    @contextmanager
    def lock(self, root):
        path = root / ".write.lock"
        try:
            handle = path.open("xb")
        except FileExistsError as exc:
            raise model.MemoryError("project_memory_writer_conflict") from exc
        try:
            yield
        finally:
            handle.close()
            path.unlink()

    def persist(self, proposal, workspace, *, authorized, authorization_ref, expected_previous_digest,
                privacy_reviewed, reference_reader=load_library):
        model.require(authorized is True and privacy_reviewed is True, "project_memory_authorization_required")
        model._validate(authorization_ref, model.ID)
        model.screen(authorization_ref)
        model.validate_proposal(proposal)
        locator = self.check_identity(proposal["identity"], workspace)
        root = self.root(workspace)
        directory = self.check_layout(root)
        verify_evidence(proposal, locator)
        if proposal["references_used"]:
            snapshot = reference_reader()
            model.require(snapshot.status == "loaded", "project_memory_references_unavailable")
            known = {r["id"] for r in snapshot.records if r["workspace"] in {workspace_binding(workspace.root), "shared"}
                     and r["acceptance"] in {"accepted", "preferred"}}
            model.require({r["reference_id"] for r in proposal["references_used"]} <= known,
                          "project_memory_unknown_reference")
        identity = proposal["identity"]
        target = directory / (identity["workspace_binding"] + "." + identity["project_id"] + ".json")
        with self.lock(root):
            self.root(workspace)
            self.check_layout(root)
            entries = self.entries(directory)
            old = self.read_bundle(target, root) if os.path.lexists(target) else None
            current = old["current_digest"] if old else None
            model.require(current == expected_previous_digest, "project_memory_digest_conflict")
            if old:
                self.check_identity(old["revisions"][-1]["identity"], workspace)
                model.require(all(old["revisions"][-1]["identity"][key] == identity[key]
                                  for key in ("project_id", "workspace_binding", "project_locator")))
                validate_supersessions(old["revisions"][-1], proposal)
            else:
                model.require(len(entries) < model.MAX_PROJECTS, "project_memory_capacity_reached")
                model.require(not proposal["supersessions"])
            revisions = list(old["revisions"]) if old else []
            model.require(len(revisions) < model.MAX_REVISIONS, "project_memory_capacity_reached")
            revision = {key: proposal[key] for key in model.PROPOSAL_FIELDS}
            revision.update(schema_version="nexus.project-memory.revision.v1", number=len(revisions) + 1,
                            previous_digest=current, written_at=datetime.now(timezone.utc).isoformat(),
                            authorization_ref=authorization_ref)
            revision["revision_digest"] = model.digest(revision)
            revisions.append(revision)
            bundle = {"schema_version": "nexus.project-memory.bundle.v1", "project_id": identity["project_id"],
                      "workspace_binding": identity["workspace_binding"], "current_digest": revision["revision_digest"],
                      "revisions": revisions}
            model.validate_bundle(bundle)
            raw = model.encoded(bundle)
            sizes = sum(guard_regular_file(p, [root])[1].st_size for p in entries)
            model.require(sizes - (target.stat().st_size if old else 0) + len(raw) <= model.MAX_STORE_BYTES,
                          "project_memory_capacity_reached")
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(dir=directory, prefix=".memory-", delete=False) as handle:
                    temporary = Path(handle.name)
                    handle.write(raw)
                    handle.flush()
                    os.fsync(handle.fileno())
                self.root(workspace)
                self.check_layout(root)
                if old:
                    model.require(self.read_bundle(target, root)["current_digest"] == current,
                                  "project_memory_digest_conflict")
                else:
                    model.require(not os.path.lexists(target), "project_memory_digest_conflict")
                os.replace(temporary, target)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
        receipt = dict(schema_version="nexus.project-memory.write-receipt.v1", status="persisted",
            project_id=identity["project_id"], workspace_binding=identity["workspace_binding"],
            revision=revision["number"], previous_digest=current, revision_digest=revision["revision_digest"],
            bundle_digest=hashlib.sha256(raw).hexdigest(), authorization_ref=authorization_ref)
        return model.validate(receipt, "write_receipt")


def validate_supersessions(previous, proposal):
    model.validate_supersessions(previous, proposal)


def verify_evidence(proposal, locator):
    # Read only named, bounded approved pointers. Never execute a validator.
    for item in proposal["evidence"] + proposal["artifacts"]:
        if item["sha256"] is not None:
            raw = stable_read(locator / item["locator"], locator, 128 * 1024)
            model.require(hashlib.sha256(raw).hexdigest() == item["sha256"], "project_memory_evidence_mismatch")
    completion = proposal["completion"]
    if completion["kind"] not in {"project_completed", "validated_checkpoint"}:
        return
    evidence = next(e for e in proposal["evidence"] if e["id"] == completion["receipt_id"])
    receipt = model.parse(stable_read(locator / evidence["locator"], locator, 32 * 1024), 32 * 1024)
    model.validate(receipt, "validation_receipt")
    model.screen(receipt)
    model.require(all(receipt[key] == completion[key] for key in
                      ("scope", "scope_complete", "automated_validation", "validated_at", "checks"))
                  and receipt["project_id"] == proposal["identity"]["project_id"]
                  and receipt["workspace_binding"] == proposal["identity"]["workspace_binding"],
                  "project_memory_completion_unverified")
    model.require(receipt["artifact_digests"], "project_memory_completion_unverified")
    for artifact in receipt["artifact_digests"]:
        model.safe_locator(artifact["locator"])
        raw = stable_read(locator / artifact["locator"], locator, 128 * 1024)
        model.require(hashlib.sha256(raw).hexdigest() == artifact["sha256"], "project_memory_evidence_mismatch")


def load_config(workspace_config):
    parent = _canonical_root(Path(workspace_config).parent)
    path = parent / model.CONFIG_NAME
    config = model.parse(stable_read(path, parent, 4096), 4096)
    return MemoryStore(model.validate(config, "config"))

"""Installer alias protection using only disposable local state."""
import argparse
import contextlib
import io
import hashlib
import json
import os
from pathlib import Path
import sys
import shutil
import subprocess
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from scripts import setup_nexus as setup
from scripts import release_install as release


class WorkspaceAliasPreservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.data = self.root / "data"
        self.project = self.root / "project"
        self.other = self.root / "other"
        self.project.mkdir()
        self.other.mkdir()
        self.args = argparse.Namespace(
            data_root=str(self.data), workspace_root=str(self.project),
            workspace_id="nexus-default", runtime_python=str(Path(sys.executable).resolve()),
            with_plugin=False, codex_command="", mode="standalone", migrate_standalone=False,
        )

    def tearDown(self):
        self.temp.cleanup()

    def seed(self, entries):
        self.data.mkdir(exist_ok=True)
        payload = {"schema_version": setup.WORKSPACE_SCHEMA_VERSION, "workspaces": entries}
        (self.data / "workspaces.json").write_text(json.dumps(payload), encoding="utf-8")
        (self.data / setup.CONFIG_FILENAME).write_bytes(b'{"preserve":"original config"}\n')
        return payload

    def snapshot(self):
        return {p.relative_to(self.data).as_posix(): p.read_bytes()
                for p in self.data.rglob("*") if p.is_file()}

    def test_setup_conflict_has_no_writes_or_runtime_creation(self):
        self.seed({"nexus-default": {"root": str(self.other)}})
        before = self.snapshot()
        self.args.runtime_python = None
        with patch.object(setup, "create_runtime") as runtime, patch.object(setup.subprocess, "run") as probe:
            with self.assertRaisesRegex(setup.SetupError, "different root"):
                setup.install(self.args)
        runtime.assert_not_called()
        probe.assert_not_called()
        self.assertEqual(self.snapshot(), before)

    def test_matching_normalized_root_is_idempotent_and_preserves_record(self):
        child = self.project / "child"
        child.mkdir()
        original = self.seed({"nexus-default": {"root": str(child) + "/..", "label": "retained"}})
        forms = [str(self.project), str(child) + "/.."]
        if os.name == "nt":
            forms.append(str(self.project).swapcase())
        with patch.object(setup.subprocess, "run"), contextlib.redirect_stdout(io.StringIO()):
            for form in forms:
                self.args.workspace_root = form
                self.assertEqual(setup.install(self.args), 0)
                self.assertEqual(setup.load_workspaces(self.data / "workspaces.json"), original)

    def test_fresh_alias_preserves_other_mappings(self):
        original = self.seed({"existing": {"root": str(self.other)}})
        with patch.object(setup.subprocess, "run"), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(setup.install(self.args), 0)
        result = setup.load_workspaces(self.data / "workspaces.json")
        self.assertEqual(result["workspaces"]["existing"], original["workspaces"]["existing"])
        self.assertEqual(result["workspaces"]["nexus-default"], {"root": str(self.project.resolve())})

    def test_fresh_data_directory_registration(self):
        self.assertFalse(self.data.exists())
        with patch.object(setup.subprocess, "run"), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(setup.install(self.args), 0)
        self.assertEqual(setup.load_workspaces(self.data / "workspaces.json"), {
            "schema_version": setup.WORKSPACE_SCHEMA_VERSION,
            "workspaces": {"nexus-default": {"root": str(self.project.resolve())}},
        })

    def test_release_conflict_precedes_marketplace_transaction_and_runtime(self):
        self.seed({"nexus-default": {"root": str(self.other)}})
        self.args.mode = "plugin"
        before = self.snapshot()
        with patch.object(release, "verify_release_tree", return_value={"version": "0.4.0-rc.1"}), \
             patch.object(release, "bundled_runtime") as runtime, \
             patch.object(release.desktop_marketplace, "install") as marketplace, \
             patch.object(release, "atomic_json_write") as write:
            with self.assertRaisesRegex(setup.SetupError, "different root"):
                release.install(self.args)
        runtime.assert_not_called()
        marketplace.assert_not_called()
        write.assert_not_called()
        self.assertEqual(self.snapshot(), before)

    def test_release_registration_and_supported_rollback_restore_exact_bytes(self):
        self.seed({"existing": {"root": str(self.other)}})
        before = self.snapshot()
        with patch.object(release, "verify_release_tree", return_value={"version": "0.4.0-rc.1"}), \
             patch.object(release, "bundled_runtime", return_value=Path(sys.executable).resolve()), \
             patch.object(setup.subprocess, "run"), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(release.install(self.args), 0)
            self.assertIn("nexus-default", setup.load_workspaces(self.data / "workspaces.json")["workspaces"])
            self.assertEqual(release.uninstall(self.args, rollback=True), 0)
        for name, raw in before.items():
            self.assertEqual((self.data / name).read_bytes(), raw)
        self.assertFalse(release.state_path(self.data).exists())

    def test_failure_after_configure_uses_existing_rollback(self):
        self.seed({"existing": {"root": str(self.other)}})
        self.args.mode = "plugin"
        before = self.snapshot()
        configure = release.configure

        def fail_after_configure(args, root):
            configure(args, root)
            raise RuntimeError("injected post-configuration failure")

        with patch.object(release, "verify_release_tree", return_value={"version": "0.4.0-rc.1"}), \
             patch.object(release, "bundled_runtime", return_value=Path(sys.executable).resolve()), \
             patch.object(setup.subprocess, "run"), \
             patch.object(release.desktop_marketplace, "install", return_value={"owner": "test fixture"}), \
             patch.object(release.desktop_marketplace, "uninstall") as rollback, \
             patch.object(release, "configure", side_effect=fail_after_configure), \
             contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "injected"):
                release.install(self.args)
        rollback.assert_called_once_with(rollback=True)
        for name, raw in before.items():
            self.assertEqual((self.data / name).read_bytes(), raw)
        self.assertFalse(release.state_path(self.data).exists())
        journals = list((self.data / "transactions").glob("*.json"))
        self.assertEqual(len(journals), 1)
        self.assertEqual(json.loads(journals[0].read_text())["status"], "rolled_back")

    def test_invalid_existing_record_is_not_replaced(self):
        for record in (None, {}, {"root": 123}):
            with self.subTest(record=record):
                self.seed({"nexus-default": record})
                before = self.snapshot()
                with self.assertRaises(setup.SetupError):
                    setup.install(self.args)
                self.assertEqual(self.snapshot(), before)


@unittest.skipUnless(os.name == "nt" and shutil.which("powershell.exe"), "Windows PowerShell required")
class BootstrapAliasPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        self.other = self.root / "other"
        self.data = self.root / "data"
        for path in (self.project, self.other, self.data):
            path.mkdir()
        self.archive = self.root / "release.zip"
        with zipfile.ZipFile(self.archive, "w") as archive:
            archive.writestr("Nexus-fixture/sentinel.txt", "extraction reached")
        self.receipt = self.root / "release.sha256"
        self.script = Path(__file__).resolve().parents[1] / "scripts/Install-Nexus.ps1"
        self.env = os.environ.copy()
        profile = self.root / "profile"
        profile.mkdir()
        self.env.update(USERPROFILE=str(profile), LOCALAPPDATA=str(profile / "local"),
                        APPDATA=str(profile / "roaming"),
                        PSModuleAnalysisCachePath=str(self.root / "module-cache"))
        modules = str(Path(os.environ["SystemRoot"]) / "System32/WindowsPowerShell/v1.0/Modules")
        self.env["PSModulePath"] = modules + os.pathsep + self.env.get("PSModulePath", "")

    def seed(self, entries):
        (self.data / "workspaces.json").write_text(json.dumps({
            "schema_version": setup.WORKSPACE_SCHEMA_VERSION, "workspaces": entries,
        }), encoding="utf-8")
        (self.data / setup.CONFIG_FILENAME).write_bytes(b'{"unchanged":true}\n')

    def snapshot(self):
        return {p.relative_to(self.data).as_posix(): p.read_bytes() if p.is_file() else None
                for p in self.data.rglob("*")}

    def run_bootstrap(self, workspace=None, default_data=False, mode="plugin"):
        self.receipt.write_text(hashlib.sha256(self.archive.read_bytes()).hexdigest(), encoding="ascii")
        arguments = ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                     "-File", str(self.script), "-ArchivePath", str(self.archive),
                     "-ChecksumPath", str(self.receipt), "-WorkspaceRoot", workspace or str(self.project),
                     "-Mode", mode]
        if not default_data:
            arguments += ["-DataRoot", str(self.data)]
        result = subprocess.run(arguments, cwd=self.root, env=self.env, capture_output=True, timeout=45)
        self.assertNotEqual(result.returncode, 0)  # Fixture deliberately has no runtime.
        return (result.stdout + result.stderr).decode("utf-8", errors="replace")

    def assert_refused(self, message, **kwargs):
        before = self.snapshot()
        output = self.run_bootstrap(**kwargs)
        self.assertIn(message, output)
        self.assertEqual(self.snapshot(), before, output)
        self.assertFalse((self.data / "releases").exists())

    def assert_reaches_extraction(self, **kwargs):
        before = self.snapshot()
        output = self.run_bootstrap(**kwargs)
        self.assertIn("release-owned embedded Python runtime is unavailable", output)
        self.assertEqual((self.data / "releases/Nexus-fixture/sentinel.txt").read_text(), "extraction reached")
        for name, content in before.items():
            if content is not None:
                self.assertEqual((self.data / name).read_bytes(), content)

    def test_conflict_before_even_opening_archive_zero_installation_writes(self):
        self.seed({"nexus-default": {"root": str(self.other)}})
        self.archive.write_bytes(b"not a zip; preflight must run before opening")
        self.assert_refused("workspace ID already belongs to a different root")

    def test_normalized_matching_alias_preserves_existing_configuration(self):
        child = self.project / "child"
        child.mkdir()
        self.seed({"nexus-default": {"root": str(child) + "/..", "label": "preserved"}})
        self.assert_reaches_extraction(workspace=str(self.project).swapcase() + "\\", mode="standalone")

    def test_new_alias_preserves_unrelated_registration(self):
        self.seed({"existing": {"root": str(self.other)}})
        self.assert_reaches_extraction()

    def test_fresh_data_root_allows_normal_path(self):
        self.data.rmdir()
        self.assert_reaches_extraction()

    def test_case_distinct_id_is_not_an_existing_alias(self):
        self.seed({"Nexus-Default": {"root": str(self.other)}})
        self.assert_reaches_extraction()

    def test_default_data_root_conflict_zero_writes(self):
        self.data = Path(self.env["LOCALAPPDATA"]) / "Nexus"
        self.data.mkdir(parents=True)
        self.seed({"nexus-default": {"root": str(self.other)}})
        self.assert_refused("workspace ID already belongs to a different root", default_data=True)

    def test_malformed_registration_is_refused_without_writes(self):
        self.seed({"nexus-default": {"ROOT": str(self.project)}})
        self.assert_refused("existing workspace registration is invalid")

    def test_invalid_configuration_is_refused_without_writes(self):
        (self.data / "workspaces.json").write_text('{"schema_version":"wrong","workspaces":{}}')
        self.assert_refused("existing workspace configuration is invalid")

    def test_junction_matching_root_uses_resolved_identity(self):
        junction = self.root / "junction"
        result = subprocess.run(["cmd.exe", "/c", "mklink", "/J", str(junction), str(self.project)],
                                capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.addCleanup(junction.rmdir)
        self.seed({"nexus-default": {"root": str(junction)}})
        self.assert_reaches_extraction()


if __name__ == "__main__":
    unittest.main()

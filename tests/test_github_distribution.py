from __future__ import annotations

import base64
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from scripts.release_common import (
    ReleaseError,
    load_manifest,
    safe_extract,
    safe_member_name,
    verify_release_tree,
)
import scripts.release_install as release_install
import scripts.build_release as release_build
import scripts.rebase_release as rebase_release
import scripts.setup_nexus as setup
import scripts.desktop_marketplace as desktop_marketplace


ROOT = Path(__file__).resolve().parents[1]


def write_test_wheel(directory: Path) -> Path:
    wheel = directory / "example_dependency-1.0.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr("example_dependency-1.0.0.dist-info/METADATA", "Metadata-Version: 2.1\nName: example-dependency\nVersion: 1.0.0\n")
    return wheel


def write_test_embed(directory: Path) -> tuple[Path, dict[str, str]]:
    """A structural fixture; real embedded-runtime acceptance is separate."""
    archive = directory / "test-python-embed.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("python.exe", "test executable")
        bundle.writestr("python313._pth", "python313.zip\n.\n")
        bundle.writestr("LICENSE.txt", "PSF test notice")
    return archive, {
        "schema_version": "nexus.windows.embedded-runtime.v1",
        "provider": "Python Software Foundation",
        "python_version": "3.13.15",
        "platform": "win-amd64",
        "filename": archive.name,
        "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
        "source_url": "https://example.invalid/python-embed.zip",
        "license": "PSF-2.0",
        "license_notice": "runtime/python/LICENSE.txt",
        "python_pth": "python313._pth",
    }


def write_static_manifest(root: Path) -> None:
    """Write the closed LF-normalized source-integrity fixture used by releases."""
    entries: dict[str, dict[str, int | str]] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.name == "MANIFEST.json":
            continue
        contents = path.read_bytes()
        try:
            contents = contents.decode("utf-8").replace("\r\n", "\n").encode("utf-8")
        except UnicodeDecodeError:
            pass
        entries[path.relative_to(root).as_posix()] = {
            "bytes": len(contents),
            "sha256": hashlib.sha256(contents).hexdigest(),
        }
    (root / "MANIFEST.json").write_text(
        json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n",
        encoding="utf-8",
        newline="\n",
    )


class GitHubDistributionTests(unittest.TestCase):
    def build_candidate(self, temporary: Path) -> tuple[Path, Path]:
        wheelhouse = temporary / "reviewed wheels"
        wheelhouse.mkdir()
        write_test_wheel(wheelhouse)
        embed, spec = write_test_embed(temporary)
        output = temporary / "release output"
        with patch.object(release_build, "runtime_spec", return_value=spec), patch.object(release_build, "embedded_runtime_self_check"):
            archive, _ = release_build.build(output, "0.1.0-rc.2", wheelhouse, embed)
        self.assertTrue(archive.is_file())
        self.assertTrue(archive.with_suffix(".zip.sha256").is_file())
        self.assertTrue((output / "Install-Nexus-0.1.0-rc.2.ps1").is_file())
        self.assertTrue((output / "Install-Nexus-0.1.0-rc.2.ps1.sha256").is_file())
        manifest = output / "Nexus-0.1.0-rc.2.release-manifest.json"
        self.assertTrue(manifest.is_file())
        self.assertEqual(manifest.with_suffix(manifest.suffix + ".sha256").read_text(encoding="ascii").split()[0], hashlib.sha256(manifest.read_bytes()).hexdigest())
        return archive, output

    def test_release_artifact_is_allowlisted_hashed_and_location_independent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            archive, output = self.build_candidate(Path(temporary))
            receipt = archive.with_suffix(".zip.sha256").read_text(encoding="ascii").split()[0]
            self.assertEqual(receipt, hashlib.sha256(archive.read_bytes()).hexdigest())
            with zipfile.ZipFile(archive) as bundle:
                names = bundle.namelist()
                self.assertTrue(all(name.startswith("Nexus-0.1.0-rc.2/") for name in names))
                text_names = [name for name in names if not name.endswith(".whl")]
                joined = "\n".join(bundle.read(name).decode("utf-8", errors="ignore") for name in text_names)
                self.assertIn("Nexus-0.1.0-rc.2/release-manifest.json", names)
                self.assertIn("Nexus-0.1.0-rc.2/requirements-release.lock", names)
                self.assertIn("Nexus-0.1.0-rc.2/research/nexus-ecosystem-gap-scan.json", names)
                self.assertIn("Nexus-0.1.0-rc.2/config/scout-sources.json", names)
                self.assertIn("Nexus-0.1.0-rc.2/ash/scout.py", names)
                self.assertIn("Nexus-0.1.0-rc.2/ash/semantic_domains.py", names)
                self.assertIn("Nexus-0.1.0-rc.2/config/skill-applicability.json", names)
                self.assertNotIn("Nexus-0.1.0-rc.2/wheelhouse/example_dependency-1.0.0-py3-none-any.whl", names)
                self.assertIn("Nexus-0.1.0-rc.2/runtime/python/python.exe", names)
                self.assertNotIn("D:" + chr(92) + "chatgpt", joined)
                self.assertNotIn("C:" + chr(92) + "Users" + chr(92) + "De Yong", joined)
                self.assertNotIn("state/installed-skills.json", names)
                self.assertFalse(any("__pycache__" in name or name.endswith(".pyc") for name in names))
                payload = json.loads(bundle.read("Nexus-0.1.0-rc.2/plugins/nexus-desktop/.codex-plugin/plugin.json"))
                self.assertEqual(payload["version"], "0.1.0-rc.2")
                source_payload = json.loads(
                    (ROOT / "plugins" / "nexus-desktop" / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
                )
                self.assertEqual(payload["description"], source_payload["description"])
                self.assertIn("server-issued short-lived Host inventory tickets", payload["description"])
                self.assertEqual(bundle.read("Nexus-0.1.0-rc.2/release/VERSION").decode("utf-8"), "0.1.0-rc.2\n")
                mcp = json.loads(bundle.read("Nexus-0.1.0-rc.2/plugins/nexus-desktop/.mcp.json"))
                self.assertEqual(mcp["mcpServers"]["nexus_desktop_local"]["command"], "../../runtime/python/python.exe")
            extracted = safe_extract(archive, output / "clean machine path with spaces")
            manifest = verify_release_tree(extracted)
            self.assertEqual(manifest["version"], "0.1.0-rc.2")
            applicability = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    "-c",
                    (
                        "import json,sys;from pathlib import Path;root=Path(sys.argv[1]);"
                        "sys.path.insert(0,str(root));"
                        "from ash.semantic_domains import load_trusted_applicability_registry;"
                        "registry=load_trusted_applicability_registry(root=root);"
                        "print(json.dumps({'rules':len(registry.rules)}))"
                    ),
                    str(extracted),
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(applicability.returncode, 0, applicability.stderr)
            self.assertEqual(json.loads(applicability.stdout), {"rules": 24})
            check = subprocess.run([sys.executable, str(extracted / "scripts" / "release_install.py"), "verify"], capture_output=True, text=True)
            self.assertEqual(check.returncode, 0, check.stderr)

            isolated = subprocess.run(
                [
                    sys.executable,
                    "-I",
                    "-c",
                    (
                        "import json,sys;from pathlib import Path;root=Path(sys.argv[1]);"
                        "sys.path.insert(0,str(root));"
                        "from ash.runtime_decision import RuntimeCapabilityAdapter,parse_runtime_requirements;"
                        "from ash.scout import ScoutRuntimeAdapter,parse_scout_request;"
                        "from datetime import datetime,timezone;"
                        "adapter=RuntimeCapabilityAdapter(root/'config'/'capability-foundation.json',"
                        "root/'config'/'upstream-source-registry.json',local_roots={});"
                        "request=parse_runtime_requirements({'schema_version':'nexus.runtime-requirements.v1',"
                        "'requirements_id':'req:isolated-release','requirements_version':'1',"
                        "'task_category':'presentation','domains':['presentation'],"
                        "'outputs':['editable_pptx_create'],"
                        "'validation_requirements':['pptx_open_render_validate'],"
                        "'allowed_permissions':['write_artifact'],"
                        "'allowed_execution_mechanisms':['host_native']});"
                        "result=adapter.decide(request);"
                        # The packaged catalog is frozen August 2026 evidence.
                        # Test its fresh branch at an explicit historical clock;
                        # separately prove that a later clock removes recommendations.
                        "scout=ScoutRuntimeAdapter(adapter,root=root,clock=lambda:datetime(2026,8,28,tzinfo=timezone.utc));"
                        "scout_request=parse_scout_request({'schema_version':'nexus.candidate-scout-request.v1',"
                        "'runtime_requirements':{'schema_version':'nexus.runtime-requirements.v1',"
                        "'requirements_id':'req:isolated-scout','requirements_version':'1',"
                        "'task_category':'mcp','domains':['skill-standard'],'outputs':[],"
                        "'validation_requirements':[],'allowed_permissions':['read_metadata'],"
                        "'allowed_execution_mechanisms':['nexus_local_read_plan']},"
                        "'source_ids':['ecosystem-gap-scan']},parse_requirements=parse_runtime_requirements);"
                        "scouted=scout.scout(scout_request);"
                        "expired=ScoutRuntimeAdapter(adapter,root=root,clock=lambda:datetime(2027,8,28,tzinfo=timezone.utc)).scout(scout_request);"
                        "print(json.dumps({'result_code':result['result_code'],"
                        "'selected':result['selected_capabilities'],"
                        "'authority':result['security_result']['mcp_execution_authority'],"
                        "'scout_status':scouted['status'],"
                        "'scout_authority':scouted['security_result']['execution_authority'],"
                        "'expired_scout_status':expired['status'],"
                        "'expired_recommendations':expired['recommended_candidate_ids'],"
                        "'expired_authority':expired['security_result']['execution_authority']}))"
                    ),
                    str(extracted),
                ],
                cwd=output,
                capture_output=True,
                text=True,
            )
            self.assertEqual(isolated.returncode, 0, isolated.stderr)
            isolated_result = json.loads(isolated.stdout)
            self.assertEqual(isolated_result, {
                "result_code": "HOST_EVIDENCE_REQUIRED",
                "selected": [],
                "authority": "none",
                "scout_status": "recommendation_ready",
                "scout_authority": "none",
                "expired_scout_status": "evidence_only",
                "expired_recommendations": [],
                "expired_authority": "none",
            })

    def test_release_archive_is_byte_reproducible_with_fixed_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            wheelhouse = base / "reviewed-wheels"
            wheelhouse.mkdir()
            wheel = write_test_wheel(wheelhouse)
            embed, spec = write_test_embed(base)
            with (
                patch.object(release_build, "runtime_spec", return_value=spec),
                patch.object(release_build, "embedded_runtime_self_check"),
            ):
                first, _ = release_build.build(
                    base / "first-output", "0.1.0-repro", wheelhouse, embed
                )
                os.utime(wheel, ns=(1_700_000_000_000_000_000,) * 2)
                os.utime(embed, ns=(1_800_000_000_000_000_000,) * 2)
                second, _ = release_build.build(
                    base / "second-output", "0.1.0-repro", wheelhouse, embed
                )

            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(
                hashlib.sha256(first.read_bytes()).hexdigest(),
                hashlib.sha256(second.read_bytes()).hexdigest(),
            )
            with zipfile.ZipFile(first) as archive:
                self.assertTrue(archive.infolist())
                self.assertEqual(
                    archive.namelist(),
                    sorted(archive.namelist(), key=lambda item: item.encode("utf-8")),
                )
                for info in archive.infolist():
                    self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
                    self.assertEqual((info.external_attr >> 16) & 0o777, 0o644)

    def test_release_manifest_excludes_host_generated_embedded_python_bytecode(self) -> None:
        """A restarted/pilot runtime must remain verifiable after bytecode exists."""
        with tempfile.TemporaryDirectory() as temporary:
            stage = Path(temporary) / "Nexus-pilot"
            cache = stage / "runtime" / "python" / "site-packages" / "example" / "__pycache__"
            cache.mkdir(parents=True)
            source = stage / "scripts" / "release_install.py"
            source.parent.mkdir(parents=True)
            source.write_text("# verified source\n", encoding="utf-8")
            (cache / "example.cpython-313.pyc").write_bytes(b"host-generated-bytecode")

            release_build.write_manifest(stage, "0.1.0-r5.pilot.1")
            manifest = json.loads((stage / "release-manifest.json").read_text(encoding="utf-8"))

            self.assertNotIn(
                "runtime/python/site-packages/example/__pycache__/example.cpython-313.pyc",
                manifest["files"],
            )
            self.assertEqual(verify_release_tree(stage)["version"], "0.1.0-r5.pilot.1")

    def test_release_manifest_schema_and_file_metadata_are_strictly_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            payload = {
                "schema_version": "nexus.release.manifest.v1",
                "product": "Nexus",
                "distribution": "github-release",
                "version": "0.1.0-test",
                "files": {"ash/module.py": {"sha256": "a" * 64, "size": 1}},
            }

            def rejected(candidate: object) -> None:
                (root / "release-manifest.json").write_text(
                    json.dumps(candidate, sort_keys=True), encoding="utf-8"
                )
                with self.assertRaises(ReleaseError):
                    load_manifest(root)

            (root / "release-manifest.json").write_text(
                json.dumps(payload, sort_keys=True), encoding="utf-8"
            )
            self.assertEqual(load_manifest(root), payload)
            for mutate in (
                lambda value: value.update(unexpected=True),
                lambda value: value.update(product="Other"),
                lambda value: value.update(distribution="other"),
                lambda value: value.update(version="../unsafe"),
                lambda value: value["files"]["ash/module.py"].update(unexpected=True),
                lambda value: value["files"]["ash/module.py"].update(sha256="A" * 64),
                lambda value: value["files"]["ash/module.py"].update(size=True),
                lambda value: value["files"].update(
                    {"ASH/MODULE.PY": {"sha256": "b" * 64, "size": 1}}
                ),
                lambda value: value.update(
                    files={"ash\\escape.py": {"sha256": "a" * 64, "size": 1}}
                ),
                lambda value: value.update(
                    files={"ash/name:stream": {"sha256": "a" * 64, "size": 1}}
                ),
                lambda value: value.update(
                    files={"ash/evil\u202etxt.py": {"sha256": "a" * 64, "size": 1}}
                ),
                lambda value: value.update(
                    files={"ash/CON.txt": {"sha256": "a" * 64, "size": 1}}
                ),
                lambda value: value.update(
                    files={"ash/.GIT/config": {"sha256": "a" * 64, "size": 1}}
                ),
                lambda value: value.update(
                    files={"ash/__PYCACHE__/module.pyc": {"sha256": "a" * 64, "size": 1}}
                ),
                lambda value: value.update(
                    files={"ash/.Env.Production": {"sha256": "a" * 64, "size": 1}}
                ),
                lambda value: value.update(
                    files={"ash/secret.PEM": {"sha256": "a" * 64, "size": 1}}
                ),
                lambda value: value.update(
                    files={"Release-Manifest.JSON": {"sha256": "a" * 64, "size": 1}}
                ),
            ):
                candidate = json.loads(json.dumps(payload))
                mutate(candidate)
                rejected(candidate)

            (root / "release-manifest.json").write_text(
                '{"schema_version":"nexus.release.manifest.v1",'
                '"schema_version":"nexus.release.manifest.v1",'
                '"product":"Nexus","distribution":"github-release",'
                '"version":"0.1.0-test","files":{"ash/module.py":'
                '{"sha256":"' + ("a" * 64) + '","size":1}}}',
                encoding="utf-8",
            )
            with self.assertRaises(ReleaseError):
                load_manifest(root)

    def test_release_rejects_every_ecosystem_state_namespace_before_staging(self) -> None:
        namespaces = (
            "ecosystem",
            "objects",
            "quarantine",
            "incoming",
            "intake-attempts",
            "evidence",
            "comparisons",
            "state",
            "receipts",
            "trees",
            "revisions",
            "components",
            "decisions",
            "locks",
            "observations",
            "staging",
            "tmp",
        )
        for namespace in namespaces:
            member = f"ash/{namespace}/sha256/object"
            with self.subTest(archive_member=namespace), self.assertRaises(ReleaseError):
                safe_member_name(member)

            with self.subTest(source_member=namespace), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                for name in release_build.ROOT_FILES | release_build.EXTRA_FILES:
                    path = root / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text("synthetic release fixture\n", encoding="utf-8")
                for directory in release_build.DIRECTORIES:
                    (root / directory).mkdir(parents=True, exist_ok=True)
                write_static_manifest(root)
                state = root / member
                state.parent.mkdir(parents=True, exist_ok=True)
                state.write_bytes(b"mutable-state-must-not-stage")
                with patch.object(release_build, "ROOT", root), self.assertRaises(ReleaseError):
                    release_build.source_members()

    def test_release_sources_are_exactly_bound_to_static_manifest(self) -> None:
        def fixture(root: Path) -> None:
            for name in release_build.ROOT_FILES | release_build.EXTRA_FILES:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("synthetic release fixture\n", encoding="utf-8")
            for directory in release_build.DIRECTORIES:
                (root / directory).mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)

            unlisted = base / "unlisted"
            fixture(unlisted)
            write_static_manifest(unlisted)
            (unlisted / "ash" / "unreviewed.py").write_text(
                "UNREVIEWED = True\n", encoding="utf-8"
            )
            with patch.object(release_build, "ROOT", unlisted), self.assertRaisesRegex(
                ReleaseError, "differ from the integrity-reviewed MANIFEST set"
            ):
                release_build.source_payloads()

            drifted = base / "drifted"
            fixture(drifted)
            reviewed = drifted / "ash" / "reviewed.py"
            reviewed.write_text("REVIEWED = True\n", encoding="utf-8")
            write_static_manifest(drifted)
            reviewed.write_text("REVIEWED = False\n", encoding="utf-8")
            with patch.object(release_build, "ROOT", drifted), self.assertRaisesRegex(
                ReleaseError, "differs from the integrity-reviewed MANIFEST"
            ):
                release_build.source_payloads()

            missing = base / "missing"
            fixture(missing)
            reviewed = missing / "ash" / "reviewed.py"
            reviewed.write_text("REVIEWED = True\n", encoding="utf-8")
            write_static_manifest(missing)
            reviewed.unlink()
            with patch.object(release_build, "ROOT", missing), self.assertRaisesRegex(
                ReleaseError, "differ from the integrity-reviewed MANIFEST set"
            ):
                release_build.source_payloads()

            valid = base / "valid"
            fixture(valid)
            normalized = valid / "ash" / "normalized.py"
            normalized.write_bytes(b"VALUE = True\r\n")
            write_static_manifest(valid)
            with patch.object(release_build, "ROOT", valid):
                payloads = {
                    path.relative_to(valid).as_posix(): contents
                    for path, contents in release_build.source_payloads()
                }
            self.assertEqual(payloads["ash/normalized.py"], b"VALUE = True\n")

    def test_release_manifest_boundary_failure_publishes_no_partial_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            root = base / "source"
            for name in release_build.ROOT_FILES | release_build.EXTRA_FILES:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("synthetic release fixture\n", encoding="utf-8")
            for directory in release_build.DIRECTORIES:
                (root / directory).mkdir(parents=True, exist_ok=True)
            write_static_manifest(root)
            (root / "ash" / "unreviewed.py").write_text(
                "UNREVIEWED = True\n", encoding="utf-8"
            )
            output = base / "output"
            with patch.object(release_build, "ROOT", root), self.assertRaisesRegex(
                ReleaseError, "differ from the integrity-reviewed MANIFEST set"
            ):
                release_build.build(
                    output,
                    "0.1.0-boundary",
                    base / "unused-wheelhouse",
                    base / "unused-embed.zip",
                )
            self.assertTrue(output.is_dir())
            self.assertEqual(list(output.iterdir()), [])

    def test_release_source_mutation_during_stable_read_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in release_build.ROOT_FILES | release_build.EXTRA_FILES:
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("synthetic release fixture\n", encoding="utf-8")
            for directory in release_build.DIRECTORIES:
                (root / directory).mkdir(parents=True, exist_ok=True)
            target = root / "ash" / "reviewed.py"
            target.write_text("REVIEWED = True\n", encoding="utf-8")
            write_static_manifest(root)

            original_read_bytes = Path.read_bytes
            mutated = False

            def read_then_mutate(path: Path) -> bytes:
                nonlocal mutated
                contents = original_read_bytes(path)
                if path == target and not mutated:
                    mutated = True
                    path.write_text("REVIEWED = False and changed\n", encoding="utf-8")
                return contents

            with (
                patch.object(release_build, "ROOT", root),
                patch.object(Path, "read_bytes", read_then_mutate),
                self.assertRaisesRegex(ReleaseError, "could not be read safely"),
            ):
                release_build.source_payloads()
            self.assertTrue(mutated)

    @unittest.skipUnless(os.name == "nt", "Windows-specific reparse-point boundary")
    def test_release_source_and_verified_tree_reject_directory_junctions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source = base / "source"
            outside = base / "outside"
            outside.mkdir()
            (outside / "external.py").write_text("external = True\n", encoding="utf-8")
            for name in release_build.ROOT_FILES | release_build.EXTRA_FILES:
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("synthetic release fixture\n", encoding="utf-8")
            for directory in release_build.DIRECTORIES:
                (source / directory).mkdir(parents=True, exist_ok=True)
            write_static_manifest(source)
            junction = source / "ash" / "linked"
            created = subprocess.run(
                ["cmd.exe", "/d", "/s", "/c", "mklink", "/J", str(junction), str(outside)],
                capture_output=True,
                text=True,
                check=False,
            )
            if created.returncode:
                self.skipTest(f"junction fixture unavailable: {created.stderr.strip()}")

            with patch.object(release_build, "ROOT", source), self.assertRaisesRegex(
                ReleaseError, "links or reparse points"
            ):
                release_build.source_members()

            # The first half models the static source tree; the second models
            # an extracted release tree, where static MANIFEST.json is itself
            # forbidden and would correctly fail before reaching the junction.
            (source / "MANIFEST.json").unlink()
            payload = source / "payload.txt"
            payload.write_bytes(b"reviewed\n")
            (source / "release-manifest.json").write_text(
                json.dumps(
                    {
                        "schema_version": "nexus.release.manifest.v1",
                        "product": "Nexus",
                        "distribution": "github-release",
                        "version": "0.1.0-test",
                        "files": {
                            "payload.txt": {
                                "sha256": hashlib.sha256(payload.read_bytes()).hexdigest(),
                                "size": payload.stat().st_size,
                            }
                        },
                    },
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ReleaseError, "links or reparse points"):
                verify_release_tree(source)

    def test_corrupted_artifact_and_traversal_are_rejected_before_install(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive, output = self.build_candidate(root)
            extracted = safe_extract(archive, output / "extract")
            target = extracted / "scripts" / "nexus_mcp.py"
            target.write_text(target.read_text(encoding="utf-8") + "# tampered\n", encoding="utf-8")
            with self.assertRaises(ReleaseError):
                verify_release_tree(extracted)
            malicious = root / "malicious.zip"
            with zipfile.ZipFile(malicious, "w") as bundle:
                bundle.writestr("Nexus-0.1.0-rc.2/../escape.txt", "no")
            with self.assertRaises(ReleaseError):
                safe_extract(malicious, root / "target")
            symlink = root / "symlink.zip"
            with zipfile.ZipFile(symlink, "w") as bundle:
                entry = zipfile.ZipInfo("Nexus-0.1.0-rc.2/link")
                entry.external_attr = 0o120777 << 16
                bundle.writestr(entry, "target")
            with self.assertRaises(ReleaseError):
                safe_extract(symlink, root / "target-symlink")

    def test_release_archive_rejects_unsafe_directory_members(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive_path = root / "candidate.zip"
            payload = b"reviewed\n"
            manifest = {
                "schema_version": "nexus.release.manifest.v1",
                "product": "Nexus",
                "distribution": "github-release",
                "version": "0.1.0-test",
                "files": {
                    "payload.txt": {
                        "sha256": hashlib.sha256(payload).hexdigest(),
                        "size": len(payload),
                    }
                },
            }
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("release/../", b"")
                archive.writestr("release/payload.txt", payload)
                archive.writestr(
                    "release/release-manifest.json",
                    json.dumps(manifest, sort_keys=True).encode("utf-8"),
                )

            with self.assertRaisesRegex(ReleaseError, "unsafe path"):
                safe_extract(archive_path, root / "output")
            self.assertFalse((root / "output").exists())

    def test_windows_bootstrap_rejects_wrong_checksum_before_extraction(self) -> None:
        if not shutil.which("powershell") and not shutil.which("pwsh"):
            self.skipTest("PowerShell is unavailable")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive, output = self.build_candidate(root)
            bad_receipt = output / "wrong.sha256"
            bad_receipt.write_text("0" * 64 + f"  {archive.name}\n", encoding="ascii")
            destination = root / "machine local data"
            bootstrap = output / "Install-Nexus-0.1.0-rc.2.ps1"
            command = shutil.which("powershell") or shutil.which("pwsh")
            result = subprocess.run([
                command, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(bootstrap),
                "-ArchivePath", str(archive), "-ChecksumPath", str(bad_receipt),
                "-WorkspaceRoot", str(root), "-DataRoot", str(destination),
            ], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((destination / "releases").exists())

    def test_release_builder_requires_a_reviewed_wheelhouse(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = subprocess.run([
                sys.executable, str(ROOT / "scripts" / "build_release.py"),
                "--output-dir", str(Path(temporary) / "out"), "--wheelhouse", str(Path(temporary) / "missing"),
                "--python-embed", str(Path(temporary) / "missing-python.zip"),
            ], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("wheelhouse", result.stdout)

    def test_rebase_builder_requires_a_pinned_verified_base_and_rewrites_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            base, _ = self.build_candidate(root)
            digest = hashlib.sha256(base.read_bytes()).hexdigest()
            with patch.object(rebase_release, "BASE_VERSION", "0.1.0-rc.2"):
                archive, receipt = rebase_release.build(
                    base,
                    base.with_suffix(".zip.sha256"),
                    root / "rebased",
                    "0.1.0-rc.5",
                    expected_base_sha256=digest,
                )
            self.assertEqual(receipt.read_text(encoding="ascii").split()[0], hashlib.sha256(archive.read_bytes()).hexdigest())
            extracted = safe_extract(archive, root / "extract")
            manifest = verify_release_tree(extracted)
            self.assertEqual(manifest["version"], "0.1.0-rc.5")
            self.assertEqual((extracted / "release" / "VERSION").read_text(encoding="utf-8").strip(), "0.1.0-rc.5")
            plugin = json.loads((extracted / "plugins" / "nexus-desktop" / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
            self.assertEqual(plugin["version"], "0.1.0-rc.5")
            self.assertIn('candidate = f"./.codex/plugins/{PLUGIN_NAME}"', (extracted / "scripts" / "desktop_marketplace.py").read_text(encoding="utf-8"))

    def test_clean_install_reinstall_rollback_and_uninstall_need_no_repository(self) -> None:
        runtime = Path(sys.executable).resolve()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive, output = self.build_candidate(root)
            release = safe_extract(archive, output / "clean machine install")
            project = root / "project with spaces"
            project.mkdir()
            data = root / "machine local state"
            args = type("Args", (), {"data_root": str(data), "workspace_root": str(project), "workspace_id": "nexus-default", "mode": "standalone", "migrate_standalone": False, "remove_runtime": False, "codex_command": "codex"})()
            with patch.object(release_install, "verify_release_tree", return_value={"version": "0.1.0-rc.2"}), patch.object(release_install, "bundled_runtime", return_value=runtime), patch.object(release_install, "configure"):
                self.assertEqual(release_install.install(args), 0)
                self.assertTrue((data / "github-release-state.json").is_file())
                self.assertEqual(release_install.uninstall(args, rollback=True), 0)
                self.assertEqual(release_install.install(args), 0)
                self.assertEqual(release_install.uninstall(args), 0)
            self.assertFalse((data / "nexus-desktop-plugin.json").exists())

    def test_plugin_mode_requires_no_codex_cli_and_prepares_personal_marketplace(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = root / "local data"
            project = root / "project"
            project.mkdir()
            profile = root / "fresh user"
            profile.mkdir()
            args = type("Args", (), {
                "data_root": str(data), "workspace_root": str(project), "workspace_id": "nexus-default",
                "mode": "plugin", "migrate_standalone": False, "remove_runtime": False,
            })()
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout), patch.object(release_install, "verify_release_tree", return_value={"version": "0.1.0-rc.4"}), patch.object(release_install, "bundled_runtime", return_value=Path(sys.executable).resolve()), patch.object(release_install.desktop_marketplace, "install", return_value={"owner": "Nexus"}) as marketplace, patch.object(release_install, "configure"):
                self.assertEqual(release_install.install(args), 0)
            marketplace.assert_called_once()
            self.assertTrue((data / "github-release-state.json").is_file())
            self.assertIn("ChatGPT Desktop → Plugins → Personal → Nexus → + Install", stdout.getvalue())
            self.assertNotIn("verify @Nexus", stdout.getvalue())

    def test_release_lifecycle_uses_utf8_for_the_host_managed_action(self) -> None:
        class ReconfigurableStream:
            def __init__(self) -> None:
                self.calls: list[dict[str, str]] = []

            def reconfigure(self, **kwargs: str) -> None:
                self.calls.append(kwargs)

        stream = ReconfigurableStream()
        with patch.object(release_install.sys, "stdout", stream):
            release_install._configure_utf8_stdout()
        self.assertEqual(stream.calls, [{"encoding": "utf-8", "errors": "backslashreplace"}])

    def test_windows_bootstrap_constructs_the_host_action_without_non_ascii_source(self) -> None:
        """Windows PowerShell 5.1 must not misdecode a UTF-8 arrow literal."""
        source = (ROOT / "scripts" / "Install-Nexus.ps1").read_bytes()
        self.assertNotIn("→".encode("utf-8"), source)
        self.assertIn(b"$NexusArrow = [char]0x2192", source)

    def test_same_plugin_release_upgrade_retains_the_original_rollback_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = root / "local data"
            project = root / "project"
            project.mkdir()
            args = type("Args", (), {
                "data_root": str(data), "workspace_root": str(project), "workspace_id": "nexus-default",
                "mode": "plugin", "migrate_standalone": False, "remove_runtime": False,
            })()
            initial = {
                "schema_version": release_install.STATE_SCHEMA,
                "version": "0.1.0-rc.6",
                "release_root": str(release_install.ROOT.resolve()),
                "mode": "plugin",
                "marketplace": {"owner": "Nexus"},
                "previous_install": None,
                "previous_files": {"config": None, "workspaces": None},
            }
            release_install.atomic_json_write(release_install.state_path(data), initial)
            with patch.object(release_install, "verify_release_tree", return_value={"version": "0.1.0-rc.6"}), patch.object(release_install, "bundled_runtime", return_value=Path(sys.executable).resolve()), patch.object(release_install.desktop_marketplace, "install", return_value={"owner": "Nexus"}), patch.object(release_install, "configure"):
                self.assertEqual(release_install.install(args), 0)
            refreshed = release_install.current_install(data)
            self.assertIsNotNone(refreshed)
            self.assertIsNone(refreshed["previous_install"])
            self.assertEqual(refreshed["previous_files"], {"config": None, "workspaces": None})

    def test_marketplace_adapter_stops_before_host_managed_install_state(self) -> None:
        """The installer may create a source, never Desktop cache/config state."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            profile = root / "fresh standard user"
            profile.mkdir()
            release = root / "release"
            plugin = release / "plugins" / "nexus-desktop"
            (plugin / "scripts").mkdir(parents=True)
            (plugin / "skills" / "nexus").mkdir(parents=True)
            (plugin / ".mcp.json").write_text(json.dumps({"mcpServers": {"nexus_desktop_local": {}}}), encoding="utf-8")
            (plugin / "scripts" / "launch_nexus_mcp.py").write_text("# bridge\n", encoding="utf-8")
            (plugin / "skills" / "nexus" / "SKILL.md").write_text("---\nname: nexus\ndescription: test\n---\n", encoding="utf-8")
            runtime = release / "runtime" / "python" / "python.exe"
            runtime.parent.mkdir(parents=True)
            shutil.copy2(sys.executable, runtime)
            config = profile / ".codex" / "config.toml"
            cache = profile / ".codex" / "plugins" / "cache" / "host-owned" / "nexus-desktop"
            config.parent.mkdir(parents=True)
            config_before = b"[host]\nenabled = true\n"
            config.write_bytes(config_before)
            cache.mkdir(parents=True)
            cache_marker = cache / "host-state.txt"
            cache_marker.write_text("host-owned", encoding="utf-8")

            desktop_marketplace.install(release, "0.1.0-rc.6", runtime, release, profile)
            source = profile / ".codex" / "plugins" / "nexus-desktop"
            self.assertTrue(source.is_dir())
            self.assertEqual(config.read_bytes(), config_before)
            self.assertEqual(cache_marker.read_text(encoding="utf-8"), "host-owned")
            desktop_marketplace.uninstall(profile)
            self.assertFalse(source.exists())
            self.assertEqual(config.read_bytes(), config_before)
            self.assertEqual(cache_marker.read_text(encoding="utf-8"), "host-owned")

    def test_marketplace_adapter_preserves_unrelated_entries_and_rolls_back_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            profile = root / "fresh profile"
            profile.mkdir()
            release = root / "release with spaces"
            plugin = release / "plugins" / "nexus-desktop"
            (plugin / "scripts").mkdir(parents=True)
            (plugin / ".codex-plugin").mkdir()
            (plugin / "skills" / "nexus").mkdir(parents=True)
            (plugin / ".mcp.json").write_text(json.dumps({"mcpServers": {"nexus_desktop_local": {"command": "python", "args": ["./scripts/launch_nexus_mcp.py"], "cwd": "."}}}), encoding="utf-8")
            (plugin / "scripts" / "launch_nexus_mcp.py").write_text("# bridge\n", encoding="utf-8")
            (plugin / "skills" / "nexus" / "SKILL.md").write_text("---\nname: nexus\ndescription: test\n---\n", encoding="utf-8")
            runtime = release / "runtime" / "python" / "python.exe"
            runtime.parent.mkdir(parents=True)
            shutil.copy2(sys.executable, runtime)
            manifest = profile / ".agents" / "plugins" / "marketplace.json"
            manifest.parent.mkdir(parents=True)
            before = b'{"name":"Personal","plugins":[{"name":"other","source":{"source":"local","path":"./other"}}]}\n'
            manifest.write_bytes(before)
            state = desktop_marketplace.install(release, "0.1.0-rc.4", runtime, release, profile)
            payload = json.loads(manifest.read_text(encoding="utf-8"))
            self.assertEqual([item["name"] for item in payload["plugins"]], ["other", "nexus-desktop"])
            self.assertEqual(payload["plugins"][-1]["policy"]["installation"], "AVAILABLE")
            # The installer prepares the official source only. Desktop's
            # cache/config and enabled state remain host-managed.
            self.assertEqual(payload["plugins"][-1]["source"]["path"], "./.codex/plugins/nexus-desktop")
            source = profile / ".codex" / "plugins" / "nexus-desktop"
            staged = json.loads((source / ".mcp.json").read_text(encoding="utf-8"))
            self.assertEqual(staged["mcpServers"]["nexus_desktop_local"]["command"], str(runtime.resolve()))
            self.assertEqual(staged["mcpServers"]["nexus_desktop_local"]["env"], {"NEXUS_DATA_ROOT": str(release.resolve())})
            self.assertTrue((source / "skills" / "nexus" / "SKILL.md").is_file())
            self.assertNotIn('"command": "codex"', manifest.read_text(encoding="utf-8").lower())
            self.assertEqual(desktop_marketplace.install(release, "0.1.0-rc.4", runtime, release, profile)["version"], state["version"])
            desktop_marketplace.uninstall(profile, rollback=True)
            self.assertEqual(manifest.read_bytes(), before)
            self.assertFalse(source.exists())

    def test_marketplace_adapter_rejects_malformed_or_unmanaged_conflicting_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = Path(temporary)
            profile.mkdir(exist_ok=True)
            manifest = profile / ".agents" / "plugins" / "marketplace.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text("not-json", encoding="utf-8")
            with self.assertRaisesRegex(ReleaseError, "personal marketplace manifest is invalid"):
                desktop_marketplace.install(profile, "0.1.0-rc.4", Path(sys.executable), profile, profile)
            self.assertFalse((profile / ".agents" / "plugins" / "nexus-marketplace").exists())
            manifest.write_text(json.dumps({"name": "Personal", "plugins": [{"name": "nexus-desktop", "source": {"source": "local", "path": "./other"}}]}), encoding="utf-8")
            with self.assertRaisesRegex(ReleaseError, "unmanaged Nexus marketplace entry"):
                desktop_marketplace.install(profile, "0.1.0-rc.4", Path(sys.executable), profile, profile)

    def test_rc5_marketplace_layout_migrates_to_official_source_root_and_rolls_back(self) -> None:
        """The obsolete RC5 source migrates without touching host state."""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            profile = root / "fresh profile"
            profile.mkdir()
            release = root / "release"
            source = release / "plugins" / "nexus-desktop"
            (source / "scripts").mkdir(parents=True)
            (source / "skills" / "nexus").mkdir(parents=True)
            (source / ".mcp.json").write_text(json.dumps({"mcpServers": {"nexus_desktop_local": {}}}), encoding="utf-8")
            (source / "scripts" / "launch_nexus_mcp.py").write_text("# bridge\n", encoding="utf-8")
            (source / "skills" / "nexus" / "SKILL.md").write_text("---\nname: nexus\ndescription: test\n---\n", encoding="utf-8")
            runtime = release / "runtime" / "python" / "python.exe"
            runtime.parent.mkdir(parents=True)
            shutil.copy2(sys.executable, runtime)
            marketplace, managed, state_path = desktop_marketplace.paths(profile)
            legacy = profile / "plugins" / "nexus-desktop"
            shutil.copytree(source, legacy)
            legacy_entry = {
                "name": "nexus-desktop",
                "source": {"source": "local", "path": "./plugins/nexus-desktop"},
                "policy": {"installation": "INSTALLED_BY_DEFAULT", "authentication": "ON_INSTALL"},
                "category": "Developer tools",
            }
            marketplace.write_text(json.dumps({"name": "personal", "plugins": [legacy_entry]}), encoding="utf-8")
            before = managed / "backups" / "legacy.b64"
            before.parent.mkdir(parents=True)
            before.write_bytes(base64.b64encode(marketplace.read_bytes()) + b"\n")
            (legacy / ".nexus-marketplace-owner.json").write_text(json.dumps({
                "schema_version": desktop_marketplace.STATE_SCHEMA, "owner": "Nexus", "version": "0.1.0-rc.5",
            }), encoding="utf-8")
            state_path.write_text(json.dumps({
                "schema_version": desktop_marketplace.STATE_SCHEMA, "owner": "Nexus", "version": "0.1.0-rc.5",
                "marketplace_path": str(marketplace), "plugin_root": str(legacy), "marketplace_before": str(before),
                "marketplace_after_sha256": hashlib.sha256(marketplace.read_bytes()).hexdigest(), "entry": legacy_entry,
                "previous_state": None,
            }), encoding="utf-8")

            state = desktop_marketplace.install(release, "0.1.0-rc.6", runtime, release, profile)
            entry = json.loads(marketplace.read_text(encoding="utf-8"))["plugins"][0]
            canonical = profile / ".codex" / "plugins" / "nexus-desktop"
            self.assertEqual(entry["source"]["path"], "./.codex/plugins/nexus-desktop")
            self.assertTrue(desktop_marketplace._same_path(Path(state["plugin_root"]), canonical))
            self.assertTrue((canonical / "skills" / "nexus" / "SKILL.md").is_file())
            self.assertTrue(legacy.is_dir())

            desktop_marketplace.uninstall(profile, rollback=True)
            self.assertEqual(marketplace.read_text(encoding="utf-8"), json.dumps({"name": "personal", "plugins": [legacy_entry]}))
            self.assertFalse(canonical.exists())
            self.assertTrue(legacy.is_dir())

            # A non-rollback uninstall has no reason to retain the temporary
            # RC4 source.  It must not leave a stale Nexus plugin tree behind.
            desktop_marketplace.install(release, "0.1.0-rc.6", runtime, release, profile)
            desktop_marketplace.uninstall(profile)
            self.assertFalse(canonical.exists())
            self.assertFalse(legacy.exists())

    def test_official_source_upgrade_rollback_restores_the_retained_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            profile = root / "profile"
            profile.mkdir()
            release = root / "release"
            source = release / "plugins" / "nexus-desktop"
            (source / "scripts").mkdir(parents=True)
            (source / "skills" / "nexus").mkdir(parents=True)
            (source / ".mcp.json").write_text(json.dumps({"mcpServers": {"nexus_desktop_local": {}}}), encoding="utf-8")
            (source / "scripts" / "launch_nexus_mcp.py").write_text("# bridge\n", encoding="utf-8")
            (source / "skills" / "nexus" / "SKILL.md").write_text("---\nname: nexus\ndescription: test\n---\n", encoding="utf-8")
            runtime = release / "runtime" / "python" / "python.exe"
            runtime.parent.mkdir(parents=True)
            shutil.copy2(sys.executable, runtime)

            desktop_marketplace.install(release, "0.1.0-rc.6", runtime, release, profile)
            canonical = profile / ".codex" / "plugins" / "nexus-desktop"
            marker = json.loads((canonical / ".nexus-marketplace-owner.json").read_text(encoding="utf-8"))
            self.assertEqual(marker["version"], "0.1.0-rc.6")
            desktop_marketplace.install(release, "0.1.0-rc.7", runtime, release, profile)
            marker = json.loads((canonical / ".nexus-marketplace-owner.json").read_text(encoding="utf-8"))
            self.assertEqual(marker["version"], "0.1.0-rc.7")

            desktop_marketplace.uninstall(profile, rollback=True)
            marker = json.loads((canonical / ".nexus-marketplace-owner.json").read_text(encoding="utf-8"))
            self.assertEqual(marker["version"], "0.1.0-rc.6")
            self.assertFalse((profile / ".agents" / "plugins" / "nexus-marketplace" / "retired").exists())

    def test_marketplace_uninstall_preserves_new_unrelated_entry_and_rejects_escaped_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            profile = root / "profile"
            profile.mkdir()
            release = root / "release"
            plugin = release / "plugins" / "nexus-desktop"
            (plugin / "scripts").mkdir(parents=True)
            (plugin / ".codex-plugin").mkdir()
            (plugin / ".mcp.json").write_text(json.dumps({"mcpServers": {"nexus_desktop_local": {}}}), encoding="utf-8")
            runtime = release / "runtime" / "python" / "python.exe"
            runtime.parent.mkdir(parents=True)
            shutil.copy2(sys.executable, runtime)
            desktop_marketplace.install(release, "0.1.0-rc.4", runtime, release, profile)
            marketplace = profile / ".agents" / "plugins" / "marketplace.json"
            payload = json.loads(marketplace.read_text(encoding="utf-8"))
            payload["plugins"].append({"name": "later-user-plugin", "source": {"source": "local", "path": "./later"}})
            marketplace.write_text(json.dumps(payload), encoding="utf-8")
            desktop_marketplace.uninstall(profile)
            self.assertEqual([item["name"] for item in json.loads(marketplace.read_text(encoding="utf-8"))["plugins"]], ["later-user-plugin"])
            # A forged ownership record must not turn cleanup into a recursive
            # delete outside Nexus' personal-marketplace namespace.
            _, managed, state_path = desktop_marketplace.paths(profile)
            forged_entry = {"name": "nexus-desktop"}
            payload = json.loads(marketplace.read_text(encoding="utf-8"))
            payload["plugins"].append(forged_entry)
            marketplace.write_text(json.dumps(payload), encoding="utf-8")
            before_forged_cleanup = marketplace.read_bytes()
            state_path.write_text(json.dumps({
                "schema_version": desktop_marketplace.STATE_SCHEMA, "owner": "Nexus", "version": "x",
                "marketplace_path": str(marketplace), "plugin_root": str(root), "marketplace_before": str(managed / "missing"),
                "marketplace_after_sha256": "0" * 64, "entry": forged_entry, "previous_state": None,
            }), encoding="utf-8")
            with self.assertRaisesRegex(ReleaseError, "escapes its owned directory"):
                desktop_marketplace.uninstall(profile)
            self.assertEqual(marketplace.read_bytes(), before_forged_cleanup)

    def test_pinned_embedded_runtime_rejects_substitution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            wheelhouse = root / "wheels"
            wheelhouse.mkdir()
            write_test_wheel(wheelhouse)
            embed, spec = write_test_embed(root)
            spec["sha256"] = "0" * 64
            with patch.object(release_build, "runtime_spec", return_value=spec):
                with self.assertRaises(ReleaseError):
                    release_build.build(root / "out", "0.1.0-rc.2", wheelhouse, embed)

    @unittest.skipUnless(os.environ.get("NEXUS_RELEASE_TEST_EMBED") and os.environ.get("NEXUS_RELEASE_TEST_WHEELHOUSE"), "real embedded runtime inputs are not configured")
    def test_real_clean_bootstrap_without_system_python(self) -> None:
        """Actual acceptance path: archive runtime succeeds while PATH has no Python."""
        embed = Path(os.environ["NEXUS_RELEASE_TEST_EMBED"])
        wheelhouse = Path(os.environ["NEXUS_RELEASE_TEST_WHEELHOUSE"])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "release output"
            archive, _ = release_build.build(output, "0.1.0-rc.2", wheelhouse, embed)
            project = root / "workspace"
            project.mkdir()
            data = root / "Nexus local data"
            bootstrap = output / "Install-Nexus-0.1.0-rc.2.ps1"
            powershell = shutil.which("powershell") or shutil.which("pwsh")
            self.assertIsNotNone(powershell)
            environment = dict(os.environ)
            # Keep Windows' normal process variables (for a standard-user host),
            # but make python.exe/py.exe unavailable. This is not a mock: the
            # only executable that can run the release is the bundled runtime.
            environment["PATH"] = os.pathsep.join((str(Path(powershell).parent), str(Path(os.environ["SystemRoot"]) / "System32")))
            environment["LOCALAPPDATA"] = str(root / "LocalAppData")
            environment["PSModulePath"] = str(Path(os.environ["SystemRoot"]) / "System32" / "WindowsPowerShell" / "v1.0" / "Modules")
            environment["SystemDrive"] = Path(os.environ["SystemRoot"]).anchor
            for key in tuple(environment):
                if key.upper().startswith("PYTHON"):
                    environment.pop(key)
            result = subprocess.run([
                powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(bootstrap),
                "-ArchivePath", str(archive), "-ChecksumPath", str(archive.with_suffix(".zip.sha256")),
                "-WorkspaceRoot", str(project), "-DataRoot", str(data), "-Mode", "standalone",
            ], capture_output=True, text=True, encoding="utf-8", errors="strict", env=environment, timeout=60)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            release = next((data / "releases").iterdir())
            runtime = release / "runtime" / "python" / "python.exe"
            self.assertTrue(runtime.is_file())
            self.assertTrue((data / "nexus-desktop-plugin.json").is_file())
            self.assertEqual(subprocess.run([str(runtime), "-I", "-B", str(release / "scripts" / "release_install.py"), "--data-root", str(data), "verify"], capture_output=True, text=True).returncode, 0)
            # Exercise the real R2 local MCP server through the embedded client
            # and embedded server. PATH still contains no usable Python, so this
            # proves health/discover/plan/inventory do not silently fall back to a host
            # interpreter after installation.
            probe = f"""
import asyncio
import json
from uuid import uuid4
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params = StdioServerParameters(
        command={str(runtime)!r},
        args=[{str(release / 'scripts' / 'nexus_mcp.py')!r}, '--workspace-config', {str(data / 'workspaces.json')!r}],
        cwd={str(release)!r},
    )
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            health = await session.call_tool('nexus.health', {{}})
            discover = await session.call_tool('nexus.discover_capabilities', {{}})
            plan = await session.call_tool('nexus.plan_task', {{
                'workspace_id': 'nexus-default',
                'task': 'Plan a safe release check',
                'constraints': [],
            }})
            ticket_result = await session.call_tool('nexus.begin_host_capability_assessment', {{
                'schema_version': 'nexus.host-capability-ticket-request.v1',
                'host_surface': 'chatgpt_desktop',
                'inventory_scope': 'current_turn_host_visible_subset',
                'inventory_completeness': 'not_globally_enumerated',
                'task_category': 'presentation',
                'required_interfaces': ['editable_pptx_create', 'pptx_open_render_validate'],
            }})
            ticket = json.loads(ticket_result.content[0].text)
            inventory = {{
                'schema_version': 'nexus.host-capability-snapshot.v3',
                'ticket_id': ticket['ticket_id'],
                'snapshot_id': str(uuid4()),
                'capabilities': [{{
                    'capability_id': 'presentations',
                    'provider_id': 'openai-primary-runtime',
                    'display_name': 'Presentations',
                    'resource_kind': 'skill',
                    'availability': 'skill_workflow_ready_current_turn',
                    'evidence': ['current_turn_skill_metadata', 'current_turn_skill_instructions', 'current_turn_tool_catalog', 'current_turn_execution_substrate'],
                    'interfaces': ['editable_pptx_create', 'pptx_open_render_validate'],
                    'logical_capability': 'chatgpt.presentations',
                    'execution_binding_kind': 'host_skill_workflow',
                }}],
            }}
            assessment = await session.call_tool('nexus.assess_host_capabilities', inventory)
            replay = await session.call_tool('nexus.assess_host_capabilities', inventory)
            assert not health.is_error, health.content
            assert not discover.is_error, discover.content
            assert not plan.is_error, plan.content
            assert not ticket_result.is_error, ticket_result.content
            assert not assessment.is_error, assessment.content
            assert replay.is_error, replay.content
            assert json.loads(replay.content[0].text)['error']['code'] == 'HOST_INVENTORY_TICKET_REPLAYED'

asyncio.run(main())
"""
            mcp_result = subprocess.run(
                [str(runtime), "-I", "-B", "-c", probe],
                capture_output=True,
                text=True,
                timeout=45,
                env=environment,
            )
            self.assertEqual(mcp_result.returncode, 0, mcp_result.stderr + mcp_result.stdout)

    @unittest.skipUnless(os.environ.get("NEXUS_RELEASE_TEST_EMBED") and os.environ.get("NEXUS_RELEASE_TEST_WHEELHOUSE"), "real embedded runtime inputs are not configured")
    def test_real_plugin_bootstrap_without_codex_prepares_host_managed_source(self) -> None:
        """RC6 has neither host CLI nor system Python nor host-state writes."""
        embed = Path(os.environ["NEXUS_RELEASE_TEST_EMBED"])
        wheelhouse = Path(os.environ["NEXUS_RELEASE_TEST_WHEELHOUSE"])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "release output"
            archive, _ = release_build.build(output, "0.1.0-rc.6", wheelhouse, embed)
            project = root / "workspace"
            project.mkdir()
            data = root / "Nexus local data"
            powershell = shutil.which("powershell") or shutil.which("pwsh")
            self.assertIsNotNone(powershell)
            environment = dict(os.environ)
            environment["PATH"] = os.pathsep.join((str(Path(powershell).parent), str(Path(os.environ["SystemRoot"]) / "System32")))
            environment["LOCALAPPDATA"] = str(root / "LocalAppData")
            environment["USERPROFILE"] = str(root / "Fresh Standard User")
            environment["HOME"] = environment["USERPROFILE"]
            environment["PSModulePath"] = str(Path(os.environ["SystemRoot"]) / "System32" / "WindowsPowerShell" / "v1.0" / "Modules")
            environment["SystemDrive"] = Path(os.environ["SystemRoot"]).anchor
            for key in tuple(environment):
                if key.upper().startswith("PYTHON"):
                    environment.pop(key)
            result = subprocess.run([
                powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(output / "Install-Nexus-0.1.0-rc.6.ps1"),
                "-ArchivePath", str(archive), "-ChecksumPath", str(archive.with_suffix(".zip.sha256")),
                "-WorkspaceRoot", str(project), "-DataRoot", str(data), "-Mode", "plugin",
            ], capture_output=True, text=True, encoding="utf-8", errors="strict", env=environment, timeout=60)
            output_text = result.stdout + result.stderr
            self.assertEqual(result.returncode, 0, output_text)
            self.assertNotIn("[WinError 2]", output_text)
            self.assertIn("ChatGPT Desktop → Plugins → Personal → Nexus → + Install", output_text)
            self.assertTrue((data / "github-release-state.json").exists())
            marketplace = Path(environment["USERPROFILE"]) / ".agents" / "plugins" / "marketplace.json"
            payload = json.loads(marketplace.read_text(encoding="utf-8"))
            entry = next(item for item in payload["plugins"] if item["name"] == "nexus-desktop")
            self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
            self.assertEqual(entry["source"]["path"], "./.codex/plugins/nexus-desktop")
            release = next((data / "releases").iterdir())
            staged = Path(environment["USERPROFILE"]) / ".codex" / "plugins" / "nexus-desktop" / ".mcp.json"
            staged_server = json.loads(staged.read_text(encoding="utf-8"))["mcpServers"]["nexus_desktop_local"]
            self.assertEqual(staged_server["command"], str((release / "runtime" / "python" / "python.exe").resolve()))
            self.assertEqual(staged_server["env"], {"NEXUS_DATA_ROOT": str(data.resolve())})
            self.assertFalse((Path(environment["USERPROFILE"]) / ".codex" / "plugins" / "cache").exists())
            self.assertFalse((Path(environment["USERPROFILE"]) / ".codex" / "config.toml").exists())

    @unittest.skipUnless(
        os.environ.get("NEXUS_RELEASE_TEST_EMBED")
        and os.environ.get("NEXUS_RELEASE_TEST_WHEELHOUSE"),
        "real embedded runtime inputs are not configured",
    )
    def test_real_plugin_health_without_system_python_or_codex(self) -> None:
        """The registered plugin bridge and MCP server work with only RC files."""
        embed = Path(os.environ["NEXUS_RELEASE_TEST_EMBED"])
        wheelhouse = Path(os.environ["NEXUS_RELEASE_TEST_WHEELHOUSE"])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "release output"
            archive, _ = release_build.build(output, "0.1.0-rc.6", wheelhouse, embed)
            project = root / "workspace"
            project.mkdir()
            data = root / "Nexus local data"
            powershell = shutil.which("powershell") or shutil.which("pwsh")
            self.assertIsNotNone(powershell)
            environment = dict(os.environ)
            # Retain only host dependencies from the current process PATH; no
            # Python directory is available to the bootstrap or plugin launcher.
            environment["PATH"] = os.pathsep.join(item for item in environment.get("PATH", "").split(os.pathsep) if "python" not in item.casefold())
            environment["LOCALAPPDATA"] = str(root / "LocalAppData")
            environment["USERPROFILE"] = str(root / "Fresh Standard User")
            environment["HOME"] = environment["USERPROFILE"]
            environment["PSModulePath"] = str(Path(os.environ["SystemRoot"]) / "System32" / "WindowsPowerShell" / "v1.0" / "Modules")
            environment["SystemDrive"] = Path(os.environ["SystemRoot"]).anchor
            for key in tuple(environment):
                if key.upper().startswith("PYTHON"):
                    environment.pop(key)
            result = subprocess.run([
                powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(output / "Install-Nexus-0.1.0-rc.6.ps1"),
                "-ArchivePath", str(archive), "-ChecksumPath", str(archive.with_suffix(".zip.sha256")),
                "-WorkspaceRoot", str(project), "-DataRoot", str(data), "-Mode", "plugin",
            ], capture_output=True, text=True, encoding="utf-8", errors="strict", env=environment, timeout=90)
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            release = next((data / "releases").iterdir())
            runtime = release / "runtime" / "python" / "python.exe"
            probe = """
import asyncio
import json
from pathlib import Path
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    plugin = PLUGIN
    server = json.loads((plugin / '.mcp.json').read_text(encoding='utf-8'))['mcpServers']['nexus_desktop_local']
    params = StdioServerParameters(command=server['command'], args=[str(plugin / 'scripts' / 'launch_nexus_mcp.py')], cwd=str(plugin), env=server['env'])
    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            assert not (await session.call_tool('nexus.health', {})).is_error
            assert not (await session.call_tool('nexus.discover_capabilities', {})).is_error
            assert not (await session.call_tool('nexus.plan_task', {'workspace_id': 'nexus-default', 'task': 'Plan a safe release check', 'constraints': []})).is_error
            begun = await session.call_tool('nexus.begin_host_capability_assessment', {
                'schema_version': 'nexus.host-capability-ticket-request.v1',
                'host_surface': 'chatgpt_desktop',
                'inventory_scope': 'current_turn_host_visible_subset',
                'inventory_completeness': 'not_globally_enumerated',
                'task_category': 'presentation',
                'required_interfaces': ['editable_pptx_create', 'pptx_open_render_validate'],
            })
            assert not begun.is_error
            ticket = json.loads(begun.content[0].text)
            inventory = {
                'schema_version': 'nexus.host-capability-snapshot.v3',
                'ticket_id': ticket['ticket_id'],
                'snapshot_id': '6f6bb973-bb39-4ad4-a48d-76290c827f93',
                'capabilities': [{
                    'capability_id': 'presentations',
                    'provider_id': 'openai-primary-runtime',
                    'display_name': 'Presentations',
                    'resource_kind': 'skill',
                    'availability': 'skill_workflow_ready_current_turn',
                    'evidence': ['current_turn_skill_metadata', 'current_turn_skill_instructions', 'current_turn_tool_catalog', 'current_turn_execution_substrate'],
                    'interfaces': ['editable_pptx_create', 'pptx_open_render_validate'],
                    'logical_capability': 'chatgpt.presentations',
                    'execution_binding_kind': 'host_skill_workflow',
                }],
            }
            assessed = await session.call_tool('nexus.assess_host_capabilities', inventory)
            assert not assessed.is_error
            assessment = json.loads(assessed.content[0].text)
            assert assessment['security_result']['code'] == 'HOST_CAPABILITY_SELECTION_READY'
            replay = await session.call_tool('nexus.assess_host_capabilities', inventory)
            assert replay.is_error
            assert 'HOST_INVENTORY_TICKET_REPLAYED' in replay.content[0].text

asyncio.run(main())
""".replace("PLUGIN", "Path(" + repr(str(Path(environment["USERPROFILE"]) / ".codex" / "plugins" / "nexus-desktop")) + ")")
            mcp_result = subprocess.run([str(runtime), "-I", "-B", "-c", probe], capture_output=True, text=True, env=environment, timeout=45)
            self.assertEqual(mcp_result.returncode, 0, mcp_result.stderr + mcp_result.stdout)
            cleanup = subprocess.run([str(runtime), "-I", "-B", str(release / "scripts" / "release_install.py"), "--data-root", str(data), "uninstall"], capture_output=True, text=True, env=environment, timeout=45)
            self.assertEqual(cleanup.returncode, 0, cleanup.stderr + cleanup.stdout)

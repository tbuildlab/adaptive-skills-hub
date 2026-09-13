from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tests._windows_junction import create_junction

from ash.ecosystem_models import (
    ID_DOMAINS,
    EcosystemError,
    GENESIS_STATE,
    IMPLICIT_STATE,
    StateVector,
    build_component_identity,
    build_component_revision_identity,
    build_revision_identity,
    build_state_record,
    build_transition_receipt,
    build_tree,
    canonical_sha256,
    domain_sha256,
    normalize_candidate_path,
    parse_state_vector,
    parse_json_bytes,
    source_identity,
    typed_id,
    validate_state_record,
    validate_transition_receipt,
    validate_typed_id,
    zero_authority,
)
import ash.ecosystem_policy as policy_module
from ash.ecosystem_policy import (
    TrustedEcosystemSourcePolicy,
    _load_test_source_policy as load_trusted_source_policy,
    parse_source_policy_bytes,
)


ROOT = Path(__file__).resolve().parents[1]
POLICY_RAW = (ROOT / "config" / "ecosystem-source-policy.json").read_bytes()
FROZEN_STATIC_PROFILE_SHA256 = "8414bb099dacd82bb30886cb79b3cd927051f2930be6af176f8c909a2cd4bdf9"
FROZEN_CLASSIFIER_PROFILE_SHA256 = "e41da303f8f22fc0c11efda9d58206a4644854399dfc51354f5df7a3c56bf5f0"
FROZEN_STATIC_RULE_IDS = (
    "archive.nested",
    "automation.workflow",
    "binary.executable-magic",
    "content.bidi-control",
    "content.invalid-role-text",
    "credential.content",
    "credential.filename",
    "dependency.manifest",
    "evidence.license-incomplete",
    "evidence.provenance-inexact",
    "hook.git-control",
    "install.declaration",
    "instruction.control-claim",
    "mode.executable",
    "network.declaration",
    "permission.declaration",
)
FROZEN_CLASSIFIER_RULE_IDS = (
    "component.skill-directory",
    "component.advisory-agent",
    "component.memory-pattern",
    "component.workflow-pattern",
    "component.dependency-reference",
    "component.reference-architecture",
)
FROZEN_STATIC_RULE_FIELDS = {
    "rule_id",
    "rule_version",
    "predicate_id",
    "parameters",
    "category",
    "severity",
    "disposition",
}
FROZEN_CLASSIFIER_RULE_FIELDS = {
    "rule_id",
    "rule_version",
    "predicate_id",
    "parameters",
    "component_kind",
}


def temporary_policy_root(raw: bytes = POLICY_RAW, *, digest_override: str | None = None):
    temporary = tempfile.TemporaryDirectory()
    root = Path(temporary.name)
    (root / "config").mkdir()
    (root / "config" / "ecosystem-source-policy.json").write_bytes(raw)
    normalized = raw.decode("utf-8").replace("\r\n", "\n").encode("utf-8")
    manifest = {
        "config/ecosystem-source-policy.json": {
            "bytes": len(normalized),
            "sha256": digest_override or hashlib.sha256(normalized).hexdigest(),
        }
    }
    (root / "MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    return temporary, root


class EcosystemPolicyTests(unittest.TestCase):
    def test_manifest_bound_policy_loads_with_all_eight_identity_only_sources(self) -> None:
        temporary, root = temporary_policy_root()
        with temporary:
            trusted = load_trusted_source_policy(root=root)
            policy = trusted.to_dict()
            self.assertEqual(len(policy["sources"]), 8)
            self.assertEqual(len(policy["evaluation_profiles"]), 7)
            self.assertEqual(
                trusted.static_analyzer_config_sha256, FROZEN_STATIC_PROFILE_SHA256
            )
            self.assertEqual(
                trusted.component_classifier_config_sha256,
                FROZEN_CLASSIFIER_PROFILE_SHA256,
            )
            for source in policy["sources"]:
                self.assertEqual(source["identity_state"], "SOURCE_IDENTITY_ONLY")
                self.assertEqual(source["authority"], zero_authority())

    def test_parsing_alone_cannot_manufacture_trusted_authority(self) -> None:
        parsed = parse_source_policy_bytes(POLICY_RAW)
        self.assertIs(type(parsed), dict)
        with self.assertRaises(EcosystemError) as raised:
            policy_module._require_trusted_source_policy(parsed)
        self.assertEqual(raised.exception.reason_code, "POLICY_UNTRUSTED")
        with self.assertRaises(EcosystemError):
            TrustedEcosystemSourcePolicy(
                parsed,
                token=object(),
                integrity_manifest_sha256="0" * 64,
                trust_mode="production",
                repository_root=ROOT,
            )

    def test_production_policy_loader_is_root_closed_and_baseline_bound(self) -> None:
        temporary, root = temporary_policy_root()
        with temporary:
            hermetic = load_trusted_source_policy(root=root)
            with self.assertRaises(TypeError):
                policy_module.load_trusted_source_policy(root=root)  # type: ignore[call-arg]
            with self.assertRaises(EcosystemError) as raised:
                policy_module._require_production_source_policy(hermetic)
            self.assertEqual(raised.exception.reason_code, "POLICY_UNTRUSTED")

        production = policy_module.load_trusted_source_policy()
        self.assertIs(
            policy_module._require_production_source_policy(production), production
        )

    def test_manifest_failure_never_returns_a_trusted_policy(self) -> None:
        temporary, root = temporary_policy_root(digest_override="0" * 64)
        with temporary, self.assertRaises(EcosystemError) as raised:
            load_trusted_source_policy(root=root)
        self.assertEqual(raised.exception.reason_code, "POLICY_INTEGRITY_INVALID")

    def test_repository_root_link_cannot_issue_a_policy_seal(self) -> None:
        temporary, real_root = temporary_policy_root()
        with temporary, tempfile.TemporaryDirectory() as alias_parent:
            alias = Path(alias_parent) / "linked-root"
            if os.name == "nt":
                create_junction(alias, real_root)
            else:
                os.symlink(real_root, alias, target_is_directory=True)
            with self.assertRaises(EcosystemError) as raised:
                load_trusted_source_policy(root=alias)
            self.assertEqual(raised.exception.reason_code, "POLICY_INTEGRITY_INVALID")

    def test_unstable_policy_or_manifest_read_cannot_issue_a_seal(self) -> None:
        for unstable_name in ("MANIFEST.json", "ecosystem-source-policy.json"):
            temporary, root = temporary_policy_root()
            with self.subTest(unstable_name=unstable_name), temporary:
                original_reader = policy_module.stable_read_bytes

                def unstable_reader(path: Path, **kwargs: object) -> bytes:
                    if path.name == unstable_name:
                        raise EcosystemError("INPUT_UNSTABLE", "synthetic held-file mutation")
                    return original_reader(path, **kwargs)

                with patch.object(policy_module, "stable_read_bytes", side_effect=unstable_reader):
                    with self.assertRaises(EcosystemError) as raised:
                        load_trusted_source_policy(root=root)
                self.assertEqual(raised.exception.reason_code, "POLICY_INTEGRITY_INVALID")

    def test_manifest_policy_presence_size_and_reparse_matrix_fails_before_seal(self) -> None:
        mutations = {
            "manifest-missing": lambda root: (root / "MANIFEST.json").unlink(),
            "policy-file-missing": lambda root: (
                root / "config" / "ecosystem-source-policy.json"
            ).unlink(),
            "policy-entry-missing": lambda root: (root / "MANIFEST.json").write_text(
                json.dumps({"README.md": {"bytes": 0, "sha256": hashlib.sha256(b"").hexdigest()}}),
                encoding="utf-8",
            ),
            "well-typed-wrong-byte-count": lambda root: (root / "MANIFEST.json").write_text(
                json.dumps(
                    {
                        "config/ecosystem-source-policy.json": {
                            "bytes": len(POLICY_RAW) + 1,
                            "sha256": hashlib.sha256(POLICY_RAW).hexdigest(),
                        }
                    }
                ),
                encoding="utf-8",
            ),
        }
        for case, mutate in mutations.items():
            temporary, root = temporary_policy_root()
            with self.subTest(case=case), temporary:
                mutate(root)
                with self.assertRaises(EcosystemError) as raised:
                    load_trusted_source_policy(root=root)
                self.assertEqual(raised.exception.reason_code, "POLICY_INTEGRITY_INVALID")

        temporary, root = temporary_policy_root()
        with self.subTest(case="policy-symlink-or-reparse"), temporary:
            config = root / "config"
            real_config = root / "real-config"
            config.replace(real_config)
            if os.name == "nt":
                create_junction(config, real_config)
            else:
                os.symlink(real_config, config, target_is_directory=True)
            with self.assertRaises(EcosystemError) as raised:
                load_trusted_source_policy(root=root)
            self.assertEqual(raised.exception.reason_code, "POLICY_INTEGRITY_INVALID")

    def test_container_source_and_evaluation_profile_closure_matrix(self) -> None:
        class MappingSubclass(dict):
            pass

        class ListSubclass(list):
            pass

        canonical = json.loads(POLICY_RAW)
        container_cases = {
            "mapping-subclass-root": MappingSubclass(canonical),
            "list-subclass-sources": {
                **canonical,
                "sources": ListSubclass(canonical["sources"]),
            },
            "mapping-subclass-source": {
                **canonical,
                "sources": [MappingSubclass(item) for item in canonical["sources"]],
            },
        }
        for case, candidate in container_cases.items():
            with self.subTest(case=case), self.assertRaises(EcosystemError):
                policy_module.parse_untrusted_source_policy(candidate)

    def test_policy_schema_and_frozen_catalog_matrix_is_independently_closed(self) -> None:
        mutations = {
            "unknown-root-key": lambda value: value.__setitem__("unexpected", None),
            "unknown-provider-key": lambda value: value["provider_policy"].__setitem__(
                "unexpected", "disabled"
            ),
            "unknown-resource-key": lambda value: value["resource_limits"].__setitem__(
                "unexpected", 1
            ),
            "bool-for-integer-limit": lambda value: value["resource_limits"].__setitem__(
                "max_sources", True
            ),
            "unknown-analysis-key": lambda value: value["analysis_profiles"].__setitem__(
                "unexpected", {}
            ),
            "unknown-static-profile-key": lambda value: value["analysis_profiles"][
                "static_analyzer_profile"
            ].__setitem__("unexpected", None),
            "unknown-static-rule-key": lambda value: value["analysis_profiles"][
                "static_analyzer_profile"
            ]["rules"][0].__setitem__("unexpected", None),
            "unknown-static-parameter-key": lambda value: value["analysis_profiles"][
                "static_analyzer_profile"
            ]["rules"][0]["parameters"].__setitem__("unexpected", None),
            "missing-static-rule": lambda value: value["analysis_profiles"][
                "static_analyzer_profile"
            ]["rules"].pop(),
            "extra-static-rule": lambda value: value["analysis_profiles"][
                "static_analyzer_profile"
            ]["rules"].append(
                copy.deepcopy(value["analysis_profiles"]["static_analyzer_profile"]["rules"][-1])
            ),
            "duplicated-static-rule": lambda value: value["analysis_profiles"][
                "static_analyzer_profile"
            ]["rules"].__setitem__(
                1, copy.deepcopy(value["analysis_profiles"]["static_analyzer_profile"]["rules"][0])
            ),
            "mutated-static-rule": lambda value: value["analysis_profiles"][
                "static_analyzer_profile"
            ]["rules"][0].__setitem__("severity", "LOW"),
            "unknown-classifier-profile-key": lambda value: value["analysis_profiles"][
                "component_classifier_profile"
            ].__setitem__("unexpected", None),
            "unknown-classifier-rule-key": lambda value: value["analysis_profiles"][
                "component_classifier_profile"
            ]["rules"][0].__setitem__("unexpected", None),
            "unknown-classifier-parameter-key": lambda value: value["analysis_profiles"][
                "component_classifier_profile"
            ]["rules"][0]["parameters"].__setitem__("unexpected", None),
            "missing-classifier-rule": lambda value: value["analysis_profiles"][
                "component_classifier_profile"
            ]["rules"].pop(),
            "extra-classifier-rule": lambda value: value["analysis_profiles"][
                "component_classifier_profile"
            ]["rules"].append(
                copy.deepcopy(value["analysis_profiles"]["component_classifier_profile"]["rules"][-1])
            ),
            "duplicated-classifier-rule": lambda value: value["analysis_profiles"][
                "component_classifier_profile"
            ]["rules"].__setitem__(
                1,
                copy.deepcopy(
                    value["analysis_profiles"]["component_classifier_profile"]["rules"][0]
                ),
            ),
            "mutated-classifier-rule": lambda value: value["analysis_profiles"][
                "component_classifier_profile"
            ]["rules"][0].__setitem__("component_kind", "UNSUPPORTED"),
            "unknown-evaluation-profile-key": lambda value: value["evaluation_profiles"][
                0
            ].__setitem__("unexpected", None),
            "unknown-evaluation-check-key": lambda value: value["evaluation_profiles"][0][
                "required_checks"
            ][0].__setitem__("unexpected", None),
            "unknown-source-key": lambda value: value["sources"][0].__setitem__(
                "unexpected", None
            ),
            "unknown-frozen-evidence-key": lambda value: value["sources"][0][
                "frozen_evidence"
            ].__setitem__("unexpected", None),
        }
        for case, mutate in mutations.items():
            candidate = json.loads(POLICY_RAW)
            mutate(candidate)
            with self.subTest(case=case), self.assertRaises(EcosystemError):
                policy_module.parse_untrusted_source_policy(candidate)

        canonical = policy_module.parse_untrusted_source_policy(json.loads(POLICY_RAW))
        static = canonical["analysis_profiles"]["static_analyzer_profile"]
        classifier = canonical["analysis_profiles"]["component_classifier_profile"]
        self.assertEqual(tuple(item["rule_id"] for item in static["rules"]), FROZEN_STATIC_RULE_IDS)
        self.assertEqual(
            tuple(item["rule_id"] for item in classifier["rules"]),
            FROZEN_CLASSIFIER_RULE_IDS,
        )
        self.assertTrue(all(set(item) == FROZEN_STATIC_RULE_FIELDS for item in static["rules"]))
        self.assertTrue(
            all(set(item) == FROZEN_CLASSIFIER_RULE_FIELDS for item in classifier["rules"])
        )
        self.assertEqual(
            domain_sha256("nexus.ecosystem-static-analyzer-profile.v1", static),
            FROZEN_STATIC_PROFILE_SHA256,
        )
        self.assertEqual(
            domain_sha256("nexus.ecosystem-component-classifier-profile.v1", classifier),
            FROZEN_CLASSIFIER_PROFILE_SHA256,
        )

        mutations = {
            "duplicate-source": lambda value: value["sources"].__setitem__(1, copy.deepcopy(value["sources"][0])),
            "case-duplicate-source": lambda value: value["sources"][0].update(
                source_key=value["sources"][0]["source_key"].upper()
            ),
            "repository-source-mismatch": lambda value: value["sources"][0].update(
                canonical_repository="mismatch/repository"
            ),
            "extra-evaluation-profile": lambda value: value["evaluation_profiles"].append(
                copy.deepcopy(value["evaluation_profiles"][-1])
            ),
            "duplicated-evaluation-profile": lambda value: value["evaluation_profiles"].__setitem__(
                1, copy.deepcopy(value["evaluation_profiles"][0])
            ),
        }
        for case, mutate in mutations.items():
            candidate = json.loads(POLICY_RAW)
            mutate(candidate)
            with self.subTest(case=case), self.assertRaises(EcosystemError):
                policy_module.parse_untrusted_source_policy(candidate)

    def test_policy_and_manifest_must_be_single_link_stable_inputs(self) -> None:
        for relative in (
            "MANIFEST.json",
            "config/ecosystem-source-policy.json",
        ):
            temporary, root = temporary_policy_root()
            with self.subTest(relative=relative), temporary:
                source = root / relative
                target = source.with_name(source.name + ".hardlink-target")
                source.replace(target)
                source.hardlink_to(target)
                with self.assertRaises(EcosystemError) as raised:
                    load_trusted_source_policy(root=root)
                self.assertEqual(
                    raised.exception.reason_code,
                    "POLICY_INTEGRITY_INVALID",
                )

    def test_integrity_manifest_shapes_are_closed_and_format_is_path_bound(self) -> None:
        temporary, root = temporary_policy_root()
        with temporary:
            manifest_path = root / "MANIFEST.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["config/ecosystem-source-policy.json"]["unexpected"] = True
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaises(EcosystemError) as raised:
                load_trusted_source_policy(root=root)
            self.assertEqual(raised.exception.reason_code, "POLICY_INTEGRITY_INVALID")

        for name, metadata in (
            ("ash/unknown-field.py", {"bytes": 1, "sha256": "a" * 64, "unexpected": True}),
            ("ash/bool-size.py", {"bytes": True, "sha256": "a" * 64}),
            ("ash/uppercase-digest.py", {"bytes": 1, "sha256": "A" * 64}),
            ("ash/.GIT/config", {"bytes": 1, "sha256": "a" * 64}),
            ("ash/__PYCACHE__/module.pyc", {"bytes": 1, "sha256": "a" * 64}),
            ("ash/.Env.Production", {"bytes": 1, "sha256": "a" * 64}),
            ("ash/secret.PEM", {"bytes": 1, "sha256": "a" * 64}),
            ("ash\\non-posix.py", {"bytes": 1, "sha256": "a" * 64}),
            ("ash/cafe\u0301.py", {"bytes": 1, "sha256": "a" * 64}),
            ("ash/comparisons/item.json", {"bytes": 1, "sha256": "a" * 64}),
            ("ash/components/item.json", {"bytes": 1, "sha256": "a" * 64}),
            ("ash/decisions/item.json", {"bytes": 1, "sha256": "a" * 64}),
            ("ash/evidence/item.json", {"bytes": 1, "sha256": "a" * 64}),
            ("ash/locks/item.lock", {"bytes": 1, "sha256": "a" * 64}),
            ("ash/observations/item.json", {"bytes": 1, "sha256": "a" * 64}),
            ("ash/revisions/item.json", {"bytes": 1, "sha256": "a" * 64}),
            ("ash/staging/item.tmp", {"bytes": 1, "sha256": "a" * 64}),
            ("ash/trees/item.json", {"bytes": 1, "sha256": "a" * 64}),
        ):
            temporary, root = temporary_policy_root()
            with self.subTest(name=name), temporary:
                manifest_path = root / "MANIFEST.json"
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest[name] = metadata
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                with self.assertRaises(EcosystemError) as raised:
                    load_trusted_source_policy(root=root)
                self.assertEqual(
                    raised.exception.reason_code, "POLICY_INTEGRITY_INVALID"
                )

        temporary, root = temporary_policy_root()
        with temporary:
            # A static manifest entry literally named ``files`` cannot switch
            # the parser into release-manifest semantics.
            manifest_path = root / "MANIFEST.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["files"] = {"bytes": 0, "sha256": "0" * 64}
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            self.assertIs(type(load_trusted_source_policy(root=root)), TrustedEcosystemSourcePolicy)

        temporary, root = temporary_policy_root()
        with temporary:
            raw = (root / "config" / "ecosystem-source-policy.json").read_bytes()
            release = {
                "schema_version": "nexus.release.manifest.v1",
                "product": "Nexus",
                "distribution": "github-release",
                "version": "test",
                "files": {
                    "config/ecosystem-source-policy.json": {
                        "size": len(raw),
                        "sha256": hashlib.sha256(raw).hexdigest(),
                    }
                },
            }
            release_path = root / "release-manifest.json"
            release_path.write_text(json.dumps(release), encoding="utf-8")
            self.assertIs(type(load_trusted_source_policy(root=root)), TrustedEcosystemSourcePolicy)
            release["unexpected"] = True
            release_path.write_text(json.dumps(release), encoding="utf-8")
            with self.assertRaises(EcosystemError) as raised:
                load_trusted_source_policy(root=root)
            self.assertEqual(raised.exception.reason_code, "POLICY_INTEGRITY_INVALID")

    def test_copy_and_post_seal_mutation_invalidate_trust(self) -> None:
        temporary, root = temporary_policy_root()
        with temporary:
            trusted = load_trusted_source_policy(root=root)
            forged_copy = copy.copy(trusted)
            with self.assertRaises(EcosystemError):
                policy_module._require_trusted_source_policy(forged_copy)
            trusted._policy["mode"] = "approved"  # adversarial reflection
            with self.assertRaises(EcosystemError):
                trusted.to_dict()

    def test_self_consistent_post_seal_rewrite_cannot_rebind_policy_authority(self) -> None:
        temporary, root = temporary_policy_root()
        with temporary:
            trusted = load_trusted_source_policy(root=root)
            trusted._policy["sources"][0]["canonical_repository"] = "attacker/rewrite"
            trusted.policy_semantic_sha256 = domain_sha256(
                "nexus.ecosystem-source-policy.v1", trusted._policy
            )
            with self.assertRaises(EcosystemError) as raised:
                trusted.to_dict()
            self.assertEqual(raised.exception.reason_code, "POLICY_UNTRUSTED")

    def test_profile_and_source_mutation_fail_closed_before_sealing(self) -> None:
        for mutate in (
            lambda value: value["analysis_profiles"]["static_analyzer_profile"]["rules"][0].update(
                severity="LOW"
            ),
            lambda value: value["analysis_profiles"]["component_classifier_profile"]["rules"].reverse(),
            lambda value: value["evaluation_profiles"].pop(),
            lambda value: value["sources"][0].update(authority={**zero_authority(), "routing_authority": "granted"}),
        ):
            with self.subTest(mutate=mutate):
                value = json.loads(POLICY_RAW)
                mutate(value)
                raw = (json.dumps(value, separators=(",", ":")) + "\n").encode()
                with self.assertRaises(EcosystemError):
                    parse_source_policy_bytes(raw)

    def test_secret_shaped_source_identifier_component_fails_closed(self) -> None:
        value = json.loads(POLICY_RAW)
        secret_owner = "sk-" + ("a" * 20)
        value["sources"][0]["source_key"] = f"github/{secret_owner}/fixture"
        value["sources"][0]["canonical_repository"] = f"{secret_owner}/fixture"
        value["sources"].sort(key=lambda item: item["source_key"])
        raw = (json.dumps(value, separators=(",", ":")) + "\n").encode()
        with self.assertRaises(EcosystemError) as raised:
            parse_source_policy_bytes(raw)
        self.assertEqual(raised.exception.reason_code, "POLICY_SCHEMA_INVALID")

    def test_strict_json_boundaries_fail_closed(self) -> None:
        invalid = (
            b'{"a":1,"a":2}',
            b'{"a":1.0}',
            b'{"a":NaN}',
            b'\xef\xbb\xbf{}',
            (b'{"a":' * 34) + b'0' + (b'}' * 34),
            b'{"a":99999999999999999999}',
        )
        for raw in invalid:
            with self.subTest(raw=raw[:20]), self.assertRaises(EcosystemError):
                parse_json_bytes(raw)


class EcosystemIdentityAndStateTests(unittest.TestCase):
    def test_every_identity_domain_has_a_frozen_golden_vector(self) -> None:
        body = {"fixture": "slice3c-golden-v1"}
        expected = {
            "bridge": "bridge/31fd7f7195b9d1d271bdb1fbf7052d83c3d648f8d084c2e222574b20de3d61f1",
            "classification": "classification/36979c18149b5b28b2238b1487d3d352d5cd9d67e06918709fedca5c5be9c342",
            "classification-report": "classification-report/fb7b94fdf75ee869d0021185bc2fafc7b90be7633bcf94fd305622228d9a7611",
            "comparison": "comparison/9c99d56d061e9ea90d70a87a13a1d69dbbaf98d979ac8dc826c4b6a740c7bf5e",
            "component": "component/f0042e87c51700ef1e6d2bec285096b702cce9f2857913b62a8f08de1c89d761",
            "component-revision": "component-revision/6d6d91cc79b1100989fba9240ebbf2f4e1bf5156782b9eef1704aa9c2c142b32",
            "finding": "finding/cb8c863a87a122b2cf166876256761a2297a67cb2957927eee7b7916f74e53fa",
            "intake-attempt": "intake-attempt/f8cda584502456c27a5c65a528fd4fd0a6875dd39df5ed70381d621acf63f530",
            "intake-attempt-result": "intake-attempt-result/a87e874432f050dbb6fd245203d872deb127fe631b48957867e4378f75d62a74",
            "revision": "revision/c17af37a563dc9288e120e0764b2e8a1c9d7ad5ad5c18ea4d263b3f895fbbc21",
            "source": "source/77a8a774193aa46fe94496f086de66c564afb44fc023700454369098a0cb93a3",
            "state-record": "state-record/1ef14a454c2ef3afe0e9396d2cf97dc40dcca021475f34ce72a6e13c3b551534",
            "static-report": "static-report/f390d295e26cd33993d5a1a888c030774b3e66803559b64e8888996e1f5b023a",
            "transition": "transition/801ab4d37115c5d4e314c5a49986b47b07c9774c0ce21bc351c2801feef03ace",
            "tree": "tree/da5d1e16b17f509f0041070470f4ddecd0bb1bd567871c5cba5e51179d3765f7",
        }
        self.assertEqual(set(expected), set(ID_DOMAINS))
        observed = {kind: typed_id(kind, body) for kind in ID_DOMAINS}
        self.assertEqual(observed, expected)
        evidence = {
            "provenance": typed_id(
                "evidence", body, domain="nexus.ecosystem-provenance-evidence.v1"
            ),
            "license": typed_id(
                "evidence", body, domain="nexus.ecosystem-license-evidence.v1"
            ),
        }
        self.assertEqual(
            evidence,
            {
                "provenance": "evidence/6eab073a55d557a1059f9e5c6653105fead79622277373520429247fefdf8e29",
                "license": "evidence/ffe16d89838e51357178c0e6727baf54ce3451e386200249df25ba6c51354315",
            },
        )
        self.assertEqual(len(set(observed.values()) | set(evidence.values())), 17)
        with self.assertRaises(EcosystemError):
            validate_typed_id("a" * 64)

    def test_domain_separated_identities_are_deterministic_and_distinct(self) -> None:
        source_a = source_identity("github", "OpenAI/Codex")
        source_b = source_identity("github", "openai/codex")
        self.assertEqual(source_a, source_b)
        tree_id, tree = build_tree(
            [
                {
                    "path": "docs/readme.md",
                    "kind": "regular",
                    "mode": "regular_non_executable",
                    "size": 3,
                    "sha256": hashlib.sha256(b"abc").hexdigest(),
                }
            ]
        )
        revision = build_revision_identity(
            source_id=source_a,
            commit_object_format="git_sha1",
            commit_oid="a" * 40,
            input_sha256="b" * 64,
            tree_id=tree_id,
        )
        component = build_component_identity(source_id=source_a, component_root="docs/readme.md")
        component_revision = build_component_revision_identity(
            revision_id=revision,
            component_id=component,
            component_manifest_sha256=canonical_sha256(tree),
        )
        ids = {source_a, tree_id, revision, component, component_revision}
        self.assertEqual(len(ids), 5)
        for _index in range(100):
            self.assertEqual(source_identity("github", "OPENAI/CODEX"), source_a)
        with self.assertRaises(EcosystemError) as raised:
            source_identity("github", ("sk-" + ("a" * 20)) + "/fixture")
        self.assertEqual(raised.exception.reason_code, "SOURCE_IDENTITY_CONFLICT")

    def test_source_identity_excludes_observation_ref_and_popularity_metadata(self) -> None:
        records = (
            {
                "provider": "github",
                "canonical_repository": "OpenAI/Codex",
                "display_url": "https://example.invalid/first",
                "ref": "refs/heads/main",
                "observed_at": "2000-01-01T00:00:00Z",
                "popularity": 1,
            },
            {
                "provider": "github",
                "canonical_repository": "openai/codex",
                "display_url": "https://example.invalid/second",
                "ref": "refs/tags/untrusted",
                "observed_at": "2099-12-31T23:59:59Z",
                "popularity": 9_999_999,
            },
        )
        identities = {
            source_identity(record["provider"], record["canonical_repository"])
            for record in records
        }
        self.assertEqual(len(identities), 1)
        baseline = identities.pop()
        for _index in range(100):
            self.assertEqual(source_identity("github", "OPENAI/CODEX"), baseline)

    def test_paths_reject_traversal_ads_absolute_reserved_and_collisions(self) -> None:
        self.assertEqual(normalize_candidate_path("safe/file.txt"), "safe/file.txt")
        for path in (
            "../escape",
            "/absolute",
            "C:/drive",
            "\\\\server\\share\\file",
            "safe\\file",
            "safe/name:stream",
            "safe/CON.txt",
            "safe/trailing. ",
            "safe/\u202efile",
        ):
            with self.subTest(path=path), self.assertRaises(EcosystemError):
                normalize_candidate_path(path)
        entry = {
            "kind": "regular",
            "mode": "regular_non_executable",
            "size": 0,
            "sha256": hashlib.sha256(b"").hexdigest(),
        }
        with self.assertRaises(EcosystemError) as raised:
            build_tree([{**entry, "path": "a/X"}, {**entry, "path": "a/x"}])
        self.assertEqual(raised.exception.reason_code, "PATH_COLLISION")
        for invalid_entries in (
            [{**entry, "path": "a", "mode": "link"}],
            [{**entry, "path": "a", "kind": "symlink", "mode": "link"}],
            [{**entry, "path": "a", "link_target_sha256": "a" * 64}],
            [{**entry, "path": "a"}, {**entry, "path": "a/b"}],
        ):
            with self.subTest(invalid_entries=invalid_entries), self.assertRaises(EcosystemError):
                build_tree(invalid_entries)

    def test_path_exact_length_depth_control_uri_and_reserved_family_boundaries(self) -> None:
        exact_path = "/".join(("a" * 128, "b" * 128, "c" * 128, "d" * 125))
        self.assertEqual(len(exact_path.encode("utf-8")), 512)
        self.assertEqual(normalize_candidate_path(exact_path), exact_path)
        exact_segment = "x" * 128
        self.assertEqual(normalize_candidate_path(exact_segment), exact_segment)
        exact_depth = "/".join(["x"] * 32)
        self.assertEqual(normalize_candidate_path(exact_depth), exact_depth)

        invalid_cases = {
            "empty": "",
            "path-plus-one": exact_path + "e",
            "segment-plus-one": "x" * 129,
            "depth-plus-one": "/".join(["x"] * 33),
            "empty-segment": "safe//file",
            "uri-file": "file://safe/file",
            "uri-http": "http://example.test/file",
            "uri-https": "https://example.test/file",
            "nul": "safe/nu\x00l",
            "control": "safe/line\x1fbreak",
            "delete-control": "safe/delete\x7fchar",
            "dot-segment": "safe/./file",
            "dot-dot-segment": "safe/../file",
        }
        reserved = ("CON", "PRN", "AUX", "NUL") + tuple(
            f"COM{index}" for index in range(1, 10)
        ) + tuple(f"LPT{index}" for index in range(1, 10))
        invalid_cases.update({f"reserved-{name}": f"safe/{name}.txt" for name in reserved})
        for case, path in invalid_cases.items():
            with self.subTest(case=case), self.assertRaises(EcosystemError):
                normalize_candidate_path(path)

    def test_lifecycle_allows_only_declared_quarantine_edges(self) -> None:
        subject_id = typed_id("revision", {"test": "subject"})
        genesis = build_transition_receipt(
            subject_id=subject_id,
            subject_sha256="a" * 64,
            from_state=IMPLICIT_STATE,
            to_state=GENESIS_STATE,
            transition_axis="possession",
            evidence_ids=[],
            evaluation_receipt_sha256s=[],
            evaluation_profile_id=None,
            evaluation_profile_sha256=None,
            policy_semantic_sha256="b" * 64,
            reason_codes=[],
        )
        record = build_state_record(
            subject_id=subject_id,
            subject_sha256="a" * 64,
            previous_state_record_id=None,
            transition=genesis,
        )
        self.assertEqual(record["state"], GENESIS_STATE.as_dict())
        self.assertEqual(record["authority"], zero_authority())
        for forbidden in ("APPROVED", "ROUTABLE", "ACTIVE", "INSTALLED", "EXECUTABLE"):
            with self.subTest(forbidden=forbidden), self.assertRaises(EcosystemError):
                build_transition_receipt(
                    subject_id=subject_id,
                    subject_sha256="a" * 64,
                    from_state=GENESIS_STATE,
                    to_state=StateVector(forbidden, "NOT_REVIEWED", "IN_PROGRESS", "QUARANTINED"),
                    transition_axis="possession",
                    evidence_ids=[],
                    evaluation_receipt_sha256s=[],
                    evaluation_profile_id=None,
                    evaluation_profile_sha256=None,
                    policy_semantic_sha256="b" * 64,
                    reason_codes=[],
                )

    def test_transition_and_state_record_schemas_are_closed_and_concrete(self) -> None:
        subject_id = typed_id("revision", {"test": "closed-records"})
        transition = build_transition_receipt(
            subject_id=subject_id,
            subject_sha256="a" * 64,
            from_state=IMPLICIT_STATE,
            to_state=GENESIS_STATE,
            transition_axis="possession",
            evidence_ids=[],
            evaluation_receipt_sha256s=[],
            evaluation_profile_id=None,
            evaluation_profile_sha256=None,
            policy_semantic_sha256="b" * 64,
            reason_codes=[],
        )
        state = build_state_record(
            subject_id=subject_id,
            subject_sha256="a" * 64,
            previous_state_record_id=None,
            transition=transition,
        )
        self.assertEqual(validate_transition_receipt(transition), transition)
        self.assertEqual(validate_state_record(state), state)

        transition_mutations = (
            lambda value: value.pop("schema_version"),
            lambda value: value.update(unexpected=True),
            lambda value: value.update(schema_version=None),
            lambda value: value.update(schema_version="nexus.ecosystem-state-transition-receipt.v2"),
            lambda value: value.update(subject_sha256=1),
            lambda value: value.update(transition_axis=1),
            lambda value: value.update(permitted=1),
            lambda value: value.update(applied=0),
            lambda value: value.update(evidence_ids=()),
            lambda value: value.update(evidence_ids=[True]),
            lambda value: value.update(evaluation_receipt_sha256s=()),
            lambda value: value.update(evaluation_profile_id=1),
            lambda value: value.update(authority=[]),
        )
        for mutate in transition_mutations:
            with self.subTest(record="transition", mutate=mutate):
                candidate = copy.deepcopy(transition)
                mutate(candidate)
                with self.assertRaises(EcosystemError):
                    validate_transition_receipt(candidate)

        state_mutations = (
            lambda value: value.pop("schema_version"),
            lambda value: value.update(unexpected=True),
            lambda value: value.update(schema_version=None),
            lambda value: value.update(schema_version="nexus.ecosystem-state-record.v2"),
            lambda value: value.update(subject_sha256=True),
            lambda value: value.update(previous_state_record_id=0),
            lambda value: value.update(evidence_ids=()),
            lambda value: value.update(evidence_ids=[False]),
            lambda value: value.update(state=None),
            lambda value: value.update(state={**value["state"], "review_state": 1}),
            lambda value: value.update(authority=[]),
        )
        for mutate in state_mutations:
            with self.subTest(record="state", mutate=mutate):
                candidate = copy.deepcopy(state)
                mutate(candidate)
                with self.assertRaises(EcosystemError):
                    validate_state_record(candidate)

    def test_skip_back_edge_and_cross_axis_transition_matrix_fails_closed(self) -> None:
        subject_id = typed_id("revision", {"test": "closed-edge-matrix"})
        implicit = IMPLICIT_STATE
        genesis = GENESIS_STATE
        verified = StateVector(
            "SNAPSHOT_INTEGRITY_VERIFIED", "NOT_REVIEWED", "IN_PROGRESS", "QUARANTINED"
        )
        provenance = StateVector(
            "SNAPSHOT_INTEGRITY_VERIFIED",
            "PROVENANCE_EVIDENCE_COMPLETE",
            "IN_PROGRESS",
            "QUARANTINED",
        )
        static = StateVector(
            "SNAPSHOT_INTEGRITY_VERIFIED",
            "STATIC_SECURITY_EVIDENCE_COMPLETE",
            "IN_PROGRESS",
            "QUARANTINED",
        )
        semantic = StateVector(
            "SNAPSHOT_INTEGRITY_VERIFIED",
            "SEMANTIC_CLASSIFICATION_COMPLETE",
            "IN_PROGRESS",
            "QUARANTINED",
        )
        validation = StateVector(
            "SNAPSHOT_INTEGRITY_VERIFIED",
            "VALIDATION_EVIDENCE_COMPLETE",
            "IN_PROGRESS",
            "QUARANTINED",
        )
        terminal = StateVector(
            "SNAPSHOT_INTEGRITY_VERIFIED",
            "REVIEW_EVIDENCE_COMPLETE",
            "COMPLETE",
            "QUARANTINED",
        )
        cases = {
            "possession-skip": (implicit, verified, "possession"),
            "possession-back-edge": (verified, genesis, "possession"),
            "review-skip": (verified, semantic, "review"),
            "review-back-edge": (static, provenance, "review"),
            "review-terminal-on-wrong-axis": (validation, terminal, "review"),
            "terminal-compound-on-wrong-axis": (validation, terminal, "evidence_outcome"),
            "cross-axis-review-as-possession": (verified, provenance, "possession"),
            "cross-axis-possession-as-review": (genesis, verified, "review"),
            "terminal-back-edge": (terminal, validation, "review"),
            "unknown-axis": (verified, provenance, "activation"),
        }
        for case, (before, after, axis) in cases.items():
            review_edge = axis in {"review", "review_evidence_terminal"}
            with self.subTest(case=case), self.assertRaises(EcosystemError):
                build_transition_receipt(
                    subject_id=subject_id,
                    subject_sha256="a" * 64,
                    from_state=before,
                    to_state=after,
                    transition_axis=axis,
                    evidence_ids=[typed_id("evidence", {"case": case})],
                    evaluation_receipt_sha256s=["c" * 64] if review_edge else [],
                    evaluation_profile_id="nexus.profile.synthetic" if review_edge else None,
                    evaluation_profile_sha256="d" * 64 if review_edge else None,
                    policy_semantic_sha256="b" * 64,
                    reason_codes=["STATE_TRANSITION_INVALID"] if axis == "disposition" else [],
                )

    def test_forbidden_authority_and_lifecycle_tokens_are_rejected_explicitly(self) -> None:
        forbidden = (
            "APPROVAL_READY",
            "APPROVED",
            "AVAILABLE",
            "ACTIVE",
            "SUPERSEDED",
            "REVOKED",
            "ROUTABLE",
            "INSTALLED",
            "LOADED",
            "EXECUTABLE",
            "ENABLED",
            "HOST_ELIGIBLE",
        )
        for token in forbidden:
            with self.subTest(token=token), self.assertRaises(EcosystemError):
                parse_state_vector(
                    {
                        "possession_state": token,
                        "review_state": "NOT_REVIEWED",
                        "evidence_outcome": "IN_PROGRESS",
                        "disposition": "QUARANTINED",
                    }
                )

        subject_id = typed_id("revision", {"test": "authority"})
        transition = build_transition_receipt(
            subject_id=subject_id,
            subject_sha256="a" * 64,
            from_state=IMPLICIT_STATE,
            to_state=GENESIS_STATE,
            transition_axis="possession",
            evidence_ids=[],
            evaluation_receipt_sha256s=[],
            evaluation_profile_id=None,
            evaluation_profile_sha256=None,
            policy_semantic_sha256="b" * 64,
            reason_codes=[],
        )
        for field in zero_authority():
            with self.subTest(authority_field=field):
                forged = copy.deepcopy(transition)
                forged["authority"][field] = "granted"
                body = {
                    key: value
                    for key, value in forged.items()
                    if key not in {"schema_version", "transition_id"}
                }
                forged["transition_id"] = typed_id("transition", body)
                with self.assertRaises(EcosystemError):
                    validate_transition_receipt(forged)

    def test_review_cannot_progress_before_integrity_and_terminal_stays_quarantined(self) -> None:
        with self.assertRaises(EcosystemError):
            build_transition_receipt(
                subject_id=typed_id("revision", {"test": "subject"}),
                subject_sha256="a" * 64,
                from_state=GENESIS_STATE,
                to_state=StateVector(
                    "MIRRORED_UNREVIEWED",
                    "PROVENANCE_EVIDENCE_COMPLETE",
                    "IN_PROGRESS",
                    "QUARANTINED",
                ),
                transition_axis="review",
                evidence_ids=[typed_id("evidence", {"test": "e"}, domain="nexus.ecosystem-provenance-evidence.v1")],
                evaluation_receipt_sha256s=["c" * 64],
                evaluation_profile_id="nexus.profile.ecosystem-provenance",
                evaluation_profile_sha256="d" * 64,
                policy_semantic_sha256="b" * 64,
                reason_codes=[],
            )
        terminal = StateVector(
            "SNAPSHOT_INTEGRITY_VERIFIED",
            "REVIEW_EVIDENCE_COMPLETE",
            "COMPLETE",
            "QUARANTINED",
        )
        self.assertEqual(terminal.disposition, "QUARANTINED")

    def test_forged_transition_cannot_manufacture_terminal_state_record(self) -> None:
        subject_id = typed_id("revision", {"test": "forgery"})
        genesis = build_transition_receipt(
            subject_id=subject_id,
            subject_sha256="a" * 64,
            from_state=IMPLICIT_STATE,
            to_state=GENESIS_STATE,
            transition_axis="possession",
            evidence_ids=[],
            evaluation_receipt_sha256s=[],
            evaluation_profile_id=None,
            evaluation_profile_sha256=None,
            policy_semantic_sha256="b" * 64,
            reason_codes=[],
        )
        forged = copy.deepcopy(genesis)
        forged["to_state"] = {
            "possession_state": "SNAPSHOT_INTEGRITY_VERIFIED",
            "review_state": "REVIEW_EVIDENCE_COMPLETE",
            "evidence_outcome": "COMPLETE",
            "disposition": "QUARANTINED",
        }
        forged_body = {
            key: value for key, value in forged.items() if key not in {"schema_version", "transition_id"}
        }
        forged["transition_id"] = typed_id("transition", forged_body)
        with self.assertRaises(EcosystemError) as raised:
            build_state_record(
                subject_id=subject_id,
                subject_sha256="a" * 64,
                previous_state_record_id=None,
                transition=forged,
            )
        self.assertEqual(raised.exception.reason_code, "STATE_TRANSITION_INVALID")

    def test_rejected_state_cannot_coexist_with_review_progress(self) -> None:
        with self.assertRaises(EcosystemError):
            parse_state_vector(
                {
                    "possession_state": "SNAPSHOT_INTEGRITY_VERIFIED",
                    "review_state": "PROVENANCE_EVIDENCE_COMPLETE",
                    "evidence_outcome": "IN_PROGRESS",
                    "disposition": "REJECTED",
                }
            )

    def test_bridge_and_comparison_subjects_cannot_receive_lifecycle_state(self) -> None:
        for kind in ("bridge", "comparison"):
            with self.subTest(kind=kind), self.assertRaises(EcosystemError):
                build_transition_receipt(
                    subject_id=typed_id(kind, {"test": kind}),
                    subject_sha256="a" * 64,
                    from_state=IMPLICIT_STATE,
                    to_state=GENESIS_STATE,
                    transition_axis="possession",
                    evidence_ids=[],
                    evaluation_receipt_sha256s=[],
                    evaluation_profile_id=None,
                    evaluation_profile_sha256=None,
                    policy_semantic_sha256="b" * 64,
                    reason_codes=[],
                )


if __name__ == "__main__":
    unittest.main()

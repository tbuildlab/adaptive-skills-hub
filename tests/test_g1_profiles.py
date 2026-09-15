from __future__ import annotations

import copy
import json
import unittest

from ash.g1_profiles import (
    G1Error, MAX_ITEMS, MAX_STRING, TrustedObservations, _issue_observations,
    bounded, candidate as validate_candidate, conformance, digest, host_profile,
    model_profile, observations, parse_input,
)
from tests.g1_fixtures import candidate, host, inputs, model, observation, record, request


class G1ProfileTests(unittest.TestCase):
    def test_versioned_contracts(self):
        model_profile(model())
        host_profile(host())
        validate_candidate(candidate())
        conformance(record(candidate()))

    def test_authority_and_policy_fields_are_not_profile_contracts(self):
        for obj, parser in ((model(), model_profile), (host(), host_profile), (candidate(), validate_candidate)):
            for key in ("permission_grants", "trusted", "policy", "execute", "command", "aliases", "universal_score"):
                with self.subTest(key=key, schema=obj["schema_version"]), self.assertRaises(G1Error):
                    parser({**obj, key: True})

    def test_closed_versions(self):
        for obj, parser in ((model(), model_profile), (host(), host_profile), (candidate(), validate_candidate)):
            obj["schema_version"] += ".future"
            with self.assertRaises(G1Error):
                parser(obj)

    def test_no_global_host_inventory(self):
        h = host()
        h["inventory_completeness"] = "globally_enumerated"
        with self.assertRaises(G1Error):
            host_profile(h)

    def test_case_unicode_and_alias_ambiguity(self):
        for identity in ("MODEL", "ｍodel", "model\u202e", "model/path", "model alias"):
            c = candidate()
            c["model"]["profile_id"] = identity
            with self.subTest(identity=identity), self.assertRaises(G1Error):
                validate_candidate(c)

    def test_malformed_digest(self):
        for value in ("A" * 64, "a" * 63, "g" * 64, None, 1):
            c = candidate()
            c["host"]["adapter_sha256"] = value
            with self.subTest(value=value), self.assertRaises(G1Error):
                validate_candidate(c)

    def test_profile_dates_are_bounded(self):
        for key, value in (("observed_at", True), ("expires_at", 1000), ("expires_at", 100000), ("expires_at", -1)):
            h = host()
            h[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(G1Error):
                host_profile(h)

    def test_boolean_integer_confusion(self):
        h = host()
        h["states"]["visible_now"] = 1
        with self.assertRaises(G1Error):
            host_profile(h)

    def test_duplicate_profile_evidence_and_nodes(self):
        c = candidate()
        c["path"]["nodes"] *= 2
        with self.assertRaises(G1Error):
            validate_candidate(c)
        h = host()
        h["evidence_refs"] *= 2
        with self.assertRaises(G1Error):
            host_profile(h)

    def test_cost_known_requires_complete_components_and_evidence(self):
        for key in ("execution", "retries", "validation", "context", "tools", "human_recovery"):
            c = candidate()
            c["cost"]["components"][key] = None
            with self.subTest(key=key), self.assertRaises(G1Error):
                validate_candidate(c)

    def test_enforcement_classification_is_not_an_instruction(self):
        for layer in ("instructions", "host_handoff", "magic"):
            r = record(candidate())
            r["enforcing_layer"] = layer
            with self.subTest(layer=layer), self.assertRaises(G1Error):
                conformance(r)

    def test_malformed_json_is_closed(self):
        for raw in (b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":1.0}', b'\xef\xbb\xbf{}', b'\xff', b'[' * 1000,
                    b'{"n":' + b'9' * 5000 + b'}', b'{"a":"\\ud800"}'):
            with self.subTest(raw=raw[:24]), self.assertRaises(G1Error):
                parse_input(raw)

    def test_depth_cycles_size_and_subclasses(self):
        cycle = []
        cycle.append(cycle)
        class MappingSubclass(dict):
            pass
        class StringSubclass(str):
            pass
        for value in (cycle, [0] * (MAX_ITEMS + 1), "a" * (MAX_STRING + 1), MappingSubclass(), StringSubclass("x"), 1.0):
            with self.subTest(kind=type(value).__name__), self.assertRaises(G1Error):
                bounded(value)

    def test_forged_handle_and_mutation_fail(self):
        handle = inputs()["trusted_observations"]
        with self.assertRaises(G1Error):
            observations(TrustedObservations(handle._payload))
        with self.assertRaises(G1Error):
            observations(json.loads(handle._payload))
        object.__setattr__(handle, "_payload", b"{}")
        with self.assertRaises(G1Error):
            observations(handle)

    def test_observation_copies_source_and_rejects_duplicate_subject(self):
        c, req = candidate(), request()
        row = observation(c, req, [record(c)])
        handle = _issue_observations([row], source="fixture")
        row["states"]["permitted_now"] = False
        self.assertTrue(observations(handle)["rows"][0]["states"]["permitted_now"])
        with self.assertRaises(G1Error):
            _issue_observations([row, row], source="fixture")

    def test_canonical_identity_and_non_nfc(self):
        self.assertEqual(digest({"b": 2, "a": 1}), digest({"a": 1, "b": 2}))
        with self.assertRaises(G1Error):
            bounded("e\u0301")


if __name__ == "__main__":
    unittest.main()

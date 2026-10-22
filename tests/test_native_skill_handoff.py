"""Bounded native recommendation admission; real local registry, no new trust fixtures."""
import copy
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ash.mcp.adapter import NexusMcpRuntime
from ash.mcp.authorization import WorkspaceAuthorizer, guard_regular_file, verify_unchanged
from ash.mcp.schemas import NexusMcpError
from ash.semantic_domains import load_trusted_applicability_registry, resolve_trusted_applicability

ROOT = Path(__file__).resolve().parents[1]
LAB = ROOT.parent
CORE_ID = 'skill:099d20aa14905c87'
SCROLL_ID = 'skill:d5c281f399e6203f'


def recommend(request, candidate=CORE_ID):
    data = copy.deepcopy(request)
    original = {key: data.get(key, default) for key, default in (
        ('task', None), ('workspace_id', None), ('project_context_mode', 'governance'), ('constraints', []))}
    digest = hashlib.sha256(json.dumps(original, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
    data['native_recommendation'] = {'schema_version': 'nexus.native-skill-recommendation.v1', 'resource_id': candidate, 'request_sha256': digest}
    return data


def positive():
    # Reuse the original successful single-task usability request verbatim.
    return json.loads((LAB / 'core-usability-gsap-20261021/evidence/request.json').read_text(encoding='utf-8'))


class NativeSkillHandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = NexusMcpRuntime._build_catalog()
        cls.authorizer = WorkspaceAuthorizer.from_file(Path.home() / 'AppData/Local/Nexus/workspaces.json')

    def runtime(self, catalog=None, **kwargs):
        return NexusMcpRuntime(self.authorizer, catalog_builder=lambda: catalog if catalog is not None else self.catalog, **kwargs)

    def assert_refused_before_read(self, request, code, runtime=None):
        runtime = runtime or self.runtime()
        with patch.object(runtime, '_read_selected_skill', side_effect=AssertionError('must not load refused candidate')) as read:
            with self.assertRaises(NexusMcpError) as failure:
                runtime.plan(request)
            self.assertEqual(failure.exception.code, code)
            read.assert_not_called()

    def test_positive_guarded_instructions_and_legacy_projection(self):
        runtime = self.runtime()
        legacy = runtime.plan(positive())
        with patch.object(runtime, '_read_selected_skill', wraps=runtime._read_selected_skill) as read:
            result = runtime.plan(recommend(positive()))
            self.assertEqual(read.call_count, 1)
        handoff = result.pop('native_handoff')
        self.assertEqual(handoff['status'], 'loaded_verified')
        self.assertEqual(handoff['execution_authority'], 'none')
        self.assertEqual(handoff['resource_id'], CORE_ID)
        self.assertEqual(hashlib.sha256(handoff['instructions'].encode('utf-8')).hexdigest(), handoff['content_sha256'])
        self.assertIn('gsap', handoff['instructions'])
        self.assertNotIn('path', handoff)
        for key in ('status', 'task_summary', 'selected_skills', 'fallback'):
            self.assertEqual(result[key], legacy[key])
        self.assertNotIn('native_handoff', legacy)
        self.assertNotIn(handoff['instructions'], json.dumps(legacy))
        self.assertNotIn('instructions', legacy['selected_skills'][0])

    def test_shared_native_resource_identity_through_existing_discovery(self):
        runtime = self.runtime()
        # This is the gsap-core path actually surfaced in the current Host Skill
        # catalog, not a caller-selected MCP path or a copied Skill fixture.
        native_path = Path.home() / '.codex/skills/gsap-core/SKILL.md'
        native_file, native_before = guard_regular_file(native_path, runtime.skill_roots)
        discovery = runtime.discover_capabilities({'capability_tags': ['animation']})
        self.assertFalse(discovery['truncated'])
        candidates = [item for item in discovery['capabilities'] if item['display_name'] == 'gsap-core']
        self.assertEqual(len(candidates), 1)
        candidate = candidates[0]
        self.assertEqual(candidate['resource_id'], CORE_ID)
        self.assertEqual(candidate['availability'], 'available')
        records = [s for s in self.catalog['skills'] if s['id'] == candidate['resource_id']]
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertIsNotNone(resolve_trusted_applicability(record, load_trusted_applicability_registry()))
        catalog_file, catalog_before = guard_regular_file(Path(record['skill_md_path']), runtime.skill_roots)
        self.assertTrue(os.path.samefile(native_file, catalog_file))
        self.assertEqual((native_before.st_dev, native_before.st_ino), (catalog_before.st_dev, catalog_before.st_ino))
        observed = []
        original_reader = runtime._read_selected_skill

        def capture_guarded_read(path):
            self.assertTrue(os.path.samefile(native_file, path))
            raw = original_reader(path)
            observed.append(hashlib.sha256(raw).hexdigest())
            return raw

        with patch.object(runtime, '_read_selected_skill', side_effect=capture_guarded_read):
            result = runtime.plan(recommend(positive(), candidate['resource_id']))
        handoff = result['native_handoff']
        body_hash = hashlib.sha256(handoff['instructions'].encode('utf-8')).hexdigest()
        self.assertEqual(observed, [record['content_sha256']])
        self.assertEqual(body_hash, observed[0])
        self.assertEqual(handoff['content_sha256'], body_hash)
        self.assertEqual(result['selected_skills'][0]['resource_id'], candidate['resource_id'])
        verify_unchanged(native_file, native_before)
        verify_unchanged(catalog_file, catalog_before)

    def test_original_bloom_gate_is_not_bypassed(self):
        original = json.loads((LAB / 'bloom-scrolltrigger-selection-20261021/request.json').read_text(encoding='utf-8'))
        self.assert_refused_before_read(recommend(original, SCROLL_ID), 'NATIVE_APPLICABILITY_NOT_ESTABLISHED')

    def test_frozen_negative_recommendations_do_not_load(self):
        frozen = LAB / 'semantic-routing-v1-20261021/review/semantic-intent-v1/EVALUATION-BOUNDARIES.json'
        self.assertEqual(hashlib.sha256(frozen.read_bytes()).hexdigest(), '3a5ae4f3d6030795c2f5f908cec8d192ffca71dd9dce3767f00b95b31cde0e54')
        for item in json.loads(frozen.read_text(encoding='utf-8'))['cases']:
            if item['id'].startswith('N'):
                with self.subTest(case=item['id']):
                    self.assert_refused_before_read(recommend({'task': item['task'], 'workspace_id': 'nexus-capability-lab', 'project_context_mode': 'none'}, SCROLL_ID), 'NATIVE_APPLICABILITY_NOT_ESTABLISHED')

    def test_forged_fields_and_paths_rejected(self):
        for key in ('path', 'trust', 'execution_authority', 'instructions', 'domains'):
            with self.subTest(field=key):
                request = recommend(positive())
                request['native_recommendation'][key] = 'forged'
                self.assert_refused_before_read(request, 'INVALID_REQUEST')
        request = recommend(positive())
        request['native_recommendation']['resource_id'] = '../SKILL.md'
        self.assert_refused_before_read(request, 'INVALID_REQUEST')

    def test_binding_and_workspace_rejected(self):
        for key, value in (('task', 'different'), ('constraints', ['different']), ('workspace_id', 'other')):
            request = recommend(positive())
            request[key] = value
            self.assert_refused_before_read(request, 'NATIVE_RECOMMENDATION_BINDING_FAILED')
        request = positive()
        request['workspace_id'] = 'not-authorized'
        self.assert_refused_before_read(recommend(request), 'UNAUTHORIZED_WORKSPACE')

    def test_unknown_wrong_unavailable_and_duplicate_candidates(self):
        self.assert_refused_before_read(recommend(positive(), 'skill:0000000000000000'), 'NATIVE_CANDIDATE_UNAVAILABLE')
        self.assert_refused_before_read(recommend(positive(), SCROLL_ID), 'NATIVE_APPLICABILITY_NOT_ESTABLISHED')
        for status in ('disabled', 'duplicate_conflict'):
            catalog = copy.deepcopy(self.catalog)
            next(s for s in catalog['skills'] if s['id'] == CORE_ID)['status'] = status
            self.assert_refused_before_read(recommend(positive()), 'NATIVE_CANDIDATE_UNAVAILABLE', self.runtime(catalog))
        catalog = copy.deepcopy(self.catalog)
        catalog['skills'].append(copy.deepcopy(next(s for s in catalog['skills'] if s['id'] == CORE_ID)))
        self.assert_refused_before_read(recommend(positive()), 'NATIVE_CANDIDATE_UNAVAILABLE', self.runtime(catalog))

    def test_untrusted_metadata_and_changed_catalog_hash(self):
        for field, value in (('metadata_fingerprint', '0' * 64), ('content_sha256', '0' * 64)):
            catalog = copy.deepcopy(self.catalog)
            next(s for s in catalog['skills'] if s['id'] == CORE_ID)[field] = value
            self.assert_refused_before_read(recommend(positive()), 'NATIVE_APPLICABILITY_NOT_ESTABLISHED', self.runtime(catalog))

    def test_changed_bytes_refuse_instruction_delivery(self):
        runtime = self.runtime()
        with patch.object(runtime, '_read_selected_skill', return_value=b'changed after selection'):
            with self.assertRaises(NexusMcpError) as failure:
                runtime.plan(recommend(positive()))
        self.assertEqual(failure.exception.code, 'NATIVE_SKILL_LOAD_REFUSED')

    def test_existing_path_guard_still_enforced(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
            runtime = self.runtime(skill_roots=[Path(temporary)])
            with self.assertRaises(NexusMcpError) as failure:
                runtime.plan(recommend(positive()))
            self.assertEqual(failure.exception.code, 'NATIVE_SKILL_LOAD_REFUSED')

    def test_exact_existing_skill_prohibition_still_enforced(self):
        request = positive()
        request['constraints'].append('no_gsap-core')
        self.assert_refused_before_read(recommend(request), 'NATIVE_APPLICABILITY_NOT_ESTABLISHED')


if __name__ == '__main__':
    unittest.main()

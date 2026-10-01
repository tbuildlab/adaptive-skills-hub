"""One real documentary binding; negative copies are illustrative, never Hosts."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from ash.common import sha256_text
from ash.v2 import ContextItem, ProjectContext, plan_task, validate_plan
from prototypes.governance_assessment_offline_v1 import review_bytes
from prototypes.governance_advisory_traceability_v1 import review_pair
from scripts import hub

ROOT = Path(__file__).resolve().parents[1]
ASSESSMENT = ROOT / 'docs/fixtures/nexus-governance-real-evidence-assessment-v1.json'
OBSERVATION = ROOT / 'docs/fixtures/nexus-governance-real-evidence-observation-v1.json'
SOURCE = ROOT / 'docs/nexus-g2-route-b-authoritative-evidence-acceptance-v1.md'


def encode(record):
    return (json.dumps(record, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()


def canonical(report):
    return (json.dumps(report, sort_keys=True, separators=(',', ':'), ensure_ascii=True) + '\n').encode()


def lf(path):
    return path.read_bytes().replace(b'\r\n', b'\n')


class RealEvidenceApplicationTests(unittest.TestCase):
    def setUp(self):
        self.original = lf(ASSESSMENT)
        self.record = json.loads(self.original)
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name)

    def variant(self):
        result = copy.deepcopy(self.record)
        result['basis'] = 'ILLUSTRATIVE'
        result['record_id'] = 'illustrative.real-source-negative.v1'
        return result

    def advice(self, data):
        content = data.decode('utf-8')
        item = ContextItem('assessment.json', 'explicit_task_file', 'project_evidence',
                           sha256_text(content), len(data), 'explicitly named by task', content)
        plan = plan_task('Review assessment.json', {'skills': [], 'agents': []}, self.project,
                         context_reader=lambda *a, **k: ProjectContext(str(self.project), items=[item]))
        before = copy.deepcopy(plan.to_dict())
        validation = validate_plan(plan)
        plain = hub._plan_handoff(plan, [], validation, self.project)
        result = hub._plan_handoff(plan, [], validation, self.project,
                                   governance_advisory_context='assessment.json')
        advice = result.pop('governance_advisory')
        self.assertEqual(result, plain)
        self.assertEqual(plan.to_dict(), before)
        self.assertEqual(advice['authority'], 'none')
        self.assertIs(advice['dispatch_requested'], False)
        self.assertEqual(advice['freshness'], 'UNKNOWN')
        self.assertEqual(advice['selection_completeness'], 'UNVERIFIED')
        self.assertEqual(advice['source_evidence_status'], 'UNVERIFIED')
        return advice

    def rejected(self, record, code):
        report = self.advice(encode(record))['report']
        self.assertEqual(report['handling'], 'REJECT_RECORD')
        self.assertEqual(report['diagnostics'][0]['code'], code)

    def test_real_source_and_all_selected_reference_bytes_are_bound(self):
        self.assertEqual(self.record['basis'], 'REAL')
        self.assertEqual(self.record['subject']['id'], 'nexus.g2.route-b.authoritative-evidence-acceptance.v1')
        self.assertEqual(hashlib.sha256(lf(SOURCE)).hexdigest().upper(),
                         '1210577F16299C400A05D5F18EF102EBCDE3C66132BB5B2E78C3248A9DC0E568')
        for ref in self.record['references']:
            self.assertEqual(hashlib.sha256(lf(ROOT/ref['locator'])).hexdigest().upper(), ref['integrity_sha256'])
        text = lf(SOURCE).decode()
        for statement in ('PROVIDER CLARIFICATION IS REQUIRED', 'INCOMPLETE', 'Provider qualification is **NOT ACCEPTED**', 'G2 **HOLD**'):
            self.assertIn(statement, text)

    def test_captured_real_cli_observation_matches_current_computation(self):
        observation = json.loads(lf(OBSERVATION))
        actual = observation['enabled_advisory']
        self.assertEqual(actual['report'], review_bytes(self.original))
        self.assertEqual(actual, self.advice(self.original))
        self.assertEqual(observation['exit_codes'], dict(enabled=0, repeated=0, disabled=0))
        self.assertTrue(observation['repeat_advisory_equal'])
        self.assertTrue(observation['legacy_handoff_equal_when_disabled'])
        self.assertFalse(observation['disabled_advisory_present'])
        pair = review_pair(self.original, canonical(actual['report']))
        self.assertEqual(pair, observation['pair_comparison'])
        self.assertEqual(pair['comparison'], 'MATCH')
        self.assertEqual(pair['authority'], 'none')

    def test_actual_unmocked_cli_enable_repeat_disable(self):
        task = 'Read-only documentary review fixtures/nexus-governance-real-evidence-assessment-v1.json and nexus-g2-route-b-authoritative-evidence-acceptance-v1.md'
        cmd = [sys.executable, '-B', str(ROOT/'scripts/hub.py'), 'plan', task, '--project', str(ROOT/'docs'), '--handoff']
        state = ROOT/'state/last-plan.json'
        before = state.read_bytes() if state.exists() else None
        handoffs = []
        for extra in (['--governance-advisory-context', 'fixtures/nexus-governance-real-evidence-assessment-v1.json'],
                      ['--governance-advisory-context', 'fixtures/nexus-governance-real-evidence-assessment-v1.json'], []):
            completed = subprocess.run(cmd+extra, cwd=ROOT, capture_output=True, timeout=120)
            self.assertEqual(completed.returncode, 0)
            self.assertEqual(completed.stderr, b'')
            handoffs.append(json.loads(completed.stdout.decode().replace('\r\n', '\n').split('Handoff:\n', 1)[1]))
        first = handoffs[0].pop('governance_advisory')
        second = handoffs[1].pop('governance_advisory')
        self.assertEqual(first, second)
        self.assertEqual(first['report'], review_bytes(self.original))
        self.assertEqual(handoffs[0], handoffs[1])
        self.assertEqual(handoffs[0], handoffs[2])
        self.assertEqual(state.read_bytes() if state.exists() else None, before)

    def test_unknown_dependency_and_coverage_survive(self):
        report = self.advice(self.original)['report']
        self.assertEqual(report['handling'], 'PRESERVE_UNKNOWN')
        self.assertEqual(report['unresolved_required_checks'], [1, 2])
        self.assertEqual(report['unknown_profile_facts'], [2])
        self.assertEqual(report['unverified_pass_claims'], [0, 3])
        self.assertEqual(self.record['checks'][2]['requires'], ['R02'])
        self.assertEqual(len(report['declared_checks']), 4)
        self.assertNotIn('accepted', report)

    def test_missing_source_reference_rejected(self):
        record = self.variant()
        record['references'] = [r for r in record['references'] if r['id'] != 'source']
        self.rejected(record, 'UNRESOLVED_REFERENCE')

    def test_changed_underlying_source_does_not_gain_authentication(self):
        source_ref = next(r for r in self.record['references'] if r['id'] == 'source')
        changed = lf(SOURCE) + b'ILLUSTRATIVE changed source\n'
        self.assertNotEqual(hashlib.sha256(changed).hexdigest().upper(), source_ref['integrity_sha256'])
        # A focused independent byte comparison finds the mismatch. The consumer
        # cannot find it through locators; its untouched claims remain unverified.
        self.assertEqual(self.advice(self.original)['report']['unverified_pass_claims'], [0, 3])

    def test_stale_mismatched_binding_requires_independent_review(self):
        record = self.variant()
        ref = next(r for r in record['references'] if r['id'] == 'source')
        ref['integrity_sha256'] = '0' * 64
        ref['captured_at'] = '2000-01-01'
        ref['valid_until'] = '2000-01-02'
        self.assertNotEqual(hashlib.sha256(lf(SOURCE)).hexdigest().upper(), ref['integrity_sha256'])
        advice = self.advice(encode(record))
        self.assertEqual(advice['freshness'], 'UNKNOWN')
        self.assertEqual(advice['report']['handling'], 'PRESERVE_UNKNOWN')
        self.assertEqual(advice['report']['unverified_pass_claims'], [0, 3])

    def test_removed_required_evidence_never_becomes_pass(self):
        record = self.variant()
        record['checks'][1]['outcome']['evidence_refs'] = []
        self.assertIn(1, self.advice(encode(record))['report']['unresolved_required_checks'])
        record['checks'][0]['outcome']['evidence_refs'] = []
        self.rejected(record, 'PASS_EVIDENCE_ASSOCIATION_MISSING')

    def test_unresolved_dependency_blocks_attempted_pass(self):
        record = self.variant()
        record['checks'][2]['outcome']['state'] = 'PASS'
        self.rejected(record, 'PASS_REQUIRED_PREMISE_UNRESOLVED')

    def test_contradictory_applicability_outcome_rejected(self):
        record = self.variant()
        record['checks'][0]['applicability']['state'] = 'NOT_APPLICABLE'
        self.rejected(record, 'APPLICABILITY_OUTCOME_CONFLICT')

    def test_unsupported_version_and_malformed_context(self):
        record = self.variant()
        record['schema_version'] = 'future'
        self.rejected(record, 'UNSUPPORTED_VERSION')
        self.assertEqual(self.advice(b'{')['report']['handling'], 'REJECT_RECORD')

    def test_evaluator_failure_cannot_pass_or_echo(self):
        with patch('prototypes.governance_assessment_offline_v1.review_bytes',
                   side_effect=RuntimeError('ILLUSTRATIVE_ERROR_TEXT')):
            advice = self.advice(self.original)
        self.assertEqual(advice['diagnostic'], 'EVALUATOR_FAILED')
        self.assertIsNone(advice['report'])
        self.assertNotIn('ILLUSTRATIVE_ERROR_TEXT', json.dumps(advice))

    def test_unsupported_semantic_pass_remains_unverified_not_authority(self):
        record = self.variant()
        record['checks'][1]['outcome']['state'] = 'PASS'
        record['checks'][1]['outcome']['reason'] = 'ILLUSTRATIVE unsupported claim: independent runtime enforcement observed.'
        advice = self.advice(encode(record))
        # Nonempty refs do not prove their relevance. Manual source comparison
        # rejects this claim; do not claim the unchanged structural consumer did.
        self.assertIn('INCOMPLETE', lf(SOURCE).decode())
        self.assertIn(1, advice['report']['unverified_pass_claims'])
        self.assertEqual(advice['report']['declared_checks'][2]['outcome'], 'UNKNOWN')

    def test_authority_inferred_from_pass_is_inert(self):
        record = self.variant()
        record['checks'][3]['outcome']['reason'] = 'ILLUSTRATIVE forged inference: documentary PASS authorizes execution.'
        advice = self.advice(encode(record))
        self.assertEqual(advice['report']['authority'], 'none')
        self.assertIs(advice['report']['dispatch_requested'], False)
        self.assertIn(3, advice['report']['unverified_pass_claims'])
        self.assertIn('no provider outreach', lf(SOURCE).decode())

    def test_effect_claim_without_reconciliation_is_not_closed(self):
        record = self.variant()
        record['checks'][2]['outcome']['reason'] = 'ILLUSTRATIVE unsupported claim: attempted provider effect settled.'
        report = self.advice(encode(record))['report']
        self.assertIn(2, report['unresolved_required_checks'])
        record['checks'][2]['outcome']['state'] = 'PASS'
        self.rejected(record, 'PASS_REQUIRED_PREMISE_UNRESOLVED')

    def test_executed_capability_does_not_imply_applied_or_authority(self):
        record = self.variant()
        executed = copy.deepcopy(record['checks'][0])
        executed.update(id='X1', capability={'ref':'source', 'dimension':'EXECUTED'})
        executed['criterion'] = 'ILLUSTRATIVE local invocation evidence only.'
        applied = copy.deepcopy(record['checks'][2])
        applied.update(id='X2', capability={'ref':'source', 'dimension':'APPLIED'}, requires=['X1'])
        applied['criterion'] = 'ILLUSTRATIVE independent application/reconciliation remains unproved.'
        record['checks'].extend([executed, applied])
        report = self.advice(encode(record))['report']
        self.assertEqual(report['declared_checks'][4]['outcome'], 'PASS')
        self.assertIn(4, report['unverified_pass_claims'])
        self.assertEqual(report['declared_checks'][5]['outcome'], 'UNKNOWN')
        self.assertIn(5, report['unresolved_required_checks'])
        self.assertEqual(report['authority'], 'none')

    def test_changed_assessment_stale_report_mismatches(self):
        report = review_bytes(self.original)
        record = self.variant()
        record['checks'][1]['outcome']['reason'] += ' ILLUSTRATIVE different captured bytes.'
        pair = review_pair(encode(record), canonical(report))
        self.assertEqual(pair['comparison'], 'MISMATCH')
        self.assertEqual(pair['authority'], 'none')
        self.assertEqual(pair['recomputed_report']['unresolved_required_checks'], [1, 2])

    def test_omitted_coverage_cannot_become_complete(self):
        record = self.variant()
        record['checks'] = [record['checks'][0], record['checks'][3]]
        advice = self.advice(encode(record))
        self.assertEqual(len(advice['report']['declared_checks']), 2)
        self.assertEqual(advice['report']['handling'], 'REQUIRE_REVIEW')
        self.assertEqual(advice['selection_completeness'], 'UNVERIFIED')
        self.assertEqual(advice['report']['unverified_pass_claims'], [0, 1])


if __name__ == '__main__':
    unittest.main()

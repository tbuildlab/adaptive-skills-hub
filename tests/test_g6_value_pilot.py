"""Finite PUBLIC fixtures only; no signing, native attempt, pilot or model run."""
from pathlib import Path
import copy
import hashlib
import json
import tempfile
import time
import unittest
from unittest.mock import patch

from ash import g6_value_pilot as pilot, g6_native_binding as guard
from ash import g6_retention_substitution as binding, g6_private_completion as task


def public_input():
    return b'PUBLIC FINITE FIXTURE\nSource records: '+json.dumps(binding.PUBLIC_ROWS).encode('ascii')+b'\n/no_think'


def prepared(directory,raw=None):
    (directory/'input').mkdir(parents=True)
    (directory/'result').mkdir()
    (directory/'input/task.txt').write_bytes(public_input())
    output=binding.PUBLIC_EXPECTED if raw is None else raw
    (directory/'result/stdout.bin').write_bytes(output)
    return {'status':'DETERMINISTIC_RETENTION_RESULT_OBSERVED','retired':True,
        'job_active_after_termination':0,'stdout_sha256':hashlib.sha256(output).hexdigest(),
        'authenticated_payload_sha256':'a'*64,'elapsed_seconds':1,'user_cpu_100ns':1}


class ValuePilotTests(unittest.TestCase):
    def fixture_plan(self):
        return {'input_sha256':hashlib.sha256(public_input()).hexdigest()}

    def test_closed_six_roles_only_and_opposite_pair_order(self):
        self.assertEqual(frozenset(pilot.ROLES),guard.VALUE_PILOT_ROLES)
        self.assertEqual(tuple(r.split('_')[1] for r in pilot.ROLES),('native','nexus','nexus','native','native','nexus'))
        for role in ('native','deterministic','pilot_nexus_3','../pilot_native_1',''):
            with self.assertRaises(ValueError):pilot.native_plan(role)

    def test_fixed_comparable_host_model_input_policy_features_and_limits(self):
        plans=[pilot.native_plan(r) for r in pilot.ROLES]
        for field in ('executable','input_sha256','source_files','model_ref','worker_sha256',
                      'runtime_files','runtime_pins_sha256','host_material','limits','environment_names',
                      'telemetry_overrides','declared_restrictions','network'):
            self.assertTrue(all(p[field]==plans[0][field] for p in plans))
        self.assertIsNone(plans[0]['model_ref'])
        self.assertEqual(len({p['cwd'] for p in plans}),6)
        self.assertTrue(all(p['candidate_arguments'][:3]==['-I','-S','-B'] for p in plans))
        self.assertTrue(all('model_blob' not in p and p['max_attempts']==1 and not p['automatic_retry'] for p in plans))
        self.assertTrue(all(not any('.gguf' in n or '.blob' in n for n in p['filesystem']) for p in plans))

    def test_new_exact_subjects_do_not_reuse_each_other_or_old_decisions(self):
        bodies=[pilot.owner_intent(r) for r in pilot.ROLES]
        self.assertEqual(len({b['subject_id'] for b in bodies}),6)
        self.assertTrue(all(b['max_attempts']==1 and not b['automatic_retry'] and not b['capability_registration'] for b in bodies))
        self.assertTrue(all(b['purpose']=='APPROVE_ONE_G6_RETENTION_VALUE_PILOT_SLOT_V1' for b in bodies))
        self.assertNotIn(binding.owner_intent()['subject_id'],{b['subject_id'] for b in bodies})

    def test_native_recipe_does_not_call_nexus_verifier(self):
        with patch.object(task,'verified_report',side_effect=AssertionError('Native must not call Nexus')):
            self.assertEqual(pilot.native_verified_report(public_input(),binding.PUBLIC_EXPECTED),binding.PUBLIC_EXPECTED.rsplit(b'END_G6_AUDIT',1)[0])

    def test_both_validation_recipes_accept_same_source_and_reject_same_corruption(self):
        with patch.object(task,'rows',return_value=copy.deepcopy(binding.PUBLIC_ROWS)):
            for output in (binding.PUBLIC_EXPECTED,binding.PUBLIC_EXPECTED.replace(b'\n',b'\r\n'),
                           b'noise'+binding.PUBLIC_EXPECTED,binding.PUBLIC_EXPECTED[:-4],
                           binding.PUBLIC_EXPECTED.replace(b'KEEP',b'DROP'),b'',b'x'*65537):
                self.assertEqual(pilot.native_verified_report(public_input(),output),task.verified_report(output))

    def test_native_rejects_malformed_ambiguous_unretired_unsafe_or_oversized_input(self):
        cases=[b'',b'x'*16385,public_input()+b'Source records: []']
        for field,value in [('retired',False),('retained_bytes',True),('retained_bytes',65537),('attempt','../x'),('status','PASS')]:
            rows=copy.deepcopy(binding.PUBLIC_ROWS);rows[0][field]=value
            cases.append(b'Source records: '+json.dumps(rows).encode()+b'\n/no_think')
        for raw in cases:
            with self.subTest(length=len(raw)):self.assertIsNone(pilot.native_verified_report(raw,binding.PUBLIC_EXPECTED))

    def test_native_recipe_matches_fixed_worker_name_and_frame_bounds(self):
        for length in (16,17):
            rows=copy.deepcopy(binding.PUBLIC_ROWS);rows[0]['attempt']='x'*length
            raw=b'Source records: '+json.dumps(rows).encode()+b'\n/no_think'
            output=binding.PUBLIC_EXPECTED.replace(b'sampleA',b'x'*length)
            self.assertEqual(pilot.native_verified_report(raw,output) is not None,length==16)
        self.assertIsNone(pilot.native_verified_report(public_input()+b'\n/no_think',binding.PUBLIC_EXPECTED))

    def test_public_both_arm_artifacts_exclusive_and_factual_receipts_equal(self):
        results=[]
        for role in pilot.ROLES[:2]:
            with tempfile.TemporaryDirectory() as temporary:
                path=Path(temporary);state=prepared(path)
                with patch.object(pilot,'native_plan',return_value=self.fixture_plan()),patch.object(task,'rows',return_value=copy.deepcopy(binding.PUBLIC_ROWS)):
                    value=pilot._finish(role,path,state)
                self.assertEqual(value['status'],'PILOT_RETENTION_ARTIFACT_VERIFIED')
                self.assertTrue(value['retired']);self.assertFalse(value['automatic_retry'])
                self.assertIsNone(value['monetary_cost_microunits'])
                self.assertEqual((path/'result/retention-index.csv').read_bytes(),binding.PUBLIC_EXPECTED.rsplit(b'END_G6_AUDIT',1)[0])
                results.append(value)
        for key in ('artifact_sha256','artifact_bytes','rows','source_files','input_sha256','stdout_sha256',
                    'authenticated_payload_sha256','retired','automatic_retry','model_invocations'):
            self.assertEqual(results[0][key],results[1][key])

    def test_equal_planned_interruption_never_promotes_output_to_completed_artifact(self):
        for role in pilot.ROLES[-2:]:
            with tempfile.TemporaryDirectory() as temporary:
                path=Path(temporary);state=prepared(path)
                with patch.object(pilot,'native_plan',return_value=self.fixture_plan()),patch.object(task,'rows',return_value=copy.deepcopy(binding.PUBLIC_ROWS)):
                    value=pilot._finish(role,path,state)
                self.assertEqual(value['status'],'INJECTED_FINALIZATION_INTERRUPTION')
                self.assertFalse(value['artifact_committed']);self.assertTrue(value['retired'])
                self.assertFalse((path/'result/retention-index.csv').exists())
                self.assertTrue((path/'result/stdout.bin').exists())

    def test_changed_output_and_input_or_nonquiescent_job_quarantine(self):
        for change in ('output','input','job'):
            with tempfile.TemporaryDirectory() as temporary:
                path=Path(temporary);state=prepared(path)
                if change=='output':state['stdout_sha256']='0'*64
                if change=='input':(path/'input/task.txt').write_bytes(b'PUBLIC CHANGED')
                if change=='job':state['job_active_after_termination']=1
                with patch.object(pilot,'native_plan',return_value=self.fixture_plan()):
                    value=pilot._finish(pilot.ROLES[0],path,state)
                self.assertEqual(value['status'],'QUARANTINE')
                self.assertFalse((path/'result/retention-index.csv').exists())

    def test_existing_artifact_is_preserved_and_quarantined_without_retry(self):
        with tempfile.TemporaryDirectory() as temporary:
            path=Path(temporary);state=prepared(path)
            (path/'result/retention-index.csv').write_bytes(b'PUBLIC PRESERVE')
            with patch.object(pilot,'native_plan',return_value=self.fixture_plan()):
                value=pilot._finish(pilot.ROLES[0],path,state)
            self.assertEqual(value['status'],'QUARANTINE')
            self.assertEqual((path/'result/retention-index.csv').read_bytes(),b'PUBLIC PRESERVE')

    def test_verification_only_checks_all_six_and_creates_nothing(self):
        with tempfile.TemporaryDirectory() as temporary,patch.object(pilot,'ROOT',Path(temporary)),patch.object(guard,'_verify_native_owner',return_value=('a'*64,1,2,3)) as verify:
            proof=pilot.verification_only()
            self.assertEqual(tuple(proof),pilot.ROLES)
            self.assertEqual([c.args[0] for c in verify.call_args_list],list(pilot.ROLES))
            self.assertEqual(list(Path(temporary).iterdir()),[])

    def test_verification_failure_does_not_reserve_or_dispatch(self):
        with tempfile.TemporaryDirectory() as temporary,patch.object(pilot,'ROOT',Path(temporary)),patch.object(guard,'_verify_native_owner',side_effect=ValueError('PUBLIC invalid')),patch.object(guard,'_fixed_attempt') as dispatch:
            with self.assertRaises(ValueError):pilot.run_once()
            dispatch.assert_not_called();self.assertEqual(list(Path(temporary).iterdir()),[])

    def test_existing_batch_cannot_repeat_even_verification(self):
        with tempfile.TemporaryDirectory() as temporary,patch.object(pilot,'ROOT',Path(temporary)),patch.object(guard,'_verify_native_owner') as verify:
            (Path(temporary)/pilot.BATCH).mkdir(parents=True)
            with self.assertRaises(ValueError):pilot.verification_only()
            verify.assert_not_called()

    def test_dispatch_without_active_batch_denies_before_any_signature_or_launch(self):
        with tempfile.TemporaryDirectory() as temporary,patch.object(pilot,'ROOT',Path(temporary)),patch.object(guard,'_verify_native_owner') as verify:
            with self.assertRaisesRegex(ValueError,'PILOT_BATCH_NOT_ACTIVE'):
                guard._fixed_attempt(pilot.ROLES[0],'qualification')
            verify.assert_not_called();self.assertEqual(list(Path(temporary).iterdir()),[])

    def test_retained_active_looking_files_cannot_restore_a_batch_after_restart(self):
        with tempfile.TemporaryDirectory() as temporary,patch.object(pilot,'ROOT',Path(temporary)):
            batch=Path(temporary)/pilot.BATCH;batch.mkdir(parents=True)
            (batch/'batch-reservation.json').write_bytes(b'{"PUBLIC":"stale"}')
            self.assertFalse(pilot._ACTIVE_BATCH)
            with self.assertRaisesRegex(ValueError,'PILOT_BATCH_NOT_ACTIVE'):
                pilot.dispatch_gate(pilot.ROLES[0])

    def test_fixed_dispatch_order_and_exact_predecessor_binding(self):
        with tempfile.TemporaryDirectory() as temporary,patch.object(pilot,'ROOT',Path(temporary)),patch.object(pilot,'_ACTIVE_BATCH',True):
            root=Path(temporary);batch=root/pilot.BATCH;batch.mkdir(parents=True)
            design=root/pilot.DESIGN;design.parent.mkdir(parents=True);design.write_bytes(b'PUBLIC DESIGN')
            payloads={}
            for role in pilot.ROLES:
                path=root/pilot.packet(role);path.parent.mkdir(parents=True);path.write_bytes(b'PUBLIC UNSIGNED '+role.encode())
                payloads[role]=hashlib.sha256(path.read_bytes()).hexdigest()
            (batch/'batch-reservation.json').write_text(json.dumps({'design_sha256':guard.normalized_sha(design),'payloads':payloads}),encoding='utf8')
            pilot.dispatch_gate(pilot.ROLES[0])
            with self.assertRaisesRegex(ValueError,'PILOT_ORDER_OR_REPLAY'):pilot.dispatch_gate(pilot.ROLES[1])
            result=root/pilot.work(pilot.ROLES[0])/'result';result.mkdir(parents=True)
            receipt={'slot':pilot.ROLES[0],'retired':True,'status':'PILOT_RETENTION_ARTIFACT_VERIFIED',
                'automatic_retry':False,'authenticated_payload_sha256':payloads[pilot.ROLES[0]],'job_active_after_termination':0}
            (result/'pilot-receipt.json').write_text(json.dumps(receipt),encoding='utf8')
            pilot.dispatch_gate(pilot.ROLES[1])
            receipt['authenticated_payload_sha256']='0'*64
            (result/'pilot-receipt.json').write_text(json.dumps(receipt),encoding='utf8')
            with self.assertRaisesRegex(ValueError,'PILOT_PREDECESSOR_NOT_ACCEPTED'):pilot.dispatch_gate(pilot.ROLES[1])

    def test_failed_slot_stops_and_retires_all_unused_slots(self):
        with tempfile.TemporaryDirectory() as temporary,patch.object(pilot,'ROOT',Path(temporary)):
            root=Path(temporary);proof={r:'a'*64 for r in pilot.ROLES}
            (root/'output').mkdir()
            design=root/pilot.DESIGN;design.parent.mkdir(parents=True);design.write_bytes(b'PUBLIC DESIGN FIXTURE')
            def dispatch(role,case):
                path=root/pilot.work(role);path.mkdir();(path/'result').mkdir()
                return {'status':'QUARANTINE','retired':True}
            with patch.object(pilot,'verification_only',return_value=proof),patch.object(guard,'_fixed_attempt',side_effect=dispatch) as launch:
                result=pilot.run_once()
            self.assertEqual(launch.call_count,1);self.assertEqual(result['status'],'PILOT_STOPPED')
            self.assertTrue(result['retired'])
            for role in pilot.ROLES[1:]:
                value=json.loads((root/pilot.work(role)/'disposition.json').read_bytes())
                self.assertTrue(value['retired']);self.assertEqual(value['reason'],'PILOT_NOT_DISPATCHED_BATCH_RETIRED')

    def test_dispatch_exception_remains_stopped_and_never_retried(self):
        with tempfile.TemporaryDirectory() as temporary,patch.object(pilot,'ROOT',Path(temporary)),patch.object(pilot,'verification_only',return_value={r:'a'*64 for r in pilot.ROLES}),patch.object(guard,'_fixed_attempt',side_effect=ValueError('PUBLIC failure')) as launch:
            (Path(temporary)/'output').mkdir()
            design=Path(temporary)/pilot.DESIGN;design.parent.mkdir(parents=True);design.write_bytes(b'PUBLIC DESIGN FIXTURE')
            with self.assertRaises(ValueError):pilot.run_once()
            self.assertEqual(launch.call_count,1)
            result=json.loads((Path(temporary)/pilot.BATCH/'pilot-result.json').read_bytes())
            self.assertEqual(result['status'],'PILOT_STOPPED');self.assertEqual(len(result['outcomes']),0)
            self.assertEqual(result['failure'],{'slot':pilot.ROLES[0],'stage':'GUARDED_DISPATCH','exception_class':'ValueError'})
            self.assertTrue(all((Path(temporary)/pilot.work(r)/'disposition.json').exists() for r in pilot.ROLES))

    def test_wrong_slot_signed_body_and_expired_or_future_window_fail_before_key_io(self):
        expected=pilot.owner_intent(pilot.ROLES[0]);now=int(time.time())
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);path=root/pilot.packet(pilot.ROLES[0]);path.parent.mkdir(parents=True)
            for change in ({'subject_id':'nexus.g3.subject.v1:'+'0'*64},{'expires_at':now-1},{'effective_at':now+60}):
                body=dict(expected,effective_at=now-60,expires_at=now+120,review_sha256='a'*64);body.update(change)
                path.write_bytes(json.dumps(body).encode())
                with patch.object(guard,'ROOT',root),patch.object(pilot,'owner_intent',return_value=expected),patch('scripts.verify_g3_owner_signature.github') as network:
                    with self.assertRaises(ValueError):guard._verify_native_owner(pilot.ROLES[0])
                    network.assert_not_called()

    def test_pilot_design_is_not_final_protocol_or_value_acceptance(self):
        design=json.loads((pilot.ROOT/pilot.DESIGN).read_bytes())
        self.assertEqual(design['slot_order'],list(pilot.ROLES))
        self.assertEqual(design['attempts'],6);self.assertFalse(design['automatic_retry'])
        self.assertEqual(design['final_comparison_protocol'],'NOT_PREREGISTERED')
        self.assertEqual(design['ties'],'NO_INCREMENTAL_BENEFIT')
        self.assertEqual(design['shared_safety_and_observer_credit'],'EXCLUDED_FROM_INCREMENTAL_NEXUS_BENEFIT')


if __name__=='__main__':unittest.main()

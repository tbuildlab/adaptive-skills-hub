"""Deterministic public composition tests; no native candidate execution."""
from pathlib import Path
import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from ash import g6_native_binding as binding


class FixedNativeBindingTests(unittest.TestCase):
    def test_exact_eight_plan_remains_nonexecutable(self):
        plan=binding.native_plan()
        self.assertEqual({m['path'] for m in plan['members']},binding.NATIVE)
        self.assertEqual(sum(m['bytes'] for m in plan['members']),14157312)
        self.assertEqual(plan['mode'],'FRESH_OWNER_SIGNATURE_REQUIRED')
        self.assertIs(plan['network'],False)
        self.assertIs(plan['automatic_retry'],False)
        self.assertEqual(plan['max_attempts'],1)
        self.assertNotIn(str(binding.PYTHON.parent),plan['filesystem'])
        self.assertEqual(plan['filesystem'][':root'],'deny')
        self.assertEqual(plan['unknown_partial_late'],'QUARANTINE')

    def test_only_fixed_public_case_before_any_host_action(self):
        for case in ('llama-completion.exe','../success','private','',None):
            with self.assertRaises(binding.BindingHold): binding.public_attempt(case)

    def test_native_role_consumes_exact_plan_and_excludes_fixture_runtime(self):
        plan=binding.native_plan(); binary=Path(plan['cwd'])
        argv,fs=binding._arguments(binary,binary.parent/'input',binary.parent/'result',
                                  'qualification',0,0,role='native')
        self.assertEqual(fs,plan['filesystem'])
        self.assertEqual(argv[argv.index('--')+1:],[plan['executable'],*plan['candidate_arguments']])
        self.assertNotIn(str(binding.PYTHON),argv)
        self.assertNotIn(str(binding.PYTHON.parent),fs)
        with self.assertRaises(binding.BindingHold):
            binding._arguments(Path('WRONG_BIN'),Path('INPUT'),Path('OUTPUT'),'qualification',0,0,role='native')

    @unittest.skipUnless(os.name=='nt','Windows native deny path')
    def test_missing_fresh_signature_denies_before_native_materialization(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(binding,'ROOT',Path(folder)):
            with patch.object(binding,'_prepare_native') as prepare:
                with self.assertRaises(ValueError): binding.native_attempt()
                prepare.assert_not_called()
                self.assertFalse((Path(folder)/binding.NATIVE_WORK).exists())

    @unittest.skipUnless(os.name=='nt','Windows native reservation')
    def test_native_reservation_denies_even_with_test_only_verifier_projection(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(binding,'ROOT',Path(folder)):
            reserved=Path(folder)/binding.NATIVE_WORK; reserved.mkdir(parents=True)
            with patch.object(binding,'_verify_native_owner',return_value=('TEST_ONLY',100,200,10)), \
                 patch.object(binding,'_prepare_native') as prepare:
                with self.assertRaisesRegex(binding.BindingHold,'ATTEMPT_RESERVED_NO_REPLAY'): binding.native_attempt()
                prepare.assert_not_called()

    def test_exact_resume_expiry_and_freshness_are_both_required(self):
        for now,monotonic in ((200,11),(99,11),(150,41)):
            with patch.object(binding.time,'time',return_value=now), patch.object(binding.time,'monotonic',return_value=monotonic):
                with self.assertRaises(binding.BindingHold): binding._native_resume_gate(('PUBLIC_DIGEST',100,200),10)
        with patch.object(binding.time,'time',return_value=199.9), patch.object(binding.time,'monotonic',return_value=11):
            binding._native_resume_gate(('PUBLIC_DIGEST',100,200),10)

    def test_relative_prompt_resolves_to_held_exact_input_without_permission_expansion(self):
        plan=binding.native_plan()
        relative=plan['candidate_arguments'][3]
        self.assertEqual(relative,'../input/task.txt')
        self.assertTrue(relative.isascii())
        self.assertEqual((Path(plan['cwd'])/relative).resolve(),Path(plan['input']).resolve())
        self.assertEqual(plan['filesystem'][Path(plan['input']).as_posix()],'read')
        self.assertNotIn(Path(plan['input']).parent.as_posix(),plan['filesystem'])

    def test_changed_relative_target_is_denied_before_launch(self):
        plan=binding.native_plan(); plan['candidate_arguments'][3]='../input/other.txt'
        binary=Path(plan['cwd'])
        with patch.object(binding,'native_plan',return_value=plan):
            with self.assertRaisesRegex(binding.BindingHold,'NATIVE_PROMPT_PATH_BINDING'):
                binding._arguments(binary,binary.parent/'input',binary.parent/'result','qualification',0,0,role='native')

    def test_retired_packet_and_directory_are_not_reused(self):
        for version,attempt in ((1,'private'),(2,'public')):
            self.assertNotEqual(binding.NATIVE_WORK,f'output/g6-native-{attempt}-once-v{version}')
            self.assertNotEqual(binding.OWNER_PACKET,f'output/g6-native-owner-signing-v{version}/decision.json')
            self.assertNotEqual(binding.OWNER_REVIEW,f'research/nexus-g6-fixed-native-independent-review-v{version}.json')
        self.assertEqual(binding.owner_intent()['subject']['revision'],'g6-fixed-native-binding-v3')

    def test_actual_retired_owner_payload_cannot_authorize_repaired_subject(self):
        expected=binding.owner_intent()
        for version in (1,2):
            old=(binding.ROOT/f'research/nexus-g6-native-owner-decision-v{version}.json').read_bytes()
            with patch.object(binding,'owner_intent',return_value=expected), \
                 patch.object(binding,'stable_read_bytes',return_value=old):
                with self.assertRaisesRegex(binding.BindingHold,'OWNER_EXACT_SUBJECT'):
                    binding._verify_native_owner()

    def test_substituted_public_probe_denies_before_copy_or_old_input_read(self):
        with tempfile.TemporaryDirectory() as folder, \
             patch.object(binding,'normalized_sha',return_value=binding.PUBLIC_PATH_SOURCE_SHA), \
             patch.object(binding,'stable_read_bytes',return_value=b'PUBLIC_CHANGED_BINARY'):
            with self.assertRaisesRegex(binding.BindingHold,'PUBLIC_PATH_BINARY'):
                binding._prepare_public_path_probe(Path(folder),Path(folder))
            self.assertEqual(list(Path(folder).iterdir()),[])

    def test_public_native_path_probe_has_no_model_candidate_or_python_allowance(self):
        directory=binding.ROOT/binding.WORK/'path_diagnostic'; binary=directory/'bin'
        args,fs=binding._arguments(binary,directory/'input',directory/'result','path_diagnostic',0,0)
        command=args[args.index('--')+1:]
        self.assertEqual(command[0],str(binary/'probe.exe'))
        self.assertEqual(command[-4:],['-f','../input/task.txt','-r',binding.EXPECTED_NATIVE_RESULT.decode()])
        self.assertNotIn(str(binding.PYTHON.parent),fs)
        self.assertNotIn(str(binding.PYTHON),args)
        self.assertTrue(all('model.gguf' not in name and 'native-private-once-v1/bin' not in name for name in fs))
        self.assertEqual(fs[binding.RETIRED_PUBLIC_INPUT.as_posix()],'read')
        self.assertEqual(fs[':root'],'deny')

    def test_fixed_framing_preserves_user_request_and_exact_vendor_lf_semantics(self):
        contract=json.loads((binding.ROOT/'research/nexus-g6-fixed-prompt-contract-v1.json').read_bytes())
        self.assertEqual(binding.MODEL_PROMPT,contract['model_prompt'].encode())
        self.assertEqual(binding.LEGACY_PUBLIC_PROMPT[:-1],contract['user_request'].encode())
        self.assertEqual(binding.NATIVE_PROMPT[:-1],binding.MODEL_PROMPT)
        self.assertNotEqual(binding.NATIVE_PROMPT.rstrip(b'\n'),binding.MODEL_PROMPT)
        self.assertEqual(binding.MODEL_PROMPT.count(b'<|im_start|>'),2)
        self.assertTrue(binding.MODEL_PROMPT.endswith(b'assistant\n<think>\n\n</think>\n\n'))
        self.assertEqual(contract['eos_token_id'],151645)
        self.assertEqual(contract['model_sha256'],binding.native_plan()['model']['sha256'])
        self.assertNotIn(b'\\n',binding.MODEL_PROMPT)

    def test_exact_output_rejects_wrong_prefix_trailing_eog_and_old_slash_result(self):
        marker=binding.EXPECTED_NATIVE_RESULT
        self.assertTrue(binding._native_result_matches(marker+b'\r\n'))
        for bad in (b'',b'wrong',b'prefix '+marker,marker+b' trailing',marker+b' [end of text]\n',
                    b'/\r\n'*127+b'\r\n\r\n',marker+marker):
            self.assertFalse(binding._native_result_matches(bad))

    def test_fixed_stop_does_not_trigger_from_prompt_history(self):
        marker=binding.EXPECTED_NATIVE_RESULT
        for history in (binding.MODEL_PROMPT,binding.MODEL_PROMPT.replace(b'<|im_start|>',b'').replace(b'<|im_end|>',b'')):
            for length in range(1,len(history)+1):
                suffix=history[-length:]
                self.assertEqual(suffix.find(marker,max(0,len(suffix)-len(marker)-2)),-1)
        self.assertGreaterEqual(marker.find(marker,max(0,len(marker)-len(marker)-2)),0)

    def test_stop_is_not_grammar_forcing_or_interactive_authority(self):
        args=binding.native_plan()['candidate_arguments']
        self.assertEqual(args[-2:],['-r',binding.EXPECTED_NATIVE_RESULT.decode()])
        self.assertIn('-no-cnv',args)
        self.assertNotIn('--grammar',args)
        self.assertNotIn('-i',args)
        self.assertNotIn('--interactive',args)

    def test_failure_diagnostics_keep_primary_timeout_and_do_not_disclose_messages(self):
        state={'reason':'TIMEOUT','status':'QUARANTINE'}
        binding._record_binding_failure(state,binding.BindingHold('HOST_CHANGED'),0)
        self.assertEqual(state['pre_failure_reason'],'TIMEOUT')
        self.assertEqual(state['binding_failure_code'],'HOST_CHANGED')
        self.assertEqual(state['status'],'QUARANTINE')
        for error in (binding.BindingHold('PUBLIC_UNREVIEWED_VALUE'),ValueError('PUBLIC_UNREVIEWED_VALUE')):
            state={'reason':'TIMEOUT'}; binding._record_binding_failure(state,error,0)
            self.assertNotIn('PUBLIC_UNREVIEWED_VALUE',json.dumps(state))
            self.assertEqual(state['binding_failure_code'],'OTHER_FAILURE')

    @unittest.skipUnless(os.name=='nt','Windows stable identity comparison')
    def test_every_host_identity_dimension_still_denies_with_boolean_only_diagnostics(self):
        import hashlib
        with tempfile.TemporaryDirectory() as folder:
            host=Path(folder)/'public-host'; raw=b'PUBLIC_HOST_FIXTURE';host.write_bytes(raw)
            digest=hashlib.sha256(raw).hexdigest(); before=(1,b'PUBLIC_ID',len(raw),100,1)
            for index in range(5):
                after=list(before);after[index]=b'CHANGED_ID' if index==1 else before[index]+1
                observed={}
                with patch.object(binding,'HOST',host),patch.object(binding,'HOST_SHA',digest), \
                     patch.object(binding.storage,'_win_identity',side_effect=[before,tuple(after)]):
                    with self.assertRaisesRegex(binding.BindingHold,'HOST_CHANGED'):
                        with binding._held_installed_host(host,digest,diagnostics=observed):pass
                self.assertEqual(sum(observed['host_identity_changed_fields'].values()),1)
                self.assertTrue(all(type(v) is bool for v in observed['host_identity_changed_fields'].values()))
                self.assertNotIn('CHANGED_ID',json.dumps(observed))

    def test_changed_loaded_binding_is_rejected(self):
        with patch.object(binding,'normalized_sha',return_value='0'*64):
            with self.assertRaisesRegex(binding.BindingHold,'LOADED_BINDING_REVISION_CHANGED'): binding._source_gate()

    def test_changed_owner_subject_or_material_rejected_before_crypto(self):
        expected={'subject':'PUBLIC_SUBJECT','material':{'file':'PUBLIC_HASH'}}
        for field in ('subject','material'):
            body={**expected,'effective_at':100,'expires_at':200,'review_sha256':'a'*64}
            body[field]='PUBLIC_CHANGED'
            with patch.object(binding,'owner_intent',return_value=expected), patch.object(binding,'stable_read_bytes',return_value=json.dumps(body).encode()):
                with self.assertRaisesRegex(binding.BindingHold,'OWNER_EXACT_SUBJECT'): binding._verify_native_owner()

    def test_rejected_native_signature_cannot_authenticate(self):
        from scripts import verify_g3_owner_signature as issuer
        expected={'subject':'PUBLIC_SUBJECT'}
        body={**expected,'effective_at':100,'expires_at':200,'review_sha256':'a'*64}
        review=json.dumps({'decision':'PASS_SIGNING_READINESS','binding_sha256':'a'*64}).encode()
        import hashlib
        body['review_sha256']=hashlib.sha256(review).hexdigest()
        def read(path,**kwargs):
            name=str(path)
            if name.endswith('decision.json'): return json.dumps(body).encode()
            if name.endswith('.json.sig'): return b'-----BEGIN SSH SIGNATURE-----\nPUBLIC_INVALID'
            if name.endswith('.pub'): return b'PUBLIC_TEST_KEY'
            return review
        with patch.object(binding,'owner_intent',return_value=expected), patch.object(binding,'stable_read_bytes',side_effect=read), \
             patch.object(binding,'normalized_sha',return_value='a'*64),patch.object(binding.time,'time',return_value=150), \
             patch.object(issuer,'public_key',return_value=('ssh-ed25519 PUBLIC_TEST','SHA256:5FV4/OvvMPzivK/4YIolW2kPQBGoik/llHbviTDpf98')), \
             patch.object(issuer,'github',side_effect=[{'id':223441940,'login':'TDY0225'},[{'id':1242636,'key':'ssh-ed25519 PUBLIC_TEST'}]]), \
             patch.object(binding.subprocess,'run',return_value=SimpleNamespace(returncode=1)):
            with self.assertRaisesRegex(binding.BindingHold,'OWNER_CRYPTOGRAPHIC_SIGNATURE'): binding._verify_native_owner()

    def test_child_environment_never_copies_dynamic_or_provider_settings(self):
        with patch.object(binding.os,'environ',{'GGML_BACKEND_PATH':'PUBLIC_POISON','LLAMA_ARG_MODEL':'PUBLIC_POISON',
                'HF_HOME':'PUBLIC_POISON','HTTP_PROXY':'PUBLIC_POISON','OPENAI_API_KEY':'PUBLIC_FAKE'}):
            env=binding._environment(Path('PUBLIC_RESULT'))
        self.assertTrue(all(n not in env for n in ('GGML_BACKEND_PATH','LLAMA_ARG_MODEL','HF_HOME','HTTP_PROXY','OPENAI_API_KEY')))
        self.assertEqual(env['PATH'],r'C:\Windows\System32')
        self.assertEqual(env['OTEL_SDK_DISABLED'],'true')

    def test_fixed_mxc_arguments_and_no_shell_or_fallback(self):
        args,fs=binding._arguments(Path('PUBLIC_BIN'),Path('PUBLIC_INPUT'),Path('PUBLIC_RESULT'),'io',1,1234)
        self.assertIn('windows.sandbox="mxc"',args)
        self.assertIn('permissions.g6fixed.network.enabled=false',args)
        self.assertIn('--include-managed-config',args)
        self.assertIn('shell_environment_policy.set.PATH="C:\\\\Windows\\\\System32"',args)
        self.assertEqual(fs[':root'],'deny')
        self.assertNotIn('write',fs.values())
        for item in binding.TELEMETRY: self.assertIn(item,args)
        self.assertNotIn('exec',args)

    def test_local_combined_collector_hard_retained_byte_cap(self):
        with tempfile.TemporaryDirectory() as folder:
            collector=binding._Collector(Path(folder))
            for channel in ('stdout.bin','stderr.bin'):
                read,write=os.pipe(); collector.start(read,channel)
                with os.fdopen(write,'wb',buffering=0) as stream: stream.write(b'P'*70000)
            self.assertTrue(collector.finish())
            self.assertTrue(collector.overflow.is_set())
            self.assertEqual(collector.count,binding.OUTPUT_LIMIT)
            self.assertEqual(sum(p.stat().st_size for p in Path(folder).iterdir()),binding.OUTPUT_LIMIT)

    def test_unknown_partial_audit_is_preserved_and_cannot_resume(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(binding,'ROOT',Path(folder)):
            path=Path(folder)/binding.WORK/'partial'; path.mkdir(parents=True)
            original=b'{"schema":'
            (path/'disposition.json').write_bytes(original)
            result=binding.reconcile_public('partial')
            self.assertEqual(result['status'],'QUARANTINE')
            self.assertIs(result['automatic_retry'],False)
            self.assertEqual((path/'disposition.json').read_bytes(),original)
            self.assertTrue((path/'reconciliation.json').is_file())

    @unittest.skipUnless(os.name=='nt','Windows reservation semantics')
    def test_existing_reservation_denies_before_fixture_or_host_launch(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(binding,'ROOT',Path(folder)):
            path=Path(folder)/binding.WORK/'success'; path.mkdir(parents=True)
            with patch.object(binding,'_arguments') as launch:
                with self.assertRaisesRegex(binding.BindingHold,'ATTEMPT_RESERVED_NO_REPLAY'):
                    binding.public_attempt('success')
                launch.assert_not_called()


if __name__=='__main__': unittest.main()

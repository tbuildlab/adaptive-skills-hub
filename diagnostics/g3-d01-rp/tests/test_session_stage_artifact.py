"""Synthetic continuity failures at each exchange; no live IO or authority."""
from pathlib import Path
import importlib.util, subprocess, tempfile, unittest
HERE = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('session_stage', HERE/'scripts/verify_session_stage.py')
M = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(M)
SPEC = importlib.util.spec_from_file_location('session_stage_tests_base', HERE/'tests/test_identity_stage_artifact.py')
B = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(B)
DATA = M.G3.reviewed_public_input()

class SessionStageArtifact(unittest.TestCase):
    def invoke(self, script):
        with tempfile.TemporaryDirectory(prefix='nexus-g3-session-stage-offline-') as directory:
            root = Path(directory)
            for n, b in M.compose(DATA).items():
                p = root/n; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(b)
            (root/'tests').mkdir()
            r = subprocess.run(['node', '--input-type=module', '-e', B.PREFIX+script],
                cwd=root/'tests', capture_output=True, timeout=20)
            self.assertEqual(r.returncode, 0, 'Synthetic stage assertion failed; raw output not retained')
    def continuity(self, stage):
        positions = {'TOTP_PRECHECK': (False, 0, 3), 'TOTP_REPLY': (True, 1, 4), 'TOTP_POSTCHECK': (True, 2, 5)}
        two, pos, count = positions[stage]
        self.invoke("const b=raw("+str(two).lower()+");b.session.session_id='fixture-other-session';"
            "const tail=[reply(raw()),reply(raw(true)),reply(raw(true))];tail["+str(pos)+"]=reply(b);"
            "const f=await primary(fixture([sent(),reply(raw()),...tail]));"
            "const o=await f.backend.TOTP_AUTHENTICATE({code:'000000'});deny(o);"
            "assert.equal(o.error_class,'IDENTITY_SESSION_"+stage+"');"
            "assert.equal(f.io.requestShapes().length,"+str(count)+");"
            "assert.equal(f.backend.contextInfo().retired,true);"
            "assert.equal(f.backend.contextInfo().expires_at,null);"
            "assert.equal(o.authority,'NONE');assert.equal(JSON.stringify(o).includes('fixture-other-session'),false);")
    def test_precheck_failure_stops_before_totp(self): self.continuity('TOTP_PRECHECK')
    def test_reply_failure_stops_before_postcheck(self): self.continuity('TOTP_REPLY')
    def test_postcheck_failure_retires_two_factor_context(self): self.continuity('TOTP_POSTCHECK')
    def test_same_session_still_passes(self):
        self.invoke("const f=await ready();assert.equal(f.backend.contextInfo().two,true);f.backend.retire();")
    def test_later_recheck_keeps_generic_label(self):
        self.invoke("const b=raw(true);b.session.session_id='fixture-other-session';const f=await ready([reply(b)]);"
            "const o=await f.backend.SESSION_AUTHENTICATE();deny(o);assert.equal(o.error_class,'IDENTITY_SESSION_CONTINUITY');")
    def test_token_change_still_denies(self):
        self.invoke("const b=raw(true);b.session_token='OFFLINE_OTHER_TOKEN';const f=await primary(fixture([sent(),reply(raw()),reply(raw()),reply(b)]));"
            "const o=await f.backend.TOTP_AUTHENTICATE({code:'000000'});deny(o);assert.equal(o.error_class,'IDENTITY_TOKEN_CONTINUITY');")
    def test_primary_time_change_still_denies(self):
        self.invoke("const b=raw(true);b.session.authentication_factors[0].last_authenticated_at=new Date(T-1000).toISOString();"
            "const f=await primary(fixture([sent(),reply(raw()),reply(raw()),reply(b)]));const o=await f.backend.TOTP_AUTHENTICATE({code:'000000'});deny(o);assert.equal(o.error_class,'IDENTITY_PRIMARY_TIME');")
    def test_fixed_wire_fields_unchanged(self):
        self.invoke("const f=await ready();assert.deepEqual(f.io.requestShapes().map(s=>s.keys),"
            "[['email','expiration_minutes','locale'],['code','method_id','session_duration_minutes'],['session_token'],"
            "['session_duration_minutes','session_token','totp_code','user_id'],['session_token']]);f.backend.retire();")
    def test_default_disabled_before_credentials(self):
        self.invoke("assert.equal(assertDisabled({mode:'D01_DIAGNOSTIC_LIVE_STYTCH'}),true);")
    def test_profiles_and_frozen_dependencies(self):
        for profile in M.PROFILES:
            report = M.validate(M.compose(DATA, profile), DATA, profile)
            self.assertEqual(report['files'], 20)
            self.assertEqual(report['identity_acceptance_predicates'], 'UNCHANGED')
    def test_mutation_rejected(self):
        blobs = M.compose(DATA); blobs[M.TRANSPORT] += b'\n// mutation\n'
        with self.assertRaises(RuntimeError): M.validate(blobs, DATA)
    def test_review_window_and_generations_preserved(self):
        old = M.BASE.validate(M.BASE.compose(DATA), DATA); new = M.validate(M.compose(DATA), DATA)
        for k in ('application_generation', 'registration_generation', 'public_review_valid_from', 'public_review_valid_until'):
            self.assertEqual(old[k], new[k])
    def test_fixed_client_labels(self):
        for label in M.ERRORS:
            self.assertIn(repr(label).encode(), M.compose(DATA)['public/app.js'])
            # Replay the existing closed client harness with only a fixed label.
            script = B.UI.CLIENT.replace("if(variant==='DENY'){response.result='DENY';response.error_class='AUTH_REJECTED';response.context_expires_at=null;}",
                "if(variant==='DENY'){response.result='DENY';response.error_class='"+label+"';response.context_expires_at=null;}")
            with tempfile.TemporaryDirectory(prefix='nexus-g3-session-stage-client-') as directory:
                root = Path(directory)
                for n, b in M.compose(DATA).items():
                    p = root/n; p.parent.mkdir(parents=True, exist_ok=True); p.write_bytes(b)
                r = subprocess.run(['node', '--input-type=module', '-e', script, 'DENY'], cwd=root, capture_output=True, timeout=20)
                self.assertEqual(r.returncode, 0, 'Synthetic closed-label UI failed')

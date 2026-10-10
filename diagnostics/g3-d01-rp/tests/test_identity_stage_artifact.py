"""Fixed-denial classification tests; fixtures are never live authority."""
from pathlib import Path
import importlib.util,subprocess,tempfile,unittest
HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('identity_stage',HERE/'scripts/verify_identity_stage.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
DATA=M.G3.reviewed_public_input()
PREFIX=(HERE/'tests/integration.test.js').read_text().split("test('01 current service")[0]
PREFIX=PREFIX.replace("import { createCustodyDryRun } from '../lib/server/custody-dry-run.js';",'')
SPEC=importlib.util.spec_from_file_location('existing_ui_tests',HERE/'tests/test_existing_totp_artifact.py')
UI=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(UI)

class IdentityStageArtifact(unittest.TestCase):
    def invoke(self,script):
        with tempfile.TemporaryDirectory(prefix='nexus-g3-identity-stage-offline-') as directory:
            root=Path(directory)
            for n,b in M.compose(DATA).items():
                p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
            (root/'tests').mkdir()
            r=subprocess.run(['node','--input-type=module','-e',script],cwd=root/'tests',capture_output=True,timeout=20)
            self.assertEqual(r.returncode,0,'Synthetic classification assertion failed; raw data not retained')
    def denied(self,mutation,expected):
        script=PREFIX+"const b=raw(true);"+mutation+";const f=await primary(fixture([sent(),reply(raw()),reply(raw()),reply(b)]));const o=await f.backend.TOTP_AUTHENTICATE({code:'000000'});deny(o);assert.equal(o.error_class,'"+expected+"');assert.equal(f.backend.contextInfo().retired,true);"
        self.invoke(script)
    def test_profiles_inventory(self):
        for p in M.PROFILES:self.assertEqual(M.validate(M.compose(DATA,p),DATA,p)['files'],20)
    def test_only_diagnostic_delta(self):
        old=M.BASE.compose(DATA);new=M.compose(DATA)
        self.assertEqual({n for n in new if new[n]!=old[n]},{M.G3.INPUT,M.G3.POLICY,M.TRANSPORT,'public/app.js'})
    def test_no_signature_projection_or_custody_change(self):
        old=M.BASE.compose(DATA);new=M.compose(DATA)
        for n in ('lib/stytch-identity.js','lib/stytch-projection.js',M.G3.CUSTODY,M.G3.SERVICE,'public/index.html'):self.assertEqual(old[n],new[n])
    def test_disabled_before_credentials(self):
        self.invoke(PREFIX+"assert.equal(assertDisabled({mode:'D01_DIAGNOSTIC_LIVE_STYTCH'}),true);")
    def test_normal_same_lineage_passes(self):
        self.invoke(PREFIX+"const f=await ready();assert.equal(f.backend.contextInfo().two,true);f.backend.retire();")
    def test_unknown_exception_stays_unknown(self):
        self.invoke(PREFIX+"const f=fixture([{failure:'FREE_TEXT_SYNTHETIC'}]);const o=await f.backend.EMAIL_OTP_SEND();deny(o);assert.equal(JSON.stringify(o).includes('FREE_TEXT'),false);")
    def test_mutation_blocked(self):
        b=M.compose(DATA);b['lib/stytch-identity.js']+=b'\n// mutation\n'
        with self.assertRaises(RuntimeError):M.validate(b,DATA)
    def test_review_and_generations_unchanged(self):
        old=M.BASE.validate(M.BASE.compose(DATA),DATA);new=M.validate(M.compose(DATA),DATA)
        for k in ('application_generation','registration_generation','public_review_valid_from','public_review_valid_until'):self.assertEqual(old[k],new[k])
    def test_current_client_all_classifications(self):
        for code in M.ERRORS:
            # Existing response projector must preserve fixed classifications only.
            script=UI.CLIENT.replace("if(variant==='DENY'){response.result='DENY';response.error_class='AUTH_REJECTED';response.context_expires_at=null;}","if(variant==='DENY'){response.result='DENY';response.error_class='"+code+"';response.context_expires_at=null;}")
            with tempfile.TemporaryDirectory(prefix='nexus-g3-stage-client-') as directory:
                root=Path(directory)
                for n,b in M.compose(DATA).items():
                    p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
                r=subprocess.run(['node','--input-type=module','-e',script,'DENY'],cwd=root,capture_output=True,timeout=20)
                self.assertEqual(r.returncode,0,'Synthetic fixed classification UI failed')

CASES={
 'jwt_missing':("delete b.session_jwt",'IDENTITY_JWT_SHAPE'),
 'jwt_oversize':("b.session_jwt='x'.repeat(16385)",'IDENTITY_JWT_SHAPE'),
 'jwt_malformed':("b.session_jwt='not-json.x.y'",'IDENTITY_JWT_JSON'),
 'jwt_wrong_issuer':("b.session_jwt=jwt({iss:'https://synthetic.invalid'})",'IDENTITY_SIGNED_PROOF'),
 'jwt_wrong_audience':("b.session_jwt=jwt({aud:'P_OTHER'})",'IDENTITY_SIGNED_PROOF'),
 'jwt_wrong_subject':("b.session_jwt=jwt({sub:'fixture-other'})",'IDENTITY_SIGNED_PROOF'),
 'jwt_expired':("b.session_jwt=jwt({exp:T/1000})",'IDENTITY_SIGNED_PROOF'),
 'token_missing':("delete b.session_token",'IDENTITY_TOKEN_SHAPE'),
 'token_malformed':("b.session_token='OFFLINE_invalid_token'",'IDENTITY_TOKEN_SHAPE'),
 'token_changed':("b.session_token='OFFLINE_OTHER_TOKEN'",'IDENTITY_TOKEN_CONTINUITY'),
 'session_changed':("b.session.session_id='fixture-other-session'",'IDENTITY_SESSION_CONTINUITY'),
 'email_time_changed':("b.session.authentication_factors[0].last_authenticated_at=new Date(T-1000).toISOString()",'IDENTITY_PRIMARY_TIME'),
 'native_user_changed':("b.user_id='fixture-other'",'IDENTITY_TOTP_RESPONSE'),
 'totp_id_missing':("delete b.totp_id",'IDENTITY_TOTP_RESPONSE'),
}
for name,(mutation,expected) in CASES.items():
    setattr(IdentityStageArtifact,'test_'+name,lambda self,m=mutation,e=expected:self.denied(m,e))

"""No-network adversarial qualification of the accepted diagnostic ceremony."""
from pathlib import Path
import importlib.util, subprocess, tempfile, unittest
HERE=Path(__file__).resolve().parents[1]
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
M=module('mfa_builder',HERE/'scripts/verify_mfa_transition.py')
B=module('mfa_fixture_parent',HERE/'tests/test_identity_stage_artifact.py')
DATA=M.G3.reviewed_public_input()
PREFIX=B.PREFIX+r'''
const originalRaw=raw;
raw=(...args)=>{
  const b=originalRaw(...args);
  b.session.authentication_factors[0].email_factor={email_id:'fixture-email'};
  b.user.totps=[{totp_id:'fixture-totp',verified:true}];
  if(args[0])b.session.authentication_factors[1].authenticator_app_factor={totp_id:'fixture-totp'};
  return b;
};
function transitioned(){const b=raw(true);b.session.session_id='fixture-final-session';b.session_token='OFFLINE_FINAL_TOKEN';return b;}
async function transition(tail=[]){
  const f=await primary(fixture([sent(),reply(raw()),reply(raw()),reply(transitioned()),reply(transitioned()),...tail]));
  pass(await f.backend.TOTP_AUTHENTICATE({code:'000000'}));return f;
}
'''

class MfaTransitionArtifact(unittest.TestCase):
    def invoke(self,script):
        with tempfile.TemporaryDirectory(prefix='nexus-g3-mfa-offline-') as d:
            root=Path(d)
            for n,b in M.compose(DATA).items():
                p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
            (root/'tests').mkdir()
            r=subprocess.run(['node','--input-type=module','-e',PREFIX+script],cwd=root/'tests',capture_output=True,timeout=20)
            self.assertEqual(r.returncode,0,'Synthetic MFA assertion failed; no raw reply retained')
    def candidate_deny(self,change):
        self.invoke("const b=transitioned();"+change+";const f=await primary(fixture([sent(),reply(raw()),reply(raw()),reply(b),reply(b)]));"
            "deny(await f.backend.TOTP_AUTHENTICATE({code:'000000'}));assert.equal(f.backend.contextInfo().retired,true);assert.equal(f.io.requestShapes().length,4);")
    def post_deny(self,change):
        self.invoke("const b=transitioned();"+change+";const f=await primary(fixture([sent(),reply(raw()),reply(raw()),reply(transitioned()),reply(b)]));"
            "deny(await f.backend.TOTP_AUTHENTICATE({code:'000000'}));assert.equal(f.backend.contextInfo().retired,true);assert.equal(f.io.requestShapes().length,5);")
    def test_transition_binds_final_only(self):
        self.invoke("const f=await transition([reply(transitioned())]);assert.equal(f.backend.contextInfo().two,true);pass(await f.backend.SESSION_AUTHENTICATE());assert.equal(f.backend.contextInfo().expires_at,T+300000);f.backend.retire();")
    def test_same_session_ceremony_remains_supported(self):
        self.invoke("const f=await ready();assert.equal(f.backend.contextInfo().two,true);f.backend.retire();")
    def test_once_only_and_no_second_totp_network(self):
        self.invoke("const f=await transition();deny(await f.backend.TOTP_AUTHENTICATE({code:'000000'}));assert.equal(f.io.requestShapes().length,5);assert.equal(f.backend.contextInfo().retired,true);")
    def test_post_context_old_session_denied(self):
        self.invoke("const f=await transition([reply(raw(true))]);const o=await f.backend.SESSION_AUTHENTICATE();deny(o);assert.equal(o.error_class,'IDENTITY_SESSION_CONTINUITY');")
    def test_post_context_replacement_denied(self):
        self.invoke("const b=transitioned();b.session.session_id='fixture-third-session';const f=await transition([reply(b)]);deny(await f.backend.SESSION_AUTHENTICATE());assert.equal(f.backend.contextInfo().retired,true);")
    def test_post_context_factor_reference_changed_denied(self):
        self.invoke("const b=transitioned();b.session.authentication_factors[0].email_factor.email_id='fixture-other';const f=await transition([reply(b)]);deny(await f.backend.SESSION_AUTHENTICATE());")
    def test_original_deadline_expiry(self):
        self.invoke("const f=await transition();f.time(T+300000);deny(await f.backend.SESSION_AUTHENTICATE());assert.equal(f.io.requestShapes().length,5);")
    def test_clock_rollback_denied(self):
        self.invoke("const f=await transition();f.time(T-1);deny(await f.backend.SESSION_AUTHENTICATE());")
    def test_no_public_candidate_or_bearer(self):
        self.invoke("const f=await transition();const o=await f.backend.SESSION_AUTHENTICATE();deny(o);assert.equal(JSON.stringify([o,f.backend.contextInfo(),f.backend]).includes('OFFLINE_FINAL_TOKEN'),false);assert.equal(JSON.stringify(o).includes('fixture-final-session'),false);")
    def test_browser_cannot_choose_candidate(self):
        self.invoke("const f=await primary(fixture([sent(),reply(raw())]));deny(await f.backend.TOTP_AUTHENTICATE({code:'000000',session_id:'fixture-final-session'}));assert.equal(f.io.requestShapes().length,2);")
    def test_missing_factor_id_primary_denied(self):
        self.invoke("const b=raw();delete b.session.authentication_factors[0].email_factor;const f=fixture([sent(),reply(b)]);pass(await f.backend.EMAIL_OTP_SEND());deny(await f.backend.EMAIL_OTP_AUTHENTICATE({code:'000000'}));")
    def test_wrong_method_primary_denied(self):
        self.invoke("const b=raw();b.session.authentication_factors[0].email_factor.email_id='fixture-other';const f=fixture([sent(),reply(b)]);pass(await f.backend.EMAIL_OTP_SEND());deny(await f.backend.EMAIL_OTP_AUTHENTICATE({code:'000000'}));")
    def test_precheck_replacement_stays_forbidden(self):
        self.invoke("const b=raw();b.session.session_id='fixture-other';const f=await primary(fixture([sent(),reply(raw()),reply(b)]));deny(await f.backend.TOTP_AUTHENTICATE({code:'000000'}));assert.equal(f.io.requestShapes().length,3);")
    def test_missing_enrolled_totp_denied(self):
        self.invoke("const b=raw();delete b.user.totps;const f=await primary(fixture([sent(),reply(raw()),reply(b)]));deny(await f.backend.TOTP_AUTHENTICATE({code:'000000'}));assert.equal(f.io.requestShapes().length,3);")
    def test_ambiguous_enrolled_totp_denied(self):
        self.invoke("const b=raw();b.user.totps.push({...b.user.totps[0]});const f=await primary(fixture([sent(),reply(raw()),reply(b)]));deny(await f.backend.TOTP_AUTHENTICATE({code:'000000'}));")
    def test_unverified_enrollment_denied(self):
        self.invoke("const b=raw();b.user.totps[0].verified=false;const f=await primary(fixture([sent(),reply(raw()),reply(b)]));deny(await f.backend.TOTP_AUTHENTICATE({code:'000000'}));")
    def test_remote_negative_never_uses_jwt_positive(self):
        self.invoke("const f=await primary(fixture([sent(),reply(raw()),reply(raw()),reply(transitioned()),{status:401,headers:{},chunks:[]}]));deny(await f.backend.TOTP_AUTHENTICATE({code:'000000'}));assert.equal(f.backend.contextInfo().two,false);")
    def test_time_precision_equivalent_normalization(self):
        self.invoke("const b=transitioned();b.session.authentication_factors[0].last_authenticated_at='2026-10-08T00:00:00.000000000Z';const f=await primary(fixture([sent(),reply(raw()),reply(raw()),reply(b),reply(b)]));pass(await f.backend.TOTP_AUTHENTICATE({code:'000000'}));")
    def test_final_revoke_uses_final_session(self):
        self.invoke("const f=await transition([reply({status_code:200})]);pass(await f.backend.SESSION_REVOKE_EXACT());assert.equal(f.io.requestShapes().at(-1).exact_session_id,'fixture-final-session');assert.equal(f.backend.contextInfo().retired,true);")
    def test_five_points_use_final_session_without_refresh(self):
        self.invoke("const f=await transition(POINTS.map(()=>reply(transitioned())));for(const p of POINTS)pass(await f.backend.SESSION_AUTHENTICATE());assert.equal(f.backend.contextInfo().expires_at,T+300000);for(const r of f.io.requestShapes().slice(4))assert.deepEqual(r.keys,['session_token']);")
    def test_profiles_frozen_authority_boundaries(self):
        for p in M.PROFILES:
            report=M.validate(M.compose(DATA,p),DATA,p)
            self.assertEqual(report['files'],20);self.assertEqual(report['authority'],'NONE')
    def test_default_disabled(self):self.invoke("assert.equal(assertDisabled({mode:'D01_DIAGNOSTIC_LIVE_STYTCH'}),true);")
    def test_fake_cannot_native_promote(self):
        self.invoke("const f=fixture();assert.equal(createProtectedStytchTransport({mode:'D01_DIAGNOSTIC_LIVE_STYTCH',io:f.io,credentials:f.input.credentials},reg()).mode,'FAKE_DISABLED');")
    def test_review_generations_unchanged(self):
        old=M.BASE.validate(M.BASE.compose(DATA),DATA);new=M.validate(M.compose(DATA),DATA)
        for k in ('application_generation','registration_generation','public_review_valid_from','public_review_valid_until'):self.assertEqual(old[k],new[k])
    def test_mutation_rejected(self):
        b=M.compose(DATA);b[M.TRANSPORT]+=b'\n// unreviewed\n'
        with self.assertRaises(RuntimeError):M.validate(b,DATA)

CANDIDATE_CASES={
 'wrong_project':"b.project_id='P_OTHER'",
 'wrong_native_user':"b.user_id='fixture-other'",
 'wrong_signed_issuer':"b.session_jwt=jwt({iss:'https://other.invalid'})",
 'wrong_signed_audience':"b.session_jwt=jwt({aud:'P_OTHER'})",
 'wrong_signed_subject':"b.session_jwt=jwt({sub:'fixture-other'})",
 'wrong_email_ref':"b.session.authentication_factors[0].email_factor.email_id='fixture-other'",
 'changed_primary_time':"b.session.authentication_factors[0].last_authenticated_at=new Date(T-1).toISOString()",
 'submillisecond_primary_change':"b.session.authentication_factors[0].last_authenticated_at='2026-10-08T00:00:00.000000001Z'",
 'wrong_totp_ref':"b.session.authentication_factors[1].authenticator_app_factor.totp_id='fixture-other'",
 'wrong_response_totp':"b.totp_id='fixture-other'",
 'missing_totp_ref':"delete b.session.authentication_factors[1].authenticator_app_factor",
 'stale_totp':"b.session.authentication_factors[1].last_authenticated_at=new Date(T-300000).toISOString()",
 'unverified_totp':"b.user.totps[0].verified=false",
 'duplicate_factor':"b.session.authentication_factors.push(b.session.authentication_factors[1])",
 'missing_primary_factor':"b.session.authentication_factors.shift()",
 'deleted_user':"b.user.status='deleted'",
 'malformed_bearer':"b.session_token='OFFLINE_invalid_fixture'",
}
POST_CASES={
 'session_replacement':"b.session.session_id='fixture-third-session'",
 'token_replacement':"b.session_token='OFFLINE_OTHER_TOKEN'",
 'primary_time_change':"b.session.authentication_factors[0].last_authenticated_at=new Date(T-1).toISOString()",
 'totp_precision_change':"b.session.authentication_factors[1].last_authenticated_at='2026-10-08T00:00:00.000000001Z'",
 'factor_id_change':"b.session.authentication_factors[0].email_factor.email_id='fixture-other'",
 'expiry_change':"b.session.expires_at=new Date(T+899000).toISOString()",
 'foreign_user':"b.user_id='fixture-other'",
}
for name,change in CANDIDATE_CASES.items():
    setattr(MfaTransitionArtifact,'test_candidate_'+name,lambda self,c=change:self.candidate_deny(c))
for name,change in POST_CASES.items():
    setattr(MfaTransitionArtifact,'test_postcheck_'+name,lambda self,c=change:self.post_deny(c))

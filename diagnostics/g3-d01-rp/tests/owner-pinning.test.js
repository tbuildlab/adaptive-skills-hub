import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import { createHash, generateKeyPairSync, sign } from 'node:crypto';
import https from 'node:https';
import { syncBuiltinESMExports } from 'node:module';
import { readFileSync } from 'node:fs';
import { DEPLOYMENT as D } from '../lib/server/deployment-input.js';
import { registerReviewedDeployment, createReviewedCurrentControl, currentControlRecord,
  registrationCurrent, registrationRecord, validateReviewedRegistration } from '../lib/server/provider-registration.js';
import { pinnedKeys, normalizeReviewedPublicJwks } from '../lib/server/pinned-identity.js';
import { verifyStytchIdentity } from '../lib/stytch-identity.js';
import { createDiagnosticHandler } from '../lib/server/diagnostic-service.js';
import { createProtectedStytchTransport } from '../lib/server/stytch-transport.js';
import { loadServerCredentials } from '../lib/server/credential-custody.js';
import { CODE_REVIEWED_LIVE_ENABLED, DEPLOYMENT_REGISTRATION_ENABLED, liveSelectionAllowed } from '../lib/server/pre-secret-policy.js';
const R=D.provider,K=D.keyset,N=K.valid_from,copy=v=>structuredClone(v);
const h=registerReviewedDeployment(R),current=currentControlRecord(createReviewedCurrentControl(h));
let calls=0;const originalHttps=https.request,originalFetch=globalThis.fetch;
https.request=()=>{calls++;throw Error('NETWORK_FORBIDDEN');};syncBuiltinESMExports();
globalThis.fetch=()=>{calls++;throw Error('NETWORK_FORBIDDEN');};
after(()=>{assert.equal(calls,0);https.request=originalHttps;syncBuiltinESMExports();globalThis.fetch=originalFetch;});
const {privateKey,publicKey}=generateKeyPairSync('rsa',{modulusLength:2048});
const fixtureKey={...publicKey.export({format:'jwk'}),kid:'fixture-review-key',alg:'RS256',use:'sig'};
// Test-only signatures never claim provider provenance, never leave this process
// and cannot enter the native factory or any Nexus authority record.
function synthetic(extra={},header={}) {
  const a=Buffer.from(JSON.stringify({alg:'RS256',kid:fixtureKey.kid,...header})).toString('base64url');
  const b=Buffer.from(JSON.stringify({iss:R.issuer,aud:R.audience,sub:R.owner_user_id,iat:N/1000,nbf:N/1000,exp:N/1000+200,...extra})).toString('base64url');
  return `${a}.${b}.${sign('RSA-SHA256',Buffer.from(`${a}.${b}`),privateKey).toString('base64url')}`;
}
const principal={...R,client_id:R.audience};
const verify=(extra={},remote=R.owner_user_id,header={})=>verifyStytchIdentity(synthetic(extra,header),principal,remote,[fixtureKey],N);
const pin=(change={})=>pinnedKeys({...copy(K),...change},R,N);
const badKey=(changes)=>{const value=copy(K);Object.assign(value.keys[0],changes);return pinnedKeys(value,R,N);};
const normalize=(key)=>normalizeReviewedPublicJwks({keys:[key]});
function bodyCheck(result){assert.ok(result.result==='DENY'&&result.authority==='NONE'&&result.real_admission==='DISABLED');}
async function request(body,headers={}) {
  const res={setHeader(){},end(text){this.body=JSON.parse(text);}};
  await createDiagnosticHandler()({method:body?'POST':'GET',url:'/api/diagnostic',body,headers:{host:'nexus-g3-qual.vercel.app',origin:R.origin,'content-type':'application/json',...headers}},res);
  return res.body;
}
test('R01 exact Owner tuple is pinned without duplicating native IDs in tests',()=>{
  assert.equal(createHash('sha256').update(R.project_id+'\n'+R.owner_user_id).digest('hex'),'1faf53124059cb6967aae8b0fd10f9e5547f249bce6720ae789d0ccd901a58df');
  assert.ok(validateReviewedRegistration(R)&&registrationCurrent(h,current));assert.ok(verify());
});
test('R02 different remote native user denied',()=>assert.equal(verify({},'fixture-other'),false));
test('R03 different project issuer denied',()=>assert.equal(verify({iss:'stytch.com/fixture-other'}),false));
test('R04 P_OTHER audience cannot become Owner',()=>assert.equal(verify({aud:'fixture-other-project'}),false));
test('R05 U_NONOWNER signed subject cannot become Owner',()=>assert.equal(verify({sub:'fixture-nonowner'}),false));
test('R06 email equality cannot substitute native subject',()=>assert.equal(verify({sub:'owner@example.invalid',email:'owner@example.invalid'}),false));
test('R07 display name cannot substitute native subject',()=>assert.equal(verify({sub:'Owner',name:'Owner'}),false));
test('R08 external_id cannot substitute native subject',()=>assert.equal(verify({sub:'fixture-alias',external_id:R.owner_user_id}),false));
test('R09 first successful synthetic login creates no registration authority',()=>{verify({sub:'fixture-first-login'});assert.ok(registrationRecord(h).owner_user_id===R.owner_user_id);assert.ok(Object.isFrozen(R)&&Object.isFrozen(R.factors));});
test('R10 browser cannot replace Owner',async()=>bodyCheck(await request({action:'EMAIL_OTP_SEND',owner_user_id:'fixture-other'})));
test('R11 browser cannot replace project',async()=>bodyCheck(await request({action:'EMAIL_OTP_SEND',project_id:'fixture-other'})));
for(const [n,field] of [[12,'owner_generation'],[13,'binding_generation'],[14,'application_generation']])test(`R${n} stale ${field} denied`,()=>assert.equal(registrationCurrent(h,{...current,[field]:0}),false));
test('R15 unknown/missing generation denied',()=>{assert.equal(registrationCurrent(h,{...current,application_generation:2}),false);const next=copy(current);delete next.application_generation;assert.equal(registrationCurrent(h,next),false);assert.equal(validateReviewedRegistration({...R,owner_generation:'1'}),false);});
test('R16 missing registration denied',()=>assert.equal(registerReviewedDeployment(null),null));
test('R17 malformed/extra alias registration denied',()=>{assert.equal(registerReviewedDeployment({...R,external_id:'fixture-alias'}),null);assert.equal(registerReviewedDeployment({...R,session_max_minutes:16}),null);});
test('R18 explicit unregistered delivery never gains live selection',()=>{assert.ok(R.delivery_email===null&&validateReviewedRegistration(R));assert.equal(liveSelectionAllowed(D,R),false);assert.equal(createProtectedStytchTransport(D,R).mode,'FAKE_DISABLED');});
test('R19 first bootstrap generation is fixed and all static control is immutable',()=>{
  assert.ok(D.registration_generation===1&&R.project_generation===1&&R.owner_generation===1&&R.binding_generation===1&&R.application_generation===1);
  assert.ok(Object.isFrozen(D)&&Object.isFrozen(K)&&Object.isFrozen(K.keys)&&K.keys.every(Object.isFrozen));
  assert.equal(registrationCurrent(h,{...current,deployment_revision:'fixture-stale'}),false);
});
test('J01 exact Owner public pin accepted structurally',()=>{
  assert.ok(pin());assert.equal(createHash('sha256').update(JSON.stringify(K.keys)).digest('hex'),'5794378f74deee81d960d1860d744a2eed08e6da108789444f04e089efa04dd3');
});
test('J02 wrong project binding denied',()=>assert.equal(pin({project_id:'fixture-other'}),null));
test('J03 wrong/unknown application generation denied',()=>{assert.equal(pin({application_generation:2}),null);assert.equal(pin({application_generation:null}),null);});
test('J04 unknown signing kid denied',()=>assert.equal(verify({},R.owner_user_id,{kid:'fixture-missing'}),false));
test('J05 duplicate kid denied by pinned profile',()=>assert.equal(pin({keys:[K.keys[0],K.keys[0]]}),null));
test('J06 ambiguous kid denied before signature trust',()=>{const jwt=synthetic();assert.equal(verifyStytchIdentity(jwt,principal,R.owner_user_id,[fixtureKey,fixtureKey],N),false);});
test('J07 non-RSA denied',()=>assert.equal(badKey({kty:'EC'}),null));
test('J08 non-RS256 denied',()=>assert.equal(badKey({alg:'HS256'}),null));
test('J09 use other than sig denied',()=>assert.equal(badKey({use:'enc'}),null));
test('J10 present key_ops must be exactly verify; normalized pin remains six-field profile',()=>{
  for(const ops of [[],['sign'],['verify','sign'],['verify','verify'],null,undefined])assert.equal(normalize({...K.keys[0],key_ops:ops}),null);
  assert.ok(normalize({...K.keys[0],key_ops:['verify']}));assert.deepEqual(Object.keys(K.keys[0]).sort(),['alg','e','kid','kty','n','use']);
});
test('J11 sub-2048 RSA denied',()=>{const key=generateKeyPairSync('rsa',{modulusLength:1024}).publicKey.export({format:'jwk'});assert.equal(normalize({...key,kid:'fixture-small',alg:'RS256',use:'sig'}),null);});
test('J12 every private RSA field denied without persistence',()=>{for(const field of ['d','p','q','dp','dq','qi','oth']){assert.equal(normalize({...K.keys[0],[field]:'OFFLINE_PRIVATE_FIELD_PLACEHOLDER'}),null);assert.equal(badKey({[field]:'OFFLINE_PRIVATE_FIELD_PLACEHOLDER'}),null);}});
test('J13 excessive keys denied',()=>{assert.equal(pin({keys:Array(9).fill(K.keys[0])}),null);assert.equal(normalizeReviewedPublicJwks({keys:Array(9).fill(K.keys[0])}),null);});
test('J14 oversized JWKS and modulus denied',()=>{assert.equal(normalizeReviewedPublicJwks({keys:[K.keys[0]],request_id:'x'.repeat(17000)}),null);assert.equal(badKey({n:'x'.repeat(1025)}),null);});
test('J15 remote key URL fields denied',()=>{for(const name of ['x5u','jku','url'])assert.equal(normalize({...K.keys[0],[name]:'https://other.invalid'}),null);});
test('J16 browser provenance key source denied',()=>assert.equal(pin({source:'BROWSER_PROVIDED'}),null));
test('J17 discovery and TOFU source denied',()=>{assert.equal(pin({source:'TOFU'}),null);assert.equal(pin({url:'https://other.invalid'}),null);});
test('J18 expired review window denied; not automatically renewed',()=>{assert.equal(pinnedKeys(K,R,K.valid_until),null);assert.equal(D.keyset.valid_from,N);});
test('J19 future-invalid/reversed/overlong window denied',()=>{for(const values of [{valid_from:N+1},{valid_until:N-1},{valid_until:N+86400001}])assert.equal(pin(values),null);});
test('J20 malformed or non-canonical JWK denied',()=>{for(const key of [null,{}, {...K.keys[0],n:'!'}, {...K.keys[0],e:'AQAB='}])assert.equal(normalize(key),null);});
test('J21 request/status envelope metadata omitted from exact normalized public pin',()=>{
  const keys=normalizeReviewedPublicJwks({keys:[{...K.keys[0],key_ops:['verify']}],request_id:'fixture-envelope',status_code:200});
  assert.ok(keys);assert.equal(JSON.stringify(keys),JSON.stringify(K.keys));assert.equal(JSON.stringify(D).includes('fixture-envelope'),false);
});
test('J22 certificate/thumbprint are bounded consistency metadata, not accepted remote authority',()=>{
  assert.equal(normalize({...K.keys[0],x5c:['INVALID_CERT']}),null);
  assert.equal(normalize({...K.keys[0],x5tS256:'a'.repeat(43)}),null);
  assert.equal(normalize({...K.keys[0],x5c:Array(4).fill('AAAA')}),null);
  assert.equal(normalize({...K.keys[0],x5c:['A'.repeat(6145)]}),null);
  assert.equal(JSON.stringify(K).includes('x5c'),false);assert.equal(JSON.stringify(K).includes('key_ops'),false);
});
test('A01 exact pinned inputs cannot activate default assembly',async()=>{assert.equal(D.mode,'FAKE_DISABLED');bodyCheck(await request());});
test('A02 both compile gates remain literal false',()=>{assert.equal(CODE_REVIEWED_LIVE_ENABLED,false);assert.equal(DEPLOYMENT_REGISTRATION_ENABLED,false);});
test('A03 credential-loader function returns before inspecting poisoned configuration',()=>{const poison=new Proxy({}, {get(){throw Error('OFFLINE_CREDENTIAL_ACCESS');}});assert.equal(loadServerCredentials(poison,poison),null);});
test('A04 native transport is never called while registered disabled',()=>{assert.equal(createProtectedStytchTransport(D,R).mode,'FAKE_DISABLED');assert.equal(calls,0);});
test('A05 browser mode cannot activate',async()=>bodyCheck(await request({mode:'D01_DIAGNOSTIC_LIVE_STYTCH'})));
test('A06 browser keyset cannot replace server pin',async()=>bodyCheck(await request({action:'EMAIL_OTP_SEND',keyset:{source:'BROWSER'}})));
test('A07 Preview and registration presence remain disabled',()=>{assert.equal(liveSelectionAllowed({...D,deployment_tier:'PREVIEW'},R),false);assert.equal(liveSelectionAllowed({...D,mode:'D01_DIAGNOSTIC_LIVE_STYTCH'},R),false);});
test('A08 synthetically named credential presence cannot activate or be read',()=>{const configuration={...D};Object.defineProperty(configuration,'STYTCH_SECRET',{get(){throw Error('OFFLINE_MUST_NOT_READ');}});assert.equal(createProtectedStytchTransport(configuration,R).mode,'FAKE_DISABLED');});
test('A09 immutable registered native identity never enters sanitized response',async()=>{const response=JSON.stringify(await request());assert.ok(!response.includes(R.owner_user_id)&&!response.includes(R.project_id)&&!response.includes(K.review_id));});
test('A10 public sources contain no native identity/provenance or server imports',()=>{
  for(const path of ['public/app.js','public/index.html','future-deployment/app.js','future-deployment/index.html','future-deployment/owner-transient.js']) {
    const source=readFileSync(new URL('../'+path,import.meta.url),'utf8');
    assert.ok(!source.includes(R.owner_user_id)&&!source.includes(R.project_id)&&!source.includes(K.review_id));
    assert.equal(/lib\/server|process\.env|credential-custody/.test(source),false);
  }
});
test('A11 no authority serialization or positive admission exists',async()=>{bodyCheck(await request({action:'CLAIM_SIMULATION'}));assert.equal(JSON.stringify(h),'{"authority":"NONE"}');});
test('A12 network/provider call count remains zero',()=>assert.equal(calls,0));

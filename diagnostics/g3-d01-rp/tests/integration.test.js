import test, { after } from 'node:test';
import assert from 'node:assert/strict';
import https from 'node:https';
import { syncBuiltinESMExports } from 'node:module';
import { generateKeyPairSync, sign, randomBytes } from 'node:crypto';
import { readFileSync, writeFileSync, unlinkSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { runInNewContext } from 'node:vm';
import { createDiagnosticHandler, createOfflineDiagnosticHandler } from '../lib/server/diagnostic-service.js';
import { createOfflineRegistration, createOfflineCurrentControl } from '../lib/server/provider-registration.js';
import { createOfflineCredentials } from '../lib/server/credential-custody.js';
import { createOfflineIo, createOfflineStytchTransport, createProtectedStytchTransport } from '../lib/server/stytch-transport.js';
import { pinnedKeys } from '../lib/server/pinned-identity.js';
import { createCustodyDryRun } from '../lib/server/custody-dry-run.js';
import { POINTS } from '../lib/policy.js';
const read=p=>readFileSync(new URL('../'+p,import.meta.url),'utf8');
let networkCalls=0;const savedRequest=https.request,savedFetch=globalThis.fetch;
https.request=()=>{networkCalls++;throw Error('NETWORK_FORBIDDEN');};syncBuiltinESMExports();
globalThis.fetch=()=>{networkCalls++;throw Error('NETWORK_FORBIDDEN');};
after(()=>{assert.equal(networkCalls,0);https.request=savedRequest;syncBuiltinESMExports();globalThis.fetch=savedFetch;});
const T=Date.UTC(2026,9,8),project='project-test-00000000-0000-4000-8000-000000000001';
const {privateKey,publicKey}=generateKeyPairSync('rsa',{modulusLength:2048});
const jwk={...publicKey.export({format:'jwk'}),kid:'fixture-integration',alg:'RS256',use:'sig'};
const reg=()=>({provider:'STYTCH_CONSUMER',environment:'TEST',project_id:project,owner_user_id:'fixture-owner',
  project_generation:1,application_generation:1,owner_generation:1,binding_generation:1,
  origin:'https://nexus-g3-qual.vercel.app',factors:['EMAIL_OTP','TOTP'],session_max_minutes:15,context_max_ms:300000,
  issuer:`stytch.com/${project}`,audience:project,deployment_revision:'fixture-revision',source:'OFFLINE_SYNTHETIC',
  review_id:'fixture-review',delivery_email:'owner@example.invalid'});
const keyset=()=>({source:'OWNER_REVIEWED_STYTCH_TEST_PROJECT_KEYSET',project_id:project,application_generation:1,
  review_id:'fixture-key-review',valid_from:T,valid_until:T+3600000,keys:[jwk]});
function jwt(extra={},header={}) {
  const h=Buffer.from(JSON.stringify({alg:'RS256',typ:'JWT',kid:jwk.kid,...header})).toString('base64url');
  const c=Buffer.from(JSON.stringify({iss:`stytch.com/${project}`,aud:project,sub:'fixture-owner',iat:T/1000,nbf:T/1000,exp:T/1000+300,...extra})).toString('base64url');
  return `${h}.${c}.${sign('RSA-SHA256',Buffer.from(`${h}.${c}`),privateKey).toString('base64url')}`;
}
function raw(two=false,extra={},header={}) {
  const authentication_factors=[{type:'otp',delivery_method:'email',last_authenticated_at:new Date(T).toISOString()}];
  if(two)authentication_factors.push({type:'totp',delivery_method:'authenticator_app',last_authenticated_at:new Date(T).toISOString()});
  return {status_code:200,user_id:'fixture-owner',method_id:'fixture-email',totp_id:'fixture-totp',
    session_token:'OFFLINE_SESSION_PLACEHOLDER',session_jwt:jwt(extra,header),
    user:{user_id:'fixture-owner',status:'active',is_locked:false},
    session:{user_id:'fixture-owner',session_id:'fixture-session',expires_at:new Date(T+900000).toISOString(),authentication_factors}};
}
const reply=body=>({status:200,headers:{'content-type':'application/json'},chunks:[JSON.stringify(body)]});
const sent=()=>reply({status_code:200,user_id:'fixture-owner',email_id:'fixture-email'});
const enrollment=()=>reply({status_code:200,user_id:'fixture-owner',user:{user_id:'fixture-owner'},totp_id:'fixture-totp',
  secret:'OFFLINE_TOTP_SEED',qr_code:'OFFLINE_QR',recovery_codes:['OFFLINE_RECOVERY']});
function fixture(replies=[sent()],changes={}) {
  const r=reg(),registration=createOfflineRegistration(r);
  const current=createOfflineCurrentControl(Object.fromEntries(['project_id','owner_user_id','project_generation',
    'application_generation','owner_generation','binding_generation','deployment_revision'].map(k=>[k,r[k]])));
  const credentials=createOfflineCredentials({STYTCH_PROJECT_ID:project,STYTCH_SECRET:'OFFLINE_CREDENTIAL_PLACEHOLDER'},registration);
  const io=createOfflineIo(replies,true);let now=T;
  const input={registration,current,credentials,io,keyset:keyset(),publicKeys:[jwk],clock:()=>now,ownerChannel:true,...changes};
  return {backend:createOfflineStytchTransport(input),handler:createOfflineDiagnosticHandler(input),io,input,time:n=>{now=n;}};
}
function deny(o){assert.equal(o.result,'DENY');assert.equal(o.real_admission,'DISABLED');assert.equal(o.qualified_live,false);}
function pass(o){assert.equal(o.result,'PASS');assert.equal(o.authority,'NONE');assert.equal(o.qualified_live,false);}
async function primary(f){pass(await f.backend.EMAIL_OTP_SEND());pass(await f.backend.EMAIL_OTP_AUTHENTICATE({code:'000000'}));return f;}
async function ready(tail=[]) {const f=await primary(fixture([sent(),reply(raw()),reply(raw()),reply(raw(true)),reply(raw(true)),...tail]));pass(await f.backend.TOTP_AUTHENTICATE({code:'000000'}));return f;}
async function request(handler,method='GET',body,extra={}) {
  const res={headers:{},setHeader(k,v){this.headers[k]=v;},end(value){this.text=value;}};
  await handler({method,url:'/api/diagnostic',body,headers:{host:'nexus-g3-qual.vercel.app',origin:'https://nexus-g3-qual.vercel.app',
    ...(method==='POST'?{'content-type':'application/json'}:{}),...extra}},res);
  if(res.headers['Content-Type'].startsWith('application/json'))res.json=JSON.parse(res.text);return res;
}
function assertDisabled(config={},registration=reg()){return createProtectedStytchTransport(config,registration).mode==='FAKE_DISABLED';}
test('01 current service mode remains FAKE_DISABLED',async()=>{const r=await request(createDiagnosticHandler());assert.equal(r.json.adapter_mode,'FAKE_DISABLED');deny(r.json);});
test('02 secret presence alone cannot enable live',()=>assert.equal(assertDisabled({STYTCH_SECRET:'OFFLINE_CREDENTIAL_PLACEHOLDER'}),true));
test('03 project presence alone cannot enable live',()=>assert.equal(assertDisabled({STYTCH_PROJECT_ID:project}),true));
test('04 credentials with wrong mode disabled',()=>assert.equal(assertDisabled({mode:'LIVE',STYTCH_SECRET:'OFFLINE_CREDENTIAL_PLACEHOLDER'}),true));
test('05 missing registration disabled without inspection',()=>assert.equal(assertDisabled({mode:'D01_DIAGNOSTIC_LIVE_STYTCH'},null),true));
test('06 stale registration generation disabled',()=>assert.equal(assertDisabled({mode:'D01_DIAGNOSTIC_LIVE_STYTCH',registration_generation:2}),true));
test('07 browser cannot select live mode',async()=>{const r=await request(createDiagnosticHandler(),'POST',{action:'LIVE',mode:'D01_DIAGNOSTIC_LIVE_STYTCH'});deny(r.json);});
test('08 browser cannot select project',async()=>{deny(await fixture().backend.EMAIL_OTP_SEND({project_id:project}));});
test('09 browser cannot select JWKS',()=>assert.equal(pinnedKeys({...keyset(),url:'https://other.invalid'},reg(),T),null));
test('10 arbitrary endpoint rejects before IO',async()=>{const f=fixture();deny(await f.backend.EMAIL_OTP_SEND({endpoint:'/v1/users'}));assert.equal(f.io.requestShapes().length,0);});
test('11 arbitrary host rejects before IO',async()=>{deny(await fixture().backend.EMAIL_OTP_SEND({host:'other.invalid'}));});
test('12 native parser rejects redirect',async()=>{const f=fixture([{status:302,headers:{},chunks:[]}]);deny(await f.backend.EMAIL_OTP_SEND());assert.equal(f.io.requestShapes().length,1);});
test('13 native parser timeout fixture denies',async()=>{deny(await fixture([{failure:'TIMEOUT'}]).backend.EMAIL_OTP_SEND());});
test('14 native parser malformed JSON denies',async()=>{deny(await fixture([{status:200,headers:{'content-type':'application/json'},chunks:['{']}]).backend.EMAIL_OTP_SEND());});
test('15 native stream oversized response denies',async()=>{deny(await fixture([{status:200,headers:{'content-type':'application/json'},chunks:['x'.repeat(40000),'x'.repeat(40000)]}]).backend.EMAIL_OTP_SEND());});
test('16 raw provider error is never projected',async()=>{const r=await fixture([{status:503,headers:{},chunks:['OFFLINE_RAW_ERROR_SENTINEL']}]).backend.EMAIL_OTP_SEND();deny(r);assert.equal(JSON.stringify(r).includes('SENTINEL'),false);});
test('17 unknown status denies and retires',async()=>{const f=fixture([{status:299,headers:{},chunks:[]}]);deny(await f.backend.EMAIL_OTP_SEND());deny(await f.backend.EMAIL_OTP_SEND());});
test('18 initial OTP authentication uses fixed 15 minutes',async()=>{const f=await primary(fixture([sent(),reply(raw())]));assert.equal(f.io.requestShapes()[1].duration,15);f.backend.retire();});
test('19 fresh remote recheck cannot extend session',async()=>{const f=await ready([reply(raw(true))]);pass(await f.backend.SESSION_AUTHENTICATE());assert.deepEqual(f.io.requestShapes().at(-1).keys,['session_token']);f.backend.retire();});
for(const [n,field,value] of [[20,'user_id','fixture-other'],[21,'session_id','fixture-other-session']])test(`${n} TOTP ${field} mismatch retires`,async()=>{
  const b=raw(true);b.session[field]=value;const f=await primary(fixture([sent(),reply(raw()),reply(raw()),reply(b)]));deny(await f.backend.TOTP_AUTHENTICATE({code:'000000'}));});
test('22 stale TOTP factor denies',async()=>{const b=raw(true);b.session.authentication_factors[1].last_authenticated_at=new Date(T-300000).toISOString();const f=await primary(fixture([sent(),reply(raw()),reply(raw()),reply(b)]));deny(await f.backend.TOTP_AUTHENTICATE({code:'000000'}));});
test('23 enrollment cannot extend OwnerContext deadline',async()=>{const f=await primary(fixture([sent(),reply(raw()),reply(raw()),enrollment(),reply(raw())]));pass(await f.backend.TOTP_CREATE());assert.equal(f.backend.contextInfo().expires_at,T+300000);f.time(T+300000);assert.equal(f.backend.contextInfo().retired,true);});
test('24 HTTP reload preserves original deadline',async()=>{const f=fixture();const first=await request(f.handler);const cookie=first.headers['Set-Cookie'].split(';')[0];f.time(T+1000);const second=await request(f.handler,'GET',undefined,{cookie});assert.equal(second.json.context_expires_at,first.json.context_expires_at);});
test('25 new worker retires old page cookie',async()=>{const first=await request(fixture().handler);const next=await request(fixture().handler,'GET',undefined,{cookie:first.headers['Set-Cookie'].split(';')[0]});deny(next.json);});
test('26 JWT-positive remote-negative is never positive',async()=>{const b=raw(true);b.user.status='deleted';const f=await ready([reply(b)]);deny(await f.backend.SESSION_AUTHENTICATE());});
for(const [n,field,value] of [[27,'iss','https://invented.invalid'],[28,'aud','P_OTHER'],[29,'sub','fixture-other']])test(`${n} wrong signed ${field} denies`,async()=>{const f=fixture([sent(),reply(raw(false,{[field]:value}))]);pass(await f.backend.EMAIL_OTP_SEND());deny(await f.backend.EMAIL_OTP_AUTHENTICATE({code:'000000'}));});
test('30 unknown kid denies',async()=>{const f=fixture([sent(),reply(raw(false,{}, {kid:'missing'}))]);pass(await f.backend.EMAIL_OTP_SEND());deny(await f.backend.EMAIL_OTP_AUTHENTICATE({code:'000000'}));});
test('31 ambiguous signing key denies registration',()=>assert.equal(pinnedKeys({...keyset(),keys:[jwk,jwk]},reg(),T),null));
test('32 unauthorized key source, stale keys and wrong project deny',()=>{for(const k of [{...keyset(),source:'BROWSER'}, {...keyset(),project_id:'P_OTHER'}, {...keyset(),valid_until:T}])assert.equal(pinnedKeys(k,reg(),T),null);});
test('33 P_OTHER cannot become Owner',async()=>{const f=fixture([reply({status_code:200,user_id:'fixture-foreign',email_id:'fixture-email'})]);deny(await f.backend.EMAIL_OTP_SEND());});
test('34 email equality cannot become Owner',async()=>{const b=raw(false,{sub:'fixture-nonowner'});b.user_id='fixture-nonowner';b.user.user_id='fixture-nonowner';b.session.user_id='fixture-nonowner';b.user.email='owner@example.invalid';const f=fixture([sent(),reply(b)]);pass(await f.backend.EMAIL_OTP_SEND());deny(await f.backend.EMAIL_OTP_AUTHENTICATE({code:'000000'}));});
test('35 client sources cannot read loader or environment',()=>{for(const p of ['future-deployment/app.js','future-deployment/owner-transient.js'])assert.equal(/credential-custody|lib\/server|process\.env|STYTCH_SECRET/.test(read(p)),false);});
const output=fileURLToPath(new URL('../../../state/g3-d01-integration-20261008/test-artifact/',import.meta.url));
let metadata;
test('36 independent deployment artifact includes credential loader source',()=>{
  const run=spawnSync('D:\\DevTools\\NexusR2Python\\Scripts\\python.exe',['-B',fileURLToPath(new URL('../scripts/verify_deployment.py',import.meta.url)),'--output',output],{encoding:'utf8'});
  assert.equal(run.status,0);metadata=JSON.parse(readFileSync(output+'artifact-metadata.json','utf8'));assert.equal(metadata.credential_loader_source_included,true);assert.equal(metadata.deployment_requires_repository_manifest,false);
});
test('37 artifact has no environment files',()=>assert.equal(Object.keys(metadata.files).some(p=>p.split('/').some(n=>n.startsWith('.env'))),false));
test('38 artifact has no OIDC/account metadata',()=>assert.equal(Object.keys(metadata.files).some(p=>/\.vercel|OIDC|state|ash|Route/.test(p)),false));
const sentinel='OFFLINE_SENTINEL_'+randomBytes(12).toString('hex').toUpperCase();
const dry=createCustodyDryRun();dry.ownerSet(sentinel);dry.ownerDeploy();
test('39 runtime secret sentinel absent from every client source',()=>{for(const p of ['future-deployment/app.js','future-deployment/owner-transient.js','future-deployment/index.html'])assert.equal(read(p).includes(sentinel),false);});
test('40 runtime secret sentinel absent from log outputs',()=>assert.equal(JSON.stringify(dry.outputs().logs).includes(sentinel),false));
test('41 runtime secret sentinel absent from responses, headers, errors and HTML',async()=>{const r=await request(createDiagnosticHandler());assert.equal(JSON.stringify([dry.outputs().response,dry.outputs().headers,r]).includes(sentinel),false);});
test('42 runtime secret sentinel absent from evidence and artifact metadata',()=>assert.equal(JSON.stringify([dry.outputs().evidence,metadata]).includes(sentinel),false));
test('43 Preview cannot activate native service',()=>assert.equal(assertDisabled({mode:'D01_DIAGNOSTIC_LIVE_STYTCH',deployment_tier:'PREVIEW',registration_generation:1}),true));
test('44 fake adapter cannot be production promoted',()=>{const f=fixture();assert.equal(createProtectedStytchTransport({mode:'D01_DIAGNOSTIC_LIVE_STYTCH',io:f.io,credentials:f.input.credentials},reg()).mode,'FAKE_DISABLED');});
test('45 diagnostic source closure has no production authority imports',()=>{for(const p of Object.keys(metadata.files).filter(p=>p.endsWith('.js')&&!p.startsWith('public/')))assert.equal(/from\s*['"][^'"]*(?:ash|g3_production|approval|admission|dispatch)/.test(readFileSync(output+'source/'+p,'utf8')),false);});
test('46 no real receipt/grant/intent/claim/effect factories',()=>{for(const p of ['lib/server/diagnostic-service.js','lib/server/stytch-transport.js'])assert.equal(/TrustedDecisionReceipt|ApprovalGrant|AdmissionIntent|DispatchAttempt/.test(read(p)),false);});
test('47 real admission remains disabled in composed HTTP entrypoint',async()=>{const r=await request(createDiagnosticHandler());assert.equal(r.json.real_admission,'DISABLED');assert.equal(r.json.authority,'NONE');});
test('48 NETWORK_CALL_COUNT remains zero with native parser fixtures',()=>assert.equal(networkCalls,0));
test('complete OTP/TOTP Owner HTML and five-label flow is one lineage only',async()=>{
  const f=fixture([sent(),reply(raw()),reply(raw()),enrollment(),reply(raw()),reply(raw()),reply(raw()),reply(raw(true)),reply(raw(true)),...POINTS.map(()=>reply(raw(true))),reply({status_code:200})]);
  const get=await request(f.handler);const cookie=get.headers['Set-Cookie'].split(';')[0];const csrf=get.json.csrf;
  const headers={cookie,'x-g3-csrf':csrf};
  for(const action of ['EMAIL_OTP_SEND','EMAIL_OTP_AUTHENTICATE','TOTP_CREATE'])pass((await request(f.handler,'POST',{action,...(action==='EMAIL_OTP_AUTHENTICATE'?{code:'000000'}:{})},headers)).json);
  const owner=await request(f.handler,'POST',{action:'OWNER_TOTP_DISPLAY',csrf},{cookie,'content-type':'application/x-www-form-urlencoded'});
  assert.equal(owner.headers['Content-Type'],'text/html; charset=utf-8');assert.equal(owner.text.includes('OFFLINE_TOTP_SEED'),true);
  assert.equal(owner.text.includes('OFFLINE_CREDENTIAL_PLACEHOLDER'),false);
  pass((await request(f.handler,'POST',{action:'TOTP_AUTHENTICATE',code:'000000'},headers)).json);
  for(const action of POINTS)pass((await request(f.handler,'POST',{action},headers)).json);
  pass((await request(f.handler,'POST',{action:'SESSION_REVOKE_EXACT'},headers)).json);
});
test('Owner channel is one-use, wrong CSRF retires, and returned material never reaches evidence',async()=>{
  const f=await primary(fixture([sent(),reply(raw()),reply(raw()),enrollment(),reply(raw()),reply(raw())]));pass(await f.backend.TOTP_CREATE());
  const html=await f.backend.ownerTransientHtml('a'.repeat(64));assert.equal(html.includes('OFFLINE_TOTP_SEED'),true);
  assert.equal(JSON.stringify(f.backend).includes('OFFLINE_TOTP_SEED'),false);await assert.rejects(()=>f.backend.ownerTransientHtml('a'.repeat(64)));
  const g=fixture();const get=await request(g.handler);deny((await request(g.handler,'POST',{action:'EMAIL_OTP_SEND'},{cookie:get.headers['Set-Cookie'].split(';')[0],'x-g3-csrf':'b'.repeat(64)})).json);
});
test('synthetic rotation invalidates prior generation and cleanup removes runtime custody',()=>{assert.equal(dry.runtimeObservation(1).runtime_has_synthetic_custody,true);dry.ownerSet('OFFLINE_SENTINEL_REPLACEMENT');dry.ownerDeploy();assert.equal(dry.runtimeObservation(1).runtime_has_synthetic_custody,false);dry.cleanup();assert.equal(dry.runtimeObservation(3).runtime_has_synthetic_custody,false);});
test('artifact is deterministic and rejects an added unlisted environment path without reading it',()=>{
  const script=fileURLToPath(new URL('../scripts/verify_deployment.py',import.meta.url));
  const run=()=>spawnSync('D:\\DevTools\\NexusR2Python\\Scripts\\python.exe',['-B',script,'--output',output],{encoding:'utf8'});
  const first=metadata.zip_sha256;assert.equal(run().status,0);assert.equal(JSON.parse(readFileSync(output+'artifact-metadata.json','utf8')).zip_sha256,first);
  const synthetic=output+'source/.env';writeFileSync(synthetic,sentinel);try{assert.notEqual(run().status,0);}finally{unlinkSync(synthetic);}
});
test('provider duplicate members and escaped aliases cannot overwrite identity',async()=>{
  for(const bytes of ['{"status_code":200,"user_id":"fixture-other","user_id":"fixture-owner","email_id":"fixture-email"}',
    '{"status_code":200,"user_id":"fixture-other","user\\u005fid":"fixture-owner","email_id":"fixture-email"}']) {
    deny(await fixture([{status:200,headers:{'content-type':'application/json'},chunks:[bytes]}]).backend.EMAIL_OTP_SEND());
  }
});
test('signed JWT duplicate identity claim is rejected before historical verifier',async()=>{
  const header=Buffer.from(JSON.stringify({alg:'RS256',kid:jwk.kid})).toString('base64url');
  const claims=Buffer.from(`{"iss":"stytch.com/${project}","aud":"${project}","sub":"fixture-other","sub":"fixture-owner","iat":${T/1000},"nbf":${T/1000},"exp":${T/1000+300}}`).toString('base64url');
  const body=raw();body.session_jwt=`${header}.${claims}.${sign('RSA-SHA256',Buffer.from(`${header}.${claims}`),privateKey).toString('base64url')}`;
  const f=fixture([sent(),reply(body)]);pass(await f.backend.EMAIL_OTP_SEND());deny(await f.backend.EMAIL_OTP_AUTHENTICATE({code:'000000'}));
});
test('invalid offline clock construction fails closed without throwing',async()=>{
  const f=fixture();const handler=createOfflineDiagnosticHandler({...f.input,clock:()=>{throw Error('OFFLINE_SENTINEL_CLOCK');}});
  deny((await request(handler)).json);
  deny((await request(createOfflineDiagnosticHandler({...f.input,clock:null}))).json);
});
test('idle HTTP deadline proactively disposes transient server custody',async t=>{
  t.mock.timers.enable({apis:['setTimeout']});
  const f=fixture([sent(),reply(raw()),reply(raw()),enrollment(),reply(raw())]);
  const first=await request(f.handler);const cookie=first.headers['Set-Cookie'].split(';')[0];
  const headers={cookie,'x-g3-csrf':first.json.csrf};
  for(const action of ['EMAIL_OTP_SEND','EMAIL_OTP_AUTHENTICATE','TOTP_CREATE'])pass((await request(f.handler,'POST',{action,...(action==='EMAIL_OTP_AUTHENTICATE'?{code:'000000'}:{})},headers)).json);
  t.mock.timers.tick(300000);
  deny((await request(f.handler,'GET',undefined,{cookie})).json);
  assert.equal(f.backend.contextInfo().retired,true);
});
test('Owner browser cancel and deadline clear material before any transient POST',async()=>{
  for(const event of ['cancel','timeout','pagehide','visibilitychange']) {
    let cleared=false,cancelled=false;const handlers={},metas=[];let timer;
    const input={value:'000000'};
    const root={querySelectorAll:()=>[input],replaceChildren(){cleared=true;},textContent:''};
    const csrf={content:'a'.repeat(64),remove(){metas.push('csrf');}},expiry={content:String(T+300000),remove(){metas.push('expiry');}};
    const doc={getElementById:id=>id==='owner-transient'?root:id==='code'?input:{addEventListener:(_event,fn)=>{handlers[id]=fn;}},
      querySelector:s=>s.includes('csrf')?csrf:expiry,querySelectorAll:()=>[csrf,expiry]};
    runInNewContext(read('future-deployment/owner-transient.js'),{document:doc,window:{addEventListener:(name,fn)=>{handlers[name]=fn;}},
      Date:{now:()=>T},Number,Math,location:{origin:reg().origin,replace(){}},setTimeout:fn=>{timer=fn;},
      fetch:async()=>{assert.equal(cleared,true);assert.equal(input.value,'');assert.equal(metas.length,2);return {body:{cancel:async()=>{cancelled=true;}}};}});
    if(event==='timeout')timer();else await handlers[event]();
    assert.equal(cleared,true);assert.equal(input.value,'');assert.equal(metas.length,2);
    if(event==='cancel')assert.equal(cancelled,true);
  }
});

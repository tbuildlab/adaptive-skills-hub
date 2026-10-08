// Offline child-process proof. Never copies or enumerates the real environment.
import { registerHooks, syncBuiltinESMExports } from 'node:module';
import https from 'node:https';
import http from 'node:http';
import net from 'node:net';
import tls from 'node:tls';
import { resolve, relative, sep, isAbsolute } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
const repo=resolve(fileURLToPath(new URL('../../..',import.meta.url)));
const source=resolve(process.argv[2]??'');
const within=relative(resolve(repo,'state'),source);
if(!within||within.startsWith('..')||isAbsolute(within))throw Error('PROOF_SOURCE_BOUNDARY');
const variant=process.argv[3]??'DEFAULT';
if(!['DEFAULT','BROWSER','PREVIEW','DEVELOPMENT','UNKNOWN_TIER','BAD_HOST','BAD_ORIGIN','EXTRA_ROUTE','SECRET_PRESENCE'].includes(variant))throw Error('PROOF_CASE');
const proof={network_calls:0,credential_read_attempts:0,credential_loader_calls:0,
  native_factory_calls:0,provider_operation_calls:0,jwks_runtime_calls:0,
  signature_calls:0,owner_material_calls:0,environment_enumerations:0};
globalThis.__D01StartupProof=proof;
const denyNetwork=()=>{proof.network_calls++;throw Error('NETWORK_FORBIDDEN');};
https.request=denyNetwork;https.get=denyNetwork;http.request=denyNetwork;http.get=denyNetwork;
net.connect=denyNetwork;net.createConnection=denyNetwork;tls.connect=denyNetwork;
globalThis.fetch=denyNetwork;syncBuiltinESMExports();
const names=new Set(['STYTCH_SECRET','STYTCH_PROJECT_ID','VERCEL_OIDC_TOKEN','VERCEL_TOKEN']);
// No original process.env read/save. Every value in this replacement is synthetic.
process.env=new Proxy(Object.create(null),{
  get(_target,name){if(names.has(name)){proof.credential_read_attempts++;throw Error('ENVIRONMENT_FORBIDDEN');}return undefined;},
  ownKeys(){proof.environment_enumerations++;throw Error('ENVIRONMENT_ENUMERATION_FORBIDDEN');},
});
const trap=(sourceText,signature,counter)=>{
  if(!sourceText.includes(signature))throw Error('PROOF_INSTRUMENTATION_MISMATCH');
  return sourceText.replace(signature,signature+` globalThis.__D01StartupProof.${counter}++; throw Error('PROOF_TRAP');`);
};
// Instrument isolated in-memory module loads; no source/gate/file is modified.
// A trap invocation counts as failure, never as a successful disabled result.
registerHooks({load(url,context,nextLoad){
  const result=nextLoad(url,context);
  if(!url.startsWith('file:'))return result;
  const path=fileURLToPath(url);
  if(!path.startsWith(source+sep)||!path.endsWith('.js'))return result;
  let text=Buffer.from(result.source).toString();
  if(path.endsWith('credential-custody.js'))text=trap(text,'export function loadServerCredentials(configuration, registration) {','credential_loader_calls');
  if(path.endsWith('stytch-transport.js')){
    text=trap(text,'export function createProtectedStytchTransport(configuration, registration) {','native_factory_calls');
    text=trap(text,'async #exchange(op, body) {','provider_operation_calls');
  }
  if(path.endsWith('pinned-identity.js'))text=trap(text,'export function pinnedKeys(value, registration, now) {','jwks_runtime_calls');
  if(path.endsWith('stytch-identity.js'))text=trap(text,'export function verifyStytchIdentity(jwt, registration, remoteUser, publicKeys, now) {','signature_calls');
  if(path.endsWith('owner-channel.js'))text=trap(text,'export function createOwnerEnvelope(body, expires, fixture) {','owner_material_calls');
  return {...result,source:text};
}});
const {default:handler}=await import(pathToFileURL(resolve(source,'api/diagnostic.js')));
const {DEPLOYMENT:d}=await import(pathToFileURL(resolve(source,'lib/server/deployment-input.js')));
const policy=await import(pathToFileURL(resolve(source,'lib/server/pre-secret-policy.js')));
if(d.mode!=='FAKE_DISABLED'||policy.CODE_REVIEWED_LIVE_ENABLED!==false||policy.DEPLOYMENT_REGISTRATION_ENABLED!==false)throw Error('GATES');
const tier={PREVIEW:'PREVIEW',DEVELOPMENT:'DEVELOPMENT',UNKNOWN_TIER:'UNKNOWN'}[variant]??'PRODUCTION';
const config={...d,mode:'D01_DIAGNOSTIC_LIVE_STYTCH',deployment_tier:tier};
Object.defineProperty(config,'STYTCH_SECRET',{get(){proof.credential_read_attempts++;throw Error('SYNTHETIC_INPUT_FORBIDDEN');}});
if(policy.liveSelectionAllowed(config,d.provider))throw Error('SELECTION');
const base={host:'nexus-g3-qual.vercel.app',origin:'https://nexus-g3-qual.vercel.app'};
const request=async(method='GET',body,headers=base,url='/api/diagnostic')=>{
  const response={headers:{},setHeader(k,v){this.headers[k]=v;},end(s){this.body=JSON.parse(s);}};
  await handler({method,url,body,headers},response);
  if(response.body.adapter_mode!=='FAKE_DISABLED'||response.body.result!=='DENY'
      ||response.body.authority!=='NONE'||response.body.real_admission!=='DISABLED'||response.body.live_diagnostic_enabled!==false)throw Error('DISABLED_STARTUP');
  const output=JSON.stringify(response.body);
  if(output.includes(d.provider.owner_user_id)||output.includes(d.provider.project_id))throw Error('IDENTIFIER_LEAK');
  return response;
};
const initial=await request();
const mutations={BROWSER:{...base},PREVIEW:{...base,host:'preview.invalid'},DEVELOPMENT:{...base,host:'localhost'},
  BAD_HOST:{...base,host:'evil.invalid'},BAD_ORIGIN:{...base,origin:'https://evil.invalid'}};
if(mutations[variant]){
  const rejected=await request('GET',undefined,mutations[variant]);
  if(variant!=='BROWSER'&&(rejected.statusCode!==403||rejected.body.error_class!=='ORIGIN'))throw Error('HOST_ORIGIN_NOT_REJECTED');
}
if(variant==='EXTRA_ROUTE'){
  const rejected=await request('GET',undefined,base,'/api/admin');
  if(rejected.statusCode!==403||rejected.body.error_class!=='REQUEST')throw Error('EXTRA_ROUTE_NOT_REJECTED');
}
const headers={...base,'content-type':'application/json','x-g3-csrf':initial.body.csrf,
  cookie:initial.headers['Set-Cookie'].split(';')[0]};
for(const action of ['EMAIL_START','EMAIL_VERIFY','TOTP_ENROLLMENT_START','TOTP_VERIFY','PAGE',
  'DECISION_POST_SIMULATION','RECEIPT_SIMULATION','INTENT_SIMULATION','CLAIM_SIMULATION'])await request('POST',{action},headers);
const overridden=await request('POST',{action:'EMAIL_START',mode:'D01_DIAGNOSTIC_LIVE_STYTCH',provider:'OTHER'},headers);
if(overridden.statusCode!==400||overridden.body.error_class!=='REQUEST')throw Error('BROWSER_OVERRIDE_NOT_REJECTED');
await request('POST',{action:'OWNER_TOTP_DISPLAY',csrf:initial.body.csrf},{...headers,'content-type':'application/x-www-form-urlencoded'});
if(Object.values(proof).some(value=>value!==0))throw Error('SIDE_EFFECT_ATTEMPT');
process.stdout.write(JSON.stringify({startup:'PASS',case:variant,mode:'FAKE_DISABLED',result:'DENY',authority:'NONE',
  real_admission:'DISABLED',...proof})+'\n');

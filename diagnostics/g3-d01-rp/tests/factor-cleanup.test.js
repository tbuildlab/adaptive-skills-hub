import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createOfflineCleanup, runOfflineCleanup, offlineShapes, runProtectedCleanup, requestGate, scopeDigest, parseUniqueJson } from '../factor-cleanup/cleanup.js';
const scope = JSON.parse(readFileSync(new URL('../factor-cleanup/reviewed-scope.json', import.meta.url), 'utf8'));
const config = {enabled: true, valid_from: 1000, valid_until: 1801000, scope};
const env = {VERCEL_ENV: 'production', VERCEL_PROJECT_ID: scope.vercel_project_id, VERCEL_URL: 'nexus-g3-qual-syntheticonly-tdy0225.vercel.app'};
const req = {method: 'POST', host: env.VERCEL_URL, content_type: 'application/json', marker: 'fixed-factor-cleanup-v1',
  body: {action: 'DELETE_EXPOSED_FACTOR', scope_sha256: scopeDigest(scope)}};
const other = 'totp-test-00000000-0000-0000-0000-000000000000';
const user = ids => ({status_code: 200, user_id: scope.owner_user_id, totps: ids.map(totp_id => ({totp_id, verified: true}))});
const ack = ids => ({status_code: 200, user_id: scope.owner_user_id, user: user(ids)});
const fixture = (replies, clock = () => 2000) => createOfflineCleanup(config, replies.map(body => body?.failure ? body : {body}), clock);
test('fixed valid request passes; GET is non-provider preflight', () => {
  assert.equal(requestGate(req,config,env,2000),'DELETE_EXPOSED_FACTOR');
  assert.equal(requestGate({...req,method:'GET'},config,env,2000),'STATUS');
});
for (const [name, change, expected] of [
  ['foreign deployment',{host:'nexus-g3-qual.vercel.app'},'DEPLOYMENT'],
  ['browser origin',{origin:'https://nexus-g3-qual.vercel.app'},'DEPLOYMENT'],
  ['browser metadata',{fetch_site:'same-origin'},'DEPLOYMENT'],
  ['GET never mutates',{method:'GET'},'STATUS'],
  ['wrong method',{method:'DELETE'},'REQUEST'],
  ['form payload',{content_type:'application/x-www-form-urlencoded'},'REQUEST'],
  ['missing marker',{marker:undefined},'REQUEST'],
  ['arbitrary Owner body',{body:{...req.body,owner_user_id:scope.owner_user_id}},'REQUEST'],
  ['arbitrary factor body',{body:{...req.body,totp_id:other}},'REQUEST'],
  ['wrong scope',{body:{...req.body,scope_sha256:'0'.repeat(64)}},'REQUEST'],
  ['unknown action',{body:{...req.body,action:'DELETE_USER'}},'REQUEST'],
]) test('request guard '+name,()=>assert.equal(requestGate({...req,...change},config,env,2000),expected));
for (const [name, changed] of [
  ['disabled',{...config,enabled:false}],['oversized window',{...config,valid_until:1801001}],
  ['unknown scope member',{...config,scope:{...scope,token:'NEVER_A_TOKEN'}}],
  ['wrong generation',{...config,scope:{...scope,application_generation:4}}],
]) test('configuration rejects '+name,()=>assert.notEqual(requestGate(req,changed,env,2000),'DELETE_EXPOSED_FACTOR'));
for (const [name, environment] of [
  ['Preview',{...env,VERCEL_ENV:'preview'}],['wrong project',{...env,VERCEL_PROJECT_ID:'other'}],
  ['missing project',{...env,VERCEL_PROJECT_ID:undefined}],['foreign URL',{...env,VERCEL_URL:'attacker.example'}],
]) test('deployment rejects '+name,()=>assert.equal(requestGate(req,config,environment,2000),'DEPLOYMENT'));
test('expired and future-invalid windows deny',()=>{
  assert.equal(requestGate(req,config,env,1801000),'EXPIRED'); assert.equal(requestGate(req,config,env,999),'EXPIRED');
});
test('exact factor deletion preserves User and other factors with three calls',async()=>{
  const handle=fixture([user([scope.exposed_totp_id,other]),ack([other]),user([other])]);
  const result=await runOfflineCleanup(handle,'DELETE_EXPOSED_FACTOR');
  assert.equal(result.result,'PASS'); assert.equal(result.delete_calls,1); assert.equal(result.provider_calls,3);
  for(const field of ['user_preserved','factor_absent','other_factors_preserved','delete_acknowledged']) assert.equal(result[field],true);
  assert.deepEqual(offlineShapes(handle).map(x=>x.method),['GET','DELETE','GET']);
  const text=JSON.stringify(result); for(const id of [scope.owner_user_id,scope.exposed_totp_id,other]) assert.ok(!text.includes(id));
});
test('already absent factor is read-only idempotent result',async()=>{
  const handle=fixture([user([other])]); const result=await runOfflineCleanup(handle,'DELETE_EXPOSED_FACTOR');
  assert.equal(result.error_class,'ALREADY_ABSENT');assert.equal(result.delete_calls,0);assert.equal(result.provider_calls,1);
});
test('readonly verification cannot delete present factor',async()=>{
  const handle=fixture([user([scope.exposed_totp_id])]);const result=await runOfflineCleanup(handle,'VERIFY_ABSENCE');
  assert.equal(result.result,'DENY');assert.equal(result.delete_calls,0);
});
for (const [name, body] of [
  ['wrong Owner',{...user([scope.exposed_totp_id]),user_id:'user-test-00000000-0000-0000-0000-000000000000'}],
  ['missing factors',{status_code:200,user_id:scope.owner_user_id}],
  ['duplicate factor',user([scope.exposed_totp_id,scope.exposed_totp_id])],
  ['bad factor metadata',{...user([scope.exposed_totp_id]),totps:[{totp_id:scope.exposed_totp_id}]}],
  ['provider error',{status_code:401}],
]) test('precheck '+name+' denies before mutation',async()=>{
  const handle=fixture([body]);const result=await runOfflineCleanup(handle,'DELETE_EXPOSED_FACTOR');
  assert.equal(result.result,'DENY');assert.equal(result.delete_calls,0);assert.equal(result.provider_calls,1);
});
test('unknown deletion acknowledgment never retries deletion',async()=>{
  const handle=fixture([user([scope.exposed_totp_id,other]),{failure:true},user([other])]);
  const result=await runOfflineCleanup(handle,'DELETE_EXPOSED_FACTOR');
  assert.equal(result.result,'DENY');assert.equal(result.error_class,'DELETE_ACK_UNKNOWN');
  assert.equal(result.factor_absent,true);assert.equal(result.delete_calls,1);assert.equal(result.provider_calls,3);
});
for(const [name,after] of [['target survives',user([scope.exposed_totp_id,other])],['other factor lost',user([])],['other factor added',user([other,'totp-test-11111111-1111-1111-1111-111111111111'])]])
  test('postcondition '+name+' is fail closed',async()=>{
    const result=await runOfflineCleanup(fixture([user([scope.exposed_totp_id,other]),ack([other]),after]),'DELETE_EXPOSED_FACTOR');
    assert.equal(result.result,'DENY');assert.equal(result.error_class,'POSTCONDITION');assert.equal(result.delete_calls,1);
  });
test('wrong deletion response Owner remains denied even after absence readback',async()=>{
  const result=await runOfflineCleanup(fixture([user([scope.exposed_totp_id]),{...ack([]),user_id:'other'},user([])]),'DELETE_EXPOSED_FACTOR');
  assert.equal(result.result,'DENY');assert.equal(result.error_class,'OWNER_MISMATCH');
});
test('expiry after precheck prevents deletion',async()=>{
  let ticks=0;const handle=fixture([user([scope.exposed_totp_id])],()=>++ticks===1?2000:1801000);
  const result=await runOfflineCleanup(handle,'DELETE_EXPOSED_FACTOR');assert.equal(result.result,'DENY');assert.equal(result.delete_calls,0);
});
test('offline handle cannot enter protected runtime; no credential reads',async()=>{
  const handle=fixture([]);let reads=0;const environment=new Proxy({}, {get(){reads++;throw new Error('FORBIDDEN');}});
  await assert.rejects(runProtectedCleanup(handle,'DELETE_EXPOSED_FACTOR',environment));assert.equal(reads,0);
});
test('disabled runtime cannot read credentials',async()=>{
  let reads=0;const environment=new Proxy({}, {get(){reads++;throw new Error('FORBIDDEN');}});
  await assert.rejects(runProtectedCleanup({...config,enabled:false},'DELETE_EXPOSED_FACTOR',environment));assert.equal(reads,0);
});
for(const [name,body] of [['duplicate key','{"a":1,"a":2}'],['escaped duplicate','{"a":1,"\\u0061":2}'],['invalid UTF8',null],['oversize',' '.repeat(65537)],['bad JSON','{"a":}']])
  test('bounded parser '+name,()=>assert.throws(()=>parseUniqueJson(body===null?Uint8Array.from([255]):Buffer.from(body))));
test('bounded parser valid response',()=>assert.deepEqual(parseUniqueJson(Buffer.from('{"status_code":200,"totps":[]}')),{status_code:200,totps:[]}));

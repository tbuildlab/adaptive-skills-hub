import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { readFileSync } from 'node:fs';
import { DEPLOYMENT as D } from '../lib/server/deployment-input.js';
import { pinnedKeys } from '../lib/server/pinned-identity.js';
const script=fileURLToPath(new URL('../scripts/prove_disabled_startup.mjs',import.meta.url));
const output=fileURLToPath(new URL('../../../state/g3-d01-deployment-prep-20261009/artifact/source',import.meta.url));
const rows=new Map();
function proof(name='DEFAULT') {
  if(!rows.has(name)){
    const run=spawnSync('node',[script,output,name],{encoding:'utf8',timeout:20000});
    assert.equal(run.status,0,'isolated startup must pass without raw output');
    rows.set(name,JSON.parse(run.stdout));
  }
  return rows.get(name);
}
test('01 composed reviewed source starts FAKE_DISABLED -> DENY',()=>{assert.equal(proof().mode,'FAKE_DISABLED');assert.equal(proof().result,'DENY');});
test('02 false compile gate remains unchanged source input',()=>assert.equal(readFileSync(new URL('../lib/server/pre-secret-policy.js',import.meta.url),'utf8').includes('CODE_REVIEWED_LIVE_ENABLED = false'),true));
test('03 false deployment registration gate remains unchanged',()=>assert.equal(readFileSync(new URL('../lib/server/pre-secret-policy.js',import.meta.url),'utf8').includes('DEPLOYMENT_REGISTRATION_ENABLED = false'),true));
test('04 credential environment and loader are not reached',()=>{assert.equal(proof().credential_read_attempts,0);assert.equal(proof().credential_loader_calls,0);assert.equal(proof().environment_enumerations,0);});
test('05 native HTTPS construction/use and provider operations never reached',()=>{assert.equal(proof().network_calls,0);assert.equal(proof().native_factory_calls,0);assert.equal(proof().provider_operation_calls,0);});
test('06 project registration cannot activate',()=>{assert.ok(D.provider!==null);assert.equal(proof().mode,'FAKE_DISABLED');});
test('07 key pin/signature path cannot activate startup',()=>{assert.ok(D.keyset!==null);assert.equal(proof().jwks_runtime_calls,0);assert.equal(proof().signature_calls,0);});
test('08 browser mode override cannot activate',()=>assert.equal(proof('BROWSER').result,'DENY'));
test('09 Preview cannot activate',()=>assert.equal(proof('PREVIEW').mode,'FAKE_DISABLED'));
test('10 Development cannot activate',()=>assert.equal(proof('DEVELOPMENT').mode,'FAKE_DISABLED'));
test('11 unknown deployment tier cannot activate',()=>assert.equal(proof('UNKNOWN_TIER').mode,'FAKE_DISABLED'));
test('12 arbitrary Host is rejected with no IO',()=>assert.equal(proof('BAD_HOST').network_calls,0));
test('13 wrong Production Origin rejects with no IO',()=>assert.equal(proof('BAD_ORIGIN').network_calls,0));
test('14 extra route cannot reach the protected handler flow',()=>assert.equal(proof('EXTRA_ROUTE').owner_material_calls,0));
test('34 review expiry still blocks later runtime pin use without renewal',()=>{assert.equal(pinnedKeys(D.keyset,D.provider,D.keyset.valid_until),null);assert.equal(D.keyset.valid_until,1791564125000);});
test('35 REAL_ADMISSION remains disabled',()=>assert.equal(proof().real_admission,'DISABLED'));
test('36 network count remains zero with synthetically present credential input',()=>assert.equal(proof('SECRET_PRESENCE').network_calls,0));
test('37 credential read attempt count remains zero',()=>assert.equal(proof('SECRET_PRESENCE').credential_read_attempts,0));

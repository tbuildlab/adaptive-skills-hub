import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash, createPublicKey } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { DEPLOYMENT as ORIGINAL } from '../lib/server/deployment-input.js';
import { OWNER_KEYSET_GENERATION_2 as K, DISABLED_GENERATION_2_INPUT as D } from '../lib/server/owner-keyset-generation2.js';
import { normalizeReviewedPublicJwks, pinnedKeys } from '../lib/server/pinned-identity.js';
import { validateReviewedRegistration } from '../lib/server/provider-registration.js';
import { liveSelectionAllowed, CODE_REVIEWED_LIVE_ENABLED, DEPLOYMENT_REGISTRATION_ENABLED } from '../lib/server/pre-secret-policy.js';
import { createProtectedStytchTransport } from '../lib/server/stytch-transport.js';

test('fresh generation 2 key matches every core field of original pin', () => {
  assert.equal(K.keys.length, 1);
  for (const field of ['kid', 'kty', 'alg', 'use', 'e', 'n']) assert.equal(K.keys[0][field], ORIGINAL.keyset.keys[0][field]);
  assert.equal(createHash('sha256').update(JSON.stringify(K.keys)).digest('hex'),
    '5794378f74deee81d960d1860d744a2eed08e6da108789444f04e089efa04dd3');
  assert.equal(createPublicKey({ key: K.keys[0], format: 'jwk' }).asymmetricKeyDetails.modulusLength, 2048);
});

test('public metadata normalization pins only accepted six fields', () => {
  const normalized = normalizeReviewedPublicJwks({ keys: [{ ...K.keys[0], key_ops: ['verify'] }],
    request_id: 'OFFLINE_ENVELOPE', status_code: 200 });
  assert.deepEqual(normalized, K.keys);
  assert.deepEqual(Object.keys(K.keys[0]), ['kty', 'kid', 'alg', 'use', 'n', 'e']);
  assert.equal(Object.hasOwn(K, 'request_id'), false);
  assert.equal(Object.hasOwn(K, 'status_code'), false);
});

test('generation 2 input is coherent closed registration, deeply frozen pin', () => {
  assert.ok(validateReviewedRegistration(D.provider));
  assert.equal(D.registration_generation, 2);
  assert.equal(D.provider.application_generation, 2);
  assert.equal(K.application_generation, 2);
  assert.equal(K.project_id, D.provider.project_id);
  assert.equal(D.deployment_revision, D.provider.deployment_revision);
  assert.ok(Object.isFrozen(D) && Object.isFrozen(K) && Object.isFrozen(K.keys) && Object.isFrozen(K.keys[0]));
  assert.ok(pinnedKeys(K, D.provider, K.valid_from));
});

test('review is bounded, exact start valid and exact end denied', () => {
  assert.equal(K.valid_from, Date.parse('2026-10-09T16:35:37Z'));
  assert.equal(K.valid_until - K.valid_from, 23 * 60 * 60 * 1000);
  assert.equal(pinnedKeys(K, D.provider, K.valid_from - 1), null);
  assert.ok(pinnedKeys(K, D.provider, K.valid_until - 1));
  assert.equal(pinnedKeys(K, D.provider, K.valid_until), null);
});

test('generation 1 and generation 2 pins cannot cross registrations', () => {
  assert.equal(pinnedKeys(ORIGINAL.keyset, D.provider, ORIGINAL.keyset.valid_from), null);
  assert.equal(pinnedKeys(K, ORIGINAL.provider, K.valid_from), null);
  assert.equal(ORIGINAL.provider.application_generation, 1);
  assert.equal(ORIGINAL.provider.delivery_email, null);
  assert.equal(ORIGINAL.keyset.valid_until, 1791564125000);
});

test('wrong project, stale and unknown generations fail closed', () => {
  assert.equal(pinnedKeys({ ...K, project_id: 'project-test-other' }, D.provider, K.valid_from), null);
  for (const application_generation of [0, 1, 3, null, undefined, '2']) {
    assert.equal(pinnedKeys({ ...K, application_generation }, D.provider, K.valid_from), null);
  }
});

test('wrong kid, duplicate kid and malformed public key reject', () => {
  const normalize = keys => normalizeReviewedPublicJwks({ keys });
  assert.equal(normalize([K.keys[0], K.keys[0]]), null);
  assert.equal(normalize([{ ...K.keys[0], kid: '' }]), null);
  assert.equal(normalize([{ ...K.keys[0], n: 'invalid=' }]), null);
  assert.equal(K.keys.some(k => k.kid === 'OFFLINE_UNKNOWN_KID'), false);
});

test('private fields, remote URL and excessive keysets reject without persistence', () => {
  for (const field of ['d', 'p', 'q', 'dp', 'dq', 'qi', 'oth', 'x5u', 'jku']) {
    assert.equal(normalizeReviewedPublicJwks({ keys: [{ ...K.keys[0], [field]: 'OFFLINE_REJECTED' }] }), null);
  }
  assert.equal(normalizeReviewedPublicJwks({ keys: Array.from({ length: 9 }, (_, i) => ({ ...K.keys[0], kid: `offline-${i}` })) }), null);
});

test('pin presence and email cannot read credentials or enable transport', () => {
  let reads = 0;
  const configuration = { ...D };
  Object.defineProperty(configuration, 'STYTCH_SECRET', { get() { reads++; throw Error('OFFLINE_SECRET_READ'); } });
  assert.equal(CODE_REVIEWED_LIVE_ENABLED, false);
  assert.equal(DEPLOYMENT_REGISTRATION_ENABLED, false);
  assert.equal(D.mode, 'FAKE_DISABLED');
  assert.equal(liveSelectionAllowed(configuration, D.provider), false);
  const transport = createProtectedStytchTransport(configuration, D.provider);
  assert.equal(transport.mode, 'FAKE_DISABLED');
  assert.equal(reads, 0);
});

test('generation 2 transport cannot enter credential loader or any network primitive', () => {
  const script = `
    import { registerHooks, syncBuiltinESMExports } from 'node:module';
    import https from 'node:https'; import http from 'node:http';
    import net from 'node:net'; import tls from 'node:tls';
    let calls = 0;
    const deny = () => { calls++; throw Error('OFFLINE_SIDE_EFFECT'); };
    https.request=deny; https.get=deny; http.request=deny; http.get=deny;
    net.connect=deny; net.createConnection=deny; tls.connect=deny;
    globalThis.fetch=deny; syncBuiltinESMExports();
    const credentialNames=new Set(['STYTCH_SECRET','STYTCH_PROJECT_ID','VERCEL_OIDC_TOKEN','VERCEL_TOKEN']);
    process.env = new Proxy(Object.create(null), {
      get(_target,name) { if(credentialNames.has(name)) return deny(); return undefined; }, ownKeys: deny
    });
    registerHooks({ load(url, context, next) {
      const result=next(url,context);
      if (!url.endsWith('/credential-custody.js')) return result;
      const text=Buffer.from(result.source).toString();
      const signature='export function loadServerCredentials(configuration, registration) {';
      if (!text.includes(signature)) throw Error('OFFLINE_TRAP_MISMATCH');
      return { ...result, source:text.replace(signature, signature+" throw Error('OFFLINE_LOADER_ENTERED');") };
    }});
    const { DISABLED_GENERATION_2_INPUT:d }=await import(${JSON.stringify(new URL('../lib/server/owner-keyset-generation2.js', import.meta.url).href)});
    const { createProtectedStytchTransport }=await import(${JSON.stringify(new URL('../lib/server/stytch-transport.js', import.meta.url).href)});
    const transport=createProtectedStytchTransport(d,d.provider);
    const result=await transport.EMAIL_OTP_SEND();
    if(calls!==0 || transport.mode!=='FAKE_DISABLED' || result.authority!=='NONE'
      ||result.real_admission!=='DISABLED' ||result.result!=='DENY') throw Error('OFFLINE_BOUNDARY');
  `;
  const result = spawnSync(process.execPath, ['--input-type=module', '-e', script], { env: {}, encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
});

test('browser or Preview selection cannot activate future reviewed input', () => {
  assert.equal(liveSelectionAllowed({ ...D, mode: 'D01_DIAGNOSTIC_LIVE_STYTCH' }, D.provider), false);
  assert.equal(liveSelectionAllowed({ ...D, deployment_tier: 'PREVIEW' }, D.provider), false);
});

test('public and deployed entrypoints do not import additive generation 2 input', () => {
  for (const path of ['future-deployment/diagnostic-entry.js', 'lib/server/diagnostic-service.js',
    'future-deployment/app.js', 'future-deployment/index.html', 'future-deployment/owner-transient.js']) {
    const content = readFileSync(new URL('../' + path, import.meta.url), 'utf8');
    assert.ok(!content.includes('owner-keyset-generation2'));
    if (path.startsWith('future-deployment/')) {
      assert.ok(!content.includes(K.keys[0].kid) && !content.includes(D.provider.owner_user_id));
    }
  }
});

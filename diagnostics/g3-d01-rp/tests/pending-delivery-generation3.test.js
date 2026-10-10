import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { DEPLOYMENT as ORIGINAL } from '../lib/server/deployment-input.js';
import { DISABLED_GENERATION_2_INPUT as PREVIOUS } from '../lib/server/owner-keyset-generation2.js';
import { OWNER_DELIVERY_GENERATION_3_REVIEW as REVIEW,
  PENDING_OWNER_GENERATION_3_REGISTRATION as R,
  PENDING_DISABLED_GENERATION_3_INPUT as D } from '../lib/server/pending-delivery-generation3.js';
import { validateReviewedRegistration } from '../lib/server/provider-registration.js';
import { pinnedKeys } from '../lib/server/pinned-identity.js';
import { liveSelectionAllowed, CODE_REVIEWED_LIVE_ENABLED,
  DEPLOYMENT_REGISTRATION_ENABLED } from '../lib/server/pre-secret-policy.js';

test('new delivery is closed reviewed configuration, never new principal authority', () => {
  assert.ok(validateReviewedRegistration(R));
  assert.equal(REVIEW.source, 'OWNER_REVIEWED');
  assert.equal(REVIEW.authority, 'NONE');
  assert.equal(R.delivery_email, REVIEW.delivery_email);
  assert.notEqual(R.delivery_email, PREVIOUS.provider.delivery_email);
  for (const field of ['project_id', 'owner_user_id', 'issuer', 'audience']) {
    assert.equal(R[field], ORIGINAL.provider[field]);
    assert.equal(R[field], PREVIOUS.provider[field]);
  }
});

test('only reviewed delivery, review reference and application revision advance', () => {
  const changed = Object.keys(R).filter(k => R[k] !== PREVIOUS.provider[k]);
  assert.deepEqual(changed.sort(), ['application_generation', 'delivery_email', 'deployment_revision', 'review_id']);
  assert.equal(REVIEW.previous_application_generation, 2);
  assert.equal(REVIEW.next_application_generation, 3);
  assert.equal(R.application_generation, 3);
  assert.equal(D.registration_generation, 3);
  assert.equal(R.project_generation, 1);
  assert.equal(R.owner_generation, 1);
  assert.equal(R.binding_generation, 1);
});

test('pending generation 3 has no usable keyset and cannot reuse either older pin', () => {
  assert.equal(D.keyset, null);
  assert.equal(REVIEW.keyset_review_status, 'PENDING_OWNER_REVIEW_FOR_NEW_GENERATION');
  assert.equal(pinnedKeys(D.keyset, R, PREVIOUS.keyset.valid_from), null);
  assert.equal(pinnedKeys(PREVIOUS.keyset, R, PREVIOUS.keyset.valid_from), null);
  assert.equal(pinnedKeys(ORIGINAL.keyset, R, ORIGINAL.keyset.valid_from), null);
});

test('old pins and absolute review deadlines are not rewritten or renewed', () => {
  assert.equal(PREVIOUS.provider.application_generation, 2);
  assert.equal(PREVIOUS.keyset.application_generation, 2);
  assert.equal(PREVIOUS.keyset.valid_from, 1791563737000);
  assert.equal(PREVIOUS.keyset.valid_until, 1791646537000);
  assert.equal(ORIGINAL.provider.application_generation, 1);
  assert.equal(ORIGINAL.provider.delivery_email, null);
  assert.equal(ORIGINAL.keyset.valid_until, 1791564125000);
  assert.ok(!Object.hasOwn(REVIEW, 'valid_from') && !Object.hasOwn(REVIEW, 'valid_until'));
});

test('pending records are frozen and cannot be rewritten by browser fields', () => {
  for (const value of [REVIEW, R, R.factors, D]) assert.ok(Object.isFrozen(value));
  for (const field of ['delivery_email', 'project_id', 'owner_user_id', 'application_generation']) {
    assert.throws(() => { R[field] = 'OFFLINE_BROWSER_MUTATION'; }, TypeError);
  }
  assert.throws(() => { D.keyset = PREVIOUS.keyset; }, TypeError);
});

test('factor and lifetime bounds remain exact', () => {
  assert.deepEqual(R.factors, ['EMAIL_OTP', 'TOTP']);
  assert.equal(R.session_max_minutes, 15);
  assert.equal(R.context_max_ms, 300000);
  assert.equal(R.origin, ORIGINAL.origin);
  assert.equal(D.deployment_revision, R.deployment_revision);
});

test('delivery-only registration contains neither key provenance nor bearer evidence', () => {
  assert.deepEqual(Object.keys(R).sort(), Object.keys(PREVIOUS.provider).sort());
  assert.ok(!Object.hasOwn(R, 'session_id') && !Object.hasOwn(R, 'session_token'));
  assert.ok(!Object.hasOwn(R, 'session_jwt') && !Object.hasOwn(R, 'email_verified'));
  assert.equal(JSON.parse(JSON.stringify(D)).keyset, null);
});

test('all live-selection attempts remain disabled without argument inspection', () => {
  let reads = 0;
  const deny = new Proxy({}, { get() { reads++; throw Error('OFFLINE_READ'); } });
  assert.equal(CODE_REVIEWED_LIVE_ENABLED, false);
  assert.equal(DEPLOYMENT_REGISTRATION_ENABLED, false);
  assert.equal(liveSelectionAllowed(deny, deny), false);
  assert.equal(reads, 0);
  assert.equal(D.mode, 'FAKE_DISABLED');
  assert.equal(liveSelectionAllowed({ ...D, mode: 'D01_DIAGNOSTIC_LIVE_STYTCH' }, R), false);
  assert.equal(liveSelectionAllowed({ ...D, deployment_tier: 'PREVIEW' }, R), false);
});

test('deployed and client entrypoints do not import or expose pending delivery', () => {
  for (const path of ['future-deployment/diagnostic-entry.js', 'lib/server/diagnostic-service.js',
    'future-deployment/app.js', 'future-deployment/index.html', 'future-deployment/owner-transient.js']) {
    const content = readFileSync(new URL('../' + path, import.meta.url), 'utf8');
    assert.ok(!content.includes('pending-delivery-generation3'));
    assert.ok(!content.includes(REVIEW.delivery_email));
    if (path.startsWith('future-deployment/')) assert.ok(!content.includes(R.owner_user_id));
  }
});

test('pending input cannot enter credentials or networking even during send attempt', () => {
  const script = `
    import { registerHooks, syncBuiltinESMExports } from 'node:module';
    import https from 'node:https'; import http from 'node:http';
    import net from 'node:net'; import tls from 'node:tls';
    let calls = 0;
    const deny = () => { calls++; throw Error('OFFLINE_SIDE_EFFECT'); };
    https.request=deny; https.get=deny; http.request=deny; http.get=deny;
    net.connect=deny; net.createConnection=deny; tls.connect=deny;
    globalThis.fetch=deny; syncBuiltinESMExports();
    const names=new Set(['STYTCH_SECRET','STYTCH_PROJECT_ID','VERCEL_OIDC_TOKEN','VERCEL_TOKEN']);
    process.env = new Proxy(Object.create(null), {
      get(_target,name) { if(names.has(name)) return deny(); return undefined; }, ownKeys: deny
    });
    registerHooks({ load(url, context, next) {
      const result=next(url,context);
      if (!url.endsWith('/credential-custody.js')) return result;
      const text=Buffer.from(result.source).toString();
      const signature='export function loadServerCredentials(configuration, registration) {';
      if (!text.includes(signature)) throw Error('OFFLINE_TRAP_MISMATCH');
      return { ...result, source:text.replace(signature, signature+" throw Error('OFFLINE_LOADER_ENTERED');") };
    }});
    const { PENDING_DISABLED_GENERATION_3_INPUT:d }=await import(${JSON.stringify(new URL('../lib/server/pending-delivery-generation3.js', import.meta.url).href)});
    const { createProtectedStytchTransport }=await import(${JSON.stringify(new URL('../lib/server/stytch-transport.js', import.meta.url).href)});
    const transport=createProtectedStytchTransport(d,d.provider);
    const result=await transport.EMAIL_OTP_SEND();
    if(calls!==0 || transport.mode!=='FAKE_DISABLED' || result.authority!=='NONE'
      ||result.real_admission!=='DISABLED' ||result.result!=='DENY') throw Error('OFFLINE_BOUNDARY');
  `;
  const result = spawnSync(process.execPath, ['--input-type=module', '-e', script], { env: {}, encoding: 'utf8' });
  assert.equal(result.status, 0, result.stderr);
});

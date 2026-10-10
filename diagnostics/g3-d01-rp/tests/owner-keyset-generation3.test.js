import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { DISABLED_GENERATION_2_INPUT as P } from '../lib/server/owner-keyset-generation2.js';
import { DISABLED_GENERATION_3_INPUT as D } from '../lib/server/owner-keyset-generation3.js';
import { PENDING_DISABLED_GENERATION_3_INPUT as PENDING } from '../lib/server/pending-delivery-generation3.js';
import { validateReviewedRegistration } from '../lib/server/provider-registration.js';
import { pinnedKeys } from '../lib/server/pinned-identity.js';
import { liveSelectionAllowed } from '../lib/server/pre-secret-policy.js';
import { createProtectedStytchTransport } from '../lib/server/stytch-transport.js';

test('authorized generation 3 rebind preserves every public key byte and provenance', () => {
  assert.deepEqual(D.keyset.keys, P.keyset.keys);
  assert.equal(D.keyset.keys, P.keyset.keys);
  assert.equal(D.keyset.source, P.keyset.source);
  assert.equal(D.keyset.project_id, P.keyset.project_id);
  assert.equal(createHash('sha256').update(JSON.stringify(D.keyset.keys)).digest('hex'),
    '5794378f74deee81d960d1860d744a2eed08e6da108789444f04e089efa04dd3');
});

test('authorized rebind does not renew or extend review window', () => {
  assert.equal(D.keyset.valid_from, P.keyset.valid_from);
  assert.equal(D.keyset.valid_until, P.keyset.valid_until);
  assert.equal(pinnedKeys(D.keyset, D.provider, D.keyset.valid_from - 1), null);
  assert.ok(pinnedKeys(D.keyset, D.provider, D.keyset.valid_until - 1));
  assert.equal(pinnedKeys(D.keyset, D.provider, D.keyset.valid_until), null);
});

test('new registration, pin and revision coherently bind generation 3', () => {
  assert.ok(validateReviewedRegistration(D.provider));
  assert.equal(D.provider, PENDING.provider);
  assert.equal(D.registration_generation, 3);
  assert.equal(D.keyset.application_generation, 3);
  assert.equal(D.deployment_revision, D.provider.deployment_revision);
  assert.ok(pinnedKeys(D.keyset, D.provider, D.keyset.valid_from));
});

test('new and old pins cannot cross registrations in either direction', () => {
  assert.equal(pinnedKeys(P.keyset, D.provider, P.keyset.valid_from), null);
  assert.equal(pinnedKeys(D.keyset, P.provider, D.keyset.valid_from), null);
  assert.equal(PENDING.keyset, null);
  assert.equal(P.keyset.application_generation, 2);
});

test('wrong project, generation and unknown provenance fail closed', () => {
  for (const mutation of [{ project_id: 'OFFLINE_WRONG_PROJECT' }, { application_generation: 2 },
    { application_generation: '3' }, { source: 'EXECUTOR_DISCOVERED' }]) {
    assert.equal(pinnedKeys({ ...D.keyset, ...mutation }, D.provider, D.keyset.valid_from), null);
  }
});

test('disabled registration/pin presence never invokes credentials or enables transport', () => {
  let reads = 0;
  const config = { ...D };
  Object.defineProperty(config, 'STYTCH_SECRET', { get() { reads++; throw Error('OFFLINE_SECRET_READ'); } });
  assert.equal(liveSelectionAllowed(config, D.provider), false);
  assert.equal(createProtectedStytchTransport(config, D.provider).mode, 'FAKE_DISABLED');
  assert.equal(reads, 0);
});

test('rebound public data remains frozen with six normalized public fields', () => {
  for (const value of [D, D.provider, D.keyset, D.keyset.keys, D.keyset.keys[0]]) assert.ok(Object.isFrozen(value));
  assert.deepEqual(Object.keys(D.keyset.keys[0]), ['kty', 'kid', 'alg', 'use', 'n', 'e']);
  assert.throws(() => { D.keyset.valid_until++; }, TypeError);
  assert.throws(() => { D.provider.owner_user_id = 'OFFLINE_OTHER_USER'; }, TypeError);
});

test('historical and browser entrypoints remain outside new data-only source', () => {
  for (const path of ['future-deployment/diagnostic-entry.js', 'lib/server/diagnostic-service.js',
    'future-deployment/app.js', 'future-deployment/index.html', 'future-deployment/owner-transient.js']) {
    const text = readFileSync(new URL('../' + path, import.meta.url), 'utf8');
    assert.ok(!text.includes('owner-keyset-generation3') && !text.includes(D.provider.delivery_email));
  }
});

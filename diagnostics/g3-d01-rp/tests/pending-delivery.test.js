import test from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { DEPLOYMENT as D } from '../lib/server/deployment-input.js';
import { OWNER_DELIVERY_REVIEW as E, PENDING_OWNER_REGISTRATION as R,
  PENDING_REGISTRATION_GENERATION as G } from '../lib/server/pending-delivery-review.js';
import { validateReviewedRegistration, registerReviewedDeployment, registrationCurrent,
  createReviewedCurrentControl, currentControlRecord } from '../lib/server/provider-registration.js';
import { pinnedKeys } from '../lib/server/pinned-identity.js';
import { liveSelectionAllowed } from '../lib/server/pre-secret-policy.js';
import { createProtectedStytchTransport } from '../lib/server/stytch-transport.js';

test('delivery candidate is exact explicit non-secret Owner input', () => {
  assert.equal(E.source, 'OWNER_REVIEWED');
  assert.equal(E.authority, 'NONE');
  assert.equal(R.delivery_email, E.delivery_email);
  assert.equal(createHash('sha256').update(R.delivery_email).digest('hex'),
    'c471b11cb6e9e4c5491aaea523de811718170832b41ab1b5ffa5fa1d4d5254a5');
  assert.ok(validateReviewedRegistration(R));
  assert.ok(Object.isFrozen(E) && Object.isFrozen(R));
});
test('delivery configuration changes application revision, not identity or binding', () => {
  for (const key of ['project_id', 'owner_user_id', 'issuer', 'audience',
    'project_generation', 'owner_generation', 'binding_generation']) assert.equal(R[key], D.provider[key]);
  assert.equal(R.application_generation, D.provider.application_generation + 1);
  assert.equal(G, R.application_generation);
  assert.notEqual(R.deployment_revision, D.provider.deployment_revision);
});
test('old current control cannot validate the new delivery registration', () => {
  const old = registerReviewedDeployment(D.provider);
  const pending = registerReviewedDeployment(R);
  assert.equal(registrationCurrent(pending, currentControlRecord(createReviewedCurrentControl(old))), false);
});
test('email cannot substitute exact native Owner subject', () => {
  assert.notEqual(R.owner_user_id, R.delivery_email);
  assert.equal(validateReviewedRegistration({ ...R, owner_user_id: R.delivery_email }), false);
});
test('old application-bound public keyset cannot be silently promoted', () => {
  assert.equal(pinnedKeys(D.keyset, R, D.keyset.valid_from), null);
  assert.equal(E.keyset_review_status, 'PENDING_OWNER_REVIEW_FOR_NEW_GENERATION');
  assert.equal(D.keyset.application_generation, D.provider.application_generation);
});
test('original pin expires exactly at reviewed deadline', () => {
  assert.equal(pinnedKeys(D.keyset, D.provider, D.keyset.valid_until), null);
  assert.ok(pinnedKeys(D.keyset, D.provider, D.keyset.valid_until - 1));
});
test('new email and credential presence cannot enable live assembly', () => {
  const configuration = { ...D, registration_generation: G, provider: R };
  Object.defineProperty(configuration, 'STYTCH_SECRET', { get() { throw Error('OFFLINE_CREDENTIAL_READ'); } });
  assert.equal(liveSelectionAllowed(configuration, R), false);
  assert.equal(createProtectedStytchTransport(configuration, R).mode, 'FAKE_DISABLED');
});
test('candidate is not imported by current public or production entrypoint', () => {
  for (const path of ['future-deployment/diagnostic-entry.js', 'lib/server/diagnostic-service.js',
    'future-deployment/app.js', 'future-deployment/index.html', 'future-deployment/owner-transient.js']) {
    const content = readFileSync(new URL('../' + path, import.meta.url), 'utf8');
    assert.ok(!content.includes('pending-delivery-review') && !content.includes(E.delivery_email));
  }
  assert.equal(D.provider.delivery_email, null);
  assert.equal(D.registration_generation, 1);
});

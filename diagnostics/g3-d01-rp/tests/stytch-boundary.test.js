import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createStytchLiveAdapter, createFixtureTransport, createOfflineStytchHarness,
  LIVE_ADAPTER_BUILD_ENABLED } from '../lib/stytch-live-adapter.js';
import entrypoint from '../api/diagnostic.js';

function read(p) { return readFileSync(new URL(`../${p}`, import.meta.url), 'utf8'); }
test('new adapter is absent from unchanged deployed/static import graph', () => {
  const graph = ['api/diagnostic.js', 'lib/http.js', 'lib/policy.js', 'lib/adapter.js',
    'public/index.html', 'public/app.js', 'public/app.css', 'package.json', 'vercel.json'];
  for (const file of graph) {
    assert.equal(/stytch-(?:live-adapter|identity|projection)/.test(read(file)), false, file);
  }
  assert.equal(LIVE_ADAPTER_BUILD_ENABLED, false);
});
test('new modules have no networking, secret/env read, logging or arbitrary code import', () => {
  for (const file of ['lib/stytch-live-adapter.js', 'lib/stytch-identity.js', 'lib/stytch-projection.js']) {
    const source = read(file).replace(/\/\/[^\n]*/g, '');
    for (const pattern of [/\bfetch\s*\(/, /\bprocess\s*\.\s*env\b/, /\bconsole\s*\./,
      /\bimport\s*\(/, /\brequire\s*\(/, /\b(?:eval|Function)\s*\(/,
      /from\s*['"](?:node:)?(?:https?|net|tls|child_process|fs)[^'"]*['"]/, /from\s*['"][^'"]*ash[^'"]*['"]/
    ]) assert.equal(pattern.test(source), false, `${file}:${pattern}`);
  }
});
test('hard-disabled constructor performs zero calls even with malicious credential/client getters', async () => {
  let access = 0; let network = 0;
  const poisoned = new Proxy({}, { get() { ++access; throw new Error('must not inspect'); } });
  const original = globalThis.fetch;
  globalThis.fetch = () => { ++network; throw new Error('network forbidden'); };
  try {
    const adapter = createStytchLiveAdapter(poisoned, poisoned);
    for (const op of ['sendEmailOtp', 'authenticateEmailOtp', 'startTotpEnrollment',
      'authenticateTotp', 'authenticateSession', 'revokeSession']) {
      const output = await adapter[op](poisoned); assert.equal(output.result, 'DENY');
    }
    assert.equal(access, 0); assert.equal(network, 0);
  } finally { globalThis.fetch = original; }
});
test('default deployment entrypoint remains labelled FAKE_DISABLED; no fake promotion endpoint', async () => {
  const res = { headers: {}, setHeader(k, v) { this.headers[k] = v; }, end(body) { this.body = JSON.parse(body); } };
  await entrypoint({ method: 'GET', url: '/api/diagnostic', headers: { host: 'nexus-g3-qual.vercel.app' } }, res);
  assert.equal(res.statusCode, 200); assert.equal(res.body.adapter_mode, 'FAKE_DISABLED');
  assert.equal(res.body.authority, 'NONE'); assert.equal(res.body.real_admission, 'DISABLED');
  assert.equal(res.body.qualified_live, false); assert.equal(res.body.evidence_source, 'FAKE_DISABLED');
});
test('fixture transport rejects functions/network promise injection, and serializes no requests', () => {
  assert.throws(() => createFixtureTransport([() => {}]));
  assert.throws(() => createFixtureTransport([Promise.resolve({})]));
  assert.equal(JSON.stringify(createFixtureTransport([])), '{"mode":"OFFLINE_CONTRACT_ONLY"}');
});
test('missing/malformed/live registration stays disabled with no secret input reading', async () => {
  for (const registration of [undefined, {}, { environment: 'LIVE' }]) {
    const adapter = createOfflineStytchHarness({ registration, transport: createFixtureTransport([]), publicKeys: [], clock: Date.now });
    assert.equal(adapter.mode, 'FAKE_DISABLED'); assert.equal((await adapter.authenticateSession()).result, 'DENY');
  }
});

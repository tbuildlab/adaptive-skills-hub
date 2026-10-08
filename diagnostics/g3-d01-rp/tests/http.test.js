import test from 'node:test';
import assert from 'node:assert/strict';
import { makeHandler } from '../lib/http.js';
import { ORIGIN } from '../lib/policy.js';
import entrypoint from '../api/diagnostic.js';
const host = new URL(ORIGIN).host;
async function call(handler, changes = {}) {
  const headers = { host, ...changes.headers };
  const req = { method: 'GET', url: '/api/diagnostic', ...changes, headers };
  const response = { statusCode: 0, headers: {}, setHeader(k, v) { this.headers[k] = v; },
    end(s) { this.body = JSON.parse(s); } };
  await handler(req, response); return response;
}
async function browser() {
  let now = 1000000;
  const handler = makeHandler({ clock: () => now }); const first = await call(handler);
  const cookie = first.headers['Set-Cookie'].split(';')[0];
  const headers = { origin: ORIGIN, cookie, 'x-g3-csrf': first.body.csrf, 'content-type': 'application/json' };
  return { handler, first, headers, time(n) { now = n; },
    async post(action, extra = {}) { return call(handler, { method: 'POST', headers, body: { action }, ...extra }); } };
}
test('22 arbitrary redirect/callback/query injection rejected', async () => {
  const b = await browser();
  for (const body of [{ action: 'PAGE', redirect: 'https://attacker.invalid' },
    { action: 'PAGE', callback: '/evil' }, { action: 'PAGE', project_id: 'other' }]) {
    assert.equal((await call(b.handler, { method: 'POST', headers: b.headers, body })).statusCode, 400);
  }
  assert.equal((await call(b.handler, { url: '/api/diagnostic?redirect=https://attacker.invalid' })).statusCode, 403);
});
test('23 hostile Origin/CSRF/cross-site/missing Origin requests reject', async () => {
  const b = await browser();
  for (const change of [{ origin: 'https://attacker.invalid' }, { origin: undefined },
    { 'x-g3-csrf': 'bad' }, { 'x-g3-csrf': undefined }, { 'sec-fetch-site': 'cross-site' }]) {
    const r = await call(b.handler, { method: 'POST', headers: { ...b.headers, ...change }, body: { action: 'LOCAL_LOGOUT' } });
    assert.equal(r.statusCode, 403); assert.equal(r.body.result, 'DENY');
  }
});
test('every mutation provider action is disabled; browser cannot inject fake observations/flag', async () => {
  const b = await browser();
  for (const action of ['EMAIL_START', 'EMAIL_VERIFY', 'TOTP_ENROLLMENT_START', 'TOTP_VERIFY',
    'PAGE', 'DECISION_POST_SIMULATION', 'RECEIPT_SIMULATION', 'INTENT_SIMULATION', 'CLAIM_SIMULATION', 'REVOKE_OBSERVATION']) {
    const r = await b.post(action); assert.equal(r.statusCode, 403);
    assert.equal(r.body.error_class, 'LIVE_DISABLED'); assert.equal(r.body.adapter_mode, 'FAKE_DISABLED');
    assert.equal(r.body.authority, 'NONE'); assert.equal(r.body.qualified_live, false);
  }
  assert.equal((await b.post('PAGE', { body: { action: 'PAGE', G3_D01_LIVE_DIAGNOSTIC_ENABLED: true } })).statusCode, 400);
});
test('no provider network call from any handler branch', async () => {
  const saved = globalThis.fetch; let calls = 0;
  globalThis.fetch = () => { ++calls; throw new Error('network forbidden'); };
  try {
    const b = await browser(); await b.post('EMAIL_START'); await b.post('PAGE');
    await b.post('LOCAL_LOGOUT'); assert.equal(calls, 0);
  } finally { globalThis.fetch = saved; }
});
test('strict Host ignores forwarded-host and denies localhost/preview', async () => {
  for (const wrong of ['localhost:3000', 'preview.vercel.app', 'attacker.invalid', `${host}:443`]) {
    const r = await call(makeHandler(), { headers: { host: wrong, 'x-forwarded-host': host } });
    assert.equal(r.statusCode, 403); assert.equal(r.body.error_class, 'ORIGIN');
  }
});
test('page reload retains CSRF and original expiry; cookie never exported', async () => {
  const b = await browser(); b.time(1200000);
  const r = await call(b.handler, { headers: { cookie: b.headers.cookie } });
  assert.equal(r.body.csrf, b.first.body.csrf); assert.equal(r.headers['Set-Cookie'], undefined);
  assert.equal(JSON.stringify(r.body).includes(b.headers.cookie), false);
  b.time(1300000);
  assert.equal((await b.post('LOCAL_LOGOUT')).body.error_class, 'RETIRED');
});
test('restart/other worker rejects old page cookie, no rehydration', async () => {
  const b = await browser();
  const r = await call(makeHandler(), { headers: { cookie: b.headers.cookie } });
  assert.equal(r.statusCode, 403); assert.equal(r.body.error_class, 'RETIRED');
});
test('local logout retires only local page, second use denies', async () => {
  const b = await browser();
  assert.equal((await b.post('LOCAL_LOGOUT')).body.state, 'LOCAL_CONTEXT_RETIRED');
  assert.equal((await b.post('LOCAL_LOGOUT')).statusCode, 403);
});
test('bounded capacity, duplicate/bad cookies and bad content-type deny', async () => {
  const handler = makeHandler({ capacity: 1 }); await call(handler);
  assert.equal((await call(handler)).body.error_class, 'CAPACITY');
  const b = await browser();
  for (const cookie of [`${b.headers.cookie}; ${b.headers.cookie}`, '__Host-g3d01=bad', 'x'.repeat(2049)]) {
    assert.equal((await call(b.handler, { headers: { cookie } })).statusCode, 400);
  }
  assert.equal((await b.post('PAGE', { headers: { ...b.headers, 'content-type': 'text/plain' } })).statusCode, 400);
});
test('caught error emits fixed enums, no raw exception/environment/header dump', async () => {
  const handler = makeHandler({ clock() { throw new Error('SYNTHETIC_SECRET_SENTINEL'); } });
  const r = await call(handler); assert.equal(r.statusCode, 400);
  assert.equal(JSON.stringify(r.body).includes('SYNTHETIC_SECRET_SENTINEL'), false);
  assert.equal(r.body.error_class, 'REQUEST');
});
test('mutable diagnostic output has security headers, no CORS grant', async () => {
  const b = await browser(); const r = await b.post('PAGE');
  assert.equal(r.headers['Cache-Control'], 'no-store');
  assert.equal(r.headers['X-Frame-Options'], 'DENY');
  assert.equal(r.headers['Access-Control-Allow-Origin'], undefined);
  assert.match(b.first.headers['Set-Cookie'], /Secure; HttpOnly; SameSite=Strict; Max-Age=300$/);
});
test('HTTP clock rollback clears page custody', async () => {
  const b = await browser(); b.time(999999);
  assert.equal((await b.post('PAGE')).body.error_class, 'CLOCK');
  b.time(1000000); assert.equal((await b.post('PAGE')).body.error_class, 'RETIRED');
});
test('actual Vercel entrypoint returns disabled labelled output without registration/credentials', async () => {
  const r = await call(entrypoint);
  assert.equal(r.statusCode, 200); assert.equal(r.body.live_diagnostic_enabled, false);
  assert.equal(r.body.adapter_mode, 'FAKE_DISABLED');
  assert.equal(r.body.diagnostic, 'NEXUS_G3_D01_DIAGNOSTIC_ONLY');
  assert.equal(r.body.classification, 'LIVE_DIAGNOSTIC_EVIDENCE_ONLY');
  assert.equal(r.body.result, 'DENY'); assert.equal(r.body.authority, 'NONE');
});

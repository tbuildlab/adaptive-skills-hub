import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { generateKeyPairSync, sign } from 'node:crypto';
import { createOfflineRegistration, createOfflineCurrentControl, validateReviewedRegistration } from '../lib/server/provider-registration.js';
import { createOfflineCredentials, loadServerCredentials } from '../lib/server/credential-custody.js';
import { createOfflineIo, createOfflineStytchTransport, createProtectedStytchTransport } from '../lib/server/stytch-transport.js';
import { safeResult, safeError, ClosedFailure, liveSelectionAllowed, PATHS } from '../lib/server/pre-secret-policy.js';
import { createOfflineOwnerTransientView, createOwnerTransientView } from '../future-owner-ui/totp-transient.js';
import { createStytchLiveAdapter } from '../lib/stytch-live-adapter.js';
import entrypoint from '../api/diagnostic.js';

const project = 'project-test-00000000-0000-4000-8000-000000000001';
const T = Date.UTC(2026, 9, 8); const iso = n => new Date(n).toISOString();
const { privateKey, publicKey } = generateKeyPairSync('rsa', { modulusLength: 2048 });
const jwk = { ...publicKey.export({ format: 'jwk' }), kid: 'fixture-pre-secret', alg: 'RS256', use: 'sig' };
function registration() {
  return { provider: 'STYTCH_CONSUMER', environment: 'TEST', project_id: project, owner_user_id: 'fixture-owner',
    project_generation: 1, application_generation: 1, owner_generation: 1, binding_generation: 1,
    origin: 'https://nexus-g3-qual.vercel.app', factors: ['EMAIL_OTP', 'TOTP'], session_max_minutes: 15,
    context_max_ms: 300000, issuer: `stytch.com/${project}`, audience: project,
    deployment_revision: 'fixture-revision', source: 'OFFLINE_SYNTHETIC', review_id: 'fixture-review', delivery_email: 'owner@example.invalid' };
}
const control = r => Object.fromEntries(['project_id', 'owner_user_id', 'project_generation', 'application_generation',
  'owner_generation', 'binding_generation', 'deployment_revision'].map(k => [k, r[k]]));
function jwt(extra = {}) {
  const h = Buffer.from(JSON.stringify({ alg: 'RS256', typ: 'JWT', kid: jwk.kid })).toString('base64url');
  const c = Buffer.from(JSON.stringify({ iss: `stytch.com/${project}`, aud: project, sub: 'fixture-owner',
    iat: T / 1000, nbf: T / 1000, exp: T / 1000 + 300, ...extra })).toString('base64url');
  return `${h}.${c}.${sign('RSA-SHA256', Buffer.from(`${h}.${c}`), privateKey).toString('base64url')}`;
}
function raw(two = false, extra = {}) {
  const factors = [{ type: 'otp', delivery_method: 'email', last_authenticated_at: iso(T) }];
  if (two) factors.push({ type: 'totp', delivery_method: 'authenticator_app', last_authenticated_at: iso(T) });
  return { status_code: 200, user_id: 'fixture-owner', method_id: 'fixture-email', totp_id: 'fixture-totp',
    session_token: 'OFFLINE_SESSION_PLACEHOLDER', session_jwt: jwt(extra),
    user: { user_id: 'fixture-owner', status: 'active', is_locked: false },
    session: { session_id: 'fixture-session', user_id: 'fixture-owner', expires_at: iso(T + 900000), authentication_factors: factors } };
}
const reply = body => ({ status: 200, headers: { 'content-type': 'application/json' }, chunks: [JSON.stringify(body)] });
const sent = () => reply({ status_code: 200, user_id: 'fixture-owner', email_id: 'fixture-email' });
function fixture(replies = [sent()], modify = {}) {
  const r = registration(); const reg = createOfflineRegistration(r);
  const credentials = createOfflineCredentials({ STYTCH_PROJECT_ID: project, STYTCH_SECRET: 'OFFLINE_CREDENTIAL_PLACEHOLDER' }, reg);
  const io = createOfflineIo(replies); const current = createOfflineCurrentControl(control(r)); let now = T;
  const adapter = createOfflineStytchTransport({ registration: reg, credentials, io, current, publicKeys: [jwk], clock: () => now, ...modify });
  return { adapter, credentials, io, current, reg, time(n) { now = n; } };
}
function deny(o) { assert.equal(o.result, 'DENY'); assert.equal(o.authority, 'NONE'); assert.equal(o.qualified_live, false); }
function pass(o) { assert.equal(o.result, 'PASS'); assert.equal(o.authority, 'NONE'); assert.equal(o.qualified_live, false); }
async function primary(f) { pass(await f.adapter.EMAIL_OTP_SEND()); pass(await f.adapter.EMAIL_OTP_AUTHENTICATE({ code: '000000' })); return f; }
async function ready(tail = []) {
  const f = await primary(fixture([sent(), reply(raw()), reply(raw()), reply(raw(true)), reply(raw(true)), ...tail]));
  pass(await f.adapter.TOTP_AUTHENTICATE({ code: '000000' })); return f;
}
const read = name => readFileSync(new URL(`../${name}`, import.meta.url), 'utf8');
function ui(options = {}) {
  let now = T; const children = []; const handlers = new Map();
  const document = { createElement() { return { textContent: '', value: '', disabled: false, setAttribute() {}, addEventListener() {} }; } };
  const root = { replaceChildren(...nodes) { children.splice(0, children.length, ...nodes); } };
  const events = { addEventListener(k, v) { handlers.set(k, v); }, removeEventListener(k) { handlers.delete(k); } };
  const expected = { project_id: project, user_id: 'fixture-owner', session_id: 'fixture-session', owner_generation: 1, binding_generation: 1, worker_id: 'fixture-worker' };
  const context = { source: 'OFFLINE_SYNTHETIC', state: 'PRIMARY_FACTOR_VERIFIED', ...expected, started_at: T, expires_at: T + 300000 };
  const view = createOfflineOwnerTransientView({ context, expected, clock: () => now, document, root, events, ...options });
  return { view, children, handlers, time(n) { now = n; }, show() { return view.showEnrollment({ secret: 'OFFLINE_TOTP_SEED', recovery_codes: ['OFFLINE_RECOVERY'] }); } };
}

test('01 arbitrary endpoint rejected before IO', async () => { const f = fixture(); deny(await f.adapter.EMAIL_OTP_SEND({ endpoint: '/v1/users' })); assert.equal(f.io.requestShapes().length, 0); });
test('02 arbitrary URL rejected before IO', async () => { const f = fixture(); deny(await f.adapter.EMAIL_OTP_SEND({ url: 'https://other.invalid' })); });
test('03 HTTP rejected; fixed HTTPS request options only', async () => { const f = fixture(); deny(await f.adapter.EMAIL_OTP_SEND({ protocol: 'http:' })); const g = fixture(); pass(await g.adapter.EMAIL_OTP_SEND()); assert.equal(g.io.requestShapes()[0].protocol, 'https:'); });
test('04 redirects denied without following Location', async () => { const f = fixture([{ status: 302, headers: { location: 'https://other.invalid' }, chunks: [] }]); deny(await f.adapter.EMAIL_OTP_SEND()); assert.equal(f.io.requestShapes().length, 1); });
test('05 oversized response rejected by byte count and Content-Length', async () => {
  for (const r of [{ status: 200, headers: { 'content-type': 'application/json' }, chunks: ['x'.repeat(65537)] },
    { status: 200, headers: { 'content-type': 'application/json', 'content-length': '65537' }, chunks: [] }]) deny(await fixture([r]).adapter.EMAIL_OTP_SEND());
});
test('06 wrong content type and compressed body reject', async () => { for (const headers of [{ 'content-type': 'text/html' }, { 'content-type': 'application/json', 'content-encoding': 'gzip' }]) deny(await fixture([{ ...sent(), headers }]).adapter.EMAIL_OTP_SEND()); });
test('07 timeout rejects without retry', async () => { const f = fixture([{ ...sent(), delay_ms: 4000 }]); deny(await f.adapter.EMAIL_OTP_SEND()); deny(await f.adapter.EMAIL_OTP_SEND()); assert.equal(f.io.requestShapes().length, 1); });
test('08 DNS TLS and network failures are fixed classes', async () => { for (const failure of ['DNS', 'TLS', 'NETWORK']) { const o = await fixture([{ failure }]).adapter.EMAIL_OTP_SEND(); deny(o); assert.equal(o.error_class, 'PROVIDER_UNAVAILABLE'); } });
test('09 state-changing retries prohibited', async () => { const f = fixture([{ status: 503, headers: {}, chunks: [] }, sent()]); deny(await f.adapter.EMAIL_OTP_SEND()); deny(await f.adapter.EMAIL_OTP_SEND()); assert.equal(f.io.requestShapes().length, 1); });
test('10 broad user revoke prohibited', async () => { const f = await primary(fixture([sent(), reply(raw())])); deny(await f.adapter.SESSION_REVOKE_EXACT({ user_id: 'fixture-owner' })); });
test('11 exact retained session revoke request shape', async () => { const f = await primary(fixture([sent(), reply(raw()), reply({ status_code: 200 })])); pass(await f.adapter.SESSION_REVOKE_EXACT()); const s = f.io.requestShapes().at(-1); assert.deepEqual(s.keys, ['session_id']); assert.equal(s.exact_session_id, 'fixture-session'); });
test('12 missing credential disables construction', async () => { const f = fixture([], { credentials: null }); assert.equal(f.adapter.mode, 'FAKE_DISABLED'); deny(await f.adapter.EMAIL_OTP_SEND()); });
test('13 malformed credentials and accessors reject', () => { const reg = createOfflineRegistration(registration()); for (const v of [{}, { STYTCH_PROJECT_ID: project, STYTCH_SECRET: 'OFFLINE_BAD' }, { get STYTCH_SECRET() { throw new Error('not invoked'); }, STYTCH_PROJECT_ID: project }]) assert.equal(createOfflineCredentials(v, reg), null); });
test('14 secret presence cannot enable live or network', async () => {
  let reads = 0; let calls = 0; const poisoned = new Proxy({}, { get() { reads++; throw new Error('forbidden'); } });
  const saved = globalThis.fetch; globalThis.fetch = () => { calls++; throw new Error('forbidden'); };
  try { const a = createProtectedStytchTransport(poisoned, poisoned); deny(await a.EMAIL_OTP_SEND()); assert.equal(loadServerCredentials(poisoned, poisoned), null); assert.equal(reads, 0); assert.equal(calls, 0); }
  finally { globalThis.fetch = saved; }
});
test('15 no environment enumeration or credential discovery', () => { const s = read('lib/server/credential-custody.js'); assert.equal(/Object\.(?:keys|entries|values)\(process\.env|\.env\[|readFile|homedir|OIDC_TOKEN|dotenv/.test(s), false); assert.equal((s.match(/process\.env\./g) ?? []).length, 2); });
function boundary() { for (const p of ['public/app.js', 'public/index.html', 'api/diagnostic.js', 'lib/http.js', 'lib/adapter.js']) assert.equal(/server\/|credential-custody|stytch-transport|future-owner-ui/.test(read(p)), false); }
test('16 current client cannot import credential loader', boundary);
test('17 current client cannot import live transport', boundary);
test('18 browser adapter mode cannot select transport', async () => { assert.equal(liveSelectionAllowed({ mode: 'LIVE' }, { source: 'OWNER_REVIEWED' }), false); deny(await createProtectedStytchTransport({ mode: 'LIVE' }).SESSION_AUTHENTICATE()); });
test('19 browser project selector rejected', async () => { deny(await fixture().adapter.EMAIL_OTP_SEND({ project_id: project })); });
test('20 unregistered project cannot construct registered model', () => { assert.equal(createOfflineRegistration({ ...registration(), project_id: 'P_OWNER' }), null); });
test('21 unregistered user fails native/signed equality', async () => { const b = raw(); b.user.user_id = 'fixture-other'; b.session.user_id = 'fixture-other'; b.user_id = 'fixture-other'; const f = fixture([sent(), reply(b)]); pass(await f.adapter.EMAIL_OTP_SEND()); deny(await f.adapter.EMAIL_OTP_AUTHENTICATE({ code: '000000' })); });
test('22 P_OTHER cannot be Owner by alias or wrong project', async () => { const b = raw(false, { aud: 'P_OTHER' }); const f = fixture([sent(), reply(b)]); pass(await f.adapter.EMAIL_OTP_SEND()); deny(await f.adapter.EMAIL_OTP_AUTHENTICATE({ code: '000000' })); });
test('23 email equality never establishes Owner', async () => { const r = { ...registration(), owner_user_id: 'owner@example.invalid' }; assert.equal(createOfflineRegistration(r), null); const f = fixture([reply({ status_code: 200, email_id: 'fixture-email', user_id: 'fixture-nonowner', email: 'owner@example.invalid' })]); deny(await f.adapter.EMAIL_OTP_SEND()); });
test('24 changed owner generation retires existing context before IO', async () => { const f = await primary(fixture([sent(), reply(raw())])); f.current.replace({ ...control(registration()), owner_generation: 2 }); deny(await f.adapter.TOTP_AUTHENTICATE({ code: '000000' })); assert.equal(f.io.requestShapes().length, 2); });
test('25 changed binding generation retires existing context', async () => { const f = await primary(fixture([sent(), reply(raw())])); f.current.replace({ ...control(registration()), binding_generation: 2 }); deny(await f.adapter.TOTP_CREATE()); });
for (const [number, field, value] of [[26, 'iss', 'https://invented.invalid'], [27, 'aud', 'P_OTHER'], [28, 'sub', 'fixture-other']]) {
  test(`${number} wrong ${field} rejects signed identity`, async () => { const f = fixture([sent(), reply(raw(false, { [field]: value }))]); pass(await f.adapter.EMAIL_OTP_SEND()); deny(await f.adapter.EMAIL_OTP_AUTHENTICATE({ code: '000000' })); });
}
test('29 JWT-positive remote-negative still denies', async () => { const b = raw(true); b.user.status = 'deleted'; const f = await ready([reply(b)]); deny(await f.adapter.SESSION_AUTHENTICATE()); });
test('30 TOTP transient seed stays out of evidence and default UI', () => { const v = ui(); v.show(); assert.equal(JSON.stringify(v.view.status()).includes('OFFLINE_TOTP_SEED'), false); v.view.clear('DENY'); assert.equal(v.children.length, 0); deny(createOwnerTransientView().showEnrollment({ secret: 'OFFLINE_TOTP_SEED' })); });
test('31 recovery codes removed from evidence and retained DOM nodes', () => { const v = ui(); v.show(); const old = [...v.children]; assert.equal(JSON.stringify(v.view).includes('OFFLINE_RECOVERY'), false); v.view.clear('DENY'); assert.equal(old.every(n => n.textContent === '' && n.value === '' && n.disabled), true); });
test('32 provider free-text error redacted', () => { assert.equal(safeError(new Error('OFFLINE_PROVIDER_SECRET')), 'UNKNOWN'); assert.equal(JSON.stringify(safeResult({ message: 'OFFLINE_PROVIDER_SECRET' })).includes('OFFLINE_PROVIDER_SECRET'), false); });
test('33 stacks never enter closed error JSON', () => { const e = new ClosedFailure('TIMEOUT'); e.stack = 'OFFLINE_SECRET_STACK'; assert.equal(JSON.stringify(e).includes('OFFLINE_SECRET_STACK'), false); });
test('34 Authorization redacted from evidence and fixture introspection', async () => { const f = fixture(); const o = await f.adapter.EMAIL_OTP_SEND(); assert.equal(/Authorization|Basic|OFFLINE_CREDENTIAL/.test(JSON.stringify([o, f.io.requestShapes(), f.credentials])), false); });
test('35 cookies never enter closed result', () => { const o = safeResult({ cookie: 'OFFLINE_COOKIE' }); assert.equal(JSON.stringify(o).includes('OFFLINE_COOKIE'), false); });
test('36 session token never enters transport result', async () => { const f = await primary(fixture([sent(), reply(raw())])); assert.equal(JSON.stringify(f.adapter).includes('OFFLINE_SESSION'), false); f.adapter.retire(); });
test('37 reload retires instead of refreshing deadline', () => { const v = ui(); v.show(); v.handlers.get('beforeunload')(); assert.equal(v.children.length, 0); deny(v.view.showEnrollment({ secret: 'OFFLINE_TOTP_SEED', recovery_codes: [] })); });
test('38 enrollment cannot extend absolute context deadline', () => { const v = ui(); v.time(T + 299999); v.show(); v.time(T + 300000); assert.equal(v.view.status().state, 'RETIRED'); assert.equal(v.children.length, 0); });
test('39 worker loss/restart retires and cannot restore view', () => { const v = ui(); v.show(); v.view.clear('WORKER_LOSS'); assert.equal(v.children.length, 0); const g = ui({ expected: { project_id: project, user_id: 'fixture-owner', session_id: 'fixture-session', owner_generation: 1, binding_generation: 1, worker_id: 'other-worker' } }); deny(g.show()); });
test('40 actual deployed entrypoint stays FAKE_DISABLED', async () => { const res = { setHeader() {}, end(body) { this.body = JSON.parse(body); } }; await entrypoint({ method: 'GET', url: '/api/diagnostic', headers: { host: 'nexus-g3-qual.vercel.app' } }, res); assert.equal(res.body.adapter_mode, 'FAKE_DISABLED'); assert.equal(res.body.real_admission, 'DISABLED'); });
test('41 credential loader cannot activate current route', async () => { const f = fixture(); assert.equal(loadServerCredentials({ mode: 'OWNER_REVIEWED_TEST_DIAGNOSTIC' }, registration()), null); deny(await createStytchLiveAdapter(f.credentials).authenticateSession()); });
test('42 fake IO or credentials cannot be production promoted', async () => { const f = fixture(); deny(await createProtectedStytchTransport({ io: f.io, credentials: f.credentials }, registration()).EMAIL_OTP_SEND()); assert.equal(createOfflineStytchTransport({ registration: f.reg, credentials: f.credentials, io: { kind: 'OFFLINE_IO' }, current: f.current }).mode, 'FAKE_DISABLED'); });
test('43 production authority imports prohibited in prepared modules', () => { for (const p of ['lib/server/stytch-transport.js', 'lib/server/credential-custody.js', 'lib/server/provider-registration.js', 'lib/server/pre-secret-policy.js']) assert.equal(/from\s*['"][^'"]*(?:ash\/|g3_production|approval|admission|dispatch)[^'"]*['"]|AdmissionIntent|DispatchAttempt|ApprovalGrant/.test(read(p)), false); });
test('44 real admission remains disabled in all result classes', () => { for (const e of ['DISABLED', 'UNKNOWN', 'TIMEOUT', 'AUTH_REJECTED', 'SESSION_INVALID', 'RATE_LIMITED', 'PROVIDER_UNAVAILABLE', 'MALFORMED_RESPONSE']) { const o = safeResult(e); deny(o); assert.equal(o.real_admission, 'DISABLED'); } });
test('closed registration cannot be TOFU or browser reviewed source', () => { const r = registration(); assert.equal(validateReviewedRegistration(r), false); assert.equal(validateReviewedRegistration({ ...r, source: 'OWNER_REVIEWED' }), true); assert.equal(validateReviewedRegistration({ ...r, source: 'OWNER_REVIEWED', email: r.delivery_email }), false); });
test('native HTTPS preparation has TLS, absolute timeout, stream bounds and no retry', () => { const s = read('lib/server/stytch-transport.js'); assert.equal(s.includes('rejectUnauthorized: true'), true); assert.equal(s.includes('setTimeout(() => finish'), true); assert.equal(s.includes('size > RESPONSE_MAX_BYTES'), true); assert.equal(s.includes('req?.destroy()'), true); assert.equal(s.includes('Location'), false); assert.deepEqual(Object.keys(PATHS), ['EMAIL_OTP_SEND', 'EMAIL_OTP_AUTHENTICATE', 'TOTP_CREATE', 'TOTP_AUTHENTICATE', 'SESSION_AUTHENTICATE', 'SESSION_REVOKE_EXACT']); });
test('malformed JSON, invalid UTF-8, truncated and multi-chunk bodies deny', async () => {
  for (const r of [{ ...sent(), chunks: ['{'] }, { ...sent(), chunks: [new Uint8Array([255])] },
    { ...sent(), headers: { 'content-type': 'application/json', 'content-length': '1' } },
    { ...sent(), chunks: ['x'.repeat(40000), 'x'.repeat(40000)] }]) deny(await fixture([r]).adapter.EMAIL_OTP_SEND());
});
test('TOTP create is pre/post rechecked; authenticated factors rechecked and material stays private', async () => {
  const enrollment = { status_code: 200, user_id: 'fixture-owner', user: { user_id: 'fixture-owner' }, totp_id: 'fixture-totp',
    secret: 'OFFLINE_TOTP_SEED', qr_code: 'OFFLINE_QR', recovery_codes: ['OFFLINE_RECOVERY'] };
  const f = await primary(fixture([sent(), reply(raw()), reply(raw()), reply(enrollment), reply(raw()), reply(raw()), reply(raw(true)), reply(raw(true))]));
  const o = await f.adapter.TOTP_CREATE(); pass(o); assert.equal(/OFFLINE_(?:TOTP|RECOVERY|QR)/.test(JSON.stringify(o)), false);
  pass(await f.adapter.TOTP_AUTHENTICATE({ code: '000000' }));
  assert.deepEqual(f.io.requestShapes().filter(s => s.op === 'SESSION_AUTHENTICATE').map(s => s.keys), [['session_token'], ['session_token'], ['session_token'], ['session_token']]); f.adapter.retire();
});
test('UI clears on every terminal cause and denies raw/live material', () => {
  for (const reason of ['SUCCESS', 'DENY', 'TIMEOUT', 'LOGOUT', 'SWITCH', 'RELOAD', 'WORKER_LOSS', 'MISMATCH']) { const v = ui(); v.show(); v.view.clear(reason); assert.equal(v.children.length, 0); }
  const v = ui(); deny(v.view.showEnrollment({ secret: 'NOT_A_PROVIDER_SEED', recovery_codes: [] }));
});
test('malformed enrollment cleanup, missing OTP user and invalid initial clock fail closed', async () => {
  const enrollment = { status_code: 200, user_id: 'fixture-owner', user: { user_id: 'fixture-owner' },
    totp_id: 'fixture-totp', secret: 'OFFLINE_TOTP_SEED', qr_code: 'OFFLINE_QR', recovery_codes: 'OFFLINE_BAD_ARRAY' };
  const f = await primary(fixture([sent(), reply(raw()), reply(raw()), reply(enrollment)]));
  deny(await f.adapter.TOTP_CREATE()); deny(await f.adapter.TOTP_CREATE());
  const b = raw(); delete b.user_id;
  const g = fixture([sent(), reply(b)]); pass(await g.adapter.EMAIL_OTP_SEND()); deny(await g.adapter.EMAIL_OTP_AUTHENTICATE({ code: '000000' }));
  const h = fixture(); h.time(-1); deny(await h.adapter.EMAIL_OTP_SEND()); assert.equal(h.io.requestShapes().length, 0);
});

import test from 'node:test';
import assert from 'node:assert/strict';
import { generateKeyPairSync, sign } from 'node:crypto';
import { createOfflineStytchHarness, createFixtureTransport, createStytchLiveAdapter } from '../lib/stytch-live-adapter.js';
import { evidence, timestamp } from '../lib/stytch-projection.js';
import { verifyStytchIdentity } from '../lib/stytch-identity.js';
import { POINTS } from '../lib/policy.js';
import { selectAdapter } from '../lib/adapter.js';

// Synthetic signing key only in test-process memory; never PEM/export/persist private key.
const { privateKey, publicKey } = generateKeyPairSync('rsa', { modulusLength: 2048 });
const jwk = { ...publicKey.export({ format: 'jwk' }), kid: 'fixture-key', alg: 'RS256', use: 'sig' };
const T0 = Date.UTC(2026, 9, 8, 0, 0, 0);
const iso = ms => new Date(ms).toISOString();
const reg = () => ({ project_id: 'project-test-00000000-0000-4000-8000-000000000001',
  environment: 'TEST', issuer: 'stytch.com/project-test-00000000-0000-4000-8000-000000000001',
  client_id: 'project-test-00000000-0000-4000-8000-000000000001', owner_user_id: 'fixture-owner',
  owner_generation: 1, binding_generation: 1, owner_email: 'owner@example.invalid' });
function jwt(overrides = {}, header = {}) {
  const h = Buffer.from(JSON.stringify({ alg: 'RS256', typ: 'JWT', kid: jwk.kid, ...header })).toString('base64url');
  const c = Buffer.from(JSON.stringify({ iss: reg().issuer, aud: reg().project_id,
    sub: reg().owner_user_id, iat: T0 / 1000, nbf: T0 / 1000, exp: T0 / 1000 + 300,
    ...overrides })).toString('base64url');
  return `${h}.${c}.${sign('RSA-SHA256', Buffer.from(`${h}.${c}`), privateKey).toString('base64url')}`;
}
function raw(two = false, claims = {}) {
  const factors = [{ type: 'otp', delivery_method: 'email', last_authenticated_at: iso(T0) }];
  if (two) factors.push({ type: 'totp', delivery_method: 'authenticator_app', last_authenticated_at: iso(T0) });
  return { status_code: 200, request_id: '00000000-0000-4000-8000-000000000011',
    user_id: reg().owner_user_id, method_id: 'fixture-email', totp_id: 'fixture-totp',
    session_token: 'OFFLINE_SESSION_PLACEHOLDER', session_jwt: jwt(claims),
    user: { user_id: reg().owner_user_id, status: 'active', is_locked: false,
      untrusted_metadata: { ignored: 'OFFLINE_SECRET_UNKNOWN_FIELD' } },
    session: { session_id: 'fixture-session', user_id: reg().owner_user_id,
      expires_at: iso(T0 + 900000), authentication_factors: factors } };
}
const response = body => ({ kind: 'RESPONSE', status: 200, body });
const send = () => response({ status_code: 200, request_id: '00000000-0000-4000-8000-000000000012',
  user_id: reg().owner_user_id, email_id: 'fixture-email' });
function fixture(tail = [], options = {}) {
  let now = T0;
  const initial = options.initial ?? raw();
  const two = options.two ?? raw(true);
  const transport = createFixtureTransport([send(), response(initial), response(raw()), response(two), ...tail]);
  const adapter = createOfflineStytchHarness({ registration: reg(), transport, publicKeys: [jwk],
    clock: () => now, ...options });
  return { adapter, transport, time(n) { now = n; } };
}
function pass(output) {
  assert.equal(output.result, 'PASS'); assert.equal(output.authority, 'NONE');
  assert.equal(output.qualified_live, false); assert.equal(output.evidence_source, 'OFFLINE_ADAPTER_FIXTURE');
}
function deny(output) {
  assert.equal(output.result, 'DENY'); assert.equal(output.authority, 'NONE');
  assert.equal(output.real_admission, 'DISABLED'); assert.equal(output.qualified_live, false);
}
async function primary(f) {
  pass(await f.adapter.sendEmailOtp({ email: reg().owner_email }));
  return f.adapter.authenticateEmailOtp({ code: '000000' });
}
async function ready(f) {
  pass(await primary(f)); pass(await f.adapter.authenticateTotp({ code: '000000' })); return f;
}
async function remoteMutant(mutate) {
  const b = raw(true); mutate(b);
  const f = await ready(fixture([response(b)]));
  const result = await f.adapter.authenticateSession({ point: 'PAGE' });
  deny(result); deny(await f.adapter.authenticateSession({ point: 'PAGE' })); return result;
}

test('01 exact email OTP send request: pinned Test URL, send-only, fixed expiration/locale', async () => {
  const f = fixture(); pass(await f.adapter.sendEmailOtp({ email: reg().owner_email }));
  const r = f.transport.requests()[0];
  assert.equal(r.url, 'https://test.stytch.com/v1/otps/email/send'); assert.equal(r.method, 'POST');
  assert.deepEqual(Object.keys(r.body).sort(), ['email', 'expiration_minutes', 'locale']);
  assert.equal(r.body.email, reg().owner_email); assert.equal(r.body.expiration_minutes, 5);
  assert.equal(r.body.locale, 'en'); assert.equal(r.redirect, 'error'); assert.equal(r.retry, 'NEVER');
  assert.equal(r.headers.Authorization.startsWith('Basic '), true);
});
test('02 exact initial 15-minute email authentication request', async () => {
  const f = fixture(); pass(await primary(f)); const r = f.transport.requests()[1];
  assert.equal(r.url, 'https://test.stytch.com/v1/otps/authenticate');
  assert.deepEqual(Object.keys(r.body).sort(), ['code', 'method_id', 'session_duration_minutes']);
  assert.equal(r.body.session_duration_minutes, 15); assert.equal(r.body.method_id, 'fixture-email');
});
test('03 recheck has no session extension and uses exact retained opaque lineage', async () => {
  const f = await ready(fixture([response(raw(true))])); pass(await f.adapter.authenticateSession({ point: 'PAGE' }));
  const r = f.transport.requests().at(-1);
  assert.equal(r.url, 'https://test.stytch.com/v1/sessions/authenticate');
  assert.deepEqual(Object.keys(r.body), ['session_token']);
  assert.equal(r.body.session_token === 'OFFLINE_SESSION_PLACEHOLDER', true);
  assert.equal(Object.hasOwn(r.body, 'session_duration_minutes'), false);
});
test('04 no custom claims in any operation or recheck', async () => {
  const f = await ready(fixture([response(raw(true))])); pass(await f.adapter.authenticateSession({ point: 'PAGE' }));
  for (const r of f.transport.requests()) {
    assert.equal(Object.hasOwn(r.body, 'session_custom_claims'), false);
    assert.equal(Object.hasOwn(r.body, 'custom_claims'), false);
  }
});
test('05 same project/user/session factors and all five point-time fixture labels', async () => {
  const f = await ready(fixture(POINTS.map(() => response(raw(true)))));
  for (const point of POINTS) {
    const o = await f.adapter.authenticateSession({ point }); pass(o); assert.equal(o.observation_point, point);
    assert.equal(o.context_expires_at, T0 + 300000); assert.deepEqual(o.factor_types, ['EMAIL_OTP', 'TOTP']);
  }
  deny(await f.adapter.authenticateSession({ point: 'CLAIM_SIMULATION' }));
});
test('06 changed user mismatch retires', async () => { await remoteMutant(b => {
  b.user_id = 'fixture-nonowner'; b.user.user_id = b.user_id; b.session.user_id = b.user_id;
}); });
test('07 changed session mismatch retires', async () => { await remoteMutant(b => { b.session.session_id = 'fixture-other-session'; }); });
test('08 project mismatch in protected registration prevents valid proof', async () => {
  const f = fixture([], { registration: { ...reg(), project_id: 'project-test-00000000-0000-4000-8000-000000000002' } });
  deny(await f.adapter.sendEmailOtp({ email: reg().owner_email })); assert.equal(f.transport.requests().length, 0);
});
test('09 foreign signed project response denied', async () => { await remoteMutant(b => {
  b.session_jwt = jwt({ iss: 'stytch.com/foreign-project', aud: 'foreign-project' });
}); });
test('10 missing email factor denied', async () => { await remoteMutant(b => { b.session.authentication_factors.shift(); }); });
test('11 missing TOTP factor denied', async () => { await remoteMutant(b => { b.session.authentication_factors.pop(); }); });
test('12 stale email factor denied', async () => { await remoteMutant(b => { b.session.authentication_factors[0].last_authenticated_at = iso(T0 - 300000); }); });
test('13 stale TOTP factor denied', async () => { await remoteMutant(b => { b.session.authentication_factors[1].last_authenticated_at = iso(T0 - 300000); }); });
test('14 changed factor timestamp is not fresh authentication/refresh', async () => { await remoteMutant(b => {
  b.session.authentication_factors[1].last_authenticated_at = iso(T0 - 1);
}); });
test('15 invalid signed issuer denied, including SDK alternative base URL', async () => {
  for (const iss of ['https://test.stytch.com', 'stytch.com/other']) await remoteMutant(b => { b.session_jwt = jwt({ iss }); });
});
test('16 invalid/multiple audience denied', async () => {
  for (const aud of ['other', [reg().project_id, 'other']]) await remoteMutant(b => { b.session_jwt = jwt({ aud }); });
});
test('17 invalid signed subject denied; session ID cannot become subject', async () => {
  await remoteMutant(b => { b.session_jwt = jwt({ sub: b.session.session_id }); });
});
test('18 signed identity never overrides remote negative session result', async () => {
  const b = raw(true); const f = await ready(fixture([{ kind: 'RESPONSE', status: 401, body: b }]));
  deny(await f.adapter.authenticateSession({ point: 'PAGE' }));
});
test('19 expired provider session denied', async () => { await remoteMutant(b => { b.session.expires_at = iso(T0); }); });
test('20 malformed remote response denied', async () => { await remoteMutant(b => { delete b.session; }); });
test('21 timeout denies and retires without retry', async () => {
  const f = await ready(fixture([{ kind: 'TIMEOUT' }])); const o = await f.adapter.authenticateSession({ point: 'PAGE' });
  deny(o); assert.equal(o.error_class, 'TIMEOUT'); assert.equal(f.transport.requests().length, 5);
});
test('22 rate limit denies without positive cached fallback', async () => {
  const f = await ready(fixture([{ kind: 'RESPONSE', status: 429, body: raw(true) }]));
  const o = await f.adapter.authenticateSession({ point: 'PAGE' }); deny(o); assert.equal(o.error_class, 'RATE_LIMIT');
});
test('23 provider 5xx denies', async () => {
  const f = await ready(fixture([{ kind: 'RESPONSE', status: 503, body: raw(true) }]));
  const o = await f.adapter.authenticateSession({ point: 'PAGE' }); deny(o); assert.equal(o.error_class, 'PROVIDER_ERROR');
});
test('24 UNKNOWN response denies', async () => {
  const f = await ready(fixture([{ kind: 'UNKNOWN' }])); deny(await f.adapter.authenticateSession({ point: 'PAGE' }));
});
test('25 exact single retained session revoke request, no auth bearer output', async () => {
  const f = await ready(fixture([response({ status_code: 200, request_id: '00000000-0000-4000-8000-000000000019' })]));
  pass(await f.adapter.revokeSession()); const r = f.transport.requests().at(-1);
  assert.equal(r.url, 'https://test.stytch.com/v1/sessions/revoke');
  assert.deepEqual(r.body, { session_id: 'fixture-session' });
  deny(await f.adapter.revokeSession()); assert.equal(f.transport.requests().length, 5);
});
test('26 broad-user revoke and caller-specified session prohibited', async () => {
  for (const input of [{ user_id: reg().owner_user_id }, { session_id: 'other' }, { all: true }]) {
    const f = await ready(fixture()); deny(await f.adapter.revokeSession(input));
    assert.equal(f.transport.requests().length, 4);
  }
});
test('27 strict output drops all secret/raw fields and untrusted provider metadata', async () => {
  const f = await ready(fixture([response(raw(true))])); const o = await f.adapter.authenticateSession({ point: 'PAGE' });
  const encoded = JSON.stringify(o);
  assert.equal(/OFFLINE_(?:SESSION|SECRET)|session_token|session_jwt|untrusted_metadata|Authorization/.test(encoded), false);
  const direct = evidence({ session_token: 'OFFLINE_SESSION', secret: 'OFFLINE_SECRET',
    qr_code: 'OFFLINE_QR', error_class: 'OFFLINE_ERROR', factor_times: [{ type: 'OFFLINE_SECRET', at: 'OFFLINE_SECRET' }] });
  deny(direct); assert.equal(JSON.stringify(direct).includes('OFFLINE_SECRET'), false);
});
test('28 raw token as input/response cannot bypass typed operation or synthetic custody', async () => {
  const f = await ready(fixture()); deny(await f.adapter.authenticateSession('OFFLINE_SESSION_PLACEHOLDER'));
  await remoteMutant(b => { b.session_token = 'raw-bearer-disallowed'; });
});
test('29 raw provider response is not accepted as trusted operation input or evidence', async () => {
  const f = await ready(fixture()); deny(await f.adapter.authenticateSession(raw(true)));
  const o = evidence(raw(true)); deny(o); assert.equal(JSON.stringify(o).includes('session_token'), false);
});
test('30 browser cannot select project/user/endpoint', async () => {
  for (const extra of [{ project_id: 'other' }, { user_id: 'other' }, { url: 'https://attacker.invalid' }]) {
    const f = fixture(); deny(await f.adapter.sendEmailOtp({ email: reg().owner_email, ...extra }));
    assert.equal(f.transport.requests().length, 0);
  }
});
test('31 browser cannot select adapter mode', async () => {
  const f = fixture(); deny(await f.adapter.sendEmailOtp({ email: reg().owner_email, mode: 'LIVE' }));
  assert.equal(selectAdapter('LIVE').mode, 'FAKE_DISABLED');
});
test('32 secret presence/getters never activate or read prospective constructor', async () => {
  let reads = 0;
  const inputs = { get STYTCH_SECRET() { ++reads; throw new Error('not authorized'); } };
  const adapter = createStytchLiveAdapter({ mode: 'LIVE' }, inputs);
  for (const op of ['sendEmailOtp', 'authenticateEmailOtp', 'startTotpEnrollment', 'authenticateTotp', 'authenticateSession', 'revokeSession']) {
    deny(await adapter[op](inputs));
  }
  assert.equal(reads, 0); assert.equal(adapter.mode, 'FAKE_DISABLED');
});
test('33 injected fake/network client cannot be promoted into fixture or live adapter', async () => {
  let calls = 0;
  const forged = { mode: 'OFFLINE_CONTRACT_ONLY', async exchange() { calls++; return response(raw(true)); } };
  const adapter = createOfflineStytchHarness({ registration: reg(), transport: forged, publicKeys: [jwk], clock: () => T0 });
  deny(await adapter.sendEmailOtp({ email: reg().owner_email })); assert.equal(calls, 0);
  assert.equal(selectAdapter(true, adapter).mode, 'FAKE_DISABLED');
});
test('34 current default route selection stays FAKE_DISABLED with every flag', async () => {
  for (const flag of [undefined, null, 'malformed', true, 'LIVE', 'true']) {
    const adapter = selectAdapter(flag, createStytchLiveAdapter());
    assert.equal(adapter.mode, 'FAKE_DISABLED'); assert.equal((await adapter.observe('PAGE')).kind, 'FAKE_DISABLED');
  }
});

test('TOTP create uses native-user request only, pre/post direct session checks; transient wiped', async () => {
  let held;
  const enrol = response({ status_code: 200, user_id: reg().owner_user_id,
    user: { user_id: reg().owner_user_id }, totp_id: 'fixture-totp',
    secret: 'OFFLINE_TOTP_SEED', qr_code: 'OFFLINE_QR_PAYLOAD', recovery_codes: ['OFFLINE_RECOVERY'] });
  const transport = createFixtureTransport([send(), response(raw()), response(raw()), enrol,
    response(raw()), response(raw()), response(raw(true))]);
  const adapter = createOfflineStytchHarness({ registration: reg(), transport, publicKeys: [jwk], clock: () => T0,
    enrollmentConsumer(material) { held = material; assert.equal(material.secret === 'OFFLINE_TOTP_SEED', true); } });
  pass(await adapter.sendEmailOtp({ email: reg().owner_email })); pass(await adapter.authenticateEmailOtp({ code: '000000' }));
  const out = await adapter.startTotpEnrollment(); pass(out);
  assert.deepEqual(transport.requests()[3].body, { user_id: reg().owner_user_id, expiration_minutes: 5 });
  assert.equal(held.secret, null); assert.equal(held.qr_code, null); assert.deepEqual(held.recovery_codes, [null]);
  assert.equal(JSON.stringify(out).includes('OFFLINE_TOTP_SEED'), false);
  pass(await adapter.authenticateTotp({ code: '000000' }));
});
test('TOTP request carries same retained session and exact 15-minute ceremony request', async () => {
  const f = await ready(fixture()); const r = f.transport.requests().at(-1);
  assert.deepEqual(Object.keys(r.body).sort(), ['session_duration_minutes', 'session_token', 'totp_code', 'user_id']);
  assert.equal(r.body.user_id, reg().owner_user_id); assert.equal(r.body.session_duration_minutes, 15);
});
test('duplicate/out-of-order OTP, TOTP and recheck points retire', async () => {
  const f = await ready(fixture()); deny(await f.adapter.authenticateEmailOtp({ code: '000000' }));
  const g = await ready(fixture()); deny(await g.adapter.authenticateSession({ point: 'CLAIM_SIMULATION' }));
});
test('session authenticate without top-level user_id still joins Session/User/signed subject', async () => {
  const b = raw(true); delete b.user_id;
  const f = await ready(fixture([response(b)])); pass(await f.adapter.authenticateSession({ point: 'PAGE' }));
});
test('unknown factor product, duplicate factors and delivery mismatch reject', async () => {
  for (const mutate of [b => { b.session.authentication_factors[1].type = 'recovery_codes'; },
    b => { b.session.authentication_factors[1] = b.session.authentication_factors[0]; },
    b => { b.session.authentication_factors[1].delivery_method = 'email'; }]) await remoteMutant(mutate);
});
test('RSA signature, missing/duplicate kid, key URL injection and JWT time failures reject', () => {
  assert.equal(verifyStytchIdentity(jwt(), reg(), reg().owner_user_id, [jwk], T0), true);
  for (const value of [jwt().slice(0, -3) + 'abc', jwt({}, { kid: 'missing' }), jwt({}, { jku: 'https://attacker.invalid' }),
    jwt({}, { alg: 'none' }), jwt({ exp: T0 / 1000 }), jwt({ iat: T0 / 1000 + 1 }), jwt({ nbf: T0 / 1000 + 1 })]) {
    assert.equal(verifyStytchIdentity(value, reg(), reg().owner_user_id, [jwk], T0), false);
  }
  assert.equal(verifyStytchIdentity(jwt(), reg(), reg().owner_user_id, [jwk, jwk], T0), false);
});

test('standalone verifier rejects misregistered issuer/client/Owner despite matching signed claims', () => {
  const r = reg();
  assert.equal(verifyStytchIdentity(jwt(), { ...r, client_id: 'arbitrary-project-label' }, r.owner_user_id, [jwk], T0), false);
  const issuer = 'https://alternative.invalid';
  assert.equal(verifyStytchIdentity(jwt({ iss: issuer }), { ...r, issuer }, r.owner_user_id, [jwk], T0), false);
  const user = 'fixture-nonowner';
  assert.equal(verifyStytchIdentity(jwt({ sub: user }), r, user, [jwk], T0), false);
});
test('request metadata malformed or secret-shaped request_id cannot pass evidence', async () => {
  const b = raw(true); b.request_id = 'OFFLINE_SECRET_REQUEST_ID';
  const f = await ready(fixture([response(b)])); const o = await f.adapter.authenticateSession({ point: 'PAGE' });
  pass(o); assert.equal(o.request_id, null);
});
test('adapter objects JSON serialization never reveals custody; no generic operation', async () => {
  const f = await ready(fixture());
  assert.equal(/OFFLINE_SESSION|OFFLINE_SECRET|session_jwt/.test(JSON.stringify(f.adapter)), false);
  assert.equal(f.adapter.request, undefined); assert.equal(f.adapter.exchange, undefined);
});
test('changed opaque token, locked/missing account status and contradictory raw project deny', async () => {
  for (const mutate of [b => { b.session_token = 'OFFLINE_CHANGED_TOKEN'; },
    b => { b.user.is_locked = true; }, b => { delete b.user.is_locked; },
    b => { b.user.status = 'deleted'; }, b => { b.project_id = 'foreign-project'; }]) await remoteMutant(mutate);
});
test('same-session TOTP mismatch is checked before any fixture context can pass', async () => {
  for (const field of ['user_id', 'session_id']) {
    const b = raw(true);
    if (field === 'user_id') { b.user_id = 'fixture-nonowner'; b.user.user_id = b.user_id; b.session.user_id = b.user_id; }
    else b.session.session_id = 'fixture-other-session';
    const f = fixture([], { two: b }); pass(await primary(f)); deny(await f.adapter.authenticateTotp({ code: '000000' }));
  }
});
test('five-minute deadline and clock regression retire without provider call or refresh', async () => {
  for (const time of [T0 + 300000, T0 + 300001, T0 - 1]) {
    const f = await ready(fixture([response(raw(true))])); f.time(time);
    deny(await f.adapter.authenticateSession({ point: 'PAGE' }));
    assert.equal(f.transport.requests().length, 4);
  }
});
test('elapsed request timeout cannot become positive proof despite a valid response', async () => {
  let ticks = 0;
  const transport = createFixtureTransport([send()]);
  const adapter = createOfflineStytchHarness({ registration: reg(), transport, publicKeys: [jwk],
    clock() { return T0 + (++ticks >= 2 ? 5000 : 0); } });
  const o = await adapter.sendEmailOtp({ email: reg().owner_email }); deny(o); assert.equal(o.error_class, 'TIMEOUT');
});
test('bad enrollment return or failed post-check never exposes transient seed', async () => {
  for (const mismatch of [true, false]) {
    let exposed = false;
    const body = { status_code: 200, user_id: mismatch ? 'other' : reg().owner_user_id,
      user: { user_id: reg().owner_user_id }, totp_id: 'fixture-totp',
      secret: 'OFFLINE_TOTP_SEED', qr_code: 'OFFLINE_QR', recovery_codes: ['OFFLINE_RECOVERY'] };
    const transport = createFixtureTransport([send(), response(raw()), response(raw()), response(body), { kind: 'TIMEOUT' }]);
    const adapter = createOfflineStytchHarness({ registration: reg(), transport, publicKeys: [jwk], clock: () => T0,
      enrollmentConsumer() { exposed = true; } });
    pass(await adapter.sendEmailOtp({ email: reg().owner_email })); pass(await adapter.authenticateEmailOtp({ code: '000000' }));
    deny(await adapter.startTotpEnrollment()); assert.equal(exposed, false);
  }
});
test('earlier signed expiry, future factor, provider duration overflow and malformed dates deny', async () => {
  for (const mutate of [b => { b.session.expires_at = iso(T0 + 900001); },
    b => { b.session.authentication_factors[1].last_authenticated_at = iso(T0 + 1); },
    b => { b.session.expires_at = '2026-02-30T00:00:00.000Z'; },
    b => { b.session_jwt = jwt({ exp: T0 / 1000 - 1 }); }]) await remoteMutant(mutate);
});
test('UTC fractional timestamps floor precision and reject rollover/offset/oversize forms', () => {
  assert.equal(timestamp('2026-10-08T00:00:00.123456Z'), T0 + 123);
  assert.equal(timestamp('2026-10-08T00:00:00.1Z'), T0 + 100);
  for (const value of ['2026-02-30T00:00:00Z', '2026-10-08T00:00:00+00:00', '2026-10-08T00:00:00.1234567890Z']) {
    assert.equal(timestamp(value), null);
  }
});

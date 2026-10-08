import test from 'node:test';
import assert from 'node:assert/strict';
import { OfflineDiagnosticModel } from '../lib/model.js';
import { selectAdapter, FUTURE_SERVER_INPUT_NAMES } from '../lib/adapter.js';
import { sanitized, POINTS } from '../lib/policy.js';

const T0 = 1000000;
const registration = () => ({ project_id: 'fixture-project', environment: 'TEST',
  issuer: 'stytch.com/fixture-project', client_id: 'fixture-project',
  owner_user_id: 'fixture-owner', owner_generation: 1, binding_generation: 1 });
function fixture() {
  let now = T0;
  const reg = registration();
  const model = new OfflineDiagnosticModel(reg, () => now);
  const primary = { source: 'OFFLINE_FAKE_FIXTURE', project_id: reg.project_id,
    environment: 'TEST', issuer: reg.issuer, client_id: reg.client_id, subject: reg.owner_user_id,
    user_id: reg.owner_user_id, session_id: 'fixture-session',
    factors: [{ type: 'EMAIL_OTP', last_authenticated_at: T0 }],
    expires_at: T0 + 900000, start: T0, end: T0 };
  const two = structuredClone(primary);
  two.factors.push({ type: 'TOTP', last_authenticated_at: T0 });
  return { model, reg, primary, two, time(n) { now = n; },
    envelope() { const o = structuredClone(two); o.start = now; o.end = now;
      return { kind: 'OFFLINE_FAKE_FIXTURE', observation: o }; } };
}
function factors(f, enrollment = false) {
  assert.equal(f.model.step('EMAIL_START').result, 'PASS');
  assert.equal(f.model.step('PRIMARY_OBSERVATION', f.primary).result, 'PASS');
  if (enrollment) assert.equal(f.model.step('TOTP_ENROLLMENT_START').state, 'TOTP_ENROLLMENT_REQUIRED');
  assert.equal(f.model.step('TOTP_START').result, 'PASS');
  return f.model.step('TOTP_OBSERVATION', f.two);
}
function ready(f = fixture()) {
  assert.equal(factors(f).result, 'PASS');
  assert.equal(f.model.step('OWNER_EQUALITY').result, 'PASS'); return f;
}
function deny(result) {
  assert.equal(result.result, 'DENY'); assert.equal(result.authority, 'NONE');
  assert.equal(result.real_admission, 'DISABLED'); assert.equal(result.qualified_live, false);
}

test('01 U_OWNER exact simulated equality remains fake, not qualified live', () => {
  const f = fixture(); assert.equal(factors(f, true).result, 'PASS');
  const o = f.model.step('OWNER_EQUALITY');
  assert.equal(o.case_id, 'U_OWNER'); assert.equal(o.result, 'PASS');
  assert.equal(o.evidence_source, 'OFFLINE_FAKE_FIXTURE'); assert.equal(o.qualified_live, false);
  assert.equal(o.authority, 'NONE'); assert.equal(o.real_admission, 'DISABLED');
});
test('02 U_NONOWNER authenticates but Owner equality denies', () => {
  const f = fixture();
  for (const o of [f.primary, f.two]) { o.user_id = 'fixture-nonowner'; o.subject = o.user_id; }
  assert.equal(factors(f).result, 'PASS'); deny(f.model.step('OWNER_EQUALITY'));
});
test('03 U_FOREIGN wrong project denies', () => {
  const f = fixture(); f.primary.project_id = 'fixture-other';
  f.model.step('EMAIL_START'); deny(f.model.step('PRIMARY_OBSERVATION', f.primary));
});
test('04 one context cannot create another challenge', () => {
  const f = ready(); deny(f.model.step('OWNER_EQUALITY'));
});
test('05 context exactly at 300000 ms denies', () => {
  const f = ready(); f.time(T0 + 300000); deny(f.model.reload());
});
test('06 context over 300000 ms denies', () => {
  const f = ready(); f.time(T0 + 300001); deny(f.model.reload());
});
test('07 reload and recheck never extend absolute context deadline', () => {
  const f = ready(); const expiry = f.model.output().context_expires_at;
  f.time(T0 + 200000);
  assert.equal(f.model.reload().context_expires_at, expiry);
  const rechecked = f.model.recheck('PAGE', f.envelope());
  assert.equal(rechecked.context_expires_at, expiry);
  assert.equal(rechecked.observation_start, T0 + 200000);
  assert.equal(rechecked.observation_end, T0 + 200000);
  f.time(expiry); deny(f.model.reload());
});
test('08 process restart invalidates previous context', () => { deny(ready().model.restart()); });
test('09 changed remote session_id denies', () => {
  const f = ready(); const e = f.envelope(); e.observation.session_id = 'fixture-other-session';
  deny(f.model.recheck('PAGE', e));
});
test('10 changed remote user_id/sub denies', () => {
  const f = ready(); const e = f.envelope();
  e.observation.user_id = 'fixture-nonowner'; e.observation.subject = e.observation.user_id;
  deny(f.model.recheck('PAGE', e));
});
test('11 changed remote project denies', () => {
  const f = ready(); const e = f.envelope(); e.observation.project_id = 'fixture-other';
  deny(f.model.recheck('PAGE', e));
});
test('12 stale owner_generation denies', () => {
  const f = ready(); deny(f.model.replaceRegistration({ ...f.reg, owner_generation: 2 }));
});
test('13 stale binding_generation denies', () => {
  const f = ready(); deny(f.model.replaceRegistration({ ...f.reg, binding_generation: 2 }));
});
test('14 missing second factor denies', () => {
  const f = fixture(); f.two.factors.pop(); deny(factors(f));
});
test('15 stale TOTP factor denies', () => {
  const f = fixture(); f.two.factors[1].last_authenticated_at = T0 - 300000; deny(factors(f));
});
test('16 primary/TOTP user mismatch denies', () => {
  const f = fixture(); f.two.user_id = 'fixture-nonowner'; f.two.subject = f.two.user_id; deny(factors(f));
});
test('17 primary/TOTP session mismatch denies', () => {
  const f = fixture(); f.two.session_id = 'fixture-other-session'; deny(factors(f));
});
test('18 fake adapter cannot be selected/promoted to live', async () => {
  let calls = 0;
  const malicious = { mode: 'LIVE', observe() { ++calls; throw new Error('secret sentinel'); } };
  const adapter = selectAdapter(true, malicious);
  assert.equal(adapter.mode, 'FAKE_DISABLED');
  assert.deepEqual(await adapter.observe('PAGE'), { kind: 'FAKE_DISABLED' }); assert.equal(calls, 0);
});
test('19 absent/malformed/true live flags never call injected provider', async () => {
  let calls = 0;
  for (const flag of [undefined, null, '', 'true', true, false, 'malformed', 1]) {
    assert.equal((await selectAdapter(flag, { observe() { calls++; } }).observe('PAGE')).kind, 'FAKE_DISABLED');
  }
  assert.equal(calls, 0); assert.deepEqual(FUTURE_SERVER_INPUT_NAMES, ['STYTCH_PROJECT_ID', 'STYTCH_SECRET']);
});
test('20 secret-like fields and raw error strings never enter sanitized output', () => {
  const sentinel = 'SECRET_SENTINEL_DO_NOT_EXPORT';
  const o = sanitized({ session_token: sentinel, session_jwt: sentinel, STYTCH_SECRET: sentinel,
    authorization: sentinel, cookie: sentinel, OTP: sentinel, seed: sentinel, env: sentinel,
    error_class: sentinel, raw: sentinel, request_id: sentinel, case_id: sentinel, factors: sentinel });
  assert.equal(JSON.stringify(o).includes(sentinel), false);
  assert.equal(o.error_class, 'UNKNOWN'); deny(o);
});
test('21 raw provider response/extra fields rejected, not projected as success', () => {
  const f = fixture(); f.primary.session_token = 'SYNTHETIC_SENTINEL';
  f.model.step('EMAIL_START'); deny(f.model.step('PRIMARY_OBSERVATION', f.primary));
});
test('24 unexpected provider error fails closed without raw serialization', () => {
  const f = ready(); const o = f.model.recheck('PAGE', { kind: 'ERROR', message: 'SYNTHETIC_SECRET' });
  deny(o); assert.equal(JSON.stringify(o).includes('SYNTHETIC_SECRET'), false);
});
test('25 timeout/UNKNOWN fail closed, never fallback to cached JWT', () => {
  for (const kind of ['TIMEOUT', 'UNKNOWN', 'LIVE', 'JWT_ONLY', 'FAKE_DISABLED']) {
    const f = ready(); deny(f.model.recheck('PAGE', { kind }));
  }
});
test('26 duplicate/conflicting terminal action denies', () => {
  const f = ready(); f.model.recheck('PAGE', f.envelope());
  assert.equal(f.model.terminal('CONFIRM_SIMULATION', f.envelope()).result, 'PASS');
  deny(f.model.terminal('CONFIRM_SIMULATION', f.envelope()));
  deny(f.model.terminal('DENY_SIMULATION'));
});
test('all five ordered observation labels simulate only one terminal lineage', () => {
  const f = ready(); f.model.recheck(POINTS[0], f.envelope());
  f.model.terminal('CONFIRM_SIMULATION', f.envelope());
  for (const point of POINTS.slice(2)) assert.equal(f.model.recheck(point, f.envelope()).result, 'PASS');
  assert.equal(f.model.output().state, 'DIAGNOSTIC_COMPLETE');
  deny(f.model.recheck('CLAIM_SIMULATION', f.envelope()));
});
test('DENY terminal retirement cannot re-enter lineage', () => {
  const f = ready(); f.model.recheck('PAGE', f.envelope());
  assert.equal(f.model.terminal('DENY_SIMULATION').state, 'LOCAL_CONTEXT_RETIRED');
  deny(f.model.terminal('CONFIRM_SIMULATION', f.envelope()));
});
test('missing/malformed registration and browser-like state jumps deny', () => {
  for (const reg of [undefined, null, {}, { ...registration(), email: 'unused' },
    { ...registration(), environment: 'LIVE' }, { ...registration(), issuer: 'https://test.stytch.com' }]) {
    const rejected = new OfflineDiagnosticModel(reg, () => T0).step('EMAIL_START');
    deny(rejected); assert.equal(rejected.case_id, 'UNREGISTERED');
  }
  deny(fixture().model.step('OWNER_EQUALITY'));
});
test('duplicate factors, future timestamp, expired provider session and sub mismatch deny', () => {
  for (const mutate of [o => { o.factors[1].type = 'EMAIL_OTP'; },
    o => { o.factors[1].last_authenticated_at++; }, o => { o.expires_at = T0; },
    o => { o.subject = 'fixture-other'; }]) {
    const f = fixture(); mutate(f.two); deny(factors(f));
  }
});
test('local logout, observed revoke and switch invalidate without issuer claims', () => {
  for (const reason of ['LOCAL_LOGOUT', 'REMOTE_REVOKE_OBSERVED', 'ACCOUNT_SWITCH']) {
    const f = ready(); deny(f.model.retire(reason)); deny(f.model.reload());
  }
});
test('clock rollback retires; replacement IDs without generation bump also deny', () => {
  const f = ready(); f.time(T0 - 1); deny(f.model.reload());
  const g = ready(); deny(g.model.replaceRegistration({ ...g.reg, owner_user_id: 'fixture-nonowner' }));
});
test('snapshot input mutation cannot change retained identity', () => {
  const f = ready(); f.two.session_id = 'fixture-mutated';
  assert.equal(f.model.output().session_id_hash_or_registered_alias, 'SAME_DIAGNOSTIC_LINEAGE');
});
test('stale cached observation cannot stand in for new direct remote recheck', () => {
  const f = ready(); const old = f.envelope(); f.time(T0 + 1);
  deny(f.model.recheck('PAGE', old));
});
test('status read at deadline retires model rather than exporting stale PASS', () => {
  const f = ready(); f.time(T0 + 300000);
  deny(f.model.output('PASS')); f.time(T0 + 300001); deny(f.model.reload());
});

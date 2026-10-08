// NEXUS_G3_D01_DIAGNOSTIC_ONLY: protocol implementation, never runtime selection.
// No network implementation, environment read, dynamic import or SDK fallback.
import { closed, identifier, positive, stamp, POINTS, LABELS } from './policy.js';
import { evidence, projectSession } from './stytch-projection.js';
import { verifyStytchIdentity } from './stytch-identity.js';

export const STYTCH_TEST_ORIGIN = 'https://test.stytch.com';
export const LIVE_ADAPTER_BUILD_ENABLED = false;
const OPS = ['sendEmailOtp', 'authenticateEmailOtp', 'startTotpEnrollment',
  'authenticateTotp', 'authenticateSession', 'revokeSession'];
const REG_KEYS = ['project_id', 'environment', 'issuer', 'client_id', 'owner_user_id',
  'owner_generation', 'binding_generation', 'owner_email'];
const EXPECTED_ENDPOINTS = Object.freeze({
  sendEmailOtp: '/v1/otps/email/send', authenticateEmailOtp: '/v1/otps/authenticate',
  startTotpEnrollment: '/v1/totps', authenticateTotp: '/v1/totps/authenticate',
  authenticateSession: '/v1/sessions/authenticate', revokeSession: '/v1/sessions/revoke',
});
const fixtureTransports = new WeakSet();

// This prospective live constructor is intentionally unconditionally disabled.
// Credentials/config objects are not inspected, including getters or env inputs.
export function createStytchLiveAdapter(_protectedConfig, _secretInterface) {
  return Object.freeze({ mode: 'FAKE_DISABLED', ...LABELS,
    ...Object.fromEntries(OPS.map(op => [op, async () => Object.freeze({
      ...evidence({ error_class: 'LIVE_DISABLED' }), evidence_source: 'FAKE_DISABLED',
    })])),
  });
}

// Closed in-memory test transport, not an injectable network client. Responses
// must be literal data; functions/promises/real SDK clients cannot be promoted.
export function createFixtureTransport(responses) {
  if (!Array.isArray(responses) || responses.length > 64) throw new Error('REQUEST');
  const queue = structuredClone(responses);
  const requests = [];
  const transport = Object.freeze({
    mode: 'OFFLINE_CONTRACT_ONLY',
    async exchange(request) {
      requests.push(structuredClone(request));
      return queue.length ? queue.shift() : { kind: 'UNKNOWN' };
    },
    // Only test fixtures can obtain request shapes; never a deployed route/API.
    requests() { return structuredClone(requests); },
  });
  fixtureTransports.add(transport); return transport;
}

// No real credential/token is accepted by this test-only construction seam.
export function createOfflineStytchHarness({ registration, transport, publicKeys, clock,
  enrollmentConsumer = () => {} } = {}) {
  const valid = closed(registration, REG_KEYS) && registration.environment === 'TEST'
    && /^project-test-[a-f0-9-]{36}$/.test(registration.project_id)
    && registration.issuer === `stytch.com/${registration.project_id}`
    && registration.client_id === registration.project_id && identifier(registration.owner_user_id)
    && positive(registration.owner_generation) && positive(registration.binding_generation)
    && typeof registration.owner_email === 'string' && registration.owner_email.endsWith('@example.invalid')
    && fixtureTransports.has(transport) && typeof clock === 'function' && typeof enrollmentConsumer === 'function';
  if (!valid) return createStytchLiveAdapter();
  return new ProtocolHarness(structuredClone(registration), transport, structuredClone(publicKeys), clock, enrollmentConsumer);
}

class ProtocolHarness {
  #r; #transport; #keys; #clock; #consumer; #highWater = null;
  #state = 'SIGNED_OUT'; #method = null; #token = null; #session = null;
  #deadline = null; #point = 0; #busy = false; #totpId = null;
  constructor(registration, transport, keys, clock, consumer) {
    this.#r = registration; this.#transport = transport; this.#keys = keys;
    this.#clock = clock; this.#consumer = consumer;
    Object.freeze(this);
  }
  get mode() { return 'OFFLINE_CONTRACT_ONLY'; }
  toJSON() { return evidence({ error_class: 'LIVE_DISABLED' }); }
  #now() {
    const now = this.#clock();
    if (!stamp(now) || (this.#highWater !== null && now < this.#highWater)) throw new Error('CLOCK');
    this.#highWater = now; return now;
  }
  #retire(error) {
    this.#state = 'RETIRED'; this.#token = null; this.#session = null;
    this.#method = null; this.#totpId = null; this.#consumer = null;
    return evidence({ error_class: error });
  }
  #check() {
    if (['RETIRED', 'REVOKED'].includes(this.#state)) throw new Error('RETIRED');
    if (this.#deadline !== null && this.#now() >= this.#deadline) throw new Error('EXPIRED');
  }
  async #run(fn) {
    if (this.#busy) return evidence({ error_class: 'BUSY' });
    this.#busy = true;
    try {
      this.#check(); const output = await fn();
      if (this.#state !== 'REVOKED') this.#check();
      return output;
    } catch (error) {
      const known = new Set(['STATE', 'REQUEST', 'MALFORMED', 'IDENTITY', 'FACTORS', 'EXPIRED',
        'RETIRED', 'CLOCK', 'TIMEOUT', 'RATE_LIMIT', 'PROVIDER_ERROR', 'UNKNOWN', 'ENROLLMENT']);
      return this.#retire(known.has(error?.message) ? error.message : 'UNKNOWN');
    } finally { this.#busy = false; }
  }
  async #request(op, body) {
    const start = this.#now();
    const request = { url: STYTCH_TEST_ORIGIN + EXPECTED_ENDPOINTS[op], method: 'POST',
      headers: { 'Content-Type': 'application/json',
        Authorization: `Basic ${Buffer.from(`${this.#r.project_id}:OFFLINE_SECRET_PLACEHOLDER`).toString('base64')}` },
      body, timeout_ms: 5000, redirect: 'error', retry: 'NEVER',
    };
    const result = await this.#transport.exchange(request); const end = this.#now();
    if (end - start >= 5000 || result?.kind === 'TIMEOUT') throw new Error('TIMEOUT');
    if (!closed(result, ['kind', 'status', 'body']) || result.kind !== 'RESPONSE') throw new Error('UNKNOWN');
    if (result.status === 429) throw new Error('RATE_LIMIT');
    if (Number.isInteger(result.status) && result.status >= 500 && result.status <= 599) throw new Error('PROVIDER_ERROR');
    if (result.status !== 200) throw new Error('PROVIDER_ERROR');
    if (!result.body || typeof result.body !== 'object' || Array.isArray(result.body)
        || result.body.status_code !== 200) throw new Error('MALFORMED');
    return { body: result.body, start, end };
  }
  #proof(reply, factors, same = true, ceremony = false) {
    const session = projectSession(reply.body, this.#r, reply.end, factors);
    if (!verifyStytchIdentity(reply.body.session_jwt, this.#r, session.user_id, this.#keys, reply.end)) throw new Error('IDENTITY');
    if (typeof reply.body.session_token !== 'string' || !/^OFFLINE_[A-Z0-9_]{1,128}$/.test(reply.body.session_token)) throw new Error('MALFORMED');
    if (same && (session.user_id !== this.#session.user_id || session.session_id !== this.#session.session_id
        || reply.body.session_token !== this.#token)) throw new Error('IDENTITY');
    if (same && session.factors[0].at !== this.#session.factors[0].at) throw new Error('FACTORS');
    if (same && !ceremony && (session.expires_at !== this.#session.expires_at
        || session.factors.some(f => f.at !== this.#session.factors.find(old => old.type === f.type)?.at))) throw new Error('FACTORS');
    return session;
  }
  #output(reply, session, point = null) {
    return evidence({ result: 'PASS', error_class: 'NONE', request_id: reply.body.request_id,
      matched: true, factor_times: session?.factors, start: reply.start, end: reply.end,
      owner_generation: this.#r.owner_generation, binding_generation: this.#r.binding_generation,
      deadline: this.#deadline, point });
  }
  async #remote(factors) {
    const reply = await this.#request('authenticateSession', { session_token: this.#token });
    return { reply, session: this.#proof(reply, factors) };
  }
  sendEmailOtp(input) {
    return this.#run(async () => {
      if (this.#state !== 'SIGNED_OUT' || !closed(input, ['email']) || input.email !== this.#r.owner_email) throw new Error('REQUEST');
      // Send only: no login-or-create, native user merge, template/default indirection.
      const reply = await this.#request('sendEmailOtp', { email: this.#r.owner_email, expiration_minutes: 5, locale: 'en' });
      if (reply.body.user_id !== this.#r.owner_user_id || !identifier(reply.body.email_id)) throw new Error('IDENTITY');
      this.#method = reply.body.email_id; this.#state = 'EMAIL_PENDING';
      return this.#output(reply);
    });
  }
  authenticateEmailOtp(input) {
    return this.#run(async () => {
      if (this.#state !== 'EMAIL_PENDING' || !closed(input, ['code']) || !/^\d{6}$/.test(input.code)) throw new Error('REQUEST');
      const reply = await this.#request('authenticateEmailOtp', { method_id: this.#method, code: input.code, session_duration_minutes: 15 });
      if (reply.body.method_id !== this.#method || reply.body.user_id !== this.#r.owner_user_id) throw new Error('IDENTITY');
      const session = this.#proof(reply, ['EMAIL_OTP'], false);
      this.#token = reply.body.session_token; this.#session = session; this.#method = null;
      this.#deadline = Math.min(session.expires_at, session.factors[0].at + 300000);
      this.#state = 'PRIMARY_VERIFIED'; return this.#output(reply, session);
    });
  }
  startTotpEnrollment(input) {
    return this.#run(async () => {
      if (this.#state !== 'PRIMARY_VERIFIED' || input !== undefined) throw new Error('STATE');
      await this.#remote(['EMAIL_OTP']);
      // Consumer create supports user_id, NOT session_token: guard retained session
      // with direct checks before and after; do not invent a provider lease/atomic join.
      const reply = await this.#request('startTotpEnrollment', { user_id: this.#session.user_id, expiration_minutes: 5 });
      const b = reply.body;
      if (b.user_id !== this.#session.user_id || b.user?.user_id !== b.user_id || !identifier(b.totp_id)) throw new Error('IDENTITY');
      if (![b.secret, b.qr_code, ...(Array.isArray(b.recovery_codes) ? b.recovery_codes : [null])]
        .every(v => typeof v === 'string' && /^OFFLINE_[A-Z0-9_]{1,128}$/.test(v))) throw new Error('ENROLLMENT');
      await this.#remote(['EMAIL_OTP']); this.#check();
      let transient = { secret: b.secret, qr_code: b.qr_code, recovery_codes: [...b.recovery_codes] };
      try { await this.#consumer(transient); }
      finally {
        transient.secret = null; transient.qr_code = null; transient.recovery_codes.fill(null);
        transient = null;
        b.secret = null; b.qr_code = null; b.recovery_codes.fill(null);
      }
      this.#totpId = b.totp_id; this.#state = 'ENROLLMENT_PENDING';
      return this.#output(reply, this.#session);
    });
  }
  authenticateTotp(input) {
    return this.#run(async () => {
      if (!['PRIMARY_VERIFIED', 'ENROLLMENT_PENDING'].includes(this.#state)
          || !closed(input, ['code']) || !/^\d{6}$/.test(input.code)) throw new Error('REQUEST');
      await this.#remote(['EMAIL_OTP']);
      const reply = await this.#request('authenticateTotp', { user_id: this.#session.user_id,
        totp_code: input.code, session_token: this.#token, session_duration_minutes: 15 });
      if (reply.body.user_id !== this.#r.owner_user_id || !identifier(reply.body.totp_id)
          || (this.#totpId !== null && reply.body.totp_id !== this.#totpId)) throw new Error('IDENTITY');
      const session = this.#proof(reply, ['EMAIL_OTP', 'TOTP'], true, true);
      this.#session = session;
      this.#deadline = Math.min(this.#deadline, session.expires_at, session.factors[1].at + 300000);
      this.#consumer = null; this.#state = 'TWO_FACTOR_VERIFIED';
      return this.#output(reply, session);
    });
  }
  authenticateSession(input) {
    return this.#run(async () => {
      if (this.#state !== 'TWO_FACTOR_VERIFIED' || !closed(input, ['point']) || input.point !== POINTS[this.#point]) throw new Error('REQUEST');
      const { reply, session } = await this.#remote(['EMAIL_OTP', 'TOTP']);
      ++this.#point;
      if (this.#point === POINTS.length) this.#state = 'OBSERVATIONS_COMPLETE';
      return this.#output(reply, session, input.point);
    });
  }
  revokeSession(input) {
    return this.#run(async () => {
      if (!this.#session || !['PRIMARY_VERIFIED', 'ENROLLMENT_PENDING', 'TWO_FACTOR_VERIFIED', 'OBSERVATIONS_COMPLETE'].includes(this.#state)
          || input !== undefined) throw new Error('REQUEST');
      const reply = await this.#request('revokeSession', { session_id: this.#session.session_id });
      const output = evidence({ result: 'PASS', error_class: 'NONE', request_id: reply.body.request_id, start: reply.start, end: reply.end });
      this.#retire('RETIRED'); this.#state = 'REVOKED'; return output;
    });
  }
}

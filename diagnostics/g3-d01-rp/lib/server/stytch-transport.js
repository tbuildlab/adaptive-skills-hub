if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');
import { request as httpsRequest } from 'node:https';
import { closed, identifier, stamp } from '../policy.js';
import { projectSession } from '../stytch-projection.js';
import { verifyStytchIdentity } from '../stytch-identity.js';
import { PATHS, TIMEOUT_MS, RESPONSE_MAX_BYTES, REQUEST_MAX_BYTES, liveSelectionAllowed,
  ClosedFailure, safeError, safeResult, disabledOperations } from './pre-secret-policy.js';
import { registrationRecord, registrationCurrent, currentControlRecord } from './provider-registration.js';
import { loadServerCredentials, offlineCustodyMatches, authorizeFixedRequest } from './credential-custody.js';
const fixtures = new WeakMap();

// In-memory transport fixture; no caller-supplied callback, socket or SDK promotion.
export function createOfflineIo(replies) {
  if (!Array.isArray(replies) || replies.length > 64) throw new ClosedFailure('REQUEST');
  const queue = structuredClone(replies); const shapes = [];
  const handle = Object.freeze({ kind: 'OFFLINE_IO',
    requestShapes() { return structuredClone(shapes); },
    toJSON() { return { kind: 'OFFLINE_IO', authority: 'NONE' }; } });
  fixtures.set(handle, { queue, shapes }); return handle;
}
function failureForStatus(status) {
  if (status === 401 || status === 403) return 'AUTH_REJECTED';
  if (status === 404) return 'SESSION_INVALID';
  if (status === 429) return 'RATE_LIMITED';
  if (Number.isInteger(status) && status >= 500 && status <= 599) return 'PROVIDER_UNAVAILABLE';
  return 'UNKNOWN';
}
function headerCheck(status, headers) {
  if (status !== 200) throw new ClosedFailure(failureForStatus(status));
  if (!headers || !/^application\/json(?:;\s*charset=utf-8)?$/i.test(headers['content-type'] ?? '')
      || (headers['content-encoding'] !== undefined && headers['content-encoding'] !== 'identity')) throw new ClosedFailure('MALFORMED_RESPONSE');
  const length = headers['content-length'];
  if (length !== undefined && (!/^\d{1,10}$/.test(String(length)) || Number(length) > RESPONSE_MAX_BYTES)) throw new ClosedFailure('MALFORMED_RESPONSE');
}
function parseBytes(chunks, contentLength) {
  let count = 0; const retained = [];
  if (!Array.isArray(chunks)) throw new ClosedFailure('MALFORMED_RESPONSE');
  for (const chunk of chunks) {
    if (typeof chunk !== 'string' && !(chunk instanceof Uint8Array)) throw new ClosedFailure('MALFORMED_RESPONSE');
    const bytes = Buffer.from(chunk); count += bytes.length;
    if (count > RESPONSE_MAX_BYTES) throw new ClosedFailure('MALFORMED_RESPONSE');
    retained.push(bytes);
  }
  if (contentLength !== undefined && count !== Number(contentLength)) throw new ClosedFailure('MALFORMED_RESPONSE');
  try {
    const body = JSON.parse(new TextDecoder('utf-8', { fatal: true }).decode(Buffer.concat(retained)));
    if (!body || typeof body !== 'object' || Array.isArray(body) || body.status_code !== 200) throw new ClosedFailure('MALFORMED_RESPONSE');
    return body;
  } catch { throw new ClosedFailure('MALFORMED_RESPONSE'); }
}
// Prepared native HTTPS implementation. Private and unreachable from every current
// deployed entrypoint and factory. No proxies, redirects, retries or default logs.
function nativeExchange(options, bytes) {
  return new Promise((resolve, reject) => {
    let req; let settled = false; let timer;
    const finish = (error, value) => {
      if (settled) return; settled = true; clearTimeout(timer);
      if (error) { req?.destroy(); reject(error); } else resolve(value);
    };
    timer = setTimeout(() => finish(new ClosedFailure('TIMEOUT')), TIMEOUT_MS);
    try {
      req = httpsRequest(options, res => {
        try { headerCheck(res.statusCode, res.headers); }
        catch (error) { res.destroy(); finish(error); return; }
        let size = 0; const chunks = [];
        res.on('data', chunk => {
          size += chunk.length;
          if (size > RESPONSE_MAX_BYTES) { res.destroy(); finish(new ClosedFailure('MALFORMED_RESPONSE')); }
          else chunks.push(chunk);
        });
        res.on('aborted', () => finish(new ClosedFailure('UNKNOWN')));
        res.on('error', () => finish(new ClosedFailure('PROVIDER_UNAVAILABLE')));
        res.on('end', () => {
          try { finish(null, parseBytes(chunks, res.headers['content-length'])); }
          catch (error) { finish(error); }
        });
      });
      req.on('error', () => finish(new ClosedFailure('PROVIDER_UNAVAILABLE')));
      req.end(bytes);
    } catch { finish(new ClosedFailure('UNKNOWN')); }
  });
}
export function createProtectedStytchTransport(configuration, registration) {
  if (!liveSelectionAllowed(configuration, registration)) return disabledOperations();
  const credentials = loadServerCredentials(configuration, registration);
  if (!credentials) return disabledOperations();
  // Activation also needs a separately reviewed registration loader, trusted keys,
  // context lifecycle, protocol integration and Owner UI. No partial live fallback.
  credentials.dispose(); return disabledOperations();
}
export function createOfflineStytchTransport({ registration, credentials, io, current,
  publicKeys = [], clock = Date.now } = {}) {
  if (!registrationRecord(registration) || !offlineCustodyMatches(credentials, registration)
      || !fixtures.has(io) || !registrationCurrent(registration, currentControlRecord(current)) || typeof clock !== 'function') return disabledOperations();
  return new OfflineProtocol(registration, credentials, io, current, structuredClone(publicKeys), clock);
}
class OfflineProtocol {
  #registration; #credentials; #io; #current; #keys; #clock;
  #method = null; #token = null; #session = null; #deadline = null;
  #retired = false; #busy = false; #highWater = null; #two = false; #totp = null;
  constructor(r, c, io, current, keys, clock) {
    this.#registration = r; this.#credentials = c; this.#io = io;
    this.#current = current; this.#keys = keys; this.#clock = clock; Object.freeze(this);
  }
  get mode() { return 'OFFLINE_PRE_SECRET_ONLY'; }
  toJSON() { return safeResult('DISABLED'); }
  retire() {
    this.#retired = true; this.#token = null; this.#session = null; this.#method = null;
    this.#totp = null; this.#credentials.dispose(); return safeResult('RETIRED', false, true);
  }
  #now() {
    const now = this.#clock();
    if (!stamp(now) || (this.#highWater !== null && now < this.#highWater)) throw new ClosedFailure('EXPIRED');
    this.#highWater = now; return now;
  }
  #check() {
    if (this.#retired || !offlineCustodyMatches(this.#credentials, this.#registration)) throw new ClosedFailure('RETIRED');
    if (!registrationCurrent(this.#registration, currentControlRecord(this.#current))) throw new ClosedFailure('REGISTRATION');
    const now = this.#now();
    if (this.#deadline !== null && now >= this.#deadline) throw new ClosedFailure('EXPIRED');
  }
  async #run(work) {
    if (this.#busy) return safeResult('REQUEST', false, true);
    this.#busy = true;
    try { this.#check(); await work(); if (!this.#retired) this.#check(); return safeResult('NONE', true, true); }
    catch (error) { const reason = safeError(error); this.retire(); return safeResult(reason, false, true); }
    finally { this.#busy = false; }
  }
  async #exchange(op, body) {
    const bytes = Buffer.from(JSON.stringify(body));
    if (bytes.length > REQUEST_MAX_BYTES) throw new ClosedFailure('REQUEST');
    const options = { protocol: 'https:', hostname: 'test.stytch.com', port: 443,
      servername: 'test.stytch.com', rejectUnauthorized: true, method: 'POST', path: PATHS[op],
      headers: { 'Content-Type': 'application/json', 'Content-Length': bytes.length, Accept: 'application/json' }, agent: false };
    authorizeFixedRequest(this.#credentials, options);
    const fixture = fixtures.get(this.#io);
    // Only authentic fixture custody/IO can enter this class. nativeExchange is
    // retained as future private IO, never selected by text flags or injected clients.
    if (!fixture) throw new ClosedFailure('DISABLED');
    fixture.shapes.push({ op, protocol: options.protocol, host: options.hostname, path: options.path,
      method: options.method, keys: Object.keys(body).sort(), duration: body.session_duration_minutes ?? null,
      exact_session_id: body.session_id ?? null, credential_header_present: true, retries: 0 });
    const reply = fixture.queue.shift();
    if (!reply || reply.failure) throw new ClosedFailure(reply?.failure === 'TIMEOUT' ? 'TIMEOUT' : 'PROVIDER_UNAVAILABLE');
    if (!stamp(reply.delay_ms ?? 0) || (reply.delay_ms ?? 0) >= TIMEOUT_MS) throw new ClosedFailure('TIMEOUT');
    headerCheck(reply.status, reply.headers);
    return parseBytes(reply.chunks, reply.headers['content-length']);
  }
  #proof(body, factors, same = true, ceremony = false) {
    const r = registrationRecord(this.#registration); const now = this.#now();
    const p = { ...r, client_id: r.audience };
    let session;
    try { session = projectSession(body, p, now, factors); }
    catch { throw new ClosedFailure('FACTORS'); }
    if (!verifyStytchIdentity(body.session_jwt, p, session.user_id, this.#keys, now)
        || typeof body.session_token !== 'string' || !/^OFFLINE_[A-Z0-9_]{1,128}$/.test(body.session_token)) throw new ClosedFailure('IDENTITY');
    if (same && (session.session_id !== this.#session.session_id || session.user_id !== this.#session.user_id
        || body.session_token !== this.#token || session.factors[0].at !== this.#session.factors[0].at)) throw new ClosedFailure('IDENTITY');
    if (same && !ceremony && (session.expires_at !== this.#session.expires_at
        || session.factors.some(f => f.at !== this.#session.factors.find(old => old.type === f.type)?.at))) throw new ClosedFailure('FACTORS');
    return session;
  }
  async #recheck() {
    const body = await this.#exchange('SESSION_AUTHENTICATE', { session_token: this.#token });
    this.#proof(body, this.#two ? ['EMAIL_OTP', 'TOTP'] : ['EMAIL_OTP']);
  }
  EMAIL_OTP_SEND(input) { return this.#run(async () => {
    if (input !== undefined || this.#method || this.#session) throw new ClosedFailure('REQUEST');
    const r = registrationRecord(this.#registration);
    const b = await this.#exchange('EMAIL_OTP_SEND', { email: r.delivery_email, expiration_minutes: 5, locale: 'en' });
    if (b.user_id !== r.owner_user_id || !identifier(b.email_id)) throw new ClosedFailure('IDENTITY');
    this.#method = b.email_id;
  }); }
  EMAIL_OTP_AUTHENTICATE(input) { return this.#run(async () => {
    if (!this.#method || this.#session || !closed(input, ['code']) || typeof input.code !== 'string' || !/^\d{6}$/.test(input.code)) throw new ClosedFailure('REQUEST');
    const b = await this.#exchange('EMAIL_OTP_AUTHENTICATE', { method_id: this.#method, code: input.code, session_duration_minutes: 15 });
    if (b.method_id !== this.#method || b.user_id !== registrationRecord(this.#registration).owner_user_id) throw new ClosedFailure('IDENTITY');
    const s = this.#proof(b, ['EMAIL_OTP'], false);
    this.#session = s; this.#token = b.session_token; this.#method = null;
    this.#deadline = Math.min(s.expires_at, s.factors[0].at + 300000);
  }); }
  TOTP_CREATE(input) { return this.#run(async () => {
    if (!this.#session || this.#two || this.#totp || input !== undefined) throw new ClosedFailure('REQUEST');
    await this.#recheck();
    const b = await this.#exchange('TOTP_CREATE', { user_id: this.#session.user_id, expiration_minutes: 5 });
    try {
      if (b.user_id !== this.#session.user_id || b.user?.user_id !== b.user_id || !identifier(b.totp_id)
          || !Array.isArray(b.recovery_codes) || ![b.secret, b.qr_code, ...b.recovery_codes].every(v => typeof v === 'string' && /^OFFLINE_[A-Z0-9_]{1,128}$/.test(v))) throw new ClosedFailure('IDENTITY');
      await this.#recheck(); this.#totp = { totp_id: b.totp_id };
    } finally {
      // No server/browser handoff. Clear even malformed or failed post-check returns.
      b.secret = null; b.qr_code = null;
      if (Array.isArray(b.recovery_codes)) b.recovery_codes.fill(null);
    }
  }); }
  TOTP_AUTHENTICATE(input) { return this.#run(async () => {
    if (!this.#session || this.#two || !closed(input, ['code']) || typeof input.code !== 'string' || !/^\d{6}$/.test(input.code)) throw new ClosedFailure('REQUEST');
    await this.#recheck();
    const b = await this.#exchange('TOTP_AUTHENTICATE', { user_id: this.#session.user_id, totp_code: input.code,
      session_token: this.#token, session_duration_minutes: 15 });
    if (b.user_id !== this.#session.user_id || !identifier(b.totp_id)
        || (this.#totp && this.#totp.totp_id !== b.totp_id)) throw new ClosedFailure('IDENTITY');
    const s = this.#proof(b, ['EMAIL_OTP', 'TOTP'], true, true);
    this.#session = s; this.#two = true;
    this.#deadline = Math.min(this.#deadline, s.expires_at, s.factors[1].at + 300000); this.#totp = null;
    await this.#recheck();
  }); }
  SESSION_AUTHENTICATE(input) { return this.#run(async () => {
    if (!this.#session || !this.#two || input !== undefined) throw new ClosedFailure('REQUEST'); await this.#recheck();
  }); }
  SESSION_REVOKE_EXACT(input) { return this.#run(async () => {
    if (!this.#session || input !== undefined) throw new ClosedFailure('REQUEST');
    await this.#exchange('SESSION_REVOKE_EXACT', { session_id: this.#session.session_id }); this.retire();
  }); }
}

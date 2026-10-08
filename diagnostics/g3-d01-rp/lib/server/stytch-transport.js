if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');
import { request as httpsRequest } from 'node:https';
import { EventEmitter } from 'node:events';
import { closed, identifier, stamp } from '../policy.js';
import { projectSession } from '../stytch-projection.js';
import { verifyStytchIdentity } from '../stytch-identity.js';
import { PATHS, TIMEOUT_MS, RESPONSE_MAX_BYTES, REQUEST_MAX_BYTES, liveSelectionAllowed,
  ClosedFailure, safeError, safeResult, disabledOperations } from './pre-secret-policy.js';
import { registrationRecord, registrationCurrent, currentControlRecord, registerReviewedDeployment,
  createReviewedCurrentControl } from './provider-registration.js';
import { loadServerCredentials, offlineCustodyMatches, protectedCustodyMatches, authorizeFixedRequest } from './credential-custody.js';
import { pinnedKeys } from './pinned-identity.js';
import { createOwnerEnvelope, retireOwnerEnvelope, renderOwnerEnvelope } from './owner-channel.js';
const fixtures = new WeakMap();

// In-memory transport fixture; no caller-supplied callback, socket or SDK promotion.
export function createOfflineIo(replies, nativeParser = false) {
  if (!Array.isArray(replies) || replies.length > 64) throw new ClosedFailure('REQUEST');
  const queue = structuredClone(replies); const shapes = [];
  const handle = Object.freeze({ kind: 'OFFLINE_IO',
    requestShapes() { return structuredClone(shapes); },
    toJSON() { return { kind: 'OFFLINE_IO', authority: 'NONE' }; } });
  fixtures.set(handle, { queue, shapes, nativeParser: nativeParser === true }); return handle;
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
// Bounded grammar validation rejects duplicate members before JSON.parse can
// overwrite them, including escaped aliases in provider/JWT objects.
function uniqueJson(text) {
  let at=0,nodes=0;
  const space=()=>{while(/[\t\n\r ]/.test(text[at]??'!'))at++;};
  const string=()=>{
    const pattern=/"(?:[^"\\\x00-\x1f]|\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4}))*"/y;
    pattern.lastIndex=at;const match=pattern.exec(text);
    if(!match)throw new ClosedFailure('MALFORMED_RESPONSE');
    at=pattern.lastIndex;return JSON.parse(match[0]);
  };
  const value=depth=>{
    if(depth>32||++nodes>8192)throw new ClosedFailure('MALFORMED_RESPONSE');
    space();const first=text[at];
    if(first==='"'){string();return;}
    if(first==='{'||first==='['){
      const object=first==='{',end=object?'}':']',keys=new Set();at++;space();
      if(text[at]===end){at++;return;}
      for(;;){
        if(object){const key=string();if(keys.has(key))throw new ClosedFailure('MALFORMED_RESPONSE');keys.add(key);space();if(text[at++]!==':')throw new ClosedFailure('MALFORMED_RESPONSE');}
        value(depth+1);space();if(text[at]===end){at++;return;}
        if(text[at++]!==',')throw new ClosedFailure('MALFORMED_RESPONSE');space();
      }
    }
    const primitive=/(?:true|false|null|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)/y;
    primitive.lastIndex=at;if(!primitive.exec(text))throw new ClosedFailure('MALFORMED_RESPONSE');at=primitive.lastIndex;
  };
  value(0);space();if(at!==text.length)throw new ClosedFailure('MALFORMED_RESPONSE');
  return JSON.parse(text);
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
    const body = uniqueJson(new TextDecoder('utf-8', { fatal: true }).decode(Buffer.concat(retained)));
    if (!body || typeof body !== 'object' || Array.isArray(body) || body.status_code !== 200) throw new ClosedFailure('MALFORMED_RESPONSE');
    return body;
  } catch { throw new ClosedFailure('MALFORMED_RESPONSE'); }
}
// Prepared native HTTPS implementation. Private and unreachable from every current
// deployed entrypoint and factory. No proxies, redirects, retries or default logs.
function nativeExchange(options, bytes, primitive = httpsRequest) {
  return new Promise((resolve, reject) => {
    let req; let settled = false; let timer;
    const finish = (error, value) => {
      if (settled) return; settled = true; clearTimeout(timer);
      if (error) { req?.destroy(); reject(error); } else resolve(value);
    };
    timer = setTimeout(() => finish(new ClosedFailure('TIMEOUT')), TIMEOUT_MS);
    try {
      req = primitive(options, res => {
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
      req.on('error', error => finish(new ClosedFailure(safeError(error) === 'TIMEOUT' ? 'TIMEOUT' : 'PROVIDER_UNAVAILABLE')));
      req.end(bytes);
    } catch { finish(new ClosedFailure('UNKNOWN')); }
  });
}
function fixturePrimitive(reply) {
  // Literal in-memory event script exercises the same native parser/cancel path.
  // No user callback or network primitive can enter this construction boundary.
  return (_options, callback) => {
    const req = new EventEmitter(); req.destroy = () => { req.closed = true; };
    req.end = () => queueMicrotask(() => {
      if (!reply || reply.failure || (reply.delay_ms ?? 0) >= TIMEOUT_MS) {
        req.emit('error', new ClosedFailure(reply?.failure === 'TIMEOUT' || (reply?.delay_ms ?? 0) >= TIMEOUT_MS ? 'TIMEOUT' : 'PROVIDER_UNAVAILABLE')); return;
      }
      const res = new EventEmitter(); res.statusCode = reply.status; res.headers = reply.headers;
      res.destroy = () => { res.closed = true; }; callback(res);
      if (res.closed) return;
      for (const chunk of reply.chunks ?? []) { if (res.closed) return; res.emit('data', Buffer.from(chunk)); }
      if (!res.closed) res.emit('end');
    });
    return req;
  };
}
export function createProtectedStytchTransport(configuration, registration) {
  if (!liveSelectionAllowed(configuration, registration)) return disabledOperations();
  const protectedRegistration = registerReviewedDeployment(registration);
  const current = createReviewedCurrentControl(protectedRegistration);
  const keys = pinnedKeys(configuration.keyset, registration, Date.now());
  if (!protectedRegistration || !current || !keys) return disabledOperations();
  const credentials = loadServerCredentials(configuration, registration);
  if (!credentials) return disabledOperations();
  return new OfflineProtocol(protectedRegistration, credentials, null, current, keys, Date.now, true, configuration.keyset);
}
export function createOfflineStytchTransport({ registration, credentials, io, current,
  publicKeys = [], clock = Date.now, ownerChannel = false, keyset = null } = {}) {
  if (!registrationRecord(registration) || !offlineCustodyMatches(credentials, registration)
      || !fixtures.has(io) || !registrationCurrent(registration, currentControlRecord(current)) || typeof clock !== 'function') return disabledOperations();
  return new OfflineProtocol(registration, credentials, io, current, structuredClone(publicKeys), clock, false, keyset, ownerChannel === true);
}
class OfflineProtocol {
  #registration; #credentials; #io; #current; #keys; #clock;
  #method = null; #token = null; #session = null; #deadline = null;
  #retired = false; #busy = false; #highWater = null; #two = false; #totp = null;
  #native; #keyset; #ownerChannel; #envelope = null;
  constructor(r, c, io, current, keys, clock, native = false, keyset = null, ownerChannel = false) {
    this.#registration = r; this.#credentials = c; this.#io = io;
    this.#current = current; this.#keys = keys; this.#clock = clock; this.#native = native;
    this.#keyset = keyset === null ? null : structuredClone(keyset); this.#ownerChannel = native || ownerChannel; Object.freeze(this);
  }
  get mode() { return this.#native ? 'D01_DIAGNOSTIC_LIVE_STYTCH' : 'OFFLINE_PRE_SECRET_ONLY'; }
  toJSON() { return safeResult('DISABLED'); }
  retire() {
    this.#retired = true; this.#token = null; this.#session = null; this.#method = null;
    retireOwnerEnvelope(this.#envelope); this.#envelope = null;
    this.#totp = null; this.#credentials.dispose(); return safeResult('RETIRED', false, true);
  }
  #now() {
    const now = this.#clock();
    if (!stamp(now) || (this.#highWater !== null && now < this.#highWater)) throw new ClosedFailure('EXPIRED');
    this.#highWater = now; return now;
  }
  #check() {
    if (this.#retired || !(this.#native ? protectedCustodyMatches : offlineCustodyMatches)(this.#credentials, this.#registration)) throw new ClosedFailure('RETIRED');
    if (!registrationCurrent(this.#registration, currentControlRecord(this.#current))) throw new ClosedFailure('REGISTRATION');
    const now = this.#now();
    if (this.#keyset && !pinnedKeys(this.#keyset, registrationRecord(this.#registration), now)) throw new ClosedFailure('IDENTITY');
    if (this.#deadline !== null && now >= this.#deadline) throw new ClosedFailure('EXPIRED');
  }
  async #run(work) {
    if (this.#busy) return safeResult('REQUEST', false, true);
    this.#busy = true;
    try { this.#check(); await work(); if (!this.#retired) this.#check();
      const result = safeResult('NONE', true, !this.#native);
      return this.#native ? Object.freeze({ ...result, evidence_source: 'DIRECT_REMOTE_SESSION_OBSERVATION' }) : result; }
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
    if (this.#native) return nativeExchange(options, bytes);
    // A fixture can never select native IO; only the gated reviewed factory can.
    if (!fixture) throw new ClosedFailure('DISABLED');
    fixture.shapes.push({ op, protocol: options.protocol, host: options.hostname, path: options.path,
      method: options.method, keys: Object.keys(body).sort(), duration: body.session_duration_minutes ?? null,
      exact_session_id: body.session_id ?? null, credential_header_present: true, retries: 0 });
    const reply = fixture.queue.shift();
    if (fixture.nativeParser) return nativeExchange(options, bytes, fixturePrimitive(reply));
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
    if(typeof body.session_jwt!=='string'||body.session_jwt.length>16384)throw new ClosedFailure('IDENTITY');
    try {
      for(const part of body.session_jwt.split('.').slice(0,2))uniqueJson(new TextDecoder('utf-8',{fatal:true}).decode(Buffer.from(part,'base64url')));
    } catch { throw new ClosedFailure('IDENTITY'); }
    if (!verifyStytchIdentity(body.session_jwt, p, session.user_id, this.#keys, now)
        || typeof body.session_token !== 'string'
        || !(this.#native ? /^[\x21-\x7e]{1,2048}$/.test(body.session_token) : /^OFFLINE_[A-Z0-9_]{1,128}$/.test(body.session_token))) throw new ClosedFailure('IDENTITY');
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
          || !Array.isArray(b.recovery_codes)
          || (!this.#native && ![b.secret, b.qr_code, ...b.recovery_codes].every(v => typeof v === 'string' && /^OFFLINE_[A-Z0-9_]{1,128}$/.test(v)))) throw new ClosedFailure('IDENTITY');
      await this.#recheck(); this.#totp = { totp_id: b.totp_id };
      if (this.#ownerChannel) this.#envelope = createOwnerEnvelope(b, this.#deadline, !this.#native);
    } finally {
      // Only the private one-use Owner envelope survives; no evidence handoff.
      // Clear raw provider material even on malformed or failed post-check.
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
    retireOwnerEnvelope(this.#envelope); this.#envelope = null;
    await this.#recheck();
  }); }
  SESSION_AUTHENTICATE(input) { return this.#run(async () => {
    if (!this.#session || !this.#two || input !== undefined) throw new ClosedFailure('REQUEST'); await this.#recheck();
  }); }
  SESSION_REVOKE_EXACT(input) { return this.#run(async () => {
    if (!this.#session || input !== undefined) throw new ClosedFailure('REQUEST');
    await this.#exchange('SESSION_REVOKE_EXACT', { session_id: this.#session.session_id }); this.retire();
  }); }
  contextInfo() {
    try { this.#check(); return Object.freeze({ primary: !!this.#session, two: this.#two,
      retired: false, expires_at: this.#deadline }); }
    catch { this.retire(); return Object.freeze({ primary: false, two: false, retired: true, expires_at: null }); }
  }
  async ownerTransientHtml(csrf) {
    if (this.#busy) throw new ClosedFailure('REQUEST'); this.#busy = true;
    try {
      this.#check(); if (!this.#ownerChannel || !this.#session || this.#two || !this.#envelope) throw new ClosedFailure('RETIRED');
      await this.#recheck(); this.#check();
      const html = renderOwnerEnvelope(this.#envelope, csrf, this.#now()); this.#envelope = null; return html;
    } catch (error) { this.retire(); throw new ClosedFailure(safeError(error)); }
    finally { this.#busy = false; }
  }
}

import { randomUUID } from 'node:crypto';
import { closed, positive, stamp, identifier, sanitized, MAX_LIFETIME_MS, POINTS } from './policy.js';

const REG_KEYS = ['project_id', 'environment', 'issuer', 'client_id', 'owner_user_id',
  'owner_generation', 'binding_generation'];
const OBS_KEYS = ['source', 'project_id', 'environment', 'issuer', 'client_id', 'subject',
  'user_id', 'session_id', 'factors', 'expires_at', 'start', 'end'];
function registered(r) {
  return closed(r, REG_KEYS) && identifier(r.project_id) && r.environment === 'TEST'
    && r.issuer === `stytch.com/${r.project_id}` && r.client_id === r.project_id
    && identifier(r.owner_user_id) && positive(r.owner_generation) && positive(r.binding_generation);
}
function observation(o, r, now, requiredFactors) {
  if (!closed(o, OBS_KEYS) || o.source !== 'OFFLINE_FAKE_FIXTURE'
      || !identifier(o.user_id) || !identifier(o.session_id)
      || !stamp(o.start) || !stamp(o.end) || o.start > o.end || o.end > now
      || !stamp(o.expires_at) || o.expires_at <= now) return 'SCHEMA';
  if (o.project_id !== r.project_id || o.environment !== r.environment
      || o.issuer !== r.issuer || o.client_id !== r.client_id || o.subject !== o.user_id) return 'IDENTITY';
  if (!Array.isArray(o.factors) || o.factors.length !== requiredFactors.length) return 'FACTORS';
  const types = new Set();
  for (const f of o.factors) {
    if (!closed(f, ['type', 'last_authenticated_at']) || !requiredFactors.includes(f.type)
        || types.has(f.type) || !stamp(f.last_authenticated_at)
        || f.last_authenticated_at > now || now - f.last_authenticated_at >= MAX_LIFETIME_MS) return 'FACTORS';
    types.add(f.type);
  }
  return null;
}

// This type is a test-only semantic model, never imported by the deployed route.
// It stores no bearer/seed/OTP, creates no canonical authority bodies, and has no
// live data constructor. Synthetic PASS always has qualified_live=false.
export class OfflineDiagnosticModel {
  #registration; #primary; #two; #context; #state = 'SIGNED_OUT';
  #clock; #highWater; #incarnation = randomUUID(); #generation = 0;
  #terminal = false; #point = 0; #lastError = 'NONE';
  constructor(registration, clock) {
    this.#registration = registered(registration) ? structuredClone(registration) : null;
    this.#clock = clock; this.#highWater = null;
  }
  #now() {
    const n = this.#clock();
    if (!stamp(n) || (this.#highWater !== null && n < this.#highWater)) throw new Error('CLOCK');
    this.#highWater = n; return n;
  }
  #deny(error = 'STATE') {
    this.#state = 'DIAGNOSTIC_DENIED'; this.#lastError = error;
    this.#context = null; this.#primary = null; this.#two = null;
    return this.output('DENY');
  }
  #valid() {
    if (!this.#registration) return 'REGISTRATION';
    if (!this.#context) return 'RETIRED';
    if (this.#context.incarnation !== this.#incarnation) return 'RESTART';
    if (this.#context.owner_generation !== this.#registration.owner_generation
        || this.#context.binding_generation !== this.#registration.binding_generation) return 'GENERATION';
    if (REG_KEYS.some(key => this.#context.registration[key] !== this.#registration[key])) return 'GENERATION';
    if (this.#now() >= this.#context.expires_at) return 'EXPIRED';
    return null;
  }
  output(result = 'UNKNOWN', point = null) {
    let now;
    try { now = this.#now(); }
    catch {
      now = this.#highWater; result = 'DENY'; this.#lastError = 'CLOCK';
      this.#state = 'DIAGNOSTIC_DENIED'; this.#context = null; this.#primary = null; this.#two = null;
    }
    if (this.#context && now >= this.#context.expires_at) {
      result = 'DENY'; this.#lastError = 'EXPIRED'; this.#state = 'DIAGNOSTIC_DENIED';
      this.#context = null; this.#primary = null; this.#two = null;
    }
    const o = this.#two;
    return sanitized({ evidence_source: 'OFFLINE_FAKE_FIXTURE', state: this.#state, result,
      case_id: o && this.#registration && o.user_id === this.#registration.owner_user_id ? 'U_OWNER' : 'UNREGISTERED',
      project_matches: !!o && o.project_id === this.#registration?.project_id,
      continuity: !!o && o.session_id === this.#primary?.session_id,
      factors_fresh: !!o && o.factors.every(f => now - f.last_authenticated_at < MAX_LIFETIME_MS),
      factor_times: o ? ['EMAIL_OTP', 'TOTP'].map(type => o.factors.find(f => f.type === type).last_authenticated_at) : undefined,
      context_generation: this.#context?.generation,
      owner_generation: this.#context?.owner_generation, binding_generation: this.#context?.binding_generation,
      expires_at: this.#context?.expires_at, start: o?.start, end: now, point,
      error_class: this.#lastError });
  }
  step(action, data) {
    try {
      const now = this.#now();
      if (!this.#registration) return this.#deny('REGISTRATION');
      if (['DIAGNOSTIC_DENIED', 'DIAGNOSTIC_COMPLETE', 'LOCAL_CONTEXT_RETIRED'].includes(this.#state)) return this.#deny('REUSED');
      if (action === 'EMAIL_START' && this.#state === 'SIGNED_OUT' && data === undefined) {
        this.#state = 'EMAIL_OTP_PENDING';
      } else if (action === 'PRIMARY_OBSERVATION' && this.#state === 'EMAIL_OTP_PENDING') {
        const error = observation(data, this.#registration, now, ['EMAIL_OTP']);
        if (error) return this.#deny(error);
        this.#primary = structuredClone(data); this.#state = 'PRIMARY_FACTOR_VERIFIED';
      } else if (action === 'TOTP_ENROLLMENT_START' && this.#state === 'PRIMARY_FACTOR_VERIFIED' && data === undefined) {
        this.#state = 'TOTP_ENROLLMENT_REQUIRED';
      } else if (action === 'TOTP_START' && ['PRIMARY_FACTOR_VERIFIED', 'TOTP_ENROLLMENT_REQUIRED'].includes(this.#state) && data === undefined) {
        this.#state = 'TOTP_PENDING';
      } else if (action === 'TOTP_OBSERVATION' && this.#state === 'TOTP_PENDING') {
        const error = observation(data, this.#registration, now, ['EMAIL_OTP', 'TOTP']);
        if (error) return this.#deny(error);
        if (data.user_id !== this.#primary.user_id || data.session_id !== this.#primary.session_id
            || data.factors.find(f => f.type === 'EMAIL_OTP').last_authenticated_at
              !== this.#primary.factors[0].last_authenticated_at) return this.#deny('IDENTITY');
        this.#two = structuredClone(data); this.#state = 'TWO_FACTOR_VERIFIED';
      } else if (action === 'OWNER_EQUALITY' && this.#state === 'TWO_FACTOR_VERIFIED' && data === undefined) {
        if (this.#two.user_id !== this.#registration.owner_user_id) return this.#deny('IDENTITY');
        // Anchor to earliest factor time, never page creation/recheck/reload.
        const deadline = Math.min(this.#two.expires_at,
          ...this.#two.factors.map(f => f.last_authenticated_at + MAX_LIFETIME_MS));
        if (now >= deadline) return this.#deny('EXPIRED');
        this.#context = { generation: ++this.#generation, challenge: randomUUID(),
          incarnation: this.#incarnation, expires_at: deadline,
          registration: structuredClone(this.#registration),
          owner_generation: this.#registration.owner_generation,
          binding_generation: this.#registration.binding_generation };
        this.#state = 'OWNER_EQUALITY_SIMULATED';
      } else return this.#deny('STATE');
      return this.output('PASS');
    } catch { return this.#deny('CLOCK'); }
  }
  // Recheck consumes typed observation projection, not provider/raw browser JSON.
  recheck(point, envelope) {
    try {
      if (!['OWNER_EQUALITY_SIMULATED', 'SESSION_RECHECK_RESULT'].includes(this.#state)) return this.#deny('STATE');
      const valid = this.#valid(); if (valid) return this.#deny(valid);
      if (point !== POINTS[this.#point]) return this.#deny('REUSED');
      if (!closed(envelope, ['kind', 'observation']) || envelope.kind !== 'OFFLINE_FAKE_FIXTURE') {
        return this.#deny(envelope?.kind === 'TIMEOUT' ? 'TIMEOUT' : envelope?.kind === 'ERROR' ? 'PROVIDER_ERROR' : 'UNKNOWN');
      }
      const o = envelope.observation;
      const error = observation(o, this.#registration, this.#now(), ['EMAIL_OTP', 'TOTP']);
      if (error) return this.#deny(error);
      if (o.end < this.#highWater) return this.#deny('UNKNOWN');
      if (o.user_id !== this.#two.user_id || o.session_id !== this.#two.session_id
          || o.expires_at !== this.#two.expires_at
          || o.factors.some(f => f.last_authenticated_at !== this.#two.factors.find(p => p.type === f.type).last_authenticated_at)) {
        return this.#deny('IDENTITY');
      }
      if (point === 'DECISION_POST_SIMULATION' && !this.#terminal) return this.#deny('STATE');
      this.#two = structuredClone(o); // Latest sanitized observation times, never a refreshed deadline.
      ++this.#point;
      this.#state = point === 'CLAIM_SIMULATION' ? 'DIAGNOSTIC_COMPLETE' : 'SESSION_RECHECK_RESULT';
      return this.output('PASS', point);
    } catch { return this.#deny('CLOCK'); }
  }
  terminal(choice, envelope) {
    if (this.#terminal || this.#point !== 1 || !['CONFIRM_SIMULATION', 'DENY_SIMULATION'].includes(choice)) return this.#deny('REUSED');
    this.#terminal = true;
    if (choice === 'DENY_SIMULATION') return this.retire('LOCAL_LOGOUT');
    return this.recheck('DECISION_POST_SIMULATION', envelope);
  }
  reload() {
    try { const error = this.#valid(); return error ? this.#deny(error) : this.output('UNKNOWN'); }
    catch { return this.#deny('CLOCK'); }
  }
  // Protected test harness administration only. Never a browser registration API.
  replaceRegistration(registration) {
    this.#registration = registered(registration) ? structuredClone(registration) : null;
    return this.reload();
  }
  retire(reason) {
    if (!['LOCAL_LOGOUT', 'ACCOUNT_SWITCH', 'REMOTE_REVOKE_OBSERVED'].includes(reason)) return this.#deny('SCHEMA');
    if (this.#state === 'LOCAL_CONTEXT_RETIRED' || this.#state === 'DIAGNOSTIC_COMPLETE' || this.#state === 'DIAGNOSTIC_DENIED') return this.#deny('REUSED');
    this.#state = 'LOCAL_CONTEXT_RETIRED'; this.#context = null;
    this.#two = null; this.#primary = null; this.#lastError = 'RETIRED';
    return this.output('DENY');
  }
  restart() { this.#incarnation = randomUUID(); return this.reload(); }
}

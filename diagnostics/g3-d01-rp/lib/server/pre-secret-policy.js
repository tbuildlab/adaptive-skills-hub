// Server-only, future source/config activation requires a separate reviewed change.
if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');
export const CODE_REVIEWED_LIVE_ENABLED = false;
export const DEPLOYMENT_REGISTRATION_ENABLED = false;
export const BASE = 'https://test.stytch.com';
export const TIMEOUT_MS = 4000;
export const RESPONSE_MAX_BYTES = 65536;
export const REQUEST_MAX_BYTES = 4096;
export const PATHS = Object.freeze({
  EMAIL_OTP_SEND: '/v1/otps/email/send',
  EMAIL_OTP_AUTHENTICATE: '/v1/otps/authenticate',
  TOTP_CREATE: '/v1/totps',
  TOTP_AUTHENTICATE: '/v1/totps/authenticate',
  SESSION_AUTHENTICATE: '/v1/sessions/authenticate',
  SESSION_REVOKE_EXACT: '/v1/sessions/revoke',
});
const CLASSES = new Set(['NONE', 'DISABLED', 'REQUEST', 'REGISTRATION', 'CREDENTIAL', 'RETIRED',
  'AUTH_REJECTED', 'SESSION_INVALID', 'RATE_LIMITED', 'PROVIDER_UNAVAILABLE',
  'TIMEOUT', 'MALFORMED_RESPONSE', 'UNKNOWN', 'IDENTITY', 'FACTORS', 'EXPIRED']);
export function safeResult(error = 'DISABLED', success = false, fixture = false) {
  return Object.freeze({ diagnostic: 'NEXUS_G3_D01_DIAGNOSTIC_ONLY', authority: 'NONE',
    real_admission: 'DISABLED', qualified_live: false,
    evidence_source: fixture ? 'OFFLINE_PRE_SECRET_FIXTURE' : 'FAKE_DISABLED',
    result: success ? 'PASS' : 'DENY', error_class: CLASSES.has(error) ? error : 'UNKNOWN' });
}
export function safeError(error) {
  // Only our tagged failures are classified. Provider/network free text is ignored.
  return error instanceof ClosedFailure && CLASSES.has(error.code) ? error.code : 'UNKNOWN';
}
export class ClosedFailure extends Error {
  constructor(code) { super('DIAGNOSTIC_DENY'); this.code = CLASSES.has(code) ? code : 'UNKNOWN'; }
  toJSON() { return safeResult(this.code); }
}
export function disabledOperations() {
  return Object.freeze({ mode: 'FAKE_DISABLED',
    ...Object.fromEntries(Object.keys(PATHS).map(op => [op, async () => safeResult()])),
    retire() { return safeResult('RETIRED'); }, toJSON() { return safeResult(); } });
}
export function liveSelectionAllowed(configuration, registration) {
  // Do not inspect arguments, getters or environment while either build gate is off.
  if (!CODE_REVIEWED_LIVE_ENABLED || !DEPLOYMENT_REGISTRATION_ENABLED) return false;
  return configuration?.mode === 'D01_DIAGNOSTIC_LIVE_STYTCH'
    && configuration?.deployment_tier === 'PRODUCTION'
    && configuration?.origin === 'https://nexus-g3-qual.vercel.app'
    && configuration?.registration_generation === registration?.application_generation
    && configuration?.deployment_revision === registration?.deployment_revision
    && registration?.source === 'OWNER_REVIEWED'
    && typeof registration?.delivery_email === 'string'
    && /^[^\s@]+@[^\s@]+$/.test(registration.delivery_email);
}

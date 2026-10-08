// NEXUS_G3_D01_DIAGNOSTIC_ONLY. No environment or credential access.
export const ORIGIN = 'https://nexus-g3-qual.vercel.app';
export const MAX_LIFETIME_MS = 300000;
export const G3_D01_LIVE_DIAGNOSTIC_ENABLED = false;
export const LABELS = Object.freeze({
  diagnostic: 'NEXUS_G3_D01_DIAGNOSTIC_ONLY',
  classification: 'LIVE_DIAGNOSTIC_EVIDENCE_ONLY',
  authority: 'NONE', real_admission: 'DISABLED', qualified_live: false,
});
export const POINTS = Object.freeze([
  'PAGE', 'DECISION_POST_SIMULATION', 'RECEIPT_SIMULATION',
  'INTENT_SIMULATION', 'CLAIM_SIMULATION',
]);
export const ERRORS = Object.freeze([
  'NONE', 'LIVE_DISABLED', 'REGISTRATION', 'STATE', 'SCHEMA', 'IDENTITY',
  'FACTORS', 'EXPIRED', 'RESTART', 'GENERATION', 'REUSED', 'CLOCK',
  'UNKNOWN', 'PROVIDER_ERROR', 'TIMEOUT', 'ORIGIN', 'CSRF', 'REQUEST',
  'CAPACITY', 'RETIRED',
]);
export function closed(value, keys) {
  return value !== null && typeof value === 'object' && !Array.isArray(value)
    && Object.getPrototypeOf(value) === Object.prototype
    && Object.keys(value).length === keys.length
    && keys.every(k => Object.hasOwn(value, k));
}
export function positive(value) { return Number.isSafeInteger(value) && value > 0; }
export function stamp(value) { return Number.isSafeInteger(value) && value >= 0; }
export function identifier(value) {
  return typeof value === 'string' && /^[a-zA-Z0-9_-]{1,128}$/.test(value);
}
// Deliberately projects only bounded, closed enums and integer timestamps.
// No arbitrary provider messages, request IDs, identifiers or raw objects escape.
export function sanitized(input = {}) {
  const result = ['PASS', 'DENY', 'UNKNOWN'].includes(input.result) ? input.result : 'DENY';
  return Object.freeze({ ...LABELS,
    evidence_source: input.evidence_source === 'OFFLINE_FAKE_FIXTURE'
      ? 'OFFLINE_FAKE_FIXTURE' : 'FAKE_DISABLED',
    result,
    state: STATES.includes(input.state) ? input.state : 'DIAGNOSTIC_DENIED',
    case_id: ['U_OWNER', 'U_NONOWNER', 'U_FOREIGN', 'UNREGISTERED'].includes(input.case_id)
      ? input.case_id : 'UNREGISTERED',
    provider_project_alias: input.project_matches === true ? 'P_OWNER' : 'UNVERIFIED',
    user_id_hash_or_registered_alias: input.case_id === 'U_OWNER' ? 'U_OWNER' : 'UNVERIFIED',
    session_id_hash_or_registered_alias: input.continuity === true ? 'SAME_DIAGNOSTIC_LINEAGE' : 'UNVERIFIED',
    factor_types: input.factors_fresh === true ? ['EMAIL_OTP', 'TOTP'] : [],
    factor_freshness_status: input.factors_fresh === true ? 'FRESH_SIMULATED' : 'UNVERIFIED',
    factor_last_authenticated_at: Array.isArray(input.factor_times)
      && input.factor_times.length === 2 && input.factor_times.every(stamp) ? [...input.factor_times] : [],
    context_generation: positive(input.context_generation) ? input.context_generation : null,
    owner_generation: positive(input.owner_generation) ? input.owner_generation : null,
    binding_generation: positive(input.binding_generation) ? input.binding_generation : null,
    observation_start: stamp(input.start) ? input.start : null,
    observation_end: stamp(input.end) ? input.end : null,
    context_expires_at: stamp(input.expires_at) ? input.expires_at : null,
    observation_point: POINTS.includes(input.point) ? input.point : null,
    error_class: ERRORS.includes(input.error_class) ? input.error_class : 'UNKNOWN',
  });
}
export const STATES = Object.freeze([
  'SIGNED_OUT', 'EMAIL_OTP_PENDING', 'PRIMARY_FACTOR_VERIFIED',
  'TOTP_ENROLLMENT_REQUIRED', 'TOTP_PENDING', 'TWO_FACTOR_VERIFIED',
  'OWNER_EQUALITY_SIMULATED', 'SESSION_RECHECK_RESULT', 'LOCAL_CONTEXT_RETIRED',
  'DIAGNOSTIC_COMPLETE', 'DIAGNOSTIC_DENIED',
]);

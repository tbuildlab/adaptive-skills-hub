import { LABELS, MAX_LIFETIME_MS, identifier, positive, stamp, POINTS, closed } from './policy.js';

const ERRORS = new Set(['NONE', 'LIVE_DISABLED', 'REGISTRATION', 'STATE', 'REQUEST', 'MALFORMED',
  'IDENTITY', 'FACTORS', 'EXPIRED', 'RETIRED', 'BUSY', 'CLOCK', 'TIMEOUT', 'RATE_LIMIT',
  'PROVIDER_ERROR', 'UNKNOWN', 'ENROLLMENT']);
export function evidence(fields = {}) {
  // No string from a provider exception/header is copied; request ID must be UUID.
  const requestId = typeof fields.request_id === 'string'
    && /^[a-f0-9]{8}-[a-f0-9]{4}-[1-5][a-f0-9]{3}-[89ab][a-f0-9]{3}-[a-f0-9]{12}$/i.test(fields.request_id)
    ? fields.request_id : null;
  const validFactors = Array.isArray(fields.factor_times) && fields.factor_times.length <= 2
    && fields.factor_times.every(f => closed(f, ['type', 'at'])
      && ['EMAIL_OTP', 'TOTP'].includes(f.type) && stamp(f.at))
    && new Set(fields.factor_times.map(f => f.type)).size === fields.factor_times.length;
  return Object.freeze({ ...LABELS, evidence_source: 'OFFLINE_ADAPTER_FIXTURE',
    result: fields.result === 'PASS' ? 'PASS' : 'DENY',
    error_class: ERRORS.has(fields.error_class) ? fields.error_class : 'UNKNOWN',
    request_id: requestId,
    provider_project_alias: fields.matched === true ? 'P_OWNER' : 'UNVERIFIED',
    user_id_hash_or_registered_alias: fields.matched === true ? 'U_OWNER' : 'UNVERIFIED',
    session_id_hash_or_registered_alias: fields.matched === true ? 'SAME_DIAGNOSTIC_LINEAGE' : 'UNVERIFIED',
    factor_types: validFactors ? fields.factor_times.map(f => f.type) : [],
    factor_last_authenticated_at: validFactors ? fields.factor_times.map(f => f.at) : [],
    factor_freshness_status: fields.matched === true ? 'FRESH_SIMULATED' : 'UNVERIFIED',
    observation_start: stamp(fields.start) ? fields.start : null,
    observation_end: stamp(fields.end) ? fields.end : null,
    owner_generation: positive(fields.owner_generation) ? fields.owner_generation : null,
    binding_generation: positive(fields.binding_generation) ? fields.binding_generation : null,
    observation_point: POINTS.includes(fields.point) ? fields.point : null,
    context_expires_at: stamp(fields.deadline) ? fields.deadline : null,
  });
}
export function timestamp(value) {
  if (typeof value !== 'string') return null;
  const match = /^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,9}))?Z$/.exec(value);
  if (!match) return null;
  // Floor sub-millisecond precision: never round a freshness/expiry deadline up.
  const canonical = `${match[1]}.${(match[2] ?? '').padEnd(3, '0').slice(0, 3)}Z`;
  const ms = Date.parse(canonical);
  if (!stamp(ms) || new Date(ms).toISOString() !== canonical) return null;
  return ms;
}
export function projectSession(body, registration, now, factors) {
  // Raw response never escapes. Unknown user metadata/provider fields are discarded.
  if (!body || typeof body !== 'object' || Array.isArray(body) || !body.session || !body.user
      || body.status_code !== 200 || !identifier(body.user.user_id)
      || !identifier(body.session.session_id) || body.user.is_locked !== false
      || body.user.status !== 'active' || (body.user_id !== undefined && body.user_id !== body.user.user_id)
      || body.session.user_id !== body.user.user_id) throw new Error('MALFORMED');
  if (body.user.user_id !== registration.owner_user_id) throw new Error('IDENTITY');
  if ([body, body.user, body.session].some(o => o.project_id !== undefined && o.project_id !== registration.project_id)) throw new Error('IDENTITY');
  const expires = timestamp(body.session.expires_at);
  if (expires === null) throw new Error('MALFORMED');
  if (expires <= now || expires > now + 900000) throw new Error('EXPIRED');
  const providerFactors = body.session.authentication_factors;
  if (!Array.isArray(providerFactors) || providerFactors.length !== factors.length) throw new Error('FACTORS');
  const normalized = new Map();
  for (const factor of providerFactors) {
    let type;
    if (['otp', 'email_otp'].includes(factor.type) && factor.delivery_method === 'email') type = 'EMAIL_OTP';
    if (factor.type === 'totp' && factor.delivery_method === 'authenticator_app') type = 'TOTP';
    const at = timestamp(factor.last_authenticated_at);
    if (!factors.includes(type) || normalized.has(type) || at === null
        || at > now || now - at >= MAX_LIFETIME_MS) throw new Error('FACTORS');
    normalized.set(type, { type, at });
  }
  return { user_id: body.user.user_id, session_id: body.session.session_id,
    expires_at: expires, factors: factors.map(type => normalized.get(type)) };
}

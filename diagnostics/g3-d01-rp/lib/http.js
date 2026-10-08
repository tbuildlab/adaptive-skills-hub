import { randomBytes, timingSafeEqual } from 'node:crypto';
import { ORIGIN, MAX_LIFETIME_MS, sanitized, closed, stamp } from './policy.js';
import { selectAdapter } from './adapter.js';

const COOKIE_NAME = '__Host-g3d01';
const host = new URL(ORIGIN).host;
const actions = new Set(['EMAIL_START', 'EMAIL_VERIFY', 'TOTP_ENROLLMENT_START',
  'TOTP_VERIFY', 'PAGE', 'DECISION_POST_SIMULATION', 'RECEIPT_SIMULATION',
  'INTENT_SIMULATION', 'CLAIM_SIMULATION', 'LOCAL_LOGOUT', 'ACCOUNT_SWITCH',
  'REVOKE_OBSERVATION']);
const token = () => randomBytes(32).toString('hex');
function same(a, b) {
  return typeof a === 'string' && typeof b === 'string' && a.length === 64
    && b.length === 64 && timingSafeEqual(Buffer.from(a), Buffer.from(b));
}
function cookie(header) {
  if (header === undefined) return null;
  if (typeof header !== 'string' || header.length > 2048) throw new Error('REQUEST');
  const values = header.split(';').map(p => p.trim()).filter(p => p.startsWith(`${COOKIE_NAME}=`));
  if (values.length > 1) throw new Error('REQUEST');
  if (!values.length) return null;
  const value = values[0].slice(COOKIE_NAME.length + 1);
  if (!/^[a-f0-9]{64}$/.test(value)) throw new Error('REQUEST');
  return value;
}
export function checkRequest(req) {
  // Proxy headers never establish identity/origin. Preview/custom/localhost hosts deny.
  if (req.headers?.host !== host || (req.headers.origin !== undefined && req.headers.origin !== ORIGIN)
      || ['cross-site', 'same-site'].includes(req.headers['sec-fetch-site'])) return 'ORIGIN';
  if (req.url !== '/api/diagnostic' || !['GET', 'POST'].includes(req.method)) return 'REQUEST';
  if (req.method === 'POST' && req.headers.origin !== ORIGIN) return 'ORIGIN';
  return null;
}
export const RESPONSE_HEADERS = Object.freeze({
  'Content-Type': 'application/json; charset=utf-8',
  'Cache-Control': 'no-store',
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'Referrer-Policy': 'no-referrer',
  'Content-Security-Policy': "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
});

// In-memory *page anti-CSRF* store only: no Owner binding, bearer or provider state.
// No shared persistence => a different worker/restart rejects an old cookie.
// Future live implementation needs reviewed protected custody; no silent rehydrate.
export function makeHandler({ clock = Date.now, capacity = 128 } = {}) {
  if (!Number.isSafeInteger(capacity) || capacity < 1 || capacity > 128) throw new Error('CAPACITY');
  const pages = new Map(); let highWater = null;
  selectAdapter(); // Hard FAKE_DISABLED; no environment reads, provider or fake injection.
  return async function handler(req, res) {
    function reply(status, state, error, csrf = null) {
      for (const [key, value] of Object.entries(RESPONSE_HEADERS)) res.setHeader(key, value);
      // CSRF is a transport field, never a diagnostic evidence field/export.
      res.statusCode = status;
      res.end(JSON.stringify({ ...sanitized({ state, error_class: error, result: 'DENY' }),
        live_diagnostic_enabled: false, adapter_mode: 'FAKE_DISABLED', csrf }));
    }
    try {
      const rejected = checkRequest(req);
      if (rejected) return reply(403, 'DIAGNOSTIC_DENIED', rejected);
      const now = clock();
      if (!stamp(now) || (highWater !== null && now < highWater)) {
        pages.clear(); return reply(403, 'DIAGNOSTIC_DENIED', 'CLOCK');
      }
      highWater = now;
      for (const [key, p] of pages) if (now >= p.expires_at) pages.delete(key);
      const supplied = cookie(req.headers.cookie);
      let p = supplied === null ? null : pages.get(supplied);
      if (supplied !== null && !p) return reply(403, 'DIAGNOSTIC_DENIED', 'RETIRED');
      if (req.method === 'GET') {
        if (!p) {
          if (pages.size >= capacity) return reply(503, 'DIAGNOSTIC_DENIED', 'CAPACITY');
          const key = token(); p = { csrf: token(), expires_at: now + MAX_LIFETIME_MS };
          pages.set(key, p);
          res.setHeader('Set-Cookie', `${COOKIE_NAME}=${key}; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=300`);
        }
        return reply(200, 'SIGNED_OUT', 'LIVE_DISABLED', p.csrf);
      }
      if (!p || !same(req.headers['x-g3-csrf'], p.csrf)) return reply(403, 'DIAGNOSTIC_DENIED', 'CSRF');
      if (req.headers['content-type'] !== 'application/json'
          || !closed(req.body, ['action']) || !actions.has(req.body.action)) return reply(400, 'DIAGNOSTIC_DENIED', 'REQUEST');
      if (['LOCAL_LOGOUT', 'ACCOUNT_SWITCH'].includes(req.body.action)) {
        pages.delete(supplied);
        res.setHeader('Set-Cookie', `${COOKIE_NAME}=; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=0`);
        return reply(200, 'LOCAL_CONTEXT_RETIRED', 'RETIRED');
      }
      // No flags/registration from browser or environment can change this branch.
      return reply(403, 'DIAGNOSTIC_DENIED', 'LIVE_DISABLED', p.csrf);
    } catch {
      // Never serialize caught objects, headers, request body, stack or env.
      return reply(400, 'DIAGNOSTIC_DENIED', 'REQUEST');
    }
  };
}

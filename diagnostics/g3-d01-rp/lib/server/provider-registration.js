if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');
import { closed, identifier, positive, ORIGIN } from '../policy.js';
const records = new WeakMap();
const controls = new WeakMap();
const CONTROL_KEYS = ['project_id', 'owner_user_id', 'project_generation', 'application_generation',
  'owner_generation', 'binding_generation', 'deployment_revision'];
const KEYS = ['provider', 'environment', 'project_id', 'owner_user_id', 'project_generation',
  'application_generation', 'owner_generation', 'binding_generation', 'origin', 'factors',
  'session_max_minutes', 'context_max_ms', 'issuer', 'audience', 'deployment_revision',
  'source', 'review_id', 'delivery_email'];
function valid(v, source) {
  return closed(v, KEYS) && v.provider === 'STYTCH_CONSUMER' && v.environment === 'TEST'
    && /^project-test-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$/.test(v.project_id) && identifier(v.owner_user_id)
    && ['project_generation', 'application_generation', 'owner_generation', 'binding_generation'].every(k => positive(v[k]))
    && v.origin === ORIGIN && Array.isArray(v.factors) && v.factors.join(',') === 'EMAIL_OTP,TOTP'
    && v.session_max_minutes === 15 && v.context_max_ms === 300000
    && v.issuer === `stytch.com/${v.project_id}` && v.audience === v.project_id
    && identifier(v.deployment_revision) && v.source === source && identifier(v.review_id)
    && ((source === 'OWNER_REVIEWED' && v.delivery_email === null)
      || (typeof v.delivery_email === 'string' && v.delivery_email.length <= 254
        && /^[^\s@]+@[^\s@]+$/.test(v.delivery_email)));
}
export function validateReviewedRegistration(value) { return valid(value, 'OWNER_REVIEWED'); }
export function registerReviewedDeployment(value) {
  if (!validateReviewedRegistration(value)) return null;
  const copy = structuredClone(value); Object.freeze(copy.factors); Object.freeze(copy);
  const handle = Object.freeze({ kind: 'REVIEWED_REGISTRATION', toJSON() { return { authority: 'NONE' }; } });
  records.set(handle, copy); return handle;
}
export function createReviewedCurrentControl(handle) {
  const r = records.get(handle);
  if (!r || r.source !== 'OWNER_REVIEWED') return null;
  const current = Object.freeze(Object.fromEntries(CONTROL_KEYS.map(k => [k, r[k]])));
  const control = Object.freeze({ kind: 'REVIEWED_DEPLOYMENT_CONTROL', toJSON() { return { authority: 'NONE' }; } });
  controls.set(control, current); return control;
}
export function createOfflineRegistration(value) {
  if (!valid(value, 'OFFLINE_SYNTHETIC') || !value.owner_user_id.startsWith('fixture-')
      || !value.delivery_email.endsWith('@example.invalid')) return null;
  const copy = structuredClone(value); Object.freeze(copy.factors); Object.freeze(copy);
  const handle = Object.freeze({ kind: 'OFFLINE_REGISTRATION', toJSON() { return { authority: 'NONE' }; } });
  records.set(handle, copy); return handle;
}
// Server-to-server registration projection only. No bearer fields in this record.
export function registrationRecord(handle) { return records.get(handle) ?? null; }
export function registrationCurrent(handle, current) {
  const r = records.get(handle);
  return !!r && closed(current, CONTROL_KEYS)
    && Object.keys(current).every(k => current[k] === r[k]);
}
export function createOfflineCurrentControl(value) {
  if (!closed(value, CONTROL_KEYS)) return null;
  const handle = Object.freeze({ kind: 'OFFLINE_CONTROL',
    replace(next) { controls.set(handle, closed(next, CONTROL_KEYS) ? structuredClone(next) : null); },
    toJSON() { return { authority: 'NONE' }; } });
  controls.set(handle, structuredClone(value)); return handle;
}
export function currentControlRecord(handle) { return controls.get(handle) ?? null; }

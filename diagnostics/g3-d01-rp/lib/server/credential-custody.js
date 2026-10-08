if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');
import { liveSelectionAllowed, PATHS, ClosedFailure, safeResult } from './pre-secret-policy.js';
import { registrationRecord } from './provider-registration.js';
const custody = new WeakMap();
function store(project, secret, fixture) {
  const handle = Object.freeze({ kind: fixture ? 'OFFLINE_CUSTODY' : 'PROTECTED_CUSTODY',
    dispose() { custody.delete(handle); }, toJSON() { return safeResult('CREDENTIAL'); },
    [Symbol.toPrimitive]() { return '[PROTECTED_CUSTODY]'; } });
  custody.set(handle, { project, secret, fixture }); return handle;
}
export function createOfflineCredentials(values, registration) {
  const r = registrationRecord(registration);
  if (!r || values === null || typeof values !== 'object') return null;
  // Inspect exactly two named own data properties, never enumerate or invoke getters.
  const p = Object.getOwnPropertyDescriptor(values, 'STYTCH_PROJECT_ID');
  const s = Object.getOwnPropertyDescriptor(values, 'STYTCH_SECRET');
  if (!p || !s || !Object.hasOwn(p, 'value') || !Object.hasOwn(s, 'value')
      || p.value !== r.project_id || s.value !== 'OFFLINE_CREDENTIAL_PLACEHOLDER') return null;
  return store(p.value, s.value, true);
}
export function loadServerCredentials(configuration, registration) {
  if (!liveSelectionAllowed(configuration, registration)) return null;
  // Future named reads, unreachable in this build. No enumeration, fallback or disk lookup.
  const project = process.env.STYTCH_PROJECT_ID;
  const secret = process.env.STYTCH_SECRET;
  if (project !== registration.project_id || typeof secret !== 'string'
      || !/^secret-test-[A-Za-z0-9_-]{16,256}$/.test(secret)) return null;
  return store(project, secret, false);
}
export function offlineCustodyMatches(handle, registration) {
  const value = custody.get(handle); const r = registrationRecord(registration);
  return !!value && value.fixture === true && value.project === r?.project_id;
}
export function protectedCustodyMatches(handle, registration) {
  const value = custody.get(handle); const r = registrationRecord(registration);
  return !!value && value.fixture === false && r?.source === 'OWNER_REVIEWED' && value.project === r.project_id;
}
export function authorizeFixedRequest(handle, request) {
  const value = custody.get(handle);
  if (!value || request.hostname !== 'test.stytch.com' || request.protocol !== 'https:'
      || request.port !== 443 || request.method !== 'POST' || !Object.values(PATHS).includes(request.path)
      || request.servername !== 'test.stytch.com' || request.rejectUnauthorized !== true) throw new ClosedFailure('CREDENTIAL');
  request.headers.Authorization = `Basic ${Buffer.from(`${value.project}:${value.secret}`).toString('base64')}`;
}

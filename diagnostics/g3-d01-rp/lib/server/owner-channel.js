if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');
import { ClosedFailure } from './pre-secret-policy.js';
const material = new WeakMap();
const escape = s => s.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
export function createOwnerEnvelope(body, expires, fixture) {
  const valid = fixture ? v => typeof v === 'string' && /^OFFLINE_[A-Z0-9_]{1,128}$/.test(v)
    : v => typeof v === 'string' && v.length > 0 && v.length <= 1024 && /^[\x20-\x7e]+$/.test(v);
  if (!valid(body.secret) || !Array.isArray(body.recovery_codes) || body.recovery_codes.length > 16
      || !body.recovery_codes.every(valid) || !Number.isSafeInteger(expires)) throw new ClosedFailure('MALFORMED_RESPONSE');
  const handle = Object.freeze({ toJSON() { return { authority: 'NONE', result: 'DENY' }; } });
  material.set(handle, { seed: body.secret, recovery: [...body.recovery_codes], expires }); return handle;
}
export function retireOwnerEnvelope(handle) {
  const value = material.get(handle);
  if (value) { value.seed = null; value.recovery.fill(null); material.delete(handle); }
}
export function renderOwnerEnvelope(handle, csrf, now) {
  const value = material.get(handle);
  if (!value || !/^[a-f0-9]{64}$/.test(csrf) || now >= value.expires) { retireOwnerEnvelope(handle); throw new ClosedFailure('RETIRED'); }
  try {
    return `<!doctype html><html lang="en"><meta charset="utf-8"><meta name="referrer" content="no-referrer">
<meta name="d01-csrf" content="${csrf}"><meta name="d01-expires" content="${value.expires}">
<title>Disposable D01 Owner TOTP</title><main id="owner-transient">
<p>NEXUS_G3_D01_DIAGNOSTIC_ONLY · AUTHORITY = NONE · REAL_ADMISSION = DISABLED</p>
<p>Transient manual authenticator enrollment. No automatic clipboard or third-party QR service.</p>
<code id="seed">${escape(value.seed)}</code><code id="recovery">${escape(value.recovery.join('\n'))}</code>
<input id="code" type="text" inputmode="numeric" maxlength="6" autocomplete="off" aria-label="Disposable TOTP code">
<button id="confirm">Confirm</button><button id="cancel">Cancel</button>
<p id="status"></p></main><script type="module" src="/owner-transient.js"></script></html>`;
  } finally { retireOwnerEnvelope(handle); }
}

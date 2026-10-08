// Unbundled offline Owner-surface preparation. Not imported by current public app.
const REASONS = new Set(['SUCCESS', 'DENY', 'TIMEOUT', 'LOGOUT', 'SWITCH', 'RELOAD', 'WORKER_LOSS', 'MISMATCH']);
const CONTEXT_KEYS = ['source', 'state', 'project_id', 'user_id', 'session_id',
  'owner_generation', 'binding_generation', 'worker_id', 'started_at', 'expires_at'];
const EXPECTED_KEYS = ['project_id', 'user_id', 'session_id', 'owner_generation', 'binding_generation', 'worker_id'];
function closed(v, keys) {
  return !!v && Object.getPrototypeOf(v) === Object.prototype && Object.keys(v).length === keys.length && keys.every(k => Object.hasOwn(v, k));
}
function output(reason = 'DISABLED') {
  return Object.freeze({ diagnostic: 'NEXUS_G3_D01_DIAGNOSTIC_ONLY', authority: 'NONE',
    qualified_live: false, real_admission: 'DISABLED', result: 'DENY',
    evidence_source: 'OFFLINE_TRANSIENT_UI_ONLY', state: reason });
}
export function createOwnerTransientView() {
  // Future route is absent. No context/body/environment is read by this constructor.
  return Object.freeze({ showEnrollment() { return output(); }, confirm() { return output(); },
    clear() { return output(); }, status() { return output(); } });
}
export function createOfflineOwnerTransientView({ context, expected, clock, document, root, events } = {}) {
  if (!closed(context, CONTEXT_KEYS) || !closed(expected, EXPECTED_KEYS)
      || context.source !== 'OFFLINE_SYNTHETIC' || context.state !== 'PRIMARY_FACTOR_VERIFIED'
      || !EXPECTED_KEYS.every(k => context[k] === expected[k])
      || !Number.isSafeInteger(context.started_at) || !Number.isSafeInteger(context.expires_at)
      || context.started_at < 0 || context.expires_at <= context.started_at
      || context.expires_at > context.started_at + 300000
      || !Number.isSafeInteger(context.owner_generation) || context.owner_generation <= 0
      || !Number.isSafeInteger(context.binding_generation) || context.binding_generation <= 0
      || !String(context.user_id).startsWith('fixture-') || typeof clock !== 'function'
      || !document || !root || !events) return createOwnerTransientView();
  const c = structuredClone(context); let retired = false; let last = c.started_at;
  let material = null; let nodes = []; let timer = null;
  const hooks = [];
  function clear(reason = 'DENY') {
    retired = true; clearTimeout(timer); timer = null;
    for (const node of nodes) { node.textContent = ''; if ('value' in node) node.value = ''; node.disabled = true; }
    nodes = []; root.replaceChildren();
    if (material) { material.secret = null; material.recovery_codes.fill(null); material = null; }
    for (const [event, handler] of hooks) events.removeEventListener(event, handler);
    hooks.length = 0; return output(REASONS.has(reason) ? reason : 'DENY');
  }
  function check() {
    const now = clock();
    if (retired || !Number.isSafeInteger(now) || now < last || now >= c.expires_at) { clear('TIMEOUT'); return false; }
    last = now; return true;
  }
  for (const event of ['beforeunload', 'pagehide', 'visibilitychange']) {
    const handler = () => clear('RELOAD'); hooks.push([event, handler]); events.addEventListener(event, handler);
  }
  const view = Object.freeze({
    showEnrollment(value) {
      if (!check()) return output('TIMEOUT');
      if (material || !closed(value, ['secret', 'recovery_codes']) || !Array.isArray(value.recovery_codes)
          || value.recovery_codes.length > 10 || ![value.secret, ...value.recovery_codes]
            .every(v => typeof v === 'string' && /^OFFLINE_[A-Z0-9_]{1,128}$/.test(v))) return clear('DENY');
      material = structuredClone(value);
      const label = document.createElement('p'); label.textContent = 'OFFLINE_TRANSIENT_UI_ONLY · AUTHORITY = NONE';
      const seed = document.createElement('code'); seed.textContent = material.secret;
      const recovery = document.createElement('code'); recovery.textContent = material.recovery_codes.join('\n');
      const input = document.createElement('input'); input.type = 'text'; input.inputMode = 'numeric';
      input.maxLength = 6; input.autocomplete = 'off'; input.setAttribute('aria-label', 'Disposable TOTP confirmation code');
      const button = document.createElement('button'); button.textContent = 'Confirm offline transition';
      button.addEventListener('click', () => view.confirm(input.value));
      nodes = [label, seed, recovery, input, button]; root.replaceChildren(...nodes);
      timer = setTimeout(() => clear('TIMEOUT'), c.expires_at - last); timer?.unref?.();
      // Manual local seed display; no QR service, URL, clipboard or evidence export.
      return output('TRANSIENT_DISPLAYED');
    },
    confirm(code) {
      if (!check() || !material || typeof code !== 'string' || !/^\d{6}$/.test(code)) return clear('DENY');
      clear('SUCCESS');
      // Authentication and post-enrollment remote recheck still must occur in a
      // protected future server protocol. This UI cannot produce positive evidence.
      return output('PROTECTED_REMOTE_RECHECK_REQUIRED');
    },
    clear,
    status() { return check() ? output(material ? 'TRANSIENT_DISPLAYED' : 'PRIMARY_FACTOR_VERIFIED') : output('RETIRED'); },
    toJSON() { return output('DISABLED'); },
  });
  return view;
}

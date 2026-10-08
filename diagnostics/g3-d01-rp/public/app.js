'use strict';
// Same-origin transport only. No analytics, console output, storage or provider SDK.
const LABEL = 'NEXUS_G3_D01_DIAGNOSTIC_ONLY';
let csrf = null;
const status = document.getElementById('status');
const result = document.getElementById('result');
function show(body) {
  csrf = typeof body.csrf === 'string' ? body.csrf : null;
  status.textContent = `${LABEL}: ${body.state ?? 'DIAGNOSTIC_DENIED'} · ${body.error_class ?? 'UNKNOWN'}`;
  // Explicit evidence projection, even if a future transport returns more fields.
  const keys = ['diagnostic', 'classification', 'authority', 'real_admission', 'qualified_live',
    'evidence_source', 'result', 'state', 'case_id', 'provider_project_alias',
    'user_id_hash_or_registered_alias', 'session_id_hash_or_registered_alias',
    'factor_types', 'factor_freshness_status', 'factor_last_authenticated_at',
    'context_generation', 'owner_generation', 'binding_generation',
    'observation_start', 'observation_end', 'context_expires_at', 'observation_point', 'error_class'];
  result.textContent = JSON.stringify(Object.fromEntries(keys.map(k => [k, body[k] ?? null])), null, 2);
}
async function request(action) {
  if (location.origin !== 'https://nexus-g3-qual.vercel.app') {
    status.textContent = `${LABEL}: DIAGNOSTIC_DENIED · ORIGIN`; return;
  }
  try {
    const response = await fetch('/api/diagnostic', action ? {
      method: 'POST', credentials: 'same-origin', redirect: 'error',
      headers: { 'Content-Type': 'application/json', 'X-G3-CSRF': csrf ?? '' },
      body: JSON.stringify({ action }),
    } : { credentials: 'same-origin', redirect: 'error', cache: 'no-store' });
    show(await response.json());
  } catch {
    csrf = null; status.textContent = `${LABEL}: DIAGNOSTIC_DENIED · UNKNOWN`;
    result.textContent = 'LIVE_DIAGNOSTIC_EVIDENCE_ONLY · AUTHORITY = NONE · REAL_ADMISSION = DISABLED';
  }
}
document.getElementById('recheck').addEventListener('click', () => request('PAGE'));
document.getElementById('logout').addEventListener('click', () => request('LOCAL_LOGOUT'));
document.getElementById('switch').addEventListener('click', () => request('ACCOUNT_SWITCH'));
request();

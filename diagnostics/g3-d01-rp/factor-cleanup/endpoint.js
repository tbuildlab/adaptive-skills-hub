if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');
import { requestGate, runProtectedCleanup, scopeDigest } from '../lib/cleanup.js';
import { configuration } from '../lib/configuration.js';
let deleteStarted = false, busy = false;
export default async function handler(req, res) {
  res.setHeader('Cache-Control', 'private, no-store'); res.setHeader('Content-Security-Policy', "default-src 'none'; frame-ancestors 'none'");
  res.setHeader('X-Content-Type-Options', 'nosniff'); res.setHeader('Referrer-Policy', 'no-referrer');
  const safe = {authority: 'NONE', real_admission: 'DISABLED', result: 'DENY', error_class: 'REQUEST'};
  let body = req.body;
  if (typeof body === 'string' || Buffer.isBuffer(body)) {res.status(400).json(safe); return;}
  if (Number(req.headers['content-length'] ?? 0) > 512) {res.status(400).json(safe); return;}
  const gate = requestGate({method: req.method, host: req.headers.host, origin: req.headers.origin,
    fetch_site: req.headers['sec-fetch-site'], content_type: req.headers['content-type'], marker: req.headers['x-nexus-cleanup'], body},
    configuration, {VERCEL_ENV: process.env.VERCEL_ENV, VERCEL_PROJECT_ID: process.env.VERCEL_PROJECT_ID, VERCEL_URL: process.env.VERCEL_URL}, Date.now());
  if (gate === 'STATUS') {
    res.status(200).json({...safe, error_class: 'PREFLIGHT_ONLY', profile: 'FIXED_EXPOSED_FACTOR_CLEANUP',
      scope_sha256: scopeDigest(configuration.scope), valid_until: configuration.valid_until,
      provider_calls: 0, delete_calls: 0, credentials_loaded: false}); return;
  }
  if (!['DELETE_EXPOSED_FACTOR','VERIFY_ABSENCE'].includes(gate) || busy || (gate === 'DELETE_EXPOSED_FACTOR' && deleteStarted)) {
    res.status(403).json({...safe, error_class: busy || deleteStarted ? 'RETIRED' : gate}); return;
  }
  busy = true; if (gate === 'DELETE_EXPOSED_FACTOR') deleteStarted = true;
  try {res.status(200).json(await runProtectedCleanup(configuration, gate));}
  catch {res.status(200).json({...safe, error_class: 'CONFIGURATION', provider_calls: 0, delete_calls: 0});}
  finally {busy = false; body = null;}
}

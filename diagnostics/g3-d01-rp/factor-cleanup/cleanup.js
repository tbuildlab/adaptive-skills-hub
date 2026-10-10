// Separate administrative cleanup; never imported by the diagnostic or Nexus runtime.
if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');
import { request as httpsRequest } from 'node:https';
import { createHash } from 'node:crypto';
const MAX_BYTES = 65536, TIMEOUT_MS = 4000;
const ID = /^(?:user|totp|project)-test-[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/;
const fail = reason => { throw new Error(reason); };
const digest = value => createHash('sha256').update(JSON.stringify(value)).digest('hex');
export function scopeDigest(scope) {
  return digest(scope);
}
function validScope(scope) {
  return scope && Object.keys(scope).sort().join(',') ===
    'application_generation,classification,exposed_totp_id,owner_user_id,project_id,source_checkpoint,vercel_project_id' &&
    scope.classification === 'OWNER_AUTHORIZED_EXPOSED_FACTOR_CLEANUP_ONLY' &&
    ID.test(scope.project_id) && scope.project_id.startsWith('project-test-') &&
    ID.test(scope.owner_user_id) && scope.owner_user_id.startsWith('user-test-') &&
    ID.test(scope.exposed_totp_id) && scope.exposed_totp_id.startsWith('totp-test-') &&
    scope.vercel_project_id === 'prj_xH23xMATVChdhX34OS2vjI8dfWN2' &&
    scope.application_generation === 3 && /^[0-9a-f]{40}$/.test(scope.source_checkpoint);
}
export function requestGate(request, config, environment, now) {
  if (!validScope(config?.scope) || config.enabled !== true) return 'DISABLED';
  if (!Number.isSafeInteger(now) || !Number.isSafeInteger(config.valid_from) ||
      !Number.isSafeInteger(config.valid_until) || config.valid_until - config.valid_from > 1800000 ||
      config.valid_until <= config.valid_from || now < config.valid_from || now >= config.valid_until) return 'EXPIRED';
  if (environment?.VERCEL_ENV !== 'production' || environment.VERCEL_PROJECT_ID !== config.scope.vercel_project_id ||
      !/^nexus-g3-qual-[a-z0-9]+-tdy0225\.vercel\.app$/.test(environment.VERCEL_URL ?? '') ||
      request?.host !== environment.VERCEL_URL || request.origin !== undefined || request.fetch_site !== undefined) return 'DEPLOYMENT';
  if (request.method === 'GET') return 'STATUS';
  if (request.method !== 'POST' || request.content_type !== 'application/json' || request.marker !== 'fixed-factor-cleanup-v1') return 'REQUEST';
  const body = request.body;
  if (!body || typeof body !== 'object' || Array.isArray(body) ||
      Object.keys(body).sort().join(',') !== 'action,scope_sha256' || body.scope_sha256 !== scopeDigest(config.scope) ||
      !['DELETE_EXPOSED_FACTOR','VERIFY_ABSENCE'].includes(body.action)) return 'REQUEST';
  return body.action;
}
// Duplicate-key and bounded-depth grammar checks precede JSON.parse.
export function parseUniqueJson(bytes) {
  if (!(bytes instanceof Uint8Array) || bytes.length > MAX_BYTES) fail('RESPONSE');
  const text = new TextDecoder('utf-8', {fatal: true}).decode(bytes); let at = 0, nodes = 0;
  const space = () => { while (/\s/.test(text[at] ?? '!')) at++; };
  const string = () => {
    const regex = /"(?:[^"\\\x00-\x1f]|\\(?:["\\/bfnrt]|u[0-9a-fA-F]{4}))*"/y;
    regex.lastIndex = at; const found = regex.exec(text); if (!found) fail('RESPONSE');
    at = regex.lastIndex; return JSON.parse(found[0]);
  };
  const value = depth => {
    if (depth > 24 || ++nodes > 8192) fail('RESPONSE'); space(); const first = text[at];
    if (first === '"') { string(); return; }
    if (first === '{' || first === '[') {
      const object = first === '{', end = object ? '}' : ']', keys = new Set(); at++; space();
      if (text[at] === end) {at++; return;}
      for (;;) {
        if (object) {const key = string(); if (keys.has(key)) fail('RESPONSE'); keys.add(key); space(); if (text[at++] !== ':') fail('RESPONSE');}
        value(depth + 1); space(); if (text[at] === end) {at++; return;}
        if (text[at++] !== ',') fail('RESPONSE'); space();
      }
    }
    const regex = /(?:true|false|null|-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?)/y;
    regex.lastIndex = at; if (!regex.exec(text)) fail('RESPONSE'); at = regex.lastIndex;
  };
  value(0); space(); if (at !== text.length) fail('RESPONSE'); return JSON.parse(text);
}
function projectUser(body, scope, nested = false) {
  if (!body || body.status_code !== 200 || body.user_id !== scope.owner_user_id) fail('OWNER_MISMATCH');
  const user = nested ? body.user : body;
  if (!user || user.user_id !== scope.owner_user_id || !Array.isArray(user.totps) || user.totps.length > 32) fail('OWNER_MISMATCH');
  const ids = user.totps.map(factor => {
    if (!factor || !ID.test(factor.totp_id) || !factor.totp_id.startsWith('totp-test-') || typeof factor.verified !== 'boolean') fail('FACTOR_METADATA');
    return factor.totp_id;
  });
  if (new Set(ids).size !== ids.length) fail('FACTOR_METADATA');
  return ids.sort();
}
function nativeExchange(scope, credentials, method) {
  const path = method === 'GET' ? '/v1/users/' + scope.owner_user_id : '/v1/users/totps/' + scope.exposed_totp_id;
  if (!['GET','DELETE'].includes(method)) fail('METHOD');
  return new Promise((resolve, reject) => {
    let request, settled = false, timer;
    const finish = (error, value) => { if (settled) return; settled = true; clearTimeout(timer); if (error) {request?.destroy(); reject(new Error('PROVIDER_UNKNOWN'));} else resolve(value); };
    timer = setTimeout(() => finish(true), TIMEOUT_MS);
    try {
      request = httpsRequest({protocol: 'https:', hostname: 'test.stytch.com', port: 443, servername: 'test.stytch.com', rejectUnauthorized: true,
        method, path, agent: false, headers: {'Content-Type': 'application/json', Accept: 'application/json',
          Authorization: 'Basic ' + Buffer.from(credentials.project + ':' + credentials.secret).toString('base64')}}, response => {
        const headers = response.headers, length = headers['content-length'];
        if (response.statusCode !== 200 || !/^application\/json(?:;\s*charset=utf-8)?$/i.test(headers['content-type'] ?? '') ||
            (headers['content-encoding'] !== undefined && headers['content-encoding'] !== 'identity') ||
            (length !== undefined && (!/^\d{1,10}$/.test(String(length)) || Number(length) > MAX_BYTES))) {response.destroy(); finish(true); return;}
        let count = 0; const chunks = [];
        response.on('data', chunk => {count += chunk.length; if (count > MAX_BYTES) {response.destroy(); finish(true);} else chunks.push(chunk);});
        response.on('error', () => finish(true)); response.on('aborted', () => finish(true));
        response.on('end', () => {
          try {if (length !== undefined && count !== Number(length)) fail('RESPONSE'); const bytes = Buffer.concat(chunks);
            const body = parseUniqueJson(bytes); bytes.fill(0); for (const chunk of chunks) chunk.fill(0); finish(null, body);
          } catch {finish(true);}
        });
      });
      request.on('error', () => finish(true)); request.end();
    } catch {finish(true);}
  });
}
const offlineHandles = new WeakMap();
export function createOfflineCleanup(config, replies, clock = Date.now) {
  if (!validScope(config?.scope) || !Array.isArray(replies) || replies.length > 4) fail('OFFLINE_CONFIG');
  const handle = Object.freeze({kind: 'OFFLINE_FACTOR_CLEANUP', authority: 'NONE'});
  offlineHandles.set(handle, {queue: structuredClone(replies), shapes: [], config: structuredClone(config), clock}); return handle;
}
export function offlineShapes(handle) {return structuredClone(offlineHandles.get(handle)?.shapes ?? []);}
export function runOfflineCleanup(handle, action) {
  const fixture = offlineHandles.get(handle); if (!fixture) fail('OFFLINE_ONLY');
  return execute(fixture.config, action, async method => {
    fixture.shapes.push({method, route: method === 'GET' ? 'FIXED_OWNER_USER' : 'FIXED_EXPOSED_FACTOR'});
    const reply = fixture.queue.shift(); if (!reply || reply.failure) fail('PROVIDER_UNKNOWN'); return reply.body;
  }, fixture.clock);
}
export async function runProtectedCleanup(config, action, environment = process.env) {
  // Never accepts an offline handle, exchange callback, URL, user ID or factor ID.
  if (!validScope(config?.scope) || config.enabled !== true || Object.hasOwn(config, 'kind')) fail('DISABLED');
  if (requestGate({method: 'POST', host: environment.VERCEL_URL, content_type: 'application/json', marker: 'fixed-factor-cleanup-v1',
    body: {action, scope_sha256: scopeDigest(config.scope)}}, config, environment, Date.now()) !== action) fail('DEPLOYMENT');
  const project = environment.STYTCH_PROJECT_ID; if (project !== config.scope.project_id) fail('PROJECT_CONFIG');
  let secret = environment.STYTCH_SECRET;
  if (typeof secret !== 'string' || secret.length > 268 || !/^secret-test-[A-Za-z0-9_-]{16,256}={0,2}$/.test(secret)) fail('SECRET_CONFIG');
  const credentials = {project, secret}; secret = null;
  try {return await execute(config, action, method => nativeExchange(config.scope, credentials, method), Date.now);}
  finally {credentials.secret = null;}
}
async function execute(config, action, exchange, clock) {
  const result = {authority: 'NONE', real_admission: 'DISABLED', result: 'DENY', error_class: 'UNKNOWN',
    user_preserved: false, factor_absent: false, other_factors_preserved: false,
    delete_acknowledged: false, provider_calls: 0, delete_calls: 0};
  const current = () => {const now = clock(); if (config.enabled !== true || !Number.isSafeInteger(now) || now < config.valid_from || now >= config.valid_until) fail('EXPIRED');};
  const call = async method => {current(); result.provider_calls++; if (method === 'DELETE') result.delete_calls++; return exchange(method);};
  try {
    if (!['DELETE_EXPOSED_FACTOR','VERIFY_ABSENCE'].includes(action)) fail('REQUEST');
    const before = projectUser(await call('GET'), config.scope); result.user_preserved = true;
    if (!before.includes(config.scope.exposed_totp_id)) {
      result.factor_absent = true; result.other_factors_preserved = true; result.result = 'PASS'; result.error_class = 'ALREADY_ABSENT'; return result;
    }
    if (action === 'VERIFY_ABSENCE') {result.error_class = 'FACTOR_PRESENT'; return result;}
    const expected = before.filter(id => id !== config.scope.exposed_totp_id); let ackError = null;
    try {
      const ack = projectUser(await call('DELETE'), config.scope, true);
      if (JSON.stringify(ack) !== JSON.stringify(expected)) fail('DELETE_RESPONSE_MISMATCH'); result.delete_acknowledged = true;
    } catch (error) {ackError = ['OWNER_MISMATCH','FACTOR_METADATA','DELETE_RESPONSE_MISMATCH','EXPIRED'].includes(error.message) ? error.message : 'DELETE_ACK_UNKNOWN';}
    // A single independent read, including after unknown acknowledgment. Never retry DELETE.
    const after = projectUser(await call('GET'), config.scope); result.user_preserved = true;
    result.factor_absent = !after.includes(config.scope.exposed_totp_id);
    result.other_factors_preserved = JSON.stringify(after) === JSON.stringify(expected);
    if (!result.factor_absent || !result.other_factors_preserved) fail('POSTCONDITION');
    if (ackError) {result.error_class = ackError; return result;}
    result.result = 'PASS'; result.error_class = 'NONE'; return result;
  } catch (error) {
    const allowed = ['OWNER_MISMATCH','FACTOR_METADATA','EXPIRED','REQUEST','POSTCONDITION'];
    result.error_class = allowed.includes(error.message) ? error.message : 'PROVIDER_UNKNOWN'; return result;
  }
}

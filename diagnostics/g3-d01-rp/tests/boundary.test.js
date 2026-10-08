import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import vm from 'node:vm';

const root = fileURLToPath(new URL('../', import.meta.url));
function read(p) { return readFileSync(path.join(root, p), 'utf8'); }
function files(dir) {
  return readdirSync(path.join(root, dir), { withFileTypes: true }).flatMap(e =>
    e.isDirectory() ? files(`${dir}/${e.name}`) : [`${dir}/${e.name}`]);
}
test('deployed route graph has no live network, credential access, authority imports or model success seam', () => {
  const source = ['api/diagnostic.js', 'lib/http.js', 'lib/policy.js', 'lib/adapter.js'].map(read).join('\n');
  assert.equal(read('api/diagnostic.js').includes('model.js'), false);
  assert.equal(read('lib/http.js').includes('model.js'), false);
  for (const expression of [/\bprocess\s*\.\s*env\b/, /\bfetch\s*\(/,
    /\bconsole\s*\./, /\b(?:https?|net|tls|child_process)\b(?=['"])/,
    /\b(?:TrustedDecisionReceipt|ApprovalGrant|AdmissionIntent|DispatchAttempt)\b/,
    /from\s*['"][^'"]*(?:ash|model\.js)[^'"]*['"]/, /\beval\s*\(/]) {
    assert.equal(expression.test(source.replace(/\/\/[^\n]*/g, '')), false, String(expression));
  }
  assert.deepEqual(files('api'), ['api/diagnostic.js']);
});
test('dependency-free deploy config isolates static output and API; no env or SDK bundling', () => {
  const pkg = JSON.parse(read('package.json')); const config = JSON.parse(read('vercel.json'));
  assert.deepEqual(pkg.dependencies, {}); assert.equal(pkg.engines.node, '24.x');
  assert.equal(pkg.type, 'module'); assert.equal(config.framework, null);
  assert.equal(config.outputDirectory, 'public'); assert.equal(config.env, undefined);
  assert.deepEqual(Object.keys(config.functions), ['api/diagnostic.js']);
  assert.equal(config.redirects, undefined); assert.equal(config.rewrites, undefined);
  assert.equal(read('public/index.html').includes('https://'), false);
  assert.equal(read('public/app.js').includes('localStorage'), false);
});
test('static pages explicitly label diagnostic/no authority, disabled credentials and no third-party scripts', () => {
  const html = read('public/index.html');
  for (const word of ['NEXUS_G3_D01_DIAGNOSTIC_ONLY', 'LIVE_DIAGNOSTIC_EVIDENCE_ONLY',
    'AUTHORITY = NONE', 'REAL_ADMISSION = DISABLED', '<fieldset disabled>',
    'TOTP enrollment', 'UNVERIFIED']) assert.equal(html.includes(word), true, word);
  assert.deepEqual([...html.matchAll(/<script[^>]+src="([^"]+)"/g)].map(m => m[1]), ['/app.js']);
  assert.equal(/<form|type="submit"|<iframe|<img/i.test(html), false);
});
test('client projection never displays transport CSRF/extra secrets; same-origin requests only', async () => {
  const elements = new Map(['status', 'result', 'recheck', 'logout', 'switch'].map(k =>
    [k, { textContent: '', callbacks: {}, addEventListener(e, f) { this.callbacks[e] = f; } }]));
  const transport = { diagnostic: 'NEXUS_G3_D01_DIAGNOSTIC_ONLY', state: 'SIGNED_OUT',
    error_class: 'LIVE_DISABLED', csrf: 'SYNTHETIC_CSRF_SENTINEL', session_token: 'SYNTHETIC_SECRET_SENTINEL' };
  const calls = [];
  const context = vm.createContext({ document: { getElementById(k) { return elements.get(k); } },
    location: { origin: 'https://nexus-g3-qual.vercel.app' },
    fetch: async (url, options) => { calls.push({ url, options }); return { json: async () => transport }; } });
  vm.runInContext(read('public/app.js'), context);
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(calls[0].url, '/api/diagnostic');
  assert.equal(calls[0].options.redirect, 'error');
  assert.equal(elements.get('result').textContent.includes('SENTINEL'), false);
  await elements.get('recheck').callbacks.click();
  assert.equal(calls[1].options.headers['X-G3-CSRF'], transport.csrf);
  assert.deepEqual(JSON.parse(calls[1].options.body), { action: 'PAGE' });
});
test('client hostile origin never invokes even the same-origin endpoint', async () => {
  let calls = 0;
  const element = { textContent: '', addEventListener() {} };
  const context = vm.createContext({ document: { getElementById() { return element; } },
    location: { origin: 'http://localhost:3000' }, fetch() { ++calls; } });
  vm.runInContext(read('public/app.js'), context);
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(calls, 0); assert.match(element.textContent, /DIAGNOSTIC_DENIED · ORIGIN/);
});

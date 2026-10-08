if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');
import { randomBytes, timingSafeEqual } from 'node:crypto';
import { makeHandler } from '../http.js';
import { ORIGIN, POINTS, closed, stamp } from '../policy.js';
import { DEPLOYMENT } from './deployment-input.js';
import { liveSelectionAllowed, safeResult, safeError, ClosedFailure } from './pre-secret-policy.js';
import { validateReviewedRegistration, registrationRecord } from './provider-registration.js';
import { createProtectedStytchTransport, createOfflineStytchTransport } from './stytch-transport.js';
import { pinnedKeys } from './pinned-identity.js';
const COOKIE = '__Host-g3d01'; const nonce = () => randomBytes(32).toString('hex');
const COMMON = Object.freeze({ 'Cache-Control': 'no-store', 'Referrer-Policy': 'no-referrer',
  'X-Frame-Options': 'DENY', 'X-Content-Type-Options': 'nosniff',
  'Content-Security-Policy': "default-src 'none'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'" });
function equal(a, b) { return typeof a === 'string' && /^[a-f0-9]{64}$/.test(a) && typeof b === 'string'
  && /^[a-f0-9]{64}$/.test(b) && timingSafeEqual(Buffer.from(a), Buffer.from(b)); }
function cookie(value) {
  if (value === undefined) return null;
  if (typeof value !== 'string' || value.length > 2048) throw new ClosedFailure('REQUEST');
  const matches = value.split(';').map(s => s.trim()).filter(s => s.startsWith(COOKIE+'='));
  if (matches.length > 1 || (matches.length && !/^[a-f0-9]{64}$/.test(matches[0].slice(COOKIE.length+1)))) throw new ClosedFailure('REQUEST');
  return matches.length ? matches[0].slice(COOKIE.length+1) : null;
}
export function createDiagnosticHandler() {
  if (!liveSelectionAllowed(DEPLOYMENT, DEPLOYMENT.provider)) return makeHandler();
  if (!validateReviewedRegistration(DEPLOYMENT.provider) || !pinnedKeys(DEPLOYMENT.keyset, DEPLOYMENT.provider, Date.now())) return makeHandler();
  return buildHandler(() => createProtectedStytchTransport(DEPLOYMENT, DEPLOYMENT.provider), Date.now, false);
}
export function createOfflineDiagnosticHandler(input) {
  let r;
  try {
    r = registrationRecord(input?.registration);
    if (!r || r.source !== 'OFFLINE_SYNTHETIC' || typeof input.clock !== 'function'
        || !pinnedKeys(input.keyset, r, input.clock())) return makeHandler();
  } catch { return makeHandler(); }
  // Only the fixture factory can supply in-memory IO; production factory never
  // imports input, browser config, mode selectors or fake factory output.
  return buildHandler(() => createOfflineStytchTransport({ ...input, ownerChannel: true,
    publicKeys: pinnedKeys(input.keyset, r, input.clock()) }), input.clock, true);
}
function buildHandler(factory, clock, fixture) {
  const pages = new Map(); let high = null;
  const retire = key => { const p = pages.get(key); clearTimeout(p?.timer); p?.backend?.retire(); pages.delete(key); };
  const schedule = (key, page, now) => {
    clearTimeout(page.timer);
    page.timer = setTimeout(() => retire(key), Math.max(0, page.expires-now));
    page.timer.unref?.();
  };
  return async (req, res) => {
    let key = null; let page = null;
    const reply = (status, result, csrf = null) => {
      for (const [k,v] of Object.entries(COMMON)) res.setHeader(k,v);
      res.setHeader('Content-Type','application/json; charset=utf-8'); res.statusCode=status;
      res.end(JSON.stringify({ ...result, csrf, adapter_mode: fixture ? 'OFFLINE_SERVICE_ONLY' : 'D01_DIAGNOSTIC_LIVE_STYTCH',
        live_diagnostic_enabled: !fixture, context_expires_at: page?.expires ?? null }));
    };
    try {
      const h = req.headers ?? {};
      if (h.host !== new URL(ORIGIN).host || (h.origin !== undefined && h.origin !== ORIGIN)
          || ['cross-site','same-site'].includes(h['sec-fetch-site'])) throw new ClosedFailure('REQUEST');
      if (req.url !== '/api/diagnostic' || !['GET','POST'].includes(req.method)) throw new ClosedFailure('REQUEST');
      const now=clock();
      if (!stamp(now) || (high !== null && now < high)) { for (const k of pages.keys()) retire(k); throw new ClosedFailure('EXPIRED'); }
      high=now; for (const [k,p] of pages) if (now >= p.expires) retire(k);
      key=cookie(h.cookie); page=key ? pages.get(key) : null;
      if (key && !page) throw new ClosedFailure('RETIRED');
      if (req.method === 'GET') {
        if (!page) {
          if (h['x-d01-view'] !== undefined || pages.size >= 128) throw new ClosedFailure('REQUEST');
          key=nonce(); page={ csrf: nonce(), expires: now+300000, backend: null, point: 0, terminal: false }; pages.set(key,page);
          schedule(key,page,now);
          res.setHeader('Set-Cookie',`${COOKIE}=${key}; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=300`);
        }
        if (h['x-d01-view'] !== undefined) {
          if (h['x-d01-view'] !== 'OWNER_TOTP' || h.origin !== ORIGIN || !equal(h['x-g3-csrf'],page.csrf)
              || !page.backend?.contextInfo().primary || page.terminal) throw new ClosedFailure('RETIRED');
          const html=await page.backend.ownerTransientHtml(page.csrf);
          if (clock() >= page.expires || pages.get(key)!==page) throw new ClosedFailure('EXPIRED');
          for (const [k,v] of Object.entries(COMMON)) res.setHeader(k,v);
          res.setHeader('Content-Type','text/html; charset=utf-8'); res.statusCode=200; res.end(html); return;
        }
        if (page.backend?.contextInfo().retired) throw new ClosedFailure('RETIRED');
        return reply(200,safeResult('NONE',false,fixture),page.csrf);
      }
      if (h['content-type']==='application/x-www-form-urlencoded') {
        if (!page || h.origin!==ORIGIN || !page.backend?.contextInfo().primary || page.terminal) throw new ClosedFailure('RETIRED');
        let form=req.body;
        if(typeof form==='string') {
          if(Buffer.byteLength(form)>1024) throw new ClosedFailure('REQUEST');
          const entries=[...new URLSearchParams(form)];
          if(entries.length!==2 || new Set(entries.map(([k])=>k)).size!==2) throw new ClosedFailure('REQUEST');
          form=Object.fromEntries(entries);
        }
        if(!closed(form,['action','csrf'])||form.action!=='OWNER_TOTP_DISPLAY'||!equal(form.csrf,page.csrf)) throw new ClosedFailure('REQUEST');
        const html=await page.backend.ownerTransientHtml(page.csrf);
        if(clock()>=page.expires||pages.get(key)!==page) throw new ClosedFailure('EXPIRED');
        for(const [k,v] of Object.entries(COMMON)) res.setHeader(k,v);
        res.setHeader('Content-Type','text/html; charset=utf-8');res.statusCode=200;res.end(html);return;
      }
      if (!page || h.origin!==ORIGIN || !equal(h['x-g3-csrf'],page.csrf) || h['content-type']!=='application/json'
          || Buffer.byteLength(JSON.stringify(req.body ?? {}))>4096) throw new ClosedFailure('REQUEST');
      const body=req.body;
      if (!body || !closed(body, ['action', ...(Object.hasOwn(body,'code') ? ['code'] : [])])) throw new ClosedFailure('REQUEST');
      const action=body.action;
      if (['LOCAL_LOGOUT','ACCOUNT_SWITCH','CANCEL'].includes(action)) { retire(key); page=null;
        res.setHeader('Set-Cookie',`${COOKIE}=; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=0`); return reply(200,safeResult('RETIRED',false,fixture)); }
      if (page.terminal && action!=='SESSION_REVOKE_EXACT') throw new ClosedFailure('RETIRED');
      const codes=['EMAIL_OTP_AUTHENTICATE','TOTP_AUTHENTICATE'];
      if (Object.hasOwn(body,'code') !== codes.includes(action)) throw new ClosedFailure('REQUEST');
      if (!page.backend) {
        if (action!=='EMAIL_OTP_SEND') throw new ClosedFailure('REQUEST'); page.backend=factory();
        if (page.backend.mode==='FAKE_DISABLED') throw new ClosedFailure('DISABLED');
      }
      let result;
      if (POINTS.includes(action)) {
        if (action!==POINTS[page.point]) throw new ClosedFailure('REQUEST');
        result=await page.backend.SESSION_AUTHENTICATE();
        if (result.result==='PASS') { page.point++; if(page.point===POINTS.length) page.terminal=true; }
      } else if (['EMAIL_OTP_SEND','EMAIL_OTP_AUTHENTICATE','TOTP_CREATE','TOTP_AUTHENTICATE','SESSION_REVOKE_EXACT'].includes(action)) {
        result=await page.backend[action](codes.includes(action)?{code:body.code}:undefined);
      } else throw new ClosedFailure('REQUEST');
      const info=page.backend.contextInfo();
      if (action==='SESSION_REVOKE_EXACT' && result.result==='PASS') { retire(key); page=null; return reply(200,result); }
      if (info.expires_at!==null) {
        const previous=page.expires;page.expires=Math.min(page.expires,info.expires_at);
        if(page.expires<previous)schedule(key,page,clock());
      }
      if (result.result!=='PASS' || now>=page.expires || clock()>=page.expires || pages.get(key)!==page) {
        retire(key); page=null; return reply(403,safeResult('RETIRED',false,fixture));
      }
      reply(200,result,page.csrf);
    } catch (error) { if(key) retire(key); page=null; reply(403,safeResult(safeError(error),false,fixture)); }
  };
}

// Private one-use Owner channel. Same-origin vendored encoder; no remote QR service.
import { qrcodegen } from './qrcodegen.js';

export function paintOwnerQr(seed, canvas) {
  if(typeof seed!=='string'||!/^[A-Z2-7]{16,128}$/.test(seed)) throw new Error('QR_INPUT');
  let uri=null, qr=null, segments=null;
  try {
    const issuer='Nexus G3';
    const parameters=new URLSearchParams({secret:seed,issuer,algorithm:'SHA1',digits:'6',period:'30'});
    uri='otpauth://totp/'+encodeURIComponent(issuer+':D01 disposable Owner')+'?'+parameters.toString();
    parameters.delete('secret');
    segments=qrcodegen.QrSegment.makeSegments(uri);
    qr=qrcodegen.QrCode.encodeSegments(segments,qrcodegen.QrCode.Ecc.MEDIUM,1,15,-1,false);
    const border=4, scale=5, size=(qr.size+border*2)*scale;
    if(size>512) throw new Error('QR_SIZE');
    canvas.width=canvas.height=size;
    const ctx=canvas.getContext('2d');
    if(!ctx) throw new Error('QR_CANVAS');
    ctx.fillStyle='#ffffff';ctx.fillRect(0,0,size,size);ctx.fillStyle='#000000';
    for(let y=0;y<qr.size;y++)for(let x=0;x<qr.size;x++)
      if(qr.getModule(x,y))ctx.fillRect((x+border)*scale,(y+border)*scale,scale,scale);
  } finally {
    seed=null;uri=null;
    // Best-effort reference/buffer clearing; JavaScript does not guarantee heap erasure.
    for(const row of qr?.modules??[])row.fill(false);
    for(const segment of segments??[])segment.bitData?.fill(0);
    qr=null;segments=null;
  }
}

const root=document.getElementById('owner-transient');
const canvas=document.getElementById('totp-qr');
const origin='https://nexus-g3-qual.vercel.app';
let csrf=document.querySelector('meta[name="d01-csrf"]')?.content;
const deadline=Number(document.querySelector('meta[name="d01-expires"]')?.content);
let done=false, ready=false;
const safeClasses=new Set(['NONE','DISABLED','REQUEST','REGISTRATION','CREDENTIAL','RETIRED',
  'AUTH_REJECTED','SESSION_INVALID','RATE_LIMITED','PROVIDER_UNAVAILABLE','TIMEOUT',
  'MALFORMED_RESPONSE','UNKNOWN','IDENTITY','FACTORS','EXPIRED']);
function showResult(value,ok,action) {
  let result='DENY', error='MALFORMED_RESPONSE', expires=null;
  if(value && value.diagnostic==='NEXUS_G3_D01_DIAGNOSTIC_ONLY' && value.authority==='NONE'
      && value.real_admission==='DISABLED' && value.qualified_live===false
      && value.adapter_mode==='D01_DIAGNOSTIC_LIVE_STYTCH' && value.live_diagnostic_enabled===true
      && ['PASS','DENY'].includes(value.result) && safeClasses.has(value.error_class)) {
    if(value.result==='DENY')error=value.error_class==='NONE'?'UNKNOWN':value.error_class;
    else if(ok && action==='TOTP_AUTHENTICATE' && value.error_class==='NONE'
        && Number.isSafeInteger(value.context_expires_at) && value.context_expires_at<=deadline
        && Date.now()<value.context_expires_at) {
      result='PASS';error='NONE';expires=value.context_expires_at;
    } else error='RETIRED';
  }
  const evidence={diagnostic:'NEXUS_G3_D01_DIAGNOSTIC_ONLY',authority:'NONE',
    real_admission:'DISABLED',qualified_live:false,result,error_class:error,
    context_expires_at:expires,evidence_source:'SANITIZED_TOTP_RESPONSE',
    operation:action==='TOTP_AUTHENTICATE'?'TOTP_AUTHENTICATE':'CANCEL'};
  if(root) {
    const pre=document.createElement('pre');pre.id='evidence';pre.textContent=JSON.stringify(evidence,null,2);
    const link=document.createElement('a');link.href='/';link.textContent='Return to diagnostics';
    root.replaceChildren(pre,link);
  }
}
function clear() {
  done=true;ready=false;csrf=null;
  if(canvas){canvas.getContext('2d')?.clearRect(0,0,canvas.width,canvas.height);canvas.width=canvas.height=0;}
  for(const node of root?.querySelectorAll('input')??[])node.value='';
  root?.replaceChildren();
  for(const node of document.querySelectorAll('meta[name="d01-csrf"], meta[name="d01-expires"]'))node.remove();
}
async function send(action,code,keepalive=false) {
  if(done||location.origin!==origin||!Number.isSafeInteger(deadline)||Date.now()>=deadline){clear();return;}
  const token=csrf;clear();
  try {
    const res=await fetch('/api/diagnostic',{method:'POST',credentials:'same-origin',redirect:'error',keepalive,
      headers:{'Content-Type':'application/json','X-G3-CSRF':token},body:JSON.stringify({action,...(code?{code}:{})})});
    if(keepalive){await res.body?.cancel();return;}
    // Read only the same-origin diagnostic response. Never render raw response fields.
    let value=await res.json();showResult(value,res.ok,action);value=null;
  } catch { if(!keepalive)showResult(null,false,action); }
}
function abandon(){if(!done)void send('CANCEL',undefined,true);else clear();}
document.getElementById('confirm')?.addEventListener('click',()=>{
  const code=document.getElementById('code')?.value;
  if(!ready||!/^\d{6}$/.test(code)){void send('CANCEL');return;}void send('TOTP_AUTHENTICATE',code);
});
document.getElementById('cancel')?.addEventListener('click',()=>void send('CANCEL'));
for(const event of ['beforeunload','pagehide'])window.addEventListener(event,abandon);
window.addEventListener('visibilitychange',()=>{if(document.visibilityState!=='visible')abandon();});
setTimeout(abandon,Math.max(0,deadline-Date.now()));
try {
  if(location.origin!==origin||!Number.isSafeInteger(deadline)||Date.now()>=deadline
      ||typeof csrf!=='string'||!/^[a-f0-9]{64}$/.test(csrf)||!root||!canvas)throw new Error('QR_CONTEXT');
  const seedNode=document.getElementById('seed');
  try { paintOwnerQr(seedNode?.textContent,canvas);ready=true; }
  finally { if(seedNode){seedNode.textContent='';seedNode.remove();} }
} catch { abandon(); }

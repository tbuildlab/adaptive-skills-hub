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
    await res.body?.cancel();if(!keepalive)location.replace('/');
  } catch { if(!keepalive&&root)root.textContent='DENY / UNKNOWN — local material retired'; }
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

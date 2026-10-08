// Runs only inside the one-use protected Owner HTML channel; no evidence export.
const root=document.getElementById('owner-transient');
const origin='https://nexus-g3-qual.vercel.app';
let csrf=document.querySelector('meta[name="d01-csrf"]').content;
const deadline=Number(document.querySelector('meta[name="d01-expires"]').content);
let done=false;
function clear() {
  done=true;csrf=null;
  for(const node of root.querySelectorAll('input'))node.value='';
  root.replaceChildren();
  for(const node of document.querySelectorAll('meta[name="d01-csrf"], meta[name="d01-expires"]'))node.remove();
}
async function send(action,code) {
  if(done||location.origin!==origin||!Number.isSafeInteger(deadline)||Date.now()>=deadline){clear();return;}
  const token=csrf; clear();
  try { const res=await fetch('/api/diagnostic',{method:'POST',credentials:'same-origin',redirect:'error',
    headers:{'Content-Type':'application/json','X-G3-CSRF':token},body:JSON.stringify({action,...(code?{code}:{})})});
    await res.body?.cancel();location.replace('/');
  } catch { root.textContent='DENY / UNKNOWN — local material retired'; }
}
document.getElementById('confirm').addEventListener('click',()=>{
  const code=document.getElementById('code').value;
  if(!/^\d{6}$/.test(code)){send('CANCEL');return;}send('TOTP_AUTHENTICATE',code);
});
document.getElementById('cancel').addEventListener('click',()=>send('CANCEL'));
for(const event of ['beforeunload','pagehide','visibilitychange'])window.addEventListener(event,clear);
setTimeout(clear,Math.max(0,deadline-Date.now()));

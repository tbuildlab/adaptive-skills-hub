// No registration/mode/key input, provider SDK, storage or credentials.
let csrf=null;
const origin='https://nexus-g3-qual.vercel.app';
const status=document.getElementById('status'), evidence=document.getElementById('evidence');
const controls=document.getElementById('operations');
async function call(action) {
  if(location.origin!==origin) { controls.disabled=true; return; }
  const code=document.getElementById('email-code');
  const body=action ? {action, ...(action==='EMAIL_OTP_AUTHENTICATE'?{code:code.value}:{})} : null;
  if(code) code.value='';
  try {
    const res=await fetch('/api/diagnostic',body?{method:'POST',redirect:'error',credentials:'same-origin',
      headers:{'Content-Type':'application/json','X-G3-CSRF':csrf??''},body:JSON.stringify(body)}:{redirect:'error',credentials:'same-origin',cache:'no-store'});
    const value=await res.json();csrf=typeof value.csrf==='string'?value.csrf:null;
    controls.disabled=value.live_diagnostic_enabled!==true||value.adapter_mode!=='D01_DIAGNOSTIC_LIVE_STYTCH';
    status.textContent=controls.disabled?'FAKE_DISABLED':'Disposable diagnostic only — authority NONE';
    evidence.textContent=JSON.stringify(Object.fromEntries(['diagnostic','authority','real_admission','qualified_live','result','error_class','evidence_source','context_expires_at'].map(k=>[k,value[k]??null])),null,2);
  } catch { csrf=null; controls.disabled=true; evidence.textContent='DENY / UNKNOWN'; }
}
for(const button of document.querySelectorAll('[data-action]')) button.addEventListener('click',()=>call(button.dataset.action));
document.getElementById('show-owner').addEventListener('click',()=>{
  if(controls.disabled||location.origin!==origin) return;
  const form=document.createElement('form');form.method='POST';form.action='/api/diagnostic';form.hidden=true;
  for(const [name,value] of [['action','OWNER_TOTP_DISPLAY'],['csrf',csrf??'']]) {
    const input=document.createElement('input');input.type='hidden';input.name=name;input.value=value;form.append(input);
  }
  document.body.append(form);form.submit();
});
call();

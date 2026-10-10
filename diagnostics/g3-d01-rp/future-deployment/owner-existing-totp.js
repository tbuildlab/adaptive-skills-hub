// Fixed same-origin diagnostic actions. No enrollment material or provider SDK.
let csrf=null, busy=false, deadline=null, high=Date.now();
const origin='https://nexus-g3-qual.vercel.app';
const status=document.getElementById('status'), evidence=document.getElementById('evidence');
const controls=document.getElementById('operations');
const codes={EMAIL_OTP_AUTHENTICATE:document.getElementById('email-code'),
  TOTP_AUTHENTICATE:document.getElementById('totp-code')};
const classes=new Set(['NONE','DISABLED','REQUEST','REGISTRATION','CREDENTIAL','RETIRED',
  'AUTH_REJECTED','SESSION_INVALID','RATE_LIMITED','PROVIDER_UNAVAILABLE','TIMEOUT',
  'MALFORMED_RESPONSE','UNKNOWN','IDENTITY','FACTORS','EXPIRED',
  'REQUEST_ORIGIN','REQUEST_BUSY','REQUEST_FORM_SCHEMA','REQUEST_FORM_SIZE','REQUEST_FORM_CSRF']);
function clearCodes(){for(const node of Object.values(codes))if(node)node.value='';}
function fresh(){const now=Date.now();if(high!==null&&now<high)return false;high=now;
  return Number.isSafeInteger(deadline)&&now<deadline;}
function display(value,ok){
  let result='DENY',error='MALFORMED_RESPONSE',expires=null;
  const now=Date.now(), clockValid=Number.isSafeInteger(now)&&now>=high;
  if(clockValid)high=now;
  const valid=value&&value.diagnostic==='NEXUS_G3_D01_DIAGNOSTIC_ONLY'&&value.authority==='NONE'
    &&value.real_admission==='DISABLED'&&value.qualified_live===false
    &&value.adapter_mode==='D01_DIAGNOSTIC_LIVE_STYTCH'&&value.live_diagnostic_enabled===true
    &&['PASS','DENY'].includes(value.result)&&classes.has(value.error_class);
  csrf=null;controls.disabled=true;
  if(valid){
    const exp=value.context_expires_at;
    if(value.result==='DENY'&&value.error_class!=='NONE')error=value.error_class;
    else if(ok&&clockValid&&Number.isSafeInteger(exp)&&(deadline===null||exp<=deadline)&&now<exp
      &&exp-now<=300000&&/^[a-f0-9]{64}$/.test(value.csrf??'')){
      deadline=exp;csrf=value.csrf;controls.disabled=false;result=value.result;error=value.error_class;expires=exp;
      setTimeout(()=>{if(!fresh()){clearCodes();csrf=null;controls.disabled=true;}},Math.max(0,exp-now));
    }else error='RETIRED';
  }
  status.textContent=controls.disabled?'Diagnostic retired or disabled':'Disposable diagnostic only — authority NONE';
  evidence.textContent=JSON.stringify({diagnostic:'NEXUS_G3_D01_DIAGNOSTIC_ONLY',authority:'NONE',
    real_admission:'DISABLED',qualified_live:false,result,error_class:error,
    evidence_source:'SANITIZED_DIAGNOSTIC_RESPONSE',context_expires_at:expires},null,2);
}
async function call(action){
  if(busy)return;
  if(location.origin!==origin||(action&&!fresh())){clearCodes();csrf=null;controls.disabled=true;return;}
  const body=action?{action,...(Object.hasOwn(codes,action)?{code:codes[action]?.value}:{})}:null;
  clearCodes();
  if(body&&Object.hasOwn(codes,action)&&!/^\d{6}$/.test(body.code??'')){
    evidence.textContent=JSON.stringify({authority:'NONE',real_admission:'DISABLED',result:'DENY',error_class:'REQUEST_CODE_SHAPE'});return;
  }
  busy=true;controls.disabled=true;
  try{
    const res=await fetch('/api/diagnostic',body?{method:'POST',redirect:'error',credentials:'same-origin',
      headers:{'Content-Type':'application/json','X-G3-CSRF':csrf??''},body:JSON.stringify(body)}
      :{redirect:'error',credentials:'same-origin',cache:'no-store'});
    if(body?.code)body.code=null;
    let value=await res.json();display(value,res.ok);value=null;
  }catch{display(null,false);}
  finally{if(body?.code)body.code=null;busy=false;}
}
for(const button of document.querySelectorAll('[data-action]'))button.addEventListener('click',()=>call(button.dataset.action));
for(const event of ['pagehide','beforeunload'])window.addEventListener(event,clearCodes);
window.addEventListener('visibilitychange',()=>{if(document.visibilityState!=='visible')clearCodes();});
call();

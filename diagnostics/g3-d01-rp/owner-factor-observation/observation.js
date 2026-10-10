// Isolated, fixed Owner metadata read. Never imported by diagnostic or authority runtime.
if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');
import { request as httpsRequest } from 'node:https';
import { createHash } from 'node:crypto';
const MAX_BYTES=65536,TIMEOUT_MS=4000;
const fail=reason=>{throw new Error(reason);};
export const scopeDigest=scope=>createHash('sha256').update(JSON.stringify(scope)).digest('hex');
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
export function validScope(scope) {
  const id=(value,kind)=>typeof value==='string'&&new RegExp('^'+kind+'-test-[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$').test(value);
  return scope && Object.keys(scope).sort().join(',')==='application_generation,classification,owner_user_id,project_id,source_checkpoint,vercel_project_id'
    && scope.classification==='FIXED_OWNER_FACTOR_METADATA_READ_ONLY' && id(scope.project_id,'project')
    && id(scope.owner_user_id,'user') && scope.application_generation===3
    && scope.vercel_project_id==='prj_xH23xMATVChdhX34OS2vjI8dfWN2' && /^[0-9a-f]{40}$/.test(scope.source_checkpoint);
}
export function requestGate(request,config,environment,now) {
  if(!validScope(config?.scope)||config.enabled!==true)return 'DISABLED';
  if(!Number.isSafeInteger(now)||!Number.isSafeInteger(config.valid_from)||!Number.isSafeInteger(config.valid_until)
      ||config.valid_until<=config.valid_from||config.valid_until-config.valid_from>1800000
      ||now<config.valid_from||now>=config.valid_until)return 'EXPIRED';
  if(environment?.VERCEL_ENV!=='production'||environment.VERCEL_PROJECT_ID!==config.scope.vercel_project_id
      ||!/^nexus-g3-qual-[a-z0-9]+-tdy0225\.vercel\.app$/.test(environment.VERCEL_URL??'')
      ||request?.host!==environment.VERCEL_URL||request.origin!==undefined||request.fetch_site!==undefined)return 'DEPLOYMENT';
  if(request.method==='GET')return 'STATUS';
  const body=request.body;
  if(request.method!=='POST'||request.content_type!=='application/json'||request.marker!=='fixed-owner-factor-read-v1'
      ||!body||typeof body!=='object'||Array.isArray(body)||Object.keys(body).sort().join(',')!=='action,scope_sha256'
      ||body.action!=='OBSERVE_FACTORS'||body.scope_sha256!==scopeDigest(config.scope))return 'REQUEST';
  return 'OBSERVE_FACTORS';
}
export function projectOwnerFactors(body,scope) {
  if(!validScope(scope)||!body||body.status_code!==200||body.user_id!==scope.owner_user_id
      ||body.status!=='active'||body.is_locked!==false||!Array.isArray(body.totps)||body.totps.length>32)fail('OWNER_MISMATCH');
  const ids=new Set();let verified=0;
  const references=body.totps.map(f=>{
    if(!f||typeof f.totp_id!=='string'||!/^totp-test-[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}$/.test(f.totp_id)
        ||typeof f.verified!=='boolean'||ids.has(f.totp_id))fail('FACTOR_METADATA');
    ids.add(f.totp_id);if(f.verified)verified++;
    return {factor_sha256:scopeDigest([scope.project_id,scope.owner_user_id,f.totp_id]),verified:f.verified};
  }).sort((a,b)=>a.factor_sha256.localeCompare(b.factor_sha256));
  return {authority:'NONE',real_admission:'DISABLED',result:'PASS',error_class:'NONE',
    user_matched:true,total_totp_count:ids.size,verified_totp_count:verified,unverified_totp_count:ids.size-verified,
    factors:references,provider_calls:1,mutation_calls:0};
}
function nativeRead(scope,credentials) {
  return new Promise((resolve,reject)=>{
    let req,settled=false,timer;
    const finish=(error,body)=>{if(settled)return;settled=true;clearTimeout(timer);if(error){req?.destroy();reject(new Error('PROVIDER_UNKNOWN'));}else resolve(body);};
    timer=setTimeout(()=>finish(true),TIMEOUT_MS);
    try {
      req=httpsRequest({protocol:'https:',hostname:'test.stytch.com',port:443,servername:'test.stytch.com',
        rejectUnauthorized:true,method:'GET',path:'/v1/users/'+scope.owner_user_id,agent:false,
        headers:{Accept:'application/json',Authorization:'Basic '+Buffer.from(credentials.project+':'+credentials.secret).toString('base64')}},res=>{
        const length=res.headers['content-length'];
        if(res.statusCode!==200||!/^application\/json(?:;\s*charset=utf-8)?$/i.test(res.headers['content-type']??'')
            ||(res.headers['content-encoding']!==undefined&&res.headers['content-encoding']!=='identity')
            ||(length!==undefined&&(!/^\d{1,10}$/.test(String(length))||Number(length)>MAX_BYTES))){res.destroy();finish(true);return;}
        let size=0;const chunks=[];
        res.on('data',chunk=>{size+=chunk.length;if(size>MAX_BYTES){res.destroy();finish(true);}else chunks.push(chunk);});
        res.on('error',()=>finish(true));res.on('aborted',()=>finish(true));
        res.on('end',()=>{let bytes;try{if(length!==undefined&&size!==Number(length))fail('RESPONSE');bytes=Buffer.concat(chunks);finish(null,parseUniqueJson(bytes));}
          catch{finish(true);}finally{bytes?.fill(0);for(const c of chunks)c.fill(0);}});
      });
      req.on('error',()=>finish(true));req.end();
    }catch{finish(true);}
  });
}
export async function runProtectedObservation(config,environment=process.env) {
  const denied={authority:'NONE',real_admission:'DISABLED',result:'DENY',error_class:'CONFIGURATION',provider_calls:0,mutation_calls:0};
  if(!validScope(config?.scope)||config.enabled!==true)return denied;
  if(requestGate({method:'POST',host:environment.VERCEL_URL,content_type:'application/json',marker:'fixed-owner-factor-read-v1',
      body:{action:'OBSERVE_FACTORS',scope_sha256:scopeDigest(config?.scope)}},config,environment,Date.now())!=='OBSERVE_FACTORS')return denied;
  const project=environment.STYTCH_PROJECT_ID;if(project!==config.scope.project_id)return denied;
  let secret=environment.STYTCH_SECRET;
  if(typeof secret!=='string'||secret.length>268||!/^secret-test-[A-Za-z0-9_-]{16,256}={0,2}$/.test(secret))return denied;
  const credentials={project,secret};secret=null;let body;
  try {denied.provider_calls=1;body=await nativeRead(config.scope,credentials);
    if(Date.now()<config.valid_from||Date.now()>=config.valid_until)fail('EXPIRED');
    return projectOwnerFactors(body,config.scope);}
  catch{return {...denied,error_class:'PROVIDER_OR_METADATA_UNKNOWN'};}
  finally{credentials.secret=null;body=null;}
}

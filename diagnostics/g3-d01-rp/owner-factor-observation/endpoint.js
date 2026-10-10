if(typeof window!=='undefined')throw new Error('SERVER_ONLY');
import { requestGate,scopeDigest,runProtectedObservation } from '../lib/observation.js';
import { configuration } from '../lib/configuration.js';
let busy=false;
export default async function handler(req,res) {
  res.setHeader('Cache-Control','private, no-store');res.setHeader('Content-Security-Policy',"default-src 'none'; frame-ancestors 'none'");
  res.setHeader('X-Content-Type-Options','nosniff');res.setHeader('Referrer-Policy','no-referrer');
  const denied={authority:'NONE',real_admission:'DISABLED',result:'DENY',error_class:'REQUEST',provider_calls:0,mutation_calls:0};
  if(Number(req.headers['content-length']??0)>512){res.status(400).json(denied);return;}
  const gate=requestGate({method:req.method,host:req.headers.host,origin:req.headers.origin,fetch_site:req.headers['sec-fetch-site'],
    content_type:req.headers['content-type'],marker:req.headers['x-nexus-observation'],body:req.body},configuration,
    {VERCEL_ENV:process.env.VERCEL_ENV,VERCEL_PROJECT_ID:process.env.VERCEL_PROJECT_ID,VERCEL_URL:process.env.VERCEL_URL},Date.now());
  if(gate==='STATUS'){res.status(200).json({...denied,error_class:'PREFLIGHT_ONLY',scope_sha256:scopeDigest(configuration.scope),
    profile:'FIXED_OWNER_FACTOR_METADATA_READ_ONLY',valid_until:configuration.valid_until});return;}
  if(gate!=='OBSERVE_FACTORS'||busy){res.status(403).json({...denied,error_class:busy?'BUSY':gate});return;}
  busy=true;try{res.status(200).json(await runProtectedObservation(configuration));}
  catch{res.status(200).json({...denied,error_class:'UNKNOWN'});}finally{busy=false;}
}

if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');
import { safeResult } from './pre-secret-policy.js';
// Entirely synthetic lifecycle, not a Vercel/account API or credential loader.
export function createCustodyDryRun() {
  let pending=null, current=null, generation=0; const logs=[];
  const deny=()=>safeResult('DISABLED',false,true);
  return Object.freeze({
    ownerSet(value) {
      if(typeof value!=='string'||!/^OFFLINE_SENTINEL_[A-Z0-9_]{1,128}$/.test(value))return deny();
      pending=value;logs.push('OWNER_SYNTHETIC_CHANGE_PENDING');return deny();
    },
    ownerDeploy() {
      if(pending===null)return deny();current=pending;pending=null;generation++;
      logs.push('SYNTHETIC_DEPLOYMENT_GENERATION_CHANGED');return deny();
    },
    runtimeObservation(expectedGeneration) {
      return Object.freeze({ ...deny(), runtime_has_synthetic_custody: current!==null&&expectedGeneration===generation, generation });
    },
    cleanup() { pending=null;current=null;generation++;logs.push('SYNTHETIC_CLEANUP');return deny(); },
    outputs() { return Object.freeze({ response:deny(), evidence:deny(), headers:{'Cache-Control':'no-store'},
      logs:[...logs], artifact_metadata:{authority:'NONE',contains_values:false}, generation }); },
    toJSON(){return deny();},
  });
}

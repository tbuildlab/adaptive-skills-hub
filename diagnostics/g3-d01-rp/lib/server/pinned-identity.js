if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');
import { createPublicKey } from 'node:crypto';
import { closed, positive, stamp, identifier } from '../policy.js';
const SOURCE = 'OWNER_REVIEWED_STYTCH_TEST_PROJECT_KEYSET';
// No URL/discovery/fetch/TOFU. Independently reviewed project public keys are a
// non-secret immutable deployment input. Actual provider provenance is conditional.
export function pinnedKeys(value, registration, now) {
  try {
    if (!closed(value, ['source', 'project_id', 'application_generation', 'review_id',
      'valid_from', 'valid_until', 'keys']) || value.source !== SOURCE
        || value.project_id !== registration.project_id
        || value.application_generation !== registration.application_generation
        || !positive(value.application_generation) || !identifier(value.review_id)
        || !stamp(now) || !stamp(value.valid_from) || !stamp(value.valid_until)
        || now < value.valid_from || now >= value.valid_until
        || value.valid_until - value.valid_from > 86400000 || value.valid_until <= value.valid_from
        || !Array.isArray(value.keys) || value.keys.length < 1 || value.keys.length > 8
        || Buffer.byteLength(JSON.stringify(value)) > 16384) return null;
    const ids = new Set();
    for (const k of value.keys) {
      if (!closed(k, ['kty', 'kid', 'alg', 'use', 'n', 'e']) || k.kty !== 'RSA'
          || k.alg !== 'RS256' || k.use !== 'sig' || !identifier(k.kid) || ids.has(k.kid)
          || typeof k.n !== 'string' || k.n.length > 1024 || typeof k.e !== 'string' || k.e.length > 16) return null;
      const key = createPublicKey({ key: k, format: 'jwk' });
      if (key.asymmetricKeyType !== 'rsa' || key.asymmetricKeyDetails.modulusLength < 2048) return null;
      ids.add(k.kid);
    }
    return structuredClone(value.keys);
  } catch { return null; }
}

if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');
import { createPublicKey, X509Certificate, createHash } from 'node:crypto';
import { closed, positive, stamp, identifier } from '../policy.js';
const SOURCE = 'OWNER_REVIEWED_STYTCH_TEST_PROJECT_KEYSET';
const CORE = ['kty', 'kid', 'alg', 'use', 'n', 'e'];
const OPTIONAL = ['key_ops', 'x5c', 'x5tS256', 'x5t#S256'];
function publicCore(k) {
  if (!closed(k, CORE) || k.kty !== 'RSA' || k.alg !== 'RS256' || k.use !== 'sig'
      || !identifier(k.kid) || typeof k.n !== 'string' || k.n.length > 1024
      || typeof k.e !== 'string' || k.e.length > 16) return false;
  for (const field of ['n', 'e']) {
    if (!/^[A-Za-z0-9_-]+$/.test(k[field]) || Buffer.from(k[field], 'base64url').toString('base64url') !== k[field]
        || Buffer.from(k[field], 'base64url')[0] === 0) return false;
  }
  const key = createPublicKey({ key: k, format: 'jwk' });
  return key.asymmetricKeyType === 'rsa' && key.asymmetricKeyDetails.modulusLength >= 2048;
}
// Owner-supplied public input only. Envelope fields are never pinned. Optional
// certificate metadata establishes byte consistency, never CA/provider trust.
// No raw input/private field survives a rejected review.
export function normalizeReviewedPublicJwks(value) {
  try {
    const envelope = ['keys', ...(Object.hasOwn(value ?? {}, 'request_id') ? ['request_id'] : []),
      ...(Object.hasOwn(value ?? {}, 'status_code') ? ['status_code'] : [])];
    if (!closed(value, envelope) || Buffer.byteLength(JSON.stringify(value)) > 16384
        || !Array.isArray(value.keys) || value.keys.length < 1 || value.keys.length > 8) return null;
    const ids = new Set(); const keys = [];
    for (const supplied of value.keys) {
      const names = [...CORE, ...OPTIONAL.filter(name => Object.hasOwn(supplied ?? {}, name))];
      if (!closed(supplied, names)) return null;
      const key = Object.fromEntries(CORE.map(name => [name, supplied[name]]));
      if (!publicCore(key) || ids.has(key.kid)) return null;
      if (Object.hasOwn(supplied, 'key_ops') && (!Array.isArray(supplied.key_ops)
          || supplied.key_ops.length !== 1 || supplied.key_ops[0] !== 'verify')) return null;
      const thumbNames = ['x5tS256', 'x5t#S256'].filter(name => Object.hasOwn(supplied, name));
      if (thumbNames.length > 1 || (thumbNames.length && !Object.hasOwn(supplied, 'x5c'))) return null;
      if (Object.hasOwn(supplied, 'x5c')) {
        if (!Array.isArray(supplied.x5c) || supplied.x5c.length < 1 || supplied.x5c.length > 3) return null;
        const certs = [];
        for (const encoded of supplied.x5c) {
          if (typeof encoded !== 'string' || encoded.length > 6144 || !/^[A-Za-z0-9+/]+={0,2}$/.test(encoded)) return null;
          const bytes = Buffer.from(encoded, 'base64');
          if (bytes.toString('base64') !== encoded) return null;
          certs.push(new X509Certificate(bytes));
        }
        const leaf = certs[0].publicKey.export({ format: 'jwk' });
        if (leaf.kty !== key.kty || leaf.n !== key.n || leaf.e !== key.e) return null;
        if (thumbNames.length) {
          const thumb = supplied[thumbNames[0]];
          if (typeof thumb !== 'string' || !/^[A-Za-z0-9_-]{43}=?$/.test(thumb)
              || Buffer.from(thumb, 'base64url').toString('base64url') !== thumb.replace(/=$/, '')
              || !Buffer.from(thumb, 'base64url').equals(createHash('sha256').update(certs[0].raw).digest())) return null;
        }
      }
      ids.add(key.kid); keys.push(Object.freeze(key));
    }
    return Object.freeze(keys);
  } catch { return null; }
}
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
      if (!publicCore(k) || ids.has(k.kid)) return null;
      ids.add(k.kid);
    }
    return structuredClone(value.keys);
  } catch { return null; }
}

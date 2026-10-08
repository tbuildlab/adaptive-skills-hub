// Offline preparation of this one Stytch RS256 profile; no issuer/key discovery.
import { createPublicKey, verify, constants } from 'node:crypto';
import { identifier, stamp } from './policy.js';

function decode(part, limit) {
  if (typeof part !== 'string' || part.length > limit || !/^[A-Za-z0-9_-]+$/.test(part)) throw new Error('IDENTITY');
  const bytes = Buffer.from(part, 'base64url');
  if (bytes.toString('base64url') !== part) throw new Error('IDENTITY');
  return bytes;
}
// Returns only a boolean; signed raw payload/JWT never becomes diagnostic output.
export function verifyStytchIdentity(jwt, registration, remoteUser, publicKeys, now) {
  try {
    if (typeof jwt !== 'string' || jwt.length > 16384 || !stamp(now)) return false;
    if (!registration || !/^project-test-[a-f0-9-]{36}$/.test(registration.project_id)
        || registration.client_id !== registration.project_id
        || registration.issuer !== `stytch.com/${registration.project_id}`
        || remoteUser !== registration.owner_user_id || !identifier(remoteUser)) return false;
    const parts = jwt.split('.'); if (parts.length !== 3) return false;
    const header = JSON.parse(decode(parts[0], 2048).toString('utf8'));
    const claims = JSON.parse(decode(parts[1], 12288).toString('utf8'));
    if (!header || typeof header !== 'object' || Array.isArray(header)
        || Object.keys(header).some(k => !['alg', 'typ', 'kid'].includes(k))
        || header.alg !== 'RS256' || !identifier(header.kid)
        || (header.typ !== undefined && header.typ !== 'JWT')) return false;
    if (!Array.isArray(publicKeys) || publicKeys.length < 1 || publicKeys.length > 8) return false;
    const selected = publicKeys.filter(k => k.kid === header.kid);
    if (selected.length !== 1) return false;
    const jwk = selected[0];
    if (jwk.kty !== 'RSA' || jwk.alg !== 'RS256' || jwk.use !== 'sig'
        || Object.keys(jwk).some(k => !['kty', 'kid', 'alg', 'use', 'n', 'e'].includes(k))) return false;
    const key = createPublicKey({ key: jwk, format: 'jwk' });
    if (key.asymmetricKeyType !== 'rsa' || key.asymmetricKeyDetails.modulusLength < 2048) return false;
    if (!verify('RSA-SHA256', Buffer.from(`${parts[0]}.${parts[1]}`),
      { key, padding: constants.RSA_PKCS1_PADDING }, decode(parts[2], 2048))) return false;
    const sec = now / 1000;
    const exactAudience = claims.aud === registration.project_id
      || (Array.isArray(claims.aud) && claims.aud.length === 1 && claims.aud[0] === registration.project_id);
    return claims.iss === registration.issuer && exactAudience
      && claims.sub === remoteUser && identifier(claims.sub)
      && ['exp', 'iat', 'nbf'].every(k => Number.isSafeInteger(claims[k]) && claims[k] >= 0)
      && claims.iat <= sec && claims.nbf <= sec && claims.exp > sec
      && claims.exp > claims.iat && claims.exp > claims.nbf && sec - claims.iat < 300;
  } catch { return false; }
}

if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');
import { DEPLOYMENT as ORIGINAL } from './deployment-input.js';
import { PENDING_OWNER_REGISTRATION, PENDING_REGISTRATION_GENERATION } from './pending-delivery-review.js';

// Fresh public JSON supplied and explicitly reviewed by the Owner in this turn.
// Six normalized public fields only. No discovery, envelope, bearer or private
// material. This additive input is absent from the current deployed entrypoint.
const key = Object.freeze({
  kty: 'RSA',
  kid: 'jwk-test-c45fe918-34f4-454a-b3bb-48011acb591d',
  alg: 'RS256',
  use: 'sig',
  n: '4BmlA7TgEpLedgm8PM2E9WUrGfDoKYctplRTgBU47ODVt_bcbJalYQrKMnAoi2q4yTsoL6JABsJO_3TRfjdyiF4fuRWDhUtMicVcJEfDhRaosiEflyFWMVwOuhl8VaMd4cwdSFcYVhap3XalSBbOzQd8iZLL5ybRheeNt25Ic70uF7PfrxOPHfz6YpfyC4ACx5muxxIAmSBpCLCPCaYyHWBMr40ENF8iCQOXmMuO0LgALQDZqWcY15vBP65liIJ2LCVQwpyjOHOQZy1Aa5XbyX19Bq7r-Xp_Wi6S81XJhcbPVLtEUIMPYdYnoGTHZDbRBoe-aBE0Syx-07e0qPM_Qw',
  e: 'AQAB',
});

// First processing clock after the fresh confirmation, not an invented exact
// message timestamp. A conservative 23-hour window stays below the 24-hour cap.
const reviewedAt = Date.parse('2026-10-09T16:35:37Z');
export const OWNER_KEYSET_GENERATION_2 = Object.freeze({
  source: 'OWNER_REVIEWED_STYTCH_TEST_PROJECT_KEYSET',
  project_id: PENDING_OWNER_REGISTRATION.project_id,
  application_generation: 2,
  review_id: 'owner-public-keys-20261010-v2',
  valid_from: reviewedAt,
  valid_until: reviewedAt + 23 * 60 * 60 * 1000,
  keys: Object.freeze([key]),
});

// Configuration only; neither this object nor public keys provide authority.
// Original registration/pin and historical artifact validators stay unchanged.
export const DISABLED_GENERATION_2_INPUT = Object.freeze({
  ...ORIGINAL,
  mode: 'FAKE_DISABLED',
  deployment_revision: PENDING_OWNER_REGISTRATION.deployment_revision,
  registration_generation: PENDING_REGISTRATION_GENERATION,
  provider: PENDING_OWNER_REGISTRATION,
  keyset: OWNER_KEYSET_GENERATION_2,
});

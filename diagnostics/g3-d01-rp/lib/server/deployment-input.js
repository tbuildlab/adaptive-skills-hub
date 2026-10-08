if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');
// Exact Owner-supplied non-secret registration/public pin. No network discovery.
// First real registration generation: 0 (unregistered) -> 1; fixture generations
// never count as Owner registration. OTP delivery remains explicitly unregistered.
const registered = {
  "provider": "STYTCH_CONSUMER",
  "environment": "TEST",
  "project_id": "project-test-0f758990-01e7-4a4f-8bfd-44357610ef5d",
  "owner_user_id": "user-test-9da3c5e0-6828-4dfe-8d6d-6ee5dde17a8e",
  "project_generation": 1,
  "application_generation": 1,
  "owner_generation": 1,
  "binding_generation": 1,
  "origin": "https://nexus-g3-qual.vercel.app",
  "factors": [
    "EMAIL_OTP",
    "TOTP"
  ],
  "session_max_minutes": 15,
  "context_max_ms": 300000,
  "deployment_revision": "g3-d01-owner-pinning-v1",
  "source": "OWNER_REVIEWED",
  "review_id": "owner-registration-20261009-v1",
  "delivery_email": null
};
registered.factors = Object.freeze(registered.factors);
const provider = Object.freeze({ ...registered, issuer: `stytch.com/${registered.project_id}`, audience: registered.project_id });
const reviewedKeyset = {
  "source": "OWNER_REVIEWED_STYTCH_TEST_PROJECT_KEYSET",
  "application_generation": 1,
  "review_id": "owner-public-keys-20261009-v1",
  "valid_from": 1791477725000,
  "valid_until": 1791564125000,
  "keys": [
    {
      "kty": "RSA",
      "kid": "jwk-test-c45fe918-34f4-454a-b3bb-48011acb591d",
      "alg": "RS256",
      "use": "sig",
      "n": "4BmlA7TgEpLedgm8PM2E9WUrGfDoKYctplRTgBU47ODVt_bcbJalYQrKMnAoi2q4yTsoL6JABsJO_3TRfjdyiF4fuRWDhUtMicVcJEfDhRaosiEflyFWMVwOuhl8VaMd4cwdSFcYVhap3XalSBbOzQd8iZLL5ybRheeNt25Ic70uF7PfrxOPHfz6YpfyC4ACx5muxxIAmSBpCLCPCaYyHWBMr40ENF8iCQOXmMuO0LgALQDZqWcY15vBP65liIJ2LCVQwpyjOHOQZy1Aa5XbyX19Bq7r-Xp_Wi6S81XJhcbPVLtEUIMPYdYnoGTHZDbRBoe-aBE0Syx-07e0qPM_Qw",
      "e": "AQAB"
    }
  ]
};
reviewedKeyset.keys = Object.freeze(reviewedKeyset.keys.map(key => Object.freeze(key)));
const keyset = Object.freeze({ ...reviewedKeyset, project_id: provider.project_id });
export const DEPLOYMENT = Object.freeze({
  mode: 'FAKE_DISABLED', deployment_tier: 'PRODUCTION',
  origin: 'https://nexus-g3-qual.vercel.app', deployment_revision: provider.deployment_revision,
  registration_generation: 1, provider, keyset,
});

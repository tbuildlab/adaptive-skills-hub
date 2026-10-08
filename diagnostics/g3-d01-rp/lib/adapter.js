import { G3_D01_LIVE_DIAGNOSTIC_ENABLED } from './policy.js';

// Future server-only injection contract. Names, never values; no process.env read.
// Server-mediated email OTP/TOTP needs project ID + server secret. No frontend SDK
// is loaded, so STYTCH_PUBLIC_TOKEN is not required by this implementation.
export const FUTURE_SERVER_INPUT_NAMES = Object.freeze(['STYTCH_PROJECT_ID', 'STYTCH_SECRET']);
export const ADAPTER_MODE = 'FAKE_DISABLED';

// No live implementation exists. A flag/config/injected fake cannot promote it.
export function selectAdapter(_untrustedFlag, _untrustedAdapter) {
  if (G3_D01_LIVE_DIAGNOSTIC_ENABLED !== false) throw new Error('LIVE_DISABLED');
  return Object.freeze({ mode: ADAPTER_MODE,
    async observe(_point) { return Object.freeze({ kind: 'FAKE_DISABLED' }); },
  });
}

// Future reviewed implementation must project remote responses to the closed
// observation contract in model.js; authenticate the exact retained opaque token;
// omit session_duration_minutes/custom claims on recheck; verify signed pinned
// issuer/audience/sub and same remote Session/User. No networking/SDK here.

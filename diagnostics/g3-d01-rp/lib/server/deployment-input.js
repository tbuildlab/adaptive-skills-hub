if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');
// Exact future reviewed code/config input. No environment discovery and no actual
// provider IDs accepted here. Owner replacement is a separate reviewed revision.
export const DEPLOYMENT = Object.freeze({
  mode: 'FAKE_DISABLED', deployment_tier: 'PRODUCTION',
  origin: 'https://nexus-g3-qual.vercel.app', deployment_revision: 'UNREGISTERED',
  registration_generation: 0, provider: null, keyset: null,
});

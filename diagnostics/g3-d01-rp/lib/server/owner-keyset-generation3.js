if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');
import { DISABLED_GENERATION_2_INPUT as PREVIOUS } from './owner-keyset-generation2.js';
import { PENDING_OWNER_GENERATION_3_REGISTRATION as provider } from './pending-delivery-generation3.js';

// Explicit standing Owner authorization: same already-reviewed public material,
// new bounded delivery registration, no new trust source or review renewal.
export const OWNER_KEYSET_GENERATION_3 = Object.freeze({
  ...PREVIOUS.keyset,
  application_generation: provider.application_generation,
  review_id: 'owner-public-keys-standing-rebind-20261010-v3',
});

export const DISABLED_GENERATION_3_INPUT = Object.freeze({
  ...PREVIOUS,
  mode: 'FAKE_DISABLED',
  deployment_revision: provider.deployment_revision,
  registration_generation: provider.application_generation,
  provider,
  keyset: OWNER_KEYSET_GENERATION_3,
});

if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');
import { DISABLED_GENERATION_2_INPUT as PREVIOUS } from './owner-keyset-generation2.js';

// Owner-supplied delivery configuration only. Email never establishes identity.
// A new keyset-generation review is still required; generation 2 is not relabeled.
// This data-only module is absent from the deployed/public entrypoint graph.
export const OWNER_DELIVERY_GENERATION_3_REVIEW = Object.freeze({
  source: 'OWNER_REVIEWED',
  review_id: 'owner-delivery-20261010-v3',
  delivery_email: 'teedeyong0225@gmail.com',
  previous_application_generation: PREVIOUS.provider.application_generation,
  next_application_generation: PREVIOUS.provider.application_generation + 1,
  deployment_revision: 'g3-d01-owner-delivery-v3',
  keyset_review_status: 'PENDING_OWNER_REVIEW_FOR_NEW_GENERATION',
  authority: 'NONE',
});

export const PENDING_OWNER_GENERATION_3_REGISTRATION = Object.freeze({
  ...PREVIOUS.provider,
  application_generation: OWNER_DELIVERY_GENERATION_3_REVIEW.next_application_generation,
  deployment_revision: OWNER_DELIVERY_GENERATION_3_REVIEW.deployment_revision,
  review_id: OWNER_DELIVERY_GENERATION_3_REVIEW.review_id,
  delivery_email: OWNER_DELIVERY_GENERATION_3_REVIEW.delivery_email,
});

// Intentionally incomplete: neither an active pin nor a transport registration.
// Do not inherit the generation 2 keyset or mint an OWNER_REVIEWED generation 3 pin.
export const PENDING_DISABLED_GENERATION_3_INPUT = Object.freeze({
  ...PREVIOUS,
  mode: 'FAKE_DISABLED',
  deployment_revision: PENDING_OWNER_GENERATION_3_REGISTRATION.deployment_revision,
  registration_generation: PENDING_OWNER_GENERATION_3_REGISTRATION.application_generation,
  provider: PENDING_OWNER_GENERATION_3_REGISTRATION,
  keyset: null,
});

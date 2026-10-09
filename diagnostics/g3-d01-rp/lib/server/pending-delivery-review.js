if (typeof window !== 'undefined') throw new Error('SERVER_ONLY');
import { DEPLOYMENT } from './deployment-input.js';

// Explicit Owner input on 2026-10-10. Delivery is configuration, never identity.
// Data-only preparation: the deployed entrypoint does not import this module.
// No keys are rebound, gates enabled, credentials read, or provider calls made.
export const OWNER_DELIVERY_REVIEW = Object.freeze({
  source: 'OWNER_REVIEWED',
  review_id: 'owner-delivery-20261010-v2',
  delivery_email: 'nexus.g3.test4821@gmail.com',
  previous_application_generation: DEPLOYMENT.provider.application_generation,
  next_application_generation: DEPLOYMENT.provider.application_generation + 1,
  deployment_revision: 'g3-d01-owner-delivery-v2',
  keyset_review_status: 'PENDING_OWNER_REVIEW_FOR_NEW_GENERATION',
  authority: 'NONE',
});

// The application/deployment generation changes; project, human identity and
// workspace binding do not. Registration generation must match application
// generation at any later reviewed assembly. This is not an assembly or handle.
export const PENDING_OWNER_REGISTRATION = Object.freeze({
  ...DEPLOYMENT.provider,
  application_generation: OWNER_DELIVERY_REVIEW.next_application_generation,
  deployment_revision: OWNER_DELIVERY_REVIEW.deployment_revision,
  review_id: OWNER_DELIVERY_REVIEW.review_id,
  delivery_email: OWNER_DELIVERY_REVIEW.delivery_email,
});

export const PENDING_REGISTRATION_GENERATION = PENDING_OWNER_REGISTRATION.application_generation;

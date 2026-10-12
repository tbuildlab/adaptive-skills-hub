"""Exact Owner-reviewed public pins from independently retained R bytes.

This is a public-key review constraint only. It cannot enroll a source writer,
authenticate an Owner, produce a decision, or grant execution authority.
"""
from dataclasses import dataclass, replace
from datetime import datetime, timezone
import time

from ash import g3_checkpoint_custody as custody
from ash import g3_delegated_control_codec as codec
from ash.g3_control_semantics import require
from ash.g3_n01_owner_context import PROJECT, integer, public_keys

PACKAGE_SHA='be22798028d218c2ec83816e0d78407f0b30eab82295db217c673318d58fdbc3'
ACCEPTANCE_SHA='67f612bfb60977534e3fab0efbf9ca75fe5765a2e632b4be0f63844d6f5588ae'
PREFIX=custody.APPROVALS+'public-pin-owner-review-20261011-v1/'
FROM_MS=1791762711502
UNTIL_MS=1791791511502
KEYS_SHA='4e735ee0dd506031013a15c605a6ab08ffbbe1b45d3605b0ee3254872d814480'
CONFIG='3632c49345ea111aa992b27a8645e44f479fe7685c98ac04515147891fd0a2d1'


@dataclass(frozen=True)
class PublicReview:
    key_bytes: bytes
    valid_from_ms: int
    valid_until_ms: int
    package_sha256: str
    acceptance_sha256: str

    def __post_init__(self):
        require(type(self.key_bytes) is bytes and codec.digest(self.key_bytes)==KEYS_SHA)
        public_keys(tuple(codec.decode(self.key_bytes)))
        require(type(self.valid_from_ms) is int and type(self.valid_until_ms) is int
                and self.valid_from_ms==FROM_MS and self.valid_until_ms==UNTIL_MS
                and self.package_sha256==PACKAGE_SHA and self.acceptance_sha256==ACCEPTANCE_SHA)

    @property
    def authority(self):return 'NONE'

    @property
    def keys(self):return public_keys(tuple(codec.decode(self.key_bytes)))


def verify_review(proposal,acceptance,*,now_ms):
    """Exact bytes/interval only; caller must prove independent custody origin."""
    try:
        require(type(proposal) is bytes and type(acceptance) is bytes
                and 0<len(proposal)<=8192 and 0<len(acceptance)<=4096)
        require(codec.digest(proposal)==PACKAGE_SHA and codec.digest(acceptance)==ACCEPTANCE_SHA)
        pending=codec.decode(proposal);approved=codec.decode(acceptance)
        require(pending['approval']=='NOT_OBTAINED' and approved['approval']=='OWNER_EXPLICITLY_APPROVED')
        require(approved['canonical_review_package_sha256']==PACKAGE_SHA)
        for field in ('project_id','issuer','service_revision','application_generation',
                      'review_generation','review_id','valid_from_ms','valid_until_ms'):
            require(pending[field]==approved[field])
        require(pending['project_id']==PROJECT and pending['issuer']=='stytch.com/'+PROJECT)
        require(FROM_MS<=integer(now_ms)<UNTIL_MS)
        require(FROM_MS==pending['valid_from_ms'] and UNTIL_MS==pending['valid_until_ms'])
        require(type(pending['application_generation']) is int and pending['application_generation']==1
                and type(pending['review_generation']) is int and pending['review_generation']==1)
        require(approved['real_admission']==pending['real_admission']=='NO')
        keys=public_keys(tuple(pending['keys']))
        require(codec.digest(codec.canonical(list(keys)))==pending['keys_sha256'])
        return PublicReview(codec.canonical(list(keys)),FROM_MS,UNTIL_MS,PACKAGE_SHA,ACCEPTANCE_SHA)
    except Exception:
        raise ValueError('N01_PUBLIC_REVIEW_DENY') from None


def read_protected_review(client,storage_registration,*,now_ms):
    """Two fixed R-only documents, exact versions, retention and fresh inventory.

    Reuses qualified versioned-read transport; no write, credential loading,
    historical review extension, runtime/source registration or authority.
    """
    try:
        require(type(storage_registration) is custody.Registration and storage_registration.generation==2
                and storage_registration.config_sha256==CONFIG)
        require(FROM_MS<=integer(now_ms)<UNTIL_MS)
        started=int(time.time()*1000)
        require(now_ms<=started<UNTIL_MS)
        until=datetime.fromtimestamp(UNTIL_MS/1000,timezone.utc)
        fence=custody.N01S3Fence(client,replace(storage_registration,prefix=PREFIX),max_attempts=8)
        inventory=fence.inventory('')
        require(tuple(key for key,_ in inventory)==(PREFIX+'acceptance.json',PREFIX+'proposal.json'))
        material={key:fence.retained(key,version,until) for key,version in inventory}
        require(fence.inventory('')==inventory)
        finished=int(time.time()*1000);require(started<=finished<UNTIL_MS)
        return verify_review(material[PREFIX+'proposal.json'],material[PREFIX+'acceptance.json'],now_ms=finished)
    except Exception:
        raise ValueError('N01_PUBLIC_REVIEW_CUSTODY_QUARANTINE') from None

"""Closed N01 runtime/source binding against independently protected enrollment.

This module owns deterministic equality and bounds only. The runtime must obtain
enrollment bytes from R-only custody, qualify its deployed artifact separately,
and obtain current Owner observations through the native SDK. Nothing here can
authenticate supplied bytes, restore a context, mint a grant or enable admission.
"""
from dataclasses import dataclass,replace
from datetime import datetime,timezone
import re
import time

from ash import g3_delegated_control_codec as codec
from ash import g3_checkpoint_custody as custody
from ash.g3_control_semantics import require
from ash.g3_n01_owner_context import PROJECT, OWNER, integer
from ash.g3_n01_public_review import PublicReview, PACKAGE_SHA, ACCEPTANCE_SHA, FROM_MS, UNTIL_MS

CONFIG='3632c49345ea111aa992b27a8645e44f479fe7685c98ac04515147891fd0a2d1'
HOST_PROJECT='prj_xH23xMATVChdhX34OS2vjI8dfWN2'
FIELDS=frozenset(('schema_version','purpose','authority_mode','authority_config_sha256',
    'authority_instance','application_generation','review_generation','service_revision',
    'review_package_sha256','review_acceptance_sha256','principal','deployment_id','deployment_host',
    'host_project_id','artifact_inventory_sha256','process_nonce','source_kinds','issued_at_ms',
    'expires_at_ms','no_automatic_redispatch','real_admission'))
PREFIX=custody.APPROVALS+'current-source-controller-v1/'


@dataclass(frozen=True)
class EnrolledSource:
    canonical_bytes: bytes
    enrollment_sha256: str

    @property
    def authority(self):return 'NONE'

    @property
    def value(self):return codec.decode(self.canonical_bytes)


def bind_source(raw,review,*,native_environment,artifact_inventory_sha256,process_nonce,now_ms):
    """Caller must already prove R origin, not merely an expected file digest.

    Fixed source kinds only, exact deployment and ephemeral process incarnation.
    This can constrain later Owner-context ingestion, not make a PRODUCTION grant
    registration or qualify G1/G2/technical/task/effect sources.
    """
    try:
        require(type(raw) is bytes and 0<len(raw)<=8192 and type(review) is PublicReview)
        value=codec.decode(raw);require(type(value) is dict and set(value)==FIELDS)
        require(value['schema_version']=='nexus.g3.n01.current-source-enrollment.v1')
        require(value['purpose']=='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY'
                and value['authority_mode']=='DELEGATED_EXECUTOR'
                and value['authority_config_sha256']==CONFIG
                and value['authority_instance']=='g3-n01-qualification-v1')
        require(value['service_revision']=='nexus-g3-n01-controller-v1')
        for field in ('application_generation','review_generation'):
            require(type(value[field]) is int and value[field]==1)
        require(value['review_package_sha256']==review.package_sha256==PACKAGE_SHA
                and value['review_acceptance_sha256']==review.acceptance_sha256==ACCEPTANCE_SHA)
        require(value['principal']==dict(issuer='stytch.com/'+PROJECT,client_id=PROJECT,subject=OWNER))
        require(value['real_admission']=='NO' and value['no_automatic_redispatch']=='REQUIRED')
        require(value['source_kinds']==['D01','D03','OWNER_ENROLLMENT'])
        require(FROM_MS<=integer(value['issued_at_ms'])<=integer(now_ms)<integer(value['expires_at_ms'])<=UNTIL_MS)
        require(review.valid_from_ms==FROM_MS and review.valid_until_ms==UNTIL_MS)
        codec.old.check_type(value['artifact_inventory_sha256'],'h')
        require(value['artifact_inventory_sha256']==artifact_inventory_sha256)
        require(type(value['process_nonce']) is str
                and re.fullmatch('[0-9a-f]{64}',value['process_nonce']) is not None
                and value['process_nonce']==process_nonce)
        require(type(value['deployment_id']) is str
                and re.fullmatch('dpl_[A-Za-z0-9]{20,40}',value['deployment_id']) is not None)
        require(type(value['deployment_host']) is str and re.fullmatch(
            r'nexus-g3-qual-[a-z0-9]+-tdy0225\.vercel\.app',value['deployment_host']) is not None)
        # Read only four non-secret system fields; do not enumerate environment.
        require(native_environment.get('VERCEL_ENV')=='production'
                and native_environment.get('VERCEL_PROJECT_ID')==value['host_project_id']==HOST_PROJECT
                and native_environment.get('VERCEL_DEPLOYMENT_ID')==value['deployment_id']
                and native_environment.get('VERCEL_URL')==value['deployment_host'])
        return EnrolledSource(raw,codec.digest(raw))
    except Exception:
        raise ValueError('N01_SOURCE_ENROLLMENT_DENY') from None


def read_protected_source(client,storage_registration,review,*,native_environment,
                          artifact_inventory_sha256,process_nonce,now_ms,custody_revision=1):
    """One fixed independently writable enrollment, never caller-selected origin.

    The existing A role can only version-read this prefix; R administration must
    separately verify actual deployment/source before writing it. No missing or
    ambiguous object can be replaced by a local file or a supplied PASS label.
    """
    try:
        require(type(storage_registration) is custody.Registration and storage_registration.generation==2
                and storage_registration.config_sha256==CONFIG)
        require(FROM_MS<=integer(now_ms)<UNTIL_MS)
        started=int(time.time()*1000);require(now_ms<=started<UNTIL_MS)
        require(type(review) is PublicReview)
        require(type(custody_revision) is int and custody_revision in (1,2,3))
        prefix=custody.APPROVALS+f'current-source-controller-v{custody_revision}/'
        scope=replace(storage_registration,prefix=prefix)
        fence=custody.N01S3Fence(client,scope,max_attempts=4)
        inventory=fence.inventory('')
        require(len(inventory)==1 and inventory[0][0]==prefix+'registration.json')
        raw=fence.retained(*inventory[0],datetime.fromtimestamp(UNTIL_MS/1000,timezone.utc))
        require(fence.inventory('')==inventory)
        finished=int(time.time()*1000);require(started<=finished<UNTIL_MS)
        return bind_source(raw,review,native_environment=native_environment,
            artifact_inventory_sha256=artifact_inventory_sha256,process_nonce=process_nonce,now_ms=finished)
    except Exception:
        raise ValueError('N01_SOURCE_CUSTODY_QUARANTINE') from None

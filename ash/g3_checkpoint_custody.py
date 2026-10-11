"""Exact N01 v2 storage compatibility over the retained D03 S3 transport.

No authentication, grant, dispatch or production registration. This bounded
storage qualification is TEST_ONLY; independently retained bytes constrain but
cannot create authority. Credentials and resource enrollment are external.
"""
from dataclasses import dataclass, replace
from ash import g3_delegated_record_codec as records
from ash import g3_delegated_control_codec as control
from ash.g3_control_semantics import check_delegated_control
from scripts import g3_d03_s3_fence as transport

NORMAL = 'qualification/n01/v1/normal/'
APPROVALS = 'qualification/n01/v1/approvals/'
INSTANCE = 'g3-n01-qualification-v1'
require = transport.require
FenceError = transport.FenceError


def reference(raw):
    parsed = records.parse_metadata(raw)
    require(parsed.to_dict()['schema_version'] == records.PREFIX+'recovery-checkpoint.v2')
    return dict(id=parsed.record_id, body_sha256=parsed.body_sha256)


@dataclass(frozen=True)
class Registration:
    bucket: str
    owner: str
    prefix: str
    authority_instance: str
    generation: int
    genesis_id: str
    genesis_sha256: str
    admin_checkpoint_ids: tuple[str, ...]
    config_sha256: str
    purpose: str = 'TEST_ONLY'

    def __post_init__(self):
        require(self.bucket == 'nexus-d03-custody-862902859484-ap-southeast-1-v1')
        require(self.owner == '862902859484' and self.purpose == 'TEST_ONLY')
        require(self.prefix.endswith('/') and (self.prefix == NORMAL or self.prefix.startswith(APPROVALS)))
        require(not any(part in self.prefix for part in ('..', '//', '\\')))
        require(self.authority_instance == INSTANCE and type(self.generation) is int and self.generation == 1)
        control.old.check_type(self.config_sha256, 'h')
        control.old.check_type(self.genesis_sha256, 'h')
        require(type(self.genesis_id) is str and self.genesis_id.startswith(records.PREFIX+'recovery-checkpoint.v2:'))
        control.old.check_type(self.genesis_id.rpartition(':')[2], 'h')
        require(type(self.admin_checkpoint_ids) is tuple and self.genesis_id in self.admin_checkpoint_ids)


@dataclass(frozen=True)
class ProtectedHistory(transport.ProtectedHistory):
    @property
    def head(self):
        return reference(self.checkpoints[-1])


class N01S3Fence(transport.S3Fence):
    """Fixed v2 lineage; always NONE. Does not upgrade diagnostic membership."""
    registration_type = Registration
    ledger_domain = records.PREFIX+'ledger-commit.v2'
    record_parser = staticmethod(records.parse_metadata)
    reference = staticmethod(reference)
    decoded = staticmethod(control.decode)
    domain_digest = staticmethod(records.domain_digest)

    def independent_recovery_authorization(self, body, ref, valid_until):
        prefix = APPROVALS+f"recover/{body['recovery_sequence']:020d}/"
        protected = N01S3Fence(self.client, replace(self.registration,prefix=prefix),
                               max_attempts=self.max_attempts-self.attempts)
        try:
            inventory = protected.inventory('')
            require(len(inventory)==1 and inventory[0][0]==prefix+'authorization.json')
            raw = protected.retained(*inventory[0],valid_until)
            require(control.decode(raw)==dict(schema_version='nexus.g3.n01.storage-admin.v1',
                purpose='TEST_ONLY',config_sha256=self.registration.config_sha256,
                generation=self.registration.generation,checkpoint=ref,
                previous_checkpoint=body['previous_checkpoint']))
            require(protected.inventory('')==inventory)
        finally:
            self.attempts += protected.attempts

    def read(self, *, valid_until):
        try:
            result = super().read(valid_until=valid_until)
            bodies = {}
            for raw,root,pages in zip(result.checkpoints,result.controls,result.pages):
                ref=reference(raw);bodies[ref['id']]=raw
                body=control.decode(raw)
                require(body['authority_config_sha256']==self.registration.config_sha256)
                snapshot=control.EncodedSnapshot(root,pages)
                # A source/receipt/grant cannot enter this empty storage-only
                # enrollment: its missing authentic body/evidence fails closed.
                checked=check_delegated_control(snapshot,bodies,{},profile='TEST_ONLY',
                            protected_config=self.registration.config_sha256)
                require(checked.authority=='NONE')
            return ProtectedHistory(result.checkpoints,result.versions,result.descriptors,
                                    result.controls,result.pages)
        except Exception:
            self.quarantined=True
            raise FenceError('N01_CUSTODY_QUARANTINE') from None

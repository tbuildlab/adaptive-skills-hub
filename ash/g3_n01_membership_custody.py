"""Complete immutable membership read, always NONE and without source promotion.

Reuses the qualified version/inventory/retention/lineage transport and complete
retained-state resolver. The historical empty TEST_ONLY fence remains unchanged.
PRODUCTION selects structural joins only; it does not qualify any source writer.
"""
from dataclasses import dataclass

from ash import g3_checkpoint_custody as custody
from ash import g3_delegated_control_codec as control
from ash import g3_delegated_record_codec as records
from ash import g3_grant_codec as grants
from ash import g3_n01_retained_state as retained
from ash.g3_control_semantics import require
from scripts import g3_d03_s3_fence as transport


@dataclass(frozen=True)
class StructuralRecordReference:
    record_id: str
    body_sha256: str
    @property
    def authority(self):return 'NONE'


def parse_retained_record(raw):
    """Exact existing mixed v1 grant/revocation and v2 metadata identities."""
    value=control.decode(raw)
    if value.get('schema_version')==grants.GRANT_SCHEMA:
        ident=grants.approval_grant(value).grant_id
    elif value.get('schema_version')==grants.REVOCATION_SCHEMA:
        ident=grants.revocation(value).revocation_id
    else:
        parsed=records.parse_metadata(raw)
        require(parsed.to_dict()['schema_version'].endswith('.v2'))
        ident=parsed.record_id
    return StructuralRecordReference(ident,control.digest(raw))


@dataclass(frozen=True)
class CompleteMembership:
    history: custody.ProtectedHistory
    states: tuple[retained.RetainedState,...]
    objects: tuple[tuple[str,bytes],...]
    @property
    def authority(self):return 'NONE'
    @property
    def head(self):return self.history.head
    @property
    def checkpoints(self):return self.history.checkpoints
    @property
    def versions(self):return self.history.versions


class MembershipFence(custody.N01S3Fence):
    """Read-only full body resolution. No append, recovery, grant or admission.

The resource Registration is still TEST_ONLY and generation 1/2. A caller cannot
use structural PRODUCTION joins to promote that resource or an enrolled writer.
Old independent recovery authorization semantics remain exactly inherited.
"""
    record_parser=staticmethod(parse_retained_record)
    def __init__(self,client,registration,*,profile,max_attempts=1000):
        require(profile in ('TEST_ONLY','PRODUCTION') and registration.prefix==custody.NORMAL)
        super().__init__(client,registration,max_attempts=max_attempts)
        self.profile=profile
    def call(self,operation,**kwargs):
        require(operation in ('list_object_versions','get_object','get_object_retention'))
        return super().call(operation,**kwargs)
    def append(self,*args,**kwargs):
        self.quarantined=True
        raise ValueError('N01_MEMBERSHIP_READER_HAS_NO_WRITE_AUTHORITY')
    def reconcile(self,*args,**kwargs):
        self.quarantined=True
        raise ValueError('N01_MEMBERSHIP_READER_HAS_NO_RECOVERY_AUTHORITY')
    def read(self,*,valid_until):
        self.quarantined=True
        try:
            # Deliberately bypass only the old empty-membership semantic reader;
            # preserve the full authenticated-transport/lineage checks unchanged.
            base=transport.S3Fence.read(self,valid_until=valid_until)
            history=custody.ProtectedHistory(base.checkpoints,base.versions,base.descriptors,base.controls,base.pages)
            inventory=self.inventory('objects/')
            require(0<len(inventory)<=256)
            descriptors={control.decode(raw)['ledger_commit_sha256']:descriptor
                for raw,descriptor in zip(history.checkpoints,history.descriptors)}
            objects={}
            for key,version in inventory:
                digest=key.removeprefix(custody.NORMAL+'objects/')
                control.old.check_type(digest,'h')
                raw=self.retained(key,version,valid_until)
                if digest in descriptors:
                    require(raw==descriptors[digest])
                elif control.digest(raw)!=digest:
                    # PREPARED retains a future domain-addressed descriptor
                    # before its journal append. Validate its complete closed
                    # shape, but do not resolve it as checkpoint membership.
                    descriptor=control.decode(raw)
                    require(type(descriptor) is dict and 'control_after_sha256' in descriptor)
                    control.old.check_type(descriptor['control_after_sha256'],'h')
                    require(records.domain_digest(records.PREFIX+'ledger-commit.v2',descriptor)==digest)
                    checkpoint={key:value for key,value in descriptor.items() if key!='control_after_sha256'}
                    checkpoint.update(schema_version=records.PREFIX+'recovery-checkpoint.v2',ledger_commit_sha256=digest)
                    parsed=records.parse_metadata(control.canonical(checkpoint))
                    require(parsed.to_dict()['authority_config_sha256']==self.registration.config_sha256)
                else:
                    require(control.digest(raw)==digest)
                    objects[digest]=raw
            # Checkpoints live in the qualified journal, not normal objects.
            # Add those independently read exact bytes for nested references.
            for raw in history.checkpoints:
                digest=control.digest(raw)
                require(digest not in objects or objects[digest]==raw)
                objects[digest]=raw
            require(len(objects)<=256)
            states=[]
            for position,(raw,root,pages) in enumerate(zip(history.checkpoints,history.controls,history.pages)):
                require(control.decode(raw)['authority_config_sha256']==self.registration.config_sha256)
                states.append(retained.resolve_retained_state(control.EncodedSnapshot(root,pages),
                    history.checkpoints[:position+1],objects,profile=self.profile,
                    config_sha256=self.registration.config_sha256))
            require(self.inventory('journal/')==history.versions and self.inventory('objects/')==inventory)
            return CompleteMembership(history,tuple(states),tuple(sorted(objects.items())))
        except Exception:
            raise ValueError('N01_MEMBERSHIP_CUSTODY_QUARANTINE') from None

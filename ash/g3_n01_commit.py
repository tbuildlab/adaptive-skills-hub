"""One exact N01 PREPARED/custody/FINALIZED protocol; never release authority.

Native transports are supplied by independently enrolled protected runtime. No
credential discovery, source enrollment, genesis, recovery, retries or effects.
Unknown outcomes retire this process coordinator permanently. A fresh process
can observe NONE only; it cannot restore the retired coordinator or a bearer.
"""
from ash import g3_checkpoint_custody as custody
from ash import g3_delegated_control_codec as control
from ash import g3_delegated_record_codec as records
from ash.g3_primary_ledger import DelegatedDynamoReservations
from ash.g3_transition_protocol import Preparation,prepare_delegated_transition
from ash.g3_control_semantics import require,check_delegated_control


class SingleCommit:
    """Fixed transaction ordering only. TEST_ONLY fence cannot accept live sources."""
    def __init__(self,ledger,fence,*,expected_head,valid_until):
        require(type(ledger) is DelegatedDynamoReservations and type(fence) is custody.N01S3Fence)
        require(type(expected_head) is bytes)
        custody.reference(expected_head)
        require(ledger.instance==fence.registration.authority_instance)
        require(fence.registration.prefix==custody.NORMAL)
        self.ledger=ledger;self.fence=fence;self.expected_head=expected_head
        self.valid_until=valid_until;self.retired=False;self.used=False
    @property
    def authority(self):return 'NONE'
    def __repr__(self):return 'SingleCommit(authority=NONE)'
    def __reduce_ex__(self,_):raise TypeError('N01_COMMIT_NOT_RESTORABLE')
    def __getstate__(self):raise TypeError('N01_COMMIT_NOT_RESTORABLE')

    def commit(self,candidate):
        try:
            require(not self.retired and not self.used)
            require(type(candidate) is Preparation and candidate.expected_checkpoint==self.expected_head)
            value=records.parse_metadata(candidate.checkpoint).to_dict()
            require(value['transition_kind'] not in ('GENESIS','RECOVER'))
            require(value['authority_config_sha256']==self.fence.registration.config_sha256)
            # Reject live membership before any primary write. This qualified
            # storage transport has an empty TEST_ONLY provenance registration.
            rows=control.verify_snapshot(candidate.snapshot)
            require(all(control.decode(row.value)['family'] in ('root','revocation','recovery') for row in rows))
            history=self.fence.read(valid_until=self.valid_until)
            require(history.checkpoints[-1]==self.expected_head)
            # Preparation is a publicly constructible NONE dataclass. Recompute
            # semantic transitions from independently observed predecessor bytes.
            bodies={custody.reference(raw)['id']:raw for raw in history.checkpoints}
            previous=control.EncodedSnapshot(history.controls[-1],history.pages[-1])
            before=check_delegated_control(previous,bodies,{},profile='TEST_ONLY',
                protected_config=self.fence.registration.config_sha256)
            after=check_delegated_control(candidate.snapshot,bodies,{},profile='TEST_ONLY',
                protected_config=self.fence.registration.config_sha256)
            require(prepare_delegated_transition(before,after,self.expected_head,
                group=candidate.group,transition=value['transition_kind'],record_refs=value['record_refs'])==candidate)
            self.ledger.observe_current(independent_checkpoint=history.checkpoints[-1])
            # Pin retirement before first mutation: no same-object redispatch even
            # if an immutable blob/PREPARED/custody/finalization acknowledgment is lost.
            self.used=True
            self.ledger.prepare(candidate)
            objects=dict(self.fence.inventory('objects/'))
            material={control.digest(raw):raw for raw in (candidate.snapshot.root,*candidate.snapshot.pages)}
            material[records.domain_digest(records.PREFIX+'ledger-commit.v2',control.decode(candidate.descriptor))]=candidate.descriptor
            for digest,raw in sorted(material.items()):
                key=custody.NORMAL+'objects/'+digest
                if key in objects:
                    require(self.fence.retained(key,objects[key],self.valid_until)==raw)
                else:
                    self.fence.call('put_object',Key=key,Body=raw,IfNoneMatch='*',
                        ContentType='application/json',ChecksumAlgorithm='SHA256')
            history=self.fence.append(candidate.checkpoint,custody.reference(self.expected_head),
                                      valid_until=self.valid_until)
            require(history.checkpoints[-1]==candidate.checkpoint)
            self.ledger.finalize(candidate,independent_checkpoint=history.checkpoints[-1])
            history=self.fence.read(valid_until=self.valid_until)
            require(history.checkpoints[-1]==candidate.checkpoint)
            result=self.ledger.observe_current(independent_checkpoint=history.checkpoints[-1])
            self.retired=True
            return result
        except Exception:
            self.retired=True;self.ledger.quarantined=True;self.fence.quarantined=True
            raise ValueError('N01_COMMIT_QUARANTINE') from None

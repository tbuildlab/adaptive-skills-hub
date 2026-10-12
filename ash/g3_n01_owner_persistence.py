"""Bounded Owner-membership durability, always NONE and without execution.

The protected controller supplies authenticated native transports and its actual
measured deployment/process fields. Independent R source enrollment is reread;
no local approval, public dataclass or matching source hash replaces that read.
Historical TEST_ONLY SingleCommit and recovery authorizations stay unchanged.
This module cannot mint a grant, admit, claim, dispatch or enable REAL_ADMISSION.
"""
from dataclasses import replace
from datetime import datetime, timezone
import time

from ash import g3_checkpoint_custody as custody
from ash import g3_delegated_control_codec as control
from ash import g3_delegated_record_codec as records
from ash import g3_n01_public_review as review
from ash import g3_n01_source_enrollment as source
from ash import g3_n01_retained_state as retained
from ash.g3_n01_membership_custody import MembershipFence
from ash.g3_primary_ledger import DelegatedDynamoReservations
from ash.g3_transition_protocol import Preparation,prepare_delegated_transition
from ash.g3_control_semantics import require
from scripts import g3_d03_s3_fence as transport

FAMILIES=frozenset(('root','binding','context','challenge','view','decision','receipt',
                   'nonce','revocation','retirement','recovery','registration','source'))
GROUPS=frozenset(('T1','T2','T3','T5','T9'))
RECOVERY_PREFIX=custody.APPROVALS+'owner-controller-recovery-v1/'


class OwnerMembershipFence(MembershipFence):
    """Separate exact enrolled writer transport; all observations remain NONE.

The old resource registration is not promoted. A separate R-protected current
source binds the actual Owner-only writer. Owner RECOVER additionally needs one
exact R-only authorization per checkpoint; restart source mismatch denies.
"""
    def __init__(self,client,registration,*,public_review,native_environment,
                 artifact_inventory_sha256,process_nonce,max_attempts=1000,custody_revision=1):
        super().__init__(client,registration,profile='PRODUCTION',max_attempts=max_attempts)
        require(type(public_review) is review.PublicReview)
        self.public_review=public_review
        self.native_environment=native_environment
        self.artifact_inventory_sha256=artifact_inventory_sha256
        self.process_nonce=process_nonce
        require(type(custody_revision) is int and custody_revision in (1,2))
        self.custody_revision=custody_revision
        self.retired=False
        self.__write_plan=None;self.__write_used=False
    def __repr__(self):return 'OwnerMembershipFence(authority=NONE)'
    def __reduce_ex__(self,_):raise TypeError('N01_OWNER_FENCE_NOT_RESTORABLE')
    def __getstate__(self):raise TypeError('N01_OWNER_FENCE_NOT_RESTORABLE')
    def current_source(self):
        require(not self.retired and self.max_attempts-self.attempts>=4)
        # Exactly four independent version/inventory/retention reads, accounted
        # before dispatch so failure cannot make the operation budget disappear.
        self.attempts+=4
        try:
            return source.read_protected_source(self.client,self.registration,self.public_review,
                native_environment=self.native_environment,artifact_inventory_sha256=self.artifact_inventory_sha256,
                process_nonce=self.process_nonce,now_ms=int(time.time()*1000),custody_revision=self.custody_revision)
        except Exception:
            self.retired=True;self.quarantined=True
            raise ValueError('N01_OWNER_SOURCE_QUARANTINE') from None
    def call(self,operation,**kwargs):
        require(not self.retired)
        require(operation in ('list_object_versions','get_object','get_object_retention','put_object'))
        if operation=='put_object':
            require(review.FROM_MS<=int(time.time()*1000)<review.UNTIL_MS)
            require(set(kwargs)=={'Key','Body','IfNoneMatch','ContentType','ChecksumAlgorithm'})
            require(self.__write_plan is not None and kwargs.get('Key') in self.__write_plan
                and kwargs.get('Body')==self.__write_plan[kwargs['Key']]
                and kwargs.get('IfNoneMatch')=='*' and kwargs.get('ContentType')=='application/json'
                and kwargs.get('ChecksumAlgorithm')=='SHA256'
                and type(kwargs.get('Body')) is bytes and 0<len(kwargs['Body'])<=65536)
            del self.__write_plan[kwargs['Key']]  # Consume before dispatch, even on unknown ACK.
        else:require(kwargs.get('Key',kwargs.get('Prefix','')).startswith(custody.NORMAL))
        try:return transport.S3Fence.call(self,operation,**kwargs)
        except Exception:
            self.retired=True;self.__write_plan=None
            raise ValueError('N01_OWNER_CUSTODY_QUARANTINE') from None
    def _begin_write(self,material,checkpoint):
        """Internal exact one-operation plan, never a transferable authorization."""
        require(not self.__write_used and self.__write_plan is None and not self.retired)
        self.current_source()
        require(type(material) is dict and 1<=len(material)<=100)
        plan={}
        for digest,raw in material.items():
            control.old.check_type(digest,'h');control.decode(raw)
            require(type(raw) is bytes and 0<len(raw)<=65536)
            plan[custody.NORMAL+'objects/'+digest]=raw
        value=control.decode(checkpoint);custody.reference(checkpoint)
        plan[custody.NORMAL+f"journal/{value['recovery_sequence']:020d}"]=checkpoint
        self.__write_plan=plan;self.__write_used=True
    def read(self,*,valid_until):
        self.current_source()
        return super().read(valid_until=valid_until)
    def independent_recovery_authorization(self,body,ref,valid_until):
        if body['recovery_sequence']<=2:
            return custody.N01S3Fence.independent_recovery_authorization(self,body,ref,valid_until)
        enrolled=self.current_source()
        require(body['incarnation']=='n01-owner-'+enrolled.value['process_nonce'][:32])
        base=RECOVERY_PREFIX if self.custody_revision==1 else custody.APPROVALS+'owner-controller-recovery-v2/'
        prefix=base+f"{body['recovery_sequence']:020d}/"
        remaining=self.max_attempts-self.attempts
        require(remaining>=4)
        protected=custody.N01S3Fence(self.client,replace(self.registration,prefix=prefix),max_attempts=remaining)
        try:
            inventory=protected.inventory('')
            require(len(inventory)==1 and inventory[0][0]==prefix+'authorization.json')
            raw=protected.retained(*inventory[0],valid_until)
            expected=dict(schema_version='nexus.g3.n01.owner-recovery-authorization.v1',
                purpose='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY',authority_mode=records.MODE,
                authority_config_sha256=self.registration.config_sha256,
                source_enrollment_sha256=enrolled.enrollment_sha256,
                checkpoint=ref,previous_checkpoint=body['previous_checkpoint'],
                authority_epoch=body['authority_epoch'],incarnation=body['incarnation'],
                application_generation=1,review_generation=1,expires_at_ms=review.UNTIL_MS,
                no_automatic_redispatch='REQUIRED',real_admission='NO')
            require(control.decode(raw)==expected and protected.inventory('')==inventory)
        finally:self.attempts+=protected.attempts
    def append(self,raw,expected_head,*,valid_until):
        self.current_source()
        return transport.S3Fence.append(self,raw,expected_head,valid_until=valid_until)
    def reconcile(self,*,valid_until):
        return transport.S3Fence.reconcile(self,valid_until=valid_until)
    def append_recovery(self,raw,expected_head,*,valid_until):
        require(self.pending is None)
        body=control.decode(raw);ref=custody.reference(raw)
        require(body['transition_kind']=='RECOVER' and ref['id'] in self.registration.admin_checkpoint_ids)
        history=self.read(valid_until=valid_until)
        require(history.head==expected_head and body['previous_checkpoint']==expected_head)
        previous=control.decode(history.checkpoints[-1])
        require(body['authority_instance']==previous['authority_instance']==custody.INSTANCE)
        require(body['recovery_sequence']==previous['recovery_sequence']+1
                and body['authority_epoch']==previous['authority_epoch']+1
                and body['incarnation']!=previous['incarnation']
                and body['time_high_water_ms']>=previous['time_high_water_ms'])
        self.independent_recovery_authorization(body,ref,valid_until)
        # The coordinator rederives all complete candidate semantics and retains
        # material first. The journal still admits one exact conditional append.
        self.pending=raw
        self.call('put_object',Key=custody.NORMAL+f"journal/{body['recovery_sequence']:020d}",Body=raw,
            IfNoneMatch='*',ContentType='application/json',ChecksumAlgorithm='SHA256')
        return self.reconcile(valid_until=valid_until)


class OwnerMembershipCommit:
    """One non-authorizing, non-restorable durability operation; unknown retires."""
    def __init__(self,ledger,fence,*,expected_head,valid_until):
        require(type(ledger) is DelegatedDynamoReservations and type(fence) is OwnerMembershipFence)
        require(ledger.instance==custody.INSTANCE==fence.registration.authority_instance)
        custody.reference(expected_head)
        require(type(valid_until) is datetime and valid_until.tzinfo is not None
                and datetime.now(timezone.utc)<valid_until<=datetime.fromtimestamp(review.UNTIL_MS/1000,timezone.utc))
        self.ledger=ledger;self.fence=fence;self.expected_head=expected_head;self.valid_until=valid_until
        self.used=False;self.retired=False
    @property
    def authority(self):return 'NONE'
    def __repr__(self):return 'OwnerMembershipCommit(authority=NONE)'
    def __reduce_ex__(self,_):raise TypeError('N01_OWNER_COMMIT_NOT_RESTORABLE')
    def __getstate__(self):raise TypeError('N01_OWNER_COMMIT_NOT_RESTORABLE')
    def commit(self,candidate,*,objects):
        try:
            require(not self.used and not self.retired and type(candidate) is Preparation)
            require(candidate.expected_checkpoint==self.expected_head and candidate.group in GROUPS)
            value=control.decode(candidate.checkpoint)
            require(value['transition_kind']!='GENESIS'
                    and value['authority_config_sha256']==self.fence.registration.config_sha256)
            require(type(objects) is dict and len(objects)<=32)
            for digest,raw in objects.items():
                require(type(raw) is bytes and 0<len(raw)<=65536 and control.digest(raw)==digest)
                control.decode(raw)
            history=self.fence.read(valid_until=self.valid_until)
            require(history.checkpoints[-1]==self.expected_head)
            enrolled=self.fence.current_source()
            rows=control.verify_snapshot(candidate.snapshot)
            require(all(control.decode(row.value)['family'] in FAMILIES for row in rows))
            prior_rows={row.key:control.decode(row.value) for row in history.states[-1].checked.rows}
            next_rows={row.key:control.decode(row.value) for row in rows}
            # T1 creates one single-challenge context atomically, not an orphan
            # reusable login record via a registration or invalidation operation.
            for key,item in next_rows.items():
                if item['family']=='context' and key not in prior_rows and item['state']=='CURRENT':
                    require(candidate.group=='T1')
                    challenges=[row for row in next_rows.values() if row['family']=='challenge'
                                and row['context_id']==item['context_id'] and row['state']=='PENDING']
                    require(len(challenges)==1)
                    challenge=challenges[0]
                    require('challenge:'+challenge['challenge_id'] not in prior_rows
                            and 'view:'+challenge['view_id'] not in prior_rows
                            and 'nonce:'+challenge['nonce'] not in prior_rows)
                if item['family']=='context' and item['state']=='CONSUMED' and prior_rows.get(key,{}).get('state')=='CURRENT':
                    require(candidate.group=='T3' and value['transition_kind'] in ('CONFIRM','DENY'))
                    decisions=[row for row in next_rows.values() if row['family']=='decision'
                               and row['context_id']==item['context_id'] and row['choice']==value['transition_kind']]
                    require(len(decisions)==1 and 'decision:'+decisions[0]['challenge_id'] not in prior_rows)
            for row in rows:
                item=control.decode(row.value)
                if item['family']=='source':
                    require(item['kind'] in enrolled.value['source_kinds']
                        and item['principal']==enrolled.value['principal'])
                if item['family']=='binding':require(item['principal']==enrolled.value['principal'])
                if item['family']=='context':
                    require(item['provider_project']==enrolled.value['principal']['client_id']
                            and item['provider_user']==enrolled.value['principal']['subject'])
            combined=dict(history.objects)
            require(all(digest not in combined or combined[digest]==raw for digest,raw in objects.items()))
            combined.update(objects)
            after=retained.resolve_retained_state(candidate.snapshot,history.checkpoints,combined,
                profile='PRODUCTION',config_sha256=self.fence.registration.config_sha256)
            require(prepare_delegated_transition(history.states[-1].checked,after.checked,self.expected_head,
                group=candidate.group,transition=value['transition_kind'],record_refs=value['record_refs'])==candidate)
            # Unreferenced payloads cannot be retained through this writer. Exact
            # source provenance still belongs to the protected enrolled controller.
            referenced={control.digest(raw) for _,raw in (*after.bodies,*after.evidence,*after.assertions)}
            require(set(objects)<=referenced)
            if value['transition_kind']=='RECOVER':
                self.fence.independent_recovery_authorization(value,custody.reference(candidate.checkpoint),self.valid_until)
            self.ledger.observe_current(independent_checkpoint=self.expected_head)
            material=dict(objects)
            material.update({control.digest(raw):raw for raw in (candidate.snapshot.root,*candidate.snapshot.pages)})
            material[records.domain_digest(records.PREFIX+'ledger-commit.v2',control.decode(candidate.descriptor))]=candidate.descriptor
            self.fence._begin_write(material,candidate.checkpoint)
            self.used=True  # Before any mutation; never resend an ambiguous operation.
            for _,raw in sorted(objects.items()):self.ledger.retain_blob(raw)
            self.ledger.prepare(candidate)
            inventory=dict(self.fence.inventory('objects/'))
            for digest,raw in sorted(material.items()):
                key=custody.NORMAL+'objects/'+digest
                if key in inventory:require(self.fence.retained(key,inventory[key],self.valid_until)==raw)
                else:self.fence.call('put_object',Key=key,Body=raw,IfNoneMatch='*',ContentType='application/json',ChecksumAlgorithm='SHA256')
            append=self.fence.append_recovery if value['transition_kind']=='RECOVER' else self.fence.append
            history=append(candidate.checkpoint,custody.reference(self.expected_head),valid_until=self.valid_until)
            require(history.checkpoints[-1]==candidate.checkpoint)
            self.ledger.finalize(candidate,independent_checkpoint=history.checkpoints[-1])
            history=self.fence.read(valid_until=self.valid_until)
            require(history.checkpoints[-1]==candidate.checkpoint)
            result=self.ledger.observe_current(independent_checkpoint=history.checkpoints[-1])
            self.retired=True
            return result
        except Exception:
            self.retired=True;self.ledger.quarantined=True;self.fence.quarantined=True;self.fence.retired=True
            raise ValueError('N01_OWNER_MEMBERSHIP_COMMIT_QUARANTINE') from None

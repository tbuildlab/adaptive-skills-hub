"""Thin DynamoDB reservation transport, not an authority service.

Uses immutable closed codec blobs and a single conditional N01 head. No retry,
restore, dispatcher or positive acknowledgment is inferred from primary storage.
Independent current-history verification is required for each finalization/read.
Actual deployment, writer/source provenance and N01 ingress remain unqualified.
"""
from dataclasses import dataclass
from functools import wraps
import re
from ash import g3_control_codec as c, g3_record_codec as r
from ash.g3_transition_protocol import Preparation, checkpoint_ref


class LedgerError(ValueError):
    """Fixed sanitized fail-closed outcome, without SDK messages/credentials."""


def require(condition):
    if not condition:
        raise LedgerError("G3_LEDGER_QUARANTINE")


def _closed(method):
    @wraps(method)
    def guarded(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except Exception:
            self.quarantined=True
            raise LedgerError("G3_LEDGER_QUARANTINE") from None
    return guarded


@dataclass(frozen=True)
class PrimaryObservation:
    checkpoint: bytes
    phase: str

    @property
    def authority(self):
        return "NONE"


class DynamoReservations:
    """Fixed table/instance transport; creation and credentials are external."""
    def __init__(self, client, *, table_arn, instance, max_attempts):
        require(type(table_arn) is str and re.fullmatch(
            r'arn:aws:dynamodb:ap-southeast-1:175880707430:table/NexusG3AuthorityV1',table_arn))
        c.check_type(instance,"t")
        require(type(max_attempts) is int and 1 <= max_attempts <= 5000)
        require(client.meta.config.retries.get("total_max_attempts") == 1)
        self.client=client;self.table=table_arn;self.instance=instance
        self.max_attempts=max_attempts;self.attempts=0;self.quarantined=True
        self.control_codec=c;self.record_codec=r;self.record_version=1

    def checkpoint_ref(self, raw):
        parsed=self.record_codec.parse_metadata(raw)
        require(parsed.to_dict()['schema_version']==r.PREFIX+f'recovery-checkpoint.v{self.record_version}')
        return dict(id=parsed.record_id,body_sha256=parsed.body_sha256)

    def _call(self, operation, **kwargs):
        if self.attempts >= self.max_attempts:
            self.quarantined=True
            raise LedgerError("G3_LEDGER_QUARANTINE")
        self.attempts+=1
        try:
            return getattr(self.client,operation)(**kwargs)
        except Exception:
            self.quarantined=True
            raise LedgerError("G3_LEDGER_QUARANTINE") from None

    def _key(self, sort):
        return {'pk':{'S':'authority#'+self.instance},'sk':{'S':sort}}

    def _get(self, sort):
        result=self._call('get_item',TableName=self.table,Key=self._key(sort),ConsistentRead=True)
        require(type(result) is dict)
        return result.get('Item')

    @_closed
    def retain_blob(self, raw):
        require(type(raw) is bytes and 0 < len(raw) <= 65536)
        c.decode(raw)  # Canonical closed control/record checks happen at preparation.
        sort='blob#'+c.digest(raw);existing=self._get(sort)
        item=dict(self._key(sort),body={'B':raw})
        if existing is not None:
            require(existing==item)
            return sort
        # Unknown write outcome is never retried. Reconciliation is read-only.
        self._call('put_item',TableName=self.table,Item=item,ConditionExpression='attribute_not_exists(pk)')
        require(self._get(sort)==item)
        return sort

    def _retained(self, raw):
        item=self._get('blob#'+c.digest(raw))
        require(item==dict(self._key('blob#'+c.digest(raw)),body={'B':raw}))

    def _retain_candidate(self, raws):
        for raw in raws:self.retain_blob(raw)

    def _check_material(self, raws):
        for raw in raws:self._retained(raw)

    @_closed
    def enroll_genesis(self, checkpoint, snapshot):
        """Primary enrollment only. Requires independent admin/fence outside API."""
        require(self._get('HEAD') is None)
        value=self.record_codec.parse_metadata(checkpoint).to_dict();self.checkpoint_ref(checkpoint)
        require(value['transition_kind']=='GENESIS' and value['authority_instance']==self.instance)
        self.control_codec.verify_snapshot(snapshot)
        header=c.decode(snapshot.root)
        require(all(value[key]==header[key] for key in ('authority_instance','authority_epoch',
            'incarnation','recovery_sequence','time_high_water_ms')))
        descriptor={key:v for key,v in value.items() if key not in ('schema_version','ledger_commit_sha256')}
        descriptor['control_after_sha256']=snapshot.control_after_sha256
        require(self.record_codec.domain_digest(r.PREFIX+f'ledger-commit.v{self.record_version}',descriptor)==value['ledger_commit_sha256'])
        for raw in (checkpoint,snapshot.root,*snapshot.pages,r.canonical_bytes(descriptor)):
            self.retain_blob(raw)
        item=dict(self._key('HEAD'),phase={'S':'READY'},checkpoint={'B':checkpoint},sequence={'N':'0'})
        self._call('put_item',TableName=self.table,Item=item,ConditionExpression='attribute_not_exists(pk)')
        # Startup remains quarantined: matching primary bytes are not recovery proof.
        require(self._get('HEAD')==item)
        return PrimaryObservation(checkpoint,'PRIMARY_ENROLLED_UNQUALIFIED')

    @_closed
    def prepare(self, candidate):
        require(not self.quarantined and type(candidate) is Preparation)
        prior=self.record_codec.parse_metadata(candidate.expected_checkpoint).to_dict()
        current=self.record_codec.parse_metadata(candidate.checkpoint).to_dict()
        require(current['authority_instance']==prior['authority_instance']==self.instance)
        require(current['recovery_sequence']==prior['recovery_sequence']+1)
        require(current['previous_checkpoint']==self.checkpoint_ref(candidate.expected_checkpoint))
        self.control_codec.verify_snapshot(candidate.snapshot)
        header=c.decode(candidate.snapshot.root)
        require(all(current[key]==header[key] for key in ('authority_instance','authority_epoch',
            'incarnation','recovery_sequence','time_high_water_ms')))
        if self.record_version == 2:
            roots=[c.decode(row.value) for row in self.control_codec.verify_snapshot(candidate.snapshot)
                   if c.decode(row.value)['family']=='root']
            require(all(current[field]==prior[field]==roots[0][field]
                        for field in self.record_codec.CONFIG_FIELDS.split()))
        descriptor=c.decode(candidate.descriptor)
        require(self.record_codec.domain_digest(r.PREFIX+f'ledger-commit.v{self.record_version}',descriptor)==current['ledger_commit_sha256'])
        require(descriptor['control_after_sha256']==candidate.snapshot.control_after_sha256)
        require({key:v for key,v in descriptor.items() if key!='control_after_sha256'}==
                {key:v for key,v in current.items() if key not in ('schema_version','ledger_commit_sha256')})
        self._retain_candidate((candidate.checkpoint,candidate.descriptor,candidate.snapshot.root,*candidate.snapshot.pages))
        sort='reservation#'+f"{current['recovery_sequence']:020d}"
        reservation=dict(self._key(sort),phase={'S':'PREPARED'},
            expected_checkpoint={'B':candidate.expected_checkpoint},checkpoint={'B':candidate.checkpoint},
            descriptor={'B':candidate.descriptor},root={'B':candidate.snapshot.root},
            pages={'L':[{'S':c.digest(page)} for page in candidate.snapshot.pages]})
        # Pages are immutable retained blobs. References, not multi-megabyte page
        # contents, occupy the <=400 KiB reservation; all 64 codec pages fit.
        require(sum(len(raw) for raw in (candidate.checkpoint,candidate.descriptor,
            candidate.snapshot.root))<=3*65536)
        self.quarantined=True  # Before sending: any ambiguous ACK closes release.
        self._call('transact_write_items',ClientRequestToken=candidate.reservation_digest[:36],
            TransactItems=[{'Put':{'TableName':self.table,'Item':reservation,
                'ConditionExpression':'attribute_not_exists(pk)'}},
                {'Update':{'TableName':self.table,'Key':self._key('HEAD'),
                    'UpdateExpression':'SET #phase = :prepared, pending = :next',
                    'ConditionExpression':'#phase = :ready AND checkpoint = :old AND #sequence = :sequence',
                    'ExpressionAttributeNames':{'#phase':'phase','#sequence':'sequence'},
                    'ExpressionAttributeValues':{':prepared':{'S':'PREPARED'},':ready':{'S':'READY'},
                        ':next':{'B':candidate.checkpoint},':old':{'B':candidate.expected_checkpoint},
                        ':sequence':{'N':str(prior['recovery_sequence'])}}}}])
        require(self._get(sort)==reservation)
        return PrimaryObservation(candidate.checkpoint,'PREPARED_QUARANTINED')

    @_closed
    def observe_current(self, *, independent_checkpoint):
        """Exact current independent bytes; caller must authenticate their origin.

        Does not reopen after an outstanding reservation or reconcile a write.
        This transport observation returns NONE even if bytes are equal.
        """
        self.checkpoint_ref(independent_checkpoint)
        item=self._get('HEAD')
        expected=self.record_codec.parse_metadata(independent_checkpoint).to_dict()
        require(item==dict(self._key('HEAD'),phase={'S':'READY'},checkpoint={'B':independent_checkpoint},
            sequence={'N':str(expected['recovery_sequence'])}))
        require(expected['authority_instance']==self.instance)
        self._retained(independent_checkpoint)
        self.quarantined=False
        return PrimaryObservation(independent_checkpoint,'PRIMARY_MATCHES_INDEPENDENT_BYTES_UNQUALIFIED')

    @_closed
    def finalize(self, candidate, *, independent_checkpoint):
        """Finalize exact reservation only; never acknowledge authority or an effect."""
        require(type(candidate) is Preparation and independent_checkpoint==candidate.checkpoint)
        self.checkpoint_ref(independent_checkpoint)
        value=self.record_codec.parse_metadata(candidate.checkpoint).to_dict()
        require(value['authority_instance']==self.instance)
        sort='reservation#'+f"{value['recovery_sequence']:020d}"
        expected=dict(self._key(sort),phase={'S':'PREPARED'},
            expected_checkpoint={'B':candidate.expected_checkpoint},checkpoint={'B':candidate.checkpoint},
            descriptor={'B':candidate.descriptor},root={'B':candidate.snapshot.root},
            pages={'L':[{'S':c.digest(page)} for page in candidate.snapshot.pages]})
        require(self._get(sort)==expected)
        self._check_material((candidate.checkpoint,candidate.descriptor,candidate.snapshot.root,*candidate.snapshot.pages))
        self.quarantined=True
        self._call('transact_write_items',ClientRequestToken=('f'+candidate.reservation_digest)[:36],
            TransactItems=[{'Update':{'TableName':self.table,'Key':self._key(sort),
                'UpdateExpression':'SET #phase = :finalized',
                'ConditionExpression':'#phase = :prepared AND checkpoint = :next',
                'ExpressionAttributeNames':{'#phase':'phase'},
                'ExpressionAttributeValues':{':prepared':{'S':'PREPARED'},':finalized':{'S':'FINALIZED'},':next':{'B':candidate.checkpoint}}}},
                {'Update':{'TableName':self.table,'Key':self._key('HEAD'),
                    'UpdateExpression':'SET #phase = :ready, checkpoint = :next, #sequence = :sequence REMOVE pending',
                    'ConditionExpression':'#phase = :prepared AND checkpoint = :old AND pending = :next',
                    'ExpressionAttributeNames':{'#phase':'phase','#sequence':'sequence'},
                    'ExpressionAttributeValues':{':prepared':{'S':'PREPARED'},':ready':{'S':'READY'},
                        ':old':{'B':candidate.expected_checkpoint},':next':{'B':candidate.checkpoint},
                        ':sequence':{'N':str(value['recovery_sequence'])}}}}])
        # Remain closed until a separate fresh independent-current observation.
        return PrimaryObservation(candidate.checkpoint,'FINALIZED_RECHECK_REQUIRED')


class DelegatedDynamoReservations(DynamoReservations):
    """Exact v2 transport. Config bytes/source origin still cannot create authority."""
    def __init__(self, client, *, table_arn, instance, max_attempts, atomic_reads=False):
        super().__init__(client,table_arn=table_arn,instance=instance,max_attempts=max_attempts)
        from ash import g3_delegated_control_codec as modern_control
        from ash import g3_delegated_record_codec as modern_records
        self.control_codec=modern_control
        self.record_codec=modern_records
        self.record_version=2
        require(type(atomic_reads) is bool)
        self.atomic_reads=atomic_reads

    def _retain_candidate(self, raws):
        if self.atomic_reads:return self.retain_blobs(raws)
        return super()._retain_candidate(raws)

    def _check_material(self, raws):
        if self.atomic_reads:return self._retained_many(raws)
        return super()._check_material(raws)

    @_closed
    def observe_current(self, *, independent_checkpoint):
        if not self.atomic_reads:return super().observe_current(independent_checkpoint=independent_checkpoint)
        self.checkpoint_ref(independent_checkpoint)
        expected=self.record_codec.parse_metadata(independent_checkpoint).to_dict()
        head,blob=self._pair_get(('HEAD','blob#'+c.digest(independent_checkpoint)))
        require(head==dict(self._key('HEAD'),phase={'S':'READY'},checkpoint={'B':independent_checkpoint},
            sequence={'N':str(expected['recovery_sequence'])}))
        require(expected['authority_instance']==self.instance)
        require(blob==dict(self._key('blob#'+c.digest(independent_checkpoint)),body={'B':independent_checkpoint}))
        self.quarantined=False
        return PrimaryObservation(independent_checkpoint,'PRIMARY_MATCHES_INDEPENDENT_BYTES_UNQUALIFIED')

    def _pair_get(self, sorts):
        """Fresh serializable observation, at most two fixed-instance items."""
        require(type(sorts) is tuple and 1<=len(sorts)<=2 and len(set(sorts))==len(sorts))
        require(all(type(sort) is str and 0<len(sort)<=128 for sort in sorts))
        result=self._call('transact_get_items',TransactItems=[
            {'Get':{'TableName':self.table,'Key':self._key(sort)}} for sort in sorts])
        require(type(result) is dict and type(result.get('Responses')) is list
                and len(result['Responses'])==len(sorts))
        items=[]
        for sort,row in zip(sorts,result['Responses']):
            require(row is None or type(row) is dict and set(row)<= {'Item'})
            item=None if row is None else row.get('Item')
            if item is not None:
                require(type(item) is dict and all(item.get(key)==value for key,value in self._key(sort).items()))
            items.append(item)
        return tuple(items)

    @_closed
    def retain_blobs(self, raws):
        """Same immutable pre/write/post checks; no observation survives return."""
        require(type(raws) is tuple and 1<=len(raws)<=68)
        expected={}
        for raw in raws:
            require(type(raw) is bytes and 0<len(raw)<=65536);c.decode(raw)
            sort='blob#'+c.digest(raw)
            item=dict(self._key(sort),body={'B':raw})
            require(sort not in expected or expected[sort]==item);expected[sort]=item
        for start in range(0,len(expected),2):
            sorts=tuple(expected)[start:start+2]
            before=self._pair_get(sorts)
            missing=[]
            for sort,item in zip(sorts,before):
                require(item is None or item==expected[sort])
                if item is None:missing.append(sort)
            for sort in missing:
                self._call('put_item',TableName=self.table,Item=expected[sort],ConditionExpression='attribute_not_exists(pk)')
            if missing:
                after=self._pair_get(tuple(missing))
                require(all(item==expected[sort] for sort,item in zip(missing,after)))

    @_closed
    def _retained_many(self, raws):
        require(type(raws) is tuple and 1<=len(raws)<=68)
        expected={}
        for raw in raws:
            require(type(raw) is bytes and 0<len(raw)<=65536);c.decode(raw)
            sort='blob#'+c.digest(raw);item=dict(self._key(sort),body={'B':raw})
            require(sort not in expected or expected[sort]==item);expected[sort]=item
        for start in range(0,len(expected),2):
            sorts=tuple(expected)[start:start+2]
            require(all(item==expected[sort] for sort,item in zip(sorts,self._pair_get(sorts))))

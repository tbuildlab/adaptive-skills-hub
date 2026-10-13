"""Fixed native OIDC/SDK transport for the existing bounded N01 resources.

No credential discovery, URL selection, environment enumeration, resource
creation or admission. Temporary credentials stay inside maintained SDK clients.
Write access additionally requires a fresh independently retained Owner-source
read; that constraint does not turn a transport response into authority.
"""
import time
import threading
from ash import g3_checkpoint_custody as custody
from ash import g3_n01_controller_bootstrap as boot
from ash import g3_n01_public_review as review
from ash import g3_n01_source_enrollment as source
from ash.g3_control_semantics import require

TABLE='arn:aws:dynamodb:ap-southeast-1:175880707430:table/NexusG3AuthorityV1'
MAX_DDB=256
MAX_S3=8000
MAX_S3_WRITES=256
MAX_WRITE_BYTES=16777216
_BUDGET={'leases':0,'ddb':0,'s3':0,'s3_writes':0,'s3_bytes':0,'ddb_bytes':0}
_LOCK=threading.Lock()


def _size(value,depth=0):
    require(depth<=16)
    if type(value) is bytes:return len(value)+16
    if type(value) is str:return len(value.encode('utf-8'))+16
    if type(value) is dict:
        require(len(value)<=128 and all(type(key) is str for key in value))
        return 64+sum(_size(key,depth+1)+_size(child,depth+1) for key,child in value.items())
    if type(value) is list:
        require(len(value)<=128)
        return 64+sum(_size(child,depth+1) for child in value)
    require(value is None or type(value) in (bool,int));return 16


class NativeTransport:
    """NONE and non-restorable. One process budget; unknown retires all clients."""
    def __init__(self,native_header,*,review_generation=1,review_profile=None):
        import boto3
        from botocore.config import Config
        from botocore import UNSIGNED
        require(type(native_header) is str and native_header.isascii() and 0<len(native_header)<=16384)
        self.__clients=[];self.__ddb=None;self.__s3=None;self.__write=False;self.retired=False
        self.__review=review.select_pins(review_generation,restart_profile=review_profile)
        self.sts_attempts=0
        cfg=Config(retries={'total_max_attempts':1},connect_timeout=5,read_timeout=10)
        unsigned=Config(signature_version=UNSIGNED,retries={'total_max_attempts':1},connect_timeout=5,read_timeout=10)
        def client(service,credentials):
            item=boto3.client(service,region_name='ap-southeast-1',config=cfg,
                aws_access_key_id=credentials['AccessKeyId'],aws_secret_access_key=credentials['SecretAccessKey'],
                aws_session_token=credentials['SessionToken'])
            self.__clients.append(item);return item
        try:
            require(self.__review.valid_from_ms<=int(time.time()*1000)<self.__review.valid_until_ms)
            with _LOCK:
                require(_BUDGET['leases']<8);_BUDGET['leases']+=1
            initial=boto3.client('sts',region_name='us-east-1',config=unsigned);self.__clients.append(initial)
            self.sts_attempts+=1
            a=initial.assume_role_with_web_identity(RoleArn=boot.A,RoleSessionName='NexusG3N01Vercel',
                WebIdentityToken=native_header,DurationSeconds=900)
            sts=client('sts',a['Credentials']);self.sts_attempts+=1
            ident=sts.get_caller_identity()
            require(ident['Account']=='175880707430' and ident['Arn']==
                'arn:aws:sts::175880707430:assumed-role/NexusG3QualificationCaller/NexusG3N01Vercel')
            self.sts_attempts+=1
            r=sts.assume_role(RoleArn=boot.R,RoleSessionName='NexusG3N01Custody',DurationSeconds=900)
            self.sts_attempts+=1
            ident=client('sts',r['Credentials']).get_caller_identity()
            require(ident['Account']=='862902859484' and ident['Arn']==
                'arn:aws:sts::862902859484:assumed-role/NexusG3N01AppendRead/NexusG3N01Custody')
            self.__ddb=client('dynamodb',a['Credentials']);self.__s3=client('s3',r['Credentials'])
            self.primary=PrimaryClient(self);self.custody=CustodyClient(self)
        except Exception:
            self.close();raise ValueError('N01_NATIVE_TRANSPORT_QUARANTINE') from None
    @property
    def authority(self):return 'NONE'
    @property
    def ddb_attempts(self):return _BUDGET['ddb']
    @property
    def s3_attempts(self):return _BUDGET['s3']
    def __repr__(self):return 'NativeTransport(authority=NONE)'
    def __reduce_ex__(self,_):raise TypeError('N01_NATIVE_TRANSPORT_NOT_RESTORABLE')
    def __getstate__(self):raise TypeError('N01_NATIVE_TRANSPORT_NOT_RESTORABLE')
    def enable_owner_storage(self,public_review,*,native_environment,artifact_inventory_sha256,process_nonce,custody_revision=1,restart_profile=None):
        try:
            require(not self.retired and not self.__write)
            if self.__review.generation>=2:require(type(public_review) is review.PublicReview and public_review.pins==self.__review)
            enrollment=source.read_protected_source(self.custody,boot.storage_scope(),public_review,
                native_environment=native_environment,artifact_inventory_sha256=artifact_inventory_sha256,
                process_nonce=process_nonce,now_ms=int(time.time()*1000),custody_revision=custody_revision,
                **({} if restart_profile is None else {'restart_profile':restart_profile}))
            self.__write=True
            return enrollment
        except Exception:
            self.close();raise ValueError('N01_NATIVE_WRITE_ENROLLMENT_QUARANTINE') from None
    def _call(self,service,operation,kwargs):
        try:
            require(not self.retired and self.__review.valid_from_ms<=int(time.time()*1000)<self.__review.valid_until_ms)
            if service=='s3':
                require(operation in ('list_object_versions','get_object','get_object_retention','put_object'))
                require(kwargs.get('Bucket')==boot.storage_scope().bucket and kwargs.get('ExpectedBucketOwner')=='862902859484')
                key=kwargs.get('Key',kwargs.get('Prefix',''))
                require(type(key) is str and key.startswith((custody.NORMAL,custody.APPROVALS))
                        and not any(part in key for part in ('..','//','\\')))
                if operation=='put_object':
                    require(self.__write and key.startswith(custody.NORMAL)
                        and set(kwargs)=={'Bucket','ExpectedBucketOwner','Key','Body','IfNoneMatch','ContentType','ChecksumAlgorithm'}
                        and kwargs['IfNoneMatch']=='*' and kwargs['ContentType']=='application/json'
                        and kwargs['ChecksumAlgorithm']=='SHA256' and type(kwargs['Body']) is bytes
                        and 0<len(kwargs['Body'])<=65536)
                with _LOCK:
                    require(_BUDGET['s3']<MAX_S3)
                    if operation=='put_object':
                        require(_BUDGET['s3_writes']<MAX_S3_WRITES)
                        size=len(kwargs['Body']);require(_BUDGET['s3_bytes']+size<=MAX_WRITE_BYTES)
                        _BUDGET['s3_bytes']+=size;_BUDGET['s3_writes']+=1
                    _BUDGET['s3']+=1
                client=self.__s3
            else:
                require(service=='dynamodb' and operation in ('get_item','put_item','transact_write_items','transact_get_items'))
                if operation=='get_item':
                    require(kwargs.get('TableName')==TABLE and kwargs.get('ConsistentRead') is True)
                    require(kwargs.get('Key',{}).get('pk')=={'S':'authority#'+custody.INSTANCE})
                elif operation=='transact_get_items':
                    require(set(kwargs)=={'TransactItems'})
                    items=kwargs['TransactItems'];require(type(items) is list and 1<=len(items)<=2)
                    keys=[]
                    for item in items:
                        require(type(item) is dict and set(item)=={'Get'})
                        value=item['Get'];require(type(value) is dict and set(value)=={'TableName','Key'} and value['TableName']==TABLE)
                        key=value['Key'];require(type(key) is dict and set(key)=={'pk','sk'}
                            and key['pk']=={'S':'authority#'+custody.INSTANCE}
                            and type(key['sk']) is dict and set(key['sk'])=={'S'}
                            and type(key['sk']['S']) is str and 0<len(key['sk']['S'])<=128)
                        keys.append(key['sk']['S'])
                    require(len(keys)==len(set(keys)))
                elif operation=='put_item':
                    require(self.__write and kwargs.get('TableName')==TABLE and kwargs.get('ConditionExpression')=='attribute_not_exists(pk)')
                    require(kwargs.get('Item',{}).get('pk')=={'S':'authority#'+custody.INSTANCE})
                    require(_size(kwargs['Item'])<=400000)
                else:
                    require(self.__write and set(kwargs)=={'ClientRequestToken','TransactItems'})
                    items=kwargs['TransactItems'];require(type(items) is list and len(items)==2)
                    for item in items:
                        require(type(item) is dict and len(item)==1 and set(item)<= {'Put','Update'})
                        value=next(iter(item.values()))
                        require(value.get('TableName')==TABLE)
                        row=value.get('Item',value.get('Key',{}))
                        require(row.get('pk')=={'S':'authority#'+custody.INSTANCE})
                        require(_size(value)<=400000)
                with _LOCK:
                    require(_BUDGET['ddb']<MAX_DDB)
                    if operation not in ('get_item','transact_get_items'):
                        size=_size(kwargs);require(_BUDGET['ddb_bytes']+size<=MAX_WRITE_BYTES)
                        _BUDGET['ddb_bytes']+=size
                    _BUDGET['ddb']+=1
                client=self.__ddb
            return getattr(client,operation)(**kwargs)
        except Exception:
            self.close();raise ValueError('N01_NATIVE_TRANSPORT_QUARANTINE') from None
    def close(self):
        self.retired=True;self.__write=False
        for client in self.__clients:
            try:client.close()
            except Exception:pass
        self.__clients=[];self.__ddb=None;self.__s3=None
    def _meta(self,service):
        require(not self.retired)
        return (self.__ddb if service=='dynamodb' else self.__s3).meta


class PrimaryClient:
    """Only the existing primary-ledger operations; no raw client getter."""
    def __init__(self,parent):self.__parent=parent
    @property
    def meta(self):return self.__parent._meta('dynamodb')
    def get_item(self,**kwargs):return self.__parent._call('dynamodb','get_item',kwargs)
    def put_item(self,**kwargs):return self.__parent._call('dynamodb','put_item',kwargs)
    def transact_write_items(self,**kwargs):return self.__parent._call('dynamodb','transact_write_items',kwargs)
    def transact_get_items(self,**kwargs):return self.__parent._call('dynamodb','transact_get_items',kwargs)


class CustodyClient:
    """Only the existing retained-custody operations; no raw client getter."""
    def __init__(self,parent):self.__parent=parent
    @property
    def meta(self):return self.__parent._meta('s3')
    def list_object_versions(self,**kwargs):return self.__parent._call('s3','list_object_versions',kwargs)
    def get_object(self,**kwargs):return self.__parent._call('s3','get_object',kwargs)
    def get_object_retention(self,**kwargs):return self.__parent._call('s3','get_object_retention',kwargs)
    def put_object(self,**kwargs):return self.__parent._call('s3','put_object',kwargs)

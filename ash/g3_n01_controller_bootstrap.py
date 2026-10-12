"""Native current-source bootstrap, without identity credentials or authority.

Only artifact measurement, exact existing federation and retained public review
are performed. A process nonce is never restored. Enrollment and live Owner
context still require independently protected registration and later composition.
"""
from pathlib import PurePosixPath
import hashlib
import json
import secrets
import time

from ash import g3_checkpoint_custody as custody
from ash import g3_delegated_control_codec as codec
from ash import g3_n01_public_review as review
from ash import g3_n01_source_enrollment as source
from ash.g3_control_semantics import require

PROCESS_NONCE=secrets.token_hex(32)
GENESIS_ID='nexus.g3.production.recovery-checkpoint.v2:ca736f0ab3d739456f41f6107f1582941c071835b6ca05c8f98e624b64e61f50'
# Exact accepted genesis bytes, not a new or reconstructed lineage.
GENESIS_SHA='7fe0fb527ce2c8bb519a0f837124bfce22ce8e964008f2aa0fc7b4f1c9b036db'
HEAD_ID='nexus.g3.production.recovery-checkpoint.v2:2324a4475c42debe0a21e2b94cd42f1c3d68e9dc1af0397223dfdde4a4076281'
A='arn:aws:iam::175880707430:role/NexusG3QualificationCaller'
R='arn:aws:iam::862902859484:role/NexusG3N01AppendRead'


def storage_scope():
    return custody.Registration('nexus-d03-custody-862902859484-ap-southeast-1-v1',
        '862902859484',custody.NORMAL,custody.INSTANCE,2,GENESIS_ID,GENESIS_SHA,
        (GENESIS_ID,HEAD_ID),review.CONFIG)


def measure_artifact(root,expected_manifest_sha256):
    """Measure every inventoried source plus the exact loader/manifest bytes."""
    raw=(root/'source-inventory.json').read_bytes()
    require(0<len(raw)<=65536 and hashlib.sha256(raw).hexdigest()==expected_manifest_sha256)
    inventory=json.loads(raw)
    require(type(inventory) is dict and 1<=len(inventory)<=64)
    measured={}
    for name,entry in inventory.items():
        require(type(name) is str and not PurePosixPath(name).is_absolute()
            and all(part not in ('..','.','') for part in name.split('/'))
            and '\\' not in name and name not in ('api/n01-controller.py','source-inventory.json'))
        require(type(entry) is dict and set(entry)=={'bytes','sha256'})
        data=(root/name).read_bytes()
        require(type(entry['bytes']) is int and len(data)==entry['bytes']
            and hashlib.sha256(data).hexdigest()==entry['sha256'])
        measured[name]=entry
    for name in ('api/n01-controller.py','source-inventory.json'):
        data=(root/name).read_bytes()
        measured[name]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    return codec.digest(codec.canonical(measured))


class PublicCustodyClient:
    """Read-only exact public review/source prefixes; no fallback or mutation."""
    def __init__(self,client):
        self.client=client;self.attempts=0;self.retired=False
        self.meta=client.meta
    def __getattr__(self,operation):
        def invoke(**kwargs):
            require(not self.retired and self.attempts<12 and
                review.FROM_MS<=int(time.time()*1000)<review.UNTIL_MS)
            require(operation in ('list_object_versions','get_object','get_object_retention'))
            require(kwargs.get('Bucket')=='nexus-d03-custody-862902859484-ap-southeast-1-v1'
                and kwargs.get('ExpectedBucketOwner')=='862902859484'
                and kwargs.get('Key',kwargs.get('Prefix','')).startswith((review.PREFIX,source.PREFIX)))
            self.attempts+=1
            try:return getattr(self.client,operation)(**kwargs)
            except Exception:
                self.retired=True
                raise ValueError('N01_BOOTSTRAP_CUSTODY_QUARANTINE') from None
        return invoke
    def close(self):
        self.retired=True;self.client.close()


def native_public_custody(native_header):
    """Native platform OIDC goes directly to STS; values never leave SDK memory."""
    import boto3
    from botocore.config import Config
    from botocore import UNSIGNED
    cfg=Config(retries={'total_max_attempts':1},connect_timeout=5,read_timeout=10)
    unsigned=Config(signature_version=UNSIGNED,retries={'total_max_attempts':1},connect_timeout=5,read_timeout=10)
    clients=[]
    def client(service,credentials):
        result=boto3.client(service,region_name='ap-southeast-1',config=cfg,
            aws_access_key_id=credentials['AccessKeyId'],aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken'])
        clients.append(result);return result
    try:
        initial=boto3.client('sts',region_name='us-east-1',config=unsigned);clients.append(initial)
        a=initial.assume_role_with_web_identity(RoleArn=A,RoleSessionName='NexusG3N01Vercel',
            WebIdentityToken=native_header,DurationSeconds=900)
        sts=client('sts',a['Credentials']);identity=sts.get_caller_identity()
        require(identity['Account']=='175880707430' and identity['Arn']==
            'arn:aws:sts::175880707430:assumed-role/NexusG3QualificationCaller/NexusG3N01Vercel')
        r=sts.assume_role(RoleArn=R,RoleSessionName='NexusG3N01Custody',DurationSeconds=900)
        ident=client('sts',r['Credentials']).get_caller_identity()
        require(ident['Account']=='862902859484' and ident['Arn']==
            'arn:aws:sts::862902859484:assumed-role/NexusG3N01AppendRead/NexusG3N01Custody')
        result=PublicCustodyClient(client('s3',r['Credentials']))
        clients.remove(result.client)
        return result
    except Exception:
        raise ValueError('N01_BOOTSTRAP_NATIVE_FEDERATION_QUARANTINE') from None
    finally:
        for item in clients:item.close()


def bootstrap(native_header,environment,artifact_inventory_sha256):
    client=native_public_custody(native_header)
    try:
        current=review.read_protected_review(client,storage_scope(),now_ms=int(time.time()*1000))
        return dict(status='NATIVE_PUBLIC_REVIEW_BOOTSTRAP_VERIFIED',authority='NONE',real_admission='NO',
            project_id=environment.get('VERCEL_PROJECT_ID'),deployment_id=environment.get('VERCEL_DEPLOYMENT_ID'),
            deployment_host=environment.get('VERCEL_URL'),artifact_inventory_sha256=artifact_inventory_sha256,
            process_nonce=PROCESS_NONCE,application_generation=1,review_generation=1,
            review_package_sha256=current.package_sha256,review_acceptance_sha256=current.acceptance_sha256,
            expires_at_ms=current.valid_until_ms,s3_attempts=client.attempts,ddb_attempts=0,
            owner_context='NOT_CREATED',source_enrollment='NOT_PERFORMED',automatic_redispatch='DENY')
    finally:client.close()

"""Bounded public JWKS normalization, never source enrollment or authority.

Certificate metadata proves consistency only, not CA/provider provenance. No
fetch, credential, key refresh, review renewal or discovery path exists here.
"""
import base64
import hashlib
import re

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from ash import g3_n01_owner_context as owner
from ash.g3_control_semantics import require

CORE=frozenset(('kty','kid','alg','use','n','e'))
OPTIONAL=frozenset(('key_ops','x5c','x5tS256','x5t#S256'))


def normalize_public_jwks(raw):
    """Public metadata only. All supplied fields validated before normalization."""
    try:
        require(type(raw) is bytes and 0<len(raw)<=16384)
        body=owner.unique_json(raw)
        require(type(body) is dict and set(body)<= {'keys','status_code','request_id'}
                and 'keys' in body)
        if 'status_code' in body:
            require(type(body['status_code']) is int and body['status_code']==200)
        if 'request_id' in body:
            require(type(body['request_id']) is str and
                    re.fullmatch(r'request-id-test-[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',body['request_id']))
        require(type(body['keys']) is list and 1<=len(body['keys'])<=8)
        keys=[]
        for supplied in body['keys']:
            require(type(supplied) is dict and CORE<=set(supplied)<=CORE|OPTIONAL)
            key={name:supplied[name] for name in CORE}
            owner.public_keys((key,))
            if 'key_ops' in supplied:require(supplied['key_ops']==['verify'])
            thumbs=set(supplied)&{'x5tS256','x5t#S256'}
            require(len(thumbs)<=1 and (not thumbs or 'x5c' in supplied))
            if 'x5c' in supplied:
                chain=supplied['x5c'];require(type(chain) is list and 1<=len(chain)<=3)
                certs=[]
                for encoded in chain:
                    require(type(encoded) is str and 0<len(encoded)<=6144 and
                            re.fullmatch(r'[A-Za-z0-9+/]+={0,2}',encoded))
                    data=base64.b64decode(encoded,validate=True)
                    require(base64.b64encode(data).decode()==encoded)
                    certificate=x509.load_der_x509_certificate(data)
                    require(certificate.public_bytes(serialization.Encoding.DER)==data)
                    certs.append((data,certificate))
                public=certs[0][1].public_key()
                require(isinstance(public,rsa.RSAPublicKey))
                values=public.public_numbers()
                require(values.n==int.from_bytes(owner.part(key['n'],1024),'big') and
                        values.e==int.from_bytes(owner.part(key['e'],16),'big'))
                if thumbs:
                    thumb=supplied[next(iter(thumbs))]
                    require(type(thumb) is str and re.fullmatch(r'[A-Za-z0-9_-]{43}=?',thumb))
                    unpadded=thumb.rstrip('=')
                    require(owner.part(unpadded,43)==hashlib.sha256(certs[0][0]).digest())
            keys.append(key)
        return owner.public_keys(tuple(keys))
    except Exception:
        raise ValueError('N01_PUBLIC_PIN_DENY') from None

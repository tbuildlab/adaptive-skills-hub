"""N01's fixed Consumer Test transport for the maintained Stytch SDK.

Transport only, always NONE. This does not enroll a source, read credentials,
authenticate an Owner, restore a bearer, issue authority or select a provider.
The protected relying party must gate current registration before constructing
the SDK client. Native HTTP is fixed; no injectable production transport exists.
"""
import json
import re
import time

import requests
from requests.adapters import HTTPAdapter

from ash.g3_control_semantics import require
from ash.g3_n01_owner_context import OWNER

ORIGIN='https://test.stytch.com'
LIMIT=65536
MAX_ATTEMPTS=32
PATHS={
    '/v1/otps/email/send': {'email','expiration_minutes'},
    '/v1/otps/authenticate': {'method_id','code','session_duration_minutes'},
    '/v1/totps/authenticate': {'user_id','totp_code','session_token'},
    '/v1/sessions/authenticate': {'session_token'},
    '/v1/sessions/revoke': {'session_id'},
}


def decode_response(raw):
    require(type(raw) is bytes and 0<len(raw)<=LIMIT)
    def pairs(items):
        result={}
        for key,value in items:
            require(key not in result);result[key]=value
        return result
    def invalid(_):raise ValueError('N01_IDENTITY_TRANSPORT_DENY')
    value=json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=invalid)
    nodes=0
    def visit(child,depth):
        nonlocal nodes
        nodes+=1;require(depth<=32 and nodes<=8192)
        if type(child) is dict:
            for descendant in child.values():visit(descendant,depth+1)
        elif type(child) is list:
            for descendant in child:visit(descendant,depth+1)
    visit(value,0);require(type(value) is dict)
    return value


def request_shape(method,url,body):
    require(method=='POST' and type(url) is str and url.startswith(ORIGIN))
    path=url[len(ORIGIN):]
    require(path in PATHS and type(body) is dict and set(body)==PATHS[path])
    require(len(json.dumps(body).encode())<=8192)
    if path=='/v1/otps/email/send':
        require(type(body['email']) is str and 0<len(body['email'])<=320
                and body['expiration_minutes']==2 and type(body['expiration_minutes']) is int)
    elif path=='/v1/otps/authenticate':
        require(type(body['method_id']) is str and re.fullmatch(r'email-test-[a-f0-9-]{36}',body['method_id']))
        require(type(body['code']) is str and re.fullmatch(r'\d{6}',body['code']))
        require(type(body['session_duration_minutes']) is int and body['session_duration_minutes']==15)
    elif path=='/v1/totps/authenticate':
        require(body['user_id']==OWNER and type(body['totp_code']) is str
                and re.fullmatch(r'\d{6}',body['totp_code']))
    elif path=='/v1/sessions/revoke':
        require(type(body['session_id']) is str and re.fullmatch(r'session-test-[a-f0-9-]{36}',body['session_id']))
    if 'session_token' in body:
        require(type(body['session_token']) is str and 0<len(body['session_token'])<=8192)
    return path


class BoundedStytchSession(requests.Session):
    """One bounded native SDK session; unknown outcomes retire, never retry."""
    def __init__(self):
        super().__init__()
        self.trust_env=False
        self.proxies={}
        self.mount('https://',HTTPAdapter(max_retries=0))
        self.attempts=0;self.retired=False;self._native_body=None

    @property
    def authority(self):return 'NONE'

    def request(self,method,url,**kwargs):
        self._native_body=None
        response=None
        try:
            require(not self.retired and self.attempts<MAX_ATTEMPTS)
            request_shape(method,url,kwargs.get('json'))
            # requests.Session.post supplies its unused data=None argument.
            if 'data' in kwargs:
                require(kwargs.pop('data') is None)
            require(set(kwargs)<= {'json','headers','auth'})
            require(self.trust_env is False and not self.proxies)
            adapter=self.get_adapter(url)
            require(type(adapter) is HTTPAdapter and adapter.max_retries.total==0)
            self.cookies.clear()
            headers=kwargs.get('headers',{})
            require(type(headers) is dict and set(headers)<= {'Content-Type','User-Agent'})
            require(headers.get('Content-Type')=='application/json')
            kwargs['headers']=dict(headers,Accept='application/json',**{'Accept-Encoding':'identity'})
            self.attempts+=1
            started=time.monotonic()
            response=super().request(method,url,**kwargs,timeout=(3,5),verify=True,
                allow_redirects=False,stream=True)
            require(type(response.status_code) is int and response.status_code in (200,404))
            require(re.fullmatch(r'application/json(?:;\s*charset=utf-8)?',
                response.headers.get('Content-Type',''),re.IGNORECASE))
            require(response.headers.get('Content-Encoding','identity')=='identity')
            declared=response.headers.get('Content-Length')
            if declared is not None:require(re.fullmatch(r'\d{1,10}',declared) and int(declared)<=LIMIT)
            pieces=[];size=0
            for piece in response.iter_content(chunk_size=4096):
                require(time.monotonic()-started<15)
                size+=len(piece);require(size<=LIMIT);pieces.append(piece)
            require(time.monotonic()-started<15 and (declared is None or size==int(declared)))
            raw=b''.join(pieces);body=decode_response(raw)
            require(type(body.get('status_code')) is int and body['status_code']==response.status_code)
            if response.status_code==404:
                require(url==ORIGIN+'/v1/sessions/authenticate'
                        and body.get('error_type')=='session_not_found'
                        and set(body)<= {'status_code','error_type','request_id','error_message','error_url'})
            # Preserve nanosecond strings before SDK models project timestamps.
            # Raw response remains protected process memory and is never logged.
            self._native_body=body
            response._content=raw;response._content_consumed=True
            return response
        except Exception:
            self.retired=True;self._native_body=None
            raise ValueError('N01_IDENTITY_TRANSPORT_DENY') from None
        finally:
            if response is not None:response.close()
            self.cookies.clear()

    def close(self):
        self.retired=True;self._native_body=None
        super().close()

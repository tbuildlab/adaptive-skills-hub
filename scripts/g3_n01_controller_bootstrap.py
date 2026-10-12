"""One native public-review bootstrap read. No login, source grant or effect."""
from http.server import BaseHTTPRequestHandler
import json
import os
import re
import threading
import time

from ash.g3_control_semantics import require
from ash import g3_n01_public_review as review
from ash import g3_n01_source_enrollment as source
from ash import g3_n01_controller_bootstrap as boot

LOCK=threading.Lock()
OUTCOME=None
ARTIFACT_ROOT=None
EXPECTED_MANIFEST_SHA=None


def request_allowed(path,method,headers,environment):
    host=environment.get('VERCEL_URL','')
    return (path=='/api/n01-controller' and method=='GET'
        and environment.get('VERCEL_ENV')=='production'
        and environment.get('VERCEL_PROJECT_ID')==source.HOST_PROJECT
        and re.fullmatch(r'dpl_[A-Za-z0-9]{20,40}',environment.get('VERCEL_DEPLOYMENT_ID','')) is not None
        and re.fullmatch(r'nexus-g3-qual-[a-z0-9]+-tdy0225\.vercel\.app',host) is not None
        and headers.get_all('Host')==[host] and headers.get('Origin') is None
        and headers.get_all('x-vercel-oidc-token') is not None
        and len(headers.get_all('x-vercel-oidc-token'))==1
        and headers.get_all('Content-Length') in (None,['0'])
        and headers.get_all('Transfer-Encoding') is None
        and review.FROM_MS<=int(time.time()*1000)<review.UNTIL_MS)


class handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def do_GET(self):
        global OUTCOME
        status=403;result=dict(status='DENY',authority='NONE',real_admission='NO')
        if request_allowed(self.path,self.command,self.headers,os.environ):
            with LOCK:
                if OUTCOME is None:
                    OUTCOME=dict(status='QUARANTINE',authority='NONE',real_admission='NO',bootstrap_stage='ARTIFACT_MEASUREMENT')
                    try:
                        require(ARTIFACT_ROOT is not None and EXPECTED_MANIFEST_SHA is not None)
                        measured=boot.measure_artifact(ARTIFACT_ROOT,EXPECTED_MANIFEST_SHA)
                        OUTCOME['bootstrap_stage']='NATIVE_PUBLIC_REVIEW_READ'
                        OUTCOME=boot.bootstrap(self.headers.get('x-vercel-oidc-token'),os.environ,measured)
                    except Exception as error:
                        if type(error) is boot.ArtifactConfigMismatch:
                            OUTCOME['artifact_config_shape']=error.observation
                        # Report only our closed public-file diagnostics. Never
                        # emit SDK errors, request fields or arbitrary exceptions.
                        diagnostic=str(error) if type(error) is ValueError else ''
                        if diagnostic=='N01_ARTIFACT_MANIFEST_UNAVAILABLE':OUTCOME['bootstrap_stage']=diagnostic
                        elif diagnostic.startswith(('N01_ARTIFACT_FILE_UNAVAILABLE:','N01_ARTIFACT_FILE_MISMATCH:')):
                            name=diagnostic.partition(':')[2]
                            if name in ('requirements.txt','.python-version','vercel.json','index.html',
                                        'api/n01-controller.py','source-inventory.json'):
                                OUTCOME['bootstrap_stage']=diagnostic
                result=OUTCOME;status=200 if result['status']=='NATIVE_PUBLIC_REVIEW_BOOTSTRAP_VERIFIED' else 503
        raw=json.dumps(result,sort_keys=True).encode()
        print(json.dumps({'n01_controller_bootstrap_readback':result},sort_keys=True),flush=True)
        self.send_response(status)
        for key,value in {'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store',
            'Referrer-Policy':'no-referrer','X-Frame-Options':'DENY','X-Content-Type-Options':'nosniff',
            'Content-Security-Policy':"default-src 'none'; frame-ancestors 'none'"}.items():self.send_header(key,value)
        self.end_headers();self.wfile.write(raw)
    do_POST=do_GET
    do_PUT=do_GET
    do_DELETE=do_GET

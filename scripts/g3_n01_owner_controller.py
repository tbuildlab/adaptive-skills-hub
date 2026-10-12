"""Fixed native Owner-only qualification controller; no execution or admission.

Requests cannot supply projections, source assertions, preparations, keys, URLs,
resource names or authority verdicts. Native protected facilities supply origin;
one process stores original identity material privately and never restores it.
"""
from http.server import BaseHTTPRequestHandler
from datetime import datetime,timezone
from dataclasses import replace
import hashlib
import hmac
import json
import os
import re
import secrets
import threading
import time
from io import BytesIO
from types import SimpleNamespace
from urllib.parse import unquote_to_bytes

from ash import g3_n01_controller_bootstrap as boot
from ash import g3_n01_native_transport as native
from ash import g3_n01_public_review as review
from ash import g3_n01_source_enrollment as source
from ash import g3_n01_membership_custody as membership
from ash import g3_n01_owner_state as state
from ash import g3_n01_owner_protocol as protocol
from ash import g3_n01_owner_persistence as persistence
from ash import g3_n01_owner_ingress as ingress
from ash import g3_n01_stytch_transport as identity_transport
from ash import g3_n02_presentation as presentation
from ash import g3_delegated_control_codec as codec
from ash import g3_delegated_record_codec as records
from ash import g3_checkpoint_custody as custody
from ash.g3_primary_ledger import DelegatedDynamoReservations
from ash.g3_control_semantics import require

ARTIFACT_ROOT=None
EXPECTED_MANIFEST_SHA=None
DELIVERY_EMAIL_SHA=None
LOCK=threading.Lock()
CONTROLLER=None
PROBE_USED=False
POST_PATHS=frozenset(('/api/n01/recover','/api/n01/enroll','/api/n01/login','/api/n01/decision','/api/n01/revoke'))
GET_PATHS=frozenset(('/api/n01-controller','/api/n01/start','/api/n01/login','/api/n01/confirm','/api/n01/status'))
UNTIL=datetime.fromtimestamp(review.UNTIL_MS/1000,timezone.utc)
CUSTODY_REVISION=1
RESTART_PROFILE=None


def canonical_route(path):
    """Closed internal rewrite selector; never an authorization or supplied URL."""
    routes=('start','login','confirm','status','recover','enroll','decision','revoke')
    for route in routes:
        if path=='/api/n01-controller?n01_route='+route:return '/api/n01/'+route
        if path=='/api/n01/'+route+'?n01_route='+route:return '/api/n01/'+route
    return path


def request_allowed(path,method,headers,environment):
    host=environment.get('VERCEL_URL','')
    allowed=(path in (GET_PATHS if method=='GET' else POST_PATHS if method=='POST' else ())
        and environment.get('VERCEL_ENV')=='production'
        and environment.get('VERCEL_PROJECT_ID')==source.HOST_PROJECT
        and re.fullmatch(r'dpl_[A-Za-z0-9]{20,40}',environment.get('VERCEL_DEPLOYMENT_ID','')) is not None
        and re.fullmatch(r'nexus-g3-qual-[a-z0-9]+-tdy0225\.vercel\.app',host) is not None
        and headers.get_all('Host')==[host]
        and headers.get_all('Transfer-Encoding') is None
        and len(headers.get_all('x-vercel-oidc-token') or [])==1
        and review.FROM_MS<=int(time.time()*1000)<review.UNTIL_MS)
    if not allowed:return False
    if method=='GET':return headers.get_all('Content-Length') in (None,['0']) and headers.get('Origin') in (None,'https://'+host)
    return (headers.get_all('Origin')==['https://'+host]
        and headers.get_all('Content-Type')==['application/x-www-form-urlencoded']
        and len(headers.get_all('Content-Length') or [])==1
        and re.fullmatch('[1-9][0-9]{0,3}',headers.get('Content-Length','')) is not None
        and int(headers.get('Content-Length'))<=4096
        and len(headers.get_all('Cookie') or [])==1)


def form(raw,allowed):
    require(type(raw) is bytes and 0<len(raw)<=4096)
    value={}
    for field in raw.decode('ascii').split('&'):
        require(field.count('=')==1)
        key,item=field.split('=');require(re.search(r'%(?![0-9A-Fa-f]{2})',key+item) is None)
        key=unquote_to_bytes(key.replace('+',' ')).decode('utf-8','strict')
        item=unquote_to_bytes(item.replace('+',' ')).decode('utf-8','strict')
        require(key in allowed and key not in value);value[key]=item
    require(set(value)==set(allowed));return value


def native_identity_client():
    """Private native construction only; no auth call or credential projection."""
    from stytch import Client
    require(os.environ.get('STYTCH_PROJECT_ID')==source.PROJECT)
    transport=identity_transport.BoundedStytchSession()
    try:
        client=Client(project_id=source.PROJECT,secret=os.environ['STYTCH_SECRET'],environment='test',sync_session=transport)
        require(client.sync_client._session is transport and client.sync_client.project_id==source.PROJECT)
        return client,transport
    except Exception:
        transport.close();raise ValueError('N01_NATIVE_IDENTITY_BOOTSTRAP_DENY') from None


class OwnerController:
    """A fixed lifecycle, not a workflow engine. Unknown is terminal quarantine."""
    def __init__(self,header,environment,artifact_sha):
        self.__phase='QUARANTINE';self.__environment={key:environment.get(key) for key in
            ('VERCEL_ENV','VERCEL_URL','VERCEL_PROJECT_ID','VERCEL_DEPLOYMENT_ID')}
        self.__artifact_sha=artifact_sha;self.__transport=native.NativeTransport(header)
        self.__lease_started=int(time.time()*1000);self.__maintenance=secrets.token_hex(32)
        self.__review=None;self.__history=None;self.__candidate=None;self.__enrolled=None
        self.__owner=None;self.__current=None;self.__challenge=None;self.__view=None;self.__shown=None
        self.__last_wall=int(time.time()*1000);self.__last_monotonic=time.monotonic()
        self.__source_proposal=None;self.__events=[]
        try:
            if RESTART_PROFILE=='OWNER_SDK_REPAIR_FORWARD_V1':
                client,identity=native_identity_client();identity.close();client=None
            self.__review=review.read_protected_review(self.__transport.custody,boot.storage_scope(),now_ms=self.__last_wall)
            if RESTART_PROFILE is None:
                self.__history=membership.MembershipFence(self.__transport.custody,boot.storage_scope(),profile='PRODUCTION').read(valid_until=UNTIL)
            else:
                from ash import g3_n01_owner_restart as restart
                restart.require_profile(RESTART_PROFILE)
                restart=restart.configuration(RESTART_PROFILE)
                self.__history=restart.HistoricalOwnerFence(self.__transport.custody).read(valid_until=UNTIL)
            self._ledger().observe_current(independent_checkpoint=self.__history.checkpoints[-1])
            self.__candidate=(state.prepare_empty_recovery(self.__history,process_nonce=boot.PROCESS_NONCE,now_ms=self._time())
                if RESTART_PROFILE is None else restart.prepare_forward_recovery(self.__history,process_nonce=boot.PROCESS_NONCE,now_ms=self._time()))
            now=self._time()
            value=dict(schema_version='nexus.g3.n01.current-source-enrollment.v1',purpose='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY',
                authority_mode=records.MODE,authority_config_sha256=source.CONFIG,authority_instance=custody.INSTANCE,
                application_generation=1,review_generation=1,service_revision='nexus-g3-n01-controller-v1',
                review_package_sha256=review.PACKAGE_SHA,review_acceptance_sha256=review.ACCEPTANCE_SHA,
                principal=dict(issuer='stytch.com/'+source.PROJECT,client_id=source.PROJECT,subject=source.OWNER),
                deployment_id=environment['VERCEL_DEPLOYMENT_ID'],deployment_host=environment['VERCEL_URL'],host_project_id=source.HOST_PROJECT,
                artifact_inventory_sha256=artifact_sha,process_nonce=boot.PROCESS_NONCE,source_kinds=['D01','D03','OWNER_ENROLLMENT'],
                issued_at_ms=now,expires_at_ms=review.UNTIL_MS,no_automatic_redispatch='REQUIRED',real_admission='NO')
            raw=codec.canonical(value)
            self.__source_proposal=source.bind_source(raw,self.__review,native_environment=self.__environment,
                artifact_inventory_sha256=artifact_sha,process_nonce=boot.PROCESS_NONCE,now_ms=now)
            self.__phase='SOURCE_PROPOSAL_READY_NONE'
            self._event('NATIVE_OWNER_SOURCE_PROPOSAL_READY_NONE')
        except Exception:
            self._quarantine();raise ValueError('N01_NATIVE_OWNER_PROBE_QUARANTINE') from None
    @property
    def authority(self):return 'NONE'
    @property
    def phase(self):return self.__phase
    def __repr__(self):return 'OwnerController(authority=NONE)'
    def __getstate__(self):raise TypeError('N01_OWNER_CONTROLLER_NOT_RESTORABLE')
    def __reduce_ex__(self,_):raise TypeError('N01_OWNER_CONTROLLER_NOT_RESTORABLE')
    def _time(self):
        now=int(time.time()*1000);monotonic=time.monotonic()
        require(review.FROM_MS<=self.__last_wall<=now<review.UNTIL_MS and self.__last_monotonic<=monotonic)
        self.__last_wall=now;self.__last_monotonic=monotonic;return now
    def _ledger(self):
        return DelegatedDynamoReservations(self.__transport.primary,table_arn=native.TABLE,instance=custody.INSTANCE,max_attempts=256)
    def _fence(self):
        original=boot.storage_scope()
        if RESTART_PROFILE is not None:
            from ash import g3_n01_owner_restart as restart
            original=restart.configuration(RESTART_PROFILE).scope()
        scope=replace(original,admin_checkpoint_ids=original.admin_checkpoint_ids+
            (custody.reference(self.__candidate.checkpoint)['id'],))
        return persistence.OwnerMembershipFence(self.__transport.custody,scope,public_review=self.__review,
            native_environment=self.__environment,artifact_inventory_sha256=self.__artifact_sha,process_nonce=boot.PROCESS_NONCE,max_attempts=1000,custody_revision=CUSTODY_REVISION,
            **({} if RESTART_PROFILE is None else {'restart_profile':RESTART_PROFILE}))
    def _storage(self):
        fence=self._fence();history=fence.read(valid_until=UNTIL)
        self._ledger().observe_current(independent_checkpoint=history.checkpoints[-1])
        return fence,history
    def _commit(self,candidate,objects):
        fence=self._fence();ledger=self._ledger()
        result=persistence.OwnerMembershipCommit(ledger,fence,expected_head=candidate.expected_checkpoint,valid_until=UNTIL).commit(candidate,objects=objects)
        require(result.authority=='NONE');self.__history=self._fence().read(valid_until=UNTIL)
        require(self.__history.checkpoints[-1]==candidate.checkpoint)
        self._time()
    def _event(self,name):
        record=dict(event=name,phase=self.__phase,observed_at_ms=self._time(),authority='NONE',real_admission='NO',
            artifact_inventory_sha256=self.__artifact_sha,process_nonce=boot.PROCESS_NONCE,
            deployment_id=self.__environment['VERCEL_DEPLOYMENT_ID'],deployment_host=self.__environment['VERCEL_URL'],
            ddb_attempts=self.__transport.ddb_attempts,s3_attempts=self.__transport.s3_attempts,
            checkpoint=self.__history.head if self.__history is not None else None,no_automatic_redispatch='REQUIRED')
        self.__events.append(record);print(json.dumps({'n01_owner_controller_observation':record},sort_keys=True),flush=True)
    def _quarantine(self):
        self.__phase='QUARANTINE'
        if self.__owner is not None:self.__owner.retire()
        self.__current=None;self.__transport.close()
    def proposal(self):
        require(self.__source_proposal is not None and self.__candidate is not None)
        body=codec.decode(self.__candidate.checkpoint)
        authorization=dict(schema_version='nexus.g3.n01.owner-recovery-authorization.v1',purpose='BOUNDED_OWNER_CONTEXT_SOURCE_ONLY',
            authority_mode=records.MODE,authority_config_sha256=source.CONFIG,
            source_enrollment_sha256=self.__source_proposal.enrollment_sha256,checkpoint=custody.reference(self.__candidate.checkpoint),
            previous_checkpoint=body['previous_checkpoint'],authority_epoch=body['authority_epoch'],incarnation=body['incarnation'],
            application_generation=1,review_generation=1,expires_at_ms=review.UNTIL_MS,no_automatic_redispatch='REQUIRED',real_admission='NO')
        return dict(status=self.__phase,source_proposal=self.__source_proposal.value,source_sha256=self.__source_proposal.enrollment_sha256,
            recovery_authorization=authorization,recovery_authorization_sha256=codec.digest(codec.canonical(authorization)),
            public_review='EXACT_RETAINED_REVIEW_VERIFIED',current_owner='NOT_AUTHENTICATED',authority='NONE',real_admission='NO')
    def maintenance_cookie(self,handler):
        require(self.__phase!='QUARANTINE')
        handler.send_header('Set-Cookie','__Host-NexusN01Maintenance='+self.__maintenance+'; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=3600')
    def maintenance_form(self,handler):
        route={'SOURCE_PROPOSAL_READY_NONE':'recover','RECOVERED_OWNER_LINEAGE_NONE':'enroll',
            'OWNER_SOURCE_ENROLLED_NONE':'login','DECISION_CONSUMED_NONE':'revoke'}.get(self.__phase)
        require(route is not None)
        text=('<!doctype html><html lang="en"><meta charset="utf-8"><title>N01 bounded continuation</title>'
            '<h1>Bounded N01 continuation</h1><p>Owner-only preparation. REAL_ADMISSION remains NO.</p>'
            '<form method="post" action="/api/n01/'+route+'"><input type="hidden" name="operation" value="'+route+'">'
            '<button type="submit">'+route.upper()+'</button></form></html>')
        handler.wfile.write(text.encode())
    def __maintenance_gate(self,headers):
        values=headers.get_all('Cookie');require(type(values) is list and len(values)==1)
        own=[part.strip().partition('=')[2] for part in values[0].split(';') if part.strip().partition('=')[0]=='__Host-NexusN01Maintenance']
        require(len(own)==1 and hmac.compare_digest(own[0],self.__maintenance));self._time()
    def maintain(self,operation,headers,header):
        self.__maintenance_gate(headers)
        stage='MAINTENANCE_PHASE'
        try:
            if operation=='recover':
                require(self.__phase=='SOURCE_PROPOSAL_READY_NONE')
                # Fresh native credential lease is a new explicit maintenance
                # action, never replay of an unknown primary mutation.
                if self._time()-self.__lease_started>=600000:
                    self.__transport.close();self.__transport=native.NativeTransport(header);self.__lease_started=self._time()
                self.__phase='RECOVER_UNKNOWN'
                self.__enrolled=self.__transport.enable_owner_storage(self.__review,native_environment=self.__environment,
                    artifact_inventory_sha256=self.__artifact_sha,process_nonce=boot.PROCESS_NONCE,custody_revision=CUSTODY_REVISION,
                    **({} if RESTART_PROFILE is None else {'restart_profile':RESTART_PROFILE}))
                require(self.__enrolled==self.__source_proposal)
                self._commit(self.__candidate,{})
                self.__phase='RECOVERED_OWNER_LINEAGE_NONE';self._event('NATIVE_OWNER_RECOVERY_FINALIZED_NONE')
            elif operation=='enroll':
                require(self.__phase=='RECOVERED_OWNER_LINEAGE_NONE');self.__phase='ENROLL_UNKNOWN'
                _,history=self._storage()
                candidate,objects=state.prepare_owner_enrollment(history,self.__enrolled,now_ms=self._time(),
                    **({} if RESTART_PROFILE is None else {'restart_profile':RESTART_PROFILE}))
                self._commit(candidate,objects)
                self.__phase='OWNER_SOURCE_ENROLLED_NONE';self._event('NATIVE_OWNER_SOURCE_MEMBERSHIP_FINALIZED_NONE')
            elif operation=='login':
                require(self.__phase=='OWNER_SOURCE_ENROLLED_NONE')
                if self._time()-self.__lease_started>=600000:
                    require(self.__owner is None and self.__current is None)
                    self.__transport.close();self.__transport=native.NativeTransport(header);self.__lease_started=self._time()
                    current=self.__transport.enable_owner_storage(self.__review,native_environment=self.__environment,
                        artifact_inventory_sha256=self.__artifact_sha,process_nonce=boot.PROCESS_NONCE,custody_revision=CUSTODY_REVISION,
                        **({} if RESTART_PROFILE is None else {'restart_profile':RESTART_PROFILE}))
                    require(current==self.__enrolled)
                # Credential use stays in the protected native SDK. No value
                # is returned, inspected by the operator or written to evidence.
                stage='NATIVE_IDENTITY_BOOTSTRAP'
                client,transport=native_identity_client()
                stage='DELIVERY_BINDING'
                require(DELIVERY_EMAIL_SHA is not None)
                stage='CURRENT_CUSTODY_READ'
                fence,_=self._storage()
                stage='CURRENT_OWNER_INGRESS'
                self.__owner=ingress.OwnerIngress(client,transport,fence,self._ledger(),delivery_email_sha256=DELIVERY_EMAIL_SHA)
                self.__phase='OWNER_LOGIN_READY_NONE';self._event('NATIVE_CURRENT_OWNER_LOGIN_READY_NONE')
            elif operation=='revoke':
                require(self.__phase=='DECISION_CONSUMED_NONE' and self.__current is not None)
                self.__phase='REVOKE_UNKNOWN';result=self.__current.revoke();self.__current=None
                _,history=self._storage()
                candidate,objects=protocol.prepare_revoke_after_consumption(history,self.__enrolled,remote_result=result,now_ms=self._time())
                self._commit(candidate,objects)
                self.__phase='OWNER_CONTEXT_CONSUMED_REVOKED_NONE';self._event('NATIVE_EXACT_OWNER_SESSION_REVOKED_PERSISTED_NONE')
            else:require(False)
            return self.__phase
        except Exception:
            if operation=='login':
                print(json.dumps({'n01_owner_bootstrap_denial':dict(stage=stage,authority='NONE',real_admission='NO',
                    ddb_attempts=self.__transport.ddb_attempts,s3_attempts=self.__transport.s3_attempts)},sort_keys=True),flush=True)
            self._quarantine();raise ValueError('N01_NATIVE_OWNER_MAINTENANCE_QUARANTINE') from None
    def write_login(self,handler):
        require(self.__phase=='OWNER_LOGIN_READY_NONE');self.__owner.write_form(handler)
    @property
    def initial_login(self):
        return self.__phase=='OWNER_LOGIN_READY_NONE' and self.__owner is not None and self.__owner.state=='PREAUTH'
    def owner_cookie(self,handler):
        require(self.__owner is not None);self.__owner.attach_cookie(handler)
    def login(self,raw,headers):
        require(self.__phase=='OWNER_LOGIN_READY_NONE')
        try:
            kind=self.__owner.state
            key={'PREAUTH':'email','OTP_SENT':'code','OTP_VERIFIED':'totp_code'}[kind]
            fields=form(raw,('csrf',key));self.__owner.authenticated_form(headers,csrf=fields['csrf'])
            if kind=='PREAUTH':self.__owner.send_email(fields[key])
            elif kind=='OTP_SENT':self.__owner.authenticate_email(fields[key])
            else:
                self.__current=self.__owner.authenticate_totp(fields[key])
                _,history=self._storage();projection=self.__current.recheck()
                candidate,objects,challenge,view=protocol.prepare_challenge(history,self.__enrolled,projection,
                    deadline_ms=self.__current.deadline_ms,nonce=secrets.token_hex(32),now_ms=self._time())
                self.__phase='CHALLENGE_UNKNOWN';self._commit(candidate,objects)
                self.__current.recheck();self.__challenge=challenge;self.__view=view
                self.__phase='CURRENT_OWNER_CHALLENGE_PERSISTED_NONE';self._event('NATIVE_CURRENT_OWNER_CHALLENGE_FINALIZED_NONE')
            return self.__phase
        except Exception:
            self._quarantine();raise ValueError('N01_NATIVE_OWNER_LOGIN_QUARANTINE') from None
    def display(self,handler):
        require(self.__phase=='CURRENT_OWNER_CHALLENGE_PERSISTED_NONE')
        self.__owner.current_projection()
        self.__shown=self.__owner.render_current(self.__challenge,self.__view,now_ms=self._time())
        handler.wfile.write(self.__shown.html)
    def decide(self,raw,headers):
        require(self.__phase=='CURRENT_OWNER_CHALLENGE_PERSISTED_NONE' and self.__shown is not None)
        try:
            decision=self.__owner.compare_current_decision(raw,self.__shown,headers,
                expected_host=self.__environment['VERCEL_URL'],now_ms=self._time())
            projection=self.__current.recheck();_,history=self._storage()
            candidate,objects=protocol.prepare_decision(history,self.__enrolled,decision,projection,now_ms=self._time())
            self.__phase='DECISION_UNKNOWN';self._commit(candidate,objects)
            self.__current.recheck()
            self.__phase='DECISION_CONSUMED_NONE';self._event('NATIVE_EXACT_HUMAN_'+decision.choice+'_CONSUMED_NONE')
            return self.__phase
        except Exception:
            self._quarantine();raise ValueError('N01_NATIVE_OWNER_DECISION_QUARANTINE') from None
    def status(self):
        return dict(status=self.__phase,events=self.__events,authority='NONE',real_admission='NO',automatic_redispatch='DENY',
            current_owner='NOT_EXPORTABLE_OR_RESTORABLE',grant_issuance='NOT_IMPLEMENTED',execution='DENY',
            ddb_attempts=self.__transport.ddb_attempts,s3_attempts=self.__transport.s3_attempts)


class handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass
    def _headers(self,status=200,*,html=False):
        self.send_response(status)
        values=presentation.response_headers() if html else {'Content-Type':'application/json; charset=utf-8',
            'Cache-Control':'no-store','Referrer-Policy':'no-referrer','X-Frame-Options':'DENY',
            'X-Content-Type-Options':'nosniff','Content-Security-Policy':"default-src 'none'; frame-ancestors 'none'"}
        # A navigation-mode HTML form POST under no-referrer sends Origin:null.
        # Same-origin retains exact Origin while disclosing nothing cross-origin.
        # Private state, codes and credentials are never part of these URLs.
        if html:values['Referrer-Policy']='same-origin'
        for key,value in values.items():self.send_header(key,value)
    def _redirect(self,path,*,owner_cookie=False):
        self.send_response(303);self.send_header('Location',path);self.send_header('Cache-Control','no-store')
        if owner_cookie:CONTROLLER.owner_cookie(self)
        self.end_headers()
    def _deny(self):
        print(json.dumps({'n01_owner_transport_denial':dict(
            known_route=self.path if self.path in GET_PATHS|POST_PATHS else 'UNSUPPORTED',
            known_base=self.path.split('?',1)[0] if self.path.split('?',1)[0] in GET_PATHS|POST_PATHS else 'UNSUPPORTED',
            has_query='?' in self.path,controller_present=CONTROLLER is not None,probe_used=PROBE_USED,
            native_oidc_present=len(self.headers.get_all('x-vercel-oidc-token') or [])==1,
            header_guard_passed=request_allowed(self.path,self.command,self.headers,os.environ),
            origin_is_exact=self.headers.get_all('Origin')==['https://'+os.environ.get('VERCEL_URL','')],
            origin_is_null=self.headers.get_all('Origin')==['null'],
            phase=CONTROLLER.phase if CONTROLLER is not None and type(CONTROLLER) is OwnerController else 'NOT_AVAILABLE',
            authority='NONE',real_admission='NO')},sort_keys=True),flush=True)
        self._headers(403);self.end_headers();self.wfile.write(b'{"status":"DENY_OR_QUARANTINE","authority":"NONE","real_admission":"NO"}')
    def do_GET(self):
        global CONTROLLER,PROBE_USED
        self.path=canonical_route(self.path)
        if not request_allowed(self.path,self.command,self.headers,os.environ):return self._deny()
        with LOCK:
            try:
                if self.path=='/api/n01-controller':
                    if not PROBE_USED:
                        PROBE_USED=True  # Before federation; no implicit retry after unknown.
                        measured=boot.measure_artifact(ARTIFACT_ROOT,EXPECTED_MANIFEST_SHA)
                        CONTROLLER=OwnerController(self.headers.get('x-vercel-oidc-token'),os.environ,measured)
                    require(CONTROLLER is not None)
                    value=CONTROLLER.proposal()
                    print(json.dumps({'n01_owner_controller_proposal':value},sort_keys=True),flush=True)
                    self._headers();self.end_headers();self.wfile.write(json.dumps(value,sort_keys=True).encode())
                elif self.path=='/api/n01/status':
                    require(CONTROLLER is not None);self._headers();self.end_headers()
                    self.wfile.write(json.dumps(CONTROLLER.status(),sort_keys=True).encode())
                elif self.path=='/api/n01/start':
                    require(CONTROLLER is not None);buffer=BytesIO();CONTROLLER.maintenance_form(SimpleNamespace(wfile=buffer))
                    self._headers(html=True);CONTROLLER.maintenance_cookie(self)
                    self.end_headers();self.wfile.write(buffer.getvalue())
                elif self.path=='/api/n01/login':
                    require(CONTROLLER is not None);buffer=BytesIO();CONTROLLER.write_login(SimpleNamespace(wfile=buffer))
                    self._headers(html=True)
                    # The initial preauth cookie is delivered once through the
                    # protected browser. OTP intermediate responses do not rotate.
                    if CONTROLLER.initial_login:CONTROLLER.owner_cookie(self)
                    self.end_headers();self.wfile.write(buffer.getvalue())
                else:
                    require(CONTROLLER is not None);buffer=BytesIO();CONTROLLER.display(SimpleNamespace(wfile=buffer))
                    self._headers(html=True);self.end_headers();self.wfile.write(buffer.getvalue())
            except Exception:self._deny()
    def do_POST(self):
        self.path=canonical_route(self.path)
        if not request_allowed(self.path,self.command,self.headers,os.environ):return self._deny()
        with LOCK:
            raw=None
            try:
                require(CONTROLLER is not None);raw=self.rfile.read(int(self.headers.get('Content-Length')))
                require(len(raw)==int(self.headers.get('Content-Length')))
                if self.path=='/api/n01/login':
                    if CONTROLLER.phase=='OWNER_SOURCE_ENROLLED_NONE':
                        fields=form(raw,('operation',));require(fields['operation']=='login')
                        CONTROLLER.maintain('login',self.headers,self.headers.get('x-vercel-oidc-token'))
                    else:CONTROLLER.login(raw,self.headers)
                    path='/api/n01/confirm' if CONTROLLER.phase=='CURRENT_OWNER_CHALLENGE_PERSISTED_NONE' else '/api/n01/login'
                    self._redirect(path,owner_cookie=CONTROLLER.phase=='CURRENT_OWNER_CHALLENGE_PERSISTED_NONE')
                elif self.path=='/api/n01/decision':
                    CONTROLLER.decide(raw,self.headers);self._redirect('/api/n01/start')
                else:
                    fields=form(raw,('operation',));operation=self.path.rsplit('/',1)[-1]
                    require(fields['operation']==operation);CONTROLLER.maintain(operation,self.headers,self.headers.get('x-vercel-oidc-token'))
                    self._redirect('/api/n01/status' if operation=='revoke' else '/api/n01/start')
            except Exception:self._deny()
            finally:raw=None
    do_PUT=do_GET
    do_DELETE=do_GET

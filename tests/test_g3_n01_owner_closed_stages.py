"""Inactive HTTP and secret-free diagnostic contracts; never native authority."""
from contextlib import redirect_stdout
from email.message import Message
from http.client import HTTPConnection
from http.server import HTTPServer
from io import BytesIO,StringIO
import json
import hashlib
import threading
import unittest
from unittest.mock import Mock,patch
from types import SimpleNamespace
from scripts import g3_n01_owner_controller as service
from ash import g3_n01_owner_ingress as ingress
from ash import g3_n01_public_review as review
from ash import g3_n01_source_enrollment as source


def inactive_owner():
    owner=object.__new__(ingress.OwnerIngress)
    for key,value in dict(state='PREAUTH',cookie='b'*64,csrf='a'*64,context=None,
                          method=None,bearer=None,transport=Mock(),client=None).items():
        setattr(owner,'_OwnerIngress__'+key,value)
    return owner


class InactiveController(service.OwnerController):
    """Test-only maintenance projection: no SDK, custody or primary calls."""
    def __init__(self):
        self._OwnerController__phase='OWNER_SOURCE_ENROLLED_NONE'
        self._OwnerController__owner=inactive_owner()
        self._OwnerController__transport=Mock();self._OwnerController__current=None
    def maintain(self,operation,headers,header):
        if operation!='login' or self.phase!='OWNER_SOURCE_ENROLLED_NONE':raise ValueError('INACTIVE_DENY')
        ingress.closed_stage('MAINTENANCE_LOGIN','ENTER')
        self._OwnerController__phase='OWNER_LOGIN_READY_NONE'
        ingress.closed_stage('MAINTENANCE_LOGIN','PASS')


def stages(text):
    return [json.loads(line)['n01_owner_closed_stage'] for line in text.splitlines()
            if 'n01_owner_closed_stage' in line]


class ClosedStageTests(unittest.TestCase):
    def setUp(self):
        self.previous=(service.CONTROLLER,service.PROBE_USED)
        self.addCleanup(lambda:setattr(service,'CONTROLLER',self.previous[0]))
        self.addCleanup(lambda:setattr(service,'PROBE_USED',self.previous[1]))
    def test_closed_schema_rejects_arbitrary_values_without_logging_them(self):
        output=StringIO()
        with redirect_stdout(output):
            for args,kwargs in ((('SECRET_SENTINEL','PASS'),{}),(('CSRF_MATCH','SECRET_SENTINEL'),{}),
                                (('REQUEST','ENTER'),dict(method='SECRET_SENTINEL')),
                                (('REQUEST','ENTER'),dict(route='SECRET_SENTINEL'))):
                with self.assertRaises(ValueError):ingress.closed_stage(*args,**kwargs)
            ingress.closed_stage('REQUEST','ENTER',method='POST',route='LOGIN')
        self.assertNotIn('SECRET_SENTINEL',output.getvalue())
        self.assertEqual(stages(output.getvalue()),[dict(stage='REQUEST',result='ENTER',method='POST',route='LOGIN',authority='NONE',real_admission='NO')])
    def test_private_csrf_and_cookie_failures_have_distinct_closed_stages(self):
        for csrf,cookie,expected in (('', 'b'*64,'CSRF_PRESENT'),('c'*64,'b'*64,'CSRF_MATCH'),('a'*64,'c'*64,'COOKIE_MATCH')):
            owner=inactive_owner();headers=Message();headers['Cookie']='__Host-NexusN01='+cookie
            output=StringIO()
            with redirect_stdout(output),self.assertRaises(ValueError):owner.authenticated_form(headers,csrf=csrf)
            self.assertEqual(stages(output.getvalue())[-1]['stage'],expected)
            self.assertEqual(stages(output.getvalue())[-1]['result'],'DENY')
            self.assertFalse(any(value in output.getvalue() for value in ('a'*64,'b'*64,'c'*64)))
    def test_repeated_maintenance_body_fails_auth_form_shape_before_provider(self):
        controller=InactiveController();controller._OwnerController__phase='OWNER_LOGIN_READY_NONE'
        output=StringIO()
        with patch.object(ingress.OwnerIngress,'send_email') as provider,redirect_stdout(output),self.assertRaises(ValueError):
            controller.login(b'operation=login',Message())
        self.assertEqual(stages(output.getvalue())[-1],dict(stage='AUTH_FORM_SHAPE',result='DENY',authority='NONE',real_admission='NO'))
        self.assertEqual(controller.phase,'QUARANTINE');provider.assert_not_called()
    def test_real_http_post_303_get_issues_form_cookie_without_auth_or_state_write(self):
        service.CONTROLLER=InactiveController();service.PROBE_USED=True
        environment=dict(VERCEL_ENV='production',VERCEL_PROJECT_ID=source.HOST_PROJECT,
            VERCEL_URL='nexus-g3-qual-inactive-tdy0225.vercel.app',VERCEL_DEPLOYMENT_ID='dpl_ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        output=StringIO()
        with patch.dict(service.os.environ,environment,clear=True),patch('time.time',return_value=(review.FROM_MS+1000)/1000),redirect_stdout(output):
            server=HTTPServer(('127.0.0.1',0),service.handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            try:
                headers={'Host':environment['VERCEL_URL'],'Origin':'https://'+environment['VERCEL_URL'],
                    'Content-Type':'application/x-www-form-urlencoded','Cookie':'SYNTHETIC_ONLY',
                    'x-vercel-oidc-token':'SYNTHETIC_ONLY_NOT_AUTHORITY'}
                connection=HTTPConnection(*server.server_address,timeout=5)
                connection.request('POST','/api/n01/login',body=b'operation=login',headers=headers)
                response=connection.getresponse();self.assertEqual(response.status,303)
                self.assertEqual(response.getheader('Location'),'/api/n01/login');self.assertEqual(response.read(),b'');connection.close()
                connection=HTTPConnection(*server.server_address,timeout=5)
                connection.request('GET','/api/n01/login',headers={'Host':environment['VERCEL_URL'],'x-vercel-oidc-token':'SYNTHETIC_ONLY_NOT_AUTHORITY'})
                response=connection.getresponse();self.assertEqual(response.status,200)
                self.assertTrue(response.getheader('Set-Cookie').startswith('__Host-NexusN01='))
                self.assertIn('Secure; HttpOnly; SameSite=Strict',response.getheader('Set-Cookie'))
                self.assertIn(b'Current enrolled Owner email',response.read());connection.close()
            finally:server.shutdown();server.server_close();thread.join(timeout=2)
        passes={row['stage'] for row in stages(output.getvalue()) if row['result']=='PASS'}
        self.assertTrue({'MAINTENANCE_FORM_SHAPE','MAINTENANCE_LOGIN','REDIRECT_TARGET','REDIRECT_303',
                         'GET_FORM_RENDER','PREAUTH_COOKIE_ISSUANCE','GET_FORM_DELIVERY'}<=passes)
        self.assertFalse(any(value in output.getvalue() for value in ('a'*64,'b'*64,'SYNTHETIC_ONLY')))
    def test_redirect_target_is_closed_before_any_response(self):
        handler=object.__new__(service.handler);handler.send_response=Mock();output=StringIO()
        with redirect_stdout(output),self.assertRaises(ValueError):handler._redirect('https://untrusted.invalid/SECRET_SENTINEL')
        handler.send_response.assert_not_called();self.assertNotIn('SECRET_SENTINEL',output.getvalue())
    def test_current_gate_failure_is_distinct_from_provider_send_and_never_sends(self):
        owner=inactive_owner();email='synthetic-owner@example.invalid'
        owner._OwnerIngress__email_sha=hashlib.sha256(email.encode()).hexdigest()
        owner._OwnerIngress__fence=SimpleNamespace(public_review=SimpleNamespace(valid_from_ms=0))
        owner._OwnerIngress__started=1;owner._OwnerIngress__last_wall=1
        owner._OwnerIngress__until=2**63;owner._OwnerIngress__last_monotonic=0;owner._OwnerIngress__monotonic=0
        output=StringIO()
        with redirect_stdout(output),self.assertRaises(ValueError):owner.send_email(email)
        observed=stages(output.getvalue())
        self.assertIn(dict(stage='CURRENT_STATE_GATE',result='DENY',authority='NONE',real_admission='NO'),observed)
        self.assertFalse(any(row['stage']=='PROVIDER_SEND_RESULT' for row in observed))
        self.assertNotIn(email,output.getvalue())
    def test_render_failure_identifies_get_stage_without_cookie_or_partial_form(self):
        service.CONTROLLER=InactiveController()
        obj=object.__new__(service.handler);obj.path='/api/n01/login';obj.command='GET'
        obj.wfile=BytesIO();obj.headers=Message();obj.send_response=Mock();obj.send_header=Mock();obj.end_headers=Mock()
        output=StringIO()
        with patch.object(service,'request_allowed',return_value=True),patch.object(service.CONTROLLER,'write_login',side_effect=ValueError('SECRET_SENTINEL')),redirect_stdout(output):obj.do_GET()
        self.assertIn(dict(stage='GET_FORM_RENDER',result='DENY',authority='NONE',real_admission='NO'),stages(output.getvalue()))
        self.assertFalse(any(row['stage']=='PREAUTH_COOKIE_ISSUANCE' for row in stages(output.getvalue())))
        self.assertNotIn('SECRET_SENTINEL',output.getvalue());self.assertNotIn(b'<form',obj.wfile.getvalue())


if __name__=='__main__':unittest.main()

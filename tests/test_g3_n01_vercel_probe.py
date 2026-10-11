"""Boundary-only simulated HTTP tests; never live runtime qualification."""
from email.message import Message
from io import BytesIO, StringIO
from contextlib import redirect_stdout
import json
import unittest
from unittest.mock import patch
from scripts import g3_n01_vercel_probe as p


def headers(host='nexus-g3-qual-abc123-tdy0225.vercel.app'):
    result=Message();result['Host']=host;result['x-vercel-oidc-token']='TEST_ONLY_NOT_AUTHORITY'
    return result


class RuntimeProbeTests(unittest.TestCase):
    def setUp(self):
        p.OUTCOME=None
        self.env={'VERCEL_ENV':'production','VERCEL_URL':'nexus-g3-qual-abc123-tdy0225.vercel.app'}
    def call(self, h=None, path='/api/n01-storage', method='GET'):
        obj=object.__new__(p.handler)
        obj.path=path;obj.command=method;obj.headers=h or headers();obj.wfile=BytesIO()
        obj.send_response=lambda status:setattr(obj,'status',status)
        obj.send_header=lambda *args:None;obj.end_headers=lambda:None
        log=StringIO()
        with patch.dict(p.os.environ,self.env,clear=True),redirect_stdout(log):obj.do_GET()
        self.assertEqual(json.loads(log.getvalue())['n01_runtime_readback'],json.loads(obj.wfile.getvalue()))
        return obj.status,obj.wfile.getvalue()
    def test_alias_is_denied_before_paid_io(self):
        with patch.object(p,'read_current') as io:
            self.assertEqual(self.call(headers('nexus-g3-qual.vercel.app'))[0],403)
            io.assert_not_called()
    def test_method_query_or_preview_cannot_invoke(self):
        with patch.object(p,'read_current') as io:
            self.assertEqual(self.call(method='POST')[0],403)
            self.assertEqual(self.call(path='/api/n01-storage?refresh=1')[0],403)
            self.env['VERCEL_ENV']='preview'
            self.assertEqual(self.call()[0],403);io.assert_not_called()
    def test_duplicate_native_header_or_origin_denied(self):
        duplicate=headers();duplicate['x-vercel-oidc-token']='OTHER_TEST_ONLY'
        origin=headers();origin['Origin']='https://unqualified.example'
        with patch.object(p,'read_current') as io:
            self.assertEqual(self.call(duplicate)[0],403)
            self.assertEqual(self.call(origin)[0],403);io.assert_not_called()
    def test_unknown_outcome_is_sanitized_terminal_no_retry(self):
        with patch.object(p,'read_current',side_effect=RuntimeError('SECRET_SENTINEL_NOT_A_CREDENTIAL')) as io:
            first=self.call();second=self.call()
            self.assertEqual(first[0],503);self.assertEqual(first,second)
            self.assertNotIn(b'SECRET_SENTINEL',first[1]);self.assertEqual(io.call_count,1)
    def test_cached_success_still_none_not_owner_context(self):
        value=dict(n01_vercel_status='TEST_ONLY_SIMULATED_VERIFIED',authority='NONE',real_admission='NO')
        with patch.object(p,'read_current',return_value=value) as io:
            first=self.call();second=self.call()
            self.assertEqual(first[0],200);self.assertEqual(first,second);self.assertEqual(io.call_count,1)
            self.assertNotIn(b'TEST_ONLY_NOT_AUTHORITY',first[1])
    def test_read_only_sdk_shape_rejects_mutation_before_client(self):
        from unittest.mock import Mock
        native=Mock();service=p.ReadOnlyService(native,'DDB',2)
        with self.assertRaises(ValueError):service.put_item(TableName=p.TABLE,Item={})
        native.put_item.assert_not_called();self.assertEqual(service.attempts,0)


if __name__=='__main__':unittest.main()

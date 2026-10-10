from pathlib import Path
import importlib.util, unittest
ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('factor_cleanup',ROOT/'scripts/verify_factor_cleanup.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)

class FactorCleanupArtifactTests(unittest.TestCase):
    def test_default_disabled_and_closed(self):
        blobs=M.compose(1791624600000)
        report=M.validate(blobs,1791624600000)
        self.assertFalse(report['enabled']);self.assertEqual(report['files'],5)
        self.assertEqual(report['real_admission_enabled'],'NO')

    def test_enabled_exact_scoped_artifact(self):
        self.assertTrue(M.validate(M.compose(1791624600000,True),1791624600000,True)['enabled'])

    def test_source_tampering_rejected(self):
        blobs=M.compose(1791624600000);blobs['lib/cleanup.js']+=b'\n'
        with self.assertRaises(RuntimeError):M.validate(blobs,1791624600000)

    def test_extra_files_rejected(self):
        blobs=M.compose(1791624600000);blobs['.env']=b'NO_SECRET'
        with self.assertRaises(RuntimeError):M.validate(blobs,1791624600000)

    def test_no_public_asset_or_user_delete_route(self):
        blobs=M.compose(1791624600000)
        self.assertFalse(any(n.startswith('public/') for n in blobs))
        self.assertIn(b"method === 'GET' ? '/v1/users/'",blobs['lib/cleanup.js'])
        self.assertIn(b"'/v1/users/totps/' + scope.exposed_totp_id",blobs['lib/cleanup.js'])

    def test_historical_diagnostic_remains_disabled(self):
        data=M.QR.G3.generation3_input()
        report=M.QR.validate(M.QR.compose(data),data)
        self.assertEqual(report['mode'],'FAKE_DISABLED')

    def test_fixed_operation_window(self):
        report=M.validate(M.compose(1791624600000),1791624600000)
        self.assertEqual(report['valid_until'],1791626400000)

    def test_historical_owner_binding(self):
        scope=M.reviewed_scope();registration=M.QR.G3.generation3_input()['provider']
        self.assertEqual(scope['owner_user_id'],registration['owner_user_id'])
        self.assertEqual(scope['project_id'],registration['project_id'])

if __name__=='__main__':unittest.main()

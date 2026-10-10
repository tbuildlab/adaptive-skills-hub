"""Closed Origin policy correction; fixtures cannot establish live authority."""
from pathlib import Path
import copy,importlib.util,subprocess,tempfile,unittest
SPEC=importlib.util.spec_from_file_location('owner_origin',Path(__file__).resolve().parents[1]/'scripts/verify_owner_origin.py')
M=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(M)
TS=importlib.util.spec_from_file_location('owner_form_tests',Path(__file__).with_name('test_owner_form_artifact.py'))
T=importlib.util.module_from_spec(TS);TS.loader.exec_module(T)
DATA=M.BASE.BASE.BASE.reviewed_public_input()

class OwnerOriginArtifact(unittest.TestCase):
    def reject(self,path,transform):
        b=M.compose(DATA);b[path]=transform(b[path])
        with self.assertRaises(RuntimeError):M.validate(b,DATA)
    def runtime(self,variant):
        script=T.RUNTIME.replace("if(variant==='SERVER_WRONG_ORIGIN')headers.origin='https://other.invalid';",
            "if(variant==='SERVER_WRONG_ORIGIN')headers.origin='https://other.invalid';\nif(variant==='SERVER_NULL_ORIGIN')headers.origin='null';\nif(variant==='SERVER_MISSING_ORIGIN')delete headers.origin;\nif(variant==='SERVER_SAME_SITE')headers['sec-fetch-site']='same-site';")
        with tempfile.TemporaryDirectory(prefix='nexus-g3-origin-offline-') as directory:
            root=Path(directory)
            for n,b in M.compose(DATA).items():
                p=root/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
            r=subprocess.run(['node','--input-type=module','-e',script,variant],cwd=root,env={'SystemRoot':r'C:\Windows'},capture_output=True,timeout=15)
            self.assertEqual(r.returncode,0,r.stderr.decode())
    def test_exact_inventory(self):self.assertEqual(M.validate(M.compose(DATA),DATA)['files'],19)
    def test_exact_two_file_delta(self):
        old=M.BASE.compose(DATA);self.assertEqual({n for n,b in M.compose(DATA).items() if b!=old[n]},{M.BASE.BASE.BASE.INPUT,'public/index.html'})
    def test_historical_native_hash(self):self.assertEqual(M.BASE.validate(M.BASE.compose(DATA),DATA)['zip_sha256'],'c8cc3405fade529dd0b11a378872c17bb4155bb5ffe9d29c7e62a10f48b4e31f')
    def test_public_policy_exact(self):self.assertIn(b'<meta name="referrer" content="strict-origin">',M.compose(DATA)['public/index.html'])
    def test_private_no_referrer_preserved(self):self.assertIn(b"'Referrer-Policy': 'no-referrer'",M.compose(DATA)[M.BASE.BASE.BASE.SERVICE])
    def test_global_no_referrer_preserved(self):self.assertEqual(M.compose(DATA)['vercel.json'],M.BASE.compose(DATA)['vercel.json'])
    def test_review_window_unchanged(self):
        a=M.validate(M.compose(DATA),DATA);b=M.BASE.validate(M.BASE.compose(DATA),DATA)
        self.assertEqual((a['public_review_valid_from'],a['public_review_valid_until']),(b['public_review_valid_from'],b['public_review_valid_until']))
    def test_deterministic_zip(self):
        b=M.compose(DATA);self.assertEqual(M.BASE.BASE.BASE.HISTORICAL.frozen_zip(b),M.BASE.BASE.BASE.HISTORICAL.frozen_zip(dict(reversed(list(b.items())))))
    def test_wrong_owner_input(self):
        d=copy.deepcopy(DATA);d['provider']['owner_user_id']='offline-impostor'
        with self.assertRaises(RuntimeError):M.compose(d)
    def test_unsafe_url_policy_rejected(self):self.reject('public/index.html',lambda b:b.replace(b'strict-origin',b'unsafe-url'))
    def test_get_form_rejected(self):self.reject('public/index.html',lambda b:b.replace(b'method="POST"',b'method="GET"'))
    def test_external_form_rejected(self):self.reject('public/index.html',lambda b:b.replace(b'action="/api/diagnostic"',b'action="https://other.invalid"'))
    def test_origin_bypass_rejected(self):self.reject(M.BASE.BASE.BASE.SERVICE,lambda b:b.replace(b'h.origin!==ORIGIN',b'false'))
    def test_server_null_origin_denied_zero_io(self):self.runtime('SERVER_NULL_ORIGIN')
    def test_server_missing_origin_denied_zero_io(self):self.runtime('SERVER_MISSING_ORIGIN')
    def test_same_site_denied_zero_io(self):self.runtime('SERVER_SAME_SITE')
    def test_valid_origin_prefactor_denied_zero_io(self):self.runtime('SERVER_STRING')
    def test_current_local_form_guard(self):self.runtime('ACCEPT')

if __name__=='__main__':unittest.main()

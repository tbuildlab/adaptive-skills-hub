"""Public key/certificate consistency; ephemeral keys are not source authority."""
import base64
import copy
from datetime import datetime,timedelta,timezone
import hashlib
import json
import unittest

from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from ash import g3_n01_public_pin as pin
from tests import test_g3_n01_owner_context as fixture


class PublicPinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fixture.OwnerContextTests.setUpClass()
        cls.private=fixture.OwnerContextTests.private
        cls.core=fixture.OwnerContextTests.keys[0]
        now=datetime.now(timezone.utc)
        name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,'Ephemeral consistency test')])
        certificate=x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(
            cls.private.public_key()).serial_number(1).not_valid_before(now-timedelta(days=1)).not_valid_after(
            now+timedelta(days=1)).sign(cls.private,hashes.SHA256())
        cls.der=certificate.public_bytes(serialization.Encoding.DER)
    def value(self):
        return dict(keys=[dict(self.core,key_ops=['verify'],x5c=[base64.b64encode(self.der).decode()],
            x5tS256=base64.urlsafe_b64encode(hashlib.sha256(self.der).digest()).rstrip(b'=').decode())],
            request_id='request-id-test-aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',status_code=200)
    def check(self,value):return pin.normalize_public_jwks(json.dumps(value).encode())
    def test_consistent_native_public_fields_normalize_to_closed_core(self):
        self.assertEqual(self.check(self.value()),(self.core,))
    def test_certificate_is_optional_but_not_a_trust_claim(self):
        self.assertEqual(self.check(dict(keys=[self.core])),(self.core,))
    def test_private_unknown_or_bad_use_fields_fail_before_normalization(self):
        for extra in ({'d':'private'},{'arbitrary':'unknown'},{'key_ops':['sign']},{'use':'enc'}):
            value=self.value();value['keys'][0].update(extra)
            with self.subTest(extra=tuple(extra)),self.assertRaisesRegex(ValueError,'N01_PUBLIC_PIN_DENY'):self.check(value)
    def test_thumbprint_mismatch_or_alias_ambiguity_denies(self):
        for extra in ({'x5tS256':'a'*43},{'x5t#S256':self.value()['keys'][0]['x5tS256']}):
            value=self.value();value['keys'][0].update(extra)
            with self.assertRaises(ValueError):self.check(value)
    def test_certificate_public_key_mismatch_denies(self):
        value=self.value()
        other=rsa.generate_private_key(public_exponent=65537,key_size=2048).public_key().public_numbers().n
        value['keys'][0]['n']=base64.urlsafe_b64encode(other.to_bytes(256,'big')).rstrip(b'=').decode()
        with self.assertRaises(ValueError):self.check(value)
    def test_invalid_certificate_duplicate_key_or_envelope_denies(self):
        for change in (lambda v:v['keys'][0].update(x5c=['YWJj']),
                       lambda v:v['keys'].append(copy.deepcopy(v['keys'][0])),
                       lambda v:v.update(status_code=True),lambda v:v.update(unknown=1),
                       lambda v:v.update(request_id='request-id-live-aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa')):
            value=self.value();change(value)
            with self.assertRaises(ValueError):self.check(value)
    def test_duplicate_json_and_oversized_input_deny(self):
        for raw in (b'{"keys":[],"keys":[]}',b' '*16385):
            with self.assertRaises(ValueError):pin.normalize_public_jwks(raw)


if __name__=='__main__':unittest.main()

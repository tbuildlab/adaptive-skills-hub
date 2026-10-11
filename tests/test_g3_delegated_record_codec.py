"""Versioned structural examples only; never production gate evidence."""
import copy
import unittest
from ash import g3_delegated_record_codec as d, g3_record_codec as old
from tests.test_g3_production_metadata import samples


def delegated(body):
    def convert(value):
        if type(value) is dict:
            if set(value) == {'id', 'body_sha256'} and value['id'].startswith(old.PREFIX):
                domain, _, digest = value['id'].rpartition(':')
                return dict(id=domain[:-1]+'2:'+digest, body_sha256=value['body_sha256'])
            return {k: convert(v) for k,v in value.items()}
        if type(value) is list:
            return [convert(v) for v in value]
        return value
    value=convert(copy.deepcopy(body))
    value['schema_version']=value['schema_version'][:-1]+'2'
    value.update(authority_mode=d.MODE,authority_config_sha256='c'*64,d04_historical_status=d.D04_STATUS)
    if 'gate_facts' in value:
        value['gate_facts']=[f for f in value['gate_facts'] if f['kind']!='D04_EXECUTOR_EXCLUSION']
    return value


class DelegatedRecordCodecTests(unittest.TestCase):
    def parse(self,value):return d.parse_metadata(old.canonical_bytes(value))
    def test_all_closed_shapes_remain_untrusted(self):
        for source in samples():
            with self.subTest(kind=source['schema_version'],phase=source.get('phase')):
                value=delegated(source);parsed=self.parse(value)
                self.assertEqual(parsed.to_dict(),value)
                self.assertEqual(parsed.authority,'NONE')
                self.assertEqual(parsed.semantic_validation,'NOT_PERFORMED')
                self.assertIn('.v2:',parsed.record_id)
    def test_old_v1_contract_and_ids_are_not_redefined(self):
        value=samples()[4];old_id=old.parse_metadata(old.canonical_bytes(value)).record_id
        with self.assertRaises(old.MetadataError):self.parse(value)
        modern=delegated(value)
        with self.assertRaises(old.MetadataError):old.parse_metadata(old.canonical_bytes(modern))
        self.assertNotEqual(self.parse(modern).record_id,old_id)
        value['gate_facts'].pop(2)
        with self.assertRaises(old.MetadataError):old.parse_metadata(old.canonical_bytes(value))
    def test_mode_and_config_are_mandatory(self):
        for key,bad in [('authority_mode','OWNER_EXCLUSIVE'),('authority_config_sha256','x'),
                        ('d04_historical_status','PASS')]:
            value=delegated(samples()[4]);value[key]=bad
            with self.subTest(key=key),self.assertRaises(old.MetadataError):self.parse(value)
            del value[key]
            with self.subTest(missing=key),self.assertRaises(old.MetadataError):self.parse(value)
    def test_d04_cannot_be_substituted_for_any_mandatory_gate(self):
        for index in range(7):
            value=delegated(samples()[4]);value['gate_facts'][index]['kind']='D04_EXECUTOR_EXCLUSION'
            with self.subTest(index=index),self.assertRaises(old.MetadataError):self.parse(value)
    def test_unknown_or_conditional_cannot_qualify_positive_shape(self):
        for source in (samples()[4],samples()[5]):
            for index in range(7):
                for verdict in ('UNKNOWN','FAIL','CONDITIONAL'):
                    value=delegated(source);value['gate_facts'][index]['verdict']=verdict
                    with self.subTest(index=index,verdict=verdict),self.assertRaises(old.MetadataError):self.parse(value)
    def test_extra_eighth_gate_and_reordering_deny(self):
        value=delegated(samples()[4]);value['gate_facts'].append(copy.deepcopy(value['gate_facts'][0]))
        with self.assertRaises(old.MetadataError):self.parse(value)
        value=delegated(samples()[4]);value['gate_facts'].reverse()
        with self.assertRaises(old.MetadataError):self.parse(value)
    def test_legacy_anchor_cannot_enter_new_lineage(self):
        value=delegated(samples()[0]);value['stamp']['base_checkpoint']=samples()[0]['stamp']['base_checkpoint']
        with self.assertRaises(old.MetadataError):self.parse(value)
    def test_deadlines_expiry_and_grant_read_binding_remain_exact(self):
        for mutation in ('expiry','grant','stale_gate','context'):
            value=delegated(samples()[4])
            if mutation=='expiry':value['use_until_ms']=value['evaluated_at_ms']
            elif mutation=='grant':value['revocation_read']['grant']['id']=value['grant']['id'][:-1]+'c'
            elif mutation=='stale_gate':value['gate_facts'][0]['observed_at_ms']=5000
            else:value['owner_context']['context_expires_at_ms']=value['use_until_ms']-1
            with self.subTest(mutation=mutation),self.assertRaises(old.MetadataError):self.parse(value)
    def test_deny_and_unknown_result_never_gain_authority(self):
        value=delegated(samples()[4]);value.update(disposition='DENIED',reason_codes=['GATE_UNKNOWN'],use_until_ms=value['evaluated_at_ms'])
        value['gate_facts'][0]['verdict']='UNKNOWN'
        self.assertEqual(self.parse(value).authority,'NONE')
        self.assertEqual(self.parse(delegated(samples()[6])).authority,'NONE')
    def test_principal_and_material_are_preserved_without_executor_substitution(self):
        before=samples()[0];after=delegated(before)
        self.assertEqual(self.parse(after).to_dict()['binding']['owner'],before['binding']['owner'])
        self.assertEqual(after['material'],before['material'])
    def test_serialized_record_cannot_claim_authenticated_fields(self):
        value=delegated(samples()[4]);value['qualified']=True
        with self.assertRaises(old.MetadataError):self.parse(value)
    def test_malformed_and_unsupported_versions_fail_closed(self):
        for raw in (b'',b'null',b'{}',b'[]',b'{"schema_version":1}',b'{"schema_version":"unsupported"}'):
            with self.subTest(raw=raw),self.assertRaises(old.MetadataError):d.parse_metadata(raw)


if __name__=='__main__':unittest.main()

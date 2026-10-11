"""Validate inert documentary knowledge; no production importer or rule loader."""
from copy import deepcopy
import hashlib
from pathlib import Path, PurePosixPath
import re
import unittest

from ash.ecosystem_models import parse_json_bytes, canonical_json_bytes
from ash.g1_profiles import exact, token, sha, tokens
from ash import g4_contracts as g4
from ash.g4_host_adapter import pre_execution_gate, StructuralSession
from tests.g4_fixtures import bundle, request, NOW, domain_body

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'research/nexus-website-experience-pack-v1.json'
CATEGORIES = {'planning', 'ux', 'visual_qa', 'responsive', 'accessibility',
              'interaction', 'content_truthfulness', 'forms', 'integrations',
              'deployment', 'performance', 'testing', 'production_hardening',
              'acceptance_freeze'}


def read_pack(raw):
    """Test-only closed curation check using existing frozen parsers/validators."""
    p = parse_json_bytes(raw, maximum_bytes=65536, label='website experience')
    g4.canonical(p)
    exact(p, {'schema_version', 'title', 'basis', 'advisory_only', 'dispatch_authority',
              'sources', 'lessons', 'context_versions', 'audit_counts'})
    if (p['schema_version'] != 'nexus.website-experience-pack.v1'
            or p['basis'] != 'ADVISORY_CONTEXT_ONLY' or p['advisory_only'] is not True
            or p['dispatch_authority'] != 'none'):
        raise ValueError('NON_AUTHORITATIVE_KNOWLEDGE_REQUIRED')
    source_ids = set()
    for source in p['sources']:
        exact(source, {'id', 'path', 'sha256'})
        token(source['id']); sha(source['sha256'])
        path = PurePosixPath(source['path'])
        if (source['id'] in source_ids or path.is_absolute() or '..' in path.parts
                or not source['path'].startswith('docs/') or path.suffix != '.md'):
            raise ValueError('SOURCE_REF_INVALID')
        source_ids.add(source['id'])
    ids = set(); current_keys = set()
    for lesson in p['lessons']:
        exact(lesson, {'id', 'semantic_key', 'state', 'superseded_by', 'categories',
                       'advice', 'applicability', 'limitations', 'provenance', 'origin'})
        token(lesson['id']); token(lesson['semantic_key'])
        if lesson['id'] in ids or lesson['origin'] not in {'EXISTING', 'INGESTED_NOW'}:
            raise ValueError('DUPLICATE_ORIGIN_INVALID')
        ids.add(lesson['id'])
        categories = tokens(lesson['categories'], nonempty=True)
        if not set(categories) <= CATEGORIES or not lesson['provenance']:
            raise ValueError('CURATION_SCOPE_INVALID')
        refs = set()
        for source in lesson['provenance']:
            exact(source, {'source_id', 'locator'})
            if not re.fullmatch(r'[KLRMN][0-9]{2}|D0[12]',source['locator']):
                raise ValueError('LOCATOR_INVALID')
            pair = (source['source_id'], source['locator'])
            if source['source_id'] not in source_ids or pair in refs:
                raise ValueError('PROVENANCE_INVALID')
            refs.add(pair)
        if lesson['state'] == 'CURRENT':
            if lesson['semantic_key'] in current_keys or lesson['superseded_by'] is not None:
                raise ValueError('DUPLICATE_CURRENT_SEMANTIC_KEY')
            current_keys.add(lesson['semantic_key'])
        elif lesson['state'] != 'SUPERSEDED' or not lesson['superseded_by']:
            raise ValueError('STATE_INVALID')
    for lesson in p['lessons']:
        if lesson['state'] == 'SUPERSEDED':
            if lesson['superseded_by'] not in ids or lesson['superseded_by'] == lesson['id']:
                raise ValueError('SUPERSESSION_INVALID')
            target = next(v for v in p['lessons'] if v['id'] == lesson['superseded_by'])
            if target['state'] != 'CURRENT' or target['semantic_key'] != lesson['semantic_key']:
                raise ValueError('SUPERSESSION_INVALID')
    version_ids = {v['id'] for v in p['context_versions']}
    if len(version_ids) != len(p['context_versions']):
        raise ValueError('VERSION_DUPLICATE')
    for v in p['context_versions']:
        exact(v, {'id', 'state', 'superseded_by', 'summary'})
        if v['state'] == 'SUPERSEDED':
            targets = [t for t in p['context_versions'] if t['id'] == v['superseded_by']]
            if len(targets) != 1 or targets[0]['state'] != 'CURRENT':
                raise ValueError('VERSION_SUPERSESSION_INVALID')
        elif v['state'] != 'CURRENT' or v['superseded_by'] is not None:
            raise ValueError('VERSION_STATE_INVALID')
    return p


def current_lessons(p):
    return [v for v in p['lessons'] if v['state'] == 'CURRENT']


class HistoricalExperienceTests(unittest.TestCase):
    def setUp(self):
        self.p = read_pack(PACK.read_bytes())

    def test_closed_parse_and_category_retrieval(self):
        self.assertEqual(read_pack(canonical_json_bytes(self.p)), self.p)
        self.assertEqual(len(current_lessons(self.p)), 41)
        for category in CATEGORIES:
            self.assertTrue([v for v in current_lessons(self.p) if category in v['categories']])

    def test_provenance_digest_and_original_archives(self):
        for source in self.p['sources']:
            raw=(ROOT/source['path']).read_bytes().replace(b'\r\n',b'\n')
            self.assertEqual(hashlib.sha256(raw).hexdigest(), source['sha256'])
        for name, expected, size in [
            ('nexus-northstar-demo2-project-memory-v1.md','4170f3f387d4b6625adab49cb2d0f5f5af78fb7a74f4233fa808dcc170cb2dd8',46088),
            ('nexus-apex-aircare-demo3-project-memory-v1.md','de9abce0578e7dd1b9e398cd177e0c9b79d17fde67eccaa663ef9487a1e01f2e',48732),
        ]:
            raw=(ROOT/'docs'/name).read_bytes().replace(b'\r\n',b'\n')
            archive=raw.split(b'````markdown\n',1)[1].rsplit(b'````',1)[0]
            self.assertEqual(len(archive),size)
            self.assertEqual(hashlib.sha256(archive).hexdigest(),expected)

    def test_semantic_duplicates_and_duplicate_provenance_refused(self):
        p=deepcopy(self.p); old=deepcopy(p['lessons'][0]);old['id']='another'
        p['lessons'].append(old)
        with self.assertRaises(ValueError):read_pack(canonical_json_bytes(p))
        p=deepcopy(self.p);p['lessons'][0]['provenance']*=2
        with self.assertRaises(ValueError):read_pack(canonical_json_bytes(p))

    def test_superseded_records_cannot_silently_become_current(self):
        p=deepcopy(self.p);old=deepcopy(p['lessons'][0])
        old.update(id='historical',state='SUPERSEDED',superseded_by='w01')
        p['lessons'].append(old)
        validated=read_pack(canonical_json_bytes(p))
        self.assertNotIn('historical',[v['id'] for v in current_lessons(validated)])
        old['state']='CURRENT';old['superseded_by']=None
        with self.assertRaises(ValueError):read_pack(canonical_json_bytes(p))
        p=deepcopy(self.p);p['context_versions'][0]['state']='CURRENT'
        with self.assertRaises(ValueError):read_pack(canonical_json_bytes(p))

    def test_malformed_sensitive_and_unrelated_material_refused(self):
        mutations=[{'password':'private'},{'dispatch_authority':'execute'}, {'advisory_only':False}]
        for changes in mutations:
            p=deepcopy(self.p);p.update(changes)
            with self.assertRaises(ValueError):read_pack(canonical_json_bytes(p))
        p=deepcopy(self.p);p['lessons'][0]['advice']='Bearer sensitive-value'
        with self.assertRaises(ValueError):read_pack(canonical_json_bytes(p))
        p=deepcopy(self.p);p['lessons'][0]['provenance'][0]['source_id']='unrelated-private-chat'
        with self.assertRaises(ValueError):read_pack(canonical_json_bytes(p))
        for raw in (b'{"a":1,"a":2}',b'{"a":NaN}',b'"'+b'x'*65536+b'"'):
            with self.assertRaises(ValueError):read_pack(raw)

    def test_recorded_inventory_preserves_unknowns_and_excludes_style_rules(self):
        counts=self.p['audit_counts']
        self.assertEqual(counts['source_items'], counts['canonical_current_lessons']+counts['merged_duplicate_or_partial_items']+counts['not_reusable_items'])
        self.assertEqual(counts['existing_source_items'],52)
        self.assertEqual(sum(v['origin']=='INGESTED_NOW' for v in self.p['lessons']),counts['new_unique_lessons'])
        self.assertEqual(sum(v['state']=='SUPERSEDED' for v in self.p['context_versions']),counts['superseded_context_versions'])
        corpus=' '.join(v['advice']+' '+v['limitations'] for v in self.p['lessons'])
        for grade in ('UNKNOWN','UNVERIFIED','DEFERRED'):
            self.assertIn(grade,corpus)
        self.assertNotIn('K20',[r['locator'] for v in self.p['lessons'] for r in v['provenance']])
        self.assertNotIn('K21',[r['locator'] for v in self.p['lessons'] for r in v['provenance']])
        self.assertNotRegex(corpus,r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}')

    def test_existing_g4_can_reference_knowledge_without_admission(self):
        b=bundle();digest=hashlib.sha256(PACK.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
        original=self.p['sources'][-1]['sha256']
        b['source_refs'] += [digest,original]
        b['source_digests'][digest]=digest
        body=b['context'].to_dict()
        source=deepcopy(body['sources'][0])
        source.update(ref=digest,sha256=digest,transformation='DERIVED',original_ref=original)
        body['sources'].append(source);b['context']=g4.record('context-manifest',body)
        session=StructuralSession();r=request();fixture=session.fixture(r,now=NOW)
        verdict=session.check_domain(r,fixture,bundle=b,now=NOW)
        self.assertEqual(verdict['status'],'ALLOW_STRUCTURAL_TEST_ONLY')
        self.assertEqual(verdict['dispatch_authority'],'none')
        for value,authority in [(self.p,None),(r,self.p),(r,fixture)]:
            self.assertEqual(pre_execution_gate(value,authority,now=NOW)['status'],'DENY')
        b['source_refs'].remove(original)
        with self.assertRaises(g4.G4Error):g4.validate_domain_bundle(**b)


if __name__=='__main__':unittest.main()

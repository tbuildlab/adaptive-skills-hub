"""Validate inert documentary knowledge; no production importer or rule loader."""
from copy import deepcopy
from collections import Counter
import hashlib
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit
import re
import unittest

from ash.ecosystem_models import parse_json_bytes, canonical_json_bytes
from ash.g1_profiles import exact, token, sha, tokens, integer
from ash import g4_contracts as g4
from ash.g4_host_adapter import pre_execution_gate, StructuralSession
from tests.g4_fixtures import bundle, request, NOW, domain_body

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / 'research/nexus-website-experience-pack-v1.json'
REFERENCES = ROOT / 'research/nexus-website-reference-index-v1.json'
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
            if not re.fullmatch(r'[KLRMNF][0-9]{2}|D0[12]',source['locator']):
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


def read_reference_index(raw, pack):
    """Test-only documentary check; cannot authorize reference execution."""
    p=parse_json_bytes(raw,maximum_bytes=65536,label='reference index')
    g4.canonical(p)
    exact(p,{'schema_version','basis','advisory_only','dispatch_authority',
             'evidence_register','evidence_register_sha256','sources','lesson_aliases','counts'})
    if (p['schema_version']!='nexus.website-reference-index.v1'
            or p['basis']!='ADVISORY_CONTEXT_ONLY' or p['advisory_only'] is not True
            or p['dispatch_authority']!='none'):
        raise ValueError('ADVISORY_REFERENCE_REQUIRED')
    register=next(s for s in pack['sources'] if s['id']=='reference_evidence')
    if p['evidence_register']!=register['path'] or p['evidence_register_sha256']!=register['sha256']:
        raise ValueError('REFERENCE_EVIDENCE_BINDING_INVALID')
    states={'CONFIRMED_USED','CONSULTED_ONLY','CONSIDERED','REJECTED',
            'SUPERSEDED','NOT_FOUND','INSUFFICIENT_EVIDENCE'}
    ids=set()
    for r in p['sources']:
        exact(r,{'id','name','status','purpose','reference_links','observations','limitations'})
        token(r['id'])
        if r['id'] in ids or r['status'] not in states:
            raise ValueError('REFERENCE_ID_STATUS_INVALID')
        ids.add(r['id'])
        for link in r['reference_links']:
            if link!=p['evidence_register']+'#ref-'+r['id']:
                raise ValueError('REFERENCE_LINK_METADATA_ONLY')
        for o in r['observations']:
            exact(o,{'project','status','artifact','locator','detail'})
            token(o['artifact'])
            if o['project'] not in {'noma','apex','northstar','meranti'} or o['status'] not in states:
                raise ValueError('OBSERVATION_INVALID')
        if r['status']=='CONFIRMED_USED' and not any(o['status']=='CONFIRMED_USED' for o in r['observations']):
            raise ValueError('CONFIRMED_USE_REQUIRES_OBSERVATION')
        if r['status']=='NOT_FOUND' and (r['observations'] or r['reference_links']):
            raise ValueError('NOT_FOUND_HAS_UNSUPPORTED_EVIDENCE')
    locators=set()
    for a in p['lesson_aliases']:
        exact(a,{'locator','lesson_id','disposition','reference_ids','interpretation'})
        if not re.fullmatch(r'F[0-9]{2}',a['locator']) or a['locator'] in locators:
            raise ValueError('REFERENCE_ALIAS_DUPLICATE_INVALID')
        locators.add(a['locator'])
        if a['disposition'] not in {'NEW','DUPLICATE'} or not a['reference_ids'] or not set(a['reference_ids'])<=ids:
            raise ValueError('REFERENCE_ALIAS_SCOPE_INVALID')
        lessons=[v for v in current_lessons(pack) if v['id']==a['lesson_id']]
        if len(lessons)!=1 or {'source_id':'reference_evidence','locator':a['locator']} not in lessons[0]['provenance']:
            raise ValueError('REFERENCE_LESSON_PROVENANCE_INVALID')
    c=p['counts'];counts=Counter(r['status'] for r in p['sources'])
    expected={'reference_source_count':len(ids),**{s.lower()+'_count':counts[s] for s in states},
              'new_reusable_reference_lessons':sum(a['disposition']=='NEW' for a in p['lesson_aliases']),
              'duplicate_reference_lessons':sum(a['disposition']=='DUPLICATE' for a in p['lesson_aliases'])}
    exact(c,set(expected))
    for key,value in c.items():
        integer(value)
        if value!=expected[key]:raise ValueError('REFERENCE_COUNT_INVALID')
    return p


class HistoricalExperienceTests(unittest.TestCase):
    def setUp(self):
        self.p = read_pack(PACK.read_bytes())

    def test_closed_parse_and_category_retrieval(self):
        self.assertEqual(read_pack(canonical_json_bytes(self.p)), self.p)
        self.assertEqual(len(current_lessons(self.p)), 44)
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

    def test_reference_evidence_states_and_source_binding(self):
        p=read_reference_index(REFERENCES.read_bytes(),self.p)
        source=self.p['sources'][-1]
        self.assertEqual(hashlib.sha256((ROOT/source['path']).read_bytes().replace(b'\r\n',b'\n')).hexdigest(),p['evidence_register_sha256'])
        by_id={r['id']:r for r in p['sources']}
        self.assertEqual(by_id['impeccable']['status'],'CONFIRMED_USED')
        self.assertTrue(any(o['project']=='northstar' and o['status']=='INSUFFICIENT_EVIDENCE' for o in by_id['impeccable']['observations']))
        self.assertTrue(any(o['project']=='noma' and o['status']=='CONSULTED_ONLY' for o in by_id['impeccable']['observations']))
        self.assertTrue(any(o['status']=='SUPERSEDED' for o in by_id['bencho']['observations']))
        for name in ('arlan','amieiro','libraries-dev'):
            self.assertEqual(by_id[name]['status'],'NOT_FOUND')
            self.assertIn('UNKNOWN',by_id[name]['limitations'])
        register=(ROOT/p['evidence_register']).read_text(encoding='utf-8')
        for r in p['sources']:
            for o in r['observations']:self.assertIn('| '+o['artifact']+' |',register)
            for link in r['reference_links']:self.assertIn('id="'+link.split('#')[1]+'"',register)
        for url in re.findall(r'\]\((https://[^)]+)\)',register):
            u=urlsplit(url)
            self.assertTrue(u.hostname)
            self.assertFalse(u.username or u.password or u.query or u.fragment)

    def test_reference_alias_deduplication_counts_and_authority(self):
        p=read_reference_index(REFERENCES.read_bytes(),self.p)
        self.assertEqual(p['counts']['reference_source_count'],27)
        self.assertEqual(p['counts']['new_reusable_reference_lessons'],3)
        self.assertEqual(p['counts']['duplicate_reference_lessons'],13)
        for a in p['lesson_aliases']:
            if a['disposition']=='NEW':self.assertIn(a['lesson_id'],{'w42','w43','w44'})
            else:self.assertNotIn(a['lesson_id'],{'w42','w43','w44'})
        self.assertEqual(pre_execution_gate(p,None,now=NOW)['status'],'DENY')
        self.assertEqual(pre_execution_gate(request(),p,now=NOW)['status'],'DENY')

    def test_reference_malformed_links_claims_and_duplicates_refused(self):
        base=read_reference_index(REFERENCES.read_bytes(),self.p)
        for mutation in ('authority','status','count','duplicate','secret','account_link','unbound','unsupported_use'):
            p=deepcopy(base)
            if mutation=='authority':p['dispatch_authority']='execute'
            if mutation=='status':p['sources'][0]['status']='EXECUTED_PASS'
            if mutation=='count':p['counts']['confirmed_used_count']+=1
            if mutation=='duplicate':p['lesson_aliases'].append(deepcopy(p['lesson_aliases'][0]))
            if mutation=='secret':p['sources'][0]['limitations']='Bearer sensitive-value'
            if mutation=='account_link':p['sources'][0]['reference_links']=['https://example.invalid/?session=value']
            if mutation=='unbound':p['evidence_register_sha256']='0'*64
            if mutation=='unsupported_use':p['sources'][0]['observations']=[]
            with self.subTest(mutation=mutation),self.assertRaises(ValueError):
                read_reference_index(canonical_json_bytes(p),self.p)


if __name__=='__main__':unittest.main()

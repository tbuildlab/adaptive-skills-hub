"""Synthetic renderer/ingress contracts only; no Owner or live consent proof."""
import copy
from html.parser import HTMLParser
import json
import unittest
from urllib.parse import urlencode

from ash import g3_n02_presentation as page
from ash import g3_delegated_record_codec as records
from tests import g3_delegated_state_fixtures as fixtures


class Display(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True);self.tags=[];self.pre=[];self.current=None;self.buttons=[]
    def handle_starttag(self,tag,attrs):
        self.tags.append((tag,dict(attrs)))
        if tag=='pre':self.current=''
        if tag=='button':self.buttons.append(dict(attrs))
    def handle_data(self,data):
        if self.current is not None:self.current+=data
    def handle_endtag(self,tag):
        if tag=='pre':self.pre.append(self.current);self.current=None


def material():
    _,bodies,_,_=fixtures.state()
    values=[records.parse_metadata(raw).to_dict() for raw in bodies.values()
            if json.loads(raw).get('schema_version','').endswith('.v2')]
    challenge=next(value for value in values if value['schema_version']==records.PREFIX+'authority-challenge.v2')
    view=next(value for value in values if value['schema_version']==records.PREFIX+'presentation-view.v2')
    view['template_revision']=page.TEMPLATE_REVISION
    return challenge,view


def encode(challenge,view):
    raw=records.canonical_bytes(challenge);parsed=records.parse_metadata(raw)
    view=copy.deepcopy(view)
    view['challenge']=dict(id=parsed.record_id,body_sha256=parsed.body_sha256)
    projection=dict(challenge_body=challenge,owner_context=view['owner_context'],
        template_revision=view['template_revision'],expires_at_ms=view['expires_at_ms'])
    view['presentation_sha256']=records.domain_digest(records.PREFIX+'presentation-material.v1',projection)
    return raw,records.canonical_bytes(view)


class PresentationTests(unittest.TestCase):
    def setUp(self):
        self.challenge,self.view=material();self.csrf='a'*64
        self.now=max(self.challenge['issued_at_ms'],self.view['issued_at_ms'])
        self.host='nexus-g3-qual-exact-tdy0225.vercel.app'
    def render(self):return page.render(*encode(self.challenge,self.view),csrf=self.csrf,now_ms=self.now)
    def fields(self,shown):
        return dict(csrf=self.csrf,choice='CONFIRM',**{name:getattr(shown,name)
            for name in ('challenge_id','view_id','proposal_id','nonce','presentation_sha256')})
    def submit(self,raw,shown,**changes):
        arguments=dict(csrf=self.csrf,origin='https://'+self.host,host=self.host,expected_host=self.host,
            method='POST',content_type='application/x-www-form-urlencoded',now_ms=self.now)
        arguments.update(changes)
        return page.compare_post(raw,shown,**arguments)
    def test_complete_untruncated_material_and_exact_two_explicit_controls(self):
        shown=self.render();display=Display();display.feed(shown.html.decode())
        sections=[json.loads(text) for text in display.pre]
        self.assertEqual(len(sections),len(page.LABELS))
        for value in (self.challenge['material']['targets'],self.challenge['material']['operations']):
            self.assertIn(value,sections)
        self.assertIn(dict(scope=self.challenge['material']['scope'],scope_sha256=self.challenge['material']['scope_sha256']),sections)
        self.assertEqual([button['value'] for button in display.buttons],['CONFIRM','DENY'])
        self.assertEqual(shown.authority,'NONE')
        self.assertFalse(any('checked' in attrs or 'selected' in attrs for _,attrs in display.tags))
        self.assertFalse(any(tag in ('script','iframe','img','a','textarea') for tag,_ in display.tags))
        hidden=[attrs for tag,attrs in display.tags if tag=='input']
        self.assertTrue(all(row['name'] in page.FORM_FIELDS for row in hidden))
    def test_html_directional_and_control_material_is_data_only(self):
        self.challenge['material']['effect_explanation']='</pre><script>alert(1)</script> & " Full material'
        value=self.challenge['material']
        self.challenge['proposal_id']=records.PREFIX+'proposal-material.v1:'+records.domain_digest(records.PREFIX+'proposal-material.v1',value)
        shown=self.render();display=Display();display.feed(shown.html.decode())
        self.assertFalse(any(tag=='script' for tag,_ in display.tags))
        self.assertNotIn('\u202e',shown.html.decode())
        self.assertEqual(json.loads(display.pre[8])['explanation'],value['effect_explanation'])
        _,view=encode(self.challenge,self.view)
        for invalid in ('\u202e','\n','\x00'):
            value['effect_explanation']=invalid
            raw=json.dumps(self.challenge,ensure_ascii=False).encode()
            with self.assertRaises(ValueError):page.render(raw,view,csrf=self.csrf,now_ms=self.now)
    def test_deterministic_output_and_exact_template_config_stamp_digest(self):
        shown=self.render();self.assertEqual(shown,self.render())
        for field,value in (('template_revision','b'*64),('authority_config_sha256','d'*64),
                            ('stamp',dict(self.view['stamp'],incarnation='wrong'))):
            original=self.view[field];self.view[field]=value
            with self.assertRaises(ValueError):self.render()
            self.view[field]=original
        raw,view=encode(self.challenge,self.view)
        value=records.parse_metadata(view).to_dict();value['presentation_sha256']='b'*64
        with self.assertRaises(ValueError):page.render(raw,records.canonical_bytes(value),csrf=self.csrf,now_ms=self.now)
    def test_missing_corrupt_records_and_unsupported_schema_deny(self):
        raw,view=encode(self.challenge,self.view)
        for args in ((b'{}',view),(raw,b'{}'),(raw+b'\n',view),(view,raw)):
            with self.assertRaises(ValueError):page.render(*args,csrf=self.csrf,now_ms=self.now)
    def test_issue_expiry_context_and_unbounded_or_bad_csrf_deny(self):
        raw,view=encode(self.challenge,self.view)
        for now in (self.now-1,self.view['expires_at_ms'],True,-1):
            with self.assertRaises(ValueError):page.render(raw,view,csrf=self.csrf,now_ms=now)
        for csrf in ('',self.csrf+'a','<script>','A'*64):
            with self.assertRaises(ValueError):page.render(raw,view,csrf=csrf,now_ms=self.now)
    def test_both_exact_decisions_remain_untrusted_none_without_execution(self):
        shown=self.render();fields=self.fields(shown)
        for choice in ('CONFIRM','DENY'):
            fields['choice']=choice;result=self.submit(urlencode(fields).encode(),shown)
            self.assertEqual((result.choice,result.authority),(choice,'NONE'))
            self.assertFalse(hasattr(result,'grant'))
    def test_missing_duplicate_extra_malformed_and_unknown_choice_deny(self):
        shown=self.render();fields=self.fields(shown);raw=urlencode(fields).encode()
        variants=[raw+b'&choice=DENY',raw+b'&unknown=x',b'csrf=%zz',b'\xff',b'x'*4097]
        for key in fields:
            variant=dict(fields);del variant[key];variants.append(urlencode(variant).encode())
        for choice in ('confirm','APPROVE','', 'CONFIRM\x00'):
            variants.append(urlencode(dict(fields,choice=choice)).encode())
        for variant in variants:
            with self.assertRaisesRegex(ValueError,'^N02_DECISION_INPUT_DENIED$'):self.submit(variant,shown)
    def test_wrong_origin_host_method_media_and_expiry_deny(self):
        shown=self.render();raw=urlencode(self.fields(shown)).encode()
        for changes in ({'origin':None},{'origin':'null'},{'origin':'https://attacker.example'},
            {'host':self.host+':443'},{'expected_host':'attacker.example'},{'method':'GET'},
            {'content_type':'application/json'},{'now_ms':shown.expires_at_ms}):
            with self.assertRaises(ValueError):self.submit(raw,shown,**changes)
    def test_every_frozen_join_and_csrf_mismatch_denies(self):
        shown=self.render();fields=self.fields(shown)
        for key in fields:
            if key=='choice':continue
            value=dict(fields);value[key]='b'*64
            with self.assertRaises(ValueError):self.submit(urlencode(value).encode(),shown)
    def test_response_policy_blocks_scripts_frames_fetch_and_cache(self):
        headers=page.response_headers()
        self.assertEqual(headers['Cache-Control'],'no-store')
        self.assertEqual(headers['X-Frame-Options'],'DENY')
        for directive in ("default-src 'none'","script-src 'none'","form-action 'self'","frame-ancestors 'none'"):
            self.assertIn(directive,headers['Content-Security-Policy'])
        self.assertNotIn('Set-Cookie',headers)


if __name__=='__main__':unittest.main()

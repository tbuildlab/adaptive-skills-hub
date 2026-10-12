"""Fixed N02 rendering and untrusted POST comparison; never consent authority.

The protected N01 runtime must independently supply current retained membership,
authenticated Owner/session, source enrollment and transaction serialization.
Matching rendered hashes or this public NONE result cannot replace those gates.
There is no HTTP server, identity provider, writer, grant or execution interface.
"""
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import hmac
from html import escape
import json
import re
from urllib.parse import unquote_to_bytes

from ash import g3_delegated_record_codec as records
from ash import g3_delegated_control_codec as control
from ash.g3_control_semantics import require


STYLE='body{max-width:72rem;margin:2rem auto;padding:1rem;font:16px system-ui;line-height:1.5}pre{white-space:pre-wrap;overflow-wrap:anywhere;padding:1rem;border:1px solid #777}button{font:inherit;padding:.8rem 1.4rem;margin:.5rem}h2{margin-top:2rem}'
LABELS=('Authority instance and incarnation','Workspace and project','Verified Owner principal',
    'Canonical Subject and Subject identity','Requested action','Exact scope','Operations',
    'Complete target material','Effect summary and explanation','Frozen dispatch material',
    'Challenge nonce','Challenge expiry and server time','Current binding generation',
    'Proposal and presentation identities','Source evidence references')
TEMPLATE_REVISION=hashlib.sha256(control.canonical({'template':'nexus.g3.n02.fixed-page.v1',
    'style':STYLE,'labels':list(LABELS),'decisions':['CONFIRM','DENY']})).hexdigest()
DECISION_PATH='/api/n01/decision'
FORM_FIELDS=frozenset(('csrf','choice','challenge_id','view_id','proposal_id','nonce','presentation_sha256'))
MAX_HTML_BYTES=524288
MAX_POST_BYTES=4096


@dataclass(frozen=True)
class RenderedPresentation:
    html: bytes
    challenge_id: str
    view_id: str
    proposal_id: str
    nonce: str
    presentation_sha256: str
    render_sha256: str
    expires_at_ms: int
    @property
    def authority(self):return 'NONE'


@dataclass(frozen=True)
class UntrustedDecision:
    choice: str
    challenge_id: str
    view_id: str
    proposal_id: str
    nonce: str
    presentation_sha256: str
    @property
    def authority(self):return 'NONE'


def _csrf(value):
    require(type(value) is str and re.fullmatch('[0-9a-f]{64}',value) is not None)
    return value


def _data(value):
    # ASCII JSON visibly escapes directional/control characters. No raw HTML,
    # target navigation, hidden material, fetch, truncation or script evaluation.
    return escape(json.dumps(value,ensure_ascii=True,sort_keys=True,indent=2),quote=True)


def render(challenge_raw,view_raw,*,csrf,now_ms):
    """Exact deterministic full display. Structural bytes remain NONE."""
    try:
        csrf=_csrf(csrf)
        require(type(now_ms) is int and now_ms>=0)
        challenge=records.parse_metadata(challenge_raw)
        view=records.parse_metadata(view_raw)
        body=challenge.to_dict();shown=view.to_dict()
        require(type(challenge_raw) is bytes and challenge_raw==records.canonical_bytes(body))
        require(type(view_raw) is bytes and view_raw==records.canonical_bytes(shown))
        require(body['schema_version']==records.PREFIX+'authority-challenge.v2')
        require(shown['schema_version']==records.PREFIX+'presentation-view.v2')
        require(shown['challenge']==dict(id=challenge.record_id,body_sha256=challenge.body_sha256))
        require(shown['stamp']==body['stamp'] and shown['authority_config_sha256']==body['authority_config_sha256'])
        require(shown['template_revision']==TEMPLATE_REVISION)
        require(max(body['issued_at_ms'],shown['issued_at_ms'])<=now_ms<shown['expires_at_ms']<=body['expires_at_ms'])
        projection=dict(challenge_body=body,owner_context=shown['owner_context'],
            template_revision=shown['template_revision'],expires_at_ms=shown['expires_at_ms'])
        require(records.domain_digest(records.PREFIX+'presentation-material.v1',projection)==shown['presentation_sha256'])
        material=body['material'];binding=body['binding'];context=shown['owner_context']
        require((binding['workspace_id'],binding['project_id'])==
                (material['scope']['workspace_id'],material['scope']['project_id']))
        expiry=datetime.fromtimestamp(shown['expires_at_ms']/1000,timezone.utc).isoformat(timespec='milliseconds')
        values=(dict(stamp=body['stamp'],authority_mode=body['authority_mode'],authority_config_sha256=body['authority_config_sha256']),
            dict(workspace_id=binding['workspace_id'],project_id=binding['project_id']),binding['owner'],
            dict(subject=material['subject'],subject_id=material['subject_id']),material['requested_action'],
            dict(scope=material['scope'],scope_sha256=material['scope_sha256']),material['operations'],
            material['targets'],dict(summary=material['effect_summary'],explanation=material['effect_explanation']),
            dict(payload=material['dispatch_payload'],dispatch_material_sha256=material['dispatch_material_sha256']),
            body['nonce'],dict(expires_at_ms=shown['expires_at_ms'],expires_at_utc=expiry,server_time_ms=now_ms,
                maximum_remaining_ms=shown['expires_at_ms']-now_ms),
            dict(binding_id=binding['binding_id'],owner_generation=binding['owner_generation'],
                binding_generation=binding['binding_generation'],context=context),
            dict(proposal_id=body['proposal_id'],presentation_sha256=shown['presentation_sha256'],
                challenge_id=challenge.record_id,view_id=shown['view_key'],template_revision=TEMPLATE_REVISION),
            material['source_evidence'])
        sections=''.join('<section><h2>'+escape(label)+'</h2><pre>'+_data(value)+'</pre></section>'
                         for label,value in zip(LABELS,values))
        fields=dict(csrf=csrf,challenge_id=challenge.record_id,view_id=shown['view_key'],
            proposal_id=body['proposal_id'],nonce=body['nonce'],presentation_sha256=shown['presentation_sha256'])
        hidden=''.join('<input type="hidden" name="'+key+'" value="'+escape(value,quote=True)+'">'
                       for key,value in sorted(fields.items()))
        page=('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            '<title>Exact Owner confirmation</title><style>'+STYLE+'</style></head><body>'
            '<h1>Review one exact proposal</h1><p>CONFIRM records a bounded decision only. '
            'It does not execute this proposal or enable real admission. No option is preselected.</p>'
            +sections+'<form method="post" action="'+DECISION_PATH+'">'+hidden+
            '<button type="submit" name="choice" value="CONFIRM">CONFIRM</button>'
            '<button type="submit" name="choice" value="DENY">DENY</button></form></body></html>').encode('utf-8')
        require(len(page)<=MAX_HTML_BYTES)
        return RenderedPresentation(page,challenge.record_id,shown['view_key'],body['proposal_id'],body['nonce'],
            shown['presentation_sha256'],hashlib.sha256(page).hexdigest(),shown['expires_at_ms'])
    except Exception:
        raise ValueError('N02_PRESENTATION_DENIED') from None


def response_headers():
    """Fixed response policy, no cookie issuance or authentication claim."""
    style_hash=hashlib.sha256(STYLE.encode()).digest()
    import base64
    csp="default-src 'none'; script-src 'none'; style-src 'sha256-"+base64.b64encode(style_hash).decode()+"'; form-action 'self'; frame-ancestors 'none'; base-uri 'none'; object-src 'none'"
    return {'Content-Type':'text/html; charset=utf-8','Cache-Control':'no-store','Referrer-Policy':'no-referrer',
        'X-Content-Type-Options':'nosniff','Content-Security-Policy':csp,'X-Frame-Options':'DENY',
        'Permissions-Policy':'camera=(), microphone=(), geolocation=()'}


def compare_post(raw,shown,*,csrf,origin,host,expected_host,method,content_type,now_ms):
    """Compare untrusted fields only; Owner/session/current membership still required."""
    try:
        require(type(shown) is RenderedPresentation)
        require(type(expected_host) is str and re.fullmatch('[a-z0-9][a-z0-9-]{0,120}\\.vercel\\.app',expected_host))
        require(method=='POST' and host==expected_host and origin=='https://'+expected_host)
        require(content_type=='application/x-www-form-urlencoded')
        require(type(now_ms) is int and 0<=now_ms<shown.expires_at_ms)
        require(type(raw) is bytes and 0<len(raw)<=MAX_POST_BYTES)
        text=raw.decode('ascii');fields={}
        for part in text.split('&'):
            require(part.count('=')==1)
            name,value=part.split('=')
            require(re.search(r'%(?![0-9A-Fa-f]{2})',name+value) is None)
            name=unquote_to_bytes(name.replace('+',' ')).decode('utf-8','strict')
            value=unquote_to_bytes(value.replace('+',' ')).decode('utf-8','strict')
            require(name in FORM_FIELDS and name not in fields)
            fields[name]=value
        require(set(fields)==FORM_FIELDS and fields['choice'] in ('CONFIRM','DENY'))
        require(hmac.compare_digest(_csrf(fields['csrf']),_csrf(csrf)))
        for name in ('challenge_id','view_id','proposal_id','nonce','presentation_sha256'):
            require(fields[name]==getattr(shown,name))
        return UntrustedDecision(fields['choice'],shown.challenge_id,shown.view_id,shown.proposal_id,
                                 shown.nonce,shown.presentation_sha256)
    except Exception:
        raise ValueError('N02_DECISION_INPUT_DENIED') from None

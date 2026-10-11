"""Additive delegated v2 record shapes. All results remain UNTRUSTED/NONE.

The v1 eight-gate contracts are unchanged. This codec cannot authenticate mode,
configuration, a writer, Owner confirmation, custody, grants or live permission.
"""
from __future__ import annotations
import hashlib
from ash import g3_record_codec as v1

MODE = 'DELEGATED_EXECUTOR'
D04_STATUS = 'UNQUALIFIED_NOT_A_RELEASE_GATE'
DOMAINS = frozenset(v1.PREFIX + kind + '.v2' for kind in v1.KINDS)
GATE_KINDS = tuple(kind for kind in v1.GATE_KINDS if kind != 'D04_EXECUTOR_EXCLUSION')
CONFIG_FIELDS = 'authority_mode authority_config_sha256 d04_historical_status'


def _shape_projection(value):
    """Throwaway v1 shape lens only; never a record, gate result or evidence.

    Preserve reference hashes and all material/Principal bytes. Actual v2 IDs
    and retained bytes are validated separately by the future semantic reader.
    Positive intent/claim shapes never use the v1 all-eight-PASS predicate.
    """
    if type(value) is dict:
        if set(value) == {'id', 'body_sha256'}:
            ident = value['id']
            v1._require(type(ident) is str)
            if ident.startswith(v1.PREFIX):
                domain, sep, digest = ident.rpartition(':')
                v1._require(sep == ':' and domain in DOMAINS)
                v1._sha(digest)
                v1._sha(value['body_sha256'])
                return {'id': domain[:-1] + '1:' + digest, 'body_sha256': value['body_sha256']}
            return dict(value)
        return {key: _shape_projection(child) for key, child in value.items()}
    if type(value) is list:
        return [_shape_projection(child) for child in value]
    return value


def _facts(value, all_pass):
    v1._require(type(value) is list and len(value) == 7)
    for kind, fact in zip(GATE_KINDS, value):
        v1._closed(fact, 'kind verdict observed_at_ms valid_until_ms source_evidence')
        v1._require(fact['kind'] == kind and fact['verdict'] in ('PASS', 'FAIL', 'UNKNOWN'))
        v1._require(not all_pass or fact['verdict'] == 'PASS')
        v1._integer(fact['observed_at_ms'])
        v1._integer(fact['valid_until_ms'])
        v1._require(fact['observed_at_ms'] < fact['valid_until_ms'])
        v1._evidence(fact['source_evidence'])


def _positive_common(body):
    for key, value in body.items():
        if key.endswith('_ms'):
            v1._integer(value)
        elif key.endswith('_sha256'):
            v1._sha(value)
    v1._stamp(body['stamp'])
    for key, kind in (('challenge', 'authority-challenge'), ('receipt', 'trusted-decision-receipt'),
                      ('intent', 'admission-intent')):
        if key in body:
            v1._ref(body[key], kind)
    if 'binding' in body:
        v1._binding(body['binding'])
        v1._context(body['owner_context'])
        v1._typed(body['proposal_id'], 'proposal-material')
        v1._typed(body['subject_id'], 'subject', old=True)
    for key in ('intent_key', 'attempt_key', 'executor_environment'):
        if key in body:
            v1._token(body[key])


def _envelope(body):
    v1._require(type(body) is dict and type(body.get('schema_version')) is str)
    v1._require(body['schema_version'] in DOMAINS)
    kind = body['schema_version'][len(v1.PREFIX):-3]
    fields = v1._FIELDS[kind] + ' ' + CONFIG_FIELDS
    if kind == 'dispatch-attempt':
        v1._require(body.get('phase') in ('CLAIM', 'RESULT'))
        fields += (' claimed_at_ms handoff_until_ms gate_facts revocation_read executor_environment'
                   if body['phase'] == 'CLAIM' else ' claim observed_at_ms outcome outcome_evidence')
    v1._closed(body, fields, 'host_proposal' if kind == 'authority-challenge' else '')
    v1._require(body['authority_mode'] == MODE and body['d04_historical_status'] == D04_STATUS)
    v1._sha(body['authority_config_sha256'])
    base = {key: value for key, value in body.items() if key not in CONFIG_FIELDS.split()}
    projected = _shape_projection(base)
    projected['schema_version'] = projected['schema_version'][:-1] + '1'
    if kind == 'admission-intent':
        _positive_common(projected)
        positive = body['disposition'] == 'ADMIT_PENDING'
        v1._require(body['disposition'] in ('DENIED', 'ADMIT_PENDING'))
        _facts(body['gate_facts'], positive)
        v1._require((body['grant'] is None) == (body['revocation_read'] is None))
        if body['grant'] is not None:
            v1._ref(body['grant'], 'grant', old=True)
            v1._revocation_read(body['revocation_read'])
            v1._require(body['grant'] == body['revocation_read']['grant'])
        reasons = body['reason_codes']
        v1._require(type(reasons) is list and 1 <= len(reasons) <= 8)
        v1._require(all(type(code) is str for code in reasons) and reasons == sorted(set(reasons)))
        if positive:
            v1._require(body['grant'] is not None and reasons == ['INTENT_PENDING'])
            v1._require(body['owner_context']['authenticated_at_ms'] <= body['evaluated_at_ms'])
            v1._require(all(f['observed_at_ms'] <= body['evaluated_at_ms'] for f in body['gate_facts']))
            v1._require(body['evaluated_at_ms'] < body['use_until_ms'] <= min(
                body['evaluated_at_ms'] + 60000, body['owner_context']['context_expires_at_ms'],
                *(f['valid_until_ms'] for f in body['gate_facts'])))
        else:
            v1._require(set(reasons) <= v1.FAILURE_CODES and body['use_until_ms'] == body['evaluated_at_ms'])
    elif kind == 'dispatch-attempt' and body['phase'] == 'CLAIM':
        _positive_common(projected)
        v1._ref(body['grant'], 'grant', old=True)
        _facts(body['gate_facts'], True)
        v1._revocation_read(body['revocation_read'])
        v1._require(body['grant'] == body['revocation_read']['grant'])
        v1._require(all(f['observed_at_ms'] <= body['claimed_at_ms'] for f in body['gate_facts']))
        v1._require(body['claimed_at_ms'] < body['handoff_until_ms'] <= min(
            f['valid_until_ms'] for f in body['gate_facts']))
    else:
        v1._envelope(projected)


def parse_metadata(raw):
    """Versioned shape/identity only. Runtime source qualification stays absent."""
    try:
        body = v1.parse_json(raw)
        _envelope(body)
        canonical = v1.canonical_bytes(body)
        domain = body['schema_version']
        digest = hashlib.sha256(domain.encode('utf-8') + b'\0' + canonical).hexdigest()
        return v1.UntrustedMetadata(canonical, domain + ':' + digest,
                                    hashlib.sha256(canonical).hexdigest())
    except (ValueError, TypeError, KeyError, AttributeError, RecursionError, OverflowError, UnicodeError):
        raise v1.MetadataError('G3_PRODUCTION_METADATA_INVALID') from None

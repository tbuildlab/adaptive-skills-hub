"""Complete retained v2 control resolution over bounded independent S3 bytes.

All results are NONE. This reader does not qualify a writer, install a registration
or promote the earlier TEST_ONLY lineage. Authentic deployment/source membership
must be established separately before any production use.
"""
from dataclasses import dataclass

from ash import g3_delegated_control_codec as control
from ash import g3_delegated_record_codec as records
from ash import g3_grant_codec as grants
from ash.g3_control_semantics import check_delegated_control,require


@dataclass(frozen=True)
class RetainedState:
    checked: object
    bodies: tuple[tuple[str,bytes],...]
    evidence: tuple[tuple[str,bytes],...]
    assertions: tuple[tuple[str,bytes],...]

    @property
    def authority(self):return 'NONE'


def resolve_retained_state(snapshot,checkpoints,objects,*,profile,config_sha256):
    """Pure exact resolution. The concrete fence supplies independently read blobs.

    No URL, credential, writer choice, state restore, fallback or mutable cache.
    Unknown/unreferenced blobs never provide membership or authority.
    """
    try:
        require(type(checkpoints) is tuple and 1<=len(checkpoints)<=64)
        require(type(objects) is dict and len(objects)<=256)
        require(profile in ('TEST_ONLY','PRODUCTION'))
        control.old.check_type(config_sha256,'h')
        for digest,raw in objects.items():
            control.old.check_type(digest,'h')
            require(type(raw) is bytes and 0<len(raw)<=65536 and control.digest(raw)==digest)
            control.decode(raw)
        rows=control.verify_snapshot(snapshot)
        bodies={};evidence={};assertions={}

        def insert(mapping,ident,raw):
            require(ident not in mapping or mapping[ident]==raw)
            mapping[ident]=raw

        def body(ref):
            require(type(ref) is dict and set(ref)=={'id','body_sha256'})
            raw=objects.get(ref['body_sha256'])
            require(type(raw) is bytes)
            value=control.decode(raw)
            if value.get('schema_version')==grants.GRANT_SCHEMA:
                ident=grants.approval_grant(value).grant_id
            elif value.get('schema_version')==grants.REVOCATION_SCHEMA:
                ident=grants.revocation(value).revocation_id
            else:ident=records.parse_metadata(raw).record_id
            require(ident==ref['id']);insert(bodies,ident,raw)
            return value

        for raw in checkpoints:
            parsed=records.parse_metadata(raw)
            require(parsed.to_dict()['schema_version']==records.PREFIX+'recovery-checkpoint.v2')
            insert(bodies,parsed.record_id,raw)
        for row in rows:
            value=control.decode(row.value)
            if value['family']=='source':
                ref=value['evidence_ref'];raw=objects.get(ref['sha256'])
                require(type(raw) is bytes);insert(evidence,ref['ref'],raw)
                sha=value['assertion_sha256'];raw=objects.get(sha)
                require(type(raw) is bytes);insert(assertions,sha,raw)

        visited=set()
        def nested(value):
            if type(value) is dict:
                if set(value)=={'id','body_sha256'}:
                    if value['id'] not in visited:
                        visited.add(value['id']);nested(body(value))
                    else:body(value)
                elif set(value)=={'ref','sha256'}:
                    require(value['ref'] in evidence and control.digest(evidence[value['ref']])==value['sha256'])
                else:
                    for item in value.values():nested(item)
            elif type(value) is list:
                for item in value:nested(item)
        for row in rows:nested(control.decode(row.value))
        checked=check_delegated_control(snapshot,bodies,evidence,profile=profile,
            protected_config=config_sha256,assertions=assertions)
        return RetainedState(checked,tuple(sorted(bodies.items())),tuple(sorted(evidence.items())),
                             tuple(sorted(assertions.items())))
    except Exception:
        raise ValueError('N01_RETAINED_STATE_QUARANTINE') from None

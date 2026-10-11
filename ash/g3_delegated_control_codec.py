"""Delegated v2 control rows in unchanged v1 page/snapshot encoding. NONE.

Fixed version compatibility only; no writer authentication or authority ingress.
Historical v1 codec and row field sets remain unchanged.
"""
from dataclasses import dataclass
from ash import g3_control_codec as old
from ash import g3_delegated_record_codec as records
canonical=old.canonical
decode=old.decode
digest=old.digest
require=old.require
OfflineError=old.OfflineError
NAMESPACES=old.NAMESPACES
SPECS=old.SPECS
VERSION='nexus.g3.n01-control.v2'


def _lens(value):
    if type(value) is dict:
        if set(value)=={'id','body_sha256'}:
            return records._shape_projection(value)
        return {key:_lens(child) for key,child in value.items()}
    if type(value) is list:return [_lens(child) for child in value]
    return value


@dataclass(frozen=True)
class ControlRow:
    namespace: str
    key: str
    value: bytes

    def __post_init__(self):
        body=decode(self.value)
        require(type(body) is dict and body.get('schema_version')==VERSION)
        require(len(self.value)<=16384)
        if body.get('family')=='root':
            require(body.get('authority_mode')==records.MODE)
            require(body.get('d04_historical_status')==records.D04_STATUS)
            old.check_type(body.get('authority_config_sha256'),'h')
            base={key:value for key,value in body.items() if key not in records.CONFIG_FIELDS.split()}
        else:
            require(not set(records.CONFIG_FIELDS.split()) & set(body))
            base=body
        try:
            projected=_lens(base)
        except ValueError:
            raise OfflineError('G3_OFFLINE_REJECTED') from None
        projected['schema_version']=old.VERSION
        old.ControlRow(self.namespace,self.key,canonical(projected))

    @property
    def authority(self):return 'NONE'

    @classmethod
    def from_value(cls,body):
        require(type(body) is dict and body.get('family') in SPECS)
        family=body['family'];namespace,field,_=SPECS[family]
        require(field in body)
        part=str(body[field])
        if family=='recovery':old.check_type(body[field],'u');part=f"{body[field]:020d}"
        elif family=='retirement':part=body['entity_kind']+':'+part
        return cls(namespace,family+':'+part,canonical(body))


@dataclass(frozen=True)
class EncodedSnapshot:
    root: bytes
    pages: tuple[bytes, ...]

    @property
    def control_after_sha256(self):
        return digest(self.root)

    @property
    def authority(self):
        return "NONE"


def encode_snapshot(rows):
    """Closed rows + header agreement, not full production semantic qualification."""
    require(type(rows) is tuple and 1 <= len(rows) <= 4096)
    require(all(type(row) is ControlRow for row in rows))
    for row in rows:
        ControlRow(row.namespace,row.key,row.value)
    ordered = sorted(rows, key=lambda row: (row.namespace.encode(), row.key.encode()))
    require(len({(row.namespace, row.key) for row in ordered}) == len(ordered))
    roots = [decode(row.value) for row in ordered if decode(row.value)["family"] == "root"]
    require(len(roots) == 1)
    root = roots[0]
    for row in ordered:
        value = decode(row.value)
        if value["family"] == "recovery":
            require(value["sequence"] < root["recovery_sequence"])
    pages = []
    references = []
    for namespace in NAMESPACES:
        pending = []
        def page_bytes(items):
            return canonical({"codec_version": "nexus.g3.control-page.v1", "namespace": namespace, "rows": items})
        def flush():
            if pending:
                raw = page_bytes(pending)
                pages.append(raw)
                references.append(dict(namespace=namespace,first_key=pending[0]["key"],
                    last_key=pending[-1]["key"],row_count=len(pending),page_sha256=digest(raw)))
                pending.clear()
        for row in ordered:
            if row.namespace != namespace:
                continue
            item = dict(key=row.key,value_canonical_utf8=row.value.decode(),value_sha256=digest(row.value))
            if len(pending) == 64:
                flush()
            try:
                page_bytes(pending + [item])
            except OfflineError:
                require(len(pending) > 0); flush(); page_bytes([item])
            pending.append(item)
        flush()
    require(len(references) <= 64)
    header = {field: root[field] for field in ("authority_instance","authority_epoch","incarnation","recovery_sequence","time_high_water_ms")}
    header.update(codec_version="nexus.g3.control-snapshot.v1", inventory=list(NAMESPACES),pages=references)
    return EncodedSnapshot(canonical(header), tuple(pages))


def verify_snapshot(snapshot):
    """Verify exact closed encoding/readback; never authenticate its origin."""
    require(type(snapshot) is EncodedSnapshot and type(snapshot.pages) is tuple)
    header = decode(snapshot.root)
    require(type(header) is dict and set(header) == {"codec_version","authority_instance","authority_epoch",
        "incarnation","recovery_sequence","time_high_water_ms","inventory","pages"})
    require(header["codec_version"] == "nexus.g3.control-snapshot.v1")
    require(header["inventory"] == list(NAMESPACES))
    require(type(header["pages"]) is list and len(header["pages"]) == len(snapshot.pages) <= 64)
    rows=[]
    for raw,reference in zip(snapshot.pages,header["pages"]):
        require(type(reference) is dict and set(reference) == {"namespace","first_key","last_key","row_count","page_sha256"})
        require(digest(raw)==reference["page_sha256"])
        page=decode(raw)
        require(type(page) is dict and set(page)=={"codec_version","namespace","rows"})
        require(page["codec_version"]=="nexus.g3.control-page.v1" and page["namespace"]==reference["namespace"])
        require(type(page["rows"]) is list and 1<=len(page["rows"])<=64)
        require(type(reference["row_count"]) is int and reference["row_count"]==len(page["rows"]))
        keys=[]
        for item in page["rows"]:
            require(type(item) is dict and set(item)=={"key","value_canonical_utf8","value_sha256"})
            require(type(item["value_canonical_utf8"]) is str)
            value=item["value_canonical_utf8"].encode("utf-8")
            require(digest(value)==item["value_sha256"])
            rows.append(ControlRow(page["namespace"],item["key"],value));keys.append(item["key"])
        require(keys==sorted(set(keys),key=lambda key:key.encode()))
        require(keys[0]==reference["first_key"] and keys[-1]==reference["last_key"])
    # Re-encoding rejects omitted root, overlapping pages, header mismatch and
    # non-deterministic splitting. Complete semantic joins remain a future gate.
    require(encode_snapshot(tuple(rows))==snapshot)
    return tuple(rows)

"""Bounded D03 diagnostic S3 custody adapter. Never issues production authority.

Receives an already scoped SDK client; no credential discovery, retry, planner,
dispatch or production admission API. Structural codecs remain untrusted until
the independently registered origin, complete versions and retained bytes join.
This adapter qualifies the minimal D03 canary, not N01 ledger semantics.
"""
from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import re

from scripts.g3_production_metadata import (
    canonical_bytes, parse_json, parse_metadata, domain_digest, MetadataError,
)

SCHEMA = "nexus.g3.production.recovery-checkpoint.v1"
LEDGER = "nexus.g3.production.ledger-commit.v1"
_SHA = re.compile(r"[0-9a-f]{64}\Z")


class FenceError(ValueError):
    """Closed diagnostic; never includes backend errors or caller material."""


def require(condition):
    if not condition:
        raise FenceError("D03_QUARANTINE")


def sha(raw):
    require(type(raw) is bytes)
    return hashlib.sha256(raw).hexdigest()


def decoded(raw):
    try:
        value = parse_json(raw)
        require(canonical_bytes(value) == raw)
        return value
    except MetadataError:
        raise FenceError("D03_QUARANTINE") from None


def reference(raw):
    try:
        m = parse_metadata(raw)
        require(m.to_dict()["schema_version"] == SCHEMA)
        return {"id": m.record_id, "body_sha256": m.body_sha256}
    except MetadataError:
        raise FenceError("D03_QUARANTINE") from None


@dataclass(frozen=True)
class Registration:
    """Pinned by independent setup, never constructed from a recovery claimant."""
    bucket: str
    owner: str
    prefix: str
    authority_instance: str
    generation: int
    genesis_id: str
    genesis_sha256: str
    admin_checkpoint_ids: tuple[str, ...]
    purpose: str = "TEST_ONLY"

    def __post_init__(self):
        require(self.bucket == "nexus-d03-custody-862902859484-ap-southeast-1-v1")
        require(self.owner == "862902859484" and self.purpose == "TEST_ONLY")
        require(type(self.prefix) is str and self.prefix.endswith("/"))
        require(self.prefix.startswith(("qualification/v1/normal/", "qualification/v1/faults/")))
        require(not any(x in self.prefix for x in ("..", "//", "\\")))
        require(type(self.generation) is int and self.generation > 0)
        require(type(self.genesis_sha256) is str and _SHA.fullmatch(self.genesis_sha256))
        require(type(self.admin_checkpoint_ids) is tuple)
        require(self.genesis_id in self.admin_checkpoint_ids)


@dataclass(frozen=True)
class ProtectedHistory:
    """Custody/integrity observation only; does not authenticate grants or consent."""
    checkpoints: tuple[bytes, ...]
    versions: tuple[tuple[str, str], ...]
    descriptors: tuple[bytes, ...]
    controls: tuple[bytes, ...]
    pages: tuple[tuple[bytes, ...], ...]

    @property
    def head(self):
        return reference(self.checkpoints[-1])

    @property
    def authority(self):
        return "NONE"


class S3Fence:
    """No retries. Any unknown/partial history quarantines; no stale fallback."""
    registration_type = Registration
    ledger_domain = LEDGER
    record_parser = staticmethod(parse_metadata)
    reference = staticmethod(reference)
    decoded = staticmethod(decoded)
    domain_digest = staticmethod(domain_digest)

    def __init__(self, client, registration, *, max_attempts=1000):
        require(type(registration) is self.registration_type)
        require(type(max_attempts) is int and 1 <= max_attempts <= 1000)
        self.client, self.registration = client, registration
        self.attempts, self.max_attempts = 0, max_attempts
        self.pending = None
        self.quarantined = True

    def call(self, operation, **kwargs):
        require(self.attempts < self.max_attempts)
        self.attempts += 1
        try:
            result = getattr(self.client, operation)(
                Bucket=self.registration.bucket,
                ExpectedBucketOwner=self.registration.owner, **kwargs)
            require(type(result) is dict)
            require(result.get("ResponseMetadata", {}).get("HTTPStatusCode") in (200, 204))
            return result
        except Exception:
            self.quarantined = True
            raise FenceError("D03_QUARANTINE") from None

    def inventory(self, suffix):
        prefix = self.registration.prefix + suffix
        rows, seen, cursor = [], set(), {}
        for _ in range(8):
            result = self.call("list_object_versions", Prefix=prefix, MaxKeys=128, **cursor)
            require(type(result.get("IsTruncated")) is bool)
            require(not result.get("DeleteMarkers"))
            values = result.get("Versions", [])
            require(type(values) is list and len(values) <= 128)
            for row in values:
                require(type(row) is dict and type(row.get("Key")) is str)
                require(row["Key"].startswith(prefix) and row.get("IsLatest") is True)
                require(type(row.get("VersionId")) is str and row["VersionId"] not in ("", "null"))
                require(type(row.get("Size")) is int and 0 < row["Size"] <= 65536)
                require(row["Key"] not in seen)
                seen.add(row["Key"])
                rows.append((row["Key"], row["VersionId"]))
                require(len(rows) <= 256)
            if not result["IsTruncated"]:
                return tuple(sorted(rows))
            key, version = result.get("NextKeyMarker"), result.get("NextVersionIdMarker")
            require(type(key) is str and key.startswith(prefix) and type(version) is str)
            next_cursor = {"KeyMarker": key, "VersionIdMarker": version}
            require(next_cursor != cursor)
            cursor = next_cursor
        raise FenceError("D03_QUARANTINE")

    def retained(self, key, version, valid_until):
        result = self.call("get_object", Key=key, VersionId=version)
        require(result.get("VersionId") == version)
        require(type(result.get("ContentLength")) is int and 0 < result["ContentLength"] <= 65536)
        body = result.get("Body")
        require(hasattr(body, "read") and hasattr(body, "close"))
        try:
            raw = body.read(65537)
        finally:
            body.close()
        require(type(raw) is bytes and len(raw) == result["ContentLength"] <= 65536)
        retention = self.call("get_object_retention", Key=key, VersionId=version).get("Retention")
        require(type(retention) is dict and retention.get("Mode") == "COMPLIANCE")
        until = retention.get("RetainUntilDate")
        require(type(until) is datetime and until.tzinfo is not None and until >= valid_until)
        return raw

    def independent_recovery_authorization(self, body, ref, valid_until):
        """A registered candidate hash is not an independently observed approval.

        This separate fault-side custody namespace is writable only from protected
        R administration. The normal append role has version/retention reads only.
        Missing/duplicate/expired authorization quarantines even a known RECOVER.
        """
        prefix = "qualification/v1/faults/admin-authorizations-v1/" + f"{body['recovery_sequence']:020d}/"
        remaining = self.max_attempts-self.attempts
        require(remaining > 0)
        protected = S3Fence(self.client, replace(self.registration, prefix=prefix), max_attempts=remaining)
        try:
            before = protected.inventory("")
            require(len(before) == 1 and before[0][0] == prefix + "authorization.json")
            authorization = self.decoded(protected.retained(*before[0], valid_until))
            require(authorization == dict(schema_version="nexus.g3.d03.diagnostic-admin-authorization.v1",
                purpose="TEST_ONLY", generation=self.registration.generation, checkpoint=ref,
                previous_checkpoint=body["previous_checkpoint"]))
            require(protected.inventory("") == before)
        finally:
            self.attempts += protected.attempts

    def read(self, *, valid_until):
        self.quarantined = True
        require(type(valid_until) is datetime and valid_until.tzinfo is not None)
        require(valid_until > datetime.now(timezone.utc))
        try:
            journal = self.inventory("journal/")
            objects = self.inventory("objects/")
            require(0 < len(journal) <= 64)
            blobs, cache = dict(objects), {}

            def blob(digest, domain=None):
                require(type(digest) is str and _SHA.fullmatch(digest))
                key = self.registration.prefix + "objects/" + digest
                require(key in blobs)
                if key not in cache:
                    cache[key] = self.retained(key, blobs[key], valid_until)
                actual = self.domain_digest(domain, self.decoded(cache[key])) if domain else sha(cache[key])
                require(actual == digest)
                return cache[key]

            bodies, descriptors, controls, pages = [], [], [], []
            prior = None
            for seq, (key, version) in enumerate(journal):
                require(key == self.registration.prefix + f"journal/{seq:020d}")
                raw = self.retained(key, version, valid_until)
                ref, body = self.reference(raw), self.decoded(raw)
                require(body["authority_instance"] == self.registration.authority_instance)
                require(body["recovery_sequence"] == seq and body["previous_checkpoint"] == prior)
                if seq == 0:
                    require(ref == {"id": self.registration.genesis_id,
                                    "body_sha256": self.registration.genesis_sha256})
                previous = self.decoded(bodies[-1]) if bodies else None
                admin = body["transition_kind"] in ("GENESIS", "RECOVER")
                require(not admin or ref["id"] in self.registration.admin_checkpoint_ids)
                if previous:
                    require(body["time_high_water_ms"] >= previous["time_high_water_ms"])
                    if body["transition_kind"] == "RECOVER":
                        require(body["authority_epoch"] > previous["authority_epoch"])
                        require(body["incarnation"] != previous["incarnation"])
                        self.independent_recovery_authorization(body, ref, valid_until)
                    else:
                        require(body["authority_epoch"] == previous["authority_epoch"])
                        require(body["incarnation"] == previous["incarnation"])
                descriptor_raw = blob(body["ledger_commit_sha256"], self.ledger_domain)
                descriptor = self.decoded(descriptor_raw)
                fields = set(body) - {"schema_version", "ledger_commit_sha256"}
                require(set(descriptor) == fields | {"control_after_sha256"})
                require(all(descriptor[x] == body[x] for x in fields))
                # Descriptor objects are addressed by their domain-separated hash.
                require(self.domain_digest(self.ledger_domain, descriptor) == body["ledger_commit_sha256"])
                control = blob(descriptor["control_after_sha256"])
                header = self.decoded(control)
                require(set(header) == {"codec_version", "authority_instance", "authority_epoch",
                    "incarnation", "recovery_sequence", "time_high_water_ms", "inventory", "pages"})
                require(header["codec_version"] == "nexus.g3.control-snapshot.v1")
                require(all(header[x] == body[x] for x in ("authority_instance", "authority_epoch",
                    "incarnation", "recovery_sequence", "time_high_water_ms")))
                require(type(header["pages"]) is list and len(header["pages"]) <= 64)
                page_bodies = tuple(blob(x["page_sha256"]) for x in header["pages"])
                for item in body["record_refs"]:
                    retained = blob(item["body_sha256"])
                    # Records remain untrusted structural metadata, never authority.
                    require(self.record_parser(retained).record_id == item["id"])
                bodies.append(raw); descriptors.append(descriptor_raw)
                controls.append(control); pages.append(page_bodies); prior = ref
            require(self.inventory("journal/") == journal)
            require(self.inventory("objects/") == objects)
            return ProtectedHistory(tuple(bodies), journal, tuple(descriptors), tuple(controls), tuple(pages))
        except Exception:
            raise FenceError("D03_QUARANTINE") from None

    def append(self, raw, expected_head, *, valid_until):
        """One conditional attempt only; uncertainty pins candidate, never retries."""
        require(self.pending is None)
        self.reference(raw)
        body = self.decoded(raw)
        require(body["transition_kind"] not in ("GENESIS", "RECOVER"))
        history = self.read(valid_until=valid_until)
        require(history.head == expected_head and body["previous_checkpoint"] == expected_head)
        previous = self.decoded(history.checkpoints[-1])
        require(body["recovery_sequence"] == previous["recovery_sequence"] + 1)
        require(all(body[x] == previous[x] for x in ("authority_instance", "authority_epoch", "incarnation")))
        require(body["time_high_water_ms"] >= previous["time_high_water_ms"])
        # Caller has independently retained descriptor/snapshot before journal append.
        objects = dict(self.inventory("objects/"))
        def candidate_blob(digest, domain=None):
            require(type(digest) is str and _SHA.fullmatch(digest))
            key = self.registration.prefix + "objects/" + digest
            require(key in objects)
            data = self.retained(key, objects[key], valid_until)
            require((self.domain_digest(domain, self.decoded(data)) if domain else sha(data)) == digest)
            return data
        descriptor = self.decoded(candidate_blob(body["ledger_commit_sha256"], self.ledger_domain))
        fields = set(body) - {"schema_version", "ledger_commit_sha256"}
        require(set(descriptor) == fields | {"control_after_sha256"})
        require(all(descriptor[x] == body[x] for x in fields))
        control = self.decoded(candidate_blob(descriptor["control_after_sha256"]))
        require(control.get("codec_version") == "nexus.g3.control-snapshot.v1")
        require(all(control.get(x) == body[x] for x in ("authority_instance", "authority_epoch",
            "incarnation", "recovery_sequence", "time_high_water_ms")))
        require(type(control.get("pages")) is list and len(control["pages"]) <= 64)
        for page in control["pages"]:
            candidate_blob(page["page_sha256"])
        for item in body["record_refs"]:
            require(self.record_parser(candidate_blob(item["body_sha256"])).record_id == item["id"])
        require(self.inventory("objects/") == tuple(sorted(objects.items())))
        self.pending = raw
        self.call("put_object", Key=self.registration.prefix + f"journal/{body['recovery_sequence']:020d}",
                  Body=raw, IfNoneMatch="*", ContentType="application/json", ChecksumAlgorithm="SHA256")
        return self.reconcile(valid_until=valid_until)

    def reconcile(self, *, valid_until):
        require(self.pending is not None)
        history = self.read(valid_until=valid_until)
        require(history.checkpoints[-1] == self.pending)
        self.pending = None
        # Recovery eligibility still belongs to the independently qualified consumer.
        return history

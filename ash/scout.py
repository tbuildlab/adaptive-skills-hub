"""Bounded, read-only discovery and admission for untrusted Skill/MCP candidates.

The Scout is intentionally outside the trusted capability selector.  It may
read reviewed research evidence or bounded public metadata, but it cannot
install, enable, load, connect to, execute, or promote any discovered item.
External text is always data: only closed fields produced by this module can
cross the receipt boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import ipaddress
import json
from pathlib import Path
import re
import socket
from typing import Any, Callable, Iterable, Mapping, Sequence
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, unquote, urlencode, urljoin, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from uuid import UUID, uuid4

from .runtime_decision import (
    RUNTIME_SELECTOR_VERSION,
    RuntimeCapabilityAdapter,
    RuntimeDecisionError,
    RuntimeRequirements,
)


SCOUT_REQUEST_SCHEMA_VERSION = "nexus.candidate-scout-request.v1"
SCOUT_RECEIPT_SCHEMA_VERSION = "nexus.candidate-scout-receipt.v1"
SCOUT_VERSION = "nexus.read-only-skill-mcp-scout.v1"
ADMISSION_VERSION = "nexus.provenance-aware-admission.v1"
SOURCE_CONFIG_SCHEMA_VERSION = "nexus.scout-sources.v1"
AGENT_SKILLS_DISCOVERY_SCHEMA = (
    "https://schemas.agentskills.io/discovery/0.2.0/schema.json"
)

MAX_SOURCE_IDS = 3
MAX_SEARCH_QUERIES = 3
MAX_CANDIDATES_PER_SOURCE = 8
MAX_TOTAL_CANDIDATES = 16
MAX_REDIRECTS = 2
MAX_RESPONSE_BYTES = 512 * 1024
MAX_METADATA_BYTES = 4 * 1024
MAX_SKILL_ARTIFACT_BYTES = 128 * 1024
MAX_SKILL_ARTIFACT_FETCHES = 4
MAX_HTTP_REQUESTS = 8
HTTP_TIMEOUT_SECONDS = 5.0
HTTP_RETRIES = 0
EVIDENCE_TTL_DAYS = 30
MAX_RECEIPT_BYTES = 24 * 1024

SOURCE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
TOKEN_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,63}$")
REPOSITORY_RE = re.compile(
    r"^(?P<owner>[A-Za-z0-9](?:[A-Za-z0-9-]{0,38}[A-Za-z0-9])?)/"
    r"(?P<repo>[A-Za-z0-9._-]{1,100})$"
)
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
SKILL_NAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$")
SAFE_PROVIDER_RE = re.compile(r"^[a-z0-9][a-z0-9._/-]{0,127}$")
SAFE_TAG_RE = re.compile(r"^[a-z0-9][a-z0-9._:-]{0,63}$")
MCP_SERVER_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,255}$")
VERSION_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.+_-]{0,127}$")

ADMISSION_DISPOSITIONS = frozenset(
    {
        "ADMITTED_FOR_REVIEW",
        "REFERENCE_ONLY",
        "QUARANTINED",
        "REJECTED",
        "INSUFFICIENT_EVIDENCE",
    }
)
LICENSE_STATES = frozenset(
    {
        "VERIFIED_COMPATIBLE",
        "VERIFIED_RESTRICTED",
        "AMBIGUOUS",
        "MISSING",
        "INCOMPATIBLE",
    }
)
CANDIDATE_TYPES = frozenset(
    {"agent_skill", "mcp_server", "agent_skill_source", "mcp_registry_source"}
)
CANDIDATE_LIFECYCLES = frozenset({"discovered", "classified", "quarantined", "rejected"})
DECLARED_EXECUTION_MECHANISMS = frozenset(
    {"skill_md", "skill_archive", "mcp_stdio", "mcp_sse", "mcp_streamable_http", "reference_source"}
)
AUTHENTICATION_STATES = frozenset({"declared", "not_declared", "unknown", "not_applicable"})
SUPPORTED_SOURCE_KINDS = frozenset(
    {"research_snapshot", "mcp_registry", "agent_skills_well_known"}
)
SUPPORTED_MCP_TRANSPORTS = frozenset({"stdio", "sse", "streamable-http"})
_PERMISSIVE_LICENSES = frozenset(
    {"mit", "apache-2.0", "bsd-2-clause", "bsd-3-clause", "isc", "mpl-2.0"}
)
_RESTRICTED_LICENSE_MARKERS = ("gpl", "agpl", "lgpl", "source available")
_PROMPT_INJECTION_MARKERS = (
    "ignore previous",
    "ignore all previous",
    "system prompt",
    "developer message",
    "override policy",
    "bypass security",
    "exfiltrate",
    "read credentials",
    "steal secret",
    "run shell",
    "execute command",
    "install this",
    "modify nexus",
    "grant execution",
)
_PROTECTED_REPOSITORY_OWNERS = {
    "registry": "modelcontextprotocol",
    "agentskills": "agentskills",
    "agent-skills-discovery-rfc": "cloudflare",
}
_FORBIDDEN_RECEIPT_KEYS = frozenset(
    {
        "description",
        "readme",
        "skill_md",
        "skill_instructions",
        "raw_metadata",
        "prompt",
        "project_context",
        "workspace_path",
        "path",
        "credentials",
        "secrets",
        "host_mapping",
        "mapping_id",
        "tool_arguments",
        "install_command",
        "executed_capability_ids",
    }
)
_PUBLIC_QUERY_TERMS = frozenset(
    {
        "accessibility", "agent", "architecture", "artifact", "automation",
        "backend", "code", "database", "debugging", "document", "evaluation",
        "filesystem", "frontend", "memory", "mcp", "pdf", "presentation",
        "provenance", "registry", "research", "security", "skill", "spreadsheet",
        "testing", "validation", "workflow",
    }
)
_PUBLIC_QUERY_ALIASES = {
    "agent-skill": "skill",
    "agent-skills": "skill",
    "skill-standard": "skill",
    "candidate-recommendation": "skill",
    "provenance-review": "provenance",
    "mcp-server": "mcp",
    "mcp-registry": "mcp",
}


class ScoutError(ValueError):
    """Fail-closed Scout error with a safe machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.safe_message = message


@dataclass(frozen=True)
class ScoutRequest:
    runtime_requirements: RuntimeRequirements
    source_ids: tuple[str, ...]


@dataclass(frozen=True)
class FetchResult:
    final_url: str
    content_type: str
    body: bytes
    redirects: int


class _BoundedRedirectHandler(HTTPRedirectHandler):
    def __init__(self, allowed_hosts: frozenset[str]) -> None:
        super().__init__()
        self.allowed_hosts = allowed_hosts
        self.redirects = 0

    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> Any:
        self.redirects += 1
        if self.redirects > MAX_REDIRECTS:
            raise ScoutError("REDIRECT_OVERFLOW", "Scout redirect budget exceeded")
        checked_url = _validated_https_url(
            newurl,
            allowed_hosts=self.allowed_hosts,
            allow_query=True,
        )
        _validate_public_resolution((urlsplit(checked_url).hostname or "").casefold())
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class PublicMetadataFetcher:
    """HTTPS-only fetcher for manifest-approved public origins.

    It never accepts credentials, cookies, arbitrary headers, POST bodies, or
    caller-provided hosts.  The caller supplies only hosts already verified in
    the integrity-protected Scout source configuration.
    """

    def __init__(self) -> None:
        self.requests = 0

    def fetch(
        self,
        url: str,
        *,
        allowed_hosts: Iterable[str],
        max_bytes: int = MAX_RESPONSE_BYTES,
    ) -> FetchResult:
        if self.requests >= MAX_HTTP_REQUESTS:
            raise ScoutError("REQUEST_OVERFLOW", "Scout HTTP request budget exceeded")
        hosts = frozenset(item.casefold() for item in allowed_hosts)
        checked_url = _validated_https_url(url, allowed_hosts=hosts, allow_query=True)
        _validate_public_resolution((urlsplit(checked_url).hostname or "").casefold())
        self.requests += 1
        redirects = _BoundedRedirectHandler(hosts)
        opener = build_opener(redirects)
        request = Request(
            url,
            method="GET",
            headers={
                "Accept": "application/json, text/markdown;q=0.8, text/plain;q=0.7",
                "User-Agent": "Nexus-Read-Only-Scout/1",
            },
        )
        try:
            with opener.open(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
                final_url = response.geturl()
                _validated_https_url(final_url, allowed_hosts=hosts, allow_query=True)
                body = response.read(max_bytes + 1)
                if len(body) > max_bytes:
                    raise ScoutError("RESPONSE_SIZE_OVERFLOW", "Scout response exceeded its byte budget")
                content_type = str(response.headers.get_content_type()).casefold()
        except ScoutError:
            raise
        except (HTTPError, URLError, OSError, TimeoutError, socket.timeout) as exc:
            raise ScoutError("SOURCE_UNAVAILABLE", "Scout public metadata source is unavailable") from exc
        return FetchResult(final_url, content_type, body, redirects.redirects)


def _validated_https_url(
    value: Any,
    *,
    allowed_hosts: frozenset[str] | None = None,
    allow_query: bool = False,
) -> str:
    if not isinstance(value, str) or not value or len(value) > 2048:
        raise ScoutError("URL_INVALID", "candidate URL is invalid")
    parsed = urlsplit(value)
    host = (parsed.hostname or "").casefold()
    if (
        parsed.scheme != "https"
        or not host
        or parsed.username is not None
        or parsed.password is not None
        or parsed.fragment
        or (parsed.query and not allow_query)
        or parsed.port not in (None, 443)
        or host in {"localhost", "localhost.localdomain"}
        or host.endswith(".local")
        or "." not in host
    ):
        raise ScoutError("URL_INVALID", "candidate URL is not an approved public HTTPS URL")
    decoded_path = unquote(parsed.path)
    decoded_query = unquote(parsed.query)
    if (
        "\\" in decoded_path
        or ".." in decoded_path.split("/")
        or any(ord(ch) < 32 for ch in decoded_path + decoded_query)
    ):
        raise ScoutError("URL_INVALID", "candidate URL path is unsafe")
    try:
        if ipaddress.ip_address(host).is_private or ipaddress.ip_address(host).is_loopback:
            raise ScoutError("URL_INVALID", "candidate URL may not target a private address")
    except ValueError:
        pass
    if allowed_hosts is not None and host not in allowed_hosts:
        raise ScoutError("REDIRECT_ORIGIN_REJECTED", "candidate URL origin is not approved")
    return urlunsplit(("https", parsed.netloc.casefold(), parsed.path or "/", parsed.query, ""))


def _validate_public_resolution(host: str) -> None:
    """Reject an allowlisted public name if it currently resolves privately.

    The source host is already fixed by the manifest-protected allowlist. This
    additional check narrows accidental/private resolution; it is not treated
    as publisher identity or transport integrity evidence.
    """
    try:
        addresses = {
            ipaddress.ip_address(sockaddr[0])
            for _family, _socktype, _proto, _canonname, sockaddr
            in socket.getaddrinfo(host, 443, type=socket.SOCK_STREAM)
        }
    except (OSError, ValueError) as exc:
        raise ScoutError("SOURCE_UNAVAILABLE", "Scout public source name could not be resolved safely") from exc
    if not addresses or any(not address.is_global for address in addresses):
        raise ScoutError("SOURCE_RESOLUTION_REJECTED", "Scout public source resolved outside the public network")


def _canonical_github_repository(value: Any) -> tuple[str, str]:
    if not isinstance(value, str):
        raise ScoutError("IDENTITY_INVALID", "candidate repository identity is invalid")
    match = REPOSITORY_RE.fullmatch(value)
    if not match or value.endswith(".git"):
        raise ScoutError("IDENTITY_INVALID", "candidate repository identity is invalid")
    canonical = f"{match.group('owner')}/{match.group('repo')}"
    expected_owner = _PROTECTED_REPOSITORY_OWNERS.get(match.group("repo").casefold())
    if expected_owner is not None and match.group("owner").casefold() != expected_owner:
        raise ScoutError("IDENTITY_TYPOSQUAT", "candidate repository impersonates a protected identity")
    return canonical, f"https://github.com/{canonical}"


def _safe_text(value: Any, *, limit: int = MAX_METADATA_BYTES) -> str:
    if not isinstance(value, str):
        raise ScoutError("METADATA_MALFORMED", "candidate metadata text is invalid")
    text = value.strip()
    if not text or len(text.encode("utf-8")) > limit or any(ord(ch) < 32 and ch not in "\n\t" for ch in text):
        raise ScoutError("METADATA_MALFORMED", "candidate metadata text is invalid")
    return text


def _metadata_is_suspicious(*values: Any) -> bool:
    for value in values:
        if not isinstance(value, str):
            continue
        folded = value.casefold()
        if any(marker in folded for marker in _PROMPT_INJECTION_MARKERS):
            return True
    return False


def _safe_tokens(*values: Any, limit: int = 12) -> list[str]:
    tokens: list[str] = []
    for value in values:
        if isinstance(value, list):
            pieces = value
        elif isinstance(value, str):
            pieces = re.findall(r"[a-z0-9][a-z0-9._-]{1,63}", value.casefold())
        else:
            continue
        for piece in pieces:
            token = str(piece).casefold().replace("_", "-")
            if SAFE_TAG_RE.fullmatch(token) and token not in tokens:
                tokens.append(token)
                if len(tokens) >= limit:
                    return sorted(tokens)
    return sorted(tokens)


def _candidate_id(identity_key: str, immutable_value: str) -> str:
    digest = hashlib.sha256(f"{identity_key}\n{immutable_value}".encode("utf-8")).hexdigest()
    return f"candidate/{digest}"


def _license_from_research(value: Any, *, rejected_for_license: bool = False) -> str:
    if not isinstance(value, str) or not value.strip():
        return "MISSING"
    folded = value.casefold()
    if "unresolved" in folded or "unknown" in folded or "no license" in folded:
        return "MISSING"
    if rejected_for_license or "proprietary" in folded:
        return "INCOMPATIBLE"
    if folded in _PERMISSIVE_LICENSES:
        return "VERIFIED_COMPATIBLE"
    if any(marker in folded for marker in _RESTRICTED_LICENSE_MARKERS):
        return "VERIFIED_RESTRICTED"
    return "AMBIGUOUS"


def _license_from_untrusted_metadata(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return "MISSING"
    return "AMBIGUOUS"


def _iso_timestamp(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ScoutError("EVIDENCE_TIMESTAMP_INVALID", "candidate evidence timestamp is invalid")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ScoutError("EVIDENCE_TIMESTAMP_INVALID", "candidate evidence timestamp is invalid") from exc
    if parsed.tzinfo is None:
        raise ScoutError("EVIDENCE_TIMESTAMP_INVALID", "candidate evidence timestamp is invalid")
    return parsed.astimezone(timezone.utc)


def _freshness(observed: datetime, now: datetime) -> str:
    if observed > now + timedelta(minutes=5):
        return "future_invalid"
    if now - observed > timedelta(days=EVIDENCE_TTL_DAYS):
        return "stale"
    return "fresh"


def _queries(requirements: RuntimeRequirements) -> list[str]:
    values = list(requirements.domains) + list(requirements.outputs) + list(requirements.validation_requirements)
    queries: list[str] = []
    for value in values:
        normalized = value.replace("_", "-").casefold()
        if normalized not in queries:
            queries.append(normalized)
        if len(queries) >= MAX_SEARCH_QUERIES:
            break
    if not queries:
        raise ScoutError("QUERY_INVALID", "Scout capability-gap query is empty")
    return queries


def _public_queries(requirements: RuntimeRequirements, source_kinds: set[str]) -> list[str]:
    """Map local requirements to a fixed non-sensitive public search vocabulary."""
    values = [
        requirements.task_category,
        *requirements.domains,
        *requirements.outputs,
        *requirements.validation_requirements,
    ]
    safe: list[str] = []
    for value in values:
        normalized = value.replace("_", "-").casefold()
        mapped = _PUBLIC_QUERY_ALIASES.get(normalized)
        if mapped is not None and mapped not in safe:
            safe.append(mapped)
        for piece in re.split(r"[.:-]", normalized):
            if piece in _PUBLIC_QUERY_TERMS and piece not in safe:
                safe.append(piece)
        if len(safe) >= MAX_SEARCH_QUERIES:
            break
    if not safe:
        safe.append("mcp" if "mcp_registry" in source_kinds else "skill")
    return safe[:MAX_SEARCH_QUERIES]


def _base_candidate(
    *,
    capability_type: str,
    provider_id: str,
    identity_key: str,
    canonical_identity: str,
    canonical_url: str,
    immutable_kind: str,
    immutable_value: str,
    immutable_verification: str,
    source_id: str,
    discovered_at: datetime,
    evidence_observed_at: datetime,
    provenance_state: str,
    license_state: str,
    trust_state: str,
    compatibility_state: str,
    lifecycle_state: str,
    claimed_tags: Sequence[str],
    verified_tags: Sequence[str],
    evidence_references: Sequence[str],
    admission_disposition: str,
    reason_codes: Sequence[str],
    declared_execution_mechanisms: Sequence[str] = (),
    authentication_state: str = "not_applicable",
) -> dict[str, Any]:
    if capability_type not in CANDIDATE_TYPES:
        raise ScoutError("CANDIDATE_TYPE_INVALID", "candidate capability type is invalid")
    if not SAFE_PROVIDER_RE.fullmatch(provider_id):
        raise ScoutError("IDENTITY_INVALID", "candidate provider identity is invalid")
    url = _validated_https_url(canonical_url)
    if license_state not in LICENSE_STATES or admission_disposition not in ADMISSION_DISPOSITIONS:
        raise ScoutError("ADMISSION_INVALID", "candidate admission state is invalid")
    evidence_urls = [_validated_https_url(item) for item in evidence_references[:3]]
    candidate = {
        "candidate_id": _candidate_id(identity_key, immutable_value),
        "capability_type": capability_type,
        "provider_id": provider_id,
        "identity_key": identity_key,
        "canonical_identity": canonical_identity,
        "canonical_url": url,
        "immutable_reference": {
            "kind": immutable_kind,
            "value": immutable_value,
            "verification_state": immutable_verification,
        },
        "source_ids": [source_id],
        "discovered_at": discovered_at.isoformat().replace("+00:00", "Z"),
        "evidence_observed_at": evidence_observed_at.isoformat().replace("+00:00", "Z"),
        "provenance_state": provenance_state,
        "license_state": license_state,
        "trust_state": trust_state,
        "compatibility_state": compatibility_state,
        "lifecycle_state": lifecycle_state,
        "execution_mechanism": "none",
        "declared_execution_mechanisms": sorted(set(declared_execution_mechanisms)),
        "authentication_state": authentication_state,
        "claimed_capability_tags": _safe_tokens(list(claimed_tags)),
        "verified_capability_tags": _safe_tokens(list(verified_tags)),
        "evidence_references": evidence_urls,
        "admission_disposition": admission_disposition,
        "reason_codes": sorted(set(reason_codes)),
        "ranking": {"score": 0, "position": None, "relation": "ineligible"},
        "authority_states": {
            "installation": "not_installed",
            "enablement": "not_enabled",
            "loading": "not_loaded",
            "execution": "not_executed",
            "validation": "not_validated",
        },
    }
    return validate_candidate(candidate)


_CANDIDATE_FIELDS = {
    "candidate_id",
    "capability_type",
    "provider_id",
    "identity_key",
    "canonical_identity",
    "canonical_url",
    "immutable_reference",
    "source_ids",
    "discovered_at",
    "evidence_observed_at",
    "provenance_state",
    "license_state",
    "trust_state",
    "compatibility_state",
    "lifecycle_state",
    "execution_mechanism",
    "declared_execution_mechanisms",
    "authentication_state",
    "claimed_capability_tags",
    "verified_capability_tags",
    "evidence_references",
    "admission_disposition",
    "reason_codes",
    "ranking",
    "authority_states",
}


def validate_candidate(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != _CANDIDATE_FIELDS:
        raise ScoutError("CANDIDATE_MALFORMED", "candidate record is malformed")
    candidate_id = value.get("candidate_id")
    if not isinstance(candidate_id, str) or not re.fullmatch(r"candidate/[0-9a-f]{64}", candidate_id):
        raise ScoutError("CANDIDATE_MALFORMED", "candidate identity is malformed")
    if value.get("capability_type") not in CANDIDATE_TYPES:
        raise ScoutError("CANDIDATE_MALFORMED", "candidate type is malformed")
    provider_id = value.get("provider_id")
    identity_key = value.get("identity_key")
    canonical_identity = value.get("canonical_identity")
    if (
        not isinstance(provider_id, str)
        or not SAFE_PROVIDER_RE.fullmatch(provider_id)
        or not isinstance(identity_key, str)
        or not identity_key
        or len(identity_key.encode("utf-8")) > 512
        or not isinstance(canonical_identity, str)
        or not canonical_identity
        or len(canonical_identity.encode("utf-8")) > 1024
        or any(ord(ch) < 32 for ch in identity_key + canonical_identity)
    ):
        raise ScoutError("CANDIDATE_MALFORMED", "candidate canonical identity is malformed")
    if value.get("execution_mechanism") != "none":
        raise ScoutError("EXECUTION_AUTHORITY_FORBIDDEN", "Scout candidate cannot receive execution authority")
    declared = value.get("declared_execution_mechanisms")
    if (
        not isinstance(declared, list)
        or len(declared) != len(set(declared))
        or not set(declared) <= DECLARED_EXECUTION_MECHANISMS
        or value.get("authentication_state") not in AUTHENTICATION_STATES
    ):
        raise ScoutError("CANDIDATE_MALFORMED", "candidate declared execution metadata is malformed")
    if value.get("admission_disposition") not in ADMISSION_DISPOSITIONS:
        raise ScoutError("CANDIDATE_MALFORMED", "candidate disposition is malformed")
    if value.get("license_state") not in LICENSE_STATES:
        raise ScoutError("CANDIDATE_MALFORMED", "candidate license state is malformed")
    for key in ("provenance_state", "trust_state", "compatibility_state"):
        state = value.get(key)
        if not isinstance(state, str) or not TOKEN_RE.fullmatch(state):
            raise ScoutError("CANDIDATE_MALFORMED", "candidate evidence state is malformed")
    disposition = value.get("admission_disposition")
    lifecycle = value.get("lifecycle_state")
    expected_lifecycle = {
        "ADMITTED_FOR_REVIEW": "classified",
        "REFERENCE_ONLY": "classified",
        "INSUFFICIENT_EVIDENCE": "classified",
        "QUARANTINED": "quarantined",
        "REJECTED": "rejected",
    }.get(str(disposition))
    if lifecycle not in CANDIDATE_LIFECYCLES or lifecycle != expected_lifecycle:
        raise ScoutError("LIFECYCLE_PROMOTION_FORBIDDEN", "Scout candidate lifecycle is invalid")
    authority = value.get("authority_states")
    if authority != {
        "installation": "not_installed",
        "enablement": "not_enabled",
        "loading": "not_loaded",
        "execution": "not_executed",
        "validation": "not_validated",
    }:
        raise ScoutError("EXECUTION_AUTHORITY_FORBIDDEN", "Scout candidate authority state is invalid")
    immutable = value.get("immutable_reference")
    if not isinstance(immutable, Mapping) or set(immutable) != {"kind", "value", "verification_state"}:
        raise ScoutError("CANDIDATE_MALFORMED", "candidate immutable reference is malformed")
    immutable_value = immutable.get("value")
    if (
        not isinstance(immutable.get("kind"), str)
        or not isinstance(immutable_value, str)
        or not immutable_value
        or not isinstance(immutable.get("verification_state"), str)
        or value.get("candidate_id") != _candidate_id(identity_key, immutable_value)
    ):
        raise ScoutError("CANDIDATE_MALFORMED", "candidate immutable identity is inconsistent")
    for key in ("source_ids", "claimed_capability_tags", "verified_capability_tags", "evidence_references", "reason_codes"):
        items = value.get(key)
        if not isinstance(items, list) or len(items) != len(set(items)):
            raise ScoutError("CANDIDATE_MALFORMED", "candidate list field is malformed")
    if (
        any(not isinstance(item, str) or not SOURCE_ID_RE.fullmatch(item) for item in value["source_ids"])
        or any(not isinstance(item, str) or not SAFE_TAG_RE.fullmatch(item) for item in value["claimed_capability_tags"] + value["verified_capability_tags"])
        or any(not isinstance(item, str) or not TOKEN_RE.fullmatch(item) for item in value["reason_codes"])
    ):
        raise ScoutError("CANDIDATE_MALFORMED", "candidate bounded token field is malformed")
    _iso_timestamp(value.get("discovered_at"))
    _iso_timestamp(value.get("evidence_observed_at"))
    _validated_https_url(value.get("canonical_url"))
    for ref in value.get("evidence_references", []):
        _validated_https_url(ref)
    ranking = value.get("ranking")
    if (
        not isinstance(ranking, Mapping)
        or set(ranking) != {"score", "position", "relation"}
        or not isinstance(ranking.get("score"), int)
        or ranking.get("position") is not None and not isinstance(ranking.get("position"), int)
        or ranking.get("relation") not in {
            "ineligible", "recommended", "alternative", "complementary", "redundant", "reference_only"
        }
    ):
        raise ScoutError("CANDIDATE_MALFORMED", "candidate ranking is malformed")
    return json.loads(json.dumps(value, ensure_ascii=False))


def _research_candidate_type(record: Mapping[str, Any]) -> str | None:
    category = str(record.get("category", "")).casefold()
    repository = str(record.get("repository", "")).casefold()
    description = str(record.get("description", "")).casefold()
    if "mcp" in category or "mcp" in repository or "mcp server" in description:
        return "mcp_registry_source"
    if "skill" in category or "agent skill" in description:
        return "agent_skill_source"
    return None


def candidates_from_research_snapshot(
    payload: Any,
    *,
    source_id: str,
    requirements: RuntimeRequirements,
    now: datetime,
) -> list[dict[str, Any]]:
    if (
        not isinstance(payload, Mapping)
        or payload.get("schema_version") != "nexus.ecosystem-gap-scan.v1"
        or payload.get("research_only") is not True
        or not isinstance(payload.get("authority_statement"), str)
        or "No candidate record grants" not in payload["authority_statement"]
    ):
        raise ScoutError("RESEARCH_EVIDENCE_INVALID", "Gap Scan research evidence is invalid")
    observed = _iso_timestamp(payload.get("generated_at"))
    freshness = _freshness(observed, now)
    serious = payload.get("serious_candidates")
    if not isinstance(serious, list) or len(serious) != 69:
        raise ScoutError("RESEARCH_EVIDENCE_INVALID", "Gap Scan serious-candidate boundary changed")
    query_tokens = set(_queries(requirements))
    prepared: list[tuple[int, dict[str, Any]]] = []
    for raw in serious:
        if not isinstance(raw, Mapping):
            raise ScoutError("RESEARCH_EVIDENCE_INVALID", "Gap Scan candidate is malformed")
        capability_type = _research_candidate_type(raw)
        if capability_type is None:
            continue
        metadata_values = (
            raw.get("description"), raw.get("category"), raw.get("gap_addressed"), raw.get("nexus_decision")
        )
        suspicious = _metadata_is_suspicious(*metadata_values)
        repository, canonical_url = _canonical_github_repository(raw.get("canonical_repository") or raw.get("repository"))
        if raw.get("canonical_url") != canonical_url:
            raise ScoutError("RESEARCH_IDENTITY_MISMATCH", "Gap Scan canonical repository URL mismatches identity")
        commit = raw.get("exact_commit")
        commit_valid = isinstance(commit, str) and bool(COMMIT_RE.fullmatch(commit))
        review_verified = (
            raw.get("review_status") == "DEEPLY_EVALUATED"
            and raw.get("source_status") == "CANDIDATE_SOURCE"
            and commit_valid
            and raw.get("commit_membership_verified") is not False
        )
        disposition = str(raw.get("disposition", ""))
        rejected_for_license = disposition == "REJECT" and any(
            marker in str(raw.get("principal_risks", "")).casefold()
            for marker in ("license", "proprietary")
        )
        license_state = _license_from_research(raw.get("license"), rejected_for_license=rejected_for_license)
        reason_codes: list[str] = ["research_evidence_only", "no_execution_authority"]
        duplicate_group = raw.get("duplicate_group")
        duplicate_tag: str | None = None
        if isinstance(duplicate_group, str) and duplicate_group.strip():
            duplicate_tag = "duplicate:" + hashlib.sha256(
                duplicate_group.strip().casefold().encode("utf-8")
            ).hexdigest()[:12]
            reason_codes.append("known_duplicate_group")
        if disposition == "REJECT":
            admission, lifecycle = "REJECTED", "rejected"
            reason_codes.append("previously_rejected")
        elif suspicious:
            admission, lifecycle = "QUARANTINED", "quarantined"
            reason_codes.append("suspicious_metadata")
        elif freshness != "fresh":
            admission, lifecycle = "INSUFFICIENT_EVIDENCE", "classified"
            reason_codes.append("stale_evidence")
        elif not review_verified:
            admission, lifecycle = "INSUFFICIENT_EVIDENCE", "classified"
            reason_codes.append(
                "commit_not_belonging_to_repository"
                if raw.get("commit_membership_verified") is False
                else "provenance_unverified"
            )
        elif license_state == "INCOMPATIBLE":
            admission, lifecycle = "REJECTED", "rejected"
            reason_codes.append("license_incompatible")
        elif disposition in {"ADAPT PATTERNS", "REFERENCE ONLY"}:
            admission, lifecycle = "REFERENCE_ONLY", "classified"
            reason_codes.append("research_reference_only")
        elif disposition == "WATCH":
            admission, lifecycle = "INSUFFICIENT_EVIDENCE", "classified"
            reason_codes.append("watch_only")
        else:
            admission, lifecycle = "ADMITTED_FOR_REVIEW", "classified"
            reason_codes.append("deep_research_candidate")
        if license_state in {"MISSING", "AMBIGUOUS"} and admission == "ADMITTED_FOR_REVIEW":
            admission = "INSUFFICIENT_EVIDENCE"
            reason_codes.append("license_evidence_insufficient")
        tags = _safe_tokens(
            raw.get("category", ""), raw.get("domains", []), raw.get("gap_addressed", ""),
            raw.get("description", ""), repository, [duplicate_tag] if duplicate_tag else [],
        )
        overlap = len(query_tokens & set(tags))
        if not overlap and not ({"skill", "mcp"} & set(tags)):
            continue
        candidate = _base_candidate(
            capability_type=capability_type,
            provider_id=repository.split("/", 1)[0].casefold(),
            identity_key=f"github:{repository.casefold()}",
            canonical_identity=f"github:{repository}@{commit if commit_valid else 'unpinned'}",
            canonical_url=canonical_url,
            immutable_kind="git_commit" if commit_valid else "mutable_or_missing",
            immutable_value=commit if commit_valid else "unverified",
            immutable_verification="verified_at_research_snapshot" if review_verified else "unverified",
            source_id=source_id,
            discovered_at=now,
            evidence_observed_at=observed,
            provenance_state="verified_research_snapshot" if review_verified else "insufficient",
            license_state=license_state,
            trust_state="candidate_research_evidence_only",
            compatibility_state=(
                "reference_only" if admission == "REFERENCE_ONLY" else
                "incompatible" if admission == "REJECTED" else "adaptable"
            ),
            lifecycle_state=lifecycle,
            claimed_tags=tags,
            verified_tags=[str(item).casefold() for item in raw.get("domains", []) if isinstance(item, str)],
            evidence_references=[item for item in raw.get("evidence_urls", []) if isinstance(item, str)],
            admission_disposition=admission,
            reason_codes=reason_codes,
            declared_execution_mechanisms=["reference_source"],
            authentication_state="not_applicable",
        )
        prepared.append((overlap, candidate))
    prepared.sort(key=lambda item: (-item[0], item[1]["candidate_id"]))
    if len(prepared) > MAX_CANDIDATES_PER_SOURCE:
        prepared = prepared[:MAX_CANDIDATES_PER_SOURCE]
    return [item[1] for item in prepared]


def _parse_frontmatter(raw: bytes) -> tuple[dict[str, str], str]:
    if len(raw) > MAX_SKILL_ARTIFACT_BYTES:
        raise ScoutError("SKILL_SIZE_OVERFLOW", "Skill artifact exceeded its byte budget")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ScoutError("SKILL_METADATA_MALFORMED", "Skill artifact is not UTF-8") from exc
    normalized = text.replace("\r\n", "\n")
    if not normalized.startswith("---\n"):
        raise ScoutError("SKILL_METADATA_MALFORMED", "Skill frontmatter is missing")
    end = normalized.find("\n---\n", 4)
    if end < 0:
        raise ScoutError("SKILL_METADATA_MALFORMED", "Skill frontmatter is unterminated")
    frontmatter: dict[str, str] = {}
    for line in normalized[4:end].splitlines():
        if not line.strip():
            continue
        if ":" not in line or line[:1].isspace():
            raise ScoutError("SKILL_METADATA_MALFORMED", "Skill frontmatter uses unsupported structure")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip("\"").strip("'")
        if key in frontmatter or not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", key):
            raise ScoutError("SKILL_METADATA_MALFORMED", "Skill frontmatter key is invalid")
        frontmatter[key] = value
    if set(("name", "description")) - set(frontmatter):
        raise ScoutError("SKILL_METADATA_MALFORMED", "Skill name or description is missing")
    return frontmatter, normalized[end + 5:]


def candidates_from_agent_skills_index(
    payload: Any,
    *,
    source: Mapping[str, Any],
    index_url: str,
    artifacts: Mapping[str, bytes],
    requirements: RuntimeRequirements,
    now: datetime,
) -> list[dict[str, Any]]:
    if not isinstance(payload, Mapping) or payload.get("$schema") != AGENT_SKILLS_DISCOVERY_SCHEMA:
        raise ScoutError("SKILL_INDEX_SCHEMA_UNSUPPORTED", "Agent Skills index schema is unsupported")
    skills = payload.get("skills")
    if not isinstance(skills, list):
        raise ScoutError("SKILL_INDEX_MALFORMED", "Agent Skills index is malformed")
    if len(skills) > MAX_CANDIDATES_PER_SOURCE:
        raise ScoutError("CANDIDATE_OVERFLOW", "Agent Skills index exceeds the candidate budget")
    allowed_hosts = frozenset(str(item).casefold() for item in source.get("allowed_hosts", []))
    index_host = (urlsplit(index_url).hostname or "").casefold()
    if index_host not in allowed_hosts:
        raise ScoutError("SOURCE_CONFIG_INVALID", "Agent Skills index host is not allowlisted")
    query_tokens = set(_queries(requirements))
    results: list[dict[str, Any]] = []
    for entry in skills:
        if not isinstance(entry, Mapping):
            raise ScoutError("SKILL_INDEX_MALFORMED", "Agent Skills entry is malformed")
        name = entry.get("name")
        kind = entry.get("type")
        description = entry.get("description")
        digest = entry.get("digest")
        if (
            not isinstance(name, str)
            or not SKILL_NAME_RE.fullmatch(name)
            or "--" in name
            or kind not in {"skill-md", "archive"}
            or not isinstance(description, str)
            or not description.strip()
            or len(description) > 1024
            or not isinstance(digest, str)
            or not re.fullmatch(r"sha256:[0-9a-f]{64}", digest)
        ):
            raise ScoutError("SKILL_INDEX_MALFORMED", "Agent Skills entry fields are malformed")
        resolved = urljoin(index_url, str(entry.get("url", "")))
        resolved = _validated_https_url(resolved, allowed_hosts=allowed_hosts)
        tags = _safe_tokens(name, description)
        suspicious = _metadata_is_suspicious(description)
        raw = artifacts.get(resolved)
        verified = False
        metadata_match = False
        license_state = "MISSING"
        body_suspicious = False
        reason_codes = ["external_content_untrusted", "no_execution_authority"]
        if raw is not None:
            actual = hashlib.sha256(raw).hexdigest()
            if digest != f"sha256:{actual}":
                reason_codes.append("integrity_mismatch")
            elif kind != "skill-md":
                reason_codes.append("archive_not_opened_in_slice2")
            else:
                verified = True
                frontmatter, body = _parse_frontmatter(raw)
                metadata_match = frontmatter["name"] == name and frontmatter["description"] == description
                license_state = _license_from_untrusted_metadata(frontmatter.get("license"))
                body_suspicious = _metadata_is_suspicious(body, frontmatter.get("allowed-tools", ""))
                if not metadata_match:
                    reason_codes.append("skill_metadata_identity_mismatch")
                if body_suspicious:
                    reason_codes.append("untrusted_skill_instruction_detected")
        else:
            reason_codes.append("skill_artifact_not_fetched")
        if suspicious or body_suspicious or (verified and not metadata_match):
            admission, lifecycle = "QUARANTINED", "quarantined"
            reason_codes.append("suspicious_or_mismatched_metadata")
        elif raw is not None and not verified:
            admission, lifecycle = "REJECTED", "rejected"
        elif verified and metadata_match:
            admission, lifecycle = "ADMITTED_FOR_REVIEW", "classified"
            reason_codes.append("artifact_digest_verified")
        else:
            admission, lifecycle = "INSUFFICIENT_EVIDENCE", "classified"
        identity_key = f"agent-skill:{index_host}/{name}"
        results.append(_base_candidate(
            capability_type="agent_skill",
            provider_id=index_host.replace(".", "-"),
            identity_key=identity_key,
            canonical_identity=f"{identity_key}@{digest}",
            canonical_url=resolved,
            immutable_kind="sha256",
            immutable_value=digest.removeprefix("sha256:"),
            immutable_verification="artifact_digest_verified" if verified else "index_claim_only",
            source_id=str(source["source_id"]),
            discovered_at=now,
            evidence_observed_at=now,
            provenance_state="artifact_digest_verified" if verified and metadata_match else "publisher_index_claim",
            license_state=license_state,
            trust_state="untrusted_public_candidate",
            compatibility_state="adaptable" if admission == "ADMITTED_FOR_REVIEW" else "unknown",
            lifecycle_state=lifecycle,
            claimed_tags=tags,
            verified_tags=tags if verified and metadata_match else [],
            evidence_references=[index_url, resolved],
            admission_disposition=admission,
            reason_codes=reason_codes,
            declared_execution_mechanisms=["skill_md" if kind == "skill-md" else "skill_archive"],
            authentication_state="unknown",
        ))
    results.sort(key=lambda item: (-len(query_tokens & set(item["claimed_capability_tags"])), item["candidate_id"]))
    return results


def _mcp_transports(server: Mapping[str, Any]) -> tuple[set[str], bool]:
    transports: set[str] = set()
    authentication_declared = False
    packages = server.get("packages", [])
    remotes = server.get("remotes", [])
    if packages is not None and not isinstance(packages, list):
        raise ScoutError("MCP_METADATA_MALFORMED", "MCP package metadata is malformed")
    if remotes is not None and not isinstance(remotes, list):
        raise ScoutError("MCP_METADATA_MALFORMED", "MCP remote metadata is malformed")
    for package in packages or []:
        if not isinstance(package, Mapping):
            raise ScoutError("MCP_METADATA_MALFORMED", "MCP package entry is malformed")
        transport = package.get("transport")
        if isinstance(transport, Mapping) and isinstance(transport.get("type"), str):
            transports.add(str(transport["type"]).casefold())
        else:
            transports.add("stdio")
        if package.get("environmentVariables") or package.get("packageArguments") or package.get("runtimeArguments"):
            authentication_declared = authentication_declared or bool(package.get("environmentVariables"))
    for remote in remotes or []:
        if not isinstance(remote, Mapping):
            raise ScoutError("MCP_METADATA_MALFORMED", "MCP remote entry is malformed")
        transport = remote.get("type") or remote.get("transport")
        if isinstance(transport, str):
            transports.add(transport.casefold())
        if remote.get("headers"):
            authentication_declared = True
    return transports, authentication_declared


def candidates_from_mcp_registry(
    payload: Any,
    *,
    source_id: str,
    source_url: str,
    now: datetime,
) -> list[dict[str, Any]]:
    if not isinstance(payload, Mapping) or not isinstance(payload.get("servers"), list):
        raise ScoutError("MCP_METADATA_MALFORMED", "MCP Registry response is malformed")
    servers = payload["servers"]
    if len(servers) > MAX_CANDIDATES_PER_SOURCE:
        raise ScoutError("CANDIDATE_OVERFLOW", "MCP Registry response exceeds the candidate budget")
    results: list[dict[str, Any]] = []
    for wrapper in servers:
        if not isinstance(wrapper, Mapping):
            raise ScoutError("MCP_METADATA_MALFORMED", "MCP Registry entry is malformed")
        server = wrapper.get("server", wrapper)
        if not isinstance(server, Mapping):
            raise ScoutError("MCP_METADATA_MALFORMED", "MCP server metadata is malformed")
        name = _safe_text(server.get("name"), limit=256)
        version = _safe_text(server.get("version"), limit=128)
        if not MCP_SERVER_NAME_RE.fullmatch(name) or not VERSION_RE.fullmatch(version):
            raise ScoutError("MCP_METADATA_MALFORMED", "MCP server identity or version is malformed")
        description = server.get("description", "metadata unavailable")
        if not isinstance(description, str) or len(description.encode("utf-8")) > MAX_METADATA_BYTES:
            raise ScoutError("METADATA_SIZE_OVERFLOW", "MCP description exceeds the metadata budget")
        repository_info = server.get("repository")
        repository: str | None = None
        canonical_url: str = source_url
        if isinstance(repository_info, Mapping):
            repo_url = repository_info.get("url")
            if isinstance(repo_url, str):
                parsed = urlsplit(repo_url.removesuffix(".git"))
                if parsed.scheme == "https" and parsed.hostname == "github.com":
                    repository = parsed.path.strip("/")
                    repository, canonical_url = _canonical_github_repository(repository)
        transports, auth = _mcp_transports(server)
        unsupported = bool(transports - SUPPORTED_MCP_TRANSPORTS) or not transports
        suspicious = _metadata_is_suspicious(description, name)
        digest: str | None = None
        for package in server.get("packages", []) or []:
            if isinstance(package, Mapping):
                for key in ("fileSha256", "sha256", "digest"):
                    value = package.get(key)
                    if isinstance(value, str):
                        candidate_digest = value.removeprefix("sha256:")
                        if SHA256_RE.fullmatch(candidate_digest):
                            digest = candidate_digest
                            break
                if digest:
                    break
        identity_key = f"mcp-registry:{name.casefold()}"
        immutable_value = digest or version
        reason_codes = ["official_registry_metadata_only", "no_mcp_connection", "no_execution_authority"]
        license_state = _license_from_untrusted_metadata(server.get("license"))
        if suspicious:
            admission, lifecycle = "QUARANTINED", "quarantined"
            reason_codes.append("suspicious_metadata")
        elif unsupported:
            admission, lifecycle = "REJECTED", "rejected"
            reason_codes.append("unsupported_transport")
        elif digest and repository:
            admission, lifecycle = "ADMITTED_FOR_REVIEW", "classified"
            reason_codes.append("package_digest_present")
        else:
            admission, lifecycle = "INSUFFICIENT_EVIDENCE", "classified"
            reason_codes.append("immutable_provenance_insufficient")
        if auth:
            reason_codes.append("authentication_declared")
        tags = _safe_tokens(name, description, list(transports))
        results.append(_base_candidate(
            capability_type="mcp_server",
            provider_id=(repository.split("/", 1)[0].casefold() if repository else "official-mcp-registry"),
            identity_key=identity_key,
            canonical_identity=f"{identity_key}@{version}" + (f"#{digest}" if digest else ""),
            canonical_url=canonical_url,
            immutable_kind="package_sha256" if digest else "registry_version",
            immutable_value=immutable_value,
            immutable_verification="registry_claim_with_digest" if digest else "version_only_unverified_artifact",
            source_id=source_id,
            discovered_at=now,
            evidence_observed_at=now,
            provenance_state="official_registry_metadata_with_digest" if digest else "official_registry_metadata_only",
            license_state=license_state,
            trust_state="official_registry_unverified_publisher_candidate",
            compatibility_state="adaptable" if not unsupported else "incompatible",
            lifecycle_state=lifecycle,
            claimed_tags=tags,
            verified_tags=sorted(transports) if not unsupported else [],
            evidence_references=[source_url] + ([canonical_url] if canonical_url != source_url else []),
            admission_disposition=admission,
            reason_codes=reason_codes,
            declared_execution_mechanisms=[
                "mcp_" + item.replace("-", "_") for item in sorted(transports)
                if "mcp_" + item.replace("-", "_") in DECLARED_EXECUTION_MECHANISMS
            ],
            authentication_state="declared" if auth else "not_declared",
        ))
    return results


def _deduplicate_and_rank(
    candidates: Sequence[Mapping[str, Any]],
    requirements: RuntimeRequirements,
) -> tuple[list[dict[str, Any]], list[str]]:
    if len(candidates) > MAX_TOTAL_CANDIDATES:
        raise ScoutError("CANDIDATE_OVERFLOW", "Scout candidate total exceeds the bounded budget")
    by_id: dict[str, dict[str, Any]] = {}
    identities: dict[str, set[str]] = {}
    for raw in candidates:
        item = validate_candidate(raw)
        candidate_id = item["candidate_id"]
        identity_key = item["identity_key"]
        identities.setdefault(identity_key, set()).add(candidate_id)
        if candidate_id in by_id:
            existing = by_id[candidate_id]
            conflict_fields = {
                "capability_type", "provider_id", "canonical_identity", "canonical_url",
                "provenance_state", "license_state", "trust_state", "compatibility_state",
                "admission_disposition", "lifecycle_state",
            }
            if any(existing[field] != item[field] for field in conflict_fields):
                existing["admission_disposition"] = "QUARANTINED"
                existing["lifecycle_state"] = "quarantined"
                existing["reason_codes"] = sorted(set(
                    existing["reason_codes"] + item["reason_codes"] + ["duplicate_evidence_conflict"]
                ))
            existing["source_ids"] = sorted(set(existing["source_ids"] + item["source_ids"]))
            existing["evidence_references"] = sorted(
                set(existing["evidence_references"] + item["evidence_references"])
            )[:3]
        else:
            by_id[candidate_id] = item
    for identity_key, candidate_ids in identities.items():
        if len(candidate_ids) > 1:
            for candidate_id in candidate_ids:
                item = by_id[candidate_id]
                item["admission_disposition"] = "QUARANTINED"
                item["lifecycle_state"] = "quarantined"
                item["reason_codes"] = sorted(set(item["reason_codes"] + ["conflicting_candidate_identity"]))
    requirement_tags = set(_queries(requirements))
    eligible: list[dict[str, Any]] = []
    for item in by_id.values():
        overlap = len(requirement_tags & set(item["claimed_capability_tags"] + item["verified_capability_tags"]))
        score = overlap * 8
        if item["admission_disposition"] == "ADMITTED_FOR_REVIEW":
            score += 60
        elif item["admission_disposition"] == "REFERENCE_ONLY":
            score += 20
        elif item["admission_disposition"] == "INSUFFICIENT_EVIDENCE":
            score += 5
        if item["provenance_state"] in {"artifact_digest_verified", "verified_research_snapshot"}:
            score += 15
        if item["license_state"] == "VERIFIED_COMPATIBLE":
            score += 10
        if item["compatibility_state"] in {"compatible", "adaptable"}:
            score += 8
        item["ranking"] = {"score": score, "position": None, "relation": "ineligible"}
        if item["admission_disposition"] == "ADMITTED_FOR_REVIEW" and overlap:
            eligible.append(item)
        elif item["admission_disposition"] == "REFERENCE_ONLY":
            item["ranking"]["relation"] = "reference_only"
    eligible.sort(key=lambda item: (-item["ranking"]["score"], item["candidate_id"]))
    recommended: list[str] = []
    covered: set[str] = set()
    recommended_duplicate_groups: set[str] = set()
    for position, item in enumerate(eligible, start=1):
        tags = set(item["claimed_capability_tags"] + item["verified_capability_tags"])
        relevant = tags & requirement_tags
        duplicate_groups = {tag for tag in tags if tag.startswith("duplicate:")}
        if duplicate_groups & recommended_duplicate_groups:
            item["ranking"] = {"score": item["ranking"]["score"], "position": position, "relation": "redundant"}
        elif relevant - covered and len(recommended) < 3:
            item["ranking"] = {"score": item["ranking"]["score"], "position": position, "relation": "recommended"}
            recommended.append(item["candidate_id"])
            covered.update(relevant)
            recommended_duplicate_groups.update(duplicate_groups)
        elif relevant <= covered:
            item["ranking"] = {"score": item["ranking"]["score"], "position": position, "relation": "redundant"}
        elif relevant:
            item["ranking"] = {"score": item["ranking"]["score"], "position": position, "relation": "alternative"}
        else:
            item["ranking"] = {"score": item["ranking"]["score"], "position": position, "relation": "complementary"}
    ordered = sorted(by_id.values(), key=lambda item: (
        item["ranking"]["position"] is None,
        item["ranking"]["position"] or 999,
        -item["ranking"]["score"],
        item["candidate_id"],
    ))
    return [validate_candidate(item) for item in ordered], recommended


def _forbidden_receipt_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        if set(value) & _FORBIDDEN_RECEIPT_KEYS:
            return True
        return any(_forbidden_receipt_key(item) for item in value.values())
    if isinstance(value, list):
        return any(_forbidden_receipt_key(item) for item in value)
    return False


def validate_scout_receipt(value: Any) -> dict[str, Any]:
    fields = {
        "schema_version", "scout_id", "issued_at", "runtime_decision_id",
        "invoked_reason", "capability_gap", "search_scope", "source_results",
        "candidates", "recommended_candidate_ids", "scout_version",
        "admission_version", "selector_version", "status", "result_code",
        "evidence_freshness", "authority_states", "security_result",
    }
    if not isinstance(value, Mapping) or set(value) != fields or _forbidden_receipt_key(value):
        raise ScoutError("SCOUT_RECEIPT_MALFORMED", "Scout receipt is malformed")
    if value.get("schema_version") != SCOUT_RECEIPT_SCHEMA_VERSION:
        raise ScoutError("SCOUT_RECEIPT_MALFORMED", "Scout receipt schema is unsupported")
    if (
        value.get("scout_version") != SCOUT_VERSION
        or value.get("admission_version") != ADMISSION_VERSION
        or value.get("selector_version") != RUNTIME_SELECTOR_VERSION
    ):
        raise ScoutError("SCOUT_RECEIPT_MALFORMED", "Scout receipt component version is invalid")
    try:
        UUID(str(value.get("scout_id")))
        UUID(str(value.get("runtime_decision_id")))
        issued = _iso_timestamp(value.get("issued_at"))
    except (ValueError, ScoutError) as exc:
        raise ScoutError("SCOUT_RECEIPT_MALFORMED", "Scout receipt identity is malformed") from exc
    if issued.tzinfo is None:
        raise ScoutError("SCOUT_RECEIPT_MALFORMED", "Scout receipt timestamp is malformed")
    gap = value.get("capability_gap")
    if not isinstance(gap, Mapping) or set(gap) != {
        "task_category", "domains", "outputs", "validation_requirements",
    }:
        raise ScoutError("SCOUT_RECEIPT_MALFORMED", "Scout capability gap is malformed")
    if not isinstance(gap.get("task_category"), str) or not TOKEN_RE.fullmatch(gap["task_category"]):
        raise ScoutError("SCOUT_RECEIPT_MALFORMED", "Scout capability gap is malformed")
    for key in ("domains", "outputs", "validation_requirements"):
        items = gap.get(key)
        if (
            not isinstance(items, list)
            or len(items) > 8
            or len(items) != len(set(items))
            or any(not isinstance(item, str) or not TOKEN_RE.fullmatch(item) for item in items)
        ):
            raise ScoutError("SCOUT_RECEIPT_MALFORMED", "Scout capability gap is malformed")
    search_scope = value.get("search_scope")
    if not isinstance(search_scope, Mapping) or set(search_scope) != {"source_ids", "queries", "limits"}:
        raise ScoutError("SCOUT_RECEIPT_MALFORMED", "Scout search scope is malformed")
    source_ids = search_scope.get("source_ids")
    queries = search_scope.get("queries")
    if (
        not isinstance(source_ids, list)
        or len(source_ids) > MAX_SOURCE_IDS
        or len(source_ids) != len(set(source_ids))
        or any(not isinstance(item, str) or not SOURCE_ID_RE.fullmatch(item) for item in source_ids)
        or not isinstance(queries, list)
        or len(queries) > MAX_SEARCH_QUERIES
        or len(queries) != len(set(queries))
        or any(not isinstance(item, str) or not TOKEN_RE.fullmatch(item) for item in queries)
        or search_scope.get("limits") != _limits_receipt()
    ):
        raise ScoutError("SCOUT_RECEIPT_MALFORMED", "Scout search scope is malformed")
    source_results = value.get("source_results")
    if not isinstance(source_results, list) or len(source_results) > MAX_SOURCE_IDS:
        raise ScoutError("SCOUT_RECEIPT_MALFORMED", "Scout source results are malformed")
    for result in source_results:
        if (
            not isinstance(result, Mapping)
            or set(result) != {"source_id", "kind", "status", "candidate_count", "http_requests", "execution_or_connection"}
            or result.get("source_id") not in source_ids
            or result.get("kind") not in SUPPORTED_SOURCE_KINDS
            or result.get("status") != "queried"
            or not isinstance(result.get("candidate_count"), int)
            or not 0 <= result["candidate_count"] <= MAX_CANDIDATES_PER_SOURCE
            or not isinstance(result.get("http_requests"), int)
            or not 0 <= result["http_requests"] <= MAX_HTTP_REQUESTS
            or result.get("execution_or_connection") != "none"
        ):
            raise ScoutError("SCOUT_RECEIPT_MALFORMED", "Scout source result is malformed")
    candidates = value.get("candidates")
    recommended = value.get("recommended_candidate_ids")
    if not isinstance(candidates, list) or len(candidates) > MAX_TOTAL_CANDIDATES:
        raise ScoutError("SCOUT_RECEIPT_MALFORMED", "Scout receipt candidate set is malformed")
    checked = [validate_candidate(item) for item in candidates]
    candidate_ids = [item["candidate_id"] for item in checked]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ScoutError("SCOUT_RECEIPT_MALFORMED", "Scout receipt duplicates a candidate")
    if (
        not isinstance(recommended, list)
        or len(recommended) > 3
        or len(recommended) != len(set(recommended))
        or not set(recommended) <= set(candidate_ids)
    ):
        raise ScoutError("SCOUT_RECEIPT_MALFORMED", "Scout recommendations are malformed")
    candidate_source_ids = {source for item in checked for source in item["source_ids"]}
    if not candidate_source_ids <= set(source_ids):
        raise ScoutError("SCOUT_RECEIPT_MALFORMED", "Scout candidate source binding is malformed")
    if any(
        item["admission_disposition"] != "ADMITTED_FOR_REVIEW"
        or item["ranking"]["relation"] != "recommended"
        for item in checked if item["candidate_id"] in recommended
    ):
        raise ScoutError("SCOUT_RECEIPT_MALFORMED", "Scout recommendation is not admissible")
    status = value.get("status")
    result_code = value.get("result_code")
    reason = value.get("invoked_reason")
    freshness = value.get("evidence_freshness")
    allowed_outcomes = {
        ("not_invoked", "SCOUT_NOT_REQUIRED_TRUSTED_COVERAGE", "not_invoked_trusted_coverage_or_host_evidence_path", "not_applicable"),
        ("not_invoked", "SCOUT_NOT_APPLICABLE_HOST_EVIDENCE_REQUIRED", "not_invoked_trusted_coverage_or_host_evidence_path", "not_applicable"),
        ("recommendation_ready", "SCOUT_RECOMMENDATION_READY", "trusted_capability_gap_capability_not_covered", "fresh"),
        ("recommendation_ready", "SCOUT_RECOMMENDATION_READY", "trusted_capability_gap_capability_not_covered", "mixed_or_stale"),
        ("evidence_only", "SCOUT_NO_ADMISSIBLE_RECOMMENDATION", "trusted_capability_gap_capability_not_covered", "fresh"),
        ("evidence_only", "SCOUT_NO_ADMISSIBLE_RECOMMENDATION", "trusted_capability_gap_capability_not_covered", "mixed_or_stale"),
        ("evidence_only", "SCOUT_NO_ADMISSIBLE_RECOMMENDATION", "trusted_capability_gap_capability_not_covered", "no_candidates"),
    }
    if (status, result_code, reason, freshness) not in allowed_outcomes:
        raise ScoutError("SCOUT_RECEIPT_MALFORMED", "Scout receipt outcome is inconsistent")
    if status == "not_invoked" and any((source_ids, queries, source_results, candidates, recommended)):
        raise ScoutError("SCOUT_RECEIPT_MALFORMED", "non-invoked Scout receipt contains discovery evidence")
    if status != "not_invoked" and (not source_ids or not queries):
        raise ScoutError("SCOUT_RECEIPT_MALFORMED", "invoked Scout receipt lacks a bounded search scope")
    if status != "not_invoked" and {item["source_id"] for item in source_results} != set(source_ids):
        raise ScoutError("SCOUT_RECEIPT_MALFORMED", "invoked Scout receipt lacks a source result")
    if value.get("authority_states") != {
        "installation": "not_installed",
        "enablement": "not_enabled",
        "loading": "not_loaded",
        "execution": "not_executed",
        "validation": "not_validated",
    }:
        raise ScoutError("EXECUTION_AUTHORITY_FORBIDDEN", "Scout receipt authority state is invalid")
    security = value.get("security_result")
    if security != {
        "execution_authority": "none",
        "installation_authority": "none",
        "mcp_connection_authority": "none",
        "host_mapping_authority": "none",
        "lifecycle_promotion_authority": "none",
        "external_content_control_authority": "none",
        "private_host_state_access": "none",
        "recommendation_is_selection_or_execution": False,
    }:
        raise ScoutError("EXECUTION_AUTHORITY_FORBIDDEN", "Scout receipt security boundary is invalid")
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(encoded) > MAX_RECEIPT_BYTES:
        raise ScoutError("RECEIPT_SIZE_OVERFLOW", "Scout receipt exceeded its byte budget")
    return json.loads(json.dumps(value, ensure_ascii=False))


def _authority_states() -> dict[str, str]:
    return {
        "installation": "not_installed",
        "enablement": "not_enabled",
        "loading": "not_loaded",
        "execution": "not_executed",
        "validation": "not_validated",
    }


def _security_result() -> dict[str, Any]:
    return {
        "execution_authority": "none",
        "installation_authority": "none",
        "mcp_connection_authority": "none",
        "host_mapping_authority": "none",
        "lifecycle_promotion_authority": "none",
        "external_content_control_authority": "none",
        "private_host_state_access": "none",
        "recommendation_is_selection_or_execution": False,
    }


def _stable_bytes(path: Path) -> bytes:
    try:
        if path.is_symlink() or not path.is_file():
            raise OSError("not regular")
        before = path.stat()
        raw = path.read_bytes()
        after = path.stat()
    except OSError as exc:
        raise ScoutError("LOCAL_EVIDENCE_UNAVAILABLE", "Scout local evidence is unavailable") from exc
    fingerprint = lambda stat: (stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns)
    if fingerprint(before) != fingerprint(after) or len(raw) != after.st_size:
        raise ScoutError("LOCAL_EVIDENCE_CHANGED", "Scout local evidence changed during verification")
    return raw


def _manifest_digest(raw: bytes, *, normalize_text: bool) -> str:
    if normalize_text:
        try:
            raw = raw.decode("utf-8").replace("\r\n", "\n").encode("utf-8")
        except UnicodeDecodeError:
            pass
    return hashlib.sha256(raw).hexdigest()


def _verified_local_buffers(
    root: Path,
    manifest_path: Path,
    paths: Sequence[Path],
) -> list[bytes]:
    try:
        manifest_raw = _stable_bytes(manifest_path)
        manifest = json.loads(manifest_raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ScoutError("LOCAL_EVIDENCE_INVALID", "Scout integrity manifest is invalid") from exc
    release_manifest = isinstance(manifest, Mapping) and "files" in manifest
    entries = manifest.get("files") if release_manifest else manifest
    if not isinstance(entries, Mapping):
        raise ScoutError("LOCAL_EVIDENCE_INVALID", "Scout integrity manifest is invalid")
    root_resolved = root.resolve(strict=True)
    buffers: list[bytes] = []
    for path in paths:
        try:
            relative = path.resolve(strict=True).relative_to(root_resolved).as_posix()
        except (OSError, ValueError) as exc:
            raise ScoutError("LOCAL_EVIDENCE_INVALID", "Scout evidence is outside its integrity root") from exc
        metadata = entries.get(relative)
        raw = _stable_bytes(path)
        if (
            not isinstance(metadata, Mapping)
            or not isinstance(metadata.get("sha256"), str)
            or not SHA256_RE.fullmatch(str(metadata["sha256"]))
            or _manifest_digest(raw, normalize_text=not release_manifest) != metadata["sha256"]
        ):
            raise ScoutError("LOCAL_EVIDENCE_INTEGRITY_FAILED", "Scout local evidence integrity check failed")
        buffers.append(raw)
    return buffers


def validate_source_config(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping) or set(value) != {"schema_version", "policy", "sources"}:
        raise ScoutError("SOURCE_CONFIG_INVALID", "Scout source configuration is malformed")
    if value.get("schema_version") != SOURCE_CONFIG_SCHEMA_VERSION:
        raise ScoutError("SOURCE_CONFIG_INVALID", "Scout source configuration schema is unsupported")
    policy = value.get("policy")
    if not isinstance(policy, str) or "no install" not in policy.casefold() or "no execution" not in policy.casefold():
        raise ScoutError("SOURCE_CONFIG_INVALID", "Scout source policy is invalid")
    sources = value.get("sources")
    if not isinstance(sources, list) or not sources or len(sources) > MAX_SOURCE_IDS:
        raise ScoutError("SOURCE_CONFIG_INVALID", "Scout source set is invalid")
    seen: set[str] = set()
    checked: list[dict[str, Any]] = []
    for raw in sources:
        if not isinstance(raw, Mapping):
            raise ScoutError("SOURCE_CONFIG_INVALID", "Scout source is malformed")
        required = {"source_id", "kind", "enabled", "default", "trust_state"}
        if not required <= set(raw):
            raise ScoutError("SOURCE_CONFIG_INVALID", "Scout source fields are malformed")
        source_id = raw.get("source_id")
        kind = raw.get("kind")
        if (
            not isinstance(source_id, str)
            or not SOURCE_ID_RE.fullmatch(source_id)
            or source_id in seen
            or kind not in SUPPORTED_SOURCE_KINDS
            or not isinstance(raw.get("enabled"), bool)
            or not isinstance(raw.get("default"), bool)
            or not isinstance(raw.get("trust_state"), str)
        ):
            raise ScoutError("SOURCE_CONFIG_INVALID", "Scout source identity is invalid")
        seen.add(source_id)
        item = dict(raw)
        if kind == "research_snapshot":
            if set(item) != required | {"relative_path"}:
                raise ScoutError("SOURCE_CONFIG_INVALID", "research source fields are invalid")
            relative = item.get("relative_path")
            if (
                relative != "research/nexus-ecosystem-gap-scan.json"
                or Path(str(relative)).is_absolute()
                or ".." in Path(str(relative)).parts
            ):
                raise ScoutError("SOURCE_CONFIG_INVALID", "research source path is unsafe")
        else:
            expected = required | {"canonical_url", "allowed_hosts"}
            if set(item) != expected:
                raise ScoutError("SOURCE_CONFIG_INVALID", "public source fields are invalid")
            hosts = item.get("allowed_hosts")
            if not isinstance(hosts, list) or not hosts or len(hosts) > 4 or any(not isinstance(host, str) for host in hosts):
                raise ScoutError("SOURCE_CONFIG_INVALID", "public source host allowlist is invalid")
            _validated_https_url(item.get("canonical_url"), allowed_hosts=frozenset(host.casefold() for host in hosts))
        checked.append(item)
    result = dict(value)
    result["sources"] = checked
    return json.loads(json.dumps(result, ensure_ascii=False))


def parse_scout_request(value: Any, *, parse_requirements: Callable[[Any], RuntimeRequirements]) -> ScoutRequest:
    if not isinstance(value, Mapping) or set(value) != {"schema_version", "runtime_requirements", "source_ids"}:
        raise ScoutError("SCOUT_REQUEST_INVALID", "Scout request is malformed")
    if value.get("schema_version") != SCOUT_REQUEST_SCHEMA_VERSION:
        raise ScoutError("SCOUT_REQUEST_INVALID", "Scout request schema is unsupported")
    source_ids = value.get("source_ids")
    if (
        not isinstance(source_ids, list)
        or not source_ids
        or len(source_ids) > MAX_SOURCE_IDS
        or len(source_ids) != len(set(source_ids))
        or any(not isinstance(item, str) or not SOURCE_ID_RE.fullmatch(item) for item in source_ids)
    ):
        raise ScoutError("QUERY_OVERFLOW", "Scout source selection is invalid or exceeds its bound")
    try:
        requirements = parse_requirements(value.get("runtime_requirements"))
    except RuntimeDecisionError as exc:
        raise ScoutError("SCOUT_REQUEST_INVALID", "Scout runtime requirements are invalid") from exc
    return ScoutRequest(requirements, tuple(source_ids))


class ScoutRuntimeAdapter:
    """Gap-gated runtime adapter for recommendation-only candidate discovery."""

    def __init__(
        self,
        capability_adapter: RuntimeCapabilityAdapter,
        *,
        root: Path,
        source_config_path: Path | None = None,
        integrity_manifest_path: Path | None = None,
        fetcher_factory: Callable[[], PublicMetadataFetcher] | None = None,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.capability_adapter = capability_adapter
        self.root = root
        self.source_config_path = source_config_path or root / "config" / "scout-sources.json"
        release_manifest = root / "release-manifest.json"
        self.integrity_manifest_path = integrity_manifest_path or (
            release_manifest if release_manifest.is_file() else root / "MANIFEST.json"
        )
        self.fetcher_factory = fetcher_factory or PublicMetadataFetcher
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def _load_sources(self) -> tuple[dict[str, Any], dict[str, Any]]:
        # Parse only the exact byte buffers whose manifest hashes were checked.
        config_raw, research_raw = _verified_local_buffers(
            self.root,
            self.integrity_manifest_path,
            [self.source_config_path, self.root / "research" / "nexus-ecosystem-gap-scan.json"],
        )
        try:
            config = validate_source_config(json.loads(config_raw.decode("utf-8")))
            research = json.loads(research_raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ScoutError("LOCAL_EVIDENCE_INVALID", "Scout local evidence is invalid") from exc
        return config, research

    def scout(self, request: ScoutRequest) -> dict[str, Any]:
        try:
            runtime_decision = self.capability_adapter.decide(request.runtime_requirements)
        except RuntimeDecisionError as exc:
            raise ScoutError("RUNTIME_DECISION_BLOCKED", "trusted runtime decision failed closed") from exc
        now = self.clock().astimezone(timezone.utc)
        local_query_values = _queries(request.runtime_requirements)
        common = {
            "schema_version": SCOUT_RECEIPT_SCHEMA_VERSION,
            "scout_id": str(uuid4()),
            "issued_at": now.isoformat().replace("+00:00", "Z"),
            "runtime_decision_id": runtime_decision["decision_id"],
            "capability_gap": {
                "task_category": request.runtime_requirements.task_category,
                "domains": list(request.runtime_requirements.domains),
                "outputs": list(request.runtime_requirements.outputs),
                "validation_requirements": list(request.runtime_requirements.validation_requirements),
            },
            "scout_version": SCOUT_VERSION,
            "admission_version": ADMISSION_VERSION,
            "selector_version": RUNTIME_SELECTOR_VERSION,
            "authority_states": _authority_states(),
            "security_result": _security_result(),
        }
        if runtime_decision["result_code"] not in {
            "RUNTIME_CAPABILITY_SELECTION_READY", "HOST_EVIDENCE_REQUIRED", "CAPABILITY_NOT_COVERED",
        }:
            raise ScoutError("RUNTIME_DECISION_BLOCKED", "trusted runtime decision returned an unsupported outcome")
        if runtime_decision["result_code"] != "CAPABILITY_NOT_COVERED":
            envelope = {
                **common,
                "invoked_reason": "not_invoked_trusted_coverage_or_host_evidence_path",
                "search_scope": {"source_ids": [], "queries": [], "limits": _limits_receipt()},
                "source_results": [],
                "candidates": [],
                "recommended_candidate_ids": [],
                "status": "not_invoked",
                "result_code": (
                    "SCOUT_NOT_REQUIRED_TRUSTED_COVERAGE"
                    if runtime_decision["result_code"] == "RUNTIME_CAPABILITY_SELECTION_READY"
                    else "SCOUT_NOT_APPLICABLE_HOST_EVIDENCE_REQUIRED"
                ),
                "evidence_freshness": "not_applicable",
            }
            return validate_scout_receipt(envelope)
        config, research = self._load_sources()
        by_id = {item["source_id"]: item for item in config["sources"] if item["enabled"]}
        if not set(request.source_ids) <= set(by_id):
            raise ScoutError("SOURCE_NOT_APPROVED", "Scout source is not approved or enabled")
        query_values = _public_queries(
            request.runtime_requirements,
            {by_id[source_id]["kind"] for source_id in request.source_ids},
        )
        fetcher = self.fetcher_factory()
        candidates: list[dict[str, Any]] = []
        source_results: list[dict[str, Any]] = []
        for source_id in request.source_ids:
            source = by_id[source_id]
            kind = source["kind"]
            if kind == "research_snapshot":
                found = candidates_from_research_snapshot(
                    research,
                    source_id=source_id,
                    requirements=request.runtime_requirements,
                    now=now,
                )
                requests_used = 0
            elif kind == "mcp_registry":
                found = []
                requests_before = fetcher.requests
                per_query_limit = max(1, MAX_CANDIDATES_PER_SOURCE // len(query_values))
                for query in query_values:
                    parsed = urlsplit(source["canonical_url"])
                    query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))
                    query_params.update({"limit": str(per_query_limit), "search": query})
                    url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query_params), ""))
                    response = fetcher.fetch(url, allowed_hosts=source["allowed_hosts"])
                    if response.content_type not in {"application/json", "application/problem+json"}:
                        raise ScoutError("CONTENT_TYPE_INVALID", "MCP Registry did not return JSON")
                    try:
                        payload = json.loads(response.body.decode("utf-8"))
                    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                        raise ScoutError("MCP_METADATA_MALFORMED", "MCP Registry JSON is invalid") from exc
                    batch = candidates_from_mcp_registry(
                        payload,
                        source_id=source_id,
                        source_url=source["canonical_url"],
                        now=now,
                    )
                    if len(batch) > per_query_limit:
                        raise ScoutError("CANDIDATE_OVERFLOW", "MCP Registry ignored the per-query candidate budget")
                    found.extend(batch)
                    if len(found) > MAX_CANDIDATES_PER_SOURCE:
                        raise ScoutError("CANDIDATE_OVERFLOW", "MCP Registry candidate union exceeds its bound")
                requests_used = fetcher.requests - requests_before
            elif kind == "agent_skills_well_known":
                requests_before = fetcher.requests
                response = fetcher.fetch(source["canonical_url"], allowed_hosts=source["allowed_hosts"])
                if response.content_type not in {"application/json", "application/problem+json"}:
                    raise ScoutError("CONTENT_TYPE_INVALID", "Agent Skills index did not return JSON")
                try:
                    payload = json.loads(response.body.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise ScoutError("SKILL_INDEX_MALFORMED", "Agent Skills index JSON is invalid") from exc
                entries = payload.get("skills", []) if isinstance(payload, Mapping) else []
                ranked_entries = sorted(
                    [entry for entry in entries if isinstance(entry, Mapping)],
                    key=lambda entry: (
                        -len(set(local_query_values) & set(_safe_tokens(entry.get("name", ""), entry.get("description", "")))),
                        str(entry.get("name", "")),
                    ),
                )[:MAX_SKILL_ARTIFACT_FETCHES]
                artifact_urls = {
                    _validated_https_url(
                        urljoin(source["canonical_url"], str(entry.get("url", ""))),
                        allowed_hosts=frozenset(host.casefold() for host in source["allowed_hosts"]),
                    )
                    for entry in ranked_entries
                }
                artifacts: dict[str, bytes] = {}
                for artifact_url in sorted(artifact_urls):
                    artifact_response = fetcher.fetch(
                        artifact_url,
                        allowed_hosts=source["allowed_hosts"],
                        max_bytes=MAX_SKILL_ARTIFACT_BYTES,
                    )
                    artifacts[artifact_url] = artifact_response.body
                found = candidates_from_agent_skills_index(
                    payload,
                    source=source,
                    index_url=source["canonical_url"],
                    artifacts=artifacts,
                    requirements=request.runtime_requirements,
                    now=now,
                )
                requests_used = fetcher.requests - requests_before
            else:  # pragma: no cover - source config validator makes this unreachable.
                raise ScoutError("SOURCE_CONFIG_INVALID", "Scout source kind is unsupported")
            candidates.extend(found)
            if len(candidates) > MAX_TOTAL_CANDIDATES:
                raise ScoutError("CANDIDATE_OVERFLOW", "Scout candidate total exceeds its bound")
            source_results.append({
                "source_id": source_id,
                "kind": kind,
                "status": "queried",
                "candidate_count": len(found),
                "http_requests": requests_used,
                "execution_or_connection": "none",
            })
        ranked, recommended = _deduplicate_and_rank(candidates, request.runtime_requirements)
        freshness_states = {
            _freshness(_iso_timestamp(item["evidence_observed_at"]), now) for item in ranked
        }
        envelope = {
            **common,
            "invoked_reason": "trusted_capability_gap_capability_not_covered",
            "search_scope": {
                "source_ids": list(request.source_ids),
                "queries": query_values,
                "limits": _limits_receipt(),
            },
            "source_results": source_results,
            "candidates": ranked,
            "recommended_candidate_ids": recommended,
            "status": "recommendation_ready" if recommended else "evidence_only",
            "result_code": "SCOUT_RECOMMENDATION_READY" if recommended else "SCOUT_NO_ADMISSIBLE_RECOMMENDATION",
            "evidence_freshness": (
                "fresh" if freshness_states <= {"fresh"} else
                "mixed_or_stale" if freshness_states else "no_candidates"
            ),
        }
        return validate_scout_receipt(envelope)


def _limits_receipt() -> dict[str, Any]:
    return {
        "max_search_queries": MAX_SEARCH_QUERIES,
        "max_sources": MAX_SOURCE_IDS,
        "max_candidates_per_source": MAX_CANDIDATES_PER_SOURCE,
        "max_total_candidates": MAX_TOTAL_CANDIDATES,
        "max_redirects": MAX_REDIRECTS,
        "max_response_bytes": MAX_RESPONSE_BYTES,
        "max_metadata_bytes": MAX_METADATA_BYTES,
        "max_http_requests": MAX_HTTP_REQUESTS,
        "timeout_seconds": HTTP_TIMEOUT_SECONDS,
        "retries": HTTP_RETRIES,
        "evidence_ttl_days": EVIDENCE_TTL_DAYS,
    }

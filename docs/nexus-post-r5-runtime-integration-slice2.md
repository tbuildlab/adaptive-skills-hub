# Nexus Post-R5 Runtime Integration — Slice 2

**Status:** development candidate for independent review. It is not accepted,
merged, frozen, installed, or execution-authorized.

## Baselines and scope

Slice 2 starts from the accepted Slice 1 commit
`32d01941acca95a9067329f0493508d151893b42` and retains the R5 frozen commit
`627484495a6578b13532e7560918c137394379af`. The completed Ecosystem Gap Scan
research commit `1968a8ddde1eaaa9ff99393fbb15d625cfb4b013` was cherry-picked as a
separate, auditable research-only commit. Its 55 bounded queries, 265
deduplicated repositories, 69 serious candidates, and 6/17/28/8/10
INTEGRATE/ADAPT/REFERENCE/WATCH/REJECT dispositions were not recomputed.

This slice implements only:

```text
trusted runtime decision
  -> exact CAPABILITY_NOT_COVERED gap
  -> bounded read-only Skill/MCP Scout
  -> provenance/license/trust/compatibility classification
  -> fail-closed candidate admission
  -> deterministic deduplication/ranking
  -> recommendation-only receipt
```

It does not install, enable, load as trusted instructions, connect to, execute,
update, vendor, or promote any candidate. It adds no Agent runtime, remote MCP,
OAuth, background crawler, package-manager call, shell, or subprocess.

## Independent architecture and security review

The review retained the frozen architecture and placed Scout beside, not
inside, the trusted selector. `nexus.scout_candidates` does not accept a prior
decision code, URL, repository, candidate, display name, Host mapping, task
text, project context, credential, install request, or execution request. It
accepts the same closed `nexus.runtime-requirements.v1` object plus up to three
manifest-approved source IDs. The server independently reruns
`RuntimeCapabilityAdapter.decide`; discovery proceeds only when that validated
result is exactly `CAPABILITY_NOT_COVERED`.

This closes the major escalation paths reviewed for Slice 2:

- discovery cannot overwrite trusted capability records or lifecycle state;
- display names never participate in identity or authorization;
- mutable branches and missing/unverified pins are insufficient evidence;
- conflicting revisions of one canonical identity are quarantined;
- exact duplicates with conflicting evidence are quarantined conservatively;
- external metadata cannot create an R5 Host mapping or current-turn evidence;
- non-Presentation candidates cannot enter the Presentations-only R5 route;
- recommendations cannot be represented as selection, loading, execution,
  artifact creation, or validation; and
- all local source configuration/research bytes are parsed from the exact
  stable buffers whose manifest hashes were verified.

## Supported sources

### Ecosystem Gap Scan snapshot

`ecosystem-gap-scan` reads the manifest-verified
`research/nexus-ecosystem-gap-scan.json`. It preserves exact reviewed GitHub
repository and commit evidence, prior dispositions, license findings,
duplicate-group hints, and evidence dates. It is research evidence only. A
candidate that was previously rejected stays rejected; WATCH remains
insufficient; ADAPT PATTERNS/REFERENCE ONLY remain reference-only. Evidence
older than the fixed TTL cannot be admitted for review.

TencentCloud/TencentDB-Agent-Memory remains **ADAPT PATTERNS**. Its proxy and
runtime are not installed and do not become dependencies.

### Official MCP Registry

`official-mcp-registry` uses only the manifest-approved HTTPS origin
`registry.modelcontextprotocol.io` and the documented read-only
`/v0.1/servers` API. Registry descriptions, package metadata, transports,
authentication declarations, repository links, versions, and digests are
untrusted candidate data. The Scout never launches a package, connects to a
remote endpoint, sends credentials, or starts OAuth. A registry version without
an artifact digest or immutable repository evidence remains insufficient.

The official registry is a preview metadata service, not a security scanner or
execution-trust authority. Its own architecture expects downstream
aggregators/subregistries to add curation. See:

- <https://registry.modelcontextprotocol.io/docs>
- <https://modelcontextprotocol.io/registry/about>
- <https://modelcontextprotocol.io/registry/registry-aggregators>

### Agent Skills well-known indexes

The adapter implements the pinned Cloudflare discovery RFC v0.2 data model:
`/.well-known/agent-skills/index.json`, exact known `$schema`, bounded entries,
canonical HTTPS resolution, and `sha256:` artifact digests. Only origins
explicitly added to the integrity-protected source configuration can be read.
No third-party publisher origin is enabled by default in this slice; the Gap
Scan supplies existing Skill-source research until a publisher origin receives
separate provenance review.

For `skill-md`, the Scout can read a bounded artifact, verify its raw SHA-256,
and parse only strict frontmatter needed for static classification. The body is
never loaded as instructions or returned in the receipt. Archives are not
extracted in Slice 2. See:

- <https://agentskills.io/specification>
- <https://github.com/cloudflare/agent-skills-discovery-rfc/blob/1bd1167983fa5ac9cd47987710c525308eda1a98/README.md>

Canonical GitHub candidates currently enter through the reviewed Gap Scan
records. Slice 2 does not add an unbounded GitHub search crawler.

## Fixed discovery bounds

| Boundary | Limit |
|---|---:|
| Approved sources per request | 3 |
| Derived search queries | 3 |
| Candidates per source | 8 |
| Total candidates | 16 |
| Redirects per request | 2 |
| HTTP requests | 8 |
| Public response bytes | 512 KiB |
| Candidate metadata bytes | 4 KiB |
| `skill-md` artifact bytes | 128 KiB |
| Skill artifact fetches | 4 |
| Network timeout | 5 seconds |
| Retries | 0 |
| Local research freshness TTL | 30 days |
| MCP receipt bytes | 24 KiB |

Malformed fields, unknown source IDs, query/candidate/redirect/size overflow,
cross-origin redirects, credentials in URLs, private/literal IP targets,
unsafe URL paths, unsupported schemas/transports, and local integrity changes
fail closed.

Normalized requirements are not sent verbatim to public sources. Public search
terms are reduced to a fixed non-sensitive capability vocabulary; an unknown
token falls back to the source category (`mcp` or `skill`). This prevents a
schema-valid but sensitive-looking token from being leaked as a Registry query.

## Candidate identity and admission

The canonical candidate ID is SHA-256 over a display-independent identity key
and immutable reference. Examples of identity keys are an Agent Skill publisher
origin/name, an MCP Registry server identity, or a canonical GitHub owner/repo.
The receipt records:

- candidate and capability type;
- provider and canonical identity/HTTPS URL;
- commit, version, or digest plus verification state;
- source IDs and evidence timestamps;
- provenance, license, trust, compatibility, and lifecycle states;
- declared Skill/MCP mechanism and authentication state;
- claimed and verified bounded capability tags;
- evidence references, reason codes, ranking, and relationship; and
- fixed non-authority states.

Admission outcomes are `ADMITTED_FOR_REVIEW`, `REFERENCE_ONLY`,
`QUARANTINED`, `REJECTED`, and `INSUFFICIENT_EVIDENCE`.
`ADMITTED_FOR_REVIEW` is never equivalent to approved/available/executable.
License is explicit as `VERIFIED_COMPATIBLE`, `VERIFIED_RESTRICTED`,
`AMBIGUOUS`, `MISSING`, or `INCOMPATIBLE`. Missing or ambiguous license cannot
become execution trust.

## Data-plane/control-plane isolation

README text, Skill descriptions, `SKILL.md` frontmatter/body, MCP descriptions,
and registry metadata stay on the untrusted data plane. The Scout reduces them
to bounded tokens and closed evidence states. It never places raw text in the
MCP receipt or in Nexus control instructions. Suspicious control language,
identity mismatch, hash mismatch, unsupported permissions/transports, or
malformed metadata causes quarantine/rejection; undetected prose still cannot
change policy because it is never interpreted as instructions.

Popularity is not used as authority and is not a sole ranking signal. Ranking
uses gap overlap, admission, provenance, license, compatibility, and duplicate
evidence. Only `ADMITTED_FOR_REVIEW` candidates with actual bounded overlap are
ranked for recommendation. Exact duplicates merge only when their evidence is
consistent; known duplicate groups and redundant coverage are marked
redundant, while alternatives/complements remain distinct.

## Receipt and execution boundary

`nexus.candidate-scout-receipt.v1` binds the trusted decision ID, gap, search
scope, source results, candidates, ranking, evidence freshness, Scout/admission
versions, and outcome. Every receipt and candidate states:

```text
execution_authority: none
installation: not_installed
enablement: not_enabled
loading: not_loaded
execution: not_executed
validation: not_validated
```

It additionally fixes MCP connection, Host mapping, lifecycle promotion,
external-content control, and private Host-state authority to `none`.

The MCP tool is read-only but truthfully carries `openWorldHint: true` because
an explicitly requested source may be a fixed public registry. It is not an
open URL fetcher. The local research path performs no network request.

## Compatibility and deferred work

- The frozen R5 v3 Host inventory/assessment/receipt schemas are unchanged.
- `current_turn_host_visible_subset / not_globally_enumerated` remains the only
  Host inventory scope; Scout is public candidate discovery, not Host inventory.
- The sole accepted Host mapping remains the Presentations mapping created only
  from fresh R5 evidence.
- Slice 1 selection, R4/R5 handoff, planner behavior, installers, rollback, and
  prior Core/runtime tags are not redesigned.
- The known Product Design `research` semantic-routing precision issue is
  documented but deferred because it is not required for Scout correctness.
- The Host-managed cache drift affecting document, spreadsheet, PDF, and the
  research-document chain is an environment limitation. No files or trust
  evidence are fabricated to turn the baseline 6/10 smoke into 10/10.
- Agent Runtime, automatic installation/update, remote MCP/OAuth, Slice 3, R6,
  and V1.3 remain deferred.

No Desktop UI/human acceptance is required for this read-only protocol slice.
Independent code/security review and repository acceptance are still required
before any merge or freeze.

## Development checkpoint validation

- Focused Scout/admission/security coverage: 31 tests passed.
- Full repository regression: 261 tests passed with four expected
  environment-dependent skips.
- Isolated GitHub-distribution coverage: 21 tests passed with three expected
  environment-dependent skips. The packaged runtime exercised the local
  research Scout without a development repository or execution authority.
- A live bounded query against the fixed official MCP Registry returned eight
  metadata candidates and no admissible recommendation because immutable
  evidence was insufficient. No server was connected to or launched.
- Final smoke remains 6/10 on both this branch and the unchanged Slice 1
  checkpoint in the same Host environment. The four failures are the known
  Host-managed Plugin-cache drift cases documented above, not Slice 2 changes.
- The 102-file static manifest rebuilt reproducibly: two consecutive builds
  produced the same SHA-256 and an independent per-entry check found zero
  mismatches.
- Static review found no execution primitives in the Scout, no tracked
  runtime/generated state, and no newly introduced credentials or private
  machine paths.

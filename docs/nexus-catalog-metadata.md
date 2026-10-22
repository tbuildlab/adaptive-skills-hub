# Additive Capability Catalog Metadata

`nexus.discover_capabilities` retains its existing input, `nexus.mcp.v1` text-envelope response, legacy fields, filtering and size limits. It adds three fields to each resource:

| Field | Values | Meaning |
| --- | --- | --- |
| description | string or null | Existing discovery-record description; never generated. At most 1,024 characters. |
| description_status | available, missing, redacted, truncated | Whether the source text is present, omitted for safety, or returned as a bounded source prefix. |
| trust_status | verified_trusted, unverified, unknown | Registry identity evidence, not task applicability or permission. |

Descriptions come from the existing discovery parser, which uses the Skill frontmatter description, with an existing first-heading fallback. Neither discovery nor this response generates new descriptions. All descriptions remain untrusted resource metadata, including descriptions of registered resources. Known secret-assignment patterns reuse the existing context reader's detector. Absolute local-path patterns, credential-bearing HTTP URLs and unsafe control characters cause description omission. This is conservative redaction, not a universal secret detector or semantic prompt-injection filter.

`verified_trusted` requires all of:

- The existing applicability registry loads through its unchanged manifest-integrity and schema validator.
- The resource is a Skill with available status and a unique resource ID across the complete catalog, before filtering.
- The ID matches the existing stable-ID algorithm for its discovery-record Skill path.
- The registry's resolver matches the resource name, metadata fingerprint, content hash and source scope uniquely.

The Nexus-owned in-memory applicability shortcut and resource-supplied trust fields cannot grant this catalog status. With a validated registry, missing/mismatched/ambiguous identity, duplicate IDs and unavailable resources are unverified. Registry validation failure produces unknown, while preserving metadata discovery. No raw registry error, paths, instruction bodies or fingerprints are exposed.

The envelope adds `metadata_authority: none`, `description_trust: untrusted_resource_metadata` and `trust_scope: validated_applicability_registry_identity_only`. Existing `host_inventory_authority: none` remains.

This is a bounded catalog snapshot. It does not perform a guarded instruction read, establish current-task applicability, certify Host accessibility, authenticate an Owner, or grant selection/loading/execution permission. Current identity/content must still pass all existing loader and authorization checks. Agent discovery/execution is not added.

Old consumers can continue reading the unchanged legacy subset; no input schema changes or output-schema version bump are required for additive JSON metadata. Unknown extra fields must be ignored by consumers. This does not claim compatibility with undocumented clients that reject every additional field.

Descriptions can consume the existing response budget and therefore reduce the number of returned records. The existing `truncated` and counts remain authoritative. `available_capability_count` retains its legacy meaning of total matching records before response truncation; resource-level availability remains separate. No pagination, new registry or routing logic is introduced.

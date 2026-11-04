# Humanoid Content Metadata Contract

Version 1 planning contract for #5177. This Markdown schema describes outline
records; it is not a replacement article validator or permission to publish.

## Existing Contracts

Published article front matter remains governed by
[`schemas/article-front-matter-v1.schema.json`](../../schemas/article-front-matter-v1.schema.json),
[`config/article-front-matter-allowlist.yml`](../../config/article-front-matter-allowlist.yml)
and the [editorial style guide](../development/editorial-style-guide.md).
Claim provenance and evidence remain governed by
[`schemas/trust-metadata-v1.schema.json`](../../schemas/trust-metadata-v1.schema.json).
Do not redefine `audience-level`, `status`, `evidence-rung` or trust fields here.
The existing article schema's `prerequisites` array is reused without changing
its meaning. Planning fields below are not automatically accepted article keys.

## Required Fields

Every planning record supplies all five keys. Reject missing keys, unknown keys,
wrong types and empty identifiers at editorial review; do not silently default.

| Field | Type and Constraints | Meaning |
| --- | --- | --- |
| `pillar` | Enum: `cross_engine_parity`, `contact_wrenches`, `whole_body_mpc` | Planning pillar; not a measured result or maturity status |
| `series` | Nonempty string; one stable identifier per launch outline | Groups related planned articles; #5178 owns the outlines |
| `prerequisites` | Array of nonempty strings, matching the existing article schema | Page links or named topics; an empty array explicitly means no prerequisites |
| `engines_used` | Unique array drawn from `MuJoCo`, `Drake`, `Pinocchio`, `MJX` | Engines required by the proposed example; not a claim that they agree |
| `datasets_used` | Unique array of exact artifact names from the #5176 rights ledger | Cleared inputs only; an empty array means no external dataset is selected |

For `cross_engine_parity`, `engines_used` must be nonempty. An eventual parity
claim must identify the actual compared engines and pass the publication and
evidence gates; listing engines alone proves nothing.

Each `datasets_used` entry must resolve to one row of
`docs/humanoid/rights-licence-ledger.md` (#5176). Record the intended use against
that row and verify its clearance covers that use. Missing, PENDING or ON-HOLD
rows fail closed. AMASS remains ON-HOLD and must not appear in `datasets_used`
until the owner clears the required licence and intended use in the ledger.
Do not substitute a URL or invented artifact name for a missing row.

## Planning Example

This synthetic outline selects no external dataset. It asserts no completed
experiment, engine parity or clearance. Identifiers are illustrative.

```yaml
pillar: cross_engine_parity
series: humanoid-cross-engine-parity
prerequisites:
  - Rigid-body transforms and spatial wrenches
engines_used:
  - MuJoCo
  - Drake
datasets_used: []
```

## Review and Integration

Reviewers check field types, the pillar enum, engine names, prerequisite links,
and ledger resolution before accepting an outline. Reject an empty parity
engine list, an unknown engine, or any uncleared dataset selection. These are
editorial preconditions in Phase 0; no production ingestion is implemented.

If later site work needs these fields in article front matter, #5171 coordinates
one extension to the existing schema, allowlist and validation fixtures instead
of adding a parallel registry. Keep evidence in the trust contract. Later article
PRs remain subject to Karl → Feynman → panel → Fleet-Critic → Dieter's sign-off
and carry `do-not-merge`; this planning contract does not satisfy that gate.

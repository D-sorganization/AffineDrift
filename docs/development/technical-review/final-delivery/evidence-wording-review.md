# Evidence Wording Review — 5 October 2026

Issue: https://github.com/D-sorganization/AffineDrift/issues/4976
Parent delivery: PR #4970; broad review: #4009.

## Adjudication

Read the full incoming How to Read section at prospective queue candidate 76815ab5e86807ab78d02a98fc69d832b6ab2feb, including its preceding claim-specific/model-conditioned status principle. A read-only Gemini 3.8 Flash review identified three wording concerns. Lead review accepts the following bounded clarification, with no code redesign.

1. The universal "weakest to strongest support" wording conflates model-conditional deduction with empirical support. The six existing categories can describe a progression toward human application without claiming that observations strengthen or weaken a proved identity.
2. A separate group can rerun original observations. That alone is not empirical replication under the explicitly adopted National Academies terminology. Further observations answering the same question are required; neither a different group nor a different participant cohort is a universal requirement. Assess agreement against uncertainty.
3. The existing sentence about the build rejecting absent measured-data records is true. Clarify its limited reach; do not allege a validator defect or imply that another automated check establishes scientific validity.

Primary passage read: https://www.nationalacademies.org/read/25303/chapter/3, definitions and uncertainty, DOI 10.17226/25303. Terms differ among disciplines; explicitly identify the convention used here.

## Intended Prose

Opening: "These six evidence categories organize the progression from model-internal results to empirically bounded human applications. They are not a universal ranking of truth: an identity may hold exactly under stated assumptions while the model's applicability to a golfer remains untested. A page's declared rung summarizes the evidence for its stated claim; other statements do not inherit that support."

Replicated result (same definition in config and guide): "A measured participant finding supported by a further study addressing the same question using newly collected observations, with agreement assessed in light of uncertainty."

Concluding clarification: "Rungs 4-6 require measured participant observations. The build checks that a page declaring one of these rungs links a catalogue record flagged as measured participant data. This is a necessary prerequisite; scientific review must still establish that the data support the claimed comparison, any replication and the application limits. Following the National Academies' terminology, repeating an analysis with the original data can establish computational reproducibility; empirical replication requires new observations."

Link the primary source on National Academies; preserve anchor, six labels, keys, aliases, flags and code behavior. Preserve all unrelated text.

## Validation Plan

Flash inspected the incoming tests. Label/order checks require the existing anchor and six bold numbered labels; definition length must exceed 20 characters. No exact definition strings are pinned. Lead will run the entire evidence-ladder suite plus frontmatter/maturity tests, scoped Quarto rendering/layout checks, canonical claim-audit regeneration and its check. Compare changed metadata semantically: identities, rationales, dates and original acceptance remain unchanged. Only affected source digests should change.

## Implementation and Local Acceptance

Parent PR #4970 merged on 5 October at 15:11:58 UTC as
`7904cfc1c6234e5ce0ac31127021f28b81fcb0a5`, verified as an ancestor of fetched
`origin/main`. Integration commit `7bd543d00` brought that protected guide into
the final handoff branch without changing the queued #4953 branch. The bounded
prose correction was then applied to the guide and matching config definition.

All 54 tests in the evidence-ladder, frontmatter, maturity-vocabulary and caveat
suites pass. Frontmatter validation passes for 245 files. Scoped Quarto HTML
rendering and canonical claim-audit regeneration checks pass. Semantic comparison
finds exactly two guide-hash replacements across the audit inventory and derived
report; review identities, dates, rationales and all other metadata are unchanged.
All config keys, aliases, flags and non-replication definitions remain unchanged.

Desktop/mobile inspection at 1440/390 pixels finds no horizontal document
overflow. The primary-source hyperlink resolves to the inspected National
Academies passage. The single-page local preview reports a missing publication
manifest, a blocked legacy polyfill and a font-path 404. Sticky navigation and
floating controls also affect long element captures; viewport captures were
used to inspect the amended replication and terminology paragraphs. This is
scoped prose/render evidence, not global layout or accessibility clearance.
Exact source and screenshot hashes are in
[the validation receipt](evidence-wording-validation.json).

Protected/public delivery of this clarification is still pending. Publish it
with the final handoff using a regular PR for #4976; retain #4009 until the
protected source, public artifacts and final handoff have all been verified.

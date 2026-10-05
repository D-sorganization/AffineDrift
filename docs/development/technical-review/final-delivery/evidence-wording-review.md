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

No publication edit has been applied. Wait for actual protected merge of the parent changes; never push to the queued PR. Include the correction and its evidence in final handoff delivery after integrating protected main, using a regular PR with issue #4976. Keep #4009 open until protected/public delivery is proved.
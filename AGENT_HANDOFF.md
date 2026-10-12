# Current Agent Handoff

## Shot-Pattern Publication

- AffineDrift issue #5004 published the reviewed article and nine report/graphic assets through protected PR #5005, merged as `ace2a1ac49ec179f982f4457b0e3a2ccb3c16a84`. The source is `articles/shot-pattern-analysis.qmd`; the asset identities are in `articles/shot_pattern_analysis/asset_manifest.json`.
- The live article, PDF, and graphic routes passed 53 publication checks and the PDF hash matched. Four browser cells passed accessibility and overflow checks, but visual inspection found the mobile title split words beside Quarto's unnecessary Code control. That visual finding remains open on the live site.
- Follow-up branch `codex/shot-pattern-mobile-heading` disables Code tools only for this code-free article. A rendered-page Playwright regression fails on the merged source and passes after the change; local Chromium and Mobile Chrome runs pass. Four local desktop/mobile light/dark captures show intact title words and no Code control. These are local validation, not a new live-site acceptance.
- All nine article assets, including the 39-page PDF, retain their recorded byte counts and SHA-256 digests. The scientific review in `reports/shot-pattern-publication/technical-review.md` remains scoped to its original source hash; this follow-up changes presentation metadata only.
- Next: complete canonical pre-PR validation, review and publish the follow-up through the protected queue, then recheck the deployed mobile title and original asset routes. Preserve the upstream study, report and graphic bytes; UpstreamDrift's integration PR #12278 and empirical qualification are separate.

## Other Current Boundaries

- The accepted final technical-review evidence for epic #4009 is in `docs/development/technical-review/final-delivery/closing-review.md` and its public receipt. This handoff does not renew those acceptance claims.
- AffineDrift #3954 is the revision-pinned markerless-mocap publication projection; Tools owns its public contracts and UpstreamDrift owns scientific computation. AffineDrift #3956 is the camera evidence registry; candidate devices and manufactured fixtures are not procurement or validation authority. Neither boundary changes in this follow-up.
- For other workstreams, consult `docs/development/HANDOFF.md`, the governing issue, and their scope-specific receipts before acting. The earlier handoff contains historical checkpoints, including research issue #4828, whose present status is not asserted here.

## Historical Handoff Preservation

The prior 2,943-line `AGENT_HANDOFF.md` from merged source `ace2a1ac49ec179f982f4457b0e3a2ccb3c16a84` is preserved byte-for-byte in [the deterministic gzip archive](docs/development/handoffs/archive/AGENT_HANDOFF_ace2a1ac_20261012.md.gz). Its uncompressed SHA-256 is `f1fa7b514bec7a8cb1b62c3cd1a15476c3f5b09f5f6cd194dc654e37f5b76ed3` (424,035 bytes). Git history also retains the original. Historical statuses inside that archive are evidence of prior checkpoints, not current instructions.

# Current Agent Handoff

## Shot-Pattern Publication

- AffineDrift issue #5004 is closed after protected PR #5005 (`ace2a1ac49ec179f982f4457b0e3a2ccb3c16a84`) and mobile-title PR #5016 (`8162b803e96aefbc998d13dc68b9fd1f1678a455`) merged. The source is `articles/shot-pattern-analysis.qmd`; identities for all nine report/graphic assets are in `articles/shot_pattern_analysis/asset_manifest.json`.
- Deploy Website run 38255088410 completed successfully at `9002c8a2f94050e013762c08de053abab48711ee`, including every-public-page verification. The post-deployment receipt records 53/53 exact HTTP/hash/PDF checks, four browser cells and root manual review; issue #5004 links the final archive. PR #5016's earlier run 38247838597 was automatically canceled when the newer main run started. Exact canceled-run responses and final closure evidence are preserved under `reports/shot-pattern-publication/deploy-stability/`.
- Issue #5019 governs branch `codex/shot-pattern-deploy-stability`, which keeps an active revision-bound Pages publish running while newer main pushes coalesce. Two focused deployment contracts failed on source `9002c8a2` and pass after the workflow/linter change. The prior canonical RM-6 at `5f90c8ec8` passed seven gates; its sole block was the inherited development-log ceiling (76 active, limit 75). The completed #5004 row is now moved to `shipped` through the governed fragment-collator API, with the original log archived byte-for-byte; the validator passes with an unchanged nonblocking portfolio warning. The branch remains unpublished pending a fresh full gate and protected review.
- All nine article assets, including the 39-page PDF, retain their recorded byte counts and SHA-256 digests. The scientific review in `reports/shot-pattern-publication/technical-review.md` remains scoped to its original source hash; this deployment follow-up changes delivery configuration only.
- Next: run canonical RM-6 on this combined source, independently review the log transition and deployment policy, then publish the #5019 repair through the protected queue. Preserve the upstream study, report and graphic bytes; UpstreamDrift's integration PR #12278 and empirical qualification remain separate.

## Other Current Boundaries

- The accepted final technical-review evidence for epic #4009 is in `docs/development/technical-review/final-delivery/closing-review.md` and its public receipt. This handoff does not renew those acceptance claims.
- AffineDrift #3954 is the revision-pinned markerless-mocap publication projection; Tools owns its public contracts and UpstreamDrift owns scientific computation. AffineDrift #3956 is the camera evidence registry; candidate devices and manufactured fixtures are not procurement or validation authority. Neither boundary changes in this follow-up.
- For other workstreams, consult `docs/development/HANDOFF.md`, the governing issue, and their scope-specific receipts before acting. The earlier handoff contains historical checkpoints, including research issue #4828, whose present status is not asserted here.

## Historical Handoff Preservation

The prior 2,943-line `AGENT_HANDOFF.md` from merged source `ace2a1ac49ec179f982f4457b0e3a2ccb3c16a84` is preserved byte-for-byte in [the deterministic gzip archive](docs/development/handoffs/archive/AGENT_HANDOFF_ace2a1ac_20261012.md.gz). Its uncompressed SHA-256 is `f1fa7b514bec7a8cb1b62c3cd1a15476c3f5b09f5f6cd194dc654e37f5b76ed3` (424,035 bytes). Git history also retains the original. Historical statuses inside that archive are evidence of prior checkpoints, not current instructions.

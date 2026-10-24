# Current Agent Handoff

## Shot-Pattern Publication

- AffineDrift issue #5004 is closed after protected PR #5005 (`ace2a1ac49ec179f982f4457b0e3a2ccb3c16a84`) and mobile-title PR #5016 (`8162b803e96aefbc998d13dc68b9fd1f1678a455`) merged. The source is `articles/shot-pattern-analysis.qmd`; identities for all nine report/graphic assets are in `articles/shot_pattern_analysis/asset_manifest.json`.
- Deploy Website run 38255088410 completed successfully at `9002c8a2f94050e013762c08de053abab48711ee`, including every-public-page verification. The post-deployment receipt records 53/53 exact HTTP/hash/PDF checks, four browser cells and root manual review; issue #5004 links the final archive. PR #5016's earlier run 38247838597 was automatically canceled when the newer main run started. Exact canceled-run responses and final closure evidence are preserved under `reports/shot-pattern-publication/deploy-stability/`.
- Issue #5019 governs branch `codex/shot-pattern-deploy-stability`, which keeps an active revision-bound Pages publish running while newer main pushes coalesce. Two focused deployment contracts failed on source `9002c8a2` and pass after the workflow/linter change. The prior canonical RM-6 at `5f90c8ec8` passed seven gates; its sole block was the inherited development-log ceiling (76 active, limit 75). The completed #5004 row is now moved to `shipped` through the governed fragment-collator API, with the original log archived byte-for-byte; the validator passes with an unchanged nonblocking portfolio warning. Fresh canonical RM-6 passed all eight gates at `ba75df15b`; the branch remains unpublished pending independent review and protected PR delivery.
- All nine article assets, including the 39-page PDF, retain their recorded byte counts and SHA-256 digests. The scientific review in `reports/shot-pattern-publication/technical-review.md` remains scoped to its original source hash; this deployment follow-up changes delivery configuration only.
- Next: independently review the log transition and deployment policy, then publish the #5019 repair through the protected queue. Preserve the upstream study, report and graphic bytes; UpstreamDrift's integration PR #12278 and empirical qualification remain separate.

## Null-Space Exploration Article (Epic #5093)

- AD-1 through AD-4 are on `main` (merged PRs #5100, #5101, #5107; superseded AD-3 branch #5105 closed after #5141 restored the pending #5095 change fragment). Article: `articles/after-one-solution-null-space-exploration.qmd` with contract tests in `tests/test_after_one_solution_article.py`; content correction #5137 is merged.
- UpstreamDrift companion code remains in draft PRs #13475, #13470, #13467, #13493; `data/companion/pins.json` keeps those heads `review-required`. AD-5 #5098 (finalize pins after owner merge of the UD PRs) is the remaining AffineDrift checkpoint. `_quarto.yml` menu entry for the article is an owner decision, not automated.

## Other Current Boundaries

- The accepted final technical-review evidence for epic #4009 is in `docs/development/technical-review/final-delivery/closing-review.md` and its public receipt. This handoff does not renew those acceptance claims.
- AffineDrift #3954 is the revision-pinned markerless-mocap publication projection; Tools owns its public contracts and UpstreamDrift owns scientific computation. AffineDrift #3956 is the camera evidence registry; candidate devices and manufactured fixtures are not procurement or validation authority. Neither boundary changes in this follow-up.
- For other workstreams, consult `docs/development/HANDOFF.md`, the governing issue, and their scope-specific receipts before acting. The earlier handoff contains historical checkpoints, including research issue #4828, whose present status is not asserted here.

## Historical Handoff Preservation

The prior 2,943-line `AGENT_HANDOFF.md` from merged source `ace2a1ac49ec179f982f4457b0e3a2ccb3c16a84` is preserved byte-for-byte in [the deterministic gzip archive](docs/development/handoffs/archive/AGENT_HANDOFF_ace2a1ac_20261012.md.gz). Its uncompressed SHA-256 is `f1fa7b514bec7a8cb1b62c3cd1a15476c3f5b09f5f6cd194dc654e37f5b76ed3` (424,035 bytes). Git history also retains the original. Historical statuses inside that archive are evidence of prior checkpoints, not current instructions.

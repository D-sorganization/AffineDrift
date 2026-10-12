---
issue: 5004
summary: "Record the Verified Shot-Pattern Publication Closure"
dl_state: "shipped"
next_step: "AffineDrift publication is complete; UpstreamDrift integration and empirical qualification remain separately governed"
---

Issue #5004 closed on 2026-10-12 at 14:39:27 UTC after protected merges
#5005 (`ace2a1ac49ec179f982f4457b0e3a2ccb3c16a84`) and #5016
(`8162b803e96aefbc998d13dc68b9fd1f1678a455`). Deploy Website run
38255088410 completed successfully at `9002c8a2f94050e013762c08de053abab48711ee`.
The issue's post-deployment receipt records 53/53 exact HTTP/hash/PDF checks,
four browser cells and root manual review. The closed issue, merged PRs and
completed deployment responses are preserved byte-for-byte in deterministic
gzip files under `reports/shot-pattern-publication/deploy-stability/`.

This is a retrospective state correction for the already completed AffineDrift
publication. It does not approve UpstreamDrift integration, empirical claims,
or the separate deployment-concurrency repair governed by #5019.

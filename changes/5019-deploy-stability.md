---
issue: 5019
summary: "Keep a running revision-bound website deployment active while newer pushes coalesce"
branch: "codex/shot-pattern-deploy-stability"
---

Protected publication PRs #5005 and #5016 merged, but the latter's exact-revision
Deploy Website run 38247838597 was canceled in its 65-minute build while checking
every rendered page. New main run 38255088410 had started under the same
workflow/ref concurrency group. The original run, job, and build-log responses
are preserved losslessly in `reports/shot-pattern-publication/deploy-stability/`.

This change preserves the active revision-bound Pages publish and coalesces newer
pending main pushes. It changes no route, scientific claim, asset, manifest,
browser check, or release acceptance rule. Issue #5004 was subsequently closed
after a complete deployment and fresh live verification; this independent
delivery-scheduling repair is governed by issue #5019.

An earlier canonical RM-6 run passed seven gates, including affected unit tests
and workflow lint. The remaining failure was the inherited development-log
ceiling: the existing `origin/main` log had 76 active entries against a limit
of 75. The separate completed #5004 publication row is reconciled through
the governed log collator with its original bytes preserved in this branch.

---
issue: 5004
summary: "Keep a running revision-bound website deployment active while newer pushes coalesce"
dl_state: "in_review"
next_step: "Review this workflow repair, pass canonical gates, merge through protected queue, then verify the actual deployed manifest and public article"
branch: "codex/shot-pattern-deploy-stability"
---

Protected publication PRs #5005 and #5016 merged, but the latter's exact-revision
Deploy Website run 38247838597 was canceled in its 65-minute build while checking
every rendered page. New main run 38255088410 had started under the same
workflow/ref concurrency group. The original run, job, and build-log responses
are preserved losslessly in `reports/shot-pattern-publication/deploy-stability/`.

This change preserves the active revision-bound Pages publish and coalesces newer
pending main pushes. It changes no route, scientific claim, asset, manifest,
browser check, or release acceptance rule. A future complete deployment and
fresh live verification remain necessary for issue #5004 closure.

Canonical RM-6 on the fixed source passed seven gates, including affected unit
tests and workflow lint. The remaining failure is the development-log ceiling:
the existing `origin/main` log has 76 active entries against a limit of 75.
This branch leaves that log and its policy unchanged and remains unpublished.

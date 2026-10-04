---
issue: 4894
summary: "Prepare coordinated flight accuracy and design review with primary-reading limits and helper adjudication"
dl_state: "in_progress"
next_step: "Complete primary reads and revise chapters 8 9 and 10; validate math, rebuild PDF, freeze regression, then regular PR"
owner: "codex"
branch: "fix/flight-accuracy-design-review"
---

Two Flash inventories and complete originals read; no publication edits or acceptance yet. Detailed plan is in the book research/flight-accuracy-review-20261004.md. Parent implementation acceptance through 0f81bb1ac is integrated unchanged; PR 4895 remains stacked on 4891. Parameter PR 4886 delivered with eight verified hashes, receipt copied here; article PR 4889 targets main. Follow main dependencies before retargeting children. Current review lease expires 21:40 UTC. Use per-PR fragments under the new upstream policy; keep existing historical shared-file records intact. Local author PDF references stay outside commits.

Delivery update: article PR #4889 is pushed at 9695aa229 on main, with source hashes unchanged and hooks passing. The central guard found no hold but could not arm due to GitHub GraphQL rate limiting at 19:58 UTC; retry after reset without bypassing protection. Parameter PR #4886 is delivered. Date #4891 and implementation #4895 remain dependent. Implementation head 0f81bb1ac and its acceptance metadata are integrated here. This preparation branch passed five explicit-ref pre-PR gates and all push hooks; no new manuscript acceptance is claimed.

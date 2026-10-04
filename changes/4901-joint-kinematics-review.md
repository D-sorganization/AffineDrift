---
issue: 4901
summary: "Correct joint screw-axis conventions, constraint mobility and soft-tissue stiffness"
dl_state: "in_review"
next_step: "Publish regular PR against #4904, then protected delivery and fetched-main hash verification"
owner: "codex"
branch: "fix/joint-kinematics-review"
---

Complete chapter revised after lead reading and two adjudicated read-only Flash reviews. Detailed reasoning, primary-source scope, rejected helper claims, TDD and PDF scope are in docs/development/technical-review/joint-kinematics-review/review-notes.md. Thirteen actual-listing tests pass; five manufactured identities pass 100 cases each below 1e-6; 76-page PDF with 37 references is visually inspected in affected chapter/TOC/bibliography scope. Audit bindings refreshed while preserving historical identities. Frozen regression and corpus acceptance pending.

Parent #4900 has accepted Chapters 5–6 and full regression 6,894 passed, 93.24% coverage. Experimental #4898 is regular PR #4902. The owner merged #4899/#4897/#4895 into surviving date parent #4891, not main; do not claim remote-main delivery. Article PR #4889 now needs a main-metadata conflict repair after #4893 delivered. All protected merges and canonical hashes must be verified. Joint lease technical-review-20261004-joint through 2026-10-05 00:28 UTC; presence through 00:31 UTC. Worktree C:/Users/diete/Repositories/Worktrees/AffineDrift-joint-kinematics-review. Broader goal remains active.

Accepted source 7d483e5965c55dacdd262fde40d63dba97170232 passed frozen regression: 6,907 passed, 29 skipped, 210 deselected, 60 warnings, 561.84 seconds, 93.24% src coverage. Before/after tracked trees empty. Seven canonical Git-blob hashes and acceptance scope are recorded in reports/technical-review/joint-kinematics-validation.json. Only Chapter 4 advanced: 76 pending-prefix rows of 407 remain. Packaging artifacts were moved into the ignored/untracked QA area after the run. Parent inverse review is regular PR #4904; article main repair is pushed and guarded.

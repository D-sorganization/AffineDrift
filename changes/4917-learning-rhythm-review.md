---
issue: 4917
summary: "Distinguish action effects, rhythmic generators and motor-learning processes"
dl_state: "in_progress"
next_step: "Finish PDF and audit checks, freeze full regression, then accept scoped rows and open a regular PR against #4919"
owner: "codex"
branch: "fix/learning-rhythm-review"
---

Complete Volume IV ch05_ideomotor, ch08_cpg and ch09_motor_learning sources revised (printed Chapters5,9,10). Keep intended, predicted and observed effects distinct; derive rate-model scaling and local phase stability; correct interference definitions, washout/clamp decay and hidden-state recovery. Nine successful agy Gemini3.8 Flash original/final reviews, test proposals and a handoff copyedit read and adjudicated. Lead implemented sources and repaired helper tests.43 actual-listing tests and seven100-case mathematical checks pass. PDF and digest checks pending; corpus remains407 rows,67 pending-prefix rows. No whole-volume or empirical certification.

Parent regular PR #4919: https://github.com/D-sorganization/AffineDrift/pull/4919 . Source bfe4dbbe14c816261a492bcd1b9d824e0de3e530 passed7,004 tests,93.24% coverage, clean frozen tree; parent delivery head dbbcf82ca integrated. This branch PR not created. Ten parent hashes are in prediction-passive-control-validation.json. App PR attachment failed because this thread already has100 artifacts; PR creation and push succeeded.

Delivery chain: #4889 is queued, #4891 contains owner topic merges #4895/#4897/#4899; #4902 -> #4904 -> #4906 -> #4910 -> #4916 -> #4919 are stacked. Owner Claude synchronized #4889 with main at c174453c1538a6ead2a540fba655526916eacf91; latest main c741b3710. This added ADR/test/metadata changes, not reviewed source changes. Latest #4889 checks pass except e2e still running. Retarget only after actual parent remote-main delivery, use central guarded merge and verify source hashes. Do not bypass protections or treat topic merges as main delivery.

Worktree C:/Users/diete/Repositories/Worktrees/AffineDrift-learning-rhythm-review; session technical-review-20261005-learning-rhythm, lease through03:11UTC, receipt5986424716. The initial central lease command was unavailable under GraphQL quota; exact lease format was posted via REST after reading the fresh issue. Presence registered5986418592; historical inbox identity/page-limit errors remain, so absence of all messages is not proven. B/I leases renewed through03:29UTC. Detailed derivations, helper rejections and primary-reading scope: docs/development/technical-review/learning-rhythm-review/review-notes.md. Preserve primary papers, build intermediates and visual sheets untracked.

Final source checkpoint: 84-page PDF, 45 references; physical pages 3–6, 34–37, 62–70 and 82–84 inspected. Final build accepted-pass11.txt has no overfull boxes or unresolved citations/references. All 81 combined listing/reference/audit tests pass. Freeze the source commit for full regression; corpus remains 407 rows and 67 pending-prefix rows.

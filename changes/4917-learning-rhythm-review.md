---
issue: 4917
summary: "Distinguish action effects, rhythmic generators and motor-learning processes"
dl_state: "in_progress"
next_step: "Run pre-PR checks, open a regular PR against #4919, then protected main delivery"
owner: "codex"
branch: "fix/learning-rhythm-review"
---

Complete Volume IV ch05_ideomotor, ch08_cpg and ch09_motor_learning sources accepted (printed Chapters 5, 9, 10). Intended, predicted and observed effects are distinct; rate-model scaling and local phase stability are derived; interference, washout/clamp decay and hidden-state recovery are corrected. Nine successful agy Gemini 3.8 Flash reviews, test proposals and a handoff copyedit were lead-adjudicated. No whole-volume or empirical certification.

Frozen source 1c25166ad562a4d6bf1e3a47f83341aa144f8b60 passed 7,047 tests, 29 skipped, 210 deselected, 60 warnings in 454.97 seconds; source coverage 93.24%, exit 0, tracked tree unchanged. The 84-page PDF has 45 references; physical pages 3–6, 34–37, 62–70 and 82–84 inspected. Final build accepted-pass11.txt has no overfull boxes or unresolved citations/references. All 81 combined listing/reference/audit tests pass; 43 actual-listing tests and seven 100-case independent mathematical checks pass. Nine Git-blob hashes are recorded in reports/technical-review/learning-rhythm-validation.json. Corpus: 407 rows, 64 pending-prefix rows. Counts describe review scope, not empirical certification or uniform percentage completion.

Parent regular PR #4919: https://github.com/D-sorganization/AffineDrift/pull/4919 . Parent delivery head dbbcf82ca integrated. PR for this branch is being prepared. App attachment may fail because the thread already has 100 artifacts; retain the created PR URL.

Delivery chain: #4889 is open on main at c174453c1538a6ead2a540fba655526916eacf91, e2e still running, fresh mergeQueueEntry null. Re-arm only through the central guard once checks pass. #4891 contains owner topic merges #4895/#4897/#4899; #4902 -> #4904 -> #4906 -> #4910 -> #4916 -> #4919 remain stacked. Retarget only after actual parent remote-main delivery and verify source hashes. Topic merges do not establish main delivery.

Worktree C:/Users/diete/Repositories/Worktrees/AffineDrift-learning-rhythm-review; session technical-review-20261005-learning-rhythm, lease through 03:11 UTC, receipt 5986424716. Exact lease format was posted via REST after a fresh issue read when the central GraphQL call failed. Presence 5986418592. Historical inbox identity/page-limit errors remain. Detailed derivations, helper rejections and primary-reading scope: docs/development/technical-review/learning-rhythm-review/review-notes.md. Keep primary papers, build intermediates and visual sheets untracked.

Next bounded review: issue #4921, worktree AffineDrift-golf-capstone-review, branch fix/golf-capstone-review, based on this accepted source. Original chapter/module fully read; two Flash reviews complete and a test proposal delegated. Correct same-state versus trajectory claims, joint versus Cartesian acceleration, grid spacing and inconsistent synthetic torques. No implementation edits yet at this checkpoint.

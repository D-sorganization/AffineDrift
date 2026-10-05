---
issue: 4923
summary: "Correct platform, engine comparison and model construction contracts"
dl_state: "in_review"
next_step: "Open regular PR against fix/golf-capstone-review; await protected parent delivery, retarget to main and verify accepted blobs"
owner: "codex"
branch: "fix/platform-model-contracts-review"
---

Complete Volume V chapters 1–3 reviewed. Corrected RNEA/ABA and MyoSuite descriptions, removed unmeasured engine rankings, repaired initial-energy and time-grid defects, and replaced invalid/disconnected URDF output with a complete analytic cylinder model. The golf extension connects frame/inertia errors, external forces, muscle assumptions and control interpretation. Engine features, wrapper capabilities, numerical verification and human validation remain separate.

49 actual-listing/XML tests passed after all 49 failed against the originals; includes MuJoCo 3.4.0 import. Six independent 100-case checks passed, maximum absolute error 1.098e-9. Six Flash reviews/proposals were lead-adjudicated; exact errors rejected and primary-reading scope are recorded in docs/development/technical-review/platform-model-contracts-review/review-notes.md. PDF pass 4 has 48 pages and 26 references, reviewed physical pages 3–5, 9–19 and 47–48; no scoped overflow. Parent integration requires final rebuild. No empirical or whole-volume certification.

Accepted source 29a555d22ee4c71403259ced67b97b8c66b94ece: 7121 passed, 29 skipped, 210 deselected, 60 warnings, 404.52 seconds, 93.25% source coverage, exit 0 and unchanged tracked tree. The earlier 889584996 run had one bibliography-parser collision; the two descriptive parser titles now differ before protected URDF braces. No guard was weakened. Final PDF pass 10 has 48 pages and 26 entries, with the changed bibliography pages reinspected. Eight exact Git-blob hashes are in reports/technical-review/platform-model-contracts-validation.json. Three complete corpus rows accepted: 407 total, 59 pending-prefix rows. Counts are scope labels, not a scientific completion percentage.

Parent golf capstone is regular PR #4928 at d1641ef33; its final acceptance metadata is integrated. Own lease receipt 5986928965 through 04:11:50 UTC; presence 5987112389 through 04:33:16. Own stash backup retained. Successor #4927 covers simulation, optimization and feedback in its own worktree; no successor source is included here. Protected remote-main delivery remains pending for the earlier chain. Never arm auto-merge into a topic parent or treat that as main delivery.

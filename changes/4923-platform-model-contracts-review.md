---
issue: 4923
summary: "Correct platform, engine comparison and model construction contracts"
dl_state: "in_progress"
next_step: "Finish combined checks and frozen regression; accept three corpus rows and open a regular PR after the golf capstone parent"
owner: "codex"
branch: "fix/platform-model-contracts-review"
---

Complete Volume V chapters 1–3 reviewed. Corrected RNEA/ABA and MyoSuite descriptions, removed unmeasured engine rankings, repaired initial-energy and time-grid defects, and replaced invalid/disconnected URDF output with a complete analytic cylinder model. The golf extension connects frame/inertia errors, external forces, muscle assumptions and control interpretation. Engine features, wrapper capabilities, numerical verification and human validation remain separate.

49 actual-listing/XML tests passed after all 49 failed against the originals; includes MuJoCo 3.4.0 import. Six independent 100-case checks passed, maximum absolute error 1.098e-9. Six Flash reviews/proposals were lead-adjudicated; exact errors rejected and primary-reading scope are recorded in docs/development/technical-review/platform-model-contracts-review/review-notes.md. PDF pass 4 has 48 pages and 26 references, reviewed physical pages 3–5, 9–19 and 47–48; no scoped overflow. Parent integration requires final rebuild. No empirical or whole-volume certification.

Source not yet accepted or in a PR. Corpus has 407 rows, 62 pending-prefix rows after parent capstone acceptance. Own lease receipt 5986928965 through 04:11:50 UTC; presence 5987112389 through 04:33:16. Own stash backup retained. Next: regenerate enclosing evidence after book-ledger repair, run full regression at a clean committed source, record exact hashes, and use a regular stacked PR. Protected remote-main delivery remains pending for the earlier chain.

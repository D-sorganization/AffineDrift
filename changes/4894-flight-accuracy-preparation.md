---
issue: 4894
summary: "Correct the connected flight, accuracy and design chapters with explicit uncertainty and validation limits"
dl_state: "in_review"
next_step: "Publish regular PR after 4895; retarget to main after parent delivery; use central guard and verify canonical hashes; then continue pending corpus"
owner: "codex"
branch: "fix/flight-accuracy-design-review"
---

Complete original/revised chapters 8–10 accepted at ce6e068c464eb680267b4903695cd43cb9aa7728. Seven read-only agy Gemini 3.8 Flash helpers completed and were lead-adjudicated. Research rationale, primary-source reading limits and rejected suggestions are in the book research dossier; canonical bindings and validation are in reports/technical-review/flight-accuracy-validation.json. The 102-page canonical PDF has 102 printed bibliography entries, no unresolved references and visual acceptance of all affected chapters, TOC and bibliography. Four independent 100-case identity checks passed. Final frozen regression passed 6,863 tests, 29 skipped, 210 deselected and 60 warnings in 488.46 seconds with 93.24% coverage. Tracked source stayed unchanged. The initial two root-allowlist failures and subsequent parent repair are preserved. Three corpus rows advance; 81 exact pending rows and one partially reconciled pending row remain. No empirical, whole-book or live-site certification.

Parameter PR #4886 and shared tooling RM #1943 are delivered with remote-main hash receipts. Article #4889 is armed at df1084d07 with static/Python checks passed and browser build running at 20:54 UTC. Date #4891 is pushed at fbab9456b with parent integration, unchanged implementation hashes, 40 focused tests and five pre-PR gates (15 mapped tests); it still targets #4889. Implementation #4895 follows #4891. Open this batch as a regular PR based on #4895; never merge a child into a topic parent. Verify each actual main merge before retargeting the next child. Keep historical PDF/bibliography receipts: the new bibliography and PDF intentionally supersede them without changing accepted earlier chapter sources.

Use per-PR fragments and PR Handoff sections; preserve historical shared records. Keep author PDFs, contact-sheet images and test packaging directories out of commits. Flash read-only camera/survey inventories and lead notes are in TEMP/affine-camera-survey-read-ahead-20261004; both complete originals were read, but no new issue, source edit or acceptance exists. Verify official device manuals and geometry before using those findings. The broad goal remains active.

Forty acceptance metadata/root/SPEC tests passed in 22.12 seconds. Implementation and flight leases/presence renewed through 22:54 UTC (issue receipts 5984283569/5984283709; presence 5984283820/5984284034).

Regular PR #4897 opened at f01cdda80; all push hooks and five explicit-ref pre-PR gates passed (zero mapped tests; full frozen suite separately recorded). Parent implementation delivery repairs through aa08d334a are now integrated with all seven canonical source/evidence hashes unchanged. The parent's transient Windows-decoding failure was repaired from original UTF-8 Git blobs before this integration; one encoding artifact in this fragment was also corrected. Original flight-accuracy session renewed through 23:00 UTC after correcting an accidentally shortened session name; receipts 5984333706 (short-name release), 5984333840 (original lease), 5984321970 (original presence through 22:58 UTC). Next camera/survey work is filed as #4896 and claimed under technical-review-20261004-camera; no source edits there yet.

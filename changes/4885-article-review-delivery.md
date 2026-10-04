---
issue: 4885
summary: "Clarify dimension types and bind educational integration claims to qualified provider evidence"
dl_state: "in_review"
next_step: "Protected main merge of PR 4889, verify four accepted canonical hashes, then retarget date PR 4891"
title: "Dimensionality and Educational Integration Review"
owner: "codex"
branch: "fix/dimensionality-integration-review"
paths: "articles/degrees-of-freedom-and-dimensionality.qmd,articles/upstreamdrift-educational-integration.qmd"
---

Parent PR 4886 is delivered at d33e635d5; all eight hashes verified and lease released. Main merged at 7fb56524a with metadata-only conflict resolutions. Four article acceptance hashes unchanged; original full frozen regression remains valid. Additional 25 root/spec tests pass. PR 4889 now targets main. Source receipt reports/technical-review/parameter-remote-main-receipt.json. Article lease renewed through 21:50 UTC. Date PR 4891 follows; implementation PR 4895 follows it. Broad corpus goal remains active. Use change fragments for future turnover; older shared-file edits predate this policy integration.

Pre-push formatting caught stale whitespace in the newly inherited managed policy. Synced only spec-changelog-rows from central Repository_Management 5ee23e5d (canonical source already corrected at 1cfc3466); exact managed-block equality verified. CLAUDE blank-line cleanup is formatter-only outside managed blocks. No policy wording changed and no hook was bypassed.

CI at 9695aa229 exposed two integration defects: the newly mandated changes/ directory was absent from the root allowlist, and the two source-evidence hashes reflected CRLF working bytes rather than canonical committed LF. The root tests reproduced the first failure before the one-line allowlist repair. The two article working files were normalized to the already-committed LF bytes, with no content or canonical-hash change, then governed evidence regeneration updated just their ledger digests. Review dates, reviewer and source commit now identify the accepted 2026-10-04 review instead of the earlier September review. All 27 root/inventory/output-boundary tests passed after the repair; Ruff, Black and mypy checks follow. This supersedes the earlier claim that the root checks covered the subsequently added fragment. The full scientific-source regression remains historical evidence at 6cd4d2eee, not a claim that the failed CI run passed.

---
issue: 4888
summary: "Preserve verified and unverified publication-date presentation while integrating parent delivery repairs"
dl_state: "in_review"
next_step: "After PR 4889 reaches main, retarget PR 4891; use central merge guard and verify the three accepted implementation hashes on remote main"
owner: "codex"
branch: "fix/unverified-date-display"
---

Integrated parent article PR #4889 through df1084d07, including the root changes/ allowlist and canonical LF claim-evidence metadata repair. All three accepted date implementation blobs still match source 70337154c. Shared-file conflicts retained both historical records; this fragment records current continuation. The existing 6,863-test frozen pass and rendered-browser acceptance remain historical evidence for that unchanged implementation. Integration validation passed: 40 metadata/root/SPEC tests in 29.60 seconds (parent-integration-tests.txt). Parent #4889 is armed and its static/Python checks passed; browser CI is still running. Parameter #4886 and shared tooling RM #1943 are delivered; implementation #4895 and flight/accuracy/design #4894 follow this date change. The date lease/presence lasts through 22:21/22:27 UTC. No draft PR or bypass.

The owner merged camera/flight/implementation PRs into this branch at 1a1374681. These remain parent-branch delivery only. Local main reconciliation integrates article checkpoint 62d4afecf, preserving all independent SPEC rows and turnover histories. Initial apparent dirty files had empty diffs and were resolved by refreshing their Git index, not discarding content. Verify date hashes plus current camera-book hashes; after #4889 merges, retarget #4891 to main and use the guarded queue.

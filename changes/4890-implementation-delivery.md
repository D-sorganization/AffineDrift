---
issue: 4890
summary: "Integrate parent CI repairs without changing the accepted implementation appendix"
dl_state: "in_review"
next_step: "After date PR 4891 reaches main, retarget PR 4895 and use central guard; verify the five canonical hashes before release"
owner: "codex"
branch: "fix/implementation-appendix-review"
---

Parent date PR #4891 integrated through fbab9456b, carrying the changes/ root allowance and canonical LF trust-evidence metadata from article #4889. All five accepted appendix/PDF/bibliography/research/math hashes still match f141a02b5. Historical shared-file conflicts retained both records. The frozen 6,863-test pass, 97-page scoped visual acceptance, five Flash adjudications and independent Jacobian checks remain unchanged. Forty integration metadata/root/SPEC tests passed in 25.53 seconds (parent-integration-tests.txt). Parameter #4886 and shared pre-PR RM #1943 are delivered; article #4889 browser CI is running. Current lease/presence runs through 22:54 UTC. Three following chapters under #4894 have now independently passed full regression at ce6e068c4; their PDF and bibliography intentionally supersede this checkpoint only in that later batch. Use regular PRs and verify each parent on main before retargeting its child.

Initial integration pre-PR gate caught Windows-default decoding damage in the three historical handoff/log files. Reconstructed the merge from the original UTF-8 Git blobs and retained both sides; scientific sources were unaffected. The failed gate log is preserved as parent-integration-pre-pr-initial.txt.

---
issue: 5004
summary: "Prepare a model-conditional shot-pattern research article and share preview"
dl_state: "in_review"
next_step: "Review and push main-merged PR #5005 with passing local gates, await new protected CI, then verify protected merge and public asset responses"
branch: "codex/shot-pattern-report-publication"
---

The revised article and all nine report/graphic assets are populated from the
reviewed UpstreamDrift study source at `f3e83ea8aa754d93ea29b8d176a36fa3d4004a7d`.
The 39-page PDF SHA-256 is
`fd5506da87f5e619a550fb8cc871a0e8195b6fb98965a99809e3238a0f01508b`. The asset
manifest records hashes and source paths, with `e2c3b22c93da1ffc3e5001fd9468a7c6ff4ea429`
as additional study-integration lineage context; neither source commit is
asserted to be publicly reachable. Pinned Quarto 1.8.26 rendering, render
coverage, title capitalization, article link checks, and the cross-page site
gate pass. Open Graph and Twitter previews resolve to the 1200×630 Facebook
preview PNG. This is a locally validated publication draft, not a live site
release; it still requires protected PR review and merge-queue integration.
Upstream study and publication provenance are tracked under UpstreamDrift
#11976 and PR #12278.

The owner authorized a generated pre-merge development-log reconciliation for three independently verified merged scopes (#1976, #4952, #4998). Official collation helpers preserve the other 111 entries and reduce active count from 77 to 74 without changing limits. Evidence and exact patch: `reports/shot-pattern-publication/devlog-reconciliation/`. Publication acceptance still awaits protected delivery and live verification.

The successor review corrects article frontmatter/navigation and separates unavailable nominal matches from simulated-row accounting. It adds an evidence-bound route audit and carries forward only the configuration digests for two existing reviews, preserving their identities/dates/commits. Full gates and live acceptance remain pending; all nine asset bytes are unchanged.

The successor canonical pre-PR at `26f1de47` and evidence freshness checks pass
in the complete requirements environment. The local Python attempt timed out at
60 seconds in unchanged dynamics. The redundant local full-site Quarto render
was terminated after 48/253 pages; remote CI at `94831b9e` completed its
full-site E2E build, Chromium, every-route axe, screenshot, and layout checks
successfully in 56m31s. Updated-commit protected CI and live HTTP/hash
acceptance are still required. See
`reports/shot-pattern-publication/followup-validation.json`.

CI at `94831b9e` passes7,615tests and93.42%coverage but finds a stale
generated search-maturity index. Official regeneration adds only this article
experimental entry; all7index tests and generator freshness pass afterward.
The nine frozen assets and13review-bound evidence digests remain unchanged.
The exact canonical pre-PR pass and incomplete local-render transcripts are
retained in `reports/shot-pattern-publication/` with hashes in the progress
receipt. The CI browser job at `94831b9e` passed. Its overall run failed
solely because the Python lane checked the stale generated index; its dependent
quality gate also failed. The repaired index at `26f1de47` awaits a new
protected CI run.

At `05a76506`, all six PR workflows passed, including CI Standard's Python,
full-site E2E, and quality-gate jobs. Main `81ef6e0d` was merged locally at
`44e59bcf`; the sole development-log conflict retains both main's new shipped
entries and the publication reconciliation's three shipped entries. The
post-merge canonical pre-PR, seven search-index tests, search-index generator
check, claim-audit check, all 13 article evidence digests, and nine frozen
asset hashes pass. The development-log checker exits zero with an existing
portfolio WIP-cap warning. The merged head still awaits protected CI, review,
and live publication verification; see the exact receipts in
`reports/shot-pattern-publication/followup-validation.json`.
The separate predeployment receipt confirms the frozen 39-page desktop PDF and
all nine local asset hashes. At that checkpoint the live manifest contained
253 pages without this article, and the four target routes returned 404.

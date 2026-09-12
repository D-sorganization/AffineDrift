# Agent Handoff — AffineDrift

## Cross-Article Linking Gate: #3898 / #3899

- PR #4302 (branch `bot/3898-3899-link-gate`) adds `config/categories.yml`
  (15-category controlled vocabulary) applied as canonical YAML block-list
  `categories:` front matter to every rendered content page (195 pages; book
  chapters exempt), plus the C3 site gate in
  `src/tools/site_link_gate.py` + `src/tools/site_page_scan.py` wired as
  `scripts/link-checker.py --site-gate` and a CI step in
  `.github/workflows/link-checker.yml`.
- The gate is green on main state: 0 broken links, 0 path-style violations,
  0 orphans, 0 unknown categories. Fixes shipped along the way: generated
  critique-annotation routes made parent-relative
  (scripts/generate_claim_critique_ledger.py), monograph chapter
  `data/<experiment>/figures/` paths corrected to `figures/`,
  companion-chapter workbench links, and ~50 stale `.qmd`/root-absolute
  links normalized.
- Pre-existing Related-Article gaps (106 pages) are enumerated in
  `tests/link_gate_baseline.json`; shrink it when #3900/#3901/#3905 land.
- Still open from the 34-issue wave-2 backlog: #3898/#3899 close via PR
  #4302; #3900/#3901 implementable next (lease claim:claude active);
  #3905 (book bridges), #4025-#4029 (COMP-B), #4031/#4032 (C10/C11),
  TRUST-AUDIT #4054-#4061 + #4021 depend on provider evidence or large
  editorial sweeps; #4299 held by codex lease until 2026-09-09T01:19Z;
  #4253/#4255 remain evidence-gated (Tools #5068, UpstreamDrift #9700).

## Rate-of-Closure Release Cross-Link

- Branch `bot/roc-release-article-update`: `articles/green-simulation.qmd` §4
  gains an "Interactive web companion" bullet linking the live
  rate-of-closure-explorer putting tab and its "Import green…" heightfield
  import (ADR-0045 F2 web behavior), completing the article-side item of
  D-sorganization/public-web-management#2. `scripts/link-checker.py --root .
--internal-only` passes ("All links valid!"). No other articles touched
  (trajectory record import is desktop Qt, not live web — not written into
  any web-facing article).

## Impact Dynamics and Acoustics: #4253

- Theory #4258/#4282/#4298 and force-regularity #4356 are merged; #4356 is
  963867d7c78e544799ef4b6070eb1779e64c0452, with all 15 protected checks passed.
- Current turnover-only branch docs/4255-impact-handoff, checkpoint SELF.
  Canonical docs/development/HANDOFF.md contains source/CI identities and resume steps.
- Tools contact, load-history, FRF and calibration foundations are merged.
  Friction #5162 still needs final integration and exact-head hosted qualification
  at this checkpoint; consult its live PR before advancing a consumer pin.
- All program parents remain open for event-work, physical, calibrated radiation
  and blinded-perception evidence. Preserve protected sources and peer scopes.

## Build-Section Lateral Links: #3902

- Branch `claude/issue-3902-models-lateral` (base `1ce02d7`) adds the canonical
  markdown `## Related Articles` component to all 8 `models/*.qmd` and all 6
  `repositories/*.qmd` pages, plus `pages/tools.qmd` and
  `articles/upstreamdrift-educational-integration.qmd`, `articles/rotation-converter.qmd`
  and `articles/proximal-distal-model-workbench.qmd` — 177 new relative markdown
  content links, every model↔repository pair bidirectional, every target verified to
  exist in the worktree.
- `articles/technology-heavy-hit-impact-coupling.qmd` is intentionally untouched:
  PR #4267 (issue #3903, sibling branch) adds the model-interchange links on that
  branch; do not duplicate them here.

## Technical Content Review

- **Current null-space continuation:** #4371 under epic4009/corpus4021/core4058; worktree `C:/Users/diete/Repositories/AffineDrift-technical-review`, branch `fix/4371-nullspace-rigor`, checkpoint SELF, regular PR4373 OPEN: https://github.com/D-sorganization/AffineDrift/pull/4373. Implementation `7253d6671b0b7f69d36178578664a1478e66b0ce` is committed and pushed; all normal commit/push hooks passed. Base integrates main at `5a576fc612541a3ab0c72c0f2f7441fcd95d1e7c`. Full article and bibliography rewrite, five-source BibTeX, numerical builder, durable example JSON and16 independent tests are saved. The oversized earlier write failed to reach disk; fresh inspection established this and the rewrite was recovered in bounded chunks. Audit: `docs/development/technical-review/nullspace-review.md`. DL-#4371 is in_progress; full corpus remains unfinished.
- **Null-space completed local review:** all 29 latest article reading captures and all six bibliography captures in each theme are read. Mobile equations, both expanded explanations and full table contents across horizontal scroll positions were inspected. Actual production-route gate48906 passed all 28 cases, each independently checked: HTTP200/no failures/overflow/retries; axe scanned one configuration per route, with no serious/critical findings. Final bibliography table keyboard checks pass after correcting a QA-only attempt to click the offscreen theme toggle. Browser nullspace-final closed. Durable reports: reports/technical-review/nullspace-complete-review.md and nullspace-render-verification.json. All seven source/example paths match committed implementation 1cfa47d45ebd14c719c0ec981e83eb53a231fb4d byte-for-byte. Next: bind the two route reviews to the actual commit containing these reports, adjust the audit partition and run its gates. Shared TOC4370 and keyboard4374 remain explicitly open; the two short article callouts stay expanded.
- **Publication omission discovered after local review:** the bibliography URL returns live HTTP404 and its Markdown source was absent from \_quarto.yml. SELF renames the byte-identical companion from .md to .qmd so the existing production rules select it. A regression first failed for the absent Markdown render target and now verifies actual production selection. The attempted \_quarto.yml edit was restored after the hook correctly identified its bound audit evidence; those earlier records remain unchanged. The selected local preview did not prove default-build inclusion. The review reports remain valid as local evidence, but the bibliography needs a new public route inventory entry and full hosted build/publication checks. Do not add all article Markdown indiscriminately. The existing article route and new companion route must be distinguished when reconciling the historical audit partition.
- **Null-space checkpoint gates:** latest root5334 passed/29 skipped/132 deselected/59 warnings in193.45s, coverage79.29% (nullspace-readable-root.log); earlier Ruff/Black709/configured mypy91/direct builder mypy1/content lint pass. Static CI at a8bd721056f29b236872f025e3d45a6c7d882e94 failed only two unnamed gravity literals; SELF names the independently specified test constant. Focused16 checks/Ruff/Black pass and the actual static checker reports zero findings across735 tracked Python files. Unfiltered local static scanning includes175 unrelated scratch findings; it is not a passing full-tree result. Render94019 and browser56238 completed exit0; browser closed and no validation jobs remain live. Six generated outputs were restored after semantic comparison.
- **Muscle PR4372 published:** all exact-head hosted checks succeeded at b862099ac3b1afc58eadbbd08d4f4e5b1060b9e9; protected squash3f87332512858febf2c131fbda44b62acad8d222 at22:13:28Z September12 is integrated at5a576fc6. Exact deployment34722147597 completed successfully. Live artifact10306629143 was inspected record by record:956 unique viewport/theme records across239 routes, all HTTP200/pass without inspection failures, overflow or retries. All four Chapter16 cases pass. Axe ran on one configuration per route (239 scans), with zero serious/critical violations. DL-#4369 is shipped; older OPEN/next-check wording below is historical. Preserve the complete local review and open TOC issue4370.
- **Current coordination and preservation:** nullspace session `technical-review-20260912-nullspace`, own4371 lease5648917433 expires23:49Z; presence renewed with durable report and inventory paths. Startup inbox has no conflicts/messages; unrelated identity-change warning is not vacancy proof. Stage explicit nullspace/doc paths only; thousands of untracked scratch artifacts remain. Never mutate git while test/render/browser QA handles are live. Preserve all peer work and protected authority.

- **Active chapter review:** #4369 under #4009/#4021; worktree `C:/Users/diete/Repositories/AffineDrift-technical-review`, branch `fix/4369-muscle-torque-rigor`, checkpoint SELF, regular PR #4372 OPEN: https://github.com/D-sorganization/AffineDrift/pull/4372. Reviewed implementation/report commit `447634a4cc0bbc01b5172766f920ba64f45079b5` is pushed and every bound file was independently compared with that commit. Paired scientific rewrite655b6514 and contact/figure refinementbd42b1ab are pushed. Current checkpoint completes local rendered review and adds durable reports under `reports/technical-review/muscle-torque-*`. All eleven worked answers and nine independent mechanics checks are retained. Whole-corpus work remains unfinished.
- **Completed visual review:** all29 final web captures, all15 chapter PDF pages179-193 (printed149-163), and four new bibliography entries on530-533 read. The536-page book has resolved citations and no changed-chapter overfull boxes. Other book pages are not certified. An ineffective clubpenalty attempt was replaced with an explicit exercise-box break before question4; pages191-193 reread. Recipe and failed attempts remain in `muscle-torque-review.md`.
- **Local gates:** delivery root5318 passed/29 skipped/132 deselected in306.11s, coverage79.35% (`muscle-torque-delivery-root.log`); session88383 reaped exit0. Ruff, Black100 (706 files), configured mypy91 and title636 pass. Browser QA:170 expressions,16 displays,14 width/theme cases,68 regions,24 keyboard scrolls. Production route gate47646 reaped exit0; all14 records individually inspected, HTTP200/no failures/overflow/retries. Existing moderate landmark-unique remains. Browser `muscle-torque-nav` closed; idle preview8767 remains.
- **Navigation defect:** fresh settled browser reproduces incorrect TOC active-section highlighting. Tracker compares document scroll with offsets relative to positioned section parents. Native subissue #4370 under #4009 records reproduction and acceptance; do not claim navigation is fully correct or edit generated Quarto JS directly. Scientific review evidence explicitly preserves this limitation.
- **Boundary repair:** bound-root run96214 failed only deployment-pruning evidence survival (5317 passed). Figure builder moved from disposable docs output to `scripts/build_muscle_torque_figures.py`; exact SVG drawing bytes reproduce after ignoring date metadata. Correct Axes typing passes direct mypy. All51 boundary/inventory/mechanics/figure tests pass. Source relocation is committed at `a2d482bff6252be13cbced65cddb3b3f353027ac`; all nine evidence paths were checked against that git commit and the inventory now binds it. Rebuilt PDF figure pixels are identical at1500x780. Final repaired root5318 passed/29 skipped/132 deselected/59 warnings in187.39s, coverage79.21%; session78917 reaped exit0. All local validation handles are closed.
- **Next chapter delivery action:** review exact-head hosted checks for regular PR4372, resolve any failures, then protected merge and live-publication verification. SPEC4372 is added in this checkpoint; tested binding50904c89 is already pushed. No draft PRs. Inventory now reviews this route with four corrected scientific findings and one open TOC finding; 50 combined inventory/mechanics/figure checks pass after the partition check first failed at198 versus197 deferred routes.
- **Coordination:** session `technical-review-20260912-muscle`; own4369 lease receipt5648758448 expires23:19Z September12. Presencebc5c808d-b11e-445a-ad4d-ed4e0b0fd457 receipt5648866245 expires23:39Z, includes the relocated script, two durable reports, inventory and inventory test. Startup inbox has no conflicts/messages; unrelated rejected identity-change warning is not vacancy proof. Stage explicit canonical files only; thousands of scratch files remain untracked.
- **Strokes PR4368 published:** protected squash93bbfd29d3e69147dedef153749a47a1b650dfe9 at20:36:25Z September12. Exact deployment34717587828 succeeded. Live artifact10305443224 independently inspected: all956 unique records/239 routes pass with HTTP200, no record/inspection failures, overflow, retries or axe violations. Both strokes article and critique have all four viewport/theme records. DL-#4358 may now be shipped; governed critique remains open. Current muscle branch integrates the squash at84640cab; preserve the numerical repair713a4ca5 and its bound evidence.

- **Published strokes continuation:** #4358 under #4009/#4021/#4059, DL-#4358. Worktree `C:/Users/diete/Repositories/AffineDrift-technical-review`; branch `fix/4358-strokes-delivery`; base `59b4b84790d22e45d26e222a86d5ae260954b836`; this checkpoint SELF. Regular follow-up PR #4368 is merged: https://github.com/D-sorganization/AffineDrift/pull/4368. PR #4360 was made regular and merged as `e19e3ff17fd6340ae05c9362fea7c7049d4bf089` before the recorded rendered review/inventory work was complete. The full corpus remains unfinished. **Never create draft PRs**, per user instruction.
- **Scientific continuation:** added joint immediate-cost/distribution/continuation decomposition with attribution-order dependence, .025 interaction example, conditional Jensen coupling condition, and finite-mixture derivative assumptions. The full original and revised article, bibliography companion and linked critique have been read. Independent numerical suite now has 17 passing tests. The prior rewrite's exact accounting, penalties, category cancellation, policy evaluation, player heterogeneity, causal identification and mechanics-to-score limits remain intact. No empirical golfer dataset fitted; no textbook PDF changed.
- **Presentation defects corrected:** scoped `css/strokes-gained.css` fixes dark references, expanded panel clipping under semantic headings, and pale text on white cards in dark mode. Two equation-only table headers now have text. Initial aria-expanded checks missed zero-height panels; strengthened browser checks require actual visible height. Full source render succeeds. Production HTML polyfill normalization was applied through `strip_legacy_math_polyfill` only; never invoke the root pruning function.
- **Prior strokes presentation checks:** root 5,297 pass/29 skip/132 deselected/59 warnings, coverage 79.35%; numerical builder 100% statement coverage; focused numerical/source-mapping/inventory/pruning suite 57 pass. Earlier Playwright root-hygiene failures were resolved by closing the browser and relocating its output. Ruff and Black100 (705 files), exact CI mypy (91 files), stricter changed-module mypy (2 files), content lint 131 pass/4 skip, titles 636 pass, and CSS budget pass. Production-style actual-route gate passes all 28 cases for article and critique, no console/inspection/axe failures or retries. Current article/critique/CSS hashes match the stored review. All 154 article expressions, 37 old IDs, 126 regions and 64 keyboard scrolls were verified; critique has four expressions and five read captures. Failure history and exact source boundaries remain in `docs/development/technical-review/strokes-gained-review.md`.
- **Next action:** bind Chapter16 durable review evidence to its committed implementation and create a regular PR. Strokes deployment at93bbfd29 is independently verified above. Leave governed critique `crit-strokes-gained-non-ergodic` open; the corpus remains unfinished.
- **Evidence paths and validator:** numerical builder now `scripts/build_strokes_gained_examples.py`; numerical JSON and browser summary are under `reports/technical-review/`, outside generated docs output. Source resolver now permits an existing same-route .md only when .qmd is absent, matching publication precedence; three regression cases cover acceptance, precedence and unrelated-path rejection. The audit partition accounts for both completed strokes routes. Governed critique remains open. Both routes pass final inventory validation. Bind the complete implementation SHA after this checkpoint; this is local review, not a live-publication attestation.
- **Forces #4355 / PR #4357 merged:** squash `0c753400190cf330533bffc12e9b035162f37749`, exact deployment34477888759 succeeded. Artifact10153444359 independently inspected: all956 records/239 routes HTTP200/pass, no record/inspection failures, retries or axe violations. Complete audit remains `forces-torques-review.md`; full original/revised paired reading, all12 PDF chapter pages and full web captures previously verified. Root5254/coverage79.29%, focused35, content131, static34, titles636, mypy91; prior shared moderate landmark-unique and console noise were recorded honestly.
- **Double #4353 / PR #4354:** squash `e9ad402e50f111589252292178e5f45ac58b427c`. Its exact deployment34473831404 was cancelled before publication when superseded; never call that run successful. The later forces deployment above includes four passing Chapter3 route records. GitHub comparison proves e9ad402e is an ancestor of published0c753400 and both Chapter3 canonical sources are unchanged; descendant publication is verified, not the cancelled exact run. Full audit `double-pendulum-review.md` retained.
- **Previously shipped:** constraint #4351/PR4352 at b5362af0005c8ae1ad00e81390e9151991157155 (deploy34470677053, artifact10150223079, all956/239 verified); affine #4349/PR4350 at60d0298826880ca24580908127e8032565407216 (deploy34466267456, artifact10148726944); brain #4347/PR4348 at688dda81c3f0c38759d9994cbc0d5c0cd0478bd2; triple #4345/PR4346 at8808f68ab8b7e39c5110ce260473d02dbff63c45. Their complete audits are retained. Fascia4341, deploy repair4342 and bound DCR4338 remain shipped.
- **Strokes coordination:** session `technical-review-20260912`, renewed claim receipt5648476087 expires22:24Z September12; presence b174514d-5903-4cb2-bda1-c56e47118e0a expires21:25Z. The previous claim query correctly identified our own open PR4368. Latest inbox has no conflicts/messages; unrelated rejected identity-change warning remains and is not vacancy proof.
- **Preserve:** original checkout, immutable `articles/proximal_distal_energy_transfer/`, publication/authority pins, bound DCR audit, peer impact/acoustics #4253/#4255 and Chapter29, and all peer handoff/DL sections. Thousands of local untracked research/QA files exist; stage explicit canonical files only. Test-generated registry/summary drift must be inspected and restored only when proven unrelated. Idle preview port8767 may remain; verify it before reuse. Source PDFs are local scratch, not redistributable deliverables.
- **Next long article #4371:** complete original `articles/null-space-constraint-jacobian.qmd` read, including explanations, critiques and appendices. Issue records ten finding groups: nonintegrable speed frames, DAE index, missing constraint curvature and task acceleration, false instantaneous-rank controllability necessity, inconsistent golf coordinates/grasp Jacobian, basis-dependent synergies and unsupported coaching. Independent two-mass spring model K=[[2,-1],[-1,2]], M=I, input[1,0] has state controllability rank4 despite acceleration input rank1. No source edits or full primary-source review yet; claim the issue before implementation. Primary-source lead: https://underactuated.mit.edu/multibody.html, generalized-speed and bilateral-position passages read (lines32-54 in the September12 retrieval); independently audit its dual-sign/transpose conventions before reuse. The Caltech author site says the MLS book PDF is no longer publicly distributed; do not claim that book was read.
- **Remaining corpus:** muscle-to-joint torques (~5283 original words; full print source read, web read fully; sign/transpose, feasibility, anatomy, inverse-estimation and unsupported coaching issues identified, complete paired rewrite and initial render checks, final visual review pending; issue4369 claimed), nullspace (~5174), curiosity (~5123), many indexed/partial entries, and five read DCR critiques #4340. Review index is not proof of full review. Central DL checker reports peer DL1595/3903/3902 metadata gaps; preserve those entries. This checkpoint updates DL4369 and DL4358 and the corpus index; the overall goal is deliberately still active.

## Protected Authority

- Website PR #4092 protected-squash-merged as
  `c1963cf038dcc5cf8dacb583aed9e35fe176fc41`, on top of the #4091 visual
  authority at `af49c1f15f2771397ecf0e67eb53dd92646ac0b1`, #4090 reader
  authority at `1c0c04c5c115afe34f65e416f3007d9c525f0e80` and #4083 discovery
  authority at `75042154b05c2a04351b0d47e6ed44c994243476`. #4092's exact-head
  protected checks passed. The prior #4091 deployment run 33303380671 passed,
  including its revision-matched live every-route gate.
- Deployment run 33306144800 succeeded for the exact #4092 merge, including
  the full build, every-page predeployment verification, Pages publication,
  revision-matched live-route verification, and uploaded live evidence.
- Programming-companion PR #4093 protected-squash-merged as
  `17b5f15d362eb0225053d4e51ed86863d305074c`; all exact-head CI, benchmark,
  link, SPEC, routing, and governance checks passed, and issue #4022 is closed.
- Handoff-only PR #4094 protected-squash-merged as
  `bcc25fa43a1f741e8565a2037476deed9f45cd69`; deployment run 33308185575
  passed through revision-matched live every-page verification. It changed no
  runtime or scientific publication authority.
- Post-atlas handoff PR #4096 protected-squash-merged as
  `b5df6d5cd7a1b81c0771c6f7378c37f7378c6618` after every protected check
  passed. It changed only this handoff and the specification; it introduced no
  runtime, scientific-authority, or immutable-monograph byte changes.
- Proximal-distal atlas PR #4095 protected-squash-merged as
  `ea14c92e5bdbb544b75dc254be0f68b3ec1310b8`; all exact-head required checks
  passed and issue #4087 is closed. Deployment run 33311698720 passed the
  complete build, Pages publication, and revision-matched live every-route
  verification for that exact merge.
- Programming Companion PR #4099 protected-squash-merged as
  `717461e42e2de9f257cfa873ed336795dcc2d321`; issue #4098 is closed and every
  exact-head CI, content-lint, link, benchmark, governance, Quarto, and browser
  check passed. Deployment run 33317188855 passed the complete build, Pages
  publication, and revision-matched live every-route verification for that
  exact merge.
- Handoff-only PR #4101 protected-squash-merged as
  `8edfc9117d7c52d829f61540d455f6b4bbd31d42`. Its deployment run 33318598234
  reproducibly found one failed item among 928 browser inspections: the
  bibliography metrics widget skipped from H2 to H4 on desktop/light. Evidence
  artifact `public-site-verification-8edfc911...` identifies the exact route and
  assertion.
- Bibliography accessibility PR #4103 protected-squash-merged as
  `d8775589e4ac5270816e60330b338354a78047db`; issue #4102 is closed. All
  exact-head checks passed, including the complete Python lane, JavaScript,
  content lint, links, E2E, visual invariants, benchmarks, and governance. The
  exact source diff is four retained files, +49/-8, with zero deleted paths and
  zero immutable-monograph diff.
- Verifier reliability PR #4107 protected-squash-merged as
  `6350a5d4fdd59ccc68e1b8562d8f8c2b20d3e262`; issue #4104 is tracked.
  Deployment run 33324477245 passed the complete build, all 928 pre-deployment
  browser inspections, Pages publication, and all 928 revision-matched live
  inspections with 100% green status and uploaded live evidence.
- Provider-consumer compatibility PR #4109 protected-squash-merged as
  `de1f5a7ed6d68b9fefaa4e1975e5fb25d259c782`; issue #4030 is closed.
  All exact-head CI, benchmark, link, SPEC, and browser checks passed.
  The companion schema pins UpstreamDrift protected `main` `6ff956a4d`
  and includes comprehensive schema version matrix fixtures in `tests/fixtures/companion/`.
- Programming companion catalog generator PR #4112 protected-squash-merged as
  `2eb6e9a7e651522db9ff81fffe1a6beaa53a79d0`; issue #4023 is closed.
  Implements `src/affine_control/programming_companion/catalog_generator.py` and `scripts/generate_programming_catalog.py`, generating authoritative Quarto indexes and detail pages for Engines, Programs, Features, Workflows, and Provenance (`models/programming/*.qmd`) from pinned provider facts, with comprehensive TDD test suite in `tests/test_programming_companion_catalog_generator.py`.
- Onboarding & Installation guidance (Issue #4024): Replaced stale installation and verification guidance across documentation with verified UpstreamDrift CI entrypoints and companion workflows (`scripts/ci/verify_installation.py`, `python -m scripts.companion_workflows execute --workflow-id installation-verification`), cross-linked to `/models/programming/engines.html`, and added regression tests in `tests/test_programming_companion_onboarding_contract.py`.
- Corrective retry PR #4108 (`fix/4104-live-evidence-v2`) restricts retries to live evidence only, tracks attempts, and extracts navigation policy.
- The primary checkout is clean
  on `main`. Reverify exact equality before starting new work. #4112 is the latest Programming Companion presentation
  authority; #4093 merge
  `17b5f15d362eb0225053d4e51ed86863d305074c` remains the immutable provider
  consumer authority, #4095 remains the falsification-atlas authority, and
  #4030 remains the provider-consumer compatibility authority.
- Numerous older local worktrees remain. Their presence is not evidence that an
  issue or pull request is active. Verify GitHub state and exact ancestry before
  resuming any of them.

## Merge Governance

- Use full pull requests and ordinary protected merges; never bypass checks,
  reviews, or branch protection.
- The live ruleset requires zero approving reviews. Human review remains
  optional for risk or expertise, not a standing release gate.
- Regenerate controlled outputs from canonical source, run exact-head gates,
  and verify the protected merge plus post-merge deployment before claiming
  publication.
- PR #4271 (series navigation sidebars, tangent-space cluster, issue #3904)
  branch repair 2026-09-08: regenerated stale trust-surface/claim-audit
  digests (`python -m scripts.regenerate_claim_audit_evidence`), replaced the
  raw `::: {.callout-note}` fenced div in `articles/affine-nature-golf-swing.qmd`
  that fails `test_target_pages_do_not_use_raw_fenced_div_markers`, and added
  the #4271 SPEC.md change-log row. Focused suites
  (textbook quality, trust surface, claim audit, series navigation) pass locally.

## Website and Companion Program

- Issue #4080 / PR #4083 is protected, deployed, and closed. The final reviewed
  PR head was `b544dc8ceea985eac5f3ca32d674f5e6b8aa125a`; its diff was 24 files,
  +841/-175, with zero deleted paths.
- The governed proximal-to-distal monograph is now a peer of the two rendered
  textbook collections in Read navigation, the homepage, and the full-width
  Books hub. It is also present in the article catalog, search contract,
  biomechanics and golf-science learning paths, Models, and Software. The
  companion/workbench use local governed evidence and exact protected pins.
- Live desktop inspection at 1440 px shows three equal 386 px long-form cards;
  390 px collapses to one column. Both have one visible H1, no horizontal
  overflow, and no fresh-console errors.
- Exact #4095 publication evidence: 231 Quarto inputs rendered; site health found
  zero broken links and 24 known legacy orphans; pruning removed 30 internal
  artifacts; the manifest contains 232 public routes; claim-audit generation
  and enforcement pass; browser verification passes 924/924 mobile/desktop,
  light/dark cells. Jest passes 307 with 19 documented skips. The complete
  Python suite and hosted full-test lane pass, and the projection verifier reports 207
  source-identical, 21 flattened, zero immutable-link rewrites, and 36 declared
  adaptations.
- The immutable monograph source, chapter, figure, PDF, and source-manifest tree
  has zero diff. The render preview was removed after validation and is fully
  reproducible from source. Root and nested review renders were sent to the
  Windows Recycle Bin after their absolute paths were verified inside the
  worktree.
- `reports/website-companion-review-2026-08-29.md` records the content gaps and
  Packages A–E. Package A is delivered. Epic #4008, programming subepic #4010,
  and reader-evidence subepic #4084 own the remaining work. #4085–#4089 cover
  baseline reconciliation, shared evidence semantics, the proximal-distal
  falsification atlas, reader validation, and whole-site desktop regression.
- The writing-quality batches protected in merged PR #3831 at
  `915309d51ec43a475efcce32ad3ecb98cc8e207c` are reconciled: child trackers
  #3823-#3828 closed on 2026-08-30 with batch completion recorded and unproven
  aggregate metrics left unchecked. HTML-2 and author-decision residue remain
  open in #3821/#3830.
- #4089's governed visual foundation is protected in PR #4091. The final
  reviewed head was `b74160d9e3c0f955c0f1a4befdd333255188edf1`; its source diff was 21
  files, +1,346/-60, with zero deleted paths. The protected squash is
  `af49c1f15f2771397ecf0e67eb53dd92646ac0b1` and its deployment is green.
- The supplemental #4089 slice is protected through PR #4092. It adds 18 cells for the
  global footer, dense-content containment, keyboard focus, reduced motion,
  print, and no-JavaScript behavior, bringing local evidence to 158/158. Keep
  #4089 open until a human reviews and approves an exact candidate baseline.
- The new representative contract is ten route families by seven viewports
  (390, 768, 1024, 1200, 1280, 1366, and 1920 px) by two themes: 140 cells. It includes a
  real `proximal distal` search interaction while preserving the separate
  924-cell every-route structural verifier. The first full run failed 10 cells:
  five route families in both themes overflowed at 1024 px because Quarto
  exposed the margin TOC too early. Adversarial review then measured a second
  21 px monograph overflow at the former 1200 px rail-entry boundary. Exact
  1200 and 1280 px probes plus a canonical 1279.98 px hide threshold govern the
  corrected transition. The protected Linux evidence passes 140/140.
- Screenshot evidence binds route family, scenario, source revision, renderer,
  decoded PNG dimensions, byte count, and SHA-256. The runner emits a candidate
  baseline only. Comparison validates the complete baseline schema and fails
  closed on missing or malformed reviewer/timestamp/pull-request metadata,
  count mismatch, non-derived or duplicate keys, or renderer mismatch. A
  protected follow-up must still approve a candidate. The supplemental runner
  now exercises footer, bounded dense content, keyboard focus, reduced motion,
  print, and no-JavaScript behavior. Browser review found and corrected
  character-by-character mobile table wrapping plus print-title suppression,
  dark title colors, and raw citation URL expansion. The complete local matrix
  passes 158/158; candidate approval remains deliberately human-gated.
  Exact Linux artifact review also caught a bright mobile footer in dark mode;
  a color-surface assertion and token-driven footer styling now guard that
  theme boundary.
- The PR E2E job renders every representative source, generates the bounded
  current flattened CSS bundle, generates the bounded public manifest, runs all
  140 cells, and uploads screenshots, results, and the candidate baseline as
  `public-site-visual-evidence-<SHA>`. The explicit bundle step prevents partial
  Quarto renders from testing a stale tracked stylesheet. Deployment keeps the
  same candidate capture in addition to its complete live-route gate.
- `scripts/e2e_relevant_paths.py` is the single change-detector authority for
  that lane. It covers every tracked CSS/SCSS path (including article-local
  proximal-distal and monograph stylesheets), visual runner/evidence/manifest
  scripts, screenshot schemas, the public report source, and both visual
  workflows; executable unit contracts prevent silent trigger erosion.
- Programming work reuses #4022–#4030 and provider UpstreamDrift #9174 rather
  than creating another catalog. Protected UpstreamDrift main is
  `f98bf7b382083322c609bfd7d680e4e82d71aed8`; provider workflow PR #9307 is
  open at head `6614f7ad8eafedde8a4f3162470850921d20e195` with that exact base. Its
  substantive checks, including `companion-workflows` and the optional stack,
  passed; `check-and-trigger` remains queued, while GitHub reports the PR as
  conflicting even though local Git proves protected main is a parent of the
  merge head. Requery before acting and never force-push; if GitHub does not
  reconcile, create a fresh replacement branch from current protected main.
  #9174 and #9190–#9193 remain incomplete and exact-main has no
  `dist/companion/` publication tree. No provider artifact is accepted for
  AffineDrift import; only provider-independent RED/security fixtures are safe
  before those gates close.
- Issue #4098 is closed through protected PR #4099 at merge
  `717461e42e2de9f257cfa873ed336795dcc2d321` and deployment run 33317188855.
  Retired branch/worktree checkpoints are not current publication authority.
- The stable `/models/models.html` route now removes copied provider versions,
  counts, launcher/install commands, support tiers, repository structure, and
  mutable branch links. It features the technical monograph, visual companion,
  falsification atlas, workbench, Books hub, and two learning paths. Catalog,
  onboarding, workflow, screenshot, and compatibility cards fail closed behind
  UpstreamDrift #9174/#9190–#9193 and AffineDrift #4023–#4030. The seven legacy
  engine guides remain explicitly deferred under #4060.
- Browser review at 1440 px measured a centered 1,200 px content canvas and
  three 386 px peer long-form cards; at 390 px the cards collapse to 341 px,
  with one visible H1 and no horizontal overflow. The retired three-rail shell
  had squeezed primary desktop content to 691 px. Post-deployment inspection at
  1280 px measured a 1,265 px body/canvas inside the 1,280 px viewport; at
  390 px it measured 375 px, with one visible H1 and no page overflow in both
  cases. Human visual approval for the separate #4089 governed baseline remains
  open.
- #4098 local and protected verification render all 231 canonical Quarto
  inputs and produce a 232-route public manifest; internal links, title case,
  claim-audit generation/enforcement, book/site-trust audits, and the immutable
  projection verifier pass. The maintained Python suite passes 3,609 tests with
  29 dependency/platform skips and 117 configured deselections; Jest passes 307
  with 19 documented skips; Ruff, Black, strict `src/affine_control` mypy, and
  Stylelint pass. Direct light/dark browser review reports no console errors.
- The provider-independent #4022 consumer foundation is protected on `main`
  through PR #4093 at merge `17b5f15d362eb0225053d4e51ed86863d305074c`.
  It pins the exact protected provider schema from UpstreamDrift
  `1af18489e8755933a0d189aa8edafe787fa94d0f`
  (`d0d0389...` SHA-256) with an adjacent provenance record. The typed package
  enforces exact-commit allowlists, bounded no-redirect acquisition, strict
  schema/provider/commit/path validation, content-addressed snapshots, canonical
  active locks, rollback, tamper detection, read-only update comparison, and
  explicit active-lock-digest replacement. Thirty manufactured contracts pass.
  There is deliberately no production lock or snapshot.
- #4087 is protected and closed through PR #4095 at merge
  `ea14c92e5bdbb544b75dc254be0f68b3ec1310b8`. The final PR is 23 files,
  +1,303/-37, with zero deleted paths. The
  dependency-safe foundation uses a strict editorial schema and typed
  deterministic generator to join six required themes to pinned claim,
  critique, readiness, validation-release, source-manifest, and provider
  authorities. Scientific wording and state are authority-derived; exact
  provider workflows and validation releases remain visibly unavailable. The
  public static atlas has desktop/mobile/no-overflow and clean-console browser
  evidence, plus print/no-JavaScript semantics. The immutable monograph source
  tree remains byte-identical; discovery is provided through catalog and
  sidebar surfaces rather than by mutating the governed projection.
- UpstreamDrift PR #9267 remains a separate blocked scientific-authority lane at
  observed head `7215e0e285bd21f7f1631681e51226bbf746d610`. It cannot authorize a
  refreshed proximal-distal projection until its exact artifact, manifests,
  protected checks, and merge are complete.

## Content-Loss Audit

- Protected PR #4103 changed four retained source/governance files by +49/-8,
  with zero deleted paths and no immutable proximal-distal publication change.
  Its full render briefly produced +422/-3,154 across generated `docs/` assets;
  restoring tracked generated output and removing only dry-run-enumerated
  untracked render products returned the intended diff to four files.
- Protected handoff PR #4101 changed two retained governance files by
  +47/-30, with zero deleted paths and no public-site source change.
- Protected PR #4099 is 10 retained files, +402/-475, with zero
  deleted paths. The 475 removals replace a 511-line copy-maintained hub
  and small obsolete test expectations; no article, book, monograph, provider
  snapshot, program source, or scientific evidence path is deleted.
- The #4098 full render reproduced transient generated-site churn at 72 tracked
  `docs/` paths, +785/-12,057, including 67 apparent deletions and 31 untracked
  render entries. Restoring only tracked `docs/` bytes from Git returned the
  generated tree to zero tracked diff while all canonical source and audit
  changes remained. This is additional direct evidence that large UI deletion
  totals during Quarto rendering are not committed source loss.
- The final #4095 pull request is 23 files, +1,303/-37, with zero deleted
  paths. Its 37 removals are retained-file edits in the handoff, SPEC,
  generated readiness table, claim-audit inventory/report, and research
  readiness generator; the immutable proximal-distal monograph tree has zero
  diff.
- The #4087 full render/prune reproduced the transient deletion alarm at 82
  tracked files, +618/-15,107. After the 232-route manifest and audit evidence
  were generated, restoring tracked `docs/` bytes and removing only dry-run-
  enumerated untracked render products returned the canonical diff to zero
  deleted paths. No source, monograph, book, or scientific evidence path was
  removed.
- #4093 is 15 files, +2,236/-20, with zero deleted paths. Its 20 removals are
  replacements in the retained handoff and specification; no scientific
  article, book, monograph, or generated-site path changed.
- No reviewed implementation range deletes a path. #4041 from `cec3842d` to
  protected `b28fd822` is 37 files, +6,356/-22, with zero deleted paths. The 22
  removals are edits in retained configuration, specification, handoff, audit,
  and sitemap files.
- The #4081/#4082 handoff compaction intentionally changes one retained file by
  +96/-1,239. It removes stale chronology, not scientific or implementation
  content; Git/GitHub remain the history authority.
- No Git range examined matches the Codex summary of 222 files,
  +12,882/-46,645. A normal in-progress Quarto render was directly reproduced
  at 81 tracked files, +22/-20,843 while generated HTML was still being moved.
  After completion and exact restoration, tracked source was clean. The large
  Codex tuple is therefore build/prune workspace churn, not a committed loss
  claim. Continue to verify exact Git ranges and manifests rather than trusting
  a transient UI aggregate.
- The #4089 full local render/prune reproduced the same effect: 75 tracked
  generated paths appeared as +853/-11,959 until `docs/` was restored exactly.
  The implementation commit itself is 10 files, +916/-14, with zero deleted
  paths. Canonical scientific and monograph sources are unchanged.
- The supplemental #4089 render/prune reproduced it again: 80 generated
  `docs/` paths appeared as +1,531/-12,060, including apparent deleted files.
  Restoring only tracked `docs/` bytes and removing only untracked generated
  preview files returned the source diff to zero deleted paths. This is direct
  evidence that the alarming deletion totals are transient generated-site
  churn, not loss of canonical content.

## Proximal–Distal Publication Boundary

- UpstreamDrift is the computational, claim, evidence, and campaign authority.
  AffineDrift is the immutable publication and explanatory layer.
- The current protected projection is AffineDrift #3992 / PR #3993. It pins the
  protected UpstreamDrift #9151/#9152 authority and the 252-page technical PDF.
- Canonical technical source:
  `articles/proximal_distal_energy_transfer/index.qmd`.
- Qualified local PDF:
  `articles/proximal_distal_energy_transfer/proximal_distal_energy_transfer.pdf`.
- `source_manifest.json` and
  `python scripts/verify_proximal_distal_projection.py` govern immutable source,
  figure, adaptation, claim-registry, and PDF identity.
- UpstreamDrift PRs #9305 and #9306 protected the event-aligned forward
  attribution kernel and distributed event-boundary adapter at protected main
  `f98bf7b382083322c609bfd7d680e4e82d71aed8`, but issue #9153 remains open.
  Do not refresh the AffineDrift projection until #9153's explicit remaining
  gates close, its release manifest is immutable, and all failure boundaries
  remain visible.
- Do not infer human technique, anatomy, physiology, or coaching effects from
  structural-model evidence.

## Research-Readiness Program

- #4041 is protected on current `main` through PR #4079. The public lifecycle
  library is simulation-ready only; it does not mint publication authority or
  measured-human validation.
- #4042 owns the external immutable release and claim-promotion adapter. Its
  clean local checkpoint is `730210d9e39730ac72c4bbc0ed77c61210411873` on
  branch checkpoint `AffineDrift-4042-e10`. Independent
  review returned GO as a truthful handoff checkpoint and NO-GO for merge: 531
  tests pass, 8 opposite-platform tests skip, and exactly 14 standard-lane
  publication/reproduction contracts still fail. Do not skip or deselect them,
  push a completion PR, or mark #4042 complete until those acceptance contracts
  are implemented and protected CI can pass.
- #4034–#4040 define falsifiability programs for the model ladder, bilateral
  wrenches, active impedance, neural timing, impact timing, participant-held-out
  generalization, and equipment response. Preserve unavailable and adverse
  evidence; never substitute manufactured fixtures for human data.
- #4021/#4063 govern route-level scientific claim audit and trust surfaces.
  Current protected main includes the #4075/#4077 deploy and heading repairs.

## Markerless Mocap Boundary

- AffineDrift #3954 is the immutable publication projection; Tools owns public
  contracts and UpstreamDrift owns orchestration and scientific computation.
- AffineDrift #3956 is the camera evidence registry. Candidate devices and
  manufactured fixtures are not procurement or validation authority.
- Never publish raw video, PII, secrets, private evidence, or AGPL runtime
  components. Public projection records must be revision-pinned and fail closed.

## Must-Read Files

1. `AGENTS.md` and `CLAUDE.md` — repository and publication policy.
2. `SPEC.md` — current scientific/publication contracts.
3. `articles/proximal_distal_energy_transfer/source_manifest.json` — immutable
   upstream projection boundary.
4. `reports/scientific-claim-audit.md` — governed route classification.
5. `scripts/verify_proximal_distal_projection.py` — projection verifier.
6. `reports/website-companion-review-2026-08-29.md` — argument gaps, feature
   choices, research augmentation, and implementation order.
7. Issue #4128 turnover comments — copy-ready next-agent prompt, exact current state,
   commands, stop conditions, and closure order (retired from `TURNOVER_PROMPT.md`).

## Validation

The corrective branch was validated on 2026-08-30 before turnover: the full
JavaScript suite passed 319 tests with 19 skips; the focused verifier suite
passed 22/22; the deployment/content lane passed with its one declared missing
LaTeX-release-workflow skip; and the complete headless Python lane had already
passed 3,658 tests with 26 skips. The only excluded collection module was
`tests/tools/test_wrist_universal_joint_window.py`, because this workstation's
PyQt6 QtGui native DLL could not import. That environment exclusion is not a
substitute for CI.

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD = "1"
$proximalTests = @(Get-ChildItem tests -File -Filter "test_proximal_distal_*.py" | ForEach-Object FullName)
python -m pytest $proximalTests -v
python -m pytest tests/test_markerless_mocap_projection_contract.py -v
python -m pytest tests/test_mocap_camera_registry_contract.py -v
python -m ruff check .
python -m black --check --line-length 100 .
python scripts/check_title_case.py
python -m scripts.book_publication_audit --check
python -m scripts.site_trust_surface_audit --check
quarto render --to html
python scripts/prune_internal_docs_from_deploy.py --docs-dir docs
$sourceRevision = (git rev-parse HEAD).Trim()
python scripts/public_site_manifest.py --docs-dir docs --source-root . --source-revision $sourceRevision --output docs/public-site-manifest.json
python -m scripts.generate_claim_audit_inventory --manifest docs/public-site-manifest.json --check --enforce-publication
$siteServer = Start-Process python -ArgumentList "-m", "http.server", "8000", "--directory", "docs" -WindowStyle Hidden -PassThru
try {
    node scripts/verify-public-site.js --base-url http://127.0.0.1:8000 --manifest docs/public-site-manifest.json --output artifacts/public-site-verification/local-every-page.json
    node scripts/verify-public-site-visual.js --base-url http://127.0.0.1:8000 --manifest docs/public-site-manifest.json --output artifacts/public-site-verification/local-representative.json --screenshot-dir artifacts/public-site-verification/screenshots --candidate-baseline artifacts/public-site-verification/candidate-baseline.json
} finally {
    Stop-Process -Id $siteServer.Id
}
```

For publication work, also render Quarto from canonical sources, run site
health/publication enforcement, and inspect responsive output in both themes.
Do not treat source tests alone as rendered-publication evidence.

## Ordered Next Actions

1. Complete the current-main corrective #4104 branch through an ordinary
   protected PR. Do not rerun deployment 33321616181. Require one new
   exact-revision 928/928 live artifact that contains the attempt counters, and
   close #4104 only after that artifact is inspected.
2. Requery UpstreamDrift PR #9307. Its substantive checks passed, but the bot
   trigger is queued and GitHub reports a conflict despite exact base ancestry.
   Do not force-push or merge while that discrepancy remains; use a fresh
   replacement branch from current protected main if GitHub does not reconcile.
3. Keep production companion installation fail-closed. Finish provider
   #9174/#9190–#9193 before installing any lock/snapshot or starting generated
   catalog #4023/#4024; then exercise #4030 against current and previous
   supported provider schema versions.
4. Obtain explicit human approval for the #4089 visual candidate before
   creating an approved baseline. Implement #4086 shared evidence semantics
   only when the provider-owned catalog and evidence authority are protected.
5. Preserve the protected #4087 atlas and immutable monograph source; never
   create a competing scientific registry. Add exact provider workflow links
   only after #9174 publishes qualified records.
6. Run #4088 baseline and follow-up reader validation under its privacy and
   preregistration gates. Keep #4042 and #9267 fail-closed until independently
   complete and protected.

## Do Not

- Do not duplicate computational engines or edit generated projection files.
- Do not use mutable upstream links as scientific authority.
- Do not revive a stale worktree without fetching and proving exact ancestry.
- Do not promote simulation-ready, manufactured, unavailable, or private
  evidence to validated or published status.
- Do not retry run 33321616181 or weaken the every-page verifier to obtain a
  green result; #4104 must retain both isolated-503 artifacts as adverse data.

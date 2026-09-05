# Agent Handoff — AffineDrift

Updated: 2026-09-05. Current-state only; use Git and GitHub for history.

## Technical Content Review

- User-directed review is governed by epic #4009. Full-corpus #4021 and route batches #4054–#4061 remain open; the 405-source inventory does not certify every claim. Preserve the immutable upstream monograph boundary.
- PR #4153 merged as `d5a55f229d190e0dda71d7c55f0d5e8f40518281`; deployment 33957446845 succeeded through revision-matched live verification. Seven concrete findings are closed, 59 files changed, and five publication PDFs regenerated. Final CI: 3,728 Python tests, 92.29% coverage, all eight textbook builds and other checks passed.
- PR #4159 merged as `fba9ad794d486ab60895d777c43bcb03dcaafaa6`; deployment 33959676165 succeeded through every live route. Its contraction/tangent reference now has correct metric/Riccati conditions, numerical certificates, biological scope, task dynamics, covariance, and hybrid-event sensitivity. Final CI: 3,736 Python tests, 29 skips, 92.29% coverage, all eight textbook builds and other checks passed. The historical critique still needs its own full audit.
- PR #4162 closed #4160 and merged as `32b774c438eb325c7cdb059d512e8ea3b54cdda0`; all final-head checks passed, including 3,745 Python tests, 92.29% source coverage, and eight textbook builds. Deployment 33964697060 succeeded through every revision-matched live route. Direct inspection confirms 180 math expressions, zero errors, and no mobile page overflow. It corrects the Physics loop chapter and two repeated spine-loop statements.
- PR #4163 closed #4161 and merged as `bbb163d48d21318658dfd6650a6e1bc454ebd461`; final CI passed 3,756 tests, 92.29% coverage, all eight textbook builds, and every other check. Deployment 33966729029 is pending. It rebuilds the full inverse-dynamics chapter and paired web edition, with a shared inference workflow, 11 numerical/regression checks, and targeted incoming-reference corrections. Local validation: 3,756 tests, 29 skips, 92.32% coverage; 128 content checks and 34 static contracts. The 580-page PDF and 13 revised chapter pages are inspected; HTML has 190 math expressions, zero math errors, and no page overflow at 1440/390 pixels. Full adjacent-chapter audits remain pending.
- Issue #4164 on `fix/physics-aerodynamic-drag` corrects the full aerodynamic chapter in both editions: air-relative forces, distributed moments, inverse signs, energy, input dependence, reproducible forward counterfactuals, ball flight, and environmental sensitivity. Validation: 3,767 tests, 29 skips, 92.32% coverage; 128 content checks and 34 static contracts. The 573-page PDF and all nine revised pages are inspected; HTML has 135 math expressions, zero math errors, and no page overflow at 1440/390 pixels. Adjacent chapters and the remaining corpus still need their own audits.
- Detailed findings, primary sources, scope, and validation live in `docs/development/technical-review/REVIEW.md` and `corpus-review-index.csv`. Temporary QA artifacts in that directory are not publication authority.

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

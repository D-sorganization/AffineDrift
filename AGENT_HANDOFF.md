# Agent Handoff — AffineDrift

Updated: 2026-08-30. Current-state only; use Git and GitHub for history.

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
- The primary checkout at `C:\Users\diete\Repositories\AffineDrift` is clean
  on `main` and equals `origin/main`. The latest substantive companion authority
  is #4093 merge `17b5f15d362eb0225053d4e51ed86863d305074c`; this handoff-only
  follow-up changes no runtime or publication behavior.
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
- Exact publication evidence: 230 Quarto inputs rendered; site health found
  zero broken links and 24 known legacy orphans; pruning removed 30 internal
  artifacts; the manifest contains 231 public routes; claim-audit generation
  and enforcement pass; browser verification passes 924/924 mobile/desktop,
  light/dark cells. Jest passes 297 with 19 documented skips. The final
  governed Python slice passes 60/60, and the projection verifier reports 207
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
  `727bda2de2d4656e8d9a3abbbc3a72b30fa06ebb`; it advances the previously
  audited `4cf39347...` only through vendor force-source frame pinning. #9174
  and #9190–#9193 remain open, and exact-main has no `dist/companion/`
  publication tree. No provider artifact is accepted for AffineDrift import;
  only provider-independent RED/security fixtures are safe before those gates
  close.
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
- UpstreamDrift PR #9267 remains a separate blocked scientific-authority lane at
  observed head `7215e0e285bd21f7f1631681e51226bbf746d610`. It cannot authorize a
  refreshed proximal-distal projection until its exact artifact, manifests,
  protected checks, and merge are complete.

## Content-Loss Audit

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
- UpstreamDrift #9153 is still an unprotected structural campaign. Do not edit
  or refresh the AffineDrift projection until #9153 is protected, its release
  manifest is immutable, and all failure boundaries remain visible.
- Do not infer human technique, anatomy, physiology, or coaching effects from
  structural-model evidence.

## Research-Readiness Program

- #4041 is protected on current `main` through PR #4079. The public lifecycle
  library is simulation-ready only; it does not mint publication authority or
  measured-human validation.
- #4042 owns the external immutable release and claim-promotion adapter. Its
  clean local checkpoint is `730210d9e39730ac72c4bbc0ed77c61210411873` in
  `C:\Users\diete\Repositories\worktrees\AffineDrift-4042-e10`. Independent
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

## Validation

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

1. Keep production companion installation fail-closed. Finish provider
   #9174/#9190–#9193 before installing any lock/snapshot or starting generated
   catalog #4023/#4024; then exercise #4030 against current and previous
   supported provider schema versions.
2. Obtain explicit human approval for the #4089 visual candidate before
   creating an approved baseline. Implement #4086 shared evidence semantics
   only when the provider-owned catalog and evidence authority are protected.
3. Build #4087 from existing governed claim/critique/readiness/provider IDs;
   never create a competing scientific registry.
4. Run #4088 baseline and follow-up reader validation under its privacy and
   preregistration gates. Keep #4042 and #9267 fail-closed until independently
   complete and protected.

## Do Not

- Do not duplicate computational engines or edit generated projection files.
- Do not use mutable upstream links as scientific authority.
- Do not revive a stale worktree without fetching and proving exact ancestry.
- Do not promote simulation-ready, manufactured, unavailable, or private
  evidence to validated or published status.

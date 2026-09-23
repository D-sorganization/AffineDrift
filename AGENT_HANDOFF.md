# Paired Chapter 1 Review in CI — #4450 / PR #4451

- Worktree: `C:/Users/diete/Repositories/AffineDrift-technical-review`.
- Branch: `fix/why-physics-rigor`; base main `bdf47374`; current commit `SELF`.
- Regular PR: [#4451](https://github.com/D-sorganization/AffineDrift/pull/4451), open.
  Governing issue #4450 is a native child of corpus #4021 under epic #4009.
- Frozen source/render revision: `787fb5819204d637b2e5eeb5ad9b589fba07b389`.
  Six findings bind twelve paths, independently checked against committed bytes.
  Binding commit: `966d3187785c2e9cb9c6f13af38f423236be1dc1`.
- Both complete Chapter 1 editions now distinguish force, acceleration, work and
  power; define the input baseline and actuator mapping; retain feasible constraint
  reactions; separate drive-torque removal, attachment removal and muscle relaxation.
  Connect these mechanics to finite-time delivery/impact without inferring skill,
  metabolism or human anatomy from manufactured model results.
- New reproducible SVG/PDF compares retained and released point-mass trajectories;
  six worked answers and 22 independent mechanics/regression cases accompany it.
  Figure output uses LF on Windows so Git preserves its frozen evidence bytes.
- Final full Python suite: 5,538 passed, 29 skipped, 132 deselected; 92.9% src
  coverage, 79.22% including scripts. All 47 focused audit/boundary/hygiene/mechanics
  cases pass. Content lint: 131 passed/four existing skips. Jest: 25 suites,
  420 passed/19 skipped. Ruff, Black, mypy (91 existing targets plus the new figure
  script), title case, bibliography, display math, size/style and site-link gates pass.
- Rebuilt 529-page PDF; physical Chapter 1 pages 32–41 inspected, final refinements
  reread. Other chapters are not certified. Production browser gate 4/4 with zero
  serious/critical axe issues. All 103 expressions render in both themes at desktop
  and mobile sizes; six wide equations and the diagram support keyboard scrolling.
- Reports: `reports/technical-review/why-physics-review.md` and
  `reports/technical-review/why-physics-render-verification.json`. Preserve these
  frozen reports during merge/live publication; use a separate publication receipt.
- Initial broad-run failures were the temporary deferred route, changing PDF digests
  during rendering and local browser captures at the root. Final bindings and
  capture relocation fix all five without weakening tests. An initial push hook
  also caught concurrent test-generated changes; the clean retry passed all hooks.
  Test-only generated timestamps/format changes were verified and restored.
- Corpus index marks both sources fully reviewed; 167 source entries still require
  a full technical audit, plus whole-book reconciliation. The user explicitly resumed
  the full active goal; never create drafts or report the corpus complete prematurely.
- Coordination session: `technical-review-20260923-why-physics`; lease 5804272169,
  presence 5804272400, expiry 2026-09-24 00:51 UTC. Inbox complete with no conflicts;
  seven historical identity warnings and two already-landed informational notices.
- Next: push this final validation/PR handoff; arm auto-merge only through central
  `scripts/automerge_guard.py`; verify checks on the final PR head, merge tree and
  live deployment. Record publication/corpus/turnover through regular PRs. Then
  continue long pending sources from remote main with a fresh ownership check.
- Validation commands: `py -3.12 -X utf8 -m pytest --cov --cov-report=term:skip-covered`;
  `py -3.12 -X utf8 -m pytest --override-ini addopts= tests/ -m content_lint --timeout=120`;
  `npx --no-install jest --runInBand`; `python -m scripts.regenerate_claim_audit_evidence --check`.
  Browser and print recipes/results are in the frozen verification report.
- Stage explicit paths only. Preserve peer handoff/log/SPEC records and old frozen
  evidence. Existing untracked captures and helpers are local QA. Local HTTP server
  session 70076 serves docs on port 8770; Playwright session is `why-physics`.

---

# Deferred Catalog Enforcement - #4445

- Worktree: `C:/Users/diete/Repositories/Worktrees/AffineDrift-deferred-guard`.
  Branch `chore/4445-deferred-catalog-guard`; commit `SELF`; PR [#4446](https://github.com/D-sorganization/AffineDrift/pull/4446), protected auto-merge armed.
- Governing issue #4445; full fleet rollout Repository_Management#1687 remains open.
- Installs the registered three-file validator bundle unchanged from central
  `0a1041018e737173e49ff97ed4b82283e3cb672f`; every SHA-256 matches its manifest.
  The new always-run pre-commit hook invokes the portable entry point directly.
  Other hooks and original DV-4253 planning/source bytes are preserved.
- Syncs only the central deferred-validation managed block from RM PR #1723,
  source `198c2baea626b311d8bf3c01db5ccb80dc3c495b`, now merged unchanged in
  central `a59cb194fe9a04c8ecc655c112539356a268a45d`. Its deployed-v1 fields
  are distinct from new adopters.
- TDD: four integration tests fail for the absent hook, then all four pass.
  They execute the configured hook on the actual catalog and on isolated invalid
  activation, missing-checker and competing-catalog copies. Actual pre-commit
  hook passes. No validation implementation is duplicated in the tests.
- Root Ruff passes; Black reports 721 files unchanged (optional notebook formatter
  unavailable); three copied modules pass mypy; title audit checks 637 sources.
  CI-equivalent mypy passes 91 source files. The broad Python run records 5,483
  passes, 26 skips, 132 deselections and two hygiene failures caused solely by
  transient .coverage.OGLaptop.\* subprocess files; coverage is 77.27% (floor 75%).
  After coverage combines, all 30 hygiene/catalog/SPEC controls pass. Test-created
  generated date changes were restored; no allowlist or threshold was changed.
- A fifth RED test requires the pinned bundle receipt; all five catalog/digest
  controls now pass after the real hooks. Explicit-file Black reproduced drift in
  all three canonical files; changing the existing vendored-path policy from
  extend-exclude to force-exclude preserves its intended exact bytes for hook
  inputs too. The receipt lives in docs/development/deferred-catalog-bundle.json.
- Validation commands: `python -m pytest --cov --cov-report=term:skip-covered`;
  `python -m pytest tests/test_root_hygiene.py tests/test_deferred_catalog_hook.py
tests/test_spec_changelog.py -q -o addopts=''`; root Ruff/Black and the exact
  CI mypy command; explicit `pre_commit run --files` passes all configured hooks.
- Narrow per-file lint exceptions retain the canonical code: S101 only in the
  checker whose assertions narrow types after runtime checks; S105 only in the
  handoff checker where SELF is a commit marker, not a password. No gate bypass.
- The optional standalone handoff-validator CLI reports missing legacy sections
  in docs/development/HANDOFF.md because it does not recognize this repository's
  prose override to AGENT_HANDOFF.md. The catalog gate imports only its secret
  patterns and passes; the actual canonical root handoff is updated here. This
  deployment does not introduce a new handoff-format gate or rewrite peer history.
- The central development-log checker also reports ten pre-existing metadata
  findings (missing historical verification SHAs/fields); comparison with unchanged
  baseline HEAD reproduces the identical findings, with none introduced here.
  Its portfolio warning remains. Existing peer entries are preserved.
- Preserve both live scientific-review agents' handoff/log/SPEC entries. Coordination
  notice: RM mailbox 5802259806. No article, model, approval or measurement changes.
- Merge sync preserves scientific peer #4443 from main `6036629e`, including
  its complete development entry, SPEC row and source/evidence bytes. All fifty
  selected catalog, hygiene, SPEC and contraction-review tests pass.
- Next: publish through protected CI and verify default-branch bundle/hook/rule bytes. Continue the
  other nine owner installations and deployment audit under the central goal.

---

# Deferred Impact Project Projection — #4438

- Repository/worktree: AffineDrift,
  `C:/Users/diete/Repositories/Worktrees/AffineDrift-deferred-project`.
- Branch: `docs/4438-deferred-project-projection`; base `96c703c2`; commit `SELF`;
  PR: [#4439](https://github.com/D-sorganization/AffineDrift/pull/4439), open with protected auto-merge armed. Development entry DL-#4438; fleet parent RM#1687 / RD#1248.
- Adds initial `docs/project/CHARTER.md` and `STATUS.md` for the existing impact
  program. #4253 stays active for theory/source/numerical work; DV-4253 is parked
  with its original owner-plan link and pending Board/prerequisite decisions.
- The charter explicitly limits its feature counts to this initial program slice.
  Source README/SPEC and current open epic were inspected; original catalog,
  plan and source snapshot are preserved. No measurements, approval, scheduled
  Staff Hub run or full-program completion are claimed.
- Validation: central catalog valid; central/dashboard parsers agree on both
  feature rows and three pending decisions. Every original planning byte is
  unchanged. Title-case (637 sources) and SPEC changelog checks pass; normal
  docs commit and pre-push hooks pass. No executable source changes.
- This scoped fleet-planning rollout preserves the independent technical-review
  campaign below.
- Merge sync: incoming force-mobility PR #4437 is preserved exactly from main
  7664a390; both development-log entries and handoff histories are retained.
- Next: validate and publish through a regular protected PR; verify default-branch
  content and live dashboard projection after cache refresh. The new feature-detail
  UI is Runner_Dashboard#1251; shared discovery is RM PR #1717. Full fleet rollout
  remains open. Preserve the independent technical-review state below.

---

# Completed Technical Review Checkpoint — #4444

This checkpoint completes the existing Chapter 2 correction and publication
verification. No additional article or textbook rewrite was started. The broader
corpus review remains incomplete: 169 source entries still require a full
technical audit, plus the recorded whole-book reconciliation work.

- Regular correction PR: #4448; issue #4444 under #4021/#4009.
- Frozen source/render revision: `0aa07cf70e074dfe6b3d6ee32767d0096418f734`.
  Six findings bind twelve retained evidence paths. The legacy development
  figure helper remains documented as provenance, while the deployed evidence
  binding uses the retained Chapter 3 mechanics tests.
- Corrected both full Chapter 2 editions: frames and angle signs, configuration
  versus predictive state, constraint rank and reachability, directional endpoint
  velocity/acceleration, synthetic examples and six worked answers. The 527-page
  PDF was rebuilt; physical Chapter 2 pages 41–50 were inspected. Other chapters
  were not certified by rebuilding the book.
- Final local suite: 5,516 passed, 29 skipped, 132 deselected; 92.88% src coverage
  and 79.19% including scripts. All 59 focused/boundary cases and 131 content-lint
  cases pass (four existing content skips). Ruff, Black, mypy and repository
  content/evidence gates pass. All book compilation jobs passed in CI.
- Local browser gate: 4/4; 89 expressions and 15 displays render. Eight wide
  mobile equations, the table, diagram and code support keyboard scrolling at
  reading size. Frozen scientific/render reports were preserved through release.
- CI attempt 1 had one homepage navigation timeout before its assertion and
  133 browser passes. The unchanged heading test passed three local runs;
  the protected retry passed all 134 Chromium tests, visual158/158 and
  route240/240. No timeout or assertion was weakened.
- PR #4448 merged at `9d72e2c2124730a8642be45e837c9069b2484368` with every required check green; its tree matches checked head `8ccf6f664f63ff5c5fc6e2810e00209237e36809`. Deployment 35925227535 succeeded: live 960/960, all four cases for each reviewed route, and zero serious/critical axe violations. Artifact 10779298519.
- PR #4443 corrected the complete contraction lay article. Its frozen revision
  `65e74e9ac43d8cf93205cdddd238e1d02c7e7094` and ten evidence paths remain
  unchanged. Its separate publication receipt records verified carry-forward
  after superseded deployments; cancellation is not reported as success.
- Publication receipts: `reports/technical-review/language-motion-publication.json`
  and `reports/technical-review/contraction-lay-publication.json`.
- Independent #4445/#4446 and #4447 changes, handoff sections and SPEC rows are
  preserved. Do not treat other agents' work or historical records as this
  checkpoint's remaining development scope.
- This release does not complete the broader corpus/epic. The latest explicit
  instruction resumes the full goal. Merge the regular turnover PR first;
  subsequent review starts from remote main, checks live ownership, prioritizes
  long pending sources, and uses the corpus index and frozen reports.
  Never create draft PRs. Earlier pause records are historical.
- Older untracked browser captures, rendered previews and analysis scratch files
  are local QA, not unpublished source changes. Stage explicit paths only.

---

# Resumed Technical Review — Contraction Lay Article #4441

The user explicitly resumed the broader review after the published #4437 and
checkpoint #4440. The goal remains incomplete. Continue substantive reviews,
prioritizing long pending sources, and use regular protected PRs to main.
Never create draft PRs. Previous pause records below are historical.

- Worktree: `C:/Users/diete/Repositories/AffineDrift-technical-review`.
- Branch: `fix/contraction-lay-rigor`; base main `585f700b`.
- Regular PR: #4443 merged at 6036629e; protected checks passed. Live deployment 35916642728 verification is pending.
- Current source/render checkpoint: `65e74e9ac43d8cf93205cdddd238e1d02c7e7094`; issue #4441, native child of #4021
  under epic #4009. Historical route batch #4056 remains closed; its limited
  route acceptance does not certify all article content.
- Complete lay article and corrected technical companion read. Corrected
  incremental-stability examples, Riccati rates and normalization, finite-horizon
  interpretation, unsupported benchmarks/software, optimization assumptions,
  physical impedance and golf outcome/event sensitivity. No new human data.
- Full local run: 5,490 passed, 29 skipped, 132 deselected; 92.88% src coverage
  and 79.19% including scripts. The broader default lane also collects benchmark
  correctness cases; no comparative runtime claim. Test-generated date/format
  changes were verified and restored. Fleet policy sync #4442 from main
  `438bd9c1` changes only AGENTS/CLAUDE and is preserved.
- Twenty new regression/numerical cases; 56 focused cases pass. Red baseline:
  nine expected failures. All 638 source titles pass; content lint 131 passed
  with four existing skips; Ruff, Black (721 files), mypy (91 files),
  bibliography (169 entries), display math and the site link gate pass.
- Quarto HTML and production browser gate pass 4/4. Expanded keyboard/axe
  checks pass 4/4. All 78 expressions and nine displays render without errors;
  two wide equations scroll on mobile at 17.78px, desktop font is 18px.
- Review: `reports/technical-review/contraction-lay-review.md`; machine evidence:
  `reports/technical-review/contraction-lay-render-verification.json`.
- Initial raw HTML contained the known legacy polyfill; production sanitization
  removes it. No unrelated global styling, CSP, numerical module or workflow
  change. Reused existing disclosure and reading-size CSS.

## Next Release Steps

The review and all six findings now bind ten evidence paths to the immutable
source/render checkpoint above. All committed hashes match the declared bytes.
Local full validation passed. Publish a regular PR, pass protected CI, verify merged bytes
and live deployment, and update the turnover/corpus records. Do not count the
405-source corpus or whole-book consistency as complete from this one page.

## Coordination

Session `technical-review-20260923-contraction-lay`, agent codex. Lease receipt
5801562142 and presence 5801562442 expire at approximately 21:34 UTC September 23.
The startup inbox was complete with no conflicts and six rejected historical
identity warnings; independent project-planning records are preserved.
Stage explicit paths; scratch renders, captures, scripts and logs remain under
`docs/development/technical-review/`. Do not stage older untracked artifacts.

---

# Paused Technical Review Checkpoint — #4437

The user requested a stopping checkpoint. All current scientific changes are
merged on remote main and verified live. Merge this final documentation-only
closeout through a regular PR, then pause. No new article, issue or rewrite is
authorized until the user explicitly resumes. Never create draft PRs.

- Scientific release: regular PR #4437, merged September 23 at 17:51:25 UTC.
- Remote-main source: `7664a39026811e19d23abd72b9b5638ebe88996b`.
- Checked PR head: `cacba18b677457c4460234894e702fa1646dbe3a`.
- Their trees match exactly: `c97e2382aa6043c0985c7eb337e871b4a3ef70fc`.
- Deployment `35898481011` was superseded by the independent project-docs
  merge #4439. Current publication run `35900025138` targets main
  `c169bbd93a262d0bb48cf3024977f6869a559c28`, which retains every scientific
  source and frozen evidence byte. It succeeded with live 960/960, including
  all four article cases and zero serious/critical axe violations.
- Closeout branch: `docs/force-mobility-pause-checkpoint`; commit `SELF`.
- Worktree: `C:/Users/diete/Repositories/AffineDrift-technical-review`.

Publication receipt: `reports/technical-review/force-mobility-publication.json`.
Live artifact `10769877887` retains the complete gate summary, four article
cases and its GitHub SHA-256 digest. The live manifest was independently
confirmed at `c169bbd9`. One transient response recovered under the standard
retry policy; no retries were exhausted.

## Completed Correction and Evidence

Issue #4436 is closed by PR #4437. The complete article and bibliography now
separate rate/load metrics, conditional reciprocity, singular geometry,
constrained dynamics, impact and compliance. Independent counterexamples
connect these quantities without asserting unmeasured human capacities.
The rectangular SVD is corrected, mobile math remains readable, and the
corrected lay and critics' text uses visible native disclosures.

Six findings and eight evidence paths bind to exact source/render commit
`d032cb0fd65c3674a0ba7c950c5e4b41962288b0`. Initial science is `981e8d34`;
the later source checkpoint corrects CRLF/LF hashes inside the render record.
Do not refresh these frozen records during this documentation-only closeout.
The technical review and browser reports are under `reports/technical-review/`.

## Validation

All required PR checks passed, including full-site browser/accessibility,
Python, JavaScript, links, static checks and the aggregate quality gate.
CI Python: 5,422 passed, 32 skipped, 132 deselected, 92.85% coverage.
Content lint: 131 passed, four existing skips. All 56 local audit/root/scientific
checks pass after resolving the temporary audit deferral and scratch hygiene.
Twenty new mechanics/algorithm cases and two planar-scope checks pass.
Local production and expanded keyboard/axe each pass four device/theme cases;
all 133 expressions render, 16 displays were inspected, and four wide mobile
equations scroll at 17.78px without document overflow.

The advisory benchmark workflow reported no executed benchmarks because its
environment lacked the timeout plugin; its job nevertheless returned success.
No performance result is claimed. This unrelated tooling limitation was not
expanded into a new task or workflow change during the requested closeout.

## Stop Boundary and Remaining Scope

The broader review is paused after this release, not complete. The 405-source
index has 172 entries still marked Full Technical Audit Pending, plus a
whole-book consistency pass. The 240-route inventory (237 reviewed, three
exempt) is a coverage census, not full-corpus technical acceptance. Historical
provenance follow-up #4429 stays open and outside today's work.

No next development task is assigned. At a future explicit resume, read the
corpus index, epic #4009 and the relevant child issue before selecting work.
Preserve the distinction between model identities, illustrative calculations
and empirical evidence.

## Coordination and Workspace

Session `technical-review-20260923-mobility` owns the release closeout.
Its original issue lease is receipt `5798813017` (expires 18:42 UTC);
closeout presence `5800030166` expires 19:52 UTC. Release both at the final pause.
The inbox reported no conflicts and six rejected identity warnings. The other
active project-planning session was informed at receipt `5800266364` that this
release is closing out. Its #4438 handoff and development-log entries are
preserved exactly; its planning work is independent of this paused review.

Local scratch files were preserved under
`docs/development/technical-review/checkpoint-4436-local-artifacts/`.
Stage explicit paths; many older untracked QA artifacts remain. The final diff
must contain only turnover/log/index records and the publication receipt.
For GitHub auth, use the documented Codex App bootstrap. If its cached token
fails, the same setup helper with `-SkipGhLogin` refreshes it; suppress setup
output and never expose credential values or switch identities.

A routine deployment triggered by the final documentation-only merge does not
require another receipt commit or a restart of development.

# Previous Checkpoints

# Paused Technical Review Checkpoint

The user requested a stopping checkpoint. The current technical releases are
merged and verified live. Merge this final documentation-only closeout through
a regular PR, then stop. No new article, issue or rewrite is authorized until
the user explicitly resumes the broader goal. Never create draft PRs.

- Worktree: `C:/Users/diete/Repositories/AffineDrift-technical-review`.
- Turnover branch: `docs/technical-review-pause-checkpoint`; commit `SELF`.
- Published source checkpoint on remote main:
  `66f63f873ce05d441189816825c31888fb87af38` (regular PR #4433).
- All protected checks passed. The merged main tree exactly equals checked
  PR head `af8347f380cb1b592ca157185c4a45d6b1360ec2`.
- This closeout changes only handoff/log/index records and publication receipts.
  Scientific sources, tests, styles and frozen audit evidence remain unchanged.
  A routine deployment triggered by the documentation merge does not require
  another receipt commit or restart of development.

## Completed Releases

| Work                       | Regular PR | Published Main | Deployment    | Live Result |
| -------------------------- | ---------- | -------------- | ------------- | ----------- |
| Putting Roll               | #4424      | `ded63640`     | `35792227837` | 960/960     |
| Induced Acceleration       | #4426      | `99aa5835`     | `35796355561` | 960/960     |
| Zero-Torque Counterfactual | #4430      | `4fe70151`     | `35802860809` | 960/960     |
| Manifesto Units and Scope  | #4432      | `2ef5c908`     | `35805142089` | 960/960     |
| Nonlinear Control Insights | #4433      | `66f63f87`     | `35807652744` | 960/960     |

Publication receipts are under `reports/technical-review/`. The final two are
`manifesto-notation-publication.json` and
`nonlinear-control-insights-publication.json`. They retain full source SHAs,
run URLs, artifact IDs/digests, complete gate summaries and the reviewed route
cases. Each final release passes all four mobile/desktop and light/dark route
cases and the whole-site serious/critical accessibility gate.

## Technical Decisions and Frozen Evidence

Nonlinear-control final source/render checkpoint:
`a424ead9e985bb6e47e658c4497bf1460af70c0c`. The initial scientific checkpoint
is `3053bb71`; only 17 published-link suffixes changed afterward. Eight findings
and nine evidence paths bind to the final committed bytes. The review report
records derivations, independent checks and primary-source access limits.

The argument connects instantaneous acceleration, energy accounting, declared
interventions, finite-time control and measurement identifiability. The physical
two-rod example uses unchanged Cartesian mechanics helpers. A positive distal
acceleration increment can coexist with negative total distal acceleration and
negative actuator power. Accessibility does not establish practical control
or human sequencing benefits. The governed sequencing critique remains open;
this rewrite does not adjudicate it or supply new human validation.

Manifesto source/render `2250d07f` and aggregate `31664586` remain frozen.
Zero-torque scientific evidence remains at `e7d8c688`. Preserve the distinctions
between model identities, illustrative calculations and empirical evidence.

## Validation

- All required checks passed before PR #4433 merged, including Python,
  JavaScript, end-to-end, accessibility, links and the aggregate quality gate.
- All 55 selected scientific/audit checks passed; full content lint passed
  131 tests with four existing skips. The new article contributes 16 checks
  and reuses 11 existing Cartesian-mechanics checks.
- Local production and keyboard-expanded summary checks each passed 4/4.
  All 106 math expressions rendered in each case; all 22 displays and six
  wide mobile endpoints in both themes were inspected.
- Both releases passed live 960/960. Nonlinear artifact `10729736031` and
  manifesto artifact `10727234915` report zero serious/critical axe violations.
- The two initial PR failures were resolved: published `.html` link targets
  replaced `.qmd` targets, and issue #4431 identified the actual new test module.

## Remaining Scope and Resume Instructions

The broader audit is paused, not complete. The corpus index contains 173
sources marked Full Technical Audit Pending, plus a whole-book consistency
pass. The 219-route census does not establish full-corpus technical acceptance.
Historical provenance follow-up #4429 remains open and was not taken on during
this closeout. Older publication-pending wording in historical records should
be interpreted against the corresponding immutable publication receipts.

No next development task is assigned. On an explicit future resume, read this
checkpoint, the corpus index, epic #4009 and the relevant child issue before
selecting work. Preserve frozen source/evidence relationships and record any
future carry-forward explicitly rather than silently refreshing old claims.

## Coordination and Workspace

Completed issue #4431 belongs to #4058/#4021/#4009. Session
`technical-review-20260923-nonlinear` registered the documentation closeout at
receipt `5787749290`; release its issue lease and presence at the final pause.
The last inbox had no messages or conflicts, but remained incomplete due to
pre-existing malformed/identity-rejected board comments. This is not evidence
that no other agent exists. At a future resume, check claims and the inbox.

Stage explicit paths: this worktree contains many untracked local QA artifacts.
No scratch screenshots, logs, downloaded artifacts or temporary scripts belong
in the final closeout commit. Do not push directly to main.

# Historical Checkpoints

The records below describe earlier states. The current checkpoint above controls.

## Deferred Impact Evidence - 2026-09-22

- Worktree: `C:/Users/diete/Repositories/Worktrees/AffineDrift-validation-planning`.
  Branch `docs/deferred-validation-planning`; commit `SELF`; PR #4423 is open.
- Governing epic #4253; central standard Repository_Management #1687. Added
  DV-4253, catalog and original public issue snapshot, README link and synced
  central policy. Empirical/perceptual dependencies are future Board work.
- Keep #4253 open for qualified provider-result and literature synthesis. No
  roadmap label, completed experiment, acoustic effect or perception claim is
  supplied by this documentation. Tools/UpstreamDrift retain experiment ownership.
- Validation: catalog valid, all three existing heavy-hit boundary checks pass,
  and the 637-file publishable title audit passes.
  No article, citation, executable model or trust-evidence source was changed.
- Main `9ef76c6e` integrated without article/model edits; both handoff scopes kept.
- Next: publish through normal PR checks, verify default-branch plan artifacts,
  then post the immutable scope link on #4253 and record the audit receipt.
- Branch policy: current root CLAUDE/AGENTS and user-authorized topic-PR workflow
  target main; older GAAI staging guidance is superseded for this work.

## Fleet Main Health: #4406 Deploy Website

- Worktree `C:/Users/diete/Repositories/agent-worktrees/issue-4406-local`, branch
  `fix/issue-4406-deploy-website-local-storage-pageerrors-local` (base `7a0a9986`).
- Deploy run 35619994945 failed 960/960 with one cell:
  `/resources/resources-videos.html` mobile/light — nine third-party YouTube iframe
  `pageerror` messages for denied `localStorage` access (artifact
  `local-every-page.json`).
- Fix filters those embed SecurityErrors in `scripts/verify-public-site.js` via
  `isActionablePageError`, with Jest contract coverage in
  `tests/public-site-verifier.test.js`.

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

- **Current implementation:** paired Chapter30b review #4425, branch
  `fix/induced-acceleration-rigor`, starts at d3bc7d76. Complete original source
  reads and eight new/19 combined mechanics checks are saved; rewrite pending.
  Current HANDOFF and induced-acceleration-preparation.md lead.

- **Force merged:** #4421 passed protected checks and merged as 9ef76c6e;
  tree equals4047d917. Deployment35787101015 is pending.

- **Superposition shipped:** deploy 35782578807 succeeded at 31cdc615; 960/960 live cases and all four article cases passed. Durable publication record is saved.

- **Current successor:** putting issue #4422, regular PR #4424, branch `fix/putting-roll-rigor`,
  starts at force head 4047d917. Fifteen independent checks and four production browser cases pass; final
  rendered review passes and seven findings are bound to a17f5ded. Preparation notes and current HANDOFF lead.
  Prior force implementation details below remain valid for PR #4421.

- **Active:** comprehensive review #4009/#4021; long articles and paired sources
  first, regular PRs only. The goal remains active.
- **Shipped:** anatomy #4414 and preface #4416, verified on protected main
  581857cb by deploy 35774559003, 960/960 live cases; eight relevant route cases
  saved in `reports/technical-review/anatomy-preface-publication.json`.
- **GRF delivery:** #4417 merged as a6774e33 with all protected checks green.
  Deploy 35779150741 succeeded: live artifact 10718336671 passes all 960 cases
  across 240 routes. All four GRF cases were independently inspected; the durable
  publication record is reports/technical-review/ground-reaction-publication.json.
  Scientific evidence remains bound to 8feeaa11.
- **Superposition delivery:** regular #4419 merged as 31cdc615; deployment
  35782578807 is pending. Protected main has the same tree as f5e8dca1. Four
  scientific findings remain bound to 47321eb8; no evidence rebind is required.
- **Current implementation:** #4420 under measurement #4059, branch
  `fix/force-measurement-rigor`, regular PR #4421. SELF saves the complete article reread, eight
  corrected finding groups, independent numerical checks and final render review.
  Article-scoped CSS fixes the inaccessible expanded overview and preserves
  readable math. The report records full-paper versus abstract access limits.
- **Next:** the article, CSS, tests, review and render records now bind to 99d1653c
  using committed LF bytes. The zero-deferred census is restored. Protected main 31cdc615 is integrated by normal merge 7cac4aad; final diff
  excludes superposition science. Drive #4421 checks and verify predecessor
  superposition live publication before merging.
- **Coordination:** session `technical-review-20260922-anatomy`; #4420 lease
  5783527746 expires 22:21 UTC, presence 9730b845 expires 22:52 UTC September 22.
  Inbox reports no messages/conflicts but incomplete unrelated board evidence.
- **Turnover:** DL-#4420/#4418/#4415; primary-source preparation is in
  `docs/development/technical-review/force-measurement-preparation.md`.
  Local PDFs/text/XML and browser helpers are QA material, not publication.
  Stage explicit paths; many historical untracked QA files remain. Never
  force-push or bypass hooks. The broader goal remains active.

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

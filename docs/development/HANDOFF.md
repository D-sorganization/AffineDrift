# Datasets Page Rebuild — #4549 (WEB-07.7)

- Repository: `D-sorganization/AffineDrift`, worktree
  `C:/Users/diete/Repositories/AffineDrift-worktrees/claude-4549`.
- Branch `claude/issue-4549`, commit `SELF`; pull request:
  https://github.com/D-sorganization/AffineDrift/pull/4632 (draft, targets
  `main`).
- Governing issue: #4549 (WEB-07.7, child of epic #4552). Objective: rebuild the
  Datasets resource page with real licence/access/schema/checksum metadata for
  third-party datasets and AffineDrift's own `data/`/`schemas/` artefacts, and
  drop the third-party `mini.s-shot.ru` thumbnail host.
- Added `data/datasets.yml` as the single source of truth (4 third-party
  datasets: GolfDB, CaddieSet, SportsPose, MoVi; 3 AffineDrift artefact groups:
  `data/ztcf`, `data/research_protocols`, `schemas`). Licence/access/size fields
  for the third-party entries were verified against each dataset's own GitHub
  repository or paper (WebFetch), not guessed; SportsPose has no licence stated
  by its publisher, and the page says so rather than inventing one. AffineDrift's
  own artefacts have no declared data licence yet — tracked separately as
  WEB-07.8 — so their `licence` field says "not yet declared" instead of picking
  MIT or all-rights-reserved.
- Added `src/tools/datasets_catalog.py` (load/validate `data/datasets.yml`,
  compute real SHA-256 checksums per file, render HTML cards) and
  `scripts/generate_datasets_catalog.py` (CLI wrapper with `--check`), following
  the existing `generate_programming_catalog.py` generated-page pattern.
  `resources/resources-datasets.qmd` now has a
  `<!-- GENERATED:BEGIN/END datasets-catalog -->` block that the generator
  owns; hand-edit `data/datasets.yml` and regenerate instead.
- Wired `python3 -m scripts.generate_datasets_catalog --check` into
  `.github/workflows/ci-standard.yml` next to the Programming Companion catalog
  check, so a stale page or a hand edit fails CI.
- Added `.resource-meta`/`.resource-checksums` styles to `css/resources.css`
  (mirrored to `docs/css/resources.css` via `scripts/sync_frontend_assets.py`)
  and dropped `.resource-card.has-media`/`<img>` thumbnails from this page —
  no self-hosted screenshot images were fabricated; the rest of the resources
  section (Papers, Websites, etc.) already uses plain cards without thumbnails.
- Tests: `tests/test_generate_datasets_catalog.py` (14 cases) — DbC field
  validation, real-SHA-256 checksum computation, marker-block replacement
  preserving surrounding content, and each of the four issue acceptance
  criteria (no truncated text, no third-party thumbnail host, every entry has
  licence/access, artefacts listed with checksums).
- Validation commands run in this worktree:
  - `python3 -m pytest tests/test_generate_datasets_catalog.py -q` → 14 passed.
  - `python3 -m scripts.generate_datasets_catalog --check` → up to date.
  - `python3 -m ruff check .` → all checks passed.
  - `python3 -m black --check --line-length 100 .` → 736 files unchanged.
  - `python3 -m mypy src/tools/datasets_catalog.py scripts/generate_datasets_catalog.py`
    → no issues.
  - `python3 scripts/check_quarto_render_coverage.py`,
    `python3 scripts/scan_quarto_syntax.py`, `python3 scripts/check_quarto_xrefs.py`,
    `python3 scripts/check_single_title.py resources/resources-datasets.qmd`,
    `python3 scripts/check_title_case.py`, `python3 -m scripts.check_module_size_budget`
    → all pass.
  - Full `python3 -m pytest --cov` suite: see the PR description for the run
    started from this worktree (long-running; results attached there).
- Not done / deferred: no `_quarto.yml` resource-publishing change was made, so
  schema filenames in the AffineDrift cards are shown as plain text, not links
  (`schemas/` is only partially published as a site resource today). No CSS
  `check_style_discipline.py` fixes were made — it reports 248 pre-existing
  violations across other stylesheets unrelated to this change; `resources.css`
  itself has zero.

- Unrelated fix required to push at all: this host's global Python had a
  broken `PySide6` install (`ImportError: DLL load failed while importing
  QtCore`). `pytest-qt`'s autodetection (`qt_compat.py::_guess_qt_api`) only
  catches `ModuleNotFoundError`, not `ImportError`, so probing PySide6 crashed
  `pytest_configure` with an uncaught `INTERNALERROR`, which failed the
  `pytest-unit` pre-push hook for every push attempt — reproduced directly with
  `python -m pytest tests/unit -x -q --tb=short -m "not slow and not
  integration"` outside the hook too, so it is not hook-specific. Fixed with a
  one-line addition to `tests/conftest.py`
  (`os.environ.setdefault("PYTEST_QT_API", "pyqt6")`), next to the existing
  `QT_QPA_PLATFORM` line, pinning to the binding this repo actually installs
  and skipping the crashing autodetection entirely. This is a pre-existing,
  host-environment issue unrelated to the datasets page; called out here and
  in the PR body rather than silently folded into the feature diff.

## Next Steps

1. None outstanding for #4549 from this session.
# Implementation Handoff — Create "How to Read This Site" Guide (#4491)

## Identity

- Repository: D-sorganization/AffineDrift
- Branch: fix/web-01-6-how-to-read-this-site-4491
- Baseline commit: fc36109d (origin/main)
- Implementation commit: dd961a63
- Pull request: #4665 (https://github.com/D-sorganization/AffineDrift/pull/4665)
- Governing issue: #4491 (WEB-01.6, epic #4496)

## Objective and Status

- Objective: Create a canonical "How to Read This Site" guide explaining the content layers, publication maturity states, the evidence ladder, critique records, and citation standards. Consolidate publication states to be single-sourced.
- Status: Implementation complete, tests and static checks passing; opening PR.
- Completed:
  - Created `pages/how-to-read.qmd` covering site architecture, the six canonical publication states (`Available`, `Validated`, `Experimental`, `Planned`, `Deprecated`, `Opinion`), the 4-level evidence ladder, how to read critique records, and citation standards.
  - Replaced inline publication-state definitions in `index.qmd` and `pages/development-roadmap.qmd` with links to `how-to-read.html#publication-states`.
  - Linked status pills in `pages/tools.qmd` to `how-to-read.html#publication-states` and normalized non-canonical `EXPLORATORY` to `EXPERIMENTAL`.
  - Added link styles for `a.status-pill` and `.status-banner__title a` in `css/components/status-banner.css` and compiled bundle to `docs/styles.css`.
  - Integrated `How to Read This Site` into `_quarto.yml` navbar Read menu and footer navigation.
  - Added unit test suite `tests/test_how_to_read.py` (6 tests).
  - Regenerated claim audit evidence digests and updated `SPEC.md` changelog.

---

# Implementation Handoff — Unified Publication Status Badge Component (#4516)

## Identity

- Repository: D-sorganization/AffineDrift
- Branch: fix/web-04-2-status-badge-component-4516
- Baseline commit: b000cfee (origin/main)
- Implementation commit: 8623636f, 8a5b6b98
- Pull request: to be opened
- Governing issue: #4516 (WEB-04.2, epic #4499)

## Objective and Status

- Objective: Implement a unified publication status badge component used on cards, headers, listings, and search, rendering an inline SVG icon and accessible text for all 6 canonical states, meeting WCAG AA contrast in light and dark themes, and linking to the publication state definition.
- Status: Implementation complete, test suites passing (Python tests, link checker, Jest/npm tests); opening PR.
- Completed:
  - Created Quarto shortcode `{{< status >}}` (`_extensions/status/_extension.yml`, `_extensions/status/status.lua`) supporting front matter detection (`status`, `maturity`, `publication-state`) and explicit parameters (`{{< status available >}}`, `{{< status "planned" "In Planning" >}}`).
  - Added SVG icons and textual labels for all 6 canonical states (`available`, `validated`, `experimental`, `planned`, `deprecated`, `opinion`) plus normalization for legacy aliases (`canonical`, `reviewed`, `exploratory`, etc.).
  - Implemented high-contrast theme-aware styling in `css/components/status-badge.css` meeting WCAG AA contrast (≥ 4.5:1, achieving ≥ 8:1) for both light and dark (`body.quarto-dark`) themes.
  - Linked status badges by default to `pages/how-to-read.html#publication-states` with depth-aware relative path computation (`quarto.project.offset` and source path handling).
  - Integrated with `scripts/filters/page-header-card.lua` to render status badges on page headers when metadata contains a publication state.
  - Replaced legacy `.status-pill` elements across `pages/tools.qmd`, `pages/book-reviews.qmd`, `pages/daydreams-doodles.qmd`, `pages/drifter-manifesto.qmd`, `resources/research-reviews.qmd`, and updated `CONTRIBUTING.md`.
  - Added unit test suite `tests/test_status_badge.py` (15 tests) verifying all 6 states, icons, labels, aliases, link resolution, and contrast requirements.
  - Regenerated claim audit evidence digests and updated `SPEC.md` changelog.

---

# Implementation Handoff — Cache Quarto Renders in CI (#4595)

## Identity

- Repository: D-sorganization/AffineDrift
- Working directory: C:/Users/diete/Repositories/AffineDrift-worktrees/claude-4595
- Branch: claude/issue-4595
- Baseline commit: 382446d0dafee32930744c7f2aabb8a4915fb757
- Implementation commit: `SELF`
- Pull request: to be opened as a draft by this session
- Governing issue/epic: #4595 (WEB-13.1, part of epic #4604 "[E13] Build, Reliability, and Maintainability")

## Objective and Status

- Objective: stop the ~14-minute full Quarto render running unconditionally on every PR's
  `e2e-tests` job in `ci-standard.yml`, per the issue's acceptance criteria (cache `.quarto/`
  keyed on source hashes, or render incrementally for PRs; reduce median PR end-to-end time by
  ≥ 30 %; deploy keeps doing a clean full render).
- Status: **partial / honest-scope**. Implemented the safe half of criterion 1 (an
  `actions/cache` step over `docs/` + `.quarto/`, keyed by `hashFiles()` on every
  Quarto-render-relevant source pattern) and left criterion 3 untouched by construction
  (`deploy-website.yml` was not edited). Criterion 2 (≥ 30 % median reduction) cannot be
  confirmed from this session — it needs real CI timing history after this merges, which is not
  fabricable — so it is not checked off.
- Why the scope stops here: a true "render incrementally for PRs" implementation (rendering only
  the changed `.qmd` files while reusing a restored `docs/` for the rest) was built first, but
  `tests/test_deployment_integrity.py::test_ci_captures_revision_bound_representative_visual_evidence`
  already guards, with an explicit #4126 rationale, that the E2E lane always does
  `run: quarto render --to html` (the whole site) — "so every representative route family is
  present without a hand-maintained per-file render list" — and never a per-file invocation. A
  partial render would restore a `docs/` tree that mixes this PR's changed pages with an older
  cached snapshot of every other page, undermining that guarantee for the governed
  representative-visual-evidence and per-route axe-core steps later in the same job. Overriding a
  deliberate existing safety invariant to hit a performance target is exactly the kind of
  contested design decision CLI-tier agents are asked not to guess on (`tier:strong` territory,
  not `tier:cli`), so the implementation was scoped back to the option that cannot regress
  correctness: skip the render only on an **exact** hash match (nothing Quarto-render-relevant
  changed at all since a previous cached run), and fall through to the identical, unconditional
  full render otherwise. No `restore-keys` fallback is configured, specifically so an inexact
  match can never restore a stale/incomplete `docs/`.
- Completed:
  - `.github/workflows/ci-standard.yml` (`e2e-tests` job): new "Restore cached Quarto render" step
    (`actions/cache@55cc8345863c7cc4c66a329aec7e433d2d1c52a9 # v6.1.0`, pinned per
    `scripts/check_workflow_action_pins.py`), caching `docs` + `.quarto`, keyed on
    `hashFiles()` over every `*.qmd` render root plus `_quarto.yml`, `.quarto-version`,
    `custom.scss`, `styles.css`, `css/**`, `js/**`, `data/**`, `schemas/**`, `references/*.bib`,
    and the other `_quarto.yml` `resources:` entries. "Build site for E2E" now runs only when
    `steps.quarto_cache.outputs.cache-hit != 'true'`.
  - TDD: `tests/test_deployment_integrity.py::test_e2e_quarto_render_is_cached_and_skipped_only_on_exact_source_hash_match`
    (written first, confirmed RED against the pre-change workflow, then GREEN).
- Remaining (recommended follow-up issue, `tier:strong` — a design decision, not mechanical):
  1. Decide whether to relax the #4126 "always full render" invariant to allow a bounded
     incremental render (e.g., only when a `docs/` snapshot restored from the base branch's last
     successful render is fresh, and the changed-file set excludes anything in this PR's new
     `GLOBAL_*` classification) without weakening the representative-evidence/axe-core coverage
     guarantee, or find another path to the ≥ 30 % target.
  2. Once real CI history exists on this branch's pattern (a run or two after merge), measure the
     actual median PR end-to-end time delta and check off criterion 2 if it clears 30 %, or open
     the follow-up above if it does not.

## Files and Decisions

- Key decisions:
  - Cache path is `docs` + `.quarto` (not `_freeze/`): this site has no executable code cells
    (per the existing "Build site for E2E" comment), so Quarto's freeze mechanism buys nothing;
    the actual expensive artifact is the rendered HTML output itself.
  - No `restore-keys`: an exact-match-only cache is strictly safer than a fallback that could
    restore a `docs/` tree from an unrelated prior commit. This trades away some of the potential
    speedup (a cache miss on any relevant change always pays the full 14 minutes, unchanged from
    before this PR) for a guarantee that a cache hit can only ever replay a `docs/` tree that
    this exact source state would have produced anyway.
  - Deploy workflow untouched: criterion 3 ("deploy still does a clean full render") is satisfied
    by construction rather than by a new check, since the cache step only exists in
    `ci-standard.yml`.
- User-owned or unrelated worktree changes: none observed.

## Validation

- `python -m pytest tests/test_deployment_integrity.py` — 16 passed, 1 skipped.
- `python -m pytest tests/test_workflow_action_pins.py` — 2 passed.
- `python -m ruff check .` and `python -m black --check --line-length 100 .` — both clean
  repo-wide.
- `python scripts/check_workflow_action_pins.py` — PASS (new `actions/cache` reference pinned to
  a full 40-char commit SHA).
- CI workflow YAML validated with
  `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci-standard.yml'))"` — OK.
- `scripts/check_dry_adoption.py`, `scripts/check_module_size_budget.py`,
  `scripts/check_changed_file_size_budget.py` — all PASS, no new violations.
- Known pre-existing failure outside this change's scope: `python -m pytest tests/` errors
  during collection on ~70 unrelated `*_rigor.py`/benchmark test modules with
  `ValueError: numpy.dtype size changed, may indicate binary incompatibility` (a
  scipy-compiled-against-a-different-NumPy-ABI mismatch in this local Anaconda environment).
  Confirmed pre-existing and unrelated: reproduces in isolation for
  `tests/test_manifold_mechanics_rigor.py`, a file this PR never touches.

## Blockers and Risks

- Blocker: criterion 2 (≥ 30 % median PR end-to-end time reduction) is not verifiable from this
  session; it requires observing real CI run durations after this merges.
- Risk: none to render correctness — the cache can only ever replay output for a source state
  that is byte-identical (by hash) to a state that already produced it; any other source state
  always takes the pre-existing full-render path unchanged.

## Next Steps

1. After merge, watch a handful of real PR `e2e-tests` run durations; if the median reduction is
   short of 30 %, open the `tier:strong` follow-up above to decide on a bounded incremental-render
   design that preserves the #4126 full-coverage guarantee.

## Change Log

- `SELF` — Cache the PR E2E Quarto render on an exact source-hash match; deploy is untouched (#4595).

---

>>>>>>> origin/main
# Service-Worker Cache Busting by Content Hash — 2026-09-29

- Repository: `D-sorganization/AffineDrift`, working directory
  `C:\Users\diete\Repositories\AffineDrift-worktrees\claude-4600`.
- Branch `claude/issue-4600`, commit `SELF`; pull request: to be opened this session (draft).
- Governing issue: #4600 (epic #4604, E13 — Build, Reliability, and Maintainability).
  Objective: resolve the unresolved content-hash cache-busting note (#1459, closed) in
  `service-worker.js` and re-enable the excluded offline Playwright test (#4140).
- Completed work:
  - `service-worker.js`: removed the stale `TODO #1459` comment. Content-hash cache busting
    is already implemented by `scripts/update_sw_cache_version.py`, which hashes the precached
    CSS/JS assets into `CACHE_NAME`'s suffix (well covered by
    `tests/test_update_sw_cache_version.py`, 12 tests, all passing); the comment now documents
    that instead of pointing at a closed issue asking for it.
  - `tests/e2e/offline.spec.js`: replaced the `should serve cached homepage when offline` test's
    hardcoded `page.waitForTimeout(3000)` with a deterministic
    `await page.evaluate(() => navigator.serviceWorker.ready)` wait, so the assertion no longer
    races the service worker's install/precache step under CI load.
  - `.github/workflows/ci-standard.yml`: dropped `should serve cached homepage when offline` from
    the full-site E2E `--grep-invert` exclusion list added for #4140. The other eight excluded
    titles are unrelated to this issue and left untouched.
- Key decision: acceptance criterion "Content-hash precache manifest" is satisfied by the
  existing `update_sw_cache_version.py` mechanism (a single content-hash-derived `CACHE_NAME`
  covering all precached assets) rather than a per-file manifest — that mechanism already has
  full test coverage, so the only unresolved half of the acceptance criteria was the stale
  comment and the CI exclusion.
- Compatibility constraints: none — no public API or cache-key format changed; `CACHE_NAME`
  values still follow the pre-existing `affinedrift-v5-<hash>` shape.
- Validation commands and outcomes:
  - `npx jest` → 25 suites, 420 passed, 19 skipped, 0 failed.
  - `python3 -m pytest tests/test_update_sw_cache_version.py -q` → 12 passed.
  - `python3 -m ruff check .` → all checks passed.
  - `python3 -m black --check --line-length 100 .` → 733 files unchanged, no diffs.
  - `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci-standard.yml'))"` → OK
    (workflow YAML still parses after the exclusion-list edit).
  - **Not run locally:** `quarto render` (blocked in this sandbox — ~14 min full-site render is
    out of policy for this session) and `npx playwright test`. The re-enabled offline spec was
    reasoned through by code inspection (SW registers on `window.load` in
    `_includes/site-after-body.html`, activates via `self.clients.claim()`, and
    `navigator.serviceWorker.ready` resolves once an active SW is present) but has not been
    executed against a real rendered site. CI's `e2e-tests` job (full-site Playwright run) is the
    first actual execution of the un-excluded test — check its result on the opened PR.
- Blockers/risks: none identified beyond the above. If CI's `e2e-tests` job still fails the
  re-enabled title, the next step is to inspect that job's trace/video artifact rather than
  re-guess a timing fix.
- Next steps: open the draft PR; watch `e2e-tests` on the PR for the un-excluded offline test.
# Implementation Handoff — Report Broken External Links as Issues (#4596)
# Implementation Handoff — Keep Internal Governance Vocabulary Out of Reader Prose (#4588)

## Identity

- Repository: D-sorganization/AffineDrift
- Working directory: C:/Users/diete/Repositories/AffineDrift-worktrees/claude-4596 (worktree)
- Branch: claude/issue-4596
- Baseline commit: 02507aac (origin/main)
- Implementation commit: SELF
- Pull request: not created yet (opening as draft in this session)
- Governing issue/epic: #4596 (epic #4604)

## Objective and Status

- Objective: In `.github/workflows/link-checker.yml`, make the scheduled external-link check
  report to a single tracking issue instead of only job logs, check DOI links through their
  doi.org redirect, and suggest an archive.org fallback for each dead link.
- Status: Implementation complete, tests passing; opening draft PR.
- Completed:
  - `scripts/link-checker.py`: added `is_doi_url()` and a `SafeRedirectHandler` so DOI links
    (which resolve via an HTTP redirect by design) are checked by following that redirect,
    safety-checked per hop against SSRF instead of being flagged broken on the 30x response.
  - Added `archive_org_suggestion()` and attached it to every external-URL warning.
  - Changed `check_file`'s external warnings from plain strings to structured dicts
    (`file`, `url`, `reason`, `archive_suggestion`).
  - Added `--json-report PATH` to `scripts/link-checker.py` to emit those warnings as JSON.
  - `.github/workflows/link-checker.yml`: changed the schedule from daily to weekly
    (`0 2 * * 1`), added `issues: write` permission, wired `--json-report` into the
    "Check external URLs" step, and added a "Report broken external links as a tracking
    issue" step that finds-or-updates a single open issue (marker comment + `ci`/`report`/
    `automation` labels) with the current broken-link table, and closes it once the report
    is empty.
  - Updated `docs/LINK-CHECKER.md` to document the weekly cadence, DOI handling, the
    archive.org suggestion, the tracking-issue behavior, and `--json-report`.
  - Added `tests/test_link_checker_script.py` (12 tests) covering DOI-domain detection, the
    archive.org suggestion format, DOI redirect-following (including the SSRF-blocked
    redirect case), the structured warning shape, and `--json-report` output.
  - Keyed SPEC.md change-log row to #4596.
- Remaining: none for this issue's acceptance criteria. The pre-existing "convoluted
  continue-on-error" in the internal-refs step (named in the issue's Problem section) was
  left untouched — it is not covered by an acceptance-criteria checkbox and changing CI
  failure semantics for internal refs is out of scope for this surgical change; noted as a
  follow-up opportunity in the PR body.

## Files and Decisions

- Files changed:
  - `scripts/link-checker.py`: DOI-aware redirect handling, archive.org suggestions,
    structured warnings, `--json-report`.
  - `.github/workflows/link-checker.yml`: weekly schedule, `issues: write`, tracking-issue
    upsert/close step.
  - `docs/LINK-CHECKER.md`: documented the new behavior and CLI flag.
  - `tests/test_link_checker_script.py`: new test file (script is hyphenated, loaded via
    `importlib`, mirroring the existing `tests/test_check_equations.py` pattern).
  - `SPEC.md`: added change-log row.
  - `docs/development/DEVELOPMENT_LOG.md`: added `DL-#4596`.
  - `docs/development/HANDOFF.md`: this entry.
- Key decisions:
  - Only `doi.org`/`dx.doi.org` links follow redirects; all other external links keep the
    existing `NoRedirectHandler` behavior (unrelated to this issue's acceptance criteria,
    so left as-is rather than expanded into a general redirect-following change).
  - The redirect handler re-validates every hop with the existing `is_safe_url` SSRF check
    before following it, since DOI targets are otherwise attacker-influenceable indirection.
  - The archive.org suggestion is a Wayback Machine lookup built as
    `https://web.archive.org/web/*/` followed by the dead link, not a verified/availability-checked
    snapshot — the acceptance criterion asks for a suggestion, not confirmed availability, and
    adding a second network call per dead link would slow the scheduled job for no required benefit.
  - The tracking issue is identified by an HTML-comment marker in its body plus the existing
    `ci`/`report`/`automation` labels (all already used elsewhere in the repo), rather than
    minting a new label.
- Working directory: C:/Users/diete/Repositories/AffineDrift-worktrees/claude-4588
- Branch: claude/issue-4588
- Governing issue/epic: #4588 (epic #4594 "[E12] Editorial Voice and Plain-Language Standard")
- Pull request: not yet created at the time this section was written (draft PR opened in the same session; see PR link in the commit that follows)

## Objective and Status

- Objective: keep the five internal governance/critique-apparatus words ("governed", "qualified", "provenance", "protected", "fail-closed") out of reader-facing prose — replace with plain language or a glossary link — and add a CI lint that warns (then eventually blocks) on new occurrences outside the evidence/developer surfaces.
- Status: **partial / Blocked**. Infrastructure (lint + glossary) is complete and CI-wired in warn mode. Content remediation is complete on the hub/entry reader pages (`pages/`, `resources/`, `books/`, and the non-`programming/` `models/` boilerplate) but **not** on the bulk of the deep scientific-chapter corpus under `articles/` (roughly 90+ files, ~180 remaining occurrences) or on a cluster of evidence/protocol-specification pages under `models/` (`active-impedance-identification.qmd`, `bilateral-hand-wrench-validation.qmd`, `hybrid-impact-contact.qmd`, `model-ladder.qmd`, `equipment-individual-response.qmd`, `research-protocol-readiness.qmd`, `neural-timing-feedback.qmd`, `population-generalization.qmd`) that read as evidence-tier documents despite their directory location.
- Why partial: the issue's acceptance criterion ("at least a 75% reduction on reader pages") requires rewriting dense, precise scientific/methodological prose across the textbook chapter corpus. Doing that correctly needs a consistent plain-language standard, which is the explicit subject of the still-open prerequisite issue **#4587 "[WEB-12.1] Write the Editorial Style Guide"** (listed first in the epic, `tier:strong`/`judgement:design`). Rewriting ~180 occurrences across ~90 chapter files without that standard risks inconsistent terminology and, more importantly, risks silently changing precise methodological claims in peer-review-style scientific prose — exactly the kind of judgment call CLI-tier agents are asked not to guess on. Measured against the lint's own scope (reader-facing `.qmd` under `articles/`, `books/`, `models/`, `pages/`, `resources/`, excluding `articles/_generated/` and `models/programming/`), occurrences dropped from 303 to 252 (~17%); within just `pages/` + `resources/` + `books/` + top-level `models/` (excluding the evidence-tier protocol cluster above), the reduction is close to 100% (`resources/` and `books/` are now fully clean; `pages/` only retains the glossary page itself and CSS class-attribute mentions, both deliberate).
- Completed:
  - TDD: `tests/test_check_governance_vocabulary.py` (19 tests, written first, RED confirmed against the missing module before implementation).
  - `scripts/check_governance_vocabulary.py`: scans `articles/`, `books/`, `models/`, `pages/`, `resources/` (`.qmd` only), excluding `articles/_generated/` and `models/programming/`, for the five terms; baseline-gated like the existing `scripts/check_terminology.py`.
  - `config/governance-vocabulary-baseline.json`: grandfathers the 252 remaining occurrences (the deep chapter corpus, the evidence-tier `models/` protocol cluster, the glossary page itself, and incidental CSS-class/URL matches that are not reader-visible prose).
  - `pages/glossary.qmd`: new plain-language glossary for the five terms, linked from `pages/notation.qmd`.
  - Content edits reducing or removing the five terms on: `pages/overview.qmd`, `pages/collaborate.qmd`, `pages/tools.qmd`, `pages/tangent-hyperplanes.qmd`, `pages/technology.qmd`, `pages/development-roadmap.qmd`, `pages/drifter-manifesto.qmd`, `pages/notation.qmd`, `resources/articles.qmd`, `resources/learning-path-golf-science.qmd`, `resources/learning-path-biomechanics.qmd`, `resources/learning-paths.qmd`, `resources/research-review-induced-acceleration-analysis.qmd`, `resources/resources-software.qmd`, `books/index.qmd`, `books/roadmap.qmd`, `books/human-motor-control.qmd`, `models/models.qmd`, `models/models-opensim.qmd`, `models/models-myosim.qmd`, `models/models-pinocchio.qmd`, `models/models-mujoco.qmd`, `models/models-drake.qmd`, `models/models-simulink.qmd`.
  - `.github/workflows/ci-standard.yml`: new "Verify Governance Vocabulary Stays Out of Reader Prose" step, `continue-on-error: true` (warn mode per the acceptance criterion), matching the existing MATLAB Quality Check warn-mode precedent.
- Remaining (recommended follow-up, likely as one or more new issues once #4587 lands):
  1. Write the editorial style guide (#4587) — a prerequisite for consistent chapter-level rewrites.
  2. Rewrite the `articles/` chapter corpus (proximal-distal energy-transfer/companion chapters, tangent-hyperplanes series, Geometry of Motion / Physics of Golf textbook chapters) against that standard, removing baseline entries as each file is cleaned.
  3. Decide whether the `models/` evidence-tier protocol cluster listed above should be reclassified as an evidence surface (like `critiques/`/`reports/`) and excluded from this lint's scope, or rewritten — a scope decision, not a mechanical one.
  4. Once the reader surfaces are clean, remove `continue-on-error: true` from the CI step to make the gate blocking, per the issue's second acceptance criterion.

## Files and Decisions

- Key decisions:
  - Reader-page scope = `articles/`, `books/`, `models/`, `pages/`, `resources/` per `docs/development/repository_inventory.md`'s existing reader/process split; evidence/developer exclusions = `articles/_generated/` (generated trust/critique annotations) and `models/programming/` (the programming-companion consumer docs), matching the issue's own "evidence and developer surfaces" language.
  - "Warn mode" implemented via the CI step's `continue-on-error: true` (the repo's existing precedent for MATLAB Quality Check), not a script-level flag, so promoting to blocking later is a one-line diff.
  - Baseline mechanism copied from `scripts/check_terminology.py` (`path::term` keys, no line number) rather than inventing a new grandfathering scheme.
  - Did not rename the `provenance-note` CSS component (`css/components/provenance-note.css`, used in `pages/tools.qmd`, `pages/drifter-manifesto.qmd`, `index.qmd`, tested in `tests/tools/test_design_primitives.py` and `tests/test_home_page_layout.py`, documented in `CONTRIBUTING.md`) — a CSS class name is not reader-visible prose, and renaming it is a separate CSS/design-system refactor outside this issue's scope.
- User-owned or unrelated worktree changes: none observed.

## Validation

- `pytest tests/test_link_checker_script.py` — PASS (12 passed)
- `pytest tests/test_link_checker_script.py tests/test_check_links.py tests/test_check_links_additional.py tests/test_link_utils.py` — PASS (79 passed)
- `python -m ruff check scripts/link-checker.py tests/test_link_checker_script.py` — PASS
- `python -m black --check --line-length 100 scripts/link-checker.py tests/test_link_checker_script.py` — PASS
- `python -m scripts.check_spec_changelog` — PASS

## Blockers and Risks

- Blockers: none.
- Risks/assumptions: the tracking-issue step is exercised only via the workflow's scheduled/
  manual trigger in production GitHub Actions; it is not covered by a live integration test
  (no local GitHub API to test against). The JSON-report plumbing and issue-body construction
  logic were reviewed by hand against the existing `github-script` patterns in
  `ci-benchmarks.yml`/`spec-check.yml`.

## Next Steps

1. Push branch and open a draft PR referencing `Fixes #4596`; release the fleet lease.

---

- `python -m pytest tests/test_check_governance_vocabulary.py tests/test_check_terminology.py -m content_lint` — 52 passed.
- `python -m ruff check scripts/check_governance_vocabulary.py tests/test_check_governance_vocabulary.py` — PASS.
- `python -m black --check --line-length 100 scripts/check_governance_vocabulary.py tests/test_check_governance_vocabulary.py` — PASS.
- `python scripts/check_governance_vocabulary.py --root . --baseline config/governance-vocabulary-baseline.json` — PASS (0 new violations; 252 baselined).
- CI workflow YAML validated with `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci-standard.yml'))"` — OK.
- `python -m ruff check .` and `python -m black --check --line-length 100 .` — both clean repo-wide.
- `python scripts/check_root_hygiene.py` and `python -m scripts.check_spec_changelog` — both pass.
- Known pre-existing failure outside this change's scope: `python -m pytest -m content_lint` errors during collection on ~75 unrelated `*_rigor.py`/benchmark test modules with `ImportError: numpy.core.multiarray failed to import` (a scipy-compiled-against-NumPy-1.x vs. installed NumPy 2.x ABI mismatch in this local environment). Confirmed pre-existing and unrelated: none of those files are touched by this change, and the same import fails in isolation for a file this PR never edited (`tests/test_swing_plane_launch_rigor.py`).

## Blockers and Risks

- Blocker: full 75% reduction depends on the not-yet-written editorial style guide (#4587) for consistent chapter-level plain-language replacements, and on a scope decision about the `models/` evidence-tier protocol cluster. See "Objective and Status" above.
- Risk: none to existing functionality — all edits are prose/link-text changes plus new, additive tooling; no existing behavior was removed.

## Next Steps

1. Land #4587 (editorial style guide), then use it to drive chapter-by-chapter rewrites of the `articles/` corpus, removing baseline entries as each file is cleaned.

## Change Log

- `SELF` — Keep internal governance vocabulary out of reader prose; add warn-mode CI lint (#4588).

---

# Restore the Ten Excluded Browser Tests — Issue #4563

## Identity

- Repository: `D-sorganization/AffineDrift`, worktree `C:/Users/diete/Repositories/AffineDrift-worktrees/claude-4563`.
- Branch: `claude/issue-4563`, commit `SELF`. Pull request: to be opened as a draft by this session.
- Governing issue: #4563 (WEB-09.3, part of epic #4569 / E9 — Accessibility Conformance).

## Objective and Status

- Objective: `ci-standard.yml`'s Chromium E2E step `--grep-invert`-excludes ten test titles (added in
  #4126/#4141, diagnosed in #4140); remove the exclusion for every title whose defect is actually fixed,
  fix any defect that isn't, and never loosen a test to make CI green.
- Investigation found the ten titles split three ways:
  1. Two of the ten (`should render desktop home layout as a three-column grid`, `should toggle mobile
     sidebar sections`) no longer match any test title at all — PR #4200 already renamed/rewrote those
     tests for the single-column home redesign, so these two clauses in the exclusion regex have been
     dead weight (matching nothing) since 2026-09-05.
  2. Seven of the ten (`should meet WCAG AA text contrast in both themes`, `should show entry details
     when clicked`, `should navigate to articles page`, `should serve cached homepage when offline`,
     `should validate mobile menu button`, `should provide summary of all compliant elements`, `should
     allow a user to navigate from home to article and back to top`) have defects that were fixed in
     source by PR #4200 (dark-theme link/button contrast tokens, bibliography detail-panel class,
     back-to-top touch target, stale navigation/user-journey selectors) — confirmed by reading
     PR #4200's diff and the current state of `styles.css`, `css/tokens/colors.css`, `js/bibliography.js`,
     `service-worker.js`, and the three rewritten spec files, plus three subsequent site-wide a11y
     remediation PRs (#4139/#4206, #4207/#4208, #4209/#4210) that further extended contrast/axe fixes
     across every route. PR #4200 never removed the CI exclusion, so none of this was ever confirmed by
     an actual CI run of these tests.
  3. One of the seven above (`should validate mobile menu button`) had a second, independent defect in
     the *test* itself, found by reading `tests/e2e/touch-targets.spec.js`'s shared `checkTouchTarget`
     helper: at a desktop-width viewport, Bootstrap's `.navbar-toggler` is legitimately CSS-hidden
     (`display: none` above the `lg` breakpoint), so `elementHandle.boundingBox()` returns `null`; the
     helper counted that as a non-compliant 0×0 touch target rather than treating a non-rendered element
     as not applicable. This same bug is almost certainly the actual cause of the `55 non-compliant
     elements` reported by #4140's diagnosis for `should provide summary of all compliant elements`
     (that test walks every `button`/`a`/`input` on the homepage, many of which are legitimately hidden
     at any single viewport). Fixed by skipping null-bounding-box elements instead of flagging them;
     this can only turn existing false failures into skips, since a real 0-size *visible* element still
     returns a real (non-null) zero-size box and is still caught.
  4. The tenth (`matches visual snapshot`, 60 parametrized pixel-comparison cases in `visual.spec.js`)
     stays excluded. No baseline PNGs are committed anywhere in the repository (confirmed via `git
     ls-files` / `Glob`), so `toHaveScreenshot()` fails with "no baseline found" on every run regardless
     of whether the rendered site is correct. Generating correct baselines needs a `playwright test
     --update-snapshots` run on the actual fleet CI runner — this sandbox has neither `quarto` nor
     `docker` (both denied by this session's permission policy), and even if it did, this is a Windows
     sandbox, so locally generated screenshots would not byte-match the Linux runner's font metrics and
     would just fail immediately for a different reason. This is left excluded with an updated,
     accurate comment instead of guessed at.
- Status: draft PR to be opened with a `Blocked:` section covering item 4 above.

## Files and Decisions

- `.github/workflows/ci-standard.yml`: replaced the ten-title `--grep-invert` value with just `"matches
  visual snapshot"`, and rewrote the adjacent comment/TODO (which pointed at #4140, already closed) to
  explain the current state and point at #4563.
- `tests/e2e/touch-targets.spec.js`: `checkTouchTarget` now `continue`s (skips) on a `null` bounding box
  instead of pushing a `compliant: false` result, with a comment explaining why (see point 3 above).
- Deliberately did not touch `js/bibliography.js`, `styles.css`, `css/tokens/colors.css`,
  `service-worker.js`, or the already-rewritten `homepage.spec.js` / `navigation.spec.js` /
  `user_journey.spec.js` — their fixes are already on `main` from PR #4200 and later a11y PRs; re-editing
  them would not trace to anything this issue still needs.

## Validation

- `npx jest`: 429 passed, 19 skipped, 26 suites — unaffected by this change, run to confirm no
  regression from touching a `tests/e2e/*.spec.js` file (Jest does not execute `tests/e2e/`).
- `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/ci-standard.yml'))"`: parses cleanly.
- **Not run: the actual Playwright suite.** This sandboxed worktree has no Quarto-rendered `docs/`
  (`docs/**/*.html` is gitignored, built only by `quarto render`), and both `quarto` and `docker` are
  denied by this session's permission policy, so there is no way to render the site and run
  `npx playwright test --project=chromium` locally. Every claim above about which tests now pass is
  based on reading source and the merged PR #4200 diff, not on an observed pass. CI's own `e2e-tests`
  job (which does render the full site) is the first real execution of the restored tests — treat its
  result as the actual acceptance evidence for this issue, not this handoff.

## Blockers and Risks

- Blocker: cannot render the Quarto site locally (`quarto`/`docker` both denied), so this PR's core
  claim — that the nine restored tests pass — is unverified by this session. See `Validation` above.
- Risk: if CI's `e2e-tests` run turns up a real remaining failure among the nine, the fix belongs in the
  same area PR #4200 touched (contrast tokens, touch targets, bibliography JS, or the three rewritten
  spec files) — do not re-add the title to `--grep-invert` to make CI green.

## Next Steps

1. Push the branch and open the draft PR with `Fixes #4563` and a `Blocked:` section for the
   pixel-snapshot baselines (item 4 above), which need a follow-up on the fleet CI runner, not more
   source changes here.
2. Frontier review reads CI's `e2e-tests` result as the real pass/fail evidence for the nine restored
   titles, since this session could not run them.
3. If CI does turn up a genuine failure, fix it at the source named in `Risks` above and keep the
   exclusion removed rather than reverting it.

---

# Readability Measurement Tool — Issue #4591

- Repository: `D-sorganization/AffineDrift`, worktree `C:/Users/diete/Repositories/AffineDrift-worktrees/claude-4591`.
- Branch `claude/issue-4591`, commit `SELF`; pull request: to be opened as a draft by this session.
- Governing issue: #4591 (WEB-12.5, part of epic #4594 / E12 — Editorial Voice and Plain-Language Standard).
- Objective: `scripts/check_readability.py`, an advisory Flesch-Kincaid grade-level checker for
  lay blocks (`<section class="laymans-terms">` content), the `summary-plain` frontmatter field,
  and hub pages, excluding math/code/Markdown/HTML markup from the scoring text.
- Threshold: grade 10, taken from WEB-12.1's stated readability target ("lay block <= grade 10")
  and WEB-12.4's hub-page acceptance criterion, applied uniformly via `--threshold`. WEB-12.1
  itself (`docs/development/editorial-style-guide.md`) is still open (`tier:strong`, unmerged);
  this issue only needed the numeric target already stated in its issue body, not the finished
  guide document, so implementation proceeded rather than blocking on #4587.
- `summary-plain` and most named WEB-12.4 hub pages (a dedicated "Start Here" page, for example)
  do not exist yet; the checker is forward-compatible — it silently finds nothing for absent
  frontmatter fields or hub-page paths rather than erroring, and `--hub-page`/`ReadabilityConfig`
  let a later pass add pages as they're created.
- CI wiring mirrors the existing MATLAB Quality Check pattern in `ci-standard.yml`:
  `continue-on-error: true` plus an `upload-artifact` step (`readability-report.json`), so the
  check is advisory rather than blocking, per the acceptance criteria.
- Validation:
  - `python3 -m pytest tests/tools/test_check_readability.py --no-cov -q`: 33 passed.
  - `python3 -m ruff check scripts/check_readability.py tests/tools/test_check_readability.py`: clean.
  - `python3 -m black --check --line-length 100 scripts/check_readability.py tests/tools/test_check_readability.py`: clean (after one auto-format pass).
  - `python3 -m mypy scripts/check_readability.py --ignore-missing-imports --allow-untyped-decorators --disable-error-code no-any-unimported --disable-error-code misc --disable-error-code unused-ignore --disable-error-code no-any-return`: clean.
  - Manual run against the live repo (`python3 -m scripts.check_readability`) found 16/22 existing
    lay-block/hub-page passages currently over grade 10 — expected, since WEB-12.4's rewrite pass
    (the issue that will actually bring prose under the threshold) hasn't happened yet.
- Full project suite (`pytest --cov`, `npx jest`, `npx playwright test`) was not run in this
  session; the change touches only a new script, its test file, and one CI workflow step, with no
  behavioral change to any existing module.

## Next Steps

1. Open the draft PR (`Fixes #4591`) and let the frontier review pass judge the hub-page default
   list and the shared grade-10 threshold across all three layers, since WEB-12.1 only states the
   lay-block number explicitly.
2. Once WEB-12.1's style guide merges, revisit whether `summary-plain` or hub pages should get a
   different threshold than lay blocks.
3. No further implementation is planned from this session pending review feedback.
# Implementation Handoff — Build the Page Header Card Component (#4507)
# Implementation Handoff — Extend Personas to Include Curious Golfer/Coach and Student (#4488)

## Identity

- Repository: D-sorganization/AffineDrift
- Working directory: C:/Users/diete/Repositories/AffineDrift
- Branch: feat/web-01-3-extend-personas-4488
- Baseline commit: 69f9f9b8ee43c7cfd252ce1d7bd2f3ce9c5859a9
- Implementation commit: SELF
- Pull request: #4638
- Governing issue/epic: #4488 (epic #4496)

## Objective and Status

- Objective: Extend config/personas.yml with golfer-coach and student personas, provide structured routes (first page, 30-minute route, go deeper), generate persona cards include, state plainly that the site does not give swing instruction, and eliminate duplicated grid on learning-paths.qmd.
- Status: PR #4638 created, awaiting auto-merge
- Completed:
  - Extended `config/personas.yml` to define 8 personas including `golfer-coach` and `student`.
  - Added structured routes (`first_page`, `route_30min`, `route_deep`) for every persona with verified targets.
  - Added plain disclaimer to `golfer-coach` that AffineDrift does not provide swing instruction or swing coaching.
  - Created deterministic generator `scripts/generate_persona_cards.py` producing `_includes/generated/persona-cards.qmd`.
  - Updated `resources/learning-paths.qmd` to include `_includes/generated/persona-cards.qmd` and removed the duplicated "Choose a path" grid.
  - Updated `data/trust/claim_audit_inventory.json` evidence_paths to include the new include file.
  - Added comprehensive test coverage in `tests/test_persona_start_paths.py` (20 tests, all passing).
  - Regenerated claim audit evidence digests and verified all checks pass.
  - Keyed change-log row in `SPEC.md` to #4638.
- Remaining: Arm auto-merge and release lease.

## Files and Decisions

- Files changed:
  - `config/personas.yml`: Added golfer-coach and student personas, plus first_page, route_30min, and route_deep for all 8 personas.
  - `scripts/generate_persona_cards.py`: Deterministic include generator with `--check` support.
  - `_includes/generated/persona-cards.qmd`: Generated include file with persona cards and route links.
  - `resources/learning-paths.qmd`: Included persona cards and eliminated duplicated path grid.
  - `data/trust/claim_audit_inventory.json`: Added `_includes/generated/persona-cards.qmd` to evidence_paths.
  - `tests/test_persona_start_paths.py`: Extended test suite covering all 8 personas, routes, existence, disclaimer, and include generation.
  - `SPEC.md`: Added change-log row.
  - `docs/development/HANDOFF.md`: Updated durable handoff state.
- Key decisions: Canonical root-relative paths in YAML; generator converts paths to context-relative paths for includes; golfer/coach persona explicitly disclaims swing instruction.
- User-owned or unrelated worktree changes: none observed

## Validation

- `pytest tests/test_persona_start_paths.py` — PASS (20 passed)
- `python -m src.tools.site_link_gate` — PASS (0 errors)
- `python -m ruff check scripts/generate_persona_cards.py tests/test_persona_start_paths.py` — PASS
- `python -m black --check --line-length 100 scripts/generate_persona_cards.py tests/test_persona_start_paths.py` — PASS
- `python -m scripts.regenerate_claim_audit_evidence --check` — PASS
- `python scripts/check_spec_changelog.py` — PASS

## Blockers and Risks

- Blockers: none
- Risks/assumptions: none

## Next Steps

1. Monitor PR #4638 CI and auto-merge into main.

## Change Log

- `SELF` — Extend critique annotations to ZTCF and Proximal-Distal pages (#4524).
- 4c7a5d5f — Remove fragile third-party book cover media from resources-books and filter network ERR console noise (#4617).

---

# Website Review and Draft Board Backlog — 2026-09-29

- Repository: `D-sorganization/AffineDrift`, working directory `/home/user/AffineDrift`.
- Branch `claude/ecstatic-darwin-latmzr`, commit `SELF`; pull request #4485 (open).
- Objective: at the user's request, review the external "Comprehensive Technical & Architectural
  Review Summary", do an independent source-level review of the website, and draft epics and
  issues for Board review.
- Deliverable: `docs/development/website-improvement-draft-issues-2026-09-29.md` (moved from `reports/` per the AGENTS.md rule that development plans live in `docs/development/`), with 14 epics, 124 draft
  issues, 10 Board decisions, sequencing, success measures, and a map to existing open work
  (#4008/#4010/#4022-#4030, #4084-#4089, #4139/#4140 and others).
- No GitHub issues were filed. The drafts await Board approval. No site source, content, or code
  changed. The live site was not reachable from the review sandbox, so findings about rendered
  behaviour are marked "verify on live site".
- Validation:
  - `prettier --write` applied to the report.
  - Headings title-cased with `scripts.check_title_case.expected_title`.
  - Review follow-up: the WEB-06.2 packaging scope includes `src.core`, the WEB-06.10 viewer is planar-first, and WEB-07.3 dates must be verified by the owner rather than taken from Git.
  - `python3 -m scripts.regenerate_claim_audit_evidence --check` passes.
  - `scripts/check_root_hygiene.py` passes.
  - The report-scanning pytest subset passes: claim audit, trust surface, public-site manifest,
    render coverage, and e2e paths (67 tests).
- No development-log entry: this is planning only, with no governing issue yet. Entries should be
  created per epic once the Board files the issues.

## Next Steps

1. Done 2026-09-29: the Board accepted all 14 epics (#4496, #4505, #4514, #4521, #4530, #4543,
   #4552, #4560, #4569, #4579, #4586, #4594, #4604, #4610). 111 children are filed and 13 are held;
   the report's §6 records the epic numbers and the held items.
2. The owner decides D4 (canonical versions, one ADR per family), D7 (content licence) and D8
   (external review model) to release the 13 held items.

---

# Night Watch Pass — 2026-09-28

- Role: `night-watch`; branch `staff/night-watch-task-587ee0`.
- No open PRs and no simple-tier issues on AffineDrift this pass (all 6 open
  issues are epics/subepics — out of overnight scope per playbook).
- Docs compliance checklist: found two `DEVELOPMENT_LOG.md` entries stuck at
  `in_review` well past their PRs' merges — DL-#3904 (PR #4271, merged
  2026-09-08 as `c088f9d0`) and DL-#3903 (PR #4267, merged 2026-09-08 as
  `5aedc884`). Confirmed both squash-merge commits are ancestors of `main`,
  then flipped both entries to `shipped` with refreshed `Last verified` and
  `Next step`.
- No source, test, or article changes. Documentation currency maintenance
  only. Draft PR opened on branch `staff/night-watch-task-587ee0` targeting
  `main`.

## Next Steps

- None outstanding from this pass.

---

# Cartographer Pass — 2026-09-27

- Role: `cartographer`; branch `staff/cartographer-task-afa7bc`.
- Scheduled codemap-freshness pass (re-run after the 2026-09-27 CLI upgrade).
  Audited codemap posture against the playbook checklist:
  - `AGENTS.md` existed and already referenced `docs/codemap.md` and the
    freshness runbook, but neither existed — a dead-end for agents following
    the documented discovery path.
  - `docs/architecture/C4.md` was already present and CI-enforced
    (`architecture-map-contract.yml` + `scripts/architecture_map_contract.py`),
    last updated 2026-09-10 (#1595/#4363) — no gap there.
  - `.codemap/` was not in `.gitignore`.
- Added `docs/codemap.md` (points to `C4.md`, directory table, refresh
  mechanism, agent discovery path) and a `.codemap/` entry in `.gitignore`.
- Logged both the fix and a follow-up suggestion (staleness check for
  `docs/codemap.md` itself, best done with the shared
  `codemap-refresh-workflow.yml` template) in
  `docs/operations/cartographer-suggestions.md` — no bulk issues filed.
- No source, test, or article changes. Documentation/navigation maintenance
  only. Draft PR opened on branch `staff/cartographer-task-afa7bc` targeting
  `main`.

## Next Steps

- A follow-on pass could wire the drift check described in the cartographer
  suggestion log rather than re-deriving it from scratch.

---

No material handoff change — sanitation pass (branch/worktree hygiene, see
`docs/operations/sanitation/sanitation-2026-09-28.md`) is a separate fleet
lane from the corpus-review checkpoint below and does not alter its
continuation state.

---

# Paused After Merged Checkpoint — 2026-09-28

The user requested finishing the existing edits, merging to remote main and
pausing. All content edits are merged. Do not start another audit, rewrite or
issue unless the user resumes. Never create draft PRs. This section supersedes
historical continuation instructions below.

- Camera #4472, fitting #4474, green #4476 and ledger #4478 are merged.
  All edits are on main `e2cc43616f31993eea8173ebcbdd9fc6bb90217f`; ledger checked head
  `cfaa84c7` passed required CI 36400072252, including full-site browser,
  layout, visual-evidence and accessibility checks.
- Camera, fitting and green publication is verified at `1a8dd00b`: deployment
  36397339440 and CI 36397339445 passed; all 960 site cases and twelve reviewed
  route cases pass, zero severe axe findings. Exact evidence and the live
  camera-registry download match. Earlier cancelled camera deployment is not
  counted as success.
- Ledger deployment 36402704961 and post-merge CI 36402704969 were still
  running when this checkpoint was recorded. Ledger live publication is not
  claimed. The documentation merge may supersede those runs; if publication
  verification is later requested, inspect the latest inclusive deployment and
  compare the live PDF with the canonical committed bytes. No new audit is needed.
- Exact record: `reports/technical-review/2026-09-28-stop-checkpoint.json`.
- Ledger source/PDF: `aac4dbfd`; twelve canonical review paths and nine findings
  bound at `ad94b93f`. Complete Chapters 1 and 29 and wrapper own content were
  reviewed. Other 28 chapters are unchanged dependencies; historical review
  reports, dates and scientific scope are preserved.
- Final local suite: 5,626 passed, 29 skipped, 132 deselected, 92.88% coverage.
  Seventeen focused checks; 38 final boundary/hierarchy checks; content 131
  passed/four skipped; static and citation checks pass. Four browser cases pass;
  six display equations and 23 PDF pages visually inspected. Identical canonical
  PDFs contain 207 pages and all thirty numbered chapters.
- The first remote ledger test run found a deployment-output PDF wrongly listed
  as canonical review evidence. Removed the duplicate registry entry, retained
  the canonical PDF and both-copy receipt, and reran the full suite successfully.
- Four supplied-text-only agy Gemini 3.8 Flash calls supported this ledger review;
  lead independently adjudicated all suggestions. No delegated tools or bypass.
- The optional benchmark wrapper did not execute benchmarks because its
  environment lacked the configured timeout plugin. Its wrapper status is not
  measured performance evidence. No unrelated tooling task was started.
- Remaining: 144 sources awaiting full technical audit, plus whole-book
  reconciliation. Epic #4009 / corpus #4021 remains incomplete and paused.
- All intended product/review changes are committed. Preserve untracked local
  QA. Owned preview 8770 and Playwright camera-rigor are closed. After this
  documentation checkpoint merges, release ledger lease/presence and stop;
  do not create another checkpoint task or pursue deployment work unprompted.

---

# Current Stop Checkpoint — Ledger Review #4477

The user's latest instruction is to finish the existing edits, merge them and
pause the goal. Do not start another article, chapter, issue or rewrite.
Never create draft PRs. Historical sections below record earlier checkpoints;
this section supersedes their instructions to continue corpus development.

- Current branch: `fix/4477-ledger-rigor`. Green PR #4476 merged at
  1a8dd00b; its protected checks pass and its lease/presence are released.
- Scope: complete Chapters 1 and 29, wrapper's own opening/glossary and shared
  opening figure. Other 28 chapter sources and historical review reports remain
  unchanged. Full-book scientific reconciliation is still pending.
- Seventeen focused checks pass; seven archived provider hashes and NPZ
  consistency verified. Four supplied-text-only agy Flash calls completed;
  lead independently adjudicated findings. No delegated tool execution.
- Source/PDF frozen at aac4dbfd; twelve canonical evidence paths and nine findings
  bound to ad94b93f. Full suite 5,626 passed, 92.88% coverage; content
  131 passed/four skipped. Static checks pass. Four browser cases pass with
  zero severe axe findings; six display equations visually reviewed. The
  207-page PDF preserves all thirty chapters. Regular PR #4478 is open. The first remote Python run exposed a duplicate
  deployment-output PDF in the route evidence paths; removed that duplicate,
  keeping the canonical PDF and both-copy hashes in the frozen render receipt.
  Verify inclusive deployment of camera #4472, fitting #4474,
  green #4476 and this ledger correction; update this turnover before pausing.
- Current pending corpus count: 144 after binding three reviewed sources, plus whole-book reconciliation. Do not claim the
  broader goal is complete.
- Preserve all untracked QA. Owned preview 8770 / Playwright camera-rigor are
  temporary review services; close them at final pause.

---

# Green Simulation Review — #4475

Current branch: `fix/4475-green-rigor`, based on club-fitting PR #4474.
Full corpus goal remains resumed. Never create draft PRs.

- Complete green-simulation article corrected under #4475, native child of
  #4021 / epic #4009. Nine grouped findings cover signed slip, rolling inertia,
  event/rest/capture semantics, surface geometry, probability, noise timing,
  anisotropic resistance, actual provider behavior and downstream inference.
- Sixteen exact provider source snapshots are indexed by revision and SHA-256.
  Tools 96ab281e and explorer af7f2682 retain discrepancies explicitly described
  in the article. No provider code or audited rolling-putt companion was changed.
- Four supplied-text-only agy Gemini 3.8 Flash calls completed in two pairs.
  Lead independently adjudicated every finding. No delegated tools or bypass.
- Sixteen focused checks pass (RED: ten numerical passes, six source failures).
  Final full suite: 5,609 passed, 29 skipped, 132 deselected, 92.88% coverage.
  Initial stale audit-digest failures were corrected and the full suite rerun. Content 131 passed/four skipped. Ruff,
  Black 724 files, mypy 91, tracked quality 761, citation/title checks pass.
- Four browser cases pass, zero severe axe findings. All 83 math expressions
  and eight display equations load; every display visually inspected at mobile
  and desktop widths. Tables scroll inside their wrappers; no document overflow.
- Review: reports/technical-review/green-simulation-review.md. Source frozen at 460a0192;
  five evidence paths and nine findings bound to 9f603f37. Remote main 994cd2be
  incorporated; next open a regular protected PR. No green PR yet.
- Club-fitting PR #4474 merged at 994cd2be (checked head 428a4561).
  Source 692b5a68; five evidence paths 4ec7a679. Deployment 36394993854
  and CI 36394993725 running. Fitting lease/presence released.
- Camera PR #4472 merged at 5fd2f8ab; CI 36392177961 passed. Its
  deployment 36392177929 was cancelled by the fitting merge. Verify both
  camera and fitting against the newer inclusive deployment before publication.
- Volume I PR #4470 and secondary-axis PR #4468 verified published; receipts
  are committed. No whole-book or whole-corpus completion claimed.
- Corpus: 147 pending full audits, plus whole-book reconciliation.
- Green lease technical-review-20260928-green expires 09:39 UTC. Preserve
  all untracked QA.
- Owned preview 8770 and Playwright camera-rigor remain active for green QA.

---

# Club-Fitting Review — #4473

Current branch: `fix/4473-fitting-rigor`, based on camera PR #4472.
Full corpus goal remains resumed. Never create draft PRs.

- Complete club-fitting article corrected under #4473, child of #4021 / epic
  #4009. Nine grouped findings connect spatial conventions, model interventions,
  shaft dynamics, mass identification and uncertainty to fitting decisions.
- Fixed the point-shift sign, mesh factors, centrifugal-load dimensions and
  bending/rotation coupling. Removed neural-causality and engine-interchange
  guarantees; all three JSON records are explicitly synthetic proposals.
- Four supplied-text-only agy Gemini 3.8 Flash jobs ran in two parallel pairs.
  Lead tested/adjudicated every finding; no delegated tools or permission bypass.
- Sixteen focused checks pass (RED: nine numerical passes, seven source/example
  failures). Full suite: 5,593 passed, 29 skipped, 132 deselected, 92.88% coverage.
  Content: 131 passed, four skipped. Ruff, Black 723 files, mypy 91 sources,
  title audit 638, tracked quality 760 and bibliography/citation checks pass.
- Quarto: four mobile/desktop light/dark browser cases pass; zero severe axe
  findings. All 89 math expressions and ten display equations load. Display
  equations visually inspected at both widths; JSON scrolls within code blocks.
- Review: reports/technical-review/club-fitting-review.md. Source frozen at 692b5a68; five evidence paths and nine findings bound
  to 4ec7a679. Render receipt: club-fitting-render-verification.json. Next complete
  a regular protected PR after merging remote main. No fitting PR yet.
- Camera PR #4472: source 98b37ee5, six-path evidence 40a26284, final head
  eaefc499. Merged at 5fd2f8ab on 2026-09-28 UTC. Deployment 36392177929
  and post-merge CI 36392177961 are running; publication verification pending.
- Volume I PR #4470 is verified published at 24c77a55. Deployment, CI and
  Compile pass. Live gate: 960/960 site cases and four reviewed-route cases,
  zero severe axe findings. Both immutable source/PDF downloads and all six
  evidence hashes match. Receipt: volume-one-reference-publication.json.
- Secondary-axis PR #4468 is verified published at 54d73e39; receipt committed.
- Corpus: 148 pending full audits, plus whole-book reconciliation. No whole-corpus completion claimed.
- Fitting lease technical-review-20260928-fitting expires 09:14 UTC. Camera
  and reference leases released. Preserve all untracked QA.
- Owned preview 8770 and Playwright camera-rigor are active for fitting QA.

---

# Camera Selection Review — #4471

Current branch: `fix/4471-camera-rigor`. Full corpus goal remains resumed.
Never create draft PRs. Issue #4471 is a native child of #4021 under epic #4009.

- Complete article and all 57 registry claims reviewed; corrected vendor modes,
  throughput assumptions, clock/exposure distinctions, geometric uncertainty,
  derivative noise and study-transfer limits. Prices and licenses remain
  unavailable where exact current evidence is missing. No hardware qualification.
- Four supplied-text-only agy Gemini 3.8 Flash calls completed in two review
  pairs; lead adjudicated suggestions. No delegated tools or permission bypass.
- Thirty focused checks pass. Full suite: 5,577 passed, 29 skipped, 132 deselected,
  92.88% coverage. Content: 131 passed, four skipped. Static checks pass.
- Four mobile/desktop light/dark browser cases pass, zero serious/critical axe
  findings. All 36 math expressions loaded; seven display equations visually
  inspected at both widths. Tables scroll horizontally within their wrappers.
- Review: reports/technical-review/camera-selection-review.md. Frozen source 98b37ee5; six exact evidence paths and nine findings
  bound to 40a26284. Render receipt: camera-selection-render-verification.json.
  Next merge remote main and open a regular protected PR. No camera PR yet.
- PR #4470 merged at 24c77a55; live publication and immutable reference/PDF
  downloads still require verification. Source/PDF 14b8f183, six-path evidence
  782dc161. PR #4468 is verified published at 54d73e39: all 960 site cases pass,
  12 reviewed-route cases pass, eight hashes match; secondary-axis-publication.json.
- Corpus: 149 pending full audits, plus whole-book reconciliation. Do not claim whole-corpus completion.
- Camera lease technical-review-20260927-camera expires 08:40 UTC; reference
  lease technical-review-20260927-volume-one-reference has been released.
- Preserve untracked QA. Stage explicit paths only. Preview 8770 and browser
  camera-rigor are owned by this session and still active.

---

# Volume I Reference Review — #4469

Current branch: `fix/4469-volume-one-reference`. The full corpus goal is resumed;
never create draft PRs. Preceding PR #4468 merged at 54d73e39 on 2026-09-28 UTC
with every check green; deployment and post-merge verification remain pending.

- Issue #4469 is a native child of #4021, under epic #4009. Session:
  technical-review-20260927-volume-one-reference; lease expires 07:50 UTC.
- Complete Volume I main source and public book map reviewed. Chapter inputs
  are unchanged; this is a bounded reference correction, not whole-book approval.
- Corrected controlled Jacobians, transport versus flow sensitivity, rotation
  branches, twist/wrench duality, coordinate/metric conventions, matrix and
  optimization hypotheses, and both executable examples. Fixed appendix labels,
  contents spacing and code placement in the 149-page PDF.
- Frozen source/PDF: 14b8f183. Six exact evidence paths: 782dc161. Reports:
  reports/technical-review/volume-one-reference-review.md,
  volume-one-reference-render-verification.json and
  volume-one-reference-dependency-carry-forward.json in that same directory.
  Other books retain historical scientific review dates and render revisions;
  shared dependency refreshes are recorded separately from new findings.
- Validation: 21 focused checks; 52 reference/audit contracts; full suite 5,561
  passed, 29 skipped, 132 deselected, 92.88% src coverage. Content: 131 passed,
  four skipped. Ruff, Black (729 files), mypy (91), titles (638) and quality
  checks across 758 tracked Python files pass. Changed print regions inspected;
  remaining header/enumitem warnings are outside the changed reference material.
- Public book map: four mobile/desktop light/dark cases, zero serious/critical
  axe findings. Immutable main-source and PDF links use the frozen source commit;
  older chapter/notebook links retain their explicitly separate snapshot.
- Four supplied-text-only agy Gemini 3.8 Flash calls ran in two parallel pairs;
  parent adjudicated all suggestions. Dispatcher #1800 still blocks unattended
  tool access. No tool/permission bypass; no fabricated physical validation.
- Next: merge remote main, open a regular PR, complete protected CI/merge and
  verify deployment, full site receipt and frozen downloads. Also record #4468
  publication after deployment. Latest secondary evidence is 919f6d18.
- Corpus: 150 full audits remain, plus whole-book reconciliation. Next read-only
  triage identified camera-specification discrepancies in the markerless mocap
  article; no new issue or implementation has started for that article.
- Preserve older untracked QA and stage explicit paths only. Owned browser and
  preview sessions are stopped.

---

# Secondary-Axis Review — #4467

Worktree: `C:/Users/diete/Repositories/AffineDrift-technical-review`.
Branch: `fix/4467-secondary-axis`, including remote main e48c9e00.
The complete corpus goal is resumed; never create draft PRs.

- Biology #4463 is published through PR #4464 at 855b6fa6. Its publication
  receipt verifies deployment 36378430500, artifact 10952174815, 960/960 site
  cases and frozen source/PDF downloads.
- Contraction #4465 merged through PR #4466 at e48c9e00; lease/presence released.
  Excluded development routes remain excluded/redirected.
- #4467 corrects the complete article and both critiques: free/forced spin,
  moving origins, inertia, gravity, impulse response and unsupported equipment
  inference. Both critiques are responded, without empirical resolution.
- Source/annotation checkpoint 3a136679; evidence checkpoint 33a8c83a binds
  eight exact paths for three full route reviews and ten findings. Reports are
  secondary-axis-review.md and secondary-axis-render-verification.json under
  reports/technical-review/. The atlas authority hash changes but its projection
  is unchanged; the derived research-release digest follows that dependency.
  Other generated critique headers change without new unrelated-page reviews.
  Static CI identified an unqualified related-reading ZTCF acronym; the caption
  now declares pointwise/forward scope. Its separate navigation receipt verifies
  that this is the only source change since the full mathematical/render review.
- Validation: 19 mechanics/source checks; full suite 5,540 passed, 29 skipped,
  132 deselected, 92.88% src coverage; 80 final audit/mechanics contracts pass.
  Browser 12/12, axe severe findings zero; 117 math expressions loaded and all
  17 display equations checked at both widths. Ruff, Black, titles and mypy pass.
- Six supplied-text-only agy Gemini 3.8 Flash calls ran in three parallel pairs.
  Lead adjudicated every suggestion; no tool/permission bypass. Dispatcher #1800
  still blocks unattended agy tool access.
- Active session technical-review-20260927-secondary; lease expires 07:05 UTC.
  Regular PR #4468 is open with protected auto-merge armed.
  Next complete CI/merge and verify live publication.
  Stage explicit files; preserve old untracked QA and close owned preview sessions.
- Corpus index: 152 full audits remain, plus whole-book reconciliation.
  Continue after this batch; the complete goal is not achieved.

---

# Contraction Workspace Review and Biology Publication Follow-Up

Current branch: `fix/4465-contraction-workspace`; worktree:
`C:/Users/diete/Repositories/AffineDrift-technical-review`.
The user resumed the complete corpus goal and authorized parallel agy Gemini
3.8 Flash assistance. Never create draft PRs. No pause is currently requested.

- Biology PR #4464 merged to remote main at
  `855b6fa6e3e7c2eeb764452ac77b45b1fe24e926`; all required PR checks passed.
  Deployment 36378430500 succeeded; the publication receipt above verifies it.
- #4465 corrects the complete contraction development manuscript, consolidated
  QMD, all eight chapters and hub. These eleven indexed sources are excluded
  from production rendering; their old routes redirect to the newer series.
  No route activation, destination-series clearance or new public PDF is claimed.
- Scientific corrections cover regional contraction, control-affine Jacobians,
  finite-horizon LQR/DDP, strict metric bounds, coordinate Hessians, task-rank
  deficiencies, LMI signs, sampling gaps and biological/contact assumptions.
  All 32 LaTeX equation labels are preserved.
- Fourteen focused tests pass after six source RED failures. Full suite: 5,519
  passed, two temporary root-hygiene failures, 29 skipped, 132 deselected; 92.88%
  src coverage. Moving Playwright logs under development QA resolves both;
  all six hygiene tests pass. Content lint: 131 passed/four skipped. Ruff,
  Black (727 files), title audit (638 sources), mypy (91 sources) pass.
- Native MiKTeX builds a 15-page preview with no overfull/undefined-reference
  warnings; all pages visually checked. Built-in compiler unavailable due to
  host standard-directory error. Ten Quarto previews and twenty light-theme
  mobile/desktop cases pass. No dark-theme or axe claim for these local previews.
- Six supplied-text-only agy Gemini 3.8 Flash calls handled inventory, arithmetic
  and final consistency in parallel pairs. The lead adjudicated all suggestions.
  No permission bypass; dispatcher #1800 still blocks unattended tool access.
- Reports: `reports/technical-review/contraction-workspace-review.md` and
  `contraction-workspace-render-verification.json`. Local PDF/screenshots/logs
  remain in `docs/development/technical-review/`; stage explicit product paths.
- Regular PR #4466 merged at e48c9e00; its lease/presence are released. Citation keys were
  aligned with the shared bibliography after the structural CI gate found five
  uses it could not resolve. Native compilation and the structural gate pass (excluding an old untracked generated LaTeX preview).
- Next: continue the
  corpus. The current CSV count is 154 full audits pending, plus whole-book
  reconciliation. Do not infer completion from this batch or a passing site gate.


---

# Biology Model Selection: Source Checkpoint for #4463

Current branch: `fix/4463-biology-model-selection`; worktree:
`C:/Users/diete/Repositories/AffineDrift-technical-review`.
The user has resumed the complete corpus goal. Never create draft PRs.

- Publication metadata PR #4462 merged at `f3593142cef875a2e43372fa712998a2a4c6d637`.
  The branch includes remote main. The parent #4021 lease was released; child
  #4463/session `technical-review-20260927-biology` owns this correction.
- Complete Volume III Chapter 1 and its contradictory introduction are corrected:
  augmented flexibility, power-consistent muscle forces, task/force redundancy,
  feasible dynamics, mass accounting and spatial inertia, conditional input affinity.
- Existing anthropometric coefficients are retained only as an explicit erroneous
  accounting example; the replacement exercise is synthetic, not de Leva data.
- RED: six source failures and eight passing numerical fixtures. GREEN: 14 focused
  checks. Root Ruff, Black (726 files), title audit (638 sources), and CI-equivalent
  mypy (91 sources) pass. Final full Python run: 5,507 passed, 29 skipped,
  132 deselected, 92.88% src coverage. Content lint: 131 passed, four skipped.
  Initial audit-record failures were repaired; 67 focused checks also pass.
- Full Volume III PDF compiles (66 pages). Introduction page 3 and chapter pages
  9-17 visually inspected; title and long exercise equation repaired. Zero chapter
  overfull boxes or undefined references. Existing warnings elsewhere remain.
- Six supplied-text-only Gemini 3.8 Flash calls via agy assisted extraction,
  numerical-test/exercise preparation, and consistency review. Lead checked every
  adopted change. No permission bypass, file/tool delegation, or empirical evidence
  was supplied by those agents; dispatcher issue #1800 still blocks unattended tools.
- Source/PDF freeze: `3875b82d18d27078d6d0aa22fcfa4ca4acf65a58`. The
  public book map pins this freeze and passes four local browser cases with zero
  serious/critical axe violations. Seven scientific evidence files are byte-verified
  at `9df52f26f4b0fa4b5cccd30f267774c130096d8e`. The dependency carry-forward
  receipt preserves all six prior book records; only the biology route received
  a new technical/browser review. Generated audit metadata follows that source
  checkpoint. Next: open a regular PR, protected merge, and verify live publication.
  Continue the
  remaining corpus afterward; 165 full technical audits remain, plus whole-book reconciliation.
- Stage explicit files only. Old untracked QA is not product content. Fresh QA is
  under `docs/development/technical-review/biology-*` and `flash-biology-*`.

---

# Resumed Corpus Review and Verified Chapter 1 Publication

The user resumed the complete scientific-review goal on 2026-09-27 and authorized
parallel Gemini 3.8 Flash assistance through agy for routine work. Prior pause
instructions are superseded. Never create draft PRs.

- Worktree: `C:/Users/diete/Repositories/AffineDrift-technical-review`.
- Branch: `review/corpus-resume-20260927`; base main `bf78cb2a`; commit `SELF`.
- Corpus #4021 under epic #4009 remains open: 167 indexed source entries await
  complete technical audit, plus whole-book reconciliation. Do not infer completion
  from a passing publication gate or the shipped state of one chapter.
- PR #4451 merged at `530778efe12948d51b16fd96e7959e78ff0fb933`.
  Its checked final head `82b1a90410cc13e50d20c69a5d699f5a282953a4` and merge share
  tree `8398d0407f957d4dd395e86cfb8aee084098f305`. Every required workflow passed;
  CI Standard 35938311583 and post-merge CI 35940168938 succeeded.
- Source/render freeze `787fb5819204d637b2e5eeb5ad9b589fba07b389` remains intact.
  Final CI added explicit SI gravity naming and tolerant floating-point zero checks.
  The prior handoff's twelve-path comparison against 95b5c738 must therefore be
  superseded by final evidence revision 82b1a904, which matches all twelve current
  ledger digests at the merge and deployed descendant. No published argument changed.
- Successful deployment 36298955953 carries all twelve paths unchanged at
  `bf78cb2a537f851630199e26725687a1b95b21c9`. The live manifest matches that revision.
  Artifact 10925830179 archive SHA-256 was verified: live 960/960 across 240 routes,
  all four Chapter 1 viewport/theme cases, zero serious/critical axe violations.
  Receipt: `reports/technical-review/why-physics-publication.json`.
- Prior validation: local Python 5,538 passed; 92.9% src coverage and 79.22% with
  scripts; final correction 63 focused and seven output-boundary/hygiene checks.
  Paired print/web review inspected Chapter 1 pages 32–41 of the 529-page PDF;
  103 expressions rendered, with keyboard-accessible wide math and figure.
  Preserve original frozen scientific and render reports.
- Parent session `technical-review-20260927-resume` holds corpus #4021 lease
  5862741342 and presence 5862741553 through 2026-09-28 05:25 UTC. Startup inbox
  was complete, without active peers/conflicts; nine historical warnings remain.
- Delegation: agy reports `gemini-3.8-flash-high` available. The fleet issue dispatcher
  currently refuses unattended agy tool use (#1800: no working permission allowlist).
  No permission bypass was used. Two parallel plan-mode, supplied-text-only Flash
  calls completed: longest-pending-source grouping and biology-chapter claim extraction.
  They had no filesystem/network tasks or editing authority. Their prompts/results
  are local QA under `docs/development/technical-review/flash-*.txt`; their assertions
  are advisory and require independent verification. In particular, nonlinear state
  dependence alone does not disprove input-affine dynamics.
- Next scientific candidate: Volume III Chapter 1, How Biology Differs From
  Engineering (3,891 indexed words). Complete source reading found mixed anthropometric
  coefficients, missing bilateral duplication, underdefined COM/inertia exercises,
  incomplete flexible-coordinate dynamics, unconditional excitation-affine claims,
  and unsupported engineering/biology generalizations. Confirm publication surfaces
  and primary sources, create a bounded child issue and fresh claim before editing.
- First publish this metadata closeout through a regular PR. Continue the full review
  afterward, prioritizing long substantive sources; preserve peer SPEC/log/history.
  Use Black 100, not Ruff format. Stage explicit paths only; old untracked helpers,
  render captures and logs are QA, not missing product commits. No local preview
  or CI watcher remains running from the previous session.

---

# Issue Remediator Pass — 2026-09-24

- Role: `issue-remediator`; run ID `fc83f2189fe2`; branch `staff/issue-remediator-task-467858`.
- Resolved four stale `in_progress`/`in_review` development log entries whose
  corresponding PRs had already merged:
  - DL-#4429 → `shipped` (PR #4453 merged 2026-09-24; issue #4429 closed)
  - DL-#4253 → `shipped` (PR #4423 merged 2026-09-22; epic #4253 open/deferred)
  - DL-#4406 → `shipped` (PR #4407 merged 2026-09-21; issue #4406 closed)
  - DL-#1595 → `shipped` (PR #4363 merged ~2026-09-10; RM#1595 addressed)
- Previous steward note about DL-#4429 is now resolved.
- No source, test, or article changes. Documentation maintenance only.
- Draft PR opened on branch `staff/issue-remediator-task-467858` targeting `main`.

## Next Steps

- A follow-on session may audit the remaining development log for any further
  stale entries as the corpus review advances.
- Open issues: all 8 remaining are epics or complex content audits — no
  low/medium complexity code issues are currently open.

---

# Current Technical Review Checkpoint — #4429

- Worktree: `C:/Users/diete/Repositories/AffineDrift/Worktrees/AffineDrift-4429`.
- Branch: `feat/4429-reconcile-audit-provenance`; base `origin/main` (`7a39e169`).
- Governing issue: #4429 (site-surface audit #4063; corpus #4021; epic #4009).
- Reconciles historical provenance of site-surface audit evidence across 12 canonical routes documented in `reports/technical-review/zero-torque-dependency-carry-forward.json`.
- Intervening diffs between baseline `0d2bd503a226cbbf7da1e87ce558952efe797d33` and HEAD across the 11 affected canonical routes were audited and verified as non-scientific link-gate additions (categories and related articles). Zero lines of scientific claims, derivations, or authority boundaries changed.
- Source revisions bound to committed checkpoint `63d98d19203049d3f52d44d071862fcbb1685147` where exact file bytes match HEAD.
- Render revisions preserved at `0d2bd503a226cbbf7da1e87ce558952efe797d33`.
- `ad-finding-notation-render-integrity` test symbol provenance verified; verification commit bound to `63d98d19203049d3f52d44d071862fcbb1685147` where all evidence paths and test symbols exist and pass.
- Manifesto notation correction #4428 and homepage #4063 preserved unchanged.
- Validation: 10/10 site trust surface audit tests pass; 18/18 claim audit inventory tests pass; `regenerate_claim_audit_evidence --check` passes.
- Reports: `reports/technical-review/site-surface-provenance-review.md` and `reports/technical-review/site-surface-provenance-reconciliation.json`.

# Prior Handoff Checkpoint — #4450 / PR #4451

- Worktree: `C:/Users/diete/Repositories/AffineDrift-technical-review`.
- Branch: `fix/why-physics-rigor`; base main `bdf47374`; current commit `SELF`.
- Regular PR: [#4451](https://github.com/D-sorganization/AffineDrift/pull/4451), open.
  Governing issue #4450 is a native child of corpus #4021 under epic #4009.
- Frozen source/render revision: `787fb5819204d637b2e5eeb5ad9b589fba07b389`.
  Six findings bind twelve paths, independently checked against committed bytes.
  Initial binding: `966d3187785c2e9cb9c6f13af38f423236be1dc1`.
  Final twelve-path verification: `95b5c738aaf9aded51530c1383da484ee9b1267f`; the only
  later scientific-evidence change is the CI-required Python constant naming.
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
  a full technical audit, plus whole-book reconciliation. The broader goal is
  paused at the user's request; never report the corpus complete prematurely.
- Coordination session: `technical-review-20260923-why-physics`. Previous lease
  5804272169 and presence 5804272400 expire 2026-09-24 00:51 UTC; release at
  this handoff. A successor must check ownership and acquire a fresh lease.
  Inbox was complete with no conflicts; seven historical identity warnings
  and two already-landed informational notices remain nonblocking.
- CI correction: static job 107425724858 required the conventional
  `GRAVITY_M_S2` name. The generator and independent tests now use that name
  with the same 9.81 value. Published source, figures and frozen render reports
  remain unchanged; live evidence digests track the revised Python files.
  All 63 mechanics/figure/audit cases pass, as does the code-quality checker
  on all 754 tracked Python files. Every trajectory array and both regenerated
  vector files exactly match the frozen output.
- GitHub CI on `570252198f3361006944a25b6cf9066c57a181ce`:
  CI Standard run 35934522768; static, JavaScript and website lint passed.
  Python job 107428571259 passed: 5,490 tests, 32 skips, 132 deselections,
  92.85% coverage; content lint 131 passed/four skips. E2E job 107428571258
  was still rendering the full site at the last snapshot. No review comments
  or requested changes were present. This handoff-only push creates a new CI
  head: inspect PR #4451's actual head rather than reusing an older success.
- Protected squash auto-merge is already armed through central
  `scripts/automerge_guard.py`. Leave branch protection intact. The PR may merge
  after this handoff; check current state before any further push.
- Successor steps: verify final-head checks and reviews; allow protected merge;
  fetch main and compare its tree to the checked head; verify all twelve evidence
  paths against `95b5c738aaf9aded51530c1383da484ee9b1267f`. Follow the exact main
  CI/deployment (or a verified descendant carrying those same bytes). Inspect
  the live revision manifest and live-every-page artifact: 240 routes × four
  viewport/theme cases, all four Chapter 1 results, zero serious/critical axe
  violations. Do not count a cancelled deployment as successful publication.
- Then create `reports/technical-review/why-physics-publication.json`, update
  DL-#4450 to shipped and both corpus rows, and merge a regular documentation
  PR. Preserve original source/render reports. No additional content work is
  authorized at this checkpoint. Never create a draft PR.
- Validation commands: `py -3.12 -X utf8 -m pytest --cov --cov-report=term:skip-covered`;
  `py -3.12 -X utf8 -m pytest --override-ini addopts= tests/ -m content_lint --timeout=120`;
  `npx --no-install jest --runInBand`; `python -m scripts.regenerate_claim_audit_evidence --check`.
  Browser and print recipes/results are in the frozen verification report.
- Stage explicit paths only. Preserve peer handoff/log/SPEC records and old frozen
  evidence. Existing untracked captures, helpers and logs are local QA, not
  unpublished product changes. The CI watcher and local preview are stopped
  for handoff; restart the preview only if another validation requires it.

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

| Work | Regular PR | Published Main | Deployment | Live Result |
| --- | --- | --- | --- | --- |
| Putting Roll | #4424 | `ded63640` | `35792227837` | 960/960 |
| Induced Acceleration | #4426 | `99aa5835` | `35796355561` | 960/960 |
| Zero-Torque Counterfactual | #4430 | `4fe70151` | `35802860809` | 960/960 |
| Manifesto Units and Scope | #4432 | `2ef5c908` | `35805142089` | 960/960 |
| Nonlinear Control Insights | #4433 | `66f63f87` | `35807652744` | 960/960 |

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

# Current Technical Review Checkpoint — #4428

Worktree C:/Users/diete/Repositories/AffineDrift-technical-review; branch
`fix/manifesto-notation-units`; commit `SELF`; regular PR #4432:
https://github.com/D-sorganization/AffineDrift/pull/4432.
PR4432 now targets main. PR4430 merged as4fe70151c4e6c7e9e86f38db02a70db5dd50447e;
its tree exactly equals checked head86ac900f (949d5fa81471776ca185b79f9b77ad3df4c09d7d).
Normal integration deaecd6b preserves the complete42f10e6f tree: six turnover/
audit conflicts retain the newer manifesto records, with no source or evidence
change. Its auto-merge is not enabled; wait for4430 live publication before
allowing the successor merge. Never create draft PRs.

Issue4428 is a native child of4063 under4021/4009. Our codex lease receipt
5786396346 expires01:49UTC Sep23. The coordination inbox returned incomplete
board evidence with malformed-comment/identity warnings; the issue claim still
identifies our active codex lease. No peer message or ownership transfer was
inferred from the incomplete result.

Complete manifesto index reread and correction are saved with review/render
reports. The source distinguishes Bu, inverse-inertia acceleration and full-state
Gu, retained flexible coordinates, state ordering, input-affinity and
memory/contact rules. Part5 describes the actual numerical verification
protocol; Part4 matches its current beam/pendulum scope. Eleven expressions
render in four browser cases; production4/4, title638 and internal links pass.
Page-local CSS restores reading-size display math in raw HTML. No model or
solver changed. Source/render remain frozen at2250d07f; all five findings bind
to it. Aggregate review binds to31664586. All13 route evidence maps match their
committed bytes. Twelve unchanged dependencies are carried forward only for the
shared audit/report update; #4429 preserves their historical provenance issues.
The28 inventory/site-audit tests pass again before opening4432.

PR4430 passed every required check, including the full browser/accessibility
job, and merged through protected auto-merge at00:37:21UTC Sep23. Deployment
35802860809 is in progress at4fe70151. Verify its live artifact (expected960/960
and eight corrected-route cases) before recording4427 shipped. No check was
bypassed. The manifesto branch includes its figure/glossary CI fixes. IAA4426 is
shipped at99aa5835 with live960/960. Active entries DL-#4428 and DL-#4427.
The whole development-log validator has pre-existing WIP/older-record defects;
do not claim a clean whole-log result.

The broader goal remains active. Next long article #4431 has not been claimed
or edited. Its issue now preserves checked physical replacement values, the
finite-difference energy balance and explicit control counterexamples. The
entire linked critique was read and has its own unsupported full-actuation,
reachability and necessary-efficiency claims; do not adopt those as facts or
silently close the governed critique. Primary transcript/source access and the
unavailable geometric-phase full preprint are recorded on4431. Claim and lease
before implementation after the current releases.

Disk headroom recovered to about1.9GB after earlier exhaustion. Previous
cleanup removed only verified untracked duplicate QA PNGs, preserving source,
PDFs, equation/endpoint images and JSON receipts. Stage explicit task paths;
many unrelated untracked QA helpers remain. Preserve unrelated planning records.

# Current Technical Review Checkpoint — #4427

Worktree C:/Users/diete/Repositories/AffineDrift-technical-review; branch
`fix/zero-torque-counterfactual-rigor`; commit `SELF`; regular PR #4430 open:
https://github.com/D-sorganization/AffineDrift/pull/4430.
Issue #4427 under Physics #4054/core #4058, corpus #4021 and epic #4009.
Complete chapter print/web and canonical article rewrite is qualified and saved.
Scientific/render evidence is frozen at e7d8c6885550ed2731843ff7d9e581d36b69788e:
14 findings, 11 exact committed evidence paths, 128 paired math expressions,
nine print pages, 26/16 web displays, 25/eight mobile scroll endpoints, local
production 8/8 and expanded overview four theme/width cases pass. Both routes
are reviewed again; the 219 original-route census is restored.

Thirteen site-audit dependencies are carried forward to457dbba2 after verifying
all unrelated evidence is unchanged from the accepted03db46ff baseline. The
changed manifesto intervention finding alone is rebound toe7d8c688. Historical
source/finding SHA discrepancies predate this work and are explicitly listed
in reports/technical-review/zero-torque-dependency-carry-forward.json, tracked
as #4429 under #4063. This is not a new review of those thirteen pages.
Manifesto notation units are separately tracked in #4428. Audit tests now check
exact bytes and valid separate revisions rather than requiring every finding,
source and aggregate review to share one historical SHA. Both old equality
assertions failed on this valid dependency refresh; replacement contracts pass.

Validation: 51 selected mechanics, ZTCF, inventory and site-audit tests pass;
Black100 and Ruff pass for all three affected test modules; title audit638 passes.
Use py -3.12 -X utf8 -m pytest tests/test_zero_torque_chapter_rigor.py
tests/test_ztcf_intervention_contract.py tests/test_claim_audit_inventory.py
tests/test_site_trust_surface_audit.py -q --no-cov. Normal hooks remain mandatory.
No adapter, fixture, schema, existing shared CSS or predecessor science changed.

IAA #4426 is shipped at99aa58356f45f4ff2bf15dd90dc735460dc8d3b4. Deployment35796355561
succeeded; artifact10725510305 passes960/960 and all four IAA chapter cases.
Receipt: reports/technical-review/induced-acceleration-publication.json. Putting is
shipped atded63640 with live960/960. Normal merge of origin/main99aa5835 preserves the complete fc5745ea tree;
the main tree equals our IAA parent03db46ff, so four turnover/index conflicts
retain the newer zero-torque records. No source or SPEC row changes.
Regular PR4430 is open. Python CI exposed two stale figure-census expectations after the deliberate
unsupported timeline removal; the corpus now has27 figured chapters,36 figures,
five TikZ figures and four unpaired figures. The23 figure-audit tests pass after
updating exact counts; no source or frozen scientific evidence changed.
The separate content_lint CI phase then exposed three old phrase assertions.
They now require the corrected capacity expression, retained activation and
feasible instantaneous ZVCF reset. The complete content_lint selection passes
locally with four skips (three unavailable Streamlit modules and the existing
missing latex-release workflow). No scientific source or frozen evidence changed.
Disk headroom fell below4MB: removed80 untracked duplicate ZTCF section
screenshots, retaining all equation/endpoints, overview/title, PDF and JSON evidence.
Next complete protected CI, merge it, and verify its
main deployment/live artifact before recording the zero-torque release as shipped.
No draft PRs. Goal remains active; entries advanced DL-#4427 and DL-#4425.

Disk headroom is very low due external activity. Removed seven untracked
counterfactual-spread draft PNGs only after confirming each final replacement;
final QA, source and evidence remain. Many older untracked QA files exist;
stage explicit task paths only. Preserve unrelated deferred-planning records.

# Current Technical Review Checkpoint — #4425

Branch `fix/induced-acceleration-rigor` now contains the complete paired Chapter30b
rewrite, nine new independent numerical checks, corrected bibliographies and a
review report explaining the argument and primary-source access limits. Twenty
numerical checks pass with the existing constrained tests; fourteen attribution
contracts pass with their explicit marker. All128 body math expressions agree.
All ten isolated print pages inspected, zero overfull/undefined/duplicate warnings.
The root public route passes four production cases; all139 browser expressions
render in each case. All18 desktop displays inspected and all11 wide mobile
expressions reach their horizontal endpoints. Eight corrected findings and all12 evidence paths are bound to9981bddf.
Three prior bibliography-dependent reviews were carried forward after every
other review/corrected-finding evidence path matched its prior commit and this
checkpoint exactly. The pre-existing open TOC finding remains unchanged.

Issue4425 is a native subissue of4054 under4021/4009. Lease/presence expire
23:44UTC September22. Read technical-review/induced-acceleration-preparation.md
and reports/technical-review/induced-acceleration-review.md for scope and limits.
The shared include and predecessor force/putting scientific evidence are unchanged.
The route is reviewed and the219-route census restored; publication is pending.

Putting regular PR4424 merged asded63640, tree-identical to checked head cd55cce8;
its source/render evidence remains frozen at a17f5ded. Force4421 merged as9ef76c6e.
Its first deployment35787101015 was superseded by planning PR4423; replacement
35789304756 at d9a8d08e succeeded. Live artifact10721968227 passes960/960 and
four force cases; publication receipt saved. Putting deployment35792227837 is pending; verify it before the next merge.
Normal integration a1197c03 preserves all scientific bytes and main SPEC order.
Preserve all planning work.

Disk space hit zero during derived screenshot assembly and checks. All tracked
JSON files parsed successfully afterward; no chapter source was truncated. Removed
only untracked downloaded PNG copies in six older CI artifact folders (about208MB),
retaining JSON evidence, source, frozen reports and current QA. Headroom continues
to fall due activity outside these small chapter outputs. Re-run interrupted checks;
never mark a partial check complete. Save and push checkpoints promptly.

Regular PR4426 is open and attached. All eight full textbook builds and Python3.12 tests passed. Static checks found an unnamed gravity literal in the new test; SELF extracts GRAVITY_M_S2 without numerical changes. All12 IAA evidence paths are verified at9981bddf; only the named test constant differs from06c948b7. Source/render bytes and bibliography carry-forward remain unchanged. The broad local quality scan includes untracked drafting helpers; its194 unrelated findings are not a clean-CI result. The tracked new test passes the same file checker.
Wait for putting deployment before enabling merge. Scientific/render source bytes remain frozen at06c948b7; the test-only evidence refresh is9981bddf. Evidence; update publication/turnover separately. This is analytical
chapter acceptance, not an empirical golf or full-book result. The goal is active.

# Deferred Validation Planning Checkpoint

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
- Next: publish through normal PR checks, verify default-branch plan artifacts,
  then post the immutable scope link on #4253 and record the audit receipt.
- Branch policy: current root CLAUDE/AGENTS and user-authorized topic-PR workflow
  target main; older GAAI staging guidance is superseded for this work.

- Integration: main `9ef76c6e` is preserved in full; conflict resolution keeps
  the force-measurement delivery and planning records. No article/model edits
  were made. Local disk exhaustion interrupted unrelated Design-Procedures
  tests; avoid broad local reruns until capacity is restored.

# Current Technical Review Checkpoint — #4422

Branch `fix/putting-roll-rigor` begins at force head 4047d917. SELF saves
the full putting rewrite, 15 independent passing numerical checks and four
production browser cases. Detailed equation/overview QA passes: all168 math expressions in four cases,
28 inspected desktop equations, all table contents, expanded accessibility and
scroll endpoints. SELF saves the complete scientific/render checkpoint before binding. Issue #4422 is claimed under #4059/#4021/#4009.
Lease/presence expire 23:09 UTC September 22. Inbox has no reported messages
or conflicts but is incomplete because of unrelated malformed board records.
See `technical-review/putting-roll-preparation.md` for derivations, source
access limits and the next steps. The route is reviewed with seven findings bound to complete checkpoint
a17f5ded. All five evidence paths match committed LF bytes; zero-deferred census
is restored. Final33 audit/mechanics checks pass; regular PR #4424 is open. Drive
protected checks and wait for force publication before enabling merge.

Delivery: superposition #4419 is shipped at 31cdc615; deploy 35782578807
and live artifact 10720600549 passed 960/960 cases. Publication record saved. Force #4421 merged as 9ef76c6e after all protected checks passed. Its tree
matches 4047d917 exactly; normal merge of origin/main retains the later putting
turnover where squash ancestry repeated predecessor text. Deployment35787101015 was superseded by the planning merge #4423; replacement
deployment35789304756 at d9a8d08e is pending. Save its publication record independently of frozen scientific evidence. Do not alter
force-bound files at 99d1653c; the putting article may reuse its scoped CSS.

The comprehensive review goal remains active. No draft PRs.

A disk-full event interrupted the first audit binding attempt. The committed
inventory was restored, six untracked reproducible research PDF downloads were
removed within this worktree, and binding was repeated with an atomic file
replacement. No tracked source or frozen evidence was lost. Disk headroom
remains low; monitor before additional rendering.

The following previously merged persona-work handoff is retained for its
separate scope; it is not the active technical-review task.

# Implementation Handoff — #4409

- Repository: `D-sorganization/AffineDrift`
- Working directory: `/workspace`
- Branch: `cursor/persona-start-paths-394f` (base `origin/main`)
- Pull request: https://github.com/D-sorganization/AffineDrift/pull/4411
- Governing issue: `#4409` (Persona start paths on learning-paths)
- Current HEAD: `d3b8e438`

## Objective and Status

- Objective: Add persona start paths (learner / researcher / integrator / experimentalist / reviewer / contributor) to `resources/learning-paths.qmd`, each routing to content clusters and exact-commit workflow pages.
- Status: **Implementation complete, awaiting CI**
- All local tests pass (14 persona tests + emoji heading test)
- CI workflows not triggering for commits after initial push (GitHub Actions issue)

## Completed Work

1. Created `config/personas.yml` with persona definitions:
   - 6 personas: learner, researcher, integrator, experimentalist, reviewer, contributor
   - Each maps to content clusters (from categories.yml)
   - Each maps to exact-commit workflows (from workflows.qmd)

2. Updated `resources/learning-paths.qmd`:
   - Added "Start by Persona" section with resource cards
   - Links to content clusters and workflow pages
   - No emojis in headings (repo style requirement)

3. Created `tests/test_persona_start_paths.py`:
   - 14 contract tests validating persona configuration
   - Tests pass locally

4. Updated `SPEC.md` with change-log row

5. Regenerated claim audit evidence

## Files Changed

- `config/personas.yml` (new)
- `resources/learning-paths.qmd` (modified)
- `tests/test_persona_start_paths.py` (new)
- `SPEC.md` (modified)
- `data/trust/claim_audit_inventory.json` (modified)
- `data/trust/generated/claim_audit_report.json` (modified)

## Validation (Local)

```bash
python3 -m pytest tests/test_persona_start_paths.py -v  # 14 passed
python3 -m pytest tests/test_formatting_lints.py::TestEmojiConsistency::test_learning_paths_headings_emoji_free -v  # passed
python3 -m ruff check tests/test_persona_start_paths.py  # passed
python3 -m black --check --line-length 100 tests/test_persona_start_paths.py  # passed
```

## Known Issue

- GitHub Actions workflows not triggering for commits after initial push
- First CI run (commit ca1db05f) completed with failures (expected - pre-fix code)
- Subsequent commits (aa45dcad, 2cf79129, 8b62f79e, d3b8e438) have not triggered CI
- This appears to be a GitHub Actions service issue

## Next Steps

1. Wait for GitHub Actions to recover and trigger CI for latest commit
2. Once CI passes, arm squash auto-merge
3. If CI continues to fail to trigger, may need to create a new PR

Integration checkpoint: merge planning main d9a8d08e into putting PR4424;
preserve both delivery records and all planning artifacts. Putting science and
frozen evidence are unchanged. Wait for the replacement deployment before merge.

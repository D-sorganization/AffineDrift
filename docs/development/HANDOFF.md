# Dataset Explorer Deployment Route Audit — #4688

- Repository: D-sorganization/AffineDrift; branch `fix/luna-deploy-route-4688`, based on protected main `3471f7d30245b688a62429726a3b2916442000d2`.
- Objective: restore the truthful claim-audit record for `/models/dataset-explorer.html`, which the deployment render emitted but the manually maintained route inventory omitted.
- Diagnosis: `_quarto.yml` selects `models/**/*.qmd` and the navbar links this source. The deployment render included `models/dataset-explorer.qmd` at [141/249], producing a 250-page manifest; the existing exact manifest/inventory gate correctly rejected the missing route. Earlier tests exercised generic coverage mismatch behavior but did not assert that this canonical source-derived route was represented. The on-ramp repair added its own route but did not reconcile this separate render-selected source.
- Review boundary: one route record is `reviewed`, with no direct claim IDs or critique IDs. This records an audit of the page's bounded content and evidence, not scientific validation. Dataset schema checks establish JSON structure only; population-generalization evidence is manufactured synthetic and does not authorize population claims; ZTCF and proximal-distal materials remain model-level/educational evidence, with human validation unclaimed. No new exemption, deferment, or finding was introduced. Existing open finding #4695 remains preserved; separate publication-gate follow-up #4694 remains outside this content repair.
- TDD: `test_canonical_inventory_covers_dataset_explorer_quarto_route` failed before the inventory update with `missing=['/models/dataset-explorer.html']`, then passed after the truthful record was added.
- Validation: focused claim-inventory/output-boundary/markdown-source/dataset-manifest/public-site-manifest contracts passed (44 tests); canonical evidence regeneration check and local inventory publication check passed. On the preserved v2 deployment-shaped output, canonical prune removed 27 internal artifacts; the deployment-argument public manifest contains 250 pages, binds source revision `3471f7d30245b688a62429726a3b2916442000d2`, and includes `/models/dataset-explorer.html`; `generate_claim_audit_inventory --manifest <manifest> --check --enforce-publication` passed with `verified 2 claim-audit report(s)`. The original native Quarto process exit is unknown (`exit_code: null`); artifact validation does not prove or rewrite that status. Root authorized these artifact checks, and no third render was run solely to recover the missing status.
- Next: root review and PR CI's actual render/publication gates; do not close #4688 before merged-main deploy evidence. No workflow changes, push, PR, or closure were made by this worker.

# Implementation Handoff — on-ramp route claim audit (#4492 follow-up)

- Repository: D-sorganization/AffineDrift; worktree `AffineDrift-worktrees/claude-onramp-audit`
- Branch: `claude/audit-on-ramp-paths`; commit SELF; PR: see branch
- Objective: Deploy Website failed after #4677 because `/resources/on-ramp-paths.html` had no
  claim-audit record. Added a reviewed record; every self-check quote was checked against its
  linked page. Open p3 finding (four "3 Hours" on-ramps sum to 120-140 min) tracked in #4695.
- A scan of every render-selected source (`_is_site_source`) found no other unrecorded route.
- Validation: `pytest tests/test_claim_audit_inventory.py tests/test_check_quarto_render_coverage.py` (29 passed).
- Next: confirm Deploy Website is green on main after merge; #4694 adds this gate to PR CI.

# "What's New" Feed RSS Validation — #4606 (WEB-14.4)

- Repository: `D-sorganization/AffineDrift`, worktree
  `C:/Users/diete/Repositories/AffineDrift-worktrees/claude-4606`.
- Branch `claude/issue-4606`, commit `SELF`; pull request:
  https://github.com/D-sorganization/AffineDrift/pull/4675 (draft, targets
  `main`).
- Governing issue: #4606 (WEB-14.4, epic #4610 / E14 — Reader Validation,
  Feedback, and Community). Acceptance criteria: "The RSS feed validates" and
  "Items link to revision history."
- **Status: partial / Blocked.** Implemented and shipped criterion 1 (the RSS
  feed validates). Criterion 2 (items link to revision history) is blocked on
  the still-open prerequisite **#4545 "[WEB-07.3] Real Dates and Per-Article
  Change History"**, which is the issue that introduces the `changes:`
  front-matter field and the per-page "Revision history" section this
  criterion's links would point to. Neither exists anywhere in the repository
  today (confirmed by grep across `*.qmd` for `changes:` front matter and a
  "Revision history" heading — zero matches). #4545 itself documents
  "Enables: 'What's new'", i.e. this issue is the documented downstream
  consumer of #4545, not an independent design decision this session can make
  up (the `changes:` schema and the anchor id/heading the revision-history
  section will render under are #4545's design, not #4606's).
- Completed (criterion 1, "The RSS feed validates"):
  - `scripts/generate_feed.py`: added `validate_feed_xml(xml: str) -> list[str]`,
    a structural RSS 2.0 validator (well-formed XML; rss element with
    version="2.0"; required channel title/link/description elements; every
    item element has a title or description, an absolute http(s) link
    element, a guid element, and an RFC-822-parseable pubDate element; no
    duplicate guid values across items). `main()` now calls it after
    building the XML and raises the new `FeedValidationError` instead of
    writing an invalid feed to disk — DbC: fail loudly at the boundary
    rather than silently publishing something a reader's feed client would
    reject.
  - This closes the actual gap: the generator already produced well-formed
    output in practice, but nothing enforced it, so a future regression (e.g.
    a frontmatter field with an unescaped value bypassing `escape()`, or a
    future edit dropping a required element) would have shipped to
    `docs/feed.xml`/`feed.xml` undetected. `deploy-website.yml` already
    invokes `scripts/generate_feed.py` on every deploy, so this check is now
    load-bearing in production without any workflow change.
  - TDD: `tests/test_generate_feed.py` — wrote `TestValidateFeedXml` (9 cases:
    valid-output, empty-item-list, malformed XML, wrong RSS version, missing
    channel title, missing/relative item link, unparseable pubDate, duplicate
    guids) and `TestMainValidatesBeforeWriting` (main() raises and writes
    nothing on an invalid feed) against the pre-existing module first,
    confirmed RED (`ImportError: cannot import name 'FeedValidationError'`),
    then implemented until GREEN.
  - Ran the generator against the real repository content
    (module invocation with an output path under a scratch directory): 30
    items, no validation errors — the live feed passes the new gate as-is.
- Not done (criterion 2, blocked): no `changes:` front-matter reading, no
  "Revision history" rendering, and no change to feed item link targets.
  Guessing at #4545's unimplemented schema/anchor here risks a second,
  conflicting implementation landing when #4545 itself ships. The optional
  "email digest through a privacy-respecting provider" named in the issue's
  Proposal (not one of its two checkbox acceptance criteria) was also not
  started, for the same reason plus its own unresolved provider-choice design
  question.

## Next Steps

1. Land #4545 (WEB-07.3): the `changes:` front-matter field and per-page
   "Revision history" section.
2. Once #4545's anchor/heading id is fixed, point each feed item's link
   at that page's revision-history anchor (or add a second, changelog-scoped
   feed sourced from `changes:` entries, per the issue's "dated changelog"
   proposal) and re-check criterion 2.
3. Decide (frontier/owner) whether the optional email digest is still wanted
   for this issue or should be split into its own follow-up, since it is not
   one of the two checkbox acceptance criteria.
# Manifesto Consolidation — #4592

- Repository: `D-sorganization/AffineDrift`, working directory: this worktree (`claude-4592`).
- Branch `claude/issue-4592`, commit `SELF`; pull request: not created yet at this commit
  (opening a draft PR immediately after).
- Governing issue: #4592 (WEB-12.6, part of epic #4594; `tier:cli`, `complexity:routine`).
- Objective: consolidate `pages/drifter-manifesto.qmd` ("Series Index") and
  `articles/drifter-manifesto.qmd` ("Single-File Edition") per WEB-02.4: declare
  one canonical page, correct the miscategorised `critique` label, and clearly
  label both pages Opinion.
- Completed work:
  - Added `opinion` to the controlled category vocabulary
    (`config/categories.yml`) and changed both pages' `categories:` from
    `critique` to `opinion`.
  - `pages/drifter-manifesto.qmd` (the navbar target and Series Index) now
    carries an explicit "Canonical page" note declaring it the canonical entry
    point for the Manifesto; `articles/drifter-manifesto.qmd`'s existing
    "Canonical Version" callout now explicitly says it is a non-canonical
    companion and labels itself Opinion, matching the "State: Opinion..."
    banner already on the series index.
  - Regenerated claim-audit evidence digests
    (`python -m scripts.regenerate_claim_audit_evidence`) for the files whose
    bytes changed; `--check` passes.
  - New test: `tests/test_editorial_and_consistency.py::test_manifesto_is_categorised_opinion_with_one_canonical_page`.
- Scope decision (recorded for the reviewing frontier agent): full physical
  retirement of `articles/drifter-manifesto.qmd` (redirects, deleting the
  duplicate single-file content) is WEB-02.4's own acceptance criterion, and
  WEB-02.4 itself is `tier:strong`/`judgement:contested`, requiring an
  owner-approved ADR per family. Retiring the file would also require
  rewriting roughly ten test files that assert directly against its content
  (`test_control_affine_scientific_trust.py`,
  `test_counterfactual_invariance_rigor.py`,
  `test_manifesto_flexible_foundations.py`, `test_mechanical_claim_contract.py`,
  `test_modal_pendulum_rigor.py`, `test_longform_mechanics_rigor.py`) plus the
  site's redirect/sitemap machinery (WEB-02.9). That is out of scope for this
  `tier:cli`/`complexity:routine` issue. This PR instead formalizes the
  canonical/non-canonical declaration already implicit in the site's internal
  linking (every other page already links to `pages/drifter-manifesto.qmd` as
  the entry point) without deleting content.
- Validation:
  - `python3 -m pytest tests/test_editorial_and_consistency.py -q` — 6 passed.
  - `python3 -m pytest tests/test_site_trust_surface_audit.py tests/test_claim_audit_inventory.py tests/test_claim_audit_output_boundary.py tests/test_page_style_discipline.py -q` — all passed.
  - `python3 -m pytest tests/test_control_affine_scientific_trust.py tests/test_counterfactual_invariance_rigor.py tests/test_manifesto_flexible_foundations.py tests/test_mechanical_claim_contract.py tests/test_modal_pendulum_rigor.py tests/test_longform_mechanics_rigor.py tests/test_formatting_lints.py tests/test_site_link_gate.py -q` — all passed.
  - `python3 -m pytest -q` (full suite) — all passed (only pre-existing skips).
  - `python3 -m ruff check .` and `python3 -m black --check --line-length 100 .` — clean.
  - `python3 -m scripts.regenerate_claim_audit_evidence --check` — passes.
  - `src.tools.site_link_gate.run_site_gate` — 0 errors, including the new `opinion` category.
- Next steps: none outstanding for this issue. If the reviewing frontier agent
  wants full retirement/redirect of the single-file edition, track that as
  WEB-02.4's per-family ADR work rather than folding it into this issue.
# Fixture and Dataset Explorer — 2026-09-30

- Repository: `D-sorganization/AffineDrift`, working directory
  `C:\Users\diete\Repositories\AffineDrift-worktrees\claude-4541`.
- Branch `claude/issue-4541`, commit `SELF`; pull request: to be opened this session (draft).
- Governing issue: #4541 (epic #4543, E6 — Interactive Models and Reproducibility). Objective:
  a browser viewer for `data/ztcf/*.json`, `data/population_generalization/`, and the
  proximal-distal snapshots that validates each file against its published schema and shows an
  accessible data table and a SHA-256 download.
- Completed work:
  - `scripts/generate_dataset_explorer_manifest.py` + `data/dataset_explorer_manifest.json`:
    generates the list of browsable fixtures per family, recording each fixture's declared
    `schema_version` and — only when a `*.schema.json` file actually exists in that family's
    directory — the schema path. Neither `data/population_generalization/` nor
    `data/proximal_distal_energy_transfer/` has a published schema today, so both are recorded
    with `schema_path: null` rather than a guessed or fabricated reference.
  - `js/dataset-explorer.js`: pure-logic engine — a dependency-free SHA-256 (FIPS 180-4) over
    fetched bytes, a JSON Schema validator covering the 2020-12 keyword subset actually used by
    `data/ztcf/ztcf_intervention_v1.schema.json` (type, const, enum, required/properties/
    additionalProperties, pattern, minItems/maxItems/prefixItems, minimum/exclusiveMinimum,
    anyOf/allOf/if-then-else, local $ref/$defs — not a general-purpose validator), a generic
    JSON-to-table flattener capped at 500 rows, and `describeSchemaStatus()` which reports
    `valid` / `invalid` / `unavailable` and never claims validation when no schema is published.
  - `js/dataset-explorer-ui.js`: fetches the manifest, then per family fetches its schema (if
    any) and each fixture, rendering a card per fixture with a status badge, an accessible
    `<table>` (caption, `scope="col"`/`scope="row"`), and a download link whose `<code>` shows
    the SHA-256 of the exact bytes served (computed once, reused for both the display and the
    downloaded `Blob`).
  - `css/dataset-explorer.css`, `models/dataset-explorer.qmd`: the page itself, with its own
    `## Related Articles` section (site link gate requires this on every non-hub content page)
    linking out to `models/population-generalization.qmd`, `articles/zero-torque-counterfactual.qmd`,
    `articles/proximal-distal-energy-transfer.qmd`, and `models/models.qmd`. Reachability into the
    page comes from a new `_quarto.yml` navbar entry (Build → Datasets → "Fixture and Dataset
    Explorer") rather than an edit to any of those articles — see Key decisions.
  - `scripts/sync_frontend_assets.py`: registered `dataset-explorer.js` and `dataset-explorer-ui.js`
    in `CANONICAL_JS_NAMES` so `test_every_canonical_javascript_module_has_a_deploy_sync_map` covers
    the two new modules.
  - `SPEC.md`: one change-log row keyed `#4541` (section 12); verified with
    `python3 -m scripts.check_spec_changelog`.
- Key decisions:
  - The issue's acceptance criteria ("validates ... against the published schemas") is honored
    literally: only `data/ztcf/` has a published schema in this repository, so only that family
    is validated; the other two families are explicitly labeled "schema unavailable" instead of
    a fabricated schema being invented for them. This matches the epic's own stated goal ("No
    button promises more than exists").
  - No general JSON Schema library (e.g. ajv) is bundled into the browser bundle; a small
    hand-rolled validator scoped to the keywords actually in use follows this repository's
    existing convention (see `js/rotation-converter.js`'s hand-rolled rotation math) and avoids a
    new third-party runtime dependency for a self-hosted light widget.
  - SHA-256 is computed client-side from the fetched bytes (not precomputed into the manifest),
    so the displayed digest can never drift from the file a reader actually downloads.
  - The new page is not cross-linked from existing narrative articles. This repo's claim-audit
    governance (`data/trust/claim_audit_inventory.json`) pins exact SHA-256 digests of
    `articles/zero-torque-counterfactual.qmd`, `articles/proximal-distal-energy-transfer.qmd`, and
    `models/population-generalization.qmd` as reviewed evidence for specific adjudicated claim
    records; editing any of them (even to add an unrelated cross-link) breaks that pin and fails
    `tests/test_claim_audit_inventory.py`. Those three edits were reverted. Instead, the site-gate
    orphan check (`check_orphans` in `src/tools/site_link_gate.py`) was satisfied by adding the
    page to `_quarto.yml`'s navbar (Build → Datasets). `_quarto.yml` is *also* pinned (as evidence
    for `/articles/proximal-distal-falsification-atlas.html`), but unlike the narrative articles a
    navbar-entry addition is not a scientific claim, and the repository has a sanctioned mechanism
    for exactly this case: `python -m scripts.regenerate_claim_audit_evidence` recomputes every
    pinned digest from the current tree and rewrites only the digest values in place (it never
    touches evidence paths, rationales, reviewers, or commits — see the script's own docstring and
    `tests/test_claim_audit_inventory.py::test_regenerate_patches_only_digest_values_and_keeps_ledger_formatting`).
    It was run once after the `_quarto.yml` edit, rewriting `data/trust/claim_audit_inventory.json`
    only.
- Compatibility constraints: none — purely additive; no existing schema, API, or CI config
  changed except the new manifest/generator, the `_quarto.yml` navbar entry, and the resulting
  claim-audit digest refresh.
- Validation commands and outcomes:
  - `npx jest` → 28 suites, 455 passed, 19 skipped, 0 failed (includes the two new suites,
    `tests/dataset-explorer.test.js` and `tests/dataset-explorer-ui.test.js`).
  - `python3 -m pytest tests/test_generate_dataset_explorer_manifest.py tests/test_claim_audit_inventory.py
    tests/test_claim_audit_output_boundary.py tests/test_sync_frontend_assets.py
    tests/test_check_single_title.py tests/test_site_trust_surface_audit.py` → 84 passed.
  - `python3 -m ruff check .` (repo-wide) → all checks passed.
  - `python3 -m black --check --line-length 100 .` (repo-wide) → 744 files unchanged.
  - `npx stylelint css/dataset-explorer.css` → clean.
  - `python3 -m scripts.check_spec_changelog` → passed (one row added, keyed `#4541`).
  - Site link gate (`scripts/link-checker.py --site-gate`) → "Site gate passed!" (orphan check now
    satisfied by the `_quarto.yml` navbar entry; no Related Articles or path-style violations).
  - **Not run locally:** `quarto render` and `npx playwright test` (14-minute full-site render is
    out of scope for this session per repo policy). The new page's HTML/CSS/JS were validated by
    the Jest suites and by reading the rendered `.qmd` structure against the existing
    `rotation-converter.qmd`/`bibliography.qmd` conventions it follows; CI's `e2e-tests` job is
    the first real render and axe-core pass for this page.
  - Pre-existing, unrelated to this change: `python3 -m scripts.check_tree_parity` reports 2 "NEW"
    LaTeX-only `glossary` divergences that `config/tree-parity-baseline.json` already documents as
    an accepted structural difference; the baseline-matching logic appears not to recognize them,
    but this predates and is untouched by this branch. Also pre-existing: `git status` shows
    `_includes/generated/evidence-presentation-summary.qmd` and
    `data/trust/generated/evidence_presentation_registry.json` as modified in this worktree from
    before this session started (unrelated generated-report drift); they were left untouched and
    are not part of this branch's staged diff.
- Blockers/risks: none identified for the acceptance criteria. Two family schemas
  (`population_generalization`, `proximal_distal_energy_transfer`) do not exist yet upstream; the
  explorer is honest about that rather than blocked by it. If those schemas are published later,
  re-run `scripts/generate_dataset_explorer_manifest.py` to pick them up automatically.
- Next steps: push the branch, open the draft PR (`Fixes #4541`), and watch CI's
  `quarto render`/Playwright lane and the full `pytest --cov` job for the new page and files.
# Implementation Handoff — Print and PDF Editions for Books and Core Series (#4550)
# Make the 404 Page and Empty States Useful — #4495 (WEB-01.10)

- Repository: `D-sorganization/AffineDrift`, worktree
  `C:/Users/diete/Repositories/AffineDrift-worktrees/claude-4495`.
- Branch `claude/issue-4495`, commit `SELF`; pull request: to be opened as a draft
  by this session.
- Governing issue: #4495 (WEB-01.10, epic #4496 / E1 — Audience Routing and
  Onboarding Funnel). Acceptance criteria: (1) the 404 page links Start Here,
  search, and the Library; (2) the contact address matches the About and
  Contact pages.
- Completed: fixed `404.qmd`'s broken-link `mailto:` address, which pointed at
  a personal Gmail account (`dieterolson@gmail.com`) while `pages/about.qmd`
  and `pages/contact.qmd` both use `dieterolson@AffineDrift.com`. Added
  `tests/test_404_page.py` (3 tests, written first and confirmed RED against
  the Gmail address) asserting the 404 page's contact address matches both
  pages and that no personal Gmail address appears on it.
- Investigated the rest of acceptance criterion 1 before touching `404.qmd`
  further:
  - **Search** — already satisfied. Quarto's default website navbar search box
    is enabled (no `search: false` override anywhere in `_quarto.yml`), and the
    existing 404 prose already tells readers to "Use the search box in the
    navigation bar".
  - **Top five destinations** — already satisfied. `404.qmd`'s `<nav
    aria-label="Helpful links">` already lists five links (Home, Article Index,
    Books & Textbooks, The Physics of Golf, The Geometry of Motion).
  - **"Start Here"** — not satisfiable yet. There is no `pages/start-here.qmd`
    or equivalent page in this repository. It is proposed in a separate,
    sibling issue, #4486 "[WEB-01.1] Add a 'Start Here' Page", which is
    `tier:strong`/`judgement:design` and still open.
  - **"the Library"** — not satisfiable yet. "Library" is not an existing page
    or navbar section; it is a proposed navbar grouping (Books, Series, Article
    Index, Companion Guides) from the unmerged WEB-02.1 "Restructure the Navbar
    Into Single-Purpose Menus" issue (also `tier:strong`/`judgement:design`,
    part of epic E2), per
    `docs/development/website-improvement-draft-issues-2026-09-29.md`.
  - Linking to either target now would mean fabricating a page or a navbar
    section under a tier:strong design issue's name — exactly the kind of
    judgment call CLI-tier agents are asked not to guess on. Substituting some
    other existing page under those labels (e.g. `pages/overview.qmd` for
    "Start Here") would be a silent, undocumented design decision, not a
    mechanical fix, so it was not done either.
- Status: **partial / Blocked**. Contact-address criterion is done. The
  Start Here / Library links cannot be added without either building
  `tier:strong` design work under this `tier:cli` issue or guessing at a
  substitute target; see the PR's Blocked section.
- Validation commands run in this worktree:
  - `python3 -m pytest tests/test_404_page.py -v` → 3 passed.
  - `python3 -m pytest tests/test_link_checker_script.py tests/test_check_links.py -q` → 31 passed (no broken-link regression from the edit).
  - `python3 -m pytest tests/test_404_page.py tests/test_public_site_content_hygiene.py tests/test_editorial_and_consistency.py -q` → 8 passed.
  - `python3 -m ruff check .` → all checks passed.
  - `python3 -m black --check --line-length 100 .` → all checks passed (no diffs).
- Not done / deferred: the "Start Here" and "the Library" links (see above);
  they depend on #4486 and the WEB-02.1 navbar restructure landing first.

## Next Steps

1. Once #4486 ("Start Here" page) and WEB-02.1 (Library navbar grouping) merge,
   add the two links to `404.qmd`'s `<nav aria-label="Helpful links">` list and
   close out the remaining acceptance criterion.
# Math Accessibility Verification — #4565 (WEB-09.5)

- Repository: `D-sorganization/AffineDrift`, worktree
  `C:/Users/diete/Repositories/AffineDrift-worktrees/claude-4565`.
- Branch `claude/issue-4565`, commit `SELF`; pull request: see PR opened from
  this branch against `main` (draft).
- Governing issue: #4565 (WEB-09.5, part of epic #4569 — E9 Accessibility
  Conformance). Objective: verify the site's `connect-src 'self'` CSP
  (`_includes/site-head.html`) does not block MathJax speech-rule locale
  fetches, and that lazy typesetting does not break screen-reader access to
  math, on three math-heavy pages.
- **Automated finding:** `_includes/mathjax-loader.html` only sets
  `enableAssistiveMml: true` — it never loads MathJax's `[a11y]/explorer`
  component or `speech-rule-engine`, so there is no code path today that
  fetches external SRE locale files for the CSP to block. Added a
  regression test for this in `tests/mathjax-loader.test.js`.
- Added an E2E test in `tests/e2e/accessibility.spec.js` ("math pages expose
  assistive MathML with no CSP-blocked speech/locale requests (#4565)") that
  loads `/articles/theory-part1.html`, `/articles/affine-nature-golf-swing.html`,
  and `/articles/The_Geometry_of_Motion/quarto/ch01_foundations.html`, waits
  for lazy MathJax typesetting, and asserts no CSP-violation console
  messages and no failed asset requests. Runs in CI's E2E lane (needs the
  full Quarto-rendered site); not run locally here because Quarto is not
  installed in this worktree environment.
- Filed findings and a manual test protocol at
  `docs/development/math-accessibility-verification-4565.md`.
- **CI review found a real bug, fixed here:** the new E2E test's first CI run
  failed for real — `/articles/theory-part1.html` (and the other math-heavy
  pages) still had Pandoc's legacy `cdnjs.cloudflare.com` ES6 polyfill script
  tag in `docs/`, which `script-src` blocks. `scripts/prune_internal_docs_from_deploy.py`
  already strips that tag, but `ci-standard.yml`'s `e2e-tests` job only ran
  the prune step *after* Playwright, so the un-pruned render is what
  Playwright actually tested. Fixed by moving the prune call into the "Sync
  Frontend Assets" step, before Playwright runs; the CSP was not widened.
  Also fixed a dead regex in the new `mathjax-loader.test.js` test
  (`speechrulengine` typo never matched anything) and made the new
  Playwright test tolerate `net::ERR_ABORTED` navigation noise instead of
  failing on any failed request.
- **Blocked:** the issue's first acceptance criterion requires an actual
  NVDA or VoiceOver screen-reader run with recorded results — a
  human-in-the-loop verification step (no screen reader installed here, no
  human available to transcribe speech output). See "What Could Not Be
  Verified" in the findings doc for the manual protocol a human tester
  should follow to close it. This is a `type:test` issue.
- `_includes/site-head.html` and `_includes/mathjax-loader.html` are
  unmodified; the one production-adjacent change is the `ci-standard.yml`
  step-ordering fix above.
- Validation commands run in this worktree:
  - `npm ci` (node_modules was absent in this worktree).
  - `npx jest` → 26 suites passed, 432 passed / 19 skipped, 0 failed.
  - `python -c "import yaml; yaml.safe_load(open('.github/workflows/ci-standard.yml'))"` → valid.
  - `npx playwright test tests/e2e/accessibility.spec.js --list` → new test
    registers correctly across all 5 configured browser projects (40 total
    entries); full run deferred to CI (requires a full site render).
- Next steps: a human (or a future session with NVDA/VoiceOver access) runs
  the manual protocol in `docs/development/math-accessibility-verification-4565.md`
  and records results as a comment on #4565 before that criterion can be
  checked off.
# Consolidate Inline "Recent" History Scripts — #4599

- Repository: `D-sorganization/AffineDrift`, working directory: worktree `AffineDrift-worktrees/claude-4599`.
- Branch `claude/issue-4599`, commit `SELF`; pull request: [draft #4625](https://github.com/D-sorganization/AffineDrift/pull/4625).
- Governing issue: #4599 (`WEB-13.5`, child of epic #4604 / E13), labeled `tier:cli`.
- Objective: replace the 15 duplicated inline localStorage "Recent X" history
  scripts across `models/models-*.qmd` and `resources/resources-*.qmd` with a
  single shared implementation in `js/history.js`, or remove the widget where
  it added nothing, per the issue's acceptance criteria.
- What changed:
  - `js/history.js`: added `initCategoryHistory()`, a shared category-scoped
    "recently viewed" tracker; refactored `updateHistorySidebar()` and
    `initArticleHistory()` to reuse new `createHistoryListItem()` /
    `createExploreArticlesEmptyState()` helpers instead of duplicating list-item
    and empty-state DOM construction.
  - `models/models-{drake,mujoco,myosim,opensim,pendulum,pinocchio,simulink}.qmd`:
    replaced each page's ~70-line duplicated inline `<script>` (all sharing the
    `affinedrift_models_history` storage key and the same 8-page `MODEL_PAGES`
    set) with a `<script type="module">` that imports and calls
    `initCategoryHistory()`. Behavior is unchanged (same storage key, page set,
    empty message, per-page fallback filename); only the implementation is
    now shared.
  - `resources/resources-{books,datasets,notebooklm,papers,researchers,software,videos,websites}.qmd`:
    removed the "Recent X" sidebar widget and its inline script. Each of these
    tracked only its own page under a page-unique storage key, so the widget
    could never show anything but the page the visitor was already on — a
    no-op feature, matching the issue's own diagnosis ("On the Datasets page
    it records only the page itself"). Switched `.standard-page-layout` to the
    existing `.standard-page-layout--single` two-column modifier (already
    defined in `styles.css`, previously unused by any `.qmd`) so the grid
    reflows to two columns instead of leaving an empty right column.
  - Added `tests/history.test.js` (25 cases covering `updateHistorySidebar`,
    `initArticleHistory`, `initCategoryHistory`) and `tests/home.test.js`
    (covering `js/home.js`'s collapsible-sidebar toggle) — both modules
    previously had zero Jest coverage, per the issue's second acceptance
    criterion.
- Validation:
  - `npx jest` — 27 suites, 445 passed, 19 skipped (pre-existing, unrelated).
  - `python3 -m ruff check .` — all checks passed (no Python changed).
  - `python3 -m black --check --line-length 100 .` — no diffs.
  - `python3 -m scripts.check_spec_changelog` — passed.
  - Not run: `quarto render` / Playwright E2E / `verify-public-site-visual.js`
    — full-site rendering is ~14 minutes per `CLAUDE.md` and wasn't required
    to validate a markup/script consolidation; `verify-public-site-visual.js`'s
    print-chrome check (`visible("#quarto-header, .left-sidebar, .right-sidebar")`)
    is satisfied by any one of the three selectors matching, and `.left-sidebar`
    is untouched on every affected page.
- SPEC.md: added the `#4599` change-log row. No other SPEC/DEVELOPMENT_LOG
  entries were touched besides `DL-#4599` below.

## Next Steps

1. None outstanding — acceptance criteria are met; awaiting reviewer merge.
- Removing the inline history script dropped `resources/resources-notebooklm.qmd` to 258 prose
  words, under the 300-word scaffolding threshold the script's text had been masking. Added a
  short, accurate usage caveat (machine-generated notes; external Google service) rather than a
  Planned badge, since the page is live content.

# Fix Programming-Companion Metadata and Repository Links — 2026-09-29

- Repository: `D-sorganization/AffineDrift`, worktree
  `C:\Users\diete\Repositories\AffineDrift-worktrees\claude-4542`.
- Branch `claude/issue-4542`, commit `SELF`; pull request not yet created.
- Governing issue: #4542 (`tier:cli`, epic #4543). Objective: no Programming Companion
  program or engine record renders its ID as its title, and every UpstreamDrift link in
  `repositories/*.qmd` is either SHA-pinned or explicitly labelled "navigation only".
- Root cause: `CatalogGenerator.generate_programs`/`generate_engines` read a `title` key
  that does not exist in the pinned UpstreamDrift companion manifest schema (the real
  field is `name`); every row silently fell back to the record's `id`. The programs
  table's `Engine` column had the same bug against a nonexistent `engine` key (real field
  `engine_id`). The engines table's `Maturity` column has no backing schema field at all
  (engines only carry `support_tier`), so it always printed "Unspecified"; removed it
  rather than inventing data.
- Completed work:
  - `src/affine_control/programming_companion/catalog_generator.py`: read `name` (not
    `title`) for program and engine rows; read `engine_id` (not `engine`) for the
    programs' Engine column; dropped the Engines page's fabricated Maturity column.
  - Regenerated `models/programming/programs.qmd` and `models/programming/engines.qmd`
    via `python -m scripts.generate_programming_catalog` (source: the active provider
    lock) so the committed pages match the fixed generator.
  - Labelled all 16 unpinned UpstreamDrift repository-root links across
    `repositories/*.qmd` (`repositories.qmd`, `repositories-2d-model.qmd`,
    `repositories-3d-model.qmd`, `repositories-drake.qmd`, `repositories-models.qmd`,
    `repositories-pinocchio.qmd`) with a visible "(navigation only; not pinned to a
    specific commit)" note, since these send readers to browse the live repository
    rather than citing a reviewed revision. Left existing `tree`/`blob`/`commit`
    SHA-pinned links untouched.
  - Refreshed the claim-audit evidence ledgers (`data/trust/claim_audit_inventory.json`,
    `data/trust/generated/claim_audit_report.json`) with
    `python -m scripts.regenerate_claim_audit_evidence` so their pinned digests match the
    edited files.
- Not in scope (flagged for follow-up, not fixed here): the programs table's `Kind`
  column reads a nonexistent `kind` key (real field `type`) and always prints `program`;
  the `Surfaces` column has no direct schema field at all (would need to be derived from
  cross-referencing each program's `feature_ids` against feature `surfaces`). Neither is
  named in #4542's acceptance criteria and both need a design call rather than a
  mechanical field-name fix.
- Validation:
  - `pytest tests/test_programming_companion_catalog_generator.py
    tests/test_repository_links_pinned.py tests/test_companion_pins.py
    tests/test_claim_audit_inventory.py -q` — all pass (new tests
    `test_program_titles_use_the_manifest_name_not_the_id`,
    `test_engine_names_use_the_manifest_name_not_the_id`,
    `test_every_bare_upstreamdrift_link_is_labelled_navigation_only`,
    `test_repositories_directory_has_at_least_the_known_bare_links` added).
  - Full `pytest` run: passes (exit 0; no failures or errors).
  - `ruff check` and `black --check --line-length 100` clean on every touched Python file.
- Blockers/risks: none known. Draft PR not yet opened as of this handoff; will update
  this entry's PR line once it exists.

## Next Steps

1. Open the draft PR (`gh pr create --draft`) and record its number/URL here.
2. Await frontier-agent review per the `tier:cli` lane.

# Implementation Handoff — Consolidated web PRs (2026-09-30)

- Repository: D-sorganization/AffineDrift; worktree `AffineDrift-worktrees/claude-consolidated`
- Branch: `chore/web-consolidated-2026-09-30`; commit SELF; PR: see branch (opened after push)
- Objective: land nine reviewed PRs (#4635, #4637, #4673, #4679, #4681, #4625, #4641, #4627,
  #4636) in one CI cycle under the consolidation policy (Repository_Management#1691).
- Decisions: HANDOFF/DEVELOPMENT_LOG merged by whole section; claim-audit counts summed
  (`/pages/*` #4063 = 20, reviewed batches = 226); `pages/notation-quick-reference.qmd`
  description shortened to 144 chars to meet main's 70-160 char rule (#4575).
- Validation: full non-slow suite 6147 passed; the two other failures under xdist
  (citation sample pages, generated-reports currency) pass in isolation.
- Next: after merge, close the nine originals as superseded by the consolidated PR.

# Implementation Handoff — Deploy Website route coverage (#4548 follow-up)

- Repository: D-sorganization/AffineDrift; worktree `AffineDrift-worktrees/claude-route-coverage`
- Branch: `claude/claim-audit-route-coverage`; commit SELF; PR: see branch (draft at open)
- Objective: Deploy Website's `--enforce-publication` gate failed on main after #4629 because
  24 newly rendered routes had no claim-audit record (22 `articles/*-bibliography.md`
  companions from #4548 plus `/pages/privacy-policy.html` and `/pages/accessibility.html`).
- Decisions: the 22 companion bibliographies are retired from the render (not marked
  reviewed: their `references_out_ids` are unverified and at least one repeats the ZTCF
  "total passive drift" overclaim). Their two linking articles now point at the GitHub source.
  The two policy pages were reviewed against the code and carry open p3 findings tracked in #4691.
- Validation: `pytest tests/test_claim_audit_inventory.py tests/test_check_quarto_render_coverage.py`
  (29 passed); `python -m scripts.check_quarto_render_coverage` passes.
- Next: after merge, confirm Deploy Website is green on main, then reopen #4548 to audit
  each bibliography route before re-adding the render rule.

# Implementation Handoff — Readable Claim Ledger Page (#4523)

## Identity

- Repository: D-sorganization/AffineDrift
- Working directory: C:/Users/diete/Repositories/AffineDrift-worktrees/claude-4523
- Branch: claude/issue-4523
- Baseline commit: 46df5059
- Implementation commit: SELF
- Pull request: #4637 (draft) — https://github.com/D-sorganization/AffineDrift/pull/4637
- Governing issue/epic: #4523 (epic #4530)

## Objective and Status

- Objective: Add a dedicated `evidence/claims.qmd` page, generated from the governed
  claim registry, with one accessible card per claim (plain statement, formal
  statement, evidence rung, falsifiers, related critiques, and the pages making the
  claim), and link every claim-making page back to its ledger entry.
- Status: merged forward onto `origin/main` (which renamed the DCR article to
  `articles/drift-control-ratio.qmd` in #4629); stale
  `controllability-drift-ratio` paths in this branch's generated include and
  handoff/log prose fixed to match. Reviewed and added claim-audit inventory
  records for the new `/evidence/claims.html` route so
  `scripts.generate_claim_audit_inventory --check --enforce-publication`
  (which PR CI does not run but Deploy Website on `main` does) does not break.
  Draft PR #4637 remains open for frontier review.
- Completed: New `scripts/generate_claims_ledger.py` generator (reusing
  `generate_trust_panels.load_registry`, `generate_claim_critique_ledger.load_ledger`,
  and the `evidence_presentation` projector/renderer for the evidence-rung badge);
  new `evidence/claims.qmd` page; generated `_includes/generated/claims-ledger.qmd`
  and per-page link partial `_includes/generated/claims-ledger/drift-control-ratio.qmd`;
  `articles/drift-control-ratio.qmd` now includes its generated ledger link;
  `evidence/**/*.qmd` added to the `_quarto.yml` render list; `evidence` added to
  `src/tools/site_page_scan.py`'s `CONTENT_DIRS` (and its pinned test) so the site
  link gate (categories, Related Articles, orphan check) covers the new page.
- Remaining: Frontier review of draft PR #4637.

## Files and Decisions

- Files changed:
  - `scripts/generate_claims_ledger.py`: New generator. `build_claim_cards()` projects
    `data/trust/claim_registry.json` (joined with `data/trust/claim_critique_ledger.json`
    for related critiques, matched via `related_claim_ids`) into card view models;
    `generate()` writes/verifies the ledger partial and one link partial per page that
    carries a `data-trust-claim` anchor naming that claim ID, or is a claim's
    defining page.
  - `evidence/claims.qmd`: New hand-authored wrapper page (front matter, authority
    boundary callout, reading guide, the generated include, a "Related Articles"
    section, and regeneration instructions).
  - `articles/drift-control-ratio.qmd`: Added a Quarto include of the
    generated `_includes/generated/claims-ledger/drift-control-ratio.qmd`
    partial, next to the existing scientific-trust-panel include. (Path updated
    2026-09-30 for #4629's rename from `controllability-drift-ratio.qmd`.)
  - `_quarto.yml`: Added `"evidence/**/*.qmd"` to the render list.
  - `src/tools/site_page_scan.py`, `tests/test_site_link_gate.py`: Added `"evidence"`
    to `CONTENT_DIRS` (and its pinned assertion) so the new page is checked for
    categories, Related Articles coverage, and orphan status like every other content
    directory.
  - `scripts/check_root_hygiene.py`: Added `"evidence"` to
    `ALLOWED_TRACKED_ROOT_DIRECTORIES`, since the new top-level `evidence/` directory
    otherwise fails the root hygiene allowlist check.
  - `data/trust/claim_audit_inventory.json`, `data/trust/generated/claim_audit_report.json`,
    `reports/scientific-claim-audit.md`: Added the new generated per-page link include
    to the DCR route's review evidence paths and ran
    `python -m scripts.regenerate_claim_audit_evidence` to refresh the bound digests,
    since editing `articles/drift-control-ratio.qmd` and adding its new
    included source changed the bytes the claim-audit ledger pins (the
    `claim-audit-evidence` pre-commit hook, AffineDrift #4124). Also added a
    reviewed `claim_audit_inventory.json` record for `/evidence/claims.html`
    itself (2026-09-30 route review, #4523).
  - `tests/test_claims_ledger.py`: New TDD suite covering card projection (plain/
    formal statement, rung, full falsifier list, related critiques, pages making the
    claim), accessible rendering (`role="region"`, `aria-label`, human-readable
    anchor), generator determinism, per-page link generation, and staleness detection.
  - `docs/development/DEVELOPMENT_LOG.md`: Added `DL-#4523`.
  - `SPEC.md`: Added the #4523 change-log row.
  - `scripts/claim_audit_ids.py`, `tests/test_claim_audit_inventory.py`: Bumped the
    deferred-scope/reviewed-batch counts to account for the new reviewed route.
- Key decisions:
  - Reused the existing `data-trust-claim` anchor convention (already present on
    `articles/drift-control-ratio.qmd`) to discover "pages making the
    claim," rather than inventing a new metadata field.
  - Reused `project_claim()`/`render_evidence_badge()` from
    `src/affine_control/evidence_presentation/` for the rung badge instead of
    duplicating the tier-to-label mapping, and reused `generate_claim_critique_ledger`'s
    private `_route`/`_title` helpers (generic path-routing and frontmatter-title
    extraction, not critique-specific) instead of re-deriving them.
  - The issue's acceptance criteria say pages must link to the ledger "through the
    WEB-03.4 block" (issue #WEB-03.4, a separate `tier:strong` "What This Shows /
    What It Does Not Show" component). That component does not exist yet anywhere in
    the codebase. This PR satisfies the literal criterion (every claim-making page is
    linked) with a small generated include today; when WEB-03.4 lands, that component
    can subsume or wrap this link.
  - `scripts/generate_sitemap.py`'s `SITEMAP_CONTENT_DIRS` does not include `evidence/`
    yet. Left out of scope (not required by #4523's acceptance criteria); flagged in
    the PR body as a follow-up.
- User-owned or unrelated worktree changes: none observed.

## Validation

- `pytest tests/test_claims_ledger.py` — PASS (10 passed)
- `pytest tests/test_claims_ledger.py tests/test_evidence_presentation.py tests/test_scientific_trust_metadata.py tests/test_claim_critique_ledger.py tests/test_site_link_gate.py` — PASS (96 passed)
- `python -m ruff check scripts/generate_claims_ledger.py tests/test_claims_ledger.py src/tools/site_page_scan.py tests/test_site_link_gate.py` — PASS
- `python -m black --check --line-length 100 scripts/generate_claims_ledger.py tests/test_claims_ledger.py src/tools/site_page_scan.py tests/test_site_link_gate.py` — PASS
- `python -m scripts.check_module_size_budget` — PASS (336 files scanned, no violations)
- `run_site_gate()` (`src/tools/site_link_gate.py`, the same check `scripts/link-checker.py --site-gate` runs in CI) — 0 violations across broken-links, path-style, related-coverage, chapter-bridges, orphans, categories (compared against `tests/link_gate_baseline.json`)
- 2026-09-30 (SELF): `pytest tests/test_claim_audit_inventory.py tests/test_check_quarto_render_coverage.py` and `scripts.regenerate_claim_audit_evidence` — see Change Log for outcome.
- Not run locally: `quarto render` (~14 min full-site render per `CLAUDE.md`) and the Playwright E2E/axe-core lane, which depends on it.

## Blockers and Risks

- Blockers: none.
- Risks/assumptions: Accessibility of the rendered page (axe-core, per the E2E lane)
  was not verified against a real Quarto render in this session — the markup follows
  the same `role="region"`/`aria-label`/semantic-heading pattern already used and
  tested elsewhere on the site (`render_evidence_card`), so it is expected to pass,
  but this is not confirmed end-to-end.

## Next Steps

1. Frontier review of draft PR #4637; if `quarto render` + Playwright axe-core surfaces
   an accessibility issue on `evidence/claims.html`, fix the markup in
   `scripts/generate_claims_ledger.py`.
2. Release agent lease for #4523.

## Change Log

- c090f480 — Add the reader-facing Claim Ledger page, its generator, and per-page links (#4523).
- c2bd47af — Merged `origin/main` forward (31 commits, incl. #4629's DCR rename), fixed
  stale `controllability-drift-ratio` paths, and added a reviewed claim-audit
  inventory record for `/evidence/claims.html` with one open finding (#4523).
- SELF — Marked that finding `corrected` with `verification_commit: c2bd47af...`
  now that c2bd47af is a real, landed commit containing the page fix (#4523).

# Parameters Page and Notation Quick-Reference Card — #4551

- Repository: `D-sorganization/AffineDrift`, worktree
  `C:/Users/diete/Repositories/AffineDrift-worktrees/claude-4551`.
- Branch `claude/issue-4551`, commit `SELF`; PR:
  https://github.com/D-sorganization/AffineDrift/pull/4627 (draft, targets
  `main`).
- Governing issue: #4551 (`[WEB-07.10]`, part of epic #4552), development log
  `DL-#4551`.
- Objective: render `PARAMETERS.md`, add a one-page printable notation
  quick-reference card, link core pages to notation from their header card,
  and remove `pages/notation.qmd`'s duplicate heading/manual table of contents.
- Completed:
  - `pages/parameters.qmd` (new): includes `../PARAMETERS.md`, `categories:
[reference]`, a Related Articles section.
  - `pages/notation-quick-reference.qmd` (new): condensed one-page printable
    card (control-affine form, canonical acronyms, core physical-quantity
    symbols, axis convention) that points back to `notation.html` as the
    normative source rather than duplicating its full prose definitions.
  - `NOTATION.md`: removed the redundant `## Mathematical Notation Reference`
    heading and manual `## Table of Contents` (the wrapper page already
    supplies the title and Quarto's sitewide `toc: true` already renders one).
  - `PARAMETERS.md`: removed the redundant top-level `# Canonical Parameters
    Reference` heading for the same reason, so the new wrapper page does not
    reintroduce the defect it was created to avoid.
  - `pages/notation.qmd`: added the two new pages to its Related Articles
    section (also gives both new pages an inbound link so the site link
    gate's orphan check passes).
  - `sitemap.xml`: added `pages/notation-quick-reference.html` and
    `pages/parameters.html` entries (hand-inserted at the existing
    alphabetical position; the `generate_sitemap.py` tool resorts and
    re-dates every entry, which would have produced a large unrelated diff).
  - `tests/test_notation_and_parameters_pages.py` (new): pins the four
    behaviors above.
  - Ran `python -m scripts.regenerate_claim_audit_evidence` (NOTATION.md and
    pages/notation.qmd are bound evidence for the `/pages/notation.html`
    trust-surface route) and committed the digest-only diff.
  - **2026-09-30 follow-up (Deploy Website route-coverage fix):** merged
    `origin/main` (32 commits; `d53290cd` → `0ec2c7f1`), resolving conflicts in
    `SPEC.md`, `docs/development/{HANDOFF,DEVELOPMENT_LOG}.md` (kept `main`'s
    content, re-added this branch's own row/entry once) and taking `main`'s
    copy of every generated file (`data/trust/claim_audit_inventory.json`,
    `data/trust/generated/claim_audit_report.json`,
    `data/trust/site_trust_surface_audit.json`,
    `reports/site-trust-surface-audit.md`, `sitemap.xml`), then re-applying
    this branch's own `sitemap.xml` entries and regenerating. Added two
    `reviewed` claim-audit inventory records (`/pages/parameters.html`,
    `/pages/notation-quick-reference.html`) with `evidence_sha256` computed
    from the actual page/source files after the merge, `review_commit` set to
    `origin/main`'s HEAD (`0ec2c7f1`), and `findings: []` — the content review
    (below) found no inaccuracies. Bumped `DEFERRED_AUDIT_SCOPE_COUNTS` for
    issue #4063 in `scripts/claim_audit_ids.py` from 15 to 17 and
    `tests/test_claim_audit_inventory.py`'s
    `reviewed_completed_batches`/route-partition assertion from 221 to 223 to
    match the two new `/pages/` routes. This closes the Deploy Website gap:
    `scripts.generate_claim_audit_inventory --check --enforce-publication`
    would otherwise fail on `main` once these two routes render, because they
    had no claim-audit record at all.
  - **Content review performed (evidence/uncertainty/falsifiers/audience_framing):**
    verified the control-affine form, ZTCF/ZVCF/DCR/DgCR acronym expansions,
    core physical-quantity symbols/units, and axis convention in
    `pages/notation-quick-reference.qmd` against `NOTATION.md`'s terminology
    contract and Coordinate Frame Conventions table — all match exactly. The
    card's simplified $\dot x = f(x)+G(x)u$ (vs. `NOTATION.md`'s
    $\dot x = f_p(x) + G_p(x)u$) is a stated simplification, not an error — the
    card explicitly defers to `notation.html` as the normative source.
    Verified `pages/parameters.qmd`'s include of `../PARAMETERS.md` and that
    both pages' Related Articles links (`notation.html`,
    `notation-quick-reference.html`, `parameters.html`, `theory-part1.html`,
    `lagrangian-reference.html`) resolve to existing source files. No
    inaccuracies found; no findings recorded.
- **Blocked:** "Every core page links notation from its header card" is not
  implemented. The header card component (issue #4507 / WEB-03.2 "Build the
  Page Header Card Component") is itself open and unimplemented — there is no
  header card on any page yet to add a link to. Hand-editing the ~20
  `theory-core` pages with an ad hoc substitute would create rework once
  #4507 lands and would be a parallel, competing design to a component
  explicitly scoped as its own `tier:cli`/`complexity:complex` issue. Left
  for the reviewer/owner to decide: accept the PR with 3 of 4 criteria met
  now, or hold this issue until #4507 ships.
- Validation:
  - `python -m pytest tests/test_notation_and_parameters_pages.py tests/test_site_link_gate.py tests/test_site_trust_surface_audit.py tests/test_claim_audit_inventory.py tests/test_check_terminology.py tests/test_root_hygiene.py tests/test_validate_frontmatter.py tests/test_check_tree_parity.py tests/test_check_quarto_render_coverage.py -q` — 152 passed (2026-09-30, post-merge).
  - `python -m scripts.check_quarto_render_coverage` — passes (247 sitemap
    URLs, bidirectional coverage, 2026-09-30 post-merge).
  - `python -m scripts.regenerate_claim_audit_evidence` — "already current"
    after the merge + new records (2026-09-30).
  - `python -m ruff check .` and `python -m black --check --line-length 100 .`
    — both clean (2026-09-30, full tree post-merge).
  - Merge commit's own pre-commit hooks (gitleaks/detect-secrets, ruff, black,
    deferred-validation catalog, claim-audit evidence freshness, prettier) all
    passed; no `.gitleaksignore` addition was needed for the new sha256
    digests.
  - Not run: `quarto render` (not available in this sandbox) and the Jest/
    Playwright suites (no JS/browser behavior changed by this branch). No
    UI/browser verification was performed; the print-card layout is untested
    in an actual browser print preview.
- Next steps:
  1. Push this merge commit and confirm the PR's CI (including the merged-in
     `main` changes) is green.
  2. Owner/reviewer decides whether to merge the 3-of-4 scope or wait for
     #4507, and whether the quick-reference card's condensed content is the
     right shape.
  3. Once merged, flip `DL-#4551` to `shipped`.

# Implementation Handoff — Contributor and Reviewer Guide (#4607)

## Identity

- Repository: D-sorganization/AffineDrift
- Working directory: C:\Users\diete\Repositories\AffineDrift-worktrees\claude-4607
- Branch: claude/issue-4607
- Baseline commit: 46df5059
- Implementation commit: SELF
- Pull request: https://github.com/D-sorganization/AffineDrift/pull/4636 (draft)
- Governing issue/epic: #4607 (part of #4610)

## Objective and Status

- Objective: Add a reader-facing "Contributor and Reviewer Guide" page covering how to propose a
  correction, critique a claim, contribute a dataset, or review a chapter, linked from Collaborate.
- Status: in_review
- Completed: New page `pages/contributor-guide.qmd` routing each of the four paths to its GitHub
  issue template; linked from `pages/collaborate.qmd` (intro sentence + Related Articles); pytest
  coverage added. Merged `origin/main` (which had advanced ~85 commits, including PRs #4491, #4666,
  #4692-equivalent privacy-policy/glossary pages) and added the missing claim-audit inventory record
  for the new `/pages/contributor-guide.html` route that `scripts.generate_claim_audit_inventory
  --enforce-publication` requires for Deploy Website.
- Remaining: none known; awaiting frontier review.

## Files and Decisions

- Files changed (this session, beyond the original PR content):
  - `data/trust/claim_audit_inventory.json`: added one reviewed record for
    `/pages/contributor-guide.html` (route audit, no findings — the page's four claims about
    GitHub issue templates were checked against `.github/ISSUE_TEMPLATE/` and all resolve).
  - `scripts/claim_audit_ids.py`: bumped `DEFERRED_AUDIT_SCOPE_COUNTS` for issue 4063 by 1
    (one new `/pages/` route).
  - `tests/test_claim_audit_inventory.py`: bumped the `reviewed_completed_batches` count assertion
    by 1 to match.
  - `SPEC.md`, `docs/development/DEVELOPMENT_LOG.md`, `docs/development/HANDOFF.md`: merge
    conflict resolution — kept `origin/main`'s content and re-added this branch's own row/section.
  - Regenerated `data/trust/generated/claim_audit_report.json`, `data/trust/site_trust_surface_audit.json`,
    `reports/site-trust-surface-audit.md` via `python -m scripts.regenerate_claim_audit_evidence`
    after taking `origin/main`'s copies and merging in this branch's new record.
- Key decisions: WEB-03.4 ("What This Shows / What It Does Not Show" block, `tier:strong`) does not
  exist anywhere in the codebase yet, so the acceptance criterion "linked from every WEB-03.4 block"
  is not yet actionable — only the "linked from Collaborate" half is implemented. No navbar entry
  was added; the page follows the existing convention of orphan pages (e.g.
  `pages/development-roadmap.qmd`) reached only via inbound content links, keeping the diff
  surgical. Reused existing `.article-section` / `.article-category` / `.article-card` /
  `.provenance-note` CSS primitives already used by `pages/tools.qmd` — no new CSS.
- User-owned or unrelated worktree changes: none observed

## Validation

- `python3 -m pytest -q -o addopts= tests/test_claim_audit_inventory.py tests/test_check_quarto_render_coverage.py tests/test_contributor_reviewer_guide.py tests/test_page_style_discipline.py` — see PR/commit for exact pass counts recorded at commit time.
- `python3 -m scripts.check_quarto_render_coverage` — PASS (sitemap lists the new route).
- `python3 -m scripts.check_spec_changelog` — PASS.
- `python3 -m ruff check .` / `python3 -m black --check --line-length 100 .` on changed files — PASS.

## Blockers and Risks

- Blockers: none. The "linked from every WEB-03.4 block" acceptance criterion cannot be satisfied
  because WEB-03.4 has not been implemented by any repository yet (separate `tier:strong` issue);
  noted in the PR body as a forward-looking follow-up rather than blocking this PR.
- Risks/assumptions: GitHub's `issues/new?template=<file>.md` query parameter is assumed stable
  (documented GitHub behavior); no site-wide link checker was found that needed updating (confirmed
  via `scripts/check_quarto_render_coverage.py` glob-based rendering).

## Next Steps

1. Owner/frontier review of the draft PR #4636.
2. Mark ready and merge once approved.

## Change Log

- SELF — Add reader-facing Contributor and Reviewer Guide page, linked from Collaborate (#4607);
  merge `origin/main` and add the required claim-audit inventory record for the new route.

---

# Implementation Handoff — Short On-Ramp Learning Paths (#4492)

- Repository: `D-sorganization/AffineDrift`, worktree
  `C:/Users/diete/Repositories/AffineDrift-worktrees/claude-4492`.
- Branch `claude/issue-4492`, commit `SELF`; pull request:
  https://github.com/D-sorganization/AffineDrift/pull/4677 (draft, targets
  `main`).
- Governing issue: #4492 (WEB-01.7, part of epic #4496 — Audience Routing and
  Onboarding Funnel). Objective: add short on-ramp learning paths (5 minutes,
  30 minutes, 3 hours) per persona, each a curated sequence of existing
  sections with a goal statement and a self-check question.
- Dependencies listed on the issue (WEB-01.4 "Big Idea in Five Minutes"
  explainer, #4489; WEB-12.4 plain-language entry-page rewrite, #4590) are
  both still open. Neither blocks this issue: the acceptance criteria require
  curating *existing* sections, and no on-ramp here depends on content those
  issues would add — each links only to pages that already exist on `main`.
- Added `resources/on-ramp-paths.qmd`: for each of the 8 personas in
  `config/personas.yml` (learner, researcher, integrator, experimentalist,
  reviewer, contributor, golfer-coach, student), a 5-minute, 30-minute, and
  3-hour on-ramp. Each tier lists existing pages in order with a per-page time
  estimate, a one-line goal statement, and ends with one self-check question
  and its answer grounded in the linked page's actual body content. Every
  link resolves under the site link gate; anchors use the
  `{#onramp-<persona>-<tier>}` convention.
- Linked the new page from `resources/learning-paths.qmd` (an intro pointer
  plus a Path Index entry) so it is not orphaned by the link gate; no
  `_quarto.yml` navigation change was needed, matching how the existing
  per-path pages (`learning-path-foundations.qmd`, etc.) are already wired.
- **Fix round (review of draft PR #4677):** the reviewer found the first pass's
  self-check questions were mostly front-matter-description recall ("per its
  own description...") rather than reflective questions, plus several factual
  errors. Fixed in this commit:
  - A lowercase `g(x)u` in one self-check answer, against `NOTATION.md`'s
    uppercase $G(x)$ convention for the control-affine input map — the
    question that contained it was replaced.
  - A self-check that called the Zero Velocity Counterfactual (ZVCF) a
    "trajectory"; per `articles/theory-part2.qmd` only ZTCF integrates
    forward into a trajectory, ZVCF is a single-state evaluation — reworded.
  - Two self-checks (Researcher 3hr, Student 3hr) that claimed Theory Part 4
    supplies an "independently checkable double-pendulum benchmark."
    `articles/theory-part4.qmd` never mentions a double pendulum — it derives
    beam and pendulum (shaft-flexibility) dynamics. Both were rewritten using
    `articles/theory-part5.qmd`'s own phrase, "independently checkable
    mathematical examples," and the Student 3hr item line and time estimate
    were corrected to match.
  - A factual error found during the required broader verification pass (not
    itself cited by the reviewer): the Researcher and Reviewer 5-minute
    on-ramps described the `resources/research-review-*.qmd` pages as
    finished, evidence-graded reviews. Those pages are explicitly marked
    "Planned (Scaffolding Phase)" / "source-collection stub" with an Evidence
    Status warning that they do not yet establish claims — both on-ramps now
    say so.
  - All 24 self-check questions were rewritten (21 of 24 were previously
    shallow recall) to test a real distinction or mechanism from the linked
    page's body text, with the answer grounded in that text.
  - Theory Part 1's time estimate (appeared at 90/30/60/90 minutes across four
    on-ramps) is now ~30 minutes everywhere, matching the pre-existing,
    already-vetted "30-Minute Route" convention for that article in
    `config/personas.yml`.
  - The page subtitle's "40–160 hours" claim didn't match
    `resources/learning-paths.qmd`'s own stated range (10–80 / 80–160 / 160+
    hours); changed to "10–160+ hours."
- Tests: `tests/test_on_ramp_paths.py`, now 10 cases (5 original + 5 added
  this round as regression guards for the fixes above): front-matter
  validity, all 24 persona/tier anchors present, every tier has a timed page
  link plus a self-check question and answer, all internal links resolve, the
  page is linked from the learning-paths hub, no unqualified lowercase
  `g(x)u`, Theory Part 1's time estimate is consistent everywhere it appears,
  Theory Part 4 is never described with "double pendulum" wording, no
  "per its own description" recall phrasing remains, and the subtitle matches
  the learning-paths hub's stated hour range.
- Validation commands run in this worktree (this fix round):
  - `python -m pytest tests/test_on_ramp_paths.py -v` → 10 passed.
  - `python -m pytest tests/test_site_link_gate.py tests/test_how_to_read.py
    tests/test_persona_start_paths.py tests/test_check_links.py
    tests/test_check_site_health.py -v` → 98 passed.
  - Site gate (invoked via `scripts/link-checker.py`'s `main(["--site-gate"])`
    with the repo root on `sys.path`, working around a `ModuleNotFoundError`
    when the script is run directly without `PYTHONPATH`) → "Site gate
    passed!".
  - `python -m ruff check tests/test_on_ramp_paths.py` → all checks passed.
  - `python -m black --check --line-length 100 tests/test_on_ramp_paths.py`
    → clean after one auto-format pass for the new assertion's line wrap.
  - Full `python -m pytest --cov` suite: still fails at collection on ~75
    unrelated test modules (`tests/test_screw_examples.py`,
    `benchmarks/test_core_benchmarks.py`, etc.) with
    `ImportError: A module that was compiled using NumPy 1.x cannot be run in
    NumPy 2.2.6`. Confirmed pre-existing and unrelated to this change in the
    original pass; unchanged this round. Not fixed here; out of scope for a
    WEB-01.7 content change.
- Not done / deferred: none for the issue's own acceptance criteria. The two
  open dependency issues (#4489, #4590) may eventually add content (a "Big
  Idea in Five Minutes" explainer, plain-language entry-page rewrites) that a
  future pass could fold into these on-ramps, but nothing here requires it.

## Next Steps

1. Push `claude/issue-4492` with this fix round.
2. Awaiting frontier-agent re-review of PR #4677.
# Deduplicate and Reconcile Bibliography Databases — 2026-09-29

- Repository: `D-sorganization/AffineDrift`, worktree
  `C:\Users\diete\Repositories\AffineDrift-worktrees\claude-4547`.
- Branch `claude/issue-4547`, commit `SELF`; pull request:
  #4676 (draft), https://github.com/D-sorganization/AffineDrift/pull/4676.
- Governing issue: #4547 (WEB-07.5). Objective: zero duplicate keys/DOIs across the site's
  bibliography databases, with rendered citations unchanged in meaning.
- **Reworked 2026-09-29 after review blocked the original mechanical-merge draft.** The review
  found the merge had: broken the locked `articles/proximal_distal_energy_transfer/` publication
  source (its `references.bib` dropped from 100 to 24 entries); touched
  `data/trust/book_publication_audit.json`, an owner-sign-off-gated ledger, and the book chapter it
  audits; deleted citation keys still cited on live pages (`Penner2003`, `zajac1989determining`,
  `sprigings2000insight`, `opensim_lib`, `Khalil2002`, `harris1998signal`, `khatib1987unified`,
  `mackenzie2009three`, `marsden1999introduction`, `nesbit2005three`, `winter2009biomechanics`,
  `featherstone2008rigid`, and others); silently renamed the Choi & Park grip-kinetics key to
  `koike2020`; and mistyped `clark2013whatever` as a book when it is a *Behavioral and Brain
  Sciences* journal article. All of that is reverted; see "Completed work" below for what ships
  instead.
- Completed work (post-rework):
  - Restored `articles/proximal_distal_energy_transfer/` and
    `data/trust/book_publication_audit.json` (plus the audited
    `articles/The_Geometry_of_Motion/Volume_III/chapters/ch01_biology_vs_engineering.tex`) to
    `origin/main` byte-for-byte via `git checkout <branch-point> -- <path>`, and likewise reverted
    every other file the original merge had touched (all 8 `.bib` files, every renamed citation
    site across `.qmd`/`.tex`/`*-bibliography.md`, and the `claim_audit_inventory.json`/
    `claim_audit_report.json` digest refreshes) — confirmed by an exhaustive
    `git diff --stat <branch-point>` showing only the files listed below differ from the branch
    point.
  - Added `articles/proximal_distal_energy_transfer/references.bib` to `STANDALONE_LINKED` in
    `scripts/check_bibliography_cross_file.py`: `index.qmd` uses it as its sole `bibliography:`
    override, so — like the other `STANDALONE_LINKED` files — it needs local self-sufficiency for
    every key its own pages cite, and a shared DOI there is not an avoidable duplicate.
  - Fixed `clark2013whatever` (the only occurrence repo-wide, in
    `articles/The_Physics_of_Golf/golf_physics.bib`) from `@book`/Oxford University Press to
    `@article`/*Behavioral and Brain Sciences*/Cambridge University Press, volume 36, number 3,
    pages 181–204 — sourced from `geometry_of_motion.bib`'s pre-existing, correctly-typed
    `Clark2013` entry for the same paper.
  - Confirmed the Choi & Park grip-kinetics key needed no further action: the full revert already
    restored `golf_physics.bib`'s `Choi2020GripKinetics` (and `tests/test_constraint_forces_rigor.py:163`'s
    reference to it). The two other `koike2020`-adjacent entries found while checking this
    (`articles/proximal_distal_energy_transfer/references.bib` and
    `references/proximal-distal-energy.bib`, each a distinct, pre-existing, unrelated paper) were
    left untouched.
  - Did **not** add a new citation-resolution test: the repo already has one, wired into CI
    (`.github/workflows/ci-standard.yml`) and running today. `scripts/check_citation_resolution.py`
    and `scripts/check_qmd_citation_keys.py` both walk every `.qmd` under `articles/`, `books/`,
    `pages/`, `resources/` (plus root `index.qmd`), resolve each page's bibliography the same way
    (per-page `bibliography:` frontmatter, else the nearest ancestor `_quarto.yml`'s default), and
    fail on any `[@key]`/`@key` that does not resolve there; `scripts/check_latex_structure.py`
    (`TestCitations` in `tests/test_check_latex_structure.py`) does the equivalent for LaTeX
    `\cite`-family commands against a baseline
    (`config/latex-structure-baseline.json`). Writing a fourth, parallel implementation of the same
    check would have duplicated working, already-CI-gated infrastructure rather than fixed
    anything — confirmed by running all three directly against the reverted tree:
    `python3 -m scripts.check_citation_resolution` → "passed for 286 qmd files";
    `python3 -m scripts.check_qmd_citation_keys` → "passed"; `python3 scripts/check_latex_structure.py
    --root articles --baseline config/latex-structure-baseline.json` → "No new structural
    problems." All three already confirm none of the reviewer's named keys (or any other citation)
    are unresolved post-revert; that was the actual verification this issue's item 3 needed, and
    existing infrastructure already provides it.
  - Updated the two `TestDuplicateDois` fixtures in `tests/test_check_bibliography_cross_file.py`
    that had used `articles/proximal_distal_energy_transfer/references.bib` as a "non-standalone"
    example; they now use a synthetic label, since — after the `STANDALONE_LINKED` addition above —
    `references/impact-acoustics.bib` is the only file among the 8 still fully non-exempt, and no
    second real file remains to pair it with.
- Key decisions:
  - Reverting was chosen over attempting to selectively re-fix the blocked merge: the review's
    findings spanned locked content, an audit ledger requiring owner sign-off, and silent renames,
    and disentangling "which parts of the merge are still safe" file-by-file carried more risk of
    missing another instance of the same problem than reverting wholesale and re-adding only the
    two genuinely isolated, verified fixes (the `STANDALONE_LINKED` entry and the `clark2013whatever`
    metadata correction).
  - The 82 raw duplicate-DOI groups still in the 8 bibliographies (110 extra copies) are left in
    place rather than mechanically merged again. Per the narrowed scope, only genuinely identical
    duplicate entries should be consolidated, and distinguishing "the same work legitimately copied
    into two `STANDALONE_LINKED` files" from "an avoidable duplicate" for each of the 82 groups by
    hand is future work, not this PR's.
  - No rendered-bibliography diff (`quarto render` before/after) was performed — out of policy for
    this session (~14 min for a full-site render) and, since nothing in the reverted tree changed
    relative to `origin/main` except the two isolated fixes above, not needed to establish that
    rendered citations are unchanged in meaning for everything but `clark2013whatever`.
- Compatibility constraints: none — no public API changed; the locked
  `proximal_distal_energy_transfer` article and the audited book chapter are untouched, matching
  the review's explicit requirement.
- Validation commands and outcomes:
  - `git diff --stat <branch-point>` (working tree vs. the commit this branch was created from) →
    only `SPEC.md`, `docs/development/DEVELOPMENT_LOG.md`, `docs/development/HANDOFF.md`,
    `scripts/check_bibliography_cross_file.py`, `tests/test_check_bibliography_cross_file.py`, and
    `articles/The_Physics_of_Golf/golf_physics.bib` differ; every other file the original merge
    touched matches the branch point exactly.
  - `python3 scripts/check_bibliography_cross_file.py` → 8 bibliographies, 770 distinct keys, 163
    shared across files, 0 disagreeing, 0 CI-flagged duplicate DOIs (82 raw shared-DOI groups exist
    before the `STANDALONE_LINKED` exemption is applied — see the PR body for the honest count).
  - `python3 -m pytest tests/test_check_bibliography_cross_file.py -v` → 18 passed.
  - `python3 -m scripts.check_citation_resolution` → passed for 286 qmd files.
  - `python3 -m scripts.check_qmd_citation_keys` → passed.
  - `python3 scripts/check_latex_structure.py --root articles --baseline config/latex-structure-baseline.json`
    → no new structural problems.
  - `python3 -m ruff check .` and `python3 -m black --check --line-length 100 .` → clean.
- The `claim-audit-evidence` pre-commit hook caught a stale review-evidence digest for
  `articles/The_Geometry_of_Motion/quarto/ch09_parallel_mechanisms_constrained_dynamics.qmd` — a
  file with zero diff on this branch and no presence in this PR's changed-file list at any point,
  so the staleness reflects drift already on `origin/main` since this branch's fork point, not this
  change. Ran the sanctioned `python -m scripts.regenerate_claim_audit_evidence` (the same tool
  used earlier in this issue) to refresh it, since the hook blocks the commit regardless of cause
  and bypassing it is against repo policy. Confirmed via `git diff` that the regeneration touched
  exactly two file digests: that pre-existing stale one, and `golf_physics.bib` (expected, from the
  `clark2013whatever` content fix above) — no other entry moved.
- Blockers/risks: none identified for the reworked scope. Two items remain out of scope and are
  disclosed in the PR body rather than fixed here (per the "Spotted ≠ fix" fleet rule and the
  explicit rework instructions): (1) the 82 raw duplicate-DOI groups; (2) no rendered-bibliography
  diff was performed.
- Next steps: reworked draft PR #4676 is open with the honest remaining-scope disclosure in its
  body; awaiting owner/frontier review.
# Implementation Handoff — Cross-Browser Coverage (#4564)

## Identity

- Repository: D-sorganization/AffineDrift
- Working directory: C:/Users/diete/Repositories/AffineDrift-worktrees/claude-4550
- Branch: claude/issue-4550
- Baseline commit: 047fc82b (origin/main)
- Implementation commit: SELF
- Pull request: to be opened as a draft by this session
- Governing issue/epic: #4550 (WEB-07.9, part of epic #4552 "E7 — Researcher Infrastructure")

## Objective and Status

- Objective: three acceptance criteria — (1) PDFs built in CI and linked from the header card,
  (2) one print stylesheet, (3) print includes typeset math.
- Status: **partial / honest-scope**. Criteria (2) and (3) are implemented and tested. Criterion
  (1) is deliberately not implemented — see Blocked below.
- Completed:
  - `css/print.css` / `styles.css`: merged the two competing `@media print` blocks (the
    comprehensive one in `css/print.css` and the "In Layman's Terms" one at `styles.css:1788`)
    into `css/print.css` alone, so exactly one print stylesheet exists.
  - `css/print.css`: changed `@page { size: a4; }` to `size: auto`, so the browser honors the
    printer/OS paper-size choice instead of forcing A4 — this is how a static CSS stylesheet
    supports both Letter and A4 (there is no CSS construct to force "either A4 or Letter";
    `auto` is the standard way to defer to the print dialog).
  - `js/pdf.js`: new `initPrintMathTypesetting()`, wired from `main.js`, registers a
    `beforeprint` listener that calls `MathJax.typesetPromise()`. The existing `.export-to-pdf`
    button already delayed printing by `MATHJAX_RENDER_DELAY_MS` but never actually forced a
    typeset, and neither path covered a native Ctrl+P print. Because MathJax here is
    lazy-loaded (`loader.load: ['ui/lazy']`), off-screen math is left as raw TeX until scrolled
    into view (the concern named by the referenced WEB-11.3), so this is the "typesetting is
    forced before print" fallback WEB-11.3 itself describes.
  - Tests: `tests/test_print_stylesheet_consolidation.py` (4 tests, written first, RED confirmed
    against the pre-change two-block/A4-only state), plus new `tests/pdf.test.js` (2 tests) for
    the `beforeprint` handler.
- **Blocked:** criterion (1), "PDFs built in CI and linked from the header card," was not
  implemented. Investigation found:
  - The compiled book PDFs (`articles/The_Physics_of_Golf/main.pdf`,
    `articles/The_Geometry_of_Motion/Volume_*/main.pdf`, `articles/Launch_Monitor_Technology_Review/main.pdf`)
    are hand-committed binaries built from a separate LaTeX source tree
    (`main.tex`/`chapters/`). `.github/workflows/compile-textbooks.yml` already compiles and
    verifies them in CI on every push/PR that touches `.tex`/`.bib` sources, but only uploads
    them as 14-day CI artifacts — it does not commit them back or publish them to `docs/`.
  - The web-reading experience for those same two books is a **second, independent** Quarto
    source tree (`articles/The_Physics_of_Golf/quarto/*.qmd`,
    `articles/The_Geometry_of_Motion/quarto/*.qmd`), with no automated check that the two trees
    stay in sync. Linking the committed PDF from every chapter's header card
    (`scripts/filters/page-header-card.lua`) without a freshness guarantee risks silently
    surfacing a stale/diverged "official" PDF next to the live HTML chapter — a correctness
    problem this repository's own tooling (claim-audit gates, `check_quarto_render_coverage.py`)
    treats seriously elsewhere.
  - The issue's "Proposal" text ("attached to releases and covered by the DOI") names
    infrastructure that does not exist in this repository at all: no `CITATION.cff`, no GitHub
    Releases workflow, no Zenodo/DOI integration. Building that is an architecture decision
    (which release mechanism, which DOI provider, concept vs. versioned DOI), not a mechanical
    change — `tier:strong` territory under this repo's own Agent Tiers rule regardless of this
    issue's `tier:cli` label (the issue also independently carries `complexity:complex`).
  - Scope of "header card" and "core series" is also open: every chapter across two books, six
    Geometry-of-Motion volumes, and the proximal-distal monograph, or only each book's/series's
    landing page? Guessing wrong here either ships a misleading stale-PDF link or a change the
    frontier reviewer has to unwind.
  - Per this session's own instructions ("do not guess; push what you have, open the draft PR
    with a Blocked section, and stop"), criterion (1) is left for an owner/frontier decision
    rather than guessed at.
- Working directory: C:/Users/diete/Repositories/AffineDrift-worktrees/claude-4564
- Branch: claude/issue-4564
- Baseline commit: 047fc82b (origin/main)
- Implementation commit: SELF
- Pull request: https://github.com/D-sorganization/AffineDrift/pull/4685 (draft)
- Governing issue/epic: #4564 (WEB-09.4; epic #4569 / E9 — Accessibility Conformance)

## Objective and Status

- Objective: CI's `e2e-tests` job in `ci-standard.yml` only runs the Chromium
  Playwright project on pull requests. `playwright.config.js` also defines
  `firefox`, `webkit`, `Mobile Chrome`, and `Mobile Safari` projects that never
  run in CI. The issue asks for (1) a nightly job that runs Firefox and WebKit
  on a representative route set, and (2) failures that open issues
  automatically, deduplicated by title.
- Status: ready for commit / PR.
- Completed:
  - Added `.github/workflows/cross-browser-nightly.yml`: a scheduled
    (`0 7 * * *` UTC) + `workflow_dispatch` workflow with a `[firefox, webkit]`
    matrix job that builds the site (reusing the same Quarto render cache key
    as `ci-standard.yml`'s `e2e-tests` job, #4595) and runs
    `tests/e2e/smoke.spec.js` — the existing PR-smoke suite covering six
    representative public routes plus dark-mode/back-to-top/no-splash
    behavioral invariants — against each browser, uploading the Playwright
    JSON report as an artifact per browser.
  - Added a downstream `report-failures` job (`if: always()`) that downloads
    both JSON reports and runs `scripts/report_e2e_browser_failures.py`.
  - Added `scripts/report_e2e_browser_failures.py`: parses one or more
    Playwright JSON reporter files, extracts tests whose final verdict was an
    unexpected failure, builds one issue per distinct `(browser, test title)`
    pair, and skips any pair already covered by an existing open issue with
    the same title — the dedup-by-title acceptance criterion.
  - Added `tests/test_report_e2e_browser_failures.py` (29 tests, TDD:
    confirmed RED before implementing, both in the initial commit and for
    each round of review feedback below) covering nested-suite JSON parsing,
    the title-building dedup key, issue body content, and dedup selection
    (including same-title-different-browser must NOT be deduped together).
  - Review feedback round 1 — three behavior changes, each landed test-first:
    1. **No new labels.** `ISSUE_LABELS` dropped the nonexistent
       `cross-browser` label (now just `("ci", "automation")`, both of which
       already exist in the repo). `fetch_existing_open_titles` no longer
       filters by `--label`; it now uses
       `gh issue list --search '"[Cross-Browser Nightly]" in:title'` and a new
       pure `filter_cross_browser_titles()` helper keeps only titles that
       actually start with the reporter's prefix (defends against `--search`
       matching the phrase elsewhere in a title).
    2. **Missing/unparseable/empty reports no longer crash or vanish
       silently.** New `load_report_failures()` replaces the old
       `load_report()`: a missing file, an empty file, or invalid JSON for a
       given `--report` path now yields one synthetic failure entry (title
       `"no test report produced (job failed before tests ran)"`, project
       derived from the filename via `derive_project_from_report_path()`,
       e.g. `playwright-report-webkit.json` -> `webkit`) instead of raising or
       being skipped.
    3. **Issue-creation cap.** When a run has more than
       `MAX_INDIVIDUAL_ISSUES` (5) new (not-already-open) failures, one rollup
       issue is opened instead — titled `"[Cross-Browser Nightly] "` followed
       by the failure count, `" failures on "`, and today's UTC date in
       `YYYY-MM-DD` form (`build_summary_issue_title` /
       `build_summary_issue_body`) and listing every `(project, test, file)`
       in a table. Per-failure dedup against
       already-open issues still applies before the count is taken, and
       `--dry-run` prints the rollup title the same way it prints individual
       titles.
  - Updated `docs/development/DEVELOPMENT_LOG.md` (`DL-#4564`) and this file.
- Remaining: Commit, push, and post the review-feedback update to draft PR
  #4685.

## Files and Decisions

- Files changed:
  - `css/print.css`: `@page` size `a4` → `auto`; added the merged-in "In Layman's Terms" print
    rules.
  - `styles.css`: removed its competing `@media print` block, replaced with a pointer comment.
  - `js/pdf.js`: new `initPrintMathTypesetting()`.
  - `js/main.js`: imports and calls `initPrintMathTypesetting()` from `./pdf.js`.
  - `tests/test_print_stylesheet_consolidation.py`: new file, 4 tests.
  - `tests/pdf.test.js`: new file, 2 tests for `initPrintMathTypesetting`.
  - `docs/development/HANDOFF.md`, `docs/development/DEVELOPMENT_LOG.md`: this entry.
- Key decisions: see "Completed" and "Blocked" above.
- User-owned or unrelated worktree changes: none observed. Note: this file
  (`docs/development/HANDOFF.md`) already contained a pre-existing unresolved merge-conflict
  marker (`>>>>>>> origin/main`) further down, from a prior session's edit — not introduced or
  touched by this change; flagged in the PR body rather than fixed here (out of this issue's
  scope).

## Validation

- `python3 -m pytest tests/test_print_stylesheet_consolidation.py -q` — 4 passed.
- `python3 -m pytest tests/test_page_header_card.py::test_print_stylesheet_includes_page_header_card_rules tests/test_summary_takeaways.py -k print -q` — 2 passed (unaffected by the merge).
- `npx jest` — 26 suites, 437 passed, 19 skipped, 0 failed.
- `python3 -m ruff check .` — all checks passed.
- `python3 -m black --check --line-length 100 .` — all files unchanged.
- `python3 -m scripts.check_css_architecture` — PASS (62 files scanned).
- `python3 -m scripts.check_styles_budget` — PASS (3,314 / 3,400 line budget).

## Blockers and Risks

- Blocker: criterion (1) needs an owner/frontier decision on CI-publication freshness, header-card
  link scope, and (per the Proposal text) release/DOI infrastructure choice — see "Blocked" above.
- Risk: none to existing print/PDF behavior — the CSS merge is a pure relocation (same selectors,
  same declarations) plus the `a4` → `auto` page-size change, and the new `beforeprint` handler is
  additive and no-ops when `MathJax` is undefined.

## Next Steps

1. Push the branch and open the draft PR with `Fixes #4550` and the Blocked section above.
2. Owner/frontier decides the deferred scope for criterion (1); implement in this issue or split
   into a follow-up.

## Change Log

- `SELF` — Consolidate print CSS into one stylesheet, support Letter and A4, force MathJax
  typesetting before print; defer the PDF-build/header-card-link criterion pending a scope
  decision (#4550).
  - `.github/workflows/cross-browser-nightly.yml`: new nightly workflow.
  - `scripts/report_e2e_browser_failures.py`: new issue-filing script.
  - `tests/test_report_e2e_browser_failures.py`: new pytest suite.
  - `docs/development/DEVELOPMENT_LOG.md`: `DL-#4564` entry.
  - `docs/development/HANDOFF.md`: this entry.
  - `SPEC.md`: pending change-log row.
- Key decisions:
  - Chose `tests/e2e/smoke.spec.js` as the "representative route set" rather
    than the full suite: it already exists precisely for this purpose (fast
    PR smoke coverage across public routes + interactive behavior) and
    keeps nightly runtime bounded instead of running visual-snapshot/axe
    suites twice more per night.
  - Issue dedup keys on the rendered issue title, built as
    `[Cross-Browser Nightly] ` followed by the browser project name, a colon,
    and the Playwright spec title, rather than a hidden marker, matching the
    issue's literal "deduplicated by title" wording; a title search
    (`gh issue list --search`) plus a prefix filter scopes the lookup instead
    of a label, since the repo has no `cross-browser` label and this script
    must not create one.
  - The rollup-issue threshold (`MAX_INDIVIDUAL_ISSUES = 5`) is a plain
    constant, not a CLI flag: nothing in the issue or the review feedback asks
    for it to be tunable per run, and a flag nobody sets is just dead surface
    area.
  - Did not touch `ci-standard.yml`'s Chromium-only `e2e-tests` job: the issue
    is additive (a new nightly job), not a change to the PR-gated lane.
- User-owned or unrelated worktree changes: none observed.

## Validation

- `python -m pytest -q -o addopts= tests/test_report_e2e_browser_failures.py` —
  29 passed (11 from the initial commit + 18 added for the three review-
  feedback behaviors, all confirmed RED before implementation).
- `python -m ruff check scripts/report_e2e_browser_failures.py tests/test_report_e2e_browser_failures.py` —
  all checks passed.
- `python -m black --check --line-length 100 scripts/report_e2e_browser_failures.py tests/test_report_e2e_browser_failures.py` —
  both files unchanged.
- `python3 -m pytest tests/ --cov=src --cov=scripts --cov-report=term-missing --timeout=120 -q` —
  full suite passes at 79.11% coverage (floor 75%) as of the initial commit;
  one pre-existing failure in
  `tests/test_dates_and_history.py::TestRevisionHistoryRendering::test_filter_renders_revision_history_section`
  unrelated to this change (pandoc emits a `div` element with that id instead
  of the expected `section` element in this environment).
- `python3 -m scripts.check_workflow_action_pins` — all workflow actions
  pinned to immutable SHAs (workflow file itself untouched by this round).
- Not run: the nightly workflow itself (requires a scheduled/dispatched
  Actions run on the fleet runner with real browser binaries; cannot execute
  GitHub Actions locally).

## Blockers / Risks

- The workflow's actual behavior (browser install, site render, issue
  creation via `gh`) is unverified end-to-end until it runs in GitHub
  Actions — either via `workflow_dispatch` after merge or the first nightly
  fire. A frontier review should consider triggering `workflow_dispatch` once
  merged to confirm the full pipeline before relying on it.

---

# Website Consolidation (Seven Web Issues) — 2026-09-29

- Repository: `D-sorganization/AffineDrift`, working directory
  `AffineDrift-worktrees/w-ad-web-consolidated`.
- Branch `claude/website-consolidated-0929`, commit `SELF`; one consolidated
  draft pull request (see the PR list) supersedes drafts #4615, #4616 and #4618
  and the unpushed branches for #4608, #4583, #4568 and #4548.
- Objective: land seven Sonnet 5 CLI-tier website issues in one CI cycle under
  the PR-queue consolidation rule (RM#1691).

| Issue | Branch              | Change                                                                   |
| ----- | ------------------- | ------------------------------------------------------------------------ |
| #4576 | `claude/issue-4576` | Privacy Policy page (`pages/privacy-policy.qmd`) plus footer link.       |
| #4582 | `claude/issue-4582` | Uppercase `G(x)` notation; `scripts/check_notation.py` baseline lint.    |
| #4546 | `claude/issue-4546` | `scripts/filters/schema-jsonld.lua` JSON-LD filter; deletes dead include. |
| #4608 | `claude/issue-4608` | Website/UX problem issue template plus contract test.                    |
| #4583 | `claude/issue-4583` | "Drift-Control Ratio" naming; slug `drift-control-ratio` with alias.     |
| #4568 | `claude/issue-4568` | Accessibility statement page (WCAG 2.1 AA target, #4139 inventory).      |
| #4548 | `claude/issue-4548` | Render rule plus front matter for all 22 companion bibliographies.       |

- Key decisions:
  - `data/trust/claim_audit_inventory.json` was merged by hand: #4583's route
    rename (`/articles/drift-control-ratio.html`, audit id
    `ad-route-4a8ccbe60039`) applied, routes re-sorted, then
    `python -m scripts.regenerate_claim_audit_evidence` after every merge.
  - `articles/Pinocchio_Project_Outline-bibliography.md` is kept (given front
    matter) rather than deleted; it holds 194 lines of substantive references.
  - `articles/controllability-drift-ratio-bibliography.md` keeps its filename;
    #4583 renamed only the article.
  - The privacy page's related section was renamed to `## Related Articles`
    and given a third link so the site gate's related-coverage rule passes.
- Validation on the consolidated branch:
  - `python -m pytest -o addopts= tests/test_privacy_policy_page.py
    tests/test_check_notation.py tests/test_schema_jsonld.py
    tests/test_companion_hierarchy.py tests/test_website_ux_issue_template.py
    tests/test_accessibility_statement_page.py
    tests/test_check_quarto_render_coverage.py tests/test_navbar_ia.py
    tests/test_public_site_manifest.py tests/test_claim_audit_inventory.py
    tests/test_site_link_gate.py tests/test_dcr_reachability_contract.py
    tests/test_dcr_article_rigor.py tests/test_scientific_trust_metadata.py`
    — 165 passed.
  - `python -m scripts.link-checker --site-gate --root .` — passed.
  - `python -m scripts.regenerate_claim_audit_evidence --check` — current.
  - `python -m scripts.check_spec_changelog` — passed.
  - Full render and Playwright/axe run in CI only.
- Blockers/risks: none known. Rendered output is not committed.
- Next steps:
  1. Wait for CI on the consolidated PR; fix any failure on this branch.
  2. Mark ready, verify the remote head, arm via `automerge_guard.py`.
  3. After merge, close #4615, #4616 and #4618 as superseded and remove the
     seven `claude-<issue>` worktrees.
# Implementation Handoff — Deploy Website Verification Fix (#4617)
# Implementation Handoff — Resolve Passive/Active Nomenclature Conflict (#4529)
# Implementation Handoff — Plain-Language Summary and Key Takeaways Block (#4508)
# Implementation Handoff — Correct Learning-Path Contradictions and Chapter References (#4493)
# Configure Search, and Include Maturity in Results — 2026-09-29

- Repository: `D-sorganization/AffineDrift`, working directory
  `C:\Users\diete\Repositories\AffineDrift-worktrees\claude-4504`.
- Branch `claude/issue-4504`, commit `SELF`; pull request: to be opened this session (draft).
- Governing issue: #4504 (WEB-02.10, part of epic #4514). Objective: configure an explicit
  Quarto `search:` block, fix or remove the unverified `SearchAction` JSON-LD, and show the
  page-header-card maturity badge on matching search results.
- Completed work:
  - `_quarto.yml`: added an explicit `website.search` block (`type: overlay`, `limit: 20` — Quarto's default, so deep
    monograph results stay reachable —
    `keyboard-shortcut: ["/", "s"]`) — search previously ran on unconfigured Quarto defaults.
  - `_includes/site-head.html`: removed the JSON-LD `SearchAction` sub-object, which pointed at
    `https://affinedrift.com/?q={search_term_string}` — a target the site does not implement
    (Quarto's search is a client-side overlay, not a query-string-driven page). The rest of the
    `WebSite` JSON-LD schema is unchanged.
  - `js/search-maturity-badge.js` (new): a self-initializing client module that fetches a
    committed `/data/search-maturity.json` map and annotates matching `.search-result-doc` entries
    with the same `.badge.badge--maturity.badge--<variant>` markup
    `scripts/filters/page-header-card.lua` renders on the page itself, using a
    `MutationObserver` since Quarto's search overlay renders results asynchronously.
  - `scripts/generate_search_maturity_index.py` (new): scans `status`/`maturity` front matter
    across the same content directories as `generate_sitemap.py` and writes the href → 
    `{label, variant}` map consumed by the JS module above to the committed
    `data/search-maturity.json` (a Quarto resource). `--check` and a freshness pytest keep it
    current; no deploy-workflow change (the file is `{}` until pages declare a maturity).
  - `css/search-metrics.css`: appended badge placement/spacing rules for the injected badge
    inside `.search-result-title-container`.
  - `articles/zero-torque-counterfactual.qmd`: titled it "Zero-Torque Counterfactual (ZTCF) Family" (the family
    qualifier satisfies the ZTCF first-use rule)
    so the page ranks first for a "ZTCF" search query (many other pages mention ZTCF in body
    headings, but none had it in the title). No maturity status was added: no page carries a
    `status`/`maturity` field yet, and assigning one is an editorial decision, not a test fixture.
  - `scripts/sync_frontend_assets.py`: registered `search-maturity-badge.js` in
    `CANONICAL_JS_NAMES`.
  - `tests/e2e/search.spec.js`: added a Playwright test asserting a "ZTCF" search returns the
    ZTCF page first. The "with its badge" half of acceptance criterion #1 stays open until the
    owner assigns real maturity states; badge injection is covered by the Jest fixtures.
  - `tests/search-config.test.js`, `tests/search-maturity-badge.test.js`,
    `tests/test_generate_search_maturity_index.py` (all new): unit coverage for the search
    config block, the SearchAction removal, the badge-injection module (9 tests), and the
    index generator (7 tests).
  - Regenerated pinned evidence digests in `data/trust/claim_audit_inventory.json`,
    `data/trust/generated/claim_audit_report.json`, and `data/trust/site_trust_surface_audit.json`
    via `scripts/regenerate_claim_audit_evidence.py`, since editing `_quarto.yml` and the ZTCF
    `.qmd` invalidated their previously-pinned SHA-256 evidence hashes.
  - Keyed SPEC.md change-log row to #4504.
- Key decisions:
  - Removed the `SearchAction` rather than fixing its target, since the acceptance criterion
    accepts either and Quarto's overlay search has no server-side query-string endpoint to
    point it at; fabricating one would be a bigger, out-of-scope change.
  - The maturity badge could not be added through Quarto's own search-result templating (no
    such hook exists), so it is applied client-side against the search overlay's DOM, mirroring
    the badge markup/CSS already shipped for page headers by #4507 rather than inventing new
    badge styling.
  - "Index the glossary" (issue's proposal bullet) needed no new mechanism: `pages/glossary.qmd`
    already renders as a normal page with no search exclusions, so it is already indexed by
    Quarto's default `search.json` generation.
- Compatibility constraints: none — additive JSON-LD removal and new generated asset; no
  existing route, API, or schema changed shape.
- Validation commands and outcomes:
  - `npx jest` → 28 suites, 441 passed, 19 skipped, 0 failed.
  - `python3 -m pytest --timeout=120 -q` → all passed (only pre-existing environment skips).
  - `python3 -m ruff check .` → clean.
  - `python3 -m black --check --line-length 100 .` → clean.
  - `python3 -m scripts.check_spec_changelog` → passed.
  - `python3 -m scripts.regenerate_claim_audit_evidence --check` → "claim-audit evidence digests
    and reports are current".
  - `python3 -m scripts.check_css_architecture`, `check_module_size_budget`,
    `check_tech_debt_budget`, `check_contract_coverage`, `check_js_dependency_boundaries` → all
    passed.
  - **Not run locally:** `quarto render` and `npx playwright test` (quarto CLI is blocked in
    this sandbox). The new `tests/e2e/search.spec.js` case ("finds the ZTCF page first, with its
    maturity badge") is reasoned through by code inspection against Quarto's search-overlay DOM
    structure but has not executed against a real rendered site — CI's `e2e-tests` job is the
    first actual execution; check its result on the opened PR.
- Blockers/risks: none identified. If CI's `e2e-tests` job fails the new search spec, the next
  step is to inspect the Playwright trace/video artifact — the DOM selectors used
  (`.search-result-doc .search-result-link`, `.search-result-title-container`) were
  reverse-engineered from git history of the vendored `quarto-search.js` and may need
  adjustment if the installed Quarto version's search markup differs.
- Spotted but not fixed (out of scope, per "Spotted ≠ fix"): running the full pytest suite
  repeatedly regenerates unrelated drift in `_includes/generated/research-releases-summary.qmd`,
  `data/trust/generated/research_releases_registry.json`, and
  `data/trust/generated/reader_validation_study.json` (a `generated_on` timestamp bump plus
  JSON reformatting) — reverted with `git checkout --` before committing so this PR's diff stays
  surgical to #4504; this looks like a pre-existing non-determinism in one of those generators,
  unrelated to this change.
- Next steps: push the branch, open the draft PR, and watch CI's `e2e-tests` job for the new
  ZTCF search spec.
# DCR Visualiser Widget — #4535 (WEB-06.5)

- Repository: `D-sorganization/AffineDrift`, worktree
  `C:/Users/diete/Repositories/AffineDrift-worktrees/claude-4535`.
- Branch `claude/issue-4535`, commit `SELF`; pull request: not created by this session — the
  orchestrator opens it.
- Governing issue: #4535 (WEB-06.5, child of epic #4543 "[E6] Interactive Models and
  Reproducibility"). Objective: an interactive widget, driven by
  `src/affine_control/reachability.py::instantaneous_scalar_dcr`, showing how the DCR ratio
  changes through a phase of a trajectory and explicitly demonstrating why DCR is not a
  reachability certificate (claim `ad-dcr-001`), embedded on the DCR page with the claim
  linked, plus a parity test.
- Design: WEB-06.1 (the ADR deciding between `{ojs}`/Pyodide/Shinylive for interactive widgets)
  is still open and `tier:strong`, so this widget follows the only existing precedent in the
  repo — `articles/rotation-converter.qmd`'s plain hand-rolled JS engine plus a separate UI
  script, loaded via `<script src="../js/...">` from a raw `{=html}` block, no new build
  tooling.
- Review response (this update): a human review of the initial implementation asked for four
  fixes plus one optional DRY improvement, all applied:
  1. Relabeled the phase slider from "Swing phase (fraction of horizon elapsed)" to "Phase
     time $t$" (it displays elapsed time, not a fraction) and renamed the subsection heading
     and internal wording from "Swing Phase"/"swing phase" to the neutral "Phase" — the widget
     is a declared mathematical construction, not real golf-swing data, and the heading
     shouldn't imply otherwise.
  2. Added a `<thead>` with `<th scope="col">` headers ("Quantity", "Additive drift",
     "State-dependent drift") to the numeric results table, which previously had no column
     labels.
  3. Added a `<noscript>` fallback (following `articles/proximal-distal-falsification-atlas.qmd:29`'s
     pattern) stating the default scenario's values and linking claim `ad-dcr-001`, so the page
     degrades gracefully without JavaScript.
  4. Moved all ~20 inline `style=` attributes and the hard-coded `#2563eb`/`#dc2626` colors into
     a new `css/dcr-visualizer.css`, using `var(--bg-secondary)`/`var(--border-color)`/
     `var(--bg-primary)`/`var(--text-secondary)` design tokens for surfaces, and two
     widget-scoped custom properties (`--dcrviz-additive`, `--dcrviz-state-dependent`) for the
     two-series accent colors — the same scoping pattern `css/rotation-converter.css` uses for
     `--rc-error`/`--rc-success` — with a `[data-theme="dark"]` / `prefers-color-scheme: dark`
     override so the series colors adapt in dark mode. Registered the new stylesheet in
     `scripts/sync_frontend_assets.py`'s `SYNC_MAPS` (mirrors to `docs/css/dcr-visualizer.css`)
     so the deploy pipeline's `sync_frontend_assets.py --check` step covers it. While doing
     this, found and fixed a real gap from the initial implementation: `js/dcr-visualizer.js`
     and `js/dcr-visualizer-ui.js` had never been added to `CANONICAL_JS_NAMES`, so
     `tests/test_sync_frontend_assets.py::test_every_canonical_javascript_module_has_a_deploy_sync_map`
     was failing — the two JS modules were not registered for deploy-time mirroring to
     `docs/js/`.
  5. (Optional, applied) Centralized the shared parity numbers — the governed fixture's
     $x_0=1$, $\bar u=1$, $T=1$, the two systems' drift parameters, and their expected
     instantaneous-DCR/reachable-interval/width values — into
     `tests/fixtures/dcr_visualizer_parity.json`, read by both
     `tests/test_dcr_visualizer_parity.py` (Python) and `tests/dcr-visualizer.test.js` (JS)
     instead of each suite hardcoding the same literals independently.
- The widget compares two `LinearScalarSystem`s that share one instantaneous DCR at the start
  of the phase — an additive-drift system (`gradient=0`) and a state-dependent-drift system
  (`gradient=ubar/x0`) — and evolves each along its own zero-input drift trajectory as the
  reader drags the phase slider. This is the exact scenario already governed by
  `tests/test_dcr_event_sensitivity_protocol.py::test_state_dependent_drift_breaks_any_dcr_to_reachable_width_mapping`
  (both systems: instantaneous DCR = 1; reachable-interval widths = 2 and 2(e−1)), which gives
  both the Python and JS test suites the same anchored ground truth.
- Added:
  - `js/dcr-visualizer.js` — pure, DOM-free JS mirror of `LinearScalarSystem`,
    `instantaneous_scalar_dcr`, `scalar_linear_reachable_interval`, and
    `constant_additive_drift_interval`, plus the two zero-input drift trajectories
    (`additiveDriftState`, `multiplicativeDriftState`) used to evolve state through the phase.
  - `js/dcr-visualizer-ui.js` — DOM wiring: reads the `x0`/`ubar`/`horizon`/phase-slider inputs,
    validates them (nonzero `x0`, positive `ubar`, nonnegative `horizon`) with the same
    fail-loud contract as the Python dataclass, renders an inline SVG line chart of DCR across
    the phase for both systems, an accessible data table of sampled values, and the computed
    reachable intervals/widths.
  - `css/dcr-visualizer.css` — the widget's styles (see review-response item 4 above), mirrored
    to `docs/css/dcr-visualizer.css` at deploy time via `scripts/sync_frontend_assets.py`.
  - Embedded the widget in `articles/controllability-drift-ratio.qmd`, in a new
    "Interactive: DCR Through a Phase" subsection directly after the existing
    "Executable Constant-Drift Counterexample" subsection, with
    `<a data-trust-claim="ad-dcr-001" href="#claim-ad-dcr-001">` linking the same registered
    claim already cited earlier in the article (and again in the `<noscript>` fallback).
  - `tests/dcr-visualizer.test.js` (17 cases) and `tests/dcr-visualizer-ui.test.js` (5 cases) —
    Jest parity tests for the pure module and a DOM smoke test that extracts the actual
    `{=html}` block from the `.qmd` file (mirroring `tests/rotation-converter-ui.test.js`'s
    pattern) and exercises the live widget, including its two error paths (`x0 = 0`,
    `ubar <= 0`).
  - `tests/test_dcr_visualizer_parity.py` (5 cases) — recomputes the same governed fixture
    directly from `src/affine_control/reachability.py`, asserts the widget's numeric defaults
    in the article match that exact fixture, and asserts the claim link is present. Together
    with the Jest suite (which computes the identical numbers from the JS implementation),
    this is the "parity test" required by the acceptance criteria — there is no existing
    cross-runtime (Python-calls-Node) execution harness in this repo to build a single
    combined test on. Both suites now read `tests/fixtures/dcr_visualizer_parity.json` for the
    shared scenario parameters and expected values (review-response item 5 above).
  - Regenerated the pinned SHA-256/revision digests that reference
    `articles/controllability-drift-ratio.qmd`'s bytes after editing it:
    `python -m scripts.regenerate_claim_audit_evidence` (touches
    `data/trust/claim_audit_inventory.json`, `data/trust/generated/claim_audit_report.json`)
    and `python -m scripts.generate_research_readiness_library` (touches
    `data/research_protocols/library.json`, `data/research_protocols/public_summary.json`).
    These two generators reference each other's output (the research-readiness library's own
    digest is itself pinned as evidence for an unrelated route, `proximal-distal-falsification-atlas`),
    so both were re-run until both `--check` invocations passed cleanly.
- Validation commands run in this worktree:
  - `npm install` (node_modules was not present in the worktree).
  - `npx jest tests/dcr-visualizer.test.js tests/dcr-visualizer-ui.test.js tests/rotation-converter-ui.test.js` → 36 passed.
  - `python3 -m pytest tests/test_dcr_visualizer_parity.py tests/test_dcr_reachability_contract.py tests/test_dcr_article_rigor.py tests/test_dcr_event_sensitivity_protocol.py tests/test_scientific_trust_metadata.py -q` → all passed.
  - `python3 -m pytest tests/test_check_single_title.py tests/test_editorial_and_consistency.py tests/test_formatting_lints.py tests/test_publication_markup_contract.py tests/test_research_protocol_readiness.py tests/test_claim_audit_inventory.py tests/test_sync_frontend_assets.py tests/test_deployment_integrity.py tests/test_page_style_discipline.py tests/test_check_styles_budget.py tests/test_check_css_architecture.py tests/test_css_bundle.py -q` → all passed (after regenerating digests and registering the new CSS/JS sync maps).
  - `python3 -m ruff check .` → all checks passed.
  - `python3 -m black --check --line-length 100 .` → clean.
  - `npx prettier --check tests/fixtures/dcr_visualizer_parity.json css/dcr-visualizer.css` → clean.
  - `python3 -m scripts.check_module_size_budget` → passes (`js/dcr-visualizer.js` 74 lines,
    `js/dcr-visualizer-ui.js` 114 lines, `css/dcr-visualizer.css` well under budget).
  - `python3 -m scripts.regenerate_claim_audit_evidence --check` and
    `python3 -m scripts.generate_research_readiness_library --check` → both clean.
  - `python3 -m scripts.sync_frontend_assets --check` → clean (after running it once without
    `--check` to generate `docs/css/dcr-visualizer.css`, then reverting the unrelated
    pre-existing drift it also surfaced in the already-tracked `docs/css/print.css` and the
    untracked `docs/css/rotation-converter.css`/`docs/js/*.js` build artifacts — those mirrors
    are generated by `quarto render` at deploy time, not committed, so they were left out of
    this diff).
  - **Not run:** `quarto render` and `npx playwright test` (full-site render out of scope for
    this sandbox). The widget was reasoned through via the Jest DOM smoke test rather than a
    rendered-page browser check; CI's `e2e-tests` job is the first real render/axe-core pass
    over this page.

---

# Implementation Handoff — Hide, Mark, or Retire Stub Hubs (#4500)
# Implementation Handoff — Real Dates and Per-Article Change History (#4545)

## Identity

- Repository: D-sorganization/AffineDrift
- Working directory: C:/Users/diete/Repositories/AffineDrift
- Branch: fix/web-07-3-real-dates-and-change-history-4545
- Baseline commit: b6aa4baf87635c3451558596fc4c20f121d5c219
- Implementation commit: SELF
- Pull request: #4640
- Governing issue/epic: #4545 (epic #4552)

## Objective and Status

- Objective: Eliminate build-time `date: today` across all rendered sources, enforce verified `date-source:` metadata, add `date-modified:` derived from substantive changes, and build a front-matter driven `changes:` Revision History section for core pages.
- Status: ready for commit / PR
- Completed:
  - Eliminated `date: today` across all 12 articles, marking unverified first-publication dates as `Date unverified` with `date-source: unverified`.
  - Added `date-source: initial-publication-record` across all 35 articles with concrete publication dates.
  - Derived `date-modified` from substantive commit history and latest changes.
  - Added structured `changes:` revision history to the 10 core theory and foundational pages.
  - Created Pandoc Lua filter `scripts/filters/revision-history.lua` rendering accessible semantic `<section id="revision-history">` before references.
  - Created CSS component `css/components/revision-history.css` registered in `styles.css` with print styles in `css/print.css`.
  - Registered `scripts/filters/revision-history.lua` in `_quarto.yml`.
  - Created automated validator `scripts/derive_substantive_dates.py` supporting `--check`.
  - Created comprehensive TDD test suite `tests/test_dates_and_history.py` (16 tests, all passing).
  - Regenerated claim audit evidence digests and verified all contracts pass.
  - Added change-log row in `SPEC.md`.
- Remaining: Commit, push, create PR, key SPEC.md row, arm auto-merge, and release lease.

## Files and Decisions

- Files changed:
  - `_quarto.yml`: Registered `scripts/filters/revision-history.lua`.
  - `articles/*.qmd`: Replaced `date: today` with `Date unverified` and `unverified` source; added `date-source` and `date-modified`; added `changes:` to core pages.
  - `css/components/revision-history.css`: Component styling.
  - `css/print.css`: Print styling avoiding page breaks inside revision history.
  - `styles.css`: Component import.
  - `scripts/filters/revision-history.lua`: Pandoc filter for revision history rendering.
  - `scripts/derive_substantive_dates.py`: Date metadata derivation and check script.
  - `tests/test_dates_and_history.py`: Unit and contract tests for dates and revision history.
  - `SPEC.md`: PR change-log row.
  - `docs/development/HANDOFF.md`: Updated durable handoff state.
- Key decisions: Unverified dates show 'Date unverified' and emit no citation date; verified dates require 'date-source'; revision history driven from 'changes:' front matter and placed before references by Lua filter.
- User-owned or unrelated worktree changes: none observed

---

# Implementation Handoff — Hide, Mark, or Retire Stub Hubs (#4500)

- Branch: fix/web-02-6-hide-mark-or-retire-stub-hubs-4500
- Baseline commit: fc36109d (origin/main)
- Implementation commit: 67256799
- Pull request: #4664 (https://github.com/D-sorganization/AffineDrift/pull/4664)
- Governing issue: #4500 (WEB-02.6)

## Objective and Status

- Objective: Hide, mark, or retire stub hubs and enforce scaffolding styling policy:
  1. Scaffolding/stub pages must never use success styling (`status-banner--success`, `callout-success`, etc.).
  2. No hub card links to a page under 300 words unless it carries a Planned badge.
- Status: Merged to main in PR #4664.
- Completed:
  - Added `.status-pill--planned` and `.status-badge--planned` CSS styles in `css/components/status-banner.css` and bundled to `docs/styles.css`.
  - Replaced misleading success status styling on scaffolding pages (`resources/research-reviews.qmd`, `pages/book-reviews.qmd`, individual review stubs, `pages/daydreams-doodles.qmd`) with warning status styling indicating planned / scaffolding phase expected 2026-Q4.
  - Replaced promoted stub card on `resources/resources.qmd` with Research Reviews hub card carrying `Planned` badge.
  - Added `Planned` badges to all 4 review entries on `resources/research-reviews.qmd`, to `Dead Fish Swimming Upstream` on `pages/tools.qmd`, and `(Planned)` marks to inward links on `resources/resources-books.qmd`, `resources/resources-papers.qmd`, and `resources/resources-researchers.qmd`.
  - Implemented `scripts/check_scaffolding_styling.py` to enforce that scaffolding pages never use success styling and that hub cards linking to stubs (< 300 words) carry a Planned badge.
  - Added comprehensive test suite `tests/test_check_scaffolding_styling.py` (13 tests) and wired check into `.github/workflows/ci-standard.yml`.
  - Regenerated claim audit evidence digests (`data/trust/` and `reports/`).

---

# Performance of MathJax-Heavy Pages — #4577 (WEB-10.9)

## Identity

- Repository: D-sorganization/AffineDrift
- Working directory: C:/Users/diete/Repositories/AffineDrift-worktrees/claude-4577
- Branch: claude/issue-4577
- Baseline commit: 3bf09e7778aaf4e8f4e9ec99c0955f1f546c34e2
- Implementation commit: `SELF`
- Pull request: to be opened as a draft by this session
- Governing issue/epic: #4577 (WEB-10.9, part of epic #4579 "[E10] Performance, SEO, and Privacy")

## Objective and Status

- Objective: the issue proposes evaluating either (a) a smaller MathJax component build (TeX
  input + CHTML output only) or (b) build-time pre-rendering of static equations to SVG/MathML
  for large chapters, measured before/after on the three heaviest chapters with no change in
  rendering or accessibility.
- Status: implemented option (a). Option (b) was evaluated and not implemented — see "Why
  option (b) was not implemented" below.
- Identified the three heaviest chapters by display/inline math delimiter density (`grep -c` over
  `*.qmd` for `$$|\[|\(`, a reproducible proxy for MathJax rendering load per page):
  `articles/tangent-hyperplane-articles/Tangent_Hyperplanes_Unified_Thesis.qmd` (329),
  `articles/The_Geometry_of_Motion/quarto/volume2_content.qmd` (284), and
  `articles/superposition.qmd` (190).
- Changed `_includes/mathjax-loader.html` (the single gated/lazy MathJax loader used by every
  Quarto-rendered page per #3332-A) to request `tex-chtml.js` instead of `tex-mml-chtml.js`, with
  a re-pinned SRI hash. `tex-mml-chtml.js` additionally bundles the MathML *input* jax; Quarto only
  ever emits TeX delimiters into `.math` spans (confirmed by reading the loader's own
  `adPageHasMath()` detection and every `.qmd` source's math syntax), so that input parser was
  dead weight on every math-bearing page, including the three heaviest chapters above (they all
  load the exact same shared script).
- Measured before/after directly against the pinned jsDelivr CDN URLs (reproducible with
  `curl -s -o /dev/null -w '%{size_download}'` against each URL for raw bytes, and the same
  command with `--compressed` added for gzip transfer size):
  - `tex-mml-chtml.js` (before): 1,173,007 bytes raw; 264,567 bytes gzip transfer.
  - `tex-chtml.js` (after): 1,160,989 bytes raw; 261,828 bytes gzip transfer.
  - Delta: −12,018 bytes raw (−1.0%), −2,739 bytes gzip transfer (−1.0%) on every page that loads
    MathJax, cached after the first load site-wide.
- No change in rendering or accessibility: both bundles include the `assistive-mml` a11y extension
  (verified by string search on both downloaded bundles), which is what `enableAssistiveMml: true`
  in the loader's `MathJax` config activates; the removed component is exclusively the MathML
  *input* parser, which this site's TeX-only content never invokes. CHTML output, TeX input syntax,
  macros, and the existing lazy-typesetting (`ui/lazy`) behavior are all unchanged.
- **Why option (b) (build-time SVG/MathML pre-rendering) was not implemented:** it would need a new
  build step (either a Quarto post-processor or swapping `html-math-method` for a subset of
  "large" chapters), a definition of which chapters qualify, and re-verification that pre-rendered
  markup preserves the existing `enableAssistiveMml` screen-reader behavior and the lazy lookup this
  repo relies on (#3332-A, `ui/lazy`) — none of which the issue specifies, and getting any of it
  wrong risks a real accessibility or rendering regression on the heaviest, most math-dense
  chapters. That is a contested architecture/design decision (`tier:strong` territory per
  `AGENTS.md`'s Agent Tiers matrix — "architecture ... anything unclear" — not the well-specified,
  low-risk mechanical swap that `tier:cli` covers), not something to guess at. Recommended as a
  follow-up issue if the ~1% savings from option (a) alone do not meet the epic's performance
  budget (#4570, WEB-10.1).
- Also spotted, not fixed (out of scope for this issue): `_templates/latex_article.html` (a
  separate, unrelated ad hoc LaTeX→HTML conversion tool, not part of the Quarto site or the three
  heaviest chapters) loads the same `tex-mml-chtml.js`/hash pair without the gating this loader has;
  and the loader's `MathJax.svg: { fontCache: 'global' }` config block is currently unused dead
  configuration since the output jax is CHTML, not SVG, in both the old and new bundle. Neither is
  touched here since neither traces to this issue's acceptance criteria.

## Validation

- TDD: `tests/mathjax-loader.test.js` — added
  `loads the smaller TeX-input + CHTML-output component build (#4577)`, confirmed RED against the
  pre-change `tex-mml-chtml.js` source, then GREEN after the change.
- `npx jest tests/mathjax-loader.test.js` — 10 passed.
- `npx jest` (full suite) — 26 suites, 432 passed, 19 skipped, 0 failed.
- `python3 -m ruff check .` — all checks passed.
- `python3 -m black --check --line-length 100 .` — 748 files unchanged.
- **Not run:** `quarto render` / Playwright E2E (blocked by this session's sandbox permission
  policy, consistent with prior sessions' notes in this file) — the existing
  `tests/e2e/article.spec.js` assertion `script[src*="mathjax"][src*="/es5/tex-"]` count === 1
  already matches either bundle filename, so it is expected to keep passing under CI's real
  Quarto-rendered E2E run, but that run is the first actual execution against a live page.

## Blockers and Risks

- Blockers: none.
- Risk: none to rendering or accessibility — see "No change in rendering or accessibility" above.
  The ~1% size reduction is modest; if the epic's performance budget needs more, the follow-up
  above proposes the larger pre-rendering option as separate `tier:strong` work.

## Next Steps

1. Push the branch and open the draft PR referencing `Fixes #4577`; release the fleet lease.
2. Frontier review reads CI's `e2e-tests` run as the real MathJax-rendering evidence for the three
   heaviest chapters, since this session could not render the site locally.
3. If the epic's performance budget (#4570) still isn't met after this lands, open the recommended
   `tier:strong` follow-up for build-time SVG/MathML pre-rendering.

---

# Implementation Handoff — Social Cards per Page (#4578)
# Implementation Handoff — Wire Alt-Text and Long-Description Validation Into CI (#4567)

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

---

# Implementation Handoff — Create "How to Read This Site" Guide (#4491)

## Identity

- Repository: D-sorganization/AffineDrift
- Working directory: C:/Users/diete/Repositories/AffineDrift-worktrees/claude-4578
- Branch: claude/issue-4578
- Governing issue/epic: #4578 (WEB-10.10, part of epic #4579 "E10 — Performance, SEO, and Privacy")
- Pull request: opened as a draft by this session (see PR link in the commit that follows)

## Objective and Status

- Objective: generate per-book/per-series Open Graph social card images (title,
  badge, and the site signature graphic) at build time instead of relying on
  one site-wide card for every page.
- Status: **complete for the two stated acceptance criteria within this
  issue's scope**, with one caveat noted below.
- Completed:
  - TDD: `tests/test_social_cards.py` (7 tests, written first, RED confirmed
    against the missing module before implementation).
  - `scripts/generate_social_cards.py`: renders one 1200x630 PNG per
    configured book/series (badge pill + wrapped title + the existing
    `logo/logo-icon-512.png` signature graphic), following the same
    checked-in-asset + `--check` pattern as `scripts/optimize_images.py`'s
    existing site-wide `logo/og-card.png`.
  - `logo/social-cards/{physics-of-golf,geometry-of-motion,proximal-distal-energy-transfer}.png`:
    the three generated cards, checked in.
  - Per-page `open-graph`/`twitter-card` `image` overrides added to the three
    representative book/series landing pages
    (`articles/The_Physics_of_Golf/quarto/index.qmd`,
    `articles/The_Geometry_of_Motion/quarto/index.qmd`,
    `articles/proximal_distal_energy_transfer/index.qmd`), overriding the
    site-wide default set in `_quarto.yml`.
  - `.github/workflows/deploy-website.yml`: new "Verify Per-Book/Series Social
    Cards" step (`scripts/generate_social_cards.py --check`), mirroring the
    existing "Verify Optimized Image Derivatives" step.
- Caveat: the issue's second acceptance criterion ("Validated with a
  social-card debugger on three pages") requires a public, deployed URL for
  each page — social-card debugger tools (Facebook Sharing Debugger, Twitter
  Card Validator, opengraph.xyz, etc.) fetch the live page over HTTP and
  cannot be run against an unmerged branch or a local render. This PR
  implements and tests the generation and per-page wiring (the three chosen
  pages render valid, correctly sized OG/Twitter images with distinct
  title/badge per book), but the live debugger pass itself must happen after
  merge and deploy to `https://affinedrift.com`.
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

# Implementation Handoff — Deploy Website Claim-Audit Route Coverage (#4666)

## Identity

- Repository: D-sorganization/AffineDrift
- Branch: fix/main-is-red-deploy-website-4666
- Baseline commit: 45d9fca0 (origin/main)
- Governing issue: #4666 (main is red: Deploy Website, fleet-main-health)

## Objective and Status

- Objective: Restore green `Deploy Website` on `main` by adding newly created pages (`pages/glossary.html` and `pages/how-to-read.html`) to `data/trust/claim_audit_inventory.json` so that `--enforce-publication` coverage check succeeds during production website build.
- Status: Implementation complete, test suites passing; opening PR.
- Completed:
  - Added reviewed route entries for `/pages/glossary.html` and `/pages/how-to-read.html` to `data/trust/claim_audit_inventory.json` with self-contained byte evidence (SHA-256 digests).
  - Updated `DEFERRED_AUDIT_SCOPE_COUNTS` in `scripts/claim_audit_ids.py` for issue 4063 (from 13 to 15) to account for the two new pages.
  - Updated route partition test in `tests/test_claim_audit_inventory.py`.
  - Regenerated `data/trust/generated/claim_audit_report.json` and `reports/scientific-claim-audit.md`.
  - Verified with `scripts.generate_claim_audit_inventory --check --enforce-publication`.

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
  - Three representative landing pages (the two textbooks with dedicated
    `index.qmd` pages plus the one monograph) were chosen to satisfy "on three
    pages" concretely rather than generating cards for every book/series in
    the sidebar, which the issue did not ask for.
  - `ImageFont.load_default(size=...)` (Pillow >= 10.1) is used instead of a
    vendored or system TrueType font, so card rendering is deterministic
    across the Windows dev environment and the Linux CI runner without adding
    a new font asset.
  - Per-page `open-graph:`/`twitter-card:` YAML blocks (matching the same keys
    already used site-wide in `_quarto.yml`) were used for the override,
    rather than the generic Quarto `image:` field, to make the override
    explicit and symmetric with the site-level config it replaces.
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

- `python -m pytest tests/test_social_cards.py tests/test_image_budget.py -q` — 13 passed.
- `python -m ruff check scripts/generate_social_cards.py tests/test_social_cards.py` — PASS.
- `python -m black --check --line-length 100 scripts/generate_social_cards.py tests/test_social_cards.py` — PASS.
- `python scripts/generate_social_cards.py --check` — PASS.
- `python -m scripts.check_module_size_budget` — PASS.
- `python -m scripts.check_tech_debt_budget` — PASS.
- YAML frontmatter of the three edited `.qmd` files and the edited workflow
  file validated with `yaml.safe_load`.

## Blockers and Risks

- Blocker: none for the generation/wiring work in this PR.
- Risk: the live social-card-debugger validation (acceptance criterion 2)
  cannot be executed by an agent pre-merge; it needs a human or a follow-up
  automated check to run post-deploy against the three live URLs.

## Next Steps

1. After merge and the next site deploy, run a social-card debugger against
   the three pages' live URLs to close out acceptance criterion 2.

## Change Log

- `SELF` — Generate per-book/series Open Graph social cards at build time and wire three landing pages to use them (#4578).

---

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
- Working directory: C:/Users/diete/Repositories/AffineDrift-worktrees/claude-4567
- Branch: claude/issue-4567
- Baseline commit: 02507aac
- Implementation commit: SELF
- Pull request: not created yet (draft PR opened this session)
- Governing issue/epic: #4567 (epic #4569)

## Objective and Status

- Objective: Wire `scripts/validate_accessibility.py` into `quality-gate` and add a check requiring complex E8 SVG diagrams to carry a long description.
- Status: Implementation complete; draft PR pending.
- Completed:
  - Added `check_long_description_for_diagrams()` to `scripts/validate_accessibility.py`: flags an SVG image reference in a QMD file unless the file also has an `aria-describedby` resolved to an in-page element, or a `<details>` "long description" disclosure.
  - Fixed a pre-existing latent bug: the QMD loop in `validate_accessibility()` called `qmd_file.relative_to(repo_root)`, but `collect_qmd_files()` returns CWD-relative paths, not absolute ones, so any real finding crashed the script (previously dormant because every existing check found zero issues repo-wide). Now uses the path as-is, matching `seo_audit.py`'s convention.
  - Discovered the new check would flag 39 pre-existing QMD files whose SVG figures are matplotlib-generated data plots that predate the E8 diagram work, not the hand-authored explanatory diagrams E8 specifies. Added `config/accessibility-long-description-baseline.json` (same `_comment`/`accepted` shape as `tree-parity-baseline.json`/`terminology-baseline.json`) to grandfather them, so the new check only blocks new/changed content.
  - Discovered the script's existing CSS colorblind-safe-color and JS ARIA-label checks also have unrelated pre-existing findings (dozens of CSS colors, `js/main.js`) with no baseline. Added a `--qmd-only` flag to `validate_accessibility()`/`main()` so CI wires only the in-scope checks (alt text, heading hierarchy, long descriptions); the CSS/JS checks stay unwired pending their own baseline/cleanup work (out of #4567's scope; flagged in the PR body).
  - Added `.github/workflows/ci-standard.yml` step "Verify Alt Text and Long Descriptions" running `python3 scripts/validate_accessibility.py --qmd-only` in the `static-checks` job that feeds `quality-gate`.
  - Added tests in `tests/test_validate_accessibility.py` for the new check (non-SVG images ignored, missing long description flagged, `aria-describedby` pass, `<details>` disclosure pass, dangling `aria-describedby` still flagged).
  - Added a `SPEC.md` change-log row keyed to #4567.
- Remaining: Open the draft PR.
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
  - `scripts/validate_accessibility.py`: new `check_long_description_for_diagrams()`, baseline loader, `qmd_only` param, `--qmd-only` CLI flag, `relative_to` bugfix.
  - `config/accessibility-long-description-baseline.json`: new baseline of 39 pre-existing files.
  - `tests/test_validate_accessibility.py`: new `TestLongDescriptionForDiagrams` class.
  - `.github/workflows/ci-standard.yml`: new CI step in `static-checks`.
  - `SPEC.md`: change-log row.
  - `docs/development/HANDOFF.md`, `docs/development/DEVELOPMENT_LOG.md`: this entry.
- Key decisions:
  - "Complex diagram" is scoped to SVG image references, matching E8's stated format (WEB-08.2/08.3 specify SVG diagrams with a long description); PNG/JPEG figures are unaffected.
  - The long-description check is file-wide (permissive), matching this module's existing style (`check_colorblind_safe_colors`'s docstring states the same rationale) rather than requiring a 1:1 image-to-description mapping.
  - CSS/JS checks are deliberately left out of the CI step rather than baselined, since remediating dozens of CSS color findings and the JS ARIA gap is unrelated scope; this is called out as a known gap in the PR body rather than silently fixed or silently wired in as a failure.
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

- `python -m pytest tests/test_validate_accessibility.py` — PASS (20 passed)
- `python -m ruff check scripts/validate_accessibility.py tests/test_validate_accessibility.py` — PASS
- `python -m black --check --line-length 100 scripts/validate_accessibility.py tests/test_validate_accessibility.py` — PASS
- `python3 scripts/validate_accessibility.py --qmd-only` (PYTHONPATH=.) — exit 0 across the full repo
- `python3 -m scripts.check_spec_changelog` — PASS
- `python3 scripts/check_module_size_budget.py` — PASS
- `python3 scripts/check_root_hygiene.py` — PASS
- `python3 scripts/check_workflow_action_pins.py` — PASS
- `pytest tests/test_link_checker_script.py` — PASS (12 passed)
- `pytest tests/test_link_checker_script.py tests/test_check_links.py tests/test_check_links_additional.py tests/test_link_utils.py` — PASS (79 passed)
- `python -m ruff check scripts/link-checker.py tests/test_link_checker_script.py` — PASS
- `python -m black --check --line-length 100 scripts/link-checker.py tests/test_link_checker_script.py` — PASS
- `python -m scripts.check_spec_changelog` — PASS

## Blockers and Risks

- Blockers: none.
- Risks/assumptions: the 39-file baseline is a one-time grandfather; new SVG diagrams added anywhere (including under E8) must supply a long description or add themselves to the baseline (not recommended) to pass CI. The CSS/JS checks remaining unwired is a known gap, not a defect introduced by this change.

## Next Steps

1. Open the draft PR for #4567 and note the unwired CSS/JS checks as follow-up scope in its body.

---


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

# Implementation Handoff — Real Publication Dates and Per-Article Change History (#4545)

## Identity

- Repository: D-sorganization/AffineDrift
- Working directory: C:/Users/diete/Repositories/AffineDrift
- Branch: fix/web-07-3-real-dates-and-change-history-4545
- Baseline commit: ebced38fbe6908492e5c8e2ff08866516f5691c0
- Implementation commit: SELF
- Pull request: #4640
- Governing issue/epic: #4545 (epic #4552)

## Objective and Status

- Objective: Eliminate build-time `date: today` across all rendered sources, enforce verified `date-source:` metadata, add `date-modified:` derived from substantive changes, and build a front-matter driven `changes:` Revision History section for core pages.
- Status: ready for commit / PR
- Completed:
  - Eliminated `date: today` across all 12 articles, marking unverified first-publication dates as `Date unverified` with `date-source: unverified`.
  - Added `date-source: initial-publication-record` across all 35 articles with concrete publication dates.
  - Derived `date-modified` from substantive commit history and latest changes.
  - Added structured `changes:` revision history to the 10 core theory and foundational pages.
  - Created Pandoc Lua filter `scripts/filters/revision-history.lua` rendering accessible semantic `<section id="revision-history">` before references.
  - Created CSS component `css/components/revision-history.css` registered in `styles.css` with print styles in `css/print.css`.
  - Registered `scripts/filters/revision-history.lua` in `_quarto.yml`.
  - Created automated validator `scripts/derive_substantive_dates.py` supporting `--check`.
  - Created comprehensive TDD test suite `tests/test_dates_and_history.py` (16 tests, all passing).
  - Regenerated claim audit evidence digests and verified all contracts pass.
  - Added change-log row in `SPEC.md`.
- Remaining: Monitor PR #4640 CI and auto-merge into main.

## Files and Decisions

- Files changed:
  - `_quarto.yml`: Registered `scripts/filters/revision-history.lua`.
  - `articles/*.qmd`: Replaced `date: today` with `Date unverified` and `unverified` source; added `date-source` and `date-modified`; added `changes:` to core pages.
  - `css/components/revision-history.css`: Component styling.
  - `css/print.css`: Print styling avoiding page breaks inside revision history.
  - `styles.css`: Component import.
  - `scripts/filters/revision-history.lua`: Pandoc filter for revision history rendering.
  - `scripts/derive_substantive_dates.py`: Date metadata derivation and check script.
  - `tests/test_dates_and_history.py`: Unit and contract tests for dates and revision history.
  - `SPEC.md`: PR change-log row.
  - `docs/development/HANDOFF.md`: Updated durable handoff state.
- Key decisions: Unverified dates show 'Date unverified' and emit no citation date; verified dates require 'date-source'; revision history driven from 'changes:' front matter and placed before references by Lua filter.
- User-owned or unrelated worktree changes: none observed

## Validation

- `pytest tests/test_dates_and_history.py` — PASS (16 passed)
- `python -m scripts.derive_substantive_dates --check` — PASS
- `python -m ruff check scripts/derive_substantive_dates.py tests/test_dates_and_history.py` — PASS
- `python -m black --check --line-length 100 scripts/derive_substantive_dates.py tests/test_dates_and_history.py` — PASS
- `npm run lint:css` — PASS
- `python scripts/check_css_architecture.py` — PASS
- `python scripts/check_root_hygiene.py` — PASS
- `python -m src.tools.site_link_gate` — PASS
- `python -m scripts.regenerate_claim_audit_evidence --check` — PASS
- `python scripts/check_spec_changelog.py` — PASS

## Blockers and Risks

- Blockers: none
- Risks/assumptions: none

## Next Steps

1. Monitor PR #4640 CI and auto-merge into main.

## Change Log

- 02507aac — Extend personas to include curious golfer/coach and student (#4488) (#4638).
- ebced38f — Build the page header card component (#4507) (#4633).
- `SELF` — Extend critique annotations to ZTCF and Proximal-Distal pages (#4524).

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

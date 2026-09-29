# Implementation Handoff — Readable Claim Ledger Page (#4523)

## Identity

- Repository: D-sorganization/AffineDrift
- Working directory: C:/Users/diete/Repositories/AffineDrift-worktrees/claude-4523
- Branch: claude/issue-4523
- Baseline commit: 46df5059
- Implementation commit: SELF
- Pull request: not created
- Governing issue/epic: #4523 (epic #4530)

## Objective and Status

- Objective: Add a dedicated `evidence/claims.qmd` page, generated from the governed
  claim registry, with one accessible card per claim (plain statement, formal
  statement, evidence rung, falsifiers, related critiques, and the pages making the
  claim), and link every claim-making page back to its ledger entry.
- Status: implementation complete; draft PR not yet opened.
- Completed: New `scripts/generate_claims_ledger.py` generator (reusing
  `generate_trust_panels.load_registry`, `generate_claim_critique_ledger.load_ledger`,
  and the `evidence_presentation` projector/renderer for the evidence-rung badge);
  new `evidence/claims.qmd` page; generated `_includes/generated/claims-ledger.qmd`
  and per-page link partial `_includes/generated/claims-ledger/controllability-drift-ratio.qmd`;
  `articles/controllability-drift-ratio.qmd` now includes its generated ledger link;
  `evidence/**/*.qmd` added to the `_quarto.yml` render list; `evidence` added to
  `src/tools/site_page_scan.py`'s `CONTENT_DIRS` (and its pinned test) so the site
  link gate (categories, Related Articles, orphan check) covers the new page.
- Remaining: Open the draft PR; frontier review.

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
  - `articles/controllability-drift-ratio.qmd`: Added a Quarto include of the
    generated `_includes/generated/claims-ledger/controllability-drift-ratio.qmd`
    partial, next to the existing scientific-trust-panel include.
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
    since editing `articles/controllability-drift-ratio.qmd` and adding its new
    included source changed the bytes the claim-audit ledger pins (the
    `claim-audit-evidence` pre-commit hook, AffineDrift #4124).
  - `tests/test_claims_ledger.py`: New TDD suite covering card projection (plain/
    formal statement, rung, full falsifier list, related critiques, pages making the
    claim), accessible rendering (`role="region"`, `aria-label`, human-readable
    anchor), generator determinism, per-page link generation, and staleness detection.
  - `docs/development/DEVELOPMENT_LOG.md`: Added `DL-#4523`.
  - `SPEC.md`: Added the #4523 change-log row.
- Key decisions:
  - Reused the existing `data-trust-claim` anchor convention (already present on
    `articles/controllability-drift-ratio.qmd`) to discover "pages making the
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
- Not run locally: `quarto render` (~14 min full-site render per `CLAUDE.md`) and the Playwright E2E/axe-core lane, which depends on it.

## Blockers and Risks

- Blockers: none.
- Risks/assumptions: Accessibility of the rendered page (axe-core, per the E2E lane)
  was not verified against a real Quarto render in this session — the markup follows
  the same `role="region"`/`aria-label`/semantic-heading pattern already used and
  tested elsewhere on the site (`render_evidence_card`), so it is expected to pass,
  but this is not confirmed end-to-end.

## Next Steps

1. Open the draft PR for #4523 with `Fixes #4523`.
2. Frontier review; if `quarto render` + Playwright axe-core surfaces an accessibility
   issue on `evidence/claims.html`, fix the markup in `scripts/generate_claims_ledger.py`.
3. Release agent lease for #4523.

## Change Log

- SELF — Add the reader-facing Claim Ledger page, its generator, and per-page links (#4523).

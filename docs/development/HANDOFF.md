# Implementation Handoff

Keep this file current and concise. Replace instructional placeholders; do not append an unbounded transcript.

## Identity

- Repository: `D-sorganization/AffineDrift`
- Working directory: `C:/tmp/AD_w3899` (branch `claude/issue-3899-link-checker`, based on `origin/staging`)
- Branch: `claude/issue-3899-link-checker`
- Baseline commit: `f6adaa2` (fix(ci): add Bandit SAST and detect-secrets blocking security gates (#3029))
- Implementation commit: `SELF` — the commit containing this update; resolve with `git rev-parse HEAD`
- Pull request: #4268 (https://github.com/D-sorganization/AffineDrift/pull/4268, open against `staging`)
- Governing issue/epic: #3899 (C3 of epic #3896); defect-class reference #3906

## Objective and Status

- Objective: extend the existing link checker (`src.tools.check_links`, no new tool) with source-level site link quality checks — include-aware internal link resolution, page-link path-style normalization, Related-Articles coverage, orphan detection — wire it into the `ci-standard.yml` quality gate, and document exit codes in `docs/LINK-CHECKER.md`.
- Status: complete (ready for review)
- Completed: all four checks implemented TDD-first (RED = pytest collection failure of `tests/tools/test_link_checks.py` before implementation; GREEN = 25 focused tests pass); include-aware resolution reproduces the exact #3906 `data/...`/`../figures/` defect class in fixture tests; repo-level RED run captured 138 baseline violations, GREEN run exits 0 with everything budgeted; the single fixable path-style defect (`ch03_double_pendulum.qmd` root-absolute notation link) corrected to `../../../pages/notation-conventions.html`; budget baselines recorded in `config/link_checker_budget.json` (62 related-coverage pages, 39 orphans, 11 `.qmd`-extension files / 17 links, 1 root-absolute include file).
- Remaining: ratchet the budget file as follow-up issues (C4-C9) remediate baselines; CI run on the PR itself (checked once post-open per fleet rules).

## Files and Decisions

- Files changed:
  - `src/tools/utils/link_checks.py` (new) — the four source-level checks, budget orchestration, `run_source_checks` exit-code contract.
  - `src/tools/utils/site_config_utils.py` (new) — render-config and navigation parsing (`collect_nav_pages` covers `href` + book `chapters` across every `_quarto.yml`, including nested book projects).
  - `src/tools/utils/link_utils.py` — added include-shortcode/related-section extraction, moved `find_links` here (re-exported by `check_links`), centralized resolution helpers (`html_target_resolvable`, `internal_link_resolvable`, browser-semantics `page_target_key`).
  - `src/tools/check_links.py` — legacy scan preserved; new `main()` with `--source-checks` / `--config` flags; resolution logic now delegates to `link_utils` (no duplicate logic).
  - `config/link_checker_budget.json` (new) — baseline budgets; ratchet down over time.
  - `docs/LINK-CHECKER.md` (new) — check semantics, budget keys, exit codes.
  - `.github/workflows/ci-standard.yml` — one new quality-gate step (`python3 -m src.tools.check_links --source-checks`).
  - `docs/development/QUALITY_GATES_POLICY.md` — gate registered.
  - `articles/The_Physics_of_Golf/quarto/ch03_double_pendulum.qmd` — 1-line path-style fix (root-absolute → parent-relative).
  - `tests/tools/test_link_checks.py` (new), `tests/test_check_links_additional.py` — focused tests incl. CLI.
  - `docs/development/HANDOFF.md`, `docs/development/DEVELOPMENT_LOG.md` (new, fleet-mandated; will textually conflict with sibling PRs that created the same files — resolve by taking the richer merged version).
- Key decisions:
  - Extended the existing tool (`python3 -m src.tools.check_links`) instead of adding a new one, per issue scope; `scripts/link-checker.py` named in the issue does not exist on staging — `src/tools/check_links.py` is the actual link-checking tool (CI: deploy-website.yml).
  - Include-aware resolution: links in ``{{< include >}}``d files resolve against the including page; a link is flagged in every render context (standalone + each includer), deduped to one report line preferring the context-annotated variant.
  - Baselines use the repo's standard `config/` budget pattern with per-file allowlists (not numeric caps) so any violation in a new/unfixed file fails while known ones are reported as budgeted counts.
  - Hub pages (`hub_pages`) are exempt from related-coverage and treated as orphan-gate roots; content universe via `content_page_globs` excludes book-chapter interiors by construction.
  - Broken internal links and missing include targets are unbudgeted (always fail); the deployed `#3906` defect class is proven by fixture tests mirroring the shipped chapter names/paths.
  - Rejected alternative: numeric caps for path style (allows trading old violations for new); rejected new standalone script (violates "extend, don't add").
- User-owned or unrelated worktree changes: none observed; sibling-owned files untouched (six motor-control cluster pages left to PR #4265).

## Validation

- `python -m pytest tests/tools/test_link_checks.py -q` — 25 passed.
- `python -m pytest tests/test_check_links.py tests/test_check_links_additional.py tests/tools/test_check_links.py tests/test_link_utils.py -q` — 89 passed (no legacy regressions).
- `python -m pytest tests/test_check_links.py tests/test_check_links_additional.py --cov=src.tools.check_links --cov-fail-under=70 -q` — 98.6% (critical-module threshold met).
- `python -m src.tools.check_links --source-checks` — RED (pre-budget): 138 violations (62 related-missing, 39 orphans, 17 `.qmd`-extension links in 11 files, 20 root-absolute links incl. `ch03_double_pendulum.qmd:60`); GREEN (post-budget + ch03 fix): 0/0/0/0, exit 0.
- `python -m src.tools.check_links` — legacy scan unchanged: "No broken internal links found."
- `black --line-length 100` and `ruff check` clean on all changed Python files; `mypy` clean on changed modules (pre-existing `conversion_utils.py:108` arg-type error on HEAD is unrelated and disclosed in the PR).

## Blockers and Risks

- Blockers: none.
- Risks/assumptions: related-coverage allowlist (62 pages) and orphan allowlist (39 pages) are large because the #3896 child issues (C4-C9) own the remediation; the gate still fails on any new unlisted page. `HANDOFF.md`/`DEVELOPMENT_LOG.md` are new files and will conflict with sibling fleet PRs (#4265 and similar) — resolve by keeping both sections during merge. Pre-existing mypy error in `src/tools/utils/conversion_utils.py:108` surfaces under local mypy 2.1.0 on clean HEAD; unrelated to this change.

## Next Steps

1. Rebase this branch over `origin/staging` after PR #4265 lands, union-resolving the new HANDOFF/DEVELOPMENT_LOG files, then watch the `ci-standard.yml` "Verify Site Link Quality" step run green on PR #4268.

## Change Log

- `SELF` — Initial handoff for the #3899 site link quality gate (checks, budgets, CI wiring, docs, ch03 path fix).
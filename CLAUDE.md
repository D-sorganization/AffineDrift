# CLAUDE.md — AffineDrift

> **GAAI Fleet Member.** GAAI framework installed in `.gaai/`. Read `.gaai/core/GAAI.md` for full governance spec.
> Rules: `@.gaai/core/contexts/rules/base.rules.md` and `@.gaai/project/contexts/rules/project.rules.md`
> All work on `staging` branch. PRs target `staging`. Never push directly to `main`.

## What This Is

Educational textbook and companion website for engineering mathematics. Content is
authored in Quarto (.qmd files) and rendered to HTML. Combines narrative text,
interactive code cells, and mathematical visualizations.

## Key Directories

- `chapters/` or `content/` — Quarto `.qmd` source files (the textbook)
- `css/` — canonical stylesheets (CSS budget enforced by CI)
- `docs/` — rendered output; CSS mirrors enforced by CI to match `css/`
- `tests/` — pytest (Python) and Jest (JavaScript) test suites
- `e2e/` or `tests/e2e/` — Playwright end-to-end browser tests
- `references/` — BibTeX bibliography files

## Python and Tooling

- **Python 3.12**. Use `python3`.
- **Formatter:** Black (NOT Ruff format). **100-char line limit.**
- **Linter:** Ruff check.

## Development Commands

```bash
python3 -m ruff check .                               # lint
python3 -m black --check --line-length 100 .           # format check (Black!)
python3 -m black --line-length 100 .                   # auto-format
python3 -m pytest --cov --cov-fail-under=50            # Python tests (50% min)
npx jest                                               # JavaScript tests
npx playwright test                                    # E2E browser tests
quarto render                                          # build the site
```

## CI Requirements (All Must Pass)

1. `ruff check` — zero violations
2. `black --check --line-length 100` — zero diffs (NOT ruff format)
3. CSS budget validation — stylesheet sizes within configured limits
4. Bibliography quality check — BibTeX well-formed, no broken refs
5. DRY adoption tracking — duplication metrics monitored
6. Module size budget — enforced per-file
7. pytest with **50% coverage minimum** — coverage must not decrease
8. Jest — all JS tests pass
9. Playwright E2E — critical user flows pass
10. CSS mirror enforcement — `css/` must be mirrored in `docs/` (never edit `docs/` CSS directly)
11. No `print()` in `src/` — use logging
12. No TODO/FIXME unless tied to a tracked GitHub issue

## Content Authoring

- Write in `.qmd` using Quarto markdown. Executable cells use `{python}` or `{javascript}` fenced blocks.
- Cross-references: `@sec-`, `@fig-`, `@eq-` syntax. New chapters need an entry in `_quarto.yml`.
- Bibliography: add entries to references dir, cite with `[@key]`.
- Images must have alt text. Math uses MathJax/KaTeX.

## Known Constraints

- **Black with 100-char lines.** Do not configure or run `ruff format` in this repo.
- **Quarto rendering** can be slow; CI may only render changed chapters.
- **Playwright** requires `npx playwright install` for browser binaries before first run.
- **CSS lives in two places:** edit in `css/`, CI validates that `docs/` mirrors match. Never edit rendered CSS directly.

## Coding Standards (Enforced by CI and QA)

- **DRY:** CI tracks duplication. Extract shared Quarto includes and Python utilities. No copy-paste between chapters.
- **DbC:** Validation functions check inputs, raise clear errors with context.
- **LOD:** No method chains >2 levels. Keep rendering logic separate from content logic. Complex Python goes in importable modules, not inline in QMD.
- **TDD:** New Python utilities need pytest tests. New interactive features need Jest tests. Coverage stays above 50%.

## Cross-Repo Dependencies

- **Standalone.** AffineDrift does not import from other fleet repos.
- Shared engineering principles (DRY tracking, module budgets) are consistent across the fleet but implemented independently here.

## Slash Commands

- `/gaai-deliver` — Run Delivery Loop for next ready backlog item
- `/gaai-status` — Show current backlog and memory state

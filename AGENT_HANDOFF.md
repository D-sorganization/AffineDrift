# Agent Handoff — AffineDrift

> Update this file with every PR and every push to main.

Last updated: 2026-08-09

## Where This Repo Is Heading

AffineDrift is the educational textbook + companion website (Quarto → GitHub Pages)
for engineering mathematics, plus a growing set of AffineDrift-relevant research
articles that support a fleet-wide "Shared Web Tools" program.

Active epics/PRs:

- **#3792 / PR #3793 — repair the local-only runner guard** (in progress). Removes raw
  Actions-expression delimiters from the workflow's embedded Python so GitHub
  can parse push events, with a deployment-integrity regression test. The same
  recovery PR corrects eight proximal-to-distal figure paths identified by the
  post-merge Pages pre-build link gate.
- **#3791 — proximal-to-distal open research refinement** — MERGED
  (`7b1a06c7`). Removes meta and software-promotion framing, clarifies evidence
  boundaries, and adds the 13-case parameter-sensitivity result from merged
  UpstreamDrift PR #8428. The remaining validation roadmap stays open in
  UpstreamDrift epic #8426.
- **#3777 — EPIC: Sharable Web Tools Program** (open). Converts AffineDrift-relevant
  analysis tools (Tools repo) into GitHub-Pages-hosted web models with a parity
  process against the canonical PyQt6 implementations. Workstreams: simulation
  platform web release, WASM parity upgrade, parity review checklist, candidate
  tool selection, shared mirror-repo infra, executables track. Cross-refs:
  D-sorganization/Tools#4103, D-sorganization/UpstreamDrift#8339,
  D-sorganization/Repository_Management#1387.
- **#3778 — putting research articles (H4, Tools#4125)** — MERGED (PR #3778,
  commit ada43cd3). Added `articles/putting-roll-models.qmd` and
  `articles/green-simulation.qmd`. No longer in flight; kept here as recent
  context since #3777 references the same putting vertical.

## Must-Read Architecture Pointers

1. `AGENTS.md` (repo root) — authoritative agent directives: coding standards,
   TDD, network/API hygiene, fleet-managed sections (do not hand-edit blocks
   marked `<!-- BEGIN FLEET-MANAGED -->`; edit the source in
   Repository_Management/AGENTS.md instead).
2. `CLAUDE.md` (repo root) — condensed dev-commands + CI-requirements summary;
   also points at `.gaai/core/GAAI.md` for the GAAI fleet framework.
3. `SPEC.md` — specification of record; `spec-check.yml` CI requires it be
   updated alongside changes to `src/`, `tests/`, `config/`, `pyproject.toml`,
   `Cargo.toml`, `CMakeLists.txt`, `package.json`, or `requirements.txt`
   (label `spec-exempt` to bypass when genuinely not applicable).
4. `.github/workflows/ci-standard.yml` — the real quality-gate job list (article
   content: title case, single-title, display-math, LaTeX quotes/environments,
   terminology, bibliography, frontmatter, plus Python/JS budgets and tests).
5. `.github/workflows/deploy-website.yml` — the Pages build/deploy pipeline;
   its `scripts/check_*.py` steps are the closest thing to "docs governance"
   but are scoped to `.qmd`/`articles/` content, not root-level markdown.

## In-Flight Branches

- `fix/affine-runner-guard-expression-8426` (this branch) — based on merged
  PR #3791 at `7b1a06c7`; fixes AffineDrift issue #3792.
- `docs/agent-handoff-1390` (legacy handoff-policy branch) — stacks on `origin/main`
  (b2e98ae3). Adds this file and the AGENTS.md policy section. No other
  branch currently stacks on it.
- Other open remote branches exist (see `git branch -r`) but none were found
  stacked on this work; treat each as independent unless its own PR says
  otherwise.

## Gate Commands (run before pushing)

```bash
python3 -m ruff check .                               # lint
python3 -m black --check --line-length 100 .           # format check (Black, not ruff format)
python3 -m pytest --cov --cov-fail-under=65 --timeout=120   # Python tests, 65% min coverage
npx jest --coverage                                     # JavaScript tests
npx playwright test                                     # E2E (needs `npx playwright install` first)
quarto render                                           # build the site (Quarto 1.6.39 in CI)
python3 scripts/check_quarto_render_coverage.py
python3 scripts/check_title_case.py
python3 scripts/check_single_title.py
python3 scripts/check_dependency_boundaries.py
python3 scripts/check_js_dependency_boundaries.py
python3 scripts/check_module_size_budget.py
python3 scripts/check_changed_file_size_budget.py
python3 scripts/check_tech_debt_budget.py
python3 scripts/check_dry_adoption.py
```

Full authoritative list: `.github/workflows/ci-standard.yml` (`quality-gate` and
`tests` jobs) and `.github/workflows/deploy-website.yml` (`build` job, main-only).

## Do-Not List

- Do not edit `docs/` HTML/CSS directly — it is Quarto-generated output; edit
  `css/` (canonical) and let CI mirror-check `docs/css/`.
- Do not run `ruff format` in this repo — formatting is Black, 100-char lines.
- Do not add cross-repo imports — AffineDrift is standalone by design
  (`AGENTS.md` "Cross-Repo Dependencies").
- Do not hand-edit `<!-- BEGIN FLEET-MANAGED -->…<!-- END FLEET-MANAGED -->`
  blocks in `AGENTS.md` — they sync from Repository_Management/AGENTS.md.
- Do not commit `.codemap/` or `.codemap/index.db` (cache/artifact data).
- Do not use `git commit --no-verify` / `--push --no-verify` as a routine
  workaround — see `CLAUDE.md` "Hook bypass policy".
- Do not change source files without updating `SPEC.md` in the same PR
  (`spec-check.yml` blocks on staleness; use `spec-exempt` label only when
  genuinely inapplicable).
- Do not open PRs as drafts — this epic requires full, ready-for-review PRs.
- Self-approval is blocked (`block-self-merge.yml`); a PR still needs a
  human/other-agent review before `gh pr merge --auto` will complete.

## Short-Term Roadmap (ordered)

1. Land this handoff-policy PR (Repository_Management#1390) for AffineDrift.
2. Progress #3777 workstreams: candidate-tool selection and the first formal
   parity review (Rate of Closure tool, PyQt6 vs web).
3. Track Tools PR #4119 (consolidated Swing–Impact–Ball-Flight platform) and
   update the mirror/Pages deployment + article links once it merges.
4. Begin the WASM parity upgrade to retire interim TS ports (P7 of Tools
   epic #4103).
5. Write and apply the per-tool parity review checklist as a repeatable
   process for future tool releases.

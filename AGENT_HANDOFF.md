# Agent Handoff — AffineDrift

> Update this file with every PR and every push to main.

Last updated: 2026-08-11

## Where This Repo Is Heading

AffineDrift is the educational textbook + companion website (Quarto → GitHub Pages)
for engineering mathematics, plus a growing set of AffineDrift-relevant research
articles that support a fleet-wide "Shared Web Tools" program.

Active epics/PRs:

- **UpstreamDrift #8493 ground-reaction drift attribution** — UpstreamDrift PR
  #8494 merged to remote `main` at
  `06a0ca6317f6351e5b6da3789d2cd8e1e3dc53b5`, with the raced SPEC freshness
  follow-up #8495 merged at `33ec92f04ee80b5ac2200488e10a4531eecf1892`.
  AffineDrift PR #3802 pins the scientific merge and replaces the textbook GRF chapter's sign error,
  universal zero-work claim, unique muscle-torque inference, and single optimal
  waveform framing with a constrained-wrench treatment. The public
  proximal-to-distal article now reports the fixed-support benchmark,
  pointwise ZTCF/ZVCF overlap, cancellation-safe impulse interpretation, and
  participant-held-out falsification protocol. Primary references were added
  to both bibliographies and scientific boundary tests fail on regression.

- **#8458 / UpstreamDrift #8470 — hand-path force attribution** (publication
  integration complete on this branch). UpstreamDrift PR #8473 merged to remote
  `main` at `69eb7e9db32ccd17e45824619315b1d04b400c27`. AffineDrift pins that
  exact commit, compact three-tier results, and eight SHA-256-verified SVGs;
  reports force, impulse, power, work, every-joint/time-window, two-hand-mode,
  and bounded-preview findings; and preserves the model-only/biological-effort
  boundary. The affected Quarto article renders successfully; all image paths
  resolve, the evidence figures were visually inspected, 3,015 full-suite tests
  and 44 content-lint tests pass, and measured coverage is 93.35%. Remaining
  PR #3799 merged to remote `main` at
  `f9a5dee8a21838c87202bd3be405c4b977e9ed8c`. Post-merge Linux CI exposed one
  CRLF-derived preactivation-SVG manifest digest; the current hotfix pins the
  canonical LF Git-blob digest without changing figure content or scientific
  results.
- **Document title capitalization** — this branch extends the established
  Quarto gate to LaTeX structural titles, normalizes the tracked canonical
  LaTeX corpus, preserves technical literals such as `A/S`, `et al.`, and
  `mph`, and records the fleet convention in `AGENTS.md` and `SPEC.md`.

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

- `research/hand-path-force-attribution-8470` (this branch) — consumer-side
  schema, validator, tests, pinned evidence, and article/theory integration for
  epic #8458. Exact upstream pin: `69eb7e9db32ccd17e45824619315b1d04b400c27`.
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

1. After UpstreamDrift #8470 merges, copy only its compact publication
   artifacts, pin the full merged SHA and SHA-256 values in
   `data/proximal_distal_energy_transfer/hand_path_attribution_snapshot.json`,
   populate the declared tiers/quantities, run
   `python3 scripts/check_proximal_distal_evidence.py --require-pinned`, render,
   and visually inspect the article before publishing numerical claims.
2. Land this handoff-policy PR (Repository_Management#1390) for AffineDrift.
3. Progress #3777 workstreams: candidate-tool selection and the first formal
   parity review (Rate of Closure tool, PyQt6 vs web).
4. Track Tools PR #4119 (consolidated Swing–Impact–Ball-Flight platform) and
   update the mirror/Pages deployment + article links once it merges.
5. Begin the WASM parity upgrade to retire interim TS ports (P7 of Tools
   epic #4103).
6. Write and apply the per-tool parity review checklist as a repeatable
   process for future tool releases.

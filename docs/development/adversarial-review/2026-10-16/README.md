# Adversarial Review — AffineDrift (2026-10-16)

> An adversarial review assumes the code is wrong until shown otherwise. Every finding below cites a file and line
> that the reviewer read. Findings are **proposals**: each page carries a draft PR title, a pitch for why the change
> earns its place in the queue, and a PR body you can paste. Nothing here was changed in the code itself.

**Repository:** [D-sorganization/AffineDrift](https://github.com/D-sorganization/AffineDrift) · **Findings:** 35 (🟥 Critical: 1 · 🟧 High: 4 · 🟨 Medium: 12 · ⬜ Low: 18)

## Executive Read

AffineDrift is a Quarto research site + textbook corpus (396 .qmd, 161 .tex, 242 committed PDFs) with a
~36k-LOC Python package whose *scientific kernel* is small: `dynamics.py`, `golf_model.py`,
`double_pendulum_affine.py`, `rnea.py`, `lqr.py`, `swing_analysis.py`, `impact_contact_models.py`, `ilqr_solver.py`
(~2.5k LOC). That kernel is **correct**: I verified Ṃ−2C skew-symmetry (3e-16), closed-form vs Christoffel C
(1e-12), RNEA vs Lagrangian (1e-9), energy drift under RK4 (1e-9 rel), the constrained-field projector, and
`drift + M⁻¹τ = forced` to machine precision. The ZTCF *pointwise* decomposition (`drift_acceleration`,
`SwingAnalysis.joint_acceleration_components`) is exactly `−M⁻¹(Cq̇+g)` and `M⁻¹τ` at each measured state.
Ruff and Black pass as cloned; the 775 math-adjacent tests pass.

The three things that would hurt most in journal review:
1. **Four headline figures in the ZTCF and Superposition articles are hand-drawn parametric curves** (logistic,
   sine, power laws) captioned as computed trajectories, decompositions and "Exact Nonlinear" results, with
   quantitative legends ("-62% speed", "48.2 m/s") — while a working `GolfModel` sits beside them.
2. **The site defines ZTCF as a four-member family whose only governed executable, the fixture, the explorer
   widget and the article abstract are the *forward-integrated* construction** — the opposite of the manuscript's
   pointwise thesis. A reviewer who follows the supplementary links will find the website contradicting the paper.
3. **The claims machinery verifies bytes, not science.** 1016 "evidence paths" are 87 % prose/PDF/CSS/JSON logs;
   the gate checks that SHA-256s match whatever `regenerate` last blessed. 11 of 12 registry claims are
   `not_reviewed`, 27 of 35 critiques are `open` including one `critical` with no open-date against a declared
   14-day SLA.

## Coverage Statement

**Read line by line (every line):** `src/affine_control/{dynamics,double_pendulum_affine,ztcf_contract,
ztcf_explorer,golf_model,golf_model_3d,rnea,reachability,residuals,lqr,ddp,swing_optimizer,swing_analysis,
ucm_analysis,impact_contact_models,arm_viewer_frames,impedance_sources}.py` (≈3.6k LOC);
`src/affine_control/programming_companion/{consumer,transport,policy,validation,models(1-80)}.py`;
`src/core/constants.py`, `src/core/optimizers/{ilqr_solver,optimizer_factory}.py`; `src/golf_simulation/ball_flight.py`;
`src/tangent_models/examples.py` (140-260); `src/tools/rl_funnel_dynamics.py`; `scripts/claim_audit_evidence.py`,
`scripts/check_proximal_distal_evidence.py`, `scripts/core_theory_figures/ztcf.py` (large parts), `service-worker.js`,
`.github/workflows/ci-standard.yml` (lines 1-650 + quality-gate), `CLAUDE.md`, `AGENTS.md`, `pyproject.toml`,
`package.json`, `.pre-commit-config.yaml` (grep), `tests/test_applications_model_rigor.py` (55-249),
`tests/test_dcr_reachability_contract.py`, `tests/test_ztcf_intervention_contract.py` (outline),
`tests/ztcf-explorer.test.js`, `tests/e2e/ztcf-explorer.spec.js`, `tests/test_wheel_packaging.py` (15-44).

**Swept (grep / structural read, not every line):** the ~9.7k-LOC protocol/fixture/evidence declaration family
(`impedance_*`, `hand_wrench_*`, `neural_timing_*`, `population_generalization*`, `equipment_response*`,
`model_ladder*`, `impact_contact_{protocol,fixtures,uncertainty}`, `research_readiness/`, `evidence_presentation/`,
`falsification_atlas/`, `research_releases/`, `historical_research/`); `src/tools/` (7.5k LOC); `scripts/`
(34.6k LOC, 189 files); `tests/` (611 .py / 90.6k LOC, 66 .js); `data/trust/*.json`; `config/*.json`;
`docs/development/technical-review` (1254 files); the .qmd corpus (regex for cells, ZTCF language).

**Not touched:** `src/tools/wrist_universal_joint/*` Qt code, `src/golf_simulation/{course,round_simulator,
putting,clubs,terrain}.py` beyond the stimpmeter formula, `shared_scripts/`, `.gaai/`, `.jules/`, LaTeX sources,
notebooks, the 242 PDFs, `js/*.js` other than the three files named above.

LOC: src 36,036 (affine_control 10.5k top-level + 5.5k subpackages; tools 7.5k; golf_simulation 2.2k; core 0.3k +
0.5k optimizers; tangent_models 0.4k). scripts 34.6k. tests 90.6k. js 7.3k. 4,909 tracked files; 735 .txt, 371 .exit,
612 .md, 242 .pdf (31 MB), `.git` 51 MB.

## Gate Audit — Does Each Claimed Quality Gate Actually Gate?

| Claimed gate | Where enforced | Real? | Evidence |
|---|---|---|---|
| `ruff check` zero violations | ci-standard.yml:141 | Yes | `ruff check .` → "All checks passed" locally (ruff 0.16.8; CI pins 0.15.6) |
| `black --check -l 100` | ci-standard.yml:145 | Yes | 978 files unchanged locally |
| Module size budget "400 lines" (AGENTS.md:173,381) | ci-standard.yml:310 → config/module_size_budget.json:5 | **No** — limit is 750 for .py; largest file is 648; two `explicit_limits` point at files that do not exist | F-AD-016 |
| Test-count regression guard | ci-standard.yml:420,481 | **Theater** — baseline 2282, actual 8088 collected; cannot fire | F-AD-017 |
| Coverage floor `fail_under = 75` | pyproject.toml:95 via `--cov` | Yes (measured 92.6 % per comment) | — |
| "Critical module coverage" | scripts/check_critical_module_coverage.py:28-80 | Partial — lists site-health/links/sitemap/mock-optimizer; omits dynamics.py, golf_model.py, rnea.py | F-AD-018 |
| DRY adoption tracking | scripts/check_dry_adoption.py:37-41 | **Theater** — three substring checks in two scripts | F-AD-019 |
| Contract coverage | config/contract_coverage_rules.json | Theater — four `required_tokens` substring checks; reports `files_scanned=0` (check_contract_coverage.py:38) | F-AD-019 |
| Dependency boundaries | scripts/check_dependency_boundaries.py | Real (AST import scan) but reports `files_scanned=0` (line 86) | — |
| CSS budget | config/css_quality_budget.json:3 | Real; 3393/3400 lines → saturated | F-AD-020 |
| CSS mirror `css/` ↔ `_site/` (CLAUDE.md:93,109) | ci-standard.yml:152-156 | **Always skipped** in PR CI (no `_site/`); real only in deploy | F-AD-021 |
| Claim-audit evidence ledgers | ci-standard.yml:357 → scripts/regenerate_claim_audit_evidence.py | Real byte check; **not** a scientific check | F-AD-005 |
| Governance-vocabulary gate | ci-standard.yml:264 | `continue-on-error: true` — advisory | — |
| Readability | ci-standard.yml:402 | advisory | — |
| No `print()` in src | pre-commit `no-print-in-src` | Yes (0 hits outside src/tools) | — |
| TODO/FIXME tied to issues | config/tech_debt_budget.json | Count ceiling (47), not issue linkage | — |
| Jules overnight architecture (AGENTS.md:488-620) | `.github/workflows/` | **Fiction** — 10 named workflows absent; only two `Jules-Redundant-*` closers exist | F-AD-022 |
| E2E axe / Playwright per route | ci-standard.yml e2e job | Real when site-facing files change (path filter) | — |
| Programming-companion SHA-256 | validation.py:53-66 | Real, fail-closed, digest before parse | §5 |

## Findings, Ranked

| Sev | ID | Title | Category | Effort | One line |
|---|---|---|---|---|---|
| 🟥 Critical | [F-AD-001](findings/F-AD-001-four-flagship-figures-are-hand-drawn-curves-presented-as-com.md) | Four flagship figures are hand-drawn curves presented as computed results | docs | M | ZTCF/superposition article figures are invented logistic/sine/power-law curves captioned as model output with quantitative legends. |
| 🟧 High | [F-AD-002](findings/F-AD-002-corpus-and-the-only-executable-ztcf-contract-define-ztcf-as-.md) | Corpus and the only executable ZTCF contract define ZTCF as forward-integrated; manuscript says pointwise | docs | M | construction: Literal['forward'] is the only governed ZTCF; site abstract says ZTCF 'computes the forward-dynamics trajectory'. |
| 🟧 High | [F-AD-003](findings/F-AD-003-no-zvcf-implementation-exists-repo-only-format-checks-an-ups.md) | No ZVCF implementation exists; repo only format-checks an upstream manifest field | correctness | S | ZVCF appears in 59 content files and NOTATION.md but no src/js code computes -M^-1 h(q,0); validator checks 'is finite'. |
| 🟧 High | [F-AD-004](findings/F-AD-004-non-functional-mock-ddp-is-the-default-solver-of-swingoptimi.md) | Non-functional mock DDP is the default solver of SwingOptimizer while a real iLQR with the same signature is unused | architecture | M | ddp.py self-describes as 'non-functional mock'; ~100 tests cover it; optimizer_factory.ilqr_solver_wrapper is wired to nothing. |
| 🟧 High | [F-AD-005](findings/F-AD-005-claim-audit-evidence-gate-verifies-bytes-unchanged-since-las.md) | Claim-audit evidence gate verifies bytes unchanged since last regenerate, not claims | governance | M | 1016 evidence paths (87% prose/PDF/CSS/logs) digest-pinned; 11/12 claims not_reviewed; 27/35 critiques open incl. one critical with no open-date. |
| 🟨 Medium | [F-AD-006](findings/F-AD-006-two-thirds-of-the-pytest-suite-are-prose-presence-tests-on-t.md) | Two-thirds of the pytest suite are prose-presence tests on the content corpus | tests | M | 413/611 test files read .qmd/.tex; 2638 string-presence asserts dilute the coverage number the manuscript leans on. |
| 🟨 Medium | [F-AD-007](findings/F-AD-007-five-copies-of-the-same-fixed-step-rk4-loop.md) | Five copies of the same fixed-step RK4 loop | architecture | S | Identical k1..k4 bodies in five modules plus a duplicate forced_acceleration; the DRY gate cannot see it. |
| 🟨 Medium | [F-AD-008](findings/F-AD-008-9-7k-loc-of-fail-closed-protocol-declarations-that-validate-.md) | ~9.7k LOC of fail-closed protocol declarations that validate prose for unrun experiments | architecture | L | 87 __post_init__ validators and 162 'must be declared' checks on strings; belongs in JSON validated by the existing schemas. |
| 🟨 Medium | [F-AD-009](findings/F-AD-009-11-mb-of-terminal-transcripts-committed-including-371-exit-f.md) | 11 MB of terminal transcripts committed, including 371 .exit files containing '0' | hygiene | S | 1254 files under docs/development/technical-review plus 448 localhost Playwright JSON logs in reports/, referenced as ledger 'evidence'. |
| 🟨 Medium | [F-AD-010](findings/F-AD-010-service-worker-cache-first-for-non-precached-assets-svg-json.md) | Service worker cache-first for non-precached assets; SVG/JSON/PDF not in the cache-busting hash | correctness | S | Figures and data JSON are served stale-while-revalidate; returning readers see the previous deploy's figure. |
| 🟨 Medium | [F-AD-011](findings/F-AD-011-wheel-packaging-test-builds-into-repo-root-and-reuses-a-stal.md) | Wheel-packaging test builds into repo root and reuses a stale wheel forever | tests | S | _get_or_build_wheel globs dist/ and skips the build if any wheel exists; leaves dist/ build/ egg-info in the checkout. |
| 🟨 Medium | [F-AD-012](findings/F-AD-012-toolchain-versions-disagree-across-requirements-txt-ci-and-p.md) | Toolchain versions disagree across requirements.txt, CI and pre-commit | governance | S | ruff 0.17.0/0.15.6/0.15.7, black 26.10.0/26.3.1, mypy 2.4.0/1.19.1/1.13.0 across three sources. |
| 🟨 Medium | [F-AD-016](findings/F-AD-016-module-size-budget-is-750-lines-vs-documented-400-two-explic.md) | Module-size budget is 750 lines vs documented 400; two explicit limits name nonexistent files | governance | S | Gate has never fired on a .py; src/js/bibliography.js and src/core/contracts.py do not exist. |
| 🟨 Medium | [F-AD-018](findings/F-AD-018-critical-module-coverage-gate-omits-every-physics-kernel.md) | Critical-module coverage gate omits every physics kernel | governance | S | Protects link checker, sitemap and the mock optimizer; not dynamics.py, golf_model.py, rnea.py, lqr.py. |
| 🟨 Medium | [F-AD-022](findings/F-AD-022-agents-md-documents-a-ten-workflow-jules-control-tower-that-.md) | AGENTS.md documents a ten-workflow Jules Control Tower that does not exist and links six missing files | docs | S | Only two Jules-Redundant-* closers exist; scripts/pre_pr.py, .logging-standard.md etc. are absent. |
| 🟨 Medium | [F-AD-023](findings/F-AD-023-two-double-pendulum-models-with-different-mass-placement-sha.md) | Two double-pendulum models with different mass placement share a function name | correctness | S | Midpoint-mass (m1/4) vs end-mass ((m1+m2)L1^2) double_pendulum_mass_matrix; both correct, neither cross-referenced. |
| 🟨 Medium | [F-AD-024](findings/F-AD-024-clamped-free-shaft-modes-with-no-tip-mass-the-open-critical-.md) | Clamped-free shaft modes with no tip mass; the open critical critique targets the shipped model | correctness | M | _BETA_L are clamped-free eigenvalues and shaft_blocks has no m_tip term; critique is 'critical' and 'open' with no date. |
| ⬜ Low | [F-AD-013](findings/F-AD-013-source-revision-model-authority-is-a-constant-compared-to-it.md) | source_revision model authority is a constant compared to itself | governance | S | SUPPORTED_MODEL_REVISION is never compared to golf_model.py bytes or HEAD; the real pin is the parity fixture's dependency_sha256. |
| ⬜ Low | [F-AD-014](findings/F-AD-014-exact-float-equality-on-replayed-trajectories-in-branch-inte.md) | Exact float equality on replayed trajectories in branch_intervention | numerics | S | pydantic != on float fields while the contract test uses abs=1e-10; brittle across BLAS/platforms. |
| ⬜ Low | [F-AD-015](findings/F-AD-015-gravity-constant-defined-six-times-bypassing-src-core-consta.md) | Gravity constant defined six times, bypassing src.core.constants | hygiene | S | Six 9.81 literals including one baked into a protocol string compared by equality. |
| ⬜ Low | [F-AD-017](findings/F-AD-017-test-count-ratchet-2282-is-3-5x-below-the-8088-collected-and.md) | Test-count ratchet (2282) is 3.5x below the 8088 collected and can never fire | governance | S | A PR could delete 5800 tests and pass the regression guard. |
| ⬜ Low | [F-AD-019](findings/F-AD-019-dry-and-contract-coverage-gates-are-substring-greps-over-2-4.md) | DRY and contract-coverage gates are substring greps over 2-4 files | governance | S | 'DRY adoption tracking' is three token checks; two gates hard-code files_scanned=0. |
| ⬜ Low | [F-AD-020](findings/F-AD-020-css-budget-saturated-at-3393-3400-lines.md) | CSS budget saturated at 3393/3400 lines | governance | S | Next CSS change forces a budget bump; !important budget is 4.5x actual. |
| ⬜ Low | [F-AD-021](findings/F-AD-021-claude-md-promises-a-css-mirror-gate-that-pr-ci-always-skips.md) | CLAUDE.md promises a CSS mirror gate that PR CI always skips | docs | S | _site/ is git-ignored so the mirror step echoes 'Skipping' on every PR. |
| ⬜ Low | [F-AD-025](findings/F-AD-025-e2e-self-hosted-assertion-attaches-its-request-listener-afte.md) | E2E self-hosted assertion attaches its request listener after page load | tests | S | Initial-load cross-origin requests are invisible to the test. |
| ⬜ Low | [F-AD-026](findings/F-AD-026-review-commit-verification-commit-source-revision-are-unveri.md) | review_commit/verification_commit/source_revision are unverifiable 40-hex strings | governance | S | Regex-validated only; never resolved against git or file digests. |
| ⬜ Low | [F-AD-027](findings/F-AD-027-collection-time-hard-imports-of-optional-notebook-tooling.md) | Collection-time hard imports of optional notebook tooling | hygiene | S | Missing nbclient/nbformat aborts collection so the count guard would see 0. |
| ⬜ Low | [F-AD-028](findings/F-AD-028-hard-coded-windows-user-path-in-a-committed-script.md) | Hard-coded Windows user path in a committed script | hygiene | S | C:\Users\diete\Repositories\AffineDrift literal; script unused. |
| ⬜ Low | [F-AD-029](findings/F-AD-029-dead-physics-constants-with-undocumented-provenance.md) | Dead physics constants with undocumented provenance | hygiene | S | HOLE_CAPTURE_SPEED_MS and STIMPMETER_CALIBRATION_FACTOR=1.285 are unused and uncited. |
| ⬜ Low | [F-AD-030](findings/F-AD-030-solve-ivp-reference-trajectory-uses-default-rtol-1e-3.md) | solve_ivp reference trajectory uses default rtol=1e-3 | numerics | S | Chaotic double pendulum 'reference' at 1e-3 relative; series_elastic_demo shows the right settings. |
| ⬜ Low | [F-AD-031](findings/F-AD-031-242-pdfs-31-mb-committed-lfs-rule-only-matches-root-level-pd.md) | 242 PDFs (31 MB) committed; LFS rule only matches root-level PDFs | hygiene | S | '/*.pdf filter=lfs' never matches; ledgers pin main.pdf digests so every recompile forces a regenerate. |
| ⬜ Low | [F-AD-032](findings/F-AD-032-test-critical-physics-fixes-py-has-three-layers-of-ruff-exem.md) | test_critical_physics_fixes.py has three layers of ruff exemption including F821 | hygiene | S | Excluded, per-file-ignored and '# ruff: noqa' for one 415-line test file. |
| ⬜ Low | [F-AD-033](findings/F-AD-033-ztcf-explorer-s-declared-torque-horizon-are-module-constants.md) | ZTCF explorer's declared torque/horizon are module constants, not part of the intervention record | governance | S | The branch record cannot describe the actual-branch torque it is compared against. |
| ⬜ Low | [F-AD-034](findings/F-AD-034-claude-md-claims-interactive-executable-code-cells-the-corpu.md) | CLAUDE.md claims interactive/executable code cells; the corpus has zero executable cells | docs | S | 0 {python}/{ojs} fences in 396 .qmd; the inline-Python rule is vacuous. |
| ⬜ Low | [F-AD-035](findings/F-AD-035-lqr-convergence-uses-an-absolute-1e-14-tolerance-on-s.md) | LQR convergence uses an absolute 1e-14 tolerance on S | numerics | S | Large-norm S will chatter above 1e-14 and be reported as non-convergent. |

## Patterns and Approaches Worth Adopting

- **Generate figures from the model, always.** One `scripts/figures/<name>.py` per figure that *imports* the kernel
  and writes both the SVG and a `.json` of the plotted arrays; a test re-derives the arrays. This single discipline
  would have prevented F-AD-001 and makes every figure a reproducibility artifact.
- **Hash the assertion, not the file.** Evidence = a pytest node-id + the commit it passed at + the claim text
  it was asserted against. `pytest --junitxml` already gives you pass/fail per node-id; the ledger should
  consume that, not SHA-256 of a .bib.
- **Mutation testing on the kernel** (`mutmut run --paths-to-mutate src/affine_control/dynamics.py,golf_model.py,
  rnea.py`). The kernel is small enough to run nightly; it answers "would these tests notice a sign flip in
  Christoffel" directly, which 8,088 tests and 92 % coverage do not.
- **Property-based tests on the physics, not the mock.** Hypothesis is installed and used on `estimate_perturbation_size`
  (a function of a mock); point it at `GolfModel`: random (q, q̇, τ) → `M(f+Gτ)+Cq̇+g == τ`, `Ṃ−2C` skew,
  energy rate = τ·q̇, RNEA == Lagrangian.
- **Unit-typed quantities** for the interface layer (`pint` or a tiny `Quantity` dataclass): the repo already
  suffixes names (`_m_s`, `_rad`, `_kg_m2`) which is the manual version; the `rad/s` vs `rpm`, `deg` vs `rad`
  mistakes in a biomechanics paper are the ones reviewers love.
- **Declarative protocols in data, code only for computation.** 9.7k LOC of dataclasses whose job is to hold
  strings is JSON with a schema (which you already wrote). Code should be the part that can be *wrong*.
- **Golden-master discipline**: the widget parity fixtures are the best thing in the repo — generated, digest-pinned,
  tolerance-declared, consumed by both Python and JS. Apply the same pattern to worked-example numbers in the
  LaTeX (you half do: `generate_worked_examples.py --check`), to the forward fixture, and to every figure.
- **One integrator, one gravity, one pendulum.** DRY is a correctness tool here, not style: the parity between
  Python and JS depends on there being exactly one definition to mirror.
- **Treat AGENTS.md as code**: a test that every path it names exists, every command it gives runs `--help`.
  Dead instructions train agents to skip instructions.
- **Separate the two test suites** (kernel vs corpus-lint) in reporting. The manuscript's credibility rests on
  the ~800 kernel tests; let that number be visible.
- **Stop committing build outputs** (PDFs, render logs, `.exit` files, `reports/*.json`). Publish them as release
  assets or CI artifacts; cite them by URL + digest in the ledger if you must.
- **Decide the ZTCF vocabulary once and encode it**: a `Construction` enum with exactly the members the manuscript
  uses, and a terminology gate that checks the *construction qualifier*, not the acronym expansion.

## What Is Good — Keep It

- `dynamics.py` is a model of how to write a reference kernel: the docstring records the four published sign errors
  it exists to prevent, conventions (angular-first spatial vectors) are stated and tested, the Christoffel
  construction is generic and numerically verified against the closed form. `constrained_affine_fields` correctly
  keeps the multiplier out of the drift — a point most textbooks get wrong — and I verified `Jc(f+Gu)+Jċq̇ = 0`.
- `GolfModel` assembles the mass matrix from COM Jacobians (PD by construction), the shaft blocks use the correct
  transverse moment arms, and `tests/test_applications_model_rigor.py:111-130` checks the printed closed-form
  inertia against the assembly. Energy conservation tests exist with sensible tolerances (1e-6 rel, 1e-7 abs rate)
  and a step-refinement check (`:232-248`).
- `rnea.py` and the Lagrangian route are genuinely independent and agree to 1e-9; the chapter's "numbers might be"
  problem was fixed the right way.
- `lqr.py`: the stabilising solution, closed-loop spectral radius and Riccati residual are all *returned* so the
  text is generated from them; the divergence guard is thoughtful.
- `impact_contact_models.py`: Newton/Coulomb reset with correct sticking impulse, Hunt–Crossley with the
  damping factor clamped at zero, step-halving convergence error reported, and an explicit refusal to pick a
  "preferred model".
- `programming_companion/`: a real supply-chain consumer — exact-commit URL allow-list, redirects forbidden,
  Content-Length and streamed byte caps, digest compared *before* parse, duplicate-key JSON rejected, schema `$id`
  pinned, atomic install with `os.replace` + `fsync`, explicit-replace guarded by the active lock's digest.
  (Not constant-time, which is fine: the digest is of public bytes.)
- Widget parity fixtures (`tests/fixtures/widgets/*.parity.json`) with declared abs/rel tolerance and
  `dependency_sha256` of the Python sources — verified to match HEAD.
- `tests/test_worked_example_callouts.py` parses the article's **Given**/**Result** and recomputes — that is the
  correct shape for claim evidence; make it the only shape.
- Ruff and Black pass as cloned; no `print` in `src/`; no `shell=True`, `eval`, `pickle`, bare `except`; only one
  hard-coded path in the whole tree.
- `ci-standard.yml` step comments explain *why* each content gate exists with the defect that motivated it —
  rare and valuable.

## Positive-Deletion Candidates

| Path | Why | Est. LOC / size |
|---|---|---|
| `docs/development/technical-review/**/*.exit`, `**/*.txt`; `reports/technical-review/*.json` | session transcripts and localhost Playwright logs committed as "evidence" | 1,254 files, 11 MB + 448 JSON, ~17 MB |
| `src/affine_control/ddp.py`, `swing_optimizer.py` mock paths, `swing_types.py` mock flags; ~100 mock tests | non-functional mock with a real replacement available | ~900 LOC src, ~1,500 LOC tests |
| `src/affine_control/*_protocol.py`, `*_fixtures.py`, `*_evidence.py`, `research_readiness/`, `evidence_presentation/`, `falsification_atlas/`, `research_releases/`, `historical_research/` → JSON + schema | prose-in-dataclasses | ~7,000–8,000 LOC |
| `data/trust/site_trust_surface_audit.json` entries for `/`, about, book-reviews; `claim_audit_inventory.json` (1.8 MB generated) | audits of non-scientific pages; generated artifact tracked | ~2 MB |
| `scripts/check_dry_adoption.py`, `check_contract_coverage.py`, `config/contract_coverage_rules.json` | substring theater | ~200 LOC |
| AGENTS.md §"System Architecture & Agent Roles" + dangling references | describes absent workflows | ~140 lines |
| `scripts/find_magic_numbers.py` | Windows user path; unused | 60 LOC |
| `src/core/constants.py:114-118` two dead constants | unused | 6 LOC |
| `articles/**/main.pdf`, `articles/**/figures/*.pdf` → LFS or release assets | build outputs in git | 31 MB |
| `tests/test_critical_physics_fixes.py` ruff exemptions (3 layers) | unneeded | 3 config lines |
| 4 duplicated RK4 loops after extracting `core/integrators.py` | DRY | ~60 LOC |

## Fleet-Wide Synthesis

Cross-repository observations (shared verbatim across the four reviewed repos) are in
[`fleet-synthesis.md`](fleet-synthesis.md).

## How This Review Was Produced

- Mechanical pass over every tracked `.py` file: `ruff` (repo config and an isolated adversarial rule set), `bandit`,
  `radon`, `vulture`, AST structure metrics, and pattern greps. Summaries in [`baseline.md`](baseline.md).
- Deep pass: a reviewer read the modules named in the coverage statement line by line, ran the repo's own gates, and
  executed at least one numerical check where the module imported cleanly.
- Pitches were drafted per finding afterwards from the finding text; they do not add claims beyond it.

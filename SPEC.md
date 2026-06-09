# SPEC.md — Repository Specification Document

Last-Updated: 2026-06-03T00:00:00Z

<!--
  TEMPLATE VERSION: 1.0.0
  LAST UPDATED: 2026-03-30

  This is the canonical specification template for all repositories in the
  D-sorganization fleet. Every repo MUST have a SPEC.md at its root.

  INSTRUCTIONS:
  1. Copy this template to the root of your repository as SPEC.md
  2. Fill in every section — leave nothing as "[TODO]"
  3. Keep this document updated with every PR that changes functionality
  4. CI will block merges if SPEC.md is stale (source changed but spec didn't)

  AUDIENCE: This document is designed for both human developers AND AI agents.
  Write clearly, use concrete examples, and avoid ambiguity.
-->

## 1. Identity

| Field                   | Value                                            |
| ----------------------- | ------------------------------------------------ |
| **Repository Name**     | `AffineDrift`                                    |
| **GitHub URL**          | `https://github.com/D-sorganization/AffineDrift` |
| **Owner**               | D-sorganization                                  |
| **Primary Language(s)** | Python 3.12, JavaScript ES6+, Quarto             |
| **License**             | MIT                                              |
| **Current Version**     | 1.0.8                                            |
| **Spec Version**        | 1.0.118                                          |
| **Last Spec Update**    | 2026-05-31                                       |

## 2. Purpose & Mission

AffineDrift is a research platform that explores golf swing biomechanics through the lens of affine control theory. The project combines rigorous mathematical modeling with interactive educational content, publishing research-quality materials via a Quarto-based website hosted on GitHub Pages. It demonstrates how differential dynamic programming and iterative linear-quadratic regulation (iLQR) can optimize swing trajectories, while serving as an educational bridge between control theory and biomechanics for the broader scientific community.

## 3. Goals & Non-Goals

### Goals

- Model golf swings as affine controllable systems with mathematical rigor, enabling optimization through advanced control algorithms
- Publish and maintain research-quality educational content via Quarto website (AffineDrift.com) on GitHub Pages
- Implement swing trajectory optimization using differential dynamic programming (DDP) and iLQR solvers
- Model golf-ball flight with velocity-dependent drag and spin-dependent Magnus lift using the standard projected-area aerodynamic formulation
- Achieve and maintain >50% test coverage with property-based testing (Hypothesis) across all critical modules
- Maintain opt-in performance benchmarks for stable computational paths without slowing routine CI
- Provide comprehensive educational resources that bridge control theory and applied biomechanics
- Maintain textbook bibliographies and chapter citations with explicit scientific sourcing for biomechanics, multibody dynamics, geometry, and control-theory claims
- Present the textbook volumes with shared algorithm and pseudocode conventions so implementation guidance is consistent across the series

### Non-Goals

- Not a production game engine (QuatEngine serves that purpose)
- Not a real-time physics simulator (UpstreamDrift provides real-time simulation)
- Not a general-purpose mathematics library

## 4. Architecture Overview

### System Context

AffineDrift operates as a standalone research and education platform within the D-sorganization fleet. It complements but does not depend on QuatEngine (game engine) or UpstreamDrift (real-time physics simulator). The platform produces research content and optimization algorithms that can be consumed by educational institutions, biomechanics researchers, and control theory practitioners. It integrates with GitHub Pages for deployment and GitHub Actions for continuous integration, deployment, and automated quality assurance.

### Module Map

```
AffineDrift/
├── PARAMETERS.md       # Canonical parameters reference table
├── src/
│   ├── affine_control/          # Swing optimization and control algorithms
│   │   ├── swing_optimizer.py   # DDP and iLQR solvers for swing trajectories
│   │   ├── ddp_solver.py        # Differential dynamic programming implementation
│   │   ├── residuals.py         # Optimization residual calculations
│   │   └── swing_types.py       # Swing model definitions and types
│   ├── core/                    # Foundational abstractions and utilities
│   │   ├── constants.py         # Physical and mathematical constants
│   │   ├── contracts.py         # Design-by-contract specifications
│   │   ├── optimizers.py        # iLQR optimizer implementations
│   │   └── protocols.py         # Type protocols and interfaces
│   └── tangent_models/          # Tangent space and hyperplane methods
│       ├── tangent_space.py     # Tangent space mathematics
│       └── examples.py          # Example implementations and tutorials
├── src/tools/                   # CI/CD utilities and build tools
│   ├── link_checker.py          # Validate links in documentation
│   ├── site_health.py           # Monitor website health metrics
│   └── code_quality_ast.py      # AST-based code quality analysis
├── tests/                       # Test suite (80+ test files)
│   ├── test_affine_control/     # Physics and optimization tests
│   ├── test_core/               # Core module tests
│   ├── test_tangent_models/     # Tangent space method tests
│   ├── test_tools/              # Tool and CI/CD tests
│   ├── test_content/            # Content structure and validation
│   └── test_integration/        # Cross-module integration tests
├── benchmarks/                  # Opt-in pytest-benchmark performance suite
├── js/                          # JavaScript interactive features
│   ├── rotation-converter/      # 3D rotation visualization
│   ├── search.js                # Site search functionality
│   └── interactive-viz.js       # Mathematical visualizations
├── css/                         # Canonical stylesheets (CSS budget enforced)
│   ├── main.css                 # Primary stylesheet
│   ├── typography.css           # Typography and layout
│   └── responsive.css           # Responsive design rules
├── content/                     # Quarto markdown source files (.qmd)
│   ├── index.qmd                # Homepage
│   ├── getting-started.qmd      # Getting started guide
│   └── [other pages]            # Additional educational content
├── articles/                    # Research articles (.qmd format)
│   ├── swing-modeling.qmd       # Core swing modeling article
│   ├── optimization-theory.qmd  # Optimization theory and methods
│   └── [other articles]         # Additional research content
├── books/                       # Quarto book projects
│   └── control-theory-guide.qmd # Comprehensive control theory textbook
├── .github/workflows/           # 6 executable GitHub Actions workflows plus templates/docs
│   ├── ci-standard.yml          # Main CI pipeline
│   ├── deploy-website.yml       # Quarto site build and deployment
│   ├── ci-benchmarks.yml        # Opt-in performance benchmark gate
│   ├── link-checker.yml         # Link validation
│   ├── spec-check.yml           # SPEC freshness enforcement
│   └── block-self-merge.yml     # Distributed review guard
├── scripts/                     # Content and repository maintenance utilities
│   ├── check_bibliography_quality.py # Bibliography structure and metadata validation
│   ├── check_qmd_citation_keys.py    # Quarto citation-key integrity scan for site content
│   ├── check_quarto_render_coverage.py # Sitemap-to-source coverage guard for Quarto pages
│   ├── cli_output.py                 # Explicit stdout/stderr helpers for intentional CLI contracts
│   └── README.md                # Script usage and CI-facing documentation
├── tests/                       # Additional test organization
│   └── e2e/                     # End-to-end Playwright tests
├── _quarto.yml                  # Quarto configuration
├── Dockerfile                   # Verified multi-stage container build for preview/runtime
├── pyproject.toml               # Python project metadata and dependencies
├── requirements-docker.lock     # Hash-locked Python dependency set for container builds
├── package.json                 # JavaScript dependencies
├── SPEC.md                      # This specification document
└── README.md                    # Project overview and quick start
```

### Key Components

| Component             | Location                                 | Purpose                                                     |
| --------------------- | ---------------------------------------- | ----------------------------------------------------------- |
| Swing Optimizer       | `src/affine_control/swing_optimizer.py`  | DDP and iLQR-based trajectory optimization for golf swings  |
| DDP Solver            | `src/affine_control/ddp_solver.py`       | Core differential dynamic programming algorithm             |
| Core Constants        | `src/core/constants.py`                  | Physical and mathematical constants used throughout         |
| iLQR Optimizer        | `src/core/optimizers.py`                 | Iterative linear-quadratic regulation solver                |
| Tangent Space Models  | `src/tangent_models/`                    | Tangent space and hyperplane mathematical abstractions      |
| Link Checker          | `src/tools/link_checker.py`              | CI/CD tool for validating documentation links               |
| Site Health Monitor   | `src/tools/site_health.py`               | Automated website health and performance checks             |
| Code Quality Analyzer | `src/tools/code_quality_ast.py`          | AST-based Python code quality analysis                      |
| Rotation Converter    | `js/rotation-converter/`                 | Interactive 3D rotation visualization and converter         |
| Search Functionality  | `js/search.js`                           | Full-text search across website content                     |
| Quarto Configuration  | `_quarto.yml`                            | Website build and rendering configuration                   |
| Container Build       | `Dockerfile`, `requirements-docker.lock` | Verified preview/runtime image build with provenance output |
| Test Suite            | `tests/`                                 | 80+ pytest and Jest test files                              |
| Benchmark Suite       | `benchmarks/`                            | Opt-in pytest-benchmark timing checks for stable paths      |

## 5. Desired Functionality

### Core Features

| #   | Feature                                  | Status | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| --- | ---------------------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| F1  | Quarto Website Rendering and Deployment  | ✅     | Renders Quarto markdown (.qmd) source files into static HTML and deploys to GitHub Pages                                                                                                                                                                                                                                                                                                                                                                       |
| F2  | Affine Control Theory Swing Optimizer    | ✅     | Implements DDP and iLQR algorithms to optimize golf swing trajectories as affine controllable systems                                                                                                                                                                                                                                                                                                                                                          |
| F3  | Tangent Space and Hyperplane Models      | ✅     | Provides mathematical models for tangent space methods with educational examples                                                                                                                                                                                                                                                                                                                                                                               |
| F4  | Interactive JavaScript Visualizations    | ✅     | Rotation converter, search interface, and mathematical visualization components                                                                                                                                                                                                                                                                                                                                                                                |
| F5  | Mathematical Notation Rendering          | ✅     | Supports MathJax and KaTeX for rendering LaTeX equations in web content, with `ui/lazy` enabled for performance and LaTeX cleanup that preserves escaped percent signs while removing real comments                                                                                                                                                                                                                                                            |
| F6  | Property-Based Testing with Hypothesis   | ✅     | Comprehensive property-based testing strategy using Hypothesis framework                                                                                                                                                                                                                                                                                                                                                                                       |
| F7  | CSS Budget Enforcement                   | ✅     | Automated CI enforcement of CSS file size limits to maintain performance                                                                                                                                                                                                                                                                                                                                                                                       |
| F8  | Mirror Validation                        | ✅     | Ensures duplicate stylesheets match canonical versions across the codebase                                                                                                                                                                                                                                                                                                                                                                                     |
| F9  | GitHub Actions Automation                | ✅     | The executable GitHub Actions workflow set is limited to the repository's production CI, deployment, benchmark, link-check, spec-check, and self-review guard workflows; third-party actions are pinned to immutable SHAs and checked by CI.                                                                                                                                                                                                                   |
| F10 | Progressive Web App Support              | ✅     | Service worker and manifest for PWA capabilities with bounded offline caching and update notices (offline access, installability)                                                                                                                                                                                                                                                                                                                              |
| F11 | Textbook Compilation Pipeline            | ✅     | Quarto pipeline to compile educational materials into publishable textbook format                                                                                                                                                                                                                                                                                                                                                                              |
| F12 | Textbook claim guardrail                 | ✅     | PR CI blocks newly added unsupported quantitative or study claims in textbook content unless they include a citation or an explicit illustrative caveat                                                                                                                                                                                                                                                                                                        |
| F13 | PR site-build and dependency-audit gate  | ✅     | `ci-standard.yml` installs dependencies from lockfiles, audits Python dependencies with blocking `pip-audit`, measures coverage across the full `src/` tree, renders the Quarto pages exercised by PR smoke tests, validates sitemap URLs against committed Quarto source pages, syncs frontend assets, and runs Playwright smoke tests against the generated docs, including workflow-file changes in CI triggers                                             |
| F14 | Bibliography duplicate-alias guardrail   | ✅     | Reference-integrity tests require duplicate bibliography records to carry an explicit legacy-compatibility note instead of silently diverging                                                                                                                                                                                                                                                                                                                  |
| F15 | Textbook bibliography synchronization    | ✅     | The Geometry of Motion and The Physics of Golf keep chapter-level citations synchronized with shared bibliography sources in `references/affine-drift.bib` and the book-specific `.bib` files                                                                                                                                                                                                                                                                  |
| F16 | Website citation-resolution guardrail    | ✅     | PR CI scans website `.qmd` sources, resolves their configured bibliography files, and fails when citation keys do not map to a known bibliography entry                                                                                                                                                                                                                                                                                                        |
| F17 | Textbook algorithm convention sharing    | ✅     | `geometry_of_motion.sty` exposes shared algorithm and pseudocode primitives so implementation-oriented chapters use one consistent notation and formatting style                                                                                                                                                                                                                                                                                               |
| F18 | Textbook applied-optimization guidance   | ✅     | Volume I uses the canonical 12-file include list in `volume0.qmd`, and Volume II renders from monolithic `volume2_content.qmd`; both volumes include implementation-grade pseudocode for DDP/iLQR, direct collocation, funnel synthesis, ILC, and trajectory-library adaptation, plus a bounded treatment of evolutionary search                                                                                                                               |
| F19 | Script CLI output contracts              | ✅     | Maintenance scripts route intentional terminal output through `scripts/cli_output.py`, making stdout/stderr behavior explicit and easier to test without weakening logging semantics                                                                                                                                                                                                                                                                           |
| F20 | RL benchmark modular split               | ✅     | `src/tools/rl_funnel_benchmark.py` now stays under the repo file-size budget by delegating dynamics, controllers, and simulation concerns to focused helper modules while preserving the benchmark module's public API, including caller-provided reference trajectory timesteps                                                                                                                                                                               |
| F21 | Tooling Demeter facades                  | ✅     | Link and site-health utilities isolate DOM/path traversal behind small façade objects so repository-governance checks depend on narrower interfaces instead of nested reach-through                                                                                                                                                                                                                                                                            |
| F45 | Verified container build inputs          | ✅     | The Docker preview/runtime path pins the Python base image by digest, verifies the Quarto release checksum, installs Python dependencies from `requirements-docker.lock` in hash-checking mode, and emits `docs/build-provenance.json` with the commit, Quarto artifact hash, lock hash, and rendered-site checksum.                                                                                                                                           |
| F22 | Wrist-model Qt module split              | ✅     | The legacy `content/wrist-as-universal-joint/Universal_Joint_Model_Enhanced.py` launcher now delegates geometry, kinematics, Qt canvas rendering, and window assembly to focused modules under `src/tools/wrist_universal_joint`, keeping the entrypoint thin while preserving its public surface; the launcher re-export test gracefully skips when the Qt runtime is unavailable (headless CI)                                                               |
| F23 | Analysis helper fallback logging         | ✅     | `src/tools/utils/analysis_utils.py` logs recoverable parse and file-read failures at debug level when it falls back to zeroed or empty analysis results, keeping repository-quality scans observable without turning invalid files into hard failures                                                                                                                                                                                                          |
| F24 | Developer test target coverage           | ✅     | `make test` runs Python `src/` coverage and JavaScript coverage so local developer checks exercise both primary test stacks before code reaches CI                                                                                                                                                                                                                                                                                                             |
| F25 | Core algorithm regression coverage       | ✅     | Executable pytest coverage exercises the actual iLQR optimizer and RL funnel controller modules, including optimization progress, input validation, setpoint control, trajectory tracking control, and weight-matrix shape validation                                                                                                                                                                                                                          |
| F25 | Workflow event-payload hardening         | ✅     | Comment, issue, and PR-body GitHub event payloads are passed through workflow `env:` values and shell-safe handling instead of being interpolated directly into `run:` scripts                                                                                                                                                                                                                                                                                 |
| F26 | Wrist universal-joint ratio consistency  | ✅     | The wrist universal-joint tools use the Cardan/Hooke transmission denominator without a square root, standardize ratio call sites with keyword arguments, and keep Streamlit cache decorators typed for mypy                                                                                                                                                                                                                                                   |
| F27 | Batch converter package imports          | ✅     | Batch LaTeX conversion entrypoints import converter classes through package-qualified `src.tools.*` paths so they work under pytest and module execution                                                                                                                                                                                                                                                                                                       |
| F28 | Physics of Golf numeric consistency      | ✅     | Critical textbook checks pin the chapter 3 double-pendulum numerical example to the documented `M2 = 1.5 kg` parameter set so rendered values do not drift from the stated model                                                                                                                                                                                                                                                                               |
| F29 | Wrist-model figure lifecycle             | ✅     | Wrist-model Streamlit visualizations create Matplotlib figures through the object-oriented `Figure` API and avoid resource-caching array-backed plot functions                                                                                                                                                                                                                                                                                                 |
| F30 | Assessment category mappings             | ✅     | Repository assessment helpers keep `ASSESSMENT_DEFINITIONS` names synchronized with canonical A-N category labels so generated reports and category lookups use consistent terminology.                                                                                                                                                                                                                                                                        |
| F31 | Dependency pinning and tool isolation    | ✅     | Root Python requirements use exact pins for reproducible CI installs, including the April 2026 refresh to `hypothesis==6.152.1`, `ruff==0.15.11`, and `pydantic==2.13.2`, while the Streamlit wrist tool keeps its optional UI-specific requirements in its local requirements file.                                                                                                                                                                           |
| F32 | Stimpmeter-calibrated putting physics    | ✅     | Putting roll simulation and round-level putt speed estimation share the USGA Stimpmeter launch-speed deceleration formula, with regression coverage for Stimp 10 stopping distance.                                                                                                                                                                                                                                                                            |
| F33 | Round putting simulator injection        | ✅     | `RoundSimulator` accepts an optional prebuilt `PuttingSimulator` so tests and callers can provide calibrated green physics without relying on inline flat-green construction.                                                                                                                                                                                                                                                                                  |
| F34 | Mypy autofix package entrypoints         | ✅     | The mypy autofix agent is split into focused modules under `scripts/mypy_autofix` while preserving the legacy `scripts/mypy_autofix_agent.py` workflow entrypoint as a compatibility wrapper.                                                                                                                                                                                                                                                                  |
| F35 | Face-angle sensitivity consistency       | ✅     | Physics of Golf chapter 31 keeps driver face-angle offline-distance sensitivity in the documented 13--20 yards-per-degree range and regression tests block the previous 60--70 yards-per-degree contradiction.                                                                                                                                                                                                                                                 |
| F36 | Dynamic beam model consistency           | ✅     | Physics of Golf chapter 11 uses the dynamic Euler-Bernoulli equation with explicit inertial term and a content test guards the modal consistency of the governing equation in the chapter source.                                                                                                                                                                                                                                                              |
| F37 | Double-pendulum parameter context        | ✅     | Physics of Golf chapters 3, 6, and 8 explicitly document when their double- or triple-pendulum parameters are canonical chapter baselines versus compact worked-example sets, with content tests guarding the modeling-context notes.                                                                                                                                                                                                                          |
| F38 | Robust quaternion extraction             | ✅     | The rotation-representations reference article uses a numerically stable matrix-to-quaternion extraction path for trace-positive and dominant-axis cases, with executable regression coverage for 180-degree rotations about coordinate axes and arbitrary unit axes.                                                                                                                                                                                          |
| F39 | Workflow documentation hygiene           | ✅     | `.github/workflows/` contains the active workflow YAML files plus workflow-local README/template assets; repository-level workflow inventory remains documented through `docs/development/repository_inventory.md` and `SPEC.md`.                                                                                                                                                                                                                              |
| F40 | Opt-in benchmark suite                   | ✅     | `benchmarks/` provides pytest-benchmark-compatible baseline timing checks for double-pendulum dynamics and trajectory-cost helpers; normal `pytest` remains scoped to `tests/` so routine validation does not run benchmark timing.                                                                                                                                                                                                                            |
| F41 | Distributed code review enforcement      | ✅     | .github/workflows/block-self-merge.yml prevents PR authors from approving their own pull requests; enforced at the review stage with branch protection rules as the authoritative gate                                                                                                                                                                                                                                                                         |
| F42 | Cyclomatic complexity (McCabe) gate      | ✅     | Enforces `max-complexity = 10` in Ruff CI to maintain code quality                                                                                                                                                                                                                                                                                                                                                                                             |
| F43 | Isolated benchmark CI environment        | ✅     | The performance benchmark workflow installs dependencies into a workflow-local virtual environment and guards PR comment/artifact steps when benchmark output is unavailable, keeping benchmark failures attributable to the benchmark command instead of shared runner state                                                                                                                                                                                  |
| F44 | Production-readiness CI hardening        | ✅     | `ci-standard.yml` now treats mypy over `src/tools/` plus the production-readiness policy scripts, generated-agent-artifact checks, and GitHub Actions pinning checks as blocking quality gates, while the website-lint job fails on HTML validation errors instead of downgrading them to warnings.                                                                                                                                                            |
| F45 | Optimizer and browser-state hardening    | ✅     | The core iLQR solver records `last_diagnostics` for convergence, iteration count, final cost, failure reason, and rollout/callback errors while preserving the existing return contract; dynamics outputs are validated for shape and finite values during rollout, linearization, and line search. Browser persistence helpers for history, metrics, and notes now delete corrupted `localStorage` payloads and bound notes recycle-bin retention to 30 days. |
| F46 | Python 3.10 contract compatibility       | ✅     | `src/contracts.py` uses explicit `TypeVar`/`ParamSpec` declarations instead of Python 3.12+ PEP 695 type parameter syntax, restoring import compatibility for environments running Python 3.10 or 3.11. Ruff UP047 is suppressed with `# noqa: UP047` on the affected generic function definitions.                                                                                                                                                            |
| F47 | Website design primitives                | ✅     | The homepage and content architecture use canonical CSS primitives for site cards, buttons, section stacks, and sticky page sidebars so reusable layout semantics live in `css/components/` and `css/layout/` instead of one-off inline styles.                                                                                                                                                                                                                |
| F48 | QMD style-discipline linting             | ✅     | `src/tools/check_style_discipline.py` scans rendered-source `.qmd` files outside excluded generated/content directories and fails on inline `style=` attributes, gradient functions, or hardcoded hex colors, with unit tests covering clean files and each violation category.                                                                                                                                                                                |
| F49 | Consolidated frontend dependency refresh | ✅     | The site frontend keeps Dependabot JavaScript and Python dependency refreshes together with navigation traversal and UI component optimizations, then regenerates committed `docs/` mirrors from the canonical frontend assets so production pages match source behavior.                                                                                                                                                                                      |

### API / Interface Contract

**Python API:**

- `affine_control.swing_optimizer.SwingOptimizer` — Main optimization interface
  - Constructor requires a real `ddp_solver` unless `SwingOptimizationConfig.allow_mock_solver=True` is paired with a pytest session or the explicit demo flag `AFFINEDRIFT_ENABLE_MOCK_DDP=1`
  - `optimize(...)` may execute the mock solver only after both the config opt-in and the test/demo environment gate are satisfied
  - `optimize(swing_model, constraints) -> OptimizedTrajectory` — Run trajectory optimization
- `core.optimizers.iLQR` — iLQR solver
  - `solve(dynamics, cost_fn, initial_trajectory) -> Solution` — Compute optimal trajectory
  - `last_diagnostics` exposes the most recent solve status without changing the tuple-style solution return value; callers can inspect convergence, failure reason, final cost, and iteration count after a solve attempt
  - Dynamics callbacks must return finite state vectors matching the current state shape; invalid outputs fail fast instead of being silently propagated through rollout or line search
- `golf_simulation.ball_flight.BallFlightDynamics` — Golf-ball flight integrator
  - Uses Reynolds-dependent drag and spin-parameter lift to compute aerodynamic forces during free flight
- `tangent_models.TangentSpaceModel` — Tangent space abstraction
  - `project(vector) -> Vector` — Project to tangent space

**JavaScript API:**

- `RotationConverter` — Interactive 3D rotation tool
  - `convert(matrix, target_format) -> string` — Convert rotation representations
- `SearchIndex.query(term) -> SearchResults` — Full-text search across content
- Browser persistence utilities must fail closed on corrupted `localStorage` JSON by removing invalid keys and returning empty/default state; notes recycle-bin entries are retained for 30 days before cleanup

**CLI Tools:**

- `link-checker.py` — Validate all documentation links
- `site-health.py` — Generate health report on website assets
- `code-quality-ast.py` — Analyze Python code structure and metrics
- `check_style_discipline.py` — Enforce QMD style-discipline rules that keep page styling in canonical CSS primitives
- `scripts/cli_output.py` — Shared helper for scripts that intentionally emit user-facing stdout/stderr lines as part of their CLI contract

**Website (HTTP):**

- GitHub Pages deployment at `AffineDrift.com`
- Service worker handles offline content caching
- All pages render with MathJax notation support

**Textbook Bibliographies:**

- `references/affine-drift.bib` is the shared canonical bibliography source for the site and textbook projects
- `articles/The_Geometry_of_Motion/geometry_of_motion.bib` and `articles/The_Physics_of_Golf/golf_physics.bib` contain book-specific bibliography entries used by Quarto renders
- Chapter sources in both textbook projects are expected to cite foundational literature for geometric mechanics, multibody dynamics, parallel mechanisms, motor control, and impedance-control claims

## 6. Data & Configuration

### Input Data

| Input                    | Format                 | Source                               | Schema                                                   |
| ------------------------ | ---------------------- | ------------------------------------ | -------------------------------------------------------- |
| Swing Trajectories       | YAML / JSON            | User-defined or benchmark datasets   | Defines initial position, velocity, torques, constraints |
| Mathematical Examples    | Quarto Markdown        | `articles/` and `books/` directories | Standard Quarto with LaTeX and code cells                |
| Website Content          | Quarto Markdown (.qmd) | `content/`, `articles/`, `books/`    | Quarto markdown with YAML frontmatter                    |
| Configuration Parameters | YAML                   | `_quarto.yml`, `.github/workflows/`  | Quarto and GitHub Actions configuration                  |

### Output Data

| Output                       | Format              | Destination                      | Description                                         |
| ---------------------------- | ------------------- | -------------------------------- | --------------------------------------------------- |
| Optimized Swing Trajectories | NumPy arrays / JSON | Memory or file system            | Joint angles, velocities, and torques over time     |
| Optimization Reports         | JSON                | User-defined or CI logs          | Convergence metrics, final cost, solver statistics  |
| Static Website               | HTML + CSS + JS     | GitHub Pages (`AffineDrift.com`) | Rendered Quarto site with interactive features      |
| Test Reports                 | JSON / HTML         | GitHub Actions artifacts         | Coverage reports, test results, performance metrics |
| Code Quality Reports         | JSON / Text         | CI logs and artifacts            | Linting results, type checking errors, AST analysis |

### Configuration

**Quarto Configuration** (`_quarto.yml`):

- Website title, author, and metadata
- Output format (HTML for GitHub Pages)
- Theme and CSS customization
- MathJax and KaTeX rendering settings
- Navigation: three top-level dropdowns (`Read` / `Build` / `Connect`) plus `Home`. Each dropdown is capped at 10 items; see `tests/test_navbar_ia.py` for the enforced contract.

**Website design contract** (EPIC #3140):

- Palette is anchored to the design tokens in `css/tokens/colors.css` (`--color-primary-dark: #1a1a2e`, `--color-primary-main: #0f4c75`, `--color-primary-light: #3282b8`) — the UpstreamDrift launcher palette.
- Forbidden patterns in any top-level QMD page (anything outside `articles/**`): inline `style="..."` attributes, `linear-gradient(...)`, and hardcoded hex colors. Enforced by `scripts/check_style_discipline.py` and the `style-discipline-qmd` pre-commit hook.
- Canonical primitives live under `css/components/`: `site-card`, `site-button`, `section-stack`, `page-sidebar`, `entry-list`, `provenance-note`, `home-hero`, `status-banner`. Pages must consume these instead of bespoke per-page styles.
- The homepage source uses one closed raw-HTML fence for the full custom layout; desktop rendering must keep the left navigation, main content, and right table of contents in a three-column grid without escaped layout markup or horizontal overflow.

**GitHub Actions Secrets:**

- GitHub Pages deployment token (auto-configured)

**Python Configuration** (`pyproject.toml`):

- Python version: 3.12
- Core runtime dependencies pinned to exact versions in `requirements.txt`
- Test discovery paths: `tests/` for unit/integration tests and `benchmarks/` for performance benchmarks
- pytest markers: `integration`, `content_lint`, and `benchmark` for test categorization
- Coverage configuration (minimum 50%)
- Opt-in pytest-benchmark suite (`benchmarks/` directory scoped separately from `tests/`)

**Code Quality Settings:**

- **ruff** — Linting rules in `pyproject.toml` under `[tool.ruff]`
- **black** — 100-character line limit (NOT ruff format)
- **mypy** — Type checking enabled for all src/ modules
- **No print() in src/** — Only logging module permitted

## 7. Testing Specification

### Testing Strategy

AffineDrift follows a **test pyramid** strategy: unit tests form the base (fast, numerous), integration tests verify module interactions, and end-to-end tests validate user-facing workflows. The project uses **property-based testing** (Hypothesis) to ensure mathematical correctness across parameter spaces. All code in `src/` must maintain >50% coverage minimum. Critical physics and optimization modules target 80%+ coverage.

### Test Organization

| Category                         | Location                                                                       | Framework             | Markers                    |
| -------------------------------- | ------------------------------------------------------------------------------ | --------------------- | -------------------------- |
| Unit                             | `tests/test_affine_control/`, `tests/test_core/`, `tests/test_tangent_models/` | pytest                | `@pytest.mark.unit`        |
| Integration                      | `tests/test_integration/`                                                      | pytest                | `@pytest.mark.integration` |
| Content/Structure                | `tests/test_content/`                                                          | pytest                | `@pytest.mark.content`     |
| Specialized (DbC, RL benchmarks) | `tests/test_specialized/`                                                      | pytest                | `@pytest.mark.specialized` |
| Performance Benchmarks           | `benchmarks/`                                                                  | pytest-benchmark      | `@pytest.mark.benchmark`   |
| JavaScript/Bibliography          | `tests/`                                                                       | Jest                  | N/A                        |
| End-to-End                       | `tests/e2e/`                                                                   | Playwright (Chromium) | N/A                        |

### Coverage Requirements

| Scope           | Minimum | Current | Enforced By                                 |
| --------------- | ------- | ------- | ------------------------------------------- |
| Overall src/    | 65%     | ~90%    | CI (`pytest --cov=src --cov-fail-under=65`) |
| affine_control/ | 70%     | ~70%    | Critical module coverage gate               |
| core/           | 70%     | ~70%    | Critical module coverage gate               |
| tools/          | 60%     | ~90%    | CI plus critical module coverage gate       |

### Required Test Scenarios

- [x] Unit creation with valid physics parameters returns expected optimization trajectory
- [x] DDP solver converges on benchmark swing problems within tolerance
- [x] iLQR solver produces lower-cost trajectories than initial guess
- [x] Tangent space projections maintain mathematical properties (linearity, completeness)
- [x] Quarto website renders without build errors
- [x] CSS file size stays within enforced budget limits
- [x] All documentation links are valid (no 404s)
- [x] MathJax and KaTeX equations render correctly in browser
- [x] Interactive visualizations (rotation converter) load and function without JS errors
- [x] Smoke tests on Chromium pass for critical pages
- [x] Homepage Playwright checks verify the desktop three-column grid, closed raw HTML rendering, mobile sidebar-section toggles, and no horizontal overflow
- [x] Property-based tests with Hypothesis verify DDP convergence across parameter ranges
- [x] Design-by-contract assertions enforce preconditions and postconditions
- [x] Website `.qmd` citations resolve against project or page bibliography files, excluding Quarto cross-references such as `@eq-` and `@sec-`

## 8. Quality Standards

### Code Quality Tools

| Tool       | Version | Purpose                          | Blocking?           |
| ---------- | ------- | -------------------------------- | ------------------- |
| ruff       | Latest  | Linting (multiple rules)         | Yes                 |
| black      | Latest  | Code formatting (100-char lines) | Yes                 |
| mypy       | Latest  | Static type checking             | Yes                 |
| pytest     | Latest  | Testing framework                | Yes                 |
| pytest-cov | Latest  | Coverage measurement             | Yes                 |
| Hypothesis | Latest  | Property-based testing           | No (optional depth) |
| Jest       | Latest  | JavaScript testing               | Yes                 |
| Playwright | Latest  | E2E testing (Chromium)           | Yes                 |

### Design Principles

- **TDD (Test-Driven Development)**: Enforced for new features; PR must include tests before implementation merges
- **Design by Contract (DbC)**: Preconditions and postconditions on core optimization functions; enforced with assertions and Pydantic models
- **DRY (Don't Repeat Yourself)**: CSS mirror validation ensures stylesheets are not duplicated; AST analysis flags code duplication
- **Orthogonality**: Modules are decoupled; affine_control, core, and tangent_models have minimal coupling; tools are independent

### CI/CD Pipeline

| Workflow               | Trigger             | Purpose                                                                                                | Blocking?         |
| ---------------------- | ------------------- | ------------------------------------------------------------------------------------------------------ | ----------------- |
| `ci-standard.yml`      | Push/PR/manual      | Lint, formatting, blocking mypy, repository policy checks, tests, dependency audit, JS, E2E, HTML lint | Yes               |
| `deploy-website.yml`   | Merge/manual        | Build Quarto site, validate generated assets and health, deploy to GitHub Pages                        | Yes               |
| `ci-benchmarks.yml`    | Push/PR/manual      | Run opt-in performance benchmarks and fail regressions above the configured hard threshold             | Yes               |
| `link-checker.yml`     | PR/scheduled/manual | Validate internal Quarto references and report bounded external URL checks                             | Yes for internals |
| `spec-check.yml`       | PR                  | Block source changes that do not update `SPEC.md` unless explicitly labeled `spec-exempt`              | Yes               |
| `block-self-merge.yml` | PR review/open      | Prevent PR author self-approval and surface distributed review requirements                            | Yes               |

## 9. Dependencies

### Runtime Dependencies

| Package        | Version | Purpose                                                              |
| -------------- | ------- | -------------------------------------------------------------------- |
| numpy          | 2.4.4   | Numerical computations for trajectory optimization                   |
| scipy          | 1.17.1  | Scientific algorithms (optimization, linear algebra)                 |
| matplotlib     | 3.10.8  | Plotting and visualization of swing trajectories                     |
| pydantic       | 2.12.5  | Data validation and runtime type checking                            |
| PyYAML         | 6.0.3   | YAML configuration file parsing                                      |
| beautifulsoup4 | 4.14.3  | HTML parsing for link checking and site analysis                     |
| requests       | 2.33.1  | HTTP requests for external data fetching                             |
| streamlit      | 1.56.0  | Interactive dashboard for visualization _(optional tool dependency)_ |

### Development Dependencies

| Package    | Version  | Purpose                          |
| ---------- | -------- | -------------------------------- |
| pytest     | 8.3.5    | Testing framework                |
| pytest-cov | 7.1.0    | Coverage reporting               |
| hypothesis | 6.151.12 | Property-based testing library   |
| ruff       | 0.15.9   | Linting and code quality         |
| black      | 26.3.1   | Code formatting (100-char lines) |
| mypy       | 1.19.1   | Type checking                    |
| jest       | Latest   | JavaScript testing framework     |
| playwright | Latest   | Browser automation for E2E tests |

### Fleet Dependencies

| Repo          | Relationship            | Description                                               |
| ------------- | ----------------------- | --------------------------------------------------------- |
| QuatEngine    | Referenced in non-goals | Game engine; AffineDrift does not depend on it            |
| UpstreamDrift | Referenced in non-goals | Real-time physics simulator; AffineDrift is complementary |

## 10. Deployment & Operations

### How to Run

```bash
# Prerequisites
- Python 3.12 or later
- Node.js 20 or later
- Quarto 1.6.39 or later
- Git

# Installation
git clone https://github.com/D-sorganization/AffineDrift.git
cd AffineDrift
pip install -r requirements.txt
pip install -r src/tools/wrist_universal_joint/requirements.txt  # optional, for Streamlit wrist tool
npm install

# Running tests
pytest tests/ --cov=src --cov-fail-under=65
npm run test  # JavaScript tests
npx playwright test  # E2E tests

# Running optimization example
python -m affine_control.swing_optimizer --config=example_swing.yaml

# Building website locally
quarto render

# Running CI tools
python src/tools/link_checker.py
python src/tools/site_health.py
python src/tools/code_quality_ast.py
```

### Build Artifacts

| Artifact             | Format          | Destination                                 |
| -------------------- | --------------- | ------------------------------------------- |
| Static Website       | HTML + CSS + JS | GitHub Pages (AffineDrift.com)              |
| Test Reports         | JSON + HTML     | GitHub Actions artifacts and CI logs        |
| Coverage Reports     | LCOV + HTML     | CI artifacts (coverage.xml)                 |
| Quarto Book          | PDF + HTML      | GitHub Pages and releases                   |
| Optimization Results | JSON            | File system or cloud storage (user-defined) |

## 11. Roadmap & Open Issues

### Current Phase

**Active Development & Maintenance**: AffineDrift is a mature research platform with core functionality complete (v1.0.0). Current focus is on expanding educational content, maintaining test coverage above 50%, and refining the optimization algorithms based on real-world validation data. The project serves as both a research artifact and an educational resource.

### Planned Work

| Priority | Item                                                              | Target Date |
| -------- | ----------------------------------------------------------------- | ----------- |
| P0       | Maintain test coverage >50% across all PRs                        | Ongoing     |
| P1       | Publish research paper on affine swing modeling                   | Q2 2026     |
| P1       | Expand tangent space examples and tutorials                       | Q2 2026     |
| P2       | Optimize iLQR solver performance for real-time feedback           | Q3 2026     |
| P2       | Add interactive swing trajectory editor to website                | Q3 2026     |
| P3       | Support additional swing types (left-handed, alternative stances) | Q4 2026     |

### Known Limitations

- **Real-time Performance**: Current optimizers are designed for batch analysis, not real-time control (handled by UpstreamDrift)
- **Physical Accuracy**: Models assume rigid-body dynamics; soft-tissue deformation not modeled
- **Browser Support**: Progressive Web App features require modern browsers (ES6+, Service Worker API)
- **Content Rendering**: Complex 3D visualizations limited to JavaScript WebGL (no headless rendering)
- **Optimization Convergence**: DDP solver may not converge for highly nonlinear swing models; iLQR is more robust but slower

## 12. Change Log

| Date       | Version | Changes                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ---------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 2026-06-09 | 1.0.117 | chore(repo): Pruned the stale root-level `site_libs/` Quarto-bundled vendor artifacts (regenerated by `quarto render` into `docs/site_libs/`) from the tracked tree, git-ignored `/site_libs/` so the generated output cannot return and inflate source-quality budgets, added a governance regression test asserting it stays untracked and ignored, and closed public docstring gaps on `check_local_only_workflows.py::main`, `link-checker.py::main`, and the `TrajectoryOptimizer.optimize`/`ILQRSolver.optimize` boundaries (documenting their DbC preconditions).                    |
| 2026-06-09 | 1.0.118 | refactor(test): Re-export the canonical RL-funnel double-pendulum dynamics from `rl_funnel_benchmark.py` instead of carrying duplicate function bodies, add identity regression coverage for the benchmark public surface, and add adversarial iLQR optimizer precondition plus property-invariant tests for the public `ILQRSolver.optimize` boundary.                                                                                                                                                                                                                                     |
| 2026-05-31 | 1.0.114 | fix(security): Hardened sitemap/render-coverage XML parsing with `defusedxml`, expanded the security audit so it recognizes safe `defusedxml.ElementTree` aliases while continuing to flag unsafe standard-library `ElementTree.fromstring()` usage, and added regression coverage for both safe and unsafe sitemap parsing paths.                                                                                                                                                                                                                                                          |
| 2026-05-23 | 1.0.111 | feat(website): Documented the content-first homepage cleanup, canonical CSS design primitives, and `check_style_discipline.py` QMD lint contract that blocks inline style attributes, gradient functions, and hardcoded hex colors outside excluded generated/content directories.                                                                                                                                                                                                                                                                                                          |
| 2026-05-14 | 1.0.107 | fix(deploy): Normalized Tangent-Space Series source links from legacy spaced generated-path URLs to source-backed `tangent-hyperplane-articles` paths, replaced stale `CRITICAL_REVIEW.md` references with `CRITICS_CORNER.md`, and added regression coverage for those internal links so clean deploy checkouts do not depend on rendered `docs/` artifacts.                                                                                                                                                                                                                               |
| 2026-05-14 | 1.0.106 | fix(accessibility): Marked decorative repository accordion `+` icons as `aria-hidden="true"` so screen readers rely on the button label and `aria-expanded` state instead of announcing redundant icon text, with regression coverage for the repositories page.                                                                                                                                                                                                                                                                                                                            |
| 2026-05-23 | 1.0.107 | 🎨 Palette: Enhanced mobile navbar toggle button accessibility by adding dynamic `title` attributes matching the `aria-label` for native tooltips.                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 2026-05-13 | 1.0.105 | perf(frontend): Replaced startup and navigation `querySelectorAll` scans in `js/navigation.js`, `js/startup-launcher.js`, and `script.js` with direct DOM collection lookups to reduce initialization overhead, and extended the Playwright smoke timeout so the rendered-site E2E gate remains stable on slower runners while exercising the same critical flows.                                                                                                                                                                                                                          |
| 2026-05-07 | 1.0.100 | fix(ci): normalized the PR 3062 touched regression tests to the repository's required Black 100-column formatting and recorded the no-behavior-change test-maintenance update so SPEC freshness tracks the branch's quality-gate-only edits.                                                                                                                                                                                                                                                                                                                                                |
| 2026-05-03 | 1.0.99  | fix(ci): hardened production-readiness gates by making mypy and HTML validation blocking, pinning workflow actions to immutable SHAs with a CI policy check, removing tracked generated agent automation artifacts, blocking those artifacts from returning, and tightening the site CSP by removing `unsafe-eval`.                                                                                                                                                                                                                                                                         |
| 2026-04-23 | 1.0.78  | fix(content): corrected Quarto cross-reference syntax in `articles/affine-nature-golf-swing.qmd` and `articles/inverse-dynamics.qmd`, replacing undefined appendix/equation citation keys with native section/equation refs, moving equation labels to renderable display-math positions, and adding content regression checks for these patterns.                                                                                                                                                                                                                                          |
| 2026-04-23 | 1.0.77  | chore(hygiene): removed tracked root-level review, lint, generated PDF, scratch, and temporary issue-body artifacts; added regression checks that prevent these root artifacts and book-source `.tmp` files from returning; and expanded ignore rules for transient automation/review scratch outputs.                                                                                                                                                                                                                                                                                      |
| 2026-04-22 | 1.0.75  | fix(content): corrected the ZTCF Identifiability Critique link in `articles/theory-part2.qmd` and added a regression guard preventing top-level article links from escaping above the rendered article root.                                                                                                                                                                                                                                                                                                                                                                                |
| 2026-04-18 | 1.0.72  | fix(ci): made TinyTeX path discovery persistent across Quarto PDF workflow steps by exporting common TinyTeX/local binary directories and appending them to `GITHUB_PATH` before TeX verification and rendering.                                                                                                                                                                                                                                                                                                                                                                            |
| 2026-04-18 | 1.0.71  | fix(ci): supplied a non-secret placeholder Codecov token for PR-only Quarto PDF rendering so dotenv validation does not block local runner PDF artifacts, removed a Quarto syntax scanner violation in the DDP pseudocode, and restored the Physics of Golf DCR glossary phrase expected by content lint.                                                                                                                                                                                                                                                                                   |
| 2026-04-18 | 1.0.70  | fix(ci): added the Geometry of Motion LaTeX style, TikZ libraries, theorem fallbacks, and shared math macro fallbacks to the Quarto PDF configuration; normalized Quarto chapter LaTeX shorthands and fixed exposed PDF content errors so the self-hosted render completes instead of failing on HTML-only MathJax macros or stale masked errors.                                                                                                                                                                                                                                           |
| 2026-04-18 | 1.0.69  | fix(ci): hardened the Quarto PDF render workflow on self-hosted runners by skipping TinyTeX installation when TeX is already available, bounding install/render/upload steps with timeouts, failing on real render errors instead of masking them, and cleaning up orphaned Quarto/TeX child processes.                                                                                                                                                                                                                                                                                     |
| 2026-04-16 | 1.0.66  | feat(palette): added explicit `type="button"` attribute to all dynamically created button elements in `js/ui-components.js`, `js/pdf.js`, and `js/dark-mode-toggle.js` to prevent unintended form submission behavior when these buttons are placed inside form elements.                                                                                                                                                                                                                                                                                                                   |
| 2026-04-16 | 1.0.65  | ci(content): hardened `ci-standard.yml` system dependency installation so self-hosted runner apt lock contention produces a warning instead of blocking content-only validation, and documented the Contraction Tangent layman's and critics content merge resolution.                                                                                                                                                                                                                                                                                                                      |
| 2026-04-12 | 1.0.58  | fix(ci): added RUN_UI_TESTS environment guard to matplotlib.use("QtAgg") in qt_canvases.py to allow headless verification without triggering ImportError, and removed redundant pytest-xvfb plugin. fix(test): skip legacy wrist launcher test when Qt runtime is unavailable via `pytest.skip`, and reformat test assertions to comply with black 100-char style                                                                                                                                                                                                                           |
| 2026-04-11 | 1.0.57  | refactor(src): decomposed ten oversized functions (`_simulate_putt`, `ILQRSolver._backward_pass`, `ILQRSolver.optimize`, `BallFlightDynamics.dynamics`, `BallFlightDynamics.simulate`, `compute_hessian_norm`, `batch_convert`, `collect_python_file_metrics`, `plot_acceleration`, `SwingOptimizer.__init__`) into thin orchestrators plus focused helpers, preserving numerical and observable behavior (issue #2362).                                                                                                                                                                    |
| 2026-04-12 | 1.0.56  | fix(ci): installed PyQt6 in the standard Python test job so the legacy wrist universal-joint launcher API regression can import the Qt canvas wrappers on GitHub-hosted runners.                                                                                                                                                                                                                                                                                                                                                                                                            |
| 2026-04-11 | 1.0.55  | docs(textbook): resolved Physics of Golf citation TODO markers across `.tex` and `.qmd` sources (issue #2346). Existing `golf_physics.bib` entries (Nesbit2005, McTeigue1994, Penner2003, Jorgensen1994, Broadie2014, McGill2007, hosea1990biomechanical, DeLeva1996, Winter2009, Hume2005, Gatt1998, Kandel2013, Delp2007, etc.) were attached to the corresponding claims; remaining TODOs where no matching bib entry exists were converted to a new visible `\citeneeded{}` LaTeX placeholder (defined in `golf_physics.sty`) so unresolved citations are surfaced in the rendered PDF. |
| 2026-04-12 | 1.0.54  | refactor(affine-control): decomposed `ResidualMonitor.update()` into focused residual-estimation, hysteresis-counter, transition-selection, and transition-application helpers while preserving the LQR/MPC_WARN/MPC_FULL state-machine behavior.                                                                                                                                                                                                                                                                                                                                           |
| 2026-04-12 | 1.0.53  | refactor(wrist): decomposed the Qt transmission sweep plotter into focused helpers for visible series, current-angle markers, and axis metadata, with source-level regression coverage for the extracted structure.                                                                                                                                                                                                                                                                                                                                                                         |
| 2026-04-12 | 1.0.52  | test(tooling): added closeout coverage for the formerly monolithic wrist model launchers and mypy autofix script so all listed legacy entrypoints remain thin wrappers around their packaged implementations.                                                                                                                                                                                                                                                                                                                                                                               |
| 2026-04-12 | 1.0.51  | refactor(golf-simulation): decomposed `GolfHole.get_terrain()` into focused distance and play-corridor helpers while preserving tee, green, fairway, rough, and custom terrain override behavior with targeted regression coverage.                                                                                                                                                                                                                                                                                                                                                         |
| 2026-04-11 | 1.0.50  | refactor(golf-simulation): decomposed terrain bounce physics into focused validation, surface-normal normalization, velocity decomposition, and friction helpers while preserving post-impact velocity and spin behavior with edge-case tests.                                                                                                                                                                                                                                                                                                                                              |
| 2026-04-11 | 1.0.49  | refactor(golf-simulation): moved championship course hole definitions and handicaps into declarative module-level data so `create_championship_course()` stays focused on building `GolfHole` instances, with regression coverage for par, yardage, hole ordering, and handicap stability.                                                                                                                                                                                                                                                                                                  |
| 2026-04-11 | 1.0.48  | refactor(rl-funnel): centralized benchmark result, result formatting, pendulum constants, mass-matrix, and state-vector validation in `src/tools/rl_funnel_support.py`, with compatibility re-export coverage across the RL funnel modules.                                                                                                                                                                                                                                                                                                                                                 |
| 2026-04-11 | 1.0.47  | refactor(wrist): replaced the duplicated docs/content Universal_Joint_Model_Enhanced.py monolith with a thin compatibility launcher that re-exports the maintained wrist universal-joint modules, with regression coverage for the legacy public API surface.                                                                                                                                                                                                                                                                                                                               |
| 2026-04-11 | 1.0.46  | fix(textbook): documented the modeling context for differing double-pendulum and triple-pendulum parameter sets in Physics of Golf chapters 3, 6, and 8, with content checks guarding the explanatory notes.                                                                                                                                                                                                                                                                                                                                                                                |
| 2026-04-11 | 1.0.45  | fix(textbook): corrected Physics of Golf chapter 11 from a static Euler-Bernoulli form to the dynamic equation including $\rho A \partial_t^2 w$, aligned supporting prose and LaTeX source, and added a regression assertion against static-only omissions.                                                                                                                                                                                                                                                                                                                                |
| 2026-04-11 | 1.0.44  | fix(textbook): corrected Geometry of Motion chapter 1 statements about time-dependent coordinate-change eigenvalues and SO(3) tangent spaces, with source-content regression checks for the corrected mathematical claims.                                                                                                                                                                                                                                                                                                                                                                  |
| 2026-04-11 | 1.0.43  | fix(textbook): corrected Physics of Golf chapter 31 face-angle and path-angle directional sensitivity values so the later sensitivity section matches the earlier 13--20 yards-per-degree face-angle range, with regression coverage against the old 60--70 yards-per-degree claim.                                                                                                                                                                                                                                                                                                         |
| 2026-04-11 | 1.0.42  | refactor(tooling): decomposed the mypy autofix agent into a package with focused parser, strategy, file, model, and runner modules while keeping the legacy script path callable for GitHub workflow compatibility.                                                                                                                                                                                                                                                                                                                                                                         |
| 2026-04-11 | 1.0.41  | refactor(simulation): allowed `RoundSimulator` to receive an injected `PuttingSimulator`, preserving the default flat-green path while enabling calibrated putting physics in tests and callers.                                                                                                                                                                                                                                                                                                                                                                                            |
| 2026-04-11 | 1.0.40  | fix(physics): corrected putting deceleration to use the Stimpmeter stopping-distance formula in both direct putting simulation and round-level putt speed estimation, with regression coverage for Stimp 10 rollout distance.                                                                                                                                                                                                                                                                                                                                                               |
| 2026-04-11 | 1.0.39  | test(algorithms): replaced placeholder algorithm smoke checks with executable coverage for the iLQR optimizer and RL funnel controllers, including finite-control and validation assertions.                                                                                                                                                                                                                                                                                                                                                                                                |
| 2026-04-11 | 1.0.38  | chore(deps): pinned root Python dependencies exactly and isolated the optional Streamlit wrist-tool requirements in the tool-local requirements file while preserving documented setup steps.                                                                                                                                                                                                                                                                                                                                                                                               |
| 2026-04-11 | 1.0.37  | fix(assessment): synchronized `ASSESSMENT_DEFINITIONS` category names with the canonical A-N `CATEGORIES` map and added regression coverage for report-label consistency.                                                                                                                                                                                                                                                                                                                                                                                                                   |
| 2026-04-11 | 1.0.35  | fix(pwa): bounded the service-worker cache and surfaced update notices so stale offline content refreshes visibly without unbounded storage growth                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 2026-04-11 | 1.0.34  | fix(wrist): switched wrist-model Matplotlib helpers from pyplot state to object-oriented `Figure` construction and removed resource caching from array-backed plot functions.                                                                                                                                                                                                                                                                                                                                                                                                               |
| 2026-04-11 | 1.0.33  | fix(ci): removed duplicate requirements installation from `ci-standard.yml`, enabled pip caching, allowed workflow-only changes to trigger CI, aligned PR auto-labeler path rules with the repository layout, and cleaned stale SPEC conflict markers.                                                                                                                                                                                                                                                                                                                                      |
| 2026-04-11 | 1.0.32  | chore(deps): pinned previously unpinned root requirements and moved streamlit out of core requirements into the wrist tool optional requirements file.                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| 2026-04-11 | 1.0.31  | fix(latex): documented the tcolorbox package loading contract to avoid option-clash failures in the golf physics PDF build.                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 2026-04-11 | 1.0.30  | fix(logging): made `setup_logging()` import-order safe by avoiding root `basicConfig()` calls for named loggers while preserving root configuration for script entry points.                                                                                                                                                                                                                                                                                                                                                                                                                |
| 2026-04-11 | 1.0.30  | fix(tools): preserved escaped LaTeX percent signs during comment cleanup and added regression coverage for `\%` content followed by trailing comments                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| 2026-04-11 | 1.0.29  | fix(critical): hardened workflow event payload handling, corrected wrist universal-joint ratio semantics, refreshed the chapter 3 double-pendulum numeric example, and restored package-qualified batch converter imports                                                                                                                                                                                                                                                                                                                                                                   |
| 2026-04-11 | 1.0.27  | fix(tools): prevented display math created from LaTeX `equation` environments in `src/tools/latex_to_html.py` from being wrapped twice, and added a regression test for the single-wrapper output                                                                                                                                                                                                                                                                                                                                                                                           |
| 2026-04-14 | 1.0.28  | security(xss): Fixed DOM-based XSS vulnerability in `script.js` history list component by safely validating and sanitizing `href` properties                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 2026-04-11 | 1.0.26  | fix(testing): made `make test` run Python coverage before JavaScript coverage and removed the bare `pass` coverage exclusion so stubs remain visible in reports                                                                                                                                                                                                                                                                                                                                                                                                                             |
| 2026-04-11 | 1.0.25  | fix(tools): made RL benchmark comparison honor the caller-provided `dt` when generating reference trajectories and added regression coverage for the reference time grid                                                                                                                                                                                                                                                                                                                                                                                                                    |
| 2026-04-09 | 1.0.24  | docs(articles): Refined the Layman's Terms section in Contraction_Tangent_CRITIC.qmd to use relatable analogies and improve clarity                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| 2026-04-07 | 1.0.19  | chore(types): annotated the remaining public Python functions in `src/` and `scripts/`, added an AST regression test to keep return annotations from drifting, and closed the final actionable slice of assessment issue #2241 after auditing stale print/config findings                                                                                                                                                                                                                                                                                                                   |
| 2026-04-07 | 1.0.18  | fix(scripts): replaced remaining raw script-level `print()` calls with explicit stdout/stderr helpers, made maintenance scripts import-safe with `main()` entry points, and added CLI-output regression tests for the affected utilities                                                                                                                                                                                                                                                                                                                                                    |
| 2026-04-07 | 1.0.17  | fix(ci): documented the explicit `SwingOptimizer` mock-solver opt-in at construction time, widened `ci-standard.yml` coverage enforcement to the full `src/` tree, and made the main `pip-audit` gate blocking                                                                                                                                                                                                                                                                                                                                                                              |
| 2026-04-05 | 1.0.15  | security(xss): Prevented XSS in polynomial evaluation by explicitly stripping allowed math variables/functions and validating the remainder strictly via regex before `new Function` evaluation in `grip_angle_simulator.html`                                                                                                                                                                                                                                                                                                                                                              |
| 2026-04-08 | 1.0.23  | security(xss): Fixed DOM-based XSS vulnerability in `.qmd` history list components by replacing `innerHTML` with `document.createElement` and safe text assignment                                                                                                                                                                                                                                                                                                                                                                                                                          |
| 2026-04-06 | 1.0.16  | ci(content): added citation-resolution checks for website `.qmd` sources, covering root and nested Quarto bibliography files and excluding Quarto cross-references from unresolved-key failures                                                                                                                                                                                                                                                                                                                                                                                             |
| 2026-04-04 | 1.0.13  | security(xss): Fixed XSS vulnerability in `notes-workspace.js` by avoiding `document.write` with string interpolation and safely assigning `value` property                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 2026-04-05 | 1.0.15  | fix(tools): made `fix_html.py` repo-root portable with explicit input/output resolution and dry-run support                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 2026-04-04 | 1.0.15  | perf(frontend): Apply resize:none to auto-growing textareas managed by `initAutoGrowTextareas()` to prevent user manual resizing which conflicts with JS logic                                                                                                                                                                                                                                                                                                                                                                                                                              |
| 2026-04-04 | 1.0.14  | perf(frontend): Replaced DOM-based escapeHtml with Regex string replacement in JS to avoid layout thrashing and reduce memory allocations                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| 2026-04-05 | 1.0.15  | security(xss): Fixed XSS vulnerability in `notes-workspace.js` popout feature by removing `document.write` template literal evaluation.                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 2026-04-03 | 1.0.12  | security(matlab): Fixed path escaping vulnerability in `matlab_quality_check.py` by properly escaping single quotes for MATLAB strings instead of aggressively removing characters                                                                                                                                                                                                                                                                                                                                                                                                          |
| 2026-05-27 | 1.0.17  | Performance fix: replaced expensive `.querySelector()` calls with native `.getElementsByTagName()[0]` and `.getElementsByClassName()[0]` in script.js for faster descendant DOM lookups.                                                                                                                                                                                                                                                                                                                                                                                                    |
| 2026-04-01 | 1.0.10  | security(links): Added `rel="noopener noreferrer"` to `target="_blank"` links generated by `latex_utils.py` and `bibliography.js` to mitigate reverse tabnabbing vulnerabilities                                                                                                                                                                                                                                                                                                                                                                                                            |
| 2026-04-06 | 1.0.16  | Added repository-wide Quarto citation-key integrity validation in `ci-standard.yml`, documented `scripts/check_qmd_citation_keys.py`, and updated review-bot workflow handling so trusted automated reviewers do not fail PR automation                                                                                                                                                                                                                                                                                                                                                     |
| 2026-03-30 | 1.0.9   | fix(html): corrected malformed HTML structure in Wrist_Universal_Claude.html — removed stray </p> tags after list elements and fixed <p> tags improperly wrapping <ul>/<ol> block content                                                                                                                                                                                                                                                                                                                                                                                                   |
| 2026-03-30 | 1.0.6   | fix(ci): aligned regression tests with current workflows — mock-solver guard asserted at optimize() per SwingOptimizer contract; test_deployment_integrity updated to match Quarto render action in ci-standard.yml; added dotenv-example removal step before E2E render; updated torque-generator docstrings in Universal_Joint_Model_Enhanced.py                                                                                                                                                                                                                                          |
| 2026-03-30 | 1.0.6   | A-N Assessment remediation (issue #2012): auto-formatted 10 files to comply with black 100-char limit; added missing docstrings to priority_score, **post_init**, \_requires_token, create_issue, sha256, sync_one, main, **init**, \_handle_text/\_code_block/\_inline_code/\_display_math/\_inline_math, setup_logging_with_timestamp, find_markdown_files across scripts/                                                                                                                                                                                                                |
| 2026-03-30 | 1.0.5   | Performance fix: replaced O(n²) list.index() loop in putt simulator with enumerate() for linear-time hole-score lookups in round_simulator.py                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| 2026-03-30 | 1.0.4   | Fixed remaining CI failures in batch-4 PR: replaced bare HTML TODO comments with inline caveat phrasing ("illustrative", "depends on", etc.) in ch16, ch18--ch31 qmd files and ch14--ch16, ch19 tex files to satisfy checker window requirements                                                                                                                                                                                                                                                                                                                                            |
| 2026-03-30 | 1.0.3   | Added TODO(citation) markers and humble qualifiers for unsourced numerical claims in ch14--ch31 LaTeX chapters of The Physics of Golf — issues #1881, #1882, #1883, #1884, #1885, #1886, #1887, #1888, #1889, #1890, #1892, #1893, #1894, #1895, #1896, #1897, #1898, #1899 (batch 2)                                                                                                                                                                                                                                                                                                       |
| 2026-03-30 | 1.0.2   | Added caveat phrasing and improved humble language for uncited numerical claims in ch02, ch03, ch04, ch07, ch10, ch11, ch13, ch18, ch19, ch20, ch21, ch23, ch25, ch26, ch29, ch31, and glossary of The Physics of Golf (content audit wave 2; issues #2007--#2011)                                                                                                                                                                                                                                                                                                                          |
| 2026-03-30 | 1.0.2   | Added citation markers, TODO notes, and humble phrasing for unsourced numerical claims and study references in ch22--ch31, glossary.qmd (The Physics of Golf), and 01-throwing-away-target.qmd (The Geometry of Motion) — issues #1921, #1922, #1924, #1925, #1926, #1927, #1928, #1929, #1930, #1931, #1932, #1948 (batch 4)                                                                                                                                                                                                                                                               |
| 2026-03-30 | 1.0.1   | Improve accessibility for Critics Corner with aria-controls                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| 2026-03-30 | 1.0.1   | Added citation markers, TODO notes, and humble phrasing for unsourced claims in chapters 1--13 of The Physics of Golf (issues #1868--#1880, batch 1)                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| 2026-03-30 | 1.0.1   | Added citation markers (TODO comments) and humble qualifiers to unsourced numerical claims in ch01--ch21 of The Physics of Golf — issues #1900--#1920 (batch 3)                                                                                                                                                                                                                                                                                                                                                                                                                             |
| 2026-03-30 | 1.0.0   | Consolidated frontend scroll event handlers via `requestAnimationFrame`                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 2026-03-30 | 1.0.0   | Documented PR CI dependency-audit plus rendered-site E2E gate, mock-solver opt-in behavior at `SwingOptimizer.optimize`, and bibliography duplicate-alias integrity guardrails                                                                                                                                                                                                                                                                                                                                                                                                              |
| 2026-03-28 | 1.0.0   | Initial SPEC.md specification for AffineDrift v1.0.0 — all core features documented and implemented                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| 2026-04-13 | 1.0.63  | content(laymans): Added `.jules/laymans_data/` tracking files cataloguing Layman's Terms coverage across all articles via Jules Layman's Terms Writer automation.                                                                                                                                                                                                                                                                                                                                                                                                                           |
| 2026-04-13 | 1.0.62  | content(laymans): Updated Layman's Terms section in `Contraction_Tangent_CRITIC.qmd` with improved analogies — replaced abstract descriptions with more relatable real-world comparisons.                                                                                                                                                                                                                                                                                                                                                                                                   |
| 2026-04-13 | 1.0.60  | feat(ui): Added native `title` tooltips to icon-only buttons (`dark-mode-toggle`, `back-to-top`, lightbox close/zoom) in `js/dark-mode-toggle.js` and `js/ui-components.js` to improve discoverability and accessibility for pointer-device users.                                                                                                                                                                                                                                                                                                                                          |
| 2026-04-12 | 1.0.58  | fix(tests): Guarded `matplotlib.use("QtAgg")` in `src/tools/wrist_universal_joint/qt_canvases.py` to prevent headless CI runner crashes when pytest imports the module.                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 2026-04-13 | 1.0.59  | perf(frontend): Optimized `initAriaLabels` in `script.js` by replacing `querySelectorAll` with `O(1)` live collections (`getElementsByTagName`, `getElementsByClassName`) and consolidating input loops to reduce layout thrashing.                                                                                                                                                                                                                                                                                                                                                         |
| 2026-04-13 | 1.0.61  | content(critics): Added Critics' Comments section to `Contraction_Tangent_CRITIC.qmd` via Jules Critics Comments Writer automation; updated `.jules/critics_data/` tracking files.                                                                                                                                                                                                                                                                                                                                                                                                          |
| 2026-04-12 | 1.0.59  | ci: Add fleet mode-aware `pick-runner` dispatcher to all CI workflows for self-hosted runner routing with hybrid/local/cloud modes.                                                                                                                                                                                                                                                                                                                                                                                                                                                         |

---

<!--
  SPEC MAINTENANCE RULES:

  1. WHEN TO UPDATE: Any PR that adds, removes, or changes functionality
     described in this spec MUST include a corresponding spec update.

  2. WHO UPDATES: The PR author (human or agent) is responsible.

  3. CI ENFORCEMENT: The spec-check workflow will flag PRs where source
     files changed but SPEC.md did not. This is a blocking check.

  4. REVIEW: Spec changes should be reviewed with the same rigor as code.

  5. VERSION: Bump the Spec Version field when making substantive changes.
     Use semver: major (structure change), minor (new features), patch (corrections).
-->

| 2026-04-17 | 1.0.67 | ui(accessibility): Added rotation transform `aria-expanded="true"` for `.toggle-icon` inside `.sidebar-section-toggle` in `styles.css` to properly sync the visual state with the semantic state of collapsible sidebars. |
| 2026-04-18 | 1.0.68 | fix(security): Prevent DOM-based XSS in PDF export by escaping pageTitle before injecting via innerHTML. |
| 2026-05-05 | 1.0.69 | security(xss): Fixed CRITICAL client-side code injection vulnerability in polynomial signal generator (`WristPolynomialEvaluator`) by replacing unsafe `new Function` evaluation with a custom AST-based parser and evaluator. The vulnerability could allow arbitrary JavaScript execution when processing malicious mathematical expressions. Verified against test cases including `1; alert(1)` and confirmed correct parsing of valid expressions with mathematical functions and scientific notation. |
| 2026-05-06 | 1.0.70 | perf(frontend): Replaced the animated-section `querySelectorAll(...:not(...))` scan in `script.js` with live `<section>` collection filtering, preserved the zero-torque canonical definition note with compliant markdown in `affine-nature-golf-swing.qmd`, and aligned tangent-article regression tests with the lowercase article path plus the renamed residual Hessian helper. |
| 2026-05-07 | 1.0.101 | ci(workflows): pin the redundant Jules issue/PR closer workflows to immutable `create-github-app-token`, `checkout`, and `setup-python` SHAs so workflow pinning passes on PR branches and `main`. |
| 2026-05-07 | 1.0.102 | fix(content): remove orphaned Geometry of Motion split chapter `.qmd` files so Volume 0 matches the canonical include list and Volume II renders solely from `volume2_content.qmd`, restoring the cleanup regression guard on PR branches. |
| 2026-05-08 | 1.0.103 | perf(frontend): Optimized initAnchorLinks by replacing querySelectorAll with getElementsByTagName for faster heading lookup. |
| 2026-05-08 | 1.0.104 | 🎨 Palette: Add `aria-hidden="true"` to purely decorative SVG icons within the `.mobile-menu-toggle` button in `index.qmd` to improve screen reader accessibility. |
| 2026-07-20 | 1.0.105 | fix(security): Prevent DOM-based XSS in grip angle simulator by refactoring `addCheckbox` to use native DOM methods instead of `innerHTML`. |
| 2026-05-19 | 1.0.109 | chore(deps): consolidated compatible npm, Python, benchmark, and GitHub Actions dependency bumps into one repo-level PR; workflow action pins remain immutable and the benchmark workflow preserves a single top-level concurrency policy. |
| 2026-05-22 | 1.0.110 | fix(ci): normalized pre-commit hook execution by formatting the wrist universal-joint Streamlit app, removing duplicate golf constants, and documenting Streamlit cache decorator type ignores so mypy and noqa-justification hooks pass without bypasses. |
| 2026-05-24 | 1.0.112 | perf(frontend): Optimized global `keydown` and `mousedown` event listeners in `js/accessibility.js` by caching the keyboard active state and only mutating the DOM attribute when the state actually changes, preventing redundant layout invalidations on every keystroke. |
| 2026-05-29 | 1.0.113 | fix(layout): Restored the homepage raw-HTML fence and Quarto page-grid overrides so the desktop homepage renders as a clean three-column layout, added Playwright and source-level regressions for escaped layout markup, mobile section toggles, and horizontal overflow, removed the anti-phantom workflow's dependency on runner-installed `jq`, scoped PR e2e rendering to the pages covered by the smoke suite, and removed fragile setup-action cache restores from PR-facing workflows. |
| 2026-06-03 | 1.0.114 | perf(frontend): Consolidated multiple `.closest()` checks into a single comma-separated selector string in `script.js` to reduce CSS parsing overhead and JS-to-C++ boundary crossings. |
| 2026-06-03 | 1.0.115 | fix(security): Prevent DOM-based XSS in grip angle simulator by refactoring info panel generation to use native DOM methods instead of `innerHTML`. |
| 2026-06-03 | 1.0.116 | 🎨 Palette: Add dynamic `title` attributes to collapsible headers based on their `aria-expanded` state to improve accessibility. |

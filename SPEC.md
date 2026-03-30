# SPEC.md — Repository Specification Document

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

| Field | Value |
|-------|-------|
| **Repository Name** | `AffineDrift` |
| **GitHub URL** | `https://github.com/D-sorganization/AffineDrift` |
| **Owner** | D-sorganization |
| **Primary Language(s)** | Python 3.12, JavaScript ES6+, Quarto |
| **License** | MIT |
| **Current Version** | 1.0.0 |
| **Spec Version** | 1.0.2 |
| **Last Spec Update** | 2026-03-30 |

## 2. Purpose & Mission

AffineDrift is a research platform that explores golf swing biomechanics through the lens of affine control theory. The project combines rigorous mathematical modeling with interactive educational content, publishing research-quality materials via a Quarto-based website hosted on GitHub Pages. It demonstrates how differential dynamic programming and iterative linear-quadratic regulation (iLQR) can optimize swing trajectories, while serving as an educational bridge between control theory and biomechanics for the broader scientific community.

## 3. Goals & Non-Goals

### Goals

- Model golf swings as affine controllable systems with mathematical rigor, enabling optimization through advanced control algorithms
- Publish and maintain research-quality educational content via Quarto website (AffineDrift.com) on GitHub Pages
- Implement swing trajectory optimization using differential dynamic programming (DDP) and iLQR solvers
- Achieve and maintain >50% test coverage with property-based testing (Hypothesis) across all critical modules
- Provide comprehensive educational resources that bridge control theory and applied biomechanics

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
├── .github/workflows/           # 54 GitHub Actions workflows
│   ├── ci-standard.yml          # Main CI pipeline
│   ├── deploy-website.yml       # Quarto site build and deployment
│   ├── test-coverage.yml        # Test coverage reporting
│   ├── link-check.yml           # Link validation
│   ├── css-budget.yml           # CSS size enforcement
│   └── [other workflows]        # Jules agents, specialized tests, etc.
├── tests/                       # Additional test organization
│   └── e2e/                     # End-to-end Playwright tests
├── _quarto.yml                  # Quarto configuration
├── pyproject.toml               # Python project metadata and dependencies
├── package.json                 # JavaScript dependencies
├── SPEC.md                      # This specification document
└── README.md                    # Project overview and quick start
```

### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Swing Optimizer | `src/affine_control/swing_optimizer.py` | DDP and iLQR-based trajectory optimization for golf swings |
| DDP Solver | `src/affine_control/ddp_solver.py` | Core differential dynamic programming algorithm |
| Core Constants | `src/core/constants.py` | Physical and mathematical constants used throughout |
| iLQR Optimizer | `src/core/optimizers.py` | Iterative linear-quadratic regulation solver |
| Tangent Space Models | `src/tangent_models/` | Tangent space and hyperplane mathematical abstractions |
| Link Checker | `src/tools/link_checker.py` | CI/CD tool for validating documentation links |
| Site Health Monitor | `src/tools/site_health.py` | Automated website health and performance checks |
| Code Quality Analyzer | `src/tools/code_quality_ast.py` | AST-based Python code quality analysis |
| Rotation Converter | `js/rotation-converter/` | Interactive 3D rotation visualization and converter |
| Search Functionality | `js/search.js` | Full-text search across website content |
| Quarto Configuration | `_quarto.yml` | Website build and rendering configuration |
| Test Suite | `tests/` | 80+ pytest and Jest test files |

## 5. Desired Functionality

### Core Features

| # | Feature | Status | Description |
|---|---------|--------|-------------|
| F1 | Quarto Website Rendering and Deployment | ✅ | Renders Quarto markdown (.qmd) source files into static HTML and deploys to GitHub Pages |
| F2 | Affine Control Theory Swing Optimizer | ✅ | Implements DDP and iLQR algorithms to optimize golf swing trajectories as affine controllable systems |
| F3 | Tangent Space and Hyperplane Models | ✅ | Provides mathematical models for tangent space methods with educational examples |
| F4 | Interactive JavaScript Visualizations | ✅ | Rotation converter, search interface, and mathematical visualization components |
| F5 | Mathematical Notation Rendering | ✅ | Supports MathJax and KaTeX for rendering LaTeX equations in web content |
| F6 | Property-Based Testing with Hypothesis | ✅ | Comprehensive property-based testing strategy using Hypothesis framework |
| F7 | CSS Budget Enforcement | ✅ | Automated CI enforcement of CSS file size limits to maintain performance |
| F8 | Mirror Validation | ✅ | Ensures duplicate stylesheets match canonical versions across the codebase |
| F9 | GitHub Actions Automation | ✅ | 54 CI/CD workflows including Jules automation agents for code analysis and deployment |
| F10 | Progressive Web App Support | ✅ | Service worker and manifest for PWA capabilities (offline access, installability) |
| F11 | Textbook Compilation Pipeline | ✅ | Quarto pipeline to compile educational materials into publishable textbook format |
| F12 | Textbook claim guardrail | ✅ | PR CI blocks newly added unsupported quantitative or study claims in textbook content unless they include a citation or an explicit illustrative caveat |
| F13 | PR site-build and dependency-audit gate | ✅ | `ci-standard.yml` audits Python dependencies with `pip-audit`, renders the Quarto site in PR CI, syncs frontend assets, and runs Playwright smoke tests against the generated docs |
| F14 | Bibliography duplicate-alias guardrail | ✅ | Reference-integrity tests require duplicate bibliography records to carry an explicit legacy-compatibility note instead of silently diverging |

### API / Interface Contract

**Python API:**
- `affine_control.swing_optimizer.SwingOptimizer` — Main optimization interface
  - Constructor permits a missing solver for inspection/tests but emits a warning and binds the documented mock implementation
  - `optimize(...)` rejects the mock solver unless `SwingOptimizationConfig.allow_mock_solver=True`
  - `optimize(swing_model, constraints) -> OptimizedTrajectory` — Run trajectory optimization
- `core.optimizers.iLQR` — iLQR solver
  - `solve(dynamics, cost_fn, initial_trajectory) -> Solution` — Compute optimal trajectory
- `tangent_models.TangentSpaceModel` — Tangent space abstraction
  - `project(vector) -> Vector` — Project to tangent space

**JavaScript API:**
- `RotationConverter` — Interactive 3D rotation tool
  - `convert(matrix, target_format) -> string` — Convert rotation representations
- `SearchIndex.query(term) -> SearchResults` — Full-text search across content

**CLI Tools:**
- `link-checker.py` — Validate all documentation links
- `site-health.py` — Generate health report on website assets
- `code-quality-ast.py` — Analyze Python code structure and metrics

**Website (HTTP):**
- GitHub Pages deployment at `AffineDrift.com`
- Service worker handles offline content caching
- All pages render with MathJax notation support

## 6. Data & Configuration

### Input Data

| Input | Format | Source | Schema |
|-------|--------|--------|--------|
| Swing Trajectories | YAML / JSON | User-defined or benchmark datasets | Defines initial position, velocity, torques, constraints |
| Mathematical Examples | Quarto Markdown | `articles/` and `books/` directories | Standard Quarto with LaTeX and code cells |
| Website Content | Quarto Markdown (.qmd) | `content/`, `articles/`, `books/` | Quarto markdown with YAML frontmatter |
| Configuration Parameters | YAML | `_quarto.yml`, `.github/workflows/` | Quarto and GitHub Actions configuration |

### Output Data

| Output | Format | Destination | Description |
|--------|--------|-------------|-------------|
| Optimized Swing Trajectories | NumPy arrays / JSON | Memory or file system | Joint angles, velocities, and torques over time |
| Optimization Reports | JSON | User-defined or CI logs | Convergence metrics, final cost, solver statistics |
| Static Website | HTML + CSS + JS | GitHub Pages (`AffineDrift.com`) | Rendered Quarto site with interactive features |
| Test Reports | JSON / HTML | GitHub Actions artifacts | Coverage reports, test results, performance metrics |
| Code Quality Reports | JSON / Text | CI logs and artifacts | Linting results, type checking errors, AST analysis |

### Configuration

**Quarto Configuration** (`_quarto.yml`):
- Website title, author, and metadata
- Output format (HTML for GitHub Pages)
- Theme and CSS customization
- MathJax and KaTeX rendering settings
- Navigation menu structure

**GitHub Actions Secrets:**
- GitHub Pages deployment token (auto-configured)

**Python Configuration** (`pyproject.toml`):
- Python version: 3.12
- Dependencies pinned with version ranges
- Test discovery paths
- Coverage configuration (minimum 50%)

**Code Quality Settings:**
- **ruff** — Linting rules in `pyproject.toml` under `[tool.ruff]`
- **black** — 100-character line limit (NOT ruff format)
- **mypy** — Type checking enabled for all src/ modules
- **No print() in src/** — Only logging module permitted

## 7. Testing Specification

### Testing Strategy

AffineDrift follows a **test pyramid** strategy: unit tests form the base (fast, numerous), integration tests verify module interactions, and end-to-end tests validate user-facing workflows. The project uses **property-based testing** (Hypothesis) to ensure mathematical correctness across parameter spaces. All code in `src/` must maintain >50% coverage minimum. Critical physics and optimization modules target 80%+ coverage.

### Test Organization

| Category | Location | Framework | Markers |
|----------|----------|-----------|---------|
| Unit | `tests/test_affine_control/`, `tests/test_core/`, `tests/test_tangent_models/` | pytest | `@pytest.mark.unit` |
| Integration | `tests/test_integration/` | pytest | `@pytest.mark.integration` |
| Content/Structure | `tests/test_content/` | pytest | `@pytest.mark.content` |
| Specialized (DbC, RL benchmarks) | `tests/test_specialized/` | pytest | `@pytest.mark.specialized` |
| JavaScript/Bibliography | `tests/` | Jest | N/A |
| End-to-End | `tests/e2e/` | Playwright (Chromium) | N/A |

### Coverage Requirements

| Scope | Minimum | Current | Enforced By |
|-------|---------|---------|-------------|
| Overall src/ | 50% | ~50% | CI (`--cov-fail-under=50`) |
| affine_control/ | 70% | ~70% | CI |
| core/ | 70% | ~70% | CI |
| tools/ | 60% | ~60% | CI |

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
- [x] Property-based tests with Hypothesis verify DDP convergence across parameter ranges
- [x] Design-by-contract assertions enforce preconditions and postconditions

## 8. Quality Standards

### Code Quality Tools

| Tool | Version | Purpose | Blocking? |
|------|---------|---------|-----------|
| ruff | Latest | Linting (multiple rules) | Yes |
| black | Latest | Code formatting (100-char lines) | Yes |
| mypy | Latest | Static type checking | Yes |
| pytest | Latest | Testing framework | Yes |
| pytest-cov | Latest | Coverage measurement | Yes |
| Hypothesis | Latest | Property-based testing | No (optional depth) |
| Jest | Latest | JavaScript testing | Yes |
| Playwright | Latest | E2E testing (Chromium) | Yes |

### Design Principles

- **TDD (Test-Driven Development)**: Enforced for new features; PR must include tests before implementation merges
- **Design by Contract (DbC)**: Preconditions and postconditions on core optimization functions; enforced with assertions and Pydantic models
- **DRY (Don't Repeat Yourself)**: CSS mirror validation ensures stylesheets are not duplicated; AST analysis flags code duplication
- **Orthogonality**: Modules are decoupled; affine_control, core, and tangent_models have minimal coupling; tools are independent

### CI/CD Pipeline

| Workflow | Trigger | Purpose | Blocking? |
|----------|---------|---------|-----------|
| `ci-standard.yml` | Push/PR to main | Lint, type-check, dependency audit, site render, E2E smoke tests, coverage | Yes |
| `deploy-website.yml` | Merge to main | Build Quarto site, deploy to GitHub Pages | Yes |
| `test-coverage.yml` | Push/PR | Report coverage metrics | Yes (50% minimum) |
| `link-check.yml` | Push/PR | Validate all links in content | Yes |
| `css-budget.yml` | Push/PR | Enforce CSS file size limits | Yes |
| `module-size-budget.yml` | Push/PR | Enforce Python module complexity | Yes |
| `dry-tracker.yml` | Nightly | Identify code duplication patterns | No (informational) |
| `Jules automation agents` | Various | Automated code review, refactoring suggestions | No (informational) |

## 9. Dependencies

### Runtime Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| numpy | Latest | Numerical computations for trajectory optimization |
| scipy | Latest | Scientific algorithms (optimization, linear algebra) |
| matplotlib | Latest | Plotting and visualization of swing trajectories |
| pydantic | Latest | Data validation and runtime type checking |
| PyYAML | Latest | YAML configuration file parsing |
| beautifulsoup4 | Latest | HTML parsing for link checking and site analysis |
| requests | Latest | HTTP requests for external data fetching |
| streamlit | Latest | Interactive dashboard for visualization (optional) |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | Latest | Testing framework |
| pytest-cov | Latest | Coverage reporting |
| hypothesis | Latest | Property-based testing library |
| ruff | Latest | Linting and code quality |
| black | Latest | Code formatting (100-char lines) |
| mypy | Latest | Type checking |
| jest | Latest | JavaScript testing framework |
| playwright | Latest | Browser automation for E2E tests |

### Fleet Dependencies

| Repo | Relationship | Description |
|------|-------------|-------------|
| QuatEngine | Referenced in non-goals | Game engine; AffineDrift does not depend on it |
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
npm install

# Running tests
pytest tests/ --cov=src --cov-fail-under=50
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

| Artifact | Format | Destination |
|----------|--------|-------------|
| Static Website | HTML + CSS + JS | GitHub Pages (AffineDrift.com) |
| Test Reports | JSON + HTML | GitHub Actions artifacts and CI logs |
| Coverage Reports | LCOV + HTML | CI artifacts (coverage.xml) |
| Quarto Book | PDF + HTML | GitHub Pages and releases |
| Optimization Results | JSON | File system or cloud storage (user-defined) |

## 11. Roadmap & Open Issues

### Current Phase

**Active Development & Maintenance**: AffineDrift is a mature research platform with core functionality complete (v1.0.0). Current focus is on expanding educational content, maintaining test coverage above 50%, and refining the optimization algorithms based on real-world validation data. The project serves as both a research artifact and an educational resource.

### Planned Work

| Priority | Item | Target Date |
|----------|------|-------------|
| P0 | Maintain test coverage >50% across all PRs | Ongoing |
| P1 | Publish research paper on affine swing modeling | Q2 2026 |
| P1 | Expand tangent space examples and tutorials | Q2 2026 |
| P2 | Optimize iLQR solver performance for real-time feedback | Q3 2026 |
| P2 | Add interactive swing trajectory editor to website | Q3 2026 |
| P3 | Support additional swing types (left-handed, alternative stances) | Q4 2026 |

### Known Limitations

- **Real-time Performance**: Current optimizers are designed for batch analysis, not real-time control (handled by UpstreamDrift)
- **Physical Accuracy**: Models assume rigid-body dynamics; soft-tissue deformation not modeled
- **Browser Support**: Progressive Web App features require modern browsers (ES6+, Service Worker API)
- **Content Rendering**: Complex 3D visualizations limited to JavaScript WebGL (no headless rendering)
- **Optimization Convergence**: DDP solver may not converge for highly nonlinear swing models; iLQR is more robust but slower

## 12. Change Log

| Date | Version | Changes |
|------|---------|---------|
| 2026-03-30 | 1.0.2 | Added caveat phrasing and improved humble language for uncited numerical claims in ch02, ch03, ch04, ch07, ch10, ch11, ch13, ch18, ch19, ch20, ch21, ch23, ch25, ch26, ch29, ch31, and glossary of The Physics of Golf (content audit wave 2; issues #2007--#2011) |
| 2026-03-30 | 1.0.1 | Added citation markers, TODO notes, and humble phrasing for unsourced claims in chapters 1--13 of The Physics of Golf (issues #1868--#1880, batch 1) |
| 2026-03-30 | 1.0.0 | Documented PR CI dependency-audit plus rendered-site E2E gate, mock-solver opt-in behavior at `SwingOptimizer.optimize`, and bibliography duplicate-alias integrity guardrails |
| 2026-03-28 | 1.0.0 | Initial SPEC.md specification for AffineDrift v1.0.0 — all core features documented and implemented |

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

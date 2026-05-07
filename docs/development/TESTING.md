# D-sorganization Fleet Testing Strategy

This document outlines the testing methodologies, requirements, and best practices across the D-sorganization fleet of repositories, fulfilling Epic 3061 (TEST-007).

## 1. Core Principles
- **Shift-Left Testing**: All PRs must pass unit tests before merging.
- **Contract-Based Validation**: External interfaces (especially simulation boundaries) are verified using contract tests.
- **Flakiness Intolerance**: Flaky tests are quarantined, investigated, and stabilized immediately (TEST-006).

## 2. Test Types & Coverage
- **Unit Tests**: Minimum 85% coverage target for all core Python and Rust modules.
- **Integration Tests**: Ensure sub-systems (e.g., Runner_Dashboard to Agent) communicate properly.
- **Performance Benchmarks**: Handled via `pytest-benchmark` on specialized runners (TEST-002).
- **Platform-Specific Validation**: Tests execute on Linux, Windows, iOS, and Jetson architectures (TEST-001).

## 3. Tooling
- **Python**: `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-benchmark`.
- **Rust**: Built-in `cargo test`.
- **JavaScript/TypeScript**: `Jest` and `Playwright`.

## 4. CI/CD Integration
Automated testing is enforced on all branches via GitHub Actions. A `TESTING.md` compliance check runs on all PRs involving significant architectural changes.

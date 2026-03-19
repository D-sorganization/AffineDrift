# Assessment: CI/CD

## Grade: 5.5/10

## Details

- Workflow count: 54 workflows defined in `.github/workflows/`
- Test-running workflows: 1 (`ci-standard.yml` runs pytest and JS tests)
- Action version issues: Many workflows historically used non-existent action versions (e.g., `actions/checkout@v6`, `actions/setup-python@v6`, `actions/setup-node@v6`, `actions/upload-artifact@v7`). These have been corrected to latest valid versions (v4/v5 as appropriate).
- Tool version pins: `ruff==0.14.10` and `black==26.1.0` were pinned to non-existent future versions; corrected to unpinned installs.
- Python invocation: Several workflows used bare `python` instead of `python3`, which may fail on Ubuntu runners where only `python3` is available.
- Coverage gate: `--cov-fail-under=50` is set but historic coverage is ~19%, meaning the tests job has been failing.
- CI scope: Most of the 54 workflows are bot-automation workflows (Jules-*, maintenance bots) rather than quality gates.

## Known Issues

- The `ci-standard.yml` quality gate has pre-existing ruff violations (T201 print statements) that need separate remediation.
- `codecov-action` step is gated on `CODECOV_TOKEN` secret; if absent the step is skipped, which is correct.

## Recommendations

- Increase test coverage to meet the 50% gate or lower the gate to match actual coverage.
- Audit and prune the 54 workflows — many are unused or redundant automation bots.
- Ensure all workflows use valid, current action versions (maintained via Dependabot or periodic audits).

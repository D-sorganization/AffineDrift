# Issue Candidates - 2026-04-11

Repository: `AffineDrift-textbook-review`  

These issue candidates were generated locally because GitHub issue creation is blocked by credentials/access in this environment.

### Split oversized functions by responsibility

- Severity: medium
- Problem statement: One or more Python functions exceed 40 LOC.
- Evidence: current assessment metrics for `AffineDrift-textbook-review`; see large function/module tables and CI/test inventory above.
- Impact: Large functions weaken SRP, reviewability, and targeted TDD.
- Proposed fix: Extract pure helpers and add tests around extracted behavior.
- Acceptance criteria: No priority function remains above 40 LOC without documented justification.
- Expectations: preserve TDD, DRY, Design by Contract, Law of Demeter, small functions, SRP, and bounded module size.

### Decompose monolithic modules and scripts

- Severity: medium
- Problem statement: One or more modules exceed 300 LOC.
- Evidence: current assessment metrics for `AffineDrift-textbook-review`; see large function/module tables and CI/test inventory above.
- Impact: Long modules concentrate unrelated responsibilities and increase maintenance risk.
- Proposed fix: Move orchestration, I/O, and domain logic into focused modules.
- Acceptance criteria: Top oversized modules have clear boundaries and regression tests.
- Expectations: preserve TDD, DRY, Design by Contract, Law of Demeter, small functions, SRP, and bounded module size.


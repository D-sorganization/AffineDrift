# Qualitative Code Quality Assessment Template (Clean Code + Pragmatic Programmer)

## Purpose
Use this template to run a qualitative engineering assessment focused on maintainability and correctness discipline.

- In scope: coding standards, architecture quality, test discipline, modularity, coupling, documentation quality, change safety.
- Out of scope: performance and security hardening (assessed separately).

## Scoring Rubric (1-5)
- 5: Exemplary. Consistent and automated; very low friction to change.
- 4: Strong. Mostly consistent with minor gaps.
- 3: Adequate. Mixed quality; important gaps exist.
- 2: Weak. Frequent anti-patterns; change risk is high.
- 1: Critical. Systemic quality debt; unsafe to evolve quickly.

## Assessment Criteria

### 1) TDD (Test-Driven Discipline)
What good looks like:
- Unit tests define behavior at module boundaries.
- Regressions are encoded as tests before fixes.
- Critical workflows have stable integration tests.

Red flags:
- Large untested modules.
- E2E-only testing without unit coverage.
- Frequent bugfixes without regression tests.

Actionable checks:
- Coverage by critical module, not just global total.
- Test pyramid health: unit > integration > e2e volume.
- Flakiness tracking and retry budget.

### 2) DbC (Design by Contract)
What good looks like:
- Explicit preconditions, postconditions, invariants at public interfaces.
- Input validation centralized at boundaries.
- Contract violations fail fast and clearly.

Red flags:
- Implicit assumptions in comments only.
- Late failures deep in call chain.
- Multiple ad-hoc validation styles.

Actionable checks:
- Contract modules or typed schema enforcement at API/UI/tool boundaries.
- Error messages tied to violated rule.
- Test cases for invalid inputs and boundary conditions.

### 3) Law of Demeter (LoD)
What good looks like:
- Callers talk to direct collaborators, not deep object chains.
- Data transfer objects flatten deep navigation needs.

Red flags:
- Frequent `a.b.c.d` traversal in business logic.
- UI layers reaching through service internals.

Actionable checks:
- Introduce façade methods where deep traversal repeats.
- Move navigation logic closer to owning object.

### 4) DRY
What good looks like:
- Repeated rules live in one canonical module.
- UI and API behavior shared through common helpers.

Red flags:
- Copy-paste calculators/handlers with slight drift.
- Mirrored assets without synchronization controls.

Actionable checks:
- Create shared kernels/libraries for repeated domain logic.
- Add sync/check scripts or eliminate mirrored sources.

### 5) Orthogonality
What good looks like:
- Features can change independently with minimal side effects.
- Clear ownership boundaries between modules.

Red flags:
- One change requires edits across unrelated areas.
- Feature flags/config leak across layers.

Actionable checks:
- Dependency-direction map by package.
- Cross-module edit frequency from git history.

### 6) Reversibility
What good looks like:
- Changes are easy to rollback or reconfigure.
- Risky refactors are isolated and staged.

Red flags:
- Giant mixed-purpose commits.
- Hard-cut migrations without compatibility windows.

Actionable checks:
- Branch by abstraction for large rewrites.
- Migration playbooks with clear rollback points.

### 7) Reusability
What good looks like:
- Stable reusable components with narrow interfaces.
- Low friction to compose existing modules.

Red flags:
- Reimplementation across products/repos.
- Shared modules tied to app-specific assumptions.

Actionable checks:
- Publish internal shared contracts/helpers.
- Separate reusable core from UI/runtime wrappers.

### 8) Changeability
What good looks like:
- Typical feature changes touch few files.
- New behavior added mostly through extension points.

Red flags:
- High blast radius per small requirement.
- Monolith files mixing orchestration, business logic, I/O.

Actionable checks:
- Cap file/module size for core layers.
- Extract orchestration from domain calculations.

### 9) Decoupling
What good looks like:
- Ports/adapters isolate framework/tooling specifics.
- Domain layer independent from transport/UI concerns.

Red flags:
- Domain logic directly importing GUI/network/runtime modules.
- Circular dependencies between core packages.

Actionable checks:
- Enforce layering in import-lint checks.
- Introduce anti-corruption layers around legacy components.

### 10) Comment Quality
What good looks like:
- Comments explain why, constraints, and non-obvious tradeoffs.
- Minimal restatement of obvious code.

Red flags:
- Stale comments contradicting behavior.
- Placeholder comments (`TRACKED_TASK/TRACKED_DEFECT`) as long-term policy.

Actionable checks:
- Replace low-value comments with clearer naming and extracted functions.
- Add doc comments for contracts, assumptions, units, and edge cases.

### 11) Documentation Quality
What good looks like:
- Docs map directly to current architecture and workflows.
- Onboarding and contribution flows are reproducible.

Red flags:
- Numerous archived docs with no canonical current source.
- No decision history for architectural tradeoffs.

Actionable checks:
- Define canonical docs and archive policy.
- Add ADRs for major architecture decisions.

### 12) Architecture Quality (qualitative)
What good looks like:
- Bounded contexts are clear and enforceable.
- Dependency direction is explicit and testable.
- Runtime composition is simple and observable.

Red flags:
- God modules crossing many contexts.
- Multiple architecture styles mixed without boundaries.

Actionable checks:
- Domain map and ownership map.
- Dependency rules: `domain -> application -> adapters`, never reverse.
- Architecture fitness tests in CI.

## Additional Common Quality Measures
- Naming & intention-revealing code.
- Error model consistency (typed/domain-specific errors).
- CI quality gates relevance (fast, deterministic, trusted).
- Build and tooling reproducibility.
- Code review quality signals (small PRs, clear rationale, linked tests).

## Reporting Format
For each repo, include:
1. Scorecard table (all criteria, 1-5).
2. Evidence summary (objective signals + file examples).
3. Top 10 prioritized actions (short, testable, owner-friendly).
4. 30/60/90 day quality roadmap.
5. Suggested CI quality gates to enforce improvements.

## Clean Code + Pragmatic Programmer Action Patterns
- Prefer small functions/classes with single responsibility.
- Make illegal states unrepresentable where possible.
- Program to interfaces; isolate side effects.
- Replace shotgun surgery with cohesive modules.
- Keep knowledge in one place (true DRY).
- Use tracer bullets/spikes for uncertain design, then harden.
- Treat warnings/debt markers as inventory with explicit budget.
- Leave code better than found (boy scout rule).

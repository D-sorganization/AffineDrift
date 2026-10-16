# F-AD-012

**Toolchain versions disagree across requirements.txt, CI and pre-commit**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| 🟨 Medium | governance | high | S | proposed |

**Locations:** `requirements.txt:30`, `requirements.txt:31`, `requirements.txt:32`, `.github/workflows/ci-standard.yml:128`, `.pre-commit-config.yaml:31`, `.pre-commit-config.yaml:42`

## Finding

- Severity: Medium  - Category: governance
- Confidence: high
- Location: requirements.txt:30-32, 38; .github/workflows/ci-standard.yml:95, 128; .pre-commit-config.yaml:31, 42, 145, 180
- Evidence: ruff 0.17.0 / 0.15.6 / 0.15.7; black 26.10.0 / 26.3.1 / 26.3.1; mypy 2.4.0 / 1.19.1 / 1.13.0;
  bandit 1.9.4 / 1.7.7 / 1.7.7. pydantic 2.14.0 (requirements) vs 2.13.3 (CI static lane), numpy 2.5.3 vs 2.4.4.
- Failure scenario: `black --check` passes locally and fails in CI (or the hook), and the fix is "run the other
  black"; mypy 2.x vs 1.x differ in strictness, so the hook and CI disagree on the same diff.
- Why a newer engineer misses this: four files, four authors, no single source. `.nvmrc`/`.quarto-version`/
  `.python-version` *are* single-sourced (Dockerfile:17-22 even enforces it) — do the same for linters.
- Proposed change: `requirements-dev.txt` pinned once; CI and pre-commit (`additional_dependencies`/`rev` kept in
  sync by `scripts/check_tool_pins.py`).
- Verification: the new check script in `static-checks`.
- Effort: S

## Draft Pull Request

**Title:** `chore(tooling): single-source linter pins across CI and pre-commit`

### Why This Matters (The Pitch)

Four files pin four sets of tool versions. The finding lists ruff at 0.17.0, 0.15.6 and 0.15.7, black at 26.10.0 versus 26.3.1, mypy at 2.4.0, 1.19.1 and 1.13.0, bandit at 1.9.4 versus 1.7.7, plus pydantic and numpy mismatches between requirements and the CI static lane. The result is a diff that passes locally and fails in CI, or a hook and CI that disagree on mypy strictness, and the usual fix is "run the other black". That is wasted contributor time on every PR and a bad look for a repository that claims reproducibility. The repo already single-sources `.nvmrc`, `.quarto-version` and `.python-version`, and the Dockerfile enforces them; linters should follow. One pinned `requirements-dev.txt`, with a `scripts/check_tool_pins.py` check keeping pre-commit and CI in sync, ends the argument.

### Proposed PR Body

## Problem
Versions disagree across `requirements.txt:30-32, 38`, `.github/workflows/ci-standard.yml:95, 128` and `.pre-commit-config.yaml:31, 42, 145, 180` (ruff 0.17.0 / 0.15.6 / 0.15.7; black 26.10.0 / 26.3.1; mypy 2.4.0 / 1.19.1 / 1.13.0; bandit 1.9.4 / 1.7.7; pydantic 2.14.0 vs 2.13.3; numpy 2.5.3 vs 2.4.4).

## Change
- [ ] Add a pinned `requirements-dev.txt`
- [ ] Point CI and pre-commit (`additional_dependencies`/`rev`) at the same pins
- [ ] Add `scripts/check_tool_pins.py` and run it in `static-checks`

## Verification
The new check script passes in `static-checks` and fails when a pin is changed in only one place.

## Risk and Rollback
Aligning to one version may surface new lint or type findings; pin to the version currently passing, or fix findings in the same PR. Revert to roll back.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** none

Refs: adversarial review 2026-10-16, F-AD-012


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._

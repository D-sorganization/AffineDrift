# F-AD-016

**Module-size budget is 750 lines vs documented 400; two explicit limits name nonexistent files**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| 🟨 Medium | governance | high | S | proposed |

**Locations:** `config/module_size_budget.json:5`, `config/module_size_budget.json:10`, `config/module_size_budget.json:11`, `AGENTS.md:173`, `AGENTS.md:381`

## Finding

- Severity: Medium  - Category: governance
- Confidence: high
- Location: config/module_size_budget.json:5-13; AGENTS.md:173, 381; src/affine_control/swing_optimizer.py:1; src/affine_control/programming_companion/catalog_generator.py:1; src/golf_simulation/round_simulator.py:1; src/tools/wrist_universal_joint/qt_ui_sections.py:1
- Evidence:
  ```json
  "max_lines_by_extension": {".py": 750, ...},
  "explicit_limits": {"src/js/bibliography.js": 500, "src/core/contracts.py": 450, ...}
  ```
  `src/js/` and `src/core/contracts.py` do not exist (`contracts` is a package). Four .py files (586, 576, 596,
  648 lines) exceed the documented 400; none exceeds 750, so the gate has never fired on a Python file.
- Failure scenario: the rule agents read (400) and the rule CI enforces (750) differ by ~2×; every agent that
  "splits a 450-line file to satisfy the budget" is doing work the gate never asked for, and files grow to 749.
- Proposed change: set `.py: 400` with an explicit, dated allow-list for the four current offenders; delete the
  two stale entries; add a test that every `explicit_limits` key exists.
- Verification: `python3 scripts/check_module_size_budget.py` fails on the stale keys until fixed.
- Effort: S

## Draft Pull Request

**Title:** `fix(governance): set .py module budget to 400 and remove stale limits`

### Why This Matters (The Pitch)

The rule agents read says 400 lines per module; the rule CI enforces is 750. The largest Python file is 648 lines, so the gate has never fired on a Python file. Two explicit limits point at paths that do not exist (`src/js/bibliography.js`, `src/core/contracts.py`). Agents that split a 450-line file to satisfy the budget are doing work the gate never asked for, and files drift up toward 749. Set `.py` to 400 with a dated allow-list for the four current offenders (586, 576, 596 and 648 lines), delete the stale keys, and add a test that every explicit-limit key exists. Documentation and enforcement finally say the same thing, and the budget starts doing the job the docs already claim it does.

### Proposed PR Body

## Problem
`config/module_size_budget.json:5-13` sets `.py: 750` against the documented 400 (`AGENTS.md:173, 381`); `explicit_limits` references `src/js/bibliography.js` and `src/core/contracts.py`, which do not exist. Four files exceed 400: `src/affine_control/swing_optimizer.py`, `src/affine_control/programming_companion/catalog_generator.py`, `src/golf_simulation/round_simulator.py`, `src/tools/wrist_universal_joint/qt_ui_sections.py`.

## Change
- [ ] Set `.py` to 400 with a dated allow-list for the four current offenders
- [ ] Delete the two stale `explicit_limits` entries
- [ ] Add a test that every `explicit_limits` key exists

## Verification
`python3 scripts/check_module_size_budget.py` fails on the stale keys until fixed, then passes with the allow-list.

## Risk and Rollback
Config-only; revert to roll back.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** none

Refs: adversarial review 2026-10-16, F-AD-016


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._

# Mechanical Baseline — AffineDrift (2026-10-16)

Every tracked Python file was scanned. This page is evidence for the review, not a finding list; the reviewer
decided which of these matter and wrote those up as findings.

## The Repo's Own Ruff Check

Command: `ruff check .`

```
(clean)
```

## Isolated Adversarial Ruff Rules

Rules the repo does not enable; counts over `src` and `scripts`.

| count | rule |
|---|---|
| 1133 | `TRY003` [ ] raise-vanilla-args |
| 173 | `T201` [ ] print |
| 108 | `N806` [ ] non-lowercase-variable-in-function |
| 66 | `PERF401` [ ] manual-list-comprehension |
| 56 | `PLR0917` [ ] too-many-positional-arguments |
| 46 | `RUF001` [ ] ambiguous-unicode-character-string |
| 40 | `PTH123` [ ] builtin-open |
| 39 | `N803` [ ] invalid-argument-name |
| 33 | `TRY400` [ ] error-instead-of-exception |
| 30 | `S603` [ ] subprocess-without-shell-equals-true |
| 26 | `C901` [ ] complex-structure |
| 23 | `PLC0415` [ ] import-outside-top-level |
| 18 | `S607` [ ] start-process-with-partial-path |
| 18 | `TRY300` [ ] try-consider-else |
| 18 | `RUF100` [*] unused-noqa |
| 15 | `PTH118` [ ] os-path-join |
| 15 | `PERF203` [ ] try-except-in-loop |
| 14 | `BLE001` [ ] blind-except |
| 14 | `PLR0912` [ ] too-many-branches |
| 14 | `TRY004` [ ] type-check-without-type-error |
| 13 | `ARG001` [ ] unused-function-argument |
| 11 | `N802` [ ] invalid-function-name |
| 11 | `PTH201` [*] path-constructor-current-directory |
| 10 | `PLW2901` [ ] redefined-loop-name |
| 9 | `ARG002` [ ] unused-method-argument |

## Structure From the AST

- functions: 9,940; files > 800 lines: 2; functions > 80 lines: 40; functions > 6 params: 41
- largest files:
  - 1147 lines `tests/test_automerge_guard.py`
  - 808 lines `scripts/automerge_guard.py`
- longest functions:
  - 235 lines `src/affine_control/programming_companion/tools_catalog.py:27` `render_tools_qmd`
  - 174 lines `shared_scripts/deferred_validation.py:188` `_validate_record_shape`
  - 159 lines `scripts/core_theory_figures/superposition.py:25` `build_superposition_decomposition`
  - 147 lines `shared_scripts/handoff_validator.py:230` `validate_handoff_content`
  - 140 lines `tests/test_proximal_distal_complete_claim_audit.py:21` `test_complete_claim_audit_snapshot_is_exact_and_fail_closed`
  - 135 lines `src/affine_control/research_readiness/fixtures.py:189` `_protocol`
  - 134 lines `tests/test_proximal_distal_complete_claim_audit.py:163` `test_articulated_tier_blocks_are_exact_and_retain_their_boundaries`
  - 132 lines `scripts/core_theory_figures/ztcf.py:25` `build_ztcf_trajectory_divergence`
  - 129 lines `src/affine_control/research_readiness/fixtures.py:58` `_specification`
  - 125 lines `scripts/generate_claim_critique_ledger.py:111` `validate_ledger`
  - 121 lines `shared_scripts/development_log_validator.py:66` `_validate_entry`
  - 120 lines `shared_scripts/development_log_validator.py:189` `validate_devlog_content`
  - 119 lines `src/affine_control/research_readiness/template.py:11` `concept_template`
  - 117 lines `shared_scripts/deferred_validation.py:448` `validate_catalog`
  - 112 lines `src/tools/wrist_universal_joint/qt_ui_sections.py:447` `_build_plot_controls_group`

## Test-Suite Texture

Greps over `tests/` and `src/`.

- `pytest.skip` / `@pytest.mark.skip` sites: 43
- `MagicMock` / `patch(` sites: 162
- literal `assert True` / `assert 1` lines: 24
  - `tests/test_counterfactual_chapter.py:179`
  - `tests/test_orbital_stability_rigor.py:107`
  - `tests/test_timing_review.py:49`
  - `tests/test_trajectory_optimization_rigor.py:130`
  - `tests/test_flexible_shaft_rigor.py:53`
  - `tests/test_contraction_workspace_rigor.py:89`
  - `tests/test_muscle_force_rigor.py:49`
  - `tests/test_muscle_force_rigor.py:124`
  - `tests/test_muscle_force_rigor.py:127`
  - `tests/test_muscle_force_rigor.py:128`

## Bandit Findings at Medium and High Severity

| sev | id | text | n |
|---|---|---|---|
| — | — | nothing at MEDIUM/HIGH | — |

## Dangerous-Pattern Greps

Over `src` and `scripts`; many `exec(` hits are Qt `dialog.exec()` — the reviewer triaged these.

- `eval(`: 8
- `exec(`: 4
- `shell=True`: 2
- `verify=False`: 2
- `os.system(`: 2
- `md5`: 1
- `pickle.load`: 1

## Radon: Functions at Cyclomatic Complexity D, E or F

Count at or above 21: 0


## Vulture Dead-Code Hits

At 80 % confidence or higher: 1 hits

- `src/tools/wrist_universal_joint/qt_widgets.py:33: unused variable 'watched' (100% confidence)`

# Review Rules: AffineDrift

Repo-specific rules for anyone reviewing an AffineDrift pull request. The
author checks them first with the `fleet-review` skill. A breach is a finding
only when it's cited here or in `AGENTS.md` / `CLAUDE.md`, by file and section.

## Scope and Size

- Under 500 changed lines after formatters, targeting `main`, never stacked.
- No new file over 400 lines; over 800 is a critical violation. CI enforces
  the budgets with `scripts/check_module_size_budget.py` and
  `scripts/check_changed_file_size_budget.py` (AGENTS.md, 5d).
- No function over 50 lines or with more than 4 parameters, and no function
  with more than two responsibilities (AGENTS.md, 5g and 5i).

## Quarto Content

- Content is `.qmd`. A new chapter has an entry in `_quarto.yml`.
- Citations use `[@key]` with entries under `references/`. Images have alt
  text.
- Complex Python lives in importable modules under `src/`; a cell imports and
  calls one function (AGENTS.md, 7b).
- Prose and code examples are not copied between chapters; shared material
  becomes an include or a utility under `src/tools/utils/` (AGENTS.md, 7d).
- Titles and headings use title case (`scripts/check_title_case.py`).

## Styles

- CSS is edited only in `css/`, never in the rendered `_site/` copy, and stays
  within `scripts/check_styles_budget.py`.
- Math on mobile scrolls horizontally; no fixed font sizes that break the
  layout.

## Evidence

- New behaviour needs a test that fails on `main` (TDD): pytest for Python
  utilities, Jest for interactive features. Coverage stays at or above the
  `fail_under` floor in `pyproject.toml`.
- Python is formatted with Black at 100 characters, not `ruff format`.
- No `print()` in `src/`; use logging. No TODO or FIXME without a tracked
  issue.
- Loosening a tolerance, budget or coverage floor needs a
  `Tolerance-Change-Evidence: #N — <numbers>` commit trailer.

## Shared Files

- A substantive PR adds exactly one SPEC.md section 12 row keyed by its PR or
  issue (`scripts/check_spec_changelog.py`), or a change fragment under
  `changes/`. The `Spec Version` field is never bumped by hand.
- A new root file is added to `scripts/check_root_hygiene.py`.
- Editing a file bound by a `data/trust/*.json` ledger regenerates the claim
  audit evidence (`python3 -m scripts.regenerate_claim_audit_evidence`) in the
  same PR.
- `AGENT_HANDOFF.md` is current-state only and is updated with each PR that
  changes what it describes (AGENTS.md, Agent Handoff & PR Policy).

## Merging

- PRs open ready, never as drafts.
- A PR that deletes files says `deletions-acknowledged: yes` on its own line
  in the body, or carries the `deletions-acknowledged` label. Otherwise the
  arm guard refuses it.
- PRs are armed only with `scripts/automerge_guard.py`, never with a
  merge-method flag, `--admin` or a ruleset change.
- Commits use a GitHub noreply email. No secrets, tokens or personal data.
- `Closes #N` sits on its own line. An issue closes only through a merged PR
  or an exempt label.

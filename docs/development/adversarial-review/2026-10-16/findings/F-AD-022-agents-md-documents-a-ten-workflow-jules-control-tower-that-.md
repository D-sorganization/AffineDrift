# F-AD-022

**AGENTS.md documents a ten-workflow Jules Control Tower that does not exist and links six missing files**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| 🟨 Medium | docs | high | S | proposed |

**Locations:** `AGENTS.md:488`, `AGENTS.md:511`, `AGENTS.md:522`, `AGENTS.md:976`, `CLAUDE.md:125`, `CLAUDE.md:129`

## Finding

- Severity: Medium  - Category: docs
- Confidence: high
- Location: AGENTS.md:488, 511, 522, 961, 976; CLAUDE.md:125, 129; src/affine_control/ddp.py:9; .github/workflows/README.md:39-40
- Evidence: `.github/workflows/` contains only `Jules-Redundant-Issue-Closer.yml` and `Jules-Redundant-PR-Closer.yml`.
  Missing: `JULES_ARCHITECTURE.md`, `docs/workflows/WORKFLOW_TRACKING.md`, `.logging-standard.md`,
  `.dry-improvements.md`, `scripts/pre_pr.py`, `scripts/dispatch_cli_agent.py`,
  `docs/assessments/issues/ISSUE_Completist_Critical_DDPMock_2026-01-30.md`.
- Failure scenario: every agent session starts by reading 44 KB of AGENTS.md; a third of it describes machinery
  that will never run, and the "Before pushing, run `python -m scripts.pre_pr`" instruction fails immediately,
  teaching agents to ignore instructions.
- Proposed change: delete §"System Architecture & Agent Roles" and the dangling references; add a test
  (`tests/test_agents_md_links.py`) that every backticked repo path in AGENTS.md/CLAUDE.md exists.
- Effort: S

## Draft Pull Request

**Title:** `docs(agents): remove nonexistent Jules workflows and dead references`

### Why This Matters (The Pitch)

Every agent session starts by reading 44 KB of AGENTS.md, and a third of it describes a ten-workflow control tower that does not exist; only two Jules closer workflows are present. Six referenced files are missing, and the instruction to run `python -m scripts.pre_pr` before pushing fails immediately, which teaches agents to ignore instructions. That is wasted context on every session and a documentation set that contradicts the repository, which a reviewer reading the supplement will also notice. Delete the "System Architecture & Agent Roles" section and the dangling links, then add a test that every backticked repo path in AGENTS.md and CLAUDE.md exists, so the document cannot rot silently again. Less to read, and instructions that work. New agents and new human contributors both stop learning to skim past the setup guidance.

### Proposed PR Body

## Problem
`AGENTS.md:488, 511, 522, 961, 976` and `CLAUDE.md:125, 129` describe a ten-workflow Jules Control Tower; `.github/workflows/` contains only `Jules-Redundant-Issue-Closer.yml` and `Jules-Redundant-PR-Closer.yml`. Missing: `JULES_ARCHITECTURE.md`, `docs/workflows/WORKFLOW_TRACKING.md`, `.logging-standard.md`, `.dry-improvements.md`, `scripts/pre_pr.py`, `scripts/dispatch_cli_agent.py`, and `docs/assessments/issues/ISSUE_Completist_Critical_DDPMock_2026-01-30.md` (also referenced at `src/affine_control/ddp.py:9` and `.github/workflows/README.md:39-40`).

## Change
- [ ] Delete AGENTS.md section "System Architecture & Agent Roles" and the dangling references
- [ ] Fix `CLAUDE.md:125, 129` and `.github/workflows/README.md:39-40`
- [ ] Add `tests/test_agents_md_links.py` asserting every backticked repo path in AGENTS.md/CLAUDE.md exists

## Verification
`pytest tests/test_agents_md_links.py` passes.

## Risk and Rollback
Documentation-only; revert to roll back.

## Handoff

- **Branch, commit, and pull request:** `<branch>` @ `<commit>` — PR #<n> (fill in when opened)
- **Validation:** the command(s) under *Verification* above, run locally and green; plus the repo's fast gates
  (`ruff check`, `ruff format --check`, the relevant `-m unit` subset)
- **Blockers:** none known at drafting time — record any that appear
- **Next step:** open the PR against `main`, arm auto-merge with `scripts/automerge_guard.py`, end the session
- **Follow-ups:** none

Refs: adversarial review 2026-10-16, F-AD-022


---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53fa`. This is a proposal, not a verdict — verify the cited lines before acting._

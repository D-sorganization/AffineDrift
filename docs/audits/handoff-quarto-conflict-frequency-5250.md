# `AGENT_HANDOFF.md` & `_quarto.yml` Merge-Conflict Frequency (#5250)

## 1. 60-Day Main-Branch Touch Frequency (`2026-08-30` to `2026-10-29`)

| File / Overlap | Total Commits (60d) | Pre-RM5 Rollout (`2026-08-30..2026-10-05`) | Post-RM5 Rollout (`2026-10-05..2026-10-29`, after `#4918`) |
| --- | --- | --- | --- |
| `AGENT_HANDOFF.md` | `253` | `243` (`~6.8/day`) | `10` (`0.4/day`; only `3` since `2026-10-13`) |
| `_quarto.yml` | `34` | `24` (`~0.7/day`) | `10` (`0.4/day`; only `3` since `2026-10-15`) |
| Touched both in same commit | `6` | `4` | `2` (`#5005`, `#5107`) |

## 2. Superseded PRs and Conflict Incidents (Last 60 Days)

| Closed / Superseded PR(s) | Surviving PR(s) | Target Files Touched | Root Cause |
| --- | --- | --- | --- |
| #5105 | #5107, #5141 | `_quarto.yml`, `articles/after-one-solution-null-space-exploration.qmd`, `changes/5095-*.md` | Duplicate/stacked branch for #5096/#5097; #5107 merged the article with pinned UpstreamDrift SHAs and omitted premature `_quarto.yml` navbar entry; #5141 restored the #5095 fragment (`AGENT_HANDOFF.md` not touched by #5105). |
| #4683 | #4995 | `_quarto.yml` (`output-dir: _site`) | Superseded Quarto `output-dir` migration PR; replaced by #4995 after separating internal docs. |
| #4667, #4649, #4639, #4624 | #4698, #4704, #4740 | `_quarto.yml`, `AGENT_HANDOFF.md` | Wave 5/6 web PR batch consolidations (2026-09-30..2026-10-01) prior to RM-5 `changes/` fragment rollout (#4918). |
| #4689 (fix) | #4689 | `docs/development/HANDOFF.md` | Stray merge-conflict marker committed into `HANDOFF.md` prior to RM-5 fragment rollout (#4918) and `HANDOFF.md` archival (#4991/#5011). |

## 3. Recommendation: **NO-GO** on `.agent/state` JSON Split

- **Decision**: **NO-GO** on migrating `AGENT_HANDOFF.md` to `.agent/state/*.json`.
- **Evidence**:
  1. **RM-5 change fragments (`changes/<issue>-<slug>.md`, `#4918`) already solved per-PR handoff contention**: `AGENT_HANDOFF.md` commits dropped by **96%** (from `243` commits in the 36 days before `#4918` to `10` commits in the 24 days after, and only `3` commits in the last 17 days: `#5107`, `#5154`, `#5231`).
  2. **`#5105` vs `#5107`/`#5141` was not an `AGENT_HANDOFF.md` conflict**: `#5105` never modified `AGENT_HANDOFF.md`; it overlapped `#5107` on `articles/after-one-solution-null-space-exploration.qmd` and `_quarto.yml`, and `#5141` restored only the 4-line `changes/5095-*.md` fragment.
  3. **Root-hygiene and migration cost**: `.agent` is explicitly forbidden in `scripts/check_root_hygiene.py` (`FORBIDDEN_ROOT_DIRECTORIES`), and `_quarto.yml` navbar edits are already governed by owner-only control under epic `#5248`.

# Sanitation Report — 2026-09-28

Scheduled Sanitation Engineer pass on `D-sorganization/AffineDrift`.

## What Was Cleaned

| Item | Evidence | Action |
| --- | --- | --- |
| `origin/drive/e-content-fixes` | Tip `3b68512292a0` is an ancestor of `origin/main` (`git merge-base --is-ancestor`); its only associated PR, [#3618](https://github.com/D-sorganization/AffineDrift/pull/3618), is closed | Deleted the stale remote branch (`git push origin --delete drive/e-content-fixes`) |

## What Was Left Alone, and Why

- **589 remote branches remain.** Only one branch's tip was a direct ancestor of
  `main` under local git ancestry — most of the rest are either still open,
  unmerged, or were squash-merged (so their tip SHA no longer matches any commit
  on `main`, and `git merge-base --is-ancestor` cannot confirm them). Confirming
  squash-merge status for hundreds of branches requires a PR-state lookup per
  branch, which the fleet's GitHub API hygiene rules forbid doing in bulk
  (`gh pr list`/REST loops over the whole branch set). This needs a dedicated,
  rate-limited sweep — not a single sanitation pass — so it is being flagged
  here rather than attempted.
- **Six other worktrees under `staff-worktrees/`** (`pr-remediator`,
  `cartographer` ×2, `project-steward`, `issue-remediator`, plus this session's
  own) are live agent sessions on branches with recent activity; none were
  touched, per fleet-guard `foreign-worktree` and the operator's explicit
  instruction not to touch other worktrees.
- **`.jules/` and `.Jules/` working-data directories** (`pending/`,
  `processed/`, `*_data/`, `review_logs/`) are active state for the Jules
  content-review tooling (evidenced by non-empty `pending/pr_comments.json` and
  dated `processed/comments_20260426_013621.json`), not orphaned scratch files.
  Left untouched — sanitation is not the owning role for that tool's state.
- **`.benchmarks/`** (180 KB, 4 dated JSON runs) is small and within any
  reasonable retention window; not archived.
- **Working tree was clean** on checkout — no stray root-level logs, reports,
  or temp artifacts to archive this pass.

## Follow-Up

- The open-PR-less branch backlog (589 remote branches, the vast majority
  pre-dating 2026-06) is a standing structural-debt item. Recommend a
  dedicated multi-session sweep that batches PR-state lookups (one bulk
  GraphQL query rather than per-branch REST calls) instead of ad hoc
  sanitation passes, to stay inside fleet API quota rules.

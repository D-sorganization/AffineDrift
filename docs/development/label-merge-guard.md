# Label Merge Guard

Workflow: [`.github/workflows/label-merge-guard.yml`](../../.github/workflows/label-merge-guard.yml)

## Purpose

Fleet agents historically merged pull requests that still carried `do-not-merge`, and closed issues marked `do-not-automate`. This workflow adds repository-side enforcement that branch protection can require independently of `scripts/automerge_guard.py` (which only blocks arming auto-merge).

## Checks

| Job | When | Outcome |
| --- | --- | --- |
| **Block do-not-merge label** | `pull_request` (open/sync/label changes) targeting `main`, and `merge_group` | Fails while the PR has `do-not-merge` (case-insensitive). |
| **Reopen do-not-automate bot closes** | `issues` `closed` | If the issue still has `do-not-automate` and the closer is a bot, GitHub App agent (`d-sorg*agent`), or `[bot]` login, reopen and comment that a human must close it. |

## Local validation

```bash
python3 scripts/dry_run_label_merge_guard.py
python3 -m pytest tests/test_label_merge_guard_workflow.py -q
```

Optional live probe (requires `gh` auth):

```bash
python3 scripts/dry_run_label_merge_guard.py --live-pr D-sorganization/AffineDrift 1234
```

Exit code `2` means the PR is blocked by `do-not-merge`.

## Branch protection

After merge, add **Block do-not-merge label** (workflow *Label Merge Guard*) to the required checks for `main`. Humans remove `do-not-merge` only when the hold is cleared; the check then passes on the next run.

---
issue: 4947
summary: "Consolidate reviewed mechanics, control and historical corrections for main delivery"
dl_state: "in_progress"
next_step: "Run frozen combined regression and all relevant CI gates before opening the regular consolidation PR"
owner: "codex"
branch: "feat/technical-review-consolidated-20261005"
---

Consolidates this session's fourteen regular PRs #4902 through #4946 in dependency
order, plus historical-source corrections #4945. No other agent's PR, workflow
change or draft is included. Capacity measured 14/15 online runners busy (93%),
triggering the mandatory consolidation policy. Original PRs remain open until
actual protected main merge and canonical-file verification.

Turnover and evidence: docs/development/technical-review/consolidated-20261005/review-notes.md.
Original frozen batch acceptances remain historical evidence; combined acceptance
is pending. The 407-row corpus has 42 pending-prefix scopes, including fifteen
historical drafts awaiting this combined acceptance. This is not a scientific
completion percentage. No empirical human-swing validation is asserted.

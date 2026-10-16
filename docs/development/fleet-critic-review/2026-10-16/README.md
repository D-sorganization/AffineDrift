# Fleet Critic Review — AffineDrift (2026-10-16)

**Scope:** per the [Fleet Critic schedule](https://github.com/D-sorganization/Repository_Management/blob/main/docs/fleet-critic.md),
this pass reviews persistent documented claims added in the last 30 days that
had not yet gone through adversarial review. The 2026-10-16 mechanical
adversarial review (`docs/development/adversarial-review/2026-10-16/`,
PR #5074) covered the pre-existing `src/affine_control` kernel and the ZTCF/DCR
article family; it did not read `articles/forward_dynamics_matching/`, the
26-chapter research book recovered and merged the day before this pass
(PR #4948 / #5070, 2026-10-15). That book is this review's subject.

## Executive Read

The Forward Dynamics Matching book is unusually well hedged for a first draft:
nearly every chapter states its own non-identifiability results, labels
numbers as "diagnostic" or "unmeasured" where the source material says so, and
explicitly declines to repeat UpstreamDrift's "promoted" speedup claims
(ch. 3, ch. 26). That internal discipline is real and should not be
undersold.

The weakness is structural, not rhetorical: the book's central evidentiary
chapters (`02_upstream_inventory.qmd`, `03_historical_lessons.qmd`) assert
dozens of specific numeric results — RMS values, gate pass/fail outcomes, test
counts — attributed to a single pinned commit of a *different* repository
(UpstreamDrift). The only verification this repository performs against that
commit is **path existence**, not content. `link_validation.json` records
`"live_http_status": "pending_network_stop"` for every one of its 53 entries
and `"scope": "Local path validation only; HTTP and claim validation are
separate"`. The book's own recovery record
(`docs/development/forward-dynamics-matching/validation.md`) says the same
thing plainly: *"local existence is not HTTP or claim verification"* and
*"Live external links and primary-source metadata still require
validation."* That caveat lives in a development-process document a reader of
the published book will never see; the chapters themselves state the numbers
as fact.

See `weaknesses.md` for the itemized findings.

## Coverage Statement

Read in full: all 26 chapters' prose text plus `index.qmd`
(`articles/forward_dynamics_matching/*.qmd`, ~2,775 lines); `source_manifest.json`;
`link_validation.json`; `tests/test_forward_dynamics_matching_book.py`;
`tests/test_forward_dynamics_matching_frontmatter.py`; and the recovery
record at `docs/development/forward-dynamics-matching/` (`recovery.md`,
`validation.md`, `upstream-source-audit.md`, `recovery-receipt.json`).
Not independently re-verified: the cited UpstreamDrift commit
`d7c7d07add0d7407a5a3376d5fe4a97aee9112a0` itself (no network access taken in
this session; see Finding 1).

## Gate Audit

This review changes no source, config, or workflow files — documentation
only. `ruff check .` and `black --check --line-length 100 .` were not
re-run because nothing they lint was touched.

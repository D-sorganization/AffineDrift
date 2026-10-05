---
issue: 4952
summary: "Repair inherited development-log metadata and archive completed records without losing evidence"
dl_state: "in_review"
next_step: "Verify the consolidation pre-PR gate against the repaired generated development log"
owner: "codex"
branch: "feat/technical-review-consolidated-20261005"
---

The unchanged main development log blocked the central pre-PR gate. A scripted
maintenance pass uses git-blame provenance, the central field setter and archive
helper. It retains historical validation statements, explicitly distinguishes
metadata provenance from newly executed checks, fixes the issue4710/PR4712 key,
and preserves duplicate record text in the repair evidence. The vocabulary
change done-to-shipped is supported by the existing exact main-delivery receipt.

Terminal records older than seven days move intact to the annual archive after
the default thirty-day archive left the log above its 200000-byte limit. Active
states remain unchanged. The validator passes, retaining its advisory WIP warning.
This is generated metadata maintenance under #4952, not a new scientific review
or a claim to refresh every historical task. Evidence and transformation history:
docs/development/technical-review/consolidated-20261005/devlog-repair-evidence.json.

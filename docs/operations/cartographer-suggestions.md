# Cartographer Suggestion Log — AffineDrift

Improvement suggestions from the Silent Cartographer role. Logged here per
`docs/fleet-cartographer.md`; suggestions become GitHub issues only when
high priority, not fixable in one small PR, and cross-repo.

## Suggestion Log

### 2026-09-27 — AffineDrift — Missing `docs/codemap.md` and ungitignored `.codemap/`

**Current state**: The fleet-managed section of `AGENTS.md` ("Repo Context &
Codemap Freshness") told agents to check `docs/codemap.md` and to keep
`.codemap/` out of version control, but neither existed: there was no local
navigation guide and no `.codemap/` entry in `.gitignore`. The repo did
already have a real, CI-enforced architecture map at
`docs/architecture/C4.md` (`architecture-map-contract.yml`), so the gap was
navigation, not structure.

**Suggested improvement**: Added `docs/codemap.md` (points to `C4.md`, gives
a directory table, states the refresh mechanism) and added `.codemap/` to
`.gitignore`. Done in this pass's PR.

**Rationale**: Closes the "AGENTS.md references a file that doesn't exist"
gap so agents following the documented discovery path don't hit a dead end.

**Priority**: Medium

**Status**: Implemented

---

### 2026-09-27 — AffineDrift — No staleness signal for `docs/codemap.md` itself

**Current state**: `docs/architecture/C4.md` has a structural CI contract
(`architecture-map-contract.yml`) that fails a PR if the map's shape breaks,
but nothing checks whether `docs/codemap.md`'s directory table still matches
`CLAUDE.md`'s "Key Directories" list, or whether new top-level directories
have been added since the codemap was last touched.

**Suggested improvement**: A lightweight CI check (or a `codemap-refresh`
workflow per the fleet template) that diffs the top-level directory listing
against `docs/codemap.md`'s table and fails/warns on drift. This mirrors what
`architecture_map_contract.py` already does for `C4.md`, so it should reuse
that pattern rather than invent a new one.

**Rationale**: Prevents the same drift class this pass just fixed from
recurring silently; matches the freshness-runbook pattern used elsewhere in
the fleet.

**Priority**: Low

**Status**: Logged (not implemented this pass — small in isolation, but
best done alongside the shared `codemap-refresh-workflow.yml` template so
AffineDrift doesn't diverge from how other product repos wire it up).

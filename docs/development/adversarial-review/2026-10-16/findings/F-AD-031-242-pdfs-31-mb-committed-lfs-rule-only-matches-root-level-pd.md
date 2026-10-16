# F-AD-031

**242 PDFs (31 MB) committed; LFS rule only matches root-level PDFs**

| Severity | Category | Confidence | Effort | Status |
|---|---|---|---|---|
| ⬜ Low | hygiene | high | S | proposed |

**Locations:** `.gitattributes:33`

## Finding

- Severity: Low  - Category: hygiene
- Confidence: high
- Location: .gitattributes:33
- Evidence: `/*.pdf filter=lfs …` (leading slash → root only; there are none). 126 PDFs under one `figures/` dir.
  The trust ledgers pin `articles/**/main.pdf` digests (37 references), so each recompile forces a ledger regenerate.
- Proposed change: `*.pdf filter=lfs` or stop committing build outputs (publish via release assets / Pages);
  never make a PDF an `evidence_path`.
- Effort: S

## Draft Pull Request

**Title:** `chore(git): route all PDFs through LFS or stop committing build outputs`

### Why This Matters (The Pitch)

The LFS rule has a leading slash, so it matches only root-level PDFs and there are none. 242 PDFs, 31 MB, sit in git, and 37 ledger references to `main.pdf` force a regenerate on each recompile. Use `*.pdf filter=lfs` or publish via release assets, and never use a PDF as evidence.

### Proposed PR Body

## Problem
`.gitattributes:33` has `/*.pdf filter=lfs ...`, which matches root only; 242 PDFs (31 MB) are committed, 126 in one `figures/` directory, and the trust ledgers pin `articles/**/main.pdf` digests.

## Change
- [ ] Change the rule to `*.pdf filter=lfs`, or stop committing build outputs and publish via release assets or Pages
- [ ] Never make a PDF an `evidence_path`

## Verification
`git lfs ls-files` lists the PDFs, or `git ls-files '*.pdf'` is empty.

## Risk and Rollback
LFS migration rewrites history if done retroactively; do it forward-only unless agreed. Revert the attributes change to roll back.

## Handoff
Follow-ups: F-AD-005 and F-AD-009.

Refs: adversarial review 2026-10-16, F-AD-031

---
_Generated 2026-10-16 from an adversarial review of `AffineDrift` @ `498f53f`. This is a proposal, not a verdict — verify the cited lines before acting._

# GitHub Issue Templates — Technical Content Reference Audit (2026-04-06)

This file provides ready-to-create GitHub issue templates based on the findings in
`docs/development/technical_content_reference_audit_2026-04-06.md`.

## Usage

1. Open each issue draft below.
2. Create one GitHub issue per draft.
3. Assign an owner and milestone.
4. Link each issue back to the audit report.

---

## Issue 1 — Fix citation key mismatches in The Physics of Golf chapters

**Title**  
`docs(citations): normalize mismatched citation keys in Physics of Golf chapters`

**Body**

### Problem
Several citation keys in The Physics of Golf chapters do not resolve to any bibliography entry, likely due to key-name drift.

### Affected files
- `articles/The_Physics_of_Golf/quarto/ch11_flexible_shaft.qmd`
- `articles/The_Physics_of_Golf/quarto/ch14_complete_swing.qmd`

### Unresolved keys
- `nesbit2005work` (appears multiple times)
- `mackenzie2009parametric` (appears multiple times)

### Required work
- Confirm intended sources.
- Replace unresolved keys with canonical existing keys where appropriate.
- If intended papers are different, add proper BibTeX entries instead of reusing near-match keys.

### Acceptance criteria
- No unresolved keys remain in the affected files.
- Quarto render shows no unresolved citation warnings for these chapters.
- Added/updated references include DOI or URL metadata.

---

## Issue 2 — Add missing contraction/control bibliography entries

**Title**  
`docs(citations): add missing contraction and optimization references`

**Body**

### Problem
Core method chapters cite keys that are not present in any repository bibliography.

### Affected files
- `articles/tangent-hyperplane-contraction/textbook-main.qmd`
- `articles/tangent-hyperplane-contraction/chapters/06-computation-and-certification.qmd`

### Missing keys
- `forni2014contraction`
- `boyd1994`

### Required work
- Add BibTeX entries for missing keys in the appropriate bibliography files.
- Ensure entries include author, title, venue, year, and DOI/URL when available.

### Acceptance criteria
- All listed keys resolve during Quarto render.
- No placeholder or partial bibliography entries are introduced.

---

## Issue 3 — Add missing spine and neuro references

**Title**  
`docs(citations): add missing spine-modeling and motor-control references`

**Body**

### Problem
Two citations in technical chapters are unresolved, breaking provenance for biomechanical/neuroscience claims.

### Affected files
- `articles/The_Physics_of_Golf/quarto/ch21_spine_modeling.qmd`
- `articles/The_Physics_of_Golf/quarto/ch24_motor_control_brain.qmd`

### Missing keys
- `white1990clinical`
- `azevedo2009equal`

### Required work
- Add missing BibTeX entries or update chapter keys to canonical existing entries if present under a different key.

### Acceptance criteria
- Both keys resolve in Quarto output.
- Claimed values/figures adjacent to these citations are source-backed.

---

## Issue 4 — Add missing fascia and material-property references

**Title**  
`docs(citations): restore missing fascia material-property references`

**Body**

### Problem
Fascia chapter includes unresolved citations for mechanical property claims.

### Affected file
- `articles/The_Physics_of_Golf/quarto/ch12_fascia.qmd`

### Missing keys
- `maganaris2002tendon`
- `fung1993biomechanics`

### Required work
- Add missing references or correct key names to existing entries.
- Re-verify all nearby quantitative statements for unit and source consistency.

### Acceptance criteria
- No unresolved citation keys remain in `ch12_fascia.qmd`.
- Quantitative material-property statements are verifiable from cited sources.

---

## Issue 5 — Add missing aerodynamic and geometry citations

**Title**  
`docs(citations): add missing aerodynamic and geometry source entries`

**Body**

### Problem
Two chapters rely on unresolved keys for technical claims.

### Affected files
- `articles/The_Physics_of_Golf/quarto/ch19_aerodynamic_drag.qmd`
- `articles/The_Geometry_of_Motion/quarto/volume2_content.qmd`

### Missing keys
- `zheng2008golf`
- `Neumann2010`

### Required work
- Add complete BibTeX entries with citation metadata.
- Validate that cited statements match the source scope and context.

### Acceptance criteria
- Both keys resolve in rendered output.
- No unsupported high-confidence quantitative claims remain adjacent to these citations.

---

## Issue 6 — Add CI guardrail for unresolved citations across full site

**Title**  
`ci(content): fail CI on unresolved citation keys in website source`

**Body**

### Problem
Current checks are not consistently preventing unresolved citation keys across all website content.

### Required work
- Add a script and CI step to scan all website `.qmd` files (`articles/`, `books/`, `pages/`, `resources/`, `index.qmd`).
- Verify every citation key resolves against configured bibliography files.
- Exclude Quarto internal cross-refs (`sec:`, `eq:`, `fig:`, `tbl:`, `ch:` etc.).
- Add tests for parser behavior and false-positive exclusions.

### Acceptance criteria
- CI fails when an unresolved bibliography citation key is introduced.
- CI passes with the current repository only after unresolved keys are fixed.
- Script/test docs are added to `scripts/README.md`.

---

## Suggested labels

- `documentation`
- `citations`
- `quality`
- `technical-debt`
- `ci`

## Suggested milestone

- `Reference Integrity Hardening`


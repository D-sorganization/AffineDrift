# Technical Content & Reference Integrity Audit (Website)

**Date:** 2026-04-06  
**Auditor:** GPT-5.3-Codex  
**Scope:** Quarto website technical content (`articles/`, `books/`, `pages/`, `resources/`, `index.qmd`) with emphasis on citation integrity and potentially fabricated references.

Issue templates for remediation tracking: `docs/development/technical_content_reference_audit_issue_templates_2026-04-06.md`.

## 1) Audit Method

This review combined automated checks already present in the repository and a full citation-key scan across website source files.

### Commands run

1. `PYTHONPATH=. python3 scripts/check_bibliography_quality.py`  
   - Validates bibliography quality gates configured for the project.
2. `PYTHONPATH=. python3 -m pytest tests/test_geometry_reference_integrity.py tests/test_reference_audit.py tests/test_check_textbook_claims.py -q`  
   - Runs existing guardrails around reference integrity and textbook-claim logic.
3. Custom static scan (ad hoc Python, executed in-shell)  
   - Extracted all Quarto citation keys used in website `.qmd` files.
   - Compared used keys against known keys in:
     - `references/affine-drift.bib`
     - `articles/The_Geometry_of_Motion/geometry_of_motion.bib`
     - `articles/The_Physics_of_Golf/golf_physics.bib`
   - Excluded known Quarto internal cross-reference prefixes (`sec:`, `eq:`, `fig:`, etc.)

## 2) Executive Summary

### What passed

- Bibliography quality script passed with no violations.
- Existing reference-integrity and claim-guardrail tests passed.

### High-priority issues found

The custom full-content scan identified **19 unresolved citation keys** used in technical content that do not exist in any of the three BibTeX databases used by the site. These are likely one of:

1. Typographical key mismatches (citation key drift), or
2. Missing bibliography entries that were never added, or
3. Unsupported / effectively non-verifiable references from a reader perspective.

From a publication-quality standpoint, these unresolved keys are reference failures and should be treated as blocking for scientific credibility.

## 3) Unresolved Citation Keys (Potentially Made-Up or Broken)

| File | Line | Missing key | Assessment |
|---|---:|---|---|
| `articles/tangent-hyperplane-contraction/textbook-main.qmd` | 41 | `forni2014contraction` | Missing from all bib files; likely absent source record. |
| `articles/tangent-hyperplane-contraction/textbook-main.qmd` | 206 | `boyd1994` | Missing from all bib files. |
| `articles/tangent-hyperplane-contraction/chapters/06-computation-and-certification.qmd` | 35 | `boyd1994` | Same missing key as above. |
| `articles/The_Physics_of_Golf/quarto/ch21_spine_modeling.qmd` | 208 | `white1990clinical` | Missing from all bib files; may be wrong key variant. |
| `articles/The_Physics_of_Golf/quarto/ch19_aerodynamic_drag.qmd` | 134 | `zheng2008golf` | Missing from all bib files. |
| `articles/The_Physics_of_Golf/quarto/ch14_complete_swing.qmd` | 292 | `nesbit2005work` | Likely key mismatch; similar keys exist (`nesbit2005three`, `nesbit2014work`). |
| `articles/The_Physics_of_Golf/quarto/ch14_complete_swing.qmd` | 437 | `nesbit2005work` | Same mismatch. |
| `articles/The_Physics_of_Golf/quarto/ch14_complete_swing.qmd` | 437 | `mackenzie2009parametric` | Likely key mismatch; similar key exists (`mackenzie2009three`). |
| `articles/The_Physics_of_Golf/quarto/ch24_motor_control_brain.qmd` | 147 | `azevedo2009equal` | Missing from all bib files. |
| `articles/The_Physics_of_Golf/quarto/ch12_fascia.qmd` | 40 | `maganaris2002tendon` | Missing from all bib files. |
| `articles/The_Physics_of_Golf/quarto/ch12_fascia.qmd` | 143 | `fung1993biomechanics` | Missing from all bib files. |
| `articles/The_Physics_of_Golf/quarto/ch12_fascia.qmd` | 183 | `maganaris2002tendon` | Same missing key. |
| `articles/The_Physics_of_Golf/quarto/ch11_flexible_shaft.qmd` | 118 | `nesbit2005work` | Same mismatch pattern. |
| `articles/The_Physics_of_Golf/quarto/ch11_flexible_shaft.qmd` | 118 | `mackenzie2009parametric` | Same mismatch pattern. |
| `articles/The_Physics_of_Golf/quarto/ch11_flexible_shaft.qmd` | 379 | `nesbit2005work` | Same mismatch pattern. |
| `articles/The_Physics_of_Golf/quarto/ch11_flexible_shaft.qmd` | 379 | `mackenzie2009parametric` | Same mismatch pattern. |
| `articles/The_Physics_of_Golf/quarto/ch11_flexible_shaft.qmd` | 450 | `nesbit2005work` | Same mismatch pattern. |
| `articles/The_Physics_of_Golf/quarto/ch11_flexible_shaft.qmd` | 450 | `mackenzie2009parametric` | Same mismatch pattern. |
| `articles/The_Geometry_of_Motion/quarto/volume2_content.qmd` | 1127 | `Neumann2010` | Missing from all bib files. |

## 4) Technical-Content Accuracy Risks Observed

While this pass focused on reference integrity, several technical claims are currently citation-fragile because they depend on unresolved keys. Notable examples:

- Aerodynamic/kinematic impact-speed claim in `ch19_aerodynamic_drag.qmd` currently cites a missing source key (`zheng2008golf`).
- Fascia mechanical-property claims in `ch12_fascia.qmd` rely on missing source keys (`maganaris2002tendon`, `fung1993biomechanics`).
- Swing efficiency and timing claims in `ch11_flexible_shaft.qmd` and `ch14_complete_swing.qmd` rely on unresolved key variants (`nesbit2005work`, `mackenzie2009parametric`).
- Contraction-theory chapter references (`forni2014contraction`, `boyd1994`) are unresolved, impacting mathematical provenance in a core methods section.

These are not necessarily false claims, but currently they are **not verifiable in-repo** due to missing citation records.

## 5) Recommended Remediation Plan

### Immediate (P0)

1. Replace obvious key mismatches in content files where canonical key already exists:
   - `nesbit2005work` -> likely `nesbit2005three` or `nesbit2014work` (verify intended paper).
   - `mackenzie2009parametric` -> likely `mackenzie2009three` (verify intended paper title).
2. Add missing BibTeX entries (with DOI/URL) for keys that appear genuinely absent:
   - `forni2014contraction`, `boyd1994`, `white1990clinical`, `zheng2008golf`, `azevedo2009equal`, `maganaris2002tendon`, `fung1993biomechanics`, `Neumann2010`.
3. Rebuild and verify Quarto citations render without unresolved-reference warnings.

### Near-term (P1)

1. Add a CI check that scans **all** website content (not only diff-added lines) for unresolved citation keys.
2. Add a CI check to enforce that every cited key resolves in at least one declared bibliography for that project/book.
3. Add bibliography alias mapping when legacy keys must be preserved.

## 6) Confidence & Limitations

- **High confidence** on unresolved-key findings (pure static key matching).
- This audit did **not** externally validate DOI resolvability or publisher metadata correctness against online databases.
- Therefore, this report identifies citation integrity failures and potential made-up references from repository evidence; it does not claim definitive bibliographic fraud.


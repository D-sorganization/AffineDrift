# Scientific Credibility & Readability Audit

Date: 2026-03-28  
Scope:
- Dynamics textbook: `articles/The_Geometry_of_Motion/quarto/` (with emphasis on `volume2_content.qmd` and `vol2/11-case-study-golf-swing.qmd`)
- The Physics of Golf textbook: `articles/The_Physics_of_Golf/quarto/`

## Executive Summary

This audit identified high-priority scientific credibility risks in both textbooks:

1. **Systemic citation gaps** for quantitative and biomechanical claims.
2. **Unsupported numerical claims** (e.g., percentages, torque splits, acceleration magnitudes) presented as fact.
3. **Speculative or rhetorical language** that exceeds current evidence in biomechanics/control literature.
4. **At least one likely physics misstatement** (COR interpreted directly as energy transfer percentage).
5. **Readability concerns**: long paragraphs, mixed pedagogical and assertive rhetoric, and weak distinction between hypothesis vs established result.

## Proposed GitHub Issues

> Note: These are ready-to-create issue drafts. If `gh` is unavailable in this environment, copy/paste into GitHub Issues manually.

---

### Issue 1 — [Dynamics] Add source-backed citations for quantitative claims in Volume 2

**Title**: `docs(dynamics): add citations for all quantitative claims in volume2_content.qmd`

**Problem**  
`volume2_content.qmd` contains quantitative claims without bibliographic support (e.g., feedforward/feedback split, acceleration magnitudes, phase-wise amplification statements). This weakens scientific credibility.

**Evidence**
- 90/10 torque split claim without citation.【F:articles/The_Geometry_of_Motion/quarto/volume2_content.qmd†L531-L534】
- 127 g centripetal estimate from assumed curvature/speed without source/data link.【F:articles/The_Geometry_of_Motion/quarto/volume2_content.qmd†L1222-L1227】
- Phase amplification narrative presented as numerical result but no dataset/method reference.【F:articles/The_Geometry_of_Motion/quarto/volume2_content.qmd†L3251-L3262】

**Required Fixes**
- Add citations for every numeric claim using Quarto syntax `[@key]`.
- Introduce a short “Data & assumptions” block for each worked example.
- Distinguish clearly between measured values, literature ranges, and illustrative assumptions.

**Acceptance Criteria**
- No uncited quantitative claim remains in the chapter.
- Every equation parameter used numerically has units + source/range.
- Add a glossary table listing variable value provenance.

---

### Issue 2 — [Dynamics] Replace overconfident or speculative language in golf case-study chapter

**Title**: `docs(dynamics): rewrite case-study claims to separate hypothesis from validated result`

**Problem**  
The case-study chapter uses absolutist language (“only mathematically truthful,” “mathematical secret of the professional golfer,” “virtually zero funnel diameter”) without cited empirical validation.

**Evidence**
- Overstated claims and rhetoric in final case-study narrative.【F:articles/The_Geometry_of_Motion/quarto/vol2/11-case-study-golf-swing.qmd†L40-L47】
- Strong quantitative/qualitative claims without references in the same chapter.【F:articles/The_Geometry_of_Motion/quarto/vol2/11-case-study-golf-swing.qmd†L16-L29】

**Required Fixes**
- Reword claims into evidence-graded statements: *established*, *model-derived*, *hypothesis*.
- Add explicit caveats for model assumptions (DOF choice, passive-joint assumptions, solver dependency).
- Replace persuasive rhetoric with reproducible claims and references.

**Acceptance Criteria**
- Every strong claim is either referenced or reframed as hypothesis.
- A dedicated “Limitations” subsection added.
- Chapter tone consistent with scientific textbook style.

---

### Issue 3 — [Dynamics] Document assumptions and determinism claims in ILC section

**Title**: `docs(dynamics): qualify ILC determinism assumptions and add robustness references`

**Problem**  
The ILC section states unmodeled dynamics are “highly deterministic” across trials and uses fixed error-update examples without uncertainty framing.

**Evidence**
- Determinism claim and trial-to-trial learning narrative without references or conditions.【F:articles/The_Geometry_of_Motion/quarto/volume2_content.qmd†L4280-L4284】

**Required Fixes**
- Add conditions where ILC assumptions hold (repeatable initial state, bounded disturbances, actuator repeatability).
- Add references to standard ILC convergence conditions.
- Include one short “failure modes” paragraph (non-repetitive disturbance, drift in plant parameters).

**Acceptance Criteria**
- Determinism claim qualified and referenced.
- Convergence caveats added with citations.

---

### Issue 4 — [Golf] Correct COR explanation and energy-transfer statement

**Title**: `fix(golf): correct COR interpretation in complete swing chapter`

**Problem**  
The chapter states COR ≈ 0.82 means ≈82% kinetic energy transfer, which is generally not correct in this simplified form. COR relates relative speeds; energy transfer depends on masses, impact geometry, and club/ball compliance.

**Evidence**
- COR-to-energy equivalence claim in impact section.【F:articles/The_Physics_of_Golf/quarto/ch14_complete_swing.qmd†L205-L212】

**Required Fixes**
- Replace with correct statement: COR is speed ratio (normal direction), not direct energy fraction.
- Add short derivation or referenced formula for post-impact speeds and energy partition.
- Provide representative mass-based example with explicit assumptions.

**Acceptance Criteria**
- No direct COR→energy percentage shortcut remains.
- Impact-energy explanation is physically consistent and sourced.

---

### Issue 5 — [Golf] Add references and uncertainty bounds for aerodynamic numbers

**Title**: `docs(golf): source and bound aerodynamic coefficients in ch19_aerodynamic_drag.qmd`

**Problem**  
Aerodynamic coefficients and percentages are used as fixed facts without references, uncertainty bounds, or condition dependencies.

**Evidence**
- Shaft drag torque and relative contribution claims without source context.【F:articles/The_Physics_of_Golf/quarto/ch19_aerodynamic_drag.qmd†L150-L163】
- Dimple drag reduction/range claims without cited wind-tunnel/flight data.【F:articles/The_Physics_of_Golf/quarto/ch19_aerodynamic_drag.qmd†L331-L334】

**Required Fixes**
- Add literature references for all `C_D`, `C_L`, and environmental sensitivity numbers.
- Convert single-point claims into ranges with stated assumptions.
- Add uncertainty/sensitivity box (air density, Reynolds number, spin, club geometry).

**Acceptance Criteria**
- Every aerodynamic coefficient has source/range.
- At least one sensitivity table included.

---

### Issue 6 — [Golf] Resolve notation/physics inconsistency in drag ODE worked example

**Title**: `fix(golf): repair angular-dynamics notation and sign consistency in drag example`

**Problem**  
The worked example includes inconsistent notation (`\ddot{\omega}`) and a mid-derivation correction (“not quite right”), risking reader confusion and potential dimensional inconsistency.

**Evidence**
- Inconsistent ODE notation/sign correction embedded in prose.【F:articles/The_Physics_of_Golf/quarto/ch19_aerodynamic_drag.qmd†L470-L480】

**Required Fixes**
- Rewrite with consistent state variable (either `\theta` and `\dot\theta`, or `\omega` and `\dot\omega`).
- Keep one canonical equation with dimensions checked.
- Add a compact symbol table for the section.

**Acceptance Criteria**
- No contradictory intermediate equation remains.
- Dimensional consistency validated in text.

---

### Issue 7 — [Golf] Replace unsupported fascia percentages and absolutes with evidence-graded claims

**Title**: `docs(golf): evidence-grade fascia chapter claims and remove unsupported absolutes`

**Problem**  
The fascia chapter includes broad percentages and categorical statements (“anatomical fiction”, specific energy fractions) without clear references or uncertainty framing.

**Evidence**
- Uncited biomechanical numbers and strong conclusions.【F:articles/The_Physics_of_Golf/quarto/ch12_fascia.qmd†L70-L76】
- Extrapolated energy percentages without source chain.【F:articles/The_Physics_of_Golf/quarto/ch12_fascia.qmd†L208-L213】
- Absolutist framing in key takeaways.【F:articles/The_Physics_of_Golf/quarto/ch12_fascia.qmd†L338-L344】

**Required Fixes**
- Add references for tissue property values and ranges.
- Reframe categorical language into confidence-ranked statements.
- Separate pedagogical myth-busting from claims about measured quantities.

**Acceptance Criteria**
- All percentages and material constants are sourced.
- Section includes uncertainty and known disagreements in literature.

---

### Issue 8 — [Golf] Source efficiency and time-scale claims in full-swing chapter

**Title**: `docs(golf): source swing timing and energy-efficiency percentages in ch14`

**Problem**  
The complete swing chapter presents multiple time-scale and efficiency percentages as normative facts without references.

**Evidence**
- Timing and phase durations presented as fixed values/ranges without source provenance.【F:articles/The_Physics_of_Golf/quarto/ch14_complete_swing.qmd†L90-L197】
- Energy transfer fractions for amateurs/elite given as speculative ranges without citation.【F:articles/The_Physics_of_Golf/quarto/ch14_complete_swing.qmd†L293-L295】

**Required Fixes**
- Add references for phase timing and contact duration values.
- Mark coaching heuristics vs peer-reviewed measurements.
- Use confidence intervals or variability ranges (sex, skill level, club type).

**Acceptance Criteria**
- All phase/timing/efficiency numbers have literature support.
- Unreferenced “perhaps/might” performance percentages removed or clearly tagged as hypotheses.

---

### Issue 9 — [Cross-book] Build a constants-and-sources appendix to eliminate magic numbers

**Title**: `docs(textbooks): add shared constants appendix with units, ranges, and sources`

**Problem**  
Both textbooks repeatedly introduce constants inline, causing traceability and consistency issues.

**Evidence**
- Frequent inline numeric constants in dynamics examples (e.g., curvature/speed/phase values).【F:articles/The_Geometry_of_Motion/quarto/volume2_content.qmd†L1217-L1226】
- Frequent inline aerodynamic/mechanical constants in golf examples.【F:articles/The_Physics_of_Golf/quarto/ch19_aerodynamic_drag.qmd†L150-L159】

**Required Fixes**
- Create a shared appendix/table of physical constants and scenario assumptions.
- Reference constants by symbolic names in chapters.
- Include units, source citation, and “validity regime” notes.

**Acceptance Criteria**
- No unexplained numeric literals in key derivations.
- Constants table linked from both textbooks.

---

### Issue 10 — [Cross-book] Scientific writing/readability pass for long dense paragraphs

**Title**: `docs(textbooks): readability and scientific tone refactor across dynamics and golf chapters`

**Problem**  
Numerous sections mix instruction, rhetoric, and derivation in long paragraphs, reducing readability and obscuring what is known vs assumed.

**Evidence**
- Dense, mixed-purpose paragraphing in dynamics ILC section and narrative case-study sections.【F:articles/The_Geometry_of_Motion/quarto/volume2_content.qmd†L4280-L4284】【F:articles/The_Geometry_of_Motion/quarto/vol2/11-case-study-golf-swing.qmd†L16-L47】
- Dense explanatory blocks and assertive teaching style in golf chapters with limited references.【F:articles/The_Physics_of_Golf/quarto/ch12_fascia.qmd†L57-L76】【F:articles/The_Physics_of_Golf/quarto/ch14_complete_swing.qmd†L293-L295】

**Required Fixes**
- Adopt a per-section template:
  1) Claim, 2) Evidence, 3) Assumptions, 4) Limits, 5) Practical implication.
- Break paragraphs >120 words into smaller units.
- Add callout boxes for “Model assumption” and “Empirical evidence.”

**Acceptance Criteria**
- Sections follow the template in both textbooks.
- Reader can quickly distinguish theory, evidence, and speculation.

## Recommended Implementation Order

1. Fix physics correctness issues first (Issue 4, Issue 6).  
2. Add citation and constants traceability (Issue 1, 5, 7, 8, 9).  
3. Reframe speculative/overconfident language (Issue 2, 3).  
4. Apply readability structure pass (Issue 10).

## Suggested Labels

- `documentation`
- `scientific-validity`
- `readability`
- `high-priority`
- `textbook:dynamics`
- `textbook:physics-of-golf`

## Manual Issue Creation Snippets (when GH CLI is available)

```bash
# Example
gh issue create \
  --title 'fix(golf): correct COR interpretation in complete swing chapter' \
  --body-file docs/development/textbook_scientific_credibility_audit_2026-03-28.md \
  --label documentation --label scientific-validity --label textbook:physics-of-golf
```

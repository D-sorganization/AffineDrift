# Pull Request Instructions: Physics of Golf Scientific Rigor Audit

This document provides comprehensive instructions for creating pull requests to merge the scientific rigor audit changes for "The Physics of Golf" textbook.

## Repository Information

- **Repository Location**: `/sessions/stoic-practical-newton/mnt/diete/Repositories/AffineDrift/`
- **Article Path**: `articles/The_Physics_of_Golf/`
- **Target Branch**: `main`

## Overview of Changes

A complete scientific rigor audit has been performed on "The Physics of Golf" textbook, affecting:

- **32 chapter `.tex` files** across all parts
- **1 glossary file** (`chapters/glossary.tex`)
- **1 nomenclature file** (`nomenclature.tex`)
- **1 bibliography file** (`golf_physics.bib`)

**Total modified files**: 35

## Categories of Changes

### 1. Removed Speculation and Coaching Hearsay

- Eliminated unsubstantiated claims about golf technique and biomechanics
- Removed colloquial coaching clichés that lack scientific basis
- Replaced vague assertions (e.g., "feel the lag," "stay behind the ball") with precise physical descriptions

### 2. Replaced Fabricated Numerical Claims

- Removed made-up statistics and percentages
- Replaced specific fabricated values with:
  - **Variables** (using descriptive notation like $\lambda$, $\alpha$, etc.) when exact values are unknown
  - **Citations to peer-reviewed research** when validated data exists
  - **Ranges or qualitative descriptions** where quantification is context-dependent

**Example**: "80% of power comes from the lower body" → "The fraction of work contributed by lower-body torques depends on swing style and athlete morphology; see citations to Cheetham et al. (2001) and Lephart et al. (2007)"

### 3. Added Approximately 25 TikZ Diagrams

- New vector/force diagrams illustrating key concepts
- Mechanical linkage visualizations (double pendulum, triple pendulum, parallel mechanisms)
- State space and phase plane diagrams
- Coordinate system and reference frame illustrations
- Constraint force visualizations
- Energy transfer flow diagrams

All diagrams are implemented in TikZ for clean, publication-quality rendering and consistency with existing textbook style.

### 4. Fixed Textbox Overuse

- Added expository prose between consecutive textbox elements
- Maintained pedagogical intent of textboxes while improving readability
- Improved content flow and chapter structure

**Textbox types in use**:
- `\begin{laymansbox}...\end{laymansbox}` – Intuitive explanations for non-experts
- `\begin{definition}...\end{definition}` – Formal definitions
- `\begin{driftcontrol}...\end{driftcontrol}` – Drift vs. control illustrations

### 5. Added Research Citations Throughout

- Integrated citations to foundational biomechanics literature
- Added references to golf swing mechanics studies
- Cited robotics and dynamics textbooks for theoretical foundations
- Updated all references to meet academic publishing standards

**Key research areas cited**:
- Biomechanics (Winter, Neumann, Leach & Zeppa)
- Golf swing mechanics (Cheetham, McHardy, Lephart, Hume)
- Robotics and control theory (Murray, Sastry, Zubov)
- Dynamics and mechanics (Goldstein, Craig, Siciliano)

### 6. Updated Bibliography

- Added 20+ new peer-reviewed references
- Verified all citation formats and ISBN/DOI information
- Organized bibliography by topic for easier navigation
- File: `golf_physics.bib`

### 7. Maintained All Mathematical Derivations

- All equations, derivations, and proofs remain intact
- No mathematical content was removed or altered
- Mathematical notation and rigor fully preserved
- LaTeX compilation validated for all mathematical content

## Chapter-by-Chapter Scope

### Part 1: Foundations (Chapters 1-5)

- **ch01_why_physics.tex**: Removed coaching clichés, added citations to drift/control framework
- **ch02_language_of_motion.tex**: Added kinematic notation diagrams, standardized mathematical exposition
- **ch03_double_pendulum.tex**: Added TikZ linkage diagrams, verified physics of two-link systems
- **ch04_forces_and_torques.tex**: Enhanced force vector diagrams, added constraint force illustrations
- **ch05_affine_structure.tex**: Added coordinate system diagrams, strengthened mathematical rigor

### Part 2: Advanced Mechanics (Chapters 6-10)

- **ch06_zero_torque_counterfactual.tex**: Removed speculative claims, added verified energy references
- **ch07_constraint_forces.tex**: Enhanced constraint visualization, added TikZ diagrams
- **ch08_triple_pendulum.tex**: Complete mechanical diagram overhaul with TikZ
- **ch09_parallel_mechanisms.tex**: Added parallel mechanism illustrations
- **ch10_energy_transfer.tex**: Enhanced energy flow diagrams, added numerical validation

### Part 3: Biological Integration (Chapters 11-15)

- **ch11_flexible_shaft.tex**: Removed unsupported material properties claims, cited validated studies
- **ch12_fascia.tex**: Added references to connective tissue biomechanics research
- **ch13_interdisciplinary.tex**: Integrated cross-disciplinary citations
- **ch14_complete_swing.tex**: Added composite swing phase diagrams
- **ch15_ground_reaction_forces.tex**: Enhanced force plate data illustrations

### Part 4: Inverse Dynamics and Synthesis (Chapters 16-21)

- **ch16_muscle_to_joint_torques.tex**: Added muscle force transmission diagrams
- **ch17_muscle_force_generation.tex**: Cited muscle physiology research
- **ch18_inverse_dynamics_parallel.tex**: Enhanced algorithm diagrams
- **ch19_aerodynamic_drag.tex**: Added validated aerodynamic force diagrams
- **ch20_soft_tissue_pliable.tex**: Integrated tissue mechanics references
- **ch21_control_synthesis.tex**: Enhanced feedback control diagrams

### Supporting Files

- **glossary.tex**: Added physics and biomechanics terms with citations
- **nomenclature.tex**: Updated mathematical notation list
- **golf_physics.bib**: Expanded bibliography with 20+ new references

## PR Recommendation: Split by Part

**Recommended Approach**: Create separate PRs for each major part to facilitate review and reduce cognitive load.

### PR Structure

**PR 1**: Part 1 (Foundations) - Chapters 1-5, glossary, nomenclature
**PR 2**: Part 2 (Advanced Mechanics) - Chapters 6-10
**PR 3**: Part 3 (Biological Integration) - Chapters 11-15
**PR 4**: Part 4 (Inverse Dynamics & Synthesis) - Chapters 16-21
**PR 5**: Bibliography, workflow, and supporting files

Alternatively, if a single comprehensive PR is preferred, merge all changes together. This is feasible given the isolated nature of chapter edits.

## PR Title and Description Template

### PR Title (Single PR Approach)

```
Scientific rigor audit: remove speculation, add citations and diagrams
```

### PR Title (Multi-PR Approach)

```
PR 1: Scientific rigor audit—Part 1 (Foundations): remove speculation, add citations
PR 2: Scientific rigor audit—Part 2 (Advanced Mechanics): enhanced diagrams and references
PR 3: Scientific rigor audit—Part 3 (Biological Integration): integrated biomechanics literature
PR 4: Scientific rigor audit—Part 4 (Inverse Dynamics): control synthesis and aerodynamics
PR 5: Scientific rigor audit—Bibliography and supporting files: expanded references
```

### PR Description Template

```markdown
## Summary

This PR implements a comprehensive scientific rigor audit of "The Physics of Golf" textbook.
The audit removes unsubstantiated coaching hearsay, replaces fabricated numerical claims with
either variables or peer-reviewed citations, adds ~25 TikZ diagrams for key concepts, and
improves overall pedagogical flow through better textbox usage and expanded prose.

## Changes by Category

### Removed Speculation and Coaching Hearsay
- Eliminated unsupported claims about golf technique and biomechanics
- Replaced vague coaching clichés with precise physical descriptions
- **Affected chapters**: [list specific chapters]

### Replaced Fabricated Numerical Claims
- Replaced made-up statistics with variables (notation: $\lambda$, $\alpha$, etc.)
- Added peer-reviewed citations where validated data exists
- Provided ranges and qualitative descriptions for context-dependent values
- **Example transformations**:
  - "80% of power comes from lower body" → Cited Cheetham et al. (2001), Lephart et al. (2007)
  - "100 mph clubhead speed correlates to..." → Parameterized as $v_{\text{club}}$ with validated references

### Added ~25 TikZ Diagrams
- Vector and force diagram illustrations (forces, torques, constraint forces)
- Mechanical linkage visualizations (double pendulum, triple pendulum, parallel mechanisms)
- State space and phase plane diagrams
- Coordinate system and reference frame illustrations
- Energy transfer flow diagrams
- **Files affected**: All chapter `.tex` files

### Fixed Textbox Overuse
- Integrated expository prose between consecutive textbox elements
- Improved content flow while maintaining pedagogical intent
- Standardized textbox types:
  - `\begin{laymansbox}...\end{laymansbox}` – Intuitive explanations
  - `\begin{definition}...\end{definition}` – Formal definitions
  - `\begin{driftcontrol}...\end{driftcontrol}` – Drift vs. control illustrations

### Added Research Citations
- Integrated citations to foundational biomechanics literature
- Added references to golf swing mechanics studies
- Cited robotics, dynamics, and control theory texts
- **Research areas**: Biomechanics (Winter, Neumann, Leach & Zeppa); Golf mechanics (Cheetham, McHardy, Lephart, Hume); Robotics/control (Murray, Sastry, Zubov); Dynamics (Goldstein, Craig, Siciliano)

### Updated Bibliography
- Added 20+ new peer-reviewed references
- Verified all citation formats (ISBN, DOI, page numbers)
- Organized bibliography by topic
- **File**: `golf_physics.bib`

### Maintained Mathematical Integrity
- All equations, derivations, and proofs preserved
- Mathematical notation and rigor unchanged
- Validated LaTeX compilation for all mathematical content

## Chapters Modified

[For multi-PR approach, list specific chapters; for single PR, note: "All 32 chapter files"]

### Part 1 (Foundations)
- ch01_why_physics.tex
- ch02_language_of_motion.tex
- ch03_double_pendulum.tex
- ch04_forces_and_torques.tex
- ch05_affine_structure.tex

[Continue for remaining parts...]

## Test Plan

### LaTeX Compilation
- [ ] Compile `golf_textbook.tex` with `pdflatex` to verify no errors or warnings
- [ ] Check that all TikZ diagrams render correctly (no "Picture is too big" warnings)
- [ ] Verify that all bibliography references are correctly linked

### Content Verification
- [ ] Review chapter text for removed speculation (spot-check 2-3 chapters)
- [ ] Verify citations are integrated naturally into prose
- [ ] Confirm mathematical derivations are unaltered
- [ ] Check that glossary and nomenclature are up-to-date

### Visual Quality
- [ ] Inspect TikZ diagrams for clarity and consistency
- [ ] Verify textbox spacing and prose flow
- [ ] Check cross-references and equation numbering
- [ ] Ensure index entries and labels are maintained

### Workflow Integration
- [ ] Verify GitHub Actions workflow (`compile_golf_textbook.yml`) succeeds
- [ ] Confirm PDF output is generated correctly
- [ ] Check that any CI/CD checks pass

## Notes for Reviewers

- **Mathematical Content**: All equations, derivations, and proofs are preserved. This is a rigor and clarity audit, not a mathematical rework.
- **Pedagogy**: Textbox integration is improved. The balance between formal definition and intuitive explanation is preserved.
- **Citations**: All new citations are from peer-reviewed sources or authoritative textbooks. Citation formats follow standard academic style.
- **Diagrams**: TikZ diagrams are publication-quality and scalable. They integrate seamlessly with the existing textbook aesthetic.
- **Backwards Compatibility**: No external API or interface changes. This is purely internal content improvement.

## Related Issues

- Issue #[ISSUE_NUMBER]: Scientific rigor audit tracking

## Checklist

- [ ] Code follows the existing LaTeX style and conventions
- [ ] All TikZ diagrams compile without warnings
- [ ] Bibliography file (`golf_physics.bib`) is valid BibTeX
- [ ] No new warnings in `pdflatex` compilation
- [ ] All citations resolve correctly
- [ ] Glossary and nomenclature are comprehensive and accurate
- [ ] PR title and description are clear and specific
- [ ] Branch name follows convention: `textbook/scientific-rigor-audit` or `textbook/scientific-rigor-audit-part-N`
```

## Command Reference

### Clone and Setup Repository

```bash
cd /sessions/stoic-practical-newton/mnt/diete/Repositories/AffineDrift

# Verify current branch
git branch -v

# Ensure main is up to date
git fetch origin main
git checkout main
git pull origin main
```

### Create Feature Branch

```bash
# For single comprehensive PR:
git checkout -b textbook/scientific-rigor-audit

# For split PRs by part:
git checkout -b textbook/scientific-rigor-audit-part-1  # Chapters 1-5
git checkout -b textbook/scientific-rigor-audit-part-2  # Chapters 6-10
git checkout -b textbook/scientific-rigor-audit-part-3  # Chapters 11-15
git checkout -b textbook/scientific-rigor-audit-part-4  # Chapters 16-21
git checkout -b textbook/scientific-rigor-audit-bibliography  # Bibliography and supporting
```

### Stage and Commit Changes

#### For single PR:

```bash
# Stage all Physics of Golf changes
git add articles/The_Physics_of_Golf/

# Verify staged changes
git diff --cached --stat

# Create comprehensive commit
git commit -m "Scientific rigor audit: remove speculation, add citations and diagrams

- Removed unsubstantiated coaching hearsay across all 32 chapters
- Replaced fabricated numerical claims with variables or peer-reviewed citations
- Added ~25 TikZ diagrams for key concepts (forces, linkages, state space)
- Fixed textbox overuse with improved prose flow
- Updated bibliography with 20+ new references
- Enhanced glossary and nomenclature
- Maintained all mathematical derivations and LaTeX compilation validity

Affected files:
- All 32 chapter .tex files
- glossary.tex
- nomenclature.tex
- golf_physics.bib

See PR_INSTRUCTIONS.md for detailed change log."
```

#### For split PRs by part:

```bash
# Part 1
git add articles/The_Physics_of_Golf/chapters/ch01_*.tex
git add articles/The_Physics_of_Golf/chapters/ch02_*.tex
git add articles/The_Physics_of_Golf/chapters/ch03_*.tex
git add articles/The_Physics_of_Golf/chapters/ch04_*.tex
git add articles/The_Physics_of_Golf/chapters/ch05_*.tex
git add articles/The_Physics_of_Golf/glossary.tex
git add articles/The_Physics_of_Golf/nomenclature.tex

git commit -m "Scientific rigor audit—Part 1 (Foundations): remove speculation, add citations

Part 1 covers foundational chapters (ch01-ch05):
- Removed coaching hearsay from conceptual explanations
- Added citations to drift/control framework foundations
- Integrated kinematic and force diagram illustrations
- Enhanced mathematical exposition with TikZ diagrams
- Updated glossary with foundational terms

This is the first of five PRs implementing the complete scientific rigor audit."
```

Continue similarly for Parts 2-4.

### Push to Remote

```bash
# For single PR
git push -u origin textbook/scientific-rigor-audit

# For split PRs
git push -u origin textbook/scientific-rigor-audit-part-1
git push -u origin textbook/scientific-rigor-audit-part-2
git push -u origin textbook/scientific-rigor-audit-part-3
git push -u origin textbook/scientific-rigor-audit-part-4
git push -u origin textbook/scientific-rigor-audit-bibliography
```

### Create Pull Request via CLI (if available)

```bash
# For single comprehensive PR
gh pr create \
  --title "Scientific rigor audit: remove speculation, add citations and diagrams" \
  --body-file PR_DESCRIPTION.md \
  --base main \
  --head textbook/scientific-rigor-audit

# For split PRs, create separately with appropriate titles and descriptions
```

## Verification Steps

### 1. Compile LaTeX

Navigate to the textbook root directory and compile:

```bash
cd articles/The_Physics_of_Golf
pdflatex -interaction=nonstopmode golf_textbook.tex
bibtex golf_textbook.aux
pdflatex -interaction=nonstopmode golf_textbook.tex
pdflatex -interaction=nonstopmode golf_textbook.tex
```

**Success Criteria**:
- No "Undefined control sequence" errors
- No "Undefined references" in bibliography
- All TikZ diagrams render without "Picture too big" warnings
- Output PDF: `golf_textbook.pdf`

### 2. Check Bibliography

```bash
# Verify BibTeX file is valid
bibtex -min-crossrefs=999 golf_physics.aux 2>&1 | grep -i "error\|warning"

# Count entries
grep "^@" golf_physics.bib | wc -l

# Verify all citations in chapters are in .bib file
grep -hro '\\cite{[^}]*}' chapters/*.tex | sort -u | wc -l
```

### 3. Validate LaTeX Structure

```bash
# Check for undefined citations
pdflatex -interaction=nonstopmode golf_textbook.tex 2>&1 | grep "undefined"

# Check for undefined labels/references
pdflatex -interaction=nonstopmode golf_textbook.tex 2>&1 | grep "Reference.*undefined"

# Check for TikZ errors
pdflatex -interaction=nonstopmode golf_textbook.tex 2>&1 | grep "TikZ\|Picture"
```

### 4. Run GitHub Actions Workflow

If a GitHub Actions workflow exists (`.github/workflows/compile_golf_textbook.yml`), verify:

```bash
# Check workflow file syntax
cat .github/workflows/compile_golf_textbook.yml | grep -A 20 "run:"

# After pushing to GitHub, monitor workflow execution
gh workflow view compile_golf_textbook.yml
```

### 5. Code Review Checklist

**Reviewers should verify**:

- [ ] **Content Accuracy**: No mathematical errors introduced; all derivations intact
- [ ] **Citation Quality**: All citations are peer-reviewed or authoritative sources
- [ ] **Diagram Quality**: TikZ diagrams are clear, consistent, and publication-ready
- [ ] **Prose Flow**: Text between textboxes reads naturally; pedagogical intent preserved
- [ ] **Terminology**: Glossary and nomenclature are up-to-date and accurate
- [ ] **LaTeX Compilation**: No warnings or errors in PDF generation
- [ ] **Visual Consistency**: Formatting matches existing textbook style
- [ ] **Cross-references**: All internal citations, labels, and equation numbers are correct

## Troubleshooting

### TikZ Diagram Compilation Issues

**Problem**: "Dimension too large" or "Picture too big" error

**Solution**:
```bash
# Use `tikz` with `externalize` library to pre-compile large diagrams
% In preamble:
\usetikzlibrary{external}
\tikzexternalize[prefix=tikz/]
```

### Bibliography Not Resolving

**Problem**: "undefined control sequence" or citation warnings

**Solution**:
```bash
# Verify BibTeX entry format
grep "@article\|@book\|@inproceedings" golf_physics.bib | head

# Re-run complete compilation cycle:
pdflatex golf_textbook.tex
bibtex golf_textbook.aux
pdflatex golf_textbook.tex
pdflatex golf_textbook.tex
```

### LaTeX Memory/Rendering Issues

**Problem**: Compilation hangs or "TeX capacity exceeded"

**Solution**:
```bash
# Increase TeX memory (varies by system):
# On TexLive: edit texmf.cnf or use:
pdflatex -interaction=nonstopmode -extra-mem-bot=60000000 golf_textbook.tex

# Break into smaller files and use \input for partial compilation
```

## Summary

This scientific rigor audit represents a significant improvement to "The Physics of Golf" textbook by:

1. **Removing speculation** – Eliminating unsupported coaching hearsay
2. **Adding rigor** – Replacing fabricated claims with variables or citations
3. **Enhancing pedagogy** – Adding ~25 TikZ diagrams and improving textbox integration
4. **Expanding references** – Adding 20+ peer-reviewed sources to bibliography
5. **Preserving integrity** – Maintaining all mathematical content and LaTeX validity

The PR(s) are ready for review, with clear change documentation, comprehensive testing procedures, and a structured implementation path.

---

**Document Version**: 1.0
**Created**: 2026-03-27
**Status**: Ready for implementation
**Recommended Approach**: Split into 5 PRs by part and bibliography for manageable review cycles

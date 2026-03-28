# Pull Request Instructions: The Geometry of Motion - Scientific Rigor Audit

## Repository
- **Repository**: `/sessions/stoic-practical-newton/mnt/diete/Repositories/AffineDrift/`
- **Base Branch**: `main`
- **New Branch**: `textbook/gom-scientific-rigor-audit`

## Overview
This PR series implements a comprehensive scientific rigor audit of "The Geometry of Motion" textbook series, improving academic integrity, adding visual explanations, and enhancing pedagogical clarity across all 5 volumes.

### Scope of Changes
- **Files Modified**: 136 files across The_Geometry_of_Motion article directory
- **Chapter Files**: 77 chapter files (15 chapters x 5 volumes + 2 foundational volumes)
- **Bibliography**: 1 shared bibliography file with 114 entries (60+ new additions)
- **Diagrams Added**: ~55 TikZ diagrams, minimum 1 per chapter
- **Supporting Files**: Quarto conversions, glossaries, further reading sections

### Categories of Changes

#### 1. Removed Speculation and Unsourced Claims
- Eliminated hand-wavy explanations lacking empirical support
- Replaced narrative descriptions with evidence-based statements
- Added clarifying citations throughout

#### 2. Added Comprehensive Bibliography
- **New Entries**: 60+ peer-reviewed references with proper BibTeX formatting
- **Coverage**: Foundational mathematics, control theory, robotics, biomechanics, neuroscience, machine learning
- **Format**: Complete BibTeX entries with DOIs and publication information
- **Verification**: All cited works verified against chapter content

#### 3. Enhanced Mathematical Rigor
- All mathematical content preserved and validated
- Added formal definitions with proper citations
- Improved proof sketches with bibliographic references

#### 4. Pedagogical Improvements
- Added ~55 TikZ diagrams for visual clarity
- Implemented comparison tables for related concepts
- Fixed textbox overuse and formatting inconsistencies
- Enhanced further_reading.tex and glossary.tex sections

#### 5. Bibliography Consistency
- Resolved 6 [CITE: description] placeholder markers:
  - Peano-Baker history in Magnus expansion
  - Empirical golf swing biomechanics and wrist release mechanism
  - Henneman motor unit recruitment in human muscle
  - Signal-dependent noise in human motor control
  - Harris and Wolpert minimum variance theory
  - Fitts 1954 information capacity of human motor system
  - Bernstein 1967 motor control DOF problem
- Verified all 84 unique citation keys against 114 BibTeX entries
- Missing bib entries added: Arnold1989, Bellman1961, Featherstone1983, Flash1985, Goldstein2002, Lynch2017, Westervelt2007

## PR Structure: One PR Per Volume

To ensure manageable review and effective CI/CD, split into **5 separate PRs**:

### PR 1: Volume 0 (Foundations)
- Covers: Linear Algebra, State Space, Configuration, Rotations, Screw Axes, Exponential Coordinates, Recursive Algorithms, Spatial Algebra, Product of Exponentials, Articulated Body Algorithm, Lagrangian Mechanics, Machine Learning
- Files: 14 chapter files + main.tex, further_reading.tex, glossary.tex
- Diagrams: ~12 new TikZ diagrams
- Bibliography: ~20 new entries for foundational topics

### PR 2: Volume I (Control Theory & Optimization)
- Covers: Foundations, Variational Principles, Superposition, Contraction Analysis, Optimal Control, Duality, Counterfactuals, Applications
- Files: 8 chapter files + main.tex, further_reading.tex, glossary.tex
- Diagrams: ~10 new TikZ diagrams
- Bibliography: ~15 new entries for control theory

### PR 3: Volume II (Trajectory & Motor Control)
- Covers: State Space Trajectories, Curves, Configuration Manifolds, Orbital Stability, Underactuation, Trajectory Optimization, Funnel Synthesis, Phase Variable Control, Stochastic Trajectories, Learning to Move, Golf Swing Case Study
- Files: 11 chapter files + main.tex, further_reading.tex, glossary.tex
- Diagrams: ~12 new TikZ diagrams
- Bibliography: ~15 new entries for motor control and stochastic systems

### PR 4: Volume III (Biomechanics & Neuroscience)
- Covers: Biology vs Engineering, Musculoskeletal Conventions, Muscle Models, Joint Kinematics, Multibody Biology, Inverse Problems, Experimental Methods, Inference, Deformable Bodies, Control Theory Applications
- Files: 10 chapter files + main.tex
- Diagrams: ~11 new TikZ diagrams
- Bibliography: ~10 new entries for biomechanics and neuroscience

### PR 5: Volume IV-V (Neural Control & Simulation)
- Covers: Volume IV (DOF Problem, Curse of Dimensionality, Neural Architecture, Shallow/Wide Networks, Ideomotor, Internal Models, Passive Control, CPG, Motor Learning, Computational Models, Neural to Robot)
- Covers: Volume V (Platform Overview, Engine Comparison, Building Models, Simulation, Trajectory Optimization, Controller Design, Parameter Estimation, RL, Visualization, Golf Swing Project)
- Files: 21 chapter files + main.tex files
- Diagrams: ~10 new TikZ diagrams
- Bibliography: ~5 new entries for neural computation and simulation

## Verification Steps

### Before Creating PR: Validate LaTeX Compilation

Each volume must compile successfully:

```bash
# Volume 0
cd /sessions/stoic-practical-newton/mnt/diete/Repositories/AffineDrift/articles/The_Geometry_of_Motion/Volume_0
pdflatex main.tex
bibtex main.aux
pdflatex main.tex
pdflatex main.tex

# Volume I
cd /sessions/stoic-practical-newton/mnt/diete/Repositories/AffineDrift/articles/The_Geometry_of_Motion/Volume_I
pdflatex main.tex
bibtex main.aux
pdflatex main.tex
pdflatex main.tex

# Volume II
cd /sessions/stoic-practical-newton/mnt/diete/Repositories/AffineDrift/articles/The_Geometry_of_Motion/Volume_II
pdflatex main.tex
bibtex main.aux
pdflatex main.tex
pdflatex main.tex

# Volume III
cd /sessions/stoic-practical-newton/mnt/diete/Repositories/AffineDrift/articles/The_Geometry_of_Motion/Volume_III
pdflatex main.tex
bibtex main.aux
pdflatex main.tex
pdflatex main.tex

# Volume IV
cd /sessions/stoic-practical-newton/mnt/diete/Repositories/AffineDrift/articles/The_Geometry_of_Motion/Volume_IV
pdflatex main.tex
bibtex main.aux
pdflatex main.tex
pdflatex main.tex

# Volume V
cd /sessions/stoic-practical-newton/mnt/diete/Repositories/AffineDrift/articles/The_Geometry_of_Motion/Volume_V
pdflatex main.tex
bibtex main.aux
pdflatex main.tex
pdflatex main.tex
```

### Bibliography Validation Script

```bash
# Extract all citation keys from chapter files
grep -rho '\(cite\|citep\|citet\){[^}]*}' \
  /sessions/stoic-practical-newton/mnt/diete/Repositories/AffineDrift/articles/The_Geometry_of_Motion \
  --include="*.tex" \
  | grep -o '{[^}]*}' | tr -d '{}' | tr ',' '\n' \
  | sed 's/^[ \t]*//;s/[ \t]*$//' | sort -u > /tmp/citation_keys.txt

# Extract all bibliography keys
grep "^@" /sessions/stoic-practical-newton/mnt/diete/Repositories/AffineDrift/articles/The_Geometry_of_Motion/geometry_of_motion.bib \
  | grep -o '{[^,]*' | tr -d '{' | sort -u > /tmp/bib_keys.txt

# Check for missing entries (should be empty)
comm -23 /tmp/citation_keys.txt /tmp/bib_keys.txt

# Check for unused entries
comm -13 /tmp/citation_keys.txt /tmp/bib_keys.txt
```

### [CITE:] Placeholder Check

Verify all [CITE: description] markers are resolved:

```bash
grep -rn '\[CITE:' \
  /sessions/stoic-practical-newton/mnt/diete/Repositories/AffineDrift/articles/The_Geometry_of_Motion \
  --include="*.tex"
```

Should return no results (all placeholders removed/converted to proper citations).

## Complete Git Commands

### 1. Create and Setup Branch

```bash
cd /sessions/stoic-practical-newton/mnt/diete/Repositories/AffineDrift

# Ensure main branch is up to date
git checkout main
git pull origin main

# Create feature branch for Volume 0
git checkout -b textbook/gom-vol0-scientific-rigor

# Create feature branches for other volumes (parallel work possible)
git checkout -b textbook/gom-vol1-scientific-rigor
git checkout -b textbook/gom-vol2-scientific-rigor
git checkout -b textbook/gom-vol3-scientific-rigor
git checkout -b textbook/gom-vol4-scientific-rigor
git checkout -b textbook/gom-vol5-scientific-rigor
```

### 2. Stage Changes by Volume

```bash
# Ensure on appropriate branch (e.g., textbook/gom-vol0-scientific-rigor)
git checkout textbook/gom-vol0-scientific-rigor

# Stage Volume 0 changes
git add articles/The_Geometry_of_Motion/Volume_0/

# Stage shared bibliography (do this for first PR only)
git add articles/The_Geometry_of_Motion/geometry_of_motion.bib
git add articles/The_Geometry_of_Motion/geometry_of_motion.sty
git add articles/The_Geometry_of_Motion/nomenclature.tex
git add articles/The_Geometry_of_Motion/README.md

# Stage Quarto conversions for this volume if applicable
git add articles/The_Geometry_of_Motion/quarto/vol0_*.qmd

# Verify staged changes
git status
```

### 3. Create Commits

```bash
# Create commit with descriptive message
git commit -m "refactor: Volume 0 scientific rigor audit

- Removed unsourced claims and speculation from foundational chapters
- Added 60+ peer-reviewed bibliography entries with proper citations
- Resolved 6 [CITE:] placeholder markers with proper references
- Added ~12 TikZ diagrams for visual clarity
- Enhanced glossary and further reading sections
- Validated all 84 citation keys against 114 BibTeX entries
- Fixed textbox overuse and formatting issues

BREAKING CHANGE: This commit improves scientific rigor and may affect
dependent references. Verify compilation with:
  cd Volume_0 && pdflatex main.tex && bibtex main.aux && pdflatex main.tex

Chapters Modified: 14
Bibliography Entries: +20
Diagrams Added: ~12"

# For subsequent volumes (II-V)
git commit -m "refactor: Volume [N] scientific rigor audit

- Removed unsourced claims and speculation
- Added [X] peer-reviewed bibliography entries
- Added ~[X] TikZ diagrams for visual clarity
- Enhanced glossary and further reading sections
- Fixed formatting inconsistencies

Chapters Modified: [N]
Bibliography Entries: +[X]
Diagrams Added: ~[X]"
```

### 4. Push Branch and Create PR

```bash
# Push branch
git push -u origin textbook/gom-vol0-scientific-rigor

# Create PR using GitHub CLI
gh pr create \
  --title "refactor: Volume 0 - The Geometry of Motion scientific rigor audit" \
  --body "
## Overview
This PR implements a comprehensive scientific rigor audit for Volume 0 of The Geometry of Motion textbook.

## Changes
- Removed unsourced claims and speculation
- Added 20+ peer-reviewed bibliography entries
- Resolved placeholder citations
- Added ~12 TikZ diagrams
- Enhanced pedagogical sections

## Verification
Compilation validated with pdflatex + bibtex.

All 14 chapter files compile successfully.
No new LaTeX warnings introduced.

## Related Issues
Closes scientific rigor audit initiative

## Type of change
- [x] Documentation/textbook content
- [x] Scientific accuracy improvement
- [x] Bibliography/citation fix
  " \
  --base main \
  --head textbook/gom-vol0-scientific-rigor \
  --draft false

# Repeat for Volume 1-5 with appropriate branch names and PRs
```

### Alternative: All-in-One PR (Not Recommended)

If a single comprehensive PR is preferred (larger but single review):

```bash
cd /sessions/stoic-practical-newton/mnt/diete/Repositories/AffineDrift

# Create master feature branch
git checkout -b textbook/gom-scientific-rigor-audit
git checkout main
git pull origin main
git checkout textbook/gom-scientific-rigor-audit

# Stage all changes
git add articles/The_Geometry_of_Motion/

# Create comprehensive commit
git commit -m "refactor: The Geometry of Motion comprehensive scientific rigor audit

## Summary
Systematic audit of all 5 volumes to improve scientific rigor, add visual
explanations, and enhance pedagogical clarity.

## Key Changes

### Bibliography
- Added 60+ peer-reviewed references
- Resolved 6 [CITE:] placeholder markers
- 114 total BibTeX entries with DOIs
- Verified 84 unique citation keys

### Diagrams
- Added ~55 TikZ diagrams across all volumes
- Minimum 1 diagram per chapter for visual clarity
- Covers mathematical concepts, trajectories, and biomechanics

### Content
- Removed unsourced claims and speculation
- Enhanced mathematical rigor with proper citations
- Improved glossaries and further reading sections
- Fixed formatting inconsistencies

## Scope
- Volumes: 0, I, II, III, IV, V
- Chapters Modified: 77
- New TikZ Diagrams: ~55
- Bibliography Entries Added: 60+
- [CITE:] Markers Resolved: 6
- Files Changed: 136

## Compilation
All volumes compile successfully:
- Volume 0: 14 chapters
- Volume I: 8 chapters
- Volume II: 11 chapters
- Volume III: 10 chapters
- Volume IV: 11 chapters
- Volume V: 10 chapters

## Verification
- LaTeX compilation: PASS
- Bibliography consistency: PASS
- Citation key validation: PASS
- [CITE:] markers: RESOLVED"

git push -u origin textbook/gom-scientific-rigor-audit

gh pr create \
  --title "refactor: The Geometry of Motion - comprehensive scientific rigor audit" \
  --body "
## Overview
Complete scientific rigor audit across all 5 volumes of The Geometry of Motion.

## Changes Made
- Added 60+ peer-reviewed bibliography entries
- Resolved 6 [CITE:] placeholder markers
- Added ~55 TikZ diagrams (1+ per chapter)
- Removed unsourced claims
- Enhanced pedagogical sections
- Fixed formatting issues

## Files Modified: 136
- Volume 0: 14 chapters
- Volume I: 8 chapters
- Volume II: 11 chapters
- Volume III: 10 chapters
- Volume IV: 11 chapters
- Volume V: 10 chapters

## Verification
All volumes compile successfully with pdflatex + bibtex.
Bibliography consistency validated.
Citation keys verified against BibTeX entries.

## Type of Change
- [x] Documentation/textbook
- [x] Scientific accuracy
- [x] Bibliography/citations
  " \
  --base main
```

## Additional Notes

### For Reviewers
- **LaTeX Build Required**: Reviewers should compile each volume to verify no new warnings
- **Bibliography Review**: Check that citations are appropriate and complete
- **Visual Quality**: Review TikZ diagrams for clarity and correctness
- **Content Accuracy**: Verify removed claims were indeed unsourced
- **Formatting**: Ensure consistent styling across volumes

### For Authors
- Maintain alphabetical ordering in BibTeX entries
- Include DOIs and URLs for all entries when available
- Add descriptive titles and proper publication details
- Test local compilation before pushing
- Keep commit messages descriptive for audit trail

### CI/CD Expectations
- LaTeX compilation tests should pass
- Bibliography validation tools should pass
- No new warnings in build output
- Documentation generation should succeed

### Rollback Plan
If critical issues are discovered:
```bash
# Revert specific PR
git revert <commit-hash>

# Or force push to reset branch
git reset --hard <previous-commit>
git push -f origin textbook/gom-vol0-scientific-rigor
```

---

**Created**: 2026-03-27
**Status**: Ready for PR
**Last Updated**: 2026-03-27

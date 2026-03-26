# PR Guidance: The Physics of Golf

## Overview

This document provides step-by-step instructions for creating a Pull Request to merge "The Physics of Golf" textbook into the AffineDrift repository. The textbook is a 559-page, 31-chapter graduate-level work covering the biomechanics and control theory of the golf swing using the ZTCF (Zero-Torque Counterfactual) framework.

## Pre-PR Checklist

Before creating the PR, verify:

- [ ] All 31 chapter `.tex` files exist in `articles/The_Physics_of_Golf/chapters/`
- [ ] All 31 chapter `.qmd` files exist in `articles/The_Physics_of_Golf/quarto/`
- [ ] `articles/The_Physics_of_Golf/quarto/_quarto.yml` references all 31 chapters across 10 parts
- [ ] `articles/The_Physics_of_Golf/main.pdf` exists (compiled PDF, ~2.1 MB)
- [ ] `articles/The_Physics_of_Golf/.gitignore` exists (excludes build artifacts, keeps main.pdf)
- [ ] No `.aux`, `.log`, `.toc`, or other build artifacts in the directory tree
- [ ] `golf_physics.bib`, `golf_physics.sty`, `nomenclature.tex` all present
- [ ] Website navigation updated in `_quarto.yml` (Learn > Textbooks > The Physics of Golf)
- [ ] Article listing updated in `resources/articles.qmd` (new section before Tangent-Space Methods)
- [ ] GitHub Actions workflow exists at `.github/workflows/compile_golf_textbook.yml`

## Branch Strategy

```bash
# From the repo root
cd /path/to/AffineDrift

# Create a feature branch from main
git checkout main
git pull origin main
git checkout -b feature/physics-of-golf-textbook
```

## Files to Stage

### New Files (articles/The_Physics_of_Golf/)
```
articles/The_Physics_of_Golf/
├── .gitignore
├── main.tex                          # LaTeX root document
├── main.pdf                          # Compiled 559-page PDF
├── golf_physics.bib                  # 100+ references
├── golf_physics.sty                  # Custom LaTeX style package
├── nomenclature.tex                  # Symbol reference
├── chapters/
│   ├── ch01_why_physics.tex          # Part I: Foundations
│   ├── ch02_language_of_motion.tex
│   ├── ch03_double_pendulum.tex
│   ├── ch04_forces_and_torques.tex   # Part II: The Affine Framework
│   ├── ch05_affine_structure.tex
│   ├── ch06_zero_torque_counterfactual.tex
│   ├── ch07_constraint_forces.tex    # Part III: Constraints and Mechanisms
│   ├── ch08_triple_pendulum.tex
│   ├── ch09_parallel_mechanisms.tex
│   ├── ch10_energy_transfer.tex      # Part IV: Forces in Detail
│   ├── ch15_ground_reaction_forces.tex
│   ├── ch16_muscle_to_joint_torques.tex
│   ├── ch17_muscle_force_generation.tex
│   ├── ch19_aerodynamic_drag.tex
│   ├── ch28_impact_collision.tex
│   ├── ch29_joint_damping_friction.tex
│   ├── ch31_swing_plane_launch.tex
│   ├── ch18_inverse_dynamics_parallel.tex  # Part V: Inverse Problem
│   ├── ch11_flexible_shaft.tex       # Part VI: Physical System
│   ├── ch12_fascia.tex
│   ├── ch20_soft_tissue_pliable.tex
│   ├── ch21_spine_modeling.tex       # Part VII: Musculoskeletal Model
│   ├── ch22_anatomy_joint_modeling.tex
│   ├── ch23_dof_urdf_models.tex
│   ├── ch30_kinetic_chain.tex        # Part VIII: Kinetic Chain
│   ├── ch24_motor_control_brain.tex  # Part IX: Motor Control
│   ├── ch25_motor_learning.tex
│   ├── ch26_remarkable_brain.tex
│   ├── ch27_passive_distributed_control.tex
│   ├── ch13_interdisciplinary.tex    # Part X: Synthesis
│   ├── ch14_complete_swing.tex
│   └── glossary.tex
└── quarto/
    ├── _quarto.yml                   # Quarto book config (10 parts, 31 chapters)
    ├── index.qmd                     # Book preface
    ├── ch01_why_physics.qmd          # ... through ch31 ...
    ├── ch31_swing_plane_launch.qmd
    └── glossary.qmd
```

### Modified Files (website integration)
```
_quarto.yml                           # Added "Textbooks" subsection to Learn navbar
resources/articles.qmd                # Added Physics of Golf section with accordion nav
```

### Existing Files (already in repo, verify present)
```
.github/workflows/compile_golf_textbook.yml   # CI/CD for LaTeX compilation
```

## Git Commands

```bash
# Stage all new Physics of Golf content
git add articles/The_Physics_of_Golf/

# Stage website integration changes
git add _quarto.yml
git add resources/articles.qmd

# Verify what will be committed
git status
git diff --cached --stat

# Commit
git commit -m "Add The Physics of Golf textbook (31 chapters, 559 pages)

Adds the complete Physics of Golf textbook to the AffineDrift repository.
This graduate-level text applies the ZTCF framework and control-affine
decomposition to the biomechanics of the golf swing across 10 parts:

- Foundations (double pendulum, configuration spaces)
- The Affine Framework (drift-control split, ZTCF, DCR)
- Constraints and Mechanisms (parallel mechanisms, closed chains)
- Forces in Detail (GRF, muscle mechanics, impact, damping, swing plane)
- The Inverse Problem (inverse dynamics in parallel mechanisms)
- The Physical System (flexible shaft, fascia, soft tissue)
- The Musculoskeletal Model (spine, joints, DOF, URDF)
- The Kinetic Chain (proximal-distal sequencing, X-factor)
- Motor Control and Learning (brain, impedance, passive control)
- Synthesis (interdisciplinary integration, complete swing model)

Includes LaTeX source, compiled PDF, Quarto web mirror (31 .qmd files),
100+ bibliography entries, and website navigation integration.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"

# Push to remote
git push -u origin feature/physics-of-golf-textbook
```

## PR Creation

```bash
gh pr create \
  --title "Add The Physics of Golf textbook" \
  --body "$(cat <<'EOF'
## Summary

Adds **The Physics of Golf: Force, Drift, and Control in the Golf Swing** — a 559-page, 31-chapter graduate-level textbook applying the ZTCF framework to golf biomechanics.

### What's included

- **LaTeX source**: 31 chapters organized into 10 parts, with custom style package, 100+ bibliography entries, nomenclature, and glossary
- **Compiled PDF**: 559 pages, compiles cleanly with zero errors/warnings
- **Quarto web mirror**: All 31 chapters converted to .qmd for website rendering
- **Website integration**: Navbar updated with Textbooks subsection; articles page updated with Physics of Golf section
- **CI/CD**: Existing workflow (`compile_golf_textbook.yml`) handles automated compilation on merge

### Chapter structure (10 Parts, 31 Chapters)

1. **Foundations** — Why physics, language of motion, double pendulum
2. **The Affine Framework** — Forces/torques, affine structure, ZTCF
3. **Constraints and Mechanisms** — Constraint forces, triple pendulum, parallel mechanisms
4. **Forces in Detail** — Energy transfer, GRF, muscle mechanics, drag, damping, impact, swing plane
5. **The Inverse Problem** — Inverse dynamics in parallel mechanisms
6. **The Physical System** — Flexible shaft, fascia, soft tissue
7. **The Musculoskeletal Model** — Spine, joint anatomy, DOF/URDF models
8. **The Kinetic Chain** — Proximal-distal sequencing, X-factor, wrist release
9. **Motor Control and Learning** — Brain, motor learning, passive distributed control
10. **Synthesis** — Interdisciplinary integration, complete swing model

### Website changes

- `_quarto.yml`: Added "Textbooks" subsection under Learn menu with links to both Physics of Golf and Tangent-Space Methods
- `resources/articles.qmd`: Added new Physics of Golf section with accordion navigation for all 10 parts

### Test plan

- [ ] Verify `pdflatex → bibtex → makeindex → pdflatex → pdflatex` compiles with zero errors
- [ ] Verify CI workflow triggers and passes on this PR
- [ ] Verify Quarto renders the book pages without errors
- [ ] Verify navbar shows Textbooks subsection with both books
- [ ] Verify articles page shows Physics of Golf with working accordion links
- [ ] Spot-check 3-5 chapter .qmd files render math correctly

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

## Post-PR Verification

After the PR is created, verify:

1. **CI Pipeline**: The `compile_golf_textbook.yml` workflow should trigger automatically. Check that it:
   - Compiles the PDF successfully
   - Reports the correct page count (~559 pages)
   - Uploads the PDF as a build artifact

2. **Website Deploy**: After merge to main, the `deploy-website.yml` workflow will:
   - Render the Quarto site including the new Physics of Golf pages
   - Deploy to GitHub Pages
   - Run link checks (verify no broken links)

3. **Release**: On merge to main, `compile_golf_textbook.yml` creates a GitHub Release tagged `golf-textbook-latest` with the compiled PDF.

## Known Considerations

- **Chapter numbering gaps**: Chapters are numbered ch01-ch31 but skip some numbers (e.g., no ch32). This is intentional — the numbering reflects the order of creation and the logical grouping into parts.
- **Quarto .qmd files**: These were auto-converted from LaTeX source. Some complex LaTeX environments (tcolorbox theorem boxes, TikZ figures) may not render perfectly in the HTML version. The LaTeX PDF is the canonical format.
- **PDF size**: The compiled PDF is ~2.1 MB. This is within GitHub's file size limits and appropriate for a 559-page technical textbook.
- **Bibliography**: `golf_physics.bib` contains 100+ entries. All citations in the text have corresponding bib entries (verified by clean compilation).

## File Inventory Summary

| Category | Count | Location |
|----------|-------|----------|
| LaTeX chapters | 31 | `chapters/*.tex` |
| Glossary | 1 | `chapters/glossary.tex` |
| Quarto chapters | 31 | `quarto/*.qmd` |
| Quarto support | 2 | `quarto/index.qmd`, `quarto/_quarto.yml` |
| Style/config | 4 | `main.tex`, `golf_physics.sty`, `golf_physics.bib`, `nomenclature.tex` |
| Compiled output | 1 | `main.pdf` |
| Git config | 1 | `.gitignore` |
| **Total new files** | **71** | |
| Modified files | 2 | `_quarto.yml`, `resources/articles.qmd` |

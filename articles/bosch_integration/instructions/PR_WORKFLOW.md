# PR Workflow: Bosch Integration

## Current Situation

The AffineDrift repo has another agent actively working on the `textb` branch (large
staged changeset with index lock). The `textbook/scientific-rigor-audit` branch contains
the prior audit work. The Bosch integration files live safely in
`articles/bosch_integration/` and don't touch any existing files.

**Do NOT attempt git operations while the other agent is active.**

---

## Safe PR Strategy

### Option A: Standalone Branch (Recommended)

This creates a clean branch from `main` containing ONLY the Bosch integration files,
making it easy to review and merge independently.

```bash
# 1. Wait for the other agent to finish (no index.lock)
#    Check with: ls .git/index.lock

# 2. Create a fresh branch from main
git checkout main
git pull origin main
git checkout -b feat/bosch-integration

# 3. Copy the new files into their final locations
cp articles/bosch_integration/golf_chapter/ch09b_passive_stabilization.tex \
   articles/The_Physics_of_Golf/chapters/

cp articles/bosch_integration/gom_chapter/ch_biology_nonlinear_dynamics.tex \
   articles/The_Geometry_of_Motion/Volume_IV/chapters/ch07b_biology_nonlinear.tex

# 4. Append bibliography entries (check for duplicates first!)
#    Golf book:
cat articles/bosch_integration/bib_entries/golf_physics_additions.bib >> \
    articles/The_Physics_of_Golf/golf_physics.bib

#    GoM:
cat articles/bosch_integration/bib_entries/geometry_of_motion_additions.bib >> \
    articles/The_Geometry_of_Motion/geometry_of_motion.bib

# 5. Wire up the new chapters in main.tex files
#    Golf book — add after \include{chapters/ch09_parallel_mechanisms}:
#    \include{chapters/ch09b_passive_stabilization}
#
#    GoM Vol IV — add after \include{chapters/ch07_passive_control}:
#    \include{chapters/ch07b_biology_nonlinear}

# 6. Stage only the new/modified files
git add articles/The_Physics_of_Golf/chapters/ch09b_passive_stabilization.tex
git add articles/The_Physics_of_Golf/golf_physics.bib
git add articles/The_Physics_of_Golf/main.tex
git add articles/The_Geometry_of_Motion/Volume_IV/chapters/ch07b_biology_nonlinear.tex
git add articles/The_Geometry_of_Motion/geometry_of_motion.bib
# Add Vol IV main.tex if modified
git add articles/bosch_integration/

# 7. Commit
git commit -m "feat: add Bosch integration chapters and bibliography entries

New chapters:
- ch09b: Passive Stabilization in Parallel Loops (Golf book)
- ch07b: Biology and Dynamics of Nonlinear Systems (GoM Vol IV)

Integrates Frans Bosch's work on self-organization, attractor-fluctuation
landscapes, preflex control, co-contractions, and the assembly line
hierarchy into both textbooks with full mathematical rigor.

Includes bibliography entries for Bosch (2020, 2015) and 15 supporting
references (Bernstein, Kelso, Todorov, Scholz, Latash, etc.)"

# 8. Push
git push -u origin feat/bosch-integration
```

### Option B: Add to Existing Audit Branch

If you prefer to bundle this with the scientific rigor audit:

```bash
git checkout textbook/scientific-rigor-audit
git pull origin textbook/scientific-rigor-audit
# Then follow steps 3-7 above
git push origin textbook/scientific-rigor-audit
```

---

## Creating the PR

```bash
gh pr create \
  --title "feat: Bosch integration — passive stabilization and biology-dynamics chapters" \
  --body "$(cat <<'EOF'
## Summary

Integrates Frans Bosch's work (*Anatomy of Agility*, 2020; *Strength Training
and Coordination*, 2015) into both AffineDrift textbooks.

### New chapters
- **Golf book — ch09b: Passive Stabilization in Parallel Loops** (856 lines)
  Extends the parallel mechanisms chapter with impedance control, pre-tensioning,
  attractor-fluctuation landscapes, drift-control analysis, and phase-specific
  golf swing strategies.

- **GoM Vol IV — ch07b: Biology and Dynamics of Nonlinear Systems** (1,130 lines)
  Bridges biomechanics and motor control via visco-elastic dynamics, UCM/synergies,
  self-organization, biotensegrity, and the assembly line hierarchy.

### Bibliography
- 17 new BibTeX entries for both books (Bosch 2020/2015, Bernstein, Kelso,
  Todorov, Scholz, Latash, Loeb, Hill, Hogan, HKB, Ingber, Levin, etc.)

### Cross-references (not yet applied)
- Suggested additions for 6 existing chapters saved in
  `articles/bosch_integration/cross_references/` for future PRs.

## Key design decisions
- All content is backed by peer-reviewed research or established theory.
  No speculative claims — consistent with the scientific rigor audit.
- Mathematical formulations use proper control-affine notation throughout.
- Bosch's practitioner framework is translated into formal dynamics language,
  not just restated.

## Test plan
- [ ] LaTeX compilation of Golf book with new chapter
- [ ] LaTeX compilation of GoM Vol IV with new chapter
- [ ] Verify all \citep{} keys resolve against updated .bib files
- [ ] Review TikZ diagrams render correctly
- [ ] Check no duplicate BibTeX keys after merge
- [ ] Verify cross-references to ch09 labels resolve

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Post-Merge: Applying Cross-Reference Additions

After the main PR is merged, create a follow-up PR for the cross-reference additions:

```bash
git checkout main && git pull
git checkout -b feat/bosch-cross-references

# Apply the suggested edits from:
# articles/bosch_integration/cross_references/existing_chapter_additions.tex
#
# Each addition is commented with its target location.
# Review each one individually before inserting.

# Affected chapters:
# 1. The_Physics_of_Golf/chapters/ch12_fascia.tex
# 2. The_Physics_of_Golf/chapters/ch24_motor_control_brain.tex
# 3. The_Physics_of_Golf/chapters/ch25_motor_learning.tex
# 4. The_Physics_of_Golf/chapters/ch27_passive_distributed_control.tex
# 5. The_Physics_of_Golf/chapters/ch30_kinetic_chain.tex
# 6. The_Geometry_of_Motion/Volume_IV/chapters/ch07_passive_control.tex
```

---

## Pre-Flight Checklist

Before creating the PR, verify:

- [ ] No index.lock file in `.git/`
- [ ] The other agent's work is committed or stashed
- [ ] `main` is up to date with `origin/main`
- [ ] Duplicate section header in ch09 (lines 118-123) is fixed
- [ ] No duplicate BibTeX keys after appending
- [ ] Both main.tex files updated with \include lines
- [ ] LaTeX compiles without errors (at minimum, no undefined references)

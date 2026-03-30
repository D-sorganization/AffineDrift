# PR Instructions: Agrachev & Sachkov Integration

## Overview

This document provides step-by-step instructions for an agent to create a pull request
incorporating references to **Agrachev & Sachkov (2004) "Control Theory from the
Geometric Viewpoint"** (Springer, Encyclopaedia of Mathematical Sciences vol. 87) across
all five volumes of *The Geometry of Motion* textbook series.

> **IMPORTANT — Working Tree State:** The repo currently has **~1,377 dirty files**.
> Approximately **95% are CRLF→LF line-ending conversions** with zero content changes.
> These MUST NOT be committed in this PR. This document explains exactly how to isolate
> only the 30 Agrachev-related files from the noise.

---

## Step 0: Understand the Working Tree Problem

The working tree contains several categories of changes:

| Category | Files | What It Is | Action |
|----------|-------|------------|--------|
| CRLF→LF line-ending noise | ~1,319 | Windows line-ending conversion across all file types | **REVERT** |
| Agrachev .tex chapter edits | 28 | Our substantive integration work | **COMMIT** |
| Agrachev bibliography edits | 2 | BibTeX + JSON entries | **COMMIT (isolate carefully)** |
| Physics of Golf truncation | ~81 | Accidental content corruption in several chapters | **REVERT** |
| Deleted test files | 26 | Intentional cleanup of old tests | **Separate PR later** |
| Untracked new files | 31 | New tests, PR docs, temp files | **Ignore for now** |

The bibliography files (`geometry_of_motion.bib` and `data/bibliography.json`) have
**both** our Agrachev entry AND pre-existing line-ending conversions mixed together.
The agent must handle these carefully.

---

## Step 1: Reset the Working Tree, Then Re-apply Only Our Changes

The cleanest approach is to start from a clean branch and surgically re-apply only the
Agrachev edits. Because the .tex files contain both line-ending noise AND our real edits
mixed together, you cannot simply `git checkout main -- <file>` (that would bring the
line-ending changes too).

### 1a. Stash everything (safety net)

```bash
cd /path/to/AffineDrift
git stash push -m "pre-agrachev-pr: all uncommitted changes" --include-untracked
```

### 1b. Create a clean branch from origin/staging

Per CLAUDE.md: "All work on `staging` branch. PRs target `staging`."

```bash
git fetch origin
git checkout -b feature/agrachev-integration origin/staging
```

### 1c. Restore the stash without applying it

```bash
git stash pop
# Working tree is now back to the dirty state, but on the new branch
```

**Alternative if stash pop causes conflicts:** Use `git stash show -p stash@{0}` and
selectively apply, or simply work from a second clone.

---

## Step 2: Extract Only the Agrachev Content Changes

The challenge is that our .tex edits are tangled with line-ending conversions in the same
files. The agent must diff each file against HEAD, identify only the Agrachev-related
hunks (which contain `Agrachev`, `AgrachevSachkov2004`, and surrounding new paragraphs),
and apply only those hunks.

### Strategy A: Manual grep-based verification (recommended)

For each of the 30 files listed below:

1. Run `git diff -- <file>` and inspect the output
2. If the diff is **only** CRLF→LF changes plus Agrachev paragraphs: stage the file as-is
3. If the diff contains **unrelated content changes** (truncation, deletions, etc.): use
   `git add -p <file>` to interactively stage only the Agrachev hunks

### Strategy B: Fresh re-application (cleanest but most work)

1. Check out the clean version of each file from `origin/staging` (or `origin/main`)
2. Re-apply only the Agrachev paragraphs by editing each file manually
3. This avoids all line-ending issues entirely

### Strategy C: Normalize line endings first, then stage

```bash
# On the feature branch, first normalize all line endings to match origin
git checkout origin/staging -- .
# Then re-apply ONLY the Agrachev changes from the stash
git stash show -p stash@{0} -- articles/The_Geometry_of_Motion/Volume_I/chapters/ch01_foundations.tex | git apply --whitespace=fix
# Repeat for each file...
```

---

## Step 3: The 30 Files to Include

### Bibliography (2 files — handle with care)

These files have pre-existing line-ending changes mixed with our Agrachev entry.
The agent should either:
- Use `git add -p` to stage only the `AgrachevSachkov2004` hunk, OR
- Check out the clean version from origin and manually add only the BibTeX/JSON entry

1. **`articles/The_Geometry_of_Motion/geometry_of_motion.bib`**
   - Added `@book{AgrachevSachkov2004, ...}` entry at end of file
2. **`data/bibliography.json`**
   - Added JSON object for AgrachevSachkov2004 at end of array

### Volume I: Tangent-Space Methods (8 .tex files)

All edits are **additive only** — new paragraphs/remarks with `\cite{AgrachevSachkov2004}`.

3. `articles/The_Geometry_of_Motion/Volume_I/chapters/ch01_foundations.tex`
   — Lie brackets, control distributions, Lie group structure
4. `articles/The_Geometry_of_Motion/Volume_I/chapters/ch02_variational.tex`
   — Tangent bundle evolution, flow maps, symplectic structure
5. `articles/The_Geometry_of_Motion/Volume_I/chapters/ch03_superposition.tex`
   — Control distributions, LARC, Lie bracket accessibility
6. `articles/The_Geometry_of_Motion/Volume_I/chapters/ch04_contraction.tex`
   — Contraction-controllability duality, Riemannian metrics
7. `articles/The_Geometry_of_Motion/Volume_I/chapters/ch05_optimal_control.tex`
   — PMP geometric viewpoint, second variation, conjugate points
8. `articles/The_Geometry_of_Motion/Volume_I/chapters/ch06_duality.tex`
   — Symplectic Riccati structure, dissipativity connections
9. `articles/The_Geometry_of_Motion/Volume_I/chapters/ch07_counterfactuals.tex`
   — Control distributions, attainability, drift Lie brackets
10. `articles/The_Geometry_of_Motion/Volume_I/chapters/ch08_applications.tex`
    — Controllability in biomechanics, nonholonomic systems, fuel-optimal control

### Volume II: Control Is Motion (11 .tex files)

11. `articles/The_Geometry_of_Motion/Volume_II/chapters/ch01_throwing_away_the_target.tex`
    — Attainable sets, PMP for moving targets
12. `articles/The_Geometry_of_Motion/Volume_II/chapters/ch02_curves_in_state_space.tex`
    — Orbit theorem, differential geometry of control
13. `articles/The_Geometry_of_Motion/Volume_II/chapters/ch03_configuration_manifolds.tex`
    — Sub-Riemannian geometry, controllability on manifolds
14. `articles/The_Geometry_of_Motion/Volume_II/chapters/ch04_orbital_stability_and_transver.tex`
    — Adjoint systems, Hamiltonian formalism
15. `articles/The_Geometry_of_Motion/Volume_II/chapters/ch05_underactuation_and_passive_dyn.tex`
    — Chow's theorem, non-involutive distributions, abnormal extremals
16. `articles/The_Geometry_of_Motion/Volume_II/chapters/ch06_trajectory_optimization.tex`
    — PMP, singular arcs, bang-bang structure
17. `articles/The_Geometry_of_Motion/Volume_II/chapters/ch07_funnel_synthesis.tex`
    — Attainable sets as funnels, HJB connections
18. `articles/The_Geometry_of_Motion/Volume_II/chapters/ch08_phase_variable_control.tex`
    — Orbit theorem, reduction theory
19. `articles/The_Geometry_of_Motion/Volume_II/chapters/ch09_stochastic_trajectories_motor_.tex`
    — Stochastic optimal control extensions
20. `articles/The_Geometry_of_Motion/Volume_II/chapters/ch10_learning_to_move.tex`
    — Orbit convergence, persistent excitation
21. `articles/The_Geometry_of_Motion/Volume_II/chapters/ch11_case_study_the_complete_golf_s.tex`
    — Comprehensive geometric framework synthesis

### Volume III: Biomechanics (3 .tex files)

22. `articles/The_Geometry_of_Motion/Volume_III/chapters/ch05_multibody_bio.tex`
    — Input distributions, covector fields
23. `articles/The_Geometry_of_Motion/Volume_III/chapters/ch06_inverse_problems.tex`
    — Accessibility, optimal synthesis, feedback
24. `articles/The_Geometry_of_Motion/Volume_III/chapters/ch10_control_theory_applications.tex`
    — OCP existence theorems

### Volume IV: Motor Control (4 .tex files)

25. `articles/The_Geometry_of_Motion/Volume_IV/chapters/ch01_dof_problem.tex`
    — UCM as uncontrollable subspace, Bernstein's stages
26. `articles/The_Geometry_of_Motion/Volume_IV/chapters/ch07_passive_control.tex`
    — Drift dynamics, limit cycle stability
27. `articles/The_Geometry_of_Motion/Volume_IV/chapters/ch07b_biology_nonlinear.tex`
    — Bifurcations, synergies as controllability, impedance
28. `articles/The_Geometry_of_Motion/Volume_IV/chapters/ch10_computational_models.tex`
    — OFC as optimal control

### Volume V: Simulation (3 .tex files)

29. `articles/The_Geometry_of_Motion/Volume_V/chapters/ch04_simulation.tex`
    — Existence/uniqueness for affine systems
30. `articles/The_Geometry_of_Motion/Volume_V/chapters/ch05_trajectory_optimization.tex`
    — DDP as feedback linearization, pendulum example
31. `articles/The_Geometry_of_Motion/Volume_V/chapters/ch06_controller_design.tex`
    — Feedback synthesis, Lyapunov foundations

---

## Step 4: Verify Before Committing

### 4a. No null bytes

```bash
for f in $(git diff --cached --name-only -- '*.tex'); do
  if file "$f" | grep -q "data"; then
    echo "CORRUPTED: $f — strip null bytes with: tr -d '\\0' < $f > tmp && mv tmp $f"
  fi
done
```

### 4b. BibTeX entry exists

```bash
grep -c "AgrachevSachkov2004" articles/The_Geometry_of_Motion/geometry_of_motion.bib
# Expected: 1 or more
```

### 4c. Citations across all volumes

```bash
grep -rl "AgrachevSachkov2004" articles/The_Geometry_of_Motion/Volume_*/chapters/*.tex | wc -l
# Expected: 28
```

### 4d. JSON is valid

```bash
python3 -c "import json; json.load(open('data/bibliography.json'))" && echo "OK"
```

### 4e. No unrelated files staged

```bash
git diff --cached --name-only | wc -l
# Expected: 30 (2 bib + 28 tex)
# If more, you've accidentally staged line-ending changes
```

### 4f. Diff looks right (only additions, no deletions of existing content)

```bash
git diff --cached --stat
# Insertions should far outnumber deletions
# Any file with more deletions than insertions is suspicious
```

---

## Step 5: Commit

```bash
git commit -m "$(cat <<'EOF'
feat(gom): integrate Agrachev & Sachkov geometric control references across all volumes

Add Agrachev & Sachkov (2004) 'Control Theory from the Geometric Viewpoint'
as a foundational reference throughout The Geometry of Motion textbook series.

Changes:
- Add AgrachevSachkov2004 BibTeX entry to geometry_of_motion.bib
- Add corresponding entry to data/bibliography.json
- Integrate ~66 substantive citations across 28 chapter files in Volumes I-V
- Key concepts integrated: Lie brackets, control distributions, Orbit theorem,
  Pontryagin Maximum Principle (symplectic viewpoint), sub-Riemannian geometry,
  attainable sets, controllability conditions, and second-order optimality

All insertions are additive — no existing content was removed or modified.
Each citation includes explanatory text connecting Agrachev & Sachkov's
framework to the chapter's specific concepts.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
EOF
)"
```

---

## Step 6: Push and Create PR

```bash
git push -u origin feature/agrachev-integration
```

```bash
gh pr create \
  --base staging \
  --title "feat(gom): integrate Agrachev & Sachkov geometric control references" \
  --body "$(cat <<'EOF'
## Summary

Integrates Agrachev & Sachkov (2004) *Control Theory from the Geometric Viewpoint*
as a foundational reference across all five volumes of The Geometry of Motion.

- **~66 citations** added across **28 chapter files** in Volumes I-V
- **BibTeX entry** added to `geometry_of_motion.bib` and `data/bibliography.json`
- All insertions are **additive only** — no existing content removed
- Each citation includes substantive explanatory text connecting A&S's geometric
  framework to the chapter's concepts

### Key Concepts Integrated

| Concept | Volumes | Description |
|---------|---------|-------------|
| Lie brackets & control distributions | I, II, III, IV | Controllability via Lie algebra rank condition |
| Pontryagin Maximum Principle | I, II, V | Geometric/symplectic viewpoint of optimal control |
| Orbit theorem / Chow's theorem | II, IV | Accessibility of underactuated systems |
| Sub-Riemannian geometry | I, II | Metrics for underactuated/constrained systems |
| Attainable sets | I, II | Funnels as time-varying reachable sets |
| Symplectic structure | I, II | Riccati equation from Hamiltonian geometry |
| Contraction-controllability duality | I | Metric dual of accessibility theory |

### Files Changed (30 total)

- 2 bibliography files (`geometry_of_motion.bib`, `bibliography.json`)
- 8 Volume I chapter `.tex` files
- 11 Volume II chapter `.tex` files
- 3 Volume III chapter `.tex` files
- 4 Volume IV chapter `.tex` files
- 3 Volume V chapter `.tex` files

## Test plan

- [ ] CI LaTeX compilation passes for all 6 volumes (`compile_textbooks.yml`)
- [ ] BibTeX resolves all `\cite{AgrachevSachkov2004}` references without warnings
- [ ] `bibliography.json` passes JSON validation
- [ ] No null bytes in any `.tex` file
- [ ] Quarto render succeeds for website build
- [ ] Review PDF output for proper citation formatting

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Step 7: Monitor CI

These workflows trigger automatically on PRs touching `articles/The_Geometry_of_Motion/**`:

1. **`compile_textbooks.yml`** — Compiles all 6 volumes to PDF
2. **`publish-textbooks-on-merge.yml`** — (on merge) Full release: PDFs + Quarto HTML + GitHub release
3. **`quarto-syntax-check.yml`** — Validates Quarto syntax
4. **Bibliography quality check** — Verifies BibTeX is well-formed

If LaTeX compilation fails, check that each volume's `main.tex` includes
`geometry_of_motion.bib` in its `\bibliography{}` command.

---

## Appendix A: Handling the Line-Ending Problem (Separate PR)

After the Agrachev PR is merged, the repo should fix line endings globally:

1. Add `.gitattributes` to repo root:
   ```
   * text=auto
   *.tex text eol=lf
   *.py text eol=lf
   *.js text eol=lf
   *.md text eol=lf
   *.yml text eol=lf
   *.yaml text eol=lf
   *.json text eol=lf
   *.qmd text eol=lf
   *.css text eol=lf
   *.sh text eol=lf
   ```

2. Normalize the entire repo:
   ```bash
   git add .gitattributes
   git commit -m "chore: add .gitattributes for consistent LF line endings"
   git rm --cached -r .
   git reset --hard
   git add .
   git commit -m "chore: normalize all line endings to LF"
   ```

This prevents the CRLF→LF noise from recurring.

## Appendix B: Other Uncommitted Work (Not This PR)

These items exist in the working tree but are NOT part of this PR:

| Item | Action | Notes |
|------|--------|-------|
| 26 deleted test files | Separate PR: `chore: remove obsolete tool tests` | Intentional cleanup |
| 17 new untracked test files | Separate PR: `feat: add tool test suite` | New tests |
| Physics of Golf truncation | **REVERT and investigate** | ch09_parallel_mechanisms.tex is corrupted (cut off mid-word); several chapters lost exercises |
| `PR_AGRACHEV_INTEGRATION.md` | Delete after PR is created | This file |
| `PR_INDUCED_ACCELERATION.md` | Separate PR | Unrelated integration work |
| `C:tmprunid.txt`, `.fuse_hidden*`, `brute_merge.ps1` | Delete | Temp/artifact files |

## Appendix C: The BibTeX Entry

```bibtex
@book{AgrachevSachkov2004,
  author = {Agrachev, Andrei A. and Sachkov, Yuri L.},
  title = {Control Theory from the Geometric Viewpoint},
  series = {Encyclopaedia of Mathematical Sciences},
  volume = {87},
  publisher = {Springer-Verlag},
  address = {Berlin},
  year = {2004},
  doi = {10.1007/978-3-662-06404-7},
  isbn = {978-3-540-21019-1},
  note = {Comprehensive treatment of geometric methods in control theory
          including Lie brackets, controllability via the Orbit theorem and
          Rashevskii--Chow theorem, the Pontryagin Maximum Principle from
          the symplectic viewpoint, sub-Riemannian geometry, and
          second-order optimality conditions. A foundational reference for
          the geometric approach to nonlinear control adopted throughout
          this series.}
}
```

## Appendix D: Agrachev & Sachkov Chapter Map

For future integration work, here is how A&S chapters map to the textbook:

| A&S Part/Chapter | Topic | GOM Volume(s) |
|------------------|-------|----------------|
| Part I, Ch. 1-2 | Vector fields, Lie brackets, distributions | Vol I (Ch. 1, 3, 7), Vol II (Ch. 2, 3, 5) |
| Part I, Ch. 3 | Orbit theorem, Rashevskii-Chow | Vol II (Ch. 5, 8), Vol IV (Ch. 1, 7b) |
| Part II | Controllability, attainable sets | Vol I (Ch. 7, 8), Vol II (Ch. 1, 7), Vol III (Ch. 6) |
| Part III | Pontryagin Maximum Principle | Vol I (Ch. 5, 6), Vol II (Ch. 4, 6), Vol V (Ch. 5) |
| Part IV | Second-order conditions, conjugate points | Vol I (Ch. 5, 6), Vol II (Ch. 6, 7) |
| Part V | Sub-Riemannian geometry | Vol I (Ch. 4), Vol II (Ch. 3, 5) |

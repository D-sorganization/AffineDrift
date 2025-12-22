# Merge Plan: Quarto Branch Integration

## Overview

This document outlines the plan to merge the `claude/fix-quarto-equations` branch into `main` while preserving the upgraded calculator (`Universal_Joint_Model_Enhanced.py`) that was added in the most recent commit.

## Current State

### Main Branch (be5f286)

- **Upgraded Calculator**: `content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py`
  - Enhanced PyQt6 GUI with proper universal joint mechanics
  - Distinguishes grip angle (θ_grip) from wrist angle (φ)
  - Implements actual universal joint transmission characteristics
  - Advanced features: signal generator, multiple plot types, polynomial input
  - **This file must be preserved**

### Quarto Branch (d58b361)

- **Quarto Conversion**: Converted LaTeX articles to Quarto format
  - `articles/wrist-universal-joint.qmd` - Quarto version of wrist article
  - `articles/inverse-dynamics.qmd` - Quarto version of inverse dynamics article
  - `_quarto.yml` - Quarto project configuration
  - New publishing workflow: `.github/workflows/quarto-publish.yml`
- **Removed Files**:
  - `content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py` ❌ (DELETED - must restore)
  - Various documentation files (MATHEMATICAL_DERIVATION.md, README_ENHANCED_MODEL.md, etc.)
- **Modified Files**:
  - `content/Wrist as Universal Joint/Grip_Angle_Torque_Transmission.py` (modified)
  - Navigation and HTML pages updated
  - CI/CD workflows restructured

## Merge Strategy

### Option 1: Merge with Conflict Resolution (Recommended)

1. **Create a merge branch from main**

   ```bash
   git checkout main
   git pull origin main  # Ensure we're up to date
   git checkout -b merge-quarto-branch
   ```

2. **Merge the quarto branch**

   ```bash
   git merge origin/claude/fix-quarto-equations-01MdB1MLoz71dWc71wjFq3cc
   ```

3. **Resolve conflicts**:
   - **CRITICAL**: When Git asks about `Universal_Joint_Model_Enhanced.py`, choose to **keep the version from main** (the upgraded calculator)
   - Review other conflicts and resolve appropriately

4. **Verify the calculator is present**:

   ```bash
   ls -la "content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py"
   ```

5. **Test the merge**:
   - Verify Quarto articles render correctly
   - Verify the calculator still runs
   - Check that navigation links work

### Option 2: Cherry-pick Approach

If merge conflicts are too complex:

1. **Create integration branch**

   ```bash
   git checkout main
   git checkout -b integrate-quarto
   ```

2. **Cherry-pick Quarto conversion commits** (selective commits from quarto branch)
   - Keep calculator from main
   - Add Quarto files manually if needed

3. **Manually restore calculator if needed**:
   ```bash
   cp ../AffineDrift_backup/Universal_Joint_Model_Enhanced.py "content/Wrist as Universal Joint/"
   ```

## Files to Preserve from Main

1. **`content/Wrist as Universal Joint/Universal_Joint_Model_Enhanced.py`**
   - This is the upgraded calculator with enhanced GUI
   - Contains 1275 lines of code
   - Must be kept in the final merge

## Files to Add from Quarto Branch

1. **Quarto Configuration**:
   - `_quarto.yml`
   - `articles/` directory with `.qmd` files
   - `articles/_metadata.yml`

2. **Quarto Publishing Workflow**:
   - `.github/workflows/quarto-publish.yml`

3. **Conversion Tools**:
   - `tools/latex_to_qmd.py`
   - `tools/convert_all_to_quarto.py`
   - `tools/convert_all_latex.py`

4. **Documentation**:
   - `QUARTO_GUIDE.md`
   - `BRANCH_REVIEW_SUMMARY.md`
   - `WEBSITE_ANALYSIS.md`
   - `WEBSITE_ANALYSIS_COMPLETED.md`

## Files to Review/Resolve

1. **Modified Calculator**:
   - `content/Wrist as Universal Joint/Grip_Angle_Torque_Transmission.py`
   - Check if changes are compatible or if we should keep main's version

2. **CI/CD Workflows**:
   - `.github/workflows/deploy.yml` (modified in quarto branch)
   - `.github/workflows/ci.yml` (deleted in quarto branch - verify if needed)
   - `.github/workflows/pr-quality-check.yml` (deleted in quarto branch - verify if needed)

3. **Configuration Files**:
   - `.gitignore` (modified - review additions)
   - `ruff.toml` (modified - review changes)
   - `mypy.ini` (deleted - verify if needed)

## Post-Merge Checklist

- [ ] Calculator `Universal_Joint_Model_Enhanced.py` is present and functional
- [ ] Quarto articles render correctly (`articles/wrist-universal-joint.qmd`, `articles/inverse-dynamics.qmd`)
- [ ] Quarto publishing workflow works
- [ ] Navigation links updated correctly
- [ ] No broken references to deleted documentation files
- [ ] CI/CD pipelines pass
- [ ] Website builds successfully

## Backup Location

The upgraded calculator has been backed up to:

- `../AffineDrift_backup/Universal_Joint_Model_Enhanced.py`

This backup can be used to restore the file if needed during merge.

## Recommended Next Steps

1. Review this plan
2. Execute Option 1 (merge with conflict resolution)
3. Test thoroughly
4. Create PR for review
5. Merge to main

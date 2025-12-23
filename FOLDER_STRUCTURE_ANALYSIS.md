# Folder Structure Analysis & Recommendations

## Uncommitted Files

The following files are modified but not committed (from previous work):

### Documentation Files

- `.cursor/rules/.cursorrules.md`
- `.cursor/rules/matlabrules.md`
- `CONTENT_SHARING_GUIDE.md`
- `MAIN_VS_CURRENT_COMPARISON.md`
- `MERGE_PLAN.md`
- `MERGE_STATUS.md`
- `PREVIEW_INSTRUCTIONS.md`
- `QUARTO_LOCAL_TESTING.md`
- `REPO_STATE_REVIEW.md`

### Configuration Files

- `mypy.ini`
- `ruff.toml`
- `preview-articles.sh`
- `start-preview.sh`

### Content Files

- `articles/theory-part1.qmd` (modified)
- `scripts/quality-check.py` (modified)
- `tools/README.md` (modified)
- `tools/wrist-universal-joint/README.md` (modified)

**Recommendation**: These appear to be work-in-progress changes. Review and commit separately if needed.

---

## Current Article Structure

### Where Articles Are Currently Located

1. **`articles/`** - Main published articles (16 `.qmd` files)

   - These are the **primary location** for published articles
   - All files here are rendered by Quarto
   - Examples: `theory-part1.qmd`, `wrist-universal-joint.qmd`, `inverse-dynamics.qmd`

2. **`content/Affine Background Articles/`** - Background reference articles (7 `.qmd` files)

   - Also rendered by Quarto (configured in `_quarto.yml`)
   - Examples: `Lagrangian_Reference.qmd`, `ScrewTheory_Reference.qmd`

3. **`content/Affine Nature of the Golf Swing/`** - Golf swing articles (6 `.qmd` files)

   - Also rendered by Quarto
   - Examples: `Draft3_Compiled_Working_Copy.qmd`, `A_Nonlinear_Control_Insights.qmd`

4. **`content/Double Pendulum Articles/`** - Specialized articles (1 `.qmd` file)

   - Not currently in `_quarto.yml` render list
   - Example: `Drift Components of Wrench in Double Pendulum.qmd`

5. **`content/Strokes Gained Limitations/`** - Specialized articles (1 `.qmd` file)
   - Not currently in `_quarto.yml` render list
   - Example: `Strokes_Gained_Limitations.qmd`

---

## Issues & Misplacements

### 1. **Duplicate Articles**

Some articles exist in both `articles/` and `content/`:

- `articles/force-mobility-matrices.qmd` vs `content/Affine Background Articles/Force_Mobility_Matrices.qmd`
- `articles/inverse-dynamics-inference.qmd` vs `content/Affine Background Articles/Inverse_Dynamics_Inference.qmd`
- `articles/lagrangian-reference.qmd` vs `content/Affine Background Articles/Lagrangian_Reference.qmd`
- `articles/nonlinear-control-insights.qmd` vs `content/Affine Background Articles/Nonlinear_Control_Insights.qmd`
- `articles/null-space-constraint-jacobian.qmd` vs `content/Affine Background Articles/null_space_constraint_jacobian.qmd`
- `articles/screw-theory-reference.qmd` vs `content/Affine Background Articles/ScrewTheory_Reference.qmd`

**Issue**: This creates confusion about which is the "source of truth"

### 2. **Mixed Source Files**

The `content/` folders contain both:

- `.qmd` files (Quarto articles - should be rendered)
- `.tex` files (LaTeX source - not rendered, just source material)

**Issue**: Unclear which files are active vs archived

### 3. **Articles Not in Render List**

These articles exist but aren't configured in `_quarto.yml`:

- `content/Double Pendulum Articles/Drift Components of Wrench in Double Pendulum.qmd`
- `content/Strokes Gained Limitations/Strokes_Gained_Limitations.qmd`

**Issue**: These won't be rendered automatically

### 4. **Draft/Archive Files Mixed with Active Content**

- `content/Affine Nature of the Golf Swing/Draft3_Compiled_Working_Copy.qmd` - "Draft" in name
- `content/Inverse Dynamics Analysis/Drafts/` - Draft folder
- `content/Wrist as Universal Joint/Archive/` - Archive folder

**Issue**: Unclear what's active vs draft vs archived

---

## Recommended Folder Structure

### Proposed Organization

```
AffineDrift/
├── articles/                    # PRIMARY: All published articles go here
│   ├── theory-part1.qmd
│   ├── theory-part2.qmd
│   ├── wrist-universal-joint.qmd
│   ├── inverse-dynamics.qmd
│   └── ... (all published articles)
│
├── content/                     # SOURCE MATERIAL: LaTeX sources, drafts, archives
│   ├── source/                  # LaTeX source files (.tex)
│   │   ├── Affine Background Articles/
│   │   ├── Affine Nature of the Golf Swing/
│   │   └── ...
│   │
│   ├── drafts/                 # Work-in-progress articles
│   │   └── ...
│   │
│   └── archive/                 # Archived/old versions
│       └── ...
│
├── tools/                       # Tools and utilities
├── scripts/                     # CI/CD and utility scripts
└── docs/                        # Rendered output (generated)
```

### Where to Add New Articles

**For new published articles:**

1. Create `.qmd` file in `articles/` directory
2. Add YAML frontmatter with title, author, date
3. Write content in Markdown with LaTeX equations
4. Article will automatically appear in `articles.html` when rendered

**For source material:**

- Keep LaTeX `.tex` files in `content/source/` (organized by topic)
- Keep drafts in `content/drafts/` until ready to publish
- Move to `articles/` when ready to publish

---

## Cleanup Recommendations

### Phase 1: Consolidate Duplicates

1. **Decide which version is canonical** for each duplicate article
2. **Remove duplicates** from `content/` folders (keep only in `articles/`)
3. **Move LaTeX sources** to `content/source/` for reference

### Phase 2: Organize Content Folder

1. **Create clear structure**:
   ```
   content/
   ├── source/          # LaTeX source files
   ├── drafts/          # Work-in-progress
   └── archive/         # Old/archived versions
   ```
2. **Move `.tex` files** to `content/source/`
3. **Move draft files** to `content/drafts/`
4. **Move archived files** to `content/archive/`

### Phase 3: Update Configuration

1. **Update `_quarto.yml`** to only render from `articles/`
2. **Remove `content/` paths** from render list (or keep only if needed)
3. **Update `articles.qmd`** to ensure all articles are listed

### Phase 4: Document Structure

1. **Create `articles/README.md`** (already exists - update if needed)
2. **Create `content/README.md`** explaining the structure
3. **Update main `README.md`** with folder structure explanation

---

## Quick Answer: Where to Add New Articles?

**✅ Add new published articles to: `articles/`**

Steps:

1. Create `articles/your-article-name.qmd`
2. Add YAML frontmatter:
   ```yaml
   ---
   title: "Your Article Title"
   author: "AffineDrift"
   date: "2025-01-26"
   ---
   ```
3. Write your content
4. Run `quarto render` or `quarto preview` to see it
5. Update `articles.qmd` to add it to the articles listing page

**The article will automatically be rendered and available at `articles/your-article-name.html`**

---

## Next Steps

1. **Review uncommitted files** - Decide what to commit
2. **Resolve duplicates** - Choose canonical versions
3. **Reorganize content/** - Move files to proper locations
4. **Update documentation** - Document the new structure
5. **Test rendering** - Ensure all articles still render correctly

Would you like me to help with any of these cleanup tasks?

# Final Repository Structure

## Clear Separation: Published vs Drafts

### `articles/` - **All Published Articles**

All published articles go here. This is the single source of truth for published content.

**Current articles (19 total):**

- Theory Parts 1-5
- Current studies (inverse-dynamics, wrist-universal-joint, superposition, controllability-drift-ratio, drift-components-wrench-double-pendulum, strokes-gained-limitations)
- Affine Nature of the Golf Swing series
- Affine Background Articles

**Workflow for new articles:**

1. Create draft in `content/drafts/`
2. Work on it there
3. When ready: `git mv content/drafts/my-article.qmd articles/my-article.qmd`
4. Update `articles.qmd` to add to listing
5. Done!

### `content/` - **Drafts & Supporting Materials**

**Purpose:**

- ✅ **Drafts** - Work-in-progress articles before publishing
- ✅ **Source materials** - LaTeX `.tex` files, Python scripts
- ✅ **Supporting documentation** - Technical reviews, validation notes
- ✅ **Media assets** - Images, PDFs, presentations
- ✅ **Archive** - Preserved duplicates and old versions

**Structure:**

```
content/
├── drafts/                    # Your work-in-progress articles
├── Inverse Dynamics Analysis/  # Analysis materials
├── Wrist as Universal Joint/   # Supporting materials
├── WSCG2024/                  # Conference materials
└── archive/                   # Archived content
    ├── duplicates/            # Duplicate articles (archived)
    ├── source/               # LaTeX source files
    └── drafts/               # Old drafts
```

## Benefits

1. **Clear workflow**: Drafts in `content/`, published in `articles/`
2. **No confusion**: One place for published articles
3. **Easy to find**: All published content in `articles/`
4. **Flexible**: `content/` can hold anything you're working on
5. **Clean**: Published content is separate from work-in-progress

## Configuration

**`_quarto.yml`** now only renders:

- `*.qmd` (root level pages)
- `articles/*.qmd` (all published articles)

No `content/` paths in render list - keeps it clean!

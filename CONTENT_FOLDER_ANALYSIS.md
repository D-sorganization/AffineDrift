# Content Folder Analysis: Should We Keep It?

## Current State

### Active Articles in `content/` (3 files)
1. `content/Affine Background Articles/Controllability_Drift_Ratio.qmd`
2. `content/Double Pendulum Articles/Drift Components of Wrench in Double Pendulum.qmd`
3. `content/Strokes Gained Limitations/Strokes_Gained_Limitations.qmd`

### Other Content in `content/`
- `archive/` - Archived duplicates, source files, drafts
- `Inverse Dynamics Analysis/` - Drafts, images, markdown files, LaTeX sources
- `Wrist as Universal Joint/` - Python scripts, images, LaTeX sources, documentation
- `WSCG2024/` - Conference materials (PDF, PPTX, images)
- `Front Page Matter/` - Introduction.md

## Recommendation: **Keep `content/` but move active articles to `articles/`**

### Why Keep `content/`?

The `content/` folder serves important purposes:

1. **Source Materials**: LaTeX files, Python scripts, supporting code
2. **Supporting Documentation**: Markdown docs, technical reviews, validation notes
3. **Drafts & Work-in-Progress**: Materials not yet ready for publication
4. **Media Assets**: Images, PDFs, presentations organized by topic
5. **Archive**: Preserved duplicates and old versions
6. **Specialized Materials**: Conference materials, analysis files, etc.

### What Should Move to `articles/`?

**All published articles should be in `articles/`**, including:
- `Controllability_Drift_Ratio.qmd` - If it's a published article
- `Drift Components of Wrench in Double Pendulum.qmd` - If it's a published article
- `Strokes_Gained_Limitations.qmd` - If it's a published article

### Proposed Structure

```
articles/                    # ALL published articles go here
├── theory-part1.qmd
├── theory-part2.qmd
├── ...
├── controllability-drift-ratio.qmd          # ← Move from content/
├── drift-components-wrench-double-pendulum.qmd  # ← Move from content/
└── strokes-gained-limitations.qmd           # ← Move from content/

content/                     # Source materials, supporting files, archive
├── archive/                  # Archived duplicates, source files, drafts
├── Inverse Dynamics Analysis/  # Analysis materials, drafts, images
├── Wrist as Universal Joint/   # Python scripts, LaTeX sources, docs
├── WSCG2024/                  # Conference materials
└── Front Page Matter/         # Supporting content
```

## Action Items

### Option 1: Move Active Articles to `articles/` (Recommended)
1. Move the 3 active `.qmd` files from `content/` to `articles/`
2. Update `_quarto.yml` to remove `content/Affine Background Articles/*.qmd`
3. Update `articles.qmd` to include the new articles in the listing
4. Keep `content/` for source materials and supporting files

### Option 2: Keep Everything in `content/`
- Keep articles in `content/` if they're not meant to be main published articles
- Use `content/` for specialized/supplementary content
- Keep `articles/` only for core published articles

## My Recommendation

**Move the 3 active articles to `articles/`** because:
- Consistency: All published articles should be in one place
- Clarity: `articles/` = published, `content/` = source/supporting materials
- Simplicity: Easier to find and manage published content
- Quarto rendering: All articles in one location is cleaner

**Keep `content/`** for:
- Source files (LaTeX, Python)
- Supporting documentation
- Drafts
- Media assets
- Archive
- Specialized materials

This gives you a clear separation: **published articles** vs **source/supporting materials**.

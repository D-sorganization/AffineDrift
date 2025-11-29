# Content Directory

This directory contains source material, drafts, and archived content for the AffineDrift website.

## Structure

```
content/
├── Affine Background Articles/     # Active background articles
│   └── Controllability_Drift_Ratio.qmd
│
├── Double Pendulum Articles/       # Specialized articles
│   └── Drift Components of Wrench in Double Pendulum.qmd
│
├── Strokes Gained Limitations/     # Specialized articles
│   └── Strokes_Gained_Limitations.qmd
│
├── Inverse Dynamics Analysis/      # Analysis materials and drafts
│   └── Drafts/                     # Draft versions
│
├── Wrist as Universal Joint/      # Wrist analysis materials
│   └── Archive/                    # Archived versions
│
├── WSCG2024/                       # Conference materials
│
└── archive/                        # Archived content (see archive/README.md)
    ├── duplicates/                 # Duplicate articles
    ├── source/                     # LaTeX source files
    └── drafts/                     # Draft articles
```

## Active Content

### Published Articles
**All published articles are in the `articles/` directory**, not here. This directory contains:
- Source material (LaTeX files, drafts)
- Specialized articles not yet in the main articles list
- Supporting materials

### Active Quarto Articles

These `.qmd` files are currently active:
- `Affine Background Articles/Controllability_Drift_Ratio.qmd` - Background article
- `Double Pendulum Articles/Drift Components of Wrench in Double Pendulum.qmd` - Specialized article
- `Strokes Gained Limitations/Strokes_Gained_Limitations.qmd` - Specialized article

**Note**: Some of these may not be in the `_quarto.yml` render list. Check `_quarto.yml` to see which are configured for rendering.

## Adding New Content

### For Published Articles
**Add new published articles to `articles/`**, not here. See `articles/README.md` for instructions.

### For Source Material
- Keep LaTeX `.tex` files here organized by topic
- Keep drafts in subdirectories until ready to publish
- Move to `articles/` when ready to publish

### For Specialized Content
- Use topic-specific subdirectories (like `Double Pendulum Articles/`)
- Update `_quarto.yml` if you want them rendered automatically
- Or link to them manually from other pages

## Archive

See `archive/README.md` for details about archived content, including:
- What was archived and why
- How to recover archived files
- Archive structure


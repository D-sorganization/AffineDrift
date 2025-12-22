# Content Directory

This directory contains **drafts, source materials, and supporting content** for the AffineDrift website.

## Purpose

**`content/` is for work-in-progress, not published articles.**

- ✅ **Drafts** - Articles you're working on before publishing
- ✅ **Source materials** - LaTeX files, Python scripts, supporting code
- ✅ **Supporting documentation** - Technical reviews, validation notes
- ✅ **Media assets** - Images, PDFs, presentations organized by topic
- ✅ **Archive** - Preserved duplicates and old versions

**All published articles go in `articles/`**, not here.

## Structure

```
content/
├── Inverse Dynamics Analysis/      # Analysis materials and drafts
│   └── Drafts/                     # Draft versions
│
├── Wrist as Universal Joint/      # Wrist analysis materials
│   └── Archive/                    # Archived versions
│
├── WSCG2024/                       # Conference materials
│
├── Front Page Matter/              # Supporting content
│
└── archive/                        # Archived content (see archive/README.md)
    ├── duplicates/                 # Duplicate articles
    ├── source/                     # LaTeX source files
    └── drafts/                     # Draft articles
```

## Using Content/ for Drafts

**Recommended workflow:**

1. **Create drafts in `content/`** - Work on articles here while developing
   ```
   content/drafts/my-new-article.qmd
   ```

2. **When ready to publish** - Move to `articles/`
   ```bash
   git mv content/drafts/my-new-article.qmd articles/my-new-article.qmd
   ```

3. **Update `articles.qmd`** - Add the article to the listing page

4. **Render and publish** - The article will be rendered automatically

This keeps your published content clean and organized while giving you a place to work on drafts.

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

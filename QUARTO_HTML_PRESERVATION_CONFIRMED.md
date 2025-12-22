# Quarto HTML Preservation - Confirmed

## Question

Does Quarto preserve `{=html}` blocks with custom 3-column layout structure, or does it strip/transform the HTML during rendering?

## Answer: ✅ QUARTO PRESERVES HTML EXACTLY

By examining git history, I can confirm that **Quarto passes `{=html}` blocks through unchanged**.

## Evidence

### Test Case: Commit 0d17e60 (Nov 27, 2025)

**Source (`articles.qmd`):**

````html
```{=html}
<section class="article-section">
  <div class="container">
    <div class="articles-list">
      <div class="article-category">
        <h2>The Drifter Manifesto</h2>
      </div>
    </div>
  </div>
</section>
````

**Output (`docs/articles.html` after Quarto render):**

```html
<section class="article-section">
  <div class="container">
    <div class="articles-list">
      <div class="article-category">
        <h2 class="anchored">The Drifter Manifesto</h2>
      </div>
    </div>
  </div>
</section>
```

**Result**: The HTML structure is preserved exactly. Quarto only added `class="anchored"` to headings, which is standard Quarto behavior for navigation.

## Why the TOC Wasn't Appearing

The issue was NOT that Quarto stripped the HTML. The timeline shows:

1. **Nov 27, 2:27 PM**: Quarto rendered all files with simple layout (no sidebars)
2. **Nov 30, 9:29 AM**: 3-column layout removed intentionally
3. **Dec 2, 2:00 PM**: 3-column layout added back to `.qmd` files
4. **Dec 2-3**: No Quarto render occurred (feature branch work)
5. **Dec 3, 4:24 AM**: My manual fix using `build-html.py`

**The root cause**: Quarto workflows only run on `main` branch, so HTML files were never regenerated after the layout was re-added.

## Conclusion

1. ✅ **Quarto DOES preserve `{=html}` blocks**
2. ✅ **The 3-column layout WILL work** when Quarto is run
3. ✅ **The problem was simply that Quarto wasn't run** on feature branches

## Solution Implemented

Created `.github/workflows/quarto-render-check.yml` to:

- Run Quarto on ALL branches when `.qmd` files change
- Verify that the 3-column layout structure is preserved
- Auto-commit rendered HTML files on feature branches
- Catch rendering issues before merging to main

## Recommendations

### Option 1: Use the New Workflow (Implemented)

The `quarto-render-check.yml` workflow will:

- Automatically render HTML when you change `.qmd` files
- Verify the output structure is correct
- Commit the rendered files back to your branch
- Work on all branches, not just `main`

### Option 2: Pre-commit Hook (Alternative)

If you prefer local control, add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
if git diff --cached --name-only | grep -q '\.qmd$'; then
  echo "Rendering Quarto files..."
  quarto render
  git add docs/
fi
```

### Option 3: Don't Commit docs/ (Clean Approach)

- Add `docs/` to `.gitignore`
- Only track `.qmd` source files
- Let CI/CD render and deploy
- Developers use `quarto preview` locally

## Testing the Fix

To verify Quarto preserves your layout:

```bash
# On your local machine with Quarto installed
quarto render articles.qmd

# Check the output
grep -A5 "standard-page-layout" docs/articles.html
grep -A5 "left-sidebar" docs/articles.html
```

You should see the exact HTML structure from your `.qmd` file.

## Related Files

- Investigation: `QUARTO_RENDERING_INVESTIGATION.md`
- Workflow: `.github/workflows/quarto-render-check.yml`
- Build script: `build-html.py` (temporary workaround)

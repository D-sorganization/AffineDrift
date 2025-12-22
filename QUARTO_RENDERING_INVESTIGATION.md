# Quarto Rendering Investigation Summary

## Problem Statement

The table of contents (TOC) was not appearing in the left sidebar throughout the site, despite the `.qmd` source files containing the correct 3-column layout structure with `left-sidebar`, `main-content-area`, and `right-sidebar`.

## Root Cause Analysis

### Discovery 1: Mismatch Between Source and Output

**Source files (`.qmd`)**: Contained the correct structure
```html
<div class="standard-page-layout">
  <aside class="left-sidebar">
    <nav class="toc-nav">...</nav>
  </aside>
  <main class="main-content-area">...</main>
  <aside class="right-sidebar">...</aside>
</div>
```

**Output files (`docs/*.html`)**: Missing the sidebar structure entirely
```html
<div class="articles-list">
  <div class="article-category">...</div>
</div>
```

### Discovery 2: Files Were Never Rendered

Investigation of git history revealed:

1. **Commit 697cf51 (Nov 2025)**: 3-column layout was added to `.qmd` files
   - Changes made to: `articles.qmd`, `models*.qmd`, `resources-*.qmd`
   - Sidebars and 3-column structure added to all these files

2. **Commit 1ddbccf**: Last change to `docs/articles.html`
   - Only changed script.js path (1 line)
   - NOT a Quarto render

3. **Missing HTML files**: 15 files never existed in git
   - `docs/models.html` + 7 model-specific pages
   - 6 resource-specific pages
   - These were created for the first time in commit b5a59e2

### Discovery 3: Quarto Workflows Only Run on Main Branch

The Quarto rendering workflows (`.github/workflows/quarto-publish.yml` and `.github/workflows/deploy.yml`) only run when:

```yaml
on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
```

This means:
- Changes to `.qmd` files on feature branches are NOT automatically rendered
- The `docs/*.html` files must be manually kept in sync, OR
- The files are only rendered when merged to main

### Discovery 4: The Files Were Outdated

Timeline:
1. Commit 0d17e60: Last full Quarto render before sidebar changes
   - `docs/articles.html` had NO sidebars (correct for that time)
2. Commit 697cf51: Sidebars ADDED to `articles.qmd` on feature branch
   - Quarto did NOT run (feature branch)
   - `docs/articles.html` never updated
3. Commit 1ddbccf: Manual edit to fix script.js path
   - Still no Quarto render
4. Present: HTML files still contain pre-sidebar structure

## Why Quarto Didn't Transform the HTML

The investigation revealed that **Quarto was never run** after the sidebars were added, so the question "Does Quarto strip `{=html}` blocks?" remains **unanswered**.

However, based on Quarto documentation:
- `{=html}` blocks should be passed through unchanged to the output
- This is the documented way to include raw HTML in Quarto documents
- The syntax is correct in the `.qmd` files

## The Temporary Fix

Since Quarto couldn't be installed in the current environment, a workaround was implemented:

1. Created `build-html.py` script that:
   - Extracts `{=html}` blocks from `.qmd` files
   - Uses existing `docs/articles.html` as a template
   - Replaces content sections while preserving Quarto's header/footer
   - Generates all missing HTML files

2. This successfully created 16 HTML files with the correct 3-column layout structure

## The Proper Solution

To properly fix this issue long-term:

### Option 1: Render on Feature Branches (Recommended)

Add a workflow that runs Quarto on all branches:

```yaml
# .github/workflows/quarto-render-check.yml
name: Quarto Render Check
on:
  push:
    branches:
      - '**'  # All branches
  pull_request:
jobs:
  render:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: quarto-dev/quarto-actions/setup@v2
        with:
          version: 1.4.549
      - name: Render site
        run: quarto render
      - name: Check for changes
        run: |
          git add docs/
          git diff --staged --stat
```

This would:
- Automatically render HTML when `.qmd` files change
- Catch rendering issues before merging to main
- Keep `docs/` folder always in sync

### Option 2: Don't Commit docs/ Folder

Alternative approach:
1. Add `docs/` to `.gitignore`
2. Only track `.qmd` source files in git
3. Let CI/CD render and deploy directly
4. Developers preview locally with `quarto preview`

This is cleaner but requires CI/CD for all deployments.

### Option 3: Pre-commit Hook

Add a git pre-commit hook that:
```bash
#!/bin/bash
# .git/hooks/pre-commit
if git diff --cached --name-only | grep -q '\.qmd$'; then
  echo "Rendering Quarto files..."
  quarto render
  git add docs/
fi
```

This ensures `docs/` is always updated when `.qmd` changes.

## Testing the Quarto HTML Processing

To verify that Quarto properly preserves `{=html}` blocks:

1. Install Quarto locally
2. Run `quarto render articles.qmd`
3. Compare `docs/articles.html` output to source
4. Verify that `<div class="standard-page-layout">` and sidebars are preserved

If Quarto strips the structure, alternative approaches:
- Use Quarto's built-in sidebar features instead of custom HTML
- Configure Quarto templates to include the 3-column layout
- Use Quarto includes/partials for the sidebar structure

## Recommendations

1. **Immediate**: The current fix (build-html.py) works but is a workaround
2. **Short-term**: Add Quarto rendering to feature branch workflow (Option 1)
3. **Long-term**: Consider using Quarto's native sidebar/layout features instead of custom HTML
4. **Documentation**: Update QUARTO_LOCAL_TESTING.md to reflect actual workflow

## Open Questions

1. Does Quarto actually preserve the `{=html}` blocks with the 3-column structure?
   - Answer requires running Quarto render to verify
2. Why was `docs/` committed with outdated files instead of being rendered on merge?
   - Possible workflow gap or manual intervention
3. Should `docs/` be in git at all, or only generated by CI/CD?
   - Design decision for the team

## References

- Quarto raw HTML blocks: https://quarto.org/docs/authoring/markdown-basics.html#raw-content
- Quarto page layouts: https://quarto.org/docs/output-formats/page-layout.html
- Commit 697cf51: Added 3-column layout to .qmd files
- Commit b5a59e2: Generated HTML files with build-html.py script

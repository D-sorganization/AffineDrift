# Website Analysis Report: Dead Links & Items to Archive

**Date**: November 26, 2025
**Branch**: claude/fix-quarto-equations-01MdB1MLoz71dWc71wjFq3cc

## Critical Issues

### 1. Broken Logo Link
**File**: `resources.html:45`
**Issue**: References non-existent path `logo/logo-transparent/logo.png`
**Fix**: Change to `logo/Logo Transparent/1.png`

### 2. Articles Page - Remaining Meta Bubbles
**File**: `articles.html` (Background Articles section)
**Issue**: Still has `<div class="article-meta">` bubbles that should be removed
**Lines**: 128-165 (Background Articles section)

## Pages with Outdated Navigation

The following pages still use old navigation structure and should be updated:

### Pages with Old Nav (not matching current index.html):
1. **book-reviews.html** - Has: Theory, Modelling, WSCG 2024, Book Reviews, Daydreams & Doodles
2. **contact.html** - Has old nav links
3. **daydreams-doodles.html** - Has old nav
4. **modelling.html** - Has old nav
5. **research-reviews.html** - Has old nav
6. **theory-part1.html** through **theory-part5.html** - Has old nav
7. **theory.html** - Has old nav
8. **wscg-research.html** - Has old nav

### Current Navigation Should Be:
- Affine Drift (index.html)
- Articles (articles.html)
- Reviews (research-reviews.html)
- Resources (resources.html)
- Contact (contact.html)
- About (about.html)

## Orphaned/Inaccessible Pages

These pages exist but are NOT in the main navigation:

1. **book-reviews.html** - Book reviews page
   - Only accessible from old nav pages
   - Decision needed: Add to nav or archive?

2. **daydreams-doodles.html** - Casual thoughts/ideas
   - Only accessible from old nav pages
   - Decision needed: Add to nav or archive?

3. **theory.html** - Appears to be umbrella page
   - May be redundant with articles.html
   - Has old navigation

4. **Reference Pages** (accessible via articles.html):
   - force-mobility-matrices.html
   - inverse-dynamics-inference.html
   - lagrangian-reference.html
   - nonlinear-control-insights.html
   - null-space-constraint-jacobian.html
   - screw-theory-reference.html
   - These are properly linked from articles.html

## Content Directory Items

### Potentially Archivable Content

**Multiple versions of same content:**
- `content/Wrist as Universal Joint/`
  - Wrist_Universal_ChatGPT.tex
  - Wrist_Universal_Gemini.tex
  - Wrist_Universal_GeminiCombined.tex
  - Wrist_Universal_GrokCombined.tex
  - Wrist_Universal_GrokCombined_2.tex
  - **Current**: Wrist_Universal_Claude.tex (converted to .html and .qmd)

**Recommendation**: Archive all except Claude version

**Inverse Dynamics drafts:**
- Multiple ChatGPT and Gemini versions
- Archive folder exists but may need more organization

## Logo Issues

**Multiple logo files in root:**
- AffineDriftLogo.png (324K)
- AffineDriftLogoText.png (37K)
- AffineDriftLogo_Clean.png (268K)

**Logo directories:**
- logo/Logo Normal/
- logo/Logo Transparent/ (used in current pages)

**Issue**: Inconsistent logo references
- Most pages use: `logo/Logo Transparent/1.png`
- resources.html incorrectly uses: `logo/logo-transparent/logo.png`

## Recommendations

### Immediate Actions Required:

1. **Fix broken logo link** in resources.html
2. **Remove meta bubbles** from articles.html Background Articles section
3. **Update navigation** on all pages to match current structure
4. **Decide on book-reviews.html and daydreams-doodles.html**:
   - Option A: Add to main navigation
   - Option B: Archive or remove

### Archive Candidates:

1. **Content directory cleanup**:
   ```
   content/Wrist as Universal Joint/Archive/
   ├── Wrist_Universal_ChatGPT.tex
   ├── Wrist_Universal_Gemini.tex
   ├── Wrist_Universal_GeminiCombined.tex
   ├── Wrist_Universal_GrokCombined.tex
   └── Wrist_Universal_GrokCombined_2.tex
   ```

2. **Consider creating Archive/ in root for**:
   - theory.html (if redundant)
   - Old versions of converted pages

### Long-term Improvements:

1. **Consolidate logos** - decide on single logo style
2. **Remove unused logo files**
3. **Create consistent navigation include** (or use Quarto for entire site)
4. **Add 404 page** for broken links
5. **Add sitemap.xml** for SEO

## Summary Statistics

- **Total HTML pages**: 27
- **Pages with current navigation**: 5 (index, articles, about, resources, reading-list)
- **Pages with old navigation**: 12
- **Orphaned pages**: 2-3 (depending on decisions)
- **Critical broken links**: 1 (resources.html logo)
- **Minor issues**: Meta bubbles in articles.html

## Priority Fixes

**High Priority**:
1. Fix resources.html logo path
2. Update navigation on all theory pages (part1-5)
3. Remove article-meta from articles.html

**Medium Priority**:
1. Update navigation on modelling, wscg-research, research-reviews
2. Decide fate of book-reviews and daydreams-doodles
3. Archive old content versions

**Low Priority**:
1. Consolidate logo files
2. Archive theory.html if redundant
3. Create systematic archive structure

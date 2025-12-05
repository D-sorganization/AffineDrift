# Website Update Plan

## Overview
This document outlines the comprehensive plan for updating the AffineDrift website with all requested changes. Each task includes specific implementation details and verification steps.

---

## 1. Researchers Section Updates

### 1.1 Add Rob Neal
**File**: `resources-researchers.qmd`
- **Links to add**:
  - Wedgecraft: https://wedgecraft.com/dr-robert-neal/
  - World Class Golf: [To be confirmed - may be Golf BioDynamics: https://golfbiodynamics.com/]
  - Google Scholar: [Search for exact profile URL]
- **Location**: Add new resource card after existing researchers
- **Format**: Match existing researcher card structure with image, description, and links
- **Bio**: Dr. Robert Neal is a world-renowned biomechanist and co-founder of WedgeCraft, a wedge play data collective committed to developing a comprehensive model for learning the short game through coaching and science-based methods.

### 1.2 Add Steven Nesbit
**File**: `resources-researchers.qmd`
- **Links to add**:
  - Jacobs3dGolf: https://www.jacobs3dgolf.com/ (or https://jacobs3d.com/)
  - Google Scholar: [Search for exact profile URL]
- **Location**: Add new resource card after Rob Neal
- **Format**: Match existing researcher card structure
- **Bio**: Dr. Steven M. Nesbit is a professor of mechanical engineering with extensive research in golf biomechanics, including kinematic and kinetic studies of the golf swing.

### 1.3 Remove Researchers Home Page
**File**: `resources.qmd` and `_quarto.yml`
- Remove "Resources Home" link from researchers navigation
- Update navbar in `_quarto.yml` to remove "Resources Home" from Resources menu
- Ensure direct links to all resource sub-pages work correctly

**Status**: ⬜ Pending

---

## 2. Homepage Equation Formatting

### 2.1 Fix Equation Rendering
**File**: `index.qmd`
- **Issue**: Equations showing with `$` symbols instead of rendering
- **Solution**: 
  - Review all equations in `index.qmd` (lines 82, 111, 116-129, 161, 198, 206)
  - Convert all inline math from `$...$` to `\(...\)` or ensure proper MathJax delimiters
  - Convert all display math from `$$...$$` to `\[...\]` or `<div class="equation">` blocks
  - Ensure equations are properly escaped and formatted
  - Test rendering after changes

**Status**: ⬜ Pending

---

## 3. Repository Dropdown Updates

### 3.1 Update Repository Links
**File**: `_quarto.yml` (lines 64-77)
- **Current**: Links to repository home pages
- **Required**: Direct links to actual repositories
- **Changes needed**:
  - Replace "Repositories Home" with actual GitHub organization/repo links
  - Add organization name for user's repos
  - Add common repos:
    - MyoSim: [GitHub URL]
    - MuJoCo: [GitHub URL]
    - Other resources primarily sourced via repository
- **Format**: Keep dropdown structure but update hrefs to actual repo URLs

**Status**: ⬜ Pending

---

## 4. Layout Standardization (Videos Page Model)

### 4.1 Videos Page Layout Analysis
**File**: `resources-videos.qmd`
- **Current structure**:
  - Title: "Videos" (h2.section-heading)
  - Single column layout
  - No left/right sidebars currently
  - Clean, simple design

### 4.2 Target Layout Structure
**Required layout for all pages**:
- **Left Sidebar**: Table of contents / category navigation
- **Main Content**: Single column, full width (like Videos page)
- **Right Sidebar**: History of recent pages visited (per resource type)
- **Title**: Move up to just under menu bar (reduce wasted space)
- **Title Style**: Match "Videos" heading style (elegant, clean)

### 4.3 Pages Requiring Layout Updates

#### 4.3.1 Models Pages
- [ ] `models.qmd` - Main models page
- [ ] `models-simulink.qmd`
- [ ] `models-mujoco.qmd`
- [ ] `models-drake.qmd`
- [ ] `models-pinnochio.qmd`
- [ ] `models-pendulum.qmd`
- [ ] `models-opensim.qmd`
- [ ] `models-myosim.qmd`

**Implementation**:
- Add left sidebar with model categories (table of contents)
- Add right sidebar with recent model pages visited
- Update title positioning
- Ensure single column content layout

#### 4.3.2 Resources Pages
- [ ] `resources.qmd` - Resources home (remove or update)
- [ ] `resources-videos.qmd` - Add left/right sidebars
- [ ] `resources-software.qmd`
- [ ] `resources-websites.qmd`
- [ ] `resources-datasets.qmd`
- [ ] `resources-books.qmd`
- [ ] `resources-papers.qmd`
- [ ] `resources-researchers.qmd`

**Implementation**:
- Left sidebar: Category navigation (table of contents)
- Right sidebar: History of pages visited in that resource type
- Middle section: Categories separated by category titles
- Single column layout for content

#### 4.3.3 Articles Pages
- [ ] `articles.qmd` - Main articles page
- [ ] Individual article pages in `articles/` directory

**Implementation**:
- Left sidebar: Article topics/categories (table of contents)
- Right sidebar: Recent articles visited
- Categories in middle section with category titles
- Single column layout

**Status**: ⬜ Pending

---

## 5. Fix "Affine Drift Matters" Repetition

### 5.1 Locate and Fix
**File**: `_quarto.yml` (lines 158-161)
- **Issue**: "Affine Drift matters" appears twice in footer
- **Current**:
  ```yaml
  <p>&copy; 2025. Affine Drift Effin Matters.</p>
  <p class="footer-tagline">2025 AffineDrift matters</p>
  ```
- **Fix**: Remove duplicate, keep one version
- **Check**: All rendered HTML pages for footer content

**Status**: ⬜ Pending

---

## 6. RSS Feed Implementation

### 6.1 Add RSS Feed
**Location**: Near search bar in header
- **File**: `_templates/partials/header.html` or `_quarto.yml`
- **Implementation**:
  - Create `feed.xml` or `rss.xml` for static site
  - Add RSS icon/link next to search bar
  - Generate feed from articles metadata
  - Ensure compatibility with GitHub Pages (static hosting)
  - Use Quarto's built-in RSS support if available, or generate manually

**Status**: ⬜ Pending

---

## 7. Remove Three-Column Layouts

### 7.1 Sitewide Check
**Action**: Scroll through entire site and identify all three-column layouts
- **Files to check**: All `.qmd` files and rendered HTML
- **Replace with**: Single column layout matching Videos page
- **Width and layout**: Match Videos page exactly

**Status**: ⬜ Pending

---

## 8. Add Video Links

### 8.1 Dead Fish Swimming Upstream
**File**: `resources-videos.qmd`
- **URL**: https://fyfluiddynamics.com/2018/07/when-i-was-a-child-my-father-would-take-me-trout/
- **Action**: 
  - Add new video card with link
  - Research and add link to original paper if available (may need to search article for paper reference)
  - Format: Match existing video card structure
  - Title: "Dead Fish Swimming Upstream" or similar descriptive title

**Status**: ⬜ Pending

---

## 9. Add Grip Papers

### 9.1 Papers to Add
**File**: `resources-papers.qmd`
- **Choi and Park instrumented grip papers**: [Find and add]
- **Koike instrumented grip paper**: [Find and add]
- **Vaughan papers (1 and 2) on closed loop constraints on the grip**: [Find and add]
- **Format**: Match existing paper card structure

**Status**: ⬜ Pending

---

## 10. Articles Page Updates

### 10.1 Change "Current Studies" to "Articles"
**File**: `articles.qmd` (line 66)
- **Current**: `<h2>Current studies</h2>`
- **Change to**: `<h2>Articles</h2>`
- **Also update**: Sidebar navigation link (line 301)

**Status**: ⬜ Pending

### 10.2 Remove Appendix Labels
**File**: `articles.qmd` (lines 168, 178, 188, 198, 208)
- **Current**: "Appendix A:", "Appendix B:", etc.
- **Change to**: Remove "Appendix" prefix, keep descriptive titles
- **Examples**:
  - "Appendix A: Nonlinear Control Insights" → "Nonlinear Control Insights"
  - "Appendix B: Inverse Dynamics Inference" → "Inverse Dynamics Inference"
  - etc.

**Status**: ⬜ Pending

---

## 11. Fix Previews

### 11.1 Book Previews
**File**: `resources-books.qmd`
- **Issue**: Preview images not working
- **Action**: 
  - Check all book preview image sources
  - Update to working URLs from Google Books API, Amazon, or other sources
  - Ensure proper image tags and error handling

### 11.2 Article Previews
**File**: Article pages in `articles/` directory
- **Issue**: Preview images not working
- **Action**: 
  - Add preview images from appropriate sources
  - Ensure images load correctly

### 11.3 Website Previews
**File**: `resources-websites.qmd`
- **Issue**: Previews flash and disappear
- **Action**: 
  - Fix preview iframe/embed code
  - Ensure proper loading and display
  - Check for CORS or security issues

**Status**: ⬜ Pending

---

## Implementation Checklist

### Phase 1: Content Updates
- [ ] Add Rob Neal to researchers
- [ ] Add Steven Nesbit to researchers
- [ ] Remove researchers home page
- [ ] Add dead fish video
- [ ] Add grip papers (Choi/Park, Koike, Vaughan)
- [ ] Change "Current Studies" to "Articles"
- [ ] Remove appendix labels

### Phase 2: Layout Standardization
- [ ] Update Videos page with left/right sidebars
- [ ] Update all Models pages
- [ ] Update all Resources pages
- [ ] Update Articles page
- [ ] Remove three-column layouts sitewide
- [ ] Fix title positioning (move up under menu)

### Phase 3: Technical Fixes
- [ ] Fix homepage equations
- [ ] Update repository dropdown links
- [ ] Fix "Affine Drift matters" repetition
- [ ] Add RSS feed
- [ ] Fix book previews
- [ ] Fix article previews
- [ ] Fix website previews

### Phase 4: Verification
- [ ] Sitewide layout check
- [ ] All pages match Videos page layout
- [ ] All links work correctly
- [ ] All previews function
- [ ] Equations render properly
- [ ] RSS feed works
- [ ] No broken layouts remain

---

## Notes

1. **Videos Page as Model**: The Videos page layout should be the standard for all pages. Study its structure carefully before applying to other pages.

2. **Left Sidebar**: Table of contents for categories/topics
3. **Right Sidebar**: History of recent pages (per resource type)
4. **Title Position**: Move up to just under menu bar
5. **Single Column**: All content in single column, full width

6. **Testing**: After each phase, test locally and verify all changes work correctly.

7. **GitHub Pages**: Ensure all changes work with static site hosting (no server-side processing).

---

## Priority Order

1. **High Priority**: Layout standardization (affects user experience)
2. **Medium Priority**: Content updates (researchers, papers, videos)
3. **Medium Priority**: Technical fixes (equations, previews, RSS)
4. **Low Priority**: Minor text changes (appendix labels, "Current Studies")

---

**Last Updated**: [Date]
**Status**: Planning Phase


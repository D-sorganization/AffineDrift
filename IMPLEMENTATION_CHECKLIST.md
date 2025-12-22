# Website Update Implementation Checklist

This checklist should be used to track progress on all website updates. Check off items as they are completed.

## Quick Reference: Key URLs Found

### Researchers
- **Rob Neal**:
  - Wedgecraft: https://wedgecraft.com/dr-robert-neal/
  - Golf BioDynamics: https://golfbiodynamics.com/
  - Google Scholar: [To be searched]
- **Steven Nesbit**:
  - Jacobs3dGolf: https://www.jacobs3dgolf.com/
  - Google Scholar: [To be searched]

### Repositories
- **Organization**: D-sorganization (based on existing repos)
- **Common Repos to Add**:
  - MyoSim: https://github.com/myosim/myosim (verify)
  - MuJoCo: https://github.com/deepmind/mujoco (verify)

### Video
- **Dead Fish**: https://fyfluiddynamics.com/2018/07/when-i-was-a-child-my-father-would-take-me-trout/

---

## Phase 1: Content Updates

### Researchers Section
- [ ] Add Rob Neal card to `resources-researchers.qmd`
  - [ ] Add biography text
  - [ ] Add Wedgecraft link
  - [ ] Add World Class Golf or Golf BioDynamics link
  - [ ] Add Google Scholar link
  - [ ] Add profile image (if available)
- [ ] Add Steven Nesbit card to `resources-researchers.qmd`
  - [ ] Add biography text
  - [ ] Add Jacobs3dGolf link
  - [ ] Add Google Scholar link
  - [ ] Add profile image (if available)
- [ ] Remove "Resources Home" from researchers navigation
  - [ ] Update `resources-researchers.qmd` sidebar
  - [ ] Update `_quarto.yml` navbar (remove "Resources Home" from Resources menu)

### Papers Section
- [ ] Add Choi and Park instrumented grip papers to `resources-papers.qmd`
- [ ] Add Koike instrumented grip paper to `resources-papers.qmd`
- [ ] Add Vaughan papers (1 and 2) on closed loop constraints to `resources-papers.qmd`

### Videos Section
- [ ] Add "Dead Fish Swimming Upstream" video to `resources-videos.qmd`
  - [ ] Add video card with proper formatting
  - [ ] Research and add link to original paper (if available)

### Articles Page
- [ ] Change "Current studies" to "Articles" in `articles.qmd` (line 66)
- [ ] Update sidebar link from "Current Studies" to "Articles" (line 301)
- [ ] Remove "Appendix" labels from article titles in `articles.qmd`
  - [ ] "Appendix A: Nonlinear Control Insights" → "Nonlinear Control Insights"
  - [ ] "Appendix B: Inverse Dynamics Inference" → "Inverse Dynamics Inference"
  - [ ] "Appendix C: Applications" → "Applications"
  - [ ] "Appendix D: Lagrangian Reference" → "Lagrangian Reference"
  - [ ] "Appendix E: Screw Theory Reference" → "Screw Theory Reference"

---

## Phase 2: Layout Standardization

### Videos Page (Model Layout)
- [ ] Review current Videos page layout (`resources-videos.qmd`)
- [ ] Add left sidebar with category navigation (if categories exist)
- [ ] Add right sidebar with recent videos history
- [ ] Adjust title position (move up under menu bar)
- [ ] Ensure single column content layout

### Models Pages
- [ ] `models.qmd` - Apply Videos page layout
  - [ ] Add left sidebar (table of contents for model categories)
  - [ ] Add right sidebar (recent model pages visited)
  - [ ] Adjust title position
  - [ ] Ensure single column layout
- [ ] `models-simulink.qmd` - Apply layout
- [ ] `models-mujoco.qmd` - Apply layout
- [ ] `models-drake.qmd` - Apply layout
- [ ] `models-pinnochio.qmd` - Apply layout
- [ ] `models-pendulum.qmd` - Apply layout
- [ ] `models-opensim.qmd` - Apply layout
- [ ] `models-myosim.qmd` - Apply layout

### Resources Pages
- [ ] `resources.qmd` - Update or remove (if redundant)
- [ ] `resources-videos.qmd` - Add sidebars, adjust layout
- [ ] `resources-software.qmd` - Apply layout
  - [ ] Left sidebar: Software categories
  - [ ] Right sidebar: Recent software pages
  - [ ] Categories in middle section
- [ ] `resources-websites.qmd` - Apply layout
  - [ ] Left sidebar: Website categories
  - [ ] Right sidebar: Recent website pages
  - [ ] Categories in middle section
- [ ] `resources-datasets.qmd` - Apply layout
- [ ] `resources-books.qmd` - Apply layout
  - [ ] Left sidebar: Book categories
  - [ ] Right sidebar: Recent book pages
  - [ ] Categories in middle section
- [ ] `resources-papers.qmd` - Apply layout
  - [ ] Left sidebar: Paper categories
  - [ ] Right sidebar: Recent paper pages
  - [ ] Categories in middle section
- [ ] `resources-researchers.qmd` - Apply layout
  - [ ] Left sidebar: Researcher categories (if any)
  - [ ] Right sidebar: Recent researcher pages
  - [ ] Ensure single column layout

### Articles Pages
- [ ] `articles.qmd` - Apply layout
  - [ ] Left sidebar: Article topics/categories (table of contents)
  - [ ] Right sidebar: Recent articles visited
  - [ ] Categories in middle section with category titles
  - [ ] Single column layout
- [ ] Individual article pages in `articles/` directory
  - [ ] Ensure consistent layout across all articles

### Layout Requirements (All Pages)
- [ ] Title style matches "Videos" page (elegant, clean)
- [ ] Title positioned just under menu bar (reduce wasted space)
- [ ] Left sidebar: Table of contents / category navigation
- [ ] Right sidebar: History of recent pages (per resource type)
- [ ] Main content: Single column, full width
- [ ] No three-column layouts remain anywhere

---

## Phase 3: Technical Fixes

### Homepage Equations
- [ ] Review all equations in `index.qmd`
- [ ] Fix equation on line 82: `$\dot{x} = f(x) + g(x)u$`
- [ ] Fix equation on line 111: `$$\dot{x} = f(x) + g(x)u$$`
- [ ] Fix equations in explanation section (lines 116-129)
- [ ] Fix equation on line 161: `$f(x)$`
- [ ] Fix equation on line 198: `$f(x)$`
- [ ] Fix equation on line 206: `$g(x)$`
- [ ] Test all equations render correctly
- [ ] Ensure no `$` symbols visible in rendered output

### Repository Dropdown
- [ ] Update `_quarto.yml` Repositories menu (lines 64-77)
- [ ] Replace "Repositories Home" with direct repo links
- [ ] Add organization name (D-sorganization) for user repos
- [ ] Add MyoSim repository link
- [ ] Add MuJoCo repository link
- [ ] Add other common repos (as needed)
- [ ] Keep dropdown structure but update all hrefs

### Footer Duplication
- [ ] Fix `_quarto.yml` footer (lines 158-161)
- [ ] Remove duplicate "Affine Drift matters" text
- [ ] Keep one version only
- [ ] Check all rendered pages for footer content

### RSS Feed
- [ ] Research RSS implementation for static GitHub Pages sites
- [ ] Create RSS feed file (`feed.xml` or `rss.xml`)
- [ ] Add RSS icon/link near search bar
- [ ] Update header template or `_quarto.yml` to include RSS link
- [ ] Test RSS feed functionality
- [ ] Ensure feed updates with new articles

---

## Phase 4: Preview Fixes

### Book Previews
- [ ] Review all books in `resources-books.qmd`
- [ ] Check each book preview image source
- [ ] Update broken image URLs
- [ ] Source images from Google Books API, Amazon, or other reliable sources
- [ ] Ensure proper image tags and error handling
- [ ] Test all book previews load correctly

### Article Previews
- [ ] Review article pages in `articles/` directory
- [ ] Add preview images where missing
- [ ] Source images from appropriate sources
- [ ] Ensure images load correctly
- [ ] Test all article previews

### Website Previews
- [ ] Review all websites in `resources-websites.qmd`
- [ ] Fix preview iframe/embed code
- [ ] Ensure proper loading and display
- [ ] Check for CORS or security issues
- [ ] Fix previews that flash and disappear
- [ ] Test all website previews are stable

---

## Phase 5: Sitewide Verification

### Layout Check
- [ ] Scroll through entire site
- [ ] Identify any remaining three-column layouts
- [ ] Convert all to single column
- [ ] Verify all pages match Videos page layout
- [ ] Check title positioning on all pages
- [ ] Verify sidebar functionality on all pages

### Link Check
- [ ] Test all internal links
- [ ] Test all external links
- [ ] Verify repository links work
- [ ] Check researcher links
- [ ] Verify paper links
- [ ] Test video links

### Functionality Check
- [ ] Test RSS feed
- [ ] Verify all previews work
- [ ] Check equation rendering on all pages
- [ ] Test navigation menus
- [ ] Verify sidebar history tracking
- [ ] Check responsive design (mobile/tablet)

### Content Check
- [ ] Verify all new researchers added
- [ ] Check all papers added
- [ ] Verify video added
- [ ] Confirm "Current Studies" changed to "Articles"
- [ ] Verify appendix labels removed
- [ ] Check footer duplication fixed

---

## Notes

1. **Priority Order**:
   - Layout standardization (affects UX most)
   - Content updates (researchers, papers, videos)
   - Technical fixes (equations, previews, RSS)
   - Minor text changes

2. **Testing**: After each phase, test locally and verify changes work correctly.

3. **GitHub Pages**: Ensure all changes work with static site hosting.

4. **Videos Page Model**: Study `resources-videos.qmd` carefully - this is the layout standard for all pages.

5. **Sidebar Implementation**:
   - Left: Table of contents / categories
   - Right: History of recent pages (per resource type)
   - Use JavaScript for history tracking if needed

---

## Completion Status

**Overall Progress**: 0% Complete

**Phase 1 (Content)**: 0% Complete
**Phase 2 (Layout)**: 0% Complete  
**Phase 3 (Technical)**: 0% Complete
**Phase 4 (Previews)**: 0% Complete
**Phase 5 (Verification)**: 0% Complete

---

**Last Updated**: 2025-12-05
**Next Review**: 2025-12-12

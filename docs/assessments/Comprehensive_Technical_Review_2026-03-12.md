# Comprehensive Technical Review: AffineDrift Website

**Date:** March 12, 2026
**Scope:** Full-stack review covering technical claims, UI/UX, implementation quality, and maintainability
**Reviewer:** Automated comprehensive audit

---

## Executive Summary

AffineDrift is an ambitious Quarto-based website presenting novel applications of control theory, differential geometry, and nonlinear dynamics to golf swing biomechanics. The site contains ~146 QMD content files, 4 book volumes, multiple article series, and extensive supplementary resources. This review identifies **47 issues** across four domains:

- **Technical Claims & Content Accuracy**: 15 issues (3 critical, 5 major, 7 moderate)
- **UI/UX & Website Implementation**: 12 issues (2 critical, 4 major, 6 moderate)
- **Maintainability & Architecture**: 13 issues (3 critical, 5 major, 5 moderate)
- **Content Completeness & Quality**: 7 issues (1 critical, 3 major, 3 moderate)

---

## Part I: Technical Claims & Content Accuracy

### CRITICAL Issues

#### ISSUE-TC01: Control-Affine Assumption Scope Overreach
**Files:** `articles/theory-part1.qmd`, `articles/affine-nature-golf-swing.qmd`, `articles/superposition.qmd`
**Severity:** CRITICAL

The core framework claims that the golf swing is a control-affine system: `ẋ = f(x) + G(x)u`. While this is a standard and useful modeling framework, the articles frequently make **categorical claims** that exceed the scope of this assumption:

1. **Muscle force-velocity coupling**: Hill's muscle model introduces multiplicative (not additive) coupling between activation and velocity, violating affine structure. The articles mention this limitation in `sources-of-nonlinearity.qmd` but the core theory articles (Part 1-3) do not adequately caveat this.
2. **Co-contraction and impedance modulation**: When antagonist muscles co-contract, they produce zero net torque but modulate joint stiffness. This stiffness modulation occurs in the null space of the torque map and is not captured by the affine input structure.
3. **History-dependent effects**: Fatigue, calcium buffering, and metabolite accumulation mean the effective input matrix G depends on movement history, not just instantaneous state.

**Recommendation:** Add explicit scope-limitation sections to theory-part1 and theory-part2 clarifying that the control-affine structure applies at the **joint-torque level** as a modeling choice, not as a physical truth. The existing `sources-of-nonlinearity.qmd` already addresses many of these concerns but is not cross-referenced from the core theory.

---

#### ISSUE-TC02: Superposition Claims Require Stronger Temporal Caveats
**Files:** `articles/superposition.qmd`, `index.qmd`, `overview.qmd`
**Severity:** CRITICAL

The superposition article (1,200+ lines) establishes that force superposition holds **instantaneously** at fixed state. This is mathematically correct. However:

1. The homepage states "generalized forces DO superpose" without the instantaneous caveat, implying trajectory-level superposition.
2. Several articles reference "force superposition" without clarifying it is an instantaneous property that requires re-evaluation as state evolves.
3. The phrase "Instantaneous Force-Acceleration Superposition" (used in the Tangent Hyperplane series) is more precise but is not consistently used across the site.

**Recommendation:** Standardize on the term "Instantaneous Force-Acceleration Superposition" across all articles. Add the instantaneous caveat to the homepage framework section.

---

#### ISSUE-TC03: Novel Claims Not Clearly Distinguished from Established Results
**Files:** Multiple tangent hyperplane articles, textbook chapters
**Severity:** CRITICAL

The site mixes well-established results from control theory/differential geometry with novel interpretations and applications. Readers cannot easily distinguish:

1. **Established**: Control-affine systems, tangent space linearization, contraction analysis, Lie bracket accessibility
2. **Novel interpretation**: Application to golf biomechanics, "drift/input" decomposition naming, ZTCF/ZVCF counterfactual framework
3. **Potentially novel**: Integral superposition framework, residual-aware control design, specific contraction-tangent unification claims

**Recommendation:** Add a "Novelty Status" callout to each major article indicating whether the content is: (a) established textbook material, (b) novel application of existing theory, or (c) potentially novel theoretical contribution.

---

### MAJOR Issues

#### ISSUE-TC04: ZTCF (Zero-Torque Counterfactual) Identifiability Gap
**Files:** `articles/theory-part2.qmd`, `articles/inverse-dynamics-inference.qmd`
**Severity:** MAJOR

The ZTCF framework (setting u=0 to observe pure drift) is conceptually valuable but faces a **practical identifiability problem**: you cannot directly measure or observe the ZTCF trajectory from real golf swing data because:
1. The golfer is always applying some control input
2. Muscle tone maintains joint stiffness even during "passive" phases
3. Separating gravitational, Coriolis, and centrifugal contributions from measured motion requires knowing the full system model

The existing critique in `critiques/ztcf_identifiability.md` identifies this issue but the main articles do not adequately address it.

**Recommendation:** Add a "Practical Considerations" section to theory-part2 addressing identifiability and referencing the critique.

---

#### ISSUE-TC05: Dimensional Inconsistency in Drift-Control Ratio (DCR)
**Files:** `articles/controllability-drift-ratio.qmd`
**Severity:** MAJOR

The DCR is defined as a ratio of norms, but the choice of norm affects the numerical value and physical interpretation:
1. The article uses the kinetic energy norm (`M(q)`-weighted) for accelerations, which is physically motivated
2. However, the DCR is also compared across different joints/DOFs without normalizing for the different physical dimensions (some are rotational, some translational)
3. The existing critique `critiques/dimensional_inconsistency_dcr.md` identifies this but the article has not been updated

**Recommendation:** Add a section on dimensional consistency, norm choice sensitivity, and cross-joint comparison caveats.

---

#### ISSUE-TC06: Lie Bracket Formalism Overreach
**Files:** `articles/theory-part3.qmd`, tangent hyperplane series
**Severity:** MAJOR

Several articles invoke Lie brackets for accessibility analysis, but:
1. The Lie bracket condition (LARC) provides **local** accessibility, not global controllability
2. The articles sometimes conflate accessibility with controllability
3. For underactuated systems (like the golf swing), the distinction is crucial

**Recommendation:** Clarify the distinction between accessibility and controllability wherever Lie brackets are discussed.

---

#### ISSUE-TC07: Contraction-Tangent Unification Claims Need Proof Completion
**Files:** `articles/Tangent Hyperplane Articles/Advanced/Contraction_Tangent_Unification.qmd`
**Severity:** MAJOR

The contraction-tangent unification article makes ambitious claims about bridging contraction analysis with tangent space methods, but several key results are stated without complete proofs. The connection to Lohmiller & Slotine's contraction analysis framework needs more rigorous mathematical development.

**Recommendation:** Either complete the proofs or explicitly mark incomplete results as conjectures.

---

#### ISSUE-TC08: "Control Is Motion" Paradigm Lacks Formal Definition
**Files:** `books/control-is-motion.qmd`, various articles
**Severity:** MAJOR

The phrase "Control Is Motion" is used as a paradigm label throughout the site but lacks a formal mathematical definition. It appears to mean "control inputs are best understood through their geometric effects on the configuration manifold" but this is never precisely stated. This makes it difficult for readers to evaluate or critique the claim.

**Recommendation:** Provide a formal definition of what "Control Is Motion" means mathematically, distinct from the standard control-affine formulation.

---

### MODERATE Issues

#### ISSUE-TC09: Intermediate Axis Theorem Misapplication
**Files:** `articles/secondary-axis-stability.qmd`
**Severity:** MODERATE

The article discusses stability about the intermediate axis of inertia (Dzhanibekov effect) but the application to the golf club is questionable since:
1. The golf club is not a free rigid body (it's attached at the grip)
2. The relevant instability is about the constraint reaction, not free-body rotation
3. The existing critique `critiques/intermediate_axis_fallacy.md` identifies this

**Recommendation:** Revise to clearly distinguish constrained vs. free-body rotation dynamics.

---

#### ISSUE-TC10: Strokes Gained Critique Makes Strong Non-Ergodicity Claim
**Files:** `articles/strokes-gained-limitations.qmd`
**Severity:** MODERATE

The article claims strokes gained is fundamentally flawed due to non-ergodicity. While the statistical critique has merit, the claim that strokes gained "fails" is overstated. Strokes gained is a descriptive statistic, not a causal model.

**Recommendation:** Reframe as "limitations of strokes gained as a causal analysis tool" rather than a fundamental failure.

---

#### ISSUE-TC11: Wrist-as-Universal-Joint Model Simplification
**Files:** `articles/wrist-universal-joint.qmd`
**Severity:** MODERATE

The wrist is modeled as a universal joint (2-DOF), but the actual wrist has 3 DOF (flexion/extension, radial/ulnar deviation, pronation/supination). The simplification is reasonable but the limitations are not discussed in the main article.

---

#### ISSUE-TC12: Double Pendulum Model Energy Considerations
**Files:** `articles/drift-components-wrench-double-pendulum.qmd`
**Severity:** MODERATE

The double pendulum wrench analysis focuses on force decomposition but does not discuss energy balance. Energy is a fundamental constraint that should be addressed, especially for the ZTCF where energy is conserved (no input work).

---

#### ISSUE-TC13: Intentional Constraint Collapse Needs Formal Treatment
**Files:** `articles/intentional-constraint-collapse.qmd`
**Severity:** MODERATE

"Intentional Constraint Collapse" (ICC) is presented as a deliberate strategy but the mathematical formalization is incomplete. When/why is ICC optimal vs. maintaining constraints? The answer likely involves the DCR approaching specific threshold values but this connection is not made explicit.

---

#### ISSUE-TC14: Textbook Chapters Reference Theorems Without Full Proofs
**Files:** `articles/tangent-hyperplane-contraction/chapters/*.qmd`
**Severity:** MODERATE

Several textbook chapters reference theorems (e.g., "Theorem 3.1", "Proposition 4.2") but the proofs are either sketched or deferred. For a textbook, this needs to be resolved before publication.

---

#### ISSUE-TC15: Bibliography Cross-Reference Gaps
**Files:** Multiple articles, `data/bibliography.json`
**Severity:** MODERATE

Some articles reference works that do not appear in the centralized bibliography (120 entries). The bibliography system appears well-maintained but cross-referencing is inconsistent:
- Some articles use inline citations
- Some use the Quarto citation system
- Some use neither and just mention authors by name

**Recommendation:** Standardize on Quarto's built-in citation system across all articles.

---

## Part II: UI/UX & Website Implementation

### CRITICAL Issues

#### ISSUE-UX01: AI Agent Internal Monologue Leaked into Production HTML
**File:** `resources-videos.qmd:439-445`
**Severity:** CRITICAL

An AI editing agent's internal thought process is visible as an HTML comment in the production source:
```html
<!-- Using a generic section or appending to others? The user wanted specific updates.
     I will update the A. Sala and Biomechanics channels in place or here if I removed them.
     Wait, I am replacing lines 342-395 (Physics Demos + Fluid Dynamics).
     I need to go upwards to fix the Channels which were earlier in the file (lines 195 and 322).
     ...
-->
```
This is shipped to users in the HTML source and is unprofessional. While it's in a comment and not visible on screen, it's visible via "View Source" and indicates a quality control gap.

**Recommendation:** Remove all AI agent internal comments. Audit all QMD/HTML files for similar leaked content.

---

#### ISSUE-UX02: Font Variable Mismatch in custom.scss
**File:** `custom.scss:24`
**Severity:** CRITICAL (affects entire site typography)

```scss
$font-family-sans-serif: "Playfair Display", serif;
```

"Playfair Display" is a **serif** font being assigned to the `$font-family-sans-serif` Bootstrap variable. This means:
1. The variable name is semantically incorrect (sans-serif variable holds a serif font)
2. If the font fails to load, the fallback is `serif` which is correct for the font but wrong for the variable name
3. This makes the CSS architecture misleading for future contributors

**Recommendation:** Either rename the variable usage to accurately reflect the font choice, or switch to an actual sans-serif font for this variable.

---

### MAJOR Issues

#### ISSUE-UX03: Massive CSS Codebase with Significant Duplication
**Files:** `styles.css` (2,655 lines), `css/` (19 files, ~4,700 lines), `custom.scss`
**Severity:** MAJOR

Total CSS is ~7,400 lines across multiple files. Key concerns:
1. `styles.css` (2,655 lines) is a single monolithic file that imports 3 more CSS files
2. The `css/` directory has 19 additional CSS files
3. Not all CSS files in `css/` are referenced from `_quarto.yml` or `styles.css`
4. Only `css/startup-launcher.css`, `css/search-metrics.css`, and `styles.css` are explicitly included in `_quarto.yml`
5. Dead CSS rules likely exist given the size

**Recommendation:** Audit CSS for dead rules using coverage tools. Consolidate into a clear architecture with a single entry point.

---

#### ISSUE-UX04: Inconsistent Page Layouts
**Severity:** MAJOR

Some pages use Quarto's native layouts while others use raw HTML blocks with custom CSS. This creates visual inconsistency:
1. The homepage (`index.qmd`) is entirely raw HTML in a `{=html}` block
2. Theory articles use Quarto's native markdown rendering
3. Resource pages use raw HTML with accordion components
4. The visual styles (spacing, typography, card designs) differ between these approaches

**Recommendation:** Standardize on one approach per page type. Define 3-4 page templates (landing, article, resource list, tool) and apply consistently.

---

#### ISSUE-UX05: Missing Dark Mode Support
**Severity:** MAJOR

The `custom.scss` defines a colorblind-safe palette (Okabe-Ito), which is excellent. However:
1. No dark mode is implemented despite the site being content-heavy (reading fatigue)
2. CSS custom properties in `styles.css` define light theme values but no `prefers-color-scheme: dark` media query
3. For a technical audience that reads long articles, dark mode is expected

**Recommendation:** Implement dark mode using CSS custom properties and `prefers-color-scheme` media query, with a manual toggle.

---

#### ISSUE-UX06: Navigation Becomes Overwhelming at Scale
**Severity:** MAJOR

The navbar has 7 top-level items, several with dropdowns. The left sidebar on the homepage adds more links. As the site grows:
1. The Books dropdown will grow with each new volume
2. The Resources dropdown already has 8 items
3. The Articles dropdown mixes different content types (manifesto, series, reviews)
4. The Repositories dropdown only has a single external GitHub link, wasting nav space

**Recommendation:** Restructure navigation around user tasks: "Learn" (theory + articles), "Explore" (resources + bibliography), "Build" (models + tools + repositories), "Connect" (about + contact).

---

### MODERATE Issues

#### ISSUE-UX07: Homepage Emoji Icons Instead of Proper Icons
**File:** `index.qmd:152-166`
**Severity:** MODERATE

Quick-start cards use HTML entity emojis (&#128214;, &#128187;, etc.) as icons. These render inconsistently across platforms and look unprofessional.

**Recommendation:** Use SVG icons or an icon library (e.g., Bootstrap Icons which is already loaded via Quarto).

---

#### ISSUE-UX08: No Breadcrumb Navigation
**Severity:** MODERATE

Articles nested in subdirectories (e.g., `articles/Tangent Hyperplane Articles/Advanced/...`) have no breadcrumb navigation. Users can get lost in the content hierarchy.

**Recommendation:** Add breadcrumb navigation to all article pages.

---

#### ISSUE-UX09: Table of Contents Disabled Globally
**File:** `_quarto.yml:157`
**Severity:** MODERATE

`toc: false` is set globally in `_quarto.yml`. Individual articles override this, but long resource pages and some articles lack a table of contents. For 1000+ line articles, this is a usability problem.

**Recommendation:** Set `toc: true` globally and disable on specific pages that don't need it (homepage, contact).

---

#### ISSUE-UX10: Service Worker Caches Stale Content
**File:** `service-worker.js`
**Severity:** MODERATE

The service worker uses `CACHE_NAME = 'affinedrift-v2'` but there's no automated cache-busting. When content is updated, users may see stale content until the service worker is manually updated.

**Recommendation:** Implement content-hash-based cache keys or at minimum increment the version number as part of the build process.

---

#### ISSUE-UX11: Book Placeholder Images Throughout Resources
**Files:** `resources-books.qmd` (25+ instances)
**Severity:** MODERATE

Most book entries use `book_placeholder.svg` instead of actual cover images. This makes the page look incomplete.

**Recommendation:** Add actual book cover images or remove the image element for books without covers.

---

#### ISSUE-UX12: Mobile Menu Has Custom Implementation Over Quarto's
**Files:** `index.qmd:10-21`, `css/mobile.css`
**Severity:** MODERATE

The homepage implements a custom mobile menu toggle button with custom CSS, but Quarto already provides responsive navigation. This creates potential conflicts between the two systems.

**Recommendation:** Use Quarto's built-in responsive navigation consistently.

---

## Part III: Maintainability & Architecture

### CRITICAL Issues

#### ISSUE-MA01: Triplicated Asset Directories (CSS and JS)
**Files:** `css/`, `src/css/`, `docs/css/` and `js/`, `src/js/`, `docs/js/`
**Severity:** CRITICAL

Three copies of CSS and JS files exist:
- **`css/`** (19 files): Appears to be the primary source
- **`src/css/`** (6 files): Identical copies of some files from `css/`
- **`docs/css/`** (6 files): Identical copies (output directory, copied by Quarto build)
- **`js/`** (13 files): Primary source
- **`src/js/`** (9 files): Some overlap with different content (has `modules/` subdirectory)
- **`docs/js/`** (13 files): Identical copies from `js/`

This means:
1. Changes to CSS/JS must be made in the correct directory or they'll be overwritten
2. `src/js/` has module versions that don't match `js/` (different architecture)
3. No build pipeline reconciles these directories

**Recommendation:** Designate `src/` as the single source of truth. Set up a build pipeline that copies from `src/` to the locations Quarto expects. Remove duplicate files from `css/` and `js/`.

---

#### ISSUE-MA02: 40 QMD Files at Repository Root
**Severity:** CRITICAL

The repository root contains 40 QMD files alongside config files, README, etc. This creates:
1. A cluttered root directory that's hard to navigate
2. Difficulty distinguishing content from configuration
3. No clear content hierarchy

Root-level QMD files include: `index.qmd`, `overview.qmd`, `about.qmd`, `contact.qmd`, `collaborate.qmd`, `bibliography.qmd`, `articles.qmd`, `drifter-manifesto.qmd`, `tangent-hyperplanes.qmd`, `research-reviews.qmd`, `book-reviews.qmd`, `daydreams-doodles.qmd`, `tools.qmd`, `models.qmd`, `repositories.qmd`, `resources-*.qmd` (8 files), `models-*.qmd` (7 files), `repositories-*.qmd` (5 files), `offline.html`

**Recommendation:** Move content pages into subdirectories: `pages/`, `resources/`, `models/`, `repositories/`. Update `_quarto.yml` render paths accordingly.

---

#### ISSUE-MA03: Multiple Overlapping Content Hierarchies
**Severity:** CRITICAL

Content is spread across at least 5 directories with unclear relationships:
1. **Root-level QMDs**: Main site pages
2. **`articles/`**: Core theory articles (primary content)
3. **`content/`**: Additional content with its own `README.md`
4. **`books/`**: Book-format versions of similar content
5. **`articles/tangent-hyperplane-contraction/`**: Textbook-format content
6. **`articles/The_Geometry_of_Motion/`**: Another textbook-format content
7. **`articles/Tangent Hyperplane Articles/`**: Yet another organization of tangent hyperplane content

The same theoretical material appears in multiple forms:
- Tangent hyperplanes: standalone articles, book chapters, textbook chapters, series articles, unified thesis
- Core theory: theory-part1-5, book volume content, Geometry of Motion chapters

**Recommendation:** Create a clear content architecture document. Designate one canonical version of each article and make others clearly derivative. Consider using Quarto's multi-format output instead of maintaining multiple versions.

---

### MAJOR Issues

#### ISSUE-MA04: No Build Pipeline or Asset Management
**Severity:** MAJOR

There is no build tool (webpack, esbuild, Vite) for:
1. CSS concatenation/minification
2. JS bundling/minification
3. Image optimization
4. Cache-busting hash generation
5. Dead code elimination

The site relies on Quarto's built-in rendering plus manual file management.

**Recommendation:** Add a minimal build pipeline. Even a simple npm script that concatenates and minifies CSS/JS would help. Consider Vite for its simplicity.

---

#### ISSUE-MA05: Spaces in Directory Names
**Files:** `articles/Tangent Hyperplane Articles/`, `articles/The_Geometry_of_Motion/`, `content/Drift Ratio Visualizations/`, etc.
**Severity:** MAJOR

Multiple directories use spaces in their names. This causes:
1. Quoting issues in scripts and CI/CD
2. URL encoding problems (%20 in URLs)
3. Difficulty with command-line tools
4. Git operations become error-prone

**Recommendation:** Rename all directories to use hyphens or underscores. Update all references.

---

#### ISSUE-MA06: `docs/` as Output Directory is Committed to Git
**Severity:** MAJOR

The entire `docs/` directory (Quarto's output) is committed to the repository. This includes:
- 159 HTML files
- Multiple copies of CSS/JS
- Bootstrap and Quarto library files
- Generated search index

This means every content change produces massive diffs. The `docs/` directory should either:
1. Be in `.gitignore` and built via CI/CD, or
2. Be deployed from a separate branch (e.g., `gh-pages`)

**Recommendation:** Move to CI/CD-based builds. Add `docs/` to `.gitignore`. Use GitHub Pages with GitHub Actions to build and deploy.

---

#### ISSUE-MA07: 18+ Configuration Files at Root
**Severity:** MAJOR

Root directory has: `_quarto.yml`, `package.json`, `package-lock.json`, `pyproject.toml`, `ruff.toml`, `.pre-commit-config.yaml`, `playwright.config.js`, `jest.config.js`, `.htmlvalidate.json`, `manifest.json`, `custom.scss`, `styles.css`, plus files in `config/` directory (8 JSON config files).

**Recommendation:** Consolidate where possible. Move tool configs to a `config/` directory. Use `pyproject.toml` for Python tool configs instead of separate files.

---

#### ISSUE-MA08: Stale Assessment/Report Files
**Files:** `docs/assessments/` (60+ files), `critiques/` (40+ files)
**Severity:** MAJOR

There are 60+ assessment files and 40+ critique files. Many are dated and may be stale:
- Assessment archive has reports from Jan-Feb 2026
- Multiple "Completist Reports" at different dates
- Status JSON files at root (`1007_status.json`, `1008_status.json`)

**Recommendation:** Archive old assessments. Remove stale status files. Create a clear retention policy for assessment documents.

---

#### ISSUE-MA09: No Content Validation Pipeline
**Severity:** MAJOR

Despite having Jest and Playwright tests, there is no:
1. Link checker for internal/external links
2. Math equation validator
3. Bibliography consistency checker
4. Spell checker
5. Content linting (consistent headings, frontmatter validation)

**Recommendation:** Add a pre-commit or CI check that validates links, frontmatter, and bibliography consistency.

---

### MODERATE Issues

#### ISSUE-MA10: Test Coverage Gaps
**Files:** `tests/` directory
**Severity:** MODERATE

Unit tests cover: bibliography, global search, metrics, notes workspace, script, utils
E2E tests cover: accessibility, articles, bibliography, homepage, navigation, offline, search, user journey

Missing test coverage:
- No tests for the service worker
- No tests for mobile menu behavior
- No visual regression tests
- No tests for print CSS
- E2E smoke test has only 20 lines

---

#### ISSUE-MA11: Python Code Not Integrated
**Files:** `src/affine_control/`, `src/tangent_models/`, `src/tools/`
**Severity:** MODERATE

Python source code exists in `src/` but:
1. `pyproject.toml` is minimal
2. No Python tests are defined in the test directories
3. The MATLAB tools referenced in articles are not available in the repository
4. The relationship between Python code and the website is unclear

---

#### ISSUE-MA12: Archive Directories Lack Cleanup Policy
**Files:** `archive/`, `content/archive/`, `articles/archive/`, `articles/calculation-framework-comparison/archive/`
**Severity:** MODERATE

Multiple archive directories contain old versions of articles and code. There's no cleanup policy or retention schedule.

---

#### ISSUE-MA13: Duplicate Data Files
**Files:** `data/`, `docs/data/`
**Severity:** MODERATE

`data/bibliography.json`, `data/bibliography.yaml`, `data/reading_paths.yaml` exist in both `data/` and `docs/data/`. The `docs/data/` copies are generated by the Quarto build but committed to git.

---

## Part IV: Content Completeness & Quality

### CRITICAL Issue

#### ISSUE-CQ01: "Coming Soon" and Placeholder Content on Live Site
**Files:** `resources-papers.qmd:65`, multiple resource pages
**Severity:** CRITICAL

Active pages contain placeholder content:
- `resources-papers.qmd:65`: "Note: Detailed review of Carol Putnam's work on interaction forces and proximal-to-distal sequencing coming soon."
- `resources-books.qmd`: 25+ book entries using `book_placeholder.svg`
- `resources-researchers.qmd`: Multiple researcher entries with fallback placeholder images

**Recommendation:** Either complete the content or remove placeholder entries. "Coming soon" content reduces site credibility.

---

### MAJOR Issues

#### ISSUE-CQ02: Textbook Content Is Draft Quality
**Files:** `articles/tangent-hyperplane-contraction/textbook-main.qmd`
**Severity:** MAJOR

The textbook-main.qmd explicitly identifies itself as a draft:
- Line 3: `subtitle: "A Geometry-First Textbook Draft for High-Dimensional Nonlinear Control"`
- Line 25: References "This draft" multiple times
- Line 252: "This draft establishes the core architecture for a full textbook"

This draft content is published on the live site alongside polished articles, creating quality inconsistency.

**Recommendation:** Either clearly mark draft content with visual indicators (e.g., a banner) or move to a separate staging area.

---

#### ISSUE-CQ03: Inconsistent Article Metadata
**Severity:** MAJOR

Articles have inconsistent YAML frontmatter:
- Some have `author:`, `date:`, `abstract:`
- Some have none of these
- Citation format varies (some use Quarto's citation system, others use inline references)
- Date formats vary

**Recommendation:** Define a standard frontmatter template and apply to all articles.

---

#### ISSUE-CQ04: Cross-Referencing Between Articles Is Weak
**Severity:** MAJOR

Despite the content being deeply interconnected, articles rarely link to each other:
1. Theory-part2 introduces ZTCF but doesn't link to the existing critique
2. The sources-of-nonlinearity article addresses many criticisms in the critiques/ directory but doesn't reference them
3. Book chapters don't link to the corresponding standalone articles
4. No "See Also" or "Related Articles" sections

**Recommendation:** Add systematic cross-references using Quarto's cross-reference system. Add "Related Articles" sections to each article.

---

### MODERATE Issues

#### ISSUE-CQ05: Critiques Directory Not Surfaced on Website
**Files:** `critiques/` (40+ files)
**Severity:** MODERATE

The `critiques/` directory contains 40+ detailed critique files but these are:
1. Not rendered as QMD pages
2. Not linked from the articles they critique
3. Not accessible from the website navigation

**Recommendation:** Convert key critiques to QMD pages and link them from the relevant articles. The "Critic's Corner" page for the Tangent Hyperplane series shows this is already being done selectively.

---

#### ISSUE-CQ06: Multiple Versions of Same Article Without Version Control
**Files:** Various archive/ directories
**Severity:** MODERATE

Articles like `controllability-drift-ratio` and `secondary-axis-stability` have v1 versions in archive directories, but:
1. No changelog documenting what changed between versions
2. No indication on the current version that it's been revised
3. Readers finding old versions via search may get outdated information

---

#### ISSUE-CQ07: The Geometry of Motion and Tangent Hyperplane Contraction Textbooks Overlap
**Files:** `articles/The_Geometry_of_Motion/`, `articles/tangent-hyperplane-contraction/`
**Severity:** MODERATE

Two separate textbook-format content areas cover overlapping material:
- Both cover foundations of nonlinear dynamics
- Both discuss tangent space methods
- Both include optimal control chapters

It's unclear whether these are intended as separate books or if one supersedes the other.

**Recommendation:** Clarify the relationship between these two textbook projects. If they're separate books, add clear scope statements. If one is deprecated, archive it.

---

## Recommended GitHub Issues

The following issues should be created in the GitHub repository, organized by priority:

### Priority 1 (Critical - Address Immediately)

| # | Title | Labels | Related Issues Above |
|---|-------|--------|---------------------|
| 1 | Remove leaked AI agent comments from resources-videos.qmd | `bug`, `content` | ISSUE-UX01 |
| 2 | Add scope-limitation caveats to core theory articles (Part 1-3) | `content`, `technical-accuracy` | ISSUE-TC01 |
| 3 | Standardize "Instantaneous Force-Acceleration Superposition" terminology | `content`, `technical-accuracy` | ISSUE-TC02 |
| 4 | Distinguish novel claims from established results across all articles | `content`, `documentation` | ISSUE-TC03 |
| 5 | Fix serif font assigned to $font-family-sans-serif in custom.scss | `bug`, `ui` | ISSUE-UX02 |
| 6 | Consolidate triplicated CSS/JS directories (css/, src/css/, docs/css/) | `architecture`, `tech-debt` | ISSUE-MA01 |
| 7 | Move QMD content files out of repository root into subdirectories | `architecture`, `tech-debt` | ISSUE-MA02 |
| 8 | Define canonical content hierarchy to resolve overlapping directories | `architecture`, `documentation` | ISSUE-MA03 |
| 9 | Remove "coming soon" and placeholder content from live pages | `content`, `quality` | ISSUE-CQ01 |

### Priority 2 (Major - Address Soon)

| # | Title | Labels | Related Issues Above |
|---|-------|--------|---------------------|
| 10 | Add ZTCF identifiability discussion to theory-part2 | `content`, `technical-accuracy` | ISSUE-TC04 |
| 11 | Address dimensional inconsistency in DCR article | `content`, `technical-accuracy` | ISSUE-TC05 |
| 12 | Clarify accessibility vs. controllability in Lie bracket discussions | `content`, `technical-accuracy` | ISSUE-TC06 |
| 13 | Complete proofs in contraction-tangent unification article | `content`, `technical-accuracy` | ISSUE-TC07 |
| 14 | Formally define "Control Is Motion" paradigm | `content`, `documentation` | ISSUE-TC08 |
| 15 | Audit and reduce CSS codebase (~7,400 lines) | `tech-debt`, `ui` | ISSUE-UX03 |
| 16 | Standardize page layouts across site | `ui`, `ux` | ISSUE-UX04 |
| 17 | Implement dark mode | `enhancement`, `ui` | ISSUE-UX05 |
| 18 | Redesign navigation for scalability | `enhancement`, `ux` | ISSUE-UX06 |
| 19 | Add minimal build pipeline for assets | `architecture`, `enhancement` | ISSUE-MA04 |
| 20 | Rename directories with spaces to use hyphens | `tech-debt`, `architecture` | ISSUE-MA05 |
| 21 | Move docs/ to CI/CD build output (stop committing generated files) | `architecture`, `ci-cd` | ISSUE-MA06 |
| 22 | Consolidate root-level configuration files | `tech-debt` | ISSUE-MA07 |
| 23 | Archive stale assessment and status files | `tech-debt` | ISSUE-MA08 |
| 24 | Add content validation pipeline (link checker, frontmatter lint) | `ci-cd`, `quality` | ISSUE-MA09 |
| 25 | Mark draft textbook content with visual indicators | `content`, `ux` | ISSUE-CQ02 |
| 26 | Standardize article frontmatter (author, date, abstract, citations) | `content`, `quality` | ISSUE-CQ03 |
| 27 | Add systematic cross-references between related articles | `content`, `ux` | ISSUE-CQ04 |

### Priority 3 (Moderate - Address When Convenient)

| # | Title | Labels | Related Issues Above |
|---|-------|--------|---------------------|
| 28 | Revise intermediate axis theorem application in secondary-axis-stability | `content`, `technical-accuracy` | ISSUE-TC09 |
| 29 | Reframe strokes-gained critique as limitations analysis | `content` | ISSUE-TC10 |
| 30 | Add DOF limitation discussion to wrist-universal-joint article | `content` | ISSUE-TC11 |
| 31 | Add energy balance to double pendulum wrench analysis | `content` | ISSUE-TC12 |
| 32 | Formalize Intentional Constraint Collapse with DCR thresholds | `content`, `technical-accuracy` | ISSUE-TC13 |
| 33 | Complete proofs in textbook chapters | `content` | ISSUE-TC14 |
| 34 | Standardize bibliography cross-references across all articles | `content`, `quality` | ISSUE-TC15 |
| 35 | Replace emoji icons with SVG/icon library on homepage | `ui` | ISSUE-UX07 |
| 36 | Add breadcrumb navigation to nested articles | `ux`, `enhancement` | ISSUE-UX08 |
| 37 | Enable table of contents globally, disable per-page as needed | `ux` | ISSUE-UX09 |
| 38 | Implement content-hash cache busting for service worker | `enhancement` | ISSUE-UX10 |
| 39 | Add actual book cover images to resources-books | `content` | ISSUE-UX11 |
| 40 | Remove custom mobile menu in favor of Quarto's responsive nav | `tech-debt`, `ui` | ISSUE-UX12 |
| 41 | Improve test coverage (service worker, mobile, visual regression) | `testing` | ISSUE-MA10 |
| 42 | Integrate Python tools with website or document relationship | `documentation` | ISSUE-MA11 |
| 43 | Define archive/retention policy for old assessments and versions | `documentation`, `tech-debt` | ISSUE-MA12 |
| 44 | Remove duplicate data files from docs/data/ | `tech-debt` | ISSUE-MA13 |
| 45 | Surface critiques directory on website with links from articles | `content`, `ux` | ISSUE-CQ05 |
| 46 | Add version history/changelog to revised articles | `documentation` | ISSUE-CQ06 |
| 47 | Clarify relationship between overlapping textbook projects | `documentation`, `content` | ISSUE-CQ07 |

---

## Summary Statistics

| Category | Critical | Major | Moderate | Total |
|----------|----------|-------|----------|-------|
| Technical Claims | 3 | 5 | 7 | 15 |
| UI/UX | 2 | 4 | 6 | 12 |
| Maintainability | 3 | 5 | 5 | 13 |
| Content Quality | 1 | 3 | 3 | 7 |
| **Total** | **9** | **17** | **21** | **47** |

---

## Positive Observations

While this review focuses on issues, the following strengths should be noted:

1. **Colorblind-safe palette**: The Okabe-Ito palette in `custom.scss` shows excellent accessibility awareness
2. **Self-critique culture**: The `critiques/` directory with 40+ critique files demonstrates intellectual honesty
3. **Mathematical depth**: Articles like `sources-of-nonlinearity.qmd` show rigorous, thorough treatment
4. **Comprehensive bibliography**: 120 entries in a structured JSON format with consistent fields
5. **Testing infrastructure**: Jest + Playwright setup with 2,257 lines of test code
6. **AI transparency**: The homepage openly discusses AI-assisted content creation
7. **Focus visibility**: CSS implements `:focus-visible` for keyboard accessibility
8. **Service worker**: Offline support is implemented (though needs cache-busting improvements)
9. **Pre-commit hooks**: `.pre-commit-config.yaml` exists for code quality enforcement
10. **Multiple reading paths**: The `reading_paths.yaml` system shows thoughtful UX consideration

---

*This assessment was generated on March 12, 2026. Issues should be re-evaluated after major changes to the codebase.*

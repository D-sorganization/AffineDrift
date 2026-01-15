# Website Construction Review Template (Static GitHub Pages + Quarto)

## 0) Reviewer Operating Rules (Read First)

**Assume the site is not production-ready until proven otherwise.**

*   **No vague feedback.** Every criticism must include:
    *   **What’s wrong**
    *   **Why it matters**
    *   **Exact fix** (steps, settings, file names, or code snippets if applicable)
    *   **Severity**: Blocker / High / Medium / Low
    *   **Effort**: S / M / L
*   Prefer “delete / simplify / standardize” over “add more.”
*   If you can’t verify something (no repo access / no live URL), list it as an assumption and provide an explicit verification method.

---

## 1) Context Summary (Fill In)

*   **Site URL**:
*   **Repo URL**:
*   **Build system**: (Quarto version? GitHub Actions? direct Pages build?)
*   **Primary audience**: (undergrad / grad / self-learners / engineers)
*   **Primary outcomes**: (what a learner should be able to do after using the site)
*   **Content scope**: nonlinear control topics included (e.g., Lyapunov, ISS, feedback linearization, sliding mode, passivity, backstepping, NMPC, differential flatness, etc.)

---

## 2) Executive Summary (1 page max)

### A. Top 10 Critical Issues (ranked)

**For each issue:**

*   **Issue title**
*   **Severity / Effort**
*   **Where found** (page, file path, section)
*   **Impact on learner**
*   **Proposed fix** (short)
*   **Acceptance criteria** (how we know it’s fixed)

### B. Quick Wins (do these first)

*   List 5–15 changes that are small effort but high impact.

### C. Strategic Fixes (bigger refactors)

*   List 3–8 changes that materially improve maintainability or usability.

---

## 3) Information Architecture and Pedagogy (Education-first)

### 3.1 Learning Flow and Curriculum Design

*   Does the site have a clear “Start Here” path for beginners?
*   Is there a progression from fundamentals → advanced topics?
*   Are prerequisites explicit (math, linear systems, differential equations)?
*   Is there an estimated time to complete modules?
*   Are there learning objectives per section?

**Provide brutally specific recommendations:**

*   What to reorder, merge, split, or delete.
*   Missing “bridge” content learners will need.
*   Suggested canonical structure (outline it).

### 3.2 Resource Quality Control

The site is link-heavy. Evaluate:

*   Link credibility (papers vs. blog posts vs. random notes)
*   Link redundancy / overlap
*   Dead links / moved PDFs / paywalls
*   Whether each link has a one-line “why this matters” annotation

**Required output:**

*   A list of the worst offenders: pages with link dumps and no guidance.
*   A rule set for curating links (e.g., “must include: difficulty, prerequisites, key takeaway, and tags”).

### 3.3 Content Readability for Technical Topics

*   Are definitions and assumptions stated before derivations?
*   Are symbols consistent across pages?
*   Do pages have examples and small “sanity check” cases?
*   Do pages have diagrams where they should?
*   Do you overuse walls of equations without narrative?

**Deliverable:** Identify 5 pages with the biggest readability failures and provide rewrite guidance.

---

## 4) Quarto + QMD Rendering and Equation Fidelity (Hard requirement)

**This section is a dealbreaker. Treat it like a “math typesetting QA audit.”**

### 4.1 Math Rendering Correctness (KaTeX/MathJax)

**Verify:**

*   Inline math renders consistently (spacing, font, baseline)
*   Display equations align and break properly on mobile
*   Numbering behavior is consistent (if numbering is used)
*   Environments work (align, cases, matrix, split, etc.)
*   No raw LaTeX is leaking onto pages
*   No double-rendering or escaped characters (e.g., `\\` shown literally)

**Checklist (mark Pass/Fail and cite pages):**

- [ ] Inline math works everywhere
- [ ] Display math works everywhere
- [ ] align blocks render correctly
- [ ] Matrices render correctly
- [ ] Equation references work (if used)
- [ ] Code blocks do not interfere with LaTeX
- [ ] Long equations wrap or scroll cleanly on mobile
- [ ] No visible TeX artifacts ($, \(, \[ showing)

### 4.2 QMD Authoring Patterns (Consistency rules)

**Inspect .qmd files and identify:**

*   Mixed math delimiters or inconsistent style
*   Inconsistent callouts, admonitions, figure captions, citations
*   Missing YAML fields or inconsistent metadata

**Required output:**

*   A “house style” for equations and theorem-like blocks (copy/paste rules).
*   3–5 concrete examples of bad QMD patterns and the corrected versions.

### 4.3 Build and Rendering Reproducibility

*   Does the site build deterministically on GitHub?
*   Is Quarto pinned to a version?
*   Are extensions pinned?
*   Are there fragile dependencies (pandoc versions, Lua filters)?

**Deliverable:** a “build reliability” risk report with fixes.

---

## 5) Frontend UX/UI Review (Be mean, but useful)

### 5.1 Visual Hierarchy and Layout

*   Is the site readable in long sessions?
*   Headings: do they guide scanning?
*   Are pages too dense?
*   Are there consistent margins, line length, font sizes, spacing?

**Provide:**

*   The 10 most annoying layout problems (with where they occur).
*   Concrete fixes (CSS or Quarto theme config) and why.

### 5.2 Navigation and Findability

*   Can a learner find “Lyapunov stability” in 10 seconds?
*   Is search enabled and good?
*   Do pages have “Next / Previous” or module navigation?
*   Is there a tags/categories system?

**Deliverable:** Proposed nav structure + minimum viable improvements.

### 5.3 Link Presentation (Critical for resource-heavy sites)

*   Are external links visually distinct?
*   Do external links open in new tabs (and should they)?
*   Do you show link metadata (paper/year/authors) where appropriate?
*   Do you avoid “here” and “this” anchor text?

**Deliverable:** a link style guide and required lint rules.

---

## 6) Mobile-Friendly Compliance (No excuses)

**Test at common breakpoints (320px width minimum) and provide:**

*   Issues with overflow, zooming, horizontal scroll
*   Tap targets too small
*   Sidebar/nav usability
*   Tables, code blocks, and long equations on mobile
*   Performance on mobile networks (LCP / page weight)

**Checklist (Pass/Fail with examples):**

- [ ] No horizontal scrolling on typical pages
- [ ] Nav works with one hand
- [ ] Code blocks are scrollable and readable
- [ ] Equations don’t break layout
- [ ] Tables are responsive (or alternatives provided)
- [ ] Font size legible without zoom
- [ ] Touch targets ≥ ~44px effective size

**Deliverable:** Specific CSS/Quarto changes to fix the top 5 mobile failures.

---

## 7) Performance (Static doesn’t mean fast)

**Evaluate:**

*   Total page weight (especially if many scripts are loaded)
*   Image optimization
*   Excessive JS/CSS or multiple font loads
*   Caching headers (as applicable in GitHub Pages constraints)
*   Third-party scripts (MathJax can be heavy)

**Deliverable:** A prioritized performance plan:

*   What to remove
*   What to defer/lazy-load
*   What to optimize and how

---

## 8) Repository Layout and Organization (Maintainability Audit)

### 8.1 Structure Review

**Assess whether the repo:**

*   Clearly separates content (.qmd) from assets and config
*   Has predictable naming conventions
*   Avoids “misc/” dumping grounds
*   Makes it easy to add a new module without breaking nav

**Required output:**

*   Current structure problems (with examples)
*   Proposed repo tree (example below) and migration steps

**Example target tree (modify as needed):**

```text
/_quarto.yml
/content/
/modules/
/reference/
/appendices/
/assets/
/img/
/css/
/js/
/data/ (if any)
/scripts/ (build helpers)
/tests/ (link checks, render checks)
README.md (contributor instructions)
CONTRIBUTING.md
.github/workflows/ (build/deploy)
```

### 8.2 Docs and Contributor Experience

**Check for:**

*   README clarity: how to build locally, how to add content, how to run checks
*   Contribution guidelines
*   Issue templates (content bug, math rendering bug, link bug)
*   Changelog/release notes (optional)

**Deliverable:** Minimum doc set required for a healthy repo.

### 8.3 Quality Gates (Automated checks)

**Recommend CI steps:**

*   Quarto render build
*   Broken link checker
*   Spell check (optional)
*   Linting for markdown/QMD style
*   HTML validation (optional)
*   “Math rendering smoke test” (at least presence of expected scripts)

**Deliverable:** A proposed GitHub Actions workflow outline.

---

## 9) Security Review (Static sites still screw this up)

**Even with GitHub Pages, review:**

### 9.1 Dependency & Supply Chain

*   Are you pulling remote scripts from random CDNs?
*   Are versions pinned (MathJax/KaTeX, highlight.js, etc.)?
*   Any suspicious third-party widgets?

**Deliverable:** A “remote dependency” inventory and recommendations:

*   Prefer bundling or reputable CDNs
*   Pin versions
*   Avoid abandoned libraries

### 9.2 Content Injection / XSS Surface

*   Are there any forms, embedded HTML, or untrusted user content?
*   Is any markdown allowing raw HTML that could be abused by contributors?
*   Are external iframes used?

**Deliverable:** Risk assessment and mitigation:

*   Quarto settings to restrict raw HTML (if applicable)
*   Safe embed patterns

### 9.3 Secrets and Repo Hygiene

*   Check for accidentally committed API keys/tokens
*   `.env` files
*   GitHub Actions secrets usage

**Deliverable:** “Secrets hygiene” checklist + recommended scanning (e.g., secret scanning, dependabot).

### 9.4 Headers, Policies, and External Links

**GitHub Pages limits headers, but review:**

*   CSP possibility (even if limited)
*   Referrer policy for external links
*   `noopener noreferrer` when opening new tabs
*   Any tracking/privacy concerns

**Deliverable:** Practical security improvements within Pages constraints.

---

## 10) Accessibility Audit (Don’t exclude half your users)

**Check:**

*   Color contrast
*   Keyboard navigation
*   Screen reader semantics (headings in correct order)
*   Alt text for figures
*   Link text clarity (no “click here”)
*   Code blocks and math readability

**Deliverable:** Top 10 a11y issues and fixes.

---

## 11) Content Integrity and Academic Rigor

**For nonlinear control theory specifically:**

*   Are definitions correct and standard?
*   Are stability statements stated with conditions (continuity, Lipschitz, etc.)?
*   Are references properly cited (papers, textbooks)?
*   Are you accidentally teaching folklore as theorem?

**Deliverable:** List questionable claims with suggested corrections and citations needed.

---

## 12) Output Format Requirements (So the feedback is usable)

### 12.1 Issue Log Table (Required)

For each issue:

| ID | Title | Severity | Effort | Location (URL + repo path) | What’s wrong | Why it matters | Exact fix | Acceptance criteria |
|----|-------|----------|--------|----------------------------|--------------|----------------|-----------|---------------------|
|    |       |          |        |                            |              |                |           |                     |

### 12.2 “Fix Plan” (Required)

*   **Phase 1** (Stability/Rendering/Navigation blockers)
*   **Phase 2** (Repo refactor + UX cleanup)
*   **Phase 3** (Content expansion + pedagogy improvements)

### 12.3 “Do Not Do” List (Required)

*   List tempting changes that should be avoided (e.g., “adding more links without annotations,” “custom JS for math hacks,” “mega-sidebar with 200 entries,” etc.)

---

## 13) Testing Protocol the Reviewer Must Follow (Required)

**The reviewer must explicitly state what they tested:**

*   **Browsers**: Chrome / Firefox / Safari (if possible)
*   **Devices**: desktop + at least one mobile (or emulation)
*   **Pages sampled**: at least N pages including math-heavy ones
*   **Link checking method**
*   **Build method**: local render + GitHub Pages output

---

## 14) Optional But Strongly Recommended Add-ons

*   A “gold standard” sample page rewrite: take one messy page and rewrite it to the site’s ideal standard (structure + math + link annotations).
*   A “navigation redesign mock outline” (no design tools needed, just text).
*   A minimal CSS/theme patch list (exact files/variables).

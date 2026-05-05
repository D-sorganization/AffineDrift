# Phase 2 CSS Refactor Roadmap
**Issue:** #2953  
**Duration:** 6–8 hours  
**Status:** Ready to start

---

## Overview

Phase 2 focuses on **high-impact, low-risk improvements** that unblock Phase 3 (token integration) and clean up technical debt.

### Phase 2 Deliverables
- [ ] Activate design token system
- [ ] Consolidate dark mode (DRY fix)
- [ ] Standardize breakpoint operators
- [ ] Responsive behavior test plan
- [ ] Updated import order

---

## Task 1: Activate Design Token System
**Duration:** 2–3 min  
**Risk:** Low  
**Files:** `styles.css`

### Current State
```css
/* styles.css (lines 1–8) */
@import url("css/breakpoints.css");
@import url("css/bibliography.css");
@import url("css/critics-corner.css");
@import url("css/resources.css");
```

### Change
Add design-tokens.css FIRST (before breakpoints):
```css
@import url("css/design-tokens.css");  /* NEW: Design token definitions */
@import url("css/breakpoints.css");
@import url("css/bibliography.css");
@import url("css/critics-corner.css");
@import url("css/resources.css");
```

### Verification
```bash
# Should see no CSS errors, tokens available
grep "color: var(" styles.css | head -5
grep "margin: var(" styles.css | head -5
```

### Why This Works
- `design-tokens.css` already imports all 8 token categories
- Existing inline `:root` variables will be supplemented (not overwritten)
- No breaking changes; CSS variables cascade naturally

---

## Task 2: Consolidate Dark Mode (DRY Fix)
**Duration:** 15–20 min  
**Risk:** Low  
**Files:** `styles.css` (lines 2645–2673)

### Current State (Duplicated)

**Lines 2645–2653:**
```css
@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: dark;
    --bg-body: #0d0d1a;
    --bg-alt: #1a1a2e;
    --bg-sidebar: #112;
    --text-main: #dde1e7;
    --text-muted: #8b90a0;
    --border-color: #2a2a40;
    --light-blue: #0a2a40;
    --legal-pad-yellow: #1a1810;
    --shadow-color: rgb(0, 0, 0, 0.4);
  }
}
```

**Lines 2664–2673:** (Identical)
```css
[data-theme="dark"] {
  color-scheme: dark;
  --bg-body: #0d0d1a;
  /* ... same 9 variables ... */
}
```

### Proposed Solution

Replace both sections with:
```css
/* Dark Mode – automatic via prefers-color-scheme + manual toggle via [data-theme="dark"] */
@media (prefers-color-scheme: dark),
[data-theme="dark"] {
  :root {
    color-scheme: dark;
    --bg-body: #0d0d1a;
    --bg-alt: #1a1a2e;
    --bg-sidebar: #112;
    --text-main: #dde1e7;
    --text-muted: #8b90a0;
    --border-color: #2a2a40;
    --light-blue: #0a2a40;
    --legal-pad-yellow: #1a1810;
    --shadow-color: rgb(0, 0, 0, 0.4);
  }
}
```

### Verification
```bash
# Check that both behaviors still work
grep -A 10 "prefers-color-scheme: dark" styles.css
grep -A 2 "\[data-theme" styles.css
```

### Testing
- [ ] Load page in light mode → correct colors
- [ ] Load page in dark mode (system pref) → dark colors
- [ ] Toggle theme button → dark mode activates correctly
- [ ] No visual regression in components

---

## Task 3: Standardize Breakpoint Operators
**Duration:** 1.5–2 hours  
**Risk:** Medium (requires testing)  
**Files:** `styles.css` (15 @media queries)

### Current State (Inconsistent)

| Breakpoint | Inconsistent Patterns |
|------------|----------------------|
| `xl` | `width <`, `width >=`, `width <=` |
| `lg` | `width <`, `width <=` |
| `md` | `width <`, `width >=` |

### Problem
- Operator inconsistency makes logic hard to trace
- No clear mobile-first vs desktop-first pattern
- Difficult to predict breakpoint interactions

### Proposed Standard: Mobile-First Pattern

**Rule:** Use `width >=` to **add features** at larger sizes:
```css
/* Base styles: mobile first */
.component { /* 320px and up */ }

/* Add desktop features at lg */
@media (width >= var(--breakpoint-lg)) {
  .component { /* desktop enhancements */ }
}

/* Hide small-screen features at md+ */
@media (width >= var(--breakpoint-md)) {
  .mobile-only { display: none; }
}
```

**Avoid:** Mixing `<` and `>=` for the same semantic effect.

### Lines to Update

**Affected Queries (15 total):**

1. **Line 898:** `@media (width < var(--breakpoint-xl))` 
   - → Rewrite as "hide right sidebar at xl" (keep <)

2. **Line 906:** `@media (width < var(--breakpoint-lg))`
   - → Rewrite as mobile-first equivalent

3. **Line 921:** `@media (width < var(--breakpoint-md))`
   - → Rewrite as mobile-first equivalent

... (12 more to audit)

### Verification Checklist
- [ ] All `@media` queries follow mobile-first pattern
- [ ] Document intended behavior at each breakpoint
- [ ] Test at 320px, 640px, 768px, 1024px, 1440px widths
- [ ] Verify no "dead" rules (e.g., `< lg` inside `>= lg` block)

### Testing Matrix

Test these viewports for each component:
```
xs:  320px  → base styles
sm:  640px  → enhanced layout
md:  768px  → tablet layout
lg:  1024px → desktop features
xl:  1440px → full-width layout
```

Example test case:
```html
<!-- Component: .home-layout-3col -->
320px:  flexbox single column
640px:  flexbox single column (same)
768px:  grid 2-column (sidebar + content)
1024px: grid 3-column (sidebar + content + toc)
1440px: grid 3-column full-width (same as 1024px)
```

---

## Task 4: Create Responsive Behavior Test Plan
**Duration:** 1 hour (documentation)  
**Risk:** Low (reference, no code changes)  
**Deliverable:** `docs/css-responsive-test-plan.md`

### Test Cases to Document

For each breakpoint transition, verify:
- [ ] Layout shifts happen at correct breakpoint
- [ ] No content overflow at edge widths
- [ ] All interactive elements remain accessible
- [ ] No visual glitches (spacing, alignment)
- [ ] Typography remains readable

### Example Test Template
```markdown
## Test: Standard Page Layout at Breakpoints

### xs (320px) — Mobile
- [ ] Sidebar hidden or stacked
- [ ] Content full width
- [ ] No horizontal scroll

### md (768px) — Tablet
- [ ] Sidebar appears alongside content
- [ ] Content area 2-column grid
- [ ] TOC still hidden

### xl (1440px) — Desktop
- [ ] 3-column layout active
- [ ] Sidebar (left) + Content (center) + TOC (right)
- [ ] Max-width enforced (1400px)
```

---

## Task 5: Breakpoint Definition Cleanup
**Duration:** 10–15 min  
**Risk:** Low  
**Files:** `css/breakpoints.css` (legacy), `css/tokens/breakpoints.css` (modern)

### Current State
- Two breakpoint definition files exist
- `css/breakpoints.css` (imported, legacy)
- `css/tokens/breakpoints.css` (in token system, modern)

### Action (Phase 2b)
1. Verify both define identical values (✓ confirmed)
2. Update imports: use only `css/design-tokens.css` (which imports tokens version)
3. Delete legacy `css/breakpoints.css` after Phase 3 testing

### Verification
```bash
# Confirm identical definitions
diff <(grep "breakpoint" css/breakpoints.css) \
     <(grep "breakpoint" css/tokens/breakpoints.css)
```

---

## Phase 2 Checklist

### Pre-Work
- [ ] Read this roadmap
- [ ] Review audit findings (`docs/css-audit-2953.md`)
- [ ] Understand current !important usage

### Implementation
- [ ] Task 1: Activate design-tokens.css (2 min)
- [ ] Task 2: Consolidate dark mode (15 min)
- [ ] Task 3: Standardize breakpoints (1.5 hrs)
- [ ] Task 4: Document test plan (1 hr)
- [ ] Task 5: Cleanup breakpoint defs (10 min)

### Testing
- [ ] CSS compiles without errors
- [ ] All media queries work at target breakpoints
- [ ] Dark mode toggle works (both methods)
- [ ] Visual regression testing at all breakpoints
- [ ] Light/dark mode appearance verified
- [ ] Accessibility: reduced motion still works

### Code Review
- [ ] All @media query operators consistent
- [ ] No new !important declarations
- [ ] Comments updated for clarity
- [ ] Commit message references #2953

### Handoff to Phase 3
- [ ] Phase 2 complete, merge to main
- [ ] Create Phase 3 sub-issue for token integration
- [ ] Document blockers (if any)

---

## Rollback Plan

If issues arise:
1. **Design tokens import breaks?** → Remove import, revert to inline `:root` variables
2. **Dark mode toggle fails?** → Revert to two separate blocks
3. **Breakpoint changes cause layout issues?** → Revert @media operators, re-test with original pattern

All changes are isolated and reversible without breaking existing functionality.

---

## Success Criteria

✓ Design token system is imported and available  
✓ Dark mode variables defined once (DRY)  
✓ All breakpoint operators follow mobile-first pattern  
✓ Responsive behavior documented and tested  
✓ No visual regression at any breakpoint  
✓ All 5 standard breakpoints working correctly  

---

**Next:** Create Phase 3 issue for design token integration (color, animation, border extraction).

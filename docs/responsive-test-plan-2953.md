# Responsive Design Test Plan — CSS Issue #2953

## Objective

Validate that all page layouts render correctly at standardized breakpoints after breakpoint operator standardization (Phase 2, task 4).

## Breakpoints

| Breakpoint | Size | Device Type | Test Notes |
|-----------|------|-------------|-----------|
| **xs** | 320px | Old phones | Minimum supported width |
| **sm** | 640px | Large phones | Modern smartphone |
| **md** | 768px | Tablets | Tablet portrait |
| **lg** | 1024px | Small laptops | Desktop minimum |
| **xl** | 1440px | Wide desktop | Design maximum |

## Test Environment Setup

### Browser DevTools (Recommended for CI)

```bash
# Test using Chrome DevTools responsiveness
# Or use Playwright for automated E2E tests (existing: tests/e2e/touch-targets.spec.js)
npx playwright test --project=chromium --headed
```

### Manual Testing Widths

Test at exact breakpoint values:
- **319px** → Expected: xs-specific styles
- **320px** → Expected: xs styles activate
- **639px** → Expected: sm styles NOT active
- **640px** → Expected: sm styles activate
- **767px** → Expected: md styles NOT active
- **768px** → Expected: md styles activate
- **1023px** → Expected: lg styles NOT active
- **1024px** → Expected: lg styles activate
- **1439px** → Expected: xl styles NOT active
- **1440px** → Expected: xl styles activate

## Critical Page Elements to Validate

### 1. Layout & Sidebars

**Pages Tested:** Home, standard pages with sidebars

| Breakpoint | Left Sidebar | Right Sidebar | Main Content | Layout Type |
|-----------|--------|---------|---------|------------|
| **xs–sm** | Hidden | Hidden | 100% width | Single flex column |
| **md–lg** | 240px fixed | Hidden | 1fr | 2-column grid |
| **xl** | 280px fixed | 250px fixed | 1fr | 3-column grid |

**Validation:**
- [ ] Left sidebar width matches `--sidebar-width`
- [ ] Right sidebar visibility matches expectation
- [ ] Main content reflows smoothly (no overflow)
- [ ] Gap between columns matches `--sidebar-gap`

### 2. Typography Scaling

**Elements Tested:** h1, h2, h3, p, code blocks

| Breakpoint | h1 Size | h2 Size | h3 Size | p Size |
|-----------|---------|---------|---------|--------|
| **xs–md** | 1.5rem (24px) | 1.35rem | 1.25rem | 1rem |
| **md+** | 2.5rem (40px) | 2rem | 1.5rem | 1.125rem |

**Validation:**
- [ ] Headings scale smoothly (use fluid `clamp()` where applicable)
- [ ] Line-height remains readable (min 1.4 for body, 1.2 for headings)
- [ ] Code blocks don't overflow on narrow screens

### 3. Navigation & Header

**Elements Tested:** Navbar, mobile menu, breadcrumbs

| Breakpoint | Navbar Layout | Mobile Menu | Breadcrumbs |
|-----------|--------|--------|-----------|
| **xs–md** | Collapsed mobile hamburger | Vertical stack | Single line |
| **md+** | Full horizontal | Hidden | Visible |

**Validation:**
- [ ] Mobile menu opens/closes without layout shift
- [ ] Hamburger icon at least 44×44px (WCAG 2.5.5)
- [ ] Navbar logo fits without wrapping
- [ ] Breadcrumbs don't overflow

### 4. Content Cards & Grids

**Elements Tested:** Resource cards, bibliography items, critics-corner comments

**Validation (at each breakpoint):**
- [ ] Cards stack vertically on small screens
- [ ] Cards arrange in 2+ columns on tablets
- [ ] Gap between cards matches design token
- [ ] No text overflow in card titles/descriptions
- [ ] Images scale responsively (max-width: 100%)

### 5. Forms & Interactive Elements

**Elements Tested:** Input fields, buttons, select dropdowns, contact form

**Validation:**
- [ ] Input fields full width on mobile
- [ ] Buttons at least 44×44px (touch targets)
- [ ] Form labels don't overlap inputs
- [ ] Textarea has adequate line-height for mobile typing
- [ ] Error messages readable without overflow

### 6. Accessibility: Touch Targets

**Target Size:** Minimum 44×44px per WCAG 2.5.5

**Elements to Check:**
- Buttons (primary, copy, sort)
- Links in navigation
- Form inputs & checkboxes
- Close buttons (lightbox, modals)
- Expand/collapse toggles

**Tools:**
```bash
# Automated E2E test (existing)
npx playwright test tests/e2e/touch-targets.spec.js
```

## Test Execution Matrix

### Automated Testing (CI)

```bash
# Run existing Playwright tests
npx playwright test

# Run specific breakpoint test
npx playwright test --project=chromium-mobile
```

### Manual Spot Checks

1. **Start at widest (xl = 1440px)**
   - Verify 3-column layout (left sidebar, main, right sidebar)
   - Check all typography sizes
   - Verify all images load and scale

2. **Resize down to lg (1024px)**
   - Check 2-column layout maintained
   - Verify right sidebar hiding (if applicable)
   - Check for any text overflow

3. **Resize down to md (768px)**
   - Verify 2-column grid (left sidebar + main)
   - Check for mobile menu appearing
   - Verify horizontal scrolling not occurring

4. **Resize down to sm (640px)**
   - Verify single-column flex layout
   - Check sidebar hidden
   - Verify mobile menu operational
   - Test form inputs full-width

5. **Resize down to xs (320px)**
   - Verify layout still valid
   - Check minimum widths on all elements
   - Verify text readable without zoom

## Edge Cases to Test

- [ ] **Long URLs** in text (should wrap or break gracefully)
- [ ] **Long function names** in code blocks (should allow horizontal scroll, not break layout)
- [ ] **Large tables** (responsive scroll table, not horizontal scroll on page)
- **Form inputs with labels** (label above input on mobile, beside on desktop)
- [ ] **Images in content** (max-width: 100%, scale with container)
- [ ] **Deep nesting** (headings, lists, blockquotes should maintain indentation at all sizes)
- [ ] **Color contrast** on all backgrounds (test dark mode at each breakpoint)

## Dark Mode Validation

Test these checks at each breakpoint in both light and dark modes:
- [ ] Text contrast ratio ≥ 4.5:1 (normal), 3:1 (large text)
- [ ] Interactive elements distinguishable from background
- [ ] Icons rendering correctly with --text-main and --text-muted
- [ ] Borders visible with --border-color

## Sign-Off Checklist

**Pre-Merge (Developer):**
- [ ] All breakpoints tested in Chrome DevTools
- [ ] E2E Playwright tests pass
- [ ] No console errors in browser DevTools
- [ ] Touch targets verified (44×44px minimum)
- [ ] Dark mode tested at 2+ breakpoints
- [ ] Mobile menu toggle works (xs–md)
- [ ] No horizontal scrolling anywhere
- [ ] Typography readable without zoom

**Post-Merge (QA):**
- [ ] Verify on physical devices (phone, tablet, desktop)
- [ ] Test on Safari, Firefox, Edge (if relevant)
- [ ] Verify print layout (if applicable)
- [ ] Test keyboard navigation at each breakpoint
- [ ] Verify screen reader experience (NVDA, JAWS)

## Related Issues

- **#2953** — CSS Architecture Audit (this issue)
- **#2954** — MathJax MML for screen readers
- **#2955** — WCAG 2.5.5 touch target size (related E2E tests in `tests/e2e/touch-targets.spec.js`)

## Implementation Notes

This test plan covers Phase 2 work:
- ✅ Task 1: Design tokens import (commit c31e80c9)
- ✅ Task 2: Dark mode consolidation (commit 0509d897)
- ✅ Task 3: Breakpoint operator standardization (commit 76eaed78)
- 📋 Task 4: Responsive test plan (this document)
- ⏳ Task 5: Cleanup redundant definitions (pending)

**Test Execution:** Run this plan after each Phase 2 task completion to catch regressions early.

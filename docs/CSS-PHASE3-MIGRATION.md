# CSS Phase 3: Design Token Migration Guide

Migration strategy for consolidating styles.css to use design tokens (issue #2969).

## Current Status

- **Phase 1**: Design token system created (8 files, 200+ variables) ✅
- **Phase 2**: Breakpoint standardization (5 breakpoints) ✅  
- **Phase 3**: Migrate monolithic styles.css to use tokens (THIS)
- **Phase 4**: Component-based CSS architecture (modularization)

## What Are Design Tokens?

Design tokens are CSS custom properties that define design values once and reuse them:

```css
/* Token Definition (css/tokens/colors.css) */
:root {
  --color-primary-main: #3b82f6;
  --color-primary-dark: #1e40af;
}

/* Usage in styles.css */
button {
  background: var(--color-primary-main);
}
button:hover {
  background: var(--color-primary-dark);
}

/* Dark mode automatic */
[data-theme="dark"] {
  --color-primary-main: #60a5fa;
  --color-primary-dark: #3b82f6;
}
/* Styles automatically update! */
```

## Migration Strategy

### Phase 3 Approach: Incremental Migration

Rather than a complete rewrite, migrate sections strategically:

```
Week 1: Colors & typography
Week 2: Spacing & layout
Week 3: Dark mode completion
Week 4: Cleanup & refinement
```

### Step 1: Replace Color Values

**Before:**
```css
.button {
  background: #3b82f6;
  color: white;
  border: 1px solid #2563eb;
}
```

**After:**
```css
.button {
  background: var(--color-primary-main);
  color: var(--color-text-inverted);
  border: 1px solid var(--color-primary-dark);
}
```

### Step 2: Replace Spacing Values

**Before:**
```css
.container {
  padding: 1.5rem 2rem;
  margin-bottom: 2rem;
  gap: 1rem;
}
```

**After:**
```css
.container {
  padding: var(--spacing-md) var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  gap: var(--spacing-sm);
}
```

### Step 3: Replace Typography Values

**Before:**
```css
body {
  font-family: 'Inter', sans-serif;
  font-size: 16px;
  line-height: 1.6;
  font-weight: 400;
}
h1 {
  font-size: 2.5rem;
  font-weight: 700;
  line-height: 1.2;
}
```

**After:**
```css
body {
  font-family: var(--font-family-base);
  font-size: var(--font-size-base);
  line-height: var(--line-height-normal);
  font-weight: var(--font-weight-normal);
}
h1 {
  font-size: var(--font-size-h1);
  font-weight: var(--font-weight-bold);
  line-height: var(--line-height-heading);
}
```

### Step 4: Remove !important Declarations

**Before:**
```css
.override {
  color: red !important;
  display: block !important;
}
```

**After:**
```css
/* Use proper CSS specificity instead */
.container .override {
  color: var(--color-error-main);
  display: block;
}

/* Or use specific selector hierarchy */
.container > .override {
  color: var(--color-error-main);
}
```

## Available Token Variables

### Colors

```css
/* Primary colors */
--color-primary-main    /* #3b82f6 */
--color-primary-dark    /* #1e40af */
--color-primary-light   /* #dbeafe */

/* Semantic colors */
--color-success-main    /* #10b981 */
--color-warning-main    /* #f59e0b */
--color-error-main      /* #ef4444 */
--color-info-main       /* #0284c7 */

/* Text colors */
--color-text-primary    /* #1f2937 */
--color-text-secondary  /* #6b7280 */
--color-text-light      /* #9ca3af */
--color-text-inverted   /* #ffffff */

/* Backgrounds */
--color-bg-base         /* #ffffff */
--color-bg-alt          /* #f9fafb */
--color-bg-hover        /* #f3f4f6 */
```

### Typography

```css
/* Font families */
--font-family-base      /* 'Inter', sans-serif */
--font-family-mono      /* 'Courier', monospace */
--font-family-serif     /* 'Georgia', serif */

/* Font sizes */
--font-size-xs          /* 0.75rem */
--font-size-sm          /* 0.875rem */
--font-size-base        /* 1rem */
--font-size-md          /* 1.125rem */
--font-size-lg          /* 1.5rem */
--font-size-h1          /* 2.5rem */
--font-size-h2          /* 2rem */
--font-size-h3          /* 1.5rem */

/* Font weights */
--font-weight-light     /* 300 */
--font-weight-normal    /* 400 */
--font-weight-medium    /* 500 */
--font-weight-bold      /* 700 */

/* Line heights */
--line-height-tight     /* 1.2 */
--line-height-normal    /* 1.6 */
--line-height-relaxed   /* 1.8 */
```

### Spacing

```css
/* Base unit: 0.25rem (4px) */
--spacing-xs            /* 0.25rem */
--spacing-sm            /* 0.5rem */
--spacing-md            /* 1rem */
--spacing-lg            /* 1.5rem */
--spacing-xl            /* 2rem */
--spacing-2xl           /* 3rem */

/* Semantic spacing */
--padding-compact       /* 0.5rem */
--padding-normal        /* 1rem */
--padding-spacious      /* 1.5rem */

--margin-compact        /* 0.5rem */
--margin-normal         /* 1rem */
--margin-spacious       /* 1.5rem */

--gap-tight             /* 0.5rem */
--gap-normal            /* 1rem */
--gap-loose             /* 2rem */
```

### Breakpoints

```css
/* Responsive breakpoints */
--breakpoint-xs         /* 320px */
--breakpoint-sm         /* 640px */
--breakpoint-md         /* 768px */
--breakpoint-lg         /* 1024px */
--breakpoint-xl         /* 1440px */
```

### Dark Mode

Tokens automatically adjust. Example:

```css
/* Light mode (default) */
:root {
  --color-text-primary: #1f2937; /* dark gray */
  --color-bg-base: #ffffff;      /* white */
}

/* Dark mode */
[data-theme="dark"] {
  --color-text-primary: #e5e7eb; /* light gray */
  --color-bg-base: #0f172a;      /* dark blue */
}
```

## !important Removal Strategy

### Why Remove !important?

1. **Indicates specificity problems** - proper CSS hierarchy shouldn't need it
2. **Makes overrides difficult** - emergency sledgehammer for bad architecture
3. **Harder to maintain** - harder to understand intent
4. **Bad practice** - violates CSS best practices

### How to Remove It

**Problem:** `.element { color: red !important; }`

**Solution 1: Increase Specificity**
```css
/* Change from .element to .container .element */
.container .element {
  color: var(--color-error-main);
}
```

**Solution 2: Add ID if necessary**
```css
#main .element {
  color: var(--color-error-main);
}
```

**Solution 3: Use CSS Cascade**
```css
/* Define base styles first */
.element {
  color: var(--color-text-primary);
}

/* Override in more specific context */
.dark-theme .element {
  color: var(--color-text-inverted);
}
```

**Solution 4: Use Attribute Selectors**
```css
/* Before */
.special { background: red !important; }

/* After */
[data-special="true"] {
  background: var(--color-accent);
}
```

## Audit & Testing Checklist

- [ ] Replace all hardcoded colors with --color-* tokens
- [ ] Replace all hardcoded spacing with --spacing-* tokens
- [ ] Replace all font sizes with --font-size-* tokens
- [ ] Replace all fonts with --font-family-* tokens
- [ ] Remove all !important declarations (count: ? → 0)
- [ ] Verify dark mode works automatically
- [ ] Test on all breakpoints (xs, sm, md, lg, xl)
- [ ] Visual regression testing (screenshot comparison)
- [ ] No console errors in DevTools
- [ ] Performance: no regression in paint/layout time

## Examples

### Example 1: Card Component

**Before:**
```css
.card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border: 1px solid #e5e7eb;
  margin-bottom: 20px;
}
.card h3 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 10px;
  color: #1f2937;
}
.card p {
  color: #6b7280;
  font-size: 14px;
  line-height: 1.6;
}
```

**After:**
```css
.card {
  background: var(--color-bg-base);
  padding: var(--spacing-lg);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-light);
  margin-bottom: var(--spacing-lg);
}
.card h3 {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-bold);
  margin-bottom: var(--spacing-sm);
  color: var(--color-text-primary);
}
.card p {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  line-height: var(--line-height-normal);
}
```

### Example 2: Button Component

**Before:**
```css
.button {
  background: #3b82f6;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
}
.button:hover {
  background: #1e40af !important;
}
.button.disabled {
  background: #d1d5db !important;
  cursor: not-allowed !important;
}
```

**After:**
```css
.button {
  background: var(--color-primary-main);
  color: var(--color-text-inverted);
  padding: var(--spacing-sm) var(--spacing-md);
  border: none;
  border-radius: var(--border-radius-sm);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-bold);
  cursor: pointer;
  transition: background-color var(--animation-fast) ease-in-out;
}
.button:hover {
  background: var(--color-primary-dark);
}
.button:disabled {
  background: var(--color-bg-disabled);
  cursor: not-allowed;
}
```

## Tools for Migration

### Automated Refactoring
```bash
# VS Code Find & Replace (Regex mode)
# Find: (#[0-9a-f]{6}|rgb\([^)]+\))
# Replace: var(--color-*)  [requires manual review]
```

### Manual Audit
```bash
# Find all hardcoded values
grep -n "rgba\|rgb\|#[0-9a-f]" styles.css | wc -l

# Count !important declarations
grep -c "!important" styles.css
```

### Visual Testing
1. Screenshot baseline (main branch)
2. Make changes (feature branch)
3. Screenshot comparison tool
4. Compare side-by-side

## Success Criteria (Phase 3 Complete)

- [ ] 95%+ of CSS rules use design tokens
- [ ] 0 !important declarations (was 36)
- [ ] Dark mode complete for all components
- [ ] All color/spacing/typography values from tokens
- [ ] No visual regressions
- [ ] Performance maintained or improved
- [ ] Tests pass (Lighthouse, axe, visual regression)

## Timeline

- **Week 1**: Colors & typography migration (50% of styles.css)
- **Week 2**: Spacing & layout migration (30% of styles.css)
- **Week 3**: Dark mode completion & cleanup (20% of styles.css)
- **Week 4**: Testing, refinement, and documentation

## Next Phase (Phase 4)

After token migration is complete, Phase 4 will:
- Split monolithic styles.css into component modules
- Organize CSS by feature/component
- Reduce average file size
- Improve maintainability

## Questions?

Refer to:
- `css/design-tokens.css` - Central import
- `css/tokens/*.css` - Token definitions
- `docs/CSS-ARCHITECTURE.md` - Design system overview

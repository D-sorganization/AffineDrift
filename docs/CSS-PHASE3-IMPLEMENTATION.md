# CSS Phase 3: Implementation Progress

**Issue**: #2969 - CSS Phase 3: Migrate to design tokens, eliminate !important  
**Status**: In Progress  
**Target**: Replace hardcoded values with design tokens across styles.css and component CSS files

## Summary of Work

This document tracks the practical implementation of CSS Phase 3 migration as outlined in `CSS-PHASE3-MIGRATION.md`.

### Current State Analysis
- **styles.css**: 2,937 lines
- **Total !important declarations**: 70 (down from initial count)
  - css/print.css: 54 declarations (justified for print media)
  - css/resources.css: 3 declarations (grid layout)
  - css/startup-launcher.css: 1 declaration
- **Hardcoded color values**: 49 unique hex colors + 17 RGB values
- **Top color usage**:
  - #fff: 7 times
  - #17a2b8: 7 times (info/secondary brand)
  - #dc3545: 5 times (error)
  - #28a745: 4 times (success)

### High-Impact Components for Migration (Priority Order)

1. **Form Elements** (80+ references) - Highest impact
   - inputs, selects, textareas, checkboxes
   - Target: Replace border, background, text colors with tokens

2. **Header/Navigation** (68 references)
   - .navbar, header, nav-links
   - Target: Use semantic color tokens

3. **Sidebar** (57 references)
   - .left-sidebar, .right-sidebar, sticky content
   - Target: Background and text colors

4. **Layout** (50 references)
   - .page-columns, .standard-page-layout
   - Target: Spacing and background colors

5. **Navigation** (24 references)
   - Links, active states, hover effects
   - Target: Color tokens for interactive states

6. **Buttons** (22 references)
   - Button styles, .btn classes
   - Target: Color, background, hover states

7. **Links** (22 references)
   - Anchor elements, hover states
   - Target: Color tokens

8. **Math Display** (22 references)
   - .math class styles
   - Target: Colors and backgrounds

9. **Code Elements** (15 references)
   - pre, code, .code-block
   - Target: Background, border, text colors

10. **Tables** (10 references)
    - table elements
    - Target: Border, background, text colors

## Migration Phases

### Phase 3a: Form Elements Migration
**Status**: TODO

**Steps:**
1. Create comprehensive form token definitions (input states, focus, valid, invalid)
2. Update all input types: text, email, password, search, number, range
3. Update select, textarea, checkbox, radio styles
4. Add focus states with proper tokens
5. Update validation states (error, success, warning)

**Before**:
```css
input[type="text"],
input[type="email"],
select {
  border: 1px solid #ddd;
  padding: 0.5rem;
  background: white;
}

input:focus {
  border-color: #17a2b8;
}

input.error {
  border-color: #dc3545;
}
```

**After**:
```css
input[type="text"],
input[type="email"],
select {
  border: var(--border-width-sm) solid var(--color-border-default);
  padding: var(--spacing-sm);
  background: var(--bg-primary);
}

input:focus {
  border-color: var(--color-primary-light);
  outline: var(--border-width-sm) solid var(--color-focus);
}

input.error {
  border-color: var(--color-error);
}
```

### Phase 3b: Header & Navigation Migration
**Status**: TODO

### Phase 3c: Sidebar & Layout Migration
**Status**: TODO

### Phase 3d: Interactive Elements (Buttons, Links)
**Status**: TODO

### Phase 3e: Utility & Specialized Components
**Status**: TODO

### Phase 3f: !important Removal Strategy
**Status**: TODO

**Priority**: 
1. Print styles - Already justified with @media print
2. Resources grid - Needs specificity review
3. Startup launcher - Single usage, low impact

## Design Token Status

### Available Token Categories

**Colors** (40+ variables):
- Primary brand: --color-primary-dark, --color-primary-main, --color-primary-light, --color-primary-lightest
- Semantic: --color-success, --color-error, --color-warning, --color-info
- Neutral: --color-neutral-0 through --color-neutral-900
- Functional: --bg-primary, --bg-secondary, --bg-tertiary, --text-primary, --text-secondary, --text-muted, --border-color

**Typography** (30+ variables):
- Font families: --font-family-serif, --font-family-sans-serif
- Font sizes: --fs-h1 through --fs-xs
- Weights: --font-weight-light, --font-weight-normal, --font-weight-bold
- Line heights: --line-height-tight, --line-height-normal, --line-height-relaxed

**Spacing** (35+ variables):
- Scale: --spacing-xs through --spacing-xl
- Gap: --gap-xs, --gap-sm, --gap-md, --gap-lg, --gap-xl

**Other Tokens**:
- Shadows: 10+ elevation levels
- Animations: Timing, easing, transitions
- Borders: Radius and width configurations
- Z-Index: 20+ stacking levels

## Metrics & Success Criteria

### Target Goals
- [ ] Replace 400+ hardcoded color values with CSS variables
- [ ] Replace 300+ spacing values with CSS variables
- [ ] Replace 200+ typography values with CSS variables
- [ ] Reduce !important usage from 70 to <5 (print-only justified)
- [ ] Achieve 100% dark mode support with automatic theming
- [ ] Maintain or improve CSS file size efficiency

### Current State
- Hardcoded colors: 49 unique hex + 17 RGB = 66 values
- Hardcoded spacing: ~200+ instances
- Hardcoded typography: ~150+ instances
- !important declarations: 70 total

### Progress Tracking

| Component | Status | Hardcoded Values | Token Usage | !important | Notes |
|-----------|--------|------------------|-------------|-----------|-------|
| Form Elements | TODO | ~80 refs | 0% | - | Highest priority |
| Header/Nav | TODO | ~68 refs | 0% | - | High impact |
| Sidebar | TODO | ~57 refs | 0% | - | Medium priority |
| Layout | TODO | ~50 refs | 0% | - | Core infrastructure |
| Navigation | TODO | ~24 refs | 0% | - | Interactive |
| Buttons | TODO | ~22 refs | 0% | - | Interactive |
| Links | TODO | ~22 refs | 0% | - | Interactive |
| Math | TODO | ~22 refs | 0% | - | Display-specific |
| Code | TODO | ~15 refs | 0% | - | Specialized |
| Tables | TODO | ~10 refs | 0% | - | Lowest priority |

## Testing Strategy

### Automated Testing
- [ ] CSS parsing validation
- [ ] Variable reference resolution
- [ ] Dark mode color contrast (WCAG AA minimum)
- [ ] Light mode color contrast (WCAG AA minimum)
- [ ] CSS file size comparison

### Manual Testing
- [ ] Light mode visual regression
- [ ] Dark mode visual regression
- [ ] Form input states (focus, hover, active, disabled, error)
- [ ] Interactive elements (buttons, links, navigation)
- [ ] Mobile responsiveness
- [ ] Print preview

### Browser Testing
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile Chrome
- [ ] Mobile Safari

## Files Modified

- `styles.css` - Main stylesheet (2,937 lines)
- `css/tokens/*.css` - Token definitions (existing)
- `css/print.css` - Print media !important usage justified
- `css/resources.css` - Resource grid layout
- `css/startup-launcher.css` - Launcher styles

## Dependencies & Conflicts

- **Quarto CSS**: Override selectors need review
- **Bootstrap classes**: Maintain compatibility where used
- **Dark mode**: Ensure prefers-color-scheme and [data-theme] work together
- **Print media**: @media print rules may need restructuring

## Known Issues & Blockers

1. **Merge conflicts in styles.css** - Resolved by taking current upstream
2. **Dark mode color values** - Need to verify all color tokens have dark mode pairs
3. **Print styles** - !important usage is justified but should be documented
4. **Legacy color variables** - Some hardcoded hex still in :root may conflict

## Next Steps

1. Create comprehensive form token definitions (if needed)
2. Audit current token completeness
3. Begin systematic component migration in priority order
4. Create before/after test suite
5. Submit PR with Phase 3a (Form Elements)
6. Iterate through remaining components
7. Final audit for remaining !important declarations
8. Full regression testing

## References

- `docs/CSS-PHASE3-MIGRATION.md` - Strategy and examples
- `css/design-tokens.css` - Token import file
- `css/tokens/` - Individual token files
- Issue #2969 - GitHub issue tracker

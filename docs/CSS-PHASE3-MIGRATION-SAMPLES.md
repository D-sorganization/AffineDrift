# CSS Phase 3: Migration Code Samples

**Issue**: #2969  
**Purpose**: Practical before/after examples for migrating styles.css to design tokens

## Form Elements Migration (Highest Priority)

### Text Input Fields

**Before** (current hardcoded):
```css
input[type="text"],
input[type="email"],
input[type="password"],
input[type="search"],
input[type="number"],
textarea {
  border: 1px solid #ddd;
  padding: 0.5rem;
  background: white;
  color: #212529;
  font-size: 1rem;
  font-family: inherit;
  border-radius: 4px;
}

input[type="text"]:focus,
input[type="email"]:focus,
input[type="password"]:focus,
input[type="search"]:focus,
input[type="number"]:focus,
textarea:focus {
  outline: none;
  border-color: #17a2b8;
  box-shadow: 0 0 0 3px rgba(23, 162, 184, 0.1);
}

input[type="text"]:disabled,
input[type="email"]:disabled,
textarea:disabled {
  background: #f3f4f6;
  color: #6b7280;
  cursor: not-allowed;
}

input[type="text"].error,
input[type="email"].error {
  border-color: #dc3545;
}

input[type="text"].success,
input[type="email"].success {
  border-color: #28a745;
}
```

**After** (using design tokens):
```css
input[type="text"],
input[type="email"],
input[type="password"],
input[type="search"],
input[type="number"],
textarea {
  border: var(--input-border-width) var(--border-style-solid) var(--input-border-color);
  padding: var(--padding-sm);
  background: var(--input-background);
  color: var(--input-text-color);
  font-size: var(--fs-base);
  font-family: inherit;
  border-radius: var(--radius-input);
  transition: var(--transition-colors);
}

input[type="text"]:hover,
input[type="email"]:hover,
textarea:hover {
  border-color: var(--input-hover-border-color);
  background: var(--input-hover-background);
}

input[type="text"]:focus,
input[type="email"]:focus,
input[type="password"]:focus,
input[type="search"]:focus,
input[type="number"]:focus,
textarea:focus {
  outline: var(--input-focus-outline);
  outline-offset: var(--input-focus-outline-offset);
  border-color: var(--input-focus-border-color);
  box-shadow: var(--input-focus-box-shadow);
}

input[type="text"]:disabled,
input[type="email"]:disabled,
textarea:disabled {
  background: var(--input-disabled-background);
  color: var(--input-disabled-color);
  cursor: var(--input-disabled-cursor);
  opacity: var(--disabled-opacity);
}

input[type="text"].error,
input[type="email"].error {
  border-color: var(--state-error-border);
  background: var(--state-error-bg);
}

input[type="text"].success,
input[type="email"].success {
  border-color: var(--state-success-border);
  background: var(--state-success-bg);
}
```

### Select Dropdown

**Before**:
```css
select {
  border: 1px solid #ddd;
  padding: 0.5rem;
  background: white;
  color: #212529;
  border-radius: 4px;
}

select:focus {
  outline: none;
  border-color: #17a2b8;
  box-shadow: 0 0 0 3px rgba(23, 162, 184, 0.1);
}
```

**After**:
```css
select {
  border: var(--input-border-width) var(--border-style-solid) var(--input-border-color);
  padding: var(--padding-sm);
  background: var(--input-background);
  color: var(--input-text-color);
  border-radius: var(--radius-input);
  transition: var(--transition-colors);
}

select:hover {
  border-color: var(--input-hover-border-color);
}

select:focus {
  outline: var(--input-focus-outline);
  outline-offset: var(--input-focus-outline-offset);
  border-color: var(--input-focus-border-color);
  box-shadow: var(--input-focus-box-shadow);
}
```

### Checkboxes & Radio Buttons

**Before**:
```css
input[type="checkbox"],
input[type="radio"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #17a2b8;
}

input[type="checkbox"]:focus,
input[type="radio"]:focus {
  outline: 2px solid #17a2b8;
  outline-offset: 2px;
}

input[type="checkbox"]:disabled,
input[type="radio"]:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
```

**After**:
```css
input[type="checkbox"],
input[type="radio"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--color-primary-main);
  transition: var(--transition-colors);
}

input[type="checkbox"]:hover,
input[type="radio"]:hover {
  accent-color: var(--color-primary-light);
}

input[type="checkbox"]:focus,
input[type="radio"]:focus {
  outline: var(--input-focus-outline);
  outline-offset: var(--input-focus-outline-offset);
}

input[type="checkbox"]:disabled,
input[type="radio"]:disabled {
  cursor: var(--disabled-cursor);
  opacity: var(--disabled-opacity);
  accent-color: var(--disabled-border-color);
}
```

## Header & Navigation Migration

### Navigation Links

**Before**:
```css
.nav-links a {
  color: #0f4c75;
  text-decoration: none;
  padding: 0.5rem 1rem;
  transition: color 0.2s ease;
}

.nav-links a:hover {
  color: #205d86;
  text-decoration: underline;
}

.nav-links a.active {
  color: #1a1a2e;
  font-weight: bold;
  border-bottom: 2px solid #0f4c75;
}

.nav-links a:focus {
  outline: 2px solid #205d86;
  outline-offset: 2px;
}
```

**After**:
```css
.nav-links a {
  color: var(--link-color);
  text-decoration: none;
  padding: var(--padding-sm) var(--padding-md);
  transition: var(--transition-colors);
}

.nav-links a:hover {
  color: var(--link-hover-color);
  text-decoration: var(--hover-text-decoration);
}

.nav-links a.active {
  color: var(--link-active-color);
  font-weight: var(--font-weight-bold);
  border-bottom: var(--border-width-md) var(--border-style-solid) var(--color-primary-main);
}

.nav-links a:focus {
  outline: var(--focus-ring);
  outline-offset: var(--focus-ring-offset);
  border-radius: var(--radius-sm);
}
```

### Header

**Before**:
```css
header {
  background: white;
  padding: 1rem 2rem;
  border-bottom: 1px solid #e9ecef;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

header h1 {
  margin: 0;
  color: #0f4c75;
  font-size: 1.5rem;
}
```

**After**:
```css
header {
  background: var(--bg-primary);
  padding: var(--padding-md) var(--padding-lg);
  border-bottom: var(--border-width-default) var(--border-style-solid) var(--border-color);
  position: sticky;
  top: 0;
  z-index: var(--z-header);
  box-shadow: var(--shadow-sm);
}

header h1 {
  margin: 0;
  color: var(--color-primary-main);
  font-size: var(--fs-h2);
}
```

## Button Migration

### Primary Button

**Before**:
```css
button,
.btn {
  background: #0f4c75;
  color: white;
  border: 1px solid #0f4c75;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  transition: all 0.2s ease;
  min-height: 44px;
}

button:hover,
.btn:hover {
  background: #205d86;
  border-color: #205d86;
}

button:active,
.btn:active {
  background: #1a1a2e;
  transform: scale(0.98);
}

button:disabled,
.btn:disabled {
  background: #bbb;
  cursor: not-allowed;
  opacity: 0.6;
}

button:focus,
.btn:focus {
  outline: 2px solid #205d86;
  outline-offset: 2px;
}
```

**After**:
```css
button,
.btn {
  background: var(--btn-primary-bg);
  color: var(--btn-primary-color);
  border: var(--border-width-default) var(--border-style-solid) var(--btn-primary-border);
  padding: var(--padding-sm) var(--padding-md);
  border-radius: var(--radius-button);
  cursor: pointer;
  font-size: var(--fs-base);
  font-weight: var(--font-weight-bold);
  transition: var(--transition-colors);
  min-height: 44px;
}

button:hover,
.btn:hover {
  background: var(--btn-primary-hover-bg);
  border-color: var(--btn-primary-hover-border);
}

button:active,
.btn:active {
  background: var(--btn-primary-active-bg);
  transform: var(--active-transform);
}

button:disabled,
.btn:disabled {
  background: var(--btn-primary-disabled-bg);
  border-color: var(--btn-primary-disabled-border);
  cursor: var(--disabled-cursor);
  opacity: var(--disabled-opacity);
}

button:focus,
.btn:focus {
  outline: var(--focus-ring);
  outline-offset: var(--focus-ring-offset);
  border-radius: var(--radius-button);
}
```

## Code Block Migration

**Before**:
```css
.code-block {
  background: #1a1a2e;
  color: #e0e0e0;
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
  font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, Courier, monospace;
  font-size: 0.9rem;
  margin: 1.5rem 0;
  border: 1px solid #374151;
}

.copy-btn {
  background: rgb(255, 255, 255, 0.1);
  border: 1px solid rgb(255, 255, 255, 0.2);
  color: #fff;
  padding: 0.5rem 0.75rem;
}

.copy-btn:hover {
  background: rgb(255, 255, 255, 0.2);
}

.copy-btn:focus {
  outline: 2px solid #205d86;
  outline-offset: 2px;
}
```

**After**:
```css
.code-block {
  background: var(--color-primary-dark);
  color: var(--color-neutral-300);
  padding: var(--padding-md);
  border-radius: var(--radius-lg);
  overflow-x: auto;
  font-family: var(--font-family-monospace);
  font-size: var(--fs-small);
  margin: var(--margin-lg) 0;
  border: var(--border-width-default) var(--border-style-solid) var(--color-neutral-700);
  transition: var(--transition-colors);
}

.copy-btn {
  background: rgba(255, 255, 255, var(--hover-opacity));
  border: var(--border-width-default) var(--border-style-solid) rgba(255, 255, 255, 0.2);
  color: var(--color-neutral-0);
  padding: var(--padding-sm) var(--padding-md);
  transition: var(--transition-colors);
}

.copy-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.copy-btn:focus {
  outline: var(--focus-ring);
  outline-offset: var(--focus-ring-offset);
  border-radius: var(--radius-sm);
}
```

## Dark Mode Example

The tokens automatically handle dark mode via `@media (prefers-color-scheme: dark)` and `[data-theme="dark"]` selector. No component-level changes needed!

**Example with design tokens** (no component CSS change):
```css
/* Light mode (default) */
input {
  background: white;              /* --input-background resolves to white */
  color: #212529;                 /* --input-text-color resolves to dark */
  border-color: #ddd;             /* --input-border-color resolves to light */
}

/* Dark mode - automatically switches via token definitions */
/* NO COMPONENT CSS CHANGES NEEDED - tokens handle it */
```

The token definitions in `css/tokens/interactive-states.css` and `css/tokens/colors.css` already include:
```css
@media (prefers-color-scheme: dark), [data-theme="dark"] {
  :root {
    --input-background: var(--color-neutral-800);  /* Dark */
    --input-text-color: var(--color-neutral-50);   /* Light */
    --input-border-color: var(--color-neutral-700); /* Dark */
  }
}
```

Result: All components automatically become dark-mode compatible!

## Migration Checklist

For each component being migrated:

1. [ ] Identify all hardcoded color values
2. [ ] Identify all hardcoded spacing/padding values
3. [ ] Identify all hardcoded typography values
4. [ ] Replace colors with semantic color tokens
5. [ ] Replace spacing with token scale
6. [ ] Replace typography with token scales
7. [ ] Add/update transitions using transition tokens
8. [ ] Verify focus states use focus ring tokens
9. [ ] Test light mode appearance
10. [ ] Test dark mode appearance (automatic)
11. [ ] Test reduced motion preference (automatic via tokens)
12. [ ] Run accessibility contrast checker
13. [ ] Test on mobile/responsive
14. [ ] Update component documentation

## Token Reference Quick Guide

### Colors
```css
--color-primary-main   /* Brand primary */
--color-primary-light  /* Primary lighter */
--color-primary-dark   /* Primary darker */
--color-success        /* Success semantic */
--color-error          /* Error semantic */
--color-warning        /* Warning semantic */
--color-info           /* Info semantic */
--bg-primary           /* Background primary */
--text-primary         /* Text primary */
--border-color         /* Border default */
```

### Spacing
```css
--spacing-xs through --spacing-2xl
--padding-xs through --padding-xl
--margin-xs through --margin-xl
--gap-xs through --gap-xl
```

### Typography
```css
--fs-h1 through --fs-xs  /* Font sizes */
--font-weight-light, --font-weight-normal, --font-weight-bold
--line-height-tight, --line-height-normal, --line-height-relaxed
```

### Interactive States
```css
--focus-ring                    /* Focus outline */
--input-focus-box-shadow        /* Focus shadow */
--transition-colors             /* Color transitions */
--transition-all                /* All transitions */
--disabled-opacity              /* Disabled state */
--btn-primary-hover-bg          /* Button hover */
```

### Borders & Radius
```css
--radius-sm, --radius-md, --radius-lg, --radius-xl
--radius-button, --radius-input, --radius-card
--border-width-default, --border-width-md, --border-width-lg
```

## Tips for Successful Migration

1. **Incremental approach** - Migrate one component at a time
2. **Test thoroughly** - Light, dark, mobile, accessible
3. **Use semantic names** - e.g., `--input-focus-color` not `--blue-light`
4. **Leverage defaults** - Most tokens have sensible defaults
5. **Document changes** - Update component docs as you go
6. **Reference guide** - Keep token names accessible to team
7. **Review before/after** - Visual regression testing is critical

## Resources

- `css/design-tokens.css` - Token imports and organization
- `css/tokens/*.css` - Individual token files
- `docs/CSS-PHASE3-MIGRATION.md` - Strategy overview
- `docs/CSS-PHASE3-IMPLEMENTATION.md` - Progress tracking

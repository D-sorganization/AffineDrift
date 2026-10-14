# Design System Component Gallery and Architecture

This document serves as the canonical design system reference and component gallery
for AffineDrift. It records the design token architecture, core reusable UI primitives,
and styling governance rules enforced across the site.

## Overview and Purpose

AffineDrift pairs rigorous biomechanical and control-theoretic analysis with an accessible,
consistent reader experience. The user interface relies on a modular CSS architecture
located in `css/tokens/` and `css/components/`, layered on top of Bootstrap and Quarto themes.

The primary goals of this architecture are:
1. **Single Source of Truth**: Centralize visual constants (colors, typography, spacing, breakpoints) into dedicated token files.
2. **Accessible Primitives**: Provide WCAG AA compliant interactive components with dark-mode support and high-contrast fallbacks.
3. **Cascade Predictability**: Eliminate aggressive global resets that conflict with third-party frameworks like Bootstrap.
4. **Architectural Hygiene**: Prevent stylesheet bloat via strict line and `!important` budget policies enforced by CI gates.

---

## Design Token Architecture

Design tokens form the foundation of visual styling across AffineDrift. All tokens are imported
in dependency order through `css/tokens/design-tokens.css`.

### Central Token Import (`design-tokens.css`)

The central manifest at `css/tokens/design-tokens.css` defines the loading order for all
design tokens before consuming stylesheets apply them:

1. `colors.css` (color palette and dark-mode remaps)
2. `typography.css` (font families, clamp-based fluid scales, weights, line heights)
3. `spacing.css` (spacing grid, component padding/margins, layout gaps)
4. `breakpoints.css` (viewport thresholds and responsive guidelines)
5. `shadows.css` (elevation levels)
6. `animations.css` (transitions and easing curves)
7. `borders.css` (border radius, widths, and styles)
8. `z-index.css` (layer stacking hierarchy)
9. `interactive-states.css` (focus rings, hover, active, and validation states)

### Semantic Color Palette (`colors.css`)

`css/tokens/colors.css` is the canonical single source of truth for color values in both light
and dark themes (issue #3224). Key color groups include:

- **Primary Brand Colors**:
  - `--color-primary-dark`: `#1a1a2e` (deep navy)
  - `--color-primary-main`: `#0f4c75` (classic brand blue)
  - `--color-primary-light`: `#3282b8` (mid blue)
  - `--color-primary-lightest`: `#e3f2fd` (soft tint)
- **Semantic Colors**:
  - `--color-success`: `#15803d`
  - `--color-error`: `#c82333`
  - `--color-warning`: `#ffc107`
  - `--color-info`: `#17a2b8`
- **Neutral Scale**:
  - `--color-neutral-0` (`#fff`) through `--color-neutral-900` (`#000`), with intermediate grays (`--color-neutral-50` through `--color-neutral-800`).
- **Okabe-Ito Colorblind-Safe Palette**:
  - `--color-orange`: `#e69f00`
  - `--color-sky-blue`: `#56b4e9`
  - `--color-green`: `#009e73`
  - `--color-yellow`: `#f0e442`
  - `--color-blue`: `#0072b2`
  - `--color-vermillion`: `#d55e00`
  - `--color-purple`: `#cc79a7`
  - `--color-gray`: `#999`
- **Functional Tokens**:
  - `--bg-primary`, `--bg-secondary`, `--bg-tertiary`, `--bg-dark`, `--bg-body`, `--bg-alt`, `--bg-sidebar`.
  - `--text-primary`, `--text-secondary`, `--text-main`, `--text-muted`, `--text-dark`, `--text-light`, `--text-inverse`.
  - `--border-color`, `--border-light`, `--shadow-color`.

Dark mode is centralized in `colors.css` using two symmetric gates:
1. `[data-theme="dark"]` for manual theme toggling.
2. `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { ... } }` for system preference with explicit light override precedence.

### Typography System (`typography.css`)

`css/tokens/typography.css` standardizes font stacks and responsive scaling:

- **Font Families**:
  - `--font-family-base`: System sans-serif stack (`-apple-system, blinkmacsystemfont, "Segoe UI", "Roboto", "Helvetica Neue", "Arial", sans-serif`).
  - `--font-family-heading`: Serif stack (`"Georgia", "Times New Roman", serif`), supplemented by self-hosted Playfair Display (`/fonts/playfair-display/`, #4557).
  - `--font-family-mono`: Monospace stack (`"SFMono-Regular", "Menlo", "Monaco", "Consolas", monospace`).
- **Fluid Font Sizes**:
  - Built with `clamp()` to scale gracefully between mobile viewports and large desktop screens without abrupt media query jumps:
    - `--font-size-body`: `clamp(0.875rem, 1vw + 0.5rem, 1.125rem)`
    - `--font-size-sm`: `clamp(0.75rem, 0.9vw + 0.4rem, 1rem)`
    - `--font-size-xs`: `clamp(0.625rem, 0.8vw + 0.3rem, 0.875rem)`
    - `--font-size-lg`: `clamp(1rem, 1.2vw + 0.6rem, 1.25rem)`
    - `--font-size-xl`: `clamp(1.25rem, 1.5vw + 0.7rem, 1.75rem)`
    - `--font-size-2xl`: `clamp(1.5rem, 2vw + 0.8rem, 2rem)`
    - `--font-size-3xl`: `clamp(1.875rem, 2.5vw + 0.9rem, 2.5rem)`
    - Headings `--font-size-h1` through `--font-size-h6`, `--font-size-prose`, and `--font-size-code`.
- **Font Weights and Line Heights**:
  - Weights from 300 to 800 (`--font-weight-light` through `--font-weight-extrabold`).
  - Line heights from 1.2 to 2 (`--line-height-tight`, `--line-height-normal`, `--line-height-relaxed`, `--line-height-loose`).

### Spacing and Grid Scale (`spacing.css`)

`css/tokens/spacing.css` follows an 8px grid based on a 4px (0.25rem) base unit:

- **Spacing Scale**:
  - `--spacing-0`: `0`
  - `--spacing-xs`: `0.25rem` (4px)
  - `--spacing-sm`: `0.5rem` (8px)
  - `--spacing-md`: `1rem` (16px)
  - `--spacing-lg`: `1.5rem` (24px)
  - `--spacing-xl`: `2rem` (32px)
  - `--spacing-2xl`: `4rem` (64px)
  - `--spacing-3xl`: `6rem` (96px)
- **Padding, Margin, and Gap Primitives**:
  - Dedicated tokens for inline/block padding, directional margins, container responsive padding (`--padding-container-mobile/tablet/desktop`), and flex/grid gaps (`--gap-xs` through `--gap-2xl`, `--gap-standard`, `--gap-loose`, `--gap-compact`).

### Breakpoint Scale (`breakpoints.css`)

`css/tokens/breakpoints.css` defines the 5 standard viewport boundaries:

- `--breakpoint-xs`: `320px` (small mobile devices)
- `--breakpoint-sm`: `640px` (large phones / small tablets)
- `--breakpoint-md`: `768px` (tablets / small laptops)
- `--breakpoint-lg`: `1024px` (standard desktop screens)
- `--breakpoint-xl`: `1440px` (wide desktop monitors)

### The `@media` Literal-Pixel Rule (#3326)

> **CRITICAL RULE**: CSS custom properties are strictly **invalid** in `@media` query preludes per the W3C CSS Values and Units specification.

An expression such as:
```css
/* INVALID - DO NOT USE: parses as 'not all' and is discarded by browsers */
@media (width < var(--breakpoint-sm)) { ... }
```
is treated by browsers as unparseable syntax, silently resolving to `not all` and dropping all contained rules. This caused mobile layouts to break completely prior to issue #3326.

**Mandatory Practice**:
- Always use the literal pixel values in media queries:
  - Mobile only: `@media (width < 768px) { ... }`
  - Tablet and up: `@media (width >= 768px) { ... }`
  - Desktop and up: `@media (width >= 1024px) { ... }`
  - Large desktop: `@media (width >= 1440px) { ... }`
- Reference the custom properties (`var(--breakpoint-*)`) exclusively inside CSS declaration blocks.

---

## Component Gallery and Primitives

The following component primitives live in `css/components/` and provide consistent UI surfaces across chapters and reference pages.

### Site Card Primitive (`site-card`)

Defined in `css/components/site-card.css`.
The canonical container primitive replacing legacy fragmented card classes (`.quick-link-card`, `.audience-card`, `.resource-card`, `.featured-card`, `.category-section`).

- **Classes**:
  - `.site-card`: Base container with 1px border, 6px border-radius, background padding, and hover/focus transitions.
  - `.site-card--inline`: Compact padding (`0.75rem 1rem`) for dense rows and lists.
  - `.site-card--feature`: Generous padding (`2rem`) for major landing-page highlights.
  - `.site-card--brand`: Full primary brand fill (`--color-primary-main`) with white text for singular hero callouts.
  - `.site-card--callout`: Left accent border (`4px solid var(--color-primary-light)`) on neutral secondary background.

### Site Button Primitive (`site-button`)

Defined in `css/components/site-button.css`.
The two-variant accessible button primitive replacing inline styles and ad-hoc CTA links.

- **Classes**:
  - `.site-button`: Primary filled button (`--color-primary-main`) with bold text, hover contrast, and 44px minimum touch targets (WCAG 2.5.5 / 2.5.8).
  - `.site-button--ghost`: Transparent background with primary-colored border and text.
  - `.site-card--brand .site-button--on-brand`: Inverted solid button designed to sit inside `.site-card--brand`.
  - `.site-card--brand .site-button--on-brand-ghost`: Inverted ghost button designed to sit inside `.site-card--brand`.
- **States**: High-visibility `:focus-visible` outline (`2px solid var(--color-primary-light)`), disabled state styling (`[disabled]`, `[aria-disabled="true"]`).

### Status Badge Component (`status-badge`)

Defined in `css/components/status-badge.css`.
Implements the Unified Publication Status Badge system (WEB-04.2 #4516) reflecting content maturity and verification level.

- **Design Contracts**:
  - Employs both text and SVG icon (does not convey meaning by color alone, WCAG 1.4.1).
  - Guarantees WCAG AA contrast ratio (>= 4.5:1) in both light and dark themes.
  - Links to canonical documentation at `/how-to-read.html#publication-states`.
- **Six Canonical States**:
  1. `status-badge--available`: Blue tint, indicates fully written and inspectable text open for review.
  2. `status-badge--validated`: Green tint, indicates empirical evidence, calibrated data, and bounded error.
  3. `status-badge--experimental`: Purple tint, indicates exploratory modeling or open conjectures.
  4. `status-badge--planned`: Amber tint, indicates reserved chapters or scaffolding.
  5. `status-badge--deprecated`: Slate gray tint, indicates historical or superseded derivation.
  6. `status-badge--opinion`: Rose red tint, indicates interpretive commentary or subjective perspectives.

### Callout Boxes and Equation Containers (`callouts`)

Defined in `css/components/callouts.css`.
The single source of truth for pedagogical callout blocks (issue #3331):

- `.equation`: Distinct display container for standalone mathematical formulas with left accent border and horizontal scroll support.
- `.abstract-section`: Introductory overview panel with brand tint and prominent typography.
- `.keypoint-box`: Highlight box emphasizing key findings and core takeaways.
- `.limitation-box`: Explicit epistemic boundary container with error-accent border (`--color-error`).
- `.callout.callout-example`: Dedicated callout style for worked mathematical examples verified by test suites (#4511).

### In Layman's Terms Component (`laymans-terms`)

Defined in `css/components/laymans-terms.css`.
Created for issue #4494 and rendered via `scripts/filters/laymans-terms.lua`:

- Provides plain-English non-technical explanations paired with rigorous mathematical articles.
- Includes expandable content panel (`.laymans-terms-content[aria-hidden="false"]`) with accessible accordion controls.
- Enforces underline on embedded links (`.laymans-terms a`) to prevent reliance on color alone (WCAG 1.4.1).
- Distinct sub-containers for analogies (`.laymans-item .analogy`) and takeaways (`.laymans-item .key-takeaway`) that remain legible across both light and dark themes.

### Caveats and Scope Boundary Block (`caveats-block`)

Defined in `css/components/caveats-block.css`.
Implements standard "What This Shows / What It Does Not Show" boundaries (WEB-03.4 #4509):

- Classes: `.caveats-card`, `.what-this-shows-card`.
- Amber warning accent border (`border-left: 4px solid var(--color-warning)`).
- Clear typography hierarchy: `.caveats-title`, `.caveats-subtitle`, `.caveats-list`, and italicized `.caveats-gate-text`.
- Prevents overclaiming and reinforces honest epistemic boundaries for theoretical models.

### Golfers and Coaches Box (`golfers-coaches-box`)

Conceptualized under WEB-03.7 ("What This Means for Golfers and Coaches"):

- Bounded practical implications container bridging academic derivations and real-world athletic application.
- Formulates coaching questions and conceptual takeaways without offering unverified biomechanical prescriptions.
- Employs the bounded callout pattern (`.caveats-card` / `.site-card--callout`) with dedicated status badges linking back to empirical evidence rungs.

### Page Header Card Component (`page-header-card`)

Defined in `css/components/page-header-card.css`.
Standardized metadata header block (WEB-03.2 #4507) placed at the top of long-form articles:

- Responsive grid (`.page-header-metadata`) organizing reading time, prerequisites, publication dates, and citations.
- Structured badge system:
  - Maturity: `.badge--canonical`, `.badge--reviewed`, `.badge--draft`, `.badge--exploratory`.
  - Audience: `.badge--audience`.
- Provides instant context regarding article rigor and prerequisites.

### Scientific Trust Panel (`scientific-trust-panel`)

Defined in `css/components/scientific-trust-panel.css`.
Presentation container for scientific claims registered in `data/trust/claim_registry.json`:

- Clean responsive grid layout with blue accent border (`border-left: 0.35rem solid var(--accent-blue)`).
- Links claims directly to reproducible test suites and mathematical validation evidence via `.trust-claim-link`.
- Includes print media styling (`break-inside: avoid`) for readable exported reports.

### Drift Plus Control Vector Graphic (`drift-plus-control`)

Defined in `css/components/drift-plus-control.css`.
Signature interactive/static vector graphic (WEB-08.2 #4554) illustrating affine vector fields:

- Theme-aware SVG styling driven completely by CSS variables (`--dpc-drift`, `--dpc-push`, `--dpc-ink`, `--dpc-muted`).
- Color mappings adapt dynamically between light mode and dark mode without inline SVG hardcoding.
- Renders passive drift trajectories (`.dpc-drift`), active input vectors (`.dpc-push`), and resulting control paths (`.dpc-sum`).

---

## Global Reset Removal and CSS Budget Policy

### Removal of Global Margin and Padding Reset

Historically, `styles.css` (lines 64-70) included an indiscriminate universal reset:
```css
/* Legacy problematic reset */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
```

**Problem**:
Zeroing `margin` and `padding` on all elements via `*` stripped Bootstrap's default element spacing,
disrupted standard Quarto typography, and forced components throughout the codebase to declare
defensive margin/padding overrides.

**Resolution (#4553)**:
The reset was replaced with the modern box-sizing standard:
```css
/* Reset and Base Styles */
*,
*::before,
*::after {
  box-sizing: border-box;
}
```
This preserves `box-sizing: border-box` inheritance without clearing native and framework
spacing rules, preventing cascade conflicts with Bootstrap.

### CSS Budget Enforcement Policy (`max_lines: 3400`, `max_important: 10`)

To protect maintainability and prevent stylesheet entropy, the CSS architecture is bounded
by CI tests (`scripts/check_styles_budget.py` and `tests/test_check_styles_budget.py`).

1. **Line Budget (`max_lines: 3400`)**:
   - `styles.css` is restricted to a maximum of 3400 lines.
   - Any new component or token additions must be placed into modular files under `css/tokens/` or `css/components/` rather than expanding `styles.css`.
2. **Specificity Budget (`max_important: 10`)**:
   - At most 10 instances of `!important` are allowed in `styles.css`.
   - Prevents specificity escalation and preserves clean cascade layering.

# Design Token Audit (Issue #4553, WEB-08.1)

Scope: where colour, spacing and type values are defined and duplicated in the
site CSS, what this change consolidates, and what remains blocked.

## Token Sources (After This Change)

| Concern | Canonical file | Notes |
| --- | --- | --- |
| Colour, light and dark | `css/tokens/colors.css` | Includes the Okabe-Ito palette (`--color-orange` ... `--color-gray`) since #4553 |
| Type families, sizes, weights | `css/tokens/typography.css` | |
| Spacing scale | `css/tokens/spacing.css` | |
| Radius and border width | `css/tokens/borders.css` | |
| Elevation | `css/tokens/shadows.css` | |
| Motion | `css/tokens/animations.css` | |
| Stacking | `css/tokens/z-index.css` | |
| Breakpoints | `css/tokens/breakpoints.css` | Literal px only in `@media` (#3326) |
| Bootstrap compile-time palette | `custom.scss` (`$color-*`, `$primary` ...) | SCSS needs literals; `tests/test_design_token_palette.py` pins them to the CSS tokens |

## Findings

1. **Okabe-Ito palette declared twice (fixed).** `custom.scss` carried a
   `:root` block with eight `--color-*` custom properties while every other
   colour token lived in `css/tokens/colors.css`. The block now lives only in
   the token file; the SCSS variables stay (Bootstrap uses them at compile time)
   and a test asserts the two agree. Values are identical (hex case normalised
   to lower case), so rendering is unchanged.
2. **Elevation, fluid type and fluid spacing tokens are redeclared in
   `styles.css` `:root`** (`--shadow-sm/md/lg`, `--fs-*`, `--spacing-xs..xl`,
   plus 27 distinct custom properties in total). Because `styles.css` loads
   after the token imports, the `styles.css` values win. **Blocked**, see below.
3. **Global reset** `* { margin: 0; padding: 0; box-sizing: border-box; }` at
   `styles.css` line 65 sits on top of Bootstrap and causes the cascade fights
   the issue describes. **Blocked**, see below.
4. **Display-math overflow** was duplicated in `custom.scss` and `styles.css`;
   already consolidated by #4581 (`tests/test_math_overflow_rules.py`).
5. **Raw hex literals outside the token files.** Across `styles.css`,
   `css/*.css` and `css/components/*.css` the most repeated are `#fff` (20),
   `#e5e7eb` (15), `#f8f9fa` (11), `#0d6efd` (11), `#6c757d` (10), `#3282b8` (10),
   `#dc3545` (9) and `#e2e8f0` (8). Several equal an existing token
   (`#fff` = `--color-neutral-0`, `#e5e7eb` = `--color-neutral-200`, `#f8f9fa` =
   `--bg-secondary`, `#3282b8` = `--color-primary-light`). Near-duplicate
   neighbours worth unifying in a visual-regression-approved follow-up:
   `#dc3545` / `#c82333` (error), `#3b82f6` / `#2563eb` / `#0d6efd` (blue).
6. **Per-page stylesheets.** 35 files directly under `css/` plus 30 under
   `css/components/`. Page stylesheets pinned by `data/trust` audits
   (`css/articulated-body.css`, `css/computational-brain.css`,
   `css/duality-chapter.css`, `css/force-measurement.css`,
   `css/force-mobility.css`, `css/lagrangian-reference.css`,
   `css/manifesto.css`, `css/nonlinear-control.css`,
   `css/technical-explanations.css`, `css/zero-torque.css`,
   `css/components/falsification-atlas.css`,
   `articles/proximal-distal-companion.css`) cannot be edited without
   regenerating `data/trust/**`.

## Why Items 2, 3 and 5 Are Not Changed Here

`styles.css` is source-digest-pinned by the `ad-finding-notation-render-integrity`
finding in `data/trust/site_trust_surface_audit.json`. Verified: appending a
single comment line to `styles.css` makes
`tests/test_site_trust_surface_audit.py` fail with
`evidence digest mismatch: styles.css`. The task constraints forbid editing
`data/trust/**`, so any change to `styles.css` (removing the reset, dropping the
duplicated `:root` tokens) needs an owner-approved digest regeneration
(`python3 -m scripts.regenerate_claim_audit_evidence`).

## Remaining Acceptance Criteria

- [ ] Component gallery page (internal). Needs a Quarto build to verify; `quarto`
  is not installed on this host.
- [x] CSS budget does not increase (`styles.css` untouched; token file +12 lines).
- [ ] Visual-regression snapshots approved (needs the Playwright run in CI).
- [ ] Reset removed with no regression (blocked on the digest pin above).

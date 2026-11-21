/**
 * Docked sidebar as a phone off-canvas panel (issue #5325).
 *
 * Below Bootstrap's lg breakpoint Quarto collapses the docked sidebar into a
 * fixed panel. These contracts keep it at the navbar menu's quality: a bounded
 * panel width, padding, 44px rows, a current-page indicator, a visible scrim
 * and a 44px close button that is hidden on desktop.
 */

const fs = require('fs');
const path = require('path');

const sidebarCss = fs.readFileSync(
  path.join(__dirname, '..', 'css', 'components', 'page-sidebar.css'),
  'utf8',
);

/** Body of the first `@media (max-width: 991.98px)` block. */
function phoneBlock(css) {
  const start = css.indexOf('@media (max-width: 991.98px)');
  if (start === -1) return '';
  const open = css.indexOf('{', start);
  let depth = 0;
  for (let i = open; i < css.length; i++) {
    if (css[i] === '{') depth++;
    else if (css[i] === '}') {
      depth--;
      if (depth === 0) return css.slice(open + 1, i);
    }
  }
  return '';
}

/** Declarations of the first rule whose selector list includes `selector`. */
function rule(css, selector) {
  const re = /([^{}]+)\{([^{}]*)\}/g;
  const uncommented = css.replace(/\/\*[\s\S]*?\*\//g, '');
  let match;
  while ((match = re.exec(uncommented))) {
    const selectors = match[1].split(',').map((s) => s.trim());
    if (selectors.includes(selector)) return match[2];
  }
  return '';
}

describe('docked sidebar off-canvas on phones (#5325)', () => {
  const phone = phoneBlock(sidebarCss);

  test('the open panel is bounded to the phone width and padded', () => {
    const panel = rule(phone, '#quarto-sidebar.sidebar-navigation');
    expect(panel).toMatch(/width:\s*min\(/);
    expect(panel).toMatch(/padding:/);
  });

  test('sidebar rows are 44px touch targets', () => {
    expect(rule(phone, '#quarto-sidebar .sidebar-link')).toMatch(
      /min-height:\s*44px/,
    );
  });

  test('the current page is marked with an accent bar', () => {
    expect(rule(phone, '#quarto-sidebar .sidebar-link.active')).toMatch(
      /border-left:\s*3px solid var\(--color-primary-main\)/,
    );
  });

  test('the scrim behind the panel is visibly dimmed', () => {
    expect(rule(phone, '#quarto-sidebar-glass.show')).toMatch(/background-color:/);
  });

  test('the close button is a 44px target on phones and hidden on desktop', () => {
    const close = rule(phone, '#quarto-sidebar .sidebar-close');
    expect(close).toMatch(/min-width:\s*44px/);
    expect(close).toMatch(/min-height:\s*44px/);
    expect(rule(sidebarCss, '.sidebar-close')).toMatch(/display:\s*none/);
  });
});

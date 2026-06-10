/**
 * Regression tests for the dark-mode CSS cascade (2026-06-09 web audit).
 *
 * Two invariants:
 *
 * 1. No selector may appear inside an @media query list.
 *    `@media (prefers-color-scheme: dark), [data-theme="dark"]` is invalid
 *    CSS — a media query list may only contain media queries. Browsers
 *    treat the selector member as `not all` and silently drop it.
 *
 * 2. The OS-preference dark block must not override an explicit light
 *    choice. js/dark-mode-toggle.js sets data-theme="light" when the user
 *    picks light, so the prefers-color-scheme block must scope its
 *    variables with :root:not([data-theme="light"]). Without the guard, a
 *    user on an OS dark theme who toggles the site to light still gets
 *    dark CSS variables (half-dark page).
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');

function cssFiles() {
  const files = ['styles.css'];
  const walk = (dir) => {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (entry.name.endsWith('.css')) {
        files.push(path.relative(ROOT, full).replace(/\\/g, '/'));
      }
    }
  };
  walk(path.join(ROOT, 'css'));
  return files;
}

describe('dark mode CSS cascade', () => {
  test.each(cssFiles())(
    '%s has no attribute selector inside an @media query list',
    (file) => {
      const cssText = fs
        .readFileSync(path.join(ROOT, file), 'utf8')
        .replace(/\/\*[\s\S]*?\*\//g, ''); // ignore comments
      // Match "@media ... [data-theme" before the opening brace — a selector
      // can never legally appear in the media query prelude.
      expect(cssText).not.toMatch(/@media[^{]*\[data-theme/);
    }
  );

  test('prefers-color-scheme dark block yields to explicit light theme', () => {
    const cssText = fs.readFileSync(path.join(ROOT, 'styles.css'), 'utf8');
    const mediaBlocks = cssText.match(
      /@media\s*\(prefers-color-scheme:\s*dark\)[^{]*\{[\s\S]*?\n\}/g
    ) || [];
    expect(mediaBlocks.length).toBeGreaterThan(0);
    for (const block of mediaBlocks) {
      // Any :root rule inside the OS-dark media block must carry the
      // :not([data-theme="light"]) guard.
      const rootSelectors = block.match(/:root[^,{]*/g) || [];
      for (const selector of rootSelectors) {
        expect(selector).toContain(':not([data-theme="light"])');
      }
    }
  });
});

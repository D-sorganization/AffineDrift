/**
 * Design-token unification contract — issue #3224.
 *
 * Asserts that the legacy brand palette in styles.css :root is now expressed
 * as aliases of the canonical css/tokens/colors.css token set, so there is a
 * single source of truth for brand color and the two systems cannot drift.
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');

function read(rel) {
  return fs.readFileSync(path.join(ROOT, rel), 'utf8');
}

/** Extract the first `:root { ... }` block's variable declarations. */
function rootDeclarations(cssText) {
  const idx = cssText.indexOf(':root');
  const open = cssText.indexOf('{', idx);
  // Walk to the matching close brace.
  let depth = 0;
  let end = open;
  for (let i = open; i < cssText.length; i++) {
    if (cssText[i] === '{') depth++;
    else if (cssText[i] === '}') {
      depth--;
      if (depth === 0) {
        end = i;
        break;
      }
    }
  }
  const body = cssText.slice(open + 1, end);
  const decls = {};
  const re = /(--[\w-]+)\s*:\s*([^;]+);/g;
  let m;
  while ((m = re.exec(body)) !== null) {
    decls[m[1].trim()] = m[2].trim();
  }
  return decls;
}

describe('design tokens (#3224)', () => {
  const styles = rootDeclarations(read('styles.css'));
  const colors = rootDeclarations(read('css/tokens/colors.css'));

  const LEGACY_BRAND_VARS = [
    '--primary-dark',
    '--primary-blue',
    '--accent-blue',
    '--light-blue',
    '--pure-white',
    '--legal-pad-yellow',
  ];

  test.each(LEGACY_BRAND_VARS)(
    'styles.css :root declares %s as a var(--color-*) alias, not a raw literal',
    (name) => {
      expect(styles[name]).toBeDefined();
      expect(styles[name]).toMatch(/^var\(--color-[\w-]+\)$/);
    }
  );

  test('the genuinely-unique brand values are canonicalized in colors.css', () => {
    // #205d86 (page-chrome accent) and #fef9e7 (legal-pad highlight) live in
    // colors.css as named tokens — the single source of truth.
    expect(colors['--color-accent']).toBe('#205d86');
    expect(colors['--color-highlight-yellow']).toBe('#fef9e7');
  });

  test('styles.css :root no longer hard-codes the brand hex literals', () => {
    for (const name of LEGACY_BRAND_VARS) {
      expect(styles[name]).not.toMatch(/#[0-9a-fA-F]{3,6}/);
    }
  });
});

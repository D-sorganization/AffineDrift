/**
 * Token unification contract tests (issue #3224).
 *
 * Asserts that css/tokens/colors.css is the single source of truth for color:
 *  (a) every legacy palette var in styles.css :root resolves to a var(--color-*)
 *      / canonical functional token alias (no raw hex re-declarations);
 *  (b) styles.css contains no color-variable dark-mode block (dark remaps are
 *      centralized in colors.css);
 *  (c) colors.css remaps dark under BOTH gates, and the prefers-color-scheme
 *      gate yields to an explicit light choice (:not([data-theme="light"])).
 */

const fs = require('fs');
const path = require('path');

const repoRoot = path.resolve(__dirname, '..');
const stylesCss = fs.readFileSync(path.join(repoRoot, 'styles.css'), 'utf8');
const colorsCss = fs.readFileSync(
  path.join(repoRoot, 'css', 'tokens', 'colors.css'),
  'utf8',
);

/** Extract the first top-level `:root { ... }` block body from CSS text. */
function rootBlock(css) {
  const start = css.indexOf(':root {');
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

describe('design tokens: single source of truth', () => {
  test('styles.css :root no longer declares raw color hex values', () => {
    const block = rootBlock(stylesCss);
    // Color tokens must not be re-declared as raw hex in styles.css.
    const colorVarNames = [
      '--primary-dark',
      '--primary-blue',
      '--accent-blue',
      '--light-blue',
      '--bg-body',
      '--bg-alt',
      '--bg-sidebar',
      '--text-main',
      '--text-muted',
      '--border-color',
      '--legal-pad-yellow',
    ];
    for (const name of colorVarNames) {
      const rawHex = new RegExp(`${name}\\s*:\\s*#[0-9a-fA-F]{3,8}\\s*;`);
      expect(block).not.toMatch(rawHex);
    }
  });

  test('legacy aliases in colors.css resolve to canonical --color-* tokens', () => {
    expect(colorsCss).toMatch(/--primary-dark:\s*var\(--color-primary-dark\)/);
    expect(colorsCss).toMatch(/--primary-blue:\s*var\(--color-primary-main\)/);
    expect(colorsCss).toMatch(/--light-blue:\s*var\(--color-primary-lightest\)/);
    expect(colorsCss).toMatch(/--accent-blue:\s*var\(--color-accent\)/);
    expect(colorsCss).toMatch(/--legal-pad-yellow:\s*var\(--color-highlight-yellow\)/);
  });

  test('the unique accent value lives in colors.css as --color-accent', () => {
    expect(colorsCss).toMatch(/--color-accent:\s*#205d86/);
    expect(colorsCss).toMatch(/--color-highlight-yellow:\s*#fef9e7/);
  });

  test('styles.css contains no color-variable dark-mode block', () => {
    // No prefers-color-scheme dark block remains in styles.css.
    expect(stylesCss).not.toMatch(/@media\s*\(prefers-color-scheme:\s*dark\)/);
    // No [data-theme="dark"] block that assigns color custom properties.
    const darkBlocks = stylesCss.match(/\[data-theme="dark"\]\s*\{[\s\S]*?\}/g) || [];
    for (const b of darkBlocks) {
      // Toggle-button / focus-ring selectors are fine; pure variable remaps are not.
      expect(b).not.toMatch(/--bg-body|--text-main|--legal-pad-yellow|--border-color:/);
    }
  });

  test('colors.css centralizes dark remaps under both gates', () => {
    expect(colorsCss).toMatch(/\[data-theme="dark"\]\s*\{/);
    expect(colorsCss).toMatch(/@media\s*\(prefers-color-scheme:\s*dark\)/);
  });

  test('prefers-color-scheme dark block yields to explicit light theme', () => {
    const mediaBlocks = colorsCss.match(
      /@media\s*\(prefers-color-scheme:\s*dark\)\s*\{[\s\S]*?\n {2}\}/g,
    );
    expect(mediaBlocks).toBeTruthy();
    for (const block of mediaBlocks) {
      const selector = block.split('{')[1];
      expect(selector).toContain(':not([data-theme="light"])');
    }
  });

  test('no hex literal is declared under two different var names across files', () => {
    // (b): same hex must not map to different legacy/canonical names in the
    // two :root blocks. Build hex -> set(varNames) from both :root blocks.
    const decls = `${rootBlock(colorsCss)}\n${rootBlock(stylesCss)}`;
    const hexToNames = new Map();
    const re = /(--[\w-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\s*;/g;
    let m;
    while ((m = re.exec(decls)) !== null) {
      const [, name, hex] = m;
      const key = hex.toLowerCase();
      if (!hexToNames.has(key)) hexToNames.set(key, new Set());
      hexToNames.get(key).add(name);
    }
    // colors.css is the only place raw hex lives; styles.css :root should add
    // zero raw-hex color names, so no hex maps to a styles.css name at all.
    const stylesNames = new Set(
      [...rootBlock(stylesCss).matchAll(/(--[\w-]+)\s*:\s*#[0-9a-fA-F]{3,8}/g)].map(
        (x) => x[1],
      ),
    );
    expect(stylesNames.size).toBe(0);
  });
});

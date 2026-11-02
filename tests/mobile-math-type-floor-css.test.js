const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const STYLES = fs.readFileSync(path.join(ROOT, 'css', 'components', 'quarto-theme.css'), 'utf8');
const CANONICAL = fs.readFileSync(path.join(ROOT, 'styles.css'), 'utf8');

/** Body of the first `@media (max-width: <px>px)` block that contains `needle`. */
function mediaBlockContaining(css, maxWidthPx, needle) {
  const opener = `@media (max-width: ${maxWidthPx}px)`;
  let from = 0;
  for (;;) {
    const start = css.indexOf(opener, from);
    if (start === -1) return '';
    let depth = 0;
    let end = css.indexOf('{', start);
    for (let i = end; i < css.length; i += 1) {
      if (css[i] === '{') depth += 1;
      if (css[i] === '}') depth -= 1;
      if (depth === 0) {
        end = i;
        break;
      }
    }
    const body = css.slice(start, end + 1);
    if (body.includes(needle)) return body;
    from = end + 1;
  }
}

describe('Mobile math fit and 12px type floor (#5326)', () => {
  test('phone display math steps down enough for near-fit equations to fit', () => {
    // The rule applies to both the wrapper and mjx-container, so the scale
    // compounds: 0.82^2 brings theory-part1's widest 356px equation to ~331px,
    // inside the 337px column at 390px.
    const phone = mediaBlockContaining(CANONICAL, 480, '.math.display');
    const match = phone.match(
      /mjx-container\[jax="CHTML"\]\[display="true"\],\s*\.MathJax_Display,\s*\.math\.display\s*\{[^}]*font-size:\s*([0-9.]+)em/,
    );
    expect(match).not.toBeNull();
    expect(Number(match[1]) ** 2 * (356 / 0.85 ** 2)).toBeLessThanOrEqual(337);
  });

  test('display math never bleeds into the gutter, which widens its section', () => {
    expect(STYLES).not.toMatch(/\.math\.display\s*\{[^}]*margin-inline:\s*-/);
  });

  test('title-block meta headings and category chips never render under 12px', () => {
    expect(STYLES).toMatch(
      /#title-block-header\.quarto-title-block\.default \.quarto-title-meta-heading,\s*#title-block-header \.quarto-title \.quarto-categories \.quarto-category,[^{]*\{[^}]*font-size:\s*max\(12px,\s*0\.75rem\)/,
    );
  });

  test('the appendix BibTeX citation block never renders under 12px', () => {
    expect(STYLES).toMatch(
      /pre\.quarto-appendix-bibtex,\s*pre\.quarto-appendix-bibtex > code\s*\{[^}]*font-size:\s*max\(12px,\s*0\.75rem\)/,
    );
  });
});

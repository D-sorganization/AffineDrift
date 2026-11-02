const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const STYLES = fs.readFileSync(path.join(ROOT, 'css', 'components', 'quarto-theme.css'), 'utf8');

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
  test('phone display equations in top-level paragraphs may use the side gutter', () => {
    const phone = mediaBlockContaining(STYLES, 480, 'section > p > .math.display');
    expect(phone).toMatch(
      /#quarto-document-content > p > \.math\.display,\s*#quarto-document-content section > p > \.math\.display\s*\{[^}]*margin-inline:\s*-1rem/,
    );
    // The canonical display-math rule caps max-width at 100%, which would
    // cancel the negative margins.
    expect(phone).toMatch(/section > p > \.math\.display\s*\{[^}]*max-width:\s*none/);
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

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(ROOT, relativePath), 'utf8');
}

describe('Quarto title semantics (#3445)', () => {
  test('uses Quarto title-block rendering instead of verbatim Pandoc title blocks', () => {
    const config = read('_quarto.yml');
    expect(config).toMatch(/title-block-style:\s*default/);
    expect(config).not.toMatch(/title-block-style:\s*none/);
  });

  test('does not globally hide Quarto title blocks on standard content pages', () => {
    const css = read('styles.css');
    const displayNoneRules = [...css.matchAll(/([^{}]+#title-block-header[^{}]*)\{[^{}]*display:\s*none[^{}]*\}/g)];

    expect(displayNoneRules.length).toBeGreaterThan(0);
    for (const [, selector] of displayNoneRules) {
      expect(selector).toContain('#quarto-content.page-layout-full');
    }
  });

  test.each([
    ['index.qmd', '<h1>AffineDrift</h1>'],
    ['pages/collaborate.qmd', '<h1>Collaborate with AffineDrift</h1>'],
    ['pages/book-reviews.qmd', '<h1>Book Reviews</h1>'],
    ['resources/resources.qmd', '<h1 id="resources-links-heading">Resources & Links</h1>'],
  ])('%s keeps one authored visible H1 for its full-layout page', (relativePath, heading) => {
    const source = read(relativePath);
    expect(source).toContain('page-layout: full');
    expect(source).toContain(heading);
    expect(source.match(/<h1\b/gi)).toHaveLength(1);
  });
});

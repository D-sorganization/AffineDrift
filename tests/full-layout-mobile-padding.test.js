const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');

describe('Full-layout mobile side padding (#5323)', () => {
  test('styles.css pads page-layout-full main.content on the inline axis', () => {
    const css = fs.readFileSync(path.join(ROOT, 'styles.css'), 'utf8');
    const rule = css.match(
      /#quarto-content\.page-layout-full main\.content\s*\{[^}]*padding-inline:\s*clamp\([^)]+\)/s,
    );
    expect(rule).not.toBeNull();
  });
});

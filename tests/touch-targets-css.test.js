const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');

describe('Touch Target CSS Contract (WCAG 2.5.5, #4563)', () => {
  test('.entry-list__title in entry-list.css declares 44px min-dimensions', () => {
    const css = fs.readFileSync(path.join(ROOT, 'css', 'components', 'entry-list.css'), 'utf8');
    expect(css).toMatch(/\.entry-list__title\s*\{[^}]*min-height:\s*44px/);
    expect(css).toMatch(/\.entry-list__title\s*\{[^}]*min-width:\s*44px/);
    expect(css).toMatch(/\.entry-list__title\s*\{[^}]*display:\s*inline-flex/);
  });

  test('.site-button in site-button.css declares 44px min-dimensions', () => {
    const css = fs.readFileSync(path.join(ROOT, 'css', 'components', 'site-button.css'), 'utf8');
    expect(css).toMatch(/\.site-button\s*\{[^}]*min-height:\s*44px/);
    expect(css).toMatch(/\.site-button\s*\{[^}]*min-width:\s*44px/);
    expect(css).toMatch(/\.site-button\s*\{[^}]*display:\s*inline-flex/);
  });

  test('.provenance-note a in provenance-note.css declares 44px min-height and inline-flex', () => {
    const css = fs.readFileSync(path.join(ROOT, 'css', 'components', 'provenance-note.css'), 'utf8');
    expect(css).toMatch(/\.provenance-note a\s*\{[^}]*min-height:\s*44px/);
    expect(css).toMatch(/\.provenance-note a\s*\{[^}]*display:\s*inline-flex/);
  });

  test('.navbar-brand in quarto-theme.css declares 44px min-height and inline-flex', () => {
    const css = fs.readFileSync(path.join(ROOT, 'css', 'components', 'quarto-theme.css'), 'utf8');
    expect(css).toMatch(/\.navbar-brand\s*\{[^}]*min-height:\s*44px/);
    expect(css).toMatch(/\.navbar-brand\s*\{[^}]*display:\s*inline-flex/);
  });

  test('bundled docs/styles.css includes the touch target rules', () => {
    const bundle = fs.readFileSync(path.join(ROOT, 'docs', 'styles.css'), 'utf8');
    expect(bundle).toMatch(/\.entry-list__title\s*\{[^}]*min-height:\s*44px/);
    expect(bundle).toMatch(/\.site-button\s*\{[^}]*min-height:\s*44px/);
    expect(bundle).toMatch(/\.provenance-note a\s*\{[^}]*min-height:\s*44px/);
    expect(bundle).toMatch(/\.navbar-brand\s*\{[^}]*min-height:\s*44px/);
  });

  test('ci-standard.yml no longer inverts should provide summary of all compliant elements', () => {
    const workflow = fs.readFileSync(path.join(ROOT, '.github', 'workflows', 'ci-standard.yml'), 'utf8');
    expect(workflow).not.toMatch(/should provide summary of all compliant elements/);
  });
});

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

  test('.navbar-nav .nav-link and .dropdown-item in quarto-theme.css declare 44px min-height', () => {
    const css = fs.readFileSync(path.join(ROOT, 'css', 'components', 'quarto-theme.css'), 'utf8');
    expect(css).toMatch(/\.navbar-nav \.nav-link\s*\{[^}]*min-height:\s*44px/);
    expect(css).toMatch(/\.dropdown-item\s*\{[^}]*min-height:\s*44px/);
    expect(css).toMatch(/\.quarto-citation-bibtex-download\s*\{[^}]*min-height:\s*44px/);
    expect(css).toMatch(/\.code-copy-button\s*\{[^}]*min-height:\s*44px/);
  });

  test('.navbar-nav .nav-link never wraps, so a long label cannot reflow the navbar', () => {
    const css = fs.readFileSync(path.join(ROOT, 'css', 'components', 'quarto-theme.css'), 'utf8');
    expect(css).toMatch(/\.navbar-nav \.nav-link\s*\{[^}]*white-space:\s*nowrap/);
  });

  test('.page-header-cite-link in page-header-card.css declares 44px min-dimensions', () => {
    const css = fs.readFileSync(path.join(ROOT, 'css', 'components', 'page-header-card.css'), 'utf8');
    expect(css).toMatch(/\.page-header-cite-link\s*\{[^}]*min-height:\s*44px/);
    expect(css).toMatch(/\.page-header-cite-link\s*\{[^}]*min-width:\s*44px/);
  });

  test('bundled _site/styles.css includes the touch target rules', () => {
    const bundle = fs.readFileSync(path.join(ROOT, '_site', 'styles.css'), 'utf8');
    expect(bundle).toMatch(/\.entry-list__title\s*\{[^}]*min-height:\s*44px/);
    expect(bundle).toMatch(/\.site-button\s*\{[^}]*min-height:\s*44px/);
    expect(bundle).toMatch(/\.provenance-note a\s*\{[^}]*min-height:\s*44px/);
    expect(bundle).toMatch(/\.navbar-brand\s*\{[^}]*min-height:\s*44px/);
    expect(bundle).toMatch(/\.navbar-nav \.nav-link\s*\{[^}]*min-height:\s*44px/);
    expect(bundle).toMatch(/\.dropdown-item\s*\{[^}]*min-height:\s*44px/);
    expect(bundle).toMatch(/\.code-copy-button\s*\{[^}]*min-height:\s*44px/);
  });

  test('ci-standard.yml no longer inverts should provide summary of all compliant elements', () => {
    const workflow = fs.readFileSync(path.join(ROOT, '.github', 'workflows', 'ci-standard.yml'), 'utf8');
    expect(workflow).not.toMatch(/should provide summary of all compliant elements/);
  });
});

describe('Mobile widget touch targets (#5324)', () => {
  const coarseBlock = (css) => {
    const match = css.match(/@media\s*\(\s*pointer:\s*coarse\s*\)\s*\{([\s\S]*?)\n\}/);
    expect(match).not.toBeNull();
    return match[1];
  };

  test('drift-control sandbox enlarges coarse-pointer controls', () => {
    const css = fs.readFileSync(path.join(ROOT, 'css', 'drift-control-sandbox.css'), 'utf8');
    const block = coarseBlock(css);
    expect(block).toMatch(/#dcsb-controls input\[type="range"\][\s\S]*min-height:\s*44px/);
    expect(block).toMatch(/#dcsb-controls input\[type="checkbox"\][\s\S]*min-height:\s*44px/);
    expect(block).toMatch(/#dcsb-controls select[\s\S]*min-height:\s*44px/);
  });

  test('rotation converter enlarges coarse-pointer form controls', () => {
    const css = fs.readFileSync(path.join(ROOT, 'css', 'rotation-converter.css'), 'utf8');
    const block = coarseBlock(css);
    expect(block).toMatch(/\.rc-panel input\[type="text"\][\s\S]*min-height:\s*44px/);
    expect(block).toMatch(/\.rc-load-btn[\s\S]*min-height:\s*44px/);
    expect(block).toMatch(/\.rc-preset-btn[\s\S]*min-height:\s*44px/);
  });

  test('dataset explorer enlarges coarse-pointer summaries and download buttons', () => {
    const css = fs.readFileSync(path.join(ROOT, 'css', 'dataset-explorer.css'), 'utf8');
    const block = coarseBlock(css);
    expect(block).toMatch(/#dataset-explorer-app details > summary[\s\S]*min-height:\s*44px/);
    expect(block).toMatch(/\.de-download__button[\s\S]*min-height:\s*44px/);
  });

  test('.badge--maturity meets coarse-pointer min height in page-header-card.css', () => {
    const css = fs.readFileSync(path.join(ROOT, 'css', 'components', 'page-header-card.css'), 'utf8');
    const block = coarseBlock(css);
    expect(block).toMatch(/\.badge--maturity[\s\S]*min-height:\s*44px/);
  });
});

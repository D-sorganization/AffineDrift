const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');

describe('Page Header Card Component (#4507)', () => {
  test('print stylesheet includes .page-header-card rules with break-inside avoid', () => {
    const printCss = fs.readFileSync(path.join(ROOT, 'css', 'print.css'), 'utf8');
    expect(printCss).toMatch(/\.page-header-card/);
    expect(printCss).toMatch(/break-inside:\s*avoid/);
  });

  test('css/components/page-header-card.css exists and is imported in styles.css', () => {
    const stylesCss = fs.readFileSync(path.join(ROOT, 'styles.css'), 'utf8');
    expect(stylesCss).toMatch(/@import\s+(?:url\()?["']css\/components\/page-header-card\.css["']\)?/);

    const componentCssPath = path.join(ROOT, 'css', 'components', 'page-header-card.css');
    expect(fs.existsSync(componentCssPath)).toBe(true);
    const componentCss = fs.readFileSync(componentCssPath, 'utf8');
    expect(componentCss).toMatch(/\.page-header-card/);
    expect(componentCss).toMatch(/\.page-header-metadata/);
  });

  test('js/accessibility.js labels reading time as an estimate', () => {
    const accessJs = fs.readFileSync(path.join(ROOT, 'js', 'accessibility.js'), 'utf8');
    expect(accessJs).toMatch(/min read \(estimate\)/);
  });

  test('books/roadmap.qmd records the reading-time estimate policy resolution', () => {
    const roadmap = fs.readFileSync(path.join(ROOT, 'books', 'roadmap.qmd'), 'utf8');
    expect(roadmap.toLowerCase()).toMatch(/reading.time/);
    expect(roadmap.toLowerCase()).toMatch(/estimate/);
  });

  test('scripts/filters/page-header-card.lua exists and handles front matter metadata', () => {
    const filterPath = path.join(ROOT, 'scripts', 'filters', 'page-header-card.lua');
    expect(fs.existsSync(filterPath)).toBe(true);
    const filterContent = fs.readFileSync(filterPath, 'utf8');
    expect(filterContent).toMatch(/page-header-card/);
    expect(filterContent).toMatch(/page-header-metadata/);
    expect(filterContent).toMatch(/badge--maturity/);
    expect(filterContent).toMatch(/badge--audience/);
  });
});

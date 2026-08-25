const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');

function read(relativePath) {
  return fs.readFileSync(path.join(ROOT, relativePath), 'utf8');
}

function findFullLayoutFiles(dir, files = []) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    const relPath = path.relative(ROOT, fullPath).replace(/\\/g, '/');
    if (entry.isDirectory()) {
      if (['node_modules', '.git', '.quarto', 'docs', '_freeze'].includes(entry.name)) {
        continue;
      }
      findFullLayoutFiles(fullPath, files);
    } else if (entry.name.endsWith('.qmd')) {
      const content = fs.readFileSync(fullPath, 'utf8');
      if (/page-layout:\s*full/i.test(content)) {
        files.push(relPath);
      }
    }
  }
  return files;
}

describe('Quarto title semantics (#3445, #3917)', () => {
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

  test('every full-layout page authors exactly one visible H1 (#3917)', () => {
    const fullLayoutFiles = findFullLayoutFiles(ROOT);
    expect(fullLayoutFiles.length).toBeGreaterThan(40);

    for (const relPath of fullLayoutFiles) {
      const content = read(relPath);
      const noCode = content.replace(/```[\s\S]*?```/g, '').replace(/~~~[\s\S]*?~~~/g, '');
      const mdH1s = [...noCode.matchAll(/^#\s+\S.*/gm)];
      const htmlH1s = [...content.matchAll(/<h1\b[^>]*>[\s\S]*?<\/h1>/gi)];
      const totalH1s = mdH1s.length + htmlH1s.length;

      expect(totalH1s).toBe(1);
    }
  });
});

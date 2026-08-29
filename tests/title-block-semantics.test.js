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

function findStandaloneArticleFiles(dir, files = []) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    const relPath = path.relative(ROOT, fullPath).replace(/\\/g, '/');
    if (entry.isDirectory()) {
      if (['node_modules', '.git', '.quarto', 'docs', '_freeze', 'Drafts_Original_Articles', 'tangent-hyperplane-contraction', 'The_Physics_of_Golf', 'The_Geometry_of_Motion', 'proximal_distal_energy_transfer', 'proximal_distal_companion'].includes(entry.name)) {
        continue;
      }
      findStandaloneArticleFiles(fullPath, files);
    } else if (entry.name.endsWith('.qmd')) {
      if (['volume2_content.qmd', 'CRITICS_CORNER.qmd'].includes(entry.name)) {
        continue;
      }
      const content = fs.readFileSync(fullPath, 'utf8');
      if (!/page-layout:\s*full/i.test(content) && /^title:\s*\S/m.test(content)) {
        files.push(relPath);
      }
    }
  }
  return files;
}

describe('Quarto title semantics (#3445, #3917)', () => {
  test('publishes canonical URLs while delegating the math runtime to the local gate', () => {
    const config = read('_quarto.yml');

    expect(config).toMatch(/canonical-url:\s*true/);
    expect(config).toMatch(/method:\s*mathjax/);
    expect(config).toMatch(/url:\s*["']\/js\/equation-runtime-gate\.js["']/);
    expect(config).not.toMatch(/html-math-method:\s*plain/);
  });

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

  test('full-layout pages use their authored H1 as the only visible title', () => {
    const css = read('styles.css');

    expect(css).toMatch(
      /#quarto-content\.page-layout-full\s+#title-block-header\s*\{[^}]*display:\s*none/s,
    );
    expect(css).not.toMatch(
      /page-layout-full:has\(\.page-has-custom-h1\)\s+#title-block-header/,
    );
  });

  test('site layout containers are namespaced away from Bootstrap container', () => {
    const css = read('styles.css');
    const authoredPages = findFullLayoutFiles(ROOT);

    expect(css).not.toMatch(/(^|\n)\.container\s*\{/);
    expect(css).toMatch(/(^|\n)\.ad-page-container\s*\{/);
    for (const relPath of authoredPages) {
      expect(read(relPath)).not.toMatch(
        /class=["'](?:[^"']+\s)?container(?:\s[^"']*)?["']/,
      );
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

  test('standalone articles with YAML title do not author body H1s (#3917, #3944)', () => {
    const standaloneFiles = findStandaloneArticleFiles(path.join(ROOT, 'articles'));
    expect(standaloneFiles.length).toBeGreaterThan(20);

    for (const relPath of standaloneFiles) {
      const content = read(relPath);
      const noCode = content.replace(/```[\s\S]*?```/g, '').replace(/~~~[\s\S]*?~~~/g, '');
      const mdH1s = [...noCode.matchAll(/^#\s+\S.*/gm)];
      const htmlH1s = [...content.matchAll(/<h1\b[^>]*>[\s\S]*?<\/h1>/gi)];
      const totalBodyH1s = mdH1s.length + htmlH1s.length;

      expect(totalBodyH1s).toBe(0);
    }
  });
});

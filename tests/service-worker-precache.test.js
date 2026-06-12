/**
 * Contract test: the service worker must precache the deployed stylesheet
 * bundle, not the modular source @import graph. `styles.css` remains modular
 * for authoring, while scripts/bundle_css.py renders a flattened
 * `docs/styles.css` for deployment.
 *
 * Regression test for the 2026-06-09 web audit.
 */

const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');

function readText(relPath) {
  return fs.readFileSync(path.join(ROOT, relPath), 'utf8');
}

/**
 * Extract @import targets from a stylesheet's source text.
 * Handles both `@import "x.css";` and `@import url("x.css");`.
 */
function extractImports(cssText) {
  const imports = [];
  const re = /@import\s+(?:url\(\s*)?["']([^"']+)["']\s*\)?\s*;/g;
  let match;
  while ((match = re.exec(cssText)) !== null) {
    imports.push(match[1]);
  }
  return imports;
}

/**
 * Resolve an @import target to a site-absolute URL path, given the
 * directory (site-absolute) of the importing stylesheet.
 */
function resolveImport(importerDir, target) {
  if (target.startsWith('/')) return target;
  return path.posix.normalize(path.posix.join(importerDir, target));
}

/** Collect the full transitive @import graph starting from source styles.css. */
function collectSourceImportedStylesheets() {
  const resolved = new Set();
  const queue = [{ urlPath: '/styles.css', dir: '/' }];
  const seen = new Set();

  while (queue.length > 0) {
    const { urlPath, dir } = queue.shift();
    if (seen.has(urlPath)) continue;
    seen.add(urlPath);

    const fsPath = urlPath.replace(/^\//, '');
    const cssText = readText(fsPath);
    for (const target of extractImports(cssText)) {
      const childUrl = resolveImport(dir, target);
      resolved.add(childUrl);
      queue.push({ urlPath: childUrl, dir: path.posix.dirname(childUrl) + '/' });
    }
  }

  return [...resolved];
}

describe('service worker stylesheet precache contract', () => {
  const swSource = readText('service-worker.js');
  const sourceImportedStylesheets = collectSourceImportedStylesheets();

  test('deployed docs/styles.css is a flattened bundle', () => {
    expect(readText('docs/styles.css')).not.toMatch(/@import\s+/);
  });

  test('precaches bundled and independently linked stylesheets', () => {
    expect(swSource).toContain("'/styles.css'");
    expect(swSource).toContain("'/css/search-metrics.css'");
  });

  test('no longer precaches the removed splash-screen assets (#3329)', () => {
    expect(swSource).not.toContain('startup-launcher');
  });

  test.each(sourceImportedStylesheets)('does not precache bundled source import %s', (stylesheet) => {
    expect(swSource).not.toContain(`'${stylesheet}'`);
  });

  test('every precached css file exists on disk', () => {
    const cssEntries = [...swSource.matchAll(/'(\/css\/[^']+\.css)'/g)].map(
      (m) => m[1]
    );
    expect(cssEntries.length).toBeGreaterThan(0);
    for (const entry of cssEntries) {
      const fsPath = path.join(ROOT, entry.replace(/^\//, ''));
      expect(fs.existsSync(fsPath)).toBe(true);
    }
  });
});

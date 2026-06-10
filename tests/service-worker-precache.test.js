/**
 * Contract test: the service worker must precache every stylesheet that
 * styles.css pulls in via @import (directly, and transitively through
 * css/tokens/design-tokens.css). Caching only /styles.css leaves offline
 * pages unstyled, because @import sub-resources are separate requests that
 * are NOT cached when the parent stylesheet is cached.
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

/** Collect the full transitive @import graph starting from styles.css. */
function collectImportedStylesheets() {
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
  const importedStylesheets = collectImportedStylesheets();

  test('styles.css has at least one @import (sanity check)', () => {
    expect(importedStylesheets.length).toBeGreaterThan(0);
  });

  test.each(importedStylesheets)(
    'precaches @imported stylesheet %s',
    (stylesheet) => {
      expect(swSource).toContain(`'${stylesheet}'`);
    }
  );

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

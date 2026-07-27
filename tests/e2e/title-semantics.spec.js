const { test, expect } = require('@playwright/test');

const PAGES = [
  ['home', '/', 'AffineDrift'],
  ['collaborate', '/pages/collaborate.html', 'Collaborate with AffineDrift'],
  ['book reviews', '/pages/book-reviews.html', 'Book Reviews'],
  ['resources', '/resources/resources.html', 'Resources & Links'],
  [
    'article',
    '/articles/theory-part1.html',
    'Affine Control Interpretation of the Golf Swing',
  ],
];

test.describe('title semantics (#3445)', () => {
  for (const [name, url] of PAGES) {
    test(`${name} has unique rendered element IDs`, async ({ page }) => {
      await page.goto(url, { waitUntil: 'domcontentloaded' });

      const duplicateIds = await page.evaluate(() => {
        const seen = new Set();
        const duplicates = new Set();
        for (const element of document.querySelectorAll('[id]')) {
          if (seen.has(element.id)) {
            duplicates.add(element.id);
          }
          seen.add(element.id);
        }
        return [...duplicates].sort();
      });

      expect(duplicateIds).toEqual([]);
    });
  }

  for (const [name, url, expectedHeading] of PAGES) {
    test(`${name} has one visible primary H1`, async ({ page }) => {
      await page.goto(url, { waitUntil: 'domcontentloaded' });

      const visibleH1Text = await page.locator('main h1').evaluateAll((headings) =>
        headings
          .filter((heading) => {
            const style = window.getComputedStyle(heading);
            const rect = heading.getBoundingClientRect();
            return (
              style.display !== 'none' &&
              style.visibility !== 'hidden' &&
              rect.width > 0 &&
              rect.height > 0
            );
          })
          .map((heading) => heading.textContent.trim().replace(/\s+/g, ' ')),
      );

      expect(visibleH1Text).toEqual([expectedHeading]);
    });
  }

  test('article uses one visible Quarto title block', async ({ page }) => {
    await page.goto('/articles/theory-part1.html', { waitUntil: 'domcontentloaded' });

    await expect(page.locator('header#title-block-header')).toHaveCount(1);
    await expect(page.locator('header#title-block-header')).toBeVisible();
    await expect(page.locator('header#title-block-header h1')).toHaveText(
      'Affine Control Interpretation of the Golf Swing',
    );
  });
});

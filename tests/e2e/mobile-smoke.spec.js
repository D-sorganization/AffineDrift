const { test, expect } = require('@playwright/test');

/**
 * Phone-viewport smoke test (#5316).
 *
 * Runs under the chromium project at 390x844 with touch, so the e2e-tests job
 * picks it up without a new project or job. Keep ROUTES in step with
 * config/lighthouserc.json: the nightly Lighthouse mobile baseline audits the same set.
 * Touch-target size (#5314) and full-layout side padding (#5323) are covered by
 * their own specs.
 */
const ROUTES = [
  '/',
  '/articles/theory-part1.html',
  '/articles/tangent-hyperplanes-series/part-1-geometry.html',
  '/resources/articles.html',
  '/resources/bibliography.html',
  '/resources/projections.html',
  '/pages/overview.html',
  '/pages/tangent-hyperplanes.html',
  '/models/models.html',
];

test.describe('Mobile smoke at 390x844 (#5316)', () => {
  test.use({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  test.describe.configure({ timeout: 90000 });

  for (const route of ROUTES) {
    test(`${route} renders for phones without horizontal scroll`, async ({ page }) => {
      const response = await page.goto(route, { waitUntil: 'load', timeout: 60000 });
      expect(response && response.ok()).toBeTruthy();
      await expect(page.locator('body')).toBeVisible();

      const viewportMeta = await page.locator('meta[name="viewport"]').getAttribute('content');
      expect(viewportMeta).toContain('width=device-width');

      const overflow = await page.evaluate(() => ({
        scrollWidth: document.documentElement.scrollWidth,
        innerWidth: window.innerWidth,
      }));
      expect(overflow.scrollWidth, 'page scrolls horizontally').toBeLessThanOrEqual(
        overflow.innerWidth,
      );
    });

    test(`${route} collapses the navbar behind a working toggle`, async ({ page }) => {
      await page.goto(route, { waitUntil: 'load', timeout: 60000 });
      const toggle = page.locator('.navbar-toggler').first();
      const menu = page.locator('#navbarCollapse');
      await expect(toggle).toBeVisible();
      await expect(menu).toBeHidden();

      await toggle.tap();
      await expect(menu).toBeVisible();
    });
  }
});
